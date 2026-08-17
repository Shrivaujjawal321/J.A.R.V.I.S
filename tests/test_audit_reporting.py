"""
Tests for jarvis_core.audit_agent.reporting

Coverage:
  (a) VulnClass classification — CWE, scanner, rule-id pattern
  (b) build_bug_report — SQLi, hardcoded-secret, SCA-CVE, SSRF, path-traversal,
      XSS, deserialization, JWT, generic
  (c) render_markdown — required sections present, proper formatting
  (d) Secret masking — no raw long tokens in PoC text
  (e) write_reports — file creation, filtering (HIGH+CRIT non-FP), index.md
  (f) Edge cases — missing CVSS, missing file_path, very long evidence, unicode

All tests run WITHOUT scanner binaries and WITHOUT LLM calls (deterministic path).
"""
from __future__ import annotations

import asyncio
import json
import sys
import uuid
from pathlib import Path
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from jarvis_core.audit_agent.models import (
    AuditRun,
    AuditState,
    Finding,
    OWASPCategory,
    ScopePolicy,
    Severity,
    Target,
    VerificationStatus,
)
from jarvis_core.audit_agent.reporting import (
    BugReport,
    VulnClass,
    _classify_finding,
    _mask_evidence_secrets,
    _make_slug,
    build_bug_report,
    render_markdown,
    write_reports,
)


# ── Helpers ────────────────────────────────────────────────────────────────────


def _make_target(uri: str = "/tmp/test-repo") -> Target:
    return Target(kind="local_dir", uri=uri, verified_owner=True)


def _make_run(uri: str = "/tmp/test-repo") -> AuditRun:
    policy = ScopePolicy(target=_make_target(uri))
    run = AuditRun(user_id="test", scope_policy=policy)
    run.audit_state = AuditState.DONE
    return run


def _make_finding(
    scanner: str = "semgrep",
    rule_id: str = "python.sql.injection",
    cwe: str | None = "CWE-89",
    owasp: OWASPCategory | None = OWASPCategory.A05_INJECTION,
    severity: Severity = Severity.HIGH,
    file_path: str = "api/users.py",
    line_start: int = 42,
    evidence: str = "SQL injection via string concatenation: query = 'SELECT * FROM users WHERE id = ' + user_id",
    cvss_vector: str | None = None,
    cvss_score: float | None = None,
    verification_status: VerificationStatus = VerificationStatus.CONFIRMED,
    endpoint: str | None = None,
) -> Finding:
    f = Finding(
        scanner=scanner,
        rule_id=rule_id,
        cwe=cwe,
        owasp_category=owasp,
        severity=severity,
        file_path=file_path,
        line_start=line_start,
        evidence=evidence,
        cvss_vector=cvss_vector,
        cvss_score=cvss_score,
        verification_status=verification_status,
        endpoint=endpoint,
    )
    return f


# ═══════════════════════════════════════════════════════════════════════════════
# (a) VulnClass classification
# ═══════════════════════════════════════════════════════════════════════════════


