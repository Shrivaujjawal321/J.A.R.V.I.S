"""
AuditAgent canonical data models (Pydantic v2).

Source-of-truth types that drive runtime validation, API responses,
and state persistence. No `Any` in hot paths.
"""
from __future__ import annotations

import hashlib
import uuid
from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, computed_field


# ── Enums ──────────────────────────────────────────────────────────────────────


class AuditState(str, Enum):
    SCOPE_GATE              = "scope_gate"
    RECON                   = "recon"
    SCAN_RUNNING            = "scan_running"
    ANALYZE                 = "analyze"
    VERIFY                  = "verify"
    HUMAN_APPROVAL_PENDING  = "human_approval_pending"
    REPORT_GENERATING       = "report_generating"
    DONE                    = "done"
    SCOPE_DENIED            = "scope_denied"
    CANCELLED               = "cancelled"


TERMINAL_STATES: frozenset[AuditState] = frozenset({
    AuditState.DONE,
    AuditState.SCOPE_DENIED,
    AuditState.CANCELLED,
})


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH     = "high"
    MEDIUM   = "medium"
    LOW      = "low"
    INFO     = "info"


class VerificationStatus(str, Enum):
    UNVERIFIED     = "unverified"
    CONFIRMED      = "confirmed"
    FALSE_POSITIVE = "false_positive"
    NEEDS_MANUAL   = "needs_manual"


class OWASPCategory(str, Enum):
    A01_BAC          = "A01:2025-BAC"
    A02_MISCONFIG    = "A02:2025-Misconfig"
    A03_SUPPLY_CHAIN = "A03:2025-SupplyChain"
    A04_CRYPTO       = "A04:2025-CryptoFail"
    A05_INJECTION    = "A05:2025-Injection"
    SECRETS          = "SECRETS"
    SCA_CVE          = "SCA:CVE"
    UNKNOWN          = "UNKNOWN"


# ── Core finding model ─────────────────────────────────────────────────────────


def _dedupe_key(scanner: str, rule_id: str,
                file_path: str | None, line_start: int | None) -> str:
    """Stable 16-char hex hash for deduplication."""
    raw = f"{rule_id}|{file_path or ''}|{line_start or 0}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _mask_secret(secret: str) -> str:
    """Redact a secret value — show first 4 + last 4 chars only."""
    if not secret:
        return "****"
    if len(secret) <= 8:
        return secret[:2] + "****"
    return secret[:4] + "..." + secret[-4:]


