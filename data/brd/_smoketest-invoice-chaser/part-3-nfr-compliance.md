# Part 3 — §10 NFRs · Compliance Constraints · Data Retention · Audit Trail

*Agent 3 of 5. Feed-forward items for §4, §11, §13, §14 are listed at the end.*

> **Scope note.** This part identifies **regulatory surface and the controls it demands**. It states no
> legal conclusion and is not legal advice. Applicability questions are written as **trigger conditions
> to confirm or rule out** with qualified counsel — not as findings.

**Reading the tags.** The intake was one sentence with no volume, geography, channel or SLA data.
Numeric targets appear only where a regulation fixes them (three places: CGST §36 · Income-tax Rule
6F(5) · DPDP Rules 2025 Rule 7). Every other target is left open by design — a plausible-sounding
invented threshold would score well on a rubric and mislead delivery.
Status: **[R]** resolvable here · **[C]** counsel must confirm · **[B]** sponsor input needed.

---

## 10. Non-Functional Requirements

| ID | Category | Requirement | Target | Measurement | Driver / Traces to | Status |
|---|---|---|---|---|---|---|
| NFR-001 | Availability | Each scheduled chase shall execute **exactly once** per schedule instance; recovery from interruption shall not re-send a chase already dispatched | Zero duplicate dispatches per invoice per step | Dispatch log reconciled to schedule ledger, monthly | Duplicate-chase is a client-conduct harm, not just a defect | Must [R] |
| NFR-002 | Availability | Service availability during the daily send window | `[NEEDS INPUT: uptime commitment — and is a missed send window materially worse than UI downtime?]` | Uptime monitoring, monthly | OBJ-### *(reconcile at assembly)* | Must [B] |
| NFR-003 | Performance | Lag from payment recorded → **suppression of the next scheduled chase** | `[NEEDS INPUT: max acceptable lag]` | Timestamp delta, sampled monthly | Chasing a client who already paid is the product's highest-salience failure | Must [B] |
| NFR-004 | Performance | Interactive response, user-facing screens | `[NEEDS INPUT: is interactive speed a stated business concern at all, or is this a background-batch product where only NFR-003 matters?]` | APM under representative load | OBJ-### | Should [B] |
| NFR-005 | Scalability | Sustained and peak dispatch volume absorbed without breaching NFR-001/003 | `[NEEDS INPUT: invoices per user, clients per user, users at 12 months]` | Load test at agreed peak multiple, pre-launch + quarterly | `[ASSUMPTION: volume concentrates at month-end and FY-end rather than distributing evenly \| conf: med]` | Must [B] |
| NFR-006 | Security | Personal data of users **and their clients** protected by the safeguards required of a Data Fiduciary | Per DPDP Act 2023 §8(5) and DPDP Rules 2025 Rule 6 `[confirm sub-clauses + phased commencement]` | Independent assessment pre-launch, annual after | DPDP §8(5); Schedule penalty up to ₹250 cr `[verify current Schedule]` | Must [C] |
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
| NFR-019 | Usability | A user can see what is scheduled to go to which client, and stop it, without support contact | `[NEEDS INPUT: task success target, n]` | Usability testing at UAT | An automation the user cannot see or halt is how conduct risk becomes real | Must [B] |
| NFR-020 | Accessibility | Conformance level for user-facing surfaces | `[NEEDS INPUT: does the sponsor commit to a standard, and does any Indian statutory accessibility duty apply to this service?]` | Accessibility audit pre-launch | — | Should [B] |

### 10.1 Categories considered and judged not applicable

| Category | Verdict | Reason |
|---|---|---|
| Maintainability | Not stated at BRD level | Below the business/solution boundary (BABOK Tier 3) — belongs in the FRD |
| Interoperability | Deferred | Depends on whether the tool is the system of record or a layer over existing invoicing — unresolved, see RET-001 |
| PCI DSS v4.0.1 | Conditionally out of scope | Only if the CMP-F trigger fires. If the product never receives, transmits or stores cardholder data, merchant validation scope is materially reduced — but the trigger must be **confirmed, not assumed** |
| DR / RPO-RTO | Deferred to §13 | Cannot be stated until NFR-002 has a target |

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
unmanaged liability for its own users** — flagged to the §8 requirements agent.

