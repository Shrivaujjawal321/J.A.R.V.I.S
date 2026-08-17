# R1 — Revision of A6 under DEC-LOCK-003 (broker of record locked)

**Governs:** `part-A6-money-invoicing.md`, IDs 600-699 (unchanged block). Revision, not a rewrite —
every item below is tagged `[REVISED]`, `[NEW]`, or `[CLOSED]` against the original. Untagged original
requirements (BR-602/603/604/606-608/610, EC-602–EC-609) stand as written; they were never
model-conditional and DEC-LOCK-003 does not touch them.

## 1. The fork is collapsed

§1's `[NEEDS INPUT]` is closed. **Model B — broker of record — is the only model.** A (pass-through)
and C (commission-only) are **rejected**, not deprioritised: the platform sets price via auction and
now holds broker authority, which is incompatible with A's "never touches the freight charge" and C's
"not party of record." Delete both rows.

| Original hedge | Resolution |
|---|---|
| ASM-600 (invoice = "at minimum an artifact... resolved once §1 answered") | **[CLOSED].** It is the shipper-facing sell invoice of a principal, one half of the pair in §2. Confidence Low → High. |
| BR-605 "**In Model B**, carrier payable and shipper receivable... two independently timed obligations" | **[REVISED]** — unconditional now, and both are formal documents (§2), not just ledger states. |
| BR-609 quick pay funding, platform capital **or** third-party partner | **[REVISED]** — both paths live; financing-partner path gets a structuring condition, §7. |
| §6's three-row "who bridges the gap" table | **[REVISED] → one structural default.** "Platform bridges" is no longer an alternative among three — it's the only shape as principal. "Carrier bridges independently" survives only as the carrier's own choice to factor its *platform-owed* receivable (folds into §4). "Hybrid quick-pay" survives as a tactic *within* Model B. |
| BR-611 payment terms, both `[NEEDS INPUT]` | **[REVISED, figures still open]** — that both terms must exist is now certain; no number invented. |
| BR-612/613 W-9 / 1099-NEC | **[REVISED — universal]** — every carrier payment now runs through the platform; no path (Model A) sits outside this. |
| BR-614 mechanism "set by §1 model choice (subscription/listing/spread)" | **[REVISED]** — mechanism is the spread only. Ancillary fees are A10's call, out of scope here. New presentation rule at BR-616. |
| §8 money-transmission flag, routed to A7 | **[REVISED — stress-tested, still routed].** See §7. Not closed here. |

## 2. The invoice pair

One load now produces **two documents**. DEC-600's `INVOICE_ISSUED → INVOICE_FINALISED` split governs
each independently.

| | **Sell-side: Platform → Shipper** | **Buy-side: Carrier → Platform (or self-bill)** |
|---|---|---|
| Basis | Sell rate = base + spread `[NEEDS INPUT: spread policy]` + verified accessorials + shipper FSC | Carrier rate-confirmation base (the winning bid) + carrier-incurred, evidenced accessorials + carrier FSC |
| Trigger | `POD_CAPTURED` → `INVOICE_ISSUED` | Carrier submits invoice + POD, **or** platform self-bills off the rate confirmation + accessorial log — `[NEEDS INPUT: which mode]` |
| Lifecycle | `INVOICE_ISSUED` → held lines → `INVOICE_FINALISED` | Shadow lifecycle on the same load, can finalise on a different clock |
| Presentation | All-in sell price only — never itemise a "carrier cost" against a "platform fee" (BR-616, §7) | Full backup: rate confirmation ref, accessorial evidence (BR-602), POD ref |

**BR-600 [REVISED]** Generate **two rate confirmations** at `AWARD_ACCEPTED`: carrier-facing (winning
bid as base, accessorial table, carrier FSC method) and shipper-facing (sell rate, pass-through terms,
shipper FSC method). Carrier's acks before `PICKUP_SCHEDULED`; shipper's before `AWARDED` closes.
*Acceptance: no load reaches `PICKUP_SCHEDULED` without both on file.*

