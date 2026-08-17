# FRD spine — canonical conventions for the functional/technical specification

**Authored by Jarvis (manager) before any agent was dispatched.** The BRD phase proved this works:
twelve agents, 212 requirements, **zero ID collisions**, because the shared skeleton existed first.
Same discipline here. Every agent reads this file and works inside it.

**Read `spine.md` (the BRD spine) too.** Its §0 (USA jurisdiction), §1 (roles), §3 (lifecycle and
custody chain) are inherited unchanged. **Do not re-invent the state machine.** If a state is missing
for your area, propose it in a `CHALLENGE:` block — three such proposals were accepted in the BRD
phase, so the mechanism works.

---

## 0. What changed from the BRD phase — read this first

The BRD **forbade solution language.** This document **requires it.** You are now specifying the
system: entities, endpoints, roles, permissions, screens, errors, events.

Two rules survive unchanged:
1. **No invented numbers.** No rate limits, timeouts, retention days, page sizes, SLAs or thresholds
   pulled from the air. Tag `[NEEDS INPUT]` or `[ASSUMPTION: … | conf: …]`. This rule cost the BRD
   points on a rubric that rewards filled-in numbers — and it was still right. Hold it.
2. **No vendor lock-in.** Name the *capability* (ELD telematics ingestion, carrier-vetting data feed,
   document capture), not the vendor, unless Boss has chosen one. Vendors go in an integration
   register as candidates, never baked into a requirement.

---

## 1. Scope additions Boss stated on 2026-07-29

