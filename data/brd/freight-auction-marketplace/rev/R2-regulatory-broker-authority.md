# R2 — Regulatory surface, revised: the platform IS the broker

**Revision of `part-A7-regulatory.md` under `DEC-LOCK-003` (2026-07-30). ID block 700-799 retained.**
Markers `[REVISED]` `[NEW]` `[CLOSED]`. Citations retrieved **2026-07-30**; unverified marked `[verify]`.

⚠️ **General regulatory awareness only. NOT legal advice; certifies nothing.** States what compliance *would
require* and what evidence a regulator, auditor or plaintiff's counsel looks for.

**Scenario.** The entity operating a US interstate truckload auction marketplace will itself arrange
transportation of property for compensation — a property broker holding FMCSA authority, a bond, and the
Part 371 record duty.

**Assumptions.** `ASM-701` interstate for-hire domestic truckload *(med)* · `ASM-702` no household goods *(med)* ·
`ASM-703` no hazmat phase 1 *(low)* · `ASM-704` no employed drivers *(high)* · `ASM-706` `[NEW]` one US operating
entity, one domicile state *(med — multi-entity changes AUTH-1)*.

---

## R2.0 Correction first — the $150,000 bond in `DEC-LOCK-003` is not verified `[NEW]`

| Check | Record |
|---|---|
| Current regulation | 49 CFR 387.307: *"A broker must have a surety bond or trust fund of **$75,000** in effect."* No phase-in, no second figure. |
| The rule being described | 88 FR 78656 (16 Nov 2023, eff. 16 Jan 2024) amended **five areas** — readily-available assets, immediate suspension, surety/trustee duties on financial failure, enforcement authority, BMC-85 eligible entities. **Not the amount.** |
| Where "Jan 2026" comes from | 89 FR 107021 (31 Dec 2024) moved the **compliance date** for certain provisions to **16 Jan 2026** pending the new registration system. A date, not an amount. |
| Every later change | 91 FR 45653 (21 Jul 2026) is technical corrections that "do not impose any new material requirements." Federal Register API sweep of all FMCSA "broker" documents, 1 Jun 2025 → 30 Jul 2026: **13 documents, none raises the bond.** |
| 2026 corroboration | Post-*Montgomery* trade coverage still describes brokers holding "**$75,000** in surety bond coverage that does not respond to tort claims." |

$150,000 traces to surety-vendor and dispatch-blog commentary, not a published rule. It appears in the 2023
NPRM record (88 FR 830) as a considered option, and FMCSA published a Mar-2026 report *Appropriateness of the
Current Financial Responsibility and Security Requirements…* `[verify — 403, unread]`. The direction of travel is
real; **the obligation is not.** **Plan against $75,000**; treat $150,000 as a watch item and funded contingency,
not a launch cost. Amend `DEC-LOCK-003`; confirm with surety **and** counsel before any figure is budgeted.

---

## R2.1 The authorisation path, sequenced `[NEW]`

| # | Step | Cite |
|---|---|---|
| AUTH-1 | US entity formed, legal name fixed. Authority issues to an **entity**; 371.7(a) bars brokering in any name but the registered one, so trading name must reconcile | 371.7(a) |
| AUTH-2 | USDOT number; **broker** authority applied for (Form OP-1). **`[REVISED]`:** FMCSA is migrating to **Motus** — Phase I (8 Dec 2025) covered supporting companies incl. BOC-3 blanket and financial-responsibility filers; Phase II (Q2 2026) opens to brokers and sunsets URS for new applications. MC numbers reported still active `[verify]` | 91 FR 23144 |
| AUTH-3 | **BOC-3** process agents for every state with an office or where contracts are written; blanket filing normal, filed **by the agent** | 49 CFR Pt 366 |
| AUTH-4 | **BMC-84 bond** or BMC-85 trust, **$75,000**, filed by surety/trustee. Registration valid **only while** in effect | 387.307 |
| AUTH-5 | Post-2026 conditions on that security: readily-available assets, surety notice on drop below floor or financial failure, immediate suspension — compliance **16 Jan 2026** | 88 FR 78656; 89 FR 107021 |
| AUTH-6 | Authority granted and **active**. **Hard gate** — only now may a load be arranged for compensation | 49 U.S.C. 13904 `[verify]` |
| AUTH-7 | **UCR** — owed by brokers as well as carriers | 49 CFR Pt 367 `[verify]` |
| AUTH-8 | Insurance placed (R2.7); W-9 collected and 1099-NEC reporting live before first payment | commercial / IRS |

