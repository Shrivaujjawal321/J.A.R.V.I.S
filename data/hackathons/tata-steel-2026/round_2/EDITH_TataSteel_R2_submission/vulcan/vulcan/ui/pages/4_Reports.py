"""VULCAN · Reports — view & generate structured maintenance reports (FR4).

Three grounded, dataset-cited builders:
  • Incident report  — full diagnosis / RCA / RUL / risk / actions / procurement / cost
  • Decision card    — 10-second action card (band · next action · order-now part)
  • Alert report     — from a fired alerting episode (escalation + autonomous diagnosis)

Generation runs the agentic core once to ground the report, then renders the
deterministic Markdown. Existing reports on disk are browsable + downloadable.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parents[3]
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))
os.environ.pop("ANTHROPIC_API_KEY", None)

import streamlit as st  # noqa: E402

from vulcan.ui import _shared as S  # noqa: E402


def _reports_dir() -> Path:
    from vulcan.config import get_settings
    d = get_settings().package_root / "data" / "reports"
    d.mkdir(parents=True, exist_ok=True)
    return d


def main() -> None:
    S.page_setup("Reports", icon="📄")
    st.markdown("### 📄 Structured maintenance reports")
    st.caption(
        "Every figure traces to a dataset source (spine · SOP · spare catalog · ML "
        "artifact). Generation grounds the report through the agentic core; missing "
        "values render explicitly as 'not available' — never fabricated."
    )

    tab_gen, tab_browse = st.tabs(["⚙️ Generate", "📁 Browse saved"])

    with tab_gen:
        _generate_tab()
    with tab_browse:
        _browse_tab()


def _generate_tab() -> None:
    assets = S.fleet_assets()
    ids = [a["asset_id"] for a in assets]

    c1, c2, c3 = st.columns([2, 2, 1.4])
    with c1:
        asset_id = st.selectbox("Asset", ids, index=0)
    with c2:
        kind = st.selectbox("Report type",
                            ["Incident report", "Decision card"])
    with c3:
        save = st.toggle("Save to disk", value=True)

    # optional scenario hint
    from vulcan.tools import data_tools as T
    scns = T.get_scenarios_for_asset(asset_id).get("scenarios", [])
    scn_opts = ["(auto — let EDITH match)"] + [
        f"{s['scenario_id']} · {s['failure_mode']}" for s in scns]
    scn_pick = st.selectbox("Scenario", scn_opts, index=0)
    scenario_id = None if scn_pick.startswith("(auto") else scn_pick.split(" · ")[0]

    if st.button("⚙️ Generate report", type="primary", width="stretch"):
        _do_generate(asset_id, scenario_id, kind, save)


def _do_generate(asset_id: str, scenario_id, kind: str, save: bool) -> None:
    try:
        from vulcan.reports import incident_report, decision_summary, save_report
        with st.spinner("Grounding report through EDITH…"):
            if kind == "Incident report":
                rep = incident_report(asset_id, scenario_id, run_gate=False)
            else:
                rep = decision_summary(asset_id, scenario_id)
        st.success(f"Generated `{rep.report_id}` — {rep.title}")
        if save:
            path = save_report(rep)
            st.caption(f"Saved → {path}")
        st.download_button("⬇ Download Markdown", rep.markdown,
                           file_name=f"{rep.report_id}.md", mime="text/markdown")
        st.divider()
        st.markdown(rep.markdown)
    except Exception as exc:  # noqa: BLE001
        st.error("Report generation hit a snag — the agentic core may be offline. "
                 "The deterministic floor still grounds the figures; please retry.",
                 icon="⚠️")
        st.caption(f"(internal: {type(exc).__name__}: {exc})")


def _browse_tab() -> None:
    d = _reports_dir()
    files = sorted(d.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        st.caption("_No saved reports yet — generate one in the first tab._")
        return
    names = [p.name for p in files]
    pick = st.selectbox("Saved reports (newest first)", names, index=0)
    p = d / pick
    try:
        text = p.read_text(encoding="utf-8")
    except OSError as exc:
        st.error(f"Could not read {pick}: {exc}")
        return
    st.download_button("⬇ Download", text, file_name=pick, mime="text/markdown")
    st.divider()
    st.markdown(text)


main()
