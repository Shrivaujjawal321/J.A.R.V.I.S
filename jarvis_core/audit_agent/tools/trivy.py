"""
TrivyAdapter — SCA + container scanner.

Command: trivy fs --format json --exit-code 0 <target_path>
--exit-code 0 ensures trivy exits 0 even when findings are present,
so we can distinguish "scan ran" from "scan failed".
"""
from __future__ import annotations

import json
import logging
import time

from ..models import Finding, RawScanResult, Severity, OWASPCategory
from ..normalizers.cvss import cwe_to_owasp, cve_severity_to_cvss_vector, score_vector
from .base import ToolAdapter, ToolInput, ToolTimeoutError, ToolError, _run_subprocess

log = logging.getLogger("jarvis_core.audit_agent.tools.trivy")

_SEVERITY_MAP: dict[str, Severity] = {
    "CRITICAL": Severity.CRITICAL,
    "HIGH":     Severity.HIGH,
    "MEDIUM":   Severity.MEDIUM,
    "LOW":      Severity.LOW,
    "UNKNOWN":  Severity.INFO,
}


class TrivyAdapter(ToolAdapter):
    name = "trivy"
    scanner_type = "sca"

    async def run(self, inp: ToolInput) -> RawScanResult:
        started = time.perf_counter()
        cmd = [
            "trivy", "fs",
            "--format", "json",
            "--exit-code", "0",
            "--quiet",
            inp.target_path,
            *inp.extra_args,
        ]
        try:
            rc, stdout, stderr = await _run_subprocess(
                cmd,
                timeout_seconds=inp.timeout_seconds,
                env_overrides=inp.env_overrides,
            )
        except FileNotFoundError:
            log.info("trivy binary not found — skipping")
            return self._make_error_result("not_installed")
        except ToolTimeoutError as exc:
            log.warning("trivy timeout: %s", exc)
            return self._make_error_result(f"timeout:{exc}")
        except ToolError as exc:
            log.warning("trivy error: %s", exc)
            return self._make_error_result(f"tool_error:{exc}")

        duration_ms = int((time.perf_counter() - started) * 1000)
        if rc != 0:
            log.warning("trivy exit_code=%d stderr=%r", rc, stderr[:300])

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
            log.warning("trivy JSON parse failed: %s", exc)
            return []

        for result in data.get("Results", []):
            target = result.get("Target", "")
            for vuln in result.get("Vulnerabilities") or []:
                try:
                    sev_raw = vuln.get("Severity", "UNKNOWN").upper()
                    severity = _SEVERITY_MAP.get(sev_raw, Severity.INFO)
                    cve_id = vuln.get("VulnerabilityID", "UNKNOWN")
                    pkg = vuln.get("PkgName", "unknown")
                    installed = vuln.get("InstalledVersion", "?")
                    fixed = vuln.get("FixedVersion", "none")
                    title = vuln.get("Title", "") or vuln.get("Description", "")[:120]

                    cvss_vec = cve_severity_to_cvss_vector(sev_raw)
                    cvss_score = score_vector(cvss_vec) if cvss_vec else None

                    findings.append(Finding(
                        scanner=self.name,
                        rule_id=cve_id,
                        owasp_category=OWASPCategory.SCA_CVE,
                        cvss_vector=cvss_vec,
                        cvss_score=cvss_score,
                        severity=severity,
                        file_path=target,
                        evidence=(
                            f"{cve_id} in {pkg}@{installed} "
                            f"(fix: {fixed}): {title}"
                        ),
                    ))
                except Exception as exc:
                    log.debug("trivy normalize skipped vuln: %s", exc)

        log.info("trivy normalized %d findings", len(findings))
        return findings
