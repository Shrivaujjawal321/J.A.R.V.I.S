# Part A7 — Regulatory & Compliance Surface (USA)

**Scope note.** States **trigger conditions** — facts that make a US regime attach — and the records
and controls that follow. General regulatory awareness, **not legal advice**; certifies nothing. Never
says the platform *is* compliant, only what compliance *would require* and what evidence an auditor or
plaintiff's counsel looks for. §7.9 = what only counsel resolves. Requirements trace **OBJ-007** unless
shown. A8 owns liability *allocation*, A6 charge mechanics, A2 vetting *execution*.

## 7.1 Threshold question — what is the client?

49 U.S.C. §13102: arranging transport of property for compensation is **brokerage**; operating the
truck is **motor carriage**. Separate authorities.

`[NEEDS INPUT: Does the client hold FMCSA broker authority, carrier authority, both, or neither — and will the platform itself arrange transport for compensation, or be software run by a third party holding the authority?]`

| Answer | Consequence |
|---|---|
| **A — licensed property broker** | Part 371 / bond / BOC-3 / UCR surface is the client's, as is negligent-selection exposure (§7.3). BR-701…708 become Must. |
| **B — carrier bidding its own loads** | Conflict of interest in an auction it runs; Parts 387/391/395/382 attach directly. Neutrality disclosure → A3, A10. |
| **C — software vendor, tenant holds authority** | Duties sit with the tenant; platform still stores the evidence they are judged on. Requirements shift to "let the tenant discharge and prove it". |
| **D — neither, yet sets price and awards** | The classic unauthorised-brokerage fact pattern. Counsel question, not design question. |

`[ASSUMPTION: interstate, for-hire, domestic truckload; no household goods | conf: med]`
`[NEEDS INPUT: intrastate-only lanes? Intrastate carriage is state-regulated; not covered here.]`

## 7.2 Trigger register

