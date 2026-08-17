"""
wizard.ui.pages.05_Settings
============================
System health + demo controls + configuration.

Features:
- GET /health -> system component status (backend, RAG, KG, ML, LLM)
- POST /sensor/speed {multiplier} — set playback multiplier for demo
- POST /sensor/reset — reset sensor playback to start
- POST /sensor/inject_fault {equipment_id} — immediate fault inject (belt+suspenders)
- Session summary display (total cost avoidance, alerts, feedback)
- Arize Phoenix trace link (port 6006)
- LLM provider switch (primary/fallback display)
- Backend connection info

CRITICAL: httpx.Client (sync) ONLY.
"""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from wizard.ui._http import safe_get, safe_post
from wizard.ui._ui import (
    inject_global_css, status_badge, kpi_tile, page_header,
    render_hero_header, render_section_header,
)

inject_global_css()

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
render_hero_header(
    "System Settings",
    "Backend status, demo controls, session summary, and configuration.",
    badge="SYSTEM STATUS",
)

# ---------------------------------------------------------------------------
# System health check
# ---------------------------------------------------------------------------
render_section_header("System Health")

@st.fragment(run_every=10)
def _health_panel() -> None:
    """Polls /health every 10 seconds."""
    health_resp = safe_get("/v1/health")

    if health_resp is None:
        st.error(
            "Backend not responding. Start the server with: make run-backend",
            icon=":material/cloud_off:",
        )
        with st.expander("Startup commands"):
            st.code(
                "# From repo root:\n"
                "make run-backend   # starts FastAPI on :8000\n\n"
                "# Or:\n"
                "python -m uvicorn wizard.backend.main:app --port 8000 --reload",
                language="bash",
            )
        return

    # Parse health payload (real /v1/health shape: status, db_ok, scheduler_running,
    # circuit_breaker_state, alert_broadcaster_clients, version, uptime_seconds)
    overall_status = health_resp.get("status", "unknown")
    version = health_resp.get("version", "—")
    uptime = health_resp.get("uptime_seconds", None)

    cb = health_resp.get("circuit_breaker_state", "unknown")
    components = health_resp.get("components") or {
        "database": {"status": "ok" if health_resp.get("db_ok") else "down",
                     "detail": "SQLite (WAL)"},
        "scheduler": {"status": "ok" if health_resp.get("scheduler_running") else "down",
                      "detail": "APScheduler proactive evaluator (5s)"},
        "llm_circuit": {"status": "ok" if cb == "closed" else "degraded",
                        "detail": f"circuit breaker: {cb}"},
        "alert_stream": {"status": "ok",
                         "detail": f"{health_resp.get('alert_broadcaster_clients', 0)} SSE client(s)"},
    }

    if overall_status in ("ok", "healthy"):
        st.success(
            f"All systems operational  ·  v{version}",
            icon=":material/check_circle:",
        )
    elif overall_status == "degraded":
        st.warning(
            f"System degraded — some components offline  ·  v{version}",
            icon=":material/warning:",
        )
    else:
        st.error(
            f"System status: {overall_status}  ·  v{version}",
            icon=":material/cloud_off:",
        )

    if uptime:
        h, m = divmod(int(uptime), 3600)
        m, s = divmod(m, 60)
        st.caption(f"Uptime: {h:02d}h {m:02d}m {s:02d}s")

    # Component grid — use kpi_tile for status-accented display
    if components:
        comp_cols = st.columns(min(len(components), 4))
        component_items = list(components.items())
        for i, (comp_name, comp_data) in enumerate(component_items):
            col = comp_cols[i % 4]
            if isinstance(comp_data, dict):
                status = comp_data.get("status", "unknown")
                detail = comp_data.get("detail", "")
            else:
                status = str(comp_data)
                detail = ""

            # Map status string to tile variant
            tile_status = "normal" if status == "ok" else ("warning" if status == "degraded" else "critical")
            status_label = status.upper() if status != "unknown" else "Unknown"
            with col:
                kpi_tile(
                    comp_name.replace("_", " ").title(),
                    status_label,
                    detail[:40] if detail else "",
                    tile_status,
                )
    else:
        # No component breakdown — show basic status
        for comp in ["Backend", "RAG (LanceDB)", "Knowledge Graph", "ML Models", "LLM (Gemini)"]:
            st.markdown(f"- {comp}: OK")

_health_panel()

