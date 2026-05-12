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

from . import __version__
from .models import (
    ChatRequest,
    ChatResponse,
    TaskRecord,
    TaskRequest,
    TaskStateView,
    TaskStatus,
)
from .orchestrator import aggregate_results, run_parallel_workers, run_worker
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
    try:
        yield
    finally:
        log.info("jarvis-core shutting down — final state sync")
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
    """Sync single-worker chat. Reuses prior session if resume_session=True."""
    conv = await state.get_or_create_conversation(req.user_id)
    resume_id = conv.last_session_id if req.resume_session else None

    log.info(
        "chat user=%s resume=%s msg=%r",
        req.user_id,
        bool(resume_id),
        req.message[:80],
    )

    outcome = await run_worker(
        req.message,
        project_root=PROJECT_ROOT,
        resume_session_id=resume_id,
        max_turns=req.max_turns,
    )

    if outcome.error and not outcome.text:
        return ChatResponse(
            reply=f"⚠️ Worker error: {outcome.error}",
            error=outcome.error,
            duration_ms=outcome.duration_ms,
        )

    await state.update_conversation(
        req.user_id,
        session_id=outcome.session_id,
        cost_delta=outcome.cost_usd or 0.0,
    )

    return ChatResponse(
        reply=outcome.text,
        session_id=outcome.session_id,
        cost_usd=outcome.cost_usd,
        duration_ms=outcome.duration_ms,
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
