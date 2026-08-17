# FRD Part F8 — Tracking, Telematics, ETA, Geofencing, Location Privacy

**Owns:** position ingestion · milestones · ETA · geofencing · dwell/detention detection · location
retention & privacy. **Not owned here:** permission rows (→F2) · error codes (→F5) · API envelope
(→F4) · screens (→F9) · HOS record (→F7) · detention *rate*/invoicing (→BR-524/A6) · entities (→F3).

## 0. Principles

Three position sources, none guaranteed: ELD/telematics (carrier-controlled, refusable), driver mobile
app (best fidelity, needs cooperation + signal), phone call to ops (manual). System must work with any
one, a mix, or none — "dark" is first-class and visible (BR-401), never silently read as "on schedule."
Milestones outrank raw pings. A milestone is **derived** (system-inferred from position) or **claimed**
(asserted by a human act — BR-400's pickup record, A5's POD signature); never merged, since detention
pay and Carmack claims hang on which kind a timestamp is. Location is the **driver's** personal
location, not the account holder's — collection is trip-scoped and minimised by default.

## 1. Position ingestion & degraded mode

| ID | Requirement | MoSCoW | Traces |
|---|---|---|---|
| FR-800 | Accept position data from three independent capability classes (ELD feed, driver app, manual entry) as alternatives, never a mandatory stack. | Must | OBJ-002/004 |
| FR-801 | Every position record carries `source_type` (ELD/MOBILE_APP/MANUAL) and a `confidence_tier`; sources never blend into one unlabelled "position." | Must | OBJ-004/006 |
| FR-802 | Declining ELD/telematics never blocks the shipment; sets a `tracking_capability` flag at dispatch instead. | Must | OBJ-002 |
| FR-803 | No update within `[NEEDS INPUT: reporting interval]` while `IN_TRANSIT` → visible `NO_UPDATE_RECEIVED` state; last-known display stays age-labelled, never current. | Must | OBJ-002/006 — realises BR-401 |
| FR-804 | No position source at all → `TRACKING_UNAVAILABLE` from dispatch, distinct from `NO_UPDATE_RECEIVED`. | Must | OBJ-006 — small-carrier honest baseline, BRD A4 |
| FR-805 | Manual updates use a bounded milestone/exception vocabulary plus free text, entered by an authenticated ops user; always visibly `MANUAL`. | Must | OBJ-004/006 |
| FR-806 | Source-type switches mid-trip are accepted without gap-filling fabricated positions for the uncovered interval. | Must | OBJ-006 |
| FR-807 | Repeated `NO_UPDATE_RECEIVED` beyond `[NEEDS INPUT]` feeds carrier scoring (realises BR-409), not scored here. | Could | OBJ-006 |
| FR-808 | A driver's personal device/number is never the *only* compliance path; manual entry stays a fallback. | Must | OBJ-007 |

## 2. Milestones — derived vs claimed

Six per custody leg: arrived/loaded/departed at pickup, arrived/unloaded/departed at drop.
`arrived`/`departed` are **derived** from geofencing (§3). `loaded`/`unloaded` are **claimed** — BR-400's
pickup record and A5's POD signature, human acts F8 consumes, not re-invents; F8 attaches corroborating
(or contradicting) position evidence, never overwrites the business record.

| ID | Requirement | MoSCoW | Traces |
|---|---|---|---|
| FR-809 | `arrived_at_facility`/`departed_facility` derive exclusively from geofence enter/exit (§3), each carrying its producing position record(s). | Must | OBJ-004 |
| FR-810 | `loaded`/`unloaded` source from BR-400's pickup record and A5's POD event; F8 consumes, does not generate, the claim. | Must | OBJ-004 |
| FR-811 | Every claimed milestone gets a `corroboration_status`: `CORROBORATED` (device inside the geofence within a defined window of the claim), `UNCORROBORATED` (no match, source exists), `NO_POSITION_DATA` (no source). | Must | OBJ-004/006 |
| FR-812 | `UNCORROBORATED` never auto-labels a claim "fraud" or blocks it; it routes to ops/claims review only. | Must | OBJ-006 — →A8 if pattern repeats |
| FR-813 | Milestone records are immutable; a correction is a new, linked record with a reason, never an in-place edit. | Must | OBJ-004/006 |
| FR-814 | Full milestone sequence, including gaps, is queryable as one ordered timeline. | Must | OBJ-002/004 |
| FR-815 | Out-of-order milestones (e.g. `departed` recorded before `arrived`) raise a data-quality flag, never silently reorder. | Should | OBJ-006 — see §5 |
| FR-816 | Mid-trip relay/transload (BR-402) opens a fresh milestone set for the new leg; the prior leg closes untouched, and carries the matched geofence polygon (not just facility name) where an address serves multiple docks. | Must | OBJ-004/006 |

