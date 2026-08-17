"""
wizard.ui.pages.04_Logbook
===========================
Maintenance logbook: historical records + CSV export.

Data sources (in order of priority):
1. GET /v1/logbook from backend (SQLite MaintenanceRecord table via FastAPI)
2. Direct sqlite3 read of data/sessions.db (read-only — avoids round-trip for static data)
3. Pre-seeded demo DEMO_LOGBOOK from session_state (always has content on first load)

Features:
- st.dataframe with column config (sorted by performed_at desc)
- Filter by equipment, date range, maintenance type, outcome
- st.download_button CSV export (pandas to_csv in-memory)
- Acknowledged alert -> logbook entry promotion
- Acknowledged alerts from session_state shown as "acknowledged" entries
- Compact card view for each record

NOTE: sqlite3 read is read-only. No writes from UI.
CRITICAL: httpx.Client (sync) ONLY.
"""

from __future__ import annotations

import io
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

from wizard.ui._http import safe_get
from wizard.ui._demo_seed import DEMO_LOGBOOK, DEMO_EQUIPMENT
from wizard.ui._ui import inject_global_css, status_badge, page_header, render_hero_header, render_section_header

inject_global_css()

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
render_hero_header(
    "Maintenance Logbook",
    "Historical records and engineer notes. Sorted by date, newest first.",
    badge="MAINTENANCE HISTORY",
)

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_logbook_from_backend() -> list[dict]:
    """GET /v1/logbook — returns list of maintenance records."""
    resp = safe_get("/v1/logbook", params={"limit": 200, "offset": 0})
    if resp and isinstance(resp, list) and len(resp) > 0:
        return resp
    return []


def _load_from_sessions_db() -> list[dict]:
    """
    Direct sqlite3 read of data/sessions.db (read-only).
    Reads maintenance_record table if it exists.
    Falls back silently.
    """
    records: list[dict] = []
    db_candidates = [
        Path("data/sessions.db"),
        Path("data/wizard.db"),
    ]
    for db_path in db_candidates:
        if not db_path.exists():
            continue
        try:
            conn = sqlite3.connect(str(db_path), check_same_thread=False)
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                """
                SELECT entity_id as log_id,
                       asset_id,
                       work_order_id,
                       maintenance_type,
                       description,
                       performed_at,
                       technician_id,
                       duration_hours,
                       parts_used,
                       outcome,
                       ingested_at
                FROM maintenance_record
                ORDER BY performed_at DESC
                LIMIT 200
                """
            )
            rows = cur.fetchall()
            conn.close()
            for row in rows:
                d = dict(row)
                # Resolve equipment name
                eq_map = {eq["asset_id"]: eq["name"] for eq in DEMO_EQUIPMENT}
                d["equipment_name"] = eq_map.get(d.get("asset_id", ""), d.get("asset_id", "—"))
                # parts_used may be JSON string
                try:
                    parts = d.get("parts_used", "[]")
                    d["parts_used"] = json.loads(parts) if isinstance(parts, str) else parts
                except Exception:
                    d["parts_used"] = []
                records.append(d)
            if records:
                return records
        except Exception:
            continue
    return []


def _merge_acknowledged_alerts(logbook: list[dict]) -> list[dict]:
    """
    Acknowledged alerts from session_state become logbook entries.
    Avoids duplicate entries by checking log_id vs alert_id.
    """
    existing_ids = {e.get("log_id", "") for e in logbook}
    alerts: list[dict] = st.session_state.get("alerts", [])

    for alert in alerts:
        if not alert.get("acknowledged", False):
            continue
        aid = alert.get("alert_id", "")
        if aid in existing_ids:
            continue
        logbook.append({
            "log_id": aid,
            "asset_id": alert.get("asset_id", "—"),
            "equipment_name": alert.get("equipment_name", alert.get("asset_id", "—")),
            "work_order_id": f"ALERT-{aid[:8]}",
            "maintenance_type": "predictive",
            "description": f"[Alert acknowledged] {alert.get('description', '')}",
            "performed_at": alert.get("acknowledged_at", alert.get("triggered_at", "")),
            "technician_id": alert.get("acknowledged_by", "engineer"),
            "duration_hours": None,
            "outcome": "pending",
            "fault_codes": [alert.get("alert_type", "")],
            "parts_used": [],
            "source": "alert_ack",
        })
        existing_ids.add(aid)

    return logbook


