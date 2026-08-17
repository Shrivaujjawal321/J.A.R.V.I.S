"""
Relevance gate — §1.4–§1.7 of 03_relevance_and_ranking_engine.md

Combines kb_match_score + embed_sim → relevance_score (0–100).
Reads threshold from data/config/relevance_config.json (default 30).
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

from .kb_match import compute_kb_match_score
from .embeddings import build_document_text, compute_embed_sim, load_embeddings_model

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config — hot-reloadable from JSON file
# ---------------------------------------------------------------------------
_CONFIG_PATH = Path(__file__).parent.parent.parent / "data" / "config" / "relevance_config.json"
_DEFAULT_THRESHOLD = 30.0


def _load_config() -> dict:
    """Load relevance config. Returns defaults on any failure."""
    try:
        if _CONFIG_PATH.is_file():
            with open(_CONFIG_PATH) as f:
                return json.load(f)
    except Exception:
        pass
    return {"relevance_gate_threshold": _DEFAULT_THRESHOLD}


def get_threshold() -> float:
    cfg = _load_config()
    return float(cfg.get("relevance_gate_threshold", _DEFAULT_THRESHOLD))


# ---------------------------------------------------------------------------
# Score combination
# ---------------------------------------------------------------------------

def compute_relevance_score(
    kb_match_score: float,
    embed_sim: Optional[float],
    raw_kb: Optional[dict] = None,
) -> float:
    """
    Returns relevance_score in [0, 100].

    Hybrid (both signals present): 0.65 × KB + 0.35 × embed, scaled ×100
    KB-only fallback: kb_match_score × 85.0 (compress top end; no embedding corroboration)

    Anti-gaming: if corroboration signals indicate renamed junk (mean_corr low,
    zero-corr sensors present), the embedding score is discounted — the embeddings
    can see column NAMES which are easy to fake, but not VALUE distributions.
    """
    cfg = _load_config()
    raw_kb = raw_kb or {}

    # Detect gaming signal from corroboration evidence
    corr_per_type = raw_kb.get("corroboration_per_type", {})
    n_zero = sum(1 for v in corr_per_type.values() if v == 0.0)
    n_total = len(corr_per_type)
    mean_corr = raw_kb.get("mean_corroboration", 1.0)

    # Gaming multiplier: if >= 30% of checked sensors are physically impossible,
    # cap the embed contribution (embed can be fooled by column names; KB cannot).
    gaming_penalty = 1.0
    if n_total > 0 and n_zero / n_total >= 0.3:
        # Penalize embed_sim contribution proportional to how many sensors are impossible
        gaming_penalty = max(0.0, 1.0 - (n_zero / n_total) * 0.8)

    if embed_sim is None:
        scale = float(cfg.get("weights_kb_only_scale", 85.0))
        raw = kb_match_score * scale
    else:
        w_kb = float(cfg.get("weights_hybrid", {}).get("kb_match", 0.65))
        w_em = float(cfg.get("weights_hybrid", {}).get("embed_sim", 0.35))
        raw = (w_kb * kb_match_score + w_em * embed_sim * gaming_penalty) * 100.0

    return round(min(max(raw, 0.0), 100.0), 2)


# ---------------------------------------------------------------------------
# Gate decision
# ---------------------------------------------------------------------------

def gate_dataset(relevance_score: float) -> Tuple[bool, str]:
    """
    Returns (accepted: bool, gate_message: str).
    """
    threshold = get_threshold()
    if relevance_score < threshold:
        return False, (
            "Dataset is not relevant to the Tata Steel Hackathon. "
            f"Relevance score: {relevance_score:.0f}/100 "
            f"(minimum required: {threshold:.0f}). "
            "This platform scores datasets for steel-plant predictive maintenance. "
            "Expected data types: sensor time-series (vibration, temperature, current, "
            "pressure, speed), maintenance logs, or equipment fault records from "
            "industrial manufacturing environments. "
            "Non-industrial datasets (Iris, Titanic, sales, weather, etc.) cannot be ranked."
        )
    return True, f"Dataset accepted for scoring. Relevance score: {relevance_score:.0f}/100."


# ---------------------------------------------------------------------------
# Explainability trace
# ---------------------------------------------------------------------------

def build_relevance_trace(
    raw_kb: Dict,
    embed_sim: Optional[float],
    relevance_score: float,
    accepted: bool,
) -> List[str]:
    """Build human-readable reasoning trace for the relevance decision."""
    threshold = get_threshold()
    trace: List[str] = []

    trace.append(
        f"RELEVANCE GATE: score={relevance_score:.1f}/100 | "
        f"threshold={threshold} | "
        f"verdict={'ACCEPTED' if accepted else 'REJECTED'}"
    )

    # Sensor hits
    detected = raw_kb.get("detected_sensors", [])
    if detected:
        trace.append(
            f"  KB Tier A — sensor types matched: {detected} "
            f"({raw_kb.get('n_sensor_types', 0)} types)"
        )
        for stype, score in raw_kb.get("corroboration_per_type", {}).items():
            if score >= 0.8:
                verdict = "OK"
            elif score < 0.3:
                verdict = "SUSPECT (values outside physical range)"
            else:
                verdict = "MARGINAL"
            trace.append(f"    [{verdict}] {stype}: corroboration={score:.2f}")
    else:
        trace.append("  KB Tier A — no sensor-type keywords matched in column names")

    # Equipment hits
    eq_hits = raw_kb.get("equipment_hits", {})
    if eq_hits:
        trace.append(f"  KB Tier B — equipment classes matched: {list(eq_hits.keys())}")
    else:
        trace.append("  KB Tier B — no equipment class matched")

    # Maintenance vocab
    maint = raw_kb.get("maintenance_hits", {})
    if maint:
        trace.append(f"  KB Tier C — maintenance vocab groups: {list(maint.keys())}")
    else:
        trace.append("  KB Tier C — no maintenance vocabulary matched")

    # Coherence
    coh = raw_kb.get("coherence", 0.5)
    coherence_str = "OK" if coh > 0.4 else "LOW — may indicate renamed junk data"
    trace.append(f"  Cross-signal coherence: {coh:.2f} ({coherence_str})")

    # Structural
    ts = raw_kb.get("has_timestamp", False)
    n_num = raw_kb.get("n_numeric", 0)
    trace.append(f"  Structural: timestamp_present={ts}, numeric_cols={n_num}")

    # Embedding
    if embed_sim is not None:
        trace.append(f"  Embedding similarity (bge-small) vs PS anchor+KB: {embed_sim:.3f}")
    else:
        trace.append("  Embedding similarity: SKIPPED (sentence-transformers unavailable)")

    return trace


# ---------------------------------------------------------------------------
# One-shot convenience function (used by main.py pipeline)
# ---------------------------------------------------------------------------

def score_dataset(
    df: pd.DataFrame,
    filename: str = "",
    user_name: str = "",
    user_description: str = "",
    user_tags: Optional[List[str]] = None,
) -> Dict:
    """
    Run the full relevance scoring pipeline on a parsed DataFrame.

    Returns a dict with keys:
      relevance_score, accepted, gate_message, relevance_reasons,
      kb_match_score, embed_sim, raw_kb, trace
    """
    user_tags = user_tags or []

    # Ensure embeddings are loaded (lazy — first call loads, subsequent calls are cached)
    load_embeddings_model()

    # Step 1: KB-vocab match
    kb_match_score, raw_kb = compute_kb_match_score(
        df=df,
        filename=filename,
        user_name=user_name,
        user_description=user_description,
        user_tags=user_tags,
    )

    # Step 2: Embedding similarity (graceful None on failure)
    doc_text = build_document_text(
        df=df,
        filename=filename,
        user_name=user_name,
        user_description=user_description,
        user_tags=user_tags,
    )
    embed_sim = compute_embed_sim(doc_text)

    # Step 3: Combined score (pass raw_kb for anti-gaming adjustment)
    relevance_score = compute_relevance_score(kb_match_score, embed_sim, raw_kb=raw_kb)

    # Step 4: Gate decision
    accepted, gate_message = gate_dataset(relevance_score)

    # Step 5: Trace
    trace = build_relevance_trace(raw_kb, embed_sim, relevance_score, accepted)

    # Build concise reasons lists for API response
    reasons_for: List[str] = []
    reasons_against: List[str] = []

    if raw_kb.get("detected_sensors"):
        reasons_for.append(
            f"{raw_kb['n_sensor_types']} sensor types matched: "
            f"{', '.join(raw_kb['detected_sensors'][:5])}"
        )
    if raw_kb.get("equipment_hits"):
        reasons_for.append(
            f"Equipment class matched: {', '.join(list(raw_kb['equipment_hits'].keys())[:3])}"
        )
    if raw_kb.get("maintenance_hits"):
        reasons_for.append(
            f"Maintenance vocabulary groups: {', '.join(list(raw_kb['maintenance_hits'].keys()))}"
        )
    if raw_kb.get("has_timestamp") and raw_kb.get("n_numeric", 0) >= 5:
        reasons_for.append("Time-series structure with multiple numeric sensor columns")
    if embed_sim is not None and embed_sim >= 0.5:
        reasons_for.append(f"Semantic similarity to PS: {embed_sim:.2f}")

    # Negative signals
    if not raw_kb.get("detected_sensors"):
        reasons_against.append("No sensor-type keywords in column names")
    if not raw_kb.get("equipment_hits"):
        reasons_against.append("No industrial equipment class detected")
    if not raw_kb.get("has_timestamp"):
        reasons_against.append("No timestamp column (time-series signals missing)")
    if raw_kb.get("n_numeric", 0) < 3:
        reasons_against.append("Very few numeric columns (fewer than 3)")
    suspect_sensors = [
        s for s, c in raw_kb.get("corroboration_per_type", {}).items() if c < 0.3
    ]
    if suspect_sensors:
        reasons_against.append(
            f"Value ranges outside physical bounds for: {', '.join(suspect_sensors)} "
            "(possible renamed non-industrial data)"
        )

    return {
        "relevance_score": relevance_score,
        "accepted": accepted,
        "gate_message": gate_message,
        "relevance_reasons": reasons_for,
        "relevance_against": reasons_against,
        "kb_match_score": kb_match_score,
        "embed_sim": embed_sim,
        "raw_kb": raw_kb,
        "trace": trace,
    }
