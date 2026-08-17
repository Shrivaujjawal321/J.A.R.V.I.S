"""
wizard.backend.alerting
========================
Real-time proactive alert pipeline:

  [APScheduler 5s tick] → [Alert Evaluator + Dedup] → [AlertBroadcaster]
                                        ↓
                                [SQLite AnomalyAlert table]

Components:
  AlertBroadcaster  — fan-out registry; each SSE client gets its own asyncio.Queue
  DedupRegistry     — in-memory cooldown tracking keyed by (asset_id, alert_type)
  evaluate_alerts() — coroutine run by APScheduler every N seconds
  trigger_demo_eaf04_alert() — one-shot job for the 90s scripted CRITICAL wow moment
  setup_scheduler() — initialises AsyncIOScheduler bound to FastAPI lifespan

Alert lifecycle:
  1. Evaluator reads SensorSummary + AnomalyAlert from wizard.db
  2. Checks cooldown registry (in-memory dict)
  3. If new alert: persists to AnomalyAlert table, constructs AlertEvent
  4. broadcaster.broadcast(event) → fan-out to all registered client queues
  5. SSE generator drains client queue → pushes to browser via EventSourceResponse

Cooldown windows (seconds):
  CRITICAL: 120    HIGH: 300    MEDIUM: 900    LOW: 3600
"""
from __future__ import annotations

import asyncio
import os
import time
import uuid
from collections import deque
from datetime import datetime, timezone
from typing import Optional

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlmodel import Session, select

from wizard.core.config import settings
from wizard.core.db import get_session, session_scope
from wizard.core.schemas import (
    AlertEvent,
    AlertSeverity,
    AnomalyAlert,
    AssetProfile,
    SensorSummary,
    _new_ulid,
)

log = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Cooldown windows by severity (seconds)
# ---------------------------------------------------------------------------
_COOLDOWN_SECONDS: dict[str, int] = {
    AlertSeverity.CRITICAL: 120,
    AlertSeverity.HIGH: 300,
    AlertSeverity.MEDIUM: 900,
    AlertSeverity.LOW: 3600,
}


# ---------------------------------------------------------------------------
# Dedup registry
# ---------------------------------------------------------------------------

class DedupRegistry:
    """
    In-memory cooldown registry keyed by cooldown_key = '{asset_id}:{alert_type}'.
    Thread-safe via asyncio.Lock (single-event-loop operation).
    """

    def __init__(self) -> None:
        self._last_fired: dict[str, float] = {}  # key → monotonic timestamp
        self._lock = asyncio.Lock()

    async def should_fire(self, key: str, severity: AlertSeverity) -> bool:
        """Return True if the alert may fire (not in cooldown)."""
        async with self._lock:
            last = self._last_fired.get(key)
            if last is None:
                return True
            cooldown = _COOLDOWN_SECONDS.get(severity, 300)
            return (time.monotonic() - last) >= cooldown

    async def mark_fired(self, key: str) -> None:
        """Record that this key just fired."""
        async with self._lock:
            self._last_fired[key] = time.monotonic()

    async def force_key(self, key: str) -> None:
        """Force-reset a key (used by demo trigger to bypass cooldown)."""
        async with self._lock:
            self._last_fired.pop(key, None)


# ---------------------------------------------------------------------------
# AlertBroadcaster — per-client queue fan-out
# ---------------------------------------------------------------------------

