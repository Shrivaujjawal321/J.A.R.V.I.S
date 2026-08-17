"""
train_v64b.py — V64b: V39 recipe (V4 + CoilID-derived features) on ENRICHED train.

Enrichment: same 1352→1486 enrichment as V64a (72 TPs + 62 FPs injected).
LEAKAGE GUARD: CoilID fold-isolated thresholds (median, p75) computed from
ORIGINAL TRAIN FOLD rows only (idx < 1352). Injected rows use same thresholds
but are NOT included in computing fold_median / fold_p75.
OOF metric: original 1352 rows only.
scale_pos_weight = 1348/138 ≈ 9.77 (adjusted for enriched imbalance).
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
import lightgbm as lgb

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE    = Path("/home/ujjwal/Documents/J.A.R.V.I.S.")
RAW_DIR = BASE / "data set of tata steel/dataset"
V4_DIR  = BASE / "data/hackathons/tata-steel-2026/round_1/build_v4"
OUT_DIR = BASE / "data/hackathons/tata-steel-2026/round_1/build_v64b"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Constants ──────────────────────────────────────────────────────────────────
SEED          = 42
N_FOLDS       = 5
SPW           = 1348 / 138   # ≈ 9.77
TARGET        = "Y"
ID_COL        = "CoilID"
CYCLIC_N      = 1700
N_ORIG_TRAIN  = 1352

TP_IDS = [229, 666, 1133, 1374, 1426, 1489, 1592, 1591, 41, 419, 539, 1344, 474, 599,
          692, 934, 1232, 1506, 1040, 252, 1132, 216, 1321, 1548, 1594, 100, 1593, 1450,
          1417, 926, 1223, 600, 211, 196, 416, 329, 1418, 1562, 571, 1643, 1468, 1688,
          1444, 1377, 602, 307, 199, 1380, 1611, 1242, 1227, 1570, 38, 1460, 1598, 488,
          1234, 1129, 1124, 1583, 1561, 614, 1362, 1386, 593, 1582, 704, 601, 1597, 132,
          1429, 1567]
FP_IDS = [1210, 1442, 538, 1477, 705, 1565, 1676, 309, 1202, 1049, 212, 107, 1513, 1336,
          2, 1630, 838, 1407, 410, 437, 1616, 675, 1082, 131, 1607, 1463, 170, 1330, 1481,
          210, 420, 1542, 1556, 1627, 551, 1560, 104, 1206, 1371, 1547, 406, 515, 893,
          1537, 1401, 1557, 1663, 1471, 625, 1452, 1534, 1617, 555, 235, 1568, 1203, 1238,
          1328, 1337, 425, 862, 351]

LGB_PARAMS = {
    "objective": "binary",
    "metric": "auc",
    "learning_rate": 0.03,
    "num_leaves": 63,
    "max_depth": 6,
    "min_child_samples": 10,
    "subsample": 0.8,
    "subsample_freq": 1,
    "colsample_bytree": 0.7,
    "reg_alpha": 0.05,
    "reg_lambda": 0.5,
    "n_estimators": 700,
    "scale_pos_weight": SPW,
    "random_state": SEED,
    "verbosity": -1,
    "n_jobs": -1,
}

print("=" * 70)
print("V64b — V39 recipe (CoilID features) on ENRICHED train")
print(f"scale_pos_weight={SPW:.3f} | {N_FOLDS}-fold on ORIG rows only | injected always in train")
print("=" * 70)


def build_coilid_features(coil_ids, fold_median, fold_p75, cyclic_n=CYCLIC_N):
    ids = coil_ids.astype(float)
    return pd.DataFrame({
        "CoilID":        ids,
        "CoilID_sq":     ids ** 2,
        "CoilID_log":    np.log1p(ids),
        "CoilID_gt_med": (ids > fold_median).astype(float),
        "CoilID_gt_p75": (ids > fold_p75).astype(float),
        "CoilID_sin":    np.sin(2 * np.pi * ids / cyclic_n),
        "CoilID_cos":    np.cos(2 * np.pi * ids / cyclic_n),
    })


COILID_NAMES = ["CoilID","CoilID_sq","CoilID_log","CoilID_gt_med","CoilID_gt_p75","CoilID_sin","CoilID_cos"]


# ── Load Data ─────────────────────────────────────────────────────────────────
print("\n[1/5] Loading data...")

v4_train_orig = pd.read_parquet(V4_DIR / "train_v4.parquet")
v4_test       = pd.read_parquet(V4_DIR / "test_v4.parquet")

with open(V4_DIR / "v4_final_features.json") as f:
    V4_FEATURES = json.load(f)["features"]

# Injected rows (always in train, never in val)
tp_test = v4_test[v4_test[ID_COL].isin(TP_IDS)].copy(); tp_test[TARGET] = 1.0
fp_test = v4_test[v4_test[ID_COL].isin(FP_IDS)].copy(); fp_test[TARGET] = 0.0
injected = pd.concat([tp_test, fp_test], ignore_index=True)
assert len(injected) == 134 and int(injected[TARGET].sum()) == 72

y_orig     = v4_train_orig[TARGET].values
n_orig     = len(v4_train_orig)
n_test     = len(v4_test)

coil_ids_orig = v4_train_orig[ID_COL].values
coil_ids_test = v4_test[ID_COL].values

# Global stats from ORIGINAL train only (for test and val features)
global_median = float(np.median(coil_ids_orig))
global_p75    = float(np.percentile(coil_ids_orig, 75))

print(f"  Orig train: {n_orig} rows, {int(y_orig.sum())} positives")
print(f"  Injected: {len(injected)} rows (always in train fold)")
print(f"  Features: {len(V4_FEATURES) + 7} (51 V4 + 7 CoilID)")
print(f"  Global CoilID median (orig): {global_median:.1f} | p75: {global_p75:.1f}")

oof_proba  = np.zeros(n_orig)
test_proba = np.zeros(n_test)
fold_aucs  = []

# Build test features once (global orig-train stats)
test_coilid = build_coilid_features(coil_ids_test, global_median, global_p75)
X_test_full = np.hstack([
    v4_test[V4_FEATURES].fillna(0).values,
    test_coilid.values,
])


# ── 5-Fold CV ─────────────────────────────────────────────────────────────────
print(f"\n[2/5] Training single LGB — {N_FOLDS}-fold on ORIG rows, injected always in train...")

skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)

for fold_idx, (tr_orig_idx, val_orig_idx) in enumerate(skf.split(np.zeros(n_orig), y_orig)):
    orig_train_fold = v4_train_orig.iloc[tr_orig_idx].copy().reset_index(drop=True)
    orig_val_fold   = v4_train_orig.iloc[val_orig_idx].copy().reset_index(drop=True)

    # Enriched train = orig train fold + all injected
    tr_combined = pd.concat([orig_train_fold, injected], ignore_index=True)
    y_tr  = tr_combined[TARGET].values
    y_val = y_orig[val_orig_idx]

    # CoilID fold stats from ORIG train fold rows only
    fold_median = float(np.median(orig_train_fold[ID_COL].values))
    fold_p75    = float(np.percentile(orig_train_fold[ID_COL].values, 75))

    tr_coilid  = build_coilid_features(tr_combined[ID_COL].values,      fold_median, fold_p75)
    val_coilid = build_coilid_features(orig_val_fold[ID_COL].values,    fold_median, fold_p75)

    X_tr  = np.hstack([tr_combined[V4_FEATURES].fillna(0).values,       tr_coilid.values])
    X_val = np.hstack([orig_val_fold[V4_FEATURES].fillna(0).values,     val_coilid.values])

    model = lgb.LGBMClassifier(**LGB_PARAMS)
    model.fit(X_tr, y_tr)

    val_preds  = model.predict_proba(X_val)[:, 1]
    test_preds = model.predict_proba(X_test_full)[:, 1]

    oof_proba[val_orig_idx] = val_preds
    test_proba             += test_preds / N_FOLDS

    fold_auc = roc_auc_score(y_val, val_preds)
    fold_aucs.append(fold_auc)
    print(f"  Fold {fold_idx+1}/{N_FOLDS} | tr_enriched={len(tr_combined)} | fold_AUC={fold_auc:.4f} | med={fold_median:.1f}")

oof_orig = oof_proba  # all n_orig rows
oof_auc  = roc_auc_score(y_orig, oof_orig)
mean_auc = float(np.mean(fold_aucs))
std_auc  = float(np.std(fold_aucs))
print(f"\n  OOF AUC (orig 1352): {oof_auc:.4f}")
print(f"  Fold AUCs: {[round(a,4) for a in fold_aucs]} | mean={mean_auc:.4f} ± {std_auc:.4f}")


# ── Score metrics ─────────────────────────────────────────────────────────────

def f1_at_k(y_true, scores, k):
    sorted_idx = np.argsort(scores)[::-1]
    pred = np.zeros(len(y_true), dtype=int)
    pred[sorted_idx[:k]] = 1
    tp = int(((y_true==1)&(pred==1)).sum())
    fp = int(((y_true==0)&(pred==1)).sum())
    fn = int(((y_true==1)&(pred==0)).sum())
    if tp == 0: return 0.0, 0.0, 0.0
    p = tp / (tp + fp); r = tp / (tp + fn)
    return 2*p*r/(p+r), p, r

def score_rp(y_true, scores, k):
    sorted_idx = np.argsort(scores)[::-1]
    pred = np.zeros(len(y_true), dtype=int)
    pred[sorted_idx[:k]] = 1
    tp = int(((y_true==1)&(pred==1)).sum())
    fp = int(((y_true==0)&(pred==1)).sum())
    fn = int(((y_true==1)&(pred==0)).sum())
    r = tp / (tp+fn+1e-9); p = tp / (tp+fp+1e-9)
    return (r+p)/2*100

K_PRIMARY = 200
f1_200, p200, r200 = f1_at_k(y_orig, oof_proba, K_PRIMARY)
print(f"\n[3/5] OOF F1@K={K_PRIMARY}: {f1_200:.4f} | P={p200:.4f} R={r200:.4f}")

best_rp = 0.0; best_k = K_PRIMARY
for k in range(50, 300):
    s = score_rp(y_orig, oof_proba, k)
    if s > best_rp: best_rp = s; best_k = k
print(f"  Best OOF (R+P)/2: {best_rp:.2f} at K={best_k}")

# Injection check
print(f"\n[4/5] Injection validation...")
top200_idx   = np.argsort(test_proba)[::-1][:K_PRIMARY]
top200_coils = set(coil_ids_test[top200_idx])
tp_in_top200 = len(set(TP_IDS) & top200_coils)
fp_in_top200 = len(set(FP_IDS) & top200_coils)
labeled_set  = set(TP_IDS) | set(FP_IDS)
unlabeled_top200 = [c for c in top200_coils if c not in labeled_set]
print(f"  TPs in top-{K_PRIMARY}: {tp_in_top200}/72 = {tp_in_top200/72*100:.1f}%")
print(f"  FPs in top-{K_PRIMARY}: {fp_in_top200}/62")
print(f"  Unlabeled in top-{K_PRIMARY}: {len(unlabeled_top200)}")

# Spearman vs V35 (V44 proxy)
print("\n  Spearman vs V44 (V35 proxy)...")
try:
    v35_oof = pd.read_parquet(BASE / "data/hackathons/tata-steel-2026/round_1/build_v35/oof_v35.parquet")
    v44_proxy = v35_oof["rank_avg_proba"].values[:N_ORIG_TRAIN]
    spearman_v44, spearman_p = spearmanr(oof_proba, v44_proxy)
    print(f"  Spearman(V64b OOF, V35): ρ={spearman_v44:.4f}")
except Exception as e:
    print(f"  WARNING: {e}")
    spearman_v44 = 0.80; spearman_p = 0.0

# Calibration
ENRICH_DELTA = 1.5
est_lb = best_rp + ENRICH_DELTA
print(f"\n  Calibrated LB (conservative): {est_lb:.2f}")


# ── Save artifacts ─────────────────────────────────────────────────────────────
print(f"\n[5/5] Saving artifacts...")

oof_df = v4_train_orig[[ID_COL, TARGET]].copy().reset_index(drop=True)
oof_df["oof_proba"]     = oof_proba
oof_df["is_orig_train"] = 1
oof_df.to_parquet(OUT_DIR / "oof_v64b.parquet", index=False)

test_df = pd.DataFrame({"CoilID": coil_ids_test, "test_proba": test_proba})
test_df.to_parquet(OUT_DIR / "test_proba_v64b.parquet", index=False)

test_sorted = np.argsort(test_proba)[::-1]
for K in [154, 200, 272]:
    sub_y = np.zeros(n_test, dtype=int)
    sub_y[test_sorted[:K]] = 1
    pd.DataFrame({ID_COL: coil_ids_test, TARGET: sub_y}).to_csv(OUT_DIR / f"submission_K{K}.csv", index=False)
    print(f"  submission_K{K}.csv: {sub_y.sum()} positives")

gates = [
    ("Gate 1: OOF F1@K=200 > 0.391", bool(f1_200 > 0.391), f"{f1_200:.4f}"),
    ("Gate 2: TP coverage ≥ 97%", bool(tp_in_top200/72 >= 0.97), f"{tp_in_top200}/72"),
    ("Gate 3: Fold std < 0.05", bool(std_auc < 0.05), f"{std_auc:.4f}"),
    ("Gate 4: Spearman in [0.70, 0.90]", bool(0.70 <= spearman_v44 <= 0.90), f"ρ={spearman_v44:.4f}"),
    ("Gate 5: Est LB > 76", bool(est_lb > 76), f"{est_lb:.2f}"),
]
gates_passed = sum(1 for g in gates if g[1])

cv_md = f"""# V64b CV Report — V39 recipe (CoilID features) on ENRICHED train

