"""
Tests for jarvis_core.audit_agent.context — classify_context().

Covers all six categories, edge cases, and the fp_prior contract.
All tests are pure-Python with no I/O, no LLM, no subprocess.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from jarvis_core.audit_agent.context import (
    CATEGORY_BUILD,
    CATEGORY_CONFIG_LOCAL,
    CATEGORY_DOCUMENTATION,
    CATEGORY_EXAMPLE,
    CATEGORY_SOURCE,
    CATEGORY_TEST,
    FindingContext,
    classify_context,
)


# ── Helpers ────────────────────────────────────────────────────────────────────


def _cat(path: str | None) -> str:
    return classify_context(path).category


def _ctx(path: str | None) -> FindingContext:
    return classify_context(path)


# ── Test category: test ────────────────────────────────────────────────────────


class TestTestCategory:
    def test_tests_directory(self):
        assert _cat("tests/auth/test_login.py") == CATEGORY_TEST

    def test_dunder_tests_directory(self):
        assert _cat("lib/__tests__/razorpay.test.ts") == CATEGORY_TEST

    def test_spec_directory(self):
        assert _cat("spec/fixtures/payment_fixture.rb") == CATEGORY_TEST

    def test_go_test_file(self):
        assert _cat("pkg/auth/auth_test.go") == CATEGORY_TEST

    def test_jest_test_file(self):
        assert _cat("src/__tests__/auth.test.js") == CATEGORY_TEST

    def test_vitest_spec_file(self):
        assert _cat("components/Button.spec.tsx") == CATEGORY_TEST

    def test_pytest_conftest(self):
        """conftest.py is not a test by name-pattern but often in tests/ dir."""
        assert _cat("tests/conftest.py") == CATEGORY_TEST

    def test_test_prefix_in_filename(self):
        assert _cat("app/test_utils.py") == CATEGORY_TEST

    def test_integration_dir(self):
        assert _cat("tests/integration/test_db.py") == CATEGORY_TEST

    def test_fp_prior_is_high(self):
        ctx = _ctx("tests/test_secrets.py")
        assert ctx.fp_prior >= 0.85

    def test_rationale_is_non_empty(self):
        ctx = _ctx("__tests__/payment.test.ts")
        assert len(ctx.rationale) > 5


# ── Test category: documentation ──────────────────────────────────────────────


class TestDocumentationCategory:
    def test_markdown_file(self):
        assert _cat("content/getting-started.md") == CATEGORY_DOCUMENTATION

    def test_mdx_file(self):
        assert _cat("content/docs/api-reference.mdx") == CATEGORY_DOCUMENTATION

    def test_rst_file(self):
        assert _cat("docs/configuration.rst") == CATEGORY_DOCUMENTATION

    def test_readme_md(self):
        assert _cat("README.md") == CATEGORY_DOCUMENTATION

    def test_changelog_md(self):
        assert _cat("CHANGELOG.md") == CATEGORY_DOCUMENTATION

    def test_docs_dir_non_md(self):
        """A .yaml file inside docs/ should be documentation context."""
        assert _cat("docs/openapi.yaml") == CATEGORY_DOCUMENTATION

    def test_wiki_dir(self):
        assert _cat("wiki/setup.md") == CATEGORY_DOCUMENTATION

    def test_fp_prior_is_very_high(self):
        ctx = _ctx("docs/auth.md")
        assert ctx.fp_prior >= 0.88

    def test_blog_dir(self):
        assert _cat("blog/post-2026-01.md") == CATEGORY_DOCUMENTATION


# ── Test category: example ────────────────────────────────────────────────────


class TestExampleCategory:
    def test_env_example(self):
        assert _cat(".env.example") == CATEGORY_EXAMPLE

    def test_env_sample(self):
        assert _cat(".env.sample") == CATEGORY_EXAMPLE

    def test_env_template(self):
        assert _cat(".env.template") == CATEGORY_EXAMPLE

    def test_example_dir(self):
        assert _cat("examples/basic/config.json") == CATEGORY_EXAMPLE

    def test_fixtures_dir(self):
        # "fixtures" is in _TEST_SEGMENTS → classified as test (test wins over example)
        # because test check runs first. This is the correct behavior: fixtures are
        # test-context by convention.
        assert _cat("fixtures/user_data.json") == CATEGORY_TEST

    def test_mock_dir(self):
        assert _cat("mocks/api_response.json") == CATEGORY_EXAMPLE

    def test_demo_dir(self):
        assert _cat("demo/sample_app.py") == CATEGORY_EXAMPLE

    def test_example_in_filename_stem(self):
        assert _cat("config/example.config.json") == CATEGORY_EXAMPLE

    def test_sample_in_filename_stem(self):
        assert _cat("scripts/sample_migration.sql") == CATEGORY_EXAMPLE

    def test_fp_prior_is_high(self):
        ctx = _ctx(".env.example")
        assert ctx.fp_prior >= 0.85


# ── Test category: config_local ───────────────────────────────────────────────


class TestConfigLocalCategory:
    def test_env_local(self):
        assert _cat(".env.local") == CATEGORY_CONFIG_LOCAL

    def test_env_development(self):
        assert _cat(".env.development") == CATEGORY_CONFIG_LOCAL

    def test_env_development_local(self):
        assert _cat(".env.development.local") == CATEGORY_CONFIG_LOCAL

    def test_env_production_local(self):
        assert _cat(".env.production.local") == CATEGORY_CONFIG_LOCAL

    def test_fp_prior_is_moderate(self):
        """config_local is REAL but dev-scoped — moderate fp_prior, not high."""
        ctx = _ctx(".env.local")
        assert 0.25 <= ctx.fp_prior <= 0.50

    def test_plain_dotenv_is_source(self):
        """A plain .env (not .env.local) should fall through to source — it's a real secret."""
        assert _cat(".env") == CATEGORY_SOURCE

    def test_env_override(self):
        assert _cat(".env.override") == CATEGORY_CONFIG_LOCAL


