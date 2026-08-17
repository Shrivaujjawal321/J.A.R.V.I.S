"""
backend/orchestrator.py
========================
Async fan-out orchestrator. Pure asyncio — no LangGraph for V1.

Architecture: asyncio.Queue bridge pattern (Research doc 16).
Each source task pushes SSE-ready events into a queue as it completes.
The SSE generator in main.py drains the queue and yields to the client.

This allows clients to see each source result in real-time (~1-3s apart)
rather than waiting for all 8 sources to complete before seeing anything.

Named SSE events emitted via queue:
    source_started    — source began fetching (emitted before tasks kick off)
    source_completed  — source returned (ok, error, blocked, timeout, cached)
    synthesis_start   — all sources done, synthesizer begins
    contradiction     — cross-source contradiction detected (post-synthesis)
    done              — final InvestmentBrief JSON written to cache + emitted
    error             — unrecoverable orchestration error
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import AsyncIterator
from typing import Awaitable, Callable

from .schemas import BriefEvent, SourceResult, SourceStatus
from .sources import (
    fetch_sec,
    fetch_yahoo,
    fetch_news,
    fetch_reddit,
    fetch_linkedin,
    fetch_glassdoor,
    fetch_gdelt,
    fetch_satellite,
)

logger = logging.getLogger(__name__)

# Order = priority for token-budget pruning in synthesizer
# (sec first = highest quality, satellite last = conditional)
SOURCES: list[tuple[str, Callable[[str], Awaitable]]] = [
    ("sec", fetch_sec),
    ("yahoo", fetch_yahoo),
    ("news", fetch_news),
    ("reddit", fetch_reddit),
    ("linkedin", fetch_linkedin),
    ("glassdoor", fetch_glassdoor),
    ("gdelt", fetch_gdelt),
    ("satellite", fetch_satellite),
]

# Per-source timeout (seconds). Synthesizer needs to start ≤15s after first connect.
SOURCE_TIMEOUT: float = 12.0


# ---------------------------------------------------------------------------
# safe_scrape — never raises, always returns SourceResult
# ---------------------------------------------------------------------------

async def safe_scrape(
    ticker: str,
    source_name: str,
    fn: Callable[[str], Awaitable],
    timeout_s: float = SOURCE_TIMEOUT,
) -> SourceResult:
    """
    Wrap any source fetch function so exceptions never escape.
    Returns SourceResult with appropriate status enum on failure.
    """
    start = time.monotonic()
    try:
        async with asyncio.timeout(timeout_s):
            result = await fn(ticker)
            # fn() already returns SourceResult — validate type
            if not isinstance(result, SourceResult):
                raise TypeError(f"Source {source_name} returned {type(result)}, expected SourceResult")
            return result
    except asyncio.TimeoutError:
        return SourceResult(
            source=source_name,
            status=SourceStatus.TIMEOUT,
            error_msg=f"Timed out after {timeout_s}s",
            latency_ms=int((time.monotonic() - start) * 1000),
        )
    except Exception as exc:
        return SourceResult(
            source=source_name,
            status=SourceStatus.ERROR,
            error_msg=f"{type(exc).__name__}: {exc}",
            latency_ms=int((time.monotonic() - start) * 1000),
        )


# ---------------------------------------------------------------------------
# Queue-based fan-out
# ---------------------------------------------------------------------------

async def _run_source_into_queue(
    ticker: str,
    source_name: str,
    fn: Callable[[str], Awaitable],
    queue: asyncio.Queue,
) -> SourceResult:
    """
    Run one source; push a source_completed SSE event into queue when done.
    The queue drain loop in main.py's SSE generator yields these to the client.
    """
    result = await safe_scrape(ticker, source_name, fn)

    is_ok = result.status == SourceStatus.OK
    payload = {
        "source": source_name,
        "ticker": ticker,
        "latency_ms": result.latency_ms,
        "status": result.status.value,
        "cached": result.cached,
    }
    if not is_ok and result.error_msg:
        payload["error"] = result.error_msg

    # Lean preview for log overlay (first 120 chars of data)
    if is_ok and result.data:
        preview = str(result.data)
        payload["preview"] = preview[:120] + ("…" if len(preview) > 120 else "")

    await queue.put(BriefEvent(
        event_type="source_done" if is_ok else "source_failed",
        source=source_name,
        progress=0,  # progress filled in main.py after counting
        message=(
            f"{source_name}: {result.status.value} ({result.latency_ms}ms)"
            if not is_ok
            else f"{source_name}: ok ({result.latency_ms}ms)"
        ),
        data=payload,
    ))

    return result


async def run_pipeline(
    ticker: str,
    queue: asyncio.Queue,
    sources: list[tuple[str, Callable]] | None = None,
) -> list[SourceResult]:
    """
    Fan-out all sources in parallel.
    Pushes source_started events immediately, then source_completed events
    as each source finishes.

    Returns the complete list of SourceResults for the synthesizer.

    Queue events:
        BriefEvent(event_type="source_done"|"source_failed") — one per source
        BriefEvent(event_type="synthesis_start")             — after all sources done
    """
    sources = sources or SOURCES
    total = len(sources)

    # Emit source_started events for all sources upfront
    # (lets the UI show "spinning" indicators for all 8 sources immediately)
    for name, _ in sources:
        await queue.put(BriefEvent(
            event_type="started",
            source=name,
            progress=2,
            message=f"{name}: fetching…",
        ))

    # Kick off all tasks in parallel
    tasks: list[asyncio.Task[SourceResult]] = []
    for name, fn in sources:
        task = asyncio.create_task(
            _run_source_into_queue(ticker, name, fn, queue),
            name=f"source-{name}",
        )
        tasks.append(task)

    # gather with return_exceptions=True — _run_source_into_queue never raises,
    # but asyncio.gather's exception suppression is belt-and-suspenders here
    raw_results = await asyncio.gather(*tasks, return_exceptions=True)

    results: list[SourceResult] = []
    for i, r in enumerate(raw_results):
        if isinstance(r, SourceResult):
            results.append(r)
        else:
            # Shouldn't happen given safe_scrape, but handle defensively
            source_name = sources[i][0] if i < len(sources) else "unknown"
            logger.error("Source %s returned exception: %s", source_name, r)
            results.append(SourceResult(
                source=source_name,
                status=SourceStatus.ERROR,
                error_msg=str(r),
                latency_ms=0,
            ))

    # Signal synthesis start
    ok_count = sum(1 for r in results if r.status == SourceStatus.OK)
    await queue.put(BriefEvent(
        event_type="synthesis_start",
        progress=78,
        message=f"Synthesising brief ({ok_count}/{total} sources ok) with Claude Sonnet…",
    ))

    return results


# ---------------------------------------------------------------------------
# Legacy generator API (kept for compatibility with run_pipeline callers that
# use the original AsyncIterator[BriefEvent | list[SourceResult]] interface)
# ---------------------------------------------------------------------------

async def run_pipeline_legacy(
    ticker: str,
    sources: list[tuple[str, Callable]] | None = None,
) -> AsyncIterator[BriefEvent | list[SourceResult]]:
    """
    Legacy generator interface. Yields BriefEvent objects and finally the
    list[SourceResult]. New code should use run_pipeline() with queue instead.

    Kept for compatibility with existing callers / tests.
    """
    sources = sources or SOURCES
    total = len(sources)

    yield BriefEvent(
        event_type="started",
        progress=2,
        message=f"Dispatching {total} parallel scrapers for {ticker}",
    )

    task_map: dict[asyncio.Task, str] = {}
    for name, fn in sources:
        t = asyncio.create_task(safe_scrape(ticker, name, fn))
        task_map[t] = name

    results: list[SourceResult] = []
    completed = 0
    for task in asyncio.as_completed(task_map.keys()):
        result = await task
        results.append(result)
        completed += 1
        progress = int(5 + (completed / total) * 70)
        event_type = "source_done" if result.status == SourceStatus.OK else "source_failed"
        yield BriefEvent(
            event_type=event_type,
            source=result.source,
            progress=progress,
            message=(
                f"{result.source}: ok ({result.latency_ms}ms)"
                if result.status == SourceStatus.OK
                else f"{result.source}: {result.status.value} — {result.error_msg or ''}"
            ),
        )

    yield BriefEvent(
        event_type="synthesis_start",
        progress=78,
        message="Synthesising brief with Claude Sonnet…",
    )

    yield results