@st.cache_data(ttl=30, show_spinner=False)
def _load_full_logbook() -> list[dict]:
    """
    Load logbook from all sources, merge, deduplicate.
    Cached 30s so tab navigation doesn't re-query.
    Never raises — always returns at least the demo seed so the UI has content.
    """
    try:
        # Priority 1: backend
        records = _load_logbook_from_backend()
        if not records:
            # Priority 2: direct DB
            records = _load_from_sessions_db()
        if not records:
            # Priority 3: demo seed
            records = list(DEMO_LOGBOOK)
        return records
    except Exception:
        # Fallback — never let a cached error state break the page
        return list(DEMO_LOGBOOK)


# ---------------------------------------------------------------------------
# Build unified logbook
# ---------------------------------------------------------------------------
try:
    logbook = list(_load_full_logbook())
except Exception:
    st.warning(
        "Logbook backend unavailable — showing demo data.",
        icon=":material/cloud_off:",
    )
    logbook = list(DEMO_LOGBOOK)

# Merge acknowledged alerts from this session
logbook = _merge_acknowledged_alerts(logbook)

# Also add session-state logbook (seeded at startup)
session_logbook = st.session_state.get("logbook", [])
existing_ids = {e.get("log_id", "") for e in logbook}
for entry in session_logbook:
    if entry.get("log_id", "") not in existing_ids:
        logbook.append(entry)
        existing_ids.add(entry["log_id"])

# Sort by performed_at desc
logbook.sort(
    key=lambda x: x.get("performed_at", x.get("timestamp", "")) or "",
    reverse=True,
)

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        "<p style='font-size:0.6875rem;font-weight:600;color:#94A3B8;"
        "text-transform:uppercase;letter-spacing:0.06em;margin:0 0 8px;'>Filters</p>",
        unsafe_allow_html=True,
    )

    equip_names = sorted({e.get("equipment_name", e.get("asset_id", "—")) for e in logbook})
    selected_equip = st.multiselect(
        "Equipment",
        options=equip_names,
        default=[],
        key="logbook_equip_filter",
        placeholder="All equipment",
    )

    maint_types = sorted({e.get("maintenance_type", "—") for e in logbook})
    selected_types = st.multiselect(
        "Type",
        options=maint_types,
        default=[],
        key="logbook_type_filter",
        placeholder="All types",
    )

    outcomes = sorted({e.get("outcome", "—") for e in logbook})
    selected_outcomes = st.multiselect(
        "Outcome",
        options=outcomes,
        default=[],
        key="logbook_outcome_filter",
        placeholder="All outcomes",
    )

    # Date range
    today = datetime.utcnow().date()
    date_from = st.date_input("From", value=today - timedelta(days=60), key="logbook_date_from")
    date_to = st.date_input("To", value=today, key="logbook_date_to")


# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------
def _parse_date(s: str | None) -> datetime | None:
    if not s:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s[:len(fmt) + 1].strip(), fmt)
        except ValueError:
            continue
    return None


filtered = logbook
if selected_equip:
    filtered = [e for e in filtered if e.get("equipment_name", e.get("asset_id", "")) in selected_equip]
if selected_types:
    filtered = [e for e in filtered if e.get("maintenance_type", "") in selected_types]
if selected_outcomes:
    filtered = [e for e in filtered if e.get("outcome", "") in selected_outcomes]

# Date filter
date_filtered: list[dict] = []
for e in filtered:
    dt = _parse_date(e.get("performed_at") or e.get("timestamp") or e.get("ingested_at"))
    if dt:
        if datetime.combine(date_from, datetime.min.time()) <= dt <= datetime.combine(date_to, datetime.max.time()):
            date_filtered.append(e)
    else:
        date_filtered.append(e)  # Include records with no date
