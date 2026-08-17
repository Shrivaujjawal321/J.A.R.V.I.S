"""VULCAN ML feature engineering — rolling-window stats on dense sensor tables.

The flagship `by_equipment/*.csv` tables are steel-native: one row per timestamp,
the asset's own physical-unit sensor columns + `fault_label` (0=normal, 1=warning,
2=failure). We build a per-row feature vector from a trailing window of W rows:
for each sensor column -> {mean, std, min, max, range, last, slope}. These window
features feed both the LightGBM fault classifier and the IsolationForest anomaly
detector, so a single deterministic featurizer keeps train/inference identical.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

META_COLS = ("timestamp", "asset_id", "equipment_class", "fault_label",
             "scenario_id", "run_id", "split", "opc_quality", "RUL_hours")
_STATS = ("mean", "std", "min", "max", "range", "last", "slope")


def sensor_columns(df: pd.DataFrame) -> list[str]:
    """Numeric sensor columns of a dense table (excludes meta + label)."""
    return [c for c in df.columns if c not in META_COLS]


def feature_names(sensor_cols: list[str]) -> list[str]:
    return [f"{c}__{s}" for c in sensor_cols for s in _STATS]


def _window_stats(window: np.ndarray) -> list[float]:
    """Stats for one sensor's trailing window (1-D array). NaN-safe."""
    w = window[~np.isnan(window)] if window.size else window
    if w.size == 0:
        return [0.0] * len(_STATS)
    mean = float(np.mean(w))
    std = float(np.std(w))
    mn = float(np.min(w))
    mx = float(np.max(w))
    rng = mx - mn
    last = float(w[-1])
    # slope = least-squares trend over the window (per-step)
    if w.size >= 2:
        x = np.arange(w.size, dtype=np.float64)
        slope = float(np.polyfit(x, w, 1)[0])
    else:
        slope = 0.0
    return [mean, std, mn, mx, rng, last, slope]


def build_window_matrix(
    df: pd.DataFrame, sensor_cols: list[str], window: int = 24
) -> tuple[np.ndarray, np.ndarray]:
    """Build (X, y) where each row i uses rows [i-window+1 .. i] of the table.

    Returns X (n_rows, n_sensors*7) float32 and y (n_rows,) int (fault_label).
    Rows before a full window use a shorter trailing window (warm-up tolerant)."""
    arr = df[sensor_cols].to_numpy(dtype=np.float64)
    n = arr.shape[0]
    feats = np.zeros((n, len(sensor_cols) * len(_STATS)), dtype=np.float32)
    for i in range(n):
        lo = max(0, i - window + 1)
        win = arr[lo:i + 1]
        row_feats: list[float] = []
        for j in range(len(sensor_cols)):
            row_feats.extend(_window_stats(win[:, j]))
        feats[i] = np.asarray(row_feats, dtype=np.float32)
    if "fault_label" in df.columns:
        y = df["fault_label"].fillna(0).to_numpy(dtype=np.int64)
    else:
        y = np.zeros(n, dtype=np.int64)
    return feats, y


def features_from_window(
    rows: list[dict], sensor_cols: list[str]
) -> np.ndarray:
    """Inference-time: build one feature vector from a list of recent reading dicts."""
    if not rows:
        return np.zeros(len(sensor_cols) * len(_STATS), dtype=np.float32)
    mat = np.array(
        [[float(r.get(c, np.nan)) if r.get(c) not in (None, "") else np.nan
          for c in sensor_cols] for r in rows],
        dtype=np.float64,
    )
    row_feats: list[float] = []
    for j in range(len(sensor_cols)):
        row_feats.extend(_window_stats(mat[:, j]))
    return np.asarray(row_feats, dtype=np.float32)
