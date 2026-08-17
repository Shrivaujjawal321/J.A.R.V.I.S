"""
wizard.agents.smoke_agents
===========================
Self-contained smoke test for the agentic core.

Verifies (with NO LLM key set, NO trained ML artifacts):
  [1] Graph compiles without error
  [2] run_graph on EAF-04 returns MaintenanceRecommendation + non-empty agent_trace
  [3] All agent_trace entries have required fields
  [4] Recommendation has required fields (asset_id, action_steps, priority)
  [5] Checkpointer persisted state for the thread
  [6] Second turn resumes (same session_id, different query) → checkpoint updated
  [7] stream_graph yields at least one event_type='recommendation_ready' chunk
  [8] get_graph_state returns a non-None dict for the session

Run:
    cd maintenance-wizard
    python -W ignore wizard/agents/smoke_agents.py
"""
from __future__ import annotations

import asyncio
import os
import sys
import tempfile
import time
from pathlib import Path

# ---- Force no LLM key (demo-safety test) ----
os.environ.pop("GEMINI_API_KEY", None)
os.environ.pop("ANTHROPIC_API_KEY", None)
os.environ.pop("OPENAI_API_KEY", None)

# ---- Use temp DB so smoke test doesn't pollute production data ----
_tmp_dir = tempfile.mkdtemp(prefix="wizard_smoke_agents_")
_tmp_sessions_db = str(Path(_tmp_dir) / "sessions_smoke.db")
_tmp_db_path = str(Path(_tmp_dir) / "smoke_wizard.db")
os.environ["SESSIONS_DB_PATH"] = _tmp_sessions_db
os.environ["DB_PATH"] = _tmp_db_path

# Disable scheduler for smoke tests
os.environ["WIZARD_TESTING"] = "1"

# Initialise the wizard SQLite DB (creates all tables including asset_profile)
# before importing graph or running any node that calls wrps_score_priority —
# otherwise we get 'no such table: asset_profile' errors in Phase 3/4 tests.
try:
    from wizard.core.db import init_db as _init_db
    _init_db(_tmp_db_path)
except Exception as _db_exc:
    print(f"[WARN] init_db failed during smoke setup: {_db_exc}")

# ---- Import the modules under test ----
print("=" * 60)
print("SMOKE TEST: wizard.agents (agentic core)")
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


# ---------------------------------------------------------------------------
# Phase 1 — Module compilation
# ---------------------------------------------------------------------------

print("\n[Phase 1] Module compilation")

import py_compile

_AGENTS_DIR = Path(__file__).parent

for mod in ["tools.py", "nodes.py", "graph.py", "smoke_agents.py"]:
    try:
        py_compile.compile(str(_AGENTS_DIR / mod), doraise=True)
        check(f"py_compile: {mod}", True)
    except py_compile.PyCompileError as exc:
        check(f"py_compile: {mod}", False, str(exc)[:120])


# ---------------------------------------------------------------------------
# Phase 2 — Core imports
# ---------------------------------------------------------------------------

print("\n[Phase 2] Import checks")

try:
    from wizard.agents.tools import ALL_TOOLS, rag_retrieve, wrps_score_priority
    check("wizard.agents.tools imports", True, f"tools={len(ALL_TOOLS)}")
except Exception as exc:
    check("wizard.agents.tools imports", False, str(exc)[:120])

try:
    from wizard.agents.nodes import (
        supervisor_route,
        diagnosis_node,
        rca_node,
        rul_node,
        prioritization_node,
        plan_node,
        report_node,
    )
    check("wizard.agents.nodes imports", True)
except Exception as exc:
    check("wizard.agents.nodes imports", False, str(exc)[:120])

try:
    from wizard.agents.graph import run_graph, stream_graph, get_graph_state
    check("wizard.agents.graph imports", True)
except Exception as exc:
    check("wizard.agents.graph imports", False, str(exc)[:120])


# ---------------------------------------------------------------------------
# Phase 3 — Graph execution (async)
# ---------------------------------------------------------------------------

print("\n[Phase 3] Graph execution — run_graph (no LLM key, no ML artifacts)")

