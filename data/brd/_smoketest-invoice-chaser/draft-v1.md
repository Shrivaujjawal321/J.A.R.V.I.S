# Business Requirements Document — Invoice Chaser (Smoke Test)

## Document Control

| Field | Value |
|---|---|
| Document Title | Business Requirements Document — Invoice Chaser (Smoke Test) |
| Document ID | BRD-INVOICECHASER-2026-001 |
| Version | 0.1 (Draft — first assembly) |
| Status | Draft |
| Author | Jarvis — Business Analyst Specialist (assembled from 5 parallel-drafted parts) |
| Business Sponsor | `[NEEDS INPUT: see STK-01 — ownership/sponsor identity (Boss's own product vs. client engagement vs. hypothetical) not yet confirmed]` |
| Date Created | 2026-07-29 |
| Readiness Score | `[NEEDS INPUT — a formal readiness-rubric scoring pass was not run in this assembly; see the Appendix note at the end of this document]` |

**Change Log**

| Version | Date | Author | Change | Approved By |
|---|---|---|---|---|
| 0.1 | 2026-07-29 | Jarvis (assembler) | Initial assembly of 5 parallel-drafted sections into one document: ID reconciliation across OBJ-/BR-/NFR-/ASM-/RSK-/CON- prefixes, complete Assumptions Register sweep, de-duplication of the data-protection requirement across §8/§10/§13/§14, §1 Executive Summary drafted, Document Control / §9 / Glossary / Sign-off skeleton added | `[NEEDS INPUT]` |

> **Note on this document's status.** This BRD was generated from a **one-sentence intake** ("freelancers ke liye ek tool jo unpaid invoices automatically chase kare") as a deliberate smoke test of the BRD-generation skill, not a real Boss request (see `intake.md`). It carries roughly 100+ `[NEEDS INPUT]` markers and 37 register-level `[ASSUMPTION]`s by design. That is not a defect in this draft — it is the honest output of thin input, structured so that every gap is visible and actionable rather than silently guessed. See §1 for what is and is not decided.

---

## 1. Executive Summary

This document was built from a single Hinglish sentence — "a tool for freelancers that automatically chases unpaid invoices" — with no interview, no existing-tool audit, and no numbers of any kind supplied. Per this skill's anti-fabrication rule, that means the document is honest about what it is: a **structured map of the decisions that must be made before a build can start**, not a set of approved requirements. Nothing in §2 (Objectives) or §15 (Metrics) carries a real baseline or target; every one carries a `[NEEDS INPUT]` in its place. The intake itself states a solution ("a tool that chases") without a validated problem — the Five Whys ladder in §3 gets one confirmed rung out of five, and the other four (root cause of non-payment, why existing invoicing tools' built-in reminders don't already solve this, the freelancer segment, the cost of inaction) are open.

What the document **does** deliver, and what would otherwise have taken a discovery workshop to surface: a hypothesised current-state process with pain points named at the exact failing steps (§6); a mirrored future-state process showing what closes each one (§7); nine business requirements with Gherkin acceptance criteria, the two highest-risk of which (client-override, stop-on-payment) are pre-flagged as non-negotiable Musts (§8); a 20-line non-functional and compliance surface identifying eight distinct regulatory trigger conditions — DPDP fiduciary/processor status, TRAI/TCCCPR sender-registration, GDPR, GST e-invoicing, PCI-DSS, and three more — every one of them a **trigger to confirm, not a finding** (§10); a stakeholder map that, unusually, treats the freelancer's own client as a first-class non-consenting stakeholder whose harm is tracked as a counter-metric (§5, KPI-03); a full risk register where the four highest-scored risks are all pre-build and none is fixed by building a better product (§14); and a cost-benefit structure that names the six inputs that gate a go/no-go decision without inventing any of them (§17).

**What is decided:** the document's structure, traceability, and the shape of the open-question set itself. **What is not decided:** whether this is Boss's own venture or a client/hypothetical engagement (blocks the entire sign-off chain, DEP-01), the target segment and jurisdiction, the root cause of non-payment (ASM-001, the premise the rest of the register sits on), the monetisation model, and every numeric threshold in the document. The single next action this document recommends, ahead of any build work: run the ASM-001 retrospective (§11) — an eight-freelancer interview round that is cheap, fast, and can independently kill or redirect the initiative before a line of code is written.

---

## 2. Business Objectives

Because §3 could not establish a validated baseline for any metric, the objectives below are structurally SMART (each names a direction, a proposed measurement method, and a trace to requirements and a KPI) but are **numerically incomplete by design** — a fabricated baseline or target would score as "complete" while being worthless. Read OBJ-001 through OBJ-004 as the exact list of data that must be collected before this BRD can go to sign-off, not as agreed targets.

> **OBJ-001 — Faster invoice collection.** Reduce the average number of days an invoice remains unpaid past its due date, for freelancers using the solution, from `[NEEDS INPUT: baseline days-overdue for the target freelancer segment — no current data supplied]` to `[NEEDS INPUT: target days-overdue and target date]`, measured via invoice due-date vs. payment-received-date, tracked monthly. **Traces to:** BR-001, BR-002, BR-005. **KPI:** KPI-01 (Days Sales Outstanding), KPI-02 (invoice collection rate), KPI-06 (chase-communication deliverability, enabling metric) — §15.

> **OBJ-002 — Reduced manual chasing effort.** Reduce the time a freelancer personally spends following up on overdue invoices, from `[NEEDS INPUT: baseline — no time-and-motion or survey data available]` to `[NEEDS INPUT: target]`, measured via `[ASSUMPTION: periodic in-app or survey-based self-report of time spent chasing, since no objective instrumentation of the freelancer's pre-tool manual process exists | conf: low]` (ASM-001, §11). **Traces to:** BR-002, BR-003, BR-009. **KPI:** KPI-04 (freelancer time saved) — §15.

> **OBJ-003 — Preserve the freelancer-client relationship while chasing.** Hold the rate of client friction attributable to automated chasing (e.g., a reminder sent after payment, a wrong-amount reminder, a client complaint about tone or frequency) at or below `[NEEDS INPUT: acceptable threshold — not defined by Boss]`, measured via `[ASSUMPTION: freelancer-reported incident log within the solution | conf: low]` (ASM-002, §11). **This objective is the initiative's non-negotiable constraint: automation must not increase net client friction relative to the freelancer's own prior manual chasing.** **Traces to:** BR-003, BR-004. **KPI:** KPI-03 (client-side harm signal — counter-metric) — §15.

> **OBJ-004 — Regulatory-safe automated client communication.** Ensure `[NEEDS INPUT: 100%, or an owner-defined percentage]` of automated chase communications comply with applicable data-protection and commercial-communication law in the jurisdiction(s) of both freelancer and client — provisionally scoped to India's DPDP Act 2023, `[ASSUMPTION: target market is India-based freelancers and India-based or India-serving clients, consistent with the commissioning context; not confirmed by Boss | conf: low]` (ASM-003, §11) — measured via `[NEEDS INPUT: compliance audit method, cadence, and named owner not yet defined]`. **Traces to:** BR-006, BR-008. **KPI: `[NEEDS INPUT — genuine orphan, see assembly-report.md]`.** No metric in §15's current set measures compliance directly; §15's six KPIs all measure collection or relationship outcomes. This is a real gap in the requirement set's downward completeness, not an oversight this assembly is silently patching — a compliance-audit-pass-rate KPI would need to be proposed and validated with STK-04, not invented here.

---

## 3. Background / Problem Statement

**Five Whys — traceability of the stated need**

1. **WHY build this tool?** → Because freelancers need unpaid invoices chased automatically.
   *Known — verbatim intake: "freelancers ke liye ek tool jo unpaid invoices automatically chase kare."*
2. **WHY do freelancers need invoices "chased" at all?** → Because client invoices are not being paid by an agreed due date, i.e., invoices go overdue.
   `[ASSUMPTION: this is a direct, low-risk reading of the plain meaning of "unpaid invoices" in the intake — the existence of overdue invoices, not a specific rate or cause of them | conf: high]` (ASM-004, §11)
3. **WHY are client invoices going overdue** — what is the actual root cause? Candidates: the client forgot; the client is disputing the amount or the delivered work; the client has their own cash-flow problem; the client's own accounts-payable process has no reminder step; or the client is deliberately delaying because the freelancer has limited leverage to enforce payment terms.
   `[NEEDS INPUT: Boss has not specified the dominant root cause. This is not a formality — a "forgot" problem is solved by a reminder; a "disputing the invoice" or "client has no cash" problem is not, and a reminder aimed at the wrong root cause can actively damage the freelancer-client relationship (see OBJ-003).]` — this is the same open question the risk register tracks as **ASM-028 / RSK-005** (§11, §14); resolving it is the single highest-leverage pre-build action on this whole document.
4. **WHY is the freelancer's current manual chasing process insufficient** — time cost, inconsistency, avoidance/awkwardness around asking a client for money, no visibility into which invoices are actually overdue, or something else?
   `[NEEDS INPUT: no baseline exists on current freelancer behaviour, time spent chasing, or the emotional/relationship cost of chasing today.]`
5. **WHY hasn't this already been solved** — most invoicing platforms already used by freelancers (generalist accounting/invoicing SaaS) ship built-in payment-reminder features. What does this tool do that those don't, and for which freelancers specifically?
   `[NEEDS INPUT: the single largest open gap in this intake. Without an answer, this BRD cannot establish whether the initiative is a net-new product, a competitive-parity feature, or a fix for an underserved sub-segment (e.g., freelancers invoicing outside any formal tool, via email/WhatsApp/manual PDF).]` — tracked as **RSK-001** (§14).

Only rung 1 is directly sourced. Rung 2 is a safe, low-risk inference. Rungs 3-5 are open and, per the anti-fabrication rule, are **not** answered with an invented root cause anywhere in this document.

**Problem Statement**

What is known, stated without invented numbers: freelancers — read here as solo-operators, per the initiative's classification — currently carry unpaid client invoices, and currently chase payment on those invoices through some unspecified manual process (verbatim intake). No baseline exists in the intake for how many invoices go overdue, by how much, how often, for which freelancer sub-segment, or what the current manual chasing process actually consists of.

- `[NEEDS INPUT: freelancer segment definition — geography, discipline/vertical, typical invoice size, typical client type (business vs. individual), and whether the segment already uses an invoicing tool today.]`
- `[NEEDS INPUT: quantified baseline — average days overdue, % of invoices that go overdue, average manual time spent per week chasing, and the source/method by which any of these would be measured.]`
- `[NEEDS INPUT: cost of inaction — what a freelancer actually loses when an invoice goes unpaid or late (cash-flow gap, real bad-debt/write-off rate, time cost, stress/opportunity cost) is not stated and is not assumed here.]`
- `[NEEDS INPUT: competitive baseline — which invoicing/reminder tools freelancers in the target segment already use, and specifically why those are judged insufficient, if they are.]`

Cost of inaction cannot be quantified from the intake supplied. A responsible BRD does not assert a dollar figure, an abandonment rate, or a compliance-exception rate when none exist to cite — inventing one to make this section "complete-looking" would be the exact failure this document is designed to avoid. That gap is itself the primary finding of this section: **the intake states a solution ("a tool that chases") without a validated problem.** The objectives in §2 are consequently structural placeholders pending the inputs listed above, not approved targets.

**This document does not decide:** the communication channel(s) used to chase (email/SMS/WhatsApp/voice), the tone or escalation script, the specific invoicing/accounting platform this integrates with (if any), or the pricing/business model of the tool itself. Those are FRD/product decisions, and several of them are contingent on the root-cause and segment answers still outstanding above.

---

## 4. Project Scope

Two scope-defining questions are still open and are listed as `[NEEDS INPUT]` below rather than silently resolved onto either side of the line — placing them on one side without an answer would misrepresent a decision as already made.