| # | Trigger | Duty bearer | Platform must hold | Counsel-only |
|---|---|---|---|---|
| T-01 | Arranging transport for compensation | Platform (A/D) | Own authority evidence, shown both sides | Is this brokerage? |
| T-02 | Broker registration valid **only while** BMC-84 bond or BMC-85 trust of **$75,000** in effect (387.307) | Platform-as-broker | Bond/trust certificate; lapse alarm | Bond vs trust; claims path |
| T-03 | **BOC-3** process agents for every state with an office or where contracts are written (Pt 366) | Platform-as-broker; carriers | BOC-3 on file; blanket coverage; refresh on new-state contracting | Reach of "writes contracts" |
| T-04 | Brokered transaction → record shows consignor; originating carrier + registration no.; BOL/freight-bill no.; broker compensation + payer; non-brokerage services + payer; freight charges collected + date paid. **3 yrs; each party may review** (371.3) | Platform-as-broker | Six fields per load, immutable + a party-facing review path | Waiver enforceability; who is a "party" |
| T-05 | FMCSA *Transparency in Property Broker Transactions* — electronic records in **48 hrs**, non-waivable. **Not final** `[verify]` | Platform-as-broker | Per-load electronic retrievability now | Build ahead of finalisation? |
| T-06 | Goods received by carrier under receipt/BOL, interstate | Carrier (Carmack §14706) | BOL, tendered condition/count, delivery signed clear vs exception | Carmack scope |
| T-07 | Carrier may not contract **<9 months** to claim or **<2 years** to sue, from written disallowance (§14706(e)) | Carrier | Per-shipment claim clock; disallowance date | May platform terms touch this? |
| T-08 | Released-value / limitation of liability agreed | Shipper + carrier | Declared value captured **at load creation, pre-bid** — a price input | Validity on-platform |
| T-09 | For-hire interstate, GVWR ≥10,001 lb, non-haz → **$750k** min public liability; **$5m** specified bulk hazmat; **$1m** oil/listed hazmat (387.9) | Carrier | COI: limits, dates, insurer, cancellation notice | Limits above minimum |
| T-10 | Cargo insurance **commercial, not statutory**; broker may carry **contingent cargo** | Commercial choice | Cargo limit vs declared value; contingent policy | Adequacy; triggers |
| T-11 | Driver keeping RODS → HOS (395.3: 11-hr driving / 14-hr window / 60-in-7 or 70-in-8) and ELDs (Pt 395 Subpt B) | Driver + carrier | Windows feasible within HOS; appointment + detention times | Does scheduling create exposure? |
| T-12 | RODS + supporting docs kept **≥6 months** (395.8(k)) | Carrier | Nothing — ingesting ELD data inherits a privacy duty not otherwise held | Do not ingest without advice |
| T-13 | CDL driver under D&A rules → **annual Clearinghouse query**, rolling 365 days (382.701) | **Employing carrier, not platform** | Carrier attestation only, never the result | Is attestation adequate? |
| T-14 | DQ file employment **+3 yrs** (391.51); D&A records to **5 yrs** (382.401) | Carrier | Attestation and its date only | — |
| T-15 | Broker selects a carrier → state **negligent-selection** claim **not preempted** by FAAAA (*Montgomery v. Caribe Transport II*, S. Ct. 2026-05-14, unanimous) | Platform-as-broker | Criteria applied, safety data available at award, why the winner won — frozen, replayable | The whole exposure — §7.9 |
| T-16 | Awarded carrier re-brokers | Carrier; platform contractually | Written consent or prohibition; who actually picked up | Enforceability; remedy |
| T-17 | Carrier leases owner-operators on (376.12) | Carrier | Out of scope unless platform administers owner-operator settlement — then chargeback disclosure attaches | Does settlement reach Pt 376? |
| T-18 | Platform **accepts shipper funds, transmits to carrier** | Platform | Whether funds held, how long, in whose name | **ESCALATE — §7.4** |
| T-19 | Driver or consignee personal data collected | Platform | Notice at collection, purpose, retention, deletion/opt-out — **for a consignee who never signed up** | Per-state applicability |
| T-20 | Repeat carriers bid one lane, observe each other (Sherman §1) | Platform + participants | Bid-pattern surveillance; limits on competitor data shown | Disclosure design |
| T-21 | Hazmat; oversize/overweight permits; **UCR** (also owed by brokers/forwarders/leasing cos.); IFTA | Carrier; UCR also platform-as-broker | Hazmat flag; permit evidence; UCR filing calendar | Scope pending |

## 7.3 The sharpest collision — lowest bid vs negligent selection

In *Montgomery v. Caribe Transport II, LLC* (2026-05-14, unanimous, Barrett J.) the Supreme Court held
a claim that one company negligently hired another to transport goods is **not** preempted by the
FAAAA; states retain authority over safety with respect to motor vehicles. The *Ye v. GlobalTranz* /
*Aspen American v. Landstar* preemption line no longer shields a broker.

Consequence: **an award rule that ignores available FMCSA safety data in favour of price is the fact
pattern a plaintiff builds on, and the platform's own award log is the exhibit.** Not a reason to drop
lowest-bid — Boss specified it — but A2's eligibility gate becomes load-bearing and the award record a
litigation artefact from day one. A3 must price mechanism options against this, not only efficiency.

## 7.4 Money movement — ESCALATION, not analysis

A6 routed this here. **I will not opine on whether the platform is a money transmitter or which state
licences it needs.** Federal MSB status under 31 CFR 1010.100(ff)(5) and its narrow payment-processor
exclusion at (ff)(5)(ii)(B) are fact-specific, and **state money-transmitter licensing is a separate
state-by-state determination** a non-attorney should not attempt. Specialist payments counsel required.
A7 supplies the trigger and the fork only:

