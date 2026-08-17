# India Agentic AI Opportunity Map — Steel & Metals

_Deep-dive research brief · Last updated: 2026-06-23 · Draft for review · Not investment advice_

---

## 0. Why this industry, why now (first-principles setup)

India is the **world's #2 steel producer**. Crude steel production hit **~153.6 MT in FY26 (Apr–Feb)** and the market is projected to reach **~161.7 MT in 2026** heading toward **~250 MT by 2031** at roughly **9% CAGR**; capacity is targeted at **300 MTPA by 2030** (Source: Mordor Intelligence, India Steel Market, 2026, https://www.mordorintelligence.com/industry-reports/india-steel-market ; IBEF Steel, 2026, https://www.ibef.org/industry/steel). Capacity already surged past **205 MT** (Source: Tube & Pipe India, 2025, https://tubepipeindia.com/indias-steel-capacity-surges/).

Named giants: **JSW Steel (~30.1 MT FY26, targeting 50 MTPA by 2030)**, **Tata Steel (India ~23.5 MT FY26, ~35 MT global)**, **SAIL (~20.6 MT)**, **Jindal Steel & Power (~9.25 MT, capacity 15.6 MTPA)**, plus ArcelorMittal Nippon Steel India (AM/NS), Rashtriya Ispat Nigam (RINL), and a long tail of secondary/induction-furnace and re-rolling MSMEs (Source: PSU Connect, 2026, https://www.psuconnect.in/corporate-news/tata-steel-vs-jsw-steel-vs-jindal-steel-india-steel-titans-battle-for-dominance-in-2026 ; JSW Group, https://group.jsw.in/media/steel).

**Why agentic AI now, not just ML dashboards:**
1. **Margins are structurally squeezed.** ~90% coking-coal import dependence + ₹-volatility means input cost is the swing factor and it moves daily (Source: IEEFA, 2025, https://www.downtoearth.org.in/energy/indias-steel-sector-90-energy-import-dependent-with-64-of-new-capacity-coal-based-ieefa ; S&P Global, 2025).
2. **Two regulatory deadlines are converging:** EU **CBAM fully operational Jan 2026** (Indian steel faces the steepest exposure, ~32% cost increase by 2032), and India's domestic **CCTS** with steel emission-intensity targets and first CCC trading expected **mid-2026** (Source: CO2 AI, 2026, https://co2ai.com/insights/cbam-and-indian-steel-the-market-is-already-deciding-winners-and-losers ; ICAP, 2025, https://icapcarbonaction.com/en/news/compliance-obligations-under-indias-carbon-credit-trading-scheme-enter-force-seven-sectors).
3. **The data layer already exists** in most large mills (Level-2 automation, MES, SAP, FOIS feeds, historians) but is siloed — agentic systems are the missing orchestration layer that turns silos into autonomous decisions.

The opportunity is to move from "ML model that flags a problem on a dashboard" to **autonomous multi-agent systems that diagnose, decide, and act (with human gates)** across maintenance, energy, procurement, quality, compliance, logistics, safety, and commercial functions.

---

## 1. Opportunity scoring summary

| # | Opportunity | Pain | Urgency | AI Feasibility | Market | Revenue |
|---|-------------|------|---------|----------------|--------|---------|
| 1 | Predictive Maintenance & Autonomous Work-Order Agent | 9 | 9 | 8 | 9 | 9 |
| 2 | Energy / Coke-Rate / Process Optimization Agent | 9 | 8 | 7 | 9 | 9 |
| 3 | CBAM + CCTS Carbon Compliance Agent | 8 | 10 | 8 | 7 | 8 |
| 4 | Raw-Material Procurement Intelligence Agent | 9 | 9 | 7 | 8 | 8 |
| 5 | Surface-Defect / Quality Yield Agent | 8 | 7 | 9 | 8 | 8 |
| 6 | Rail Rake & Outbound Logistics Agent | 7 | 7 | 8 | 6 | 7 |
| 7 | Safety Sentinel (PPE/zone/permit) Agent | 9 | 8 | 7 | 7 | 7 |
| 8 | Sales / Dynamic Pricing & Demand Agent | 7 | 6 | 7 | 7 | 7 |
| 9 | Scrap Sourcing & Charge-Mix Optimization Agent | 7 | 7 | 7 | 6 | 7 |
| 10 | Finance / AP-AR / GST Reconciliation Agent | 7 | 6 | 8 | 6 | 7 |
| 11 | Plant Knowledge / SOP Tribal-Knowledge Agent | 8 | 6 | 8 | 6 | 6 |
| 12 | Executive Decision Cockpit (cross-plant) Agent | 7 | 6 | 7 | 8 | 7 |

---

## 2. The opportunities (detail)

### 1. Predictive Maintenance & Autonomous Work-Order Agent
**Problem.** Unplanned downtime is the single largest controllable cost. Globally the steel industry spent ~$4.2B on unplanned downtime in 2024 (5–8% of operating cost); a single hour can cost **$50k–$150k** depending on the area (Source: Oxmaint, 2025, https://oxmaint.com/industries/steel-plant/ai-predictive-maintenance-steel-plants-implementation-roadmap ; AssetWatch, https://www.assetwatch.com/blog/steel-and-metal-ai-predictive-maintenance). In India only ~40% of plants run predictive maintenance; reactive-heavy plants pay 3–4× per repair event.

**Why existing fails.** Condition-monitoring dashboards flag anomalies but a human still has to diagnose, decide, raise the work order in SAP-PM/Maximo, check spares, and schedule against the production plan. That loop is slow and breaks at night/weekends.

**Agentic solution.** Multi-agent loop: (a) *Sensing agent* fuses vibration/MCA/thermal/historian; (b) *Diagnosis agent* (RAG over OEM manuals + failure history) ranks root causes; (c) *Spares agent* checks inventory & lead time; (d) *Scheduling agent* slots work against the production plan; (e) *Work-order agent* drafts the SAP-PM order. **Human gate:** maintenance head approves before execution. Integrations: SAP-PM/Maximo, historian (PI/Aspen), CMMS, IIoT gateways.

**Automation: High · Complexity: High.** ROI 6–12 mo (91% report ROI within 12 mo; 35–55% downtime cut). Vendors: AssetWatch, Oxmaint, ifactory, Aspen Mtell, Uptake, plus Indian SIs (Fractal, Tredence). **Gap:** most stop at prediction; nobody closes the loop to autonomous SAP work-order + spares + scheduling with HITL.

---

### 2. Energy / Coke-Rate / Process Optimization Agent
**Problem.** Blast-furnace ironmaking is ~70% of plant energy & emissions; coke rate drift and over-firing silently burn margin (Source: ifactory, 2026, https://ifactoryapp.com/blog/blast-furnace-optimization-ai-steel-industry).

**Cost of inaction.** A documented case cut coke rate to 375 kg/tHM in 4 months = **₹45 Cr/yr fuel savings on a single furnace**; integrated energy AI = ~11% energy-cost reduction, **$8.8–13.2M/yr for a 2 MTPA plant** (Source: ifactory, 2026, https://ifactoryapp.com/industries/steel-plant/energy-cost-optimization-ai-insights).

**Why existing fails.** APC/Level-2 systems are rule-based and tuned periodically; they don't reason across 200+ variables or adapt to changing burden/ore quality in real time, and they're closed black boxes operators distrust.

**Agentic solution.** *Setpoint advisor agent* tunes hot blast/PCI/burden every 60s; *constraints agent* enforces safety/quality envelopes; *explainer agent* tells the operator why. **Human gate:** operator confirms setpoint bands; full autonomy only inside pre-approved guardrails. Integrations: Level-2 PLC/DCS, historian, quality lab (LIMS).

**Automation: High · Complexity: High.** ROI 3–9 mo. Vendors: ifactory, Fero Labs, Petuum/industrial-AI, ABB/Honeywell APC. **Gap:** closed-loop autonomy with operator-trust UX and India-tuned models for variable domestic ore/coal blends.

---

### 3. CBAM + CCTS Carbon Compliance & Decarbonization Agent
**Problem.** EU **CBAM live Jan 2026**; Indian steel faces the steepest exposure (~32% cost rise by 2032, €200+/t at €80/t CO₂). Domestically, **CCTS** sets 2–3% emission-intensity cuts in 2025-26 tightening to 4–6% by 2026-27, with mandatory MRV and CCC trading from mid-2026 (Source: CO2 AI, 2026; ICAP, 2025; CarbonNeeti, https://carbonneeti.com/blog/ccts-india-2025-2026-complete-guide).

**Why existing fails.** Carbon accounting is done in spreadsheets by small ESG teams; CBAM needs **embedded-emissions per product per shipment** and CCTS needs verifiable facility-level MRV — manual, error-prone, and audit-fragile.

**Agentic solution.** *Data-collection agent* pulls energy/material flows from MES/SAP/historian; *emissions-calc agent* computes embedded CO₂ per heat/coil/shipment per CBAM & CCTS methodology; *report agent* drafts CBAM declarations + CCTS MRV; *abatement-scenario agent* simulates marginal abatement cost vs CCC price to advise buy-credits-vs-abate. **Human gate:** ESG/finance sign-off before filing (regulatory). Integrations: SAP, MES, Indian Carbon Market Portal, EU CBAM registry.

**Automation: Medium · Complexity: Medium-High.** ROI 6–12 mo (avoided penalties + optimized credit trades). Vendors: CO2 AI, CleanCarbon.ai, Sentra, CarbonNeeti, Persefoni. **Gap:** none do agentic *abatement-vs-trade decisioning* tied live to plant data + dual CBAM/CCTS coverage for India.

---

### 4. Raw-Material Procurement Intelligence Agent
**Problem.** ~90% coking-coal import dependence; benchmark premium HCC hit **$252.5/t (Feb 2026, +50% over 2025 lows)**; landed-cost bands swing **$15–25/t** on freight+FX (Source: S&P Global, 2025; IEEFA, https://ieefa.org/resources/west-asia-conflict-exposing-indias-steel-energy-security-risk). Procurement is the single biggest cost lever and it's geopolitically fragile.

**Why existing fails.** Buyers track prices in spreadsheets/broker calls; hedging, supplier diversification, and timing are done on gut. No system fuses commodity indices + FX + freight + geopolitical news + inventory + production plan into a buy/hedge decision.

**Agentic solution.** *Market-intel agent* ingests Platts/Argus indices, FX, Baltic freight, geopolitical news; *demand agent* reads the production plan + inventory; *scenario agent* runs buy-now vs hedge vs wait; *negotiation-prep agent* drafts supplier RFQs and BATNA. **Human gate:** procurement head approves PO/hedge. Integrations: SAP MM/Ariba, commodity data feeds, treasury system.

**Automation: Medium-High · Complexity: Medium-High.** ROI 3–9 mo (even 1–2% on a multi-thousand-Cr coal bill is huge). Vendors: Metalbook, mjunction, Kpler/Vortexa (data), generic S2P suites. **Gap:** an agent that turns market intelligence into *autonomous timed buy/hedge recommendations* against live plant demand.

---

### 5. Surface-Defect & Quality Yield Agent
**Problem.** Scrap/rework ~2.2% of revenue; a ₹500 Cr plant loses ~₹11 Cr/yr; surface quality is an $80–220/t swing; manual inspectors miss **18–34%** of defects and physically can't see at hot-strip speeds (Source: ifactory, 2026, https://ifactoryapp.com/industries/steel-plant/ai-vision-inspection-steel-surface-defect-detection ; Qualitas Tech).

**Cost of inaction.** One missed defect on a 25-t automotive coil = **$80k–400k** in penalties; one India producer lost **₹15 Cr/yr** to undetected defects, recovered via vision AI (98.5% detection) with 7-month payback.

**Why existing fails.** Pure CV systems detect but don't act — they don't trace root cause back to the upstream process parameter, re-grade the coil commercially, or adjust the mill. Detection without closed loop.

**Agentic solution.** *Vision agent* (existing CV) detects; *root-cause agent* correlates defect to upstream Level-2 params; *disposition agent* auto-regrades/re-routes the coil and updates the order; *feedback agent* recommends a mill setpoint change. **Human gate:** quality manager approves re-grade & setpoint change. Integrations: line cameras, MES, Level-2, ERP order book.

**Automation: High · Complexity: Medium.** ROI 6–12 mo. Vendors: ISRA Vision, Qualitas, ifactory, Akridata, AB Dynamics. **Gap:** the closed loop from defect → root cause → commercial disposition → process correction.

---

### 6. Rail Rake & Outbound Logistics Agent
**Problem.** A mid plant taking 3 rakes/day faces **₹8–15 lakh/month avoidable demurrage** (₹150/wagon/hr); rake management is still manual at most plants despite 1.5B t/yr moving by rail (Source: Helios Tech, https://www.heliostechsolutions.in/blogs/rake-guard-indias-first-fully-automated-rake-to-tippler-system).

**Why existing fails.** FOIS tracking exists but is just visibility; nobody orchestrates rake placement, yard prep, loading sequence, and customer dispatch commitments together. Decisions are reactive.

**Agentic solution.** *Tracking agent* (FOIS/FNR feeds) predicts rake ETA; *yard-prep agent* sequences loading/unloading; *dispatch agent* matches rakes to confirmed orders & customer windows; *demurrage agent* flags risk and reschedules. **Human gate:** logistics controller confirms placement plan. Integrations: FOIS, TMS, SAP SD, yard IoT.

**Automation: Medium-High · Complexity: Medium.** ROI 3–9 mo. Vendors: Rake Guard (Helios), TMILL, Mahindra Logistics. **Gap:** agentic orchestration (not just tracking) tying rakes to the order book and demurrage avoidance.

---

### 7. Safety Sentinel Agent (PPE / zone / permit-to-work)
**Problem.** Fatal incidents recur: 4 dead at AM/NS Hazira Corex (Jan 2025), 9 dead at a Vizag steel plant explosion; OSHWC self-certification weakens external inspection (Source: Business & Human Rights Centre, 2025, https://www.business-humanrights.org/en/latest-news/india-four-workers-killed-and-one-injured-in-fire-after-equipment-failure-at-arcelormittal-steel-plant/).

**Cost of inaction.** A fatality = statutory compensation + plant shutdown + reputational + leadership liability under the Factories Act/OSHWC. Hard to fully quantify but routinely **₹crores per serious incident [estimate]** plus production halts.

**Why existing fails.** CCTV is watched by humans (or not). PPE/zone-intrusion detection exists in pilots but doesn't connect to permit-to-work, gas sensors, or automated escalation/lockout.

**Agentic solution.** *Vision agent* detects PPE/zone breaches near hot metal/cranes; *permit agent* cross-checks live permit-to-work; *gas/sensor agent* fuses CO/temperature; *escalation agent* alerts supervisor, can trigger interlock, logs for compliance. **Human gate:** humans confirm any equipment lockout; agent advises, supervisor acts (safety-critical → graduated autonomy). Integrations: CCTV/RTSP, gas sensors, PTW system, PA/alarm, SAP-EHS.

**Automation: Medium · Complexity: Medium-High.** ROI 6–12 mo (one prevented incident pays for years). Vendors: Intenseye, Protex AI, Everguard, Indian CV startups. **Gap:** fusing vision + permit + gas into a single escalation agent with auditable compliance trail for Indian regs.

---

### 8. Sales / Dynamic Pricing & Demand-Sensing Agent
**Problem.** TMT ~₹60,500/MT (Mar 2026) but "price islands" by region; sales teams discount reactively, especially quarter-end; demand-sensing is weak (Source: Nexizo, https://nexizo.in ; Madgeek). Margin leaks via undisciplined discounting.

**Why existing fails.** Pricing is in spreadsheets/CRM with manual approvals; no system fuses competitor prices, freight, regional demand (Gati Shakti projects), inventory, and credit risk into a recommended price + dealer-level offer.

**Agentic solution.** *Demand agent* senses regional pipeline (infra/RE projects); *price agent* recommends region/grade/customer price vs competitors+freight; *credit agent* checks dealer exposure; *offer agent* drafts the quote. **Human gate:** sales manager approves price floor & credit. Integrations: SAP SD, CRM, distributor portal, market price feeds (mjunction/SteelonCall).

**Automation: Medium · Complexity: Medium.** ROI 6–12 mo. Vendors: PROS, Vendavo, McKinsey/Periscope, B2B price trackers. **Gap:** India-specific agentic pricing tying dealer credit + freight islands + demand sensing into a live quote engine.

---

### 9. Scrap Sourcing & Charge-Mix Optimization Agent
**Problem.** As EAF/green-steel grows (CBAM/CCTS push), scrap sourcing & charge-mix become a daily margin + emissions decision. Scrap prices and availability are volatile and fragmented across informal vendors.

**Why existing fails.** Charge-mix is set by metallurgists on experience; scrap procurement is broker-driven and opaque; the two aren't optimized jointly against cost, quality, and carbon.

**Agentic solution.** *Scrap-market agent* tracks scrap prices/availability; *charge-mix agent* optimizes scrap-vs-DRI-vs-hot-metal blend for cost + chemistry + carbon intensity (CCTS-relevant); *sourcing agent* drafts purchase plans. **Human gate:** metallurgist + procurement approve. Integrations: LIMS, SAP MM, scrap-market feeds, emissions model (links to #3).

**Automation: Medium · Complexity: Medium-High.** ROI 6–12 mo. Vendors: Metalbook, scrapyard SaaS, Fero Labs (charge optimization). **Gap:** joint cost+quality+carbon charge-mix agent tied to live scrap markets — almost greenfield in India.

---

### 10. Finance / AP-AR / GST & E-Invoice Reconciliation Agent
**Problem.** Steel majors process massive vendor/customer volumes; GST e-invoicing + e-way bills + 2A/2B reconciliation + TDS create heavy manual finance load and ITC leakage risk. Working capital is tied in reconciliation lag.

**Why existing fails.** ERP + bolt-on GST tools still need humans to match invoices, chase mismatches, and release payments; reconciliation is monthly and reactive, causing blocked ITC and disputes.

**Agentic solution.** *Ingestion agent* reads invoices/e-way bills; *match agent* reconciles PO-GRN-invoice + GSTR-2B; *exception agent* chases mismatches with vendors; *payment agent* drafts payment runs; *audit agent* keeps a trail. **Human gate:** finance controller approves payment release (Tier-3 financial). Integrations: SAP FI/MM, GSTN/IRP, banking, vendor portal.

**Automation: Medium-High · Complexity: Medium.** ROI 3–9 mo (faster ITC + fewer disputes + working-capital release). Vendors: ClearTax, Cygnet, Zoho/SAP add-ons, generic AP automation. **Gap:** agentic exception-resolution (autonomous vendor follow-up + reconciliation) vs rule-based matching.

---

### 11. Plant Knowledge / Tribal-Knowledge SOP Agent
**Problem.** Decades of operating knowledge live in retiring veterans, scattered SOPs, shift logs, and incident reports. Contract-worker churn + ageing workforce = repeated mistakes and slow onboarding. Vizag-type incidents linked to ageing infra + knowledge gaps.

**Why existing fails.** Document repositories are dead PDFs; nobody searches them mid-shift. Knowledge isn't captured from daily operations.

**Agentic solution.** *Capture agent* ingests shift logs, incident reports, SOPs, OEM manuals, maintenance history into a knowledge graph; *Q&A agent* (RAG) answers operator questions in Hindi/regional language at the console; *drift agent* flags when current practice deviates from SOP. **Human gate:** SME validates new SOP content before publish. Integrations: DMS, MES, historian, CMMS, voice interface.

**Automation: Medium · Complexity: Medium.** ROI 6–12 mo (faster onboarding, fewer repeat errors). Vendors: generic enterprise RAG (Glean, Microsoft Copilot), Indian SIs. **Gap:** domain-grounded, vernacular, shop-floor-deployed knowledge agent for steel ops.

---

### 12. Executive Decision Cockpit (cross-plant) Agent
**Problem.** Group leadership (multi-plant majors like JSW/Tata/SAIL) lacks a single autonomous layer that synthesizes production, cost, energy, carbon, safety, and commercial signals into prioritized decisions. Data is siloed per plant/function; board decisions lag.

**Why existing fails.** BI dashboards (Power BI/Tableau) are descriptive and pull-based; executives ask analysts, who take days. No system proactively surfaces "this is the decision you need to make this week."

**Agentic solution.** *Aggregator agents* per domain (the agents above feed it); *synthesis agent* ranks cross-plant issues by ₹ impact; *briefing agent* produces a daily/weekly exec brief + recommended actions; *what-if agent* answers natural-language strategic questions. **Human gate:** executives decide; agent advises. Integrations: SAP BW/Datasphere, data lake, all domain agents.

**Automation: Medium · Complexity: High.** ROI 6–12 mo (faster, better capital + ops decisions). Vendors: ThoughtSpot, Microsoft Fabric+Copilot, Fractal/Tredence custom. **Gap:** an agentic *decision* layer (not BI) purpose-built on the steel domain agents above — natural orchestration play once 2–3 domain agents exist.

---

## 3. India market sizing (rough, all [estimate] unless cited)

- **TAM (Indian steel sector AI/digital spend):** the sector is a multi-lakh-crore industry; even 0.3–0.6% of revenue on AI/digital → a **₹3,000–8,000 Cr/yr** addressable digital+AI spend across majors+mid-tier [estimate].
- **SAM (agentic-AI-addressable, large + mid plants, ₹100Cr–₹1L Cr+ revenue):** **~₹1,500–3,000 Cr/yr** [estimate] — concentrated in ~15–25 integrated majors plus ~100 mid-tier mills.
- **SOM (realistically winnable by a focused agentic vendor in 3 yrs):** **~₹150–400 Cr/yr** [estimate], landing 2–4 flagship majors + a dozen mid-tier across 2–3 of the top opportunities (maintenance, energy, carbon).

The **buyer concentration is a feature**: ~20 enterprises drive most of the value, so a focused land-and-expand into JSW/Tata/SAIL/JSPL/AM-NS with one wedge (maintenance or carbon) can compound across the other 11 opportunities.

---

## 4. Competitive landscape & the structural gap

- **Point-solution ML vendors** (ifactory, Oxmaint, AssetWatch, ISRA, Qualitas, Fero Labs) — strong at *detection/prediction*, weak at *closing the loop* and at multi-agent orchestration.
- **Global SIs / hyperscalers** (Deloitte, Accenture, Microsoft Fabric+Copilot, AWS) — broad but not steel-domain-deep; expensive; slow.
- **Indian AI SIs** (Fractal, Tredence, Softweb) — strong delivery, but mostly project-based dashboards, not productized closed-loop agents.
- **Carbon SaaS** (CO2 AI, Sentra, CarbonNeeti, CleanCarbon.ai) — compliance reporting, not decisioning, and rarely dual CBAM+CCTS.

**The gap = the whole thesis:** everyone sells *insight*; nobody sells the **autonomous decision+action layer with human-in-the-loop gates** wired into SAP/MES/Level-2/FOIS/GSTN. Whoever owns the orchestration layer (maintenance work-orders, carbon abatement-vs-trade, procurement buy/hedge timing) owns the mission-critical position. Only ~14% of enterprises have agentic solutions production-ready (Source: Kai Waehner / enterprise agentic landscape, 2026, https://www.kai-waehner.de/blog/2026/04/06/enterprise-agentic-ai-landscape-2026-trust-flexibility-and-vendor-lock-in/), and Gartner expects 40% of enterprise apps to embed agents by end-2026 (Source: ML Mastery, 2026, https://machinelearningmastery.com/7-agentic-ai-trends-to-watch-in-2026/) — the window is now.

---

## 5. Counter-view (steel-man the skeptic)

Steel plants are **safety-critical, capital-heavy, and conservative**. Level-2 process control is already heavily engineered; operators distrust black boxes; OT/IT integration is genuinely hard and regulated; and a single bad autonomous action near a blast furnace is catastrophic. Many "agentic" pilots stall at the integration boundary (only 11% in production). The honest read: the **highest-autonomy opportunities (energy setpoints, safety lockout) will stay human-gated for years**, and the fastest wins are in **back-office and advisory loops** (procurement, carbon, finance, knowledge, exec cockpit) where being wrong is cheap and reversible. The winning go-to-market is *advisory-agent first, autonomy later* — earn trust on recommendations before touching the plant.

## 6. Open questions that would change the ranking

1. **CCTS final steel targets** — still pending; once published, opportunity #3's urgency could jump to a forced 10.
2. **OT/IT integration cost** — real implementation complexity for Level-2/historian access varies hugely by plant vintage; could push #1/#2 ROI windows past 12 months for older mills.
3. **Buyer appetite for autonomy** — will Indian majors accept any closed-loop action, or only advisory? This decides whether the high-value (#1, #2, #5) loops are truly agentic or stay "human-approves-everything."

---

_Sources cited inline. Figures tagged [estimate] are first-principles, not sourced. Draft research note for review. Not investment advice._
