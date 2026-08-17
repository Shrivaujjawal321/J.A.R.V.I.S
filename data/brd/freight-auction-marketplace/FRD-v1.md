# FRD-v1 — US Freight Reverse-Auction Marketplace

**Assembled by Jarvis (manager role) from thirteen parallel FRD parts (F1–F13), the FRD spine, the
BRD spine, `DECISIONS.md`, and `BRD-v1.md`.** This document is the functional/technical
specification the platform is built against. It supersedes the thirteen `frd-F*.md` files as the
build reference; those files remain the drafting record and are cited by section throughout.

**How this document was assembled, and what that means for how you read it.** Thirteen agents each
owned a numeric ID block (F1=100s … F13=1300s) and could not see each other's output while writing.
Three things follow from that, and all three are visible in this document rather than smoothed over:
(1) three entities (Tractor, Trailer, ExceptionCase) were independently proposed by more than one
agent and are merged here into one definition each; (2) one load-bearing function
(`eligibility()`) was specified with two different call signatures by two different agents and is
resolved here to one; (3) two agents (F4, F10) independently built a full event-name catalog for
the same state machine, which this document reconciles rather than ships as two systems of record.
Every merge, fix, and unresolved conflict is called out explicitly with an **[ASSEMBLER …]** marker
so a reader can distinguish original agent output from assembly-time work. Full detail on every
propagation and every conflict this document could not resolve is in `frd-assembly-report.md`.

**What this document does not do.** It does not invent a single number, rate limit, timeout,
retention period, threshold, or SLA that was not already in the source material — every `[NEEDS
INPUT]` tag from all thirteen parts is preserved verbatim, none promoted to a default. It does not
score itself; an independent reviewer does that separately.

---

## 0. Executive Summary

This is a US freight reverse-auction marketplace connecting shippers, asset-holding and
broker-carriers, drivers, and (for delivery only) a consignee who never holds an account. Boss's
locked design — **lowest bid wins** — is built exactly as specified, but never as "price alone": the
system checks carrier eligibility (authority, insurance, safety, equipment, driver, HOS-feasibility)
**before** ranking on price, per `DEC-LOCK-001`, and the ranking itself remains mechanical with no
human discretion inside the gate. That gate is the single most load-bearing mechanism in the entire
spec, and it very nearly shipped unowned — see §16.3.

