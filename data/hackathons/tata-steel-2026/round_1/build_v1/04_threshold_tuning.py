"""
Step 4 — Threshold tuning on OOF predictions.
The critical step: find the threshold that maximizes recall subject to precision >= 0.90.
Also explores cost-sensitive threshold strategies.
"""

import sys
sys.path.insert(0, "/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1/ml_harness")

import json
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import precision_recall_curve, roc_auc_score, recall_score, precision_score

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
OUT_DIR = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1/build_v1")
FIG_DIR = OUT_DIR / "figures"
FIG_DIR.mkdir(exist_ok=True)

# ── Load OOF ──────────────────────────────────────────────────────────────────
oof_df = pd.read_parquet(OUT_DIR / "oof_predictions.parquet")
y_true = oof_df["Y"].values
y_prob = oof_df["oof_proba"].values

n_pos = y_true.sum()
n_neg = (y_true == 0).sum()
print(f"OOF set: {len(y_true)} rows, {n_pos:.0f} positive, {n_neg:.0f} negative")
print(f"OOF AUC: {roc_auc_score(y_true, y_prob):.4f}")
print()

# ── Dense threshold sweep ──────────────────────────────────────────────────────
# Use sklearn's precision_recall_curve which gives exact breakpoints
prec_arr, rec_arr, thr_arr = precision_recall_curve(y_true, y_prob)
# sklearn returns arrays of shape (n_thresholds + 1,) for prec/rec and (n_thresholds,) for thr
# Last element of prec/rec is always precision=1, recall=0 (no-predict edge case — skip)
prec_curve = prec_arr[:-1]
rec_curve  = rec_arr[:-1]
# Add extra sweep for edge cases (very low thresholds)
extra_thr = np.concatenate([np.linspace(0.001, thr_arr[0], 50)[:-1], thr_arr])
extra_prec = []
extra_rec  = []
for t in extra_thr:
    pred = (y_prob >= t).astype(int)
    p = precision_score(y_true, pred, zero_division=0)
    r = recall_score(y_true, pred, zero_division=0)
    extra_prec.append(p)
    extra_rec.append(r)

all_thr  = extra_thr
all_prec = np.array(extra_prec)
all_rec  = np.array(extra_rec)

# ── Key findings ───────────────────────────────────────────────────────────────
print("=" * 60)
print("THRESHOLD ANALYSIS")
print("=" * 60)

# 1. Smallest threshold where precision >= 0.90
prec90_mask = all_prec >= 0.90
if prec90_mask.any():
    # Among thresholds with precision >= 0.90, find the one with MAXIMUM recall
    best_idx   = np.argmax(all_rec[prec90_mask])
    best_thr   = all_thr[prec90_mask][best_idx]
    best_rec   = all_rec[prec90_mask][best_idx]
    best_prec  = all_prec[prec90_mask][best_idx]
    print(f"\n[TARGET]: Max recall at precision>=0.90")
    print(f"  Threshold : {best_thr:.4f}")
    print(f"  Recall    : {best_rec:.4f}  ({best_rec*n_pos:.0f}/{n_pos:.0f} defects caught)")
    print(f"  Precision : {best_prec:.4f}")
    tpr90_thr    = best_thr
    tpr90_recall = best_rec
    tpr90_prec   = best_prec
else:
    print("\n[TARGET]: NO threshold achieves precision>=0.90 on OOF")
    print("  (This is expected given 4.88% positive rate — precision floor is low)")
    tpr90_thr    = None
    tpr90_recall = 0.0
    tpr90_prec   = 0.0

# 2. Largest threshold where recall == 1.0
recall1_mask = all_rec >= 1.0
if recall1_mask.any():
    # Max threshold still giving recall=1.0 → highest precision while catching all
    best_r1_idx  = np.argmax(all_thr[recall1_mask])
    r1_thr       = all_thr[recall1_mask][best_r1_idx]
    r1_prec      = all_prec[recall1_mask][best_r1_idx]
    r1_rec       = all_rec[recall1_mask][best_r1_idx]
    print(f"\n[RECALL=1.0]: Highest threshold where recall=100%")
    print(f"  Threshold : {r1_thr:.4f}")
    print(f"  Precision : {r1_prec:.4f}  ({r1_prec:.1%} precision — needs to be >90%)")
    print(f"  Predicted positives: {(y_prob >= r1_thr).sum() if r1_thr is not None else 'N/A'}")
    print(f"  Gap from target: precision needs {0.90 - r1_prec:.4f} more")
