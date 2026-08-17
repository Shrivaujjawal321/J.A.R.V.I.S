"""
V20 Track 2 -- NCA-learned metric + distance-weighted KNN
NCA learns a linear projection maximising KNN classification accuracy
Then KNN with distance weights in the learned space
5-fold OOF, full threshold sweep, gate applied
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier, NeighborhoodComponentsAnalysis
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

BASE = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1")
V5_DIR = BASE / "build_v5"
V20_DIR = BASE / "build_v20"

# Load data
train = pd.read_parquet(V5_DIR / "train_v5.parquet")
test  = pd.read_parquet(V5_DIR / "test_v5.parquet")
oof   = pd.read_parquet(V5_DIR / "oof_v5.parquet")

feat_list = json.load(open(V5_DIR / "feature_list_v5.json"))["features"]

X_train = train[feat_list].values.astype(np.float64)
y_train = oof["Y"].values
X_test  = test[feat_list].values.astype(np.float64)

print(f"Train: {X_train.shape}, Test: {X_test.shape}")
print(f"Positives: {y_train.sum()} / {len(y_train)}  ({y_train.mean():.4f})")

# Gate mask
x42_train = train["X42"].values if "X42" in train.columns else None
x39_train = train["X39"].values if "X39" in train.columns else None
x42_test  = test["X42"].values  if "X42" in test.columns  else None
x39_test  = test["X39"].values  if "X39" in test.columns  else None

def gate_mask(x42, x39, n):
    mask = np.ones(n, dtype=bool)
    if x42 is not None:
        mask &= (x42 <= 0.025067)
    if x39 is not None:
        mask &= (x39 < 169)
    return mask

gate_train = gate_mask(x42_train, x39_train, len(X_train))
gate_test  = gate_mask(x42_test,  x39_test,  len(X_test))

# NCA pipeline
# n_components=20 captures most variance while making KNN tractable
# NCA max_iter=300 enough for convergence on 1352 rows
pipe = Pipeline([
    ("scale", StandardScaler()),
    ("nca",   NeighborhoodComponentsAnalysis(
                  n_components=20,
                  random_state=42,
                  max_iter=300,
                  verbose=1)),
    ("knn",   KNeighborsClassifier(n_neighbors=15, weights="distance")),
])

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
oof_nca = np.zeros(len(X_train))
fold_aucs = []

print("\n--- NCA-KNN 5-Fold CV ---")
for fold, (tr_idx, val_idx) in enumerate(cv.split(X_train, y_train)):
    X_tr, X_val = X_train[tr_idx], X_train[val_idx]
    y_tr, y_val = y_train[tr_idx], y_train[val_idx]
    print(f"\nFold {fold+1}: train={len(X_tr)}, val={len(X_val)}, pos_train={y_tr.sum()}")
    pipe.fit(X_tr, y_tr)
    proba = pipe.predict_proba(X_val)[:, 1]
    oof_nca[val_idx] = proba
    auc = roc_auc_score(y_val, proba)
    fold_aucs.append(auc)
    print(f"Fold {fold+1}: AUC={auc:.4f}")

nca_oof_auc = roc_auc_score(y_train, oof_nca)
print(f"\nNCA-KNN OOF AUC: {nca_oof_auc:.4f}  (V5 baseline: 0.8886)")
print(f"Fold AUCs: {[round(a,4) for a in fold_aucs]}")

# Full train fit for test
print("\nFitting full pipeline on entire train set...")
pipe.fit(X_train, y_train)
test_proba_nca = pipe.predict_proba(X_test)[:, 1]

# Apply gate
oof_gated  = oof_nca.copy();  oof_gated[~gate_train]  = 0.0
test_gated = test_proba_nca.copy(); test_gated[~gate_test] = 0.0

# Threshold sweep (scoring = (Recall + Precision)/2 * 100)
def score_threshold(y_true, y_prob, t):
    pred = (y_prob >= t).astype(int)
    tp = ((pred == 1) & (y_true == 1)).sum()
    fp = ((pred == 1) & (y_true == 0)).sum()
    fn = ((pred == 0) & (y_true == 1)).sum()
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    prec   = tp / (tp + fp) if (tp + fp) > 0 else 0
    return (recall + prec) / 2 * 100, recall, prec

thresholds = np.linspace(0.005, 0.3, 200)
best_score, best_t, best_recall, best_prec = 0, 0.05, 0, 0
rows = []
for t in thresholds:
    sc, rec, prec = score_threshold(y_train, oof_gated, t)
    rows.append({"threshold": t, "score": sc, "recall": rec, "precision": prec,
                 "n_pos": int((oof_gated >= t).sum())})
    if sc > best_score:
        best_score, best_t, best_recall, best_prec = sc, t, rec, prec

print(f"\nBest OOF score: {best_score:.4f} @ threshold={best_t:.4f}")
print(f"Recall={best_recall:.4f}, Precision={best_prec:.4f}")
print(f"N predictions (test): {int((test_gated >= best_t).sum())}")

# Calibration: V4/V13 delta ~+2.7; DO NOT apply to NCA (unknown)
# Just report raw OOF -> est LB range
est_lb_low  = best_score + 0.0   # pessimistic: no uplift
est_lb_high = best_score + 2.7   # optimistic: same uplift as V4
print(f"Estimated LB: {est_lb_low:.2f} -- {est_lb_high:.2f}")

# Build submission
sub = test[["CoilID"]].copy()
sub["Defect Flag"] = (test_gated >= best_t).astype(int)
n_pos = sub["Defect Flag"].sum()
print(f"Submission positives: {n_pos}")

# Save
sweep_df = pd.DataFrame(rows)
sweep_df.to_csv(V20_DIR / "threshold_sweep_nca.csv", index=False)
sub.to_csv(V20_DIR / "submission_nca.csv", index=False)
np.save(V20_DIR / "oof_nca.npy", oof_nca)
np.save(V20_DIR / "test_nca.npy", test_proba_nca)

result2 = {
    "track": "nca_knn",
    "success": True,
    "oof_auc": float(nca_oof_auc),
    "v5_baseline_auc": 0.8886,
    "delta_vs_v5": float(nca_oof_auc - 0.8886),
    "fold_aucs": [float(a) for a in fold_aucs],
    "best_oof_score": float(best_score),
    "best_threshold": float(best_t),
    "best_recall": float(best_recall),
    "best_precision": float(best_prec),
    "n_pos_test": int(n_pos),
    "est_lb_low": float(est_lb_low),
    "est_lb_high": float(est_lb_high),
}
json.dump(result2, open(V20_DIR / "track2_result.json", "w"), indent=2)
print("\nTrack 2 saved:", json.dumps(result2, indent=2))
