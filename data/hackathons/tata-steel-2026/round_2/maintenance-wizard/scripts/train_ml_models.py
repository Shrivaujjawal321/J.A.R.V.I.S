"""
scripts/train_ml_models.py
==========================
Offline training script for ALL ML models in wizard.ml.

Run once before starting the demo server:
  python scripts/train_ml_models.py

Options:
  --subset EQUIPMENT_CLASS   Train one class only (default: all 5)
  --use-cmapss               Download + use NASA C-MAPSS (requires internet)
  --use-ai4i                 Download + use AI4I 2020 (requires internet)
  --synthetic-only           Use synthetic data only (offline-safe, smoke-test mode)
  --epochs INT               LSTM-AE training epochs (default: 20)
  --models-dir PATH          Override output directory (default: data/models/)

Artifacts written to data/models/:
  rul_<class>.pkl                    WeibullAFTFitter per equipment class
  rul_population_<class>.pkl         WeibullFitter fallback per class
  rul_scaler_<class>.pkl             StandardScaler for RUL features
  rul_centroids_<class>.pkl          Healthy/failure centroids
  anomaly_if_<class>.pkl             IsolationForest
  anomaly_threshold_<class>.pkl      Adaptive threshold float
  anomaly_lstm_ae_<class>.pkl        LSTM-AE weights + threshold
  failure_lgbm_<class>.pkl           CalibratedClassifierCV (LightGBM)
  failure_threshold_<class>.pkl      Optimal decision threshold
  rca_gcm_default.pkl                DoWhy GCM (sensor → failure DAG)
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Make wizard importable when run from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)-30s  %(levelname)s  %(message)s",
)
logger = logging.getLogger("train_ml_models")

EQUIPMENT_CLASSES = ["bearing", "fan", "pump", "conveyor", "hydraulic_unit"]

# ---------------------------------------------------------------------------
# Synthetic data generators (offline-safe fallback)
# ---------------------------------------------------------------------------

def _make_synthetic_episodes(equipment_class: str, n: int = 80, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic WeibullAFT training episodes.
    Returns DataFrame with columns: s0..s8, cycles_to_failure, is_failure
    """
    from wizard.ml.feature_utils import make_synthetic_episodes
    arr = make_synthetic_episodes(n_engines=n, rng_seed=seed)
    n_sensors = arr.shape[1] - 2
    cols = [f"s{i}" for i in range(n_sensors)] + ["cycles_to_failure", "is_failure"]
    df = pd.DataFrame(arr, columns=cols)
    df["cycles_to_failure"] = df["cycles_to_failure"].clip(lower=1.0)
    logger.info("[%s] Synthetic episodes: %d rows, %.0f%% failure",
                equipment_class, len(df), df["is_failure"].mean() * 100)
    return df


def _make_synthetic_windows(n_normal: int = 5000, n_anomaly: int = 500,
                             n_features: int = 54, seed: int = 42) -> tuple:
    """
    Generate synthetic (normal, anomaly) window feature arrays for anomaly detector.
    Returns (normal_arr, anomaly_arr) — both shape (N, n_features)
    """
    rng = np.random.default_rng(seed)
    normal = rng.normal(loc=0.3, scale=0.1, size=(n_normal, n_features)).astype(np.float32)
    normal = np.clip(normal, 0.0, 1.0)
    anomaly = rng.normal(loc=0.7, scale=0.2, size=(n_anomaly, n_features)).astype(np.float32)
    anomaly = np.clip(anomaly, 0.0, 1.0)
    return normal, anomaly


