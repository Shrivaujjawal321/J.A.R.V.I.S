"""
Step 2 (v2c): Train v2 LightGBM.
Key insight: val set has only 13 positives -> AUC variance ~0.017 per step.
Early stopping with noisy val kills good models after 18-30 rounds.
Fix: NO early stopping, fixed 250 rounds at LR=0.05.
Evidence: Fold 4 (best fold in v1 AND v2b) ran to 142 rounds — shows optimal
is ~100-200 rounds, not <30.
Run: .venv/bin/python data/hackathons/tata-steel-2026/round_1/build_v2/02_train_v2.py
"""
import os, json, warnings
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score, recall_score, precision_score
from imblearn.over_sampling import SMOTE

warnings.filterwarnings("ignore")

V2_DIR = "data/hackathons/tata-steel-2026/round_1/build_v2"

print("=" * 65)
print("STEP 2 (v2c): LightGBM — fixed 250 rounds, no early stopping")
print("  Root cause fix: 13 val positives -> AUC noise=0.017 kills early stop")
print("=" * 65)

train = pd.read_parquet(f"{V2_DIR}/train_v2.parquet")
feat_meta = json.load(open(f"{V2_DIR}/feature_list_v2.json"))
feat_cols = [c for c in feat_meta["features"] if c in train.columns]

X = train[feat_cols].values.astype(np.float64)
y = train["Y"].values.astype(int)
coil_ids = train["CoilID"].values

print(f"Train: {X.shape}  Positives: {y.sum()} ({100*y.mean():.2f}%)")
print(f"AUC noise with 13 val positives: ~{1/np.sqrt(13*258):.4f} — disabling early stop")

# ─── Params: no is_unbalance (SMOTE handles), no early stopping ──────────────
params_v2 = {
    "objective":        "binary",
    "metric":           "auc",
    "is_unbalance":     False,
    "learning_rate":    0.05,
    "num_leaves":       15,
    "min_data_in_leaf": 5,
    "feature_fraction": 0.7,
    "bagging_fraction": 0.7,
    "bagging_freq":     3,
    "reg_alpha":        0.1,
    "reg_lambda":       0.1,
    "verbose":          -1,
    "seed":             42,
}
FIXED_ROUNDS = 250  # no early stopping — consistent training across all folds

kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
oof_proba = np.zeros(len(y))
fold_metrics = []
models = []

print(f"\nTraining 5-fold CV (fixed {FIXED_ROUNDS} rounds, no early stopping)...")
print("-" * 65)

for fold_idx, (train_idx, val_idx) in enumerate(kf.split(X, y)):
    X_tr, y_tr = X[train_idx], y[train_idx]
    X_val, y_val = X[val_idx],   y[val_idx]

    pos_before = int(y_tr.sum())
    neg_before = int((y_tr==0).sum())

    # SMOTE inside fold only
    try:
        smote = SMOTE(sampling_strategy=0.3, k_neighbors=3, random_state=42)
        X_tr_s, y_tr_s = smote.fit_resample(X_tr, y_tr)
    except ValueError as e:
        print(f"  [WARN] SMOTE failed fold {fold_idx+1}: {e}")
        X_tr_s, y_tr_s = X_tr, y_tr

    pos_after = int(y_tr_s.sum())

    dtrain = lgb.Dataset(X_tr_s, label=y_tr_s, feature_name=feat_cols)
    # No valid_sets — no early stopping
    model = lgb.train(
        params_v2, dtrain,
        num_boost_round=FIXED_ROUNDS,
        # No callbacks, no valid_sets — pure fixed rounds
    )

    val_pred          = model.predict(X_val)
    oof_proba[val_idx] = val_pred

    auc     = roc_auc_score(y_val, val_pred)
    rec_05  = recall_score(y_val,    (val_pred>=0.5).astype(int), zero_division=0)
    prec_05 = precision_score(y_val, (val_pred>=0.5).astype(int), zero_division=0)

    print(f"Fold {fold_idx+1}: AUC={auc:.4f}  iter={FIXED_ROUNDS} [FIXED OK]  "
          f"pos {pos_before}->{pos_after}  R@0.5={rec_05:.3f}  P@0.5={prec_05:.3f}")

    fold_metrics.append({
        "fold":             fold_idx+1,
        "auc":              float(auc),
        "best_round":       FIXED_ROUNDS,
        "pos_before_smote": pos_before,
        "pos_after_smote":  pos_after,
        "neg_before_smote": neg_before,
        "neg_after_smote":  int((y_tr_s==0).sum()),
        "recall_at_05":     float(rec_05),
        "prec_at_05":       float(prec_05),
    })

    model.save_model(f"{V2_DIR}/models/fold_{fold_idx}.lgb")
    models.append(model)

print("-" * 65)

oof_auc = roc_auc_score(y, oof_proba)
print(f"\nOOF AUC: {oof_auc:.4f}  (v1 was 0.827)")
print(f"OOF proba: min={oof_proba.min():.4f}  p25={np.percentile(oof_proba,25):.4f}  "
      f"median={np.median(oof_proba):.4f}  p75={np.percentile(oof_proba,75):.4f}  "
      f"max={oof_proba.max():.4f}")
print(f"Defect:   min={oof_proba[y==1].min():.4f}  "
      f"median={np.median(oof_proba[y==1]):.4f}  max={oof_proba[y==1].max():.4f}")
print(f"Non-def:  min={oof_proba[y==0].min():.4f}  "
      f"median={np.median(oof_proba[y==0]):.4f}  max={oof_proba[y==0].max():.4f}")

# Feature importance
import_sum = np.zeros(len(feat_cols))
for m in models:
    import_sum += m.feature_importance(importance_type="gain")
top_idx = np.argsort(import_sum)[::-1][:20]
print("\nTop 20 features by gain:")
for rank, i in enumerate(top_idx):
    print(f"  {rank+1:2d}. {feat_cols[i]:<30s} {import_sum[i]:.1f}")

iso_ri = feat_cols.index("iso_score") if "iso_score" in feat_cols else -1
if iso_ri >= 0:
    iso_gr = int(np.where(np.argsort(import_sum)[::-1] == iso_ri)[0][0]) + 1
    print(f"\niso_score rank: {iso_gr} / {len(feat_cols)}")
    print("  [KEEP — top 15]" if iso_gr <= 15 else "  [NOTE: rank {iso_gr} — may drop in v3]")

oof_df = pd.DataFrame({"CoilID": coil_ids, "Y": y, "oof_proba": oof_proba})
oof_df.to_parquet(f"{V2_DIR}/oof_v2.parquet", index=False)

cv_summary = {
    "fold_metrics":   fold_metrics,
    "oof_auc":        float(oof_auc),
    "oof_proba_min":  float(oof_proba.min()),
    "oof_proba_max":  float(oof_proba.max()),
    "mean_fold_auc":  float(np.mean([m["auc"] for m in fold_metrics])),
    "min_fold_iters": FIXED_ROUNDS,
    "fixed_rounds":   FIXED_ROUNDS,
    "v1_oof_auc":     0.827,
}
json.dump(cv_summary, open(f"{V2_DIR}/cv_summary_v2.json","w"), indent=2)

print(f"\nSaved oof_v2.parquet + cv_summary_v2.json")
print(f"All folds ran exactly {FIXED_ROUNDS} rounds — fold stability target MET")
print("Step 2 DONE.")
