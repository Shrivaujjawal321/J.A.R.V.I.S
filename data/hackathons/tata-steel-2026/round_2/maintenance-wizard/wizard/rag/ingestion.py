"""
wizard.rag.ingestion
====================
Document ingestion pipeline for the Maintenance Wizard RAG layer.

Pipeline:
  1. Load source: PDF (pymupdf4llm → Markdown) or raw Markdown/text string.
  2. Split by headers: MarkdownHeaderTextSplitter (## / ###).
  3. Secondary split: RecursiveCharacterTextSplitter (512 chars / 64 overlap).
  4. Optional contextual prefix injection via LLM (Haiku/Gemini Flash).
  5. Embed each chunk: BAAI/bge-small-en-v1.5 (ONNX).
  6. Insert into LanceDB ``chunks`` table with full metadata.
  7. Build/refresh FTS (Tantivy) index.

Handles empty directories gracefully — logs a warning and returns 0.
Idempotent: chunks with the same chunk_id are skipped on re-ingest.
"""

from __future__ import annotations

import datetime
from datetime import timezone
import hashlib
import logging
import os
from pathlib import Path
from typing import Optional

from wizard.core.config import settings
# DocumentRecord and _new_ulid are intentionally NOT imported here.
# chunk_id is a deterministic sha256 prefix (idempotent dedup); DocumentRecord
# is only used by external callers that need a typed envelope, not by ingestion
# internals.  Source cross-referenceability is preserved via source_entity_id
# stored on every LanceDB row (see _embed_and_insert).

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Chunking constants
# ---------------------------------------------------------------------------
HEADERS_TO_SPLIT = [
    ("##", "section"),
    ("###", "subsection"),
]
CHUNK_SIZE = settings.rag_chunk_size      # 512 chars
CHUNK_OVERLAP = settings.rag_chunk_overlap  # 64 chars


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------

def ingest_directory(
    directory: Path,
    asset_id: str = "unknown",
    equipment_id: str = "unknown",
    equipment_type: str = "unknown",
    doc_type: str = "manual",
    criticality: str = "medium",
    revision: str = "",
    use_contextual_prefix: bool = False,
    db=None,
) -> int:
    """
    Ingest all PDF + Markdown files in ``directory`` into LanceDB.

    Parameters
    ----------
    directory:
        Directory containing source documents.
    asset_id:
        Asset/equipment ID to tag all chunks with (used for prefilter).
    equipment_id:
        Specific equipment tag (may differ from asset_id for scoping).
    equipment_type:
        Equipment class string (e.g. 'bearing', 'fan', 'pump').
    doc_type:
        Document type: 'manual'|'sop'|'failure_analysis'|'incident_summary'.
    criticality:
        'critical'|'high'|'medium'|'low'.
    revision:
        Document revision identifier.
    use_contextual_prefix:
        If True, call the LLM to generate a one-sentence context prefix per chunk.
        Disabled by default to avoid API calls during offline tests.
    db:
        Open LanceDB connection (auto-opened if None).

    Returns
    -------
    int: number of chunks inserted.
    """
    directory = Path(directory)
    if not directory.exists():
        logger.warning("ingest_directory: path does not exist: %s — skipping.", directory)
        return 0

    files = list(directory.glob("*.pdf")) + list(directory.glob("*.md")) + list(directory.glob("*.txt"))
    if not files:
        logger.warning("ingest_directory: no PDF/MD/TXT files found in %s — skipping.", directory)
        return 0

    total = 0
    for filepath in files:
        count = ingest_file(
            filepath=filepath,
            asset_id=asset_id,
            equipment_id=equipment_id,
            equipment_type=equipment_type,
            doc_type=doc_type,
            criticality=criticality,
            revision=revision,
            use_contextual_prefix=use_contextual_prefix,
            db=db,
        )
        total += count

    logger.info("ingest_directory: ingested %d chunks from %s", total, directory)
    return total


