"""
wizard.ui.pages.03_Alerts
==========================
Real-time alert feed with acknowledge workflow.

Features:
- st.fragment run_every=3 polls GET /v1/alerts (paginated, items list) every 3s
- Alert cards: severity badge + equipment name + description + RUL + recommended action
- One-click acknowledge -> POST /v1/alerts/{alert_entity_id}/ack
- Filter by severity (CRITICAL / HIGH / MEDIUM / LOW / All)
- Pre-seeded demo data ensures content on first load
- st.toast on new incoming alerts (fired from app.py sidebar fragment too)

CRITICAL: httpx.Client (sync) ONLY — never asyncio.run().
"""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from wizard.ui._http import safe_get, safe_put, safe_post
from wizard.ui._demo_seed import append_cost_event
from wizard.ui._ui import (
    inject_global_css, status_badge, severity_to_variant, kpi_tile,
    page_header, render_hero_header,
)

inject_global_css()

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
render_hero_header(
    "Active Alerts",
    "Unacknowledged alerts sorted by severity.",
    badge="LIVE · 3s REFRESH",
    accent_color="#F87171",
)

# ---------------------------------------------------------------------------
# Severity display config (no emoji)
# ---------------------------------------------------------------------------
_SEVERITY_CONFIG: dict[str, dict] = {
    "CRITICAL": {"icon": ":material/error:",   "color": "red",    "order": 0},
    "HIGH":     {"icon": ":material/warning:", "color": "orange", "order": 1},
    "MEDIUM":   {"icon": ":material/info:",    "color": "blue",   "order": 2},
    "LOW":      {"icon": ":material/info:",    "color": "green",  "order": 3},
}


def _sev_order(alert: dict) -> int:
    sev = alert.get("severity", "LOW").upper()
    return _SEVERITY_CONFIG.get(sev, {"order": 99})["order"]


# ---------------------------------------------------------------------------
# Filter controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        "<p style='font-size:0.6875rem;font-weight:600;color:#94A3B8;"
        "text-transform:uppercase;letter-spacing:0.06em;margin:0 0 8px;'>Filters</p>",
        unsafe_allow_html=True,
    )
    show_acked = st.checkbox("Include acknowledged", value=False, key="alerts_show_acked")
    sev_filter = st.multiselect(
        "Severity",
        options=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        default=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        key="alerts_sev_filter",
    )


# ---------------------------------------------------------------------------
# Alert poll fragment (run_every=3 — isolated, no full page rerun)
# ---------------------------------------------------------------------------
@st.fragment(run_every=3)
def _alert_poller() -> None:
    """
    Polls GET /v1/alerts (paginated) every 3 seconds.
    Backend returns AlertListResponse: {items: [...], total, next_cursor}.
    AlertListItem uses 'alert_entity_id'; we normalise to 'alert_id' for
    session_state consistency with the demo-seed data.
    Merges new backend alerts into session_state['alerts'].
    Fires st.toast for new CRITICAL/HIGH events.
    """
    try:
        resp = safe_get("/v1/alerts", params={"limit": 50})
    except Exception:
        resp = None

    if resp and isinstance(resp, dict):
        alert_items = resp.get("items", [])
    elif resp and isinstance(resp, list):
        # Defensive: if backend ever returns a plain list
        alert_items = resp
    else:
        alert_items = []

    if alert_items:
        seen_ids: set = st.session_state.get("seen_alert_ids", set())
        existing: list = st.session_state.get("alerts", [])
        existing_ids = {a["alert_id"] for a in existing}

        new_alerts: list[dict] = []
        for raw in alert_items:
            # Normalise alert_entity_id -> alert_id
            aid = raw.get("alert_entity_id") or raw.get("alert_id", "")
            if not aid:
                continue

            # Build a session-state compatible dict
            alert = dict(raw)
            alert["alert_id"] = aid
            # Backend uses 'risk_level' not 'severity' — normalise
            sev = (raw.get("severity") or raw.get("risk_level") or "LOW").upper()
            alert["severity"] = sev

            if aid not in seen_ids:
                seen_ids.add(aid)
                if aid not in existing_ids:
                    new_alerts.append(alert)
                    existing_ids.add(aid)
                    toast_icon = ":material/error:" if sev == "CRITICAL" else ":material/warning:"
                    st.toast(
                        f"[{sev}] {alert.get('equipment_name', alert.get('asset_id', ''))}",
                        icon=toast_icon,
                    )
                    # Credit cost ticker
                    rul_days = alert.get("estimated_rul_days")
                    if rul_days is not None and sev in ("CRITICAL", "HIGH"):
                        prevented_hours = min(float(rul_days) * 24, 8.0)
                        append_cost_event(
                            alert_id=aid,
                            equipment=alert.get("equipment_name", alert.get("asset_id", "")),
                            severity=sev,
                            prevented_hours=prevented_hours,
                        )

        if new_alerts:
            existing = new_alerts + existing
        st.session_state["alerts"] = existing
        st.session_state["seen_alert_ids"] = seen_ids

    # Render summary KPI tiles
    alerts: list[dict] = st.session_state.get("alerts", [])
    unacked = [a for a in alerts if not a.get("acknowledged", False)]
    critical_n = sum(1 for a in unacked if a.get("severity", "").upper() == "CRITICAL")
    high_n = sum(1 for a in unacked if a.get("severity", "").upper() == "HIGH")

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_tile("Critical", str(critical_n), "", "critical" if critical_n > 0 else "idle")
    with c2:
        kpi_tile("High", str(high_n), "", "high" if high_n > 0 else "idle")
    with c3:
        kpi_tile("Total Active", str(len(unacked)), "", "warning" if len(unacked) > 0 else "idle")


