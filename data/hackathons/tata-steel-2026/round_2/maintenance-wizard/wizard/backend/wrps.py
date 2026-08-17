"""
wizard.backend.wrps
====================
Weighted Risk Priority Score (WRPS) engine — the maintenance prioritisation core.

WRPS is a 4+1 factor composite score in [0, 100] that directly maps to the
Tata Steel Problem Statement §5.2 priority dimensions:
  F1 — Process criticality     (weight 0.35)
  F2 — Delay severity          (weight 0.25) — derived from FaultLog.severity
  F3 — Spare availability risk (weight 0.20)
  F4 — Procurement lead time   (weight 0.12)
  F5 — ML signal (bonus)       (weight 0.08) — RUL + anomaly score blend

Weights are stored in data/feedback/wrps_weights.json and updated via EMA
on every engineer feedback call (FR6 — feedback-driven improvement).

AHP seed: the DEFAULT_WEIGHTS below were derived using pyDecision.AHP_Method
with a 5×5 pairwise comparison matrix encoding domain consensus. The vector
is stored in JSON so it is human-readable and auditable.

Public API:
  score_maintenance_priority(asset_id: str) -> RiskScore
      Synchronous. Creates its own DB session. Call from LangGraph tool context
      or wrap with asyncio.to_thread() in async routes.

  score_maintenance_priority_for_session(asset_id: str, session: Session) -> RiskScore
      Same computation but accepts an existing SQLModel session (for app.py routes).

  apply_feedback_to_weights(corrected_risk_level: AlertSeverity, asset_id: str) -> None
      EMA weight update triggered by POST /v1/feedback.

  get_current_weights() -> dict[str, float]
      Returns the current weight vector (for UI sliders / explainability).

  update_weights_from_ui(new_weights: dict[str, float]) -> None
      Direct weight override from Streamlit settings page.
"""
from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np
import structlog
from sqlmodel import Session, select
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from wizard.core.config import settings
from wizard.core.db import get_session, session_scope
from wizard.core.schemas import (
    AlertSeverity,
    AnomalyAlert,
    AssetProfile,
    FaultLog,
    RiskScore,
    SensorSummary,
    SparePart,
    _new_ulid,
)

log = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# AHP-seeded default weights (sum = 1.0)
DEFAULT_WEIGHTS: dict[str, float] = {
    "process_criticality": 0.35,
    "delay_severity":      0.25,
    "spare_availability":  0.20,
    "lead_time":           0.12,
    "ml_signal":           0.08,
}

# Factor normalization maps
_CRITICALITY_MAP: dict[str, float] = {
    "critical": 1.00,
    "high":     0.75,
    "medium":   0.50,
    "low":      0.25,
}

_SEVERITY_MAP: dict[str, float] = {
    "critical": 1.00,
    "high":     0.75,
    "medium":   0.50,
    "low":      0.25,
}

_RISK_LEVEL_MAP: dict[str, float] = {
    "critical": 1.00,
    "high":     0.67,
    "medium":   0.33,
    "low":      0.00,
}

# WRPS tier thresholds (tuned for ~5% CRITICAL / ~20% HIGH distribution)
_TIER_THRESHOLDS: list[tuple[float, AlertSeverity]] = [
    (75.0, AlertSeverity.CRITICAL),
    (50.0, AlertSeverity.HIGH),
    (25.0, AlertSeverity.MEDIUM),
    ( 0.0, AlertSeverity.LOW),
]

# Weights file location (relative to cwd)
_WEIGHTS_FILE: Path = Path("data/feedback/wrps_weights.json")

# EMA decay factor: w_new = 0.9 * w_old + 0.1 * w_corrected
_EMA_ALPHA: float = 0.10


# ---------------------------------------------------------------------------
# Weight persistence
# ---------------------------------------------------------------------------

def _load_weights() -> dict[str, float]:
    """Load weights from JSON file; fall back to DEFAULT_WEIGHTS if missing/corrupt."""
    try:
        if _WEIGHTS_FILE.exists():
            raw = json.loads(_WEIGHTS_FILE.read_text())
            # Validate: all keys present, sum approximately 1.0
            if set(raw.keys()) == set(DEFAULT_WEIGHTS.keys()):
                total = sum(raw.values())
                if abs(total - 1.0) < 0.01:
                    return raw
    except Exception as exc:
        log.warning("wrps.weights_load_failed", error=str(exc))
    return DEFAULT_WEIGHTS.copy()


