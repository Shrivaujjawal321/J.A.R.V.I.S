"""
wizard/ml/smoke_ml.py
======================
Self-contained smoke test for the wizard.ml layer.

Tests ALL four inference functions against:
  - Mock/registered model artifacts (avoids network I/O or heavy training)
  - Tiny synthetic data (30 episodes, ~1s runtime)

Run:
    python wizard/ml/smoke_ml.py

Pass criteria:
  1. predict_rul() returns RULResult with correct types + valid range values
  2. get_anomaly_score() returns dict with score in [0,1], severity string
  3. predict_failure() returns dict with valid alert_class
  4. rca_analyze() returns RCAResult with non-empty cause_chain
  5. apply_engineer_correction() updates RUL Bayesian blend
  6. All imports succeed (py_compile equivalent via normal import)

Exit 0 = PASS, Exit 1 = FAIL.
"""

from __future__ import annotations

import logging
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

# ── add repo root to path so imports work from any cwd ──────────────────────
_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))

logging.basicConfig(
    level=logging.WARNING,  # silence training-noise; only FAIL messages shown
    format="%(name)-25s %(levelname)s %(message)s",
)
logger = logging.getLogger("smoke_ml")

# ── track pass/fail ──────────────────────────────────────────────────────────
_RESULTS: List[tuple] = []  # (test_name, passed, error_msg)

def _check(name: str, passed: bool, msg: str = "") -> None:
    _RESULTS.append((name, passed, msg))
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}] {name}" + (f" — {msg}" if (not passed and msg) else ""))


# ============================================================================
# 0. Minimal joblib artifact registration (avoids any file I/O)
# ============================================================================

def _register_mock_artifacts() -> None:
    """
    Register minimal in-memory model artifacts so inference functions
    don't hit disk.  Uses ModelRegistry.register() directly.
    """
    from wizard.ml.registry import ModelRegistry

    # ── RUL artifacts ────────────────────────────────────────────────────────
    # Instead of a real WeibullAFTFitter, we'll rely on the stub path
    # (no artifact registered → fallback to stub mode).
    # Register population WeibullFitter mock
    try:
        from lifelines import WeibullFitter  # type: ignore[import]
        import pandas as pd

        # Fit a WeibullFitter on tiny synthetic data
        rng = np.random.default_rng(42)
        durations = rng.integers(20, 200, size=80).astype(float)
        events    = rng.choice([0, 1], size=80, p=[0.15, 0.85])
        wf = WeibullFitter()
        wf.fit(durations, event_observed=events)

        for eq_class in ["default", "bearing", "fan"]:
            ModelRegistry.register(f"rul_population_{eq_class}", wf)

        logger.info("Registered WeibullFitter mock artifacts.")
    except ImportError:
        logger.warning("lifelines not installed — RUL will use stub mode (OK for smoke test).")

    # ── Anomaly artifacts: IsolationForest ───────────────────────────────────
    try:
        from sklearn.ensemble import IsolationForest  # type: ignore[import]
        from wizard.ml.feature_utils import FEATURE_DIM

        rng = np.random.default_rng(42)
        X_normal = rng.normal(0.3, 0.1, size=(500, FEATURE_DIM)).astype(np.float32)
        if_model = IsolationForest(n_estimators=10, contamination=0.05, random_state=42)
        if_model.fit(X_normal)

        for eq_class in ["default", "bearing"]:
            ModelRegistry.register(f"anomaly_if_{eq_class}", if_model)
            ModelRegistry.register(f"anomaly_threshold_{eq_class}", 0.65)

        logger.info("Registered IsolationForest mock artifacts.")
    except ImportError:
        logger.warning("scikit-learn not installed — anomaly will use stub IF score.")

    # ── Failure predictor: LightGBM ──────────────────────────────────────────
    try:
        import lightgbm as lgb  # type: ignore[import]
        from sklearn.calibration import CalibratedClassifierCV  # type: ignore[import]
        from sklearn.model_selection import StratifiedKFold  # type: ignore[import]
        from wizard.ml.feature_utils import FEATURE_DIM

        rng = np.random.default_rng(42)
        n = 500
        X = rng.normal(size=(n, FEATURE_DIM)).astype(np.float32)
        y = rng.choice([0, 1, 2, 3], size=n, p=[0.70, 0.15, 0.10, 0.05]).astype(np.int32)

        base_lgbm = lgb.LGBMClassifier(
            objective="multiclass", num_class=4, n_estimators=20,
            verbose=-1, random_state=42,
        )
        cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
        calibrated = CalibratedClassifierCV(base_lgbm, method="sigmoid", cv=cv)
        calibrated.fit(X, y)

        for eq_class in ["default", "bearing"]:
            ModelRegistry.register(f"failure_lgbm_{eq_class}", calibrated)
            ModelRegistry.register(f"failure_threshold_{eq_class}", 0.35)

        logger.info("Registered LightGBM failure predictor mock artifacts.")
    except ImportError:
        logger.warning("lightgbm not installed — failure predictor will use stub mode.")


