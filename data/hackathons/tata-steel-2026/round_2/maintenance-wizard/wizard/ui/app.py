"""
wizard.ui.app
=============
Streamlit 1.58 multipage entry point for Maintenance Wizard.

Run with:
    streamlit run wizard/ui/app.py

Architecture:
- st.navigation() defines the 5-page structure (Streamlit 1.28+ multipage API)
- Sidebar: shared cost-avoidance ticker (st.fragment run_every=5)
- Sidebar: alert badge counter (st.fragment run_every=3)
- Per-session demo data seeded once via _demo_seed.ensure_demo_seed()
- HTTP client singleton created once per session via _http.get_client()

CRITICAL: httpx.Client (sync) ONLY — never AsyncClient.
"""

from __future__ import annotations

import streamlit as st

# ---- page config MUST be first Streamlit call ----
st.set_page_config(
    page_title="Maintenance Wizard — Tata Steel AI",
    page_icon=":material/build:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": (
            "**Maintenance Wizard** — Tata Steel AI Hackathon 2026 Round 2.\n\n"
            "Agentic maintenance co-pilot for steel-plant engineers.\n\n"
            "Stack: LangGraph 1.2 · FastAPI 0.136 · Streamlit 1.58 · "
            "LanceDB · WeibullAFT · Gemini 2.5 Flash"
        )
    },
)

# ---- inject design-system CSS ----
from wizard.ui._ui import inject_global_css
inject_global_css()

# ---- seed demo data (idempotent) ----
from wizard.ui._demo_seed import ensure_demo_seed
ensure_demo_seed()

# ---- page definitions ----
pages = [
    st.Page("views/01_Chat.py",      title="Maintenance Chat",  icon=":material/chat:",       default=True),
    st.Page("views/02_Dashboard.py", title="Equipment Health",  icon=":material/dashboard:"),
    st.Page("views/03_Alerts.py",    title="Active Alerts",     icon=":material/warning:"),
    st.Page("views/04_Logbook.py",   title="Logbook",           icon=":material/history:"),
    # System Settings page removed — system-health/demo-controls are not a
    # problem-statement requirement and the demo controls reveal scaffolding.
    # The /v1/demo/inject_fault backend endpoint stays for the recording.
]

