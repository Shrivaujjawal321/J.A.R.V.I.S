"""
wizard/ml/train_anomaly.py
===========================
Entrypoint: train IsolationForest + LSTM Autoencoder anomaly detectors
for all 5 equipment classes.

Keeps LSTM epochs small (8-12 default) so CPU training finishes in a few minutes.

Artifacts written to data/models/:
  anomaly_if_{equipment_class}.pkl        — IsolationForest
  anomaly_threshold_{equipment_class}.pkl — Adaptive 97th-percentile threshold
  anomaly_lstm_ae_{equipment_class}.pkl   — {'state_dict': ..., 'threshold': ...}

Usage::
    python wizard/ml/train_anomaly.py [--epochs 8]
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import numpy as np

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("train_anomaly")

EQUIPMENT_CLASSES = ["bearing", "fan", "pump", "conveyor", "hydraulic_unit"]

# IsolationForest feature dimension: N_SENSORS × N_STATS = 9 × 6 = 54
_WINDOW_FEATURE_DIM = 54
# Raw sensor dimension: used by LSTM-AE and River HST
_N_SENSORS = 9


def _make_synthetic_windows(
    n_normal: int = 5000,
    n_anomaly: int = 500,
    n_features: int = _WINDOW_FEATURE_DIM,
    seed: int = 42,
) -> "tuple[np.ndarray, np.ndarray]":
    """
    Generate synthetic normal + anomaly 54-dim window feature matrices (for IsolationForest).

    FIX (2026-06-07 v2): Add constant-pattern normal windows (std=0 slices) so the
    IsolationForest learns that low-variance readings from steady-state equipment are
    *normal* — not anomalous.  Without this, a constant-history inference window
    (std=0, range=0) looks like an outlier because training data had std~0.15 on
    every feature, causing the IF to score all low-variance windows as 1.0.

    Composition:
      80% Gaussian normal:    centred at 0.3, std 0.15, clipped [0, 1]
      20% Constant-value rows: each row filled with a single random value in [0.1, 0.6]
                               (covers healthy steady-state sensor readings)
    Anomaly windows: centred at 0.80, std 0.20, clipped [0, 1]
                     (high-value cluster; well separated from normal cluster at 0.3).

    Returns (normal_arr, anomaly_arr) — shapes (n_normal, n_features) and (n_anomaly, n_features).
    """
    rng = np.random.default_rng(seed)
    n_gaussian = int(n_normal * 0.80)
    n_constant = n_normal - n_gaussian

    # Gaussian normal batch
    gauss = rng.normal(loc=0.3, scale=0.15, size=(n_gaussian, n_features)).astype(np.float32)
    gauss = np.clip(gauss, 0.0, 1.0)

    # Constant-value normal batch: each row = one steady-state reading repeated across features
    # The mean-feature values in extract_window_features for a constant history are the sensor
    # readings themselves, while std/range/roc = 0 — these should be normal (equipment at rest).
    const_vals = rng.uniform(0.1, 0.6, size=(n_constant, 1)).astype(np.float32)
    const_rows = np.repeat(const_vals, n_features, axis=1)
    # Add tiny jitter (1e-3) to prevent degenerate collapse in the IF trees
    jitter = rng.normal(0.0, 1e-3, size=const_rows.shape).astype(np.float32)
    const_rows = np.clip(const_rows + jitter, 0.0, 1.0)

    normal = np.concatenate([gauss, const_rows], axis=0)
    # Shuffle so constant rows are distributed throughout (not all at end)
    perm = rng.permutation(n_normal)
    normal = normal[perm]

    # Anomaly cluster shifted to 0.80 for cleaner separation from normal at 0.3
    anomaly = rng.normal(loc=0.80, scale=0.20, size=(n_anomaly, n_features)).astype(np.float32)
    anomaly = np.clip(anomaly, 0.0, 1.0)
    return normal, anomaly


def _make_raw_sensor_windows(
    n_timesteps: int = 5000,
    n_sensors: int = _N_SENSORS,
    seed: int = 42,
) -> np.ndarray:
    """
    Generate synthetic raw sensor time-steps for LSTM-AE and River HST training.

    Each row = one time-step with n_sensors raw sensor readings.
    Normal operating range centred at 0.3, std 0.1, clipped [0, 1].

    Returns shape (n_timesteps, n_sensors).
    """
    rng = np.random.default_rng(seed)
    raw = rng.normal(loc=0.3, scale=0.1, size=(n_timesteps, n_sensors)).astype(np.float32)
    return np.clip(raw, 0.0, 1.0)


def main(lstm_epochs: int = 10) -> None:
    from wizard.ml.anomaly_detector import train_anomaly_models, train_river_hst

    models_dir = _REPO_ROOT / "data" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    for eq_class in EQUIPMENT_CLASSES:
        log.info("=" * 55)
        log.info("Training anomaly detector: %s", eq_class)
        log.info("=" * 55)

        seed = abs(hash(eq_class)) % (2 ** 31) + 42

        # 54-dim window features for IsolationForest
        normal_arr, anomaly_arr = _make_synthetic_windows(
            n_normal=5000,
            n_anomaly=500,
            n_features=_WINDOW_FEATURE_DIM,
            seed=seed,
        )

        # 9-dim raw sensor time-steps for LSTM-AE (same seed, separate matrix)
        raw_windows = _make_raw_sensor_windows(
            n_timesteps=5000,
            n_sensors=_N_SENSORS,
            seed=seed + 1,
        )

        log.info(
            "[%s] IF windows: %d×%d | LSTM-AE raw windows: %d×%d | anomaly: %d | epochs: %d",
            eq_class,
            len(normal_arr), _WINDOW_FEATURE_DIM,
            len(raw_windows), _N_SENSORS,
            len(anomaly_arr),
            lstm_epochs,
        )

        # FIX: contamination raised to 0.05 (matches ~5% anomaly prevalence)
        # and threshold percentile stays at 97th (internal to train_anomaly_models).
        train_anomaly_models(
            normal_df=normal_arr,
            anomaly_df=anomaly_arr,
            equipment_class=eq_class,
            n_estimators=200,
            contamination=0.05,
            lstm_epochs=lstm_epochs,
            models_dir=models_dir,
            raw_sensor_windows=raw_windows,
        )

    # River HST: one global model trained on normal raw sensor data
    log.info("=" * 55)
    log.info("Training River HalfSpaceTrees (global streaming model)")
    log.info("=" * 55)
    # Combine a multi-class normal signal (5000 samples)
    rng = np.random.default_rng(0)
    hst_data = np.clip(
        rng.normal(loc=0.3, scale=0.1, size=(5000, _N_SENSORS)).astype(np.float32),
        0.0, 1.0,
    )
    train_river_hst(
        raw_sensor_windows=hst_data,
        n_trees=25,
        height=8,
        window_size=250,
        models_dir=models_dir,
    )

    log.info("Anomaly model training complete. Artifacts in %s", models_dir)
    pkls = sorted(models_dir.glob("anomaly_*.pkl"))
    for p in pkls:
        log.info("  %s (%.1f KB)", p.name, p.stat().st_size / 1024)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train IsolationForest + LSTM-AE anomaly detectors")
    parser.add_argument(
        "--epochs", type=int, default=10,
        help="LSTM-AE training epochs per equipment class (default: 10 — CPU-friendly)",
    )
    args = parser.parse_args()

    main(lstm_epochs=args.epochs)
    sys.exit(0)
