"""Smoke test for the ml_harness utils — run with: python notebooks/_harness_smoke_test.py
All modules exercised on synthetic data. Prints PASS/FAIL per module. Exit 0 = all pass."""

from __future__ import annotations

import sys
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

# ── make sure ml_harness package is importable regardless of CWD ──────────────
_HARNESS_ROOT = Path(__file__).resolve().parent.parent
if str(_HARNESS_ROOT.parent) not in sys.path:
    sys.path.insert(0, str(_HARNESS_ROOT.parent))

from ml_harness.utils.cv import group_kfold, stratified_kfold, timeseries_split
from ml_harness.utils.ensemble import rank_average, simple_average, weighted_average
from ml_harness.utils.metrics import get_metric
from ml_harness.utils.optuna_runner import run_study
from ml_harness.utils.seed import set_seed
from ml_harness.utils.submission import write_submission

RESULTS: dict[str, str] = {}
START = time.perf_counter()

RNG = np.random.default_rng(42)
N_ROWS = 1000
N_FEAT = 20

# ── synthetic dataset ─────────────────────────────────────────────────────────
X = RNG.standard_normal((N_ROWS, N_FEAT)).astype(np.float32)
y_cls = (X[:, 0] + X[:, 1] > 0).astype(int)          # binary classification target
y_reg = (X[:, 2] * 3 + X[:, 3] - X[:, 4] + RNG.normal(0, 0.5, N_ROWS)).astype(float)


# ─────────────────────────────────────────────────────────────────────────────
# Module 1 — seed.py
# ─────────────────────────────────────────────────────────────────────────────
def test_seed() -> None:
    seed_used = set_seed(42)
    assert seed_used == 42, f"Expected 42, got {seed_used}"
    # reproducibility check
    set_seed(99)
    a = np.random.rand()
    set_seed(99)
    b = np.random.rand()
    assert a == b, "seed not reproducible"


try:
    test_seed()
    RESULTS["seed"] = "PASS"
except Exception:
    RESULTS["seed"] = f"FAIL\n{traceback.format_exc()}"

# ─────────────────────────────────────────────────────────────────────────────
# Module 2 — cv.py + metrics.py  (stratified_kfold + f1_macro, LightGBM clf)
# ─────────────────────────────────────────────────────────────────────────────
def test_cv_classification() -> None:
    import lightgbm as lgb

    set_seed(42)
    metric_fn = get_metric("classification", "f1_macro")
    fold_scores: list[float] = []

    for train_idx, val_idx in stratified_kfold(y_cls, n_splits=5, seed=42):
        X_tr, X_val = X[train_idx], X[val_idx]
        y_tr, y_val = y_cls[train_idx], y_cls[val_idx]

        clf = lgb.LGBMClassifier(n_estimators=50, random_state=42, verbose=-1)
        clf.fit(X_tr, y_tr)
        preds = clf.predict(X_val)
        score = metric_fn(y_val, preds)
        fold_scores.append(score)

    mean_score = np.mean(fold_scores)
    assert 0.5 < mean_score <= 1.0, f"Suspiciously low f1_macro: {mean_score:.4f}"
    print(f"  [clf] 5-fold f1_macro: {mean_score:.4f}  folds={[f'{s:.3f}' for s in fold_scores]}")


try:
    test_cv_classification()
    RESULTS["cv_classification"] = "PASS"
except Exception:
    RESULTS["cv_classification"] = f"FAIL\n{traceback.format_exc()}"

# ─────────────────────────────────────────────────────────────────────────────
# Module 3 — cv.py + metrics.py  (timeseries_split + rmse, LightGBM reg)
# ─────────────────────────────────────────────────────────────────────────────
def test_cv_timeseries() -> None:
    import lightgbm as lgb

    set_seed(42)
    metric_fn = get_metric("regression", "rmse")
    fold_scores: list[float] = []

    for train_idx, val_idx in timeseries_split(X, n_splits=5):
        X_tr, X_val = X[train_idx], X[val_idx]
        y_tr, y_val = y_reg[train_idx], y_reg[val_idx]

        reg = lgb.LGBMRegressor(n_estimators=50, random_state=42, verbose=-1)
        reg.fit(X_tr, y_tr)
        preds = reg.predict(X_val)
        score = metric_fn(y_val, preds)
        fold_scores.append(score)

    mean_rmse = np.mean(fold_scores)
    assert mean_rmse > 0, f"RMSE should be positive, got {mean_rmse}"
    print(f"  [reg] 5-fold RMSE:    {mean_rmse:.4f}  folds={[f'{s:.3f}' for s in fold_scores]}")


