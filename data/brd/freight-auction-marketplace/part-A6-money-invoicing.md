# A6 — Charges, Invoicing & Settlement

**Scope note.** Money model only: the charge a load actually costs, who bills whom, when it becomes
payable, and how it is collected and reported. Regulatory licensing this money movement may trigger
is A7's; unit economics/take-rate strategy is A10's; claim adjudication outcomes are A8's — this
section tracks only what happens to money while those are unresolved.

## 1. Who invoices whom — the load-bearing open decision

`[NEEDS INPUT: which of the three models below does the client intend? This single choice determines
whether the platform needs broker authority, carries credit risk, and needs working capital — it is
upstream of nearly every other requirement in this section.]`

| Model | Structure | Platform requires | Consequence |
|---|---|---|---|
| **A — Pass-through software** | Carrier invoices shipper directly; platform never touches the freight charge | No broker authority; no BMC-84 bond (confirm with A7) | Cannot monetize a spread; revenue is a listing/subscription/transaction fee (§8). No credit risk, no factoring exposure on the freight leg — but weak control over collection quality and no assurance the invoice matches the rate confirmation |
| **B — Broker of record (buy/sell)** | Platform contracts separately with shipper and carrier, invoices the shipper the sell rate, pays the carrier the buy rate (≈ winning bid + accessorials), keeps the spread | FMCSA property broker authority, BMC-84 surety bond / BMC-85 trust, BOC-3 (A7 owns citation) — plus working capital or a financing facility (§6) | Closest fit to the stated auction → invoice flow. Platform carries shipper credit risk, owns factoring/NOA handling (§4), and can offer quick pay (§5) as a margin lever. Highest capital and compliance burden |
| **C — Commission-only marketplace** | Carrier invoices shipper directly for freight; platform separately bills its own commission/fee | May still trigger money-transmission review if funds pass through the platform even transiently (flag to A7) | Capital-light like A, monetizable like B, but the platform is not party of record on the freight contract — weaker leverage when an invoice is disputed |

`[ASSUMPTION: intake.md's "Invoice generation" step means at minimum a platform-generated invoice
artifact, not necessarily a platform-issued bill for the freight charge itself | conf: low]` —
resolved once §1 is answered.

## 2. Rate confirmation and the charge model

**BR-600** (Must · → OBJ-005, OBJ-002) The system shall generate a rate confirmation at
`AWARD_ACCEPTED` carrying the winning bid as base linehaul rate, the fuel-surcharge method, and the
applicable accessorial rate table, requiring carrier acknowledgement before `PICKUP_SCHEDULED`.
*Source: derived from spine §3 + intake happy path. Acceptance: no load reaches `PICKUP_SCHEDULED`
without an acknowledged rate confirmation on file.*