| Option | Posture | Trade-off |
|---|---|---|
| **M1** shipper pays carrier direct, platform bills a fee | Does not engage "accept and transmit" | Weakest settlement guarantee; factoring/NOA stays with shipper |
| **M2** funds via licensed processor/bank, platform never holds | Aims at the exclusion without self-assessing into it | Vendor dependency; allocation must be explicit |
| **M3** platform holds and disburses | Raises federal MSB + state MTL | Best product, earliest and highest legal cost |

`[NEEDS INPUT: M1, M2 or M3? A6 cannot finalise settlement requirements without it.]`

## 7.5 Business requirements

| ID | Requirement | MoSCoW | Acceptance | Source |
|---|---|---|---|---|
| BR-701 | Operator status (broker/carrier/vendor) recorded as a documented decision with authority evidence before any load is published | Must | No load reaches PUBLISHED while status unset | §7.1 |
| BR-702 | Where broker authority held, current bond/trust + BOC-3 evidence held with pre-expiry alerting | Must | Expiry simulation alerts operator and blocks new awards | 387.307; Pt 366 |
| BR-703 | Six broker-record elements captured per brokered load, retained ≥3 yrs | Must | 20-load sample: all six present; retention job proves horizon | 371.3 |
| BR-704 | Each party can obtain that transaction's record via a defined path; request + response logged | Must | A shipper and a carrier each request one; both served, both logged | 371.3 |
| BR-705 | Authority status + Part 387 insurance evaluated **at award**, not only onboarding, and frozen into the award record | Must | Award replays the exact state used; later source changes do not alter it | 387.9; T-15 |
| BR-706 | Award record preserves safety/eligibility data at award, criteria applied, any override identity | Must | Decision basis reproducible from stored data alone | *Montgomery* |
| BR-707 | Per-carrier attestation: CDL validity, Clearinghouse currency, D&A programme — dated, attributable — with **no storage of Clearinghouse or D&A results** | Must | Attestation attributable; no field holds a test result | 382.701; 391.51 |
| BR-708 | Pickup/delivery windows checked for HOS feasibility; infeasible ones flagged pre-auction | Should (→OBJ-004) | Infeasible window raises pre-publication flag; flag + response logged | 395.3 |
| BR-709 | No ELD/HOS data ingested, stored or displayed absent documented lawful basis + retention rule | Must | No such field exists without a recorded authorising decision | T-12 |
| BR-710 | Re-brokering prohibited, or only on recorded written shipper consent; party taking possession recorded and reconciled against awarded carrier | Must (→OBJ-006) | Mismatch raises exception before departure; consent retrievable | T-16; →A2/A8 |
| BR-711 | Declared value + released-value term captured at load creation pre-bid, immutable once the auction opens | Must (→OBJ-004) | Post-AUCTION_OPEN edit rejected and logged | §14706 |
| BR-712 | Delivery record captures clear-vs-exception, exception text, signing party | Must (→OBJ-004) | No shipment reaches POD_CAPTURED without it | Carmack; →A5 |
| BR-713 | Claim and suit windows recorded per shipment from the governing document; no platform term shortens them | Must | Displayed dates match the governing document | §14706(e); →A8 |
| BR-714 | Notice at/before collection to every individual whose data is collected, **including an unregistered consignee** — categories, purposes, retention, rights | Must | Unregistered consignee reaches notice + rights path from the delivery message alone | §7.7 |
| BR-715 | Personal data retained per explicit per-class schedule separating rule-fixed from business-decided periods | Must | Every personal-data class maps to a §7.7 row | §7.7 |
| BR-716 | Rights requests (access, deletion, correction, opt-out) received, verified, actioned, logged within the requester's state period | Must | Per state, end-to-end test yields a logged, timed response | 20 state statutes 2026 `[verify per state]` |
| BR-717 | Competitor bid values/identities not disclosed beyond what a documented decision authorises | Must (→OBJ-006) | No bidder-facing view exposes another bid amount or identity | 15 U.S.C. §1; →A3 |
| BR-718 | Repeat-lane bidding monitored for rotation, clustering, withdrawal signatures; detections routed to a named reviewer | Should (→OBJ-006) | Seeded rotation pattern detected and routed | T-20; →A3/A8 |
| BR-719 | Hazmat loads flagged at creation, blocked from award absent authority, endorsement, applicable Part 387 limit | Must (if in scope) | Flagged load not awardable without the evidence | 387.9; Pt 172 |
| BR-720 | Each party's regulatory obligations stated in version-controlled terms, acceptance recorded per version | Must | Accepted version + timestamp retrievable per user | derived |

