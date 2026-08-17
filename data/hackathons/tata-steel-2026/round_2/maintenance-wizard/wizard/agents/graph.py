"""
wizard.agents.graph
===================
LangGraph StateGraph for the Maintenance Wizard agentic core.

Topology:
  START → supervisor → [diagnosis | rca | rul | prioritization | plan | report] → END

  The supervisor_route function is a deterministic Python router (Literal return,
  no LLM involved) that forwards to the next un-executed pipeline stage.
  Each domain node runs, updates its slice of MaintenanceState, and returns
  to supervisor which routes forward again.  After report_node completes,
  supervisor routes to END.

  recursion_limit = 25 (set in compile config, enforced by LangGraph in Python).

Checkpointing:
  AsyncSqliteSaver persists per thread_id=session_id to data/sessions/agents.db.
  Multi-turn: subsequent calls with the same thread_id resume from last checkpoint.

Public API (EXACT signatures expected by wizard.backend.app):
  run_graph(request: ChatRequest) -> tuple[MaintenanceRecommendation, list[dict]]
  stream_graph(request: ChatRequest) -> AsyncGenerator[dict, None]

Also exposes:
  get_compiled_graph() -> CompiledGraph   (for session state endpoint)
  get_graph_state(session_id: str) -> dict | None
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncGenerator, Literal, Optional

from wizard.core.schemas import MaintenanceRecommendation, MaintenanceState, _new_ulid
from wizard.backend.schemas import ChatRequest

from wizard.agents.nodes import (
    supervisor_route,
    diagnosis_node,
    rca_node,
    rul_node,
    prioritization_node,
    plan_node,
    report_node,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

_RECURSION_LIMIT = 25  # enforced by LangGraph in code

def _build_graph():
    """
    Build and compile the MaintenanceWizard StateGraph.

    Called once at module load (singleton pattern). Returns a compiled graph
    backed by an AsyncSqliteSaver checkpointer.

    Returns (compiled_graph, checkpointer_conn_string).
    """
    from langgraph.graph import StateGraph, END, START

    # Resolve sessions DB path
    from wizard.core.config import settings
    sessions_db = Path(settings.sessions_db_path)
    if not sessions_db.is_absolute():
        sessions_db = Path.cwd() / sessions_db
    # Fallback to a known good path if cwd-relative doesn't resolve nicely
    if not sessions_db.parent.exists():
        sessions_db = Path(__file__).resolve().parents[2] / "data" / "sessions" / "agents.db"

    sessions_db.parent.mkdir(parents=True, exist_ok=True)
    conn_string = str(sessions_db)

    # Build graph
    builder = StateGraph(MaintenanceState)

    # Add domain nodes
    builder.add_node("diagnosis", diagnosis_node)
    builder.add_node("rca", rca_node)
    builder.add_node("rul", rul_node)
    builder.add_node("prioritization", prioritization_node)
    builder.add_node("plan", plan_node)
    builder.add_node("report", report_node)

    # Add supervisor routing node (pure Python — no LLM)
    # The supervisor is implemented as a conditional edge from START
    # and from each domain node back to a routing decision.
    # We use a dedicated "supervisor" node that just returns routing info.

    def supervisor_node(state: MaintenanceState) -> dict:
        """No-op node — routing happens in the conditional edge function."""
        return {}

    builder.add_node("supervisor", supervisor_node)

    # Entry: START → supervisor
    builder.set_entry_point("supervisor")

    # Supervisor → conditional edge to next stage
    builder.add_conditional_edges(
        "supervisor",
        supervisor_route,
        {
            "diagnosis": "diagnosis",
            "rca": "rca",
            "rul": "rul",
            "prioritization": "prioritization",
            "plan": "plan",
            "report": "report",
            "__end__": END,
        },
    )

    # After each domain node → back to supervisor
    for node_name in ["diagnosis", "rca", "rul", "prioritization", "plan"]:
        builder.add_edge(node_name, "supervisor")

    # After report → END (report is the terminal node)
    builder.add_edge("report", END)

    return builder, conn_string


# Build the graph structure once at module load
_graph_builder, _SESSIONS_DB = _build_graph()

# ---------------------------------------------------------------------------
# Async context manager for checkpointer lifecycle
# ---------------------------------------------------------------------------

# Module-level compiled graph cache (keyed by conn_string)
_compiled_graph: Optional[Any] = None
_saver_ctx: Optional[Any] = None
_saver_instance: Optional[Any] = None


async def _ensure_compiled_graph():
    """
    Lazily compile the graph with an AsyncSqliteSaver checkpointer.
    Returns the compiled graph (singleton — created once per process).

    The saver's serde is replaced with a WIZARD_SERDE instance that has all
    wizard.core.schemas types allow-listed, eliminating the
    'Deserializing unregistered type' warnings.  The LANGGRAPH_CHECKPOINT_ALLOWED_MODULES
    env-var is a no-op at runtime — setting saver.serde directly is the only
    effective approach.
    """
    global _compiled_graph, _saver_ctx, _saver_instance

    if _compiled_graph is not None:
        return _compiled_graph

    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
    from wizard.agents import WIZARD_SERDE

    # Use context manager to get the saver (keep it alive for process lifetime)
    _saver_ctx = AsyncSqliteSaver.from_conn_string(_SESSIONS_DB)
    _saver_instance = await _saver_ctx.__aenter__()

    # Inject configured serde to silence 'Deserializing unregistered type' warnings.
    # AsyncSqliteSaver.__init__ accepts serde= but from_conn_string does not expose it,
    # so we set the attribute directly (confirmed working via introspection).
    if WIZARD_SERDE is not None:
        _saver_instance.serde = WIZARD_SERDE

    _compiled_graph = _graph_builder.compile(
        checkpointer=_saver_instance,
    )
    logger.info(
        "wizard.agents.graph compiled (db=%s, recursion_limit=%d)",
        _SESSIONS_DB, _RECURSION_LIMIT,
    )
    return _compiled_graph


def get_compiled_graph() -> Optional[Any]:
    """Return the compiled graph if already initialised, else None."""
    return _compiled_graph


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def run_graph(
    request: ChatRequest,
) -> tuple[MaintenanceRecommendation, list[dict]]:
    """
    Synchronous-style graph runner (returns full recommendation at once).

    Builds/resumes the session graph from checkpoint, runs all nodes,
    and returns the final MaintenanceRecommendation + agent_trace.

    On any failure: returns a deterministic structured fallback so the demo
    never crashes.

    Signature: (ChatRequest) -> tuple[MaintenanceRecommendation, list[dict]]
    (EXACT match to what wizard.backend.app expects)
    """
    start = time.monotonic()
    session_id = request.session_id
    equipment_id = request.equipment_id
    query = request.query

    logger.info(
        "run_graph.start session=%s equipment=%s",
        session_id, equipment_id,
    )

    try:
        graph = await _ensure_compiled_graph()

        config = {
            "configurable": {"thread_id": session_id},
            "recursion_limit": _RECURSION_LIMIT,
        }

        # FIX #5 — Load prior conversation_history BEFORE resetting per-turn slots.
        # LangGraph's SqliteSaver checkpoints state per thread_id. On turn 2+, the
        # prior state is already in the checkpointer. We read it here so we can carry
        # conversation_history forward explicitly in state_input (the TypedDict merge
        # would otherwise overwrite it with the incoming value, which is the new empty list).
        prior_snapshot = await graph.aget_state(config)
        prior_values = prior_snapshot.values if prior_snapshot and prior_snapshot.values else {}
        prior_conversation_history: list[dict] = list(
            prior_values.get("conversation_history") or []
        )
        logger.debug(
            "run_graph.prior_history session=%s turns=%d",
            session_id, len(prior_conversation_history),
        )

        # Null out per-turn slots so the pipeline re-evaluates every call.
        # Without this, a second call with the same session_id sees a fully-populated
        # state and supervisor routes straight to END (producing a 1-step trace).
        # conversation_history is carried forward explicitly from prior state (FIX #5).
        state_input: MaintenanceState = {
            "thread_id": session_id,
            "equipment_id": equipment_id,
            "user_query": query,
            "sensor_snapshot": _extract_sensor_snapshot(request),
            "fault_codes": _extract_fault_codes(request),
            # Per-turn pipeline slots — reset so every query runs the full pipeline
            "diagnosis": None,
            "rca": None,
            "rul_estimate": None,
            "risk_level": None,
            "maintenance_plan": None,
            # FIX #5: Carry prior conversation history forward; report_node will append this turn
            "conversation_history": prior_conversation_history,
            # FIX #8: Reset per-turn RAG chunk accumulator and faithfulness scores
            "retrieved_chunks_raw": [],
            "faithfulness_scores": {},
            # Other accumulators — keep growing across turns
            "feedback_corrections": [],
            "alert_events": [],
            "agent_trace": [],
        }

        async for _ in graph.astream(state_input, config=config):
            pass  # drain the generator; state is persisted in the checkpointer

        # Read the flat state from the checkpointer snapshot.
        # astream() returns per-node update dicts keyed by node name, NOT flat state —
        # so final_state.get('maintenance_plan') is always None.  aget_state() returns
        # the fully-merged flat state, which is the correct extraction path.
        snapshot = await graph.aget_state(config)
        recommendation = _extract_recommendation_from_snapshot(snapshot, equipment_id)
        agent_trace = _extract_trace_from_snapshot(snapshot)

        latency = (time.monotonic() - start) * 1000
        logger.info(
            "run_graph.complete session=%s latency_ms=%.1f steps=%d",
            session_id, latency, len(agent_trace),
        )

        return recommendation, agent_trace

    except Exception as exc:
        logger.error("run_graph.failed session=%s error=%s", session_id, exc, exc_info=True)
        fallback = _build_fallback_recommendation(equipment_id, query, str(exc))
        fallback_trace = [
            {
                "agent": "graph",
                "node": "error_recovery",
                "latency_ms": (time.monotonic() - start) * 1000,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(exc)[:200],
            }
        ]
        return fallback, fallback_trace


async def stream_graph(
    request: ChatRequest,
) -> AsyncGenerator[dict, None]:
    """
    Streaming graph runner — yields SSE-ready dicts matching AgentStepEvent fields.

    Each LangGraph astream chunk is converted to an event dict with:
      event_type: 'agent_step' | 'risk_update' | 'recommendation_ready' | 'done' | 'error'
      session_id, equipment_id, payload, timestamp_utc, source_node

    Signature: (ChatRequest) -> AsyncGenerator[dict, None]
    (EXACT match to what wizard.backend.app expects)
    """
    session_id = request.session_id
    equipment_id = request.equipment_id
    query = request.query

    logger.info("stream_graph.start session=%s equipment=%s", session_id, equipment_id)

    try:
        graph = await _ensure_compiled_graph()

        config = {
            "configurable": {"thread_id": session_id},
            "recursion_limit": _RECURSION_LIMIT,
        }

        # FIX #5 — Load prior conversation_history BEFORE resetting per-turn slots
        # (same rationale as run_graph — see detailed comment there).
        prior_snapshot = await graph.aget_state(config)
        prior_values = prior_snapshot.values if prior_snapshot and prior_snapshot.values else {}
        prior_conversation_history: list[dict] = list(
            prior_values.get("conversation_history") or []
        )
        logger.debug(
            "stream_graph.prior_history session=%s turns=%d",
            session_id, len(prior_conversation_history),
        )

        # Null out per-turn slots (same rationale as run_graph — see comment there)
        state_input: MaintenanceState = {
            "thread_id": session_id,
            "equipment_id": equipment_id,
            "user_query": query,
            "sensor_snapshot": _extract_sensor_snapshot(request),
            "fault_codes": _extract_fault_codes(request),
            # Per-turn pipeline slots — reset so every query runs the full pipeline
            "diagnosis": None,
            "rca": None,
            "rul_estimate": None,
            "risk_level": None,
            "maintenance_plan": None,
            # FIX #5: Carry prior conversation history forward
            "conversation_history": prior_conversation_history,
            # FIX #8: Reset per-turn RAG chunk accumulator and faithfulness scores
            "retrieved_chunks_raw": [],
            "faithfulness_scores": {},
            # Other accumulators — keep growing across turns
            "feedback_corrections": [],
            "alert_events": [],
            "agent_trace": [],
        }

        now_str = lambda: datetime.now(timezone.utc).isoformat()

        final_state: dict = {}
        async for chunk in graph.astream(state_input, config=config):
            if not chunk:
                continue

            final_state.update(chunk)

            # chunk is {node_name: updated_state_slice}
            for node_name, node_state in chunk.items():
                if not isinstance(node_state, dict):
                    continue

                # Emit agent_step event for every node update
                event: dict = {
                    "event_type": "agent_step",
                    "session_id": session_id,
                    "equipment_id": equipment_id,
                    "payload": {
                        "agent": node_name,
                        "message": f"{node_name} node completed",
                        "state_keys": list(node_state.keys()),
                    },
                    "timestamp_utc": now_str(),
                    "source_node": node_name,
                }

                # Enrich specific nodes
                if node_name == "prioritization" and "risk_level" in node_state:
                    risk_level = node_state.get("risk_level")
                    if risk_level:
                        wrps = getattr(risk_level, "wrps", None)
                        tier = getattr(risk_level, "risk_tier", None)
                        event = {
                            "event_type": "risk_update",
                            "session_id": session_id,
                            "equipment_id": equipment_id,
                            "payload": {
                                "risk_tier": tier.value if tier else "medium",
                                "wrps": wrps,
                                "spares_risk": getattr(risk_level, "spares_risk", "ok"),
                            },
                            "timestamp_utc": now_str(),
                            "source_node": node_name,
                        }

                elif node_name in ("plan", "report") and "maintenance_plan" in node_state:
                    plan = node_state.get("maintenance_plan")
                    if plan:
                        try:
                            plan_dict = plan.model_dump(mode="json") if hasattr(plan, "model_dump") else {}
                        except Exception:
                            plan_dict = {}
                        event = {
                            "event_type": "recommendation_ready",
                            "session_id": session_id,
                            "equipment_id": equipment_id,
                            "payload": plan_dict,
                            "timestamp_utc": now_str(),
                            "source_node": node_name,
                        }

                yield event

        # Read flat state from checkpoint for accurate trace count
        snapshot = await graph.aget_state(config)
        trace_count = len(_extract_trace_from_snapshot(snapshot))

        # Final done event
        yield {
            "event_type": "done",
            "session_id": session_id,
            "equipment_id": equipment_id,
            "payload": {
                "steps_completed": trace_count,
            },
            "timestamp_utc": now_str(),
            "source_node": None,
        }

    except Exception as exc:
        logger.error("stream_graph.failed session=%s error=%s", session_id, exc)
        yield {
            "event_type": "error",
            "session_id": session_id,
            "equipment_id": equipment_id,
            "payload": {
                "error": {"code": "GRAPH_ERROR", "message": str(exc)[:200]}
            },
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "source_node": None,
        }


async def get_graph_state(session_id: str) -> Optional[dict]:
    """
    Retrieve the full MaintenanceState for a session from the SqliteSaver checkpoint.

    Returns None if no checkpoint exists for the session.
    Used by GET /v1/session/{id}/state endpoint.
    """
    try:
        graph = await _ensure_compiled_graph()
        config = {"configurable": {"thread_id": session_id}}
        snapshot = await graph.aget_state(config)
        if snapshot and snapshot.values:
            return dict(snapshot.values)
        return None
    except Exception as exc:
        logger.warning("get_graph_state failed for %s: %s", session_id, exc)
        return None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_sensor_snapshot(request: ChatRequest) -> dict:
    """
    Look up the LATEST SensorSummary row for the requested asset and return its
    sensor_readings dict.  Falls back to {} gracefully if no row exists.

    Resolution order:
      1. request.equipment_id
      2. request.asset_id  (fallback alias)

    The inject_fault endpoint writes a CRITICAL SensorSummary for EAF-04 — so
    after /v1/demo/inject_fault is called, EAF-04 will return real critical values
    here rather than a hardcode, preserving the wow-moment with honest data.
    """
    asset_id: str = (
        request.equipment_id
        or getattr(request, "asset_id", None)
        or ""
    )
    if not asset_id:
        return {}

    try:
        from sqlmodel import select
        from wizard.core.db import session_scope
        from wizard.core.schemas import SensorSummary

        with session_scope() as session:
            row = session.exec(
                select(SensorSummary)
                .where(SensorSummary.asset_id == asset_id)
                .order_by(SensorSummary.window_end.desc())  # type: ignore[union-attr]
                .limit(1)
            ).first()

        if row is None:
            logger.debug("_extract_sensor_snapshot: no SensorSummary for asset_id=%s", asset_id)
            return {}

        readings = row.sensor_readings
        if not isinstance(readings, dict):
            return {}

        logger.debug(
            "_extract_sensor_snapshot: asset_id=%s condition=%s readings_keys=%s",
            asset_id,
            row.operating_condition,
            list(readings.keys()),
        )
        return readings

    except Exception as exc:
        logger.warning(
            "_extract_sensor_snapshot: DB lookup failed for asset_id=%s: %s",
            asset_id, exc,
        )
        return {}


def _extract_fault_codes(request: ChatRequest) -> list[str]:
    """
    Attempt to extract fault codes from the query text.
    Simple heuristic: look for codes matching BRG-*, HDF-*, TWF-*, etc.
    """
    import re
    codes = re.findall(r'\b[A-Z]{2,6}-[A-Z0-9]{3,10}\b', request.query)
    return codes[:5]  # cap at 5


def _extract_recommendation_from_snapshot(snapshot: Any, equipment_id: str) -> MaintenanceRecommendation:
    """
    Pull MaintenanceRecommendation from an aget_state() snapshot.

    After astream(), call `snapshot = await graph.aget_state(config)`.
    snapshot.values is a flat dict of the merged state — keys are state field names,
    not node names.  This is the correct (and only working) extraction path.

    The old approach of reading final_state accumulated from astream() chunks is
    dead code: astream() yields {node_name: node_update_dict} per step, so
    final_state.get('maintenance_plan') is always None (it would need
    final_state.get('plan', {}).get('maintenance_plan')).
    """
    values = snapshot.values if snapshot and snapshot.values else {}
    plan = values.get("maintenance_plan")

    if isinstance(plan, MaintenanceRecommendation):
        return plan

    return _build_fallback_recommendation(equipment_id, "", "state extraction failed")


def _extract_trace_from_snapshot(snapshot: Any) -> list[dict]:
    """Pull agent_trace from an aget_state() snapshot (flat state values)."""
    values = snapshot.values if snapshot and snapshot.values else {}
    trace = values.get("agent_trace")
    if isinstance(trace, list):
        return trace
    return []


def _build_fallback_recommendation(
    equipment_id: str,
    query: str,
    error_hint: str = "",
) -> MaintenanceRecommendation:
    """
    Deterministic fallback MaintenanceRecommendation returned when the graph fails.
    Structurally complete — never crashes. Clearly labelled as fallback.
    """
    from wizard.core.schemas import ActionStep

    steps = [
        ActionStep(
            step_number=1,
            action=f"Apply LOTO on {equipment_id}. Verify zero-energy state before inspection.",
            responsible_role="safety_officer",
            estimated_duration_hours=0.25,
            safety_precautions=["LOTO certification required", "Confirm zero-energy state"],
            cited_sop_section="SOP-SAFETY-001 §2.1",
        ),
        ActionStep(
            step_number=2,
            action=f"Conduct visual and instrument-based inspection of {equipment_id}. Document all anomalies.",
            responsible_role="maintenance_technician",
            estimated_duration_hours=1.0,
            safety_precautions=["PPE required", "Use calibrated instruments"],
            cited_sop_section="SOP-GEN-002 §3.1",
        ),
        ActionStep(
            step_number=3,
            action="Review sensor trend data (temperature, vibration, pressure) for the past 72 hours.",
            responsible_role="maintenance_engineer",
            estimated_duration_hours=0.5,
            cited_sop_section="SOP-GEN-002 §3.4",
        ),
        ActionStep(
            step_number=4,
            action="Confirm spare parts availability. Schedule maintenance window with production team.",
            responsible_role="maintenance_planner",
            estimated_duration_hours=0.25,
            cited_sop_section=None,
        ),
    ]

    return MaintenanceRecommendation(
        recommendation_id=_new_ulid(),
        asset_id=equipment_id,
        diagnosis_report_id=_new_ulid(),
        priority=AlertSeverity_MEDIUM(),
        maintenance_type="predictive",
        action_steps=steps,
        estimated_total_hours=2.0,
        parts_bill_of_materials=[],
        narrative_summary=(
            f"Maintenance Wizard — Fallback Recommendation for {equipment_id}. "
            f"Query: '{query[:80]}'. "
            "Full agentic analysis was not available (possible: no LLM key, cold start, or no ML models). "
            "This deterministic plan follows standard inspection protocols. "
            "Sources: [1] SOP-SAFETY-001 §2.1, [2] SOP-GEN-002 §3.1."
        ),
        cited_sources=["SOP-SAFETY-001-§2.1", "SOP-GEN-002-§3.1"],
        spares_procurement_warning=None,
        cost_avoidance_inr=None,
    )


def AlertSeverity_MEDIUM():
    """Lazy import to avoid circular import."""
    from wizard.core.schemas import AlertSeverity
    return AlertSeverity.MEDIUM