`[NEEDS INPUT: does the vendor intend any use of client data beyond executing the user's instructions — analytics, benchmarking, model training, cross-user payment signals? A "yes" changes the role determination and the whole consent analysis.]`

### CMP-B — Lawful basis for contacting a third party who never signed up `[C]`

Grounds are consent (DPDP §4, §6) or a legitimate use (§7). §7(a) covers data a Data Principal
**voluntarily provided** without objecting — but the client gave their details to the **freelancer**,
not the platform. Whether that carries down the chain to an automated third-party sender is exactly
what counsel must answer. **Flagged, not resolved.** If the EU trigger fires, the sharper obligation is
**GDPR Art. 14** (data not obtained from the data subject), Art. 14(3)(a) at the latest one month.

**Control implied regardless of outcome:** at import the user attests to the basis on which they hold
each client's contact details, and the attestation is logged (AUD-004).

### CMP-C — Communication conduct *(the assigned domain issue)*

An automated dunning tool sends **unsolicited messages to a third party on the user's behalf**. Five
live constraints, each trigger-conditioned:

| # | Constraint | Trigger | Requirement if triggered | Status |
|---|---|---|---|---|
| C-1 | Registered sender identity (SMS, India) | Any commercial/service SMS to an Indian subscriber | Principal Entity registration on DLT, registered header, pre-registered content templates matched to the correct category, sender identity carried in the message body — TRAI TCCCPR 2018 | [C] |
| C-2 | **Who is the Principal Entity — vendor or each user?** | Same as C-1 | Unresolved. **Product-viability question, not just compliance:** if every freelancer must individually register on DLT before sending one reminder, SMS carries an onboarding cost that may make it unusable for the solo segment | [C][B] |
| C-3 | Opt-out in every message | (a) US **consumer** debt → Reg F, 12 CFR §1006.6(e), reasonable and simple opt-out in every electronic communication (b) EU → GDPR Art. 21 (c) India → DPDP §6 withdrawal, §13 grievance | Working opt-out on every channel, honoured **across** channels, evidenced per AUD-003 | [C] |
| C-4 | Frequency and quiet-hours ceiling | US consumer debt → Reg F §1006.14(b), presumed violation above 7 calls in 7 days per debt (calls only; electronic messages judged on cumulative harassment effect). India → **no general statutory cap is cited here for a non-regulated creditor**; RBI recovery-agent conduct norms bind Regulated Entities, which a freelancer is not `[C — confirm no conduct floor applies]` | Ceiling enforced and **configurable per regime**. **No default frequency or quiet-hours value is stated in this document** | [C][B] |
| C-5 | Escalation-language conduct | Any template asserting legal consequence ("legal action", "notice", "recovery proceedings") | Shall not dispatch automatically without explicit per-instance user confirmation (AUD-007). Two exposures for counsel: misrepresentation/coercion in collection conduct, and whether platform-authored legal-notice language raises unauthorised-practice-of-law questions | [C] |

**Also:** WhatsApp/Meta Business Messaging policy and email-provider AUPs are **contractual, not
statutory** — but a channel suspension is an availability event on the product's core function.
Routed to §14 Risks.

`[NEEDS INPUT: which channels are in scope — email only, or email + SMS + WhatsApp + voice? Every constraint above is channel-specific.]`

### CMP-D — GDPR `[C]`

**Trigger:** users established in the EU/EEA, **or** EU/EEA-located clients whose data is processed in
connection with offering them services. If it fires: Art. 6(1)(f) with a documented balancing
assessment, Art. 14 (per CMP-B), Art. 21, Art. 28, Art. 30, Art. 32, Art. 33, Art. 20.