## 3. Geofencing and dwell/detention

| ID | Requirement | MoSCoW | Traces |
|---|---|---|---|
| FR-818 | Every pickup/drop stop has a facility geofence polygon sourced from the load's declared location (→F1/F3); radius/shape defaults `[NEEDS INPUT]`. No geofence → claimed-only milestones. | Must | OBJ-004 |
| FR-819 | Entry/exit requires sustained presence across `[NEEDS INPUT: debounce window]`, not one ping, suppressing edge-of-polygon flicker. | Must | OBJ-006 |
| FR-820 | A `DwellSession` opens on entry, closes on exit, holding start, end, and every contributing position record. | Must | OBJ-004/005 |
| FR-821 | Dwell minus `[NEEDS INPUT: free-time hours]` (rate owned by BR-524/A6) is exposed as `detention_candidate_minutes`; F8 emits evidence only, never bills. | Must | OBJ-005 |
| FR-822 | A `detention_candidate` on a manual-only trip is still constructible from claimed timestamps (BR-403/BR-515), tagged `MANUAL` tier, never blocked — small carriers may only phone in. | Must | OBJ-005/006 — DEC-802 |
| FR-823 | A truck proximate but outside the polygon beyond `[NEEDS INPUT]` surfaces `PROXIMATE_NOT_GEOFENCED`, not silent exclusion from dwell. | Should | OBJ-005/006 |
| FR-824 | Early arrival still opens a `DwellSession`; whether pre-appointment dwell counts toward detention is A1/A6 policy. | Should | OBJ-005 |
| FR-825 | GPS-degraded oscillation is smoothed by FR-819's debounce; unresolved oscillation beyond `[NEEDS INPUT]` downgrades confidence rather than averaging the noise away. | Should | OBJ-006 |

## 4. ETA

| ID | Requirement | MoSCoW | Traces |
|---|---|---|---|
| FR-826 | ETA computes from last known position (or last milestone), remaining truck-legal route time (→A11 BR-1100), and any attached work-zone/weather/chain-control event (→A11 BR-1107) — capabilities, not vendors. | Must | OBJ-002/004 |
| FR-827 | Where the route/event feed's geography doesn't cover the corridor, ETA states coverage absent — never "no incident = clear." Work zones AZ/KS/MN/WA only; chain controls CA-only, licence `Unverified` — must not surface per BR-1107 until confirmed. | Must | OBJ-006 |
| FR-828 | ETA recomputes on every new ping, milestone transition, `TRANSIT_EXCEPTION`, and on a `[NEEDS INPUT: recompute interval]` schedule when dark. | Must | OBJ-002/004 |
| FR-829 | ETA older than `[NEEDS INPUT: staleness threshold]` since last recompute is marked `STALE`, stays visibly timestamped. | Must | OBJ-006 |
| FR-830 | ETA is presented as a confidence tier (HIGH = live within interval; MEDIUM = manual/scheduled only; LOW/UNKNOWN = dark), never a bare timestamp implying precision the inputs lack. | Must | OBJ-004/006 |
| FR-831 | An open `TRANSIT_EXCEPTION` is carried as an explicit ETA factor, never a silent widening with no stated cause. | Must | OBJ-004/006 — →A4 BR-405 |
| FR-832 | ETA may consume remaining drive-time as a feasibility input (→F7 HOS signal) but never becomes a compliance record of hours. | Should | OBJ-002 |
| FR-833 | ETA is read/derived only; never blocks a state transition — distinct from A11's pre-bid route-feasibility gate. | Must | boundary |

## 5. Temporal honesty

| ID | Requirement | MoSCoW | Traces |
|---|---|---|---|
| FR-834 | Every position/milestone record carries `observed_at` (when true) and `received_at` (when ingested), never collapsed into one field. | Must | OBJ-004/006 |
| FR-835 | `received_at − observed_at` beyond `[NEEDS INPUT: batch-lag threshold]` flags the record `BATCHED`; never surfaced as "live." | Must | OBJ-006 |
| FR-836 | Milestone ordering (FR-814) sorts by `observed_at`, never `received_at`, so a late batched ping inserts at its true position. | Must | OBJ-004/006 |
| FR-837 | Timestamps store/reason in UTC with local offset for display; no ambiguous naive-local timestamps persist. | Must | OBJ-006 |
| FR-838 | Derived durations (dwell, ETA) compute from `observed_at` pairs; a `received_at`-only gap never silently substitutes. | Must | OBJ-004/005 |

