"""Composite scoring: weighted mean + penalty caps."""

from __future__ import annotations
from typing import Dict, List, Tuple

# ------------------------------------------------------------------
# Weight configurations
# ------------------------------------------------------------------
TABULAR_WEIGHTS: Dict[str, float] = {
    "completeness":        0.15,
    "class_balance":       0.12,
    "label_quality":       0.15,
    "duplicates":          0.08,
    "outliers":            0.08,
    "schema_validity":     0.08,
    "leakage":             0.12,
    "temporal_coverage":   0.00,  # ignored for tabular
    "feature_redundancy":  0.10,
    "distribution_sanity": 0.12,
}

TIME_SERIES_WEIGHTS: Dict[str, float] = {
    "completeness":        0.12,
    "class_balance":       0.05,   # reduced — domain_pdm.pdm_imbalance overrides for PdM context
    "label_quality":       0.08,   # reduced — domain_pdm.pdm_label_quality adds PdM-specific checks
    "duplicates":          0.06,
    "outliers":            0.05,   # reduced — sensor_health in domain_pdm covers physics-aware checks
    "schema_validity":     0.07,
    "leakage":             0.10,
    "temporal_coverage":   0.18,   # reduced slightly — domain_pdm.temporal_degradation adds arc checks
    "feature_redundancy":  0.05,   # reduced
    "distribution_sanity": 0.05,   # reduced — domain_pdm.sensor_health covers physical range sanity
    "domain_pdm":          0.19,   # NEW — highest single weight for sensor time-series
    # Total = 1.00
}

GRADE_THRESHOLDS: List[Tuple[float, str]] = [
    (85.0, "Excellent"),
    (70.0, "Good"),
    (55.0, "Fair"),
    (35.0, "Needs Work"),
    (0.0,  "Poor"),
]


def get_weights(dataset_type: str) -> Dict[str, float]:
    if dataset_type == "time_series":
        return TIME_SERIES_WEIGHTS
    return TABULAR_WEIGHTS


def score_to_grade(score: float) -> str:
    for threshold, grade in GRADE_THRESHOLDS:
        if score >= threshold:
            return grade
    return "Poor"


def compute_composite(
    sub_scores: Dict[str, Dict],
    dataset_type: str,
) -> Tuple[float, str, List[str]]:
    """
    Returns (composite_score, grade, cap_reasons).
    cap_reasons is a list of human-readable strings explaining any active caps.
    """
    weights = get_weights(dataset_type)
    cap_reasons: List[str] = []

    # Find minimum score across all dimensions
    scores_by_dim = {k: v["score"] for k, v in sub_scores.items()}
    min_score = min(scores_by_dim.values()) if scores_by_dim else 0.0

    # --- Weighted mean ---
    total_weight = 0.0
    weighted_sum = 0.0
    for dim, weight in weights.items():
        if dim not in sub_scores or weight == 0:
            continue
        s = sub_scores[dim]["score"]
        weighted_sum += s * weight
        total_weight += weight

    raw_composite = weighted_sum / total_weight if total_weight > 0 else 0.0

    # --- Domain PdM cap: if domain_pdm is critical → composite capped at 50 ---
    domain_r = sub_scores.get("domain_pdm", {})
    domain_pdm_score = domain_r.get("score", None)
    if domain_pdm_score is not None and domain_pdm_score < 30:
        if raw_composite > 50.0:
            raw_composite = 50.0
            cap_reasons.append(
                "Score capped at 50 due to critical domain quality failure "
                "(missing required sensors, sub-Nyquist sampling, or zero failure events). "
                "This dataset cannot support predictive maintenance modeling in its current state."
            )

    # --- Leakage cap (hard cap at 45 if any leakage detected) ---
    leakage_raw = sub_scores.get("leakage", {})
    leak_detected = leakage_raw.get("raw", {}).get("leak_detected", False)
    if leak_detected:
        if raw_composite > 45.0:
            raw_composite = 45.0
            cap_reasons.append(
                "Score capped at 45 due to detected data leakage. "
                "Leaky features will cause artificially inflated model performance."
            )

    # --- Minimum sub-score caps ---
    if min_score < 10:
        cap = 35.0
        if raw_composite > cap:
            raw_composite = cap
            dim_at_fault = min(scores_by_dim, key=scores_by_dim.get)
            cap_reasons.append(
                f"Score capped at 35 because dimension '{dim_at_fault}' scored {min_score:.0f}/100 "
                f"(below critical threshold of 10). This dimension is a hard blocker."
            )
    elif min_score < 20:
        cap = 55.0
        if raw_composite > cap:
            raw_composite = cap
            dim_at_fault = min(scores_by_dim, key=scores_by_dim.get)
            cap_reasons.append(
                f"Score capped at 55 because dimension '{dim_at_fault}' scored {min_score:.0f}/100 "
                f"(below severe threshold of 20). Requires urgent attention."
            )
    elif min_score < 40:
        cap = 75.0
        if raw_composite > cap:
            raw_composite = cap
            dim_at_fault = min(scores_by_dim, key=scores_by_dim.get)
            cap_reasons.append(
                f"Score capped at 75 because dimension '{dim_at_fault}' scored {min_score:.0f}/100 "
                f"(below moderate threshold of 40). Reduces overall reliability."
            )

    final_score = round(max(0.0, min(100.0, raw_composite)), 2)
    grade = score_to_grade(final_score)

    return final_score, grade, cap_reasons
