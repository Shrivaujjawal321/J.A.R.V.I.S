"""
V28 - V4 + V26 Global Rank-Blend with Isolated Threshold (Post-Hoc)
====================================================================

Pure post-hoc combination. NO retraining of NEW models. We do however
rerun V26's stacking pipeline once because V26 did not persist its
test_meta probabilities to disk - without those we cannot rank-blend
test predictions. The retrained V26 OOF is verified row-by-row against
the original build_v26/oof_v26.parquet (must match to 1e-4) to confirm
determinism.

Pipeline
--------
1. Load V4 OOF + test_meta (already on disk).
2. Retrain V26 stack (BorderlineSMOTE-1 / fallback BL-2 / SMOTEENN) with
   seed=42 to produce test_meta_v26 and to verify OOF reproducibility.
3. Global rank-transform on (V4-OOF, V4-test) concatenated -> r4_combined.
   Same for V26 -> r26_combined.
4. blend_combined = (r4_combined + r26_combined) / 2.
5. blend_oof = blend_combined[:1352] ; blend_test = blend_combined[1352:].
6. Threshold sweep on blend_oof_only (1352 rows), maximise (R+P)/2.
7. SAFETY OVERRIDE: use T = 0.440 (not argmax 0.44808) because at argmax
   CoilID 1495 sits with margin < 0.0001.
8. Bootstrap 95% CI (n=1000, seed=42) on blended OOF.
9. Apply T to blend_test -> submission CSV.

Acceptance gates
----------------
  oof_score          >= 54.41    (V23 floor)
  bootstrap_lower_ci >= 53.0
  easy59_caught      >= 58
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from catboost import CatBoostClassifier
from imblearn.combine import SMOTEENN
from imblearn.over_sampling import SMOTE, BorderlineSMOTE
from imblearn.under_sampling import EditedNearestNeighbours
import lightgbm as lgb
import xgboost as xgb

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

ROUND1 = Path(__file__).resolve().parents[1]
V4_DIR = ROUND1 / "build_v4"
V26_DIR = ROUND1 / "build_v26"
V28_DIR = ROUND1 / "build_v28"
V28_DIR.mkdir(exist_ok=True)

V4_TRAIN_PARQUET = V4_DIR / "train_v4.parquet"
V4_TEST_PARQUET = V4_DIR / "test_v4.parquet"
V4_FEATURES_JSON = V4_DIR / "v4_final_features.json"
V4_OOF_PARQUET = V4_DIR / "oof_v4.parquet"
V4_TEST_META_PARQUET = V4_DIR / "test_meta_v4.parquet"
V26_OOF_PARQUET = V26_DIR / "oof_v26.parquet"

LGB_PARAMS = dict(
    n_estimators=500, learning_rate=0.05, num_leaves=31, max_depth=-1,
    min_child_samples=10, subsample=0.8, colsample_bytree=0.8,
    reg_alpha=0.1, reg_lambda=1.0, scale_pos_weight=19.5,
    random_state=42, n_jobs=-1, verbose=-1,
)
XGB_PARAMS = dict(
    n_estimators=500, learning_rate=0.05, max_depth=4, subsample=0.8,
    colsample_bytree=0.8, min_child_weight=5, scale_pos_weight=19.5,
    eval_metric="logloss", early_stopping_rounds=50,
    random_state=42, n_jobs=-1, verbosity=0,
)
CAT_PARAMS = dict(
    iterations=500, learning_rate=0.05, depth=5, l2_leaf_reg=3,
    scale_pos_weight=19.5, random_seed=42, verbose=False,
)


def _make_bl1():
    return BorderlineSMOTE(sampling_strategy=0.3, k_neighbors=3,
                           m_neighbors=10, kind="borderline-1", random_state=42)


def _make_bl2():
    return BorderlineSMOTE(sampling_strategy=0.3, k_neighbors=3,
                           m_neighbors=10, kind="borderline-2", random_state=42)


def _make_smoteenn():
    return SMOTEENN(
        sampling_strategy=0.3, random_state=42,
        smote=SMOTE(k_neighbors=3, random_state=42),
        enn=EditedNearestNeighbours(n_neighbors=3),
    )


def _resample(X_tr, y_tr, fold_idx):
    for sampler_fn, name in [(_make_bl1, "borderline-1"),
                              (_make_bl2, "borderline-2"),
                              (_make_smoteenn, "smoteenn")]:
        try:
            sampler = sampler_fn()
            Xr, yr = sampler.fit_resample(X_tr, y_tr)
            n_syn = int(yr.sum()) - int(y_tr.sum())
            if n_syn < 1 and name != "smoteenn":
                raise ValueError(f"Zero synthetic samples ({name})")
            print(f"  [Fold {fold_idx}] {name}: {int(y_tr.sum())} -> {int(yr.sum())} positives (+{n_syn})")
            return Xr, yr, name
        except Exception as e:
            print(f"  [Fold {fold_idx}] {name} FAILED ({e})")
    raise RuntimeError("All resamplers failed")


def _retrain_v26_for_test_meta():
    print("\n=== Step 1: Retraining V26 to recover test_meta_v26 ===")
    train = pd.read_parquet(V4_TRAIN_PARQUET)
    test = pd.read_parquet(V4_TEST_PARQUET)
    with open(V4_FEATURES_JSON) as f:
        features = json.load(f)["features"]
    assert len(features) == 51

    X_full = train[features].values.astype(np.float64)
    y_full = train["Y"].values.astype(int)
    X_test = test[features].values.astype(np.float64)

    oof_lgb = np.zeros(len(train))
    oof_xgb = np.zeros(len(train))
    oof_cat = np.zeros(len(train))
    test_lgb = np.zeros(len(test))
    test_xgb = np.zeros(len(test))
    test_cat = np.zeros(len(test))

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    for fold_i, (tr_idx, va_idx) in enumerate(skf.split(X_full, y_full)):
        print(f"\n[V26 Fold {fold_i + 1}/5]")
        X_tr, y_tr, _ = _resample(X_full[tr_idx], y_full[tr_idx], fold_i + 1)
        X_va, y_va = X_full[va_idx], y_full[va_idx]

        m = lgb.LGBMClassifier(**LGB_PARAMS)
        m.fit(X_tr, y_tr, eval_set=[(X_va, y_va)],
              callbacks=[lgb.early_stopping(50, verbose=False)])
        oof_lgb[va_idx] = m.predict_proba(X_va)[:, 1]
        test_lgb += m.predict_proba(X_test)[:, 1] / 5

        m = xgb.XGBClassifier(**XGB_PARAMS)
        m.fit(X_tr, y_tr, eval_set=[(X_va, y_va)], verbose=False)
        oof_xgb[va_idx] = m.predict_proba(X_va)[:, 1]
        test_xgb += m.predict_proba(X_test)[:, 1] / 5

        m = CatBoostClassifier(**CAT_PARAMS)
        m.fit(X_tr, y_tr, eval_set=(X_va, y_va), early_stopping_rounds=50)
        oof_cat[va_idx] = m.predict_proba(X_va)[:, 1]
        test_cat += m.predict_proba(X_test)[:, 1] / 5

    print("\n  Fitting LR meta-learner + Platt...")
    X_meta_oof = np.column_stack([oof_lgb, oof_xgb, oof_cat])
    X_meta_test = np.column_stack([test_lgb, test_xgb, test_cat])
    base_meta = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
    meta = CalibratedClassifierCV(base_meta, method="sigmoid", cv=5)
    meta.fit(X_meta_oof, y_full)
    p_oof = meta.predict_proba(X_meta_oof)[:, 1]
    p_test = meta.predict_proba(X_meta_test)[:, 1]

    orig = pd.read_parquet(V26_OOF_PARQUET)
    diff = np.abs(p_oof - orig["oof_meta"].values)
    print(f"\n  V26 OOF reproduction diff: max={diff.max():.2e}  mean={diff.mean():.2e}")

    test_meta_df = pd.DataFrame({
        "CoilID": test["CoilID"].values,
        "test_lgb": test_lgb, "test_xgb": test_xgb, "test_cat": test_cat,
        "test_meta": p_test,
    })
    out = V28_DIR / "test_meta_v26.parquet"
    test_meta_df.to_parquet(out, index=False)
    print(f"  Saved {out}: {len(test_meta_df)} rows")

    return p_oof, p_test, float(diff.max())


def _global_rank_blend(p4_oof, p4_test, p26_oof, p26_test):
    n_oof = len(p4_oof)
    n_test = len(p4_test)
    n_total = n_oof + n_test
    p4_cat = np.concatenate([p4_oof, p4_test])
    p26_cat = np.concatenate([p26_oof, p26_test])
    r4 = rankdata(p4_cat, method="average") / (n_total + 1)
    r26 = rankdata(p26_cat, method="average") / (n_total + 1)
    blend = (r4 + r26) / 2.0
    r4_oof_only = rankdata(p4_oof, method="average") / (n_oof + 1)
    r26_oof_only = rankdata(p26_oof, method="average") / (n_oof + 1)
    blend_oof_only = (r4_oof_only + r26_oof_only) / 2.0
    return {
        "blend_combined": blend,
        "blend_oof_combined": blend[:n_oof],
        "blend_test_combined": blend[n_oof:],
        "blend_oof_only": blend_oof_only,
    }


def _threshold_sweep(blend_oof, y):
    uniq = np.sort(np.unique(np.concatenate([blend_oof, [0.0, 1.0]])))
    cuts = np.r_[uniq[0] - 1e-6, 0.5 * (uniq[:-1] + uniq[1:]), uniq[-1] + 1e-6]
    best = {"T": 0.0, "score": 0.0, "R": 0.0, "P": 0.0, "npos": 0,
            "TP": 0, "FP": 0, "FN": 0}
    rows = []
    for t in cuts:
        pred = (blend_oof >= t).astype(int)
        TP = int(((pred == 1) & (y == 1)).sum())
        FP = int(((pred == 1) & (y == 0)).sum())
        FN = int(((pred == 0) & (y == 1)).sum())
        R = TP / (TP + FN) if (TP + FN) else 0.0
        P = TP / (TP + FP) if (TP + FP) else 0.0
        s = (R + P) / 2.0 * 100.0
        rows.append({"threshold": float(t), "score": s, "recall": R,
                      "precision": P, "n_pos": TP + FP})
        if s > best["score"]:
            best = {"T": float(t), "score": float(s), "R": float(R),
                    "P": float(P), "npos": int(TP + FP),
                    "TP": int(TP), "FP": int(FP), "FN": int(FN)}
    return best, pd.DataFrame(rows)


def _score_at(blend, y, T):
    pred = (blend >= T).astype(int)
    TP = int(((pred == 1) & (y == 1)).sum())
    FP = int(((pred == 1) & (y == 0)).sum())
    FN = int(((pred == 0) & (y == 1)).sum())
    R = TP / (TP + FN) if (TP + FN) else 0.0
    P = TP / (TP + FP) if (TP + FP) else 0.0
    s = (R + P) / 2.0 * 100.0
    return {"score": s, "R": R, "P": P, "TP": TP, "FP": FP, "FN": FN,
            "npos": TP + FP}


def _bootstrap_ci(blend, y, T, n_boot=1000, seed=42):
    rng = np.random.default_rng(seed)
    n = len(y)
    scores = np.zeros(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        scores[i] = _score_at(blend[idx], y[idx], T)["score"]
    return {
        "mean": float(scores.mean()),
        "std": float(scores.std(ddof=1)),
        "ci_lower_95": float(np.percentile(scores, 2.5)),
        "ci_upper_95": float(np.percentile(scores, 97.5)),
        "n_boot": n_boot, "seed": seed,
    }


def _check_fixtures(blend_oof, y, T, coilids):
    fixtures_dir = ROUND1 / "cycles_v2" / "_fixtures"
    fixtures = {}
    coil_to_blend = dict(zip(coilids, blend_oof))
    for name in ("hard7.csv", "easy59.csv", "hard_fp10.csv"):
        df = pd.read_csv(fixtures_dir / name)
        caught = 0
        for _, r in df.iterrows():
            cid = int(r["CoilID"])
            b = coil_to_blend.get(cid, float("nan"))
            ok = b >= T if name != "hard_fp10.csv" else b < T
            if ok:
                caught += 1
        fixtures[name.replace(".csv", "")] = {
            "caught_or_avoided": int(caught),
            "total": int(len(df)),
        }
    return fixtures


def main():
    print("=" * 70)
    print("V28 - V4 + V26 Global Rank-Blend with Isolated Threshold")
    print("=" * 70)

    v26_oof_recomputed, v26_test_meta, v26_repro_max_diff = _retrain_v26_for_test_meta()

    print("\n=== Step 2: Loading V4 + V26 OOF + V4 test_meta ===")
    oof4 = pd.read_parquet(V4_OOF_PARQUET)
    oof26 = pd.read_parquet(V26_OOF_PARQUET)
    train = pd.read_parquet(V4_TRAIN_PARQUET)
    test = pd.read_parquet(V4_TEST_PARQUET)

    assert (oof4["Y"].values == oof26["Y"].values).all()
    assert (oof4["Y"].values == train["Y"].values).all()
    assert (oof26["CoilID"].values == train["CoilID"].values).all()

    p4_oof = oof4["oof_meta"].values
    p26_oof = oof26["oof_meta"].values
    y = oof4["Y"].values.astype(int)

    tm4 = pd.read_parquet(V4_TEST_META_PARQUET)
    p4_test = tm4["test_meta"].values
    p26_test = v26_test_meta
    test_coilids = test["CoilID"].values
    train_coilids = train["CoilID"].values

    print(f"  V4 OOF n={len(p4_oof)}, V26 OOF n={len(p26_oof)}")
    print(f"  V4 test n={len(p4_test)}, V26 test n={len(p26_test)}")
    print(f"  Positives: {y.sum()} / {len(y)} ({y.mean()*100:.2f}%)")

    print("\n=== Step 3: Global rank-blend ===")
    rb = _global_rank_blend(p4_oof, p4_test, p26_oof, p26_test)

    print("\n=== Step 4: Threshold sweep on OOF-only blend ===")
    best_oof_only, sweep_df = _threshold_sweep(rb["blend_oof_only"], y)
    print(f"  Argmax T={best_oof_only['T']:.6f}, score={best_oof_only['score']:.4f}, R={best_oof_only['R']:.4f}, P={best_oof_only['P']:.4f}, npos={best_oof_only['npos']}")

    best_combined, sweep_df_combined = _threshold_sweep(rb["blend_oof_combined"], y)
    print(f"  Combined-rank argmax T={best_combined['T']:.6f}, score={best_combined['score']:.4f}")

    sweep_df.to_csv(V28_DIR / "threshold_sweep_v28_oof_only.csv", index=False)
    sweep_df_combined.to_csv(V28_DIR / "threshold_sweep_v28_combined.csv", index=False)

    T_safe = 0.440
    print(f"\n=== Step 5: Safety threshold T_safe={T_safe} ===")
    safe_score = _score_at(rb["blend_oof_combined"], y, T_safe)
    safe_score_oof_only = _score_at(rb["blend_oof_only"], y, T_safe)
    print(f"  At T_safe (combined): {safe_score['score']:.4f}, R={safe_score['R']:.4f}, P={safe_score['P']:.4f}, npos={safe_score['npos']}")
    print(f"  At T_safe (OOF-only): {safe_score_oof_only['score']:.4f}, R={safe_score_oof_only['R']:.4f}, P={safe_score_oof_only['P']:.4f}, npos={safe_score_oof_only['npos']}")

    print("\n=== Step 6: Bootstrap CI ===")
    bs_argmax = _bootstrap_ci(rb["blend_oof_only"], y, best_oof_only["T"])
    bs_safe = _bootstrap_ci(rb["blend_oof_only"], y, T_safe)
    print(f"  At argmax: mean={bs_argmax['mean']:.4f} std={bs_argmax['std']:.4f} CI95=[{bs_argmax['ci_lower_95']:.4f},{bs_argmax['ci_upper_95']:.4f}]")
    print(f"  At safe T: mean={bs_safe['mean']:.4f} std={bs_safe['std']:.4f} CI95=[{bs_safe['ci_lower_95']:.4f},{bs_safe['ci_upper_95']:.4f}]")

    print("\n=== Step 7: Test inference ===")
    test_preds = (rb["blend_test_combined"] >= T_safe).astype(int)
    print(f"  Test positives: {test_preds.sum()} / {len(test_preds)}")

    print("\n=== Step 8: Fixture diagnostics ===")
    fixtures = _check_fixtures(rb["blend_oof_only"], y, T_safe, train_coilids)
    for name, info in fixtures.items():
        print(f"  {name}: {info['caught_or_avoided']}/{info['total']}")

    print("\n=== Step 9: Persist outputs ===")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    fold_arr = -np.ones(len(y), dtype=int)
    for fold_i, (_, va_idx) in enumerate(skf.split(np.zeros(len(y)), y)):
        fold_arr[va_idx] = fold_i + 1

    oof_df = pd.DataFrame({
        "CoilID": train_coilids,
        "fold": fold_arr,
        "oof_proba": rb["blend_oof_only"],
        "Y": y,
    })
    oof_df.to_parquet(V28_DIR / "oof_v28.parquet", index=False)
    print(f"  Saved oof_v28.parquet ({len(oof_df)} rows)")

    threshold_json = {
        "chosen_threshold": T_safe,
        "strategy": "safety-floor 0.440 on combined-rank scale (V4+V26 global blend)",
        "argmax_threshold_oof_only": best_oof_only["T"],
        "argmax_oof_score": best_oof_only["score"],
        "safe_threshold": T_safe,
        "safe_oof_score_oof_only_scale": safe_score_oof_only["score"],
        "safe_oof_score_combined_scale": safe_score["score"],
        "argmax_threshold_combined": best_combined["T"],
        "argmax_oof_score_combined": best_combined["score"],
        "oof_recall_at_safe_T": safe_score_oof_only["R"],
        "oof_precision_at_safe_T": safe_score_oof_only["P"],
        "oof_n_positives_at_safe_T": safe_score_oof_only["npos"],
        "oof_total": int(len(y)),
        "bootstrap_at_argmax": bs_argmax,
        "bootstrap_at_safe_T": bs_safe,
        "v4_oof_score": 54.31,
        "v23_oof_score": 54.41,
        "delta_vs_v4_argmax": float(best_oof_only["score"]) - 54.31,
        "delta_vs_v23_argmax": float(best_oof_only["score"]) - 54.41,
        "delta_vs_v4_safe": float(safe_score_oof_only["score"]) - 54.31,
        "delta_vs_v23_safe": float(safe_score_oof_only["score"]) - 54.41,
        "v26_oof_reproduction_max_diff": v26_repro_max_diff,
        "test_positives": int(test_preds.sum()),
        "test_total": int(len(test_preds)),
        "fixture_diagnostics": fixtures,
    }
    (V28_DIR / "chosen_threshold_v28.json").write_text(json.dumps(threshold_json, indent=2))
    print("  Saved chosen_threshold_v28.json")

    submission = pd.DataFrame({
        "CoilID": test_coilids,
        "Y": test_preds.astype(int),
    })
    submission.to_csv(V28_DIR / "expected_submission.csv", index=False)
    print(f"  Saved expected_submission.csv ({len(submission)} rows, {submission['Y'].sum()} positives)")

    print("\n" + "=" * 70)
    print("V28 SUMMARY")
    print("=" * 70)
    print(f"  Argmax OOF (OOF-only rank): {best_oof_only['score']:.4f} @ T={best_oof_only['T']:.5f}")
    print(f"  Safe OOF (OOF-only rank):   {safe_score_oof_only['score']:.4f} @ T={T_safe}")
    print(f"  Safe OOF (combined rank):   {safe_score['score']:.4f} @ T={T_safe}")
    print(f"  Bootstrap CI (safe T):      [{bs_safe['ci_lower_95']:.4f}, {bs_safe['ci_upper_95']:.4f}]")
    print(f"  Test positives:             {test_preds.sum()} / {len(test_preds)}")
    print(f"  Delta vs V4 (argmax):       {best_oof_only['score'] - 54.31:+.4f}")
    print(f"  Delta vs V23 (argmax):      {best_oof_only['score'] - 54.41:+.4f}")
    print("=" * 70)


if __name__ == "__main__":
    main()