def _save_weights(weights: dict[str, float]) -> None:
    """Persist weight vector to JSON file (creates directories as needed)."""
    try:
        _WEIGHTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        _WEIGHTS_FILE.write_text(json.dumps(weights, indent=2))
    except Exception as exc:
        log.error("wrps.weights_save_failed", error=str(exc))


# Singleton weight cache (loaded once, mutated by feedback)
_current_weights: dict[str, float] = _load_weights()


# ---------------------------------------------------------------------------
# Factor normalization helpers
# ---------------------------------------------------------------------------

def _norm_criticality(tier: str) -> float:
    return _CRITICALITY_MAP.get(tier.lower(), 0.50)


def _norm_delay(fault: Optional["FaultLog"]) -> float:
    """
    Map FaultLog to delay urgency [0, 1].

    COALESCE strategy — uses whichever signal is available:
      1. FaultLog.delay_hours (added by core fixer — float | None)
         Normalised against a 72-hour cap so a 3-day delay → 1.0.
      2. Fallback: FaultLog.severity string → _SEVERITY_MAP lookup.

    The getattr() guard makes this safe whether or not delay_hours is present
    on the schema (works before and after the core migration lands).
    """
    if fault is None:
        return 0.0
    delay_hours: Optional[float] = getattr(fault, "delay_hours", None)
    if delay_hours is not None:
        # Normalise: 72-hour max considered "full urgency"
        return min(float(delay_hours) / 72.0, 1.0)
    # Fallback: severity string proxy
    return _SEVERITY_MAP.get((fault.severity or "medium").lower(), 0.25)


def _norm_spare_availability(stock_qty: int, min_stock_qty: int) -> float:
    """
    Low stock = high urgency score [0, 1].
    Inversion: comfortable buffer → 0.0; stockout when min_qty > 0 → 1.0.
    """
    if min_stock_qty <= 0:
        return 0.0 if stock_qty > 0 else 1.0
    ratio = stock_qty / min_stock_qty      # 0=none, 1=at min, 2+=comfortable
    return float(max(0.0, 1.0 - (ratio / 2.0)))


def _norm_lead_time(lead_time_days: int, cap_days: float = 90.0) -> float:
    """Long lead time = high urgency (act now before it's too late)."""
    return min(float(lead_time_days) / cap_days, 1.0)


def _norm_ml_signal(
    anomaly_risk_level: Optional[str],
    rul_days_p50: Optional[float],
    rul_cap_days: float = 30.0,
) -> float:
    """Blended ML signal: 60% RUL urgency + 40% anomaly severity."""
    anomaly_score = _RISK_LEVEL_MAP.get((anomaly_risk_level or "low").lower(), 0.0)
    if rul_days_p50 is not None:
        rul_score = float(max(0.0, 1.0 - (rul_days_p50 / rul_cap_days)))
    else:
        rul_score = anomaly_score
    return 0.6 * rul_score + 0.4 * anomaly_score


def _tier_from_wrps(wrps: float) -> AlertSeverity:
    for threshold, tier in _TIER_THRESHOLDS:
        if wrps >= threshold:
            return tier
    return AlertSeverity.LOW


# ---------------------------------------------------------------------------
# SQL-based data collection helpers
# ---------------------------------------------------------------------------

def _fetch_asset(session: Session, asset_id: str) -> Optional[AssetProfile]:
    return session.exec(
        select(AssetProfile).where(AssetProfile.asset_id == asset_id)
    ).first()


def _fetch_latest_sensor(session: Session, asset_id: str) -> Optional[SensorSummary]:
    return session.exec(
        select(SensorSummary)
        .where(SensorSummary.asset_id == asset_id)
        .order_by(SensorSummary.window_end.desc())  # type: ignore[union-attr]
        .limit(1)
    ).first()


def _fetch_latest_fault(session: Session, asset_id: str) -> Optional[FaultLog]:
    """Fetch the latest confirmed fault (for delay severity proxy)."""
    return session.exec(
        select(FaultLog)
        .where(
            FaultLog.asset_id == asset_id,
            FaultLog.confirmed == True,  # noqa: E712
        )
        .order_by(FaultLog.detected_at.desc())  # type: ignore[union-attr]
        .limit(1)
    ).first()


