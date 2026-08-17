"""
wizard/ml/train_rul.py
=======================
Entrypoint: train WeibullAFTFitter RUL models for all 5 equipment classes.

Uses synthetic episode data (offline-safe) by default.
If C-MAPSS is already cached in data/raw/cmapss/, it will be used for
higher-quality training.

Artifacts written to data/models/:
  rul_{equipment_class}.pkl          — WeibullAFTFitter
  rul_population_{equipment_class}.pkl — WeibullFitter fallback
  rul_scaler_{equipment_class}.pkl   — StandardScaler
  rul_centroids_{equipment_class}.pkl — dict {'healthy':[], 'failure':[], 'feature_cols':[]}

Usage::
    python wizard/ml/train_rul.py [--epochs 10] [--use-cmapss]
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("train_rul")

EQUIPMENT_CLASSES = ["bearing", "fan", "pump", "conveyor", "hydraulic_unit"]


def _make_synthetic_episodes(equipment_class: str, n: int = 80, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic WeibullAFT training episodes (offline-safe)."""
    from wizard.ml.feature_utils import make_synthetic_episodes

    arr = make_synthetic_episodes(n_engines=n, rng_seed=seed)
    n_sensors = arr.shape[1] - 2
    cols = [f"s{i}" for i in range(n_sensors)] + ["cycles_to_failure", "is_failure"]
    df = pd.DataFrame(arr, columns=cols)
    df["cycles_to_failure"] = df["cycles_to_failure"].clip(lower=1.0)
    log.info(
        "[%s] Synthetic episodes: %d rows, %.0f%% failure",
        equipment_class, len(df), df["is_failure"].mean() * 100,
    )
    return df