else:
    r1_thr  = None
    r1_prec = None
    print("\n[RECALL=1.0]: Cannot achieve recall=1.0 at any threshold")

# 3. Full sweep report (every 5% threshold)
print("\n\nFULL THRESHOLD SWEEP (representative points):")
print(f"{'Threshold':>10} | {'Recall':>8} | {'Precision':>10} | {'TP':>4} | {'FP':>4} | {'FN':>4} | {'Passes?':>8}")
print("-" * 65)
for thr in [0.01, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60, 0.70, 0.80, 0.90]:
    pred = (y_prob >= thr).astype(int)
    tp   = ((pred == 1) & (y_true == 1)).sum()
    fp   = ((pred == 1) & (y_true == 0)).sum()
    fn   = ((pred == 0) & (y_true == 1)).sum()
    p    = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    r    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    passes = "YES" if (r >= 1.0 and p >= 0.90) else ("RECALL" if r >= 1.0 else ("PREC" if p >= 0.90 else "MISS"))
    print(f"{thr:>10.2f} | {r:>8.3f} | {p:>10.3f} | {tp:>4} | {fp:>4} | {fn:>4} | {passes:>8}")

# ── Decision logic ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("PRODUCTION THRESHOLD DECISION")
print("=" * 60)

# Strategy: primary goal is recall, precision is constraint
# Given the hard imbalance, we'll use the threshold that gives highest recall at prec>=0.90
# If no threshold achieves prec>=0.90 AND recall=1.0, we use the recall-maximizing threshold

if tpr90_thr is not None and tpr90_recall >= 1.0:
    chosen_thr = tpr90_thr
    rationale  = f"Both criteria met: recall=1.0, precision={tpr90_prec:.3f}>=0.90"
    criteria_met = True
elif tpr90_thr is not None:
    chosen_thr = tpr90_thr
    rationale  = f"Max recall at prec>=0.90 constraint: recall={tpr90_recall:.3f}, precision={tpr90_prec:.3f}. Gap: need {1.0-tpr90_recall:.3f} more recall."
    criteria_met = False
elif r1_thr is not None:
    # The ultra-low threshold catches all defects but precision is near base rate.
    # This causes test set collapse (all rows flagged). Use thr=0.02 instead:
    # OOF recall=0.924 @ precision=0.078 — best recall achievable without flagging everything on test.
    chosen_thr   = 0.02
    _pred_02     = (y_prob >= 0.02).astype(int)
    _rec_02      = recall_score(y_true, _pred_02, zero_division=0)
    _prec_02     = precision_score(y_true, _pred_02, zero_division=0)
    rationale    = (
        f"Recall=1.0 at thr=0.0028 BUT test proba floor=0.0168 causes all-positive collapse. "
        f"Using thr=0.02 instead: OOF recall={_rec_02:.3f}, precision={_prec_02:.3f}. "
        f"Test positives ~17%. Prioritize recall, accept precision gap — v2 will close it."
    )
    criteria_met = False
else:
    # Use very low threshold to maximize recall
    chosen_thr = all_thr[np.argmax(all_rec)]
    rationale  = "No clean solution. Using minimum threshold to maximize recall."
    criteria_met = False

chosen_pred  = (y_prob >= chosen_thr).astype(int)
chosen_rec   = recall_score(y_true, chosen_pred, zero_division=0)
chosen_prec  = precision_score(y_true, chosen_pred, zero_division=0)
chosen_tp    = ((chosen_pred == 1) & (y_true == 1)).sum()
chosen_fp    = ((chosen_pred == 1) & (y_true == 0)).sum()
chosen_fn    = ((chosen_pred == 0) & (y_true == 1)).sum()

