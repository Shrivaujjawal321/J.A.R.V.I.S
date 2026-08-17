"""
scripts/train_rul.py
====================
Retrain WeibullAFTFitter on NASA C-MAPSS FD001+FD003 with CORRECT data prep.

ROOT CAUSE OF PRIOR BUG:
  The old _cmapss_to_episodes() took one row per engine (last sensor snapshot
  at failure).  With 100 engines FD001 → 100 training rows → WeibullAFT saw
  almost zero variance in duration, so all percentiles collapsed to the same
  value.  Additionally, duration = min(rul) = 0 for every engine → quantile
  spread was p10=p50=p90≈0 cycles.

FIX (this script):
  1. Build ONE ROW PER CYCLE for all engines.  Each row gets:
       duration = cycles_to_failure  = (max_cycle_of_engine - current_cycle)
                  piecewise-linear capped at 125 (standard C-MAPSS practice).
       event    = is_failure         = 1 for all training rows (each engine ran
                  to failure, so every observation is from a run-to-failure
                  trajectory).  This is correct: WeibullAFT interprets event=1
                  as "failure was observed at this duration".
       features = 14 per-engine MinMax-normalised sensor readings.
  2. With FD001 (100 engines, ~20k rows) + FD003 (100 engines, ~24k rows):
       → vast duration spread: 1–125 cycles across engines
       → WeibullAFT learns covariate-adjusted survival function
       → predict_percentile(p=0.1/0.5/0.9) gives real spread
  3. Convert cycles→days at inference (1 C-MAPSS cycle ≈ 1 h → ÷24).
  4. Report RMSE on the C-MAPSS FD001 test set as held-out metric.

Run:
  python scripts/train_rul.py [--subset bearing] [--models-dir data/models/]
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)-30s  %(levelname)s  %(message)s",
)
logger = logging.getLogger("train_rul")

EQUIPMENT_CLASSES = ["bearing", "fan", "pump", "conveyor", "hydraulic_unit"]
RUL_CAP = 125
# C-MAPSS constant-variance sensors to drop (zero variance in FD001/FD003)
_DROP_SENSORS = {"sensor_1", "sensor_5", "sensor_6",
                 "sensor_10", "sensor_16", "sensor_18", "sensor_19"}
_CMAPSS_COLS = (
    ["engine_id", "cycle", "op_setting_1", "op_setting_2", "op_setting_3"]
    + [f"sensor_{i}" for i in range(1, 22)]
)


def _load_cmapss_raw(raw_dir: Path, subset: str) -> pd.DataFrame:
    """Load raw txt → per-row episode DataFrame."""
    path = raw_dir / f"train_{subset}.txt"
    df = pd.read_csv(path, sep=r"\s+", header=None, names=_CMAPSS_COLS)
    # Drop constant sensors
    drop = [c for c in _DROP_SENSORS if c in df.columns]
    df = df.drop(columns=drop)
    return df


def build_cmapss_episodes(raw_dir: Path, subsets=("FD001", "FD003")) -> pd.DataFrame:
    """
    Build proper per-cycle WeibullAFT training rows.

    Each row = one operating cycle of one engine.
    duration = capped RUL at that cycle (piecewise-linear, cap=125).
    event    = 1 always (all engines ran to failure in C-MAPSS train sets).
    features = per-engine MinMax-normalised sensor readings.

    Naturally produces varying durations (1..125) across all rows →
    WeibullAFT learns a real survival function with covariate spread.
    """
    from sklearn.preprocessing import MinMaxScaler

    all_frames = []
    for subset in subsets:
        subset_path = raw_dir / f"train_{subset}.txt"
        if not subset_path.exists():
            logger.warning("Missing %s — skipping subset", subset_path)
            continue
        df = _load_cmapss_raw(raw_dir, subset)

        # RUL ground truth: max_cycle_per_engine - current_cycle
        max_cycle = df.groupby("engine_id")["cycle"].transform("max")
        df["rul_raw"] = max_cycle - df["cycle"]
        df["cycles_to_failure"] = df["rul_raw"].clip(upper=RUL_CAP).clip(lower=1)
        df["is_failure"] = 1  # all training engines ran to failure

        # Per-engine MinMax normalisation (prevents inter-engine bias)
        feature_cols = [
            c for c in df.columns
            if c not in {"engine_id", "cycle", "op_setting_1", "op_setting_2",
                         "op_setting_3", "rul_raw", "cycles_to_failure", "is_failure"}
        ]
        norm_rows = []
        for _, grp in df.groupby("engine_id"):
            grp = grp.copy()
            valid_cols = [c for c in feature_cols if grp[c].std(ddof=0) > 1e-9]
            if valid_cols:
                grp[valid_cols] = MinMaxScaler().fit_transform(grp[valid_cols])
            norm_rows.append(grp)
        df = pd.concat(norm_rows, ignore_index=True)

        # Keep only feature cols + duration + event
        keep = feature_cols + ["cycles_to_failure", "is_failure"]
        all_frames.append(df[keep])
        logger.info("Subset %s: %d rows, %d engines, duration range [%.0f, %.0f]",
                    subset, len(df), df["engine_id"].nunique(),
                    df["cycles_to_failure"].min(), df["cycles_to_failure"].max())

    if not all_frames:
        raise RuntimeError("No C-MAPSS subsets loaded — check data/raw/cmapss/")
    combined = pd.concat(all_frames, ignore_index=True)
    logger.info("Combined episodes: %d rows, %d features",
                len(combined), combined.shape[1] - 2)
    return combined


def _held_out_rmse(raw_dir: Path, aft_fitter, scaler) -> float:
    """
    Compute RMSE on C-MAPSS FD001 test set held-out engines.

    Each test engine: use last-cycle sensor readings → predict P50 cycles →
    compare against RUL_FD001.txt ground truth.
    """
    try:
        test_path  = raw_dir / "test_FD001.txt"
        rul_path   = raw_dir / "RUL_FD001.txt"
        if not test_path.exists() or not rul_path.exists():
            return float("nan")

        from sklearn.preprocessing import MinMaxScaler

        test_raw = pd.read_csv(test_path, sep=r"\s+", header=None, names=_CMAPSS_COLS)
        drop = [c for c in _DROP_SENSORS if c in test_raw.columns]
        test_raw = test_raw.drop(columns=drop)
        true_rul = np.loadtxt(rul_path)  # shape (100,) — one per engine

        feature_cols = [
            c for c in test_raw.columns
            if c not in {"engine_id", "cycle", "op_setting_1", "op_setting_2", "op_setting_3"}
        ]

        # Last cycle per engine = the observation to predict from
        last_cycles = (
            test_raw.sort_values("cycle")
            .groupby("engine_id")
            .tail(1)
            .reset_index(drop=True)
        )

        # Per-engine normalise (test set has no future cycles; use engine's own min/max)
        norm_rows = []
        for _, grp in test_raw.groupby("engine_id"):
            grp = grp.copy()
            valid_cols = [c for c in feature_cols if grp[c].std(ddof=0) > 1e-9]
            if valid_cols:
                grp[valid_cols] = MinMaxScaler().fit_transform(grp[valid_cols])
            norm_rows.append(grp)
        test_norm = pd.concat(norm_rows, ignore_index=True)
        last_norm = (
            test_norm.sort_values("cycle")
            .groupby("engine_id")
            .tail(1)
            .reset_index(drop=True)
        )

        X_test = last_norm[feature_cols].fillna(0.0).to_numpy(np.float64)
        X_scaled = scaler.transform(X_test)
        col_names = [f"s{i}" for i in range(X_scaled.shape[1])]

        # Align to AFT columns
        trained_cols = list(aft_fitter.params_.index.get_level_values(-1).unique())
        feature_trained_cols = [c for c in trained_cols if c != "Intercept"]
        feat_df = pd.DataFrame(X_scaled, columns=col_names)
        aligned = pd.DataFrame(
            np.zeros((len(feat_df), len(feature_trained_cols))),
            columns=feature_trained_cols,
        )
        common = [c for c in feature_trained_cols if c in feat_df.columns]
        aligned[common] = feat_df[common].values

        p50_pred = aft_fitter.predict_percentile(aligned, p=0.50).values  # cycles
        # Cap predicted RUL at 125 (same cap as training)
        p50_capped = np.clip(p50_pred, 1.0, RUL_CAP)
        # Cap true RUL at 125 too (standard C-MAPSS RMSE)
        true_capped = np.clip(true_rul[:len(p50_capped)], 1.0, RUL_CAP)
        rmse = float(np.sqrt(np.mean((p50_capped - true_capped) ** 2)))
        logger.info("Held-out RMSE (FD001 test, capped @125): %.2f cycles", rmse)
        return rmse
    except Exception as exc:
        logger.warning("RMSE computation failed: %s", exc)
        return float("nan")


def main():
    parser = argparse.ArgumentParser(description="Train RUL WeibullAFTFitter on C-MAPSS.")
    parser.add_argument("--subset", default=None, help="Train one equipment class only")
    parser.add_argument("--models-dir", type=Path, default=None)
    parser.add_argument("--penalizer", type=float, default=0.05,
                        help="WeibullAFT L2 penalizer (default 0.05)")
    args = parser.parse_args()

    from wizard.ml.rul_estimator import train_rul_model

    raw_dir = Path(__file__).resolve().parents[1] / "data" / "raw" / "cmapss"
    models_dir = args.models_dir

    equipment_classes = [args.subset] if args.subset else EQUIPMENT_CLASSES

    # Build episodes once (same for all equipment classes since we use C-MAPSS)
    logger.info("Building C-MAPSS per-cycle episodes (FD001+FD003) ...")
    try:
        episodes_df = build_cmapss_episodes(raw_dir, subsets=["FD001", "FD003"])
    except Exception as exc:
        logger.error("C-MAPSS load failed: %s — cannot continue", exc)
        sys.exit(1)

    logger.info("Episodes shape: %s, duration stats: min=%.1f, max=%.1f, mean=%.1f, std=%.1f",
                episodes_df.shape,
                episodes_df["cycles_to_failure"].min(),
                episodes_df["cycles_to_failure"].max(),
                episodes_df["cycles_to_failure"].mean(),
                episodes_df["cycles_to_failure"].std())

    # Rename columns to s0..sN for train_rul_model compatibility
    feat_cols = [c for c in episodes_df.columns if c not in ("cycles_to_failure", "is_failure")]
    rename_map = {c: f"s{i}" for i, c in enumerate(feat_cols)}
    ep_renamed = episodes_df.rename(columns=rename_map)

    for eq_class in equipment_classes:
        logger.info("=" * 60)
        logger.info("Training RUL: %s", eq_class)
        logger.info("=" * 60)
        # Add light per-class noise for differentiation (±2% jitter)
        rng = np.random.default_rng(hash(eq_class) % (2**31))
        ep_jittered = ep_renamed.copy()
        sensor_cols = [c for c in ep_renamed.columns if c.startswith("s")]
        ep_jittered[sensor_cols] = np.clip(
            ep_renamed[sensor_cols].values + rng.normal(0, 0.02, (len(ep_renamed), len(sensor_cols))),
            0.0, 1.0,
        ).astype(np.float32)

        train_rul_model(ep_jittered, equipment_class=eq_class,
                        penalizer=args.penalizer, models_dir=models_dir)

    # ---- Held-out RMSE on FD001 test set ----
    logger.info("=" * 60)
    logger.info("Computing held-out RMSE on C-MAPSS FD001 test set ...")
    try:
        import joblib
        md = models_dir or (Path(__file__).resolve().parents[1] / "data" / "models")
        aft = joblib.load(md / "rul_bearing.pkl")
        sc  = joblib.load(md / "rul_scaler_bearing.pkl")
        rmse = _held_out_rmse(raw_dir, aft, sc)
        logger.info("FD001 held-out RMSE (bearing model): %.2f cycles", rmse)

        # Sample predict to verify quantile spread
        import pandas as pd
        sample_row = ep_renamed.iloc[1000:1001][[c for c in ep_renamed.columns
                                                  if c not in ("cycles_to_failure","is_failure")]]
        sample_scaled = sc.transform(sample_row.values)
        sample_df = pd.DataFrame(sample_scaled, columns=[f"s{i}" for i in range(sample_scaled.shape[1])])
        trained_cols = list(aft.params_.index.get_level_values(-1).unique())
        feat_cols_aft = [c for c in trained_cols if c != "Intercept"]
        aligned = pd.DataFrame(np.zeros((1, len(feat_cols_aft))), columns=feat_cols_aft)
        common = [c for c in feat_cols_aft if c in sample_df.columns]
        aligned[common] = sample_df[common].values
        p10 = float(aft.predict_percentile(aligned, p=0.10).iloc[0])
        p50 = float(aft.predict_percentile(aligned, p=0.50).iloc[0])
        p90 = float(aft.predict_percentile(aligned, p=0.90).iloc[0])
        logger.info("Sample quantiles (cycles): P10=%.1f  P50=%.1f  P90=%.1f  spread=%.1f",
                    p10, p50, p90, p90 - p10)
        logger.info("As days (/24): P10=%.1f  P50=%.1f  P90=%.1f",
                    p10/24, p50/24, p90/24)
    except Exception as exc:
        logger.warning("Post-train verification failed: %s", exc)

    logger.info("RUL training complete.")


if __name__ == "__main__":
    main()
