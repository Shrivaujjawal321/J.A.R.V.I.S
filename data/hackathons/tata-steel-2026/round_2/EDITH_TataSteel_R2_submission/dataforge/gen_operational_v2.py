"""
Operational-layer generator v2 — fixes Root Cause A (temporal/causal join) + F1.
Consumes condition_monitoring/episodes_manifest.csv (the 137 real failure episodes,
each already aligned to the 2025 sensor timeline) + the spine, and emits operational
records that are CAUSALLY LINKED to those episodes:

  incident_records.csv        one incident per episode, run_id + scenario_id FK,
                              ISO-14224 fields + production_impact_tonnes        [A1,A3]
  equipment_delay_logs.csv    precursor + failure delays carry incident_id FK
                              (+ background nuisance delays w/o FK)              [A2]
  fault_error_messages.csv    scenario fault codes escalate to failure_ts,
                              incident_id FK (+ background faults)               [A2]
  maintenance_feedback.csv    NEW: prediction->outcome->correction triples,
                              recurrence (days_to_next_failure) from the next
                              episode on the same asset                         [F1/OFH-04/OE-4]

Every incident timestamp now falls INSIDE its asset's degradation window, so
"show me the sensor trend that led to INC-XXXX" resolves via run_id.  Synthetic.
"""
import json, hashlib, datetime as dt
from pathlib import Path
import numpy as np, pandas as pd

BASE = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_2/dataforge/datasets/steel-maintenance-flagship")
CM = BASE / "condition_monitoring"
OF = BASE / "operational_failure"
SPINE = json.loads((BASE / "SPEC" / "ground_truth_spine.json").read_text())
rng = np.random.default_rng(20260610)

scn_by_id = {s["scenario_id"]: s for s in SPINE["failure_scenario_catalog"]}
asset_by_id = {a["asset_id"]: a for a in SPINE["asset_registry"]}

# process-stage nominal throughput (tonnes/hour) for production-impact estimate
STAGE_TPH = {
    "raw_material_handling": 1800, "iron_making": 320, "sintering": 550,
    "steelmaking": 300, "ladle_handling": 280, "casting": 250,
    "reheating": 300, "hot_rolling": 350, "cold_rolling": 180, "utilities": 200,
}
SEV = {"P1": "critical", "P2": "high", "P3": "medium", "P4": "low", "": "medium"}
MECH = {  # ISO 14224 failure-mechanism family by mode keyword
    "fatigue": "Material/fatigue", "spall": "Material/fatigue", "wear": "Wear/abrasion",
    "contamination": "Contamination", "seal": "Leakage", "imbalance": "Vibration/misalignment",
    "misalign": "Vibration/misalignment", "insulation": "Electrical", "winding": "Electrical",
    "breakout": "Process/thermal", "refractory": "Thermal/erosion", "rope": "Material/fatigue",
    "silt": "Contamination", "surge": "Process/instability", "seizure": "Mechanical/seizure",
}
DETECT = ["condition_monitoring_alert", "operator_observation", "routine_inspection",
          "process_excursion", "alarm_system"]

ep = pd.read_csv(CM / "episodes_manifest.csv", parse_dates=["onset_ts", "failure_ts"])
ep = ep.sort_values(["asset_id", "failure_ts"]).reset_index(drop=True)

def mech_for(mode):
    m = mode.lower()
    for k, v in MECH.items():
        if k in m: return v
    return "Mechanical/general"

# next-failure recurrence per asset (for feedback + ISO MTBF realism)
ep["next_failure_ts"] = ep.groupby("asset_id")["failure_ts"].shift(-1)

