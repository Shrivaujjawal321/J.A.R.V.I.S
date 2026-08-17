"""
wizard.ui.pages.02_Dashboard
=============================
Equipment-health dashboard: RUL gauges + heatmap.

Features:
- go.Indicator RUL gauges (6 equipment, 2x3 grid) with @st.cache_data ttl=30
- go.Heatmap equipment health (6x7 days) with RdYlGn colorscale
- @st.cache_data ttl=30 on all chart-generating functions
- st.fragment run_every=3 for live gauge refresh
- Sensor detail section per equipment
- ISA-101 muted background, color reserved for status

CRITICAL: httpx.Client (sync) ONLY.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from wizard.ui._http import safe_get
from wizard.ui._demo_seed import DEMO_EQUIPMENT, DEMO_SENSOR_STATE
from wizard.ui._ui import (
    inject_global_css, page_header, status_badge, kpi_tile,
    render_hero_header, render_section_header,
)

inject_global_css()

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
render_hero_header(
    "Equipment Health",
    "Real-time RUL estimates, anomaly scores, and 7-day health trend for all monitored assets.",
    badge="LIVE · 30s REFRESH",
    accent_color="#34D399",
)

# ---------------------------------------------------------------------------
# Health-score to colour mapping (ISA-101: muted background, colour = status)
# ---------------------------------------------------------------------------

def _health_color(score: float) -> str:
    """Map health score 0-100 to a CSS colour for non-Plotly contexts."""
    if score >= 75:
        return "green"
    if score >= 50:
        return "orange"
    if score >= 25:
        return "red"
    return "darkred"


def _rul_gauge_color(rul_days: float) -> str:
    if rul_days <= 0.5:   # <12 h
        return "crimson"
    if rul_days <= 3.0:
        return "orangered"
    if rul_days <= 14.0:
        return "darkorange"
    if rul_days <= 30.0:
        return "gold"
    return "seagreen"


# ---------------------------------------------------------------------------
# Fetch sensor state — tries backend, falls back to demo seed
# ---------------------------------------------------------------------------

def _get_sensor_state() -> dict[str, dict]:
    """
    Returns {asset_id: {rul_days_p50, anomaly_score, health_score, ...}}

    Backend /v1/sensor/state returns {"assets": [...], ...}.
    We normalise to the flat {asset_id: fields} dict that the rest of the
    dashboard expects, mapping backend field names to the demo-seed names
    where they differ.
    """
    resp = safe_get("/v1/sensor/state")
    if resp and isinstance(resp, dict) and "assets" in resp:
        normalised: dict[str, dict] = {}
        for asset in resp["assets"]:
            aid = asset.get("asset_id", "")
            normalised[aid] = {
                "rul_days_p50": asset.get("rul_days_p50", 30.0),
                "rul_days_p90": asset.get("rul_days_p90", asset.get("rul_days_p50", 30.0)),
                "rul_days_p10": asset.get("rul_days_p10", asset.get("rul_days_p50", 30.0)),
                "anomaly_score": asset.get("anomaly_score", 0.0),
                "health_score": asset.get("health_score", 70),
                "failure_probability": asset.get("failure_probability", asset.get("anomaly_score", 0.0)),
                "failure_class": asset.get("failure_class", "unknown"),
                "degradation_index": asset.get("degradation_index", 0.0),
                "sensor_readings": asset.get("latest_sensor_readings", {}),
            }
        if normalised:
            return normalised

    # Backend offline or unexpected shape — use demo seed data (always has content)
    return DEMO_SENSOR_STATE


# ---------------------------------------------------------------------------
# RUL Gauge figure — @st.cache_data ttl=30
# Anti-pattern avoided: cache prevents redundant re-render on every rerun
# ---------------------------------------------------------------------------

@st.cache_data(ttl=30, show_spinner=False)
def _build_rul_gauge_figure(sensor_state_json: str) -> go.Figure:
    """
    Build a 2x3 Plotly subplot with go.Indicator gauges.
    sensor_state_json: JSON string of {asset_id: state_dict} for cache key.
    """
    import json
    sensor_state: dict[str, dict] = json.loads(sensor_state_json)

    equipment_list = list(DEMO_EQUIPMENT)
    n = len(equipment_list)
    rows, cols = 2, 3

    # go.Indicator traces require subplot cells typed as "indicator" (domain),
    # not the default "xy" — otherwise make_subplots raises ValueError on add_trace.
    # No subplot_titles here: title text causes layout collision with the gauge
    # number/delta area in a compact grid. Equipment names are rendered as
    # st.markdown headers above each gauge column instead (see render_dashboard).
    fig = make_subplots(
        rows=rows,
        cols=cols,
        specs=[[{"type": "indicator"} for _ in range(cols)] for _ in range(rows)],
        vertical_spacing=0.12,
        horizontal_spacing=0.06,
    )

    for i, eq in enumerate(equipment_list[:n]):
        row = (i // cols) + 1
        col = (i % cols) + 1
        asset_id = eq["asset_id"]
        state = sensor_state.get(asset_id, {})

        rul_p50 = state.get("rul_days_p50", 30.0)
        rul_p10 = state.get("rul_days_p10", rul_p50 * 0.6)
        rul_p90 = state.get("rul_days_p90", rul_p50 * 1.4)
        health = state.get("health_score", 70)
        anomaly = state.get("anomaly_score", 0.2)

        # Gauge colour based on RUL
        bar_color = _rul_gauge_color(rul_p50)

        # Title: only health + anomaly on one compact line — NO equipment name
        # (equipment name is already shown as a header above the gauge column).
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=rul_p50,
                number={"suffix": " d", "valueformat": ".1f", "font": {"size": 26, "color": "#E8E8F2"}},
                title={
                    "text": (
                        f"<span style='font-size:11px;color:#9B9CB5;'>"
                        f"Health {health}% · Anomaly {anomaly:.2f}</span>"
                    ),
                    "font": {"size": 11, "color": "#9B9CB5"},
                },
                gauge={
                    "axis": {
                        "range": [0, 60],
                        "tickwidth": 1,
                        "tickcolor": "#5E6080",
                        "nticks": 5,
                        "tickfont": {"size": 9, "color": "#5E6080"},
                    },
                    "bar": {"color": bar_color, "thickness": 0.28},
                    "bgcolor": "rgba(22,27,39,1)",
                    "borderwidth": 1,
                    "bordercolor": "rgba(255,255,255,0.08)",
                    "steps": [
                        {"range": [0, 0.5],  "color": "rgba(248,113,113,0.20)"},
                        {"range": [0.5, 3],  "color": "rgba(251,146,60,0.15)"},
                        {"range": [3, 14],   "color": "rgba(251,191,36,0.12)"},
                        {"range": [14, 30],  "color": "rgba(52,211,153,0.08)"},
                        {"range": [30, 60],  "color": "rgba(52,211,153,0.04)"},
                    ],
                    "threshold": {
                        "line": {"color": "#F87171", "width": 2},
                        "thickness": 0.8,
                        "value": 0.5,
                    },
                },
            ),
            row=row,
            col=col,
        )

    fig.update_layout(
        height=440,
        margin={"l": 10, "r": 10, "t": 20, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "IBM Plex Sans, Inter, sans-serif", "color": "#E8E8F2", "size": 11},
        showlegend=False,
    )
    return fig


def _build_single_gauge(state: dict) -> go.Figure:
    """
    One self-contained RUL gauge for a single asset. Rendered inside its own
    column cell directly beneath that asset's name header, so the label and the
    gauge always stay together (avoids the names-detached-from-gauges layout bug).
    """
    rul_p50 = state.get("rul_days_p50", 30.0)
    health = state.get("health_score", 70)
    anomaly = state.get("anomaly_score", 0.2)
    bar_color = _rul_gauge_color(rul_p50)

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=rul_p50,
            number={"suffix": " d", "valueformat": ".1f", "font": {"size": 24, "color": "#E8E8F2"}},
            title={
                "text": (
                    f"<span style='font-size:11px;color:#9B9CB5;'>"
                    f"Health {health}% · Anomaly {anomaly:.2f}</span>"
                ),
                "font": {"size": 11, "color": "#9B9CB5"},
            },
            gauge={
                "axis": {
                    "range": [0, 60],
                    "tickwidth": 1,
                    "tickcolor": "#5E6080",
                    "nticks": 5,
                    "tickfont": {"size": 9, "color": "#5E6080"},
                },
                "bar": {"color": bar_color, "thickness": 0.28},
                "bgcolor": "rgba(22,27,39,1)",
                "borderwidth": 1,
                "bordercolor": "rgba(255,255,255,0.08)",
                "steps": [
                    {"range": [0, 0.5],  "color": "rgba(248,113,113,0.20)"},
                    {"range": [0.5, 3],  "color": "rgba(251,146,60,0.15)"},
                    {"range": [3, 14],   "color": "rgba(251,191,36,0.12)"},
                    {"range": [14, 30],  "color": "rgba(52,211,153,0.08)"},
                    {"range": [30, 60],  "color": "rgba(52,211,153,0.04)"},
                ],
                "threshold": {
                    "line": {"color": "#F87171", "width": 2},
                    "thickness": 0.8,
                    "value": 0.5,
                },
            },
        )
    )
    fig.update_layout(
        height=210,
        margin={"l": 12, "r": 12, "t": 30, "b": 6},
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "IBM Plex Sans, Inter, sans-serif", "color": "#E8E8F2", "size": 11},
        showlegend=False,
    )
    return fig


# ---------------------------------------------------------------------------
# 7-day health heatmap — @st.cache_data ttl=30
# ---------------------------------------------------------------------------

@st.cache_data(ttl=30, show_spinner=False)
def _build_health_heatmap(_cache_key: str) -> go.Figure:
    """
    go.Heatmap: 6 equipment x 7 days health scores (0-100).
    RdYlGn colorscale — ISA-101 standard for process industry.
    Text overlay satisfies multi-cue requirement (color + text label).
    """
    equipment_names = [eq["name"].split(" ")[0] + " " + eq["name"].split(" ")[-1]
                       for eq in DEMO_EQUIPMENT]

    # Build 7-day synthetic trend from current health scores
    # In production this comes from GET /sensor/history?days=7
    health_scores_now = [
        DEMO_SENSOR_STATE[eq["asset_id"]].get("health_score", 70)
        for eq in DEMO_EQUIPMENT
    ]

    # Simulate daily trend: each day adds ~2-5 points degradation going back
    import random
    random.seed(42)
    days_back = 7
    z_matrix: list[list[float]] = []
    day_labels = [
        (datetime.utcnow() - timedelta(days=i)).strftime("%b %d")
        for i in range(days_back - 1, -1, -1)
    ]

    for score_now in health_scores_now:
        row_scores: list[float] = []
        s = min(score_now + random.uniform(10, 25), 100)
        for d in range(days_back):
            row_scores.append(round(s, 1))
            s = max(s - random.uniform(0.5, 3.5), 0)
        z_matrix.append(row_scores)

    fig = go.Figure(
        go.Heatmap(
            z=z_matrix,
            x=day_labels,
            y=equipment_names,
            colorscale="RdYlGn",
            zmin=0,
            zmax=100,
            text=[
                [f"{v:.0f}%" for v in row]
                for row in z_matrix
            ],
            texttemplate="%{text}",
            textfont={"size": 10},
            showscale=True,
            colorbar={
                "title": "Health %",
                "tickvals": [0, 25, 50, 75, 100],
                "ticktext": ["Critical", "High", "Medium", "Low", "Healthy"],
                "len": 0.8,
            },
            hovertemplate="<b>%{y}</b><br>%{x}: %{z:.0f}%<extra></extra>",
        )
    )

    fig.update_layout(
        height=300,
        margin={"l": 10, "r": 10, "t": 30, "b": 40},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "IBM Plex Sans, Inter, sans-serif", "color": "#E8E8F2", "size": 11},
        title={
            "text": "Equipment Health — 7-Day Trend",
            "x": 0.0,
            "font": {"size": 14, "color": "#E8E8F2"},
        },
        xaxis={"tickangle": -30, "tickcolor": "#5E6080", "tickfont": {"color": "#9B9CB5"}},
        yaxis={"tickcolor": "#5E6080", "tickfont": {"color": "#9B9CB5"}},
        coloraxis_colorbar={
            "tickfont": {"color": "#9B9CB5"},
            "title": {"font": {"color": "#9B9CB5"}},
        },
    )
    return fig


# ---------------------------------------------------------------------------
# Main dashboard rendering with st.fragment for live refresh
# ---------------------------------------------------------------------------

@st.fragment(run_every=30)
def render_dashboard() -> None:
    """
    Refreshes the gauge grid every 30 seconds independently.
    (Heatmap refreshes separately via its own cache ttl.)
    """
    import json

    sensor_state = _get_sensor_state()
    sensor_state_json = json.dumps(
        {k: {kk: v for kk, v in vv.items() if kk not in ("sensor_readings",)}
         for k, vv in sensor_state.items()},
        default=str,
    )

    # KPI Summary strip — 4 tiles.
    # An asset counts as CRITICAL when failure is near (RUL < 3 days) OR its
    # anomaly score is high (>= 0.80). HIGH RISK when RUL < 14 days OR the
    # anomaly is rising (>= 0.55). This keeps the dashboard counts consistent
    # with the risk classification used by the chat + alerts (RUL-only
    # thresholds previously showed 0 critical even when an asset was failing).
    critical_assets: list[str] = []
    high_assets: list[str] = []
    for eq in DEMO_EQUIPMENT:
        s = sensor_state.get(eq["asset_id"], {})
        rul = s.get("rul_days_p50", 99)
        anom = s.get("anomaly_score", 0.0)
        if rul < 3.0 or anom >= 0.80:
            critical_assets.append(eq["name"])
        elif rul < 14.0 or anom >= 0.55:
            high_assets.append(eq["name"])
    avg_health = sum(
        sensor_state.get(eq["asset_id"], {}).get("health_score", 70)
        for eq in DEMO_EQUIPMENT
    ) / len(DEMO_EQUIPMENT)

    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        kpi_tile(
            "Critical",
            str(len(critical_assets)),
            "Near failure or high anomaly",
            "critical" if critical_assets else "idle",
        )
    with kpi_cols[1]:
        kpi_tile(
            "High Risk",
            str(len(high_assets)),
            "Declining or rising anomaly",
            "high" if high_assets else "idle",
        )
    with kpi_cols[2]:
        kpi_tile(
            "Monitored Assets",
            str(len(DEMO_EQUIPMENT)),
            "",
            "idle",
        )
    with kpi_cols[3]:
        health_status = "normal" if avg_health >= 75 else ("warning" if avg_health >= 50 else "critical")
        kpi_tile(
            "Avg Health",
            f"{avg_health:.0f}%",
            "",
            health_status,
        )

    # Alert banners
    if critical_assets:
        st.error(
            f"Critical: {', '.join(critical_assets)} — inspect within 12 hours.",
            icon=":material/error:",
        )
    if high_assets:
        st.warning(
            f"High risk: {', '.join(high_assets)} — schedule within 72 hours.",
            icon=":material/warning:",
        )

    render_section_header(
        "Remaining Useful Life",
        "RUL P50 estimate in days. Zones: red < 12 h  ·  orange 12h-3d  ·  yellow 3-14d  ·  green 14d+",
    )

    # Each asset is a self-contained cell: name header + its OWN gauge + range
    # caption, in a 3-per-row grid. This keeps every label attached to its gauge.
    equipment_list = list(DEMO_EQUIPMENT)
    for row_idx in range(2):
        row_cols = st.columns(3, gap="medium")
        for col_idx in range(3):
            eq_idx = row_idx * 3 + col_idx
            if eq_idx >= len(equipment_list):
                break
            eq = equipment_list[eq_idx]
            asset_id_key = eq["asset_id"]
            state = sensor_state.get(asset_id_key, {})
            rul_p50 = state.get("rul_days_p50", 30.0)
            rul_p10 = state.get("rul_days_p10", rul_p50 * 0.6)
            rul_p90 = state.get("rul_days_p90", rul_p50 * 1.4)
            with row_cols[col_idx]:
                st.markdown(
                    f"<p style='margin:0 0 2px;font-size:0.82rem;font-weight:600;"
                    f"color:#E8E8F2;text-align:center;line-height:1.3;'>{eq['name']}</p>"
                    f"<p style='margin:0;font-size:0.7rem;color:#9B9CB5;"
                    f"text-align:center;'>P10-P90: {rul_p10:.1f} - {rul_p90:.1f} d</p>",
                    unsafe_allow_html=True,
                )
                st.plotly_chart(
                    _build_single_gauge(state),
                    use_container_width=True,
                    key=f"rul_gauge_{asset_id_key}",
                    theme=None,
                )


render_dashboard()

# ---------------------------------------------------------------------------
# Health heatmap (separate, its own cache)
# ---------------------------------------------------------------------------
st.divider()
render_section_header("Health Trend — 7 Days")
heatmap_cache_key = datetime.utcnow().strftime("%Y-%m-%dT%H:%M")  # changes each minute
heatmap_fig = _build_health_heatmap(heatmap_cache_key)
st.plotly_chart(heatmap_fig, use_container_width=True, theme=None)

# ---------------------------------------------------------------------------
# Sensor detail expandable section
# ---------------------------------------------------------------------------
st.divider()
render_section_header("Sensor Detail")

sensor_state = _get_sensor_state()

for eq in DEMO_EQUIPMENT:
    asset_id_val = eq["asset_id"]
    state = sensor_state.get(asset_id_val, {})
    readings = state.get("sensor_readings", {})
    health = state.get("health_score", 70)
    rul_p50 = state.get("rul_days_p50", 30.0)

    # Text-based status label — no emoji
    if health < 25:
        health_label = "CRITICAL"
    elif health < 50:
        health_label = "WARNING"
    elif health < 75:
        health_label = "Normal"
    else:
        health_label = "Normal"

    with st.expander(
        f"{eq['name']} — Health {health}%  ·  RUL {rul_p50:.1f}d  ·  {health_label}",
        expanded=(health < 25),
    ):
        col1, col2, col3 = st.columns(3)

        # Sensor readings
        with col1:
            st.markdown("**Sensor Readings**")
            for sensor_key, display_name, unit in [
                ("temperature_c", "Temperature", "C"),
                ("vibration_mm_s", "Vibration", "mm/s"),
                ("pressure_bar", "Pressure", "bar"),
                ("current_a", "Current", "A"),
                ("rpm", "RPM", "rpm"),
                ("torque_nm", "Torque", "Nm"),
            ]:
                val = readings.get(sensor_key)
                if val is not None:
                    st.metric(display_name, f"{val:.1f} {unit}")

        with col2:
            st.markdown("**Health Metrics**")
            st.metric("Anomaly Score", f"{state.get('anomaly_score', 0):.3f}")
            st.metric("Degradation Index", f"{state.get('degradation_index', 0):.3f}")
            failure_prob = state.get("failure_probability", 0)
            st.metric("Failure Probability", f"{failure_prob:.1%}")

        with col3:
            st.markdown("**RUL Estimates**")
            st.metric("P10 (pessimistic)", f"{state.get('rul_days_p10', 0):.1f}d")
            st.metric("P50 (median)", f"{rul_p50:.1f}d")
            st.metric("P90 (optimistic)", f"{state.get('rul_days_p90', 0):.1f}d")
            failure_class = state.get("failure_class", "—")
            st.caption(f"Failure class: {failure_class}")
