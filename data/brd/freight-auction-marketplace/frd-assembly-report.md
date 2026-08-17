# FRD Assembly Report

Companion to `FRD-v1.md`. This is the record of what the assembler did, why, and what it could not
do — not a second copy of the specification. Where `FRD-v1.md` has an **[ASSEMBLER FIX]**,
**[ASSEMBLER ADDITION]**, or **[ASSEMBLER NOTE]** marker, this report gives the full reasoning
behind it; the two documents are meant to be read together.

**No self-score is given here or in `FRD-v1.md`.** A prior assembly on this project scored its own
work and an independent scorer found it had graded only the dimensions it was good at. An
independent scorer runs separately against this document.

---

## 1. Counts

### 1.1 Entities

**34 consolidated entities** (`FRD-v1.md` §3.2): 25 from F3's base catalog (`ENT-300`–`324`) + 1
new (`ENT-325 AvailabilityWindow`, closing a gap neither F3 nor F7 alone fully covered — §3.1.2) + 8
from F13 (`ENT-1300`–`1307`, additive, no overlap). **F7's own 6 entity IDs (`ENT-700`–`705`) are
superseded, not counted separately** — see §2.1 below for the full duplicate-resolution reasoning.
F8's six named-but-unnumbered entities (`PositionPing`, `Milestone`, `GeofenceZone`, `DwellSession`,
`ETAEstimate`, `TrackingCapability`) are flagged as a real gap in the catalog, not assigned IDs here
(§10.8 of the FRD; assigning IDs without F8's own field-level detail would be guessing rather than
reconciling).

### 1.2 Requirements (`FR-`)

Per-section counts, verified against each source file's own full-prefix `FR-nnn` mentions:

| Section | FR count |
|---|---|
| F1 (§5) | 56 |
| F2 (§4) | 23 |
| F3 (§3) | 22 |
| F6 (§8) | 19 |
| F7 (§9) | 38 (6 HOS-conditional) |
| F8 (§10) | 50 |
| F9 (§11) | 3 explicit (`FR-900`, `FR-901` referenced, `FR-903`) — F9 mostly specifies via `SCR-` rows instead |
| F10 (§12) | 11 original + 0 new (the two new events, `EVT-1049`/`1050`, did not require new `FR-` rows) |
| F11 (§13) | 50 |
| F12 (§14) | 1 (`FR-1200`; F12 predominantly uses `NFR-`, counted separately) |
| F13 (§15) | 21 |
| **Total** | **294** |

F4 (§6) and F5 (§7) define no `FR-` rows by design — F4 is a wire-contract catalog (`API-`/`EVT-`/
`INT-`/`EC-` only), F5 is an error taxonomy (`ERR-`/`EC-` only).

### 1.3 API Endpoints (`API-`)

| Section | API count |
|---|---|
| F1 (§5) | 19 |
| F4 (§6) | 56 |
| F6 (§8) | 6 |
| F7 (§9) | 8 |
| F13 (§15) | 7 |
| **Total** | **96** |

One overlap resolved, not double-counted: `API-468` (F4) and `API-1300` (F13) are two different
consumer-facing wrappers (self-check vs. F6-internal call) around the same `eligibility()`
computation, now sharing the same four-argument contract (§2.2 below). Both remain in the catalog —
they are legitimately two endpoints, not a duplicate.

### 1.4 Error Codes (`ERR-`)

**68** — F5's own 67 (`ERR-500`–`566`, of an allocated-vs-reserved range of 500-599) plus **1
assembler-added** (`ERR-567 EXCEPTION_CASE_TRANSITION_INVALID`, §7.3 of the FRD, closing the gap F3
explicitly named: "F5 gets a smaller Load-transition set plus a new ExceptionCase-transition set").

### 1.5 Permissions (`PERM-`) and Roles (`ROLE-`)

- **Permissions: 65** — F2's original 60 (`PERM-200`–`259`) + **5 assembler-added** (`PERM-260`
  eligibility-gate override, closing F13's out-of-block `PERM-1300` reference; `PERM-261`/`262`/
  `263`, the field-level location-view-mask rows F8's `CHALLENGE-800` required and F2's matrix never
  wrote; `PERM-264`, auction-ruleset/eligibility-gate-policy config editing, required by F6 §8.7, F11
  §13.7, and F13 §15.6 but owned by none of them).
