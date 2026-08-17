"""
Tests for jarvis_core.audit_agent.reachability + custom semgrep rule validity.

Coverage:
(a) extract_package_name from OSV-style evidence
(b) assess_reachability: imported pkg → reachable; lockfile-only pkg → not reachable
(c) JS require/import detection; npm scope handling
(d) non-SCA findings + unparseable evidence → neutral verdict
(e) apply_verdict downgrade/keep semantics (recall-safe: never FALSE_POSITIVE)
(f) every custom semgrep rule yaml compiles (`semgrep --validate`), skipped if
    the semgrep binary is unavailable.

All tests run without scanner binaries (except the explicitly-skippable validate
test) and without LLM calls.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from jarvis_core.audit_agent.models import Finding, Severity, VerificationStatus
from jarvis_core.audit_agent.reachability import (
    ReachabilityVerdict,
    apply_verdict,
    assess_reachability,
    extract_package_name,
    _import_module_candidates,
    _normalize_pkg,
)

RULES_DIR = PROJECT_ROOT / "jarvis_core" / "audit_agent" / "configs" / "rules"


# ── Helpers ──────────────────────────────────────────────────────────────────


def _osv_finding(pkg: str, version: str = "1.0.0", sev: Severity = Severity.HIGH) -> Finding:
    return Finding(
        scanner="osv",
        rule_id="CVE-2024-0001",
        severity=sev,
        evidence=f"CVE-2024-0001 in {pkg}@{version}: a vulnerability in {pkg}",
    )


# ── (a) package-name extraction ──────────────────────────────────────────────


def test_extract_package_name_basic():
    f = _osv_finding("requests", "2.25.0")
    assert extract_package_name(f) == "requests"


def test_extract_package_name_npm_scope():
    f = _osv_finding("@babel/traverse", "7.0.0")
    assert extract_package_name(f) == "@babel/traverse"


def test_extract_package_name_unparseable():
    f = Finding(scanner="osv", rule_id="X", severity=Severity.LOW,
                evidence="some malformed evidence with no package marker")
    assert extract_package_name(f) is None


def test_normalize_pkg_strips_scope_and_lowercases():
    assert _normalize_pkg("@Scope/MyPkg") == "mypkg"
    assert _normalize_pkg("Requests") == "requests"


def test_import_candidates_include_hyphen_underscore_variants():
    cands = _import_module_candidates("python-jose")
    assert "python-jose" in cands
    assert "python_jose" in cands


# ── (b) reachable: package imported in app code ──────────────────────────────


def test_python_imported_package_is_reachable(tmp_path: Path):
    (tmp_path / "app.py").write_text(
        "import os\nimport requests\n\ndef f():\n    return requests.get('x')\n"
    )
    f = _osv_finding("requests")
    v = assess_reachability(f, str(tmp_path))
    assert v.reachable is True
    assert v.priority_adjustment == "raise"  # HIGH severity → raise
    assert v.evidence is not None
    assert "app.py:2" in v.evidence


def test_python_from_import_is_reachable(tmp_path: Path):
    (tmp_path / "svc.py").write_text("from jinja2 import Template\n")
    f = _osv_finding("jinja2", sev=Severity.MEDIUM)
    v = assess_reachability(f, str(tmp_path))
    assert v.reachable is True
    assert v.priority_adjustment == "keep"  # non-high severity → keep


# ── (b') NOT reachable: present only in a lockfile, never imported ───────────


def test_lockfile_only_package_is_not_reachable(tmp_path: Path):
    # Package appears in a lockfile but is never imported by source.
    (tmp_path / "requirements.txt").write_text("leftpad==1.0.0\nrequests==2.25.0\n")
    (tmp_path / "app.py").write_text("import requests\nrequests.get('x')\n")
    f = _osv_finding("leftpad")
    v = assess_reachability(f, str(tmp_path))
    assert v.reachable is False
    assert v.priority_adjustment == "downgrade"
    assert v.adjusted_severity == Severity.LOW
    assert v.adjusted_status == VerificationStatus.NEEDS_MANUAL
    assert "not reachable" in v.reason.lower()


def test_transitive_unused_dep_downgraded(tmp_path: Path):
    (tmp_path / "package-lock.json").write_text('{"dependencies": {"lodash": {}}}')
    (tmp_path / "index.js").write_text("const x = require('express');\n")
    f = _osv_finding("lodash")
    v = assess_reachability(f, str(tmp_path))
    assert v.reachable is False
    assert v.priority_adjustment == "downgrade"


# ── (c) JS/TS import detection + scope ───────────────────────────────────────


def test_js_require_is_reachable(tmp_path: Path):
    (tmp_path / "server.js").write_text("const ax = require('axios');\n")
    f = _osv_finding("axios")
    v = assess_reachability(f, str(tmp_path))
    assert v.reachable is True


def test_ts_esm_import_is_reachable(tmp_path: Path):
    (tmp_path / "api.ts").write_text("import express from 'express';\n")
    f = _osv_finding("express")
    v = assess_reachability(f, str(tmp_path))
    assert v.reachable is True


def test_js_scoped_package_reachable(tmp_path: Path):
    (tmp_path / "b.js").write_text("import traverse from '@babel/traverse';\n")
    f = _osv_finding("@babel/traverse")
    v = assess_reachability(f, str(tmp_path))
    assert v.reachable is True


def test_js_subpath_import_reachable(tmp_path: Path):
    (tmp_path / "c.js").write_text("const m = require('lodash/merge');\n")
    f = _osv_finding("lodash")
    v = assess_reachability(f, str(tmp_path))
    assert v.reachable is True


# ── (c') exclusions: imports only inside node_modules don't count ────────────


def test_imports_in_node_modules_are_excluded(tmp_path: Path):
    nm = tmp_path / "node_modules" / "somepkg"
    nm.mkdir(parents=True)
    (nm / "index.js").write_text("require('lodash');\n")  # vendored, not app code
    (tmp_path / "app.js").write_text("console.log('no deps here');\n")
    f = _osv_finding("lodash")
    v = assess_reachability(f, str(tmp_path))
    assert v.reachable is False


# ── (d) neutral verdicts ─────────────────────────────────────────────────────


def test_non_sca_finding_is_neutral(tmp_path: Path):
    f = Finding(scanner="semgrep", rule_id="jarvis-ssrf", severity=Severity.HIGH,
                evidence="ssrf in app.py")
    v = assess_reachability(f, str(tmp_path))
    assert v.reachable is None
    assert v.priority_adjustment == "none"


def test_unparseable_package_is_neutral(tmp_path: Path):
    f = Finding(scanner="osv", rule_id="X", severity=Severity.LOW,
                evidence="no package marker present")
    v = assess_reachability(f, str(tmp_path))
    assert v.reachable is None
    assert v.priority_adjustment == "none"


def test_missing_target_path_is_neutral():
    f = _osv_finding("requests")
    v = assess_reachability(f, "/nonexistent/path/xyz123")
    assert v.reachable is None


# ── (e) apply_verdict semantics (recall-safe) ────────────────────────────────


def test_apply_verdict_downgrade_mutates_finding():
    f = _osv_finding("leftpad", sev=Severity.HIGH)
    v = ReachabilityVerdict(
        finding_id=f.id, package="leftpad", reachable=False,
        priority_adjustment="downgrade", adjusted_severity=Severity.LOW,
        adjusted_status=VerificationStatus.NEEDS_MANUAL, reason="unused dep",
    )
    out = apply_verdict(f, v)
    assert out.severity == Severity.LOW
    assert out.verification_status == VerificationStatus.NEEDS_MANUAL
    # Recall-safe: a downgrade NEVER marks FALSE_POSITIVE (stays auditable).
    assert out.verification_status != VerificationStatus.FALSE_POSITIVE
    assert out.confidence <= 0.4
    assert out.verification_reason == "unused dep"


def test_apply_verdict_raise_sets_reason_and_confidence():
    f = _osv_finding("requests", sev=Severity.HIGH)
    f.confidence = 0.5
    v = ReachabilityVerdict(
        finding_id=f.id, package="requests", reachable=True,
        evidence="app.py:2", priority_adjustment="raise", reason="imported",
    )
    out = apply_verdict(f, v)
    assert out.severity == Severity.HIGH  # unchanged
    assert out.confidence >= 0.6
    assert out.verification_reason == "imported"


def test_apply_verdict_neutral_is_noop():
    f = _osv_finding("requests", sev=Severity.HIGH)
    before = (f.severity, f.verification_status)
    v = ReachabilityVerdict(finding_id=f.id, reachable=None, priority_adjustment="none")
    out = apply_verdict(f, v)
    assert (out.severity, out.verification_status) == before


# ── (f) semgrep rule validity ────────────────────────────────────────────────


def test_rules_directory_exists_and_has_yaml():
    assert RULES_DIR.is_dir()
    yamls = list(RULES_DIR.glob("*.yaml"))
    assert len(yamls) >= 7, f"expected >=7 rule packs, found {len(yamls)}"


@pytest.mark.parametrize("rule_file", sorted(RULES_DIR.glob("*.yaml")), ids=lambda p: p.name)
def test_each_semgrep_rule_file_compiles(rule_file: Path):
    """`semgrep --validate` must pass for each rule pack. Skips if semgrep absent."""
    semgrep_bin = shutil.which("semgrep") or str(PROJECT_ROOT / ".venv" / "bin" / "semgrep")
    if not Path(semgrep_bin).exists() and not shutil.which("semgrep"):
        pytest.skip("semgrep binary not available")
    proc = subprocess.run(
        [semgrep_bin, "--config", str(rule_file), "--validate", "--metrics=off"],
        capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, (
        f"{rule_file.name} failed --validate:\n{proc.stdout}\n{proc.stderr}"
    )


def test_full_rules_dir_validates():
    """The whole directory must validate as one config (no cross-file id clashes)."""
    semgrep_bin = shutil.which("semgrep") or str(PROJECT_ROOT / ".venv" / "bin" / "semgrep")
    if not Path(semgrep_bin).exists() and not shutil.which("semgrep"):
        pytest.skip("semgrep binary not available")
    proc = subprocess.run(
        [semgrep_bin, "--config", str(RULES_DIR), "--validate", "--metrics=off"],
        capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, f"rules dir failed --validate:\n{proc.stdout}\n{proc.stderr}"
