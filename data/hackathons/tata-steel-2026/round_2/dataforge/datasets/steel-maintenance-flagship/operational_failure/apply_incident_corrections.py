"""
apply_incident_corrections.py
==============================
Applies the audit corrections for the incident_records modality so the shipped
incident_records.csv and ground_truth_spine.json are mutually consistent.

Corrections applied here (CSV + spine):
  #5 (FK integrity, major). The spine had NO FAILURE scenario for the three
     NORMAL-only assets EAF.AUX.HYD01, BF.CW.PMP02, SP.SINT.FAN01, so failure
     rows for them had to borrow a sibling's scenario_id (cross-asset / often
     cross-equipment-class). Fix: add one PRIMARY FAILURE scenario per asset
     (SCN-049/050/051) covering its most representative registry failure_mode,
     then repoint the matching incident rows to their OWN asset's scenario_id.
     This mirrors the catalog's one-FAILURE-scenario-per-asset pattern (the
     other 12 assets each have exactly one cataloged FAILURE scenario for their
     primary mode; secondary-mode rows stay blank). Strict FK contract: a
     scenario_id may only be set when BOTH asset_id AND failure_mode match.

  #6 (minor). Add a `maintenance_type` column (planned|unplanned) so the single
     downtime_hours column can be reconciled to the scenario's planned vs
     unplanned figure. Heuristic: rows whose resolution/root-cause signals a
     proactive / planned-window catch (or whose downtime equals the scenario's
     PLANNED value) are 'planned'; emergency / trip / immediate-stop events are
     'unplanned'.

Re-runnable / idempotent: spine scenarios are upserted by id; the CSV column is
re-derived each run; FK repoint is anchored to the (asset, mode) -> scenario map.
"""

import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SPINE = os.path.join(HERE, "..", "SPEC", "ground_truth_spine.json")
CSV_PATH = os.path.join(HERE, "incident_records.csv")

# --- New PRIMARY FAILURE scenarios for the three NORMAL-only assets ----------
NEW_SCENARIOS = [
    {
        "scenario_id": "SCN-049",
        "asset_id": "EAF.AUX.HYD01",
        "label": "FAILURE",
        "failure_mode": "filter_clog",
        "degradation_timeline": {
            "healthy": "filter DP 0.0-1.5 bar",
            "warning": "DP rising 1.5->3.0 bar (EAF dust ingress)",
            "alarm": "DP 4.5 bar (element blinding, bypass risk)",
            "failure": "filter fully blind -> bypass opens, unfiltered oil to servos",
        },
        "sensor_signature": {
            "JSR.MS.EAF1.HYD.FILT.DP": {
                "normal_value": 1.0,
                "defect_value": 4.5,
                "threshold_crossed": True,
            }
        },
        "fault_codes": ["HYD-FILT-DP-ALARM"],
        "root_cause": "Filter element blinding from systematic EAF dust ingress via breather; differential pressure reaches the 4.5 bar bypass threshold.",
        "correct_resolution": [
            "Isolate HPU",
            "Replace FLT-HYD-10 element set",
            "Clean suction strainer; fit desiccant breather",
            "Verify DP <1.5 bar on restart; tighten PM cadence to weekly",
        ],
        "spares_required": [
            {"part_id": "FLT-HYD-10", "name": "Hydraulic filter element 10um"}
        ],
        "downtime_hours": {"planned": 4, "unplanned": 4},
        "cost_impact": {"inr": 200000, "usd": 2395},
        "safety_class": "P4",
    },
    {
        "scenario_id": "SCN-050",
        "asset_id": "BF.CW.PMP02",
        "label": "FAILURE",
        "failure_mode": "pump_bearing_failure",
        "degradation_timeline": {
            "healthy": "bearing temp 40-70C, 1x vib <1.8mm/s",
            "warning": "bearing temp ->85C, broadband vib ->2.5mm/s",
            "alarm": "bearing temp 100C + 1x vib 5.6mm/s (cage distress)",
            "failure": "bearing cage fracture / seizure",
        },
        "sensor_signature": {
            "JSR.BF.CW.PMP02.TEMP.BRG": {
                "normal_value": 55,
                "defect_value": 100,
                "threshold_crossed": True,
            },
            "JSR.BF.CW.PMP02.VIB.1X": {
                "normal_value": 1.2,
                "defect_value": 5.6,
                "threshold_crossed": True,
            },
        },
        "fault_codes": ["BRG-TEMP-ALARM", "VIB-1X-ALARM"],
        "root_cause": "Cooling-water pump bearing degradation (often with secondary seal weep); suction-side water hammer accelerates cage fatigue to fracture.",
        "correct_resolution": [
            "Switch to standby CW pump; isolate + LOTO",
            "Disassemble; replace bearing set + SEAL-MECH-DSC",
            "Inspect shaft for fretting/scoring",
            "Fit suction-line surge damper; reassemble + align",
        ],
        "spares_required": [
            {"part_id": "SEAL-MECH-DSC", "name": "Mechanical seal cartridge SiC/SiC"}
        ],
        "downtime_hours": {"planned": 4, "unplanned": 8},
        "cost_impact": {"inr": 2500000, "usd": 29940},
        "safety_class": "P2",
    },
    {
        "scenario_id": "SCN-051",
        "asset_id": "SP.SINT.FAN01",
        "label": "FAILURE",
        "failure_mode": "mass_imbalance_deposit_shedding",
        "degradation_timeline": {
            "healthy": "1x vib 1.0-2.3mm/s, axial 2x ratio <0.3",
            "warning": "1x vib ->4.5mm/s (asymmetric dust build-up)",
            "alarm": "1x vib 7.1mm/s + axial 2x ratio 0.4 (shedding event)",
            "failure": "rotor mass imbalance -> bearing/shaft overload",
        },
        "sensor_signature": {
            "JSR.SP.FAN01.VIB.1X": {
                "normal_value": 1.8,
                "defect_value": 7.1,
                "threshold_crossed": True,
            },
            "JSR.SP.FAN01.VIB.AXIAL": {
                "normal_value": 0.2,
                "defect_value": 0.4,
                "threshold_crossed": True,
            },
        },
        "fault_codes": ["VIB-1X-ALARM", "IMBALANCE-SHED"],
        "root_cause": "Asymmetric dust-cake shedding from the sinter-fan rotor causes a step mass imbalance; 1x vibration jumps from baseline to the 7.1 mm/s alarm.",
        "correct_resolution": [
            "Emergency stop; access fan housing",
            "Manually clean rotor deposits",
            "Dynamic balance online; trim with BAL-WT-01",
            "Apply erosion-resistant hard-facing if recurring; verify <4.5 mm/s",
        ],
        "spares_required": [
            {"part_id": "BAL-WT-01", "name": "Balancing weights set"}
        ],
        "downtime_hours": {"planned": 0, "unplanned": 24},
        "cost_impact": {"inr": 8000000, "usd": 95808},
        "safety_class": "P2",
    },
]

