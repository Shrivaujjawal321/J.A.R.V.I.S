"""
wizard/ml/train_failure.py
==========================
Entrypoint: train LightGBM 4-class ordinal failure classifiers + isotonic calibration
for all 5 equipment classes.

Uses synthetic data (offline-safe) by default.
If AI4I 2020 is cached in data/raw/ai4i/, it will be used for higher-quality training.

Artifacts written to data/models/:
  failure_lgbm_{equipment_class}.pkl      — CalibratedClassifierCV
  failure_threshold_{equipment_class}.pkl — Optimal decision threshold (float)

Usage::
    python wizard/ml/train_failure.py [--use-ai4i] [--n-estimators 200]
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
log = logging.getLogger("train_failure")

EQUIPMENT_CLASSES = ["bearing", "fan", "pump", "conveyor", "hydraulic_unit"]


def _make_synthetic_failure_df(n: int = 2000, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic 4-class ordinal failure dataset (offline-safe)."""
    from wizard.ml.feature_utils import FEATURE_DIM

    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, FEATURE_DIM)).astype(np.float32)
    # Realistic class distribution: ~70% NORMAL, 15% WARN_72H, 10% WARN_24H, 5% IMMINENT
    probs = [0.70, 0.15, 0.10, 0.05]
    y = rng.choice([0, 1, 2, 3], size=n, p=probs).astype(np.int32)
    cols = [f"f{i}" for i in range(FEATURE_DIM)]
    df = pd.DataFrame(X, columns=cols)
    df["failure_class"] = y
    log.info(
        "Synthetic failure dataset: %d rows, class distribution=%s",
        n,
        dict(zip([0, 1, 2, 3], np.bincount(y, minlength=4))),
    )
    return df


