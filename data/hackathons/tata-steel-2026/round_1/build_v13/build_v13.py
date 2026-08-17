"""
V13 — Single CatBoost, V12-tuned, gate-at-inference, precision-focused threshold.

V10 lesson: blending corrupted threshold (LB 47 vs predicted 58). Calibration
delta +2.67 from V4 is NOT universal. Bootstrap CI doesn't bracket actual LB
when model architectures differ.

V13 strategy:
  1. Single CatBoost with V12's tuned hyperparams (AUC 0.879)
  2. 5-fold OOF (seed=42)
  3. Hard gate at inference (X42>0.025 OR X39>=169 -> predict 0)
  4. Generate MULTIPLE submission CSVs at different threshold strategies:
     - (R+P)/2 sweep (matches V4 behaviour, ~150 positives)
     - Top-30 prediction (precision-focused)
     - Top-50 prediction (balanced)
     - Top-80 prediction (V4 mid-band)
  5. Bootstrap each, report ALL options for Boss to choose

NO blending. NO multi-seed averaging.
"""

from __future__ import annotations

import json
import warnings
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from catboost import CatBoostClassifier

warnings.filterwarnings("ignore")

ROOT = Path("/home/ujjwal/Documents/J.A.R.V.I.S.")
V5 = ROOT / "data/hackathons/tata-steel-2026/round_1/build_v5"
V13 = ROOT / "data/hackathons/tata-steel-2026/round_1/build_v13"
V13.mkdir(parents=True, exist_ok=True)

SEED = 42
N_FOLDS = 5
X42_DEFECT_CEIL = 0.025067
X39_CLEAN_FLOOR = 169.0

# V12-tuned CatBoost params (AUC 0.879)
CAT_PARAMS = {
    "iterations": 300,
    "learning_rate": 0.01432169828911152,
    "depth": 4,
    "l2_leaf_reg": 7.348118405270449,
    "auto_class_weights": "Balanced",
    "random_seed": SEED,
    "verbose": False,
}


def hard_gate(df):
    return ((df["X42"] > X42_DEFECT_CEIL) | (df["X39"] >= X39_CLEAN_FLOOR)).values


print("Loading V5 features...")
train_v5 = pd.read_parquet(V5 / "train_v5.parquet").reset_index(drop=True)
test_v5 = pd.read_parquet(V5 / "test_v5.parquet").reset_index(drop=True)
with open(V5 / "feature_list_v5.json") as f:
    v5_features = json.load(f)["features"]

y = train_v5["Y"].values.astype(int)
n_train, n_test = len(train_v5), len(test_v5)
X_tr = train_v5[v5_features].values
X_te = test_v5[v5_features].values
print(f"  train: {n_train}  test: {n_test}  defects: {y.sum()} ({y.mean()*100:.2f}%)")


# ─── Phase A: Single CatBoost 5-fold OOF ─────────────────────────────────────
print("\n[Phase A] Single CatBoost 5-fold OOF (seed=42)")

skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
oof_cat = np.zeros(n_train)
test_cat = np.zeros(n_test)
fold_aucs = []

for fold_i, (tr_idx, val_idx) in enumerate(skf.split(np.zeros(n_train), y)):
    Xtr, Xva = X_tr[tr_idx], X_tr[val_idx]
    ytr, yva = y[tr_idx], y[val_idx]
    m = CatBoostClassifier(**CAT_PARAMS)
    m.fit(Xtr, ytr, eval_set=(Xva, yva), early_stopping_rounds=30)
    oof_cat[val_idx] = m.predict_proba(Xva)[:, 1]
    test_cat += m.predict_proba(X_te)[:, 1] / N_FOLDS
    fold_aucs.append(roc_auc_score(yva, oof_cat[val_idx]))
    print(f"  Fold {fold_i+1}: AUC={fold_aucs[-1]:.4f}")

oof_auc = float(roc_auc_score(y, oof_cat))
print(f"\n  Single CatBoost OOF AUC: {oof_auc:.4f}")


# ─── Phase B: Platt calibration ──────────────────────────────────────────────
print("\n[Phase B] Platt calibration via CalibratedClassifierCV")
from sklearn.linear_model import LogisticRegression
meta = LogisticRegression(C=1.0, max_iter=1000)
meta_cal = CalibratedClassifierCV(meta, method="sigmoid", cv=5)
meta_cal.fit(oof_cat.reshape(-1, 1), y)
p_oof = meta_cal.predict_proba(oof_cat.reshape(-1, 1))[:, 1]
p_test = meta_cal.predict_proba(test_cat.reshape(-1, 1))[:, 1]
cal_auc = float(roc_auc_score(y, p_oof))
print(f"  Calibrated OOF AUC: {cal_auc:.4f}")


# ─── Phase C: gate at inference ──────────────────────────────────────────────
print("\n[Phase C] Apply gate at inference + at OOF for sweep consistency")
gate_oof = hard_gate(train_v5)
gate_test = hard_gate(test_v5)
p_oof_g = p_oof.copy(); p_oof_g[gate_oof] = 0
p_test_g = p_test.copy(); p_test_g[gate_test] = 0
print(f"  Test rows gated: {gate_test.sum()} / {n_test}")


