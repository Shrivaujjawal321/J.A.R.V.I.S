"""
wizard.rag.embedder
===================
Thin wrapper around sentence-transformers for the RAG embedding pipeline.

Model: BAAI/bge-small-en-v1.5 (384-dim, MTEB NDCG@10 avg 0.517)
Backend: ONNX for 1.4–3× CPU speedup; falls back to torch if ONNX unavailable.

Always calls ``normalize_embeddings=True`` — required by BGE model family.

Singleton pattern: model is loaded ONCE at module level on first call.
"""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np

from wizard.core.config import settings

logger = logging.getLogger(__name__)

_model = None  # module-level singleton


def _load_model() -> "SentenceTransformer":  # type: ignore[name-defined]
    """
    Load and cache the embedding model.
    Tries ONNX backend first; falls back to torch backend on ImportError.
    """
    global _model
    if _model is not None:
        return _model

    try:
        from sentence_transformers import SentenceTransformer  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "sentence-transformers is required. Run: pip install sentence-transformers"
        ) from exc

    model_name = settings.embedding_model  # BAAI/bge-small-en-v1.5

    # Try ONNX backend for CPU speedup
    try:
        model = SentenceTransformer(model_name, backend="onnx")
        logger.info("Embedding model loaded with ONNX backend: %s", model_name)
    except Exception as onnx_err:
        logger.warning(
            "ONNX backend unavailable (%s) — falling back to torch backend.", onnx_err
        )
        model = SentenceTransformer(model_name)
        logger.info("Embedding model loaded with torch backend: %s", model_name)

    # Pre-warm: one dummy encode so first real call is not cold
    _ = model.encode(["warm-up"], normalize_embeddings=True)
    logger.debug("Embedding model pre-warmed.")

    _model = model
    return _model


def embed_texts(texts: list[str], batch_size: int = 64) -> np.ndarray:
    """
    Embed a list of texts.

    Parameters
    ----------
    texts:
        List of strings to embed.
    batch_size:
        Encode batch size (default 64 — safe for CPU RAM).

    Returns
    -------
    np.ndarray of shape (len(texts), embedding_dim), float32, L2-normalized.
    """
    model = _load_model()
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,  # REQUIRED for BGE cosine similarity
        show_progress_bar=False,
    )
    return embeddings.astype(np.float32)


def embed_single(text: str) -> list[float]:
    """
    Embed a single string and return as a plain Python list[float].
    Convenience wrapper for LanceDB insert / query paths.
    """
    vec = embed_texts([text])
    return vec[0].tolist()


def get_embedding_dim() -> int:
    """Return the model's output dimension (384 for bge-small-en-v1.5)."""
    return settings.embedding_dim
