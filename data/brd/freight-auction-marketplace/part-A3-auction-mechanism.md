# Part A3 — Auction & Bidding Mechanism

**Scope:** auction lifecycle, bid rules, A2's gate applied, award and tie-breaks, failure paths,
anti-gaming, alternatives. **Not here:** eligibility (A2), settlement (A6), fraud and penalties (A8),
regulation (A7).

---

## 4.1 The legal constraint that bounds the mechanism

In the US a party that selects a motor carrier for a shipper can be sued for **negligent selection**,
and *the selection criteria become discovery evidence*. **This is settled law, nationwide.** In
*Montgomery v. Caribe Transport II, LLC*, No. 24-1238, 608 U.S. ___ (2026) (14 May 2026, 9-0,
Barrett, J.), the Supreme Court held a state-law negligent-hiring claim against a freight broker
falls inside the FAAAA safety exception and is **not** preempted, reversing the Seventh Circuit. The
broker was C.H. Robinson. The preemption defence that ended these claims at the pleading stage is
gone in all fifty states.

**Awarding on price alone while FMCSA safety data was available and unused is the exact fact pattern
plaintiffs' counsel look for**, and post-*Montgomery* they get to prove it. SAFER/SMS is public. A
platform that *collects* safety data then ignores it at award has built the exhibit against itself.

**Minimum defensible design — binding on every option below:**

1. Price ranks **within** a pool; it does not define the pool (DEC-301).
2. The gate is written, versioned, applied identically to every bidder (A2 owns content); no silent
   admission of a failing carrier.
3. Eligibility **re-verified at award** — authority and insurance lapse between bid and award.
4. The **award record is the evidence** (BR-303), retained for the limitation period
   `[NEEDS INPUT: retention]`.
5. Every override named, reasoned, logged.

**DEC-301 — Award basis.** *Boss-supplied: lowest bid wins.* Recorded, not re-litigated;
consequences carry as RSK-301…309. What *Montgomery* changes is the gate's **status**: **price
competes inside a safety-gated pool** is no longer A3's preference but a precondition on every option
in §4.7 (A7 challenge, accepted). Price-only across all comers stays available to Boss, but it is not
a neutral fork — it manufactures the plaintiff's exhibit, and would need written acceptance by the
client *and* its insurer.

---

## 4.2 Auction lifecycle

Spine §3 states carry unchanged (PENDING · OPEN · CANCELLED · FAILED_NO_ELIGIBLE_CARRIER → ops desk).
A3-owned transitions:

| State | Trigger | To |
|---|---|---|
| `AUCTION_EXTENDED` | Anti-snipe (DEC-305) or thin-market re-open (DEC-310) | CLOSED |
| `AUCTION_CLOSED` | Close time or early close (DEC-308) | AWARD_PENDING · FAILED_NO_BIDS · FAILED_ALL_ABOVE_LIMIT |
| `AWARD_PENDING` | Winner determined, gate re-verified | ACCEPTED · DECLINED · LAPSED · VOIDED_INELIGIBLE |
| `AWARD_DECLINED`/`AWARD_LAPSED` | Refusal / expiry | Cascade (DEC-309) or re-auction |
| `AWARD_VOIDED_INELIGIBLE` | Gate fails on re-verification | Cascade or re-auction |
| `AUCTION_FAILED_NO_BIDS` | Zero bids at close | DEC-310 |
| `AUCTION_FAILED_ALL_ABOVE_LIMIT` | All bids above ceiling (DEC-306) | Re-auction · accept · fall back |

**CHALLENGE (additive).** Spine §3 lists three A3 exception states; three more are proposed above —
each a distinct decision by a distinct party, so folding them into an existing state loses
who-decides.

---

## 4.3 Parameters that must be decided before this can operate

Real forks. **A3 does not choose; every row is `[NEEDS INPUT]`.** No numbers invented.

| ID | Fork | Trade-off |
|---|---|---|
| **DEC-302** | Open vs sealed bidding | Open: faster price fall and returning bidders, but self-policing collusion. Sealed: less collusion, less tension, worse curse. |
| **DEC-303** | Standing best price, or rank only | The number invites grinding and leaks rivals' costs across repeat lanes. Rank-only: tension, less leakage. |
| **DEC-304** | Duration; fixed or shipper-set | Longer than the shipper's slack is unusable; US spot demand is often same-day. |
| **DEC-305** | Anti-snipe extension vs hard close | Hard close pushes bidding into an unsupervised last second; auto-extension makes close time unpredictable. |
| **DEC-306** | Reserve / ceiling price | Turns a bad award into a clean failure and blocks thin-market gouging; if disclosed it becomes the price. |
| **DEC-307** | May the shipper decline the winner? | Binding award is what makes bidding worth the effort; discretion allows judgement the gate cannot encode but reinstates the human selection decision — where liability attaches. Post-*Montgomery* that is sharper: it moves a discoverable decision to the party holding *less* safety data. **Highest-consequence fork.** |
| **DEC-308** | Shipper early close | Useful under time pressure; indistinguishable from favouritism to carriers about to bid. |
| **DEC-309** | Decline cascade vs re-auction | Fast, but the runner-up's price is stale and truck re-committed; creates a win-then-decline incentive. |
| **DEC-310** | Thin-market degradation | §4.5 |
| **DEC-311** | Minimum decrement | Stops one-cent grinding; raises the clearing price and makes bid patterns legible enough to coordinate around. |
| **DEC-312** | Overnight / weekend / holiday close | An unattended close awards and starts a clock nobody can rescue, on freight with a Monday appointment. |

