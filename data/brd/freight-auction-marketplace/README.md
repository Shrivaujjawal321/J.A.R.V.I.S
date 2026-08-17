# Freight Reverse-Auction Marketplace — document set

US domestic truckload marketplace. A shipper posts a load, eligible carriers bid, the lowest
qualified bid wins, a truck moves the freight, the consignee signs, an invoice is raised.

Built 2026-07-29 from one paragraph of Boss's own words (`intake.md`, kept verbatim). Twenty-five
specialist agents, two assembly passes, one independent scoring pass.

---

## Read in this order

| # | File | Words | Why |
|---|---|---|---|
| 1 | **`NEXT-STEPS.md`** | 978 | **Start here.** 284 open questions compressed into the five that actually block, in the order to answer them. |
| 2 | **`DECISIONS.md`** | 1,586 | The two decisions Boss has locked, the evidence behind each, and two corrections filed against Jarvis. |
| 3 | **`BRD-v1.md`** | 31,366 | The business requirements document. What the business needs and why. |
| 4 | **`FRD-v1.md`** | 36,652 | The functional/technical specification — 20 sections. Auth, permissions, entities, APIs, errors, auction engine, driver/HOS, tracking, screens, notifications, ops console, platform security, eligibility service. |
| 5 | **`prototype.html`** | — | Clickable prototype. Open it in a browser: shipper load board, live auction, carrier bidding, ops queue, shipment timeline, and the driver's phone screens. |

**If you only read two things:** `NEXT-STEPS.md` for what to do next, and `prototype.html` to see what
it looks like.

Two supporting reads once you are in: `FRD-v1.md` §16 (cross-cutting reconciliations — the conflicts
between sections and how they were resolved) and §17 (the 46 open design decisions, deduplicated).

Everything else is source material for those four.

---

## What is settled

**Award rule** — carrier eligibility is checked **first**; the auction ranks on price **inside** the
qualified pool. Boss's mechanism is unchanged: lowest bid still wins, ranking is mechanical, no human
discretion. A gate sits before the auction, not inside it.

**Data assets** — Boss's US truck-data platform is in scope as a feature set: route feasibility
(can this load lawfully run this lane on this equipment) and a fuel-based cost floor that catches a
bid which could never be performed. It is **not** a moat, and this document set does not claim it is.

Both are in `DECISIONS.md` with the reasoning and the evidence.

---

## What blocks everything else

1. **Is the client a licensed property broker, a motor carrier, or a software vendor?** A fact the
   client already knows. Five sections stopped on it independently. It decides whether this is
   software or a regulated brokerage.
2. **What is the client actually being paid to fix?** Needs one conversation with one real shipper.
   If the answer is not "price", this is not an auction product.
3. **What form does the client receive the data platform in** — hosted API, embedded dataset, or a
   database they own? The licence answer differs in all three.
4. **How strict is the eligibility gate?** Too strict removes most US small-fleet capacity; too loose
   and the gate does not do its job. The client's insurer will have a view.
5. **The auction parameters** — eleven of them, deliberately last.

Detail and reasoning in `NEXT-STEPS.md`.

---

## Three findings that could change the product

**The Supreme Court moved under this design.** *Montgomery v. Caribe Transport II, LLC* (14 May 2026,
unanimous) held that state-law negligent-hiring claims against freight brokers are not preempted by
federal law. The preemption defence brokers used to end these cases early is gone nationwide. A rule
that awards on price alone, with FMCSA safety data available and unused, is the fact pattern
plaintiffs look for. This is why the eligibility gate is not optional — and why the award must record
*why* each carrier was selected or excluded.

**Price discovery is not an available wedge.** DAT and Truckstop already sell it cheaply, and the
best-funded attempt at this exact business — Convoy, roughly $1.1B raised — shut down in October 2023.
More instructive than the shutdown: **Convoy's own auction was never price-only.** It scored carrier
quality alongside price so a strong carrier could win without being cheapest.

**Cargo insurance is not federally required for general freight.** FMCSA removed that requirement in
2011. A fully compliant carrier can carry zero cargo cover — so a first large loss on the platform
can be uninsured, and the cheapest bidder is exactly the one most likely to be uncovered.

