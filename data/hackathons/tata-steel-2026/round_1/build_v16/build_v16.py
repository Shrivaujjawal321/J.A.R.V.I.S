"""
V16 — Two genuinely untried angles.

(1) CatBoost native categorical handling for X11 + X39 (grade codes).
    Previous builds passed these as NUMERIC. CatBoost's ordered boosting with
    cat_features uses target-statistic-based splits — different decision
    surfaces than numeric splitting. Known to lift AUC +0.02-0.04 on
    grade-coded data.

(2) Adversarial validation reweighting.
    Train an AV classifier to predict "is this row train or test?". Use the
    predicted "test-like" probability as a sample weight for the main
    classifier. Forces the main model to focus on training rows that match
    the test distribution.

No blending (V10 lesson). Single CatBoost model with these two techniques.
"""

from __future__ import annotations

import json
import warnings
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from catboost import CatBoostClassifier

warnings.filterwarnings("ignore")

ROOT = Path("/home/ujjwal/Documents/J.A.R.V.I.S.")
V5 = ROOT / "data/hackathons/tata-steel-2026/round_1/build_v5"
V16 = ROOT / "data/hackathons/tata-steel-2026/round_1/build_v16"
V16.mkdir(parents=True, exist_ok=True)

SEED = 42
N_FOLDS = 5
CAL_DELTA = 2.67
X42_DEFECT_CEIL = 0.025067
X39_CLEAN_FLOOR = 169.0
CAT_FEATURES_NAMES = ["X11", "X39"]


def hard_gate(df):
    return ((df["X42"] > X42_DEFECT_CEIL) | (df["X39"] >= X39_CLEAN_FLOOR)).values


print("Loading V5 features...")
train_v5 = pd.read_parquet(V5 / "train_v5.parquet").reset_index(drop=True)
test_v5 = pd.read_parquet(V5 / "test_v5.parquet").reset_index(drop=True)
with open(V5 / "feature_list_v5.json") as f:
    v5_features = json.load(f)["features"]

y = train_v5["Y"].values.astype(int)
n_train, n_test = len(train_v5), len(test_v5)


# ─── Phase A: Adversarial validation ─────────────────────────────────────────
print("\n[Phase A] Adversarial validation: train vs test classifier")

X_train = train_v5[v5_features].values
X_test = test_v5[v5_features].values
X_all = np.vstack([X_train, X_test])
y_av = np.concatenate([np.zeros(n_train), np.ones(n_test)])  # 0=train, 1=test

# 5-fold AV
av_oof = np.zeros(len(X_all))
av_skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
for tr, va in av_skf.split(X_all, y_av):
    m = CatBoostClassifier(
        iterations=200, learning_rate=0.05, depth=6,
        l2_leaf_reg=3.0, random_seed=SEED, verbose=False,
    )
    m.fit(X_all[tr], y_av[tr])
    av_oof[va] = m.predict_proba(X_all[va])[:, 1]

av_auc = roc_auc_score(y_av, av_oof)
print(f"  AV AUC: {av_auc:.4f}  (0.50 = no shift, >0.70 = significant shift)")

# Train portion's AV proba = "how test-like is this train row"
train_av_proba = av_oof[:n_train]
print(f"  Train AV proba range: [{train_av_proba.min():.3f}, {train_av_proba.max():.3f}]")

# Sample weight = av_proba (more weight to test-like train rows)
# Clip to avoid extreme weights
sample_weight = np.clip(train_av_proba, 0.05, 0.95)
sample_weight = sample_weight / sample_weight.mean()  # normalize
print(f"  Sample weight stats: mean={sample_weight.mean():.3f}, std={sample_weight.std():.3f}, max={sample_weight.max():.3f}")


# ─── Phase B: CatBoost with cat_features + sample_weight ─────────────────────
print("\n[Phase B] CatBoost with native categorical X11, X39 + AV-weighted")

# We need a DataFrame for cat_features by name. Use train_v5 directly + V5 engineered.
# Also encode X11 and X39 as integers (they're already integer-valued)
# Ensure X11 and X39 are in feature set
EXTRA_CAT = [c for c in CAT_FEATURES_NAMES if c not in v5_features]
v16_features = v5_features + EXTRA_CAT
print(f"  Adding categorical features to set: {EXTRA_CAT}")
print(f"  V16 feature count: {len(v16_features)}")

def prep_df(df):
    out = df[v16_features].copy()
    for c in CAT_FEATURES_NAMES:
        if c in out.columns:
            out[c] = out[c].fillna(-1).astype(int)
    return out

train_df = prep_df(train_v5)
test_df = prep_df(test_v5)

# Get category indices (positions in v16_features list)
cat_idx = [v16_features.index(c) for c in CAT_FEATURES_NAMES if c in v16_features]
print(f"  Categorical feature indices: {cat_idx} (names: {[v16_features[i] for i in cat_idx]})")

skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
oof = np.zeros(n_train)
test_pred = np.zeros(n_test)
fold_aucs = []

for fold_i, (tr, va) in enumerate(skf.split(np.zeros(n_train), y)):
    m = CatBoostClassifier(
        iterations=400, learning_rate=0.03, depth=6,
        l2_leaf_reg=3.0, auto_class_weights="Balanced",
        cat_features=cat_idx,
        random_seed=SEED, verbose=False,
        early_stopping_rounds=30,
    )
    m.fit(
        train_df.iloc[tr], y[tr],
        eval_set=(train_df.iloc[va], y[va]),
        sample_weight=sample_weight[tr],
    )
    oof[va] = m.predict_proba(train_df.iloc[va])[:, 1]
    test_pred += m.predict_proba(test_df)[:, 1] / N_FOLDS
    fold_aucs.append(roc_auc_score(y[va], oof[va]))
    print(f"  Fold {fold_i+1}: AUC={fold_aucs[-1]:.4f}")