---

## 4.4 Bid rules and award

| ID | Requirement | MoSCoW | Traces | Acceptance | Source |
|---|---|---|---|---|---|
| **BR-301** | Only a carrier passing A2's gate for *this load* may bid; an ineligible price is never recorded or ranked. | Must | 002/006/007 | No audited auction ranks a gate-fail bid. | §4.1 |
| **BR-302** | Eligibility re-verified at award; failure → `AWARD_VOIDED_INELIGIBLE` before commitment. | Must | 006/007 | Gate result timestamped at/after close on every award. | §4.1 |
| **BR-303** | The award record **is** A8's selection record — one requirement, not two: authority status, safety snapshot, insurance evidence, gate version, who was excluded and why, every bid with time, winner, rule. | Must | 006/007 | Reproducible; shows why the winner won *and* who was excluded. | 49 CFR 371 → A7; A8 |
| **BR-304** | Award to the lowest bid in the eligible pool, tie-broken per BR-305. | Must | 001 | Winner is the minimum-price eligible bid, else override logged. | **Boss** |
| **BR-305** | Lowest-price ties resolve by a pre-published deterministic order. | Must | 001/006 | Same inputs, same winner; order published beforehand. | `[NEEDS INPUT: earliest / safety / on-time / random — safety is most defensible post-*Montgomery*]` |
| **BR-306** | Any gate or award override attributed to a named person, with a reason. | Must | 006/007 | No override lacks identity and reason. | §4.1 |
| **BR-307** | A bid is a firm commitment to move the load at that price on stated terms until close. | Must | 002 | Accepted bid = rate-confirmation price → A6. | Derived |
| **BR-308** | Pre-close withdrawal only under stated policy; recorded against the bidder. | Should | 006 | Withdrawals on the bidder record → A2/A8. | `[NEEDS INPUT]` |
| **BR-309** | Acceptance runs on a bounded window; expiry → `AWARD_LAPSED` → DEC-309. | Must | 002 | Nothing sits in AWARD_PENDING past the window. | `[NEEDS INPUT]` |
| **BR-310** | Any post-award price change, including at the dock, recorded with requester, reason, amount, approver; unrecorded changes are unpayable. | Must | 001/005/006 | Settled = awarded bid plus approved changes. | RSK-303 |
| **BR-311** | Re-trade frequency and magnitude tracked per carrier and lane, exposed to A2 and A8. | Must | 001/006 | Per-carrier re-trade rate queryable. | Derived |
| **BR-312** | Bidder identity resolves to verified operating authority; bidding under one while operating under another is blocked. | Must | 006/007 | No award where identity and authority disagree. | → A2 |
| **BR-313** | Broker-authority-only bidder flagged at bid time; shipper sees it pre-award. | Must | 006/007 | Authority-type flag on every bid. | Spine §1 |
| **BR-314** | Bidder-visible data must not let bidders infer rivals' identity or pricing across auctions. | Should | 006 | No rival-identifying field. | → A7 |
| **BR-315** | Bid patterns monitored for rotation, coordinated withdrawal and price alignment on repeat lanes. | Should | 006/007 | Flags actioned or dismissed with reason. | Sherman §1 |
| **BR-316** | Parties under common ownership or control may not bid twice in one auction. | Must | 006 | Related-entity second bids rejected. | Derived |
| **BR-317** | Shipper, operator and related parties may not bid. | Must | 001/006 | No bid traces to shipper or operator. | Anti-shill |
| **BR-318** | Where pool size or bid count falls below the competitive threshold, the auction is labelled; DEC-310 applies. | Must | 001/003 | Every award carries bid-count and pool size. | Derived |

---

## 4.5 Thin markets — a one-bidder auction is not an auction

Early on, single- and zero-bidder auctions are the normal case. With one bidder, "lowest bid wins"
awards at the bidder's ask with no tension — *worse* than a negotiated rate, since a bidder who sees
a thin pool prices to it. **DEC-310 `[NEEDS INPUT]`:**

