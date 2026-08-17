"""
V69 — Tabular Foundation Model Stack
Models: TabICL + TabDPT (+ TabPFN if TABPFN_TOKEN set)
Aggregation: Rank-average across available foundation models
Features: V4's 51 SHAP-selected features
"""

import os
import sys
import json
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from scipy.stats import spearmanr

warnings.filterwarnings("ignore")

# ─── Paths ───────────────────────────────────────────────────────────────────
ROOT = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1")
V4_DIR = ROOT / "build_v4"
OUT_DIR = ROOT / "build_v69"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ─── Load data ────────────────────────────────────────────────────────────────
print("=" * 60)
print("V69 — Tabular Foundation Model Stack")
print("=" * 60)

train_v4 = pd.read_parquet(V4_DIR / "train_v4.parquet")
test_v4 = pd.read_parquet(V4_DIR / "test_v4.parquet")

with open(V4_DIR / "v4_final_features.json") as f:
    features_info = json.load(f)
FEATURES = features_info["features"]  # 51 SHAP-selected

print(f"Features: {len(FEATURES)}")
print(f"Train: {train_v4.shape} | Test: {test_v4.shape}")

X_train = train_v4[FEATURES].values.astype(np.float32)
y_train = train_v4["Y"].values.astype(int)
X_test = test_v4[FEATURES].values.astype(np.float32)
coilid_train = train_v4["CoilID"].values
coilid_test = test_v4["CoilID"].values

print(f"Pos rate: {y_train.mean():.4f} ({y_train.sum()}/{len(y_train)})")

# ─── CV Setup ─────────────────────────────────────────────────────────────────
SEEDS = [42, 137, 1000]
N_FOLDS = 5
SKF = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)

# ─── Model availability check ─────────────────────────────────────────────────
AVAILABLE_MODELS = {}

# 1. TabICL
try:
    from tabicl import TabICLClassifier
    AVAILABLE_MODELS["TabICL"] = True
    print("\nTabICL: AVAILABLE")
except ImportError as e:
    AVAILABLE_MODELS["TabICL"] = False
    print(f"\nTabICL: UNAVAILABLE ({e})")

# 2. TabDPT
try:
    from tabdpt import TabDPTClassifier
    AVAILABLE_MODELS["TabDPT"] = True
    print("TabDPT: AVAILABLE")
except ImportError as e:
    AVAILABLE_MODELS["TabDPT"] = False
    print(f"TabDPT: UNAVAILABLE ({e})")

# 3. TabPFN — only if TABPFN_TOKEN set
TABPFN_TOKEN = os.environ.get("TABPFN_TOKEN", "")
if TABPFN_TOKEN:
    try:
        from tabpfn import TabPFNClassifier
        AVAILABLE_MODELS["TabPFN"] = True
        print("TabPFN: AVAILABLE (token set)")
    except ImportError as e:
        AVAILABLE_MODELS["TabPFN"] = False
        print(f"TabPFN: UNAVAILABLE ({e})")
else:
    AVAILABLE_MODELS["TabPFN"] = False
    print("TabPFN: SKIPPED (TABPFN_TOKEN not set)")

n_available = sum(AVAILABLE_MODELS.values())
print(f"\nActive models: {n_available} — {[k for k, v in AVAILABLE_MODELS.items() if v]}")

if n_available == 0:
    print("\nFAILURE: No foundation models available. Exiting.")
    sys.exit(1)


# ─── Helper: Rank normalisation ───────────────────────────────────────────────
def rank_normalize(arr: np.ndarray) -> np.ndarray:
    """Map raw probabilities to [0,1] via percentile rank."""
    from scipy.stats import rankdata
    return rankdata(arr, method="average") / len(arr)


# ─── TabICL Training ──────────────────────────────────────────────────────────
oof_tabicl: Optional[np.ndarray] = None
test_tabicl: Optional[np.ndarray] = None
tabicl_fold_aucs = []

