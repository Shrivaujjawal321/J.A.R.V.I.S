# Exemplars — the quality bar

This is what the drafting agents must match. Every passage below is at the level a real review
board accepts. Read the relevant section before drafting that section.

⚠️ **Scenario is fictional.** "Meridian Retail Bank — Consumer Loan Origination System
Replacement" is a **composite exemplar**, not a real company. Real complete corporate BRDs are
essentially never published (they carry commercially sensitive scope and cost data). This composite
is calibrated against real institutional templates (Stanford UIT, IIBA/Podeswa, BC Gov, CAISO) and
genuine verbatim fragments from BA training sources. **Replicate the structure and prose
discipline — never the numbers, names, or company.**

---

## Business Objectives (SMART)

> **OBJ-001 — Cycle-time reduction.** Reduce average consumer-loan origination cycle time
> (application-submitted to funds-disbursed) from 9.4 business days to 3.0 business days by end of
> Q2 FY27, measured monthly via the LOS pipeline-stage timestamp report, **without relaxing the
> current credit-risk score threshold (minimum 640 FICO)**.
>
> **OBJ-002 — Manual-touch reduction.** Reduce manual underwriter data-entry touches per
> application from an average of 14 to no more than 4 by Q3 FY27, measured via underwriter
> time-and-motion sampling (20 applications/month, sampled by Internal Audit).
>
> **OBJ-003 — Compliance exception reduction.** Reduce Regulation B adverse-action-notice
> timeliness exceptions from 6.2% of declined applications to below 1.0% by Q4 FY27, measured via
> the monthly Compliance exception report.

**Why this passes:** number, baseline, target, measurement method, data source, date — all present.
And OBJ-001 names its non-negotiable constraint *inline*. That's the move a CFO or risk officer
actually looks for: the objective proves it isn't going to trade one metric for a worse hidden one.

---

## Problem Statement (CFO-acceptable)

> Meridian's consumer Loan Origination System (LOS), implemented in 2014, requires underwriters to
> re-key applicant data across four disconnected systems (core banking, credit-bureau interface,
> decisioning engine, document management), averaging 14 manual touches per application. This drives
> an average origination cycle of 9.4 business days, against a market median of 2.1 days across
> three fintech competitors now active in Meridian's footprint (Competitor benchmarking study,
> Q1 FY26, Retail Banking Strategy).
>
> The cost of inaction is threefold. **Application abandonment:** 22% of applicants who start an
> application do not complete it; post-application exit surveys (n=340, Q4 FY25) cite "too slow /
> went elsewhere" in 61% of cases — an estimated $4.1M in annual foregone net interest income at
> current approval rates. **Compliance exposure:** manual re-keying has produced a 6.2% Regulation B
> adverse-action-notice timeliness exception rate over the trailing twelve months, flagged by
> Compliance as elevated risk ahead of the FY27 exam cycle. **Operating cost:** underwriting labour
> allocated to manual reconciliation is estimated at 3.8 FTE-equivalents annually ($430K fully
> loaded), duplicating data already captured at intake.
>
> This document defines the business requirements for replacing the manual-touch data flow; **it
> does not prescribe the replacement system's architecture or vendor.**

**Why this passes:** zero blame language, zero solution language, every claim carries a number and
an attributable source, and it closes by stating what the document is explicitly *not* deciding.

> **Practitioner note, from a real case:** an initial draft blamed a department for "duplicate
> processes and inconsistent data." A stakeholder objected. The fix was reframing entirely around
> **current state and cost of inaction** rather than fault. That is the register a CFO accepts.

---

## Scope — In / Out, with rationale

| # | In Scope | # | Out of Scope | Rationale for exclusion |
|---|---|---|---|---|
| IS-1 | Consumer unsecured personal loans ($1K-$50K) origination workflow | OS-1 | Auto loan and mortgage origination | Separate LOS platforms with independent FY27/28 roadmap; combining would delay Phase 1 by ~5 months |
| IS-2 | Intake, document capture, bureau pull, decisioning integration, funding hand-off | OS-2 | Core banking replacement or upgrade | Separate funded FY28 initiative (Project Anchor); this integrates via existing API, does not modify it |
| IS-3 | Underwriter workbench UI for the manual-review exception queue | OS-3 | Collections and servicing post-disbursement | Owned by the Servicing platform team; a separate BRD governs it |
| IS-4 | Reg B adverse-action-notice generation and timestamping | OS-4 | Marketing lead-gen front-end | Managed by Digital Channels on an independent CMS; only the API contract is in scope (see IS-2) |
| IS-5 | Migration of 24 months of in-flight and historical application data | OS-5 | Branch point-of-sale hardware refresh | Not a dependency; on an independent 5-year cycle |

