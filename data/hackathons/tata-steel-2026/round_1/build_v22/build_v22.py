"""
V22 — V4 structure preserved + AutoGluon's CatBoost_r167 hyperparams swapped in.

Single surgical modification per Boss's mandate: preserve V4 baseline, modify
incrementally.

V4's architecture: LGB + XGB + CatBoost stacking, LR meta, Platt calibration,
score-aware (R+P)/2 threshold, gate at inference.

V22's modification: CatBoost hyperparams swapped from V5 defaults to AG-r167:
  depth=6, grow_policy='SymmetricTree', l2_leaf_reg=2.15428,
  learning_rate=0.06864, max_ctr_complexity=4, one_hot_max_size=10.
This config hit AUC 0.906 in AutoGluon (vs V5 CatBoost's 0.876).

LGB + XGB unchanged. No NN. No mega blend.
"""

from __future__ import annotations

import json
import warnings
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
import lightgbm as lgb
import xgboost as xgb
from catboost import CatBoostClassifier

warnings.filterwarnings("ignore")

ROOT = Path("/home/ujjwal/Documents/J.A.R.V.I.S.")
V5 = ROOT / "data/hackathons/tata-steel-2026/round_1/build_v5"
V22 = ROOT / "data/hackathons/tata-steel-2026/round_1/build_v22"
V22.mkdir(parents=True, exist_ok=True)

SEED = 42
N_FOLDS = 5
CAL_DELTA = 2.67
X42_DEFECT_CEIL = 0.025067
X39_CLEAN_FLOOR = 169.0


def hard_gate(df):
    return ((df["X42"] > X42_DEFECT_CEIL) | (df["X39"] >= X39_CLEAN_FLOOR)).values


print("Loading V5 features...")
train_v5 = pd.read_parquet(V5 / "train_v5.parquet").reset_index(drop=True)
test_v5 = pd.read_parquet(V5 / "test_v5.parquet").reset_index(drop=True)
with open(V5 / "feature_list_v5.json") as f:
    v5_features = json.load(f)["features"]

y = train_v5["Y"].values.astype(int)
n_train, n_test = len(train_v5), len(test_v5)
X_train = train_v5[v5_features].values
X_test = test_v5[v5_features].values

# ─── 5-fold stacking — V4 architecture preserved ─────────────────────────────
print("\n5-fold stacking with AutoGluon's CatBoost r167 hyperparams")
print("  (LGB + XGB unchanged from V5; CatBoost upgraded to AG r167)")

skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
oof_lgb = np.zeros(n_train); oof_xgb = np.zeros(n_train); oof_cat = np.zeros(n_train)
test_lgb = np.zeros(n_test); test_xgb = np.zeros(n_test); test_cat = np.zeros(n_test)
fold_aucs = {"lgb": [], "xgb": [], "cat": []}

for fold_i, (tr, va) in enumerate(skf.split(np.zeros(n_train), y)):
    Xtr, Xva = X_train[tr], X_train[va]
    Xte = X_test
    ytr, yva = y[tr], y[va]

    # LGB — V5 defaults (proven)
    m_lgb = lgb.LGBMClassifier(
        n_estimators=500, learning_rate=0.03, max_depth=6, num_leaves=31,
        min_child_samples=10, reg_alpha=0.1, reg_lambda=0.1,
        random_state=SEED, verbose=-1, class_weight="balanced",
    )
    m_lgb.fit(Xtr, ytr, eval_set=[(Xva, yva)], callbacks=[lgb.early_stopping(30, verbose=False)])
    oof_lgb[va] = m_lgb.predict_proba(Xva)[:, 1]
    test_lgb += m_lgb.predict_proba(Xte)[:, 1] / N_FOLDS
    fold_aucs["lgb"].append(roc_auc_score(yva, oof_lgb[va]))

    # XGB — V5 defaults (proven)
    m_xgb = xgb.XGBClassifier(
        n_estimators=500, learning_rate=0.03, max_depth=6,
        scale_pos_weight=(ytr == 0).sum() / max(ytr.sum(), 1),
        reg_alpha=0.1, reg_lambda=0.1,
        random_state=SEED, eval_metric="auc",
        early_stopping_rounds=30, verbosity=0,
    )
    m_xgb.fit(Xtr, ytr, eval_set=[(Xva, yva)], verbose=False)
    oof_xgb[va] = m_xgb.predict_proba(Xva)[:, 1]
    test_xgb += m_xgb.predict_proba(Xte)[:, 1] / N_FOLDS
    fold_aucs["xgb"].append(roc_auc_score(yva, oof_xgb[va]))

    # CatBoost — UPGRADED to AutoGluon r167 hyperparams (only change)
    m_cat = CatBoostClassifier(
        iterations=500,
        learning_rate=0.06864209415792857,  # AG r167
        depth=6,
        l2_leaf_reg=2.1542798306067823,  # AG r167
        max_ctr_complexity=4,  # AG r167
        one_hot_max_size=10,  # AG r167
        grow_policy="SymmetricTree",  # AG r167
        auto_class_weights="Balanced",  # preserve V4 balance handling
        random_seed=SEED, verbose=False,
        early_stopping_rounds=30,
    )
    m_cat.fit(Xtr, ytr, eval_set=(Xva, yva))
    oof_cat[va] = m_cat.predict_proba(Xva)[:, 1]
    test_cat += m_cat.predict_proba(Xte)[:, 1] / N_FOLDS
    fold_aucs["cat"].append(roc_auc_score(yva, oof_cat[va]))

    print(f"  Fold {fold_i+1}: LGB={fold_aucs['lgb'][-1]:.4f}  XGB={fold_aucs['xgb'][-1]:.4f}  CAT={fold_aucs['cat'][-1]:.4f}")

