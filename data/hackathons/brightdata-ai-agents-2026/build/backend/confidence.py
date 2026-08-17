"""
Weighted confidence rollup for AltBrief.

Two functions coexist in this module:

1. compute_overall_confidence() — original simple rollup (kept for backward
   compat; used by the basic orchestrator path).

2. rollup_confidence() — full research/19 formula used by synthesizer.py:
     base_weighted_score * direction_agreement_bonus * coverage_cap
     - contradiction_penalty
   Returns (confidence: float, data_quality_flag: str).

Source quality weights reflect peer-reviewed alpha strength:
- SEC Form 4 insider buys: Cohen-Malloy-Pomorski JoF 2012 (82bps/mo alpha)
- Glassdoor rating Δ: Green et al JFE 2019 (84bps/mo alpha)
- Satellite: Berkeley Haas study (4-5% earnings window returns)
- Reddit: Bradley 2024 / Alpha Architect 2024 (zero measurable alpha post-GME)
"""
from __future__ import annotations

from .schemas import Signal

# ─────────────────────────── Source Weights ─────────────────────────────────

# Higher weight = more peer-reviewed / structural alpha
QUALITY_WEIGHTS: dict[str, float] = {
    "sec": 1.00,         # SEC EDGAR filings + Form 4 insider trades
    "earnings": 0.90,    # Earnings transcripts
    "yahoo": 0.80,       # Fundamentals
    "glassdoor": 0.75,   # Peer-reviewed JFE 2019
    "linkedin": 0.70,    # Hiring trajectory
    "satellite": 0.70,   # Peer-reviewed Berkeley study
    "news": 0.65,        # Reuters/SERP
    "gdelt": 0.55,       # News volume tone
    "github": 0.50,      # Repo activity
    "reddit": 0.40,      # Decayed alpha post-2021
    "twitter": 0.35,
    "trends": 0.30,      # Nowcast only
}

# Penalty per contradiction severity (research 19 §4 Step 4)
SEVERITY_PENALTIES: dict[str, float] = {
    "high": 0.15,
    "medium": 0.08,
    "low": 0.03,
}

N_TOTAL_SOURCES = 8


# ─────────────────────── Original Simple Rollup ─────────────────────────────

def compute_overall_confidence(
    signals: list[Signal], sources_ok: int, total_sources: int
) -> float:
    """
    Simple rollup — original implementation kept for backward compat.

    base = weighted avg of per-signal confidence
    penalty = coverage multiplier (1.0 / 0.75 / 0.50)
    floor = 0.10 if no signals
    cap = 0.97
    """
    if not signals or total_sources == 0:
        return 0.10

    weighted_sum = sum(
        s.confidence * QUALITY_WEIGHTS.get(s.source, 0.5) for s in signals
    )
    weight_total = sum(QUALITY_WEIGHTS.get(s.source, 0.5) for s in signals)
    base = weighted_sum / weight_total if weight_total > 0 else 0.30

    coverage = sources_ok / total_sources
    if coverage >= 0.85:
        penalty = 1.00
    elif coverage >= 0.60:
        penalty = 0.85
    else:
        penalty = 0.65

    return round(min(base * penalty, 0.97), 3)


# ─────────────────────── Full Research-19 Rollup ────────────────────────────

def rollup_confidence(
    signals: list[Signal],
    contradictions: list,  # list[Contradiction] — imported lazily to avoid circular
) -> tuple[float, str]:
    """
    Compute overall investment brief confidence using the full formula from
    research/19_contradiction_confidence_algo.md §4.

    Formula:
        score = base_weighted_score * direction_agreement_bonus
        score = min(score, coverage_cap)
        score = score - contradiction_penalty
        final = clamp(score, 0.0, 1.0)

    Step 1 — Base Weighted Score:
        base = Σ(signal.confidence * SOURCE_WEIGHTS[source]) / Σ(SOURCE_WEIGHTS[source])
        Normalize to [0, 1]. Unknown sources get weight 0.50.

    Step 2 — Direction Agreement Bonus:
        majority_count = max(n_bullish, n_bearish)
        agreement_ratio = majority_count / n_total
        direction_bonus = 0.85 + (0.30 * agreement_ratio)
        Range: [0.85 (50/50 split = -15%) .. 1.15 (100% agreement = +15%)]

    Step 3 — Coverage Cap:
        coverage_ratio = n_available / 8
        coverage_cap = 0.30 + (0.70 * coverage_ratio)
        At 3/8 sources: cap = 0.5625 (cap bites hard on partial coverage)
        At 8/8 sources: cap = 1.00

    Step 4 — Contradiction Penalty:
        Penalty per severity: high=0.15, medium=0.08, low=0.03
        Total capped at 0.35 (score never goes negative from contradictions alone)

    Returns:
        (confidence: float in [0.0, 1.0], data_quality_flag: "full"|"partial"|"minimal")

    Worked examples (from research 19 §4):
        6 sources, 0 contradictions, 0.78 avg: → 0.80, "full"
        3 sources, 0 contradictions, 0.72 avg: → 0.56, "minimal"
        6 sources, 1 high + 1 medium contradiction: → 0.45, "partial"
    """
    if not signals:
        return 0.0, "minimal"

    # Step 1: Base weighted score
    weight_sum = 0.0
    weighted_conf_sum = 0.0
    for sig in signals:
        w = QUALITY_WEIGHTS.get(sig.source, 0.50)
        weighted_conf_sum += sig.confidence * w
        weight_sum += w

    base_score = weighted_conf_sum / weight_sum if weight_sum > 0 else 0.0

    # Step 2: Direction agreement bonus
    n_bullish = sum(1 for s in signals if s.direction == "bullish")
    n_bearish = sum(1 for s in signals if s.direction == "bearish")
    majority = max(n_bullish, n_bearish)
    agreement_ratio = majority / len(signals)
    direction_bonus = 0.85 + (0.30 * agreement_ratio)
    score = base_score * direction_bonus

    # Step 3: Coverage penalty cap
    coverage_ratio = len(signals) / N_TOTAL_SOURCES
    coverage_cap = 0.30 + (0.70 * coverage_ratio)
    score = min(score, coverage_cap)

    # Step 4: Contradiction penalty (severity-weighted)
    total_penalty = 0.0
    for c in contradictions:
        # Support both Contradiction objects and plain dicts
        severity = c.severity if hasattr(c, "severity") else c.get("severity", "low")
        total_penalty += SEVERITY_PENALTIES.get(severity, 0.0)
    total_penalty = min(total_penalty, 0.35)  # cap at 35pp
    score = score - total_penalty

    # Clamp to [0.0, 1.0]
    final_score = max(0.0, min(1.0, score))

    # Data quality flag
    n = len(signals)
    if n >= 6:
        quality = "full"
    elif n >= 4:
        quality = "partial"
    else:
        quality = "minimal"

    return round(final_score, 3), quality


# ─────────────────────────── UI Helper ──────────────────────────────────────

def confidence_band(confidence: float) -> str:
    """Human label for UI display."""
    if confidence >= 0.80:
        return "High Conviction"
    if confidence >= 0.60:
        return "Moderate Signal"
    return "Weak Signal — verify manually"