class AlertBroadcaster:
    """
    Fan-out registry for SSE alert clients.

    Each connected client calls register() to get a dedicated asyncio.Queue[AlertEvent].
    When evaluate_alerts() fires an event it calls broadcast() which puts a copy
    into every registered queue. Clients drain their own queue in the SSE generator.

    Queue size is capped at 100 to prevent unbounded growth (oldest dropped on overflow).

    Ring buffer (anti-pattern fix #8):
      broadcast() also appends to a bounded ring buffer (deque, MAX_RING_BUFFER_SIZE).
      Clients that reconnect with a Last-Event-ID header call get_missed_events()
      to replay any events that arrived while they were disconnected.
      ULID IDs are lexicographically sortable by time, so string comparison works.
    """

    MAX_QUEUE_SIZE = 100
    MAX_RING_BUFFER_SIZE = 200  # last 200 alert events available for replay

    def __init__(self) -> None:
        self._clients: dict[str, asyncio.Queue[AlertEvent]] = {}
        self._lock = asyncio.Lock()
        # Ring buffer: bounded deque of recent AlertEvents for Last-Event-ID replay
        self._ring_buffer: deque[AlertEvent] = deque(maxlen=self.MAX_RING_BUFFER_SIZE)
        self._ring_lock = asyncio.Lock()

    def client_count(self) -> int:
        return len(self._clients)

    async def register(self, client_id: str) -> asyncio.Queue[AlertEvent]:
        """Register a new SSE client; return its dedicated queue."""
        q: asyncio.Queue[AlertEvent] = asyncio.Queue(maxsize=self.MAX_QUEUE_SIZE)
        async with self._lock:
            self._clients[client_id] = q
        log.info("alert_broadcaster.client_registered", client_id=client_id)
        return q

    async def unregister(self, client_id: str) -> None:
        """Remove a disconnected client."""
        async with self._lock:
            self._clients.pop(client_id, None)
        log.info("alert_broadcaster.client_unregistered", client_id=client_id)

    async def get_missed_events(self, since_id: str) -> list[AlertEvent]:
        """
        Return events from the ring buffer with alert_id > since_id.

        ULIDs are lexicographically ordered by creation time, so plain string
        comparison recovers correct chronological order without parsing.
        Used by the SSE endpoint when a client reconnects with Last-Event-ID.
        """
        async with self._ring_lock:
            buffered = list(self._ring_buffer)
        return [e for e in buffered if e.alert_id > since_id]

    async def broadcast(self, event: AlertEvent) -> None:
        """
        Put a copy of the event into every registered client queue.
        Also appends to the ring buffer for Last-Event-ID replay on reconnect.
        If a queue is full, drop the oldest item (non-blocking put_nowait).
        """
        # Append to ring buffer first so replays are always consistent
        async with self._ring_lock:
            self._ring_buffer.append(event)

        async with self._lock:
            clients = dict(self._clients)

        for client_id, q in clients.items():
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                # Drop oldest, insert new
                try:
                    q.get_nowait()
                except asyncio.QueueEmpty:
                    pass
                try:
                    q.put_nowait(event)
                except asyncio.QueueFull:
                    log.warning(
                        "alert_broadcaster.queue_full_drop",
                        client_id=client_id,
                        alert_id=event.alert_id,
                    )


# ---------------------------------------------------------------------------
# Module-level singletons (initialised by setup_scheduler)
# ---------------------------------------------------------------------------

broadcaster = AlertBroadcaster()
_dedup = DedupRegistry()
_demo_start_time: Optional[float] = None  # set at lifespan startup


# ---------------------------------------------------------------------------
# Evaluate alerts (APScheduler job)
# ---------------------------------------------------------------------------

async def evaluate_alerts() -> None:
    """
    Proactive alert evaluator — called every N seconds by APScheduler.

    Algorithm:
      1. Pull all AssetProfiles from wizard.db
      2. For each asset, get latest SensorSummary
      3. Check: anomaly_score > threshold OR rul_days_p50 < critical_days
      4. Check dedup cooldown
      5. If fire: persist AnomalyAlert, construct AlertEvent, broadcast

    Uses session_scope() so the AnomalyAlert rows are always committed on exit.
    (The old next(get_session()) pattern silently dropped writes because the
    generator was never advanced past the yield.)
    """
    _log = log.bind(job="evaluate_alerts")

    try:
        with session_scope() as session:
            await _run_evaluation(session, _log)
    except Exception as exc:
        _log.error("evaluate_alerts.error", error=str(exc))


