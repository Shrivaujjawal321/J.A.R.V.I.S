#!/usr/bin/env python3
"""
scripts/full_demo_runner.py
============================
Complete demo runner: init DB, start backend on :8000, run all beats,
capture live responses to data/demo/demo_cache.json, verify results.

This is the authoritative capture script for demo day preparation.

Usage:
    cd maintenance-wizard
    .venv/bin/python scripts/full_demo_runner.py

Requirements:
    - .venv must be set up (make setup)
    - wizard package installed as editable (pip install -e .)
    - GEMINI_API_KEY in .env (optional — system falls back to deterministic templates)
"""
from __future__ import annotations

import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
os.chdir(REPO)
sys.path.insert(0, str(REPO))

PYTHON = REPO / ".venv" / "bin" / "python"
UVICORN = REPO / ".venv" / "bin" / "uvicorn"
PORT = 8000
BASE_URL = f"http://127.0.0.1:{PORT}"
DEMO_DIR = REPO / "data" / "demo"
LOG_PATH = DEMO_DIR / "backend_capture.log"
CACHE_PATH = DEMO_DIR / "demo_cache.json"

DEMO_SESSION_ID = "demo-gold-session-001"
EAF04_ASSET_ID = "EAF-04"


def step(n: int, label: str) -> None:
    print(f"\n{'='*60}")
    print(f"[Step {n}] {label}")
    print('='*60)


def init_db() -> None:
    step(1, "Initialize database")
    from wizard.core.db import init_db as _init
    _init()
    print("  DB initialized at data/wizard.db")


def start_backend() -> subprocess.Popen:
    step(2, "Start backend on :8000")
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "BACKEND_PORT": str(PORT)}
    log_f = open(LOG_PATH, "w")
    proc = subprocess.Popen(
        [str(UVICORN), "wizard.backend.app:app",
         "--host", "127.0.0.1",
         "--port", str(PORT),
         "--workers", "1"],
        env=env,
        stdout=log_f,
        stderr=subprocess.STDOUT,
        cwd=str(REPO),
    )
    print(f"  Backend PID: {proc.pid}")
    print(f"  Log: {LOG_PATH}")
    return proc


def wait_for_health(max_seconds: int = 90) -> bool:
    step(3, f"Wait for backend health ({max_seconds}s max)")
    import httpx
    client = httpx.Client(base_url=BASE_URL, timeout=5.0)
    start = time.monotonic()
    while time.monotonic() - start < max_seconds:
        try:
            r = client.get("/v1/health")
            if r.status_code == 200:
                d = r.json()
                print(f"  OK  status={d.get('status')} db={d.get('db_ok')} sched={d.get('scheduler_running')}")
                client.close()
                return True
        except Exception:
            pass
        elapsed = int(time.monotonic() - start)
        print(f"  Waited {elapsed}s...")
        time.sleep(3)
    client.close()
    print("  ERROR: Backend did not come up in time")
    return False