print(f"\n  Chosen threshold : {chosen_thr:.4f}")
print(f"  Recall           : {chosen_rec:.4f}  (TP={chosen_tp}, FN={chosen_fn})")
print(f"  Precision        : {chosen_prec:.4f}  (FP={chosen_fp})")
print(f"  Criteria met     : {criteria_met}")
print(f"  Rationale        : {rationale}")

# ── Plot ───────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Left: Precision-Recall curve
axes[0].plot(rec_curve, prec_curve, "b-", lw=2, label="Precision-Recall curve")
axes[0].axhline(0.90, color="red", linestyle="--", lw=1.5, label="Precision=0.90 target")
axes[0].axvline(1.0,  color="green", linestyle="--", lw=1.5, label="Recall=1.0 target")
axes[0].scatter([chosen_rec], [chosen_prec], c="orange", s=150, zorder=5, label=f"Chosen (thr={chosen_thr:.3f})")
if r1_thr is not None:
    axes[0].scatter([r1_rec], [r1_prec], c="purple", s=150, zorder=5, marker="^", label=f"Recall=1.0 point (prec={r1_prec:.3f})")
axes[0].set_xlabel("Recall")
axes[0].set_ylabel("Precision")
axes[0].set_title("OOF Precision-Recall Curve")
axes[0].legend(fontsize=9)
axes[0].set_xlim([0, 1.05])
axes[0].set_ylim([0, 1.05])
axes[0].grid(True, alpha=0.3)

# Right: Recall and Precision vs Threshold
axes[1].plot(all_thr, all_rec,  "b-",  lw=2, label="Recall")
axes[1].plot(all_thr, all_prec, "r-",  lw=2, label="Precision")
axes[1].axhline(0.90, color="red",   linestyle="--", lw=1, alpha=0.7, label="Precision=0.90 target")
axes[1].axhline(1.00, color="blue",  linestyle="--", lw=1, alpha=0.7, label="Recall=1.0 target")
axes[1].axvline(chosen_thr, color="orange", linestyle="--", lw=2, label=f"Chosen thr={chosen_thr:.3f}")
axes[1].set_xlabel("Threshold")
axes[1].set_ylabel("Score")
axes[1].set_title("Recall & Precision vs Threshold")
axes[1].legend(fontsize=9)
axes[1].set_xlim([0, 1])
axes[1].set_ylim([0, 1.05])
axes[1].grid(True, alpha=0.3)

plt.suptitle(f"OOF Threshold Analysis — AUC={roc_auc_score(y_true, y_prob):.4f}", fontsize=13)
plt.tight_layout()
plt.savefig(FIG_DIR / "recall_precision_curve.png", dpi=120, bbox_inches="tight")
plt.close()
print(f"\nFigure saved: {FIG_DIR / 'recall_precision_curve.png'}")

# ── Save chosen threshold ──────────────────────────────────────────────────────
threshold_doc = {
    "chosen_threshold": float(chosen_thr),
    "chosen_recall": float(chosen_rec),
    "chosen_precision": float(chosen_prec),
    "tp": int(chosen_tp),
    "fp": int(chosen_fp),
    "fn": int(chosen_fn),
    "criteria_met": criteria_met,
    "rationale": rationale,
    "target_recall": 1.0,
    "target_precision": 0.90,
    "oof_auc": float(roc_auc_score(y_true, y_prob)),
    "recall_at_r1_0": {
        "threshold": float(r1_thr) if r1_thr else None,
        "precision": float(r1_prec) if r1_prec else None,
    },
    "max_recall_at_prec90": {
        "threshold": float(tpr90_thr) if tpr90_thr else None,
        "recall": float(tpr90_recall),
        "precision": float(tpr90_prec),
    },
}

(OUT_DIR / "chosen_threshold.json").write_text(json.dumps(threshold_doc, indent=2))
print(f"Threshold saved: {OUT_DIR / 'chosen_threshold.json'}")
print()
print("Step 4 complete.")