## 6. Location privacy — requirement and defaults

Position is the **driver's** location, not the account's. Table uses spine §3's permission shape as
requirement + recommended default — F2 formalises as `PERM-` rows.

| Role | Action | Resource | Scope | Default granularity |
|---|---|---|---|---|
| Shipper ops user | view | trip progress | assigned_load | Milestone + corridor/ETA band; not exact coordinates `[NEEDS INPUT: confirm]` |
| Carrier dispatcher | view | live position | own_org | Exact position, own fleet, load active |
| Driver | view/manage | own position sharing | self | Visibility into collection; consent →F12 |
| Platform ops | view | live position | assigned_load, audited | Exact position, exception handling only |
| Consignee (no account) | view | trip progress | tokenised link | Corridor/ETA band only; no coordinates, no history |

| ID | Requirement | MoSCoW | Traces |
|---|---|---|---|
| FR-839 | Position collection is scoped to the active trip window (dispatch through POD, plus `[NEEDS INPUT]` buffer) — never off-duty or between-loads. | Must | OBJ-007 |
| FR-840 | Exact live coordinates are not exposed to a shipper by default; default signal is milestone + corridor/ETA per the table above (see CHALLENGE-800). | Must | OBJ-007 |
| FR-841 | The consignee tokenised link (F1 pattern) carries only current corridor/ETA state, never raw coordinates or history. | Must | OBJ-007 |
| FR-842 | Raw pings and derived milestone/dwell records have independently configurable retention, both `[NEEDS INPUT]`; neither shorter than an open claim's evidentiary need. | Must | OBJ-005/007 |
| FR-843 | A driver may request access to, and deletion of, their own position history, subject to an active-claim/legal-hold exception, per state privacy law (CCPA/CPRA and peers). | Must | OBJ-007 — `[NEEDS INPUT: counsel]` |
| FR-844 | No location data leaves the transaction parties without a stated legal basis; never logged in plaintext general application logs. | Must | OBJ-006/007 — →F12 |

## 7. Anti-spoofing

| ID | Requirement | MoSCoW | Traces |
|---|---|---|---|
| FR-846 | Consecutive pings implying speed above `[NEEDS INPUT]` flag `IMPLAUSIBLE_TRANSIT`, excluded from milestone/dwell computation. | Must | OBJ-006 |
| FR-847 | A device's mock-location/tamper indicator, where exposed, tags the record, excludes it from `CORROBORATED`. | Must | OBJ-006 — capability-dependent |
| FR-848 | ELD vs app disagreement beyond `[NEEDS INPUT]` keeps both records, flagged `SOURCE_CONFLICT`; neither silently preferred. | Should | OBJ-006 |
| FR-849 | A `detention_candidate` or `loaded`/`unloaded` claim built on flagged evidence routes to fraud review before reaching billable/POD-evidentiary status. | Must | OBJ-005/006 — →A8 |
| FR-850 | Manual updates are unverifiable by construction; never presented at the same trust tier as device-sourced ones. | Must | OBJ-006 |
| FR-851 | Repeated spoofing signals feed risk signalling (→A8 pattern detection), never an automatic penalty at this layer. | Should | OBJ-006 |

## 8. Events, entities, integrations

Events (`<entity>.<past_tense_event>`): `position.received` · `tracking.went_dark`/`unavailable` ·
`geofence.entered`/`exited` · `milestone.derived`/`claimed`/`corroboration_flagged` ·
`dwell.session_opened`/`closed` · `detention.candidate_computed` · `eta.recomputed`/`marked_stale` ·
`tracking.spoof_suspected`.

Entities (F3 canonicalises): `PositionPing` (source_type, observed_at, received_at, coordinates,
confidence_tier, flags) · `Milestone` (derived/claimed, corroboration_status) · `GeofenceZone` (facility
ref, polygon, debounce) · `DwellSession` (open/close, contributing pings) · `ETAEstimate` (value,
confidence tier, computed_at, factors[]) · `TrackingCapability` (per-shipment).