class TestVulnClassClassification:
    """Classification is deterministic: CWE > scanner > rule_id > GENERIC."""

    def test_cwe_89_is_sqli(self):
        f = _make_finding(cwe="CWE-89")
        assert _classify_finding(f) == VulnClass.SQLI

    def test_cwe_79_is_xss(self):
        f = _make_finding(cwe="CWE-79", scanner="semgrep", rule_id="xss-sink")
        assert _classify_finding(f) == VulnClass.XSS

    def test_cwe_918_is_ssrf(self):
        f = _make_finding(cwe="CWE-918", scanner="semgrep", rule_id="ssrf-url-param")
        assert _classify_finding(f) == VulnClass.SSRF

    def test_cwe_22_is_path_traversal(self):
        f = _make_finding(cwe="CWE-22")
        assert _classify_finding(f) == VulnClass.PATH_TRAVERSAL

    def test_cwe_798_is_hardcoded_secret(self):
        f = _make_finding(cwe="CWE-798", scanner="semgrep", rule_id="hardcoded-api-key")
        assert _classify_finding(f) == VulnClass.HARDCODED_SECRET

    def test_cwe_502_is_deserialization(self):
        f = _make_finding(cwe="CWE-502")
        assert _classify_finding(f) == VulnClass.DESERIALIZATION

    def test_cwe_347_is_jwt(self):
        f = _make_finding(cwe="CWE-347")
        assert _classify_finding(f) == VulnClass.JWT

    def test_trivy_scanner_no_cwe_is_sca_cve(self):
        f = _make_finding(scanner="trivy", cwe=None, rule_id="CVE-2023-12345")
        assert _classify_finding(f) == VulnClass.SCA_CVE

    def test_osv_scanner_no_cwe_is_sca_cve(self):
        f = _make_finding(scanner="osv", cwe=None, rule_id="GHSA-xxxx-yyyy-zzzz")
        assert _classify_finding(f) == VulnClass.SCA_CVE

    def test_gitleaks_scanner_no_cwe_is_secret(self):
        f = _make_finding(scanner="gitleaks", cwe=None, rule_id="generic-api-key")
        assert _classify_finding(f) == VulnClass.HARDCODED_SECRET

    def test_trufflehog_scanner_no_cwe_is_secret(self):
        f = _make_finding(scanner="trufflehog", cwe=None, rule_id="aws-access-token")
        assert _classify_finding(f) == VulnClass.HARDCODED_SECRET

    def test_rule_id_sqli_pattern_fallback(self):
        f = _make_finding(cwe=None, scanner="semgrep", rule_id="python.sqli.string-concat")
        assert _classify_finding(f) == VulnClass.SQLI

    def test_rule_id_xss_pattern_fallback(self):
        f = _make_finding(cwe=None, scanner="semgrep", rule_id="js.xss.dangerouslySetInnerHTML")
        assert _classify_finding(f) == VulnClass.XSS

    def test_unknown_cwe_scanner_rule_fallback_to_generic(self):
        f = _make_finding(cwe="CWE-9999", scanner="semgrep", rule_id="unknown-rule-zzz")
        assert _classify_finding(f) == VulnClass.GENERIC

    def test_cwe_takes_priority_over_scanner(self):
        # CWE-89 → SQLi, even though scanner is trivy (which normally → SCA_CVE)
        f = _make_finding(cwe="CWE-89", scanner="trivy", rule_id="something")
        assert _classify_finding(f) == VulnClass.SQLI


# ═══════════════════════════════════════════════════════════════════════════════
# (b) build_bug_report — per vuln class
# ═══════════════════════════════════════════════════════════════════════════════


