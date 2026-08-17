"""
Step 3: Threshold tuning on OOF v2 predictions.
Sweeps thresholds to find:
  - T_a: precision >= 0.90, report recall
  - T_b: recall = 1.0, report precision
Saves chosen_threshold_v2.json + recall-precision plot.
Run: .venv/bin/python data/hackathons/tata-steel-2026/round_1/build_v2/03_threshold_tune.py
"""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve, roc_auc_score

V2_DIR = "data/hackathons/tata-steel-2026/round_1/build_v2"

print("=" * 60)
print("STEP 3: Threshold tuning on OOF v2")
print("=" * 60)

oof = pd.read_parquet(f"{V2_DIR}/oof_v2.parquet")
y        = oof["Y"].values.astype(int)
oof_prob = oof["oof_proba"].values

oof_auc = roc_auc_score(y, oof_prob)
print(f"OOF AUC: {oof_auc:.4f}")

# ─── Full precision-recall curve ──────────────────────────────────────────────
precision_arr, recall_arr, thr_arr = precision_recall_curve(y, oof_prob)

# Drop last point (sklearn appends recall=0, prec=1, no threshold)
precision_arr = precision_arr[:-1]
recall_arr    = recall_arr[:-1]

print(f"Sweep: {len(thr_arr)} thresholds from {thr_arr.min():.4f} to {thr_arr.max():.4f}")

# ─── Find T_a: highest threshold where precision >= 0.90 ─────────────────────
# (highest threshold = fewest positives predicted = best precision but lowest recall)
mask_prec90 = precision_arr >= 0.90
if mask_prec90.any():
    # Among thresholds achieving P>=0.90, find max recall
    recall_at_prec90   = recall_arr[mask_prec90].max()
    best_idx_prec90    = np.where(mask_prec90)[0][np.argmax(recall_arr[mask_prec90])]
    T_a                = float(thr_arr[best_idx_prec90])
    prec_at_T_a        = float(precision_arr[best_idx_prec90])
    print(f"\nT_a (P>=0.90): threshold={T_a:.4f}  recall={recall_at_prec90:.4f}  precision={prec_at_T_a:.4f}")
else:
    T_a = None
    recall_at_prec90 = 0.0
    print(f"\nT_a (P>=0.90): NOT ACHIEVABLE on OOF (precision ceiling < 90%)")
    # Report best achievable precision and at what recall
    best_prec = precision_arr.max()
    best_prec_recall = recall_arr[np.argmax(precision_arr)]
    print(f"  Max OOF precision achievable: {best_prec:.4f} at recall={best_prec_recall:.4f}")

# ─── Find T_b: lowest threshold where recall = 1.0 ───────────────────────────
mask_r1 = recall_arr >= 1.0
if mask_r1.any():
    # Highest threshold still achieving recall=1.0 (= best precision at full recall)
    best_idx_r1  = np.where(mask_r1)[0][np.argmax(precision_arr[mask_r1])]
    T_b          = float(thr_arr[best_idx_r1])
    prec_at_r1   = float(precision_arr[best_idx_r1])
    print(f"T_b (R=1.0):   threshold={T_b:.4f}  recall=1.000  precision={prec_at_r1:.4f}")
else:
    # Recall never quite reaches 1.0 due to floating point — find closest
    max_recall = recall_arr.max()
    best_idx_r1 = np.argmax(recall_arr)
    T_b          = float(thr_arr[best_idx_r1])
    prec_at_r1   = float(precision_arr[best_idx_r1])
    print(f"T_b (max recall): threshold={T_b:.4f}  recall={max_recall:.4f}  precision={prec_at_r1:.4f}")

# ─── Sweep for PR table ───────────────────────────────────────────────────────
print("\nPrecision-Recall at key thresholds:")
print(f"{'Threshold':>12}  {'Recall':>8}  {'Precision':>10}  {'TP':>5}  {'FP':>6}  {'FN':>5}")
print("-" * 60)

for thr in [0.001, 0.005, 0.01, 0.02, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50]:
    pred = (oof_prob >= thr).astype(int)
    tp   = int(((pred==1)&(y==1)).sum())
    fp   = int(((pred==1)&(y==0)).sum())
    fn   = int(((pred==0)&(y==1)).sum())
    rec  = tp / (tp + fn) if (tp+fn)>0 else 0.0
    pre  = tp / (tp + fp) if (tp+fp)>0 else 0.0
    mark = " <-- CRITERIA MET" if (rec >= 1.0 and pre >= 0.90) else \
           " <-- R=1.0" if rec >= 1.0 else \
           " <-- P>=0.90" if pre >= 0.90 else ""
    print(f"{thr:>12.3f}  {rec:>8.4f}  {pre:>10.4f}  {tp:>5d}  {fp:>6d}  {fn:>5d}{mark}")

# ─── Determine chosen threshold ───────────────────────────────────────────────
CRITERIA_MET = False
chosen_threshold = None
chosen_recall    = None
chosen_precision = None
rationale        = ""