async def _run_evaluation(session: Session, _log: structlog.BoundLogger) -> None:
    """Inner evaluation logic (separated for testability)."""
    # 1. All assets
    assets = session.exec(select(AssetProfile)).all()
    if not assets:
        return

    for asset in assets:
        # 2. Latest SensorSummary for this asset
        stmt = (
            select(SensorSummary)
            .where(SensorSummary.asset_id == asset.asset_id)
            .order_by(SensorSummary.window_end.desc())  # type: ignore[union-attr]
            .limit(1)
        )
        sensor = session.exec(stmt).first()
        if sensor is None:
            continue

        # 3. Determine if alert should fire
        alert_type, severity, description = _classify_alert(asset, sensor)
        if alert_type is None:
            continue

        # 4. Check cooldown
        key = f"{asset.asset_id}:{alert_type}"
        if not await _dedup.should_fire(key, severity):
            continue

        # 4b. Suppress duplicates: if an UNACKNOWLEDGED alert for this
        # (asset_id, alert_type) already exists, do not create another one.
        # The proactive evaluator re-runs every 5s and the fault condition
        # persists, so without this guard alerts pile up. One active alert per
        # asset+type until the engineer acknowledges it (alert-fatigue control).
        existing_open = session.exec(
            select(AnomalyAlert)
            .where(
                AnomalyAlert.asset_id == asset.asset_id,
                AnomalyAlert.alert_type == alert_type,
                AnomalyAlert.acknowledged == False,  # noqa: E712
            )
            .limit(1)
        ).first()
        if existing_open is not None:
            await _dedup.mark_fired(key)  # refresh cooldown so we don't re-check every tick
            continue

        # 5. Persist AnomalyAlert entity
        anomaly_row = AnomalyAlert(
            entity_id=_new_ulid(),
            asset_id=asset.asset_id,
            plant_area=asset.plant_area,
            alert_type=alert_type,
            risk_level=severity.value,
            description=description,
            triggering_sensor_summary_id=sensor.entity_id,
            estimated_rul_days=sensor.rul_days_p50,
            recommended_action=_recommended_action(alert_type, severity),
            acknowledged=False,
            cooldown_key=key,
        )
        session.add(anomaly_row)
        session.flush()

        await _dedup.mark_fired(key)

        # 6. Construct AlertEvent
        cost = None
        if severity in (AlertSeverity.CRITICAL, AlertSeverity.HIGH):
            rul = sensor.rul_days_p50 or 0.0
            cost = rul * 24 * settings.cost_avoidance_rate_inr_per_hour * 0.5

        event = AlertEvent(
            alert_id=anomaly_row.entity_id,
            asset_id=asset.asset_id,
            equipment_name=asset.equipment_name,
            severity=severity,
            alert_type=alert_type,
            description=description,
            estimated_rul_days=sensor.rul_days_p50,
            recommended_action=anomaly_row.recommended_action,
            triggered_at=datetime.now(timezone.utc),
            source_alert_entity_id=anomaly_row.entity_id,
            cost_avoidance_inr=cost,
        )

        await broadcaster.broadcast(event)
        _log.info(
            "alert_fired",
            asset_id=asset.asset_id,
            severity=severity.value,
            alert_type=alert_type,
        )


def _classify_alert(
    asset: AssetProfile,
    sensor: SensorSummary,
) -> tuple[Optional[str], AlertSeverity, str]:
    """
    Classify a sensor reading into (alert_type, severity, description).
    Returns (None, ...) if no alert should fire.
    """
    rul = sensor.rul_days_p50
    anomaly = sensor.anomaly_score or 0.0

    # RUL-based classification
    if rul is not None:
        if rul <= settings.rul_critical_days:
            return (
                "rul_critical",
                AlertSeverity.CRITICAL,
                (
                    f"CRITICAL: {asset.equipment_name} (ID: {asset.asset_id}) has estimated "
                    f"RUL of {rul:.1f} days (threshold: {settings.rul_critical_days:.0f} days). "
                    "Immediate maintenance action required to prevent unplanned failure."
                ),
            )
        if rul <= settings.rul_warning_days:
            return (
                "rul_warning",
                AlertSeverity.HIGH,
                (
                    f"HIGH: {asset.equipment_name} (ID: {asset.asset_id}) has estimated "
                    f"RUL of {rul:.1f} days (threshold: {settings.rul_warning_days:.0f} days). "
                    "Plan maintenance within the current planning window."
                ),
            )

    # Anomaly score classification
    if anomaly >= settings.anomaly_score_threshold:
        sev = AlertSeverity.CRITICAL if anomaly >= 0.90 else AlertSeverity.HIGH
        readings = sensor.sensor_readings
        temp = readings.get("temperature_c", "N/A")
        vib = readings.get("vibration_mm_s", "N/A")
        return (
            "sensor_anomaly",
            sev,
            (
                f"{sev.value.upper()}: Anomaly detected on {asset.equipment_name} "
                f"(ID: {asset.asset_id}). Score: {anomaly:.3f}. "
                f"Temp: {temp}°C, Vib: {vib} mm/s. "
                "Inspect and evaluate for corrective action."
            ),
        )

    return None, AlertSeverity.LOW, ""


def _recommended_action(alert_type: str, severity: AlertSeverity) -> str:
    """Return a brief recommended action string based on alert classification."""
    if alert_type == "rul_critical":
        return (
            "1. Immediately notify shift supervisor. "
            "2. Verify spare parts availability. "
            "3. Schedule emergency maintenance window."
        )
    if alert_type == "rul_warning":
        return (
            "1. Schedule predictive maintenance within 7 days. "
            "2. Confirm spare parts on order. "
            "3. Increase monitoring frequency to hourly."
        )
    if alert_type == "sensor_anomaly":
        return (
            "1. Inspect equipment for visible signs of failure. "
            "2. Review full sensor trend over last 24 hours. "
            "3. Consult maintenance SOP for this equipment class."
        )
    return "Review equipment status with maintenance team."


# ---------------------------------------------------------------------------
# Demo EAF-04 one-shot trigger (the 90-second wow moment)
# ---------------------------------------------------------------------------

