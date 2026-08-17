"""
Embedding similarity engine — §1.3 of 03_relevance_and_ranking_engine.md

Model: BAAI/bge-small-en-v1.5 (lazy-load, cached in-process).
Graceful KB-only fallback if sentence-transformers unavailable or OOM.
"""
from __future__ import annotations

import logging
import os
from typing import List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level state
# ---------------------------------------------------------------------------
EMBEDDINGS_AVAILABLE: bool = False
_model = None  # SentenceTransformer instance (lazy-loaded once)
_query_embeddings: Optional[np.ndarray] = None  # [N_queries, 384] cached

# PS anchor text — describes the Tata Steel Hackathon scope
PS_ANCHOR_TEXT = """
Tata Steel Hackathon — Maintenance Wizard for Industrial Equipment.
Predictive maintenance, anomaly detection, root-cause analysis, failure prediction.
Steel manufacturing equipment: rolling mill, blast furnace, caster, converter, ladle,
furnace, crane, conveyor, compressor, pump, motor, gearbox, bearing, fan, hydraulic.
Sensor data: vibration, temperature, acoustic emission, current, speed, pressure,
oil quality, position, flow, force, power, level.
Maintenance records, work orders, equipment logs, SOPs, inspection history.
Run-to-failure trajectories, remaining useful life (RUL), fault labels, failure modes.
"""

# One concept text per major equipment class — embedded once at startup
KB_CONCEPT_TEXTS = [
    "Rolling mill predictive maintenance: vibration, temperature, current, roll force sensors required.",
    "Blast furnace maintenance: temperature, pressure, flow, vibration monitoring.",
    "Bearing predictive maintenance: vibration rms, temperature, acoustic emission.",
    "Gearbox fault detection: vibration velocity, oil quality, temperature, acoustic.",
    "Motor condition monitoring: current, vibration, temperature, speed sensors.",
    "Pump predictive maintenance: vibration, pressure, flow, temperature, acoustic.",
    "Compressor health: vibration, pressure, temperature, current monitoring.",
    "Crane structural monitoring: vibration, load, position, acoustic emission.",
    "Conveyor belt monitoring: vibration, speed, tension, temperature.",
    "Hydraulic system monitoring: pressure, flow, oil quality, temperature.",
    "Ladle handling equipment: temperature, vibration, load sensors.",
    "Caster monitoring: temperature, speed, vibration, cooling flow.",
    "Furnace temperature control: temperature, pressure, flow, fuel sensors.",
    "Fan vibration monitoring: vibration rms, temperature, speed, current.",
    "Industrial equipment failure prediction: sensor time-series, fault labels, RUL.",
    "Steel plant predictive maintenance dataset: multiple sensors, failure events.",
    "Industrial anomaly detection: time-stamped sensor readings, equipment health.",
]

QUERY_TEXTS = [PS_ANCHOR_TEXT] + KB_CONCEPT_TEXTS
_EMBEDDING_MODEL_NAME = os.environ.get("EDITH_EMBED_MODEL", "BAAI/bge-small-en-v1.5")


def load_embeddings_model() -> bool:
    """
    Lazy-load the BGE-small embedding model. Sets EMBEDDINGS_AVAILABLE flag.
    Safe to call multiple times — loads once.
    """
    global EMBEDDINGS_AVAILABLE, _model, _query_embeddings

    if EMBEDDINGS_AVAILABLE and _model is not None and _query_embeddings is not None:
        return True  # already loaded

    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
        _model = SentenceTransformer(_EMBEDDING_MODEL_NAME)
        EMBEDDINGS_AVAILABLE = True
        logger.info(f"[EDITH] Loaded embedding model: {_EMBEDDING_MODEL_NAME}")
    except Exception as exc:
        EMBEDDINGS_AVAILABLE = False
        logger.warning(
            f"[EDITH] sentence-transformers unavailable ({exc}); "
            "relevance gate will run in KB-only mode."
        )
        return False

    # Pre-compute query embeddings immediately
    precompute_query_embeddings()
    return True