| # | In Scope (Release 1) | MoSCoW | # | Out of Scope (Won't Have, this release) | Rationale for exclusion |
|---|---|---|---|---|---|
| IS-1 | Track payment status (paid / unpaid / overdue) for invoices the freelancer has already issued | Must | OS-1 | Creating or generating the invoice itself | Distinct, mature capability already served by existing invoicing tools; combining would roughly double build scope for a segment that plausibly already issues invoices some other way `[ASSUMPTION: target freelancers already issue invoices through some existing means — own tool, template, or accounting software — before ever reaching this product | conf: med]` (ASM-005, §11) |
| IS-2 | Send automated, freelancer-configured reminder messages to the client as an invoice ages | Must | OS-2 | Collect or process the payment itself (card/bank funds movement) | Money movement pulls PCI-DSS and payment-licensing obligations into scope (see NFR §10.1 CMP-F, CMP-G); the intake's word "chase" is read here as communication, not funds collection — that reading is itself unconfirmed, see NI-1 |
| IS-3 | Escalate message tone/frequency on a configurable schedule as an invoice's days-overdue count increases | Should | OS-3 | Legal escalation / third-party debt-collection agency handoff | Separate regulated domain (recovery-agent licensing varies by Indian state); this release stops at surfacing the invoice for the freelancer's own next step, see To-Be step 1.6 |
| IS-4 | Let the freelancer pause, edit, or manually trigger an off-cycle message, overriding the automated cadence | Should | OS-4 | Full accounting / bookkeeping / GST e-invoicing | Distinct regulated domain; GST e-invoicing applies only above Rs 5cr annual turnover `[ASSUMPTION: not applicable to the target solo/micro-freelancer segment | conf: med]` (ASM-006, §11) — confirmed only once NI-2 (target segment) is answered. See also §10.2 CMP-E. |
| IS-5 | Give the freelancer a basic outstanding-amount / aging-bucket view across all tracked invoices | Could | OS-5 | Multi-currency / cross-border invoicing | Target geography is undetermined (NI-2); scoping currency handling now would be guessing rather than deciding |
| | | | OS-6 | Cross-user payment-reputation features — shared defaulter lists, a public score, cross-user warnings, or any feature that shares a client's payment behaviour beyond the user who entered it | Not in the intake; flagged at assembly as the natural next feature after IS-1/IS-5, and the compliance jump is discontinuous — such a feature leaves the Data Processor posture entirely (§10.2 CMP-A) and raises credit-information and defamation questions on top of the DPDP surface already in scope. Recorded here explicitly so it cannot arrive later as an unreviewed enhancement (source: §10.2 CMP-H). |

**Open boundary decisions — genuinely undecided, not placed on either side:**

- `[NEEDS INPUT: NI-1]` Does "chase" ever extend to the tool detecting that a payment was received
  (even without moving funds itself) — and if so, is that detected automatically (bank/payment-gateway
  signal) or marked manually by the freelancer? This changes whether IS-1 is a pure manual-entry
  status log or has an integration dependency, and it is the fact that determines whether OS-2 stays
  safely excluded. Cross-references DEP-05 (§12) and NFR-003 (§10).
- `[NEEDS INPUT: NI-2]` Is the target market India-only freelancers, or global? This determines the
  compliance frame (DPDP alone vs. DPDP + GDPR — see §10.2 CMP-D), whether OS-5 (multi-currency) should really be a
  Release-2 Should rather than an outright exclusion, and whether the GST-e-invoicing assumption
  under IS-4/OS-4 holds. Same open question as ASM-002/ASM-020 (§11).
- `[NEEDS INPUT: NI-3]` Does invoice data enter this product by manual entry, file import, or a live
  integration with an existing invoicing/accounting tool the freelancer already uses? This is a
  scope-defining boundary for IS-1 and cannot be safely assumed either way — it changes both the
  build shape and OS-1's "we don't touch invoice creation" boundary (an integration still means
  reading someone else's invoice data, which is a data-sharing/DPDP question in its own right).

---

## 5. Stakeholder Analysis + RACI

**Before the table — one unresolved question that determines everything below it:**

> `[NEEDS INPUT: Is this (a) Boss's own product with Boss as Business Sponsor, (b) a client
> engagement where a named external client company is the sponsor, or (c) a hypothetical/portfolio
> exercise with no real sponsor? The Business Sponsor row, the escalation path, and the entire
> "Requirements sign-off" column are unassignable to a real name until this is answered — assigning
> a placeholder person here would be inventing a stakeholder, which this document does not do.]`
> This is **DEP-01** (§12) — the single most-blocking open item in the whole document.

**The stakeholder structure itself is non-standard and must not be flattened.** This product has
two people on the receiving end of its core action, and they are not aligned:

- The **freelancer** is the buyer and the primary user. They benefit directly — this is the
  demand side of the tool.
- The freelancer's **client** (the payer, "the recipient of automated chasing") is the object of
  the tool's core action and is a first-class stakeholder in risk terms even though they are
  **not a project participant, were never asked to opt in, and have no product relationship with
  the vendor.** A stakeholder table that lists only "freelancer" and "admin" would silently erase
  the one relationship the entire product depends on not damaging. Automated, unconsented
  collection-style contact toward this party is the single largest source of reputational, legal,
  and churn risk in this initiative — see §10.2 CMP-B/C, §13 CON-05, and §14 RSK-002/007/012 — and
  it must be visible here even though it carries no RACI role.