`[ASSUMPTION: initial users are India-resident freelancers but a meaningful share invoice overseas clients, so the EU trigger is likelier to fire via the *client* side than the *user* side | conf: low — inferred from the intake being written in Hinglish and nothing else; must be validated before it drives any design decision]`

### CMP-E — GST e-invoicing and tax records `[C]`

**Trigger:** user's aggregate turnover crosses the e-invoicing threshold (CGST Rules r.48(4), ₹5 crore
`[verify current notification]`) **and** they issue B2B invoices **and** the tool generates or
transmits the invoice rather than only chasing one already issued.

`[ASSUMPTION: target-segment solo freelancers sit below the e-invoicing threshold, keeping IRN/QR out of scope | conf: med — plausible for the stated segment, unverified, and one agency-scale user breaks it]`

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
raises credit-information and defamation questions. **If it is not being built, record it as explicitly
out of scope in §4** so it cannot arrive later as an unreviewed enhancement.

---

## 10.3 Data retention requirements

**Governing tension:** DPDP §8(7) requires erasure once the purpose is served, while tax law requires
the *user* to keep the underlying records for years. One rule across the whole record set breaks one of
the two — retention must be set **per data class**.

| ID | Data class | Driver | Period | Status |
|---|---|---|---|---|
| RET-001 | Invoice and transaction records | The **user's own** statutory duty, not the vendor's | **72 months** from the due date of furnishing the annual return for that year — CGST Act 2017 §36 (extended to 1 year after final disposal of an appeal/investigation) where the user is GST-registered. Separately **6 years** from the end of the relevant assessment year — Income-tax Rules 1962, r.6F(5), specified professions | [R] for the citation; `[NEEDS INPUT: is the tool the system of record for invoices, or a chase layer over existing invoicing? If the latter, the vendor holds a copy rather than the record — different obligation.]` |
| RET-002 | Client personal data (contact details) | DPDP §8(7) + DPDP Rules 2025 Rule 8 | **No legally fixed period applies.** Third Schedule defaults (3 years) bind only e-commerce and social-media entities above 2 crore registered users and online gaming above 50 lakh — classes this product is not in `[ASSUMPTION: user counts stay far below those thresholds \| conf: high]`. Period is a **purpose-bound business decision**: `[NEEDS INPUT: how long after an invoice settles or is written off does a client's contact record still serve a purpose?]`. Rule 8(3)'s 48-hour pre-erasure intimation attaches to the Third Schedule regime — noted, not asserted as binding here | [B][C] |
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

## 10.5 Feed-forward

**→ §11 Assumptions** (each needs an owner and validation date this agent cannot assign):

| Ref | Assumption | Conf | Impact if wrong |
|---|---|---|---|
| NFR-005 | Volume concentrates at month-end / FY-end | med | Peak-shaped load invalidates the availability and scalability commitments |
| CMP-D | EU exposure likelier via overseas clients than EU-resident users | **low** | GDPR lands on a different trigger than designed for; Art. 14 becomes live |
| CMP-E | Users sit below the GST e-invoicing threshold | med | One agency-scale user brings e-invoicing into scope |
| RET-002 | User counts stay far below DPDP Third Schedule thresholds | high | Statutory default retention periods would apply |

**→ §13 Constraints:** DR/RPO-RTO blocked until NFR-002 has a target.

**→ §14 Risks:** (i) channel-provider suspension (Meta policy, email AUP) disabling the core function;
(ii) DLT Principal-Entity burden landing on individual users, making SMS commercially unusable for the
solo segment (C-2); (iii) CMP-A resolving against the vendor, converting it into a Data Fiduciary with
the full obligation set.

**→ §4 Scope:** CMP-H — add an explicit out-of-scope entry for cross-user payment-reputation features.

**→ Assembly:** `OBJ-###` placeholders in the Driver column must be reconciled against §2 or the
upward-traceability check fails on orphaned NFRs.

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