The system is organized around four structural commitments established at the spine level and
enforced end-to-end below: **tenant isolation** beneath role-based access (a shipper must not be
able to see a competitor's freight even if an application-layer check is missing, F12 §1);
**evidentiary integrity** for the record a *Montgomery v. Caribe Transport* plaintiff or a Carmack
claimant will later subpoena (the selection record, the audit log, the BOL/POD chain — all
append-only, F3 §4-5, F12 §6); **exhaustive exception handling** as a first-class `ExceptionCase`
model rather than exceptions bolted onto the happy path (F3 §3.1, F11); and **honesty about what the
system does not know** — tracking that is "dark" says so, an ETA that is stale says so, a consignee
delivery notice that bounced says so, rather than any of them defaulting to a false-confident state
(F8, F10).

Thirteen functional domains cover: identity/auth/onboarding (F1), authorization/RBAC (F2), the
entity and state model (F3), the API surface (F4), the error taxonomy (F5), the auction engine (F6),
driver/equipment/HOS (F7), tracking/telematics/privacy (F8), dashboards and screens (F9),
notifications and events (F10), the admin/ops console (F11), platform NFRs — security, tenancy,
availability, observability, DR (F12), and carrier vetting / the `eligibility()` service (F13). F13
did not exist in the original ID allocation; it exists because F6 filed a `CHALLENGE` mid-phase when
it discovered its entire gate mechanism called a function nobody owned — the same mechanism the
challenge process worked for in the BRD phase, working again here.

**What a reader new to this project needs to know before anything else, in priority order:**

1. **§16.1 — Rival-bid visibility (`DEC-302`/`DEC-303`) is a build-blocking decision**, converged on
   independently by F6, F2, and F9. Nothing downstream should be built past the conservative default
   until Boss locks it.
2. **§16.3 — The `eligibility()` gate had no clear single owner mid-phase** and is now resolved to
   one four-argument call surface (F13's), with F6's and F4's references corrected to match.
3. **§3 — The consolidated entity/state model** merges three independently-discovered duplications
   (Tractor/Trailer, ExceptionCase, and a genuine gap — `AvailabilityWindow` — that no single agent's
   model actually covered even though F7's BR-214 requirement needs it).
4. **§4 — The permission matrix is 65 rows, not 60**, because assembling F8's field-level location
   masks and F11's ops role vocabulary into F2's matrix surfaced three roles (a second-approver tier,
   a config-admin tier, and a corrected `ExceptionCase` scope for the exception desk) that F2's own
   matrix needed but didn't have. **F2's matrix is not cut for length** despite being roughly 1.9×
   its word budget — see §16.5.
5. **§16.6 — F4 and F10 independently built two overlapping event-name catalogs** for the same state
   machine. This document adopts F10's as canonical and treats F4's as superseded; no other agent's
   individual output could have surfaced this, because F4 and F10 each only ever saw their own file.

**Two BRD defects were found downstream, during FRD drafting, and are recorded rather than silently
patched** (§16.4): BRD BR-111's equipment-type closed list omits tanker, and BRD BR-209/BR-214 model
equipment as one asset per carrier row when a tractor and a trailer are independently owned,
insured, and available. The FRD works around both; the BRD itself is not edited by this document.

---

## 1. Conventions inherited (frd-spine.md, spine.md, DECISIONS.md — not restated in full)

Full text in `frd-spine.md` and `spine.md`. Load-bearing points, because every section below assumes
them:

- **Tenancy** (frd-spine §2): `Organization(SHIPPER|CARRIER|PLATFORM)` → `Users` (one org each) →
  `Roles` (scoped). Every resource belongs to an Organization. The Receiver/Consignee has **no
  account** — every consignee interaction is a tokenised, single-purpose, expiring capability link,
  never a login (this is non-negotiable and touches §5.8, §4.1 ROLE-240, §11.4, §12.2/§12.4).
- **Permission primitive** (frd-spine §3): `(role) may (action) on (resource_type) when (scope)`.
  Scope kinds, **closed set**: `own_org · own_site · assigned_load · eligible_load · platform_wide ·
  granted_case · aggregate_threshold`. The last two were added mid-phase by accepted challenges (F2's
  `granted_case`, F12's `aggregate_threshold`) — both are in the current spine and both are used
  throughout §4. **Field-level view masks** are a third, later accepted extension (F8's
  `CHALLENGE-800`): `(role) may (action) on (resource_type) when (scope) [at (granularity)]` —
  enforced at the data layer, never the serializer.
- **API conventions** (frd-spine §4): `/v1` base, idempotency keys on mutating calls, cursor
  pagination, trace id per response, one canonical error envelope, events named
  `<entity>.<past_tense_event>`.
- **ID allocation** (frd-spine §5): each agent owns a fixed numeric block per prefix, F1=100s through
  F13=1300s. **No collisions occurred** in the raw drafts — every conflict found during assembly (§3,
  §16) is a *duplicate concept under two different IDs*, or a *reference to an ID in the wrong
  agent's block* (§16.3's PERM-1300 case), never two agents claiming the same number.
- **Lifecycle** (`spine.md` §3, reconciled to 24 states in `BRD-v1.md` §7.4, further reconciled here
  in §3.3 to reflect F3's `ExceptionCase` split): the happy path is
  `DRAFT → PUBLISHED → AUCTION_OPEN → AUCTION_CLOSED → AWARDED → AWARD_ACCEPTED → PICKUP_SCHEDULED →
  AT_PICKUP → PICKED_UP → IN_TRANSIT → AT_DROP → DELIVERED → POD_CAPTURED → INVOICE_ISSUED →
  INVOICE_FINALISED → SETTLED → COMPLETED`.
- **`DEC-LOCK-001`** (`DECISIONS.md`): lowest bid wins **inside** a carrier-eligibility gate applied
  first. Not price-only; price decides only among carriers that cleared the gate. Grounded in
  *Montgomery v. Caribe Transport II* (2026) removing the FAAAA preemption defence for
  negligent-selection claims, and in Convoy's own operating history of never awarding on price alone.
- **`DEC-LOCK-002`**: Boss's existing US truck-data platform is an available asset, gated by an
  enforceable architectural rule — ODbL-sourced layers (`osm.*`) are Produced-Works-only and never
  cross the API boundary (F4 §2 "not built, on purpose"; F12 §7; F8 INT-803).

---

## 2. Roles and tenancy — as inherited, not re-derived

Six roles at the BRD level (`spine.md` §1): Shipper, Carrier–asset-holder, Carrier–broker/agent,
Receiver/Consignee (no account), Platform/Operator, Driver. F1 and F2 expand these into an
authentication-assurance framework (F1 §1) and a full role taxonomy (F2 §2.1, 24 `ROLE-` records,
consolidated at §4.1 below).

---

## 3. Consolidated Entity & State Model — assembler-owned

**This section is owned by the assembler per frd-spine §9; no drafting agent wrote it.** It merges
F3's entity catalog (the base), F7's tractor/trailer split (already independently absorbed into F3's
own draft — see §3.1), F13's eligibility entities (additive, no overlap), and F11's `ExceptionCase`
challenge (accepted by F3 itself, §3.3 below is F3's own reconciliation, reproduced as the
canonical state model).

### 3.1 Entity catalog — one catalog, 34 entities, duplicates resolved

**Finding.** F3 and F7 independently modelled `Tractor`, `Trailer`, and their pairing. This was not
visible to either agent: F7 was told to split equipment (§3.1.1 below) and did so under its own IDs
`ENT-700`–`ENT-706`; F3, drafted slightly later in the run, *also* absorbed the split, natively,
under its own IDs `ENT-303`–`ENT-306`. Both are internally consistent; keeping both would silently
build two tables for one asset. **Resolution: F3's IDs are canonical** (they sit in F3's
entity-of-record catalog, which every other domain already references by `ENT-3xx`). F7's
`ENT-700`–`ENT-703` are **superseded, not built** — F7's *field content and requirements* (equipment
taxonomy detail, temp-range/deck-height/tanker attributes, pairing/substitution rules — F7 §2–§4) are
retained in full at §9 (F7's own section) and apply to F3's `ENT-303`/`ENT-304`/`ENT-305`, they are
just no longer separate entities.

| F7 ID (superseded) | F3 ID (canonical) | Disposition |
|---|---|---|
| `ENT-700` Driver | `ENT-302` Driver | Same entity. F3's field list is extended below with F7's richer qualification fields (F7 §5), which F3's one-line description under-specified. |
| `ENT-701` TractorAsset | `ENT-303` Tractor | Same entity, same fields. |
| `ENT-702` TrailerAsset | `ENT-304` Trailer | Same entity, same fields. |
| `ENT-703` EquipmentPairing | `ENT-305` Tractor-Trailer Pairing | Same entity, same fields (`tractor_id, trailer_id, valid_from, valid_to`). |
| `ENT-704` DriverQualificationRecord | *(folded into `ENT-302`)* | **[ASSEMBLER DECISION]** F7 wanted this as a separate normalized row; F3 already inlines CDL/clearinghouse fields on `Driver`. Rather than build a redundant table, `ENT-302` is extended below with F7's full field list (endorsements, medical-cert expiry, per-field verifier-type + verified-at, FR-735). If a future normalization need arises (e.g. multiple historical qualification snapshots per driver), F7's original framing is the fallback — noted, not built. |
| `ENT-705` Assignment | *(folded into `ENT-314` Trip, with a flagged gap)* | **Not fully resolved — see the unresolved-conflict note below.** |
| `ENT-706` AvailabilityWindow | `ENT-325` AvailabilityWindow (new) | **Genuine gap in F3's model, not previously duplicated — added, see §3.1.2.** |

**Unresolved conflict [could not fully resolve — recorded per hard rule].** F7 requires "Assignment
state queryable independent of load state... e.g. `IN_TRANSIT` load, mid-trip-relayed Assignment"
(F7 FR-716) and substitution logged with requester/reason distinct from the award record (F7
FR-715). F3's `ENT-314` Trip already carries `assigned_driver/tractor/trailer_id` but as *current
values on one Trip row*, not a queryable history of bindings. F7's need is real (a relay mid-trip
must be reconstructable — who was assigned before and after, and when) and F3's `StateTransitionLog`
(F3 §4) partially covers it generically but was not designed with Assignment's specific shape in
mind. **This document does not invent the resolution.** The two live options — (a) `Trip` carries an
embedded `assignment_history[]` array (leg_no, driver_id, tractor_id, trailer_id, bound_at,
unbound_at, reason), or (b) `Assignment` is reinstated as its own entity with a foreign key to
`Trip` — are both consistent with everything else in this document and the choice is a schema-design
call that neither F3 nor F7 was positioned to make alone. Flagged for the build phase, not decided
here.

#### 3.1.1 The equipment-split challenge, restated for the record

F7's `CHALLENGE` (F7 §2): BRD `BR-209`/`BR-214` model equipment as one asset per carrier row, and
`BR-111`'s closed equipment-type list omits **tanker**. F3 accepted the split structurally
(`ENT-303`/`304`/`305`/`306`); this document accepts it too, and treats both BRD gaps as **findings
against the BRD, not corrections made to it** — see §16.4.

#### 3.1.2 `ENT-325` — AvailabilityWindow (new, assembler-added)

| Field | Note |
|---|---|
| `owner_type` | `DRIVER \| TRACTOR \| TRAILER` |
| `owner_id` | FK, polymorphic |
| `window_start`, `window_end` | The committed/unavailable interval |
| `committed_load_id` | Nullable — set when the window is a load commitment, null for self-declared unavailability |
| `source` | `LOAD_COMMITMENT \| SELF_DECLARED \| MAINTENANCE_HOLD` |

**Why this exists.** BR-214 requires detecting *overlapping-window* double-commitment ("An asset
committed to Load A (Mon 08:00–Wed 14:00) is not eligible for an overlapping Load B, but is eligible
for Load C starting Wed 18:00" — `BRD-v1.md` BR-214 acceptance test). F3's `ENT-303`/`ENT-304` model
availability as a **current status enum** (`AVAILABLE|COMMITTED|OUT_OF_SERVICE|MAINTENANCE`) — a
single current value, which cannot answer "is this asset free for a *specific future* window," only
"what is it doing *right now*." F7 independently required exactly this as `ENT-706`
`AvailabilityWindow` (F7 §1, §4 FR-720). Neither F3 alone nor F7 alone fully closed the gap: F3
didn't build the windowed structure BR-214's own acceptance test requires; F7 built it but under a
duplicate-entity framing that also redefined Driver/Tractor/Trailer. **This is a case where the
correct answer used pieces from both documents and neither document's literal proposal.**

### 3.2 Full consolidated entity catalog (34 entities)

The 25 base entities are F3's `ENT-300`–`ENT-324`, reproduced in full below with `ENT-302` extended
per §3.1's fold-in. `ENT-325` is new (§3.1.2). `ENT-1300`–`ENT-1307` are F13's, additive, no overlap.

| ID | Entity | Core fields & relationships | Trace |
|---|---|---|---|
| ENT-300 | Organization | org_type(SHIPPER\|CARRIER\|PLATFORM), broker_flag, verification_status, standing_status | BR-100/203 |
| ENT-301 | User | org_id, contact, role_set(→§4), account_type(STANDARD\|DRIVER) | BR-900/901 |
| ENT-302 | Driver | **[extended]** 1:1 User ext.: cdl_number/class/state/status, endorsements[] (H/N/T/combo, 383.93), medical_cert_expires_at, clearinghouse_attestation(status+attested-at only, never raw result), employment_type; every qualification field carries verifier_type(self\|carrier\|platform-doc-check\|third-party) + verified_at (folds in F7 ENT-704/FR-730–735) | BR-210/707/709/903, F7 §5 |
| ENT-303 | Tractor | carrier_org_id, VIN, plate, status(AVAILABLE\|COMMITTED\|OUT_OF_SERVICE\|MAINTENANCE), authority_ref, insurance_doc_ref | BR-209/214/215 |
| ENT-304 | Trailer | carrier_org_id, unit_no, equipment_type_id(FK 306), status, insurance_doc_ref. No FK to a tractor — pairing is separate (ENT-305) | Boss scope §1; BR-214 |
| ENT-305 | Tractor-Trailer Pairing | tractor_id, trailer_id, valid_from, valid_to(null=current) | Boss scope §1; BR-214 |
| ENT-306 | Equipment Type | code(DRY_VAN\|REEFER\|FLATBED\|STEP_DECK\|TANKER\|POWER_ONLY\|… open set), temp_range_required, attribute_set(json) | BR-111/112 — see §16.4 |
| ENT-307 | Load/Shipment | shipper_org_id, posting_user_id, lifecycle_state(§3.3), site_from/to, current_declaration_id, supersedes_load_id(nullable), legal_hold(bool) | BR-100-156 |
| ENT-308 | Declaration Snapshot | load_id, version_no, content(commodity, weight, equipment_type, dimensions, hazmat_flag, declared_value, appointment windows, addresses), immutable, superseded_by | BR-121/122/136 |
| ENT-309 | Auction | load_id, declaration_snapshot_id(frozen at open), opens_at, closes_at, state(§3.3), pool_size, bid_count | BR-301-318 |
| ENT-310 | Bid | auction_id, carrier_org_id, tractor_id, trailer_id, driver_id(optional), price, submitted_at, withdrawn_at, gate_result_ref, status(ACTIVE\|WITHDRAWN\|EXCLUDED\|WINNING) | BR-301/304/307/308 |
| ENT-311 | Award | auction_id, winning_bid_id, awarded_org_id, state(§3.3), selection_record_id | BR-303/304 |
| ENT-312 | Selection Record | award_id, gate_version, every_bid[], excluded[], authority/insurance/safety_snapshot_refs, decided_by. Append-only | BR-303/706 |
| ENT-313 | Rate Confirmation | award_id, base_linehaul_rate, fsc_method_ref, accessorial_table_ref, carrier_acknowledged_at | BR-600 |
| ENT-314 | Trip | award_id, load_id, assigned_driver/tractor/trailer_id, state, current_custody_holder. **[flagged gap]** assignment history not yet structured — §3.1 | BR-212/910 |
| ENT-315 | Custody Event | trip_id, event_type(TENDER_PICKUP\|TRANSLOAD\|DELIVERY\|RETURN_TO_ORIGIN), prev_event_id, from/to_holder, condition_notes_ref, acknowledged_by[], observed_at, recorded_at | BR-400/402/403 |
| ENT-316 | **Bill of Lading** (merged BOL+POD) | load_id, trip_id, origin_capture(count, weight, condition, seal, dual signature, both timestamps), delivery_capture(clear\|exception, OS&D notation[], signer name/role, both timestamps — null until drop), addenda[], concealed_damage_reports[]. **One entity, two stages** — see §3.4 | BR-500-514 |
| ENT-317 | Invoice | load_id, rate_confirmation_id, revenue_model(A\|B\|C). Header status = computed rollup of lines | BR-600/601/614 |
| ENT-318 | Invoice Line | invoice_id, line_type, amount, evidence_ref, status(ISSUED\|HELD\|FINALISED\|CREDITED), held_reason_ref, credit_note_ref | BR-601-604 |
| ENT-319 | Claim | load_id, bol_id, type(CARGO_LOSS\|DAMAGE\|SHORTAGE\|TONU\|DETENTION…), filed_at, amount_asserted, status, disallowance_notice_ref, next_obligation_due_at. Detail body of an ExceptionCase, case_type=CARGO_CLAIM | BR-807-809/821 |
| ENT-320 | Dispute | subject_type(FREIGHT\|MONEY), related_ref, raised_by, status(OPEN\|CLOSED_UNRESOLVED\|RESOLVED), evidence_owner. Detail body of an ExceptionCase, case_type=DISPUTE_FREIGHT\|MONEY | BR-811 |
| ENT-321 | Document | owner_type(ORG\|DRIVER\|TRACTOR\|TRAILER), owner_id, doc_type(AUTHORITY\|COI\|CDL\|PERMIT\|W9\|NOA…), issuer, expires_at, verification_status/source | BR-204/209/606/612 |
| ENT-322 | Rating | load_id(completed only), rater_org_id, ratee_org_id, objective_event_refs[], stars(gated, DEC-330) | BR-815/816 |
| ENT-323 | Notification | event_ref, recipient_type(USER\|OUT_OF_BAND_CONSIGNEE), channel, delivery_status | BR-912; catalog owned by §12 (F10) |
| ENT-324 | **Exception Case** | load_id(FK, not unique), case_type(FRAUD_REVIEW\|CARGO_INTEGRITY\|CARGO_CLAIM\|DISPUTE_FREIGHT\|DISPUTE_MONEY\|CARRIER_ENFORCEMENT_COLLISION), status(OPEN\|IN_REVIEW\|RECOVERY_IN_PROGRESS\|RESOLVED\|CLOSED_UNRESOLVED), owner_role, opened_at, closed_at, detail_ref, evidence_refs[] | F11 challenge, accepted — §3.3 |
| **ENT-325** | **AvailabilityWindow** (new) | owner_type(DRIVER\|TRACTOR\|TRAILER), owner_id, window_start, window_end, committed_load_id(nullable), source(LOAD_COMMITMENT\|SELF_DECLARED\|MAINTENANCE_HOLD) | BR-214, F7 FR-720 — §3.1.2 |
| ENT-1300 | CarrierVettingRecord | Per carrier org; role, onboarding status, suspension state | F13 §2 |
| ENT-1301 | OperatingAuthorityRecord | MC/USDOT, status, checked-at, authority-granted-date | BR-202 |
| ENT-1302 | InsurancePolicyRecord | COI, certificate-holder=platform, coverage, limits, expiry, per-equipment binding | BR-204 |
| ENT-1303 | SafetySignalRecord | Safety rating + CSA/SMS BASIC snapshot, refreshed-at | BR-205 |
| ENT-1304 | CredentialDocument | Authority cert, COI, W-9, ID doc — submitted→verified→expiring→expired/revoked | — |
| ENT-1305 | EligibilityGatePolicy | Versioned, effective-dated ruleset: hard-gate elements, thresholds, tiering | §16.3, DEC-201 |
| ENT-1306 | EligibilityEvaluation | `eligibility()` output + full input snapshot; append-only | §16.3 |
| ENT-1307 | IdentityMismatchSignal | F13 §7 output; consumed by A8/F11, never self-classified | BR-225 |

### 3.3 Consolidated state machine

**Load lifecycle** — inherited from `BRD-v1.md` §7.4 (24-state canonical table), **with F3's
`ExceptionCase` split applied** (F3 §3.1, accepted from F11's `CHALLENGE`). The BRD's 24-state table
included five conditions that are **not** mutually-exclusive states of one thread and are moved to
the `ExceptionCase` model instead:

| Removed from Load.lifecycle_state | → case_type on ExceptionCase | Why |
|---|---|---|
| `DISPUTED` / `CLOSED_UNRESOLVED` | `DISPUTE_FREIGHT` \| `DISPUTE_MONEY` | Content about the load, not a state of it — mirrors A5's already-accepted OS&D reasoning (`BRD-v1.md` §7.4) |
| `CLAIM_OPEN` | `CARGO_CLAIM` | Already had its own entity/status (`ENT-319` Claim) — never truly single-valued |
| `FRAUD_SUSPECTED` / `RECOVERY` | `FRAUD_REVIEW` | A status change inside one case, not two Load states |
| `DAMAGED` / `LOST` / `PILFERED` | `CARGO_INTEGRITY` | A fact discovered about freight, worked independently of the load's own execution state |
| `CARRIER_SUSPENDED_IN_FLIGHT` | `CARRIER_ENFORCEMENT_COLLISION` | A party-level action (`Organization.status`), not a load fact |

**Test that governs the split** (F3): a *state* is a mutually-exclusive condition of the load's one
thread; a *case* is work opened **about** the load, coexisting with any state or other case.
Multiple `ExceptionCase`s may be open on one Load simultaneously (a fraud case and a detention
dispute at once — the exact scenario a single-valued state field cannot represent).

**Remaining Load state adjacency (regenerated per F3 FR-351's instruction — this is the corrected
version of F5's Class-3 table, §7.3 below):**

```
DRAFT → {PUBLISHED}
PUBLISHED → {AUCTION_OPEN, CANCELLED_BY_SHIPPER}
AUCTION_OPEN → {AUCTION_EXTENDED, AUCTION_CLOSED, AUCTION_FAILED_NO_ELIGIBLE_CARRIER, CANCELLED_BY_SHIPPER}
AUCTION_CLOSED → {AWARD_PENDING, AUCTION_FAILED_NO_BIDS, AUCTION_FAILED_ALL_ABOVE_LIMIT}
AWARD_PENDING → {AWARDED, AWARD_VOIDED_INELIGIBLE}
AWARDED → {AWARD_ACCEPTED, AWARD_DECLINED, AWARD_LAPSED}
AWARD_ACCEPTED → {PICKUP_SCHEDULED, CANCELLED_BY_SHIPPER}
PICKUP_SCHEDULED → {AT_PICKUP, CARRIER_NO_SHOW, CANCELLED_BY_SHIPPER}
AT_PICKUP → {PICKED_UP, SHIPPER_NOT_READY, PICKUP_REFUSED}
PICKED_UP → {IN_TRANSIT}
IN_TRANSIT → {AT_DROP, TRANSIT_EXCEPTION, CANCELLED_BY_SHIPPER(charged)}
AT_DROP → {DELIVERED, PARTIAL_DELIVERY, DELIVERY_REFUSED, DELIVERY_ATTEMPTED_NO_RECEIVER}
DELIVERED → {POD_CAPTURED}
POD_CAPTURED → {INVOICE_ISSUED}
INVOICE_ISSUED → {INVOICE_FINALISED}
INVOICE_FINALISED → {SETTLED}
SETTLED → {COMPLETED}
RETURN_TO_ORIGIN ← post-refusal (PICKUP_REFUSED, DELIVERY_REFUSED)
```

**[ASSEMBLER FIX]** Compare against F5's original §3 (drafted before F3's ExceptionCase split
landed): F5's `IN_TRANSIT` target set included `DAMAGED/LOST/PILFERED, FRAUD_SUSPECTED,
CARRIER_SUSPENDED_IN_FLIGHT`; its `DELIVERED` target set included `CLAIM_OPEN`; and it noted
`DISPUTED` "reachable from any state." All three are removed above, per F3's own explicit
instruction that F5 "gets a smaller Load-transition set plus a new ExceptionCase-transition set."

**New — `ExceptionCase` transition set** (assembler-added, closing the gap F3's FR-351 named but
F5 could not generate because it was written before F3's split existed):

```
(none) → OPEN                              [any case_type, trigger varies — see F11 §1-3]
OPEN → {IN_REVIEW, RECOVERY_IN_PROGRESS, RESOLVED, CLOSED_UNRESOLVED}
IN_REVIEW → {RECOVERY_IN_PROGRESS, RESOLVED, CLOSED_UNRESOLVED}
RECOVERY_IN_PROGRESS → {RESOLVED, CLOSED_UNRESOLVED}
```

Opening triggers per `case_type`, consolidated from F11 §1–§3 and F3 §3.1: `FRAUD_REVIEW` ← BR-221/
224 arrival mismatch, BR-814 anomaly, BR-228 contact change, BR-812 remit change (F11 FR-1117);
`CARGO_INTEGRITY` ← damage/loss/pilferage discovered at any custody state; `CARGO_CLAIM` ← BR-807
claim filed; `DISPUTE_FREIGHT`/`DISPUTE_MONEY` ← raised at any Load state; `CARRIER_ENFORCEMENT_
COLLISION` ← a Trip bound to an org whose `Organization.status` transitions to `SUSPENDED`.

**Auction sub-machine** — unchanged, F6's own (F6 header): `AUCTION_OPEN → AUCTION_EXTENDED →
AUCTION_CLOSED → AWARD_PENDING → AWARD_ACCEPTED / AWARD_DECLINED / AWARD_LAPSED /
AWARD_VOIDED_INELIGIBLE`; terminal: `AUCTION_FAILED_NO_BIDS`, `AUCTION_FAILED_NO_ELIGIBLE_CARRIER`,
`AUCTION_FAILED_ALL_ABOVE_LIMIT`.

### 3.4 BOL/POD merge — confirmed, checked against downstream sections

**F3's `CHALLENGE` (accepted, §3.2 above):** spine §2 listed `Bill of Lading` and `Delivery receipt
(POD)` as two entities; BRD `BR-514` requires "one continuous, linked document chain, not two
independent records." `ENT-316` merges them — POD is the delivery-signed *stage* of the same
document, not a sibling row.

**Checked against F4, F5, F9 per the assembly brief's explicit instruction:**
- **F4** (§6 below) uses `/v1/trips/{id}/pod` and `/v1/documents` as separate *endpoints*, which is
  correct — pickup-stage capture (a document upload/custody event) and delivery-stage capture (a
  structured POD submission) are different **API calls at different times**, not different
  **entities**. Both write to `ENT-316`'s two stages (`origin_capture`, `delivery_capture`). No
  change needed; confirmed consistent.
- **F5** (§7 below) treats `POD_PRECONDITION_NOT_MET`, `POD_ALREADY_CAPTURED`,
  `CUSTODY_PRECONDITION_NOT_MET` as guards on `ENT-316`'s delivery_capture stage. Consistent, no
  change needed.
- **F9** (§11 below) has two *screens* — `SCR-923` (Document Capture, pickup) and `SCR-924` (POD
  Capture, delivery) — which is correct UX (two physical moments need two screens) but was not
  explicit that both write the *same* entity's two stages. **[ASSEMBLER ADDITION]** noted at §11:
  `SCR-923` and `SCR-924` both write `ENT-316`, `stage=origin` and `stage=delivery` respectively —
  a build note to prevent two separate document tables being built by mistake.

No conflict found beyond that clarifying note; the merge holds cleanly across all three consumers.

---

## 4. Consolidated Permission Matrix — assembler-owned

**Base document: F2 (`frd-F2-authorization-rbac.md`), reproduced in full below** — F2's matrix is
the security specification for this system and is **not cut for length** (§16.5 explains why, and
what F2's own suggested cut would have removed). Additions from F8 (field-level view masks), F11
(ops role vocabulary — which exposed three roles F2's matrix needed but didn't have), and F13 (the
`PERM-1300` fix) are marked **[ASSEMBLER ADDITION]** inline.

### 4.1 Role taxonomy (F2 §2.1, extended)

A **role** is a record `(user, role, scope binding, granted_by, granted_at, expires_at?)`. A
grantable capability is a **role variant**, `ROLE[+CAP]`. Four org shapes: SHIPPER, CARRIER
(asset-holder), CARRIER (broker-flagged), PLATFORM.

| ID | Role | Org type | Default scope | Note |
|---|---|---|---|---|
| ROLE-200 | `SHIPPER_ORG_ADMIN` | SHIPPER | `own_org` | Users, sites, grants; only role that may cancel post-award |
| ROLE-201 | `SHIPPER_LOAD_POSTER` | SHIPPER | `own_site` | Publishes for its site(s); BR-901 |
| ROLE-202 | `SHIPPER_VIEWER` | SHIPPER | `own_org`/`own_site` | Read-only everywhere |
| ROLE-203 | `SHIPPER_BILLING` | SHIPPER | `own_org` | Invoices, disputes; no load mutation |
| ROLE-204 | `SHIPPER_CLAIMS_CONTACT` | SHIPPER | `own_org` | Claim raise/track; BR-906 relay point |
| ROLE-210 | `CARRIER_OWNER` | CARRIER | `own_org` | Authority holder; inherently `+BID` and `+ACCEPT_AWARD`; sole payee-of-record authority (BR-909) |
| ROLE-211 | `CARRIER_DISPATCHER` | CARRIER | `own_org` | Bids only with `+BID`; accepts only with `+ACCEPT_AWARD` |
| ROLE-212 | `CARRIER_ACCOUNTING` | CARRIER | `own_org` | Invoices, settlement; **never** bid/accept/payee |
| ROLE-213 | `CARRIER_COMPLIANCE` | CARRIER | `own_org` | Uploads authority/COI/CDL; no commercial authority |
| ROLE-214 | `CARRIER_DRIVER` | CARRIER | `assigned_load` | Mobile-only; sees nothing unassigned |
| ROLE-215 | `CARRIER_AGENT` | CARRIER | `own_org`, time-boxed | External delegate via grant, not membership |
| ROLE-216 | `OWNER_OPERATOR` | CARRIER | `own_org` + `assigned_load` | Union of ROLE-210 and ROLE-214, nothing more |
| ROLE-220 | `PLATFORM_SUPPORT` | PLATFORM | `granted_case` | Read-only + view-as; no state override |
| ROLE-221 | `PLATFORM_EXCEPTION_DESK` | PLATFORM | `granted_case` | **[ASSEMBLER FIX]** Scope updated from "exception states only" to **`ExceptionCase` (any `case_type`), `granted_case`** — F2's original wording referenced Load *states* that F3's split (§3.3) removed. No bids, awards or money. |
| ROLE-222 | `PLATFORM_FRAUD_REVIEWER` | PLATFORM | `platform_wide` read, `granted_case` write | Suspend/flag; cannot approve a carrier or settle money |
| ROLE-223 | `PLATFORM_CARRIER_VETTING` | PLATFORM | `platform_wide` | Sole onboarding approver (BR-908); exclusive of ROLE-225 |
| ROLE-224 | `PLATFORM_CLAIMS_DESK` | PLATFORM | `granted_case` | Settles/disallows claims, maker-checker |
| ROLE-225 | `PLATFORM_BILLING_OPS` | PLATFORM | `granted_case` | *Requests* waivers; never approves its own |
| ROLE-226 | `PLATFORM_ADMIN` | PLATFORM | `platform_wide` | Identity administration **only** — no business-object mutation |
| ROLE-227 | `PLATFORM_AUDITOR` | PLATFORM | `platform_wide` | Read-only by definition |
| ROLE-228 | `PLATFORM_AWARD_OVERRIDE` | PLATFORM | `granted_case`, time-boxed | Break-glass re-award; dual-approved, disclosed to both orgs |
| **ROLE-229** | **`PLATFORM_SENIOR_REVIEWER`** *(new)* | PLATFORM | `granted_case` + segregation-of-duty | **[ASSEMBLER ADDITION]** F11's "ops-senior" (F11 §9: "second-approve waiver/reinstatement/gate-override") formalizes what F2's own `PERM-245` referred to only informally as "ops supervisor." F2's matrix needed this role and didn't name it — added here, actor must ≠ original requester on every use. |
| **ROLE-230** | **`PLATFORM_CONFIG_ADMIN`** *(new)* | PLATFORM | `platform_wide` | **[ASSEMBLER ADDITION]** F11's "ops-config-admin" (F11 FR-1142/1145: auction ruleset + eligibility-gate-policy authoring, "distinct from ops-vetting-reviewer"), and F13's `EligibilityGatePolicy` authoring (F13 API-1306, vaguely "admin-scoped"), and F6's eleven open auction parameters (F6 §7) — none of the three had a named owner in F2's original role list. Distinct from `PLATFORM_ADMIN` (ROLE-226, identity-only) and `PLATFORM_CARRIER_VETTING` (ROLE-223, per F11 FR-1145's explicit segregation requirement: "no reviewer loosens the gate they themselves operate under"). |
| ROLE-240 | `CONSIGNEE_TOKEN` | *no org/account* | `assigned_load` | Single-load, single-purpose, expiring link |
| ROLE-241 | `DRIVER_DEVICE` | CARRIER-bound | `assigned_load` | Driver with no login; POD capture principal |
| ROLE-242 | `FACTOR_PAYEE` | *no account* | — | Notification target only `[NEEDS INPUT: factor portal wanted?]` |

### 4.2 The permission matrix (F2 §2.2, 60 rows, + 5 assembler additions = 65)

Shape: `(role) may (action) on (resource_type) when (scope)`.

| PERM | Role | may (action) | on (resource_type) | when (scope) | Trace |
|---|---|---|---|---|---|
| PERM-200 | `SHIPPER_LOAD_POSTER` | create, amend (pre-bid) | `load_draft` | `own_site` | BR-101/135 |
| PERM-201 | `SHIPPER_LOAD_POSTER` | publish | `load` | `own_site` | BR-901/130 |
| PERM-202 | `SHIPPER_ORG_ADMIN` | publish, amend | `load` | `own_org` | BR-901 |
| PERM-203 | `SHIPPER_LOAD_POSTER` | cancel (pre-award only) | `load` | `own_site` + own-authored | BR-904/140 |
| PERM-204 | `SHIPPER_ORG_ADMIN` | cancel (any pre-pickup state) | `load` | `own_org` | BR-904/141/142 |
| PERM-205 | *no role* | cancel | `load` in/after `PICKED_UP` | — | BR-144 — action does not exist |
| PERM-206 | `SHIPPER_VIEWER` | read | `load`, `bid_summary`, `award` | `own_org`/`own_site` | BR-901 |
| PERM-207 | `SHIPPER_ORG_ADMIN` | read, decide | `bid` (all bids on own load) | `own_org` | BR-303 |
| PERM-208 | `SHIPPER_ORG_ADMIN` | create, revoke | `role_grant` (shipper roles) | `own_org` | NFR-901 |
| PERM-209 | `SHIPPER_ORG_ADMIN` | create, deactivate | `user`, `site` | `own_org` | BR-103 |
| PERM-210 | `SHIPPER_BILLING` | read, dispute | `invoice` | `own_org` | 9.3.2 |
| PERM-211 | `SHIPPER_CLAIMS_CONTACT` | create, read, respond | `claim` | `own_org` | BR-807 |
| PERM-212 | `SHIPPER_*` | read | `tracking_position` | `assigned_load` (own load, post-pickup) **[at `corridor_band`]** | §4.4, F8 §6 |
| PERM-213 | `SHIPPER_ORG_ADMIN` | read | `pod`, `bol`, `selection_record` | `own_org` | BR-802/809 |
| PERM-214 | `CARRIER_OWNER` \| `CARRIER_DISPATCHER[+BID]` | read (bid view) | `load` | `eligible_load` | BR-301 |
| PERM-215 | `CARRIER_OWNER` \| `CARRIER_DISPATCHER[+BID]` | create, withdraw (per policy) | `bid` | `eligible_load` | BR-301/308 |
| PERM-216 | `CARRIER_ACCOUNTING`, `CARRIER_DRIVER`, `CARRIER_COMPLIANCE` | create | `bid` | — | denied always |
| PERM-217 | `CARRIER_OWNER` \| `CARRIER_DISPATCHER[+ACCEPT_AWARD]` | accept, decline | `award` | `own_org` | BR-902/905 |
| PERM-218 | `CARRIER_DISPATCHER[+BID]` (no accept grant) | accept | `award` | — | denied — BR-902 acceptance test |
| PERM-219 | `CARRIER_OWNER` \| `CARRIER_DISPATCHER` | create, change | `assignment` (driver + truck) | `assigned_load` | BR-910 → §9 (F7) |
| PERM-220 | `CARRIER_OWNER` | create, revoke | `role_grant` (incl. `+BID`, `+ACCEPT_AWARD`) | `own_org` | BR-900 |
| PERM-221 | `CARRIER_OWNER` | set | `payee_of_record` | `own_org` | BR-909 |
| PERM-222 | `CARRIER_DISPATCHER`, `CARRIER_ACCOUNTING` | set | `payee_of_record` | — | denied — BR-909 acceptance test |
| PERM-223 | `CARRIER_COMPLIANCE` \| `CARRIER_OWNER` | upload, replace | `document` | `own_org` | BR-804 |
| PERM-224 | `CARRIER_ACCOUNTING` \| `CARRIER_OWNER` | read, dispute | `invoice`, `payment` | `own_org` | — |
| PERM-225 | `CARRIER_OWNER` \| `CARRIER_ACCOUNTING` | create, respond | `claim` | `own_org` | BR-807 |
| PERM-226 | `CARRIER_DRIVER` \| `DRIVER_DEVICE` | read (execution view) | `load` | `assigned_load` | BR-910 |
| PERM-227 | `CARRIER_DRIVER` \| `DRIVER_DEVICE` | capture, sign | `pod`, `bol_exception` | `assigned_load` | BR-903 |
| PERM-228 | `CARRIER_DRIVER` | read | `bid`, `invoice`, `rate_confirmation` amount | — | denied — `[ASSUMPTION: rate withheld from driver by default \| conf: med]` |
| PERM-229 | `CARRIER_DISPATCHER` | sign | `pod` | — | denied — dispatcher may only record a *carrier attestation*, distinctly typed |
| PERM-230 | `CARRIER_*` | read | `load` | any load not `eligible_load` / not `assigned_load` | denied → **not-found** |
| PERM-231 | `CONSIGNEE_TOKEN` | read (delivery view), submit exception note | `load`, `bol_exception` | `assigned_load` **[at `corridor_band`, position only]** | BR-906/912, F8 §6 |
| PERM-232 | `CONSIGNEE_TOKEN` | read | `bid`, `invoice`, `award`, `carrier commercials` | — | denied always |
| PERM-233 | `PLATFORM_SUPPORT` | read | `load`, `award`, `claim`, `invoice` | `granted_case` | BR-813 |
| PERM-234 | `PLATFORM_SUPPORT` | start (read-only view-as) | `impersonation_session` | `granted_case` | FR-212 |
| PERM-235 | `PLATFORM_SUPPORT` | write anything as another org | any | — | denied always |
| PERM-236 | `PLATFORM_EXCEPTION_DESK` | claim, work, transition status | `exception_case` | `granted_case` | BR-913, F3 §3.1 — **[wording fixed]** |
| PERM-237 | `PLATFORM_EXCEPTION_DESK` | create, amend, withdraw | `bid`, `award`, `invoice` | — | denied always |
| PERM-238 | `PLATFORM_FRAUD_REVIEWER` | read | `bid`, `award`, `selection_record`, `org` | `platform_wide` | BR-814/815 |
| PERM-239 | `PLATFORM_FRAUD_REVIEWER` | suspend, flag | `organization`, `user` | `granted_case` | BR-817/818 |
| PERM-240 | `PLATFORM_CARRIER_VETTING` | approve, reject | `carrier_application` | `platform_wide` | BR-908 |
| PERM-241 | `PLATFORM_CARRIER_VETTING` | approve | `carrier_application` it also authored/edited | — | denied — maker-checker |
| PERM-242 | `PLATFORM_CLAIMS_DESK` | settle, disallow | `claim` | `granted_case` + second approver (`PLATFORM_SENIOR_REVIEWER`, ROLE-229) | BR-807/808/907 |
| PERM-243 | `PLATFORM_BILLING_OPS` | request | `charge_waiver` | `granted_case` | BR-907 |
| PERM-244 | `PLATFORM_BILLING_OPS` | approve | `charge_waiver` it requested | — | denied — maker-checker |
| PERM-245 | `PLATFORM_SENIOR_REVIEWER` (ROLE-229) | approve | `charge_waiver` | `granted_case`, requester ≠ approver | BR-907 — **[role name corrected from informal "ops supervisor"]** |
| PERM-246 | `SHIPPER_*`, `CARRIER_*` | approve | `charge_waiver`, `claim_settlement` | — | denied always — BR-907 |
| PERM-247 | `PLATFORM_ADMIN` | create, revoke | `role_grant`, `user`, `organization` | `platform_wide` | FR-215 |
| PERM-248 | `PLATFORM_ADMIN` | read, mutate | `bid`, `award`, `invoice`, `claim`, `pod` | — | denied always — admin ≠ operator |
| PERM-249 | `PLATFORM_ADMIN` | grant itself | any business role | — | denied — self-grant blocked |
| PERM-250 | `PLATFORM_AUDITOR` | read | `audit_log`, `selection_record`, all business objects | `platform_wide` | BR-819 |
| PERM-251 | `PLATFORM_AUDITOR` | any mutation | any | — | unrepresentable by role definition |
| PERM-252 | `PLATFORM_AWARD_OVERRIDE` | void, re-award | `award` | `granted_case`, dual-approved, time-boxed | BR-306 |
| PERM-253 | `PLATFORM_*` | accept, decline | `award` on behalf of a carrier | — | **denied always** |
| PERM-254 | `PLATFORM_*` | create, amend | `bid` | — | **denied always** — BR-317 anti-shill |
| PERM-255 | `CARRIER_OWNER` | read | `audit_log` entries for its own org | `own_org` | RSK-900 |
| PERM-256 | `SHIPPER_ORG_ADMIN` | read | `carrier identity + authority type` on own load | `own_org`, post-award / at-bid | BR-313 |
| PERM-257 | `CARRIER_AGENT` | inherit | grantor-specified subset of ROLE-211 | `own_org` (host org), until `expires_at` | §4 (F2 §2.8) |
| PERM-258 | any role | read | `document` (COI, CDL, authority) of another org | `assigned_load` only | BR-813 |
| PERM-259 | any suspended user/org | any mutating action | any | — | denied — BR-818 preserves read on in-flight loads |
| **PERM-260** | **`PLATFORM_CARRIER_VETTING`** | **override** | **`eligibility_evaluation`** | **`granted_case`**, dual-approved when overriding an automated FAIL | **[ASSEMBLER ADDITION]** BR-908, F13 FR-1350/1351, F11 FR-1113 — see §16.3 |
| **PERM-261** | **`CARRIER_DISPATCHER`** | **read (live)** | **`tracking_position`** | **`own_org`** **[at `exact_position`]** | **[ASSEMBLER ADDITION]** F8 §6 |
| **PERM-262** | **`PLATFORM_SUPPORT`/`PLATFORM_EXCEPTION_DESK`** | **read** | **`tracking_position`** | **`granted_case`** **[at `exact_position`, audited]** | **[ASSEMBLER ADDITION]** F8 §6, exception handling only |
| **PERM-263** | **`CONSIGNEE_TOKEN`** | **read** | **`tracking_position`** | **`assigned_load`** **[at `corridor_band`, no history, no coordinates]** | **[ASSEMBLER ADDITION]** F8 §6, formalizes PERM-231's masked view |
| **PERM-264** | **`PLATFORM_CONFIG_ADMIN`** (ROLE-230) | **edit** | **`auction_ruleset`, `eligibility_gate_policy`** | **`platform_wide`** | **[ASSEMBLER ADDITION]** F6 §7, F13 §6, F11 FR-1142/1145 |

### 4.3 The contested actions — explicit answers (F2 §2.3, unchanged)

| Action | Answer (authoritative) | Trace |
|---|---|---|
| Publish a load | `SHIPPER_LOAD_POSTER` when `own_site`; `SHIPPER_ORG_ADMIN` when `own_org`. | BR-101/901/904 |
| Bid | `CARRIER_OWNER`, or `CARRIER_DISPATCHER[+BID]`, when `eligible_load`. Never accounting, compliance or driver. | BR-900/301 |
| **Accept an award on a carrier's behalf** | Only `CARRIER_OWNER` or `CARRIER_DISPATCHER[+ACCEPT_AWARD]`. **No PLATFORM role may ever accept for a carrier.** | BR-902/905, PERM-253 |
| Sign a POD | The assigned driver when `assigned_load`; binding on the carrier org. A dispatcher-entered POD is a distinctly-typed carrier attestation, weaker evidence. | BR-903/910 |
| Cancel | Pre-award: original poster or admin. Post-award pre-pickup: `SHIPPER_ORG_ADMIN` only `[ASSUMPTION: conf: med]`. Post-`PICKED_UP`: no role — RTO instead. | BR-904/905/144 |
| Raise a claim | `SHIPPER_CLAIMS_CONTACT`/admin, `CARRIER_OWNER`/`CARRIER_ACCOUNTING`, or `PLATFORM_CLAIMS_DESK` relaying a consignee observation. | BR-807/906 |
| Settle a claim | `PLATFORM_CLAIMS_DESK` only, two distinct platform actors. | BR-907/808 |
| Waive a charge | `PLATFORM_BILLING_OPS` requests → `PLATFORM_SENIOR_REVIEWER` decides. | BR-907 |
| Approve a carrier | `PLATFORM_CARRIER_VETTING` only; approver ≠ editor. | BR-908 |
| **Override the eligibility gate for a specific carrier/load** *(new row)* | **`PLATFORM_CARRIER_VETTING`, `granted_case`, dual-approved on FAIL→APPROVE, never bypassing the gate to force-award — F11 FR-1128 refuses that outright.** | **[ASSEMBLER ADDITION]** F13 §8, F11 §4 |

### 4.4 Cross-org visibility (F2 §2.4, unchanged) + field-level view masks (F8 §6, folded in)

Legend: **✓** visible · **✗** hidden · **D** = decided by F6's `DEC-302`/`303` fork · **P** =
post-award only.

| Field | Ineligible carrier | Eligible, not bid | Live bidder | Losing bidder (post-award) | Awarded carrier | Assigned driver | Consignee token |
|---|---|---|---|---|---|---|---|
| Load exists at all | ✗ (not-found) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Lane at city/state level | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Full pickup/drop street address | ✗ | ✗ | ✗ | ✗ | **P** ✓ | **P** ✓ | own stop only |
| Dock #, gate code, site contact | ✗ | ✗ | ✗ | ✗ | **P** ✓ | **P** ✓ | own stop only |
| Commodity class, weight, dims, equipment, hazmat | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| Appointment windows | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Shipper legal identity | ✗ | **D** `[NEEDS INPUT]` | **D** | **D** | ✓ | ✓ | ✓ |
| Own bid | — | — | ✓ | ✓ | ✓ | ✗ | ✗ |
| Rival bid amounts | ✗ | ✗ | **D** — §16.1 | ✗ | ✗ | ✗ | ✗ |
| Rival bidder identities | ✗ | ✗ | ✗ **never** | ✗ | ✗ | ✗ | ✗ |
| Award outcome (won/closed) | ✗ | ✗ | ✓ | ✓ "no longer open" — not the clearing price | ✓ | ✓ | ✗ |
| Winning price | ✗ | ✗ | ✗ | ✗ | ✓ (own) | ✗ | ✗ |
| Selection record | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ — shipper + platform + auditor only |
| **Tracking position (`at` granularity, F8 §6)** | ✗ | ✗ | ✗ | ✗ | **exact** (own trip) | **exact** | **corridor/ETA band only** |
| POD / BOL images | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | own delivery only |

**Field-level view mask table (F8 §6, the granularity values PERM-212/261/262/263 above cite):**

| Role | Scope | Default granularity |
|---|---|---|
| Shipper ops user | `assigned_load` | Milestone + corridor/ETA band; not exact coordinates `[NEEDS INPUT: confirm]` |
| Carrier dispatcher | `own_org` | Exact position, own fleet, load active |
| Platform ops | `granted_case`, audited | Exact position, exception handling only |
| Consignee (no account) | `assigned_load` tokenised | Corridor/ETA band only; no coordinates, no history |

### 4.5 Scope enforcement, ops power, delegation, FRs, edge cases

Reproduced from F2 §2.6–§2.10 in full (unchanged substance; this is the mechanism-level material
that makes the matrix above enforceable, not just declared):

**Scope enforcement failure modes** (F2 §2.6): IDOR on load/bid/document id → reads filter by scope
at the query layer, not post-fetch; tenant id from a client-supplied value → org context derives
only from the session, never a body/header/path org id; enumeration via authorization errors →
cross-org and non-eligible denials return **not-found**, never forbidden; driver enumerating
unassigned loads → driver principal resolves to an explicit `assigned_load` set, no list filter
widens it; suspended user's live token → suspension revokes at the authorization layer, not only at
login; permissions cached after revocation → bounded staleness window `[NEEDS INPUT]`; broker-carrier
seeing a load via two paths → visibility computed per org context, once per request; escalation via
self-grant → no role grants itself or a role it does not hold.

**Platform ops power — the insider case** (F2 §2.7): impersonation is read-only by default; every
audit entry carries `actor_user_id` and `real_actor_user_id`; separation of duties is enforced, not
stated (vetting ≠ billing ops, claim settlement needs two actors, waiver requester ≠ approver,
`PLATFORM_ADMIN` holds no business permission, `PLATFORM_AUDITOR` cannot be granted write); award
override is its own break-glass role, dual-approved, disclosed to every affected org; **no platform
role bids or accepts — "the hardest line in this document" (F2's own words).**

**Delegation** (F2 §2.8): dispatcher acting for a driver may bind the tuple and record a *carrier
attestation* but never a driver signature; owner-operator is a **union**, not a superset, of
`CARRIER_OWNER` ∪ `CARRIER_DRIVER`, so a one-person carrier is never blocked by a maker-checker rule
that needs two humans; `CARRIER_AGENT` is time-boxed, revocable, capped, never inheriting
`+ACCEPT_AWARD` unless explicit; a person working for two carriers is two separate user identities,
whose linkage is a related-entity fraud signal, not a convenience feature.

**Functional requirements** (F2 §2.9, FR-200–FR-222, 23 requirements) and **edge-case register**
(F2 §2.10, EC-200–EC-222, 23 rows) are carried forward unchanged — full text in
`frd-F2-authorization-rbac.md` §2.9–§2.10, cited here rather than reproduced a second time to avoid
duplicating ~900 words with zero substantive change.

**What F2 could not resolve without the client** (F2's own closing line, still true): the post-award
cancel tier, the impersonation and delegation durations, whether the shipper's identity is masked
pre-award (depends on §16.1), and the sole-owner account-recovery path. Risk-appetite calls, not
drafting gaps.

---

## 5. F1 — Identity, Authentication, Sessions, Onboarding

*Full source: `frd-F1-identity-auth.md`. Reproduced with cross-references updated to this document's
section numbers.*

**Owns:** authentication mechanisms · session/token lifecycle · org & user onboarding flow ·
credential/account recovery · identity assurance framework. **Does not own:** role permissions (§4)
· entity/state storage & audit log (§3) · comparing a driver's document to the record on file (§9,
BR-221/224) · fraud classification on mismatch (§9/§13 consume F1's signal) · screens (§11) ·
notification delivery (§12) · rate-limit/security NFRs (§14).

### 5.1 Assurance framework

Two axes, NIST 800-63-3 terms: **IAL** (how sure who this person is), **AAL** (how sure this session
is that person).

| Population | IAL target | AAL standing | AAL step-up |
|---|---|---|---|
| Shipper coordinator / carrier dispatcher | IAL1, org-vetted | AAL1, MFA by role | AAL2 |
| Org admin / owner-operator | IAL2-equiv at onboarding | AAL2 | AAL2 + re-challenge |
| Driver | IAL2-equiv artifact at pickup only | AAL1, device-bound | AAL2 for payout actions |
| Platform ops | IAL2, employee-vetted | AAL2 always | AAL2 + impersonation consent |
| Consignee | No identity system — capability token only | n/a | n/a |

### 5.2 Organization onboarding

| ID | Requirement | Pri | Trace |
|---|---|---|---|
| FR-100 | Org creation is type-scoped at entry: SHIPPER, CARRIER (asset-holder/broker), PLATFORM | Must | §2 |
| FR-101 | Carrier/shipper org creation requires IAL2-equiv proofing (doc + liveness) before leaving DRAFT | Must | BR-208 |
| FR-102 | Owner-operator org (admin = sole driver) onboards without a forced second-user step | Must | §2 |
| FR-103 | Org auth state (`PENDING_VERIFICATION`→`VERIFIED`) is independent of §9's document-vetting; login allowed at `PENDING_VERIFICATION`, bidding is not (§4 gates) | Must | BR-200/908 |
| FR-104 | Shipper proofing is lighter (IAL1 + domain-verified email); no FMCSA dependency | Should | derived |
| FR-105 | Platform-org accounts are never self-serve; created only by an existing platform admin | Must | scope boundary |

### 5.3 User onboarding into an existing org

| ID | Requirement | Pri | Trace |
|---|---|---|---|
| FR-106 | Org admin/delegate invites by email or phone; invite = single-use, expiring, role-tagged, bound to one identifier | Must | BR-900/901 |
| FR-107 | Invite acceptance requires credential creation + MFA enrollment matching role policy before first action | Must | BR-900 |
| FR-108 | Driver invite supports SMS/phone as primary channel, not email-first | Must | BR-914 |
| FR-109 | Self-service signup creates a **new** org only; never a silent join of an existing org | Must | §2 |

### 5.4 Authentication mechanisms

| ID | Requirement | Pri | Trace |
|---|---|---|---|
| FR-110 | Desk users authenticate via credential (identifier+password) or org SSO (§5.4a) | Must | derived |
| FR-111 | Passwordless magic-link available as an alternative, not a default | Could | derived |
| FR-112 | Driver device biometric/PIN is a local-unlock layer atop a valid server session, never a substitute | Must | §5.1 |
| FR-113 | SSO capability: SAML 2.0, OIDC (no vendor), offered to shipper orgs above a size `[NEEDS INPUT]` | Should | OBJ-002 |
| FR-114 | SSO JIT provisioning requires prior domain verification | Must | derived |
| FR-115 | SSO never extends to drivers regardless of org config — phone-first stays | Must | BR-914 |

**`DEC-100` (open):** driver primary credential — (A) phone+SMS-OTP primary; (B) email+password,
phone MFA-fallback; (C) phone-first + device-bound long session, rare OTP re-entry. `[NEEDS INPUT]`.
**`DEC-101` (open):** SSO default — SP-initiated only vs. also accept IdP-initiated. `[NEEDS INPUT]`.

### 5.5 MFA policy

| ID | Requirement | Pri | Trace |
|---|---|---|---|
| FR-116 | MFA mandatory for any role that can accept an award, approve a waiver, change payee-of-record, or is platform ops | Must | BR-902/907 |
| FR-117 | MFA optional for read-only/viewer users | Could | derived |
| FR-118 | MFA methods: TOTP, WebAuthn/passkey (strongest), SMS OTP fallback only — never sole method for a privileged role | Must | OBJ-006 |
| FR-119 | Driver base login needs no MFA; MFA required the moment a driver action touches payout/bank details | Must | BR-812/914 |

### 5.6 Step-up authentication

| ID | Requirement | Pri | Trace |
|---|---|---|---|
| FR-120 | Accepting an award, changing payee-of-record, approving a waiver, starting impersonation each require a fresh MFA challenge within `[NEEDS INPUT]` window regardless of standing session | Must | BR-902/907/909 |

### 5.7 Session & token lifecycle

| ID | Requirement | Pri | Trace |
|---|---|---|---|
| FR-121 | Web/desk: short-lived access token + rotating refresh token; lifetimes `[NEEDS INPUT]` | Must | OBJ-006 |
| FR-122 | Mobile driver: longer-lived, device-bound refresh token; lifetime `[NEEDS INPUT]` | Must | §5.1 |
| FR-123 | Refresh token bound to device/install id; token from an unregistered device rejected outright | Must | OBJ-006 |
| FR-124 | Driver app caches read state offline; queues state-changing actions with a client idempotency key for reconnect-sync (cross-ref §10) | Must | OBJ-004, §1 |
| FR-125 | Reconnect tries silent refresh first; interactive re-login only if the refresh token itself is invalid | Must | UX for population |
| FR-126 | Every user can list/revoke their own sessions | Should | OBJ-006 |
| FR-127 | Org admin can force-revoke any org user's sessions | Must | BR-900/910 |
| FR-128 | Lost/stolen device: user/admin deregisters device, invalidating its bound refresh token server-side | Must | §5.1, OBJ-006 |

### 5.8 Consignee capability link

| ID | Requirement | Pri | Trace |
|---|---|---|---|
| FR-129 | Every consignee action is a signed, single-purpose, expiring token scoped to one shipment + one action class — never a login | Must | §2, BR-906/912 |
| FR-130 | State-changing tokens are single-use; a replay is rejected with the first consumption event shown | Must | BR-906 |
| FR-131 | Read-only tokens may be multi-use within expiry | Must | BR-912 |
| FR-132 | Token delivered only via the out-of-band channel captured at load creation | Must | BR-912 |
| FR-133 | Expired-token access returns a safe error plus a relay path back through shipper/carrier contact | Must | BR-906, OBJ-004 |
| FR-134 | Wrong-person-opens-link is a **named residual risk, not solved** — mitigation: short expiry `[NEEDS INPUT]`, device/IP fingerprint, flag "unauthenticated party" | Must | BR-906/912 |

### 5.9 Driver identity assurance at dispatch/pickup

Three-agent chain, F1 owns one link: F1 proves the acting session is the authenticated, device-bound
driver session. §9 (F7) compares the captured artifact to the dispatch record (BR-212/221/224).
§9/§13 classify and queue the mismatch (BR-806).

| ID | Requirement | Pri | Trace |
|---|---|---|---|
| FR-135 | Dispatch acceptance binds the authenticated driver session to the load's driver+equipment tuple | Must | BR-212 |
| FR-136 | Pickup check-in accepted only from an authenticated, device-bound driver session; wrong device rejected before any comparison runs | Must | BR-221/227 |
| FR-137 | Check-in captures a machine-readable identity artifact attached to the action record; F1 captures, §9 compares | Must | BR-221 |
| FR-138 | Last-minute change of driver contact channel near dispatch is flagged to §9's review queue, not silently accepted | Must | BR-228 |
| FR-139 | On a §9 mismatch signal, F1 suspends further session-scoped actions on that load pending §9/§13 resolution | Must | BR-221/806, BR-225 |
| FR-140 | Geofence+timestamp of check-in captured as session metadata by F1; geofencing mechanism itself is §10's | Must | OBJ-006 |

### 5.10 Credential and account recovery

| ID | Requirement | Pri | Trace |
|---|---|---|---|
| FR-141 | Reset via verified channel only; security questions explicitly excluded | Must | OBJ-006 |
| FR-142 | Reset tokens single-use, short expiry `[NEEDS INPUT]` | Must | derived |
| FR-143 | Lost-MFA recovery for a privileged role is never self-service — ops-assisted, re-proofed, logged | Must | §5.1, OBJ-006 |
| FR-144 | Changing recovery email/phone requires fresh auth + notifies the **old** channel | Must | OBJ-006 |
| FR-145 | All-admins-locked-out recovery is ops-assisted, identity-proofed, never fully automated | Must | OBJ-006 |

### 5.11 Support impersonation

| ID | Requirement | Pri | Trace |
|---|---|---|---|
| FR-146 | Impersonation is a distinct session type, requiring consent or a logged justification when unobtainable | Must | OBJ-006 |
| FR-147 | Impersonation sessions auto-expire, duration `[NEEDS INPUT]`, every touched screen visibly bannered | Must | derived |
| FR-148 | Starting impersonation requires ops's own fresh MFA + an elevated permission (§4 defines it, F1 requires the auth event) | Must | BR-907 pattern |
| FR-149 | Every impersonated action audited as actor=ops, on-behalf-of=target, never merged unlabeled into target's history | Must | OBJ-006 |

### 5.12 Account and org lifecycle

| ID | Requirement | Pri | Trace |
|---|---|---|---|
| FR-150 | Org suspension revokes every active session for every org user immediately | Must | BR-229 |
| FR-151 | Suspension doesn't retroactively invalidate actions already taken pre-suspension on a load past pickup | Must | BR-230 |
| FR-152 | Offboarding one user (driver leaves mid-trip) revokes that session; trip custody/tracking record persists independently | Must | BR-910 |
| FR-153 | Org admin must bind a replacement driver session to the in-flight load before further driver-scoped actions | Must | BR-910/224 |
| FR-154 | A removed/suspended org's proofed identity is flagged; re-onboarding under it routes to ops review | Should | BR-229 |

### 5.13 Language and accessibility

| ID | Requirement | Pri | Trace |
|---|---|---|---|
| FR-155 | Auth flows available in English and Spanish at minimum for drivers | Must | BR-914 |

### 5.14 API surface

| API | Method / path | Idempotency? | FR |
|---|---|---|---|
| API-100 | `POST /v1/orgs` | Yes | FR-100 |
| API-101 | `POST /v1/orgs/{id}/verify-identity` | Yes | FR-101 |
| API-102 | `POST /v1/orgs/{id}/invites` | Yes | FR-106 |
| API-103 | `POST /v1/invites/{token}/accept` | No (token guards) | FR-107 |
| API-104 | `POST /v1/auth/login` | No | — |
| API-105 | `POST /v1/auth/sso/{org_id}/start` | No | FR-113/114 |
| API-106 | `POST /v1/auth/mfa/challenge` | No | FR-116/120 |
| API-107 | `POST /v1/auth/token/refresh` | No | FR-121/125 |
| API-108 | `GET /v1/users/me/sessions` | No | FR-126 |
| API-109 | `DELETE /v1/users/me/sessions/{id}` | No | FR-126/128 |
| API-110 | `DELETE /v1/orgs/{id}/users/{id}/sessions` | No | FR-127 |
| API-111 | `POST /v1/consignee-links` | Yes | FR-129 |
| API-112 | `GET /v1/consignee-links/{token}` | n/a | FR-130/133/134 |
| API-113 | `POST /v1/consignee-links/{token}/submit` | Yes | FR-130 |
| API-114 | `POST /v1/auth/recovery/start` | Yes | FR-141 |
| API-115 | `POST /v1/auth/recovery/mfa-reset` | Yes | FR-143 |
| API-116 | `POST /v1/impersonation/sessions` | Yes | FR-146/148 |
| API-117 | `DELETE /v1/impersonation/sessions/{id}` | No | FR-147 |
| API-118 | `POST /v1/dispatch/{load_id}/checkin` | Yes | FR-136/137 |

### 5.15 Error names (candidates; §7 F5 allocates real `ERR-` IDs)

`INVALID_CREDENTIALS` · `MFA_REQUIRED` · `MFA_CHALLENGE_FAILED` · `TOKEN_EXPIRED` ·
`TOKEN_ALREADY_USED` · `DEVICE_NOT_REGISTERED` · `SESSION_REVOKED` · `INVITE_EMAIL_MISMATCH` ·
`ORG_NOT_VERIFIED` · `ORG_SUSPENDED` · `STEP_UP_REQUIRED` · `IMPERSONATION_NOT_CONSENTED` ·
`DRIVER_SESSION_MISMATCH_HOLD` · `CONSIGNEE_LINK_EXPIRED` · `CONSIGNEE_LINK_ALREADY_USED`.

### 5.16 Edge case register (15)

| EC | Trigger | Behaviour | Who decides | Unresolved? |
|---|---|---|---|---|
| EC-100 | Consignee link forwarded/replayed after use | Flagged "unauthenticated party"; replay shows prior consumption | F1/§11 | Yes — flag only |
| EC-101 | Link opened after expiry | Safe error + relay-back path | F1 | No |
| EC-102 | Owner-operator loses only device | Lost-device flow on the sole session; SLA `[NEEDS INPUT]` | F1 | Partially |
| EC-103 | Driver has no phone / shared family device | Shared device binds sequentially; needs a "switch driver" flow | Product | Yes — flow unspecified |
| EC-104 | Fully offline pickup-to-drop cycle | Queued actions sync via idempotency key; no-reconnect-before-deadline stalls state | F1/§10 | Yes → §9/§6 |
| EC-105 | SSO IdP asserts email on unverified domain | JIT refused, falls to manual invite | F1 | No |
| EC-106 | Impersonation consent unreachable, or session outlives time-box | Justification path logged; server-side hard expiry either way | F1 | Escalation authority `[NEEDS INPUT]` |
| EC-107 | Admin offboards driver mid-trip, loaded | Session revoked; trip persists; blocked until reassignment | F1/§9 | Interim gap → §9 |
| EC-108 | Broker's downstream driver never invited as a user | Broker can't dispatch — BR-223 needs driver as User | F1/§9 | Who triggers invite — flagged |
| EC-109 | Two admins race revoke/re-grant same session | Last-write-wins at session store | §3 | Yes |
| EC-110 | Suspended org, in-transit session still valid | Stays valid for that load (FR-151); new actions blocked | F1 | No |
| EC-111 | Reset requested, no login-holding account | Safe, non-enumerating response | F1 | Copy `[NEEDS INPUT]` |
| EC-112 | Driver CDL expires between dispatch and pickup | F1 authenticates check-in; §9's comparison fails and holds (FR-139) | §9/F1 | No |
| EC-113 | Lost phone is both app device and MFA device | Session and MFA recovery must be handled together | F1 | Yes — overlap unmodelled |
| EC-114 | Consignee is also a shipper's posting user elsewhere | Identities not linked; token flow assumes no account regardless | Product | Yes |

**Counts:** 56 FR · 19 API · 15 EC · 13 `[NEEDS INPUT]` · 2 open `DEC-`.

---

## 6. F4 — API Surface & Integrations

*Full source: `frd-F4-api-surface.md`. `eligibility` endpoint fixed to match §15's canonical
signature (§16.3); event catalog superseded by §12's (§16.6) — see both for why.*

**ID block: 400-499.** Inherits §1's API conventions unchanged: `/v1` base, resource-oriented plural
nouns, idempotency keys on mutating calls, cursor pagination, trace id per response, canonical error
envelope, `<entity>.<past_tense>` events. Domain semantics belong to the owning section — F4 is the
wire contract, traced to BRD `BR-`/`OBJ-`.

### 6.1 Three consumer classes

| Class | Auth carrier | Payload shape | Pagination | Failure mode designed for |
|---|---|---|---|---|
| **Web** (shipper/carrier/ops) | Bearer session/JWT (§5) | Full resource, rich forms | Cursor, filter, sort | Standard timeout/retry |
| **Driver mobile, poor connectivity** | Bearer JWT, long refresh | Minimal fields, compressed images, batched arrays | None — own trip only | **Offline queue**: client persists + client-generated key, flushes on reconnect; server accepts late arrivals, reconciles by sequence, never blind-overwrites |
| **Server-to-server** (TMS, factoring, accounting) | API key+HMAC or OAuth2 client-credentials `[NEEDS INPUT]` | Strict schema, additive-tolerant | Bulk cursor GET, webhook preferred | Middleware retry storms — idempotency-key mandatory |

Mobile has no "list loads" — only the assigned trip (`API-431`). Deliberate payload minimisation.

### 6.2 Endpoint catalog

Consumers: **W**=web, **M**=driver mobile, **S**=server-to-server, **C**=tokenised/no-auth,
**O**=platform ops. Idem = idempotency-key required.

| ID | Method & path | Purpose | Consumers | Idem | Traces |
|---|---|---|---|---|---|
| API-400 | `POST /v1/loads` | Create draft load | W,S | — | BR-100/110 |
| API-401 | `GET /v1/loads` | List, cursor, filter org/status/lane | W,S | — | BR-100 |
| API-402 | `GET`\|`PATCH /v1/loads/{id}` | Retrieve; amend pre-bid only | W,S | — | BR-135/136 |
| API-403 | `POST /v1/loads/{id}/publish` | Commit to auction | W,S | Y | BR-121/130 |
| API-404 | `POST /v1/loads/{id}/withdraw` | Pre-award withdraw | W,S | Y | BR-138/139 |
| API-405 | `POST /v1/loads/{id}/cancel` | Cancellation ladder entry | W,S | Y | BR-140–144 |
| API-406 | `GET /v1/loads/{id}/snapshot` | Immutable original declaration | W,S,O | — | BR-122 |
| API-407 | `GET /v1/loads/{id}/history` | State-transition audit | W,S,O | — | BR-102 |
| API-410 | `GET /v1/loads/{id}/auction` | Auction state & params | W,S | — | §8.3 |
| API-411 | `POST /v1/loads/{id}/bids` | Place bid, firm commitment | W,S | **Y, mandatory** | BR-301/307 |
| API-412 | `GET /v1/loads/{id}/bids` | Own bid / full list post-close, RBAC-scoped | W,S | — | BR-314 |
| API-413 | `DELETE /v1/loads/{id}/bids/{bidId}` | Pre-close withdrawal, logged | W,S | Y | BR-308 |
| API-414 | `POST /v1/loads/{id}/auction/close` | Early close (shipper/ops) | W,O | Y | DEC-308 |
| API-415 | `GET /v1/bids/feed` | Own eligible-load feed, cursor | W,S | — | BR-200 |
| API-420 | `GET /v1/loads/{id}/award` | Award detail | W,S | — | §8.3 |
| API-421 | `POST /v1/loads/{id}/award/accept` | Accept — re-gates eligibility on receipt | W,S | **Y, mandatory** | BR-302 |
| API-422 | `POST /v1/loads/{id}/award/decline` | Decline, structured reason code | W,S | Y | BR-156 |
| API-423 | `GET /v1/loads/{id}/selection-record` | Immutable award/selection evidence | O, carrier(own) | — | BR-303 |
| API-424 | `GET`\|`POST /v1/loads/{id}/rate-confirmation` | Retrieve; acknowledge | W,S | Y (accept) | BR-600 |
| API-430 | `POST /v1/loads/{id}/trip` | Assign driver+truck | W | Y | BR-212 |
| API-431 | `GET`\|`PATCH /v1/trips/{id}` | Retrieve; status transition, seq-guarded | M(primary),W | Y | BR-400–409 |
| API-432 | `POST /v1/trips/{id}/custody-events` | Pickup / transload / RTO record | M | **Y, mandatory** | BR-400/402/404 |
| API-433 | `POST /v1/trips/{id}/exceptions` | Transit exception, offline-safe | M | Y | BR-405 |
| API-440 | `POST /v1/trips/{id}/positions` | Batched position ingest (§10) | M,S | seq-dedup, not key | BR-401 |
| API-441 | `GET /v1/trips/{id}/eta` | Derived ETA (§10) | W,S | — | §8.4 |
| API-442 | `GET /v1/track/{token}` | Read-only tracking, tokenised, expiring | C | — | §2 |
| API-445 | `POST /v1/documents` | Upload BOL/COI/authority, image-tolerant | W,M,S | Y | §8.5/§8.2 |
| API-446 | `GET /v1/documents/{id}` | Retrieve document | W,M,S,O | — | §8.5/§8.2 |
| API-447 | `POST /v1/trips/{id}/pod` | Structured POD capture incl. OS&D fields — writes `ENT-316` delivery_capture (§3.4) | M | **Y, mandatory** | BR-500–509 |
| API-448 | `GET /v1/pod/{token}`, `POST /v1/pod/{token}/sign` | Tokenised POD capture, no account | C | Y (sign) | BR-510 |
| API-449 | `POST /v1/pod/{id}/addenda` | Post-capture correction, never overwrites | W,M,O | Y | BR-512 |
| API-455 | `GET /v1/loads/{id}/invoice` | Invoice detail, per-line status | W,S | — | BR-601/603 |
| API-456 | `POST /v1/invoices/{id}/lines/{lineId}/dispute` | Raise a line dispute | W,S | **Y, mandatory** | BR-604 |
| API-457 | `GET /v1/invoices` | List, org-scoped, cursor | W,S | — | §8.6 |
| API-458 | `GET /v1/invoices/{id}/settlement` | Payout / receivable status | W,S | — | BR-605 |
| API-460 | `POST /v1/claims` | Carmack claim intake, §370.3 fields | W,S | Y | BR-807 |
| API-461 | `GET`\|`PATCH /v1/claims/{id}` | Retrieve; ops decision | W,O | Y | BR-807/808 |
| API-462 | `POST /v1/disputes` | Money dispute, distinct queue | W,S | Y | BR-811 |
| API-463 | `GET /v1/disputes/{id}` | Retrieve | W,O | — | BR-811 |
| API-465 | `POST /v1/carriers` | Onboard carrier org | W | — | BR-201–208 |
| API-466 | `GET`\|`PATCH /v1/carriers/{id}` | Profile; role, entity fields | W,O | — | BR-203/222 |
| API-467 | `POST /v1/carriers/{id}/documents` | Authority / COI / W-9 upload | W | Y | BR-204/206 |
| API-468 | `GET /v1/loads/{id}/eligibility?carrier_id=&truck_id=&driver_id=` | **[ASSEMBLER FIX]** Pre-bid self-check. Original draft took only `carrier_id`, inconsistent with §15's canonical `eligibility(carrier_id, truck_id, driver_id, load_id)` four-argument contract — "no carrier is eligible in the abstract" (§2) applies to a self-check exactly as much as to F6's internal call. Params corrected to the full tuple. | W,S | — | BR-200, §15 FR-1300 |
| API-469 | `POST /v1/carriers/{id}/suspend`, `/reinstate` | Graduated enforcement | O | Y | BR-817/818 |
| API-470 | `POST`\|`GET /v1/drivers` | CDL/class registry (§9) | W | — | BR-210 |
| API-471 | `POST`\|`GET /v1/equipment` | Tractor/trailer registry — type, VIN, policy | W | — | BR-209 |
| API-472 | `PATCH /v1/equipment/{id}/availability` | Time-windowed lock/release — writes `ENT-325` (§3.1.2) | W,S | — | BR-214/215 |
| API-475 | `GET /v1/notifications` | In-app feed, cursor (§12 content) | W,M | — | §7.3 |
| API-476 | `POST /v1/webhooks` | Server-to-server event subscription mgmt | S | — | §1 |
| API-477 | `GET /v1/webhooks/{id}/deliveries` | Delivery log, on-demand replay | S | — | §1 |
| API-480 | `GET /v1/admin/exceptions-queue` | Cross-domain exception desk feed | O | — | §7.3 |
| API-481 | `POST /v1/admin/overrides` | Gate/award override, named + reasoned | O | Y | BR-306 |
| API-482 | `GET /v1/admin/audit-log` | Every mutating action, actor+time | O | — | §8.9 |
| API-485 | `GET /v1/reports/loads` | Bulk export, filter, cursor | W,S | — | derived |
| API-486 | `GET /v1/reports/settlement` | Reconciliation export | W,S | — | §8.6 |
| API-487 | `GET /v1/reports/licence-register` | BR-1205 data-licence register export | O | — | BR-1205 |

**Not built, on purpose:** a driver "browse loads" feed (§6.1); a raw `osm.*`-record endpoint
anywhere (`DEC-LOCK-002` — `API-441`'s ETA/routing signals return an aggregated corridor summary,
never OSM rows); a bidder-visible rival-identity field on `API-412` (BR-314).

### 6.3 Idempotency — where a duplicate is materially harmful

Rule: `Idempotency-Key` header, scoped per (org, endpoint, key). Replay, same body → original
response unchanged. Replay, **different** body, same key → `409 IDEMPOTENCY_KEY_REUSED`. Retention
`[NEEDS INPUT: TTL, ≥24h per spine floor]`.

| Endpoint | Harm if duplicated | Semantics |
|---|---|---|
| `API-411` bid | Phantom price in the pool | Replay = no-op, returns original bid |
| `API-421` award accept | Races a decline/lapse | Re-gates every attempt; only first success binds |
| `API-447` POD capture | Duplicate/overwritten delivery evidence | Replay returns original; a *distinct* 2nd capture on already-`POD_CAPTURED` is `409` |
| `API-432` custody events | Phantom pickup from mobile retry | Mandatory — primary offline-queue endpoint |
| `API-456`/`API-460` dispute/claim | Inflated exposure | Replay returns original claim/dispute ID |
| `API-440` positions | High-frequency, header-per-ping wasteful | Dedup by client sequence number, not header |

### 6.4 Concurrency

| Scenario | Mechanism | Outcome |
|---|---|---|
| Two bids, same instant | Not a conflict — both persist; ranking deterministic at close | None; only a retried bid is deduped |
| Award races a withdrawal | Optimistic lock; award-commit re-checks load state in-transaction | `409 LOAD_WITHDRAWN` if withdrawal committed first |
| Load amended while bids open | `API-402` PATCH checks `bid_count == 0` via version field | `409 LOAD_HAS_BIDS` → withdraw-and-republish path |
| POD submitted twice, different content | State guard: trip already `POD_CAPTURED` | 2nd distinct submission is `409`; correction = `API-449` addenda only |
| Mobile posts a stale regression | Sequence/version check on `API-431` | `409 STALE_STATUS_TRANSITION`; client re-fetches, re-files as exception |

### 6.5 Events — superseded by §12's catalog

**[ASSEMBLER NOTE — see §16.6 for the full finding.]** F4's original draft included its own
`EVT-400`–`EVT-429` event-name table (30 events) covering essentially the same lifecycle transitions
as §12's (F10's) `EVT-1000`–`EVT-1048` catalog (49 events), independently and with different names
for some of the same transitions (e.g. F4's `load.awarded` vs. F10's split `award.determined`/
`award.confirmed`; F4's `carrier.suspended`/`carrier.reinstated` vs. F10's narrower
`carrier.suspended_in_flight`). **§12's catalog is canonical.** F4's IDs `EVT-400`–`EVT-429` are
retained below, not deleted (an ID is never reused once allocated, §1), but marked superseded — each
maps to the §12 event of the same underlying transition. Delivery: at-least-once, signed,
`schema_version` field so additive changes don't break subscribers; retry/backoff/max-attempts
`[NEEDS INPUT]`; failed deliveries logged at `API-477`, replayable — **this mechanics layer is
F4's and is unaffected by the catalog-ownership fix.**

| Superseded ID | Original name | Canonical §12 event |
|---|---|---|
| EVT-400 | `load.published` | 1000 `load.published` |
| EVT-401 | `load.amended` | *(no §12 equivalent — gap, §16.6)* |
| EVT-402 | `load.withdrawn` | 1039 `load.withdrawn` |
| EVT-403 | `load.cancelled` | 1038 `load.cancelled` |
| EVT-404 | `auction.opened` | 1001 `auction.opened` |
| EVT-405 | `auction.closed` | 1004 `auction.closed` |
| EVT-406 | `bid.placed` | 1002 `bid.submitted` |
| EVT-407 | `bid.withdrawn` | *(no §12 equivalent — gap, §16.6)* |
| EVT-408 | `load.awarded` | 1005 `award.determined` |
| EVT-409 | `award.accepted` | 1010 `award.accepted` / 1006 `award.confirmed` (two-phase, §12 §1) |
| EVT-410 | `custody.transferred` | 1022 `custody.transferred` |
| EVT-411 | `trip.status_changed` | *(execution-internal, not persona-facing — kept as F4-internal only)* |
| EVT-412 | `transit.exception_raised` | 1021 `transit.exception_reported` |
| EVT-413 | `pod.captured` | 1028 `pod.captured` |
| EVT-414 | `pod.addendum_added` | *(no §12 equivalent — gap, §16.6)* |
| EVT-415 | `delivery.refused` | 1026 `delivery.refused` |
| EVT-416 | `rate_confirmation.acknowledged` | 1011 `rate_confirmation.issued` (nearest match; ack vs. issue distinction not reconciled — flagged) |
| EVT-417 | `award.declined` | 1007 `award.declined` |
| EVT-418 | `award.lapsed` | 1008 `award.lapsed` |
| EVT-419 | `award.voided` | 1009 `award.voided_ineligible` |
| EVT-420 | `invoice.finalised` | *(no §12 equivalent — §12 has 1040 issued/1041 held/1042 settled but no explicit "finalised" — gap)* |
| EVT-421 | `payment.settled` | 1042 `invoice.settled` |
| EVT-422 | `claim.opened` | 1034 `claim.opened` |
| EVT-423 | `claim.decided` | 1035 `claim.obligation_due` (nearest match; "decided" ≠ "obligation due" — gap, not the same event) |
| EVT-424 | `dispute.opened` | 1036 `dispute.opened` |
| EVT-425 | `dispute.resolved` | *(§12 only has 1037 `dispute.closed_unresolved` — no "resolved-favourably" equivalent — genuine gap, §16.6)* |
| EVT-426 | `carrier.suspended` | *(§12 only has 1033 `carrier.suspended_in_flight`, narrower — genuine gap, §16.6)* |
| EVT-427 | `carrier.reinstated` | *(no §12 equivalent at all — genuine gap, §16.6)* |
| EVT-428 | `document.uploaded` | *(no §12 equivalent — informational tier, arguably correctly omitted)* |
| EVT-429 | `document.verified` | *(no §12 equivalent — same)* |

### 6.6 Integrations (capability, never vendor)

**Inbound**

| ID | Capability | Consumes at | Note |
|---|---|---|---|
| INT-400 | FMCSA authority/safety data (SAFER, CSA/SMS) | `API-465/467/468` | BR-201/205 |
| INT-401 | Insurance certificate verification | `API-467` | BR-204/804, insurer-sourced, never carrier-supplied PDF |
| INT-402 | ELD/telematics position & HOS signal | `API-440` | §9's planning-vs-compliance-record fork — not a compliance system of record |
| INT-403 | Document capture / OCR | `API-445` | BOL/POD/COI extraction |
| INT-404 | Payment & factoring remittance | `API-458` | NOA-gated routing, BR-606–608 |
| INT-405 | Mapping & truck-legal routing | `API-441`, `API-468` | Truck-intel platform candidate (`DEC-LOCK-002`); ODbL never crosses boundary |
| INT-406 | Identity / KYB (EIN, signer) | `API-465` | BR-104/208 |
| INT-407 | SMS/push delivery | `EVT-*` transport | §12 |
| INT-408 | Email delivery | `EVT-*` transport | §12 |
| INT-409 | Weather/work-zone/chain-control feed | `API-441` | Several feeds `Unverified` — cleared sources only (BR-1209) |

**Outbound**

| ID | Capability | Exposes | Note |
|---|---|---|---|
| INT-420 | Shipper TMS | `API-400/401/403`, events | Load posting + status by API, not screen |
| INT-421 | Carrier TMS | `API-415/424`, events | Bid feed + award push, trip pull |
| INT-422 | Accounting/ERP export | `API-457/486` | Invoice/settlement, W-9/1099 |
| INT-423 | Factoring NOA verification | `API-467`, `INT-404` | Signed-NOA-only routing, BR-607 |

### 6.7 Versioning & deprecation

`/v1` is the only live version. A breaking change (field removal/rename, semantics change, error-code
reuse — forbidden) ships as `/v2`, parallel-served for a deprecation window `[NEEDS INPUT: length]`,
announced via `Deprecation`/`Sunset` headers + changelog. An **additive** change ships in place —
`API-476` subscribers must tolerate unknown fields by contract. Event payloads carry their own
`schema_version`, independent of the API version.

**CHALLENGE (F4's own, carried forward):** the mobile offline queue (§6.1) means a
`TRANSIT_EXCEPTION`-worthy "no status update" can be a real physical gap or a connectivity gap that
resolves on reconnect. If F4 silently clears the flag on reconnect, §10's exception record
understates real gaps in poor-coverage lanes; if it never clears, every rural lane looks
exception-prone. **§10's call, not F4's.**

### 6.8 Edge case register (17)

| ID | Trigger | Behaviour | Who decides | Unresolved? |
|---|---|---|---|---|
| EC-400 | Idempotency key replayed w/ different body, or reused across endpoints | `409 IDEMPOTENCY_KEY_REUSED` | F4 | No |
| EC-401 | Award accepted after acceptance window lapses (BR-309) | `409` → `AWARD_LAPSED` cascade | §3/§8 own window value | Value `[NEEDS INPUT]` |
| EC-402 | COI lapses mid-auction, bid already placed | Rejected at submission, never ranked | §4/§15 | No |
| EC-403 | Cursor references a since-withdrawn load | Resolves (tombstone), marked withdrawn in payload | F4 | No |
| EC-404 | Bulk export times out mid-stream | Resumable via cursor, not restart-from-zero | F4 | Caps `[NEEDS INPUT]` |
| EC-405 | Webhook subscriber down past retry exhaustion | Failed delivery visible + replayable, no silent drop | F4 | Retry policy `[NEEDS INPUT]` |
| EC-406 | Position batch arrives out of order | Later sequence applied; stragglers appended, never overwrite current | F4/§10 | No |
| EC-407 | Tokenised consignee link reused after expiry | `410 GONE`; fresh link reissued via `API-431` | F4 | Expiry `[NEEDS INPUT]` |
| EC-408 | Second party attempts to sign an already-signed token | Rejected; correction = `API-449` addenda only | F4/§11 | No |
| EC-409 | Rate limit exceeded mid-run | `429` + `X-RateLimit-Reset` | F4 | Limits `[NEEDS INPUT]` |
| EC-410 | S2S client presents expired API key | `401`, no partial batch processing | §5/F4 | No |
| EC-411 | Uploaded document fails OCR / malformed / oversized | `status=UNPROCESSED`, human-review flag, never dropped | F4/INT-403 | Size cap `[NEEDS INPUT]` |
| EC-412 | Mobile clock skew on a custody timestamp | Server receipt time + device-asserted time both retained, flagged | F4/§9 | Feeds §9's HOS tension |
| EC-413 | `pod.addendum_added` fires after `pod.captured` delivered | Consumer must reconcile, never assume first event final | F4/§11 | No |
| EC-414 | Regulatory change forces a breaking change mid-deprecation-window | `/v2` ships early, window shortened, notice given | F4 + client relations | Notice period `[NEEDS INPUT]` |
| EC-415 | Integrator requests raw ODbL routing records | Hard-refused, no per-partner exception | F4 | No |
| EC-416 | Mobile queue flushes a multi-day dead-zone backlog on reconnect | Applied by sequence; silent interval stays flagged, not cleared | §10 | **Yes** |

**Counts:** 56 API · 30 EVT (superseded, §16.6) · 17 EC · 11 `[NEEDS INPUT]`.

---

## 7. F5 — Error Taxonomy and Failure Semantics

*Full source: `frd-F5-error-taxonomy.md`. §7.3 regenerated per F3's `ExceptionCase` split (§3.3);
one new error code (`ERR-567`) added to close the gap F3 named explicitly.*

**ID block:** `ERR-500`–`599` (68 allocated after this document's addition, 32 reserved) ·
`EC-500`–`599`. Envelope is §1's, unchanged: `{error:{code, message, field?, details, trace_id}}`.

### 7.1 Validation — `ERR-500`–`509`

| ID | Code | HTTP | Trigger |
|---|---|---|---|
| 500 | `REQUIRED_FIELD_MISSING` | 400 | Declared field absent |
| 501 | `FIELD_TYPE_INVALID` | 400 | Wrong type/format |
| 502 | `FIELD_VALUE_IMPLAUSIBLE` | 422 | Valid but implausible — `[NEEDS INPUT]` bounds |
| 503 | `FIELD_VALUE_OUT_OF_RANGE` | 400 | Negative weight/price, zero dimensions |
| 504 | `STOP_SEQUENCE_INVALID` | 400 | Drop scheduled before pickup, or before publish time |
| 505 | `EQUIPMENT_ATTRIBUTE_CONFLICT` | 422 | Impossible pairing — temp range on a dry van, hazmat on unplacarded equipment |
| 506 | `DOCUMENT_FORMAT_UNSUPPORTED` | 400 | Uploaded document unreadable/unverifiable |
| 507 | `DECLARATION_INCOMPLETE_FOR_PUBLISH` | 422 | Individually-valid fields, still fails the publish gate |
| 508 | `IDENTIFIER_MALFORMED` | 400 | Malformed resource id / idempotency key |
| 509 | `PAGINATION_CURSOR_INVALID` | 400 | Expired or tampered cursor |

### 7.2 Business-rule violations — `ERR-510`–`523`

| ID | Code | HTTP | Trigger | Traces to |
|---|---|---|---|---|
| 510 | `BID_BELOW_ELIGIBILITY_FLOOR` | 422 | Bid from a carrier failing the eligibility gate | `DEC-LOCK-001` |
| 511 | `BID_WINDOW_CLOSED` | 409 | Bid submitted after `AUCTION_CLOSED` | §8; state-derived → `ERR-525` |
| 512 | `BID_BELOW_MINIMUM_DECREMENT` | 422 | Undercuts by less than the platform floor | `DEC-311`, `[NEEDS INPUT]` |
| 513 | `LOAD_AMENDMENT_BLOCKED_LIVE_AUCTION` | 409 | Amendment attempted once bids exist | BR-136/138 |
| 514 | `CARRIER_INELIGIBLE_FOR_AWARD` | 409 | Award target fails gate on re-verification | `DEC-LOCK-001`; state `AWARD_VOIDED_INELIGIBLE` |
| 515 | `POD_PRECONDITION_NOT_MET` | 409 | POD submitted before pickup is recorded | BR-500; → `ERR-527` |
| 516 | `CANCELLATION_BLOCKED_POST_DELIVERY` | 409 | Cancel attempted at/after `POD_CAPTURED` | contrast `EC-509` |
| 517 | `AWARD_ACCEPTANCE_WINDOW_EXPIRED` | 409 | Accept attempted after lapse | BR-309, `DEC-309` |
| 518 | `DUPLICATE_FREIGHT_REFERENCE` | 422 | Same freight, two open loads, same org | BR-132; detection gap `[NEEDS INPUT]` |
| 519 | `BROKER_BID_UNDISCLOSED` | 422 | Broker bids without required disclosure | BR-313 — contrast `EC-512` |
| 520 | `COMMON_OWNERSHIP_BID_REJECTED` | 409 | Second bid from a commonly-owned entity | BR-316 |
| 521 | `PERMIT_OR_ENDORSEMENT_MISSING` | 422 | Load needs an endorsement no bidder holds | §9/§8 |
| 522 | `CARRIER_STANDING_SUSPENDED` | 403 | Action by a suspended carrier/org | BR-902 |
| 523 | `RESERVE_CEILING_MATH_INVALID` | 422 | Ceiling ≤ 0 or ≤ minimum decrement | `DEC-306` |

### 7.3 State-machine violations — `ERR-524`–`529` **[regenerated per F3's ExceptionCase split, §3.3]**

**Generation rule (unchanged):** for every state `S`, `allowed_next(S)` = §3.3's Load adjacency. A
transition request whose target ∉ `allowed_next(current)` is rejected as `ERR-524`, with
`details.allowed_next` listing the legal set — never a bare 409. **The adjacency itself is §3.3's
corrected table**, not the original 24-state one F5 was drafted against — see §3.3's
**[ASSEMBLER FIX]** note for exactly what changed and why (three target-state removals:
`DAMAGED/LOST/PILFERED`, `FRAUD_SUSPECTED`, `CARRIER_SUSPENDED_IN_FLIGHT` off `IN_TRANSIT`;
`CLAIM_OPEN` off `DELIVERED`; `DISPUTED`/`CLOSED_UNRESOLVED` no longer "reachable from any state" —
all five are `ExceptionCase` events now, not Load states).

| ID | Code | HTTP | Trigger |
|---|---|---|---|
| 524 | `STATE_TRANSITION_INVALID` | 409 | Generic — target ∉ `allowed_next(current)` (Load) |
| 525 | `AUCTION_ALREADY_CLOSED` | 409 | Bid/withdraw attempted once `AUCTION_CLOSED`+ — instance of 524 |
| 526 | `LOAD_NOT_YET_PUBLISHED` | 409 | Action requiring `PUBLISHED`+ attempted on `DRAFT` |
| 527 | `CUSTODY_PRECONDITION_NOT_MET` | 409 | Transit/drop/POD action attempted before `PICKED_UP` |
| 528 | `TERMINAL_STATE_IMMUTABLE` | 409 | Mutation attempted on `COMPLETED` or a cancelled terminal |
| 529 | `CONCURRENT_TRANSITION_SUPERSEDED` | 409 | Target state changed between read and write — optimistic-lock mismatch |
| **567** | **`EXCEPTION_CASE_TRANSITION_INVALID`** | **409** | **[ASSEMBLER ADDITION, closing F3's explicitly-named gap]** Generic — target ∉ `allowed_next(current)` for `ExceptionCase.status` (§3.3's new case-transition set: `OPEN→{IN_REVIEW,RECOVERY_IN_PROGRESS,RESOLVED,CLOSED_UNRESOLVED}` etc.), mirroring `ERR-524`'s shape for the parallel case machine F3's split created. Allocated from F5's reserved range (567–599) since F3's split postdates F5's draft. |

### 7.4 Authorization — `ERR-530`–`533`

§4 owns the boundary; this is the code shape it emits through. **Rule:** default to
`RESOURCE_NOT_FOUND` whenever an actor knowing a resource *exists* is itself sensitive; use
`ACCESS_DENIED` only when the actor is already a visible party to the resource but lacks that
action's permission.

| ID | Code | HTTP | Trigger |
|---|---|---|---|
| 530 | `NOT_AUTHENTICATED` | 401 | Missing/invalid/expired token |
| 531 | `RESOURCE_NOT_FOUND` | 404 | Doesn't exist **or** exists-but-invisible, indistinguishably |
| 532 | `ACCESS_DENIED` | 403 | Known relationship, wrong role/permission for this action |
| 533 | `SCOPE_CONDITION_NOT_MET` | 403 | Permission exists abstractly; scope fails at evaluation |

### 7.5 Concurrency and race — `ERR-534`–`539`

Two bids at the same instant resolve **silently** (deterministic receipt-sequence order, `EC-500`) —
no code. Everything else here **must surface**.

| ID | Code | HTTP | Trigger | Traces to |
|---|---|---|---|---|
| 534 | `AWARD_TARGET_BID_WITHDRAWN` | 409 | Award computed against a bid withdrawn in the same window | `DEC-309` cascade |
| 535 | `POD_ALREADY_CAPTURED` | 409 | Second POD write for a load that already has one | second-actor race, not a replay |
| 536 | `INVOICE_ALREADY_ISSUED` | 409 | Duplicate invoice generation for one load | — |
| 537 | `TRUCK_ALREADY_COMMITTED` | 409 | Two dispatchers assign one truck to overlapping windows | §9; prevented structurally by `ENT-325`, this is the guard when it isn't |
| 538 | `ELIGIBILITY_LAPSED_MID_AUCTION` | 409 | Bid voided — authority/insurance lapses between bid and close | §8 |
| 539 | `CLAIM_CONCURRENT_UPDATE` | 409 | Two desks write conflicting claim outcomes | optimistic lock |

### 7.6 Idempotency — `ERR-540`–`543`

| ID | Code | HTTP | Trigger |
|---|---|---|---|
| 540 | `IDEMPOTENCY_KEY_REPLAY_MISMATCH` | 409 | Same key, **different** payload |
| 541 | `IDEMPOTENCY_KEY_REUSE_ACROSS_RESOURCE` | 409 | Same key bound to a different endpoint/resource than first use |
| 542 | `IDEMPOTENCY_KEY_IN_PROGRESS` | 409 | Retry fired while the first attempt with this key is still executing |
| 543 | `IDEMPOTENCY_KEY_EXPIRED` | 409 | Key presented after retention window |

### 7.7 External dependency failure — `ERR-544`–`549`

Per-dependency posture — **stop / degrade / proceed-and-flag** — answered once. A physical trip is
never auto-aborted by a data problem. Degrade/proceed-and-flag responses are **200s with a warning
in `details`**; only STOP produces an `ERR-`.

| ID | Code | HTTP | Dependency | Posture |
|---|---|---|---|---|
| 544 | `ELIGIBILITY_SOURCE_UNAVAILABLE_NO_FALLBACK` | 422 | FMCSA authority/safety feed | Degrade on cached snapshot within grace `[NEEDS INPUT]`; STOP only with no cache |
| 545 | `INSURANCE_VERIFICATION_UNAVAILABLE_NO_FALLBACK` | 422 | COI verification | Same posture |
| 546 | `SETTLEMENT_PROVIDER_UNAVAILABLE` | 503 | Payment/settlement | Degrade — queue, hold only `INVOICE_FINALISED→SETTLED` |
| 547 | `DOCUMENT_STORE_UNAVAILABLE` | 503 | Document/image store | STOP where structurally required — mitigated by offline queueing |
| 548 | `ESIGN_PROVIDER_UNAVAILABLE` | 503 | e-sign / rate-confirmation | `[NEEDS INPUT]` whether mandatory for `AWARD_ACCEPTED` |
| 549 | `UPSTREAM_DEPENDENCY_TIMEOUT` | 504 | Any uncatalogued upstream call | Generic fallback |

**Telematics/tracking has no STOP path at all** — always proceed-and-flag; stale-tracking is
`EC-502`, never an error, never halts or reverses a trip.

### 7.8 Offline and mobile — `ERR-550`–`553`

**Rule.** The canonical state machine, not wall-clock sync order, is authoritative. A queued event
is accepted at sync **only if still a legal transition from the load's current state**; otherwise
rejected and routed to human reconciliation — never silently applied, never silently dropped.

| ID | Code | HTTP | Trigger |
|---|---|---|---|
| 550 | `OFFLINE_QUEUE_CONFLICT_STATE_ADVANCED` | 409 | Queued event's precondition state no longer matches canonical state at sync — → `ERR-524` |
| 551 | `OFFLINE_QUEUE_EXPIRED` | 409 | Queued action exceeds retention before sync |
| 552 | `OFFLINE_TIMESTAMP_UNTRUSTED` | 422 | Device clock skew exceeds tolerance on a money-bearing timestamp |
| 553 | `OFFLINE_SYNC_ORDER_AMBIGUOUS` | 409 | Multiple queued events for one load sync out of causal order |

### 7.9 Money-adjacent failures — `ERR-554`–`560`

| ID | Code | HTTP | Trigger | Traces to |
|---|---|---|---|---|
| 554 | `PAYOUT_BLOCKED_CLAIM_OPEN` | 409 | Full settlement attempted while any invoice line is claim-held | — |
| 555 | `DEDUCTION_EXCEEDS_PAYABLE` | 422 | OS&D deduction produces a negative balance | `[NEEDS INPUT]` recovery |
| 556 | `ACCESSORIAL_EVIDENCE_MISSING` | 422 | Claimed accessorial has no supporting record | `[NEEDS INPUT]` default policy |
| 557 | `FACTORING_NOA_INVALID` | 422 | Forged or expired Notice of Assignment | flagged to fraud |
| 558 | `FACTORING_NOA_RELEASE_PENDING` | 409 | Carrier switched factors; prior NOA on file, no signed Release | — |
| 559 | `PAYEE_OF_RECORD_AMBIGUOUS` | 409 | Broker-vs-asset-holder payee undetermined at settlement | `[NEEDS INPUT]` payee rule |
| 560 | `PAYMENT_HELD_DOUBLE_PAY_RISK` | 409 | Undisclosed factoring found mid-dispute, after direct payment | — |

### 7.10 Generic / system — `ERR-561`–`566`

| ID | Code | HTTP | Trigger |
|---|---|---|---|
| 561 | `RATE_LIMIT_EXCEEDED` | 429 | Headers per §1; limits `[NEEDS INPUT]` |
| 562 | `INTERNAL_ERROR` | 500 | Unclassified — generic user message, detail only in logs + `trace_id` |
| 563 | `SERVICE_UNAVAILABLE_MAINTENANCE` | 503 | Planned maintenance window |
| 564 | `METHOD_NOT_ALLOWED_ON_RESOURCE` | 405 | Verb misuse — e.g. delete on an immutable audit record |
| 565 | `REQUEST_ENTITY_TOO_LARGE` | 413 | Document/image upload exceeds size limit `[NEEDS INPUT]` |
| 566 | `API_VERSION_UNSUPPORTED` | 410 | Deprecated/unsupported version requested |

### 7.11 Partial-failure handling

The mutating core of any transaction is atomic at the DB boundary; **side effects are decoupled and
retried independently** — a failed `load.awarded` webhook never rolls back the committed award. Any
batch/bulk endpoint returns a per-item result array, not one aggregate status; whether batch
endpoints exist is `[NEEDS INPUT]`.

### 7.12 Human-safe messaging — two layers, one code

`message` is always safe for a user; `details` is structured and machine-safe — **never** a raw
exception, stack trace, SQL constraint, or vendor name. The `code`→driver-copy mapping is a
presentation-layer table, not a new error class — §11/§12 own it.

### 7.13 `EC-` register — failures the system absorbs, not rejects (15)

| ID | Trigger | Behaviour | Who decides | Unresolved |
|---|---|---|---|---|
| EC-500 | Two bids at the same instant | Resolved silently, deterministic receipt-sequence order | Platform | Sequencing granularity `[NEEDS INPUT]` |
| EC-501 | Idempotent replay, identical key + payload | Original response returned verbatim | Platform | — |
| EC-502 | Telematics/tracking feed goes silent | Stale-tracking flag only; trip never auto-aborted | Platform | Silence interval `[NEEDS INPUT]` |
| EC-503 | COI/authority lapses between `AWARDED` and `PICKUP_SCHEDULED` | Flagged for ops review, not auto-cancelled | §13 | Grace window `[NEEDS INPUT]` |
| EC-504 | Authority/insurance lapses mid-transit, post-custody-transfer | Flagged, no automatic transit action | §13/§9 | — |
| EC-505 | Consignee signs clear without inspecting | Stored as clear; undetectable at capture | — | Real-world limit |
| EC-506 | Declared vs. scale weight, small margin | Notice only, not rejected | §9 | Tolerance band `[NEEDS INPUT]` |
| EC-507 | Ceiling set below plausible market rate | Warned at publish, never blocks | Shipper | — |
| EC-508 | Detention accrues from slow unloading | Timestamp fact captured; fault attribution deferred | §10 | Fault rule `[NEEDS INPUT]` |
| EC-509 | Shipper cancels post-pickup, pre-delivery | Allowed, with a financial consequence — contrast `ERR-516` | — | — |
| EC-510 | Offline event syncs in causal order matching canonical state | Applied silently, no reconciliation needed | Platform | — |
| EC-511 | Awarded carrier declines | First-class outcome (`AWARD_DECLINED`), cascades per `DEC-309` | Platform | Cascade vs. re-auction `[NEEDS INPUT]` |
| EC-512 | Winner holds broker authority, disclosed | Permitted, subject to disclosure — contrast `ERR-519` | — | — |
| EC-513 | Very-new authority bids | Age visible at review, no auto-block on age alone | §16.3, `DEC-201` | Threshold `[NEEDS INPUT]` |
| EC-514 | Exact tie at lowest price | Tie-break rule resolves deterministically | Platform | Which order `[NEEDS INPUT]` |

**Counts:** 68 ERR (67 original + 1 assembler-added) · 15 EC · 23 `[NEEDS INPUT]`.

---

## 8. F6 — Auction & Bidding Engine

*Full source: `frd-F6-auction-engine.md`. `eligibility()` call surface corrected to §15's canonical
four-argument form — see the boxed note in §8.1 and §16.3 for the full reconciliation. F6's own
`CHALLENGE` (that no agent owned carrier vetting) is the reason §15/F13 exists at all — resolved,
not still open.*

**Owns:** auction lifecycle execution · bid intake/validation · eligibility-gate *application* ·
award execution · the selection record · anti-gaming controls · timers/closing. **Eligibility
computation itself is §15's (F13)** — F6 calls it, never re-derives it.

### 8.1 Eligibility gate — computed per tuple, re-evaluated twice, never cached as a set

**FR-600.** At `AUCTION_OPEN` the eligible pool is *not* materialised as a fixed list. Each bid
submission triggers a fresh call to
**`eligibility(carrier_id, truck_id, driver_id, load_id) → {status: ELIGIBLE|INELIGIBLE, reasons[],
gate_version, policy_version, evaluated_at, snapshot_id}`** (BR-200/BR-301).

> **[ASSEMBLER FIX — the eligibility signature conflict, resolved].** F6's original draft wrote this
> as `eligibility(carrier, authority, insurance, safety_signal, truck, driver, load)` — seven
> arguments, implying the *caller* resolves authority/insurance/safety_signal before calling. §15
> (F13) filed a `CHALLENGE` against this exact line: that is BRD A2's *tuple concept* — what gets
> evaluated — not the *call surface* — what gets passed in. F13 resolves authority, insurance, and
> the safety signal **internally** from `carrier_id`; the caller never holds or passes them.
> **F13's four-argument form is adopted as canonical throughout this document** (§15 FR-1300, §6.2
> `API-468`, §15 `API-1300`). F6's own text below is corrected to match; no behavioural
> disagreement existed between the two agents, only a call-surface ambiguity that would have
> produced two incompatible client implementations if shipped as originally drafted by each.

A truck ELIGIBLE at open and committed elsewhere five minutes later is INELIGIBLE at its own bid
attempt — checked at the moment of the act, never off an earlier snapshot.

**FR-601.** Bid submission is rejected (`BID_CARRIER_INELIGIBLE`, `details.reasons[]` from the gate)
if the tuple fails at submission. An ineligible price is never recorded as a bid row — only as a
rejected-attempt event.

**FR-602.** At `AUCTION_CLOSED → AWARD_PENDING` the engine re-runs `eligibility()` for every recorded
bid, in price order, **not just the apparent winner** — voiding the leader must fall through without
a second pass. First tuple to re-pass becomes the candidate; every tuple checked (pass or fail) is
written to the selection record (§8.2) with its own `gate_version` and `evaluated_at`.

**FR-603.** A candidate that re-fails does not silently drop — the bid row transitions to
`VOIDED_INELIGIBLE_AT_AWARD` and the loop continues down price order. Pool exhausted with no pass →
`AUCTION_FAILED_NO_ELIGIBLE_CARRIER` even though bids existed at close.

**FR-604.** `eligibility()`'s data freshness is §15's cadence decision (`DEC-1300`/`DEC-1301`), not
F6's — F6 records `gate_version` and `evaluated_at` and assumes nothing about currency.

### 8.2 The selection record — evidence, written progressively, sealed at award

Not a log line; a reconstructable exhibit (BR-303, merged BR-802 per `DECISIONS.md`). Three
append-only write points on the same `selection_record` (`ENT-312`) keyed to the auction:

| Write point | Trigger | Content appended |
|---|---|---|
| **Per bid** | Each valid bid accepted (FR-610) | bidder org, tuple ref, price, server-receive timestamp, idempotency key, gate result + `gate_version` at that instant |
| **At close** | `AUCTION_CLOSED` (FR-630) | frozen bid-price ordering, tie-break rule applied if any, close-job run id, closing timestamp, pool size/bid count |
| **At award** | `AWARD_PENDING` resolves | for every candidate walked in FR-602: gate result + version + evidence pointers (as returned by §15, not re-derived here); the winner; the rule applied; **every excluded bidder with the specific reason** |

**FR-605.** Immutable once each write point completes — a correction is a new addendum row.
Retention `[NEEDS INPUT: Carmack/negligent-selection limitation period]`.

**FR-606.** Reconstructable **from stored data alone**, no live re-query at read time — the
acceptance test for BR-303, and the exact property §15's FR-1303 independently guarantees for its
own snapshot (the two are consistent by construction, not by coincidence — §15's evaluation record
*is* what F6's selection record quotes).

**FR-607.** Every gate or ranking override (FR-640) is written with the overriding user's identity
and stated reason; an override with no identity/reason cannot be persisted. **This is the same
override path formalized at §4.3's new contested-action row and §4.2's `PERM-260`.**

### 8.3 Bid intake and validation

**FR-610.** `POST /v1/loads/{id}/bids` requires an `Idempotency-Key` header; a retried key with
identical payload returns the original bid (`BID_DUPLICATE` if payload differs under the same key).

| Case | Result | Error code |
|---|---|---|
| Below configured floor (`DEC-306`, if set) | Rejected, not recorded | `BID_BELOW_CEILING` *(ceiling is a max, not a floor — a literal reserve-floor is not in BRD scope)* |
| Malformed | Rejected | `BID_MALFORMED`, `field` set |
| From now-ineligible carrier | Rejected, logged as attempt | `BID_CARRIER_INELIGIBLE` |
| After close | Rejected | `AUCTION_CLOSED` |
| Duplicate idempotency key, same payload | Original bid returned, 200 not 201 | — |
| Duplicate key, different payload | Rejected | `BID_DUPLICATE` |
| Withdrawal pre-close | Allowed only if `[NEEDS INPUT]` policy permits; recorded against bidder regardless | `BID_WITHDRAWN` (informational on success) |
| Withdrawal post-close, pre-award | Treated as a decline-equivalent | `BID_WITHDRAWAL_POST_CLOSE` |
| Re-trade / unrecorded price change post-award | Never silently accepted; requires a recorded change object or it is unpayable | `RETRADE_UNRECORDED` |

**FR-611.** An accepted bid is a firm commitment until close; no in-place price edit — a changed
price is a new bid superseding the prior one for ranking, both retained. **FR-612.** Re-trade
attempts increment a per-carrier, per-lane counter, read by §15's vetting domain and A8's fraud
surface — consumers, not owners.

### 8.4 Timers and closing — a missed close has money attached

**FR-630.** Close runs via a scheduled job holding an exclusive, idempotent close-token per auction;
a second invocation is a no-op returning the already-recorded close event. **FR-631.** If the close
job is late, the auction closes **using bids that existed at the nominal boundary**; late-arriving
bids in the gap are rejected as `AUCTION_CLOSED`, timestamp-adjudicated. `[NEEDS INPUT: grace-period
auto-extend instead — DEC-312]`. **FR-632.** If down across a scheduled close entirely, every
auction past nominal close closes against its frozen boundary bid set before new intake resumes.
**FR-633.** Anti-snipe extension (`DEC-305`), if enabled, triggers inside a configured window before
close; count and total elapsed extension are capped `[NEEDS INPUT]`. **FR-634.** `AWARD_PENDING` is
time-boxed (BR-309); expiry with no accept/decline moves to `AWARD_LAPSED` automatically.

### 8.5 Failure paths → §3.3 states

| BRD condition | State | F6 behaviour |
|---|---|---|
| Zero bids at close | `AUCTION_FAILED_NO_BIDS` | Selection record still written (empty), pool size 0 |
| No eligible carrier at open, or all bids fail FR-602 | `AUCTION_FAILED_NO_ELIGIBLE_CARRIER` | Every rejected/voided attempt retained as evidence |
| All bids above shipper ceiling (`DEC-306`) | `AUCTION_FAILED_ALL_ABOVE_LIMIT` | Bids retained; accept-above-ceiling choice `[NEEDS INPUT]` |
| Exact tie at lowest eligible price | Resolved before state change | Deterministic pre-published order, `[NEEDS INPUT: basis]` |
| Winner declines / never responds | `AWARD_DECLINED` / `AWARD_LAPSED` | → `DEC-309` cascade-vs-re-auction, `[NEEDS INPUT]` |

### 8.6 Anti-gaming controls

| Pattern | Detected how | Recorded | Ops-desk action |
|---|---|---|---|
| Shill/spoiler bidding | Bidder org resolved against shipper/platform org at submission | Hard-blocked, not just flagged | None — rejected inline |
| Related-party double bid | Ownership-link check from §15's vetting domain, at bid time | Second bid rejected, first stands | None — rejected inline |
| Broker bids as broker-of-record and via undisclosed sub-carrier | Identity/authority-type resolution flags broker bids visibly | Flag visible pre-award | Shipper/ops decide at award |
| Collusion / rotation on a repeat lane (Sherman Act §1) | Pattern monitor over re-trade counter + win/price history per carrier-lane | Flagged, never auto-penalised | Ops/counsel — F6 does not adjudicate antitrust exposure |
| Bid-shading / probing | Bid-revision rate per bidder per auction | Flagged when `DEC-303` = standing-best | `[NEEDS INPUT: rate-limit threshold]` |
| Implausible low bid | Compared to fuel-floor cost *signal* (`DEC-LOCK-002`, flag-only) | Flagged in selection record | Ops warn-or-hold `[NEEDS INPUT]` |

**FR-640.** Every flag is written to the selection record at the write point it occurred; proceeding
despite an open flag requires FR-607's override.

### 8.7 Configurability — eleven open parameters as settings, not constants

Each is a field on a per-auction, shipper-overridable **auction ruleset** (`ENT-` TBD, F3 to add).
**Editing this ruleset requires `PLATFORM_CONFIG_ADMIN` (§4.1 `ROLE-230`, `PERM-264`)** — the role
this assembly added specifically because this table needed an owner and had none. All defaults
`[NEEDS INPUT]`.

| DEC | Setting | Type | Default |
|---|---|---|---|
| DEC-302 | `bid_visibility_mode` | enum `OPEN` \| `SEALED` | `[NEEDS INPUT]` — **§16.1 build-blocking** |
| DEC-303 | `price_disclosure_mode` | enum `STANDING_BEST` \| `RANK_ONLY` | `[NEEDS INPUT]` — **§16.1 build-blocking** |
| DEC-304 | `duration_seconds`, `duration_basis` | int, enum | `[NEEDS INPUT]` |
| DEC-305 | anti-snipe params | bool/int | `[NEEDS INPUT]` |
| DEC-306 | `ceiling_price`, `ceiling_disclosed` | decimal, bool | `[NEEDS INPUT]` |
| DEC-307 | `shipper_decline_right` | enum | `[NEEDS INPUT]` — Boss decision pending |
| DEC-308 | `shipper_early_close_allowed` | bool | `[NEEDS INPUT]` |
| DEC-309 | `award_failure_mode` | enum `CASCADE`\|`RE_AUCTION` | `[NEEDS INPUT]` |
| DEC-310 | `thin_market_mode` | enum, see §8.8 | `[NEEDS INPUT]` |
| DEC-311 | `min_decrement` | decimal | `[NEEDS INPUT]` |
| DEC-312 | `close_calendar` | enum | `[NEEDS INPUT]` |

**FR-650.** Ruleset changes mid-auction are blocked; fixed at `AUCTION_OPEN`, carried into the
selection record's close-event so a later dispute can prove which rules governed.

### 8.8 Thin-market behaviour

**FR-660.** `bid_count < 2` or `eligible_pool_size < 2` at close sets `thin_market = true`
regardless of outcome. **A one-bidder auction is not awarded silently as a normal close.** Per
`thin_market_mode` (`DEC-310`): `AWARD_ANYWAY` (labelled), `EXTEND_AND_REOPEN` (bounded retry,
`[NEEDS INPUT]`), `CEILING_TEST_ONLY` (needs `DEC-306` set), `FALLBACK_POSTED_RATE` (hands off to a
non-auction flow), `ESCALATE_TO_OPS_DESK`. No default.

### 8.9 API surface

| ID | Endpoint | Notes |
|---|---|---|
| API-600 | `POST /v1/loads/{id}/bids` | Idempotency-Key required |
| API-601 | `DELETE /v1/loads/{id}/bids/{bid_id}` | Withdrawal, subject to policy |
| API-602 | `GET /v1/loads/{id}/auction` | State + `DEC-303` price disclosure, scoped by §4 |
| API-603 | `GET /v1/loads/{id}/selection-record` | Ops + involved parties only, scoped by §4 |
| API-604 | `POST /v1/loads/{id}/award/accept\|decline` | Idempotency-Key required |
| API-605 | `POST /v1/loads/{id}/award/override` | FR-607 identity+reason required |

### 8.10 Events

`EVT-600`–`614` (superseded by §12's catalog per §16.6, same reconciliation logic as §6.5):
`auction.opened/extended/closed/failed_no_bids/failed_no_eligible_carrier/failed_all_above_limit` ·
`bid.accepted/rejected` · `award.pending/accepted/declined/lapsed/voided_ineligible` ·
`retrade.flagged` · `anti_gaming.flagged`. **The last two have no §12 equivalent at all** — a
genuine gap, §16.6.

### 8.11 Edge case register (23)

| ID | Trigger | Behaviour | Decides | Unresolved |
|---|---|---|---|---|
| EC-600 | Truck eligible at open, committed before its bid | FR-600 re-checks per bid; rejected | Automatic | — |
| EC-601 | Truck eligible at bid, lapses before award | FR-602 walks to next candidate | Automatic | — |
| EC-602 | Every bid fails re-verification at award | `AUCTION_FAILED_NO_ELIGIBLE_CARRIER` despite bids existing | Automatic | Re-auction default? |
| EC-603 | Close job runs twice | FR-630 token → no-op | Automatic | — |
| EC-604 | Close job late by minutes/hours | FR-631 closes against nominal boundary | Automatic | Grace-extend instead? `[NEEDS INPUT]` |
| EC-605 | System down across scheduled close | FR-632 closes on restart before new intake | Automatic | — |
| EC-606 | Award-lapse job itself fails to run | Award sits in `AWARD_PENDING` past window undetected | — | Needs a watchdog; owner `[NEEDS INPUT]` |
| EC-607 | Bid arrives in the gap between boundary and actual close run | Rejected `AUCTION_CLOSED`, timestamp-adjudicated | Automatic | — |
| EC-608 | Two bids at the same server timestamp | Needs sub-ms/sequence tiebreak | Platform | Granularity `[NEEDS INPUT]` |
| EC-609 | Idempotency key reused, different payload / retried after drop | `BID_DUPLICATE` on mismatch | Automatic | — |
| EC-611 | Withdrawal request post-close, pre-award | Treated as decline-equivalent | Policy | Distinct penalty from true decline? |
| EC-612/613 | Re-trade demanded at dock — shipper refuses / accepted under pressure | No cancellation ladder on refusal; acceptance = exception record, not overwrite | Automatic | — |
| EC-614 | Anti-snipe extension chain runs past pickup lead time | FR-633 cap; hard stop if exceeded | Platform | Cap value `[NEEDS INPUT]` |
| EC-615 | Shipper cancels mid-auction | Auction voided, bidders notified same instant | Automatic → §12 | — |
| EC-616 | Load materially amended mid-auction | Bids priced against stale freight — must void | Automatic | Re-auction vs re-bid `[NEEDS INPUT]` |
| EC-618 | Repeated re-auctions produce no bids | Freight ages against appointment, no cap | Ops | Cap-before-escalation `[NEEDS INPUT]` |
| EC-619 | Ruleset changed while auction open | FR-650 blocks; rejected | Automatic | — |
| EC-621 | Broker wins, downstream asset-carrier not yet vetted | Award proceeds provisionally; dispatch-gate blocks dispatch, not this engine | Automatic + external gate | — |
| EC-622 | Thin-market threshold met only after a late withdrawal | Recompute `thin_market` at close, not at last-bid time | Automatic | — |
| EC-623 | Standing-best price mode leaks rival cost structure over repeat lane | Feeds §8.6 pattern monitor | Ops/counsel | Fix is `DEC-303`'s choice — §16.1 |
| EC-624 | Override forces award despite an open anti-gaming flag | Requires FR-607 identity+reason; never silent | Named person | — |
| EC-625 | Selection-record write fails mid-transaction | Award must not reach `AWARD_PENDING` without a complete write | Automatic | Mechanism → §7/§14 |

**CHALLENGE, resolved.** F6's original `CHALLENGE` — "no FRD owner for carrier/authority/insurance/
safety vetting and eligibility computation... the gate is under-specified end to end" — is why §15
(F13) exists. Recorded here for the historical record, not as an open item.

**Counts:** 19 FR · 6 API · 15 EVT (superseded) · 23 EC · 30 `[NEEDS INPUT]`.

---

## 9. F7 — Driver, Equipment/Trailer Taxonomy, Assignment, Hours of Service

*Full source: `frd-F7-driver-equipment-hos.md`. Entities superseded into §3.1/§3.2 (`ENT-302`/303/
304/305/325) — this section keeps F7's full requirement content, which applies to those consolidated
entities.*

**Owns:** driver records/qualification, equipment taxonomy incl. trailers, driver+truck assignment,
availability/double-commitment, driver lifecycle, HOS tension. **Not owned:** gate mechanics (§15),
fraud classification (§13), transit execution (§10), POD (§11), auction (§8), permission engine (§4
— rows only), privacy controls (§14 — classes flagged only).

### 9.1 Equipment taxonomy — the BRD-defect finding

**`CHALLENGE` (accepted at §3.1.1; recorded as a BRD defect, §16.4, not silently patched):** BRD
`BR-209`/`BR-214` and `BR-111` model equipment as one asset per carrier row, and `BR-111`'s closed
set omits **tanker**.

| ID | Requirement | MoSCoW | Traces |
|---|---|---|---|
| FR-700 | Tractor and Trailer are independently identified assets, each with own availability; never one merged record. | Must | ext. BR-209 |
| FR-701 | Extensible trailer-type taxonomy: dry van, reefer, flatbed, step deck, tanker, power-only — not a hard-coded enum. | Must | ext. BR-111/209 |
| FR-702 | Reefer: settable temp range (min/max) + mode (continuous-run vs cycle/set-and-hold); matched against load's declared requirement. | Must | §15 |
| FR-703 | Flatbed/step deck: deck-height offset + on-hand securement (tarps/straps/chains/coil racks) as match-usable attributes. | Should | OBJ-003 |
| FR-704 | Tanker: commodity class rated/cleaned for (food-grade vs chemical), compartment count, wash-out flag. | Should | OBJ-003/006 |
| FR-705 | All trailers: length, interior height/width, door type, max weight, axle count. | Must | OBJ-003/004 |
| FR-706 | Power-only tractor (no owned trailer) valid; eligibility needs a shipper/broker drop trailer or a pairing — modelled as pairing, not gate failure. | Should | `[NEEDS INPUT: drop-trailer pools in scope?]` |
| FR-707 | Tractor/trailer attributes checked independently vs load requirement; compliant tractor + incompatible trailer = ineligible even if carrier clears the gate. | Must | §15 |
| FR-708 | Trailer ownership/lease/pool status informational, not a hard gate absent Boss instruction. | Could | `[ASSUMPTION: conf: med]` |

### 9.2 Assignment, pairing, substitution

| ID | Requirement | MoSCoW | Traces |
|---|---|---|---|
| FR-710 | `EquipmentPairing` (`ENT-305`) is the unit dispatched per leg; may change within one load's lifecycle (drop-and-hook) without changing carrier-of-record or the driver. | Must | ext. BR-212 |
| FR-711 | Bind (driver, tractor, trailer, carrier) at dispatch acceptance, per leg for multi-leg loads. | Must | ext. BR-212 |
| FR-712 | Disclosed trailer swap mid-transit = custody event (§10 BR-402/407), not a mismatch signal; undisclosed swap follows BR-224. | Must | §10, BR-224 |
| FR-713 | Substitution before pickup re-checks eligibility on the new tuple; after custody transfer, additionally requires a §10 custody event. | Must | §15, §10 |
| FR-714 | At pickup, arriving driver+tractor+**trailer** checked against the bound Assignment — extends BR-221, which omitted trailer. | Must | ext. BR-221 |
| FR-715 | Post-`AWARD_ACCEPTED`, pre-pickup Assignment change logged with requester/reason; doesn't alter the award record. | Must | derived |
| FR-716 | Assignment state queryable independent of load state (e.g. `IN_TRANSIT` load, mid-trip-relayed Assignment). **[flagged unresolved at §3.1 — `Trip` vs. a separate `Assignment` entity]** | Should | derived |

### 9.3 Availability and double-commitment

| ID | Requirement | MoSCoW | Traces |
|---|---|---|---|
| FR-720 | Driver, tractor, trailer each hold independent time-windowed availability (`ENT-325`, §3.1.2); overlapping-window double-commitment blocked per-asset. | Must | ext. BR-214 |
| FR-721 | Trailer dropped at dock transitions to a location-based state distinct from "committed to a load" — pairs with a different tractor while the original departs. | Should | Boss's drop-and-hook instruction |
| FR-722 | Driver self-declared unavailability doesn't release a committed tractor/trailer, and vice versa — states correlate, never collapse. | Should | ext. BR-216 |
| FR-723 | Driver belongs to exactly one carrier org unless §4 explicitly supports multi-carrier lease-on. | Must | `[NEEDS INPUT: lease-on drivers in scope?]` |

### 9.4 Driver qualification — captured, verified, stored

Minimisation (BR-707/709) governs every row: **attestation + expiry only.** These fields extend
`ENT-302` (Driver) per §3.1's fold-in decision.

| ID | Requirement | MoSCoW | Verifier/Holder |
|---|---|---|---|
| FR-730 | CDL class (A/B/C, 49 CFR 383.91 `[verify GVWR thresholds]`) + endorsements (H/N/T/combo, 383.93). | Must | Self-attested; optional doc image = evidence-of-currency, not verified lookup. |
| FR-731 | CDL verification defaults to self-attestation; live CDLIS/PSP-class lookup is optional. | Should | `[NEEDS INPUT: live CDL-verification integration in scope?]` |
| FR-732 | DOT medical-cert **expiry date only**, never exam result/condition. | Must | Carrier is system of record (391.51 DQ file `[verify]`); platform holds expiry+attestation. |
| FR-733 | Clearinghouse currency as dated attestation — no result, violation, or return-to-duty status. | Must | Carrier queries (382.301/.305); platform stores attestation date only. |
| FR-734 | Endorsement-to-load match: hazmat load (BR-719) or tanker trailer requires matching driver endorsement, checked with tractor/trailer type. | Must | §15, §5 |
| FR-735 | Every qualification field records verifier-type (self/carrier/platform-doc-check/third-party) + verified-at. | Must | derived |

### 9.5 Driver lifecycle

| ID | Requirement | MoSCoW | Traces |
|---|---|---|---|
| FR-740 | Driver record created by employing carrier org (or owner-operator self); exists independent of login credentials. | Must | derived |
| FR-741 | Driver leaving deactivates from new Assignments; in-flight Assignments flagged for ops review, not auto-cancelled. | Must | ext. BR-230 |
| FR-742 | Driver abandonment mid-trip = §10's `TRANSIT_EXCEPTION`; F7 supplies only the state change (`ASSIGNED → UNAVAILABLE`) §10 consumes. | Must | §10 |
| FR-743 | Owner-operator: one person is carrier account + equipment owner + driver at once — not three artificial records; §4's bid-vs-accept-award split still applies, distinctly granted even if self-granted. | Must | §4, BR-902 |

### 9.6 The Hours-of-Service tension — options, not a pick

Boss wants driving-hours tracking. §14 (F12, carrying A7) already locked **no ELD, Clearinghouse, or
D&A data stored absent a lawful basis.** Not reconcilable by engineering alone — **`DEC-700` is the
fork.**

| Option | What it does | Fulfils ask? | Liability | Cost | Conflicts |
|---|---|---|---|---|---|
| **A — No HOS feature.** No hours field anywhere; carrier alone bears Part 395. | Nothing shown | No | Lowest, zero new exposure | None | Downgrades BR-708 to not-built — a named Boss decision |
| **B — Derived planning signal.** Bounded, attested "hours available this window" at bid/dispatch → FEASIBLE/INFEASIBLE flag vs. transit estimate; flag persisted, raw value discarded. ELD is one optional *source* of the same bounded value, never a raw duty stream. | Partial — signal, not a log | **Real but bounded.** The negligent-selection logic that hit Boss's own auction (`Montgomery`) extends to "negligent scheduling" if the flag is wrong/ignored. | Moderate — needs a documented lawful basis + retention rule *before* build | Satisfies the minimisation constraint if raw value not retained |
| **C — Full system of record.** Ingest ELD telematics, store RODS-equivalent logs, real-time dashboard, authoritative. | Fully | **High** — platform becomes what an auditor/plaintiff subpoenas | High — retention ≈ 395.8(k), multi-vendor ELD surface | **Reverses the already-locked minimisation constraint.** Silent build overrides a recorded decision |

**`DEC-701` (only if B):** input source (driver self-report / dispatcher-report / optional
ELD-capability read) `[NEEDS INPUT]`; INFEASIBLE hard-blocks vs. warns only `[NEEDS INPUT]`.

| ID | Requirement (conditional) | MoSCoW |
|---|---|---|
| FR-750 | **[B]** Bounded attested "hours available" at bid/dispatch; never a full RODS/ELD export. | Must-if-B |
| FR-751 | **[B]** FEASIBLE/INFEASIBLE vs. estimated transit time; warning only absent a Boss decision to hard-gate. | Should-if-B |
| FR-752 | **[B]** Persist only flag+timestamp on the award record; discard the raw value after use. | Must-if-B |
| FR-753 | **[B]** ELD integration is an optional capability supplying the same bounded value — no vendor, never a raw stream. | Must-if-B |
| FR-754 | **[A]** No hours field/computation/display exists; BR-708 downgrade is a named Boss decision. | Must-if-A |
| FR-755 | **[C]** Out of scope absent an explicit Boss override. | — |

### 9.7 Driver personal data (§14 owns controls)

| ID | Requirement | MoSCoW | Traces |
|---|---|---|---|
| FR-760 | Driver PII classified as sensitive personal data under state privacy statutes at schema level. | Must | §14 |
| FR-761 | Driver often not account holder — carrier org's role (controller vs. processor) `[NEEDS INPUT]`, same shape as consignee's unresolved consent. Data classes flagged only. | Must | §14 |

### 9.8 Permission rows (§4 owns the engine)

Already folded into §4.2's matrix at `PERM-219` (Assignment create/change). F7's original narrower
rows (driver view own Assignment, driver update own AvailabilityWindow, dispatcher create/edit
Driver/Tractor/Trailer, owner deactivate Driver, platform ops view qualification fields) are
consistent with §4's matrix's existing `own_org`/`assigned_load` scopes and needed no separate PERM
row — no new addition required here.

### 9.9 API, events, errors, NFRs

**API-700–707:** `/v1/carriers/{id}/drivers` · `/v1/drivers/{id}` ·
`/v1/carriers/{id}/equipment/tractors` · `/v1/carriers/{id}/equipment/trailers` ·
`/v1/loads/{id}/assignment` (POST bind, PATCH substitute, GET) · `/v1/drivers/{id}/availability` ·
`/v1/loads/{id}/hos-feasibility-check` `[if B]`.

**EVT-700–708** (superseded by §12's catalog per §16.6): `driver.created` · `driver.deactivated` ·
`equipment.tractor.created` · `equipment.trailer.created` · `assignment.bound` ·
`assignment.substituted` · `assignment.mismatch_detected` (→ §13 BR-806) · `trailer.dropped`/`hooked`
(→ §10) · `hos.feasibility_flagged` `[if B]`.

**ERR-700–706:** `DRIVER_INELIGIBLE_FOR_LOAD` · `EQUIPMENT_TYPE_MISMATCH` ·
`EQUIPMENT_ALREADY_COMMITTED` · `DRIVER_ALREADY_COMMITTED` · `ASSIGNMENT_TUPLE_INCOMPLETE` ·
`ARRIVAL_MISMATCH` (feeds BR-221/224) · `HOS_INFEASIBLE_WINDOW` `[if B]`.

**NFR-700:** no ELD/HOS/Clearinghouse raw-data field exists absent `DEC-700` B/C with a documented
lawful basis. **NFR-701:** every qualification/availability field is verifier- and time-attributed.

### 9.10 Edge case register (13)

| ID | Trigger | Behaviour | Who decides | Unresolved? |
|---|---|---|---|---|
| EC-700 | Driver lacks endorsement for an already-assigned hazmat/tanker load | Hold, `ERR-700`, same-shift review | ops | No |
| EC-701 | Trailer temp range doesn't cover load requirement, found post-bid | Assignment blocked, not auto-cancelled | dispatcher/ops | No |
| EC-702 | CDL/medical cert/Clearinghouse attestation lapses mid-trip | Driver → `INELIGIBLE_FOR_NEW_BIDS`; current trip not auto-stopped | ops | Whether current trip continues is a policy call |
| EC-704 | Trailer breakdown/reefer failure mid-transit | §10's `TRANSIT_EXCEPTION`; F7 only flips TrailerAsset state | §10 | No |
| EC-705 | Owner-operator's sole driver unavailable mid-trip, no org substitute | No internal relay; becomes §10's carrier-failure path | §10/carrier | Genuinely hard — no internal substitution exists |
| EC-706 | Driver leased to two orgs bids the same window from both | Double-commitment block (FR-720) | system | Only if FR-723 in scope |
| EC-707 | Shared trailer pool at dock, drop-point ownership ambiguous | VIN/plate resolves it, not "whose pool" | §10/§15 | `[NEEDS INPUT]` drop-pool ownership model |
| EC-708 | Power-only tractor arrives, shipper-supplied trailer not present | `PICKUP_REFUSED`/hold — existing §10 table applies | §10 | No |
| EC-709 | Disclosed drop-and-hook but arriving trailer VIN ≠ disclosed swap | New trailer-identity signal — fraud vector not named in the fraud typology | §13 | **Yes — recommend adding a trailer-identity fraud type** |
| EC-710 | Driver deactivated for cause mid-trip | FR-741 flags Assignment; trip not auto-stopped | ops | No |
| EC-712 | HOS attested value (Option B) proves false after an incident | Attestation-only design tested in court | counsel | Yes — inherent to Option B |
| EC-713 | Ops needs to override a mismatch (verified benign cause) | Named-person override + reason | ops (named) | No |
| EC-714 | Driver never individually onboarded to platform | Assignment binds via carrier-entered record; POD binds per BR-903 | derived | No |

### 9.11 F7's own summary, preserved verbatim

**6-line summary.** Split tractor and trailer into independent assets with own availability so
drop-and-hook is first-class, not an exception; built a full trailer taxonomy with type attributes,
flagging BR-111's closed set is missing tanker. Extended driver+equipment binding (BR-212/221) to
name trailer explicitly — undisclosed trailer swaps are a fraud vector the existing typology doesn't
name yet. Kept every driver-qualification field to attestation-plus-expiry, never the underlying
record. Resolved the HOS tension into three options — did not pick, Boss's call.

**Three sharpest questions only Boss can answer** (F7's own, still open): (1) HOS fork `DEC-700` —
Option A or Option B? Won't build Option C without an explicit override. (2) Is a shipper/broker-
owned drop-trailer pool in scope, or is every trailer carrier-owned (FR-706)? (3) Do owner-operators
need to lease on to more than one carrier org, or is one-driver-one-carrier fine (FR-723)?

**Counts:** 38 FR (6 HOS-conditional) · 8 API · 9 EVT (superseded) · 13 EC · 8 `[NEEDS INPUT]` · 2
open `DEC-`.

---

## 10. F8 — Tracking, Telematics, ETA, Geofencing, Location Privacy

*Full source: `frd-F8-tracking-telematics.md`. Its `CHALLENGE-800` (field-level view masks) is the
reason §1/§4.4 has a granularity extension at all — resolved, folded into §4.2 as `PERM-261`–`263`.*

**Owns:** position ingestion · milestones · ETA · geofencing · dwell/detention detection · location
retention & privacy. **Not owned here:** permission rows (§4) · error codes (§7) · API envelope (§6)
· screens (§11) · HOS record (§9) · detention *rate*/invoicing (§8/A6) · entities (§3).

### 10.0 Principles

Three position sources, none guaranteed: ELD/telematics (carrier-controlled, refusable), driver
mobile app (best fidelity, needs cooperation + signal), phone call to ops (manual). System must work
with any one, a mix, or none — "dark" is first-class and visible (BR-401), never silently read as
"on schedule." Milestones outrank raw pings. A milestone is **derived** (system-inferred from
position) or **claimed** (asserted by a human act); never merged. Location is the **driver's**
personal location, not the account holder's — collection is trip-scoped and minimised by default.

### 10.1 Position ingestion & degraded mode

| ID | Requirement | MoSCoW | Traces |
|---|---|---|---|
| FR-800 | Accept position data from three independent capability classes (ELD feed, driver app, manual entry) as alternatives, never a mandatory stack. | Must | OBJ-002/004 |
| FR-801 | Every position record carries `source_type` and a `confidence_tier`; sources never blend into one unlabelled "position." | Must | OBJ-004/006 |
| FR-802 | Declining ELD/telematics never blocks the shipment; sets a `tracking_capability` flag at dispatch instead. | Must | OBJ-002 |
| FR-803 | No update within `[NEEDS INPUT: reporting interval]` while `IN_TRANSIT` → visible `NO_UPDATE_RECEIVED` state; last-known display stays age-labelled, never current. | Must | realises BR-401 |
| FR-804 | No position source at all → `TRACKING_UNAVAILABLE` from dispatch, distinct from `NO_UPDATE_RECEIVED`. | Must | small-carrier honest baseline |
| FR-805 | Manual updates use a bounded milestone/exception vocabulary plus free text, entered by an authenticated ops user; always visibly `MANUAL`. | Must | OBJ-004/006 |
| FR-806 | Source-type switches mid-trip are accepted without gap-filling fabricated positions for the uncovered interval. | Must | OBJ-006 |
| FR-807 | Repeated `NO_UPDATE_RECEIVED` beyond `[NEEDS INPUT]` feeds carrier scoring, not scored here. | Could | OBJ-006 |
| FR-808 | A driver's personal device/number is never the *only* compliance path; manual entry stays a fallback. | Must | OBJ-007 |

### 10.2 Milestones — derived vs claimed

Six per custody leg: arrived/loaded/departed at pickup, arrived/unloaded/departed at drop.
`arrived`/`departed` are **derived** from geofencing (§10.3). `loaded`/`unloaded` are **claimed** —
the pickup record and the POD signature, human acts F8 consumes, never overwrites.

| ID | Requirement | MoSCoW | Traces |
|---|---|---|---|
| FR-809 | `arrived_at_facility`/`departed_facility` derive exclusively from geofence enter/exit, each carrying its producing position record(s). | Must | OBJ-004 |
| FR-810 | `loaded`/`unloaded` source from the pickup record and the POD event; F8 consumes, does not generate, the claim. | Must | OBJ-004 |
| FR-811 | Every claimed milestone gets a `corroboration_status`: `CORROBORATED`, `UNCORROBORATED`, `NO_POSITION_DATA`. | Must | OBJ-004/006 |
| FR-812 | `UNCORROBORATED` never auto-labels a claim "fraud" or blocks it; it routes to ops/claims review only. | Must | →§13 if pattern repeats |
| FR-813 | Milestone records are immutable; a correction is a new, linked record with a reason, never an in-place edit. | Must | OBJ-004/006 |
| FR-814 | Full milestone sequence, including gaps, is queryable as one ordered timeline. | Must | OBJ-002/004 |
| FR-815 | Out-of-order milestones raise a data-quality flag, never silently reorder. | Should | §10.5 |
| FR-816 | Mid-trip relay/transload opens a fresh milestone set for the new leg; the prior leg closes untouched, carrying the matched geofence polygon (not just facility name). | Must | OBJ-004/006 |

### 10.3 Geofencing and dwell/detention

| ID | Requirement | MoSCoW | Traces |
|---|---|---|---|
| FR-818 | Every pickup/drop stop has a facility geofence polygon sourced from the load's declared location; radius/shape defaults `[NEEDS INPUT]`. No geofence → claimed-only milestones. | Must | OBJ-004 |
| FR-819 | Entry/exit requires sustained presence across `[NEEDS INPUT: debounce window]`, not one ping. | Must | OBJ-006 |
| FR-820 | A `DwellSession` opens on entry, closes on exit, holding start, end, every contributing position record. | Must | OBJ-004/005 |
| FR-821 | Dwell minus `[NEEDS INPUT: free-time hours]` (rate owned by A6) is exposed as `detention_candidate_minutes`; F8 emits evidence only, never bills. | Must | OBJ-005 |
| FR-822 | A `detention_candidate` on a manual-only trip is still constructible from claimed timestamps, tagged `MANUAL` tier, never blocked. | Must | `DEC-802` |
| FR-823 | A truck proximate but outside the polygon beyond `[NEEDS INPUT]` surfaces `PROXIMATE_NOT_GEOFENCED`, not silent exclusion. | Should | OBJ-005/006 |
| FR-824 | Early arrival still opens a `DwellSession`; whether pre-appointment dwell counts toward detention is A1/A6 policy. | Should | OBJ-005 |
| FR-825 | GPS-degraded oscillation is smoothed by FR-819's debounce; unresolved oscillation beyond `[NEEDS INPUT]` downgrades confidence rather than averaging noise away. | Should | OBJ-006 |

### 10.4 ETA

| ID | Requirement | MoSCoW | Traces |
|---|---|---|---|
| FR-826 | ETA computes from last known position (or last milestone), remaining truck-legal route time, and any attached work-zone/weather/chain-control event — capabilities, not vendors. | Must | OBJ-002/004 |
| FR-827 | Where the route/event feed's geography doesn't cover the corridor, ETA states coverage absent — never "no incident = clear." Work zones AZ/KS/MN/WA only; chain controls CA-only, licence `Unverified`. | Must | OBJ-006 |
| FR-828 | ETA recomputes on every new ping, milestone transition, `TRANSIT_EXCEPTION`, and on a `[NEEDS INPUT: recompute interval]` schedule when dark. | Must | OBJ-002/004 |
| FR-829 | ETA older than `[NEEDS INPUT: staleness threshold]` since last recompute is marked `STALE`, stays visibly timestamped. | Must | OBJ-006 |
| FR-830 | ETA is presented as a confidence tier (HIGH = live within interval; MEDIUM = manual/scheduled only; LOW/UNKNOWN = dark), never a bare timestamp implying precision the inputs lack. | Must | OBJ-004/006 |
| FR-831 | An open `TRANSIT_EXCEPTION` is carried as an explicit ETA factor, never a silent widening with no stated cause. | Must | §10 BR-405 |
| FR-832 | ETA may consume remaining drive-time as a feasibility input (§9 HOS signal) but never becomes a compliance record of hours. | Should | OBJ-002 |
| FR-833 | ETA is read/derived only; never blocks a state transition — distinct from the pre-bid route-feasibility gate. | Must | boundary |

### 10.5 Temporal honesty

| ID | Requirement | MoSCoW | Traces |
|---|---|---|---|
| FR-834 | Every position/milestone record carries `observed_at` and `received_at`, never collapsed into one field. | Must | OBJ-004/006 |
| FR-835 | `received_at − observed_at` beyond `[NEEDS INPUT: batch-lag threshold]` flags the record `BATCHED`; never surfaced as "live." | Must | OBJ-006 |
| FR-836 | Milestone ordering sorts by `observed_at`, never `received_at`, so a late batched ping inserts at its true position. | Must | OBJ-004/006 |
| FR-837 | Timestamps store/reason in UTC with local offset for display; no ambiguous naive-local timestamps persist. | Must | OBJ-006 |
| FR-838 | Derived durations compute from `observed_at` pairs; a `received_at`-only gap never silently substitutes. | Must | OBJ-004/005 |

### 10.6 Location privacy — requirement and defaults

Position is the **driver's** location, not the account's. This is the source of §4.4's field-level
view masks (`PERM-212/261/262/263`).

| ID | Requirement | MoSCoW | Traces |
|---|---|---|---|
| FR-839 | Position collection is scoped to the active trip window (dispatch through POD, plus `[NEEDS INPUT]` buffer) — never off-duty or between-loads. | Must | OBJ-007 |
| FR-840 | Exact live coordinates are not exposed to a shipper by default; default signal is milestone + corridor/ETA per §4.4's table. | Must | OBJ-007 |
| FR-841 | The consignee tokenised link carries only current corridor/ETA state, never raw coordinates or history. | Must | OBJ-007 |
| FR-842 | Raw pings and derived milestone/dwell records have independently configurable retention, both `[NEEDS INPUT]`; neither shorter than an open claim's evidentiary need. | Must | OBJ-005/007 |
| FR-843 | A driver may request access to, and deletion of, their own position history, subject to an active-claim/legal-hold exception. | Must | `[NEEDS INPUT: counsel]` |
| FR-844 | No location data leaves the transaction parties without a stated legal basis; never logged in plaintext general application logs. | Must | §14 |

### 10.7 Anti-spoofing

| ID | Requirement | MoSCoW | Traces |
|---|---|---|---|
| FR-846 | Consecutive pings implying speed above `[NEEDS INPUT]` flag `IMPLAUSIBLE_TRANSIT`, excluded from milestone/dwell computation. | Must | OBJ-006 |
| FR-847 | A device's mock-location/tamper indicator, where exposed, tags the record, excludes it from `CORROBORATED`. | Must | OBJ-006 |
| FR-848 | ELD vs app disagreement beyond `[NEEDS INPUT]` keeps both records, flagged `SOURCE_CONFLICT`; neither silently preferred. | Should | OBJ-006 |
| FR-849 | A `detention_candidate` or `loaded`/`unloaded` claim built on flagged evidence routes to fraud review before reaching billable/POD-evidentiary status. | Must | →§13 |
| FR-850 | Manual updates are unverifiable by construction; never presented at the same trust tier as device-sourced ones. | Must | OBJ-006 |
| FR-851 | Repeated spoofing signals feed risk signalling, never an automatic penalty at this layer. | Should | OBJ-006 |

### 10.8 Events, entities, integrations

Events (unnumbered in F8's own draft; consolidated into §12's catalog per §16.6):
`position.received` · `tracking.went_dark`/`unavailable` · `geofence.entered`/`exited` ·
`milestone.derived`/`claimed`/`corroboration_flagged` · `dwell.session_opened`/`closed` ·
`detention.candidate_computed` · `eta.recomputed`/`marked_stale` · `tracking.spoof_suspected`.

Entities (canonicalised at §3): `PositionPing`, `Milestone`, `GeofenceZone`, `DwellSession`,
`ETAEstimate`, `TrackingCapability` — **[ASSEMBLER NOTE]** these six were named in F8's draft but not
given `ENT-` IDs, and are not yet in §3's 34-entity catalog. Genuine gap, flagged for the next
assembly pass rather than invented here (assigning IDs without F8's own field-level detail would be
guessing).

Integration capabilities: **INT-800** ELD/telematics ingestion, carrier-controlled, refusable.
**INT-801** driver mobile app position. **INT-802** manual/ops-desk status capture. **INT-803**
truck-legal routing capability — ODbL layers stay Produced-Works-only, never cross this API
(`DEC-LOCK-002`). **INT-804** work-zone/weather/chain-control feed, geography-bounded, chain-control
licence `[NEEDS INPUT]`.

### 10.9 Edge case register (17)

| EC | Trigger | Behaviour | Decides | Unresolved? |
|---|---|---|---|---|
| EC-800 | No position source at all | `TRACKING_UNAVAILABLE` from dispatch | System | No |
| EC-801 | Source goes silent mid-trip | `NO_UPDATE_RECEIVED`, last-known stays age-labelled | System | No |
| EC-802 | Truck parked across the road, never enters polygon | `PROXIMATE_NOT_GEOFENCED`; dwell via manual claim only | Ops | Yes — threshold |
| EC-803 | Poor GPS in a steel yard, oscillating enter/exit | Debounced; persistent oscillation downgrades confidence | System | Partial |
| EC-804 | Imprecise polygon, or early arrival before appointment | False arrive, or dwell opens with billability left to A1/A6 policy | — | Yes |
| EC-805 | `loaded`/`unloaded` claimed with no corroborating position | `UNCORROBORATED` flag; claim stands, routed to review | Claims/ops | No |
| EC-806 | Manual-only trip, no device ever | All milestones `MANUAL` tier; detention still constructible | Ops | No |
| EC-807 | Batched offline upload arrives late | `BATCHED`, timeline reorders on `observed_at`, never shown live | System | No |
| EC-808 | Impossible-speed pings, mock-location, or ELD-vs-app disagreement | Flagged/excluded — none silently accepted | System, →§13 | Conflict cases yes |
| EC-809 | Detention candidate built on flagged evidence | Held from billing/claim use pending review | §13/A6 | No |
| EC-810 | Mid-trip relay/transload | New milestone set opens; prior leg closes untouched | System | No |
| EC-811 | Driver revokes/loses location sharing mid-trip | Falls back to manual/`TRACKING_UNAVAILABLE`, no fabrication | System | Yes — revocation UX |
| EC-812 | Consignee requests live location via token | Corridor/ETA only, no pin, link expires | System | No |
| EC-813 | Claim opens after retention window elapsed, or deletion requested mid-claim | Litigation hold extends retention / deletion yields to hold | Legal | Yes |
| EC-814 | Position crosses a state line/DST boundary | Stored UTC + local offset, no ambiguity | System | No |
| EC-815 | Device shared across multiple drivers | Attribution to a specific driver unreliable | F1 | Yes |
| EC-816 | Corridor outside covered geographies, or feed licence unconfirmed | States "coverage absent," never "clear"; suppressed until licence confirmed | System, legal | Yes |

### 10.10 Open design decisions

**DEC-800 — Shipper's default location granularity.** (A) exact pin always; (B) corridor/ETA-only
default, opt-in exact-pin during exceptions; (C) contract-tier configurable. F8 recommends (B) —
already reflected as §4.4's default. **DEC-801 — Retention posture.** (A) flat period; (B) tiered
(raw pings short-lived, milestone/dwell to at least the Carmack horizon); (C) carrier-configurable.
F8 recommends (B). **DEC-802 — Does manual-only (phone-reported) dwell qualify as billable
detention evidence?** (A) never bills; (B) bills at lower confidence with shipper review; (C) bills
identically. A6/Boss decision.

**Counts:** 50 FR · 0 numbered API (own resources referenced via §6's endpoints) · ~14 named events
(unnumbered, superseded) · 17 EC · 3 open `DEC-` · 17 `[NEEDS INPUT]`.

---

## 11. F9 — Dashboards & Screens per Persona

*Full source: `frd-F9-dashboards-screens.md`. §11.3's `SCR-923`/`SCR-924` annotated per §3.4's
BOL/POD merge finding.*

**Scope.** Screen inventory, IA, required states, field-usability constraints for five personas. No
visual design, no component library, no layout. Every `SCR-`/`FR-` traces to a BRD `BR-`/`OBJ-`.
**Core state set — mandatory on every screen below unless noted:** Loading · Empty · Partial data ·
Stale data · Permission-denied · Error · Offline · Contested (in-progress-by-someone-else).

**FR-900** Every `SCR-` in this document shall implement the core state set as a first-class render,
not a spinner-then-blank fallback. **IA principle carried through every persona:** exceptions
surface above normal status, never buried in a uniform list — Linear-dense triage, not Notion-airy
browsing.

### 11.1 Screen inventory

**Shipper coordinator (desk)**

| ID | Screen | Purpose | Key actions | Notable states | Traces |
|---|---|---|---|---|---|
| SCR-900 | Load Dashboard | Home; exceptions ranked above on-track loads | Publish, filter, jump to any load | Empty = "no loads — publish one" | BR-100/102 |
| SCR-901 | Post a Load | Structured multi-step declaration | Save draft, publish, ack BR-121 warning | Partial = autosaved draft; Error names the missing field | BR-110–127 |
| SCR-902 | Auction Watch | Live view of one open auction | Watch bids arrive, early-close (if `DEC-308` permits), pre-bid cancel | See §11.2 | BR-301–318 →§8 |
| SCR-903 | Award & Accept-Flow Monitor | Track `AWARD_PENDING → ACCEPTED` | View selection-record excerpt, see decline/lapse | Transient "re-verifying" state | BR-303/309 |
| SCR-904 | Shipment Tracker | Pickup→transit→drop for one load | View custody events, message ops | Stale = missed interval flagged, not hidden | BR-401/403 |
| SCR-905 | Exception Inbox (org-scoped) | Only this shipper's open `ExceptionCase`s (§3.3) | Acknowledge, respond, escalate | Empty is a genuinely good state, shown as such | BR-913 |
| SCR-906 | Invoice Approval | Review/approve/dispute lines | Approve clean lines, dispute one line without blocking the rest | Partial = mixed held/clear lines rendered distinctly | BR-601–604 |
| SCR-907 | Claim Intake | Raise a Carmack claim | Submit §370.3-minimum fields, track status | — | BR-807 |
| SCR-908 | Standing & Cancellation History | Own org's record | View only | Depends on an orphan upstream field (BR-106) — §16.7 | BR-105/145 |

**Carrier dispatcher (desk or phone)**

| ID | Screen | Purpose | Key actions | Notable states | Traces |
|---|---|---|---|---|---|
| SCR-910 | Load Board | Browse loads this org is eligible for | Filter, sort, open an auction | Permission-denied if org-wide gate fails | BR-200–217 |
| SCR-911 | Bid & Comparison Screen | **Core loop** — bid under a live timer | Submit, withdraw pre-close, view own bid history | See §11.2 — **§16.1 build-blocking dependency** | BR-301/307/308/314/717 |
| SCR-912 | Fleet Assignment | Bind driver+truck to an accepted award | Confirm tuple, see overlap conflict | Contested = two dispatchers, same truck | BR-212–215 |
| SCR-913 | Active Loads (multi-truck) | Every truck in flight, exceptions ranked first | Drill into one trip, message driver | Same exception-forward pattern as SCR-900 | BR-401/405 |
| SCR-914 | Breakdown / Exception Report | Report a `TRANSIT_EXCEPTION` sub-type | Pick category, attach evidence, request relief | — | BR-402/405 |
| SCR-915 | Driver & Equipment Roster | Manage availability | Self-declare unavailable, see expiry alerts | Error = expired document blocks new assignment | BR-209–220 |
| SCR-916 | Settlement Status | Per-load payable + factoring/NOA state | View, contact ops to dispute | — | BR-605/606 |

**Driver (phone, one-handed, gloves, sun/dark, poor connectivity, possibly Spanish)**

| ID | Screen | Purpose | Key actions | Notable states | Traces |
|---|---|---|---|---|---|
| SCR-920 | Today (home) | One current assignment, one primary action | Start nav, call dispatch, report a problem | Offline = last-known assignment cached, badged, never blank | BR-910 |
| SCR-921 | Navigation Handoff | Hand off to an external nav app | One tap; no in-app map surface owned here | — | derived |
| SCR-922 | Arrival / Departure Capture | Check in/out at pickup and drop | Confirm arrival, confirm departure | Offline = queued locally, syncs on reconnect | BR-403 |
| SCR-923 | Document Capture | Photo of BOL, seal, condition at pickup — **writes `ENT-316` `stage=origin` (§3.4)** | Take, retake, confirm | Error = unreadable image flagged before accept, not silently stored | BR-400/408 |
| SCR-924 | POD Capture | Clear-vs-exception signature — see §11.3 — **writes `ENT-316` `stage=delivery` (§3.4)** | — | — | BR-500–514 |
| SCR-925 | Report a Problem | Entry point to any transit exception | Category, voice-note or photo, submit | Offline = high-priority sync queue | BR-405 |
| SCR-926 | Language & Support | Toggle English/Spanish; call/text dispatch or ops | — | — | BR-914 |

**Platform ops / exception desk**

| ID | Screen | Purpose | Key actions | Notable states | Traces |
|---|---|---|---|---|---|
| SCR-930 | Exception Work Queue | Ranked — what's broken, action attached; **not** a dashboard | Claim, act, reassign, escalate | Contested = claimed by another; Stale = unclaimed past `[NEEDS INPUT]` | BR-913 |
| SCR-931 | Exception Detail & Resolution | Full context: load, custody events, prior actions | Resolve, request info, escalate to fraud (SCR-941) | — | BR-913 |
| SCR-932 | Claims Desk | Every open Carmack claim against its 30/120/60-day clock | Acknowledge, request evidence, decide, issue disallowance | Stale = obligation date approaching/missed, escalating visually | BR-807/808 |
| SCR-933 | Silence / No-Response Monitor | Loads flagged for missed status interval or no-show risk | Contact carrier, escalate | Empty is the goal state | BR-401/409 |

**Platform admin / fraud reviewer**

| ID | Screen | Purpose | Key actions | Notable states | Traces |
|---|---|---|---|---|---|
| SCR-940 | Carrier Vetting Queue | New/re-verifying carriers awaiting explicit ops approval | Approve, reject, request evidence | Partial = some automated checks cleared, some pending | BR-908, BR-201–208 |
| SCR-941 | Fraud Case Review | Classified case (double-broker / identity theft / disclosed substitution) | Classify, escalate, notify counterparties | — | BR-806 |
| SCR-942 | Selection Record / Audit Viewer | Reproduce any award's full immutable record | Search, export, view exclusions + reasons | — | BR-303/706 |
| SCR-943 | Enforcement Action | Apply graduated penalty | Warn / restrict / suspend / remove, log ground + evidence + appeal | Contested = live in-flight load exists under a suspending carrier | BR-817/818 |

### 11.2 Auction screens — the product's heart

**Shipper's Auction Watch (SCR-902).** States beyond core: **live** (bids arriving, running low bid +
eligible-bidder count, countdown as `aria-live="polite"`); **extended** (`AUCTION_EXTENDED` —
visually distinct, never a silent reset); **thin-market** (pool/bid count below labelled threshold);
**closing** (brief lock while `AWARD_PENDING` re-verifies, shown as "verifying," never
already-awarded); **failed** (each failure reason distinct). Shipper sees price, timestamp, carrier
authority type per bid, and a standing indicator where BR-106's feed exists — this is the shipper's
own auction, not a bidder view, so BR-717 does not apply here.

**Carrier's Bid & Comparison Screen (SCR-911).** The dispatcher's core loop, and the screen most
exposed to §16.1's build-blocking fork: **what a bidder sees of rivals is undecided** (`DEC-302`/
`303`), and BR-717 forbids exposing another bid's value or identity absent a documented decision.
Built with rival-visibility as a swappable parameter, three states ready for whichever §8 locks:
**(a) none** — own bid + timer + eligible-count only; **(b) rank-only** — "#2 of 5 eligible," no
amounts; **(c) leading-price band** — rounded, never exact. **Default: (a) none** — the conservative
BR-717 reading.

**CHALLENGE (F9's own, still live):** shipping a bid screen against an undecided disclosure boundary
risks a BR-717 violation in production, not a UI bug, if the default proves too permissive later. §8/
Boss should lock `DEC-302`/`303` before SCR-911 builds past "none." **This is the same decision
surfaced independently by §4.5, §8.7, and here — consolidated once at §16.1.**

### 11.3 POD capture flow (SCR-924) — carries the entire commercial settlement

Sequence, each its own screen state, never skippable: **(1) Arrival** confirmed. **(2) Count/
condition entry** against declared. **(3) The forced choice** — full-screen, two-option: **"Delivered
CLEAR"** vs **"Delivered WITH EXCEPTION."** No pre-selection, no default path; continue is disabled
until one is explicitly chosen. Exception forces a structured sub-screen before signature is
reachable. **(4) Photo evidence** — optional on clear, **mandatory** on exception. **(5) Signature**
— from whoever is present, no account required; printed name + stated role captured, never inferred.
**(6) Confirmation** — read-only summary before submit, since the record is fixed once captured; any
later addition is a separately timestamped addendum, never an overwrite. **[ASSEMBLER NOTE, §3.4]**
This entire sequence writes `ENT-316`'s `delivery_capture` stage — the same entity `SCR-923`'s
pickup flow writes at `origin_capture`.

**Additional screen:** concealed-damage/addendum entry, reachable later, always linked to the
original POD, never replacing it. `DELIVERY_ATTEMPTED_NO_RECEIVER` is its own outcome — arrival
timestamp recorded, no POD, forced-choice screen never reached.

**FR-903** The clear/exception screen shall never render a default selection, a "skip" affordance,
or one combined "confirm delivery" button implying clear.

**Offline:** the sequence must complete and persist locally without connectivity, syncing with a
visible "pending sync" state — a captured signature is never lost. `[ASSUMPTION: offline-first
capture required given stated field conditions | conf: high]`.

### 11.4 Exception desk (SCR-930) and notifications-in-app

**Queue ranking dimensions:** severity class (custody/safety > commercial > informational), age
since trigger, proximity to a regulatory clock (Carmack's 30/120/60-day marks), and
`FRAUD_SUSPECTED`/`CARRIER_SUSPENDED_IN_FLIGHT`-classed cases (§3.3's `ExceptionCase` `case_type`s
`FRAUD_REVIEW`/`CARRIER_ENFORCEMENT_COLLISION`) always surfacing above routine items. Every row
carries the action already attached — a linked resolution screen, not a re-triage step.

**Notifications land per persona** (§12 owns delivery/transport; this is where they render):

| Persona | Landing surface |
|---|---|
| Shipper coordinator | Banner atop SCR-900 for own-org exceptions + SCR-905 inbox; routed to the posting user specifically |
| Carrier dispatcher | Badge on SCR-910/913; breakdown/expiry alerts route to SCR-914/915 |
| Driver | Full-screen interrupt on SCR-920, never a dismissible toast for anything blocking; optional audio cue, eyes-on-road context |
| Ops desk | Queue re-sort (SCR-930) + distinct cue for a newly-critical item |
| Admin/fraud | Case appears in SCR-941; cadence `[NEEDS INPUT: real-time or digest]` |
| Consignee | **No in-app surface** — out-of-band delivery required, explicit "delivery status unknown," never a false confirmed-read |

### 11.5 Accessibility & field usability (WCAG 2.2 AA minimum, non-negotiable)

Target size ≥24×24 CSS px; AA 4.5:1 baseline, driver screens target AAA 7:1; single-pointer
alternative wherever drag is used; English/Spanish minimum on every driver screen and support path,
persisting across sessions; icon **+** short label always paired; every driver screen degrades
gracefully offline, no infinite spinner, no data loss on a dropped connection mid-capture;
`prefers-reduced-motion` respected; auction updates `aria-live="polite"`, close/award
`aria-live="assertive"`; desk screens keyboard-complete, logical focus order.

### 11.6 Edge case register (16)

| ID | Trigger | Behaviour | Who decides | Unresolved? |
|---|---|---|---|---|
| EC-900 | Two dispatchers act on same truck at once (SCR-912/913) | Optimistic lock; second actor sees "updated by X, refresh" | Convention | No |
| EC-901 | Driver phone loses connectivity mid-POD (SCR-924) | Local draft persists, syncs on reconnect, "pending sync" badge | Resolved (FR-901) | No |
| EC-902 | Shipper watches SCR-902 during `AWARD_PENDING` re-verify | Transient "verifying eligibility," not premature award | Resolved | No |
| EC-903 | Rival-visibility level on SCR-911 (`DEC-303`) | Defaults to "none" until `DEC-303` locks | §8/Boss | **Yes — §16.1** |
| EC-904 | Ops queue item claimed by a second user (SCR-930) | "Already claimed by X"; duplicate resolution blocked | Resolved | No |
| EC-905 | Consignee reports damage minutes after signing "clear" | Only path is the addendum channel; original never overwritten | Resolved | No |
| EC-906 | Spanish-speaking driver hits an English error code | Maps `ERR-` codes (§7) to localized strings, never raw codes | §7/§12 | Partially |
| EC-907 | SCR-908's standing indicator has no upstream feed (BR-106 orphan) | Renders "not yet available," never fabricates a value | Rendering rule set; orphan remains — §16.7 | Yes (upstream) |
| EC-908 | Auction has exactly one bidder | Both screens label it "thin market," not competitive | Labelling resolved; `DEC-310` open | Yes (mechanism) |
| EC-909 | Award cascades to next bidder after a decline (`DEC-309`) | Does new winner's screen disclose the cascade? | Boss — privacy vs transparency | **Yes** |
| EC-910 | Driver has no camera permission (SCR-923/924) | Degrades to text-only notation; signature never blocked by missing photo unless exception path requires one | Resolved | No |
| EC-911 | Exception lands for a shipper org itself suspended mid-flight | Queue item surfaces both facts together | Resolved | No |
| EC-912 | SCR-920 has no HOS-feasibility signal from §9 | Shows "not evaluated," never a false-safe green light | §9 dependency | Depends on §9 |
| EC-913 | Two trucks, one org, overlapping window on SCR-912 | Truck B shows "unavailable for this window" | Resolved | No |
| EC-914 | Fraud reviewer (SCR-941) has case open when a suspension hits an in-flight load | Shows "recovery protocol active," never "frozen" | Resolved | No |

### 11.7 Open questions this domain cannot resolve alone

`[NEEDS INPUT]`: exception-queue stale-threshold value (SCR-930); real-time vs. digest cadence for
fraud review (SCR-941); whether a cascade winner is told (EC-909, Boss's call); `DEC-302`/`303`
rival-visibility resolution before SCR-911 ships past its "none" default — **§16.1.**

**Counts:** 31 SCR · 3 FR (explicit) · 16 EC · 3 `[NEEDS INPUT]` · 6 open `DEC-` (cross-referenced,
not F9's own).

---

## 12. F10 — Notifications, Events & Messaging

*Full source: `frd-F10-notifications-events.md`. **This is the canonical event/notification
catalog for the whole system** — see §16.6 for why F4's, F6's, F7's and F13's own event lists are
superseded by it rather than the reverse. `ExceptionCase` propagation (§3.3) applied per §12.1's
note and §12.1a's additions.*

**ID block 1000-1099.** Owns: event catalog, notification matrix, delivery semantics,
preferences/suppression, outbound webhook catalog+semantics, auditability. Not here: transport/HMAC
mechanics (§6), error taxonomy (§7), who may trigger an action (§4), preference/notification screens
(§11). Events named `<entity>.<past_tense_event>` per §1, one per BRD-lifecycle transition unless
noted.

**[ASSEMBLER FIX — ID prefix normalised].** F10's own draft listed events by bare number (`1000`,
`1001`, …) in its table, unlike every other section's `EVT-` prefixed convention. Below, every row
is written `EVT-1000` etc. for consistency; no semantic change.

### 12.1 Event catalog & notification matrix

**Tier**: T0 critical (overrides quiet hours, may use voice) · T1 high (real-time, quiet-hours
aware) · T2 normal (real-time best-effort) · T3 digest-default (§12.6). **Channels**: `IA` in-app ·
`PU` push · `SMS` · `EM` email · `VO` voice call · `OOB` out-of-band, consignee's supplied contact
only · `DG` digest-routed · `—` not notified. **Personas**: `Shpr` shipper (poster+admins) · `Disp`
carrier dispatcher · `Drv` driver · `Ops` platform-ops · `Cnsg` consignee.

| EVT | Event | Tier | Shpr | Disp | Drv | Ops | Cnsg | Src |
|---|---|---|---|---|---|---|---|---|
| EVT-1000 | load.published | T3 | IA | — | — | — | — | BR-110/130 |
| EVT-1001 | auction.opened | T3 | IA | DG¹ | — | — | — | §3.3 |
| EVT-1002 | bid.submitted | T3 | DG | IA | — | — | — | BR-301/307 |
| EVT-1003 | bid.rejected_ineligible | T2 | — | IA,EM | — | — | — | BR-301/200 |
| EVT-1004 | auction.closed | T3 | IA | DG | — | — | — | §3.3 |
| EVT-1005 | award.determined | T1 | — | IA,PU | — | DG | — | BR-303 |
| EVT-1006 | award.confirmed | **T0** | IA,EM | IA,PU,SMS,EM;VO² | — | DG | — | BR-302/303 |
| EVT-1007 | award.declined | T1 | IA,EM | IA | — | IA | — | BR-905 |
| EVT-1008 | award.lapsed | T1 | IA,EM | IA,PU | — | IA | — | BR-309 |
| EVT-1009 | award.voided_ineligible | **T0** | IA,EM | IA,PU,SMS | — | IA,SMS | — | BR-302 |
| EVT-1010 | award.accepted | T1 | IA,EM | IA | — | — | — | §3.3 |
| EVT-1011 | rate_confirmation.issued | T1 | IA | IA,PU,EM³ | — | — | — | BR-600 |
| EVT-1012 | pickup.scheduled | T2 | IA,EM | IA,PU,SMS | PU,SMS | — | — | BR-114 |
| EVT-1013 | pickup.identity_mismatch | **T0** | — | IA,SMS | PU,SMS | IA,SMS,VO | — | BR-221/406 |
| EVT-1014 | pickup.shipper_not_ready | T1 | IA,SMS | IA,PU,SMS | PU,SMS | IA | — | BR-143 |
| EVT-1015 | pickup.carrier_no_show | **T0** | IA,SMS,VO | IA,SMS | — | IA,SMS | — | BR-142 |
| EVT-1016 | pickup.refused | T1 | IA,SMS | IA,PU | PU | IA | — | §3.3 |
| EVT-1017 | load.picked_up | T2 | IA,EM | IA,PU | PU | DG | OOB⁴ | BR-400 |
| EVT-1018 | shipment.in_transit | T3 | DG | IA | — | DG | — | §3.3 |
| EVT-1019 | shipment.status_updated | T3 | DG | DG | — | DG | — | BR-401 |
| EVT-1020 | shipment.status_overdue | T1 | IA | IA,PU,SMS | — | IA,SMS | — | BR-401 |
| EVT-1021 | transit.exception_reported | T1/T0⁵ | IA,EM | IA,PU,SMS | PU,SMS | IA,SMS | OOB⁵ | BR-405 |
| EVT-1022 | custody.transferred | T1 | IA,EM | IA,PU | PU | IA | OOB | BR-402 |
| EVT-1023 | truck.arrived_at_drop | T2 | DG | IA | — | — | OOB | §3.3 |
| EVT-1024 | delivery.attempted_no_receiver | **T0** | IA,SMS,EM | IA,PU,SMS | PU | IA | OOB,SMS/VO | BR-509 |
| EVT-1025 | delivery.completed | T1 | IA,EM | IA,PU | PU | DG | — | §3.3 |
| EVT-1026 | delivery.refused | **T0** | IA,SMS,EM | IA,PU,SMS | PU | IA,SMS | — | §3.3 |
| EVT-1027 | delivery.partial_accepted | T1 | IA,EM | IA,PU | — | IA | — | §3.3 |
| EVT-1028 | pod.captured | T1 | IA,EM | IA,EM | — | DG | OOB⁶ | BR-500/501, writes `ENT-316` (§3.4) |
| EVT-1029 | shipment.returned_to_origin | T1 | IA,EM | IA,PU | PU | IA | — | §3.3 |
| EVT-1030 | cargo.exception_reported | **T0** | IA,SMS,EM | IA,SMS | PU | IA,SMS,VO | OOB | **`ExceptionCase.opened`, case_type=CARGO_INTEGRITY (§3.3)** |
| EVT-1031 | cargo.recovery_opened | T1 | IA,EM | IA | — | IA | OOB | **`ExceptionCase.status_changed`, case_type=CARGO_INTEGRITY → RECOVERY_IN_PROGRESS (§3.3)** |
| EVT-1032 | fraud.suspected | **T0**⁷ | — | — | — | IA,SMS,VO | — | **`ExceptionCase.opened`, case_type=FRAUD_REVIEW (§3.3)** |
| EVT-1033 | carrier.suspended_in_flight | **T0** | IA | IA,PU,SMS | — | IA,SMS | — | **`ExceptionCase.opened`, case_type=CARRIER_ENFORCEMENT_COLLISION (§3.3)** |
| EVT-1034 | claim.opened | T1 | IA,EM | IA,EM | — | IA | via Shpr relay | **`ExceptionCase.opened`, case_type=CARGO_CLAIM (§3.3), detail=`ENT-319`** |
| EVT-1035 | claim.obligation_due | T1/T0⁸ | DG | DG | — | IA,EM | — | BR-807 |
| EVT-1036 | dispute.opened | T1 | IA,EM | IA,EM | — | IA | via Shpr relay | **`ExceptionCase.opened`, case_type=DISPUTE_FREIGHT\|MONEY (§3.3)** |
| EVT-1037 | dispute.closed_unresolved | T1 | IA,EM | IA,EM | — | IA | via Shpr relay | **`ExceptionCase.status_changed` → CLOSED_UNRESOLVED (§3.3)** |
| EVT-1038 | load.cancelled | T1/T0⁹ | IA | IA,PU,SMS,EM | PU,SMS | IA | OOB if post-pickup | BR-138/139/144 |
| EVT-1039 | load.withdrawn | T1 | IA | IA,PU,EM | — | — | — | BR-136/138 |
| EVT-1040 | invoice.issued | T2 | IA,EM | IA,EM | — | — | — | BR-601 |
| EVT-1041 | invoice.line_held | T1 | IA,EM | IA,EM | — | DG | — | BR-602/603 |
| EVT-1042 | invoice.settled | T2 | IA,EM | IA,EM | — | DG | — | BR-603 |
| EVT-1043 | shipment.completed | T3 | DG | DG | — | DG | — | §3.3 |
| EVT-1044 | carrier.eligibility_lapsed | T1 | — | IA,PU,SMS,EM | — | DG | — | BR-217 |
| EVT-1045 | carrier.document_expiring | T2 | — | IA,EM,DG | — | DG | — | BR-220 |
| EVT-1046 | payee_of_record.changed | **T0** | — | IA,EM (old+new) | — | IA,SMS | — | BR-909/812 |
| EVT-1047 | consignee.notice_delivery_unknown | T2, internal | — | — | — | DG | (unreached) | BR-912 |
| EVT-1048 | webhook.subscription_unhealthy | T1, internal | IA if subscriber | IA if subscriber | — | IA,EM | — | §12.7 |

¹ digest unless real-time-subscribed. ² voice only if undelivered within ack window (§12.5). ³ ack
required before `PICKUP_SCHEDULED`. ⁴ first consignee touch, establishes ETA. ⁵ T0 only for safety
sub-types (accident/breakdown/HOS/theft/OOS); weather is T1; consignee told only if ETA changes.
⁶ bundles BR-714 notice if not already sent at 1017/1021. ⁷ restricted fanout, never reaches
suspect/counterparty (BR-225); consequence gets its own event. ⁸ escalates to `Ops` only when
overdue. ⁹ T0 only post-dispatch/pickup (BR-142/144); pre-award is routine.

### 12.1a `ExceptionCase` propagation — the fix this section required (per F3 FR-351)

**Finding, stated plainly.** F10 was drafted before F3 accepted F11's `ExceptionCase` challenge
(§3.3). F10 never actually emitted a generic `load.state_changed` event for the seven conditions F3
pulled out of `Load.lifecycle_state` (`DISPUTED`/`CLOSED_UNRESOLVED`, `CLAIM_OPEN`,
`FRAUD_SUSPECTED`/`RECOVERY`, `DAMAGED`/`LOST`/`PILFERED`, `CARRIER_SUSPENDED_IN_FLIGHT`) — it
independently named seven specific events instead (`EVT-1030`–`1034`, `1036`, `1037`), which turns
out to be **the right shape for a case-based model**, just not yet labelled as one. The fix above
(inline annotations on those seven rows) is a re-labelling, not a rewrite: each already-correct
event is now explicitly tied to its `ExceptionCase` `case_type` and lifecycle transition
(`opened`/`status_changed`/`closed`) per F3's FR-351 instruction.

**What was still a genuine gap, closed here — two new events, next available IDs in F10's block:**

| ID | Event | Tier | Shpr | Disp | Drv | Ops | Cnsg | Src |
|---|---|---|---|---|---|---|---|---|
| **EVT-1049** | **case.resolved** | T1 | IA,EM | IA,EM | — | IA | via Shpr relay if consignee-relevant | **[ASSEMBLER ADDITION]** F3's case-transition set (§3.3) has a `RESOLVED` terminal state with no corresponding event for `CARGO_INTEGRITY`, `FRAUD_REVIEW`, or `CARRIER_ENFORCEMENT_COLLISION` cases — `EVT-1031`/`1032`/`1033` cover *opening*, `EVT-1037` covers only the *unfavourable* dispute close. A cargo-integrity case that resolves as "found, not lost," a fraud case that clears the carrier, or an enforcement collision that ends in reinstatement all had no event to fire. This closes it generically across the three case_types F10's per-type table doesn't already terminate. |
| **EVT-1050** | **carrier.reinstated** | T1 | — | IA,EM | — | IA | — | **[ASSEMBLER ADDITION]** F10 has `EVT-1033 carrier.suspended_in_flight` (the specific in-flight sub-case) but no general reinstatement event at all — F4's superseded draft had one (`EVT-427`, §6.5) and F13 named one informally (§15.10) but neither owns F10's block. Canonicalised here; fires on `CarrierVettingRecord`/`Organization.status` returning from `SUSPENDED`, whether or not the suspension coincided with an in-flight load. |

**What remains a named, not-invented gap (§16.6 has the full list):** no event exists for a plain
`carrier.suspended` (as opposed to the specifically in-flight `EVT-1033`) — a carrier with zero
active loads at suspension time currently has nothing corresponding in F10's own catalog, only in
F4's superseded one (`EVT-426`). This document does not invent that event's full notification-matrix
row (tier, per-persona channels) because F10 — the domain owner — never specified it, and guessing
those columns would be inventing a decision, not reconciling one. Flagged in `frd-assembly-report.md`
as an open item for the next drafting pass, not silently added.

### 12.2 Channel semantics

| Channel | Fits | Constraint |
|---|---|---|
| In-app | Desk-based Shpr/Disp/Ops | Audit floor — every event gets an IA record regardless of primary channel |
| Push | Mobile Disp/Drv | Needs app installed; degrades to SMS if not |
| SMS | Drv in cab, Cnsg, T0/T1 fallback | **Regulated act on a US number** — consent, sender ID, opt-out. `[NEEDS INPUT: consent-capture point]` |
| Email | Everyone with an address | Carries BR-714 notice text on first consignee contact |
| Voice | T0 only (§12.3) | Never for T2/T3 |
| Webhook | Integrated shipper/carrier systems | Signing → §6; catalog/semantics → §12.5-7; grant → §4; screen → §11 |
| OOB | Consignee only | Only channel available — no login to push into |

### 12.3 Urgency tiers

| Tier | Meaning | Quiet hours | Retry |
|---|---|---|---|
| T0 | Load uncollected / custody-safety / fraud / payment-diversion risk if missed | **Overrides**, incl. voice | Escalate channel-by-channel until acked; ops paged on exhaustion |
| T1 | Changes what recipient must do next | Respected, bounded delay `[NEEDS INPUT]` | Standard (§12.5) |
| T2 | Actionable, not urgent | Respected fully | Best-effort, no escalation |
| T3 | Routine/high-frequency/confirmatory | Batched (§12.6) | Digest job owns delivery |

### 12.4 Preferences, quiet hours, suppression

Each account-holding persona sets channel preference + quiet-hours window per channel `[NEEDS INPUT:
default window, org- vs. user-level]`. **T0 overrides every suppression setting without exception.**
A recipient cannot opt out of T0 on every channel at once; onboarding/award-acceptance blocks until
≥1 T0-reachable channel exists (enforcement → §4). The consignee has no preference surface — its
only lever is the contact the shipper supplied; SMS consent/opt-out mechanics remain `[NEEDS INPUT]`.

### 12.5 Delivery semantics

At-least-once on every channel except webhooks (dedup, §12.7); in-app is the idempotent record.
**Ordering:** each event carries the shipment's monotonic sequence number; a consumer seeing a
lower-seq event after a higher one discards and refetches. **Dedup:** idempotency key = stable
`event_id`, reused on redelivery (header shape → §6). **Retry/backoff:** exponential, bounded,
tier-dependent — `[NEEDS INPUT: interval, multiplier, cap, max attempts]`. **Dead-letter:** T0/T1
max-attempt failures raise an `Ops` alert, never vanish; T2/T3 log without paging.
**Silent-failure — the money case:** a missed `award.confirmed` is an uncollected load. Every T0/T1
attempt tracks `PENDING→SENT→DELIVERED|FAILED|UNKNOWN` (email open-tracking is `UNKNOWN`, never
inferred read). No delivered-or-better status within `[NEEDS INPUT: ack window]` auto-escalates
`award.confirmed` to voice and pages `Ops`. API errors use §1's canonical envelope.

### 12.6 Digests vs. real-time

T3 events, and T2 for digest-opted users, batch per persona instead of firing individually.
Frequency `[NEEDS INPUT: interval — likely shipper-daily, dispatcher-hourly during active auctions]`.
T0/T1 always bypass the digest.

### 12.7 Outbound webhooks

Any `EVT-` in §12.1 is subscribable, scoped to the subscribing org's own visible shipments — never
cross-org. `EVT-1032 fraud.suspected` is never webhook-subscribable, matching its restricted human
fanout.

| Concern | Requirement | Owner |
|---|---|---|
| Signing | Verifiable origin, rotatable secret | Mechanics → §6 |
| Replay | Timestamp+nonce; reject stale beyond `[NEEDS INPUT]` window | Mechanics → §6 |
| Retry | Same posture as §12.5, subscriber-scoped | This section |
| Subscriber failure | N fails (`[NEEDS INPUT]`) → unhealthy (`EVT-1048`), pauses, notifies admin, resumable, no silent drop | This section |
| Versioning | Schema version on payload; additive-only per version; breaking = new version, old kept serving | Convention → §6 |
| Subscribe grant / UI | — | §4 / §11 |

### 12.8 Auditability

Every notification attempt, any channel/persona incl. OOB, logs immutably: `event_id`, recipient,
channel, content version, sent time, delivery status, read/ack time where supported. Retained at
least as long as the shipment record — "was this party notified" is evidence in a Carmack claim or
negligent-selection dispute. The platform never fabricates a confirmed-read state for the consignee
— absent a carrier-level receipt the honest record is `EVT-1047 consignee.notice_delivery_unknown`.
Log is queryable independent of any third-party channel provider's own retention.

### 12.9 Functional requirements

| FR | Requirement | Traces | Acceptance |
|---|---|---|---|
| FR-1000 | Every lifecycle transition emits exactly one `EVT-` per §12.1. | BR-all | Mapping complete. |
| FR-1001 | `award.confirmed` escalates per §12.5 if not delivered within the ack window. | BR-303 | No award unconfirmed past window. |
| FR-1002 | Consignee notices never route in-app; unproven delivery recorded, not assumed. | BR-912 | No `Cnsg=OOB` row has an IA/PU fallback. |
| FR-1003 | T0 delivers regardless of quiet-hours/suppression. | §12.3/§12.4 | T0 in quiet hours still delivers ≥1 channel. |
| FR-1004 | Multi-poster orgs route load events to the posting user, not only admin. | BR-911 | Poster A gets Poster A's events. |
| FR-1005 | `fraud.suspected` fans out only to fraud/ops. | BR-225 | No counterparty channel carries `EVT-1032`. |
| FR-1006 | Every attempt logged (recipient/channel/status/time), retained per §14. | BR-820 | Audit query returns full attempt history. |
| FR-1007 | Webhook subscriptions scope strictly to subscriber's own org. | §2 | Cross-org delivery structurally impossible. |
| FR-1008 | Out-of-sequence deliveries discarded, not applied. | task brief | Out-of-order test never regresses state. |
| FR-1009 | Driver content available in English/Spanish minimum. | BR-914 | Spanish driver gets Spanish content. |
| FR-1010 | `payee_of_record.changed` notifies old+new, pages ops pre-effect. | BR-909/812 | No payee change routes without dual notice + ops event. |

### 12.10 Edge case register (9, +0 assembler-added — the two new events above needed no new EC rows)

| EC | Trigger | Behaviour | Who decides | Unresolved? |
|---|---|---|---|---|
| EC-1000 | Consignee OOB contact bounces | Falls to `notice_delivery_unknown`; shipper prompted to correct | Ops/Shpr | Yes — re-contact SLA `[NEEDS INPUT]` |
| EC-1001 | Driver has no signal on a T0 event | SMS queues per carrier retry; can't force delivery | Carrier | Yes — blackout tolerance `[NEEDS INPUT]` |
| EC-1002 | Award/cancellation delivery race | Sequence-discard + refetch (§12.5) | — | No |
| EC-1003 | Webhook subscriber down on a T0 event | Retry → unhealthy; human channels proceed independently | — | No |
| EC-1004 | SMS consent revoked/never captured (consignee) | SMS suppressed, falls to EM/VO | Counsel | **Yes — [NEEDS INPUT]** |
| EC-1005 | HOS-exhaustion event, no stored ELD (§9 §9.6) | Fires from self-report/derived signal only, never stored ELD | §9 / this section | Yes — depends on §9's `DEC-` |
| EC-1006 | Consignee has no channel for claim status | Relayed via shipper (BR-906); no direct channel | §11/§13 | Yes — mirrors BR-906 |
| EC-1007 | Award to broker whose sub-carrier executes | Broker gets commercial events; driver/dispatcher get fulfilment events | §9's tuple model | No |
| EC-1008 | Voice escalation reaches an off-duty driver mid-HOS-reset | Attempted anyway — only defined T0 set uses voice | §9/client ops | Yes — `[NEEDS INPUT]` policy |

**CHALLENGE:** none filed by F10 itself — the seven-condition move (§12.1a) was absorbable without a
new event catalog, which is itself evidence F10's original design was closer to the case model than
its own text acknowledged.

**What this domain cannot do:** invent quiet-hours windows, retry/backoff counts, digest intervals,
or ack-window durations; resolve SMS/voice consent and opt-out mechanics for a US phone number
(counsel); decide whether voice escalation to an off-duty driver is acceptable policy (client
operations, EC-1008).

**Counts:** 51 EVT (49 original + 2 assembler-added) · 11 FR · 9 EC · 13 `[NEEDS INPUT]`.

---

## 13. F11 — Platform Admin, Ops Console & Support Tooling

*Full source: `frd-F11-admin-ops-console.md`. F11 is the agent whose `CHALLENGE` produced §3.3's
`ExceptionCase` model in the first place — its own queue design already reads `ExceptionCase`
natively, so no propagation fix was needed here the way it was for §12. Permission-shape rows folded
into §4.1/§4.2 (`ROLE-229`, `ROLE-230`, `PERM-260`, `PERM-264`).*

ID block **1100-1199**. Screens → §11 (referenced, not duplicated). Permission matrix → §4. Error
taxonomy → §7. Entity/audit model → §3. Event catalog → §12.

**Thesis, from F11's own finding:** every exception state in the lifecycle lands on a human, and
this is that human's tool. The BRD is explicit that no staffing model, coverage size, or SLA exists
yet (`DEP-900`, `RSK-027`) — this builds the tooling that works under *any* coverage model the client
eventually picks, and states plainly where the tooling alone cannot substitute for headcount.

### 13.1 Exception work queue — the core product

Every trigger named across the BRD opens an `ExceptionCase` (`ENT-324`, §3.3), a first-class record
independent of the parent entity's own lifecycle state — **this is F11's own challenge, already the
canonical model at §3.3, not a fix applied here.**

| ID | Requirement | Traces | Pri |
|---|---|---|---|
| FR-1100 | Every trigger opens exactly one `ExceptionCase`, never held only in the domain entity's state field. AC: load enters a transit exception → a case exists referencing it. | BR-913 | Must |
| FR-1101 | One entity may hold multiple, independently-owned open cases concurrently (e.g. a fraud case and a detention dispute on the same load) — opening one never closes or hides another. | BR-913 | Must |
| FR-1102 | Each case carries a domain tag (`case_type`, §3.3), rendering as segmented swimlanes — never one flat list. | Boss's brief | Must |
| FR-1103 | Each case exposes three independent prioritisation signals, never pre-collapsed into one number: **money-at-risk**, **freight-in-motion** (load at/after `PICKED_UP`, before `POD_CAPTURED`), **time-criticality**. `[NEEDS INPUT: composite score in addition — no formula invented]` | BR-913, KPI-07/08/09 | Must |
| FR-1104 | A cross-domain "urgent" view unions freight-in-motion cases, any fraud-classified case, and cases within `[NEEDS INPUT: deadline proximity window]` of a bound deadline. | OBJ-006 | Must |
| FR-1105 | Any user with the queue-work permission (`PERM-236`, §4.2) may claim an unclaimed case; claimed cases stay platform-wide visible (read) but are removed from others' "unclaimed" filter. | BR-913 | Must |
| FR-1106 | A claimed case with no recorded action for `[NEEDS INPUT: inactivity threshold]` auto-returns to unclaimed. | derived | Should |
| FR-1107 | Manual escalation to a named senior tier (`PLATFORM_SENIOR_REVIEWER`, `ROLE-229`, §4.1) requires a reason. Auto-escalation, no human decision needed: a fraud case classified double-brokering/identity-theft where the load is at/after `PICKED_UP`; a claim case within `[NEEDS INPUT]` of its BR-808 statutory deadline. | BR-806/808 | Must |
| FR-1108 | Cases carry a free-text handoff note and a last-touched actor/timestamp. No case is bound to a shift roster — there is no staffing model in this spec — so every open case, claimed or not, stays visible platform-wide to anyone holding the permission. | DEP-900, RSK-027 | Must |
| FR-1109 | Time-in-queue and time-to-resolution are tracked for every case regardless of whether a target exists. A per-domain-tag target-response field exists, empty by default. **`[NEEDS INPUT: SLA targets per domain]`.** | KPI-11 | Must |
| FR-1110 | Resolution records type, actor, reason, and links to any downstream action taken (override, waiver, suspension, claim decision) — the case is a self-contained audit trail. | BR-306/817/907 | Must |

### 13.2 Carrier vetting and re-verification tooling

The reviewer surface behind §15's eligibility gate, and the human step BR-908 requires even after
every automated check clears.

| ID | Requirement | Traces | Pri |
|---|---|---|---|
| FR-1111 | Review surface shows, per candidate, evidence and last-verified timestamp for all six eligibility-tuple elements (§15): FMCSA/SAFER status+age, COI fields **and** verification source (insurer/agent-confirmed vs. carrier-uploaded only — the two are never shown as equivalent), safety rating/CSA-SMS with refresh time, legal-name/address match, identity document, declared role + role-specific docs. | BR-201-211 | Must |
| FR-1112 | Reviewer decision is APPROVE / REJECT / HOLD-FOR-INFO / CONDITIONAL. Reason required on every decision. Account stays non-bidding until an explicit APPROVE. | BR-908 | Must |
| FR-1113 | Reviewer may REJECT even where every automated check passed. Reviewer overriding an automated **FAIL** to APPROVE requires a documented justification **and** a second, named approver (`PLATFORM_SENIOR_REVIEWER`, `PERM-260`, §4.2) before the account becomes bid-eligible. This is `DEC-201` made operational — F11 does not pick among `DEC-201`'s three rigour options, it enforces whichever is chosen, but a fail→approve override is never single-actor. | `DEC-201`, BR-908 | Must |
| FR-1114 | Recurring re-verification cases (cadence `[NEEDS INPUT]`) render on the same surface, tagged distinct from initial onboarding. | BR-217-219 | Must |
| FR-1115 | A lapse between award and pickup (BR-218) or mid-transit (BR-219) opens a case tagged `vetting-lapse-in-flight`, pinned to freight-in-motion (FR-1103) so it never sorts below a paperwork-only lapse. | BR-218/219 | Must |
| FR-1116 | Reviewer sees the specific equipment/driver record bid on the load, never a carrier-level rollup — "no carrier is eligible in the abstract" (§2) holds in the tool, not just the schema. | BR-200/209/210 | Must |

### 13.3 Fraud review

| ID | Requirement | Traces | Pri |
|---|---|---|---|
| FR-1117 | Fraud cases open automatically from: BR-221/224 arrival mismatch (driver/tractor/MC at pickup ≠ awarded tuple — the flagship signal), BR-814 award-pattern anomaly, BR-228 last-minute contact change, BR-812 out-of-band payment/remit change, rating-manipulation pattern. Each case carries its triggering signal type as a field. | BR-806/814/228/812 | Must |
| FR-1118 | Review surface shows: triggering signal + raw evidence, the award/selection record (§8.2), the carrier's full onboarding and re-verification history, a **cross-load pattern view**, and the load's communication log. | BR-303/806 | Must |
| FR-1119 | Reviewer classifies — the act §15/A2 explicitly does not perform: double-brokering / carrier-identity-theft / disclosed-and-revetted substitution (closes, no case) / indeterminate-escalate. | BR-806/225 | Must |
| FR-1120 | Where the load is freight-in-motion, the case **cannot** close by cancellation. Available actions are containment only: withhold pending payment/settlement; flag the shipment `custody-under-investigation`; require identity re-check at the drop before a signature is accepted (→ §11 delivery screen, → §7 rejection code); generate a law-enforcement/insurer referral packet. `[NEEDS INPUT: whether the flag discloses to the suspect carrier before resolution]`. **Stated plainly: the system cannot recall a truck in physical transit.** That is a real ceiling, not an implementation gap. | BR-818/820 | Must |
| FR-1121 | Suspension from a fraud case follows BR-818: halts new bids/awards immediately, does not strand the in-flight load — the load stays under FR-1120's containment until physically resolved. | BR-818 | Must |
| FR-1122 | Any fraud case tied to theft, serious injury, fatality, or an open claim goes under litigation hold — status may change, the case and its evidence may never be deleted. | BR-819 | Must |

### 13.4 Override powers and their controls

**Overridable, controlled:**

| ID | Requirement | Traces | Pri |
|---|---|---|---|
| FR-1123 | Force a stuck lifecycle transition (e.g. `AWARD_PENDING` past its window with no automated resolution) — named actor, reason, before/after state, mandatory audit entry. | BR-306 | Must |
| FR-1124 | Re-award after `AWARD_DECLINED`/`LAPSED`/`VOIDED_INELIGIBLE` — runs the same eligibility gate and ranking as the original auction (`DEC-309`'s cascade or re-auction). Ops triggers which path applies; ops may **not** hand-pick a specific winning carrier outside the ranked pool. | BR-301/304, `DEC-309` | Must |
| FR-1125 | Waive a charge / approve a claim payout — the distinct ops role BR-907 already mandates, **plus** a second approver above `[NEEDS INPUT: threshold]`, never the same person who processed the original request. | BR-907 | Must |
| FR-1126 | Correct an operational data-entry error — audited, old value retained, reversible in the log. | derived | Should |
| FR-1127 | Reinstate a suspended/removed carrier — second approver distinct from whoever suspended (fires `EVT-1050`, §12.1a). | BR-817 | Must |

**Never overridable — refused outright:**

| ID | Requirement | Traces | Pri |
|---|---|---|---|
| FR-1128 | The eligibility gate (§15) may **never** be bypassed to force-award to a carrier that failed it for that load, at any tier. **This is the override this spec refuses to build.** It would directly defeat the negligent-selection defence the whole mechanism exists to construct (`DEC-LOCK-001`, *Montgomery*), and is the cleanest insider-fraud vector available. | `DEC-LOCK-001`, BR-301/803/814 | Must |
| FR-1129 | A captured POD/BOL signature (`ENT-316`), or the award's selection record (`ENT-312`), is never edited or deleted — annotate/append only. | BR-809/819 | Must |
| FR-1130 | A closed auction's ranked bid order or winner determination is never re-ordered after the fact. A wrong result is corrected only by a new, separately-logged event, never by editing history. | BR-303/305 | Must |
| FR-1131 | No ops actor approves their own override, waiver, carrier-approval, or reinstatement — segregation of duty is structural, not a training policy. | derived, insider-fraud control | Must |

### 13.5 Support impersonation

§5 owns the mechanism (auth/session). F11 owns the workflow and its limits.

| ID | Requirement | Traces | Pri |
|---|---|---|---|
| FR-1132 | Initiation requires target user, scope (whole-account read vs. one named load), and a reason. Session is time-boxed (`[NEEDS INPUT: duration]`), auto-expires. | → §5 | Must |
| FR-1133 | For an org user, impersonation requires consent captured per session. `[NEEDS INPUT: implicit-via-ToS vs. explicit per-session opt-in]`. | derived | Must |
| FR-1134 | Read-only by default. Any mutating action taken while impersonating requires a separate, explicit "acting on behalf of user X, ticket Y" confirmation, logged distinctly. | audit integrity | Must |
| FR-1135 | Impersonation never performs an identity-bound action: accepting an award, signing a POD, changing payee-of-record, changing banking/remit. | BR-902/903/909/812 | Must |
| FR-1136 | The consignee holds no account (§2); "support view" for a consignee means viewing the content behind their tokenised delivery link as they see it, not impersonating a login that does not exist. | §2 | Must |

### 13.6 Claims intake and collections support

Does not duplicate §8/A6 pricing or A8 adjudication — F11 owns intake, triage, and the ops-facing
tracking surface.

| ID | Requirement | Traces | Pri |
|---|---|---|---|
| FR-1137 | Intake captures BR-807's §370.3 minimum content from shipper submission, carrier dispute, or consignee relay. | BR-807/906 | Must |
| FR-1138 | Every open claim's 30/120/60-day obligation clock surfaces as an auto-escalating case (FR-1107) as it nears deadline; the statutory floor is never configurable downward. | BR-807/808 | Must |
| FR-1139 | Intake separates freight disputes from money disputes, routing each to its owning path — F11 does not determine liability or amount. | BR-811 | Must |
| FR-1140 | Collections surface shows F6-flagged aged receivables/payables; F11 provides contact-attempt logging, dispute-hold flagging, escalation-to-external-collections triggers `[NEEDS INPUT: process/agency]`. | derived | Should |
| FR-1141 | The charge-waiver action (FR-1125) is initiated from either the exception queue or the collections surface and always writes back to the linked invoice/case — one source of truth. | BR-907 | Must |

### 13.7 Configuration management

| ID | Requirement | Traces | Pri |
|---|---|---|---|
| FR-1142 | A governed surface represents §8.7's eleven open auction parameters (`DEC-302`..`312`) as versioned settings, not code constants. **Requires `PLATFORM_CONFIG_ADMIN`, `ROLE-230`, `PERM-264` (§4.1) — the role this assembly added because this requirement had none.** | `DEC-302`..`312` | Must |
| FR-1143 | A parameter change never silently alters terms bidders already committed to: values lock at `PUBLISHED`; changes apply to auctions not yet published, unless the parameter is itself a designed runtime behaviour. | BR-307 | Must |
| FR-1144 | Every parameter/threshold change is versioned, attributed, reasoned; the version applied to a given auction is stored on that auction's award record. | BR-303 | Must |
| FR-1145 | The eligibility-gate content (§15's six-tuple thresholds, `DEC-201`'s chosen rigour tier) is a governed setting under the same discipline as FR-1144, changeable only by `PLATFORM_CONFIG_ADMIN` — distinct from `PLATFORM_CARRIER_VETTING` (`ROLE-223`) — no reviewer loosens the gate they themselves operate under. | `DEC-201`, BR-200 | Must |
| FR-1146 | Feature flags are a separate, audited toggle set from business-rule parameters — never conflated. | derived | Should |

### 13.8 Internal reporting

| ID | Requirement | Traces | Pri |
|---|---|---|---|
| FR-1147 | Daily ops reporting surfaces KPI-01 through KPI-17 with KPI-05..09 — the counter-metrics — rendered at **equal visual weight** to KPI-04 (price), never subordinated. | KPI-04..09 | Must |
| FR-1148 | The queue itself feeds a "marketplace health" view: open-case count and age by domain tag, fraud cases opened/closed this period, vetting approvals/rejections/overrides this period, claims aging against statutory deadlines. | FR-1102/1107/1109 | Should |
| FR-1149 | Reporting is read-only; no report triggers a business action directly. | audit hygiene | Must |

### 13.9 Permission shape — already folded into §4

F11's own permission-shape table (ops-reviewer / ops-vetting-reviewer / ops-fraud-reviewer /
ops-senior / ops-config-admin / ops-support) is the source of §4.1's `ROLE-229`
(`PLATFORM_SENIOR_REVIEWER`) and `ROLE-230` (`PLATFORM_CONFIG_ADMIN`) — see §4's
**[ASSEMBLER ADDITION]** notes for the full reasoning. No further action needed here.

### 13.10 Events — already folded into §12

F11's own event list (`case.opened` · `case.claimed` · `case.escalated` · `case.resolved` ·
`vetting.approved`/`.rejected`/`.held` · `fraud.classified` · `override.executed` ·
`waiver.approved` · `config.parameter_changed` · `impersonation.started`/`.ended`) is unnumbered in
F11's own draft. Cross-checked against §12.1/§12.1a: `case.opened`/`case.resolved` map onto §12.1a's
newly-canonicalised `ExceptionCase` events; `vetting.approved`/`.rejected`/`.held`,
`fraud.classified`, `override.executed`, `waiver.approved`, `config.parameter_changed`,
`impersonation.started`/`.ended` have **no equivalent anywhere in §12's 51-event catalog** —
genuine gaps, not duplicates. These are internal ops-tooling events (who did what to the console
itself) rather than persona-facing lifecycle notifications, which is plausibly why F10 never covered
them — but they still need a wire event if `API-482`'s audit log or any future ops-side webhook is
to be event-driven rather than poll-only. **Not invented here** (assigning six-plus new `EVT-` rows
with tiers/channels for an ops-internal audience F10 never specified is exactly the kind of
"papering over" the assembly brief forbids) — flagged in `frd-assembly-report.md` as an open item.

### 13.11 CHALLENGE — the origin of §3.3, restated for the record

`spine.md` §3 models exceptions as lifecycle **states** on the parent entity. That collapses when
two independent exceptions apply to one load at once. FR-1100/1101 require `ExceptionCase` as a
first-class F3 entity — **accepted, and it is §3.3/`ENT-324` today.**

### 13.12 Edge Case register (18)

| ID | Trigger | Behaviour | Who decides | Unresolved? |
|---|---|---|---|---|
| EC-1100 | Two ops users claim the same case near-simultaneously | Optimistic lock; first commit wins, second sees a conflict error (→ §7) | System | No |
| EC-1101 | Claimed case's owner goes inactive, no auto-release threshold set yet | Case ages visibly (time-in-queue keeps counting per FR-1109) | Ops lead | Yes — depends on FR-1106 |
| EC-1102 | Fraud case and reinstatement request open on the same carrier at once | Reinstatement request blocks/links to the open fraud case; cannot resolve independently | Fraud reviewer must classify/close first | No |
| EC-1103 | An override is attempted on a load already under litigation hold | Override proceeds but the hold status is force-surfaced in the audit entry | System enforces field; counsel decides disclosure scope | Yes |
| EC-1104 | Impersonation requested on a user who is the subject of an open fraud case against their own account | Blocked while the fraud case is open | System rule | No |
| EC-1105 | Config parameter change submitted while several auctions are `AUCTION_OPEN` | Per FR-1143, change queues for future auctions only; open ones unaffected | System | No |
| EC-1106 | Second-approver required but no second qualified person on shift | No safe default — action stalls until a second approver is available | Client staffing model (DEP-900) | Yes, explicitly |
| EC-1107 | Mismatch turns out to be a legitimate substitution the shipper approved out-of-band, unrecorded | Classifies "disclosed-and-revetted," case closes, but the review itself is recorded | Fraud reviewer | No |
| EC-1108 | A party under active fraud investigation requests their own selection record for legal defence | Release vs. investigation-integrity conflict, no default picked | Counsel + fraud lead | Yes |
| EC-1109 | Ops actor waives a charge on an account they have an undisclosed personal relationship with | Not fully software-detectable beyond FR-1131's role/actor check | Policy/training control, residual | Yes, partially |
| EC-1110 | Eligibility-gate config (FR-1145) proposed before `DEC-201` is decided | Gate ships at current default, versioned; surface exists regardless of which `DEC-201` option lands | Client (`DEC-201`) | Yes |
| EC-1111 | A case's freight-in-motion signal flips mid-review | Re-prioritises live; reviewer isn't relying on a stale snapshot | System | No |
| EC-1112 | Fraud-relevant fact reported via the no-account consignee relay, not the driver/dock signal | Case opens, tagged unverified-source, corroboration required before classification | Fraud reviewer | No |
| EC-1113 | Overnight/weekend exception volume exceeds informal coverage; freight moves 24/7 | Tooling has no coverage-gap remedy | Client | Yes, explicitly (`DEP-900`, `RSK-027`) |
| EC-1114 | Force-transition override attempted on a load with an open, unresolved fraud case | Blocked/warned before proceeding | System warns; ops user proceeds or stops | No |
| EC-1115 | Two fraud cases on different loads share a carrier pattern | Pattern view surfaces it; no auto-classification across cases without a human | Fraud reviewer | Partially |
| EC-1116 | Ops user attempts to view impersonation session content after it auto-expired | Session dead, no replay of live actions; only the audit log survives | System | No |
| EC-1117 | A carrier disputes a suspension that was itself the output of an override chain | Full chain must be reconstructable from linked case/audit records for the dispute to be answerable at all | Ops senior / dispute path | No |

**Counts:** 50 FR · 18 EC · 14 `[NEEDS INPUT]` · 4 open `DEC-` (cross-referenced).

---

## 14. F12 — Platform NFRs: Security, Tenancy Isolation, Availability, Observability, DR

*Full source: `frd-F12-platform-nfr-security.md`. F12's `CHALLENGE` (the `aggregate_threshold` scope
kind) is already accepted into §1/§4 — no propagation fix needed here.*

**ID block 1200-1299.** §4 owns the permission model; this section owns that it cannot be bypassed
beneath it.

### 14.1 Tenant isolation — the highest-severity property in this system

A shipper seeing a competitor's freight, or a carrier seeing a rival bid, ends the business.
Isolation holds **beneath** §4's RBAC — every layer below the API independently refuses cross-org
data even if an application check is missing.

| ID | Layer | Requirement | Test |
|---|---|---|---|
| NFR-1200 | Data store | Every row traceable to one `org_id`; cross-org read blocked at the store itself (row-level security / mandatory tenant predicate), not only the query builder | Read with wrong tenant context on every table → zero rows, in CI |
| NFR-1201 | Cache | Keys namespaced by `org_id`; no shared key serves two tenants | Poison one tenant's key pattern, assert no cross-read |
| NFR-1202 | Search index | Results filtered server-side by tenant scope before ranking; unscoped query structurally impossible | Query without filter clause must fail to compile/execute |
| NFR-1203 | File/document storage | Authority docs, insurance certs, BOL/POD images under tenant-scoped path; signed, expiring, single-purpose URLs only | Path traversal / prefix guess → denial + `EC-1201` |
| NFR-1204 | Logs | Structured logs carry `org_id`+`trace_id`; log *access* itself is tenant- and role-scoped for support staff | Support role cannot query outside assigned case without logged elevation |
| NFR-1205 | Backups | Encrypted; single-tenant incident restore does not expose another tenant's rows to the operator | Restore drill: one org's recovery, no cross-org visibility |
| NFR-1206 | Analytics/BI/reporting | Lane-average/benchmark pricing never reveals an identifiable competitor's bid | Figure below the `k`-anonymity floor of contributing orgs must refuse, not approximate |
| NFR-1207 | **Errors & diagnostics** | An error body, stack trace, or debug payload never carries another tenant's identifiers, freight, bids, or PII; §1's canonical error envelope is sanitized before serialization | Every documented error path (→ §7) contract-tested for foreign `org_id`/entity leakage |
| NFR-1208 | Support/impersonation tooling | "View as" a tenant is session-scoped, time-boxed, reason-coded — never a standing credential | 100% of sessions logged: actor, target org, reason, duration (→ §13) |
| NFR-1209 | Shared compute | No worker/queue message processes two tenants without re-deriving scope per unit of work | Poisoned job cannot pull unscoped data |

**This section's `CHALLENGE` — already resolved into §1/§4.** F12 proposed `aggregate_threshold`
as a sixth scope kind, for exactly `NFR-1206`'s cross-org, de-identified, threshold-gated
comparative reporting. It is in §1's closed scope-kind list and §4's matrix already reflects it
where applicable — recorded here as the historical origin, not an open item.

### 14.2 Availability — tiered by consequence

A data problem never auto-aborts a physical trip. All numeric targets `[NEEDS INPUT]`; the tiering
and degradation contract is not optional even before numbers exist.

| ID | Tier | Example | Degradation when a dependency is down |
|---|---|---|---|
| NFR-1210 | 0 — physical-blocking | POD/BOL capture, custody handover, driver/truck assignment lookup | Offline-capable local capture, client-timestamped, syncs on reconnect — never blocks a truck at the dock |
| NFR-1211 | 1 — auction-critical | Bid submission, auction close, award | Close **extends** rather than closing on an unreliable clock (→ §8); never award on partial data |
| NFR-1212 | 2 — operational | Load publish, eligibility check, notifications | Queue + retry; visible "delayed" beats false success |
| NFR-1213 | 3 — informational | Dashboards, reports, ratings | Stale-data banner acceptable; never blocks Tier 0/1 |
| NFR-1214 | Evidence retrieval | Selection record, audit log, POD on demand | Served off a path architecturally independent of the auction/award path, so a degraded auction never hides a record a party has the right to review (49 CFR 371) |

Every external dependency needs documented timeout/retry-backoff/circuit-breaker and a fallback that
degrades the *feature*, never the *trip*. Numbers `[NEEDS INPUT]`.

### 14.3 The 24/7 reality

| ID | Requirement |
|---|---|
| NFR-1215 | No planned maintenance overlaps a known high-load period; zero-downtime rolling deploys for Tier 0/1. Windows `[NEEDS INPUT]` — freight has no universal quiet hour |
| NFR-1216 | Continuous on-call, not business-hours; escalation/paging thresholds `[NEEDS INPUT]`, must exist pre-launch |
| NFR-1217 | Support path for a driver at a dock does not assume desk-hours staffing (→ §13) |
| NFR-1218 | Migrations run without locking Tier 0 write paths — backward-compatible given zero acceptable downtime |

### 14.4 Data classes and retention

| Class | Period | Fixed by |
|---|---|---|
| Broker transaction record (6 elements) | ≥3 yrs | 49 CFR 371.3 |
| BOL/POD/exception notation (`ENT-316`) | **Open** — claim/suit horizon (Carmack) | — |
| Bid history, selection/award record | **Open**, litigation-evidence value argues long | — |
| Consignee contact data | **Open**, purpose-limited | State statute |
| Driver personal/location data | **Open**, minimise; no ELD/HOS/Clearinghouse/D&A (§9.6) | State statute |
| Audit log | **Open** — NFR-1219: cannot be shorter than the retention of the record it documents | — |
| Security/error logs, telemetry | `[NEEDS INPUT]` — high-volume, needs its own cost/legal review | — |
| Backups | `[NEEDS INPUT]`, ≥ live-data retention per class | — |

**NFR-1220 — Legal hold overrides purge.** Any record under litigation hold, claim, or subpoena is
exempt from automated deletion regardless of class; the hold is logged, reversible only by the
authority that placed it. **Corresponds to `Load.legal_hold` at `ENT-307` (§3.2, FR-347).**

### 14.5 Privacy for the two populations who never signed up

| ID | Requirement |
|---|---|
| NFR-1221 | Consignee reaches access/deletion/opt-out from the unregistered, tokenised delivery link alone — no account required |
| NFR-1222 | Driver rights requests route through the employing carrier for data the platform doesn't hold directly; a direct path exists for what the platform does hold (assignment history, in-trip location) |
| NFR-1223 | **Deletion vs. evidentiary retention:** a request against a record inside its 371.3 window, under legal hold, or evidence for an open claim is not auto-honoured; system supports a distinct **retained-restricted** state |
| NFR-1224 | Location data minimised to active-trip need; retained-trip-history period is a separate `[NEEDS INPUT]` |
| NFR-1225 | Third-party processors bound by terms matching this section's class-level retention/deletion |

**DEC-1200 (options).** How `retained-restricted` surfaces: **(a)** name the legal basis/duration —
transparent, more friction. **(b)** confirm receipt only. **(c)** silent partial deletion of
non-required fields. Needs counsel + product.

### 14.6 The immutable audit trail

The selection record (`ENT-312`) is legal evidence post-*Montgomery*; 49 CFR 371 gives parties a
right to review the broker record. This must be structurally unfalsifiable.

| ID | Requirement |
|---|---|
| NFR-1226 | Append-only store for load/bid/award/eligibility/POD/claim state changes and every permission grant/revoke. No in-place `UPDATE`/`DELETE`; corrections are compensating entries |
| NFR-1227 | Tamper-evidence: entries hash-chained (or equivalent) so any alteration anywhere is detectable |
| NFR-1228 | The selection record snapshots safety/insurance/authority evidence **as it existed at award time** — not a live pointer that changes when source data later changes |
| FR-1200 | A record-production capability assembles the full transaction record (371.3's 6 elements + selection record + custody events) for an entitled party within a stated turnaround `[NEEDS INPUT]`, designed against the pending 48-hr FMCSA proposal |
| NFR-1229 | Audit retrieval served off a path independent of the transactional write path |
| NFR-1230 | Audit trail is tenant-scoped per §14.1; cross-org audit access is itself audited, bounded to platform-ops (→ §13) |

### 14.7 The ODbL architectural boundary — enforceable, not advisory

Per `DECISIONS.md` `DEC-LOCK-002`: `osm.*` tables compute Produced Works internally but raw records
never cross the API boundary.

| ID | Requirement | Test |
|---|---|---|
| NFR-1231 | No response body, export, webhook, or error `details` field ever contains a raw row or row-derived field-set from `osm.*` | Static: any serializer touching an `osm.*` model flagged at build |
| NFR-1232 | Only aggregated Produced Works (feasibility flag, cost-floor number, distance) cross the boundary — never station name/coordinates/tags sourced from `osm.*` | Field-provenance tagging: a field whose lineage touches `osm.*` and isn't a documented aggregation is rejected pre-serialization |
| NFR-1233 | CI-enforced — not a code-review convention | Release blocked if the test is missing or fails, same severity as a security-scan failure |
| EC-1200 | New endpoint joins `osm.*` "for one internal report" | Boundary test runs against it before merge, no exemption path | — |

### 14.8 Observability

| ID | Signal | What must be measurable |
|---|---|---|
| NFR-1234 | Golden signals per tier | Latency/error-rate/saturation/traffic per Tier (§14.2) — a Tier 3 outage never masks a Tier 0 problem |
| NFR-1235 | Correlation | `trace_id` (§1) threads logs/metrics/traces end-to-end |
| NFR-1236 | Authorization denials | Rate/pattern of denials, tenant-scoped, alertable |
| NFR-1237 | Cross-tenant attempt | A request whose resolved scope would have crossed org boundary (caught by §14.1) is logged as a **security event**, not silently 403'd |
| NFR-1238 | Impersonation/override use | "View as," manual award override, claim waiver — first-class observable events with volume trend |
| NFR-1239 | Auction integrity | Bid-timing anomalies, rotation patterns, shill-bid heuristics — feeds §8/§10's anti-gaming, observed here as platform health |
| NFR-1240 | SLO burn | Error-budget consumption per Tier; multi-window burn-rate alerts, thresholds `[NEEDS INPUT]` |

### 14.9 Secrets, keys, encryption, third-party data handling

| ID | Requirement |
|---|---|
| NFR-1241 | Secrets in a dedicated store, never in config/source/logs; rotation interval `[NEEDS INPUT]` |
| NFR-1242 | Encryption in transit (all hops) and at rest for every §14.4 data class — mandatory, no exception path |
| NFR-1243 | Key rotation/revocation is drillable; compromise blast radius bounded by per-purpose key separation |
| NFR-1244 | Every third-party processor has a data-processing agreement matching this section's retention/deletion/breach obligations before integration |
| NFR-1245 | Breach-notification procedure/timeline `[NEEDS INPUT]` per state law; drilled, not shelved |

### 14.10 Backup and disaster recovery

| ID | Requirement |
|---|---|
| NFR-1246 | RPO `[NEEDS INPUT]` per Tier — Tier 0 evidentiary data drives the tightest RPO |
| NFR-1247 | RTO `[NEEDS INPUT]` per Tier |
| NFR-1248 | Backups verified by actual restore drill, cadence `[NEEDS INPUT]` |
| NFR-1249 | Restore respects §14.1 isolation and §14.4 retention boundaries |

**The honest question:** freight physically moves while the system is down. "Recovered" for a Tier
0 system is not "database restored to a consistent point" — it means the gap between last-synced
state and physical reality is **reconciled**, not assumed correct. A truck that moved during an
outage needs a driver/dispatcher-asserted, timestamped reconciliation workflow (→ §13), not a silent
overwrite.

### 14.11 Edge-case register (15)

| ID | Trigger | Behaviour | Decides | Unresolved |
|---|---|---|---|---|
| EC-1201 | File path/prefix guessed or brute-forced | Signed-URL denial + security alert | Platform | Alert threshold `[NEEDS INPUT]` |
| EC-1202 | Support agent queries logs outside assigned case | Denied (NFR-1204); elevation needs a logged reason | Platform ops | Elevation approval flow → §13 |
| EC-1203 | Benchmark report would reveal a single-bidder lane | Refuse below `k`-anonymity floor (NFR-1206) | — | Floor value `[NEEDS INPUT]` |
| EC-1204 | Unanticipated exception leaks a foreign `org_id` in a stack trace | Caught pre-release by NFR-1207; if it reaches prod, treated as a security incident | Security on-call | Severity threshold |
| EC-1205 | Tier 0 capture fully offline, no dock connectivity | Local capture, capture-time timestamp, sync + reconcile on reconnect | §6/§7 | Conflict resolution on double-sync |
| EC-1206 | Auction close-time infra degraded | Extend, never close on an unreliable clock | §8 | Extension length `[NEEDS INPUT]` |
| EC-1207 | Deletion request against a record under hold / in 371.3 window | `retained-restricted`, not deleted | Counsel + Platform | Disclosure model — `DEC-1200` |
| EC-1208 | Hold placed after a related record already queued for purge | Purge suspendable per-record on demand | Platform | Hold-placement latency `[NEEDS INPUT]` |
| EC-1209 | Feature joins `osm.*` "just this once" | CI boundary test blocks merge regardless of intent | Platform eng | No exemption path — by design |
| EC-1210 | Regulator/counsel subpoenas the full transaction record | FR-1200 serves it off the audit-independent path | Counsel + Platform | Turnaround SLA `[NEEDS INPUT]` |
| EC-1211 | System recovers from Tier 0 outage; pickup/delivery occurred during the gap | Reconciliation workflow, not silent overwrite | Ops → §13 | Reconciliation UX + authority |
| EC-1212 | Driver rights-request arrives directly, not via carrier | Standing/verification required | Counsel | Verification method |
| EC-1213 | Impersonation session left open beyond intended use | Time-boxed auto-expiry, not manual-only close | Platform | Timeout value `[NEEDS INPUT]` |
| EC-1214 | Restore for one tenant's incident overlaps another tenant's active hold | Isolation (NFR-1205) and hold (NFR-1220) both hold simultaneously | Platform + Counsel | Concurrent-constraint procedure |
| EC-1215 | Cross-tenant read succeeds despite layered defences | SEV-1 security incident, breach-assessment procedure triggers | Security on-call | Customer-notification threshold |

**Counts:** 50 NFR · 1 FR · 15 EC · 1 open `DEC-` · 21 `[NEEDS INPUT]`.

---

## 15. F13 — Carrier Vetting & the Eligibility Computation Service

*Full source: `frd-F13-eligibility-vetting.md`. This block did not exist in the original ID
allocation — it exists because §8 (F6) filed a `CHALLENGE` mid-phase when it discovered its entire
gate mechanism called a function nobody owned. F13's four-argument `eligibility()` signature is
**the canonical one** used throughout this document — see §8.1's boxed note for the full
reconciliation against F6's original seven-argument draft.*

**ID block:** 1300-1399. **Owns:** carrier onboarding verification · the `eligibility()`
computation service · authority/insurance/safety-signal ingestion + freshness · credential lifecycle
· re-verification cadence · the eligibility evaluation record (§8's selection record quotes it) ·
fraud-adjacent identity signals at onboarding/dispatch · gate-policy versioning · overrides.
**Must NOT write:** equipment/trailer taxonomy, driver qualification, HOS, assignment/substitution
(§9 — F13 calls §9's sub-checks, doesn't re-specify them) · bid/award mechanics, selection-record
write points (§8) · fraud classification/penalty (§13, F11) · entity/state canon (§3) · permission
rows (§4) · error taxonomy (§7) · ops UI (§13).

### 15.1 The `eligibility()` contract — canonical signature

**FR-1300.** Canonical signature: `eligibility(carrier_id, truck_id, driver_id, load_id) →
{status: ELIGIBLE|INELIGIBLE, reasons: [{code, element, detail}], gate_version, policy_version,
evaluated_at, snapshot_id}`. **A call, never a cached set** — every invocation re-resolves all six
tuple elements from current/last-refreshed data; nothing reads from a prior result.

**This is the resolution of the eligibility-signature conflict, referenced from §8.1.** F13's own
`CHALLENGE` against F6's literal reading is preserved for the record: F6 wrote the signature as
`eligibility(carrier, authority, insurance, safety_signal, truck, driver, load)` — implying the
caller resolves authority/insurance/safety_signal. That is BRD A2's *tuple concept*, not the call
surface; **F13 resolves those three internally from `carrier_id`.** No behavioural disagreement
existed — flagged so the assembler didn't merge two signatures into the API catalogue, and it
didn't: §6.2's `API-468` and §15.9's `API-1300` both now carry the four-argument form.

**FR-1301.** Output composes two mandatory sub-evaluations: (a) **carrier/authority/insurance/
safety** — computed here, §15.3-§15.4; (b) **equipment/driver match + availability** — F13 calls
§9's per-load match function (FR-702/707, HOS capacity), folding its pass/fail + reasons into the
same `reasons[]` unmodified. F13 never re-derives §9-owned facts, only aggregates.

**FR-1302.** `reasons[]` is never empty on `INELIGIBLE`, structured (`element` = one of the six
tuple elements) — §8's selection record and the negligent-selection defence both consume it as the
evidentiary "why," not just the boolean.

**FR-1303. Determinism and replay.** Every evaluation persists a **full input snapshot**, not
pass/fail alone: `gate_version` (logic), `policy_version` (§15.6's thresholds), and a copy of the
actual authority status, insurance evidence, safety data and §9 sub-result **as read at that
instant** (`snapshot_id`). Reconstructable **from stored data alone, months later** — no live
re-query — matching §8's FR-606 exactly, since §8's selection record quotes this one, not restates
it.

**FR-1304.** Gate-policy changes (§15.6) are never retroactive; an evaluation cites the
`policy_version` active at `evaluated_at`, immutable once written (mirrors §8's FR-650).

**FR-1305.** F13 does not decide *when* it is called — §8 calls it at bid submission and again per
candidate at award (§8 FR-600/602). The same tuple returning a different result between calls is
correct behaviour, not a bug.

### 15.2 Entities — consolidated at §3.2 (`ENT-1300`–`1307`)

`CarrierVettingRecord` · `OperatingAuthorityRecord` · `InsurancePolicyRecord` · `SafetySignalRecord`
· `CredentialDocument` · `EligibilityGatePolicy` · `EligibilityEvaluation` ·
`IdentityMismatchSignal` — full field detail at §3.2. No duplication found against §3's base
catalog; these are additive.

### 15.3 External data ingestion — capabilities, not vendors

| Capability | What it does | Freshness posture | Unreachable behaviour |
|---|---|---|---|
| **Authority status lookup** (FMCSA SAFER-class) | Active/revoked/OOS status, name/address, authority age | Periodically refreshed store (`DEC-1300`); `[NEEDS INPUT: award-time live vs store]` | Last-known-good + `stale_after` flag; **never auto-fails** — flagged pass or hold per policy tier; routes to §13 past threshold `[NEEDS INPUT]` |
| **Safety/CSA-SMS feed** | Safety rating + BASIC scores | Batch-refreshed store only, no live per-bid call | Same posture; last-refreshed timestamp visible |
| **Insurance/COI verification** | COI current, platform as certificate holder, covers bound equipment; ingests cancellation notices (carrier PDFs never suffice alone) | Onboarding + event push + periodic reverification | No push ≠ assumed valid; expiry alone drives auto-`INELIGIBLE_FOR_NEW_BIDS` (BR-217) |
| **Identity/document verification** | Signer ID, name/address vs authority | Onboarding + material change | Onboarding holds open, not silently approved |
| **W-9 capture** | Tax-form intake | Onboarding, before first payout | Collected/stored only; A6 gates payout — **not** in the eligibility tuple |

**FR-1310.** No upstream reachability problem may **auto-abort a trip already in motion** (BR-218/
219) — data-layer failure degrades to a flag + §13 route, never a transit action (§10). **FR-1311.**
Every ingested field records its **source** (verified vs self-reported) so the snapshot (FR-1303)
distinguishes "we checked" from "carrier told us."

### 15.4 Re-verification cadence — `DEC-1300`, options only

Cadence can differ **per signal** — a policy field, not one number.

| Option | Mechanism | Cost | Risk if chosen |
|---|---|---|---|
| A — Real-time per bid | Live call every `eligibility()` invocation | Highest — call volume = bid volume, rate limits, latency | Lowest staleness risk; most defensible post-*Montgomery* |
| B — Periodic batch refresh | Store on a fixed interval `[NEEDS INPUT]`; `eligibility()` reads the store | Low, predictable | Refresh-to-lapse gap; mitigated by BR-217's expiry auto-block |
| C — On-demand at award only | Live call only at award walk (§8 FR-602); store at bid time | Medium | Bid-time result stale for whole open window, caught only at award |

**DEC-1301 — staleness threshold.** Store-age at which a signal stops being "current." `[NEEDS
INPUT]` per signal, on `EligibilityGatePolicy` (`ENT-1305`), versioned. **DEC-1302 — mixed cadence,
likely shape.** Authority = A or C; safety = B; insurance = event-driven push + B baseline + expiry-
date hard block regardless of choice. `[NEEDS INPUT: final per-signal selection]`.

### 15.5 Credential lifecycle — never auto-abort, always flag

| BRD source | Trigger | F13 behaviour |
|---|---|---|
| BR-217 | Authority/COI/CDL lapses (own detection, or §9 for CDL) | `INELIGIBLE_FOR_NEW_BIDS` same-day, automatic; blocks new bids only |
| BR-218 | Lapse **between award and pickup** | Award unchanged; re-run flags the tuple, review item → §13 queue. No auto-cancel |
| BR-219 | Lapse **after custody transfer** | Same — flag to §13, no transit action (§10's domain) |
| BR-229/230 | Carrier suspended/removed | `INELIGIBLE` for new bids/awards immediately; load past pickup **not** auto-altered — flagged to §13 |
| BR-220 | Advance-expiry reminders | Content owned here; delivery → §12. Cadence `[NEEDS INPUT]` |

**FR-1320.** Every lifecycle transition above writes an addendum to the `EligibilityEvaluation`
row(s) it invalidates — original never edited in place (mirrors §8's FR-605).

### 15.6 Verification rigour vs. supply liquidity — `DEC-201`, as a versioned policy object

Most US carriers run very few trucks; a bar tuned for large fleets removes the supply this
marketplace needs. **Not a hard-coded threshold** — a versioned, effective-dated
`EligibilityGatePolicy` (`ENT-1305`), since every tuning changes *who was allowed to bid*, itself
evidence in a negligent-selection claim.

| Option | Shape | Cost | Risk |
|---|---|---|---|
| A — Uniform high bar before bidding | Every element hard-gates at onboarding | Fewest edge cases, strongest litigation posture | Shrinks the pool hardest — small-fleet carriers (the actual supply) excluded |
| B — Light bar to bid / heavy bar to win | Cheap onboarding check; full re-verification only for the tuple that would win | Best liquidity, lowest friction | Bid-time record with a light bar is weaker evidence if scrutinised without winning |
| C — Baseline bids, tiered award review | Authority/insurance always hard-gate; safety threshold/authority age enter a review tier near award | Balances both | Tier boundary is itself tunable, contestable — needs its own change log |

**FR-1330.** Whichever option is chosen is a field on `EligibilityGatePolicy`, not application
logic; changes are authored, dated, attributed, never retroactive. `[NEEDS INPUT: Boss to choose
A/B/C — reaches §8.7]`. **Editing this policy requires `PLATFORM_CONFIG_ADMIN`, `PERM-264` (§4.2).**

### 15.7 Fraud-adjacent identity checks — signals only, not classification

BR-225 binds this section: **facts, never a verdict.** Classification, case-opening and consequence
are §13's (F11).

| Check | BRD source | F13 output |
|---|---|---|
| Legal name/address vs authority record mismatch | BR-207 | Holds onboarding; `IdentityMismatchSignal` (`ENT-1307`) |
| Authorized-signer identity | BR-208 | ID doc on file, reviewable; no auto-block criterion invented |
| Brand-new authority as risk signal | BR-202 | Age captured as **distinct field**, visible at review; **no auto-block on age alone** |
| Dispatch-contact change not matching onboarding record | BR-228 | Flag to review, not hard block |
| Broker double-brokering path | BR-223 | Downstream asset-carrier must independently clear `eligibility()` before dispatch — F13 evaluates the *sub-carrier's* tuple only, does not adjudicate the pattern |
| Pickup mismatch (driver/tractor/MC vs bound tuple) | BR-221/224/227 (§9 executes the check) | F13 supplies the bound-tuple record; the mismatch fact routes to §13's classification (BR-806) |

**FR-1340.** Every signal is timestamped, attributed to the check that produced it, and appended to
`EligibilityEvaluation` or `CarrierVettingRecord` — never silently dropped even if no case opens.

### 15.8 Overrides — evidence, not a bypass

**FR-1350.** An ops reviewer (`PLATFORM_CARRIER_VETTING`, `PERM-260`, §4.2 — **[ASSEMBLER FIX]**
F13's own draft wrote "→ F2 PERM-1300" here, an ID in the *wrong agent's block*: `PERM-` is §4's
prefix, block 200-299, never 1300-1399. Corrected to `PERM-260`, the row this assembly added at §4.2
specifically to close this reference.) may admit a carrier the gate rejected. Requires named identity
+ stated reason — unattributed overrides cannot be persisted (mirrors §8's FR-607).

**FR-1351.** The override does not alter the original `EligibilityEvaluation` row; it writes an
addendum row of type `OVERRIDDEN`, referencing the original result and every reason overridden
individually — a blanket override hiding *which* element failed is not permitted.

**FR-1352.** Stated plainly, since it governs §13's review screen: **an override is itself evidence
in a negligent-selection claim** — it converts "the gate said no" into a discoverable fact with a
name attached. §13's console must surface the override's history wherever the evaluation is later
shown, not just at decision time.

### 15.9 API surface

| ID | Endpoint | Notes |
|---|---|---|
| API-1300 | `POST /v1/loads/{load_id}/eligibility-checks` | Body `{carrier_id, truck_id, driver_id}`; internal, §8 calls at bid+award — **same four-argument contract as §6.2's `API-468`, corrected together (§8.1)** |
| API-1301 | `GET /v1/carriers/{id}/eligibility-evaluations` | Audit history; scoped `own_org`/`platform_wide` (§4) |
| API-1302 | `POST /v1/carriers/{id}/documents` | Credential upload (authority cert, COI, W-9, ID doc) |
| API-1303 | `GET /v1/carriers/{id}/documents` | Status per document, expiry, source |
| API-1304 | `GET /v1/carriers/{id}/eligibility-status` | **Advisory only**, dashboards (§11); only a per-load `eligibility()` call is authoritative |
| API-1305 | `POST /v1/eligibility-evaluations/{id}/override` | FR-1350 identity+reason required |
| API-1306 | `GET/POST /v1/eligibility-gate-policies` | Policy authoring (§15.6), **`PLATFORM_CONFIG_ADMIN`-scoped (`PERM-264`, §4.2)** — F13's own draft said only "admin-scoped," which this assembly resolves to a specific role rather than leave ambiguous between `PLATFORM_ADMIN` and `PLATFORM_CARRIER_VETTING` |

Errors route via §1's canonical envelope to §7's taxonomy; representative codes:
`ELIGIBILITY_AUTHORITY_REVOKED`, `ELIGIBILITY_COI_EXPIRED`, `ELIGIBILITY_COI_COVERAGE_MISMATCH`,
`ELIGIBILITY_SAFETY_DATA_STALE`, `ELIGIBILITY_EQUIPMENT_MISMATCH` (§9 reason, surfaced through this
envelope), `ELIGIBILITY_DATA_SOURCE_UNREACHABLE` (flags, never hard-fails), `CARRIER_SUSPENDED`,
`OVERRIDE_MISSING_REASON`.

### 15.10 Events

`carrier.credential_lapsed` · `carrier.credential_restored` · `carrier.suspended` ·
`carrier.reinstated` · `eligibility.gate_override_applied` · `eligibility.identity_mismatch_flagged`
· `gate_policy.version_published`. **[ASSEMBLER NOTE]** `carrier.reinstated` is now canonicalised at
§12.1a as `EVT-1050`; the other six have no §12 equivalent — genuine gaps, catalogued at §16.6, same
disposition as §13.10's ops-internal events (not invented here, flagged for the next pass). **No
`eligibility.evaluated` event** — volume equals bid volume; per-evaluation events would flood §12.
Only state-changing outcomes emit.

### 15.11 Edge case register (20)

| ID | Trigger | Behaviour | Decides | Unresolved |
|---|---|---|---|---|
| EC-1300 | Authority/safety upstream unreachable at bid time | Last-known-good + `stale` flag; never hard-fails on unreachability alone | Automatic | Staleness threshold (`DEC-1301`) |
| EC-1301 | Same, at award-time re-walk (§8 FR-602) | Higher stakes — flagged in selection record | Automatic + §13 | Live vs store read at award (`DEC-1300` C) |
| EC-1302 | COI lapses between award and pickup | BR-218: award unchanged, ops flag opened | §13 | — |
| EC-1303 | Authority revoked mid-transit, post-custody-transfer | BR-219: flag only, no transit action | §13/§6 | — |
| EC-1304 | Safety batch refresh fails/falls behind; re-verification backlog misses cadence window | `refreshed_at`/`stale` visible at review; held past `DEC-1301` threshold per policy tier | Automatic | Alert threshold owner `[NEEDS INPUT]` → §14 |
| EC-1305 | Name/address mismatch vs authority record at onboarding | Onboarding held, not silently approved | Ops (§13) | — |
| EC-1306 | Brand-new authority bids | Age visible, no auto-block | Policy (§15.6 tiering) | Default review-tier entry for new authority? |
| EC-1307 | Undisclosed post-award substitution signal | Fact recorded only; routes to §13 | §13 | — |
| EC-1308 | Override admits a gate-rejected carrier | Addendum written (FR-1351); treated as evidence (FR-1352) | Named person | — |
| EC-1309 | Gate policy version changes while auctions open on old version | Mirrors §8's FR-650: in-flight evaluations keep `policy_version` | Automatic | — |
| EC-1310 | §9 sub-check (equipment/driver) unavailable or incomplete | Tuple unresolved → `INELIGIBLE`, reason element cited | Automatic | — |
| EC-1311 | Broker wins; downstream asset-carrier not yet vetted | Award proceeds provisionally (BR-223); dispatch-gate blocks dispatch, not award | Automatic + F13 gate | — |
| EC-1312 | Carrier suspended with an in-flight load | New bids/awards blocked; existing load not stranded | §13 | — |
| EC-1313 | Identity/document verification capability down at onboarding | Onboarding holds open; no default admission | Automatic | — |
| EC-1314 | W-9 missing | Blocks payout (A6), not bidding — kept out of the tuple | Automatic | — |
| EC-1315 | Identity theft at onboarding — impostor uses real MC/insurance | §15.7 checks are the only detection surface F13 owns; classification is §13's | §13 | Detection depends on `DEC-1300`/`1302` |
| EC-1316 | Dispatch-contact change not matching onboarding record | Flagged to review, never hard-blocked alone | Ops | — |
| EC-1317 | Self-declared unavailability on an asset bound to an in-progress award | Blocks *new* eligibility only; binding not retracted — conflict flagged | §13 | Precedence rule `[NEEDS INPUT]` |
| EC-1319 | Gate-policy tightening disqualifies many previously-eligible carriers | No auto-rollback; effective-dated, reviewable — thin-market fallout is §8's `DEC-310` | Ops/Boss | Cost-of-tightening not modelled here |
| EC-1320 | `EligibilityEvaluation` write fails mid-transaction | Never reports ELIGIBLE without a complete persisted snapshot | Automatic | Mechanism → §7/§14 |

**What F13 cannot resolve alone:** cadence (`DEC-1300`/`1301`) and rigour tier (`DEC-201`/§15.6) are
supply-vs-liability trade-offs only Boss, with counsel/insurer input, can set.

**Counts:** 21 FR · 7 API · 7 named events (unnumbered, 1 canonicalised at §12) · 20 EC · 9 `[NEEDS
INPUT]` · 5 open `DEC-`.

---

## 16. Cross-Cutting Reconciliations — what no single agent's output could show

Every entry below was invisible to the agent that wrote the section it touches, because each agent
saw only its own file. This section exists to state each finding once, in one place, rather than
let it echo across three or four domain sections.

### 16.1 Build-blocking decision: rival-bid visibility (`DEC-302`/`DEC-303`)

**Three agents converged on this independently, from three different angles, without seeing each
other's work:**

- **§8 (F6), the mechanism owner:** wrote `bid_visibility_mode` (`DEC-302`: `OPEN`|`SEALED`) and
  `price_disclosure_mode` (`DEC-303`: `STANDING_BEST`|`RANK_ONLY`) as open settings with no default,
  and filed a `CHALLENGE` that DEC-303's "rank only" and DEC-302's sealed-with-feedback option
  should be evaluated as *one* fork, not two, because rank feedback is the same oracle as a
  winning-flag once decrements are small.
- **§4 (F2), the enforceability owner:** ran the actual security analysis (§4.5, drawn from F2 §2.5)
  and found that **"sealed + a 'you are currently winning' flag" leaks by construction** — repeated
  decrements binary-search the standing best price, so the leak is not a bug an access-control fix
  can close; it is inherent to the feature. It also found that "open standing best price" makes
  BR-314 (bid confidentiality) **unachievable**, not merely weaker, since price patterns fingerprint
  a bidder over time even under anonymisation.
- **§11 (F9), the screen owner:** built `SCR-911` (the carrier's core bidding loop) with
  rival-visibility as a swappable parameter and three ready states, but shipped the **conservative
  default (`none`)** specifically because building past it without a locked decision risks a BR-717
  violation in production — "not a UI bug" if the default proves too permissive later.

**This is presented once, here, as build-blocking**, rather than as three separate open items in
§4.5, §8.7, and §11.2 (each of which now cross-references this section instead of re-arguing it).
**Recommendation for Boss, not a decision made on his behalf:** F2's finding effectively removes one
of the four combinatorial options — `SEALED` + `STANDING_BEST`-as-a-live-flag is not a viable
setting regardless of preference, because it cannot be built to leak-proof. The live choice is really
between `SEALED`+`RANK_ONLY` (F6's proposed merge of the two "softer" options, since F2's analysis
shows they're the same oracle), full `OPEN`, or `SEALED` with no live feedback at all. `[NEEDS
INPUT: Boss to lock DEC-302/303 before SCR-911 (§11) or the anti-gaming pattern monitor (§8.6)
build past their current conservative defaults.]`

### 16.2 BOL/POD merge — see §3.4

Already stated in full at §3.4, cross-referenced here for completeness of the "converged findings"
list. No further action.

### 16.3 The `eligibility()` signature conflict — resolved

Already stated in full at §8.1 (the fix) and §15.1 (the origin). **Canonical signature:**
`eligibility(carrier_id, truck_id, driver_id, load_id)`. Fixed at §6.2 (`API-468`), §8.1, §15.1,
§15.9 (`API-1300`). **This was found only because both F6's and F13's drafts were read side by side
during assembly** — F6 was drafted first and F13's own `CHALLENGE` text (correctly) called out the
discrepancy against F6's *specific line*, but F6's file itself was never revised, so shipping both
files unmodified would have produced two client implementations against two different contracts.

### 16.4 BRD defects found downstream — recorded, not silently patched

Per the assembly brief's explicit instruction: these are **findings against `BRD-v1.md`**, not
corrections made to it. `BRD-v1.md` is not edited by this document.

1. **`BR-111`'s equipment-type closed list omits tanker.** `BRD-v1.md` BR-111: "Equipment type is a
   closed set (dry van, reefer, flatbed, step deck, power-only, …)." Tanker is absent. §9 (F7) found
   this while building the trailer taxonomy (§9.1) and it propagates directly into `ENT-306`
   (§3.2), which **does** include `TANKER` — the FRD works around the BRD gap rather than
   inheriting it, but the BRD itself still needs a correction pass.
2. **`BR-209`/`BR-214` model equipment as one asset per carrier row.** The BRD's carrier/equipment
   model does not distinguish tractor from trailer as independently owned, insured, and available
   assets — which cannot represent drop-and-hook, one of the most common capacity patterns in US
   truckload. §3.1's `ENT-303`/`304`/`305` split (already independently absorbed by both F3 and F7)
   works around this; `BRD-v1.md` BR-209/BR-214 remain unedited and should be revisited in a future
   BRD pass.

### 16.5 F2's word-budget overage — reported, not cut

**F2 (`frd-F2-authorization-rbac.md`) measures at 4,752 words against a 2,500-word ceiling** (§1's
hard rule §8.5 in the original spine) — roughly 1.9× budget. **This document does not cut it.** The
permission matrix (§4.2, 65 rows after this assembly's additions) is the security specification for
the entire system; cutting it for a word-count target would be optimizing the wrong variable. F2's
own relayed suggestion for the cheapest cut — collapsing §4.4's 18-row × 7-column cross-org
visibility matrix down to four viewer columns — is recorded here **so Boss can see the option and
reject or accept it explicitly**, rather than have it silently applied or silently ignored. This
assembler's recommendation is against the cut: the 18×7 shape is what makes §4.4 answer "what does
*this specific* viewer see at *this specific* moment in the lifecycle," which is exactly the
question a negligent-selection or bid-confidentiality dispute will ask.

### 16.6 F4 and F10 independently built two overlapping event catalogs

**The finding.** F4's brief (§1's API conventions, and F4's own header: "F4 owns webhook transport;
§12 owns notification content") should have produced a *transport mechanics* section with no event
*names* of its own. Instead, F4's original draft (§6.5) built a full 30-event catalog
(`EVT-400`–`429`) naming essentially the same lifecycle transitions §12's (F10's) 49-event catalog
(`EVT-1000`–`1048`) also names — independently, with different names for several of the same
underlying transitions (F4's single `load.awarded` vs. F10's two-phase `award.determined`/
`award.confirmed`; F4's general `carrier.suspended`/`carrier.reinstated` vs. F10's narrower
`carrier.suspended_in_flight`; F4's `dispute.resolved` vs. F10 having only the unfavourable
`dispute.closed_unresolved`). **Neither agent could see this** — F4 never read F10's file and vice
versa, and both are individually internally consistent.

**§8 (F6), §9 (F7), and §15 (F13) each also independently allocated their own event names** in their
own ID blocks (`EVT-600`–614, `EVT-700`–708, and seven unnumbered names respectively) for auction,
assignment, and vetting-lifecycle transitions — a legitimate use of the "every agent owns its own
block" ID rule, but the same underlying-transition overlap exists there too (F6's `award.accepted`
vs. F10's `award.accepted`/`award.confirmed`; F13's `carrier.suspended`/`carrier.reinstated` vs.
F10's/F4's versions of the same).

**Resolution adopted in this document:** §12 (F10)'s catalog is canonical — it is the most deeply
analysed (tiers, per-persona channel routing, quiet hours, delivery/ack semantics — none of which
F4, F6, F7, or F13 attempted), and it is the section spine explicitly assigns event-catalog ownership
to (§1's ID block table: "F10 | 1000-1099 | Notifications, events, messaging"). F4's `EVT-400`–`429`
IDs are retained (never reused, per §1's rule) but marked **superseded**, with a full mapping table
at §6.5. F6's, F7's, and F13's own event lists are left as-is in their sections (execution-internal
signals, cited but not renumbered) with a note at each pointing to their §12 equivalent where one
exists.

**Genuine gaps this surfaced, not invented, listed once:**

| Gap | Where it showed up | Disposition |
|---|---|---|
| No `case.resolved`-equivalent for `CARGO_INTEGRITY`/`FRAUD_REVIEW`/`CARRIER_ENFORCEMENT_COLLISION` cases | F3's `ExceptionCase` split (§3.3) has a `RESOLVED` terminal state; only `DISPUTE_*`'s unfavourable close (`EVT-1037`) had an event | **Closed** — `EVT-1049 case.resolved` added at §12.1a |
| No general `carrier.reinstated` event in F10's own catalog | F4's superseded `EVT-427` and F13's unnumbered list both name one; F10 (canonical) did not | **Closed** — `EVT-1050 carrier.reinstated` added at §12.1a |
| No plain `carrier.suspended` (as opposed to the specifically in-flight `EVT-1033`) | Same three sections | **Not closed** — F10 never specified tier/channel routing for this case; inventing that table is inventing a decision, not reconciling one. Flagged for the next drafting pass, not added here. |
| `load.amended`, `bid.withdrawn`, `pod.addendum_added`, `invoice.finalised` (F4's superseded `EVT-401/407/414/420`) have no §12 equivalent at all | §6.5's mapping table | **Not closed** — same reasoning; §12's domain owner never specified these as persona-facing notifications, possibly deliberately (a bid withdrawal might be intentionally silent to avoid signalling pool thinness — consistent with §8.6's anti-gaming posture). Flagged, not assumed. |
| §13's (F11's) ten ops-internal events (`case.claimed`, `case.escalated`, `vetting.approved`/etc., `override.executed`, `waiver.approved`, `config.parameter_changed`, `impersonation.started`/`.ended`) have no §12 equivalent | §13.10 | **Not closed** — plausibly correctly out of scope for F10's *notification* catalog (these are audit/ops-console events, not persona notifications), but if `API-482`'s audit log or any ops-side webhook needs to be event-driven, these need `EVT-` IDs eventually. Flagged. |

### 16.7 Orphans carried forward from `BRD-v1.md`, still unresolved at the FRD layer

`BRD-v1.md` §8.12 already names two orphans this document inherits rather than resolves: **BR-106**
(a payment-reliability signal shown to bidders pre-bid — no A6 or A9 requirement, and no FRD
section, ever specifies where that signal is computed or what feeds it; §11's `SCR-908` and `SCR-902`
both render a value for it that has no upstream producer) and **BR-108** (an org with an open
unresolved non-payment dispute cannot publish — resolves loosely to the `DISPUTE_MONEY` `ExceptionCase`
type at §3.3, but no FRD requirement anywhere actually gates `API-403` `publish` on an open case of
that type). Both are flagged, not silently wired up, because doing so would mean inventing the
missing upstream requirement rather than reporting its absence.

### 16.8 One entity/permission tension this document could not fully close

Restated from §3.1: **`Trip` (`ENT-314`) vs. a standalone `Assignment` entity** (F7's original
`ENT-705`). F7's requirement (queryable assignment history independent of Trip's broader state,
substitution logged separately from the award record) is real and not satisfied by F3's current
`Trip` shape. Two live resolutions exist (`assignment_history[]` embedded array, or reinstating
`Assignment` as its own entity) and this document does not pick between them — it is a schema-design
call, not a reconciliation of two agents' stated intent, since neither F3 nor F7 was asked to decide
between those two specific shapes.

---

## 17. Open Decisions Register (`DEC-`)

Every `DEC-` tag across all thirteen parts, gathered in one place. Rival-bid visibility (`DEC-302`/
`303`) is flagged **build-blocking** per §16.1 and should be resolved first; the rest are ordered by
section, not priority.

| DEC | Section | Question | Options | Status |
|---|---|---|---|---|
| DEC-100 | §5.4 | Driver primary credential | Phone+OTP / email+password+phone-fallback / phone-first+device-bound | `[NEEDS INPUT]` |
| DEC-101 | §5.4 | SSO default | SP-initiated only / also IdP-initiated | `[NEEDS INPUT]` |
| DEC-201 | §15.6 | Vetting rigour tier | A (uniform high bar) / B (light-to-bid, heavy-to-win) / C (baseline + tiered review) | `[NEEDS INPUT]` — also gates §13's FR-1145 |
| DEC-302 | §8.7 | Bid visibility mode | OPEN / SEALED | **`[NEEDS INPUT]` — build-blocking, §16.1** |
| DEC-303 | §8.7 | Price disclosure mode | STANDING_BEST / RANK_ONLY | **`[NEEDS INPUT]` — build-blocking, §16.1; F2's finding removes STANDING_BEST-as-live-flag as a viable combination with SEALED (§16.1)** |
| DEC-304 | §8.7 | Auction duration | Fixed / shipper-set | `[NEEDS INPUT]` |
| DEC-305 | §8.7 | Anti-snipe extension | Params | `[NEEDS INPUT]` |
| DEC-306 | §8.7 | Ceiling price / disclosure | Value + bool | `[NEEDS INPUT]` |
| DEC-307 | §8.7 | Shipper decline right | NONE / STRUCTURED_REASON_REQUIRED | `[NEEDS INPUT]` — Boss decision pending |
| DEC-308 | §8.7 | Early close allowed | bool | `[NEEDS INPUT]` |
| DEC-309 | §8.7 | Award failure mode | CASCADE / RE_AUCTION | `[NEEDS INPUT]` |
| DEC-310 | §8.8 | Thin-market mode | AWARD_ANYWAY / EXTEND_AND_REOPEN / CEILING_TEST_ONLY / FALLBACK_POSTED_RATE / ESCALATE_TO_OPS_DESK | `[NEEDS INPUT]` — no default; F6 refuses to pick |
| DEC-311 | §8.7 | Minimum bid decrement | Value | `[NEEDS INPUT]` |
| DEC-312 | §8.7 | Close calendar | ANY_TIME / BUSINESS_HOURS_ONLY / PAUSE_WEEKENDS | `[NEEDS INPUT]` |
| DEC-330 | §3.2 | Superseded-load lineage visible to bidders | Transparent vs. opaque | `[NEEDS INPUT]` |
| DEC-331 | §3.2 | Legal-hold release authority | Same individual / any ops-role / second approver | `[NEEDS INPUT]` |
| DEC-332 | §3.2 | Human reference number format/charset/checksum | — | `[NEEDS INPUT]` — Boss/§6 call |
| DEC-700 | §9.6 | HOS feature scope | A (none) / B (bounded feasibility signal) / C (full system of record — refused absent explicit override) | `[NEEDS INPUT]` — one of F7's "three sharpest questions" |
| DEC-701 | §9.6 | HOS input source (if B) | Self-report / dispatcher-report / optional ELD read | `[NEEDS INPUT]` |
| DEC-800 | §10.10 | Shipper default location granularity | (A) exact pin / (B) corridor-only default, opt-in exact / (C) contract-tier | F8 recommends (B) — already §4.4's default |
| DEC-801 | §10.10 | Location retention posture | (A) flat / (B) tiered / (C) carrier-configurable | F8 recommends (B) |
| DEC-802 | §10.10 | Manual-only dwell as billable detention evidence | (A) never / (B) lower-confidence with review / (C) full confidence | A6/Boss decision |
| DEC-1200 | §14.5 | `retained-restricted` disclosure model | (a) name legal basis / (b) confirm-receipt-only / (c) silent partial deletion | Needs counsel + product |
| DEC-1300 | §15.4 | Re-verification cadence mechanism | A (real-time) / B (periodic batch) / C (on-demand at award) | `[NEEDS INPUT]` |
| DEC-1301 | §15.4 | Staleness threshold per signal | — | `[NEEDS INPUT]` |
| DEC-1302 | §15.4 | Mixed cadence, final per-signal selection | — | `[NEEDS INPUT]` |
| DEC-LOCK-001 | §1 | Award rule | Lowest bid within eligibility gate | **Locked** — Boss, 2026-07-29 |
| DEC-LOCK-002 | §1 | Platform's own data assets in scope | ODbL Produced-Works-only boundary | **Locked** — Boss, 2026-07-29 |

**Total: 46 distinct open `DEC-` tags** across the thirteen parts (grep-deduplicated per file, per
`frd-assembly-report.md`'s methodology note), of which **two are build-blocking** (`DEC-302`/`303`,
§16.1) and the rest are feature-shape or numeric-threshold decisions that can proceed in parallel
with build once acknowledged as open.

---

## 18. `[NEEDS INPUT]` — summary, not a re-listing

Every `[NEEDS INPUT]` tag from all thirteen source parts is preserved verbatim in its own section
above — **none promoted to a default, none invented.** Counting occurrences of the literal tag
string per source file (not unique topics — several rows share a tag, e.g. multiple retention
periods all tagged `[NEEDS INPUT]` independently):

| Section | File | Count |
|---|---|---|
| §5 | F1 | 14 |
| §6 | F4 | 11 |
| §7 | F5 | 23 |
| §8 | F6 | 30 |
| §9 | F7 | 8 |
| §10 | F8 | 17 |
| §11 | F9 | 3 |
| §12 | F10 | 13 |
| §13 | F11 | 14 |
| §14 | F12 | 21 |
| §15 | F13 | 9 |
| §4 (F2) | F2 | 10 |
| §3 (F3) | F3 | 6 |
| **Total** | | **179** |

**The single most consequential cluster:** every numeric value governing money, timing, or
retention across the entire system — bid decrement, auction duration, acceptance windows, retention
periods, staleness thresholds, rate limits, SLA targets — is untagged by design, per §1's rule 2.
This is not a gap in drafting; it is thirteen agents and one assembler collectively refusing to
invent a number Boss did not supply, exactly as instructed.

---

## 19. Traceability, Orphans, and Closing Note

### 19.1 Trace coverage

Every `FR-`/`API-`/`ERR-`/`PERM-` in this document traces to a `BR-`/`OBJ-` in `BRD-v1.md`, or is
explicitly marked `derived` (a reasonable implication of a BR, not independently sourced) or
`[ASSUMPTION: … | conf: …]` per §1's inherited rules. **Two orphans found and not silently
resolved** (§16.7): BR-106 (payment-reliability signal with no computing requirement anywhere) and
BR-108 (dispute-gates-publish with no FRD requirement enforcing it). Both were already flagged as
orphans in `BRD-v1.md` §8.12 at the BRD assembly stage; this FRD assembly confirms neither was
closed by any of the thirteen FRD parts, and does not close them here either.

### 19.2 What this document is not

It does not self-score. It does not resolve `DEC-302`/`303` (§16.1), `DEC-201` (§15.6),
`DEC-700`/`701` (§9.6), or any of §17's other 43 open decisions. It does not invent a single number.
It does not silently drop F2's word-budget overage, F7's two BRD defects, or the event-catalog
duplication (§16.6) — all three are reported, not fixed by fiat. It does not fully resolve the
`Trip`-vs-`Assignment` schema tension (§16.8, §3.1) because that is a build-time call neither source
agent was asked to make.

### 19.3 The single worst structural problem remaining

**The event-catalog duplication (§16.6).** Not because any individual event definition is wrong —
every one of F4's, F6's, F7's, F10's, and F13's event tables is internally coherent — but because
five agents each holding a legitimate ID block independently decided to *name the same underlying
business transitions*, and nothing in the spine's ID-allocation rule ("every agent owns its own
block") prevented that, because the rule addresses collision, not duplication. A build team handed
all thirteen source files without this assembly would plausibly wire two notification systems (or
worse, two independently-triggered webhook deliveries) for one `load.awarded` moment. This assembly
adopted §12's catalog as canonical and mapped the rest, but the underlying spine gap — no rule
saying *only one agent may name a given business event* — is not fixed by this document; it would
recur on the next FRD phase unless the spine itself gets a fifth rule about event-name ownership.

### 19.4 What no individual agent could have seen — full list

1. F3's and F7's independent, duplicate modelling of Tractor/Trailer/Pairing under two different ID
   sets (§3.1).
2. F6's and F13's two different `eligibility()` call signatures for the one function every
   downstream section depends on (§16.3).
3. F4's and F10's two overlapping event-name catalogs for the same lifecycle (§16.6) — the single
   largest duplication in the document by row count (30 vs. 49 events, ~25 of the 30 near-duplicate).
4. F2's matrix needing three roles (`PLATFORM_SENIOR_REVIEWER`, `PLATFORM_CONFIG_ADMIN`, and a
   corrected `PLATFORM_EXCEPTION_DESK` scope) that only became visible once F6's, F11's, and F13's
   requirements were read against F2's actual row set (§4.1).
5. F13's own text referencing a `PERM-1300` — an ID in F2's block, written from F13's block, which
   only a cross-file ID audit at assembly time could catch (§15.8).
6. BR-214's own acceptance test (an overlapping-window commitment check) requiring a windowed
   `AvailabilityWindow` entity that neither F3's status-enum model nor F7's duplicate-entity model
   fully satisfied on its own (§3.1.2).

Individually, every one of the thirteen parts is high-quality, internally consistent work. All six
items above are true only in the union of two or more files — which is exactly the job an assembler
exists to do, and exactly why one agent seeing only its own 2,500-word block, however carefully, was
never going to catch them.

---

*End of FRD-v1. Companion document: `frd-assembly-report.md` — per-propagation detail, full count
methodology, and the record of every conflict logged above.*
