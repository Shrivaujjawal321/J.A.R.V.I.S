"""
V68 — Unsupervised Anomaly Detection Ensemble (FINAL)
=====================================================
Hypothesis: defective coils = anomalies in feature space.
Strategy after diagnostic run: 5 detectors fit, but ECOD/LOF/DeepSVDD add noise.
Final ensemble: IsolationForest (3-seed bag) + COPOD, equal rank-average.
  - IsolationForest alone: AUC 0.7474, G2=28.8% recall, rho=0.539
  - ECOD alone: AUC 0.5989 (weak — drops ensemble AUC)
  - LOF alone: AUC 0.5294 (negative correlation — harmful)
  - DeepSVDD: AUC 0.5721 (loss plateau, not converging cleanly)
  - COPOD: AUC 0.6887 — good diversity additive
  - IF + COPOD equal: AUC 0.7312, G2=22.7%, rho=0.446 — ALL GATES PASS

NO LABELS used — purely distributional, robust to public/private LB split.
Train+test combined for detector fitting (test sees its own distribution).

Output:
  - test_proba_v68.parquet  (CoilID, test_score)
  - oof_v68.parquet         (CoilID, Y, v68_score, plus per-detector scores)
  - v68_metrics.json        (all gate results)
  - top30_test_v68.csv      (V70 consensus candidates)
"""

import os
import json
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import spearmanr
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")

# ── Paths ───────────────────────────────────────────────────────────────────
ROOT = Path("/home/ujjwal/Documents/J.A.R.V.I.S.")
R1   = ROOT / "data/hackathons/tata-steel-2026/round_1"
V4   = R1 / "build_v4"
OUT  = R1 / "build_v68"
OUT.mkdir(exist_ok=True)

SEED = 42

# ── 1. Load Data ─────────────────────────────────────────────────────────────
print("Loading data...")
train_raw = pd.read_parquet(V4 / "train_v4.parquet")
test_raw  = pd.read_parquet(V4 / "test_v4.parquet")

with open(V4 / "v4_final_features.json") as f:
    feats_meta = json.load(f)

FEATS = feats_meta["features"]  # 51 SHAP-selected features
print(f"  Train: {train_raw.shape}, Test: {test_raw.shape}, Features: {len(FEATS)}")

# Extract feature matrices
X_train = train_raw[FEATS].copy()
X_test  = test_raw[FEATS].copy()
y_train = train_raw["Y"].values.astype(int)
train_coils = train_raw["CoilID"].values
test_coils  = test_raw["CoilID"].values

print(f"  Train positives: {y_train.sum()} / {len(y_train)} ({y_train.mean()*100:.1f}%)")

# ── 2. Impute & Scale ────────────────────────────────────────────────────────
print("Imputing & scaling...")
train_medians = X_train.median()
X_train_imp = X_train.fillna(train_medians)
X_test_imp  = X_test.fillna(train_medians)

# Combine for anomaly fitting — unsupervised, so test sees its own distribution
X_combined = pd.concat([X_train_imp, X_test_imp], axis=0, ignore_index=True)
n_train = len(X_train_imp)
n_test  = len(X_test_imp)
print(f"  Combined: {X_combined.shape}")

# Standard scale (required for LOF/COPOD, consistent for IF)
scaler = StandardScaler()
X_combined_scaled = scaler.fit_transform(X_combined)
X_train_scaled = X_combined_scaled[:n_train]
X_test_scaled  = X_combined_scaled[n_train:]

# ── 3. Anomaly Detectors ─────────────────────────────────────────────────────
print("\nFitting anomaly detectors...")
detector_scores_train = {}
detector_scores_test  = {}
detector_aucs         = {}

# --- 3a. IsolationForest — 3-seed bag ---
print("  [1] IsolationForest (3-seed bag: 42, 137, 1000)...")
if_bags_train = []
if_bags_test  = []
for seed in [42, 137, 1000]:
    clf = IsolationForest(
        n_estimators=200,
        contamination="auto",
        random_state=seed,
        n_jobs=-1,
    )
    clf.fit(X_combined_scaled)
    # score_samples: higher = more normal → negate for anomaly score
    sc_train = -clf.score_samples(X_train_scaled)
    sc_test  = -clf.score_samples(X_test_scaled)
    if_bags_train.append(sc_train)
    if_bags_test.append(sc_test)

detector_scores_train["isoforest"] = np.mean(if_bags_train, axis=0)
detector_scores_test["isoforest"]  = np.mean(if_bags_test, axis=0)
auc_if = roc_auc_score(y_train, detector_scores_train["isoforest"])
detector_aucs["isoforest"] = auc_if
print(f"    AUC={auc_if:.4f}, range=[{detector_scores_train['isoforest'].min():.4f}, {detector_scores_train['isoforest'].max():.4f}]")

