"""
Overall Score computation — §2.3 of 03_relevance_and_ranking_engine.md

Formula:
  Time-series: R×0.30 + Q×0.35 + D×0.20 + F×0.10 + P×0.05
  Tabular:     R×0.30 + Q×0.45 + F×0.15 + P×0.10

Hard constraint: relevance_score < threshold → Overall=0.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

_CONFIG_PATH = Path(__file__).parent.parent.parent / "data" / "config" / "relevance_config.json"
_DEFAULT_THRESHOLD = 30.0


def _get_threshold() -> float:
    try:
        if _CONFIG_PATH.is_file():
            with open(_CONFIG_PATH) as f:
                return float(json.load(f).get("relevance_gate_threshold", _DEFAULT_THRESHOLD))
    except Exception:
        pass
    return _DEFAULT_THRESHOLD


def compute_overall_score(
    relevance_score: float,
    quality_score: float,
    domain_pdm_score: Optional[float],
    feature_richness: float,
    ps_alignment: float,
    dataset_type: str,
) -> float:
    """
    Returns overall_score in [0, 100].
    Returns 0.0 if relevance gate failed.
    """
    threshold = _get_threshold()
    if relevance_score < threshold:
        return 0.0

    if dataset_type == "time_series" and domain_pdm_score is not None:
        raw = (
            relevance_score * 0.30
            + quality_score * 0.35
            + domain_pdm_score * 0.20
            + feature_richness * 0.10
            + ps_alignment * 0.05
        )
    else:
        # Tabular: redistribute domain_pdm weight to quality + feature_richness + ps_alignment
        raw = (
            relevance_score * 0.30
            + quality_score * 0.45
            + feature_richness * 0.15
            + ps_alignment * 0.10
        )

    return round(min(max(raw, 0.0), 100.0), 2)
