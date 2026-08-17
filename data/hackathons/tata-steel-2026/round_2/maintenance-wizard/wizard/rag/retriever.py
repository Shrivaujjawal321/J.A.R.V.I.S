"""
wizard.rag.retriever
====================
Hybrid retrieval pipeline: LanceDB native hybrid (dense + BM25) → FlashRank rerank → top-k.

Key features:
  - LanceDB native hybrid search (query_type="hybrid") — dense + Tantivy BM25 in one call.
  - SQL ``where()`` prefilter on ``equipment_id`` and/or ``doc_type`` before scoring.
  - HyDE (Hypothetical Document Embedding) for short queries (<= 12 tokens).
  - FlashRank cross-encoder rerank (ms-marco-MiniLM-L-12-v2, ONNX, ~15–30ms/30 candidates).
  - Returns top-k ``RetrievedChunk`` Pydantic objects ready for citation injection.

Latency budget on a modern laptop CPU:
  - Embed query:  ~5–10 ms  (bge-small ONNX)
  - HyDE call:    ~300–800 ms  (optional, skipped if disabled or fast path)
  - LanceDB hybrid query: ~5–15 ms
  - FlashRank rerank (30 candidates): ~15–30 ms
  Total (without HyDE): ~30–60 ms  — well under 2s budget.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Optional

from wizard.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SQL injection defence — LanceDB where() clauses are SQL strings, so we
# must sanitize any user-controlled values before interpolation.
# ---------------------------------------------------------------------------

_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9_./-]+$")  # equipment IDs, asset tags

# Characters that are unsafe in SQL string literals even after quote-escaping:
# semicolons (statement termination), parens (subqueries), forward-slash + star
# (comment openers), backslash (escape sequences in some SQL dialects).
_FORBIDDEN_SQL_RE = re.compile(r"[;()/\\*]")


def _escape_sql_string(value: str) -> str:
    """
    Escape a string value for safe interpolation into a LanceDB SQL where-clause.
    Escapes single-quotes (SQL injection vector) and rejects values that still
    contain structurally dangerous characters after quote-escaping.

    Raises ValueError for values with non-whitelisted characters — these should
    never appear in legitimate equipment IDs or doc types.
    """
    # Replace single-quote with doubled single-quote (standard SQL escaping)
    escaped = value.replace("'", "''")
    if _FORBIDDEN_SQL_RE.search(escaped):
        raise ValueError(
            f"Unsafe character in filter value after escaping: {escaped!r}"
        )
    return escaped

# ---------------------------------------------------------------------------
# Output schema
# ---------------------------------------------------------------------------

@dataclass
class RetrievedChunk:
    """
    A single retrieved + reranked chunk with full citation metadata.

    Used by the NLI gate, agents, and UI citation renderer.
    """
    chunk_id: str
    text: str
    doc_name: str
    section: str
    page_or_step: str
    doc_type: str
    equipment_id: str
    asset_id: str
    criticality: str
    rerank_score: float
    hybrid_score: float = 0.0
    faithfulness_score: float = 0.0  # filled by NLI gate

    def to_citation_dict(self) -> dict:
        """Serialise for inclusion in a ``cited_sources`` list."""
        return {
            "chunk_id": self.chunk_id,
            "doc_name": self.doc_name,
            "section": self.section,
            "page_or_step": self.page_or_step,
            "doc_type": self.doc_type,
            "text_preview": self.text[:200],
            "rerank_score": round(self.rerank_score, 4),
            "faithfulness_score": round(self.faithfulness_score, 4),
        }


# ---------------------------------------------------------------------------
# Lazy singletons (loaded on first call)
# ---------------------------------------------------------------------------

_flashrank_ranker = None


def _get_ranker():
    """Return the FlashRank Ranker singleton (loaded once)."""
    global _flashrank_ranker
    if _flashrank_ranker is None:
        try:
            from flashrank import Ranker  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "flashrank is required. Run: pip install flashrank"
            ) from exc
        # FlashRank needs a real cache_dir string; None raises a path TypeError.
        import os, tempfile
        _cache = os.path.join(tempfile.gettempdir(), "flashrank_cache")
        os.makedirs(_cache, exist_ok=True)
        _flashrank_ranker = Ranker(
            model_name=settings.reranker_model,  # ms-marco-MiniLM-L-12-v2
            cache_dir=_cache,
        )
        logger.info("FlashRank ranker loaded: %s", settings.reranker_model)
    return _flashrank_ranker


# ---------------------------------------------------------------------------
# HyDE helper
# ---------------------------------------------------------------------------

def _generate_hyde(query: str) -> str:
    """
    Generate a hypothetical answer paragraph for the query.
    Uses the light LLM (Gemini Flash / Haiku) — adds ~300–800ms.

    Falls back to the original query on any error.
    """
    try:
        import litellm  # type: ignore[import]

        prompt = (
            "You are a steel-plant maintenance expert. "
            "Write a 2-3 sentence factual answer about the following maintenance query. "
            "Write as if from an official maintenance manual or SOP. "
            "Be specific about equipment, procedures, and thresholds.\n\n"
            f"Query: {query}\n\n"
            "Hypothetical answer:"
        )
        response = litellm.completion(
            model=settings.llm_model_light,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120,
            temperature=0.2,
        )
        hypothesis = response.choices[0].message.content.strip()
        logger.debug("HyDE generated: %s...", hypothesis[:80])
        return hypothesis if hypothesis else query
    except Exception as exc:
        logger.debug("HyDE generation failed: %s — using original query.", exc)
        return query


# ---------------------------------------------------------------------------
# Core retrieval function
# ---------------------------------------------------------------------------

def retrieve(
    query: str,
    equipment_id: Optional[str] = None,
    doc_types: Optional[list[str]] = None,
    top_k: Optional[int] = None,
    use_hyde: Optional[bool] = None,
    db=None,
) -> list[RetrievedChunk]:
    """
    Hybrid retrieval with FlashRank rerank.

    Parameters
    ----------
    query:
        Natural-language engineer query.
    equipment_id:
        If provided, prefilter chunks to this equipment (SQL ``where()``).
    doc_types:
        If provided, prefilter to these doc types (e.g. ``['SOP', 'manual']``).
    top_k:
        Number of final ranked results to return (default: settings.rag_top_k_final = 5).
    use_hyde:
        Override HyDE toggle. If None, uses settings.rag_hyde_enabled.
    db:
        Open LanceDB connection (auto-opened if None).

    Returns
    -------
    list[RetrievedChunk]
        Reranked chunks, best first. Empty list if store is empty.
    """
    from wizard.rag.store import get_store, TABLE_NAME
    from wizard.rag.embedder import embed_single

    top_k = top_k if top_k is not None else settings.rag_top_k_final
    n_candidates = settings.rag_top_k_retrieve  # default 20

    db = db or get_store()

    # Guard: empty table
    try:
        table = db.open_table(TABLE_NAME)
        row_count = table.count_rows()
        if row_count == 0:
            logger.warning("RAG store is empty — no chunks to retrieve.")
            return []
    except Exception as exc:
        logger.error("Could not open LanceDB table: %s", exc)
        return []

    # HyDE: expand short queries
    hyde_enabled = use_hyde if use_hyde is not None else settings.rag_hyde_enabled
    query_for_embed = query
    if hyde_enabled and len(query.split()) <= 12:
        query_for_embed = _generate_hyde(query)

    # Embed the (possibly expanded) query
    try:
        query_vec = embed_single(query_for_embed)
    except Exception as exc:
        logger.error("Query embedding failed: %s", exc)
        return []

    # Build prefilter SQL — sanitize all values before interpolation to prevent
    # SQL injection through the LanceDB where() string API.
    filter_clauses: list[str] = []
    if equipment_id:
        try:
            safe_eid = _escape_sql_string(equipment_id)
        except ValueError as exc:
            logger.warning("Rejected unsafe equipment_id in filter: %s", exc)
            safe_eid = None
        if safe_eid is not None:
            filter_clauses.append(f"equipment_id = '{safe_eid}'")
    if doc_types:
        safe_types: list[str] = []
        for t in doc_types:
            try:
                safe_types.append(_escape_sql_string(t))
            except ValueError as exc:
                logger.warning("Rejected unsafe doc_type in filter: %s", exc)
        if safe_types:
            types_sql = ", ".join(f"'{t}'" for t in safe_types)
            filter_clauses.append(f"doc_type IN ({types_sql})")
    where_clause = " AND ".join(filter_clauses) if filter_clauses else None

    # LanceDB hybrid search (dense + BM25).
    #
    # lancedb >=0.33 API (LanceHybridQueryBuilder):
    #   table.search(query_type="hybrid")   ← NO positional query arg
    #       .vector(query_vec)              ← dense side
    #       .text(query_string)             ← BM25 / FTS side
    #       .where(...)                     ← optional prefilter
    #       .limit(n)
    #
    # The old API (table.search(vec, query_type="hybrid").with_query(str)) was
    # removed — with_query() does not exist in 0.33.x.
    # Passing a vector positionally AND calling .text() raises ValueError in 0.33.
    #
    # Fallback: if FTS index is missing (fresh table, no data yet) lancedb raises;
    # we catch and fall back to dense-only vector search.
    try:
        search = (
            table.search(query_type="hybrid")
            .vector(query_vec)
            .text(query)  # BM25 text query (requires FTS index on 'text' column)
        )

        if where_clause:
            search = search.where(where_clause, prefilter=True)

        results_df = search.limit(n_candidates).to_pandas()
        logger.debug("Hybrid search (dense+BM25) returned %d candidates.", len(results_df))
    except Exception as exc:
        logger.warning(
            "Hybrid search failed (%s) — falling back to dense-only search.", exc
        )
        try:
            search = table.search(query_vec, query_type="vector", vector_column_name="vector")
            if where_clause:
                search = search.where(where_clause, prefilter=True)
            results_df = search.limit(n_candidates).to_pandas()
        except Exception as exc2:
            logger.error("Dense-only search also failed: %s", exc2)
            return []

    if results_df is None or len(results_df) == 0:
        logger.warning("No candidates retrieved for query: %s", query[:60])
        return []

    # FlashRank rerank
    try:
        from flashrank import Ranker, RerankRequest  # type: ignore[import]

        ranker = _get_ranker()
        passages = [
            {"id": i, "text": row["text"]}
            for i, (_, row) in enumerate(results_df.iterrows())
        ]
        rerank_req = RerankRequest(query=query, passages=passages)
        reranked = ranker.rerank(rerank_req)

        # Map back to rows
        ranked_rows: list[RetrievedChunk] = []
        for reranked_item in reranked[:top_k]:
            # FlashRank returns a list of dicts ({"id","text","score"}); guard for
            # object-style results across versions.
            idx = reranked_item["id"] if isinstance(reranked_item, dict) else reranked_item.id
            if idx >= len(results_df):
                continue
            row = results_df.iloc[idx]
            _rr_score = (
                reranked_item["score"] if isinstance(reranked_item, dict)
                else reranked_item.score
            )

            hybrid_score = float(row.get("_relevance_score", row.get("score", 0.0)))

            chunk = RetrievedChunk(
                chunk_id=str(row.get("chunk_id", "")),
                text=str(row.get("text", "")),
                doc_name=str(row.get("doc_name", "")),
                section=str(row.get("section", "")),
                page_or_step=str(row.get("page_or_step", "")),
                doc_type=str(row.get("doc_type", "")),
                equipment_id=str(row.get("equipment_id", "")),
                asset_id=str(row.get("asset_id", "")),
                criticality=str(row.get("criticality", "medium")),
                rerank_score=float(_rr_score),
                hybrid_score=hybrid_score,
            )
            ranked_rows.append(chunk)

        logger.debug(
            "Retrieved %d chunks (from %d candidates) for query: %s...",
            len(ranked_rows), len(results_df), query[:60],
        )
        return ranked_rows

    except ImportError:
        # FlashRank not installed — return LanceDB results directly
        logger.warning("FlashRank not available — returning unranked hybrid results.")
        return _rows_to_chunks(results_df.head(top_k))

    except Exception as exc:
        logger.warning("FlashRank rerank failed (%s) — returning hybrid results.", exc)
        return _rows_to_chunks(results_df.head(top_k))


def _rows_to_chunks(df) -> list[RetrievedChunk]:
    """Convert a pandas DataFrame of LanceDB results to RetrievedChunk objects."""
    result = []
    for _, row in df.iterrows():
        score = float(row.get("_relevance_score", row.get("score", 0.0)))
        chunk = RetrievedChunk(
            chunk_id=str(row.get("chunk_id", "")),
            text=str(row.get("text", "")),
            doc_name=str(row.get("doc_name", "")),
            section=str(row.get("section", "")),
            page_or_step=str(row.get("page_or_step", "")),
            doc_type=str(row.get("doc_type", "")),
            equipment_id=str(row.get("equipment_id", "")),
            asset_id=str(row.get("asset_id", "")),
            criticality=str(row.get("criticality", "medium")),
            rerank_score=score,
            hybrid_score=score,
        )
        result.append(chunk)
    return result


# ---------------------------------------------------------------------------
# Convenience: format retrieved chunks for LLM context injection
# ---------------------------------------------------------------------------

def format_context_block(chunks: list[RetrievedChunk]) -> str:
    """
    Format retrieved chunks as a numbered ``Source [N]`` context block
    for injection into LLM generation prompts.

    Example output::

        Source [1] (BF-SOP-001, § 3.4 Cooling Valve, p.12):
        The cooling water valve must be inspected every 500 operating hours...

        Source [2] (Rolling-Mill-Manual, § 5.1 Bearing Maintenance, p.34):
        Bearing temperature exceeding 85°C indicates early-stage lubrication failure...
    """
    parts: list[str] = []
    for i, chunk in enumerate(chunks, start=1):
        header = f"Source [{i}] ({chunk.doc_name}, § {chunk.section}, p.{chunk.page_or_step}):"
        parts.append(f"{header}\n{chunk.text}")
    return "\n\n".join(parts)


def chunks_to_cited_sources(chunks: list[RetrievedChunk]) -> list[dict]:
    """
    Convert chunks to the ``cited_sources`` list format expected by
    ``DiagnosisReport.cited_sources`` and the Streamlit citation renderer.
    """
    return [c.to_citation_dict() for c in chunks]
