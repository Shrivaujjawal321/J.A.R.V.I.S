"""
SemgrepAdapter — SAST scanner.

Command: semgrep --config=auto --json <target_path>
Exit code 1 means findings found (not an error).
Exit code 2+ means scanner error.

Note: semgrep>=1.70.0 is installed in this venv.
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path

from ..models import Finding, RawScanResult, Severity, OWASPCategory
from ..normalizers.cvss import cwe_to_owasp, cwe_to_cvss_vector, score_vector
from ..models import _mask_secret
from .base import ToolAdapter, ToolInput, ToolTimeoutError, ToolError, _run_subprocess

log = logging.getLogger("jarvis_core.audit_agent.tools.semgrep")

# Jarvis's custom high-value rule packs (SSRF, SQLi/cmd-injection taint,
# path-traversal, deserialization, SSTI, authz, MCP/agent-security). Run ALONGSIDE
# p/default so we add high-signal bounty-class detection on top of the broad pack.
_CUSTOM_RULES_DIR = Path(__file__).resolve().parent.parent / "configs" / "rules"

_SEVERITY_MAP: dict[str, Severity] = {
    "ERROR":   Severity.HIGH,
    "WARNING": Severity.MEDIUM,
    "INFO":    Severity.LOW,
    "CRITICAL": Severity.CRITICAL,
    "HIGH":    Severity.HIGH,
    "MEDIUM":  Severity.MEDIUM,
    "LOW":     Severity.LOW,
}


def _extract_cwe(metadata: dict) -> str | None:
    """Pull CWE from semgrep metadata dict (multiple possible field names)."""
    for key in ("cwe", "cwe2022-top25", "cwe2021-top25", "CWE"):
        val = metadata.get(key)
        if val:
            if isinstance(val, list):
                val = val[0]
            s = str(val).strip()
            if s.upper().startswith("CWE-"):
                return s.upper()
            if s.isdigit():
                return f"CWE-{s}"
    return None


class SemgrepAdapter(ToolAdapter):
    name = "semgrep"
    scanner_type = "sast"
    # SAST rule-pack download + analysis is slower than the secrets/SCA scanners.
    # First run downloads the registry pack into ~/.semgrep (cached after).
    default_timeout = 300

    async def run(self, inp: ToolInput) -> RawScanResult:
        started = time.perf_counter()
        # p/default: broad security + correctness pack. Measured to catch the real
        # vulns (formatted-SQL, raw-query-exec, hardcoded creds) that the narrower
        # p/security-audit pack MISSED on our planted-vuln target — so it stays.
        # The real speed fix is the --exclude list: stripping build/vendor/minified
        # dirs took litellm/proxy from a 300s timeout down to ~2min, and removes the
        # #1 false-positive source (minified JS chunks tripping rules). Verify layer
        # kills whatever FPs remain.
        cmd = [
            "semgrep",
            "--config=p/default",
            f"--config={_CUSTOM_RULES_DIR}",
            "--json",
            "--no-rewrite-rule-ids",
            "--quiet",
            "--metrics=off",
            "--exclude=*.min.js",
            "--exclude=*.bundle.js",
            "--exclude=node_modules",
            "--exclude=dist",
            "--exclude=build",
            "--exclude=.next",
            "--exclude=out",
            "--exclude=_experimental",
            "--exclude=vendor",
            "--exclude=.venv",
            "--exclude=tests",
            "--exclude=test",
            inp.target_path,
            *inp.extra_args,
        ]
        try:
            rc, stdout, stderr = await _run_subprocess(
                cmd,
                timeout_seconds=inp.timeout_seconds,
                env_overrides=inp.env_overrides,
                cwd=inp.target_path,
            )
        except FileNotFoundError:
            log.info("semgrep binary not found — skipping")
            return self._make_error_result("not_installed")
        except ToolTimeoutError as exc:
            log.warning("semgrep timeout: %s", exc)
            return self._make_error_result(f"timeout:{exc}")
        except ToolError as exc:
            log.warning("semgrep error: %s", exc)
            return self._make_error_result(f"tool_error:{exc}")

        duration_ms = int((time.perf_counter() - started) * 1000)
        # Exit code 1 = findings found, that's normal for semgrep
        if rc >= 2:
            log.warning("semgrep exit_code=%d stderr=%r", rc, stderr[:300])

        return RawScanResult(
            scanner=self.name,
            exit_code=rc,
            stdout=stdout,
            stderr=stderr,
            duration_ms=duration_ms,
        )

    def normalize(self, raw: RawScanResult) -> list[Finding]:
        findings: list[Finding] = []
        try:
            data = json.loads(raw.stdout or "{}")
        except json.JSONDecodeError as exc:
            log.warning("semgrep JSON parse failed: %s", exc)
            return []

        for r in data.get("results", []):
            try:
                meta = r.get("extra", {}).get("metadata", {})
                cwe = _extract_cwe(meta)
                sev_raw = r.get("extra", {}).get("severity", "WARNING").upper()
                severity = _SEVERITY_MAP.get(sev_raw, Severity.MEDIUM)

                cvss_vec = cwe_to_cvss_vector(cwe) if cwe else None
                cvss_score = score_vector(cvss_vec) if cvss_vec else None
                owasp = cwe_to_owasp(cwe) if cwe else OWASPCategory.UNKNOWN

                findings.append(Finding(
                    scanner=self.name,
                    rule_id=r.get("check_id", "unknown"),
                    cwe=cwe,
                    owasp_category=owasp,
                    cvss_vector=cvss_vec,
                    cvss_score=cvss_score,
                    severity=severity,
                    file_path=r.get("path"),
                    line_start=r.get("start", {}).get("line"),
                    line_end=r.get("end", {}).get("line"),
                    evidence=r.get("extra", {}).get("message", r.get("check_id", "")),
                ))
            except Exception as exc:
                log.debug("semgrep normalize skipped result: %s", exc)

        log.info("semgrep normalized %d findings", len(findings))
        return findings
