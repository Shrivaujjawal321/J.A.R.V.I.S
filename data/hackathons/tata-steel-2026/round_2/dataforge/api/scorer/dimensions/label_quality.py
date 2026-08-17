"""Label quality dimension: cleanlab if available, else cross-val disagreement heuristic."""

from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Any, Dict


def _fast_disagreement_fallback(df: pd.DataFrame, label_col: str) -> Dict[str, Any]:
    """
    Lightweight label-noise estimate without cleanlab.
    Strategy: 3-fold cross-val with a fast GBM; any sample whose held-out predicted
    class has probability > 0.80 for the OPPOSITE class is flagged as a potential mislabel.
    Returns estimated noisy_fraction and list of suspect indices.
    """
    from sklearn.model_selection import StratifiedKFold
    from sklearn.preprocessing import LabelEncoder
    from sklearn.impute import SimpleImputer
    import lightgbm as lgb

    y = df[label_col]
    X_raw = df.drop(columns=[label_col])

    # Only use numeric columns for speed
    X_num = X_raw.select_dtypes(include=[np.number])
    if X_num.shape[1] == 0:
        return {"noisy_fraction": 0.0, "suspect_count": 0, "method": "no_numeric_features"}

    le = LabelEncoder()
    y_enc = le.fit_transform(y.fillna(y.mode()[0]))
    n_classes = len(le.classes_)

    if n_classes < 2:
        return {"noisy_fraction": 0.0, "suspect_count": 0, "method": "single_class"}

    imp = SimpleImputer(strategy="median")
    X_imp = imp.fit_transform(X_num)

    # For binary, use binary objective; else multiclass
    objective = "binary" if n_classes == 2 else "multiclass"
    params = {
        "objective": objective,
        "n_estimators": 50,
        "max_depth": 4,
        "learning_rate": 0.1,
        "num_leaves": 15,
        "n_jobs": -1,
        "verbose": -1,
        "random_state": 42,
    }
    if n_classes > 2:
        params["num_class"] = n_classes

    kf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    probs = np.zeros((len(y_enc), n_classes))

    for train_idx, val_idx in kf.split(X_imp, y_enc):
        model = lgb.LGBMClassifier(**params)
        model.fit(X_imp[train_idx], y_enc[train_idx])
        fold_probs = model.predict_proba(X_imp[val_idx])
        probs[val_idx] = fold_probs

    # Sample is "suspect" if model is confident it should be a different class
    predicted_class = np.argmax(probs, axis=1)
    max_prob = np.max(probs, axis=1)
    # Suspect: model ≥80% confident in a DIFFERENT class than labelled
    suspect_mask = (predicted_class != y_enc) & (max_prob >= 0.80)
    suspect_count = int(suspect_mask.sum())
    noisy_fraction = suspect_count / max(len(y_enc), 1)

    return {
        "noisy_fraction": round(noisy_fraction, 4),
        "suspect_count": suspect_count,
        "method": "cross_val_disagreement",
        "suspect_indices": np.where(suspect_mask)[0][:20].tolist(),  # first 20
    }


def compute(df: pd.DataFrame, label_col: str = None, **ctx) -> Dict[str, Any]:
    if label_col is None or label_col not in df.columns:
        return {
            "score": 50.0,
            "detail": "No label column provided — label quality not assessed.",
            "severity": "info",
            "raw": {},
        }

    series = df[label_col].dropna()
    if series.nunique() < 2:
        return {
            "score": 20.0,
            "detail": f"Label column '{label_col}' has < 2 unique values.",
            "severity": "critical",
            "raw": {},
        }

    # Try cleanlab first
    cleanlab_available = False
    try:
        from cleanlab.filter import find_label_issues  # type: ignore
        from sklearn.model_selection import cross_val_predict
        from sklearn.preprocessing import LabelEncoder
        from sklearn.impute import SimpleImputer
        import lightgbm as lgb

        y = df[label_col]
        X_raw = df.drop(columns=[label_col])
        X_num = X_raw.select_dtypes(include=[np.number])

        if X_num.shape[1] > 0:
            le = LabelEncoder()
            y_enc = le.fit_transform(y.fillna(y.mode()[0]))
            n_classes = len(le.classes_)

            imp = SimpleImputer(strategy="median")
            X_imp = imp.fit_transform(X_num)

            params = {
                "objective": "binary" if n_classes == 2 else "multiclass",
                "n_estimators": 50,
                "max_depth": 4,
                "n_jobs": -1,
                "verbose": -1,
                "random_state": 42,
            }
            if n_classes > 2:
                params["num_class"] = n_classes

            model = lgb.LGBMClassifier(**params)
            probs = cross_val_predict(model, X_imp, y_enc, cv=3, method="predict_proba")
            issues = find_label_issues(y_enc, probs, return_indices_ranked_by="self_confidence")
            suspect_count = len(issues)
            noisy_fraction = suspect_count / max(len(y_enc), 1)
            cleanlab_available = True
            method = "cleanlab"
            raw = {
                "noisy_fraction": round(noisy_fraction, 4),
                "suspect_count": suspect_count,
                "method": "cleanlab",
                "suspect_indices": issues[:20].tolist(),
            }
        else:
            raise ValueError("no numeric features")

    except Exception:
        raw = _fast_disagreement_fallback(df, label_col)
        noisy_fraction = raw["noisy_fraction"]
        suspect_count = raw["suspect_count"]
        method = raw.get("method", "cross_val_disagreement")

    # Score: 100 - 300*noisy_fraction (capped at 0)
    score = max(0.0, min(100.0, 100.0 - 300.0 * noisy_fraction))

    if noisy_fraction >= 0.15:
        severity = "critical"
    elif noisy_fraction >= 0.05:
        severity = "warning"
    elif noisy_fraction > 0.01:
        severity = "info"
    else:
        severity = "ok"

    detail = (
        f"Estimated label noise: {noisy_fraction*100:.1f}% "
        f"({suspect_count} suspect rows out of {len(series):,}). "
        f"Method: {method}."
    )
    if suspect_count > 0 and "suspect_indices" in raw and raw["suspect_indices"]:
        top_indices = raw["suspect_indices"][:5]
        detail += f" First suspect row indices: {top_indices}."

    return {
        "score": round(score, 2),
        "detail": detail,
        "severity": severity,
        "raw": raw,
    }
