"""
Structural artifacts v2 — fills the remaining missing features:
  G1  additional/process_flow_graph.json   inter-asset dependency DAG for
       plant-level BOTTLENECK prioritization (PS 5.2)                       [OE-6]
  G3  operational_failure/process_defect_events.csv  product/process-defect
       ground truth, causally linked to equipment condition (PS 5.1)        [OE-2/DR-04]
  G4  condition_monitoring/event_stream.csv  one event-ordered real-time feed
       (alerts + faults + delays + incidents merged, time-sorted)           [OE-7]
  B5  condition_monitoring/SPLITS.md  train/val/test protocol doc            [CM-04]
Synthetic; consistent with the v2 sensor + operational layers.
"""
import json, datetime as dt
from pathlib import Path
import numpy as np, pandas as pd

BASE = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_2/dataforge/datasets/steel-maintenance-flagship")
SPINE = json.loads((BASE/"SPEC"/"ground_truth_spine.json").read_text())
rng = np.random.default_rng(99)
assets = SPINE["asset_registry"]
by_id = {a["asset_id"]: a for a in assets}

# ── G1 process-flow dependency graph ────────────────────────────────────────
# Integrated-steel material flow (upstream -> downstream). Buffer_hours = how long
# a downstream unit can run on stock/WIP before an upstream stoppage bites it.
STAGE_ORDER = ["raw_material_handling","iron_making","sintering","steelmaking",
               "ladle_handling","casting","reheating","hot_rolling","cold_rolling","utilities"]
STAGE_EDGES = [  # (from, to, buffer_hours, coupling)
    ("raw_material_handling","sintering",8,"strong"),
    ("raw_material_handling","iron_making",12,"strong"),
    ("sintering","iron_making",10,"strong"),
    ("iron_making","steelmaking",6,"strong"),
    ("steelmaking","ladle_handling",2,"strong"),
    ("ladle_handling","casting",1.5,"strong"),
    ("casting","reheating",24,"medium"),   # slab yard buffer
    ("reheating","hot_rolling",2,"strong"),
    ("hot_rolling","cold_rolling",72,"weak"),  # HR coil stock
    ("utilities","steelmaking",0.5,"strong"),
    ("utilities","casting",0.5,"strong"),
    ("utilities","hot_rolling",0.5,"strong"),
]
STAGE_TPH = {"raw_material_handling":1800,"iron_making":320,"sintering":550,"steelmaking":300,
             "ladle_handling":280,"casting":250,"reheating":300,"hot_rolling":350,"cold_rolling":180,"utilities":200}
nodes = []
for a in assets:
    st = a.get("process_stage","hot_rolling")
    nodes.append({"asset_id": a["asset_id"], "equipment_class": a["equipment_class"],
        "process_stage": st, "criticality": a.get("criticality",2),
        "stage_throughput_tph": STAGE_TPH.get(st,300),
        "area": a.get("location",{}).get("area","")})
# downstream reachability per stage (for bottleneck propagation)
adj = {}
for f,t,b,c in STAGE_EDGES: adj.setdefault(f,[]).append(t)
def reach(stage):
    seen=set(); stack=list(adj.get(stage,[]))
    while stack:
        n=stack.pop()
        if n in seen: continue
        seen.add(n); stack+=adj.get(n,[])
    return sorted(seen)
graph = {
    "description": "Inter-asset / inter-stage material-flow dependency DAG for plant-level bottleneck prioritization. A failure propagates downstream once the buffer is exhausted. Use with incident downtime + spares lead-time to rank concurrent failures.",
    "stage_order": STAGE_ORDER,
    "nodes": nodes,
    "stage_edges": [{"from":f,"to":t,"buffer_hours":b,"coupling":c} for f,t,b,c in STAGE_EDGES],
    "stage_downstream_reach": {s: reach(s) for s in STAGE_ORDER},
    "bottleneck_rule": "priority_score = process_criticality(1=highest) -> weight 0.35; delay_severity(downtime_hours vs buffer) 0.30; spares_availability(in_stock?) 0.20; procurement_lead_time_weeks 0.15. Lower buffer + more downstream_reach => higher propagation cost.",
}
(BASE/"additional"/"process_flow_graph.json").write_text(json.dumps(graph,indent=2))
print(f"G1 process_flow_graph.json: {len(nodes)} nodes, {len(STAGE_EDGES)} edges")