`CON-704` `[NEW]` No load reaches `PUBLISHED` before AUTH-6 is evidenced in-system; no `AWARD` while bond or
BOC-3 evidence is expired. Extends `CON-701`; makes `BR-702` a hard block.

---

## R2.2 Part 371 is now central, not conditional `[REVISED]`

Under the old answer C this was a tenant's duty. It is now the operating entity's own, every load.

**49 CFR 371.3 — six elements, retained three years:** consignor · originating carrier's name, address and
**registration number** · BOL/freight-bill number · *"the amount of compensation received by the broker … and
the name of the payer"* · non-brokerage services and their payer · *"the amount of any freight charges collected
by the broker and the date of payment to the carrier."* Then: *"Each party to a brokered transaction has the
right to review the record of the transaction."*

**Why a price-setting marketplace sits directly on this rule.** `DEC-LOCK-003` locked the revenue model as a
**spread**. Elements (4) and (6) are exactly the numbers that make the spread visible — and the review right
belongs to the carrier the platform is bargaining against. Setting both sides' prices therefore carries a
per-transaction disclosure duty pointed at the platform's own margin. Language purporting to waive it is a live
enforceability question, not a defence (`EC-708`; handoff 4).

**Transparency rulemaking — status checked `[REVISED]`.** NPRM 89 FR 91648 (20 Nov 2024); comments reopened
90 FR 9702 (18 Feb 2025); ~7,000 comments. FMCSA chose a **fresh proposal** over finalising, agenda-slated around
**May 2026**. Federal Register shows **no FMCSA transparency document after 18 Feb 2025** — not final, no
effective date, replacement slipped `[verify — re-check quarterly]`. Proposed duty: electronic records furnished
within **48 hours**, non-waivable. Build-ahead stays a decision; `NFR-705` already assumes it, cheaply.

---

## R2.3 Forks that close `[CLOSED]`

| Was open | Now |
|---|---|
| §7.1 broker/carrier/vendor/neither | **Answer A — licensed property broker.** BR-701…708 unconditional Must. |
| §7.1 answer **D** | Not a posture — the **failure mode to avoid**; prevented by `CON-704`. |
| T-01 "is this brokerage?" | Settled by 371.2; residual question narrows to the bona-fide-agent boundary. |
| T-02 amount · T-04 bearer | Operating entity; **$75,000** per R2.0; every load. |
| T-15 negligent selection | The platform's own exposure → R2.5. |
| NFR-701 · §7.5 conditional Musts | Unconditional. |
| A6 · A8 · A9 · A10 | Principal both sides · broker not carrier not vendor · operating entity is sponsor · spread. |
| T-18 / §7.4 M1-M2-M3 | **Narrowed, not closed** → R2.6. |

Not closed: safety floor (`DEC-201`) · "Open" §7.7 retention periods · intrastate lanes (`EC-723`) · hazmat
(`ASM-703`).

---

## R2.4 What does **not** change `[REVISED]`

**Under the Carmack Amendment, 49 U.S.C. §14706, the motor carrier — not the broker — bears cargo liability**
for loss of or damage to goods received for interstate transport. Becoming a broker does not import cargo
liability; the ≥9-month claim and ≥2-year suit minima stay the carrier's clock (`BR-712`, `BR-713` unchanged).

**The qualification that matters.** A broker holding itself out as arranging carriage can be found to have acted
as a **carrier** on a shipment, at which point Carmack attaches to it. 371.7(b) is the regulatory edge of the
same problem: a broker *"shall not, directly or indirectly, represent its operations to be that of a carrier,"*
and *"any advertising shall show the broker status of the operation."* Two consequences bite this product:
UI copy guaranteeing coverage, capacity or delivery builds the holding-out record itself; and 371.3(2) requires
the **originating carrier's registration number** on every record — the field distinguishing broker from carrier
is also a mandatory record element.

**Allocation is not mine.** Carmack-vs-contract, released value, indemnity, broker-carrier agreement terms →
**A8 / R3**. R2 supplies trigger and record duty only.

