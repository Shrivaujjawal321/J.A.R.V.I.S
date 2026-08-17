"""Feature redundancy: correlated pairs + VIF."""

from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Any, Dict, List


def compute(df: pd.DataFrame, label_col: str = None, timestamp_col: str = None, **ctx) -> Dict[str, Any]:
    exclude = [c for c in [label_col, timestamp_col] if c]
    num_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in exclude]

    if len(num_cols) < 2:
        return {
            "score": 100.0,
            "detail": "Fewer than 2 numeric feature columns — redundancy check not applicable.",
            "severity": "ok",
            "raw": {},
        }

    # Sample for speed. NB: dropna(how="all") can shrink the frame, so the sample
    # size must be derived from the POST-dropna length — never the original len(df),
    # otherwise sample(n>population) raises ValueError on small/sparse datasets.
    df_avail = df[num_cols].dropna(how="all")
    if len(df_avail) == 0:
        return {
            "score": 50.0,
            "detail": "All numeric feature columns are empty — redundancy not assessable.",
            "severity": "info",
            "raw": {},
        }
    sample_size = min(len(df_avail), 50_000)
    df_sample = df_avail.sample(n=sample_size, random_state=42)

    # Fill remaining NAs with median for correlation
    df_filled = df_sample.fillna(df_sample.median())

    # Correlation matrix
    try:
        corr_matrix = df_filled.corr(method="pearson").abs()
    except Exception:
        return {
            "score": 50.0,
            "detail": "Could not compute correlation matrix.",
            "severity": "info",
            "raw": {},
        }

    # Find highly correlated pairs (|r| >= 0.95)
    threshold = 0.95
    redundant_pairs: List[Dict] = []
    cols = corr_matrix.columns.tolist()
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            val = corr_matrix.iloc[i, j]
            if val >= threshold:
                redundant_pairs.append({
                    "col_a": cols[i],
                    "col_b": cols[j],
                    "pearson_r": round(float(val), 4),
                })

    # VIF for top N columns (cap at 20 for speed)
    vif_results: List[Dict] = []
    vif_cols = num_cols[:20]
    if len(vif_cols) >= 2:
        try:
            from statsmodels.stats.outliers_influence import variance_inflation_factor  # type: ignore
            from sklearn.impute import SimpleImputer

            imp = SimpleImputer(strategy="median")
            X = imp.fit_transform(df[vif_cols])
            for idx, col in enumerate(vif_cols):
                try:
                    vif_val = variance_inflation_factor(X, idx)
                    if not np.isfinite(vif_val):
                        vif_val = 999.0
                    if vif_val >= 10:
                        vif_results.append({"column": col, "vif": round(float(vif_val), 2)})
                except Exception:
                    pass
        except ImportError:
            pass

    n_redundant = len(redundant_pairs)
    n_high_vif = len(vif_results)

    # Score
    penalty = 5.0 * n_redundant + 3.0 * n_high_vif
    score = max(0.0, min(100.0, 100.0 - penalty))

    if n_redundant >= 5 or n_high_vif >= 5:
        severity = "warning"
    elif n_redundant >= 2 or n_high_vif >= 2:
        severity = "info"
    else:
        severity = "ok"

    if redundant_pairs:
        pairs_str = "; ".join(
            [f"'{p['col_a']}' ↔ '{p['col_b']}' (r={p['pearson_r']})" for p in redundant_pairs[:4]]
        )
        detail = f"{n_redundant} highly correlated feature pair(s) (|r|≥{threshold}): {pairs_str}. "
    else:
        detail = "No highly correlated feature pairs (|r|≥0.95) detected. "

    if vif_results:
        vif_str = ", ".join([f"'{v['column']}' VIF={v['vif']}" for v in vif_results[:4]])
        detail += f"{n_high_vif} feature(s) with VIF≥10 (multicollinearity): {vif_str}."
    else:
        detail += "VIF check: no severe multicollinearity detected."

    return {
        "score": round(score, 2),
        "detail": detail,
        "severity": severity,
        "raw": {
            "redundant_pairs": redundant_pairs,
            "high_vif": vif_results,
            "n_numeric_features": len(num_cols),
        },
    }
