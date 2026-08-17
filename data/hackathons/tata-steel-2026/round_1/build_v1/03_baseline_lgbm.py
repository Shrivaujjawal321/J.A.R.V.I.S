"""
Step 3 — Baseline LightGBM with 5-fold StratifiedKFold
Outputs: oof_predictions.parquet, models/fold_{i}.lgb, fold metrics
"""

import sys
sys.path.insert(0, "/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1/ml_harness")

import json
import warnings
import numpy as np
import pandas as pd
import lightgbm as lgb
from pathlib import Path
from sklearn.metrics import roc_auc_score, precision_recall_curve, recall_score, precision_score

from utils.seed import set_seed
from utils.cv import stratified_kfold

warnings.filterwarnings("ignore")
set_seed(42)

# ── Paths ─────────────────────────────────────────────────────────────────────
OUT_DIR   = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1/build_v1")
MODEL_DIR = OUT_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

# ── Load engineered data ──────────────────────────────────────────────────────
train_eng = pd.read_parquet(OUT_DIR / "train_engineered.parquet")
feat_info = json.loads((OUT_DIR / "feature_list.json").read_text())
feature_cols = feat_info["feature_cols"]

X = train_eng[feature_cols].values
y = train_eng["Y"].values
coil_ids = train_eng["CoilID"].values

n_pos = y.sum()
n_neg = (y == 0).sum()
spw   = n_neg / n_pos

print(f"Features: {len(feature_cols)}")
print(f"Train rows: {len(X)}")
print(f"Positives: {n_pos}, Negatives: {n_neg}")
print(f"scale_pos_weight: {spw:.2f}")
print()

# ── LightGBM params ───────────────────────────────────────────────────────────
params = {
    "objective": "binary",
    "metric": "auc",
    "scale_pos_weight": spw,
    "learning_rate": 0.03,
    "num_leaves": 31,
    "min_child_samples": 10,
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 5,
    "reg_alpha": 0.1,
    "reg_lambda": 0.1,
    "random_state": 42,
    "verbose": -1,
    "n_jobs": -1,
}

# ── 5-fold CV ─────────────────────────────────────────────────────────────────
oof_proba = np.zeros(len(X))
fold_metrics = []

print("=" * 60)
print("5-FOLD STRATIFIED CV")
print("=" * 60)

for fold_idx, (tr_idx, val_idx) in enumerate(stratified_kfold(y, n_splits=5, seed=42)):
    X_tr, X_val = X[tr_idx], X[val_idx]
    y_tr, y_val = y[tr_idx], y[val_idx]

    dtrain = lgb.Dataset(X_tr, label=y_tr)
    dval   = lgb.Dataset(X_val, label=y_val, reference=dtrain)

    callbacks = [
        lgb.early_stopping(stopping_rounds=100, verbose=False),
        lgb.log_evaluation(period=-1),
    ]

    model = lgb.train(
        params,
        dtrain,
        num_boost_round=1000,
        valid_sets=[dval],
        callbacks=callbacks,
    )

    val_proba = model.predict(X_val)
    oof_proba[val_idx] = val_proba

    # Metrics at default threshold 0.5
    val_pred_05 = (val_proba >= 0.5).astype(int)
    auc     = roc_auc_score(y_val, val_proba)
    recall  = recall_score(y_val, val_pred_05, zero_division=0)
    prec    = precision_score(y_val, val_pred_05, zero_division=0)

    # Best threshold on this fold: maximize recall subject to precision >= 0.90
    prec_arr, rec_arr, thr_arr = precision_recall_curve(y_val, val_proba)
    # precision_recall_curve returns precision/recall in decreasing threshold order
    # Find all thresholds where precision >= 0.90
    viable_mask = prec_arr[:-1] >= 0.90
    if viable_mask.any():
        # Among viable thresholds, pick the one with max recall
        best_recall_at_90prec = rec_arr[:-1][viable_mask].max()
        best_thr_at_90prec    = thr_arr[viable_mask][np.argmax(rec_arr[:-1][viable_mask])]
    else:
        best_recall_at_90prec = 0.0
        best_thr_at_90prec    = float("nan")

    # Precision at recall=1.0
    # Find thresholds where recall == 1.0 (catch ALL positives)
    recall1_mask = rec_arr[:-1] >= 1.0
    if recall1_mask.any():
        prec_at_recall1 = prec_arr[:-1][recall1_mask].max()
    else:
        # Lower threshold until we catch all
        prec_at_recall1 = prec_arr[0]  # lowest threshold = all ones

    # Best AUC-based threshold for sanity
    f_scores = 2 * prec_arr[:-1] * rec_arr[:-1] / (prec_arr[:-1] + rec_arr[:-1] + 1e-9)
    best_f1_thr = thr_arr[np.argmax(f_scores)]
    best_f1_pred = (val_proba >= best_f1_thr).astype(int)
    f1_recall = recall_score(y_val, best_f1_pred, zero_division=0)
    f1_prec   = precision_score(y_val, best_f1_pred, zero_division=0)

    print(f"\nFold {fold_idx + 1}:")
    print(f"  Best round     : {model.best_iteration}")
    print(f"  AUC            : {auc:.4f}")
    print(f"  @thr=0.50 — recall={recall:.3f}, precision={prec:.3f}")
    print(f"  @best-F1 thr={best_f1_thr:.3f} — recall={f1_recall:.3f}, precision={f1_prec:.3f}")
    print(f"  Recall @ precision≥0.90: {best_recall_at_90prec:.3f}  (thr={best_thr_at_90prec:.4f})")
    print(f"  Precision @ recall=1.0 : {prec_at_recall1:.4f}")

    fold_metrics.append({
        "fold": fold_idx + 1,
        "auc": float(auc),
        "recall_at_05": float(recall),
        "prec_at_05": float(prec),
        "recall_at_prec90": float(best_recall_at_90prec),
        "thr_at_prec90": float(best_thr_at_90prec) if not np.isnan(best_thr_at_90prec) else None,
        "prec_at_recall1": float(prec_at_recall1),
        "best_round": int(model.best_iteration),
    })

    model.save_model(str(MODEL_DIR / f"fold_{fold_idx}.lgb"))

