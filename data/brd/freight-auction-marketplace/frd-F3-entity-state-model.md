# F3 — Entity Model, State Machines, Audit & Provenance

**Block 300-399. Inherits spine §2/§3, DECISIONS.md.** F3 defines entity shape, fields, relationships, state, mutability — including Tractor/Trailer/Equipment Type. F7 owns matching/HOS logic; F2 permissions; F4 the API; F5 error codes (referenced, not defined).

## 1. Entity catalog

Every row belongs to one Organization (spine §2) via a direct/inherited `org_id`, except Document (polymorphic) and Notification (system). All PKs opaque (§10).

| ID | Entity | Core fields & relationships | Trace |
|---|---|---|---|
| ENT-300 | Organization | org_type(SHIPPER\|CARRIER\|PLATFORM), broker_flag, verification_status, standing_status | BR-100/203 |
| ENT-301 | User | org_id, contact, role_set(→F2), account_type(STANDARD\|DRIVER) | BR-900/901 |
| ENT-302 | Driver | 1:1 User ext.: cdl_number/class/state/status, clearinghouse_attestation(status only, never raw result), employment_type | BR-210/707/709/903 |
| ENT-303 | Tractor | carrier_org_id, VIN, plate, status(AVAILABLE\|COMMITTED\|OUT_OF_SERVICE\|MAINTENANCE), authority_ref, insurance_doc_ref | BR-209/214/215 |
| ENT-304 | Trailer | carrier_org_id, unit_no, equipment_type_id(FK 306), status(AVAILABLE\|COMMITTED\|DROPPED\|OUT_OF_SERVICE), insurance_doc_ref. No FK to a tractor — pairing is separate (ENT-305), so an unattached dropped trailer is normal | Boss scope §1 |
| ENT-305 | Tractor-Trailer Pairing | tractor_id, trailer_id, valid_from, valid_to(null=current). No successor after valid_to ⇒ "dropped" | Boss scope §1; BR-214 |
| ENT-306 | Equipment Type | code(DRY_VAN\|REEFER\|FLATBED\|STEP_DECK\|TANKER\|POWER_ONLY\|… open set), temp_range_required, attribute_set(json). Reference table, not an asset | BR-111/112 |
| ENT-307 | Load/Shipment | shipper_org_id, posting_user_id, lifecycle_state(§3), site_from/to, current_declaration_id(FK 308), supersedes_load_id(nullable, §2), legal_hold(bool, §7) | BR-100-156 |
| ENT-308 | Declaration Snapshot | load_id, version_no, content(commodity, weight, equipment_type, dimensions, hazmat_flag, declared_value, appointment windows, addresses), immutable, superseded_by | BR-121/122/136 — §2 |
| ENT-309 | Auction | load_id, declaration_snapshot_id(frozen at open), opens_at, closes_at, state(§3), pool_size, bid_count | BR-301-318 |
| ENT-310 | Bid | auction_id, carrier_org_id, tractor_id, trailer_id, driver_id(optional), price, submitted_at, withdrawn_at, gate_result_ref, status(ACTIVE\|WITHDRAWN\|EXCLUDED\|WINNING) | BR-301/304/307/308 |
| ENT-311 | Award | auction_id, winning_bid_id, awarded_org_id, state(§3), selection_record_id(FK 312) | BR-303/304 |
| ENT-312 | Selection Record | award_id, gate_version, every_bid[](id, price, gate_result), excluded[](bidder_id, reason), authority/insurance/safety_snapshot_refs, decided_by. Append-only, never updated post-creation | BR-303/706/802-retired |
| ENT-313 | Rate Confirmation | award_id, base_linehaul_rate, fsc_method_ref, accessorial_table_ref, carrier_acknowledged_at | BR-600 |
| ENT-314 | Trip | award_id, load_id, assigned_driver/tractor/trailer_id, state (fulfilment sub-states), current_custody_holder. Spans every leg of one shipment — relay/transload/RTO included, not one Trip per truck | BR-212/910 |
| ENT-315 | Custody Event | trip_id, event_type(TENDER_PICKUP\|TRANSLOAD\|DELIVERY\|RETURN_TO_ORIGIN), prev_event_id, from/to_holder, condition_notes_ref, acknowledged_by[](name+role only, for the consignee), observed_at, recorded_at (§6). Append-only, chained | BR-400/402/403; spine §3 |
| ENT-316 | Bill of Lading | load_id, trip_id, origin_capture(count, weight, condition, seal, dual signature, both timestamps), delivery_capture(clear\|exception, OS&D notation[], signer name/role, both timestamps — null until drop), addenda[], concealed_damage_reports[]. One entity, two stages — see CHALLENGE | BR-500-514 |
| ENT-317 | Invoice | load_id, rate_confirmation_id, revenue_model(A\|B\|C). Header status is a computed rollup of its lines (§4), never hand-set | BR-600/601/614 |
| ENT-318 | Invoice Line | invoice_id, line_type(LINEHAUL\|FSC\|DETENTION\|TONU\|LUMPER\|OSD_DEDUCTION\|…), amount, evidence_ref, status(ISSUED\|HELD\|FINALISED\|CREDITED), held_reason_ref, credit_note_ref. `INVOICE_ISSUED`→`INVOICE_FINALISED` lives here, line-grain not header-grain (BR-603) | BR-601-604 |
| ENT-319 | Claim | load_id, bol_id, type(CARGO_LOSS\|DAMAGE\|SHORTAGE\|TONU\|DETENTION…), filed_at, amount_asserted, status(FILED\|ACKNOWLEDGED\|DECLINED\|SETTLED), disallowance_notice_ref, next_obligation_due_at. Detail body of an ExceptionCase (324), case_type=CARGO_CLAIM | BR-807-809/821 |
| ENT-320 | Dispute | subject_type(FREIGHT\|MONEY), related_ref(claim/invoice_line), raised_by, status(OPEN\|CLOSED_UNRESOLVED\|RESOLVED), evidence_owner. Detail body of an ExceptionCase, case_type=DISPUTE_FREIGHT\|MONEY | BR-811 |
| ENT-321 | Document | owner_type(ORG\|DRIVER\|TRACTOR\|TRAILER), owner_id, doc_type(AUTHORITY\|COI\|CDL\|PERMIT\|W9\|NOA…), issuer, expires_at, verification_status/source. New verification appends, old row never overwritten | BR-204/209/606/612 |
| ENT-322 | Rating | load_id(completed only), rater_org_id, ratee_org_id, objective_event_refs[], stars(gated, DEC-330) | BR-815/816 |
| ENT-323 | Notification | event_ref, recipient_type(USER\|OUT_OF_BAND_CONSIGNEE), channel, delivery_status(SENT\|UNKNOWN out-of-band). Stub, catalog owned by F10 | BR-912 |
| ENT-324 | Exception Case | load_id(FK, not unique — many cases per Load), case_type(FRAUD_REVIEW\|CARGO_INTEGRITY\|CARGO_CLAIM\|DISPUTE_FREIGHT\|DISPUTE_MONEY\|CARRIER_ENFORCEMENT_COLLISION), status(OPEN\|IN_REVIEW\|RECOVERY_IN_PROGRESS\|RESOLVED\|CLOSED_UNRESOLVED), owner_role, opened_at, closed_at, detail_ref(FK→Claim/Dispute), evidence_refs[]. §3.1 | F11 challenge |

