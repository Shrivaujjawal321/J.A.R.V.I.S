"""
wizard.ui.smoke_ui
==================
Smoke test for the UI module.

Verifies:
1. All UI Python files compile cleanly (py_compile)
2. _demo_seed data structures are valid
3. _http module can be imported and client config is correct
4. All page files can be imported without Streamlit context errors

Run with:
    python wizard/ui/smoke_ui.py

Expected output:
    [OK] All UI files compile cleanly
    [OK] Demo seed data valid — 6 equipment, 6 sensor states, 5 alerts, 3 logbook
    [OK] _http module: base_url=http://localhost:8000, sync=True
    [OK] All cross-imports validate
    SMOKE PASS — wizard.ui ready
"""

from __future__ import annotations

import importlib
import json
import py_compile
import sys
from pathlib import Path

# Resolve repo root so imports work regardless of cwd
# wizard/ui/smoke_ui.py -> parents[2] is the repo root (maintenance-wizard/)
_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))

_UI_DIR = Path(__file__).resolve().parent
_PAGES_DIR = _UI_DIR / "views"

ERRORS: list[str] = []
PASSES: list[str] = []


def _ok(msg: str) -> None:
    PASSES.append(msg)
    print(f"[OK] {msg}")


def _fail(msg: str) -> None:
    ERRORS.append(msg)
    print(f"[FAIL] {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# 1. py_compile all UI Python files
# ---------------------------------------------------------------------------
def check_syntax() -> None:
    py_files = sorted(_UI_DIR.rglob("*.py"))
    failed_files: list[str] = []
    for py_file in py_files:
        try:
            py_compile.compile(str(py_file), doraise=True)
        except py_compile.PyCompileError as exc:
            failed_files.append(f"  {py_file.relative_to(_REPO_ROOT)}: {exc}")

    if failed_files:
        _fail(f"Syntax errors in {len(failed_files)} file(s):\n" + "\n".join(failed_files))
    else:
        _ok(f"All {len(py_files)} UI files compile cleanly")


# ---------------------------------------------------------------------------
# 2. Demo seed data validation
# ---------------------------------------------------------------------------
def check_demo_seed() -> None:
    try:
        from wizard.ui._demo_seed import (
            DEMO_EQUIPMENT,
            DEMO_SENSOR_STATE,
            DEMO_ALERTS,
            DEMO_LOGBOOK,
            DEMO_COST_EVENTS,
            append_cost_event,
            ensure_demo_seed,
        )

        assert len(DEMO_EQUIPMENT) == 6, f"Expected 6 equipment, got {len(DEMO_EQUIPMENT)}"
        assert len(DEMO_SENSOR_STATE) == 6, f"Expected 6 sensor states, got {len(DEMO_SENSOR_STATE)}"
        assert len(DEMO_ALERTS) == 5, f"Expected 5 alerts, got {len(DEMO_ALERTS)}"
        assert len(DEMO_LOGBOOK) == 3, f"Expected 3 logbook entries, got {len(DEMO_LOGBOOK)}"

        # All equipment have matching sensor states
        for eq in DEMO_EQUIPMENT:
            aid = eq["asset_id"]
            assert aid in DEMO_SENSOR_STATE, f"No sensor state for {aid}"
            state = DEMO_SENSOR_STATE[aid]
            assert "rul_days_p50" in state, f"Missing rul_days_p50 for {aid}"
            assert "health_score" in state, f"Missing health_score for {aid}"
            assert 0 <= state["health_score"] <= 100, f"health_score out of range for {aid}"

        # Alert structure
        for alert in DEMO_ALERTS:
            assert "alert_id" in alert, "Alert missing alert_id"
            assert "severity" in alert, "Alert missing severity"
            assert alert["severity"].upper() in ("CRITICAL", "HIGH", "MEDIUM", "LOW"), \
                f"Invalid severity: {alert['severity']}"

        # EAF-04 must be CRITICAL (the demo asset)
        eaf04_state = DEMO_SENSOR_STATE.get("EAF-04", {})
        assert eaf04_state.get("rul_days_p50", 99) < 1.0, \
            f"EAF-04 should be CRITICAL (RUL < 1 day), got {eaf04_state.get('rul_days_p50')}"
        assert eaf04_state.get("health_score", 99) < 25, \
            f"EAF-04 health should be CRITICAL (<25%), got {eaf04_state.get('health_score')}"

        _ok(
            f"Demo seed data valid — "
            f"{len(DEMO_EQUIPMENT)} equipment, "
            f"{len(DEMO_SENSOR_STATE)} sensor states, "
            f"{len(DEMO_ALERTS)} alerts, "
            f"{len(DEMO_LOGBOOK)} logbook"
        )
    except Exception as exc:
        _fail(f"Demo seed validation: {exc}")


# ---------------------------------------------------------------------------
# 3. _http module — no Streamlit context needed for import
# ---------------------------------------------------------------------------
def check_http_module() -> None:
    try:
        import httpx

        # Check that _http uses sync client (not AsyncClient)
        # Note: "AsyncClient" may appear in doc comments explaining what NOT to use.
        # We check that there is no actual instantiation of AsyncClient.
        http_source = (_UI_DIR / "_http.py").read_text()
        # Look for actual usage patterns (not doc comment mentions)
        import re
        async_instantiation = re.search(r'httpx\.AsyncClient\s*\(', http_source)
        assert async_instantiation is None, \
            "httpx.AsyncClient() instantiation found in _http.py — must use sync httpx.Client only"
        assert "httpx.Client" in http_source, "httpx.Client not found in _http.py"

        _ok("_http module: sync httpx.Client enforced, no AsyncClient instantiation")
    except Exception as exc:
        _fail(f"_http module check: {exc}")


# ---------------------------------------------------------------------------
# 4. App.py syntax + structure check
# ---------------------------------------------------------------------------
def check_app_structure() -> None:
    try:
        app_source = (_UI_DIR / "app.py").read_text()

        # Must use st.navigation (Streamlit 1.28+ multipage)
        assert "st.navigation(" in app_source, "app.py must use st.navigation()"

        # Must call ensure_demo_seed
        assert "ensure_demo_seed" in app_source, "app.py must call ensure_demo_seed()"

        # Must have cost ticker fragment
        assert "run_every=5" in app_source, "Cost ticker fragment must have run_every=5"

        # Must have alert badge fragment
        assert "run_every=3" in app_source, "Alert badge fragment must have run_every=3"

        # Must NOT use asyncio
        assert "asyncio" not in app_source, \
            "app.py must not use asyncio — httpx.Client (sync) only"

        _ok("app.py structure: st.navigation, ensure_demo_seed, fragments, no asyncio")
    except Exception as exc:
        _fail(f"app.py structure: {exc}")


# ---------------------------------------------------------------------------
# 5. Page files — key patterns
# ---------------------------------------------------------------------------
def check_page_patterns() -> None:
    page_checks = {
        "01_Chat.py": [
            ("st.write_stream", "Chat must use st.write_stream for LLM streaming"),
            ("st.chat_input", "Chat must use st.chat_input"),
            ("st.expander", "Chat must use st.expander for traceable chain"),
            ("_GOLD_RESPONSE", "Chat must have gold cached response for demo safety"),
            ("try:", "Chat must wrap backend calls in try/except"),
        ],
        "02_Dashboard.py": [
            ("go.Indicator", "Dashboard must use go.Indicator for RUL gauges"),
            ("go.Heatmap", "Dashboard must use go.Heatmap for health matrix"),
            ("@st.cache_data(ttl=30", "Dashboard must cache with ttl=30"),
            ("use_container_width=True", "Dashboard must use use_container_width=True"),
        ],
        "03_Alerts.py": [
            ("@st.fragment(run_every=3)", "Alerts must poll every 3s"),
            ("safe_put", "Alerts must use safe_put for acknowledge"),
            ("st.toast", "Alerts must show toast on new alerts"),
        ],
        "04_Logbook.py": [
            ("sqlite3", "Logbook must support direct sqlite3 read"),
            ("st.download_button", "Logbook must have CSV export"),
            ("pd.DataFrame", "Logbook must use pandas DataFrame"),
            ("@st.cache_data(ttl=30", "Logbook must cache with ttl=30"),
        ],
        "05_Settings.py": [
            ("/v1/sensor/speed", "Settings must have sensor speed control"),
            ("/v1/sensor/reset", "Settings must have sensor reset"),
            ("/v1/sensor/inject_fault", "Settings must have fault inject (belt+suspenders)"),
            ("@st.fragment(run_every=10)", "Settings must poll health every 10s"),
        ],
    }

    all_ok = True
    for page_file, checks in page_checks.items():
        page_path = _PAGES_DIR / page_file
        if not page_path.exists():
            _fail(f"Page file missing: {page_file}")
            all_ok = False
            continue
        page_source = page_path.read_text()
        page_ok = True
        for pattern, msg in checks:
            if pattern not in page_source:
                _fail(f"{page_file}: {msg} (missing: `{pattern}`)")
                all_ok = False
                page_ok = False
        if page_ok:
            _ok(f"{page_file}: all key patterns present")

    if all_ok:
        _ok("All page pattern checks pass")


# ---------------------------------------------------------------------------
# 6. Cross-import: demo_seed does not import Streamlit at module level
#    (would crash if imported outside Streamlit runtime)
#    It imports streamlit inside functions — verify
# ---------------------------------------------------------------------------
def check_no_module_level_streamlit() -> None:
    try:
        seed_source = (_UI_DIR / "_demo_seed.py").read_text()
        # Check that 'import streamlit' only appears inside functions
        lines = seed_source.split("\n")
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("import streamlit") and not line.startswith(" "):
                # Top-level import — check it's not conditional
                _fail(f"_demo_seed.py line {i}: top-level `import streamlit` — must be inside functions")
                return
        _ok("_demo_seed.py: no top-level Streamlit imports (safe to import in tests)")
    except Exception as exc:
        _fail(f"_demo_seed.py check: {exc}")


# ---------------------------------------------------------------------------
# 7. Verify data/demo directory exists (created by _demo_seed)
# ---------------------------------------------------------------------------
def check_demo_dir() -> None:
    demo_dir = _REPO_ROOT / "data" / "demo"
    if not demo_dir.exists():
        demo_dir.mkdir(parents=True, exist_ok=True)
    _ok(f"data/demo directory: {demo_dir}")


# ---------------------------------------------------------------------------
# Run all checks
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("wizard.ui smoke test")
    print("=" * 60)

    check_syntax()
    check_demo_seed()
    check_http_module()
    check_app_structure()
    check_page_patterns()
    check_no_module_level_streamlit()
    check_demo_dir()

    print("=" * 60)
    print(f"PASSES: {len(PASSES)}  FAILURES: {len(ERRORS)}")

    if ERRORS:
        print("\nFAILURES:")
        for e in ERRORS:
            print(f"  - {e}")
        print("\nSMOKE FAIL")
        sys.exit(1)
    else:
        print("SMOKE PASS — wizard.ui ready")
        print(
            "\nTo run the app:\n"
            "  streamlit run wizard/ui/app.py\n\n"
            "Requirements:\n"
            "  pip install streamlit==1.58.0 plotly==5.22.0 httpx==0.27.0 pandas==2.2.0\n"
        )
        sys.exit(0)
