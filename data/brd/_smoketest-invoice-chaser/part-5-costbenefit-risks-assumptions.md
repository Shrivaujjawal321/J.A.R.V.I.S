# BRD Part 5 — §11 Assumptions · §14 Risks · §17 Business Case

> **Assembly note.** Drafted in parallel with four sibling parts; sections in document order.
> Assumption IDs use the reserved **ASM-501+** block so siblings can use ASM-001+ without collision —
> renumber at merge. Risks use RSK-001+ (§14 is owned wholly by this part). The entire supplied input
> was one sentence; no market, pricing, cost or user figures exist, so §17 gives the arithmetic and
> names the missing inputs rather than inventing them.

---

## 11. Assumptions Register

**Consolidation point** — every `[ASSUMPTION]` tag anywhere in the BRD terminates here. Siblings were
drafted concurrently and their tags were not visible, so **rows below cover only §14 and §17**;
Jarvis merges the rest at assembly. A merged register shorter than the document's total inline tag
count is itself a defect.

**Owner note.** Solo initiative — Ujjawal owns every row. Accurate, but a single point of validation
failure, which is why most validation methods below require *external* evidence, not self-judgement.

| # | Assumption | Conf | Impact if wrong | Owner | Validation method | By |
|---|---|---|---|---|---|---|
| ASM-501 | **Non-payment is materially caused by inconsistent follow-up** — i.e. chasing changes the outcome. The intake named a solution, never a cause. | **low** | **Fatal** — if the real cause is client insolvency, disputed scope or absent written terms, uplift `U` (§17.3) → 0 and the case collapses regardless of execution. | Ujjawal | "Last 5 unpaid invoices" retrospective, ≥8 freelancers; record why each stalled. Survives only if follow-up failure is primary in a majority. | 2026-08-12 |
| ASM-502 | Segment is **India-first, INR, solo/micro operators** — no finance staff, no PO process. | med | Agencies or EU users change the compliance surface (GDPR joins DPDP), the buyer and the price band. | Ujjawal | Confirm with Boss; cross-check against channels he can actually reach. | 2026-08-05 |
| ASM-503 | The freelancer's clients are **businesses**, not consumers. | med | B2C receivables carry a different tone constraint, DPDP posture and escalation path; re-scopes RSK-006/007. | Ujjawal | Record client type per invoice in the ASM-501 interviews. | 2026-08-12 |
| ASM-504 | **Buyer = user**, own cash, no approval step. | high | Shortens the sales cycle but caps price at personal-discretionary level — the constraint behind RSK-003. | Ujjawal | Same interviews. | 2026-08-12 |
| ASM-505 | Monetization is a **recurring subscription**, not a success fee on recovered amounts. | med | High to the arithmetic: a success fee replaces §17.4's model with contingent revenue, largely dissolves RSK-003, and triggers RSK-009. The two cannot share one input set. | Ujjawal | Boss decision, informed by RSK-009. Required before §17 can carry numbers. | 2026-08-19 |
| ASM-506 | The offering **never takes custody of funds** and never touches card data. | high | Custody or card handling pulls in PCI-DSS and aggregator licensing — order-of-magnitude cost change, unsurvivable at this price point. | Ujjawal | Re-confirm whenever scope drifts from "pursue the payment" to "collect the payment". | Standing |
| ASM-507 | Micro-SMB buyers need a **visible value-to-price multiple**, not parity. Sets `k` in §17.3. | med | Practitioner wisdom, **not sourced here**. If k≈1 a far wider price band is viable; if k is high the category may be unpriceable. | Ujjawal | Price probe: state a price, record reaction, ask what recovered amount would justify it. | 2026-08-12 |
| ASM-508 | **LTV/CAC ≥ 3** is an appropriate viability gate. | low | A convention, not a law, and weak at micro price points where the ratio looks healthy while absolute contribution is trivial. Used as shape only. | Ujjawal | Replace with an absolute test (aggregate contribution vs fixed run cost + opportunity cost) once inputs exist. | 2026-09-02 |
| ASM-509 | Build cost is denominated principally in **Boss's time**, not cash. | med | Makes investment a judgement about foregone alternatives; if cash dominates, payback tightens. | Ujjawal | Boss states hourly opportunity value + honest build-hours; compare against cash lines. | 2026-08-19 |
| ASM-510 | Dates above assume start **2026-07-29**, Boss executing personally. | med | Low — slippage delays the go/no-go, changes no conclusion. | Ujjawal | Self-evident at first missed date. | Standing |