filtered = date_filtered

# ---------------------------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Records", len(filtered))
col2.metric(
    "Corrective",
    sum(1 for e in filtered if e.get("maintenance_type") == "corrective"),
)
col3.metric(
    "Predictive",
    sum(1 for e in filtered if e.get("maintenance_type") == "predictive"),
)
resolved = sum(1 for e in filtered if e.get("outcome") == "resolved")
col4.metric("Resolved", resolved)

# ---------------------------------------------------------------------------
# Dataframe view
# ---------------------------------------------------------------------------
if filtered:
    df_rows = []
    for e in filtered:
        df_rows.append({
            "Log ID": e.get("log_id", "—")[:12],
            "Equipment": e.get("equipment_name", e.get("asset_id", "—")),
            "Work Order": e.get("work_order_id", "—"),
            "Type": e.get("maintenance_type", "—"),
            "Description": (e.get("description", "") or "")[:80],
            "Date": e.get("performed_at", "—"),
            "Technician": e.get("technician_id", "—"),
            "Duration (h)": e.get("duration_hours"),
            "Parts Used": ", ".join(e.get("parts_used", []) or []) or "—",
            "Outcome": e.get("outcome", "—"),
        })
    df = pd.DataFrame(df_rows)

    with st.expander("All Records", expanded=True):
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Log ID": st.column_config.TextColumn(width="small"),
                "Equipment": st.column_config.TextColumn(width="medium"),
                "Work Order": st.column_config.TextColumn(width="small"),
                "Type": st.column_config.TextColumn(width="small"),
                "Description": st.column_config.TextColumn(width="large"),
                "Date": st.column_config.TextColumn(width="medium"),
                "Duration (h)": st.column_config.NumberColumn(format="%.1f", width="small"),
                "Outcome": st.column_config.TextColumn(width="small"),
            },
        )

    # CSV export
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="Download CSV",
        data=csv_buffer.getvalue(),
        file_name=f"maintenance_logbook_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        help="Download all visible logbook records as a CSV file.",
        icon=":material/download:",
    )
else:
    st.info("No records match this filter. Adjust the date range or clear filters.")

# ---------------------------------------------------------------------------
# Card view (last 5 records — quick scan)
# ---------------------------------------------------------------------------
st.divider()
render_section_header("Recent Activity")

# Maintenance type -> badge variant mapping
_TYPE_VARIANT = {
    "corrective":  "critical",
    "preventive":  "info",
    "predictive":  "normal",
    "emergency":   "high",
}

# Outcome -> badge variant mapping
_OUTCOME_VARIANT = {
    "resolved":  "normal",
    "partial":   "warning",
    "escalated": "critical",
    "pending":   "info",
}

for entry in filtered[:5]:
    maint_type = entry.get("maintenance_type", "—")
    outcome = entry.get("outcome", "—")

    type_variant = _TYPE_VARIANT.get(maint_type, "idle")
    outcome_variant = _OUTCOME_VARIANT.get(outcome, "idle")

    with st.container(border=True):
        c1, c2 = st.columns([5, 1])
        with c1:
            equip_name = entry.get("equipment_name", entry.get("asset_id", "—"))
            work_order = entry.get("work_order_id", "—")
            st.markdown(
                f"**{equip_name}** "
                f"<span class='mw-id'>{work_order}</span>",
                unsafe_allow_html=True,
            )
            desc = entry.get("description", "")
            if desc:
                st.markdown(desc[:200] + ("..." if len(desc) > 200 else ""))
            parts = entry.get("parts_used", [])
            if parts:
                st.caption(f"Parts: {', '.join(parts)}")
            performed = entry.get("performed_at", "—")
            tech = entry.get("technician_id", "—")
            dur = entry.get("duration_hours")
            meta = f"{performed}  ·  {tech}"
            if dur:
                meta += f"  ·  {dur:.1f} h"
            st.caption(meta)
        with c2:
            st.markdown(
                status_badge(type_variant, maint_type.title()) + "<br><br>" +
                status_badge(outcome_variant, outcome.title()),
                unsafe_allow_html=True,
            )