# ── OOF summary ───────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("OOF SUMMARY")
print("=" * 60)

oof_auc = roc_auc_score(y, oof_proba)

# OOF precision-recall curve
prec_arr_oof, rec_arr_oof, thr_arr_oof = precision_recall_curve(y, oof_proba)

viable_oof = prec_arr_oof[:-1] >= 0.90
if viable_oof.any():
    oof_recall_at_prec90 = rec_arr_oof[:-1][viable_oof].max()
    oof_thr_at_prec90    = thr_arr_oof[viable_oof][np.argmax(rec_arr_oof[:-1][viable_oof])]
else:
    oof_recall_at_prec90 = 0.0
    oof_thr_at_prec90    = float("nan")

# Recall=1.0 on OOF
r1_mask_oof = rec_arr_oof[:-1] >= 1.0
prec_at_r1_oof = prec_arr_oof[:-1][r1_mask_oof].max() if r1_mask_oof.any() else prec_arr_oof[0]

print(f"  OOF AUC                    : {oof_auc:.4f}")
print(f"  OOF Recall @ precision≥0.90: {oof_recall_at_prec90:.4f}  (thr={oof_thr_at_prec90:.4f})")
print(f"  OOF Precision @ recall=1.0 : {prec_at_r1_oof:.4f}")
print()

mean_auc          = np.mean([m["auc"] for m in fold_metrics])
mean_recall_90    = np.mean([m["recall_at_prec90"] for m in fold_metrics])
mean_prec_r1      = np.mean([m["prec_at_recall1"] for m in fold_metrics])

print(f"  Mean fold AUC              : {mean_auc:.4f}")
print(f"  Mean fold recall@prec≥0.90 : {mean_recall_90:.4f}")
print(f"  Mean fold prec@recall=1.0  : {mean_prec_r1:.4f}")

# ── Save OOF predictions ──────────────────────────────────────────────────────
oof_df = pd.DataFrame({
    "CoilID": coil_ids,
    "Y": y,
    "oof_proba": oof_proba,
})
oof_df.to_parquet(OUT_DIR / "oof_predictions.parquet", index=False)
print(f"\nOOF saved: {OUT_DIR / 'oof_predictions.parquet'}")

# Save fold metrics
summary = {
    "fold_metrics": fold_metrics,
    "oof_auc": float(oof_auc),
    "oof_recall_at_prec90": float(oof_recall_at_prec90),
    "oof_thr_at_prec90": float(oof_thr_at_prec90) if not np.isnan(oof_thr_at_prec90) else None,
    "oof_prec_at_recall1": float(prec_at_r1_oof),
    "mean_fold_auc": float(mean_auc),
    "mean_fold_recall_at_prec90": float(mean_recall_90),
    "mean_fold_prec_at_recall1": float(mean_prec_r1),
}
(OUT_DIR / "cv_summary.json").write_text(json.dumps(summary, indent=2))
print(f"CV summary saved: {OUT_DIR / 'cv_summary.json'}")
print()
print("Step 3 complete.")
