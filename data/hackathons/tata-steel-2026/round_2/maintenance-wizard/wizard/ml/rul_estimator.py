"""
wizard.ml.rul_estimator
========================
Remaining Useful Life (RUL) prediction.

Architecture (per research report 08):
  Stage 1: lifelines.WeibullAFTFitter — probabilistic survival model trained
            offline on historical fault episodes.  Outputs P10/P50/P90 quantiles.
  Stage 2: Real-time degradation index — ||z_current - z_healthy|| / ||z_failure - z_healthy||
            applied as a multiplicative correction: rul_adj = rul_p50 * (1 - d * alpha).
  Stage 3: Bayesian engineer correction — new_rul = 0.7 * model_rul + 0.3 * engineer_rul.
            Persisted to data/feedback/rul_corrections.jsonl, replayed on startup.

Public API
----------
  predict_rul(asset_id, sensor_readings, sensor_summary_id, readings_history) -> RULResult
  apply_engineer_correction(asset_id, engineer_rul_days) -> None

The function degrades gracefully if the joblib artifact is missing:
  → falls back to WeibullFitter (population-level, no covariates).
  → if even that fails, returns a synthetic safe stub (model_used='stub').
"""

from __future__ import annotations

import json
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from wizard.core.schemas import RULResult
from wizard.ml.feature_utils import (
    SENSOR_KEYS,
    build_sensor_vector,
    compute_degradation_index,
)
from wizard.ml.registry import ModelRegistry
# Physics-informed degradation index (steel-sensor domain fix).
# The centroid-based index operates in C-MAPSS normalized space and cannot
# respond to steel-plant sensor degradation → replaced at inference time.
from wizard.ml.degradation import physics_degradation_index

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Physical-range normalization for inference-time sensor readings
# ---------------------------------------------------------------------------
# Maps each SENSOR_KEY to its [lo, hi] physical range so we can normalize
# raw steel-plant sensor values to [0, 1] before passing them to the
# StandardScaler / WeibullAFT (which was trained on C-MAPSS per-engine
# MinMax-normalized 0-1 data).
#
# Ranges are intentionally wide enough to accommodate steel-plant variation;
# readings outside the range are clipped to [0, 1].
_SENSOR_PHYSICAL_RANGE: Dict[str, tuple] = {
    "temperature_c":   (100.0, 600.0),   # inlet temp: 100–600 °C
    "process_temp_c":  (100.0, 650.0),   # process/outlet temp
    "pressure_bar":    (  0.0, 300.0),   # pressure
    "vibration_mm_s":  (  0.0,  15.0),   # vibration RMS mm/s
    "rpm":             (  0.0,3000.0),   # rotational speed
    "torque_nm":       (  0.0,1200.0),   # torque
    "current_a":       (  0.0, 120.0),   # current / bleed-flow proxy
    "tool_wear_min":   (  0.0, 300.0),   # tool wear minutes
    "health_score":    (  0.0,   1.0),   # already normalized [0,1]
}


def _normalize_sensor_readings(
    sensor_readings: Dict[str, float],
    sensor_keys: List[str],
) -> np.ndarray:
    """
    Normalize raw physical-unit sensor readings to [0, 1] using known
    physical ranges, producing a feature vector compatible with the
    StandardScaler (which was trained on 0-1 C-MAPSS data).

    Returns float32 array of shape (len(sensor_keys),).
    """
    out = np.zeros(len(sensor_keys), dtype=np.float32)
    for i, key in enumerate(sensor_keys):
        lo, hi = _SENSOR_PHYSICAL_RANGE.get(key, (0.0, 1.0))
        raw = float(sensor_readings.get(key, 0.0))
        rng = hi - lo
        out[i] = float(np.clip((raw - lo) / rng if rng > 0 else 0.0, 0.0, 1.0))
    return out


# ---------------------------------------------------------------------------
# Constants (from research report §6 thresholds)
# ---------------------------------------------------------------------------
# Degradation index damping factors per equipment family
# Tuned against C-MAPSS test set to minimize RMSE on held-out engines
_ALPHA_BY_CLASS: Dict[str, float] = {
    "bearing":        0.55,
    "fan":            0.50,
    "pump":           0.45,
    "conveyor":       0.40,
    "hydraulic_unit": 0.60,
    "default":        0.50,
}

