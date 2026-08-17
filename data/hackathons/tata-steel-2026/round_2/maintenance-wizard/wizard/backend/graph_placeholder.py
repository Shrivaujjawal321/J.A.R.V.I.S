"""
wizard.backend.graph_placeholder
=================================
Typed stub that returns a MaintenanceRecommendation from a hard-coded
template. Replaces the real LangGraph graph until the agentic-core wave
ships.

INTEGRATION CONTRACT FOR AGENTIC-CORE WAVE
-------------------------------------------
Replace this module by wiring ``wizard.agents.graph`` as follows:

    # In app.py or a dedicated agent runner module:
    from wizard.agents.graph import build_graph
    _graph = build_graph()  # call once at lifespan startup

    async def run_graph(request: ChatRequest) -> tuple[MaintenanceRecommendation, list[dict]]:
        config = {"configurable": {"thread_id": request.session_id}}
        state_input = {
            "equipment_id": request.equipment_id,
            "user_query": request.query,
        }
        final_state: MaintenanceState = {}
        async for chunk in _graph.astream(state_input, config=config):
            final_state.update(chunk)
        return (
            final_state.get("maintenance_plan") or _fallback_recommendation(request.equipment_id),
            final_state.get("agent_trace", []),
        )

    async def stream_graph(request: ChatRequest) -> AsyncGenerator[dict, None]:
        config = {"configurable": {"thread_id": request.session_id}}
        state_input = {
            "equipment_id": request.equipment_id,
            "user_query": request.query,
        }
        async for chunk in _graph.astream(state_input, config=config):
            yield chunk

The functions below have IDENTICAL signatures to the real graph runners.
Swap them out with zero changes to app.py.
"""
from __future__ import annotations

import asyncio
from datetime import datetime
from typing import AsyncGenerator, Optional

import structlog

from wizard.core.schemas import (
    ActionStep,
    AlertSeverity,
    MaintenanceRecommendation,
    MaintenanceState,
    _new_ulid,
)
from wizard.backend.schemas import ChatRequest

log = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Stub recommendation factory
# ---------------------------------------------------------------------------

def _build_placeholder_recommendation(
    equipment_id: str,
    query: str,
) -> MaintenanceRecommendation:
    """
    Return a structurally complete MaintenanceRecommendation stub.
    Content is clearly labelled as placeholder so it cannot be confused with
    real agent output.
    """
    now = datetime.utcnow()
    diag_id = _new_ulid()

    steps: list[ActionStep] = [
        ActionStep(
            step_number=1,
            action=(
                f"[PLACEHOLDER] Inspect {equipment_id} for visible wear, leaks, "
                "or unusual vibration patterns. Record all observations."
            ),
            responsible_role="maintenance_technician",
            estimated_duration_hours=0.5,
            parts_required=[],
            safety_precautions=[
                "Lockout/Tagout (LOTO) before physical inspection",
                "Wear PPE: safety glasses, gloves, steel-toe boots",
            ],
            cited_sop_section="SOP-GEN-001 §2.1 — Inspection Procedure",
        ),
        ActionStep(
            step_number=2,
            action=(
                "[PLACEHOLDER] Review sensor trend data for temperature, vibration, "
                "and pressure anomalies over the last 72 hours."
            ),
            responsible_role="maintenance_engineer",
            estimated_duration_hours=0.5,
            parts_required=[],
            safety_precautions=[],
            cited_sop_section="SOP-GEN-002 §3.4 — Data Review Protocol",
        ),
        ActionStep(
            step_number=3,
            action=(
                "[PLACEHOLDER] Schedule component replacement based on RUL estimate. "
                "Confirm spare parts availability with stores before planning downtime."
            ),
            responsible_role="maintenance_planner",
            estimated_duration_hours=1.0,
            parts_required=["SPARE-PLACEHOLDER-001"],
            safety_precautions=["Coordinate with production scheduling"],
            cited_sop_section=None,
        ),
    ]

    return MaintenanceRecommendation(
        recommendation_id=_new_ulid(),
        asset_id=equipment_id,
        diagnosis_report_id=diag_id,
        rca_result_id=None,
        rul_result_id=None,
        risk_score_id=None,
        priority=AlertSeverity.MEDIUM,
        maintenance_type="predictive",
        action_steps=steps,
        estimated_total_hours=2.0,
        parts_bill_of_materials=["SPARE-PLACEHOLDER-001"],
        narrative_summary=(
            f"[PLACEHOLDER RESPONSE — agentic-core not yet wired] "
            f"For equipment {equipment_id}, a predictive maintenance inspection "
            f"is recommended based on current sensor trends. "
            f"Query received: '{query[:100]}'. "
            f"This stub will be replaced by the real LangGraph agent output once "
            f"wizard.agents.graph is integrated in the next build wave. "
            f"Source citations: [1] SOP-GEN-001 §2.1, [2] SOP-GEN-002 §3.4."
        ),
        cited_sources=["SOP-GEN-001-§2.1", "SOP-GEN-002-§3.4"],
        spares_procurement_warning=None,
        cost_avoidance_inr=None,
        created_at=now,
    )


