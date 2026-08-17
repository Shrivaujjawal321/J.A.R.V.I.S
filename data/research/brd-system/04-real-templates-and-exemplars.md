# Research Brief: What Real, High-Quality BRDs Actually Look Like (2025-2026)

**Purpose:** Ground-truth reference for building a BRD generator. This is not "how to write a BRD" advice — it is concrete section lists, real quoted fragments, and calibrated example prose so the generator's output can be checked against a real quality bar.

**Note on exemplar text below:** Real, complete corporate BRDs are almost never published publicly (they contain commercially sensitive scope/cost data). What *is* publicly available: (a) blank templates from consulting/training sites, universities, and government procurement bodies, with real section structures and instructional text, and (b) partial worked examples from BA training blogs, some with genuinely verbatim excerpt text (quoted and cited below). Where I had a real verbatim fragment, it is quoted directly and cited. Where no public real example existed for a required section (most of the "hardest sections" list — full stakeholder RACI tables, complete risk registers, full success-metrics tables, full acceptance-criteria blocks, full business cases are not published anywhere I could find, verified across 20+ searches), I constructed **one continuous, professional-quality composite exemplar** (a fictional bank loan-origination project, "Meridian Retail Bank — Consumer LOS Replacement") calibrated directly to the real templates' structure and the real quoted fragments' register. **These composite passages are explicitly flagged `[COMPOSITE EXEMPLAR — not a real company]`** so they are never mistaken for a leaked real document. This is the same technique BA training sites (businessanalyststoolkit.com, altexsoft.com) use — their "examples" are also constructed, not real client deliverables.

---

## 1. Real templates found, with exact section headings

### 1.1 Stanford University IT — Business Requirements Document Template
Source: [Stanford UIT BRD Template (.doc)](https://uit.stanford.edu/sites/default/files/2017/08/30/Business%20Requirements%20Document%20Template.doc)

This is a genuinely detailed, IEEE-SRS-influenced BRD template (unusually rigorous for a university). Section order:

1. **Introduction**
   1.1 Purpose of the Document
   1.2 Document Conventions, Terms, and Definitions
   1.3 Intended Audience and Reading Suggestions *(unusual — explicitly describes different reader personas: developers, project managers, testers, end users, and how each should read the doc differently)*
   1.4 Scope — split into **1.4.1 Project Scope** and **1.4.2 Business Requirement Document Scope** *(unusual — separates "what the project covers" from "what this document covers," which matters when a BRD is one artifact among several, e.g., also a Project Charter and an SRS)*
   1.5 References
2. **Overall Description**
   2.1 Project Overview
   2.2 Product Features
   2.3 User Classes and Characteristics
   2.4 Operating Environment
   2.5 Design and Implementation Constraints
   2.6 User Documentation
   2.7 Assumptions, Dependencies, and Risks
3. **System Features** — repeated block per feature: Description → Stimulus/Response Sequences → Functional Requirements → Use Cases
4. **External Interface Requirements** — User Interface / Hardware / Software / Communications Interfaces / Reporting Requirements
5. **Other Nonfunctional Requirements** — Performance / Security / Data / Software Quality Attributes
6. **Other Requirements**
7. **Campus Readiness and Training** *(unusual — most BRD templates skip organizational change management; Stanford bakes it in as a first-class section)*

Appendices: A) Glossary, B) Analysis Models, C) Issues List, D) Screenshots/Mock-ups/Live Links, E) Test Scenarios.

Notable instruction embedded in the template: authors are told they can only finish "Product Features" *after* Section 3 is drafted — i.e., the template enforces bottom-up validation (write detailed features first, then summarize), a discipline most generators skip by writing top-down and never reconciling.

### 1.2 British Columbia Government (Ministry of Education, K-12 sector) — BRD Template
Source: [BC Gov BRD Template (.doc)](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/services-policies-for-government/information-technology/standards/education-k-12-sector/dt_brd.doc)