def ingest_file(
    filepath: Path,
    asset_id: str = "unknown",
    equipment_id: str = "unknown",
    equipment_type: str = "unknown",
    doc_type: str = "manual",
    criticality: str = "medium",
    revision: str = "",
    use_contextual_prefix: bool = False,
    db=None,
) -> int:
    """
    Ingest a single PDF or Markdown file into LanceDB.

    Returns number of chunks inserted.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        logger.warning("ingest_file: file not found: %s", filepath)
        return 0

    doc_name = filepath.stem

    # Step 1: Load to Markdown
    markdown_text = _load_to_markdown(filepath)
    if not markdown_text or not markdown_text.strip():
        logger.warning("ingest_file: empty content after loading %s — skipping.", filepath)
        return 0

    # Step 2+3: Chunk
    chunks = _chunk_markdown(markdown_text, doc_name=doc_name)
    if not chunks:
        logger.warning("ingest_file: no chunks produced from %s — skipping.", filepath)
        return 0

    # Step 4: Optional contextual prefix injection
    if use_contextual_prefix:
        chunks = _inject_contextual_prefixes(chunks, doc_name=doc_name, doc_type=doc_type)

    # Step 5+6: Embed + insert
    count = _embed_and_insert(
        chunks=chunks,
        asset_id=asset_id,
        equipment_id=equipment_id,
        equipment_type=equipment_type,
        doc_type=doc_type,
        criticality=criticality,
        revision=revision,
        db=db,
    )
    logger.info("ingest_file: %d chunks from '%s'", count, filepath.name)
    return count


def ingest_text(
    text: str,
    doc_name: str,
    asset_id: str = "unknown",
    equipment_id: str = "unknown",
    equipment_type: str = "unknown",
    doc_type: str = "manual",
    criticality: str = "medium",
    revision: str = "",
    source_entity_id: str = "",
    source_entity_type: str = "knowledge_doc",
    use_contextual_prefix: bool = False,
    db=None,
) -> int:
    """
    Ingest raw Markdown/text string directly — used by the knowledge module
    which generates synthetic docs programmatically.

    Returns number of chunks inserted.
    """
    if not text or not text.strip():
        logger.warning("ingest_text: empty text for doc '%s' — skipping.", doc_name)
        return 0

    chunks = _chunk_markdown(text, doc_name=doc_name)
    if not chunks:
        return 0

    if use_contextual_prefix:
        chunks = _inject_contextual_prefixes(chunks, doc_name=doc_name, doc_type=doc_type)

    count = _embed_and_insert(
        chunks=chunks,
        asset_id=asset_id,
        equipment_id=equipment_id,
        equipment_type=equipment_type,
        doc_type=doc_type,
        criticality=criticality,
        revision=revision,
        source_entity_id=source_entity_id,
        source_entity_type=source_entity_type,
        db=db,
    )
    return count


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_to_markdown(filepath: Path) -> str:
    """Convert PDF to Markdown using pymupdf4llm; read MD/TXT as-is."""
    suffix = filepath.suffix.lower()

    if suffix == ".pdf":
        try:
            import pymupdf4llm  # type: ignore[import]
            return pymupdf4llm.to_markdown(str(filepath))
        except ImportError:
            logger.warning(
                "pymupdf4llm not installed — cannot parse PDF %s. "
                "Install: pip install pymupdf4llm",
                filepath.name,
            )
            return ""
        except Exception as exc:
            logger.warning("Failed to parse PDF %s: %s", filepath.name, exc)
            return ""

    # Markdown or plain text — read directly
    try:
        return filepath.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        logger.warning("Failed to read file %s: %s", filepath.name, exc)
        return ""


def _chunk_markdown(
    markdown_text: str,
    doc_name: str,
) -> list[dict]:
    """
    Two-stage chunking:
      1. MarkdownHeaderTextSplitter  → section-aligned chunks
      2. RecursiveCharacterTextSplitter → token-bounded secondary split

    Returns list of dicts with keys:
      text, section, subsection, page_or_step
    """
    try:
        from langchain_text_splitters import (  # type: ignore[import]
            MarkdownHeaderTextSplitter,
            RecursiveCharacterTextSplitter,
        )
    except ImportError as exc:
        raise ImportError(
            "langchain-text-splitters is required. "
            "Run: pip install langchain-text-splitters"
        ) from exc

    # Stage 1: header-aware split
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS_TO_SPLIT,
        strip_headers=False,  # keep header text in chunk for context
    )
    try:
        header_docs = header_splitter.split_text(markdown_text)
    except Exception as exc:
        logger.warning("Header splitting failed for '%s': %s — using full text.", doc_name, exc)
        # Fallback: treat entire document as one chunk
        header_docs = []
        class _FakeDoc:
            page_content = markdown_text
            metadata: dict = {}
        header_docs = [_FakeDoc()]

    # Stage 2: recursive character split within each section
    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    result: list[dict] = []
    for doc in header_docs:
        sub_docs = char_splitter.split_text(doc.page_content)
        meta = getattr(doc, "metadata", {}) or {}
        section = meta.get("section", meta.get("Header 1", meta.get("Header 2", "")))
        subsection = meta.get("subsection", meta.get("Header 3", ""))

        for i, sub_text in enumerate(sub_docs):
            if not sub_text.strip():
                continue
            result.append({
                "text": sub_text.strip(),
                "section": section or "General",
                "subsection": subsection or "",
                "page_or_step": str(i + 1),  # within-section chunk index
            })

    return result


def _inject_contextual_prefixes(
    chunks: list[dict],
    doc_name: str,
    doc_type: str,
) -> list[dict]:
    """
    Prepend a one-sentence context to each chunk using the LLM.

    Anthropic Contextual Retrieval pattern — reduces retrieval failure 49–67%.
    Falls back gracefully if LLM is unavailable.

    NOTE: Costs ~$0.15 for 500 chunks at Haiku pricing (one-time, cached).
    Only call when ``use_contextual_prefix=True``.
    """
    try:
        import litellm  # type: ignore[import]
    except ImportError:
        logger.warning("litellm not available — skipping contextual prefix injection.")
        return chunks

    prefixed: list[dict] = []
    model = settings.llm_model_light  # Haiku-class — cheapest

    for chunk in chunks:
        try:
            prompt = (
                f"Document: {doc_name} (type: {doc_type}, section: {chunk['section']}).\n"
                f"Chunk text:\n{chunk['text'][:400]}\n\n"
                "Write ONE sentence (max 30 words) that describes what equipment, "
                "procedure, or specification this chunk covers. "
                "Start with: 'This chunk describes...'"
            )
            response = litellm.completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=60,
                temperature=0.0,
            )
            prefix = response.choices[0].message.content.strip()
            new_text = f"{prefix}\n\n{chunk['text']}"
        except Exception as exc:
            logger.debug("Contextual prefix failed for chunk in '%s': %s", doc_name, exc)
            new_text = chunk["text"]

        prefixed.append({**chunk, "text": new_text})

    return prefixed


def _embed_and_insert(
    chunks: list[dict],
    asset_id: str,
    equipment_id: str,
    equipment_type: str,
    doc_type: str,
    criticality: str,
    revision: str,
    source_entity_id: str = "",
    source_entity_type: str = "knowledge_doc",
    db=None,
) -> int:
    """
    Embed all chunk texts and insert into LanceDB.
    Skips chunks whose chunk_id already exists (idempotent).
    """
    from wizard.rag.store import get_store, ensure_fts_index, TABLE_NAME
    from wizard.rag.embedder import embed_texts

    if not chunks:
        return 0

    db = db or get_store()

    # Embed all texts in one batch call
    texts = [c["text"] for c in chunks]
    try:
        vectors = embed_texts(texts)
    except Exception as exc:
        logger.error("Embedding failed: %s — skipping insert.", exc)
        return 0

    now_utc = datetime.datetime.now(timezone.utc)

    rows: list[dict] = []
    for chunk, vec in zip(chunks, vectors):
        # Deterministic chunk_id from content hash so re-ingest is idempotent
        content_hash = hashlib.sha256(chunk["text"].encode()).hexdigest()[:16]
        chunk_id = f"chk_{content_hash}"

        row = {
            "chunk_id": chunk_id,
            "source_entity_id": source_entity_id or chunk_id,
            "source_entity_type": source_entity_type,
            "asset_id": asset_id,
            "text": chunk["text"],
            "doc_type": doc_type,
            "doc_name": chunk.get("doc_name", asset_id),
            "section": chunk.get("section", ""),
            "page_or_step": chunk.get("page_or_step", ""),
            "equipment_id": equipment_id,
            "equipment_type": equipment_type,
            "criticality": criticality,
            "revision": revision,
            "embedding_model": settings.embedding_model,
            "char_count": len(chunk["text"]),
            "ingested_at": now_utc,
            "vector": vec.tolist(),
        }
        rows.append(row)

    if not rows:
        return 0

    table = db.open_table(TABLE_NAME)

    # Dedup: fetch all existing chunk_ids.
    # LanceDB >=0.20 requires a query vector for table.search(); for a full
    # column scan without ANN we use table.to_arrow() (reads Lance columnar
    # format directly, no query vector required, no pylance dependency).
    # We then extract only the chunk_id column from the resulting Arrow table.
    try:
        all_rows = table.to_arrow()
        existing_ids: set[str] = set(all_rows["chunk_id"].to_pylist())
    except Exception:
        existing_ids = set()

    new_rows = [r for r in rows if r["chunk_id"] not in existing_ids]
    if not new_rows:
        logger.debug("All %d chunks already exist — nothing new to insert.", len(rows))
        return 0

    try:
        table.add(new_rows)
        logger.info("Inserted %d new chunks into LanceDB.", len(new_rows))
    except Exception as exc:
        logger.error("LanceDB insert failed: %s", exc)
        return 0

    # Refresh FTS index after insert
    ensure_fts_index(db)

    return len(new_rows)