class TestBuildBugReport:
    """build_bug_report returns a valid BugReport for each vuln class."""

    def test_sqli_report_structure(self):
        run = _make_run()
        f = _make_finding(cwe="CWE-89", severity=Severity.HIGH)
        report = build_bug_report(f, run)

        assert isinstance(report, BugReport)
        assert report.vuln_class == VulnClass.SQLI
        assert report.finding_id == f.id
        assert report.audit_id == run.audit_id
        assert "SQL" in report.title
        assert len(report.reproduction_steps) >= 5
        assert len(report.proof_of_concept) > 50
        assert len(report.impact) > 20
        assert len(report.remediation_primary) > 20
        assert len(report.references) >= 3
        assert report.severity == "High"
        assert report.llm_enriched is False

    def test_hardcoded_secret_report_structure(self):
        run = _make_run()
        f = _make_finding(
            scanner="gitleaks",
            cwe="CWE-798",
            rule_id="generic-api-key",
            evidence="Rule: generic-api-key | File: config.py:15 | Match: sk-1234567890abcdef1234567890abcdef",
            severity=Severity.CRITICAL,
        )
        report = build_bug_report(f, run)

        assert report.vuln_class == VulnClass.HARDCODED_SECRET
        assert report.severity == "Critical"
        assert "credential" in report.summary.lower() or "secret" in report.summary.lower()
        assert len(report.reproduction_steps) >= 5

    def test_sca_cve_report_structure(self):
        run = _make_run()
        f = _make_finding(
            scanner="trivy",
            cwe=None,
            rule_id="CVE-2023-32681",
            evidence="requests==2.28.0 CVE-2023-32681 HIGH GHSA-j8r2-6x86-q33q",
            owasp=None,
            severity=Severity.HIGH,
        )
        report = build_bug_report(f, run)

        assert report.vuln_class == VulnClass.SCA_CVE
        assert "Dependency" in report.title or "dependency" in report.title.lower() or "Vulnerable" in report.title
        assert len(report.reproduction_steps) >= 4
        assert "requests" in report.proof_of_concept or "CVE" in report.proof_of_concept

    def test_ssrf_report_structure(self):
        run = _make_run()
        f = _make_finding(cwe="CWE-918", severity=Severity.HIGH, rule_id="ssrf-url-param")
        report = build_bug_report(f, run)

        assert report.vuln_class == VulnClass.SSRF
        assert "SSRF" in report.title or "Request Forgery" in report.title
        assert "OOB" in report.proof_of_concept or "interactsh" in report.proof_of_concept or "collab" in report.proof_of_concept.lower()

    def test_path_traversal_report_structure(self):
        run = _make_run()
        f = _make_finding(cwe="CWE-22", severity=Severity.HIGH, rule_id="path-traversal")
        report = build_bug_report(f, run)

        assert report.vuln_class == VulnClass.PATH_TRAVERSAL
        assert "Path Traversal" in report.title or "file" in report.title.lower()
        assert "hostname" in report.proof_of_concept  # benign file, not passwd

    def test_xss_report_structure(self):
        run = _make_run()
        f = _make_finding(cwe="CWE-79", severity=Severity.HIGH, rule_id="xss-sink")
        report = build_bug_report(f, run)

        assert report.vuln_class == VulnClass.XSS
        assert "XSS" in report.title or "Scripting" in report.title
        assert "alert(document.domain)" in report.proof_of_concept

    def test_deserialization_report_structure(self):
        run = _make_run()
        f = _make_finding(cwe="CWE-502", severity=Severity.CRITICAL, rule_id="unsafe-deserialization")
        report = build_bug_report(f, run)

        assert report.vuln_class == VulnClass.DESERIALIZATION
        assert "OOB" in report.proof_of_concept or "ysoserial" in report.proof_of_concept or "DNS" in report.proof_of_concept

    def test_jwt_report_structure(self):
        run = _make_run()
        f = _make_finding(cwe="CWE-347", severity=Severity.HIGH, rule_id="jwt-alg-none")
        report = build_bug_report(f, run)

        assert report.vuln_class == VulnClass.JWT
        assert "JWT" in report.title or "Token" in report.title
        assert "alg" in report.proof_of_concept.lower() and "none" in report.proof_of_concept.lower()

    def test_generic_fallback_report_structure(self):
        run = _make_run()
        f = _make_finding(cwe=None, scanner="semgrep", rule_id="some-unknown-security-rule")
        report = build_bug_report(f, run)

        assert report.vuln_class == VulnClass.GENERIC
        assert len(report.reproduction_steps) >= 4

    def test_cvss_score_populated_from_cwe_table(self):
        """CVSS score should be filled in via normalizer even when not set on finding."""
        run = _make_run()
        f = _make_finding(cwe="CWE-89", cvss_score=None, cvss_vector=None)
        report = build_bug_report(f, run)

        # normalizer should have provided these
        assert report.cvss_score is not None
        assert report.cvss_vector is not None
        assert 0 < report.cvss_score <= 10.0

    def test_affected_asset_with_file_and_line(self):
        run = _make_run()
        f = _make_finding(file_path="src/db.py", line_start=99)
        report = build_bug_report(f, run)
        assert "src/db.py:99" in report.affected_asset

    def test_affected_asset_fallback_to_endpoint(self):
        run = _make_run()
        f = _make_finding(file_path=None, line_start=None, endpoint="/api/v1/users")
        report = build_bug_report(f, run)
        assert report.affected_asset == "/api/v1/users"

    def test_affected_asset_fallback_to_rule_id(self):
        run = _make_run()
        f = _make_finding(file_path=None, line_start=None, endpoint=None, rule_id="my-rule-id")
        report = build_bug_report(f, run)
        assert report.affected_asset == "my-rule-id"

    def test_platform_hint_sca_is_huntr(self):
        run = _make_run()
        f = _make_finding(scanner="trivy", cwe=None, rule_id="CVE-2023-1234")
        report = build_bug_report(f, run)
        assert "huntr" in report.platform_hint.lower()

    def test_platform_hint_semgrep_is_hackerone(self):
        run = _make_run()
        f = _make_finding(scanner="semgrep", cwe="CWE-89")
        report = build_bug_report(f, run)
        assert "hackerone" in report.platform_hint.lower() or "bugcrowd" in report.platform_hint.lower()

    def test_slug_is_filename_safe(self):
        run = _make_run()
        f = _make_finding(cwe="CWE-89")
        report = build_bug_report(f, run)
        import re
        assert re.match(r"^[a-z0-9\-]+$", report.slug), f"Slug not filename-safe: {report.slug!r}"


