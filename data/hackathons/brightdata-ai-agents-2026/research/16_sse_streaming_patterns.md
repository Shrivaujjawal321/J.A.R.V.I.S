# SSE Streaming Patterns — AltBrief Implementation Guide
**Research Date:** 2026-05-27  
**Stack:** FastAPI (Python 3.12 + asyncio) ↔ Next.js 15 App Router (React 19)  
**Deployment:** Fly.io backend / Vercel hobby frontend

---

## 1. FastAPI Side — Endpoint Choice in 2026

### Decision: `fastapi.sse` (native) over `sse-starlette`

**FastAPI 0.135.0+ ships a built-in `EventSourceResponse` at `fastapi.sse`.** Use it. Do NOT install `sse-starlette` for new projects in 2026.

| Feature | `fastapi.sse` (native) | `sse-starlette` |
|---|---|---|
| Installation | Zero (built-in) | `pip install sse-starlette` |
| Pydantic serialization | Rust-side (fast) | Python `json.dumps()` |
| Keep-alive pings | Auto every 15s | Manual `ping=10` param |
| `X-Accel-Buffering: no` | Auto | Auto |
| `Cache-Control: no-cache` | Auto | Auto |
| `Last-Event-ID` resumption | Native header support | Manual |
| Named events | `ServerSentEvent(event=...)` | dict `{"event": ..., "data": ...}` |
| ASGI compatibility | Full | Full |

**One gotcha:** FastAPI 0.135.0 is current as of late 2025. Verify your installed version:
```bash
pip show fastapi | grep Version
```
If you're on < 0.135.0, either upgrade (`pip install -U fastapi`) or fall back to `sse-starlette`.

---

### 1a. CORS Setup (required — Fly.io backend, Vercel frontend, different origins)

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="AltBrief API")

# Pull allowed origins from env; default to localhost for dev
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,        # e.g. "https://altbrief.vercel.app,http://localhost:3000"
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Cache-Control", "X-Accel-Buffering"],
)
```

In `.env` on Fly.io:
```
CORS_ORIGINS=https://altbrief.vercel.app,https://altbrief-git-main.vercel.app
```

---

### 1b. The Fan-Out SSE Endpoint — asyncio + named events

The key challenge: `asyncio.as_completed()` is not directly an async iterable compatible with SSE generators. The correct pattern uses **asyncio.Queue** as the bridge: each source task pushes its result into the queue as it finishes; the SSE generator drains the queue.

```python
# backend/main.py
import asyncio
import json
import time
from collections.abc import AsyncIterable
from typing import Annotated

from fastapi import FastAPI, Header, Query
from fastapi.sse import EventSourceResponse, ServerSentEvent

from .orchestrator import run_all_sources
from .synthesizer import synthesize_brief
from .cache import get_cached_brief, set_cached_brief
from .schemas import SourceResult

app = FastAPI()

