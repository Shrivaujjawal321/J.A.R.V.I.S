"""
Step 5: Score-Aware Threshold Optimization
- Sweep thresholds 0.01 - 0.99 on OOF meta probas
- Metric: (recall + precision) / 2 * 100  (matches HackerEarth leaderboard formula)
- Find T* maximizing this metric
- Also compute T_balanced (|recall - precision| minimized) and T_v2_style (recall=1.0)
- Plot score-vs-threshold curve
- Save chosen_threshold_v3.json with full comparison table
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import recall_score, precision_score, roc_auc_score

BASE = "/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1"
V3   = BASE + "/build_v3"

print("Loading OOF meta predictions...")
oof = pd.read_parquet(V3 + "/oof_meta.parquet")
y_true  = oof["Y"].values
y_proba = oof["oof_proba"].values

n_pos = int(y_true.sum())
n_all = len(y_true)
print(f"  OOF samples: {n_all}  |  Positives: {n_pos}  |  Prevalence: {n_pos/n_all*100:.1f}%")
print(f"  AUC: {roc_auc_score(y_true, y_proba):.4f}")
print(f"  Proba range: [{y_proba.min():.4f}, {y_proba.max():.4f}]")

# ── Threshold sweep ──────────────────────────────────────────────────────────
thresholds  = np.linspace(0.01, 0.99, 198)
scores      = []
recalls     = []
precisions  = []
n_positives = []

for t in thresholds:
    y_pred = (y_proba >= t).astype(int)
    r = recall_score(y_true, y_pred, zero_division=0)
    p = precision_score(y_true, y_pred, zero_division=0)
    s = (r + p) / 2 * 100
    scores.append(s)
    recalls.append(r)
    precisions.append(p)
    n_positives.append(int(y_pred.sum()))

scores     = np.array(scores)
recalls    = np.array(recalls)
precisions = np.array(precisions)

# ── Find optimal thresholds ──────────────────────────────────────────────────
# T_max_score: maximizes (R+P)/2 * 100
best_idx       = int(np.argmax(scores))
T_max_score    = float(thresholds[best_idx])
best_score     = float(scores[best_idx])
best_recall    = float(recalls[best_idx])
best_precision = float(precisions[best_idx])
best_n_pos     = n_positives[best_idx]

# T_balanced: minimize |recall - precision| (closest to recall=precision)
balance_diff = np.abs(recalls - precisions)
bal_idx        = int(np.argmin(balance_diff))
T_balanced     = float(thresholds[bal_idx])

# T_v2_style: highest threshold where recall >= 0.88 (v2-like high recall)
v2_recall_thresh = 0.88
v2_eligible = np.where(recalls >= v2_recall_thresh)[0]
if len(v2_eligible) > 0:
    # Pick highest threshold in that set (best precision among high-recall configs)
    T_v2_style = float(thresholds[v2_eligible[-1]])
    v2_idx     = v2_eligible[-1]
else:
    T_v2_style = 0.001
    v2_idx     = 0

print(f"\n{'='*60}")
print("THRESHOLD COMPARISON:")
print(f"{'Strategy':<20} {'T':>6} {'Score':>7} {'Recall':>7} {'Prec':>7} {'N_pos':>6}")
print("-"*60)

for label, idx, T in [
    ("T_max_score",   best_idx, T_max_score),
    ("T_balanced",    bal_idx,  T_balanced),
    ("T_v2_style",    v2_idx,   T_v2_style),
]:
    r = recalls[idx]
    p = precisions[idx]
    s = scores[idx]
    n = n_positives[idx]
    print(f"  {label:<18} {T:>6.3f} {s:>7.2f} {r:>7.3f} {p:>7.3f} {n:>6}")

print("-"*60)
print(f"\nCHOSEN: T_max_score = {T_max_score:.3f}")
print(f"  Predicted LB score: {best_score:.2f}")
print(f"  OOF Recall:         {best_recall:.4f}  ({best_recall*100:.1f}%)")
print(f"  OOF Precision:      {best_precision:.4f}  ({best_precision*100:.1f}%)")
print(f"  Test positive rate (estimated from OOF rate): {best_n_pos}/{n_all} = {best_n_pos/n_all*100:.1f}%")

# ── Save chosen_threshold_v3.json ────────────────────────────────────────────
result = {
    "chosen_threshold":    T_max_score,
    "strategy":            "maximize_(recall+precision)/2",
    "predicted_lb_score":  best_score,
    "oof_recall":          best_recall,
    "oof_precision":       best_precision,
    "oof_n_positives":     best_n_pos,
    "oof_total":           n_all,
    "oof_positive_rate":   best_n_pos / n_all,
    "comparison": {
        "T_max_score": {
            "threshold": T_max_score,
            "score":     float(scores[best_idx]),
            "recall":    float(recalls[best_idx]),
            "precision": float(precisions[best_idx]),
            "n_pos":     int(n_positives[best_idx]),
        },
        "T_balanced": {
            "threshold": T_balanced,
            "score":     float(scores[bal_idx]),
            "recall":    float(recalls[bal_idx]),
            "precision": float(precisions[bal_idx]),
            "n_pos":     int(n_positives[bal_idx]),
        },
        "T_v2_style": {
            "threshold": T_v2_style,
            "score":     float(scores[v2_idx]),
            "recall":    float(recalls[v2_idx]),
            "precision": float(precisions[v2_idx]),
            "n_pos":     int(n_positives[v2_idx]),
        },
    },
    "v2_lb_score_for_reference": 50.19,
    "delta_vs_v2":  best_score - 50.19,
    "top10_target": 70.0,
    "on_track_for_top10": best_score >= 70.0,
}
with open(V3 + "/chosen_threshold_v3.json", "w") as f:
    json.dump(result, f, indent=2)
print(f"\nSaved chosen_threshold_v3.json")

# ── Score vs threshold plot ───────────────────────────────────────────────────
fig, axes = plt.subplots(2, 1, figsize=(12, 10))

ax1 = axes[0]
ax1.plot(thresholds, scores, color="steelblue", lw=2, label="(R+P)/2 × 100")
ax1.axvline(T_max_score, color="red",    ls="--", label=f"T_max_score={T_max_score:.3f} (LB≈{best_score:.1f})")
ax1.axvline(T_balanced,  color="orange", ls="--", label=f"T_balanced={T_balanced:.3f}")
ax1.axvline(T_v2_style,  color="gray",   ls="--", label=f"T_v2_style={T_v2_style:.3f}")
ax1.axhline(70, color="green", ls=":", lw=1.5, label="Top-10 target (70)")
ax1.axhline(50.19, color="purple", ls=":", lw=1.5, label="V2 score (50.19)")
ax1.set_xlabel("Threshold")
ax1.set_ylabel("LB Score (R+P)/2 × 100")
ax1.set_title("Score vs Threshold (OOF Meta Predictions)")
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)
ax1.set_xlim(0, 1)

ax2 = axes[1]
ax2.plot(thresholds, recalls,    color="blue",   lw=2, label="Recall")
ax2.plot(thresholds, precisions, color="orange", lw=2, label="Precision")
ax2.axvline(T_max_score, color="red", ls="--", lw=1.5, label=f"T*={T_max_score:.3f}")
ax2.set_xlabel("Threshold")
ax2.set_ylabel("Metric")
ax2.set_title("Recall & Precision vs Threshold")
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_xlim(0, 1)
ax2.set_ylim(0, 1.05)

plt.tight_layout()
plt.savefig(V3 + "/figures/score_curve.png", dpi=120)
plt.close()
print("Saved figures/score_curve.png")

# ── Also save sweep data as CSV for inspection ────────────────────────────────
sweep_df = pd.DataFrame({
    "threshold":  thresholds,
    "score":      scores,
    "recall":     recalls,
    "precision":  precisions,
    "n_positive": n_positives,
})
sweep_df.to_csv(V3 + "/threshold_sweep_v3.csv", index=False)
print("Saved threshold_sweep_v3.csv")

print(f"\n{'='*60}")
print(f"PREDICTED LB SCORE V3: {best_score:.2f}")
print(f"DELTA vs V2 (50.19):   {best_score - 50.19:+.2f}")
print(f"TOP 10 TARGET (70.0):  {'ON TRACK' if best_score >= 70 else 'NOT YET -- see V4 ideas'}")
print(f"{'='*60}")

print("\n=== Step 5 COMPLETE ===")