def _make_synthetic_failure_df(n: int = 2000, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic 4-class ordinal failure dataset for LightGBM.
    Returns DataFrame with feature columns + 'failure_class' (0-3).
    """
    from wizard.ml.feature_utils import FEATURE_DIM
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, FEATURE_DIM)).astype(np.float32)
    # Class distribution: ~70% NORMAL, 15% WARN_72H, 10% WARN_24H, 5% IMMINENT
    probs = [0.70, 0.15, 0.10, 0.05]
    y = rng.choice([0, 1, 2, 3], size=n, p=probs).astype(np.int32)
    cols = [f"f{i}" for i in range(FEATURE_DIM)]
    df = pd.DataFrame(X, columns=cols)
    df["failure_class"] = y
    logger.info("Synthetic failure dataset: %d rows, class distribution=%s",
                n, dict(zip([0,1,2,3], np.bincount(y, minlength=4))))
    return df


def _make_synthetic_sensor_df(n: int = 1000, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic sensor DataFrame for DoWhy GCM training.
    Columns: temperature_c, pressure_bar, vibration_mm_s, rpm, torque_nm,
             current_a, tool_wear_min, machine_failure
    """
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "temperature_c":   rng.normal(350, 30, n),
        "pressure_bar":    rng.normal(180, 20, n),
        "vibration_mm_s":  rng.exponential(0.5, n),
        "rpm":             rng.normal(1200, 100, n),
        "torque_nm":       rng.normal(500, 80, n),
        "current_a":       rng.normal(50, 8, n),
        "tool_wear_min":   rng.uniform(0, 300, n),
    })
    # machine_failure: roughly 5% failures, correlated with high vibration
    df["machine_failure"] = (
        (df["vibration_mm_s"] > df["vibration_mm_s"].quantile(0.92)) |
        (df["tool_wear_min"] > 250)
    ).astype(int)
    logger.info("Synthetic sensor DF: %d rows, %.1f%% failures",
                n, df["machine_failure"].mean() * 100)
    return df


# ---------------------------------------------------------------------------
# C-MAPSS → WeibullAFT episodes
# ---------------------------------------------------------------------------

def _cmapss_to_episodes(ds: Any) -> pd.DataFrame:
    """Convert CmapssDataset to WeibullAFT episode rows."""
    rows = []
    for subset in ["FD001"]:
        train_df = ds.train.get(subset)
        if train_df is None:
            continue
        feature_cols = ds.feature_cols or []
        for engine_id, grp in train_df.groupby("engine_id"):
            last_row = grp.sort_values("cycle").iloc[-1]
            sensor_vals = {f"s{i}": float(last_row.get(c, 0.0)) for i, c in enumerate(feature_cols)}
            sensor_vals["cycles_to_failure"] = float(grp["rul"].min())
            sensor_vals["is_failure"] = 1.0
            rows.append(sensor_vals)
    df = pd.DataFrame(rows).fillna(0.0)
    df["cycles_to_failure"] = df["cycles_to_failure"].clip(lower=1.0)
    return df


# ---------------------------------------------------------------------------
# AI4I → failure class DataFrame
# ---------------------------------------------------------------------------

def _ai4i_to_failure_df(ai4i_df: Any) -> pd.DataFrame:
    """Map AI4I 2020 data to 4-class ordinal labels for LightGBM."""
    from wizard.data.ai4i_loader import FEATURE_COLS  # type: ignore[import]
    from wizard.ml.feature_utils import FEATURE_DIM

    available = [c for c in FEATURE_COLS if c in ai4i_df.columns]
    X = ai4i_df[available].fillna(0.0).to_numpy(np.float32)

    # Ordinal label: NORMAL=0, WARN_72H=1, WARN_24H=2, IMMINENT=3
    # Map from active_fault_mode (failures → IMMINENT; near-failure → WARN_24H etc.)
    # Simple heuristic: machine_failure=1 → 3 (IMMINENT), else 0 (NORMAL)
    # (More granular labels would require look-ahead window on time-series)
    labels = np.where(ai4i_df["machine_failure"].values == 1, 3, 0).astype(np.int32)

    # Pad feature matrix to FEATURE_DIM if needed
    if X.shape[1] < FEATURE_DIM:
        pad = np.zeros((len(X), FEATURE_DIM - X.shape[1]), dtype=np.float32)
        X = np.concatenate([X, pad], axis=1)
    elif X.shape[1] > FEATURE_DIM:
        X = X[:, :FEATURE_DIM]

    cols = [f"f{i}" for i in range(FEATURE_DIM)]
    df = pd.DataFrame(X, columns=cols)
    df["failure_class"] = labels
    return df


