# Part A8 — Liability, Trust, Fraud and Disputes

**Owns:** custody-chain liability · cargo loss/damage/theft/shortage · Carmack claims · insurance ·
ratings · fraud · disputes · penalties. **Not here:** regulatory citation depth (A7), auction mechanics
(A3), invoicing mechanics (A6). **Not legal advice** — citations exist so counsel can verify them.
`[inference]` = analysis, not a legal conclusion. `[verify]` = not read in primary source here.

---

## 8.1 The platform's own legal position governs everything below — `DEC-801` `[NEEDS INPUT]`

Under Carmack (49 U.S.C. §14706) the **motor carrier** bears cargo liability. A **property broker**
arranges carriage and generally does not — but is still exposed in tort for negligent selection, and a
party holding itself out as responsible for the carriage can be found to have acted as a carrier whatever
its contract says `[verify]` `[inference]`. Boss chooses; this document does not.

| Position | Cargo-loss exposure | Selection-tort exposure | Consequence |
|---|---|---|---|
| **P1 — licensed broker** | Generally not Carmack-liable `[verify]` | **High, now nationwide** (§8.3) | Broker authority, BMC-84/85, BOC-3, Part 371 records (A7); needs contingent cargo + contingent auto |
| **P2 — carrier / dual authority** | **Directly liable, full load value** | High, plus vicarious for subcontractors | Heaviest insurance burden; strongest trust story |
| **P3 — software vendor to brokers** | None | Low — **strained if the platform's algorithm awards** `[inference]` | Cheapest legally; but the auction *is* the selection act |

`[NEEDS INPUT: broker authority, carrier authority, both or neither — and is the client a party to the
transportation contract? §8.4-§8.6 all turn on this.]`

## 8.2 Liability along the custody chain

Risk sits with the shipper pre-pickup, transfers to the carrier at receipt (Carmack), transfers to the
consignee on delivery. The handovers decide everything: count, condition, seal, driver identity on the
origin BOL (A4); **clear vs exception** on the delivery signature (A5). **Plainly: a clear POD undermines
a later damage claim** — it is prima facie evidence the goods arrived as described, pushing the burden
onto the claimant to prove loss happened in the carrier's custody (*Missouri Pacific R.R. v. Elmore &
Stahl*, 377 U.S. 134 (1964)) `[verify]`. A5's tailgate notation is worth more to a claim than everything
recorded over the preceding 900 miles.

## 8.3 Negligent selection — the defining exposure for this product

**This changed in May 2026.** *Montgomery v. Caribe Transport II, LLC*, No. 24-1238, 608 U.S. ___ (2026)
(Barrett, J., unanimous; Kavanaugh, J., concurring, joined by Alito, J.; decided 14 May 2026) held the
FAAAA safety exception, 49 U.S.C. §14501(c)(2)(A), encompasses state-law negligent-hiring claims against
brokers concerning the use of motor vehicles — reversing the Seventh Circuit and resolving the 7th/11th vs
9th/6th split `[verify — read the slip opinion]`. **Broker selection exposure is no longer
circuit-dependent.** Awarding strictly to the lowest bid with FMCSA safety data available and unused is
the fact pattern plaintiffs' counsel look for after a serious crash `[inference]`. The defence is a
contemporaneous record of *why this carrier was fit*. **This is a requirement on A3's mechanism, stated
explicitly:** award must emit a selection record, not just a price — A3 cannot treat award as a
sort-by-price with no memory.

## 8.4 Carmack claims path, end to end

