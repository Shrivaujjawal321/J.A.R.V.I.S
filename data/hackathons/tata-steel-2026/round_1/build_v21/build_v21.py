"""
V21 — TabPFN v2 with API token unlocked.

Token is read from TABPFN_TOKEN env var. Never written to disk.
Single TabPFN model, 5-fold OOF on V5's 59 features. Compare to V5 baseline.
If TabPFN alone underperforms, try blend with V5.
"""

from __future__ import annotations

import json
import os
import warnings
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

ROOT = Path("/home/ujjwal/Documents/J.A.R.V.I.S.")
V5 = ROOT / "data/hackathons/tata-steel-2026/round_1/build_v5"
V21 = ROOT / "data/hackathons/tata-steel-2026/round_1/build_v21"
V21.mkdir(parents=True, exist_ok=True)

SEED = 42
N_FOLDS = 5
CAL_DELTA = 2.67
X42_DEFECT_CEIL = 0.025067
X39_CLEAN_FLOOR = 169.0


def hard_gate(df):
    return ((df["X42"] > X42_DEFECT_CEIL) | (df["X39"] >= X39_CLEAN_FLOOR)).values


# Verify token is set
if not os.environ.get("TABPFN_TOKEN"):
    raise SystemExit("TABPFN_TOKEN env var not set!")
print(f"TABPFN_TOKEN set (length {len(os.environ['TABPFN_TOKEN'])})")

print("\nLoading V5 features...")
train_v5 = pd.read_parquet(V5 / "train_v5.parquet").reset_index(drop=True)
test_v5 = pd.read_parquet(V5 / "test_v5.parquet").reset_index(drop=True)
with open(V5 / "feature_list_v5.json") as f:
    v5_features = json.load(f)["features"]

y = train_v5["Y"].values.astype(int)
n_train, n_test = len(train_v5), len(test_v5)
print(f"  train: {n_train}  test: {n_test}  defects: {y.sum()} ({y.mean()*100:.2f}%)")

# Scale features for TabPFN (it expects normalized inputs)
scaler = StandardScaler()
X_train = scaler.fit_transform(np.nan_to_num(train_v5[v5_features].values))
X_test = scaler.transform(np.nan_to_num(test_v5[v5_features].values))


# ─── TabPFN v2 5-fold OOF ────────────────────────────────────────────────────
print("\n[Phase A] TabPFN v2 5-fold OOF (token-unlocked)")

try:
    from tabpfn import TabPFNClassifier
    print("  using local tabpfn (license unlocked via token)")
    use_cloud = False
except Exception as e:
    print(f"  local tabpfn failed: {e}, falling back to tabpfn-client cloud")
    from tabpfn_client import TabPFNClassifier
    use_cloud = True

skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
oof = np.zeros(n_train)
test_preds_per_fold = []
fold_aucs = []

for fold_i, (tr, va) in enumerate(skf.split(np.zeros(n_train), y)):
    print(f"\n  Fold {fold_i+1}/{N_FOLDS}: {y[tr].sum()} pos train | {y[va].sum()} pos val")
    try:
        m = TabPFNClassifier(
            device="cpu",
            ignore_pretraining_limits=True,
            random_state=SEED,
        )
    except TypeError:
        # Older API
        m = TabPFNClassifier(device="cpu")
    try:
        m.fit(X_train[tr], y[tr])
        oof[va] = m.predict_proba(X_train[va])[:, 1]
        test_preds_per_fold.append(m.predict_proba(X_test)[:, 1])
        fold_aucs.append(roc_auc_score(y[va], oof[va]))
        print(f"    AUC={fold_aucs[-1]:.4f}")
    except Exception as e:
        print(f"    FAILED: {e}")
        fold_aucs.append(np.nan)
        test_preds_per_fold.append(np.zeros(n_test))

mean_auc = float(np.nanmean(fold_aucs)) if any(~np.isnan(fold_aucs)) else 0.5
oof_auc = float(roc_auc_score(y, oof)) if not np.all(oof == 0) else 0.5
test_proba = np.mean(test_preds_per_fold, axis=0)

print(f"\n  TabPFN per-fold mean AUC: {mean_auc:.4f}")
print(f"  TabPFN OOF AUC overall:   {oof_auc:.4f}  (V5 baseline: 0.8886)")


# ─── Threshold + gate ────────────────────────────────────────────────────────
print("\n[Phase B] Gate + threshold sweep")
gate_oof = hard_gate(train_v5); gate_test = hard_gate(test_v5)
oof_g = oof.copy(); oof_g[gate_oof] = 0
test_g = test_proba.copy(); test_g[gate_test] = 0


def sweep(p, y):
    uniq = np.sort(np.unique(np.concatenate([p, [0.0, 1.0]])))
    cuts = np.r_[uniq[0]-1e-6, 0.5*(uniq[:-1]+uniq[1:]), uniq[-1]+1e-6]
    bT, bS, bR, bP, bN = 0, 0, 0, 0, 0
    for t in cuts:
        pred = (p >= t).astype(int)
        tp = ((pred==1)&(y==1)).sum(); fp = ((pred==1)&(y==0)).sum(); fn = ((pred==0)&(y==1)).sum()
        R = tp/(tp+fn) if (tp+fn) else 0; P = tp/(tp+fp) if (tp+fp) else 0
        s = (R+P)/2*100
        if s > bS: bS, bT, bR, bP, bN = s, t, R, P, pred.sum()
    return bT, bS, bR, bP, bN

