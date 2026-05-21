"""
jarvis-core FastAPI daemon.

Long-running localhost service that orchestrates Claude Code workers.
Telegram bridge (and future voice / web UI) hit this via HTTP instead of
spawning `claude` CLI directly. Persistent state survives requests.

Endpoints:
- POST /chat                 sync single-worker chat (Telegram-style)
- POST /task                 async parallel fan-out, returns task_id
- GET  /task/{task_id}       poll task status
- GET  /tasks                list recent tasks
- GET  /health               liveness + version
- GET  /state                debug stats
- POST /session/clear        forget prior session for a user (start fresh)

Auth model: bind to 127.0.0.1 only — no exposed port. Telegram bridge runs on
same host, so localhost access is sufficient. Do NOT expose this port publicly
without adding bearer-token auth first.

Run:
    .venv/bin/python -m jarvis_core.daemon
or via systemd unit `jarvis-core.service`.
"""
from __future__ import annotations

import logging
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException

from pydantic import BaseModel, Field

from . import __version__
from .models import (
    ApprovalDecision,
    ApprovalRequest,
    ChatRequest,
    ChatResponse,
    GoalRecord,
    GoalStateView,
    GoalStatus,
    TaskRecord,
    TaskRequest,
    TaskStateView,
    TaskStatus,
)
from .critic import Critic
from .intent import IntentClassifier
from .orchestrator import aggregate_results, run_parallel_workers, run_worker
from .recall import Recaller
from .scheduler import GoalScheduler, resume_goal_after_approval
from .state import JarvisState

# === Bootstrap ===

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