FIELDNAMES = [
    "incident_id", "asset_id", "start_ts", "end_ts", "downtime_hours",
    "failure_mode", "severity", "root_cause_short", "resolution_short",
    "cost_estimate", "scenario_id", "maintenance_type",
]

PLANNED_HINTS = (
    "planned", "planned-window", "planned weekend", "planned stop",
    "planned outage", "planned plate change", "force work roll change early",
    "schedule", "next outage", "next shutdown", "next major outage",
    "annual mfl", "expedite",
)
UNPLANNED_HINTS = (
    "emergency stop", "immediately", "controlled stop", "controlled trip",
    "controlled shutdown", "trip", "auto cutoff", "auto fuel cutoff",
    "out of service", "oos", "stop belt", "stop immediately", "isolate hpu",
    "end heat", "switch to standby", "purge",
)


def classify_maintenance_type(row):
    """planned vs unplanned from resolution/root-cause language."""
    text = (row["resolution_short"] + " " + row["root_cause_short"]).lower()
    # Strong planned signals win over generic unplanned verbs.
    if any(h in text for h in PLANNED_HINTS):
        return "planned"
    if any(h in text for h in UNPLANNED_HINTS):
        return "unplanned"
    # Fallback: treat as unplanned (reactive event).
    return "unplanned"


def upsert_scenarios(spine):
    cat = spine["failure_scenario_catalog"]
    by_id = {s["scenario_id"]: i for i, s in enumerate(cat)}
    for sc in NEW_SCENARIOS:
        if sc["scenario_id"] in by_id:
            cat[by_id[sc["scenario_id"]]] = sc
        else:
            cat.append(sc)
    cat.sort(key=lambda s: s["scenario_id"])


def main():
    spine = json.load(open(SPINE))
    upsert_scenarios(spine)
    json.dump(spine, open(SPINE, "w"), indent=2, ensure_ascii=False)

    # (asset, mode) -> scenario_id for ALL FAILURE scenarios (incl. new ones)
    valid_fk = {
        (s["asset_id"], s["failure_mode"]): s["scenario_id"]
        for s in spine["failure_scenario_catalog"]
        if s.get("label") != "NORMAL"
    }

    rows = list(csv.DictReader(open(CSV_PATH)))
    repointed = 0
    for r in rows:
        want = valid_fk.get((r["asset_id"], r["failure_mode"]), "")
        if want and r.get("scenario_id", "").strip() != want:
            repointed += 1
        r["scenario_id"] = want  # strict FK: blank when no exact (asset,mode) match
        r["maintenance_type"] = classify_maintenance_type(r)

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(rows)

    # ---- verification ----
    scn_asset = {s["scenario_id"]: s["asset_id"]
                 for s in spine["failure_scenario_catalog"]}
    scn_mode = {s["scenario_id"]: s["failure_mode"]
                for s in spine["failure_scenario_catalog"]}
    bad = sum(
        1 for r in rows if r["scenario_id"] and
        (scn_asset.get(r["scenario_id"]) != r["asset_id"]
         or scn_mode.get(r["scenario_id"]) != r["failure_mode"])
    )
    print(f"scenarios in catalog : {len(spine['failure_scenario_catalog'])}")
    print(f"rows                 : {len(rows)}")
    print(f"rows repointed       : {repointed}")
    print(f"rows with scenario_id: {sum(1 for r in rows if r['scenario_id'])}")
    print(f"residual FK violations: {bad}")
    mt = {}
    for r in rows:
        mt[r["maintenance_type"]] = mt.get(r["maintenance_type"], 0) + 1
    print(f"maintenance_type     : {mt}")
    assert bad == 0, "FK contract violated"


if __name__ == "__main__":
    main()