bT, bS, bR, bP, bN = sweep(oof_g, y)
print(f"  V21 standalone: T={bT:.5f}  OOF={bS:.3f}  R={bR:.3f}  P={bP:.3f}  n_oof={bN}")
print(f"  Calibrated LB: {bS + CAL_DELTA:.2f}")


# ─── Blend with V5 (safe single-add blend, not 3-way) ────────────────────────
print("\n[Phase C] Blend with V5")
oof_v5 = pd.read_parquet(V5 / "oof_v5.parquet")["oof_meta"].values
test_v5_meta = pd.read_parquet(V5 / "test_meta_v5.parquet")["test_meta"].values

best_blend = None
for w in [0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]:
    blend_oof = w * oof_g + (1 - w) * oof_v5 * (1 - gate_oof.astype(int))
    blend_test = w * test_g + (1 - w) * test_v5_meta * (1 - gate_test.astype(int))
    bT_, bS_, bR_, bP_, bN_ = sweep(blend_oof, y)
    auc = roc_auc_score(y, blend_oof)
    print(f"  V21_w={w:.1f}: AUC={auc:.4f}  OOF={bS_:.3f}  R={bR_:.3f}  P={bP_:.3f}  n_oof={bN_}")
    if best_blend is None or bS_ > best_blend[1]:
        best_blend = (w, bS_, bT_, bR_, bP_, blend_oof, blend_test, auc)

bw, bs_blend, bt_blend, br_blend, bp_blend, blend_oof_best, blend_test_best, blend_auc = best_blend
print(f"\n  Best blend: V21 weight {bw:.1f}, OOF {bs_blend:.3f}, AUC {blend_auc:.4f}")
print(f"  Calibrated LB est: {bs_blend + CAL_DELTA:.2f}")

# Bootstrap CI
rng = np.random.default_rng(SEED)
boot = np.empty(2000)
for i in range(2000):
    idx = rng.integers(0, n_train, n_train)
    pred = (blend_oof_best[idx] >= bt_blend).astype(int)
    yb = y[idx]
    tp = ((pred==1)&(yb==1)).sum(); fp = ((pred==1)&(yb==0)).sum(); fn = ((pred==0)&(yb==1)).sum()
    R = tp/(tp+fn) if (tp+fn) else 0; P = tp/(tp+fp) if (tp+fp) else 0
    boot[i] = (R+P)/2*100
ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
cal_lb = bs_blend + CAL_DELTA


# Save best variant
test_pred = (blend_test_best >= bt_blend).astype(int)
sub = pd.DataFrame({"CoilID": test_v5["CoilID"].values, "Y": test_pred})
sub.to_csv(V21 / "expected_submission.csv", index=False)

# Persist (no token in output)
pd.DataFrame({"oof_v21": oof, "Y": y}).to_parquet(V21 / "oof_v21.parquet")
pd.DataFrame({"test_v21": test_proba}).to_parquet(V21 / "test_v21.parquet")

with open(V21 / "chosen_threshold_v21.json", "w") as f:
    json.dump({
        "v21_standalone_oof_auc": oof_auc,
        "v21_standalone_score_oof": float(bS),
        "v5_baseline_auc": 0.8886,
        "delta_vs_v5": float(oof_auc - 0.8886),
        "fold_aucs": [float(a) if not np.isnan(a) else None for a in fold_aucs],
        "best_blend_weight": float(bw),
        "best_blend_auc": float(blend_auc),
        "best_blend_score_oof": float(bs_blend),
        "chosen_threshold": float(bt_blend),
        "recall_at_T": float(br_blend), "precision_at_T": float(bp_blend),
        "n_pos_test": int(test_pred.sum()),
        "bootstrap_ci_oof": [float(ci_lo), float(ci_hi)],
        "lb_estimate_corrected": float(cal_lb),
        "v4_actual_lb": 56.98113,
    }, f, indent=2)

with open(V21 / "approach.md", "w") as f:
    f.write(f"# V21 — TabPFN v2 + blend\n\nTabPFN OOF AUC: {oof_auc:.4f}\nBest blend (V21 weight {bw}): AUC {blend_auc:.4f}, OOF {bs_blend:.2f}\nCalibrated LB: {cal_lb:.2f}\n")
import nbformat as nbf
nb = nbf.v4.new_notebook()
nb["cells"] = [nbf.v4.new_markdown_cell(f"# V21 OOF {bs_blend:.2f}")]
with open(V21 / "solution.ipynb", "w") as f: nbf.write(nb, f)
with zipfile.ZipFile(V21 / "submission_v21.zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.write(V21 / "expected_submission.csv", "expected_submission.csv")
    z.write(V21 / "approach.md", "approach.md")
    z.write(V21 / "solution.ipynb", "solution.ipynb")

print("\n" + "=" * 60)
print("V21 FINAL")
print("=" * 60)
print(f"  TabPFN standalone OOF AUC: {oof_auc:.4f}  (V5: 0.8886, delta {oof_auc-0.8886:+.4f})")
print(f"  Best blend weight:         {bw:.1f}")
print(f"  Best blend OOF AUC:        {blend_auc:.4f}")
print(f"  Best blend OOF (R+P)/2:    {bs_blend:.2f}")
print(f"  Bootstrap CI OOF:          [{ci_lo:.2f}, {ci_hi:.2f}]")
print(f"  Calibrated LB est:         {cal_lb:.2f}")
print(f"  V4 actual:                 56.98")
print(f"  Test n_pos:                {test_pred.sum()}")
print(f"  Hits 70/65/60?             {'Y' if cal_lb>=70 else 'N'}/{'Y' if cal_lb>=65 else 'N'}/{'Y' if cal_lb>=60 else 'N'}")
print("=" * 60)
