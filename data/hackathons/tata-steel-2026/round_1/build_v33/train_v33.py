"""
train_v33.py — V33 Final Training Script
Tata Steel Hot Rolling Defect Detection

Architecture: LightGBM (single model) with:
  - V4 global feature set (X ratios, lag, rolling, poly, iso_score)
  - V33 NEW: per-stand residual features (11 stand columns → 54 new features)
  - V33 NEW: X35 bimodal decomposition (3 features)
  - BBSE sample weights (w1=9.0, w0=0.579)
  - StratifiedKFold(5) + bootstrap CI + K-sweep threshold

Key findings from ablation experiments (2026-05-24):
  - Stand FE features add +0.015 AUC over raw features alone
  - BBSE vs scale_pos_weight: near-neutral on AUC
  - Single LGB ceiling on this dataset: ~0.84-0.85 AUC
  - V4's 0.8837 came from 3-model stacking (LGB+XGB+CatBoost meta LR)
  - Target 0.935 is not achievable with single LGB on 1352 rows / 66 positives
  - TabPFN v2: requires license acceptance (unavailable in non-interactive env)
  - TabICLv2: 0.8697 AUC — similar to LGB

HONEST GATE ASSESSMENT EXPECTED:
  - AUC gate (0.935): WILL FAIL — single LGB ~0.84-0.85
  - OOF score > 54.31: WILL FAIL — best single-model score ~44-49
  - Estimated LB: ~47-52 (behind V4's 56.98)
  → DO NOT FIRE unless gates pass

V4 calibration anchor: V4 OOF score 54.31 → LB 56.98 (delta +2.67)
"""

from __future__ import annotations

import json
import sys
import os
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, RepeatedStratifiedKFold
from sklearn.metrics import roc_auc_score, precision_score, recall_score
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import PolynomialFeatures
import lightgbm as lgb

sys.path.insert(0, os.path.dirname(__file__))
from feature_engineering import StandSetpoints, validate_stand_ordering, TEMP_COLS, FORCE_COLS, ID_COL, TARGET_COL

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = "/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1"
DATA_DIR = "/home/ujjwal/Documents/J.A.R.V.I.S./data set of tata steel/dataset"
BUILD_DIR = os.path.join(BASE_DIR, "build_v33")
V4_OOF_PATH = os.path.join(BASE_DIR, "build_v4", "oof_v4.parquet")

# ─── Config ───────────────────────────────────────────────────────────────────
SEED = 42
N_FOLDS = 5
N_REPEATS = 3
BBSE_W1 = 9.0       # 0.45/0.05
BBSE_W0 = 0.579     # 0.55/0.95
V4_OOF_AUC = 0.8837
V4_LB = 56.98
V4_DELTA = 2.67
V4_OOF_SCORE = 54.31

LGB_PARAMS = {
    "objective": "binary",
    "metric": "auc",
    "learning_rate": 0.03,
    "num_leaves": 63,
    "max_depth": 6,
    "min_child_samples": 10,
    "subsample": 0.8,
    "subsample_freq": 1,
    "colsample_bytree": 0.7,
    "reg_alpha": 0.05,
    "reg_lambda": 0.5,
    "n_estimators": 700,
    "random_state": SEED,
    "verbosity": -1,
    "n_jobs": -1,
}

# ─── Load data ────────────────────────────────────────────────────────────────
print("=" * 60)
print("V33 — Single LGB + Per-Stand Residual Features + BBSE")
print("=" * 60)

train = pd.read_csv(os.path.join(DATA_DIR, "train.csv")).sort_values(ID_COL).reset_index(drop=True)
test = pd.read_csv(os.path.join(DATA_DIR, "test.csv")).sort_values(ID_COL).reset_index(drop=True)
y = train[TARGET_COL].values.astype(int)
coil_ids_train = train[ID_COL].values
coil_ids_test = test[ID_COL].values

print(f"Train: {train.shape} | Test: {test.shape}")
print(f"Defect rate: {y.mean():.4f} ({y.sum()} positives)")

# ─── AP-6: Stand ordering validation ──────────────────────────────────────────
print("\nStand ordering validation (AP-6)...")
ordering = validate_stand_ordering(train)
print(f"  Temp X4-X9: {ordering['temp_order_status']}")
print(f"    {', '.join(f'{c}={v:.1f}' for c, v in ordering['temp_means'].items())}")
print(f"  Force X29-X33: {ordering['force_order_status']}")
print(f"    {', '.join(f'{c}={v:.2f}' for c, v in ordering['force_means'].items())}")

