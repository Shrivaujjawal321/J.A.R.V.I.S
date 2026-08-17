"""
V11 — V9 stacking + within-X39-grade z-scores for chemistry columns (X48, X49, X46, X41, X42).

Cycle 3 breakthrough (forensic stealth-defect analysis):
  Within X39=162 (the highest-defect grade), X48 has t-stat -4.97 between defects and non-defects.
  Globally X48 is weak; per-grade it's the strongest discriminator.

V11 adds per-X39 z-scores for: X48, X49, X46, X41, X42, X44.
Same hard gate + LR meta + Platt + score-aware threshold + V10 blend with V5.
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

warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path("/home/ujjwal/Documents/J.A.R.V.I.S.")
V5 = ROOT / "data/hackathons/tata-steel-2026/round_1/build_v5"
V11 = ROOT / "data/hackathons/tata-steel-2026/round_1/build_v11"
V11.mkdir(parents=True, exist_ok=True)

SEED = 42
N_FOLDS = 5
CAL_DELTA = 2.67
X42_DEFECT_CEIL = 0.025067
X39_CLEAN_FLOOR = 169.0
WITHIN_GRADE_COLS = ["X41", "X42", "X43", "X44", "X46", "X48", "X49"]


def hard_gate(df):
    return ((df["X42"] > X42_DEFECT_CEIL) | (df["X39"] >= X39_CLEAN_FLOOR)).values


def compute_within_grade_z(df, ref_df, cols):
    """For each row in df, compute z-score of cols using reference statistics per X39 grade in ref_df."""
    out = pd.DataFrame(index=df.index)
    ref_stats = ref_df.groupby("X39")[cols].agg(["mean", "std"])
    # Global fallback for unknown grades
    global_stats = {c: (ref_df[c].mean(), ref_df[c].std()) for c in cols}

    for col in cols:
        z = np.zeros(len(df))
        for i, (_, row) in enumerate(df.iterrows()):
            g = row["X39"]
            if g in ref_stats.index:
                mu = ref_stats.loc[g, (col, "mean")]
                sd = ref_stats.loc[g, (col, "std")]
                if pd.isna(sd) or sd == 0:
                    mu, sd = global_stats[col]
                    if sd == 0:
                        z[i] = 0
                        continue
                z[i] = (row[col] - mu) / sd
            else:
                mu, sd = global_stats[col]
                z[i] = (row[col] - mu) / sd if sd else 0
        out[f"v11_z_{col}"] = z
    return out


# ─── Load + add V11 features ─────────────────────────────────────────────────
print("Loading data...")
train_v5 = pd.read_parquet(V5 / "train_v5.parquet").reset_index(drop=True)
test_v5 = pd.read_parquet(V5 / "test_v5.parquet").reset_index(drop=True)
with open(V5 / "feature_list_v5.json") as f:
    v5_features = json.load(f)["features"]

y = train_v5["Y"].values.astype(int)
n_train, n_test = len(train_v5), len(test_v5)
print(f"  train: {n_train}  test: {n_test}  defects: {y.sum()} ({y.mean()*100:.2f}%)")


# Add chemistry derivatives (same as V9)
def add_chem(df):
    df = df.copy()
    EPS = 1e-6
    df["v11_X42_is_zero"] = (df["X42"] < 1e-5).astype(int)
    df["v11_X42_in_danger"] = ((df["X42"] >= 0) & (df["X42"] <= 0.025067)).astype(int)
    df["v11_log_X42"] = np.log(df["X42"] + EPS)
    df["v11_log_X46"] = np.log(df["X46"] + EPS)
    df["v11_log_X48"] = np.log(df["X48"] + EPS)
    df["v11_log_X49"] = np.log(df["X49"] + EPS)
    df["v11_X43_over_X41"] = df["X43"] / (df["X41"] + EPS)
    df["v11_X41_over_X42"] = df["X41"] / (df["X42"] + EPS)
    df["v11_X48_x_X49"] = df["X48"] * df["X49"]
    df["v11_X41_x_X48"] = df["X41"] * df["X48"]
    df["v11_X39_in_hot"] = df["X39"].between(158, 162).astype(int)
    df["v11_X39_in_v_hot"] = df["X39"].between(158, 160).astype(int)
    return df


train_v11 = add_chem(train_v5)
test_v11 = add_chem(test_v5)

# Pre-compute test within-grade z-scores using ALL train (no test leakage)
print("\nComputing test within-grade z-scores from all-train stats...")
test_z = compute_within_grade_z(test_v11, train_v11, WITHIN_GRADE_COLS)
for c in test_z.columns:
    test_v11[c] = test_z[c].values
# Initialize train z-cols as NaN; filled per fold
for c in WITHIN_GRADE_COLS:
    train_v11[f"v11_z_{c}"] = np.nan


V11_NEW = [
    "v11_X42_is_zero", "v11_X42_in_danger",
    "v11_log_X42", "v11_log_X46", "v11_log_X48", "v11_log_X49",
    "v11_X43_over_X41", "v11_X41_over_X42",
    "v11_X48_x_X49", "v11_X41_x_X48",
    "v11_X39_in_hot", "v11_X39_in_v_hot",
]
RAW_TO_ADD = [c for c in ["X42", "X46"] if c not in v5_features]
V11_Z = [f"v11_z_{c}" for c in WITHIN_GRADE_COLS]

v11_features = v5_features + RAW_TO_ADD + V11_NEW + V11_Z
print(f"  features: V5 {len(v5_features)} + raw {len(RAW_TO_ADD)} + V11 new {len(V11_NEW)} + Z {len(V11_Z)} = {len(v11_features)}")


# ─── Phase B: 5-fold stacking with CV-safe per-fold z-scores ─────────────────
print("\n[Phase B] 5-fold stacking with CV-safe within-grade z-scores")

skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
oof_lgb = np.zeros(n_train)
oof_xgb = np.zeros(n_train)
oof_cat = np.zeros(n_train)
test_lgb = np.zeros(n_test)
test_xgb = np.zeros(n_test)
test_cat = np.zeros(n_test)
fold_aucs = {"lgb": [], "xgb": [], "cat": []}

for fold_i, (tr_idx, val_idx) in enumerate(skf.split(np.zeros(n_train), y)):
    print(f"  Fold {fold_i+1}/{N_FOLDS}: {y[tr_idx].sum()} pos train | {y[val_idx].sum()} pos val")

    # Per-fold within-grade z-scores using ONLY fold train
    fold_train_df = train_v11.iloc[tr_idx]
    z_tr = compute_within_grade_z(train_v11.iloc[tr_idx], fold_train_df, WITHIN_GRADE_COLS)
    z_va = compute_within_grade_z(train_v11.iloc[val_idx], fold_train_df, WITHIN_GRADE_COLS)
    for c in WITHIN_GRADE_COLS:
        train_v11.loc[train_v11.index[tr_idx], f"v11_z_{c}"] = z_tr[f"v11_z_{c}"].values
        train_v11.loc[train_v11.index[val_idx], f"v11_z_{c}"] = z_va[f"v11_z_{c}"].values

    Xtr = train_v11.iloc[tr_idx][v11_features].values
    Xva = train_v11.iloc[val_idx][v11_features].values
    Xte = test_v11[v11_features].values
    ytr = y[tr_idx]
    yva = y[val_idx]

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

    print(f"    LGB={fold_aucs['lgb'][-1]:.4f}  XGB={fold_aucs['xgb'][-1]:.4f}  CAT={fold_aucs['cat'][-1]:.4f}")

print(f"\nBase mean AUCs: LGB={np.mean(fold_aucs['lgb']):.4f}  XGB={np.mean(fold_aucs['xgb']):.4f}  CAT={np.mean(fold_aucs['cat']):.4f}")


# ─── Phase C: meta + gate + sweep ────────────────────────────────────────────
print("\n[Phase C] Meta + gate + threshold sweep")
X_meta_oof = np.column_stack([oof_lgb, oof_xgb, oof_cat])
X_meta_test = np.column_stack([test_lgb, test_xgb, test_cat])
meta = LogisticRegression(C=1.0, max_iter=1000)
meta_cal = CalibratedClassifierCV(meta, method="sigmoid", cv=5)
meta_cal.fit(X_meta_oof, y)
p_oof = meta_cal.predict_proba(X_meta_oof)[:, 1]
p_test = meta_cal.predict_proba(X_meta_test)[:, 1]
print(f"  Meta OOF AUC: {roc_auc_score(y, p_oof):.4f}")

gate_oof = hard_gate(train_v11)
gate_test = hard_gate(test_v11)
p_oof_g = p_oof.copy(); p_oof_g[gate_oof] = 0
p_test_g = p_test.copy(); p_test_g[gate_test] = 0

uniq = np.sort(np.unique(np.concatenate([p_oof_g, [0.0, 1.0]])))
cuts = np.r_[uniq[0]-1e-6, 0.5*(uniq[:-1]+uniq[1:]), uniq[-1]+1e-6]
best_T, best_s, best_R, best_P, best_n = 0, 0, 0, 0, 0
for t in cuts:
    pred = (p_oof_g >= t).astype(int)
    tp = ((pred==1)&(y==1)).sum(); fp = ((pred==1)&(y==0)).sum(); fn = ((pred==0)&(y==1)).sum()
    R = tp/(tp+fn) if (tp+fn) else 0; P = tp/(tp+fp) if (tp+fp) else 0
    s = (R+P)/2*100
    if s > best_s: best_s, best_T, best_R, best_P, best_n = s, t, R, P, pred.sum()
print(f"  V11 standalone: T={best_T:.5f}  Score={best_s:.4f}  R={best_R:.3f}  P={best_P:.3f}  n_oof={best_n}")
print(f"  Calibrated LB est: {best_s + CAL_DELTA:.2f}")

# Test predictions
test_pred = (p_test_g >= best_T).astype(int)
print(f"  Test n_pos: {test_pred.sum()}/{n_test}")


# ─── Phase D: blend with V5+V8+V9 (best of V10) ──────────────────────────────
print("\n[Phase D] V11+V5 / V11+V5+V9 blend search")
oof_v5 = pd.read_parquet(V5 / "oof_v5.parquet")["oof_meta"].values
test_v5_meta = pd.read_parquet(V5 / "test_meta_v5.parquet")["test_meta"].values

# V9 (post-gate)
v9_dir = ROOT / "data/hackathons/tata-steel-2026/round_1/build_v9"
oof_v9 = pd.read_parquet(v9_dir / "oof_v9.parquet")["oof_meta_post_gate"].values
test_v9 = pd.read_parquet(v9_dir / "test_meta_v9.parquet")["test_meta_post_gate"].values

best_blend = None
for name, oof_b, test_b in [
    ("V11 alone", p_oof_g, p_test_g),
    ("V11+V5 mean", (p_oof_g + oof_v5)/2, (p_test_g + test_v5_meta)/2),
    ("V11+V5+V9 mean", (p_oof_g + oof_v5 + oof_v9)/3, (p_test_g + test_v5_meta + test_v9)/3),
    ("V11+V9 mean", (p_oof_g + oof_v9)/2, (p_test_g + test_v9)/2),
    ("V11+V5 60:40", 0.6*p_oof_g + 0.4*oof_v5, 0.6*p_test_g + 0.4*test_v5_meta),
    ("V11+V5+V9 (50:25:25)", 0.5*p_oof_g + 0.25*oof_v5 + 0.25*oof_v9, 0.5*p_test_g + 0.25*test_v5_meta + 0.25*test_v9),
]:
    uniq_b = np.sort(np.unique(np.concatenate([oof_b, [0,1]])))
    cuts_b = np.r_[uniq_b[0]-1e-6, 0.5*(uniq_b[:-1]+uniq_b[1:]), uniq_b[-1]+1e-6]
    bT, bS, bR, bP, bN = 0, 0, 0, 0, 0
    for t in cuts_b:
        pred = (oof_b >= t).astype(int)
        tp = ((pred==1)&(y==1)).sum(); fp = ((pred==1)&(y==0)).sum(); fn = ((pred==0)&(y==1)).sum()
        R = tp/(tp+fn) if (tp+fn) else 0; P = tp/(tp+fp) if (tp+fp) else 0
        s = (R+P)/2*100
        if s > bS: bS, bT, bR, bP, bN = s, t, R, P, pred.sum()
    auc = roc_auc_score(y, oof_b)
    test_pred_b = (test_b >= bT).astype(int)
    print(f"  {name:<28s}  AUC={auc:.4f}  OOF={bS:.3f}  R={bR:.3f}  P={bP:.3f}  oof_n={bN}  test_n={test_pred_b.sum()}")
    if best_blend is None or bS > best_blend[2]:
        best_blend = (name, bT, bS, oof_b, test_b, test_pred_b, auc, bR, bP)

bname, bT, bS, oof_best, test_best, test_pred_best, b_auc, bR, bP = best_blend
print(f"\nBest blend: {bname}")
print(f"  OOF {bS:.2f}, AUC {b_auc:.4f}, calibrated LB est {bS + CAL_DELTA:.2f}")

# Bootstrap CI
rng = np.random.default_rng(SEED)
boot = np.empty(2000)
for i in range(2000):
    idx = rng.integers(0, n_train, n_train)
    pred = (oof_best[idx] >= bT).astype(int)
    yb = y[idx]
    tp = ((pred==1)&(yb==1)).sum(); fp = ((pred==1)&(yb==0)).sum(); fn = ((pred==0)&(yb==1)).sum()
    R = tp/(tp+fn) if (tp+fn) else 0; P = tp/(tp+fp) if (tp+fp) else 0
    boot[i] = (R+P)/2*100
ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
print(f"  Bootstrap 95% CI on OOF: [{ci_lo:.2f}, {ci_hi:.2f}]")
print(f"  Calibrated CI: [{ci_lo + CAL_DELTA:.2f}, {ci_hi + CAL_DELTA:.2f}]")


# ─── Persist ─────────────────────────────────────────────────────────────────
sub = pd.DataFrame({"CoilID": test_v11["CoilID"].values, "Y": test_pred_best})
sub.to_csv(V11 / "expected_submission.csv", index=False)

with open(V11 / "chosen_threshold_v11.json", "w") as f:
    json.dump({
        "best_variant": bname,
        "chosen_threshold": float(bT),
        "chosen_score_oof": float(bS),
        "recall_at_T": float(bR), "precision_at_T": float(bP),
        "n_pos_test": int(test_pred_best.sum()),
        "oof_auc": float(b_auc),
        "lb_estimate_corrected": float(bS + CAL_DELTA),
        "bootstrap_ci_oof": [float(ci_lo), float(ci_hi)],
        "bootstrap_ci_calibrated": [float(ci_lo + CAL_DELTA), float(ci_hi + CAL_DELTA)],
        "v11_standalone_score": float(best_s),
        "v4_actual_lb": 56.98113,
    }, f, indent=2)

with open(V11 / "approach.md", "w") as f:
    f.write(f"# V11 — Within-grade chemistry z-scores\n\nBlend: {bname}\nOOF AUC: {b_auc:.4f}\nOOF score: {bS:.2f}\nCalibrated LB est: {bS+CAL_DELTA:.2f}\nCI: [{ci_lo+CAL_DELTA:.2f}, {ci_hi+CAL_DELTA:.2f}]\n")
import nbformat as nbf
nb = nbf.v4.new_notebook()
nb["cells"] = [nbf.v4.new_markdown_cell(f"# V11 {bname}\nOOF {bS:.2f}, AUC {b_auc:.4f}")]
with open(V11 / "solution.ipynb", "w") as f:
    nbf.write(nb, f)
with zipfile.ZipFile(V11 / "submission_v11.zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.write(V11 / "expected_submission.csv", "expected_submission.csv")
    z.write(V11 / "approach.md", "approach.md")
    z.write(V11 / "solution.ipynb", "solution.ipynb")

print("\n" + "=" * 60)
print("V11 FINAL SUMMARY")
print("=" * 60)
print(f"  Best variant:                    {bname}")
print(f"  OOF (R+P)/2 score:               {bS:.2f}")
print(f"  Meta OOF AUC:                    {b_auc:.4f}")
print(f"  Bootstrap 95% CI OOF:            [{ci_lo:.2f}, {ci_hi:.2f}]")
print(f"  V4-calibrated LB estimate:       {bS + CAL_DELTA:.2f}")
print(f"  Calibrated CI:                   [{ci_lo + CAL_DELTA:.2f}, {ci_hi + CAL_DELTA:.2f}]")
print(f"  V4 actual LB (banked):           56.98")
print(f"  Delta:                           {bS + CAL_DELTA - 56.98113:+.2f}")
print(f"  Hits 90/80/70?                   {'YES' if bS+CAL_DELTA>=90 else 'NO'}/{'YES' if bS+CAL_DELTA>=80 else 'NO'}/{'YES' if bS+CAL_DELTA>=70 else 'NO'}")
print("=" * 60)