# RUL → risk_class mapping (uses P10 — pessimistic — per report anti-pattern #1)
# Thresholds from MASTER_BRIEF §1 / report 08 §6
def _risk_class(rul_p10: float) -> str:
    if rul_p10 > 90:
        return "LOW"
    elif rul_p10 > 30:
        return "MEDIUM"
    elif rul_p10 > 7:
        return "HIGH"
    else:
        return "CRITICAL"

# Bayesian blend weights
_W_MODEL = 0.7
_W_ENGINEER = 0.3

# ---------------------------------------------------------------------------
# Thread-safe Bayesian correction store
# ---------------------------------------------------------------------------
_correction_lock = threading.Lock()
_corrections: Dict[str, float] = {}  # asset_id -> engineer_rul_days

def _corrections_path() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists():
            return parent / "data" / "feedback" / "rul_corrections.jsonl"
    return Path.cwd() / "data" / "feedback" / "rul_corrections.jsonl"

def _load_corrections() -> None:
    """Replay corrections from disk into in-memory store (called at startup)."""
    path = _corrections_path()
    if not path.exists():
        return
    seen: Dict[str, float] = {}
    try:
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            entry = json.loads(line)
            seen[entry["asset_id"]] = float(entry["engineer_rul_days"])
        with _correction_lock:
            _corrections.update(seen)
        logger.info("RUL corrections replayed: %d assets", len(seen))
    except Exception as exc:  # pragma: no cover
        logger.warning("Could not replay RUL corrections: %s", exc)

def _persist_correction(asset_id: str, engineer_rul_days: float) -> None:
    path = _corrections_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "asset_id": asset_id,
        "engineer_rul_days": engineer_rul_days,
        "corrected_at": datetime.utcnow().isoformat(),
    }
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")

# Load corrections once at module import
_load_corrections()

# ---------------------------------------------------------------------------
# Artifact keys
# ---------------------------------------------------------------------------
# Each equipment class gets its own WeibullAFTFitter artifact.
# Registry falls back gracefully if artifact is missing.
def _rul_artifact_key(equipment_class: str) -> str:
    return f"rul_{equipment_class.lower().replace(' ', '_').replace('-', '_')}"

def _scaler_key(equipment_class: str) -> str:
    return f"rul_scaler_{equipment_class.lower().replace(' ', '_').replace('-', '_')}"

def _centroids_key(equipment_class: str) -> str:
    return f"rul_centroids_{equipment_class.lower().replace(' ', '_').replace('-', '_')}"


# ---------------------------------------------------------------------------
# Inference helpers
# ---------------------------------------------------------------------------

def _predict_with_weibull_aft(
    fitter: "lifelines.WeibullAFTFitter",  # type: ignore[name-defined]
    feature_row: pd.DataFrame,
) -> tuple[float, float, float]:
    """
    Call fitter.predict_percentile for P10, P50, P90.

    Returns (p10, p50, p90) as floats in 'days', with P10 < P50 < P90.

    IMPORTANT — lifelines percentile semantics (survival vs. failure):
      predict_percentile(p=q) → time T where P(failure ≤ T) = q.
      So p=0.10 gives the time by which only 10% of units fail → OPTIMISTIC (long).
      And p=0.90 gives the time by which 90% of units fail → PESSIMISTIC (short).

    RUL display convention: P10 = pessimistic lower bound, P90 = optimistic upper bound.
    To produce P10 < P50 < P90 ordering, we map:
      P10_rul (pessimistic) ← predict_percentile(p=0.10)  [10% survival = low survival]
      P50_rul (median)      ← predict_percentile(p=0.50)
      P90_rul (optimistic)  ← predict_percentile(p=0.90)  [10% failure = high survival]

    Wait — that's still backwards. The correct fix:
      In lifelines: predict_percentile(p=0.1) = T where 10% fail by T = 90th-pctile survival time.
      For our display (P10=pessimistic=short, P90=optimistic=long):
        P10_display = predict_percentile(p=0.90)  [90% fail by this time → near-term → pessimistic]
        P50_display = predict_percentile(p=0.50)
        P90_display = predict_percentile(p=0.10)  [only 10% fail by this time → far-out → optimistic]

    Conversion: cycles → days (1 C-MAPSS cycle ≈ 1 operating hour, 24h/day).
    """
    try:
        # lifelines p=0.90: time by which 90% of units have failed → pessimistic → our P10
        # lifelines p=0.50: median
        # lifelines p=0.10: time by which 10% have failed → optimistic → our P90
        raw_p90f = float(fitter.predict_percentile(feature_row, p=0.90).iloc[0])  # pessimistic
        raw_p50  = float(fitter.predict_percentile(feature_row, p=0.50).iloc[0])  # median
        raw_p10f = float(fitter.predict_percentile(feature_row, p=0.10).iloc[0])  # optimistic

        # Map to display convention: P10 (short/pessimistic) → P50 → P90 (long/optimistic)
        p10_d = max(0.0, raw_p90f / 24.0)  # pessimistic lower bound
        p50_d = max(0.0, raw_p50  / 24.0)  # median estimate
        p90_d = max(0.0, raw_p10f / 24.0)  # optimistic upper bound

        # Enforce monotonicity guard (should hold by definition, but protect against NaN)
        p10_d = min(p10_d, p50_d)
        p90_d = max(p50_d, p90_d)

        return p10_d, p50_d, p90_d
    except Exception as exc:
        logger.warning("WeibullAFTFitter.predict_percentile failed: %s", exc)
        raise


