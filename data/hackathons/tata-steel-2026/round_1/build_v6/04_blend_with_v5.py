"""
04_blend_with_v5.py — Simple average blend of V6 FT-Transformer + V5 tree-stack
Rationale: Trees and Transformers have different error modes.
V5 meta = LGB+XGB+CatBoost+LR stack; V6 = attention-based feature interactions.
Blend probas 50/50, re-sweep threshold, generate blend submission.
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path

V5_DIR = Path("data/hackathons/tata-steel-2026/round_1/build_v5")
V6_DIR = Path("data/hackathons/tata-steel-2026/round_1/build_v6")

# ─── Load ─────────────────────────────────────────────────────────────────────
oof_v5   = pd.read_parquet(V5_DIR / "oof_v5.parquet")       # has oof_meta (V5)
test_v5  = pd.read_parquet(V5_DIR / "test_meta_v5.parquet") # has test_meta (V5)
oof_v6   = pd.read_parquet(V6_DIR / "oof_v6.parquet")       # has oof_v6
test_v6  = pd.read_parquet(V6_DIR / "test_meta_v6.parquet") # has test_meta_v6

# Align by CoilID to be safe
oof_merged = oof_v5[["CoilID", "Y", "oof_meta"]].merge(
    oof_v6[["CoilID", "oof_v6"]], on="CoilID", how="inner"
)
test_merged = test_v5[["CoilID", "test_meta"]].merge(
    test_v6[["CoilID", "test_meta_v6"]], on="CoilID", how="inner"
)

print(f"OOF aligned: {len(oof_merged)} rows (train={len(oof_v5)}, v6={len(oof_v6)})")
print(f"Test aligned: {len(test_merged)} rows")

y_true      = oof_merged["Y"].values.astype(int)
oof_blend   = (oof_merged["oof_meta"].values + oof_merged["oof_v6"].values) / 2.0
test_blend  = (test_merged["test_meta"].values + test_merged["test_meta_v6"].values) / 2.0

print(f"OOF blend range: [{oof_blend.min():.4f}, {oof_blend.max():.4f}]")

# ─── Threshold sweep on blend OOF ─────────────────────────────────────────────
thresholds = np.unique(oof_blend)
results = []

for t in thresholds:
    preds  = (oof_blend >= t).astype(int)
    tp = int(((preds == 1) & (y_true == 1)).sum())
    fp = int(((preds == 1) & (y_true == 0)).sum())
    fn = int(((preds == 0) & (y_true == 1)).sum())
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    score     = (recall + precision) / 2 * 100
    results.append({
        "threshold": float(t), "score": float(score),
        "recall": float(recall), "precision": float(precision),
        "tp": tp, "fp": fp, "fn": fn,
        "n_pos_pred": int(preds.sum()),
    })

sweep_df = pd.DataFrame(results).sort_values("score", ascending=False)
sweep_df.to_csv(V6_DIR / "threshold_sweep_v6_blend.csv", index=False)

best  = sweep_df.iloc[0]
T     = float(best["threshold"])
score = float(best["score"])
R     = float(best["recall"])
P     = float(best["precision"])

print(f"\n=== V6 + V5 Blend Threshold ===")
print(f"  Best T     : {T:.6f}")
print(f"  OOF Score  : {score:.4f}  (R={R:.4f}, P={P:.4f})")
print(f"  Positives  : {int(best['n_pos_pred'])} predicted / {int(y_true.sum())} actual")

# Also report AUC of blend
from sklearn.metrics import roc_auc_score
blend_auc = roc_auc_score(y_true, oof_blend)
print(f"  Blend OOF AUC: {blend_auc:.4f}")

# Save threshold metadata
chosen_blend = {
    "chosen_threshold_v6_blend": T,
    "oof_score_v6_blend": score,
    "recall_at_T": R,
    "precision_at_T": P,
    "blend_oof_auc": float(blend_auc),
    "n_pos_oof": int(best["n_pos_pred"]),
    "n_pos_test": int((test_blend >= T).sum()),
    "blend_weights": {"v5_meta": 0.5, "v6_ft_transformer": 0.5},
}
with open(V6_DIR / "chosen_threshold_v6_blend.json", "w") as f:
    json.dump(chosen_blend, f, indent=2)

# Generate blend test submission
test_preds = (test_blend >= T).astype(int)
sub_df = pd.DataFrame({
    "CoilID": test_merged["CoilID"].values,
    "Y":      test_preds,
})
sub_df.to_csv(V6_DIR / "expected_submission_v6_blend.csv", index=False)

# Save blend OOF + test probas for downstream analysis
pd.DataFrame({
    "CoilID": oof_merged["CoilID"].values,
    "Y":      y_true,
    "oof_v5_meta": oof_merged["oof_meta"].values,
    "oof_v6":      oof_merged["oof_v6"].values,
    "oof_blend":   oof_blend,
}).to_parquet(V6_DIR / "oof_blend_v6_v5.parquet", index=False)

pd.DataFrame({
    "CoilID":     test_merged["CoilID"].values,
    "test_v5":    test_merged["test_meta"].values,
    "test_v6":    test_merged["test_meta_v6"].values,
    "test_blend": test_blend,
}).to_parquet(V6_DIR / "test_blend_v6_v5.parquet", index=False)

print(f"  Test positives: {test_preds.sum()} / {len(test_preds)}")
print(f"  Saved: expected_submission_v6_blend.csv, chosen_threshold_v6_blend.json")
print("04_blend_with_v5.py DONE")
