"""VULCAN RAG retrieval — Chroma dense retrieve -> FlashRank rerank -> top-k.

`retrieve(query)` returns reranked `RetrievedChunk` objects, each carrying its
`source` filename so the agent can cite it inline (FR4: explainable + traceable).
Optional `equipment_class` / `doc_types` metadata prefilter narrows the candidate
pool before scoring. No LLM, no HyDE (the wizard's HyDE used an LLM key — dropped):
local hybrid dense + cross-encoder rerank already covers retrieval, keyless.
"""

from __future__ import annotations

import logging
import os
import tempfile
from dataclasses import dataclass
from typing import Optional

from .embedder import embed_single
from .store import COLLECTION, get_client

logger = logging.getLogger(__name__)

RERANKER_MODEL = "ms-marco-MiniLM-L-12-v2"
_TOP_K_RETRIEVE = 20
_TOP_K_FINAL = 5


@dataclass
class RetrievedChunk:
    chunk_id: str
    text: str
    source: str           # filename — the citation ref
    doc_type: str
    doc_title: str
    section: str
    equipment_class: str
    dense_score: float    # cosine similarity (1 - distance)
    rerank_score: float
    faithfulness_score: float = 0.0   # filled by the NLI gate, if run

    def citation(self) -> str:
        """One-line inline citation string, e.g. `[MAN-005_bf_sinter_fan_blower.md § Surge]`."""
        sec = f" § {self.section}" if self.section and self.section != self.doc_title else ""
        return f"[{self.source}{sec}]"

    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk_id,
            "source": self.source,
            "doc_type": self.doc_type,
            "doc_title": self.doc_title,
            "section": self.section,
            "equipment_class": self.equipment_class,
            "dense_score": round(self.dense_score, 4),
            "rerank_score": round(self.rerank_score, 4),
            "faithfulness_score": round(self.faithfulness_score, 4),
            "text_preview": self.text[:200],
            "citation": self.citation(),
        }


# ---------------------------------------------------------------------------
# FlashRank reranker singleton
# ---------------------------------------------------------------------------
_ranker = None


def _get_ranker():
    global _ranker
    if _ranker is None:
        from flashrank import Ranker  # type: ignore[import]
        cache = os.path.join(tempfile.gettempdir(), "vulcan_flashrank")
        os.makedirs(cache, exist_ok=True)
        _ranker = Ranker(model_name=RERANKER_MODEL, cache_dir=cache)
        logger.info("FlashRank ranker loaded: %s", RERANKER_MODEL)
    return _ranker


# ---------------------------------------------------------------------------
# retrieve
# ---------------------------------------------------------------------------
def retrieve(
    query: str,
    equipment_class: Optional[str] = None,
    doc_types: Optional[list[str]] = None,
    top_k: int = _TOP_K_FINAL,
    n_candidates: int = _TOP_K_RETRIEVE,
) -> list[RetrievedChunk]:
    """Dense retrieve from Chroma, then FlashRank rerank to top_k.

    Returns [] if the collection is empty or unreachable (fail-soft)."""
    try:
        coll = get_client().get_collection(COLLECTION)
    except Exception as exc:  # noqa: BLE001
        logger.warning("RAG collection unavailable (%s) — did you ingest()?", exc)
        return []
    if coll.count() == 0:
        logger.warning("RAG collection is empty.")
        return []

    where: dict | None = None
    clauses = []
    if equipment_class:
        clauses.append({"equipment_class": equipment_class})
    if doc_types:
        clauses.append({"doc_type": {"$in": list(doc_types)}})
    if len(clauses) == 1:
        where = clauses[0]
    elif len(clauses) > 1:
        where = {"$and": clauses}

    try:
        qvec = embed_single(query)
        res = coll.query(
            query_embeddings=[qvec],
            n_results=min(n_candidates, coll.count()),
            where=where,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Chroma query failed (%s) — retrying without prefilter.", exc)
        try:
            res = coll.query(
                query_embeddings=[qvec],
                n_results=min(n_candidates, coll.count()),
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc2:  # noqa: BLE001
            logger.error("Chroma query failed entirely: %s", exc2)
            return []

    ids = res.get("ids", [[]])[0]
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]
    if not docs:
        return []

    candidates = []
    for cid, doc, meta, dist in zip(ids, docs, metas, dists):
        meta = meta or {}
        candidates.append({
            "chunk_id": cid, "text": doc, "meta": meta,
            "dense_score": float(1.0 - dist),
        })

    # FlashRank rerank
    try:
        from flashrank import RerankRequest  # type: ignore[import]
        ranker = _get_ranker()
        passages = [{"id": i, "text": c["text"]} for i, c in enumerate(candidates)]
        reranked = ranker.rerank(RerankRequest(query=query, passages=passages))
        order = []
        for item in reranked[:top_k]:
            idx = item["id"] if isinstance(item, dict) else item.id
            score = item["score"] if isinstance(item, dict) else item.score
            order.append((idx, float(score)))
    except Exception as exc:  # noqa: BLE001
        logger.warning("FlashRank unavailable (%s) — using dense order.", exc)
        order = [(i, candidates[i]["dense_score"]) for i in range(min(top_k, len(candidates)))]

    out: list[RetrievedChunk] = []
    for idx, rr_score in order:
        if idx >= len(candidates):
            continue
        c = candidates[idx]
        m = c["meta"]
        out.append(RetrievedChunk(
            chunk_id=c["chunk_id"],
            text=c["text"],
            source=str(m.get("source", "")),
            doc_type=str(m.get("doc_type", "")),
            doc_title=str(m.get("doc_title", "")),
            section=str(m.get("section", "")),
            equipment_class=str(m.get("equipment_class", "")),
            dense_score=c["dense_score"],
            rerank_score=rr_score,
        ))
    return out


def format_context(chunks: list[RetrievedChunk]) -> str:
    """Numbered `Source [N]` context block for LLM prompt injection (cited)."""
    parts = []
    for i, c in enumerate(chunks, start=1):
        sec = f" § {c.section}" if c.section else ""
        parts.append(f"Source [{i}] ({c.source}{sec}):\n{c.text}")
    return "\n\n".join(parts)


def sources(chunks: list[RetrievedChunk]) -> list[dict]:
    """Distinct source files behind a retrieval, for the citation panel."""
    seen: dict[str, dict] = {}
    for c in chunks:
        seen.setdefault(c.source, {"source": c.source, "doc_type": c.doc_type,
                                   "doc_title": c.doc_title})
    return list(seen.values())
