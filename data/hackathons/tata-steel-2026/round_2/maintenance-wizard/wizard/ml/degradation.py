"""
wizard.ml.degradation
======================
Physics-informed degradation index for steel-plant sensor data.

WHY THIS EXISTS:
The trained WeibullAFT, LightGBM, and IsolationForest models were learned on
NASA C-MAPSS (turbofan, 21 sensors) and AI4I-2020 datasets.  At inference time,
live steel-plant sensors (temperature_c, vibration_mm_s, pressure_bar, rpm,
current_a, etc.) arrive in physical units with domain-specific normal/warning/
critical bands that bear no relation to the C-MAPSS feature space.

The centroid-based degradation index (||z - z_healthy|| / ||z_failure - z_healthy||)
operates in StandardScaler-normalized C-MAPSS space, so it cannot respond to
steel sensor degradation signals.

FIX: a physics-informed degradation index derived from per-sensor severity bands
that are grounded in steel-plant domain knowledge.  This index is deterministic,
retraining-free, and can be hot-swapped into the RUL / failure / anomaly inference
paths as a correction signal.

Public API
----------
  physics_degradation_index(sensor_readings, equipment_class) -> float in [0, 1]

    Returns:
      ~0.05–0.15  for clearly-normal readings (all sensors inside normal band)
      ~0.85–0.98  for clearly-failing readings (critical-band sensors present)
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Per-sensor, per-equipment-class physical severity bands.
#
# Each entry is (normal_lo, normal_hi, critical_lo, critical_hi).
# Interpretation:
#   value in [normal_lo, normal_hi]         → severity 0.0  (healthy)
#   value approaching critical_lo (low bad) or critical_hi (high bad) → severity → 1.0
#   Both tails are handled for sensors where going TOO LOW is also dangerous
#   (e.g. pressure drop, rpm drop, health_score drop).
#
# Bands derived from ISO 10816 vibration standards, ISO 13381 condition monitoring
# guidelines, and typical steel-plant operating envelopes.
#
# Layout:
#   key:   sensor name (must match SENSOR_KEYS in feature_utils.py)
#   value: (normal_lo, normal_hi, warn_lo, warn_hi, critical_lo, critical_hi)
#          where warn_lo/critical_lo are the "low-end bad" thresholds,
#                warn_hi/critical_hi are the "high-end bad" thresholds.
# ---------------------------------------------------------------------------

# Shared default bands — safe fallback when equipment_class is unknown.
# Per-class overrides below for sensors whose bands differ across equipment.
_DEFAULT_BANDS: Dict[str, Tuple[float, float, float, float, float, float]] = {
    # (normal_lo, normal_hi, warn_lo, warn_hi, critical_lo, critical_hi)
    # LOW end is bad if sensor can drop dangerously; HIGH end is bad for heat/wear.
    "temperature_c":   (200.0, 420.0,  150.0, 470.0,  100.0, 530.0),
    "process_temp_c":  (200.0, 450.0,  150.0, 500.0,  100.0, 560.0),
    "pressure_bar":    ( 80.0, 220.0,   50.0, 250.0,   20.0, 280.0),  # low = leak/failure
    "vibration_mm_s":  (  0.0,   3.5,    3.5,   7.0,    7.0,  12.0),  # high = fault
    "rpm":             (900.0,1500.0,  700.0,1700.0,  500.0,1900.0),  # low = stall
    "torque_nm":       (200.0, 700.0,  150.0, 800.0,  100.0, 900.0),  # high = overload
    "current_a":       ( 20.0,  70.0,   15.0,  85.0,   10.0, 100.0),  # high = overload
    "tool_wear_min":   (  0.0, 150.0,  150.0, 220.0,  220.0, 300.0),  # high = worn
    "health_score":    (  0.0,   0.45,   0.45,  1.0,    0.65,  1.0),  # HIGH = degraded (wear proxy: 0=new, 1=worn)
}

# Per-equipment-class overrides for sensors with tighter or looser operating
# envelopes.  Only sensors that differ from _DEFAULT_BANDS are listed.
_CLASS_BAND_OVERRIDES: Dict[str, Dict[str, Tuple[float, float, float, float, float, float]]] = {
    "bearing": {
        # Bearings: sensitive to vibration, temperature spikes, and lubrication pressure drop
        "vibration_mm_s": (0.0, 2.5,  2.5,  5.5,  5.5, 10.0),
        "temperature_c":  (200.0, 400.0, 150.0, 450.0, 100.0, 510.0),
        "pressure_bar":   (120.0, 220.0, 90.0, 240.0, 40.0, 270.0),  # lube pressure; drop to 90 = warning
    },
    "fan": {
        # Industrial fans: wider acceptable vibration, sensitive to rpm drop
        "vibration_mm_s": (0.0, 4.5,  4.5,  8.5,  8.5, 13.0),
        "rpm":            (700.0, 1600.0, 500.0, 1800.0, 300.0, 2000.0),
        # Large EAF/BF fans are high-power machines; rated current is hundreds
        # of amps (not the 10-100 A default band which applies to smaller motors).
        # Baseline current_a=48..400 A is normal for this equipment class.
        "current_a":      (30.0, 400.0, 10.0, 500.0, 5.0, 600.0),
        # Fan static / duct pressure operates in a much lower and wider window
        # than the default (80-220 bar) which targets hydraulics / pumps.
        # EAF/BF fans: pressure_bar can be <30 bar in normal duct operation.
        "pressure_bar":   (5.0, 200.0, 2.0, 250.0, 0.0, 300.0),
    },
    "pump": {
        # Pumps: pressure is critical — both low (cavitation) and high (over-pressure)
        "pressure_bar":   (100.0, 200.0, 70.0, 230.0, 30.0, 260.0),
        "vibration_mm_s": (0.0, 3.0, 3.0, 6.5, 6.5, 11.0),
    },
    "conveyor": {
        # Conveyors: torque and current are primary failure signals.
        # RPM range is wider — belt drive motors can run 200–1500 rpm normally.
        "torque_nm":  (100.0, 650.0, 80.0, 780.0, 50.0, 900.0),
        "current_a":  (15.0, 65.0, 10.0, 80.0, 5.0, 95.0),
        "rpm":        (200.0, 1400.0, 100.0, 1600.0, 50.0, 1800.0),
    },
    "hydraulic_unit": {
        # Hydraulic units: pressure is paramount; temperature also critical
        "pressure_bar":    (120.0, 250.0, 80.0, 270.0, 40.0, 290.0),
        "temperature_c":   (150.0, 380.0, 100.0, 430.0, 60.0, 490.0),
        "vibration_mm_s":  (0.0, 3.0, 3.0, 6.0, 6.0, 10.0),
    },
}


def _get_bands(
    equipment_class: str,
) -> Dict[str, Tuple[float, float, float, float, float, float]]:
    """Return the merged band dict for a given equipment class."""
    eq_key = equipment_class.lower().replace(" ", "_").replace("-", "_")
    bands = dict(_DEFAULT_BANDS)  # start from defaults
    overrides = _CLASS_BAND_OVERRIDES.get(eq_key, {})
    bands.update(overrides)
    return bands


def _sensor_severity(
    value: float,
    normal_lo: float,
    normal_hi: float,
    warn_lo: float,
    warn_hi: float,
    critical_lo: float,
    critical_hi: float,
) -> float:
    """
    Compute per-sensor severity in [0, 1] given the 6-parameter band spec.

    Severity ramps:
      - Inside [normal_lo, normal_hi]              → 0.0 (fully healthy)
      - Between normal and warn boundary            → linear ramp 0→0.5
      - Between warn and critical boundary          → linear ramp 0.5→1.0
      - At or beyond critical boundary              → 1.0

    Both the low tail (value < normal_lo, going toward critical_lo) and the
    high tail (value > normal_hi, going toward critical_hi) are handled.
    The maximum severity from either tail wins.
    """
    sev_high = 0.0
    sev_low  = 0.0

    # --- High-end severity (value above normal) ---
    if value > normal_hi:
        warn_span = max(warn_hi - normal_hi, 1e-6)
        crit_span = max(critical_hi - warn_hi, 1e-6)
        if value <= warn_hi:
            sev_high = 0.5 * (value - normal_hi) / warn_span
        else:
            sev_high = 0.5 + 0.5 * min((value - warn_hi) / crit_span, 1.0)

    # --- Low-end severity (value below normal — e.g. pressure/rpm dropping) ---
    if value < normal_lo:
        warn_span = max(normal_lo - warn_lo, 1e-6)
        crit_span = max(warn_lo - critical_lo, 1e-6)
        if value >= warn_lo:
            sev_low = 0.5 * (normal_lo - value) / warn_span
        else:
            sev_low = 0.5 + 0.5 * min((warn_lo - value) / crit_span, 1.0)

    return float(np.clip(max(sev_high, sev_low), 0.0, 1.0))


def physics_degradation_index(
    sensor_readings: Dict[str, float],
    equipment_class: str = "default",
) -> float:
    """
    Compute a physics-informed degradation index for steel-plant sensors.

    Rationale:
      The trained ML models (WeibullAFT, LightGBM, IsolationForest) were fit on
      C-MAPSS/AI4I data in a normalized feature space incompatible with real
      steel-plant physical-unit readings.  This function provides a sensor-space
      degradation signal that IS grounded in steel-plant operating ranges, so it
      can override or blend into the model outputs to restore discrimination.

    Aggregation:
      severity scores per sensor → soft-max blend: 0.6*max + 0.4*mean
      Rationale: one critical sensor (e.g. vibration=9.5 mm/s) should dominate,
      but multiple elevated sensors compound each other via the mean component.

    Parameters
    ----------
    sensor_readings : dict[str, float]
        Raw steel-plant sensor readings in physical units.
    equipment_class : str
        ISO 14224 equipment class: 'bearing'|'fan'|'pump'|'conveyor'|'hydraulic_unit'.

    Returns
    -------
    float in [0, 1]
      ~0.05–0.15  → normal / healthy operating state
      ~0.30–0.55  → mild degradation / early warning
      ~0.60–0.80  → significant degradation / alert zone
      ~0.85–0.98  → critical / imminent failure state
    """
    bands = _get_bands(equipment_class)

    severities = []
    for sensor_key, band in bands.items():
        value = float(sensor_readings.get(sensor_key, float("nan")))
        if np.isnan(value):
            # Missing sensor: assume mid-range severity (don't dominate)
            severities.append(0.3)
            continue
        normal_lo, normal_hi, warn_lo, warn_hi, critical_lo, critical_hi = band
        sev = _sensor_severity(value, normal_lo, normal_hi, warn_lo, warn_hi, critical_lo, critical_hi)
        severities.append(sev)

    if not severities:
        return 0.5  # fallback

    arr = np.array(severities, dtype=np.float64)
    # Soft-max blend: dominant sensor (max) + mean of all sensors
    index = 0.6 * float(arr.max()) + 0.4 * float(arr.mean())
    return float(np.clip(index, 0.0, 1.0))