Integration capabilities (no vendor names): **INT-800** ELD/telematics ingestion, carrier-controlled,
refusable. **INT-801** driver mobile app position, best fidelity. **INT-802** manual/ops-desk status
capture, lowest trust tier. **INT-803** truck-legal routing capability — ODbL layers stay
Produced-Works-only, never cross this API (DEC-LOCK-002). **INT-804** work-zone/weather/chain-control
feed, geography-bounded (AZ/KS/MN/WA/CA), chain-control licence `[NEEDS INPUT]` per BR-1107.

## 9. Edge case register

| EC | Trigger | Behaviour | Decides | Unresolved? |
|---|---|---|---|---|
| EC-800 | No position source at all | `TRACKING_UNAVAILABLE` from dispatch | System | No |
| EC-801 | Source goes silent mid-trip | `NO_UPDATE_RECEIVED`, last-known stays age-labelled | System | No |
| EC-802 | Truck parked across the road, never enters polygon | `PROXIMATE_NOT_GEOFENCED`; dwell via manual claim only | Ops | Yes — threshold |
| EC-803 | Poor GPS in a steel yard, oscillating enter/exit | Debounced; persistent oscillation downgrades confidence | System | Partial |
| EC-804 | Imprecise polygon, or early arrival before appointment | False arrive, or dwell opens with billability left to A1/A6 policy | F1/F3, A1/A6 | Yes |
| EC-805 | `loaded`/`unloaded` claimed with no corroborating position | `UNCORROBORATED` flag; claim stands, routed to review | Claims/ops | No |
| EC-806 | Manual-only trip, no device ever | All milestones `MANUAL` tier; detention still constructible | Ops | No |
| EC-807 | Batched offline upload arrives late | `BATCHED`, timeline reorders on `observed_at`, never shown live | System | No |
| EC-808 | Impossible-speed pings, mock-location, or ELD-vs-app disagreement | Flagged/excluded — none silently accepted | System, →A8 | Conflict cases yes |
| EC-809 | Detention candidate built on flagged evidence | Held from billing/claim use pending review | A8/A6 | No |
| EC-810 | Mid-trip relay/transload | New milestone set opens; prior leg closes untouched | System | No |
| EC-811 | Driver revokes/loses location sharing mid-trip | Falls back to manual/`TRACKING_UNAVAILABLE`, no fabrication | System | Yes — revocation UX |
| EC-812 | Consignee requests live location via token | Corridor/ETA only, no pin, link expires | System | No |
| EC-813 | Claim opens after retention window elapsed, or deletion requested mid-claim | Litigation hold extends retention / deletion yields to hold | Legal | Yes |
| EC-814 | Position crosses a state line/DST boundary | Stored UTC + local offset, no ambiguity | System | No |
| EC-815 | Device shared across multiple drivers | Attribution to a specific driver unreliable | F1 | Yes |
| EC-816 | Corridor outside covered geographies, or feed licence unconfirmed | States "coverage absent," never "clear"; suppressed until licence confirmed | System, A12/legal | Yes |

## 10. Open design decisions

**DEC-800 — Shipper's default location granularity.** (A) exact pin always; (B) corridor/ETA-only
default, opt-in exact-pin during exceptions; (C) contract-tier configurable. Recommend (B) —
data-minimisation — Boss's call.

**DEC-801 — Retention posture.** (A) one flat period for all location data; (B) tiered — raw pings
short-lived, milestone/dwell evidence retained to at least the Carmack claim/suit-limitation horizon;
(C) carrier-configurable. Recommend (B), the only option avoiding both over- and under-retention.

**DEC-802 — Does manual-only (phone-reported) dwell qualify as billable detention evidence?** Small
carriers may only ever phone in (BRD A4); requiring geofence corroboration for every line structurally
excludes that segment from recovering it. (A) never bills; (B) bills at lower confidence with shipper
review; (C) bills identically, accepting the fraud surface. A6/Boss decision; F8 supplies the evidence
tiering any option needs.

## CHALLENGE-800

Spine §3's scope kinds resolve **which resource** a role sees, not **which fields within it**. Location
privacy (§6) needs field-level redaction — shipper and carrier dispatcher both `view` the same
`assigned_load` trip-progress resource, but one should see a corridor band, the other exact
coordinates. Recommend F2 add a documented field-level view mask as an extension to the permission
primitive (not a fifth scope kind), rather than F8/F9 each inventing ad-hoc redaction.
