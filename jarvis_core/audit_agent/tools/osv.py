"""
OsvScannerAdapter — SCA via OSV database.

Command: osv-scanner --format json -r <target_path>
Exit code 1 = vulnerabilities found (normal), 0 = clean.
"""
from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path

from ..models import Finding, RawScanResult, Severity, OWASPCategory
from ..normalizers.cvss import cve_severity_to_cvss_vector, score_vector
from .base import ToolAdapter, ToolInput, ToolTimeoutError, ToolError, _run_subprocess

log = logging.getLogger("jarvis_core.audit_agent.tools.osv")

# Dependency manifests/lockfiles osv-scanner understands. Used to find a scan
# root when the audited subdir has none of its own (deps are repo-global).
_MANIFEST_NAMES = {
    "requirements.txt", "pyproject.toml", "poetry.lock", "Pipfile", "Pipfile.lock",
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "go.mod", "go.sum", "Gemfile", "Gemfile.lock", "Cargo.toml", "Cargo.lock",
    "composer.lock", "pom.xml", "build.gradle", "build.gradle.kts",
}


def _has_manifest(d: Path) -> bool:
    try:
        for entry in os.listdir(d):
            if entry in _MANIFEST_NAMES or (
                entry.startswith("requirements") and entry.endswith(".txt")
            ):
                return True
    except OSError:
        pass
    return False


def _find_scan_root(target_path: str) -> str | None:
    """When the audited path has no dependency manifest, walk up to find one.

    Dependencies are repo-global, so for an SCA scan we want the repo's manifests
    even if the user pointed at a subdir. Prefer the git repo root (scanning it
    with -r catches every manifest in the repo); else the nearest ancestor that
    directly holds a manifest. Bounded by $HOME to never escape the repo.
    """
    start = Path(target_path).resolve()
    home = Path(os.path.expanduser("~")).resolve()
    cur = start if start.is_dir() else start.parent

    # 1. Prefer the git repo root.
    walk = cur
    for _ in range(40):
        if (walk / ".git").exists():
            return str(walk)
        if walk == walk.parent or walk == home:
            break
        walk = walk.parent

    # 2. No git root — nearest ancestor directly holding a manifest.
    walk = cur
    for _ in range(40):
        if _has_manifest(walk):
            return str(walk)
        if walk == walk.parent or walk == home:
            break
        walk = walk.parent
    return None


def _no_package_sources(rc: int, stderr: str) -> bool:
    """osv-scanner signals 'nothing to scan' via exit 128 / this stderr line."""
    return rc == 128 or "No package sources found" in (stderr or "")

_SEVERITY_MAP: dict[str, Severity] = {
    "CRITICAL": Severity.CRITICAL,
    "HIGH":     Severity.HIGH,
    "MEDIUM":   Severity.MEDIUM,
    "LOW":      Severity.LOW,
}


class OsvScannerAdapter(ToolAdapter):
    name = "osv"
    scanner_type = "sca"

    async def run(self, inp: ToolInput) -> RawScanResult:
        started = time.perf_counter()

        # First pass: scan exactly what was requested.
        result = await self._scan_path(inp, inp.target_path, started)
        if result is None:
            log.info("osv-scanner binary not found — skipping")
            return self._make_error_result("not_installed")

        # If the audited dir holds no dependency manifest, deps live at the repo
        # root — walk up and re-scan there so SCA isn't silently empty.
        if _no_package_sources(result.exit_code, result.stderr):
            scan_root = _find_scan_root(inp.target_path)
            if scan_root and os.path.abspath(scan_root) != os.path.abspath(inp.target_path):
                log.info(
                    "osv: no manifest under %s — rescanning repo root %s",
                    inp.target_path, scan_root,
                )
                retry = await self._scan_path(inp, scan_root, started)
                if retry is not None:
                    return retry
        return result

    async def _scan_path(self, inp: ToolInput, path: str, started: float) -> RawScanResult | None:
        """Run osv-scanner against one path. Returns None only if no binary exists."""
        for binary in ("osv-scanner", "osv_scanner"):
            cmd = [
                binary,
                "--format", "json",
                "-r", path,
                *inp.extra_args,
            ]
            try:
                rc, stdout, stderr = await _run_subprocess(
                    cmd,
                    timeout_seconds=inp.timeout_seconds,
                    env_overrides=inp.env_overrides,
                )
                duration_ms = int((time.perf_counter() - started) * 1000)
                # exit 1 = vulns found (normal); 128 = nothing to scan (not an error)
                if rc > 1 and rc != 128:
                    log.warning("osv-scanner exit_code=%d stderr=%r", rc, stderr[:300])
                return RawScanResult(
                    scanner=self.name,
                    exit_code=rc,
                    stdout=stdout,
                    stderr=stderr,
                    duration_ms=duration_ms,
                )
            except FileNotFoundError:
                continue  # Try next binary name
            except ToolTimeoutError as exc:
                log.warning("osv-scanner timeout: %s", exc)
                return self._make_error_result(f"timeout:{exc}")
            except ToolError as exc:
                log.warning("osv-scanner error: %s", exc)
                return self._make_error_result(f"tool_error:{exc}")
        return None

    def normalize(self, raw: RawScanResult) -> list[Finding]:
        findings: list[Finding] = []
        try:
            data = json.loads(raw.stdout or "{}")
        except json.JSONDecodeError as exc:
            log.warning("osv JSON parse failed: %s", exc)
            return []

        for result in data.get("results", []):
            for pkg_info in result.get("packages", []):
                pkg_name = pkg_info.get("package", {}).get("name", "unknown")
                pkg_version = pkg_info.get("package", {}).get("version", "?")
                for vuln in pkg_info.get("vulnerabilities", []):
                    try:
                        vuln_id = vuln.get("id", "UNKNOWN")
                        summary = vuln.get("summary", "") or vuln.get("details", "")[:120]

                        # Determine severity from aliases or database_specific
                        sev = Severity.MEDIUM
                        sev_raw = "MEDIUM"
                        db_specific = vuln.get("database_specific", {})
                        if db_specific.get("severity"):
                            sev_raw = db_specific["severity"].upper()
                            sev = _SEVERITY_MAP.get(sev_raw, Severity.MEDIUM)

                        cvss_vec = cve_severity_to_cvss_vector(sev_raw)
                        cvss_score = score_vector(cvss_vec) if cvss_vec else None

                        findings.append(Finding(
                            scanner=self.name,
                            rule_id=vuln_id,
                            owasp_category=OWASPCategory.SCA_CVE,
                            cvss_vector=cvss_vec,
                            cvss_score=cvss_score,
                            severity=sev,
                            evidence=(
                                f"{vuln_id} in {pkg_name}@{pkg_version}: {summary}"
                            ),
                        ))
                    except Exception as exc:
                        log.debug("osv normalize skipped: %s", exc)

        log.info("osv normalized %d findings", len(findings))
        return findings