| Option | Trade-off |
|---|---|
| Award anyway | Fastest; no price discipline; teaches carriers to price thin pools |
| Extend / re-open | Spends the scarcest resource: lead time |
| Ceiling test only (DEC-306) | Simple, defensible; needs a ceiling |
| Fall back to a posted rate | Preserves service; abandons the premise where it matters most |
| Escalate to human desk (A9) | Best coverage; unscalable; reintroduces selection liability |

**CON-301:** tension depends on pool depth **per lane**, not platform size. A platform with two
carriers on a lane runs a two-carrier auction. → A10

---

## 4.6 Known failure modes, applied to US truckload

| ID | Mode | How it presents here | P | I |
|---|---|---|---|---|
| **RSK-301** | Winner's curse | Winner most underestimated cost (fuel, deadhead, detention, HOS) — likeliest to re-trade or fail. | 4 | 4 |
| **RSK-302** | Adverse selection | Cheapest via a deficiency the gate misses: maintenance, unpaid drivers, minimum-only insurance. | 4 | 4 |
| **RSK-303** | **Post-award re-trade at the dock** | Carrier demands more on arrival; the shipper has an appointment, so it pays. **The biggest practical leak — a competitive award becomes a hostage negotiation, erasing OBJ-001.** | 4 | 5 |
| **RSK-304** | Service-quality collapse | Only price is measured, so on-time, communication and claims decay. | 4 | 4 |
| **RSK-305** | Fraud attraction | Double brokering, identity theft, fictitious pickup — the cheapest bid comes from a party never intending to haul. → A8 | 4 | 5 |
| **RSK-306** | Collusion / bid rotation | Repeat carriers learn the lane's rotation; open bidding makes the cartel self-policing. → A7 | 3 | 5 |
| **RSK-307** | Shill / spoiler bids | Shipper shill anchors down; spoiler wins low, declines, exposes the runner-up. | 3 | 3 |
| **RSK-308** | Negligent selection | Price-only award; FMCSA data available, unused. No preemption shield post-*Montgomery*; the §4.1 gate is the only mitigation left. | 4 | 5 |
| **RSK-309** | Bidder fatigue | Low win rates or advisory awards (DEC-307) → bidding stops → the pool collapses with OBJ-001. | 4 | 4 |

---

## 4.7 Mechanism alternatives — options with honest trade-offs

**DEC-313 `[NEEDS INPUT]`.** For Boss's choice; DEC-301 stands unless he changes it. **Every option
below runs on a gated pool — post-*Montgomery* the gate is not a variable.** Only the ranking inside
it varies.

| Mechanism | Gains | Costs |
|---|---|---|
| **Lowest bid among qualified** (§4.1 minimum) | Keeps Boss's rule; the award record is defensible | Does nothing about curse, re-trade, service collapse |
| **Best-value scoring** (price + safety + on-time) | Answers §4.1; the one at-scale precedent scored quality beside price, so a strong carrier could win without being cheapest (A10) | Weights are a policy choice and become evidence too; opaque; disputable; needs history absent at launch |
| **Reserve / ceiling** | Bad award becomes a clean failure; thin-market cover | Becomes the price if leaked; shipper must know its limit |
| **Second-price / Vickrey** | Theory: truthful bidding, milder curse | The auctioneer controls the losing bid that sets the price — a shill objection carriers raise instantly; unused in US freight |
| **Hybrid assign-then-auction** | Committed volume to reliable carriers, spot overflow auctions — mirrors US contract-plus-spot practice | Two mechanisms; the auction inherits the hardest loads |
| **Instant-book at a posted rate** | No latency; load-board UX; works in thin markets | No competition — abandons the premise |

**What this adds over what exists.** DAT and Truckstop already do price discovery — by posting and
negotiation, not competitive award, with no auditable selection record; digital brokers post a
take-it-or-leave-it rate. An auction adds three things: **tension on a single load, not a posted
rate**, **a defensible record of why this carrier was selected** (post-*Montgomery*, plausibly its
most valuable output), and **a per-load price series the shipper owns**. It subtracts their
advantage: **immediacy.** `[ASSUMPTION: shippers will trade latency for price and
record | conf: low — the premise the business rests on → A10.]` The best-funded attempt at digital
freight brokerage here shut down in 2023 (classification.md).

---

## 4.8 Metrics, assumptions, dependencies