@app.get("/brief/stream/{ticker}", response_class=EventSourceResponse)
async def stream_brief(
    ticker: str,
    last_event_id: Annotated[str | None, Header()] = None,
) -> AsyncIterable[ServerSentEvent]:
    """
    SSE endpoint. Yields events as each of the 8 sources returns.
    Named events:
      source_started   — source began scraping
      source_completed — source returned data (or failed gracefully)
      synthesis_chunk  — token from Claude Sonnet streamed
      done             — full InvestmentBrief JSON, stream closes
      error            — unrecoverable failure
    """
    ticker = ticker.upper().strip()

    # Fast path: check file cache
    cached = await get_cached_brief(ticker)
    if cached:
        yield ServerSentEvent(
            data=json.dumps({"ticker": ticker, "source": "cache"}),
            event="source_completed",
            id="cache-hit",
        )
        yield ServerSentEvent(
            data=cached,
            event="done",
            id="done",
        )
        return

    # --- Fan-out via asyncio.Queue ---
    queue: asyncio.Queue[ServerSentEvent | None] = asyncio.Queue()
    start_time = time.monotonic()

    async def producer() -> None:
        """Run all 8 sources in parallel; push SSE events as they complete."""
        try:
            # Signal each source starting
            source_names = [
                "sec", "yahoo", "news", "reddit",
                "linkedin", "glassdoor", "gdelt", "satellite",
            ]
            for name in source_names:
                await queue.put(ServerSentEvent(
                    data=json.dumps({"source": name, "ticker": ticker}),
                    event="source_started",
                    id=f"start-{name}",
                ))

            # Kick off all sources concurrently
            source_results: list[SourceResult] = await run_all_sources(ticker, queue)

            # Synthesize with Claude Sonnet — stream tokens
            async for chunk in synthesize_brief(ticker, source_results):
                await queue.put(ServerSentEvent(
                    data=json.dumps({"text": chunk}),
                    event="synthesis_chunk",
                ))

        except Exception as exc:
            await queue.put(ServerSentEvent(
                data=json.dumps({"error": str(exc), "ticker": ticker}),
                event="error",
                id="error",
            ))
        finally:
            await queue.put(None)  # Sentinel: producer done

    # Launch producer as background task (non-blocking)
    task = asyncio.create_task(producer())

    # --- SSE generator drains queue ---
    try:
        event_index = 0
        while True:
            event = await queue.get()
            if event is None:
                break
            event_index += 1
            yield event
    except asyncio.CancelledError:
        # Client disconnected
        task.cancel()
        return
    finally:
        if not task.done():
            task.cancel()
```

---

### 1c. orchestrator.py — The Fan-Out with per-source SSE events

```python
# backend/orchestrator.py
import asyncio
import json
import time
from typing import Any

from fastapi.sse import ServerSentEvent

from .schemas import SourceResult
from .sources import sec, yahoo, news, reddit, linkedin, glassdoor, gdelt, satellite
from .cache import get_cached_source, set_cached_source

# Map source name → coroutine factory
SOURCE_MAP = {
    "sec":       sec.fetch,
    "yahoo":     yahoo.fetch,
    "news":      news.fetch,
    "reddit":    reddit.fetch,
    "linkedin":  linkedin.fetch,
    "glassdoor": glassdoor.fetch,
    "gdelt":     gdelt.fetch,
    "satellite": satellite.fetch,
}

async def _run_single_source(
    name: str,
    ticker: str,
    queue: asyncio.Queue,
) -> SourceResult:
    """Run one source; push completion event into queue when done."""
    t0 = time.monotonic()
    try:
        # Cache check per-source
        cached = await get_cached_source(name, ticker)
        if cached:
            result = SourceResult(source=name, data=cached, latency_ms=0, from_cache=True)
        else:
            raw = await SOURCE_MAP[name](ticker)
            latency_ms = int((time.monotonic() - t0) * 1000)
            result = SourceResult(source=name, data=raw, latency_ms=latency_ms, from_cache=False)
            await set_cached_source(name, ticker, raw)

        await queue.put(ServerSentEvent(
            data=json.dumps({
                "source": name,
                "ticker": ticker,
                "latency_ms": result.latency_ms,
                "from_cache": result.from_cache,
                "status": "ok",
                "summary": _first_n_chars(str(result.data), 120),
            }),
            event="source_completed",
            id=f"done-{name}",
        ))
        return result

    except Exception as exc:
        latency_ms = int((time.monotonic() - t0) * 1000)
        await queue.put(ServerSentEvent(
            data=json.dumps({
                "source": name,
                "ticker": ticker,
                "latency_ms": latency_ms,
                "status": "error",
                "error": str(exc),
            }),
            event="source_completed",
            id=f"done-{name}",
        ))
        # Return empty result so synthesis can continue with partial data
        return SourceResult(source=name, data=None, latency_ms=latency_ms, error=str(exc))