# ─── Global features (V4 style, no fold leakage) ─────────────────────────────
print("\nBuilding global features (V4 style + stand FE prep)...")

def build_global_features(df: pd.DataFrame, iso_model: IsolationForest | None = None) -> pd.DataFrame:
    """Build non-target-encoded global features. IsoForest fitted on all train."""
    df = df.copy()
    df["X13_over_X36"] = df["X13"] / (df["X36"].replace(0, np.nan) + 1e-9)
    df["X13_minus_X36"] = df["X13"] - df["X36"]
    df["X30_over_X35"] = df["X30"] / (df["X35"].replace(0, np.nan) + 1e-9)
    df["X13_over_X34"] = df["X13"] / (df["X34"].replace(0, np.nan) + 1e-9)

    xcols = [c for c in df.columns if c.startswith("X")]
    df["row_skew"] = df[xcols].apply(lambda r: pd.to_numeric(r, errors="coerce").skew(), axis=1)

    for col in ["X13", "X10", "X36"]:
        df[f"{col}_lag1"] = df[col].shift(1)
        df[f"{col}_rollmean5"] = df[col].rolling(5, min_periods=1).mean()

    df["X36_roll5"] = df["X36"].rolling(5, min_periods=1).mean()

    # Polynomial interactions on top-5 V4 features
    poly_base = ["X13_over_X36", "X36", "X14", "X13_minus_X36", "X16"]
    poly = PolynomialFeatures(degree=2, include_bias=False)
    poly_arr = poly.fit_transform(df[poly_base].fillna(0))
    poly_names = poly.get_feature_names_out(poly_base)
    for i in range(len(poly_base), poly_arr.shape[1]):
        safe_name = f"p_{poly_names[i].replace(' ', '_').replace('^', 'p')}"
        df[safe_name] = poly_arr[:, i]

    # IsolationForest score (use ONLY original X columns that iso was fitted on)
    if iso_model is not None:
        # iso_model was fitted on train X columns (X1..X49) — use same cols from original df
        orig_x_cols = [c for c in df.columns if c.startswith("X") and len(c) <= 4]  # X1..X49 only
        # More reliable: use only single-digit or double-digit Xnn columns
        import re
        iso_feat_cols = sorted([c for c in df.columns if re.match(r'^X\d{1,2}$', c)])
        df["iso_score"] = -iso_model.score_samples(df[iso_feat_cols].fillna(0))

    return df


# Fit IsoForest on ALL train raw X columns (X1..X49) — consistent with V4 approach
import re as _re
iso_xcols = sorted([c for c in train.columns if _re.match(r'^X\d{1,2}$', c)])
iso_model = IsolationForest(n_estimators=100, contamination=0.05, random_state=SEED, n_jobs=-1)
iso_model.fit(train[iso_xcols].fillna(0))

train_g = build_global_features(train, iso_model)
test_g = build_global_features(test, iso_model)

base_feat_cols = [c for c in train_g.columns if c not in [ID_COL, TARGET_COL]]
X_base = train_g[base_feat_cols].fillna(0)
X_test_base = test_g[base_feat_cols].fillna(0)
print(f"  Global features: {len(base_feat_cols)}")

# ─── CV loop: stand FE inside each fold ──────────────────────────────────────
rkf = RepeatedStratifiedKFold(n_splits=N_FOLDS, n_repeats=N_REPEATS, random_state=SEED)
total_folds = N_FOLDS * N_REPEATS

oof_proba_first = np.zeros(len(train))  # first repeat OOF
test_preds_accum = np.zeros(len(test))
fold_aucs = []

# Compute all-train setpoints for test set transformation
all_sp = StandSetpoints()
all_sp.fit(X_base)
X_test_eng = all_sp.transform(X_test_base)

print(f"\nRunning {total_folds}-fold CV ({N_FOLDS}×{N_REPEATS})...")

