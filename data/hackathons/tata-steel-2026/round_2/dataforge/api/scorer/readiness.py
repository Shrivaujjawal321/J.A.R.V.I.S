"""Readiness scoring: LightGBM 3-fold CV → baseline AUC → quality-adjusted readiness."""

from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Any, Dict, Optional
from scipy.stats import norm


def compute_readiness(
    df: pd.DataFrame,
    label_col: str,
    composite_score: float,
    sub_scores: Dict[str, Dict],
    target_auc: float = 0.80,
    dataset_type: str = "tabular",
) -> Optional[Dict[str, Any]]:
    """
    Returns readiness dict or None if training should be skipped.
    Skips if: no label, composite < 40, or fewer than 50 labelled rows.
    """
    if not label_col or label_col not in df.columns:
        return None

    y = df[label_col].dropna()
    if y.nunique() < 2:
        return None

    if composite_score < 40:
        return {
            "skipped": True,
            "reason": (
                f"Composite score {composite_score:.0f}/100 is below 40 — "
                "baseline training skipped. Fix critical data quality issues first."
            ),
        }

    if len(y) < 50:
        return {
            "skipped": True,
            "reason": f"Only {len(y)} labelled rows — too few for reliable 3-fold CV.",
        }

    # --- Prepare features ---
    from sklearn.preprocessing import LabelEncoder
    from sklearn.impute import SimpleImputer
    from sklearn.model_selection import StratifiedKFold, cross_val_score
    import lightgbm as lgb

    X_raw = df.drop(columns=[label_col])
    # Drop non-numeric and timestamp
    X_num = X_raw.select_dtypes(include=[np.number])

    if X_num.shape[1] == 0:
        return {
            "skipped": True,
            "reason": "No numeric features available for training.",
        }

    le = LabelEncoder()
    y_enc = le.fit_transform(y.fillna(y.mode()[0]))
    n_classes = len(le.classes_)

    imp = SimpleImputer(strategy="median")
    X_imp = imp.fit_transform(X_num)

    # Cap rows for speed (60s budget)
    max_rows = 100_000
    if len(X_imp) > max_rows:
        idx = np.random.RandomState(42).choice(len(X_imp), max_rows, replace=False)
        X_imp = X_imp[idx]
        y_enc = y_enc[idx]

    params = {
        "n_estimators": 100,
        "max_depth": 5,
        "num_leaves": 31,
        "learning_rate": 0.1,
        "class_weight": "balanced",
        "n_jobs": -1,
        "verbose": -1,
        "random_state": 42,
    }
    if n_classes == 2:
        params["objective"] = "binary"
    else:
        params["objective"] = "multiclass"
        params["num_class"] = n_classes

    model = lgb.LGBMClassifier(**params)

    try:
        scoring = "roc_auc" if n_classes == 2 else "roc_auc_ovr"
        cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
        scores = cross_val_score(model, X_imp, y_enc, cv=cv, scoring=scoring, n_jobs=1)
        baseline_auc = float(np.mean(scores))
    except Exception as e:
        return {
            "skipped": True,
            "reason": f"Cross-validation failed: {type(e).__name__}: {e}",
        }

    # --- Quality-adjusted penalties ---
    label_noise_raw = sub_scores.get("label_quality", {}).get("raw", {})
    noisy_frac = label_noise_raw.get("noisy_fraction", 0.0)
    label_noise_penalty = min(0.08, noisy_frac * 0.5)

    imbalance_raw = sub_scores.get("class_balance", {}).get("raw", {})
    ir = imbalance_raw.get("imbalance_ratio", 1.0)
    # Penalty scales from 0 (IR=1) to 0.05 (IR=100)
    imbalance_penalty = min(0.05, 0.005 * np.log10(max(ir, 1.0)))

    temporal_raw = sub_scores.get("temporal_coverage", {}).get("raw", {})
    gap_frac = temporal_raw.get("gap_fraction", 0.0) if dataset_type == "time_series" else 0.0
    temporal_penalty = min(0.04, gap_frac * 0.10)

    adjusted_auc = baseline_auc - label_noise_penalty - imbalance_penalty - temporal_penalty
    adjusted_auc = max(0.5, min(1.0, adjusted_auc))

    # Readiness: probability of exceeding target_auc given adjusted_auc ± 0.04 uncertainty
    readiness_pct = float(norm.sf(target_auc, loc=adjusted_auc, scale=0.04) * 100)
    readiness_pct = round(max(0.0, min(100.0, readiness_pct)), 1)

    return {
        "readiness_pct": readiness_pct,
        "baseline_auc": round(baseline_auc, 4),
        "target_auc": target_auc,
        "adjusted_auc": round(adjusted_auc, 4),
        "penalties": {
            "label_noise": round(label_noise_penalty, 4),
            "imbalance": round(imbalance_penalty, 4),
            "temporal_gaps": round(temporal_penalty, 4),
        },
        "cv_scores": [round(float(s), 4) for s in scores],
    }