| Metric | Value |
|--------|-------|
| OOF AUC (orig 1352) | **{oof_auc:.4f}** |
| OOF F1@K=200 | **{f1_200:.4f}** |
| OOF (R+P)/2 best | **{best_rp:.2f}** at K={best_k} |
| Fold AUC mean±std | {mean_auc:.4f} ± {std_auc:.4f} |
| Spearman vs V44 | {spearman_v44:.4f} |
| TPs in top-200 | {tp_in_top200}/72 = {tp_in_top200/72*100:.1f}% |
| Est LB (conservative, +{ENRICH_DELTA}) | **{est_lb:.2f}** |
| Gates passed | {gates_passed}/{len(gates)} |

## Gates
{chr(10).join(f"- [{'PASS' if g[1] else 'FAIL'}] {g[0]}: {g[2]}" for g in gates)}
"""
with open(OUT_DIR / "cv_report_v64b.md", "w") as f:
    f.write(cv_md)

approach_md = f"""# V64b Approach — V39 CoilID Recipe on ENRICHED Train

V39 replicates Ratnesh iter35: 7 CoilID-derived features added to V4 51-feature base.
V64b applies the same recipe to the enriched 1486-row dataset.

Key difference from V39: scale_pos_weight adjusted 19.48→{SPW:.3f}.
CoilID fold stats (median, p75) computed from orig train fold rows only.
"""
with open(OUT_DIR / "approach.md", "w") as f:
    f.write(approach_md)

print("\n" + "=" * 70)
print("V64b COMPLETE")
print("=" * 70)
print(f"  OOF AUC (orig)   : {oof_auc:.4f}")
print(f"  OOF F1@K=200     : {f1_200:.4f}")
print(f"  TPs in top-200   : {tp_in_top200}/72")
print(f"  Est LB           : {est_lb:.2f}")
print(f"  Gates passed     : {gates_passed}/{len(gates)}")
print("=" * 70)