def precompute_query_embeddings() -> None:
    """Pre-encode query pool (PS anchor + KB concept texts). Called once at startup."""
    global _query_embeddings, EMBEDDINGS_AVAILABLE

    if not EMBEDDINGS_AVAILABLE or _model is None:
        return
    try:
        _query_embeddings = _model.encode(
            QUERY_TEXTS,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        logger.info(
            f"[EDITH] Query embeddings pre-computed: {_query_embeddings.shape}"
        )
    except Exception as exc:
        EMBEDDINGS_AVAILABLE = False
        logger.warning(
            f"[EDITH] Failed to pre-compute query embeddings ({exc}); "
            "falling back to KB-only mode."
        )


def _infer_unit_hint(col_name: str, series: pd.Series) -> str:
    """Heuristically infer physical unit from column name + value range."""
    col_l = col_name.lower()
    try:
        median = float(series.median())
    except Exception:
        return "unknown"
    if any(k in col_l for k in ["temp", "degc", "celsius"]):
        return "degC" if -50 < median < 500 else "unknown"
    if any(k in col_l for k in ["vib", "rms", "mm_s"]):
        return "mm/s" if 0 < median < 100 else ("g" if median < 50 else "unknown")
    if any(k in col_l for k in ["current", "_a", "amps", "amp"]):
        return "A" if 0 < median < 2000 else "unknown"
    if any(k in col_l for k in ["rpm", "speed"]):
        return "RPM" if 0 < median < 50000 else "unknown"
    if any(k in col_l for k in ["pressure", "bar", "psi"]):
        return "bar" if 0 < median < 500 else ("psi" if 0 < median < 7000 else "unknown")
    return "unknown"


def build_document_text(
    df: pd.DataFrame,
    filename: str = "",
    user_name: str = "",
    user_description: str = "",
    user_tags: Optional[List[str]] = None,
) -> str:
    """
    Construct a single text string representing the dataset identity for embedding.
    """
    user_tags = user_tags or []
    parts: List[str] = []

    # 1. User-provided metadata
    if user_name:
        parts.append(f"Dataset name: {user_name}")
    if user_description:
        parts.append(f"Description: {user_description}")
    if user_tags:
        parts.append(f"Tags: {', '.join(user_tags)}")
    if filename:
        parts.append(f"Filename: {filename}")

    # 2. Column names
    parts.append(f"Columns: {', '.join(str(c) for c in df.columns.tolist())}")

    # 3. Sample values for object/categorical columns
    try:
        for col in df.select_dtypes(include=["object", "category"]).columns[:10]:
            uniq = df[col].dropna().astype(str).unique()[:5].tolist()
            if uniq:
                parts.append(f"{col} values: {', '.join(uniq)}")
    except Exception:
        pass

    # 4. Numeric column stats (range hints that corroborate sensor types)
    try:
        for col in df.select_dtypes(include=[np.number]).columns[:12]:
            s = df[col].dropna()
            if len(s) >= 10:
                try:
                    unit = _infer_unit_hint(col, s)
                    parts.append(
                        f"{col}: min={s.min():.2g} max={s.max():.2g} "
                        f"mean={s.mean():.2g} unit_hint={unit}"
                    )
                except Exception:
                    parts.append(f"{col}: values present")
    except Exception:
        pass

    return " | ".join(parts)


def compute_embed_sim(document_text: str) -> Optional[float]:
    """
    Returns max cosine similarity of the document embedding against the query pool.
    Returns None if embeddings are unavailable.
    """
    global _model, _query_embeddings, EMBEDDINGS_AVAILABLE

    # Lazy load on first call (startup may not have been hooked)
    if not EMBEDDINGS_AVAILABLE or _model is None:
        load_embeddings_model()
    if not EMBEDDINGS_AVAILABLE or _model is None or _query_embeddings is None:
        return None

    try:
        doc_emb = _model.encode(
            [document_text],
            normalize_embeddings=True,
            show_progress_bar=False,
        )  # [1, 384]
        # cosine sim = dot product (vectors are L2-normalized)
        sims = (_query_embeddings @ doc_emb.T).squeeze()  # [N_queries,]
        result = float(np.max(sims))
        return max(0.0, min(1.0, result))
    except Exception as exc:
        logger.warning(f"[EDITH] embed_sim computation failed: {exc}")
        return None
