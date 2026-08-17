"""Outliers dimension: IsolationForest + IQR cross-check."""

from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Any, Dict


def compute(df: pd.DataFrame, **ctx) -> Dict[str, Any]:
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if not num_cols:
        return {
            "score": 50.0,
            "detail": "No numeric columns found — outlier analysis not applicable.",
            "severity": "info",
            "raw": {},
        }

    # Work on a sample for speed
    sample_size = min(len(df), 100_000)
    df_num = df[num_cols].dropna()
    if len(df_num) == 0:
        return {
            "score": 0.0,
            "detail": "All numeric rows are null after dropping missing values.",
            "severity": "critical",
            "raw": {},
        }

    df_sample = df_num.sample(n=min(sample_size, len(df_num)), random_state=42)

    # --- IQR outliers per column ---
    iqr_outlier_counts: Dict[str, int] = {}
    for col in num_cols:
        s = df_sample[col].dropna()
        if len(s) == 0:
            continue
        Q1 = s.quantile(0.25)
        Q3 = s.quantile(0.75)
        IQR = Q3 - Q1
        if IQR == 0:
            continue
        fence_low = Q1 - 3.0 * IQR
        fence_high = Q3 + 3.0 * IQR
        n_out = int(((s < fence_low) | (s > fence_high)).sum())
        if n_out > 0:
            iqr_outlier_counts[col] = n_out

    total_iqr_outliers = sum(iqr_outlier_counts.values())
    iqr_frac = total_iqr_outliers / max(len(df_sample) * len(num_cols), 1)

    # --- IsolationForest (fast, contamination auto) ---
    iso_frac = 0.0
    iso_count = 0
    try:
        from sklearn.ensemble import IsolationForest
        from sklearn.impute import SimpleImputer

        imp = SimpleImputer(strategy="median")
        X = imp.fit_transform(df_sample)

        # Estimate contamination from IQR fraction, clamp 0.01..0.3
        contamination = max(0.01, min(0.30, iqr_frac * 2))
        iso = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=42,
            n_jobs=-1,
        )
        preds = iso.fit_predict(X)
        iso_count = int((preds == -1).sum())
        iso_frac = iso_count / len(X)
    except Exception:
        iso_frac = iqr_frac

    # Consensus: take average of both methods
    combined_frac = (iqr_frac + iso_frac) / 2.0

    # Score: gentle — some outliers are normal in industrial data
    # 5% outliers → 85 score, 15% → 60, 30% → 30
    score = max(0.0, min(100.0, 100.0 * np.exp(-4.5 * combined_frac)))

    if combined_frac >= 0.20:
        severity = "critical"
    elif combined_frac >= 0.10:
        severity = "warning"
    elif combined_frac >= 0.03:
        severity = "info"
    else:
        severity = "ok"

    worst_cols = sorted(iqr_outlier_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    worst_str = ", ".join([f"'{c}' ({n:,})" for c, n in worst_cols]) if worst_cols else "none"

    detail = (
        f"IQR fence (3×): {total_iqr_outliers:,} outlier cells across {len(iqr_outlier_counts)} column(s). "
        f"IsolationForest: {iso_count:,} anomalous rows ({iso_frac*100:.1f}%). "
        f"Most affected: {worst_str}."
    )
    if severity == "ok":
        detail = f"Outlier rate is within acceptable range ({combined_frac*100:.1f}% consensus). {detail}"

    return {
        "score": round(score, 2),
        "detail": detail,
        "severity": severity,
        "raw": {
            "iqr_outlier_cols": iqr_outlier_counts,
            "iqr_frac": round(iqr_frac, 4),
            "iso_frac": round(iso_frac, 4),
            "combined_frac": round(combined_frac, 4),
        },
    }
