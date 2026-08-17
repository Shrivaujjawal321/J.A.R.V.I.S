"""
V15 — Hierarchical per-grade specialists.

For each X39 grade with sufficient train data, train a separate LGBMClassifier.
Predict test rows using matching-grade specialist. Low-data grades fall back to
V5 ensemble probabilities.

Architecture:
  Stage 1: Hard gate (X42 > 0.025 OR X39 >= 169) -> predict 0
  Stage 2: For each "majority grade" with >= 30 train rows and >= 5 defects,
           train an LGB specialist on that grade's rows (V5 features).
  Stage 3: Test predictions = specialist proba (if grade has specialist)
                              OR V5 meta proba (fallback)
  Stage 4: Score-aware threshold sweep on full OOF.
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
import lightgbm as lgb

warnings.filterwarnings("ignore")

ROOT = Path("/home/ujjwal/Documents/J.A.R.V.I.S.")
V5 = ROOT / "data/hackathons/tata-steel-2026/round_1/build_v5"
V15 = ROOT / "data/hackathons/tata-steel-2026/round_1/build_v15"
V15.mkdir(parents=True, exist_ok=True)

SEED = 42
N_FOLDS = 5
CAL_DELTA = 2.67
X42_DEFECT_CEIL = 0.025067
X39_CLEAN_FLOOR = 169.0
MIN_ROWS_FOR_SPECIALIST = 30
MIN_DEFECTS_FOR_SPECIALIST = 5


def hard_gate(df):
    return ((df["X42"] > X42_DEFECT_CEIL) | (df["X39"] >= X39_CLEAN_FLOOR)).values


print("Loading V5 features + OOF...")
train_v5 = pd.read_parquet(V5 / "train_v5.parquet").reset_index(drop=True)
test_v5 = pd.read_parquet(V5 / "test_v5.parquet").reset_index(drop=True)
with open(V5 / "feature_list_v5.json") as f:
    v5_features = json.load(f)["features"]

y = train_v5["Y"].values.astype(int)
n_train, n_test = len(train_v5), len(test_v5)

# V5 OOF + test meta for fallback
v5_oof_meta = pd.read_parquet(V5 / "oof_v5.parquet")["oof_meta"].values
v5_test_meta = pd.read_parquet(V5 / "test_meta_v5.parquet")["test_meta"].values

# Identify majority grades (qualifying for specialist)
grade_counts = train_v5.groupby("X39").agg(n=("Y", "size"), defects=("Y", "sum")).reset_index()
qualifying = grade_counts[(grade_counts["n"] >= MIN_ROWS_FOR_SPECIALIST) & (grade_counts["defects"] >= MIN_DEFECTS_FOR_SPECIALIST)]
specialist_grades = sorted(qualifying["X39"].astype(int).tolist())
print(f"\nGrades qualifying for specialist (>= {MIN_ROWS_FOR_SPECIALIST} rows + >= {MIN_DEFECTS_FOR_SPECIALIST} defects):")
for g in specialist_grades:
    row = qualifying[qualifying.X39 == g].iloc[0]
    print(f"  X39={g}: {int(row['n'])} rows, {int(row['defects'])} defects ({row['defects']/row['n']*100:.1f}%)")

# Coverage
spec_mask_train = train_v5["X39"].isin(specialist_grades)
spec_mask_test = test_v5["X39"].isin(specialist_grades)
print(f"\nSpecialist coverage:")
print(f"  Train: {spec_mask_train.sum()}/{n_train} rows ({spec_mask_train.mean()*100:.1f}%)  defects: {y[spec_mask_train].sum()}/{y.sum()}")
print(f"  Test:  {spec_mask_test.sum()}/{n_test} rows ({spec_mask_test.mean()*100:.1f}%)")


# ─── 5-fold OOF: per-grade specialists + V5 fallback ─────────────────────────
print("\n[Phase A] 5-fold OOF with per-grade specialists")

skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
oof_v15 = np.zeros(n_train)
test_v15_aggregator = {g: [] for g in specialist_grades}  # collect per-fold test probas

for fold_i, (tr_idx, val_idx) in enumerate(skf.split(np.zeros(n_train), y)):
    print(f"\n  Fold {fold_i+1}/{N_FOLDS}")
    # For each grade with specialist, train on fold's train-rows-in-grade
    for g in specialist_grades:
        grade_tr_mask = (train_v5.iloc[tr_idx]["X39"] == g).values
        grade_va_mask = (train_v5.iloc[val_idx]["X39"] == g).values
        if grade_tr_mask.sum() < 5 or y[tr_idx[grade_tr_mask]].sum() < 1:
            # Fall back to V5 OOF for this fold/grade
            oof_v15[val_idx[grade_va_mask]] = v5_oof_meta[val_idx[grade_va_mask]]
            continue
        Xtr = train_v5.iloc[tr_idx[grade_tr_mask]][v5_features].values
        ytr = y[tr_idx[grade_tr_mask]]
        Xva = train_v5.iloc[val_idx[grade_va_mask]][v5_features].values if grade_va_mask.any() else np.empty((0, len(v5_features)))
        Xte_grade = test_v5[test_v5["X39"] == g][v5_features].values

        # Very small data -> heavy regularization, no class weight (we want stability)
        m = lgb.LGBMClassifier(
            n_estimators=200, learning_rate=0.03, max_depth=4, num_leaves=8,
            min_child_samples=3, reg_alpha=1.0, reg_lambda=1.0,
            random_state=SEED, verbose=-1,
            scale_pos_weight=max(1.0, (ytr == 0).sum() / max(ytr.sum(), 1) * 0.5),  # moderate
        )
        try:
            m.fit(Xtr, ytr)
        except Exception as e:
            print(f"    grade {g}: fit failed ({e}); fallback to V5")
            if grade_va_mask.any():
                oof_v15[val_idx[grade_va_mask]] = v5_oof_meta[val_idx[grade_va_mask]]
            continue

        if grade_va_mask.any():
            oof_v15[val_idx[grade_va_mask]] = m.predict_proba(Xva)[:, 1]
        # Test predictions for this grade (averaged across folds)
        if len(Xte_grade) > 0:
            test_v15_aggregator[g].append(m.predict_proba(Xte_grade)[:, 1])
        if fold_i == 0:
            print(f"    grade {g}: train={grade_tr_mask.sum()} rows, val={grade_va_mask.sum()}, defects_train={int(ytr.sum())}")

    # Fallback: any val row NOT in a specialist grade -> use V5 OOF
    fallback_va_mask = ~train_v5.iloc[val_idx]["X39"].isin(specialist_grades).values
    fallback_idx = val_idx[fallback_va_mask]
    oof_v15[fallback_idx] = v5_oof_meta[fallback_idx]


# Aggregate test predictions: per-grade average across folds, V5 fallback otherwise
test_v15 = np.zeros(n_test)
for i, row in test_v5.iterrows():
    g = int(row["X39"])
    if g in specialist_grades and test_v15_aggregator[g]:
        # Multi-fold average for this grade's specialists
        per_fold_preds = test_v15_aggregator[g]
        # Each fold's specialist predicted on ALL test rows in this grade; average them
        # Stack and average (preserving row order in this grade)
        idx_in_grade = test_v5[test_v5["X39"] == g].index
        position = list(idx_in_grade).index(i)
        per_fold_vals = [p[position] for p in per_fold_preds]
        test_v15[i] = np.mean(per_fold_vals)
    else:
        test_v15[i] = v5_test_meta[i]


# ─── Phase B: AUC + gate + threshold ─────────────────────────────────────────
print("\n[Phase B] V15 OOF AUC + gate + threshold")
oof_auc = float(roc_auc_score(y, oof_v15))
print(f"  V15 OOF AUC: {oof_auc:.4f}  (V5 baseline: 0.8886)")

gate_oof = hard_gate(train_v5)
gate_test = hard_gate(test_v5)
oof_v15_g = oof_v15.copy(); oof_v15_g[gate_oof] = 0
test_v15_g = test_v15.copy(); test_v15_g[gate_test] = 0

uniq = np.sort(np.unique(np.concatenate([oof_v15_g, [0.0, 1.0]])))
cuts = np.r_[uniq[0]-1e-6, 0.5*(uniq[:-1]+uniq[1:]), uniq[-1]+1e-6]
best_T, best_S, best_R, best_P, best_n = 0, 0, 0, 0, 0
for t in cuts:
    pred = (oof_v15_g >= t).astype(int)
    tp = ((pred==1)&(y==1)).sum(); fp = ((pred==1)&(y==0)).sum(); fn = ((pred==0)&(y==1)).sum()
    R = tp/(tp+fn) if (tp+fn) else 0; P = tp/(tp+fp) if (tp+fp) else 0
    s = (R+P)/2*100
    if s > best_S: best_S, best_T, best_R, best_P, best_n = s, t, R, P, pred.sum()
test_pred = (test_v15_g >= best_T).astype(int)
print(f"  V15 standalone: T={best_T:.5f}  OOF={best_S:.3f}  R={best_R:.3f}  P={best_P:.3f}  n_oof={best_n}  n_test={test_pred.sum()}")

# Bootstrap
rng = np.random.default_rng(SEED)
boot = np.empty(2000)
for i in range(2000):
    idx = rng.integers(0, n_train, n_train)
    pred = (oof_v15_g[idx] >= best_T).astype(int)
    yb = y[idx]
    tp = ((pred==1)&(yb==1)).sum(); fp = ((pred==1)&(yb==0)).sum(); fn = ((pred==0)&(yb==1)).sum()
    R = tp/(tp+fn) if (tp+fn) else 0; P = tp/(tp+fp) if (tp+fp) else 0
    boot[i] = (R+P)/2*100
ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
cal_lb = best_S + CAL_DELTA
print(f"  Bootstrap CI: [{ci_lo:.2f}, {ci_hi:.2f}]  Calibrated LB: {cal_lb:.2f}")


# ─── Phase C: V15 + V5 blend (V5 acts as stabilizer) ─────────────────────────
print("\n[Phase C] V15 + V5 blend")
for w_v15 in [0.3, 0.5, 0.7, 1.0]:
    p_blend_oof = w_v15 * oof_v15_g + (1 - w_v15) * v5_oof_meta * (1 - gate_oof.astype(int))
    p_blend_test = w_v15 * test_v15_g + (1 - w_v15) * v5_test_meta * (1 - gate_test.astype(int))
    uniq_b = np.sort(np.unique(np.concatenate([p_blend_oof, [0.0, 1.0]])))
    cuts_b = np.r_[uniq_b[0]-1e-6, 0.5*(uniq_b[:-1]+uniq_b[1:]), uniq_b[-1]+1e-6]
    bT, bS = 0, 0; bR, bP, bN = 0, 0, 0
    for t in cuts_b:
        pred = (p_blend_oof >= t).astype(int)
        tp = ((pred==1)&(y==1)).sum(); fp = ((pred==1)&(y==0)).sum(); fn = ((pred==0)&(y==1)).sum()
        R = tp/(tp+fn) if (tp+fn) else 0; P = tp/(tp+fp) if (tp+fp) else 0
        s = (R+P)/2*100
        if s > bS: bS, bT, bR, bP, bN = s, t, R, P, pred.sum()
    auc = roc_auc_score(y, p_blend_oof)
    test_p = (p_blend_test >= bT).astype(int)
    print(f"  V15 weight {w_v15:.1f}: AUC={auc:.4f}  OOF={bS:.3f}  R={bR:.3f}  P={bP:.3f}  n_test={test_p.sum()}")


# Persist V15 (single, no blend - per V10 lesson)
sub = pd.DataFrame({"CoilID": test_v5["CoilID"].values, "Y": test_pred})
sub.to_csv(V15 / "expected_submission.csv", index=False)

pd.DataFrame({"oof_v15": oof_v15, "Y": y}).to_parquet(V15 / "oof_v15.parquet")
pd.DataFrame({"test_v15": test_v15}).to_parquet(V15 / "test_v15.parquet")

with open(V15 / "chosen_threshold_v15.json", "w") as f:
    json.dump({
        "oof_auc": oof_auc, "v5_baseline_auc": 0.8886,
        "delta_vs_v5": float(oof_auc - 0.8886),
        "chosen_threshold": float(best_T),
        "chosen_score_oof": float(best_S),
        "recall_at_T": float(best_R), "precision_at_T": float(best_P),
        "n_pos_test": int(test_pred.sum()),
        "bootstrap_ci_oof": [float(ci_lo), float(ci_hi)],
        "lb_estimate_corrected": float(cal_lb),
        "specialist_grades": specialist_grades,
        "specialist_coverage_train": float(spec_mask_train.mean()),
        "specialist_coverage_test": float(spec_mask_test.mean()),
        "v4_actual_lb": 56.98113,
    }, f, indent=2)

with open(V15 / "approach.md", "w") as f:
    f.write(f"# V15 — Per-grade specialists\n\nV15 OOF AUC: {oof_auc:.4f} (V5: 0.8886)\nOOF (R+P)/2: {best_S:.2f}\nCalibrated LB: {cal_lb:.2f}\nSpecialist grades: {specialist_grades}\n")
import nbformat as nbf
nb = nbf.v4.new_notebook()
nb["cells"] = [nbf.v4.new_markdown_cell(f"# V15 OOF {best_S:.2f}")]
with open(V15 / "solution.ipynb", "w") as f: nbf.write(nb, f)
with zipfile.ZipFile(V15 / "submission_v15.zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.write(V15 / "expected_submission.csv", "expected_submission.csv")
    z.write(V15 / "approach.md", "approach.md")
    z.write(V15 / "solution.ipynb", "solution.ipynb")

print("\n" + "=" * 60)
print("V15 FINAL")
print("=" * 60)
print(f"  V15 OOF AUC:           {oof_auc:.4f}  (V5: 0.8886, delta {oof_auc-0.8886:+.4f})")
print(f"  OOF (R+P)/2:           {best_S:.2f}")
print(f"  Bootstrap CI:          [{ci_lo:.2f}, {ci_hi:.2f}]")
print(f"  Calibrated LB:         {cal_lb:.2f}")
print(f"  Specialist coverage:   {spec_mask_train.mean()*100:.1f}% train, {spec_mask_test.mean()*100:.1f}% test")
print(f"  V4 actual:             56.98")
print(f"  Hits 70/65/60?         {'Y' if cal_lb>=70 else 'N'}/{'Y' if cal_lb>=65 else 'N'}/{'Y' if cal_lb>=60 else 'N'}")
print("=" * 60)