async def run_all_sources(
    ticker: str,
    queue: asyncio.Queue,
) -> list[SourceResult]:
    """
    Fan-out: run all 8 sources concurrently.
    Each source pushes its own SSE event to queue when done.
    Returns list of results (some may have error field).
    """
    tasks = [
        asyncio.create_task(
            _run_single_source(name, ticker, queue),
            name=f"source-{name}",
        )
        for name in SOURCE_MAP
    ]

    # gather(return_exceptions=True) so one failure doesn't kill the rest
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out raw exceptions (shouldn't happen since _run_single_source catches internally)
    source_results: list[SourceResult] = []
    for r in results:
        if isinstance(r, SourceResult):
            source_results.append(r)
    return source_results


def _first_n_chars(s: str, n: int) -> str:
    return s[:n] + "…" if len(s) > n else s
```

---

### 1d. Heartbeat / Keep-Alive

The native `fastapi.sse` `EventSourceResponse` sends **automatic comment pings every 15 seconds**. This is sufficient for Fly.io's default idle timeouts (see Section 3).

If you need to control the interval explicitly (e.g., lower to 10s for aggressive proxy chains), you can emit comment events manually inside your generator:

```python
# Inside your SSE generator, if you want explicit heartbeats
# alongside the queue drain:
async def _with_heartbeat(
    queue: asyncio.Queue,
    interval: float = 10.0,
) -> AsyncIterable[ServerSentEvent]:
    """Drain queue, injecting heartbeat comments if idle."""
    while True:
        try:
            event = await asyncio.wait_for(queue.get(), timeout=interval)
        except asyncio.TimeoutError:
            # Emit comment heartbeat — not visible to client JS, keeps connection alive
            yield ServerSentEvent(comment="heartbeat")
            continue
        if event is None:
            break
        yield event
```

Replace the plain `queue.get()` loop in `stream_brief` with this if you observe dropped connections on proxied environments.

---

## 2. Next.js 15 App Router Client

### Decision: `@microsoft/fetch-event-source` over native `EventSource`

| Feature | Native `EventSource` | `@microsoft/fetch-event-source` |
|---|---|---|
| Custom headers (`Authorization`) | No | Yes |
| POST body | No | Yes |
| Reconnect control | Browser-default (opaque) | Full control + backoff |
| Named event handlers | `addEventListener` | `onmessage` with `event.event` field |
| Page Visibility API | No | Yes (pauses when tab hidden) |
| AbortController support | No (must `.close()`) | Yes |
| TypeScript types | Minimal | Good |

Install:
```bash
npm install @microsoft/fetch-event-source
```

---

### 2a. `useSSE` hook — complete, production-ready

```typescript
// frontend/lib/sse.ts
"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { fetchEventSource } from "@microsoft/fetch-event-source";

// ------- Types -------

export type SSEEvent =
  | { type: "source_started";   data: { source: string; ticker: string } }
  | { type: "source_completed"; data: { source: string; ticker: string; latency_ms: number; status: "ok" | "error"; summary?: string; error?: string; from_cache?: boolean } }
  | { type: "synthesis_chunk";  data: { text: string } }
  | { type: "done";             data: string }        // raw JSON of InvestmentBrief
  | { type: "error";            data: { error: string; ticker: string } };

export interface UseSSEOptions {
  ticker: string | null;              // null = don't connect
  onEvent: (event: SSEEvent) => void;
  onDone?: (brief: string) => void;   // called with raw JSON when "done" arrives
  onError?: (err: Error) => void;
}

export interface UseSSEReturn {
  isConnected: boolean;
  isStreaming: boolean;
  abort: () => void;
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";
const MAX_RETRIES = 5;
const BASE_RETRY_MS = 1000;

// ------- Hook -------

export function useSSE({
  ticker,
  onEvent,
  onDone,
  onError,
}: UseSSEOptions): UseSSEReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const retriesRef = useRef(0);

  // Stable refs so callbacks don't cause reconnect loops
  const onEventRef = useRef(onEvent);
  const onDoneRef = useRef(onDone);
  const onErrorRef = useRef(onError);
  useEffect(() => { onEventRef.current = onEvent; }, [onEvent]);
  useEffect(() => { onDoneRef.current = onDone; }, [onDone]);
  useEffect(() => { onErrorRef.current = onError; }, [onError]);

  const abort = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
  }, []);

  useEffect(() => {
    if (!ticker) return;

    // Clean up any previous connection
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    retriesRef.current = 0;

    const url = `${BACKEND_URL}/brief/stream/${encodeURIComponent(ticker)}`;

    const connect = () => {
      setIsStreaming(true);

      fetchEventSource(url, {
        method: "GET",
        signal: controller.signal,

        headers: {
          Accept: "text/event-stream",
          "Cache-Control": "no-cache",
        },

        // ---- Connection opened ----
        async onopen(response) {
          if (response.ok && response.headers.get("content-type")?.includes("text/event-stream")) {
            setIsConnected(true);
            retriesRef.current = 0;
            return;
          }
          // Non-SSE response → treat as fatal, don't retry
          throw new Error(`Unexpected response: ${response.status}`);
        },

        // ---- Named event dispatch ----
        onmessage(msg) {
          if (!msg.data) return;

          // `msg.event` is the SSE "event:" field name
          const eventType = msg.event || "message";

          let parsed: unknown;
          try {
            parsed = JSON.parse(msg.data);
          } catch {
            parsed = msg.data; // raw string for "done" event
          }

          switch (eventType) {
            case "source_started":
              onEventRef.current({
                type: "source_started",
                data: parsed as SSEEvent["data"],
              });
              break;

            case "source_completed":
              onEventRef.current({
                type: "source_completed",
                data: parsed as SSEEvent["data"],
              });
              break;

            case "synthesis_chunk":
              onEventRef.current({
                type: "synthesis_chunk",
                data: parsed as { text: string },
              });
              break;

            case "done":
              setIsConnected(false);
              setIsStreaming(false);
              onEventRef.current({ type: "done", data: msg.data });
              onDoneRef.current?.(msg.data);
              controller.abort(); // Close cleanly after done
              break;

            case "error":
              onEventRef.current({
                type: "error",
                data: parsed as { error: string; ticker: string },
              });
              break;

            default:
              break;
          }
        },

        // ---- Connection closed by server ----
        onclose() {
          setIsConnected(false);
          setIsStreaming(false);
        },

        // ---- Error + exponential backoff reconnect ----
        onerror(err) {
          if (controller.signal.aborted) return; // intentional abort, don't retry

          setIsConnected(false);
          onErrorRef.current?.(err instanceof Error ? err : new Error(String(err)));

          if (retriesRef.current >= MAX_RETRIES) {
            setIsStreaming(false);
            controller.abort();
            return; // Stop retrying
          }

          // Exponential backoff with jitter
          const delay =
            BASE_RETRY_MS * Math.pow(2, retriesRef.current) +
            Math.random() * 500;
          retriesRef.current += 1;

          // Return delay (ms) tells fetch-event-source when to reconnect
          return delay;
        },
      });
    };

    connect();

    // Cleanup on unmount or ticker change
    return () => {
      controller.abort();
      setIsConnected(false);
      setIsStreaming(false);
    };
  }, [ticker]); // Re-run only when ticker changes

  return { isConnected, isStreaming, abort };
}
```

---

### 2b. Usage in a page component with TanStack Query

```typescript
// frontend/app/brief/[ticker]/page.tsx
"use client";

