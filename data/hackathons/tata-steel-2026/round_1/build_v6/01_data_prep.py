"""
01_data_prep.py — V6 Data Preparation
Load V5 features, handle infinities, L2-normalize numerical features, prep tensors.
Output: scaled numpy arrays + scaler pickle for test-time consistency.
"""

import json, pickle
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler

V5_DIR = Path("data/hackathons/tata-steel-2026/round_1/build_v5")
V6_DIR = Path("data/hackathons/tata-steel-2026/round_1/build_v6")
V6_DIR.mkdir(parents=True, exist_ok=True)

print("Loading V5 data...")
train = pd.read_parquet(V5_DIR / "train_v5.parquet")
test  = pd.read_parquet(V5_DIR / "test_v5.parquet")

with open(V5_DIR / "feature_list_v5.json") as f:
    feat_info = json.load(f)

FEATURES = feat_info["features"]
print(f"  Train: {train.shape}, Test: {test.shape}, Features: {len(FEATURES)}")
print(f"  Positive rate: {train['Y'].mean():.4f} ({int(train['Y'].sum())}/{len(train)})")

X_train_raw = train[FEATURES].copy()
X_test_raw  = test[FEATURES].copy()

# Clip extreme values (X13_over_X36 can be 1e9+ when X36~0)
for col in FEATURES:
    clip_val = X_train_raw[col].quantile(0.999)
    if clip_val > 0:
        X_train_raw[col] = X_train_raw[col].clip(upper=clip_val)
        X_test_raw[col]  = X_test_raw[col].clip(upper=clip_val)

# Replace inf/nan with train median
for col in FEATURES:
    med = X_train_raw[col].median()
    X_train_raw[col] = X_train_raw[col].replace([np.inf, -np.inf], np.nan).fillna(med)
    X_test_raw[col]  = X_test_raw[col].replace([np.inf, -np.inf], np.nan).fillna(med)

assert not np.isinf(X_train_raw.values).any()
assert not np.isnan(X_train_raw.values).any()
assert not np.isinf(X_test_raw.values).any()
assert not np.isnan(X_test_raw.values).any()

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_raw).astype(np.float32)
X_test_scaled  = scaler.transform(X_test_raw).astype(np.float32)

y_train = train["Y"].values.astype(np.float32)
coil_ids_train = train["CoilID"].values
coil_ids_test  = test["CoilID"].values

n_neg = int((y_train == 0).sum())
n_pos = int((y_train == 1).sum())
pos_weight = n_neg / n_pos
print(f"  pos_weight = {pos_weight:.2f} (neg={n_neg}, pos={n_pos})")
print(f"  Scale check: mean={X_train_scaled.mean():.4f} std={X_train_scaled.std():.4f}")

np.save(V6_DIR / "X_train_scaled.npy", X_train_scaled)
np.save(V6_DIR / "X_test_scaled.npy",  X_test_scaled)
np.save(V6_DIR / "y_train.npy",        y_train)
np.save(V6_DIR / "coil_ids_train.npy", coil_ids_train)
np.save(V6_DIR / "coil_ids_test.npy",  coil_ids_test)

with open(V6_DIR / "scaler_v6.pkl", "wb") as f:
    pickle.dump(scaler, f)

with open(V6_DIR / "feature_list_v6.json", "w") as f:
    json.dump(feat_info, f, indent=2)

meta = {
    "n_train": len(train), "n_test": len(test),
    "n_features": len(FEATURES), "n_pos": n_pos, "n_neg": n_neg,
    "pos_weight": pos_weight, "features": FEATURES,
}
with open(V6_DIR / "data_prep_meta.json", "w") as f:
    json.dump(meta, f, indent=2)

print("01_data_prep.py DONE")
