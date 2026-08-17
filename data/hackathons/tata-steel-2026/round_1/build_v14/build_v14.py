"""
V14 — Defect-taxonomy-driven feature engineering on V5 base.

Cycle 5 (systematic): research-agent + Latham thesis + ground-truth EDA validated
high-signal features. V14 adds 12 new features targeting the 8 defect types:

  - v14_temp_vs_lower_limit: X14 - X34 (Width Pull / Coiler Snatch). AUC 0.754
  - v14_RM_err_abs: |X13|. AUC 0.832 (X13 known signal-rich)
  - v14_FM_err_abs: |X41|. Inverse AUC 0.73
  - v14_X48_direct: X48 raw.
  - v14_cold_strip: (X14 < q25)
  - v14_high_Si: (X43 > 0.20)
  - v14_campaign_wear: X35 / max. Inverse AUC 0.78
  - v14_MnS_ratio: X45 / X46. AUC 0.662
  - v14_hot_shortness: X46 * X42. Inverse AUC 0.72
  - v14_cold_bar: low X19 + low X47
  - v14_total_offsets: |X49|. Inverse AUC 0.68
  - v14_coiler_cold: (X17 < q25)
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
V14 = ROOT / "data/hackathons/tata-steel-2026/round_1/build_v14"
V14.mkdir(parents=True, exist_ok=True)

SEED = 42
N_FOLDS = 5
CAL_DELTA = 2.67  # from V4 calibration, single-model
X42_DEFECT_CEIL = 0.025067
X39_CLEAN_FLOOR = 169.0


def hard_gate(df):
    return ((df["X42"] > X42_DEFECT_CEIL) | (df["X39"] >= X39_CLEAN_FLOOR)).values


def add_v14(df):
    df = df.copy()
    EPS = 1e-6
    # Tier 1 — defect-taxonomy direct
    df["v14_temp_vs_lower_limit"] = df["X14"] - df["X34"]
    df["v14_RM_err_abs"] = df["X13"].abs()
    df["v14_FM_err_abs"] = df["X41"].abs()
    df["v14_X48_direct"] = df["X48"]
    # Tier 2
    df["v14_high_Si"] = (df["X43"] > 0.20).astype(int)
    df["v14_campaign_wear"] = df["X35"] / df["X35"].max()
    df["v14_MnS_ratio_X45_X46"] = df["X45"] / (df["X46"] + EPS)
    df["v14_MnS_ratio_X41_X46"] = df["X41"] / (df["X46"] + EPS)
    df["v14_hot_shortness"] = df["X46"] * df["X42"]
    df["v14_cold_bar"] = (
        (df["X19"] < df["X19"].quantile(0.25)).astype(int)
        + (df["X47"] < df["X47"].quantile(0.25)).astype(int)
    )
    df["v14_total_offsets"] = df["X49"].abs()
    df["v14_coiler_cold"] = (df["X17"] < df["X17"].quantile(0.25)).astype(int)
    # Width Pull composite
    fm_p75 = df["X41"].abs().quantile(0.75)
    df["v14_width_pull_score"] = (
        ((df["X14"] - df["X34"]) < 5).astype(int)
        + (df["X41"].abs() > fm_p75).astype(int)
        + df["X48"].fillna(0).clip(upper=1).astype(int)
    )
    # Grade x temperature interactions (per-grade behaviour)
    df["v14_grade_x_temp_gap"] = df["X39"] * df["v14_temp_vs_lower_limit"]
    df["v14_grade_x_RM_err"] = df["X39"] * df["v14_RM_err_abs"]
    return df


# ─── Load ────────────────────────────────────────────────────────────────────
print("Loading V5 features...")
train_v5 = pd.read_parquet(V5 / "train_v5.parquet").reset_index(drop=True)
test_v5 = pd.read_parquet(V5 / "test_v5.parquet").reset_index(drop=True)
with open(V5 / "feature_list_v5.json") as f:
    v5_features = json.load(f)["features"]

y = train_v5["Y"].values.astype(int)
n_train, n_test = len(train_v5), len(test_v5)
print(f"  train: {n_train}  test: {n_test}  defects: {y.sum()} ({y.mean()*100:.2f}%)")


# ─── Feature engineering ─────────────────────────────────────────────────────
print("\n[Phase A] V14 feature engineering")
train_v14 = add_v14(train_v5)
test_v14 = add_v14(test_v5)

V14_NEW = [
    "v14_temp_vs_lower_limit", "v14_RM_err_abs", "v14_FM_err_abs", "v14_X48_direct",
    "v14_high_Si", "v14_campaign_wear", "v14_MnS_ratio_X45_X46", "v14_MnS_ratio_X41_X46",
    "v14_hot_shortness", "v14_cold_bar", "v14_total_offsets", "v14_coiler_cold",
    "v14_width_pull_score", "v14_grade_x_temp_gap", "v14_grade_x_RM_err",
]
RAW_TO_ADD = [c for c in ["X42", "X46"] if c not in v5_features]
v14_features = v5_features + RAW_TO_ADD + V14_NEW
print(f"  V5 base {len(v5_features)} + raw {len(RAW_TO_ADD)} + V14 new {len(V14_NEW)} = {len(v14_features)} features")


# ─── Stacking ────────────────────────────────────────────────────────────────
print("\n[Phase B] 5-fold stacking (LGB+XGB+CatBoost)")
skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
oof_lgb = np.zeros(n_train); oof_xgb = np.zeros(n_train); oof_cat = np.zeros(n_train)
test_lgb = np.zeros(n_test); test_xgb = np.zeros(n_test); test_cat = np.zeros(n_test)
fold_aucs = {"lgb": [], "xgb": [], "cat": []}

for fold_i, (tr_idx, val_idx) in enumerate(skf.split(np.zeros(n_train), y)):
    Xtr = train_v14.iloc[tr_idx][v14_features].values
    Xva = train_v14.iloc[val_idx][v14_features].values
    Xte = test_v14[v14_features].values
    ytr, yva = y[tr_idx], y[val_idx]

    m_lgb = lgb.LGBMClassifier(
        n_estimators=500, learning_rate=0.03, max_depth=6, num_leaves=31,
        min_child_samples=10, reg_alpha=0.1, reg_lambda=0.1,
        random_state=SEED, verbose=-1, class_weight="balanced",
    )
    m_lgb.fit(Xtr, ytr, eval_set=[(Xva, yva)], callbacks=[lgb.early_stopping(30, verbose=False)])
    oof_lgb[val_idx] = m_lgb.predict_proba(Xva)[:, 1]
    test_lgb += m_lgb.predict_proba(Xte)[:, 1] / N_FOLDS
    fold_aucs["lgb"].append(roc_auc_score(yva, oof_lgb[val_idx]))

    m_xgb = xgb.XGBClassifier(
        n_estimators=500, learning_rate=0.03, max_depth=6,
        scale_pos_weight=(ytr == 0).sum() / max(ytr.sum(), 1),
        reg_alpha=0.1, reg_lambda=0.1,
        random_state=SEED, eval_metric="auc",
        early_stopping_rounds=30, verbosity=0,
    )
    m_xgb.fit(Xtr, ytr, eval_set=[(Xva, yva)], verbose=False)
    oof_xgb[val_idx] = m_xgb.predict_proba(Xva)[:, 1]
    test_xgb += m_xgb.predict_proba(Xte)[:, 1] / N_FOLDS
    fold_aucs["xgb"].append(roc_auc_score(yva, oof_xgb[val_idx]))

    m_cat = CatBoostClassifier(
        iterations=500, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
        auto_class_weights="Balanced",
        random_seed=SEED, verbose=False, early_stopping_rounds=30,
    )
    m_cat.fit(Xtr, ytr, eval_set=(Xva, yva))
    oof_cat[val_idx] = m_cat.predict_proba(Xva)[:, 1]
    test_cat += m_cat.predict_proba(Xte)[:, 1] / N_FOLDS
    fold_aucs["cat"].append(roc_auc_score(yva, oof_cat[val_idx]))

    print(f"  Fold {fold_i+1}: LGB={fold_aucs['lgb'][-1]:.4f}  XGB={fold_aucs['xgb'][-1]:.4f}  CAT={fold_aucs['cat'][-1]:.4f}")

lgb_mean = float(np.mean(fold_aucs["lgb"]))
xgb_mean = float(np.mean(fold_aucs["xgb"]))
cat_mean = float(np.mean(fold_aucs["cat"]))
print(f"\n  Mean AUCs: LGB={lgb_mean:.4f}  XGB={xgb_mean:.4f}  CAT={cat_mean:.4f}  (V5 baseline: LGB 0.862, XGB 0.839, CAT 0.876)")


# ─── Meta + gate ─────────────────────────────────────────────────────────────
print("\n[Phase C] Meta + Platt + gate + threshold")
X_meta_oof = np.column_stack([oof_lgb, oof_xgb, oof_cat])
X_meta_test = np.column_stack([test_lgb, test_xgb, test_cat])
meta = LogisticRegression(C=1.0, max_iter=1000)
meta_cal = CalibratedClassifierCV(meta, method="sigmoid", cv=5)
meta_cal.fit(X_meta_oof, y)
p_oof = meta_cal.predict_proba(X_meta_oof)[:, 1]
p_test = meta_cal.predict_proba(X_meta_test)[:, 1]
meta_auc = float(roc_auc_score(y, p_oof))
print(f"  V14 Meta OOF AUC: {meta_auc:.4f}  (V5 baseline: 0.8886)")

gate_oof = hard_gate(train_v14); gate_test = hard_gate(test_v14)
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
print(f"  V14 standalone: T={best_T:.5f}  OOF={best_S:.3f}  R={best_R:.3f}  P={best_P:.3f}  n_oof={best_n}  n_test={test_pred.sum()}")

# Bootstrap CI
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
cal_lb = best_S + CAL_DELTA
print(f"  Bootstrap 95% CI OOF: [{ci_lo:.2f}, {ci_hi:.2f}]")
print(f"  Calibrated LB estimate: {cal_lb:.2f}")


# Save submission
sub = pd.DataFrame({"CoilID": test_v14["CoilID"].values, "Y": test_pred})
sub.to_csv(V14 / "expected_submission.csv", index=False)

with open(V14 / "chosen_threshold_v14.json", "w") as f:
    json.dump({
        "meta_oof_auc": meta_auc, "v5_meta_auc": 0.8886, "delta_meta_auc": meta_auc - 0.8886,
        "chosen_threshold": float(best_T),
        "chosen_score_oof": float(best_S),
        "recall_at_T": float(best_R), "precision_at_T": float(best_P),
        "n_pos_test": int(test_pred.sum()),
        "bootstrap_ci_oof": [float(ci_lo), float(ci_hi)],
        "calibration_correction": CAL_DELTA,
        "lb_estimate_corrected": float(cal_lb),
        "v4_actual_lb": 56.98113,
        "base_aucs": {"lgb": lgb_mean, "xgb": xgb_mean, "cat": cat_mean},
        "v14_new_features": V14_NEW,
    }, f, indent=2)

with open(V14 / "approach.md", "w") as f:
    f.write(f"# V14 — Defect-taxonomy-driven features\n\nMeta OOF AUC: {meta_auc:.4f} (V5: 0.8886, delta {meta_auc-0.8886:+.4f})\nOOF: {best_S:.2f} | Calibrated LB: {cal_lb:.2f}\nNew features: {len(V14_NEW)}\n")
import nbformat as nbf
nb = nbf.v4.new_notebook()
nb["cells"] = [nbf.v4.new_markdown_cell(f"# V14 OOF {best_S:.2f}")]
with open(V14 / "solution.ipynb", "w") as f: nbf.write(nb, f)
with zipfile.ZipFile(V14 / "submission_v14.zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.write(V14 / "expected_submission.csv", "expected_submission.csv")
    z.write(V14 / "approach.md", "approach.md")
    z.write(V14 / "solution.ipynb", "solution.ipynb")

print("\n" + "=" * 60)
print("V14 FINAL")
print("=" * 60)
print(f"  V14 Meta OOF AUC:     {meta_auc:.4f}  (V5 0.8886, delta {meta_auc-0.8886:+.4f})")
print(f"  OOF (R+P)/2:          {best_S:.2f}")
print(f"  Calibrated LB est:    {cal_lb:.2f}")
print(f"  Bootstrap CI cal:     [{ci_lo+CAL_DELTA:.2f}, {ci_hi+CAL_DELTA:.2f}]")
print(f"  V4 actual:            56.98")
print(f"  Hits 70/65/60?        {'Y' if cal_lb>=70 else 'N'}/{'Y' if cal_lb>=65 else 'N'}/{'Y' if cal_lb>=60 else 'N'}")
print("=" * 60)
