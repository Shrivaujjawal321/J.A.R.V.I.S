## 5. Stakeholder Analysis + RACI

**Before the table — one unresolved question that determines everything below it:**

> `[NEEDS INPUT: Is this (a) Boss's own product with Boss as Business Sponsor, (b) a client
> engagement where a named external client company is the sponsor, or (c) a hypothetical/portfolio
> exercise with no real sponsor? The Business Sponsor row, the escalation path, and the entire
> "Requirements sign-off" column are unassignable to a real name until this is answered — assigning
> a placeholder person here would be inventing a stakeholder, which this document does not do.]`

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
  and churn risk in this initiative — see NFR/Constraint cross-references below — and it must be
  visible here even though it carries no RACI role.

| STK-ID | Stakeholder | Role | Interest | Influence | RACI (Requirements sign-off) | RACI (UAT / launch-readiness sign-off) |
|---|---|---|---|---|---|---|
| STK-01 | `[NEEDS INPUT: name — Business Sponsor]` | Business Sponsor / Product Owner | High — owns the business case and the go/no-go decision | High | **A** | C |
| STK-02 | Freelancer (solo-operator, target ICP) | Primary user & buyer | High — direct beneficiary; wants unpaid invoices collected without spending personal time or damaging the client relationship themselves | Low (no formal governance seat; influences roadmap only via research/beta feedback) | C | R (beta participant) |
| STK-03 | Freelancer's client / invoice payer | **Non-opted-in recipient of the product's core automated action** ("the chased party") | High and **structurally opposed** to STK-02's interest on cadence/tone — wants to not be nagged, not have the business relationship soured, not be contacted by something that reads as a collections process | None (has no seat, was never consulted) — but is the primary source of downstream risk (complaint, relationship loss, legal exposure) that can force a redesign | N/A — not a governance participant by definition | N/A — not a governance participant by definition |
| STK-04 | `[NEEDS INPUT: name — Legal / Compliance reviewer]` | Compliance oversight — DPDP Act 2023 (processing the client's personal data: name, email, phone, invoice/payment history) and review of chase-communication content for anything that reads as unlicensed debt-collection conduct | High — a single mishandled chase sequence is a legal/reputational incident, not a bug | Medium–High | C | C |
| STK-05 | `[NEEDS INPUT: name — Engineering / Delivery owner]` | Delivery accountable | High | High | R | **A** |
| STK-06 | Freelancer's bookkeeper/accountant `[ASSUMPTION: some share of the target segment uses a third-party bookkeeper who also touches invoice status | conf: low]` | Secondary/indirect user | Low–Medium | Low | I | I |

**Escalation path:** `[NEEDS INPUT: who has authority to resolve a tone/frequency dispute between
the freelancer's collection goal (STK-02) and client-relationship risk (STK-03's downstream effect
on churn/complaints/legal exposure)? In the exemplar bank BRD this sits with the Business Sponsor;
here it cannot be assigned until STK-01 is named.]`

**Convention check:** exactly one **A** per column, both currently held by `[NEEDS INPUT]` seats —
correct, since inventing a named accountable person would violate the no-fabrication rule more than
leaving the seat visibly open.

---

## 12. Dependencies

| DEP-ID | Dependency | Owning team | Expected date | Impact if late/unmet |
|---|---|---|---|---|
| DEP-01 | Resolution of the ownership question (Business Sponsor identity — Boss's own product vs. client engagement vs. hypothetical) | `[NEEDS INPUT: owning team]` | `[NEEDS INPUT]` | **Blocking** — STK-01, STK-04, STK-05, the entire Requirements-sign-off RACI column, and §17 Cost-Benefit cannot be completed without it |
| DEP-02 | Freelancer must maintain an accurate, current record of which invoices are unpaid and their amounts (their existing invoicing/bookkeeping practice, whatever form it takes today) | Freelancer (external, outside the delivery team's control) | Ongoing, at point of onboarding | High — the tool's core action (chasing) is only as correct as the freelancer's own unpaid-invoice data; a stale record causes chasing an already-paid client, which is the single fastest way to destroy trust in the product |
| DEP-03 | Legal/compliance review and written guidance on what constitutes permissible automated-payment-reminder conduct toward a third party (vs. conduct that reads as unlicensed debt collection) under Indian law, before any chase sequence reaches a real client | `[NEEDS INPUT: name — Legal/Compliance owner, see STK-04]` | `[NEEDS INPUT — should precede first client-facing send, not follow it]` | **High** — undefined; a chase sequence that crosses into harassment/collection-agency-style conduct is a legal and reputational failure, not a product-quality one |
| DEP-04 | A reliable, non-spam-flagged outbound communication channel (email and/or other messaging) reaching the freelancer's client, with acceptable deliverability at the volumes this tool would generate | `[NEEDS INPUT: owning team]` | `[NEEDS INPUT]` | Medium — without deliverability, the core value proposition (chasing actually happens) silently fails; would show up first as a metrics anomaly (§15) rather than a visible outage |
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
| CON-04 | DPDP Act 2023 applies to any processing of the client's personal data (name, email, phone, payment status) collected and processed on the freelancer's behalf | Regulatory | Enacted law; applicability inherited from classification `[ASSUMPTION: DPDP Act 2023 applicability confirmed at classification stage | conf: high]` — current rules-notification/enforcement timeline and whether Significant Data Fiduciary thresholds could apply are `[NEEDS INPUT]` | Classification doc, this project's `data/brd/_smoketest-invoice-chaser/classification.md` |
| CON-05 | The product's core action targets a person (the client) who is not the customer and has not consented to being contacted by this tool — this is a standing constraint on every chase-related requirement, not a one-time risk item | Legal/ethical, self-imposed by the nature of the initiative | Every chase-communication requirement must be reviewed against unlicensed-debt-collection and harassment exposure before build, not after | Derived directly from the intake's own framing ("automatically chase") — not an external source, flagged as a structural constraint the requirements-drafting section must design around |
| CON-06 | Untouchable legacy system to integrate with | Technical | None identified — `[ASSUMPTION: this is a greenfield build with no mandated legacy integration, inferred from the intake describing a new standalone tool rather than an add-on | conf: med]` | Intake inference only |

---

## 15. Success Metrics / KPIs

**Read this table with its limitation stated up front, not buried:** no baseline data of any kind
was supplied for this initiative. Per the anti-fabrication rule, every Baseline and Target cell
below is `[NEEDS INPUT]` rather than an invented number — a metric with a placeholder baseline is
correct here; a metric with a confident invented baseline would be a defect. What follows is the
candidate metric *set* (what should be measured and how), not the numbers themselves.

**Cross-section flag:** the template's loop-closing rule requires every number in this table to
already appear in §2 Objectives / §3 Problem Statement. Those sections are being drafted by a
different parallel agent; with no baseline supplied anywhere in the intake, there is nothing for
either section to reconcile against yet. This table should be re-checked against the final §2/§3 for
numeric consistency before the document is assembled — flagging this explicitly rather than silently
assuming alignment.

| KPI-ID | Metric | Baseline | Target | Measurement Method | Measurement Date | Owner | Traces to |
|---|---|---|---|---|---|---|---|
| KPI-01 | Days Sales Outstanding (DSO) for freelancers using the tool, vs. their own pre-tool DSO | `[NEEDS INPUT]` — requires each pilot freelancer's own pre-adoption DSO, not an industry figure | `[NEEDS INPUT]` | Self-reported or connected-record DSO comparison, pre- vs. post-adoption, per user | `[NEEDS INPUT]` | `[NEEDS INPUT — depends on STK-01]` | `[NEEDS INPUT: OBJ-ID, pending §2]` |
| KPI-02 | Invoice collection rate — % of chased invoices paid within N days of the chase sequence starting | `[NEEDS INPUT]` | `[NEEDS INPUT]` | In-product tracking: chase-sequence-start timestamp vs. mark-paid timestamp (see DEP-05) | `[NEEDS INPUT]` | `[NEEDS INPUT]` | `[NEEDS INPUT]` |
| KPI-03 | **Client-side harm signal — complaint / opt-out / "stop contacting me" rate per 100 chase sequences sent** (counter-metric; must not be traded away for KPI-01/02) | `[NEEDS INPUT]` | `[NEEDS INPUT — should be a ceiling, not a floor, e.g. "no more than X per 100," once X is set with real data]` | Count of client replies/complaints flagged as objection, opt-out, or escalation, per chase sequence sent | `[NEEDS INPUT]` | `[NEEDS INPUT]` | `[NEEDS INPUT]` |
| KPI-04 | Freelancer time saved on manual chasing (hours/month) | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Self-reported survey at onboarding (pre-tool estimate) vs. quarterly follow-up | `[NEEDS INPUT]` | `[NEEDS INPUT]` | `[NEEDS INPUT]` |
| KPI-05 | Freelancer retention/churn correlated with active use of the chase feature | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Cohort retention analysis, chase-feature users vs. non-users | `[NEEDS INPUT]` | `[NEEDS INPUT]` | `[NEEDS INPUT]` |
| KPI-06 | Deliverability/reach of chase communications (% successfully delivered to the client, independent of DEP-04 channel choice) | `[NEEDS INPUT]` | `[NEEDS INPUT]` | Delivery-confirmation logging per chase send | `[NEEDS INPUT]` | `[NEEDS INPUT]` | `[NEEDS INPUT]` |

**Why KPI-03 is not optional:** every other metric in this table measures whether the tool works for
the buyer (the freelancer). None of them would catch the tool succeeding at collection while quietly
damaging the freelancer's client relationships or crossing into harassment — the exact failure mode
CON-05 exists to prevent. A success-metrics table for this specific product that omits a counter-metric
on the non-consenting party is, by the standard this document follows, incomplete on its face.