# Priority: find threshold meeting BOTH criteria (R>=1.0 AND P>=0.90)
for thr_val in np.sort(thr_arr)[::-1]:  # from high to low
    pred = (oof_prob >= thr_val).astype(int)
    tp = ((pred==1)&(y==1)).sum()
    fp = ((pred==1)&(y==0)).sum()
    fn = ((pred==0)&(y==1)).sum()
    rec = tp/(tp+fn) if (tp+fn)>0 else 0.0
    pre = tp/(tp+fp) if (tp+fp)>0 else 1.0
    if rec >= 1.0 and pre >= 0.90:
        CRITERIA_MET = True
        chosen_threshold = float(thr_val)
        chosen_recall    = float(rec)
        chosen_precision = float(pre)
        rationale = "Both criteria met: Recall=1.0 AND Precision>=0.90"
        break

if not CRITERIA_MET:
    # Fall back: max recall at best achievable precision
    # Try to find best P at recall >= 0.95 first, then R=max
    for min_rec in [1.0, 0.97, 0.95, 0.90, 0.85]:
        mask = recall_arr >= min_rec
        if mask.any():
            best_i = np.where(mask)[0][np.argmax(precision_arr[mask])]
            chosen_threshold = float(thr_arr[best_i])
            chosen_recall    = float(recall_arr[best_i])
            chosen_precision = float(precision_arr[best_i])
            rationale = (f"Criteria NOT met. Best precision={chosen_precision:.4f} "
                         f"at recall>={min_rec:.2f}. Criteria needs R=1.0 AND P>=0.90.")
            break

print(f"\nCHOSEN THRESHOLD: {chosen_threshold:.4f}")
print(f"  Recall:    {chosen_recall:.4f}")
print(f"  Precision: {chosen_precision:.4f}")
print(f"  Rationale: {rationale}")
print(f"  CRITERIA MET: {CRITERIA_MET}")

# ─── Plot ──────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: PR curve
ax = axes[0]
ax.plot(recall_arr, precision_arr, "b-", lw=2, label=f"V2 (AUC={oof_auc:.3f})")
ax.axhline(0.90, color="red", ls="--", alpha=0.7, label="P=0.90 target")
ax.axvline(1.00, color="green", ls="--", alpha=0.7, label="R=1.0 target")
if CRITERIA_MET:
    ax.scatter([chosen_recall], [chosen_precision], s=200, c="orange", zorder=5,
               label=f"Chosen (T={chosen_threshold:.3f})")
ax.set_xlabel("Recall"); ax.set_ylabel("Precision")
ax.set_title("OOF Precision-Recall Curve (V2)")
ax.legend(loc="upper right"); ax.grid(alpha=0.3)
ax.set_xlim([0,1]); ax.set_ylim([0,1.05])

# Right: Threshold sweep (recall + precision vs threshold)
ax2 = axes[1]
thrs_plot = np.linspace(thr_arr.min(), 0.5, 300)
recs_plot, precs_plot = [], []
for t in thrs_plot:
    p = (oof_prob >= t).astype(int)
    tp = ((p==1)&(y==1)).sum(); fp = ((p==1)&(y==0)).sum(); fn = ((p==0)&(y==1)).sum()
    recs_plot.append(tp/(tp+fn) if (tp+fn)>0 else 0.0)
    precs_plot.append(tp/(tp+fp) if (tp+fp)>0 else 1.0)
ax2.plot(thrs_plot, recs_plot,  "g-", lw=2, label="Recall")
ax2.plot(thrs_plot, precs_plot, "b-", lw=2, label="Precision")
ax2.axhline(0.90, color="red", ls="--", alpha=0.5, label="P=0.90 target")
ax2.axvline(chosen_threshold, color="orange", ls="--", lw=2,
            label=f"Chosen T={chosen_threshold:.3f}")
ax2.set_xlabel("Threshold"); ax2.set_ylabel("Score")
ax2.set_title("Recall & Precision vs Threshold (V2)")
ax2.legend(); ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(f"{V2_DIR}/figures/recall_precision_v2.png", dpi=120, bbox_inches="tight")
print(f"\nSaved figures/recall_precision_v2.png")

# ─── Save threshold decision ───────────────────────────────────────────────────
decision = {
    "chosen_threshold": chosen_threshold,
    "chosen_recall":    chosen_recall,
    "chosen_precision": chosen_precision,
    "criteria_met":     CRITERIA_MET,
    "rationale":        rationale,
    "T_a_prec90":       {"threshold": T_a, "recall": float(recall_at_prec90)} if T_a else None,
    "T_b_recall1":      {"threshold": T_b, "precision": float(prec_at_r1)},
    "oof_auc":          float(oof_auc),
}
json.dump(decision, open(f"{V2_DIR}/chosen_threshold_v2.json","w"), indent=2)
print(f"Saved chosen_threshold_v2.json")
print("Step 3 DONE.")