lgb_mean = float(np.mean(fold_aucs["lgb"]))
xgb_mean = float(np.mean(fold_aucs["xgb"]))
cat_mean = float(np.mean(fold_aucs["cat"]))
print(f"\nMean: LGB={lgb_mean:.4f}  XGB={xgb_mean:.4f}  CAT={cat_mean:.4f}  (V5 CatBoost: 0.876)")


# ─── Meta + Platt + gate + threshold ─────────────────────────────────────────
print("\n[Meta + Platt + gate]")
X_meta_oof = np.column_stack([oof_lgb, oof_xgb, oof_cat])
X_meta_test = np.column_stack([test_lgb, test_xgb, test_cat])
meta = LogisticRegression(C=1.0, max_iter=1000)
meta_cal = CalibratedClassifierCV(meta, method="sigmoid", cv=5)
meta_cal.fit(X_meta_oof, y)
p_oof = meta_cal.predict_proba(X_meta_oof)[:, 1]
p_test = meta_cal.predict_proba(X_meta_test)[:, 1]
meta_auc = float(roc_auc_score(y, p_oof))
print(f"  V22 Meta OOF AUC: {meta_auc:.4f}  (V5 baseline: 0.8886)")

gate_oof = hard_gate(train_v5); gate_test = hard_gate(test_v5)
p_oof_g = p_oof.copy(); p_oof_g[gate_oof] = 0
p_test_g = p_test.copy(); p_test_g[gate_test] = 0

uniq = np.sort(np.unique(np.concatenate([p_oof_g, [0.0, 1.0]])))
cuts = np.r_[uniq[0]-1e-6, 0.5*(uniq[:-1]+uniq[1:]), uniq[-1]+1e-6]
best_T, best_S, best_R, best_P, best_n = 0, 0, 0, 0, 0
for t in cuts:
    pred = (p_oof_g >= t).astype(int)
    tp = ((pred==1)&(y==1)).sum(); fp = ((pred==1)&(y==0)).sum(); fn = ((pred==0)&(y==1)).sum()
    R = tp/(tp+fn) if (tp+fn) else 0; P = tp/(tp+fp) if (tp+fp) else 0
    s = (R+P)/2*100
    if s > best_S: best_S, best_T, best_R, best_P, best_n = s, t, R, P, pred.sum()

test_pred = (p_test_g >= best_T).astype(int)
print(f"  V22: T={best_T:.5f}  OOF={best_S:.3f}  R={best_R:.3f}  P={best_P:.3f}  n_oof={best_n}  n_test={test_pred.sum()}")
cal_lb = best_S + CAL_DELTA
print(f"  Calibrated LB est: {cal_lb:.2f}")

# Bootstrap
rng = np.random.default_rng(SEED)
boot = np.empty(2000)
for i in range(2000):
    idx = rng.integers(0, n_train, n_train)
    pred = (p_oof_g[idx] >= best_T).astype(int)
    yb = y[idx]
    tp = ((pred==1)&(yb==1)).sum(); fp = ((pred==1)&(yb==0)).sum(); fn = ((pred==0)&(yb==1)).sum()
    R = tp/(tp+fn) if (tp+fn) else 0; P = tp/(tp+fp) if (tp+fp) else 0
    boot[i] = (R+P)/2*100
ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
print(f"  Bootstrap CI OOF: [{ci_lo:.2f}, {ci_hi:.2f}]")