Run **ASM-501 first**: lowest confidence, the premise the other nine sit on, cheapest to test. If it
fails, §17 never needs completing.

---

## 14. Risk Register

P × I, each 1-5. ≥15 High · 8-14 Med · ≤7 Low. All `Open` — no mitigation has started, and recording
otherwise would be false. Generic delivery risks (scope creep, estimate overrun) are excluded
deliberately: they are not what a review of *this* initiative turns on.

| ID | Cat | Description | P | I | Score | Mitigation | Owner | Status | Links |
|---|---|---|---|---|---|---|---|---|---|
| RSK-001 | Competitive | **Feature, not a product.** Established invoicing/accounting products for this segment already bundle automated reminders; a standalone offering must beat a capability the buyer may already own and not pay extra for. | 4 | 4 | **16 H** | Audit the cohort's existing tools — do reminders exist, are they switched on, if not why not. Proceed only if a specific nameable gap survives; a "we'd do it better" claim does not count. | Ujjawal | Open | ASM-501 |
| RSK-002 | Adoption | **The buyer's fear is relational, not operational.** Freelancers often under-chase *by choice*, protecting a client they need repeat work from. Automating the chase then amplifies the thing they fear — adoption dies at first send, not at signup. | 4 | 4 | **16 H** | Ask directly what stopped them chasing last time. If the answer is social, re-frame the value proposition around removing the *social cost* of asking — cheap now, near-impossible after build. | Ujjawal | Open | ASM-501 |
| RSK-003 | Commercial | **Willingness to pay for a single-function tool.** Most price-sensitive segment in software, personal-discretionary spend, and single-function tools are first dropped and easiest for a suite to absorb. | 4 | 5 | **20 H** | Price-probe before build (ASM-507) and pre-commit a kill threshold: if median acceptable price sits below where §17.4's contribution clears fixed run cost at a reachable user count, stop. | Ujjawal | Open | ASM-505, ASM-507 |
| RSK-004 | Operational | **Chasing an already-paid invoice.** The proposition depends on truthful payment status; a wrong chase reaches the user's paying client and embarrasses the user in front of the person who pays them. Near-certain churn plus word-of-mouth cost. | 3 | 5 | **15 H** | Establish where payment truth comes from, and how stale it may be, as a business requirement before anything else is scoped. If no reliable source can be assumed, the need must be re-stated to keep the user in the loop before each outbound action — which changes the "automatically" in the intake. | Ujjawal | Open | ASM-501 |
| RSK-005 | Validity | **Root-cause misdiagnosis.** If non-payment is driven by client cash-flow failure, disputed deliverables or missing written terms, follow-up cadence is not the binding constraint and uplift is negligible. | 3 | 5 | **15 H** | ASM-501 restated as a risk; same retrospective, run before any build decision. Highest-leverage single action on this register. | Ujjawal | Open | ASM-501 |
| RSK-006 | Regulatory | **Regulated / rate-limited outreach channels.** Business-initiated messaging to Indian recipients sits under channel-specific consent and template regimes, and repetitive dunning content is precisely what deliverability filters target. | 3 | 3 | **9 M** | Confirm the regulatory position per intended channel before committing, and record channel availability as a §13 constraint. `[NEEDS INPUT: which outreach channels are acceptable — email only, or messaging/voice too? The compliance surface differs sharply per channel.]` | Ujjawal | Open | ASM-502 |
| RSK-007 | Compliance | **DPDP 2023 exposure via third-party data.** The offering processes personal data of the *user's clients* — people with no relationship to the platform. Freelancer is fiduciary, platform is processor; obligations arrive contractually and must surface in user-facing terms. | 3 | 4 | **12 M** | Fix the fiduciary/processor split and flow-down obligations as a §10 compliance requirement before any client data is collected. This exposure exists at zero revenue. | Ujjawal | Open | ASM-502, ASM-503 |
| RSK-008 | Distribution | **Distribution and acquisition cost.** A diffuse population with no concentrated buying channel; at a micro price point paid acquisition can exceed lifetime contribution, leaving only slow organic paths — which changes the venture's time horizon, not just its budget. | 4 | 4 | **16 H** | Name one concrete reachable concentration of the segment before build; treat "we'll find distribution later" as a rejected plan. | Ujjawal | Open | ASM-508 |
| RSK-009 | Positioning | **Drift toward debt collection.** Harder tone, third-party involvement or contingency pricing raise apparent efficacy while moving the offering into a regulated, reputationally sensitive activity. | 2 | 4 | **8 M** | Draw the line in §4 Out-of-Scope now, with a stated reason, rather than during a pricing discussion. Constrains the ASM-505 choice. | Ujjawal | Open | ASM-505 |

