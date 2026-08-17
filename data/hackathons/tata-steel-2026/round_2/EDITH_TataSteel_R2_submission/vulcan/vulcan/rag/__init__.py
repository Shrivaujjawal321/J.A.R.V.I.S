"""VULCAN local RAG — bge-small embeddings + ChromaDB + FlashRank rerank + NLI gate.

All keyless, CPU-only. Ingests the flagship knowledge corpus; retrieval returns
chunks carrying their source filename for inline citations (FR2 + FR4).
"""

from .embedder import embed_single, embed_texts, EMBED_DIM, EMBED_MODEL
from .store import ingest, build_corpus, collection_count, get_collection, COLLECTION
from .retriever import retrieve, format_context, sources, RetrievedChunk
from .faithfulness import run_gate, FaithfulnessResult

__all__ = [
    "embed_single", "embed_texts", "EMBED_DIM", "EMBED_MODEL",
    "ingest", "build_corpus", "collection_count", "get_collection", "COLLECTION",
    "retrieve", "format_context", "sources", "RetrievedChunk",
    "run_gate", "FaithfulnessResult",
]