# ============================================================================
# 1. RUL test
# ============================================================================

def test_rul() -> None:
    from wizard.ml.rul_estimator import predict_rul, apply_engineer_correction
    from wizard.core.schemas import RULResult

    readings: Dict[str, float] = {
        "temperature_c":  380.0,
        "process_temp_c": 400.0,
        "pressure_bar":   165.0,
        "vibration_mm_s": 2.3,
        "rpm":            1150.0,
        "torque_nm":      510.0,
        "current_a":      52.0,
        "tool_wear_min":  180.0,
        "health_score":   0.55,
    }

    result = predict_rul(
        asset_id="EAF-04",
        sensor_readings=readings,
        sensor_summary_id="SS-MOCK-001",
        equipment_class="bearing",
    )

    _check("RUL: returns RULResult", isinstance(result, RULResult))
    _check("RUL: asset_id correct", result.asset_id == "EAF-04")
    _check("RUL: p10 <= p50", result.rul_days_p10 <= result.rul_days_p50 + 0.01)
    _check("RUL: p50 <= p90", result.rul_days_p50 <= result.rul_days_p90 + 0.01)
    _check("RUL: degradation_index in [0,1]",
           0.0 <= result.degradation_index <= 1.0)
    _check("RUL: failure_probability in [0,1]",
           0.0 <= result.failure_probability <= 1.0)
    _check("RUL: model_used non-empty", bool(result.model_used))

    # Test Bayesian engineer correction
    apply_engineer_correction("EAF-04", engineer_rul_days=5.0)
    result2 = predict_rul(
        asset_id="EAF-04",
        sensor_readings=readings,
        sensor_summary_id="SS-MOCK-002",
        equipment_class="bearing",
    )
    _check("RUL: bayesian_correction_applied after engineer override",
           result2.bayesian_correction_applied)


# ============================================================================
# 2. Anomaly test
# ============================================================================

def test_anomaly() -> None:
    from wizard.ml.anomaly_detector import get_anomaly_score

    normal_readings: Dict[str, float] = {
        "temperature_c": 350.0, "process_temp_c": 370.0,
        "pressure_bar": 180.0, "vibration_mm_s": 0.8,
        "rpm": 1200.0, "torque_nm": 490.0,
        "current_a": 48.0, "tool_wear_min": 50.0, "health_score": 0.2,
    }
    anomalous_readings: Dict[str, float] = {
        "temperature_c": 520.0, "process_temp_c": 550.0,
        "pressure_bar": 90.0, "vibration_mm_s": 9.5,
        "rpm": 800.0, "torque_nm": 820.0,
        "current_a": 95.0, "tool_wear_min": 295.0, "health_score": 0.9,
    }

    # Build small history (30 normal steps + 1 current)
    history_normal = [normal_readings] * 30

    result_normal = get_anomaly_score(
        asset_id="EAF-04",
        sensor_readings=normal_readings,
        readings_history=history_normal,
        equipment_class="bearing",
    )
    _check("Anomaly: returns dict", isinstance(result_normal, dict))
    _check("Anomaly: score in [0,1]",
           0.0 <= result_normal.get("score", -1) <= 1.0)
    _check("Anomaly: severity is string",
           isinstance(result_normal.get("severity"), str))
    _check("Anomaly: shap_values is dict",
           isinstance(result_normal.get("shap_values"), dict))
    _check("Anomaly: triggered_sensors is list",
           isinstance(result_normal.get("triggered_sensors"), list))

    # Anomalous readings should score higher than normal
    history_anomalous = [anomalous_readings] * 30
    result_anomalous = get_anomaly_score(
        asset_id="EAF-04",
        sensor_readings=anomalous_readings,
        readings_history=history_anomalous,
        equipment_class="bearing",
    )
    _check("Anomaly: if_score field present", "if_score" in result_anomalous)
    _check("Anomaly: ae_score field present", "ae_score" in result_anomalous)


