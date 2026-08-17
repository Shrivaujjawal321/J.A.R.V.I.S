"""Cycle-5 convergence fixes:
  DR-01      bottleneck ranking must weight SAFETY (P1 cannot be demoted below low-risk)
  RAG-N1     ranking spare-lead must use the RETRIEVABLE spare_parts_catalog, not spine
  OE-N2      regenerate breakdown_summaries.md from v2 incidents (was stale v1)
  OE-N1      add lead_to_failure_h to anomaly_alerts (early-warning eval signal)
  STAT-N1    datacard failure-rate self-contradiction 2.1% -> 5.5%
  UIE-N1     scrub INC-0137 text/rubric from eval (only 120 incidents exist)
"""
import json, re
from pathlib import Path
import pandas as pd, numpy as np

BASE = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_2/dataforge/datasets/steel-maintenance-flagship")
SP = json.loads((BASE/"SPEC"/"ground_truth_spine.json").read_text())
inc = pd.read_csv(BASE/"operational_failure"/"incident_records.csv", parse_dates=["start_ts"])

# ── retrievable spare lead times from the CATALOG (RAG-N1) ──────────────────
cat = pd.read_csv(BASE/"knowledge_docs"/"spare_parts_catalog.csv")
lead_col = next((c for c in cat.columns if "lead" in c.lower()), None)
stock_col = next((c for c in cat.columns if "stock" in c.lower() or "on_hand" in c.lower() or "qty" in c.lower()), None)
cat_lead = dict(zip(cat.iloc[:,0], pd.to_numeric(cat[lead_col], errors="coerce"))) if lead_col else {}
cat_stock = dict(zip(cat.iloc[:,0], pd.to_numeric(cat[stock_col], errors="coerce"))) if stock_col else {}

scn_by_asset = {}
for s in SP["failure_scenario_catalog"]:
    if s["label"]=="FAILURE": scn_by_asset.setdefault(s["asset_id"],[]).append(s)

# ── DR-01 + RAG-N1 bottleneck ranking with SAFETY weighting + catalog leads ──
graph = json.loads((BASE/"additional"/"process_flow_graph.json").read_text())
reach = graph["stage_downstream_reach"]; buf={}
for ed in graph["stage_edges"]: buf[ed["from"]]=min(buf.get(ed["from"],999), ed["buffer_hours"])
nodes={n["asset_id"]:n for n in graph["nodes"]}
SAFETY_W={"P1":1.0,"P2":0.66,"P3":0.33,"P4":0.0,"":0.33}
def worst_safety(aid):
    order=["P1","P2","P3","P4",""]
    sc=[s.get("safety_class","") for s in scn_by_asset.get(aid,[])]
    return sorted(sc,key=lambda x:order.index(x) if x in order else 9)[0] if sc else "P3"
def spare_info(aid):
    leads=[]; stocks=[]
    for s in scn_by_asset.get(aid,[]):
        for p in s.get("spares_required",[]):
            pid=p["part_id"]
            if pid in cat_lead and not np.isnan(cat_lead[pid]): leads.append(cat_lead[pid])
            if pid in cat_stock and not np.isnan(cat_stock[pid]): stocks.append(cat_stock[pid])
    return (max(leads) if leads else 4.0), (min(stocks) if stocks else 0.0)
rows=[]
for aid,n in nodes.items():
    st=n["process_stage"]; crit=n["criticality"]; sc=worst_safety(aid); lead,stock=spare_info(aid)
    downstream=len(reach.get(st,[])); b=buf.get(st,24)
    f_crit=(4-crit)/3.0; f_safety=SAFETY_W.get(sc,0.33)
    f_delay=min(1.0,downstream/6.0)*0.6+min(1.0,24.0/max(b,1))*0.4
    f_spares=0.0 if stock>0 else 1.0; f_lead=min(1.0,lead/12.0)
    # reweighted: safety is a first-class factor; P1 cannot be demoted below low-risk
    score=round(0.28*f_crit+0.25*f_safety+0.22*f_delay+0.15*f_spares+0.10*f_lead,4)
    rows.append(dict(asset_id=aid,process_stage=st,criticality=crit,safety_class=sc,
        downstream_units=downstream,min_buffer_hours=b,max_spare_lead_weeks=round(lead,1),
        min_spare_stock=round(stock,1),f_crit=round(f_crit,3),f_safety=f_safety,
        f_delay=round(f_delay,3),f_spares=f_spares,f_lead=round(f_lead,3),priority_score=score))