**BR-601** (Must · → OBJ-005) Final invoice amount = rate-confirmation base rate + verified
accessorials actually triggered + fuel surcharge per the confirmed method − any short-pay/OS&D
deduction pending an A8 claim. The bid alone is never the invoice. *Source: task mandate ("A4/A5
define triggering events; A6 defines charge treatment"). Acceptance: AC-BR601 — invoice line-item
total reconciles to rate confirmation + accessorial log.*

**Accessorials** — A4/A5 own the triggering event; A6 owns charge treatment. Every rate/threshold is
`[NEEDS INPUT]` — none invented:

| Accessorial | Triggering event (owner) | Charge treatment |
|---|---|---|
| Detention | Free time exceeded at pickup/drop (A4/A5) | Per-hour rate beyond `[NEEDS INPUT: free-time hours]`, requires timestamped arrival/departure evidence |
| TONU | `SHIPPER_NOT_READY` / `CANCELLED_BY_SHIPPER` post-dispatch (A1/A4) | Flat fee `[NEEDS INPUT]`, no linehaul charge |
| Layover | Overnight hold not attributable to carrier (A4) | Flat per-night fee `[NEEDS INPUT]` |
| Lumper fee | Third-party load/unload labor paid by carrier (A4/A5) | Reimbursed at receipted cost, not estimated |
| Driver assist | Carrier performs load/unload beyond standard (A4/A5) | Flat or hourly `[NEEDS INPUT]` |
| Stop-off | Additional pickup/drop point (A1) | Per-stop fee `[NEEDS INPUT]` |
| Redelivery / reconsignment | `DELIVERY_REFUSED` or destination change (A5) | Additional linehaul segment + admin fee |
| Fuel surcharge (FSC) | Applies to every load | Indexed method `[NEEDS INPUT: index + update cadence — verify]` on rate confirmation, not renegotiable post-award |
| OS&D deduction | Shortage/damage at delivery (A5), adjudicated (A8) | Held against `INVOICE_ISSUED`, released or finalised only on A8 claim outcome |

**BR-602** (Must · → OBJ-005) Every accessorial line shall carry documentary evidence (timestamp log,
signed BOL exception, lumper receipt) before moving from `INVOICE_ISSUED` to `INVOICE_FINALISED`.
*Source: derived. Acceptance: no accessorial line finalises without an attached evidence artifact.*

## 3. Invoice lifecycle: issued → finalised, and money-in-question handling

`INVOICE_ISSUED` (at `POD_CAPTURED`): base rate + undisputed accessorials are provisional; any line
touching an open `CLAIM_OPEN`, `DISPUTED`, or unverified accessorial is flagged `HELD`, never omitted.
`INVOICE_FINALISED`: reached once every held line resolves — a claim closes (A8), an accessorial is
evidenced (§2), or a dispute window lapses. Only a finalised invoice feeds `SETTLED`.

**BR-603** (Must · → OBJ-005) The system shall allow partial settlement: undisputed lines pay on the
standard cycle while disputed lines stay `HELD`, rather than blocking the whole invoice on one open
item. *Source: A6 challenge accepted into spine §3. Acceptance: a load with one OS&D line and nine
clean lines settles the nine without waiting on the one.*

**BR-604** (Must · → OBJ-005, OBJ-006) A short-pay or deduction against a finalised invoice shall
generate a credit note referencing the specific invoice line and linked A8 claim/dispute ID; the
platform shall never silently net a deduction without a traceable document. *Source: derived —
unexplained deductions are a leading carrier-trust complaint in this market. Acceptance: every
deduction has a credit note with a claim-ID reference.*

**BR-605** (Should · → OBJ-005) In Model B, carrier payable and shipper receivable shall be tracked
as two independently timed obligations against the same finalised invoice, so a shipper short-pay
does not automatically reduce what the carrier is owed on undisputed lines. *Source: derived from
broker buy/sell structure. Acceptance: carrier payment status is queryable independent of shipper
collection status.*

## 4. Freight factoring and Notice of Assignment (NOA)

A carrier that has factored its receivable is legally paid via the factor, not directly — an **NOA**
legally directs remittance. Paying the carrier instead of the active NOA's factor risks paying twice;
the factor can still collect from the account debtor (platform in Model B, shipper in A/C).

**BR-606** (Must · → OBJ-005, OBJ-006) The system shall capture, at carrier onboarding and per-load,
whether the receivable is factored, and if so the factor's name and remit-to instructions, sourced
from a signed NOA document, never from carrier self-declaration alone. *Source: spine §0
money-movement row. Acceptance: no carrier payment issues without an NOA-status check on the paying
record.*

**BR-607** (Must · → OBJ-006) Only one active NOA per carrier is honored at a time; a new NOA is
accepted only against a signed Release from the prior factor or documented NOA expiry. *Source:
derived — double-factoring is a known US freight fraud pattern.*
`[ASSUMPTION: NOA/Release documents arrive as uploaded artifacts, not a live factor-company API feed |
conf: med]`

**BR-608** (Must · → OBJ-005) Where a valid NOA is on file, all payable amounts on that carrier's
invoices route to the factor's remit-to instructions, not the carrier's own bank details, with no
manual override absent a compliance sign-off. *Source: derived. Acceptance: a payment run for a
factored carrier routes 100% to the factor of record.*

## 5. Quick pay

A standard US brokerage lever: pay the carrier in days rather than the standard cycle, for a discount
off the payable amount.

**BR-609** (Should · → OBJ-003, OBJ-005) The system shall offer quick pay as an elective, per-invoice
or per-carrier-tier option, with discount rate and payout window `[NEEDS INPUT]`, funded from
platform working capital or a third-party invoice-financing partner. *Source: spine money-movement
row + industry convention `[verify — cite a factoring/quick-pay industry source before build]`.*

**BR-610** (Should · → OBJ-006) Quick pay is disabled by default on any invoice carrying a held/
disputed line (§3), since the discount is priced against a clean, finalised payable. *Source: derived.
Acceptance: quick-pay election is blocked while any line is `HELD`.*

## 6. Payment terms and the working-capital gap

Carriers want fast payment against thin margins; shippers pay on standard commercial terms. Whoever
bridges the gap carries the risk.

| Option | Who bridges | Consequence |
|---|---|---|
| Platform bridges (Model B default) | Platform pays carrier near-delivery, collects from shipper on `[NEEDS INPUT: term, e.g. net-30]` | Platform absorbs shipper non-payment/insolvency risk; needs capital or a receivables-financing facility |
| Carrier bridges independently | Carrier factors on its own (§4) or waits on shipper terms | Platform stays capital-light; less monetizable, less control if the carrier's own factor is unreliable |
| Hybrid — optional platform-backed quick pay | A financing partner funds early payouts; platform takes a spread on the discount | Platform exposure limited to the spread, not the full receivable; requires diligence on the financing partner (route to A7) |

**BR-611** (Must · → OBJ-005) Standard payment terms to shippers and standard payout timing to
carriers shall each be an explicit, documented figure, never left implicit; both are
`[NEEDS INPUT]`. *Acceptance: rate confirmation and shipper contract both state a term in days.*

## 7. Tax and reporting

**BR-612** (Must · → OBJ-007) The system shall collect a completed Form W-9 from every US carrier
before its first payment. *Source: IRS Form W-9 instructions — standard practice, not a fabricated
figure. Acceptance: no first payment issues without a W-9 on file.*

**BR-613** (Must · → OBJ-007) The system shall track cumulative annual payments per carrier and
generate Form 1099-NEC data for carriers meeting the IRS reporting threshold, noting that entity type
(e.g., corporation) can change reportability — confirmed with the client's accountant, not asserted
here. *Source: IRS Form 1099-NEC instructions `[verify current threshold before build]`.*

State sales/use tax generally does not apply to interstate freight-transportation services, but
treatment is state-specific and not a rule this document asserts uniformly.
`[NEEDS INPUT: states of shipper/carrier/consignee operation, to route to counsel for a
state-by-state read]`.

## 8. Platform revenue mechanics and the money-transmission flag

**BR-614** (Must · → OBJ-005) The mechanism by which the platform is paid (subscription fee,
per-transaction listing fee, or a buy/sell spread) is set by the §1 model choice and shall be stated
explicitly on every invoice or billing statement the platform issues; rate-setting strategy is A10's,
this section owns only the mechanical form. *Acceptance: an invoice states, unambiguously, what the
platform charged and to whom.*

If the platform holds or routes shipper or carrier funds at any point (Model B, and transiently
Model C), state money-transmission / MSB licensing questions arise. **Routed to A7 — not analysed
here.**

## Edge Cases

| ID | Trigger | What happens | Who decides | Unresolved |
|---|---|---|---|---|
| EC-600 | Carrier disputes an accessorial on a finalised invoice | Line reopens to `HELD`; credit/debit note issued on resolution | Platform ops, per BR-604 | Reopening window after finalisation `[NEEDS INPUT]` |
| EC-601 | Shipper insolvency mid-transit (Model B) | Platform has already paid or promised the carrier quick pay; shipper receivable becomes uncollectable | Platform (credit-risk owner in Model B) | Bad-debt policy not defined |
| EC-602 | Forged or expired NOA presented | Payment could route to a fraudulent factor | Platform, verification step | Verification method for NOA authenticity `[NEEDS INPUT]` — flag to A8 as fraud typology |
| EC-603 | Carrier switches factors mid-load | Old NOA still on file when payment issues | Platform; requires a signed Release before honoring the new NOA | Timing gap between old-Release and new-NOA capture |
| EC-604 | Accessorial claimed with no evidence (e.g. missing detention log) | Line cannot finalise; held indefinitely or defaults to zero | `[NEEDS INPUT: default-to-zero vs indefinite-hold policy]` | — |
| EC-605 | Quick pay elected, then a dispute opens on the same invoice after payout | Platform has already paid the carrier at a discount; resolution may owe money back | Platform | Clawback mechanism undefined |
| EC-606 | Fuel-surcharge index unavailable or lagged for the shipment week | FSC line cannot compute at invoice time | `[NEEDS INPUT: fallback index or prior-week carry-forward rule]` | — |
| EC-607 | Carrier is a broker/agent (spine's carrier-broker role), not asset-holder | Payee-of-record ambiguity — the booking carrier or the underlying asset-holder | Routed to A2 (role) + A6 (payee determination) | Payee-of-record rule undefined |
| EC-608 | OS&D deduction exceeds the remaining payable on an invoice | Negative balance owed back to the platform/shipper | `[NEEDS INPUT: recovery mechanism, e.g. offset against future loads]` | — |
| EC-609 | Carrier has no factor NOA on file but is discovered mid-dispute to have factored anyway | Platform may have already paid the carrier directly, exposing it to a double-pay claim from the undisclosed factor | Platform, legal review | Undisclosed-factoring detection method undefined |

## Assumptions and Decisions

| ID | Statement | Confidence |
|---|---|---|
| ASM-600 | "Invoice generation" in the happy path means a platform-generated invoice artifact at minimum, independent of the §1 model choice | Low — resolved by §1 answer |
| ASM-601 | NOA/Release documents are captured as uploaded artifacts, not a live factor-API feed | Medium |
| DEC-600 | `INVOICE_ISSUED` / `INVOICE_FINALISED` split (accepted into spine) enables partial settlement without blocking clean lines on one dispute | High — already accepted |

---
*A6 — Charges, Invoicing & Settlement. IDs 600-699. Does not analyse regulatory regime (A7), unit
economics/take-rate (A10), or claim adjudication (A8).*