# --- 3b. COPOD ---
print("  [2] COPOD (copula-based, parameter-free)...")
from pyod.models.copod import COPOD
copod = COPOD(contamination=0.05, n_jobs=-1)
copod.fit(X_combined_scaled)
combined_copod = copod.decision_scores_
detector_scores_train["copod"] = combined_copod[:n_train]
detector_scores_test["copod"]  = combined_copod[n_train:]
auc_copod = roc_auc_score(y_train, detector_scores_train["copod"])
detector_aucs["copod"] = auc_copod
print(f"    AUC={auc_copod:.4f}, range=[{detector_scores_train['copod'].min():.4f}, {detector_scores_train['copod'].max():.4f}]")

# --- Also fit ECOD + LOF for audit (but exclude from final ensemble) ---
print("  [3] ECOD (audit only — not in final ensemble)...")
from pyod.models.ecod import ECOD
ecod = ECOD(contamination=0.05, n_jobs=-1)
ecod.fit(X_combined_scaled)
combined_ecod = ecod.decision_scores_
detector_scores_train["ecod"] = combined_ecod[:n_train]
detector_scores_test["ecod"]  = combined_ecod[n_train:]
auc_ecod = roc_auc_score(y_train, detector_scores_train["ecod"])
detector_aucs["ecod"] = auc_ecod
print(f"    AUC={auc_ecod:.4f} (excluded — drags ensemble down)")

print("  [4] LOF (audit only — not in final ensemble)...")
lof = LocalOutlierFactor(n_neighbors=20, contamination="auto", novelty=False, n_jobs=-1)
lof.fit(X_combined_scaled)
combined_lof = -lof.negative_outlier_factor_
detector_scores_train["lof"] = combined_lof[:n_train]
detector_scores_test["lof"]  = combined_lof[n_train:]
auc_lof = roc_auc_score(y_train, detector_scores_train["lof"])
detector_aucs["lof"] = auc_lof
print(f"    AUC={auc_lof:.4f} (excluded — negative contribution)")

# Final ensemble: IF + COPOD only
ENSEMBLE_DETECTORS = ["isoforest", "copod"]
print(f"\n  Final ensemble: {ENSEMBLE_DETECTORS}")

# ── 4. Rank Aggregation ──────────────────────────────────────────────────────
print("\nAggregating via rank averaging...")

def rank_normalize(scores):
    """Convert raw scores → rank percentile [0,1]. Higher = more anomalous."""
    n = len(scores)
    ranks = scores.argsort().argsort()
    return ranks / (n - 1)

# Train
train_rank_matrix = np.stack(
    [rank_normalize(detector_scores_train[d]) for d in ENSEMBLE_DETECTORS], axis=1
)
v68_train_score = train_rank_matrix.mean(axis=1)

# Test
test_rank_matrix = np.stack(
    [rank_normalize(detector_scores_test[d]) for d in ENSEMBLE_DETECTORS], axis=1
)
v68_test_score = test_rank_matrix.mean(axis=1)

print(f"  V68 train: mean={v68_train_score.mean():.4f}, std={v68_train_score.std():.4f}")
print(f"  V68 test:  mean={v68_test_score.mean():.4f}, std={v68_test_score.std():.4f}")

# ── 5. OOF Validation ────────────────────────────────────────────────────────
print("\n--- OOF VALIDATION (train rows, known Y) ---")

# Per-detector AUC
for d in ["isoforest", "copod", "ecod", "lof"]:
    tag = "" if d in ENSEMBLE_DETECTORS else " [excluded]"
    print(f"  {d:>12} AUC: {detector_aucs[d]:.4f}{tag}")

ensemble_auc = roc_auc_score(y_train, v68_train_score)
print(f"\n  {'ENSEMBLE':>12} AUC: {ensemble_auc:.4f} (IF + COPOD, equal rank-avg)")

# Gate 1: ensemble AUC > 0.65
gate1 = ensemble_auc > 0.65
print(f"\n[GATE 1] AUC {ensemble_auc:.4f} > 0.65: {'PASS' if gate1 else 'FAIL'}")

# Gate 2: top 10% of train rows by V68 score contains >= 20% of positives
n_top10pct = max(1, int(0.10 * n_train))
top10_idx = np.argsort(v68_train_score)[::-1][:n_top10pct]
n_pos_in_top10 = y_train[top10_idx].sum()
pct_pos_in_top10 = n_pos_in_top10 / y_train.sum()
print(f"\n[GATE 2] Top 10% ({n_top10pct} rows) → {n_pos_in_top10} positives "
      f"= {pct_pos_in_top10*100:.1f}% of all positives "
      f"(threshold >=20%): {'PASS' if pct_pos_in_top10 >= 0.20 else 'FAIL'}")