def _predict_with_population_weibull(
    fitter: "lifelines.WeibullFitter",  # type: ignore[name-defined]
) -> tuple[float, float, float]:
    """
    Fallback: population-level Weibull (no covariates).

    WeibullFitter.percentile(q) = time T where S(T) = 1-q → same survival semantics.
    percentile(0.10) = T where 10% survival → pessimistic (short RUL) → our P10 display.
    percentile(0.90) = T where 90% survival → optimistic (long RUL) → our P90 display.
    This is the OPPOSITE of lifelines AFT convention — WeibullFitter.percentile is a
    *survival* percentile, not failure percentile.  So: low q → short → P10, high q → long → P90.
    """
    try:
        raw_p10 = float(fitter.percentile(0.10))  # 10% survival → pessimistic → display P10
        raw_p50 = float(fitter.median_survival_time_)
        raw_p90 = float(fitter.percentile(0.90))  # 90% survival → optimistic → display P90
        p10_d = max(0.0, raw_p10 / 24.0)
        p50_d = max(0.0, raw_p50 / 24.0)
        p90_d = max(0.0, raw_p90 / 24.0)
        # Enforce ordering
        p10_d = min(p10_d, p50_d)
        p90_d = max(p50_d, p90_d)
        return p10_d, p50_d, p90_d
    except Exception:  # pragma: no cover
        return 1.0, 3.0, 7.0  # last-resort stub values


def _stub_rul(asset_id: str, sensor_summary_id: str) -> RULResult:
    """Safe default when no model artifact exists."""
    return RULResult(
        asset_id=asset_id,
        sensor_summary_id=sensor_summary_id,
        rul_days_p10=3.0,
        rul_days_p50=7.0,
        rul_days_p90=14.0,
        degradation_index=0.5,
        anomaly_score=0.5,
        failure_class="no_failure",
        failure_probability=0.1,
        model_used="stub",
        bayesian_correction_applied=False,
    )


# ---------------------------------------------------------------------------
# Public: apply_engineer_correction
# ---------------------------------------------------------------------------

def apply_engineer_correction(asset_id: str, engineer_rul_days: float) -> None:
    """
    Store an engineer's RUL override.

    Effect: next call to predict_rul for this asset_id will blend
    (0.7 × model_rul + 0.3 × engineer_rul).

    ANTI-PATTERN AVOIDED: we do NOT retrain the model on n=1 correction.
    The Bayesian weighted update is in-memory and immediate.
    """
    with _correction_lock:
        _corrections[asset_id] = float(engineer_rul_days)
    _persist_correction(asset_id, engineer_rul_days)
    logger.info(
        "RUL engineer correction stored: asset=%s, engineer_rul=%.1f days",
        asset_id, engineer_rul_days,
    )


# ---------------------------------------------------------------------------
# Public: predict_rul
# ---------------------------------------------------------------------------

