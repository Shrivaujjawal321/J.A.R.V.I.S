"""
Step 2: Polynomial Interactions on Top 5 SHAP Features
- Load selected_features.json (from Step 1)
- Add degree-2 polynomial features for top 5 SHAP features
- Save train_v3.parquet + test_v3.parquet
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures

BASE = "/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1"
V2   = BASE + "/build_v2"
V3   = BASE + "/build_v3"

print("Loading data and feature selection...")
train = pd.read_parquet(V2 + "/train_v2.parquet")
test  = pd.read_parquet(V2 + "/test_v2.parquet")

with open(V3 + "/selected_features.json") as f:
    sel = json.load(f)

top5     = sel["top_5_features"]
selected = sel["top_30_features"]

print(f"Top 5 features for polynomial expansion: {top5}")

# ── Degree-2 polynomial on top 5 ──────────────────────────────────────────────
poly = PolynomialFeatures(degree=2, interaction_only=False, include_bias=False)
poly_train = poly.fit_transform(train[top5])
poly_test  = poly.transform(test[top5])

poly_names = poly.get_feature_names_out(top5)
print(f"Polynomial features: {len(poly_names)}  (from {len(top5)} inputs, degree=2)")
print(f"New poly feature names: {list(poly_names)}")

# ── Build augmented dataframes ─────────────────────────────────────────────────
# Start from full v2 features (not just top 30 — we select inside the model)
train_v3 = train.copy()
test_v3  = test.copy()

# Add poly features with prefix to avoid name collision
for i, name in enumerate(poly_names):
    col = "poly_" + name.replace(" ", "_")
    train_v3[col] = poly_train[:, i]
    test_v3[col]  = poly_test[:, i]

# Feature list: top_30 + new poly features (excluding the 5 originals already in top30)
new_poly_cols = ["poly_" + n.replace(" ", "_") for n in poly_names]
# Filter out the 5 original features since they're already in selected list
orig_poly_names = ["poly_" + n.replace(" ", "_") for n in top5]
extra_poly_cols = [c for c in new_poly_cols if c not in orig_poly_names]

# Final feature set for v3: selected (top30) + cross/squared poly terms
feat_v3 = selected + extra_poly_cols
feat_v3 = list(dict.fromkeys(feat_v3))  # deduplicate, preserve order
print(f"\nFinal feature set size: {len(feat_v3)}")
print(f"  - Top 30 SHAP features: {len(selected)}")
print(f"  - Extra poly features: {len(extra_poly_cols)}")

# Save updated feature list
with open(V3 + "/feature_list_v3.json", "w") as f:
    json.dump({
        "features":        feat_v3,
        "n_features":      len(feat_v3),
        "top_30":          selected,
        "top_5":           top5,
        "poly_terms":      extra_poly_cols,
        "n_poly_extra":    len(extra_poly_cols),
    }, f, indent=2)

# Save parquets
train_v3.to_parquet(V3 + "/train_v3.parquet", index=False)
test_v3.to_parquet(V3 + "/test_v3.parquet",   index=False)
print(f"\nSaved train_v3.parquet: {train_v3.shape}")
print(f"Saved test_v3.parquet:  {test_v3.shape}")

print("\n=== Step 2 COMPLETE ===")