gate2 = pct_pos_in_top10 >= 0.20

# Recall@15% for reference
n_top15pct = max(1, int(0.15 * n_train))
top15_idx = np.argsort(v68_train_score)[::-1][:n_top15pct]
n_pos_in_top15 = y_train[top15_idx].sum()
pct_pos_in_top15 = n_pos_in_top15 / y_train.sum()
print(f"         Top 15% ({n_top15pct} rows) → {n_pos_in_top15} positives = {pct_pos_in_top15*100:.1f}% (reference)")

# Gate 3: Spearman vs V44 OOF meta score (0.30-0.70 window)
oof_v4 = pd.read_parquet(V4 / "oof_v4.parquet")
v44_oof_meta = oof_v4["oof_meta"].values
spearman_rho, spearman_p = spearmanr(v68_train_score, v44_oof_meta)
gate3 = 0.30 <= abs(spearman_rho) <= 0.70
print(f"\n[GATE 3] Spearman(V68, V44_meta) = {spearman_rho:.4f} (p={spearman_p:.4e}), "
      f"target [0.30, 0.70]: {'PASS' if gate3 else 'FAIL'}")
# Also check vs individual models
rho_lgb, _ = spearmanr(v68_train_score, oof_v4["oof_lgb"].values)
rho_xgb, _ = spearmanr(v68_train_score, oof_v4["oof_xgb"].values)
print(f"         Spearman vs oof_lgb={rho_lgb:.4f}, vs oof_xgb={rho_xgb:.4f} (reference)")

# Summary
print(f"\n{'='*55}")
print(f"GATES: G1={'PASS' if gate1 else 'FAIL'} | G2={'PASS' if gate2 else 'FAIL'} | G3={'PASS' if gate3 else 'FAIL'}")
all_gates = gate1 and gate2 and gate3
print(f"VERDICT: {'ALL PASS — V68 ready for V70 consensus' if all_gates else 'PARTIAL — review notes'}")
print(f"{'='*55}")

# ── 6. Output Files ──────────────────────────────────────────────────────────
print("\nWriting outputs...")

# Test predictions
test_out = pd.DataFrame({
    "CoilID": test_coils,
    "test_score": v68_test_score,
})
test_out.to_parquet(OUT / "test_proba_v68.parquet", index=False)
print(f"  Saved: {OUT / 'test_proba_v68.parquet'}")

# Train OOF with all scores
train_out = pd.DataFrame({
    "CoilID": train_coils,
    "Y": y_train,
    "v68_score": v68_train_score,
    "v68_rank_pct": rank_normalize(v68_train_score),
})
for d in ["isoforest", "copod", "ecod", "lof"]:
    train_out[f"rank_{d}"]  = rank_normalize(detector_scores_train[d])
    train_out[f"score_{d}"] = detector_scores_train[d]
train_out.to_parquet(OUT / "oof_v68.parquet", index=False)
print(f"  Saved: {OUT / 'oof_v68.parquet'}")

# Top 30 test rows by V68 anomaly score
top30_test = test_out.nlargest(30, "test_score").copy()
top30_test["rank"] = range(1, 31)
top30_test.to_csv(OUT / "top30_test_v68.csv", index=False)
print(f"  Saved: {OUT / 'top30_test_v68.csv'}")

# Metrics JSON
metrics = {
    "ensemble_detectors": ENSEMBLE_DETECTORS,
    "all_detectors_fit": ["isoforest", "copod", "ecod", "lof"],
    "per_detector_auc": detector_aucs,
    "ensemble_auc": float(ensemble_auc),
    "gate1_ensemble_auc_gt_065": bool(gate1),
    "gate2_recall_top10pct": {
        "n_top10": int(n_top10pct),
        "n_positives_in_top10": int(n_pos_in_top10),
        "pct_positives_captured": float(pct_pos_in_top10),
        "pass": bool(gate2),
    },
    "gate2_recall_top15pct": {
        "n_positives_in_top15": int(n_pos_in_top15),
        "pct_positives_captured": float(pct_pos_in_top15),
    },
    "gate3_spearman_v44": {
        "rho_meta": float(spearman_rho),
        "rho_lgb": float(rho_lgb),
        "rho_xgb": float(rho_xgb),
        "p": float(spearman_p),
        "pass": bool(gate3),
    },
    "all_gates_pass": bool(all_gates),
}
with open(OUT / "v68_metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)
print(f"  Saved: {OUT / 'v68_metrics.json'}")

# ── 7. Top 30 preview ───────────────────────────────────────────────────────
print("\n--- TOP 30 TEST COILS BY V68 ANOMALY SCORE ---")
print(top30_test[["rank", "CoilID", "test_score"]].to_string(index=False))

print("\nV68 complete.")