def _try_ai4i_failure_df() -> "pd.DataFrame | None":
    """
    Load AI4I 2020 and build a 4-class ordinal failure dataset.

    FIX (2026-06-07): The prior implementation mapped AI4I binary machine_failure
    to classes {0=NORMAL, 3=IMMINENT} only, leaving classes 1 (WARN_72H) and
    2 (WARN_24H) with zero samples.  LightGBM class_weight then fails with KeyError.

    Correct approach — create synthetic warning levels from non-failure samples
    using domain-motivated severity indicators:
      - tool_wear_min: high wear → approaching failure
      - rotational_speed_rpm: low rpm at high torque → stress
      - delta_temp_c: high process-air delta → thermal stress

    Label assignment for non-failure rows (machine_failure=0):
      - WARN_72H (class 1): top-15% severity score  → ~13% of normal rows
      - WARN_24H (class 2): top-5% severity score   → ~4% of normal rows
      - NORMAL   (class 0): remaining ~83% of normal rows

    Label assignment for failure rows (machine_failure=1):
      - IMMINENT (class 3): all 339 rows (3.4%)

    Final distribution: {0: ~8k, 1: ~1.4k, 2: ~490, 3: ~339}
    This gives all 4 classes real samples → avoids KeyError + forces LGBM to
    learn a genuine ordinal signal from sensor features.

    The severity score is a composite normalized rank — no external data needed.
    """
    raw_dir = _REPO_ROOT / "data" / "raw" / "ai4i"
    csv_path = raw_dir / "ai4i2020.csv"
    if not csv_path.exists():
        log.info("AI4I CSV not cached — using synthetic failure data.")
        return None

    try:
        from wizard.data.ai4i_loader import load_ai4i, FEATURE_COLS
        from wizard.ml.feature_utils import FEATURE_DIM

        df = load_ai4i(raw_dir=raw_dir)
        available = [c for c in FEATURE_COLS if c in df.columns]
        X = df[available].fillna(0.0).to_numpy(np.float32)

        # Build ordinal 4-class labels with all classes populated.
        labels = np.zeros(len(df), dtype=np.int32)

        # Step 1: Mark all true failures as IMMINENT (class 3).
        failure_mask = df["machine_failure"].values == 1
        labels[failure_mask] = 3

        # Step 2: For non-failure rows, compute a severity score and split into
        # NORMAL / WARN_72H / WARN_24H using percentile thresholds.
        normal_mask = ~failure_mask
        normal_df = df[normal_mask].copy()

        # Severity components (all higher = more stressed):
        #   tool_wear_min: normalized [0,1] by global max; high wear → high severity
        #   torque_nm:     high torque → mechanical stress
        #   delta_temp_c:  large temp differential → thermal stress
        #   rotational_speed_rpm: low rpm at same torque → overload; use inverted
        severity = np.zeros(normal_mask.sum(), dtype=np.float64)

        for col, weight, invert in [
            ("tool_wear_min",        0.40, False),
            ("torque_nm",            0.25, False),
            ("delta_temp_c",         0.20, False),
            ("rotational_speed_rpm", 0.15, True),   # lower rpm → higher stress
        ]:
            if col in normal_df.columns:
                s = normal_df[col].fillna(0.0).values.astype(np.float64)
                s_min, s_max = s.min(), s.max()
                if s_max > s_min:
                    s_norm = (s - s_min) / (s_max - s_min)
                else:
                    s_norm = np.zeros_like(s)
                if invert:
                    s_norm = 1.0 - s_norm
                severity += weight * s_norm

        # Percentile thresholds: top 5% → WARN_24H (class 2), next 10% → WARN_72H (class 1)
        p95 = np.percentile(severity, 95)
        p85 = np.percentile(severity, 85)

        normal_labels = np.zeros(len(severity), dtype=np.int32)
        normal_labels[severity >= p95] = 2   # WARN_24H
        normal_labels[(severity >= p85) & (severity < p95)] = 1   # WARN_72H

        # Assign back to main label array (normal rows only)
        normal_indices = np.where(normal_mask)[0]
        for i, lbl in zip(normal_indices, normal_labels):
            labels[i] = lbl

        # FIX (2026-06-07 v2): Build 54-dim window features from simulated history.
        # The inference path calls extract_window_features(30-step history) → 54 dims.
        # If we pad raw 6-dim AI4I features to 54 with zeros, the model learns from
        # a different feature space than inference uses → no discrimination.
        #
        # Correct approach: for each AI4I row (6 sensors), simulate a 30-step history
        # by adding small Gaussian noise around the base reading, then call
        # extract_window_features to produce the same 54-dim features as inference.
        # This keeps training and inference feature spaces aligned.
        log.info("Building 54-dim window features from AI4I readings (may take ~30s)...")
        try:
            from wizard.ml.feature_utils import extract_window_features
            from wizard.ml.rul_estimator import _normalize_sensor_readings, _SENSOR_PHYSICAL_RANGE

            AI4I_COL_TO_SENSOR = {
                "air_temp_c": "temperature_c",
                "process_temp_c": "process_temp_c",
                "delta_temp_c": None,              # derived, not a direct sensor key
                "rotational_speed_rpm": "rpm",
                "torque_nm": "torque_nm",
                "tool_wear_min": "tool_wear_min",
            }
            SENSOR_KEYS_9 = [
                "temperature_c", "process_temp_c", "pressure_bar",
                "vibration_mm_s", "rpm", "torque_nm",
                "current_a", "tool_wear_min", "health_score",
            ]

            def row_to_sensor_dict(row_dict):
                """Map one AI4I row to the 9-sensor inference dict, filling defaults."""
                sr = {}
                sr["temperature_c"]   = float(row_dict.get("air_temp_c", 250.0))
                sr["process_temp_c"]  = float(row_dict.get("process_temp_c", 300.0))
                sr["pressure_bar"]    = 100.0   # AI4I has no pressure — use midrange
                sr["vibration_mm_s"]  = 1.0     # AI4I has no vibration — use midrange
                sr["rpm"]             = float(row_dict.get("rotational_speed_rpm", 1500.0))
                sr["torque_nm"]       = float(row_dict.get("torque_nm", 400.0))
                sr["current_a"]       = 30.0    # AI4I has no current — use midrange
                sr["tool_wear_min"]   = float(row_dict.get("tool_wear_min", 100.0))
                sr["health_score"]    = 0.3     # placeholder
                return sr

            def norm_reading(sr):
                """Normalize one sensor dict from physical units to [0, 1]."""
                out = {}
                for key in SENSOR_KEYS_9:
                    lo, hi = _SENSOR_PHYSICAL_RANGE.get(key, (0.0, 1.0))
                    val = float(sr.get(key, 0.0))
                    rng = hi - lo
                    out[key] = float(np.clip((val - lo) / rng if rng > 0 else 0.0, 0.0, 1.0))
                return out

            rng_gen = np.random.default_rng(42)
            df_records = df.to_dict("records")
            n_rows = len(df_records)
            X_window = np.zeros((n_rows, FEATURE_DIM), dtype=np.float32)

            W = 30   # window length — matches inference _WINDOW
            noise_std = 0.02  # small noise to create history variation (in [0,1] space)

            for i, record in enumerate(df_records):
                base_sr = norm_reading(row_to_sensor_dict(record))
                base_arr = np.array([base_sr[k] for k in SENSOR_KEYS_9], dtype=np.float32)
                # Simulate W-step history: base reading ± small noise
                noise = rng_gen.normal(0.0, noise_std, size=(W, len(SENSOR_KEYS_9))).astype(np.float32)
                history_arr = np.clip(base_arr[None, :] + noise, 0.0, 1.0)  # (W, 9)
                # Convert to list of dicts for extract_window_features
                history = [{k: float(history_arr[t, j]) for j, k in enumerate(SENSOR_KEYS_9)}
                           for t in range(W)]
                feats = extract_window_features(history, window=W, sensor_keys=SENSOR_KEYS_9)
                X_window[i] = feats[:FEATURE_DIM]

            log.info("Window features built: %d rows × %d dims", n_rows, FEATURE_DIM)
            X = X_window

        except Exception as exc:
            log.warning("Window feature build failed (%s) — falling back to padded raw features.", exc)
            # Original fallback: pad raw 6-dim to 54-dim
            if X.shape[1] < FEATURE_DIM:
                pad = np.zeros((len(X), FEATURE_DIM - X.shape[1]), dtype=np.float32)
                X = np.concatenate([X, pad], axis=1)
            elif X.shape[1] > FEATURE_DIM:
                X = X[:, :FEATURE_DIM]

        cols = [f"f{i}" for i in range(FEATURE_DIM)]
        fail_df = pd.DataFrame(X, columns=cols)
        fail_df["failure_class"] = labels

        dist = dict(zip(*np.unique(labels, return_counts=True)))
        log.info(
            "AI4I 4-class failure dataset: %d rows, distribution=%s  "
            "(NORMAL/WARN_72H/WARN_24H/IMMINENT)",
            len(fail_df), dist,
        )
        return fail_df

    except Exception as exc:
        log.warning("AI4I load failed (%s) — falling back to synthetic.", exc)
        return None


