# India Agentic AI Opportunity Map — Agriculture & AgriTech

**Research date:** 2026-06-23
**Analyst:** Jarvis Research-Analyst Specialist
**Scope:** Enterprises ₹100 Cr – ₹1,00,000+ Cr revenue across the agri value chain (input cos, dairy, agritech platforms, warehousing/commodity finance, cold-chain, food processors, agri-lenders/insurers, FPO aggregators, exporters).
**Lens:** Where autonomous multi-agent AI — not dashboards/single ML models — becomes a mission-critical business layer in a 3–12 month horizon.

> Draft research note for review. Cited where possible; [estimate] elsewhere. Not investment advice.

---

## 1. Industry Overview (Why agriculture is an agentic-AI goldmine)

- Agriculture + allied contributes **17.8% of India's GDP (FY24)** and employs **~46% of the workforce (~600M people)**; agri+allied GVA grew from ~US$170B (FY12) to **US$610.5B (FY25)**. (Source: IBEF/Invest India via search, 2026, https://www.ibef.org/blogs/agritech-landscape-in-india)
- **AgriTech market:** ~US$0.97B (2025) → US$2.52B (2034) at ~10.6% CAGR on a narrow definition; broader infra-led definition puts it at **US$9B (2025) → US$28B (2030)**. Penetration only ~1.5% of a US$24B opportunity (EY). (Source: IMARC / Inc42, 2026, https://inc42.com/features/inside-indias-28-bn-agritech-opportunity-and-the-rise-of-ai-powered-farming/)
- **4,990+ agritech startups, ₹54,000 Cr (~US$6.44B) cumulative funding.** Leaders: DeHaat, Ninjacart, Arya.ag, Cropin, Fasal, AgNext, StarAgri, Garuda. (Source: Agrijob/Decentro, 2026)
- Structure: highly fragmented at the farm gate (~120M farm households, ~86% smallholders), but **consolidating fast at the enterprise layer** — input majors (Coromandel 1,100+ Gromor stores, 3M farmers; UPL multinational), dairy (Amul ₹65,911 Cr FY25, Hatsun ₹8,700 Cr FY25), commodity infra (StarAgri 2,200+ warehouses, 380 locations).

**Why now (the agentic setup):**
1. **Data finally exists.** 54,150 of 67,930 PACS on ERP; e-NAM has 1.79 Cr farmers, 4,518 FPOs, ₹4.39 lakh Cr traded; 10,000 FPOs registered (Dec 2025); WDRA regulated warehousing ~44.8M tonnes. The rails for agent-readable data are live.
2. **Government push** — Mission for Integrated Horticulture (₹6,000 Cr), PMKSY cold-chain (₹6,520 Cr through Mar 2026), drone/IoT mandates.
3. **Massive recurring loss pools** — ₹1.52 lakh Cr/yr post-harvest losses; KCC NPAs at ₹97,543 Cr (Dec 2024); 20–30% of production lost post-harvest.
4. Agri decisions are **high-frequency, multi-variable, deadline-bound** (weather windows, perishability, mandi price swings, claim deadlines) — exactly where autonomous agents beat dashboards a human can't watch fast enough.

---

## 2. Competitive Landscape (enterprise layer)

| Player | Model | TTM Revenue | Moat | Risk |
|--------|-------|-------------|------|------|
| DeHaat | Full-stack input→advisory→credit→market | ₹3,000 Cr FY25, ₹369 Cr PAT | Farmer network + exports (32 mkts) | Thin AI; mostly ops |
| Ninjacart | Farm→retail supply chain | $407M raised; 1,400 T/day | Logistics density | Margin-thin, capital-hungry |
| Cropin | SaaS crop intelligence (AI/satellite) | [UNSOURCED] | Data platform, agri-FI clients | Sells dashboards, not autonomy |
| Fasal | IoT precision farming (horticulture) | [UNSOURCED] | Hardware + microclimate AI | Niche crops, hardware capex |
| AgNext | CV-based commodity quality testing | [UNSOURCED] | Spectroscopy + CV IP | Single point in chain |
| StarAgri/Arya.ag | Warehousing + collateral mgmt + WRF | [UNSOURCED]; 2,200+ WH | Physical network, lender trust | Fraud/quality risk in collateral |
| Coromandel / UPL | Input mfg + retail | UPL multinational; Coromandel 1,100+ stores | Brand, dealer channel, R&D | Channel inventory + credit leakage |
| Amul / Hatsun / Mother Dairy | Dairy procurement→brand | Amul ₹65,911 Cr; Hatsun ₹8,700 Cr FY25 | Cooperative density, cold chain | Adulteration, procurement leakage |

(Sources as cited in Section 1; revenues from search results 2026.)

**The gap:** Almost every incumbent ships **dashboards, advisories, or single-task ML** (disease ID, satellite NDVI, quality grading). Nobody yet runs **closed-loop autonomous multi-agent systems** that sense → decide → act → escalate across procurement, claims, finance, and supply-chain orchestration with human-in-loop only at money/risk checkpoints. That white space is the opportunity map below.

---

## 3. The 12 Agentic AI Opportunities

Scores are 1–10, calibrated (not everything is a 9). ROI horizon emphasis: 3–12 months.

### OPP-1 — Crop-Insurance Claims & Underwriting Orchestration Agent (PMFBY)
- **Problem:** PMFBY claim settlement delays drive KCC NPAs (₹68,547 Cr→₹97,543 Cr, Mar'21→Dec'24). Insurers (IRDAI-regulated GICs) manually reconcile CCE yield data, satellite, weather, and farmer claims — slow, dispute-heavy.
- **Cost of inaction:** A material slice of the ~₹29,000 Cr NPA rise is claim-delay-linked [estimate]; insurers bleak on fraud + ops cost.
- **Why existing fails:** Satellite-yield startups give a *score*; humans still adjudicate. No autonomy, no audit trail IRDAI trusts.
- **Agentic solution:** Multi-agent — (a) Satellite/weather ingest agent, (b) CCE-reconciliation agent, (c) fraud-anomaly agent, (d) claim-drafting agent, (e) DPDP-compliant audit agent. Human-in-loop: payout above ₹X, fraud flags. Integrations: PMFBY portal, CCE data, IMD, NRSC/Bhuvan, insurer core.
- Automation: **High** · Complexity: **High** · ROI: 6–12 mo, claim-cycle cut 40–60% [estimate]
- Scores — market 8, pain 9, urgency 9, feasibility 6, revenue 8
- TAM/SAM/SOM (India): ~₹3,000 Cr addressable insurer+lender ops/fraud spend / ₹600 Cr serviceable / ₹60 Cr SOM [estimate]
- Competition: Cropin, RMSI, Satsure (scoring); **gap = closed-loop adjudication + IRDAI-grade auditability**

### OPP-2 — Agri-Lending Credit & Early-Warning Agent (KCC / FPO loans)
- **Problem:** KCC NPAs ₹97,543 Cr (Dec'24); banks underwrite on thin data, monitor reactively. Collateral-free limit now ₹2 lakh — more unsecured exposure.
- **Cost of inaction:** Provisioning on ~₹97k Cr NPA stock; lost lending growth.
- **Why existing fails:** Credit-scoring models are static; no continuous agentic monitoring of crop/weather/price/repayment signals.
- **Agentic solution:** Agents for alt-data underwriting (satellite yield, e-NAM price realization, weather), repayment early-warning, restructuring-recommendation, RBI/DPDP audit. Human-in-loop: sanction, restructure. Integrations: bank LOS/LMS, KCC, PMFBY, e-NAM, account aggregator (RBI AA).
- Automation: **High** · Complexity: **High** · ROI: 6–12 mo, NPA slippage cut 15–25% [estimate]
- Scores — market 9, pain 9, urgency 8, feasibility 6, revenue 9
- TAM/SAM/SOM: ~₹4,000 Cr lender agri-ops/risk spend / ₹800 Cr / ₹80 Cr [estimate]
- Competition: Jai Kisan, Samunnati, Arya.ag (lending); **gap = autonomous portfolio early-warning + AA-native**

### OPP-3 — Cold-Chain Spoilage Prevention & Energy-Optimization Agent
- **Problem:** 20–30% post-harvest loss; cold-chain electricity = up to **30% of opex**; spoilage 35–40% for tomato/potato/onion. ~8,800 cold stores, ~40M MT.
- **Cost of inaction:** Share of ₹1.52 lakh Cr loss + energy waste; per-facility spoilage + power leak in ₹ crores/yr [estimate].
- **Why existing fails:** IoT vendors (Datoms etc.) give temperature *alerts*; humans react late, no autonomous control or energy arbitrage.
- **Agentic solution:** Agents — sensor-fusion, spoilage-risk predictor, setpoint-control/energy-arbitrage (tariff-aware), maintenance-dispatch, reefer-routing. Human-in-loop: compressor shutdown, dispatch approval. Integrations: IoT/SCADA, DISCOM tariff, WMS, logistics TMS.
- Automation: **High** · Complexity: **Medium** · ROI: 3–9 mo, spoilage −20–30%, energy −10–15% [estimate]
- Scores — market 8, pain 9, urgency 8, feasibility 7, revenue 8
- TAM/SAM/SOM: cold-chain mkt INR 2,535B (2025); AI-control SOM ~₹500 Cr / ₹120 Cr / ₹15 Cr [estimate]
- Competition: Datoms, Tessol, Ecozen; **gap = autonomous control loop + energy arbitrage, not just alerts**

### OPP-4 — Procurement & Dealer-Channel Intelligence Agent (input majors, dairy)
- **Problem:** Input majors (Coromandel 1,100+ stores, UPL) and dairy (Amul, Hatsun) run vast dealer/village-society channels with credit leakage, channel-stuffing, demand-forecast misses, payment delays.
- **Cost of inaction:** Channel credit losses + working-capital drag in tens of ₹ crores per enterprise/yr [estimate].
- **Why existing fails:** ERP + BI dashboards report the past; no agent that forecasts, negotiates replenishment, and flags credit risk autonomously.
- **Agentic solution:** Agents — demand-forecast (weather/sowing/price), dealer-credit-risk, replenishment/PO drafting, payment-reconciliation, GST e-invoice/e-way validation. Human-in-loop: credit-limit changes, large POs. Integrations: SAP/Oracle ERP, GSTN, dealer apps, weather, e-NAM/mandi prices.
- Automation: **High** · Complexity: **Medium** · ROI: 4–9 mo, channel WC −10–20% [estimate]
- Scores — market 8, pain 8, urgency 7, feasibility 8, revenue 8
- TAM/SAM/SOM: ~₹2,500 Cr enterprise agri-supply-chain software / ₹500 Cr / ₹60 Cr [estimate]
- Competition: SAP, generic BI, Bizom (DMS); **gap = agentic forecast→PO→credit closed loop for agri seasonality**

### OPP-5 — Export Compliance & Pesticide-Residue Traceability Agent
- **Problem:** Indian agri/food exports face EU/US rejections on MRL residue + documentation/traceability gaps; FSSAI MRL SOPs, APEDA, Codex/WTO-SPS. SME exporters lack NABL labs + traceability.
- **Cost of inaction:** Rejected consignments = immediate loss + long-term buyer trust erosion; rejections cost lakhs–crores per shipment [estimate].
- **Why existing fails:** Manual paperwork, point-in-time lab tests; no continuous farm-to-port traceability or pre-shipment risk agent.
- **Agentic solution:** Agents — farm-input/spray-log capture, residue-risk predictor (crop+region+pesticide), NABL-lab orchestration, doc-pack assembler (APEDA/FSSAI/phytosanitary), buyer-spec matcher. Human-in-loop: shipment release, lab booking. Integrations: APEDA, FSSAI MRL DB, NABL labs, blockchain/traceability, buyer EDI.
- Automation: **Medium-High** · Complexity: **High** · ROI: 6–12 mo, rejection rate −50%+ [estimate]
- Scores — market 7, pain 8, urgency 7, feasibility 6, revenue 7
- TAM/SAM/SOM: ~₹1,500 Cr export-compliance services / ₹400 Cr / ₹40 Cr [estimate]
- Competition: TraceX, AgNext (testing); **gap = autonomous pre-shipment compliance orchestration**

### OPP-6 — Warehouse-Receipt Finance Quality & Fraud-Control Agent
- **Problem:** WRF/collateral mgmt (StarAgri 2,200+ WH, Arya.ag) relies on manual quality grading + stock audits; lenders fear quality fraud, phantom stock, grade inflation. WDRA ~44.8M MT regulated.
- **Cost of inaction:** Collateral fraud losses + lender risk premium that throttles WRF growth — a credit pool worth tens of thousands of crores [estimate].
- **Why existing fails:** Periodic human audits; CV grading exists but isn't woven into an autonomous fraud-control + lender-reporting loop.
- **Agentic solution:** Agents — CV/spectroscopy grading, stock-reconciliation (IoT weighbridge + CCTV), anomaly/fraud detector, e-NWR + lender-reporting, WDRA-compliance. Human-in-loop: fraud escalation, loan-to-value override. Integrations: WDRA e-NWR, lender core, IoT, CV grading (AgNext-style).
- Automation: **High** · Complexity: **High** · ROI: 6–12 mo, fraud loss −30–50% [estimate]
- Scores — market 7, pain 8, urgency 7, feasibility 7, revenue 7
- TAM/SAM/SOM: ~₹1,200 Cr collateral-mgmt/WRF ops / ₹300 Cr / ₹30 Cr [estimate]
- Competition: StarAgri, Arya.ag, NCML (in-house); **gap = independent agentic fraud-control layer lenders trust**

### OPP-7 — Dairy Procurement Quality & Adulteration Agent
- **Problem:** Dairy majors (Amul 28M L/day, 18,600 societies; Hatsun) test milk at thousands of collection points; adulteration + fat/SNF fraud + payment disputes are chronic, especially unorganized supply.
- **Cost of inaction:** Quality-fraud + payment errors across millions of daily transactions; ₹ crores/yr per major [estimate].
- **Why existing fails:** Analyzers at BMCs give readings; no autonomous agent linking test→fraud-pattern→farmer-payment→corrective dispatch.
- **Agentic solution:** Agents — milk-analyzer ingest, adulteration/fat-fraud anomaly, dynamic farmer-payment, route/chilling cold-chain optimizer, FSSAI-compliance. Human-in-loop: payment disputes, supplier blacklisting. Integrations: BMC analyzers, procurement ERP, payment rails (IMPS/UPI), cold-chain IoT.
- Automation: **High** · Complexity: **Medium** · ROI: 3–9 mo, quality-loss −15–25% [estimate]
- Scores — market 7, pain 8, urgency 7, feasibility 7, revenue 7
- TAM/SAM/SOM: dairy ₹65k+ Cr leaders; agentic-procurement SOM ~₹800 Cr / ₹200 Cr / ₹25 Cr [estimate]
- Competition: Stellapps, Prompt; **gap = closed-loop fraud→payment→cold-chain agent vs. point analyzers**

### OPP-8 — Mandi-Price & Trading Intelligence Agent (procurement arbitrage)
- **Problem:** Aggregators, FPOs (10,000 registered; ₹5,035 Cr turnover), processors buy across 1,000s of APMCs/e-NAM with volatile prices, asymmetric info, suboptimal timing/location of buying & selling.
- **Cost of inaction:** Margin left on table from poor buy/sell timing — 2–5% of procurement value [estimate], large at scale.
- **Why existing fails:** Price portals (e-NAM, Agmarknet) show data; no agent that forecasts, recommends, and executes arbitrage with logistics constraints.
- **Agentic solution:** Agents — price-forecast (mandi+weather+arrivals), arbitrage-opportunity, logistics-cost optimizer, contract/GST-compliant trade executor, hedging-advisor. Human-in-loop: trade execution above ₹X, hedging. Integrations: e-NAM/Agmarknet, NCDEX, GSTN, TMS, FPO/ONDC.
- Automation: **Medium-High** · Complexity: **Medium** · ROI: 3–9 mo, procurement margin +1.5–3% [estimate]
- Scores — market 8, pain 7, urgency 7, feasibility 7, revenue 8
- TAM/SAM/SOM: e-NAM trade ₹4.39 lakh Cr; intelligence SOM ~₹600 Cr / ₹150 Cr / ₹20 Cr [estimate]
- Competition: Ninjacart, DeHaat (in-house), Agmarknet (data); **gap = autonomous arbitrage + execution layer for FPOs/processors**

### OPP-9 — Predictive Maintenance Agent for Agri-Processing & Cold-Chain Assets
- **Problem:** Sugar mills, dairy plants (Hatsun 20 plants), food processors, ~8,800 cold stores suffer unplanned downtime during peak/crush season — perishable + seasonal, so downtime is catastrophic.
- **Cost of inaction:** A crush-season breakdown can cost ₹ crores/day in spoilage + idle capacity [estimate].
- **Why existing fails:** Reactive/scheduled maintenance; SCADA alerts aren't tied to autonomous spares-procurement + crew-dispatch.
- **Agentic solution:** Agents — vibration/thermal/sensor-fusion failure predictor, RUL estimator, spares-procurement (auto-PO), crew-scheduling, downtime-cost simulator. Human-in-loop: shutdown, capex spares. Integrations: SCADA/PLC, CMMS (SAP PM), IoT, vendor catalogs/GSTN.
- Automation: **High** · Complexity: **Medium-High** · ROI: 4–10 mo, unplanned downtime −25–40% [estimate]
- Scores — market 7, pain 8, urgency 7, feasibility 7, revenue 7
- TAM/SAM/SOM: agri-processing PdM ~₹1,000 Cr / ₹250 Cr / ₹30 Cr [estimate]
- Competition: generic PdM (Uptime, Infinite Uptime); **gap = agri-seasonality-aware closed loop (predict→procure→dispatch)**

### OPP-10 — FPO Operations Co-Pilot & Compliance Agent
- **Problem:** 10,000 FPOs now registered, ₹5,035 Cr turnover, but most lack staff for GST, accounting, license renewals (seed/fertilizer/mandi), credit-guarantee paperwork, ONDC/e-NAM onboarding. Only 2,583 secured CGF loans.
- **Cost of inaction:** Stranded ₹18 lakh/FPO grants + ₹2 Cr credit guarantees underused; FPO mortality from ops failure [estimate].
- **Why existing fails:** Manual handholding by CBBOs doesn't scale to 10,000 collectives; no autonomous back-office.
- **Agentic solution:** Agents — bookkeeping/GST-filing, license-renewal tracker, credit-application assembler, e-NAM/ONDC listing & order mgmt, member-payment reconciler. Human-in-loop: filings sign-off, loan submission. Integrations: GSTN, SFAC/NABARD, e-NAM/ONDC, banking AA, Tally.
- Automation: **High** · Complexity: **Medium** · ROI: 3–9 mo, FPO ops cost −40%, credit access ↑ [estimate]
- Scores — market 7, pain 8, urgency 8, feasibility 8, revenue 7
- TAM/SAM/SOM: 10,000 FPOs × ~₹3L ops/yr ≈ ₹300 Cr TAM / ₹120 Cr / ₹15 Cr [estimate]
- Competition: CBBOs (manual), Khetigaadi/local; **gap = scalable autonomous FPO back-office**

### OPP-11 — Sustainability, Carbon & ESG Reporting Agent (agri value chain)
- **Problem:** Exporters, food majors, dairy face buyer + EU CBAM-style + DPDP/BRSR pressure to prove sustainable sourcing, water/carbon footprint, and farmer traceability — currently manual, audit-heavy.
- **Cost of inaction:** Lost premium/export access + compliance cost; ESG non-compliance can gate large contracts [estimate].
- **Why existing fails:** Consultant-led, periodic, spreadsheet ESG; no continuous agentic measurement-reporting-verification (MRV).
- **Agentic solution:** Agents — farm-practice data capture, carbon/water MRV calculator, supplier-ESG scorer, BRSR/buyer-report assembler, carbon-credit (voluntary market) facilitator. Human-in-loop: report sign-off, credit issuance. Integrations: satellite, farm apps, BRSR, carbon registries (Verra/Gold Standard), buyer portals.
- Automation: **Medium-High** · Complexity: **High** · ROI: 6–12 mo, ESG-reporting cost −50%, premium capture [estimate]
- Scores — market 6, pain 7, urgency 6, feasibility 6, revenue 7
- TAM/SAM/SOM: agri-ESG/carbon services ~₹1,000 Cr / ₹250 Cr / ₹25 Cr [estimate]
- Competition: Boomitra, Varaha, Nurture.farm; **gap = integrated MRV + reporting + finance agent for enterprises**

### OPP-12 — Executive Decision-Support / "Agri War-Room" Agent
- **Problem:** Boards of input majors, dairy, agritech, processors juggle weather, prices, policy (MSP, export bans), demand, channel, NPA, and competitor moves — decisions lag because synthesis is manual.
- **Cost of inaction:** Slow response to onion/wheat export bans, monsoon shifts, price crashes = margin and inventory losses in ₹ crores [estimate].
- **Why existing fails:** Static BI dashboards; no agent that monitors, synthesizes scenarios, and recommends with quantified impact.
- **Agentic solution:** Agents — policy/news monitor (export bans, MSP), weather/price scenario simulator, demand-supply planner, competitor-intel, board-brief generator. Human-in-loop: all strategic calls (advisory only). Integrations: IMD, e-NAM/NCDEX, news, ERP/BI, govt notifications.
- Automation: **Medium** · Complexity: **Medium** · ROI: 3–9 mo, faster decisions, downside avoidance [estimate]
- Scores — market 6, pain 7, urgency 6, feasibility 7, revenue 6
- TAM/SAM/SOM: enterprise agri decision-support ~₹600 Cr / ₹150 Cr / ₹15 Cr [estimate]
- Competition: generic BI (Power BI), strategy consultants; **gap = always-on agri-specific autonomous war-room**

---

## 4. Cross-Cutting Themes & Prioritization

**Top 4 by conviction × feasibility (3–12 mo):**
1. **OPP-2 Agri-Lending Early-Warning** — biggest ₹ pool (₹97k Cr NPA), AA rails live, clear buyer (banks/NBFCs).
2. **OPP-3 Cold-Chain Spoilage/Energy** — fastest ROI (3–9 mo), tangible energy + spoilage savings, mid complexity.
3. **OPP-1 PMFBY Claims** — high pain + urgency; gated by IRDAI trust + data access (longer sell).
4. **OPP-4 Procurement/Dealer Intelligence** — enterprise budgets exist, ERP integration is the moat.

**Common enablers:** RBI Account Aggregator, e-NAM/Agmarknet, GSTN, WDRA e-NWR, NRSC/Bhuvan satellite, IMD weather. **Common regulators:** RBI (lending/AA), IRDAI (insurance), FSSAI/APEDA (food/export), WDRA (warehousing), DPDP Act 2023 (farmer PII), GST.

**Honest caveats:**
- Farm-gate data quality is still weak for smallholders — agents must degrade gracefully.
- Regulatory trust (IRDAI/RBI auditability) is the real gate, not model accuracy — build explainability + audit agents first-class.
- Many incumbents will build in-house; the wedge is **independent, multi-tenant, audit-grade agentic layers** vs. captive dashboards.

---

## 5. Counter-View (steel-man)

The strongest argument against agentic AI in Indian agri: **the binding constraint is physical and informational, not cognitive.** Post-harvest losses persist because of missing cold-chain assets, roads, and reliable power — not missing decisions. Smallholder data is sparse, noisy, and seasonal; agents may hallucinate confident actions on bad inputs, and in a low-margin, trust-based, vernacular, offline-first sector, autonomous action carries outsized downside (a wrong auto-shutdown or wrong credit cut hits livelihoods). Incumbents (DeHaat, Amul, Coromandel) already own the farmer relationship and can bolt narrow ML onto existing ops without paying for an autonomous-agent layer. So value may accrue to **boring infra + narrow ML**, with "agentic" being a 2026 buzzword premium that enterprises won't pay for until reliability and ROI are proven on the ground.

**Rebuttal:** The decision-dense, deadline-bound, regulator-audited nodes — claims, lending early-warning, energy arbitrage, compliance — are exactly where human bandwidth is the constraint and where ₹ pools are concentrated. Those are defensible agentic beachheads even if the farm-gate stays analog.

---

## 6. Open Questions (would change the conclusion)

1. **Data access:** Will RBI AA + PMFBY + WDRA expose APIs cleanly enough for third-party agents, or stay walled to incumbents?
2. **Regulatory tolerance for autonomy:** Will IRDAI/RBI accept agentic decision-making with human-in-loop, or demand full human adjudication (killing the automation ROI)?
3. **Willingness to pay:** Do ₹100–1,000 Cr agri enterprises buy independent agentic layers, or default to in-house/captive tooling?

---

> Draft research note for review. Cited where possible; [estimate] elsewhere. Not investment advice.

**Sources:** IBEF AgriTech landscape; IMARC India Agritech Market; Inc42 $28B agritech; Agrijob/Decentro startup data; National Economic Forum / StarAgri post-harvest losses; data.gov.in post-harvest survey; NextIAS / RBI on KCC NPAs; PMFBY portal; USDA FAS / NCAER on export compliance; FSSAI MRL SOP; Brickwork / smallcase / Wikipedia on dairy (Amul, Hatsun); WDRA; StarAgri / Agriwise on WRF; Mordor / Ken Research / Datoms on cold chain; Agro Spectrum / PIB / SFAC on FPOs & e-NAM. (URLs in inline citations above, accessed 2026-06-23.)
