# R3 — Liability, insurance and fraud, revised for broker-of-record

**Revises** `part-A8-liability-trust-disputes.md` under `DEC-LOCK-003`. IDs stay in the **800-899** block.
`[REVISED]` = meaning changes · `[NEW]` = did not exist · `[CLOSED]` = resolved.

> **Not legal advice, and not from a lawyer.** No attorney-client relationship. Business requirements
> informed by legal structure; legal conclusions are counsel's.
> ⚠️ **Citations are DRAFT until verified in Westlaw/Lexis or the official reporter** — LLMs fabricate
> plausible citations. The two case anchors were checked against Justia/CourtListener here; anything
> `[verify]` was not read in primary source. `[inference]` = analysis, not conclusion.

---

## R3.1 `DEC-801` is CLOSED — and eight things resolve with it

**`DEC-801` `[CLOSED]`.** The operating entity holds property-broker authority — position **P1**. P2 (motor
carrier) and P3 (software vendor) are off the table; §8.1's three-position table is historical and must not
be presented as an open fork.

| Was conditional on `DEC-801` | Now resolves to |
|---|---|
| **BR-801** `[REVISED]` — "record who bears cargo liability per `DEC-801`" | No longer a variable. Per load: platform = broker of record and contracting principal on **both** legs; awarded motor carrier = the Carmack carrier. The field becomes an *assertion to verify*, not a choice to capture. Acceptance: no load reaches `AWARDED` without the awarded MC named as Carmack carrier and the platform as broker of record. |
| **BR-805 / `DEC-803`** — cargo cover "as commercial eligibility" | Promoted to **hard gate condition** (R3.4). `DEC-803` partly closes: cover is mandated; the *limit* stays `[NEEDS INPUT]`. |
| **BR-821 / EC-837** — offset against an open claim | Still counsel's, but reshaped: not "may a shipper withhold from a carrier," but "may the platform withhold **its own payable** against **its own exposure**." Contractual, not statutory, in the first instance `[inference]`. |
| **§8.4** — "platform's role turns on `DEC-801`" | **Claim recipient** shipper-side, **claimant** carrier-side. R3.6. |
| **RSK-804** — "found to have acted as a carrier" | Mitigation changes entirely: was "resolve `DEC-801` pre-build," is now **ongoing holding-out discipline** (R3.2). Holding authority does not retire this risk — authority is not the test. |
| **EC-806/807/808** — who bears the uninsured loss; does the platform indemnify the shipper | The platform is the shipper's counterparty, so the demand lands on it regardless of cause `[inference]`. No longer questions about *who*, now about *recourse* (R3.5). |
| **EC-816** — carrier lawfully carries no cargo insurance | Resolved by gate, not by tolerance. R3.4. |
| **§8.9 / BR-816** — does reputation enter the award? | Unchanged, still `DEC-802`. Being the broker does not answer it. |

---

## R3.2 The Carmack position, precisely

Under the Carmack Amendment, **49 U.S.C. §14706**, the **motor carrier** bears cargo liability; a
**property broker** arranges transportation for compensation and is generally not a Carmack defendant.
Definitions: **§13102(2)** (broker), **§13102(14)** (motor carrier); **49 CFR §371.2** distinguishes
brokers from bona fide agents.

**The qualification that decides real cases.** Authority is not the test — conduct is. Courts ask how the
party held itself out and whether it accepted legal responsibility to transport:

- *Essex Ins. Co. v. Barrett Moving & Storage, Inc.*, 885 F.3d 1292 (11th Cir. 2018) — status turns on
  whether the party accepted legal responsibility to transport, or communicated it was brokering to a
  third party. ⚠️ Verify in Westlaw/Lexis.
- *Tryg Ins. v. C.H. Robinson Worldwide, Inc.*, 767 F. App'x 284 (3d Cir. 2019) — a licensed broker
  treated as a carrier because it never made clear it acted only as a broker. **Non-precedential.**
  ⚠️ Verify in Westlaw/Lexis.

Note for counsel: the statute defines *broker* partly by "holds itself out," and the case law finds *carrier*
status by the same phrase `[inference]`.

**What the platform must do** — `BR-822` `[NEW]` (Must · OBJ-006/007): every shipper-facing artifact states
the platform's role as property broker with its MC/FF number, and the **awarded motor carrier is the named
carrier in the BOL's carrier field** — never the platform. Acceptance: no BOL, rate confirmation, quote,
invoice, tracking screen or notification identifies the platform as carrier or omits the carrier's
identity. Source: *Essex*, *Tryg* `[verify]`.

**What to avoid** — each is a fact a plaintiff uses `[inference]`: platform in the BOL carrier box ·
agreement or marketing verbs promising to "transport," "deliver," "ensure delivery" · contractually
assuming cargo-loss responsibility · one undifferentiated "we move your freight" service with the carrier
invisible · directing driver route, sequence or method beyond load requirements · dispatch instructions in
the platform's own name.

