"""
backend/main.py
================
FastAPI application for AltBrief — Alt-Data Investment Brief Agent.

Endpoints:
    GET  /health                 — health check (always-on)
    GET  /brief/stream/{ticker}  — SSE stream: 8 parallel sources + Claude synthesis
    GET  /brief/{ticker}         — cached GET (returns 404 if not cached yet)
    POST /brief/{ticker}/warm    — pre-warm cache for a ticker (demo prep)
    GET  /metrics                — today's cost + source stats

SSE event types (named events, consumed by frontend EventSource):
    source_started    — a source began fetching
    source_completed  — source returned (ok/error/blocked/cached)
    synthesis_chunk   — token streamed from Claude Sonnet
    done              — full InvestmentBrief JSON (stream closes after this)
    error             — unrecoverable failure

Launch:
    python -m backend.main

    or:

    uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncIterable, AsyncIterator

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .observability import configure_logging, get_logger
from .schemas import BriefEvent, InvestmentBrief, SourceResult, SourceStatus
from .orchestrator import run_pipeline, SOURCES
from .cost_tracker import check_and_record, today_spend, DAILY_CAP_USD

# ---------------------------------------------------------------------------
# Logging — configure before first use
# ---------------------------------------------------------------------------
configure_logging()
log = get_logger("main")

# ---------------------------------------------------------------------------
# SSE support: prefer native fastapi.sse (>=0.135.0), fallback to sse-starlette
# ---------------------------------------------------------------------------
_SSE_MODE = "none"

try:
    from fastapi.sse import EventSourceResponse, ServerSentEvent  # type: ignore[import]
    _SSE_MODE = "native"
    log.info("sse_mode", mode="native_fastapi_sse")
except ImportError:
    try:
        from sse_starlette.sse import EventSourceResponse, ServerSentEvent  # type: ignore[import,no-redef]
        _SSE_MODE = "sse_starlette"
        log.info("sse_mode", mode="sse_starlette")
    except ImportError:
        # Manual SSE via StreamingResponse
        from fastapi.responses import StreamingResponse as _StreamingResponse  # type: ignore

        class ServerSentEvent:  # type: ignore[no-redef]
            """Minimal SSE event that can be serialised to bytes."""

            def __init__(
                self,
                data: str = "",
                event: str | None = None,
                id: str | None = None,
                comment: str | None = None,
                retry: int | None = None,
            ) -> None:
                self.data = data
                self.event = event
                self.id = id
                self.comment = comment
                self.retry = retry

            def encode(self) -> bytes:
                parts: list[str] = []
                if self.comment is not None:
                    parts.append(f": {self.comment}")
                if self.retry is not None:
                    parts.append(f"retry: {self.retry}")
                if self.event:
                    parts.append(f"event: {self.event}")
                if self.id:
                    parts.append(f"id: {self.id}")
                for line in (self.data or "").split("\n"):
                    parts.append(f"data: {line}")
                parts.append("\n")
                return "\n".join(parts).encode("utf-8")

        def EventSourceResponse(  # type: ignore[no-redef]
            generator: Any,
            **kwargs: Any,
        ) -> _StreamingResponse:
            async def _wrap() -> AsyncIterable[bytes]:
                async for evt in generator:
                    yield evt.encode()

            return _StreamingResponse(
                _wrap(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "X-Accel-Buffering": "no",
                    "Connection": "keep-alive",
                },
            )

        _SSE_MODE = "manual"
        log.warning("sse_mode", mode="manual_streaming_response")

# ---------------------------------------------------------------------------
# Synthesizer import — built by ML engineer agent
# Interface: async def synthesize_brief(ticker, sources) -> AsyncIterator[ServerSentEvent]
# ---------------------------------------------------------------------------
try:
    from .synthesizer import synthesize_brief as _synthesize_brief  # type: ignore[import]
    _HAS_SYNTHESIZER = True

    async def synthesize_brief(
        ticker: str,
        sources: dict[str, SourceResult],
    ) -> AsyncIterator[ServerSentEvent]:
        async for evt in _synthesize_brief(ticker, sources):
            yield evt

except ImportError:
    _HAS_SYNTHESIZER = False
    log.warning("synthesizer_missing", note="Using mock synthesizer")

    async def synthesize_brief(  # type: ignore[no-redef]
        ticker: str,
        sources: dict[str, SourceResult],
    ) -> AsyncIterator[ServerSentEvent]:
        """
        Mock synthesizer — active until real synthesizer.py is provided.
        Yields a single 'done' event with a minimal InvestmentBrief JSON.
        """
        ok_sources = [k for k, v in sources.items() if v.status == SourceStatus.OK]
        fail_sources = [k for k, v in sources.items() if v.status != SourceStatus.OK]

        # Narrative token stream simulation (so UI shows something moving)
        mock_narrative = (
            f"[MOCK SYNTHESIZER — wire synthesizer.py to enable real analysis]\n"
            f"Sources available ({len(ok_sources)}/{len(sources)}): {', '.join(ok_sources)}\n"
            f"Sources unavailable: {', '.join(fail_sources) or 'none'}"
        )
        for word in mock_narrative.split():
            yield ServerSentEvent(
                data=json.dumps({"text": word + " "}),
                event="synthesis_chunk",
            )
            await asyncio.sleep(0.02)  # simulate streaming

        brief = InvestmentBrief(
            ticker=ticker.upper(),
            company_name=ticker.upper(),
            sector="Unknown",
            overall_direction="neutral",
            overall_confidence=0.5,
            brief_narrative=mock_narrative,
            sources_used=ok_sources,
            sources_unavailable=fail_sources,
            data_quality_flag="minimal",
        )
        yield ServerSentEvent(
            data=brief.model_dump_json(),
            event="done",
            id="done",
        )


# ---------------------------------------------------------------------------
# Brief file cache
# ---------------------------------------------------------------------------
_CACHE_DIR = Path(os.getenv("ALTBRIEF_CACHE_DIR", "/tmp/altbrief_cache"))
_BRIEF_CACHE_DIR = _CACHE_DIR / "briefs"
_BRIEF_CACHE_TTL = int(os.getenv("BRIEF_CACHE_TTL", "3600"))  # 1 hour default


def _brief_cache_path(ticker: str) -> Path:
    return _BRIEF_CACHE_DIR / f"{ticker.upper()}.json"


def _load_brief_cache(ticker: str) -> str | None:
    """Return cached InvestmentBrief JSON string, or None if missing/stale."""
    path = _brief_cache_path(ticker.upper())
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text())
        age = time.time() - payload.get("ts", 0)
        if age < _BRIEF_CACHE_TTL:
            return payload.get("brief_json")
    except Exception as exc:
        log.warning("brief_cache_read_error", error=str(exc))
    return None


def _save_brief_cache(ticker: str, brief_json: str) -> None:
    """Persist InvestmentBrief JSON to file cache."""
    try:
        _BRIEF_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _brief_cache_path(ticker.upper()).write_text(
            json.dumps({"ts": time.time(), "brief_json": brief_json})
        )
    except Exception as exc:
        log.warning("brief_cache_write_error", error=str(exc))


# ---------------------------------------------------------------------------
# CORS origins
# ---------------------------------------------------------------------------
def _cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    origins = [o.strip().rstrip("/") for o in raw.split(",") if o.strip()]
    # Always allow localhost for dev
    for dev in ("http://localhost:3000", "http://127.0.0.1:3000"):
        if dev not in origins:
            origins.append(dev)
    return origins


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    log.info("altbrief_startup", version="1.0.0", cors=_cors_origins())

    # Ensure cache dirs exist
    _BRIEF_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Warm Pydantic schema compilation (avoids first-request latency spike)
    try:
        InvestmentBrief(ticker="WARMUP", company_name="warmup", sector="test", brief_narrative="")
    except Exception:
        pass

    # Claude grammar warmup — pre-compile InvestmentBrief tool schema (saves 200-500ms first req)
    try:
        from .synthesizer import warmup as _synth_warmup
        await _synth_warmup()
        log.info("synthesizer_warmup_ok")
    except Exception as exc:
        log.warning("synthesizer_warmup_skipped", error=str(exc))

    yield  # Application runs

    # Graceful BrightData subprocess shutdown
    try:
        from .sources.brightdata import shutdown_mcp
        await shutdown_mcp()
        log.info("brightdata_mcp_shutdown")
    except Exception as exc:
        log.warning("brightdata_mcp_shutdown_failed", error=str(exc))

    log.info("altbrief_shutdown")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AltBrief API",
    description=(
        "Alt-data investment brief agent. "
        "Fans out to 8 parallel data sources (SEC EDGAR, Yahoo Finance, "
        "Reddit, LinkedIn, Glassdoor, GDELT, NASA FIRMS, Reuters) "
        "and synthesises a structured 1-page brief via Claude Sonnet. "
        "SSE-streamed in ~30-45 seconds."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=False,  # Must be False when allow_origins is a list (not "*")
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Cache-Control", "X-Accel-Buffering", "Last-Event-Id"],
)

# ---------------------------------------------------------------------------
# Ticker validation
# ---------------------------------------------------------------------------
_TICKER_RE = re.compile(r"^[A-Z]{1,5}$")
_start_time = time.time()


def _validate_ticker(ticker: str) -> str:
    t = ticker.upper().strip()
    if not _TICKER_RE.match(t):
        raise HTTPException(
            status_code=422,
            detail={
                "error": {
                    "code": "invalid_ticker",
                    "message": f"Ticker '{ticker}' must be 1-5 uppercase letters (A-Z).",
                    "type": "validation",
                }
            },
        )
    return t


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

@app.get("/health", tags=["ops"])
async def health() -> JSONResponse:
    """
    Liveness probe. Returns 200 when the process is alive.
    Fly.io healthcheck + Docker HEALTHCHECK use this endpoint.
    """
    return JSONResponse({
        "status": "ok",
        "version": "1.0.0",
        "uptime_s": round(time.time() - _start_time, 1),
        "today_spend_usd": round(today_spend(), 6),
        "daily_cap_usd": DAILY_CAP_USD,
        "synthesizer_ready": _HAS_SYNTHESIZER,
        "sse_mode": _SSE_MODE,
    })


# ---------------------------------------------------------------------------
# /metrics
# ---------------------------------------------------------------------------

@app.get("/metrics", tags=["ops"])
async def metrics() -> JSONResponse:
    """Operational metrics: spend, source list, cache TTL."""
    spend = today_spend()
    return JSONResponse({
        "today_spend_usd": round(spend, 6),
        "daily_cap_usd": DAILY_CAP_USD,
        "spend_remaining_usd": round(max(0, DAILY_CAP_USD - spend), 6),
        "sources": [name for name, _ in SOURCES],
        "brief_cache_ttl_s": _BRIEF_CACHE_TTL,
        "synthesizer_ready": _HAS_SYNTHESIZER,
    })


# ---------------------------------------------------------------------------
# GET /brief/{ticker} — cached brief lookup
# ---------------------------------------------------------------------------

@app.get("/brief/{ticker}", tags=["brief"])
async def get_cached_brief(ticker: str) -> JSONResponse:
    """
    Return cached InvestmentBrief JSON if available (< 1h old).
    404 if not cached — call /brief/stream/{ticker} to generate.
    """
    t = _validate_ticker(ticker)
    cached = _load_brief_cache(t)
    if cached is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "brief_not_cached",
                    "message": (
                        f"No cached brief for {t}. "
                        f"Generate one via GET /brief/stream/{t}"
                    ),
                    "type": "not_found",
                }
            },
        )
    return JSONResponse(content=json.loads(cached))


# ---------------------------------------------------------------------------
# POST /brief/{ticker}/warm — pre-warm cache for demo tickers
# ---------------------------------------------------------------------------

@app.post("/brief/{ticker}/warm", tags=["ops"])
async def warm_ticker(ticker: str) -> JSONResponse:
    """
    Pre-warm brief cache for a ticker in the background.
    Useful for NVDA, XOM, WMT before a demo.
    Returns immediately; the brief will be cached asynchronously.
    """
    t = _validate_ticker(ticker)

    async def _bg_warm() -> None:
        bound = log.bind(ticker=t, task="warm")
        bound.info("warm_started")
        try:
            queue: asyncio.Queue[BriefEvent | None] = asyncio.Queue()
            results = await run_pipeline(t, queue)
            # Drain queue (not streaming to client here)
            while True:
                try:
                    item = queue.get_nowait()
                    if item is None:
                        break
                except asyncio.QueueEmpty:
                    break

            results_map = {r.source: r for r in results}
            brief_json: str | None = None
            async for evt in synthesize_brief(t, results_map):
                if hasattr(evt, "event") and evt.event == "done":
                    brief_json = evt.data
                    break

            if brief_json:
                _save_brief_cache(t, brief_json)
                bound.info("warm_complete", cached=True)
            else:
                bound.warning("warm_no_brief")
        except Exception as exc:
            log.error("warm_failed", ticker=t, error=str(exc))

    asyncio.create_task(_bg_warm(), name=f"warm-{t}")
    return JSONResponse({
        "status": "warming",
        "ticker": t,
        "message": f"Background brief generation started for {t}. Check /brief/{t} in ~60 seconds.",
    })


# ---------------------------------------------------------------------------
# SSE event builder
# ---------------------------------------------------------------------------

def _brief_event_to_sse(event: BriefEvent, idx: int) -> "ServerSentEvent":
    """Convert internal BriefEvent to a typed ServerSentEvent for the wire."""
    # Map internal type → SSE event name expected by frontend (lib/sse.ts)
    event_name = {
        "started": "source_started",
        "source_done": "source_completed",
        "source_failed": "source_completed",
        "synthesis_start": "synthesis_chunk",
        "brief_ready": "done",
        "error": "error",
    }.get(event.event_type, event.event_type)

    payload: dict = {
        "event_type": event.event_type,
        "source": event.source,
        "progress": event.progress,
        "message": event.message,
    }
    if event.data:
        payload["data"] = event.data

    return ServerSentEvent(
        data=json.dumps(payload, default=str),
        event=event_name,
        id=str(idx),
    )


# ---------------------------------------------------------------------------
# GET /brief/stream/{ticker} — main SSE endpoint
# ---------------------------------------------------------------------------

@app.get("/brief/stream/{ticker}", tags=["brief"])
async def stream_brief(
    request: Request,
    ticker: str,
    force_refresh: bool = Query(default=False, description="Bypass cache; re-fetch all sources"),
) -> "EventSourceResponse":
    """
    SSE endpoint. Streams named events as 8 parallel data sources return,
    then streams Claude Sonnet synthesis tokens, and emits the final
    InvestmentBrief JSON as the 'done' event.

    Named SSE events:
      source_started   — a source began scraping
      source_completed — a source returned (status: ok|error|timeout|blocked|cached)
      synthesis_chunk  — streaming token from Claude Sonnet synthesis
      done             — complete InvestmentBrief JSON; stream closes after this
      error            — unrecoverable failure

    Reconnection: set Last-Event-Id header to resume from an event offset
    (handled natively by EventSource / fetch-event-source on the client).
    """
    t = _validate_ticker(ticker)
    bound = log.bind(ticker=t)
    bound.info("stream_request")

    async def event_generator() -> AsyncIterable["ServerSentEvent"]:
        event_idx = 0

        # ── Fast path: full brief cache hit ──────────────────────────────────
        if not force_refresh:
            cached_json = _load_brief_cache(t)
            if cached_json:
                bound.info("brief_cache_hit")
                event_idx += 1
                yield ServerSentEvent(
                    data=json.dumps({
                        "source": "cache",
                        "ticker": t,
                        "status": "ok",
                        "message": "Returning cached brief (< 1h old)",
                    }),
                    event="source_completed",
                    id=str(event_idx),
                )
                event_idx += 1
                yield ServerSentEvent(
                    data=cached_json,
                    event="done",
                    id="done",
                )
                return

        # ── Cost cap guard ────────────────────────────────────────────────────
        if today_spend() >= DAILY_CAP_USD:
            event_idx += 1
            yield ServerSentEvent(
                data=json.dumps({
                    "error": f"Daily cost cap of ${DAILY_CAP_USD} reached. Try again tomorrow.",
                    "ticker": t,
                }),
                event="error",
                id="cost-cap",
            )
            return

        # ── Fan-out via asyncio.Queue bridge ──────────────────────────────────
        queue: asyncio.Queue[BriefEvent | None | ServerSentEvent] = asyncio.Queue()
        request_start = time.monotonic()
        brief_json_holder: list[str] = []  # mutable container for done-event data

        async def producer() -> None:
            """
            Runs all 8 sources in parallel and pushes events into the queue.
            Then calls synthesizer and pushes synthesis SSE events.
            Producer always terminates by pushing None (sentinel).
            """
            try:
                # ── Source fan-out ────────────────────────────────────────
                results = await run_pipeline(t, queue)
                results_map = {r.source: r for r in results}

                ok_count = sum(1 for r in results if r.status == SourceStatus.OK)
                bound.info(
                    "sources_complete",
                    ok=ok_count,
                    total=len(results),
                    elapsed_s=round(time.monotonic() - request_start, 2),
                )

                # ── Synthesis ─────────────────────────────────────────────
                async for sse_evt in synthesize_brief(t, results_map):
                    # Synthesizer yields ServerSentEvent objects directly
                    await queue.put(sse_evt)
                    if hasattr(sse_evt, "event") and sse_evt.event == "done":
                        brief_json_holder.append(sse_evt.data or "")

            except Exception as exc:
                bound.error("producer_error", error=str(exc), exc_info=True)
                err_evt = ServerSentEvent(
                    data=json.dumps({"error": str(exc), "ticker": t}),
                    event="error",
                    id="error",
                )
                await queue.put(err_evt)
            finally:
                await queue.put(None)  # Sentinel

        producer_task = asyncio.create_task(producer(), name=f"producer-{t}")

        try:
            while True:
                # Heartbeat-aware drain: 10s timeout → comment ping
                try:
                    item = await asyncio.wait_for(queue.get(), timeout=10.0)
                except asyncio.TimeoutError:
                    # Invisible to frontend JS; keeps proxies alive
                    yield ServerSentEvent(comment="heartbeat")
                    continue

                if item is None:
                    break  # Sentinel → producer done

                event_idx += 1

                if isinstance(item, ServerSentEvent):
                    # Synthesizer SSE event — pass through directly
                    # Rewrite id so it's sequential in the overall stream
                    yield ServerSentEvent(
                        data=getattr(item, "data", ""),
                        event=getattr(item, "event", None),
                        id=str(event_idx),
                        comment=getattr(item, "comment", None),
                    )
                elif isinstance(item, BriefEvent):
                    yield _brief_event_to_sse(item, event_idx)

                # Client disconnect check
                if await request.is_disconnected():
                    bound.info("client_disconnected")
                    break

        except asyncio.CancelledError:
            bound.info("sse_generator_cancelled")
        finally:
            if not producer_task.done():
                producer_task.cancel()

            # Cache the completed brief
            if brief_json_holder:
                brief_json = brief_json_holder[0]
                _save_brief_cache(t, brief_json)
                total_s = round(time.monotonic() - request_start, 2)
                bound.info("stream_complete", latency_s=total_s, cached=True)

    return EventSourceResponse(event_generator())


# ---------------------------------------------------------------------------
# Entry point: python -m backend.main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "0") == "1",
        log_level="info",
        access_log=True,
    )