| ID | Item |
|---|---|
| **KPI-301** | Bids per auction; share with 0, 1, 2+ — tension floor → OBJ-001 |
| **KPI-302** | Award-to-acceptance and lapse rates → OBJ-002 |
| **KPI-303** | Re-trade rate: settled ≠ awarded, plus magnitude → OBJ-001/005 |
| **KPI-304** | Coverage-failure rate: auctions ending `FAILED_*` → OBJ-002 |
| **KPI-305** | Auction-open to accepted-award time → OBJ-002 |
| **KPI-306** | Share of awards where the winner was not lowest → OBJ-006 |
| **ASM-301** | Enough eligible carriers per lane bid to make competition real `[conf: low]` — see KPI-301 |
| **ASM-302** | Carriers treat a bid as binding without deposit `[conf: low]` |
| **ASM-303** | A shipper can state a ceiling price `[conf: med]` |
| **ASM-304** | FMCSA data current enough at bid time to gate on `[conf: med]` → A2 |
| **DEP-301** | A2's gate callable per-load, per-bidder, at award |
| **DEP-302** | A6 honours the awarded bid as rate-confirmation price; rejects unrecorded changes |
| **DEP-303** | A8's carrier record accepts re-trade, decline, lapse |
| **DEP-304** | A7 rules on the antitrust posture of DEC-302/303 pre-launch |

---

## 4.9 Edge case register

| ID | Trigger | What happens | Decides | Unresolved |
|---|---|---|---|---|
| EC-301 | Zero bids at close | `FAILED_NO_BIDS`; DEC-310 | Shipper/ops | Auto re-auction? |
| EC-302 | Pool empty at open | Never opens | A2/ops | Told why? |
| EC-303 | Pool empties mid-auction (insurance lapse) | Ineligible bids voided | Platform | Told now or at close |
| EC-304 | Exactly one bid | §4.5 | DEC-310 | Open |
| EC-305 | All bids above ceiling | `FAILED_ALL_ABOVE_LIMIT` | Shipper | Accept above it? |
| EC-306 | Exact tie at lowest price | BR-305 | Rule | Which order |
| EC-307 | Tie, one bidder worse on safety | Tie-break decides — §4.1 in miniature | Rule | Safety tie-break? |
| EC-308 | Winner declines | → DEC-309 | Platform | Cascade vs re-auction; penalty → A8 |
| EC-309 | Winner never responds | `AWARD_LAPSED` | Automatic | Window length |
| EC-310 | Winner accepts then no-shows | → `CARRIER_NO_SHOW` (A4) | A4/A8 | Re-auction or desk |
| EC-311 | Bid withdrawn pre-close | BR-308 | Policy | Permitted? |
| EC-312 | Withdrawn post-close, pre-award | Treated as decline | Platform | Distinct from EC-308? |
| EC-313 | Close overnight / weekend / holiday | DEC-312 | Ops calendar | Supervised hours |
| EC-314 | Acceptance window spans a weekend | Lapses unwatched | DEC-312 | Clocks pause? |
| EC-315 | Shipper cancels mid-auction | `CANCELLED`; bidders told | Shipper (A1) | Compensating capacity |
| EC-316 | Load changed mid-auction (weight, equipment, appointment) | Bids priced against other freight | Platform | Re-auction vs re-bid |
| EC-317 | Two bids at one instant | Deterministic ordering needed | Platform | Granularity |
| EC-318 | Bid below plausible cost | Curse, error or fraud (RSK-305) | Platform | Flag: block or warn |
| EC-319 | Winner holds broker authority, not asset | BR-313; double-broker risk | Shipper/A2 | Broker bidding allowed? |
| EC-320 | Authority/insurance lapses pre-award | `AWARD_VOIDED_INELIGIBLE` | Automatic | Cascade or re-auction |
| EC-321 | Bidders share common ownership | BR-316 rejects second | Platform | Detection is A2's |
| EC-322 | One bidder wins a lane at falling margin | Curse accumulates, failures cluster | Ops | Concentration signal? |
| EC-323 | Rotation pattern on a repeat lane | BR-315 flag → A7 | Ops/counsel | Duty on detection |
| EC-324 | Carrier demands more at pickup | BR-310: recorded, or unpayable | Shipper | Who approves, limit |
| EC-325 | Shipper refuses the lowest qualified bidder | DEC-307 | Boss | Highest-consequence fork |
| EC-326 | Ceiling below plausible market rate | Fails every time | Shipper | Warn on publish |
| EC-327 | Repeated re-auctions, no bids | Freight ages against its appointment | Ops | Cap before escalation |
| EC-328 | Extension chain pushes close past lead time | Award too late | Platform | Hard stop |
| EC-329 | Bidder churns bids to probe the standing best | Information without commitment | Platform | Rate-limited? |
| EC-330 | Needs an endorsement/permit no bidder holds | Pool empty for a fixable reason | A2/shipper | Reason surfaced? |

---

**A3 limits.** Four things need a person in the room, not analysis: how stringent the §4.1 gate must
be to satisfy the client's insurer post-*Montgomery* (counsel + underwriter); whether shipper
discretion at award suits that insurer (DEC-307); realistic duration against real pickup lead times
(DEC-304 — a shipper); whether carriers bid against a binding rule with no deposit (ASM-302).
