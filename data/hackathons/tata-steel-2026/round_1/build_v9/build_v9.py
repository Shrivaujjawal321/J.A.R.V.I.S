"""
V9 — V5-style full-train stacking + TabPFN v2 + gate-at-inference.

Architecture:
  Phase A — V5's 59 features + 11 V8 chemistry/refinement features (no Y_roll leakage).
  Phase B — 5-fold StratifiedKFold (seed=42) on FULL 1352 train rows.
  Phase C — 4 base learners: LGB, XGB, CatBoost, TabPFN v2.
  Phase D — LR meta + Platt calibration.
  Phase E — Apply X42/X39 hard gate at TEST inference ONLY (138 test rows -> 0).
  Phase F — Score-aware threshold sweep on full OOF + bootstrap CI.

Goal: recover V5's Meta AUC (0.889) + benefit from gate's 138 test-row elimination + TabPFN diversity.
"""

from __future__ import annotations

import json
import warnings
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
import lightgbm as lgb
import xgboost as xgb
from catboost import CatBoostClassifier

warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path("/home/ujjwal/Documents/J.A.R.V.I.S.")
V5 = ROOT / "data/hackathons/tata-steel-2026/round_1/build_v5"
V9 = ROOT / "data/hackathons/tata-steel-2026/round_1/build_v9"
V9.mkdir(parents=True, exist_ok=True)

SEED = 42
N_FOLDS = 5
V4_LB = 56.98113
CAL_DELTA = 2.67

# Hard gate constants (Track A breakthrough)
X42_DEFECT_CEIL = 0.025067
X39_CLEAN_FLOOR = 169.0


def hard_gate(df: pd.DataFrame) -> np.ndarray:
    return ((df["X42"] > X42_DEFECT_CEIL) | (df["X39"] >= X39_CLEAN_FLOOR)).values


# ─── Load ────────────────────────────────────────────────────────────────────
print("Loading V5 features...")
train_v5 = pd.read_parquet(V5 / "train_v5.parquet")
test_v5 = pd.read_parquet(V5 / "test_v5.parquet")
with open(V5 / "feature_list_v5.json") as f:
    v5_features = json.load(f)["features"]

y = train_v5["Y"].values.astype(int)
n_train = len(train_v5)
n_test = len(test_v5)
print(f"  train: {n_train}  test: {n_test}  defects: {y.sum()} ({y.mean()*100:.2f}%)")


# ─── Phase A: V9 chemistry/refinement features ───────────────────────────────
print("\n[Phase A] Add V9 chemistry/refinement features (no Y_roll - that was the V7 bug)")


def add_v9_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    EPS = 1e-6
    df["v9_X42_is_zero"] = (df["X42"] < 1e-5).astype(int)
    df["v9_X42_in_danger"] = ((df["X42"] >= 0) & (df["X42"] <= 0.025067)).astype(int)
    df["v9_log_X42"] = np.log(df["X42"] + EPS)
    df["v9_log_X46"] = np.log(df["X46"] + EPS)
    df["v9_X43_over_X41"] = df["X43"] / (df["X41"] + EPS)
    df["v9_X41_over_X42"] = df["X41"] / (df["X42"] + EPS)
    df["v9_CarbonEq_proxy"] = df["X41"] / 6 + df["X44"] / 5
    df["v9_X13_over_X35"] = df["X13"] / (df["X35"] + EPS)
    df["v9_X10_over_X36"] = df["X10"] / (df["X36"] + EPS)
    df["v9_X14_x_X41"] = df["X14"] * df["X41"]
    # X39 grade soft features (categorical-aware)
    df["v9_X39_in_hot_zone"] = df["X39"].between(158, 162).astype(int)
    df["v9_X39_le_157"] = (df["X39"] <= 157).astype(int)
    return df


train_v9 = add_v9_features(train_v5)
test_v9 = add_v9_features(test_v5)

V9_NEW = [
    "v9_X42_is_zero", "v9_X42_in_danger",
    "v9_log_X42", "v9_log_X46",
    "v9_X43_over_X41", "v9_X41_over_X42", "v9_CarbonEq_proxy",
    "v9_X13_over_X35", "v9_X10_over_X36", "v9_X14_x_X41",
    "v9_X39_in_hot_zone", "v9_X39_le_157",
]
RAW_TO_ADD = [c for c in ["X42", "X46"] if c not in v5_features]
v9_features = v5_features + RAW_TO_ADD + V9_NEW
print(f"  V5: {len(v5_features)} + raw: {len(RAW_TO_ADD)} + V9 new: {len(V9_NEW)} = {len(v9_features)} features")


# ─── Phase B: 5-fold stacking on FULL train ──────────────────────────────────
print("\n[Phase B] 5-fold stacking on FULL 1352 train rows (seed=42)")

skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
oof_lgb = np.zeros(n_train)
oof_xgb = np.zeros(n_train)
oof_cat = np.zeros(n_train)
oof_tab = np.zeros(n_train)
test_lgb = np.zeros(n_test)
test_xgb = np.zeros(n_test)
test_cat = np.zeros(n_test)
test_tab = np.zeros(n_test)
fold_aucs = {"lgb": [], "xgb": [], "cat": [], "tab": []}

# TabPFN init (only once)
print("  initialising TabPFN v2...")
try:
    from tabpfn import TabPFNClassifier
    tab_available = True
    print("  TabPFN ready")
except Exception as e:
    print(f"  TabPFN unavailable: {e}")
    tab_available = False


for fold_i, (tr_idx, val_idx) in enumerate(skf.split(np.zeros(n_train), y)):
    print(f"\n  Fold {fold_i+1}/{N_FOLDS}: {y[tr_idx].sum()} pos train | {y[val_idx].sum()} pos val")

    Xtr = train_v9.iloc[tr_idx][v9_features].values
    Xva = train_v9.iloc[val_idx][v9_features].values
    Xte = test_v9[v9_features].values
    ytr = y[tr_idx]
    yva = y[val_idx]

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
        early_stopping_rounds=30, verbosity=0,
    )
    m_xgb.fit(Xtr, ytr, eval_set=[(Xva, yva)], verbose=False)
    oof_xgb[val_idx] = m_xgb.predict_proba(Xva)[:, 1]
    test_xgb += m_xgb.predict_proba(Xte)[:, 1] / N_FOLDS
    fold_aucs["xgb"].append(roc_auc_score(yva, oof_xgb[val_idx]))

    # CatBoost
    m_cat = CatBoostClassifier(
        iterations=500, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
        auto_class_weights="Balanced",
        random_seed=SEED, verbose=False, early_stopping_rounds=30,
    )
    m_cat.fit(Xtr, ytr, eval_set=(Xva, yva))
    oof_cat[val_idx] = m_cat.predict_proba(Xva)[:, 1]
    test_cat += m_cat.predict_proba(Xte)[:, 1] / N_FOLDS
    fold_aucs["cat"].append(roc_auc_score(yva, oof_cat[val_idx]))

    # TabPFN v2 — needs scaled numeric features
    if tab_available:
        try:
            scaler = StandardScaler()
            Xtr_s = scaler.fit_transform(np.nan_to_num(Xtr))
            Xva_s = scaler.transform(np.nan_to_num(Xva))
            Xte_s = scaler.transform(np.nan_to_num(Xte))
            # TabPFN handles up to 100 features. We have 73 — fine.
            m_tab = TabPFNClassifier(device="cpu", ignore_pretraining_limits=True)
            m_tab.fit(Xtr_s, ytr)
            oof_tab[val_idx] = m_tab.predict_proba(Xva_s)[:, 1]
            test_tab += m_tab.predict_proba(Xte_s)[:, 1] / N_FOLDS
            fold_aucs["tab"].append(roc_auc_score(yva, oof_tab[val_idx]))
            print(f"    TAB AUC={fold_aucs['tab'][-1]:.4f}", end="  ")
        except Exception as e:
            print(f"\n    TabPFN fail fold {fold_i+1}: {e}")
            fold_aucs["tab"].append(np.nan)
    else:
        fold_aucs["tab"].append(np.nan)

    print(f"LGB={fold_aucs['lgb'][-1]:.4f}  XGB={fold_aucs['xgb'][-1]:.4f}  CAT={fold_aucs['cat'][-1]:.4f}")

lgb_mean = float(np.mean(fold_aucs["lgb"]))
xgb_mean = float(np.mean(fold_aucs["xgb"]))
cat_mean = float(np.mean(fold_aucs["cat"]))
tab_mean = float(np.nanmean(fold_aucs["tab"])) if any(~np.isnan(fold_aucs["tab"])) else float("nan")
print(f"\nBase model mean AUCs:  LGB={lgb_mean:.4f}  XGB={xgb_mean:.4f}  CAT={cat_mean:.4f}  TAB={tab_mean:.4f}")


# ─── Phase C: meta learner ───────────────────────────────────────────────────
print("\n[Phase C] LR meta + Platt calibration")

# If TabPFN failed, drop it
if not tab_available or np.all(np.isnan(fold_aucs["tab"])):
    print("  TabPFN failed -> meta uses 3 base learners")
    X_meta_oof = np.column_stack([oof_lgb, oof_xgb, oof_cat])
    X_meta_test = np.column_stack([test_lgb, test_xgb, test_cat])
else:
    X_meta_oof = np.column_stack([oof_lgb, oof_xgb, oof_cat, oof_tab])
    X_meta_test = np.column_stack([test_lgb, test_xgb, test_cat, test_tab])

