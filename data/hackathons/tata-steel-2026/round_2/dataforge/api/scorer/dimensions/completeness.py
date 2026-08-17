"""Completeness dimension: per-column and aggregate missingness."""

from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Any, Dict


def compute(df: pd.DataFrame, **ctx) -> Dict[str, Any]:
    """
    Score = 100 * (1 - weighted_missing_rate)
    Weighted: columns with >50% missing penalise twice as much.
    """
    n_rows, n_cols = df.shape
    if n_cols == 0 or n_rows == 0:
        return {
            "score": 0.0,
            "detail": "Empty dataset.",
            "severity": "critical",
            "raw": {},
        }

    null_fracs = df.isnull().mean()

    # Overall missingness across all cells
    overall_null = float(df.isnull().mean().mean())  # fraction of ALL cells that are null

    # Critical column count: columns with >50% missing
    n_critical = int((null_fracs > 0.5).sum())
    n_serious   = int(((null_fracs > 0.20) & (null_fracs <= 0.5)).sum())
    n_warning   = int(((null_fracs > 0.05) & (null_fracs <= 0.20)).sum())
    n_minor     = int(((null_fracs > 0.0)  & (null_fracs <= 0.05)).sum())

    # Base score from overall null rate (linear)
    base_score = 100.0 * (1.0 - overall_null)

    # Additional penalty per severity band:
    #   critical (>50%): 12 pts each — severe blocker
    #   serious  (>20%): 5 pts each — major imputation needed
    #   warning  (>5%): 2 pts each — notable per-column missingness
    critical_penalty = n_critical * 12.0
    serious_penalty  = n_serious  * 5.0
    warning_penalty  = n_warning  * 2.0

    score = max(0.0, min(100.0, base_score - critical_penalty - serious_penalty - warning_penalty))

    # Per-column details for improvements
    bad_cols = null_fracs[null_fracs > 0.0].sort_values(ascending=False)
    critical_cols = null_fracs[null_fracs > 0.5].index.tolist()
    warning_cols = null_fracs[(null_fracs > 0.05) & (null_fracs <= 0.5)].index.tolist()

    overall_null_pct = float(df.isnull().mean().mean()) * 100

    if critical_cols:
        severity = "critical"
        detail = (
            f"{overall_null_pct:.1f}% average null rate across {n_cols} columns. "
            f"Critical columns (>50% missing): {', '.join(critical_cols[:5])}. "
            f"Total missing cells: {int(df.isnull().sum().sum()):,}."
        )
    elif warning_cols:
        severity = "warning"
        detail = (
            f"{overall_null_pct:.1f}% average null rate. "
            f"Columns with notable missingness: {', '.join(warning_cols[:5])}."
        )
    elif score < 99:
        severity = "info"
        detail = f"{overall_null_pct:.1f}% average null rate — minor gaps in {len(bad_cols)} column(s)."
    else:
        severity = "ok"
        detail = "No missing values detected — dataset is complete."

    return {
        "score": round(score, 2),
        "detail": detail,
        "severity": severity,
        "raw": {
            "null_fracs": null_fracs.to_dict(),
            "critical_cols": critical_cols,
            "warning_cols": warning_cols,
            "overall_null_pct": overall_null_pct,
        },
    }