**The rule:** every out-of-scope line states **why**, and where the work went instead. An
unexplained exclusion invites stakeholders to re-litigate scope six months later.

---

## Stakeholder Analysis + RACI

| Stakeholder | Role | Interest | Influence | RACI (Requirements sign-off) | RACI (UAT sign-off) |
|---|---|---|---|---|---|
| Priya Nandakumar, SVP Retail Lending | Business Sponsor | High — owns consumer lending P&L | High | **A** | C |
| David Osei, Chief Risk Officer | Risk oversight | High — credit-policy integrity | High | C | **A** |
| Meredith Voss, Head of Compliance | Regulatory oversight | High — Reg B exposure | High | C | C |
| Tom Achebe, VP Underwriting Operations | Process owner | High — daily workflow impact | Medium | R | R |
| Lena Fisk, Director IT Applications | Delivery accountable | High — build/integration ownership | High | R | **A** |
| Underwriting staff (12 FTE) | End users | High — direct workflow change | Low | I | R (participants) |
| Internal Audit | Control validation | Medium — SOX control mapping | Medium | I | I |

**Conventions that matter:** exactly one **A** per column, never two. **Two separate RACI columns**
because real BRDs have multiple sign-off gates and a stakeholder's role changes between them —
Priya is Accountable for requirements but only Consulted at UAT, because Lena owns delivery quality
at that gate. A single flat RACI for the whole document is a tell of shallow drafting.

---

## As-Is vs To-Be process

**Notation:** numbered steps grouped by swimlane (actor), numbered `<Phase>.<Step>`, cross-referenced
to a BPMN diagram in the appendix. **To-be mirrors as-is numbering 1:1** so a reviewer can diff them
side by side. This is the actual working convention senior BAs use.

**AS-IS — Application intake to decision** *(Applicant / Branch Staff / Underwriter / Bureau)*

1.1 (Applicant) Submits paper or PDF application at branch or via email.
1.2 (Branch Staff) Manually keys applicant data into core banking **and** separately into legacy LOS — **duplicate entry point #1**.
1.3 (Branch Staff) Manually initiates bureau pull via a separate portal; downloads PDF report.
1.4 (Underwriter) Re-keys bureau data points into a decisioning spreadsheet — **duplicate entry point #2**.
1.5 (Underwriter) Applies credit policy using a static decision-tree job aid (last updated 2019); flags exceptions for manager review.
1.6 (Underwriter) If approved, re-keys approved terms into core banking for disbursement — **duplicate entry point #3**.
1.7 (Branch Staff) Generates adverse-action notice from a Word template if declined; timestamp recorded manually in a shared spreadsheet — **root cause of the 6.2% Reg B exception rate**.

**TO-BE — Application intake to decision** *(Applicant / Digital Channel / New LOS / Underwriter)*

1.1 (Applicant) Submits via digital channel or assisted branch entry; **data captured once at source**.
1.2 (New LOS) Auto-pulls bureau report via API; normalizes fields into a single applicant record.
1.3 (New LOS) Applies configurable decision rules (same thresholds as today, config-managed by Risk, not hardcoded); auto-approves or auto-declines deterministic cases; routes ambiguous cases to the exception queue.
1.4 (Underwriter) Reviews only exception-queue cases (target ≤25% of volume) in one workbench; **no re-keying** — data pre-populated from 1.1/1.2.
1.5 (New LOS) On approval, pushes disbursement instruction to core banking via existing API.
1.6 (New LOS) On decline, auto-generates and auto-timestamps the adverse-action notice at decision time — closes the manual timestamp gap.

**Why this passes:** each as-is step names its specific failure and ties numerically back to the
problem statement's claims. "The current process is manual and slow" without that traceability
reads as generic.

---