# ═══════════════════════════════════════════════════════════════════════════════
# (c) render_markdown — required sections
# ═══════════════════════════════════════════════════════════════════════════════


_REQUIRED_SECTIONS = [
    "## TL;DR / Summary",
    "## Severity",
    "CVSS",
    "## Vulnerability Details",
    "## Affected Asset",
    "## Steps to Reproduce",
    "## Proof of Concept",
    "## Impact",
    "## Remediation",
    "## References",
]


class TestRenderMarkdown:
    """render_markdown must contain all required sections from the template."""

    def _base_report(self, cwe: str = "CWE-89") -> BugReport:
        return build_bug_report(_make_finding(cwe=cwe), _make_run())

    @pytest.mark.parametrize("section", _REQUIRED_SECTIONS)
    def test_section_present_sqli(self, section: str):
        md = render_markdown(self._base_report("CWE-89"))
        assert section in md, f"Missing section: {section!r}"

    @pytest.mark.parametrize("section", _REQUIRED_SECTIONS)
    def test_section_present_secret(self, section: str):
        f = _make_finding(scanner="gitleaks", cwe="CWE-798", rule_id="generic-api-key",
                          evidence="Match: sk-abcdef1234567890abcdef1234567890")
        md = render_markdown(build_bug_report(f, _make_run()))
        assert section in md, f"Missing section: {section!r}"

    @pytest.mark.parametrize("section", _REQUIRED_SECTIONS)
    def test_section_present_sca_cve(self, section: str):
        f = _make_finding(scanner="trivy", cwe=None, rule_id="CVE-2023-1234",
                          evidence="requests==2.25.0 CVE-2023-1234 HIGH")
        md = render_markdown(build_bug_report(f, _make_run()))
        assert section in md, f"Missing section: {section!r}"

    def test_title_is_first_heading(self):
        md = render_markdown(self._base_report())
        first_line = md.strip().split("\n")[0]
        assert first_line.startswith("# ")

    def test_platform_hint_in_footer(self):
        md = render_markdown(self._base_report())
        assert "Platform hint" in md

    def test_numbered_repro_steps(self):
        md = render_markdown(self._base_report())
        # After "Steps to Reproduce", there should be numbered list items
        steps_section = md.split("## Steps to Reproduce")[1].split("##")[0]
        assert "1." in steps_section

    def test_markdown_fences_in_poc(self):
        md = render_markdown(self._base_report())
        poc_section = md.split("## Proof of Concept")[1].split("##")[0]
        assert "```" in poc_section  # PoC should have code blocks

    def test_defensive_framing_note(self):
        md = render_markdown(self._base_report())
        assert "Defensive" in md or "defensive" in md or "authorized" in md.lower()