oof_auc = float(roc_auc_score(y, oof))
print(f"\n  V16 CatBoost-cat+AV OOF AUC: {oof_auc:.4f}  (V5 baseline: 0.8886)")


# ─── Phase C: Gate + threshold ───────────────────────────────────────────────
print("\n[Phase C] Apply gate + threshold sweep")
gate_oof = hard_gate(train_v5); gate_test = hard_gate(test_v5)
oof_g = oof.copy(); oof_g[gate_oof] = 0
test_g = test_pred.copy(); test_g[gate_test] = 0

uniq = np.sort(np.unique(np.concatenate([oof_g, [0.0, 1.0]])))
cuts = np.r_[uniq[0]-1e-6, 0.5*(uniq[:-1]+uniq[1:]), uniq[-1]+1e-6]
best_T, best_S, best_R, best_P, best_n = 0, 0, 0, 0, 0
for t in cuts:
    pred = (oof_g >= t).astype(int)
    tp = ((pred==1)&(y==1)).sum(); fp = ((pred==1)&(y==0)).sum(); fn = ((pred==0)&(y==1)).sum()
    R = tp/(tp+fn) if (tp+fn) else 0; P = tp/(tp+fp) if (tp+fp) else 0
    s = (R+P)/2*100
    if s > best_S: best_S, best_T, best_R, best_P, best_n = s, t, R, P, pred.sum()

test_pred_y = (test_g >= best_T).astype(int)
print(f"  Best T={best_T:.5f}  OOF={best_S:.3f}  R={best_R:.3f}  P={best_P:.3f}  n_oof={best_n}  n_test={test_pred_y.sum()}")

# Bootstrap
rng = np.random.default_rng(SEED)
boot = np.empty(2000)
for i in range(2000):
    idx = rng.integers(0, n_train, n_train)
    pred = (oof_g[idx] >= best_T).astype(int)
    yb = y[idx]
    tp = ((pred==1)&(yb==1)).sum(); fp = ((pred==1)&(yb==0)).sum(); fn = ((pred==0)&(yb==1)).sum()
    R = tp/(tp+fn) if (tp+fn) else 0; P = tp/(tp+fp) if (tp+fp) else 0
    boot[i] = (R+P)/2*100
ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
cal_lb = best_S + CAL_DELTA
print(f"  Bootstrap CI OOF: [{ci_lo:.2f}, {ci_hi:.2f}]")
print(f"  Calibrated LB est: {cal_lb:.2f}")


# Persist
sub = pd.DataFrame({"CoilID": test_v5["CoilID"].values, "Y": test_pred_y})
sub.to_csv(V16 / "expected_submission.csv", index=False)
pd.DataFrame({"oof_v16": oof, "Y": y}).to_parquet(V16 / "oof_v16.parquet")
pd.DataFrame({"test_v16": test_pred}).to_parquet(V16 / "test_v16.parquet")

with open(V16 / "chosen_threshold_v16.json", "w") as f:
    json.dump({
        "av_auc": float(av_auc),
        "oof_auc": oof_auc, "v5_baseline_auc": 0.8886,
        "delta_vs_v5": float(oof_auc - 0.8886),
        "fold_aucs": [float(a) for a in fold_aucs],
        "chosen_threshold": float(best_T),
        "chosen_score_oof": float(best_S),
        "recall_at_T": float(best_R), "precision_at_T": float(best_P),
        "n_pos_test": int(test_pred_y.sum()),
        "bootstrap_ci_oof": [float(ci_lo), float(ci_hi)],
        "lb_estimate_corrected": float(cal_lb),
        "cat_features": CAT_FEATURES_NAMES,
        "sample_weight_mean": float(sample_weight.mean()),
        "sample_weight_max": float(sample_weight.max()),
    }, f, indent=2)

with open(V16 / "approach.md", "w") as f:
    f.write(f"# V16 — CatBoost native categorical + AV reweighting\n\nAV AUC: {av_auc:.4f}\nOOF AUC: {oof_auc:.4f} (V5 baseline 0.8886, delta {oof_auc-0.8886:+.4f})\nOOF (R+P)/2: {best_S:.2f}\nCalibrated LB: {cal_lb:.2f}\n")
import nbformat as nbf
nb = nbf.v4.new_notebook()
nb["cells"] = [nbf.v4.new_markdown_cell(f"# V16 OOF {best_S:.2f}")]
with open(V16 / "solution.ipynb", "w") as f: nbf.write(nb, f)
with zipfile.ZipFile(V16 / "submission_v16.zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.write(V16 / "expected_submission.csv", "expected_submission.csv")
    z.write(V16 / "approach.md", "approach.md")
    z.write(V16 / "solution.ipynb", "solution.ipynb")

print("\n" + "=" * 60)
print("V16 FINAL")
print("=" * 60)
print(f"  AV AUC (train vs test):  {av_auc:.4f}")
print(f"  V16 OOF AUC:             {oof_auc:.4f}  (V5: 0.8886, delta {oof_auc-0.8886:+.4f})")
print(f"  OOF (R+P)/2:             {best_S:.2f}")
print(f"  Calibrated LB:           {cal_lb:.2f}")
print(f"  Bootstrap CI cal:        [{ci_lo+CAL_DELTA:.2f}, {ci_hi+CAL_DELTA:.2f}]")
print(f"  V4 actual:               56.98")
print(f"  Test n_pos:              {test_pred_y.sum()}")
print(f"  Hits 70/65/60?           {'Y' if cal_lb>=70 else 'N'}/{'Y' if cal_lb>=65 else 'N'}/{'Y' if cal_lb>=60 else 'N'}")
print("=" * 60)