**BR-601 [REVISED]** Buy-side = carrier base + verified carrier accessorials + carrier FSC − OS&D hold
pending A8. Sell-side = platform sell rate + pass-through accessorials per BR-616 markup policy +
shipper FSC − any shipper-side OS&D hold. Bid and buy-side total are never shown as the sell invoice.
*Acceptance: each side reconciles independently to its own confirmation + accessorial log.*

**BR-615 [NEW]** Sell- and buy-side invoices are two linked objects sharing a load ID; neither exists,
holds, or finalises without the other (even in a `[NEEDS INPUT: default pre-submission state]`).
*Acceptance: no load has one invoice without the other in at least draft state.*

**BR-616 [NEW]** Sell-side invoice presents a single all-in price — never itemises carrier rate,
spread, or "platform fee" against a disclosed carrier cost. *Source: derived — this presentation is
the structural condition under which §7's money-transmission reading holds. Acceptance: sell-side
template has no field decomposing price into carrier-cost + platform-take.*

**BR-617 [NEW]** Support both carrier-submitted invoices and platform self-billing as buy-side intake
modes, operator-configured — `[NEEDS INPUT: which mode(s) at launch]`. *Acceptance: buy-side invoice
reaches `INVOICE_ISSUED` regardless of intake mode.*

## 3. The spread is revenue, computed per load

**BR-618 [NEW]** Spread = sell-side total − buy-side total, booked as recognised revenue **only once
both sides reach `INVOICE_FINALISED`** — not at issuance, since either side can still move (claim,
accessorial, dispute). *Acceptance: no spread figure books while either side is `HELD`.*

**BR-619 [NEW]** An accessorial discovered **after** the sell-side invoice is issued generates a
linked **supplemental invoice / debit note** on the sell-side, referencing the same evidence used on
the buy-side — not a silent margin absorption. *Source: derived — BR-604 covers deductions via credit
note; nothing in the original covered late additions. Acceptance: every post-issuance buy-side
accessorial has a matched sell-side debit note, or a logged decision that the platform absorbs it.*

`[NEEDS INPUT: accessorial markup policy]` — pass-through at incurred cost, or marked up. Sets whether
BR-619's debit note equals the buy-side addition exactly or carries margin.

## 4. Factoring and NOA — core, not edge case

BR-606–BR-608 (capture, single-active-NOA, remit-to routing) are **unchanged** — written unconditional
in A6's first pass, and DEC-LOCK-003 confirms that was right. What changes is posture:

**BR-622 [NEW, restates 606-608 as universal]** NOA handling applies to **100% of carrier payables** —
no remaining path where a shipper pays a carrier directly and the platform isn't the account debtor.
*Acceptance: NOA-status check gates every buy-side payment run, no model exception.*

**Double-payment exposure, restated.** This is now the platform's own cash: pay a carrier directly
while a valid NOA is on file, and the factor — legal payee, account debtor is the platform — can still
collect. The platform pays the same invoice twice out of its own balance sheet. EC-602 and EC-609
already name this; DEC-LOCK-003 raises it from a control gap to a recurring cash-loss exposure at
volume.

**EC-612 [NEW]** Carrier elects quick pay on a load with an active NOA on file — the factor, not the
carrier, is legal payee. `[NEEDS INPUT: is quick pay offerable to a factored carrier; if so, is the
discount negotiated with the factor or the carrier]`. Decided by platform, compliance sign-off per
BR-608. No default policy exists today.

## 5. Working capital

§6's structural point (platform owns the terms gap) is now the *only* shape of the business.

**BR-620 [NEW]** Maintain independent AR ageing (shipper, sell-side) and AP ageing (carrier, buy-side)
per load, rolled up platform-wide, with net AR − AP gap as a standing figure — the platform's own
working-capital exposure. `[NEEDS INPUT: reporting cadence]`. *Acceptance: net exposure queryable
without ad hoc reconciliation.*

**BR-621 [NEW]** Carrier sees its own buy-side status (issued/held/finalised/paid) and quick-pay
eligibility independent of shipper's payment status to the platform — extends BR-605's independence
to a carrier-facing view. *Acceptance: carrier portal never references shipper collection status.*