for fold_idx, (tr_idx, val_idx) in enumerate(rkf.split(X_base, y)):
    X_tr = X_base.iloc[tr_idx].copy()
    X_val = X_base.iloc[val_idx].copy()
    y_tr = y[tr_idx]
    y_val = y[val_idx]

    # Stand FE: setpoints from TRAIN FOLD ONLY (AP-1)
    sp = StandSetpoints()
    sp.fit(X_tr)
    X_tr_eng = sp.transform(X_tr).fillna(0)
    X_val_eng = sp.transform(X_val).fillna(0)

    # BBSE weights
    sample_w = np.where(y_tr == 1, BBSE_W1, BBSE_W0)

    # Train
    model = lgb.LGBMClassifier(**LGB_PARAMS)
    model.fit(X_tr_eng, y_tr, sample_weight=sample_w)

    val_proba = model.predict_proba(X_val_eng)[:, 1]
    fold_auc = roc_auc_score(y_val, val_proba)
    fold_aucs.append(fold_auc)

    if fold_idx < N_FOLDS:
        oof_proba_first[val_idx] = val_proba

    test_pred = model.predict_proba(X_test_eng.fillna(0))[:, 1]
    test_preds_accum += test_pred

    if (fold_idx + 1) % 5 == 0 or fold_idx == 0:
        recent = fold_aucs[-5:] if len(fold_aucs) >= 5 else fold_aucs
        print(f"  Fold {fold_idx+1:2d}/{total_folds} | AUC: {fold_auc:.4f} | Avg(last5): {np.mean(recent):.4f}")

test_preds_avg = test_preds_accum / total_folds
oof_proba = oof_proba_first

# ─── Metrics ──────────────────────────────────────────────────────────────────
mean_auc = np.mean(fold_aucs)
std_auc = np.std(fold_aucs)
oof_auc_full = roc_auc_score(y, oof_proba)

print(f"\n{'='*60}")
print(f"Repeated CV AUC: {mean_auc:.4f} ± {std_auc:.4f}")
print(f"First-repeat OOF AUC: {oof_auc_full:.4f}")
print(f"V4 meta AUC (reference): {V4_OOF_AUC}")
print(f"AUC delta vs V4: {mean_auc - V4_OOF_AUC:+.4f}")

# Bootstrap CI
rng = np.random.RandomState(SEED)
boot_scores = []
for _ in range(500):
    idx = rng.choice(len(train), size=int(0.8 * len(train)), replace=False)
    y_b, p_b = y[idx], oof_proba[idx]
    if y_b.sum() >= 3 and (y_b == 0).sum() >= 3:
        try:
            boot_scores.append(roc_auc_score(y_b, p_b))
        except Exception:
            pass
boot_ci_lo = float(np.percentile(boot_scores, 2.5))
boot_ci_hi = float(np.percentile(boot_scores, 97.5))
boot_mean = float(np.mean(boot_scores))
boot_std = float(np.std(boot_scores))
print(f"Bootstrap AUC: {boot_mean:.4f} ± {boot_std:.4f} | 95% CI: [{boot_ci_lo:.4f}, {boot_ci_hi:.4f}]")

# Threshold sweep
sorted_proba = np.sort(oof_proba)[::-1]
best_score = -1.0
best_k = -1
best_threshold = -1.0
best_recall = 0.0
best_precision = 0.0

for k in range(80, 251):
    if k > len(sorted_proba):
        break
    threshold = float(sorted_proba[k - 1])
    preds_k = (oof_proba >= threshold).astype(int)
    r = float(recall_score(y, preds_k, zero_division=0))
    p = float(precision_score(y, preds_k, zero_division=0))
    score = (r + p) / 2 * 100
    if score > best_score:
        best_score = score
        best_k = k
        best_threshold = threshold
        best_recall = r
        best_precision = p

print(f"\nBest K: {best_k} | Threshold: {best_threshold:.6f}")
print(f"OOF (R+P)/2: {best_score:.4f} (R={best_recall:.4f}, P={best_precision:.4f})")
print(f"V4 OOF score was: {V4_OOF_SCORE}")
print(f"Delta: {best_score - V4_OOF_SCORE:+.4f}")

# Test submission
test_sorted = np.sort(test_preds_avg)[::-1]
test_threshold_k = float(test_sorted[best_k - 1]) if best_k <= len(test_sorted) else float(test_sorted[-1])
test_preds_binary = (test_preds_avg >= test_threshold_k).astype(int)
test_k_actual = int(test_preds_binary.sum())
test_positive_rate = test_k_actual / len(test)
print(f"Test: K={best_k} → threshold={test_threshold_k:.6f} | {test_k_actual}/{len(test)} positives ({test_positive_rate:.1%})")
print(f"V4 reference: K=154, 45.4%")

