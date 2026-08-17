"""VULCAN RAG store + corpus ingestion — ChromaDB (embedded, CPU, keyless).

Ingests the flagship knowledge corpus into a persistent local Chroma collection:

  * equipment_manuals/*.md      (13)
  * maintenance_sops/*.md       (13)
  * failure_analysis_reports/*.md (RCA reports, 25)
  * spare_parts_catalog.csv     (118 rows -> 1 chunk/part, procurement facts)
  * research/machinery/*.md     (20 domain references — bearings, gearboxes, ...)

Each chunk keeps a ``source`` ref (filename) + structural metadata (doc_type,
equipment_class, section) so retrieval results render inline citations (FR4).

Chunking: heading-aware markdown splitter with a char budget + overlap. Cheap,
deterministic, and keeps section context with each chunk.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..config import get_settings
from ..data.loaders import get_datastore
from .embedder import EMBED_DIM, embed_texts

logger = logging.getLogger(__name__)

COLLECTION = "vulcan_corpus"
_CHUNK_CHARS = 1100
_CHUNK_OVERLAP = 150


# ---------------------------------------------------------------------------
# Chroma client (persistent, singleton)
# ---------------------------------------------------------------------------
_client = None


def _vectordb_path() -> Path:
    s = get_settings()
    return s.package_root / "data" / "vectordb"


def get_client():
    """Return a cached persistent Chroma client at vulcan/data/vectordb/."""
    global _client
    if _client is not None:
        return _client
    import chromadb  # type: ignore[import]
    from chromadb.config import Settings as ChromaSettings  # type: ignore[import]

    path = _vectordb_path()
    path.mkdir(parents=True, exist_ok=True)
    _client = chromadb.PersistentClient(
        path=str(path),
        settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True),
    )
    logger.info("Chroma client at %s", path)
    return _client


def get_collection(create: bool = True):
    """Open (or create) the corpus collection. cosine space (BGE is normalized)."""
    client = get_client()
    if create:
        return client.get_or_create_collection(
            name=COLLECTION, metadata={"hnsw:space": "cosine"}
        )
    return client.get_collection(COLLECTION)


def collection_count() -> int:
    try:
        return get_collection(create=False).count()
    except Exception:  # noqa: BLE001
        return 0


# ---------------------------------------------------------------------------
# Heading-aware markdown chunker
# ---------------------------------------------------------------------------
_HEADING_RE = re.compile(r"^(#{1,4})\s+(.*)$")


def _split_markdown(text: str) -> list[tuple[str, str]]:
    """Split markdown into (section_title, body) blocks on headings, then pack
    each block into <= _CHUNK_CHARS pieces with overlap. Returns (section, chunk)."""
    lines = text.splitlines()
    blocks: list[tuple[str, list[str]]] = []
    cur_title = ""
    cur: list[str] = []
    for ln in lines:
        m = _HEADING_RE.match(ln.strip())
        if m:
            if cur:
                blocks.append((cur_title, cur))
            cur_title = m.group(2).strip()
            cur = []
        else:
            cur.append(ln)
    if cur:
        blocks.append((cur_title, cur))

    chunks: list[tuple[str, str]] = []
    for title, body_lines in blocks:
        body = "\n".join(body_lines).strip()
        if not body:
            continue
        if len(body) <= _CHUNK_CHARS:
            chunks.append((title, body))
            continue
        start = 0
        while start < len(body):
            piece = body[start:start + _CHUNK_CHARS]
            chunks.append((title, piece.strip()))
            start += _CHUNK_CHARS - _CHUNK_OVERLAP
    return [(t, c) for t, c in chunks if c.strip()]


# Descriptive SOP/keyword -> equipment_class map (SOP filenames use task words,
# not the snake_case class id, so a keyword map makes the prefilter usable).
_KEYWORD_CLASS = [
    ("bearing", "rolling_mill_work_roll_bearing"),
    ("gearbox", "mill_gearbox"),
    ("gear-service", "mill_gearbox"),
    ("motor", "large_induction_motor_vfd"),
    ("rewind", "large_induction_motor_vfd"),
    ("pump", "cooling_descaling_pump"),
    ("descal", "cooling_descaling_pump"),
    ("mechanical-seal", "cooling_descaling_pump"),
    ("fan", "bf_sinter_fan_blower"),
    ("blower", "bf_sinter_fan_blower"),
    ("surge", "bf_sinter_fan_blower"),
    ("segment", "continuous_caster_segment"),
    ("mould", "continuous_caster_mould"),
    ("mold", "continuous_caster_mould"),
    ("hot-strip-mill", "hot_strip_mill_stand"),
    ("roll-change", "hot_strip_mill_stand"),
    ("conveyor", "raw_material_conveyor"),
    ("idler", "raw_material_conveyor"),
    ("belt", "raw_material_conveyor"),
    ("crane", "ladle_crane"),
    ("wire-rope", "ladle_crane"),
    ("agc-servo", "hydraulics_agc_servo"),
    ("servo-valve", "hydraulics_agc_servo"),
    ("furnace", "reheating_furnace"),
    ("burner", "reheating_furnace"),
    ("refractory", "reheating_furnace"),
    ("eaf", "eaf_bof_auxiliary"),
]


def _equipment_class_for_doc(doc_id: str, text: str) -> str:
    """Tag a doc with an equipment_class. Deterministic, in priority order:

    1. Manual filenames embed the exact class (``MAN-005_bf_sinter_fan_blower``).
    2. RCA filenames embed the asset_id (``RCA-001-HSM-F3-WR-BRG01-...``) -> class.
    3. Descriptive keyword map (SOPs/domain docs use task words, not class ids).
    4. Full-class-name token match in the doc head (fallback).
    """
    sp = get_datastore().spine()
    classes = {a.equipment_class for a in sp.assets}
    lower_id = doc_id.lower()

    # 1. manual: the class id is literally a suffix of the filename
    for ec in classes:
        if ec in lower_id:
            return ec

    # 2. RCA: asset_id is embedded with '-' separators -> normalize and match
    nid = "".join(ch for ch in doc_id.upper() if ch.isalnum())
    for a in sp.assets:
        akey = "".join(ch for ch in a.asset_id.upper() if ch.isalnum())
        if akey and akey in nid:
            return a.equipment_class

    # 3. descriptive keyword map (covers SOPs + domain docs)
    blob = (doc_id + " " + text[:400]).lower()
    for kw, ec in _KEYWORD_CLASS:
        if kw in blob:
            return ec

    # 4. full-class-name token match in the head
    for ec in classes:
        toks = [t for t in ec.split("_") if len(t) > 3]
        if toks and all(t in blob for t in toks):
            return ec
    return ""


# ---------------------------------------------------------------------------
# Corpus assembly
# ---------------------------------------------------------------------------
@dataclass
class CorpusChunk:
    chunk_id: str
    text: str
    source: str          # filename — the citation ref
    doc_type: str        # equipment_manual | sop | rca_report | spare_catalog | domain
    doc_title: str
    section: str
    equipment_class: str


def _machinery_docs() -> list[tuple[Path, str]]:
    """research/machinery/*.md — domain references. Located relative to round_2/."""
    s = get_settings()
    # dataset_root = .../round_2/dataforge/datasets/steel-maintenance-flagship
    round2 = s.dataset_root.parents[2]      # -> .../round_2
    out: list[tuple[Path, str]] = []
    for sub in ("research/machinery", "research/domain"):
        d = round2 / sub
        if d.is_dir():
            for p in sorted(d.glob("*.md")):
                out.append((p, "domain"))
    return out


def build_corpus() -> list[CorpusChunk]:
    """Assemble all chunks (no embedding yet)."""
    ds = get_datastore()
    chunks: list[CorpusChunk] = []

    def add_md(doc_id: str, path: Path, doc_type: str, title: str, text: str,
               eq_hint: str = "") -> None:
        ec = eq_hint or _equipment_class_for_doc(doc_id, text)
        for i, (section, body) in enumerate(_split_markdown(text)):
            chunks.append(CorpusChunk(
                chunk_id=f"{doc_id}::{i}",
                text=body,
                source=path.name,
                doc_type=doc_type,
                doc_title=title,
                section=section or title,
                equipment_class=ec,
            ))

    # manuals + SOPs + RCA reports (from the typed loaders)
    for kd in ds.equipment_manuals():
        add_md(kd.doc_id, kd.path, "equipment_manual", kd.title, kd.text)
    for kd in ds.sops():
        add_md(kd.doc_id, kd.path, "sop", kd.title, kd.text)
    for kd in ds.rca_reports():
        add_md(kd.doc_id, kd.path, "rca_report", kd.title, kd.text)

    # domain references (machinery + domain research)
    for path, dtype in _machinery_docs():
        text = path.read_text(encoding="utf-8", errors="ignore")
        title = next((ln.lstrip("# ").strip() for ln in text.splitlines()
                      if ln.strip().startswith("#")), path.stem)
        add_md(path.stem, path, dtype, title, text)

    # spare-parts catalogue — one chunk per part (procurement facts, citable)
    cat_path = ds.settings.knowledge_dir / "spare_parts_catalog.csv"
    for c in ds.spare_catalog():
        body = (
            f"Spare part {c.part_id}: {c.name}. "
            f"Fits equipment class: {c.fits_equipment_class}. "
            f"Fits assets: {c.fits_asset_ids}. "
            f"On-hand quantity: {c.on_hand}; minimum stock: {c.min_qty}; "
            f"in stock: {c.in_stock}. Procurement lead-time: {c.lead_time_weeks} weeks. "
            f"Unit cost: {c.unit_cost}. Supplier: {c.supplier}. "
            f"Criticality class: {c.criticality}."
        )
        chunks.append(CorpusChunk(
            chunk_id=f"SPARE::{c.part_id}",
            text=body,
            source=cat_path.name,
            doc_type="spare_catalog",
            doc_title=f"Spare {c.part_id}",
            section=c.name,
            equipment_class=c.fits_equipment_class.split("|")[0] if c.fits_equipment_class else "",
        ))

    return chunks


# ---------------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------------
def ingest(rebuild: bool = True, batch_size: int = 64) -> dict[str, Any]:
    """Build the corpus, embed, and upsert into Chroma.

    ``rebuild=True`` drops the existing collection first (idempotent rebuild)."""
    client = get_client()
    if rebuild:
        try:
            client.delete_collection(COLLECTION)
            logger.info("Dropped existing collection for rebuild.")
        except Exception:  # noqa: BLE001
            pass
    coll = client.get_or_create_collection(
        name=COLLECTION, metadata={"hnsw:space": "cosine"}
    )

    chunks = build_corpus()
    if not chunks:
        return {"ingested": 0, "error": "no chunks assembled"}

    type_counts: dict[str, int] = {}
    for c in chunks:
        type_counts[c.doc_type] = type_counts.get(c.doc_type, 0) + 1

    total = 0
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start:start + batch_size]
        embs = embed_texts([c.text for c in batch])
        coll.add(
            ids=[c.chunk_id for c in batch],
            embeddings=embs.tolist(),
            documents=[c.text for c in batch],
            metadatas=[{
                "source": c.source,
                "doc_type": c.doc_type,
                "doc_title": c.doc_title,
                "section": c.section,
                "equipment_class": c.equipment_class,
            } for c in batch],
        )
        total += len(batch)

    return {
        "ingested": total,
        "collection": COLLECTION,
        "embedding_dim": EMBED_DIM,
        "by_doc_type": type_counts,
        "vectordb_path": str(_vectordb_path()),
    }


if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO)
    print(json.dumps(ingest(rebuild=True), indent=2))