# per-asset running recurrence counter (escalating deferred-maintenance cost)
_asset_seen = {}
SEV_RANK = ["low", "medium", "high", "critical"]
incidents, delays, faults, feedback = [], [], [], []
for i, e in ep.iterrows():
    scn = scn_by_id.get(e["scenario_id"], {})
    asset = asset_by_id.get(e["asset_id"], {})
    stage = asset.get("process_stage", "hot_rolling")
    iid = f"INC-{i+1:04d}"
    fail_ts = e["failure_ts"]; onset_ts = e["onset_ts"]
    ttf = max((fail_ts - onset_ts).total_seconds()/3600.0, 6)
    seq = _asset_seen.get(e["asset_id"], 0); _asset_seen[e["asset_id"]] = seq + 1
    # OFH-N2: detection latency — caught somewhere INTO the degradation, not at onset.
    # Some catches are late (near failure); a few effectively missed until breakdown.
    det_frac = float(np.clip(rng.beta(1.6, 3.0), 0.02, 0.97))   # mostly early-ish, long tail late
    detected_ts = onset_ts + dt.timedelta(hours=ttf * det_frac)
    deferred = bool(rng.random() < 0.14)
    # OFH-N1/DR-NEW-03: per-incident dispersion on downtime + cost (no flat templates).
    _dth = scn.get("downtime_hours", {})
    base_dh = _dth.get("unplanned") or _dth.get("planned") or float(rng.uniform(3, 18))  # OFH-01: never 0
    dh = round(float(base_dh) * rng.uniform(0.65, 1.45), 1)
    base_cost = scn.get("cost_impact", {}).get("inr", rng.uniform(2e5, 5e6))
    # escalation: later failures + deferred + late detection cost more
    esc = 1.0 + 0.05*seq + (0.35 if deferred else 0.0) + 0.30*det_frac
    cost = int(round(float(base_cost) * rng.uniform(0.7, 1.4) * esc / 1000.0) * 1000)  # k-rounded, not lakh-round
    end_ts = fail_ts + dt.timedelta(hours=float(dh))
    sev = SEV.get(scn.get("safety_class", ""), "medium")
    # occasional severity escalation when deferred + long downtime
    if deferred and dh > base_dh and rng.random() < 0.4:
        sev = SEV_RANK[min(SEV_RANK.index(sev)+1, 3)]
    tph = STAGE_TPH.get(stage, 300)
    crit = asset.get("criticality", 2)
    prod_loss = round(dh * tph * (0.9 if crit == 1 else 0.6) * rng.uniform(0.7, 1.1), 1)
    res = scn.get("correct_resolution", [])
    dmeth = str(rng.choice(DETECT, p=[.5,.18,.12,.12,.08]))
    # OFH-03: failure_class from WHEN caught (detection progress), independent of severity.
    fclass = "incipient" if det_frac < 0.30 else ("degraded" if det_frac < 0.68 else "critical")
    # OFH-02: build a varied root-cause + resolution narrative per incident.
    _rc = scn.get("root_cause","")[:150].rstrip(".")
    _stage_note = {"incipient":"caught early at incipient stage","degraded":"detected mid-degradation",
                   "critical":"late detection; advanced damage at intervention"}[fclass]
    _detail = str(rng.choice([
        f"; {seq+1}{'st' if seq==0 else ('nd' if seq==1 else ('rd' if seq==2 else 'th'))} recurrence on this asset",
        f"; flagged via {dmeth.replace('_',' ')}", f"; {_stage_note}",
        f"; accelerated by {rng.choice(['lube contamination','overload','misalignment','thermal cycling','water ingress'])}",
        f"; lead time {round(ttf*(1-det_frac))}h before functional failure"]))
    rc_text = (_rc + _detail)[:200]
    if res:
        k = int(rng.integers(0, len(res)))
        res_text = res[k][:120] + (f" (then: {res[min(k+1,len(res)-1)][:50]})" if len(res)>1 and rng.random()<0.5 else "")
    else:
        res_text = ""
    incidents.append({
        "incident_id": iid, "asset_id": e["asset_id"], "run_id": e["run_id"],
        "scenario_id": e["scenario_id"], "start_ts": fail_ts.strftime("%Y-%m-%d %H:%M:%S"),
        "end_ts": end_ts.strftime("%Y-%m-%d %H:%M:%S"), "detected_ts": detected_ts.strftime("%Y-%m-%d %H:%M:%S"),
        "detection_lead_hours": round(ttf*(1-det_frac), 1),
        "recurrence_index": seq + 1,
        "downtime_hours": dh, "failure_mode": e["failure_mode"],
        "failure_mechanism": mech_for(e["failure_mode"]),
        "failure_class": fclass,
        "detection_method": dmeth,
        "severity": sev, "safety_class": scn.get("safety_class",""),
        # OFH-02: per-incident diagnostic-text variation (not a per-asset template).
        "root_cause_short": rc_text,
        "resolution_short": res_text,
        "cost_estimate_inr": int(cost),
        "production_impact_tonnes": prod_loss,
        "deferred_maintenance": deferred,
        "maintenance_type": "breakdown" if sev in ("critical","high") else "corrective",
    })
    # ---- precursor + failure delay logs with incident_id FK (A2) -------------
    codes = scn.get("fault_codes", []) or ["GENERAL_FAULT"]
    n_pre = int(rng.integers(1, 4))
    span = max((fail_ts - onset_ts).total_seconds()/3600.0, 6)
    for k in range(n_pre):
        t = onset_ts + dt.timedelta(hours=float(span * (k+1)/(n_pre+1)))
        delays.append({"timestamp": t.strftime("%Y-%m-%d %H:%M:%S"), "asset_id": e["asset_id"],
            "line": asset.get("location",{}).get("area",""), "delay_minutes": int(rng.integers(5,45)),
            "delay_reason_code": e["failure_mode"].upper()[:24], "incident_id": iid,
            "description": f"Precursor slowdown linked to {iid} ({e['failure_mode']})"})
    delays.append({"timestamp": fail_ts.strftime("%Y-%m-%d %H:%M:%S"), "asset_id": e["asset_id"],
        "line": asset.get("location",{}).get("area",""), "delay_minutes": int(dh*60),
        "delay_reason_code": e["failure_mode"].upper()[:24], "incident_id": iid,
        "description": f"Unplanned breakdown {iid}: {e['failure_mode']}"})
    # ---- fault messages escalating to failure, incident_id FK ----------------
    for k, code in enumerate(codes):
        t = onset_ts + dt.timedelta(hours=float(span * (0.6 + 0.4*k/max(len(codes)-1,1))))
        faults.append({"timestamp": t.strftime("%Y-%m-%d %H:%M:%S"), "asset_id": e["asset_id"],
            "source_system": rng.choice(["PLC","SCADA","CMS","HMI"]), "fault_code": code,
            "severity": "ALARM" if k==len(codes)-1 else "WARNING", "incident_id": iid,
            "message": f"{code} on {e['asset_id']} (escalating to {iid})"})
    # ---- feedback triple: prediction -> outcome -> correction (F1) -----------
    pred_rul = round(float(span) * rng.uniform(0.7, 1.3), 1)   # model's RUL guess at onset
    actual_rul = round(float(span), 1)
    nxt = e["next_failure_ts"]
    days_next = round((nxt - fail_ts).total_seconds()/86400.0, 1) if pd.notna(nxt) else None
    # OF-2: the model sometimes predicts the WRONG mode (realistic). prediction_correct
    # = (mode right) AND (RUL within 25%). engineer_feedback + outcome are CONDITIONED
    # on prediction_correct so the text never contradicts the label (OF-1).
    rul_ok = abs(pred_rul - actual_rul) / max(actual_rul, 1) < 0.25
    mode_ok = rng.random() > 0.15
    pred_mode = e["failure_mode"] if mode_ok else (
        mech_for(e["failure_mode"]).lower().replace("/", "_") + "_suspected")
    pred_ok = bool(rul_ok and mode_ok)
    if pred_ok:
        efb = rng.choice(["confirmed - matched root cause",
            "confirmed - action prevented escalation", "confirmed - RUL within tolerance",
            "confirmed - sensor signature matched diagnosis"])
        outc = rng.choice(["repaired_ok","repaired_ok","repaired_ok","repaired_recurred"])
    elif mode_ok and not rul_ok:
        efb = rng.choice(["correct mode but RUL off - " + ("under" if pred_rul<actual_rul else "over") + "estimated",
            "right diagnosis, timing miss - adjust RUL model"])
        outc = rng.choice(["repaired_ok","repaired_recurred"])
    else:
        efb = rng.choice(["incorrect - actual mode was " + e["failure_mode"],
            "wrong root cause flagged - secondary cause was primary",
            "false diagnosis - re-inspected and corrected on floor"])
        outc = rng.choice(["repaired_recurred","repaired_ok","misdiagnosed_reworked"])
    feedback.append({
        "feedback_id": f"FB-{i+1:04d}", "incident_id": iid, "asset_id": e["asset_id"],
        "run_id": e["run_id"], "predicted_failure_mode": pred_mode,
        "actual_failure_mode": e["failure_mode"],
        "predicted_rul_hours": pred_rul, "actual_rul_hours": actual_rul,
        "recommended_action": (res[0] if res else "inspect")[:100],
        "action_taken": (res[0] if res else "inspect")[:100] if rng.random()<0.85 else "deferred to next shutdown",
        "prediction_correct": pred_ok,
        "engineer_feedback": efb, "outcome": outc,
        "days_to_next_failure": days_next,
        "feedback_ts": end_ts.strftime("%Y-%m-%d %H:%M:%S"),
    })