**CHALLENGE:** spine §2 lists `Bill of Lading` and `Delivery receipt (POD)` as two entities. BR-514 requires "one continuous, linked document chain, not two independent records." ENT-316 merges them: POD is the delivery-signed state of the same document, not a sibling row. Row count only, no field content lost.

## 2. Declaration snapshot — versioning and lineage

**FR-330** One *current* declaration per Load; each pre-first-bid edit creates a new immutable version, superseding the prior (BR-135). **FR-331** Once ≥1 bid exists, the referenced snapshot is frozen forever; no new version attaches (BR-136). **FR-332** A material post-first-bid change executes as `Load.supersedes_load_id → new Load, new Auction, new first snapshot` (withdraw-and-republish) — never a version bump — so every bid stays comparable against one immutable snapshot. **FR-333** Non-material fields (contact, dock instruction, gate code) live on `Load` directly, outside the snapshot, mutable through `AWARD_ACCEPTED` (BR-137). **FR-334** The withdrawn Load remains queryable via `supersedes_load_id` (BR-138).

## 3. Consolidated state machine

Inherited verbatim from spine §3 / BRD §7.4; owning domain per BRD, not repeated per row. Adds Trigger and Terminal.

| State | Enters from | Trigger | Terminal |
|---|---|---|---|
| DRAFT→PUBLISHED | Shipper action | Shipper | N |
| AUCTION_OPEN | PUBLISHED | System (schedule) | N |
| AUCTION_EXTENDED | AUCTION_OPEN | System (anti-snipe/thin-market) | N |
| AUCTION_CLOSED | Close/early-close | System/Shipper | N |
| AUCTION_FAILED_NO_BIDS | AUCTION_CLOSED | System | Y unless re-auction |
| AUCTION_FAILED_NO_ELIGIBLE_CARRIER | AUCTION_OPEN | System | Y |
| AUCTION_FAILED_ALL_ABOVE_LIMIT | AUCTION_CLOSED | System | Y unless re-auction |
| AWARD_PENDING | Winner determined | System (gate re-verify) | N |
| AWARD_VOIDED_INELIGIBLE | AWARD_PENDING | System (gate fail) | Y (new Award cycle) |
| AWARDED→AWARD_ACCEPTED | AWARD_PENDING | Carrier | N |
| AWARD_DECLINED/AWARD_LAPSED | AWARDED | Carrier/timer | Y (cascade restarts) |
| PICKUP_SCHEDULED→AT_PICKUP | AWARD_ACCEPTED | Carrier/driver | N |
| SHIPPER_NOT_READY | AT_PICKUP | System (on-time arrival, freight not ready) | N |
| CARRIER_NO_SHOW | PICKUP_SCHEDULED | System (timer) | N |
| PICKUP_REFUSED | AT_PICKUP | Driver/shipper | N (→RTO) |
| PICKED_UP→IN_TRANSIT | AT_PICKUP | System (BOL capture) | N |
| TRANSIT_EXCEPTION | IN_TRANSIT | Driver/system | N |
| AT_DROP→DELIVERED | IN_TRANSIT | Driver/consignee | N |
| DELIVERY_ATTEMPTED_NO_RECEIVER | AT_DROP | Driver | N |
| DELIVERY_REFUSED | AT_DROP | Consignee | N (→RTO) |
| PARTIAL_DELIVERY | AT_DROP | Consignee (custody fork) | N |
| RETURN_TO_ORIGIN | Post-refusal | Carrier/shipper | Y |
| POD_CAPTURED→…→COMPLETED | DELIVERED | System (rollup, §4) | Y (COMPLETED) |
| CANCELLED_BY_SHIPPER | Any pre-pickup; post-pickup w/ consequences | Shipper | Y |