import { useState, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useSSE, SSEEvent } from "@/lib/sse";
import { AgentStepTicker } from "@/components/AgentStepTicker";
import { BriefCard } from "@/components/BriefCard";
import type { InvestmentBrief } from "@/lib/types";

const BRIEF_QUERY_KEY = (ticker: string) => ["brief", ticker];

export default function BriefPage({ params }: { params: { ticker: string } }) {
  const ticker = params.ticker.toUpperCase();
  const queryClient = useQueryClient();

  const [steps, setSteps] = useState<SSEEvent[]>([]);
  const [synthesisText, setSynthesisText] = useState("");
  const [brief, setBrief] = useState<InvestmentBrief | null>(null);

  const handleEvent = useCallback((event: SSEEvent) => {
    setSteps((prev) => [...prev, event]);

    if (event.type === "synthesis_chunk") {
      setSynthesisText((prev) => prev + event.data.text);
    }
  }, []);

  // Called when "done" event arrives with full brief JSON
  const handleDone = useCallback(
    (rawJson: string) => {
      try {
        const parsed: InvestmentBrief = JSON.parse(rawJson);
        setBrief(parsed);

        // Seed TanStack Query cache — now any other component
        // calling useQuery(["brief", ticker]) gets instant data
        queryClient.setQueryData(BRIEF_QUERY_KEY(ticker), parsed);
      } catch {
        console.error("Failed to parse brief JSON");
      }
    },
    [ticker, queryClient],
  );

  const { isStreaming, isConnected } = useSSE({
    ticker,
    onEvent: handleEvent,
    onDone: handleDone,
  });

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100 p-8">
      <AgentStepTicker
        steps={steps}
        isConnected={isConnected}
        isStreaming={isStreaming}
      />

      {synthesisText && !brief && (
        <div className="font-mono text-sm text-zinc-400 mt-4 whitespace-pre-wrap">
          {synthesisText}
          <span className="animate-pulse">▌</span>
        </div>
      )}

      {brief && <BriefCard brief={brief} />}
    </main>
  );
}
```

---

### 2c. TanStack Query — reading cached brief from a sibling component

```typescript
// frontend/components/RelatedBriefs.tsx — reads cache seeded by SSE hook
"use client";

