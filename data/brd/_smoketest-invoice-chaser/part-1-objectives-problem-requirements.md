## 3. Background / Problem Statement

**Five Whys — traceability of the stated need**

1. **WHY build this tool?** → Because freelancers need unpaid invoices chased automatically.
   *Known — verbatim intake: "freelancers ke liye ek tool jo unpaid invoices automatically chase kare."*
2. **WHY do freelancers need invoices "chased" at all?** → Because client invoices are not being paid by an agreed due date, i.e., invoices go overdue.
   `[ASSUMPTION: this is a direct, low-risk reading of the plain meaning of "unpaid invoices" in the intake — the existence of overdue invoices, not a specific rate or cause of them | conf: high]`
3. **WHY are client invoices going overdue** — what is the actual root cause? Candidates: the client forgot; the client is disputing the amount or the delivered work; the client has their own cash-flow problem; the client's own accounts-payable process has no reminder step; or the client is deliberately delaying because the freelancer has limited leverage to enforce payment terms.
   `[NEEDS INPUT: Boss has not specified the dominant root cause. This is not a formality — a "forgot" problem is solved by a reminder; a "disputing the invoice" or "client has no cash" problem is not, and a reminder aimed at the wrong root cause can actively damage the freelancer-client relationship (see OBJ-003).]`
4. **WHY is the freelancer's current manual chasing process insufficient** — time cost, inconsistency, avoidance/awkwardness around asking a client for money, no visibility into which invoices are actually overdue, or something else?
   `[NEEDS INPUT: no baseline exists on current freelancer behaviour, time spent chasing, or the emotional/relationship cost of chasing today.]`
5. **WHY hasn't this already been solved** — most invoicing platforms already used by freelancers (generalist accounting/invoicing SaaS) ship built-in payment-reminder features. What does this tool do that those don't, and for which freelancers specifically?
   `[NEEDS INPUT: the single largest open gap in this intake. Without an answer, this BRD cannot establish whether the initiative is a net-new product, a competitive-parity feature, or a fix for an underserved sub-segment (e.g., freelancers invoicing outside any formal tool, via email/WhatsApp/manual PDF).]`

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

## 2. Business Objectives

Because §3 could not establish a validated baseline for any metric, the objectives below are structurally SMART (each names a direction, a proposed measurement method, and a trace to requirements and a KPI) but are **numerically incomplete by design** — a fabricated baseline or target would score as "complete" while being worthless. Read OBJ-001 through OBJ-004 as the exact list of data that must be collected before this BRD can go to sign-off, not as agreed targets.

> **OBJ-001 — Faster invoice collection.** Reduce the average number of days an invoice remains unpaid past its due date, for freelancers using the solution, from `[NEEDS INPUT: baseline days-overdue for the target freelancer segment — no current data supplied]` to `[NEEDS INPUT: target days-overdue and target date]`, measured via invoice due-date vs. payment-received-date, tracked monthly. **Traces to:** BR-001, BR-002, BR-005. **KPI:** see §15 (not drafted in this excerpt).

> **OBJ-002 — Reduced manual chasing effort.** Reduce the time a freelancer personally spends following up on overdue invoices, from `[NEEDS INPUT: baseline — no time-and-motion or survey data available]` to `[NEEDS INPUT: target]`, measured via `[ASSUMPTION: periodic in-app or survey-based self-report of time spent chasing, since no objective instrumentation of the freelancer's pre-tool manual process exists | conf: low]`. **Traces to:** BR-002, BR-003, BR-009.

> **OBJ-003 — Preserve the freelancer-client relationship while chasing.** Hold the rate of client friction attributable to automated chasing (e.g., a reminder sent after payment, a wrong-amount reminder, a client complaint about tone or frequency) at or below `[NEEDS INPUT: acceptable threshold — not defined by Boss]`, measured via `[ASSUMPTION: freelancer-reported incident log within the solution | conf: low]`. **This objective is the initiative's non-negotiable constraint: automation must not increase net client friction relative to the freelancer's own prior manual chasing.** **Traces to:** BR-003, BR-004.

> **OBJ-004 — Regulatory-safe automated client communication.** Ensure `[NEEDS INPUT: 100%, or an owner-defined percentage]` of automated chase communications comply with applicable data-protection and commercial-communication law in the jurisdiction(s) of both freelancer and client — provisionally scoped to India's DPDP Act 2023, `[ASSUMPTION: target market is India-based freelancers and India-based or India-serving clients, consistent with the commissioning context; not confirmed by Boss | conf: low]` — measured via `[NEEDS INPUT: compliance audit method, cadence, and named owner not yet defined]`. **Traces to:** BR-006, BR-008.

---

## 8. Business Requirements

No stakeholder elicitation session has occurred against this intake — every requirement below is inferred from a single unelaborated sentence. Source is therefore marked per-row as either the intake statement directly, or a flagged assumption/needs-input where the requirement required inference beyond it.