## 7.6 Non-functional requirements

| ID | Category | Requirement | Target | Measurement |
|---|---|---|---|---|
| NFR-701 | Retention | Broker transaction records | ≥3 yrs (371.3) | Restore a record ≥3 yrs old |
| NFR-702 | Retention | Beyond the regulatory floor | `[NEEDS INPUT: not fixed by 371.3; do not set without counsel]` | Signed-off schedule |
| NFR-703 | Auditability | Award decisions immutable, replayable | 100% reproducible from stored basis | Quarterly replay, random sample |
| NFR-704 | Auditability | Write-once log of create/modify/delete on load, bid, award, eligibility, POD, claim — actor, before/after, timestamp | 100% entity coverage | Tamper test + coverage report |
| NFR-705 | Auditability | Records furnishable electronically | Designed against the pending 48-hr proposal `[verify]` | Timed retrieval drill |
| NFR-706 | Security | Driver/consignee data encrypted in transit + at rest, access role-restricted | Attempts logged | Access review; pen test |
| NFR-707 | Security | Authority/insurance docs segregated, every view attributable | 100% of views logged | Access-log sample |
| NFR-708 | Compliance | Rights-request response | Shortest applicable state period `[verify per state]` | Request-log ageing report |
| NFR-709 | Compliance | Notice reachable by an unregistered consignee | ≤1 step from any delivery message | Test with unregistered recipient |
| NFR-710 | Minimisation | No ELD/HOS, Clearinghouse or D&A data stored | Zero such fields absent BR-709 | Schema review each release |
| NFR-711 | Availability | Evidence retrieval independent of the transactional path | Works while auction/award degraded | Failover drill |
| NFR-712 | Integrity | POD/BOL artefacts tamper-evident | Post-capture alteration detectable | Integrity check on sample |

Considered, not applicable: localisation (single jurisdiction); portability (no duty found beyond BR-716).

## 7.7 Retention by data class

| Class | Period | Fixed by | Holder |
|---|---|---|---|
| Broker transaction record | ≥3 yrs | 371.3 | Platform-as-broker |
| Driver RODS / ELD support | ≥6 months | 395.8(k) | Carrier, not platform |
| Driver qualification file | Employment +3 yrs | 391.51 | Carrier |
| D&A testing records | To 5 yrs by type | 382.401 | Carrier |
| BOL / POD / exception notation | **Open** | Not fixed; driven by claim/suit horizon | Platform + carrier |
| Bid history, award decision basis | **Open** | No rule found; litigation-evidence value argues long | Platform |
| Consignee contact data | **Open** | State statutes require a stated purpose-limited period, not a number | Platform |
| Financial/settlement records | **Open** → A6 | Tax/reporting rules, not this part | Platform |

**No "Open" period may be filled with a number here** — each is a counsel-plus-business decision, and a
fabricated period is worse than a blank.

## 7.8 Edge-case register

