> **Agent note:** This file contains only §4 (Project Scope), §6 (Current State / As-Is), §7 (Future
> State / To-Be) of the BRD. It is drafted by a parallel agent alongside §1-3, §5, §8-20 — sections
> here reference other sections (e.g. "§3", "BR-IDs") by number only; those numbers are owned by
> sibling agents and must be reconciled at assembly, not invented here.
>
> **Root-cause caveat that governs everything below:** the intake ("a tool that automatically chases
> unpaid freelancers' invoices") is a solution statement with no confirmed problem behind it — no
> interview, no observed workflow, no data on invoice volume, chase frequency, or where freelancers
> actually lose the money. Per the anti-fabrication rule, the As-Is below is a **hypothesised**
> process, not a documented one, and is tagged accordingly throughout. It should not be treated as
> validated until a discovery workshop or freelancer interviews confirm or correct it.

---

## 4. Project Scope

Two scope-defining questions are still open and are listed as `[NEEDS INPUT]` below rather than
silently resolved onto either side of the line — placing them on one side without an answer would
misrepresent a decision as already made.

| # | In Scope (Release 1) | MoSCoW | # | Out of Scope (Won't Have, this release) | Rationale for exclusion |
|---|---|---|---|---|---|
| IS-1 | Track payment status (paid / unpaid / overdue) for invoices the freelancer has already issued | Must | OS-1 | Creating or generating the invoice itself | Distinct, mature capability already served by existing invoicing tools; combining would roughly double build scope for a segment that plausibly already issues invoices some other way `[ASSUMPTION: target freelancers already issue invoices through some existing means — own tool, template, or accounting software — before ever reaching this product | conf: med]` |
| IS-2 | Send automated, freelancer-configured reminder messages to the client as an invoice ages | Must | OS-2 | Collect or process the payment itself (card/bank funds movement) | Money movement pulls PCI-DSS and payment-licensing obligations into scope; the intake's word "chase" is read here as communication, not funds collection — that reading is itself unconfirmed, see NI-1 |
| IS-3 | Escalate message tone/frequency on a configurable schedule as an invoice's days-overdue count increases | Should | OS-3 | Legal escalation / third-party debt-collection agency handoff | Separate regulated domain (recovery-agent licensing varies by Indian state); this release stops at surfacing the invoice for the freelancer's own next step, see To-Be step 1.6 |
| IS-4 | Let the freelancer pause, edit, or manually trigger an off-cycle message, overriding the automated cadence | Should | OS-4 | Full accounting / bookkeeping / GST e-invoicing | Distinct regulated domain; GST e-invoicing applies only above Rs 5cr annual turnover `[ASSUMPTION: not applicable to the target solo/micro-freelancer segment | conf: med]` — confirmed only once NI-2 (target segment) is answered |
| IS-5 | Give the freelancer a basic outstanding-amount / aging-bucket view across all tracked invoices | Could | OS-5 | Multi-currency / cross-border invoicing | Target geography is undetermined (NI-2); scoping currency handling now would be guessing rather than deciding |

**Open boundary decisions — genuinely undecided, not placed on either side:**

- `[NEEDS INPUT: NI-1]` Does "chase" ever extend to the tool detecting that a payment was received
  (even without moving funds itself) — and if so, is that detected automatically (bank/payment-gateway
  signal) or marked manually by the freelancer? This changes whether IS-1 is a pure manual-entry
  status log or has an integration dependency, and it is the fact that determines whether OS-2 stays
  safely excluded.
- `[NEEDS INPUT: NI-2]` Is the target market India-only freelancers, or global? This determines the
  compliance frame (DPDP alone vs. DPDP + GDPR), whether OS-5 (multi-currency) should really be a
  Release-2 Should rather than an outright exclusion, and whether the GST-e-invoicing assumption
  under IS-4/OS-4 holds.
- `[NEEDS INPUT: NI-3]` Does invoice data enter this product by manual entry, file import, or a live
  integration with an existing invoicing/accounting tool the freelancer already uses? This is a
  scope-defining boundary for IS-1 and cannot be safely assumed either way — it changes both the
  build shape and OS-1's "we don't touch invoice creation" boundary (an integration still means
  reading someone else's invoice data, which is a data-sharing/DPDP question in its own right).

---

## 6. Current State (As-Is) Process

**Status of this section: hypothesised, not observed.** No freelancer interview, time-and-motion
study, or workshop has taken place. Every step below is tagged `[ASSUMPTION]` at the confidence the
underlying claim plausibly deserves for the freelance-services segment generally — none of it is
specific to a named freelancer, tool, or dataset. Where a fact is not safely assumable at all — because
it requires seeing the actual behaviour, not just describing a plausible pattern — it is flagged as
`[NEEDS INPUT / requires observation or interview]` rather than guessed.

**Swimlanes: Freelancer · Client**

1.1 (Freelancer) Issues an invoice to the client, stating an amount and a due date `[ASSUMPTION: invoices are issued with an explicit due date, as is standard freelance-services practice | conf: high]`.

1.2 (Freelancer) Tracks which outstanding invoices are approaching or past their due date `[ASSUMPTION: this tracking is informal — memory, a spreadsheet, or scanning a bank statement — rather than a dedicated system, since the intake proposes building one from scratch | conf: low]`. **Pain point:** no forcing function surfaces an overdue invoice; detection depends entirely on the freelancer happening to check.

1.3 (Freelancer) Notices — or fails to notice in a timely way — that an invoice has gone overdue. **Pain point:** detection latency is itself unmeasured `[NEEDS INPUT / requires observation: how many days typically elapse between due date and the freelancer first noticing]`.

1.4 (Freelancer) Decides whether and when to send a follow-up, and drafts that message individually each time `[ASSUMPTION: messages are composed fresh per instance rather than from a saved template, and timing is ad hoc rather than on a fixed cadence | conf: low]`. **Pain point:** the decision to chase competes against `[ASSUMPTION: reluctance to jeopardise the client relationship, a commonly cited reason freelancers under-chase — plausible for this segment but not confirmed for this engagement | conf: med]`; the effort and discomfort of this step are candidates for the actual root cause behind "invoices go unpaid," but that causal claim is unverified.

1.5 (Client) Responds and pays, or does not respond; if not, the process loops back to 1.3/1.4 on an ad hoc basis, with no defined interval or count for how many follow-ups are attempted before the freelancer gives up. **Pain point:** the loop has no structure — cadence, channel, and escalation are entirely freelancer-dependent, so outcomes vary case by case rather than following a repeatable pattern.

1.6 (Freelancer) Eventually is paid, writes the amount off, or escalates informally (e.g. a phone call, or involving a third party) `[ASSUMPTION: no formal escalation path or defined "close" state exists today | conf: low]`. **Pain point:** there is no explicit end state — an unresolved invoice can drift indefinitely rather than being surfaced for a deliberate decision.

**What this section cannot responsibly resolve by further Q&A** — these require either a discovery
workshop, freelancer interviews, or direct observation of an actual chase cycle, not a question Boss
can answer from memory alone:

- Invoice volume and overdue rate (how many invoices a typical target freelancer issues per month, and what fraction go overdue)
- Actual time spent per week on chasing, and the actual channel mix used (email vs. WhatsApp vs. phone vs. platform messaging)
- The real distribution of days-overdue-to-resolution, and how many follow-ups it typically takes
- Whether relationship-risk hesitation (1.4) is in fact the dominant driver of non-payment, versus e.g. client cash-flow problems, disputed scope, or simple forgetfulness — these have different fixes and cannot be told apart without qualitative input
- What tool(s), if any, freelancers already use today for invoicing or tracking (feeds directly into NI-3 in §4)

---

## 7. Future State (To-Be) Process

Mirrors §6's numbering 1:1. Written at business-process level — it states what capability closes each
As-Is pain point, not which screen, database, or integration delivers it. Each step notes which As-Is
gap it closes; formal `BR-ID` cross-references are added at assembly once §8 assigns its IDs.

**Swimlanes: Freelancer · Client · Product (automated capability)**

1.1 (Freelancer) Issues an invoice to the client with a due date, as today; that invoice and due date become trackable by the product from the moment it is created — mechanism (manual entry vs. import vs. integration) is undecided, see §4 NI-3. `[Stakeholder Requirement — solution TBD in FRD]`

1.2 (Product) Automatically monitors due dates and identifies an invoice as overdue without requiring the freelancer to check — **closes the 1.2 pain point** (no forcing function).

1.3 (Product) Automatically detects the overdue state at the moment it occurs and triggers the chase workflow — **closes the 1.3 pain point** (detection no longer depends on the freelancer noticing).

1.4 (Product, with Freelancer override) Sends a follow-up message to the client on a freelancer-configured cadence and tone, with tone/frequency escalating as days-overdue increases; the freelancer retains the ability to pause, edit, or send an off-cycle message manually rather than being fully hands-off — **closes the 1.4 pain point** (removes the per-instance composition burden) while `[ASSUMPTION: preserving freelancer override addresses the relationship-risk hesitation identified at 1.4, rather than removing the freelancer's judgment entirely | conf: med — this is the product's central bet, and it rests on an unconfirmed root cause]`.

1.5 (Client / Product) Client responds or pays; the product captures the resulting payment-status update — **closes the 1.5 pain point** (the follow-up loop now runs on a defined, repeatable cadence instead of ad hoc timing). Whether status capture is automatic or freelancer-marked is still open (§4 NI-1).

1.6 (Product) For an invoice that remains unpaid past the top of the configured escalation ladder, the product surfaces it as needing the freelancer's own next decision (write off, informal escalation, or handoff outside the tool per §4 OS-3) — **closes the 1.6 pain point** (drift becomes an explicit decision point instead of an undefined state).

**Delta — what changes and why:**

- Detection moves from freelancer-memory-dependent (1.2, 1.3) to automatic — removes the single point of failure the As-Is process has no backup for.
- Chase timing moves from ad hoc, effort-and-mood-dependent (1.4) to a configurable, repeatable cadence — while deliberately keeping a manual override, because the hypothesised root cause (relationship-risk hesitation) is a judgment call the freelancer plausibly still wants to make on individual clients.
- The process gains a defined end state (1.6) where none existed before — turns silent drift into a decision the freelancer is prompted to make.

**Implementation considerations:**

- **Change management:** the freelancer is trusting the product to send messages to their own clients under their name — this is a relationship-risk transfer, not just a workflow change, and (per 1.4) is the step most likely to need a review-before-send option rather than fully autonomous sending. This is a design lean, not a decided requirement.
- **Training:** limited to a one-time cadence/tone configuration per freelancer; no ongoing training burden is implied by anything confirmed so far.
- **System/integration dependency:** the entire shape of 1.1-1.2 depends on §4's NI-3 (manual entry vs. import vs. integration); this should be resolved before any solution design proceeds, since it changes both build effort and DPDP-relevant data-handling scope (reading a third party's invoicing data on the freelancer's behalf).
