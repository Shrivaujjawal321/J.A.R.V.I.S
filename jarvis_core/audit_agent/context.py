"""
AuditAgent — deterministic file-context classifier.

classify_context(file_path) → FindingContext

Runs BEFORE any LLM call. Labels the file a finding came from as one of
six categories (test / documentation / example / config_local / build / source)
and attaches a fp_prior float — the prior probability that a finding in this
file is a false positive.

Design rules:
- Pure Python, no I/O, no LLM, no subprocess.
- Deterministic: same input always produces same output.
- Conservative: when in doubt, falls through to 'source' (low fp_prior) —
  never silently promotes a source-file finding to FP on a weak heuristic.
- Order matters: more specific categories are checked before broader ones.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import PurePosixPath


# ── Category string constants (used as enum-like literals) ────────────────────

CATEGORY_TEST          = "test"
CATEGORY_DOCUMENTATION = "documentation"
CATEGORY_EXAMPLE       = "example"
CATEGORY_CONFIG_LOCAL  = "config_local"
CATEGORY_BUILD         = "build"
CATEGORY_SOURCE        = "source"


# ── Result struct ─────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class FindingContext:
    """Deterministic context label for a single finding's file location."""

    category: str          # one of the CATEGORY_* constants
    fp_prior: float        # [0, 1] — prior probability this is a false positive
    rationale: str         # one-line human-readable reason


# ── FP priors per category ─────────────────────────────────────────────────────
#
# These are conservative estimates grounded in the design doc (§1):
#   test / doc / example  → secrets are almost always fixtures / placeholders
#   config_local          → real secret but confined (gitignored, localhost)
#   build                 → generated artefact, rarely a real credential
#   source                → production code, low prior FP

_FP_PRIOR: dict[str, float] = {
    CATEGORY_TEST:          0.90,  # gitleaks/trufflehog FP rate on test fixtures ≈ high
    CATEGORY_DOCUMENTATION: 0.92,  # .md placeholders are documentation conventions
    CATEGORY_EXAMPLE:       0.88,  # samples/fixtures/mocks — almost never live
    CATEGORY_CONFIG_LOCAL:  0.35,  # real secret but gitignored & local-only
    CATEGORY_BUILD:         0.88,  # node_modules/vendor/dist — almost never a live cred
    CATEGORY_SOURCE:        0.10,  # production source code — trust the scanner
}


# ── Pattern sets ───────────────────────────────────────────────────────────────

# Path segments (case-insensitive) that signal a TEST context.
# Checked on the FULL path (all parts), not just the filename.
_TEST_SEGMENTS: frozenset[str] = frozenset({
    "__tests__", "tests", "test", "spec", "specs",
    "e2e", "integration", "unit", "fixtures",
})

# Path segment patterns (compiled regexes against individual path parts)
_TEST_PART_RE = re.compile(
    r"(^test[_\-]|[_\-]test$|\.test\.|\.spec\.|_test\.)",
    re.IGNORECASE,
)

# File extensions that are pure documentation.
# IMPORTANT: .txt is intentionally excluded — requirements.txt, go.sum, Pipfile, etc.
# are package manifests that can carry real CVEs. Only narrative-text formats go here.
_DOC_EXTENSIONS: frozenset[str] = frozenset({
    ".md", ".mdx", ".rst", ".adoc", ".asciidoc", ".textile",
    ".wiki",
})

# Directory segments that signal documentation context
_DOC_SEGMENTS: frozenset[str] = frozenset({
    "docs", "doc", "documentation", "wiki", "content", "pages",
    "posts", "blog", "guides", "tutorials",
})

# Directory segments or file parts that signal EXAMPLE / FIXTURE / MOCK context
_EXAMPLE_SEGMENTS: frozenset[str] = frozenset({
    "example", "examples", "sample", "samples", "fixture", "fixtures",
    "mock", "mocks", "stub", "stubs", "demo", "demos", "seed", "seeds",
    "placeholder", "fake",
})

# Filenames (stem, lowercase) that signal example/template files
_EXAMPLE_STEMS_RE = re.compile(
    r"(example|sample|fixture|mock|stub|demo|template|placeholder|fake)",
    re.IGNORECASE,
)

# Exact filenames that are local-only config (gitignored by convention)
_CONFIG_LOCAL_NAMES: frozenset[str] = frozenset({
    ".env.local", ".env.development", ".env.development.local",
    ".env.test.local", ".env.production.local",
    ".env.override", ".env.default",
})

# Filenames that are example env templates (NOT real secrets)
_ENV_EXAMPLE_NAMES: frozenset[str] = frozenset({
    ".env.example", ".env.sample", ".env.template", ".env.dist",
    "example.env", "sample.env", "template.env",
})

# Build artefact directories
_BUILD_SEGMENTS: frozenset[str] = frozenset({
    "dist", "build", "out", "target", "bin", "obj", "__pycache__",
    ".next", ".nuxt", ".output", ".cache", "coverage", ".nyc_output",
    "node_modules", "vendor", "venv", ".venv",
})


# ── Main classifier ────────────────────────────────────────────────────────────


