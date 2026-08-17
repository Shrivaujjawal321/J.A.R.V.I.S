# R4 — Economics under DEC-LOCK-003: the platform is the broker

**Revises** `part-A10-problem-business-model.md` §3.5, §3.7, §15, phasing, strategic risks.
**Governed by** `DEC-LOCK-003` (platform is the broker, earns a spread) · `DEC-LOCK-001` · `DEC-LOCK-002`.
**Anti-fabrication holds.** Every model input stays `[NEEDS INPUT]`; any arithmetic is arithmetic on a
*cited* figure and labelled. IDs stay in the 1000-1099 block.

---

## 0. Correction against DEC-LOCK-003's bond figure — read before budgeting

`DEC-LOCK-003` states the bond as **"$150,000 (doubled from $75k, full amount mid-2026)."** I checked it
because it is a hard pre-launch cash cost. **It is not supported by the regulation.** The requirement is
**$75,000** (49 CFR § 387.307, [Cornell LII](https://www.law.cornell.edu/cfr/text/49/387.307)). What took
effect 16 Jan 2026 is the *Financial Responsibility* rule's compliance provisions — assets readily
available, immediate-suspension mechanics, eligible BMC-85 trustees — **not an increase in the amount**
([FMCSA](https://www.fmcsa.dot.gov/registration/broker-and-freight-forwarder-financial-responsibility-rule-overview-and-compliance),
[Fed. Reg. 2023-25312](https://www.federalregister.gov/documents/2023/11/16/2023-25312/broker-and-freight-forwarder-financial-responsibility)).
$150,000 is **unverified** — it traces to trade-blog reporting and OOIDA's *comment position*, not a rule.
What is genuinely pending is a **late-Feb-2026 ANPRM floating $75k → $100k**, which commits the agency to
nothing ([summary](https://www.carolinaexpressways.com/knowledge/news/fmcsa-broker-bond-increase-anprm)).

**Consequence.** Budget **$75,000, sensitivity $100,000** — and treat the real 2026 change as the
*suspension mechanic*: a drawdown below the minimum can suspend authority on a short cure window. Not a
cost line, a **single point of failure on the right to trade** — inside a business whose bond is drawn
against by carrier non-payment claims. `RSK-1011` revised below.

---

## 1. The revenue model is a spread `[REVISED — replaces A10 §3.7]`

Principal on both sides: the platform sells transportation to the shipper, buys it from the carrier.

```
GM_load  = P_shipper − C_carrier                     gross margin, dollars
m        = GM_load / P_shipper                       gross margin, percent
CM_load  = GM_load − c_ops − c_risk − c_capital − c_payment − c_baddebt
```

`c_baddebt` is **new** and exists only because of this decision: the carrier is owed whether or not the
shipper pays.

**The ceiling, and why an entrant sits below it.** CHR NAST adjusted gross profit margin 14.6% FY25;
RXO brokerage 13.3%→14.8% across 2025 ([CHR](https://investor.chrobinson.com/News-and-Events/Press-Releases/press-release-details/2026/C-H--Robinson-Reports-2025-Fourth-Quarter-Results/default.aspx),
[RXO](https://www.sec.gov/Archives/edgar/data/1929561/000192956125000078/rxo2025q1pressrelease.htm)) — scaled
incumbents with density, contract books, amortised back offices. Therefore:

```
m_realisable = m_incumbent − d_shipper − d_carrier          both d [NEEDS INPUT]
```

**This is the heart of the revision.** The intake's wedge is *price*, which is `d_shipper > 0` by
construction. And `DEC-LOCK-001`'s gate removes the cheapest tail of supply, raising `C_carrier`. **The
mechanism compresses the spread from both ends at once.** A licence business can sell cheap software at
a healthy software margin. A spread business selling cheap freight has nothing left.

**Recognition trap.** Gross vs net presentation needs an accountant `[verify]`. As principal, revenue may
present at `P_shipper` — making the business look ~7× its own gross margin and every downstream ratio
flattering and wrong. **Rule for this BRD: economics per gross-margin dollar, never per revenue dollar.**

## 2. This is now a financed business `[NEW]`

The platform pays the carrier before the shipper pays it. That gap is a balance sheet.

```
G         = days(carrier paid) → days(shipper collected)      [NEEDS INPUT]
Float     = (V_monthly / 30) × C̄_carrier × G                  cash permanently tied up
ΔFloat    = (ΔV_monthly / 30) × C̄_carrier × G                 cash consumed per unit of growth
c_capital = C̄_carrier × r × G / 365                           per-load funding cost, r [NEEDS INPUT]
```

**Why it grows with success.** Float is linear in volume. Each load advances 100% of the carrier rate and
returns only `m` of the sell rate, so growth *consumes* cash; the business self-funds only once retained
gross margin exceeds `ΔFloat`. Volume is not the relief — it is the constraint.

**How much margin the gap eats:** `c_capital / GM = ((1 − m) × G × r) / (360 × m)`. At `m = 0.14` — the
CHR/RXO band above, arithmetic on a cited figure — that reduces to **≈ 0.017 × G × r**. A 30-day gap
costs ~0.51·r of gross margin; a 60-day gap at a 20% facility rate costs **~20% of every gross-margin
dollar**, before ops, risk or bad debt. Inputs unknown; the coefficient is not negotiable.

**The variables the business now hinges on** — replacing A10 §3.7's three:

| Variable | Changed by DEC-LOCK-003? |
|---|---|
| **`G`** — payment-terms gap | **NEW.** Did not exist in a licence model. Converts volume into a capital requirement. |
| **`m_realisable`** — spread after both-side concessions | **CHANGED.** Was "what fee can we charge"; now "what spread can we defend against CHR/RXO/TQL while discounting to win." |
| **`c_ops` per load** | **Unchanged as hinge, worse in content.** Part 371 records, NOA handling, W-9/1099, claims are now compulsory back office. Already the category's real killer (`RSK-1005`). |
| **`c_baddebt`** | **NEW**, and dangerous because invisible in revenue terms: at `m = 0.14`, 1% bad debt *on revenue* destroys **~7% of gross margin**. |

## 3. Strategic risks, re-scored

| ID | Risk | Was | Now | Reasoning |
|---|---|---|---|---|
| `RSK-1003` **[REVISED]** | Disintermediation | 16 | **9** | **Genuinely better.** The shipper never sees `C_carrier`, the carrier never sees `P_shipper` — the spread is undisclosed, not clause-protected. The carrier's receivable, and its factor's claim, run against the platform. Going direct means re-papering, re-vetting, taking claims exposure, losing terms. Residual: the pair still meets at the dock. |
| `RSK-1008` **[REVISED]** | Capital intensity | 15 | **20** | **Clearly worse, now near-certain.** §2 makes it structural, plus dependence on a lender who tightens in exactly the market where the facility is needed. |
| `RSK-1002` **[REVISED]** | Negligent-selection tail post-*Montgomery* | 15 | **20** | The platform is no longer *near* the selection — it **is** the broker who chose. Probability of being named rises even where liability fails. `DEC-LOCK-001`'s gate and the selection record become the defence, not good practice. |
| `RSK-1009` **[REVISED]** | Freight-cycle exposure | 16 | **16, re-characterised** | A licence business is cycle-*sensitive*; a spread business is cycle-*positioned*. **On every load sold forward at a fixed rate the broker is short the spot market** — tightening lifts the buy side against a lagging sell price and the principal absorbs it. Cited direction is adverse: Cass TL linehaul +5.6% YoY Apr 2026, spot ~+25% ([FreightWaves](https://www.freightwaves.com/news/the-great-freight-recession-is-officially-over)). Collapse widens the spread but raises shipper insolvency — the risks swap, they do not cancel. |
| `RSK-1010` **[CLOSED]** | No broker authority | 15 | — | Answered. |
| `RSK-1011` **[REVISED]** | Regulatory cost step-up | 9 | **9, restated** | $75k, sensitivity $100k (§0); risk re-pointed at the suspension mechanic. |
| `RSK-1014` **[NEW]** | **Shipper credit / bad debt** — carrier paid regardless | — | **16** | Exists only as principal (`EC-601`). Credit limits per shipper *before* volume. |
| `RSK-1015` **[NEW]** | Double-pay on factored receivables | — | **12** | A6 `BR-606`/`BR-608` become Must-at-launch; undisclosed factoring (`EC-609`) is the hole. |
| `RSK-1016` **[NEW]** | Facility withdrawal / covenant breach | — | **12** | This, not "bad product," is how financed intermediaries die. |
| `RSK-1017` **[NEW]** | Vanity gross revenue mis-pricing spend | — | **9** | §1 reporting rule. |
| `RSK-1013` **[REVISED]** | Predecessor risk | 12 | **16** | Now *inside* the category that failed (§4). |

`ASM-1004` **[CLOSED]** · `ASM-1003` **[REVISED]** med→high (a ceiling on a spread, not a fee estimate) ·
`EC-1011` **[CLOSED]** · `EC-1007` **[REVISED]** factoring is core handling · `EC-601` **[ESCALATED]**.

## 4. The comparison set changed — to the worst one available `[NEW]`

Not load boards on price discovery. **A digital freight brokerage.** The category record:

- **Convoy** — ~$1.1B raised, ~$3.8B peak valuation, shut Oct 2023, no buyer ([CNBC](https://www.cnbc.com/2023/10/19/bezos-backed-freight-firm-convoy-shuts-down-read-ceo-memo-here.html), [Forbes](https://www.forbes.com/sites/tylerroush/2023/10/19/convoy-trucking-startup-backed-by-bezos-and-gates-shutting-down-after-failing-to-find-buyer-report-says/)).
- **Transfix** — SPAC of up to $375M cancelled Oct 2022; later **sold the brokerage to NFI and kept the
  software** ([DC Velocity](https://www.dcvelocity.com/articles/55721-freight-matching-platform-transfix-cancels-plans-to-go-public)). Note the direction: the survivor chose to *stop* being the broker.
- **Uber Freight** — breakeven adjusted EBITDA only in Q4 2025, first in 3+ years, on operational
  discipline not price, with revenue per load falling ([FY25 10-K](https://www.sec.gov/Archives/edgar/data/1543151/000154315126000015/uber-20251231.htm), [FreightWaves](https://www.freightwaves.com/news/uber-freight-posts-flat-q4-results-as-broader-platform-posts-record-profits)).

**Plainly: the best-funded attempt at this exact business lost, and the best-capitalised survivor took
years to reach zero.** Boss is not capital-competitive with any of them, so the Convoy playbook — buy
share, subsidise loads, out-scale to margin — **is not available** and must not be silently assumed.

Constraints, not hopes, for this to differ: **(1) no price wedge** — `d_shipper > 0` is the failed
strategy, and Convoy's own algorithm never awarded on price alone ([FreightWaves 2019](https://www.freightwaves.com/news/convoy-launches-automated-bidding-forcarriers)); **(2) narrow
scope by design**, lane- or vertical-dense, never national (`ASM-1002`); **(3) a capital plan that does
not need float to grow** (`DEC-1001`); **(4) `c_ops` structurally below incumbent cost-to-serve**,
evidenced by A9's time study, not asserted because it is software.

## 5. What being the broker genuinely buys `[NEW]`

1. **Control of the transaction** — both contracts, the sell price, the rate confirmation, the invoice,
   the claim. No match-and-fee model gives this.
2. **The ability to guarantee coverage** — a principal can re-cover a failed load at its own cost and
   still deliver; a vendor can only send a notification. **A sellable promise**, and the one thing a
   shipper cannot buy from a load board at $45–$199/month.
3. **Margin capture** — 13–16% of a load's rate is an order of magnitude above a seat subscription (both
   cited). Revenue per relationship is not comparable.
4. **The relationship holds** — price opacity + payment terms + claims history is a real switching cost,
   the honest basis for the `RSK-1003` downgrade.

**Honest read: conditionally yes, and the condition is not technological.** Worth it if the platform can
(a) name a non-price reason a shipper switches, (b) reach density enough to amortise a fixed compliance
and insurance base, and (c) avoid funding float from equity. Fail (a) and you have bought a bond, an
insurance programme, an unbounded tort tail and a receivables book in order to earn a *discounted* spread
on freight won by being cheap — strictly worse than selling software. **The decision does not create
value; it creates the capacity to capture value that must still be earned elsewhere.**

## 6. Phasing `[REVISED]` — Q2 now carries more weight, not less

**P0 does not change — it matters more.** What changed is the cost of being wrong: previously a wrong
premise wasted code; now, by the time you find out, you have posted a bond, bought contingent cargo and
auto-liability cover, appointed process agents and financed float. **Q2 is the most expensive unanswered
question in the document**, because `DEC-LOCK-003` settles the legal shape and says nothing about why a
shipper leaves CHR, RXO or TQL for an unknown broker with no record. The framing is now harsher: **we are
asking a shipper to swap a known broker for a new broker**, not to adopt a new category of tool. On A10's
own W4 finding, price discovery is already sold cheaply. **If Q2 comes back "price," this should not be
built as a brokerage.**

| Phase | Must prove now | Kill criterion |
|---|---|---|
| **P0 Premise** (no build) | One named shipper states what it does today, what it costs, what it would switch for | Answer is "price" ⇒ re-scope or stop |
| **P0b Capital & counterparty** (no build) `[NEW]` | Bond quoted; contingent cargo + auto-liability quoted; `G` taken from a real shipper contract; facility term sheet **or** `DEC-1001` = "carriers factor, we do not advance" | Cover unobtainable, or float unfundable at any `r` ⇒ stop before code |
| **P1 One load, end to end** `[REVISED]` | Positive `GM_load`, carrier paid, shipper collected, selection record that survives a *Montgomery* reading. **Coverage and cash before density** | Cannot clear one load at positive `CM` |
| **P2–P4** | As A10's phasing, with one change: **P3 must now clear `CM > 0` net of `c_capital` and `c_baddebt`**, not just `c_ops` | unchanged |

**`DEC-1001` [NEW — needs Boss + client]. Does the platform advance carrier payment, or do carriers
factor their own receivable?** The largest capital lever in the business. Advancing buys loyalty and
quick-pay margin; not advancing keeps `Float ≈ 0` and makes growth self-funding. A6 §6 framed three
options; under `DEC-LOCK-003` this decides whether the company is capital-light or capital-heavy.

## 7. KPIs `[REVISED]` — a spread business

| ID | Metric | Target | Status |
|---|---|---|---|
| `KPI-1010` | **`CM` per load** after `c_ops`, `c_risk`, `c_capital`, `c_payment`, `c_baddebt` | > 0 before scaling spend | [REVISED] |
| `KPI-1014` | **`m` per load** and GM dollars per load, against the cited 13–16% incumbent band | `[NEEDS INPUT]` | [NEW] |
| **`KPI-1015` ⚖** | **Margin give-back ratio** — GM dollars surrendered as re-cover cost, TONU, detention, service credits, claims ÷ GM dollars earned. **Counter-metric on margin capture: if `KPI-1014` rises while this rises, the spread was borrowed from reliability, not earned** | `[NEEDS INPUT]` | [NEW] |
| `KPI-1016` | **Working-capital health** — actual `G` (DSO_shipper − DPO_carrier), float outstanding $, **headroom vs facility limit** | `G` ≤ plan | [NEW] |
| **`KPI-1017` ⚖** | **Bad debt as % of gross-margin dollars** — never % of revenue, which hides it ~7× | `[NEEDS INPUT]` | [NEW] |
| `KPI-1018` | **Mis-remit / double-pay events on factored receivables** | **0** | [NEW] |
| `KPI-1004` | Two-sided benchmark: `P_shipper` **and** `C_carrier`, each vs lane index | `[NEEDS INPUT]` | [REVISED] |
| `KPI-1013` | CAC payback months on **GM dollars net of `c_capital`** | `[NEEDS INPUT]` | [REVISED] |
| `KPI-1001`–`1003`, `1005`–`1009`, `1011`, `1012` | Density, coverage, time-to-cover, on-time ⚖, no-show ⚖, claims ⚖, carrier safety ⚖, fraud ⚖, `c_ops`, leakage | per A10 §15 | [unchanged] |

**If `KPI-1014` improves while `KPI-1005`–`1009`, `1015` or `1017` degrade, the business is harvesting
its own future.**

---
*R4 — economics under DEC-LOCK-003. IDs 1000-1099. Does not own auction parameters (A3), the safety
floor (A2/DEC-201), settlement mechanics (A6) or insurance programme design (A8).*
