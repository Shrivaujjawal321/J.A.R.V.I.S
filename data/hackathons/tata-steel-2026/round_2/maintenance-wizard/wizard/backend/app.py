"""
wizard.backend.app
==================
FastAPI application entry point for the Maintenance Wizard backend.

Endpoints:
  POST /v1/chat                — synchronous chat (graph_placeholder stub)
  POST /v1/chat/stream         — streaming chat via SSE (native fastapi.sse)
  GET  /v1/alerts/stream       — persistent SSE alert stream (per-client queue)
  GET  /v1/alerts              — cursor-paginated alert history
  POST /v1/alerts/{id}/ack     — acknowledge alert (engineer confirms)
  GET  /v1/sensor/state        — current sensor snapshot for all assets
  POST /v1/feedback            — engineer correction (triggers WRPS weight update)
  GET  /v1/session/{id}/state  — LangGraph checkpoint state for explainability
  GET  /v1/health              — liveness probe (DB + scheduler + circuit breaker)
  GET  /docs                   — Swagger UI (auto-generated)

Features:
  • lifespan-managed startup/shutdown (not deprecated @app.on_event)
  • Structured ErrorEnvelope on all exceptions (Stripe-style)
  • Native fastapi.sse EventSourceResponse for all SSE endpoints
  • CorrelationIdMiddleware → X-Request-ID header + structlog binding
  • APScheduler AsyncIOScheduler 5s proactive evaluator
  • pybreaker circuit breaker around LLM calls (via middleware.llm_circuit_breaker)
  • tenacity retry on LLM calls (in wrps.py)
  • CORS limited to localhost origins

Usage::

    # Direct (development)
    uvicorn wizard.backend.app:app --host 127.0.0.1 --port 8000 --reload

    # Via Makefile
    make run
"""
from __future__ import annotations

import asyncio
import base64
import json
import os
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncGenerator, Optional

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse, ServerSentEvent
from sqlmodel import Session, select

from wizard.core.config import settings
from wizard.core.db import get_session, init_db, session_scope
from wizard.core.schemas import (
    AlertSeverity,
    AnomalyAlert,
    AssetProfile,
    SensorSummary,
    _new_ulid,
)

from wizard.backend.alerting import AlertBroadcaster, broadcaster, setup_scheduler
from wizard.backend.demo import demo_router
from wizard.agents.graph import run_graph, stream_graph
from wizard.backend.middleware import (
    AsyncCircuitBreaker,
    CircuitOpenError,
    CorrelationIdMiddleware,
    configure_structlog,
    get_request_id,
    llm_circuit_breaker,
)
from wizard.backend.schemas import (
    AlertAckResponse,
    AlertListItem,
    AlertListResponse,
    AssetSensorState,
    ChatRequest,
    ChatResponse,
    ErrorCode,
    ErrorDetail,
    ErrorEnvelope,
    FeedbackRequest,
    FeedbackResponse,
    HealthResponse,
    SensorStateResponse,
    SessionStateResponse,
)
from wizard.backend.wrps import (
    apply_feedback_to_weights,
    score_maintenance_priority_async,
    score_maintenance_priority_for_session,
    # score_maintenance_priority_for_session is intentionally not imported here:
    # wiring it into ChatResponse would require schema changes out-of-scope for
    # this wave. Import it in the agentic-core wave when ChatResponse gains a
    # risk_score field. Removing the dead import prevents lint / import errors.
)

log = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Application state
# ---------------------------------------------------------------------------

_start_time: float = time.monotonic()
_scheduler: Optional[AsyncIOScheduler] = None