# ── G3 process/product-defect ground truth ──────────────────────────────────
ep = pd.read_csv(BASE/"condition_monitoring"/"episodes_manifest.csv", parse_dates=["onset_ts","failure_ts"])
inc = pd.read_csv(BASE/"operational_failure"/"incident_records.csv", parse_dates=["start_ts","detected_ts"])
DEFECTS = {
    "hot_rolling": ["surface_scratch","edge_crack","thickness_deviation","camber","scale_pitting","roll_mark"],
    "cold_rolling": ["surface_scratch","thickness_deviation","coil_break","chatter_mark"],
    "casting": ["surface_crack","longitudinal_crack","bleeder","oscillation_mark","breakout_near_miss"],
    "reheating": ["over_scaling","temperature_streak","decarburization"],
    "steelmaking": ["inclusion","chemistry_deviation"],
}
rows = []
cid = 0
# (a) causal defects during incident degradation windows on rolling/casting assets
for _,r in inc.iterrows():
    st = by_id.get(r.asset_id,{}).get("process_stage","")
    pool = DEFECTS.get(st)
    if not pool: continue
    onset = ep[ep.run_id==r.run_id]["onset_ts"]
    if len(onset)==0: continue
    onset = onset.iloc[0]
    nd = int(rng.integers(2,7))   # defects cluster as condition worsens
    for _ in range(nd):
        cid += 1
        frac = rng.uniform(0.5,1.0)   # more defects near failure
        t = onset + (r.start_ts - onset)*frac
        rows.append({"defect_id":f"DEF-{cid:05d}","timestamp":t.strftime("%Y-%m-%d %H:%M:%S"),
            "coil_id":f"C{rng.integers(100000,999999)}","defect_type":rng.choice(pool),
            "severity":rng.choice(["minor","major","reject"],p=[.5,.35,.15]),
            "process_stage":st,"attributed_asset_id":r.asset_id,"attributed_run_id":r.run_id,
            "linked_incident_id":r.incident_id,"defect_ppm":int(rng.uniform(200,5000)),
            "root_cause_hint":r.failure_mode})
# (b) background defects (normal process variation, no equipment link)
T0,T1 = dt.datetime(2025,1,1), dt.datetime(2025,12,30)
for _ in range(450):
    cid += 1
    st = rng.choice(list(DEFECTS))
    t = T0 + dt.timedelta(hours=float(rng.uniform(0,(T1-T0).total_seconds()/3600)))
    rows.append({"defect_id":f"DEF-{cid:05d}","timestamp":t.strftime("%Y-%m-%d %H:%M:%S"),
        "coil_id":f"C{rng.integers(100000,999999)}","defect_type":rng.choice(DEFECTS[st]),
        "severity":rng.choice(["minor","major","reject"],p=[.7,.25,.05]),
        "process_stage":st,"attributed_asset_id":"","attributed_run_id":"",
        "linked_incident_id":"","defect_ppm":int(rng.uniform(50,1500)),"root_cause_hint":"process_variation"})
ddf = pd.DataFrame(rows).sort_values("timestamp").reset_index(drop=True)
ddf.to_csv(BASE/"operational_failure"/"process_defect_events.csv", index=False)
print(f"G3 process_defect_events.csv: {len(ddf)} ({(ddf.linked_incident_id!='').sum()} equipment-linked)")

# ── G4 event-ordered streaming feed ─────────────────────────────────────────
def load(p,cols):
    d=pd.read_csv(p); return d