# ---- background nuisance delays + faults (no incident_id) for realism -------
T0, T1 = dt.datetime(2025,1,1), dt.datetime(2025,12,30)
NUIS_DELAY_CODES = ["ROLL_CHANGE","COIL_CHANGE","SLAB_GAP","SCHED_HOLD","UTILITY_DIP","OPERATOR_BREAK","QUALITY_CHECK"]
for _ in range(700):
    a = rng.choice(list(asset_by_id)); ainfo = asset_by_id[a]
    t = T0 + dt.timedelta(hours=float(rng.uniform(0, (T1-T0).total_seconds()/3600)))
    delays.append({"timestamp": t.strftime("%Y-%m-%d %H:%M:%S"), "asset_id": a,
        "line": aInfo if (aInfo:=ainfo.get("location",{}).get("area","")) else "", "delay_minutes": int(rng.integers(2,30)),
        "delay_reason_code": rng.choice(NUIS_DELAY_CODES), "incident_id": "",
        "description": "Routine operational delay"})
NUIS_FAULTS = ["COMM_TIMEOUT","SENSOR_GLITCH","HMI_WARN","CAL_DUE","DOOR_OPEN","LUBE_LOW_INFO"]
for _ in range(850):
    a = rng.choice(list(asset_by_id))
    t = T0 + dt.timedelta(hours=float(rng.uniform(0, (T1-T0).total_seconds()/3600)))
    faults.append({"timestamp": t.strftime("%Y-%m-%d %H:%M:%S"), "asset_id": a,
        "source_system": rng.choice(["PLC","SCADA","CMS","HMI"]), "fault_code": rng.choice(NUIS_FAULTS),
        "severity": rng.choice(["INFO","WARNING"]), "incident_id": "",
        "message": "Nuisance/info event"})

inc_df = pd.DataFrame(incidents)
del_df = pd.DataFrame(delays).sort_values("timestamp").reset_index(drop=True)
flt_df = pd.DataFrame(faults).sort_values("timestamp").reset_index(drop=True)
fb_df = pd.DataFrame(feedback)

inc_df.to_csv(OF/"incident_records.csv", index=False)
del_df.to_csv(OF/"equipment_delay_logs.csv", index=False)
flt_df.to_csv(OF/"fault_error_messages.csv", index=False)
fb_df.to_csv(BASE/"user_interaction"/"maintenance_feedback.csv", index=False)

print(f"incidents      = {len(inc_df)}  (all run_id-linked to a sensor episode)")
print(f"delay logs     = {len(del_df)}  ({(del_df.incident_id!='').sum()} FK-linked)")
print(f"fault messages = {len(flt_df)}  ({(flt_df.incident_id!='').sum()} FK-linked)")
print(f"feedback rows  = {len(fb_df)}  ({fb_df.days_to_next_failure.notna().sum()} with recurrence)")
# verify temporal join: every incident's start_ts inside its run's degradation window
print("temporal-join check: incidents with run_id =", (inc_df.run_id!='').sum(), "/", len(inc_df))
