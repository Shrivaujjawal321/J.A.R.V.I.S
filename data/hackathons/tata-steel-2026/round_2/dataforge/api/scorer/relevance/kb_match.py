"""
KB-Vocab Match engine — §1.2 of 03_relevance_and_ranking_engine.md

3-tier hierarchy:
  Tier A — sensor-type hits from SENSOR_VOCAB + physical-range corroboration
  Tier B — equipment-class hits from EQUIPMENT_COVERAGE_RULES + EQUIPMENT_ALIASES
  Tier C — maintenance/context vocabulary hits

Anti-gaming: _corroborate_column (physical value range check) + _cross_signal_coherence.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from statistics import mean
from typing import Dict, List, Optional, Tuple

# Import from the existing domain knowledge base (no duplication).
from scorer.dimensions.domain_knowledge import (
    SENSOR_VOCAB,
    PHYSICAL_RANGE_RULES,
    EQUIPMENT_ALIASES,
    EQUIPMENT_COVERAGE_RULES,
)

# ---------------------------------------------------------------------------
# Tier C — maintenance/context vocabulary
# ---------------------------------------------------------------------------
MAINTENANCE_VOCAB: Dict[str, List[str]] = {
    "fault_labels": [
        "failure", "fault", "anomaly", "alarm", "defect", "breakdown",
        "rul", "remaining_useful_life", "ttf", "time_to_failure", "mtbf",
    ],
    "maintenance_ops": [
        "maintenance", "repair", "overhaul", "replacement", "inspection",
        "work_order", "downtime", "mttr", "planned", "unplanned",
    ],
    "process_context": [
        "steel", "blast_furnace", "bof", "eaf", "caster", "rolling", "mill",
        "ladle", "converter", "coiler", "pickling", "annealing", "hot_strip",
        "cold_strip", "galvanizing", "slab", "billet", "rebar", "coil",
    ],
    "operating_context": [
        "asset_id", "equipment_id", "machine_id", "unit_id",
        "operating_mode", "load", "rpm", "speed", "cycle",
    ],
}


# ---------------------------------------------------------------------------
# Tier A helpers
# ---------------------------------------------------------------------------

def _sensor_vocab_hits(columns: List[str]) -> Dict[str, List[Tuple[str, str, str]]]:
    """Return {sensor_type: [(col, sensor_type, matched_keyword), ...]} for cols matching SENSOR_VOCAB."""
    hits: Dict[str, List[Tuple[str, str, str]]] = {}
    for sensor_type, keywords in SENSOR_VOCAB.items():
        matched_cols = []
        for col in columns:
            col_lower = str(col).lower().strip()
            for kw in keywords:
                if kw in col_lower:
                    matched_cols.append((col, sensor_type, kw))
                    break  # one match per col per sensor_type
        if matched_cols:
            hits[sensor_type] = matched_cols
    return hits


def _corroborate_column(col: str, sensor_type: str, series: pd.Series) -> float:
    """
    Returns a corroboration score 0.0–1.0.
    0.0 = name matched but values are physically impossible (likely renamed junk).
    0.5 = neutral (range rule absent or too few values).
    1.0 = values fall within the documented physical range.
    """
    if sensor_type not in PHYSICAL_RANGE_RULES:
        return 0.5  # no rule to check

    rule = PHYSICAL_RANGE_RULES[sensor_type]
    lo: float = rule.get("min", 0.0)
    hi: float = rule.get("max", 1e6)

    numeric = pd.to_numeric(series.dropna(), errors="coerce").dropna()
    if len(numeric) < 5:
        return 0.5  # too few values

    median = float(numeric.median())
    p05 = float(numeric.quantile(0.05))
    p95 = float(numeric.quantile(0.95))

    # Hard-impossible check: >5% of values outside 10x extended range
    # (strictly-positive sensors use 0 as hard lower bound)
    strict_lo = lo - abs(lo) * 0.5  # 50% below documented min
    strict_hi = hi * 10.0           # 10x documented max (fault spikes allowed)
    pct_impossible = float(((numeric < strict_lo) | (numeric > strict_hi)).mean())

    if pct_impossible > 0.05:
        return 0.0  # GAMING DETECTED — physically inconsistent

    # Soft check: median within [lo * 0.1, hi * 5]
    lo_soft = lo * 0.1 if lo > 0 else lo - abs(lo) * 0.1 - 1
    hi_soft = hi * 5.0
    if lo_soft <= median <= hi_soft:
        return 1.0

    return 0.5  # in range but unusual


def _corroborate_all(
    df: pd.DataFrame, hits: Dict[str, List[Tuple[str, str, str]]]
) -> Dict[str, float]:
    """Corroborate every sensor-type / column pair detected in Tier A."""
    scores: Dict[str, float] = {}
    for sensor_type, hit_cols in hits.items():
        col_scores = []
        for (col, stype, kw) in hit_cols:
            if col in df.columns:
                s = _corroborate_column(col, stype, df[col])
                col_scores.append(s)
        if col_scores:
            scores[sensor_type] = float(mean(col_scores))
    return scores


# ---------------------------------------------------------------------------
# Tier B helpers
# ---------------------------------------------------------------------------

def _equipment_class_hits(
    columns: List[str],
    filename: str,
    user_name: str,
    user_description: str,
    user_tags: List[str],
) -> Dict[str, int]:
    """Return {equip_class: match_score} for matched equipment classes."""
    col_blob = (
        " ".join(str(c).lower() for c in columns)
        + " " + str(filename).lower()
        + " " + str(user_name).lower()
        + " " + str(user_description).lower()
        + " " + " ".join(str(t).lower() for t in user_tags)
    )

    equipment_hits: Dict[str, int] = {}
    for equip_class in EQUIPMENT_COVERAGE_RULES:
        score = 0
        if equip_class.lower() in col_blob:
            score += 2  # class name itself present
        for alias in EQUIPMENT_ALIASES.get(equip_class, []):
            if len(alias) >= 3 and alias.lower() in col_blob:
                score += 1
        if score > 0:
            equipment_hits[equip_class] = score
    return equipment_hits


# ---------------------------------------------------------------------------
# Tier C helpers
# ---------------------------------------------------------------------------

def _maintenance_vocab_hits(columns: List[str]) -> Dict[str, List[str]]:
    """Return {group: [matched_keywords]} for maintenance vocabulary groups."""
    col_blob = " ".join(str(c).lower().strip() for c in columns)
    maintenance_hits: Dict[str, List[str]] = {}
    for group, keywords in MAINTENANCE_VOCAB.items():
        matched = set()
        for kw in keywords:
            if kw in col_blob:
                matched.add(kw)
        if matched:
            maintenance_hits[group] = sorted(matched)
    return maintenance_hits


# ---------------------------------------------------------------------------
# Structural signal helper
# ---------------------------------------------------------------------------

def _detect_timestamp_col_fast(df: pd.DataFrame) -> Optional[str]:
    """Fast timestamp detection (subset of agent.py version, no heavy parsing)."""
    for col in df.columns:
        cl = str(col).lower().strip()
        if any(h in cl for h in ["time", "date", "ts", "timestamp", "datetime"]):
            return col
    return None


# ---------------------------------------------------------------------------
# Cross-signal coherence (anti-gaming layer)
# ---------------------------------------------------------------------------

EXPECTED_SENSOR_PAIRS = [
    ("vibration", "temperature"),
    ("speed", "current"),
    ("pressure", "flow"),
    ("temperature", "current"),
]


def _cross_signal_coherence(
    df: pd.DataFrame, hits: Dict[str, List[Tuple[str, str, str]]]
) -> float:
    """
    Returns 0.0–1.0. Real PdM sensor data exhibits inter-signal correlations.
    Randomly renamed data will show |r| ≈ 0 across expected pairs.
    """
    present_pairs = [
        (a, b) for (a, b) in EXPECTED_SENSOR_PAIRS
        if a in hits and b in hits
    ]
    if not present_pairs:
        return 0.5  # no pair to check — neutral

    corrs: List[float] = []
    for (a, b) in present_pairs:
        col_a = hits[a][0][0]  # first matched col for type a
        col_b = hits[b][0][0]  # first matched col for type b
        if col_a not in df.columns or col_b not in df.columns:
            continue
        try:
            s_a = pd.to_numeric(df[col_a], errors="coerce")
            s_b = pd.to_numeric(df[col_b], errors="coerce")
            paired = pd.concat([s_a, s_b], axis=1).dropna()
            if len(paired) >= 20:
                r = abs(float(paired.iloc[:, 0].corr(paired.iloc[:, 1])))
                if not np.isnan(r):
                    corrs.append(r)
        except Exception:
            pass

    if not corrs:
        return 0.5

    mean_r = float(mean(corrs))
    # Scale: |r| >= 0.15 → 1.0; |r| < 0.02 → 0.0 (linear between)
    scaled = min(1.0, max(0.0, (mean_r - 0.02) / (0.15 - 0.02)))
    return round(scaled, 3)


# ---------------------------------------------------------------------------
# Main KB-match scorer
# ---------------------------------------------------------------------------

def compute_kb_match_score(
    df: pd.DataFrame,
    filename: str = "",
    user_name: str = "",
    user_description: str = "",
    user_tags: Optional[List[str]] = None,
) -> Tuple[float, Dict]:
    """
    Returns (kb_match_score: 0.0–1.0, raw_evidence: dict).

    Architecture:
      Tier A (sensor vocab + value corroboration): 0.35
      Tier B (equipment class hits): 0.25
      Tier C (maintenance vocabulary): 0.15
      Cross-signal coherence: 0.15
      Structural signal (timestamp + numeric cols): 0.10
    """
    user_tags = user_tags or []

    # --- Tier A ---
    hits = _sensor_vocab_hits(list(df.columns))
    n_sensor_types = len(hits)
    sensor_diversity = min(n_sensor_types / 4.0, 1.0)  # 4+ types → full credit

    corroboration_scores = _corroborate_all(df, hits)
    mean_corr = float(mean(corroboration_scores.values())) if corroboration_scores else 0.0

    # Hard gaming penalty: if ANY sensor has corroboration=0.0 (physically impossible
    # values) we treat it as a gaming attempt and apply a strong multiplier.
    # A real PdM dataset never has physically-impossible sensor readings.
    n_zero_corr = sum(1 for v in corroboration_scores.values() if v == 0.0)
    n_checked = len(corroboration_scores)
    if n_checked > 0 and n_zero_corr / n_checked >= 0.5:
        # More than half of matched sensors are physically impossible → strong gaming signal
        mean_corr = min(mean_corr, 0.1)  # collapse mean_corr to penalize heavily

    tier_a = sensor_diversity * (0.5 + 0.5 * mean_corr)
    # mean_corr=0 (gaming) → tier_a = sensor_diversity * 0.5 → penalised
    # mean_corr=1 (legit)  → tier_a = sensor_diversity * 1.0 → full

    # --- Tier B ---
    equipment_hits = _equipment_class_hits(
        list(df.columns), filename, user_name, user_description, user_tags
    )
    tier_b = min(sum(equipment_hits.values()) / 3.0, 1.0) if equipment_hits else 0.0

    # --- Tier C ---
    maintenance_hits = _maintenance_vocab_hits(list(df.columns))
    n_groups_hit = len(maintenance_hits)
    tier_c = min(n_groups_hit / 2.0, 1.0)  # 2+ groups → full credit

    # --- Cross-signal coherence ---
    coherence = _cross_signal_coherence(df, hits)

    # --- Structural signal ---
    has_timestamp = _detect_timestamp_col_fast(df) is not None
    n_numeric = df.select_dtypes(include=[np.number]).shape[1]
    structural_signal = 0.0
    if has_timestamp and n_numeric >= 5:
        structural_signal = 1.0
    elif has_timestamp or n_numeric >= 5:
        structural_signal = 0.5

    # --- Weighted combination ---
    W = {
        "tier_a": 0.35,
        "tier_b": 0.25,
        "tier_c": 0.15,
        "coherence": 0.15,
        "structural": 0.10,
    }
    kb_match_score = (
        W["tier_a"] * tier_a
        + W["tier_b"] * tier_b
        + W["tier_c"] * tier_c
        + W["coherence"] * coherence
        + W["structural"] * structural_signal
    )
    kb_match_score = round(min(max(kb_match_score, 0.0), 1.0), 4)

    raw = {
        "n_sensor_types": n_sensor_types,
        "detected_sensors": list(hits.keys()),
        "sensor_diversity": round(sensor_diversity, 3),
        "mean_corroboration": round(mean_corr, 3),
        "corroboration_per_type": {k: round(v, 3) for k, v in corroboration_scores.items()},
        "equipment_hits": equipment_hits,
        "maintenance_hits": {k: v for k, v in maintenance_hits.items()},
        "coherence": round(coherence, 3),
        "structural_signal": structural_signal,
        "tier_a": round(tier_a, 3),
        "tier_b": round(tier_b, 3),
        "tier_c": round(tier_c, 3),
        "kb_match_score": kb_match_score,
        "n_numeric": n_numeric,
        "has_timestamp": has_timestamp,
    }
    return kb_match_score, raw