def main(use_ai4i: bool = True, n_estimators: int = 300) -> None:
    """
    Train failure predictors for all 5 equipment classes.

    use_ai4i=True (default): use real AI4I 2020 data with window-feature simulation.
    use_ai4i=False: use synthetic 54-dim random data (offline-safe fallback).
    """
    from wizard.ml.failure_predictor import train_failure_model

    models_dir = _REPO_ROOT / "data" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    ai4i_df = None
    if use_ai4i:
        ai4i_df = _try_ai4i_failure_df()

    for eq_class in EQUIPMENT_CLASSES:
        log.info("=" * 55)
        log.info("Training failure predictor: %s", eq_class)
        log.info("=" * 55)

        seed = abs(hash(eq_class)) % (2 ** 31) + 42

        if ai4i_df is not None:
            fail_df = ai4i_df.copy()
        else:
            fail_df = _make_synthetic_failure_df(n=2000, seed=seed)

        train_failure_model(
            train_df=fail_df,
            equipment_class=eq_class,
            n_estimators=n_estimators,
            models_dir=models_dir,
        )

    log.info("Failure model training complete. Artifacts in %s", models_dir)
    pkls = sorted(models_dir.glob("failure_*.pkl"))
    for p in pkls:
        log.info("  %s (%.1f KB)", p.name, p.stat().st_size / 1024)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train LightGBM failure prediction models")
    parser.add_argument("--no-ai4i", action="store_true",
                        help="Force synthetic data even if AI4I 2020 is cached (default: use AI4I)")
    parser.add_argument("--n-estimators", type=int, default=300,
                        help="LightGBM n_estimators (default: 300)")
    args = parser.parse_args()

    main(use_ai4i=not args.no_ai4i, n_estimators=args.n_estimators)
    sys.exit(0)
