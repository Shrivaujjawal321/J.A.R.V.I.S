"""
V12 — Optuna deep tune + multi-seed bagging on V10's architecture.

Cycle 4 attempt:
  - Optuna 30 trials each on LGB, XGB, CatBoost (maximize 5-fold OOF AUC).
  - For each tuned config, multi-seed bagging (seeds 42, 13, 7) and average probas.
  - LR meta + Platt + gate-at-inference + score-aware threshold.
  - Blend with V5 + V9.
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
import lightgbm as lgb
import xgboost as xgb
from catboost import CatBoostClassifier
import optuna

warnings.filterwarnings("ignore")
optuna.logging.set_verbosity(optuna.logging.WARNING)

ROOT = Path("/home/ujjwal/Documents/J.A.R.V.I.S.")
V5 = ROOT / "data/hackathons/tata-steel-2026/round_1/build_v5"
V12 = ROOT / "data/hackathons/tata-steel-2026/round_1/build_v12"
V12.mkdir(parents=True, exist_ok=True)

SEED_MAIN = 42
SEEDS_BAG = [42, 13, 7]
N_FOLDS = 5
N_TRIALS = 30
CAL_DELTA = 2.67
X42_DEFECT_CEIL = 0.025067
X39_CLEAN_FLOOR = 169.0


def hard_gate(df):
    return ((df["X42"] > X42_DEFECT_CEIL) | (df["X39"] >= X39_CLEAN_FLOOR)).values


print("Loading V5 data...")
train_v5 = pd.read_parquet(V5 / "train_v5.parquet").reset_index(drop=True)
test_v5 = pd.read_parquet(V5 / "test_v5.parquet").reset_index(drop=True)
with open(V5 / "feature_list_v5.json") as f:
    v5_features = json.load(f)["features"]

y = train_v5["Y"].values.astype(int)
n_train, n_test = len(train_v5), len(test_v5)
X_tr = train_v5[v5_features].values
X_te = test_v5[v5_features].values
print(f"  train: {n_train}  test: {n_test}  defects: {y.sum()} ({y.mean()*100:.2f}%)")


def cv_score(model_factory, X, y, n_folds=N_FOLDS, seed=SEED_MAIN):
    """5-fold OOF AUC for the given model factory (returns AUC mean)."""
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)
    aucs = []
    for tr, va in skf.split(np.zeros(len(y)), y):
        m = model_factory()
        try:
            m.fit(X[tr], y[tr])
        except Exception:
            return 0.5
        try:
            p = m.predict_proba(X[va])[:, 1]
        except Exception:
            p = m.predict(X[va])
        aucs.append(roc_auc_score(y[va], p))
    return float(np.mean(aucs))


# ─── Phase A: Optuna tune LGB ────────────────────────────────────────────────
print("\n[Phase A] Optuna tune LGB (30 trials)")


def objective_lgb(trial):
    params = dict(
        n_estimators=trial.suggest_int("n_estimators", 200, 800, step=100),
        learning_rate=trial.suggest_float("learning_rate", 0.01, 0.1, log=True),
        max_depth=trial.suggest_int("max_depth", 4, 8),
        num_leaves=trial.suggest_int("num_leaves", 15, 63),
        min_child_samples=trial.suggest_int("min_child_samples", 5, 30),
        reg_alpha=trial.suggest_float("reg_alpha", 0.01, 1.0, log=True),
        reg_lambda=trial.suggest_float("reg_lambda", 0.01, 1.0, log=True),
        random_state=SEED_MAIN, verbose=-1,
        class_weight="balanced",
    )
    return cv_score(lambda: lgb.LGBMClassifier(**params), X_tr, y)


study_lgb = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=SEED_MAIN))
study_lgb.optimize(objective_lgb, n_trials=N_TRIALS, show_progress_bar=False, n_jobs=1)
best_lgb = study_lgb.best_params
best_lgb_auc = study_lgb.best_value
print(f"  Best LGB AUC: {best_lgb_auc:.4f}  params: {best_lgb}")


# ─── Phase B: Optuna tune XGB ────────────────────────────────────────────────
print("\n[Phase B] Optuna tune XGB (30 trials)")


def objective_xgb(trial):
    params = dict(
        n_estimators=trial.suggest_int("n_estimators", 200, 800, step=100),
        learning_rate=trial.suggest_float("learning_rate", 0.01, 0.1, log=True),
        max_depth=trial.suggest_int("max_depth", 4, 8),
        reg_alpha=trial.suggest_float("reg_alpha", 0.01, 1.0, log=True),
        reg_lambda=trial.suggest_float("reg_lambda", 0.01, 1.0, log=True),
        scale_pos_weight=(y == 0).sum() / max(y.sum(), 1),
        random_state=SEED_MAIN, eval_metric="auc",
        verbosity=0,
    )
    return cv_score(lambda: xgb.XGBClassifier(**params), X_tr, y)


study_xgb = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=SEED_MAIN))
study_xgb.optimize(objective_xgb, n_trials=N_TRIALS, show_progress_bar=False, n_jobs=1)
best_xgb = study_xgb.best_params
best_xgb_auc = study_xgb.best_value
print(f"  Best XGB AUC: {best_xgb_auc:.4f}  params: {best_xgb}")


# ─── Phase C: Optuna tune CatBoost ───────────────────────────────────────────
print("\n[Phase C] Optuna tune CatBoost (30 trials)")


def objective_cat(trial):
    params = dict(
        iterations=trial.suggest_int("iterations", 200, 800, step=100),
        learning_rate=trial.suggest_float("learning_rate", 0.01, 0.1, log=True),
        depth=trial.suggest_int("depth", 4, 8),
        l2_leaf_reg=trial.suggest_float("l2_leaf_reg", 1.0, 10.0, log=True),
        auto_class_weights="Balanced",
        random_seed=SEED_MAIN, verbose=False,
    )
    return cv_score(lambda: CatBoostClassifier(**params), X_tr, y)


study_cat = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=SEED_MAIN))
study_cat.optimize(objective_cat, n_trials=N_TRIALS, show_progress_bar=False, n_jobs=1)
best_cat = study_cat.best_params
best_cat_auc = study_cat.best_value
print(f"  Best CatBoost AUC: {best_cat_auc:.4f}  params: {best_cat}")


# ─── Phase D: multi-seed bagging + stacking ──────────────────────────────────
print("\n[Phase D] Multi-seed bagging (3 seeds) + 5-fold stacking")

skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED_MAIN)
oof_lgb = np.zeros(n_train)
oof_xgb = np.zeros(n_train)
oof_cat = np.zeros(n_train)
test_lgb = np.zeros(n_test)
test_xgb = np.zeros(n_test)
test_cat = np.zeros(n_test)
fold_aucs = {"lgb": [], "xgb": [], "cat": []}

for fold_i, (tr_idx, val_idx) in enumerate(skf.split(np.zeros(n_train), y)):
    print(f"  Fold {fold_i+1}/{N_FOLDS}: {y[tr_idx].sum()} pos train | {y[val_idx].sum()} pos val")

    Xtr = X_tr[tr_idx]
    Xva = X_tr[val_idx]
    Xte = X_te
    ytr = y[tr_idx]

    # LGB bag
    val_preds = []
    test_preds_seeds = []
    for s in SEEDS_BAG:
        p = best_lgb.copy()
        p["random_state"] = s
        p["verbose"] = -1
        p["class_weight"] = "balanced"
        m = lgb.LGBMClassifier(**p)
        m.fit(Xtr, ytr)
        val_preds.append(m.predict_proba(Xva)[:, 1])
        test_preds_seeds.append(m.predict_proba(Xte)[:, 1])
    oof_lgb[val_idx] = np.mean(val_preds, axis=0)
    test_lgb += np.mean(test_preds_seeds, axis=0) / N_FOLDS
    fold_aucs["lgb"].append(roc_auc_score(y[val_idx], oof_lgb[val_idx]))

    # XGB bag
    val_preds = []
    test_preds_seeds = []
    for s in SEEDS_BAG:
        p = best_xgb.copy()
        p["random_state"] = s
        p["scale_pos_weight"] = (ytr == 0).sum() / max(ytr.sum(), 1)
        p["eval_metric"] = "auc"
        p["verbosity"] = 0
        m = xgb.XGBClassifier(**p)
        m.fit(Xtr, ytr)
        val_preds.append(m.predict_proba(Xva)[:, 1])
        test_preds_seeds.append(m.predict_proba(Xte)[:, 1])
    oof_xgb[val_idx] = np.mean(val_preds, axis=0)
    test_xgb += np.mean(test_preds_seeds, axis=0) / N_FOLDS
    fold_aucs["xgb"].append(roc_auc_score(y[val_idx], oof_xgb[val_idx]))

    # Cat bag
    val_preds = []
    test_preds_seeds = []
    for s in SEEDS_BAG:
        p = best_cat.copy()
        p["random_seed"] = s
        p["auto_class_weights"] = "Balanced"
        p["verbose"] = False
        m = CatBoostClassifier(**p)
        m.fit(Xtr, ytr)
        val_preds.append(m.predict_proba(Xva)[:, 1])
        test_preds_seeds.append(m.predict_proba(Xte)[:, 1])
    oof_cat[val_idx] = np.mean(val_preds, axis=0)
    test_cat += np.mean(test_preds_seeds, axis=0) / N_FOLDS
    fold_aucs["cat"].append(roc_auc_score(y[val_idx], oof_cat[val_idx]))

    print(f"    LGB={fold_aucs['lgb'][-1]:.4f}  XGB={fold_aucs['xgb'][-1]:.4f}  CAT={fold_aucs['cat'][-1]:.4f}")

lgb_mean = float(np.mean(fold_aucs["lgb"]))
xgb_mean = float(np.mean(fold_aucs["xgb"]))
cat_mean = float(np.mean(fold_aucs["cat"]))
print(f"\nMulti-seed-bagged base AUCs:  LGB={lgb_mean:.4f}  XGB={xgb_mean:.4f}  CAT={cat_mean:.4f}")


# ─── Phase E: meta + gate + threshold sweep ─────────────────────────────────
print("\n[Phase E] Meta + gate + threshold + blend with V5/V9")

X_meta_oof = np.column_stack([oof_lgb, oof_xgb, oof_cat])
X_meta_test = np.column_stack([test_lgb, test_xgb, test_cat])
meta = LogisticRegression(C=1.0, max_iter=1000)
meta_cal = CalibratedClassifierCV(meta, method="sigmoid", cv=5)
meta_cal.fit(X_meta_oof, y)
p_oof = meta_cal.predict_proba(X_meta_oof)[:, 1]
p_test = meta_cal.predict_proba(X_meta_test)[:, 1]
meta_auc = float(roc_auc_score(y, p_oof))
print(f"  V12 Meta OOF AUC: {meta_auc:.4f}  (V5 was 0.8886, V10 blend 0.8936)")

gate_oof = hard_gate(train_v5)
gate_test = hard_gate(test_v5)
p_oof_g = p_oof.copy(); p_oof_g[gate_oof] = 0
p_test_g = p_test.copy(); p_test_g[gate_test] = 0

# Load V5 and V9 for blends
oof_v5 = pd.read_parquet(V5 / "oof_v5.parquet")["oof_meta"].values
test_v5_meta = pd.read_parquet(V5 / "test_meta_v5.parquet")["test_meta"].values
v9_dir = ROOT / "data/hackathons/tata-steel-2026/round_1/build_v9"
oof_v9 = pd.read_parquet(v9_dir / "oof_v9.parquet")["oof_meta_post_gate"].values
test_v9 = pd.read_parquet(v9_dir / "test_meta_v9.parquet")["test_meta_post_gate"].values


def sweep(p, y, p_test=None):
    uniq = np.sort(np.unique(np.concatenate([p, [0.0, 1.0]])))
    cuts = np.r_[uniq[0] - 1e-6, 0.5 * (uniq[:-1] + uniq[1:]), uniq[-1] + 1e-6]
    bT, bS, bR, bP, bN = 0, 0, 0, 0, 0
    for t in cuts:
        pred = (p >= t).astype(int)
        tp = ((pred == 1) & (y == 1)).sum()
        fp = ((pred == 1) & (y == 0)).sum()
        fn = ((pred == 0) & (y == 1)).sum()
        R = tp / (tp + fn) if (tp + fn) else 0
        P = tp / (tp + fp) if (tp + fp) else 0
        s = (R + P) / 2 * 100
        if s > bS:
            bS, bT, bR, bP, bN = s, t, R, P, pred.sum()
    return bT, bS, bR, bP, bN


print("\n  Variants:")
best_variant = None
for name, oof_b, test_b in [
    ("V12 alone", p_oof_g, p_test_g),
    ("V12+V5 mean", (p_oof_g + oof_v5) / 2, (p_test_g + test_v5_meta) / 2),
    ("V12+V9 mean", (p_oof_g + oof_v9) / 2, (p_test_g + test_v9) / 2),
    ("V12+V5+V9 mean", (p_oof_g + oof_v5 + oof_v9) / 3, (p_test_g + test_v5_meta + test_v9) / 3),
    ("V12+V5 60:40", 0.6 * p_oof_g + 0.4 * oof_v5, 0.6 * p_test_g + 0.4 * test_v5_meta),
    ("V12+V5+V9 50:25:25", 0.5*p_oof_g + 0.25*oof_v5 + 0.25*oof_v9, 0.5*p_test_g + 0.25*test_v5_meta + 0.25*test_v9),
]:
    T, s, R, P, n = sweep(oof_b, y)
    auc = roc_auc_score(y, oof_b)
    test_pred = (test_b >= T).astype(int)
    print(f"    {name:<28s}  AUC={auc:.4f}  OOF={s:.3f}  R={R:.3f}  P={P:.3f}  n_oof={n}  n_test={test_pred.sum()}")
    if best_variant is None or s > best_variant[2]:
        best_variant = (name, T, s, oof_b, test_b, test_pred, auc, R, P)

vname, vT, vS, voof, vtest, vpred, vauc, vR, vP = best_variant
print(f"\n  Best V12 variant: {vname}  OOF={vS:.3f}  AUC={vauc:.4f}")

# Bootstrap CI
rng = np.random.default_rng(SEED_MAIN)
boot = np.empty(2000)
for i in range(2000):
    idx = rng.integers(0, n_train, n_train)
    pred = (voof[idx] >= vT).astype(int)
    yb = y[idx]
    tp = ((pred == 1) & (yb == 1)).sum()
    fp = ((pred == 1) & (yb == 0)).sum()
    fn = ((pred == 0) & (yb == 1)).sum()
    R = tp / (tp + fn) if (tp + fn) else 0
    P = tp / (tp + fp) if (tp + fp) else 0
    boot[i] = (R + P) / 2 * 100
ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
cal_lb = vS + CAL_DELTA
print(f"  Bootstrap 95% CI: [{ci_lo:.2f}, {ci_hi:.2f}]")
print(f"  Calibrated LB est: {cal_lb:.2f}  (CI [{ci_lo+CAL_DELTA:.2f}, {ci_hi+CAL_DELTA:.2f}])")


# ─── Persist ─────────────────────────────────────────────────────────────────
sub = pd.DataFrame({"CoilID": test_v5["CoilID"].values, "Y": vpred})
sub.to_csv(V12 / "expected_submission.csv", index=False)

with open(V12 / "chosen_threshold_v12.json", "w") as f:
    json.dump({
        "best_variant": vname,
        "chosen_threshold": float(vT),
        "chosen_score_oof": float(vS),
        "recall_at_T": float(vR), "precision_at_T": float(vP),
        "n_pos_test": int(vpred.sum()),
        "v12_meta_auc": meta_auc,
        "blend_auc": float(vauc),
        "lb_estimate_corrected": float(cal_lb),
        "bootstrap_ci_oof": [float(ci_lo), float(ci_hi)],
        "bootstrap_ci_calibrated": [float(ci_lo + CAL_DELTA), float(ci_hi + CAL_DELTA)],
        "best_lgb_params": best_lgb,
        "best_xgb_params": best_xgb,
        "best_cat_params": best_cat,
        "tuned_aucs": {"lgb": best_lgb_auc, "xgb": best_xgb_auc, "cat": best_cat_auc},
        "bagged_fold_aucs": fold_aucs,
        "v4_actual_lb": 56.98113,
        "v10_calibrated": 58.14,
    }, f, indent=2)

with open(V12 / "approach.md", "w") as f:
    f.write(f"# V12 — Optuna tune + multi-seed bagging\n\nBest: {vname}\nMeta AUC: {meta_auc:.4f} | Blend AUC: {vauc:.4f}\nOOF: {vS:.2f} | Calibrated LB: {cal_lb:.2f} CI [{ci_lo+CAL_DELTA:.2f}, {ci_hi+CAL_DELTA:.2f}]\n")
import nbformat as nbf
nb = nbf.v4.new_notebook()
nb["cells"] = [nbf.v4.new_markdown_cell(f"# V12 {vname} OOF {vS:.2f}")]
with open(V12 / "solution.ipynb", "w") as f:
    nbf.write(nb, f)
with zipfile.ZipFile(V12 / "submission_v12.zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.write(V12 / "expected_submission.csv", "expected_submission.csv")
    z.write(V12 / "approach.md", "approach.md")
    z.write(V12 / "solution.ipynb", "solution.ipynb")

print("\n" + "=" * 60)
print("V12 FINAL SUMMARY")
print("=" * 60)
print(f"  Best variant:                    {vname}")
print(f"  V12 Meta OOF AUC:                {meta_auc:.4f}")
print(f"  Blend OOF AUC:                   {vauc:.4f}")
print(f"  OOF (R+P)/2:                     {vS:.2f}")
print(f"  Bootstrap 95% CI:                [{ci_lo:.2f}, {ci_hi:.2f}]")
print(f"  Calibrated LB estimate:          {cal_lb:.2f}")
print(f"  Calibrated CI:                   [{ci_lo+CAL_DELTA:.2f}, {ci_hi+CAL_DELTA:.2f}]")
print(f"  V4 actual / V10 calibrated:      56.98 / 58.14")
print(f"  Hits 90/80/70?                   {'Y' if cal_lb>=90 else 'N'}/{'Y' if cal_lb>=80 else 'N'}/{'Y' if cal_lb>=70 else 'N'}")
print("=" * 60)
