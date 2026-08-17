"""
TruffleHogAdapter — secrets scanner with live credential verification.

Command: trufflehog filesystem <path> --json --no-update
Output is JSONL (one JSON object per line, not a JSON array).

Secrets are MASKED in evidence (first 4 + last 4 chars only).
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path

from ..models import Finding, RawScanResult, Severity, OWASPCategory, _mask_secret
from ..normalizers.cvss import score_vector
from .base import ToolAdapter, ToolInput, ToolTimeoutError, ToolError, _run_subprocess

log = logging.getLogger("jarvis_core.audit_agent.tools.trufflehog")

# Newline-separated path regexes to skip (node_modules etc.) — without this,
# trufflehog walks dependency dirs and times out on JS/TS projects.
_TRUFFLEHOG_EXCLUDE = str(
    Path(__file__).resolve().parent.parent / "configs" / "trufflehog-exclude.txt"
)

_SECRETS_CVSS_VECTOR = "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N"


class TruffleHogAdapter(ToolAdapter):
    name = "trufflehog"
    scanner_type = "secrets"

    async def run(self, inp: ToolInput) -> RawScanResult:
        started = time.perf_counter()
        cmd = [
            "trufflehog",
            "filesystem",
            inp.target_path,
            "--json",
            "--no-update",
            "--exclude-paths", _TRUFFLEHOG_EXCLUDE,
            *inp.extra_args,
        ]
        try:
            rc, stdout, stderr = await _run_subprocess(
                cmd,
                timeout_seconds=inp.timeout_seconds,
                env_overrides=inp.env_overrides,
            )
        except FileNotFoundError:
            log.info("trufflehog binary not found — skipping")
            return self._make_error_result("not_installed")
        except ToolTimeoutError as exc:
            log.warning("trufflehog timeout: %s", exc)
            return self._make_error_result(f"timeout:{exc}")
        except ToolError as exc:
            log.warning("trufflehog error: %s", exc)
            return self._make_error_result(f"tool_error:{exc}")

        duration_ms = int((time.perf_counter() - started) * 1000)
        # trufflehog exits 0 if secrets found (with --json), non-zero on error
        if rc != 0:
            log.warning("trufflehog exit_code=%d stderr=%r", rc, stderr[:300])

        return RawScanResult(
            scanner=self.name,
            exit_code=rc,
            stdout=stdout,
            stderr=stderr,
            duration_ms=duration_ms,
        )

    def normalize(self, raw: RawScanResult) -> list[Finding]:
        """Parse JSONL output — one JSON object per line."""
        findings: list[Finding] = []
        if not raw.stdout or not raw.stdout.strip():
            return []

        for line in raw.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            try:
                detector = obj.get("DetectorName", "") or obj.get("detectorName", "unknown")
                raw_secret = obj.get("Raw", "") or obj.get("raw", "")
                masked = _mask_secret(raw_secret)

                # File location from SourceMetadata
                src = obj.get("SourceMetadata", {}) or {}
                data = src.get("Data", {}) or {}
                fs_data = (
                    data.get("Filesystem", {})
                    or data.get("Git", {})
                    or data.get("Github", {})
                    or {}
                )
                file_path = fs_data.get("file") or fs_data.get("File", "")
                line_no = fs_data.get("line") or fs_data.get("Line")
                commit = fs_data.get("commit") or fs_data.get("Commit", "")

                verified = obj.get("Verified", False)
                # Verified secrets are higher confidence → confirmed after detect
                severity = Severity.CRITICAL if verified else Severity.HIGH
                cvss_score = score_vector(_SECRETS_CVSS_VECTOR)

                evidence_parts = [f"Detector: {detector}", f"Secret: {masked}"]
                if commit:
                    evidence_parts.append(f"Commit: {commit[:12]}")
                if verified:
                    evidence_parts.append("(VERIFIED LIVE)")

                findings.append(Finding(
                    scanner=self.name,
                    rule_id=f"trufflehog.{detector.lower().replace(' ', '_')}",
                    cwe="CWE-798",
                    owasp_category=OWASPCategory.SECRETS,
                    cvss_vector=_SECRETS_CVSS_VECTOR,
                    cvss_score=cvss_score,
                    severity=severity,
                    file_path=file_path or None,
                    line_start=int(line_no) if line_no else None,
                    evidence=" | ".join(evidence_parts),
                ))
            except Exception as exc:
                log.debug("trufflehog normalize skipped: %s", exc)

        log.info("trufflehog normalized %d findings", len(findings))
        return findings