if AVAILABLE_MODELS["TabICL"]:
    print("\n" + "─" * 50)
    print("Training TabICL")
    print("─" * 50)

    oof_preds_seeds = []
    test_preds_seeds = []

    for seed in SEEDS:
        oof_s = np.zeros(len(y_train))
        test_s = np.zeros(len(X_test))
        fold_aucs = []

        skf_s = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)

        for fold_idx, (tr_idx, val_idx) in enumerate(skf_s.split(X_train, y_train)):
            X_tr, X_val = X_train[tr_idx], X_train[val_idx]
            y_tr, y_val = y_train[tr_idx], y_train[val_idx]

            # TabICL handles imbalance internally via class shuffling
            clf = TabICLClassifier(
                n_estimators=8,
                random_state=seed,
                verbose=False,
            )
            clf.fit(X_tr, y_tr)

            val_proba = clf.predict_proba(X_val)[:, 1]
            test_proba = clf.predict_proba(X_test)[:, 1]

            oof_s[val_idx] = val_proba
            test_s += test_proba / N_FOLDS

            fold_auc = roc_auc_score(y_val, val_proba)
            fold_aucs.append(fold_auc)
            print(f"  Seed {seed} Fold {fold_idx+1}: AUC={fold_auc:.4f}")

        seed_auc = roc_auc_score(y_train, oof_s)
        print(f"  Seed {seed} OOF AUC: {seed_auc:.4f} | Fold std: {np.std(fold_aucs):.4f}")

        oof_preds_seeds.append(oof_s)
        test_preds_seeds.append(test_s)

    # Average across seeds
    oof_tabicl = np.mean(oof_preds_seeds, axis=0)
    test_tabicl = np.mean(test_preds_seeds, axis=0)

    overall_auc = roc_auc_score(y_train, oof_tabicl)
    print(f"\nTabICL Final OOF AUC: {overall_auc:.4f}")

    # Per-fold AUC on averaged OOF (for validation gates)
    skf_check = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)
    for fold_idx, (_, val_idx) in enumerate(skf_check.split(X_train, y_train)):
        fa = roc_auc_score(y_train[val_idx], oof_tabicl[val_idx])
        tabicl_fold_aucs.append(fa)
    print(f"TabICL Fold AUCs: {[f'{a:.4f}' for a in tabicl_fold_aucs]}")
    print(f"Fold std: {np.std(tabicl_fold_aucs):.4f}")


# ─── TabDPT Training ──────────────────────────────────────────────────────────
oof_tabdpt: Optional[np.ndarray] = None
test_tabdpt: Optional[np.ndarray] = None
tabdpt_fold_aucs = []

if AVAILABLE_MODELS["TabDPT"]:
    print("\n" + "─" * 50)
    print("Training TabDPT")
    print("─" * 50)

    oof_preds_seeds = []
    test_preds_seeds = []

    for seed in SEEDS:
        oof_s = np.zeros(len(y_train))
        test_s = np.zeros(len(X_test))
        fold_aucs = []

        skf_s = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)

        for fold_idx, (tr_idx, val_idx) in enumerate(skf_s.split(X_train, y_train)):
            X_tr, X_val = X_train[tr_idx], X_train[val_idx]
            y_tr, y_val = y_train[tr_idx], y_train[val_idx]

            clf = TabDPTClassifier(verbose=False)
            clf.fit(X_tr, y_tr)

            val_proba = clf.predict_proba(X_val)[:, 1]
            test_proba = clf.predict_proba(X_test)[:, 1]

            oof_s[val_idx] = val_proba
            test_s += test_proba / N_FOLDS

            fold_auc = roc_auc_score(y_val, val_proba)
            fold_aucs.append(fold_auc)
            print(f"  Seed {seed} Fold {fold_idx+1}: AUC={fold_auc:.4f}")

        seed_auc = roc_auc_score(y_train, oof_s)
        print(f"  Seed {seed} OOF AUC: {seed_auc:.4f} | Fold std: {np.std(fold_aucs):.4f}")

        oof_preds_seeds.append(oof_s)
        test_preds_seeds.append(test_s)

    oof_tabdpt = np.mean(oof_preds_seeds, axis=0)
    test_tabdpt = np.mean(test_preds_seeds, axis=0)

    overall_auc = roc_auc_score(y_train, oof_tabdpt)
    print(f"\nTabDPT Final OOF AUC: {overall_auc:.4f}")

    skf_check = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)
    for fold_idx, (_, val_idx) in enumerate(skf_check.split(X_train, y_train)):
        fa = roc_auc_score(y_train[val_idx], oof_tabdpt[val_idx])
        tabdpt_fold_aucs.append(fa)
    print(f"TabDPT Fold AUCs: {[f'{a:.4f}' for a in tabdpt_fold_aucs]}")
    print(f"Fold std: {np.std(tabdpt_fold_aucs):.4f}")


# ─── TabPFN Training (if token available) ────────────────────────────────────
oof_tabpfn: Optional[np.ndarray] = None
test_tabpfn: Optional[np.ndarray] = None
tabpfn_fold_aucs = []

