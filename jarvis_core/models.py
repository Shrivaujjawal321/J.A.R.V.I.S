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

    schema_version: int = 2  # bumped: added goals + approvals
    saved_at: datetime = Field(default_factory=datetime.utcnow)
    conversations: dict[str, ConversationState] = Field(default_factory=dict)
    tasks: dict[str, TaskRecord] = Field(default_factory=dict)
    goals: dict[str, "GoalRecord"] = Field(default_factory=dict)
    approvals: dict[str, "ApprovalRequest"] = Field(default_factory=dict)

    # Free-form metadata for future use without schema migration
    meta: dict[str, Any] = Field(default_factory=dict)


# === Autonomous goal pursuit (Phase 3) ===


class GoalStatus(str, Enum):
    QUEUED = "queued"               # Created, not yet picked by scheduler
    PLANNING = "planning"           # Decomposer is breaking it into sub-tasks
    RUNNING = "running"             # Workers executing sub-tasks
    AWAITING_APPROVAL = "awaiting_approval"  # Tier-3 sub-task needs Boss's nod
    COMPLETED = "completed"         # All sub-tasks finished (with/without success)
    FAILED = "failed"               # Error, cooldown, or budget exhausted
    CANCELLED = "cancelled"         # Boss explicitly cancelled


class SubTaskRecord(BaseModel):
    """One unit of work inside a goal (1:1 with a WorkerSpec at execution time)."""

    sub_id: str
    label: str
    prompt: str                     # The actual prompt fed to Claude
    tier: int = 1                   # 1 = auto, 2 = auto+log, 3 = needs approval
    output: str | None = None
    error: str | None = None
    cost_usd: float | None = None
    duration_ms: int | None = None
    completed_at: datetime | None = None
    # If tier==3 and not yet approved, this links to the ApprovalRequest:
    approval_id: str | None = None


class GoalRecord(BaseModel):
    """A long-running goal Jarvis pursues autonomously while Boss is offline."""

    goal_id: str
    user_id: str
    description: str                # What Boss asked for, plain English
    status: GoalStatus = GoalStatus.QUEUED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # Decomposition output (1 level only — no recursive sub-goals)
    sub_tasks: list[SubTaskRecord] = Field(default_factory=list)
    plan_summary: str | None = None  # One-liner from decomposer explaining the plan

    # Limits (per-goal safety rails)
    max_budget_usd: float = 5.0     # Hard cap on Claude spend
    max_duration_seconds: int = 7200  # 2 hours default
    cost_usd_total: float = 0.0

    # Final synthesis
    final_output: str | None = None
    error: str | None = None

    # Free-form context (e.g. {"platform": "linkedin", "max_apply": 3})
    context: dict[str, Any] = Field(default_factory=dict)

    def is_terminal(self) -> bool:
        return self.status in (GoalStatus.COMPLETED, GoalStatus.FAILED, GoalStatus.CANCELLED)

    def to_view(self) -> "GoalStateView":
        return GoalStateView(
            goal_id=self.goal_id,
            description=self.description,
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at,
            started_at=self.started_at,
            completed_at=self.completed_at,
            sub_task_count=len(self.sub_tasks),
            sub_tasks_done=sum(1 for s in self.sub_tasks if s.completed_at is not None),
            cost_usd_total=self.cost_usd_total,
            plan_summary=self.plan_summary,
            final_output_present=self.final_output is not None,
            error=self.error,
        )


class GoalStateView(BaseModel):
    """External view of a goal (for HTTP responses)."""

    goal_id: str
    description: str
    status: GoalStatus
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    sub_task_count: int
    sub_tasks_done: int
    cost_usd_total: float
    plan_summary: str | None = None
    final_output_present: bool = False
    error: str | None = None


class ApprovalDecision(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"  # No response within decision_deadline


class ApprovalRequest(BaseModel):
    """A Tier-3 action a goal wants to perform — gated on Boss's morning nod."""

    approval_id: str
    goal_id: str
    sub_id: str
    action_summary: str             # Plain-English: "Apply to LinkedIn job: ML Eng @ Acme"
    action_payload: dict[str, Any]  # Whatever the executor needs to act on approval
    risk_notes: list[str] = Field(default_factory=list)  # "Irreversible", "External recipient", etc.
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    decision_deadline: datetime | None = None  # Default 24h from request
    decision: ApprovalDecision = ApprovalDecision.PENDING
    decided_at: datetime | None = None
    decided_by: str | None = None
    boss_note: str | None = None    # Free-text from Boss on decision


# Resolve forward references for JarvisStateSnapshot (Pydantic v2)
JarvisStateSnapshot.model_rebuild()