**The register's message:** the four highest scores (RSK-003 at 20; RSK-001/002/008 at 16) are all
**pre-build** risks. Each is answerable by talking to eight people for an hour, each can independently
kill the case, and **none is mitigated by building a better product.**

---

## 17. Cost-Benefit / Business Case

### 17.1 Why this section carries no figures

Market size, willingness to pay, build cost, run cost, CAC, retention and recovery uplift were all
absent from the intake and cannot be responsibly inferred. A fabricated rupee figure would be worse
than a blank — harder to challenge, looks like analysis, propagates downstream, and nobody remembers
it was invented. What follows is the **arithmetic, its driving variables, the specific input each one
needs, and the pre-committed decision rule**. Supply the inputs and this becomes a real business case
in one pass.

`[ASSUMPTION: a business case is warranted at all — that this is intended as a commercial venture rather than a personal-use tool or a portfolio artefact. The three have different viability tests and only one needs §17. | conf: med]`

### 17.2 Alternatives, including do-nothing

| Alt | Description |
|---|---|
| **A0 — Do nothing** | The correct default; the others must beat it. Its cost is not zero (unclaimed uplift), but nor is it obviously large — the size of that uplift is exactly the unknown (ASM-501). |
| **A1 — Standalone offering** | The intake as stated. Must beat A0 *and* survive RSK-001. |
| **A2 — Capability within a broader offering** | Same need, one part of a wider proposition, so willingness-to-pay is not carried by this function alone. Weakens RSK-001/003; raises scope and cost. |
| **A3 — Non-product intervention** | The need met without software (structured terms + disciplined manual cadence). Relevant because if ASM-501 is false, A3 and A1 produce the same outcome and A3 costs nothing. |

`[ASSUMPTION: A1 is under evaluation only because the intake named it; a solution was stated without a problem, so A1 has not been shown to be the right shape of response. | conf: low]`

**No recommendation yet, deliberately** — choosing between A1/A2/A3 needs one interview round.

### 17.3 Buyer-side value — will a freelancer pay?

```
V  =  (N × A × U)        recovery gain — value that would otherwise never arrive
   +  (N × A × D × r)    carry gain — value arriving sooner × cost of money
   +  (H × W)            time gain — hours no longer spent chasing, at their rate
```
Adoption condition: **`V ≥ k × P`**.

| Sym | Meaning | Status |
|---|---|---|
| `N` | Past-due invoices per user per month | `[NEEDS INPUT: monthly invoice count and past-due share]` |
| `A` | Average past-due invoice value | `[NEEDS INPUT: typical invoice value in segment]` |
| `U` | **Recovery uplift** (pp of at-risk value additionally recovered) | `[NEEDS INPUT: no credible source exists; only a measured before/after produces it. The most important unknown in this document.]` |
| `D` | Reduction in days-to-payment | `[NEEDS INPUT: current days-to-payment + evidence reminders shorten it here]` |
| `r` | Daily cost of money / value of cash-flow certainty | `[NEEDS INPUT: for a solo operator this is a stress-and-planning cost, not an interest rate — define before estimating]` |
| `H` | Hours/month spent chasing | `[NEEDS INPUT: ask the cohort]` |
| `W` | Effective hourly rate | `[NEEDS INPUT: segment rate band]` |
| `P` | Price per month | `[NEEDS INPUT: undecided; see ASM-505]` |
| `k` | Value-to-price multiple required | `[NEEDS INPUT: probe in interviews]` (ASM-507) |