**OS&D is not a state** (BRD §7.4) — a structured notation on ENT-316's delivery_capture, attachable to `DELIVERED`, `PARTIAL_DELIVERY`, or `DELIVERY_REFUSED`.

### 3.1 State vs case — F11's challenge, accepted

**Problem:** a single-valued `Load.lifecycle_state` can't hold two open exceptions at once (fraud review + detention dispute, different owners/evidence/timelines). **Accepted.** `ExceptionCase` (ENT-324): `load_id` non-unique, N cases open per load, each with its own status/owner/audit trail (§4).

**Test:** a *state* is a mutually-exclusive condition of the load's one thread; a *case* is work opened **about** the load, coexisting with any state or other case.

| Removed from §3 | case_type | Why a case, not a state |
|---|---|---|
| `DISPUTED`/`CLOSED_UNRESOLVED` | DISPUTE_FREIGHT\|MONEY | A5's OS&D precedent again — content about the load; detail in Dispute (ENT-320) |
| `CLAIM_OPEN` | CARGO_CLAIM | Already had its own entity/status (ENT-319) — never truly single-valued |
| `FRAUD_SUSPECTED`/`RECOVERY` | FRAUD_REVIEW | Spine's own text: "distinct from a closed LOST" is a status change *inside* one case |
| `DAMAGED`/`LOST`/`PILFERED` | CARGO_INTEGRITY | A fact discovered about freight, worked independently of the load's own execution state |
| `CARRIER_SUSPENDED_IN_FLIGHT` | CARRIER_ENFORCEMENT_COLLISION | F11's sharpest one — a party-level action (`Organization.status→SUSPENDED`), not a load fact; opens when a Trip is bound to the newly-suspended org |

