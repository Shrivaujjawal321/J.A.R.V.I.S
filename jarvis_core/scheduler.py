"""
Background goal-execution scheduler.

A long-running asyncio task that polls the goal queue every POLL_INTERVAL_SECONDS,
picks the oldest QUEUED goal, decomposes it, executes its sub-tasks in parallel,
collects results, and updates state.

Safety rails enforced here:
- Per-goal max_budget_usd cap (default $5)
- Per-goal max_duration_seconds cap (default 7200 = 2h)
- Tier-3 sub-tasks NEVER auto-execute — they create ApprovalRequest entries and
  pause the goal in AWAITING_APPROVAL until Boss decides via /approval/{id}/decide.
- Concurrent goal limit (default 1) — keeps quota usage bounded.
"""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from datetime import datetime
from pathlib import Path

from .decomposer import decompose_goal, plan_to_sub_tasks
from .models import (
    ApprovalDecision,
    ApprovalRequest,
    GoalRecord,
    GoalStatus,
    SubTaskRecord,
)
from .orchestrator import run_worker
from .state import JarvisState

log = logging.getLogger("jarvis_core.scheduler")


class GoalScheduler:
    """Background loop: pick QUEUED goal → decompose → execute → finalize."""

    def __init__(
        self,
        state: JarvisState,
        project_root: Path,
        *,
        poll_interval_seconds: int = 60,
        max_concurrent_goals: int = 1,
    ):
        self.state = state
        self.project_root = project_root
        self.poll_interval = poll_interval_seconds
        self.max_concurrent_goals = max_concurrent_goals
        self._task: asyncio.Task | None = None
        self._stopped = False
        self._active_runs: set[str] = set()

    async def start(self) -> None:
        if self._task is not None:
            return
        self._task = asyncio.create_task(self._loop(), name="goal-scheduler")

    async def stop(self) -> None:
        self._stopped = True
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _loop(self) -> None:
        """Polling loop — wake up, dispatch ready goals, sleep."""
        log.info("Goal scheduler started (poll=%ds, max_concurrent=%d)", self.poll_interval, self.max_concurrent_goals)
        while not self._stopped:
            try:
                await self._tick()
            except asyncio.CancelledError:
                raise
            except Exception:
                log.exception("Scheduler tick raised; will retry next interval")
            try:
                await asyncio.sleep(self.poll_interval)
            except asyncio.CancelledError:
                break

    async def _tick(self) -> None:
        """One iteration: dispatch ready goals if capacity allows."""
        if len(self._active_runs) >= self.max_concurrent_goals:
            return

        queued = await self.state.list_goals(status=GoalStatus.QUEUED, limit=10)
        if not queued:
            return

        # Pick oldest queued goal that isn't already being processed
        for goal in reversed(queued):  # oldest first (list_goals returns most-recent-first)
            if goal.goal_id in self._active_runs:
                continue
            self._active_runs.add(goal.goal_id)
            asyncio.create_task(
                self._run_goal(goal.goal_id),
                name=f"goal-run-{goal.goal_id}",
            )
            log.info("Dispatched goal %s: %s", goal.goal_id, goal.description[:80])
            break  # one goal per tick — re-evaluate next tick

    async def _run_goal(self, goal_id: str) -> None:
        """Execute one goal end-to-end. Updates state throughout."""
        try:
            await self._run_goal_inner(goal_id)
        finally:
            self._active_runs.discard(goal_id)

    async def _run_goal_inner(self, goal_id: str) -> None:
        goal = await self.state.get_goal(goal_id)
        if goal is None:
            log.error("Goal %s vanished before run", goal_id)
            return

        start_ts = time.perf_counter()
        await self.state.update_goal(
            goal_id, status=GoalStatus.PLANNING, started_at=datetime.utcnow()
        )

        # --- 1. Decompose ---
        decomp = await decompose_goal(goal, project_root=self.project_root)
        if decomp.cost_usd:
            await self.state.update_goal(goal_id, cost_delta=decomp.cost_usd)

        if decomp.plan is None or decomp.error:
            err = decomp.error or "Decomposer returned no plan"
            log.warning("Goal %s decomposition failed: %s", goal_id, err)
            await self.state.update_goal(
                goal_id,
                status=GoalStatus.FAILED,
                error=err,
                completed_at=datetime.utcnow(),
            )
            return

        # Refusal case: planner returned plan_summary starting with REFUSED:
        if decomp.plan.plan_summary.startswith("REFUSED:") or not decomp.plan.sub_tasks:
            await self.state.update_goal(
                goal_id,
                status=GoalStatus.FAILED,
                error=decomp.plan.plan_summary,
                plan_summary=decomp.plan.plan_summary,
                completed_at=datetime.utcnow(),
            )
            log.info("Goal %s refused by planner: %s", goal_id, decomp.plan.plan_summary)
            return

        sub_tasks = plan_to_sub_tasks(decomp.plan)
        await self.state.update_goal(
            goal_id,
            sub_tasks=sub_tasks,
            plan_summary=decomp.plan.plan_summary,
            status=GoalStatus.RUNNING,
        )
        log.info(
            "Goal %s planned: %d sub-tasks (T1=%d, T2=%d, T3=%d)",
            goal_id,
            len(sub_tasks),
            sum(1 for s in sub_tasks if s.tier == 1),
            sum(1 for s in sub_tasks if s.tier == 2),
            sum(1 for s in sub_tasks if s.tier == 3),
        )

        # --- 2. Execute sub-tasks ---
        # Tier 1+2 sub-tasks: run in parallel
        # Tier 3 sub-tasks: create ApprovalRequest (do NOT execute)
        auto_subs = [s for s in sub_tasks if s.tier in (1, 2)]
        gated_subs = [s for s in sub_tasks if s.tier == 3]

        # Reload goal for budget/duration tracking
        goal = await self.state.get_goal(goal_id)
        if goal is None:
            return

        # --- Execute auto sub-tasks in parallel ---
        if auto_subs:
            results = await asyncio.gather(
                *(self._execute_sub(goal_id, s, goal.max_budget_usd) for s in auto_subs),
                return_exceptions=True,
            )
            for sub, result in zip(auto_subs, results):
                if isinstance(result, Exception):
                    log.exception("Sub-task %s/%s raised: %s", goal_id, sub.sub_id, result)

        # Check budget after auto sub-tasks
        goal = await self.state.get_goal(goal_id)
        if goal is None:
            return
        if goal.cost_usd_total > goal.max_budget_usd:
            await self.state.update_goal(
                goal_id,
                status=GoalStatus.FAILED,
                error=f"Budget exhausted ({goal.cost_usd_total:.2f} > {goal.max_budget_usd:.2f})",
                completed_at=datetime.utcnow(),
            )
            log.warning("Goal %s halted: budget exhausted", goal_id)
            return

        # Check duration cap
        elapsed = time.perf_counter() - start_ts
        if elapsed > goal.max_duration_seconds:
            await self.state.update_goal(
                goal_id,
                status=GoalStatus.FAILED,
                error=f"Duration cap exceeded ({elapsed:.0f}s > {goal.max_duration_seconds}s)",
                completed_at=datetime.utcnow(),
            )
            return

        # --- Stage Tier-3 approvals ---
        if gated_subs:
            for sub in gated_subs:
                approval = ApprovalRequest(
                    approval_id=uuid.uuid4().hex[:12],
                    goal_id=goal_id,
                    sub_id=sub.sub_id,
                    action_summary=sub.label,
                    action_payload={"prompt": sub.prompt},
                    risk_notes=["Tier-3 action — irreversible or externally visible"],
                )
                await self.state.add_approval(approval)
                sub.approval_id = approval.approval_id
                await self.state.update_goal(goal_id, sub_task_update=sub)
            await self.state.update_goal(
                goal_id,
                status=GoalStatus.AWAITING_APPROVAL,
            )
            log.info("Goal %s staged %d Tier-3 approvals", goal_id, len(gated_subs))
            return

        # --- 3. Finalize ---
        goal = await self.state.get_goal(goal_id)
        if goal is None:
            return
        synthesis = self._synthesize_final(goal)
        await self.state.update_goal(
            goal_id,
            status=GoalStatus.COMPLETED,
            final_output=synthesis,
            completed_at=datetime.utcnow(),
        )
        log.info(
            "Goal %s COMPLETED in %.1fs (cost=$%.4f, %d sub-tasks)",
            goal_id,
            elapsed,
            goal.cost_usd_total,
            len(goal.sub_tasks),
        )

    async def _execute_sub(
        self, goal_id: str, sub: SubTaskRecord, budget_cap: float
    ) -> None:
        """Run one Tier-1/Tier-2 sub-task and persist its result."""
        outcome = await run_worker(
            sub.prompt,
            project_root=self.project_root,
            max_turns=15,
            timeout_seconds=600,
        )
        updated = SubTaskRecord(
            sub_id=sub.sub_id,
            label=sub.label,
            prompt=sub.prompt,
            tier=sub.tier,
            output=outcome.text,
            error=outcome.error,
            cost_usd=outcome.cost_usd,
            duration_ms=outcome.duration_ms,
            completed_at=datetime.utcnow(),
        )
        await self.state.update_goal(
            goal_id,
            sub_task_update=updated,
            cost_delta=outcome.cost_usd or 0.0,
        )

    @staticmethod
    def _synthesize_final(goal: GoalRecord) -> str:
        """Concat sub-task outputs into a goal-level final output."""
        sections: list[str] = [
            f"# Goal: {goal.description}",
            "",
            f"**Plan:** {goal.plan_summary or '(no plan summary)'}",
            "",
            f"**Cost:** ${goal.cost_usd_total:.4f} | "
            f"**Sub-tasks:** {sum(1 for s in goal.sub_tasks if s.output)}/{len(goal.sub_tasks)} completed",
            "",
            "---",
            "",
        ]
        for sub in goal.sub_tasks:
            sections.append(f"## {sub.label} (T{sub.tier})")
            if sub.error:
                sections.append(f"⚠️ ERROR: {sub.error}")
            if sub.output:
                sections.append(sub.output.strip())
            else:
                sections.append("_(no output)_")
            sections.append("")
        return "\n".join(sections)