# ---- sidebar ----
with st.sidebar:
    st.markdown(
        "<p style='font-size:0.875rem;font-weight:700;color:#E8E8F2;"
        "margin:0 0 2px;letter-spacing:-0.01em;'>Maintenance Wizard</p>"
        "<p style='font-size:0.6875rem;color:#5E6080;margin:0;'>"
        "Tata Steel — Equipment Intelligence</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    # --- LIVE COST-AVOIDANCE TICKER (st.fragment run_every=5) ---
    @st.fragment(run_every=5)
    def cost_ticker() -> None:
        """
        Accumulates prevented-downtime cost across the demo session.
        Increments only on CRITICAL/HIGH events via avoided_hours x Rs 75,000/hr.
        Polls /v1/session/cost-events every 5 seconds.
        """
        from wizard.ui._http import safe_get
        from wizard.ui._demo_seed import append_cost_event

        # Pull new cost events from backend (if up)
        events_resp = safe_get("/v1/session/cost-events")
        if events_resp and isinstance(events_resp, list):
            seen_ids = st.session_state.get("seen_alert_ids", set())
            for ev in events_resp:
                aid = ev.get("alert_id", "")
                if aid not in seen_ids:
                    seen_ids.add(aid)
                    append_cost_event(
                        alert_id=aid,
                        equipment=ev.get("equipment", "Unknown"),
                        severity=ev.get("severity", ""),
                        prevented_hours=float(ev.get("prevented_hours", 0)),
                    )
            st.session_state["seen_alert_ids"] = seen_ids

        total = st.session_state.get("total_cost_avoidance_inr", 0.0)
        delta = st.session_state.get("last_cost_delta_inr", 0.0)

        st.metric(
            label="Cost Avoidance",
            value=f"₹{total:,.0f}",
            delta=f"+₹{delta:,.0f}" if delta > 0 else None,
            help=(
                "Accumulated cost avoidance this session.\n\n"
                "Formula: avoided_hours x Rs 75,000/hr\n\n"
                "Triggers: CRITICAL and HIGH alerts only.\n\n"
                "Rate source: Tata Steel rolling-mill deployment analysis "
                "(Rs 45 Cr/yr per blast furnace); Cypag industry benchmark "
                "($500K/day per blower trip)."
            ),
        )

        n_events = len(st.session_state.get("cost_events", []))
        st.caption(f"{n_events} events  ·  ₹75,000/hr")

    cost_ticker()
    st.divider()

    # --- ACTIVE ALERT BADGE (st.fragment run_every=3) ---
    @st.fragment(run_every=3)
    def alert_badge() -> None:
        """
        Polls /v1/alerts/active every 3 seconds.
        Updates session_state['alerts'] with new arrivals.
        Fires st.toast for new CRITICAL/HIGH alerts.
        """
        from wizard.ui._http import safe_get
        from wizard.ui._demo_seed import append_cost_event

        raw_resp = safe_get("/v1/alerts", params={"limit": 50})
        # Backend returns AlertListResponse: {items: [...], total, next_cursor}
        if raw_resp and isinstance(raw_resp, dict):
            resp_items = raw_resp.get("items", [])
        elif raw_resp and isinstance(raw_resp, list):
            resp_items = raw_resp
        else:
            resp_items = []

        if resp_items:
            seen_ids = st.session_state.get("seen_alert_ids", set())
            existing_alerts = st.session_state.get("alerts", [])
            existing_ids = {a["alert_id"] for a in existing_alerts}

            for raw_alert in resp_items:
                # Normalise alert_entity_id -> alert_id; risk_level -> severity
                alert = dict(raw_alert)
                aid = raw_alert.get("alert_entity_id") or raw_alert.get("alert_id", "")
                if not aid:
                    continue
                alert["alert_id"] = aid
                sev = (raw_alert.get("severity") or raw_alert.get("risk_level") or "LOW").upper()
                alert["severity"] = sev

                if aid not in seen_ids:
                    seen_ids.add(aid)
                    if aid not in existing_ids:
                        existing_alerts.insert(0, alert)
                        existing_ids.add(aid)
                        sev = alert.get("severity", "").upper()
                        toast_icon = ":material/error:" if sev == "CRITICAL" else ":material/warning:"
                        st.toast(
                            f"[{sev}] {alert.get('equipment_name', alert.get('asset_id', ''))}",
                            icon=toast_icon,
                        )
                        # Credit cost ticker for CRITICAL/HIGH
                        rul_days = alert.get("estimated_rul_days")
                        if rul_days is not None and sev in ("CRITICAL", "HIGH"):
                            prevented_hours = min(float(rul_days) * 24, 8.0)
                            append_cost_event(
                                alert_id=aid,
                                equipment=alert.get("equipment_name", alert.get("asset_id", "")),
                                severity=sev,
                                prevented_hours=prevented_hours,
                            )

            st.session_state["alerts"] = existing_alerts
            st.session_state["seen_alert_ids"] = seen_ids

        # Count unacknowledged
        alerts = st.session_state.get("alerts", [])
        unacked = sum(1 for a in alerts if not a.get("acknowledged", False))
        critical_n = sum(
            1 for a in alerts
            if not a.get("acknowledged", False)
            and a.get("severity", "").upper() == "CRITICAL"
        )

        if critical_n > 0:
            st.markdown(
                f"<div style='border-left:4px solid #F87171;padding:6px 10px;"
                f"background:#450A0A;border-radius:4px;font-size:0.8125rem;"
                f"color:#FCA5A5;font-weight:600;'>"
                f"Critical: {critical_n}  ·  {unacked} active</div>",
                unsafe_allow_html=True,
            )
        elif unacked > 0:
            st.markdown(
                f"<div style='border-left:4px solid #FBBF24;padding:6px 10px;"
                f"background:#422006;border-radius:4px;font-size:0.8125rem;"
                f"color:#FDE68A;font-weight:600;'>Warning: {unacked} active</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div style='border-left:2px solid #334155;padding:6px 10px;"
                "font-size:0.8125rem;color:#94A3B8;'>No active alerts</div>",
                unsafe_allow_html=True,
            )

    alert_badge()
    st.divider()

    # Active session info — styled chips readable on dark sidebar
    session_id = st.session_state.get("session_id", "—")
    short_sid = (session_id[:12] + "...") if len(session_id) > 12 else session_id
    st.markdown(
        f"<div style='display:flex;flex-direction:column;gap:4px;margin-top:2px;'>"
        f"<span style='font-size:0.6875rem;font-weight:500;color:#9B9CB5;"
        f"background:#161B27;border:1px solid rgba(255,255,255,0.07);border-radius:4px;"
        f"padding:2px 8px;font-family:IBM Plex Mono,monospace;'>"
        f"Session: {short_sid}</span>"
        f"<span style='font-size:0.6875rem;font-weight:600;color:#34D399;"
        f"background:rgba(52,211,153,0.10);border:1px solid rgba(52,211,153,0.20);"
        f"border-radius:4px;padding:2px 8px;'>Backend  :8000</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

# ---- run navigation ----
pg = st.navigation(pages)
pg.run()
