"""Distribution sanity: constant cols, zero-heavy, infinite values, physical-range heuristics."""

from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Any, Dict, List


def compute(df: pd.DataFrame, label_col: str = None, **ctx) -> Dict[str, Any]:
    issues: List[str] = []
    issue_weights: List[float] = []

    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if label_col and label_col in num_cols:
        num_cols = [c for c in num_cols if c != label_col]

    if not num_cols:
        return {
            "score": 50.0,
            "detail": "No numeric feature columns — distribution sanity check skipped.",
            "severity": "info",
            "raw": {},
        }

    # 1. Constant columns (0 variance)
    constant_cols = [c for c in num_cols if df[c].nunique(dropna=True) <= 1]
    if constant_cols:
        issues.append(f"Constant columns (no variance): {constant_cols[:5]}")
        issue_weights.append(8.0 * len(constant_cols))

    # 2. Columns with >50% zeros
    zero_heavy: List[str] = []
    for col in num_cols:
        s = df[col].dropna()
        if len(s) == 0:
            continue
        zero_frac = (s == 0).mean()
        if zero_frac > 0.5:
            zero_heavy.append(f"'{col}' ({zero_frac*100:.0f}% zeros)")
    if zero_heavy:
        issues.append(f"Columns with >50% zero values: {'; '.join(zero_heavy[:5])}")
        issue_weights.append(3.0 * len(zero_heavy))

    # 3. Infinite values
    inf_cols: List[str] = []
    for col in num_cols:
        s = df[col]
        n_inf = int(np.isinf(s.replace([None], np.nan).dropna()).sum())
        if n_inf > 0:
            inf_cols.append(f"'{col}' ({n_inf} inf)")
    if inf_cols:
        issues.append(f"Infinite values: {'; '.join(inf_cols[:5])}")
        issue_weights.append(10.0 * len(inf_cols))

    # 4. Extreme skew (|skewness| > 10 suggests unlogged or outlier-dominated)
    high_skew: List[str] = []
    for col in num_cols[:50]:  # cap for speed
        s = df[col].dropna()
        if len(s) < 20:
            continue
        try:
            skew = float(s.skew())
            if abs(skew) > 10:
                high_skew.append(f"'{col}' (skew={skew:.1f})")
        except Exception:
            pass
    if high_skew:
        issues.append(f"Extremely skewed columns (|skew|>10, may need log-transform): {'; '.join(high_skew[:5])}")
        issue_weights.append(2.0 * len(high_skew))

    # 5. Near-zero variance (not constant, but very low)
    low_var: List[str] = []
    for col in num_cols:
        s = df[col].dropna()
        if len(s) < 10:
            continue
        cv = s.std() / (abs(s.mean()) + 1e-9)
        if 0 < cv < 0.001 and col not in constant_cols:
            low_var.append(col)
    if low_var:
        issues.append(f"Near-zero coefficient of variation columns: {low_var[:5]}")
        issue_weights.append(2.0 * len(low_var))

    total_penalty = sum(issue_weights)
    score = max(0.0, min(100.0, 100.0 - total_penalty))

    if total_penalty >= 25:
        severity = "critical"
    elif total_penalty >= 12:
        severity = "warning"
    elif total_penalty > 0:
        severity = "info"
    else:
        severity = "ok"

    if issues:
        detail = f"{len(issues)} distribution issue(s): " + " | ".join(issues)
    else:
        detail = f"Distribution looks healthy across {len(num_cols)} numeric columns — no constants, inf values, or severe zero-inflation."

    return {
        "score": round(score, 2),
        "detail": detail,
        "severity": severity,
        "raw": {
            "constant_cols": constant_cols,
            "zero_heavy": zero_heavy,
            "inf_cols": inf_cols,
            "high_skew": high_skew,
            "low_var": low_var,
            "total_penalty": round(total_penalty, 2),
        },
    }
