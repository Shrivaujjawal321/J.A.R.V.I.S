"""VULCAN · Alerts — real-time condition-monitoring feed (FR7).

Replays a real asset's dense sensor stream row-by-row through the deterministic
threshold detector (LLM-free) and shows the escalation WARNING → ALARM →
CRITICAL. On the autonomous CRITICAL trip, EDITH hands off to the agentic core
for an explainable diagnosis + recommended action + spare lead-time.

The detector path never calls a model, so the live feed can never stall. The
agentic diagnosis hand-off is a single, separate, guarded call (toggle below).
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parents[3]
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))
os.environ.pop("ANTHROPIC_API_KEY", None)

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from vulcan.ui import _shared as S  # noqa: E402


def main() -> None:
    S.page_setup("Real-Time Alerts", icon="🚨")
    st.markdown("### 🚨 Real-time alerting — autonomous condition monitoring (FR7)")
    st.caption(
        "Deterministic threshold detector replays a real per-asset sensor stream "
        "and fires the instant a reading crosses its ISO/ISA spine threshold. On a "
        "sustained alarm (CRITICAL) it escalates autonomously and triggers EDITH's "
        "explainable diagnosis — no engineer input required."
    )

    from vulcan.alerting import DEMO_EPISODES

    # ---- recent persisted alerts strip ----
    _recent_alerts_strip()

    st.divider()

    # ---- episode picker + controls ----
    episodes = list(DEMO_EPISODES.keys())
    labels = {k: f"{k} — {DEMO_EPISODES[k].get('title', k)}" for k in episodes}
    c1, c2, c3 = st.columns([3, 1.2, 1.4])
    with c1:
        asset_id = st.selectbox("Demo episode", episodes,
                                format_func=lambda k: labels[k])
    with c2:
        animate = st.toggle("Animate", value=True,
                            help="Step the escalation live (slower, more dramatic)")
    with c3:
        handoff = st.toggle("Agentic diagnosis", value=False,
                            help="Hand off the CRITICAL trip to EDITH for an "
                                 "explainable diagnosis (1 LLM call; off = fast).")

    spec = DEMO_EPISODES[asset_id]
    st.info(spec.get("narrative", ""), icon="📈")

    if st.button("▶ Replay sensor stream", type="primary", width="stretch"):
        _run_episode(asset_id, animate=animate, handoff=handoff)


def _recent_alerts_strip() -> None:
    """Show the most-recent persisted alerts (the live feed history)."""
    try:
        from vulcan.alerting.store import get_alert_store
        store = get_alert_store()
        recent = store.recent(limit=8) if hasattr(store, "recent") else []
    except Exception:  # noqa: BLE001
        recent = []
    st.markdown("#### Recent fired alerts (persisted)")
    if not recent:
        st.caption("_No alerts on record yet — run an episode below to populate the feed._")
        return
    df = pd.DataFrame(recent)
    keep = [c for c in ["ts", "asset_id", "sensor", "value", "severity",
                        "alarm_threshold", "scenario_id", "reason"] if c in df.columns]
    st.dataframe(df[keep] if keep else df, width="stretch", hide_index=True)


def _run_episode(asset_id: str, *, animate: bool, handoff: bool) -> None:
    from vulcan.alerting import Severity, replay_episode

    timeline_box = st.empty()
    status_box = st.empty()
    seen: list[dict] = []
    sev_now = {"v": "NORMAL"}

    def _on_event(ev) -> None:
        seen.append({
            "Severity": ev.severity.label, "Sensor": ev.sensor,
            "Value": ev.value, "Alarm@": ev.alarm_threshold,
            "Row": ev.row_index, "Trigger": ev.reason,
        })
        if int(ev.severity) >= int(getattr(Severity, sev_now["v"], Severity.NORMAL)):
            sev_now["v"] = ev.severity.label
        color = S.SEVERITY_COLORS.get(ev.severity.label, "#94A3B8")
        status_box.markdown(
            f"<div style='font-family:IBM Plex Mono,monospace;color:{color};'>"
            f"▮ {ev.severity.label} — {ev.sensor} = {ev.value} (row {ev.row_index})</div>",
            unsafe_allow_html=True,
        )
        timeline_box.dataframe(pd.DataFrame(seen), width="stretch", hide_index=True)
        if animate:
            time.sleep(0.04)

    with st.spinner("Streaming sensor data through the detector…"):
        ep = replay_episode(asset_id, handoff=handoff, run_gate=False,
                            on_event=_on_event if animate else None)
        if not animate and ep.events:
            # render the full timeline at once
            for ev in ep.events[:200]:
                _on_event(ev)

    # ---- the autonomous CRITICAL banner ----
    if ep.fired and ep.first_critical is not None:
        fc = ep.first_critical
        st.markdown(
            f"""
            <div style="background:#2a0c12;border:1px solid #F43F5E;border-radius:14px;
                        padding:1rem 1.2rem;margin-top:.8rem;">
              <div style="color:#F43F5E;font-weight:700;font-family:IBM Plex Mono,monospace;
                          font-size:1.05rem;">🔴 AUTONOMOUS CRITICAL TRIP — {ep.asset_id}</div>
              <div style="margin-top:.3rem;">{S._esc(ep.title)}</div>
              <div style="margin-top:.4rem;font-family:IBM Plex Mono,monospace;font-size:.85rem;">
                {S._esc(fc.sensor)} = <b>{fc.value}{fc.unit or ''}</b>
                (alarm {fc.alarm_threshold}{fc.unit or ''}) · row {fc.row_index}
                · ground-truth fault_label {fc.fault_label}
              </div>
              <div style="margin-top:.3rem;font-size:.82rem;color:#cbb;">{S._esc(fc.reason)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.warning("No CRITICAL fired in this window (detector behaved nominally).")
        return

    # ---- escalation milestones ----
    st.markdown("#### Escalation timeline (deterministic, LLM-free)")
    tl = ep.severity_timeline()
    if tl:
        st.dataframe(pd.DataFrame(tl), width="stretch", hide_index=True)

    # ---- the agentic diagnosis hand-off (FR4) ----
    if ep.diagnosis:
        d = ep.diagnosis
        st.markdown("#### 🧠 EDITH autonomous diagnosis (agentic hand-off)")
        cc = st.columns([1, 1.2, 2])
        cc[0].markdown("**Risk**  \n" + S.risk_badge(d.get("risk_band")), unsafe_allow_html=True)
        rul = d.get("rul") or {}
        cc[1].markdown(
            f"**RUL**  \n`{rul.get('rul_cycles')}` cyc (~{rul.get('rul_days_estimate')} d)"
            if rul.get("rul_cycles") is not None else "**RUL**  \n_n/a_"
        )
        cc[2].markdown(f"**Confidence**  \n{d.get('confidence','?')} · rung {d.get('llm_rung','?')}")
        st.markdown(d.get("answer", "_no diagnosis_"))
        S.render_citations(d.get("sources", []))
        trace = d.get("trace")
        if trace:
            with st.expander("🧠 Show EDITH's reasoning (trace + sources)"):
                from vulcan.ui.app import _TraceView  # reuse the chat adapter
                S.render_trace(_TraceView(trace))
    elif handoff:
        st.caption("_Agentic diagnosis hand-off returned nothing (model offline) — "
                   "the detector still fired autonomously._")
    else:
        st.caption("_Agentic diagnosis toggle is off — enable it to see EDITH's "
                   "explainable diagnosis for this trip._")


main()
