"""VULCAN · Health Dashboard — fleet view of the 15 assets (FR5).

Each asset shows its ML-derived health: latest fault class, anomaly score, RUL
(cycles/days), sensor-breach count — coloured by a coarse risk band. Drill into
any asset for its sensor summary + scenario catalogue. Pure deterministic ML +
spine reads (cached) — no LLM, so the dashboard is instant.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parents[3]   # .../vulcan/  (contains vulcan/)
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))
os.environ.pop("ANTHROPIC_API_KEY", None)

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from vulcan.ui import _shared as S  # noqa: E402


def main() -> None:
    S.page_setup("Fleet Health", icon="📊")
    st.markdown("### 📊 Fleet health — 15 critical steel assets")
    st.caption(
        "Live condition status from the ML layer (fault classifier · IsolationForest "
        "anomaly · LightGBM RUL) over the per-asset condition-monitoring tables. "
        "Risk band is derived deterministically — no LLM."
    )

    assets = S.fleet_assets()

    # ---- compute health for the fleet (cached per asset) ----
    rows = []
    band_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    with st.spinner("Scoring fleet health…"):
        for a in assets:
            h = S.asset_health(a["asset_id"])
            band = S.health_band(h)
            band_counts[band] = band_counts.get(band, 0) + 1
            rows.append({**a, **h, "band": band})

    # ---- KPI strip ----
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.markdown(S.kpi("Assets monitored", str(len(rows))), unsafe_allow_html=True)
    k2.markdown(S.kpi("Critical", str(band_counts["CRITICAL"]), S.RISK_COLORS["CRITICAL"]),
                unsafe_allow_html=True)
    k3.markdown(S.kpi("High", str(band_counts["HIGH"]), S.RISK_COLORS["HIGH"]),
                unsafe_allow_html=True)
    k4.markdown(S.kpi("Medium", str(band_counts["MEDIUM"]), S.RISK_COLORS["MEDIUM"]),
                unsafe_allow_html=True)
    k5.markdown(S.kpi("Healthy", str(band_counts["LOW"]), S.RISK_COLORS["LOW"]),
                unsafe_allow_html=True)

    st.divider()

    # ---- fleet tiles (sorted: most-at-risk first) ----
    band_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    rows.sort(key=lambda r: (band_order.get(r["band"], 9), r["criticality"]))

    st.markdown("#### Fleet (most-at-risk first)")
    cols = st.columns(3)
    for i, r in enumerate(rows):
        with cols[i % 3]:
            _tile(r)

    st.divider()

    # ---- drill-down ----
    st.markdown("#### Asset drill-down")
    ids = [r["asset_id"] for r in rows]
    sel = st.selectbox("Select an asset", ids, index=0)
    _drilldown(sel)


def _tile(r: dict) -> None:
    color = S.RISK_COLORS.get(r["band"], "#94A3B8")
    rul = r.get("rul_cycles")
    rul_s = f"{rul:.0f} cyc (~{r.get('rul_days')} d)" if rul is not None else "n/a"
    anom = r.get("anomaly_score") or 0.0
    st.markdown(
        f"""
        <div class="fleet-tile" style="border-left:4px solid {color};">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span class="fleet-id">{r['asset_id']}</span>
            {S.risk_badge(r['band'])}
          </div>
          <div class="fleet-meta">{r['equipment_class']} · crit {r['criticality']} · {r['process_stage']}</div>
          <div style="margin-top:.4rem;font-size:.78rem;">
            <b>Fault:</b> {r.get('fault_class','?')} &nbsp;·&nbsp;
            <b>Anomaly:</b> {anom:.2f} &nbsp;·&nbsp;
            <b>Breaches:</b> {r.get('breach_count',0)}
          </div>
          <div style="font-size:.78rem;"><b>RUL:</b> {rul_s}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")  # spacing


def _drilldown(asset_id: str) -> None:
    from vulcan.tools import data_tools as T

    h = S.asset_health(asset_id)
    asset = T.get_asset(asset_id)
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown("**Risk**  \n" + S.risk_badge(S.health_band(h)), unsafe_allow_html=True)
    c2.markdown(f"**Fault class**  \n`{h.get('fault_class','?')}`")
    rul = h.get("rul_cycles")
    c3.markdown(f"**RUL**  \n`{rul:.0f}` cyc (~{h.get('rul_days')} d)" if rul is not None else "**RUL**  \n_n/a_")
    c4.markdown(f"**Anomaly**  \n`{h.get('anomaly_score',0):.3f}`"
                + (" 🔴" if h.get("is_anomaly") else ""))

    st.caption(f"{asset.get('description','')} · {asset.get('manufacturer','')} "
               f"{asset.get('model','')} · {h.get('breach_count',0)} sensor breach(es) "
               "· source: condition_monitoring/by_equipment + ML registry")

    # fault probability bar
    probs = h.get("fault_probs") or {}
    if probs:
        st.markdown("**Fault classifier probabilities**")
        st.bar_chart(pd.DataFrame({"P": probs}).T, height=180)

    cL, cR = st.columns(2)
    with cL:
        st.markdown("**Sensor breaches (latest reading)**")
        breaches = h.get("breaches") or []
        if breaches:
            df = pd.DataFrame(breaches)[["tag", "value", "status", "warning_threshold", "alarm_threshold"]]
            st.dataframe(df, width="stretch", hide_index=True)
        else:
            st.success("All sensors within normal band.")
    with cR:
        st.markdown("**Known failure scenarios (spine)**")
        scns = T.get_scenarios_for_asset(asset_id).get("scenarios", [])
        if scns:
            df = pd.DataFrame(scns)
            st.dataframe(df, width="stretch", hide_index=True)
        else:
            st.caption("_none_")


main()
