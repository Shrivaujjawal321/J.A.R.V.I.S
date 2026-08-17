"""
Step 1: Load v1 engineered features + add IsolationForest iso_score.
Run: .venv/bin/python data/hackathons/tata-steel-2026/round_1/build_v2/01_load_features.py
"""
import os, json
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

V1_DIR = "data/hackathons/tata-steel-2026/round_1/build_v1"
V2_DIR = "data/hackathons/tata-steel-2026/round_1/build_v2"

print("=" * 60)
print("STEP 1: Load v1 features + IsolationForest meta-feature")
print("=" * 60)

train = pd.read_parquet(f"{V1_DIR}/train_engineered.parquet")
test  = pd.read_parquet(f"{V1_DIR}/test_engineered.parquet")
print(f"Train: {train.shape}  Test: {test.shape}")
print(f"Positives: {int(train['Y'].sum())} / {len(train)} ({100*train['Y'].mean():.2f}%)")

drop_cols = [c for c in ["CoilID","Y"] if c in train.columns]
feat_cols = [c for c in train.columns if c not in drop_cols]
test_feat_cols = [c for c in feat_cols if c in test.columns]
missing = [c for c in feat_cols if c not in test.columns]
if missing:
    print(f"[WARN] {len(missing)} features in train not in test: {missing}")
    feat_cols = test_feat_cols

X_tr = train[feat_cols].values.astype(np.float64)
X_te = test[test_feat_cols].values.astype(np.float64)
assert not np.isnan(X_tr).any()
assert not np.isnan(X_te).any()
print(f"Feature cols: {len(feat_cols)}")

print("\nFitting IsolationForest...")
iso = IsolationForest(n_estimators=200, contamination=0.05,
                      max_features=0.7, random_state=42, n_jobs=-1)
iso.fit(X_tr)
train["iso_score"] = iso.score_samples(X_tr)
test["iso_score"]  = iso.score_samples(X_te)

pos_iso = train.loc[train["Y"]==1,"iso_score"].mean()
neg_iso = train.loc[train["Y"]==0,"iso_score"].mean()
delta   = pos_iso - neg_iso
print(f"iso_score: defects={pos_iso:.4f}  non-defects={neg_iso:.4f}  delta={delta:.4f}")
print("[OK]" if delta < 0 else "[WARN]", "iso_score separation")

train.to_parquet(f"{V2_DIR}/train_v2.parquet", index=False)
test.to_parquet(f"{V2_DIR}/test_v2.parquet",   index=False)

final_feats = feat_cols + ["iso_score"]
json.dump({"features": final_feats, "n_features": len(final_feats),
           "iso_score_delta": float(delta)},
          open(f"{V2_DIR}/feature_list_v2.json","w"), indent=2)

print(f"\nSaved train_v2: {train.shape}  test_v2: {test.shape}")
print(f"Total features: {len(final_feats)}")
print("Step 1 DONE.")