# ---------------------------------------------------------------------------
# Main training loop
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Train Maintenance Wizard ML models.")
    parser.add_argument("--subset", default=None, help="Single equipment class to train")
    parser.add_argument("--use-cmapss", action="store_true")
    parser.add_argument("--use-ai4i",   action="store_true")
    parser.add_argument("--synthetic-only", action="store_true", default=False)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--models-dir", type=Path, default=None)
    args = parser.parse_args()

    from wizard.ml.rul_estimator import train_rul_model
    from wizard.ml.anomaly_detector import train_anomaly_models
    from wizard.ml.failure_predictor import train_failure_model
    from wizard.ml.rca_engine import train_rca_gcm

    equipment_classes = [args.subset] if args.subset else EQUIPMENT_CLASSES
    models_dir = args.models_dir

    # --- Load real datasets if requested ---
    cmapss_ds = None
    ai4i_df = None

    if args.use_cmapss and not args.synthetic_only:
        try:
            from wizard.data.cmapss_loader import load_cmapss  # type: ignore[import]
            logger.info("Loading NASA C-MAPSS ...")
            cmapss_ds = load_cmapss(subsets=["FD001"])
        except Exception as exc:
            logger.warning("C-MAPSS load failed (%s) — using synthetic", exc)

    if args.use_ai4i and not args.synthetic_only:
        try:
            from wizard.data.ai4i_loader import load_ai4i  # type: ignore[import]
            logger.info("Loading AI4I 2020 ...")
            ai4i_df = load_ai4i()
        except Exception as exc:
            logger.warning("AI4I load failed (%s) — using synthetic", exc)

    # --- Train per equipment class ---
    for eq_class in equipment_classes:
        logger.info("=" * 60)
        logger.info("Training: %s", eq_class)
        logger.info("=" * 60)

        seed = hash(eq_class) % (2 ** 31) + 42

        # 1. RUL
        if cmapss_ds is not None:
            try:
                ep_df = _cmapss_to_episodes(cmapss_ds)
                logger.info("Using C-MAPSS episodes for RUL: %d rows", len(ep_df))
            except Exception as exc:
                logger.warning("C-MAPSS → episodes failed: %s", exc)
                ep_df = _make_synthetic_episodes(eq_class, seed=seed)
        else:
            ep_df = _make_synthetic_episodes(eq_class, seed=seed)
        train_rul_model(ep_df, equipment_class=eq_class, models_dir=models_dir)

        # 2. Anomaly
        normal_arr, anomaly_arr = _make_synthetic_windows(seed=seed)
        train_anomaly_models(
            normal_arr, anomaly_arr,
            equipment_class=eq_class,
            lstm_epochs=args.epochs,
            models_dir=models_dir,
        )

        # 3. Failure prediction
        if ai4i_df is not None:
            try:
                fail_df = _ai4i_to_failure_df(ai4i_df)
                logger.info("Using AI4I data for failure model: %d rows", len(fail_df))
            except Exception as exc:
                logger.warning("AI4I → failure_df failed: %s", exc)
                fail_df = _make_synthetic_failure_df(seed=seed)
        else:
            fail_df = _make_synthetic_failure_df(seed=seed)
        train_failure_model(fail_df, equipment_class=eq_class, models_dir=models_dir)

    # 4. DoWhy GCM (shared, once)
    logger.info("=" * 60)
    logger.info("Training DoWhy GCM (shared) ...")
    logger.info("=" * 60)
    try:
        sensor_df = _make_synthetic_sensor_df(seed=42)
        train_rca_gcm(sensor_df, models_dir=models_dir)
    except ImportError:
        logger.warning("DoWhy not installed — skipping GCM training. RCA Layer2 will use fallback.")
    except Exception as exc:
        logger.warning("DoWhy GCM training failed: %s", exc)

    logger.info("All ML model training complete.")


if __name__ == "__main__":
    main()