| STK-ID | Stakeholder | Role | Interest | Influence | RACI (Requirements sign-off) | RACI (UAT / launch-readiness sign-off) |
|---|---|---|---|---|---|---|
| STK-01 | `[NEEDS INPUT: name — Business Sponsor]` | Business Sponsor / Product Owner | High — owns the business case and the go/no-go decision | High | **A** | C |
| STK-02 | Freelancer (solo-operator, target ICP) | Primary user & buyer | High — direct beneficiary; wants unpaid invoices collected without spending personal time or damaging the client relationship themselves | Low (no formal governance seat; influences roadmap only via research/beta feedback) | C | R (beta participant) |
| STK-03 | Freelancer's client / invoice payer | **Non-opted-in recipient of the product's core automated action** ("the chased party") | High and **structurally opposed** to STK-02's interest on cadence/tone — wants to not be nagged, not have the business relationship soured, not be contacted by something that reads as a collections process | None (has no seat, was never consulted) — but is the primary source of downstream risk (complaint, relationship loss, legal exposure) that can force a redesign | N/A — not a governance participant by definition | N/A — not a governance participant by definition |
| STK-04 | `[NEEDS INPUT: name — Legal / Compliance reviewer]` | Compliance oversight — DPDP Act 2023 (processing the client's personal data: name, email, phone, invoice/payment history) and review of chase-communication content for anything that reads as unlicensed debt-collection conduct (see §10.2 counsel handoff list) | High — a single mishandled chase sequence is a legal/reputational incident, not a bug | Medium–High | C | C |
| STK-05 | `[NEEDS INPUT: name — Engineering / Delivery owner]` | Delivery accountable | High | High | R | **A** |
| STK-06 | Freelancer's bookkeeper/accountant `[ASSUMPTION: some share of the target segment uses a third-party bookkeeper who also touches invoice status | conf: low]` (ASM-007, §11) | Secondary/indirect user | Low–Medium | Low | I | I |

**Escalation path:** `[NEEDS INPUT: who has authority to resolve a tone/frequency dispute between
the freelancer's collection goal (STK-02) and client-relationship risk (STK-03's downstream effect
on churn/complaints/legal exposure)? In the exemplar bank BRD this sits with the Business Sponsor;
here it cannot be assigned until STK-01 is named.]`

**Convention check:** exactly one **A** per column, both currently held by `[NEEDS INPUT]` seats —
correct, since inventing a named accountable person would violate the no-fabrication rule more than
leaving the seat visibly open.

---

## 6. Current State (As-Is) Process

**Status of this section: hypothesised, not observed.** No freelancer interview, time-and-motion
study, or workshop has taken place. Every step below is tagged `[ASSUMPTION]` at the confidence the
underlying claim plausibly deserves for the freelance-services segment generally — none of it is
specific to a named freelancer, tool, or dataset. Where a fact is not safely assumable at all — because
it requires seeing the actual behaviour, not just describing a plausible pattern — it is flagged as
`[NEEDS INPUT / requires observation or interview]` rather than guessed.

**Swimlanes: Freelancer · Client**

1.1 (Freelancer) Issues an invoice to the client, stating an amount and a due date `[ASSUMPTION: invoices are issued with an explicit due date, as is standard freelance-services practice | conf: high]` (ASM-008, §11).

1.2 (Freelancer) Tracks which outstanding invoices are approaching or past their due date `[ASSUMPTION: this tracking is informal — memory, a spreadsheet, or scanning a bank statement — rather than a dedicated system, since the intake proposes building one from scratch | conf: low]` (ASM-009, §11). **Pain point:** no forcing function surfaces an overdue invoice; detection depends entirely on the freelancer happening to check. *(Closed by To-Be 1.2, BR-001.)*

1.3 (Freelancer) Notices — or fails to notice in a timely way — that an invoice has gone overdue. **Pain point:** detection latency is itself unmeasured `[NEEDS INPUT / requires observation: how many days typically elapse between due date and the freelancer first noticing]`. *(Closed by To-Be 1.3, BR-001.)*

1.4 (Freelancer) Decides whether and when to send a follow-up, and drafts that message individually each time `[ASSUMPTION: messages are composed fresh per instance rather than from a saved template, and timing is ad hoc rather than on a fixed cadence | conf: low]` (ASM-010, §11). **Pain point:** the decision to chase competes against `[ASSUMPTION: reluctance to jeopardise the client relationship, a commonly cited reason freelancers under-chase — plausible for this segment but not confirmed for this engagement | conf: med]` (ASM-011, §11); the effort and discomfort of this step are candidates for the actual root cause behind "invoices go unpaid," but that causal claim is unverified — same open question as §3 rung 3, ASM-028, RSK-005. *(Closed by To-Be 1.4, BR-002/BR-003.)*

1.5 (Client) Responds and pays, or does not respond; if not, the process loops back to 1.3/1.4 on an ad hoc basis, with no defined interval or count for how many follow-ups are attempted before the freelancer gives up. **Pain point:** the loop has no structure — cadence, channel, and escalation are entirely freelancer-dependent, so outcomes vary case by case rather than following a repeatable pattern. *(Closed by To-Be 1.5.)*

1.6 (Freelancer) Eventually is paid, writes the amount off, or escalates informally (e.g. a phone call, or involving a third party) `[ASSUMPTION: no formal escalation path or defined "close" state exists today | conf: low]` (ASM-012, §11). **Pain point:** there is no explicit end state — an unresolved invoice can drift indefinitely rather than being surfaced for a deliberate decision. *(Closed by To-Be 1.6.)*

**What this section cannot responsibly resolve by further Q&A** — these require either a discovery
workshop, freelancer interviews, or direct observation of an actual chase cycle, not a question Boss
can answer from memory alone:

- Invoice volume and overdue rate (how many invoices a typical target freelancer issues per month, and what fraction go overdue) — same input NFR-005 (§10) needs.
- Actual time spent per week on chasing, and the actual channel mix used (email vs. WhatsApp vs. phone vs. platform messaging)
- The real distribution of days-overdue-to-resolution, and how many follow-ups it typically takes
- Whether relationship-risk hesitation (1.4) is in fact the dominant driver of non-payment, versus e.g. client cash-flow problems, disputed scope, or simple forgetfulness — these have different fixes and cannot be told apart without qualitative input. **This is exactly what ASM-028's retrospective (§11) is designed to answer.**
- What tool(s), if any, freelancers already use today for invoicing or tracking (feeds directly into NI-3 in §4)

---

## 7. Future State (To-Be) Process

Mirrors §6's numbering 1:1. Written at business-process level — it states what capability closes each
As-Is pain point, not which screen, database, or integration delivers it.

**Swimlanes: Freelancer · Client · Product (automated capability)**

1.1 (Freelancer) Issues an invoice to the client with a due date, as today; that invoice and due date become trackable by the product from the moment it is created — mechanism (manual entry vs. import vs. integration) is undecided, see §4 NI-3. `[Stakeholder Requirement — solution TBD in FRD]`

1.2 (Product) Automatically monitors due dates and identifies an invoice as overdue without requiring the freelancer to check — **closes the 1.2 pain point** (no forcing function). *Delivered by BR-001.*

1.3 (Product) Automatically detects the overdue state at the moment it occurs and triggers the chase workflow — **closes the 1.3 pain point** (detection no longer depends on the freelancer noticing). *Delivered by BR-001, BR-002.*

1.4 (Product, with Freelancer override) Sends a follow-up message to the client on a freelancer-configured cadence and tone, with tone/frequency escalating as days-overdue increases; the freelancer retains the ability to pause, edit, or send an off-cycle message manually rather than being fully hands-off — **closes the 1.4 pain point** (removes the per-instance composition burden) while `[ASSUMPTION: preserving freelancer override addresses the relationship-risk hesitation identified at 1.4, rather than removing the freelancer's judgment entirely | conf: med — this is the product's central bet, and it rests on an unconfirmed root cause]` (ASM-013, §11). *Delivered by BR-002, BR-003, BR-005.*

1.5 (Client / Product) Client responds or pays; the product captures the resulting payment-status update — **closes the 1.5 pain point** (the follow-up loop now runs on a defined, repeatable cadence instead of ad hoc timing). Whether status capture is automatic or freelancer-marked is still open (§4 NI-1). *Delivered by BR-004; depends on DEP-05.*

1.6 (Product) For an invoice that remains unpaid past the top of the configured escalation ladder, the product surfaces it as needing the freelancer's own next decision (write off, informal escalation, or handoff outside the tool per §4 OS-3) — **closes the 1.6 pain point** (drift becomes an explicit decision point instead of an undefined state). *Delivered by BR-009.*

**Delta — what changes and why:**

- Detection moves from freelancer-memory-dependent (1.2, 1.3) to automatic — removes the single point of failure the As-Is process has no backup for.
- Chase timing moves from ad hoc, effort-and-mood-dependent (1.4) to a configurable, repeatable cadence — while deliberately keeping a manual override, because the hypothesised root cause (relationship-risk hesitation) is a judgment call the freelancer plausibly still wants to make on individual clients.
- The process gains a defined end state (1.6) where none existed before — turns silent drift into a decision the freelancer is prompted to make.

**Implementation considerations:**

- **Change management:** the freelancer is trusting the product to send messages to their own clients under their name — this is a relationship-risk transfer, not just a workflow change, and (per 1.4) is the step most likely to need a review-before-send option rather than fully autonomous sending. This is a design lean, not a decided requirement.
- **Training:** limited to a one-time cadence/tone configuration per freelancer; no ongoing training burden is implied by anything confirmed so far.
- **System/integration dependency:** the entire shape of 1.1-1.2 depends on §4's NI-3 (manual entry vs. import vs. integration); this should be resolved before any solution design proceeds, since it changes both build effort and DPDP-relevant data-handling scope (reading a third party's invoicing data on the freelancer's behalf).

---

## 8. Business Requirements

No stakeholder elicitation session has occurred against this intake — every requirement below is inferred from a single unelaborated sentence. Source is therefore marked per-row as either the intake statement directly, or a flagged assumption/needs-input where the requirement required inference beyond it.

| ID | Requirement | Traces to | Priority | Source | Acceptance |
|---|---|---|---|---|---|
| BR-001 | The solution shall identify, without manual flagging by the freelancer, which invoices have passed their stated due date and remain unpaid. | OBJ-001 | Must | Intake, verbatim (a precondition of "chasing unpaid invoices") | AC-BR001 |
| BR-002 | The solution shall initiate contact with the client on an overdue invoice automatically, without the freelancer manually triggering each individual follow-up. | OBJ-001, OBJ-002 | Must | Intake, verbatim ("automatically chase") | AC-BR002 |
| BR-003 | The freelancer shall be able to pause, stop, or override automated chasing for any specific invoice or client, at any time before or during the chase sequence. | OBJ-002, OBJ-003 | Must | `[ASSUMPTION: inferred as necessary to protect ongoing/repeat-client relationships, a common characteristic of solo-operator freelance work; not stated in intake | conf: med]` (ASM-014, §11) | AC-BR003 |
| BR-004 | The solution shall stop chasing an invoice, and shall not send any further reminder for it, as soon as that invoice is recorded as paid. | OBJ-003 | Must | `[ASSUMPTION: chasing a client after payment is a known failure mode in this product category and would directly work against OBJ-003 | conf: med]` (ASM-015, §11) | AC-BR004 |
| BR-005 | The solution shall support more than one escalation stage for a single overdue invoice (e.g., an earlier-stage reminder distinct from a later-stage one), rather than a single repeated message. | OBJ-001 | Should | `[ASSUMPTION: common practice in payment-reminder products generally; not confirmed by Boss | conf: low]` (ASM-016, §11) | AC-BR005 |
| BR-006 | The solution shall handle all client and invoice data — including any client personal data (name, contact details, payment status) — in accordance with applicable data-protection law for the jurisdiction(s) in which the freelancer and their clients operate. | OBJ-004 | Must | Classification-supplied compliance candidate (DPDP Act 2023); `[NEEDS INPUT: confirm target jurisdiction(s) — DPDP Act 2023 (India) is the working assumption, not confirmed by Boss]` | AC-BR006 |
| BR-007 | The solution shall maintain a record of every automated chase action taken against an invoice (what was attempted and when), retrievable by the freelancer. | OBJ-002, OBJ-003 | Should | `[ASSUMPTION: inferred as necessary for the freelancer to defend against a client dispute over chasing conduct, and to make BR-004's "stop on payment" behaviour auditable | conf: med]` (ASM-017, §11) | AC-BR007 |
| BR-008 | The solution shall obtain and record freelancer confirmation that automated communication to a given client is permitted, before that client is contacted automatically for the first time. | OBJ-004 | Must | `[NEEDS INPUT: whether client-side consent/notice is legally required depends on the communication channel and jurisdiction, neither of which is decided; scoped conservatively to Must pending confirmation of India IT Act 2000 / sector consent obligations for commercial electronic communication | conf: low]` | AC-BR008 |
| BR-009 | The freelancer shall be able to see the current chase status (not yet due / overdue / in active chase / paused / paid) of every outstanding invoice in one consolidated view. | OBJ-002 | Should | `[ASSUMPTION: baseline usability need for OBJ-002 — reducing chasing effort implies the freelancer can see status without re-deriving it manually | conf: med]` (ASM-018, §11) — `[Stakeholder Requirement — solution TBD in FRD]` | AC-BR009 |

**De-duplication note — BR-006.** BR-006 is the **single canonical statement** of this initiative's data-protection obligation. Three sibling sections restate closely related content and now cross-reference this row instead of repeating it: **NFR-006** (§10) sets the specific safeguard standard and citation (DPDP §8(5), Rule 6) that operationalises BR-006 at the business-quality-target tier; **CON-04** (§13) states DPDP Act 2023 applicability as an external regulatory fact, not a requirement; **RSK-007** (§14) analyses the exposure if BR-006/NFR-006 are not met. Do not add a fifth restatement anywhere else in the document — link to BR-006.

**Expanded form — the two highest-risk requirements**

> **BR-003** | **Priority: Must Have** | **Traces to: OBJ-002, OBJ-003** | **Source: `[ASSUMPTION | conf: med]`** (ASM-014, §11), not directly stated in intake
>
> The freelancer shall be able to pause, stop, or override automated chasing for any specific invoice or client at any time before or during the chase sequence, such that no further automated contact is sent once paused or stopped.
>
> *Acceptance: AC-BR003. Not in scope: the specific control surface (button, setting, command) used to pause/stop — that is an FRD/UX decision.*
> *Why Must, not Should: without an override, an automated chase system removes exactly the judgment a freelancer currently exercises manually — this is the single largest relationship-risk in the entire initiative (see OBJ-003), and it cannot be a later add-on.*

> **BR-008** | **Priority: Must Have** | **Traces to: OBJ-004** | **Source: `[NEEDS INPUT: jurisdiction and channel unconfirmed]`**
>
> The solution shall require and record freelancer confirmation that automated contact to a given client is permitted before the first automated chase message to that client is sent.
>
> *Acceptance: AC-BR008. Not in scope: the legal sufficiency of any specific consent mechanism — that determination requires the jurisdiction/channel inputs flagged in §3 and BR-006, and is `[NEEDS INPUT]` for legal review before build. See §10.2 CMP-B, CMP-C C-3, and the counsel handoff list at the end of §10.*

---

## 9. Functional Requirements Boundary

Detailed functional requirements are out of scope for this document and will be maintained in the companion FRD. This BRD defines business need and outcome only. Where a business requirement above is genuinely at the boundary between business capability and solution shape (e.g. BR-009's status view), it is tagged `[Stakeholder Requirement — solution TBD in FRD]` rather than specified further here.

---

## 10. Non-Functional Requirements

> **Scope note.** This section identifies **regulatory surface and the controls it demands**. It states no
> legal conclusion and is not legal advice. Applicability questions are written as **trigger conditions
> to confirm or rule out** with qualified counsel — not as findings.

**Reading the tags.** The intake was one sentence with no volume, geography, channel or SLA data.
Numeric targets appear only where a regulation fixes them (three places: CGST §36 · Income-tax Rule
6F(5) · DPDP Rules 2025 Rule 7). Every other target is left open by design — a plausible-sounding
invented threshold would score well on a rubric and mislead delivery.
Status: **[R]** resolvable here · **[C]** counsel must confirm · **[B]** sponsor input needed.

| ID | Category | Requirement | Target | Measurement | Driver / Traces to | Status |
|---|---|---|---|---|---|---|
| NFR-001 | Availability | Each scheduled chase shall execute **exactly once** per schedule instance; recovery from interruption shall not re-send a chase already dispatched | Zero duplicate dispatches per invoice per step | Dispatch log reconciled to schedule ledger, monthly | Duplicate-chase is a client-conduct harm, not just a defect (OBJ-003) | Must [R] |
| NFR-002 | Availability | Service availability during the daily send window | `[NEEDS INPUT: uptime commitment — and is a missed send window materially worse than UI downtime?]` | Uptime monitoring, monthly | **OBJ-001** *(assembly link: a missed send window directly delays the collection-speed objective; see assembly-report.md for reasoning)* | Must [B] |
| NFR-003 | Performance | Lag from payment recorded → **suppression of the next scheduled chase** | `[NEEDS INPUT: max acceptable lag]` | Timestamp delta, sampled monthly | Chasing a client who already paid is the product's highest-salience failure (OBJ-003, BR-004) | Must [B] |
| NFR-004 | Performance | Interactive response, user-facing screens | `[NEEDS INPUT: is interactive speed a stated business concern at all, or is this a background-batch product where only NFR-003 matters?]` | APM under representative load | **OBJ-002** *(assembly link: interactive lag on the freelancer's own status view is itself manual-effort burden; see assembly-report.md)* | Should [B] |
| NFR-005 | Scalability | Sustained and peak dispatch volume absorbed without breaching NFR-001/003 | `[NEEDS INPUT: invoices per user, clients per user, users at 12 months]` | Load test at agreed peak multiple, pre-launch + quarterly | See ASM-019 (§11): volume concentrates at month-end/FY-end, conf: med | Must [B] |
| NFR-006 | Security | Personal data of users **and their clients** protected by the safeguards required of a Data Fiduciary | Per DPDP Act 2023 §8(5) and DPDP Rules 2025 Rule 6 `[confirm sub-clauses + phased commencement]` | Independent assessment pre-launch, annual after | DPDP §8(5); Schedule penalty up to ₹250 cr `[verify current Schedule]`. Operationalises **BR-006** (§8) — see the de-dup note under §8. Depends on the CMP-A Fiduciary/Processor determination below. | Must [C] |
| NFR-007 | Security | Tenant isolation — no user may access, infer or export another user's client list or invoices | Zero cross-tenant access | Cross-tenant test suite; quarterly access review | The client list *is* the freelancer's commercial asset | Must [R] |
| NFR-008 | Security | Vendor staff access to client data authenticated, role-limited, logged, and **visible to the affected user** | 100% of staff access logged and user-visible | Quarterly sampling vs AUD-005 | DPDP §8(5); makes the Processor posture inspectable rather than asserted | Must [R] |
| NFR-009 | Compliance | Ability to produce the facts required for statutory breach reporting inside the statutory window | Intimation without delay, detailed report within **72 hours** of awareness — DPDP Rules 2025 Rule 7 (notified 13 Nov 2025) | Tabletop breach exercise pre-launch, annual | DPDP §8(6), penalty up to ₹200 cr. **If EU trigger fires: GDPR Art. 33, also 72h** | Must [C] |
| NFR-010 | Compliance | A written processing contract in force before any client personal data is processed | 100% of accounts, prior to first import | Account-provisioning control test | DPDP §8(2) — a Fiduciary may engage a Processor **only under a valid contract** | Must [C] |
| NFR-011 | Compliance | Chase conduct — sender identity, basis, opt-out, frequency, timing per channel and jurisdiction | Per §10.2 | Per §10.2 | See §10.2 | Must [C] |
| NFR-012 | Retention | Platform retention/erasure shall not destroy records the **user** is statutorily required to keep | Per §10.3 RET-001 | Retention-job audit, quarterly | CGST Act 2017 §36 · Income-tax Rules 1962 r.6F(5) | Must [R] |
| NFR-013 | Retention | Client personal data erased once its purpose is no longer served; erasure propagates to backups and derived stores | `[NEEDS INPUT: erasure window and backup-propagation window]` | Erasure job log + quarterly sample | DPDP §8(7) + DPDP Rules 2025 Rule 8 | Must [B] |
| NFR-014 | Retention | A record that a client objected or opted out shall **survive** erasure of that client's other data | Suppression enforced post-erasure, in minimised form | Erase a record, then attempt a chase to the same identifier — must be blocked | Erasing the opt-out with the record re-enables the very contact the client refused. *Tension with NFR-013 — see RET-004* | Must [C] |
| NFR-015 | Auditability | Every outbound chase, suppression, erasure job and staff access evidenced | Per §10.4 | Per §10.4 | Dispute defence + conduct evidence | Must [R] |
| NFR-016 | Auditability | Audit trail tamper-evident and retained ≥ the longest-lived record it evidences | Per RET-007 | Integrity check, quarterly | Cross-links NFR-008, NFR-012, NFR-015 | Must [R] |
| NFR-017 | Localization | Where a privacy notice is shown to an Indian Data Principal, the option to access it in English or a Constitution Eighth Schedule language is available | Option present at every notice surface | Inspection at each notice point | DPDP Act 2023 §5(3) | Must [C] |
| NFR-018 | Portability | Users can export their own invoice and client records on demand and at account closure | Self-serve, no vendor intervention | Export test | **Asymmetry:** DPDP grants no general portability right; GDPR Art. 20 does. Commercial commitment under DPDP-only scope, regulatory if the EU trigger fires | Should [R] |
| NFR-019 | Usability | A user can see what is scheduled to go to which client, and stop it, without support contact | `[NEEDS INPUT: task success target, n]` | Usability testing at UAT | An automation the user cannot see or halt is how conduct risk becomes real (BR-003, BR-009) | Must [B] |
| NFR-020 | Accessibility | Conformance level for user-facing surfaces | `[NEEDS INPUT: does the sponsor commit to a standard, and does any Indian statutory accessibility duty apply to this service?]` | Accessibility audit pre-launch | — | Should [B] |

### 10.1 Categories considered and judged not applicable

| Category | Verdict | Reason |
|---|---|---|
| Maintainability | Not stated at BRD level | Below the business/solution boundary (BABOK Tier 3) — belongs in the FRD |
| Interoperability | Deferred | Depends on whether the tool is the system of record or a layer over existing invoicing — unresolved, see RET-001, NI-3 |
| PCI DSS v4.0.1 | Conditionally out of scope | Only if the CMP-F trigger fires. If the product never receives, transmits or stores cardholder data, merchant validation scope is materially reduced — but the trigger must be **confirmed, not assumed** |
| DR / RPO-RTO | Deferred to §13 (CON-07) | Cannot be stated until NFR-002 has a target |

---

## 10.2 Compliance constraints — surface and trigger conditions

### CMP-A — Data Fiduciary vs Data Processor determination `[C]` *(load-bearing)*

**Trigger:** always, for Indian client data. The tool processes personal data of the freelancer's
**clients**, who never signed up and have no relationship with the vendor. Two open questions:
(i) is the freelancer the Fiduciary and the vendor a Processor under DPDP §8(2)? (ii) does the vendor
become a Fiduciary **in its own right** for any purpose it determines itself?

**Business consequence, not just legal:** if the freelancer is the Fiduciary, the notice duty (§5),
erasure duty (§8(7)), grievance duty (§13) and Data Principal rights (§11-§14) land on a solo operator
with no compliance function. **The product must make those duties dischargeable, or it manufactures
unmanaged liability for its own users** — this is the exact obligation BR-006 requires the solution to satisfy. If this determination resolves against the vendor instead, that is tracked separately as **RSK-012** (§14), since it is a risk to the vendor's own posture, not just the user's.

`[NEEDS INPUT: does the vendor intend any use of client data beyond executing the user's instructions — analytics, benchmarking, model training, cross-user payment signals? A "yes" changes the role determination and the whole consent analysis.]`

### CMP-B — Lawful basis for contacting a third party who never signed up `[C]`

Grounds are consent (DPDP §4, §6) or a legitimate use (§7). §7(a) covers data a Data Principal
**voluntarily provided** without objecting — but the client gave their details to the **freelancer**,
not the platform. Whether that carries down the chain to an automated third-party sender is exactly
what counsel must answer. **Flagged, not resolved.** If the EU trigger fires, the sharper obligation is
**GDPR Art. 14** (data not obtained from the data subject), Art. 14(3)(a) at the latest one month.
This is the legal-basis analysis feeding **BR-008**'s consent-recording requirement (§8) — read together, not as two separate obligations.

**Control implied regardless of outcome:** at import the user attests to the basis on which they hold
each client's contact details, and the attestation is logged (AUD-004).

### CMP-C — Communication conduct *(the assigned domain issue)*

An automated dunning tool sends **unsolicited messages to a third party on the user's behalf**. Five
live constraints, each trigger-conditioned:

| # | Constraint | Trigger | Requirement if triggered | Status |
|---|---|---|---|---|
| C-1 | Registered sender identity (SMS, India) | Any commercial/service SMS to an Indian subscriber | Principal Entity registration on DLT (Distributed Ledger Technology — the TRAI-mandated sender-registration system, unrelated to blockchain), registered header, pre-registered content templates matched to the correct category, sender identity carried in the message body — TRAI TCCCPR 2018 | [C] |
| C-2 | **Who is the Principal Entity — vendor or each user?** | Same as C-1 | Unresolved. **Product-viability question, not just compliance:** if every freelancer must individually register on DLT before sending one reminder, SMS carries an onboarding cost that may make it unusable for the solo segment. Tracked as **RSK-011** (§14). | [C][B] |
| C-3 | Opt-out in every message | (a) US **consumer** debt → Reg F, 12 CFR §1006.6(e), reasonable and simple opt-out in every electronic communication (b) EU → GDPR Art. 21 (c) India → DPDP §6 withdrawal, §13 grievance | Working opt-out on every channel, honoured **across** channels, evidenced per AUD-003 | [C] |
| C-4 | Frequency and quiet-hours ceiling | US consumer debt → Reg F §1006.14(b), presumed violation above 7 calls in 7 days per debt (calls only; electronic messages judged on cumulative harassment effect). India → **no general statutory cap is cited here for a non-regulated creditor**; RBI recovery-agent conduct norms bind Regulated Entities, which a freelancer is not `[C — confirm no conduct floor applies]` | Ceiling enforced and **configurable per regime**. **No default frequency or quiet-hours value is stated in this document** | [C][B] |
| C-5 | Escalation-language conduct | Any template asserting legal consequence ("legal action", "notice", "recovery proceedings") | Shall not dispatch automatically without explicit per-instance user confirmation (AUD-007). Two exposures for counsel: misrepresentation/coercion in collection conduct, and whether platform-authored legal-notice language raises unauthorised-practice-of-law questions | [C] |

**Also:** WhatsApp/Meta Business Messaging policy and email-provider AUPs are **contractual, not
statutory** — but a channel suspension is an availability event on the product's core function.
Tracked as **RSK-010** (§14).

`[NEEDS INPUT: which channels are in scope — email only, or email + SMS + WhatsApp + voice? Every constraint above is channel-specific.]`

### CMP-D — GDPR `[C]`

**Trigger:** users established in the EU/EEA, **or** EU/EEA-located clients whose data is processed in
connection with offering them services. If it fires: Art. 6(1)(f) with a documented balancing
assessment, Art. 14 (per CMP-B), Art. 21, Art. 28, Art. 30, Art. 32, Art. 33, Art. 20.

`[ASSUMPTION: initial users are India-resident freelancers but a meaningful share invoice overseas clients, so the EU trigger is likelier to fire via the *client* side than the *user* side | conf: low — inferred from the intake being written in Hinglish and nothing else; must be validated before it drives any design decision]` (ASM-020, §11)

### CMP-E — GST e-invoicing and tax records `[C]`

**Trigger:** user's aggregate turnover crosses the e-invoicing threshold (CGST Rules r.48(4), ₹5 crore
`[verify current notification]`) **and** they issue B2B invoices **and** the tool generates or
transmits the invoice rather than only chasing one already issued.

`[ASSUMPTION: target-segment solo freelancers sit below the e-invoicing threshold, keeping IRN/QR out of scope | conf: med — plausible for the stated segment, unverified, and one agency-scale user breaks it]` (ASM-021, §11)

The tax-record **retention** duty is separate and bites regardless — see RET-001.

### CMP-F — PCI DSS v4.0.1 `[C]`

**Trigger:** the product receives, transmits or stores cardholder data at any point, including an
embedded field touching the vendor's own page. `[NEEDS INPUT: does the product collect payment, or only link out to a gateway/UPI? "Payments-adjacent" is not specific enough to resolve this.]`

### CMP-G — Payment-handling authorisation `[ESCALATE — not analysed here]`

If the product ever **holds or routes funds** rather than linking out, payment-aggregator
authorisation questions arise under the applicable RBI framework. Licensing of a regulated activity is
outside what this document will opine on in any direction. Route to financial-services counsel before
any design assumes funds flow through the platform.

### CMP-H — Scope guard: payment-reputation features `[C]`

Not in the intake; flagged because it is the natural next feature and the compliance jump is
discontinuous. Any feature that **shares a client's payment behaviour beyond the user who entered it**
— shared defaulter list, public score, cross-user warning — leaves the Processor posture entirely and
raises credit-information and defamation questions. **The exclusion itself is now recorded in §4 as OS-6; this entry retains the compliance rationale for it.**

---

## 10.3 Data retention requirements

**Governing tension:** DPDP §8(7) requires erasure once the purpose is served, while tax law requires
the *user* to keep the underlying records for years. One rule across the whole record set breaks one of
the two — retention must be set **per data class**.

| ID | Data class | Driver | Period | Status |
|---|---|---|---|---|
| RET-001 | Invoice and transaction records | The **user's own** statutory duty, not the vendor's | **72 months** from the due date of furnishing the annual return for that year — CGST Act 2017 §36 (extended to 1 year after final disposal of an appeal/investigation) where the user is GST-registered. Separately **6 years** from the end of the relevant assessment year — Income-tax Rules 1962, r.6F(5), specified professions | [R] for the citation; `[NEEDS INPUT: is the tool the system of record for invoices, or a chase layer over existing invoicing? If the latter, the vendor holds a copy rather than the record — different obligation.]` (same open question as NI-3, §4) |
| RET-002 | Client personal data (contact details) | DPDP §8(7) + DPDP Rules 2025 Rule 8 | **No legally fixed period applies.** Third Schedule defaults (3 years) bind only e-commerce and social-media entities above 2 crore registered users and online gaming above 50 lakh — classes this product is not in `[ASSUMPTION: user counts stay far below those thresholds | conf: high]` (ASM-022, §11). Period is a **purpose-bound business decision**: `[NEEDS INPUT: how long after an invoice settles or is written off does a client's contact record still serve a purpose?]`. Rule 8(3)'s 48-hour pre-erasure intimation attaches to the Third Schedule regime — noted, not asserted as binding here | [B][C] |
| RET-003 | Communication logs, delivery/bounce receipts | Dispute defence — proving what was sent and that opt-outs were honoured | Set by reference to the limitation period for recovery of the underlying debt (Limitation Act 1963 — **the applicable Article is for counsel to identify; no figure stated here**). Shorter than that window leaves the user unable to evidence their own chase history | [C][B] |
| RET-004 | Suppression / opt-out records | Must **outlive** the data they suppress (NFR-014) | Minimised form (identifier + suppression fact + timestamp) retained after the rest of the record is erased. **Open tension:** retaining an identifier in order to honour an objection is defensible in principle but must be reconciled against §8(7) explicitly, and the minimisation must be genuine | [C] |
| RET-005 | Basis attestations captured at import (CMP-B) | Evidentiary | At least as long as RET-003 | [C] |
| RET-006 | Backups and derived stores | An un-propagated erasure is not an erasure | `[NEEDS INPUT: backup retention cycle — it sets the ceiling on how fast RET-002 can complete]` | [B] |
| RET-007 | Audit trail | NFR-016 | ≥ the longest period above. **Flagged tension:** the audit log becomes the longest-lived personal-data store in the system. Whether that is defensible under §8(7) needs counsel — it cannot be resolved by asserting "audit logs are exempt" | [C] |

**Deliberately absent:** any specific number for RET-002, RET-003 or RET-006. Four periods are open;
filling them with plausible defaults is the exact failure this structure exists to prevent.

---

## 10.4 Audit-trail requirements

**Provable to whom:** the *user* (own chase history, self-serve) · the *vendor's assessor* (control
operation) · on lawful request, a *regulator*. Designing for only the first produces a log that fails
the other two.

| ID | Event | Must capture | Why | Status |
|---|---|---|---|---|
| AUD-001 | Chase dispatched | Timestamp · channel · recipient identifier · invoice ref · **template identity and version** · user account on whose authority · automated-vs-manual flag · delivery/bounce outcome | Reconstructing what a client actually received. Version matters: "we sent the polite one" is unprovable if templates are edited in place | Must [R] |
| AUD-002 | Chase suppressed or cancelled | Timestamp · reason (payment, opt-out, objection, user cancellation) · schedule instance affected | Evidences NFR-003 | Must [R] |
| AUD-003 | Opt-out / objection received | Timestamp received · channel · timestamp effective · scope (invoice / client / all channels) | The delta between the two timestamps is the auditable conduct metric; primary evidence if CMP-C C-3 fires | Must [C] |
| AUD-004 | Client data imported | Timestamp · user account · record count · the basis attestation made (CMP-B) | The artefact the Processor posture depends on | Must [C] |
| AUD-005 | Vendor staff access to user or client data | Timestamp · staff identity · records accessed · stated reason · user-initiated flag | NFR-008 | Must [R] |
| AUD-006 | Erasure / retention job execution | Timestamp · job · records affected · failures and disposition | Proving DPDP §8(7) erasure **ran**. A policy document is not evidence; a job log is | Must [R] |
| AUD-007 | Escalation-template dispatch (CMP-C C-5) | The explicit user confirmation, timestamped, with the account that gave it | Separates automated conduct from user-authorised conduct — the distinction that matters most if collection conduct is challenged | Must [C] |

**Cross-cutting:** tamper-evident (NFR-016) · retained per RET-007 · user-exportable · **minimised** —
the trail must not become an unbounded parallel PII store; the RET-007 tension applies to every row.

---

## 10.5 Assembly disposition (feed-forward items — resolved)

The items below were staged by the §10-drafting agent for assembly and have now been merged into their true home sections. Retained here as an audit trail so a reviewer can verify nothing was silently dropped.

| Staged item | Disposed to | How |
|---|---|---|
| 4 assumptions (NFR-005 volume concentration, CMP-D EU-exposure-via-clients, CMP-E below-e-invoicing-threshold, RET-002 user-counts-below-threshold) | §11 Assumptions Register | Assigned ASM-019, ASM-020, ASM-021, ASM-022 respectively |
| DR/RPO-RTO — blocked until NFR-002 has a target | §13 Constraints | Added as CON-07 |
| Risk: channel-provider suspension (Meta policy, email AUP) disabling core function | §14 Risk Register | Added as RSK-010 |
| Risk: DLT Principal-Entity burden making SMS commercially unusable (C-2) | §14 Risk Register | Added as RSK-011 |
| Risk: CMP-A resolving against the vendor, converting it into a Data Fiduciary | §14 Risk Register | Added as RSK-012, cross-referenced against the pre-existing RSK-007 (kept as two distinct risks — see assembly-report.md) |
| Scope guard: cross-user payment-reputation features | §4 Scope | Added as OS-6 |
| `OBJ-###` placeholders in the NFR Driver column (NFR-002, NFR-004) | §10 NFR table above | Resolved to OBJ-001 and OBJ-002 respectively, with assembly reasoning noted inline and in assembly-report.md |

---

## Counsel handoff

Items that cannot be stated as settled requirements without review by counsel licensed in the relevant
jurisdiction:

1. **CMP-A** — Fiduciary vs Processor determination, and whether secondary use makes the vendor a
   Fiduciary in its own right. *Everything else depends on this.*
2. **CMP-B** — lawful basis for contacting a third party who never signed up; whether DPDP §7(a) carries
   down the chain; whether GDPR Art. 14 is engaged.
3. **CMP-C C-1/C-2** — TCCCPR 2018 Principal Entity determination: vendor or each individual user.
4. **CMP-C C-3/C-4** — opt-out and frequency duties; whether any Indian conduct floor binds a
   non-regulated creditor; whether Reg F is ever engaged (turns on the consumer-vs-business character
   of the debt — a freelancer invoicing an individual rather than a business is the boundary case).
5. **CMP-C C-5** — misrepresentation exposure and unauthorised-practice-of-law questions in escalation
   templates.
6. **CMP-F / CMP-G** — confirmation the product never touches cardholder data; **escalation** of any
   funds-handling design to financial-services counsel.
7. **RET-004 / RET-007** — reconciling suppression-record and audit-log retention against §8(7).
8. **NFR-006 / NFR-009** — applicable DPDP Rules 2025 sub-clauses and their phased commencement dates.

*Citations are drawn from the primary instruments named and corroborated against secondary sources;
verify current text before relying on any of them. Nothing here is a legal conclusion, and no statement
certifies compliance with any regulation.*

---

## 11. Assumptions Register

**Consolidation point.** Every `[ASSUMPTION]` tag anywhere in this document — swept from all five drafting parts plus the pre-formed register supplied by the risk/cost-benefit section — terminates here as one continuous ID sequence. Of 30 raw `[ASSUMPTION` occurrences found by text search across the five source parts, 3 were not independent assumption content (2 were the drafting agents explaining the tagging convention itself, 1 was a duplicate restatement of BR-003's row-level source in its expanded block) — see assembly-report.md for the exact accounting. The remaining 27 are registered below as ASM-001–ASM-027, followed by the 10 pre-formed rows supplied directly by the risk/cost-benefit section as ASM-028–ASM-037.

**Owner note.** Only ASM-028–ASM-037 arrived with an owner and validation date (the risk/cost-benefit section stated this is a solo initiative with Ujjawal owning every row in its own register). ASM-001–ASM-027 came from sections that did not make that statement, so — per the hard rule against inventing owners — their Owner and Validation Date cells are left `[NEEDS INPUT]` rather than assumed to inherit the same ownership.

| # | Assumption | Owner | Validation Date | Impact if Wrong | Confidence |
|---|---|---|---|---|---|
| ASM-001 | Manual chasing effort is measurable only via periodic in-app or survey-based self-report — no objective instrumentation of the freelancer's pre-tool process exists (OBJ-002 measurement method) | `[NEEDS INPUT]` | `[NEEDS INPUT]` | OBJ-002 cannot be measured reliably; self-report is a weak substitute for observed behaviour | Low |
| ASM-002 | Client-friction incidents are measurable via a freelancer-reported incident log within the solution (OBJ-003 measurement method) | `[NEEDS INPUT]` | `[NEEDS INPUT]` | OBJ-003, the initiative's non-negotiable constraint, has no independent measurement if freelancers under-report friction | Low |
| ASM-003 | Target market is India-based freelancers and India-based or India-serving clients, consistent with the commissioning context (OBJ-004 jurisdiction scope) | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Compliance frame is wrong; GDPR may apply instead of/alongside DPDP | Low |
| ASM-004 | "Unpaid invoices" in the intake means invoices going overdue, not a specific rate or cause of overdue invoices | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Low impact — this is a low-risk plain-language reading, not a load-bearing inference | High |
| ASM-005 | Target freelancers already issue invoices through some existing means (own tool, template, or accounting software) before reaching this product | `[NEEDS INPUT]` | `[NEEDS INPUT]` | If false, OS-1's exclusion of invoice creation may be the wrong scope boundary | Med |
| ASM-006 | GST e-invoicing is not applicable to the target solo/micro-freelancer segment | `[NEEDS INPUT]` | `[NEEDS INPUT]` | One agency-scale user brings IRN/QR e-invoicing into scope, invalidating OS-4's exclusion | Med |
| ASM-007 | Some share of the target segment uses a third-party bookkeeper who also touches invoice status | `[NEEDS INPUT]` | `[NEEDS INPUT]` | STK-06's secondary-user role may be over- or under-weighted in design | Low |
| ASM-008 | Invoices are issued with an explicit due date, as standard freelance-services practice | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Low — foundational to "overdue" being computable at all; if false, BR-001 has no due-date signal to work from | High |
| ASM-009 | Freelancer's current invoice tracking is informal (memory, spreadsheet, bank-statement scan) rather than a dedicated system | `[NEEDS INPUT]` | `[NEEDS INPUT]` | If freelancers already use a dedicated tracking tool, the As-Is pain point (1.2) and the product's core value proposition are weaker than assumed | Low |
| ASM-010 | Follow-up messages are composed fresh per instance, on ad hoc timing, not from a saved template on a fixed cadence | `[NEEDS INPUT]` | `[NEEDS INPUT]` | If freelancers already use templates/cadences informally, the automation's marginal value on this specific step is smaller | Low |
| ASM-011 | Reluctance to jeopardise the client relationship is a commonly cited reason freelancers under-chase, plausible for this segment but unconfirmed for this engagement | `[NEEDS INPUT]` | `[NEEDS INPUT]` | If the real driver is something else (client cash-flow, forgetfulness, disputes), the product's central design bet (override-preserving automation) targets the wrong problem — same premise as ASM-028/RSK-005 | Med |
| ASM-012 | No formal escalation path or defined "close" state exists today for an unresolved invoice | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Low — affects only how novel the To-Be 1.6 "surfaced decision" step actually is to users | Low |
| ASM-013 | Preserving freelancer override addresses the relationship-risk hesitation identified in As-Is 1.4, rather than removing the freelancer's judgment entirely — the product's central bet | `[NEEDS INPUT]` | `[NEEDS INPUT]` | **High** — if wrong, the whole To-Be design (automation + override) does not actually solve the root cause; rests on an unconfirmed root cause | Med |
| ASM-014 | A pause/stop/override capability is necessary to protect ongoing/repeat-client relationships, a common characteristic of solo-operator freelance work | `[NEEDS INPUT]` | `[NEEDS INPUT]` | If wrong, BR-003 (a Must) may be over-scoped relative to actual need, though the downside of building it unnecessarily is low | Med |
| ASM-015 | Chasing a client after payment is a known failure mode in this product category and would directly work against OBJ-003 | `[NEEDS INPUT]` | `[NEEDS INPUT]` | If this isn't actually a salient failure mode, BR-004's Must priority may be reconsidered — but the downside of building it regardless is low | Med |
| ASM-016 | Multi-stage escalation (distinct earlier/later reminders) is common practice in payment-reminder products generally | `[NEEDS INPUT]` | `[NEEDS INPUT]` | If wrong, BR-005 (Should) may not be a real differentiator | Low |
| ASM-017 | An audit trail of chase actions is necessary for the freelancer to defend against a client dispute over chasing conduct, and to make BR-004 auditable | `[NEEDS INPUT]` | `[NEEDS INPUT]` | If wrong, BR-007 may be lower priority than Should | Med |
| ASM-018 | A consolidated status view is a baseline usability need implied by OBJ-002 (freelancer can see status without re-deriving it manually) | `[NEEDS INPUT]` | `[NEEDS INPUT]` | If wrong, BR-009 may not be load-bearing for OBJ-002 | Med |
| ASM-019 | Dispatch volume concentrates at month-end and FY-end rather than distributing evenly | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Peak-shaped load invalidates the NFR-002/NFR-005 availability and scalability commitments if sized for average load | Med |
| ASM-020 | Initial users are India-resident freelancers, but a meaningful share invoice overseas clients — so the EU/GDPR trigger (CMP-D) is likelier to fire via the client side than the user side | `[NEEDS INPUT]` | `[NEEDS INPUT]` | GDPR lands on a different trigger than designed for; Art. 14 becomes live in a way the design didn't anticipate | Low |
| ASM-021 | Users sit below the GST e-invoicing threshold (₹5cr turnover) | `[NEEDS INPUT]` | `[NEEDS INPUT]` | One agency-scale user brings e-invoicing (IRN/QR) into scope | Med |
| ASM-022 | User counts stay far below the DPDP Third Schedule thresholds (2cr registered users / 50 lakh gaming users) that would trigger fixed statutory retention defaults | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Statutory default retention periods (RET-002) would apply instead of a purpose-bound business decision | High |
| ASM-023 | DPDP Act 2023 applicability was correctly confirmed at the classification stage of this initiative | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Low — this is a restatement of a classification-doc finding, not a new inference; current rules-notification/enforcement timeline and Significant Data Fiduciary threshold applicability remain separately `[NEEDS INPUT]` | High |
| ASM-024 | This is a greenfield build with no mandated legacy system integration | `[NEEDS INPUT]` | `[NEEDS INPUT]` | If a legacy integration is actually mandated, CON-06 and the DR/RPO-RTO gap (CON-07) both need rework | Med |
| ASM-025 | A business case (§17) is warranted at all — i.e., this is intended as a commercial venture rather than a personal-use tool or a portfolio artefact | `[NEEDS INPUT]` | `[NEEDS INPUT]` | If false, most of §17's arithmetic is unnecessary and the unquantified-benefits framing (§17.7) is the real motive | Med |
| ASM-026 | Alternative A1 (standalone offering) is under evaluation only because the intake named it — a solution was stated without a problem, so A1 has not been shown to be the right shape of response | `[NEEDS INPUT]` | `[NEEDS INPUT]` | If A2 (capability within a broader offering) or A3 (non-product intervention) is actually the right shape, evaluating A1 alone wastes the analysis | Low |
| ASM-027 | The time-saved term (H × W) alone cannot justify a subscription, because users rarely value unbilled admin hours at their billable rate — so §17.3's case rests almost entirely on the recovery-uplift variable U | `[NEEDS INPUT]` | `[NEEDS INPUT]` | If true, this narrows the entire viability case to the least-knowable variable in the model | Med |
| ASM-028 | **Non-payment is materially caused by inconsistent follow-up** — i.e. chasing changes the outcome. The intake named a solution, never a cause. | Ujjawal | 2026-08-12 | **Fatal** — if the real cause is client insolvency, disputed scope or absent written terms, recovery uplift `U` (§17.3) → 0 and the case collapses regardless of execution | Low |
| ASM-029 | Segment is **India-first, INR, solo/micro operators** — no finance staff, no PO process | Ujjawal | 2026-08-05 | Agencies or EU users change the compliance surface (GDPR joins DPDP), the buyer and the price band | Med |
| ASM-030 | The freelancer's clients are **businesses**, not consumers | Ujjawal | 2026-08-12 | B2C receivables carry a different tone constraint, DPDP posture and escalation path; re-scopes RSK-006/RSK-007 | Med |
| ASM-031 | **Buyer = user**, own cash, no approval step | Ujjawal | 2026-08-12 | Shortens the sales cycle but caps price at personal-discretionary level — the constraint behind RSK-003 | High |
| ASM-032 | Monetization is a **recurring subscription**, not a success fee on recovered amounts | Ujjawal | 2026-08-19 | High to the arithmetic: a success fee replaces §17.4's model with contingent revenue, largely dissolves RSK-003, and triggers RSK-009. The two cannot share one input set | Med |
| ASM-033 | The offering **never takes custody of funds** and never touches card data | Ujjawal | Standing | Custody or card handling pulls in PCI-DSS and aggregator licensing — order-of-magnitude cost change, unsurvivable at this price point | High |
| ASM-034 | Micro-SMB buyers need a **visible value-to-price multiple**, not parity (sets `k` in §17.3) | Ujjawal | 2026-08-12 | Practitioner wisdom, not sourced. If k≈1 a far wider price band is viable; if k is high the category may be unpriceable | Med |
| ASM-035 | **LTV/CAC ≥ 3** is an appropriate viability gate | Ujjawal | 2026-09-02 | A convention, not a law, and weak at micro price points where the ratio looks healthy while absolute contribution is trivial. Used as shape only | Low |
| ASM-036 | Build cost is denominated principally in **Boss's time**, not cash | Ujjawal | 2026-08-19 | Makes investment a judgement about foregone alternatives; if cash dominates, payback tightens | Med |
| ASM-037 | Dates in this register assume start **2026-07-29**, Boss executing personally | Ujjawal | Standing | Low — slippage delays the go/no-go, changes no conclusion | Med |

**Run ASM-028 first**: lowest confidence, the premise the largest cluster of other assumptions and risks sit on, cheapest to test. If it fails, §17 never needs completing, and several downstream ASM/RSK rows (ASM-011, ASM-013, RSK-001, RSK-002, RSK-005) collapse or need re-scoping with it.

---

## 12. Dependencies

| DEP-ID | Dependency | Owning team | Expected date | Impact if late/unmet |
|---|---|---|---|---|
| DEP-01 | Resolution of the ownership question (Business Sponsor identity — Boss's own product vs. client engagement vs. hypothetical) | `[NEEDS INPUT: owning team]` | `[NEEDS INPUT]` | **Blocking** — STK-01, STK-04, STK-05, the entire Requirements-sign-off RACI column, and §17 Cost-Benefit cannot be completed without it |
| DEP-02 | Freelancer must maintain an accurate, current record of which invoices are unpaid and their amounts (their existing invoicing/bookkeeping practice, whatever form it takes today) | Freelancer (external, outside the delivery team's control) | Ongoing, at point of onboarding | High — the tool's core action (chasing) is only as correct as the freelancer's own unpaid-invoice data; a stale record causes chasing an already-paid client, which is the single fastest way to destroy trust in the product |
| DEP-03 | Legal/compliance review and written guidance on what constitutes permissible automated-payment-reminder conduct toward a third party (vs. conduct that reads as unlicensed debt collection) under Indian law, before any chase sequence reaches a real client | `[NEEDS INPUT: name — Legal/Compliance owner, see STK-04]` | `[NEEDS INPUT — should precede first client-facing send, not follow it]` | **High** — undefined; a chase sequence that crosses into harassment/collection-agency-style conduct is a legal and reputational failure, not a product-quality one |
| DEP-04 | A reliable, non-spam-flagged outbound communication channel (email and/or other messaging) reaching the freelancer's client, with acceptable deliverability at the volumes this tool would generate | `[NEEDS INPUT: owning team]` | `[NEEDS INPUT]` | Medium — without deliverability, the core value proposition (chasing actually happens) silently fails; would show up first as a metrics anomaly (§15, KPI-06) rather than a visible outage |
| DEP-05 | A reliable signal that an invoice has actually been paid, so chasing stops — sourced from wherever the freelancer already tracks payment (bank, UPI, payment gateway, manual mark-as-paid) | `[NEEDS INPUT: owning team]` | `[NEEDS INPUT]` | High — without this, the tool keeps chasing a client who already paid, which is the second-fastest way (after DEP-02) to convert a helpful tool into a reputational liability |

*Note on discipline: this list is organisational/business dependencies only — who/what the initiative
relies on outside its own control. It deliberately does not name a payment gateway, messaging
provider, or any specific vendor/API; that decision belongs to the solution layer (FRD), not this
document, per the solution-language boundary.*

---

## 13. Constraints

No budget ceiling, go-live date, team size, or explicit regulatory deadline was supplied in the
intake. Per the standards this document follows, "limited budget and time" is not a valid constraint
statement on its own — so rather than fabricate numbers, every quantity below is flagged, not
invented.

| CON-ID | Constraint | Type | Value | Source |
|---|---|---|---|---|
| CON-01 | Budget ceiling | Financial | `[NEEDS INPUT]` | Not supplied |
| CON-02 | Go-live / launch date | Schedule | `[NEEDS INPUT]` | Not supplied |
| CON-03 | Team size / composition | Resourcing | `[NEEDS INPUT]` | Not supplied |
| CON-04 | DPDP Act 2023 applies to any processing of the client's personal data (name, email, phone, payment status) collected and processed on the freelancer's behalf | Regulatory | Enacted law; applicability inherited from classification `[ASSUMPTION: DPDP Act 2023 applicability confirmed at classification stage | conf: high]` (ASM-023, §11) — current rules-notification/enforcement timeline and whether Significant Data Fiduciary thresholds could apply are `[NEEDS INPUT]` | Classification doc, this project's `data/brd/_smoketest-invoice-chaser/classification.md`. Cross-reference: BR-006 (§8) is the requirement this constraint necessitates; NFR-006 (§10) sets the safeguard target. |
| CON-05 | The product's core action targets a person (the client) who is not the customer and has not consented to being contacted by this tool — this is a standing constraint on every chase-related requirement, not a one-time risk item | Legal/ethical, self-imposed by the nature of the initiative | Every chase-communication requirement must be reviewed against unlicensed-debt-collection and harassment exposure before build, not after | Derived directly from the intake's own framing ("automatically chase") — not an external source, flagged as a structural constraint the requirements-drafting section must design around |
| CON-06 | Untouchable legacy system to integrate with | Technical | None identified — `[ASSUMPTION: this is a greenfield build with no mandated legacy integration, inferred from the intake describing a new standalone tool rather than an add-on | conf: med]` (ASM-024, §11) | Intake inference only |
| CON-07 | Disaster-recovery RPO/RTO cannot be set | Technical | `[NEEDS INPUT — blocked until NFR-002 (§10) has an availability target; DR/RPO-RTO sizing is meaningless without it]` | §10.5 assembly disposition, feed-forward from the NFR-drafting section |

---

## 14. Risk Register

P × I, each 1-5. ≥15 High · 8-14 Med · ≤7 Low. All `Open` — no mitigation has started, and recording
otherwise would be false. Generic delivery risks (scope creep, estimate overrun) are excluded
deliberately: they are not what a review of *this* initiative turns on.

**Note on the table shape.** This table carries a **Category** column that the master template's own markdown skeleton omits, even though the template's written standard for this section explicitly requires one ("Category, description, likelihood, impact, mitigation, owner, status" — `references/standards.md` §3, row 14). The richer form is kept here as the correct one; see assembly-report.md for the discrepancy flag.

| ID | Cat | Description | P | I | Score | Mitigation | Owner | Status | Links |
|---|---|---|---|---|---|---|---|---|---|
| RSK-001 | Competitive | **Feature, not a product.** Established invoicing/accounting products for this segment already bundle automated reminders; a standalone offering must beat a capability the buyer may already own and not pay extra for. | 4 | 4 | **16 H** | Audit the cohort's existing tools — do reminders exist, are they switched on, if not why not. Proceed only if a specific nameable gap survives; a "we'd do it better" claim does not count. | Ujjawal | Open | ASM-028; §3 rung 5 |
| RSK-002 | Adoption | **The buyer's fear is relational, not operational.** Freelancers often under-chase *by choice*, protecting a client they need repeat work from. Automating the chase then amplifies the thing they fear — adoption dies at first send, not at signup. | 4 | 4 | **16 H** | Ask directly what stopped them chasing last time. If the answer is social, re-frame the value proposition around removing the *social cost* of asking — cheap now, near-impossible after build. | Ujjawal | Open | ASM-028; §6 As-Is 1.4; ASM-011, ASM-013 |
| RSK-003 | Commercial | **Willingness to pay for a single-function tool.** Most price-sensitive segment in software, personal-discretionary spend, and single-function tools are first dropped and easiest for a suite to absorb. | 4 | 5 | **20 H** | Price-probe before build (ASM-034) and pre-commit a kill threshold: if median acceptable price sits below where §17.4's contribution clears fixed run cost at a reachable user count, stop. | Ujjawal | Open | ASM-032, ASM-034 |
| RSK-004 | Operational | **Chasing an already-paid invoice.** The proposition depends on truthful payment status; a wrong chase reaches the user's paying client and embarrasses the user in front of the person who pays them. Near-certain churn plus word-of-mouth cost. | 3 | 5 | **15 H** | Establish where payment truth comes from, and how stale it may be, as a business requirement before anything else is scoped. If no reliable source can be assumed, the need must be re-stated to keep the user in the loop before each outbound action — which changes the "automatically" in the intake. | Ujjawal | Open | ASM-028; BR-004; DEP-05; NFR-003 |
| RSK-005 | Validity | **Root-cause misdiagnosis.** If non-payment is driven by client cash-flow failure, disputed deliverables or missing written terms, follow-up cadence is not the binding constraint and uplift is negligible. | 3 | 5 | **15 H** | ASM-028 restated as a risk; same retrospective, run before any build decision. Highest-leverage single action on this register. | Ujjawal | Open | ASM-028; §3 rung 3 |
| RSK-006 | Regulatory | **Regulated / rate-limited outreach channels.** Business-initiated messaging to Indian recipients sits under channel-specific consent and template regimes, and repetitive dunning content is precisely what deliverability filters target. | 3 | 3 | **9 M** | Confirm the regulatory position per intended channel before committing, and record channel availability as a §13 constraint. `[NEEDS INPUT: which outreach channels are acceptable — email only, or messaging/voice too? The compliance surface differs sharply per channel.]` | Ujjawal | Open | ASM-029; §10.2 CMP-C (general consent/template surface — distinct mechanism from RSK-010/RSK-011, kept separate, see assembly-report.md) |
| RSK-007 | Compliance | **DPDP 2023 exposure via third-party data, under the currently assumed role split.** The offering processes personal data of the *user's clients* — people with no relationship to the platform. Given the working assumption that the freelancer is fiduciary and the platform is processor (§10.2 CMP-A), obligations arrive contractually and must surface in user-facing terms. | 3 | 4 | **12 M** | Fix the fiduciary/processor split and flow-down obligations as a §10 compliance requirement before any client data is collected. This exposure exists at zero revenue. | Ujjawal | Open | ASM-029, ASM-030; BR-006; NFR-006; CMP-A. *Distinct from RSK-012: this risk is the exposure that exists **given** the assumed role split; RSK-012 is the risk that the split itself resolves the other way.* |
| RSK-008 | Distribution | **Distribution and acquisition cost.** A diffuse population with no concentrated buying channel; at a micro price point paid acquisition can exceed lifetime contribution, leaving only slow organic paths — which changes the venture's time horizon, not just its budget. | 4 | 4 | **16 H** | Name one concrete reachable concentration of the segment before build; treat "we'll find distribution later" as a rejected plan. | Ujjawal | Open | ASM-035 |
| RSK-009 | Positioning | **Drift toward debt collection.** Harder tone, third-party involvement or contingency pricing raise apparent efficacy while moving the offering into a regulated, reputationally sensitive activity. | 2 | 4 | **8 M** | Draw the line in §4 Out-of-Scope now, with a stated reason, rather than during a pricing discussion. Constrains the ASM-032 choice. Cross-reference OS-6, CMP-H. | Ujjawal | Open | ASM-032 |
| RSK-010 | Operational | **Channel-provider suspension.** WhatsApp/Meta Business Messaging policy and email-provider AUPs are contractual, not statutory, but a channel suspension is an availability event on the product's core function. | `[NEEDS INPUT]` | `[NEEDS INPUT]` | `[NEEDS INPUT — not scored by the originating section; scoring deferred rather than invented]` | Confirm channel resilience/appeal-path before committing to a single channel; consider multi-channel fallback as a design question for the FRD | Ujjawal *(applying the document-wide solo-initiative ownership fact stated in §11; not independently confirmed for this row)* | Open | §10.2 CMP-C "Also" note; DEP-04 |
| RSK-011 | Regulatory / Commercial | **DLT Principal-Entity registration burden.** If every freelancer must individually register as Principal Entity on the TRAI DLT platform before sending one SMS reminder, the onboarding cost may make SMS commercially unusable for the solo segment (CMP-C C-2). | `[NEEDS INPUT]` | `[NEEDS INPUT]` | `[NEEDS INPUT — not scored by the originating section]` | Resolve C-2 (vendor-as-Principal-Entity vs. per-user registration) with counsel before committing SMS as a supported channel | Ujjawal *(same ownership caveat as RSK-010)* | Open | §10.2 CMP-C C-1/C-2 |
| RSK-012 | Compliance / Regulatory | **Fiduciary/Processor determination resolves against the vendor.** If CMP-A's role determination finds the vendor is a Data Fiduciary in its own right (not merely a Processor), the full DPDP obligation set (notice, erasure, grievance, Data Principal rights) lands on the vendor rather than being a duty the product merely helps the user discharge. | `[NEEDS INPUT]` | `[NEEDS INPUT]` | `[NEEDS INPUT — not scored by the originating section]` | Resolve CMP-A with counsel before any client-data processing begins; this is the single load-bearing legal question in §10.2 | Ujjawal *(same ownership caveat as RSK-010)* | Open | §10.2 CMP-A; NFR-006; BR-006; RSK-007 (distinct — see RSK-007's Links cell) |

**The register's message:** the four highest scored risks with real numbers (RSK-003 at 20; RSK-001/002/008 at 16) are all
**pre-build** risks. Each is answerable by talking to eight people for an hour, each can independently
kill the case, and **none is mitigated by building a better product.** RSK-010/011/012, merged at assembly from §10's compliance analysis, are real but currently **unscored** — no P/I was assigned by either originating section, and assembly does not invent one; scoring them is a follow-up action.

---

## 15. Success Metrics / KPIs

**Read this table with its limitation stated up front, not buried:** no baseline data of any kind
was supplied for this initiative. Per the anti-fabrication rule, every Baseline and Target cell
below is `[NEEDS INPUT]` rather than an invented number — a metric with a placeholder baseline is
correct here; a metric with a confident invented baseline would be a defect. What follows is the
candidate metric *set* (what should be measured and how), not the numbers themselves.

**Loop-closing check, run at assembly:** every number in this table must already appear in §2/§3. Since §2/§3 carry no numbers either (every objective and baseline is `[NEEDS INPUT]`), there is nothing to reconcile a mismatch against — the table is consistent with §2/§3 by virtue of both being equally unpopulated, not because alignment was checked and passed. This is flagged, not silently assumed.

| KPI-ID | Metric | Baseline | Target | Measurement Method | Measurement Date | Owner | Traces to |
|---|---|---|---|---|---|---|---|
| KPI-01 | Days Sales Outstanding (DSO) for freelancers using the tool, vs. their own pre-tool DSO | `[NEEDS INPUT]` — requires each pilot freelancer's own pre-adoption DSO, not an industry figure | `[NEEDS INPUT]` | Self-reported or connected-record DSO comparison, pre- vs. post-adoption, per user | `[NEEDS INPUT]` | `[NEEDS INPUT — depends on STK-01]` | **OBJ-001** |
| KPI-02 | Invoice collection rate — % of chased invoices paid within N days of the chase sequence starting | `[NEEDS INPUT]` | `[NEEDS INPUT]` | In-product tracking: chase-sequence-start timestamp vs. mark-paid timestamp (see DEP-05) | `[NEEDS INPUT]` | `[NEEDS INPUT]` | **OBJ-001** |
| KPI-03 | **Client-side harm signal — complaint / opt-out / "stop contacting me" rate per 100 chase sequences sent** (counter-metric; must not be traded away for KPI-01/02) | `[NEEDS INPUT]` | `[NEEDS INPUT — should be a ceiling, not a floor, e.g. "no more than X per 100," once X is set with real data]` | Count of client replies/complaints flagged as objection, opt-out, or escalation, per chase sequence sent | `[NEEDS INPUT]` | `[NEEDS INPUT]` | **OBJ-003** |
| KPI-04 | Freelancer time saved on manual chasing (hours/month) | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Self-reported survey at onboarding (pre-tool estimate) vs. quarterly follow-up | `[NEEDS INPUT]` | `[NEEDS INPUT]` | **OBJ-002** |
| KPI-05 | Freelancer retention/churn correlated with active use of the chase feature | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Cohort retention analysis, chase-feature users vs. non-users | `[NEEDS INPUT]` | `[NEEDS INPUT]` | `[GENUINE ORPHAN — no upward objective link. This metric measures venture-viability churn (relevant to §17.4's `churn` variable), not a stated OBJ-001…004 outcome. Not resolved by inventing an OBJ-005; recorded in assembly-report.md as a real traceability gap.]` |
| KPI-06 | Deliverability/reach of chase communications (% successfully delivered to the client, independent of DEP-04 channel choice) | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Delivery-confirmation logging per chase send | `[NEEDS INPUT]` | `[NEEDS INPUT]` | **OBJ-001** *(assembly link: an enabling metric — collection cannot speed up if chases don't arrive; see assembly-report.md)* |

**Why KPI-03 is not optional:** every other metric in this table measures whether the tool works for
the buyer (the freelancer). None of them would catch the tool succeeding at collection while quietly
damaging the freelancer's client relationships or crossing into harassment — the exact failure mode
CON-05 exists to prevent. A success-metrics table for this specific product that omits a counter-metric
on the non-consenting party is, by the standard this document follows, incomplete on its face.

**Genuine gap, recorded not patched:** OBJ-004 (regulatory-safe communication) has no corresponding KPI in this table. §2 already flags this; it is repeated here for anyone reading §15 in isolation.

---

## 16. Acceptance Criteria

**Given/When/Then — individual requirement level** (Must-priority requirements, plus BR-009 as the representative Should)

```
AC-BR001.1
  Given an invoice has a due date in the past
  When the invoice's payment status is checked
  Then the solution classifies it as overdue without requiring
       the freelancer to mark it manually

AC-BR001.2
  Given an invoice is marked paid on or before its due date
  When the invoice's payment status is checked
  Then the solution does not classify it as overdue

AC-BR002.1
  Given an invoice has been classified as overdue (per BR-001)
  When the configured chase sequence begins
  Then the solution initiates client contact without the freelancer
       manually triggering that specific contact

AC-BR002.2
  Given the freelancer has not configured any chase sequence for a
       given invoice or client
  When that invoice becomes overdue
  Then [NEEDS INPUT: default behaviour is undefined — should the
       solution apply a system default sequence, or wait for explicit
       freelancer setup before chasing? Not answered by the intake.]

AC-BR003.1
  Given an invoice is currently in an active automated chase sequence
  When the freelancer pauses or stops chasing for that invoice
  Then no further automated contact is sent for that invoice until
       the freelancer explicitly resumes it

AC-BR003.2
  Given the freelancer stops chasing for a specific client (not a
       single invoice)
  When a future invoice for that same client becomes overdue
  Then [NEEDS INPUT: whether a client-level stop applies by default
       to all future invoices, or only to the invoice(s) explicitly
       selected at the time, is undefined.]

AC-BR004.1
  Given an overdue invoice is in an active chase sequence
  When the invoice is recorded as paid
  Then no further chase communication is sent for that invoice,
       including any already-scheduled reminder

AC-BR004.2
  Given a reminder has already been sent for the current billing
       cycle before payment is recorded
  When the payment record updates
  Then the chase status changes to "paid" and no duplicate
       payment-confirmation-seeking message is sent

AC-BR006.1
  Given client personal data (name, contact details, payment status)
       is stored or processed by the solution
  When that data is handled at any stage (collection, storage, use in
       a chase communication, deletion)
  Then the handling conforms to the data-protection obligations of the
       confirmed jurisdiction — [NEEDS INPUT: cannot be finalized as a
       pass/fail test until jurisdiction and applicable law are
       confirmed per BR-006's Source note; see also NFR-006, §10]

AC-BR008.1
  Given a client has not previously been contacted automatically on
       behalf of a freelancer
  When the freelancer's first automated chase for that client would
       be triggered
  Then the solution requires and records freelancer confirmation that
       automated contact to that client is permitted, before the
       first automated message is sent

AC-BR009.1
  Given a freelancer has outstanding invoices at different chase
       stages
  When the freelancer requests a status view
  Then every outstanding invoice shows exactly one of: not yet due,
       overdue, in active chase, paused, or paid — with no invoice
       omitted
```

**Checklist — go-live/release level**

- [ ] BR-001, BR-002, BR-003, BR-004, BR-006, BR-008 pass acceptance testing with zero Critical/High defects open
- [ ] BR-006 and BR-008 compliance behaviour signed off by `[NEEDS INPUT: named legal/compliance reviewer — STK-04, not yet named]` against the confirmed jurisdiction
- [ ] BR-003 and BR-004 specifically verified against the "chase continues after payment" and "cannot be stopped mid-sequence" failure modes, given their direct link to OBJ-003 (relationship protection)
- [ ] OBJ-001 through OBJ-004 baseline data collection (per §3's NEEDS INPUT list) completed and logged before any numeric target is locked
- [ ] Sign-off obtained from every "A" role in the Requirements-sign-off RACI column (§5) — currently STK-01, `[NEEDS INPUT: name]`

---

## 17. Cost-Benefit / Business Case

### 17.1 Why this section carries no figures

Market size, willingness to pay, build cost, run cost, CAC, retention and recovery uplift were all
absent from the intake and cannot be responsibly inferred. A fabricated rupee figure would be worse
than a blank — harder to challenge, looks like analysis, propagates downstream, and nobody remembers
it was invented. What follows is the **arithmetic, its driving variables, the specific input each one
needs, and the pre-committed decision rule**. Supply the inputs and this becomes a real business case
in one pass.

`[ASSUMPTION: a business case is warranted at all — that this is intended as a commercial venture rather than a personal-use tool or a portfolio artefact. The three have different viability tests and only one needs §17. | conf: med]` (ASM-025, §11)

### 17.2 Alternatives, including do-nothing

| Alt | Description |
|---|---|
| **A0 — Do nothing** | The correct default; the others must beat it. Its cost is not zero (unclaimed uplift), but nor is it obviously large — the size of that uplift is exactly the unknown (ASM-028). |
| **A1 — Standalone offering** | The intake as stated. Must beat A0 *and* survive RSK-001. |
| **A2 — Capability within a broader offering** | Same need, one part of a wider proposition, so willingness-to-pay is not carried by this function alone. Weakens RSK-001/003; raises scope and cost. |
| **A3 — Non-product intervention** | The need met without software (structured terms + disciplined manual cadence). Relevant because if ASM-028 is false, A3 and A1 produce the same outcome and A3 costs nothing. |

`[ASSUMPTION: A1 is under evaluation only because the intake named it; a solution was stated without a problem, so A1 has not been shown to be the right shape of response. | conf: low]` (ASM-026, §11)

**No recommendation yet, deliberately** — choosing between A1/A2/A3 needs one interview round.

### 17.3 Buyer-side value — will a freelancer pay?

```
V  =  (N × A × U)        recovery gain — value that would otherwise never arrive
   +  (N × A × D × r)    carry gain — value arriving sooner × cost of money
   +  (H × W)            time gain — hours no longer spent chasing, at their rate
```
Adoption condition: **`V ≥ k × P`**.

| Sym | Meaning | Status |
|---|---|---|
| `N` | Past-due invoices per user per month | `[NEEDS INPUT: monthly invoice count and past-due share]` |
| `A` | Average past-due invoice value | `[NEEDS INPUT: typical invoice value in segment]` |
| `U` | **Recovery uplift** (pp of at-risk value additionally recovered) | `[NEEDS INPUT: no credible source exists; only a measured before/after produces it. The most important unknown in this document.]` |
| `D` | Reduction in days-to-payment | `[NEEDS INPUT: current days-to-payment + evidence reminders shorten it here]` |
| `r` | Daily cost of money / value of cash-flow certainty | `[NEEDS INPUT: for a solo operator this is a stress-and-planning cost, not an interest rate — define before estimating]` |
| `H` | Hours/month spent chasing | `[NEEDS INPUT: ask the cohort]` |
| `W` | Effective hourly rate | `[NEEDS INPUT: segment rate band]` |
| `P` | Price per month | `[NEEDS INPUT: undecided; see ASM-032]` |
| `k` | Value-to-price multiple required | `[NEEDS INPUT: probe in interviews]` (ASM-034) |

**Two traps, stated before anyone fills these in.** (1) `N × A × U` counts **only** invoices that
would otherwise never have been paid; one that was always going to arrive, just late, belongs in the
carry term. Counting it as recovery inflates `V` by an order of magnitude and is the standard way
this category's cases go wrong. (2) `V` is not flat monthly value — it scales with invoice flow, so a
quiet month pays `P` for almost nothing. Models ignoring this overstate retention.

`[ASSUMPTION: the time term (H × W) alone cannot justify a subscription, because users rarely value unbilled admin hours at their billable rate. If true the case rests almost entirely on U — the least knowable variable. | conf: med]` (ASM-027, §11)

### 17.4 Venture-side — does Boss recover the build?

```
m = P − c_var      contribution per active user/month
B = C_fixed / m    users needed to cover fixed run cost
LTV = m / churn    payback = CAC / m
```

| Sym | Meaning | Status |
|---|---|---|
| `C_build` | One-time investment | `[NEEDS INPUT: honest build-hours × stated hourly opportunity value, plus cash outlay]` (ASM-036) |
| `C_fixed` | Fixed monthly run cost | `[NEEDS INPUT: hosting, domains, non-scaling third-party fees]` |
| `c_var` | Variable cost per user/month | `[NEEDS INPUT: outbound messaging + expected support minutes; depends on the RSK-006 channel decision]` |
| `churn` | Monthly user churn | `[NEEDS INPUT: unknowable pre-launch — model as a range, then measure]` |
| `CAC` | Blended acquisition cost | `[NEEDS INPUT: depends on RSK-008; if only organic is viable this is denominated in time, not money]` |

**Run-rate honesty, in advance.** In the usual case a new platform quietly costs more to run than the
legacy one. Here the buyer's comparison is against **₹0** — nothing is currently paid for the manual
behaviour, so there is no legacy cost to offset and the offering must be justified entirely on new
value created. That is a structurally harder business case than most.

### 17.5 The six gating inputs

| Gate | Input | Why it gates | Cheapest source |
|---|---|---|---|
| G1 | `U` recovery uplift | If ≈0, no configuration of the others saves the case | Measured before/after on a small cohort; no substitute |
| G2 | `A × N` at-risk value | Ceiling on what any uplift can be worth | Cohort interviews + invoice records |
| G3 | `P` at stated acceptance | Whether any viable price exists at all (RSK-003) | Price probe, same interviews |
| G4 | `C_build` | What payback must beat | Boss's own estimate — already known to him |
| G5 | `CAC` or a named organic channel | Whether users are reachable at all (RSK-008) | One concrete concentration of the segment |
| G6 | `churn` range | Whether `m` accumulates or leaks | Not obtainable pre-launch; bound as a range |

**G1-G3 and G5 clear in one interview round, G4 is already known** — four of six gates resolve before
any build commitment.

### 17.6 Decision rule, pre-committed

Stated now, while there is no number to rationalise around.

- **Proceed** only if `V ≥ k × P` at a price the cohort states as acceptable, **and** `m` clears
  `C_fixed` at a user count the identified channel can plausibly reach.
- **Stop** if the ASM-028 retrospective shows follow-up failure is not the primary cause of
  non-payment in a majority of cases → evaluate A3 instead.
- **Re-shape, not stop,** if the blocker is relational (RSK-002): the need is real, the framing is not.
- **Downside case, structurally:** the realistic bad outcome is not cost overrun — it is building
  something correct that nobody pays for (`U` real but small, `P` forced below `c_var + C_fixed/B`).
  Sunk cost is `C_build` in Boss's time, and none of it is discovered by building faster.

### 17.7 Unquantified benefits — quarantined

Excluded from every equation above and not to be folded in later: portfolio/credibility value of a
shipped commercial product independent of revenue; reusable capability transferable to Boss's other
initiatives; learning value of a live pricing and distribution test.

These may be the *actual* reason to proceed — but they accrue to Boss's career, not to a business
case, and folding them into the arithmetic is how unviable ventures get approved. If they are the
real motive, say so, and §17 becomes largely unnecessary rather than merely unpopulated.

---

## 18. Glossary

Terms used ≥3 times across this document, defined once here rather than re-explained at each occurrence. Compiled at assembly from definitions already present in the source sections — no new definitions introduced.

| Term | Definition |
|---|---|
| ASM | Assumption Register ID prefix (§11) |
| Audit trail (AUD-) | The evidenced log of chase, suppression, erasure and access events required by §10.4 |
| BR | Business Requirement ID prefix (§8) |
| BRD | Business Requirements Document — this document |
| CMP | Compliance-constraint ID prefix used in §10.2, one row per regulatory trigger condition |
| CON | Constraint ID prefix (§13) |
| Data Fiduciary | Under DPDP Act 2023, the entity that determines the purpose and means of processing personal data and bears the primary compliance duties (notice, erasure, grievance redressal) |
| Data Processor | Under DPDP Act 2023, an entity that processes personal data on behalf of a Data Fiduciary, under a written contract, without determining purpose/means itself |
| DEP | Dependency ID prefix (§12) |
| DLT | In this document's TRAI/TCCCPR context (§10.2 CMP-C C-1/C-2), the Distributed Ledger Technology platform used for commercial-SMS sender registration in India — unrelated to blockchain despite the shared acronym |
| DPDP Act 2023 | India's Digital Personal Data Protection Act 2023, the primary data-protection statute referenced throughout §10 |
| DSO | Days Sales Outstanding — average number of days an invoice remains unpaid past issuance/due date; used as KPI-01 |
| FRD | Functional Requirements Document — the companion document that will carry solution-level detail out of scope for this BRD (§9) |
| GDPR | EU General Data Protection Regulation; applies only if the CMP-D trigger fires (EU-established users or EU-located clients) |
| KPI | Key Performance Indicator ID prefix (§15) |
| MoSCoW | Prioritisation scheme used in §4 and §8: Must / Should / Could / Won't |
| NFR | Non-Functional Requirement ID prefix (§10); business-level quality and compliance requirements only, not solution-level detail |
| OBJ | Business Objective ID prefix (§2) |
| RACI | Responsible / Accountable / Consulted / Informed — the sign-off model used in §5 |
| RET | Data-retention requirement ID prefix (§10.3) |
| RSK | Risk Register ID prefix (§14) |
| STK | Stakeholder ID prefix (§5) |
| TCCCPR 2018 | Telecom Commercial Communications Customer Preference Regulations, 2018 — TRAI's regime governing commercial SMS sender registration and content templates in India (§10.2 CMP-C) |

---

## 19. Appendices

No appendices are attached to this draft. This section is retained per the master template's structure so its absence is explicit rather than silent.

---

## 20. Sign-off / Approval Matrix

Named individuals cannot be populated until DEP-01 (§12) resolves the ownership question. The rows below are structurally complete and awaiting names — this is not the same as an approved sign-off matrix, and this document is **not ready for sign-off** in its current state.

| Name | Role | Approving WHAT exactly | Date |
|---|---|---|---|
| `[NEEDS INPUT — see STK-01]` | Business Sponsor / Product Owner | Business requirements (§2, §3, §8) and scope (§4) — **not** the numeric objectives/targets in §2, which remain unpopulated pending baseline data | `[NEEDS INPUT]` |
| `[NEEDS INPUT — see STK-04]` | Legal / Compliance reviewer | Compliance surface and constraints only (§10, §13 CON-04/CON-05) — explicitly not a certification of regulatory compliance, since every CMP item in §10.2 remains a trigger condition pending counsel review | `[NEEDS INPUT]` |
| `[NEEDS INPUT — see STK-05]` | Engineering / Delivery owner | Feasibility of the business requirements as scoped (§8) and UAT/launch-readiness sign-off (§16 checklist) — **not** business requirements sign-off itself | `[NEEDS INPUT]` |

---

## Appendix — Readiness Report

`[NEEDS INPUT — a formal readiness-rubric scoring pass (structural quality per the skill's anti-patterns/standards rubric) was not run as part of this assembly. Running it is a legitimate next step, but assigning a score here without actually scoring against the rubric would itself be an invented number — the exact failure this document is built to avoid. See assembly-report.md for what this assembly pass did and did not verify.]`

**Honesty caveat, stated regardless of what any future score says:** a high structural score on this document would mean the sections are well-formed, traceable, and internally consistent. It would **not** mean the requirements are correct. This is a document built from one sentence; correctness can only come from validating ASM-001–ASM-037 against real freelancers, real clients, and qualified counsel — not from re-reading this draft more carefully.
