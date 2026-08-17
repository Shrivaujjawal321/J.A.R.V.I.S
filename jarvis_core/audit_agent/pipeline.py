"""
AuditAgent pipeline — normalize, dedupe, verify, report.

normalize_dedupe_correlate: Combines raw scanner outputs into canonical Finding list.
verify_findings: Two-pass LLM triage (Haiku fast → Sonnet deep for HIGH/CRIT).
generate_report: Produces AuditReport with Markdown body.

Verify layer degradation contract:
- If run_worker fails or LLM is unavailable → fall back to deterministic heuristics.
- Multi-scanner agreement (2+) → confidence += 0.2, keep as UNVERIFIED.
- No LLM call can ORIGINATE a finding. It can only confirm or reject existing findings.
- Budget exceeded → remaining findings marked NEEDS_MANUAL, run continues.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import re
import time
from datetime import datetime
from pathlib import Path

from .context import classify_context
from .models import (
    AuditReport,
    AuditRun,
    Finding,
    OWASPCategory,
    RawScanResult,
    Severity,
    ScopePolicy,
    VerificationStatus,
)
from .tools import (
    GitleaksAdapter,
    OsvScannerAdapter,
    SemgrepAdapter,
    TruffleHogAdapter,
    TrivyAdapter,
    ToolInput,
)

log = logging.getLogger("jarvis_core.audit_agent.pipeline")

PROJECT_ROOT = Path(
    os.getenv("JARVIS_PROJECT_PATH", str(Path(__file__).resolve().parent.parent.parent))
).resolve()

MAX_CONCURRENT_SCANS = int(os.getenv("AUDIT_MAX_CONCURRENT", "3"))

# Verify-layer LLM timeouts (seconds). run_worker spawns a full Claude Code
# worker (process start + one turn), so 30s was too tight — the worker hadn't
# returned yet and verify silently degraded to deterministic. Env-overridable.
_HAIKU_VERIFY_TIMEOUT = int(os.getenv("AUDIT_HAIKU_TIMEOUT", "90"))
_SONNET_VERIFY_TIMEOUT = int(os.getenv("AUDIT_SONNET_TIMEOUT", "120"))

# Haiku model name — mirrors critic.py
_HAIKU_MODEL = "claude-haiku-4-5-20251001"

_ALL_ADAPTERS = [
    SemgrepAdapter(),
    TrivyAdapter(),
    OsvScannerAdapter(),
    GitleaksAdapter(),
    TruffleHogAdapter(),
]

# ── Severity ordering ──────────────────────────────────────────────────────────

_SEV_RANK: dict[Severity, int] = {
    Severity.CRITICAL: 5,
    Severity.HIGH:     4,
    Severity.MEDIUM:   3,
    Severity.LOW:      2,
    Severity.INFO:     1,
}


# ── Recon ──────────────────────────────────────────────────────────────────────


async def run_recon(run: AuditRun) -> dict:
    """Walk the target directory, detect languages, compute content hash."""
    target_path = run.scope_policy.target.uri
    output: dict = {
        "target_uri": target_path,
        "file_count": 0,
        "languages": {},
        "content_hash": "",
        "error": None,
    }

    ext_map: dict[str, int] = {}
    file_list: list[str] = []

    try:
        p = Path(target_path)
        if not p.exists():
            output["error"] = f"Target path does not exist: {target_path}"
            return output

        for f in p.rglob("*"):
            if f.is_file():
                rel = str(f.relative_to(p))
                # Skip hidden / build dirs
                if any(part.startswith((".", "__pycache__", "node_modules")) for part in f.parts):
                    continue
                ext = f.suffix.lower()
                ext_map[ext] = ext_map.get(ext, 0) + 1
                file_list.append(rel)

        # Language detection by extension
        lang_map: dict[str, list[str]] = {
            "python": [".py"], "typescript": [".ts", ".tsx"],
            "javascript": [".js", ".jsx", ".mjs"], "go": [".go"],
            "java": [".java"], "rust": [".rs"], "ruby": [".rb"],
            "c": [".c", ".h"], "cpp": [".cpp", ".cc", ".cxx", ".hpp"],
            "yaml": [".yaml", ".yml"], "json": [".json"],
            "dockerfile": ["dockerfile"], "shell": [".sh", ".bash"],
        }
        detected: dict[str, int] = {}
        for lang, exts in lang_map.items():
            count = sum(ext_map.get(e, 0) for e in exts)
            if count:
                detected[lang] = count

        # Sort file_list for determinism, then hash
        file_list.sort()
        content_hash = hashlib.sha256(
            (target_path + "\0" + "\n".join(file_list)).encode()
        ).hexdigest()[:16]

        output["file_count"] = len(file_list)
        output["languages"] = detected
        output["content_hash"] = content_hash

    except Exception as exc:
        log.warning("Recon error: %s", exc)
        output["error"] = str(exc)

    log.info(
        "recon: %d files, langs=%s, hash=%s",
        output["file_count"], list(output["languages"].keys()), output["content_hash"],
    )
    return output


# ── Scanner fan-out ────────────────────────────────────────────────────────────


async def run_scanners(run: AuditRun) -> list[RawScanResult]:
    """Run enabled scanners in parallel with concurrency cap. Always returns."""
    target_path = run.scope_policy.target.uri
    allowed = set(run.scope_policy.allowed_scanners)

    adapters = [a for a in _ALL_ADAPTERS if a.name in allowed]
    if not adapters:
        log.warning("No adapters matched allowed_scanners=%s", run.scope_policy.allowed_scanners)
        return []

    sem = asyncio.Semaphore(MAX_CONCURRENT_SCANS)

    async def _run_one(adapter):
        async with sem:
            # Each adapter declares its own timeout (SAST needs more than secrets/SCA).
            inp = ToolInput(
                target_path=target_path,
                timeout_seconds=getattr(adapter, "default_timeout", 120),
            )
            try:
                raw = await adapter.run(inp)
                return raw
            except Exception as exc:
                log.warning("adapter=%s unexpected exception: %s", adapter.name, exc)
                return RawScanResult(
                    scanner=adapter.name,
                    exit_code=-1,
                    error=f"unexpected:{exc}",
                )

    results = await asyncio.gather(*(_run_one(a) for a in adapters))
    log.info(
        "scanners done: %s",
        {r.scanner: (r.error or f"exit={r.exit_code}") for r in results},
    )
    return list(results)


# ── Normalize, dedupe, correlate ───────────────────────────────────────────────


async def normalize_dedupe_correlate(raw_results: list[RawScanResult]) -> list[Finding]:
    """Normalize all raw scanner outputs → deduplicate → correlate."""

    # Build adapter lookup
    adapter_map = {a.name: a for a in _ALL_ADAPTERS}

    all_findings: list[Finding] = []
    for raw in raw_results:
        if raw.error:
            continue  # Scanner errored or not installed — skip normalization
        adapter = adapter_map.get(raw.scanner)
        if not adapter:
            log.warning("No adapter found for scanner=%r", raw.scanner)
            continue
        try:
            findings = adapter.normalize(raw)
            all_findings.extend(findings)
        except Exception as exc:
            log.warning("normalize failed for scanner=%s: %s", raw.scanner, exc)

    # Deduplicate: group by dedupe_key, keep highest severity, merge scanner list
    deduped: dict[str, Finding] = {}
    for f in all_findings:
        key = f.dedupe_key
        if key not in deduped:
            deduped[key] = f.model_copy(deep=True)
            if f.scanner not in deduped[key].scanners_agreeing:
                deduped[key].scanners_agreeing.append(f.scanner)
        else:
            existing = deduped[key]
            # Promote to higher severity if found
            if _SEV_RANK.get(f.severity, 0) > _SEV_RANK.get(existing.severity, 0):
                deduped[key] = f.model_copy(deep=True)
                # Preserve the agreeing scanner list
                for s in existing.scanners_agreeing:
                    if s not in deduped[key].scanners_agreeing:
                        deduped[key].scanners_agreeing.append(s)
            # Add this scanner to agreeing list
            if f.scanner not in deduped[key].scanners_agreeing:
                deduped[key].scanners_agreeing.append(f.scanner)

    # Boost confidence when multiple scanners agree
    for f in deduped.values():
        if len(f.scanners_agreeing) >= 2:
            f.confidence = min(f.confidence + 0.2, 1.0)

    # Correlate: same file + adjacent lines (within 10 lines) → link findings
    findings_list = list(deduped.values())
    _correlate_findings(findings_list)

    log.info(
        "normalize: raw=%d → deduped=%d findings",
        len(all_findings), len(findings_list),
    )
    return findings_list


def _correlate_findings(findings: list[Finding]) -> None:
    """Mutate findings in-place: link findings in same file within 10 lines."""
    by_file: dict[str, list[Finding]] = {}
    for f in findings:
        if f.file_path:
            by_file.setdefault(f.file_path, []).append(f)

    for file_findings in by_file.values():
        for i, f1 in enumerate(file_findings):
            for f2 in file_findings[i + 1:]:
                l1 = f1.line_start or 0
                l2 = f2.line_start or 0
                if abs(l1 - l2) <= 10 and f1.id != f2.id:
                    if f2.id not in f1.related_finding_ids:
                        f1.related_finding_ids.append(f2.id)
                    if f1.id not in f2.related_finding_ids:
                        f2.related_finding_ids.append(f1.id)


# ── Verify layer (two-pass Haiku → Sonnet) ────────────────────────────────────


_HAIKU_TRIAGE_PROMPT = """You are AuditAgent's verification critic. DEFAULT TO SKEPTICAL.
A finding is only confirmed if the evidence clearly supports it.
You may NOT confirm a finding the evidence does not support. Absence of evidence = "needs_manual".
You may NEVER originate a finding — your job is to confirm, downgrade, or reject existing ones.