def _fetch_spares_data(
    session: Session, asset_id: str
) -> tuple[int, int, int, list[str]]:
    """
    Return (min_stock_qty_worst, stock_qty_worst, max_lead_time_days, critical_stockouts).
    Picks the most urgent spare part (lowest stock ratio, longest lead time).
    """
    spares = session.exec(
        select(SparePart).where(SparePart.asset_id == asset_id)
    ).all()

    if not spares:
        return 1, 9999, 0, []  # no spares → comfortable defaults

    # Worst-case spare for availability (lowest stock/min ratio)
    worst_avail = min(
        spares,
        key=lambda s: (s.stock_qty / max(s.min_stock_qty, 1)),
        default=spares[0],
    )
    max_lead = max((s.lead_time_days for s in spares), default=0)
    critical_oos = [
        s.part_number
        for s in spares
        if s.stock_qty == 0 and s.criticality_override == "critical"
    ]

    return worst_avail.min_stock_qty, worst_avail.stock_qty, max_lead, critical_oos


def _fetch_latest_anomaly(session: Session, asset_id: str) -> Optional[AnomalyAlert]:
    return session.exec(
        select(AnomalyAlert)
        .where(
            AnomalyAlert.asset_id == asset_id,
            AnomalyAlert.acknowledged == False,  # noqa: E712
        )
        .order_by(AnomalyAlert.triggered_at.desc())  # type: ignore[union-attr]
        .limit(1)
    ).first()


# ---------------------------------------------------------------------------
# LLM narrative (tenacity-retried, circuit-breaker protected)
# ---------------------------------------------------------------------------

@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=30, jitter=3),
    reraise=False,
)
async def _llm_explain_risk(
    asset_id: str,
    risk_tier: AlertSeverity,
    factor_breakdown: dict[str, float],
) -> str:
    """
    Generate a two-sentence risk explanation via LiteLLM.
    Protected by tenacity retry (3 attempts, exponential backoff).
    Falls back to template on circuit-open or all retries exhausted.
    """
    from wizard.backend.middleware import llm_circuit_breaker, CircuitOpenError

    sorted_factors = sorted(factor_breakdown.items(), key=lambda x: -x[1])
    top_two = sorted_factors[:2]

    prompt_content = (
        f"Asset: {asset_id} | Risk: {risk_tier.value.upper()} | "
        f"Factor scores (0–1): {factor_breakdown} | "
        f"Top contributing factors: {top_two}"
    )

    try:
        import litellm  # type: ignore[import]

        async def _call() -> str:
            response = await litellm.acompletion(
                model=settings.llm_model_light,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a maintenance risk explainer for a steel plant. "
                            "Given a WRPS score breakdown, write exactly TWO sentences: "
                            "Sentence 1: state the risk tier and the top two contributing factors "
                            "with their values. "
                            "Sentence 2: state the single most urgent action the engineer should take. "
                            "Be specific. Do not repeat the WRPS number."
                        ),
                    },
                    {"role": "user", "content": prompt_content},
                ],
                max_tokens=150,
                temperature=0.1,
            )
            return str(response.choices[0].message.content).strip()

        return await llm_circuit_breaker.call(_call)

    except CircuitOpenError:
        log.warning("wrps.llm_circuit_open", asset_id=asset_id)
        raise  # let tenacity see it — but it's caught in the fallback wrapper

    except Exception as exc:
        log.warning("wrps.llm_call_failed", asset_id=asset_id, error=str(exc))
        raise


async def _get_narrative(
    asset_id: str,
    risk_tier: AlertSeverity,
    factor_breakdown: dict[str, float],
) -> str:
    """Narrative with guaranteed fallback — never raises."""
    try:
        return await _llm_explain_risk(asset_id, risk_tier, factor_breakdown)
    except Exception:
        # Template fallback
        sorted_factors = sorted(factor_breakdown.items(), key=lambda x: -x[1])
        top1_k, top1_v = sorted_factors[0] if sorted_factors else ("unknown", 0.0)
        top2_k, top2_v = sorted_factors[1] if len(sorted_factors) > 1 else ("unknown", 0.0)
        return (
            f"Risk tier {risk_tier.value.upper()} for {asset_id}: "
            f"primary driver is {top1_k} ({top1_v:.2f}) and {top2_k} ({top2_v:.2f}). "
            f"Review maintenance schedule and spare parts availability immediately."
        )


# ---------------------------------------------------------------------------
# Core WRPS computation
# ---------------------------------------------------------------------------