import { useQuery } from "@tanstack/react-query";
import type { InvestmentBrief } from "@/lib/types";

async function fetchBrief(ticker: string): Promise<InvestmentBrief> {
  const res = await fetch(
    `${process.env.NEXT_PUBLIC_BACKEND_URL}/brief/${ticker}`,
  );
  if (!res.ok) throw new Error("Not cached yet");
  return res.json();
}

export function RelatedBriefs({ ticker }: { ticker: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ["brief", ticker],
    queryFn: () => fetchBrief(ticker),
    staleTime: 60 * 60 * 1000,  // 1h — matches backend file cache TTL
    refetchOnWindowFocus: false, // CRITICAL: prevents duplicate SSE subscriptions
    // If useSSE already called setQueryData, this queryFn never fires
    // (TanStack Query uses cache first when staleTime not exceeded)
  });

  if (isLoading || !data) return null;
  return <div>{data.company_name} — {data.overall_direction}</div>;
}
```

**Pattern:** `useSSE` calls `queryClient.setQueryData(...)` on stream completion → `useQuery` in other components finds the data in cache immediately and skips the network fetch.

---

## 3. Vercel + Fly.io Deployment Gotchas

### 3a. NEVER proxy SSE through Next.js API routes on Vercel Hobby

Vercel Hobby serverless functions have a **10-second max execution time** on Hobby tier. SSE streams run for 30-45 seconds for AltBrief. An API route proxy will hit `504 Gateway Timeout` at 10s, killing the stream mid-synthesis.

**Solution: client connects DIRECTLY to Fly.io backend.**

```
Browser → EventSource("https://altbrief-api.fly.dev/brief/stream/NVDA")
         ↑ Direct. Not through Vercel.
```

```typescript
// frontend/lib/sse.ts — env var points directly at Fly.io
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";
// On Vercel: NEXT_PUBLIC_BACKEND_URL=https://altbrief-api.fly.dev
```

Set in Vercel dashboard: `NEXT_PUBLIC_BACKEND_URL = https://altbrief-api.fly.dev`

This is why `NEXT_PUBLIC_` prefix is required — it's exposed to the browser bundle. The SSE connection goes browser → Fly.io directly, bypassing Vercel serverless entirely.

**Do NOT create `app/api/brief/stream/route.ts`** — it would force the stream through Vercel's runtime with the 10s cap.

---

### 3b. Fly.io idle timeout

Fly.io's HAProxy layer historically dropped idle TCP connections at 60s (pre-2023 restriction). That restriction was removed in September 2023, but **two live issues remain in 2026:**

1. **HTTP/1.1 undocumented 5s idle timeout** on some Fly regions — mitigation: ensure your SSE stream always has data flowing; use heartbeat comments if synthesis takes >4s to start.
2. **Some intermediary CDN/proxy layers between Fly edge and app** can still drop after ~30s idle.