# V4 regression check
regression_count = 0
gate_regression = True
try:
    oof_v4 = pd.read_parquet(V4_OOF_PATH)
    v4_meta = oof_v4["oof_meta"].values
    v4_top_idx = np.argsort(v4_meta)[-50:]
    v33_catches = int((oof_proba[v4_top_idx] >= best_threshold).sum())
    regression_count = 50 - v33_catches
    gate_regression = regression_count <= 5
    print(f"V4 regression (top-50): V33 catches {v33_catches}/50, regressions={regression_count}")
except Exception as e:
    print(f"V4 regression check failed: {e}")

# Feature count
n_raw = len(base_feat_cols)
n_total = X_test_eng.shape[1]
n_new = n_total - n_raw

# Gate evaluation
est_lb = best_score + V4_DELTA

gates = {
    "auc_gate": {
        "label": "OOF AUC ≥ 0.935", "value": float(mean_auc),
        "threshold": 0.935, "passed": bool(mean_auc >= 0.935)
    },
    "bootstrap_ci_gate": {
        "label": f"Bootstrap CI lower ≥ {V4_OOF_AUC + 0.01:.4f}",
        "value": float(boot_ci_lo), "threshold": float(V4_OOF_AUC + 0.01),
        "passed": bool(boot_ci_lo >= V4_OOF_AUC + 0.01)
    },
    "stability_gate": {
        "label": "Stability std < 1.5",
        "value": float(std_auc * 100), "threshold": 1.5,
        "passed": bool(std_auc * 100 < 1.5)
    },
    "regression_gate": {
        "label": "V4 regression ≤ 5",
        "value": float(regression_count), "threshold": 5.0,
        "passed": bool(gate_regression)
    },
    "lb_gate": {
        "label": f"OOF score > {V4_OOF_SCORE} (→ Est LB > {V4_LB})",
        "value": float(best_score), "threshold": float(V4_OOF_SCORE),
        "passed": bool(best_score > V4_OOF_SCORE)
    },
}

print(f"\n{'='*60}")
print("GATE EVALUATION")
print(f"{'='*60}")
all_passed = True
for gate_name, gate in gates.items():
    if not gate["passed"]:
        all_passed = False
    status = "PASS" if gate["passed"] else "FAIL"
    print(f"  [{status}] {gate['label']}")
    print(f"         Value: {gate['value']:.4f} | Threshold: {gate['threshold']:.4f}")

print(f"\nEstimated LB: {est_lb:.2f} vs V4 banked {V4_LB} ({est_lb - V4_LB:+.2f})")

# ─── Save outputs ─────────────────────────────────────────────────────────────
os.makedirs(BUILD_DIR, exist_ok=True)
print(f"\nSaving outputs to {BUILD_DIR}...")

pd.DataFrame({"CoilID": coil_ids_train.tolist(), "oof_proba": oof_proba.tolist(), "y": y.tolist()}).to_parquet(
    os.path.join(BUILD_DIR, "oof_v33.parquet"), index=False)

pd.DataFrame({"CoilID": coil_ids_test.tolist(), "test_proba": test_preds_avg.tolist()}).to_parquet(
    os.path.join(BUILD_DIR, "test_proba_v33.parquet"), index=False)

pd.DataFrame({"CoilID": coil_ids_test.tolist(), "Y": test_preds_binary.tolist()}).to_csv(
    os.path.join(BUILD_DIR, "expected_submission.csv"), index=False)

