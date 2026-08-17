"""
wizard.rag.store
================
LanceDB embedded vector store for the Maintenance Wizard RAG layer.

Responsibilities:
  - Create / open the LanceDB connection and the ``chunks`` table.
  - Define the PyArrow schema (384-dim bge-small-en-v1.5 vectors + metadata).
  - Build and maintain the FTS (Tantivy BM25) full-text index.
  - Expose a single ``get_store()`` factory (cached singleton).

The table schema mirrors ``DocumentRecord`` from wizard.core.schemas so that
every chunk inserted here can be cross-referenced back to the originating
KnowledgeDocument or MaintenanceRecord.

LanceDB version: >=0.20.0  (native hybrid search, Lance columnar format).
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Optional

import pyarrow as pa

from wizard.core.config import settings

logger = logging.getLogger(__name__)

# Module-level connection cache keyed by resolved absolute path string.
# Prevents APScheduler + Streamlit from opening multiple handles to the same
# LanceDB directory (causes "database is locked" / corruption under concurrency).
_db_cache: dict[str, Any] = {}

# ---------------------------------------------------------------------------
# PyArrow schema — matches DocumentRecord fields + vector
# ---------------------------------------------------------------------------

EMBEDDING_DIM = settings.embedding_dim  # 384 for bge-small-en-v1.5

CHUNKS_SCHEMA = pa.schema([
    pa.field("chunk_id", pa.string()),                            # DocumentRecord.chunk_id (ULID)
    pa.field("source_entity_id", pa.string()),                    # FK → EntityBase.entity_id
    pa.field("source_entity_type", pa.string()),                  # e.g. 'knowledge_doc'
    pa.field("asset_id", pa.string()),                            # propagated for prefilter
    pa.field("text", pa.string()),                                # chunk text (embedded + FTS)
    pa.field("doc_type", pa.string()),                            # 'manual'|'sop'|'failure_analysis'|…
    pa.field("doc_name", pa.string()),                            # human-readable document title
    pa.field("section", pa.string()),                             # '§ 4.2 — Descaler Valve'
    pa.field("page_or_step", pa.string()),                        # page number or procedure step
    pa.field("equipment_id", pa.string()),                        # equipment / asset tag for prefilter
    pa.field("equipment_type", pa.string()),                      # 'bearing'|'fan'|'pump'|…
    pa.field("criticality", pa.string()),                         # 'critical'|'high'|'medium'|'low'
    pa.field("revision", pa.string()),                            # document revision tag
    pa.field("embedding_model", pa.string()),                     # provenance
    pa.field("char_count", pa.int32()),
    pa.field("ingested_at", pa.timestamp("us", tz="UTC")),
    pa.field("vector", pa.list_(pa.float32(), EMBEDDING_DIM)),    # dense embedding
])

TABLE_NAME = "chunks"


def _get_lancedb_path() -> Path:
    """Resolve the LanceDB directory path relative to cwd if not absolute."""
    p = Path(settings.lancedb_path)
    if not p.is_absolute():
        p = Path.cwd() / p
    return p


def get_store(db_path: Optional[Path] = None) -> "lancedb.LanceDBConnection":  # type: ignore[name-defined]
    """
    Return (and cache) the LanceDB connection.

    Creates the ``chunks`` table with ``CHUNKS_SCHEMA`` if it does not yet exist.
    Builds the FTS index on ``text`` if missing — this is idempotent.

    Parameters
    ----------
    db_path:
        Override the LanceDB directory (default: settings.lancedb_path).

    Returns
    -------
    lancedb.LanceDBConnection
        The open database handle.
    """
    try:
        import lancedb  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "lancedb is required for the RAG store. "
            "Run: pip install 'lancedb>=0.20.0'"
        ) from exc

    resolved = db_path or _get_lancedb_path()
    resolved.mkdir(parents=True, exist_ok=True)
    cache_key = str(resolved.resolve())

    if cache_key in _db_cache:
        logger.debug("LanceDB cache hit for %s", cache_key)
        return _db_cache[cache_key]

    db = lancedb.connect(str(resolved))
    logger.debug("LanceDB connected at %s", resolved)

    _ensure_table(db)
    _db_cache[cache_key] = db
    return db


def _ensure_table(db: "lancedb.LanceDBConnection") -> None:  # type: ignore[name-defined]
    """Create the chunks table and FTS index if they don't exist."""
    try:
        import lancedb  # type: ignore[import]
    except ImportError:
        raise

    existing = db.table_names()

    if TABLE_NAME not in existing:
        logger.info("Creating LanceDB table '%s'", TABLE_NAME)
        # Create empty table from schema — no data yet
        table = db.create_table(
            TABLE_NAME,
            schema=CHUNKS_SCHEMA,
            mode="create",
        )
        # Build FTS index immediately on the (empty) table
        # LanceDB requires data before FTS index creation, so we skip here
        # and build lazily in ensure_fts_index() after first ingest.
        logger.info("Table '%s' created. FTS index will be built after first ingest.", TABLE_NAME)
    else:
        logger.debug("Table '%s' already exists.", TABLE_NAME)


def ensure_fts_index(db: "lancedb.LanceDBConnection") -> None:  # type: ignore[name-defined]
    """
    Idempotently build (or replace) the FTS index on the ``text`` column.

    Must be called after data has been added — LanceDB requires rows to
    exist before building the Tantivy BM25 index.

    Safe to call multiple times; replaces the index if already present.
    """
    if TABLE_NAME not in db.table_names():
        logger.warning("Table '%s' does not exist — skipping FTS index build.", TABLE_NAME)
        return

    table = db.open_table(TABLE_NAME)
    row_count = table.count_rows()
    if row_count == 0:
        logger.warning("Table '%s' is empty — skipping FTS index build.", TABLE_NAME)
        return

    try:
        table.create_fts_index("text", replace=True)
        logger.info("FTS index built on '%s'.text (%d rows)", TABLE_NAME, row_count)
    except Exception as exc:
        logger.warning("FTS index build failed (hybrid search will fall back to dense): %s", exc)


def get_table(db: Optional["lancedb.LanceDBConnection"] = None):  # type: ignore[name-defined]
    """
    Convenience: return the open ``chunks`` LanceTable.

    Parameters
    ----------
    db:
        If provided, use this connection; otherwise open a new one.
    """
    db = db or get_store()
    return db.open_table(TABLE_NAME)