def run_capture() -> dict:
    step(4, "Run HAPPY_PATH capture")
    import httpx

    cache: dict = {}

    def _key(endpoint: str, payload: dict | None = None) -> str:
        raw = endpoint + json.dumps(payload or {}, sort_keys=True)
        return "k_" + hashlib.sha256(raw.encode()).hexdigest()[:12]

    with httpx.Client(
        base_url=BASE_URL,
        timeout=httpx.Timeout(connect=5.0, read=90.0, write=30.0, pool=5.0),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
    ) as client:

        def do(method: str, path: str, payload: dict | None = None,
               params: dict | None = None, label: str = "", note: str = "") -> dict | None:
            try:
                if method == "GET":
                    r = client.get(path, params=params)
                else:
                    r = client.post(path, json=payload or {})
                data = r.json()
                key = _key(path, payload or params)
                cache[key] = {
                    "endpoint": path,
                    "method": method,
                    "payload": payload or params,
                    "response": data,
                    "status_code": r.status_code,
                    "captured_at": datetime.now(timezone.utc).isoformat(),
                    "note": note,
                }
                if r.status_code < 400:
                    print(f"  OK  [{label}] status={r.status_code}")
                else:
                    print(f"  WARN [{label}] status={r.status_code}")
                return data
            except Exception as e:
                print(f"  ERROR [{label}]: {e}")
                return None

        # Beat 0: Health
        do("GET", "/v1/health", label="health",
           note="Liveness probe — DB + scheduler + circuit breaker state")

        # Beat 1: Sensor state
        do("GET", "/v1/sensor/state", label="sensor_state",
           note="Dashboard beat — all asset health and RUL gauges. EAF-04 is CRITICAL.")

        # Beat 2: inject_fault (THE WOW MOMENT)
        inject = do("POST", "/v1/demo/inject_fault", label="inject_fault",
                    note="WOW MOMENT: EAF-04 CRITICAL alert — RUL=11.3h, anomaly=0.94, spares OUT OF STOCK")
        if inject:
            print(f"      severity={inject.get('severity')} rul_h={inject.get('rul_days', 0)*24:.1f}h")

        # Beat 3: Alert list
        do("GET", "/v1/alerts", params={"limit": 10}, label="alerts",
           note="Alert history — shows EAF-04 CRITICAL with RUL, anomaly score, spares warning")

        # Beat 4: Chat Q1 — RCA query (the main NL query beat)
        payload_q1 = {
            "session_id": DEMO_SESSION_ID,
            "equipment_id": EAF04_ASSET_ID,
            "query": "What is the root cause for EAF-04 bearing failure and what should I do right now?",
        }
        chat1 = do("POST", "/v1/chat", payload=payload_q1, label="chat_q1",
                   note="Core NL query — 6 agents streaming: diagnosis→rca→rul→prioritization→plan→report. Source-cited.")
        if chat1:
            rec = chat1.get("recommendation", {})
            trace = chat1.get("agent_trace", [])
            print(f"      latency_ms={chat1.get('latency_ms'):.0f} steps={len(trace)} priority={rec.get('priority')}")

        # Beat 5: Chat Q2 — RUL + spares
        payload_q2 = {
            "session_id": DEMO_SESSION_ID,
            "equipment_id": EAF04_ASSET_ID,
            "query": "How many hours do we have before EAF-04 bearing fails? Are spare parts available?",
        }
        do("POST", "/v1/chat", payload=payload_q2, label="chat_q2",
           note="RUL + spares beat — P50=11.3h, SKF-6310-2RS1 OUT OF STOCK, 14-day lead time")

        # Beat 6: Chat Q3 — multi-turn prioritization
        payload_q3 = {
            "session_id": DEMO_SESSION_ID,
            "equipment_id": EAF04_ASSET_ID,
            "query": "Given the criticality, prioritize all outstanding maintenance tasks for EAF bay.",
        }
        do("POST", "/v1/chat", payload=payload_q3, label="chat_q3_multiturn",
           note="Multi-turn beat — same session_id proves LangGraph SqliteSaver context retention")

        # Beat 7: Session state (traceable chain)
        do("GET", f"/v1/session/{DEMO_SESSION_ID}/state", label="session_state",
           note="Explainability — full LangGraph checkpoint: cited_sources + agent_trace + WRPS")

        # Beat 8: Feedback
        payload_fb = {
            "session_id": DEMO_SESSION_ID,
            "equipment_id": EAF04_ASSET_ID,
            "recommendation_id": "demo-rec-001",
            "thumbs_up": False,
            "correction": "The root cause is misalignment, not thermal overload. Please update the RCA.",
            "corrected_risk_level": "critical",
        }
        fb = do("POST", "/v1/feedback", payload=payload_fb, label="feedback",
                note="FR6 feedback loop — EMA weight update. Next response shows [ENGINEER CORRECTION APPLIED]")
        if fb:
            print(f"      feedback_id={fb.get('feedback_id')} weights_updated={fb.get('weights_updated')}")

        # Beat 9: Re-query post-feedback
        payload_q4 = {
            "session_id": "demo-gold-session-002",
            "equipment_id": EAF04_ASSET_ID,
            "query": "Re-diagnose EAF-04 with the engineer correction applied — focus on misalignment.",
        }
        do("POST", "/v1/chat", payload=payload_q4, label="chat_post_feedback",
           note="Post-feedback — response has [ENGINEER CORRECTION APPLIED] badge, updated RCA framing")

        # Beat 10: Demo start (natural path)
        do("POST", "/v1/demo/start", label="demo_start",
           note="Natural degradation path — 5 steps × 15s. Use inject_fault for instant demo.")

        # Beat 11: Demo reset
        do("POST", "/v1/demo/reset", label="demo_reset",
           note="Reset — stops playback, clears EAF-04 cooldowns. Demo can be rerun cleanly.")

    return cache


def save_cache(cache: dict) -> None:
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    ok_count = sum(1 for v in cache.values() if isinstance(v, dict) and v.get("status_code", 0) < 400)
    result = {
        "schema_version": "1.0",
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "backend_url": BASE_URL,
        "demo_session_id": DEMO_SESSION_ID,
        "llm_note": (
            "These responses were captured live from the running system on port 8000. "
            "If GEMINI_API_KEY is active: LLM-generated narratives. "
            "If rate-limited: deterministic fallback templates (agentic structure identical). "
            "Re-run this script with a working key to upgrade narrative fields."
        ),
        "capture_stats": {
            "total_beats": len(cache),
            "beats_ok_2xx": ok_count,
            "demo_ready": ok_count >= 8,
        },
        "beats": cache,
    }
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\n  Saved: {CACHE_PATH}")
    print(f"  Beats: {len(cache)} total, {ok_count} OK (2xx)")


def verify_beats(cache: dict) -> int:
    step(5, "Verify HAPPY_PATH beats")
    required_beats = [
        "/v1/health",
        "/v1/demo/inject_fault",
        "/v1/alerts",
        "/v1/chat",
        "/v1/feedback",
    ]
    fails = 0
    for beat_key, beat in cache.items():
        endpoint = beat.get("endpoint", "")
        sc = beat.get("status_code", 0)
        note = beat.get("note", "")[:60]
        status = "PASS" if sc < 400 else "FAIL"
        if sc >= 400:
            fails += 1
        print(f"  {status}  [{sc}] {endpoint} — {note}")

    print(f"\nResult: {fails} failures / {len(cache)} beats")
    return fails


def main() -> None:
    proc = None
    try:
        init_db()
        proc = start_backend()
        if not wait_for_health():
            print("\nERROR: Backend failed to start. Check:")
            print(f"  {LOG_PATH}")
            if LOG_PATH.exists():
                lines = LOG_PATH.read_text().splitlines()
                for line in lines[-30:]:
                    print(f"  {line}")
            sys.exit(1)

        cache = run_capture()
        save_cache(cache)
        fails = verify_beats(cache)

        if fails == 0:
            print("\nAll beats PASS — system is demo-ready.")
        else:
            print(f"\nWARN: {fails} beats failed — check backend logs.")

    finally:
        if proc:
            step(6, "Shutdown backend")
            try:
                proc.send_signal(signal.SIGTERM)
                proc.wait(timeout=10)
                print("  Backend stopped.")
            except Exception:
                proc.kill()


if __name__ == "__main__":
    main()