| Stage | Content |
|---|---|
| Who may claim | Party bearing risk of loss — shipper or consignee — or its subrogated insurer `[verify]` |
| Filing floor | Not under **9 months** from delivery (or reasonable delivery time, if non-delivery) — §14706(e)(1) |
| Suit floor | Not under **2 years** from **written** disallowance — §14706(e)(1). Lengthenable, never shortenable |
| Valid claim | Written/electronic; identifies shipment; asserts liability; demands a specified or determinable amount — 49 CFR §370.3 |
| Acknowledge | In writing **within 30 days** — §370.5 |
| Disposition | Pay, decline or firm compromise offer **within 120 days**; then written status **every 60 days** — §370.9 |
| Evidence | Origin BOL (A4) + clear/exception delivery signature (A5) + custody and tracking record |
| Investigates / pays | Carrier and its cargo insurer, subject to §8.5; platform's role turns on `DEC-801` |
| Carrier paid while open? | **`[NEEDS INPUT]` — counsel.** Offsetting freight charges against an open cargo claim is contested → A6 |

## 8.5 Released value and limitation of liability

Post-*Hughes Aircraft Co. v. North American Van Lines*, 970 F.2d 609 (9th Cir. 1992), as modified by ICCTA
(tariff prong lapsed), a carrier limiting liability must obtain the shipper's agreement as to choice of
liability, give a **reasonable opportunity to choose between two or more levels**, and issue the BOL
before the move `[verify]`. A limitation buried in T&Cs, or silently embedded in a bid price, is unlikely
to hold `[inference]`: the choice must be presented at load creation, recorded, separately priced, printed
on the BOL.

## 8.6 Insurance structure

**The verified gap most people miss:** FMCSA eliminated the requirement for most for-hire carriers of
general freight to maintain and file cargo insurance, effective 21 March 2011; **household-goods carriers
and forwarders remain subject** (75 FR 35367, 22 June 2010) `[verify]`. A carrier can hold valid authority
and Part 387 auto-liability cover and carry **zero cargo insurance** — so cargo cover here is a commercial
eligibility requirement the platform imposes, or it is absent.

| Layer | Failure mode this build must handle |
|---|---|
| Carrier auto liability (Part 387) | Lapse or cancellation between COI issue and pickup |
| Carrier cargo | **Not federally required for general freight**; limit below load value; unattended-vehicle, theft, reefer-breakdown, scheduled-equipment, targeted-commodity exclusions `[ASSUMPTION: exclusions vary by policy \| conf: med]` |
| Broker contingent cargo | **Commonly excludes double-brokered and impersonation losses** — the two frauds most likely here `[ASSUMPTION \| conf: med — counsel + insurance broker to confirm wording]` |
| Broker contingent auto | The layer under pressure post-*Montgomery* |
| BMC-84 / BMC-85 | A7 owns the instrument; A8 owns the claim-against-bond scenario |

Certificates must come **from the insurer or its agent, never the carrier**, naming the contracting entity
as certificate holder with cancellation notice — a forged COI is a primary identity-theft tool.

## 8.7 Fraud typologies — this market is under acute pressure now

Verisk CargoNet: estimated 2025 US/Canada cargo-theft losses ≈ **$725M, up ~60% on 2024**; average value
per theft **$273,990** (up 36%); confirmed incidents up 18% (2,243 → 2,646); strategic deception-based
theft now roughly a third of cargo crime `[verify — CargoNet 2025 trends]`.

| ID | Typology | Signal |
|---|---|---|
| FR-1 | **Double brokering** — winner re-brokers to an unvetted carrier | Driver/tractor/MC mismatch at pickup; tracking not on awarded account |
| FR-2 | **Carrier identity theft** — imposter on a real MC's authority + COI | New email domain; changed phone/remit-to; COI unconfirmed; dormant authority reactivated |
| FR-3 | **Fictitious pickup** — collected, never delivered | Aggressive underbid; pressure to skip verification; no ELD |
| FR-4 | Driver absconds with load | Tracking loss + route deviation + unreachable |
| FR-5 | Strategic theft at truck stop / unattended trailer | Then denied under unattended-vehicle exclusion |
| FR-6 | Forged or altered POD | Signature unmatched to consignee; geo/time inconsistent |
| FR-7 | Shipper-contact collusion with a bidder | Implausible win share on one contact's lanes |
| FR-8 | Bid rigging / rotation on repeat lanes | Rotation; clustered bids; no undercutting → A7 |
| FR-9 | Shill / spoiler bidding | High award-decline rate → A3 |
| FR-10 | Phantom load posting to harvest carrier documents | Credential downloads; no real pickup |
| FR-11 | Inflated accessorial / detention claims | Contradicted by tracking dwell → A6 |
| FR-12 | Payment redirect / fake NOA | Out-of-band banking or factoring change → A6 |
| FR-13 | Inflated or staged cargo claim | Claim ≫ declared value; clear POD then late claim |
| FR-14 | Rating manipulation — fake, retaliatory, purchased | Rating with no matching completed load |

