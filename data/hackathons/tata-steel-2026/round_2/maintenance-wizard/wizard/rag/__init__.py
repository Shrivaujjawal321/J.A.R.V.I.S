"""
wizard.rag
==========
RAG (Retrieval-Augmented Generation) layer for the Maintenance Wizard.

Public surface — import these in other modules:

    from wizard.rag import retrieve, ingest_text, ingest_directory, RAG_TOOLS
    from wizard.rag import run_faithfulness_gate, apply_faithfulness_scores
    from wizard.rag import format_context_block, chunks_to_cited_sources
    from wizard.rag import RetrievedChunk, ContextResult, FaithfulnessResult

Architecture:
  - store.py      — LanceDB connection + schema + FTS index management
  - embedder.py   — bge-small-en-v1.5 (ONNX) singleton embedder
  - ingestion.py  — PDF/MD → chunk → embed → LanceDB
  - retriever.py  — hybrid search + HyDE + FlashRank rerank → RetrievedChunk list
  - faithfulness.py — NLI entailment gate (cross-encoder/nli-deberta-v3-small)
  - tools.py      — LangGraph ToolNode-ready wrappers (retrieve_context etc.)
"""

from wizard.rag.retriever import (
    retrieve,
    format_context_block,
    chunks_to_cited_sources,
    RetrievedChunk,
)
from wizard.rag.ingestion import (
    ingest_directory,
    ingest_file,
    ingest_text,
)
from wizard.rag.faithfulness import (
    run_faithfulness_gate,
    apply_faithfulness_scores,
    FaithfulnessResult,
    ClaimScore,
)
from wizard.rag.tools import (
    retrieve_context,
    search_manuals,
    search_incident_log,
    ContextResult,
    ContextChunk,
    RAG_TOOLS,
)
from wizard.rag.store import (
    get_store,
    get_table,
    ensure_fts_index,
)

__all__ = [
    # Retrieval
    "retrieve",
    "format_context_block",
    "chunks_to_cited_sources",
    "RetrievedChunk",
    # Ingestion
    "ingest_directory",
    "ingest_file",
    "ingest_text",
    # Faithfulness
    "run_faithfulness_gate",
    "apply_faithfulness_scores",
    "FaithfulnessResult",
    "ClaimScore",
    # LangGraph tools
    "retrieve_context",
    "search_manuals",
    "search_incident_log",
    "ContextResult",
    "ContextChunk",
    "RAG_TOOLS",
    # Store
    "get_store",
    "get_table",
    "ensure_fts_index",
]