if AVAILABLE_MODELS["TabPFN"]:
    from tabpfn import TabPFNClassifier
    print("\n" + "─" * 50)
    print("Training TabPFN v2")
    print("─" * 50)

    oof_preds_seeds = []
    test_preds_seeds = []

    for seed in SEEDS:
        oof_s = np.zeros(len(y_train))
        test_s = np.zeros(len(X_test))
        fold_aucs = []

        skf_s = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)

        for fold_idx, (tr_idx, val_idx) in enumerate(skf_s.split(X_train, y_train)):
            X_tr, X_val = X_train[tr_idx], X_train[val_idx]
            y_tr, y_val = y_train[tr_idx], y_train[val_idx]

            clf = TabPFNClassifier(
                n_estimators=4,
                balance_probabilities=True,
                random_state=seed,
                ignore_pretraining_limits=True,
            )
            clf.fit(X_tr, y_tr)

            val_proba = clf.predict_proba(X_val)[:, 1]
            test_proba = clf.predict_proba(X_test)[:, 1]

            oof_s[val_idx] = val_proba
            test_s += test_proba / N_FOLDS

            fold_auc = roc_auc_score(y_val, val_proba)
            fold_aucs.append(fold_auc)
            print(f"  Seed {seed} Fold {fold_idx+1}: AUC={fold_auc:.4f}")

        seed_auc = roc_auc_score(y_train, oof_s)
        print(f"  Seed {seed} OOF AUC: {seed_auc:.4f} | Fold std: {np.std(fold_aucs):.4f}")

        oof_preds_seeds.append(oof_s)
        test_preds_seeds.append(test_s)

    oof_tabpfn = np.mean(oof_preds_seeds, axis=0)
    test_tabpfn = np.mean(test_preds_seeds, axis=0)

    overall_auc = roc_auc_score(y_train, oof_tabpfn)
    print(f"\nTabPFN Final OOF AUC: {overall_auc:.4f}")

    skf_check = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)
    for fold_idx, (_, val_idx) in enumerate(skf_check.split(X_train, y_train)):
        fa = roc_auc_score(y_train[val_idx], oof_tabpfn[val_idx])
        tabpfn_fold_aucs.append(fa)
    print(f"TabPFN Fold AUCs: {[f'{a:.4f}' for a in tabpfn_fold_aucs]}")
    print(f"Fold std: {np.std(tabpfn_fold_aucs):.4f}")


# ─── Aggregation: Rank-average ─────────────────────────────────────────────────
print("\n" + "=" * 60)
print("Aggregation: Rank-average")
print("=" * 60)

oof_parts = []
test_parts = []
model_aucs = {}

if oof_tabicl is not None:
    oof_parts.append(rank_normalize(oof_tabicl))
    test_parts.append(rank_normalize(test_tabicl))
    model_aucs["TabICL"] = roc_auc_score(y_train, oof_tabicl)

if oof_tabdpt is not None:
    oof_parts.append(rank_normalize(oof_tabdpt))
    test_parts.append(rank_normalize(test_tabdpt))
    model_aucs["TabDPT"] = roc_auc_score(y_train, oof_tabdpt)

if oof_tabpfn is not None:
    oof_parts.append(rank_normalize(oof_tabpfn))
    test_parts.append(rank_normalize(test_tabpfn))
    model_aucs["TabPFN"] = roc_auc_score(y_train, oof_tabpfn)

oof_v69 = np.mean(oof_parts, axis=0)
test_v69 = np.mean(test_parts, axis=0)

v69_auc = roc_auc_score(y_train, oof_v69)
print(f"\nV69 ensemble OOF AUC: {v69_auc:.4f}")
for name, auc in model_aucs.items():
    print(f"  {name}: {auc:.4f}")

# ─── Validation Gates ─────────────────────────────────────────────────────────
print("\n" + "─" * 50)
print("Validation Gates")
print("─" * 50)

# Gate 1: OOF AUC > 0.85
gate1 = v69_auc > 0.85
print(f"Gate 1 — OOF AUC > 0.85: {v69_auc:.4f} → {'PASS' if gate1 else 'FAIL'}")

# Gate 2: Per-fold std AUC < 0.05
skf_gate = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)
gate2_fold_aucs = []
for _, val_idx in skf_gate.split(X_train, y_train):
    fa = roc_auc_score(y_train[val_idx], oof_v69[val_idx])
    gate2_fold_aucs.append(fa)
fold_std = np.std(gate2_fold_aucs)
gate2 = fold_std < 0.05
print(f"Gate 2 — Fold std AUC < 0.05: {fold_std:.4f} → {'PASS' if gate2 else 'FAIL'}")
print(f"         Fold AUCs: {[f'{a:.4f}' for a in gate2_fold_aucs]}")

# Gate 3: Spearman vs V44 OOF 0.50–0.80
try:
    oof_v4 = pd.read_parquet(V4_DIR / "oof_v4.parquet")
    v44_oof = oof_v4["oof_meta"].values  # V4 meta is effectively V44-like
    spear, _ = spearmanr(oof_v69, v44_oof)
    gate3 = 0.50 <= spear <= 0.80
    print(f"Gate 3 — Spearman vs V44 OOF (0.50–0.80): {spear:.4f} → {'PASS' if gate3 else 'OUT_OF_RANGE'}")
