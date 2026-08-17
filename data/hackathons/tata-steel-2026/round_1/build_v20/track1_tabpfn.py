"""
V20 Track 1 -- TabPFN Cloud (tabpfn-client 0.3.0)
Loads V5 train/test features (59 features)
Attempts anonymous TabPFN cloud inference
5-fold OOF + AUC vs V5 baseline (0.8886)
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler
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

X_train = train[feat_list].values.astype(np.float32)
y_train = oof["Y"].values
X_test  = test[feat_list].values.astype(np.float32)

print(f"Train: {X_train.shape}, Test: {X_test.shape}")
print(f"Positive rate: {y_train.mean():.4f}")

# Gate mask: X42 > 0.025067 OR X39 >= 169 -> force 0
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
print(f"Gate train: {gate_train.sum()}/{len(gate_train)} pass")
print(f"Gate test:  {gate_test.sum()}/{len(gate_test)} pass")

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

tabpfn_ok = False
tabpfn_auc = None
oof_tabpfn = np.zeros(len(X_train))
test_proba_tabpfn = np.zeros(len(X_test))

try:
    from tabpfn_client import TabPFNClassifier
    print("\nTabPFN client imported OK")
    print("Trying anonymous inference (no token)...")

    clf = TabPFNClassifier(n_estimators=4)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    fold_aucs = []

    for fold, (tr_idx, val_idx) in enumerate(cv.split(X_train_sc, y_train)):
        X_tr, X_val = X_train_sc[tr_idx], X_train_sc[val_idx]
        y_tr, y_val = y_train[tr_idx], y_train[val_idx]
        print(f"  Fold {fold+1}: {len(X_tr)} rows...")
        clf.fit(X_tr, y_tr)
        proba = clf.predict_proba(X_val)[:, 1]
        oof_tabpfn[val_idx] = proba
        auc = roc_auc_score(y_val, proba)
        fold_aucs.append(auc)
        print(f"  Fold {fold+1}: AUC={auc:.4f}")

    print("  Full-train fit for test preds...")
    clf.fit(X_train_sc, y_train)
    test_proba_tabpfn = clf.predict_proba(X_test_sc)[:, 1]

    tabpfn_auc = roc_auc_score(y_train, oof_tabpfn)
    tabpfn_ok = True
    print(f"\nTabPFN OOF AUC: {tabpfn_auc:.4f}  (V5 baseline: 0.8886)")
    print(f"Fold AUCs: {[round(a,4) for a in fold_aucs]}")

except Exception as e:
    print(f"TabPFN FAILED: {type(e).__name__}: {e}")
    if any(kw in str(e).lower() for kw in ["token","auth","login","api","account"]):
        print("  -> Auth required, no anonymous access")
    tabpfn_ok = False

result = {
    "track": "tabpfn_cloud",
    "success": tabpfn_ok,
    "oof_auc": float(tabpfn_auc) if tabpfn_auc else None,
    "v5_baseline_auc": 0.8886,
    "delta_vs_v5": float(tabpfn_auc - 0.8886) if tabpfn_auc else None,
}
json.dump(result, open(V20_DIR / "track1_result.json", "w"), indent=2)
np.save(V20_DIR / "oof_tabpfn.npy", oof_tabpfn)
np.save(V20_DIR / "test_tabpfn.npy", test_proba_tabpfn)
print("\nTrack 1 saved:", result)