**Price-only award structurally selects for FR-1, FR-2, FR-3, FR-9** `[inference]`: the lowest bidder can
be lowest precisely because it never intends to perform the movement it priced. This is the design's
attack surface, not a hypothetical.

## 8.8 Money disputes vs freight disputes are different animals

Freight disputes (loss, damage, shortage, delay, refusal, OS&D) run on Carmack + the BOL, carry statutory
clocks, turn on POD notation and photos, and are urgent *physically* — the goods are somewhere, possibly
perishing. Money disputes (rate re-trade, detention, TONU, accessorial denial, offset, NOA misdirection)
run on the rate confirmation, carry only payment-terms clocks, turn on timestamps and dwell data, and are
urgent *financially*. Separate intake, SLAs, owners — one merged queue leaves a perishable load waiting
behind an invoice argument.

## 8.9 Ratings — and the tension A3 must resolve

**Honest observation: a rating system on top of a pure lowest-price mechanism changes no award outcome.**
If price alone decides, reputation is decorative. It becomes real only if it gates eligibility (A2),
enters the award function (A3), or triggers suspension (A8). **Flagged to A3 explicitly:** either the
mechanism consumes reputation, or the BRD says plainly that ratings are informational. Ratings must be
transaction-verified, separate objective events (no-show, on-time, tracking compliance, claim rate) from
subjective stars, and release non-retaliatorily. Ratings are **not** a fitness record for §8.3 — FMCSA
data is.

## 8.10 Penalties, suspension, removal

