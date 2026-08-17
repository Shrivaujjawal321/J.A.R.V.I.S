"""Class balance dimension: imbalance ratio with non-linear scoring."""

from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Any, Dict


def compute(df: pd.DataFrame, label_col: str = None, **ctx) -> Dict[str, Any]:
    """
    If no label: score 50 (neutral, no info).
    Imbalance ratio IR = majority_count / minority_count.
    Score curve: IR=1 → 100, IR=2 → 90, IR=5 → 70, IR=10 → 50, IR=20 → 30, IR=100 → 10.
    Uses log-decay: score = 100 * exp(-0.06 * (IR - 1))
    """
    if label_col is None or label_col not in df.columns:
        return {
            "score": 50.0,
            "detail": "No label column provided — class balance not assessed.",
            "severity": "info",
            "raw": {},
        }

    series = df[label_col].dropna()
    if series.nunique() < 2:
        return {
            "score": 30.0,
            "detail": f"Label column '{label_col}' has fewer than 2 unique values — not a valid classification target.",
            "severity": "critical",
            "raw": {},
        }

    counts = series.value_counts()
    n_classes = len(counts)
    majority = int(counts.iloc[0])
    minority = int(counts.iloc[-1])
    total = int(len(series))

    ir = majority / max(minority, 1)

    # Non-linear decay: feels roughly right for industrial data
    # IR=1→100, IR=10→55, IR=50→12
    raw_score = 100.0 * np.exp(-0.055 * (ir - 1.0))
    score = max(0.0, min(100.0, raw_score))

    # Severity thresholds
    if ir >= 20:
        severity = "critical"
    elif ir >= 10:
        severity = "warning"
    elif ir >= 3:
        severity = "info"
    else:
        severity = "ok"

    class_dist = counts.to_dict()
    class_pcts = {str(k): round(100.0 * v / total, 1) for k, v in class_dist.items()}

    detail = (
        f"{n_classes} classes. Imbalance ratio: {ir:.1f}:1 "
        f"(majority class '{counts.index[0]}' = {class_pcts.get(str(counts.index[0]), '?')}%, "
        f"minority class '{counts.index[-1]}' = {class_pcts.get(str(counts.index[-1]), '?')}%)."
    )

    if ir >= 10:
        detail += f" Severe imbalance will require class-weight or resampling for reliable ML."
    elif ir >= 3:
        detail += " Moderate imbalance — use class_weight='balanced' in training."

    return {
        "score": round(score, 2),
        "detail": detail,
        "severity": severity,
        "raw": {
            "imbalance_ratio": round(ir, 2),
            "n_classes": n_classes,
            "class_counts": {str(k): int(v) for k, v in class_dist.items()},
            "class_pcts": class_pcts,
            "majority_class": str(counts.index[0]),
            "minority_class": str(counts.index[-1]),
        },
    }