# ─── Phase D: Multiple submission strategies ─────────────────────────────────
print("\n[Phase D] Generate multiple submission strategies")


def make_sub(p_test, K):
    """Predict top K test rows positive."""
    ranked = np.argsort(-p_test)
    pred = np.zeros(len(p_test), dtype=int)
    pred[ranked[:K]] = 1
    return pred


def oof_at_K(p_oof, y, K):
    pred = make_sub(p_oof, K)
    tp = ((pred == 1) & (y == 1)).sum()
    fp = ((pred == 1) & (y == 0)).sum()
    fn = ((pred == 0) & (y == 1)).sum()
    R = tp / (tp + fn) if (tp + fn) else 0
    P = tp / (tp + fp) if (tp + fp) else 0
    return R, P, (R + P) / 2 * 100, tp, fp


# Strategy 1: classic (R+P)/2 sweep
uniq = np.sort(np.unique(np.concatenate([p_oof_g, [0.0, 1.0]])))
cuts = np.r_[uniq[0] - 1e-6, 0.5 * (uniq[:-1] + uniq[1:]), uniq[-1] + 1e-6]
sweep_T, sweep_S, sweep_R, sweep_P, sweep_n = 0, 0, 0, 0, 0
for t in cuts:
    pred = (p_oof_g >= t).astype(int)
    tp = ((pred == 1) & (y == 1)).sum()
    fp = ((pred == 1) & (y == 0)).sum()
    fn = ((pred == 0) & (y == 1)).sum()
    R = tp / (tp + fn) if (tp + fn) else 0
    P = tp / (tp + fp) if (tp + fp) else 0
    s = (R + P) / 2 * 100
    if s > sweep_S:
        sweep_S, sweep_T, sweep_R, sweep_P, sweep_n = s, t, R, P, pred.sum()
test_sweep = (p_test_g >= sweep_T).astype(int)
print(f"\n  Sweep (R+P)/2 max: T={sweep_T:.5f}  OOF score={sweep_S:.3f}  R={sweep_R:.3f}  P={sweep_P:.3f}  n_oof={sweep_n}  n_test={test_sweep.sum()}")

# Strategy 2-7: Top-K test predictions, with OOF top-K reported for context
print(f"\n  Top-K strategies:")
strategies = {}
for K_test in [20, 30, 40, 50, 60, 80, 120, 154]:
    test_pred = make_sub(p_test_g, K_test)
    # Match similar K on OOF (scale up by train/test ratio)
    K_oof = int(K_test * n_train / n_test)  # roughly same prevalence
    R, P, s, tp, fp = oof_at_K(p_oof_g, y, K_oof)
    strategies[f"Top{K_test}"] = {
        "K_test": K_test,
        "K_oof": K_oof,
        "oof_R": R, "oof_P": P, "oof_score": s,
        "test_pred": test_pred,
    }
    print(f"    K_test={K_test:3d} (K_oof={K_oof:4d}): OOF R={R:.3f}  P={P:.3f}  score={s:.2f}  n_test_pos={test_pred.sum()}")


# Strategy 8: pure gate + top-K within hot zone only
# Gate eliminates 138 rows; remaining 201 are hot zone. Top-K of those.
hot_test_mask = ~gate_test
p_test_hot_only = p_test.copy()
p_test_hot_only[gate_test] = -1  # ensure gated never get picked
for K in [20, 30, 50]:
    test_pred = make_sub(p_test_hot_only, K)
    print(f"    Hot-Top{K}: n_test_pos={test_pred.sum()}  (gate-clean hot top-K)")


# ─── Phase E: which strategy to use for final submission ─────────────────────
# Honest take: V4 banked at 56.98 with n_test=154 at R=1.0. To beat this we need
# better PRECISION at similar recall. Best chance: predict in V4's positive set
# but smarter — i.e., predict the ones V4+V13 BOTH say positive.
print("\n[Phase E] Pick recommended strategy")
print("  Strategy: classic sweep is what V4 used. V13's CV-validated max is at K~150.")
print("  But V10 disaster shows OOF threshold optimization can over-extrapolate.")
print("  V13 default = sweep result (same posture as V4 banked).")

# Default = sweep prediction
sub = pd.DataFrame({"CoilID": test_v5["CoilID"].values, "Y": test_sweep})
sub.to_csv(V13 / "expected_submission.csv", index=False)
print(f"\n  Wrote expected_submission.csv: {test_sweep.sum()}/339 positives (sweep strategy)")

# Persist all strategies
for name, info in strategies.items():
    s_sub = pd.DataFrame({"CoilID": test_v5["CoilID"].values, "Y": info["test_pred"]})
    s_sub.to_csv(V13 / f"alt_{name}.csv", index=False)


