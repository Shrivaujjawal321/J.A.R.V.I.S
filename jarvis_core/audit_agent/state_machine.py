"""
AuditAgent FSM — advance() coroutine.

Each call drives ONE state transition. Called in a loop by the audit scheduler.
State is persisted to JarvisState after every transition.

Safety rules:
- allow_exploitation defaults False; Phase 4 requires human Tier-3 approval.
- SCOPE_DENIED and CANCELLED are terminal — advance() is a no-op on them.
- All errors are caught and stored in AuditRun.error; transition to CANCELLED.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime

from ..models import ApprovalDecision, ApprovalRequest
from .models import AuditRun, AuditState, TERMINAL_STATES
from .pipeline import run_recon, run_scanners, normalize_dedupe_correlate, verify_findings, generate_report
from .scope import verify_scope

log = logging.getLogger("jarvis_core.audit_agent.state_machine")


async def advance(run: AuditRun, state: object) -> AuditRun:
    """Drive one state transition on AuditRun.

    `state` is a JarvisState instance. We call:
      - state.add_approval(approval) for HUMAN_APPROVAL_PENDING
      - state.sync_to_disk() after every transition
      - state._audits[run.audit_id] = run (direct dict mutation, lock-free)

    Returns the updated AuditRun. Never raises — errors → CANCELLED.
    """
    if run.audit_state in TERMINAL_STATES:
        return run  # Nothing to do

    try:
        match run.audit_state:
            case AuditState.SCOPE_GATE:
                log.info("audit=%s SCOPE_GATE start", run.audit_id)
                ok = await verify_scope(run.scope_policy)
                if ok:
                    run.audit_state = AuditState.RECON
                    log.info("audit=%s scope verified → RECON", run.audit_id)
                else:
                    run.audit_state = AuditState.SCOPE_DENIED
                    run.error = (
                        "Target ownership could not be verified. "
                        "For local_dir targets, ensure the path is under $HOME. "
                        "For git_repo targets, add Boss's email to CODEOWNERS."
                    )
                    log.warning("audit=%s SCOPE_DENIED", run.audit_id)

            case AuditState.RECON:
                log.info("audit=%s RECON start", run.audit_id)
                run.recon_output = await run_recon(run)
                run.audit_state = AuditState.SCAN_RUNNING
                log.info(
                    "audit=%s recon done: files=%s langs=%s → SCAN_RUNNING",
                    run.audit_id,
                    run.recon_output.get("file_count", "?"),
                    list(run.recon_output.get("languages", {}).keys()),
                )

            case AuditState.SCAN_RUNNING:
                log.info("audit=%s SCAN_RUNNING start", run.audit_id)
                run.raw_results = await run_scanners(run)
                run.audit_state = AuditState.ANALYZE
                raw_count = sum(
                    1 for r in run.raw_results if not r.error
                )
                log.info(
                    "audit=%s scan done: %d scanners completed → ANALYZE",
                    run.audit_id, raw_count,
                )

            case AuditState.ANALYZE:
                log.info("audit=%s ANALYZE start", run.audit_id)
                run.findings = await normalize_dedupe_correlate(run.raw_results)
                run.audit_state = AuditState.VERIFY
                log.info(
                    "audit=%s analyze done: %d findings → VERIFY",
                    run.audit_id, len(run.findings),
                )

            case AuditState.VERIFY:
                log.info("audit=%s VERIFY start (budget=$%.2f)", run.audit_id, run.scope_policy.max_budget_usd)

                # Reachability pre-pass: for SCA (osv) findings, check whether the
                # vulnerable package is actually imported by the audited code.
                # Unused/transitive deps get downgraded (recall-safe, never deleted)
                # so a wall of CVEs becomes a prioritized few before LLM verify.
                from .reachability import assess_reachability, apply_verdict
                _target = run.scope_policy.target.uri
                for _f in run.findings:
                    if _f.scanner == "osv":
                        try:
                            _v = assess_reachability(_f, _target)
                            apply_verdict(_f, _v)
                        except Exception as exc:  # never let reachability break the run
                            log.debug("reachability skipped for %s: %s", _f.id, exc)

                updated_findings, exploitation_ids = await verify_findings(
                    run.findings,
                    max_budget_usd=run.scope_policy.max_budget_usd - run.cost_usd_total,
                )
                run.findings = updated_findings
                run.exploitation_candidates = exploitation_ids

                if exploitation_ids and run.scope_policy.allow_exploitation:
                    # Tier-3: create ApprovalRequest, pause for Boss
                    approval = ApprovalRequest(
                        approval_id=uuid.uuid4().hex[:12],
                        goal_id=run.audit_id,  # Re-use goal_id field for audit_id
                        sub_id="phase4_exploitation",
                        action_summary=(
                            f"AuditAgent Phase 4: Active exploitation on "
                            f"{run.scope_policy.target.uri} — "
                            f"{len(exploitation_ids)} HIGH/CRIT confirmed findings."
                        ),
                        action_payload={
                            "audit_id": run.audit_id,
                            "finding_ids": exploitation_ids,
                        },
                        risk_notes=[
                            "Phase 4 exploitation is irreversible for the target system.",
                            "Only proceed if you have written authorization.",
                            "Jarvis will run PoC replay in read-only detection mode only.",
                        ],
                    )
                    await state.add_approval(approval)
                    run.pending_approval_id = approval.approval_id
                    run.audit_state = AuditState.HUMAN_APPROVAL_PENDING
                    log.info(
                        "audit=%s HUMAN_APPROVAL_PENDING approval=%s",
                        run.audit_id, approval.approval_id,
                    )
                else:
                    run.audit_state = AuditState.REPORT_GENERATING
                    log.info("audit=%s verify done → REPORT_GENERATING", run.audit_id)

            case AuditState.HUMAN_APPROVAL_PENDING:
                # Poll the approval decision
                approval = await state.get_approval(run.pending_approval_id)
                if approval is None:
                    # Approval vanished — treat as rejected
                    run.audit_state = AuditState.REPORT_GENERATING
                    log.warning("audit=%s approval not found — skipping Phase 4", run.audit_id)
                elif approval.decision == ApprovalDecision.APPROVED:
                    # Phase 4 approved — for now, just advance to report
                    # (full exploitation engine is out of scope for MVP)
                    run.audit_state = AuditState.REPORT_GENERATING
                    log.info("audit=%s Phase 4 APPROVED → REPORT_GENERATING", run.audit_id)
                elif approval.decision == ApprovalDecision.REJECTED:
                    run.audit_state = AuditState.REPORT_GENERATING
                    log.info("audit=%s Phase 4 REJECTED → REPORT_GENERATING (report without exploitation)", run.audit_id)
                else:
                    # Still PENDING — don't advance, caller retries
                    log.debug("audit=%s still awaiting approval", run.audit_id)
                    return run  # Don't persist yet — nothing changed

            case AuditState.REPORT_GENERATING:
                log.info("audit=%s REPORT_GENERATING start", run.audit_id)
                run.report = await generate_report(run)
                run.audit_state = AuditState.DONE
                log.info(
                    "audit=%s DONE: %d findings (%d confirmed, %d fp)",
                    run.audit_id,
                    run.report.total_findings,
                    sum(1 for f in run.findings if f.verification_status.value == "confirmed"),
                    sum(1 for f in run.findings if f.verification_status.value == "false_positive"),
                )

            case _:
                log.error("audit=%s unknown state %r — cancelling", run.audit_id, run.audit_state)
                run.audit_state = AuditState.CANCELLED
                run.error = f"Unknown state: {run.audit_state!r}"

    except Exception as exc:
        log.exception("audit=%s exception in state=%s: %s", run.audit_id, run.audit_state, exc)
        run.error = f"{type(exc).__name__}: {exc}"
        run.audit_state = AuditState.CANCELLED

    run.updated_at = datetime.utcnow()

    # Persist to JarvisState — store in _audits dict (added by state.py patch)
    try:
        async with state._lock:
            state._audits[run.audit_id] = run
        await state.sync_to_disk()
    except Exception as exc:
        log.warning("audit=%s state persist failed: %s", run.audit_id, exc)

    return run