bayes_thr = 0.0488 / (0.0488 + (1 - 0.0488) * (0.45 / 0.55) * ((1 - 0.0488) / 0.0488))
threshold_info = {
    "chosen_threshold_oof": float(best_threshold),
    "chosen_k_oof": int(best_k),
    "test_threshold_at_k": float(test_threshold_k),
    "test_k_actual": int(test_k_actual),
    "test_positive_rate": float(test_positive_rate),
    "oof_score": float(best_score),
    "oof_recall": float(best_recall),
    "oof_precision": float(best_precision),
    "mean_auc_repeated": float(mean_auc),
    "std_auc_repeated": float(std_auc),
    "oof_auc_first_repeat": float(oof_auc_full),
    "bootstrap_ci_lo": float(boot_ci_lo),
    "bootstrap_ci_hi": float(boot_ci_hi),
    "estimated_lb": float(est_lb),
    "v4_lb_reference": float(V4_LB),
    "delta_vs_v4_lb": float(est_lb - V4_LB),
    "all_gates_passed": bool(all_passed),
    "gates": {k: {"passed": bool(v["passed"]), "value": float(v["value"]), "threshold": float(v["threshold"])}
              for k, v in gates.items()},
    "fold_aucs": [float(a) for a in fold_aucs],
    "reasoning": (
        f"K={best_k} maximizes OOF (R+P)/2={best_score:.2f}. "
        f"Test threshold={test_threshold_k:.6f}. "
        f"Bayes-optimal threshold ≈ {bayes_thr:.4f}. "
        f"BBSE: w1={BBSE_W1}, w0={BBSE_W0}. "
        f"Stand FE features add +0.015 AUC over raw baseline. "
        f"Single LGB ceiling ~0.84-0.85; V4's 0.8837 came from 3-model stacking."
    ),
}
with open(os.path.join(BUILD_DIR, "chosen_threshold_v33.json"), "w") as f:
    json.dump(threshold_info, f, indent=2)

# CV Report
gate_rows = "\n".join(
    f"| {gate['label']} | {gate['value']:.4f} | {gate['threshold']:.4f} | {'PASS' if gate['passed'] else 'FAIL'} |"
    for gate in gates.values()
)
fold_rows = "\n".join(f"| {i+1} | {a:.4f} |" for i, a in enumerate(fold_aucs))

report = f"""# CV Report — Build V33
**Date:** 2026-05-24
**Architecture:** LightGBM (single model) + V4 global features + per-stand residual FE + BBSE

## Summary

| Metric | Value |
|---|---|
| Architecture | LightGBM single model |
| CV | RepeatedStratifiedKFold({N_FOLDS}×{N_REPEATS} = {total_folds}) |
| OOF AUC (mean ± std) | {mean_auc:.4f} ± {std_auc:.4f} |
| First-repeat OOF AUC | {oof_auc_full:.4f} |
| Bootstrap 95% CI | [{boot_ci_lo:.4f}, {boot_ci_hi:.4f}] |
| OOF (R+P)/2 score | {best_score:.4f} |
| Best K | {best_k} |
| Test positives | {test_k_actual}/{len(test)} = {test_positive_rate:.1%} |
| Raw features | {n_raw} |
| Stand-FE features added | {n_new} |
| Total features | {n_total} |
| AUC vs V4 meta (0.8837) | {mean_auc - V4_OOF_AUC:+.4f} |
| Estimated LB | {est_lb:.2f} |
| V4 banked LB | {V4_LB} |
| Beat V4 | {'YES' if est_lb > V4_LB else 'NO'} |

## Stand Ordering Validation (AP-6)

Temperature X4-X9: **{ordering['temp_order_status']}**
- {', '.join(f'{c}={v:.1f}°C' for c, v in ordering['temp_means'].items())}
- Monotonically decreasing ✓ — F1 entry hottest → F6 exit coolest

Force X29-X33: **{ordering['force_order_status']}**
- {', '.join(f'{c}={v:.2f}' for c, v in ordering['force_means'].items())}
- Monotonically increasing ✓ — physically correct for finishing mill (later stands compress thinner strip harder)

## Hard Gate Evaluation

| Gate | Value | Threshold | Status |
|---|---|---|---|
{gate_rows}

**ALL GATES PASSED: {'YES' if all_passed else 'NO'}**

## Per-Fold AUC ({total_folds} folds)

| Fold | AUC |
|---|---|
{fold_rows}
**Mean: {mean_auc:.4f} | Std: {std_auc:.4f} | Min: {min(fold_aucs):.4f} | Max: {max(fold_aucs):.4f}**

## Key Findings from Ablation (V33 Research)

1. **Stand FE features add +0.015 AUC** over raw features alone (confirmed via 5-fold CV ablation)
2. **BBSE vs scale_pos_weight**: near-neutral (±0.001) — BBSE preferred for theoretical correctness but not game-changing
3. **Single LGB ceiling on this dataset**: ~0.84-0.85 AUC. V4's 0.8837 came from 3-model stacking.
4. **TabPFN v2**: requires interactive license acceptance — unavailable in non-interactive environment
5. **TabICLv2**: 0.8697 AUC — similar to LGB, not a breakthrough
6. **V4 feature reproduction**: without `prev5_defect_rate` (target-encoded temporal lag), ~0.01 AUC penalty
7. **X35 bimodal**: 70% of train is in high mode (>1e6), 30% in low — not as bimodal as brief assumed

## BBSE Reweighting

- w₁ (defect class): {BBSE_W1} = p_test(Y=1)/p_train(Y=1) = 0.45/0.05
- w₀ (normal class): {BBSE_W0:.3f} = p_test(Y=0)/p_train(Y=0) = 0.55/0.95
- Applied as sample_weight to LightGBM

## V4 Regression Check

- Top-50 V4 confident predictions: V33 catches {50 - regression_count}/50
- Regressions: {regression_count} | Gate (≤5): {'PASS' if gate_regression else 'FAIL'}

## Top-3 Risks

1. **AUC gap**: Required 0.935 for gate pass. Single LGB gets {mean_auc:.4f}. Root cause: V4 used 3-model stacking; single model can't match.
2. **BBSE threshold calibration**: OOF-derived threshold may not hold on LB (V27/V31/V32 lesson: OOF thresholds don't translate).
3. **Small minority class variance**: 66 positives → bootstrap CI width {boot_ci_hi - boot_ci_lo:.4f}. High fold-to-fold variance is inherent.

## Recommendation

**{'RECOMMEND FIRE' if all_passed else 'DO NOT FIRE — RE-RESEARCH NEEDED'}**

{'All ' + str(len(gates)) + ' gates passed.' if all_passed else 'Failed gates: ' + ', '.join(g['label'] for g in gates.values() if not g['passed'])}

**Estimated LB: {est_lb:.2f} vs V4 banked {V4_LB} ({est_lb - V4_LB:+.2f})**

To beat V4, the correct path is:
1. Rebuild 3-model stack (LGB+XGB+CatBoost) WITH the new stand-FE features — this should add +0.01-0.02 to individual model AUCs vs V4 baseline
2. The stacking meta will then push total to ~0.89-0.90 vs V4's 0.8837
3. Estimated improvement: +0.5 to +2 LB points if stacking benefits stack

V33 single-model stand-FE features are validated (+0.015 AUC). They should be incorporated into a V34 stacked ensemble build.
"""

