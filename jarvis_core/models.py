"""Pydantic schemas for jarvis-core HTTP API + internal state."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# === HTTP Request / Response models ===


class ChatRequest(BaseModel):
    """Sync single-worker chat request (Telegram-style)."""

    user_id: str = Field(..., description="Stable per-user identifier (e.g. Telegram user_id)")
    message: str = Field(..., min_length=1, max_length=20_000)
    resume_session: bool = Field(
        default=True,
        description="If True, continue prior Claude session for this user (multi-turn).",
    )
    max_turns: int = Field(default=15, ge=1, le=50)


class ChatResponse(BaseModel):
    """Sync chat response."""

    reply: str
    session_id: str | None = None
    cost_usd: float | None = None
    duration_ms: int | None = None
    error: str | None = None


class WorkerSpec(BaseModel):
    """One worker in a parallel-task fan-out."""

    label: str = Field(..., description="Human-readable label, e.g. 'research'")
    prompt: str = Field(..., min_length=1)
    allowed_tools: list[str] | None = None
    max_turns: int = Field(default=10, ge=1, le=30)


class TaskRequest(BaseModel):
    """Async parallel-workers task request."""

    user_id: str
    title: str = Field(..., description="Task title for status display")
    workers: list[WorkerSpec] = Field(..., min_length=1, max_length=8)
    aggregator_prompt: str | None = Field(
        default=None,
        description=(
            "Optional final aggregation step. If set, after all workers complete, "
            "a single Claude call summarizes their outputs using this prompt."
        ),
    )


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskStateView(BaseModel):
    """External view of a task's current state."""

    task_id: str
    title: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    worker_count: int
    workers_done: int
    final_output: str | None = None
    error: str | None = None
    cost_usd_total: float | None = None


# === Internal state models (persisted to disk) ===


class ConversationState(BaseModel):
    """Per-user conversation state."""

    user_id: str
    last_session_id: str | None = None
    last_active: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = 0
    cost_usd_total: float = 0.0


class WorkerResult(BaseModel):
    """Output of one worker in a parallel task."""

    label: str
    output: str
    cost_usd: float | None = None
    duration_ms: int | None = None
    error: str | None = None


class TaskRecord(BaseModel):
    """Internal record of a task (in-memory + persisted)."""

    task_id: str
    user_id: str
    title: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    workers: list[WorkerSpec]
    results: list[WorkerResult] = Field(default_factory=list)
    aggregator_prompt: str | None = None
    final_output: str | None = None
    error: str | None = None
    cost_usd_total: float = 0.0

    def to_view(self) -> TaskStateView:
        return TaskStateView(
            task_id=self.task_id,
            title=self.title,
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at,
            worker_count=len(self.workers),
            workers_done=len(self.results),
            final_output=self.final_output,
            error=self.error,
            cost_usd_total=self.cost_usd_total,
        )


class JarvisStateSnapshot(BaseModel):
    """Full daemon state persisted to disk every 5 min + on shutdown."""

    schema_version: int = 1
    saved_at: datetime = Field(default_factory=datetime.utcnow)
    conversations: dict[str, ConversationState] = Field(default_factory=dict)
    tasks: dict[str, TaskRecord] = Field(default_factory=dict)

    # Free-form metadata for future use without schema migration
    meta: dict[str, Any] = Field(default_factory=dict)