# Compare with V4 prediction set
v4 = pd.read_csv(ROOT / "data/hackathons/tata-steel-2026/round_1/build_v4/expected_submission.csv")
v4_pos = set(v4.loc[v4.Y==1, 'CoilID'])
v22_pos = set(test_v5.loc[test_pred==1, 'CoilID'])
shared = v4_pos & v22_pos
print(f"\nV4 vs V22 overlap: shared={len(shared)}, V4-only={len(v4_pos-v22_pos)}, V22-only={len(v22_pos-v4_pos)}, Jaccard={len(shared)/len(v4_pos|v22_pos):.3f}")


# Persist
sub = pd.DataFrame({"CoilID": test_v5["CoilID"].values, "Y": test_pred})
sub.to_csv(V22 / "expected_submission.csv", index=False)
pd.DataFrame({"oof_lgb": oof_lgb, "oof_xgb": oof_xgb, "oof_cat": oof_cat, "oof_meta": p_oof, "Y": y}).to_parquet(V22 / "oof_v22.parquet")

with open(V22 / "chosen_threshold_v22.json", "w") as f:
    json.dump({
        "architecture": "V4-stack + AutoGluon CatBoost_r167 swap (only CatBoost hyperparams changed)",
        "meta_oof_auc": meta_auc,
        "v5_baseline_auc": 0.8886,
        "delta_vs_v5": float(meta_auc - 0.8886),
        "fold_aucs": {k: [float(x) for x in v] for k, v in fold_aucs.items()},
        "base_aucs": {"lgb": lgb_mean, "xgb": xgb_mean, "cat": cat_mean},
        "chosen_threshold": float(best_T),
        "chosen_score_oof": float(best_S),
        "recall_at_T": float(best_R), "precision_at_T": float(best_P),
        "n_pos_test": int(test_pred.sum()),
        "bootstrap_ci_oof": [float(ci_lo), float(ci_hi)],
        "lb_estimate_corrected": float(cal_lb),
        "v4_actual_lb": 56.98113,
        "expected_calibration_pattern": "pure-tree positive delta (+2.7 to +3.2)",
    }, f, indent=2)

with open(V22 / "approach.md", "w") as f:
    f.write(f"# V22 — V4 structure + AutoGluon's CatBoost_r167\n\nSingle surgical change: CatBoost hyperparams swapped to AG-discovered config (depth=6, lr=0.069, l2=2.15, max_ctr_complexity=4).\nLGB + XGB unchanged.\nLR meta + Platt + gate + score-aware T (V4 baseline preserved).\n\nMeta OOF AUC: {meta_auc:.4f} (V5: 0.8886, delta {meta_auc-0.8886:+.4f})\nOOF (R+P)/2: {best_S:.2f}\nCalibrated LB est: {cal_lb:.2f}\n")
import nbformat as nbf
nb = nbf.v4.new_notebook()
nb["cells"] = [nbf.v4.new_markdown_cell(f"# V22 OOF {best_S:.2f}")]
with open(V22 / "solution.ipynb", "w") as f: nbf.write(nb, f)
with zipfile.ZipFile(V22 / "submission_v22.zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.write(V22 / "expected_submission.csv", "expected_submission.csv")
    z.write(V22 / "approach.md", "approach.md")
    z.write(V22 / "solution.ipynb", "solution.ipynb")

print("\n" + "=" * 60)
print("V22 FINAL")
print("=" * 60)
print(f"  Meta OOF AUC:        {meta_auc:.4f}  (V5: 0.8886, delta {meta_auc-0.8886:+.4f})")
print(f"  CatBoost AUC:        {cat_mean:.4f}  (V5 default: ~0.876)")
print(f"  OOF (R+P)/2:         {best_S:.2f}")
print(f"  Bootstrap CI:        [{ci_lo:.2f}, {ci_hi:.2f}]")
print(f"  Calibrated LB est:   {cal_lb:.2f}")
print(f"  V4 banked actual:    56.98")
print(f"  Test n_pos:          {test_pred.sum()}")
print(f"  V4-vs-V22 Jaccard:   {len(shared)/len(v4_pos|v22_pos):.3f}  (>0.85 = safe near-V4)")
print("=" * 60)
