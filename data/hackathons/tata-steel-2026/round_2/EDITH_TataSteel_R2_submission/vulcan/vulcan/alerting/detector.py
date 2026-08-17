"""VULCAN threshold detector — the deterministic core of FR7 real-time alerting.

This is the part of the alerting loop that MUST never stall: zero LLM, zero model
load, pure float comparisons against the spine's ISO/ISA thresholds. Given a
stream of sensor readings (one timestamp at a time) it emits an
:class:`AlertEvent` the moment a sensor crosses its WARNING or ALARM threshold,
and escalates to CRITICAL when an alarm is *sustained* (debounced) so a single
noisy spike does not trip a plant-stop alert.

Severity ladder (escalating):
    NORMAL  -> sensor inside its normal band
    WARNING -> sensor >= warning_threshold (spine)
    ALARM   -> sensor >= alarm_threshold   (spine)
    CRITICAL-> alarm SUSTAINED for >= `critical_hold` consecutive samples, OR the
               ground-truth dense table marks this region as a confirmed FAILURE
               (fault_label == 2). CRITICAL is the autonomous plant-protection
               trip that triggers the agentic diagnosis hand-off.

Everything here is fail-soft and side-effect-free: it never reads the network,
never raises on a bad row (a non-numeric value is simply skipped), and carries
the dataset ``source`` ref on every event for the explainability layer (FR4).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Optional

from ..tools import data_tools as T


class Severity(IntEnum):
    """Ordered severity ladder — higher int = more severe (comparable directly)."""

    NORMAL = 0
    WARNING = 1
    ALARM = 2
    CRITICAL = 3

    @property
    def label(self) -> str:
        return self.name


_FAULT_LABEL_TO_SEV = {0: Severity.NORMAL, 1: Severity.WARNING, 2: Severity.CRITICAL}


@dataclass
class AlertEvent:
    """One alert raised by the detector — fully self-describing + citable."""

    asset_id: str
    timestamp: str
    sensor: str
    value: float
    severity: Severity
    warning_threshold: Optional[float]
    alarm_threshold: Optional[float]
    unit: Optional[str]
    standard: Optional[str]
    row_index: int
    # context the engine fills in for the prioritized alert / hand-off
    scenario_id: Optional[str] = None
    fault_label: Optional[int] = None
    reason: str = ""
    source: str = ""

    @property
    def is_fire(self) -> bool:
        """An event worth surfacing (WARNING or worse)."""
        return self.severity >= Severity.WARNING

    def headline(self) -> str:
        th = (self.alarm_threshold if self.severity >= Severity.ALARM
              else self.warning_threshold)
        cmp = f">= {th}{self.unit or ''}" if th is not None else ""
        return (f"[{self.severity.label}] {self.asset_id} · {self.sensor} = "
                f"{self.value}{self.unit or ''} {cmp}".strip())

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "timestamp": self.timestamp,
            "sensor": self.sensor,
            "value": self.value,
            "severity": self.severity.label,
            "severity_rank": int(self.severity),
            "warning_threshold": self.warning_threshold,
            "alarm_threshold": self.alarm_threshold,
            "unit": self.unit,
            "standard": self.standard,
            "row_index": self.row_index,
            "scenario_id": self.scenario_id,
            "fault_label": self.fault_label,
            "reason": self.reason,
            "source": self.source,
        }


@dataclass
class SensorState:
    """Per-sensor running state for debounced escalation (no history buffer)."""

    tag: str
    warning_threshold: Optional[float]
    alarm_threshold: Optional[float]
    unit: Optional[str] = None
    standard: Optional[str] = None
    alarm_streak: int = 0          # consecutive samples at/over alarm
    last_severity: Severity = Severity.NORMAL

    def classify(self, value: float) -> Severity:
        """Instantaneous severity of one reading against the spine thresholds."""
        if self.alarm_threshold is not None and value >= self.alarm_threshold:
            return Severity.ALARM
        if self.warning_threshold is not None and value >= self.warning_threshold:
            return Severity.WARNING
        return Severity.NORMAL


class ThresholdMonitor:
    """Stateful, per-asset threshold detector. Deterministic + LLM-free.

    Construct once for an asset (loads its spine thresholds), then feed it one
    reading-row at a time via :meth:`feed`. It returns the single highest-severity
    :class:`AlertEvent` for that row (or ``None`` if everything is normal), and
    internally tracks alarm streaks so sustained alarms escalate to CRITICAL.

    `critical_hold` = how many consecutive at/over-alarm samples promote an ALARM
    to CRITICAL (debounce against single-sample spikes). `respect_fault_label`
    (default True) lets a ground-truth ``fault_label == 2`` row fire CRITICAL
    immediately — this is the dataset's own confirmation that the asset is in a
    real failure, so the demo CRITICAL fires at the true failure onset.
    """

    def __init__(
        self,
        asset_id: str,
        *,
        critical_hold: int = 3,
        respect_fault_label: bool = True,
    ) -> None:
        self.asset_id_query = asset_id
        self.critical_hold = max(1, int(critical_hold))
        self.respect_fault_label = respect_fault_label

        th = T.get_thresholds(asset_id)
        self.asset_id = th.get("asset_id", asset_id)
        self.equipment_class = th.get("equipment_class")
        self.source = th.get("source", "SPEC/ground_truth_spine.json")
        self.states: dict[str, SensorState] = {}
        for s in th.get("sensors", []):
            self.states[s["tag"]] = SensorState(
                tag=s["tag"],
                warning_threshold=s.get("warning_threshold"),
                alarm_threshold=s.get("alarm_threshold"),
                unit=s.get("unit"),
                standard=s.get("standard"),
            )
        # remember which scenario maps to which sensor, for the hand-off context
        self._sensor_scenario = self._build_sensor_scenario_map()

    # ------------------------------------------------------------------
    def _build_sensor_scenario_map(self) -> dict[str, str]:
        """Map a sensor tag -> the failure scenario whose signature it dominates.

        Pure spine read. Used so a fired alert can name the scenario the agentic
        core should diagnose (e.g. PRES.OSC surge -> SCN-041)."""
        out: dict[str, str] = {}
        scns = T.get_scenarios_for_asset(self.asset_id).get("scenarios", [])
        for c in scns:
            detail = T.get_scenario(c["scenario_id"])
            sig = detail.get("sensor_signature", {}) or {}
            for tag in sig.keys():
                # prefer the first FAILURE scenario that lists this sensor
                if tag not in out or (detail.get("label") == "FAILURE"):
                    out[tag] = c["scenario_id"]
        return out

    def scenario_for_sensor(self, sensor: str) -> Optional[str]:
        return self._sensor_scenario.get(sensor)

    # ------------------------------------------------------------------
    def feed(self, row: dict[str, Any], *, row_index: int = -1) -> Optional[AlertEvent]:
        """Process one reading row; return the worst alert event, or None.

        `row` is a dict of sensor_tag -> value (the dense-table columns). Extra
        meta columns (timestamp / asset_id / fault_label / equipment_class) are
        read for context but never treated as sensors.
        """
        ts = str(row.get("timestamp", ""))
        fault_label = _safe_int(row.get("fault_label"))

        worst: Optional[AlertEvent] = None
        for tag, st in self.states.items():
            if tag not in row:
                continue
            val = _safe_float(row.get(tag))
            if val is None:
                continue
            inst = st.classify(val)

            # debounced escalation to CRITICAL on sustained alarm
            if inst >= Severity.ALARM:
                st.alarm_streak += 1
            else:
                st.alarm_streak = 0

            sev = inst
            reason = ""
            if inst >= Severity.ALARM and st.alarm_streak >= self.critical_hold:
                sev = Severity.CRITICAL
                reason = (f"alarm sustained {st.alarm_streak} consecutive samples "
                          f"(>= {st.alarm_threshold}{st.unit or ''})")
            elif inst == Severity.ALARM:
                reason = (f"crossed ALARM threshold "
                          f"({st.alarm_threshold}{st.unit or ''})")
            elif inst == Severity.WARNING:
                reason = (f"crossed WARNING threshold "
                          f"({st.warning_threshold}{st.unit or ''})")

            # ground-truth failure confirmation escalates immediately (demo realism)
            if self.respect_fault_label and fault_label == 2 and inst >= Severity.ALARM:
                if sev < Severity.CRITICAL:
                    sev = Severity.CRITICAL
                    reason = (reason + "; " if reason else "") + \
                        "ground-truth fault_label=FAILURE confirmed"

            st.last_severity = sev
            if sev == Severity.NORMAL:
                continue

            ev = AlertEvent(
                asset_id=self.asset_id,
                timestamp=ts,
                sensor=tag,
                value=round(val, 4),
                severity=sev,
                warning_threshold=st.warning_threshold,
                alarm_threshold=st.alarm_threshold,
                unit=st.unit,
                standard=st.standard,
                row_index=row_index,
                scenario_id=self.scenario_for_sensor(tag),
                fault_label=fault_label,
                reason=reason,
                source=f"condition_monitoring/by_equipment (asset {self.asset_id})",
            )
            if worst is None or ev.severity > worst.severity:
                worst = ev
        return worst


# ---------------------------------------------------------------------------
def _safe_float(v: Any) -> Optional[float]:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _safe_int(v: Any) -> Optional[int]:
    f = _safe_float(v)
    return int(f) if f is not None else None