BR-609 (quick pay) and BR-611 (payment terms) stand, figures untouched: discount rate, payout window,
shipper net-terms, carrier payout-cycle days all still `[NEEDS INPUT]`. The lock changes the shape of
the requirement, not its numbers.

## 6. Tax and reporting — now certain

**BR-612/BR-613 [REVISED — universal, not conditional]** W-9 collection and 1099-NEC tracking apply to
every carrier the platform pays; no remaining path where it isn't the payer. Mechanics unchanged; only
the "conditional on §1" qualifier is deleted.

## 7. The money-transmitter question — stress-tested, not accepted whole

DEC-LOCK-003's claim: a broker of record moves its own receivables/payables, which is commercial
credit, not money transmission — and this removes a pre-launch licensing cost.

**What supports it.** This is how the conventional US freight-brokerage industry already operates,
unlicensed for money transmission, at scale — real-world evidence, not just theory. Most state
statutes target someone receiving a stranger's money for onward transfer, not a party settling its own
two contracts.

**Where it is conditional, not settled:**

1. **Presentation is load-bearing.** The reading depends on the platform selling its *own* service at
   its *own* price, not facilitating a disclosed carrier charge plus a fee. BR-616 isn't cosmetic — it
   is the fact the legal argument rests on. Itemised "carrier gets $X, platform keeps $Y" pricing pulls
   toward agency/pass-through, the exact fact pattern these statutes target.
2. **Quick-pay financing partners break it if structured wrong.** A partner funding early payouts
   *through* the platform's account, earmarked for a specific carrier, looks like transmitting someone
   else's money, not extending the platform's own credit. BR-623 names the required structure.
   `[NEEDS INPUT: is a financing partner in scope for launch, and its legal structure — routed to A7]`.
3. **State variance is unverified.** Most states exempt goods/services payments and UCC Article 9
   factoring, but exemption language isn't uniform, and a shipper/carrier/platform-HQ footprint across
   three states can implicate more than one definition at once. `[NEEDS INPUT: state survey — A7's,
   not assessed here]`.

**BR-623 [NEW]** Where a financing partner funds carrier quick-pay, structure it as a true
sale/assignment of the platform's own payable (or fund from platform capital) — never pooled custodial
pass-through of shipper funds earmarked for a carrier. *Source: derived — the condition under which
§7's reading holds for quick-pay specifically. Routed to A7, not decided here.*

**Verdict:** directionally sound and matches unlicensed industry practice today — should not be
dismissed as a comfort read. But it is **conditional**: on clean presentation (BR-616), on properly
structured financing (BR-623), and on no state quirk breaking the pattern (unverified). Treating it as
settled before A7/R2 confirms the state survey would be exactly the comfortable conclusion the brief
warned against.

## Summary

**Closed:** the §1 model fork (Model B only); ASM-600; the "conditional on model" language on
BR-605/609/611/612/613/614; the §6 three-row table (collapsed to one default plus two sub-options).

**Newly required:** BR-615 (linked pair), BR-616 (all-in presentation — also §7's structural
condition), BR-617 (buy-side intake mode), BR-618 (spread booked at dual-finalisation), BR-619
(supplemental invoice for late accessorials), BR-620 (AR/AP ledger + net exposure), BR-621
(carrier-facing payable status), BR-622 (NOA restated universal), BR-623 (financing-partner
structuring); EC-612 (quick pay vs. active NOA conflict).

**Honest verdict on the money-transmitter reading:** likely correct, not yet safe to rely on. Well
supported by how the industry operates, but resting on three conditions this document had to name
rather than inherit. Route to A7/R2; don't let confident framing stand without that check.

**Single biggest new financial risk:** double-payment exposure on factored receivables (§4) is no
longer a control gap on someone else's money — it's a direct, recurring draw on the platform's own
cash, because the platform is the account debtor on every load. A missed or forged NOA is real money
paid twice off the platform's own balance sheet, and at volume it's the line item most likely to erase
an already-thin 13-16% spread (A10's cited incumbent margin range) on the loads it hits.