| ID | Trigger | What happens | Decides | Unresolved |
|---|---|---|---|---|
| EC-701 | Operator authority revoked / bond lapses mid-auction | Auctions halt; awarded-unmoved loads stranded | Operator + counsel | May in-flight loads complete? |
| EC-702 | Carrier authority revoked between award and pickup | Award must be reversible | Ops (A9) | Cost of reversal → A6 |
| EC-703 | Carrier insurance cancelled mid-transit | Freight moving uninsured; no clean stop | Ops + counsel | May transit continue? |
| EC-704 | COI valid, limits below load requirement | Eligibility fails though carrier authorised | A2 | May shipper waive? |
| EC-705 | Winning bid implies transit infeasible under HOS | Award incentivises a violation | A3 + ops | Block, warn, or log acceptance |
| EC-706 | Winner is broker/agent, not asset holder | Undisclosed re-brokering; pickup mismatch | A2 | Consent model → BR-710 |
| EC-707 | Party at pickup ≠ awarded carrier | Identity theft / fictitious pickup | Ops, real time | Hard stop vs flag |
| EC-708 | Carrier demands 371.3 record; contract purported to waive | Waiver may not hold; refusal is exposure | Counsel | Enforceability |
| EC-709 | Shipper demands competitor bid amounts shown | Raises the §1 information-exchange question | Counsel + A3 | Disclosure design |
| EC-710 | Same three carriers alternate wins on a lane | Rotation signature; platform has knowledge | A8 + counsel | Duty on knowledge |
| EC-711 | Consignee demands deletion | May conflict with 371.3 retention | Counsel | Which prevails |
| EC-712 | Consignee never consented, refuses contact, must be notified | Notice duty, no relationship | Counsel | Lawful basis to contact |
| EC-713 | Driver demands data held via the carrier | Requester is not the account holder | Counsel | Standing + verification |
| EC-714 | Post-accident subpoena for award decision basis | Award log becomes evidence | Counsel | Legal-hold design |
| EC-715 | Legal hold collides with automated purge | Purge must be suspendable per record | Platform | Hold mechanism |
| EC-716 | Undeclared hazmat found at pickup | Carrier lacks authority/insurance | A4/A1 | Penalty and cost |
| EC-717 | Oversize/overweight at pickup, no permits | Cannot move legally | A4 | Who bears cost |
| EC-718 | Load enters a state with no BOC-3 designation | Process-agent gap | Counsel | Refresh trigger |
| EC-719 | Shipper is itself a broker re-brokering in | Authority + consent stack | A2 + counsel | Permitted at all? |
| EC-720 | Carrier factored receivable; NOA on file | Payment redirected → A6 | A6 | Regulatory only if funds held |
| EC-721 | Platform holds funds under M3, no licence determination | Unlicensed money transmission exposure | **Counsel — escalate** | §7.4 |
| EC-722 | Transparency rule finalises mid-build, 48-hr duty | Records must already be electronic | Operator | Build-ahead decision |
| EC-723 | Intrastate-only lane added | Federal analysis does not cover it | Counsel | State by state |
| EC-724 | Clearinghouse attestation proves false after an incident | Attestation-only vetting tested in court | Counsel | Depth of verification |
| EC-725 | Award manually overridden for a non-price reason | Most scrutinised record in the file | A9 | Override authority + logging |
| EC-726 | Worst safety data submits the lowest bid | The core collision, every auction | Boss (design) | §7.3 |
| EC-727 | UCR/IFTA/permit filings missed for own authority | Administrative non-compliance | Operator | Calendar ownership |

**Assumptions** — `ASM-701` interstate for-hire domestic truckload only *(med)* · `ASM-702` no household
goods *(med)* · `ASM-703` no hazmat phase 1 *(low — blocks BR-719 sizing)* · `ASM-704` platform employs no
drivers *(high)* · `ASM-705` FMCSA public safety data stays available for vetting *(med)*.
**Constraints** — `CON-701` no publish before BR-701 status set · `CON-702` no award without frozen
authority + insurance evidence · `CON-703` no ELD/Clearinghouse/D&A data stored.
**Risks** — `RSK-701` negligent-selection claim after a serious accident on a price-only award (P4/I5) ·
`RSK-702` unauthorised-brokerage finding under answer D (P3/I5) · `RSK-703` unlicensed money transmission
under M3 (P3/I5) · `RSK-704` incomplete 371.3 record (P3/I3) · `RSK-705` consignee privacy complaint,
unconsented party (P3/I3) · `RSK-706` §1 exposure from bid-transparency design (P2/I5).

