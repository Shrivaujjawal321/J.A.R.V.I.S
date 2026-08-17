# Part A10 — Problem Statement, US Market, Business Model, KPIs, Strategic Risk

**Owns:** §3 problem & Five Whys · US market context · §2 objectives (wording only) · unit-economics *structure* · liquidity/cold-start · §15 KPIs · strategic risks · phasing. A1–A9's operational requirements are referenced, not written.

**Anti-fabrication.** Every figure is cited. Boss supplied no volume or rate data, so **no unit-economics number appears here** — only equations with `[NEEDS INPUT]` variables, and no TAM (vendor market-size estimates diverge sharply).

---

## 3. Problem Statement

Boss supplied a **mechanism**, not a pain (intake, "NOT supplied"). This ladder marks — rather than fills — the unknown rungs. **Not decided here:** whether the client holds broker authority (spine §0); the mechanism (A3); pricing/settlement (A6).

### 3.1 Five Whys

| # | Question | Answer | Status |
|---|---|---|---|
| W1 | Why auction a load at all? | Because on some loads the shipper cannot get a truck at an acceptable price, or search effort is high. | **UNKNOWN here.** No shipper, lane or current method supplied. `[NEEDS INPUT: which shipper, which lanes, failing how — covered how today?]` |
| W2 | Why does the routing guide fail? | Contract carriers reject tenders when spot pays better. US tender rejections are at their highest since 2022; spot linehaul passed contract for the first time since 2021 ([Trucking Dive](https://www.truckingdive.com/news/trucking-spot-contract-rates-us-bank-dat-2026-spread/816351/), [FreightWaves](https://www.freightwaves.com/news/contract-premium-shrinks-as-truckload-market-reprices-higher)). | KNOWN market-wide; unverified here |
| W3 | Why is spot capacity scarce now? | Capacity exited: for-hire carriers ~241,000 (Jun 2020) → 475,000+ (Jul 2023); 100,000+ authorities revoked/deactivated 2023–24; net revocations +16% H1-2025 vs H1-2024 ([Tank Transport](https://tanktransport.com/2025/08/great-freight-recession-2025/), [Trucking Dive](https://www.truckingdive.com/news/fmcsa-grants-reinstatements-revocations-operating-authority-2025-data/808968/)). | KNOWN |
| W4 | Why hasn't price discovery solved it? | **It largely has.** DAT and Truckstop dominate US spot discovery and already sell lane rate analytics and instant booking ([comparison](https://truckdispatchexperts.com/resources/dat-vs-truckstop-load-boards/)); reverse-auction procurement exists (Emerge, Sleek). Residual pain is **not "I don't know the price"** — it is coverage certainty, vetting, admin. | KNOWN — undercuts the stated wedge |
| W5 | So why does anyone still lose money? | Unconfirmed: (a) vetting a stranger carrier is slow and legally hazardous; (b) fraud makes cheap capacity unusable; (c) the shipper's back office (tender → rate con → BOL → invoice → claim) is manual; (d) small shippers have no broker relationship. **Which applies decides whether this is an auction, a vetting, or a back-office product.** | **UNKNOWN — the largest gap in the document.** `[NEEDS INPUT: which of (a)–(d)?]` |

**Cost of inaction — directional.** US/Canada cargo-theft losses est. ~$725M in 2025, +60% on ~$455M in 2024, over 2,646 incidents ([Insurance Business](https://www.insurancebusinessmag.com/us/news/programs/cargo-fraud-is-generating-claims-not-just-stolen-goods--amwins-restructures-around-that-shift-583200.aspx)). TIA has estimated double-brokering at ~$700M–$1B/yr; FMCSA complaints rose ~2,000 (2021) → 8,000+ (2025) ([Truck Dispatch Experts](https://truckdispatchexperts.com/resources/broker-fraud-crackdown-2026/)). **A trust problem before a price problem.**

### 3.2 US market and competitive context

| Fact | Source |
|---|---|
| Best-funded attempt failed: Convoy raised ~$1.1B, valued ~$3.8B, shut Oct 2023 with no buyer. Post-mortem: no physical stickiness (no trailers, drop network, exclusive capacity); share bought with unattractive freight | [CNBC](https://www.cnbc.com/2023/10/19/bezos-backed-freight-firm-convoy-shuts-down-read-ceo-memo-here.html) · [Forbes](https://www.forbes.com/sites/tylerroush/2023/10/19/convoy-trucking-startup-backed-by-bezos-and-gates-shutting-down-after-failing-to-find-buyer-report-says/) · [Truckstop](https://truckstop.com/blog/when-convoy-collapsed-it-caused-a-ripple-effect-in-the-transportation-industry-find-out-what-happened-and-what-it-means-for-the-future/) |
| **Convoy's own auction was never price-only** — bids scored on carrier quality score *and* price; "not just about having the lowest price" | [FreightWaves 2019](https://www.freightwaves.com/news/convoy-launches-automated-bidding-forcarriers) |
| Transfix killed its SPAC (up to $375M) Oct 2022, cut staff, sold the brokerage to NFI, kept software | [DC Velocity](https://www.dcvelocity.com/articles/55721-freight-matching-platform-transfix-cancels-plans-to-go-public) · [S&P](https://www.spglobal.com/market-intelligence/en/news-insights/research/transfix-sale-highlights-vcs-uneasy-fit-with-freight-brokerage) |
| Best-capitalised survivor barely breaks even: Uber Freight ~breakeven Adj. EBITDA 2025, first in 3+ years; revenue/load down | [Uber FY25 10-K](https://www.sec.gov/Archives/edgar/data/1543151/000154315126000015/uber-20251231.htm) |
| Incumbent margin caps any take rate: CHR NAST adj. gross profit margin 14.6% (FY25); RXO brokerage 13.3%→14.8% across 2025 (15.5% Q4-24) | [CHR Q4-25](https://investor.chrobinson.com/News-and-Events/Press-Releases/press-release-details/2026/C-H--Robinson-Reports-2025-Fourth-Quarter-Results/default.aspx) · [RXO 8-K](https://www.sec.gov/Archives/edgar/data/1929561/000192956125000078/rxo2025q1pressrelease.htm) |
| Load boards monetise by **subscription** (~$45–$199/mo), not take rate; top 8–10 brokerages hold >⅓ of gross revenues | [comparison](https://truckdispatchexperts.com/resources/dat-vs-truckstop-load-boards/) · [A&A](https://www.freightcaviar.com/a-as-top-10-freight-brokerages-and-the-state-of-the-industry-in-2025/) |
| **Cycle has turned:** Cass TL linehaul +5.6% YoY (Apr 2026), spot ~+25% YoY. Tightening is *harder* for lowest-bid — carriers gain pricing power | [FreightWaves](https://www.freightwaves.com/news/the-great-freight-recession-is-officially-over) · [Ubico](https://www.ubico.io/post/is-the-freight-recession-over-2026) |

### 3.3 The legal fact that post-dates the intake framing

On **14 May 2026** the Supreme Court decided **Montgomery v. Caribe Transport II, LLC**, holding unanimously that the FAAAA safety exception preserves **state negligent-selection claims against brokers in all 50 states**, ending the preemption defence ([FreightWaves](https://www.freightwaves.com/news/the-supreme-court-just-told-every-freight-broker-that-they-can-be-sued), [Duane Morris](https://www.duanemorris.com/alerts/us_supreme_court_agrees_address_preemption_freight_broker_negligence_claims_1025.html), [Cornell LII 24-1238](https://www.law.cornell.edu/supremecourt/text/24-1238)). Reported guidance: *"If a broker has no documented carrier vetting process, that absence is itself evidence."*

A7/A8 own the legal treatment. A10's narrower point: an award rule documented as *"lowest bid wins"* is a discoverable record that price, not safety, chose the carrier — turning a design preference into a **balance-sheet item** whose tail is unbounded against one load's margin.

### 3.4 Why a pure lowest-bid auction may be the wrong wedge

A risk for Boss to answer, not a verdict.

1. **Price is already discovered** (W4) — a lower number alone sells against a subscription-priced substitute.
2. **It commoditises the wrong attribute** — the shipper's loss is dominated by *did the truck show, arrive intact, claim-free*, not the last 3% of linehaul. Convoy, which held the data, scored quality alongside price.
3. **It selects adversely** — the lowest bidder skews to whoever underestimated cost, will re-trade at pickup, or is not the carrier at all (double brokering: 4× complaint growth since 2021). And it is counter-cyclical: in a tightening market the marginal carrier does not need a cheap load (RSK-1009).
4. **Neither side gains a reason to stay** (§3.5).

**Steel-man:** price-only is unambiguous, un-gameable by staff, cheap to run, legible to a small carrier. **Lowest-bid-among-a-hard-qualified-pool** keeps nearly all of that and drops the negligent-selection fact pattern. A3 owns the options.

### 3.5 Disintermediation — the standard leak, not a hypothesis

Trading contacts on load #1 and booking load #2 direct is ordinary in US truckload. Something other than the match must hold it:

| Hold | Mechanism | Cost |
|---|---|---|
| Money | Pay carrier faster than shipper pays platform | Working capital (A6) |
| Risk transfer | Platform carries claim + fraud loss | Insurance, reserves, the *Montgomery* tail |
| Vetting-as-service | Continuous FMCSA/insurance monitoring | Ops cost (A2/A9) |
| Volume | Aggregated flow no single shipper can offer | Needs liquidity first — circular |
| Contract | Non-circumvention clause | Weak, costly, hostile to enforce |

`[NEEDS INPUT: which hold will the client fund? If none, leakage is the base case, not a risk.]`

### 3.6 Cold start, concretely

Loop: no vetted carriers → thin bids → bad price/coverage → shippers leave → no loads → carriers leave. Worse in a reverse auction: a thin auction does not merely underperform, it produces a **visibly bad price and a public failure state**.

- **Seed carriers first** — loads are worthless without bidders, and carrier acquisition is cheap next to enterprise shipper acquisition `[ASSUMPTION: carrier-first seeding | conf: med]`
- **Seed lane-dense, not national** — liquidity is per-lane-per-day; a national launch at the same carrier count yields zero density everywhere
- **Seed cost / kill signal:** subsidy/load × loads until density ≥ n\*; density unreached inside budget ⇒ mechanism refuted for that lane class `[NEEDS INPUT: n\*, the minimum bids per auction below which the client deems an auction failed]`

### 3.7 Unit economics — structure only

`CM = (P_shipper − C_carrier) − c_ops − c_risk − c_capital − c_payment`

| Variable | Meaning | Owner of the real number |
|---|---|---|
| `P_shipper` / `C_carrier` | Price charged / winning bid paid | `[NEEDS INPUT]` — A6 / A3 |
| `t` = take rate = `(P_shipper − C_carrier)/P_shipper` | Capped by incumbent gross margin (13.3–14.8%, §3.2) | `[NEEDS INPUT]` |
| `c_ops` | `exception_rate × handling_minutes × loaded_labour_rate` | **A9** |
| `c_risk` | `Σ (p_i × L_i)` over claim, fraud, no-show, negligent-selection tail | **A8** |
| `c_capital` | `C_carrier × r × days_pay_gap / 365` | **A6** |
| `c_payment` | Processing, factoring/NOA handling, 1099 admin | **A6** |

`LTV_side = CM × loads_per_period × periods_retained` · `Payback = CAC_side ÷ (CM × loads_per_month)` · `Effective_CAC = (CAC_shipper + CAC_carrier) ÷ loads_before_leakage`

**Three hinge variables:** (1) **`c_ops` at scale** — the category failed not on price but because cost-to-serve never fell far enough; if `c_ops` nears take-rate dollars, volume cannot fix it. (2) **`periods_retained` net of leakage** — set by §3.5. (3) **`c_risk` post-*Montgomery*** — a fat tail, not an average; one verdict is a solvency event.

---

## 2. Objectives — wording refined, IDs per spine §5

| ID | Refined objective (targets `[NEEDS INPUT]`) | Verification |
|---|---|---|
| OBJ-001 | Lower landed cost per load vs the shipper's current method, **without degrading on-time or claim performance below that method's baseline** | Pre-platform baseline, same lane |
| OBJ-002 | Cut elapsed time and human touches from "load ready" to "carrier committed" | `PUBLISHED` → `AWARD_ACCEPTED`; touch sampling |
| OBJ-003 | Give carriers load flow they cannot reach today | Awards to carriers with no prior tie to the shipper |
| OBJ-004 | Make every delivery provable in a form that survives a Carmack claim | % loads with signed BOL, clear-or-exception (A5) |
| OBJ-005 | Right invoice, right party, right reporting, on time — including factored receivables | Invoice exception + on-time settlement rate (A6) |
| OBJ-006 | Keep the platform trustworthy enough for strangers to move high-value freight under fraud pressure | Fraud events/1,000 loads `[NEEDS INPUT]` |
| OBJ-007 | Operate lawfully across brokerage, safety and privacy regimes, **with selection documented to a defensible standard** (*Montgomery*) | A7 audit; vetting record per award |

**Tension for Boss:** OBJ-001 (cheaper) and OBJ-004/006/007 (safer, provable, defensible) pull opposite ways under a price-only rule. They cannot all be Must.

## 15. KPIs

All baselines `[NEEDS INPUT]` — no operating history supplied. **⚖ = counter-metric.**

| ID | Metric | Target | Method | Owner | Traces |
|---|---|---|---|---|---|
| KPI-1001 | Bids per closed auction (density) | ≥ n\* `[NEEDS INPUT]` | Auction log | Ops | OBJ-003 |
| KPI-1002 | Coverage rate: published → award accepted | `[NEEDS INPUT]` | Lifecycle states | Ops | OBJ-002 |
| KPI-1003 | Time to cover (`PUBLISHED`→`AWARD_ACCEPTED`) | `[NEEDS INPUT]` | State timestamps | Ops | OBJ-002 |
| KPI-1004 | Award price vs external lane benchmark | `[NEEDS INPUT]` | Third-party rate index | Commercial | OBJ-001 |
| **KPI-1005 ⚖** | **On-time pickup + on-time delivery** | ≥ pre-platform baseline | POD/BOL timestamps (A5) | Ops | OBJ-001/004 |
| **KPI-1006 ⚖** | **No-show + award-decline + re-trade at pickup** | `[NEEDS INPUT]` | Lifecycle exception states | Ops | OBJ-001 |
| **KPI-1007 ⚖** | **Claims per 100 loads; claim $ per load** | `[NEEDS INPUT]` | Claims register (A8) | Risk | OBJ-004 |
| **KPI-1008 ⚖** | **Safety profile of awarded carriers** — FMCSA BASIC percentile / authority age | No award outside A2's floor | Vetting record | Compliance | OBJ-007 |
| **KPI-1009 ⚖** | **Double-brokering / identity-theft events per 1,000 loads** | `[NEEDS INPUT]` | Fraud register (A8) | Risk | OBJ-006 |
| KPI-1010 | Contribution margin per load (`CM`) | > 0 before scaling spend | Finance | Finance | OBJ-001 |
| KPI-1011 | `c_ops` per load and exception rate | Falling with volume | Ops time study (A9) | Ops | OBJ-002 |
| KPI-1012 | Repeat rate and **off-platform leakage** — pairs matched here whose next load goes elsewhere | `[NEEDS INPUT]` | Pair cohort | Commercial | OBJ-003 |
| KPI-1013 | CAC payback months, per side | `[NEEDS INPUT]` | Finance cohort | Finance | OBJ-003 |

**KPI-1005–1009 exist to catch the mechanism optimising price while destroying reliability and safety.** If KPI-1004 improves while any of them degrades, the mechanism is working as designed — and the design is wrong.

## Phasing — what Release 1 must *prove*

| Phase | Must prove | Kill criterion |
|---|---|---|
| **P0 Premise** (no build) | Named shippers have loads they fail to cover at acceptable price, and can say what they do today | Pain is admin/vetting, not price ⇒ re-scope |
| **P1 Liquidity**, one lane class | Density ≥ n\* from carriers passing A2's floor | Density unreachable inside budget |
| **P2 Fulfilment integrity** | KPI-1005/1006/1007/1009 ≥ incumbent baseline | Price wins, service loses ⇒ mechanism refuted |
| **P3 Unit economics** | `CM > 0` after real `c_ops` | Ops cost eats the take rate |
| **P4 Retention** | Repeat without leakage (KPI-1012) | Leakage caps LTV below CAC ⇒ a matcher, not a business |

Nothing beyond P1's lane class is built before P2 and P3 report.

## Strategic risks

| ID | Risk | Cat | P | I | Score | Owner | Mitigation |
|---|---|---|---|---|---|---|---|
| RSK-1001 | **Premise wrong** — pain is coverage/vetting/admin, not price; sells against a solved problem | Strategic | 4 | 5 | 20 | Sponsor | P0 gate; W5 answered by real shippers |
| RSK-1002 | **Negligent-selection tail post-*Montgomery*** — price-only award is plaintiff's evidence; one verdict exceeds cumulative margin | Legal | 3 | 5 | 15 | Sponsor + counsel | Lowest-bid-among-qualified (A3); A2 floor; vetting record |
| RSK-1003 | **Disintermediation** — parties go direct after first match; LTV collapses | Commercial | 4 | 4 | 16 | Commercial | Fund one hold (§3.5); KPI-1012 |
| RSK-1004 | **Cold start never reached** — liquidity spread thin; failed auctions poison both sides | Commercial | 4 | 4 | 16 | Commercial | Lane-dense seeding; failure state only after fallback (A3) |
| RSK-1005 | **Cost-to-serve doesn't fall** — `c_ops` flat with volume; the category's actual killer | Financial | 4 | 5 | 20 | Ops (A9) | KPI-1011; P3 kill gate |
| RSK-1006 | **Fraud loss exceeds margin** — double brokering, identity theft, fictitious pickup follow price-only award | Fraud | 4 | 5 | 20 | Risk (A8) | A2 floor; KPI-1009 |
| RSK-1007 | **Incumbent response** — load boards add auction at subscription price; CHR/RXO undercut off a 13–15% margin base | Competitive | 4 | 4 | 16 | Sponsor | Differentiate on a non-price hold |
| RSK-1008 | **Capital intensity** — paying carriers before shippers pay consumes working capital linearly with GMV | Financial | 3 | 5 | 15 | Finance (A6) | Model `c_capital`; cap float |
| RSK-1009 | **Freight-cycle exposure** — model conceived for a loose market; 2026 spot +25% YoY | Market | 4 | 4 | 16 | Sponsor | Stress-test tight-market case pre-launch |
| RSK-1010 | **No broker authority** — unlawful to arrange for compensation without it; decides take-rate vs SaaS | Regulatory | 3 | 5 | 15 | Sponsor (A7) | Resolve spine §0 first |
| RSK-1011 | **Regulatory cost step-up** — broker surety/trust minimum reported rising to $150,000 from Jul 2026 ([src](https://authenticate.com/resources/blog/fmcsa-rules-2025/)) | Regulatory | 3 | 3 | 9 | Finance | Fixed cost, not per-load; A7 confirms |
| RSK-1012 | **Antitrust surface** — repeat lowest-bid auctions on fixed lanes create a bid-rotation pattern (Sherman §1) | Legal | 2 | 4 | 8 | Counsel (A7) | Bid-pattern monitoring |
| RSK-1013 | **Predecessor risk ignored** — rebuilding what Convoy built with ~$1.1B, on less capital | Strategic | 3 | 4 | 12 | Sponsor | Written differentiation vs the three failures before P1 |

## Assumptions

| ID | Assumption | Conf | Impact if wrong |
|---|---|---|---|
| ASM-1001 | Carrier-first seeding is cheaper than shipper-first | med | Seeding budget misallocated |
| ASM-1002 | Liquidity is per-lane-per-day, never national | high | National launch yields zero density everywhere |
| ASM-1003 | Sustainable take rate is bounded by incumbent gross margins (13.3–14.8%) | med | Revenue model overstates margin |
| ASM-1004 | Client intends to intermediate, not license software | low | Model and regulatory surface both change (RSK-1010) |
| ASM-1005 | Loads are US domestic interstate truckload | med | Cross-border / intrastate / LTL change the economics |

## Edge cases — business-model level

| ID | Trigger | Consequence | Decides | Unresolved |
|---|---|---|---|---|
| EC-1001 | Auction closes with one bid | No discovery occurred; award is a negotiation with extra steps | A3 | Award, re-run, or manual cover? |
| EC-1002 | Winning bid below plausible lane cost | Winner's curse → no-show or re-trade | A3 / A2 | Is a reserve price acceptable? |
| EC-1003 | Same carrier wins every auction on a lane | Liquidity illusory; dependency + antitrust signal | Commercial | Concentration cap? `[NEEDS INPUT]` |
| EC-1004 | Pair meets here, next load moves off-platform | LTV collapse, invisible unless instrumented | Commercial | Measured, priced, or contracted against? |
| EC-1005 | Winner is a broker re-brokering | Double brokering; fraud + Carmack exposure | A2 / A8 | Is broker bidding permitted? `[NEEDS INPUT]` |
| EC-1006 | Serious accident, awarded carrier | Negligent-selection claim; the award rule is evidence | Counsel | Insurance + reserve `[NEEDS INPUT]` (A8) |
| EC-1007 | Carrier's receivable factored; NOA issued | Payment redirected; cash cycle shifts | A6 | `c_capital` effect unmodelled |
| EC-1008 | Market tightens; carriers stop bidding cheap | Auctions fail systemically, not individually | Sponsor | No tight-market case modelled |
| EC-1009 | Seeded lane hits density but never repeats | A one-shot matcher, not a marketplace | Commercial | P4 kill gate |
| EC-1010 | Shipper posts only routing-guide rejects | Adversely-selected load book — Convoy's error | Commercial | Load-mix policy `[NEEDS INPUT]` |
| EC-1011 | Client holds no broker authority | Becomes SaaS-to-licensed-brokers; take rate disappears | Sponsor | Blocking (RSK-1010) |

## What I cannot do from here

Three things need a human: (1) a named US shipper stating what it does today and what that costs — that alone closes W5; (2) a broker or carrier sanity-checking take rate, `c_ops`, leakage; (3) counsel on post-*Montgomery* selection standards and insurance. All of the above is **well-formed, not validated**.

---

> **CHALLENGE (spine §5, OBJ-001).** OBJ-001 makes cost reduction first-class while OBJ-004/006/007 make safety, provability and lawful selection first-class. Under a price-only rule these are not merely in tension: after *Montgomery v. Caribe Transport II* (14 May 2026), pursuing OBJ-001 via a documented lowest-bid rule manufactures evidence against OBJ-007. I added the constraint clause inline to OBJ-001 rather than diverging. **For Boss:** demote OBJ-001 below OBJ-006/007, or move the award rule to *lowest bid among a hard-qualified pool* (A3's options). Spine §4 called lowest-bid "a strong commitment with documented failure modes" — written before this ruling was in view. The legal weather has changed.
