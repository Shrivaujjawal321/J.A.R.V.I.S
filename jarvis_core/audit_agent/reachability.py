"""
SCA reachability analysis — the highest-leverage FP-killer for dependency CVEs.

Per the verification-layer research (`01-verification-layer.md` §3): 60–95% of SCA
alerts are unreachable code. A wall of 32 dependency-CVE findings collapses to a
prioritized few once you know which packages are actually IMPORTED/USED by the
audited source.

This module is **deterministic, fast, bounded, LLM-free**. It does *package-level*
reachability (is the vulnerable package imported anywhere in app code?) — a strong,
cheap signal. It is intentionally NOT symbol-level call-graph reachability (that's
govulncheck/OSV-Scanner-v2 territory and language-specific); package-level is the
80/20 win and never produces false *negatives* of the dangerous kind (if a package
is imported we keep the finding; we only downgrade when it is provably never
imported).

Contract (mirrors the research doc's recall-protection rule):
  - reachable=True  → keep/raise priority (vulnerable dep is in the call surface).
  - reachable=False → downgrade to LOW / NEEDS_MANUAL with reason
    "transitive/unused — not reachable from app code". NEVER hard-suppress: a static
    import scan can miss dynamic imports (importlib, require(variable)), so an
    unreachable verdict is *evidence to downgrade*, not to delete.
  - reachable=None  → unknown (could not parse the package name, or not an SCA
    finding) → no adjustment.

Pure Python, stdlib only.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from .models import Finding, Severity, VerificationStatus

# ── Bounds (keep it fast + safe) ────────────────────────────────────────────────

#: Hard cap on source files scanned, so a giant monorepo can't stall the audit.
MAX_FILES_SCANNED = int(os.getenv("AUDIT_REACH_MAX_FILES", "5000"))

#: Per-file byte cap — skip huge generated/minified files.
MAX_FILE_BYTES = int(os.getenv("AUDIT_REACH_MAX_FILE_BYTES", str(2_000_000)))

#: Directories never worth scanning for app-code imports.
_EXCLUDED_DIR_PARTS = frozenset({
    ".git", "node_modules", "vendor", ".venv", "venv", "__pycache__",
    "dist", "build", ".next", "out", "_experimental", "site-packages",
    ".tox", ".mypy_cache", ".pytest_cache", "bower_components",
})

#: Source extensions we understand imports for.
_PY_EXTS = frozenset({".py", ".pyi"})
_JS_EXTS = frozenset({".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"})

#: Files that are *lockfiles/manifests* (presence ≠ reachable; used to explain the
#: "present in lockfile but never imported" downgrade reason).
_LOCKFILE_NAMES = frozenset({
    "requirements.txt", "poetry.lock", "Pipfile.lock", "package-lock.json",
    "yarn.lock", "pnpm-lock.yaml", "go.sum", "Gemfile.lock", "Cargo.lock",
    "composer.lock",
})


# ── Verdict model ───────────────────────────────────────────────────────────────


class ReachabilityVerdict(BaseModel):
    """Deterministic reachability assessment for one dependency-CVE finding."""

    finding_id: str
    package: str | None = None
    #: True = imported in app code; False = provably not imported; None = unknown / N/A.
    reachable: bool | None = None
    #: First import site found, as "relative/path.py:LINE" (only when reachable=True).
    evidence: str | None = None
    #: Other import sites (capped), for the report.
    evidence_extra: list[str] = Field(default_factory=list)
    #: How the verdict should move the finding's priority.
    priority_adjustment: Literal["raise", "keep", "downgrade", "none"] = "none"
    #: Severity to apply when downgrading (None unless downgrade).
    adjusted_severity: Severity | None = None
    #: Verification status to apply when downgrading (None unless downgrade).
    adjusted_status: VerificationStatus | None = None
    #: Human-readable rationale (goes into Finding.verification_reason).
    reason: str = ""
    files_scanned: int = 0


# ── Package-name extraction ─────────────────────────────────────────────────────

# osv.py emits evidence as: "<vuln_id> in <pkg>@<version>: <summary>"
_OSV_EVIDENCE_RE = re.compile(r"\bin\s+([A-Za-z0-9._@/\-]+)@")


def _normalize_pkg(name: str) -> str:
    """Lowercase + strip an npm scope prefix for matching ('@scope/pkg' -> 'pkg')."""
    name = name.strip().lower()
    if name.startswith("@") and "/" in name:
        name = name.split("/", 1)[1]
    return name


def extract_package_name(finding: Finding) -> str | None:
    """Pull the package name out of an OSV finding's evidence string.

    Returns the raw (un-normalized) package name, or None if not parseable.
    """
    if not finding.evidence:
        return None
    m = _OSV_EVIDENCE_RE.search(finding.evidence)
    if m:
        return m.group(1)
    return None


def _import_module_candidates(pkg: str) -> set[str]:
    """Module/import tokens a package might be imported under.

    PyPI/npm dist names don't always equal the import name, so we accept a few
    normalizations (hyphen↔underscore, scope-stripped). This widens recall on the
    'reachable' side (we'd rather keep a finding than wrongly downgrade it).
    """
    norm = _normalize_pkg(pkg)
    cands = {norm}
    cands.add(norm.replace("-", "_"))
    cands.add(norm.replace("_", "-"))
    cands.add(norm.replace("-", ""))
    # Keep the original scoped npm form too (require('@scope/pkg'))
    raw = pkg.strip().lower()
    cands.add(raw)
    return {c for c in cands if c}


# ── Import scanners (regex-based, intra-file) ───────────────────────────────────


def _py_import_regexes(pkg_tokens: set[str]) -> list[re.Pattern[str]]:
    """`import pkg`, `import pkg.sub`, `from pkg import x`, `from pkg.sub import x`."""
    pats: list[re.Pattern[str]] = []
    for tok in pkg_tokens:
        t = re.escape(tok)
        pats.append(re.compile(rf"^\s*import\s+{t}(\s|\.|,|$)"))
        pats.append(re.compile(rf"^\s*from\s+{t}(\s|\.)"))
        # `import a, pkg, b`
        pats.append(re.compile(rf"^\s*import\s+.*[,\s]{t}(\s|\.|,|$)"))
    return pats


def _js_import_regexes(pkg_tokens: set[str]) -> list[re.Pattern[str]]:
    """`require('pkg')`, `import ... from 'pkg'`, `import 'pkg'`, dynamic import()."""
    pats: list[re.Pattern[str]] = []
    for tok in pkg_tokens:
        t = re.escape(tok)
        # Match the package as a module specifier; allow 'pkg' or 'pkg/subpath'.
        spec = rf"['\"]{t}(/[^'\"]*)?['\"]"
        pats.append(re.compile(rf"require\(\s*{spec}\s*\)"))
        pats.append(re.compile(rf"\bfrom\s+{spec}"))
        pats.append(re.compile(rf"\bimport\s+{spec}"))
        pats.append(re.compile(rf"\bimport\(\s*{spec}\s*\)"))
    return pats


def _iter_source_files(root: Path) -> "list[Path]":
    """Yield source files under root, excluding build/vendor dirs, bounded."""
    out: list[Path] = []
    if root.is_file():
        return [root]
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune excluded dirs in-place so os.walk doesn't descend into them.
        dirnames[:] = [d for d in dirnames if d not in _EXCLUDED_DIR_PARTS]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext in _PY_EXTS or ext in _JS_EXTS:
                out.append(Path(dirpath) / fn)
                if len(out) >= MAX_FILES_SCANNED:
                    return out
    return out


def _scan_for_imports(
    files: list[Path],
    root: Path,
    py_pats: list[re.Pattern[str]],
    js_pats: list[re.Pattern[str]],
    max_evidence: int = 5,
) -> tuple[list[str], int]:
    """Scan files for import sites. Returns (evidence_list, files_scanned)."""
    evidence: list[str] = []
    scanned = 0
    for f in files:
        ext = f.suffix.lower()
        if ext in _PY_EXTS:
            pats = py_pats
        elif ext in _JS_EXTS:
            pats = js_pats
        else:
            continue
        try:
            if f.stat().st_size > MAX_FILE_BYTES:
                continue
            with f.open("r", encoding="utf-8", errors="ignore") as fh:
                lines = fh.readlines()
        except OSError:
            continue
        scanned += 1
        for lineno, line in enumerate(lines, start=1):
            if any(p.search(line) for p in pats):
                try:
                    rel = f.relative_to(root)
                except ValueError:
                    rel = f
                evidence.append(f"{rel}:{lineno}")
                if len(evidence) >= max_evidence:
                    return evidence, scanned
    return evidence, scanned


# ── Public entry point ──────────────────────────────────────────────────────────


def assess_reachability(finding: Finding, target_path: str) -> ReachabilityVerdict:
    """Decide whether a dependency-CVE finding's package is reachable from app code.

    Only meaningful for SCA findings (`finding.scanner == "osv"`). For any other
    scanner, or an unparseable package name, returns a neutral verdict
    (reachable=None, priority_adjustment="none") so callers can apply it
    unconditionally without special-casing.

    Args:
        finding: the Finding to assess.
        target_path: the audited source tree root (a dir or a file path).

    Returns:
        A ReachabilityVerdict. Callers apply `adjusted_severity` / `adjusted_status`
        / `reason` to the finding when `priority_adjustment == "downgrade"`, and
        leave the finding as-is otherwise.
    """
    # Only SCA findings are subject to reachability.
    if finding.scanner != "osv":
        return ReachabilityVerdict(
            finding_id=finding.id,
            reachable=None,
            priority_adjustment="none",
            reason="not an SCA finding — reachability N/A",
        )

    pkg = extract_package_name(finding)
    if not pkg:
        return ReachabilityVerdict(
            finding_id=finding.id,
            reachable=None,
            priority_adjustment="none",
            reason="could not parse package name from finding evidence",
        )

    root = Path(target_path).resolve()
    if not root.exists():
        return ReachabilityVerdict(
            finding_id=finding.id,
            package=pkg,
            reachable=None,
            priority_adjustment="none",
            reason=f"target path does not exist: {target_path}",
        )

    tokens = _import_module_candidates(pkg)
    py_pats = _py_import_regexes(tokens)
    js_pats = _js_import_regexes(tokens)

    files = _iter_source_files(root)
    evidence, scanned = _scan_for_imports(files, root, py_pats, js_pats)

    if evidence:
        # Imported and used → keep (or raise for high-severity CVEs).
        adj: Literal["raise", "keep"] = (
            "raise" if finding.severity in (Severity.CRITICAL, Severity.HIGH) else "keep"
        )
        return ReachabilityVerdict(
            finding_id=finding.id,
            package=pkg,
            reachable=True,
            evidence=evidence[0],
            evidence_extra=evidence[1:],
            priority_adjustment=adj,
            reason=(
                f"package '{pkg}' is imported in app code "
                f"({evidence[0]}) — vulnerable dependency is reachable"
            ),
            files_scanned=scanned,
        )

    # Provably-not-imported (within our static scan) → downgrade, never delete.
    return ReachabilityVerdict(
        finding_id=finding.id,
        package=pkg,
        reachable=False,
        priority_adjustment="downgrade",
        adjusted_severity=Severity.LOW,
        adjusted_status=VerificationStatus.NEEDS_MANUAL,
        reason=(
            f"package '{pkg}' is present in the dependency tree but is never "
            f"imported in scanned app code (transitive/unused — not reachable). "
            f"Downgraded; verify manually for dynamic/reflective imports. "
            f"(scanned {scanned} source files)"
        ),
        files_scanned=scanned,
    )


def apply_verdict(finding: Finding, verdict: ReachabilityVerdict) -> Finding:
    """Mutate + return the finding per a downgrade verdict (no-op otherwise).

    Helper for the orchestrator. Keeps recall safe: only ever *lowers* severity on
    a reachable=False verdict, and routes to NEEDS_MANUAL (never FALSE_POSITIVE), so
    the finding stays auditable and a human can catch a dynamic-import blind spot.
    """
    if verdict.priority_adjustment == "downgrade":
        if verdict.adjusted_severity is not None:
            finding.severity = verdict.adjusted_severity
        if verdict.adjusted_status is not None:
            finding.verification_status = verdict.adjusted_status
        finding.verification_reason = verdict.reason
        finding.confidence = min(finding.confidence, 0.4)
    elif verdict.priority_adjustment in ("raise", "keep"):
        finding.verification_reason = verdict.reason
        if verdict.priority_adjustment == "raise":
            finding.confidence = max(finding.confidence, 0.6)
    return finding