def _compute_wrps_sync(
    asset_id: str,
    session: Session,
) -> tuple[RiskScore, dict[str, float]]:
    """
    Synchronous WRPS computation. Returns (RiskScore, factor_breakdown).
    factor_breakdown is exposed for the explainability UI.
    """
    weights = _current_weights

    # Fetch inputs
    asset = _fetch_asset(session, asset_id)
    if asset is None:
        # Unknown asset — return minimal LOW score
        log.warning("wrps.asset_not_found", asset_id=asset_id)
        return _minimal_risk_score(asset_id), {}

    sensor = _fetch_latest_sensor(session, asset_id)
    fault = _fetch_latest_fault(session, asset_id)
    min_stock, stock_qty, max_lead, critical_oos = _fetch_spares_data(session, asset_id)
    anomaly = _fetch_latest_anomaly(session, asset_id)

    # Factor normalization
    f_criticality = _norm_criticality(asset.criticality_tier)
    f_delay = _norm_delay(fault)  # COALESCE: delay_hours if present, else severity proxy
    f_spare = _norm_spare_availability(stock_qty, min_stock)
    f_lead = _norm_lead_time(max_lead)
    f_ml = _norm_ml_signal(
        anomaly_risk_level=(anomaly.risk_level if anomaly else None),
        rul_days_p50=(sensor.rul_days_p50 if sensor else None),
    )

    factor_breakdown = {
        "process_criticality": round(f_criticality, 4),
        "delay_severity":      round(f_delay,       4),
        "spare_availability":  round(f_spare,       4),
        "lead_time":           round(f_lead,        4),
        "ml_signal":           round(f_ml,          4),
    }

    # Weighted sum → WRPS in [0, 100]
    raw_score = sum(weights[k] * v for k, v in factor_breakdown.items())
    wrps = round(float(np.clip(raw_score * 100.0, 0.0, 100.0)), 2)

    risk_tier = _tier_from_wrps(wrps)

    # Spare risk label
    if critical_oos:
        spares_risk = "critical_stockout"
    elif stock_qty < min_stock:
        spares_risk = "low_stock"
    elif max_lead > 30:
        spares_risk = "long_lead_time"
    else:
        spares_risk = "ok"

    # Map factors to RiskScore schema fields (0–10 range)
    risk_score = RiskScore(
        risk_id=_new_ulid(),
        asset_id=asset_id,
        wrps=wrps,
        risk_tier=risk_tier,
        severity_factor=round(f_criticality * 10, 2),
        probability_factor=round(f_ml * 10, 2),
        detectability_factor=round((1.0 - f_spare) * 10, 2),
        business_impact_factor=round(((f_delay * 0.5) + (f_lead * 0.5)) * 10, 2),
        spares_risk=spares_risk,
        critical_parts_out_of_stock=critical_oos,
        estimated_downtime_hours=(
            (sensor.rul_days_p50 * 24 * 0.1) if (sensor and sensor.rul_days_p50) else None
        ),
        cost_avoidance_inr=(
            (sensor.rul_days_p50 * 24 * settings.cost_avoidance_rate_inr_per_hour * 0.5)
            if (sensor and sensor.rul_days_p50 and risk_tier in (AlertSeverity.CRITICAL, AlertSeverity.HIGH))
            else None
        ),
        created_at=datetime.now(timezone.utc),
    )

    log.info(
        "wrps.scored",
        asset_id=asset_id,
        wrps=wrps,
        risk_tier=risk_tier.value,
        factor_breakdown=factor_breakdown,
    )

    return risk_score, factor_breakdown