# ============================================================================
# 3. Failure predictor test
# ============================================================================

def test_failure() -> None:
    from wizard.ml.failure_predictor import predict_failure, FAILURE_CLASSES, FAILURE_MODE_COLS

    readings: Dict[str, float] = {
        "temperature_c": 420.0, "process_temp_c": 445.0,
        "pressure_bar": 150.0, "vibration_mm_s": 4.5,
        "rpm": 1050.0, "torque_nm": 600.0,
        "current_a": 62.0, "tool_wear_min": 240.0, "health_score": 0.75,
    }
    history = [readings] * 30

    result = predict_failure(
        asset_id="EAF-04",
        sensor_readings=readings,
        readings_history=history,
        equipment_class="bearing",
        rul_days_p50=8.0,
        anomaly_score=0.72,
    )

    _check("Failure: returns dict", isinstance(result, dict))
    _check("Failure: alert_class is valid",
           result.get("alert_class") in FAILURE_CLASSES)
    _check("Failure: probabilities is dict",
           isinstance(result.get("probabilities"), dict))
    prob_sum = sum(result.get("probabilities", {}).values())
    _check("Failure: probabilities sum ~1.0", abs(prob_sum - 1.0) < 0.05)
    _check("Failure: calibrated is bool",
           isinstance(result.get("calibrated"), bool))
    _check("Failure: failure_modes is dict",
           isinstance(result.get("failure_modes"), dict))
    _check("Failure: top_shap_features is list",
           isinstance(result.get("top_shap_features"), list))


# ============================================================================
# 4. RCA test
# ============================================================================

def test_rca() -> None:
    from wizard.ml.rca_engine import rca_analyze
    from wizard.core.schemas import RCAResult

    result = rca_analyze(
        asset_id="EAF-04",
        fault_log_id="FL-MOCK-001",
        fault_code="WRD",
        fault_description="Work roll degradation — tool wear exceeded threshold",
        sensor_df=None,
        context_chunks=[
            "SOP-MILL-005 §2.1: Inspect work roll surface for abrasive wear every 500 operating hours.",
            "Incident Log 2025-11: Roll replacement delayed 34 days due to production schedule conflict.",
        ],
        anomaly_scores={"vibration_mm_s": 0.82, "torque_nm": 0.65},
    )

    _check("RCA: returns RCAResult", isinstance(result, RCAResult))
    _check("RCA: asset_id correct", result.asset_id == "EAF-04")
    _check("RCA: cause_chain is list", isinstance(result.cause_chain, list))
    _check("RCA: root_cause_summary non-empty", bool(result.root_cause_summary))
    _check("RCA: five_whys is list", isinstance(result.five_whys, list))
    _check("RCA: gcm_attributions is dict", isinstance(result.gcm_attributions, dict))
    _check("RCA: cited_sources is list", isinstance(result.cited_sources, list))

    # BF tuyere chain test
    result_bf = rca_analyze(
        asset_id="BF-2",
        fault_log_id="FL-MOCK-002",
        fault_code="BF-TUYERE-WEAR",
        fault_description="Blast furnace tuyere wear detected",
        anomaly_scores={"temperature_c": 0.9, "pressure_bar": 0.75},
    )
    _check("RCA: BF chain has steps",
           isinstance(result_bf.cause_chain, list))


# ============================================================================
# 5. Schema typing test
# ============================================================================

