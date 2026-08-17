# India Agentic AI Opportunity Map — Defense & Aerospace

**Research date:** 2026-06-23
**Analyst:** Jarvis Research Analyst Specialist
**Scope:** Indian Defense & Aerospace enterprises, ₹100 Cr to ₹1,00,000+ Cr revenue — DPSUs (HAL, BEL, BDL, MDL, GRSE, BEML), private primes (L&T Defence, Adani Defence, Tata Advanced Systems, Bharat Forge/Kalyani, Mahindra Defence), Tier-1/2/3 suppliers, defence-tech startups, MRO providers, and foreign OEM India arms.

> Draft research note for review. Cited where possible; [estimate] elsewhere. Not investment advice.

---

## 1. Industry Context (Why This Sector, Why Now)

India's defence sector is in a structural up-cycle that makes it unusually fertile for agentic AI:

- **Production:** ₹1,78,000 Cr record defence production in FY2025-26, +15.6% YoY, +110% since FY2020-21. (Source: Khan Global Studies / PIB, 2026, https://currentaffairs.khanglobalstudies.com/defence-production-hits-record-%E2%82%B91-78-lakh-crore-in-fy-2025-26/)
- **Budget:** ₹6.81 lakh Cr (~$78.7B) FY25-26 defence allocation, +9.5% YoY. (Source: Mordor Intelligence, 2026, https://www.mordorintelligence.com/industry-reports/india-defense-market)
- **Exports:** Record ₹38,424 Cr in FY2025-26, up from ₹686 Cr in FY13-14; exports to 80+ countries. Target ₹50,000 Cr by 2029. (Source: Vision IAS / MoD, 2026, https://visionias.in/current-affairs/news-today/2026-04-03/security/indias-defence-exports-reached-an-all-time-high-of-rs-38424-crore-in-fy-2025-26-ministry-of-defence)
- **Order books:** HAL ~₹2.3 lakh Cr backlog + ₹4 lakh Cr pipeline; BEL ₹75,600 Cr (Oct 2025). (Source: Mordor Intelligence, 2026)
- **Indigenization mandate:** 509 import-prohibited items; ~75% of modernization outlay ring-fenced for domestic sourcing; AoN worth ₹6+ lakh Cr to DRDO-designed / Indian-made systems. (Source: IBEF, 2026, https://www.ibef.org/industry/defence-manufacturing)
- **Private sector:** Now ~24% of production (~₹42,000 Cr, highest ever) and 65% of exports. (Source: PIB, 2026)
- **AI ecosystem:** 1,000+ defence-tech startups; $233.5M raised 2025; DRDO CAIR has 75+ AI products; iDEX/ADITI funding ~30 deep-tech areas by 2026; ~₹100 Cr/yr earmarked for military AI. (Source: NextIAS, 2026, https://www.nextias.com/ca/current-affairs/11-05-2026/india-indigenous-ai-defence; India Strategic, 2026)

**Why agentic AI now:** The combination of (a) a procurement/compliance regime of extreme documentary density (DAP 2020/draft DAP 2026, offset banking, SCOMET/DGFT, DGQA), (b) chronic fleet-readiness crises (IAF combat serviceability 50-65%), and (c) a retiring-engineer "talent cliff" with undocumented tribal knowledge creates exactly the conditions where multi-agent systems — that read, reason across silos, draft, and route to a human gate — beat both manual labor and dumb dashboards. Defence's air-gap/sovereignty needs also favor on-prem Indian-stack agentic deployments (a moat against US SaaS).

**Hard constraint to respect throughout:** Anything touching weapons-release, targeting, or kinetic decisions stays human-controlled (ORF doctrine: "meaningful human control"). The opportunities below deliberately target the **business/enterprise layer** — procurement, MRO, compliance, supply chain, finance, knowledge — NOT the kill chain.

---

## 2. The Opportunities (12)

### OPP-1 — Predictive Fleet-Readiness & Spares Orchestration Agent
**Problem:** IAF combat serviceability runs 50-65% vs 75% desired; Su-30MKI fleet has dropped to 48-60%. Propulsion + avionics + spares shortages drive grounding; cannibalization is rampant. Fighter fleets need ~5% of aircraft value/yr in spares to stay ready. (Source: DefenceXP, 2026, https://www.defencexp.com/why-only-60-of-indias-fighter-jets-are-ready-for-war/)
**Cost of inaction:** A single grounded Su-30 squadron's lost availability + emergency-AOG procurement premiums run ₹100s of Cr/yr fleet-wide [estimate]. ~80% of MRO is still outsourced abroad, adding FX + turnaround penalty. (Source: TheCore, 2026, https://www.thecore.in/business/aircraft-maintenance-india-mro-adani-843093)
**Agentic solution:** Multi-agent loop — (a) Sensor/usage-ingest agent (flight hours, engine health, fault codes), (b) Failure-prediction agent (RUL models per LRU), (c) Spares-demand forecasting agent, (d) Procurement-trigger agent that drafts indents/AOG requests, (e) Cannibalization-optimizer agent. Human-in-loop: maintenance officer approves every indent and any inter-aircraft part movement. Data: AME/Form-700 logs, OEM IPC, inventory ERP (SAP/Tally), HAL ROH schedules. Integrations: SAP PM, GeM, OEM portals.
**Automation:** High. **Complexity:** High (data access + airworthiness sign-off).
**ROI:** 6-12 months to measurable AOG-reduction; magnitude high (each 5pp serviceability gain ≈ effective fleet expansion). **Scores:** market 8, pain 9, urgency 9, feasibility 6, revenue 8.
**TAM/SAM/SOM (India):** TAM ₹4,000-6,000 Cr defence MRO software+optimization [estimate]; SAM ₹800 Cr; SOM ₹80-120 Cr 3yr [estimate].
**Competition:** IFS, IBM Maximo, OEM bespoke; gap = India-sovereign, multi-fleet (Russian+Western+indigenous mixed inventory), agentic auto-drafting of indents. None do the mixed-origin Indian inventory problem well.

### OPP-2 — Defence Offset Obligation Management & Discharge Agent
**Problem:** Offsets mandatory >₹2,000 Cr contracts; foreign OEMs face FEMA/RBI banking complexity, multiplier-claim errors (claiming 3x vs eligible 1.5x), incomplete discharge evidence, indigenous-content certificate gaps. Penalties: 5% LD/yr of pending offset value + PG invocation + debarment. ThePrint: offset contracts "in shambles." (Source: Khanna & Associates, 2026, https://khannaandassociates.com/blog/defence-offset-policies-india-2026-compliance-guide/; ThePrint, https://theprint.in/opinion/brahmastra/indias-defence-offset-contracts-are-in-shambles-need-a-revamp/944531/)
**Cost of inaction:** On a ₹10,000 Cr deal with 30% offset = ₹3,000 Cr obligation; 5% LD = ₹150 Cr/yr penalty exposure per slipping program [estimate].
**Agentic solution:** Agents — (a) Obligation-tracker (per contract, banked vs pending, expiry calendar), (b) Multiplier-eligibility classifier (maps each discharge activity to correct 1x/1.5x/2x/3x), (c) Evidence-completeness auditor (flags missing EUC/invoices/IC certs), (d) FEMA/RBI routing checker, (e) Discharge-claim drafter for DDP submission. Human-in-loop: legal/finance head signs every claim filed with MoD.
**Automation:** High. **Complexity:** Medium.
**ROI:** 3-9 months (penalty avoidance is immediate); high. **Scores:** market 7, pain 8, urgency 8, feasibility 8, revenue 7.
**TAM/SAM/SOM:** TAM ₹500-900 Cr (offset advisory + software) [estimate]; SAM ₹300 Cr; SOM ₹40 Cr 3yr.
**Competition:** Big-4 advisory (manual, expensive retainers), Khanna & Associates-type law firms. Gap = no living, agentic compliance system; today it's PDFs + spreadsheets + senior consultants.

### OPP-3 — Defence Tender / Bid Intelligence & Auto-Response Agent
**Problem:** Tenders scatter across MoD eProc, DRDO e-Tender, MES, GeM; niche, time-sensitive, daily-monitored manually; mis-categorization ('Buy Indian-IDDM' vs 'Buy & Make' vs 'Buy Global') and missed deadlines = auto-rejection. (Source: NationalTenders / Minaions, 2026, https://minaions.com/blog/defence-tenders-in-india-drdo-mes-ofb-and-how-private-companies-can-participate)
**Cost of inaction:** A single missed/mis-bid ₹200 Cr program is unrecoverable; bid teams of 5-10 cost ₹2-5 Cr/yr while still missing fits [estimate].
**Agentic solution:** (a) Multi-portal scraping/monitoring agent (GeM/eProc/DRDO/MES), (b) Fit-scoring agent (matches RFP to firm capability + indigenization category), (c) Eligibility/compliance checklist agent (BG, OEM auth, AS9100, MSME status), (d) Bid-draft assembler (technical compliance matrix + boilerplate), (e) Deadline/sentinel agent. Human-in-loop: BD head approves go/no-go + final submission (never auto-submit — Tier-3).
**Automation:** High (monitoring/drafting). **Complexity:** Medium.
**ROI:** 3-6 months; medium-high. **Scores:** market 8, pain 8, urgency 7, feasibility 8, revenue 8.
**TAM/SAM/SOM:** TAM ₹600-1,000 Cr (tender intelligence in defence) [estimate]; SAM ₹350 Cr; SOM ₹50 Cr.
**Competition:** Tender18, BidAssist, GlobalTenders, TendersOnTime — alert/aggregation only, no agentic fit-scoring or draft assembly tuned to DAP categories. That's the gap.

### OPP-4 — SCOMET / Export-Authorization Compliance Agent
**Problem:** Defence exports hit ₹38,424 Cr but each shipment needs SCOMET/DGFT or DDP authorization; EUC must be flawless; 6-8 week processing, longer with inter-ministerial clearance; munitions go via DDP not DGFT. Documentation "far more rigorous" than standard exports. (Source: MEA / IndiaFilings, 2026, https://www.indiafilings.com/learn/export-of-scomet-items)
**Cost of inaction:** A held shipment delays revenue recognition by 6-12 weeks; export-control violations risk debarment + criminal exposure. With exports targeting ₹50,000 Cr, friction directly caps growth [estimate].
**Agentic solution:** (a) Item-classification agent (HS + SCOMET category mapping, esp. Cat 6 munitions routing), (b) EUC/document-assembly agent (right letterhead, signatory, supply-chain POs), (c) End-user red-flag screening agent (denied-party/sanctions lists), (d) Application-package drafter for DGFT IMWG / DDP, (e) Status-tracker. Human-in-loop: export-control officer signs filings; any sanctions hit escalates.
**Automation:** High (classification/drafting). **Complexity:** Medium-High (regulatory accuracy critical).
**ROI:** 3-9 months; high (unlocks export velocity). **Scores:** market 7, pain 8, urgency 8, feasibility 7, revenue 7.
**TAM/SAM/SOM:** TAM ₹300-600 Cr [estimate]; SAM ₹200 Cr; SOM ₹30 Cr.
**Competition:** EximAdvisory, YKG, DGFT-Guru (manual consultants). No agentic, screening-integrated product. Gap is wide.

### OPP-5 — Supplier Qualification, DGQA & AS9100 Compliance Agent
**Problem:** AS9100 is now table-stakes; vendors without it fall off approved lists and lose contracts; DGQA registration needs NCAGE/SCAGE, first-article inspection, mill test reports, full traceability. MSME suppliers (the bulk of Tier-2/3) drown in documentation. (Source: GIC, 2026, https://getisocertificate.com/as9100-certification-defence-industry-india/; JSG 015:2018, DDP)
**Cost of inaction:** A single traceability/verification gap can disqualify an entire program. Prime delays from non-qualified vendors cascade into LD on the prime's own MoD contract [estimate].
**Agentic solution:** For primes managing 100s of MSMEs: (a) Supplier-onboarding agent (collects/validates AS9100, NCAGE, GST, MSME, financials), (b) Document-currency monitor (cert expiries, audit dates), (c) First-article-inspection & traceability auditor (matches mill certs → lot → assembly), (d) NCR/CAPA tracking agent, (e) Risk-scoring agent flagging at-risk suppliers. Human-in-loop: SQA head approves vendor-list add/remove.
**Automation:** High. **Complexity:** Medium.
**ROI:** 4-9 months; medium-high. **Scores:** market 7, pain 7, urgency 7, feasibility 8, revenue 7.
**TAM/SAM/SOM:** TAM ₹500-800 Cr (SQM/QMS for defence) [estimate]; SAM ₹300 Cr; SOM ₹40 Cr.
**Competition:** Deltek, ComplianceQuest, QT9, SAP QM — generic QMS. Gap = India DGQA/JSG-specific + MSME-onboarding agentic layer.

### OPP-6 — Component Obsolescence (DMSMS) Forecasting & Redesign Agent
**Problem:** Military platforms live 25+ years; COTS electronics obsolesce in 5-7. Spares non-availability + OEM withdrawal grounds aircraft; obsolescence forces costly redesigns/LTBs. (Source: Altium/Plexus, 2026, https://www.plexus.com/blog/defense-obsolescence-management/)
**Cost of inaction:** Reactive obsolescence handling is 10x costlier than proactive; a single last-time-buy miss can ground a sub-fleet for quarters [estimate].
**Agentic solution:** (a) BOM-ingest agent (parses legacy + current BOMs), (b) Lifecycle-status agent (cross-checks part status vs IHS/SiliconExpert-type feeds + OEM PCN), (c) Risk-prioritizer (criticality × availability × lead time), (d) Mitigation-recommender (LTB qty calc, form-fit-function alternates, indigenization candidate), (e) Indigenization-sourcing agent (matches to 509-list / domestic suppliers). Human-in-loop: design authority approves any FFF substitution.
**Automation:** Medium-High. **Complexity:** High (data feeds + airworthiness).
**ROI:** 6-12 months; high. **Scores:** market 6, pain 8, urgency 7, feasibility 6, revenue 6.
**TAM/SAM/SOM:** TAM ₹300-500 Cr [estimate]; SAM ₹180 Cr; SOM ₹25 Cr.
**Competition:** IHS Markit/SiliconExpert (data only), Altium, OEM tools. Gap = agentic mitigation + indigenization-list matching for India.

### OPP-7 — Engineering Tribal-Knowledge Capture & Configuration-Management Agent
**Problem:** Up to ~29% of A&D workforce eligible to retire; decades of undocumented tribal knowledge, incomplete schematics, unrecorded mods walking out the door. CM/ECN discipline is patchy in legacy Indian programs. (Source: Altium/A&D workforce, 2026, https://resources.altium.com/p/aerospace-and-defense-proactive-obsolescence-management)
**Cost of inaction:** Re-deriving lost design rationale costs months/engineer; safety risk from drawing-as-built mismatch [estimate].
**Agentic solution:** (a) Knowledge-extraction agent (interviews retiring engineers via structured Q&A, ingests notebooks/emails/CAD comments), (b) RAG knowledge-base builder (searchable design rationale + mod history), (c) Config-consistency auditor (flags drawing vs as-built vs ECN mismatches), (d) ECN-impact-analysis agent (traces a change across drawings/specs/inspection plans), (e) Onboarding-tutor agent for new engineers. Human-in-loop: chief engineer validates captured knowledge before it's authoritative.
**Automation:** Medium. **Complexity:** Medium.
**ROI:** 6-12 months; medium (compounding). **Scores:** market 6, pain 7, urgency 7, feasibility 7, revenue 6.
**TAM/SAM/SOM:** TAM ₹400-700 Cr (KM + CM for defence eng) [estimate]; SAM ₹220 Cr; SOM ₹30 Cr.
**Competition:** PTC Windchill, Siemens Teamcenter (PLM, not knowledge capture); generic enterprise RAG. Gap = defence-CM-aware agentic capture, on-prem/air-gapped.

### OPP-8 — Indigenization & Make-in-India Content-Maximization Agent
**Problem:** 509 import-prohibited items + IDDM content thresholds; primes must continuously increase indigenous content and identify import substitutes, but mapping a BOM to domestic-supplier availability + the positive list is manual. Foreign OEMs need it for offset; primes for category eligibility.
**Cost of inaction:** Mis-stated indigenous content risks category disqualification + offset-credit rejection; missed substitution opportunities lock in FX + import-license friction [estimate].
**Agentic solution:** (a) BOM-decomposition agent, (b) Positive-list / import-prohibition matcher, (c) Domestic-supplier discovery agent (queries SIDM/iDEX/MSME registries for substitutes), (d) Indigenous-content calculator (DAP formula), (e) Substitution-business-case drafter. Human-in-loop: supply-chain head approves sourcing switch.
**Automation:** Medium-High. **Complexity:** Medium.
**ROI:** 4-9 months; medium-high. **Scores:** market 7, pain 7, urgency 8, feasibility 7, revenue 7.
**TAM/SAM/SOM:** TAM ₹400-700 Cr [estimate]; SAM ₹250 Cr; SOM ₹35 Cr.
**Competition:** Manual consultants + SIDM directories. No agentic content-maximization product exists. Strong greenfield.

### OPP-9 — Project / Program Schedule-Risk & Cost-Overrun Sentinel Agent
**Problem:** Defence programs (HAL Tejas, ships at MDL/GRSE, BDL missiles) chronically slip; complex multi-tier dependencies, milestone-linked payments, LD exposure. Decision-making delays compound slippage.
**Cost of inaction:** LD on a ₹5,000 Cr program at even 0.5%/week of delay = ₹25 Cr/week exposure [estimate]; HAL's ₹2.3 lakh Cr backlog magnifies aggregate slippage risk.
**Agentic solution:** (a) Schedule-ingest agent (Primavera/MSP + ERP milestones), (b) Dependency-risk analyzer (critical-path + supplier-delay propagation), (c) Early-warning sentinel (flags slip before it's milestone-visible), (d) Mitigation-options drafter (resource reallocation, parallel-path), (e) Exec-briefing agent (board/MoD review packs). Human-in-loop: program director approves re-baselining + any MoD-facing commitment.
**Automation:** Medium-High. **Complexity:** Medium.
**ROI:** 3-9 months; high. **Scores:** market 7, pain 8, urgency 7, feasibility 7, revenue 7.
**TAM/SAM/SOM:** TAM ₹500-900 Cr [estimate]; SAM ₹300 Cr; SOM ₹40 Cr.
**Competition:** Primavera, MS Project, EcoSys — schedule tools, not agentic risk sentinels. Gap = predictive, narrative, MoD-review-aware.

### OPP-10 — Defence Finance, Audit & CAG-Readiness Agent
**Problem:** DPSUs + defence contractors face cost-audit (CAS-4/costing for nomination contracts), CAG scrutiny, GST on defence supplies, milestone-payment reconciliation, and IFC documentation. Manual, audit-season fire-drills.
**Cost of inaction:** CAG observations + cost-audit disallowances on a large DPSU run ₹10s of Cr; delayed milestone-payment claims tie up working capital [estimate].
**Agentic solution:** (a) Cost-sheet builder (CAS-4 for nomination/single-vendor contracts), (b) Milestone-billing reconciler (contract vs delivered vs invoiced), (c) GST-classification agent (defence exemptions/rates), (d) CAG-query-prep agent (assembles evidence packs against audit observations), (e) IFC/control-testing agent. Human-in-loop: CFO/cost-auditor signs all filings.
**Automation:** High. **Complexity:** Medium.
**ROI:** 3-9 months; medium-high. **Scores:** market 6, pain 7, urgency 6, feasibility 8, revenue 6.
**TAM/SAM/SOM:** TAM ₹300-600 Cr [estimate]; SAM ₹200 Cr; SOM ₹25 Cr.
**Competition:** Big-4 cost-audit, SAP/Tally + Excel. Gap = defence-costing-aware agentic finance layer.

### OPP-11 — MRO Work-Scoping, Turnaround & AOG Orchestration Agent
**Problem:** India outsources ~80% of MRO; engine work is 50-55% of MRO value; turnaround times long; spares non-availability + custom-duty regime discourage local stocking → frequent groundings. New depots (GE F404 for Tejas, GMR Hyderabad defence hangar by Mar 2026) need scoping/throughput intelligence. (Source: Aircraft maintenance in India / Wikipedia + TheCore, 2026, https://www.thecore.in/business/aircraft-maintenance-india-mro-adani-843093)
**Cost of inaction:** Each extra day of TAT per aircraft is lost availability + hangar cost; outsourcing premium + FX on 80% of work is a structural margin leak [estimate].
**Agentic solution:** (a) Induction work-scoping agent (reads inspection findings → drafts work package + man-hour estimate), (b) Parts-availability checker + AOG-procurement drafter, (c) Hangar-slot/throughput optimizer, (d) Customs/duty-classification agent for imported spares, (e) Quality-records/return-to-service pack assembler. Human-in-loop: licensed AME signs work package + RTS.
**Automation:** High. **Complexity:** High (airworthiness).
**ROI:** 6-12 months; high. **Scores:** market 7, pain 8, urgency 7, feasibility 6, revenue 7.
**TAM/SAM/SOM:** TAM ₹600-1,000 Cr (MRO software in India, growing as domestic MRO scales) [estimate]; SAM ₹350 Cr; SOM ₹45 Cr.
**Competition:** IFS, Ramco Aviation (Indian!), Swiss-AS AMOS. Gap = agentic work-scoping + AOG auto-drafting; Ramco is the incumbent to partner-with-or-displace.

### OPP-12 — Executive Decision-Support & Geopolitical / Defence-Market Intelligence Agent
**Problem:** Defence leadership must track DAP/policy changes (draft DAP 2026), competitor order wins, export-market openings (80+ countries), geopolitical shifts affecting supply chains (Russia spares risk), and DPSU/private competitive moves — across fragmented sources, slowly.
**Cost of inaction:** A missed policy window or export-market opening is opportunity cost in the ₹100s of Cr on a single deal [estimate]; slow board reaction to supply-chain shocks (e.g., Russian-origin spares) prolongs groundings.
**Agentic solution:** (a) Policy-watch agent (DAP/MoD/DGFT/DDP notifications), (b) Competitor-intelligence agent (order wins, JVs, foreign-OEM India moves), (c) Export-market-opportunity scout (country demand + India-eligibility), (d) Supply-chain-risk monitor (geopolitical + OEM-health signals), (e) Board-brief synthesizer. Human-in-loop: strategy head curates before board.
**Automation:** Medium-High (research/synthesis). **Complexity:** Medium.
**ROI:** 3-6 months; medium-high. **Scores:** market 7, pain 6, urgency 6, feasibility 8, revenue 7.
**TAM/SAM/SOM:** TAM ₹300-600 Cr (defence market/strategy intelligence) [estimate]; SAM ₹200 Cr; SOM ₹30 Cr.
**Competition:** Janes, GlobalData, Mordor/Nexdigm reports (static). Gap = live, agentic, India-DAP-aware exec intelligence.

---

## 3. Cross-Cutting Notes

- **Sovereignty / air-gap:** Most of these must run on-prem or on India-sovereign cloud (MeitY-empanelled, possibly DRDO-cleared stacks). This is a moat against US SaaS incumbents and a reason Indian builders can win.
- **Human-in-the-loop is non-negotiable** for every filing, indent, RTS, and any kinetic-adjacent output. Position as "agentic assistant, human authority," never autonomous decisioning.
- **Avoid the kill chain.** Targeting/weapons-release autonomy is doctrinally and reputationally radioactive (ORF: meaningful human control). Stay in the enterprise/business layer.
- **Best wedge for a startup:** OPP-2 (offset), OPP-3 (bid intelligence), OPP-4 (SCOMET) — pure software, document-heavy, fast ROI, weak/manual incumbents, no airworthiness sign-off blocker. OPP-1/OPP-11 are higher-value but gated by data access + airworthiness.
- **Best wedge for selling INTO a DPSU/prime:** OPP-5 (supplier QMS), OPP-9 (schedule sentinel), OPP-7 (knowledge capture) — internal-efficiency plays that don't need MoD-facing certification.

## 4. Counter-View (Steel-man)

Defence is the hardest enterprise-AI buyer in India: procurement cycles are 12-36 months, security clearances gate vendor access, air-gap kills cloud-LLM economics, and DPSUs are risk-averse with thin software budgets. A startup could build the perfect offset agent and still wait two years for a single PSU PO. Foreign OEMs may prefer their HQ's global compliance tools over an Indian point-solution. And any AI error in a SCOMET/airworthiness context carries outsized liability. The realistic 3-12 month ROI claims hold mainly for the *software-only, document-heavy* opportunities (2,3,4,10,12) sold to *private primes and foreign-OEM India arms* — the DPSU and airworthiness-gated plays (1,6,11) are more like 18-36 month sales with high stickiness once landed.

## 5. Open Questions

1. What is the actual on-prem/air-gap requirement per buyer tier — can a MeitY-cloud deployment satisfy DPSU security, or is true air-gap mandatory (changes unit economics dramatically)?
2. Draft DAP 2026 specifics — does it change offset thresholds or indigenous-content formulas in ways that reshape OPP-2/OPP-8?
3. Where does Ramco Aviation (Indian MRO-software incumbent) already have agentic roadmap — partner vs compete on OPP-11?

---

> Draft research note for review. Cited where possible; [estimate] elsewhere. Not investment advice.

### Sources
- Mordor Intelligence — India Defense Market, 2026 — https://www.mordorintelligence.com/industry-reports/india-defense-market
- Khan Global Studies / PIB — Defence Production ₹1.78L Cr FY25-26, 2026 — https://currentaffairs.khanglobalstudies.com/defence-production-hits-record-%E2%82%B91-78-lakh-crore-in-fy-2025-26/
- Vision IAS / MoD — Defence Exports ₹38,424 Cr, 2026 — https://visionias.in/current-affairs/news-today/2026-04-03/security/indias-defence-exports-reached-an-all-time-high-of-rs-38424-crore-in-fy-2025-26-ministry-of-defence
- IBEF — Defence Manufacturing, 2026 — https://www.ibef.org/industry/defence-manufacturing
- DefenceXP — IAF serviceability, 2026 — https://www.defencexp.com/why-only-60-of-indias-fighter-jets-are-ready-for-war/
- TheCore — India MRO hurdles, 2026 — https://www.thecore.in/business/aircraft-maintenance-india-mro-adani-843093
- Khanna & Associates — Defence Offset Compliance 2026 — https://khannaandassociates.com/blog/defence-offset-policies-india-2026-compliance-guide/
- ThePrint — Offset contracts in shambles — https://theprint.in/opinion/brahmastra/indias-defence-offset-contracts-are-in-shambles-need-a-revamp/944531/
- Minaions — Defence tenders DRDO/MES/OFB — https://minaions.com/blog/defence-tenders-in-india-drdo-mes-ofb-and-how-private-companies-can-participate
- IndiaFilings / MEA — SCOMET export, 2026 — https://www.indiafilings.com/learn/export-of-scomet-items
- GIC — AS9100 in Indian defence, 2026 — https://getisocertificate.com/as9100-certification-defence-industry-india/
- Plexus / Altium — Defence obsolescence & workforce cliff, 2026 — https://www.plexus.com/blog/defense-obsolescence-management/
- NextIAS — India indigenous AI in defence, 2026 — https://www.nextias.com/ca/current-affairs/11-05-2026/india-indigenous-ai-defence
- Inc42 — Tonbo Imaging defence-tech, 2026 — https://inc42.com/startups/uri-to-sindoor-how-tonbo-imaging-helped-forces-with-warfront-intel/
- ORF — Agentic AI & meaningful human control — https://www.orfonline.org/expert-speak/agentic-ai-and-india-s-nuclear-security-threat-opportunity-and-doctrine