class Finding(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scanner: str                                    # semgrep|trivy|osv|gitleaks|trufflehog
    rule_id: str
    cwe: str | None = None                          # e.g. "CWE-89"
    owasp_category: OWASPCategory | None = None
    cvss_vector: str | None = None                  # CVSS 4.0 vector string
    cvss_score: float | None = None                 # 0.0–10.0
    severity: Severity
    file_path: str | None = None
    line_start: int | None = None
    line_end: int | None = None
    endpoint: str | None = None                     # for API / web findings
    evidence: str                                   # snippet, message, rule description
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    confidence: float = 0.5                         # 0.0–1.0 from verify layer
    dedupe_key: str = Field(default="")
    remediation: str | None = None                  # LLM-generated fix suggestion
    verification_reason: str | None = None          # LLM/deterministic rationale for verdict
    related_finding_ids: list[str] = Field(default_factory=list)
    scanners_agreeing: list[str] = Field(default_factory=list)

    def model_post_init(self, __context: object) -> None:
        if not self.dedupe_key:
            self.dedupe_key = _dedupe_key(
                self.scanner, self.rule_id, self.file_path, self.line_start
            )

    @computed_field
    @property
    def is_actionable(self) -> bool:
        return (
            self.verification_status != VerificationStatus.FALSE_POSITIVE
            and self.severity in (Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM)
        )


# ── Scanner I/O ────────────────────────────────────────────────────────────────


class RawScanResult(BaseModel):
    scanner: str
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    duration_ms: int | None = None
    error: str | None = None                        # ToolTimeoutError, ToolCrashError, not_installed


# ── Target + scope ─────────────────────────────────────────────────────────────


class Target(BaseModel):
    target_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    kind: Literal["git_repo", "local_dir", "openapi_spec", "container_image"]
    uri: str                                        # file path or URL
    verified_owner: bool = False
    verification_method: str | None = None          # "dns_txt"|"codeowners"|"local"|"manual"
    language_hints: list[str] = Field(default_factory=list)


class ScopePolicy(BaseModel):
    target: Target
    included_paths: list[str] = Field(default_factory=lambda: ["**"])
    excluded_paths: list[str] = Field(
        default_factory=lambda: [".git/**", "node_modules/**", "vendor/**", "*.pyc"]
    )
    allowed_scanners: list[str] = Field(
        default_factory=lambda: ["semgrep", "trivy", "osv", "gitleaks", "trufflehog"]
    )
    allow_exploitation: bool = False                # Phase 4 gate — default OFF, Tier-3 confirm
    max_budget_usd: float = 2.0                     # per-run ceiling
    max_duration_seconds: int = 1800                # 30 min default


# ── Audit run (the main record) ────────────────────────────────────────────────


class AuditRun(BaseModel):
    audit_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    scope_policy: ScopePolicy
    audit_state: AuditState = AuditState.SCOPE_GATE
    idempotency_key: str | None = None              # from Idempotency-Key header
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    recon_output: dict = Field(default_factory=dict)
    raw_results: list[RawScanResult] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    exploitation_candidates: list[str] = Field(default_factory=list)   # finding IDs
    pending_approval_id: str | None = None
    report: AuditReport | None = None
    cost_usd_total: float = 0.0
    error: str | None = None

    def is_terminal(self) -> bool:
        return self.audit_state in TERMINAL_STATES

    def progress_pct(self) -> int:
        """Rough % progress through the pipeline."""
        order = [
            AuditState.SCOPE_GATE,
            AuditState.RECON,
            AuditState.SCAN_RUNNING,
            AuditState.ANALYZE,
            AuditState.VERIFY,
            AuditState.REPORT_GENERATING,
            AuditState.DONE,
        ]
        try:
            idx = order.index(self.audit_state)
            return int(idx / (len(order) - 1) * 100)
        except ValueError:
            return 0


# ── Report ─────────────────────────────────────────────────────────────────────


class AuditReport(BaseModel):
    audit_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    target_uri: str
    total_findings: int
    by_severity: dict[str, int]                     # {"critical":2,"high":7,...}
    top_findings: list[Finding]                     # top 10 by cvss_score
    markdown_body: str
    json_findings: list[Finding]
    cvss_distribution: dict[str, int] = Field(default_factory=dict)


# ── HTTP API shapes ────────────────────────────────────────────────────────────


class AuditRequest(BaseModel):
    user_id: str = "ujjwal"
    target_uri: str = Field(..., description="Local path or git URL to scan")
    target_kind: Literal["git_repo", "local_dir", "openapi_spec", "container_image"] = "local_dir"
    included_paths: list[str] = Field(default_factory=lambda: ["**"])
    excluded_paths: list[str] = Field(default_factory=list)
    allowed_scanners: list[str] = Field(
        default_factory=lambda: ["semgrep", "trivy", "osv", "gitleaks", "trufflehog"]
    )
    allow_exploitation: bool = False
    max_budget_usd: float = 2.0
    max_duration_seconds: int = 1800


class AuditRunView(BaseModel):
    """External view of an audit run (safe for API responses)."""
    audit_id: str
    audit_state: AuditState
    target_uri: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    progress_pct: int
    total_findings: int
    cost_usd_total: float
    error: str | None = None


class FindingsPage(BaseModel):
    """Cursor-paginated findings response."""
    items: list[Finding]
    next_cursor: str | None = None
    total: int


# Resolve forward references
AuditRun.model_rebuild()
