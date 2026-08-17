"""
AuditAgent FastAPI router — mounted at /v1/audit in daemon.py.

Endpoints:
  POST   /v1/audit                     Start a new audit (async, returns 202)
  GET    /v1/audit/{audit_id}           Poll audit status
  GET    /v1/audit/{audit_id}/report    Get full report (425 if still running)
  GET    /v1/audit/{audit_id}/findings  Cursor-paginated findings
  POST   /v1/audit/{audit_id}/cancel    Cancel a running audit

All 4xx/5xx return Stripe-style error envelopes.
Rate-limit headers included on every response.
"""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse

from ..state import JarvisState
from .models import (
    AuditReport,
    AuditRequest,
    AuditRun,
    AuditRunView,
    AuditState,
    Finding,
    FindingsPage,
    ScopePolicy,
    Severity,
    Target,
    TERMINAL_STATES,
    VerificationStatus,
)
from .state_machine import advance

log = logging.getLogger("jarvis_core.audit_agent.router")

router = APIRouter(prefix="/v1/audit", tags=["audit"])

# ── Rate-limit config (per-process, simple token bucket) ─────────────────────

_RATE_LIMIT = 10          # requests per window
_RATE_WINDOW_S = 60       # window in seconds
_request_timestamps: list[float] = []


def _rate_limit_headers(remaining: int) -> dict[str, str]:
    reset_ts = int(time.time()) + _RATE_WINDOW_S
    return {
        "X-RateLimit-Limit": str(_RATE_LIMIT),
        "X-RateLimit-Remaining": str(max(0, remaining)),
        "X-RateLimit-Reset": str(reset_ts),
    }


def _check_rate_limit() -> int:
    """Return remaining requests. Raises HTTPException 429 if exhausted."""
    now = time.time()
    cutoff = now - _RATE_WINDOW_S
    _request_timestamps[:] = [t for t in _request_timestamps if t > cutoff]
    remaining = _RATE_LIMIT - len(_request_timestamps)
    if remaining <= 0:
        raise HTTPException(
            status_code=429,
            detail=_error_envelope(
                "rate_limit_exceeded",
                "Too many audit requests. Retry after the reset window.",
                "rate_limit",
            ),
        )
    _request_timestamps.append(now)
    return remaining - 1


# ── Error helpers ─────────────────────────────────────────────────────────────


def _error_envelope(
    code: str,
    message: str,
    error_type: str,
    doc_url: str | None = None,
) -> dict[str, Any]:
    env: dict[str, Any] = {"code": code, "message": message, "type": error_type}
    if doc_url:
        env["doc_url"] = doc_url
    return {"error": env}


def _audit_to_view(run: AuditRun) -> AuditRunView:
    return AuditRunView(
        audit_id=run.audit_id,
        audit_state=run.audit_state,
        target_uri=run.scope_policy.target.uri,
        user_id=run.user_id,
        created_at=run.created_at,
        updated_at=run.updated_at,
        progress_pct=run.progress_pct(),
        total_findings=len([
            f for f in run.findings
            if f.verification_status != VerificationStatus.FALSE_POSITIVE
        ]),
        cost_usd_total=run.cost_usd_total,
        error=run.error,
    )


# ── State accessor helper ─────────────────────────────────────────────────────


def _get_jarvis_state(request: Request) -> JarvisState:
    """Get JarvisState from app state (injected at startup)."""
    state = getattr(request.app.state, "jarvis_state", None)
    if state is None:
        raise HTTPException(
            status_code=503,
            detail=_error_envelope("service_unavailable", "State not initialized.", "server"),
        )
    return state


# ── Background audit driver ───────────────────────────────────────────────────


