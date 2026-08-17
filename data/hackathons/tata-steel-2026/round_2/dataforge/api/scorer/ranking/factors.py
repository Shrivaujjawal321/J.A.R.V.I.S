"""
Ranking factor computations — §2.2 of 03_relevance_and_ranking_engine.md

compute_feature_richness (F): column diversity, label quality, row count, completeness.
compute_ps_alignment    (P): structural requirements from the Tata Steel R2 PS.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, List, Optional

from scorer.relevance.kb_match import _sensor_vocab_hits


# ---------------------------------------------------------------------------
# F — Feature Richness (0–100)
# ---------------------------------------------------------------------------

def compute_feature_richness(
    df: pd.DataFrame,
    dataset_type: str,
    label_col: Optional[str],
    timestamp_col: Optional[str],
    raw_sub_scores: Dict,
) -> float:
    """
    Returns feature_richness score 0–100.
    Sub-factors:
      Column count vs PdM baseline (20 pts)
      Label presence + quality (25 pts)
      Sensor type diversity (25 pts)
      Row count / data volume (15 pts)
      Completeness (missing values) (15 pts)
    """
    score = 0.0

    # Sub-factor 1: Numeric column count (20 pts)
    n_num = df.select_dtypes(include=[np.number]).shape[1]
    if n_num >= 20:
        score += 20.0
    elif n_num >= 10:
        score += 15.0
    elif n_num >= 5:
        score += 10.0
    elif n_num >= 3:
        score += 5.0

    # Sub-factor 2: Label presence + quality (25 pts)
    if label_col and label_col in df.columns:
        lq_dim = raw_sub_scores.get("label_quality", {})
        lq_score = lq_dim.get("score", 50.0) if isinstance(lq_dim, dict) else 50.0
        score += 25.0 * (lq_score / 100.0)
    # No label → 0 pts; unlabelled data cannot train/evaluate PdM models

    # Sub-factor 3: Sensor type diversity across KB (25 pts)
    hits = _sensor_vocab_hits(list(df.columns))
    n_sensor_types = len(hits)
    # 6+ distinct sensor types = rich monitoring suite
    sensor_diversity_score = min(n_sensor_types / 6.0, 1.0) * 25.0
    score += sensor_diversity_score

    # Sub-factor 4: Row count (adequate data volume) (15 pts)
    n_rows = len(df)
    if n_rows >= 100_000:
        score += 15.0
    elif n_rows >= 10_000:
        score += 12.0
    elif n_rows >= 1_000:
        score += 8.0
    elif n_rows >= 500:
        score += 4.0

    # Sub-factor 5: Completeness (missing values) (15 pts)
    comp_dim = raw_sub_scores.get("completeness", {})
    comp_score = comp_dim.get("score", 50.0) if isinstance(comp_dim, dict) else 50.0
    score += 15.0 * (comp_score / 100.0)

    return round(min(score, 100.0), 2)


# ---------------------------------------------------------------------------
# P — Problem-Statement Alignment (0–100)
# ---------------------------------------------------------------------------

def compute_ps_alignment(
    df: pd.DataFrame,
    dataset_type: str,
    label_col: Optional[str],
    timestamp_col: Optional[str],
    raw_kb_evidence: Dict,
    domain_pdm_raw: Optional[Dict],
) -> float:
    """
    Returns ps_alignment score 0–100.
    Checks whether the dataset satisfies structural requirements from the Tata Steel R2 PS:
    "equipment logs, sensor alerts, manuals, SOPs, historical maintenance records;
     predictive maintenance, anomaly detection, root-cause, failure prediction"
    """
    score = 0.0
    domain_pdm_raw = domain_pdm_raw or {}

    # Criterion 1: Has a label column representing failure/fault/anomaly (25 pts)
    if label_col:
        lc = str(label_col).lower()
        if any(k in lc for k in ["failure", "fault", "anomaly", "alarm", "defect", "rul"]):
            score += 25.0
        else:
            score += 12.0  # generic target, partial credit

    # Criterion 2: Temporal structure (timestamps) (20 pts)
    if timestamp_col:
        score += 20.0

    # Criterion 3: Asset/equipment metadata (15 pts)
    sub_checks = domain_pdm_raw.get("sub_checks", {})
    metadata_found = (
        sub_checks.get("metadata_coverage", {})
        .get("raw", {})
        .get("n_found", 0)
    )
    if metadata_found >= 2:
        score += 15.0
    elif metadata_found >= 1:
        score += 8.0

    # Criterion 4: Equipment class is one of the 17 KB equipment classes (20 pts)
    eq_class = domain_pdm_raw.get("equipment_class") or raw_kb_evidence.get("equipment_hits")
    if eq_class:
        score += 20.0

    # Criterion 5: Multiple sensor modalities (20 pts)
    n_sensors = raw_kb_evidence.get("n_sensor_types", 0)
    if n_sensors >= 4:
        score += 20.0
    elif n_sensors >= 2:
        score += 12.0
    elif n_sensors >= 1:
        score += 5.0

    return round(min(score, 100.0), 2)