Kept as states: every row remaining in §3 — each a momentary branch on one thread, not parallel work.

**FR-351** Opening/progressing/closing an `ExceptionCase` never mutates `Load.lifecycle_state`; cases don't block each other. **Downstream:** F10 adds `case.opened`/`status_changed`/`closed` events, replacing `load.state_changed` for the removed rows. F11's ops queue reads `ExceptionCase`, not `Load.lifecycle_state`. F5 gets a smaller Load-transition set plus a new ExceptionCase set. F6 unaffected.

**FR-335** Every transition is validated server-side against this table before persistence; a `(from, trigger, to)` tuple not present is rejected, never partially applied. **FR-336** A rejected attempt is itself logged (attempted_from/to, actor, reason) — illegal transitions are evidence, not silence. **FR-337** F5 owns the error taxonomy; F3 guarantees each row above has exactly one corresponding failure condition.

## 4. Custody, audit and mutability classes

Liability follows custody (spine §3); custody is `Custody Event` (ENT-315), never a status field. Every entity falls into one class:

| Class | Entities | Rule |
|---|---|---|
| Immutable on creation | Declaration Snapshot, Selection Record, Custody Event, BOL capture stages, StateTransitionLog | No UPDATE/DELETE; a correction is a new linked row |
| Append-only ledger | Audit Log, BOL addenda, Document verification history | Grows only; read as a timeline |
| Mutable, logged history | Load, Auction, Bid, Award, Trip, Invoice Line, Claim, Dispute, ExceptionCase | Current value mutable; every change also lands in StateTransitionLog |

**FR-338** Every create/amend/cancel/override records the acting user (or `SYSTEM`) and both timestamps (BR-102) in an append-only Audit Log. **FR-339** `StateTransitionLog(entity_type, entity_id, from_state, to_state, trigger_actor, reason, occurred_at, recorded_at)` is the single mechanism satisfying BR-102 across every FSM, Load and ExceptionCase alike.

## 5. Selection record — the evidentiary artifact

**FR-340** ENT-312 generates once, at `AWARD_PENDING`, from data frozen at that instant — never a live pointer to rows that can later change. **FR-341** A later fraud finding attaches as a new linked annotation (via its ExceptionCase, §3.1) referencing the record by ID; the record itself is never edited — it is the *Montgomery* exhibit. **FR-342** Every exclusion/override (BR-306) carries a reason sourced from the same frozen snapshot.

## 6. Temporal semantics — observed_at vs recorded_at

**FR-343** Custody Event, BOL captures, transit status updates/exceptions, and Claim filing carry two independent timestamps — `observed_at` (true in the world) and `recorded_at` (captured) — never one collapsed field. `recorded_at` is never validated against `observed_at`; a late report can legitimately show `observed_at` earlier than another row's `recorded_at` — clock skew across actors is expected, not an error. Detention/TONU math and Carmack's clocks run on `observed_at`. **FR-344** Where the variance exceeds a threshold `[NEEDS INPUT]`, the record carries a late-report flag rather than silently accepting the value.

## 7. Soft delete, retention, legal hold

**FR-345** Immutable/evidentiary classes (§4) are never deletable under any operating mode. **FR-346** Mutable operational entities (User, Document, Tractor, Trailer) soft-delete via `deleted_at`; the row stays FK-resolvable so a historical Custody Event signed by a since-deactivated User still resolves a display identity. **FR-347** `legal_hold`(bool, platform-ops only) lives on `Load`, cascades read-only to every child (Trip, Custody Event, BOL, Invoice, Claim, Dispute, Selection Record, ExceptionCase); while set, purge skips the subtree regardless of `retention_expires_at`. **FR-348** Retention *periods* are F12's numeric call per data class (several `Open` in BRD §8.7); F3 owns the mechanism only — `retention_expires_at`, an audited purge job (actor/criteria/row count), and the hold override.

## 8. Identifier strategy

**FR-349** Every PK is opaque, non-sequential — never a monotonic integer — closing the enumeration risk F2 flags (no volume inference, no scraping sequential loads/bids). **FR-350** A human-readable reference number exists on Load, Award, and Invoice only — what a person reads over a phone — generated at the transition first making the entity externally referenceable (PUBLISHED, AWARD_ACCEPTED, INVOICE_ISSUED). Never the join key; format/length/checksum `[NEEDS INPUT]`; not globally sequential — same enumeration risk, so a per-org or salted scheme is required.