# ── Test category: build ──────────────────────────────────────────────────────


class TestBuildCategory:
    def test_node_modules(self):
        assert _cat("node_modules/some-lib/constants.js") == CATEGORY_BUILD

    def test_dist_directory(self):
        assert _cat("dist/bundle.min.js") == CATEGORY_BUILD

    def test_build_directory(self):
        assert _cat("build/Release/app.node") == CATEGORY_BUILD

    def test_vendor_directory(self):
        assert _cat("vendor/github.com/aws/sdk.go") == CATEGORY_BUILD

    def test_pycache(self):
        assert _cat("jarvis_core/__pycache__/config.cpython-312.pyc") == CATEGORY_BUILD

    def test_next_directory(self):
        assert _cat(".next/server/pages/index.js") == CATEGORY_BUILD

    def test_fp_prior_is_high(self):
        ctx = _ctx("node_modules/pkg/lib.js")
        assert ctx.fp_prior >= 0.85

    def test_coverage_directory(self):
        assert _cat("coverage/lcov.info") == CATEGORY_BUILD


# ── Test category: source (the safe default) ──────────────────────────────────


class TestSourceCategory:
    def test_production_python(self):
        assert _cat("app/auth/jwt_utils.py") == CATEGORY_SOURCE

    def test_production_typescript(self):
        assert _cat("src/api/routes.ts") == CATEGORY_SOURCE

    def test_production_go(self):
        assert _cat("pkg/db/postgres.go") == CATEGORY_SOURCE

    def test_plain_env_file(self):
        """A committed .env is a real secret — must stay as source."""
        assert _cat(".env") == CATEGORY_SOURCE

    def test_config_json_is_source(self):
        assert _cat("config/production.json") == CATEGORY_SOURCE

    def test_none_path_is_source(self):
        assert _cat(None) == CATEGORY_SOURCE

    def test_empty_path_is_source(self):
        assert _cat("") == CATEGORY_SOURCE

    def test_fp_prior_is_low(self):
        ctx = _ctx("src/config/aws.py")
        assert ctx.fp_prior <= 0.15

    def test_windows_path_normalised(self):
        """Windows backslash paths should be normalised to forward-slash."""
        assert _cat("src\\api\\routes.ts") == CATEGORY_SOURCE

    def test_deeply_nested_source_file(self):
        assert _cat("app/services/payment/stripe/client.py") == CATEGORY_SOURCE


# ── Edge cases + return contract ──────────────────────────────────────────────


class TestEdgeCases:
    def test_returns_finding_context_dataclass(self):
        ctx = classify_context("src/main.py")
        assert isinstance(ctx, FindingContext)
        assert hasattr(ctx, "category")
        assert hasattr(ctx, "fp_prior")
        assert hasattr(ctx, "rationale")

    def test_fp_prior_is_between_0_and_1(self):
        for path in [
            "tests/test_a.py", "docs/guide.md", ".env.example",
            ".env.local", "dist/app.js", "src/app.py", None, "",
        ]:
            ctx = classify_context(path)
            assert 0.0 <= ctx.fp_prior <= 1.0, f"fp_prior out of range for {path!r}"

    def test_category_is_valid_string(self):
        valid = {CATEGORY_TEST, CATEGORY_DOCUMENTATION, CATEGORY_EXAMPLE,
                 CATEGORY_CONFIG_LOCAL, CATEGORY_BUILD, CATEGORY_SOURCE}
        for path in [
            "tests/test_a.py", "docs/guide.md", ".env.example",
            ".env.local", "dist/app.js", "src/app.py",
        ]:
            ctx = classify_context(path)
            assert ctx.category in valid, f"Unknown category {ctx.category!r} for {path!r}"

    def test_deterministic_same_input_same_output(self):
        """classify_context is pure — repeated calls return identical results."""
        path = "src/__tests__/payment.test.js"
        ctx1 = classify_context(path)
        ctx2 = classify_context(path)
        assert ctx1 == ctx2

    def test_test_takes_precedence_over_source_for_test_dir(self):
        """Even a .py file in tests/ is test, not source."""
        assert _cat("tests/auth_utils.py") == CATEGORY_TEST

    def test_doc_extension_takes_precedence_over_src_dir(self):
        """A .md file in src/ is still documentation."""
        assert _cat("src/API.md") == CATEGORY_DOCUMENTATION

    def test_build_takes_precedence_over_example(self):
        """node_modules wins over a 'demo' segment deeper in the path."""
        assert _cat("node_modules/demo-pkg/demo.js") == CATEGORY_BUILD
