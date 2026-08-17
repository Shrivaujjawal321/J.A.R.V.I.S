"""Leakage detection: high feature-target correlation + lookahead in time series."""

from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Any, Dict, List


def compute(
    df: pd.DataFrame,
    label_col: str = None,
    timestamp_col: str = None,
    dataset_type: str = "tabular",
    **ctx,
) -> Dict[str, Any]:
    leaks: List[Dict] = []
    warnings: List[str] = []

    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # --- Feature-target correlation leakage ---
    if label_col and label_col in df.columns:
        y = df[label_col]
        target_num = pd.to_numeric(y, errors="coerce")

        feature_cols = [c for c in num_cols if c != label_col]

        for col in feature_cols:
            s = df[col].dropna()
            t = target_num.loc[s.index].dropna()
            common_idx = s.index.intersection(t.index)
            if len(common_idx) < 20:
                continue
            from scipy.stats import spearmanr
            corr, pval = spearmanr(s.loc[common_idx], t.loc[common_idx])
            if abs(corr) >= 0.95 and pval < 0.01:
                leaks.append({
                    "column": col,
                    "type": "feature_target_correlation",
                    "spearman_r": round(float(corr), 4),
                    "pval": round(float(pval), 6),
                })

    # --- Temporal lookahead: shifted correlation ---
    if dataset_type == "time_series" and timestamp_col and timestamp_col in df.columns:
        df_sorted = df.sort_values(timestamp_col).reset_index(drop=True)
        feature_cols_ts = [c for c in num_cols if c != label_col and c != timestamp_col]

        for col in feature_cols_ts[:20]:  # cap for speed
            s = df_sorted[col].dropna()
            if len(s) < 50:
                continue
            # Check if feature at time t+1 correlates with label at time t (lookahead)
            shifted = s.shift(-1)
            target_here = (
                pd.to_numeric(df_sorted[label_col], errors="coerce")
                if label_col and label_col in df.columns
                else None
            )
            if target_here is not None:
                common = shifted.notna() & target_here.notna()
                if common.sum() > 20:
                    from scipy.stats import spearmanr
                    corr, pval = spearmanr(shifted[common], target_here[common])
                    if abs(corr) >= 0.90 and pval < 0.01:
                        leaks.append({
                            "column": col,
                            "type": "temporal_lookahead",
                            "spearman_r_shifted": round(float(corr), 4),
                        })

    # Score: severe penalty for any detected leak
    n_leaks = len(leaks)
    leak_detected = n_leaks > 0

    if n_leaks == 0:
        score = 100.0
        severity = "ok"
        detail = "No feature-target leakage or temporal lookahead detected."
    elif n_leaks == 1:
        score = 20.0
        severity = "critical"
    else:
        score = max(0.0, 20.0 - 5.0 * (n_leaks - 1))
        severity = "critical"

    if leak_detected:
        leak_strs = [
            f"'{l['column']}' ({l['type']}, r={l.get('spearman_r', l.get('spearman_r_shifted', '?'))})"
            for l in leaks[:5]
        ]
        detail = (
            f"WARNING: {n_leaks} potential data leakage column(s) detected. "
            f"These columns are suspiciously correlated with the target: {'; '.join(leak_strs)}. "
            f"Review before training — this will produce artificially high model scores."
        )

    return {
        "score": round(score, 2),
        "detail": detail,
        "severity": severity,
        "raw": {
            "leak_count": n_leaks,
            "leaks": leaks,
            "leak_detected": leak_detected,
        },
    }
