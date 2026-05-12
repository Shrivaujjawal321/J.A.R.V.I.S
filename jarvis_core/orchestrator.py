"""
Claude Agent SDK dispatcher — single-worker (chat) + parallel-workers (task).

Each dispatch spawns a Claude Code session as a subprocess via the SDK.
- cwd = Jarvis project root → spawned workers see .claude/agents/*, .mcp.json,
  CLAUDE.md, slash commands, skills (full Jarvis specialist roster is available).
- Auth = CLAUDE_CODE_OAUTH_TOKEN env var (Max subscription), no API key.
- Streaming is collected internally and the full text is returned per call.

Cost tracking: ResultMessage.total_cost_usd is captured per call. For Max
subscribers this is a local estimate (real billing is subscription-based),
but useful as a quota-tracking signal.
"""
from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions, query

from .models import WorkerResult, WorkerSpec

log = logging.getLogger("jarvis_core.orchestrator")


@dataclass
class WorkerOutcome:
    """Internal result of one spawned worker run."""

    text: str
    session_id: str | None
    cost_usd: float | None
    duration_ms: int
    error: str | None = None


def _extract_text_blocks(message: object) -> list[str]:
    """Best-effort extraction of text content from an SDK message."""
    out: list[str] = []
    content = getattr(message, "content", None)
    if isinstance(content, list):
        for block in content:
            text = getattr(block, "text", None)
            if text:
                out.append(text)
    return out


def _extract_session_id(message: object) -> str | None:
    """Pull session_id from a SystemMessage's init payload, if present."""
    if type(message).__name__ != "SystemMessage":
        return None
    if getattr(message, "subtype", None) != "init":
        return None
    data = getattr(message, "data", None)
    if isinstance(data, dict):
        return data.get("session_id")
    return None


async def run_worker(
    prompt: str,
    *,
    project_root: Path,
    resume_session_id: str | None = None,
    max_turns: int = 15,
    allowed_tools: list[str] | None = None,
    timeout_seconds: int = 300,
) -> WorkerOutcome:
    """Run a single Claude Code worker via the Agent SDK.

    Collects streaming output into a single text response. Captures session_id
    (for resumability) and total_cost_usd (for quota tracking).
    """
    options_kwargs: dict = {
        "cwd": str(project_root),
        "max_turns": max_turns,
    }
    if resume_session_id:
        options_kwargs["resume"] = resume_session_id
    if allowed_tools is not None:
        options_kwargs["allowed_tools"] = allowed_tools

    options = ClaudeAgentOptions(**options_kwargs)

    started = time.perf_counter()
    text_parts: list[str] = []
    session_id: str | None = None
    total_cost: float | None = None
    final_result: str | None = None
    error: str | None = None

    async def _collect() -> None:
        nonlocal session_id, total_cost, final_result
        async for message in query(prompt=prompt, options=options):
            sid = _extract_session_id(message)
            if sid:
                session_id = sid
            text_parts.extend(_extract_text_blocks(message))
            cost = getattr(message, "total_cost_usd", None)
            if cost is not None:
                total_cost = cost
            result = getattr(message, "result", None)
            if isinstance(result, str) and result:
                final_result = result

    try:
        await asyncio.wait_for(_collect(), timeout=timeout_seconds)
    except asyncio.TimeoutError:
        error = f"Worker timeout after {timeout_seconds}s"
        log.warning("Worker timed out: prompt[:80]=%r", prompt[:80])
    except Exception as e:
        error = f"{type(e).__name__}: {e}"
        log.exception("Worker raised exception")

    duration_ms = int((time.perf_counter() - started) * 1000)

    # Prefer the SDK's final `result` (clean final output); fall back to
    # streamed assistant text concatenated.
    text = final_result or "\n".join(text_parts).strip()
    if not text and error is None:
        text = "(empty response from Claude — model returned no text)"

    return WorkerOutcome(
        text=text,
        session_id=session_id,
        cost_usd=total_cost,
        duration_ms=duration_ms,
        error=error,
    )


async def run_parallel_workers(
    workers: list[WorkerSpec],
    *,
    project_root: Path,
    timeout_seconds: int = 600,
) -> list[WorkerResult]:
    """Fan out N workers concurrently via asyncio.gather.

    Each worker gets its own Claude Code session (independent context window).
    All run in parallel; total wall-clock = slowest worker.
    """
    log.info("Spawning %d parallel workers", len(workers))

    async def _run_one(spec: WorkerSpec) -> WorkerResult:
        outcome = await run_worker(
            spec.prompt,
            project_root=project_root,
            max_turns=spec.max_turns,
            allowed_tools=spec.allowed_tools,
            timeout_seconds=timeout_seconds,
        )
        return WorkerResult(
            label=spec.label,
            output=outcome.text,
            cost_usd=outcome.cost_usd,
            duration_ms=outcome.duration_ms,
            error=outcome.error,
        )

    return await asyncio.gather(*(_run_one(w) for w in workers))


async def aggregate_results(
    aggregator_prompt: str,
    worker_results: list[WorkerResult],
    *,
    project_root: Path,
    max_turns: int = 5,
    timeout_seconds: int = 180,
) -> WorkerOutcome:
    """Final synthesis step: feed all worker outputs into one Claude call.

    The aggregator prompt frames how Claude should combine the worker outputs.
    Worker outputs are appended as labeled sections.
    """
    sections = ["# Worker Outputs\n"]
    for r in worker_results:
        sections.append(f"## Worker: {r.label}")
        if r.error:
            sections.append(f"[ERROR: {r.error}]")
        sections.append(r.output or "(no output)")
        sections.append("")  # blank line

    full_prompt = (
        aggregator_prompt
        + "\n\n---\n\n"
        + "\n".join(sections)
        + "\n\nProduce the synthesized response now."
    )

    return await run_worker(
        full_prompt,
        project_root=project_root,
        max_turns=max_turns,
        allowed_tools=[],  # Pure synthesis — no tool use needed
        timeout_seconds=timeout_seconds,
    )