# === Approval-resume helper (called by daemon /approval/{id}/decide) ===


async def resume_goal_after_approval(
    state: JarvisState,
    scheduler: GoalScheduler,
    approval_id: str,
) -> tuple[bool, str | None]:
    """After Boss decides on an approval, advance the parent goal.

    If APPROVED → run the Tier-3 sub-task now. If REJECTED → mark sub-task
    error. If all approvals for the goal are resolved, finalize the goal.
    """
    approval = await state.get_approval(approval_id)
    if approval is None:
        return False, "approval not found"

    goal = await state.get_goal(approval.goal_id)
    if goal is None:
        return False, "parent goal not found"

    # Find the sub-task
    sub = next((s for s in goal.sub_tasks if s.sub_id == approval.sub_id), None)
    if sub is None:
        return False, "sub-task not found"

    if approval.decision == ApprovalDecision.APPROVED:
        # Execute the Tier-3 sub-task NOW
        outcome = await run_worker(
            sub.prompt,
            project_root=scheduler.project_root,
            max_turns=15,
            timeout_seconds=900,
        )
        updated = SubTaskRecord(
            sub_id=sub.sub_id,
            label=sub.label,
            prompt=sub.prompt,
            tier=sub.tier,
            output=outcome.text,
            error=outcome.error,
            cost_usd=outcome.cost_usd,
            duration_ms=outcome.duration_ms,
            completed_at=datetime.utcnow(),
        )
        await state.update_goal(
            approval.goal_id,
            sub_task_update=updated,
            cost_delta=outcome.cost_usd or 0.0,
        )
        log.info(
            "Approval %s APPROVED — Tier-3 sub-task %s executed", approval_id, sub.sub_id
        )
    elif approval.decision == ApprovalDecision.REJECTED:
        updated = SubTaskRecord(
            sub_id=sub.sub_id,
            label=sub.label,
            prompt=sub.prompt,
            tier=sub.tier,
            error=f"Rejected by Boss: {approval.boss_note or '(no note)'}",
            completed_at=datetime.utcnow(),
        )
        await state.update_goal(approval.goal_id, sub_task_update=updated)
        log.info("Approval %s REJECTED", approval_id)

    # Check if all approvals for this goal are decided
    goal = await state.get_goal(approval.goal_id)
    if goal is None:
        return True, None
    pending = [
        s for s in goal.sub_tasks
        if s.tier == 3 and s.completed_at is None
    ]
    if not pending:
        synthesis = scheduler._synthesize_final(goal)
        await state.update_goal(
            approval.goal_id,
            status=GoalStatus.COMPLETED,
            final_output=synthesis,
            completed_at=datetime.utcnow(),
        )
    return True, None