Graduated: warning → bid restriction → suspension → removal, each with recorded ground, evidence, appeal.
**The hard part is loads in flight.** Default: suspension stops new bids and awards but does not strand
freight already in a truck — in-flight loads complete under heightened monitoring. Exception: on
cargo-integrity grounds (FR-1/2/3/4) a recovery protocol triggers — notify shipper, consignee, insurer,
law enforcement — and access is **not** simply cut, which would destroy visibility of the load. Removal
must **preserve** records: the removed party's file is the negligent-selection evidence. `[NEEDS INPUT:
penalty amounts — none invented.]`

---

## 8.11 Requirements

"The platform shall…" Traces are to OBJ IDs in spine §5.

| ID | Requirement | MoSCoW | Traces | Acceptance | Source |
|---|---|---|---|---|---|
| BR-801 | Record contracting carrier, broker, and who bears cargo liability, per `DEC-801` | Must | 006/007 | No shipment reaches AWARDED without the liable party named | spine §0 |
| BR-802 | Capture at award an immutable **selection record**: authority status, safety snapshot, insurance evidence, gate applied, bidders excluded and why, basis of award | Must | 006/007 | Every award reconstructs its decision without live data | *Montgomery* `[verify]` |
| BR-803 | Refuse award to any bidder failing the eligibility gate, regardless of price | Must | 006 | No award where gate status was FAIL | derived |
| BR-804 | Re-verify authority and insurance **at award and again at pickup**; source COIs from the insurer or agent, contracting entity as certificate holder with cancellation notice | Must | 006 | No pickup on stale verification; carrier-supplied PDFs never suffice | §8.6, FR-2 |
| BR-805 | Require cargo cover as commercial eligibility; record limit against declared value | Must | 004/006 | Loads over the carrier's limit flag pre-award | 75 FR 35367 `[verify]` |
| BR-806 | Verify at pickup that driver, tractor, MC match the awarded carrier; open a case on mismatch | Must | 004/006 | Mismatch blocks pickup, opens a case same shift | FR-1/2/3 |
| BR-807 | Provide claim intake capturing §370.3 minimum content, timestamped, and track the 30/120/60-day obligations with overdue escalation | Must | 004/007 | No submission without shipment identity, liability assertion, amount; every open claim shows its next obligation date | §370.3/.5/.9 |
| BR-808 | Never enforce under 9 months to file or 2 years to sue from written disallowance; issue and retain a dated written disallowance on decline | Must | 004/007 | Floors not configurable downward; every decline retains a notice | §14706(e)(1) |
| BR-809 | Bind every claim to origin BOL and the clear/exception delivery signature | Must | 004 | No adjudication without both, or their absence noted | → A4, A5 |
| BR-810 | Where released value is offered, present ≥2 priced liability levels at load creation, record the choice, print it on the BOL pre-pickup | Should | 004/007 | Every limited load has a pre-dispatch recorded choice | *Hughes Aircraft* `[verify]` |
| BR-811 | Separate freight from money disputes at intake — distinct evidence, owners, targets | Must | 004/005 | No queue holds both types | `[NEEDS INPUT: targets]` |
| BR-812 | Verify out-of-band changes to banking, remit-to, email domain or factoring before payment or award | Must | 005/006 | Zero payments on an unverified change | FR-2/12 → A6 |
| BR-813 | Restrict credential downloads to counterparties on an awarded load | Should | 006 | No bulk credential retrieval without an award | FR-10 |
| BR-814 | Detect award-pattern anomalies: lane rotation, single-contact win concentration, implausible underbidding | Should | 006 | Named patterns raise a reviewable alert | FR-7/8/9 → A3, A7 |
| BR-815 | Permit ratings only from a party to a completed shipment; separate objective events from stars | Must | 006 | No rating without a matching completed shipment | FR-14 |
| BR-816 | State whether reputation gates eligibility, enters award, or is informational only | Must | 001/006 | Decision documented; mechanism matches it | §8.9 → A3 |
| BR-817 | Apply graduated enforcement with recorded ground, evidence, appeal route | Must | 006 | Every action has all four fields populated | §8.10 |
| BR-818 | Suspension halts new bids/awards without stranding in-flight freight, except on cargo-integrity grounds where the recovery protocol applies | Must | 004/006 | No suspension costs a live load its visibility or custody accountability | §8.10 |
| BR-819 | Preserve vetting/selection/communication records of suspended or removed parties; litigation hold on serious injury, fatality, theft, claim | Must | 007 | Removal never deletes selection evidence; holds immutable and exportable | §8.3 |
| BR-820 | Notify shipper, consignee, insurer on loss, theft, non-delivery, refusal, with recorded time | Must | 004 | All such events produce timestamped notifications | → A5, A9 |
| BR-821 | State, per counsel, whether freight charges may be offset against an open cargo claim | Must | 005 | Rule documented and applied consistently | `[NEEDS INPUT]` → A6 |

**NFRs.** `NFR-801` selection and claim evidence retained tamper-evident `[NEEDS INPUT: retention
period]`. `NFR-802` bounded staleness of the FMCSA snapshot used at award `[NEEDS INPUT: max age]`.
`NFR-803` audit trail of every eligibility override with actor identity. `NFR-804` claim and fraud records
exportable in evidentiary form. `NFR-805` fraud-case creation available continuously `[inference]`.

## 8.12 Risks, decisions, assumptions

| ID | Risk | P | I | Mitigation |
|---|---|---|---|---|
| RSK-801 | Serious-injury crash; carrier awarded on price alone, safety data unused | 2 | 5 | BR-802/803 |
| RSK-802 | Double-brokered load lost; carrier cargo and contingent cargo both exclude it | 3 | 5 | BR-804/806 + policy-wording review |
| RSK-803 | Identity theft on a real MC's authority with a forged COI | 4 | 5 | BR-804/806/812 |
| RSK-804 | Platform found to have acted as a carrier despite intending broker/vendor status | 2 | 5 | Resolve `DEC-801` pre-build |
| RSK-805 | Claim denied — signed clear, damage reported late | 4 | 3 | BR-809 → A5 |
| RSK-806 | Ratings built then ignored by a price-only mechanism | 4 | 3 | BR-816 forces the decision |
| RSK-807 | Suspension strands freight mid-transit | 2 | 5 | BR-818 |
| RSK-808 | Released-value limitation unenforceable; full-value exposure lands | 3 | 4 | BR-810 |

**Decisions `[NEEDS INPUT]`.** `DEC-801` platform legal position · `DEC-802` whether reputation enters the
award function → A3 · `DEC-803` whether cargo cover is mandated above a declared-value threshold, at what
limit.

**Assumptions** (all `conf: med` unless noted). `ASM-801` interstate domestic truckload, so Carmack
applies; intrastate follows state law. `ASM-802` general freight, not household goods — what makes the
cargo-insurance gap live. `ASM-803` contingent cargo commonly excludes double-brokered and impersonation
losses. `ASM-804` the consignee, who never signed up, is nonetheless a likely claimant. `ASM-805` platform
holds claim and selection evidence rather than relying on carriers. `ASM-806` no hazmat, high-value or
temperature-controlled specialisation in phase 1 `[conf: low — changes §8.6]`.

## 8.13 Edge case register

| ID | Trigger | What happens | Decides | Unresolved |
|---|---|---|---|---|
| EC-801 | Exception noted at delivery | Claim opens; POD annotated | Consignee + carrier | Who arbitrates a disputed notation |
| EC-802 | Concealed damage after clear POD | Weak claim; burden on claimant | Carrier/insurer | Notice window to publish |
| EC-803 | Count at drop < BOL | Partial claim; invoice adjusts | A5 + A8 | Whether short freight is later found |
| EC-804 | Non-delivery, truck unreachable | Theft protocol | Ops | Hours before declaring theft |
| EC-805 | Theft from unattended trailer | Policy may exclude | Insurer | Whether attendance is mandated |
| EC-806 | Awarded MC never operated the load | FR-1; both insurers may deny | Platform + counsel | Who bears the uninsured loss |
| EC-807 | Bidder was an imposter on a real MC | FR-2; real carrier also a victim | Platform + police | Restoring innocent carrier's record |
| EC-808 | Fictitious pickup | Recovery protocol | Ops | Whether platform indemnifies shipper |
| EC-809 | Driver absconds mid-transit | Tracking loss escalates | Ops + carrier | Silence duration before escalation |
| EC-810 | POD signature forged | Delivery unproven; invoice held | A5 + A8 | Signature-verification standard |
| EC-811 | Consignee refuses whole load | RTO or disposal | A5 | Who pays the return move |
| EC-812 | Partial acceptance | Split claim, split invoice | A5 + A6 | Line-level claim handling |
| EC-813 | Reefer failure spoils freight | Claim; exclusion may apply | Insurer | Temperature-record standard |
| EC-814 | Insurance lapses award→pickup | Pickup blocked | Platform | Re-award or cancel |
| EC-815 | Authority revoked mid-transit | Load in unauthorised truck | Platform + counsel | Continue or intercept |
| EC-816 | Carrier has no cargo insurance (lawful) | Exposure on shipper or platform | `DEC-803` | Whether to permit at all |
| EC-817 | Cargo value exceeds carrier's limit | Under-insured load | Platform | Pre-award blocking rule |
| EC-818 | Claim exceeds a limit never knowingly chosen | Limitation likely fails | Counsel | BR-810 evidence |
| EC-819 | Claim filed month 8; carrier says closed | Statutory floor is 9 months | Counsel | Conflicting contract terms |
| EC-820 | Carrier silent past 120 days | Obligation breached | Platform + regulator | Platform's escalation duty |
| EC-821 | Decline given verbally, never in writing | 2-year clock may not start | Counsel | Enforcing written disallowance |
| EC-822 | Shipper and consignee both claim | Duplicate claims | Platform | Who has standing |
| EC-823 | Insurer subrogates against carrier | Platform is records custodian | Legal | Discovery response process |
| EC-824 | Plaintiff subpoenas the selection record | It is the defence — or the liability | Counsel | Retention adequacy |
| EC-825 | Selection record missing, old load | Indefensible selection | Platform | Retention floor `[NEEDS INPUT]` |
| EC-826 | Suspension while load in flight | Completes under monitoring | Ops | Threshold for intercept instead |
| EC-827 | Removal for fraud, load in transit | Recovery protocol; access not cut | Ops + police | Custody handover mechanics |
| EC-828 | Removed carrier returns as new MC/DBA | Re-entry evasion | Platform | Identity linkage without unlawful blacklisting |
| EC-829 | Suspended carrier disputes it | Appeal path | Platform | Appeal timeline |
| EC-830 | Shipper contact colludes with bidder | FR-7 | Platform + shipper | Notifying shipper's management |
| EC-831 | Bidders rotate wins on a lane | FR-8 | Platform + A7 | Antitrust escalation route |
| EC-832 | Shill bid wins then declines | Re-award; freight delayed | A3 | Penalty for repeat declines |
| EC-833 | Fake shipper harvests documents | FR-10 | Platform | Shipper verification depth |
| EC-834 | Claim inflated above declared value | FR-13 | Insurer | Declared-value enforcement |
| EC-835 | Detention claimed, no dwell in tracking | Money dispute | A6 + A8 | Evidence hierarchy |
| EC-836 | Receivable factored; payment misdirected | Money dispute, third party | A6 | NOA verification |
| EC-837 | Charges withheld against open claim | Contested offset | Counsel | BR-821 unresolved |
| EC-838 | Retaliatory or purchased ratings | FR-14 | Platform | Removal criteria |
| EC-839 | Claim open at would-be completion | Blocks `COMPLETED`; invoice splits | A6 | Which state holds the load |
| EC-840 | Claim abandoned by both parties | `CLOSED_UNRESOLVED` | Platform | Closure criteria; rating effect |
| EC-841 | Intrastate-only move | Carmack may not apply | Counsel | `ASM-801` |
| EC-842 | Consignee is a private individual | Claimant with no platform relationship | Platform | How they claim at all |

---

## CHALLENGE: the spine's exception-state list understates trust states

Spine §3 lists `DAMAGED/LOST/PILFERED`, `CLAIM_OPEN`, `DISPUTED`, `CLOSED_UNRESOLVED`. Three are missing:
**`FRAUD_SUSPECTED`** (unlike `DISPUTED`, attaches pre-pickup, suppresses payment, triggers third-party
notification), **`RECOVERY`** (believed stolen and actively being recovered — physically different from
`LOST`), **`CARRIER_SUSPENDED_IN_FLIGHT`** (party-level enforcement colliding with a live shipment).
Requesting these canonically rather than diverging. **Smaller:** no objective states that selection must be
*defensible after an accident*; BR-802/803/819 trace to OBJ-006/007 as closest fit — A10 may sharpen one.

## What this agent cannot do

Resolve `DEC-801` — client and counsel. Confirm what the client's policies actually exclude — needs the
wordings and an insurance broker. Decide whether charges may be offset against an open claim — counsel.
Read the *Montgomery* slip opinion in full — counsel should, before BR-802 is built. **Every citation here
must be verified against the primary source before anyone relies on it.**
