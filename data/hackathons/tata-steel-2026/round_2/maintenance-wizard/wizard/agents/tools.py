"""
wizard.agents.tools
===================
Thin LangChain-compatible tool wrappers around the wizard RAG, ML, and WRPS
functions.  Every tool returns a typed result dict and appends citation IDs
so the final report node can assemble ``cited_sources``.

Design rules:
  - Each tool has ONE responsibility (anti-pattern #3 from research report 02).
  - Docstrings are the LLM-visible tool descriptions — keep them crisp.
  - Every tool catches exceptions and returns a safe fallback dict (demo-safety).
  - Async tools run sync functions in a thread pool via asyncio.to_thread so the
    agent graph stays non-blocking.

Exported callables (plain Python functions, LangChain @tool-compatible):
  - rag_retrieve(query, equipment_id, top_k) -> dict
  - rag_search_manuals(query, equipment_id, top_k) -> dict
  - rag_search_incidents(query, equipment_id, top_k) -> dict
  - ml_predict_rul(asset_id, sensor_readings_json, sensor_summary_id) -> dict
  - ml_get_anomaly_score(asset_id, sensor_readings_json) -> dict
  - ml_predict_failure(asset_id, sensor_readings_json) -> dict
  - ml_rca_analyze(asset_id, fault_code, fault_description, context_json) -> dict
  - wrps_score_priority(asset_id) -> dict
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# _safe_call — shared exception guard
# ---------------------------------------------------------------------------

def _safe_call(fn, *args, fallback: dict, tool_name: str, **kwargs) -> dict:
    """Call fn(*args, **kwargs). On any exception, log + return fallback."""
    try:
        return fn(*args, **kwargs)
    except Exception as exc:
        logger.warning("tool %s failed: %s — returning fallback", tool_name, exc)
        return {**fallback, "tool_error": str(exc)}


# ---------------------------------------------------------------------------
# resolve_equipment_class — DB lookup with in-process LRU cache
# ---------------------------------------------------------------------------

# Thread-safe simple dict cache: asset_id -> equipment_class string.
# Per-process lifetime is fine — AssetProfile equipment_class never changes
# at runtime.  Cache is invalidated only on process restart.
_eq_class_cache: dict[str, str] = {}

# The 5 trained ISO 14224 classes.  Any AssetProfile.equipment_class that
# doesn't match one of these is mapped to 'default' so the ML registry
# gracefully falls back to the population-level artifact.
_KNOWN_CLASSES = frozenset({"bearing", "fan", "pump", "conveyor", "hydraulic_unit"})


def resolve_equipment_class(asset_id: str) -> str:
    """
    Resolve the ISO 14224 equipment_class for *asset_id* by querying
    the AssetProfile table.

    Returns one of:
      'bearing' | 'fan' | 'pump' | 'conveyor' | 'hydraulic_unit' | 'default'

    Falls back to 'default' when:
      - asset_id is not found in AssetProfile
      - equipment_class value is not one of the 5 trained classes
      - DB is unavailable (demo / unit-test context)

    Result is cached in-process so repeated calls for the same asset_id
    cost only a dict lookup (no DB hit).
    """
    if asset_id in _eq_class_cache:
        return _eq_class_cache[asset_id]

    try:
        from sqlmodel import select
        from wizard.core.db import session_scope
        from wizard.core.schemas import AssetProfile

        with session_scope() as session:
            stmt = select(AssetProfile).where(AssetProfile.asset_id == asset_id)
            profile = session.exec(stmt).first()

        if profile is None:
            logger.debug(
                "resolve_equipment_class: no AssetProfile for asset_id=%r — defaulting",
                asset_id,
            )
            eq_class = "default"
        else:
            raw = (profile.equipment_class or "").lower().strip()
            eq_class = raw if raw in _KNOWN_CLASSES else "default"
            if eq_class == "default" and raw:
                logger.debug(
                    "resolve_equipment_class: asset_id=%r has equipment_class=%r "
                    "which is not a trained class — mapping to 'default'",
                    asset_id, raw,
                )
    except Exception as exc:
        logger.warning(
            "resolve_equipment_class: DB lookup failed for asset_id=%r (%s) — defaulting",
            asset_id, exc,
        )
        eq_class = "default"

    _eq_class_cache[asset_id] = eq_class
    return eq_class


# ---------------------------------------------------------------------------
# RAG tools
# ---------------------------------------------------------------------------

def rag_retrieve(
    query: str,
    equipment_id: Optional[str] = None,
    top_k: int = 5,
) -> dict:
    """
    Retrieve relevant maintenance knowledge (SOPs, manuals, failure reports, incidents).

    Use when you need background knowledge to diagnose a fault, understand a
    procedure, or support a recommendation with cited evidence.

    Args:
        query: Natural-language search query. Be specific — include fault codes,
               equipment names, or procedure references.
        equipment_id: Asset ID to scope the search (e.g. 'EAF-04'). Optional.
        top_k: Max results to return (1-10, default 5).

    Returns:
        dict with keys: context_block (str), cited_sources (list[dict]),
        chunk_count (int), store_empty (bool), tool_error (str, if any).
    """
    from wizard.rag.tools import retrieve_context
    fallback = {
        "context_block": "[Knowledge base not available — using engineering defaults]",
        "cited_sources": [],
        "chunk_count": 0,
        "store_empty": True,
    }
    return _safe_call(
        retrieve_context,
        query=query,
        equipment_id=equipment_id,
        top_k=top_k,
        fallback=fallback,
        tool_name="rag_retrieve",
    )


def rag_search_manuals(
    query: str,
    equipment_id: Optional[str] = None,
    top_k: int = 5,
) -> dict:
    """
    Search equipment manuals and SOPs for maintenance procedures.

    Use when you need specific procedural steps, maintenance intervals, or
    equipment specifications from official documentation.

    Args:
        query: Procedure or specification to look up.
        equipment_id: Optional asset ID to scope the search.
        top_k: Max results (default 5).

    Returns:
        dict with keys: context_block, cited_sources, chunk_count, store_empty.
    """
    from wizard.rag.tools import search_manuals
    fallback = {
        "context_block": "[Manual search unavailable — consult OEM documentation]",
        "cited_sources": [],
        "chunk_count": 0,
        "store_empty": True,
    }
    return _safe_call(
        search_manuals,
        query=query,
        equipment_id=equipment_id,
        top_k=top_k,
        fallback=fallback,
        tool_name="rag_search_manuals",
    )


def rag_search_incidents(
    query: str,
    equipment_id: Optional[str] = None,
    top_k: int = 5,
) -> dict:
    """
    Search historical failure analysis reports and incident summaries.

    Use during RCA to find similar past failures, their root causes, and
    the corrective actions that resolved them.

    Args:
        query: Fault description or failure pattern to search.
        equipment_id: Optional asset ID to narrow the search.
        top_k: Max results (default 5).

    Returns:
        dict with keys: context_block, cited_sources, chunk_count, store_empty.
    """
    from wizard.rag.tools import search_incident_log
    fallback = {
        "context_block": "[Incident log unavailable — no historical data]",
        "cited_sources": [],
        "chunk_count": 0,
        "store_empty": True,
    }
    return _safe_call(
        search_incident_log,
        query=query,
        equipment_id=equipment_id,
        top_k=top_k,
        fallback=fallback,
        tool_name="rag_search_incidents",
    )


# ---------------------------------------------------------------------------
# ML tools
# ---------------------------------------------------------------------------

def ml_predict_rul(
    asset_id: str,
    sensor_readings_json: str = "{}",
    sensor_summary_id: str = "stub",
) -> dict:
    """
    Predict Remaining Useful Life (RUL) for an asset using the WeibullAFT model.

    Returns P10 (pessimistic), P50 (median), P90 (optimistic) RUL estimates
    in days, plus a degradation index [0=healthy, 1=critical].

    Args:
        asset_id: Asset/equipment ID (e.g. 'EAF-04').
        sensor_readings_json: JSON string of latest sensor readings dict.
        sensor_summary_id: SensorSummary entity_id (for FK traceability).

    Returns:
        dict with keys: rul_days_p10, rul_days_p50, rul_days_p90,
        degradation_index, anomaly_score, failure_class, failure_probability,
        model_used, rul_id.
    """
    fallback_rul = {
        "rul_id": "stub",
        "asset_id": asset_id,
        "sensor_summary_id": sensor_summary_id,
        "rul_days_p10": 30.0,
        "rul_days_p50": 45.0,
        "rul_days_p90": 60.0,
        "degradation_index": 0.3,
        "anomaly_score": 0.2,
        "failure_class": "no_failure",
        "failure_probability": 0.15,
        "model_used": "stub",
        "bayesian_correction_applied": False,
    }
    try:
        sensor_readings: dict = json.loads(sensor_readings_json) if sensor_readings_json else {}
    except json.JSONDecodeError:
        sensor_readings = {}

    try:
        from wizard.ml.rul_estimator import predict_rul
        equipment_class = resolve_equipment_class(asset_id)
        result = predict_rul(
            asset_id=asset_id,
            sensor_readings=sensor_readings,
            sensor_summary_id=sensor_summary_id,
            equipment_class=equipment_class,
        )
        return result.model_dump()
    except Exception as exc:
        logger.warning("ml_predict_rul failed for %s: %s", asset_id, exc)
        return {**fallback_rul, "tool_error": str(exc)}


def ml_get_anomaly_score(
    asset_id: str,
    sensor_readings_json: str = "{}",
) -> dict:
    """
    Compute real-time anomaly score for an asset using the IsolationForest + LSTM-AE ensemble.

    Returns a fused anomaly score [0-1], severity tier, and per-sensor SHAP attribution.

    Args:
        asset_id: Asset/equipment ID.
        sensor_readings_json: JSON string of latest sensor readings dict.

    Returns:
        dict with keys: score (float), severity (str), shap_values (dict),
        triggered_sensors (list[str]).
    """
    fallback_anomaly = {
        "score": 0.25,
        "severity": "low",
        "shap_values": {},
        "triggered_sensors": [],
        "model_used": "stub",
    }
    try:
        sensor_readings: dict = json.loads(sensor_readings_json) if sensor_readings_json else {}
    except json.JSONDecodeError:
        sensor_readings = {}

    try:
        from wizard.ml.anomaly_detector import get_anomaly_score
        equipment_class = resolve_equipment_class(asset_id)
        return get_anomaly_score(
            asset_id=asset_id,
            sensor_readings=sensor_readings,
            equipment_class=equipment_class,
        )
    except Exception as exc:
        logger.warning("ml_get_anomaly_score failed for %s: %s", asset_id, exc)
        return {**fallback_anomaly, "tool_error": str(exc)}


def ml_predict_failure(
    asset_id: str,
    sensor_readings_json: str = "{}",
) -> dict:
    """
    Run 4-class ordinal failure prediction (NORMAL / WARN_72H / WARN_24H / IMMINENT).

    Uses a calibrated LightGBM model with isotonic calibration trained on AI4I 2020 data.

    Args:
        asset_id: Asset/equipment ID.
        sensor_readings_json: JSON string of latest sensor readings dict.

    Returns:
        dict with keys: alert_class (str), probabilities (dict), calibrated (bool),
        top_shap_features (list), failure_modes (dict).
    """
    fallback_failure = {
        "alert_class": "NORMAL",
        "probabilities": {"NORMAL": 0.7, "WARN_72H": 0.2, "WARN_24H": 0.08, "IMMINENT": 0.02},
        "calibrated": False,
        "top_shap_features": [],
        "failure_modes": {},
        "model_used": "stub",
    }
    try:
        sensor_readings: dict = json.loads(sensor_readings_json) if sensor_readings_json else {}
    except json.JSONDecodeError:
        sensor_readings = {}

    try:
        from wizard.ml.failure_predictor import predict_failure
        equipment_class = resolve_equipment_class(asset_id)
        return predict_failure(
            asset_id=asset_id,
            sensor_readings=sensor_readings,
            equipment_class=equipment_class,
        )
    except Exception as exc:
        logger.warning("ml_predict_failure failed for %s: %s", asset_id, exc)
        return {**fallback_failure, "tool_error": str(exc)}


def ml_rca_analyze(
    asset_id: str,
    fault_code: str = "UNKNOWN",
    fault_description: str = "",
    context_chunks_json: str = "[]",
) -> dict:
    """
    Run 3-layer Root Cause Analysis: FMEA graph traversal + DoWhy GCM + LLM 5-whys.

    Args:
        asset_id: Asset/equipment ID.
        fault_code: Primary fault code (e.g. 'BRG-WEAR-001').
        fault_description: Natural-language fault description.
        context_chunks_json: JSON list of RAG context chunk texts.

    Returns:
        dict serialized from RCAResult: rca_id, cause_chain, root_cause_summary,
        five_whys, gcm_attributions, cited_sources.
    """
    fallback_rca = {
        "rca_id": "stub",
        "asset_id": asset_id,
        "fault_log_id": "unknown",
        "cause_chain": [
            {"node_id": fault_code, "node_label": fault_description or fault_code,
             "edge_relation": "causes", "cited_source": None, "layer": "stub"}
        ],
        "root_cause_summary": (
            f"Preliminary analysis: fault code {fault_code} detected on {asset_id}. "
            "Detailed RCA requires ML artifact deployment."
        ),
        "five_whys": [
            f"Why did {fault_code} occur? — Likely due to operational degradation.",
            "Why did degradation occur? — Maintenance interval may have lapsed.",
            "Why did maintenance lapse? — Scheduling gap in predictive maintenance window.",
            "Why was the gap not detected? — Anomaly threshold was not breached earlier.",
            "Why was threshold not triggered? — Gradual degradation below single-point threshold.",
        ],
        "gcm_attributions": {},
        "cited_sources": [],
        "model_used": "stub",
    }
    try:
        context_chunks: list = json.loads(context_chunks_json) if context_chunks_json else []
    except json.JSONDecodeError:
        context_chunks = []

    try:
        from wizard.ml.rca_engine import rca_analyze
        result = rca_analyze(
            asset_id=asset_id,
            fault_log_id="stub",
            fault_code=fault_code,
            fault_description=fault_description,
            sensor_df=None,
            context_chunks=context_chunks,
            anomaly_scores={},
        )
        return result.model_dump()
    except Exception as exc:
        logger.warning("ml_rca_analyze failed for %s: %s", asset_id, exc)
        return {**fallback_rca, "tool_error": str(exc)}


# ---------------------------------------------------------------------------
# WRPS tool
# ---------------------------------------------------------------------------

def wrps_score_priority(asset_id: str) -> dict:
    """
    Compute Weighted Risk Priority Score (WRPS) for an asset.

    Uses a 4-factor model: process criticality, delay severity, spare
    availability risk, and procurement lead time. Returns a WRPS in [0, 100]
    and a risk tier (LOW / MEDIUM / HIGH / CRITICAL).

    Args:
        asset_id: Asset/equipment ID to score.

    Returns:
        dict with keys: wrps (float), risk_tier (str), severity_factor,
        probability_factor, detectability_factor, business_impact_factor,
        spares_risk (str), critical_parts_out_of_stock (list[str]),
        cost_avoidance_inr (float or None).
    """
    fallback_wrps = {
        "risk_id": "stub",
        "asset_id": asset_id,
        "wrps": 35.0,
        "risk_tier": "medium",
        "severity_factor": 5.0,
        "probability_factor": 4.0,
        "detectability_factor": 5.0,
        "business_impact_factor": 4.0,
        "spares_risk": "ok",
        "critical_parts_out_of_stock": [],
        "estimated_downtime_hours": None,
        "cost_avoidance_inr": None,
        "model_used": "stub",
    }
    try:
        from wizard.backend.wrps import score_maintenance_priority
        result = score_maintenance_priority(asset_id)
        return result.model_dump()
    except Exception as exc:
        logger.warning("wrps_score_priority failed for %s: %s", asset_id, exc)
        return {**fallback_wrps, "tool_error": str(exc)}


# ---------------------------------------------------------------------------
# Tool registry — import this in graph.py
# ---------------------------------------------------------------------------

ALL_TOOLS = [
    rag_retrieve,
    rag_search_manuals,
    rag_search_incidents,
    ml_predict_rul,
    ml_get_anomaly_score,
    ml_predict_failure,
    ml_rca_analyze,
    wrps_score_priority,
]
