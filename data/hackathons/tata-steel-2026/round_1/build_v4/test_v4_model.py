"""
V4 model + submission test suite.

Pre-upload sanity checks — does what we *think* V4 does line up with what
the artifacts actually contain? Bootstraps a 95% CI on the predicted LB
score, validates the submission CSV schema + distribution, and compares
V4's flagged coils against V2's.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

BASE = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1")
V4 = BASE / "build_v4"
V3 = BASE / "build_v3"
V2 = BASE / "build_v2"

PASS = "[PASS]"
WARN = "[WARN]"
FAIL = "[FAIL]"
INFO = "[INFO]"

RESULTS: list[tuple[str, str]] = []


def log(tag: str, msg: str) -> None:
    RESULTS.append((tag, msg))
    print(f"{tag}  {msg}")


def section(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


# ── 1. Load artifacts ───────────────────────────────────────────────────────
section("1. LOAD V4 ARTIFACTS")

oof = pd.read_parquet(V4 / "oof_v4.parquet")
test_meta = pd.read_parquet(V4 / "test_meta_v4.parquet")
test_feat = pd.read_parquet(V4 / "test_v4.parquet")
chosen = json.loads((V4 / "chosen_threshold_v4.json").read_text())
sub = pd.read_csv(V4 / "expected_submission.csv")

log(INFO, f"OOF rows: {len(oof)} | cols: {oof.columns.tolist()}")
log(INFO, f"Test meta rows: {len(test_meta)}")
log(INFO, f"Test feat rows: {len(test_feat)}")
log(INFO, f"Submission rows: {len(sub)}")
log(INFO, f"Chosen T: {chosen['chosen_threshold']:.6f}  Predicted LB: {chosen['predicted_lb_score']:.4f}")


# ── 2. Reproduce OOF metrics ────────────────────────────────────────────────
section("2. REPRODUCE OOF METRICS FROM PROBABILITIES")

p_oof = oof["oof_meta"].values
y_oof = oof["Y"].values
T = chosen["chosen_threshold"]

pred = (p_oof >= T).astype(int)
tp = int(((pred == 1) & (y_oof == 1)).sum())
fp = int(((pred == 1) & (y_oof == 0)).sum())
fn = int(((pred == 0) & (y_oof == 1)).sum())
tn = int(((pred == 0) & (y_oof == 0)).sum())

recall = tp / (tp + fn) if (tp + fn) else 0.0
precision = tp / (tp + fp) if (tp + fp) else 0.0
score = (recall + precision) / 2 * 100
n_pos = int(pred.sum())

claimed_score = chosen["predicted_lb_score"]
claimed_recall = chosen["oof_recall"]
claimed_precision = chosen["oof_precision"]
claimed_n_pos = chosen["oof_n_positives"]

log(INFO, f"TP={tp}  FP={fp}  FN={fn}  TN={tn}")
log(INFO, f"Recall={recall:.6f} (claimed {claimed_recall:.6f})")
log(INFO, f"Precision={precision:.6f} (claimed {claimed_precision:.6f})")
log(INFO, f"Score={score:.6f} (claimed {claimed_score:.6f})")
log(INFO, f"n_pos OOF={n_pos} (claimed {claimed_n_pos})")

if abs(score - claimed_score) < 1e-3:
    log(PASS, "Score reproduces from saved probas (within 1e-3)")
else:
    log(FAIL, f"Score mismatch: computed {score:.6f}, claimed {claimed_score:.6f}")

if recall == claimed_recall:
    log(PASS, "Recall reproduces exactly")
else:
    log(FAIL, f"Recall mismatch: {recall} vs {claimed_recall}")

if abs(precision - claimed_precision) < 1e-6:
    log(PASS, "Precision reproduces (within 1e-6)")
else:
    log(FAIL, f"Precision mismatch: {precision:.6f} vs {claimed_precision:.6f}")


# ── 3. Bootstrap 95% CI on OOF score ────────────────────────────────────────
section("3. BOOTSTRAP 95% CI ON OOF SCORE (n_boot=2000)")

rng = np.random.default_rng(42)
N = len(p_oof)
scores_boot = np.empty(2000)
recalls_boot = np.empty(2000)
precisions_boot = np.empty(2000)

for i in range(2000):
    idx = rng.integers(0, N, N)
    p_b = p_oof[idx]
    y_b = y_oof[idx]
    pred_b = (p_b >= T).astype(int)
    tp_b = ((pred_b == 1) & (y_b == 1)).sum()
    fp_b = ((pred_b == 1) & (y_b == 0)).sum()
    fn_b = ((pred_b == 0) & (y_b == 1)).sum()
    r_b = tp_b / (tp_b + fn_b) if (tp_b + fn_b) else 0.0
    p_b_val = tp_b / (tp_b + fp_b) if (tp_b + fp_b) else 0.0
    scores_boot[i] = (r_b + p_b_val) / 2 * 100
    recalls_boot[i] = r_b
    precisions_boot[i] = p_b_val

s_mean = scores_boot.mean()
s_std = scores_boot.std()
s_lo, s_hi = np.percentile(scores_boot, [2.5, 97.5])
log(INFO, f"Bootstrap mean score: {s_mean:.4f}  std: {s_std:.4f}")
log(INFO, f"95% CI: [{s_lo:.4f}, {s_hi:.4f}]")
log(INFO, f"Recall  mean ± std: {recalls_boot.mean():.4f} ± {recalls_boot.std():.4f}")
log(INFO, f"Precision mean ± std: {precisions_boot.mean():.4f} ± {precisions_boot.std():.4f}")

if s_lo > 50.19:
    log(PASS, f"95% CI lower bound ({s_lo:.2f}) beats V2 LB (50.19) — V4 is robustly above V2")
elif s_mean > 50.19:
    log(WARN, f"Mean ({s_mean:.2f}) > V2 LB but CI overlaps — improvement noisy")
else:
    log(FAIL, f"Mean ({s_mean:.2f}) <= V2 LB (50.19) — V4 not robustly better")


# ── 4. Threshold sensitivity (±20% around chosen) ───────────────────────────
section("4. THRESHOLD SENSITIVITY")

multipliers = [0.5, 0.75, 0.9, 1.0, 1.1, 1.25, 1.5, 2.0]
rows = []
for m in multipliers:
    T_m = T * m
    pred_m = (p_oof >= T_m).astype(int)
    tp_m = ((pred_m == 1) & (y_oof == 1)).sum()
    fp_m = ((pred_m == 1) & (y_oof == 0)).sum()
    fn_m = ((pred_m == 0) & (y_oof == 1)).sum()
    r_m = tp_m / (tp_m + fn_m) if (tp_m + fn_m) else 0.0
    p_m = tp_m / (tp_m + fp_m) if (tp_m + fp_m) else 0.0
    s_m = (r_m + p_m) / 2 * 100
    rows.append({"mult": m, "T": T_m, "score": s_m, "R": r_m, "P": p_m, "n_pos_oof": int(pred_m.sum())})
df_sens = pd.DataFrame(rows)
print(df_sens.to_string(index=False))

# If small T moves wreck the score, that's bad — we're at a knife-edge.
nearby = df_sens[(df_sens["mult"] >= 0.9) & (df_sens["mult"] <= 1.1)]
sens_range = nearby["score"].max() - nearby["score"].min()
log(INFO, f"Score range across T × [0.9, 1.1]: {sens_range:.4f}")
if sens_range < 1.0:
    log(PASS, "Score is stable to ±10% threshold perturbation (range < 1.0)")
elif sens_range < 3.0:
    log(WARN, f"Moderate threshold sensitivity (range {sens_range:.2f}) — fine but watch")
else:
    log(FAIL, f"Score collapses under ±10% threshold perturbation ({sens_range:.2f}) — chosen T is a knife-edge")


# ── 5. Calibration check ────────────────────────────────────────────────────
section("5. CALIBRATION CHECK — meta proba vs realized defect rate")

# 10 deciles by predicted proba
oof_sorted = pd.DataFrame({"p": p_oof, "y": y_oof}).sort_values("p").reset_index(drop=True)
oof_sorted["decile"] = pd.qcut(oof_sorted.index, q=10, labels=False, duplicates="drop")
cal = oof_sorted.groupby("decile").agg(
    n=("y", "size"),
    mean_proba=("p", "mean"),
    realized_rate=("y", "mean"),
).reset_index()
cal["abs_gap"] = (cal["mean_proba"] - cal["realized_rate"]).abs()
print(cal.to_string(index=False))

# Brier score
brier = ((p_oof - y_oof) ** 2).mean()
ece = cal["abs_gap"].mean()
log(INFO, f"Brier score: {brier:.4f}")
log(INFO, f"Mean |mean_proba - realized_rate| across deciles (rough ECE): {ece:.4f}")
if ece < 0.05:
    log(PASS, "Calibration is tight (rough ECE < 0.05)")
elif ece < 0.10:
    log(WARN, f"Calibration moderate (rough ECE {ece:.3f}) — Platt scaling is doing some work but not perfect")
else:
    log(FAIL, f"Calibration is loose (rough ECE {ece:.3f}) — probabilities not trustworthy as probabilities")


# ── 6. Submission CSV validation ────────────────────────────────────────────
section("6. SUBMISSION CSV VALIDATION")

# Schema
assert sub.shape == (339, 2), f"Wrong shape {sub.shape}"
log(PASS, f"Shape (339, 2)")

assert set(sub.columns) == {"CoilID", "Y"}, f"Wrong columns {sub.columns.tolist()}"
log(PASS, f"Columns = {{CoilID, Y}}")

assert sub["Y"].isin([0, 1]).all(), "Y not binary"
log(PASS, "Y is strictly binary 0/1")

assert sub["CoilID"].is_unique, "CoilID has duplicates"
log(PASS, "CoilID is unique")

assert sub["CoilID"].equals(test_feat["CoilID"]), "CoilID order does not match test_v4"
log(PASS, "CoilID order matches test_v4.parquet")

n_pos_test = int(sub["Y"].sum())
pos_rate = n_pos_test / 339 * 100
log(INFO, f"Test predicted positives: {n_pos_test} / 339 = {pos_rate:.1f}%")

# Expected pos rate range
prevalence_train = float(y_oof.mean()) * 100
log(INFO, f"Training prevalence: {prevalence_train:.2f}%")
if pos_rate < 1 or pos_rate > 70:
    log(FAIL, f"Test pos rate {pos_rate:.1f}% is unreasonable (expected 5-50%)")
elif pos_rate > 50:
    log(WARN, f"Test pos rate {pos_rate:.1f}% is high — recall-heavy strategy as intended, but precision risk on LB")
else:
    log(PASS, f"Test pos rate {pos_rate:.1f}% in acceptable range")


# ── 7. Test proba distribution vs OOF defect proba ──────────────────────────
section("7. TEST PROBA DISTRIBUTION vs OOF DEFECT/NON-DEFECT DISTRIBUTIONS")

test_proba = test_meta["test_meta"].values
oof_pos = p_oof[y_oof == 1]
oof_neg = p_oof[y_oof == 0]

def q(arr: np.ndarray, qs=(0.0, 0.05, 0.25, 0.50, 0.75, 0.95, 1.0)) -> str:
    qv = np.quantile(arr, qs)
    return "  ".join(f"q{int(qq*100):02d}={v:.4f}" for qq, v in zip(qs, qv))

log(INFO, f"OOF defects   ({len(oof_pos):4d}):  {q(oof_pos)}")
log(INFO, f"OOF non-def   ({len(oof_neg):4d}):  {q(oof_neg)}")
log(INFO, f"Test proba    ({len(test_proba):4d}):  {q(test_proba)}")

# Two-sample KS: is test proba distribution similar to OOF (entire training set)?
ks_stat, ks_p = stats.ks_2samp(test_proba, p_oof)
log(INFO, f"KS test (test_proba vs full OOF): stat={ks_stat:.4f}, p={ks_p:.4f}")
if ks_p > 0.05:
    log(PASS, "Test proba distribution looks similar to OOF distribution (no covariate shift)")
elif ks_p > 0.01:
    log(WARN, f"Mild distribution shift between test and OOF probas (KS p={ks_p:.4f})")
else:
    log(WARN, f"Significant distribution shift (KS p={ks_p:.4f}) — model may behave differently on test than OOF suggests")


# ── 8. Compare V4 vs V2 vs V3 submissions ───────────────────────────────────
section("8. V4 vs V2 vs V3 SUBMISSION AGREEMENT")

# V2 submission
v2_sub_path = V2 / "expected_submission.csv"
v3_sub_path = V3 / "expected_submission.csv"

if v2_sub_path.exists():
    v2_sub = pd.read_csv(v2_sub_path)
    v2_pos = set(v2_sub.loc[v2_sub["Y"] == 1, "CoilID"])
    v4_pos = set(sub.loc[sub["Y"] == 1, "CoilID"])
    overlap = v2_pos & v4_pos
    only_v2 = v2_pos - v4_pos
    only_v4 = v4_pos - v2_pos
    log(INFO, f"V2 positives: {len(v2_pos)}  V4 positives: {len(v4_pos)}")
    log(INFO, f"Both:  {len(overlap)}   V2-only: {len(only_v2)}   V4-only: {len(only_v4)}")
    if len(v2_pos) and len(v4_pos):
        jaccard = len(overlap) / len(v2_pos | v4_pos)
        log(INFO, f"Jaccard(V2, V4) on positives: {jaccard:.3f}")
        if jaccard > 0.7:
            log(PASS, "V4 mostly agrees with V2 on positives — incremental improvement")
        else:
            log(WARN, f"V4 disagrees substantially with V2 (Jaccard {jaccard:.2f}) — different decision surface")
else:
    log(WARN, f"V2 submission not found at {v2_sub_path}")

if v3_sub_path.exists():
    v3_sub = pd.read_csv(v3_sub_path)
    v3_pos = set(v3_sub.loc[v3_sub["Y"] == 1, "CoilID"])
    v4_pos = set(sub.loc[sub["Y"] == 1, "CoilID"])
    overlap = v3_pos & v4_pos
    log(INFO, f"V3 positives: {len(v3_pos)}  V4 positives: {len(v4_pos)}  shared: {len(overlap)}")
    if len(v3_pos | v4_pos):
        jaccard = len(overlap) / len(v3_pos | v4_pos)
        log(INFO, f"Jaccard(V3, V4): {jaccard:.3f}")


# ── 9. Pseudo-fold stability test ───────────────────────────────────────────
section("9. PSEUDO-FOLD STABILITY (artificial 5-way split of OOF)")

# Without saved fold IDs we can't do a true per-fold report. Closest test:
# random 5-way bagging on the OOF rows — does the score vary wildly across
# resamples, or is it tight?
rng = np.random.default_rng(7)
fold_scores = []
n_iter = 200
for _ in range(n_iter):
    # Random stratified split into 5 groups, take 4/5 as "training-like" mask
    idx_pos = np.where(y_oof == 1)[0]
    idx_neg = np.where(y_oof == 0)[0]
    rng.shuffle(idx_pos)
    rng.shuffle(idx_neg)
    keep = np.concatenate([idx_pos[:int(len(idx_pos) * 0.8)],
                           idx_neg[:int(len(idx_neg) * 0.8)]])
    p_sub = p_oof[keep]
    y_sub = y_oof[keep]
    pred_sub = (p_sub >= T).astype(int)
    tp_s = ((pred_sub == 1) & (y_sub == 1)).sum()
    fp_s = ((pred_sub == 1) & (y_sub == 0)).sum()
    fn_s = ((pred_sub == 0) & (y_sub == 1)).sum()
    r_s = tp_s / (tp_s + fn_s) if (tp_s + fn_s) else 0.0
    p_s = tp_s / (tp_s + fp_s) if (tp_s + fp_s) else 0.0
    fold_scores.append((r_s + p_s) / 2 * 100)

fs = np.array(fold_scores)
log(INFO, f"80% subsample scores (n={n_iter}): mean={fs.mean():.4f}, std={fs.std():.4f}")
log(INFO, f"  min={fs.min():.4f}  p25={np.percentile(fs, 25):.4f}  median={np.median(fs):.4f}  p75={np.percentile(fs, 75):.4f}  max={fs.max():.4f}")
if fs.std() < 0.5:
    log(PASS, f"Score is very stable across subsamples (std {fs.std():.3f} < 0.5)")
elif fs.std() < 1.5:
    log(PASS, f"Score is reasonably stable (std {fs.std():.3f} < 1.5)")
else:
    log(WARN, f"Score wobbles across subsamples (std {fs.std():.3f}) — single-LB-submission could be lucky/unlucky by 1-2 points")


# ── 10. Summary ─────────────────────────────────────────────────────────────
section("10. SUMMARY")

n_pass = sum(1 for t, _ in RESULTS if t == PASS)
n_warn = sum(1 for t, _ in RESULTS if t == WARN)
n_fail = sum(1 for t, _ in RESULTS if t == FAIL)
n_info = sum(1 for t, _ in RESULTS if t == INFO)

print(f"  PASS: {n_pass}   WARN: {n_warn}   FAIL: {n_fail}   INFO: {n_info}")
if n_fail == 0:
    print(f"\n  VERDICT: V4 submission is READY TO UPLOAD.")
    print(f"  Predicted LB: {chosen['predicted_lb_score']:.2f}")
    print(f"  Bootstrap 95% CI: [{s_lo:.2f}, {s_hi:.2f}]")
    print(f"  Threshold sensitivity (±10%): {sens_range:.2f}")
else:
    print(f"\n  VERDICT: {n_fail} FAILURES — DO NOT UPLOAD until resolved.")

# Save report
report = {
    "n_pass": n_pass,
    "n_warn": n_warn,
    "n_fail": n_fail,
    "n_info": n_info,
    "verdict": "ready" if n_fail == 0 else "not_ready",
    "bootstrap_95ci": [float(s_lo), float(s_hi)],
    "bootstrap_mean": float(s_mean),
    "threshold_sensitivity_range": float(sens_range),
    "brier_score": float(brier),
    "rough_ece": float(ece),
    "test_pos_rate": float(pos_rate),
    "results": [{"tag": t, "msg": m} for t, m in RESULTS],
}
(V4 / "v4_test_report.json").write_text(json.dumps(report, indent=2))
print(f"\nReport saved to {V4 / 'v4_test_report.json'}")
