"""Schema validity: type consistency, constant columns, impossible ranges for known domains."""

from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Any, Dict, List


# Physical-range rules for steel-plant / industrial domain columns
# Format: {column_keyword: (min_val, max_val)}
DOMAIN_RANGES: Dict[str, tuple] = {
    "temperature": (-50, 2000),      # Celsius
    "temp": (-50, 2000),
    "pressure": (0, 1000),           # bar
    "vibration": (0, 1000),          # mm/s
    "rpm": (0, 100_000),
    "current": (-5000, 5000),        # Amps
    "torque": (-100_000, 100_000),   # Nm
    "humidity": (0, 100),            # %
    "voltage": (-15_000, 15_000),    # V
    "speed": (0, 1_000_000),
    "load": (0, 1_000_000),
}


def _check_domain_ranges(df: pd.DataFrame) -> List[Dict]:
    violations = []
    for col in df.select_dtypes(include=[np.number]).columns:
        col_lower = col.lower()
        for keyword, (lo, hi) in DOMAIN_RANGES.items():
            if keyword in col_lower:
                s = df[col].dropna()
                bad_low = int((s < lo).sum())
                bad_high = int((s > hi).sum())
                if bad_low + bad_high > 0:
                    violations.append({
                        "column": col,
                        "rule": f"expected [{lo}, {hi}]",
                        "violations": bad_low + bad_high,
                        "sample_vals": s[(s < lo) | (s > hi)].head(3).tolist(),
                    })
                break
    return violations


def compute(df: pd.DataFrame, **ctx) -> Dict[str, Any]:
    n_rows, n_cols = df.shape
    issues = []
    issue_weights = []

    # 1. Constant columns
    constant_cols = [c for c in df.columns if df[c].nunique() <= 1]
    if constant_cols:
        issues.append(f"Constant/single-value columns: {constant_cols[:5]}")
        issue_weights.append(5.0 * len(constant_cols))

    # 2. Mixed-type columns (object columns that are mostly numeric but have some non-numeric)
    mixed_cols = []
    for col in df.select_dtypes(include=["object"]).columns:
        sample = df[col].dropna().head(1000)
        if len(sample) == 0:
            continue
        n_numeric = pd.to_numeric(sample, errors="coerce").notna().sum()
        frac_numeric = n_numeric / len(sample)
        if 0.1 < frac_numeric < 0.9:
            mixed_cols.append(col)
    if mixed_cols:
        issues.append(f"Mixed-type columns (object but ~numeric): {mixed_cols[:5]}")
        issue_weights.append(8.0 * len(mixed_cols))

    # 3. Columns that should be numeric but are object (all-numeric strings)
    should_be_numeric = []
    for col in df.select_dtypes(include=["object"]).columns:
        sample = df[col].dropna().head(500)
        if len(sample) == 0:
            continue
        n_numeric = pd.to_numeric(sample, errors="coerce").notna().sum()
        if n_numeric / len(sample) > 0.95:
            should_be_numeric.append(col)
    if should_be_numeric:
        issues.append(f"Columns stored as string but contain numeric data: {should_be_numeric[:5]}")
        issue_weights.append(4.0 * len(should_be_numeric))

    # 4. Domain range violations
    violations = _check_domain_ranges(df)
    if violations:
        violation_strs = [f"'{v['column']}' has {v['violations']} values outside {v['rule']}" for v in violations[:3]]
        issues.append("Physical range violations: " + "; ".join(violation_strs))
        issue_weights.append(10.0 * len(violations))

    # 5. Column names: leading/trailing whitespace
    bad_names = [c for c in df.columns if c != c.strip()]
    if bad_names:
        issues.append(f"Column names with whitespace: {bad_names[:5]}")
        issue_weights.append(2.0)

    # 6. Duplicate column names
    if len(df.columns) != len(set(df.columns)):
        issues.append("Duplicate column names detected.")
        issue_weights.append(15.0)

    # Score
    total_penalty = sum(issue_weights)
    # Normalise: 100 penalty units → score 0
    score = max(0.0, min(100.0, 100.0 - total_penalty))

    if total_penalty >= 30:
        severity = "critical"
    elif total_penalty >= 15:
        severity = "warning"
    elif total_penalty > 0:
        severity = "info"
    else:
        severity = "ok"

    if issues:
        detail = f"{len(issues)} schema issue(s) found: " + " | ".join(issues)
    else:
        detail = f"Schema looks valid. {n_cols} columns with consistent types and no domain violations."

    return {
        "score": round(score, 2),
        "detail": detail,
        "severity": severity,
        "raw": {
            "constant_cols": constant_cols,
            "mixed_type_cols": mixed_cols,
            "should_be_numeric": should_be_numeric,
            "domain_violations": violations,
            "total_penalty": round(total_penalty, 2),
        },
    }