def classify_context(file_path: str | None) -> FindingContext:
    """Classify a finding's source file into one of six context categories.

    Args:
        file_path: Relative or absolute path string from the scanner.
                   None or empty → treated as source (conservative).

    Returns:
        FindingContext with category, fp_prior, and a one-line rationale.
    """
    if not file_path:
        return FindingContext(
            category=CATEGORY_SOURCE,
            fp_prior=_FP_PRIOR[CATEGORY_SOURCE],
            rationale="No file path — treating as source (conservative)",
        )

    # Normalise to forward-slash, lowercase for matching
    normalised = file_path.replace("\\", "/")
    path = PurePosixPath(normalised)
    parts_lower = [p.lower() for p in path.parts]
    name_lower  = path.name.lower()
    stem_lower  = path.stem.lower()
    suffix_lower = path.suffix.lower()

    # ── 1. BUILD artefacts ────────────────────────────────────────────────────
    # Check first — node_modules/vendor secrets are almost always transitive,
    # not hand-coded, and the finding belongs to a dep scan not source triage.
    if any(part in _BUILD_SEGMENTS for part in parts_lower):
        matched = next(p for p in parts_lower if p in _BUILD_SEGMENTS)
        return FindingContext(
            category=CATEGORY_BUILD,
            fp_prior=_FP_PRIOR[CATEGORY_BUILD],
            rationale=f"File is inside build/generated directory '{matched}'",
        )

    # ── 2. TEST files ─────────────────────────────────────────────────────────
    # Check path-part membership first (directory names like /tests/ or __tests__)
    test_dir = next(
        (p for p in parts_lower[:-1] if p in _TEST_SEGMENTS),  # dirs only
        None,
    )
    if test_dir:
        return FindingContext(
            category=CATEGORY_TEST,
            fp_prior=_FP_PRIOR[CATEGORY_TEST],
            rationale=f"File is inside test directory '{test_dir}/'",
        )

    # Then check the filename itself for test patterns
    if _TEST_PART_RE.search(name_lower):
        return FindingContext(
            category=CATEGORY_TEST,
            fp_prior=_FP_PRIOR[CATEGORY_TEST],
            rationale=f"Filename matches test pattern: '{path.name}'",
        )

    # ── 3. DOCUMENTATION files ────────────────────────────────────────────────
    # .md / .rst / etc. are almost exclusively documentation
    if suffix_lower in _DOC_EXTENSIONS:
        return FindingContext(
            category=CATEGORY_DOCUMENTATION,
            fp_prior=_FP_PRIOR[CATEGORY_DOCUMENTATION],
            rationale=f"File extension '{suffix_lower}' is a documentation format",
        )

    # Docs directory by name
    doc_dir = next(
        (p for p in parts_lower[:-1] if p in _DOC_SEGMENTS),
        None,
    )
    if doc_dir:
        return FindingContext(
            category=CATEGORY_DOCUMENTATION,
            fp_prior=_FP_PRIOR[CATEGORY_DOCUMENTATION],
            rationale=f"File is inside documentation directory '{doc_dir}/'",
        )

    # ── 4. EXAMPLE / FIXTURE / MOCK files ────────────────────────────────────
    # .env.example and similar are explicit templates, never real
    if name_lower in _ENV_EXAMPLE_NAMES:
        return FindingContext(
            category=CATEGORY_EXAMPLE,
            fp_prior=_FP_PRIOR[CATEGORY_EXAMPLE],
            rationale=f"File '{path.name}' is an environment example/template (not real secrets)",
        )

    # Example/fixture/mock directories
    example_dir = next(
        (p for p in parts_lower[:-1] if p in _EXAMPLE_SEGMENTS),
        None,
    )
    if example_dir:
        return FindingContext(
            category=CATEGORY_EXAMPLE,
            fp_prior=_FP_PRIOR[CATEGORY_EXAMPLE],
            rationale=f"File is inside example/fixture directory '{example_dir}/'",
        )

    # Example/fixture stems in filename
    if _EXAMPLE_STEMS_RE.search(stem_lower):
        return FindingContext(
            category=CATEGORY_EXAMPLE,
            fp_prior=_FP_PRIOR[CATEGORY_EXAMPLE],
            rationale=f"Filename stem '{path.stem}' matches example/fixture/mock pattern",
        )

    # ── 5. LOCAL CONFIG files ─────────────────────────────────────────────────
    # .env.local etc. are gitignored by convention and contain dev-only secrets.
    # Real, but lower severity than committed source secrets.
    if name_lower in _CONFIG_LOCAL_NAMES:
        return FindingContext(
            category=CATEGORY_CONFIG_LOCAL,
            fp_prior=_FP_PRIOR[CATEGORY_CONFIG_LOCAL],
            rationale=(
                f"File '{path.name}' is a local-only config (gitignored by convention); "
                "secret is real but dev/local scope"
            ),
        )

    # Plain .env that is NOT a committed secret (e.g. just named ".env")
    # Note: a committed .env in source root IS a real finding → leave as source
    # We only tag .env.local / .env.development / etc. here (handled above).

    # ── 6. SOURCE (default) ───────────────────────────────────────────────────
    return FindingContext(
        category=CATEGORY_SOURCE,
        fp_prior=_FP_PRIOR[CATEGORY_SOURCE],
        rationale="Production source file — scanner finding has high prior validity",
    )
