"""
wizard.backend.schemas
======================
API-level request/response models for the FastAPI backend.

These are NOT entity models (those live in wizard.core.schemas).
They define the HTTP envelope shapes for each endpoint.
All error responses use the Stripe-style ErrorEnvelope.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from wizard.core.schemas import AlertSeverity, MaintenanceRecommendation


# ---------------------------------------------------------------------------
# Error envelope (Stripe-style)
# ---------------------------------------------------------------------------

class ErrorCode(str, enum.Enum):
    """Machine-readable error codes returned in every 4xx/5xx response."""
    # Validation
    INVALID_REQUEST = "INVALID_REQUEST"
    MISSING_FIELD = "MISSING_FIELD"
    # Auth
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    # Resource
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    ASSET_NOT_FOUND = "ASSET_NOT_FOUND"
    ALERT_NOT_FOUND = "ALERT_NOT_FOUND"
    # Upstream / LLM
    LLM_UNAVAILABLE = "LLM_UNAVAILABLE"
    LLM_CIRCUIT_OPEN = "LLM_CIRCUIT_OPEN"
    LLM_TIMEOUT = "LLM_TIMEOUT"
    # Rate limiting
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    # Server
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DB_ERROR = "DB_ERROR"


class ErrorDetail(BaseModel):
    """Structured error detail — never exposes stack traces or secrets."""
    code: ErrorCode
    message: str
    type: Literal["validation", "auth", "server", "upstream", "rate_limit"]
    request_id: str
    doc_url: Optional[str] = None


class ErrorEnvelope(BaseModel):
    """Top-level error envelope wrapping every 4xx/5xx response."""
    error: ErrorDetail


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    """POST /v1/chat — synchronous or streaming chat request."""
    session_id: str = Field(
        description="Client-managed session ID; LangGraph thread_id for checkpoint"
    )
    equipment_id: str = Field(
        description="Asset ID (FK → AssetProfile.asset_id), e.g. 'EAF-04'"
    )
    query: str = Field(
        min_length=1,
        max_length=2000,
        description="Engineer's natural-language query",
    )
    idempotency_key: Optional[str] = Field(
        default=None,
        description="Optional: re-send same key → return cached response, no duplicate run",
    )


class AgentStepEvent(BaseModel):
    """Single SSE event emitted during chat streaming (matches LangGraph astream chunks)."""
    event_type: Literal[
        "agent_step",
        "tool_call",
        "token",
        "risk_update",
        "recommendation_ready",
        "alert",
        "error",
        "done",
    ]
    session_id: str
    equipment_id: Optional[str] = None
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp_utc: str = Field(
        description="ISO 8601 timestamp"
    )
    source_node: Optional[str] = Field(
        default=None,
        description="LangGraph node name for explainability traces",
    )


class ChatResponse(BaseModel):
    """POST /v1/chat — synchronous response envelope."""
    session_id: str
    equipment_id: str
    recommendation: MaintenanceRecommendation
    agent_trace: list[dict[str, Any]] = Field(default_factory=list)
    latency_ms: float


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------

class FeedbackRequest(BaseModel):
    """POST /v1/feedback — engineer correction on a recommendation."""
    session_id: str
    equipment_id: str
    recommendation_id: str
    thumbs_up: bool
    correction: Optional[str] = Field(
        default=None,
        description="Free-text correction from engineer",
    )
    corrected_risk_level: Optional[AlertSeverity] = Field(
        default=None,
        description="If engineer disagrees with risk tier, provide correct tier",
    )


class FeedbackResponse(BaseModel):
    """POST /v1/feedback — confirmation."""
    feedback_id: str
    weights_updated: bool
    message: str


# ---------------------------------------------------------------------------
# Sensor state
# ---------------------------------------------------------------------------

class AssetSensorState(BaseModel):
    """Sensor state snapshot for a single asset."""
    asset_id: str
    equipment_name: str
    criticality_tier: str
    latest_sensor_readings: dict[str, Optional[float]] = Field(default_factory=dict)
    anomaly_score: Optional[float] = None
    rul_days_p50: Optional[float] = None
    active_alert_count: int = 0
    last_updated: Optional[datetime] = None


class SensorStateResponse(BaseModel):
    """GET /v1/sensor/state — all asset sensor snapshots."""
    assets: list[AssetSensorState] = Field(default_factory=list)
    total_assets: int
    critical_asset_count: int
    retrieved_at: datetime


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

class SessionStateResponse(BaseModel):
    """GET /v1/session/{id}/state — LangGraph checkpoint state for explainability."""
    session_id: str
    state: dict[str, Any] = Field(
        default_factory=dict,
        description="Full MaintenanceState dict from LangGraph SqliteSaver checkpoint",
    )
    checkpoint_at: Optional[datetime] = None
    note: Optional[str] = Field(
        default=None,
        description="Present when graph is not yet wired (placeholder mode)",
    )


# ---------------------------------------------------------------------------
# Alerts REST
# ---------------------------------------------------------------------------

class AlertAckResponse(BaseModel):
    """POST /v1/alerts/{id}/ack — acknowledgement confirmation."""
    alert_entity_id: str
    acknowledged: bool
    acknowledged_by: str
    message: str


class AlertListItem(BaseModel):
    """Single item in GET /v1/alerts paginated list."""
    alert_entity_id: str
    asset_id: str
    equipment_name: str
    alert_type: str
    risk_level: str
    description: str
    triggered_at: datetime
    acknowledged: bool
    cooldown_key: Optional[str] = None
    estimated_rul_days: Optional[float] = None


class AlertListResponse(BaseModel):
    """GET /v1/alerts — cursor-paginated alert history."""
    items: list[AlertListItem] = Field(default_factory=list)
    total: int
    next_cursor: Optional[str] = Field(
        default=None,
        description="Opaque cursor for the next page; absent when no more pages",
    )


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    """GET /v1/health — liveness probe + subsystem status."""
    status: Literal["ok", "degraded", "error"]
    db_ok: bool
    scheduler_running: bool
    circuit_breaker_state: str = Field(
        description="'closed' | 'open' | 'half_open'"
    )
    alert_broadcaster_clients: int
    version: str = "1.0.0"
    uptime_seconds: float
    checked_at: datetime