`BR-721` `[NEW]` All shipper/carrier-facing surfaces, contracts and advertising reviewed against 371.7(b)
pre-release; broker status disclosed publicly and in both agreements. *Acceptance:* copy-review gate in the
release process; no live string promises to transport, carry, deliver or guarantee delivery.

---

## R2.5 Negligent selection is the platform's own exposure — Part 371 is where the defence lives `[NEW]`

*Montgomery v. Caribe Transport II, LLC*, No. 24-1238 (S. Ct., 14 May 2026, unanimous, Barrett J.): a state-law
negligent-hiring claim against a broker is **not** FAAAA-preempted. The platform is now the broker that chose the
carrier — and **no federal liability-insurance requirement applies to brokers**, only the $75,000 bond, which
does not answer tort claims.

**The linkage.** Part 371's record duty and the eligibility gate (`DEC-LOCK-001`) are one artefact seen from two
directions. 371.3 compels a per-transaction, three-year, party-reviewable record of **who the originating carrier
was**; `DEC-LOCK-001` compels a record of **why it was eligible**. Held as one immutable object, the regulatory
duty produces the litigation defence as a by-product. Held apart, the platform keeps a mandatory record naming
the carrier with no contemporaneous record of why it was chosen — the worst pairing available.

| In the record, per award | Why | Source |
|---|---|---|
| Originating carrier name, address, **registration number** | Mandatory element; evidences a carrier, not a re-broker | 371.3(2) |
| Authority status **as read at award**, source + timestamp, frozen | A later status change must not rewrite the basis relied on | `BR-705` |
| Part 387 insurance at award — limits, insurer, dates, cancellation | 387.9 minima ($750k non-haz, GVWR ≥10,001 lb); cargo cover is commercial only since FMCSA eliminated it for most general-freight carriers (75 FR 35315, eff. 21 Mar 2011; household goods excepted) | 387.9 |
| Safety-data snapshot actually consulted, with retrieval time | "Available safety data ignored" is the plaintiff's theme | *Montgomery* |
| Eligibility criteria **version** applied | Shows a standard existed and was applied, not improvised | `DEC-LOCK-001` |
| **Every carrier excluded, and the criterion that excluded it** | Proves the gate operated; absence implies it did not | `BR-802` (A8) |
| Any override — identity, reason, authority | Most scrutinised row in the file | `EC-725` |

`BR-722` `[NEW]` The 371.3 record and the award selection record are **one immutable, tamper-evident object**
per load, retained ≥3 yrs, replayable, retrievable while the transactional path is degraded. *Acceptance:*
sampled replay reproduces the award from stored data alone and yields all six 371.3 elements.
`BR-723` `[NEW]` Two disclosure surfaces, never one view: the 371.3 party path (`BR-704`) shows only that party's
record; the selection record only under legal process or documented decision. *Acceptance:* no carrier-facing
view exposes another carrier's exclusion reason or bid.
`BR-724` `[NEW]` Legal hold suspends purge **per record** (`EC-714`, `EC-715`).

---

## R2.6 Money transmission, re-tested — **partially holds. Do not bank it.** `[REVISED]`

`DEC-LOCK-003` argues the question recedes because a broker of record moves **its own** receivables and payables.
Sound in narrow form, **over-stated as written**: it holds only where the flow of funds matches the principal
characterisation, and four roadmap features break it.

| Holds where… | Breaks where… |
|---|---|
| Contracts **in its own name** both sides, principal | Any agreement casts it as agent collecting "on behalf of" a side |
| Shipper payment discharges a debt owed **to the platform**; carrier payment discharges a **separate** platform debt | Funds characterised as the carrier's money held by the platform — escrow, trust, "held for" |
| No stored value — no wallet or resting balance | A wallet, balance or top-up exists: the classic receive-money-for-transmission pattern |
| Nothing held pending a condition | Shipper funds **held until POD** — escrow-like even as principal |
| Only its own two-sided obligations move | **Accessorials, detention, lumpers passed through** for another's account |
| Broker of record on **every** load whose money it touches | A **third-party broker tenant** or shipper-direct arrangement uses the rails — third parties' money, analysis restarts |
| Payment goes to the contracted party | Redirected to a **factor under an NOA** — assignment is ordinary, the flow still needs review |
| No advance of funds | **Quick-pay / carrier advance** — receivable purchase or lending; state lender/factoring licensing may attach independently `[verify]` |

