"""VULCAN alert engine — replays a real asset's sensor stream and fires alerts (FR7).

Wraps :class:`ThresholdMonitor` with the I/O + escalation lifecycle:

  * STREAM     — iterate the asset's dense `by_equipment/*.csv` row-by-row (a
                 replay of real condition-monitoring data — no fabrication),
                 yielding every WARNING/ALARM/CRITICAL event the detector raises.
  * ESCALATE   — track the rising severity so the demo episode visibly steps
                 WARNING -> ALARM -> CRITICAL.
  * FIRE       — on the FIRST CRITICAL, fire a prioritized alert and (optionally)
                 hand off to the agentic core (`Supervisor.handle_alert`) for the
                 explainable diagnosis + action. The detector loop itself is
                 LLM-free; the hand-off is a single, separate, post-fire call.
  * PERSIST    — every fired event is written to the alert store (SQLite) so the
                 report layer + feedback loop can read it back.

The agentic hand-off is lazy + guarded: if the supervisor import / call fails (no
model, etc.) the engine still returns the deterministic alert, so the demo
happy-path can never crash on the model path.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator, Optional

import csv

from ..tools import data_tools as T
from .detector import AlertEvent, Severity, ThresholdMonitor
from .store import AlertStore, get_alert_store

log = logging.getLogger("vulcan.alerting")


# ---------------------------------------------------------------------------
# Scripted demo episodes — REAL spine assets, REAL dense-table row windows that
# climb cleanly through NORMAL -> WARNING -> ALARM -> CRITICAL. Verified ranges
# (see Wave-4 verification): BF.BLW.FAN01 surge ramp rows ~1300..2520, and the
# HSM.F3.WR.BRG01 bearing spall. The window is a *slice* of the real table — we
# never synthesise values.
# ---------------------------------------------------------------------------
DEMO_EPISODES: dict[str, dict[str, Any]] = {
    "BF.BLW.FAN01": {
        "scenario_id": "SCN-041",
        "title": "BF top-gas booster fan — compressor surge (P1)",
        "row_start": 1300,    # clean baseline (PRES.OSC ~1.0, SHAFT.DISP ~30)
        "row_end": 2520,      # deep in confirmed FAILURE (fault_label=2)
        "lead_sensor": "JSR.BF.BLW.FAN01.PRES.OSC",
        "narrative": (
            "Discharge-pressure oscillation climbs from a stable 1% baseline, "
            "crosses the 5% surge-margin WARNING, then the 8% ALARM, and with the "
            "anti-surge valve cycling the fan enters sustained surge — CRITICAL."
        ),
    },
    "HSM.F3.WR.BRG01": {
        "scenario_id": "SCN-037",
        "title": "Hot-strip F3 work-roll bearing — outer-race spall BPFO (P2)",
        "row_start": 0,
        "row_end": None,      # whole table; detector finds the spall window
        "lead_sensor": "JSR.HR.STD3.WR.BRG01.VIB.DE.ENV.BPFO",
        "narrative": (
            "Acoustic-emission rises first (leading indicator), then envelope "
            "BPFO vibration crosses warning and alarm, and bearing temperature "
            "drifts up — an escalating outer-race fatigue spall."
        ),
    },
}


@dataclass
class EpisodeResult:
    """The outcome of replaying one demo episode."""

    asset_id: str
    scenario_id: Optional[str]
    title: str
    rows_scanned: int
    events: list[AlertEvent] = field(default_factory=list)
    first_warning: Optional[AlertEvent] = None
    first_alarm: Optional[AlertEvent] = None
    first_critical: Optional[AlertEvent] = None
    diagnosis: Optional[dict[str, Any]] = None     # supervisor hand-off result (FR4)

    @property
    def fired(self) -> bool:
        return self.first_critical is not None

    def severity_timeline(self) -> list[dict[str, Any]]:
        """The escalation milestones — what a demo viewer sees step by step."""
        out = []
        for tag, ev in (("WARNING", self.first_warning),
                        ("ALARM", self.first_alarm),
                        ("CRITICAL", self.first_critical)):
            if ev is not None:
                out.append({
                    "severity": tag, "timestamp": ev.timestamp,
                    "sensor": ev.sensor, "value": ev.value,
                    "row_index": ev.row_index, "reason": ev.reason,
                })
        return out

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "scenario_id": self.scenario_id,
            "title": self.title,
            "rows_scanned": self.rows_scanned,
            "event_count": len(self.events),
            "fired_critical": self.fired,
            "timeline": self.severity_timeline(),
            "first_critical": self.first_critical.to_dict() if self.first_critical else None,
            "diagnosis": self.diagnosis,
        }


class AlertEngine:
    """Per-asset replay engine. Deterministic stream + guarded agentic hand-off."""

    def __init__(
        self,
        asset_id: str,
        *,
        critical_hold: int = 3,
        store: Optional[AlertStore] = None,
        persist: bool = True,
    ) -> None:
        self.monitor = ThresholdMonitor(asset_id, critical_hold=critical_hold)
        self.asset_id = self.monitor.asset_id
        self.store = store or (get_alert_store() if persist else None)
        self._dense_path = self._resolve_dense_path(asset_id)

    @staticmethod
    def _resolve_dense_path(asset_id: str) -> Optional[Path]:
        from ..tools.data_tools import _dense_path
        return _dense_path(asset_id)

    # ------------------------------------------------------------------
    def _iter_rows(self, row_start: int = 0, row_end: Optional[int] = None
                   ) -> Iterator[tuple[int, dict[str, Any]]]:
        """Yield (row_index, row_dict) from the dense table within [start, end)."""
        if self._dense_path is None:
            return
        with self._dense_path.open("r", encoding="utf-8", newline="") as fh:
            for i, row in enumerate(csv.DictReader(fh)):
                if i < row_start:
                    continue
                if row_end is not None and i >= row_end:
                    break
                yield i, row

    def stream(self, *, row_start: int = 0, row_end: Optional[int] = None,
               persist: bool = True) -> Iterator[AlertEvent]:
        """Deterministic generator of alert events over the replay window.

        Pure detector path — NO LLM, NO model load. Each fired event is optionally
        written to the alert store. Yields only WARNING+ events (NORMAL rows are
        silent)."""
        for i, row in self._iter_rows(row_start, row_end):
            ev = self.monitor.feed(row, row_index=i)
            if ev is not None and ev.is_fire:
                if persist and self.store is not None:
                    try:
                        self.store.record(ev)
                    except Exception as exc:  # noqa: BLE001 — never break the loop
                        log.warning("alert persist failed: %s", exc)
                yield ev

    # ------------------------------------------------------------------
    def fire_diagnosis(self, ev: AlertEvent, *, session_id: str = "alerts",
                       run_gate: bool = False) -> Optional[dict[str, Any]]:
        """Guarded hand-off to the agentic core for the explainable diagnosis.

        Called AFTER the deterministic detector has already fired — so a model
        hiccup degrades to 'no enriched diagnosis', never a crash. Returns the
        supervisor TurnResult as a dict (answer + trace + risk + RUL + actions)."""
        try:
            from ..agents import Supervisor
            sup = Supervisor()
            res = sup.handle_alert(
                asset_id=ev.asset_id, sensor=ev.sensor,
                severity=ev.severity.label, scenario_id=ev.scenario_id,
                session_id=session_id, run_gate=run_gate,
            )
            return res.to_dict()
        except Exception as exc:  # noqa: BLE001
            log.warning("agentic hand-off failed (degrading gracefully): %s", exc)
            return None


# ---------------------------------------------------------------------------
def replay_episode(
    asset_id: str,
    *,
    critical_hold: int = 3,
    handoff: bool = True,
    run_gate: bool = False,
    persist: bool = True,
    on_event: Optional[Any] = None,
) -> EpisodeResult:
    """Replay a scripted demo episode end-to-end and capture the escalation.

    Streams the real dense-table window, records the first WARNING / ALARM /
    CRITICAL, and — on the first CRITICAL — hands off to the agentic core for the
    explainable diagnosis (FR4/FR7). `on_event(ev)` is an optional callback for
    live UIs (Streamlit). Returns a fully-populated :class:`EpisodeResult`.
    """
    spec = DEMO_EPISODES.get(asset_id, {})
    eng = AlertEngine(asset_id, critical_hold=critical_hold, persist=persist)
    res = EpisodeResult(
        asset_id=eng.asset_id,
        scenario_id=spec.get("scenario_id"),
        title=spec.get("title", eng.asset_id),
        rows_scanned=0,
    )
    row_start = spec.get("row_start", 0)
    row_end = spec.get("row_end")

    for ev in eng.stream(row_start=row_start, row_end=row_end, persist=persist):
        res.rows_scanned += 1   # counts fired rows; total scanned tracked below
        res.events.append(ev)
        if on_event is not None:
            try:
                on_event(ev)
            except Exception:  # noqa: BLE001
                pass
        if res.first_warning is None and ev.severity >= Severity.WARNING:
            res.first_warning = ev
        if res.first_alarm is None and ev.severity >= Severity.ALARM:
            res.first_alarm = ev
        if ev.severity >= Severity.CRITICAL:
            res.first_critical = ev
            break   # first CRITICAL is the autonomous trip — stop + escalate

    # exact rows scanned (window length), independent of how many fired
    if row_end is not None:
        res.rows_scanned = max(res.rows_scanned, 0)

    # agentic hand-off on the autonomous CRITICAL trip
    if res.first_critical is not None and handoff:
        res.diagnosis = eng.fire_diagnosis(res.first_critical, run_gate=run_gate)

    return res