streams = []
al = pd.read_csv(BASE/"condition_monitoring"/"anomaly_alerts.csv")
al["event_ts"]=al["timestamp"]; al["event_type"]="anomaly_alert"; al["ref_id"]=al["alert_id"]
al["payload"]=al["sensor"]+" "+al["severity"]+" @"+al["value"].astype(str)
streams.append(al[["event_ts","event_type","asset_id","severity","ref_id","payload"]])
fl = pd.read_csv(BASE/"operational_failure"/"fault_error_messages.csv")
fl["event_ts"]=fl["timestamp"]; fl["event_type"]="fault_message"; fl["ref_id"]=fl.get("incident_id","")
fl["payload"]=fl["fault_code"]+" ("+fl["source_system"]+")"
streams.append(fl[["event_ts","event_type","asset_id","severity","ref_id","payload"]])
dl = pd.read_csv(BASE/"operational_failure"/"equipment_delay_logs.csv")
dl["event_ts"]=dl["timestamp"]; dl["event_type"]="delay"; dl["severity"]="INFO"; dl["ref_id"]=dl.get("incident_id","")
dl["payload"]=dl["delay_reason_code"]+" "+dl["delay_minutes"].astype(str)+"min"
streams.append(dl[["event_ts","event_type","asset_id","severity","ref_id","payload"]])
ic = pd.read_csv(BASE/"operational_failure"/"incident_records.csv")
ic["event_ts"]=ic["start_ts"]; ic["event_type"]="incident"; ic["severity"]=ic["severity"].str.upper(); ic["ref_id"]=ic["incident_id"]
ic["payload"]="BREAKDOWN "+ic["failure_mode"]
streams.append(ic[["event_ts","event_type","asset_id","severity","ref_id","payload"]])
ev = pd.concat(streams, ignore_index=True).sort_values("event_ts").reset_index(drop=True)
ev.insert(0,"seq",range(1,len(ev)+1))
ev.to_csv(BASE/"condition_monitoring"/"event_stream.csv", index=False)
print(f"G4 event_stream.csv: {len(ev)} events, time-ordered, types={ev.event_type.value_counts().to_dict()}")

# ── B5 splits doc ───────────────────────────────────────────────────────────
raw = pd.read_csv(BASE/"condition_monitoring"/"raw_sensor_timeseries.csv")
nruns = pd.read_csv(BASE/"condition_monitoring"/"episodes_manifest.csv").shape[0]
sd = raw.split.value_counts().to_dict()
(BASE/"condition_monitoring"/"SPLITS.md").write_text(f"""# Train / Val / Test Split Protocol

A `split` column is present in `raw_sensor_timeseries.csv`, every `by_equipment/*.csv`
dense table, and `rul_trajectories_long.csv`. **Do not random-split rows** — adjacent
hours of one degradation ramp would leak across folds.

## Protocol (leakage-safe)
- **Failure episodes** are the unit of holdout. Each episode has a unique `run_id`
  (e.g. `HSM.F3.WR.BRG01::E03`). Per asset, episodes are ordered by failure time:
  the **last 2 episodes → test**, the **prior 1 → val**, the **rest → train**.
- **Healthy steady-state rows** (no `run_id`) are split **temporally**: first 70% of
  the year → train, 70–85% → val, ≥85% → test.
- For RUL regression use **leave-one-run-out CV** over `run_id` ({nruns} independent runs).
- For failure classification use the `split` column or **group-K-fold on `asset_id`**.

## Row counts
| split | rows |
|---|---|
| train | {sd.get('train',0):,} |
| val | {sd.get('val',0):,} |
| test | {sd.get('test',0):,} |

## Why
The v1 dataset shipped no split and a clock-derived label, so a naive split reported
inflated metrics (audit CM-04). Episode-holdout + temporal healthy split + `run_id`
LORO-CV make reported RUL/failure metrics honest.
""")
print(f"B5 SPLITS.md written ({sd})")
print("\nstructural artifacts v2 complete.")
