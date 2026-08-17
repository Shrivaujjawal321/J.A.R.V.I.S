#!/usr/bin/env python3
"""
scripts/prewarm.py
==================
Pre-warm the backend cache for the three demo tickers (NVDA, XOM, WMT).

Run this once after every fresh deploy BEFORE recording the demo video.
Each ticker triggers a full pipeline run → results cached to .cache/*.json
Subsequent demo requests return in <2s from cache.

Usage
-----
    # Against local backend:
    python scripts/prewarm.py

    # Against production Fly.io:
    BACKEND_URL=https://altbrief-api.fly.dev python scripts/prewarm.py

    # Via Makefile:
    make prewarm

Exit codes
----------
    0 — all tickers pre-warmed successfully
    1 — one or more tickers failed (check output for errors)
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from typing import Any

import httpx

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
DEMO_TICKERS = ["NVDA", "XOM", "WMT"]

# How long to wait for a full pipeline run (8 sources + synthesis = up to 90s)
STREAM_TIMEOUT_S = 120


async def prewarm_ticker(client: httpx.AsyncClient, ticker: str) -> bool:
    """
    Connect to the SSE stream for `ticker`, drain events until "done" or "error".
    Returns True if brief was generated/cached successfully.
    """
    url = f"{BACKEND_URL}/brief/stream/{ticker}"
    print(f"\n[{ticker}] Connecting to {url}")
    t0 = time.monotonic()

    event_count = 0
    last_event_type = None

    try:
        async with client.stream("GET", url, timeout=STREAM_TIMEOUT_S) as response:
            if response.status_code != 200:
                print(f"[{ticker}] ERROR: HTTP {response.status_code}")
                return False

            # Parse SSE stream
            current_event_type: str | None = None
            buffer: list[str] = []

            async for line in response.aiter_lines():
                line = line.strip()

                if line.startswith("event:"):
                    current_event_type = line[6:].strip()
                elif line.startswith("data:"):
                    data_str = line[5:].strip()
                    event_count += 1
                    last_event_type = current_event_type or "message"

                    if current_event_type in ("source_started", "source_completed"):
                        try:
                            payload: Any = json.loads(data_str)
                            source = payload.get("source", "?")
                            status = payload.get("status", "")
                            latency = payload.get("latency_ms", "")
                            if current_event_type == "source_completed":
                                print(f"[{ticker}]   source {source}: {status} ({latency}ms)")
                            else:
                                print(f"[{ticker}]   source {source}: started")
                        except json.JSONDecodeError:
                            pass

                    elif current_event_type == "synthesis_chunk":
                        # Dots to show synthesis progress without spamming
                        print(".", end="", flush=True)

                    elif current_event_type == "done":
                        elapsed = round(time.monotonic() - t0, 1)
                        print(f"\n[{ticker}] Done in {elapsed}s — brief cached")
                        return True

                    elif current_event_type == "error":
                        try:
                            payload = json.loads(data_str)
                            print(f"\n[{ticker}] ERROR: {payload.get('error', data_str)}")
                        except json.JSONDecodeError:
                            print(f"\n[{ticker}] ERROR: {data_str}")
                        return False

                elif line == "":
                    # Empty line = event separator; reset event type
                    current_event_type = None

    except httpx.TimeoutException:
        elapsed = round(time.monotonic() - t0, 1)
        print(f"\n[{ticker}] TIMEOUT after {elapsed}s ({event_count} events received)")
        return False
    except Exception as exc:
        print(f"\n[{ticker}] EXCEPTION: {type(exc).__name__}: {exc}")
        return False

    print(f"\n[{ticker}] Stream ended without 'done' event (last: {last_event_type})")
    return False


async def health_check(client: httpx.AsyncClient) -> bool:
    """Verify backend is reachable before attempting pre-warm."""
    try:
        r = await client.get(f"{BACKEND_URL}/health", timeout=10.0)
        if r.status_code == 200:
            data = r.json()
            print(f"Health OK: {data}")
            return True
        print(f"Health check failed: HTTP {r.status_code}")
        return False
    except Exception as exc:
        print(f"Health check error: {exc}")
        return False


async def main() -> int:
    print(f"AltBrief Pre-warm")
    print(f"Backend: {BACKEND_URL}")
    print(f"Tickers: {', '.join(DEMO_TICKERS)}")
    print("=" * 50)

    async with httpx.AsyncClient(
        follow_redirects=True,
        headers={"Accept": "text/event-stream", "Cache-Control": "no-cache"},
    ) as client:
        # 1. Health check
        print("\nChecking backend health...")
        if not await health_check(client):
            print("Backend unreachable — run `docker compose up` or check Fly.io")
            return 1

        # 2. Pre-warm tickers SEQUENTIALLY (avoid concurrent cost spikes)
        results: dict[str, bool] = {}
        for ticker in DEMO_TICKERS:
            results[ticker] = await prewarm_ticker(client, ticker)

    # 3. Summary
    print("\n" + "=" * 50)
    print("Pre-warm summary:")
    all_ok = True
    for ticker, ok in results.items():
        icon = "OK" if ok else "FAIL"
        print(f"  {icon}  {ticker}")
        if not ok:
            all_ok = False

    if all_ok:
        print("\nAll tickers cached. Demo is ready.")
        return 0
    else:
        print("\nSome tickers failed. Check logs above and retry.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
