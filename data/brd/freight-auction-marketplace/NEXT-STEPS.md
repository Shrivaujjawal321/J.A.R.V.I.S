# What to resolve first — the critical path

The BRD states 284 open questions correctly, each in its own section. What it does not say is **which
order to answer them in**. That is this page. Written by Jarvis after assembly, because the assembler
identified the gap and it is a manager's job, not a drafting agent's.

Most of the 284 are downstream of five questions. Answer these five and the document largely
resolves itself. Answer them out of order and work gets redone.

---

## Q1 — Is the client a licensed property broker, a motor carrier, or a software vendor?

**Ask the client. Today. Before anything else is designed.**

This is a **fact the client already knows**, not a decision anyone has to make — which is why it goes
first. It costs one question and unblocks the most.

Five sections independently stopped on this and none of them could see the others asking: A6 (who
invoices whom, and whether the platform may touch the money at all), A7 (whether FMCSA authority, a
BMC-84 surety bond and BOC-3 process agents are the client's obligation), A8 (whether cargo liability
lands on the platform), A9 (who at the client signs off on anything), A10 (whether the economics are
a take rate or a software licence).

Until it is answered, four of those five sections are provisional. It also decides something larger:
**whether Boss is building software, or helping stand up a regulated freight brokerage.** Those are
different projects with different costs.

---

## Q2 — What is the client actually being paid to fix?

**Needs one conversation with one real shipper. Not a Boss answer — a shipper answer.**

A10 could not fill rungs 1 and 5 of its Five Whys ladder, and refused to invent them. The candidates
are genuinely different products:

| If the real pain is… | …then this is a |
|---|---|
| Carrier vetting is slow and now legally hazardous | vetting product |
| Fraud makes cheap capacity unusable | trust product |
| The back office is manual | operations product |
| Small shippers have no brokerage relationship | access product |
| Price | auction product |

Only the last one makes the auction the centre. And A10's finding is that price discovery in US
truckload is **already sold cheaply** by DAT and Truckstop — so if the answer is "price", the product
is competing with an incumbent substitute on its strongest ground.

This is the question most likely to re-point the whole document, and it is far cheaper to ask now
than after a build.

---

## Q3 — What form does the client receive the data platform in?

**Hosted API · embedded dataset · a database the client takes possession of.**

A12 flagged this as the input that changes the most, and it is not a preference — the ODbL answer
differs in all three cases. It decides whether the OpenStreetMap-derived layers can be used at all
inside a proprietary client product.

**Independent of the client's answer, one fix is already due in truck-intel:** `/v1/fuel` returns
`osm.fuel_stations` records as JSON today, and the tile routes serve `osm.rest_areas` and
`osm.weigh_points`. Under ODbL that is re-utilisation into a publicly-used derivative database. The
rule that keeps both the layers and a proprietary posture: **ODbL layers are consumed internally as
Produced Works only and never cross the API boundary.** The Overture layers (fuel places 151,767 and
mechanic shops 11,759) are permissive and unaffected — verified, not assumed.

---

## Q4 — What is the safety floor for the eligibility gate?

Boss has already decided **that** there is a gate (DEC-LOCK-001). What the gate actually tests is
still open, and it is A2's DEC-201: which FMCSA signals, at what level, re-checked how often.

This is a real trade-off with a real cost on both sides. Set it too high and the marketplace loses
the small-fleet and owner-operator capacity that makes up most of US truckload supply. Set it too low
and the gate does not do the job it was created to do after *Montgomery*.

It also needs a second party Boss does not control: **the client's insurer will have a view**, and
A3 flagged that the underwriter's position may bind this more tightly than counsel's.

---

## Q5 — The auction parameters

A3 has eleven parameter decisions waiting (DEC-302 … DEC-312): open versus sealed bidding, whether
bidders see the standing best price, duration, anti-sniping extension, minimum decrement, reserve
price, and whether the shipper may decline the winner.

These are last **deliberately**. Every one of them is cheap to change on paper and expensive to
change after Q1-Q4 have moved the ground under them. Two are worth flagging early anyway:

- **DEC-304, auction duration.** US truckload spot demand is frequently same-day or next-day. If the
  shortest duration a real shipper tolerates is shorter than an auction needs to attract bidders,
  the mechanism does not work on the loads it was built for.
- **DEC-307, may the shipper decline the winner.** Post-*Montgomery* this hands a discoverable
  selection decision to the party holding *less* safety data than the platform. It reads as a
  courtesy feature and behaves like a liability transfer.

---

## What is NOT blocked

Q1-Q5 do not block everything. These are settled enough to proceed on:

- The lifecycle and custody model (spine §3, as amended by A3, A5 and A8's accepted challenges)
- Carrier eligibility as a per-load computed result rather than a carrier-level flag (A2)
- The evidentiary spine: pickup record → Bill of Lading → clear-vs-exception delivery signature →
  claim (A4, A5, A8) — this is what a cargo claim lives or dies on regardless of the answers above
- Route feasibility from the truck-designated network, bridge posting and hazmat tunnel data — the
  strongest of the data capabilities, and its licence position is the clean one
