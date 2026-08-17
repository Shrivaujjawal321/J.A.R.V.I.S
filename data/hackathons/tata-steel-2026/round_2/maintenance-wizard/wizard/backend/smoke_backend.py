"""
wizard.backend.smoke_backend
=============================
Self-contained smoke test for the FastAPI backend.

Verifies:
  [1] App imports without error
  [2] GET /v1/health → 200 OK + correct shape
  [3] POST /v1/chat → 200 OK + MaintenanceRecommendation present
  [4] GET /v1/sensor/state → 200 OK (even with empty DB)
  [5] POST /v1/feedback → 200 OK
  [6] GET /v1/session/{id}/state → 200 OK
  [7] GET /v1/alerts → 200 OK (empty list is fine)
  [8] WRPS engine: score_maintenance_priority on unknown asset → returns LOW RiskScore
  [9] py_compile checks for all backend modules

Run:
    cd maintenance-wizard
    WIZARD_TESTING=1 python -m wizard.backend.smoke_backend
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

# Set testing mode to disable APScheduler demo timer
os.environ["WIZARD_TESTING"] = "1"

# Use a temp DB so smoke test doesn't pollute wizard.db
_tmp_dir = tempfile.mkdtemp(prefix="wizard_smoke_")
os.environ.setdefault("DB_PATH", str(Path(_tmp_dir) / "smoke_wizard.db"))

import py_compile

# ---------------------------------------------------------------------------
# py_compile checks
# ---------------------------------------------------------------------------

_BACKEND_DIR = Path(__file__).parent

_MODULES_TO_CHECK = [
    _BACKEND_DIR / "schemas.py",
    _BACKEND_DIR / "middleware.py",
    _BACKEND_DIR / "alerting.py",
    _BACKEND_DIR / "wrps.py",
    _BACKEND_DIR / "graph_placeholder.py",
    _BACKEND_DIR / "app.py",
    _BACKEND_DIR / "__init__.py",
]

print("=" * 60)
print("SMOKE TEST: wizard.backend")
print("=" * 60)

_passed = 0
_failed = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _passed, _failed
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {name}", f"— {detail}" if detail else "")
    if ok:
        _passed += 1
    else:
        _failed += 1


print("\n[Phase 1] py_compile checks")
for mod_path in _MODULES_TO_CHECK:
    try:
        py_compile.compile(str(mod_path), doraise=True)
        check(f"py_compile: {mod_path.name}", True)
    except py_compile.PyCompileError as exc:
        check(f"py_compile: {mod_path.name}", False, str(exc))

# ---------------------------------------------------------------------------
# FastAPI TestClient checks
# ---------------------------------------------------------------------------

print("\n[Phase 2] FastAPI endpoint checks (TestClient)")

try:
    from fastapi.testclient import TestClient
    from wizard.backend.app import app

    # IMPORTANT: TestClient must be used as a context manager so that the FastAPI
    # lifespan (init_db → CREATE TABLE + APScheduler start) is properly executed
    # before any requests are made.  Without 'with TestClient(...) as client:',
    # each request spawns a fresh anyio portal that does NOT send a lifespan.startup
    # message to the ASGI app, so init_db() is never called and all SQL queries
    # raise "no such table".
    _tc = TestClient(app, raise_server_exceptions=False)
    _tc.__enter__()  # enter lifespan (init_db + scheduler)
    client = _tc
    _client_ok = True
    check("TestClient: app imported", True)
except ImportError as exc:
    check("TestClient: app imported", False, str(exc))
    _client_ok = False
    _tc = None  # type: ignore[assignment]
except Exception as exc:
    check("TestClient: app imported", False, str(exc))
    _client_ok = False
    _tc = None  # type: ignore[assignment]

if _client_ok:
    # [2] Health
    try:
        resp = client.get("/v1/health")
        ok = resp.status_code == 200
        body = resp.json()
        has_fields = all(k in body for k in ("status", "db_ok", "scheduler_running", "circuit_breaker_state"))
        check("GET /v1/health → 200", ok and has_fields, f"status={body.get('status')}, db_ok={body.get('db_ok')}")
    except Exception as exc:
        check("GET /v1/health → 200", False, str(exc))

    # [3] Chat sync
    try:
        resp = client.post(
            "/v1/chat",
            json={
                "session_id": "smoke-session-001",
                "equipment_id": "EAF-04",
                "query": "What is the current maintenance status?",
            },
        )
        ok = resp.status_code == 200
        body = resp.json()
        has_rec = "recommendation" in body
        has_steps = has_rec and len(body["recommendation"].get("action_steps", [])) > 0
        check(
            "POST /v1/chat → 200",
            ok and has_rec,
            f"has_recommendation={has_rec}, steps={len(body.get('recommendation', {}).get('action_steps', []))}",
        )
    except Exception as exc:
        check("POST /v1/chat → 200", False, str(exc))

    # [4] Sensor state
    try:
        resp = client.get("/v1/sensor/state")
        ok = resp.status_code == 200
        body = resp.json()
        check(
            "GET /v1/sensor/state → 200",
            ok,
            f"total_assets={body.get('total_assets', 'N/A')}",
        )
    except Exception as exc:
        check("GET /v1/sensor/state → 200", False, str(exc))

    # [5] Feedback
    try:
        resp = client.post(
            "/v1/feedback",
            json={
                "session_id": "smoke-session-001",
                "equipment_id": "EAF-04",
                "recommendation_id": "rec-placeholder-001",
                "thumbs_up": False,
                "correction": "The risk should be CRITICAL, not MEDIUM",
                "corrected_risk_level": "critical",
            },
        )
        ok = resp.status_code == 200
        body = resp.json()
        check("POST /v1/feedback → 200", ok, f"feedback_id={body.get('feedback_id', 'N/A')}")
    except Exception as exc:
        check("POST /v1/feedback → 200", False, str(exc))

    # [6] Session state
    try:
        resp = client.get("/v1/session/smoke-session-001/state")
        ok = resp.status_code == 200
        body = resp.json()
        check(
            "GET /v1/session/{id}/state → 200",
            ok,
            f"has_state={('state' in body)}",
        )
    except Exception as exc:
        check("GET /v1/session/{id}/state → 200", False, str(exc))

    # [7] Alert history
    try:
        resp = client.get("/v1/alerts")
        ok = resp.status_code == 200
        body = resp.json()
        check(
            "GET /v1/alerts → 200",
            ok,
            f"items={len(body.get('items', []))}",
        )
    except Exception as exc:
        check("GET /v1/alerts → 200", False, str(exc))

    # Close lifespan properly (scheduler shutdown)
    if _tc is not None:
        try:
            _tc.__exit__(None, None, None)
        except Exception:
            pass

# ---------------------------------------------------------------------------
# WRPS engine check (no DB needed for unknown asset)
# ---------------------------------------------------------------------------

print("\n[Phase 3] WRPS engine check")

try:
    from wizard.backend.wrps import score_maintenance_priority, get_current_weights

    score = score_maintenance_priority("UNKNOWN-ASSET-000")
    ok = score.asset_id == "UNKNOWN-ASSET-000" and score.wrps == 0.0
    check(
        "WRPS: unknown asset → LOW RiskScore",
        ok,
        f"wrps={score.wrps}, tier={score.risk_tier.value}",
    )

    weights = get_current_weights()
    weights_ok = abs(sum(weights.values()) - 1.0) < 0.01
    check(
        "WRPS: weights sum to 1.0",
        weights_ok,
        f"sum={sum(weights.values()):.4f}, keys={list(weights.keys())}",
    )
except Exception as exc:
    check("WRPS: unknown asset → LOW RiskScore", False, str(exc))

# ---------------------------------------------------------------------------
# Alerting schema check
# ---------------------------------------------------------------------------

print("\n[Phase 4] Alerting + schema checks")

try:
    from wizard.backend.alerting import AlertBroadcaster, DedupRegistry
    b = AlertBroadcaster()
    check("AlertBroadcaster: instantiation", True, f"client_count={b.client_count()}")
except Exception as exc:
    check("AlertBroadcaster: instantiation", False, str(exc))

try:
    from wizard.backend.schemas import ChatRequest, HealthResponse, ErrorEnvelope, ErrorCode
    req = ChatRequest(
        session_id="test",
        equipment_id="EAF-04",
        query="test query",
    )
    check("ChatRequest: valid schema", True, f"session_id={req.session_id}")
except Exception as exc:
    check("ChatRequest: valid schema", False, str(exc))

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print(f"RESULTS: {_passed} passed, {_failed} failed")
print("=" * 60)

# Cleanup temp dir
import shutil
shutil.rmtree(_tmp_dir, ignore_errors=True)

sys.exit(0 if _failed == 0 else 1)
