"""
Cycle-2 targeted fixes:
  DR-NEW-02  regenerate additional/equipment_master.csv cleanly (always 38 fields)  [HIGH]
  KR-LUBE-CONFLICT  reconcile oil-film bearing grade to ISO VG 220 (MAN-001 authoritative)
                    in spare_parts_catalog.csv + LUBE-01 diagram                      [HIGH]
  OE-PR1     additional/bottleneck_gold_ranking.csv — gold prioritization ranking
             using the documented priority formula + process_flow_graph + spares      [HIGH]
"""
import json, csv, re, datetime as dt
from pathlib import Path
import numpy as np, pandas as pd

BASE = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_2/dataforge/datasets/steel-maintenance-flagship")
SP = json.loads((BASE/"SPEC"/"ground_truth_spine.json").read_text())
rng = np.random.default_rng(31415)
assets = SP["asset_registry"]
scn_by_asset = {}
for s in SP["failure_scenario_catalog"]:
    if s["label"]=="FAILURE": scn_by_asset.setdefault(s["asset_id"],[]).append(s)
spares = {p["part_id"]: p for p in SP["spare_parts_master"]}

# ── DR-NEW-02 equipment_master.csv (clean, 38 fields every row) ──────────────
HDR = ['asset_id','equipment_class','description','site','area','unit','equipment_tag',
 'manufacturer','model','criticality','criticality_basis','process_stage','installation_date',
 'last_overhaul_date','next_planned_overhaul','rated_power_kW','rated_speed_rpm','rated_load_t',
 'design_pressure_bar','insulation_class','bearing_model_DE','bearing_model_NDE','parent_asset_id',
 'functional_location','maintenance_strategy','pm_interval_days','pm_craft','cbm_enabled',
 'cbm_sensors_count','safety_class_worst','iso_standard_primary','oem_contact_ref','spare_parts_kit',
 'asset_replacement_cost_usd','current_health_status','health_status_date','active_wo_count','notes']
CRIT_BASIS = {1:"process-critical single-point",2:"important, partial redundancy",3:"redundant/non-critical"}
def worst_safety(aid):
    order=["P1","P2","P3","P4",""]
    sc=[s.get("safety_class","") for s in scn_by_asset.get(aid,[])]
    return sorted(sc, key=lambda x: order.index(x) if x in order else 9)[0] if sc else "P3"
rows=[]
for a in assets:
    loc=a.get("location",{}); aid=a["asset_id"]
    sensors=a.get("sensors",[]); ncbm=len(sensors)
    crit=a.get("criticality",2)
    std=next((s.get("standard","") for s in sensors if s.get("standard")),"")
    iso=re.search(r"(ISO|IEC|NEMA|ISA|IEEE|API)\s?[\d\-:]+", std)
    scns=scn_by_asset.get(aid,[])
    kit="|".join(sorted({p["part_id"] for s in scns for p in s.get("spares_required",[])})) or ""
    repl=int(np.median([s.get("cost_impact",{}).get("usd",100000) for s in scns]) * rng.uniform(8,20)) if scns else int(rng.uniform(2e5,3e6))
    ins = a.get("installation_date","2020-01-01")
    ovh = a.get("last_overhaul_date","2024-06-01")
    nxt = (dt.date.fromisoformat(ovh) + dt.timedelta(days=int(rng.integers(420,760)))).isoformat()
    is_motor = "motor" in a["equipment_class"]
    rows.append({
        'asset_id':aid,'equipment_class':a["equipment_class"],'description':a.get("description",""),
        'site':loc.get("site","TATA_JSR"),'area':loc.get("area",""),'unit':loc.get("unit",""),
        'equipment_tag':loc.get("equipment",""),'manufacturer':a.get("manufacturer",""),'model':a.get("model",""),
        'criticality':crit,'criticality_basis':CRIT_BASIS.get(crit,""),'process_stage':a.get("process_stage",""),
        'installation_date':ins,'last_overhaul_date':ovh,'next_planned_overhaul':nxt,
        'rated_power_kW':a.get("rated_power_kW", int(rng.choice([200,400,630,800,1250,2000,3150]))),
        'rated_speed_rpm':a.get("rated_speed_rpm",""),
        'rated_load_t':a.get("rated_load_t","") if "crane" in a["equipment_class"] else "",
        'design_pressure_bar':a.get("design_pressure_bar","") if ("hyd" in a["equipment_class"] or "pump" in a["equipment_class"]) else "",
        'insulation_class':"F" if is_motor else "",
        'bearing_model_DE':"SKF "+str(rng.integers(22000,23999)) if ("bearing" in a["equipment_class"] or is_motor) else "",
        'bearing_model_NDE':"SKF "+str(rng.integers(6200,6399)) if is_motor else "",
        'parent_asset_id':loc.get("unit",""),
        'functional_location':f"{loc.get('site','TATA_JSR')}-{loc.get('area','')}-{loc.get('unit','')}",
        'maintenance_strategy':"CBM+Time-Based" if ncbm>=3 else "Time-Based",
        'pm_interval_days':int(rng.choice([30,45,60,90,180])),'pm_craft':"Mechanical" if not is_motor else "Electrical",
        'cbm_enabled':"TRUE" if ncbm>=3 else "FALSE",'cbm_sensors_count':ncbm,
        'safety_class_worst':worst_safety(aid),
        'iso_standard_primary':iso.group(0) if iso else "ISO 14224",
        'oem_contact_ref':f"OEM-{a.get('manufacturer','GEN').split()[0][:4].upper()}-{rng.integers(100,999)}",
        'spare_parts_kit':kit,'asset_replacement_cost_usd':repl,
        'current_health_status':str(rng.choice(["healthy","watch","degraded"],p=[.7,.22,.08])),
        'health_status_date':"2025-12-30",'active_wo_count':int(rng.integers(0,5)),
        'notes':"representative synthetic asset master record",
    })