**Two traps, stated before anyone fills these in.** (1) `N × A × U` counts **only** invoices that
would otherwise never have been paid; one that was always going to arrive, just late, belongs in the
carry term. Counting it as recovery inflates `V` by an order of magnitude and is the standard way
this category's cases go wrong. (2) `V` is not flat monthly value — it scales with invoice flow, so a
quiet month pays `P` for almost nothing. Models ignoring this overstate retention.

`[ASSUMPTION: the time term (H × W) alone cannot justify a subscription, because users rarely value unbilled admin hours at their billable rate. If true the case rests almost entirely on U — the least knowable variable. | conf: med]`

### 17.4 Venture-side — does Boss recover the build?

```
m = P − c_var      contribution per active user/month
B = C_fixed / m    users needed to cover fixed run cost
LTV = m / churn    payback = CAC / m
```

| Sym | Meaning | Status |
|---|---|---|
| `C_build` | One-time investment | `[NEEDS INPUT: honest build-hours × stated hourly opportunity value, plus cash outlay]` (ASM-509) |
| `C_fixed` | Fixed monthly run cost | `[NEEDS INPUT: hosting, domains, non-scaling third-party fees]` |
| `c_var` | Variable cost per user/month | `[NEEDS INPUT: outbound messaging + expected support minutes; depends on the RSK-006 channel decision]` |
| `churn` | Monthly user churn | `[NEEDS INPUT: unknowable pre-launch — model as a range, then measure]` |
| `CAC` | Blended acquisition cost | `[NEEDS INPUT: depends on RSK-008; if only organic is viable this is denominated in time, not money]` |

**Run-rate honesty, in advance.** In the usual case a new platform quietly costs more to run than the
legacy one. Here the buyer's comparison is against **₹0** — nothing is currently paid for the manual
behaviour, so there is no legacy cost to offset and the offering must be justified entirely on new
value created. That is a structurally harder business case than most.

### 17.5 The six gating inputs

| Gate | Input | Why it gates | Cheapest source |
|---|---|---|---|
| G1 | `U` recovery uplift | If ≈0, no configuration of the others saves the case | Measured before/after on a small cohort; no substitute |
| G2 | `A × N` at-risk value | Ceiling on what any uplift can be worth | Cohort interviews + invoice records |
| G3 | `P` at stated acceptance | Whether any viable price exists at all (RSK-003) | Price probe, same interviews |
| G4 | `C_build` | What payback must beat | Boss's own estimate — already known to him |
| G5 | `CAC` or a named organic channel | Whether users are reachable at all (RSK-008) | One concrete concentration of the segment |
| G6 | `churn` range | Whether `m` accumulates or leaks | Not obtainable pre-launch; bound as a range |

**G1-G3 and G5 clear in one interview round, G4 is already known** — four of six gates resolve before
any build commitment.

### 17.6 Decision rule, pre-committed

Stated now, while there is no number to rationalise around.

- **Proceed** only if `V ≥ k × P` at a price the cohort states as acceptable, **and** `m` clears
  `C_fixed` at a user count the identified channel can plausibly reach.
- **Stop** if the ASM-501 retrospective shows follow-up failure is not the primary cause of
  non-payment in a majority of cases → evaluate A3 instead.
- **Re-shape, not stop,** if the blocker is relational (RSK-002): the need is real, the framing is not.
- **Downside case, structurally:** the realistic bad outcome is not cost overrun — it is building
  something correct that nobody pays for (`U` real but small, `P` forced below `c_var + C_fixed/B`).
  Sunk cost is `C_build` in Boss's time, and none of it is discovered by building faster.

### 17.7 Unquantified benefits — quarantined

Excluded from every equation above and not to be folded in later: portfolio/credibility value of a
shipped commercial product independent of revenue; reusable capability transferable to Boss's other
initiatives; learning value of a live pricing and distribution test.

These may be the *actual* reason to proceed — but they accrue to Boss's career, not to a business
case, and folding them into the arithmetic is how unviable ventures get approved. If they are the
real motive, say so, and §17 becomes largely unnecessary rather than merely unpopulated.

---

**Traceability gap for assembly.** Rows above cannot yet link to OBJ-/BR- IDs owned by sibling parts.
Jarvis must add those links at merge — unlinked register rows score as broken traceability under
rubric criterion 6.