---

## Honest limits of this document set

- The business premise is **unvalidated**. The Five Whys ladder in the BRD terminates in an honest
  unknown, because no real shipper has been asked what they do today.
- The BRD scored **60/100** against its own rubric from an independent scorer. The score is real.
- **The rubric itself has a defect**, found in that same run: a fabricated twin of this document —
  same structure, plausible invented numbers in the blanks — would score an estimated 85-88, against
  a maximum 3-point penalty for being caught. The rubric rewards filling a blank, not filling it
  truthfully. That is a defect in the scoring tool, not in this document's honesty, and it is being
  fixed.
- **Nothing here certifies that a lowest-bid auction marketplace is the right thing to build.**
  Well-formed and correct are different axes.

---

## Full index

### Governing documents
| File | Words | Contents |
|---|---|---|
| `intake.md` | 413 | Boss's original paragraph, verbatim, plus what was and was not supplied |
| `classification.md` | 981 | Business type, US compliance surface, size budget |
| `spine.md` | 2,592 | BRD canonical model — jurisdiction, roles, lifecycle, custody chain, ID allocation |
| `frd-spine.md` | 1,971 | FRD conventions — tenancy, permission shape, API conventions, error envelope |
| `DECISIONS.md` | 1,586 | Locked decisions and corrections |
| `NEXT-STEPS.md` | 978 | The critical path |

### Business requirements — source parts
| File | Words | Owns |
|---|---|---|
| `part-A1-shipper.md` | 2,472 | Shipper onboarding, load declaration, amendment, cancellation, TONU |
| `part-A2-carrier-assets.md` | 2,498 | Carrier vetting, equipment, **the definition of "eligible"** |
| `part-A3-auction-mechanism.md` | 3,032 | Auction lifecycle, bid rules, award, mechanism alternatives |
| `part-A4-fulfilment.md` | 2,493 | Pickup, custody handover, transit exceptions, HOS as a certainty |
| `part-A5-receiver-pod.md` | 2,319 | Consignee, BOL, clear-vs-exception, refusal, OS&D |
| `part-A6-money-invoicing.md` | 2,266 | Charge model, accessorials, invoicing, factoring, settlement |
| `part-A7-regulatory.md` | 3,500 | FMCSA authority, Carmack, Part 371, HOS/ELD, state privacy |
| `part-A8-liability-trust-disputes.md` | 3,766 | Liability, claims, insurance, 14 fraud typologies, disputes |
| `part-A9-stakeholders-ops.md` | 3,999 | Stakeholder map, RACI, platform operations |
| `part-A10-problem-business-model.md` | 3,145 | Problem statement, US market, unit economics, strategic risk |
| `part-A11-data-assets.md` | 2,518 | Boss's truck-data platform as product capability |
| `part-A12-data-licensing.md` | 2,593 | Per-source licence review for commercial use |
| `assembly-report.md` | 3,759 | Every ID remap, de-dup and orphan from BRD assembly |

### Functional specification — source parts
| File | Words | Owns |
|---|---|---|
| `frd-F1-identity-auth.md` | 2,500 | Authentication, sessions, org and user onboarding |
| `frd-F2-authorization-rbac.md` | 4,752 | Roles, the 60-row permission matrix, cross-org visibility |
| `frd-F3-entity-state-model.md` | 2,500 | Entities, state machines, audit, temporal semantics |
| `frd-F4-api-surface.md` | 2,497 | 56 endpoints, integrations, versioning |
| `frd-F5-error-taxonomy.md` | 2,500 | 67 error codes across 10 classes |
| `frd-F6-auction-engine.md` | 2,493 | Auction execution, bid validation, selection record |
| `frd-F7-driver-equipment-hos.md` | 2,499 | Drivers, tractor/trailer taxonomy, assignment, HOS options |
| `frd-F8-tracking-telematics.md` | 2,499 | Position, milestones, dwell, ETA, location privacy |
| `frd-F9-dashboards-screens.md` | 2,520 | 31 screens across 5 personas |
| `frd-F10-notifications-events.md` | 2,499 | 49 events, notification matrix, delivery semantics |
| `frd-F11-admin-ops-console.md` | 3,478 | Exception queue, vetting, fraud review, overrides |
| `frd-F12-platform-nfr-security.md` | 2,500 | Tenant isolation, retention, audit, DR |
| `frd-F13-eligibility-vetting.md` | 2,498 | The `eligibility()` service |
| `frd-assembly-report.md` | 3,722 | Every propagation, merge and unresolved conflict from FRD assembly |