FILE CONTEXT GUIDANCE (use this to calibrate your verdict):
- file_context = "test": The finding is in a test file. Hardcoded keys/secrets are almost
  certainly test fixtures, not real credentials. Mark false_positive unless evidence is
  extraordinary (e.g. the key appears live-verified by trufflehog --results=verified).
- file_context = "documentation": The finding is in a Markdown/RST/docs file. Strings like
  sk_live_realProductionKey, jwt_secret="prod-jwt-key-xyz789", or AKIAIOSFODNN7EXAMPLE in docs
  are documentation placeholders by convention. Mark false_positive.
- file_context = "example": The finding is in an example/fixture/mock/sample file. Treat any
  key or credential as a placeholder unless it is verified-live. Mark false_positive.
- file_context = "config_local": The file is a local-only config (.env.local, etc.) gitignored
  by convention. The secret is REAL but dev-scoped. Mark confirmed if clearly a real secret,
  but note the lower production risk in your reason. Do NOT mark false_positive just because
  it is gitignored.
- file_context = "source": Production application code. Trust the scanner. Mark confirmed if
  the evidence (rule_id, evidence snippet) clearly indicates a real vulnerability or live
  credential. Mark needs_manual when uncertain.
- file_context = "build": Generated/vendored code. Treat like example — high FP prior.