The native `fastapi.sse` `EventSourceResponse` auto-pings every 15s — this is usually sufficient. For the AltBrief case where synthesis streaming starts within ~30s, you will not hit idle timeout problems.

The `fly.toml` you need:

```toml
# fly.toml
app = "altbrief-api"
primary_region = "sin"  # Singapore — close to IST

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = false     # CRITICAL: no cold starts during demo
  min_machines_running = 1
  [http_service.concurrency]
    type = "connections"
    hard_limit = 50
    soft_limit = 25

[[vm]]
  memory = "512mb"
  cpu_kind = "shared"
  cpus = 1
```

The `auto_stop_machines = false` + `min_machines_running = 1` prevents any cold start during the demo.

---

### 3c. Mobile Safari EventSource quirks

Mobile Safari has two known issues:

1. **EventSource on iOS ≤ 16 does not respect the `event:` field** — only fires `onmessage`, not `addEventListener("named-event")`. Named events are invisible. Fix: use `@microsoft/fetch-event-source` which parses event fields itself via fetch streaming, not the native EventSource API. The `useSSE` hook above uses fetch-event-source — you are safe.

2. **HTTP/1.1 browser connection limit (6 per origin):** On HTTP/1.1, each tab gets a pool of 6 connections. `EventSource` holds one permanently; with multiple tabs open, you can starve other requests. Fly.io serves HTTP/2 by default (`force_https = true` triggers TLS → HTTP/2 negotiation). HTTP/2 multiplexes all SSE streams over one connection — the 6-connection cap is a non-issue.

   Verify: `curl -I https://altbrief-api.fly.dev` → should show `HTTP/2 200`.

3. **Background tab freezing on iOS:** When iOS suspends the tab, the SSE connection drops silently. `@microsoft/fetch-event-source` handles this via Page Visibility API — it pauses the stream when the tab goes background and reconnects with `Last-Event-ID` on foreground. For a hackathon demo this is fine.

---

### 3d. CORS preflight for SSE

EventSource (native) does NOT send CORS preflight (OPTIONS) — it only sends a GET. But `fetch-event-source` uses `fetch()` which DOES send preflight for cross-origin requests.

Your `CORSMiddleware` config in Section 1a handles this correctly. The critical settings:

```python
allow_origins=CORS_ORIGINS,  # Must match Vercel domain exactly (no trailing slash)
allow_methods=["GET", "OPTIONS"],
allow_headers=["*"],          # Allows Accept, Cache-Control, Last-Event-Id headers
```

Common mistake: setting `allow_origins=["*"]` with `allow_credentials=True` — this causes a CORS error. Pick one or the other.

---

## 4. Claude Sonnet Token Streaming Through SSE

Pattern: `AsyncAnthropic` → `stream()` async context manager → re-emit each text delta as `synthesis_chunk` SSE event.

```python
# backend/synthesizer.py
import asyncio
import json
from collections.abc import AsyncGenerator
from anthropic import AsyncAnthropic
from .schemas import SourceResult, InvestmentBrief
from .prompts import build_synthesis_prompt

client = AsyncAnthropic()  # Uses ANTHROPIC_API_KEY from env

async def synthesize_brief(
    ticker: str,
    source_results: list[SourceResult],
) -> AsyncGenerator[str, None]:
    """
    Stream Claude Sonnet synthesis tokens.
    Yields text chunks; caller wraps each in a synthesis_chunk SSE event.
    """
    system_prompt, user_prompt = build_synthesis_prompt(ticker, source_results)

    # Use stream() for token-by-token streaming
    async with client.messages.stream(
        model="claude-sonnet-4-6-20260501",   # Pin exact model version
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        # stream.text_stream is an async iterator of text deltas
        async for text_delta in stream.text_stream:
            yield text_delta

        # After streaming, get the final accumulated message
        # for structured extraction (tool use result)
        # Note: stream.get_final_message() waits for the full response
        # Use tool-use on a SEPARATE non-streaming call for InvestmentBrief schema
        # (streaming + tool use structured output don't mix cleanly in Anthropic SDK v0.40+)
```