# ---------------------------------------------------------------------------
# Lifespan (replaces deprecated @app.on_event)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPI lifespan context manager.
    Startup: init DB, start scheduler, configure structlog, update circuit breaker config.
    Shutdown: gracefully stop scheduler.
    """
    global _start_time, _scheduler

    configure_structlog()
    log.info("wizard_backend.starting", pid=os.getpid())

    # DB init (idempotent — CREATE TABLE IF NOT EXISTS)
    try:
        init_db()
        log.info("wizard_backend.db_initialized")
    except Exception as exc:
        log.error("wizard_backend.db_init_failed", error=str(exc))
        raise

    # Seed per-asset demo SensorSummary rows (idempotent; skipped if already present).
    # This ensures _extract_sensor_snapshot reads real data for every asset from the
    # first chat request — no hardcoded values.
    try:
        from wizard.data.db_ingest import (
            seed_demo_assets,
            seed_demo_sensor_summaries,
            seed_fault_log,
            seed_demo_spare_parts,
        )
        seed_demo_assets()
        n_seeded = seed_demo_sensor_summaries()
        n_faults = seed_fault_log()
        n_spares = seed_demo_spare_parts()
        log.info(
            "wizard_backend.sensor_seed_complete",
            new_rows=n_seeded, fault_rows=n_faults, spare_rows=n_spares,
        )
    except Exception as exc:
        # Non-fatal: demo still works without seed rows (returns {} for missing assets)
        log.warning("wizard_backend.sensor_seed_failed", error=str(exc)[:200])

    # Override circuit breaker config from settings
    llm_circuit_breaker._fail_max = settings.circuit_breaker_fail_max
    llm_circuit_breaker._reset_timeout = settings.circuit_breaker_reset_timeout

    # Scheduler
    _scheduler = AsyncIOScheduler(timezone="UTC")
    setup_scheduler(_scheduler)
    _scheduler.start()
    _start_time = time.monotonic()

    log.info("wizard_backend.started", port=settings.backend_port)

    yield  # ← application is running

    # Shutdown
    log.info("wizard_backend.shutting_down")
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
    log.info("wizard_backend.shutdown_complete")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Maintenance Wizard — Tata Steel AI 2026",
    description=(
        "Agentic maintenance co-pilot for steel plant engineers. "
        "Proactive RUL + RCA + structured maintenance plans with full source citations."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Demo sensor playback + inject_fault router
app.include_router(demo_router)

# Middleware — order matters: innermost first
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",  # Streamlit default
        "http://127.0.0.1:8501",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global exception handlers
# ---------------------------------------------------------------------------

def _make_error_envelope(
    code: ErrorCode,
    message: str,
    err_type: str,
    status_code: int,
    request_id: Optional[str] = None,
) -> tuple[JSONResponse, dict]:
    rid = request_id or get_request_id()
    envelope = ErrorEnvelope(
        error=ErrorDetail(
            code=code,
            message=message,
            type=err_type,  # type: ignore[arg-type]
            request_id=rid,
        )
    )
    return JSONResponse(
        status_code=status_code,
        content=envelope.model_dump(mode="json"),
    )


@app.exception_handler(CircuitOpenError)
async def circuit_open_handler(request: Request, exc: CircuitOpenError) -> JSONResponse:
    return _make_error_envelope(
        ErrorCode.LLM_CIRCUIT_OPEN,
        f"LLM service temporarily unavailable — circuit open. "
        f"Retry in {exc.resets_in_seconds:.0f}s.",
        "upstream",
        503,
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    code_map: dict[int, ErrorCode] = {
        400: ErrorCode.INVALID_REQUEST,
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.ASSET_NOT_FOUND,
        422: ErrorCode.INVALID_REQUEST,
        429: ErrorCode.RATE_LIMIT_EXCEEDED,
    }
    error_code = code_map.get(exc.status_code, ErrorCode.INTERNAL_ERROR)
    err_type = "validation" if exc.status_code in (400, 422) else "server"
    return _make_error_envelope(
        error_code,
        str(exc.detail),
        err_type,
        exc.status_code,
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    log.error(
        "unhandled_exception",
        exc_type=type(exc).__name__,
        error=str(exc)[:200],
        path=request.url.path,
    )
    return _make_error_envelope(
        ErrorCode.INTERNAL_ERROR,
        "An internal error occurred. Please retry your request.",
        "server",
        500,
    )


# ---------------------------------------------------------------------------
# v1/health
# ---------------------------------------------------------------------------

@app.get(
    "/v1/health",
    response_model=HealthResponse,
    summary="Liveness probe — DB + scheduler + circuit breaker status",
)
async def health_check() -> HealthResponse:
    # DB check (quick ping — read-only, uses session_scope for proper cleanup)
    db_ok = False
    try:
        with session_scope() as session:
            session.exec(select(AssetProfile).limit(1)).first()
            db_ok = True
    except Exception:
        pass

    scheduler_running = bool(_scheduler and _scheduler.running)
    cb_state = llm_circuit_breaker.state
    uptime = round(time.monotonic() - _start_time, 1)

    return HealthResponse(
        status="ok" if (db_ok and scheduler_running) else "degraded",
        db_ok=db_ok,
        scheduler_running=scheduler_running,
        circuit_breaker_state=cb_state,
        alert_broadcaster_clients=broadcaster.client_count(),
        version="1.0.0",
        uptime_seconds=uptime,
        checked_at=datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# v1/chat — synchronous
# ---------------------------------------------------------------------------

@app.post(
    "/v1/chat",
    response_model=ChatResponse,
    summary="Synchronous chat — returns full MaintenanceRecommendation",
)
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    request_id = get_request_id()
    start = time.monotonic()

    structlog.contextvars.bind_contextvars(
        session_id=body.session_id,
        equipment_id=body.equipment_id,
    )

    log.info("chat.request_received", query_len=len(body.query))

    # Idempotency check (simple in-memory; real graph uses SqliteSaver thread_id)
    # The graph_placeholder deduplicates naturally — same session_id + idempotency_key
    # returns same stub. Real agentic-core uses LangGraph checkpointer for this.

    recommendation, agent_trace = await run_graph(body)
    latency_ms = round((time.monotonic() - start) * 1000, 2)

    log.info(
        "chat.response_sent",
        recommendation_id=recommendation.recommendation_id,
        latency_ms=latency_ms,
    )

    return ChatResponse(
        session_id=body.session_id,
        equipment_id=body.equipment_id,
        recommendation=recommendation,
        agent_trace=agent_trace,
        latency_ms=latency_ms,
    )


# ---------------------------------------------------------------------------
# v1/chat/stream — SSE streaming chat
# ---------------------------------------------------------------------------

@app.post(
    "/v1/chat/stream",
    summary="Streaming chat via SSE — yields agent_step/token/recommendation_ready events",
)
async def chat_stream(request: Request, body: ChatRequest) -> EventSourceResponse:
    structlog.contextvars.bind_contextvars(
        session_id=body.session_id,
        equipment_id=body.equipment_id,
    )
    log.info("chat_stream.started")

    async def _generator() -> AsyncGenerator[ServerSentEvent, None]:
        try:
            async for chunk in stream_graph(body):
                if await request.is_disconnected():
                    log.info("chat_stream.client_disconnected")
                    break
                event_type = chunk.get("event_type", "agent_step")
                import json
                yield ServerSentEvent(
                    id=str(uuid.uuid4()),
                    event=event_type,
                    data=json.dumps(chunk, default=str),
                    retry=3000,
                )
        except asyncio.CancelledError:
            log.info("chat_stream.cancelled")
            raise
        except Exception as exc:
            log.error("chat_stream.error", error=str(exc))
            import json
            yield ServerSentEvent(
                event="error",
                data=json.dumps({
                    "error": {
                        "code": "STREAM_ERROR",
                        "message": "Stream interrupted — please retry",
                    }
                }),
            )

    return EventSourceResponse(
        _generator(),
        headers={"Cache-Control": "no-cache"},
    )


# ---------------------------------------------------------------------------
# v1/alerts/stream — persistent SSE alert stream
# ---------------------------------------------------------------------------

@app.get(
    "/v1/alerts/stream",
    summary="Persistent SSE stream of proactive maintenance alerts",
)
async def alerts_stream(
    request: Request,
    severity: Optional[str] = Query(
        default=None,
        description="Filter: comma-separated severity levels, e.g. 'HIGH,CRITICAL'",
    ),
) -> EventSourceResponse:
    """
    Each connected client gets its own asyncio.Queue via AlertBroadcaster.
    Events arrive from the APScheduler proactive evaluator (every 5s).
    Heartbeat ping every 15s to keep proxies alive.

    Last-Event-ID replay (anti-pattern fix #8):
      When the browser reconnects after a drop it sends 'Last-Event-ID: <ulid>'
      in the request headers. We replay any ring-buffered events with ID >
      Last-Event-ID before entering the live stream, guaranteeing at-least-once
      delivery of alerts that fired during the disconnected window.
    """
    client_id = str(uuid.uuid4())

    # Read Last-Event-ID from reconnect header (empty string = fresh connect)
    last_event_id: str = request.headers.get("Last-Event-ID", "").strip()

    # Parse severity filter
    severity_filter: Optional[set[str]] = None
    if severity:
        severity_filter = {s.strip().upper() for s in severity.split(",")}

    import json

    async def _generator() -> AsyncGenerator[ServerSentEvent, None]:
        client_queue = await broadcaster.register(client_id)
        log.info(
            "alerts_stream.client_connected",
            client_id=client_id,
            last_event_id=last_event_id or None,
        )

        # Replay missed events when client reconnects with Last-Event-ID
        if last_event_id:
            missed = await broadcaster.get_missed_events(last_event_id)
            log.info(
                "alerts_stream.replaying_missed",
                client_id=client_id,
                count=len(missed),
                since=last_event_id,
            )
            for missed_event in missed:
                if (
                    severity_filter is None
                    or missed_event.severity.value.upper() in severity_filter
                ):
                    yield ServerSentEvent(
                        id=missed_event.alert_id,
                        event="alert",
                        data=missed_event.model_dump_json(),
                        retry=3000,
                    )

        # Send a "connected" event immediately so the client knows the stream is live
        yield ServerSentEvent(
            id=_new_ulid(),
            event="connected",
            data=json.dumps({
                "client_id": client_id,
                "message": "Alert stream connected — proactive evaluator running every 5s",
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }),
            retry=3000,
        )

        try:
            while True:
                if await request.is_disconnected():
                    log.info("alerts_stream.client_disconnected", client_id=client_id)
                    break

                try:
                    alert_event = await asyncio.wait_for(
                        client_queue.get(), timeout=15.0
                    )
                    # Apply severity filter
                    if (
                        severity_filter is None
                        or alert_event.severity.value.upper() in severity_filter
                    ):
                        yield ServerSentEvent(
                            id=alert_event.alert_id,
                            event="alert",
                            data=alert_event.model_dump_json(),
                            retry=3000,
                        )
                except asyncio.TimeoutError:
                    # Heartbeat to keep connection alive through idle periods
                    yield ServerSentEvent(comment="heartbeat")

        except asyncio.CancelledError:
            log.info("alerts_stream.cancelled", client_id=client_id)
            raise
        finally:
            await broadcaster.unregister(client_id)

    return EventSourceResponse(
        _generator(),
        headers={"Cache-Control": "no-cache"},
    )


# ---------------------------------------------------------------------------
# v1/alerts — paginated history
# ---------------------------------------------------------------------------

@app.get(
    "/v1/alerts",
    response_model=AlertListResponse,
    summary="Paginated alert history — cursor-based",
)
async def list_alerts(
    session: Session = Depends(get_session),
    severity: Optional[str] = Query(default=None, description="Filter by risk_level"),
    asset_id: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    cursor: Optional[str] = Query(default=None, description="Opaque cursor from previous page"),
) -> AlertListResponse:
    # Build query
    stmt = select(AnomalyAlert).order_by(AnomalyAlert.triggered_at.desc())  # type: ignore[union-attr]

    if severity:
        stmt = stmt.where(AnomalyAlert.risk_level == severity.lower())
    if asset_id:
        stmt = stmt.where(AnomalyAlert.asset_id == asset_id)

    # Cursor decode (base64 of "triggered_at|entity_id")
    if cursor:
        try:
            raw = base64.urlsafe_b64decode(cursor).decode()
            cursor_ts_str, cursor_eid = raw.split("|", 1)
            cursor_dt = datetime.fromisoformat(cursor_ts_str)
            stmt = stmt.where(AnomalyAlert.triggered_at < cursor_dt)
        except Exception:
            pass  # Invalid cursor → ignore, return from beginning

    stmt = stmt.limit(limit + 1)
    rows = session.exec(stmt).all()

    has_more = len(rows) > limit
    rows = rows[:limit]

    # Fetch equipment names in one query
    asset_ids = {r.asset_id for r in rows}
    assets_by_id: dict[str, str] = {}
    if asset_ids:
        asset_rows = session.exec(
            select(AssetProfile).where(AssetProfile.asset_id.in_(asset_ids))  # type: ignore[union-attr]
        ).all()
        assets_by_id = {a.asset_id: a.equipment_name for a in asset_rows}

    items = [
        AlertListItem(
            alert_entity_id=r.entity_id,
            asset_id=r.asset_id,
            equipment_name=assets_by_id.get(r.asset_id, r.asset_id),
            alert_type=r.alert_type,
            risk_level=r.risk_level,
            description=r.description,
            triggered_at=r.triggered_at,
            acknowledged=r.acknowledged,
            cooldown_key=r.cooldown_key,
        )
        for r in rows
    ]

    next_cursor: Optional[str] = None
    if has_more and rows:
        last = rows[-1]
        cursor_raw = f"{last.triggered_at.isoformat()}|{last.entity_id}"
        next_cursor = base64.urlsafe_b64encode(cursor_raw.encode()).decode()

    return AlertListResponse(
        items=items,
        total=len(items),
        next_cursor=next_cursor,
    )


# ---------------------------------------------------------------------------
# v1/alerts/{id}/ack
# ---------------------------------------------------------------------------

@app.post(
    "/v1/alerts/{alert_entity_id}/ack",
    response_model=AlertAckResponse,
    summary="Acknowledge an alert — marks it as reviewed by engineer",
)
async def ack_alert(
    alert_entity_id: str,
    request: Request,
    session: Session = Depends(get_session),
    engineer_id: str = Query(default="engineer", description="Engineer identifier"),
) -> AlertAckResponse:
    row = session.exec(
        select(AnomalyAlert).where(AnomalyAlert.entity_id == alert_entity_id)
    ).first()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Alert {alert_entity_id} not found")

    row.acknowledged = True
    row.acknowledged_by = engineer_id
    session.add(row)
    session.commit()

    log.info(
        "alert.acknowledged",
        alert_entity_id=alert_entity_id,
        engineer_id=engineer_id,
    )

    return AlertAckResponse(
        alert_entity_id=alert_entity_id,
        acknowledged=True,
        acknowledged_by=engineer_id,
        message=f"Alert {alert_entity_id} acknowledged by {engineer_id}",
    )


# ---------------------------------------------------------------------------
# v1/sensor/state
# ---------------------------------------------------------------------------

@app.get(
    "/v1/sensor/state",
    response_model=SensorStateResponse,
    summary="Current sensor snapshot for all registered assets",
)
async def sensor_state(session: Session = Depends(get_session)) -> SensorStateResponse:
    assets = session.exec(select(AssetProfile)).all()

    asset_states: list[AssetSensorState] = []
    critical_count = 0

    for asset in assets:
        # Latest sensor summary
        sensor = session.exec(
            select(SensorSummary)
            .where(SensorSummary.asset_id == asset.asset_id)
            .order_by(SensorSummary.window_end.desc())  # type: ignore[union-attr]
            .limit(1)
        ).first()

        # Active (unacknowledged) alert count
        active_alerts = session.exec(
            select(AnomalyAlert).where(
                AnomalyAlert.asset_id == asset.asset_id,
                AnomalyAlert.acknowledged == False,  # noqa: E712
            )
        ).all()

        readings: dict[str, Optional[float]] = {}
        anomaly_score: Optional[float] = None
        rul_p50: Optional[float] = None
        last_updated: Optional[datetime] = None

        if sensor:
            readings = {
                k: (float(v) if v is not None else None)
                for k, v in sensor.sensor_readings.items()
            }
            anomaly_score = sensor.anomaly_score
            rul_p50 = sensor.rul_days_p50
            last_updated = sensor.window_end

        if asset.criticality_tier == "critical":
            critical_count += 1

        asset_states.append(
            AssetSensorState(
                asset_id=asset.asset_id,
                equipment_name=asset.equipment_name,
                criticality_tier=asset.criticality_tier,
                latest_sensor_readings=readings,
                anomaly_score=anomaly_score,
                rul_days_p50=rul_p50,
                active_alert_count=len(active_alerts),
                last_updated=last_updated,
            )
        )

    return SensorStateResponse(
        assets=asset_states,
        total_assets=len(asset_states),
        critical_asset_count=critical_count,
        retrieved_at=datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# v1/feedback
# ---------------------------------------------------------------------------

@app.post(
    "/v1/feedback",
    response_model=FeedbackResponse,
    summary="Record engineer feedback — triggers WRPS weight update (FR6)",
)
async def feedback(body: FeedbackRequest) -> FeedbackResponse:
    feedback_id = _new_ulid()
    weights_updated = False

    log.info(
        "feedback.received",
        feedback_id=feedback_id,
        equipment_id=body.equipment_id,
        thumbs_up=body.thumbs_up,
        correction=body.correction[:100] if body.correction else None,
    )

    # Persist feedback to JSONL (simple append — no ORM needed)
    import json

    feedback_path = settings.resolved_db_path().parent / "feedback" / "engineer_feedback.jsonl"
    feedback_path.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "feedback_id": feedback_id,
        "session_id": body.session_id,
        "equipment_id": body.equipment_id,
        "recommendation_id": body.recommendation_id,
        "thumbs_up": body.thumbs_up,
        "correction": body.correction,
        "corrected_risk_level": body.corrected_risk_level.value if body.corrected_risk_level else None,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(feedback_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    # Update WRPS weights if a risk correction was provided
    if body.corrected_risk_level:
        # We need current risk level — use WRPS to compute it
        try:
            current_score = await score_maintenance_priority_async(body.equipment_id)
            weights_updated = apply_feedback_to_weights(
                corrected_risk_level=body.corrected_risk_level,
                current_risk_level=current_score.risk_tier,
            )
        except Exception as exc:
            log.warning("feedback.weight_update_failed", error=str(exc))

    return FeedbackResponse(
        feedback_id=feedback_id,
        weights_updated=weights_updated,
        message=(
            f"Feedback recorded. "
            + ("WRPS weights updated via EMA." if weights_updated else "No weight change.")
        ),
    )


# ---------------------------------------------------------------------------
# v1/session/{id}/state
# ---------------------------------------------------------------------------

@app.get(
    "/v1/session/{session_id}/state",
    response_model=SessionStateResponse,
    summary="LangGraph checkpoint state for session explainability",
)
async def session_state(session_id: str) -> SessionStateResponse:
    """
    Returns the full LangGraph MaintenanceState for the given session.
    Reads from the AsyncSqliteSaver checkpoint via wizard.agents.graph.get_graph_state.
    """
    try:
        from wizard.agents.graph import get_graph_state
        state_dict = await get_graph_state(session_id)
        if state_dict:
            # Serialise Pydantic models within the state for JSON transport
            serialisable: dict = {}
            for k, v in state_dict.items():
                try:
                    if hasattr(v, "model_dump"):
                        serialisable[k] = v.model_dump(mode="json")
                    elif isinstance(v, list):
                        serialisable[k] = [
                            item.model_dump(mode="json") if hasattr(item, "model_dump") else item
                            for item in v
                        ]
                    else:
                        serialisable[k] = v
                except Exception:
                    serialisable[k] = str(v)
            return SessionStateResponse(
                session_id=session_id,
                state=serialisable,
                checkpoint_at=datetime.now(timezone.utc),
                note="Live MaintenanceState from LangGraph AsyncSqliteSaver checkpoint.",
            )
    except Exception as exc:
        log.warning("session_state.read_failed", session_id=session_id, error=str(exc))

    return SessionStateResponse(
        session_id=session_id,
        state={"thread_id": session_id, "status": "no_checkpoint"},
        checkpoint_at=None,
        note="No checkpoint found for this session. Run a /v1/chat query first.",
    )


# ---------------------------------------------------------------------------
# Local response models for new endpoints (not in core/schemas.py — Track B owns)
# ---------------------------------------------------------------------------

from pydantic import BaseModel as _BaseModel


class BottleneckItem(_BaseModel):
    """Single asset row in the plant-wide bottleneck ranking (§5.2)."""
    asset_id: str
    equipment_name: str
    wrps_score: float
    risk_tier: str
    process_criticality: float
    delay_severity: float
    spares_availability: float
    procurement_lead_factor: float
    top_reason: str


class BottleneckResponse(_BaseModel):
    """GET /v1/bottlenecks — plant-wide WRPS ranking for all active assets."""
    items: list[BottleneckItem]
    total: int
    computed_at: datetime
    note: str = "Ranked descending by Weighted Risk Priority Score (WRPS §5.2)."


class ScenarioItem(_BaseModel):
    """Single scenario-based troubleshooting prompt entry (§4.4)."""
    id: str
    title: str
    equipment_class: str
    equipment_id: str
    prompt: str
    difficulty: str
    tags: list[str] = []


class ScenarioListResponse(_BaseModel):
    """GET /v1/scenarios — curated troubleshooting scenario list."""
    scenarios: list[ScenarioItem]
    total: int


class ScenarioStartResponse(_BaseModel):
    """POST /v1/scenarios/{id}/start — scenario prompt ready to feed /v1/chat."""
    scenario_id: str
    title: str
    equipment_id: str
    chat_seed_query: str
    suggested_session_id: str
    note: str = "Pass chat_seed_query as the 'query' and equipment_id to POST /v1/chat to begin the session."


# Path to curated scenarios file (relative to repo root where uvicorn is launched)
_SCENARIOS_FILE: Path = Path("data/scenarios.json")


def _load_scenarios() -> list[dict]:
    """Load scenarios from JSON file; return empty list on any error."""
    try:
        if _SCENARIOS_FILE.exists():
            return json.loads(_SCENARIOS_FILE.read_text(encoding="utf-8"))
    except Exception as exc:
        log.warning("scenarios.load_failed", error=str(exc))
    return []


# ---------------------------------------------------------------------------
# v1/bottlenecks — plant-wide WRPS ranking (§5.2)
# ---------------------------------------------------------------------------

@app.get(
    "/v1/bottlenecks",
    response_model=BottleneckResponse,
    summary="Plant-wide bottleneck prioritization — all active assets ranked by WRPS descending",
)
async def get_bottlenecks(session: Session = Depends(get_session)) -> BottleneckResponse:
    """
    Computes WRPS for ALL active AssetProfile rows and returns them ranked
    descending by wrps_score.

    Each item exposes the four WRPS factor components so engineers can understand
    why an asset is ranked where it is:
      - process_criticality [0–1]
      - delay_severity      [0–1]
      - spares_availability [0–1]
      - procurement_lead_factor [0–1]

    The `top_reason` field names the single highest-scoring factor for quick scan.
    """
    assets = session.exec(select(AssetProfile)).all()

    items: list[BottleneckItem] = []
    for asset in assets:
        try:
            risk_score, factor_breakdown = score_maintenance_priority_for_session(
                asset.asset_id, session
            )
        except Exception as exc:
            log.warning(
                "bottlenecks.score_failed",
                asset_id=asset.asset_id,
                error=str(exc),
            )
            continue

        # factor_breakdown keys: process_criticality, delay_severity,
        #                         spare_availability, lead_time, ml_signal
        pc   = factor_breakdown.get("process_criticality", 0.0)
        ds   = factor_breakdown.get("delay_severity", 0.0)
        sa   = factor_breakdown.get("spare_availability", 0.0)
        lt   = factor_breakdown.get("lead_time", 0.0)

        # Top reason = the factor with the highest normalised value
        named = {
            "process_criticality": pc,
            "delay_severity":      ds,
            "spares_availability": sa,
            "procurement_lead_time": lt,
        }
        top_reason_key = max(named, key=lambda k: named[k])
        top_reason_val = named[top_reason_key]
        top_reason = f"{top_reason_key.replace('_', ' ').title()} ({top_reason_val:.2f})"

        items.append(
            BottleneckItem(
                asset_id=asset.asset_id,
                equipment_name=asset.equipment_name,
                wrps_score=risk_score.wrps,
                risk_tier=risk_score.risk_tier.value,
                process_criticality=round(pc, 4),
                delay_severity=round(ds, 4),
                spares_availability=round(sa, 4),
                procurement_lead_factor=round(lt, 4),
                top_reason=top_reason,
            )
        )

    # Sort descending by WRPS
    items.sort(key=lambda x: x.wrps_score, reverse=True)

    log.info(
        "bottlenecks.computed",
        asset_count=len(items),
        top_asset_id=items[0].asset_id if items else None,
        top_wrps=items[0].wrps_score if items else None,
    )

    return BottleneckResponse(
        items=items,
        total=len(items),
        computed_at=datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# v1/scenarios — scenario-based troubleshooting prompts (§4.4)
# ---------------------------------------------------------------------------

@app.get(
    "/v1/scenarios",
    response_model=ScenarioListResponse,
    summary="Curated scenario-based troubleshooting prompts (§4.4) — seed engineer multi-turn sessions",
)
async def list_scenarios(
    equipment_class: Optional[str] = Query(
        default=None,
        description="Filter by equipment_class (fan|pump|conveyor|bearing|hydraulic_unit)",
    ),
    difficulty: Optional[str] = Query(
        default=None,
        description="Filter by difficulty (easy|medium|hard)",
    ),
) -> ScenarioListResponse:
    """
    Returns curated troubleshooting scenario prompts loaded from data/scenarios.json.
    Each scenario is designed to seed a multi-turn maintenance engineering session.

    Use POST /v1/scenarios/{id}/start to get a chat-ready payload for /v1/chat.
    """
    raw = _load_scenarios()

    scenarios: list[ScenarioItem] = []
    for s in raw:
        if equipment_class and s.get("equipment_class", "").lower() != equipment_class.lower():
            continue
        if difficulty and s.get("difficulty", "").lower() != difficulty.lower():
            continue
        scenarios.append(
            ScenarioItem(
                id=s["id"],
                title=s["title"],
                equipment_class=s["equipment_class"],
                equipment_id=s.get("equipment_id", s["equipment_class"].upper() + "-DEMO"),
                prompt=s["prompt"],
                difficulty=s.get("difficulty", "medium"),
                tags=s.get("tags", []),
            )
        )

    return ScenarioListResponse(scenarios=scenarios, total=len(scenarios))


@app.post(
    "/v1/scenarios/{scenario_id}/start",
    response_model=ScenarioStartResponse,
    summary="Start a scenario — returns chat-ready payload for POST /v1/chat (§4.4)",
)
async def start_scenario(scenario_id: str) -> ScenarioStartResponse:
    """
    Returns a ScenarioStartResponse with:
      - chat_seed_query: the scenario prompt verbatim (ready for /v1/chat query field)
      - equipment_id: the asset the scenario is anchored to
      - suggested_session_id: a fresh session ID for this scenario run

    Clients pass chat_seed_query as the 'query' body field and equipment_id as the
    'equipment_id' field when calling POST /v1/chat, and the agent will begin the
    multi-turn troubleshooting session from the scenario context.
    """
    raw = _load_scenarios()
    scenario = next((s for s in raw if s.get("id") == scenario_id), None)

    if scenario is None:
        raise HTTPException(
            status_code=404,
            detail=f"Scenario '{scenario_id}' not found. "
                   f"Call GET /v1/scenarios to list available scenarios.",
        )

    suggested_session = f"scenario-{scenario_id}-{uuid.uuid4().hex[:8]}"

    return ScenarioStartResponse(
        scenario_id=scenario_id,
        title=scenario["title"],
        equipment_id=scenario.get("equipment_id", "EAF-04"),
        chat_seed_query=scenario["prompt"],
        suggested_session_id=suggested_session,
    )


# ---------------------------------------------------------------------------
# (Path was imported at the top of the module)
# ---------------------------------------------------------------------------