logging.basicConfig(
    level=os.getenv("JARVIS_CORE_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
log = logging.getLogger("jarvis_core.daemon")

PROJECT_ROOT = Path(os.getenv("JARVIS_PROJECT_PATH", str(ROOT))).resolve()
STATE_PATH = Path(os.getenv("JARVIS_STATE_PATH", str(ROOT / "data" / "state" / "jarvis-state.json")))
HOST = os.getenv("JARVIS_CORE_HOST", "127.0.0.1")
PORT = int(os.getenv("JARVIS_CORE_PORT", "8765"))
SYNC_INTERVAL = int(os.getenv("JARVIS_STATE_SYNC_SECONDS", "300"))


# === Lifespan: load state, start sync, register shutdown ===


state = JarvisState(state_path=STATE_PATH, sync_interval_seconds=SYNC_INTERVAL)

GOAL_POLL_INTERVAL = int(os.getenv("JARVIS_GOAL_POLL_SECONDS", "60"))
GOAL_MAX_CONCURRENT = int(os.getenv("JARVIS_GOAL_MAX_CONCURRENT", "1"))
scheduler = GoalScheduler(
    state=state,
    project_root=PROJECT_ROOT,
    poll_interval_seconds=GOAL_POLL_INTERVAL,
    max_concurrent_goals=GOAL_MAX_CONCURRENT,
)

# Self-growth singletons — Phase A (recall) + Phase B (critic) + intent classifier. See specs/.
recaller = Recaller(project_root=PROJECT_ROOT)
critic = Critic(project_root=PROJECT_ROOT)
intent_classifier = IntentClassifier(project_root=PROJECT_ROOT)

# Phase C — conversation log written here, consumed by scripts/auto_capture.py
CONVERSATION_LOG = PROJECT_ROOT / "data" / "logs" / "conversations.jsonl"


def _append_conversation_log(entry: dict) -> None:
    """Best-effort append of one chat turn to the conversation log."""
    try:
        CONVERSATION_LOG.parent.mkdir(parents=True, exist_ok=True)
        import json as _json
        with CONVERSATION_LOG.open("a") as fh:
            fh.write(_json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as exc:
        log.warning("conversation log append failed: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: D401 — FastAPI lifespan signature
    """Boot + shutdown hooks."""
    if not os.getenv("CLAUDE_CODE_OAUTH_TOKEN"):
        log.warning(
            "CLAUDE_CODE_OAUTH_TOKEN not set — Agent SDK will likely fail. "
            "Run `claude setup-token` and add to .env."
        )
    log.info("jarvis-core %s starting | project=%s state=%s", __version__, PROJECT_ROOT, STATE_PATH)
    state.load_from_disk()
    await state.start_background_sync()
    await scheduler.start()
    log.info("Goal scheduler online (poll=%ds, concurrent=%d)", GOAL_POLL_INTERVAL, GOAL_MAX_CONCURRENT)
    try:
        yield
    finally:
        log.info("jarvis-core shutting down — stopping scheduler + final state sync")
        await scheduler.stop()
        await state.stop()


app = FastAPI(
    title="jarvis-core",
    version=__version__,
    description="Super-agent orchestrator using Claude Agent SDK on Max-subscription auth.",
    lifespan=lifespan,
)


# === Routes ===


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe."""
    return {
        "status": "ok",
        "version": __version__,
        "project_root": str(PROJECT_ROOT),
        "auth": "oauth-token" if os.getenv("CLAUDE_CODE_OAUTH_TOKEN") else "missing",
    }


@app.get("/state")
async def get_state() -> dict[str, int | float]:
    """Debug stats."""
    return await state.stats()


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """Sync single-worker chat. Reuses prior session if resume_session=True.

    Pipeline (see specs/intent-classifier.spec.md + recall.spec.md + critic.spec.md):
      1. Intent — classify the message (task/question/feedback/…). Cheap Haiku.
      2. Recall — pull relevant memory chunks, build <jarvis_memory_context> block.
      3. Worker — Claude Code session with augmented prompt.
      4. Critic — silent reviewer; revises once if verdict=revise.
    """
    import asyncio as _asyncio  # local import keeps top-level deps unchanged

    conv = await state.get_or_create_conversation(req.user_id)
    resume_id = conv.last_session_id if req.resume_session else None

    log.info(
        "chat user=%s resume=%s msg=%r",
        req.user_id,
        bool(resume_id),
        req.message[:80],
    )

    # ── 1. Intent classification + Recall (run in parallel — independent layers) ─
    intent_task = _asyncio.create_task(
        intent_classifier.classify(req.message, req.user_id)
    )
    recall_result = await _asyncio.to_thread(recaller.gather, req.message, req.user_id)
    intent_result = await intent_task

    memory_context = recall_result.context

    # Build augmented prompt. Intent block always present (even synthetic) — gives
    # the worker a stable header it can branch on.
    intent_block = intent_result.to_block()
    if memory_context:
        augmented_prompt = (
            intent_block
            + "\n"
            + memory_context
            + "\n\n---\n\nUSER MESSAGE:\n"
            + req.message
        )
    else:
        augmented_prompt = (
            intent_block
            + "\n\n---\n\nUSER MESSAGE:\n"
            + req.message
        )

    # ── 2. Primary worker ─────────────────────────────────────────────────────
    outcome = await run_worker(
        augmented_prompt,
        project_root=PROJECT_ROOT,
        resume_session_id=resume_id,
        max_turns=req.max_turns,
    )

    if outcome.error and not outcome.text:
        return ChatResponse(
            reply=f"⚠️ Worker error: {outcome.error}",
            error=outcome.error,
            duration_ms=outcome.duration_ms,
            memory_hits=recall_result.n_chunks,
            intent=intent_result.category,
            priority=intent_result.priority,
        )

    # ── 3. Critic (verify + optional revise) ──────────────────────────────────
    try:
        critique_outcome = await critic.evaluate(
            user_message=req.message,
            jarvis_reply=outcome.text,
            memory_context=memory_context,
            user_id=req.user_id,
        )
        final_reply = critique_outcome.final_reply
        confidence = critique_outcome.confidence
        revised = critique_outcome.revised
    except Exception as exc:
        # Critic must never break the response path
        log.warning("critic pipeline failed: %s — shipping original reply", exc)
        final_reply = outcome.text
        confidence = "unverified"
        revised = False

    await state.update_conversation(
        req.user_id,
        session_id=outcome.session_id,
        cost_delta=outcome.cost_usd or 0.0,
    )

    # Phase C — append this turn to the conversation log for auto_capture.py
    _append_conversation_log({
        "ts": datetime.utcnow().isoformat(),
        "user_id": req.user_id,
        "user_msg": req.message,
        "reply": final_reply,
        "confidence": confidence,
        "memory_hits": recall_result.n_chunks,
        "revised": revised,
        "intent": intent_result.category,
        "priority": intent_result.priority,
        "duration_ms": outcome.duration_ms,
        "cost_usd": outcome.cost_usd,
    })

    return ChatResponse(
        reply=final_reply,
        session_id=outcome.session_id,
        cost_usd=outcome.cost_usd,
        duration_ms=outcome.duration_ms,
        confidence=confidence,
        memory_hits=recall_result.n_chunks,
        revised=revised,
        intent=intent_result.category,
        priority=intent_result.priority,
    )


@app.post("/session/clear")
async def clear_session(user_id: str) -> dict[str, str]:
    """Forget the user's prior Claude session — next /chat starts fresh."""
    await state.clear_session(user_id)
    return {"status": "cleared", "user_id": user_id}


@app.post("/task", response_model=TaskStateView)
async def create_task(req: TaskRequest, background: BackgroundTasks) -> TaskStateView:
    """Async fan-out: spawn N parallel workers. Returns task_id immediately."""
    record = TaskRecord(
        task_id=uuid.uuid4().hex[:12],
        user_id=req.user_id,
        title=req.title,
        workers=req.workers,
        aggregator_prompt=req.aggregator_prompt,
    )
    await state.create_task(record)
    background.add_task(_run_task, record.task_id)
    log.info(
        "task created id=%s user=%s workers=%d title=%r",
        record.task_id,
        req.user_id,
        len(req.workers),
        req.title,
    )
    return record.to_view()


@app.get("/task/{task_id}", response_model=TaskStateView)
async def get_task(task_id: str) -> TaskStateView:
    task = await state.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return task.to_view()


@app.get("/tasks", response_model=list[TaskStateView])
async def list_tasks(limit: int = 20) -> list[TaskStateView]:
    tasks = await state.list_recent_tasks(limit=limit)
    return [t.to_view() for t in tasks]


# === Phase 3: Autonomous goal endpoints ===


class GoalCreateRequest(BaseModel):
    user_id: str = "ujjwal"
    description: str = Field(..., min_length=5, max_length=4000)
    max_budget_usd: float = Field(default=5.0, ge=0.1, le=50.0)
    max_duration_seconds: int = Field(default=7200, ge=60, le=86_400)
    context: dict | None = None


class ApprovalDecisionRequest(BaseModel):
    decision: ApprovalDecision
    boss_note: str | None = None
    decided_by: str = "ujjwal"


@app.post("/goal", response_model=GoalStateView)
async def create_goal(req: GoalCreateRequest) -> GoalStateView:
    """Boss adds an autonomous goal. Scheduler picks it up on next tick."""
    import uuid as _uuid

    goal = GoalRecord(
        goal_id=_uuid.uuid4().hex[:12],
        user_id=req.user_id,
        description=req.description,
        max_budget_usd=req.max_budget_usd,
        max_duration_seconds=req.max_duration_seconds,
        context=req.context or {},
    )
    await state.add_goal(goal)
    log.info("Goal created id=%s user=%s budget=$%.2f", goal.goal_id, req.user_id, req.max_budget_usd)
    return goal.to_view()


@app.get("/goals", response_model=list[GoalStateView])
async def list_goals(status: GoalStatus | None = None, limit: int = 50) -> list[GoalStateView]:
    goals = await state.list_goals(status=status, limit=limit)
    return [g.to_view() for g in goals]


@app.get("/goal/{goal_id}", response_model=GoalStateView)
async def get_goal(goal_id: str) -> GoalStateView:
    goal = await state.get_goal(goal_id)
    if goal is None:
        raise HTTPException(404, "goal not found")
    return goal.to_view()


@app.get("/goal/{goal_id}/output")
async def get_goal_output(goal_id: str) -> dict:
    goal = await state.get_goal(goal_id)
    if goal is None:
        raise HTTPException(404, "goal not found")
    return {
        "goal_id": goal_id,
        "status": goal.status,
        "plan_summary": goal.plan_summary,
        "final_output": goal.final_output,
        "sub_tasks": [
            {
                "label": s.label,
                "tier": s.tier,
                "output": s.output,
                "error": s.error,
                "cost_usd": s.cost_usd,
                "approval_id": s.approval_id,
            }
            for s in goal.sub_tasks
        ],
        "cost_usd_total": goal.cost_usd_total,
        "error": goal.error,
    }


@app.post("/goal/{goal_id}/cancel", response_model=GoalStateView)
async def cancel_goal(goal_id: str, reason: str | None = None) -> GoalStateView:
    goal = await state.cancel_goal(goal_id, reason=reason)
    if goal is None:
        raise HTTPException(404, "goal not found")
    return goal.to_view()


@app.get("/approvals/pending")
async def list_pending_approvals() -> list[dict]:
    approvals = await state.list_pending_approvals()
    return [
        {
            "approval_id": a.approval_id,
            "goal_id": a.goal_id,
            "sub_id": a.sub_id,
            "action_summary": a.action_summary,
            "risk_notes": a.risk_notes,
            "requested_at": a.requested_at.isoformat(),
        }
        for a in approvals
    ]


@app.post("/approval/{approval_id}/decide")
async def decide_approval(approval_id: str, req: ApprovalDecisionRequest) -> dict:
    approval = await state.decide_approval(
        approval_id,
        decision=req.decision,
        boss_note=req.boss_note,
        decided_by=req.decided_by,
    )
    if approval is None:
        raise HTTPException(404, "approval not found")
    # Resume the goal (executes Tier-3 if approved, marks rejected if not)
    ok, err = await resume_goal_after_approval(state, scheduler, approval_id)
    return {
        "approval_id": approval_id,
        "decision": req.decision,
        "resumed": ok,
        "error": err,
    }


@app.get("/digest")
async def digest(hours: int = 24) -> dict:
    """Morning-digest data: recent goal activity + pending approvals."""
    from datetime import timedelta

    cutoff = datetime.utcnow() - timedelta(hours=hours)
    all_goals = await state.list_goals(limit=200)
    recent = [g for g in all_goals if g.updated_at >= cutoff]

    by_status: dict[str, list[dict]] = {}
    for g in recent:
        by_status.setdefault(g.status.value, []).append(
            {
                "goal_id": g.goal_id,
                "description": g.description[:200],
                "cost_usd": g.cost_usd_total,
                "sub_task_count": len(g.sub_tasks),
                "plan_summary": g.plan_summary,
                "error": g.error,
            }
        )

    pending = await state.list_pending_approvals()
    return {
        "window_hours": hours,
        "as_of": datetime.utcnow().isoformat(),
        "by_status": by_status,
        "pending_approvals": [
            {
                "approval_id": a.approval_id,
                "goal_id": a.goal_id,
                "action_summary": a.action_summary,
                "risk_notes": a.risk_notes,
            }
            for a in pending
        ],
        "totals": {
            "goals_in_window": len(recent),
            "cost_usd": sum(g.cost_usd_total for g in recent),
        },
    }


# === Background task runner ===


async def _run_task(task_id: str) -> None:
    """Execute a parallel-worker task in the background."""
    task = await state.get_task(task_id)
    if task is None:
        log.error("background task %s vanished before run", task_id)
        return

    await state.update_task(task_id, status=TaskStatus.RUNNING)
    log.info("task %s running (%d workers)", task_id, len(task.workers))

    try:
        # Run all workers in parallel
        worker_results = await run_parallel_workers(
            task.workers, project_root=PROJECT_ROOT
        )

        # Persist each worker result + cost
        for r in worker_results:
            await state.update_task(
                task_id,
                worker_result=r,
                cost_delta=r.cost_usd or 0.0,
            )

        # Optional aggregation step
        if task.aggregator_prompt:
            log.info("task %s running aggregator", task_id)
            agg = await aggregate_results(
                task.aggregator_prompt,
                worker_results,
                project_root=PROJECT_ROOT,
            )
            await state.update_task(
                task_id,
                final_output=agg.text,
                cost_delta=agg.cost_usd or 0.0,
            )
        else:
            # No aggregator — concatenate worker outputs as final
            final = "\n\n".join(
                f"### {r.label}\n{r.output}" for r in worker_results if r.output
            )
            await state.update_task(task_id, final_output=final)

        await state.update_task(task_id, status=TaskStatus.COMPLETED)
        log.info("task %s completed", task_id)

    except Exception as e:
        log.exception("task %s failed", task_id)
        await state.update_task(
            task_id,
            status=TaskStatus.FAILED,
            error=f"{type(e).__name__}: {e}",
        )


# === Entry point ===


def main() -> None:
    uvicorn.run(
        "jarvis_core.daemon:app",
        host=HOST,
        port=PORT,
        log_level=os.getenv("JARVIS_CORE_LOG_LEVEL", "info").lower(),
        reload=False,
    )


if __name__ == "__main__":
    main()
