"""VULCAN RAG embedder — bge-small-en-v1.5 via sentence-transformers (CPU, keyless).

Ported from the proven wizard build. 384-dim, L2-normalized (required by BGE).
ONNX backend tried first for CPU speedup; falls back to torch transparently.
Module-level singleton so the model loads once.
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)

EMBED_MODEL = "BAAI/bge-small-en-v1.5"
EMBED_DIM = 384

_model = None


def _load_model():
    global _model
    if _model is not None:
        return _model
    from sentence_transformers import SentenceTransformer  # type: ignore[import]

    try:
        model = SentenceTransformer(EMBED_MODEL, backend="onnx")
        logger.info("Embedder loaded (ONNX): %s", EMBED_MODEL)
    except Exception as exc:  # noqa: BLE001
        logger.warning("ONNX backend unavailable (%s) — using torch.", exc)
        model = SentenceTransformer(EMBED_MODEL)
        logger.info("Embedder loaded (torch): %s", EMBED_MODEL)
    _ = model.encode(["warm-up"], normalize_embeddings=True)
    _model = model
    return _model


def embed_texts(texts: list[str], batch_size: int = 32) -> np.ndarray:
    """Embed a list of texts -> (N, 384) float32, L2-normalized."""
    model = _load_model()
    vecs = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,   # REQUIRED for BGE cosine
        show_progress_bar=False,
    )
    return np.asarray(vecs, dtype=np.float32)


def embed_single(text: str) -> list[float]:
    """Embed one string -> list[float] (for chromadb query/insert)."""
    return embed_texts([text])[0].tolist()
