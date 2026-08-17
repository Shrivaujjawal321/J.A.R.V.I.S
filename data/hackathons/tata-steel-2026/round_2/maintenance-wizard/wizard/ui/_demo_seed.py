"""
wizard.ui._demo_seed
====================
Pre-seed session state with realistic demo data so every page shows content
on first load — even when the backend is offline.

Called once per session at app startup in app.py:
    from wizard.ui._demo_seed import ensure_demo_seed
    ensure_demo_seed()

Design rule (Report 18, Anti-pattern 10):
  Empty tables on first load look like the system has no data.
  Seed 5 historical alerts and 3 logbook entries at startup.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

# streamlit imported lazily inside functions so this module is importable
# outside a Streamlit runtime context (e.g., tests, smoke tests).

# ---------------------------------------------------------------------------
# Canonical equipment roster for the demo
# ---------------------------------------------------------------------------
DEMO_EQUIPMENT = [
    {"asset_id": "EAF-04", "name": "EAF-04 Electric Arc Furnace",
     "area": "Steel-Making-Bay-1", "class": "furnace",
     "criticality": "critical"},
    {"asset_id": "BF-FAN-02", "name": "BF-2 Fan A",
     "area": "BF-Area-1", "class": "fan",
     "criticality": "critical"},
    {"asset_id": "PUMP-HSM-07", "name": "HSM Descaler Pump 7",
     "area": "HSM-Bay-3", "class": "pump",
     "criticality": "high"},
    {"asset_id": "CONV-BRG-11", "name": "Conveyor Bearing Set 11",
     "area": "Rolling-Mill-1", "class": "bearing",
     "criticality": "medium"},
    {"asset_id": "HPU-CCS-03", "name": "CCS Hydraulic Power Unit 3",
     "area": "Continuous-Caster", "class": "hydraulic_unit",
     "criticality": "high"},
    {"asset_id": "CONV-HSM-15", "name": "HSM Conveyor Drive 15",
     "area": "HSM-Bay-2", "class": "conveyor",
     "criticality": "medium"},
]

# ---------------------------------------------------------------------------
# Sensor snapshot per equipment (realistic steel-plant ranges)
# ---------------------------------------------------------------------------
DEMO_SENSOR_STATE: dict[str, dict] = {
    "EAF-04": {
        "rul_days_p50": 0.46,   # ~11 hours — CRITICAL demo asset
        "rul_days_p90": 0.83,
        "rul_days_p10": 0.25,
        "anomaly_score": 0.91,
        "health_score": 12,
        "failure_probability": 0.94,
        "failure_class": "heat",
        "degradation_index": 0.92,
        "sensor_readings": {
            "temperature_c": 1847.3,
            "vibration_mm_s": 18.4,
            "pressure_bar": 2.1,
            "current_a": 38200,
            "rpm": None,
            "torque_nm": None,
        },
    },
    "BF-FAN-02": {
        "rul_days_p50": 3.2,
        "rul_days_p90": 5.1,
        "rul_days_p10": 1.8,
        "anomaly_score": 0.73,
        "health_score": 38,
        "failure_probability": 0.71,
        "failure_class": "tool_wear",
        "degradation_index": 0.65,
        "sensor_readings": {
            "temperature_c": 112.4,
            "vibration_mm_s": 9.2,
            "pressure_bar": 4.8,
            "current_a": 420,
            "rpm": 2940,
            "torque_nm": 1380,
        },
    },
    "PUMP-HSM-07": {
        "rul_days_p50": 11.4,
        "rul_days_p90": 16.8,
        "rul_days_p10": 7.2,
        "anomaly_score": 0.51,
        "health_score": 62,
        "failure_probability": 0.38,
        "failure_class": "no_failure",
        "degradation_index": 0.42,
        "sensor_readings": {
            "temperature_c": 68.2,
            "vibration_mm_s": 4.1,
            "pressure_bar": 12.7,
            "current_a": 185,
            "rpm": 1480,
            "torque_nm": 890,
        },
    },
    "CONV-BRG-11": {
        "rul_days_p50": 28.7,
        "rul_days_p90": 38.4,
        "rul_days_p10": 19.3,
        "anomaly_score": 0.28,
        "health_score": 76,
        "failure_probability": 0.12,
        "failure_class": "no_failure",
        "degradation_index": 0.22,
        "sensor_readings": {
            "temperature_c": 54.1,
            "vibration_mm_s": 2.8,
            "pressure_bar": 1.4,
            "current_a": 92,
            "rpm": 840,
            "torque_nm": 340,
        },
    },
    "HPU-CCS-03": {
        "rul_days_p50": 7.6,
        "rul_days_p90": 11.2,
        "rul_days_p10": 4.4,
        "anomaly_score": 0.62,
        "health_score": 51,
        "failure_probability": 0.54,
        "failure_class": "overstrain",
        "degradation_index": 0.55,
        "sensor_readings": {
            "temperature_c": 78.9,
            "vibration_mm_s": 6.7,
            "pressure_bar": 18.4,
            "current_a": 240,
            "rpm": None,
            "torque_nm": None,
        },
    },
    "CONV-HSM-15": {
        "rul_days_p50": 44.2,
        "rul_days_p90": 61.0,
        "rul_days_p10": 31.5,
        "anomaly_score": 0.19,
        "health_score": 88,
        "failure_probability": 0.06,
        "failure_class": "no_failure",
        "degradation_index": 0.11,
        "sensor_readings": {
            "temperature_c": 41.3,
            "vibration_mm_s": 1.4,
            "pressure_bar": 0.9,
            "current_a": 64,
            "rpm": 620,
            "torque_nm": 185,
        },
    },
}

# ---------------------------------------------------------------------------
# Demo alerts (seeded at startup — 5 historical + 1 active critical)
# ---------------------------------------------------------------------------
_now = datetime.utcnow()

DEMO_ALERTS: list[dict] = [
    {
        "alert_id": "ALERT-SEED-001",
        "asset_id": "EAF-04",
        "equipment_name": "EAF-04 Electric Arc Furnace",
        "severity": "CRITICAL",
        "alert_type": "rul_critical",
        "description": (
            "CRITICAL: RUL P50 = 11.0 h. Electrode cooling failure pattern detected. "
            "Vibration 18.4 mm/s (threshold 12.0). Immediate inspection required. "
            "Spare SKF-6310-2RS1 in stock (Jamshedpur)."
        ),
        "estimated_rul_days": 0.46,
        "recommended_action": (
            "1. Schedule emergency inspection within 4 h.\n"
            "2. Confirm spare SKF-6310-2RS1 availability at warehouse.\n"
            "3. Engage maintenance crew — SOP BF-SOP-007 §3.4."
        ),
        "triggered_at": (_now - timedelta(minutes=3)).isoformat(),
        "acknowledged": False,
        "cost_avoidance_inr": 825000.0,
    },
    {
        "alert_id": "ALERT-SEED-002",
        "asset_id": "BF-FAN-02",
        "equipment_name": "BF-2 Fan A",
        "severity": "HIGH",
        "alert_type": "sensor_anomaly",
        "description": (
            "HIGH: Anomaly score 0.73. Bearing wear pattern — vibration trending +4.2 mm/s "
            "over 72 h. RUL P50 = 3.2 days."
        ),
        "estimated_rul_days": 3.2,
        "recommended_action": "Schedule bearing inspection within 48 h. Review SOP BF-FAN-001 §2.1.",
        "triggered_at": (_now - timedelta(hours=2)).isoformat(),
        "acknowledged": False,
        "cost_avoidance_inr": 562500.0,
    },
    {
        "alert_id": "ALERT-SEED-003",
        "asset_id": "HPU-CCS-03",
        "equipment_name": "CCS Hydraulic Power Unit 3",
        "severity": "HIGH",
        "alert_type": "sensor_anomaly",
        "description": (
            "HIGH: Pressure variance +2.7 bar above baseline. Overstrain failure class "
            "probability 54%. RUL P50 = 7.6 days."
        ),
        "estimated_rul_days": 7.6,
        "recommended_action": "Inspect hydraulic seals. Replace if leakage confirmed — SOP CCS-HPU-003 §4.1.",
        "triggered_at": (_now - timedelta(hours=5)).isoformat(),
        "acknowledged": False,
        "cost_avoidance_inr": 337500.0,
    },
    # Historical (acknowledged)
    {
        "alert_id": "ALERT-SEED-004",
        "asset_id": "PUMP-HSM-07",
        "equipment_name": "HSM Descaler Pump 7",
        "severity": "MEDIUM",
        "alert_type": "threshold_breach",
        "description": "MEDIUM: Temperature 68°C sustained >4 h. Cavitation risk — check inlet strainer.",
        "estimated_rul_days": 11.4,
        "recommended_action": "Clean inlet strainer. Monitor for 24 h.",
        "triggered_at": (_now - timedelta(days=1, hours=3)).isoformat(),
        "acknowledged": True,
        "cost_avoidance_inr": 75000.0,
    },
    {
        "alert_id": "ALERT-SEED-005",
        "asset_id": "CONV-BRG-11",
        "equipment_name": "Conveyor Bearing Set 11",
        "severity": "LOW",
        "alert_type": "pattern_match",
        "description": "LOW: Vibration 2.8 mm/s — slight upward trend over 7 days. No immediate action required.",
        "estimated_rul_days": 28.7,
        "recommended_action": "Include in next scheduled PM cycle.",
        "triggered_at": (_now - timedelta(days=2)).isoformat(),
        "acknowledged": True,
        "cost_avoidance_inr": 0.0,
    },
]

# ---------------------------------------------------------------------------
# Demo logbook entries (historical MaintenanceRecords)
# ---------------------------------------------------------------------------
DEMO_LOGBOOK: list[dict] = [
    {
        "log_id": "LOG-SEED-001",
        "asset_id": "EAF-04",
        "equipment_name": "EAF-04 Electric Arc Furnace",
        "work_order_id": "WO-2026-0891",
        "maintenance_type": "predictive",
        "description": "Electrode cooling system inspection. Replaced O-ring seal on cooling manifold. Vibration reduced from 22.1 to 6.4 mm/s post-maintenance.",
        "performed_at": (_now - timedelta(days=14)).strftime("%Y-%m-%d %H:%M"),
        "technician_id": "TECH-047",
        "duration_hours": 3.5,
        "outcome": "resolved",
        "fault_codes": ["EAF-COOL-003"],
        "parts_used": ["SKF-6310-2RS1", "SEAL-014"],
    },
    {
        "log_id": "LOG-SEED-002",
        "asset_id": "PUMP-HSM-07",
        "equipment_name": "HSM Descaler Pump 7",
        "work_order_id": "WO-2026-0847",
        "maintenance_type": "preventive",
        "description": "Quarterly PM — impeller cleaned, mechanical seal inspected (serviceable), inlet strainer cleared of scale deposits.",
        "performed_at": (_now - timedelta(days=21)).strftime("%Y-%m-%d %H:%M"),
        "technician_id": "TECH-029",
        "duration_hours": 2.0,
        "outcome": "resolved",
        "fault_codes": [],
        "parts_used": [],
    },
    {
        "log_id": "LOG-SEED-003",
        "asset_id": "BF-FAN-02",
        "equipment_name": "BF-2 Fan A",
        "work_order_id": "WO-2026-0803",
        "maintenance_type": "corrective",
        "description": "Emergency bearing replacement after vibration alarm at 14.2 mm/s. NSK bearing 6312-C3 installed. Root cause: insufficient lubrication interval.",
        "performed_at": (_now - timedelta(days=28)).strftime("%Y-%m-%d %H:%M"),
        "technician_id": "TECH-011",
        "duration_hours": 6.0,
        "outcome": "resolved",
        "fault_codes": ["BRG-WEAR-001"],
        "parts_used": ["NSK-6312-C3"],
    },
]

# ---------------------------------------------------------------------------
# Demo cost events (pre-seeded for ticker)
# ---------------------------------------------------------------------------
DEMO_COST_EVENTS: list[dict] = [
    {
        "alert_id": "ALERT-SEED-004",
        "equipment": "HSM Descaler Pump 7",
        "severity": "MEDIUM",
        "prevented_hours": 1.0,
        "cost_inr": 75000.0,
        "timestamp": (_now - timedelta(days=1, hours=3)).isoformat(),
    },
]

# ---------------------------------------------------------------------------
# ensure_demo_seed() — called once per session in app.py
# ---------------------------------------------------------------------------

def ensure_demo_seed() -> None:
    """
    Populate st.session_state with demo data on first call per session.
    Subsequent calls are no-ops (idempotent via 'demo_seeded' flag).
    """
    import streamlit as st  # lazy import — safe outside Streamlit runtime

    if st.session_state.get("demo_seeded"):
        return

    # Alerts: start with seed, append real backend alerts as they arrive.
    # EAF-04 CRITICAL alert (ALERT-SEED-001) is intentionally NOT added to
    # seen_alert_ids at startup — it must fire as a fresh toast on the alert
    # stream so the 90-second wow-moment demo works.
    # All other seeded alerts are pre-seen to avoid duplicate toasts on reload.
    _wow_alert_ids = {"ALERT-SEED-001"}  # EAF-04 CRITICAL — must fire fresh
    _pre_seen = {a["alert_id"] for a in DEMO_ALERTS if a["alert_id"] not in _wow_alert_ids}
    st.session_state.setdefault("alerts", list(DEMO_ALERTS))
    st.session_state.setdefault("seen_alert_ids", _pre_seen)

    # Logbook
    st.session_state.setdefault("logbook", list(DEMO_LOGBOOK))

    # Cost ticker
    st.session_state.setdefault("cost_events", list(DEMO_COST_EVENTS))
    _initial_cost = sum(e["cost_inr"] for e in DEMO_COST_EVENTS)
    st.session_state.setdefault("total_cost_avoidance_inr", _initial_cost)
    st.session_state.setdefault("last_cost_delta_inr", 0.0)

    # Chat
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("session_id", _new_session_id())

    # Demo mode state
    st.session_state.setdefault("demo_mode_active", False)
    st.session_state.setdefault("playback_multiplier", 1)

    st.session_state["demo_seeded"] = True

    # Write cost_events.jsonl for the demo artifact log
    _persist_demo_cost_events()


def _new_session_id() -> str:
    """Generate a session ID without python-ulid dependency."""
    import uuid
    return f"session-{uuid.uuid4().hex[:12]}"


def _persist_demo_cost_events() -> None:
    """Write initial cost events to data/demo/cost_events.jsonl."""
    try:
        demo_dir = Path("data/demo")
        demo_dir.mkdir(parents=True, exist_ok=True)
        events_path = demo_dir / "cost_events.jsonl"
        if not events_path.exists():
            with open(events_path, "w") as f:
                for ev in DEMO_COST_EVENTS:
                    f.write(json.dumps(ev) + "\n")
    except Exception:
        pass  # Non-critical — demo runs without this file


def append_cost_event(
    alert_id: str,
    equipment: str,
    severity: str,
    prevented_hours: float,
) -> None:
    """
    Record a new cost-avoidance event.
    Updates session state ticker and appends to data/demo/cost_events.jsonl.
    Only fires for CRITICAL or HIGH events (per research brief).
    """
    import streamlit as st  # lazy import — safe outside Streamlit runtime

    if severity.upper() not in ("CRITICAL", "HIGH"):
        return

    cost_inr = prevented_hours * 75_000.0
    event = {
        "alert_id": alert_id,
        "equipment": equipment,
        "severity": severity,
        "prevented_hours": prevented_hours,
        "cost_inr": cost_inr,
        "timestamp": datetime.utcnow().isoformat(),
    }

    current_total = st.session_state.get("total_cost_avoidance_inr", 0.0)
    st.session_state["total_cost_avoidance_inr"] = current_total + cost_inr
    st.session_state["last_cost_delta_inr"] = cost_inr

    cost_events = st.session_state.get("cost_events", [])
    cost_events.append(event)
    st.session_state["cost_events"] = cost_events

    # Persist
    try:
        demo_dir = Path("data/demo")
        demo_dir.mkdir(parents=True, exist_ok=True)
        with open(demo_dir / "cost_events.jsonl", "a") as f:
            f.write(json.dumps(event) + "\n")
    except Exception:
        pass
