# Phase 2 — Problem Discovery (10 Scored Problem Opportunities)

**Compiled:** 2026-05-13
**Workflow:** Phase 1 reports → 3 subagents (product-manager + strategy-consultant + hackathon) → merged problem pool → rigorous composite scoring per anchored rubric.

**Composite weights (defaults per spec §4):** Innovation 0.20 · Judge Appeal 0.25 · Feasibility 0.25 · Technical Depth 0.15 · Business Potential 0.15.

**Synthesis methodology:** Each problem evaluated against Phase 1 evidence (Tata Steel's verified AI stack: Asset Sphere, Safety EyeQ, TDA, Zen AI, Google ADK + BigQuery + Gemini; published KPIs; EU CBAM exposure; EAF transition capex). Scoring is conservative — no score inflation. Each YAML block is calibrated against anchors; composite calculated to 2 decimals.

**Note:** Phase 2 LLM worker hit a 900s timeout during synthesis. The 3 subagents (PM + strategy + hackathon) completed their work and surfaced a 10-problem pool. Final composite scoring + YAML rendering done by Daemon synthesis layer using Phase 1 evidence base.

---

## Final Ranking

| Rank | problem_id | Composite | One-line rationale |
|----:|---|---:|---|
| 1 | `surface-defect-vlm-rca` | **8.25** | NEU-style defect CV + Gemini VLM root-cause layer. Exact stack-fit to Safety EyeQ. |
| 2 | `eaf-electrode-pdm` | **8.20** | EAF-era PdM gap (Asset Sphere is BF-only). Tied to $3.5B green-steel capex. |
| 3 | `hydrogen-dri-copilot` | **8.20** | Greenfield: no peer has built. Maximal innovation + judge wow-factor. Feasibility risk. |
| 4 | `quality-escape-rca` | **8.15** | RCA agent for quality issues. 50% complaint TAT KPI directly addressed. |
| 5 | `cbam-carbon-attribution` | **8.10** | EU CBAM Jan 2026 mandate. 15-22% price impact on EU exports. Data complexity. |
| 6 | `scrap-mix-optimizer` | **7.65** | Tabular ML for EAF scrap mix → quality. Solid Round 1 fit. |
| 7 | `bf-silicon-predictor` | **7.55** | BF hot-metal Si prediction 90-120 min ahead. Tata Steel KPI but commodity ML. |
| 8 | `shift-handover-ai` | **7.35** | LLM+RAG for shift handover + anomaly. Easy Round 2 demo, low judge thrill. |
| 9 | `energy-intensity-optimizer` | **7.30** | Multi-stage GJ/tonne minimisation. Decarbonisation aligned but diffuse. |
| 10 | `operator-knowledge-copilot` | **7.15** | RAG over plant SOPs. TDA-extension, lowest novelty. |

---

## YAML Blocks (Rank 1 → 10)

### 1. `surface-defect-vlm-rca` — Composite 8.25

```yaml
problem_id: surface-defect-vlm-rca
problem_statement: >
  Multi-class steel surface defect classification (NEU-style: scale, patches, crazing,
  pitted surface, inclusions, scratches, slivers) with a Vision-Language-Model layer
  that produces root-cause hypotheses (process / equipment / metallurgical) — not just
  the defect label. Round 2 extends into an agentic loop that routes defects to
  process-optimizer for upstream adjustment.
target_user: Plant quality inspectors at hot/cold strip mills; process engineers receiving the upstream-cause hypothesis.
pain_severity: 9
business_impact: Surface defects drive 2-5% of production to secondary/reject = $3-12M/yr per mill in downgrade losses. Tata Steel runs Safety EyeQ on Gemini + PaliGemma — direct architectural extension.
ai_opportunity: Round 1 — CNN (EfficientNet-B4 or YOLOv8) + class-balanced focal loss. Round 2 — Gemini Vision tool call for VLM root-cause + agent routing.
data_availability: hybrid
competitive_differentiation: vs Tata Steel internal (Safety EyeQ) — adds RCA layer; vs peers (ArcelorMittal, POSCO) — comparable CV maturity but VLM-RCA is novel.
alignment_with_hackathon_theme: 0.95
alignment_with_company_pain_points: 0.92
scores: { innovation: 8, judge_appeal: 9, feasibility: 8, technical_depth: 8, business_potential: 8, composite: 8.25 }
required_roles:
  - { role: "ML engineer (CV)", skill_level: senior, est_hours: 25 }
  - { role: "Agentic systems (Round 2)", skill_level: senior, est_hours: 20 }
top_risks:
  - "Round 1 dataset may not be image-based — fallback: NEU-pretrained model fine-tune on whatever surface is provided."
  - "VLM latency on Gemini API at demo time — mitigation: cache responses, batch."
```

---

### 2. `eaf-electrode-pdm` — Composite 8.20

```yaml
problem_id: eaf-electrode-pdm
problem_statement: >
  Predictive-maintenance model for EAF-era equipment health: graphite electrode
  consumption rate, power-quality fluctuations (THD, flicker), transformer thermal
  stress, water-cooled panel integrity. Asset Sphere covers BF-era PdM; EAF stack
  is a stated gap as Tata Steel transitions to green steel.
target_user: EAF shift superintendents; maintenance planning engineers at Kalinganagar (current) and Port Talbot / IJmuiden (future EAF transitions).
pain_severity: 9
business_impact: EAF unplanned downtime = ₹50K-₹2L per minute (heat-cycle cost). Tied to $3.5B green-steel capex commitment. Asset Sphere achieved 22% downtime reduction on BF era — EAF translation = comparable.
ai_opportunity: Round 1 — Multi-output XGBoost/LightGBM on electrical+thermal sensor stream; survival analysis (Cox or DeepHit) for RUL. Round 2 — agentic dispatcher routes health alerts to maintenance planner + parts ordering + scheduling.
data_availability: hybrid
competitive_differentiation: vs Tata Steel internal (Asset Sphere = BF-only) — direct gap; vs peers — Nucor + SDI have EAF PdM but their stack is closed.
alignment_with_hackathon_theme: 0.95
alignment_with_company_pain_points: 0.95
scores: { innovation: 7, judge_appeal: 9, feasibility: 8, technical_depth: 8, business_potential: 9, composite: 8.20 }
required_roles:
  - { role: "ML engineer (time-series)", skill_level: senior, est_hours: 22 }
  - { role: "Agentic orchestration (Round 2)", skill_level: senior, est_hours: 18 }
top_risks:
  - "If Round 1 dataset is purely tabular, this maps cleanly; if image — re-route to surface-defect."
  - "Sensor data realism for demo — generate synthetic via plant-physics simulator if needed."
```

---

### 3. `hydrogen-dri-copilot` — Composite 8.20

```yaml
problem_id: hydrogen-dri-copilot
problem_statement: >
  AI advisor for hydrogen-direct-reduced-iron (H2-DRI) process operations — IJmuiden
  Phase 1 DRI ramp-up (EUR 2bn Dutch grant), Port Talbot DRI consideration. No peer
  steelmaker has shipped a production H2-DRI AI; greenfield globally.
target_user: IJmuiden DRI plant superintendents; corporate green-steel program lead.
pain_severity: 8
business_impact: Tied to EUR 3.5bn green-steel capex commitment. 40% direct-emissions cut target. EU CBAM compliance directly attached. If solution shapes process even 2% better, ROI is project-defining.
ai_opportunity: Round 1 — Physics-informed NN or surrogate Gaussian Process on hydrogen-reduction thermodynamics. Round 2 — agentic copilot for process engineer with setpoint recommendation + scenario simulation.
data_availability: synthetic
competitive_differentiation: vs Tata Steel internal — greenfield, no internal model exists; vs peers (SSAB, HYBRIT) — some research published but no AI tooling shipped.
alignment_with_hackathon_theme: 0.85
alignment_with_company_pain_points: 0.92
scores: { innovation: 10, judge_appeal: 9, feasibility: 5, technical_depth: 8, business_potential: 10, composite: 8.20 }
required_roles:
  - { role: "ML engineer (physics-informed NN)", skill_level: senior, est_hours: 28 }
  - { role: "Domain ramp (chemistry + metallurgy)", skill_level: mid, est_hours: 12 }
top_risks:
  - "Highest feasibility risk — data scarce, may need to construct physics simulator from papers."
  - "If Round 1 dataset doesn't match, this is harder to redirect than #1 or #2."
```

---

### 4. `quality-escape-rca` — Composite 8.15

```yaml
problem_id: quality-escape-rca
problem_statement: >
  Root-cause analysis agent for quality escapes (defects that pass internal QC and
  reach customer). Combines multi-modal evidence (sensor logs + inspection images +
  customer complaints + maintenance records) into a causal hypothesis ranking.
target_user: Quality assurance team; customer complaint handlers; process engineers for upstream prevention.
pain_severity: 9
business_impact: Tata Steel published 50% reduction in customer complaint TAT — this problem extends to *preventing* the escape in the first place. Complaint volume estimated $20-50M/yr brand impact for premium grades.
ai_opportunity: Round 1 — Multi-class classification of escape-root-cause categories from tabular features. Round 2 — agentic RCA flow with retrieval over plant history + LLM hypothesis generation.
data_availability: hybrid
competitive_differentiation: vs Tata Steel internal (TDA is HR-focused, not technical RCA) — direct gap; vs peers — most steel RCA is manual/expert-driven; AI-RCA is research frontier.
alignment_with_hackathon_theme: 0.88
alignment_with_company_pain_points: 0.95
scores: { innovation: 8, judge_appeal: 9, feasibility: 7, technical_depth: 9, business_potential: 8, composite: 8.15 }
required_roles:
  - { role: "ML engineer (classification + causal)", skill_level: senior, est_hours: 24 }
  - { role: "Agentic RCA flow", skill_level: senior, est_hours: 22 }
top_risks:
  - "Causal inference + multi-modal is harder than pure tabular ML — schedule risk."
  - "Synthetic complaint data realism — judges spot fake data."
```

---

### 5. `cbam-carbon-attribution` — Composite 8.10

```yaml
problem_id: cbam-carbon-attribution
problem_statement: >
  Per-product carbon-footprint attribution agent for EU CBAM (Carbon Border Adjustment
  Mechanism, definitive Jan 2026 mandate). Traces emissions through BOF / BF / EAF /
  rolling stages to product SKU with audit-trail. LLM-driven report generator for
  CBAM declarations.
target_user: Trade compliance lead; CFO office for CBAM cost passthrough planning; sustainability reporting.
pain_severity: 10
business_impact: Indian steel exporters facing 15-22% price impact on EU shipments under CBAM (GTRI/Argus). Tata Steel UK + Netherlands directly exposed. Per-shipment CBAM compliance is operational pain from Jan 2026.
ai_opportunity: Round 1 — Tabular regression of process-stage emissions to product SKU (graph attribution). Round 2 — agentic compliance assistant generating CBAM declarations + variance analysis vs benchmark.
data_availability: synthetic
competitive_differentiation: vs Tata Steel internal — no public AI tooling for CBAM yet; vs peers — ArcelorMittal & Outokumpu working on this; Tata Steel does not have published solution.
alignment_with_hackathon_theme: 0.80
alignment_with_company_pain_points: 0.95
scores: { innovation: 9, judge_appeal: 9, feasibility: 6, technical_depth: 7, business_potential: 10, composite: 8.10 }
required_roles:
  - { role: "ML engineer (graph + regression)", skill_level: senior, est_hours: 22 }
  - { role: "Domain ramp (CBAM regulation)", skill_level: mid, est_hours: 8 }
top_risks:
  - "Data realism — CBAM methodology is published but Tata-Steel-specific factors are not."
  - "Judges may prefer operational problems over regulatory — judge_appeal is high but niche."
```

---

### 6. `scrap-mix-optimizer` — Composite 7.65

```yaml
problem_id: scrap-mix-optimizer
problem_statement: ML model that recommends optimal scrap-mix charge to EAF given output-grade target and economic constraints. Scrap mix is 60-70% of EAF cost; mix-quality variance is primary driver of off-grade heats.
target_user: EAF charge planners; procurement (for forward scrap booking).
pain_severity: 8
business_impact: Scrap input cost = 60-70% of total EAF cost. 0.5% efficiency gain on Kalinganagar's EAF capacity = ₹15-30 cr/yr. Tata Steel EAF transition makes this central.
ai_opportunity: Round 1 — Multi-output regression (yield + carbon + residuals) with constraint handling. Round 2 — agentic dispatcher between procurement, planning, and melt-shop with cost-aware recommendation.
data_availability: synthetic
competitive_differentiation: vs Tata Steel internal — not publicly disclosed; vs Nucor — internal model but closed.
alignment_with_hackathon_theme: 0.85
alignment_with_company_pain_points: 0.80
scores: { innovation: 7, judge_appeal: 8, feasibility: 8, technical_depth: 7, business_potential: 8, composite: 7.65 }
required_roles:
  - { role: "ML engineer (regression + constraint)", skill_level: senior, est_hours: 22 }
  - { role: "Agentic dispatcher", skill_level: mid, est_hours: 14 }
top_risks:
  - "Lower novelty than top-5."
  - "Synthetic data must respect real thermodynamics or judges will spot it."
```

---

### 7. `bf-silicon-predictor` — Composite 7.55

```yaml
problem_id: bf-silicon-predictor
problem_statement: Blast-furnace hot-metal silicon-content prediction 90-120 min ahead from upstream process telemetry. Tata Steel has an internal model; problem here is to match or exceed it on the public-data benchmark with uncertainty quantification.
target_user: BF shift superintendents; process engineers managing slag chemistry.
pain_severity: 7
business_impact: Off-spec hot metal = re-blowing / desulfurisation / rejection. Single percentage point miss = ₹50-100 lakh per shift. 7-10% throughput uplift achieved at Kalinganagar.
ai_opportunity: Round 1 — Time-series transformer or temporal-CNN with conformal prediction for uncertainty bounds. Round 2 — agentic loop with BF process-engineer recommending adjustments.
data_availability: hybrid
competitive_differentiation: vs Tata Steel internal — matching/exceeding internal model is hard; vs peers — well-studied, commodity.
alignment_with_hackathon_theme: 0.85
alignment_with_company_pain_points: 0.75
scores: { innovation: 6, judge_appeal: 8, feasibility: 9, technical_depth: 7, business_potential: 7, composite: 7.55 }
required_roles:
  - { role: "ML engineer (time-series)", skill_level: senior, est_hours: 18 }
top_risks:
  - "Lowest innovation in top-10 — 'we already have this' counter."
  - "Highest feasibility — Round 1 safe pick if dataset is BF-related time series."
```

---

### 8. `shift-handover-ai` — Composite 7.35

```yaml
problem_id: shift-handover-ai
problem_statement: Shift-handover intelligence agent — aggregates last-shift events (sensor anomalies + operator notes + maintenance flags) into a structured handover briefing with anomaly highlights and recommended first-hour actions.
target_user: Outgoing + incoming shift superintendents across BF, EAF, hot strip mill, cold mill.
pain_severity: 7
business_impact: 30-40% of shift-related incidents trace to handover gaps. Hard $ attribution but operational efficiency play.
ai_opportunity: Round 1 fit weak (event classification). Round 2 — agentic summariser with retrieval over plant history.
data_availability: synthetic
competitive_differentiation: vs Tata Steel internal — not publicly disclosed; vs peers — handover automation done in adjacent industries but not steel-specific.
alignment_with_hackathon_theme: 0.65
alignment_with_company_pain_points: 0.75
scores: { innovation: 7, judge_appeal: 7, feasibility: 9, technical_depth: 6, business_potential: 7, composite: 7.35 }
required_roles:
  - { role: "ML engineer (NLP + sequence)", skill_level: mid, est_hours: 16 }
  - { role: "Agentic summariser", skill_level: mid, est_hours: 14 }
top_risks:
  - "Round 1 fit weak — best as Round 2-only pick."
  - "Low technical depth."
```

---

### 9. `energy-intensity-optimizer` — Composite 7.30

```yaml
problem_id: energy-intensity-optimizer
problem_statement: Cross-stage energy-per-tonne (GJ/t) optimisation recommender. Identifies setpoint adjustments across BF → BOF → continuous casting → hot strip mill that minimise total energy without violating product-spec constraints.
target_user: Plant energy manager; corporate sustainability office.
pain_severity: 7
business_impact: Energy = 25-35% of integrated-steel cost. 1% improvement on Tata Steel India capacity = ₹250+ cr/yr. Decarbonisation target alignment.
ai_opportunity: Round 1 — Multi-objective regression with constraint handling. Round 2 — agentic setpoint advisor with simulator-in-the-loop.
data_availability: synthetic
competitive_differentiation: vs Tata Steel internal — existing energy analytics, not AI-driven optimisation; vs peers — most have done discrete-stage optimisation; cross-stage is harder.
alignment_with_hackathon_theme: 0.75
alignment_with_company_pain_points: 0.80
scores: { innovation: 7, judge_appeal: 7, feasibility: 7, technical_depth: 8, business_potential: 8, composite: 7.30 }
required_roles:
  - { role: "ML engineer (multi-obj optimisation)", skill_level: senior, est_hours: 22 }
top_risks:
  - "Diffuse business case."
  - "Cross-stage optimisation hard to demo in 90 seconds."
```

---

### 10. `operator-knowledge-copilot` — Composite 7.15

```yaml
problem_id: operator-knowledge-copilot
problem_statement: RAG-driven plant-operator copilot — answers technical questions over SOPs, manuals, past incident reports, vendor docs. Direct extension of TDA pattern but for plant-floor technical queries vs HR/admin focus.
target_user: Plant operators (junior + senior); maintenance technicians; new hires on shift.
pain_severity: 7
business_impact: Knowledge-retrieval friction in steel plants is substantial but hard-to-quantify. TDA achieved 70% autonomous resolution on HR — operator-side is comparable.
ai_opportunity: Round 1 poor fit (not tabular ML). Round 2 — RAG agent over Tata Steel public corpus with citation discipline and confidence scoring.
data_availability: real
competitive_differentiation: vs Tata Steel internal (TDA) — TDA is HR-focused, operator-side is open; vs peers — well-trodden RAG pattern.
alignment_with_hackathon_theme: 0.70
alignment_with_company_pain_points: 0.78
scores: { innovation: 6, judge_appeal: 7, feasibility: 9, technical_depth: 6, business_potential: 7, composite: 7.15 }
required_roles:
  - { role: "ML engineer (RAG)", skill_level: mid, est_hours: 14 }
  - { role: "Agentic flow", skill_level: mid, est_hours: 12 }
top_risks:
  - "Lowest composite — 'we already have TDA' counter."
  - "Round 1 fit nil — Round 2 + 3 only play."
```

---

## Strategic observations for Checkpoint 2

### What the ranking reveals

1. **Top 3 cluster tightly** (8.25 / 8.20 / 8.20) — different shapes of bet:
   - `surface-defect-vlm-rca` = **lowest risk** (Round 1 + Round 2 both clean) + exact stack fit (Safety EyeQ)
   - `eaf-electrode-pdm` = **strong KPI alignment** ($3.5B green-steel capex) + transferable data
   - `hydrogen-dri-copilot` = **highest innovation ceiling** (10/10) but feasibility risk (5/10) — boom-or-bust
2. **Top 5 all > 8.0** — Boss has 5 strong candidates. Pick 2-3 for Phase 3 deep solution research.
3. **Bottom 3 (7.15-7.35)** mostly Round 2-only — weak Round 1 fit. Skip unless Boss has specific reason.

### Risk profile spread

| Pick style | Recommended choices |
|---|---|
| **Safe + high-ceiling** (recommended) | #1 `surface-defect-vlm-rca` + #2 `eaf-electrode-pdm` + #4 `quality-escape-rca` |
| **Innovation-max** | #3 `hydrogen-dri-copilot` + #1 + #5 `cbam-carbon-attribution` |
| **Round-1-leaderboard-optimal** | #2 `eaf-electrode-pdm` + #6 `scrap-mix-optimizer` + #7 `bf-silicon-predictor` |
| **Round-2-agentic-max** | #4 `quality-escape-rca` + #3 `hydrogen-dri-copilot` + #1 `surface-defect-vlm-rca` |

### Round 1 dataset unlock dependency

Sab problems Round 1 dataset ke unknown holes pe contingent hain. **2026-05-22 18:00 IST** ko dataset unlock hoga (same for all participants). Strategic move: pick problems with **transferable solution patterns** so prototype work survives regardless of Round 1's actual problem domain.
