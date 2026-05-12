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
    ConversationState,
    JarvisStateSnapshot,
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
            # On restart, any RUNNING tasks are actually orphaned — mark failed
            for task in self._tasks.values():
                if task.status == TaskStatus.RUNNING:
                    task.status = TaskStatus.FAILED
                    task.error = "Daemon restarted while task was running"
                    task.updated_at = datetime.utcnow()
            log.info(
                "Restored state from %s (%d conversations, %d tasks)",
                self.state_path,
                len(self._conversations),
                len(self._tasks),
            )
        except Exception as e:
            log.exception("Failed to load state from %s: %s — starting fresh", self.state_path, e)

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
            snapshot = JarvisStateSnapshot(
                conversations=self._conversations,
                tasks=self._tasks,
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

    # === Debug / introspection ===

    async def stats(self) -> dict[str, int | float]:
        async with self._lock:
            return {
                "conversations": len(self._conversations),
                "tasks_total": len(self._tasks),
                "tasks_running": sum(1 for t in self._tasks.values() if t.status == TaskStatus.RUNNING),
                "cost_usd_total": sum(c.cost_usd_total for c in self._conversations.values()),
            }