SCA / DEPENDENCY CVE RULES:
- For dependency CVEs (scanner = "trivy" or "osv", rule_id contains "CVE-" or "GHSA-"),
  you MUST give a concrete verdict (confirmed OR needs_manual) with a one-line reason.
  NEVER return needs_manual with an empty reason. State WHY: e.g. "CVE affects lodash.template
  which is not used in this codebase" (needs_manual / false_positive) or "package version is
  within the affected range and no lock-file pin or mitigation is visible" (confirmed).

For each finding, output ONLY a JSON object on a single line:
{{"id": "<finding_id>", "verdict": "confirmed|false_positive|needs_manual", "reason": "<1 sentence, mandatory>"}}

Findings to triage (JSON array):
{findings_json}

Rules:
- Documentation-placeholder secrets (in .md, docs/, content/) → false_positive
- Test fixtures / example values / non-production code (file_context = test/example) → false_positive
- Commented-out code → false_positive
- Local dev config (.env.local, etc.) → confirmed (real but local) if clearly a real secret
- Hard evidence of real production code path → confirmed
- Uncertain or missing context → needs_manual (with a reason explaining what is missing)

Output one JSON object per line, one per finding. Nothing else."""


_SONNET_DEEP_PROMPT = """You are AuditAgent's senior verification analyst.
Perform deep analysis of the following HIGH/CRITICAL security finding.
Provide: (1) confirmation of severity, (2) concrete remediation, (3) exploitability assessment.
You may NEVER originate a finding — only confirm, downgrade, or reject.