## A properly-formed Business Requirement

> **BR-014** | **Priority: Must Have** | **Traces to: OBJ-002, OBJ-003** | **Source: Underwriting Operations workshop, 2026-03-11; confirmed by Tom Achebe**
>
> The solution shall auto-populate the underwriter exception-queue workbench with applicant data,
> credit-bureau results, and system-recommended decision rationale at the time an application enters
> the queue, such that an underwriter can complete review without re-entering any data field already
> captured in Steps 1.1-1.3 of the To-Be process.
>
> *Acceptance: AC-BR014. Not in scope: workbench visual design (separate UX spec, DES-014).*

Unique ID · explicit MoSCoW · **two** traceability links to numbered objectives (not "supports
project goals") · documented source with a **named confirmer** (auditable provenance) · testable
"shall" scoped to a specific process step · and an explicit line on what it does **not** cover.

That last line is the anti-creep device. Public vendor-blog templates almost never show
traceability IDs or sourcing — only the institutional lineage (Stanford, IIBA/BABOK) enforces it.

---

## Quantified NFRs

| ID | Category | Requirement | Target | Measurement Method |
|---|---|---|---|---|
| NFR-01 | Performance | Decision-engine response for auto-decisioned applications | p95 < 3s from data-complete to decision | APM tooling, under production load |
| NFR-02 | Availability | Platform uptime during business hours (7am-9pm, Mon-Sat) | ≥99.9% (≤43 min/month) | Uptime monitoring, monthly SLA report |
| NFR-03 | Scalability | Concurrent underwriter sessions without degradation | 150 concurrent at p95 <3s (NFR-01 held) | Load test pre-go-live; quarterly re-test |
| NFR-04 | Security | Applicant PII encryption | AES-256 at rest, TLS 1.2+ in transit, field-level for SSN | Annual penetration test + SOC 2 Type II |
| NFR-05 | Security | Access control | RBAC aligned to RACI; full audit trail of every field view/edit, retained 7 years | Quarterly access review by Internal Audit |
| NFR-06 | Compliance | Adverse-action notice generation | 100% of declines get a timestamped notice within 3 business days per Reg B §1002.9(a)(1) | Monthly Compliance exception report |
| NFR-07 | Data retention | Application data | Full record retained 25 months per Reg B; PII auto-purged beyond the window unless litigation hold | Automated retention job, quarterly governance audit |
| NFR-08 | Usability | Underwriter task completion | New underwriters (<30 days tenure) complete standard review in ≤6 min average, unassisted | UAT usability testing, n≥8, SUS ≥80 |

Every NFR has a **number, not an adjective**, plus a measurement method auditable independently of
the vendor's own claims. "Fast", "secure", "reliable" never appear unqualified.

---

## Assumptions Register

| # | Assumption | Owner | Validation Date | Impact if Wrong |
|---|---|---|---|---|
| A-01 | The core-banking disbursement API (v3.2) stays stable through go-live — no breaking changes from the parallel Project Anchor | Lena Fisk | 2026-04-15 (confirm with Anchor lead) | **High** — breaking change forces rework of the disbursement integration; ~6-week delay |
| A-02 | Bureau vendor can support real-time API pull for 100% of volume at the current contracted rate | Tom Achebe | 2026-04-30 | **Medium** — renegotiation could add $180K/yr run cost; wouldn't block go-live but changes the business case |
| A-03 | Underwriting headcount stays at 12 FTE through go-live; no attrition-driven training gap | Tom Achebe | Ongoing — monthly at steering committee | **Medium** — attrition during UAT could delay OBJ-002 by a quarter |
| A-04 | Reg B adverse-action-notice content requirements don't change materially before go-live | Meredith Voss | 2026-06-01 (re-confirm 90 days pre-go-live) | **High** — a rule change forces template rework and NFR-06 re-validation; tracked as R-04 |

Every assumption is **falsifiable** (someone can go check), has a **named owner** (not "IT"), a
**date** (not "TBD"), and states impact in terms of the objective or NFR it would break.

> **Why this discipline exists — real case:** a BRD assumed "all business units operate on the same
> enterprise network." It was wrong for two remote offices. Nobody owned validating it. The error
> surfaced weeks into design and doubled infrastructure cost.

---

## Risk Register

| ID | Description | P | I | Score | Mitigation | Owner |
|---|---|---|---|---|---|---|
| R-01 | Bureau API integration slips due to the vendor's own release schedule (outside our control) | 3 | 4 | 12 High | Written commitment + fallback SLA via contract amendment; build batch-pull fallback as contingency | Lena Fisk |
| R-02 | Underwriters resist the exception queue, keep shadow-using the legacy spreadsheet | 3 | 3 | 9 Med | Change-management plan with Tom as workflow champion; legacy access revoked at go-live (parallel run capped at 2 weeks) | Tom Achebe |
| R-03 | Auto-decision approval rate diverges from the manual rate in testing — rules miscalibrated | 2 | 5 | 10 High | 90-day parallel run with side-by-side comparison before auto-decisioning exceeds 25% of volume; Risk sign-off gate before threshold increase | David Osei |
| R-04 | Regulator changes Reg B notice content mid-build (linked to A-04) | 2 | 4 | 8 Med | Monitor the rulemaking calendar monthly; **build the notice template as configurable, not hardcoded**, specifically to absorb this cheaply | Meredith Voss |
| R-05 | Migration of 24 months of in-flight applications introduces record-matching errors | 3 | 3 | 9 Med | Dry-run in staging with full reconciliation; Internal Audit sign-off on ≥99.5% match rate before production | Lena Fisk |

P and I each 1-5, multiplied. Every mitigation is a **specific action with an owner** — and the
best ones are cheap because they were designed in (R-04's "configurable, not hardcoded" beats
"we'll deal with it if it happens"). Note the explicit **two-way link between R-04 and A-04**: a
mature BRD cross-references its own registers instead of treating them as disconnected boilerplate.

---

## Success Metrics

| Metric | Baseline | Target | Measurement Method | Measurement Date |
|---|---|---|---|---|
| Average origination cycle time | 9.4 business days | 3.0 business days | LOS pipeline-stage timestamp report, monthly | Q2 FY27 (first at 30 days post-go-live, then monthly) |
| Manual underwriter touches per application | 14 | ≤4 | Time-and-motion sample, 20 apps/month, Internal Audit | Q3 FY27 |
| Reg B timeliness exception rate | 6.2% | <1.0% | Monthly Compliance exception report | Q4 FY27, sustained 2 consecutive quarters |
| Application abandonment rate | 22% | 12% | Digital funnel analytics + branch intake log | Q3 FY27 |
| Underwriting labour on manual reconciliation | 3.8 FTE ($430K/yr) | ≤1.0 FTE ($115K/yr) | Finance FTE-allocation model | Q4 FY27 |

**The loop-closing test:** every number quoted as "cost of inaction" or "target" earlier in the
document reappears here with a measurement date. A success-metrics table that introduces **new**
numbers never seen earlier is a reliable tell of a stitched-together document.

---

## Acceptance Criteria — two altitudes

**Given/When/Then, at the individual requirement level** (maps 1:1 to a QA test case):

```
AC-BR014.1
  Given an application has been routed to the underwriter exception queue
  When the underwriter opens the application record
  Then all applicant data, bureau results, and decision rationale captured
       in Steps 1.1-1.3 are pre-populated, without manual re-entry

AC-BR014.2
  Given the underwriter modifies any pre-populated field during review
  When the modification is saved
  Then the system logs original value, new value, underwriter ID, and
       timestamp to the audit trail (per NFR-05)

AC-BR014.3
  Given an application has incomplete data from Step 1.2 (e.g. bureau pull failure)
  When the application enters the exception queue
  Then the system flags the specific missing field(s) rather than
       presenting a blank record
```

**Checklist, at the go-live/release level** (cross-cutting, ties to sign-off authority):

- [ ] BR-014 through BR-028 pass UAT with zero Critical/High defects open
- [ ] NFR-01 and NFR-03 confirmed under load test with production-representative volume
- [ ] NFR-06 validated by Compliance on 50 declined test applications, 100% pass
- [ ] Parallel run (R-03 mitigation) shows ≥98% auto/manual concordance on 500 applications
- [ ] Migration reconciliation (R-05) shows ≥99.5% match rate, signed off by Internal Audit
- [ ] All 12 underwriting FTE trained, post-training SUS ≥80 (NFR-08)
- [ ] Sign-off obtained from every "A" role in the UAT RACI column

Produce **both**. They are different altitudes and a BRD needs each.

---

## Cost-Benefit / Business Case

> **Investment:** $2.85M (build $2.1M over 14 months; change management and training $340K;
> 15% contingency $370K).
>
> **Annual run-rate:** $410K/yr for the new platform, vs $265K/yr for the legacy — **a net run-rate
> increase of $145K/yr.**
>
> **Quantified annual benefits (steady state from Q4 FY27):**
> - Reduced abandonment (10pp improvement): **$1.9M/yr** retained net interest income
> - Underwriting labour reallocation (2.8 FTE freed): **$315K/yr**
> - Avoided compliance-exception remediation (based on FY25 spend of $180K after the last exam finding): **$170K/yr**, conservative, net of residual risk
>
> **Total: $2.385M/yr. Net of run-rate increase: $2.24M/yr.**
>
> | Metric | Value |
> |---|---|
> | Total investment | $2.85M |
> | Payback period | 15.3 months from go-live |
> | 3-year net benefit | $6.87M |
> | 3-year ROI | 141% |
>
> **Unquantified benefits (excluded from the ROI above):** competitive positioning against fintech
> lenders; reduced exam risk profile; improved underwriter experience (Underwriting attrition runs
> 18% vs the 11% bank average, with exit interviews citing repetitive manual work).
>
> **Downside case:** if benefit realization is 30% below model and costs run 10% over, payback
> extends to ~22 months — still inside the 3-year evaluation horizon.

**Three things weak business cases skip:** separating **investment from run-rate** (and disclosing
that the new system costs *more* to run — a CFO will ask within 30 seconds); showing a **downside
case**; and **quarantining unquantified benefits** instead of inflating ROI with soft claims.

---

## Formatting conventions

**Prose:** Executive Summary · Problem Statement · Project Overview · As-Is/To-Be narrative (paired
with a table or diagram, never instead of one).

**Tables:** Scope · Stakeholders/RACI · Requirements · NFRs · Assumptions · Risks · Success Metrics ·
Document Control · Cost-Benefit.

**Hybrid** (numbered entry with structured sub-fields): individual requirement write-ups and
Given/When/Then blocks.

**Numbering:** decimal (`1`, `1.1`, `1.1.1`). Institutional templates all use it so requirements can
cross-reference precisely. Plain H2/H3 is fine under ~15 pages and breaks down past it.

**Document control block** on page 1, before the Executive Summary:

| Field | Value |
|---|---|
| Document Title | Business Requirements Document — Consumer LOS Replacement |
| Document ID | BRD-LOS-2026-001 |
| Version | 1.3 |
| Status | Draft / In Review / Approved |
| Author | [Name], Business Analyst |
| Business Sponsor | [Named person, title] |
| Date Created / Approved | 2026-02-10 / 2026-04-22 |

Followed by a **Change Log** (Version, Date, Author, Change, Approved By) and an **Approvals** table.
Every approver is a **named person with a date** — "IT" is not an approver.

**Length by initiative size:** small (single department) 5-10 pages · medium (cross-department)
15-25 · large (enterprise, regulatory) 30-60+, often core BRD plus separately-versioned appendices.

**Length tracks complexity, not effort-signalling.** Padding a small request into a 40-page document
is the single most common generator failure. Concision is itself a quality signal.

---

## MoSCoW discipline

- **Must have** — the initiative is not viable without it. If a Must fails, **the date moves**. Musts are not negotiable against schedule.
- **Should have** — important; a workaround exists but it hurts.
- **Could have** — desirable, low impact if dropped; first to be trimmed.
- **Won't have (this release)** — **the discipline point.** Explicitly scoped and dated, never
  silently dropped. It is a documented decision with a reason, which is precisely what prevents the
  "but I told you I needed this" argument six months later.

Default to MoSCoW with an explicit **"Won't Have (this release) — Rationale"** column. Alternatives:
High/Med/Low (common in government/waterfall procurement, but loses the Won't-have discipline unless
a "Deferred" category is added back); Kano and RICE exist but appear in no institutional template
surveyed — do not default to them.