Beyond the BRD's flow, the system also:
- **Assigns the driver and the truck** to a shipment (not just the carrier)
- **Tracks how long a driver drives in a day** — see §7, this is regulated and contested
- **Tracks the truck** in motion
- Carries an **equipment taxonomy including trailer types** — tractor, trailer, and their pairing
- Treats carrier eligibility as running **on behalf of specific trucks** (already A2's model)

Boss's words: *"there is lot of things in this system i want you to cover every posiblites… error
kia kia askte hai, authentication kese hoga, role based access kese denge, api kon kon si chahiye,
dashboard mai kia kia hoga, feature kese provide kr sakte hai. sab kuch. kuch bhi chutna nahi
chahiye."*

**Exhaustiveness is the deliverable.** A named, unresolved case is a success; a silently
unconsidered one is the failure.

---

## 2. Tenancy and identity model — canonical, do not diverge

```
Organization (tenant)
   ├─ type: SHIPPER | CARRIER | PLATFORM
   ├─ Users (belong to exactly one Organization)
   │     └─ Roles (scoped: org-wide, site, or per-load)
   └─ Resources (loads, trucks, drivers, documents) — owned by the Organization
```

- **Every resource belongs to an Organization.** Cross-org visibility is granted by the transaction
  (a carrier sees a load because it is eligible to bid or has been awarded), never by default.
- **A Driver is a User** with a narrow role — usually mobile-only. A driver may be an employee of a
  carrier org, or an owner-operator who *is* the carrier org. Both must work.
- **The Receiver/Consignee has NO account.** Inherited from the BRD and non-negotiable. Any flow
  that needs the consignee to act must work for someone with no login. Design for a tokenised,
  single-purpose, expiring link at most — never an account requirement.
- **Platform ops are Users in a PLATFORM org** with elevated, audited roles.
- **Broker-carriers** (BRD spine §1) are CARRIER orgs with a flag, not a separate tenant type.

---

## 3. Permission primitive — every agent uses this shape

```
(role) may (action) on (resource_type) when (scope condition)
```

Scope conditions are one of: `own_org` · `own_site` · `assigned_load` · `eligible_load` ·
`platform_wide` · **`granted_case`** · **`aggregate_threshold`**. **Do not invent new scope kinds
without a CHALLENGE.**

**The last two were added after two agents independently challenged the original five.** Both
challenges are accepted; recording them because the reasoning matters at build time.

- **`granted_case`** (F2's challenge, and the more urgent of the two). Platform-ops access bound to a
  **specific ticket, load or claim**, time-boxed and audited. Without it, every ops permission
  collapses to `platform_wide` — which is standing all-tenant access for every support user, and it
  is exactly what makes the BRD's insider re-award fraud vector undetectable. An ops person should be
  able to see the load they are working on, for as long as they are working on it, and not the
  marketplace. **If only one spine change survives to build, it is this one.**
- **`aggregate_threshold`** (F12's challenge). Cross-org, de-identified, minimum-count-gated access
  for comparative or benchmark reporting — lane pricing being the obvious case. It exists so that a
  benchmark feature cannot be built by quietly widening someone's scope to `platform_wide`, and so
  that a "benchmark" over two carriers on one lane, which is just a competitor's rate with extra
  steps, is impossible by construction. Threshold value is `[NEEDS INPUT]`.

Permission tables must be expressed as rows of that shape. A prose paragraph describing who can do
what is not a permission specification and will be rejected at assembly.

**Field-level view masks — a required extension, not a sixth scope kind** (F8's CHALLENGE-800,
accepted). Scope conditions resolve *which resource* a role may see. They cannot express *how much of
it*. Location is the clean example: a shipper sees a corridor band, the carrier's own dispatcher sees
an exact pin, and audited platform ops sees exact position — **same resource, different depth**.
Expressing that by widening scope would grant the whole record, which is precisely wrong.

So permissions carry an optional **view mask**: `(role) may (action) on (resource_type) when (scope)
[at (granularity)]`. Granularity values are defined per resource type by the owning agent — F8 owns
location granularity — and F2 owns the enforcement rule. **The mask must be enforced at the data
layer, not in the serializer**, for exactly the reason F2 gave: a serializer-layer rule survives
until the first export, webhook payload, or `include=` parameter forgets it, and then it fails
silently while looking like normal code.

Actions carried over from the BRD as already-identified and still contested — cite them, do not
re-litigate: who may publish a load · who may bid · who may accept an award on a carrier's behalf ·
who may sign a POD · who may cancel · who may raise or settle a claim · who may waive a charge · who
may approve a carrier onto the platform.

---

## 4. API conventions — canonical, so twelve agents produce one coherent surface

- **Versioned base path** `/v1`. Resource-oriented, plural nouns, kebab-free (`/v1/loads`,
  `/v1/loads/{id}/bids`).
- **Mutating requests carry an idempotency key.** Bidding, awarding, POD capture and payment
  operations are the ones where a duplicate is materially harmful — say so where it applies.
- **Cursor pagination**, not offset. Page size is `[NEEDS INPUT]`, do not invent one.
- **Every response carries a correlation/trace id.**
- **One canonical error envelope. Use exactly this shape:**

```json
{
  "error": {
    "code": "BID_BELOW_ELIGIBILITY_FLOOR",
    "message": "human-readable, safe to show a user",
    "field": "optional — for validation errors",
    "details": {},
    "trace_id": "..."
  }
}
```

- **Error codes are SCREAMING_SNAKE, stable, and never reused for a different meaning.** They are an
  API contract; renaming one is a breaking change.
- **Events/webhooks** for state transitions, named `<entity>.<past_tense_event>` — e.g.
  `load.awarded`, `bid.rejected`, `pod.captured`. Every BRD lifecycle state change should have one
  unless there is a reason it should not.
- **Auth scheme, token lifetime, rate limits, retry policy:** specify the *mechanism*, mark the
  *numbers* `[NEEDS INPUT]`.

---

## 5. ID allocation — no collisions

Agent N owns block `N×100 … N×100+99` for every prefix, exactly as in the BRD phase.

| Agent | Block | Area |
|---|---|---|
| F1 | 100-199 | Identity, authentication, sessions, onboarding |
| F2 | 200-299 | Authorization / RBAC / permission matrix |
| F3 | 300-399 | Entity & data model, state machines, audit |
| F4 | 400-499 | API surface — catalog, conventions, integration APIs |
| F5 | 500-599 | Error taxonomy & failure semantics |
| F6 | 600-699 | Auction & bidding functional spec |
| F7 | 700-799 | Driver, equipment/trailer taxonomy, assignment, **HOS** |
| F8 | 800-899 | Tracking, telematics, ETA, geofencing, privacy |
| F9 | 900-999 | Dashboards & screens per persona |
| F10 | 1000-1099 | Notifications, events, messaging |
| F11 | 1100-1199 | Platform admin & ops console, support tooling |
| F12 | 1200-1299 | Platform NFRs — security, tenancy isolation, availability, observability, DR |
| F13 | 1300-1399 | **Carrier vetting and the `eligibility()` computation service** |

**F13 was added mid-phase, and the reason is worth recording.** The original allocation had no owner
for carrier authority, insurance and safety verification — F7 was scoped to driver, equipment and
HOS only. F6 discovered this while specifying the auction: its entire gate machinery calls an
`eligibility()` function that belonged to nobody, which would have shipped the single most
load-bearing mechanism in DEC-LOCK-001 under-specified. F6 filed a `CHALLENGE:`, the manager accepted
it, and this block exists because of it. **This is the challenge mechanism working as intended** —
the same way three BRD-phase challenges were accepted into the BRD spine.

Prefixes: `FR-` functional requirement · `API-` endpoint · `ERR-` error code · `ROLE-` · `PERM-` ·
`SCR-` screen · `EVT-` event · `ENT-` entity · `NFR-` · `INT-` integration · `EC-` edge case ·
`DEC-` open design decision.

**Never invent another agent's ID.** Write `→ F5 (errors)` in prose; the assembler resolves it.

---

## 6. Trace upward to the BRD

Every functional requirement traces to a BRD requirement (`BR-nnn`) or objective (`OBJ-00n`). A
functional requirement that traces to nothing is either scope creep or a gap in the BRD — say which.
Both are useful findings; silently inventing scope is not.

---

## 7. The Hours-of-Service tension — do not paper over this

Boss asked for the system to track **how long a driver drives in a day.** In the US, driving hours
are federally regulated (49 CFR Part 395, plus the ELD mandate) and the compliance duty sits on the
**motor carrier**, not on a marketplace.

The BRD's regulatory agent (A7) recommended **data minimisation as a control** — specifically *not*
storing ELD, Clearinghouse or drug-and-alcohol data, because ingesting it creates a privacy and
compliance liability the platform would not otherwise carry.

**These two positions genuinely conflict, and F7 owns resolving it into options rather than picking
one.** The distinction that probably matters: using an hours signal for *planning and feasibility*
("can this driver legally complete this run in the window?") is different from becoming a *system of
record for compliance* ("we hold the logs the auditor will ask for"). The first may be achievable
with a derived, minimal, short-lived signal. The second is a regulated product.

Present it as `DEC-` options with consequences. Do not silently build the second while describing
the first.

---

## 8. Hard rules — all twelve agents

1. **Exhaustive within your area.** Boss's instruction is that nothing may be missed. End with a
   dense `EC-` register: trigger · behaviour · who decides · unresolved?
2. **No invented numbers.** §0 rule 2. Applies to timeouts, page sizes, limits, retention, SLAs.
3. **No vendor lock-in.** §0 rule 3.
4. **Obey §2 tenancy, §3 permission shape, §4 API conventions, §5 IDs.** Divergence here is what
   makes twelve outputs unmergeable.
5. **Word budget 2,000-2,500, hard ceiling 2,500.** Plan, then write once. Tables dense, prose thin.
   In the BRD phase three agents burned a run drafting 4,000+ words and rewriting.
6. **Challenge, don't diverge.** `CHALLENGE:` blocks are read and acted on.
7. **Inherit, don't re-derive.** The lifecycle, custody chain, roles and the locked decisions in
   `DECISIONS.md` are settled. Build on them.

---

## 9. Output

One file per agent: `data/brd/freight-auction-marketplace/frd-F<N>-<slug>.md`

The consolidated entity/state model, the merged permission matrix, and the executive summary are
**assembler-owned**. Do not write them.