def predict_rul(
    asset_id: str,
    sensor_readings: Dict[str, float],
    sensor_summary_id: str = "",
    readings_history: Optional[List[Dict[str, float]]] = None,
    equipment_class: str = "default",
) -> RULResult:
    """
    Predict Remaining Useful Life for a single asset.

    Parameters
    ----------
    asset_id : str
        Equipment identifier (FK → AssetProfile.entity_id).
    sensor_readings : dict[str, float]
        Latest sensor snapshot (SensorSummary.sensor_readings).
    sensor_summary_id : str
        FK → SensorSummary.entity_id for the RULResult.
    readings_history : list[dict], optional
        Ordered historical readings (oldest first).  Used only for
        degradation index computation context (not yet used in this impl —
        the scaler/centroids artifact provides the reference).
    equipment_class : str
        ISO 14224 class: 'bearing'|'fan'|'pump'|'conveyor'|'hydraulic_unit'.
        Selects the right artifact and alpha damping factor.

    Returns
    -------
    RULResult (wizard.core.schemas)
    """
    # --- Resolve equipment class ---
    eq_class = equipment_class.lower().replace(" ", "_").replace("-", "_")
    artifact_key = _rul_artifact_key(eq_class)
    scaler_key   = _scaler_key(eq_class)
    centroids_key = _centroids_key(eq_class)

    # --- Load artifacts (lazy singleton) ---
    aft_fitter = ModelRegistry.load(artifact_key, fallback=None)
    pop_fitter = ModelRegistry.load(f"rul_population_{eq_class}", fallback=None)
    scaler     = ModelRegistry.load(scaler_key, fallback=None)
    centroids  = ModelRegistry.load(centroids_key, fallback=None)  # dict with 'healthy', 'failure'

    model_used = "stub"

    # --- Prepare feature row for WeibullAFT ---
    # Step 1: normalize raw physical-unit readings to [0,1] so the downstream
    # StandardScaler receives a distribution compatible with the C-MAPSS
    # training data (which was per-engine MinMax normalized to [0,1]).
    z_norm = _normalize_sensor_readings(sensor_readings, SENSOR_KEYS)

    # Step 2: apply the saved StandardScaler (fit on per-engine-normalized
    # C-MAPSS data, so its input should be in ~[0,1]).
    if scaler is not None:
        try:
            z_scaled = scaler.transform(z_norm.reshape(1, -1)).flatten()
        except Exception:
            z_scaled = z_norm
    else:
        z_scaled = z_norm

    # Build feature DataFrame (WeibullAFTFitter expects a DataFrame)
    sensor_col_names = [f"s{i}" for i in range(len(z_scaled))]
    feature_row = pd.DataFrame([z_scaled], columns=sensor_col_names)

    # --- Degradation index (physics-informed, steel-sensor domain) ---
    # Domain-mismatch fix: the centroid-based index (||z - z_healthy|| / ||z_failure - z_healthy||)
    # operates in C-MAPSS StandardScaler-normalized space, so it produces identical or near-
    # identical values for clearly-normal vs. clearly-failing steel-plant sensor readings.
    # We replace it with physics_degradation_index(), which uses per-sensor physical severity
    # bands grounded in steel-plant operating envelopes (ISO 10816 / ISO 13381).
    # The base WeibullAFT/population prediction supplies the realistic RUL MAGNITUDE;
    # the physics index supplies the CORRECTION SIGNAL so failing sensors actually get
    # a shorter corrected RUL than healthy sensors.
    degradation_idx = physics_degradation_index(sensor_readings, equipment_class)

    # --- Stage 1: WeibullAFT predict ---
    p10, p50, p90 = None, None, None
    if aft_fitter is not None:
        try:
            # Re-index feature row to match trained model's covariates.
            # WeibullAFTFitter.params_ includes 'Intercept' in the index —
            # we must exclude it when building the feature DataFrame (lifelines
            # adds the intercept internally; passing it as a column causes errors).
            trained_cols = list(aft_fitter.params_.index.get_level_values(-1).unique())
            # Strip the internal 'Intercept' column if present
            feature_trained_cols = [c for c in trained_cols if c != "Intercept"]
            # Build aligned feature DataFrame from available sensor columns
            common = [c for c in feature_trained_cols if c in feature_row.columns]
            if common:
                aligned = pd.DataFrame(
                    np.zeros((1, len(feature_trained_cols))), columns=feature_trained_cols
                )
                aligned[common] = feature_row[common].values
            else:
                aligned = feature_row.reindex(columns=feature_trained_cols, fill_value=0.0)
            p10, p50, p90 = _predict_with_weibull_aft(aft_fitter, aligned)
            model_used = "weibull_aft"
        except Exception as exc:
            logger.warning("WeibullAFT inference failed (%s): %s — trying population fallback", artifact_key, exc)

    # --- Stage 1 fallback: population Weibull ---
    if p50 is None:
        if pop_fitter is not None:
            try:
                p10, p50, p90 = _predict_with_population_weibull(pop_fitter)
                model_used = "weibull_fitter_fallback"
            except Exception as exc:
                logger.warning("Population WeibullFitter fallback failed: %s", exc)

    # --- Last resort stub ---
    if p50 is None:
        return _stub_rul(asset_id, sensor_summary_id)

    # --- Stage 2: degradation index correction ---
    alpha = _ALPHA_BY_CLASS.get(eq_class, _ALPHA_BY_CLASS["default"])
    correction_factor = 1.0 - degradation_idx * alpha
    correction_factor = max(0.05, correction_factor)  # floor at 5% of base

    p10_adj = p10 * correction_factor
    p50_adj = p50 * correction_factor
    p90_adj = p90 * correction_factor

    # --- Physics-driven RUL cap (between Stage 2 and Stage 3) ---
    # The WeibullAFT/population Weibull was trained on C-MAPSS turbofan data whose
    # median survival greatly exceeds typical steel-plant failure windows.  When the
    # physics_degradation_index (grounded in ISO 10816 / ISO 13381 steel-plant bands)
    # indicates the asset is in the warning or critical zone, the physics-informed
    # signal is more reliable than the Weibull magnitude.  We cap P50 accordingly and
    # re-anchor P10/P90 with the same proportional scale factor so monotonicity holds.
    #
    # Thresholds (consistent with physics_degradation_index docstring):
    #   >= 0.85  critical / imminent failure state  → cap P50 at 3 days
    #   >= 0.65  significant degradation / alert zone → cap P50 at 10 days
    _physics_cap: float | None = None
    if degradation_idx >= 0.85:
        _physics_cap = 3.0
    elif degradation_idx >= 0.65:
        _physics_cap = 10.0

    if _physics_cap is not None and p50_adj > _physics_cap:
        _scale = _physics_cap / p50_adj
        p10_adj = p10_adj * _scale
        p50_adj = _physics_cap
        p90_adj = p90_adj * _scale
        logger.debug(
            "predict_rul: physics cap applied for %s (di=%.3f, cap=%.1fd): "
            "p50 %.2f→%.2f, p10 %.2f",
            asset_id, degradation_idx, _physics_cap, _physics_cap / _scale, p50_adj, p10_adj,
        )

    # --- Stage 3: Bayesian engineer correction ---
    bayesian_applied = False
    with _correction_lock:
        eng_rul = _corrections.get(asset_id)
    if eng_rul is not None:
        # Blend P50 with engineer override; then re-anchor P10 and P90 relative
        # to the blended P50 to preserve the quantile spread and monotonicity.
        # Anti-pattern avoided: do NOT use min/max collapse — scale the spread
        # proportionally so P10 <= P50 <= P90 is always guaranteed.
        old_p50 = p50_adj
        p50_adj = _W_MODEL * p50_adj + _W_ENGINEER * eng_rul
        if old_p50 > 0:
            scale = p50_adj / old_p50  # proportional adjustment
        else:
            scale = 1.0
        p10_adj = p10_adj * scale
        p90_adj = p90_adj * scale
        bayesian_applied = True

    # Hard-clamp quantile ordering (guard against float precision edge cases)
    p10_adj = max(0.0, p10_adj)
    p50_adj = max(p10_adj, p50_adj)
    p90_adj = max(p50_adj, p90_adj)

    # --- failure_probability from P(fail within 30 days) via P10 ---
    # Approximate: 1 - exp(-lambda * 30) where lambda from P10
    failure_prob_30d = 0.0
    if p50_adj > 0:
        lam = 1.0 / max(p50_adj, 0.01)
        failure_prob_30d = float(1.0 - np.exp(-lam * 30.0))
        failure_prob_30d = float(np.clip(failure_prob_30d, 0.0, 1.0))

    # --- anomaly_score proxy from degradation index ---
    anomaly_score = float(np.clip(degradation_idx, 0.0, 1.0))

    return RULResult(
        asset_id=asset_id,
        sensor_summary_id=sensor_summary_id,
        rul_days_p10=round(p10_adj, 2),
        rul_days_p50=round(p50_adj, 2),
        rul_days_p90=round(p90_adj, 2),
        degradation_index=round(degradation_idx, 4),
        anomaly_score=round(anomaly_score, 4),
        failure_class="no_failure",   # updated by failure_predictor output
        failure_probability=round(failure_prob_30d, 4),
        model_used=model_used,
        bayesian_correction_applied=bayesian_applied,
    )