| ID | Requirement | Traces to | Priority | Source | Acceptance |
|---|---|---|---|---|---|
| BR-001 | The solution shall identify, without manual flagging by the freelancer, which invoices have passed their stated due date and remain unpaid. | OBJ-001 | Must | Intake, verbatim (a precondition of "chasing unpaid invoices") | AC-BR001 |
| BR-002 | The solution shall initiate contact with the client on an overdue invoice automatically, without the freelancer manually triggering each individual follow-up. | OBJ-001, OBJ-002 | Must | Intake, verbatim ("automatically chase") | AC-BR002 |
| BR-003 | The freelancer shall be able to pause, stop, or override automated chasing for any specific invoice or client, at any time before or during the chase sequence. | OBJ-002, OBJ-003 | Must | `[ASSUMPTION: inferred as necessary to protect ongoing/repeat-client relationships, a common characteristic of solo-operator freelance work; not stated in intake | conf: med]` | AC-BR003 |
| BR-004 | The solution shall stop chasing an invoice, and shall not send any further reminder for it, as soon as that invoice is recorded as paid. | OBJ-003 | Must | `[ASSUMPTION: chasing a client after payment is a known failure mode in this product category and would directly work against OBJ-003 | conf: med]` | AC-BR004 |
| BR-005 | The solution shall support more than one escalation stage for a single overdue invoice (e.g., an earlier-stage reminder distinct from a later-stage one), rather than a single repeated message. | OBJ-001 | Should | `[ASSUMPTION: common practice in payment-reminder products generally; not confirmed by Boss | conf: low]` | AC-BR005 |
| BR-006 | The solution shall handle all client and invoice data — including any client personal data (name, contact details, payment status) — in accordance with applicable data-protection law for the jurisdiction(s) in which the freelancer and their clients operate. | OBJ-004 | Must | Classification-supplied compliance candidate (DPDP Act 2023); `[NEEDS INPUT: confirm target jurisdiction(s) — DPDP Act 2023 (India) is the working assumption, not confirmed by Boss]` | AC-BR006 |
| BR-007 | The solution shall maintain a record of every automated chase action taken against an invoice (what was attempted and when), retrievable by the freelancer. | OBJ-002, OBJ-003 | Should | `[ASSUMPTION: inferred as necessary for the freelancer to defend against a client dispute over chasing conduct, and to make BR-004's "stop on payment" behaviour auditable | conf: med]` | AC-BR007 |
| BR-008 | The solution shall obtain and record freelancer confirmation that automated communication to a given client is permitted, before that client is contacted automatically for the first time. | OBJ-004 | Must | `[NEEDS INPUT: whether client-side consent/notice is legally required depends on the communication channel and jurisdiction, neither of which is decided; scoped conservatively to Must pending confirmation of India IT Act 2000 / sector consent obligations for commercial electronic communication | conf: low]` | AC-BR008 |
| BR-009 | The freelancer shall be able to see the current chase status (not yet due / overdue / in active chase / paused / paid) of every outstanding invoice in one consolidated view. | OBJ-002 | Should | `[ASSUMPTION: baseline usability need for OBJ-002 — reducing chasing effort implies the freelancer can see status without re-deriving it manually | conf: med]` — `[Stakeholder Requirement — solution TBD in FRD]` | AC-BR009 |

**Expanded form — the two highest-risk requirements**

> **BR-003** | **Priority: Must Have** | **Traces to: OBJ-002, OBJ-003** | **Source: `[ASSUMPTION | conf: med]`, not directly stated in intake**
>
> The freelancer shall be able to pause, stop, or override automated chasing for any specific invoice or client at any time before or during the chase sequence, such that no further automated contact is sent once paused or stopped.
>
> *Acceptance: AC-BR003. Not in scope: the specific control surface (button, setting, command) used to pause/stop — that is an FRD/UX decision.*
> *Why Must, not Should: without an override, an automated chase system removes exactly the judgment a freelancer currently exercises manually — this is the single largest relationship-risk in the entire initiative (see OBJ-003), and it cannot be a later add-on.*

> **BR-008** | **Priority: Must Have** | **Traces to: OBJ-004** | **Source: `[NEEDS INPUT: jurisdiction and channel unconfirmed]`**
>
> The solution shall require and record freelancer confirmation that automated contact to a given client is permitted before the first automated chase message to that client is sent.
>
> *Acceptance: AC-BR008. Not in scope: the legal sufficiency of any specific consent mechanism — that determination requires the jurisdiction/channel inputs flagged in §3 and BR-006, and is `[NEEDS INPUT]` for legal review before build.*

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
       confirmed per BR-006's Source note]

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
- [ ] BR-006 and BR-008 compliance behaviour signed off by `[NEEDS INPUT: named legal/compliance reviewer — none identified yet]` against the confirmed jurisdiction
- [ ] BR-003 and BR-004 specifically verified against the "chase continues after payment" and "cannot be stopped mid-sequence" failure modes, given their direct link to OBJ-003 (relationship protection)
- [ ] OBJ-001 through OBJ-004 baseline data collection (per §3's NEEDS INPUT list) completed and logged before any numeric target is locked
- [ ] Sign-off obtained from every "A" role in the Requirements-sign-off RACI column (§5 — not drafted in this excerpt)