**Verdict.** The reading **narrows** the surface; it does not remove it. Federal MSB status turns on 31 CFR
1010.100(ff)(5) and its narrow payment-processor exclusion at (ff)(5)(ii)(B); state money-transmitter licensing
is a separate state-by-state determination, and the agent-of-payee exemption several states offer is conditional
and state-specific. **I will not certify that this is not money transmission — that is a legal conclusion.**
`RSK-703` reduced **P3/I5 → P2/I5**; `EC-721` stays open. **ESCALATE to payments counsel** for a written
flow-of-funds memo answering wallet, escrow-to-POD, quick-pay and third-party tenancy **separately**.
`CON-705` `[NEW]` none of those four ships before that memo exists. M2 (licensed processor of record, platform
never holds) is both cheapest and compatible with the principal characterisation — it makes the `DEC-LOCK-003`
reading far easier to sustain than characterisation alone.

---

## R2.7 Newly in scope, because the platform is a regulated intermediary `[NEW]`

| Area | What the authority carries | Requirement |
|---|---|---|
| **Contingent auto liability** | Answers a post-*Montgomery* negligent-hiring claim. **No federal broker requirement exists.** Reported median trucking verdict $36m (2022) `[verify]` against a bond that does not answer tort claims — the largest gap the decision creates | `BR-725` placed, limits documented, renewal-alarmed before first load |
| **Contingent cargo** | Carmack sits on the carrier, but most general-freight carriers need no cargo cover (75 FR 35315). The gap is the platform's when cover is absent or under declared value | `BR-726` declared value (`BR-711`) vs carrier cargo limit **at eligibility**; shortfall flagged pre-award (`EC-704`) |
| **Broker E&O** | Errors in arranging, misdelivery, wrong-carrier release | `BR-727` placed, or a documented decision not to |
| **Bond ≠ insurance** | BMC-84 answers **non-payment**, not tort; claims can suspend authority | `BR-728` bond-claim intake; escalates to a named officer, pauses new awards `[verify trigger with surety]` |
| **Claims & disputes** | The broker receives cargo claims and routes them without becoming the insurer | `BR-729` intake, acknowledgement, routing, §14706 clocks (→A8/R3) |
| **Security + registration surveillance** | Readily-available assets, surety notice, immediate suspension; Motus migration, biennial updates, UCR (2027 fees proposed up ~20%, 91 FR 17618) | `BR-730` monthly security self-check, lapse blocks awards (`BR-702`, `EC-701`) · `BR-731` filing calendar with a named owner (`EC-727`) |
| **Double-brokering, other side** | Now both potential victim *and* the broker that failed to detect it | `BR-710` `[REVISED]` → Must; pickup-identity reconciliation a hard stop (`EC-707`) |

`BR-733` `[NEW]` no first carrier payment without a W-9 on file. `NFR-713` `[NEW]` authority/bond/BOC-3
re-verified on a fixed cycle with pre-expiry alerting · `NFR-714` `[NEW]` selection-record retrieval ≤ shortest
applicable furnish window, drilled quarterly · `NFR-715` `[NEW]` the platform's **own** insurance evidence
segregated and view-logged per `NFR-707`.

`RSK-707` contingent-auto gap at a serious accident (P2/I5) · `RSK-708` 371.3 review exposes the spread, carrier
disintermediates (P4/I3, commercial) · `RSK-709` bond claim suspends authority mid-book (P2/I5) · `RSK-710`
holding-out recharacterises the platform as carrier (P2/I5) · `RSK-711` budget built on an unverified $150,000
(P3/I2) · `RSK-702` `[REVISED]` P3→P1 while `CON-704` holds. `EC-728` carrier invokes 371.3 for the platform's
compensation on a load it is still bidding · `EC-729` Motus Phase II changes the route mid-application ·
`EC-730` bond claim filed while auctions are live · `EC-731` awarded carrier has no cargo cover, declared value
high · `EC-732` marketing promised delivery, then a claim arrives. *All `[NEW]` unless marked.*

---

## R2.8 Counsel handoff — updated `[REVISED]`

US transportation counsel in the entity's state, plus specialists noted:

