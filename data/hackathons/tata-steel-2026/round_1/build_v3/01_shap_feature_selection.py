"""
Step 1: SHAP Feature Selection
- Load v2 train/test parquets
- Train LightGBM (same config as v2) with 5-fold CV
- Compute SHAP values on OOF val sets (no leakage)
- Rank by mean |SHAP|, select top 30
- Save selected_features.json + shap bar chart
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import lightgbm as lgb
import shap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedKFold
from imblearn.over_sampling import SMOTE

# ── Paths ────────────────────────────────────────────────────────────────────
BASE = "/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1"
V2   = BASE + "/build_v2"
V3   = BASE + "/build_v3"
os.makedirs(V3 + "/figures", exist_ok=True)
os.makedirs(V3 + "/models",  exist_ok=True)

# ── Load data ────────────────────────────────────────────────────────────────
print("Loading v2 parquets...")
train = pd.read_parquet(V2 + "/train_v2.parquet")
test  = pd.read_parquet(V2 + "/test_v2.parquet")

TARGET   = "Y"
DROP     = ["CoilID", "Y"]
FEATURES = [c for c in train.columns if c not in DROP]
print(f"  Train: {train.shape}  |  Test: {test.shape}")
print(f"  Features: {len(FEATURES)}")
print(f"  Class distribution: {train[TARGET].value_counts().to_dict()}")

X = train[FEATURES].values
y = train[TARGET].values

# ── Train LightGBM OOF, compute SHAP on val sets ─────────────────────────────
print("\nTraining LightGBM for SHAP (5-fold, 250 rounds)...")

lgb_params = dict(
    is_unbalance=True,
    learning_rate=0.02,
    num_leaves=15,
    min_data_in_leaf=5,
    feature_fraction=0.7,
    bagging_fraction=0.7,
    bagging_freq=1,
    n_estimators=250,
    random_state=42,
    n_jobs=-1,
    verbose=-1,
)

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
shap_values_all = np.zeros((len(X), len(FEATURES)))

for fold, (tr_idx, va_idx) in enumerate(skf.split(X, y)):
    X_tr, y_tr = X[tr_idx], y[tr_idx]

    sm = SMOTE(sampling_strategy=0.3, k_neighbors=3, random_state=42)
    X_tr_s, y_tr_s = sm.fit_resample(X_tr, y_tr)

    model = lgb.LGBMClassifier(**lgb_params)
    model.fit(X_tr_s, y_tr_s)

    explainer = shap.TreeExplainer(model)
    sv = explainer.shap_values(X[va_idx])
    if isinstance(sv, list):
        sv = sv[1]
    shap_values_all[va_idx] = sv
    print(f"  Fold {fold+1}/5 done  (val size={len(va_idx)})")

# ── Rank features ─────────────────────────────────────────────────────────────
mean_abs_shap = np.abs(shap_values_all).mean(axis=0)
shap_df = pd.DataFrame({
    "feature":       FEATURES,
    "mean_abs_shap": mean_abs_shap
}).sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)

print("\nTop 30 features by mean|SHAP|:")
print(shap_df.head(30).to_string(index=False))

TOP_N    = 30
selected = shap_df["feature"].head(TOP_N).tolist()
top5     = shap_df["feature"].head(5).tolist()

out = {
    "top_30_features": selected,
    "top_5_features":  top5,
    "shap_ranking":    shap_df[["feature","mean_abs_shap"]].to_dict(orient="records"),
    "n_selected":      TOP_N,
}
with open(V3 + "/selected_features.json", "w") as f:
    json.dump(out, f, indent=2)
print(f"\nSaved selected_features.json  ({TOP_N} features)")

# ── SHAP bar plot ──────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 12))
top30 = shap_df.head(30)
ax.barh(top30["feature"][::-1], top30["mean_abs_shap"][::-1], color="steelblue")
ax.set_xlabel("Mean |SHAP value|")
ax.set_title("Top 30 Features by Mean |SHAP| (OOF)")
plt.tight_layout()
plt.savefig(V3 + "/figures/shap_importance.png", dpi=120)
plt.close()
print("Saved figures/shap_importance.png")

print("\n=== Step 1 COMPLETE ===")