## 7.9 Counsel handoff

US transportation counsel licensed in the operator's state, plus specialists where noted:

1. Whether the design constitutes **property brokerage**; which authority to obtain — the §7.1 fork.
2. **Post-*Montgomery* negligent-selection exposure** of a lowest-bid award, and what selection standard is defensible. A litigation-risk opinion, not a product decision.
3. Enforceability of a **waiver of the 371.3 review right**; whether to build to the pending proposal.
4. Whether platform terms may address **Carmack claim/suit windows**, and how released-value terms may be offered on-platform (with A8).
5. **Money transmission — federal MSB status and state licensing.** Payments counsel; no M3 without it.
6. **State privacy applicability**, consignee notice for a non-registered party, deletion-vs-retention (EC-711).
7. **Antitrust review** of bid-information disclosure and any published lane pricing.
8. **Re-brokering consent terms and remedies**; duty on detected double brokering.
9. **Retention periods for every "Open" class** in §7.7, plus the legal-hold mechanism.
10. **Insurance programme design** — limits above statutory minimum, contingent cargo, platform E&O.

**CHALLENGE:** Spine §4 treats negligent selection as a consequence to be "surfaced as a requirement or
risk." That is understated now. *Montgomery* removed the preemption defence nationwide in May 2026,
after the spine was written. It is no longer a risk-register line against the lowest-bid rule — it is a
**precondition on the award mechanism itself**. A3's options should be re-scoped so every option shown
to Boss carries its post-*Montgomery* eligibility gate rather than treating the gate as separable.

**Sources.** [371.3](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-III/subchapter-B/part-371/subpart-A/section-371.3) ·
[387.307](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-III/subchapter-B/part-387/subpart-C/section-387.307) ·
[FMCSA bond rule](https://www.fmcsa.dot.gov/registration/broker-and-freight-forwarder-financial-responsibility-rule-overview-and-compliance) ·
[Pt 366](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-III/subchapter-B/part-366) ·
[BOC-3](https://cms7.fmcsa.dot.gov/registration/form-boc-3-designation-agents-service-process) ·
[§14706](https://www.law.cornell.edu/uscode/text/49/14706) ·
[387.9](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-III/subchapter-B/part-387/subpart-A/section-387.9) ·
[395.8](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-III/subchapter-B/part-395/subpart-A/section-395.8) ·
[Pt 395 Subpt B](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-III/subchapter-B/part-395/subpart-B) ·
[382.701](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-III/subchapter-B/part-382/subpart-G/section-382.701) ·
[382.401](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-III/subchapter-B/part-382/subpart-D/section-382.401) ·
[391.51](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-III/subchapter-B/part-391/subpart-F/section-391.51) ·
[376.12](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-III/subchapter-B/part-376/subpart-B/section-376.12) ·
[*Montgomery* opinion](https://www.supremecourt.gov/opinions/25pdf/24-1238_1b7d.pdf) ·
[*Montgomery* analysis](https://www.faegredrinker.com/en/insights/publications/2026/5/supreme-court-decides-montgomery-v-caribe-transport-ii-llc) ·
[Transparency NPRM](https://www.federalregister.gov/documents/2025/02/18/2025-02707/transparency-in-property-broker-transactions) ·
[31 CFR 1010.100](https://www.law.cornell.edu/cfr/text/31/1010.100) ·
[FinCEN MSB](https://www.fincen.gov/resources/money-services-business-msb-registration) ·
[State privacy 2026](https://www.multistate.us/insider/2026/2/4/all-of-the-comprehensive-privacy-laws-that-take-effect-in-2026) ·
[UCR fees](https://www.fmcsa.dot.gov/regulations/federal-register-documents/2026-06726) ·
[15 U.S.C. §1](https://www.law.cornell.edu/uscode/text/15/1)

*General regulatory awareness only. Not legal advice. Qualified counsel required for binding decisions in the relevant US jurisdiction.*