async def _drive_audit(audit_id: str, state: JarvisState) -> None:
    """Background task: drives audit FSM to completion."""
    run = await state.get_audit(audit_id)
    if run is None:
        log.error("Audit %s not found in state — aborting background driver", audit_id)
        return

    while run.audit_state not in TERMINAL_STATES:
        if run.audit_state == AuditState.HUMAN_APPROVAL_PENDING:
            # Poll every 10s while waiting for approval
            await asyncio.sleep(10)
        run = await advance(run, state)

    log.info(
        "Audit %s finished in state=%s findings=%d",
        audit_id, run.audit_state.value, len(run.findings),
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post("", status_code=202)
async def start_audit(
    req: AuditRequest,
    background: BackgroundTasks,
    request: Request,
    response: Response,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict:
    """Start a new security audit. Returns 202 Accepted with audit_id.

    Use GET /v1/audit/{audit_id} to poll progress.
    Use Idempotency-Key header to safely retry — same key within 24h returns existing run.
    """
    remaining = _check_rate_limit()
    state = _get_jarvis_state(request)

    # Idempotency check — return existing run for same key
    if idempotency_key:
        existing = await _find_by_idempotency_key(state, idempotency_key)
        if existing:
            for k, v in _rate_limit_headers(remaining).items():
                response.headers[k] = v
            return _audit_to_view(existing).model_dump(mode="json")

    # Scope policy — excluded_paths merge defaults + user overrides
    default_excluded = [".git/**", "node_modules/**", "vendor/**", "*.pyc", "__pycache__/**"]
    excluded = list(set(default_excluded + req.excluded_paths))

    target = Target(
        kind=req.target_kind,
        uri=req.target_uri,
        language_hints=[],
    )
    scope = ScopePolicy(
        target=target,
        included_paths=req.included_paths,
        excluded_paths=excluded,
        allowed_scanners=req.allowed_scanners,
        allow_exploitation=req.allow_exploitation,
        max_budget_usd=req.max_budget_usd,
        max_duration_seconds=req.max_duration_seconds,
    )

    run = AuditRun(
        audit_id=uuid.uuid4().hex[:12],
        user_id=req.user_id,
        scope_policy=scope,
        idempotency_key=idempotency_key,
    )
    await state.add_audit(run)
    background.add_task(_drive_audit, run.audit_id, state)

    log.info(
        "Audit started id=%s user=%s target=%r",
        run.audit_id, req.user_id, req.target_uri,
    )

    for k, v in _rate_limit_headers(remaining).items():
        response.headers[k] = v
    return _audit_to_view(run).model_dump(mode="json")


@router.get("/{audit_id}")
async def get_audit(
    audit_id: str,
    request: Request,
    response: Response,
) -> dict:
    """Poll audit progress."""
    remaining = _check_rate_limit()
    state = _get_jarvis_state(request)

    run = await state.get_audit(audit_id)
    if run is None:
        raise HTTPException(
            status_code=404,
            detail=_error_envelope("not_found", f"Audit {audit_id!r} not found.", "client"),
        )

    for k, v in _rate_limit_headers(remaining).items():
        response.headers[k] = v
    return _audit_to_view(run).model_dump(mode="json")


@router.get("/{audit_id}/report")
async def get_report(
    audit_id: str,
    request: Request,
    response: Response,
) -> dict:
    """Get the full audit report. Returns 425 if audit is still running."""
    remaining = _check_rate_limit()
    state = _get_jarvis_state(request)

    run = await state.get_audit(audit_id)
    if run is None:
        raise HTTPException(
            status_code=404,
            detail=_error_envelope("not_found", f"Audit {audit_id!r} not found.", "client"),
        )
    if run.audit_state not in TERMINAL_STATES or run.audit_state != AuditState.DONE:
        if run.audit_state == AuditState.DONE and run.report:
            pass  # Fall through
        else:
            raise HTTPException(
                status_code=425,
                detail=_error_envelope(
                    "too_early",
                    f"Audit is in state {run.audit_state.value!r}. "
                    "Wait for state=done before fetching the report.",
                    "client",
                ),
            )
    if run.report is None:
        raise HTTPException(
            status_code=500,
            detail=_error_envelope("no_report", "Report was not generated.", "server"),
        )

    for k, v in _rate_limit_headers(remaining).items():
        response.headers[k] = v
    return run.report.model_dump(mode="json")


@router.get("/{audit_id}/findings")
async def get_findings(
    audit_id: str,
    request: Request,
    response: Response,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
    severity: str | None = Query(default=None, description="Comma-separated: critical,high,medium,low,info"),
    status: str | None = Query(default=None, description="Comma-separated: confirmed,needs_manual,false_positive,unverified"),
) -> dict:
    """Cursor-paginated findings. cursor is opaque (index-based)."""
    remaining = _check_rate_limit()
    state = _get_jarvis_state(request)

    run = await state.get_audit(audit_id)
    if run is None:
        raise HTTPException(
            status_code=404,
            detail=_error_envelope("not_found", f"Audit {audit_id!r} not found.", "client"),
        )

    findings = run.findings

    # Filter by severity
    if severity:
        requested_sevs = {s.strip().lower() for s in severity.split(",")}
        findings = [f for f in findings if f.severity.value in requested_sevs]

    # Filter by verification status
    if status:
        requested_statuses = {s.strip().lower() for s in status.split(",")}
        findings = [f for f in findings if f.verification_status.value in requested_statuses]

    # Sort by CVSS score descending for deterministic ordering
    findings = sorted(
        findings,
        key=lambda f: (f.cvss_score or 0.0, ["critical","high","medium","low","info"].index(f.severity.value)),
        reverse=True,
    )

    total = len(findings)
    offset = int(cursor) if cursor and cursor.isdigit() else 0
    page = findings[offset:offset + limit]
    next_offset = offset + limit
    next_cursor = str(next_offset) if next_offset < total else None

    for k, v in _rate_limit_headers(remaining).items():
        response.headers[k] = v

    return FindingsPage(
        items=page,
        next_cursor=next_cursor,
        total=total,
    ).model_dump(mode="json")


@router.post("/{audit_id}/cancel")
async def cancel_audit(
    audit_id: str,
    request: Request,
    response: Response,
) -> dict:
    """Cancel a running audit."""
    remaining = _check_rate_limit()
    state = _get_jarvis_state(request)

    run = await state.get_audit(audit_id)
    if run is None:
        raise HTTPException(
            status_code=404,
            detail=_error_envelope("not_found", f"Audit {audit_id!r} not found.", "client"),
        )
    if run.audit_state in TERMINAL_STATES:
        raise HTTPException(
            status_code=409,
            detail=_error_envelope(
                "already_terminal",
                f"Audit is already in terminal state {run.audit_state.value!r}.",
                "client",
            ),
        )

    run.audit_state = AuditState.CANCELLED
    run.updated_at = datetime.utcnow()
    run.error = "Cancelled by user"
    async with state._lock:
        state._audits[audit_id] = run

    for k, v in _rate_limit_headers(remaining).items():
        response.headers[k] = v
    return {"cancelled": True, "audit_id": audit_id}


# ── Idempotency helper ────────────────────────────────────────────────────────


async def _find_by_idempotency_key(state: JarvisState, key: str) -> AuditRun | None:
    """Find an existing AuditRun by idempotency key (within 24h)."""
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(hours=24)
    audits = await state.list_audits(limit=200)
    for run in audits:
        if run.idempotency_key == key and run.created_at >= cutoff:
            return run
    return None
