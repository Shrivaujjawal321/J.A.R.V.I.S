"""VULCAN report builder — deterministic, dataset-grounded Markdown reports.

Every number in a report traces to a dataset source (spine / SOP / catalog / ML
artifact). The builders accept either a live :class:`TurnResult` from the agentic
core OR raw ids (in which case they run the supervisor once to ground the report).
No fabrication: a missing value renders as ``_not available_``.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from ..tools import data_tools as T


@dataclass
class Report:
    """A rendered report: id + Markdown body + a structured dict mirror."""

    report_id: str
    kind: str                      # incident | alert | decision
    title: str
    markdown: str
    data: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.markdown


# ---------------------------------------------------------------------------
def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _rid(prefix: str) -> str:
    return f"{prefix}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"


def _na(v: Any) -> str:
    if v is None or v == "" or v == [] or v == {}:
        return "_not available_"
    return str(v)


def _bullets(items: list[Any], prefix: str = "- ") -> str:
    if not items:
        return "_none_"
    return "\n".join(f"{prefix}{x}" for x in items)


def _run_turn(asset_id: str, scenario_id: Optional[str], intent: str = "report",
              run_gate: bool = False) -> Any:
    """Run the agentic core once to ground a report (lazy import to avoid cycles)."""
    from ..agents import Supervisor
    sup = Supervisor()
    q = (f"Generate a full maintenance report for asset {asset_id}"
         + (f" scenario {scenario_id}" if scenario_id else ""))
    # use the alert path when we have a scenario (it's the proactive, grounded one)
    if scenario_id:
        return sup.handle_alert(asset_id=asset_id, scenario_id=scenario_id,
                                severity="report", session_id="reports",
                                run_gate=run_gate)
    return sup.handle_query(q, session_id="reports", run_gate=run_gate)


def _findings(turn: Any) -> dict[str, Any]:
    """Pull the structured agent findings off a TurnResult (dict-or-obj safe)."""
    f = getattr(turn, "findings", None)
    return f or {}


# ===========================================================================
# 1. INCIDENT REPORT  (per-incident structured maintenance report)
# ===========================================================================
def incident_report(
    asset_id: str,
    scenario_id: Optional[str] = None,
    *,
    turn: Any = None,
    run_gate: bool = False,
) -> Report:
    """Full per-incident maintenance report grounded in the agentic findings."""
    if turn is None:
        turn = _run_turn(asset_id, scenario_id, intent="report", run_gate=run_gate)
    f = _findings(turn)
    asset = T.get_asset(asset_id)
    aid = asset.get("asset_id", asset_id)
    scn = (f["diagnosis"].data.get("matched_scenario", {})
           if "diagnosis" in f else (T.get_scenario(scenario_id) if scenario_id else {}))
    sid = scn.get("scenario_id") or scenario_id

    rca = f.get("rca")
    pred = f.get("predictor")
    prio = f.get("prioritizer")
    rec = f.get("recommender")

    risk_band = getattr(turn, "risk_band", None) or (prio.data.get("risk_band") if prio else None)
    rul = getattr(turn, "rul", None) or (pred.data.get("rul") if pred else None)

    # spares / procurement
    spares = rec.data.get("spares", {}) if rec else (
        T.get_spares_for_scenario(sid) if sid else {})
    procurement = rec.data.get("procurement_strategy", []) if rec else []
    total_cost = (rec.data.get("total_parts_cost_inr") if rec
                  else spares.get("total_parts_cost_inr"))

    rid = _rid("INC")
    rows = [
        f"# EDITH Maintenance Report · {rid}",
        f"_Generated {_now_iso()} · persona EDITH · grounded in the steel-maintenance-flagship dataset_",
        "",
        "## 1. Asset",
        f"- **Asset**: `{aid}` — {_na(asset.get('description'))}",
        f"- **Equipment class**: {_na(asset.get('equipment_class'))}",
        f"- **Process stage**: {_na(asset.get('process_stage'))}",
        f"- **Process criticality**: {_na(asset.get('criticality'))} (1 = most critical)",
        f"- **Manufacturer / model**: {_na(asset.get('manufacturer'))} / {_na(asset.get('model'))}",
        "  \n  _source: SPEC/ground_truth_spine.json_",
        "",
        "## 2. Diagnosis",
        f"- **Probable failure mode**: {_na(scn.get('failure_mode'))}"
        + (f" (scenario `{sid}`)" if sid else ""),
        f"- **Safety class**: {_na(scn.get('safety_class'))} (P1 = most severe)",
    ]
    if "diagnosis" in f:
        ml = f["diagnosis"].data.get("ml_fault", {})
        rows.append(f"- **ML fault classifier**: class `{_na(ml.get('predicted_class'))}` "
                    f"P(failure)={_na((ml.get('probabilities', {}) or {}).get('FAILURE'))}")
        br = f["diagnosis"].data.get("threshold_breaches", [])
        if br:
            rows.append("- **Sensor threshold breaches**:")
            for b in br[:6]:
                rows.append(f"    - `{b['tag']}` = {b['value']} → **{b['status']}** "
                            f"(warn {b.get('warning_threshold')}, alarm {b.get('alarm_threshold')})")
        rows.append("  \n  _source: condition_monitoring/by_equipment + ML fault classifier_")
    rows += [
        "",
        "## 3. Root Cause Analysis",
        f"- **Root cause**: {_na(rca.data.get('root_cause') if rca else scn.get('root_cause'))}",
        "  \n  _source: SPEC/ground_truth_spine.json + failure_analysis_reports_",
        "",
        "## 4. Remaining Useful Life (RUL) & Early Warning",
    ]
    if rul:
        rows += [
            f"- **Estimated RUL**: {_na(rul.get('rul_cycles'))} cycles "
            f"(~{_na(rul.get('rul_days_estimate'))} days)",
            f"- **RUL band**: {_na(pred.data.get('rul_band') if pred else None)}",
        ]
        if pred:
            an = pred.data.get("anomaly", {})
            rows.append(f"- **Anomaly score**: {_na(an.get('anomaly_score'))} "
                        f"(is_anomaly={_na(an.get('is_anomaly'))})")
        rows.append("  \n  _source: condition_monitoring/rul_trajectories_long.csv (ML RUL regressor)_")
    else:
        rows.append("- RUL: _not available_")
    rows += [
        "",
        "## 5. Risk Classification",
        f"- **Risk band**: **{_na(risk_band)}**",
    ]
    if prio:
        rows.append(f"- **Risk score**: {prio.data.get('risk_score'):.1f} / 14")
        rows.append("- **Contributing factors** (transparent scoring):")
        for fac in prio.data.get("factors", []):
            rows.append(f"    - {fac}")
        if prio.data.get("feedback_points"):
            rows.append(f"    - _(includes engineer-feedback adjustment: "
                        f"{prio.data['feedback_points']:+} pts — FR6)_")
        rows.append("  \n  _source: criticality × safety × ML × RUL × spares lead-time + feedback weight_")
    rows += [
        "",
        "## 6. Prioritized Recommended Actions",
        _bullets([f"**{i+1}.** {s}" for i, s in
                  enumerate((rec.data.get('resolution_steps') if rec else scn.get('correct_resolution')) or [])]),
        "  \n  _source: SPEC correct_resolution + maintenance SOP_",
        "",
        "## 7. Spare-Procurement Strategy",
        _bullets(procurement),
        f"\n- **Total parts cost**: INR {_na(total_cost)}",
        f"- **Max procurement lead-time**: {_na(spares.get('max_lead_time_weeks'))} weeks",
        f"- **Procurement action required**: {_na(spares.get('procurement_action_required'))}",
        "  \n  _source: knowledge_docs/spare_parts_catalog.csv + SPEC spares_required_",
        "",
        "## 8. Estimated Downtime & Cost Impact",
        f"- **Downtime (hours)**: {_na(scn.get('downtime_hours'))}",
        f"- **Cost impact**: {_na(scn.get('cost_impact'))}",
        "  \n  _source: SPEC/ground_truth_spine.json — scenario_",
        "",
        "## 9. EDITH Narrative (synthesised)",
        getattr(turn, "answer", "_not available_"),
        "",
        "## 10. Explainability",
        f"- **Confidence**: {_na(getattr(turn, 'confidence', None))} "
        f"(faithfulness {_na(getattr(turn, 'faithfulness', None))})",
        f"- **LLM rung**: {_na(getattr(turn, 'llm_rung', None))}",
        f"- **Reasoning-trace steps**: {len(getattr(turn, 'trace').steps) if getattr(turn, 'trace', None) else 0}",
        f"- **Grounded sources**: {', '.join(getattr(turn, 'sources', []) or []) or '_none_'}",
    ]
    md = "\n".join(rows)
    return Report(report_id=rid, kind="incident",
                  title=f"Incident report — {aid} ({scn.get('failure_mode', 'fault')})",
                  markdown=md,
                  data={"asset_id": aid, "scenario_id": sid, "risk_band": risk_band,
                        "rul": rul, "total_cost_inr": total_cost,
                        "procurement": procurement,
                        "trace": getattr(turn, "trace").to_dict() if getattr(turn, "trace", None) else {}})


# ===========================================================================
# 2. ALERT REPORT  (from a fired alerting episode — FR7)
# ===========================================================================
def alert_report(episode: Any) -> Report:
    """Build a real-time alert report from a fired alerting EpisodeResult."""
    ep = episode.to_dict() if hasattr(episode, "to_dict") else dict(episode)
    rid = _rid("ALR")
    aid = ep.get("asset_id")
    sid = ep.get("scenario_id")
    timeline = ep.get("timeline", [])
    fc = ep.get("first_critical") or {}
    diag = ep.get("diagnosis") or {}

    rows = [
        f"# EDITH Real-Time Alert Report · {rid}",
        f"_Generated {_now_iso()} · autonomous condition-monitoring (FR7) · LLM-free detector_",
        "",
        f"## Asset under alert: `{aid}`",
        f"- **Episode**: {ep.get('title')}",
        f"- **Mapped scenario**: `{_na(sid)}`",
        f"- **Rows replayed**: {ep.get('rows_scanned')}",
        f"- **Alert events fired**: {ep.get('event_count')}",
        f"- **Autonomous CRITICAL fired**: **{ep.get('fired_critical')}**",
        "",
        "## Escalation timeline (deterministic threshold detector)",
        "| Severity | Source timestamp | Sensor | Value | Row | Trigger |",
        "|---|---|---|---|---|---|",
    ]
    for t in timeline:
        rows.append(f"| **{t['severity']}** | {t['timestamp']} | `{t['sensor']}` | "
                    f"{t['value']} | {t['row_index']} | {t.get('reason', '')} |")
    rows += [
        "",
        "## Autonomous CRITICAL trip",
        f"- **Sensor**: `{_na(fc.get('sensor'))}` = {_na(fc.get('value'))}{fc.get('unit') or ''}",
        f"- **Crossed alarm threshold**: {_na(fc.get('alarm_threshold'))} "
        f"(standard: {_na(fc.get('standard'))})",
        f"- **At source timestamp**: {_na(fc.get('timestamp'))} (row {_na(fc.get('row_index'))})",
        f"- **Ground-truth fault_label**: {_na(fc.get('fault_label'))} (2 = confirmed FAILURE)",
        f"- **Trigger reason**: {_na(fc.get('reason'))}",
        "  \n  _source: SPEC thresholds + condition_monitoring/by_equipment replay_",
        "",
        "## Agentic diagnosis hand-off (FR4 explainable)",
    ]
    if diag:
        rows += [
            f"- **Diagnosis**: {_na(diag.get('intent'))} on `{_na(diag.get('asset_id'))}` "
            f"(scenario `{_na(diag.get('scenario_id'))}`)",
            f"- **Risk band**: **{_na(diag.get('risk_band'))}**",
            f"- **RUL**: {_na((diag.get('rul') or {}).get('rul_cycles'))} cycles "
            f"(~{_na((diag.get('rul') or {}).get('rul_days_estimate'))} days)",
            f"- **Confidence**: {_na(diag.get('confidence'))} "
            f"(faithfulness {_na(diag.get('faithfulness'))}, rung {_na(diag.get('llm_rung'))})",
            "",
            "### EDITH diagnosis",
            _na(diag.get("answer")),
        ]
    else:
        rows.append("- _Diagnosis hand-off not run / unavailable (detector still fired autonomously)._")
    md = "\n".join(rows)
    return Report(report_id=rid, kind="alert",
                  title=f"Alert report — {aid} CRITICAL",
                  markdown=md, data=ep)


# ===========================================================================
# 3. DECISION SUMMARY  (one-screen action card)
# ===========================================================================
def decision_summary(
    asset_id: str,
    scenario_id: Optional[str] = None,
    *,
    turn: Any = None,
) -> Report:
    """A 10-second action card for a shift engineer: band, next action, order-now."""
    if turn is None:
        turn = _run_turn(asset_id, scenario_id, intent="recommend")
    f = _findings(turn)
    asset = T.get_asset(asset_id)
    aid = asset.get("asset_id", asset_id)
    scn = (f["diagnosis"].data.get("matched_scenario", {}) if "diagnosis" in f else {})
    sid = scn.get("scenario_id") or scenario_id
    rec = f.get("recommender")
    pred = f.get("predictor")

    risk_band = getattr(turn, "risk_band", None)
    order_now = rec.data.get("order_now", []) if rec else []
    first_step = ((rec.data.get("resolution_steps") if rec else scn.get("correct_resolution")) or ["_not available_"])[0]
    rul = getattr(turn, "rul", None) or (pred.data.get("rul") if pred else None)

    order_line = "_no part needs ordering (all in stock)_"
    if order_now:
        p = order_now[0]
        order_line = (f"**ORDER NOW** `{p['part_id']}` ({p.get('name', '')}) — "
                      f"{p.get('lead_time_weeks', 0):.0f}-week lead"
                      + (f", supplier {p['supplier']}" if p.get("supplier") else ""))

    rid = _rid("DEC")
    rows = [
        f"# ⚡ EDITH Decision Card · `{aid}`",
        f"_{_now_iso()} · scenario {_na(sid)}_",
        "",
        f"## 🔴 RISK: **{_na(risk_band)}**",
        f"- **Probable fault**: {_na(scn.get('failure_mode'))} "
        f"(safety {_na(scn.get('safety_class'))})",
        f"- **Time you have**: RUL ≈ {_na(rul.get('rul_cycles') if rul else None)} cycles "
        f"(~{_na(rul.get('rul_days_estimate') if rul else None)} days)",
        "",
        f"## ✅ DO THIS FIRST",
        f"> {first_step}",
        "",
        f"## 📦 PROCUREMENT",
        f"> {order_line}",
        "",
        "_Full report available via EDITH incident report. Grounded in spine + SOP + catalog._",
    ]
    md = "\n".join(rows)
    return Report(report_id=rid, kind="decision",
                  title=f"Decision card — {aid}",
                  markdown=md,
                  data={"asset_id": aid, "scenario_id": sid, "risk_band": risk_band,
                        "first_action": first_step, "order_now": order_now, "rul": rul})


# ---------------------------------------------------------------------------
def save_report(report: Report, out_dir: Path | str | None = None) -> Path:
    """Write a report to `<package_root>/data/reports/<report_id>.md`."""
    if out_dir is None:
        from ..config import get_settings
        out_dir = get_settings().package_root / "data" / "reports"
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{report.report_id}.md"
    path.write_text(report.markdown, encoding="utf-8")
    return path