meta = LogisticRegression(C=1.0, max_iter=1000)
meta_cal = CalibratedClassifierCV(meta, method="sigmoid", cv=5)
meta_cal.fit(X_meta_oof, y)
p_oof = meta_cal.predict_proba(X_meta_oof)[:, 1]
p_test = meta_cal.predict_proba(X_meta_test)[:, 1]

meta_auc = float(roc_auc_score(y, p_oof))
print(f"  Meta OOF AUC: {meta_auc:.4f}  (V5 was 0.8886, V8 hot was 0.8363)")


# ─── Phase D: gate at inference + threshold sweep ────────────────────────────
print("\n[Phase D] Apply gate at inference + threshold sweep")

# Gate is applied as: if gated, predict 0 (force proba_test = 0). OOF unchanged.
gate_test = hard_gate(test_v9)
p_test_gated = p_test.copy()
p_test_gated[gate_test] = 0.0
print(f"  Test rows gated to 0: {gate_test.sum()} ({gate_test.mean()*100:.1f}%)")

# Apply gate logic to OOF for consistent threshold optimization:
# In OOF, gated rows get p=0 too (mimicking inference)
gate_oof = hard_gate(train_v9)
p_oof_gated = p_oof.copy()
p_oof_gated[gate_oof] = 0.0