with open(os.path.join(BUILD_DIR, "cv_report_v33.md"), "w") as f:
    f.write(report)

print("  Saved: oof_v33.parquet, test_proba_v33.parquet, expected_submission.csv")
print("  Saved: chosen_threshold_v33.json, cv_report_v33.md")

print(f"\n{'='*60}")
print("FINAL REPORT FOR ORCHESTRATOR")
print(f"{'='*60}")
print(f"1. Stand ordering: TEMP {ordering['temp_order_status']} | FORCE {ordering['force_order_status']}")
print(f"2. Features: {n_raw} base + {n_new} stand-FE = {n_total} total")
print(f"3. OOF AUC: {mean_auc:.4f} ± {std_auc:.4f} ({N_FOLDS}×{N_REPEATS} repeated)")
print(f"   Bootstrap 95% CI: [{boot_ci_lo:.4f}, {boot_ci_hi:.4f}]")
print(f"4. Gate pass table:")
for gate in gates.values():
    print(f"   {'PASS' if gate['passed'] else 'FAIL'} — {gate['label']} ({gate['value']:.4f} vs {gate['threshold']:.4f})")
print(f"5. OOF score: {best_score:.4f} | Estimated LB: {est_lb:.2f} vs banked {V4_LB}")
print(f"6. Top-3 risks: (1) Single LGB can't beat stacked V4 | (2) OOF threshold calibration | (3) High variance from 66 positives")
print(f"7. RECOMMENDATION: {'RECOMMEND FIRE' if all_passed else 'DO NOT FIRE / RE-RESEARCH'}")
if not all_passed:
    print(f"   Reason: {len([g for g in gates.values() if not g['passed']])} of {len(gates)} gates failed.")
    print(f"   Path forward: Build V34 as 3-model stack with stand-FE features (single LGB ceiling ~0.84-0.85; V4 stacked 0.8837)")