# ═══════════════════════════════════════════════════════════════════════════════
# (d) Secret masking
# ═══════════════════════════════════════════════════════════════════════════════


class TestSecretMasking:
    """Secret values must never appear unmasked in PoC text."""

    RAW_SECRET = "sk-1234567890abcdef1234567890abcdef"
    EXPECTED_MASK_PATTERN = r"sk-1\.\.\."  # first 4 + ... + last 4

    def test_mask_evidence_secrets_masks_long_token(self):
        evidence = f"Match: {self.RAW_SECRET}"
        masked = _mask_evidence_secrets(evidence)
        assert self.RAW_SECRET not in masked
        # Should still contain something (not empty string)
        assert len(masked) > 5

    def test_mask_preserves_short_tokens(self):
        evidence = "rule: xss line: 42"
        assert _mask_evidence_secrets(evidence) == evidence  # nothing to mask

    def test_secret_masked_in_rendered_poc(self):
        """The raw secret value from evidence must not appear in the rendered PoC."""
        raw_secret = "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"
        f = _make_finding(
            scanner="gitleaks",
            cwe="CWE-798",
            rule_id="github-pat",
            evidence=f"Rule: github-pat | Match: {raw_secret}",
            severity=Severity.CRITICAL,
        )
        report = build_bug_report(f, _make_run())
        md = render_markdown(report)
        assert raw_secret not in md, "Raw secret value leaked into rendered Markdown!"

    def test_masked_value_format(self):
        """Masked value should show first 4 chars + ... + last 4 chars."""
        evidence = "Match: sk-1234567890abcdef1234567890abcdef"
        masked = _mask_evidence_secrets(evidence)
        # Should contain the mask pattern (not the full value)
        assert "sk-1" in masked or "..." in masked

    def test_secret_in_poc_is_masked_hardcoded_class(self):
        """For HARDCODED_SECRET class, PoC must contain masked value, not raw."""
        long_secret = "AKIAIOSFODNN7EXAMPLE_longkey_1234567890"
        f = _make_finding(
            scanner="trufflehog",
            cwe="CWE-798",
            rule_id="aws-access-key",
            evidence=f"AWS Access Key: {long_secret}",
            severity=Severity.CRITICAL,
        )
        report = build_bug_report(f, _make_run())
        assert long_secret not in report.proof_of_concept

    def test_cve_id_not_masked(self):
        """CVE IDs should NOT be masked (they're not secrets)."""
        evidence = "CVE-2023-12345 requests==2.25.0 GHSA-j8r2-6x86-q33q"
        masked = _mask_evidence_secrets(evidence)
        # CVE and GHSA IDs are < 16 chars or break the pattern
        assert "CVE" in masked  # CVE IDs preserved


# ═══════════════════════════════════════════════════════════════════════════════
# (e) write_reports — file creation, filtering, index
# ═══════════════════════════════════════════════════════════════════════════════