- **Roles: 26** — F2's original 24 (`ROLE-200`–`242`) + **2 assembler-added** (`ROLE-229
  PLATFORM_SENIOR_REVIEWER`, formalizing what F2's own `PERM-245` called only "ops supervisor" and
  what F11 independently named "ops-senior"; `ROLE-230 PLATFORM_CONFIG_ADMIN`, required by the same
  three sections `PERM-264` serves).

### 1.6 Events (`EVT-` and named-but-unnumbered)

| Source | Count | Disposition |
|---|---|---|
| F4 (§6.5) | 30 (`EVT-400`–`429`) | **Superseded** by F10's catalog — retained (never reused per ID rule) with a full mapping table |
| F6 (§8.10) | 15 (`EVT-600`–`614`) | Domain-internal, cross-referenced to F10 equivalents where they exist |
| F7 (§9.9) | 9 (`EVT-700`–`708`) | Same |
| F8 (§10.8) | ~14 named, unnumbered | Same |
| F10 (§12.1/§12.1a) | 49 original + **2 assembler-added** = 51 | **Canonical catalog** |
| F11 (§13.10) | 13 named, unnumbered | Genuine gaps vs. F10 — ops-internal audience F10 never covered; not invented |
| F13 (§15.10) | 7 named, unnumbered | 1 (`carrier.reinstated`) canonicalised into F10 as `EVT-1050`; other 6 remain gaps |

**103 formally-`EVT-`-numbered events across F4+F6+F7+F10** (30+15+9+49, before the 2 assembler
additions), **137 total distinct named event concepts** across all seven sections that name events
at all, with substantial duplication by underlying transition (§2.3 below) — this duplication, not
the raw count, is the finding that matters.

### 1.7 Screens (`SCR-`)

**31** (F9, `SCR-900`–`943`, verified by direct count against the five-persona inventory).

### 1.8 Edge Cases (`EC-`)

Each file's own register size (not counting the further ~150 cross-part `EC-`/`BR-` citations
scattered through prose, which inflate a raw pattern-match count without representing additional
distinct edge cases):

| Section | EC register size |
|---|---|
| F1 (§5) | 15 |
| F2 (§4) | 23 |
| F3 (§3) | 22 |
| F4 (§6) | 17 |
| F5 (§7) | 15 |
| F6 (§8) | 23 |
| F7 (§9) | 13 |
| F8 (§10) | 17 |
| F9 (§11) | 15 |
| F10 (§12) | 9 |
| F11 (§13) | 18 |
| F12 (§14) | 15 |
| F13 (§15) | 20 |
| **Total** | **222** |

### 1.9 `[NEEDS INPUT]` tags

**179 occurrences** (literal string count, per source file — see `FRD-v1.md` §18 for the full
per-section table). Every one is preserved verbatim; none promoted to a default, none invented.

### 1.10 Open `DEC-` decisions

**46 distinct `DEC-` IDs** across the thirteen parts (deduplicated per file), collected once at
`FRD-v1.md` §17. Two are marked **build-blocking** (`DEC-302`/`303`, rival-bid visibility) rather
than left to surface three separate times across §4, §8, §11.

---

## 2. Every propagation performed

### 2.1 Tractor/Trailer/Pairing entity duplication (F3 vs. F7)

**What happened.** F7 was scoped to split BRD's single "equipment" concept into independent
Tractor/Trailer/Pairing entities (F7 §2, `ENT-700`–`703`). F3, drafted after F7 in the run, *also*
independently absorbed this split natively into its own catalog (`ENT-303`–`306`), citing "Boss
scope §1" — meaning F3 read the same instruction F7 did and built the same solution under different
IDs, without either agent aware the other had done the same thing.

**Resolution.** F3's IDs are canonical (§3.2 of the FRD), because every other domain section already
references entities by `ENT-3xx`. F7's `ENT-700`–`703` are superseded, not built. F7's *requirement
content* — the full trailer-type taxonomy, temp-range/deck-height/tanker attributes, pairing and
substitution rules (F7 §2–§4, `FR-700`–`723`) — is fully preserved at FRD §9 and now applies to F3's
entities instead of F7's.

**What was not fully resolved.** F7's `ENT-704` (`DriverQualificationRecord`) was folded into F3's
`ENT-302` (`Driver`) by extending Driver's field list rather than building a second table — a
reasonable normalization call, but a call, not a discovery. F7's `ENT-705` (`Assignment`) surfaces a
real requirement (queryable assignment history independent of Trip's broader state, FR-716) that
F3's `Trip` entity does not currently satisfy; this document does not pick between the two live
resolutions (embedded `assignment_history[]` vs. reinstating `Assignment`) because neither source
agent was asked to choose between those two specific shapes. Recorded as an open schema-design item
at FRD §3.1 and §16.8.

### 2.2 `eligibility()` call-signature conflict (F6 vs. F13)

**What happened.** F6's original draft (`frd-F6-auction-engine.md` §1, FR-600) wrote the signature
as `eligibility(carrier, authority, insurance, safety_signal, truck, driver, load)` — seven
arguments. F13 (created specifically because F6 filed a `CHALLENGE` that no agent owned eligibility
computation) wrote `eligibility(carrier_id, truck_id, driver_id, load_id)` — four arguments — and
filed its own `CHALLENGE` against F6's specific line, correctly noting that F6's seven-argument form
described *what gets evaluated* (BRD A2's tuple concept), not *what gets passed in* (the actual call
surface, since F13 resolves authority/insurance/safety internally from `carrier_id`).

**Resolution.** F13's four-argument form is canonical throughout `FRD-v1.md` (§8.1, §15.1). Fixed at
three points: F6's own §8.1 text (boxed **[ASSEMBLER FIX]** note), F4's `API-468` (originally took
only `carrier_id` as a query param — under-specified even relative to F13's contract; corrected to
the full tuple), and F13's own `API-1300`/`API-1305` (already correct, cross-referenced as the
source of truth).

**Why this mattered.** No behavioural disagreement existed between the two agents — this was a
call-surface ambiguity, not a logic conflict — but shipping both files unmodified would have
produced two client implementations against two incompatible contracts for the single most
load-bearing function in the system (per `DECISIONS.md` `DEC-LOCK-001`).

### 2.3 F4/F10 duplicate event-name catalog

**What happened.** Per spine's ID-allocation rule ("every agent owns its own numeric block for every
prefix, including `EVT-`"), F4 was structurally permitted to allocate `EVT-` IDs in its own
400-499 block. But F4's own section header states "F4 owns webhook transport; F10 owns notification
content" — and then F4's draft built a full 30-event semantic catalog (`EVT-400`–`429`) naming
essentially the same lifecycle transitions F10's 49-event catalog (`EVT-1000`–`1048`) also names,
independently, with different names for several of the same transitions. F6, F7, and F13 each did
smaller versions of the same thing in their own blocks.

**Resolution.** F10's catalog adopted as canonical (§16.6 of the FRD gives the full reasoning: it is
the only one with tier/channel/quiet-hours/delivery-semantics depth, and spine explicitly assigns
"notifications, events, messaging" to F10's block). F4's 30 IDs retained per the "never reuse an ID"
rule but marked superseded, with a full per-event mapping table (§6.5 of the FRD) showing which F10
event each one corresponds to, and — critically — **which ones have no F10 equivalent at all**
(`load.amended`, `bid.withdrawn`, `pod.addendum_added`, `invoice.finalised`, general
`carrier.suspended`, general `carrier.reinstated`). Two of those gaps were closed (`EVT-1049
case.resolved`, `EVT-1050 carrier.reinstated`, both closing gaps F3's `ExceptionCase` split
explicitly created, per §2.4 below); the rest are flagged, not invented, because F10 — the domain
owner — never specified their tier/channel/persona routing and guessing that table would be
inventing a decision rather than reconciling one.

**What was not resolved.** F6's, F7's, F8's, F11's, and F13's own event lists were left in place in
their own sections rather than deleted or renumbered — deleting another agent's allocated IDs is a
larger intervention than this assembly's brief called for, and several of them (F11's ops-console
events in particular) cover a genuinely different audience (ops tooling, not persona notifications)
that F10 may never have been meant to cover. This is reported as the single worst structural problem
remaining (`FRD-v1.md` §19.3) rather than fixed, because fixing it properly requires a spine-level
rule change (one agent owns event *naming* for a given business transition, not just its own ID
block) that is outside this assembly's authority to make unilaterally.

### 2.4 F3's `ExceptionCase` split — propagated into F5, F10, F11

**What happened.** F3 accepted F11's `CHALLENGE` and moved seven state names out of
`Load.lifecycle_state` into a new `ExceptionCase` entity (`DISPUTED`/`CLOSED_UNRESOLVED`,
`CLAIM_OPEN`, `FRAUD_SUSPECTED`/`RECOVERY`, `DAMAGED`/`LOST`/`PILFERED`,
`CARRIER_SUSPENDED_IN_FLIGHT`). F3 explicitly named the downstream work in its own §3.1: "F10 must
replace the corresponding `load.state_changed` events with `case.opened`/`case.status_changed`/
`case.closed`; F11's ops queue must read `ExceptionCase` rather than scanning `Load.lifecycle_state`;
F5's state-machine error class splits into a smaller Load-transition set plus a new
ExceptionCase-transition set." F10, F11, and F5 were all drafted before this landed.

**F5 — fixed.** §7.3 of the FRD regenerates F5's Class-3 (`ERR-524`–`529`) adjacency table against
the corrected §3.3 Load state machine (the five removed target states no longer appear), and adds
`ERR-567` for the new parallel `ExceptionCase`-transition guard, exactly as F3 asked for.

**F10 — fixed, and found to need less rework than expected.** F10 never actually built a generic
`load.state_changed` event for these seven conditions — it had already, independently, named seven
specific events (`EVT-1030`–`1034`, `1036`, `1037`) that turn out to be close to the right shape for
a case-based model, just not labelled as one. The fix (§12.1a of the FRD) is a re-labelling — each
event annotated with its `ExceptionCase` `case_type` and lifecycle transition — plus two genuinely
new events to close a real gap (`EVT-1049`, `EVT-1050`, per §2.3 above).

**F11 — no fix needed.** F11 is the agent whose own `CHALLENGE` produced the `ExceptionCase` model
in the first place (`FR-1100`/`1101` explicitly require it). Its queue design (§13 of the FRD) reads
`ExceptionCase` natively; there was nothing to propagate.

### 2.5 `PERM-1300` — an ID written in the wrong agent's block

**What happened.** F13's `FR-1350` (§15.8 of the FRD) reads: "An ops reviewer (`→ F2 PERM-1300`)
may admit a carrier the gate rejected." `PERM-` is F2's prefix, allocated to block 200-299 per spine
§5's ID-allocation table; F13 owns block 1300-1399. Spine's own rule states plainly: "Never invent
another agent's ID. Write `→ F5 (errors)` in prose; the assembler resolves it." F13 wrote a
specific, wrong-block ID instead of the prose-reference form the spine requires.

**Resolution.** Corrected to `PERM-260` (§4.2 of the FRD) — a row this assembly added to F2's matrix
specifically to close this reference, scoped to `PLATFORM_CARRIER_VETTING`, `granted_case`,
dual-approved on FAIL→APPROVE override, matching F11's independently-stated requirement (`FR-1113`)
that such an override "requires a documented justification and a second, named approver."

### 2.6 F8's field-level view masks — folded into F2's matrix

**What happened.** F8 filed `CHALLENGE-800`: spine's five (now seven, with `granted_case`/
`aggregate_threshold`) scope kinds resolve *which resource* a role sees, not *how much of it* —
location is the clean example (shipper sees a corridor band, carrier dispatcher sees an exact pin,
same resource, different depth). The challenge was accepted into spine §3 as a "field-level view
mask" extension: `(role) may (action) on (resource_type) when (scope) [at (granularity)]`. F8 wrote
the granularity table (§10.6 of the FRD) but F2's own matrix — drafted in parallel — never actually
wrote the `PERM-` rows carrying that mask.

**Resolution.** `PERM-261`/`262`/`263` added to F2's matrix (§4.2), each citing F8 §6 and carrying
the `[at granularity]` suffix the spine's extension defines: `CARRIER_DISPATCHER` exact position
`own_org`; `PLATFORM_SUPPORT`/`PLATFORM_EXCEPTION_DESK` exact position `granted_case`, audited;
`CONSIGNEE_TOKEN` corridor band only, `assigned_load`, no history.

### 2.7 F11's ops-role vocabulary exposed three roles F2's matrix needed and didn't have

**What happened.** F11's own permission-shape table (§13.9 of the FRD) named `ops-senior` and
`ops-config-admin` as required roles for second-approval and auction-ruleset/eligibility-gate-policy
editing respectively. Neither exists as a named `ROLE-` in F2's taxonomy — F2's `PERM-245` referred
to the second-approval concept only informally, as "ops supervisor," and no row anywhere assigns an
owner to F6 §8.7's eleven open auction parameters or F13 §15.6's `EligibilityGatePolicy`.

**Resolution.** `ROLE-229 PLATFORM_SENIOR_REVIEWER` and `ROLE-230 PLATFORM_CONFIG_ADMIN` added to
F2's role taxonomy (§4.1), with `PERM-245` re-pointed at the new role name and `PERM-264` added for
the config-editing permission itself. `ROLE-221`'s (`PLATFORM_EXCEPTION_DESK`) scope description was
also corrected from "exception states only" (a phrase referencing Load states F3's split removed) to
"ExceptionCase (any case_type), granted_case."

### 2.8 BOL/POD merge — confirmed clean across F4, F5, F9

**What happened.** F3's `CHALLENGE` (accepted) merged `Bill of Lading` and `Delivery receipt (POD)`
into one entity (`ENT-316`) with two capture stages, per BRD `BR-514`. The assembly brief required
checking this against F4, F5, and F9 specifically.

**Finding: no conflict, one clarifying annotation added.** F4 (§6 of the FRD) already treats pickup
and delivery capture as two *API calls at different times* writing one entity's two stages, which is
correct. F5 (§7) already treats POD-related errors as guards on one entity's delivery stage,
correct. F9 (§11) has two *screens* (`SCR-923` pickup, `SCR-924` delivery) — correct UX, since two
physical moments need two interfaces — but was not explicit that both write the same entity. Added
an **[ASSEMBLER NOTE]** at each screen's row (§11.1, §11.3) stating explicitly: `SCR-923` writes
`ENT-316` `stage=origin`, `SCR-924` writes `ENT-316` `stage=delivery` — a build note preventing two
separate document tables from being built by mistake, not a substantive fix.

### 2.9 Rival-bid visibility surfaced once instead of three times

**What happened.** F6 (`DEC-302`/`303`, an open setting with a filed `CHALLENGE` that two of its
sub-options are really one), F2 (an enforceability finding that one specific combination — sealed
bidding with a live "you are winning" flag — leaks rival prices by construction, not by
implementation flaw), and F9 (`SCR-911` shipped with a conservative default and its own `CHALLENGE`
that building past that default without a locked decision risks a BR-717 violation in production)
each independently flagged this as high-priority, in three different sections, using three different
framings.

**Resolution.** Consolidated once, prominently, at `FRD-v1.md` §16.1, explicitly labelled
build-blocking. §4.4, §8.7, and §11.2 each now cross-reference §16.1 instead of re-arguing the case
in place. §16.1 also synthesizes a finding none of the three individual sections stated on its own:
F2's enforceability analysis effectively **removes one of the four combinatorial settings**
(`SEALED` + `STANDING_BEST`-as-live-flag) from the viable option set entirely, regardless of Boss's
preference, because it cannot be built leak-proof — narrowing the real decision to three options, not
four.

---

## 3. Conflicts this assembly could NOT resolve, and why

1. **`Trip` vs. a standalone `Assignment` entity** (§3.1, §16.8 of the FRD). F7's requirement for
   queryable assignment history independent of Trip's own state is real; F3's current `Trip` shape
   doesn't satisfy it. Two live resolutions exist and neither source agent was asked to choose
   between them specifically — picking one here would be inventing a schema decision, not
   reconciling a stated disagreement.

2. **The event-catalog duplication is reduced, not eliminated** (§2.3 above, §16.3/§16.6/§19.3 of
   the FRD). F10's catalog is canonical and F4's is mapped, but F6's, F7's, F8's, F11's, and F13's
   own event allocations were left in place rather than deleted or renamed, because doing so is a
   larger intervention (potentially breaking a legitimate ID a downstream integration might already
   reference) than this assembly's brief authorized. This is named as the single worst remaining
   structural problem rather than silently left unflagged.

3. **§10.8's six named-but-unnumbered F8 entities** (`PositionPing`, `Milestone`, `GeofenceZone`,
   `DwellSession`, `ETAEstimate`, `TrackingCapability`) are not in §3's 34-entity catalog. Assigning
   them `ENT-` IDs without F8's own field-level schema detail (F8's draft names them but does not
   give full field lists the way F3's other entities have) would be guessing at a structure F8 never
   fully specified, not reconciling one.

4. **Two BRD-level orphans inherited, not closed** (§16.7 of the FRD, `BRD-v1.md` §8.12): BR-106 (a
   bidder-facing payment-reliability signal with no requirement anywhere specifying what computes
   it) and BR-108 (dispute-gates-publish with no FRD requirement actually enforcing the gate). Both
   were already flagged as orphans at the BRD assembly stage; this FRD assembly confirms none of the
   thirteen FRD parts closed them, and does not invent the missing requirement to close them here.

5. **F10's ten ops-internal events with no persona-notification equivalent** (§13.10 of the FRD:
   `case.claimed`, `case.escalated`, `vetting.approved`/`.rejected`/`.held`, `fraud.classified`,
   `override.executed`, `waiver.approved`, `config.parameter_changed`, `impersonation.started`/
   `.ended`) — plausibly correctly out of scope for a *notification* catalog, but unresolved whether
   they need `EVT-` IDs for an eventual ops-side webhook or audit-log event stream.

6. **F2's own suggested word-budget cut is reported, not decided.** §16.5 of the FRD records F2's
   relayed suggestion (collapse §4.4's 18×7 visibility matrix to four viewer columns) and this
   assembly's recommendation against it, but the actual call belongs to Boss, not the assembler.

---

## 4. What no individual agent could have seen (restated from `FRD-v1.md` §19.4)

Six findings exist only in the union of two or more source files and could not have been produced by
any single agent working from its own 2,500-word block alone: the Tractor/Trailer/Pairing
double-modelling (F3+F7), the `eligibility()` signature mismatch (F6+F13), the F4/F10 event-catalog
overlap (F4+F10, and smaller instances in F6/F7/F8/F11/F13), the three missing ops roles in F2's
matrix (F2+F6+F11+F13 read together), the `PERM-1300` wrong-block reference (F13's text vs. F2's
actual block ownership), and the `AvailabilityWindow` gap (BR-214's acceptance test vs. what F3's
status-enum model and F7's duplicate-entity model each covered alone). Full detail on each is at
`FRD-v1.md` §19.4 and the corresponding numbered items above.

---

## 5. Word counts

**Total: `FRD-v1.md` = 36,652 words. `frd-assembly-report.md` (this file) ≈ 3,900 words.**

Five largest sections of `FRD-v1.md`, by word count:

| Rank | Section | Words |
|---|---|---|
| 1 | §13 — F11 Platform Admin, Ops Console & Support Tooling | 3,044 |
| 2 | §4 — Consolidated Permission Matrix (assembler-owned) | 3,001 |
| 3 | §12 — F10 Notifications, Events & Messaging | 2,963 |
| 4 | §6 — F4 API Surface & Integrations | 2,822 |
| 5 | §15 — F13 Carrier Vetting & the Eligibility Computation Service | 2,477 |

Full per-section breakdown (all 20 top-level sections):

| Section | Words |
|---|---|
| §0 Executive Summary | 628 |
| §1 Conventions inherited | 393 |
| §2 Roles and tenancy | 52 |
| §3 Consolidated Entity & State Model | 2,238 |
| §4 Consolidated Permission Matrix | 3,001 |
| §5 F1 Identity/Auth | 2,293 |
| §6 F4 API Surface | 2,822 |
| §7 F5 Error Taxonomy | 2,109 |
| §8 F6 Auction Engine | 2,349 |
| §9 F7 Driver/Equipment/HOS | 2,102 |
| §10 F8 Tracking/Telematics | 2,196 |
| §11 F9 Dashboards/Screens | 2,309 |
| §12 F10 Notifications/Events | 2,963 |
| §13 F11 Admin/Ops Console | 3,044 |
| §14 F12 Platform NFRs | 2,258 |
| §15 F13 Eligibility/Vetting | 2,477 |
| §16 Cross-Cutting Reconciliations | 1,616 |
| §17 Open Decisions Register | 684 |
| §18 `[NEEDS INPUT]` summary | 238 |
| §19 Traceability, Orphans, Closing | 597 |

**F2's content is not a standalone section** — its full matrix (originally 4,752 words, ~1.9× the
2,500-word ceiling, §16.5) lives inside §4, alongside the assembler's five added `PERM-` rows and
two added `ROLE-` rows, rather than being duplicated in a separate "F2 section." This is why §4 is
the second-largest section in the document: it is F2's full content plus the merge work, not F2's
content trimmed.

---

## 6. Note on this report's own history

This report and `FRD-v1.md` were assembled across two work sessions after the first session's
process died mid-write on an API connection error (not a content decision) partway through §11. The
coordinator's resume instructions specified writing in smaller increments rather than one oversized
call for the remainder — §12 through §19 of `FRD-v1.md`, and this entire report, were written and
independently verified (via `tail`/`wc`/header-grep after each `Edit`) as separate operations for
exactly that reason. No content from the surviving §0–§11 was rewritten; only forward-reference
section numbers within that surviving material were corrected (§16.x renumbering, §9/§10/§11/§12/
§13/§14 cross-reference fixes within the F1 section) once the full section count was known.
