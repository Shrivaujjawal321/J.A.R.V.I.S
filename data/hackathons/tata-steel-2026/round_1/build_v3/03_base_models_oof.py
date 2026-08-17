"""
Step 3: Base Models OOF Predictions
- 5-fold StratifiedKFold (seed=42, same as v2)
- 3 base models: LightGBM, XGBoost, CatBoost
- SMOTE inside each fold (train only)
- Save OOF probas + averaged test probas for each model
- Save per-fold and aggregate metrics
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score, recall_score, precision_score
from imblearn.over_sampling import SMOTE
import lightgbm as lgb
import xgboost as xgb
from catboost import CatBoostClassifier
import warnings
warnings.filterwarnings("ignore")

BASE = "/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1"
V3   = BASE + "/build_v3"

print("Loading v3 parquets and feature list...")
train = pd.read_parquet(V3 + "/train_v3.parquet")
test  = pd.read_parquet(V3 + "/test_v3.parquet")

with open(V3 + "/feature_list_v3.json") as f:
    feat_info = json.load(f)

FEATURES = feat_info["features"]
TARGET   = "Y"

# Ensure all features exist in both datasets
FEATURES = [f for f in FEATURES if f in train.columns and f in test.columns]
print(f"Using {len(FEATURES)} features")

X_train = train[FEATURES].values
y_train = train[TARGET].values
X_test  = test[FEATURES].values

print(f"Train: {X_train.shape}  |  Test: {X_test.shape}")
print(f"Class dist: {dict(zip(*np.unique(y_train, return_counts=True)))}")

# ── Model definitions ─────────────────────────────────────────────────────────
models = {
    "lgb": lgb.LGBMClassifier(
        is_unbalance=True,
        learning_rate=0.02,
        num_leaves=15,
        min_data_in_leaf=5,
        feature_fraction=0.7,
        bagging_fraction=0.7,
        bagging_freq=1,
        n_estimators=300,
        random_state=42,
        n_jobs=-1,
        verbose=-1,
    ),
    "xgb": xgb.XGBClassifier(
        scale_pos_weight=19.5,
        learning_rate=0.03,
        max_depth=4,
        n_estimators=300,
        subsample=0.7,
        colsample_bytree=0.7,
        eval_metric="auc",
        random_state=42,
        use_label_encoder=False,
        verbosity=0,
        n_jobs=-1,
    ),
    "cat": CatBoostClassifier(
        auto_class_weights="Balanced",
        learning_rate=0.03,
        depth=4,
        iterations=300,
        verbose=False,
        random_state=42,
        thread_count=-1,
    ),
}

# ── 5-Fold CV ─────────────────────────────────────────────────────────────────
N_FOLDS = 5
skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)

oof_preds  = {name: np.zeros(len(y_train)) for name in models}
test_preds = {name: np.zeros(len(X_test))  for name in models}
metrics    = {name: [] for name in models}

for fold, (tr_idx, va_idx) in enumerate(skf.split(X_train, y_train)):
    print(f"\n{'='*50}")
    print(f"FOLD {fold+1}/{N_FOLDS}  (train={len(tr_idx)}, val={len(va_idx)})")

    X_tr, y_tr = X_train[tr_idx], y_train[tr_idx]
    X_va, y_va = X_train[va_idx], y_train[va_idx]

    # SMOTE on train portion only
    sm = SMOTE(sampling_strategy=0.3, k_neighbors=3, random_state=42)
    X_tr_s, y_tr_s = sm.fit_resample(X_tr, y_tr)
    print(f"  SMOTE: {y_tr.sum():.0f} positives -> {y_tr_s.sum():.0f}")

    for name, clf in models.items():
        clf_fold = clf.__class__(**clf.get_params())
        clf_fold.fit(X_tr_s, y_tr_s)

        va_proba = clf_fold.predict_proba(X_va)[:, 1]
        te_proba = clf_fold.predict_proba(X_test)[:, 1]

        oof_preds[name][va_idx] += va_proba
        test_preds[name]        += te_proba / N_FOLDS

        auc = roc_auc_score(y_va, va_proba)
        r05 = recall_score(y_va, (va_proba >= 0.5).astype(int))
        p05 = precision_score(y_va, (va_proba >= 0.5).astype(int), zero_division=0)

        metrics[name].append({"fold": fold+1, "auc": auc, "r@0.5": r05, "p@0.5": p05})
        print(f"  [{name:3s}] AUC={auc:.4f}  R@0.5={r05:.3f}  P@0.5={p05:.3f}")

# ── Aggregate metrics ──────────────────────────────────────────────────────────
print("\n" + "="*60)
print("AGGREGATE OOF METRICS:")
agg = {}
for name in models:
    aucs = [m["auc"] for m in metrics[name]]
    oof_auc = roc_auc_score(y_train, oof_preds[name])
    agg[name] = {
        "oof_auc":      oof_auc,
        "fold_auc_mean": float(np.mean(aucs)),
        "fold_auc_std":  float(np.std(aucs)),
        "per_fold":      metrics[name],
    }
    print(f"  [{name:3s}] OOF AUC={oof_auc:.4f}  |  fold mean={np.mean(aucs):.4f} ± {np.std(aucs):.4f}")

with open(V3 + "/base_metrics.json", "w") as f:
    json.dump(agg, f, indent=2)
print("Saved base_metrics.json")

# ── Save OOF and test probas ──────────────────────────────────────────────────
coil_ids = train["CoilID"].values
for name in models:
    pd.DataFrame({
        "CoilID":   coil_ids,
        "Y":        y_train,
        "oof_proba": oof_preds[name],
    }).to_parquet(V3 + f"/oof_{name}.parquet", index=False)

    pd.DataFrame({
        "CoilID":      test["CoilID"].values,
        "test_proba":  test_preds[name],
    }).to_parquet(V3 + f"/test_{name}.parquet", index=False)

    print(f"  Saved oof_{name}.parquet  +  test_{name}.parquet")

print("\n=== Step 3 COMPLETE ===")
