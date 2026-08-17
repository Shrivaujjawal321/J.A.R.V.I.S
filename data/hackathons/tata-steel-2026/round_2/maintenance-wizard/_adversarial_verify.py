"""
Adversarial discrimination verification for wizard.ml.

Tests each of the 5 equipment classes (bearing, fan, pump, conveyor, hydraulic_unit)
with a clearly-NORMAL reading vs a clearly-FAILING reading, and checks:

  (a) RUL: failing p50 < 0.5 * normal p50, and p10 <= p50 <= p90 monotonic,
           and normal p50 is believable (1 day <= p50 <= 3650 days)
  (b) Failure: normal -> NORMAL (or low warn), failing -> WARN_24H/IMMINENT,
               with prob gap >= 0.20 between sum(warn+imminent) for failing vs normal
  (c) Anomaly: failing score > normal score by >= 0.10 margin; severity escalates

Exit 0 if all 15 checks pass, exit 1 if any fail.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Add repo root to sys.path
_REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(_REPO))

import numpy as np

# ---------------------------------------------------------------------------
# Sensor snapshots — chosen to be UNAMBIGUOUSLY normal vs failing
# ---------------------------------------------------------------------------

# Each class gets its own normal/failing pair.
# Normal: all sensors comfortably inside the normal bands defined in degradation.py
# Failing: multiple sensors at or beyond critical thresholds

_NORMAL_READINGS: Dict[str, Dict[str, float]] = {
    "bearing": {
        "temperature_c": 300.0,      # normal 200-400
        "process_temp_c": 320.0,     # normal 200-450
        "pressure_bar": 165.0,       # normal 120-220
        "vibration_mm_s": 1.2,       # normal 0-2.5
        "rpm": 1200.0,               # normal 900-1500
        "torque_nm": 450.0,          # normal 200-700
        "current_a": 40.0,           # normal 20-70
        "tool_wear_min": 60.0,       # normal 0-150
        "health_score": 0.15,        # normal 0-0.45
    },
    "fan": {
        "temperature_c": 310.0,
        "process_temp_c": 330.0,
        "pressure_bar": 160.0,       # normal 80-220
        "vibration_mm_s": 2.5,       # normal 0-4.5 for fan
        "rpm": 1100.0,               # normal 700-1600 for fan
        "torque_nm": 400.0,
        "current_a": 38.0,
        "tool_wear_min": 50.0,
        "health_score": 0.12,
    },
    "pump": {
        "temperature_c": 300.0,
        "process_temp_c": 320.0,
        "pressure_bar": 155.0,       # normal 100-200 for pump
        "vibration_mm_s": 1.5,       # normal 0-3.0 for pump
        "rpm": 1200.0,
        "torque_nm": 400.0,
        "current_a": 38.0,
        "tool_wear_min": 60.0,
        "health_score": 0.12,
    },
    "conveyor": {
        "temperature_c": 290.0,
        "process_temp_c": 310.0,
        "pressure_bar": 150.0,
        "vibration_mm_s": 1.8,
        "rpm": 800.0,                # normal 200-1400 for conveyor
        "torque_nm": 350.0,          # normal 100-650 for conveyor
        "current_a": 35.0,           # normal 15-65 for conveyor
        "tool_wear_min": 60.0,
        "health_score": 0.12,
    },
    "hydraulic_unit": {
        "temperature_c": 260.0,      # normal 150-380 for hydraulic
        "process_temp_c": 290.0,
        "pressure_bar": 185.0,       # normal 120-250 for hydraulic
        "vibration_mm_s": 1.5,       # normal 0-3.0 for hydraulic
        "rpm": 1100.0,
        "torque_nm": 400.0,
        "current_a": 38.0,
        "tool_wear_min": 60.0,
        "health_score": 0.12,
    },
}

_FAILING_READINGS: Dict[str, Dict[str, float]] = {
    "bearing": {
        "temperature_c": 510.0,      # critical > 510 for bearing
        "process_temp_c": 550.0,     # critical > 560
        "pressure_bar": 38.0,        # critical < 40 (lube pressure drop)
        "vibration_mm_s": 9.0,       # critical > 5.5 for bearing
        "rpm": 480.0,                # critical < 500
        "torque_nm": 890.0,          # critical > 900 approaching
        "current_a": 98.0,           # critical > 100
        "tool_wear_min": 290.0,      # critical 220-300
        "health_score": 0.92,        # critical > 0.65
    },
    "fan": {
        "temperature_c": 510.0,
        "process_temp_c": 545.0,
        "pressure_bar": 18.0,        # critical < 20
        "vibration_mm_s": 12.0,      # critical > 8.5 for fan
        "rpm": 280.0,                # critical < 300 for fan
        "torque_nm": 880.0,
        "current_a": 98.0,
        "tool_wear_min": 290.0,
        "health_score": 0.90,
    },
    "pump": {
        "temperature_c": 510.0,
        "process_temp_c": 545.0,
        "pressure_bar": 28.0,        # critical < 30 for pump
        "vibration_mm_s": 10.0,      # critical > 6.5 for pump
        "rpm": 480.0,
        "torque_nm": 880.0,
        "current_a": 98.0,
        "tool_wear_min": 290.0,
        "health_score": 0.90,
    },
    "conveyor": {
        "temperature_c": 510.0,
        "process_temp_c": 545.0,
        "pressure_bar": 18.0,
        "vibration_mm_s": 9.0,
        "rpm": 45.0,                 # critical < 50 for conveyor
        "torque_nm": 890.0,          # critical > 900 approaching
        "current_a": 93.0,           # critical > 95 for conveyor
        "tool_wear_min": 290.0,
        "health_score": 0.90,
    },
    "hydraulic_unit": {
        "temperature_c": 480.0,      # critical > 490 for hydraulic
        "process_temp_c": 545.0,
        "pressure_bar": 38.0,        # critical < 40 for hydraulic
        "vibration_mm_s": 9.0,       # critical > 6.0 for hydraulic
        "rpm": 480.0,
        "torque_nm": 880.0,
        "current_a": 98.0,
        "tool_wear_min": 290.0,
        "health_score": 0.90,
    },
}

EQUIPMENT_CLASSES = ["bearing", "fan", "pump", "conveyor", "hydraulic_unit"]

# ---------------------------------------------------------------------------
# Result tracking
# ---------------------------------------------------------------------------

_RESULTS: List[Tuple[str, str, str, bool, str]] = []  # (class, metric, check, passed, detail)


def record(eq_class: str, metric: str, check: str, passed: bool, detail: str = "") -> None:
    _RESULTS.append((eq_class, metric, check, passed, detail))
    status = "PASS" if passed else "FAIL"
    tag = f"{eq_class:>16s} | {metric:>7s} | {check:<45s}"
    print(f"  [{status}] {tag}  {detail}")


# ---------------------------------------------------------------------------
# RUL checks
# ---------------------------------------------------------------------------

def check_rul(eq_class: str) -> None:
    from wizard.ml.rul_estimator import predict_rul

    normal = _NORMAL_READINGS[eq_class]
    failing = _FAILING_READINGS[eq_class]

    r_norm = predict_rul(
        asset_id=f"test-normal-{eq_class}",
        sensor_readings=normal,
        sensor_summary_id="SN-1",
        equipment_class=eq_class,
    )
    r_fail = predict_rul(
        asset_id=f"test-fail-{eq_class}",
        sensor_readings=failing,
        sensor_summary_id="SN-2",
        equipment_class=eq_class,
    )

    p50_n = r_norm.rul_days_p50
    p50_f = r_fail.rul_days_p50
    p10_n = r_norm.rul_days_p10
    p90_n = r_norm.rul_days_p90
    p10_f = r_fail.rul_days_p10
    p90_f = r_fail.rul_days_p90

    detail_a = f"fail_p50={p50_f:.2f} < 0.5*norm_p50={0.5*p50_n:.2f} (norm={p50_n:.2f})"
    record(eq_class, "RUL", "(a) failing p50 < 0.5 * normal p50",
           p50_f < 0.5 * p50_n, detail_a)

    mono_norm = p10_n <= p50_n + 1e-4 and p50_n <= p90_n + 1e-4
    detail_mono_n = f"norm: p10={p10_n:.2f} p50={p50_n:.2f} p90={p90_n:.2f}"
    record(eq_class, "RUL", "(a) normal p10<=p50<=p90 monotonic",
           mono_norm, detail_mono_n)

    mono_fail = p10_f <= p50_f + 1e-4 and p50_f <= p90_f + 1e-4
    detail_mono_f = f"fail: p10={p10_f:.2f} p50={p50_f:.2f} p90={p90_f:.2f}"
    record(eq_class, "RUL", "(a) failing p10<=p50<=p90 monotonic",
           mono_fail, detail_mono_f)

    believable = 1.0 <= p50_n <= 3650.0
    detail_bel = f"norm p50={p50_n:.2f} days (expect 1–3650)"
    record(eq_class, "RUL", "(a) normal p50 believable (1–3650 days)",
           believable, detail_bel)


# ---------------------------------------------------------------------------
# Failure predictor checks
# ---------------------------------------------------------------------------

def check_failure(eq_class: str) -> None:
    from wizard.ml.failure_predictor import predict_failure

    normal = _NORMAL_READINGS[eq_class]
    failing = _FAILING_READINGS[eq_class]

    history_norm = [normal] * 32
    history_fail = [failing] * 32

    r_norm = predict_failure(
        asset_id=f"test-normal-{eq_class}",
        sensor_readings=normal,
        readings_history=history_norm,
        equipment_class=eq_class,
    )
    r_fail = predict_failure(
        asset_id=f"test-fail-{eq_class}",
        sensor_readings=failing,
        readings_history=history_fail,
        equipment_class=eq_class,
    )

    alert_n = r_norm.get("alert_class", "?")
    alert_f = r_fail.get("alert_class", "?")
    probs_n = r_norm.get("probabilities", {})
    probs_f = r_fail.get("probabilities", {})

    # Normal should be NORMAL or at most WARN_72H (not WARN_24H/IMMINENT)
    normal_is_low = alert_n in ("NORMAL", "WARN_72H")
    detail_n = f"normal alert_class={alert_n}"
    record(eq_class, "Failure", "(b) normal -> NORMAL or WARN_72H",
           normal_is_low, detail_n)

    # Failing should be WARN_24H or IMMINENT
    fail_is_high = alert_f in ("WARN_24H", "IMMINENT")
    detail_f = f"failing alert_class={alert_f}"
    record(eq_class, "Failure", "(b) failing -> WARN_24H or IMMINENT",
           fail_is_high, detail_f)

    # Probability gap: sum of (WARN_24H + IMMINENT) for failing vs normal
    danger_norm = probs_n.get("WARN_24H", 0.0) + probs_n.get("IMMINENT", 0.0)
    danger_fail = probs_f.get("WARN_24H", 0.0) + probs_f.get("IMMINENT", 0.0)
    gap = danger_fail - danger_norm
    detail_gap = f"danger_fail={danger_fail:.3f} danger_norm={danger_norm:.3f} gap={gap:.3f}"
    record(eq_class, "Failure", "(b) prob gap (fail-danger - norm-danger) >= 0.20",
           gap >= 0.20, detail_gap)


# ---------------------------------------------------------------------------
# Anomaly checks
# ---------------------------------------------------------------------------

def check_anomaly(eq_class: str) -> None:
    from wizard.ml.anomaly_detector import get_anomaly_score

    normal = _NORMAL_READINGS[eq_class]
    failing = _FAILING_READINGS[eq_class]

    history_norm = [normal] * 32
    history_fail = [failing] * 32

    r_norm = get_anomaly_score(
        asset_id=f"test-normal-{eq_class}",
        sensor_readings=normal,
        readings_history=history_norm,
        equipment_class=eq_class,
    )
    r_fail = get_anomaly_score(
        asset_id=f"test-fail-{eq_class}",
        sensor_readings=failing,
        readings_history=history_fail,
        equipment_class=eq_class,
    )

    score_n = r_norm.get("score", 0.0)
    score_f = r_fail.get("score", 0.0)
    sev_n = r_norm.get("severity", "?")
    sev_f = r_fail.get("severity", "?")

    margin = score_f - score_n
    detail_margin = f"fail_score={score_f:.4f} norm_score={score_n:.4f} margin={margin:.4f}"
    record(eq_class, "Anomaly", "(c) failing score > normal by >= 0.10",
           margin >= 0.10, detail_margin)

    # Severity should escalate: failing >= normal in the ordering low<medium<high<critical
    sev_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    sev_n_val = sev_order.get(sev_n.lower(), -1)
    sev_f_val = sev_order.get(sev_f.lower(), -1)
    sev_escalated = sev_f_val >= sev_n_val
    detail_sev = f"norm_severity={sev_n} fail_severity={sev_f}"
    record(eq_class, "Anomaly", "(c) severity escalates (fail >= norm severity)",
           sev_escalated, detail_sev)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print("=" * 90)
    print("  ADVERSARIAL DISCRIMINATION VERIFICATION — wizard.ml")
    print("  5 equipment classes x 3 metrics = 15 core checks (+ sub-checks)")
    print("=" * 90)

    for eq_class in EQUIPMENT_CLASSES:
        print(f"\n--- {eq_class.upper()} ---")

        try:
            check_rul(eq_class)
        except Exception as exc:
            record(eq_class, "RUL", "EXCEPTION", False, str(exc))

        try:
            check_failure(eq_class)
        except Exception as exc:
            record(eq_class, "Failure", "EXCEPTION", False, str(exc))

        try:
            check_anomaly(eq_class)
        except Exception as exc:
            record(eq_class, "Anomaly", "EXCEPTION", False, str(exc))

    # -------------------------------------------------------------------------
    # Summary matrix
    # -------------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("  DISCRIMINATION MATRIX (primary 15 checks — one per class/metric)")
    print("=" * 90)
    print(f"  {'CLASS':<18s} | {'RUL (a)':<9s} | {'FAILURE (b)':<13s} | {'ANOMALY (c)':<13s}")
    print("  " + "-" * 58)

    # Primary checks for the 3x5 matrix
    # RUL primary = "failing p50 < 0.5 * normal p50"
    # Failure primary = "failing -> WARN_24H or IMMINENT"
    # Anomaly primary = "failing score > normal by >= 0.10"
    rul_primary_check    = "(a) failing p50 < 0.5 * normal p50"
    failure_primary_check = "(b) failing -> WARN_24H or IMMINENT"
    anomaly_primary_check = "(c) failing score > normal by >= 0.10"

    matrix: Dict[str, Dict[str, str]] = {c: {} for c in EQUIPMENT_CLASSES}
    for eq_class, metric, check, passed, detail in _RESULTS:
        key = f"{metric}:{check}"
        if metric == "RUL" and check == rul_primary_check:
            matrix[eq_class]["RUL"] = "PASS" if passed else "FAIL"
        elif metric == "Failure" and check == failure_primary_check:
            matrix[eq_class]["Failure"] = "PASS" if passed else "FAIL"
        elif metric == "Anomaly" and check == anomaly_primary_check:
            matrix[eq_class]["Anomaly"] = "PASS" if passed else "FAIL"

    for eq_class in EQUIPMENT_CLASSES:
        rul_r   = matrix[eq_class].get("RUL", "?")
        fail_r  = matrix[eq_class].get("Failure", "?")
        anom_r  = matrix[eq_class].get("Anomaly", "?")
        print(f"  {eq_class:<18s} | {rul_r:<9s} | {fail_r:<13s} | {anom_r:<13s}")

    # Full results summary
    total  = len(_RESULTS)
    passed = sum(1 for _, _, _, p, _ in _RESULTS if p)
    failed = total - passed

    print("\n" + "=" * 90)
    print(f"  FULL RESULTS: {passed}/{total} passed,  {failed} failed")
    print("=" * 90)

    if failed:
        print("\n  FAILING CHECKS:")
        for eq_class, metric, check, ok, detail in _RESULTS:
            if not ok:
                print(f"    FAIL  [{eq_class}][{metric}] {check}  -- {detail}")

    print("\n  OPEN ISSUES (checks that still fail discrimination):")
    open_issues = []
    for eq_class, metric, check, ok, detail in _RESULTS:
        if not ok:
            issue = f"[{eq_class}][{metric}] {check}: {detail}"
            open_issues.append(issue)
            print(f"    - {issue}")
    if not open_issues:
        print("    None — all discrimination checks pass.")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