def _minimal_risk_score(asset_id: str) -> RiskScore:
    return RiskScore(
        risk_id=_new_ulid(),
        asset_id=asset_id,
        wrps=0.0,
        risk_tier=AlertSeverity.LOW,
        severity_factor=0.0,
        probability_factor=0.0,
        detectability_factor=0.0,
        business_impact_factor=0.0,
        spares_risk="ok",
        critical_parts_out_of_stock=[],
        estimated_downtime_hours=None,
        cost_avoidance_inr=None,
        created_at=datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def score_maintenance_priority(asset_id: str) -> RiskScore:
    """
    Synchronous WRPS scoring — creates its own DB session via session_scope().

    This is the function the agentic-core LangGraph tool imports::

        from wizard.backend.wrps import score_maintenance_priority

        @tool
        def score_maintenance_priority_tool(asset_id: str) -> RiskScore:
            return score_maintenance_priority(asset_id)

    Returns:
        RiskScore with wrps ∈ [0, 100], risk_tier, factor breakdown fields.
        Never raises — returns LOW score on any error.
    """
    try:
        with session_scope() as session:
            score, _ = _compute_wrps_sync(asset_id, session)
            return score
    except Exception as exc:
        log.error("score_maintenance_priority.error", asset_id=asset_id, error=str(exc))
        return _minimal_risk_score(asset_id)


async def score_maintenance_priority_async(asset_id: str) -> RiskScore:
    """
    Async WRPS scoring for FastAPI route handlers.
    Runs the synchronous computation in a thread pool executor.
    Also generates the LLM narrative asynchronously.
    """
    # Run sync DB part in thread pool (non-blocking for event loop)
    loop = asyncio.get_running_loop()  # correct inside an async def (get_event_loop deprecated here)
    score = await loop.run_in_executor(None, score_maintenance_priority, asset_id)

    # Generate narrative asynchronously (does not block; has timeout + fallback)
    try:
        with session_scope() as session:
            _, factor_breakdown = _compute_wrps_sync(asset_id, session)
    except Exception:
        factor_breakdown = {}

    # Narrative is fire-and-forget — we don't attach it to RiskScore (no field for it)
    # It's logged for the observability trail
    if factor_breakdown:
        asyncio.create_task(
            _log_narrative(asset_id, score.risk_tier, factor_breakdown)
        )

    return score


async def _log_narrative(
    asset_id: str,
    risk_tier: AlertSeverity,
    factor_breakdown: dict[str, float],
) -> None:
    """Fire-and-forget narrative generation — logged only, not blocking."""
    narrative = await _get_narrative(asset_id, risk_tier, factor_breakdown)
    log.info(
        "wrps.llm_narrative",
        asset_id=asset_id,
        narrative=narrative[:200],
    )


def score_maintenance_priority_for_session(
    asset_id: str,
    session: Session,
) -> tuple[RiskScore, dict[str, float]]:
    """
    WRPS scoring with an existing session.
    Returns (RiskScore, factor_breakdown) for explainability display.
    """
    return _compute_wrps_sync(asset_id, session)


def get_current_weights() -> dict[str, float]:
    """Return the current weight vector (for UI sliders and audit)."""
    return dict(_current_weights)


def update_weights_from_ui(new_weights: dict[str, float]) -> None:
    """
    Direct weight override (from Streamlit Settings page slider).
    Normalises to sum=1.0 before saving.
    """
    global _current_weights
    total = sum(new_weights.values())
    if abs(total) < 1e-9:
        return
    normalised = {k: v / total for k, v in new_weights.items()}
    _current_weights = normalised
    _save_weights(normalised)
    log.info("wrps.weights_updated_from_ui", weights=normalised)


def apply_feedback_to_weights(
    corrected_risk_level: AlertSeverity,
    current_risk_level: AlertSeverity,
) -> bool:
    """
    EMA weight update triggered by engineer feedback (POST /v1/feedback).

    If the engineer says the risk is higher than scored → boost process_criticality.
    If lower → reduce delay_severity (most likely overweighted transient fault).

    Returns True if weights were updated.
    """
    global _current_weights

    update_needed = corrected_risk_level != current_risk_level

    # Map correction direction to nudge
    tier_order = [AlertSeverity.LOW, AlertSeverity.MEDIUM, AlertSeverity.HIGH, AlertSeverity.CRITICAL]
    current_idx = tier_order.index(current_risk_level)
    corrected_idx = tier_order.index(corrected_risk_level)

    if corrected_idx > current_idx:
        # Engineer upgraded: boost process_criticality
        nudge = {"process_criticality": 0.03}
    elif corrected_idx < current_idx:
        # Engineer downgraded: reduce delay_severity (most volatile factor)
        nudge = {"delay_severity": -0.02}
    else:
        return False

    weights = dict(_current_weights)
    for factor, delta in nudge.items():
        if factor in weights:
            weights[factor] = weights[factor] * (1 - _EMA_ALPHA) + (weights[factor] + delta) * _EMA_ALPHA

    # Re-normalise to sum=1.0
    total = sum(weights.values())
    if abs(total) > 1e-9:
        weights = {k: v / total for k, v in weights.items()}

    _current_weights = weights
    _save_weights(weights)
    log.info(
        "wrps.feedback_weight_update",
        corrected_risk_level=corrected_risk_level.value,
        current_risk_level=current_risk_level.value,
        new_weights=weights,
    )
    return True