## 9. Edge-case register (EC-350 — EC-371)

| ID | Trigger | Behaviour | Who decides | Unresolved? |
|---|---|---|---|---|
| EC-350 | Transition absent from §3's table | Rejected, logged (FR-336) | System | No |
| EC-351 | Two posting users edit same pre-bid Load concurrently | Optimistic concurrency on `current_declaration_id` | System | UX → F9 |
| EC-352 | Amendment attempted on a snapshot already bid against | Blocked; withdraw-and-republish only (FR-332) | System | No |
| EC-353 | `AUCTION_EXTENDED` fires | `declaration_snapshot_id` pinned; extension changes `closes_at` only | System | No |
| EC-354 | Duplicate Custody Event (retry/offline sync) | De-duplicated via idempotency key (F4); no-op | System | Dedup window → F4 |
| EC-355 | Trailer swapped mid-trip, pairing not recorded | No mechanism forces the record; next Custody Event surfaces mismatch | Platform ops | Yes |
| EC-356 | Insurance Document expires at the instant a gate check runs | Inclusive/exclusive boundary undefined | A2/counsel | Yes `[NEEDS INPUT]` |
| EC-357 | `RETURN_TO_ORIGIN` after refusal | Same Trip continues; RTO is a new Custody Event, not a new Trip | System | No |
| EC-358 | `AWARD_VOIDED_INELIGIBLE` after Trip/Rate Confirmation exists | Can't happen — both gated strictly on `AWARD_ACCEPTED` | System | No |
| EC-359 | `CARRIER_SUSPENDED_IN_FLIGHT` mid-Trip | Suspended org keeps write access to its own Custody Events; new-bid/award only is cut | Platform ops | No |
| EC-360 | Consignee (no account) signs delivery capture | `acknowledged_by` accepts name/role-only, no `user_id` | System | No |
| EC-361 | Fraud finding against an already-frozen Selection Record | New linked annotation on the ExceptionCase; record itself untouched (FR-341) | A8/ops | No |
| EC-362 | Out-of-order sync (recorded_at earlier than a prior row's observed_at) | Both values stored as given; no forced reordering (§6) | System | No |
| EC-363 | Short-pay against an already-`FINALISED` line, or a held dispute resolving post-rollup | New `CREDITED` line/credit-note; original line/header never reopened (§1 ENT-317/318) | System | No |
| EC-364 | Legal hold set after retention window already lapsed / hold released | Purge re-checks hold every run; release needs same ops-role tier, reason logged | Platform ops | Release-tier rule → Boss |
| EC-365 | Soft-deleted User referenced by a historical Custody Event | FK resolves to a frozen display name at event time | System (FR-346) | No |
| EC-366 | Human reference requested pre-`PUBLISHED`, or two orgs merge with colliding sequences | Not generated pre-publish; no merge-renumbering mechanism defined | Platform ops | Merge case: Yes |
| EC-367 | Auction re-opens after `AUCTION_FAILED_NO_BIDS` | New Auction, same frozen snapshot unless a material re-declaration also triggers (FR-332 first) | System | No |
| EC-368 | Trip spans a relay (driver/tractor swap, same carrier) | New Custody Event; `Trip.assigned_*` updates, prior binding preserved in StateTransitionLog | System | No |
| EC-369 | Rating submitted before shipment reaches a completed state | Rejected — BR-815 gates on completed shipment | System | No |
| EC-370 | Notification for a state with no consignee contact on file | Channel skipped; `UNKNOWN`, never a false-sent status | System (F10) | No |
| EC-371 | Two `ExceptionCase`s open on one Load concurrently (e.g. FRAUD_REVIEW + DISPUTE_MONEY) | Both persist independently; neither's status touches the other or `Load.lifecycle_state` (§3.1) | System | No |

## 10. Open decisions

**DEC-330** `[NEEDS INPUT]` Superseded Load lineage visible to bidders on re-listing, or opaque — transparency vs. leak, no default. **DEC-331** `[NEEDS INPUT]` Legal-hold release: same individual, any ops-role member, or second approver. **DEC-332** `[NEEDS INPUT]` Human reference format/charset/checksum — Boss/F4 call.
