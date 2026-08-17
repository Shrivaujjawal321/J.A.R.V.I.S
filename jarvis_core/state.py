"""
In-memory conversation + task state with periodic disk persistence.

State lives in RAM during daemon lifetime. Every SYNC_INTERVAL seconds
(and on shutdown) the full state is serialized to STATE_PATH as JSON.
On startup, prior state is restored if present.

Thread/coroutine safety: a single asyncio.Lock guards all mutations.
"""
from __future__ import annotations

import asyncio
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path

from .models import (
    ApprovalDecision,
    ApprovalRequest,
    ConversationState,
    GoalRecord,
    GoalStatus,
    JarvisStateSnapshot,
    SubTaskRecord,
    TaskRecord,
    TaskStatus,
    WorkerResult,
)

log = logging.getLogger("jarvis_core.state")


class JarvisState:
    """Thread-safe in-memory state with periodic disk sync."""

    def __init__(self, state_path: Path, sync_interval_seconds: int = 300):
        self.state_path = state_path
        self.sync_interval = sync_interval_seconds
        self._lock = asyncio.Lock()
        self._conversations: dict[str, ConversationState] = {}
        self._tasks: dict[str, TaskRecord] = {}
        self._goals: dict[str, GoalRecord] = {}
        self._approvals: dict[str, ApprovalRequest] = {}
        # AuditAgent state — stored additively, survives restarts via meta["audits"]
        self._audits: dict = {}  # dict[str, AuditRun] — typed at runtime
        self._sync_task: asyncio.Task | None = None
        self._stopped = False

    # === Lifecycle ===

    def load_from_disk(self) -> None:
        """Restore state from disk on startup. Safe to call before event loop."""
        if not self.state_path.exists():
            log.info("No prior state at %s — starting fresh", self.state_path)
            return
        try:
            raw = json.loads(self.state_path.read_text())
            snapshot = JarvisStateSnapshot.model_validate(raw)
            self._conversations = snapshot.conversations
            self._tasks = snapshot.tasks
            self._goals = snapshot.goals
            self._approvals = snapshot.approvals
            # On restart, any RUNNING tasks are actually orphaned — mark failed
            for task in self._tasks.values():
                if task.status == TaskStatus.RUNNING:
                    task.status = TaskStatus.FAILED
                    task.error = "Daemon restarted while task was running"
                    task.updated_at = datetime.utcnow()
            # Similarly, any RUNNING/PLANNING goals are orphaned — re-queue them
            # (idempotent: scheduler picks them up on next tick)
            for goal in self._goals.values():
                if goal.status in (GoalStatus.RUNNING, GoalStatus.PLANNING):
                    goal.status = GoalStatus.QUEUED
                    goal.updated_at = datetime.utcnow()
            # Restore AuditRun state from meta["audits"] — additive, default {}
            self._restore_audits(snapshot.meta.get("audits", {}))
            log.info(
                "Restored state from %s (%d conversations, %d tasks, %d goals, "
                "%d approvals, %d audits)",
                self.state_path,
                len(self._conversations),
                len(self._tasks),
                len(self._goals),
                len(self._approvals),
                len(self._audits),
            )
        except Exception as e:
            log.exception("Failed to load state from %s: %s — starting fresh", self.state_path, e)

    def _restore_audits(self, raw_audits: dict) -> None:
        """Deserialize AuditRun objects from the meta["audits"] snapshot dict."""
        if not raw_audits:
            return
        try:
            from jarvis_core.audit_agent.models import AuditRun
            for audit_id, audit_data in raw_audits.items():
                try:
                    self._audits[audit_id] = AuditRun.model_validate(audit_data)
                except Exception as exc:
                    log.warning("Could not restore audit %s: %s", audit_id, exc)
        except ImportError:
            log.debug("audit_agent not available — skipping audit restore")

    async def start_background_sync(self) -> None:
        """Spawn the periodic disk-sync task."""
        if self._sync_task is not None:
            return
        self._sync_task = asyncio.create_task(self._sync_loop(), name="jarvis-state-sync")

    async def stop(self) -> None:
        """Cancel sync task + write final snapshot."""
        self._stopped = True
        if self._sync_task is not None:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
        await self.sync_to_disk()

    async def _sync_loop(self) -> None:
        while not self._stopped:
            try:
                await asyncio.sleep(self.sync_interval)
                await self.sync_to_disk()
            except asyncio.CancelledError:
                raise
            except Exception:
                log.exception("Periodic disk sync failed; will retry")

    async def sync_to_disk(self) -> None:
        """Snapshot state to disk atomically (write to tmp + rename)."""
        async with self._lock:
            # Serialize audit runs into meta["audits"] for backward-compat storage
            audits_raw: dict = {}
            for audit_id, audit_run in self._audits.items():
                try:
                    audits_raw[audit_id] = json.loads(audit_run.model_dump_json())
                except Exception:
                    pass  # Skip broken audit — don't crash the sync
            snapshot = JarvisStateSnapshot(
                conversations=self._conversations,
                tasks=self._tasks,
                goals=self._goals,
                approvals=self._approvals,
                meta={"audits": audits_raw},
            )
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.state_path.with_suffix(".tmp")
            tmp.write_text(snapshot.model_dump_json(indent=2))
            tmp.replace(self.state_path)
            log.debug("State synced to %s", self.state_path)
        except Exception:
            log.exception("Failed to write state snapshot")

    # === Conversation accessors ===

    async def get_or_create_conversation(self, user_id: str) -> ConversationState:
        async with self._lock:
            conv = self._conversations.get(user_id)
            if conv is None:
                conv = ConversationState(user_id=user_id)
                self._conversations[user_id] = conv
            return conv

    async def update_conversation(
        self,
        user_id: str,
        session_id: str | None = None,
        cost_delta: float = 0.0,
    ) -> ConversationState:
        async with self._lock:
            conv = self._conversations.get(user_id) or ConversationState(user_id=user_id)
            if session_id is not None:
                conv.last_session_id = session_id
            conv.last_active = datetime.utcnow()
            conv.message_count += 1
            conv.cost_usd_total += cost_delta
            self._conversations[user_id] = conv
            return conv

    async def clear_session(self, user_id: str) -> None:
        """Forget the prior session_id for a user (start a fresh thread)."""
        async with self._lock:
            conv = self._conversations.get(user_id)
            if conv is not None:
                conv.last_session_id = None

    # === Task accessors ===

    async def create_task(self, record: TaskRecord) -> TaskRecord:
        async with self._lock:
            if not record.task_id:
                record.task_id = uuid.uuid4().hex[:12]
            self._tasks[record.task_id] = record
            return record

    async def get_task(self, task_id: str) -> TaskRecord | None:
        async with self._lock:
            return self._tasks.get(task_id)

    async def update_task(
        self,
        task_id: str,
        *,
        status: TaskStatus | None = None,
        worker_result: WorkerResult | None = None,
        final_output: str | None = None,
        error: str | None = None,
        cost_delta: float = 0.0,
    ) -> TaskRecord | None:
        async with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            if status is not None:
                task.status = status
            if worker_result is not None:
                task.results.append(worker_result)
            if final_output is not None:
                task.final_output = final_output
            if error is not None:
                task.error = error
            task.cost_usd_total += cost_delta
            task.updated_at = datetime.utcnow()
            return task

    async def list_recent_tasks(self, limit: int = 20) -> list[TaskRecord]:
        async with self._lock:
            tasks = sorted(self._tasks.values(), key=lambda t: t.updated_at, reverse=True)
            return tasks[:limit]

    # === Goal accessors (Phase 3) ===

    async def add_goal(self, goal: GoalRecord) -> GoalRecord:
        async with self._lock:
            if not goal.goal_id:
                goal.goal_id = uuid.uuid4().hex[:12]
            self._goals[goal.goal_id] = goal
            return goal

    async def get_goal(self, goal_id: str) -> GoalRecord | None:
        async with self._lock:
            return self._goals.get(goal_id)

    async def list_goals(
        self,
        *,
        status: GoalStatus | None = None,
        limit: int = 50,
    ) -> list[GoalRecord]:
        async with self._lock:
            goals = list(self._goals.values())
        if status is not None:
            goals = [g for g in goals if g.status == status]
        goals.sort(key=lambda g: g.updated_at, reverse=True)
        return goals[:limit]

    async def update_goal(
        self,
        goal_id: str,
        *,
        status: GoalStatus | None = None,
        sub_tasks: list[SubTaskRecord] | None = None,
        sub_task_update: SubTaskRecord | None = None,
        plan_summary: str | None = None,
        final_output: str | None = None,
        error: str | None = None,
        cost_delta: float = 0.0,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
    ) -> GoalRecord | None:
        async with self._lock:
            goal = self._goals.get(goal_id)
            if goal is None:
                return None
            if status is not None:
                goal.status = status
            if sub_tasks is not None:
                goal.sub_tasks = sub_tasks
            if sub_task_update is not None:
                # Replace the sub-task with matching sub_id (or append)
                replaced = False
                for i, s in enumerate(goal.sub_tasks):
                    if s.sub_id == sub_task_update.sub_id:
                        goal.sub_tasks[i] = sub_task_update
                        replaced = True
                        break
                if not replaced:
                    goal.sub_tasks.append(sub_task_update)
            if plan_summary is not None:
                goal.plan_summary = plan_summary
            if final_output is not None:
                goal.final_output = final_output
            if error is not None:
                goal.error = error
            goal.cost_usd_total += cost_delta
            if started_at is not None:
                goal.started_at = started_at
            if completed_at is not None:
                goal.completed_at = completed_at
            goal.updated_at = datetime.utcnow()
            return goal

    async def cancel_goal(self, goal_id: str, reason: str | None = None) -> GoalRecord | None:
        return await self.update_goal(
            goal_id,
            status=GoalStatus.CANCELLED,
            error=reason or "Cancelled by Boss",
            completed_at=datetime.utcnow(),
        )

    # === Approval accessors ===

    async def add_approval(self, approval: ApprovalRequest) -> ApprovalRequest:
        async with self._lock:
            if not approval.approval_id:
                approval.approval_id = uuid.uuid4().hex[:12]
            self._approvals[approval.approval_id] = approval
            return approval

    async def get_approval(self, approval_id: str) -> ApprovalRequest | None:
        async with self._lock:
            return self._approvals.get(approval_id)

    async def list_pending_approvals(self) -> list[ApprovalRequest]:
        async with self._lock:
            return [a for a in self._approvals.values() if a.decision == ApprovalDecision.PENDING]

    async def decide_approval(
        self,
        approval_id: str,
        decision: ApprovalDecision,
        *,
        boss_note: str | None = None,
        decided_by: str = "ujjwal",
    ) -> ApprovalRequest | None:
        async with self._lock:
            approval = self._approvals.get(approval_id)
            if approval is None:
                return None
            approval.decision = decision
            approval.decided_at = datetime.utcnow()
            approval.decided_by = decided_by
            approval.boss_note = boss_note
            return approval

    # === Audit accessors (AuditAgent — additive, no breaking changes) ===

    async def add_audit(self, audit_run: object) -> object:
        """Store a new AuditRun."""
        async with self._lock:
            self._audits[audit_run.audit_id] = audit_run
            return audit_run

    async def get_audit(self, audit_id: str) -> object | None:
        async with self._lock:
            return self._audits.get(audit_id)

    async def list_audits(self, limit: int = 50) -> list:
        async with self._lock:
            audits = list(self._audits.values())
        audits.sort(key=lambda a: a.updated_at, reverse=True)
        return audits[:limit]

    # === Debug / introspection ===

    async def stats(self) -> dict[str, int | float]:
        async with self._lock:
            return {
                "conversations": len(self._conversations),
                "tasks_total": len(self._tasks),
                "tasks_running": sum(1 for t in self._tasks.values() if t.status == TaskStatus.RUNNING),
                "goals_total": len(self._goals),
                "goals_active": sum(
                    1
                    for g in self._goals.values()
                    if g.status in (GoalStatus.QUEUED, GoalStatus.PLANNING, GoalStatus.RUNNING)
                ),
                "goals_awaiting_approval": sum(
                    1 for g in self._goals.values() if g.status == GoalStatus.AWAITING_APPROVAL
                ),
                "approvals_pending": sum(
                    1 for a in self._approvals.values() if a.decision == ApprovalDecision.PENDING
                ),
                "audits_total": len(self._audits),
                "cost_usd_total": sum(c.cost_usd_total for c in self._conversations.values())
                + sum(g.cost_usd_total for g in self._goals.values()),
            }
