#!/usr/bin/env python3
"""
V18 — AutoGluon best_quality deep search
Hard gate: X42 > 0.025067 OR X39 >= 169 → predict 0
Time limit: 2400s (40 min)
"""
import os, json, warnings, sys
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import roc_auc_score
from autogluon.tabular import TabularPredictor

warnings.filterwarnings("ignore")

BASE = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1")
V5   = BASE / "build_v5"
OUT  = BASE / "build_v18"
AG_PATH = str(OUT / "ag_models")

# ── Load data ─────────────────────────────────────────────────────────────────
print("[V18] Loading data...")
train = pd.read_parquet(V5 / "train_v5.parquet")
test  = pd.read_parquet(V5 / "test_v5.parquet")
with open(V5 / "feature_list_v5.json") as f:
    v5_features = json.load(f)["features"]

pos = int(train["Y"].sum())
n   = len(train)
print(f"[V18] Train: {train.shape}, positives: {pos}/{n} ({100*train['Y'].mean():.2f}%)")
print(f"[V18] Test : {test.shape}")
print(f"[V18] Features: {len(v5_features)}")

missing = [f for f in v5_features if f not in train.columns]
if missing:
    print(f"[V18] WARNING missing features: {missing}")
    v5_features = [f for f in v5_features if f in train.columns]

train_ag = train[v5_features + ["Y"]].copy()
test_ag  = test[v5_features].copy()

# ── AutoGluon fit ─────────────────────────────────────────────────────────────
print("[V18] Starting AutoGluon best_quality fit (40 min budget)...")
print(f"[V18] Models path: {AG_PATH}")

predictor = TabularPredictor(
    label="Y",
    eval_metric="roc_auc",
    path=AG_PATH,
    problem_type="binary",
    verbosity=2,
)

fit_kwargs = dict(
    train_data=train_ag,
    presets="best_quality",
    time_limit=2400,
    auto_stack=True,
    num_bag_folds=5,
    num_bag_sets=2,
    num_stack_levels=2,
    excluded_model_types=[],
)

try:
    predictor.fit(**fit_kwargs)
    print("[V18] best_quality fit complete")
except MemoryError as e:
    print(f"[V18] OOM on best_quality: {e}. Retrying high_quality no NN...")
    fit_kwargs["presets"] = "high_quality"
    fit_kwargs["excluded_model_types"] = ["NN_TORCH"]
    fit_kwargs["time_limit"] = 1200
    predictor = TabularPredictor(
        label="Y", eval_metric="roc_auc",
        path=AG_PATH + "_fallback",
        problem_type="binary", verbosity=2,
    )
    predictor.fit(**fit_kwargs)

# ── Leaderboard ───────────────────────────────────────────────────────────────
print("[V18] AutoGluon leaderboard:")
lb = predictor.leaderboard(train_ag, silent=False)
lb.to_csv(OUT / "ag_leaderboard_v18.csv", index=False)
print(lb.to_string())

# ── OOF probabilities ─────────────────────────────────────────────────────────
print("[V18] Getting OOF probabilities...")
oof_proba = None
y_true = train["Y"].values

try:
    oof_proba_df = predictor.predict_oof(as_multiclass=False)
    if isinstance(oof_proba_df, pd.DataFrame):
        oof_proba = oof_proba_df[1].values
    else:
        oof_proba = np.array(oof_proba_df)
    print(f"[V18] OOF proba shape: {oof_proba.shape}")
except Exception as e:
    print(f"[V18] predict_oof failed: {e}")
    # Try predict_proba on OOF via transform_features
    oof_proba = None

if oof_proba is not None and len(oof_proba) == len(train):
    # Clip NaNs
    oof_proba = np.nan_to_num(oof_proba, nan=0.0)
    oof_auc = roc_auc_score(y_true, oof_proba)
    print(f"[V18] OOF AUC (ensemble): {oof_auc:.5f}")
    print(f"[V18] V5 baseline AUC:    0.88860")
    print(f"[V18] Delta:              {oof_auc - 0.88860:+.5f}")
    pd.DataFrame({"y_true": y_true, "oof_proba": oof_proba}).to_parquet(OUT / "oof_v18.parquet", index=False)
else:
    print("[V18] OOF proba unavailable — will use leaderboard score")
    oof_auc = float(lb.iloc[0].get("score_val", 0.0))
    print(f"[V18] Best model val AUC: {oof_auc:.5f}")

# ── Test predictions ──────────────────────────────────────────────────────────
print("[V18] Getting test predictions...")
test_proba_df = predictor.predict_proba(test_ag)
if isinstance(test_proba_df, pd.DataFrame):
    test_proba = test_proba_df[1].values
else:
    test_proba = np.array(test_proba_df)
test_proba = np.nan_to_num(test_proba, nan=0.0)

# ── Hard gate ─────────────────────────────────────────────────────────────────
print("[V18] Applying hard gate...")
gate_mask = (test["X42"].values > 0.025067) | (test["X39"].values >= 169)
print(f"[V18] Gate zeroed: {gate_mask.sum()} / {len(test)} rows")
test_proba_gated = test_proba.copy()
test_proba_gated[gate_mask] = 0.0