### Design
| File | Contents |
|---|---|
| `prototype.html` | Single self-contained clickable prototype — 8 screens, dark-mode primary, Cmd+K palette. **Verified working:** 9 screen loads across 4 personas, 0 failures, 0 console errors, 0 external requests. |
| `DESIGN-MAP.html` | **The Figma-style design map — open this in a browser.** Interactive canvas: lifecycle baton, four persona lanes, 138 steps, 24 branch tables, 41 frames, 19 gap findings. Pan/zoom, search, click any card for its full step definition. Self-contained, no network. |
| `MINDMAP-SOURCE.pdf` / `.md` | **Feed this to NotebookLM (or any AI) to get a mind map.** 18k words, 233 headings, every one of the 138 steps fully defined under a heading hierarchy built for mind-map extraction. |
| `MINDMAP.md` | Mermaid diagrams that render as pictures — product mind map, load lifecycle, and one flowchart per persona. Renders on GitHub, Obsidian, VS Code, mermaid.live. |
| `DESIGN-STRUCTURE.md` | **The Figma-style application map** — page tree, every frame, every flow step by step, every branch |
| `DESIGN-GAPS.md` | **Read this one.** The consolidated gap register — what the design audit found missing, ranked by consequence |
| `design-spine.md` | Conventions the six design agents worked to — frame naming, the mandatory step format |
| `design/D1-foundations-components.md` | Foundations · 25 components with every state · 5 patterns |
| `design/D2-flow-shipper.md` | Shipper journey — 43 steps, 6 branch tables |
| `design/D3-flow-carrier.md` | Carrier / dispatcher journey — 42 steps, 5 branch tables |
| `design/D4-flow-driver.md` | Driver mobile journey — 28 steps, 4 branch tables |
| `design/D5-flow-ops-admin.md` | Platform ops + admin/fraud — 30 steps, 8 branch tables |
| `design/D6-cross-flow-map.md` | How the four flows hand off, the frame index, and the coverage audit |

**What the design audit found.** Twelve named gaps. The one to look at first: F10 identified a missed
`award.confirmed` as the single most expensive failure in the system — the carrier never learns it
won, and the load sits uncollected. Ops gets paged. **And no screen in the 31-screen inventory can
work that failure to resolution**, because `ExceptionCase`'s types structurally exclude it. The most
expensive failure has no tool to fix it. That finding only appears when three agents' work is read
together.

Also: the **consignee has no screen anywhere** — the party whose signature closes the shipment and
triggers the invoice. And six lifecycle states render nowhere: `CANCELLED_BY_SHIPPER`,
`CARRIER_NO_SHOW`, `SHIPPER_NOT_READY`, `PICKUP_REFUSED`, `PARTIAL_DELIVERY`, `RETURN_TO_ORIGIN`.

---

## How this was built

Each phase ran the same way: **a spine was written before any agent was dispatched** — canonical
model, pre-allocated objectives, per-agent ID blocks, explicit scope boundaries. A smoke test earlier
the same day had proved that fanning agents out without one produces orphaned IDs, duplicated
requirements, and an assumptions register incomplete by construction.

It held. The BRD phase produced 212 requirements across twelve agents with **zero ID collisions**.

Agents were required to challenge the spine rather than diverge from it silently. **Seven challenges
were accepted and changed the model**, including three that corrected the manager's own design: no
owner existed for the eligibility service; platform-ops permissions collapsed to full-platform access
and would have made insider fraud invisible; and "which resource you can see" turned out to be a
different question from "how much of it you can see."

Every unknown is tagged rather than invented. Across both documents there is not one fabricated rate,
market size, retention period, threshold or date.
