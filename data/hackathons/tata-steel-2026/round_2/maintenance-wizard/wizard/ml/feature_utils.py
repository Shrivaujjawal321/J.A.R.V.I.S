"""
wizard.ml.feature_utils
========================
Shared sliding-window feature extraction for the ML layer.

Both the anomaly detector and failure predictor consume a feature vector
computed from a raw sensor reading dict + optional history buffer.

Public API
----------
  extract_window_features(readings_history, window=30) -> np.ndarray
      Given a list of recent sensor reading dicts, compute rolling stats.
      Returns a 1-D float32 vector ready for IsolationForest / LightGBM.

  compute_degradation_index(readings, healthy_centroid, failure_centroid, scaler)
      Returns scalar d in [0, 1] for WeibullAFT correction.

  build_sensor_vector(readings_dict, sensor_keys) -> np.ndarray
      Extract ordered float32 array from a raw readings dict.

SENSOR_KEYS defines the canonical key order — all callers must use this list.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence
import logging

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Canonical sensor key order
# Derived from C-MAPSS retained columns + AI4I features (aliased to steel names)
# ---------------------------------------------------------------------------
SENSOR_KEYS: List[str] = [
    "temperature_c",       # C-MAPSS: inlet_temperature_c / AI4I: air_temp_c
    "process_temp_c",      # AI4I: process_temp_c
    "pressure_bar",        # hpc_outlet_pressure_bar / bypass_duct_pressure_bar
    "vibration_mm_s",      # vibration_rms
    "rpm",                 # rotational_speed_rpm
    "torque_nm",           # torque_nm
    "current_a",           # bleed_flow_rate proxy
    "tool_wear_min",       # AI4I tool_wear_min
    "health_score",        # derived from rul_capped in C-MAPSS loader
]
N_SENSORS = len(SENSOR_KEYS)

# Rolling stats computed per sensor per window (for anomaly + failure features)
_ROLLING_STATS = ["mean", "std", "min", "max", "range", "rate_of_change"]
N_FEATURES_PER_SENSOR = len(_ROLLING_STATS)
FEATURE_DIM = N_SENSORS * N_FEATURES_PER_SENSOR  # 54


def build_sensor_vector(
    readings: Dict[str, float],
    keys: Optional[List[str]] = None,
) -> np.ndarray:
    """
    Extract an ordered float32 vector from a readings dict.

    Missing keys are filled with 0.0 (safe for inference).

    Parameters
    ----------
    readings : dict[str, float]
        Raw sensor snapshot, e.g. SensorSummary.sensor_readings.
    keys : list[str], optional
        Key ordering; defaults to SENSOR_KEYS.

    Returns
    -------
    np.ndarray shape (len(keys),), dtype float32
    """
    if keys is None:
        keys = SENSOR_KEYS
    return np.array(
        [float(readings.get(k, 0.0)) for k in keys],
        dtype=np.float32,
    )


def extract_window_features(
    readings_history: Sequence[Dict[str, float]],
    window: int = 30,
    sensor_keys: Optional[List[str]] = None,
) -> np.ndarray:
    """
    Compute rolling-window statistical features over the last `window` sensor ticks.

    Uses the most recent `window` entries in readings_history.
    Returns a 1-D float32 array of length N_SENSORS * N_FEATURES_PER_SENSOR (= 54).

    If history is shorter than window, the available rows are used (no error).

    Parameters
    ----------
    readings_history : sequence of dicts
        Ordered from oldest to newest.
    window : int
        Rolling window size (default 30 matches research report §2d).
    sensor_keys : list[str], optional
        Sensor columns to use; defaults to SENSOR_KEYS.

    Returns
    -------
    np.ndarray shape (FEATURE_DIM,), dtype float32
    """
    if sensor_keys is None:
        sensor_keys = SENSOR_KEYS

    # Build (T, D) matrix from history tail
    tail = list(readings_history)[-window:] if len(readings_history) > window else list(readings_history)
    if not tail:
        return np.zeros(len(sensor_keys) * N_FEATURES_PER_SENSOR, dtype=np.float32)

    matrix = np.array(
        [[float(r.get(k, 0.0)) for k in sensor_keys] for r in tail],
        dtype=np.float32,
    )  # shape (T, D)

    T, D = matrix.shape

    features: List[float] = []
    for d in range(D):
        col = matrix[:, d]
        col_mean = float(np.mean(col))
        col_std  = float(np.std(col, ddof=0))
        col_min  = float(np.min(col))
        col_max  = float(np.max(col))
        col_range = col_max - col_min
        # Rate-of-change: last value minus first, normalized by window length
        roc = (float(col[-1]) - float(col[0])) / max(T - 1, 1)
        features.extend([col_mean, col_std, col_min, col_max, col_range, roc])

    return np.array(features, dtype=np.float32)


def compute_degradation_index(
    current_readings: Dict[str, float],
    healthy_centroid: np.ndarray,
    failure_centroid: np.ndarray,
    sensor_keys: Optional[List[str]] = None,
) -> float:
    """
    Compute a scalar degradation index d in [0, 1].

    d = ||z_current - z_healthy|| / ||z_failure - z_healthy||

    Where z is the raw sensor vector (not StandardScaler-normalized here;
    the caller is expected to pass z in whatever space the centroids were
    computed).

    Clipped to [0.0, 1.0] to handle extrapolation.

    Parameters
    ----------
    current_readings : dict[str, float]
        Latest sensor snapshot.
    healthy_centroid : np.ndarray shape (D,)
        Mean sensor vector over healthy operating windows.
    failure_centroid : np.ndarray shape (D,)
        Mean sensor vector over fault-onset windows.
    sensor_keys : list[str], optional

    Returns
    -------
    float in [0.0, 1.0]
    """
    if sensor_keys is None:
        sensor_keys = SENSOR_KEYS

    z = build_sensor_vector(current_readings, sensor_keys)

    denom = np.linalg.norm(failure_centroid - healthy_centroid)
    if denom < 1e-8:
        return 0.0  # centroids are the same — can't compute degradation

    d = float(np.linalg.norm(z - healthy_centroid) / denom)
    return float(np.clip(d, 0.0, 1.0))


def make_synthetic_episodes(
    n_engines: int = 50,
    max_cycles: int = 200,
    n_sensors: int = 9,
    rng_seed: int = 42,
) -> "np.ndarray":  # type: ignore[type-arg]
    """
    Generate a tiny synthetic fault-episode dataset for training smoke tests.

    Returns a (N, n_sensors + 2) array with columns:
      [sensor_0 .. sensor_{n_sensors-1}, duration_cycles, is_failure]

    Each "episode" is one equipment run with a fixed noise-corrupted sensor
    profile at degradation onset, and a randomly assigned failure time.

    NOTE: this is NOT a replacement for C-MAPSS — it is used only by
    smoke_ml.py to verify the training scripts can run without network access.
    """
    rng = np.random.default_rng(rng_seed)

    rows = []
    for _ in range(n_engines):
        # Random degradation profile: sensors drift from healthy → failure values
        healthy = rng.uniform(0.1, 0.4, size=n_sensors)
        failure = healthy + rng.uniform(0.3, 0.6, size=n_sensors)
        # Sensor at degradation onset = interpolated
        alpha = rng.uniform(0.2, 0.9)
        z_onset = (1 - alpha) * healthy + alpha * failure + rng.normal(0, 0.02, n_sensors)
        z_onset = np.clip(z_onset, 0.0, 1.0)

        duration = int(rng.integers(20, max_cycles))
        is_failure = int(rng.random() < 0.85)  # 85% fail, 15% censored
        row = list(z_onset) + [float(duration), float(is_failure)]
        rows.append(row)

    return np.array(rows, dtype=np.float32)