Government procurement templates tend to be terser than university ones and push almost everything into structured actor/use-case tables rather than prose. Notable for including an explicit **"actor profile"** specification block (who are the system's actors, what are their goals) as a first-class section before requirements — closer to a use-case-driven RUP style than a pure BABOK BRD. [unverified — fetch of full doc content did not fully resolve; treat section order as approximate from search indexing, verify before hard-coding into generator]

### 1.3 IIBA Free BRD Template (Howard Podeswa)
Source: [IIBA free BRD template download](https://go.iiba.org/free-download-business-requirement-document-BRD-template)

The template is built and endorsed by IIBA using BABOK-aligned structure. Per IIBA's own summary, it captures: project objectives, scope, business requirements, constraints, assumptions, and references — i.e., a leaner document than Stanford's, closer to what a business-facing (non-technical) BRD should be. IIBA's position (per their [Requirements Documenting blog](https://www.iiba.org/business-analysis-blogs/requirements-documenting--the-foundation-of-a-projects-success/)) is that a BRD documents the "why" — goals, objectives, outcomes — and should NOT contain solution/system detail; that belongs in a separate FRD/SRS. This is the single most important structural distinction IIBA enforces and the one generic web templates blur.

### 1.4 Smartsheet — Agile BRD Template + Software Development BRD Template
Source: [Smartsheet Business Requirement Document Templates](https://www.smartsheet.com/content/business-requirement-document-templates)

Two distinct templates on the same page, for two different audiences:

**Agile BRD:** Project Scope → Current Process → Proposed Process → Cost Benefit Analysis → Resources → Schedule/Timeline/Milestones → Assumptions. Notably **current-process/proposed-process (as-is/to-be) are core sections**, not optional appendices — Smartsheet treats them as load-bearing.

**Software Development BRD (IEEE-flavored):** Introduction (Purpose, References, Scope, Definitions/Acronyms, Document Conventions) → Requirements (User Interface, Hardware Interfaces, Functional Requirements, Performance Requirements, Security, Usability). This one is really an SRS wearing a BRD label — a common naming confusion in the wild that a generator needs to disambiguate by asking the user "business-facing or technical-facing?"

Also relevant from the same publisher: [Free Stakeholder Analysis Templates](https://www.smartsheet.com/free-stakeholder-analysis-templates), [Free Risk Register Templates](https://www.smartsheet.com/risk-register-templates), [Free Document Control Templates](https://www.smartsheet.com/content/document-control-templates) — these are the sub-artifacts a serious BRD embeds as tables/appendices rather than writing from scratch.

### 1.5 Asana — Business Requirements Document Template
Source: [Asana BRD Template + Free PDF [2026]](https://asana.com/resources/business-requirements-document-template), [Asana Simple BRD Template](https://asana.com/templates/business-requirements-document)

Section order (modern SaaS-vendor style, shorter and more "product manager" flavored than IIBA/Stanford): Executive Summary → Project Scope (with explicit in/out framing to "prevent scope creep") → Measurable Objectives (Asana explicitly instructs "Add measurable objectives, like reducing processing time by 20%... Objectives help track ROI and success metrics") → Business Requirements → Business Justification (cost-benefit, risks, ties to org goals). Asana's own copy stresses the doc should be **"detailed yet concise... give readers the information they need without unnecessary length"** — i.e., they explicitly warn against padding, which is the single most common generator failure mode.

### 1.6 Government / regulated-industry example — CAISO Business Requirements Specification
Source: [CAISO BRS — Energy Storage Enhancements Track 1 (PDF)](https://www.caiso.com/documents/businessrequirementsspecificationenergystorageenhancementstrack1.pdf)

A real, currently-published 28-page regulatory BRD from the California ISO. [unverified in detail — PDF text layer could not be extracted by the fetch tool, so exact section text is not confirmed; flagging as a genuine real-world artifact worth a human's manual read since it is a live example of a heavily regulated, multi-stakeholder BRS with formal numbered requirements used in actual grid-market rule changes]. Worth noting for the generator: utility/regulatory BRDs use "BRS" (Business Requirements Specification) as the label, and are structured around formal rule changes with cross-references to tariff clauses — a domain-specific pattern (regulatory citation linking) that generic commercial BRDs don't have.

### 1.7 University templates catalogued but not directly fetched (indexed via search, treat details as [unverified] pending direct read)
- **NYU** — advanced template with version tracking charts, spreadsheets, diagrams, and highlighted placeholder text conventions.
- **San Francisco State University** — compact 3-page template using spreadsheet tabs per section (unusual delivery format — Excel workbook, not Word doc).
- **York University** — 13-page IT-project BRD template.

### 1.8 Training-site worked examples (constructed, not real client docs, but useful for tone calibration)
Source: [businessanalyststoolkit.com — BRD Example Walk-Through](https://businessanalyststoolkit.com/business-requirements-document-example/) and [BRD Sample](https://businessanalyststoolkit.com/business-requirements-document-sample/)

Section list used across their two example docs: Document History and Approvals → Introduction → Organisational Context → System Overview → Implementation Overview → Requirements Conventions → Business Requirements → System Requirements → Definitions. Real quoted fragments from this source (verbatim):

- Problem framing example: *"physical handling of paperwork creating service bottlenecks, manual coordination of approvals consuming significant HR staff time, and double data entry between the HR system and payroll."*
- Requirement example: *"REQ01 – When a new employee record is submitted and approved, automatically generate a notification to the ICT Services team."*
- Scope table pattern (Phase / Process Group / Business Processes Included) — a **phased-scope table**, distinct from a flat in/out list; useful for multi-release BRDs.
- Requirements traceability table pattern (payroll consolidation example):

| Req ID | Requirement | Business Objective | Priority | Source |
|---|---|---|---|---|
| BR-001 | "The solution shall provide a single employee record" | Eliminate duplicate employee data | Must Have | Payroll Operations |
| BR-004 | "The solution shall provide self-service leave management" | Reduce payroll team burden | Should Have | HR, Employee Services |

- A genuinely instructive real anecdote about problem-statement drafting: an initial draft blamed a department for "duplicate processes and inconsistent data"; a stakeholder objected, and the author reframed it around **"current state and the cost of inaction"** instead of blame — this is the single best practitioner insight found on *how* to write a CFO-safe problem statement (neutral framing, cost-of-inaction, not "Team X's fault").
- Real anecdote on assumptions: the assumption "all business units operating on the same enterprise network" was wrong for remote sites and caused infrastructure cost overruns discovered weeks into design — a concrete illustration of why an Assumptions Register needs an owner + validation step, not just a list.

### 1.9 altexsoft.com — How to Write a BRD
Source: [altexsoft.com BRD guide](https://www.altexsoft.com/blog/business-requirements-document/)

Section list: Executive summary → Project objectives → Project scope → Stakeholders → SWOT analysis *(unusual — most BRD templates skip SWOT; altexsoft includes it, useful when the BRD is also functioning as a lightweight business case)* → Financial statements → Functional requirements → Schedule and deadlines → Cost-benefit analysis. Real quoted SMART-objective fragments (verbatim, from an e-commerce redesign example):
- *"Launch 3 ad campaigns to promote a redesigned eCommerce website within a month."*
- *"Gain min 100,000 unique visitors to the website by the end of Q4 2021."*
- *"Increase average time on website from 1.2 minutes to 3 minutes by the end of Q4 2021."*
- *"Decrease cart abandonment by 40 percent by the end of Q4 2021."*

Scope-table pattern: bullet, not table — "In scope: Redesign the user flow on the landing page / Redesign product pages. Out of scope: shapes and colors of click buttons / platform background theme." Note this source does **not** use MoSCoW or formal requirement IDs — a gap versus the IIBA/Stanford lineage, illustrating that vendor-blog BRDs are consistently weaker on traceability discipline than institutional templates.

---

## 2. Concrete excerpts for the hardest sections

Everything below is `[COMPOSITE EXEMPLAR]` — a single continuous fictional scenario ("Meridian Retail Bank, consumer Loan Origination System replacement") written at the quality bar the sources above describe, so all twelve pieces read as one coherent, professional BRD rather than disconnected snippets. Numbers, names, and the company are invented; the *structure and prose discipline* is what should be replicated by a generator.

### 2.1 Business Objective (SMART)

> **Objective 1 — Cycle-time reduction.** Reduce average consumer-loan origination cycle time (application-submitted to funds-disbursed) from 9.4 business days to 3.0 business days by the end of Q2 FY27, as measured monthly by the LOS pipeline-stage timestamp report, without relaxing the current credit-risk score threshold (minimum 640 FICO).
>
> **Objective 2 — Manual-touch reduction.** Reduce manual underwriter data-entry touches per application from an average of 14 to no more than 4 by Q3 FY27, measured via underwriter time-and-motion sampling (20 applications/month, sampled by Internal Audit).
>
> **Objective 3 — Compliance exception reduction.** Reduce Regulation B adverse-action-notice timeliness exceptions from a current baseline of 6.2% of declined applications to below 1.0% by Q4 FY27, measured via the monthly Compliance exception report.

*Why this is SMART:* each has a number, a baseline, a target, a measurement method, an owner-implied data source, and a date — exactly the discipline altexsoft's examples show ("Increase average time on website from 1.2 minutes to 3 minutes by the end of Q4 2021") but applied to a regulated-industry context where a naive metric (speed) could conflict with a constraint (credit risk), which is why Objective 1 explicitly states the non-negotiable constraint inline. This is the pattern a CFO/Risk officer actually looks for: **the objective proves it isn't going to trade one metric for a worse hidden one.**

### 2.2 Problem Statement a CFO would accept

> Meridian's consumer Loan Origination System (LOS), implemented in 2014, requires underwriters to re-key applicant data across four disconnected systems (core banking, credit bureau interface, decisioning engine, and document management), averaging 14 manual touches per application. This drives an average origination cycle of 9.4 business days, versus a market median of 2.1 days reported by three fintech competitors now active in Meridian's footprint (Competitor benchmarking study, Q1 FY26, Retail Banking Strategy team).
>
> The cost of inaction is threefold. First, application abandonment: 22% of applicants who start a Meridian loan application do not complete it, and post-application exit surveys (n=340, Q4 FY25) cite "too slow / went elsewhere" in 61% of abandonments — an estimated $4.1M in annual foregone net interest income at current approval rates. Second, compliance exposure: manual re-keying has produced a 6.2% Regulation B adverse-action-notice timeliness exception rate over the trailing twelve months, a rate the Compliance function has flagged as elevated risk ahead of the FY27 regulatory exam cycle. Third, operating cost: underwriting labor allocated to manual data reconciliation is estimated at 3.8 FTE-equivalents annually ($430K fully loaded), work that is redundant with data already captured at application intake.
>
> This document defines the business requirements for replacing the manual-touch data flow in the LOS; it does not prescribe the replacement system's architecture or vendor.

*Why this works:* no blame language, no solution language ("we need to buy X"), every claim has a number and an attributable source, and it closes with an explicit statement of what the document is *not* deciding — directly reflecting the businessanalyststoolkit anecdote about reframing a problem statement away from blame and toward "current state and cost of inaction."

### 2.3 In-Scope / Out-of-Scope Table

| # | In Scope | # | Out of Scope | Rationale for exclusion |
|---|---|---|---|---|
| IS-1 | Consumer unsecured personal loans ($1K–$50K) origination workflow | OS-1 | Auto loan and mortgage origination workflows | Separate LOS platforms with independent 2027/2028 replacement roadmap; combining scope would delay Phase 1 by an estimated 5 months |
| IS-2 | Application intake, document capture, credit-bureau pull, automated decisioning integration, funding hand-off to core banking | OS-2 | Core banking system replacement or upgrade | Core banking is a separate, already-funded FY28 initiative (Project Anchor); this project integrates to it via existing API, does not modify it |
| IS-3 | Underwriter workbench UI for manual-review exception queue | OS-3 | Collections and servicing workflows post-disbursement | Post-funding lifecycle is owned by the Servicing platform team; a separate BRD governs that scope |
| IS-4 | Regulation B adverse-action-notice generation and timestamping | OS-4 | Marketing/lead-generation front-end (loan application landing pages) | Marketing site is managed by Digital Channels team on an independent CMS; only the API contract between the site and LOS is in scope (see IS-2) |
| IS-5 | Migration of 24 months of in-flight and historical application data from legacy LOS | OS-5 | Branch-network point-of-sale hardware refresh | Not a dependency of this initiative; branch hardware refresh is on a 5-year independent cycle |

*Why this matters:* the out-of-scope column always states the **reason**, not just the exclusion — this is what a generator must never skip, because an unexplained exclusion invites stakeholders to re-litigate scope later ("why not mortgages too?"). Note this mirrors altexsoft's flat bullet pattern but upgrades it to a table with a rationale column, and mirrors businessanalyststoolkit's phased-scope table concept by making the "why" explicit per line.

### 2.4 Stakeholder Analysis Table with RACI

| Stakeholder | Role | Interest | Influence | RACI (on Business Requirements sign-off) | RACI (on UAT sign-off) |
|---|---|---|---|---|---|
| Priya Nandakumar, SVP Retail Lending | Business Sponsor | High — owns P&L for consumer lending | High | A | C |
| David Osei, Chief Risk Officer | Risk oversight | High — credit-policy integrity | High | C | A |
| Meredith Voss, Head of Compliance | Regulatory oversight | High — Reg B / fair-lending exposure | High | C | C |
| Tom Achebe, VP Underwriting Operations | Process owner | High — daily workflow impact | Medium | R | R |
| Lena Fisk, Director IT Applications | Delivery accountable | High — build/integration ownership | High | R | A |
| Underwriting staff (12 FTEs) | End users | High — direct workflow change | Low | I | R (participants) |
| Internal Audit | Control validation | Medium — SOX control mapping | Medium | I | I |
| Branch Network Operations | Downstream consumer | Low — indirect, faster turnaround benefits them | Low | I | I |

*Convention notes:* one Accountable per row max (RACI discipline — Meridian's RACI has exactly one "A" per column, never two); "R (participants)" for a group role is a legitimate shorthand for a whole department acting as one Responsible party. This table format — role + interest + influence + two separate RACI columns for two separate sign-off gates — is more realistic than a single flat RACI, because most real BRDs have multiple sign-off moments (requirements sign-off vs. UAT sign-off vs. go-live sign-off) and stakeholders' RACI role can change between them (e.g., Priya is Accountable for requirements but only Consulted for UAT because Lena owns delivery quality at that gate).

### 2.5 As-Is vs To-Be Process (with numbering/notation convention)

**Notation used:** numbered steps grouped by swimlane (actor), cross-referenced to a BPMN diagram maintained as Appendix B. Steps are numbered `<Phase>.<Step>` per swimlane so a reviewer can jump straight from prose to diagram. This mirrors Stanford's "Analysis Models" appendix convention and the Smartsheet Agile BRD's Current Process/Proposed Process section pairing.

**AS-IS: Application Intake to Decision (Swimlane: Applicant / Branch Staff / Underwriter / Credit Bureau System)**

1.1 (Applicant) Submits paper or PDF application at branch or via email.
1.2 (Branch Staff) Manually keys applicant data into core banking system (Step 1.2a) *and* separately into legacy LOS (Step 1.2b) — duplicate entry point #1.
1.3 (Branch Staff) Manually initiates credit-bureau pull via a separate bureau portal; downloads PDF report.
1.4 (Underwriter) Re-keys relevant bureau data points into decisioning spreadsheet — duplicate entry point #2.
1.5 (Underwriter) Manually applies credit policy rules using a static decision-tree job aid (last updated 2019); flags exceptions for manager review.
1.6 (Underwriter) If approved, re-keys approved terms into core banking for disbursement — duplicate entry point #3.
1.7 (Branch Staff) Manually generates adverse-action notice in Word template if declined; timestamp recorded manually in a shared spreadsheet — root cause of the 6.2% Reg B timeliness exception rate (see §2.2).

**TO-BE: Application Intake to Decision (Swimlane: Applicant / Digital Channel / New LOS / Underwriter)**

1.1 (Applicant) Submits application via digital channel or assisted branch entry; data captured once at source.
1.2 (New LOS) Auto-pulls credit bureau report via API (no manual portal step); normalizes fields into a single applicant record.
1.3 (New LOS) Applies configurable decision-engine rules (same credit-policy thresholds as today, config-managed by Risk, not hardcoded); auto-approves or auto-declines applications meeting deterministic criteria; routes ambiguous cases to Underwriter exception queue.
1.4 (Underwriter) Reviews only exception-queue cases (target: ≤25% of volume) in a single workbench UI; no re-keying — data pre-populated from Step 1.1/1.2.
1.5 (New LOS) On approval, pushes disbursement instruction to core banking via existing API (no manual re-entry).
1.6 (New LOS) On decline, auto-generates and auto-timestamps adverse-action notice at time of decision — eliminates the manual timestamp gap that drives Reg B exceptions.

*Why this format:* the as-is steps each name the specific duplicate-entry point and tie it back numerically to the problem statement's claims (3.8 FTE manual reconciliation, 6.2% Reg B exceptions) — a BRD that just describes "the current process is manual and slow" without this traceability reads as generic. The to-be steps mirror the as-is numbering 1:1 so a reviewer can diff them side-by-side, which is the actual working convention senior BAs use (confirmed via swimlane-diagram sourcing above — BPMN/swimlane is the standard notation, decision points as diamonds, numbered steps per lane).

### 2.6 A Properly Written Numbered Business Requirement (MoSCoW + traceability)

> **BR-014** | **Priority: Must Have** | **Traces to: Objective 2 (Manual-touch reduction), Objective 3 (Compliance exception reduction)** | **Source: Underwriting Operations workshop, 2026-03-11; confirmed by Tom Achebe**
>
> The solution shall auto-populate the underwriter exception-queue workbench with applicant data, credit-bureau results, and system-recommended decision rationale at the time an application enters the queue, such that an underwriter can complete review without re-entering any data field already captured in Steps 1.1–1.3 of the To-Be process (§2.5).
>
> *Acceptance reference: AC-BR014 (see §2.11). Not in scope: workbench UI visual design (governed by separate UX specification, ref DES-014).*

*Why this is well-formed:* it has a unique ID, an explicit MoSCoW priority, two traceability links back to numbered business objectives (not vague "supports the project goals"), a documented source (workshop + named confirmer — auditable provenance), a testable "shall" statement scoped to a specific process step reference, and an explicit line clarifying what it does *not* cover (preventing solution/design creep into a business requirement). This is the single most commonly missing discipline in generic web templates — altexsoft's and Asana's public examples do NOT show traceability IDs or sourcing; only the institutional templates (Stanford, IIBA/BABOK lineage) enforce it.

### 2.7 Quantified Non-Functional Requirement set

| NFR ID | Category | Requirement | Target | Measurement Method |
|---|---|---|---|---|
| NFR-01 | Performance | Decision-engine response time for auto-decisioned applications | p95 < 3 seconds from data-complete to decision returned | APM tooling (Datadog), measured under production load |
| NFR-02 | Availability | LOS platform uptime during business hours (7am–9pm ET, Mon–Sat) | ≥ 99.9% (≤ 43 min downtime/month during business hours) | Uptime monitoring, monthly SLA report |
| NFR-03 | Scalability | Concurrent underwriter sessions supported without degradation | 150 concurrent sessions at p95 < 3s response (NFR-01 held) | Load test prior to go-live; quarterly re-test |
| NFR-04 | Security | Applicant PII encryption | AES-256 at rest, TLS 1.2+ in transit; field-level encryption for SSN | Annual penetration test + SOC 2 Type II audit |
| NFR-05 | Security | Access control | Role-based access aligned to RACI (§2.4); underwriters cannot view applications routed to auto-decision; full audit trail of every field view/edit, retained 7 years | Quarterly access-review audit by Internal Audit |
| NFR-06 | Compliance | Adverse-action notice generation | 100% of declines generate a timestamped notice within 3 business days per Reg B §1002.9(a)(1) | Monthly Compliance exception report (target: 0% exceptions, vs. 6.2% baseline) |
| NFR-07 | Data Retention | Application data retention | Retain full application record (including declined) for 25 months per Reg B; auto-purge PII fields beyond regulatory retention window unless litigation hold | Automated retention job, verified in quarterly data-governance audit |
| NFR-08 | Usability | Underwriter task completion | New underwriters (< 30 days tenure) complete standard exception review in ≤ 6 minutes average, without dedicated support | UAT usability testing, n≥8 underwriters, System Usability Scale ≥ 80 |

*Why this works:* every NFR has a number, not an adjective ("fast," "secure," "reliable" never appear unqualified), and a measurement method that is auditable independently of the vendor's own claims — matching the pattern found in research (p95 response times, 99.9%/99.95% uptime figures, AES-256/TLS 1.2+ as the concrete security baseline actually used in 2025-2026 NFR writing).

### 2.8 Assumptions Register (owner + validation date + impact-if-wrong)

| # | Assumption | Owner | Validation Date | Impact if Wrong |
|---|---|---|---|---|
| A-01 | The existing core-banking disbursement API (v3.2) will remain stable and unchanged through go-live (no breaking changes from Project Anchor, the parallel core-banking initiative) | Lena Fisk (IT Applications) | 2026-04-15 (confirm with Project Anchor lead) | High — a breaking API change would require rework of the disbursement integration (Step 1.5, To-Be); estimated 6-week delay |
| A-02 | Credit-bureau vendor (Experian) can support real-time API pull for 100% of applicant volume at current contracted rate; no renegotiation needed | Tom Achebe (Underwriting Ops) | 2026-04-30 | Medium — if API pricing requires renegotiation, could add $180K/year to run cost; would not block go-live but would affect the business case in §2.12 |
| A-03 | Underwriting staff headcount remains at 12 FTE through go-live; no attrition-driven training gap | Tom Achebe (Underwriting Ops) | Ongoing — reviewed monthly at steering committee | Medium — unplanned attrition during UAT/training window could delay the manual-touch objective (Objective 2) by a quarter |
| A-04 | Regulation B adverse-action-notice content requirements do not change materially between now and go-live | Meredith Voss (Compliance) | 2026-06-01 (re-confirm 90 days pre-go-live) | High — a CFPB rule change would require notice-template rework and re-validation of NFR-06; treated as a standing risk (see R-04, §2.9) |

*Why this matters:* every assumption is falsifiable (someone can go check it), has a named owner (not "IT" or "the business" — a real name), a date by which it must be confirmed (not "TBD"), and states impact in terms that connect back to the objectives/NFRs it would break — directly following the real-world lesson from the businessanalyststoolkit anecdote (the wrong "same enterprise network" assumption that caused a cost overrun because nobody had assigned an owner or a validation deadline to it).

### 2.9 Risk Register (probability/impact/mitigation/owner)

| Risk ID | Description | Probability | Impact | Score (P×I, 1-5 scale) | Mitigation | Owner |
|---|---|---|---|---|---|---|
| R-01 | Credit-bureau API integration slips past planned date due to Experian's own release schedule (outside Meridian's control) | 3 | 4 | 12 (High) | Secure written commitment + fallback SLA from Experian by contract amendment; build batch-pull fallback mode as contingency, not primary path | Lena Fisk |
| R-02 | Underwriters resist exception-queue workflow, continue shadow-using legacy spreadsheet decision aid | 3 | 3 | 9 (Medium) | Change-management plan with Tom Achebe as workflow champion; legacy LOS access revoked on go-live (no parallel-run beyond 2 weeks) | Tom Achebe |
| R-03 | Auto-decision engine's approval rate diverges materially from current manual approval rate during parallel testing, indicating miscalibrated rules | 2 | 5 | 10 (High) | 90-day parallel-run with side-by-side comparison before auto-decisioning goes live for >25% of volume; Risk sign-off gate before threshold increase | David Osei |
| R-04 | CFPB issues a Reg B rule change during the build window affecting adverse-action notice content (linked to Assumption A-04) | 2 | 4 | 8 (Medium) | Compliance to monitor CFPB rulemaking calendar monthly; notice template built as a configurable, not hardcoded, component specifically to absorb this risk cheaply | Meredith Voss |
| R-05 | Data migration of 24 months of in-flight applications introduces record-matching errors (duplicate or orphaned applicant records) | 3 | 3 | 9 (Medium) | Dry-run migration in staging with full reconciliation report; Internal Audit sign-off on match-rate ≥ 99.5% before production migration | Lena Fisk |

*Convention:* probability and impact each scored 1-5, multiplied for a priority score, and every mitigation is a specific action with an owner and — where possible — a mechanism that's cheap because it was designed in (e.g., R-04's "configurable not hardcoded" mitigation is far better than "we'll deal with it if it happens," which is the generic-BRD failure mode). Note the explicit two-way link between R-04 and A-04 — a mature BRD cross-references its own risk and assumption registers rather than treating them as disconnected boilerplate sections.

### 2.10 Success Metrics Table (baseline, target, method, date)

| Metric | Baseline | Target | Measurement Method | Measurement Date |
|---|---|---|---|---|
| Average origination cycle time | 9.4 business days | 3.0 business days | LOS pipeline-stage timestamp report, monthly average | Q2 FY27 (first measurement 30 days post-go-live, then monthly) |
| Manual underwriter touches per application | 14 | ≤ 4 | Time-and-motion sample, 20 applications/month, Internal Audit | Q3 FY27 |
| Reg B adverse-action timeliness exception rate | 6.2% | < 1.0% | Monthly Compliance exception report | Q4 FY27, sustained for 2 consecutive quarters |
| Application abandonment rate | 22% | 12% | Digital channel funnel analytics + branch intake log | Q3 FY27 |
| Underwriting labor cost allocated to manual reconciliation | 3.8 FTE-equivalent ($430K/yr) | ≤ 1.0 FTE-equivalent ($115K/yr) | Finance FTE-allocation model, reviewed with Underwriting Ops | Q4 FY27 |

*Why this works:* it is the direct closing of the loop opened in the Problem Statement (§2.2) and Objectives (§2.1) — every number quoted as a "cost of inaction" or "target" earlier reappears here with a measurement date. A BRD where the success-metrics table introduces *new* numbers not seen earlier in the document is a reliable tell of sloppy drafting (a stitched-together doc, not one built by someone holding the whole picture).

### 2.11 Acceptance Criteria (Given/When/Then + checklist form)

**Given/When/Then form (for BR-014, workbench auto-population):**

```
AC-BR014.1
  Given an application has been routed to the underwriter exception queue
  When the underwriter opens the application record
  Then all applicant data, credit-bureau results, and decision-engine
       rationale captured in Steps 1.1–1.3 are pre-populated and
       displayed without requiring manual re-entry

AC-BR014.2
  Given the underwriter modifies any pre-populated field during review
  When the modification is saved
  Then the system logs the original value, new value, underwriter ID,
       and timestamp to the audit trail (per NFR-05)

AC-BR014.3
  Given an application has incomplete data from Step 1.2 (e.g., bureau
       pull failure)
  When the application enters the exception queue
  Then the system flags the specific missing field(s) rather than
       presenting a blank/incomplete record
```

**Checklist form (for go-live readiness, business-level, mixing BR/NFR references):**

- [ ] BR-014 through BR-028 (workbench requirements) pass UAT with zero Critical/High defects open
- [ ] NFR-01 and NFR-03 performance targets confirmed under load test with production-representative data volume
- [ ] NFR-06 (Reg B notice generation) validated by Compliance on a sample of 50 declined test applications, 100% pass
- [ ] Parallel-run (R-03 mitigation) completed with auto-decision/manual-decision concordance ≥ 98% on a sample of 500 applications
- [ ] Legacy LOS data migration reconciliation (R-05 mitigation) shows ≥ 99.5% match rate, signed off by Internal Audit
- [ ] Underwriting staff (12 FTE) complete training with post-training SUS score ≥ 80 (NFR-08)
- [ ] Sign-off obtained from all "A" (Accountable) roles in the UAT RACI column (§2.4)

*Convention:* Given/When/Then is used at the individual-requirement level (testable, granular, maps 1:1 to a QA test case); the checklist form is used at the go-live/release level (cross-cutting, references multiple requirement IDs, ties to sign-off authority) — these are two different altitudes of acceptance criteria and a generator should produce both, not just one.

### 2.12 Cost-Benefit / Business Case Summary

> **Investment required:** $2.85M (build: $2.1M software/integration/vendor licensing over 14 months; change management and training: $340K; contingency 15%: $370K).
>
> **Annual run-rate cost:** New LOS platform licensing and support: $410K/year (vs. legacy LOS support cost of $265K/year — net run-rate increase of $145K/year).
>
> **Quantified annual benefits (steady-state, from Q4 FY27):**
> - Reduced application abandonment (10 percentage-point improvement, §2.10): **$1.9M/year** in retained net interest income
> - Underwriting labor reallocation (2.8 FTE-equivalent freed from manual reconciliation): **$315K/year**
> - Avoided Reg B compliance-exception remediation cost (based on FY25 remediation spend of $180K following the last exam finding): **$170K/year** avoided (conservative, net of residual risk)
>
> **Total quantified annual benefit:** $2.385M/year. **Net annual benefit after run-rate cost increase:** $2.24M/year.
>
> | Metric | Value |
> |---|---|
> | Total investment | $2.85M |
> | Payback period | 15.3 months from go-live |
> | 3-year net benefit | $6.87M |
> | 3-year ROI | 141% |
>
> **Unquantified benefits (not included in ROI above, noted for completeness):** improved competitive positioning against fintech lenders; reduced regulatory-exam risk profile ahead of FY27 exam cycle; improved employee experience for underwriting staff (attrition in Underwriting Operations has run 18% annually, above the bank's 11% average, and exit interviews cite "manual, repetitive work" as a factor).
>
> **Base / downside case:** if benefit realization is 30% lower than modeled (e.g., abandonment improvement is only 7 points, not 10) and costs run 10% over budget, payback extends to approximately 22 months — still within the 3-year evaluation horizon used by Meridian's Capital Committee.

*Why this works:* it separates investment from run-rate cost (a step almost every weak BRD skips — they show "cost" as a single lump sum and never disclose that the new system costs *more* to run than the old one, which a CFO will immediately ask about); it shows a downside case, not just the rosy base case; and it explicitly quarantines "unquantified benefits" instead of inflating the ROI number with soft claims — this transparency is exactly what research on cost-benefit templates flagged as best practice (build a base/optimistic/pessimistic scenario table, state NPV/ROI/payback together).

---

## 3. Formatting conventions actually used

**Tables vs. prose — the actual split found across every real/near-real template surveyed:**
- **Prose (paragraphs):** Executive Summary, Problem Statement/Business Context, Project Overview, As-Is/To-Be process narrative (paired with a table/diagram, not instead of one).
- **Tables:** Scope (in/out), Stakeholders/RACI, Requirements (with ID/priority/source/trace columns), NFRs, Assumptions, Risks, Success Metrics, Document Control/Version History, Cost-Benefit summary.
- **Hybrid (numbered list with structured sub-fields, not a full table):** individual Business Requirement write-ups (§2.6 pattern) and Acceptance Criteria (Given/When/Then blocks).

**Heading numbering:** every institutional template (Stanford, IIBA-lineage) uses decimal numbering (`1`, `1.1`, `1.1.1`) so requirements and NFRs can cross-reference sections precisely (e.g., "per NFR-06" or "Step 1.5, To-Be process"). Vendor-blog templates (Asana, altexsoft) tend to drop numbering in favor of plain H2/H3 headers — fine for short docs, but breaks down past ~15 pages because nothing can be cross-referenced unambiguously.

**Document control block:** every serious template opens (page 1 or 2, before the Executive Summary) with a control table:

| Field | Value |
|---|---|
| Document Title | Business Requirements Document — Consumer LOS Replacement |
| Document ID | BRD-LOS-2026-001 |
| Version | 1.3 |
| Status | Approved |
| Author | [Name], Business Analyst |
| Business Sponsor | Priya Nandakumar, SVP Retail Lending |
| Date Created | 2026-02-10 |
| Date Approved | 2026-04-22 |

Followed by a **Change Log / Revision History** table (Version, Date, Author, Description of Change, Approved By) and an **Approvals** table (Name, Role, Signature/Date) — per the [document-control template research](https://www.smartsheet.com/content/document-control-templates), the discipline is: every version bump must name who changed what and why, and every approver must be a named person with a date, never a role/title alone ("IT" is not an approver; "Lena Fisk, Director IT Applications, 2026-04-20" is).

**Typical total length by initiative size** (converged figures across multiple sources):
- **Small** (single department, low integration complexity): 5–10 pages
- **Medium** (cross-department, moderate integration, the Meridian LOS example above is roughly this size): 15–25 pages
- **Large** (enterprise, multi-system, regulatory exposure): 30–60+ pages, often split into a core BRD plus appendices (process models, data dictionaries, interface specs) that are separately versioned

The universal warning across sources: **length should track complexity, not effort-signaling.** Asana explicitly instructs "detailed yet concise... without unnecessary length." A generator that pads a small-scope request into a 40-page document is committing the single most common quality failure identified in research (see §5, §6).

---

## 4. MoSCoW and other prioritization schemes

**MoSCoW (Must/Should/Could/Won't have)** is the dominant scheme in real BRDs surveyed (used explicitly in the businessanalyststoolkit payroll example, and standard in DSDM/Agile Business Consortium literature). Recorded as a column in the requirements traceability table, one value per requirement, never a free-text priority description.

- **Must have:** the initiative fails/is not viable without it (legal, safety, or core-value requirements). Per [Agile Business Consortium](https://www.agilebusiness.org/resource/what-is-moscow-prioritization/), if a Must fails, the delivery date must move — Musts are not negotiable against schedule.
- **Should have:** important, has a workaround if descoped, but the workaround is painful.
- **Could have:** desirable, low impact if left out; frequently the first release-scope trim.
- **Won't have (this release):** the critical discipline point. Per [Stoneseed/Medium's MoSCoW piece](https://medium.com/@Stoneseed/moscow-prioritisation-must-have-should-have-could-have-wont-have-getting-it-right-from-the-start-8d9934d16a37) and the DSDM handbook, "Won't have" is **explicitly scoped and dated**, not silently dropped — it is a documented decision ("we are not doing X in this release, and here is why"), which is exactly what prevents scope-creep arguments six months later ("but I told you I needed this"). The DSDM framing is stronger still: at the start of a timebox, *most* candidate requirements default to Won't Have, and only what the team commits to gets promoted — inverting the naive assumption that everything starts as a Must and gets cut down.

**Alternative schemes found in the wild:**
- **High/Medium/Low** — common in government/procurement templates (BC gov, Maryland procurement) where MoSCoW's Agile connotation feels foreign to a waterfall RFP process; functionally similar but loses the "Won't have, documented" discipline unless explicitly added back as a "Deferred" category.
- **Kano model** (Basic/Performance/Excitement) — occasionally used for product-facing BRDs where user delight matters (rare in enterprise/back-office BRDs; more common in consumer product requirement docs). Not seen in any of the institutional templates surveyed; flagging as [secondary scheme, not a default].
- **Numeric scoring (1–5 or weighted RICE-style)** — used when a BRD feeds a portfolio-prioritization exercise across many competing initiatives, not just within one document.

**Recommendation for the generator:** default to MoSCoW with an explicit "Won't Have (this release) — Rationale" column, since that is both the most common real-world scheme and the one with the clearest audit trail.

---

## 5. What separates a great BRD from a mediocre one (practitioner commentary)

Synthesizing across IIBA's own guidance, BA training-site commentary, and the recurring patterns across every real template found:

1. **"Why, not how."** IIBA's framing (confirmed via their [blog](https://www.iiba.org/business-analysis-blogs/requirements-documenting--the-foundation-of-a-projects-success/)) is that a BRD states the business need and outcome, and *deliberately does not* prescribe the solution. A great BRD reviewer will strike out any sentence that names a specific technology, vendor, or UI design and push it into a separate FRD/design doc. This single discipline is the most-cited distinguishing factor across sources.

2. **Every objective is falsifiable.** The consistent phrase across multiple sources: *"if you cannot express an objective as a number, it is not specific enough."* Reviewers explicitly reject phrases like "improve customer experience" and demand the numeric before/after/date triple.

3. **The problem statement earns trust by quantifying the cost of inaction, not by assigning blame.** This came directly from the businessanalyststoolkit real-world anecdote — a stakeholder objected to blame-framed language and the fix was reframing to "current state and cost of inaction." This is precisely the register a CFO will accept versus reject.

4. **Traceability is unbroken end-to-end.** Every requirement traces to an objective; every objective's target number reappears in the success-metrics table; every risk that references an assumption is cross-linked. Mediocre BRDs have sections that were clearly drafted independently and never reconciled (numbers introduced in the metrics table that never appeared in the objectives section is the most common tell).

5. **Explicit out-of-scope with reasons, not just an in-scope list.** Multiple sources flag "lists what's included but never says what's excluded" as a defining mediocre-BRD trait.

6. **Named individuals, not role-only stakeholders.** "IT" or "the business" as a stakeholder entry is a red flag; a great BRD names a person, their exact title, and their specific RACI role per decision gate — not a single blanket RACI for the whole document.

7. **Assumptions have an owner and a validation deadline, not just a bullet list.** The single real-world cost-overrun anecdote sourced above exists specifically because an assumption had neither.

8. **Concision is itself a quality signal.** Asana's own product copy states the goal is give readers what they need "without unnecessary length" — reviewers penalize padding (restated objectives, filler "overview" paragraphs that add no new information) as much as they penalize missing content.

9. **A standard, reused template signals institutional maturity.** Per [businessanalystmentor.com](https://businessanalystmentor.com/business-requirements-document/), organizations that reuse one consistent BRD template across projects produce measurably higher-quality documents than ones that reinvent structure per project — reviewers recognize the template and know where to look for what they need, which speeds review and reduces omission.

---

## 6. Anti-patterns — bad text and the fixed version

**1. Solution language in a BRD (should be in an FRD/design doc instead)**

> ❌ Bad: *"We will build a React-based single-page application with a PostgreSQL backend and integrate Salesforce via REST API to solve the underwriting bottleneck."*
>
> ✅ Fixed (business requirement, solution-agnostic): *"The solution shall allow an underwriter to review a complete applicant record — including bureau data and decision-engine rationale — from a single interface, without navigating between systems (see BR-014, §2.6)."*
>
> Why: the bad version locks in a technology stack inside a document whose entire purpose is to stay solution-agnostic so the delivery team can choose the best architecture; it also makes the BRD instantly stale the moment the tech decision changes, even if the business need hasn't.

**2. Unmeasurable objectives**

> ❌ Bad: *"Improve the customer experience and make the loan process more efficient."*
>
> ✅ Fixed: *"Reduce average loan origination cycle time from 9.4 to 3.0 business days by Q2 FY27, measured via the LOS pipeline-stage timestamp report (see Objective 1, §2.1)."*
>
> Why: the bad version cannot ever be disputed as "done" or "not done" — no baseline, no target, no date, no measurement method. This is the single most frequently cited anti-pattern across every source consulted.

**3. Missing out-of-scope section**

> ❌ Bad: a BRD that lists five in-scope bullet points and has no "Out of Scope" heading at all.
>
> ✅ Fixed: an explicit table (see §2.3) where every exclusion states *why* — e.g., *"Auto loan and mortgage origination workflows — Out of scope. Rationale: separate LOS platforms with independent FY27/28 replacement roadmap; combining scope would delay Phase 1 by an estimated 5 months."*
>
> Why: silence on scope is read by stakeholders as "undecided," and undecided scope items resurface as change requests mid-project — the entire point of an out-of-scope section is to pre-empt exactly that conversation, in writing, with a reason attached.

**4. Copy-paste filler sections**

> ❌ Bad: a generic "Executive Summary" that could be pasted into any BRD regardless of project — *"This document outlines the business requirements for the project. It defines scope, objectives, and requirements to ensure successful delivery aligned with organizational goals."*
>
> ✅ Fixed: *"Meridian's consumer loan origination process requires 14 manual data-entry touches per application, driving a 9.4-day average cycle time against a 2.1-day fintech-competitor median. This BRD defines the business requirements to reduce that cycle to 3.0 days and cut Reg B compliance exceptions from 6.2% to under 1.0%, without prescribing the replacement platform's architecture."*
>
> Why: the fixed version contains information that could only be true of *this* project — a real test for filler is "could this sentence be dropped unmodified into an unrelated BRD and still make sense?" If yes, it's filler.

**5. Vague NFRs**

> ❌ Bad: *"The system must be fast, secure, and highly available."*
>
> ✅ Fixed: see the full table at §2.7 — e.g., *"p95 response time < 3 seconds under 150 concurrent sessions (NFR-01/NFR-03); 99.9% uptime during business hours, ≤43 min downtime/month (NFR-02); AES-256 at rest, TLS 1.2+ in transit, field-level encryption for SSN (NFR-04)."*
>
> Why: "fast," "secure," "available" are not testable; QA cannot write a test case against an adjective, and a vendor cannot be held to a contractual SLA against one either.

**6. Stakeholder lists with no names/roles**

> ❌ Bad: *"Stakeholders: IT, Business, Compliance, Risk."*
>
> ✅ Fixed: see the full RACI table at §2.4 — every row is a named individual, exact title, stated interest/influence, and a specific RACI letter per sign-off gate, e.g., *"Meredith Voss, Head of Compliance — Interest: High (Reg B/fair-lending exposure) — Influence: High — RACI on Business Requirements sign-off: Consulted."*
>
> Why: a department name cannot sign off on anything, cannot be escalated to, and cannot be held accountable; without a named individual, "stakeholder approval" is unverifiable and disputes later ("Compliance never approved this") become impossible to resolve.

---

## Sources

- [Stanford UIT — Business Requirements Document Template (.doc)](https://uit.stanford.edu/sites/default/files/2017/08/30/Business%20Requirements%20Document%20Template.doc) — high credibility, institutional template, IEEE-SRS-influenced
- [BC Government — BRD Template, K-12 Education Sector (.doc)](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/services-policies-for-government/information-technology/standards/education-k-12-sector/dt_brd.doc) — government procurement, high credibility [section order partially unverified]
- [IIBA Free BRD Template (Howard Podeswa)](https://go.iiba.org/free-download-business-requirement-document-BRD-template) — highest credibility, IIBA-endorsed, BABOK-aligned
- [IIBA — Requirements Documenting: The Foundation of a Project's Success](https://www.iiba.org/business-analysis-blogs/requirements-documenting--the-foundation-of-a-projects-success/) — high credibility, official IIBA blog
- [Smartsheet — Free Business Requirement Document Templates](https://www.smartsheet.com/content/business-requirement-document-templates) — medium-high credibility, widely used commercial template library
- [Smartsheet — Free Stakeholder Analysis & Matrix Templates](https://www.smartsheet.com/free-stakeholder-analysis-templates)
- [Smartsheet — Free Risk Register Templates](https://www.smartsheet.com/risk-register-templates)
- [Smartsheet — Free Document Control Templates](https://www.smartsheet.com/content/document-control-templates)
- [Asana — Business Requirements Document Template + Free PDF [2026]](https://asana.com/resources/business-requirements-document-template) — medium credibility, modern SaaS-vendor template
- [Asana — Simple BRD Template](https://asana.com/templates/business-requirements-document)
- [CAISO — Business Requirements Specification, Energy Storage Enhancements Track 1 (PDF)](https://www.caiso.com/documents/businessrequirementsspecificationenergystorageenhancementstrack1.pdf) — high credibility, real regulatory artifact [detailed content unverified — extraction failed]
- [businessanalyststoolkit.com — Business Requirements Document Example: Real BRD Walk-Through](https://businessanalyststoolkit.com/business-requirements-document-example/) — medium credibility, BA training site, contains genuine verbatim worked-example fragments
- [businessanalyststoolkit.com — Business Requirements Document Sample](https://businessanalyststoolkit.com/business-requirements-document-sample/) — medium credibility, same source family
- [altexsoft.com — How to Write a Business Requirements Document: Guidelines, Template](https://www.altexsoft.com/blog/business-requirements-document/) — medium-high credibility, established dev/consulting blog, genuine verbatim SMART-objective examples
- [Agile Business Consortium — What is MoSCoW Prioritization?](https://www.agilebusiness.org/resource/what-is-moscow-prioritization/) — high credibility, originator/steward of DSDM and MoSCoW
- [Agile Business Consortium — MoSCoW Prioritisation, DSDM Handbook](https://www.agilebusiness.org/dsdm-project-framework/moscow-prioritisation.html)
- [Medium (Stoneseed) — MoSCoW Prioritisation: Getting It Right From The Start](https://medium.com/@Stoneseed/moscow-prioritisation-must-have-should-have-could-have-wont-have-getting-it-right-from-the-8d9934d16a37) — medium credibility, practitioner blog
- [businessanalystmentor.com — What Should a Business Requirements Document (BRD) Include?](https://businessanalystmentor.com/business-requirements-document/) — medium credibility, BA training site
- [Rocketlane — How to Create a Project Risk Register](https://www.rocketlane.com/blogs/risk-register-template) — medium credibility
- [Deeprojectmanager.com — Risk Register Template](https://deeprojectmanager.com/risk-register-template/) — medium credibility
- [ProjectManager.com — Cost-Benefit Analysis for Projects](https://www.projectmanager.com/blog/cost-benefit-analysis-for-projects-a-step-by-step-guide) — medium credibility
- [Osher Digital — Cost Benefit Analysis Template: From Spreadsheet to Sign-Off](https://osher.com.au/blog/cost-benefit-analysis-template/) — medium credibility, contains base/optimistic/pessimistic scenario modeling guidance
- [ProdPad — 19 Acceptance Criteria Examples for Different Products, Formats and Scenarios](https://www.prodpad.com/blog/acceptance-criteria-examples/) — medium credibility
- [altexsoft.com — Acceptance Criteria: Purposes, Types, Examples and Best Practices](https://www.altexsoft.com/blog/acceptance-criteria-purposes-formats-and-best-practices/) — medium-high credibility
- [Perforce — Non-Functional Requirements: Tips, Tools, and Examples](https://www.perforce.com/blog/alm/what-are-non-functional-requirements-examples) — medium-high credibility, established ALM vendor
- [GeeksforGeeks — Non-Functional Requirements in Software Engineering](https://www.geeksforgeeks.org/non-functional-requirements-in-software-engineering/) — medium credibility

### Confidence: Medium-High
High confidence on: template structures from Stanford/IIBA/Smartsheet/Asana (directly fetched or clearly indexed), MoSCoW discipline (sourced from the scheme's steward, Agile Business Consortium), NFR quantification conventions (converged across 3+ independent sources), and formatting/length conventions (converged across 4+ sources). Lower confidence, explicitly flagged inline: the BC Gov template's exact section order (fetch did not fully resolve), the CAISO PDF's internal content (text extraction failed — worth a manual read if this becomes a reference for regulatory-style BRDs), and the NYU/SFSU/York template details (indexed via search snippets only, not directly fetched). The twelve worked exemplars in Section 2 are explicitly composite/constructed — real, complete equivalents are not publicly available for any of these sections at the level of specificity requested (verified by exhausting the search angles most likely to surface one), so calibrated construction against real fragments and real institutional templates was the only viable path, and is flagged as such throughout rather than presented as sourced.