# ── Threshold sweep ───────────────────────────────────────────────────────────
best_score, best_T, best_R, best_P = 0.0, 0.5, 0.0, 0.0

if oof_proba is not None:
    print("[V18] Threshold sweep...")
    thresholds = np.linspace(0.001, 0.999, 1000)
    rows = []
    for T in thresholds:
        preds = (oof_proba >= T).astype(int)
        tp = int(((preds == 1) & (y_true == 1)).sum())
        fp = int(((preds == 1) & (y_true == 0)).sum())
        fn = int(((preds == 0) & (y_true == 1)).sum())
        recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        score = (recall + precision) / 2 * 100
        rows.append({"T": T, "score": score, "recall": recall, "precision": precision,
                     "n_pos": int(preds.sum()), "tp": tp, "fp": fp, "fn": fn})
        if score > best_score:
            best_score, best_T, best_R, best_P = score, T, recall, precision

    pd.DataFrame(rows).to_csv(OUT / "threshold_sweep_v18.csv", index=False)
    print(f"[V18] Best OOF score:  {best_score:.4f}")
    print(f"[V18] Threshold:       {best_T:.5f}")
    print(f"[V18] Recall:          {best_R:.4f}")
    print(f"[V18] Precision:       {best_P:.4f}")
    print(f"[V18] Test positives:  {int((test_proba_gated >= best_T).sum())}")

    # Bootstrap 95% CI
    np.random.seed(42)
    boot_scores = []
    idx_all = np.arange(len(y_true))
    for _ in range(2000):
        idx_b = np.random.choice(idx_all, size=len(idx_all), replace=True)
        y_b = y_true[idx_b]; p_b = (oof_proba[idx_b] >= best_T).astype(int)
        tp_b = int(((p_b==1)&(y_b==1)).sum()); fp_b = int(((p_b==1)&(y_b==0)).sum()); fn_b = int(((p_b==0)&(y_b==1)).sum())
        r_b  = tp_b/(tp_b+fn_b) if (tp_b+fn_b)>0 else 0.0
        pr_b = tp_b/(tp_b+fp_b) if (tp_b+fp_b)>0 else 0.0
        boot_scores.append((r_b+pr_b)/2*100)
    ci_lo, ci_hi = np.percentile(boot_scores, [2.5, 97.5])

    cal_delta = 2.67
    lb_est = best_score + cal_delta

    print(f"[V18] Bootstrap 95% CI:  [{ci_lo:.2f}, {ci_hi:.2f}]")
    print(f"[V18] Calibrated LB est: {lb_est:.2f}  (OOF {best_score:.2f} + delta {cal_delta})")
    print(f"[V18] V4 banked LB:      56.98")

    metrics = {
        "oof_auc": float(oof_auc),
        "v5_baseline_auc": 0.88860,
        "delta_auc": float(oof_auc - 0.88860),
        "best_oof_score": float(best_score),
        "best_T": float(best_T),
        "recall": float(best_R),
        "precision": float(best_P),
        "ci_lo": float(ci_lo),
        "ci_hi": float(ci_hi),
        "cal_delta": cal_delta,
        "lb_estimate": float(lb_est),
        "n_test_positives": int((test_proba_gated >= best_T).sum()),
        "gate_zeroed": int(gate_mask.sum()),
    }
else:
    # Fallback: use median threshold
    print("[V18] OOF unavailable — defaulting T=0.5 for submission")
    best_T = 0.5
    metrics = {
        "oof_auc": float(oof_auc),
        "note": "OOF proba unavailable; threshold=0.5 default",
        "n_test_positives": int((test_proba_gated >= best_T).sum()),
        "gate_zeroed": int(gate_mask.sum()),
    }

with open(OUT / "chosen_threshold_v18.json", "w") as f:
    json.dump(metrics, f, indent=2)

# ── Submission CSV ─────────────────────────────────────────────────────────────
print("[V18] Generating submission CSV...")
test_preds_binary = (test_proba_gated >= best_T).astype(int)
coil_ids = test["CoilID"].values
sub_df = pd.DataFrame({"CoilID": coil_ids, "Y": test_preds_binary})
sub_df.to_csv(OUT / "expected_submission.csv", index=False)
print(f"[V18] Submission: {len(sub_df)} rows, {int(test_preds_binary.sum())} positives")

# Save raw probas
pd.DataFrame({
    "CoilID": coil_ids,
    "proba_v18": test_proba_gated,
    "gate_zeroed": gate_mask.astype(int),
}).to_parquet(OUT / "test_meta_v18.parquet", index=False)

# ── Feature importance ─────────────────────────────────────────────────────────
print("[V18] Feature importance (top 20)...")
try:
    fi = predictor.feature_importance(train_ag, num_shuffle_sets=5, subsample_size=500)
    print(fi.head(20).to_string())
    fi.to_csv(OUT / "feature_importance_v18.csv")
except Exception as e:
    print(f"[V18] Feature importance failed: {e}")

print("[V18] DONE. Files in:", str(OUT))
print("[V18] Submission:  expected_submission.csv")
print("[V18] Metrics:     chosen_threshold_v18.json")
print("[V18] Leaderboard: ag_leaderboard_v18.csv")