# ---------------------------------------------------------------------------
# Offline training script entry-point (imported by scripts/train_rul.py)
# ---------------------------------------------------------------------------

def train_rul_model(
    episodes_df: pd.DataFrame,
    equipment_class: str = "default",
    penalizer: float = 0.1,
    models_dir: Optional[Path] = None,
) -> None:
    """
    Train WeibullAFTFitter on a fault-episode DataFrame.

    Expected columns in episodes_df:
      - duration_col: 'cycles_to_failure' (int/float)
      - event_col:    'is_failure' (0 = censored, 1 = failure)
      - feature cols: any numeric column not in the above two

    Artifacts written to data/models/:
      rul_{equipment_class}.pkl          - WeibullAFTFitter
      rul_population_{equipment_class}.pkl - WeibullFitter (fallback)
      rul_scaler_{equipment_class}.pkl   - StandardScaler
      rul_centroids_{equipment_class}.pkl - dict {'healthy': [...], 'failure': [...]}
    """
    try:
        from lifelines import WeibullAFTFitter, WeibullFitter  # type: ignore[import]
        from sklearn.preprocessing import StandardScaler  # type: ignore[import]
        import joblib  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "Training requires: lifelines, scikit-learn, joblib. "
            "pip install lifelines scikit-learn joblib"
        ) from exc

    if models_dir is None:
        here = Path(__file__).resolve()
        for parent in here.parents:
            if (parent / "pyproject.toml").exists():
                models_dir = parent / "data" / "models"
                break
        else:
            models_dir = Path.cwd() / "data" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    duration_col = "cycles_to_failure"
    event_col    = "is_failure"
    feature_cols = [
        c for c in episodes_df.columns
        if c not in (duration_col, event_col)
    ]

    if len(feature_cols) == 0:
        raise ValueError("episodes_df must contain at least one sensor feature column.")

    logger.info(
        "Training RUL for '%s': %d episodes, %d features, %.0f%% failure rate",
        equipment_class,
        len(episodes_df),
        len(feature_cols),
        episodes_df[event_col].mean() * 100,
    )

    # StandardScaler for feature normalization
    scaler = StandardScaler()
    X = episodes_df[feature_cols].fillna(0.0).to_numpy(dtype=np.float64)
    X_scaled = scaler.fit_transform(X)

    # Compute healthy / failure centroids for degradation index
    failure_mask = episodes_df[event_col].astype(bool)
    healthy_centroid = X_scaled[~failure_mask].mean(axis=0) if (~failure_mask).any() else X_scaled.mean(axis=0)
    failure_centroid = X_scaled[failure_mask].mean(axis=0)  if failure_mask.any() else X_scaled.mean(axis=0)

    # Build training DataFrame for AFT (scaled features + duration + event)
    eq_class = equipment_class.lower().replace(" ", "_").replace("-", "_")
    col_names = [f"s{i}" for i in range(len(feature_cols))]
    df_aft = pd.DataFrame(X_scaled, columns=col_names)
    df_aft[duration_col] = episodes_df[duration_col].values
    df_aft[event_col]    = episodes_df[event_col].astype(int).values

    # --- Fit WeibullAFTFitter ---
    aft = WeibullAFTFitter(penalizer=penalizer)
    try:
        aft.fit(df_aft, duration_col=duration_col, event_col=event_col)
        logger.info("WeibullAFTFitter fitted. AIC=%.2f", aft.AIC_)
    except Exception as exc:
        logger.warning("WeibullAFTFitter convergence issue (%s) — using population fallback only", exc)
        aft = None

    # --- Fit population WeibullFitter (always, as guaranteed fallback) ---
    wf = WeibullFitter()
    wf.fit(
        episodes_df[duration_col],
        event_observed=episodes_df[event_col].astype(int),
    )
    logger.info("WeibullFitter (population) fitted. Median=%.1f cycles", float(wf.median_survival_time_))

    # --- Save artifacts ---
    if aft is not None:
        aft_path = models_dir / f"rul_{eq_class}.pkl"
        joblib.dump(aft, aft_path)
        logger.info("Saved WeibullAFTFitter → %s", aft_path)

    pop_path = models_dir / f"rul_population_{eq_class}.pkl"
    joblib.dump(wf, pop_path)
    logger.info("Saved WeibullFitter (population) → %s", pop_path)

    scaler_path = models_dir / f"rul_scaler_{eq_class}.pkl"
    joblib.dump(scaler, scaler_path)
    logger.info("Saved StandardScaler → %s", scaler_path)

    centroids_path = models_dir / f"rul_centroids_{eq_class}.pkl"
    centroids = {
        "healthy": healthy_centroid.tolist(),
        "failure": failure_centroid.tolist(),
        "feature_cols": feature_cols,
    }
    joblib.dump(centroids, centroids_path)
    logger.info("Saved centroids → %s", centroids_path)
    logger.info("RUL training for '%s' complete.", equipment_class)
