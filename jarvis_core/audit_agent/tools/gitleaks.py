"""
GitleaksAdapter — secrets scanner.

Command: gitleaks detect --source=<path> --report-format json
         --report-path /dev/stdout --exit-code 0 --no-banner

Secrets are MASKED in evidence (first 4 + last 4 chars only).
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path

from ..models import Finding, RawScanResult, Severity, OWASPCategory, _mask_secret
from ..normalizers.cvss import cwe_to_cvss_vector, score_vector
from .base import ToolAdapter, ToolInput, ToolTimeoutError, ToolError, _run_subprocess

log = logging.getLogger("jarvis_core.audit_agent.tools.gitleaks")

# Config extends gitleaks' default rules + allowlists build/vendor dirs so the
# scanner skips node_modules etc. (otherwise it times out on JS/TS projects).
_GITLEAKS_CONFIG = str(
    Path(__file__).resolve().parent.parent / "configs" / "gitleaks-jarvis.toml"
)

_SECRETS_CVSS_VECTOR = "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N"


class GitleaksAdapter(ToolAdapter):
    name = "gitleaks"
    scanner_type = "secrets"

    async def run(self, inp: ToolInput) -> RawScanResult:
        started = time.perf_counter()
        # --no-git: scan files directly, do NOT walk git history. Without it,
        # gitleaks discovers a parent .git (the host repo) and scans its entire
        # history → multi-minute timeout on a 3-file target dir.
        cmd = [
            "gitleaks", "detect",
            f"--source={inp.target_path}",
            "--no-git",
            "--config", _GITLEAKS_CONFIG,
            "--report-format", "json",
            "--report-path", "/dev/stdout",
            "--exit-code", "0",
            "--no-banner",
            *inp.extra_args,
        ]
        try:
            rc, stdout, stderr = await _run_subprocess(
                cmd,
                timeout_seconds=inp.timeout_seconds,
                env_overrides=inp.env_overrides,
            )
        except FileNotFoundError:
            log.info("gitleaks binary not found — skipping")
            return self._make_error_result("not_installed")
        except ToolTimeoutError as exc:
            log.warning("gitleaks timeout: %s", exc)
            return self._make_error_result(f"timeout:{exc}")
        except ToolError as exc:
            log.warning("gitleaks error: %s", exc)
            return self._make_error_result(f"tool_error:{exc}")

        duration_ms = int((time.perf_counter() - started) * 1000)
        return RawScanResult(
            scanner=self.name,
            exit_code=rc,
            stdout=stdout,
            stderr=stderr,
            duration_ms=duration_ms,
        )

    def normalize(self, raw: RawScanResult) -> list[Finding]:
        findings: list[Finding] = []
        if not raw.stdout or not raw.stdout.strip() or raw.stdout.strip() in ("null", "[]"):
            return []
        try:
            data = json.loads(raw.stdout)
            if not isinstance(data, list):
                return []
        except json.JSONDecodeError as exc:
            log.warning("gitleaks JSON parse failed: %s", exc)
            return []

        for leak in data:
            try:
                secret_raw = leak.get("Secret", "") or leak.get("secret", "")
                masked = _mask_secret(secret_raw)
                rule_id = leak.get("RuleID", "") or leak.get("ruleID", "gitleaks.secret")
                file_path = leak.get("File", "") or leak.get("file", "")
                line = leak.get("StartLine") or leak.get("startLine")
                match_val = leak.get("Match", "") or leak.get("match", "")

                cvss_score = score_vector(_SECRETS_CVSS_VECTOR)

                findings.append(Finding(
                    scanner=self.name,
                    rule_id=f"gitleaks.{rule_id}",
                    cwe="CWE-798",
                    owasp_category=OWASPCategory.SECRETS,
                    cvss_vector=_SECRETS_CVSS_VECTOR,
                    cvss_score=cvss_score,
                    severity=Severity.CRITICAL,
                    file_path=file_path,
                    line_start=int(line) if line else None,
                    evidence=(
                        f"Secret detected by rule '{rule_id}': "
                        f"{masked} (match: {match_val[:60] if match_val else '?'})"
                    ),
                ))
            except Exception as exc:
                log.debug("gitleaks normalize skipped leak: %s", exc)

        log.info("gitleaks normalized %d findings", len(findings))
        return findings