**Tension worth naming:** the trust story ("we own the outcome") competes directly with the holding-out
discipline that keeps the platform out of Carmack. Marketing copy is now a legal artifact.

---

## R3.3 Negligent selection is now directly the platform's — `BR-802` is the load-bearing requirement

After *Montgomery v. Caribe Transport II, LLC*, No. 24-1238, 608 U.S. \_\_\_ (2026) (14 May 2026, unanimous),
the FAAAA preemption defence to state-law negligent-hiring claims against brokers is gone `[verify — counsel
must read the slip opinion before BR-802 is built]`. The platform is the broker who chose. **`BR-802` is the
single most load-bearing requirement in this BRD** — not logging, but the defence exhibit, and equally the
plaintiff's exhibit if it is thin.

`BR-802` `[REVISED]` (Must · OBJ-006/007) — per award, immutably: eligibility **gate version** applied ·
authority status at decision time with retrieval timestamp · FMCSA safety snapshot **with its own age** ·
insurance evidence and its source · every excluded bidder with the criterion it failed · basis of award ·
any override with named actor and written rationale.

**What makes it indefensible** — build these as failure conditions:

| Defect | Why it is worse than no record `[inference]` | Requirement |
|---|---|---|
| **Stale safety snapshot** | The recorded old timestamp proves the platform saw what it relied on and relied on it anyway | `NFR-802` `[REVISED]`: staleness bounded **and displayed at decision time**, not merely stored |
| **Override with no rationale** | Shows a human overrode the gate and nobody can say why | `BR-824` `[NEW]` (Must): an override without written rationale + named actor **cannot complete** — award blocked, not flagged |
| **Gate loosened without versioning** | Nobody can prove which rule was in force on the load in suit | `BR-823` `[NEW]` (Must): gate versioned, every award bound to an immutable version; `NFR-806` `[NEW]`: append-only, exportable registry |
| **No excluded-bidder list** | Cannot show the gate did anything | Acceptance: every award reconstructs its pool *and* its rejections without live data |
| **Retention shorter than the limitations tail** | The defence exists and is unavailable | `NFR-801` `[NEEDS INPUT]` — set against limitations periods, not storage cost |

---

## R3.4 The insurance stack the platform itself now needs

`BR-825` `[NEW]` (Must · OBJ-006/007): the platform's own programme in force and evidenced **before the first
live award** — **contingent cargo**, **contingent auto liability**, **E&O** covering the selection act.
Limits and premiums `[NEEDS INPUT]`; an insurance broker sizes this.

**The specific gap.** FMCSA eliminated the cargo-insurance filing requirement for most for-hire carriers of
general freight effective 21 March 2011 (75 FR 35367, 22 June 2010); household-goods carriers and forwarders
remain subject `[verify]`. A **fully compliant carrier can hold zero cargo cover.**

**Whose loss is that now?** The shipper's counterparty is the platform, so the demand lands there, and its
recourse runs against a carrier with no cargo policy behind it. Whether the platform is *legally* liable is
counsel's question. Worse, contingent cargo commonly excludes exactly the losses most likely here —
double-brokered and impersonation `ASM-803` `[ASSUMPTION | conf: med — wordings must be read]`.

**Eligibility-gate consequence:** cargo cover moves from prudent to **gate-blocking**. `BR-805` `[REVISED]`
(Must): no award without cargo cover evidenced **from the insurer or its agent**, limit recorded against
declared value; a load exceeding that limit is blocked pre-award, not flagged post-loss. `BR-826` `[NEW]`
(Must): each load records which layer is expected to respond first — carrier cargo, contingent cargo, or
none — so an uncovered load is visible before award. `DEC-803` narrows to **what limit, and whether any
exception is ever permitted** (recommend: none). The gate shrinks the pool; that trade belongs with
`DEC-201`.

---

## R3.5 Fraud re-assessed — **this is the section written under the wrong assumption**

§8.7's fourteen typologies remain correct as *typologies*. The **loss allocation around them was written for
an introducer** and is wrong now: as contracting principal on both legs, the platform owes the shipper and
has already promised the carrier.