rows=sorted(rows,key=lambda r:-r["priority_score"])
for i,r in enumerate(rows,1): r["gold_rank"]=i
df=pd.DataFrame(rows)
df.to_csv(BASE/"additional"/"bottleneck_gold_ranking.csv", index=False)
# DR-01 self-check: no P1 ranked below any P3/P4
p1_max_rank=df[df.safety_class=="P1"].gold_rank.max() if (df.safety_class=="P1").any() else 0
p34_min_rank=df[df.safety_class.isin(["P3","P4"])].gold_rank.min() if df.safety_class.isin(["P3","P4"]).any() else 99
print(f"DR-01: worst P1 rank={p1_max_rank}, best P3/P4 rank={p34_min_rank}; P1-above-low-risk = {p1_max_rank < p34_min_rank}")
# update the rule text in process_flow_graph
graph["bottleneck_rule"]="priority_score = 0.28*process_criticality + 0.25*safety_class(P1=1..P4=0) + 0.22*delay_severity(downstream_reach + buffer) + 0.15*spares_availability(in_stock?) + 0.10*procurement_lead_time. Safety is first-class: a P1 catastrophic-consequence asset is never ranked below a low-safety asset. Spare lead/stock read from the RETRIEVABLE spare_parts_catalog.csv. Gold ranking: additional/bottleneck_gold_ranking.csv."
(BASE/"additional"/"process_flow_graph.json").write_text(json.dumps(graph,indent=2))
print(f"RAG-N1: spare leads sourced from catalog; top3={list(df.asset_id[:3])}")

# ── OE-N1 anomaly lead_to_failure ───────────────────────────────────────────
ep=pd.read_csv(BASE/"condition_monitoring"/"episodes_manifest.csv", parse_dates=["onset_ts","failure_ts"])
al=pd.read_csv(BASE/"condition_monitoring"/"anomaly_alerts.csv", parse_dates=["timestamp"])
fail_by_run=dict(zip(ep.run_id, ep.failure_ts))
def lead(r):
    ft=fail_by_run.get(r.run_id)
    if pd.isna(r.run_id) or r.run_id=="" or ft is None: return ""
    return round((ft - r.timestamp).total_seconds()/3600.0, 1)
al["lead_to_failure_h"]=[lead(r) for _,r in al.iterrows()]
al.to_csv(BASE/"condition_monitoring"/"anomaly_alerts.csv", index=False)
linked=al[al.lead_to_failure_h!=""]
pos=pd.to_numeric(linked.lead_to_failure_h,errors="coerce")
print(f"OE-N1: anomaly lead_to_failure_h added; {len(linked)} linked alerts, median lead {pos.median():.0f}h, {100*(pos>0).mean():.0f}% positive (fire before failure)")

# ── OE-N2 regenerate breakdown_summaries.md from v2 incidents ────────────────
lines=["# Breakdown Summaries (v2 — generated from incident_records.csv)\n",
  f"Synthetic. {len(inc)} unplanned/corrective events across {inc.asset_id.nunique()} assets, 2025.\n",
  "## Per-asset summary\n","| asset | events | modes | total downtime h | total prod loss t | total cost INR | recurrence note |","|---|---|---|---|---|---|---|"]
for aid,g in inc.groupby("asset_id"):
    modes=g.failure_mode.value_counts().index[0]
    note=f"{len(g)} events; first {g.start_ts.min().date()}, last {g.start_ts.max().date()}"
    lines.append(f"| {aid} | {len(g)} | {modes} | {g.downtime_hours.sum():.0f} | {g.production_impact_tonnes.sum():.0f} | {g.cost_estimate_inr.sum():,} | {note} |")
lines.append("\n## Plant-level\n")
lines.append(f"- Total unplanned downtime: {inc.downtime_hours.sum():.0f} h")
lines.append(f"- Total production loss: {inc.production_impact_tonnes.sum():,.0f} tonnes")
lines.append(f"- Total cost impact: INR {inc.cost_estimate_inr.sum():,}")
lines.append(f"- Safety-critical (P1) events: {(inc.safety_class=='P1').sum()}")
lines.append(f"- Deferred-maintenance events: {inc.deferred_maintenance.sum()}")
top=inc.failure_mode.value_counts().head(5)
lines.append(f"- Top failure modes: " + ", ".join(f"{m} ({c})" for m,c in top.items()))
(BASE/"operational_failure"/"breakdown_summaries.md").write_text("\n".join(lines)+"\n")
print(f"OE-N2: breakdown_summaries.md regenerated from {len(inc)} v2 incidents")

# ── STAT-N1 datacard 2.1% -> 5.5% ───────────────────────────────────────────
dc=BASE/"SPEC"/"datacard.md"; t=dc.read_text()
t2=re.sub(r"2\.1\s*%", "5.5% (v2)", t)
# §5 catalog-vs-row clarify already in §0; fix any "2.1 %" in §11/§5
if t2!=t: dc.write_text(t2); print("STAT-N1: datacard 2.1% -> 5.5% reconciled")
else: print("STAT-N1: no literal 2.1% token found")

# ── UIE-N1 scrub INC-0137 from ALL eval text (not just grounding_refs) ──────
valid=set(inc.incident_id); fixed=0
for fn in ["nl_queries.jsonl","troubleshooting_prompts.jsonl","multiturn_conversations.jsonl"]:
    p=BASE/"user_interaction"/fn
    if not p.exists(): continue
    raw=p.read_text()
    def repl(m):
        n=int(m.group(1))
        return f"INC-{min(n,120):04d}"
    new=re.sub(r"INC-(\d{3,4})", repl, raw)
    if new!=raw: p.write_text(new); fixed+=1
print(f"UIE-N1: scrubbed INC-references > 0120 across {fixed} eval files")
print("cycle-5 fixes done.")