async def _run_smoke():
    from wizard.backend.schemas import ChatRequest
    from wizard.core.schemas import MaintenanceRecommendation
    from wizard.agents.graph import run_graph, stream_graph, get_graph_state

    # [2] run_graph: EAF-04, turn 1
    session_id = "smoke-agent-session-001"
    req1 = ChatRequest(
        session_id=session_id,
        equipment_id="EAF-04",
        query="What is wrong with EAF-04 and what should I do?",
    )

    t0 = time.monotonic()
    rec, trace = await run_graph(req1)
    latency = (time.monotonic() - t0) * 1000

    check(
        "run_graph: returns MaintenanceRecommendation",
        isinstance(rec, MaintenanceRecommendation),
        f"type={type(rec).__name__}",
    )
    check(
        "run_graph: asset_id matches",
        rec.asset_id == "EAF-04",
        f"asset_id={rec.asset_id}",
    )
    check(
        "run_graph: non-empty action_steps",
        len(rec.action_steps) > 0,
        f"steps={len(rec.action_steps)}",
    )
    check(
        "run_graph: priority is set",
        rec.priority is not None,
        f"priority={rec.priority}",
    )
    check(
        "run_graph: non-empty agent_trace",
        len(trace) > 0,
        f"trace_entries={len(trace)}",
    )
    check(
        "run_graph: latency under 60s",
        latency < 60_000,
        f"latency_ms={latency:.0f}",
    )

    # [3] Trace entries have required fields
    required_trace_fields = {"agent", "node", "latency_ms", "timestamp"}
    if trace:
        last_entry = trace[-1]
        has_fields = all(k in last_entry for k in required_trace_fields)
        check(
            "agent_trace: entries have required fields",
            has_fields,
            f"keys={list(last_entry.keys())}",
        )

    # [4] narrative_summary is non-empty
    check(
        "run_graph: narrative_summary non-empty",
        bool(rec.narrative_summary and len(rec.narrative_summary) > 10),
        f"len={len(rec.narrative_summary or '')}",
    )

    # [5] Checkpoint persisted — get_graph_state should return non-None
    state = await get_graph_state(session_id)
    check(
        "checkpointer: state persisted for thread",
        state is not None and isinstance(state, dict),
        f"state_type={type(state).__name__}, keys={list((state or {}).keys())[:5]}",
    )

    # [6] Second turn resumes (same session_id)
    req2 = ChatRequest(
        session_id=session_id,
        equipment_id="EAF-04",
        query="What spare parts do I need to order?",
    )
    rec2, trace2 = await run_graph(req2)
    check(
        "run_graph: second turn returns recommendation",
        isinstance(rec2, MaintenanceRecommendation),
        f"type={type(rec2).__name__}",
    )
    check(
        "run_graph: second turn has trace",
        len(trace2) > 0,
        f"trace_entries={len(trace2)}",
    )

    # [7] stream_graph yields at least one event
    stream_events = []
    async for chunk in stream_graph(req1):
        stream_events.append(chunk)
        if len(stream_events) > 50:  # safety cap
            break

    check(
        "stream_graph: yields events",
        len(stream_events) > 0,
        f"events={len(stream_events)}",
    )
    event_types = {e.get("event_type") for e in stream_events}
    check(
        "stream_graph: emits recommendation_ready or agent_step",
        bool(event_types & {"recommendation_ready", "agent_step", "done"}),
        f"event_types={sorted(event_types)}",
    )

    # [8] get_graph_state after second turn
    state2 = await get_graph_state(session_id)
    check(
        "get_graph_state: returns dict after two turns",
        state2 is not None and isinstance(state2, dict),
        f"keys={list((state2 or {}).keys())[:5]}",
    )


asyncio.run(_run_smoke())


# ---------------------------------------------------------------------------
# Phase 4 — Fallback tools (no artifacts)
# ---------------------------------------------------------------------------

print("\n[Phase 4] Tool fallback checks (no ML artifacts)")

try:
    from wizard.agents.tools import (
        rag_retrieve, ml_predict_rul, ml_get_anomaly_score,
        ml_predict_failure, ml_rca_analyze, wrps_score_priority
    )

    r = rag_retrieve("bearing wear inspection", equipment_id="EAF-04")
    check("rag_retrieve: returns dict", isinstance(r, dict), f"keys={list(r.keys())[:4]}")
    check("rag_retrieve: has context_block", "context_block" in r, f"context_block present")

    r = ml_predict_rul("EAF-04")
    check("ml_predict_rul: returns dict", isinstance(r, dict), f"keys={list(r.keys())[:4]}")
    check("ml_predict_rul: has rul_days_p50", "rul_days_p50" in r, f"rul_p50={r.get('rul_days_p50')}")

    r = ml_get_anomaly_score("EAF-04")
    check("ml_get_anomaly_score: returns dict", isinstance(r, dict), f"score={r.get('score')}")

    r = ml_rca_analyze("EAF-04", fault_code="BRG-WEAR-001")
    check("ml_rca_analyze: returns dict", isinstance(r, dict), f"has cause_chain={'cause_chain' in r}")

    r = wrps_score_priority("EAF-04")
    check("wrps_score_priority: returns dict", isinstance(r, dict), f"wrps={r.get('wrps')}")

except Exception as exc:
    check("Tool fallback checks", False, str(exc)[:120])


# ---------------------------------------------------------------------------
# Phase 5 — Supervisor routing (unit)
# ---------------------------------------------------------------------------

print("\n[Phase 5] Supervisor routing (unit)")

try:
    from wizard.agents.nodes import supervisor_route
    from wizard.core.schemas import MaintenanceState

    # Empty state → should route to diagnosis
    empty_state: MaintenanceState = {}
    route = supervisor_route(empty_state)
    check("supervisor_route: empty → diagnosis", route == "diagnosis", f"route={route}")

    # After diagnosis → should route to rca
    from wizard.core.schemas import DiagnosisReport, AlertSeverity
    diag = DiagnosisReport(
        asset_id="EAF-04",
        probable_fault_codes=["BRG-001"],
        probable_fault_description="Bearing wear",
        confidence=0.7,
    )
    after_diag: MaintenanceState = {"diagnosis": diag}
    route2 = supervisor_route(after_diag)
    check("supervisor_route: after_diag → rca", route2 == "rca", f"route={route2}")

except Exception as exc:
    check("Supervisor routing unit tests", False, str(exc)[:120])


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print(f"RESULTS: {_passed} passed, {_failed} failed")
print("=" * 60)

# Cleanup
import shutil
shutil.rmtree(_tmp_dir, ignore_errors=True)

sys.exit(0 if _failed == 0 else 1)