class TestWriteReports:
    """write_reports creates files correctly and applies proper filters."""

    @pytest.mark.asyncio
    async def test_emits_file_per_eligible_finding(self, tmp_path: Path):
        run = _make_run()
        findings = [
            _make_finding(cwe="CWE-89", severity=Severity.HIGH,
                          verification_status=VerificationStatus.CONFIRMED),
            _make_finding(cwe="CWE-798", severity=Severity.CRITICAL,
                          verification_status=VerificationStatus.CONFIRMED,
                          scanner="gitleaks", rule_id="api-key"),
        ]
        run.findings = findings

        paths = await write_reports(findings, run, tmp_path)

        # Should have 2 reports + 1 index
        report_files = [p for p in paths if p.name != "index.md"]
        assert len(report_files) == 2, f"Expected 2 reports, got {len(report_files)}"

    @pytest.mark.asyncio
    async def test_creates_index_md(self, tmp_path: Path):
        run = _make_run()
        f = _make_finding(severity=Severity.HIGH,
                          verification_status=VerificationStatus.CONFIRMED)
        paths = await write_reports([f], run, tmp_path)
        index_path = next(p for p in paths if p.name == "index.md")
        assert index_path.exists()
        content = index_path.read_text()
        assert "# Bug Report Index" in content

    @pytest.mark.asyncio
    async def test_false_positives_excluded(self, tmp_path: Path):
        run = _make_run()
        findings = [
            _make_finding(severity=Severity.HIGH,
                          verification_status=VerificationStatus.FALSE_POSITIVE),
            _make_finding(severity=Severity.CRITICAL,
                          verification_status=VerificationStatus.FALSE_POSITIVE),
        ]
        paths = await write_reports(findings, run, tmp_path)
        report_files = [p for p in paths if p.name != "index.md"]
        assert len(report_files) == 0, "FP findings should not generate reports"

    @pytest.mark.asyncio
    async def test_medium_findings_excluded(self, tmp_path: Path):
        run = _make_run()
        f_medium = _make_finding(severity=Severity.MEDIUM,
                                 verification_status=VerificationStatus.CONFIRMED)
        f_low = _make_finding(severity=Severity.LOW,
                              verification_status=VerificationStatus.CONFIRMED)
        paths = await write_reports([f_medium, f_low], run, tmp_path)
        report_files = [p for p in paths if p.name != "index.md"]
        assert len(report_files) == 0, "MEDIUM/LOW findings should not generate reports"

    @pytest.mark.asyncio
    async def test_needs_manual_high_is_included(self, tmp_path: Path):
        run = _make_run()
        f = _make_finding(severity=Severity.HIGH,
                          verification_status=VerificationStatus.NEEDS_MANUAL)
        paths = await write_reports([f], run, tmp_path)
        report_files = [p for p in paths if p.name != "index.md"]
        assert len(report_files) == 1, "NEEDS_MANUAL HIGH should be included"

    @pytest.mark.asyncio
    async def test_report_files_are_valid_markdown(self, tmp_path: Path):
        run = _make_run()
        f = _make_finding(cwe="CWE-89", severity=Severity.HIGH,
                          verification_status=VerificationStatus.CONFIRMED)
        paths = await write_reports([f], run, tmp_path)
        report_files = [p for p in paths if p.name != "index.md"]
        for path in report_files:
            content = path.read_text(encoding="utf-8")
            assert content.startswith("# "), f"Report {path.name} does not start with a heading"
            for section in _REQUIRED_SECTIONS:
                assert section in content, f"Missing section '{section}' in {path.name}"

    @pytest.mark.asyncio
    async def test_report_filenames_are_slug_based(self, tmp_path: Path):
        run = _make_run()
        f = _make_finding(cwe="CWE-89", severity=Severity.HIGH,
                          verification_status=VerificationStatus.CONFIRMED)
        paths = await write_reports([f], run, tmp_path)
        report_files = [p for p in paths if p.name != "index.md"]
        assert len(report_files) == 1
        filename = report_files[0].name
        assert filename.startswith("report-01-")
        assert filename.endswith(".md")

    @pytest.mark.asyncio
    async def test_reports_in_subdirectory(self, tmp_path: Path):
        run = _make_run()
        f = _make_finding(severity=Severity.HIGH,
                          verification_status=VerificationStatus.CONFIRMED)
        paths = await write_reports([f], run, tmp_path)
        for p in paths:
            assert p.parent.name == "reports", f"Report not in 'reports' subdirectory: {p}"

    @pytest.mark.asyncio
    async def test_empty_findings_list(self, tmp_path: Path):
        run = _make_run()
        paths = await write_reports([], run, tmp_path)
        # Should still write index.md
        assert any(p.name == "index.md" for p in paths)
        report_files = [p for p in paths if p.name != "index.md"]
        assert len(report_files) == 0

    @pytest.mark.asyncio
    async def test_index_contains_audit_id(self, tmp_path: Path):
        run = _make_run()
        f = _make_finding(severity=Severity.CRITICAL,
                          verification_status=VerificationStatus.CONFIRMED)
        paths = await write_reports([f], run, tmp_path)
        index = next(p for p in paths if p.name == "index.md")
        content = index.read_text()
        assert run.audit_id in content