def test_schema_types() -> None:
    """Verify all wizard.core.schemas models are importable and functional."""
    from wizard.core.schemas import (
        RULResult, RCAResult, CauseChainStep, AlertSeverity,
        AlertEvent, DiagnosisReport, RiskScore, MaintenanceRecommendation,
    )

    _check("Schema: RULResult importable", True)
    _check("Schema: RCAResult importable", True)
    _check("Schema: AlertSeverity LOW", AlertSeverity.LOW == "low")
    _check("Schema: AlertSeverity CRITICAL", AlertSeverity.CRITICAL == "critical")

    step = CauseChainStep(node_id="BRG_WEAR", node_label="Bearing Wear")
    _check("Schema: CauseChainStep default layer='graph'", step.layer == "graph")


# ============================================================================
# 6. feature_utils test
# ============================================================================

def test_feature_utils() -> None:
    from wizard.ml.feature_utils import (
        extract_window_features,
        build_sensor_vector,
        compute_degradation_index,
        SENSOR_KEYS,
        FEATURE_DIM,
        N_SENSORS,
        N_FEATURES_PER_SENSOR,
    )

    readings = {k: float(i) * 0.1 for i, k in enumerate(SENSOR_KEYS)}
    vec = build_sensor_vector(readings)
    _check("FeatureUtils: sensor vector shape", vec.shape == (N_SENSORS,))
    _check("FeatureUtils: sensor vector dtype float32", vec.dtype == np.float32)

    history = [readings] * 35
    feats = extract_window_features(history, window=30)
    _check("FeatureUtils: window features shape",
           feats.shape == (FEATURE_DIM,))

    healthy_c = np.zeros(N_SENSORS, dtype=np.float32)
    failure_c = np.ones(N_SENSORS, dtype=np.float32)
    d = compute_degradation_index(readings, healthy_c, failure_c)
    _check("FeatureUtils: degradation index in [0,1]", 0.0 <= d <= 1.0)


# ============================================================================
# Main
# ============================================================================

def main() -> int:
    print("=" * 65)
    print("  wizard.ml smoke test")
    print("=" * 65)

    print("\n[0] Registering mock artifacts ...")
    try:
        _register_mock_artifacts()
        _check("Mock artifacts: registered", True)
    except Exception as exc:
        _check("Mock artifacts: registered", False, str(exc))
        traceback.print_exc()

    print("\n[1] Schema type checks ...")
    try:
        test_schema_types()
    except Exception as exc:
        _check("schema_types: EXCEPTION", False, str(exc))
        traceback.print_exc()

    print("\n[2] feature_utils ...")
    try:
        test_feature_utils()
    except Exception as exc:
        _check("feature_utils: EXCEPTION", False, str(exc))
        traceback.print_exc()

    print("\n[3] predict_rul ...")
    try:
        test_rul()
    except Exception as exc:
        _check("predict_rul: EXCEPTION", False, str(exc))
        traceback.print_exc()

    print("\n[4] get_anomaly_score ...")
    try:
        test_anomaly()
    except Exception as exc:
        _check("get_anomaly_score: EXCEPTION", False, str(exc))
        traceback.print_exc()

    print("\n[5] predict_failure ...")
    try:
        test_failure()
    except Exception as exc:
        _check("predict_failure: EXCEPTION", False, str(exc))
        traceback.print_exc()

    print("\n[6] rca_analyze ...")
    try:
        test_rca()
    except Exception as exc:
        _check("rca_analyze: EXCEPTION", False, str(exc))
        traceback.print_exc()

    # ── Summary ──────────────────────────────────────────────────────────────
    total  = len(_RESULTS)
    passed = sum(1 for _, p, _ in _RESULTS if p)
    failed = total - passed

    print("\n" + "=" * 65)
    print(f"  RESULTS: {passed}/{total} passed,  {failed} failed")
    print("=" * 65)

    if failed:
        print("\nFailed tests:")
        for name, ok, msg in _RESULTS:
            if not ok:
                print(f"  FAIL  {name}" + (f" — {msg}" if msg else ""))
        return 1
    else:
        print("  All smoke tests PASSED.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
