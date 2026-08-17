#!/usr/bin/env python3
"""
scripts/capture_demo_cache.py
==============================
Runs the full HAPPY_PATH demo sequence against the live backend and captures
all responses into data/demo/demo_cache.json.

Usage:
    # Backend must already be running on port 8000:
    #   .venv/bin/uvicorn wizard.backend.app:app --host 127.0.0.1 --port 8000
    .venv/bin/python scripts/capture_demo_cache.py

The cache is keyed by (endpoint, payload_hash) so the Streamlit UI can serve
gold responses sub-second without hitting the backend at all — crash-safe for demo day.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx

BASE_URL = "http://127.0.0.1:8000"
DEMO_SESSION_ID = "demo-gold-session-001"
EAF04_ASSET_ID = "EAF-04"

CACHE_PATH = Path(__file__).resolve().parents[1] / "data" / "demo" / "demo_cache.json"


def _client() -> httpx.Client:
    return httpx.Client(
        base_url=BASE_URL,
        timeout=httpx.Timeout(connect=5.0, read=60.0, write=30.0, pool=5.0),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
    )


def _key(endpoint: str, payload: dict | None = None) -> str:
    raw = endpoint + json.dumps(payload or {}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def wait_for_backend(client: httpx.Client, retries: int = 30) -> bool:
    print(f"Waiting for backend on {BASE_URL}...")
    for i in range(retries):
        try:
            r = client.get("/v1/health")
            if r.status_code == 200:
                print(f"  Backend ready (attempt {i+1}): {r.json()['status']}")
                return True
        except Exception as e:
            pass
        time.sleep(2)
    print("ERROR: Backend did not come up in time.")
    return False


def capture(client: httpx.Client, cache: dict) -> None:
    """Run every demo beat and save response to cache."""

    # ─── Beat 0: Health check ──────────────────────────────────────────────────
    print("\n[0] Health check...")
    try:
        r = client.get("/v1/health")
        data = r.json()
        key = _key("/v1/health")
        cache[key] = {
            "endpoint": "/v1/health",
            "method": "GET",
            "payload": None,
            "response": data,
            "status_code": r.status_code,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "note": "Liveness probe — shows DB + scheduler + circuit breaker state",
        }
        print(f"  OK  status={data.get('status')} db={data.get('db_ok')} sched={data.get('scheduler_running')}")
    except Exception as e:
        print(f"  WARN: {e}")

    # ─── Beat 1: Sensor state (all assets) ────────────────────────────────────
    print("\n[1] Sensor state (all assets)...")
    try:
        r = client.get("/v1/sensor/state")
        data = r.json()
        key = _key("/v1/sensor/state")
        cache[key] = {
            "endpoint": "/v1/sensor/state",
            "method": "GET",
            "payload": None,
            "response": data,
            "status_code": r.status_code,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "note": "Dashboard beat — shows all asset health and RUL gauges",
        }
        total = data.get("total_assets", 0)
        critical = data.get("critical_asset_count", 0)
        print(f"  OK  total_assets={total} critical={critical}")
    except Exception as e:
        print(f"  WARN: {e}")

    # ─── Beat 2: Inject fault (EAF-04 CRITICAL — the WOW moment) ──────────────
    print("\n[2] Inject fault → EAF-04 CRITICAL alert (the 90-second wow moment)...")
    try:
        r = client.post("/v1/demo/inject_fault")
        data = r.json()
        key = _key("/v1/demo/inject_fault")
        cache[key] = {
            "endpoint": "/v1/demo/inject_fault",
            "method": "POST",
            "payload": None,
            "response": data,
            "status_code": r.status_code,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "note": "WOW MOMENT: Fires EAF-04 CRITICAL alert with RUL=11.3h, anomaly=0.94. "
                    "Proves agentic proactive alerting with zero user input.",
        }
        print(f"  OK  status={data.get('status')} severity={data.get('severity')} rul_days={data.get('rul_days')}")
        print(f"      alert_entity_id={data.get('alert_entity_id')}")
    except Exception as e:
        print(f"  WARN: {e}")

    # ─── Beat 3: Alert list (shows the injected CRITICAL) ─────────────────────
    print("\n[3] Alert list (confirm CRITICAL visible)...")
    try:
        r = client.get("/v1/alerts", params={"limit": 10})
        data = r.json()
        key = _key("/v1/alerts", {"limit": 10})
        cache[key] = {
            "endpoint": "/v1/alerts",
            "method": "GET",
            "payload": {"limit": 10},
            "response": data,
            "status_code": r.status_code,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "note": "Alert history — shows EAF-04 CRITICAL with RUL, anomaly score, spares warning",
        }
        items = data.get("items", [])
        print(f"  OK  total_alerts={len(items)}")
        for item in items[:3]:
            print(f"      [{item.get('risk_level','?').upper()}] {item.get('asset_id')} — {item.get('alert_type')}")
    except Exception as e:
        print(f"  WARN: {e}")

    # ─── Beat 4: Chat — EAF-04 diagnosis NL query ─────────────────────────────
    print("\n[4] Chat query — EAF-04 root cause and maintenance recommendation...")
    payload_4 = {
        "session_id": DEMO_SESSION_ID,
        "equipment_id": EAF04_ASSET_ID,
        "query": "What is the root cause for EAF-04 bearing failure and what should I do right now?",
    }
    try:
        r = client.post("/v1/chat", json=payload_4)
        data = r.json()
        key = _key("/v1/chat", payload_4)
        cache[key] = {
            "endpoint": "/v1/chat",
            "method": "POST",
            "payload": payload_4,
            "response": data,
            "status_code": r.status_code,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "latency_ms": data.get("latency_ms"),
            "note": "Core chat beat — NL diagnosis query → source-cited RCA + step-by-step plan. "
                    "Proves FR1 (LLM reasoning) + FR2 (knowledge integration) + FR4 (explainable).",
        }
        rec = data.get("recommendation") or {}
        print(f"  OK  latency_ms={data.get('latency_ms')}")
        print(f"      recommendation_id={rec.get('recommendation_id')}")
        print(f"      narrative_summary={str(rec.get('narrative_summary',''))[:100]}...")
        trace = data.get("agent_trace") or []
        print(f"      agent_trace steps={len(trace)}")
    except Exception as e:
        print(f"  WARN: {e}")

    # ─── Beat 5: Chat — RUL query (spare parts angle) ─────────────────────────
    print("\n[5] Chat query — RUL and spares availability for EAF-04...")
    payload_5 = {
        "session_id": DEMO_SESSION_ID,
        "equipment_id": EAF04_ASSET_ID,
        "query": "How many hours do we have before EAF-04 bearing fails? Are spare parts available?",
    }
    try:
        r = client.post("/v1/chat", json=payload_5)
        data = r.json()
        key = _key("/v1/chat", payload_5)
        cache[key] = {
            "endpoint": "/v1/chat",
            "method": "POST",
            "payload": payload_5,
            "response": data,
            "status_code": r.status_code,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "latency_ms": data.get("latency_ms"),
            "note": "RUL + spares beat — shows RUL_P50=11.3h + out-of-stock bearing + 14-day lead time. "
                    "Unique differentiator: spare-parts procurement angle most competitors miss.",
        }
        rec = data.get("recommendation") or {}
        print(f"  OK  latency_ms={data.get('latency_ms')}")
        spares = rec.get("spares_procurement_warning")
        print(f"      spares_procurement_warning={str(spares)[:100]}")
    except Exception as e:
        print(f"  WARN: {e}")

    # ─── Beat 6: Chat — multi-turn follow-up (proves context retention) ────────
    print("\n[6] Chat — multi-turn follow-up: prioritization queue...")
    payload_6 = {
        "session_id": DEMO_SESSION_ID,   # same session — multi-turn
        "equipment_id": EAF04_ASSET_ID,
        "query": "Given the criticality, prioritize all outstanding maintenance tasks for EAF bay.",
    }
    try:
        r = client.post("/v1/chat", json=payload_6)
        data = r.json()
        key = _key("/v1/chat", payload_6)
        cache[key] = {
            "endpoint": "/v1/chat",
            "method": "POST",
            "payload": payload_6,
            "response": data,
            "status_code": r.status_code,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "latency_ms": data.get("latency_ms"),
            "note": "Multi-turn beat — same session_id proves context retention across turns (LangGraph SqliteSaver). "
                    "Shows WRPS prioritization across EAF bay equipment.",
        }
        rec = data.get("recommendation") or {}
        print(f"  OK  latency_ms={data.get('latency_ms')}")
        risk = rec.get("priority") or rec.get("risk_level")
        print(f"      risk/priority={risk}")
    except Exception as e:
        print(f"  WARN: {e}")

    # ─── Beat 7: Session state (traceable diagnosis chain) ────────────────────
    print("\n[7] Session state — LangGraph checkpoint (traceable chain)...")
    try:
        r = client.get(f"/v1/session/{DEMO_SESSION_ID}/state")
        data = r.json()
        key = _key(f"/v1/session/{DEMO_SESSION_ID}/state")
        cache[key] = {
            "endpoint": f"/v1/session/{DEMO_SESSION_ID}/state",
            "method": "GET",
            "payload": None,
            "response": data,
            "status_code": r.status_code,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "note": "Explainability beat — shows full LangGraph MaintenanceState checkpoint: "
                    "diagnosis + RCA + RUL + risk_level + cited_sources + agent_trace. "
                    "Proves FR4 (explainable) + Axis C (technical depth).",
        }
        state = data.get("state") or {}
        print(f"  OK  state_keys={list(state.keys())}")
        print(f"      note={data.get('note','')}")
    except Exception as e:
        print(f"  WARN: {e}")

    # ─── Beat 8: Feedback (thumbs-down correction → proves FR6) ───────────────
    print("\n[8] Feedback — engineer thumbs-down + risk correction...")
    payload_8 = {
        "session_id": DEMO_SESSION_ID,
        "equipment_id": EAF04_ASSET_ID,
        "recommendation_id": "demo-rec-001",
        "thumbs_up": False,
        "correction": "The bearing failure is actually due to misalignment, not thermal overload. Please update the RCA.",
        "corrected_risk_level": "critical",
    }
    try:
        r = client.post("/v1/feedback", json=payload_8)
        data = r.json()
        key = _key("/v1/feedback", payload_8)
        cache[key] = {
            "endpoint": "/v1/feedback",
            "method": "POST",
            "payload": payload_8,
            "response": data,
            "status_code": r.status_code,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "note": "Feedback loop beat — one-turn correction triggers WRPS weight update. "
                    "Next query will show [ENGINEER CORRECTION APPLIED] badge. Proves FR6.",
        }
        print(f"  OK  feedback_id={data.get('feedback_id')}")
        print(f"      weights_updated={data.get('weights_updated')}")
        print(f"      message={data.get('message','')[:80]}")
    except Exception as e:
        print(f"  WARN: {e}")

    # ─── Beat 9: Re-query after feedback (correction badge visible) ────────────
    print("\n[9] Re-query after feedback — expects [ENGINEER CORRECTION APPLIED]...")
    payload_9 = {
        "session_id": f"demo-gold-session-002",  # fresh session for clean capture
        "equipment_id": EAF04_ASSET_ID,
        "query": "Re-diagnose EAF-04 with the engineer correction applied — focus on misalignment.",
    }
    try:
        r = client.post("/v1/chat", json=payload_9)
        data = r.json()
        key = _key("/v1/chat", payload_9)
        cache[key] = {
            "endpoint": "/v1/chat",
            "method": "POST",
            "payload": payload_9,
            "response": data,
            "status_code": r.status_code,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "latency_ms": data.get("latency_ms"),
            "note": "Post-feedback re-query beat — corrected RCA with [ENGINEER CORRECTION APPLIED] badge. "
                    "Closes the feedback loop demo arc.",
        }
        rec = data.get("recommendation") or {}
        print(f"  OK  latency_ms={data.get('latency_ms')}")
        narrative = str(rec.get("narrative_summary", ""))[:120]
        print(f"      narrative={narrative}...")
    except Exception as e:
        print(f"  WARN: {e}")

    # ─── Beat 10: Demo start (natural degradation path) ───────────────────────
    print("\n[10] Demo start — natural 60s degradation playback...")
    try:
        r = client.post("/v1/demo/start")
        data = r.json()
        key = _key("/v1/demo/start")
        cache[key] = {
            "endpoint": "/v1/demo/start",
            "method": "POST",
            "payload": None,
            "response": data,
            "status_code": r.status_code,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "note": "Natural degradation path — 5 steps × 15s. Use inject_fault for instant demo.",
        }
        print(f"  OK  status={data.get('status')} expected_in_seconds={data.get('eaf04_critical_expected_in_seconds')}")
    except Exception as e:
        print(f"  WARN: {e}")

    # ─── Beat 11: Demo reset (clean state for re-run) ─────────────────────────
    print("\n[11] Demo reset — clean state for recording re-run...")
    try:
        r = client.post("/v1/demo/reset")
        data = r.json()
        key = _key("/v1/demo/reset")
        cache[key] = {
            "endpoint": "/v1/demo/reset",
            "method": "POST",
            "payload": None,
            "response": data,
            "status_code": r.status_code,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "note": "Reset — stops playback + clears cooldowns. Demo can be rerun cleanly.",
        }
        print(f"  OK  status={data.get('status')}")
    except Exception as e:
        print(f"  WARN: {e}")


def main() -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with _client() as client:
        if not wait_for_backend(client):
            sys.exit(1)

        cache: dict = {}
        capture(client, cache)

    # Attach metadata
    result = {
        "schema_version": "1.0",
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "backend_url": BASE_URL,
        "demo_session_id": DEMO_SESSION_ID,
        "llm_note": (
            "These responses were captured with Gemini 2.0 Flash as the LLM. "
            "If the LLM was rate-limited during capture, some narrative fields will be "
            "deterministic fallback templates. Re-run this script with a working GEMINI_API_KEY "
            "to upgrade to full LLM-generated responses. "
            "The agentic structure (agent_trace, cited_sources, schemas) is identical regardless."
        ),
        "beats": cache,
    }

    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)

    print(f"\nDemo cache saved: {CACHE_PATH}")
    print(f"Total beats captured: {len(cache)}")
    beats_ok = sum(1 for v in cache.values() if v.get("status_code", 0) < 400)
    print(f"Beats OK (2xx): {beats_ok}/{len(cache)}")

    if beats_ok < len(cache):
        print("\nWARN: Some beats returned errors. Check backend logs.")
    else:
        print("All beats captured successfully.")


if __name__ == "__main__":
    main()