# ---------------------------------------------------------------------------
# Demo Controls
# ---------------------------------------------------------------------------
st.divider()
render_section_header(
    "Demo Controls",
    "EAF-04 CRITICAL alert fires at approximately 90 seconds when playback is set to 100x speed.",
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Sensor Playback Speed**")
    demo_mode = st.session_state.get("demo_mode_active", False)
    if not demo_mode:
        if st.button(
            "Start Demo (100x)",
            type="primary",
            use_container_width=True,
            icon=":material/play_circle:",
            help="Sets playback multiplier to 100x. EAF-04 CRITICAL alert fires in ~90 seconds.",
        ):
            result = safe_post("/v1/sensor/speed", {"multiplier": 100})
            if result is not None:
                st.session_state["demo_mode_active"] = True
                st.session_state["playback_multiplier"] = 100
                st.success(
                    "Demo mode active — EAF-04 alert fires in ~90 seconds.",
                    icon=":material/play_circle:",
                )
                st.rerun()
            else:
                st.warning(
                    "Backend offline. Demo alert will appear from pre-seeded data at page load.",
                    icon=":material/warning:",
                )
                st.session_state["demo_mode_active"] = True  # Still set for UI state
    else:
        st.markdown(status_badge("warning", "Demo active"), unsafe_allow_html=True)
        st.markdown("")
        if st.button(
            "Stop Demo",
            use_container_width=True,
            help="Resets playback to 1x real-time.",
        ):
            safe_post("/v1/sensor/speed", {"multiplier": 1})
            st.session_state["demo_mode_active"] = False
            st.session_state["playback_multiplier"] = 1
            st.rerun()

with col2:
    st.markdown("**Inject Fault**")
    inject_asset = st.selectbox(
        "Equipment",
        options=["EAF-04", "BF-FAN-02", "PUMP-HSM-07", "CONV-BRG-11", "HPU-CCS-03", "CONV-HSM-15"],
        key="inject_asset_select",
    )
    if st.button(
        "Inject Fault",
        use_container_width=True,
        type="secondary",
        icon=":material/bolt:",
        help="Immediately trigger a fault event for this equipment.",
    ):
        result = safe_post("/v1/sensor/inject_fault", {"equipment_id": inject_asset})
        if result is not None:
            st.success(
                f"Fault injected for {inject_asset}. Check the Alerts page.",
                icon=":material/check_circle:",
            )
        else:
            st.warning(
                "Backend offline — fault injection requires the backend running.",
                icon=":material/warning:",
            )

with col3:
    st.markdown("**Reset Demo**")
    st.caption("Clears all alerts and session data.")
    if st.button(
        "Full Reset",
        use_container_width=True,
        type="secondary",
        icon=":material/restart_alt:",
        help="Resets sensor playback to beginning, clears alerts, resets cost ticker.",
    ):
        # Reset backend
        safe_post("/v1/sensor/reset", {})

        # Reset session state
        keys_to_reset = [
            "alerts", "seen_alert_ids", "messages", "session_id",
            "cost_events", "total_cost_avoidance_inr", "last_cost_delta_inr",
            "demo_mode_active", "playback_multiplier", "demo_seeded",
        ]
        for k in keys_to_reset:
            if k in st.session_state:
                del st.session_state[k]

        st.success(
            "Full reset complete. Refresh the page to restart the demo.",
            icon=":material/check_circle:",
        )
        st.rerun()

# ---------------------------------------------------------------------------
# Session Summary
# ---------------------------------------------------------------------------
st.divider()
render_section_header("Session Summary", "Statistics for this demo session.")

col1, col2, col3, col4 = st.columns(4)

total_cost = st.session_state.get("total_cost_avoidance_inr", 0.0)
n_cost_events = len(st.session_state.get("cost_events", []))
alerts = st.session_state.get("alerts", [])
n_critical = sum(1 for a in alerts if a.get("severity", "").upper() == "CRITICAL")
n_acked = sum(1 for a in alerts if a.get("acknowledged", False))
messages = st.session_state.get("messages", [])
n_queries = sum(1 for m in messages if m.get("role") == "user")

col1.metric("Cost Prevented", f"₹{total_cost:,.0f}", help="avoided_hours × ₹75,000/hr")
col2.metric("Cost Events", n_cost_events, help="CRITICAL/HIGH events credited")
col3.metric("Critical Alerts", n_critical)
col4.metric("Engineer Queries", n_queries)

col5, col6, col7, col8 = st.columns(4)
col5.metric("Acknowledged", n_acked)
col6.metric("Total Alerts", len(alerts))
col7.metric("Chat Turns", len(messages))
session_id = st.session_state.get("session_id", "—")
col8.metric("Session ID", session_id[:12] if session_id else "—")

# Export session summary
if st.button(
    "Export Session Summary",
    help="Save session summary to data/demo/",
    icon=":material/download:",
):
    import json
    from pathlib import Path

    summary = {
        "session_id": st.session_state.get("session_id", ""),
        "export_at": datetime.utcnow().isoformat(),
        "total_cost_avoidance_inr": total_cost,
        "cost_events_count": n_cost_events,
        "alerts_total": len(alerts),
        "alerts_critical": n_critical,
        "alerts_acknowledged": n_acked,
        "engineer_queries": n_queries,
        "chat_turns": len(messages),
        "cost_events": st.session_state.get("cost_events", []),
    }

    try:
        demo_dir = Path("data/demo")
        demo_dir.mkdir(parents=True, exist_ok=True)
        out_path = demo_dir / "session_summary.json"
        out_path.write_text(json.dumps(summary, indent=2, default=str))
        st.success(
            f"Saved to {out_path}",
            icon=":material/check_circle:",
        )
    except Exception as exc:
        st.warning(f"Export failed: {exc}", icon=":material/warning:")

    # Also offer as in-browser download
    st.download_button(
        "Download summary.json",
        data=json.dumps(summary, indent=2, default=str),
        file_name="session_summary.json",
        mime="application/json",
        icon=":material/download:",
    )

# ---------------------------------------------------------------------------
# Observability links
# ---------------------------------------------------------------------------
st.divider()
render_section_header("Observability")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Trace Explorer**")
    st.markdown(
        "View agent execution, latency, token usage, and retrieval traces."
    )
    st.link_button(
        "Open Trace Explorer",
        "http://localhost:6006",
        use_container_width=True,
        icon=":material/analytics:",
    )
    st.caption("Arize Phoenix — localhost:6006")

with col2:
    st.markdown("**API Reference**")
    st.markdown("Browse all backend endpoints.")
    st.link_button("API Docs", "http://localhost:8000/docs", use_container_width=True)
    st.link_button("ReDoc", "http://localhost:8000/redoc", use_container_width=True)

# ---------------------------------------------------------------------------
# Configuration display
# ---------------------------------------------------------------------------
st.divider()
try:
    from wizard.core.config import settings
    with st.expander("Configuration", expanded=False):
        config_display = {
            "LLM Provider": settings.llm_provider,
            "Primary Model": settings.llm_model_primary,
            "Fallback Model": settings.llm_model_fallback,
            "Embedding Model": settings.embedding_model,
            "RUL Critical Threshold": f"{settings.rul_critical_days} days",
            "RUL Warning Threshold": f"{settings.rul_warning_days} days",
            "WRPS Critical": f"{settings.wrps_critical}",
            "Alert Cooldown": f"{settings.alert_cooldown_seconds}s",
            "Cost Rate": f"Rs {settings.cost_avoidance_rate_inr_per_hour:,.0f}/hr",
            "Backend Port": settings.backend_port,
            "Phoenix Enabled": settings.phoenix_enabled,
        }
        for key, val in config_display.items():
            col_k, col_v = st.columns([2, 3])
            col_k.markdown(f"**{key}**")
            col_v.code(str(val))
except Exception as exc:
    with st.expander("Configuration", expanded=False):
        st.info("Configuration unavailable — check the backend connection.")

# ---------------------------------------------------------------------------
# Architecture quick-ref
# ---------------------------------------------------------------------------
with st.expander("System Architecture", expanded=False):
    st.markdown("""
**Stack:**
- **Orchestration:** LangGraph 1.2 supervisor (PEV pattern) + 6 domain agents
- **RAG:** LanceDB hybrid (dense + BM25 + SQL prefilter) + FlashRank reranker + HyDE
- **Embeddings:** BAAI/bge-small-en-v1.5 (ONNX, CPU)
- **Knowledge Graph:** NetworkX FMEA ontology (ISO 14224)
- **RUL:** WeibullAFTFitter (lifelines 0.30) + degradation index + Bayesian correction
- **Anomaly:** IsolationForest + LSTM-AE + River HST + adaptive threshold
- **Failure Class:** LightGBM calibrated 4-class + tsfresh features
- **LLM:** LiteLLM - Gemini 2.5 Flash (primary) | Qwen2.5-3B Ollama (fallback)
- **Backend:** FastAPI 0.136 + APScheduler + SSE + tenacity + pybreaker
- **Frontend:** Streamlit 1.58 + Plotly 5.22 + httpx (sync)
- **Observability:** Arize Phoenix (local, port 6006) + structlog
- **Data:** NASA C-MAPSS + AI4I 2020 + 500 synthetic docs (ISO 14224 ontology)

**Data flow:**
Sensor playback - APScheduler evaluator - ML pipeline - AnomalyAlert (SQLite) -
SSE fan-out - Streamlit polling (st.fragment run_every=3) - Alert card + cost ticker

**The 90-second demo moment:**
POST /sensor/speed {multiplier: 100} - EAF-04 RUL crosses 14-day threshold -
CRITICAL AnomalyAlert fired - Supervisor routes - all 6 agents execute -
Complete plan delivered with citations - cost ticker increments - cost avoidance credited
    """)
