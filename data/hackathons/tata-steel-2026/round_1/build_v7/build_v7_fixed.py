"""
V7 FIXED — same chemistry + interactions as broken v7, but CV-safe Y_roll.

Bug in broken v7:
  fold_train_y = pd.Series(y_train[tr_idx])
  rs = fold_train_y.rolling(window=w).mean()
    - rolling included current row's Y label (target leakage)
    - rolling iterated shuffled fold-train indices, not CoilID temporal order
    - validation rows got a single scalar = distribution shift

Fix:
  Y_roll_N(coilid c) = mean of training-fold Y at coils with CoilID in [c-N, c-1]
  - sorted by CoilID, prev-N window, current row excluded
  - same function for train + val rows, using ONLY training fold's labels
  - test uses ALL-train labels (no test leakage)
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
import lightgbm as lgb
import xgboost as xgb
from catboost import CatBoostClassifier

ROOT = Path("/home/ujjwal/Documents/J.A.R.V.I.S.")
V5 = ROOT / "data/hackathons/tata-steel-2026/round_1/build_v5"
V7 = ROOT / "data/hackathons/tata-steel-2026/round_1/build_v7"
V7.mkdir(parents=True, exist_ok=True)

SEED = 42
ROLL_WINDOWS = [10, 20, 50]
N_FOLDS = 5

V4_LB = 56.98113
V5_OOF_SCORE = 53.70058610799352
CAL_DELTA = 2.67


def compute_y_roll(target_coilids: np.ndarray,
                   known_coilids: np.ndarray,
                   known_y: np.ndarray,
                   window: int) -> np.ndarray:
    """For each c in target_coilids, return mean of known_y at known_coilids in [c-window, c-1]."""
    # Build {coilid -> y} for fast lookup
    lookup = dict(zip(known_coilids.tolist(), known_y.tolist()))
    out = np.zeros(len(target_coilids), dtype=float)
    for i, c in enumerate(target_coilids):
        labels = [lookup[cc] for cc in range(int(c) - window, int(c)) if cc in lookup]
        out[i] = np.mean(labels) if labels else 0.0  # baseline = train prevalence ~0.049
    return out


print("Loading V5 features...")
train_v5 = pd.read_parquet(V5 / "train_v5.parquet")
test_v5 = pd.read_parquet(V5 / "test_v5.parquet")
with open(V5 / "feature_list_v5.json") as f:
    v5_features = json.load(f)["features"]

y_train = train_v5["Y"].values.astype(int)
coil_train = train_v5["CoilID"].values.astype(int)
coil_test = test_v5["CoilID"].values.astype(int)
n_train = len(train_v5)
n_test = len(test_v5)
print(f"  train: {n_train}  test: {n_test}  positives: {y_train.sum()}")


# ─── Phase A: chemistry + interaction features ───────────────────────────────
print("\n[Phase A] Chemistry + interaction features")


def add_chem(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["v7_log_X42"] = np.log(df["X42"] + 1e-6)
    df["v7_log_X46"] = np.log(df["X46"] + 1e-6)
    df["v7_X43_over_X41"] = df["X43"] / (df["X41"] + 1e-6)
    df["v7_X41_over_X42"] = df["X41"] / (df["X42"] + 1e-6)
    df["v7_X43_over_X42"] = df["X43"] / (df["X42"] + 1e-6)
    df["v7_CarbonEq_proxy"] = df["X41"] / 6 + df["X44"] / 5
    df["v7_X14_x_X41"] = df["X14"] * df["X41"]
    df["v7_X14_x_X49"] = df["X14"] * df["X49"]
    df["v7_X46_x_X49"] = df["X46"] * df["X49"]
    return df


train_v7 = add_chem(train_v5)
test_v7 = add_chem(test_v5)

V7_NEW_DET = [
    "X42", "X46",
    "v7_log_X42", "v7_log_X46",
    "v7_X43_over_X41",
    "v7_X41_over_X42",
    "v7_X43_over_X42",
    "v7_CarbonEq_proxy",
    "v7_X14_x_X41",
    "v7_X14_x_X49",
    "v7_X46_x_X49",
]
V7_ROLL = [f"v7_Y_roll{w}" for w in ROLL_WINDOWS]
v7_features = v5_features + V7_NEW_DET + V7_ROLL
print(f"  V5: {len(v5_features)} + new det: {len(V7_NEW_DET)} + Y_roll: {len(V7_ROLL)} = {len(v7_features)}")

# Pre-compute V7_ROLL columns as NaN placeholders (filled per fold for train, all-train for test)
for col in V7_ROLL:
    train_v7[col] = np.nan
    test_v7[col] = np.nan

# Test Y_roll: computed once using ALL train labels (no test leakage)
print("  computing test Y_roll using all-train labels...")
for w in ROLL_WINDOWS:
    test_v7[f"v7_Y_roll{w}"] = compute_y_roll(coil_test, coil_train, y_train, w)
print(f"  test Y_roll10 range: [{test_v7['v7_Y_roll10'].min():.4f}, {test_v7['v7_Y_roll10'].max():.4f}]")


# ─── Phase B: 5-fold stacking ────────────────────────────────────────────────
print("\n[Phase B] 5-fold stacking (seed=42)")

skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
oof_lgb = np.zeros(n_train)
oof_xgb = np.zeros(n_train)
oof_cat = np.zeros(n_train)
fold_aucs = {"lgb": [], "xgb": [], "cat": []}

test_lgb = np.zeros(n_test)
test_xgb = np.zeros(n_test)
test_cat = np.zeros(n_test)

DET_COLS = [c for c in v7_features if c not in V7_ROLL]

for fold_i, (tr_idx, val_idx) in enumerate(skf.split(np.zeros(n_train), y_train)):
    print(f"\n  Fold {fold_i+1}/{N_FOLDS}: {y_train[tr_idx].sum()} pos train | {y_train[val_idx].sum()} pos val")

    # CV-safe Y_roll: use ONLY training-fold labels + CoilID temporal order
    coil_tr = coil_train[tr_idx]
    y_tr = y_train[tr_idx]
    for w in ROLL_WINDOWS:
        col = f"v7_Y_roll{w}"
        # For training rows: use OTHER training rows' labels at CoilID in [c-N, c-1]
        train_roll = compute_y_roll(coil_tr, coil_tr, y_tr, w)
        train_v7.loc[train_v7.index[tr_idx], col] = train_roll
        # For validation rows: use training-fold labels (val labels unknown to model)
        val_roll = compute_y_roll(coil_train[val_idx], coil_tr, y_tr, w)
        train_v7.loc[train_v7.index[val_idx], col] = val_roll
        if fold_i == 0 and w == 10:
            print(f"    Y_roll{w} train range: [{train_roll.min():.4f}, {train_roll.max():.4f}]  val range: [{val_roll.min():.4f}, {val_roll.max():.4f}]")

    Xtr = train_v7.iloc[tr_idx][v7_features].values
    Xva = train_v7.iloc[val_idx][v7_features].values
    Xte = test_v7[v7_features].values
    ytr = y_train[tr_idx]
    yva = y_train[val_idx]

    # LGB
    m_lgb = lgb.LGBMClassifier(
        n_estimators=500, learning_rate=0.03, max_depth=6, num_leaves=31,
        min_child_samples=10, reg_alpha=0.1, reg_lambda=0.1,
        random_state=SEED, verbose=-1, class_weight="balanced",
    )
    m_lgb.fit(Xtr, ytr, eval_set=[(Xva, yva)], callbacks=[lgb.early_stopping(30, verbose=False)])
    oof_lgb[val_idx] = m_lgb.predict_proba(Xva)[:, 1]
    test_lgb += m_lgb.predict_proba(Xte)[:, 1] / N_FOLDS
    fold_aucs["lgb"].append(roc_auc_score(yva, oof_lgb[val_idx]))

    # XGB
    m_xgb = xgb.XGBClassifier(
        n_estimators=500, learning_rate=0.03, max_depth=6,
        scale_pos_weight=(ytr == 0).sum() / max(ytr.sum(), 1),
        reg_alpha=0.1, reg_lambda=0.1,
        random_state=SEED, eval_metric="auc",
        early_stopping_rounds=30, verbosity=0, use_label_encoder=False,
    )
    m_xgb.fit(Xtr, ytr, eval_set=[(Xva, yva)], verbose=False)
    oof_xgb[val_idx] = m_xgb.predict_proba(Xva)[:, 1]
    test_xgb += m_xgb.predict_proba(Xte)[:, 1] / N_FOLDS
    fold_aucs["xgb"].append(roc_auc_score(yva, oof_xgb[val_idx]))

    # CatBoost
    m_cat = CatBoostClassifier(
        iterations=500, learning_rate=0.03, depth=6,
        l2_leaf_reg=3.0,
        auto_class_weights="Balanced",
        random_seed=SEED, verbose=False,
        early_stopping_rounds=30,
    )
    m_cat.fit(Xtr, ytr, eval_set=(Xva, yva))
    oof_cat[val_idx] = m_cat.predict_proba(Xva)[:, 1]
    test_cat += m_cat.predict_proba(Xte)[:, 1] / N_FOLDS
    fold_aucs["cat"].append(roc_auc_score(yva, oof_cat[val_idx]))

    print(f"    LGB AUC={fold_aucs['lgb'][-1]:.4f}  XGB AUC={fold_aucs['xgb'][-1]:.4f}  CAT AUC={fold_aucs['cat'][-1]:.4f}")

lgb_mean = float(np.mean(fold_aucs["lgb"]))
xgb_mean = float(np.mean(fold_aucs["xgb"]))
cat_mean = float(np.mean(fold_aucs["cat"]))
print(f"\nBase model mean AUCs:  LGB={lgb_mean:.4f}  XGB={xgb_mean:.4f}  CAT={cat_mean:.4f}")


# ─── Phase C: meta learner ───────────────────────────────────────────────────
print("\n[Phase C] LR meta + Platt calibration")

X_meta_oof = np.column_stack([oof_lgb, oof_xgb, oof_cat])
X_meta_test = np.column_stack([test_lgb, test_xgb, test_cat])

meta_base = LogisticRegression(C=1.0, max_iter=1000)
meta_cal = CalibratedClassifierCV(meta_base, method="sigmoid", cv=5)
meta_cal.fit(X_meta_oof, y_train)
p_oof = meta_cal.predict_proba(X_meta_oof)[:, 1]
p_test = meta_cal.predict_proba(X_meta_test)[:, 1]

meta_auc = float(roc_auc_score(y_train, p_oof))
print(f"  Meta OOF AUC: {meta_auc:.4f}  (V5 was 0.8886)")


# ─── Phase D: score-aware threshold sweep ────────────────────────────────────
print("\n[Phase D] Score-aware threshold sweep")

uniq = np.sort(np.unique(np.concatenate([p_oof, [0.0, 1.0]])))
cuts = np.r_[uniq[0] - 1e-6, 0.5 * (uniq[:-1] + uniq[1:]), uniq[-1] + 1e-6]
best_T, best_score, best_R, best_P, best_npos = 0.0, 0.0, 0.0, 0.0, 0

for t in cuts:
    pred = (p_oof >= t).astype(int)
    tp = int(((pred == 1) & (y_train == 1)).sum())
    fp = int(((pred == 1) & (y_train == 0)).sum())
    fn = int(((pred == 0) & (y_train == 1)).sum())
    R = tp / (tp + fn) if (tp + fn) else 0
    P = tp / (tp + fp) if (tp + fp) else 0
    s = (R + P) / 2 * 100
    if s > best_score:
        best_score, best_T = s, float(t)
        best_R, best_P = float(R), float(P)
        best_npos = int(pred.sum())

print(f"  Best T={best_T:.6f}  Score={best_score:.4f}  R={best_R:.4f}  P={best_P:.4f}  n_pos={best_npos}")


# ─── Phase E: bootstrap CI ───────────────────────────────────────────────────
print("\n[Phase E] Bootstrap 95% CI on V7 score")
rng = np.random.default_rng(SEED)
boot = np.empty(2000)
for i in range(2000):
    idx = rng.integers(0, n_train, n_train)
    pred = (p_oof[idx] >= best_T).astype(int)
    yb = y_train[idx]
    tp = ((pred == 1) & (yb == 1)).sum()
    fp = ((pred == 1) & (yb == 0)).sum()
    fn = ((pred == 0) & (yb == 1)).sum()
    R = tp / (tp + fn) if (tp + fn) else 0
    P = tp / (tp + fp) if (tp + fp) else 0
    boot[i] = (R + P) / 2 * 100
ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
boot_mean = float(boot.mean())
print(f"  Bootstrap mean={boot_mean:.4f}  95% CI=[{ci_lo:.4f}, {ci_hi:.4f}]")

corrected_lb = best_score + CAL_DELTA
print(f"  +V4 calibration delta {CAL_DELTA} -> corrected LB estimate: {corrected_lb:.2f}  (range [{ci_lo+CAL_DELTA:.2f}, {ci_hi+CAL_DELTA:.2f}])")


# ─── Phase F: V7+V5 blend ────────────────────────────────────────────────────
print("\n[Phase F] V7 + V5 blend search")
oof_v5_df = pd.read_parquet(V5 / "oof_v5.parquet")
test_meta_v5_df = pd.read_parquet(V5 / "test_meta_v5.parquet")
p_oof_v5 = oof_v5_df["oof_meta"].values
p_test_v5 = test_meta_v5_df["test_meta"].values

blend_results = {}
best_blend_w, best_blend_score, best_blend_T = 0.5, 0.0, 0.0
for w in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
    p_blend_oof = w * p_oof + (1 - w) * p_oof_v5
    uniq_b = np.sort(np.unique(np.concatenate([p_blend_oof, [0.0, 1.0]])))
    cuts_b = np.r_[uniq_b[0] - 1e-6, 0.5 * (uniq_b[:-1] + uniq_b[1:]), uniq_b[-1] + 1e-6]
    bT, bS = 0.0, 0.0
    for t in cuts_b:
        pred = (p_blend_oof >= t).astype(int)
        tp = ((pred == 1) & (y_train == 1)).sum()
        fp = ((pred == 1) & (y_train == 0)).sum()
        fn = ((pred == 0) & (y_train == 1)).sum()
        R = tp / (tp + fn) if (tp + fn) else 0
        P = tp / (tp + fp) if (tp + fp) else 0
        s = (R + P) / 2 * 100
        if s > bS:
            bS, bT = s, float(t)
    blend_results[w] = {"score": bS, "threshold": bT}
    print(f"  V7 weight {w:.1f}: score={bS:.4f} @ T={bT:.6f}")
    if bS > best_blend_score:
        best_blend_score, best_blend_T, best_blend_w = bS, bT, w

print(f"\n  Best blend: V7@{best_blend_w:.1f} + V5@{1-best_blend_w:.1f}, score={best_blend_score:.4f} @ T={best_blend_T:.6f}")


# ─── Phase G: pick best submission variant + write CSV/zip ───────────────────
print("\n[Phase G] Pick best variant")

variants = {
    "v7_standalone": {"p_test": p_test, "T": best_T, "oof_score": best_score},
    f"v7_blend_w{best_blend_w}": {
        "p_test": best_blend_w * p_test + (1 - best_blend_w) * p_test_v5,
        "T": best_blend_T,
        "oof_score": best_blend_score,
    },
}
chosen_name, chosen_info = max(variants.items(), key=lambda kv: kv[1]["oof_score"])
print(f"  CHOSEN: {chosen_name}  OOF={chosen_info['oof_score']:.4f}")

# Generate all submission CSVs
for name, info in variants.items():
    sub = pd.DataFrame({
        "CoilID": coil_test,
        "Y": (info["p_test"] >= info["T"]).astype(int),
    })
    fname = V7 / f"expected_submission_{name}.csv"
    sub.to_csv(fname, index=False)
    print(f"  wrote {fname.name}: n_pos={int(sub['Y'].sum())}/{n_test}")

# Final submission CSV = chosen variant
chosen_sub = pd.DataFrame({
    "CoilID": coil_test,
    "Y": (chosen_info["p_test"] >= chosen_info["T"]).astype(int),
})
chosen_sub.to_csv(V7 / "expected_submission.csv", index=False)
print(f"  wrote expected_submission.csv (the headline): n_pos={int(chosen_sub['Y'].sum())}")


# ─── Persist artifacts ───────────────────────────────────────────────────────
print("\n[Persist]")

# OOF + test_meta parquets
pd.DataFrame({"oof_lgb": oof_lgb, "oof_xgb": oof_xgb, "oof_cat": oof_cat, "oof_meta": p_oof, "Y": y_train}).to_parquet(V7 / "oof_v7_fixed.parquet")
pd.DataFrame({"test_lgb": test_lgb, "test_xgb": test_xgb, "test_cat": test_cat, "test_meta": p_test}).to_parquet(V7 / "test_meta_v7_fixed.parquet")

chosen_threshold = {
    "chosen_variant": chosen_name,
    "chosen_score_oof": chosen_info["oof_score"],
    "chosen_threshold": chosen_info["T"],
    "meta_oof_auc_v7": meta_auc,
    "recall_at_T": best_R,
    "precision_at_T": best_P,
    "n_pos_test_chosen": int(chosen_sub["Y"].sum()),
    "v7_standalone_score": best_score,
    "v7_standalone_T": best_T,
    "best_blend_weight": best_blend_w,
    "best_blend_score": best_blend_score,
    "best_blend_T": best_blend_T,
    "bootstrap_mean": boot_mean,
    "bootstrap_ci_lo": float(ci_lo),
    "bootstrap_ci_hi": float(ci_hi),
    "calibration_correction": CAL_DELTA,
    "lb_estimate_corrected": float(corrected_lb),
    "v4_actual_lb": V4_LB,
    "v5_oof_score": V5_OOF_SCORE,
    "delta_v5": float(chosen_info["oof_score"] - V5_OOF_SCORE),
    "delta_vs_v4_lb": float(corrected_lb - V4_LB),
}
with open(V7 / "chosen_threshold_v7_fixed.json", "w") as f:
    json.dump(chosen_threshold, f, indent=2)
print(f"  wrote chosen_threshold_v7_fixed.json")

summary = {
    "n_features": len(v7_features),
    "v7_new_det": V7_NEW_DET,
    "v7_roll": V7_ROLL,
    "base_aucs": {"lgb": lgb_mean, "xgb": xgb_mean, "cat": cat_mean},
    "meta_oof_auc_v7": meta_auc,
    "meta_oof_auc_v5": 0.8886139780385504,
    "delta_meta_auc": meta_auc - 0.8886139780385504,
    "v7_standalone_oof_score": best_score,
    "v5_oof_score": V5_OOF_SCORE,
    "v6_blend_oof_score": 54.11,
    "v7_blend_oof_score": best_blend_score,
    "best_variant": chosen_name,
    "bootstrap_ci_oof": [float(ci_lo), float(ci_hi)],
    "lb_estimate": float(corrected_lb),
    "fold_aucs": fold_aucs,
}
with open(V7 / "v7_stacking_summary_fixed.json", "w") as f:
    json.dump(summary, f, indent=2)
print(f"  wrote v7_stacking_summary_fixed.json")

# Final headline
print("\n" + "=" * 60)
print("V7 FIXED FINAL SUMMARY")
print("=" * 60)
print(f"  V4 actual LB:                   56.98 (banked)")
print(f"  V5 OOF score:                   53.70")
print(f"  V6+V5 blend OOF (broken arch):  54.11")
print(f"  V7 standalone OOF:              {best_score:.2f}")
print(f"  V7+V5 best blend OOF:           {best_blend_score:.2f}  (w={best_blend_w})")
print(f"  Chosen variant:                 {chosen_name}")
print(f"  Meta AUC V7:                    {meta_auc:.4f}  (V5 was 0.8886)")
print(f"  Bootstrap 95% CI on chosen:     [{ci_lo:.2f}, {ci_hi:.2f}]")
print(f"  V4-calibrated LB estimate:      {corrected_lb:.2f}")
print(f"  Submit V7?                      {'YES' if corrected_lb > V4_LB + 0.5 else 'NO — keeps V4 banked'}")
print("=" * 60)
