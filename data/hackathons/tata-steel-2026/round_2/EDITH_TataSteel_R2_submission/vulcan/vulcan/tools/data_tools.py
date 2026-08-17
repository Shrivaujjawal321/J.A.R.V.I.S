"""VULCAN deterministic data tools — the agent's hands on the flagship dataset.

Every function here is a pure, deterministic read over the
`steel-maintenance-flagship` dataset (spine JSON + CSVs). **No LLM, ever.** These
are the tools the EDITH/VULCAN agents call to fetch real, citable dataset values:
asset specs, ISO/ISA thresholds, sensor readings, failure scenarios, spare-part
availability + procurement lead-time, recent alerts, and maintenance history.

Design notes
------------
* Thin wrappers over the cached :class:`vulcan.data.loaders.DataStore` facade, so
  repeated calls are free (the facade lru-caches parsed spine/CSVs).
* Return plain JSON-able dicts (dataclass -> dict) so they drop straight into an
  agent tool-result / Streamlit panel / report without further marshalling.
* Every result carries a ``source`` ref (spine path or CSV filename) so the
  explainability layer can render an inline citation (FR4: traceable).
* Asset resolution is forgiving: accepts the canonical id (``BF.BLW.FAN01``),
  a sloppy variant (``bf-blw-fan01``), or a sensor tag — and resolves it.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, is_dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from ..data.loaders import (
    Asset,
    CatalogSpare,
    DataStore,
    Scenario,
    get_datastore,
)

# Spine file name used as the citation source for spine-derived facts.
_SPINE_SRC = "SPEC/ground_truth_spine.json"


def _ds() -> DataStore:
    return get_datastore()


# ---------------------------------------------------------------------------
# Asset-id resolution (forgiving)
# ---------------------------------------------------------------------------
def _norm(s: str) -> str:
    return "".join(ch for ch in str(s).upper() if ch.isalnum())


@lru_cache(maxsize=256)
def _resolve_asset_id(query: str) -> str | None:
    """Resolve a loose asset query to a canonical spine asset_id.

    Accepts: exact id, case/separator variants, or a sensor tag that belongs
    to exactly one asset.
    """
    sp = _ds().spine()
    if not query:
        return None
    # 1. exact
    if sp.asset(query) is not None:
        return query
    # 2. normalized match
    nq = _norm(query)
    for a in sp.assets:
        if _norm(a.asset_id) == nq:
            return a.asset_id
    # 3. sensor tag -> asset
    a = sp.asset_for_sensor(query)
    if a is not None:
        return a.asset_id
    # 4. substring on normalized id (last resort, must be unique)
    hits = [a.asset_id for a in sp.assets if nq and nq in _norm(a.asset_id)]
    if len(hits) == 1:
        return hits[0]
    return None


def _asset_obj(asset_id: str) -> Asset | None:
    rid = _resolve_asset_id(asset_id)
    return _ds().spine().asset(rid) if rid else None


# ---------------------------------------------------------------------------
# 1. get_asset
# ---------------------------------------------------------------------------
def get_asset(asset_id: str) -> dict[str, Any]:
    """Return the full registry record for an asset (specs, sensors, failure modes).

    FR2 (knowledge integration) + FR4 (traceable: cites the spine).
    """
    a = _asset_obj(asset_id)
    if a is None:
        return {"found": False, "query": asset_id, "source": _SPINE_SRC,
                "error": f"asset '{asset_id}' not found in registry"}
    return {
        "found": True,
        "asset_id": a.asset_id,
        "equipment_class": a.equipment_class,
        "description": a.description,
        "process_stage": a.process_stage,
        "location": a.location,
        "manufacturer": a.manufacturer,
        "model": a.model,
        "rated_speed_rpm": a.rated_speed_rpm,
        "criticality": a.criticality,          # 1 = most critical
        "installation_date": a.installation_date,
        "last_overhaul_date": a.last_overhaul_date,
        "failure_modes": a.failure_modes,
        "sensor_count": len(a.sensors),
        "sensor_tags": [s.tag for s in a.sensors],
        "source": _SPINE_SRC,
    }


# ---------------------------------------------------------------------------
# 2. get_thresholds
# ---------------------------------------------------------------------------
def get_thresholds(asset_id: str) -> dict[str, Any]:
    """Return per-sensor normal/warning/alarm thresholds + the governing standard.

    These are the ISO/ISA-backed physics thresholds the ML and risk layers use,
    and the numbers a recommendation can cite (FR4 + FR5).
    """
    a = _asset_obj(asset_id)
    if a is None:
        return {"found": False, "query": asset_id, "source": _SPINE_SRC,
                "error": f"asset '{asset_id}' not found"}
    sensors = []
    for s in a.sensors:
        sensors.append({
            "tag": s.tag,
            "quantity": s.quantity,
            "unit": s.unit,
            "normal_range": list(s.normal_range),
            "warning_threshold": s.warning_threshold,
            "alarm_threshold": s.alarm_threshold,
            "standard": s.standard,
            "sampling_rate": s.sampling_rate,
        })
    return {
        "found": True,
        "asset_id": a.asset_id,
        "equipment_class": a.equipment_class,
        "sensors": sensors,
        "source": _SPINE_SRC,
    }


# ---------------------------------------------------------------------------
# Dense per-equipment table resolution (for live sensor reads)
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _dense_table_index() -> dict[str, str]:
    """Map canonical asset_id -> dense by_equipment CSV filename.

    Some classes hold 2 assets and are split per-asset (``<class>__<ASSET>.csv``);
    single-asset classes use ``<class>.csv``. Resolve by matching the asset_id
    found in each file's first data row (authoritative + cheap: one row read).
    """
    ds = _ds()
    out: dict[str, str] = {}
    cdir = ds.settings.condition_dir / "by_equipment"
    for name in ds.list_by_equipment():
        p = cdir / name
        try:
            with p.open("r", encoding="utf-8", newline="") as fh:
                rdr = csv.reader(fh)
                next(rdr, None)             # header
                row = next(rdr, None)       # first data row
            if not row or len(row) < 2:
                continue
            asset_in_file = row[1]          # column 1 = asset_id
            if asset_in_file:
                out[asset_in_file] = name
        except OSError:
            continue
    return out


def _dense_path(asset_id: str) -> Path | None:
    rid = _resolve_asset_id(asset_id)
    if not rid:
        return None
    name = _dense_table_index().get(rid)
    if not name:
        return None
    return _ds().settings.condition_dir / "by_equipment" / name


# ---------------------------------------------------------------------------
# 3. get_sensor_reading / get_sensor_summary
# ---------------------------------------------------------------------------
def _to_float(v: str) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def get_sensor_reading(asset_id: str, index: int = -1) -> dict[str, Any]:
    """Return a single sensor snapshot (one timestamp) from the dense table.

    ``index=-1`` (default) = most recent row; ``index=0`` = first row; any
    positive int = that row. Each value is annotated against the spine thresholds
    so the caller immediately sees which tags breached warning/alarm (FR5/FR7).
    """
    p = _dense_path(asset_id)
    if p is None:
        return {"found": False, "query": asset_id,
                "error": f"no dense sensor table for '{asset_id}'"}
    with p.open("r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        return {"found": False, "query": asset_id, "error": "empty table"}
    if index < 0:
        index = len(rows) + index
    index = max(0, min(index, len(rows) - 1))
    row = rows[index]

    a = _asset_obj(asset_id)
    th_by_tag = {s.tag: s for s in (a.sensors if a else [])}
    meta_cols = {"timestamp", "asset_id", "equipment_class", "fault_label"}
    readings = []
    for col, val in row.items():
        if col in meta_cols:
            continue
        fv = _to_float(val)
        if fv is None:
            continue
        s = th_by_tag.get(col)
        status = "normal"
        if s is not None:
            # J7: derive direction — if alarm_threshold < warning_threshold the sensor is
            # lower-is-worse (e.g. oil pressure: warn 2.2, alarm 2.0).  Mirror the logic
            # in vulcan/alerting/detector.py and in main.py _status().
            wt = s.warning_threshold
            at = s.alarm_threshold
            lower_is_worse = (
                wt is not None and at is not None and float(at) < float(wt)
            )
            if lower_is_worse:
                if at is not None and fv <= float(at):
                    status = "ALARM"
                elif wt is not None and fv <= float(wt):
                    status = "WARNING"
            else:
                if at is not None and fv >= float(at):
                    status = "ALARM"
                elif wt is not None and fv >= float(wt):
                    status = "WARNING"
        readings.append({
            "tag": col,
            "value": round(fv, 4),
            "unit": s.unit if s else None,
            "warning_threshold": s.warning_threshold if s else None,
            "alarm_threshold": s.alarm_threshold if s else None,
            "status": status,
        })
    return {
        "found": True,
        "asset_id": _resolve_asset_id(asset_id),
        "timestamp": row.get("timestamp"),
        "row_index": index,
        "total_rows": len(rows),
        "fault_label": _to_float(row.get("fault_label", "")),
        "readings": readings,
        "source": f"condition_monitoring/by_equipment/{p.name}",
    }


def get_sensor_summary(asset_id: str) -> dict[str, Any]:
    """Per-tag descriptive stats (min/mean/max/last) over the asset's full dense
    history. Light: streams the CSV once, no pandas. Useful for trend context."""
    p = _dense_path(asset_id)
    if p is None:
        return {"found": False, "query": asset_id,
                "error": f"no dense sensor table for '{asset_id}'"}
    a = _asset_obj(asset_id)
    th_by_tag = {s.tag: s for s in (a.sensors if a else [])}
    meta_cols = {"timestamp", "asset_id", "equipment_class", "fault_label"}
    agg: dict[str, dict[str, float]] = {}
    n = 0
    fault_counts: dict[int, int] = {}
    with p.open("r", encoding="utf-8", newline="") as fh:
        rdr = csv.DictReader(fh)
        for row in rdr:
            n += 1
            fl = _to_float(row.get("fault_label", ""))
            if fl is not None:
                fault_counts[int(fl)] = fault_counts.get(int(fl), 0) + 1
            for col, val in row.items():
                if col in meta_cols:
                    continue
                fv = _to_float(val)
                if fv is None:
                    continue
                a_ = agg.setdefault(col, {"min": fv, "max": fv, "sum": 0.0, "n": 0.0, "last": fv})
                a_["min"] = min(a_["min"], fv)
                a_["max"] = max(a_["max"], fv)
                a_["sum"] += fv
                a_["n"] += 1
                a_["last"] = fv
    summaries = []
    for tag, a_ in agg.items():
        s = th_by_tag.get(tag)
        summaries.append({
            "tag": tag,
            "unit": s.unit if s else None,
            "min": round(a_["min"], 4),
            "mean": round(a_["sum"] / a_["n"], 4) if a_["n"] else None,
            "max": round(a_["max"], 4),
            "last": round(a_["last"], 4),
            "warning_threshold": s.warning_threshold if s else None,
            "alarm_threshold": s.alarm_threshold if s else None,
        })
    return {
        "found": True,
        "asset_id": _resolve_asset_id(asset_id),
        "rows": n,
        "fault_label_counts": fault_counts,   # {0: normal, 1: warning, 2: failure}
        "sensors": summaries,
        "source": f"condition_monitoring/by_equipment/{p.name}",
    }


# ---------------------------------------------------------------------------
# 4. get_scenario
# ---------------------------------------------------------------------------
def get_scenario(scenario_id: str) -> dict[str, Any]:
    """Return a ground-truth failure scenario (label, root cause, correct
    resolution, sensor signature, spares, cost/downtime, ISA safety class).

    This is the citation anchor for diagnosis / RCA / cost (FR4)."""
    scn: Scenario | None = _ds().spine().scenario(scenario_id)
    if scn is None:
        return {"found": False, "query": scenario_id, "source": _SPINE_SRC,
                "error": f"scenario '{scenario_id}' not found"}
    return {
        "found": True,
        "scenario_id": scn.scenario_id,
        "asset_id": scn.asset_id,
        "label": scn.label,
        "failure_mode": scn.failure_mode,
        "safety_class": scn.safety_class,           # P1 (worst) .. P4
        "root_cause": scn.root_cause,
        "correct_resolution": scn.correct_resolution,
        "degradation_timeline": scn.degradation_timeline,
        "sensor_signature": scn.sensor_signature,
        "fault_codes": scn.fault_codes,
        "spares_required": [{"part_id": s.part_id, "name": s.name} for s in scn.spares_required],
        "downtime_hours": scn.downtime_hours,
        "cost_impact": scn.cost_impact,
        "source": _SPINE_SRC,
    }


def get_scenarios_for_asset(asset_id: str) -> dict[str, Any]:
    """All scenarios attached to an asset (the asset's failure catalogue)."""
    rid = _resolve_asset_id(asset_id)
    if not rid:
        return {"found": False, "query": asset_id, "error": "asset not found"}
    scns = _ds().spine().scenarios_for_asset(rid)
    return {
        "found": True,
        "asset_id": rid,
        "count": len(scns),
        "scenarios": [
            {"scenario_id": s.scenario_id, "label": s.label,
             "failure_mode": s.failure_mode, "safety_class": s.safety_class}
            for s in scns
        ],
        "source": _SPINE_SRC,
    }


# ---------------------------------------------------------------------------
# 5. get_spare  (availability + procurement lead-time)
# ---------------------------------------------------------------------------
def get_spare(part_id: str) -> dict[str, Any]:
    """Return spare-part availability + procurement intel for a part.

    Merges the procurement catalogue view (on-hand qty, supplier, lead-time,
    in-stock flag) with the spine master (canonical cost, fits-classes). Emits a
    deterministic procurement ``recommendation`` ("IN STOCK" / "ORDER NOW —
    N-week lead") that drives the FR4 spares strategy + cost reasoning."""
    cat = _ds().spare_catalog_by_id().get(part_id)
    master = _ds().spine().spare(part_id)
    if cat is None and master is None:
        return {"found": False, "query": part_id, "error": f"part '{part_id}' not found"}

    on_hand = cat.on_hand if cat else (master.stock_qty or 0)
    lead_weeks = cat.lead_weeks if cat else (master.lead_time_weeks or 0.0)
    in_stock = (cat.available if cat else (on_hand > 0))
    unit_cost = {}
    if master and master.unit_cost:
        unit_cost = master.unit_cost
    elif cat:
        unit_cost = {"inr": _to_float(cat.unit_cost)}

    if in_stock and on_hand > 0:
        rec = "IN STOCK — issue from store"
    elif lead_weeks and lead_weeks >= 12:
        rec = f"NOT IN STOCK — ORDER NOW (long lead: {lead_weeks:.0f} weeks)"
    else:
        rec = f"NOT IN STOCK — order ({lead_weeks:.0f}-week lead)" if lead_weeks else "NOT IN STOCK — order"

    return {
        "found": True,
        "part_id": part_id,
        "name": (cat.name if cat else master.name),
        "on_hand_qty": on_hand,
        "min_qty": (int(_to_float(cat.min_qty) or 0) if cat else None),
        "in_stock": in_stock,
        "lead_time_weeks": lead_weeks,
        "supplier": (cat.supplier if cat else None),
        "criticality": (cat.criticality if cat else None),
        "unit_cost": unit_cost,
        "fits_equipment_class": (master.fits_equipment_class if master else
                                 ([cat.fits_equipment_class] if cat else [])),
        "fits_asset_ids": (cat.fits_asset_ids.split("|") if cat and cat.fits_asset_ids else []),
        "recommendation": rec,
        "source": ("knowledge_docs/spare_parts_catalog.csv" if cat else _SPINE_SRC),
    }


def get_spares_for_scenario(scenario_id: str) -> dict[str, Any]:
    """Resolve the spares a scenario requires into full availability records.

    The core of the FR4 spare-procurement strategy: maps a diagnosed scenario to
    its parts and their order-now/in-stock status + total cost."""
    scn = _ds().spine().scenario(scenario_id)
    if scn is None:
        return {"found": False, "query": scenario_id, "error": "scenario not found"}
    parts = [get_spare(s.part_id) for s in scn.spares_required]
    any_order = any(p.get("found") and not p.get("in_stock") for p in parts)
    max_lead = max((p.get("lead_time_weeks") or 0) for p in parts) if parts else 0
    total_inr = sum((p.get("unit_cost", {}) or {}).get("inr") or 0 for p in parts if p.get("found"))
    return {
        "found": True,
        "scenario_id": scenario_id,
        "asset_id": scn.asset_id,
        "parts": parts,
        "procurement_action_required": any_order,
        "max_lead_time_weeks": max_lead,
        "total_parts_cost_inr": total_inr,
        "source": _SPINE_SRC,
    }


# ---------------------------------------------------------------------------
# 6. get_recent_alerts
# ---------------------------------------------------------------------------
def get_recent_alerts(asset_id: str, limit: int = 10) -> dict[str, Any]:
    """Most-recent anomaly alerts for an asset (sensor, value vs threshold,
    severity, the scenario they map to). Feeds FR7 real-time alerting."""
    rid = _resolve_asset_id(asset_id)
    if not rid:
        return {"found": False, "query": asset_id, "error": "asset not found"}
    alerts = [al for al in _ds().anomaly_alerts() if al.asset_id == rid]
    # already chronological in source; take the tail (most recent)
    recent = alerts[-limit:][::-1]
    rows = [{
        "timestamp": al.timestamp, "sensor": al.sensor,
        "value": _to_float(al.value), "threshold": _to_float(al.threshold),
        "severity": al.severity, "fault_label": _to_float(al.fault_label),
        "scenario_id": al.scenario_id,
    } for al in recent]
    sev_counts: dict[str, int] = {}
    for al in alerts:
        sev_counts[al.severity] = sev_counts.get(al.severity, 0) + 1
    return {
        "found": True,
        "asset_id": rid,
        "total_alerts": len(alerts),
        "severity_counts": sev_counts,
        "recent": rows,
        "source": "condition_monitoring/anomaly_alerts.csv",
    }


# ---------------------------------------------------------------------------
# 7. search_history  (maintenance + incident history)
# ---------------------------------------------------------------------------
def search_history(asset_id: str, limit: int = 10) -> dict[str, Any]:
    """Past maintenance work-orders + incident records for an asset.

    FR2 (history integration) + FR6 (learn from what actually fixed it before)."""
    rid = _resolve_asset_id(asset_id)
    if not rid:
        return {"found": False, "query": asset_id, "error": "asset not found"}
    wos = [r for r in _ds().maintenance_records() if r.asset_id == rid]
    incs = [i for i in _ds().incidents() if i.asset_id == rid]
    wo_rows = [{
        "work_order_id": r.work_order_id, "date": r.date, "type": r.type,
        "task": r.task_description, "sop_ref": r.sop_ref, "parts_used": r.parts_used,
        "downtime_hours": _to_float(r.downtime_hours), "cost": _to_float(r.cost),
        "outcome": r.outcome,
    } for r in wos[-limit:][::-1]]
    inc_rows = [{
        "incident_id": i.incident_id, "start": i.start_ts,
        "failure_mode": i.failure_mode, "severity": i.severity,
        "root_cause": i.root_cause_short, "resolution": i.resolution_short,
        "downtime_hours": _to_float(i.downtime_hours),
        "cost_estimate": _to_float(i.cost_estimate), "scenario_id": i.scenario_id,
        "maintenance_type": i.maintenance_type,
    } for i in incs[-limit:][::-1]]
    return {
        "found": True,
        "asset_id": rid,
        "maintenance_count": len(wos),
        "incident_count": len(incs),
        "maintenance_records": wo_rows,
        "incidents": inc_rows,
        "source": ["knowledge_docs/historical_maintenance_records.csv",
                   "operational_failure/incident_records.csv"],
    }


# ---------------------------------------------------------------------------
# Tool registry (for the agent layer to enumerate available tools)
# ---------------------------------------------------------------------------
TOOLS: dict[str, Any] = {
    "get_asset": get_asset,
    "get_thresholds": get_thresholds,
    "get_sensor_reading": get_sensor_reading,
    "get_sensor_summary": get_sensor_summary,
    "get_scenario": get_scenario,
    "get_scenarios_for_asset": get_scenarios_for_asset,
    "get_spare": get_spare,
    "get_spares_for_scenario": get_spares_for_scenario,
    "get_recent_alerts": get_recent_alerts,
    "search_history": search_history,
}


def _jsonable(obj: Any) -> Any:
    if is_dataclass(obj) and not isinstance(obj, type):
        return asdict(obj)
    return obj


if __name__ == "__main__":
    import json
    print("== get_asset(BF.BLW.FAN01) =="); print(json.dumps(get_asset("BF.BLW.FAN01"), indent=2)[:900])
    print("\n== get_spare(GEAR-WHL-M20) =="); print(json.dumps(get_spare("GEAR-WHL-M20"), indent=2))
    print("\n== get_scenario(SCN-041) =="); print(json.dumps(get_scenario("SCN-041"), indent=2)[:900])