**Critical caveat: streaming + tool-use (structured output) are incompatible for guaranteed schema compliance.**

The Anthropic SDK can stream tool-use calls, but you get partial JSON until the stream ends — you can't parse it midway. For AltBrief, the recommended split:

```python
# backend/synthesizer.py — Two-phase approach
async def synthesize_brief_two_phase(
    ticker: str,
    source_results: list[SourceResult],
    queue: asyncio.Queue,
) -> InvestmentBrief:
    """
    Phase 1: Stream narrative tokens (for live UI ticker).
    Phase 2: Single non-streaming call for structured InvestmentBrief schema.
    """
    system_prompt, user_prompt = build_synthesis_prompt(ticker, source_results)

    # Phase 1 — stream narrative to frontend
    narrative_parts: list[str] = []
    async with client.messages.stream(
        model="claude-sonnet-4-6-20260501",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        async for text_delta in stream.text_stream:
            narrative_parts.append(text_delta)
            await queue.put(ServerSentEvent(
                data=json.dumps({"text": text_delta}),
                event="synthesis_chunk",
            ))

    narrative = "".join(narrative_parts)

    # Phase 2 — tool-use for structured brief (non-streaming, fast)
    from .tools import BRIEF_TOOL_SPEC
    response = await client.messages.create(
        model="claude-sonnet-4-6-20260501",
        max_tokens=4096,
        system=system_prompt,
        tools=[BRIEF_TOOL_SPEC],
        tool_choice={"type": "tool", "name": "create_investment_brief"},
        messages=[
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": narrative},
            {"role": "user", "content": "Now output the structured InvestmentBrief."},
        ],
    )

    # Extract tool call result
    for block in response.content:
        if block.type == "tool_use" and block.name == "create_investment_brief":
            return InvestmentBrief.model_validate(block.input)

    raise ValueError("Synthesizer did not return structured brief")
```

This streams ~1024 tokens of narrative to the frontend for the live ticker effect, then makes a fast structured call for the schema-compliant `InvestmentBrief` JSON that populates the cards.

---

## 5. Reference Implementations

### 5a. GitHub repos showing this exact pattern

1. **harshitsinghai77/server-sent-events-using-fastapi-and-reactjs**  
   https://github.com/harshitsinghai77/server-sent-events-using-fastapi-and-reactjs  
   FastAPI + SSE + React, complete stack. Simpler than AltBrief but good structural reference.

2. **sysid/sse-starlette** (README + examples)  
   https://github.com/sysid/sse-starlette  
   Best reference for advanced SSE features (graceful shutdown, heartbeat tuning, anyio channels). Production-hardened library even if you use native fastapi.sse instead.

3. **aidanuno/useFetchEventSource**  
   https://github.com/aidanuno/useFetchEventSource  
   React hook wrapping `@microsoft/fetch-event-source` — very close to the `useSSE` hook above.

### 5b. Blog posts with complete working code

4. **FastAPI + Claude API: Production Streaming API — SSE & Retry (2026)**  
   https://jangwook.net/en/blog/en/fastapi-claude-api-streaming-production-guide-2026/  
   FastAPI + `AsyncAnthropic` + `StreamingResponse`. Uses `client.messages.stream()` exactly as shown in Section 4. Has error classification (rate limit vs auth vs network) and retry logic.

5. **Using Fetch Event Source for SSE in React — LogRocket (2025)**  
   https://blog.logrocket.com/using-fetch-event-source-server-sent-events-react/  
   `@microsoft/fetch-event-source` in React with `onopen`/`onmessage`/`onclose`/`onerror` lifecycle.

6. **React Query + SSE Cache Integration — Fragmented Thought (2025)**  
   https://fragmentedthought.com/blog/2025/react-query-caching-with-server-side-events  
   The `setQueryData` + `refetchOnWindowFocus: false` pattern, which is what the `useSSE` hook + `RelatedBriefs` component above implement.