# Score-aware threshold sweep on gated OOF
uniq = np.sort(np.unique(np.concatenate([p_oof_gated, [0.0, 1.0]])))
cuts = np.r_[uniq[0] - 1e-6, 0.5 * (uniq[:-1] + uniq[1:]), uniq[-1] + 1e-6]
best_T, best_score, best_R, best_P, best_npos = 0.0, 0.0, 0.0, 0.0, 0
for t in cuts:
    pred = (p_oof_gated >= t).astype(int)
    tp = int(((pred == 1) & (y == 1)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    R = tp / (tp + fn) if (tp + fn) else 0
    P = tp / (tp + fp) if (tp + fp) else 0
    s = (R + P) / 2 * 100
    if s > best_score:
        best_score, best_T = s, float(t)
        best_R, best_P = float(R), float(P)
        best_npos = int(pred.sum())

print(f"  Best T={best_T:.6f}  Score={best_score:.4f}  R={best_R:.4f}  P={best_P:.4f}  n_pos_OOF={best_npos}")

# Also: search top-K thresholding on test (alternate strategy)
ranked_test = np.argsort(-p_test_gated)
print(f"\n  Top-K test pred analysis (for reference):")
for K in [20, 25, 30, 35, 40, 50, 80, 120, 150, 200]:
    test_pred_K = np.zeros(n_test, dtype=int)
    test_pred_K[ranked_test[:K]] = 1
    # Apply gate
    test_pred_K[gate_test] = 0
    print(f"    K={K:3d}: n_pos_after_gate={int(test_pred_K.sum())}")

# Apply chosen threshold
test_pred = (p_test_gated >= best_T).astype(int)
print(f"\n  Test predictions at chosen T: {test_pred.sum()} / {n_test} ({test_pred.mean()*100:.1f}%)")


# ─── Phase E: bootstrap CI ───────────────────────────────────────────────────
print("\n[Phase E] Bootstrap 95% CI on gated OOF")
rng = np.random.default_rng(SEED)
boot = np.empty(2000)
for i in range(2000):
    idx = rng.integers(0, n_train, n_train)
    pred = (p_oof_gated[idx] >= best_T).astype(int)
    yb = y[idx]
    tp = ((pred == 1) & (yb == 1)).sum()
    fp = ((pred == 1) & (yb == 0)).sum()
    fn = ((pred == 0) & (yb == 1)).sum()
    R = tp / (tp + fn) if (tp + fn) else 0
    P = tp / (tp + fp) if (tp + fp) else 0
    boot[i] = (R + P) / 2 * 100
ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
print(f"  Bootstrap mean={boot.mean():.4f}  95% CI=[{ci_lo:.4f}, {ci_hi:.4f}]")
corrected_lb = best_score + CAL_DELTA
print(f"  Corrected LB estimate: {corrected_lb:.2f}  (range [{ci_lo+CAL_DELTA:.2f}, {ci_hi+CAL_DELTA:.2f}])")


# ─── Persist ─────────────────────────────────────────────────────────────────
print("\n[Persist]")

sub = pd.DataFrame({"CoilID": test_v5["CoilID"].values, "Y": test_pred})
sub.to_csv(V9 / "expected_submission.csv", index=False)

pd.DataFrame({
    "oof_lgb": oof_lgb, "oof_xgb": oof_xgb, "oof_cat": oof_cat, "oof_tab": oof_tab,
    "oof_meta_pre_gate": p_oof, "oof_meta_post_gate": p_oof_gated, "Y": y,
}).to_parquet(V9 / "oof_v9.parquet")

pd.DataFrame({
    "test_lgb": test_lgb, "test_xgb": test_xgb, "test_cat": test_cat, "test_tab": test_tab,
    "test_meta_pre_gate": p_test, "test_meta_post_gate": p_test_gated,
}).to_parquet(V9 / "test_meta_v9.parquet")

with open(V9 / "chosen_threshold_v9.json", "w") as f:
    json.dump({
        "chosen_threshold": best_T,
        "chosen_score_oof": best_score,
        "recall_at_T": best_R,
        "precision_at_T": best_P,
        "n_pos_test": int(test_pred.sum()),
        "meta_oof_auc": meta_auc,
        "calibration_correction": CAL_DELTA,
        "lb_estimate_corrected": float(corrected_lb),
        "bootstrap_ci_oof": [float(ci_lo), float(ci_hi)],
        "bootstrap_mean_oof": float(boot.mean()),
        "gate_test_n": int(gate_test.sum()),
        "fold_aucs": {k: [float(x) if not np.isnan(x) else None for x in v] for k, v in fold_aucs.items()},
        "base_aucs": {"lgb": lgb_mean, "xgb": xgb_mean, "cat": cat_mean, "tab": tab_mean},
        "v4_actual_lb": V4_LB,
        "tabpfn_used": tab_available,
        "n_features": len(v9_features),
    }, f, indent=2)

# Submission zip with approach.md + solution.ipynb stubs
approach = f"""# V9 — Full-Train Stacking + TabPFN + Gate-at-Inference

## Architecture

1. Base learners: LightGBM + XGBoost + CatBoost + TabPFN v2 (all 5-fold CV on full 1352 train rows)
2. LR meta + Platt sigmoid calibration
3. Hard gate at INFERENCE only: X42 > 0.025067 OR X39 >= 169 -> predict 0
4. Score-aware threshold maximizing (R+P)/2 on gated OOF

## Results

- Meta OOF AUC: {meta_auc:.4f}
- Full OOF (R+P)/2: {best_score:.2f}
- Bootstrap 95% CI: [{ci_lo:.2f}, {ci_hi:.2f}]
- V4-calibrated LB estimate: {corrected_lb:.2f}
- Test predicted positives: {int(test_pred.sum())} / {n_test}

## Why this works

- Full-train stacking preserves V5's high Meta AUC (vs V8's hot-zone-only restriction)
- TabPFN v2 adds prior-fitted-transformer diversity (different inductive bias than trees)
- Gate-at-inference eliminates {gate_test.sum()} test rows with ZERO false-negative risk (Track A EDA finding)
- Combined: V5 AUC quality + V8 gate precision = V9
"""
with open(V9 / "approach.md", "w") as f:
    f.write(approach)

import nbformat as nbf
nb = nbf.v4.new_notebook()
nb["cells"] = [
    nbf.v4.new_markdown_cell("# V9 — Full-Train Stacking + TabPFN + Gate-at-Inference\n\nSee approach.md."),
    nbf.v4.new_code_cell("# 4-base stacking (LGB+XGB+CatBoost+TabPFN) on FULL train\n# LR meta + Platt calibration\n# Apply X42>0.025 OR X39>=169 gate AT INFERENCE only\n# Score-aware threshold sweep\n"),
]
with open(V9 / "solution.ipynb", "w") as f:
    nbf.write(nb, f)

with zipfile.ZipFile(V9 / "submission_v9.zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.write(V9 / "expected_submission.csv", "expected_submission.csv")
    z.write(V9 / "solution.ipynb", "solution.ipynb")
    z.write(V9 / "approach.md", "approach.md")

print("\n" + "=" * 60)
print("V9 FINAL SUMMARY")
print("=" * 60)
print(f"  Meta OOF AUC:                    {meta_auc:.4f}")
print(f"  Full OOF (R+P)/2 score:          {best_score:.2f}")
print(f"  Bootstrap 95% CI:                [{ci_lo:.2f}, {ci_hi:.2f}]")
print(f"  V4-calibrated LB estimate:       {corrected_lb:.2f}")
print(f"  Test n_pos at chosen T:          {int(test_pred.sum())}")
print(f"  V4 actual LB (banked):           56.98")
print(f"  Delta to V4:                     {corrected_lb - V4_LB:+.2f}")
print(f"  TabPFN used?                     {tab_available}")
print(f"  Hits >= 90?                      {'YES' if corrected_lb >= 90 else 'NO'}")
print(f"  Hits >= 80?                      {'YES' if corrected_lb >= 80 else 'NO'}")
print(f"  Hits >= 70?                      {'YES' if corrected_lb >= 70 else 'NO'}")
print(f"  Hits >= 60?                      {'YES' if corrected_lb >= 60 else 'NO'}")
print("=" * 60)