# ─── Phase F: Bootstrap CI on sweep strategy ─────────────────────────────────
print("\n[Phase F] Bootstrap CI on sweep strategy")
rng = np.random.default_rng(SEED)
boot = np.empty(2000)
for i in range(2000):
    idx = rng.integers(0, n_train, n_train)
    pred = (p_oof_g[idx] >= sweep_T).astype(int)
    yb = y[idx]
    tp = ((pred == 1) & (yb == 1)).sum()
    fp = ((pred == 1) & (yb == 0)).sum()
    fn = ((pred == 0) & (yb == 1)).sum()
    R = tp / (tp + fn) if (tp + fn) else 0
    P = tp / (tp + fp) if (tp + fp) else 0
    boot[i] = (R + P) / 2 * 100
ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
print(f"  Bootstrap 95% CI on OOF: [{ci_lo:.2f}, {ci_hi:.2f}]")

# Compare to V4 OOF/LB: V4 OOF was 54.31 -> LB 56.98 (delta +2.67). V13 OOF is 53.78 (similar) so LB likely 56-57.
print()
print("  HONEST LB prediction:")
print("  - V4: OOF 54.31 -> LB 56.98 (delta +2.67)")
print(f"  - V13: OOF {sweep_S:.2f} -> LB likely 55-58 (single-model, similar architecture to V4)")
print("  - V10 disaster (LB 47) was BLENDING induced. V13 has no blend.")


# ─── Phase G: persist + zip ──────────────────────────────────────────────────
print("\n[Phase G] Persist")
with open(V13 / "chosen_threshold_v13.json", "w") as f:
    json.dump({
        "single_model": "CatBoost (V12-tuned)",
        "chosen_threshold": float(sweep_T),
        "chosen_score_oof": float(sweep_S),
        "recall_at_T": float(sweep_R), "precision_at_T": float(sweep_P),
        "n_pos_test": int(test_sweep.sum()),
        "oof_auc": float(cal_auc),
        "raw_oof_auc": float(oof_auc),
        "fold_aucs": [float(a) for a in fold_aucs],
        "bootstrap_ci_oof": [float(ci_lo), float(ci_hi)],
        "v4_actual_lb": 56.98113,
        "v10_actual_lb": 47.0,
        "v10_predicted_lb": 58.14,
        "v10_lesson": "Blending corrupts threshold calibration. Single-model only for V13.",
        "alt_strategies": {k: {"K_test": v["K_test"], "K_oof": v["K_oof"],
                                "oof_R": v["oof_R"], "oof_P": v["oof_P"],
                                "oof_score": v["oof_score"],
                                "n_test_pos": int(v["test_pred"].sum())} for k, v in strategies.items()},
    }, f, indent=2)

approach = f"""# V13 — Single CatBoost (V12-tuned), gate-at-inference, no blending

## Why V13

V10's blend disaster (predicted LB 58.14, actual LB 47.00) proved blending corrupts threshold calibration. V13 returns to single-model architecture matching V4's banked posture.

## Architecture

- Single CatBoost with V12's Optuna-tuned hyperparams (depth=4, lr=0.014, l2=7.35, iter=300)
- 5-fold StratifiedKFold (seed=42)
- Platt sigmoid calibration on CatBoost OOF
- Hard gate at inference: X42 > 0.025067 OR X39 >= 169 -> predict 0 (Track A EDA finding)
- Score-aware (R+P)/2 threshold sweep on gated OOF
- NO blending, NO multi-seed averaging (V10 lesson)

## Results

- Single CatBoost OOF AUC: {oof_auc:.4f}
- Calibrated OOF AUC: {cal_auc:.4f}
- OOF (R+P)/2: {sweep_S:.2f}
- Bootstrap 95% CI: [{ci_lo:.2f}, {ci_hi:.2f}]
- Test n_pos at chosen T: {test_sweep.sum()}/{n_test}

## Honest LB prediction

V4 OOF 54.31 -> LB 56.98 (delta +2.67). V13 architecture mirrors V4 single-model approach. Expected V13 LB: 55-58 range. NOT 90.
"""
with open(V13 / "approach.md", "w") as f:
    f.write(approach)
import nbformat as nbf
nb = nbf.v4.new_notebook()
nb["cells"] = [nbf.v4.new_markdown_cell(approach)]
with open(V13 / "solution.ipynb", "w") as f:
    nbf.write(nb, f)
with zipfile.ZipFile(V13 / "submission_v13.zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.write(V13 / "expected_submission.csv", "expected_submission.csv")
    z.write(V13 / "approach.md", "approach.md")
    z.write(V13 / "solution.ipynb", "solution.ipynb")

print(f"\n  V13 submission ready: {V13}/submission_v13.zip")
print("\n" + "=" * 60)
print("V13 FINAL")
print("=" * 60)
print(f"  Single CatBoost OOF AUC:  {oof_auc:.4f}")
print(f"  Calibrated OOF AUC:       {cal_auc:.4f}")
print(f"  OOF (R+P)/2:              {sweep_S:.2f}")
print(f"  Bootstrap 95% CI:         [{ci_lo:.2f}, {ci_hi:.2f}]")
print(f"  Test n_pos:               {test_sweep.sum()}/{n_test}")
print(f"  V4 banked actual:         56.98")
print(f"  V10 disaster actual:      47.00 (predicted 58)")
print(f"  V13 honest LB band:       55-58 expected")
print("=" * 60)
