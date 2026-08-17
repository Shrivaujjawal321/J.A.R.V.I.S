"""
wizard.backend.demo
====================
Demo sensor playback router — the 90-second WOW-MOMENT for live judging demos.

Endpoints:
  POST /v1/demo/start        — begins degrading sensor playback for EAF-04 into the DB
                               at 15-second intervals. APScheduler proactive evaluator
                               detects the RUL + anomaly threshold breach and emits a
                               CRITICAL AlertEvent within ~60-65 seconds.
  POST /v1/demo/inject_fault — deterministic backstop: immediately writes an EAF-04
                               CRITICAL AnomalyAlert to wizard.db AND broadcasts via
                               SSE. Use this when you don't want to wait 60s or as a
                               failsafe if the playback task doesn't fire on time.
                               GET /v1/alerts always shows the alert after this.
  POST /v1/demo/reset        — stops playback, clears EAF-04 dedup cooldowns so the
                               demo can be rerun cleanly from the same process.

Design:
  - inject_fault is the ONLY endpoint you NEED for the wow moment. It is completely
    deterministic (no timing dependency) and survives APScheduler restarts.
  - start + reset enable the "natural degradation" narrative for longer demos.
  - No touches to ml/rag/agents/ui per the task contract.
  - Uses session_scope() (sync, idiomatic) inside async handlers — safe for SQLite
    because operations complete in < 1 ms (local disk, no network).
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional

import structlog
from fastapi import APIRouter
from pydantic import BaseModel

from wizard.backend.alerting import _dedup, broadcaster, trigger_demo_eaf04_alert
from wizard.core.db import session_scope
from wizard.core.schemas import (
    AnomalyAlert,
    AssetProfile,
    SensorSummary,
    _new_ulid,
)

log = structlog.get_logger(__name__)

demo_router = APIRouter(prefix="/v1/demo", tags=["demo"])


# ---------------------------------------------------------------------------
# Module state (playback task)
# ---------------------------------------------------------------------------

_playback_task: Optional[asyncio.Task] = None  # type: ignore[type-arg]
_playback_running: bool = False

# EAF-04 static asset profile (written to DB if absent)
_EAF04_ASSET_FIELDS: dict = {
    "asset_id": "EAF-04",
    "plant_area": "EAF-Bay-1",
    "equipment_name": "Electric Arc Furnace 04 (EAF-04)",
    "equipment_class": "electric_arc_furnace",
    "manufacturer": "SMS Group",
    "criticality_tier": "critical",
    "subsystem": "electrode-bearing-assembly",
    "iso14224_taxonomy": "rotating.bearing.electrode_support",
    "work_center": "Steelmaking-1",
    "source_system": "demo",
}

# Degrading sensor sequence: 5 steps × 15 s = 60 s total.
# rul_critical_days default = 14.0 → CRITICAL fires at step 5 (rul=11.3/24 days).
# anomaly_score_threshold default = 0.65 → HIGH fires at step 3, CRITICAL at step 5.
_PLAYBACK_STEPS: list[tuple] = [
    # (rul_days, anomaly_score, temp_c, vibration_mm_s, operating_condition, op_hours_offset)
    (45.0, 0.40, 730.0,  8.5,  "normal",   0.00),  # t= 0s — baseline, no alert
    (35.0, 0.52, 755.0, 10.2,  "normal",   0.25),  # t=15s — slight degradation, no alert
    (28.0, 0.61, 778.0, 12.8,  "degraded", 0.50),  # t=30s — HIGH warning (rul < 30)
    (20.0, 0.76, 812.0, 14.9,  "degraded", 0.75),  # t=45s — HIGH persists
    (11.3 / 24, 0.94, 847.0, 18.7, "severe", 1.00),  # t=60s — CRITICAL (rul < 14 + anomaly > 0.9)
]


# ---------------------------------------------------------------------------
# Response schemas (demo-scoped, not in global schemas.py)
# ---------------------------------------------------------------------------

class DemoStartResponse(BaseModel):
    status: str
    message: str
    eaf04_critical_expected_in_seconds: int
    playback_steps: int


class DemoInjectFaultResponse(BaseModel):
    status: str
    alert_entity_id: str
    asset_id: str
    severity: str
    rul_days: float
    recommended_action: str
    message: str


class DemoResetResponse(BaseModel):
    status: str
    message: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_eaf04_asset_in_session(session) -> AssetProfile:  # type: ignore[no-untyped-def]
    """
    Create the EAF-04 AssetProfile row if it doesn't already exist.
    Must be called inside an active session_scope() block.
    """
    from sqlmodel import select

    existing = session.exec(
        select(AssetProfile).where(AssetProfile.asset_id == "EAF-04")
    ).first()
    if existing:
        return existing

    asset = AssetProfile(
        entity_id=_new_ulid(),
        **_EAF04_ASSET_FIELDS,
    )
    session.add(asset)
    session.flush()  # assign entity_id before return
    log.info("demo.eaf04_asset_created", entity_id=asset.entity_id)
    return asset


# ---------------------------------------------------------------------------
# Playback background task
# ---------------------------------------------------------------------------

async def _run_playback() -> None:
    """
    Background asyncio task: insert degrading SensorSummary rows for EAF-04
    every 15 seconds. APScheduler evaluate_alerts() runs every 5 seconds and
    classifies each new reading against the configured thresholds.

    Timeline:
      t= 0s  step 1: rul=45.0d, anomaly=0.40 — no alert
      t=15s  step 2: rul=35.0d, anomaly=0.52 — no alert
      t=30s  step 3: rul=28.0d, anomaly=0.61 — HIGH warning fires (rul < 30d)
      t=45s  step 4: rul=20.0d, anomaly=0.76 — HIGH persists
      t=60s  step 5: rul=0.47d, anomaly=0.94 — CRITICAL fires (rul < 14d + anomaly > 0.90)
    """
    global _playback_running

    _playback_running = True
    log.info("demo.playback_started", steps=len(_PLAYBACK_STEPS))

    for i, step in enumerate(_PLAYBACK_STEPS):
        if not _playback_running:
            log.info("demo.playback_cancelled_mid_step", step=i + 1)
            break

        rul_days, anomaly, temp, vib, condition, hours_offset = step

        log.info(
            "demo.playback_step",
            step=i + 1,
            total=len(_PLAYBACK_STEPS),
            rul_days=round(rul_days, 4),
            anomaly_score=anomaly,
            condition=condition,
        )

        try:
            now = datetime.now(timezone.utc)
            with session_scope() as session:
                asset = _ensure_eaf04_asset_in_session(session)
                sensor = SensorSummary(
                    entity_id=_new_ulid(),
                    asset_id=asset.asset_id,
                    plant_area=asset.plant_area,
                    source_system="demo",
                    window_start=now - timedelta(minutes=15),
                    window_end=now,
                    sensor_readings={
                        "temperature_c": temp,
                        "vibration_mm_s": vib,
                        "pressure_bar": round(1.02 + anomaly * 0.15, 3),
                        "rpm": round(max(1400.0 - anomaly * 200.0, 800.0), 1),
                        "current_a": round(1200.0 + anomaly * 400.0, 1),
                    },
                    anomaly_score=anomaly,
                    rul_days_p50=rul_days,
                    operating_condition=condition,
                    operating_hours=8500.0 + hours_offset,
                )
                session.add(sensor)
        except Exception as exc:
            log.error("demo.playback_step_error", step=i + 1, error=str(exc)[:200])

        # Wait between steps; skip sleep after the last one
        if i < len(_PLAYBACK_STEPS) - 1 and _playback_running:
            await asyncio.sleep(15.0)

    _playback_running = False
    log.info("demo.playback_complete")


# ---------------------------------------------------------------------------
# POST /v1/demo/start
# ---------------------------------------------------------------------------

@demo_router.post(
    "/start",
    response_model=DemoStartResponse,
    summary="Begin demo sensor degradation playback — CRITICAL alert fires in ~60 s",
)
async def demo_start() -> DemoStartResponse:
    """
    Kick off the degrading sensor data playback for EAF-04.

    5 SensorSummary rows are written every 15 seconds. The APScheduler proactive
    evaluator picks each row up within 5 seconds and classifies it:
    - Step 3 (t≈30s): HIGH warning (rul_days < 30)
    - Step 5 (t≈60s): CRITICAL alert (rul_days < 14 + anomaly_score > 0.90)

    The CRITICAL alert is broadcast via SSE (GET /v1/alerts/stream) AND persisted
    to wizard.db by the evaluator (GET /v1/alerts shows it after it fires).

    For an instant demo moment without the 60s wait, use POST /v1/demo/inject_fault.
    """
    global _playback_task, _playback_running

    if _playback_running:
        return DemoStartResponse(
            status="already_running",
            message=(
                "Playback already in progress. "
                "POST /v1/demo/reset to stop and restart."
            ),
            eaf04_critical_expected_in_seconds=60,
            playback_steps=len(_PLAYBACK_STEPS),
        )

    # Cancel any stale completed/cancelled task reference
    if _playback_task and not _playback_task.done():
        _playback_task.cancel()

    _playback_task = asyncio.create_task(_run_playback())
    log.info("demo.start_requested")

    return DemoStartResponse(
        status="started",
        message=(
            "EAF-04 sensor degradation playback started. "
            f"{len(_PLAYBACK_STEPS)} steps × 15 s intervals. "
            "APScheduler evaluator runs every 5 s — CRITICAL alert expected in ~60 s. "
            "Stream alerts at GET /v1/alerts/stream or poll GET /v1/alerts."
        ),
        eaf04_critical_expected_in_seconds=60,
        playback_steps=len(_PLAYBACK_STEPS),
    )


# ---------------------------------------------------------------------------
# POST /v1/demo/inject_fault
# ---------------------------------------------------------------------------

_EAF04_RECOMMENDED_ACTION = (
    "1. IMMEDIATE: Notify EAF Plant Manager and Maintenance Lead. "
    "2. URGENT: Place emergency order for SKF-6310-2RS1 bearing (part# EAF-BRG-001). "
    "   Alternate: NTN 6310-ZZ (compatible, 5-day delivery) — verify with stores. "
    "3. PLAN: Schedule 4-hour maintenance window within next 8 hours. "
    "4. MONITOR: Increase vibration checks to every 15 minutes until repair. "
    "5. PREPARE: Refer to EAF-SOP-007 §4.3 — Bearing Replacement Procedure."
)

def _compute_eaf04_inject_rul() -> float:
    """
    Compute rul_days_p50 for the EAF-04 CRITICAL inject_fault sensor readings
    via the same ML model path used by /v1/chat — so both surfaces (dashboard
    SensorSummary.rul_days_p50 and chat estimated_rul_days_p50) agree.

    Falls back to a hard-coded value (≈ 0.47d) if the ML model is unavailable.
    """
    _inject_readings = {
        "temperature_c": 847.0,
        "vibration_mm_s": 18.7,
        "pressure_bar": 1.16,
        "rpm": 1012.0,
        "current_a": 1576.0,
    }
    try:
        from wizard.ml.rul_estimator import predict_rul as _predict_rul
        result = _predict_rul(
            asset_id="EAF-04",
            sensor_readings=_inject_readings,
            equipment_class="fan",
        )
        return result.rul_days_p50
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning(
            "demo._compute_eaf04_inject_rul: ML unavailable (%s) — using 0.4708d fallback", exc
        )
        return round(11.3 / 24, 4)  # 11.3 hours → days ≈ 0.4708


# Compute once at module load; cached for the process lifetime.
_EAF04_RUL_DAYS: float = _compute_eaf04_inject_rul()


@demo_router.post(
    "/inject_fault",
    response_model=DemoInjectFaultResponse,
    summary="Inject EAF-04 CRITICAL alert immediately — deterministic demo backstop",
)
async def demo_inject_fault() -> DemoInjectFaultResponse:
    """
    Deterministic backstop for the demo wow-moment.

    This endpoint does TWO things atomically (within the same request):
    1. Writes an EAF-04 CRITICAL AnomalyAlert + triggering SensorSummary to wizard.db
       so that GET /v1/alerts returns the alert immediately.
    2. Broadcasts the AlertEvent to all connected SSE clients via AlertBroadcaster
       so that GET /v1/alerts/stream receives the alert in real-time.

    Use this when:
    - You want an instant demo without waiting 60 s for the playback
    - The evaluator didn't fire in time (e.g. no sensor data was in DB)
    - You want a guaranteed scripted moment at a specific point in the demo

    The endpoint is idempotent per-run: calling it again writes a new alert row
    (new ULID) and broadcasts again — each call is a distinct alert event.
    """
    alert_entity_id = _new_ulid()
    now = datetime.now(timezone.utc)

    description = (
        "CRITICAL PROACTIVE ALERT: Electric Arc Furnace EAF-04 — "
        "Electrode Bearing Assembly. "
        f"Predicted Remaining Useful Life: {_EAF04_RUL_DAYS * 24:.1f} hours (p50). "
        "IsolationForest anomaly score: 0.94 (threshold: 0.65). "
        "Vibration: 18.7 mm/s (operating limit: 12.0 mm/s). "
        "Temperature: 847°C (+42°C above baseline). "
        "Pattern matches historical BF-BEARING-BURNOUT failure mode (3 prior incidents). "
        "SPARES WARNING: SKF-6310-2RS1 bearing is OUT OF STOCK. Lead time: 14 days. "
        "ORDER NOW to avoid extended downtime. "
        "Estimated production loss if not acted: ₹8.5 Cr "
        "(11 h × ₹75,000/hr × production rate)."
    )

    # ------------------------------------------------------------------
    # Step 1: Persist to DB so GET /v1/alerts returns this alert
    # ------------------------------------------------------------------
    sensor_entity_id: Optional[str] = None

    try:
        with session_scope() as session:
            # Ensure EAF-04 asset profile exists
            _ensure_eaf04_asset_in_session(session)

            # Write the triggering SensorSummary (anomaly + RUL at critical levels)
            sensor = SensorSummary(
                entity_id=_new_ulid(),
                asset_id="EAF-04",
                plant_area="EAF-Bay-1",
                source_system="demo",
                window_start=now - timedelta(minutes=15),
                window_end=now,
                sensor_readings={
                    "temperature_c": 847.0,
                    "vibration_mm_s": 18.7,
                    "pressure_bar": 1.16,
                    "rpm": 1012.0,
                    "current_a": 1576.0,
                },
                anomaly_score=0.94,
                rul_days_p50=_EAF04_RUL_DAYS,
                operating_condition="severe",
                operating_hours=8503.75,
            )
            session.add(sensor)
            session.flush()
            sensor_entity_id = sensor.entity_id

            # Write the AnomalyAlert row (with the pre-generated ULID)
            anomaly_row = AnomalyAlert(
                entity_id=alert_entity_id,
                asset_id="EAF-04",
                plant_area="EAF-Bay-1",
                source_system="demo",
                alert_type="rul_critical",
                risk_level="critical",
                description=description,
                triggering_sensor_summary_id=sensor_entity_id,
                estimated_rul_days=_EAF04_RUL_DAYS,
                recommended_action=_EAF04_RECOMMENDED_ACTION,
                acknowledged=False,
                cooldown_key="EAF-04:rul_critical",
            )
            session.add(anomaly_row)

        log.info(
            "demo.inject_fault_persisted",
            alert_entity_id=alert_entity_id,
            sensor_entity_id=sensor_entity_id,
            rul_days=_EAF04_RUL_DAYS,
        )
    except Exception as exc:
        log.error("demo.inject_fault_db_error", error=str(exc)[:300])
        raise

    # ------------------------------------------------------------------
    # Step 2: Reset cooldown so the SSE broadcast always fires,
    #         then call trigger_demo_eaf04_alert() to broadcast via SSE.
    # ------------------------------------------------------------------
    await _dedup.force_key("EAF-04:rul_critical")
    await trigger_demo_eaf04_alert()

    clients = broadcaster.client_count()
    log.info(
        "demo.inject_fault_complete",
        alert_entity_id=alert_entity_id,
        sse_clients_notified=clients,
    )

    return DemoInjectFaultResponse(
        status="injected",
        alert_entity_id=alert_entity_id,
        asset_id="EAF-04",
        severity="critical",
        rul_days=_EAF04_RUL_DAYS,
        recommended_action=_EAF04_RECOMMENDED_ACTION,
        message=(
            f"CRITICAL alert persisted to DB (entity_id={alert_entity_id}) "
            f"and broadcast to {clients} SSE client(s). "
            "GET /v1/alerts returns this alert immediately."
        ),
    )


# ---------------------------------------------------------------------------
# POST /v1/demo/reset
# ---------------------------------------------------------------------------

@demo_router.post(
    "/reset",
    response_model=DemoResetResponse,
    summary="Stop playback + clear EAF-04 cooldowns — resets demo to clean state",
)
async def demo_reset() -> DemoResetResponse:
    """
    Stop any active playback task and clear all EAF-04 dedup cooldown keys.
    The demo can be rerun cleanly from the same process after calling this.
    DB rows written by previous runs are NOT deleted (use make reset to wipe the DB).
    """
    global _playback_task, _playback_running

    stopped = False
    if _playback_running or (_playback_task and not _playback_task.done()):
        _playback_running = False
        if _playback_task and not _playback_task.done():
            _playback_task.cancel()
            try:
                await asyncio.wait_for(_playback_task, timeout=3.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass
        _playback_task = None
        stopped = True

    # Clear all EAF-04 dedup cooldown keys so next inject_fault / playback fires cleanly
    for key in ("EAF-04:rul_critical", "EAF-04:rul_warning", "EAF-04:sensor_anomaly"):
        await _dedup.force_key(key)

    log.info("demo.reset_complete", playback_was_running=stopped)

    return DemoResetResponse(
        status="reset",
        message=(
            f"Demo state reset (playback {'stopped' if stopped else 'was idle'}). "
            "EAF-04 cooldown keys cleared. "
            "POST /v1/demo/start or /v1/demo/inject_fault to begin again."
        ),
    )
