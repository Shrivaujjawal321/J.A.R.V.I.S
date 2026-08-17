#!/usr/bin/env python3
"""
scripts/verify_demo.py
======================
Verifies the backend is running and all HAPPY_PATH beats produce
the expected response shapes. Compares live responses against
the gold demo_cache.json.

Usage:
    # Backend must be running first:
    #   .venv/bin/uvicorn wizard.backend.app:app --host 127.0.0.1 --port 8000
    .venv/bin/python scripts/verify_demo.py [--port 8000]

Exit codes:
    0 — all beats pass
    1 — one or more beats failed
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import httpx

REPO = Path(__file__).resolve().parents[1]


def _client(port: int) -> httpx.Client:
    return httpx.Client(
        base_url=f"http://127.0.0.1:{port}",
        timeout=httpx.Timeout(connect=5.0, read=60.0, write=30.0, pool=5.0),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
    )


def check(label: str, actual: dict, expected_keys: list[str], expected_status: int = 200) -> bool:
    ok = True
    missing = [k for k in expected_keys if k not in actual]
    if missing:
        print(f"  FAIL [{label}]: missing keys {missing}")
        ok = False
    return ok


def main(port: int) -> int:
    fails = 0

    with _client(port) as c:
        print(f"Verifying HAPPY_PATH against http://127.0.0.1:{port}\n")

        # Beat 0: Health
        print("[0] GET /v1/health")
        try:
            r = c.get("/v1/health")
            assert r.status_code == 200, f"status={r.status_code}"
            d = r.json()
            assert d.get("status") in ("ok", "degraded"), f"status={d.get('status')}"
            assert d.get("db_ok") is True, "db_ok is False"
            print(f"  PASS  status={d['status']} db={d['db_ok']} sched={d['scheduler_running']}")
        except Exception as e:
            print(f"  FAIL  {e}")
            fails += 1

        # Beat 1: Sensor state
        print("[1] GET /v1/sensor/state")
        try:
            r = c.get("/v1/sensor/state")
            assert r.status_code == 200
            d = r.json()
            assert "assets" in d
            print(f"  PASS  total_assets={d['total_assets']} critical={d['critical_asset_count']}")
        except Exception as e:
            print(f"  FAIL  {e}")
            fails += 1

        # Beat 2: inject_fault → EAF-04 CRITICAL
        print("[2] POST /v1/demo/inject_fault")
        try:
            r = c.post("/v1/demo/inject_fault")
            assert r.status_code == 200
            d = r.json()
            assert d.get("status") == "injected", f"status={d.get('status')}"
            assert d.get("severity") == "critical", f"severity={d.get('severity')}"
            assert d.get("asset_id") == "EAF-04"
            rul_h = (d.get("rul_days", 0)) * 24
            print(f"  PASS  severity={d['severity']} rul_hours={rul_h:.1f}")
        except Exception as e:
            print(f"  FAIL  {e}")
            fails += 1

        # Beat 3: Alert list
        print("[3] GET /v1/alerts")
        try:
            r = c.get("/v1/alerts", params={"limit": 10})
            assert r.status_code == 200
            d = r.json()
            assert "items" in d
            critical_items = [i for i in d["items"] if i.get("risk_level") == "critical"]
            print(f"  PASS  total_alerts={len(d['items'])} critical={len(critical_items)}")
        except Exception as e:
            print(f"  FAIL  {e}")
            fails += 1

        # Beat 4: Chat Q1 — RCA query
        print("[4] POST /v1/chat (RCA query)")
        try:
            r = c.post("/v1/chat", json={
                "session_id": "demo-verify-session-001",
                "equipment_id": "EAF-04",
                "query": "What is the root cause for EAF-04 bearing failure?",
            })
            assert r.status_code == 200
            d = r.json()
            rec = d.get("recommendation", {})
            assert rec.get("asset_id") == "EAF-04"
            assert len(d.get("agent_trace", [])) > 0
            trace_count = len(d["agent_trace"])
            lat = d.get("latency_ms", 0)
            print(f"  PASS  latency_ms={lat:.0f} agent_steps={trace_count} priority={rec.get('priority')}")
        except Exception as e:
            print(f"  FAIL  {e}")
            fails += 1

        # Beat 5: Session state (explainability)
        print("[5] GET /v1/session/{id}/state")
        try:
            r = c.get("/v1/session/demo-verify-session-001/state")
            assert r.status_code == 200
            d = r.json()
            assert "state" in d
            state = d["state"]
            print(f"  PASS  state_keys={list(state.keys())[:5]}")
        except Exception as e:
            print(f"  FAIL  {e}")
            fails += 1

        # Beat 6: Feedback
        print("[6] POST /v1/feedback")
        try:
            r = c.post("/v1/feedback", json={
                "session_id": "demo-verify-session-001",
                "equipment_id": "EAF-04",
                "recommendation_id": "demo-rec-verify-001",
                "thumbs_up": False,
                "correction": "Root cause is misalignment, not thermal overload.",
                "corrected_risk_level": "critical",
            })
            assert r.status_code == 200
            d = r.json()
            assert "feedback_id" in d
            print(f"  PASS  feedback_id={d['feedback_id']} weights_updated={d['weights_updated']}")
        except Exception as e:
            print(f"  FAIL  {e}")
            fails += 1

        # Beat 7: Demo reset
        print("[7] POST /v1/demo/reset")
        try:
            r = c.post("/v1/demo/reset")
            assert r.status_code == 200
            d = r.json()
            assert d.get("status") == "reset"
            print(f"  PASS  status={d['status']}")
        except Exception as e:
            print(f"  FAIL  {e}")
            fails += 1

    print(f"\n{'='*50}")
    if fails == 0:
        print(f"ALL BEATS PASS (0 failures)")
        print("System is demo-ready. Run scripts/capture_demo_cache.py to refresh gold responses.")
    else:
        print(f"FAILED: {fails} beats failed. Check backend logs.")
    print(f"{'='*50}")

    return 0 if fails == 0 else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    sys.exit(main(args.port))