# ---------------------------------------------------------------------------
# Public API — called by app.py (identical signatures to real graph runners)
# ---------------------------------------------------------------------------

async def run_graph(
    request: ChatRequest,
) -> tuple[MaintenanceRecommendation, list[dict]]:
    """
    Synchronous-style graph runner (returns full recommendation at once).

    AGENTIC-CORE REPLACEMENT: swap this body with real graph.astream() invocation.
    Signature must remain: (ChatRequest) -> tuple[MaintenanceRecommendation, list[dict]]
    """
    log.info(
        "graph_placeholder.run_graph called",
        equipment_id=request.equipment_id,
        session_id=request.session_id,
        query_len=len(request.query),
    )
    # Simulate minimal processing time (≈ what a fast cached LLM would take)
    await asyncio.sleep(0.05)

    recommendation = _build_placeholder_recommendation(
        request.equipment_id, request.query
    )

    agent_trace: list[dict] = [
        {
            "agent": "supervisor",
            "node": "START",
            "latency_ms": 12.0,
            "timestamp": datetime.utcnow().isoformat(),
            "note": "placeholder — real LangGraph trace will appear here",
        },
        {
            "agent": "diagnosis",
            "node": "diagnosis_node",
            "latency_ms": 25.0,
            "timestamp": datetime.utcnow().isoformat(),
            "note": "placeholder",
        },
    ]

    return recommendation, agent_trace


async def stream_graph(
    request: ChatRequest,
) -> AsyncGenerator[dict, None]:
    """
    Streaming graph runner — yields SSE-ready dicts matching AgentStepEvent fields.

    AGENTIC-CORE REPLACEMENT: replace loop body with:
        async for chunk in _graph.astream(state_input, config=config):
            yield chunk
    Signature must remain: (ChatRequest) -> AsyncGenerator[dict, None]
    """
    log.info(
        "graph_placeholder.stream_graph called",
        equipment_id=request.equipment_id,
        session_id=request.session_id,
    )

    now = datetime.utcnow().isoformat()

    # Step 1: supervisor routes the query
    yield {
        "event_type": "agent_step",
        "session_id": request.session_id,
        "equipment_id": request.equipment_id,
        "payload": {
            "agent": "supervisor",
            "message": f"Routing query for {request.equipment_id} to diagnosis agent",
        },
        "timestamp_utc": now,
        "source_node": "supervisor",
    }
    await asyncio.sleep(0.08)

    # Step 2: diagnosis agent (placeholder tokens)
    tokens = [
        "[PLACEHOLDER] Analysing sensor data",
        " for equipment",
        f" {request.equipment_id}",
        "...",
    ]
    for token in tokens:
        yield {
            "event_type": "token",
            "session_id": request.session_id,
            "equipment_id": request.equipment_id,
            "payload": {"delta": token},
            "timestamp_utc": datetime.utcnow().isoformat(),
            "source_node": "diagnosis_node",
        }
        await asyncio.sleep(0.03)

    # Step 3: risk update
    yield {
        "event_type": "risk_update",
        "session_id": request.session_id,
        "equipment_id": request.equipment_id,
        "payload": {
            "risk_tier": "medium",
            "wrps": 42.5,
            "note": "placeholder risk score — real WRPS will appear here",
        },
        "timestamp_utc": datetime.utcnow().isoformat(),
        "source_node": "risk_node",
    }
    await asyncio.sleep(0.05)

    # Step 4: recommendation ready
    recommendation = _build_placeholder_recommendation(
        request.equipment_id, request.query
    )
    yield {
        "event_type": "recommendation_ready",
        "session_id": request.session_id,
        "equipment_id": request.equipment_id,
        "payload": recommendation.model_dump(mode="json"),
        "timestamp_utc": datetime.utcnow().isoformat(),
        "source_node": "plan_node",
    }
    await asyncio.sleep(0.02)

    # Step 5: done
    yield {
        "event_type": "done",
        "session_id": request.session_id,
        "equipment_id": request.equipment_id,
        "payload": {},
        "timestamp_utc": datetime.utcnow().isoformat(),
        "source_node": None,
    }
