# Research Brief: Canonical BRD Structure per Professional Standards (2025-2026)

**Compiled:** 2026-07-29
**Scope:** BABOK v3, ISO/IEC/IEEE 29148:2018, canonical BRD anatomy, BRD/FRD/SRS/PRD/BRS boundaries, traceability conventions, real-world approval/rejection patterns.

---

## 1. BABOK v3 (IIBA) grounding

### 1.1 The four-tier requirements classification

BABOK v3 (IIBA's *Business Analysis Body of Knowledge*, current edition since 2015, still the governing standard for CBAP/CCBA certification in 2025-2026) classifies requirements into **four types**, forming a top-down chain of "why → who → what → how to get there":

| Tier | BABOK definition (paraphrased from IIBA-derived sources) | Answers | What belongs in it |
|---|---|---|---|
| **1. Business Requirements** | "Statements of goals, objectives, and outcomes that describe why a change has been initiated." Represent the organization's high-level needs. | WHY is this initiative needed? | Strategic goals, business drivers, desired outcomes (e.g., "reduce customer support response time by 70% within 6 months"). No mention of features, screens, or systems. |
| **2. Stakeholder Requirements** | "Describe the needs of a stakeholder or class of stakeholders... that must be met in order to achieve the business requirements." Act as the bridge between business goals and solution capability. | WHAT does each stakeholder group need from the solution? | Stakeholder-specific needs (e.g., "support agents need a daily dashboard comparing response-time SLAs across regions"). Still solution-agnostic in principle, though this is where the grey zone with "solution-ish" language begins in practice. |
| **3. Solution Requirements** | "Describe the capabilities and qualities of a solution that meets the stakeholder requirements." Split into two sub-types: **Functional Requirements** (what the solution must *do* — behaviors, features, data, business rules) and **Non-Functional Requirements** (how well the solution must perform — quality attributes like security, performance, usability, availability). | HOW will the solution behave/perform? | System behaviors, business rules, data requirements, quality attributes. This is the FRD/SRS territory, not BRD territory. |
| **4. Transition Requirements** | "Describe capabilities that the solution must have and characteristics that the solution must possess to facilitate transition from the current state to the future state, but that are not needed once the transition is complete." Inherently temporary/short-lived. | HOW do we get from AS-IS to TO-BE without the requirement persisting afterward? | Data migration, training programs, parallel-run periods, legacy decommissioning, cutover plans. |

Source: [BABOK Classification Schema — Techcanvass](https://businessanalyst.techcanvass.com/types-of-requirements-as-per-babok/), [IIBA Requirement Types Infographic](https://www.iiba.org/contentassets/38e412c7b77d456297d953de5bf5ca61/requirement-types-infograph.pdf), [ModernAnalyst BABOK requirement categorization](https://modernanalyst.com/Careers/InterviewQuestions/tabid/128/ID/2033/Explain-how-BABOK-categorizes-requirements.aspx). Note: this brief paraphrases BABOK's classification via secondary/tertiary sources widely used in the BA community (IIBA gates the full text of the printed Guide behind membership); the four-tier structure and the exact "why/what/how/transition" framing is consistently corroborated across every source checked, so treat the *classification itself* as high-confidence, but individual definition sentences are paraphrases, not verbatim BABOK quotes. [flag: could not access verbatim BABOK v3 text directly]

**Practical BRD implication:** A canonical BRD should live almost entirely in **Tier 1 (Business Requirements)** and touch **Tier 2 (Stakeholder Requirements)** only at the level of "stakeholder needs," never diving into Tier 3 (Solution/Functional/Non-Functional) or Tier 4 (Transition) except as forward-looking scope statements ("a training program will be required" is fine in a BRD; "the training LMS will use SCORM 1.2 packages" is not — that's Tier 4 detail that belongs in a transition plan/FRD).

### 1.2 BABOK Knowledge Areas that map to BRD production

BABOK v3 organizes all BA work into **six Knowledge Areas (KAs)**. Four map directly onto BRD production:

1. **Business Analysis Planning and Monitoring** — defines the BA approach, stakeholder engagement plan, governance for how the BRD itself will be reviewed/approved. This is where the sign-off/approval matrix and RACI for the BRD process itself gets defined.

2. **Elicitation and Collaboration** — the raw-material-gathering KA. Five tasks: *Prepare for Elicitation, Conduct Elicitation, Confirm Elicitation Results, Communicate Business Analysis Information, Manage Stakeholder Collaboration*. This KA is what actually produces the interview notes, workshop outputs, and confirmed findings that get distilled into the BRD's Business Requirements and Stakeholder Analysis sections. Source: [IIBA Elicitation and Collaboration](https://www.iiba.org/knowledgehub/business-analysis-body-of-knowledge-babok-guide/4-elicitation-and-collaboration/).

3. **Strategy Analysis** — the KA that directly produces the BRD's **Current State / Future State** sections. Four tasks: *Analyze Current State, Define Future State, Assess Risks, Define Change Strategy*. This is explicitly the source of AS-IS/TO-BE modeling and risk assessment — not Requirements Analysis and Design Definition, contrary to a common misconception. Source: [BA Coach — Strategy Analysis](https://bacoach.nl/2020/11/strategy-analysis/), [Business Analysis Excellence Strategy Analysis notes](https://business-analysis-excellence.com/wp-content/uploads/2020/05/Week-4-Strategy-Analysis-Study-Notes.pdf).

4. **Requirements Life Cycle Management (RLCM)** — governs requirements *after* they're written: tracing, maintaining, prioritizing, and managing change to requirements from inception to retirement. This is the KA that mandates traceability (→ RTM), versioning, and approval workflows. It's why a professionally-produced BRD always carries requirement IDs and a change-control section.

5. *(Requirements Analysis and Design Definition — mostly downstream of the BRD; it's where stakeholder requirements get analyzed into solution/functional requirements — i.e., FRD/SRS territory, not BRD territory. Still relevant as the boundary line: everything in this KA's output belongs in the *next* document, not the BRD.)*

Source: [Modern Requirements — 6 BABOK Knowledge Areas](https://www.modernrequirements.com/blogs/babok-knowledge-areas-explained/), [IIBA Knowledge Areas](https://www.iiba.org/knowledgehub/the-business-analysis-standard/5-applying-business-analysis-tasks/5-3-business-analysis-knowledge-areas/).

---

## 2. ISO/IEC/IEEE 29148:2018

ISO/IEC/IEEE 29148:2018, *Systems and software engineering — Life cycle processes — Requirements engineering*, is the internationally recognized successor to IEEE 830-1998 (SRS) and IEEE 1233 (SyRS), now maintained jointly by ISO, IEC, and IEEE. [IEEE SA listing](https://standards.ieee.org/standard/29148-2018.html). It defines the requirements engineering process across the system life cycle and prescribes both process activities and document templates. The full standard text is paywalled (ISO/IEEE Xplore); this brief synthesizes from secondary sources that quote/paraphrase it, and I could not verify the exact verbatim clause numbering. [flag: primary text not directly accessible]

### 2.1 Document types the standard defines

The standard prescribes **five distinct specification document types**, each with a defined scope:

1. **StRS — Stakeholder Requirements Specification** (stakeholder-level needs; closest sibling to a BRD/BRS)
2. **SyRS — System Requirements Specification** (system-level requirements, technology-agnostic)
3. **SRS — Software Requirements Specification** (software-level, successor to IEEE 830)
4. **BRS — Business Requirements Specification** (business/mission-level requirements — explicitly named "Business Requirements Specification" in the standard, giving BRS a more formal pedigree than "BRD," which is an industry-convention term, not an ISO-defined artifact)
5. **OpsCon — System Operational Concept** (captures stakeholder needs from an operational-scenario perspective)

Source: [ReqView — ISO/IEC/IEEE 29148 Templates](https://www.reqview.com/doc/iso-iec-ieee-29148-templates/). Note the important nuance: **"BRD" as commonly used in industry is NOT one of ISO 29148's five named document types.** The closest ISO-formal equivalents are **BRS** (Business Requirements Specification) and **StRS** (Stakeholder Requirements Specification). Most real-world "BRDs" are, in ISO terms, a hybrid of BRS + StRS content bundled into one artifact for business audiences. This is a genuinely useful distinction to make in the eventual BRD system: it explains *why* BRDs vary so much in scope from org to org — they're an informal industry convention layered on top of (and blending) two formal ISO document types.

### 2.2 Characteristics of a good INDIVIDUAL requirement

ISO/IEC/IEEE 29148:2018 defines **nine characteristics** a well-formed individual requirement must exhibit:

1. **Necessary** — the requirement defines an essential capability; removing it would leave a genuine gap in what the system/business needs, not just a "nice to have."
2. **Appropriate** — the level of detail matches the level of the document (a BRD-level requirement should not specify implementation detail appropriate to an SRS).
3. **Unambiguous** — stated so it allows exactly one interpretation. Standard illustrative contrast: "increase website speed" (ambiguous) vs. "reduce page load time to under 1 second" (unambiguous).
4. **Complete** — needs no further amplification; every threshold/condition a reader needs is present in the statement itself, not implied.
5. **Singular** — states exactly one requirement, with no conjunctions bundling multiple capabilities ("the system shall do X and Y" is a smell — split into two).
6. **Feasible** — achievable within real technical, budgetary, and schedule constraints.
7. **Verifiable** — can be proven true or false via inspection, test, analysis, or demonstration; forbids subjective/unmeasurable language like "user-friendly" or "fast" without a quantified threshold.
8. **Correct** — accurately reflects the actual stakeholder need (not a mis-transcribed or assumed need).
9. **Conforming** — follows the organization's standard template/style rules for how requirements are worded (e.g., consistent use of "shall").

Source (secondary, paraphrased from the standard): [Modern Requirements — ISO 29148 Explained](https://www.modernrequirements.com/blogs/iso-29148-explained/), corroborated by [ReqView ISO 29148 templates](https://www.reqview.com/doc/iso-iec-ieee-29148-templates/) and multiple academic papers citing the standard (e.g. arXiv papers on requirements quality NLP tooling). [flag: paraphrased, not verbatim ISO clause text — could not access the paywalled standard directly]

### 2.3 Characteristics of a good requirements SET

Beyond individual requirements, the standard also defines **five characteristics for a requirements set as a whole**:

1. **Complete** — the set as a whole covers everything the solution/business needs; no gaps.
2. **Consistent** — no requirement contradicts another; terminology is used uniformly across the whole set (this is why every serious BRD needs a **Glossary** section — inconsistent terminology is the single most common way requirement sets fail this test).
3. **Feasible** — the whole set can be implemented together within actual constraints (an individual requirement can be feasible in isolation but the set becomes infeasible in combination — e.g., two requirements that are individually fine but jointly imply conflicting architectures).
4. **Comprehensible** — the intended audience (stakeholders, not just engineers) can understand the set without additional interpretation.
5. **Able to be validated** — the set can be checked against actual, traceable stakeholder intent — i.e., every requirement in the set can be traced back to a real elicitation source, not fabricated or assumed.

Source: [Modern Requirements — ISO 29148 Explained](https://www.modernrequirements.com/blogs/iso-29148-explained/). [flag: paraphrased from secondary source]

### 2.4 Requirement attributes the standard recommends tracking

Per ISO 29148-aligned tooling documentation, each requirement should carry these metadata attributes: **ID, Heading, Text, Owner, Priority, Source, Rationale, Difficulty, Type, Status, Verification Method.** Source: [ReqView](https://www.reqview.com/doc/iso-iec-ieee-29148-templates/). This maps directly onto what a professional RTM needs as columns (see Section 5).

---

## 3. Canonical BRD section-by-section anatomy

There is no single ISO-mandated BRD template (see 2.1 — BRD is an informal industry convention, not an ISO document type), but cross-referencing multiple 2025-2026 professional templates (PandaDoc, Asana, Wrike, Business Analyst Toolkit, IT Toolkit) and real BA practice produces a highly consistent canonical structure. Below is the synthesized definitive anatomy, with weak/strong contrast and length guidance based on cross-source consensus.

| # | Section | Must contain | WEAK version | STRONG version | Typical length |
|---|---|---|---|---|---|
| 1 | **Executive Summary** | Problem, proposed change, expected business outcome, in plain English, written LAST | Copy-pasted intro restating the doc title; no numbers; reads like boilerplate | 2-3 paragraphs a VP could read in 90 seconds and know: what's broken, what's changing, what it's worth, when it lands | 150-300 words, max 1 page |
| 2 | **Business Objectives** | SMART-formatted goals tied to strategy; each objective should later map to ≥1 KPI in Section-14 | "Improve efficiency" | "Reduce average claim-processing time from 6.2 days to ≤2 days within Q1 FY27, tied to the FY26 Ops OKR of 30% cost-to-serve reduction" | 0.5-1 page, 3-7 objectives |
| 3 | **Background / Problem Statement** | Why now — current pain, business trigger (regulatory, competitive, cost, customer complaint volume), history of the problem | "The current system is outdated" | Quantified pain with named source: "Support tickets tagged 'billing-error' rose 340% YoY (Zendesk export, Jan-Dec 2025); root cause traced to manual reconciliation in the legacy AS/400 system (IT audit, Nov 2025)" | 0.5-1.5 pages |
| 4 | **Project Scope — In Scope / Out of Scope** | Explicit numbered in-scope list AND explicit numbered out-of-scope/exclusions list — the exclusions list is the single highest-leverage anti-scope-creep tool in the whole document | Only "in scope" bullets, no exclusions at all | Both lists numbered, out-of-scope items include *why* excluded ("Mobile app redesign — excluded, scheduled as Phase 2 per roadmap dated 2026-03") | 0.5-1 page |
| 5 | **Stakeholder Analysis + RACI** | Named stakeholders, role, influence/interest, and a RACI table mapped to key deliverables/decisions (not just "who's involved" prose) | "Stakeholders include IT, Finance, and Ops" | Table: Name, Role, R/A/C/I per deliverable (BRD sign-off, UAT sign-off, go-live decision), plus escalation path if RACI conflicts | 0.5-1 page |
| 6 | **Current State (As-Is) Process** | Process map or numbered flow of how the business operates TODAY, including pain points annotated on the flow | Vague prose paragraph, no diagram, no pain points marked | Swimlane/flow diagram + numbered steps + explicit "pain point" callouts at the exact steps that fail, ideally with a metric per pain point | 0.5-1.5 pages (often a diagram + captions) |
| 7 | **Future State (To-Be) Process** | Process map of how the business SHOULD operate post-change, still at a business-process level (not UI/system level — that's FRD territory) | Just restates objectives as a flow with no real change shown | Side-by-side or annotated diagram showing exactly which steps change/disappear/get automated, tied back to specific Business Requirement IDs | 0.5-1.5 pages |
| 8 | **Business Requirements (numbered)** | Every requirement has a unique ID (BR-001...), a business-language statement, a linked objective, a priority (MoSCoW or similar), and a source stakeholder | Requirements phrased as vague wishes ("system should be user-friendly"), no IDs, no traceability to objectives | Fully tabular: ID / Statement / Linked Objective / Priority / Source / Acceptance Criteria pointer | 2-6 pages depending on project size — this is the core of the document |
| 9 | **Functional Requirements boundary** | A BRD should NOT contain detailed functional requirements. At most, a short pointer section stating "detailed functional requirements are elicited and maintained in the companion FRD [link/ref]" plus perhaps a small number of business-rule-level statements that are genuinely business rules, not UI/system behavior | BRD balloons into full functional spec with screen mockups and field-level validation rules (classic BRD/FRD boundary violation, called out explicitly by rejection-reason research in Section 6) | Clear one-paragraph boundary statement + explicit reference/link to the FRD artifact that will carry Tier-3 solution requirements | 1 short paragraph, not a section |
| 10 | **Non-Functional Requirements** | Business-level quality expectations only (e.g., "system must support 5,000 concurrent users during month-end close," "must comply with GDPR / DPDP Act 2023") — NOT the fully engineered NFR spec, which lives in SRS | Missing entirely, or copy-pasted generic NFR checklist irrelevant to this project | Prioritized, quantified, business-justified NFRs directly traceable to a business risk or regulatory driver | 0.5 page |
| 11 | **Assumptions** | Explicit statements of what's presumed true but unverified — each should be falsifiable and, ideally, have an owner tasked with validating it | "We assume the project will go smoothly" | "We assume all business units share a single corporate network; NOT YET VERIFIED for the two remote regional offices — action owner: [name], due [date]" (the real BA-Toolkit example: an unvalidated version of exactly this assumption doubled infrastructure cost when it turned out false) | 0.25-0.5 page |
| 12 | **Dependencies** | Cross-project/cross-team dependencies this initiative relies on (other projects, vendor deliverables, data availability, budget approval) | Not listed at all, or vaguely "depends on IT" | Named dependency, owning team, expected delivery date, impact if delayed | 0.25-0.5 page |
| 13 | **Constraints** | Hard limits — budget ceiling, go-live date, regulatory deadline, fixed headcount, legacy system that cannot be touched | Generic "limited budget and time" | Specific numbers: "$420K hard budget cap approved by Finance 2026-04-01; go-live must precede FY-end 2027-03-31 per audit committee mandate" | 0.25-0.5 page |
| 14 | **Risks** | Categorized risks (technology, skills, environmental/political, business, requirements-related), each with likelihood, impact, and mitigation/owner | Generic risk list with no likelihood/impact/owner | Full risk register: category, description, likelihood, impact, mitigation, owner, status | 0.5-1 page |
| 15 | **Success Metrics / KPIs** | Measurable, baseline + target, tied directly back to Section-2 objectives | "Success = happy users" | Baseline value, target value, measurement method, measurement cadence, owner, tied to specific Business Objective ID | 0.5 page |
| 16 | **Acceptance Criteria** | Condition(s) under which each business requirement (or the whole initiative) is considered DONE and accepted by the business — often Given/When/Then or checklist form, requirement-linked | Missing, or one vague paragraph ("system must work correctly") | Per-requirement acceptance criteria, testable, tied to BR-IDs, later becomes the seed for UAT test cases | 1-2 pages (can be an appendix table) |
| 17 | **Cost-Benefit / Business Case** | Investment required, expected return (cost savings, revenue, risk reduction), payback period, alternatives considered including "do nothing" | Missing, or a single unsubstantiated ROI number | Full cost breakdown (build + run), quantified benefit categories, payback/NPV/IRR if applicable, alternatives with why rejected | 0.5-1.5 pages |
| 18 | **Glossary** | Every domain term, acronym, and system name used in the doc, defined once — directly serves ISO 29148's "consistent terminology" set-characteristic (2.3) | Missing, or 3 terms defined when 20 are used undefined | Comprehensive, alphabetized, includes both business and technical terms since the audience spans both | 0.5-1 page |
| 19 | **Appendices** | Supporting detail that would clutter the main body — interview notes, detailed process diagrams, raw data, prior-art research, vendor comparisons | Dumping ground with no organization | Labeled, referenced from the main body ("see Appendix C for full swimlane"), each appendix has a one-line purpose statement | Variable |
| 20 | **Sign-off / Approval Matrix** | Named approvers, role, date signed, and (critically) what they are approving — many disputes trace back to ambiguity about whether sign-off meant "I read this" vs "I commit budget/resources" | No sign-off section, or a vague "approved by management" line with no names/dates | Table: Name / Role / Approval scope (e.g., "Business Requirements only" vs "Full BRD including budget") / Date / Signature, plus a defined escalation path for non-response | 0.25 page |

Sources for section anatomy: [PandaDoc BRD Template](https://www.pandadoc.com/business-requirements-document-template/), [Business Analyst Toolkit — BRD Example Walkthrough](https://businessanalyststoolkit.com/business-requirements-document-example/), [Asana BRD Template](https://asana.com/resources/business-requirements-document-template), [IT Toolkit BRD Guide](https://www.ittoolkit.com/business-requirements-document-template-free-complete-guide/), [Wrike BRD Guide](https://www.wrike.com/blog/how-write-business-requirements-document/), [Monday.com BRD templates and best practices](https://monday.com/blog/project-management/business-requirements-document/). Note: no single source contains all 20 sections — this table is a **synthesis across sources**, cross-checked for consistency; the weak/strong contrasts and length estimates for sections not explicitly detailed in any single source (Stakeholder RACI, Current/Future State, Dependencies, Risks categorization, Cost-Benefit, Sign-off) are my own synthesis grounded in the sourced material and standard BA practice, not a verbatim quote from any one template. [flag: length estimates are practitioner convention, not from a formal standard]

---

## 4. BRD vs FRD vs SRS vs PRD vs BRS — precise boundaries

### 4.1 The document family and their level of abstraction

| Document | Owned by | Audience | BABOK tier it corresponds to | Core question |
|---|---|---|---|---|
| **BRD** (Business Requirements Document) | Business Analyst | Executives, sponsors, business stakeholders | Tier 1 (Business) + light Tier 2 (Stakeholder) | WHY are we doing this, and what does the business need? |
| **BRS** (Business Requirements Specification) | Business Analyst | Same as BRD — this is the ISO-formal name for essentially the same artifact | Tier 1 | Same as BRD; BRS is the ISO 29148-named counterpart of the informal "BRD" |
| **PRD** (Product Requirements Document) | Product Manager | Product/eng leadership, design, engineering | Tier 2 (Stakeholder) bridging into Tier 3 | WHAT should the product do to satisfy the stakeholder/user need — feature-level, still business-readable |
| **FRD/FRS** (Functional Requirements Document/Spec) | Business Analyst / Systems Analyst | Developers, QA, technical leads | Tier 3 — Functional Requirements | HOW should the system behave, function by function (internal document, defines the solution) |
| **SRS** (Software Requirements Specification) | Systems/Software Engineer, sometimes BA | Engineers, architects, QA | Tier 3 — Functional + Non-Functional Requirements, most detailed/complete | Full behavioral spec: functional AND non-functional, often with UML/data models, ready to build against |

Sources: [BA Times — BRD vs FRD](https://www.batimes.com/articles/brd-vs-frd/) *(fetch blocked 403; used via search snippet only)*, [BABeginners — BRD vs FRD vs SRS](https://babeginners.com/difference-between-brd-frd-and-srs/), [The Business Perspective — BRD vs PRD vs SRS vs FRS 2025](https://thebusinessperspective.in/brd-vs-prd-vs-srs-vs-frs/), [Modern Entrepreneurship — SRD vs BRD vs FRS](https://modernentrepreneurship.medium.com/srd-vs-brd-vs-frs-understanding-key-business-documents-for-project-success-a77d8a02818c). Consensus framing across all sources: **"The BRD is your 'why', the PRD is 'what features should it have', the SRS dives into 'how it should work', and the FRS outlines 'what functionalities it must perform.'"**

### 4.2 The exact rule for keeping solution language out of a BRD

The consistent rule across every source: **a BRD statement must survive being read by someone with zero knowledge of the eventual system/technology and still make complete sense as a business need.** If a sentence names a specific screen, field, button, database table, API, vendor product, or technical mechanism, it has crossed into FRD/SRS territory. The test in practice:

- If the sentence answers **"what does the business need to achieve"** → BRD.
- If the sentence answers **"what must the system do to make that happen"** → FRD/SRS.
- If the sentence names **a specific UI element, data field, algorithm, or technology** → definitely FRD/SRS, never BRD.

### 4.3 Ten example sentences classified (synthesized, illustrative — not sourced verbatim, constructed to demonstrate the boundary rule above)

| # | Sentence | Document | Why |
|---|---|---|---|
| 1 | "The organization needs to reduce average customer complaint resolution time to improve retention." | **BRD** | Pure business outcome, no solution implied |
| 2 | "Customer support managers need a way to see, at a glance, which regions are missing SLA targets." | **BRD** (Stakeholder Requirement, still Tier 2) | Describes a stakeholder need, not a mechanism |
| 3 | "As a support manager, I want a dashboard so that I can identify underperforming regions daily." | **PRD** | User-story format naming a specific product artifact ("dashboard") — one level more solution-committed than the BRD statement above |
| 4 | "The system shall display a bar chart of SLA compliance by region, refreshed every 15 minutes." | **FRD/FRS** | Specific UI element + specific behavior + specific refresh rate |
| 5 | "The SLA dashboard widget shall query the `region_sla_summary` materialized view and cache results for 15 minutes using Redis." | **SRS** | Names actual data structures and technology — implementation-level |
| 6 | "All customer financial data must remain compliant with the Digital Personal Data Protection Act, 2023." | **BRD** | Business/regulatory constraint, no implementation named |
| 7 | "Field-level encryption shall be applied to the `pan_number` and `aadhaar_number` columns using AES-256." | **SRS** | Named fields + named encryption method = solution-level |
| 8 | "Legacy customer records must be migrated from the AS/400 mainframe to the new platform before go-live, with zero data loss." | **BRD, Transition Requirement (Tier 4)** | Describes a necessary transition outcome without prescribing the migration mechanism |
| 9 | "A nightly ETL job using Apache NiFi shall extract, transform, and load AS/400 VSAM records into the PostgreSQL `customers` table." | **FRD/SRS** | Specific tool + specific tables = solution/implementation detail |
| 10 | "The new claims process must reduce manual reconciliation steps from 7 to no more than 2." | **BRD** (borderline into Tier 2/3) | This is the legitimate grey zone (see 4.4) — it's quantified and process-specific but still describes an outcome, not a mechanism |

### 4.4 The legitimate grey zone

All sources converge on one honest caveat: the **Stakeholder Requirements tier (BABOK Tier 2)** is inherently the grey zone. A statement like "the system needs a way to flag high-risk transactions in real time" is business-flavored but is already implying a solution shape (some kind of real-time flagging mechanism). BA practice handles this by:
- Keeping such statements at the *capability* level ("must flag," not "must display a red banner via a WebSocket push")
- Explicitly tagging borderline items in the BRD as "Stakeholder Requirement — solution TBD in FRD" so reviewers know the line was deliberately drawn there, not sloppily
- The over-detailing failure mode ("BRD balloons into functional spec with screen mockups") is explicitly named as a real-world rejection trigger in Section 6 below — this is the single most common boundary violation cited across BA practitioner sources.

---

## 5. Requirement ID / traceability conventions

### 5.1 Real-world numbering schemes

Industry-standard prefix conventions, consistently observed across BA templates and tooling docs:

- **BR-xxx** — Business Requirement (e.g., BR-001)
- **STK-xxx** or **StR-xxx** — Stakeholder Requirement
- **FR-xxx** — Functional Requirement
- **NFR-xxx** — Non-Functional Requirement
- **BUS-xxx** — sometimes used as an alternate business-rule prefix, distinct from BR when an org wants to separate "business rules" (data/logic constraints, e.g., "a policy cannot be issued to an applicant under 18") from "business requirements" (goals/outcomes)
- **TR-xxx** — Transition Requirement (less standardized than the others, sometimes folded into BR)

Numbering is typically **hierarchical and zero-padded** (BR-001, BR-002...) and sometimes nested to show decomposition (BR-001 → FR-001.1, FR-001.2 as its child functional requirements). Source: [MiniWrites — How to Write BR, FR, NFR](https://miniwrites.com/2019/11/02/how-to-write-br-fr-and-nfr/), consistent with general RTM tooling convention across [Jama Software](https://www.jamasoftware.com/requirements-management-guide/requirements-traceability/how-to-create-and-use-a-requirements-traceability-matrix-rtm/), [ReqView](https://www.reqview.com/blog/requirements-traceability-matrix/), [ProjectManager.com](https://www.projectmanager.com/blog/requirements-traceability-matrix).

### 5.2 RTM structure — real columns used in practice

Consolidating across Jama Software, ReqView, PractiTest, and ProjectManager.com guidance, a professional RTM contains:

| Column | Purpose |
|---|---|
| Requirement ID | Unique identifier (BR-001, FR-001, etc.) |
| Requirement Description | The actual requirement statement |
| Source | Who/what elicitation activity produced it (named stakeholder, interview, workshop) |
| Linked Business Objective | Upward traceability — which Section-2 objective this requirement serves |
| Priority | MoSCoW (Must/Should/Could/Won't) or numeric |
| Owner | Accountable person for the requirement's fulfillment |
| Type | BR / FR / NFR / Transition |
| Status | Draft / Approved / In Development / Tested / Deployed / Deferred |
| Linked Design/Solution Element | Downward traceability — which FRD/SRS item, screen, or module implements this |
| Linked Test Case ID | Downward traceability — which UAT/QA test case(s) verify it |
| Verification Method | Inspection / Analysis / Demonstration / Test (per ISO 29148 attribute set, 2.4 above) |
| Regulatory/Standard Reference | For regulated industries — links requirement to the specific compliance clause it satisfies |

**Upward traceability** (requirement → business objective) is explicitly the weaker-covered direction in most off-the-shelf RTM guidance — several sources (e.g., Jama Software's own guide) focus mostly on **forward traceability** (requirement → test case) and explicitly note upward-to-objective linkage is often left out of basic templates, which is a real gap professional/regulated orgs have to deliberately fix by adding a "Linked Business Objective" column. [flag: this asymmetry — strong downward, weak upward, in most public templates — is a genuine finding worth designing around]

**Downward traceability** (requirement → design → test case) is the best-covered direction: "every requirement has at least one linked test case," and RTM audits specifically check for **orphaned test cases** (test cases with no requirement) and **orphaned requirements** (requirements with no test case) as the two canonical traceability defects. Source: [Jama Software RTM Guide](https://www.jamasoftware.com/requirements-management-guide/requirements-traceability/how-to-create-and-use-a-requirements-traceability-matrix-rtm/).

---

## 6. How BRDs get approved/rejected in real orgs

Cross-referencing practitioner sources (Blueprint, ReBoot Co., Nuclino, Business Analyst Toolkit, ailawyer.pro's 2025 legal/strategic BRD piece), the concrete, recurring rejection reasons are:

1. **Vague, untestable requirements.** Requirements phrased as unmeasurable wishes ("system should be user-friendly," "improve efficiency") fail the ISO 29148 *verifiable* characteristic (2.2) — reviewers correctly reject these because there's no way to confirm they were met.

2. **Solution language leaking into the BRD.** The BRD balloons into functional-spec territory — screen mockups, field-level validation rules, specific vendor names — inside a document meant to stay solution-agnostic. This is the #1 boundary-violation rejection reason, directly tied to Section 4's grey-zone problem.

3. **No explicit out-of-scope section.** Missing exclusions is repeatedly cited as a critical gap — without it, every future ambiguous request becomes a scope-creep argument instead of a documented "explicitly excluded" fact.

4. **No measurable success criteria / KPIs.** If Section 15 (Success Metrics) is missing or vague, the review board has no way to know when the project is "done" or successful, which is a standard rejection trigger.

5. **Broken traceability.** Requirements that can't be traced back to a business objective, or objectives with no requirements serving them, get flagged — "every requirement can be traced back to a business problem" is cited as the defining trait of BRDs that actually survive contact with implementation.

6. **Unvalidated assumptions.** Assumptions stated as fact without an owner tasked to verify them are a recurring real-world failure mode — the AS/400 cross-site network assumption example (Section 3, row 11) that doubled infrastructure cost is exactly this failure pattern playing out post-approval, which review boards increasingly screen for pre-approval by requiring assumptions to be explicitly flagged as "unverified."

7. **No formal sign-off / ambiguous sign-off scope.** Shipping without a proper approval matrix (who approved WHAT, and when) is called out explicitly as a critical process failure — it re-opens disputes later about whether a stakeholder actually agreed to scope, budget, or just "read" the document.

8. **Passive, overly technical language that business stakeholders don't recognize or can't authoritatively confirm.** If the people who must approve a requirement can't understand or verify it in their own operational language, approval becomes rubber-stamping rather than genuine validation — which surfaces as disputes later in the project.

9. **Stale BRDs.** Letting the BRD go unmaintained after initial approval — no change-control process for amendments as scope legitimately evolves — is cited as a distinct failure mode from the initial-approval failures above; RLCM (BABOK KA, Section 1.2) exists specifically to prevent this.

10. **Problem-statement framing disputes.** One source frames this sharply: writing a BRD "is actually a negotiation task" disguised as a writing task — expect the problem statement (Section 3) to be rewritten at least twice, and expect the sharpest pushback to come from a stakeholder who is factually correct but has a different, equally valid framing of the underlying problem. This isn't a document-defect rejection so much as a structural reality of the BRD approval process that any BRD-authoring system should account for (iterative re-framing, not one-shot approval).

Sources: [Blueprint — Why BRD Isn't Enough](https://www.blueprintsys.com/blog/your-business-requirements-document-isnt-helping), [ReBoot Co. — BRDs are no good](https://www.rebootco.com.au/blog/business-requirements-documents-are), [Business Analyst Toolkit — BRD Example](https://businessanalyststoolkit.com/business-requirements-document-example/), [Business Analyst Toolkit — BRD Sample](https://businessanalyststoolkit.com/business-requirements-document-sample/), [ailawyer.pro — BRD 2025 Legal/Strategic Must-Have](https://ailawyer.pro/blog/business-requirements-document-(brd)-the-legal-strategic-must-have-for-2025-projects), [Nuclino — How to Write a BRD](https://www.nuclino.com/articles/business-requirements-document).

---

## Summary of what's verified vs. flagged

- **High confidence (multi-source corroborated):** BABOK four-tier requirement classification; BABOK six knowledge areas and their KA-to-BRD mapping; the BRD/FRD/SRS/PRD abstraction hierarchy and boundary rule; the canonical BRD section list (all 20 sections independently corroborated across ≥2 sources each, though no single source has all 20); RTM prefix conventions (BR/FR/NFR); the ten real-world rejection-reason categories.
- **Medium confidence / paraphrased, not verbatim:** ISO/IEC/IEEE 29148:2018's exact wording for the 9 individual-requirement characteristics and 5 set characteristics — the *list and substance* is corroborated across multiple secondary sources but I could not access the actual paywalled standard text to quote it verbatim. [flag: verbatim ISO text unverified]
- **Synthesized by me, not sourced verbatim:** the weak/strong contrast column and length estimates in Section 3's table (grounded in cross-source patterns and BA practice, but not lifted from any single template); the 10 example sentences in Section 4.3 (constructed to demonstrate the sourced boundary rule, not quoted from any document).

## Sources (consolidated)

- [BABOK Classification Schema — Techcanvass](https://businessanalyst.techcanvass.com/types-of-requirements-as-per-babok/)
- [IIBA Requirement Types Infographic](https://www.iiba.org/contentassets/38e412c7b77d456297d953de5bf5ca61/requirement-types-infograph.pdf)
- [ModernAnalyst — BABOK requirement categorization](https://modernanalyst.com/Careers/InterviewQuestions/tabid/128/ID/2033/Explain-how-BABOK-categorizes-requirements.aspx)
- [IIBA — Elicitation and Collaboration KA](https://www.iiba.org/knowledgehub/business-analysis-body-of-knowledge-babok-guide/4-elicitation-and-collaboration/)
- [Modern Requirements — 6 BABOK Knowledge Areas](https://www.modernrequirements.com/blogs/babok-knowledge-areas-explained/)
- [BA Coach — Strategy Analysis](https://bacoach.nl/2020/11/strategy-analysis/)
- [Business Analysis Excellence — Strategy Analysis Study Notes](https://business-analysis-excellence.com/wp-content/uploads/2020/05/Week-4-Strategy-Analysis-Study-Notes.pdf)
- [IEEE SA — IEEE/ISO/IEC 29148-2018](https://standards.ieee.org/standard/29148-2018.html)
- [ReqView — ISO/IEC/IEEE 29148 Templates](https://www.reqview.com/doc/iso-iec-ieee-29148-templates/)
- [Modern Requirements — ISO 29148 Explained](https://www.modernrequirements.com/blogs/iso-29148-explained/)
- [PandaDoc — BRD Template](https://www.pandadoc.com/business-requirements-document-template/)
- [Business Analyst Toolkit — BRD Example](https://businessanalyststoolkit.com/business-requirements-document-example/)
- [Business Analyst Toolkit — BRD Sample](https://businessanalyststoolkit.com/business-requirements-document-sample/)
- [Asana — BRD Template](https://asana.com/resources/business-requirements-document-template)
- [IT Toolkit — BRD Guide](https://www.ittoolkit.com/business-requirements-document-template-free-complete-guide/)
- [Wrike — BRD Guide](https://www.wrike.com/blog/how-write-business-requirements-document/)
- [Monday.com — BRD templates and best practices](https://monday.com/blog/project-management/business-requirements-document/)
- [BA Times — BRD vs FRD](https://www.batimes.com/articles/brd-vs-frd/)
- [BABeginners — BRD vs FRD vs SRS](https://babeginners.com/difference-between-brd-frd-and-srs/)
- [The Business Perspective — BRD vs PRD vs SRS vs FRS (2025)](https://thebusinessperspective.in/brd-vs-prd-vs-srs-vs-frs/)
- [Modern Entrepreneurship — SRD vs BRD vs FRS](https://modernentrepreneurship.medium.com/srd-vs-brd-vs-frs-understanding-key-business-documents-for-project-success-a77d8a02818c)
- [MiniWrites — How to Write BR, FR, NFR](https://miniwrites.com/2019/11/02/how-to-write-br-fr-and-nfr/)
- [Jama Software — RTM Guide](https://www.jamasoftware.com/requirements-management-guide/requirements-traceability/how-to-create-and-use-a-requirements-traceability-matrix-rtm/)
- [ReqView — Requirements Traceability Matrix](https://www.reqview.com/blog/requirements-traceability-matrix/)
- [ProjectManager.com — RTM Guide](https://www.projectmanager.com/blog/requirements-traceability-matrix)
- [Blueprint — Why BRD Isn't Enough](https://www.blueprintsys.com/blog/your-business-requirements-document-isnt-helping)
- [ReBoot Co. — BRDs are no good](https://www.rebootco.com.au/blog/business-requirements-documents-are)
- [ailawyer.pro — BRD 2025 Legal/Strategic Must-Have](https://ailawyer.pro/blog/business-requirements-document-(brd)-the-legal-strategic-must-have-for-2025-projects)
- [Nuclino — How to Write a BRD](https://www.nuclino.com/articles/business-requirements-document)
- [Adaptive US — RACI Matrix Guide](https://www.adaptiveus.com/blog/raci-matrix/)
- [Business Analyst Learnings — RACI Matrix Guide](https://www.businessanalystlearnings.com/ba-techniques/2013/1/22/how-to-draw-a-raci-matrix)