7. **FastAPI native SSE docs (0.135.0+)**  
   https://fastapi.tiangolo.com/tutorial/server-sent-events/  
   Authoritative source for `from fastapi.sse import EventSourceResponse, ServerSentEvent`. The `ServerSentEvent(data=item, event="item_update", id=str(i), retry=5000)` API.

---

## Quick Copy-Paste Checklist

Before demo, verify each item:

- [ ] `NEXT_PUBLIC_BACKEND_URL` set on Vercel (points to `https://altbrief-api.fly.dev`)
- [ ] `CORS_ORIGINS` set on Fly.io (includes `https://altbrief.vercel.app` — no trailing slash)
- [ ] `auto_stop_machines = false` and `min_machines_running = 1` in `fly.toml`
- [ ] FastAPI version ≥ 0.135.0 (`pip show fastapi`)
- [ ] `AsyncAnthropic()` not `Anthropic()` in synthesizer.py (don't block uvicorn event loop)
- [ ] `ANTHROPIC_API_KEY` in Fly.io secrets (`fly secrets set ANTHROPIC_API_KEY=...`)
- [ ] Pre-warm NVDA + XOM + WMT cache before demo (`GET /brief/stream/{ticker}` once)
- [ ] Verify HTTP/2: `curl -I https://altbrief-api.fly.dev` shows `HTTP/2`
- [ ] `refetchOnWindowFocus: false` on every `useQuery` that shares key with SSE hook
- [ ] No Next.js API route proxying the SSE stream

---

## Sources

- [FastAPI SSE native docs (0.135.0+)](https://fastapi.tiangolo.com/tutorial/server-sent-events/) — Official, authoritative
- [sysid/sse-starlette GitHub](https://github.com/sysid/sse-starlette) — Production SSE library, heartbeat/CORS/graceful-shutdown reference
- [FastAPI + Claude Streaming Production Guide 2026](https://jangwook.net/en/blog/en/fastapi-claude-api-streaming-production-guide-2026/) — AsyncAnthropic + SSE wiring
- [Using Fetch Event Source in React — LogRocket](https://blog.logrocket.com/using-fetch-event-source-server-sent-events-react/) — @microsoft/fetch-event-source patterns
- [React Query + SSE Cache — Fragmented Thought 2025](https://fragmentedthought.com/blog/2025/react-query-caching-with-server-side-events) — setQueryData after stream pattern
- [Anthropic SDK Streaming Docs](https://docs.anthropic.com/en/docs/build-with-claude/streaming) — stream() + text_stream async iterator
- [Fly.io TCP idle timeout thread](https://community.fly.io/t/tcp-idle-timeouts-restrictions-have-been-removed/15160) — idle timeout restriction removed Sept 2023
- [Vercel SSE time limits community thread](https://community.vercel.com/t/sse-time-limits/5954) — confirms 10s Hobby cap, streaming bypass
- [Vercel → Fly.io CORS error thread](https://community.fly.io/t/cors-error-vercel-frontend-to-fly-io-backend/22603) — cross-origin SSE setup
- [@microsoft/fetch-event-source npm](https://www.npmjs.com/package/@microsoft/fetch-event-source) — library reference
- [harshitsinghai77/server-sent-events-using-fastapi-and-reactjs](https://github.com/harshitsinghai77/server-sent-events-using-fastapi-and-reactjs) — complete reference repo
- [pydantic-ai Issue #4493 — FastAPI EventSourceResponse](https://github.com/pydantic/pydantic-ai/issues/4493) — native fastapi.sse vs sse-starlette discussion
- [TanStack Query streamedQuery docs](https://tanstack.com/query/latest/docs/reference/streamedQuery) — experimental streaming query API
- [MDN EventSource](https://developer.mozilla.org/en-US/docs/Web/API/EventSource) — HTTP/2 connection limit clarification
- [Streaming AI Agents with SSE — Panaversity Agent Factory](https://agentfactory.panaversity.org/docs/Building-Agent-Factories/fastapi-for-agents/streaming-with-sse) — agent + SSE patterns