_alert_poller()
st.divider()


# ---------------------------------------------------------------------------
# Acknowledge handler
# ---------------------------------------------------------------------------
def _acknowledge_alert(alert_id: str) -> None:
    """
    POST /v1/alerts/{alert_id}/ack (real endpoint, replaces old PUT /acknowledge).
    Optimistically updates session state — no wait for backend.
    """
    # Optimistic update
    alerts: list[dict] = st.session_state.get("alerts", [])
    for a in alerts:
        if a["alert_id"] == alert_id:
            a["acknowledged"] = True
            a["acknowledged_by"] = "engineer"
            a["acknowledged_at"] = datetime.utcnow().isoformat()
            break
    st.session_state["alerts"] = alerts

    # Fire backend (best-effort) — POST /v1/alerts/{id}/ack
    try:
        safe_post(f"/v1/alerts/{alert_id}/ack", {"engineer_id": "engineer"})
    except Exception:
        pass  # Optimistic update already applied; backend failure is non-fatal
    st.toast("Alert acknowledged and moved to logbook.", icon=":material/check_circle:")


# ---------------------------------------------------------------------------
# Relative time formatter
# ---------------------------------------------------------------------------
def _relative_time(iso_str: str) -> str:
    """Return human-readable relative time. Under 24 h -> relative; older -> absolute."""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        # make naive for comparison
        dt_naive = dt.replace(tzinfo=None)
        now = datetime.utcnow()
        diff = now - dt_naive
        seconds = diff.total_seconds()
        if seconds < 60:
            return "just now"
        if seconds < 3600:
            return f"{int(seconds // 60)} min ago"
        if seconds < 86400:
            return f"{int(seconds // 3600)} h ago"
        return dt_naive.strftime("%d %b, %H:%M")
    except Exception:
        return iso_str or "—"