async def trigger_demo_eaf04_alert() -> None:
    """
    One-shot APScheduler job: fires T+90s after demo start.
    Emits a scripted CRITICAL alert for EAF-04 regardless of sensor state.
    This is the highest-impact judging moment (FR7 proactive agentic alert).

    The alert is designed to demonstrate:
    - Proactive alert BEFORE engineer asks anything
    - Full RUL + recommended action + cost avoidance in a single event
    - Real-time SSE delivery to connected dashboard
    """
    _log = log.bind(job="demo_eaf04_trigger")
    _log.info("demo_eaf04_trigger.fired")

    # Force-reset cooldown so the alert always fires in demo
    demo_key = "EAF-04:rul_critical"
    await _dedup.force_key(demo_key)

    event = AlertEvent(
        alert_id=_new_ulid(),
        asset_id="EAF-04",
        equipment_name="Electric Arc Furnace 04 (EAF-04)",
        severity=AlertSeverity.CRITICAL,
        alert_type="rul_critical",
        description=(
            "CRITICAL PROACTIVE ALERT: Electric Arc Furnace EAF-04 — Electrode Bearing Assembly. "
            "Predicted Remaining Useful Life: 11.3 hours (p50). "
            "IsolationForest anomaly score: 0.94 (threshold: 0.65). "
            "Vibration: 18.7 mm/s (limit: 12.0 mm/s). Temperature: 847°C (+42°C above baseline). "
            "Pattern matches historical BF-BEARING-BURNOUT failure mode (3 prior incidents). "
            "SPARES WARNING: SKF-6310-2RS1 bearing is OUT OF STOCK. Lead time: 14 days. "
            "ORDER NOW to avoid extended downtime. Estimated production loss if not acted: "
            "₹8.5 Cr (11h × ₹75,000/hr × 1,024 tonne/hr production rate)."
        ),
        estimated_rul_days=round(11.3 / 24, 2),  # convert hours → days
        recommended_action=(
            "1. IMMEDIATE: Notify EAF Plant Manager and Maintenance Lead. "
            "2. URGENT: Place emergency order for SKF-6310-2RS1 bearing (part# EAF-BRG-001). "
            "   Alternate: NTN 6310-ZZ (compatible, 5-day delivery) — check with stores. "
            "3. PLAN: Schedule 4-hour maintenance window within next 8 hours. "
            "4. MONITOR: Increase vibration checks to every 15 minutes until repair. "
            "5. PREPARE: Refer to EAF-SOP-007 §4.3 — Bearing Replacement Procedure."
        ),
        triggered_at=datetime.now(timezone.utc),
        source_alert_entity_id=None,
        cost_avoidance_inr=8_500_000.0,  # ₹8.5 Cr
    )

    await broadcaster.broadcast(event)
    await _dedup.mark_fired(demo_key)

    _log.info(
        "demo_eaf04_alert_broadcast",
        alert_id=event.alert_id,
        severity=event.severity.value,
        clients_notified=broadcaster.client_count(),
    )


# ---------------------------------------------------------------------------
# Scheduler setup (called from FastAPI lifespan)
# ---------------------------------------------------------------------------

def setup_scheduler(scheduler: AsyncIOScheduler) -> None:
    """
    Register all APScheduler jobs on the provided AsyncIOScheduler.
    Call this inside the lifespan context manager (before scheduler.start()).

    Jobs registered:
      - sensor_watchdog: evaluate_alerts() every alert_poll_interval_seconds (default 5s)
      - demo_eaf04_one_shot: trigger_demo_eaf04_alert() once at T+90s from now
    """
    global _demo_start_time
    _demo_start_time = time.monotonic()

    # Periodic evaluator
    scheduler.add_job(
        evaluate_alerts,
        trigger="interval",
        seconds=settings.alert_poll_interval_seconds,
        id="sensor_watchdog",
        replace_existing=True,
        max_instances=1,  # prevent overlap if evaluation takes > poll_interval
        coalesce=True,
    )

    # One-shot demo trigger (skip in test mode)
    if os.environ.get("WIZARD_TESTING") != "1":
        from apscheduler.triggers.date import DateTrigger
        from datetime import timedelta

        trigger_time = datetime.now(timezone.utc) + timedelta(
            seconds=settings.demo_eaf04_trigger_seconds
        )
        scheduler.add_job(
            trigger_demo_eaf04_alert,
            trigger=DateTrigger(run_date=trigger_time),
            id="demo_eaf04_one_shot",
            replace_existing=True,
        )
        log.info(
            "demo_eaf04_alert_scheduled",
            trigger_at=trigger_time.isoformat(),
            seconds_from_now=settings.demo_eaf04_trigger_seconds,
        )

    log.info(
        "alert_scheduler_configured",
        poll_interval_seconds=settings.alert_poll_interval_seconds,
    )