def _try_cmapss_episodes() -> "pd.DataFrame | None":
    """
    Load C-MAPSS FD001+FD003 and build a multi-row episode dataset for WeibullAFT.

    Design (2026-06-07 fix — v2):
    ─────────────────────────────
    Classic approach for survival-model RUL: each observation is one (engine, time-step)
    with covariate = current sensor readings and duration = rul_capped (cycles remaining).
    This is correct because:
      1. Each row is an independent observation of "how many cycles remain given
         the current sensor state" — exactly what WeibullAFT is modeling.
      2. Different time steps from the same engine appear at different degradation
         levels → the AFT learns that high-degradation sensors → short remaining life.
      3. Duration (rul_capped) varies 0–125 across all rows → genuine spread in the
         survival distribution → predict_percentile(p=0.1) << p=0.5 << p=0.9.

    Sampling strategy: take every STRIDE-th row per engine to avoid excessive
    autocorrelation while keeping ~2000 total rows (manageable for CPU WeibullAFT).

    Feature mapping:
      C-MAPSS normalized sensors → 9 SENSOR_KEYS (s0..s8) used at inference.
      All sensors are already per-engine MinMax normalized [0,1] by the loader, so
      the StandardScaler fit on this data produces a z-score distribution that is
      compatible with the inference-time physical-range normalization → [0,1] →
      StandardScaler(same_params) path.

    Returns None on failure (caller falls back to synthetic episodes).
    """
    raw_dir = _REPO_ROOT / "data" / "raw" / "cmapss"
    required_fd001 = [raw_dir / f for f in ("train_FD001.txt", "test_FD001.txt", "RUL_FD001.txt")]
    if not all(p.exists() for p in required_fd001):
        log.info("C-MAPSS FD001 files not cached — using synthetic episodes.")
        return None

    available_subsets = ["FD001"]
    if all((raw_dir / f).exists() for f in ("train_FD003.txt", "test_FD003.txt", "RUL_FD003.txt")):
        available_subsets.append("FD003")

    # Sample every STRIDE cycles per engine to keep dataset size manageable on CPU.
    # FD001 has ~200 cycles/engine × 100 engines = 20k rows.
    # STRIDE=10 → ~2000 rows, fast WeibullAFT fit with rich covariate range.
    STRIDE = 10

    # C-MAPSS column → sensor slot (s0..s8) mapping.
    # SENSOR_KEYS at inference: temperature_c, process_temp_c, pressure_bar,
    # vibration_mm_s, rpm, torque_nm, current_a, tool_wear_min, health_score.
    cmapss_to_sensor = {
        "sensor_2":     "s0",   # temperature_c  ← fan/compressor inlet temp
        "sensor_4":     "s1",   # process_temp_c ← HPC outlet temp
        "sensor_7":     "s2",   # pressure_bar   ← HPC outlet pressure
        "sensor_11":    "s3",   # vibration_mm_s ← vibration RMS
        "op_setting_2": "s4",   # rpm            ← speed/load setting
        "sensor_21":    "s5",   # torque_nm      ← shaft torque
        "sensor_20":    "s6",   # current_a      ← bleed flow rate
        "sensor_12":    "s7",   # tool_wear_min  ← bleed enthalpy (wear proxy)
        "health_score": "s8",   # health_score   ← 1 - rul_capped/125 (from loader)
    }

    try:
        from wizard.data.cmapss_loader import load_cmapss

        ds = load_cmapss(subsets=available_subsets, raw_dir=raw_dir)
        all_rows = []

        for subset in available_subsets:
            train_df = ds.train.get(subset)
            if train_df is None or len(train_df) == 0:
                continue

            for engine_id, grp in train_df.groupby("engine_id"):
                grp_sorted = grp.sort_values("cycle").reset_index(drop=True)
                # Sample every STRIDE-th row; always include the last row (rul_capped=0)
                indices = list(range(0, len(grp_sorted), STRIDE))
                if len(grp_sorted) - 1 not in indices:
                    indices.append(len(grp_sorted) - 1)

                for idx in indices:
                    row = grp_sorted.iloc[idx]
                    rul_remaining = float(row.get("rul_capped", row.get("rul", 1.0)))
                    # Clamp to [1, 125]; avoid zero duration (censored rows)
                    rul_remaining = max(1.0, min(125.0, rul_remaining))
                    is_failure = 1.0 if float(row.get("rul", 0.0)) == 0.0 else 0.0

                    sensor_vals: dict = {}
                    for cmapss_col, skey in cmapss_to_sensor.items():
                        val = float(row.get(cmapss_col, 0.0))
                        sensor_vals[skey] = val

                    sensor_vals["cycles_to_failure"] = rul_remaining
                    sensor_vals["is_failure"] = is_failure
                    all_rows.append(sensor_vals)

        if not all_rows:
            log.warning("C-MAPSS parsing produced no rows — falling back to synthetic.")
            return None

        df = pd.DataFrame(all_rows).fillna(0.0)
        df["cycles_to_failure"] = df["cycles_to_failure"].clip(lower=1.0)

        # Summary stats for verification
        failure_pct = df["is_failure"].mean() * 100
        dur_min = df["cycles_to_failure"].min()
        dur_max = df["cycles_to_failure"].max()
        dur_std = df["cycles_to_failure"].std()
        dur_mean = df["cycles_to_failure"].mean()
        log.info(
            "C-MAPSS multi-step episodes (%s): %d rows, %d sensor features, "
            "rul_capped [%.0f, %.0f] (mean=%.0f, std=%.0f), %.1f%% failure events",
            "+".join(available_subsets),
            len(df),
            len(cmapss_to_sensor),
            dur_min, dur_max, dur_mean, dur_std,
            failure_pct,
        )
        return df

    except Exception as exc:
        log.warning("C-MAPSS load failed (%s) — falling back to synthetic.", exc)
        return None


def main(use_cmapss: bool = True) -> None:
    from wizard.ml.rul_estimator import train_rul_model

    models_dir = _REPO_ROOT / "data" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    # Always try C-MAPSS first when data is present (it gives real quantile spread).
    # Synthetic episodes are the fallback — they produce flat quantiles.
    cmapss_df = _try_cmapss_episodes() if use_cmapss else None

    for eq_class in EQUIPMENT_CLASSES:
        log.info("=" * 55)
        log.info("Training RUL model: %s", eq_class)
        log.info("=" * 55)

        seed = abs(hash(eq_class)) % (2 ** 31) + 42

        if cmapss_df is not None:
            ep_df = cmapss_df.copy()
        else:
            ep_df = _make_synthetic_episodes(eq_class, n=100, seed=seed)

        train_rul_model(
            episodes_df=ep_df,
            equipment_class=eq_class,
            penalizer=0.1,
            models_dir=models_dir,
        )

    log.info("RUL training complete. Artifacts in %s", models_dir)
    # List produced artifacts
    pkls = sorted(models_dir.glob("rul_*.pkl"))
    for p in pkls:
        log.info("  %s (%.1f KB)", p.name, p.stat().st_size / 1024)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train WeibullAFT RUL models")
    parser.add_argument("--no-cmapss", action="store_true",
                        help="Force synthetic episodes (skip C-MAPSS even if cached)")
    args = parser.parse_args()

    main(use_cmapss=not args.no_cmapss)
    sys.exit(0)