# ---------------------------------------------------------------------------
# Render alert cards
# ---------------------------------------------------------------------------
def _render_alert_card(alert: dict, idx: int) -> None:
    """
    Render a single alert card with severity-colored left border, details,
    and acknowledge button. Pure dark glass card — no st.container(border=True).
    """
    sev = alert.get("severity", "LOW").upper()
    asset_id_val   = alert.get("asset_id", "—")
    equip_name     = alert.get("equipment_name", asset_id_val)
    description    = (alert.get("description", "") or "")[:280]
    rul_days       = alert.get("estimated_rul_days")
    recommended_action = alert.get("recommended_action", "")
    triggered_at   = alert.get("triggered_at", "")
    acknowledged   = alert.get("acknowledged", False)
    cost_inr       = alert.get("cost_avoidance_inr", 0) or 0
    time_str       = _relative_time(triggered_at)
    is_critical    = sev == "CRITICAL"

    _left_colors = {
        "CRITICAL": "#F87171",
        "HIGH":     "#FB923C",
        "MEDIUM":   "#FBBF24",
        "LOW":      "#3B82F6",
    }
    _bg_colors = {
        "CRITICAL": "rgba(248,113,113,0.05)",
        "HIGH":     "rgba(251,146,60,0.05)",
        "MEDIUM":   "rgba(251,191,36,0.04)",
        "LOW":      "rgba(59,130,246,0.04)",
    }
    border_color = _left_colors.get(sev, "#5E6080")
    bg_color     = _bg_colors.get(sev, "rgba(22,27,39,1)")

    variant      = severity_to_variant(sev)
    badge_html   = status_badge(variant, sev.title())
    ack_badge    = (
        f"<span class='mw-badge mw-badge-idle' "
        f"style='margin-left:6px;'>ACK</span>"
    ) if acknowledged else ""

    # RUL urgency line (placeholder comment keeps the HTML block free of blank
    # lines so Streamlit's markdown parser does not leak the closing tags as text)
    rul_html = "<!-- -->"
    if rul_days is not None:
        try:
            rul_h = float(rul_days) * 24
            if rul_h < 24:
                rul_html = (
                    f"<p style='font-size:0.8rem;font-weight:600;"
                    f"color:#F87171;margin:4px 0 0;'>"
                    f"Est. failure: {rul_h:.1f} h</p>"
                )
            elif float(rul_days) < 7:
                rul_html = (
                    f"<p style='font-size:0.8rem;font-weight:600;"
                    f"color:#FBBF24;margin:4px 0 0;'>"
                    f"Est. failure: {float(rul_days):.1f} d</p>"
                )
            else:
                rul_html = (
                    f"<p style='font-size:0.8rem;color:#9B9CB5;margin:4px 0 0;'>"
                    f"Est. failure: {float(rul_days):.1f} d</p>"
                )
        except (TypeError, ValueError):
            pass

    cost_html = (
        f"<span style='color:#9B9CB5;'>&nbsp;&middot;&nbsp;"
        f"&#x20B9;{int(cost_inr):,} avoided</span>"
    ) if cost_inr > 0 else ""

    st.markdown(
        f"""<div style="
            background:{bg_color};
            border:1px solid rgba(255,255,255,0.07);
            border-left:3px solid {border_color};
            border-radius:0 12px 12px 0;
            padding:14px 16px;
            margin-bottom:8px;
        ">
          <div style="display:flex;align-items:flex-start;gap:10px;flex-wrap:wrap;">
            <div style="flex:1;min-width:0;">
              <div style="display:flex;align-items:center;gap:8px;
                          margin-bottom:5px;flex-wrap:wrap;">
                {badge_html}{ack_badge}
                <span style="font-weight:600;color:#E8E8F2;font-size:0.9rem;">
                  {equip_name}
                </span>
                <span class="mw-id">{asset_id_val}</span>
              </div>
              <p style="margin:0 0 4px;font-size:0.875rem;color:#9B9CB5;line-height:1.5;">
                {description}
              </p>
              {rul_html}
              <p style="margin:5px 0 0;font-size:0.6875rem;color:#5E6080;">
                Triggered {time_str}{cost_html}
              </p>
            </div>
          </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Recommended action expander
    if recommended_action:
        with st.expander("Recommended Action", expanded=is_critical):
            st.markdown(recommended_action)

    # Acknowledge button (Streamlit native — needed for interactivity)
    if not acknowledged:
        if st.button(
            "Mark acknowledged",
            key=f"ack_btn_{alert.get('alert_id', idx)}",
            type="primary" if is_critical else "secondary",
            icon=":material/check_circle:",
        ):
            _acknowledge_alert(alert["alert_id"])
            st.rerun()
    else:
        ack_by = alert.get("acknowledged_by", "engineer")
        ack_at = alert.get("acknowledged_at", "")
        if ack_at:
            try:
                dt = datetime.fromisoformat(ack_at.replace("Z", "+00:00"))
                ack_at = dt.strftime("%H:%M")
            except Exception:
                pass
        st.caption(f"Acknowledged by {ack_by} at {ack_at}")


# ---------------------------------------------------------------------------
# Alert list — filtered and sorted
# ---------------------------------------------------------------------------
alerts: list[dict] = st.session_state.get("alerts", [])

# Apply filters
filtered = [
    a for a in alerts
    if (show_acked or not a.get("acknowledged", False))
    and a.get("severity", "LOW").upper() in [s.upper() for s in sev_filter]
]

# Sort: unacknowledged CRITICAL first, then by severity order, then by triggered_at
filtered.sort(key=lambda a: (
    1 if a.get("acknowledged", False) else 0,
    _sev_order(a),
    a.get("triggered_at", ""),
))

if not filtered:
    if not show_acked:
        st.success(
            "No active alerts. Equipment running normally.",
            icon=":material/check_circle:",
        )
    else:
        st.info("No alerts match this filter. Clear filters to see all.")
else:
    st.markdown(
        f"<p style='font-size:0.6875rem;font-weight:600;color:#5E6080;"
        f"text-transform:uppercase;letter-spacing:0.07em;margin-bottom:12px;'>"
        f"{len(filtered)} active alert{'s' if len(filtered) != 1 else ''}</p>",
        unsafe_allow_html=True,
    )
    for idx, alert in enumerate(filtered):
        _render_alert_card(alert, idx)