1. Authority application; entity vs trading name under 371.7(a); the Motus route as it stands. `[CLOSED as fork, open as execution]`
2. **Verify the bond amount and any pending increase** with counsel *and* surety — do not rely on R2.0 alone. `[NEW]`
3. **Post-*Montgomery* negligent-selection opinion** — what standard is defensible, and whether R2.5's record set is the right evidentiary shape. Highest value.
4. **371.3 review right vs the spread** — waiver enforceability, scope of the path, what a carrier who asks must be shown. `[NEW — a business-model question now]`
5. **Holding-out review** of copy, contracts, advertising under 371.7(b). `[NEW]`
6. **Money movement** — payments counsel; the R2.6 memo; federal MSB **and** state licensing. `[REVISED — narrowed, not closed]`
7. **Insurance programme** — contingent auto limits, contingent cargo triggers, E&O, bond/claims interaction. `[REVISED — now the platform's own]`
8. **Factoring and Notices of Assignment** — paying the factor vs the carrier; double-payment risk. `[NEW]`
9. Carried forward: Carmack windows and released value on-platform (A8/R3) · re-brokering consent and remedies · antitrust review of bid disclosure · state privacy and the unregistered consignee · "Open" §7.7 periods and legal hold · intrastate lanes · UCR/permit scope.
10. **Build-ahead on the transparency proposal** — 48-hour furnishing, still not final. `[REVISED]`

**Sources** (retrieved 2026-07-30).
[371.2](https://www.law.cornell.edu/cfr/text/49/371.2) ·
[371.3](https://www.law.cornell.edu/cfr/text/49/371.3) ·
[371.7](https://www.law.cornell.edu/cfr/text/49/371.7) ·
[387.307 — $75,000](https://www.law.cornell.edu/cfr/text/49/387.307) ·
[387.9](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-III/subchapter-B/part-387/subpart-A/section-387.9) ·
[88 FR 78656](https://www.federalregister.gov/documents/2023/11/16/2023-25312/broker-and-freight-forwarder-financial-responsibility) ·
[89 FR 107021](https://www.federalregister.gov/documents/2024/12/31/2024-30509/broker-and-freight-forwarder-financial-responsibility-extension-of-compliance-date) ·
[88 FR 830 NPRM](https://www.federalregister.gov/documents/2023/01/05/2022-28259/broker-and-freight-forwarder-financial-responsibility) ·
[91 FR 45653](https://www.federalregister.gov/documents/2026/07/21/2026-14701/general-technical-organizational-conforming-and-correcting-amendments-to-the-federal-motor-carrier) ·
[91 FR 23144 Motus](https://www.federalregister.gov/documents/2026/04/29/2026-08334/availability-of-motus-fmcsas-new-registration-system) ·
[89 FR 91648 transparency NPRM](https://www.federalregister.gov/documents/2024/11/20/2024-27115/transparency-in-property-broker-transactions) ·
[90 FR 9702 reopening](https://www.federalregister.gov/documents/2025/02/18/2025-02707/transparency-in-property-broker-transactions) ·
[75 FR 35315 cargo-insurance elimination](https://www.federalregister.gov/documents/2010/06/22/2010-14866/cargo-insurance-for-property-loss-or-damage) ·
[CCJ on that rule](https://www.ccjdigital.com/business/article/14917233/fmcsa-eliminates-cargo-insurance-requirement) ·
[91 FR 17618 UCR fees](https://www.federalregister.gov/documents/2026/04/07/2026-06726/fees-for-the-unified-carrier-registration-plan-and-agreement) ·
[Pt 366 BOC-3](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-III/subchapter-B/part-366) ·
[§14706](https://www.law.cornell.edu/uscode/text/49/14706) ·
[*Montgomery*](https://www.supremecourt.gov/opinions/25pdf/24-1238_1b7d.pdf) ·
[FreightWaves — broker insurance gap](https://www.freightwaves.com/news/the-freight-broker-insurance-gap-is-now-real) ·
[FMCSA Mar-2026 report `[verify — unread\]`](https://www.fmcsa.dot.gov/sites/fmcsa.dot.gov/files/2026-03/Appropriateness%20of%20the%20Current%20Financial%20Responsibility%20and%20Security%20Requirements%20for%20Motor%20Carriers,%20Brokers,%20and%20Freight%20Forwarders.pdf) ·
[31 CFR 1010.100](https://www.law.cornell.edu/cfr/text/31/1010.100)

*General awareness only. Not legal advice. Qualified counsel required for binding decisions in your jurisdiction.*