with open(BASE/"additional"/"equipment_master.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=HDR); w.writeheader(); w.writerows(rows)
# validate 38 fields every row
chk=list(csv.reader(open(BASE/"additional"/"equipment_master.csv")))
from collections import Counter
print("equipment_master.csv field counts:", Counter(len(r) for r in chk), "(should be all 38)")

# ── KR-LUBE-CONFLICT reconcile oil-film bearing grade -> ISO VG 220 ─────────
spc = BASE/"knowledge_docs"/"spare_parts_catalog.csv"
t = spc.read_text()
t2 = t.replace("Oil-film bearing circulating oil ISO VG 68", "Oil-film bearing circulating oil ISO VG 220")
spc.write_text(t2)
print("spare_parts_catalog BRG-OFB-OIL: VG 68 ->", "VG 220" if t2!=t else "unchanged(?)")
lube = BASE/"knowledge_docs"/"diagrams"/"LUBE-01_master_lubrication_chart.md"
if lube.exists():
    lt = lube.read_text()
    lt2 = re.sub(r"ISO\s*VG\s*100[\-–/ ]*150", "ISO VG 220", lt)
    lt2 = lt2.replace("VG 100-150","VG 220").replace("VG 100–150","VG 220")
    # add a reconciliation note at the OFB row context
    if lt2!=lt: lube.write_text(lt2)
    print("LUBE-01 oil-film grade ->", "VG 220 (reconciled to MAN-001)" if lt2!=lt else "no VG100-150 token found")
else:
    print("LUBE-01 not found")

# ── OE-PR1 gold bottleneck ranking ──────────────────────────────────────────
graph = json.loads((BASE/"additional"/"process_flow_graph.json").read_text())
reach = graph["stage_downstream_reach"]
buf = {}
for ed in graph["stage_edges"]: buf[ed["from"]] = min(buf.get(ed["from"],999), ed["buffer_hours"])
inc = pd.read_csv(BASE/"operational_failure"/"incident_records.csv")
# rank each FAILURE scenario/asset by the documented priority formula
node_stage = {n["asset_id"]: n["process_stage"] for n in graph["nodes"]}
node_crit = {n["asset_id"]: n["criticality"] for n in graph["nodes"]}
def spare_lead(aid):
    sc=scn_by_asset.get(aid,[])
    leads=[spares[p["part_id"]]["lead_time_weeks"] for s in sc for p in s.get("spares_required",[]) if p["part_id"] in spares and "lead_time_weeks" in spares[p["part_id"]]]
    stock=[spares[p["part_id"]].get("stock_qty",0) for s in sc for p in s.get("spares_required",[]) if p["part_id"] in spares]
    return (max(leads) if leads else 4), (min(stock) if stock else 0)
gold=[]
for a in assets:
    aid=a["asset_id"]; st=node_stage.get(aid,"")
    crit=node_crit.get(aid,2)
    lead,stock=spare_lead(aid)
    downstream=len(reach.get(st,[])); b=buf.get(st,24)
    # normalized components (lower buffer & higher downstream => worse)
    f_crit=(4-crit)/3.0           # crit1 ->1.0
    f_delay=min(1.0, downstream/6.0)*0.6 + min(1.0, 24.0/max(b,1))*0.4
    f_spares=0.0 if stock>0 else 1.0
    f_lead=min(1.0, lead/12.0)
    score=round(0.35*f_crit + 0.30*f_delay + 0.20*f_spares + 0.15*f_lead, 4)
    gold.append({"asset_id":aid,"process_stage":st,"criticality":crit,
        "downstream_units":downstream,"min_buffer_hours":b,"max_spare_lead_weeks":lead,
        "min_spare_stock":stock,"priority_score":score})
gold=sorted(gold, key=lambda r:-r["priority_score"])
for i,g in enumerate(gold,1): g["gold_rank"]=i
pd.DataFrame(gold)[["gold_rank","asset_id","process_stage","criticality","downstream_units",
    "min_buffer_hours","max_spare_lead_weeks","min_spare_stock","priority_score"]].to_csv(
    BASE/"additional"/"bottleneck_gold_ranking.csv", index=False)
print(f"bottleneck_gold_ranking.csv: {len(gold)} assets ranked; top3 = {[g['asset_id'] for g in gold[:3]]}")
print("cycle-2 targeted fixes done.")