try:
    test_cv_timeseries()
    RESULTS["cv_timeseries"] = "PASS"
except Exception:
    RESULTS["cv_timeseries"] = f"FAIL\n{traceback.format_exc()}"

# ─────────────────────────────────────────────────────────────────────────────
# Module 4 — cv.py  (group_kfold — groups exist, no leakage)
# ─────────────────────────────────────────────────────────────────────────────
def test_cv_group() -> None:
    groups = np.repeat(np.arange(50), N_ROWS // 50)   # 50 groups, 20 rows each
    splits = list(group_kfold(groups, n_splits=5))
    assert len(splits) == 5, f"Expected 5 folds, got {len(splits)}"
    for tr, val in splits:
        overlap = set(groups[tr]) & set(groups[val])
        assert len(overlap) == 0, f"Group leakage detected: {overlap}"


try:
    test_cv_group()
    RESULTS["cv_group_kfold"] = "PASS"
except Exception:
    RESULTS["cv_group_kfold"] = f"FAIL\n{traceback.format_exc()}"

# ─────────────────────────────────────────────────────────────────────────────
# Module 5 — metrics.py  (dice, accuracy, roc_auc, mae, mape)
# ─────────────────────────────────────────────────────────────────────────────
def test_metrics_misc() -> None:
    # dice — perfect match
    mask = np.array([1, 0, 1, 1, 0])
    assert get_metric("segmentation", "dice")(mask, mask) == 1.0

    # dice — zero case
    assert get_metric("segmentation", "dice")(np.zeros(5), np.zeros(5)) == 1.0

    # accuracy
    y_t = np.array([0, 1, 1, 0])
    y_p = np.array([0, 1, 0, 0])
    acc = get_metric("classification", "accuracy")(y_t, y_p)
    assert abs(acc - 0.75) < 1e-6, f"accuracy wrong: {acc}"

    # rmse
    y_t2 = np.array([1.0, 2.0, 3.0])
    y_p2 = np.array([1.0, 2.0, 4.0])
    rmse = get_metric("regression", "rmse")(y_t2, y_p2)
    assert abs(rmse - (1 / 3) ** 0.5) < 1e-5, f"rmse wrong: {rmse}"

    # default metric for classification
    fn = get_metric("classification")
    assert callable(fn)


try:
    test_metrics_misc()
    RESULTS["metrics"] = "PASS"
except Exception:
    RESULTS["metrics"] = f"FAIL\n{traceback.format_exc()}"

# ─────────────────────────────────────────────────────────────────────────────
# Module 6 — optuna_runner.py  (minimise RMSE on synthetic regression, 10 trials)
# ─────────────────────────────────────────────────────────────────────────────
def test_optuna() -> None:
    import lightgbm as lgb

    set_seed(42)
    metric_fn = get_metric("regression", "rmse")

    # hold-out split for speed (no full CV inside Optuna — keeps runtime < 60s)
    split_idx = int(0.8 * N_ROWS)
    X_tr, X_val = X[:split_idx], X[split_idx:]
    y_tr, y_val = y_reg[:split_idx], y_reg[split_idx:]

    def objective(trial: object) -> float:
        import optuna
        assert isinstance(trial, optuna.Trial)
        n_est = trial.suggest_int("n_estimators", 20, 100)
        lr = trial.suggest_float("learning_rate", 0.01, 0.3, log=True)
        num_leaves = trial.suggest_int("num_leaves", 15, 63)
        reg = lgb.LGBMRegressor(
            n_estimators=n_est,
            learning_rate=lr,
            num_leaves=num_leaves,
            random_state=42,
            verbose=-1,
        )
        reg.fit(X_tr, y_tr)
        preds = reg.predict(X_val)
        return metric_fn(y_val, preds)

    best_params, best_value, study = run_study(
        objective,
        n_trials=10,
        direction="minimize",
        verbose=False,
    )
    assert isinstance(best_params, dict), "best_params should be dict"
    assert isinstance(best_value, float) and best_value > 0
    assert len(study.trials) == 10
    print(f"  [optuna] best RMSE={best_value:.4f}  params={best_params}")


try:
    test_optuna()
    RESULTS["optuna_runner"] = "PASS"
except Exception:
    RESULTS["optuna_runner"] = f"FAIL\n{traceback.format_exc()}"

# ─────────────────────────────────────────────────────────────────────────────
# Module 7 — ensemble.py
# ─────────────────────────────────────────────────────────────────────────────
def test_ensemble() -> None:
    # 1-D regression
    p1 = np.array([0.1, 0.5, 0.9])
    p2 = np.array([0.3, 0.4, 0.7])
    p3 = np.array([0.2, 0.6, 0.8])

    sa = simple_average([p1, p2, p3])
    expected = np.array([(0.1 + 0.3 + 0.2) / 3, (0.5 + 0.4 + 0.6) / 3, (0.9 + 0.7 + 0.8) / 3])
    np.testing.assert_allclose(sa, expected, atol=1e-6)

    wa = weighted_average([p1, p2, p3], weights=[1.0, 2.0, 1.0])
    expected_w = (1 * p1 + 2 * p2 + 1 * p3) / 4
    np.testing.assert_allclose(wa, expected_w, atol=1e-6)

    ra = rank_average([p1, p2, p3])
    assert ra.shape == (3,), f"rank_average shape wrong: {ra.shape}"
    # ranks should be in (1, 3) range before averaging
    assert ra.min() >= 1.0 and ra.max() <= 3.0

    # 2-D class probs
    p2d_1 = np.array([[0.7, 0.3], [0.4, 0.6], [0.9, 0.1]])
    p2d_2 = np.array([[0.6, 0.4], [0.5, 0.5], [0.8, 0.2]])

    sa2d = simple_average([p2d_1, p2d_2])
    assert sa2d.shape == (3, 2)

    ra2d = rank_average([p2d_1, p2d_2])
    assert ra2d.shape == (3, 2)

    print(f"  [ensemble] simple_avg={sa}  rank_avg={ra}")


try:
    test_ensemble()
    RESULTS["ensemble"] = "PASS"
except Exception:
    RESULTS["ensemble"] = f"FAIL\n{traceback.format_exc()}"

# ─────────────────────────────────────────────────────────────────────────────
# Module 8 — submission.py
# ─────────────────────────────────────────────────────────────────────────────
def test_submission() -> None:
    import tempfile

    sub_df = pd.DataFrame({"id": np.arange(100), "target": RNG.random(100)})
    sample_df = pd.DataFrame({"id": np.arange(100), "target": np.zeros(100)})

    with tempfile.TemporaryDirectory() as tmpdir:
        sample_path = Path(tmpdir) / "sample_submission.csv"
        out_path = Path(tmpdir) / "submission.csv"

        sample_df.to_csv(sample_path, index=False)
        write_submission(sub_df, out_path, sample_path=sample_path)

        assert out_path.exists(), "submission file not written"
        read_back = pd.read_csv(out_path)
        assert len(read_back) == 100
        assert list(read_back.columns) == ["id", "target"]

        # --- test row count mismatch raises ---
        bad_df = sub_df.head(50)
        try:
            write_submission(bad_df, out_path, sample_path=sample_path)
            raise AssertionError("Should have raised ValueError on row count mismatch")
        except ValueError as e:
            assert "Row count mismatch" in str(e)

        # --- test column mismatch raises ---
        col_bad = pd.DataFrame({"id": np.arange(100), "wrong_col": np.zeros(100)})
        try:
            write_submission(col_bad, out_path, sample_path=sample_path)
            raise AssertionError("Should have raised ValueError on column mismatch")
        except ValueError as e:
            assert "Column mismatch" in str(e)


try:
    test_submission()
    RESULTS["submission"] = "PASS"
except Exception:
    RESULTS["submission"] = f"FAIL\n{traceback.format_exc()}"

# ─────────────────────────────────────────────────────────────────────────────
# ── Summary ──────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
elapsed = time.perf_counter() - START
print("\n" + "=" * 56)
print("  ML HARNESS SMOKE TEST RESULTS")
print("=" * 56)
all_pass = True
for mod, result in RESULTS.items():
    status = "PASS" if result == "PASS" else "FAIL"
    icon = "OK" if status == "PASS" else "!!"
    print(f"  [{icon}] {mod:<28}  {status}")
    if status != "PASS":
        all_pass = False
        # print the traceback indented
        for line in result.splitlines()[1:]:
            print(f"       {line}")
print("=" * 56)
print(f"  Elapsed: {elapsed:.1f}s")
print(f"  Overall: {'ALL PASS' if all_pass else 'FAILURES DETECTED'}")
print("=" * 56)

sys.exit(0 if all_pass else 1)