except Exception as e:
    spear = None
    gate3 = None
    print(f"Gate 3 — Spearman: SKIPPED ({e})")

# ─── Save Outputs ─────────────────────────────────────────────────────────────
print("\n" + "─" * 50)
print("Saving outputs")
print("─" * 50)

# test_proba_v69.parquet
test_out = pd.DataFrame({"CoilID": coilid_test, "v69_score": test_v69})
test_out.to_parquet(OUT_DIR / "test_proba_v69.parquet", index=False)
print(f"Saved test_proba_v69.parquet ({len(test_out)} rows)")

# oof_v69.parquet
oof_out = pd.DataFrame({
    "CoilID": coilid_train,
    "oof_score": oof_v69,
    "y": y_train,
})
oof_out.to_parquet(OUT_DIR / "oof_v69.parquet", index=False)
print(f"Saved oof_v69.parquet ({len(oof_out)} rows)")

# Per-model OOF files (for diagnostics)
if oof_tabicl is not None:
    pd.DataFrame({"CoilID": coilid_train, "oof_tabicl": oof_tabicl, "y": y_train}).to_parquet(
        OUT_DIR / "oof_tabicl.parquet", index=False
    )
    pd.DataFrame({"CoilID": coilid_test, "tabicl_score": test_tabicl}).to_parquet(
        OUT_DIR / "test_tabicl.parquet", index=False
    )

if oof_tabdpt is not None:
    pd.DataFrame({"CoilID": coilid_train, "oof_tabdpt": oof_tabdpt, "y": y_train}).to_parquet(
        OUT_DIR / "oof_tabdpt.parquet", index=False
    )
    pd.DataFrame({"CoilID": coilid_test, "tabdpt_score": test_tabdpt}).to_parquet(
        OUT_DIR / "test_tabdpt.parquet", index=False
    )

if oof_tabpfn is not None:
    pd.DataFrame({"CoilID": coilid_train, "oof_tabpfn": oof_tabpfn, "y": y_train}).to_parquet(
        OUT_DIR / "oof_tabpfn.parquet", index=False
    )
    pd.DataFrame({"CoilID": coilid_test, "tabpfn_score": test_tabpfn}).to_parquet(
        OUT_DIR / "test_tabpfn.parquet", index=False
    )

# ─── Metrics Report ───────────────────────────────────────────────────────────
metrics = {
    "v69_oof_auc": round(v69_auc, 6),
    "v69_fold_aucs": [round(a, 6) for a in gate2_fold_aucs],
    "v69_fold_std": round(fold_std, 6),
    "spearman_vs_v44": round(spear, 6) if spear is not None else None,
    "gate1_pass": bool(gate1),
    "gate2_pass": bool(gate2),
    "gate3_pass": bool(gate3) if gate3 is not None else None,
    "models_used": [k for k, v in AVAILABLE_MODELS.items() if v],
    "models_skipped": [k for k, v in AVAILABLE_MODELS.items() if not v],
    "per_model_oof_auc": {k: round(v, 6) for k, v in model_aucs.items()},
    "tabicl_fold_aucs": [round(a, 6) for a in tabicl_fold_aucs] if tabicl_fold_aucs else [],
    "tabdpt_fold_aucs": [round(a, 6) for a in tabdpt_fold_aucs] if tabdpt_fold_aucs else [],
    "tabpfn_fold_aucs": [round(a, 6) for a in tabpfn_fold_aucs] if tabpfn_fold_aucs else [],
}

with open(OUT_DIR / "metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)
print(f"Saved metrics.json")

# ─── Final Summary ────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("V69 FINAL SUMMARY")
print("=" * 60)
print(f"Models run:   {metrics['models_used']}")
print(f"Models skip:  {metrics['models_skipped']}")
print()
for name, auc in model_aucs.items():
    print(f"  {name:10s} OOF AUC: {auc:.4f}")
print(f"\n  V69 ensemble OOF AUC: {v69_auc:.4f}")
print()
print(f"Gate 1 (AUC>0.85):          {'PASS' if gate1 else 'FAIL'}")
print(f"Gate 2 (fold std<0.05):     {'PASS' if gate2 else 'FAIL'}  (std={fold_std:.4f})")
print(f"Gate 3 (Spearman 0.5-0.8):  {'PASS' if gate3 else 'OUT_OF_RANGE' if gate3 is not None else 'SKIPPED'}  (r={spear:.4f if spear is not None else 'N/A'})")
print()
print("Deliverables:")
print(f"  {OUT_DIR}/test_proba_v69.parquet")
print(f"  {OUT_DIR}/oof_v69.parquet")
print(f"  {OUT_DIR}/metrics.json")