FILE CONTEXT: The finding's file_context field tells you where in the codebase this appears.
Apply the same context rules as the Haiku triage pass:
- test/example/documentation → very high FP prior; require extraordinary evidence to confirm
- config_local → real but local/gitignored; confirm with lowered severity note
- source → production code; confirm if evidence supports it

For SCA/CVE findings (scanner = trivy/osv): give a concrete reason citing the affected symbol
or package version. "CVE affects X.Y.Z which is [used/not used/partially used] here."

FINDING:
{finding_json}

Output ONLY this JSON (no prose, no fences):
{{"id": "{finding_id}", "verdict": "confirmed|false_positive|needs_manual",
  "cvss_score_refined": <float or null>, "remediation": "<concrete fix, 2-3 sentences>",
  "exploitability": "high|medium|low|none",
  "reason": "<mandatory 1-2 sentences citing the evidence and file context>"}}"""


def _build_triage_batch(findings: list[Finding]) -> str:
    """Build minimal JSON for Haiku triage (includes file_context for FP guidance)."""
    batch = []
    for f in findings:
        ctx = classify_context(f.file_path)
        batch.append({
            "id": f.id,
            "scanner": f.scanner,
            "rule_id": f.rule_id,
            "severity": f.severity.value,
            "file": f.file_path,
            "line": f.line_start,
            "evidence": f.evidence[:200],  # Token budget: cap evidence
            "cwe": f.cwe,
            "file_context": ctx.category,   # deterministic label fed to LLM
            "context_rationale": ctx.rationale,  # one-line why
        })
    return json.dumps(batch, indent=None)


_JSON_OBJ_RE = re.compile(r'\{[^{}]*\}', re.DOTALL)


# Distinctive placeholder tokens. None of these ever appears inside a real
# high-entropy credential, so matching one is a high-precision FP signal that
# cannot drop a real secret (preserves the zero-false-negative guarantee).
_PLACEHOLDER_MARKERS: tuple[str, ...] = (
    "your-api-key", "your_api_key", "yourapikey", "your-api-token", "your-token",
    "your_token", "your-secret", "your_secret", "your-key", "your_key", "your-password",
    "your-password-here", "api-key-here", "api_key_here", "-key-here", "_key_here",
    "key-goes-here", "token-goes-here", "goes-here", "...your", "enter-your",
    "insert-your", "insert_your", "replace-with", "replace_with", "replace-this",
    "<your", "<api", "<api-key", "<secret", "<token", "<key", "<insert", "<enter",
    "<password", "<username", "<client", "example", "sample-key", "placeholder",
    "changeme", "change-me", "change_me", "xxxxxxxx", "redacted", "dummy",
    "fake-key", "fakekey", "test-key", "test_key", "sk-test-123", "sk_test_123",
    "my-secret-key", "supersecret", "notarealkey", "not-a-real",
)


def _placeholder_marker(finding: "Finding") -> str | None:
    """Return the matched placeholder token if this SECRETS finding's value is an
    obvious doc/example placeholder, else None. Scoped to secrets findings only —
    placeholder values are a secrets-FP pattern, not a SAST/SCA one.
    """
    is_secret = finding.scanner in ("gitleaks", "trufflehog") or (
        finding.owasp_category is not None
        and "SECRET" in str(getattr(finding.owasp_category, "value", finding.owasp_category)).upper()
    )
    if not is_secret:
        return None
    hay = (finding.evidence or "").lower()
    for marker in _PLACEHOLDER_MARKERS:
        if marker in hay:
            return marker
    return None


async def verify_findings(
    findings: list[Finding],
    max_budget_usd: float = 2.0,
) -> tuple[list[Finding], list[str]]:
    """Two-pass verification. Returns (updated_findings, exploitation_candidate_ids).

    Pass 0: Deterministic context pre-triage (no LLM).
            Files classified as test/documentation/example with fp_prior >= 0.85
            are short-circuited to false_positive before any LLM call.
    Pass 1: Haiku — batch FP triage (20 findings/call) with context hints.
    Pass 2: Sonnet — deep confirm for HIGH/CRITICAL confirmed.
    Fallback: if LLM unavailable → deterministic heuristics only.
    """
    if not findings:
        return [], []

    from .context import (
        CATEGORY_BUILD, CATEGORY_DOCUMENTATION, CATEGORY_EXAMPLE, CATEGORY_TEST,
    )
    _DETERMINISTIC_FP_THRESHOLD = 0.85  # fp_prior >= this → auto-FP without LLM

    # Pass 0: deterministic context pre-triage
    # Categories with fp_prior >= 0.85 are short-circuited to false_positive.
    # This currently includes: test (0.90), documentation (0.92), example (0.88), build (0.88).
    # config_local (0.35) and source (0.10) always proceed to LLM for a proper verdict.
    pending_llm: list[Finding] = []
    for f in findings:
        if f.verification_status != VerificationStatus.UNVERIFIED:
            pending_llm.append(f)
            continue

        # Placeholder-secret pre-kill: a secret whose value is an obvious doc/example
        # placeholder ('your-api-key-here', '<token>', 'sk-test-123') is a false
        # positive regardless of file type — these markers never occur in a real
        # high-entropy credential, so this cannot drop a real secret. This is the
        # precision fix for the curl-example noise that recall-guard otherwise keeps.
        ph = _placeholder_marker(f)
        if ph:
            f.verification_status = VerificationStatus.FALSE_POSITIVE
            f.confidence = 0.05
            f.verification_reason = (
                f"[deterministic] secret value matches placeholder pattern '{ph}' — "
                f"documentation/example, not a real credential"
            )
            continue

        ctx = classify_context(f.file_path)
        if (
            ctx.category in (CATEGORY_TEST, CATEGORY_DOCUMENTATION, CATEGORY_EXAMPLE, CATEGORY_BUILD)
            and ctx.fp_prior >= _DETERMINISTIC_FP_THRESHOLD
        ):
            f.verification_status = VerificationStatus.FALSE_POSITIVE
            f.confidence = 0.05
            f.verification_reason = (
                f"[deterministic] {ctx.rationale} "
                f"(fp_prior={ctx.fp_prior:.0%}; category={ctx.category})"
            )
            log.debug(
                "deterministic pre-triage: %s → false_positive (%s)",
                f.id, ctx.rationale,
            )
        else:
            pending_llm.append(f)

    pre_triage_fp_count = len(findings) - len(pending_llm)
    if pre_triage_fp_count:
        log.info(
            "context pre-triage: %d/%d findings auto-marked false_positive",
            pre_triage_fp_count, len(findings),
        )

    spent_usd = 0.0
    haiku_available = True

    # Pass 1: Haiku triage in batches of 20 (only pending_llm findings)
    batch_size = 20
    batches = [pending_llm[i:i + batch_size] for i in range(0, len(pending_llm), batch_size)]

    for batch in batches:
        # Check budget
        if spent_usd >= max_budget_usd * 0.9:
            log.warning("Budget %.2f nearly exhausted — marking remaining as needs_manual", max_budget_usd)
            for f in batch:
                if f.verification_status == VerificationStatus.UNVERIFIED:
                    f.verification_status = VerificationStatus.NEEDS_MANUAL
            continue

        if haiku_available:
            prompt = _HAIKU_TRIAGE_PROMPT.format(
                findings_json=_build_triage_batch(batch)
            )
            result_text, cost = await _call_llm(prompt, model=_HAIKU_MODEL, timeout=_HAIKU_VERIFY_TIMEOUT)

            if result_text is None:
                haiku_available = False  # Degrade to deterministic
            else:
                if cost:
                    spent_usd += cost
                _apply_haiku_verdicts(batch, result_text)
                continue

        # Haiku unavailable — deterministic fallback
        _deterministic_triage(batch)

    # Pass 2: Sonnet deep confirm — only HIGH/CRITICAL confirmed findings
    sonnet_candidates = [
        f for f in findings
        if f.verification_status == VerificationStatus.CONFIRMED
        and f.severity in (Severity.HIGH, Severity.CRITICAL)
        and spent_usd < max_budget_usd
    ]

    for f in sonnet_candidates:
        if spent_usd >= max_budget_usd:
            f.verification_status = VerificationStatus.NEEDS_MANUAL
            continue

        prompt = _SONNET_DEEP_PROMPT.format(
            finding_json=f.model_dump_json(indent=None),
            finding_id=f.id,
        )
        result_text, cost = await _call_llm(prompt, model=None, timeout=_SONNET_VERIFY_TIMEOUT)
        if result_text and cost:
            spent_usd += cost
        if result_text:
            _apply_sonnet_verdict(f, result_text)

    # Identify exploitation candidates (confirmed HIGH/CRIT)
    exploitation_ids = [
        f.id for f in findings
        if f.verification_status == VerificationStatus.CONFIRMED
        and f.severity in (Severity.HIGH, Severity.CRITICAL)
    ]

    return findings, exploitation_ids


def _llm_may_kill(f: Finding) -> bool:
    """Recall-safety guard (enforces Boss's zero-false-negatives rule).

    The LLM may downgrade a finding to false_positive ONLY when the deterministic
    file-context is already FP-prone (test / documentation / example / build).
    For real `source` (and gitignored `config_local`) code, an LLM 'false_positive'
    is clamped to needs_manual instead — we never auto-kill a finding in real code
    on the model's word alone. Missing a real bug = missing money. A human reviews
    needs_manual; nothing real is silently dropped.
    (Note: test/doc/example/build are already pre-killed deterministically before
    the LLM runs, so in practice this makes the LLM's kill power source-safe.)
    """
    return classify_context(f.file_path).category in (
        "test", "documentation", "example", "build",
    )


def _apply_haiku_verdicts(batch: list[Finding], raw_text: str) -> None:
    """Parse Haiku JSONL output and update finding verification statuses."""
    finding_map = {f.id: f for f in batch}
    matched = 0

    for match in _JSON_OBJ_RE.finditer(raw_text):
        try:
            obj = json.loads(match.group(0))
            fid = obj.get("id", "")
            verdict_str = str(obj.get("verdict", "")).lower()
            if fid not in finding_map:
                continue

            f = finding_map[fid]
            # Store the LLM's reason (new field; old prompts used "rationale")
            reason = obj.get("reason") or obj.get("rationale") or None
            if reason:
                f.verification_reason = f"[haiku] {str(reason)[:300]}"

            if verdict_str == "confirmed":
                f.verification_status = VerificationStatus.CONFIRMED
                f.confidence = max(f.confidence, 0.7)
            elif verdict_str == "false_positive" and _llm_may_kill(f):
                f.verification_status = VerificationStatus.FALSE_POSITIVE
                f.confidence = 0.1
            elif verdict_str == "false_positive":
                # Recall guard: LLM wants to kill a real-source finding — don't.
                f.verification_status = VerificationStatus.NEEDS_MANUAL
                f.confidence = 0.4
                f.verification_reason = (
                    f"[haiku→recall-guard] LLM judged FP but file is real source; "
                    f"kept as needs_manual. " + (f.verification_reason or "")
                )[:300]
            else:
                f.verification_status = VerificationStatus.NEEDS_MANUAL
                f.confidence = 0.4
            matched += 1
        except (json.JSONDecodeError, KeyError):
            continue

    # Any findings not matched → needs_manual
    for f in batch:
        if f.verification_status == VerificationStatus.UNVERIFIED:
            f.verification_status = VerificationStatus.NEEDS_MANUAL


def _apply_sonnet_verdict(f: Finding, raw_text: str) -> None:
    """Parse Sonnet deep-verify output and update finding."""
    match = _JSON_OBJ_RE.search(raw_text)
    if not match:
        return
    try:
        obj = json.loads(match.group(0))
        verdict_str = str(obj.get("verdict", "")).lower()
        if verdict_str == "false_positive" and _llm_may_kill(f):
            f.verification_status = VerificationStatus.FALSE_POSITIVE
            f.confidence = 0.1
        elif verdict_str == "false_positive":
            # Recall guard: never auto-kill a real-source finding on the LLM's word.
            f.verification_status = VerificationStatus.NEEDS_MANUAL
            f.confidence = 0.4
        elif verdict_str == "confirmed":
            f.verification_status = VerificationStatus.CONFIRMED
            f.confidence = max(f.confidence, 0.85)
        else:
            f.verification_status = VerificationStatus.NEEDS_MANUAL

        # Store reason from Sonnet (new field; falls back to "rationale" for compat)
        reason = obj.get("reason") or obj.get("rationale") or None
        if reason:
            f.verification_reason = f"[sonnet] {str(reason)[:500]}"

        # Update remediation and refined score
        remediation = obj.get("remediation")
        if remediation:
            f.remediation = str(remediation)

        refined = obj.get("cvss_score_refined")
        if refined and isinstance(refined, (int, float)):
            f.cvss_score = float(refined)
    except (json.JSONDecodeError, KeyError, TypeError):
        pass


def _deterministic_triage(batch: list[Finding]) -> None:
    """LLM-unavailable fallback: use multi-scanner agreement + severity heuristics."""
    for f in batch:
        if f.verification_status != VerificationStatus.UNVERIFIED:
            continue
        if len(f.scanners_agreeing) >= 2:
            f.verification_status = VerificationStatus.CONFIRMED
            f.confidence = min(f.confidence + 0.15, 0.75)
            f.verification_reason = (
                f"[deterministic-fallback] Multi-scanner agreement: {f.scanners_agreeing}"
            )
        elif f.severity == Severity.CRITICAL:
            f.verification_status = VerificationStatus.NEEDS_MANUAL
            f.confidence = 0.6
            f.verification_reason = (
                "[deterministic-fallback] Single scanner, CRITICAL severity — manual review required"
            )
        else:
            f.verification_status = VerificationStatus.NEEDS_MANUAL
            f.confidence = 0.4
            f.verification_reason = (
                "[deterministic-fallback] Single scanner, no corroboration — manual review required"
            )


async def _call_llm(prompt: str, model: str | None, timeout: int) -> tuple[str | None, float | None]:
    """Call the LLM via run_worker (same mechanism as critic.py).

    Returns (text, cost_usd). Returns (None, None) on any failure.
    """
    try:
        from ..orchestrator import run_worker
        outcome = await asyncio.wait_for(
            run_worker(
                prompt,
                project_root=PROJECT_ROOT,
                # 2 turns: a large triage batch can make the model emit its JSON
                # across a tool-less reasoning step + final answer; max_turns=1
                # raised "Reached maximum number of turns" and silently degraded the
                # moat to deterministic on big targets. 2 gives headroom; still cheap.
                max_turns=2,
                allowed_tools=[],
                timeout_seconds=timeout,
                model=model,
            ),
            timeout=timeout + 5,
        )
        if outcome.error and not outcome.text:
            log.warning("LLM call failed: %s", outcome.error)
            return None, None
        return outcome.text, outcome.cost_usd
    except asyncio.TimeoutError:
        log.warning("LLM call timed out after %ds", timeout)
        return None, None
    except Exception as exc:
        log.warning("LLM call error: %s", exc)
        return None, None


# ── Report generation ──────────────────────────────────────────────────────────


async def generate_report(run: AuditRun) -> AuditReport:
    """Build AuditReport from finalized findings."""
    findings = run.findings

    # Count by severity
    by_sev: dict[str, int] = {s.value: 0 for s in Severity}
    for f in findings:
        if f.verification_status != VerificationStatus.FALSE_POSITIVE:
            by_sev[f.severity.value] = by_sev.get(f.severity.value, 0) + 1

    # CVSS distribution
    cvss_dist: dict[str, int] = {"9-10": 0, "7-9": 0, "4-7": 0, "0-4": 0}
    for f in findings:
        if f.cvss_score is not None and f.verification_status != VerificationStatus.FALSE_POSITIVE:
            s = f.cvss_score
            if s >= 9.0:
                cvss_dist["9-10"] += 1
            elif s >= 7.0:
                cvss_dist["7-9"] += 1
            elif s >= 4.0:
                cvss_dist["4-7"] += 1
            else:
                cvss_dist["0-4"] += 1

    # Top 10 by CVSS score (confirmed / needs_manual only)
    actionable = [
        f for f in findings
        if f.verification_status != VerificationStatus.FALSE_POSITIVE
    ]
    top_findings = sorted(
        actionable,
        key=lambda f: (f.cvss_score or 0.0, _SEV_RANK.get(f.severity, 0)),
        reverse=True,
    )[:10]

    # Markdown report
    md = _build_markdown(run, findings, top_findings, by_sev)

    return AuditReport(
        audit_id=run.audit_id,
        target_uri=run.scope_policy.target.uri,
        total_findings=len(actionable),
        by_severity=by_sev,
        top_findings=top_findings,
        markdown_body=md,
        json_findings=actionable,
        cvss_distribution=cvss_dist,
    )


def _build_markdown(
    run: AuditRun,
    findings: list[Finding],
    top: list[Finding],
    by_sev: dict[str, int],
) -> str:
    lines = [
        f"# Security Audit Report",
        f"",
        f"**Audit ID:** `{run.audit_id}`  ",
        f"**Target:** `{run.scope_policy.target.uri}`  ",
        f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}  ",
        f"**Scanners:** {', '.join(run.scope_policy.allowed_scanners)}",
        f"",
        f"## Summary",
        f"",
        f"| Severity | Count |",
        f"|---|---|",
    ]
    for sev in ("critical", "high", "medium", "low", "info"):
        lines.append(f"| {sev.capitalize()} | {by_sev.get(sev, 0)} |")

    lines += [
        f"",
        f"## Top Findings",
        f"",
    ]
    for i, f in enumerate(top, 1):
        lines.append(f"### {i}. [{f.severity.value.upper()}] {f.rule_id}")
        lines.append(f"")
        if f.file_path:
            loc = f"`{f.file_path}`"
            if f.line_start:
                loc += f" line {f.line_start}"
            lines.append(f"**Location:** {loc}  ")
        if f.cvss_score is not None:
            lines.append(f"**CVSS 4.0:** {f.cvss_score:.1f}  ")
        if f.cwe:
            lines.append(f"**CWE:** {f.cwe}  ")
        if f.owasp_category:
            lines.append(f"**OWASP:** {f.owasp_category.value}  ")
        lines.append(f"**Status:** {f.verification_status.value}  ")
        lines.append(f"**Confidence:** {f.confidence:.0%}  ")
        lines.append(f"")
        lines.append(f"**Evidence:**")
        lines.append(f"```")
        lines.append(f.evidence[:400])
        lines.append(f"```")
        if f.remediation:
            lines.append(f"")
            lines.append(f"**Remediation:** {f.remediation}")
        lines.append(f"")

    lines += [
        f"---",
        f"",
        f"*Generated by AuditAgent (Jarvis). Defensive-only. "
        f"Authorized targets only. This report may contain false positives; "
        f"confirm findings manually before acting.*",
    ]
    return "\n".join(lines)
