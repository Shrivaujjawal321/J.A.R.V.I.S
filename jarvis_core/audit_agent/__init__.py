"""
AuditAgent — Defensive SAST + SCA + Secrets scanner for authorized targets.

Phase PTES 1-3 + 7 run autonomously.
Phase 4 (active exploitation) gates on human Tier-3 approval.
Phases 5-6 (post-exploitation) are permanently refused.
"""
from .models import (
    AuditRun,
    AuditState,
    AuditReport,
    Finding,
    ScopePolicy,
    Target,
    RawScanResult,
    Severity,
    VerificationStatus,
    TERMINAL_STATES,
)
from .state_machine import advance
from .router import router

__all__ = [
    "AuditRun",
    "AuditState",
    "AuditReport",
    "Finding",
    "ScopePolicy",
    "Target",
    "RawScanResult",
    "Severity",
    "VerificationStatus",
    "TERMINAL_STATES",
    "advance",
    "router",
]