| Typology | Old assumption | Who eats it now `[inference]`, and what recourse exists |
|---|---|---|
| **FR-1 double brokering** | Shipper vs. two carriers; platform an introducer | **Platform** — it contracted to arrange and an unvetted third party held the freight; contingent cargo may exclude it. Recourse: carrier-agreement breach + indemnity, against a carrier often judgment-proof |
| **FR-2 carrier identity theft** | Shipper's loss; real MC also a victim | **Platform** — it contracted with an entity that does not exist as represented; its own vetting failed. Recourse: insurance (often excluded), criminal referral, near-zero civil recovery |
| **FR-3 fictitious pickup** | Shipper's loss | **Platform** — freight collected under a platform-arranged movement, never delivered. Resolves `EC-808`: indemnity is now assumed by structure, not chosen |
| **FR-12 fake NOA / payment redirect** | Shipper mispays | **Platform pays twice** — its payable, its NOA duty (A6 `BR-606/607/608`). Recourse: the fraudulent payee; verification is the only real control |
| **FR-6 forged POD** | Carrier's problem | Platform's — it invoiced on a false delivery. Recourse: withhold/offset per R3.6 |

**RSK-802 `[REVISED]`** — impact unchanged (5), but exposure lands on the operating entity's balance sheet
rather than on a shipper-carrier pair. **`BR-830` `[NEW]`** (Must): re-brokering prohibited by contract with
recorded carrier acknowledgement; any driver/tractor/MC mismatch at pickup (`BR-806`) opens a
cargo-integrity case that suppresses payment pending resolution.

§8.7's structural point bites harder now: price-only ranking selects for FR-1/2/3/9 and the platform holds
the loss. The eligibility gate is the only control acting *before* freight and money move.

---

## R3.6 The claims path with the platform in the middle

| Question | Position |
|---|---|
| Who does the shipper claim against? | **The platform**, on the shipper agreement — it is the counterparty. Whether the shipper may *also* claim the carrier directly under Carmack is counsel's `[verify]`; assume it can, and design for parallel claims. |
| How does the platform pursue the carrier? | Two routes, both needing contract support: the **carrier agreement** (breach, indemnity, insurance covenants), and a **Carmack claim** as party in interest or by assignment/subrogation from the shipper `[verify — standing needs counsel]`. |
| Statutory clocks | `BR-808` unchanged, now binding the platform as recipient: §14706(e)(1) floors and the §370.3/.5/.9 content and 30/120/60-day duties run on whoever handles the claim. |
| Is the carrier paid while a claim is open? | **Liability logic:** the platform needs an express contractual right to withhold or offset its payable against exposure on the same load; without that term, withholding is itself a breach `[inference]`. Whether to exercise it is counsel + A6/R1 (`BR-821`, A6 `BR-603/604/605`). |

`BR-827` `[NEW]` (Must): claim intake accepts a shipper claim **against the platform**, with §370.3 minimum
content. `BR-828` `[NEW]` (Must): every shipper-side claim auto-opens a mirrored carrier-side claim on the
same load with independent clocks — the platform must never be time-barred against its carrier because it
was defending the shipper's claim. `BR-829` `[NEW]` (Must): the withhold/offset right in force is recorded
per load; any exercise logs grounds, amount and linked claim ID.

---

## R3.7 Contractual structure — named for counsel to draft, not drafted here

| Instrument | Terms that must exist |
|---|---|
| **Shipper agreement (brokerage services)** | Broker-not-carrier role designation; **no** promise to transport, deliver or ensure delivery; disclaimer of cargo-loss responsibility with pass-through of Carmack rights against the carrier; claims procedure; declared/released-value handling (`BR-810`); credit terms → A6 — *R3.2, R3.6* |
| **Carrier agreement (broker-carrier)** | Carrier is sole Carmack carrier; insurance covenants — minimum cargo limit, insurer-sourced COIs, cancellation notice, platform as certificate holder; **no re-brokering**, with consequence; indemnity and defence; assignment of claim rights; **express offset/withhold right**; driver/tractor/MC identity warranty at pickup; audit and record-access rights — *R3.4, R3.5, R3.6* |
| **Rate confirmation** | Load-level incorporation of the carrier agreement; carrier named as carrier — *R3.2* |
| **BOL template + policy** | Awarded carrier in the carrier field, platform never in it; clear-vs-exception notation (A5) — *R3.2* |
| **T&Cs + marketing review protocol** | Standing counsel review of any copy that could read as accepting responsibility to transport — *R3.2* |
| **Insurance programme** | Contingent cargo, contingent auto, E&O; **wordings read for double-brokering and impersonation exclusions** pre-launch — *R3.4* |

`BR-831` `[NEW]` (Must): the platform can produce, per load, the exact versioned contract set in force —
shipper agreement, carrier agreement, rate confirmation, BOL. A defence that cannot say which terms
applied is not a defence `[inference]`.

---

## What this agent cannot do

Read the *Montgomery* slip opinion in full · confirm what the platform's policies exclude (needs wordings +
an insurance broker) · decide the offset question · determine the platform's standing to bring a Carmack
claim · set retention against limitations tails · set any limit, cap, window or premium.
**Every citation above must be verified against the primary source before anyone relies on it.**

---
*Educational summary, not legal advice. Verify with a licensed attorney.*