# ═══════════════════════════════════════════════════════════════════════════════
# (f) Edge cases
# ═══════════════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Edge-case handling: missing fields, unicode, very long evidence."""

    def test_missing_cvss_does_not_raise(self):
        run = _make_run()
        f = _make_finding(cvss_score=None, cvss_vector=None)
        report = build_bug_report(f, run)
        # Should not raise; should still produce a valid report
        assert report.severity is not None

    def test_unicode_evidence_does_not_raise(self):
        run = _make_run()
        f = _make_finding(
            evidence="SQL injection in field 'nombre_usuario': SELECT * WHERE usuario = '...' — обнаружена уязвимость; 发现漏洞",
        )
        report = build_bug_report(f, run)
        md = render_markdown(report)
        assert "## Proof of Concept" in md

    def test_very_long_evidence_truncated_gracefully(self):
        run = _make_run()
        long_evidence = "x" * 5000
        f = _make_finding(evidence=long_evidence)
        report = build_bug_report(f, run)
        md = render_markdown(report)
        # Should render without error; evidence is truncated in templates
        assert len(md) < 50_000

    def test_no_file_path_or_endpoint(self):
        run = _make_run()
        f = _make_finding(file_path=None, line_start=None, endpoint=None)
        report = build_bug_report(f, run)
        # Should use rule_id as fallback
        assert report.affected_asset == f.rule_id

    def test_critical_severity_label(self):
        run = _make_run()
        f = _make_finding(severity=Severity.CRITICAL)
        report = build_bug_report(f, run)
        assert report.severity == "Critical"

    def test_report_frozen_immutable(self):
        run = _make_run()
        f = _make_finding()
        report = build_bug_report(f, run)
        from pydantic import ValidationError
        with pytest.raises((ValidationError, TypeError)):
            # BugReport is frozen; direct attribute assignment must raise
            report.title = "mutated"  # type: ignore[misc]

    def test_references_list_is_nonempty(self):
        for cwe in ["CWE-89", "CWE-79", "CWE-918", "CWE-798", "CWE-22", "CWE-502", "CWE-347"]:
            run = _make_run()
            f = _make_finding(cwe=cwe)
            report = build_bug_report(f, run)
            assert len(report.references) >= 3, f"Too few references for {cwe}"

    def test_slug_contains_vuln_class_fragment(self):
        run = _make_run()
        f = _make_finding(cwe="CWE-89")
        report = build_bug_report(f, run)
        assert "sql" in report.slug

    def test_sca_cve_advisory_link_in_references(self):
        run = _make_run()
        f = _make_finding(
            scanner="trivy", cwe=None, rule_id="CVE-2023-32681",
            evidence="requests==2.28.0 CVE-2023-32681 HIGH",
        )
        report = build_bug_report(f, run)
        # Should contain an NVD or similar advisory link
        ref_str = " ".join(report.references)
        assert "nvd.nist.gov" in ref_str or "github.com/advisories" in ref_str or "osv.dev" in ref_str

    def test_cwe_reference_link_present(self):
        run = _make_run()
        f = _make_finding(cwe="CWE-89")
        report = build_bug_report(f, run)
        assert any("cwe.mitre.org" in ref for ref in report.references)

    def test_render_markdown_returns_string(self):
        run = _make_run()
        f = _make_finding()
        report = build_bug_report(f, run)
        md = render_markdown(report)
        assert isinstance(md, str)
        assert len(md) > 200
