# FRD — F7: Driver, Equipment/Trailer Taxonomy, Assignment, Hours of Service

**ID block:** 700-799 (all prefixes). **Traces:** A2 §8.2, A7 §8.7, A4 §8.4, A9 BR-910, spine §0/§1,
DECISIONS.md.

**Owns:** driver records/qualification, equipment taxonomy incl. trailers, driver+truck assignment,
availability/double-commitment, driver lifecycle, HOS tension. **Not owned:** gate mechanics (A2,
extended not restated), fraud classification (A8 BR-806), transit execution (A4), POD (A5), auction
(A3), permission engine (F2 — rows only), privacy controls (F12 — classes flagged only).

## 1. Entities

| ID | Entity | Note |
|---|---|---|
| ENT-700 | `Driver` | User (spine §2), one carrier org unless F2 permits lease-on (FR-723). |
| ENT-701 | `TractorAsset` | Power unit, own lifecycle. |
| ENT-702 | `TrailerAsset` | **Split from A2's single "equipment" concept** — own VIN/plate/availability/location. |
| ENT-703 | `EquipmentPairing` | Tractor+trailer for one leg; re-formable without touching either asset. |
| ENT-704 | `DriverQualificationRecord` | CDL, endorsements, medical-cert expiry, Clearinghouse attestation — fields only. |
| ENT-705 | `Assignment` | (load/leg, driver, tractor, trailer, carrier) — extends BR-212. |
| ENT-706 | `AvailabilityWindow` | Held independently by Driver, Tractor, Trailer. |

## 2. Equipment taxonomy

**CHALLENGE:** A2 BR-209/BR-214 and A1 BR-111 model equipment as one asset per carrier row, and
BR-111's closed set omits **tanker**. Recommend BR-209/BR-214 split into tractor+trailer, and
BR-111 reference this taxonomy. Not a divergence — A2's tuple is unchanged, only "equipment"
unbundles.

| ID | Requirement | MoSCoW | Traces |
|---|---|---|---|
| FR-700 | Tractor and Trailer are independently identified assets, each with own availability; never one merged record. | Must | ext. BR-209 |
| FR-701 | Extensible trailer-type taxonomy: dry van, reefer, flatbed, step deck, tanker, power-only (no trailer) — not a hard-coded enum. | Must | ext. BR-111/209 |
| FR-702 | Reefer: settable temp range (min/max) + mode (continuous-run vs cycle/set-and-hold); matched against load's declared requirement. | Must | → A2 BR-200 |
| FR-703 | Flatbed/step deck: deck-height offset + on-hand securement (tarps/straps/chains/coil racks) as match-usable attributes. | Should | OBJ-003 |
| FR-704 | Tanker: commodity class rated/cleaned for (food-grade vs chemical), compartment count, wash-out flag. Hazmat cargo detail stays with BR-719. | Should | OBJ-003/006 |
| FR-705 | All trailers: length, interior height/width, door type, max weight, axle count. | Must | OBJ-003/004 |
| FR-706 | Power-only tractor (no owned trailer) valid; eligibility needs a shipper/broker drop trailer or a pairing — modelled as pairing, not gate failure. | Should | `[NEEDS INPUT: drop-trailer pools in scope?]` |
| FR-707 | Tractor/trailer attributes checked independently vs load requirement; compliant tractor + incompatible trailer = ineligible even if carrier clears A2's gate. | Must | → A2 BR-200 |
| FR-708 | Trailer ownership/lease/pool status informational (mirrors BR-213), not a hard gate absent Boss instruction. | Could | `[ASSUMPTION: informational only \| conf: med]` |

## 3. Assignment, pairing, substitution

| ID | Requirement | MoSCoW | Traces |
|---|---|---|---|
| FR-710 | `EquipmentPairing` is the unit dispatched per leg; may change within one load's lifecycle (drop-and-hook) without changing carrier-of-record or the driver. | Must | ext. BR-212 |
| FR-711 | Bind (driver, tractor, trailer, carrier) at dispatch acceptance, per leg for multi-leg loads. | Must | ext. BR-212 |
| FR-712 | Disclosed trailer swap mid-transit = custody event (→ A4 BR-402/407), not a mismatch signal; undisclosed swap follows BR-224. | Must | → A4, BR-224 |
| FR-713 | Substitution before pickup re-checks eligibility on the new tuple; after custody transfer, additionally requires an A4 custody event. | Must | → A2, A4 |
| FR-714 | At pickup, arriving driver+tractor+**trailer** checked against the bound Assignment — extends BR-221, which omitted trailer. | Must | ext. BR-221 |
| FR-715 | Post-`AWARD_ACCEPTED`, pre-pickup Assignment change logged with requester/reason (mirrors BR-310); doesn't alter the award record. | Must | derived |
| FR-716 | Assignment state queryable independent of load state (e.g. `IN_TRANSIT` load, mid-trip-relayed Assignment). | Should | derived |

## 4. Availability and double-commitment

| ID | Requirement | MoSCoW | Traces |
|---|---|---|---|
| FR-720 | Driver, tractor, trailer each hold independent time-windowed availability (extends BR-214 to all three); overlapping-window double-commitment blocked per-asset. | Must | ext. BR-214 |
| FR-721 | Trailer dropped at dock transitions to a location-based state distinct from "committed to a load" — pairs with a different tractor while the original departs. | Should | Boss's drop-and-hook instruction |
| FR-722 | Driver self-declared unavailability (ext. BR-216) doesn't release a committed tractor/trailer, and vice versa — states correlate, never collapse. | Should | ext. BR-216 |
| FR-723 | Driver belongs to exactly one carrier org unless F2 explicitly supports multi-carrier lease-on. | Must | `[NEEDS INPUT: lease-on drivers in scope?]` |

## 5. Driver qualification — captured, verified, stored

Minimisation (BR-707/709, NFR-710, CON-703) governs every row: **attestation + expiry only.**

| ID | Requirement | MoSCoW | Verifier/Holder |
|---|---|---|---|
| FR-730 | CDL class (A/B/C, 49 CFR 383.91 `[verify GVWR thresholds]`) + endorsements (H-hazmat, N-tanker, T-doubles, or combo, 383.93). | Must | Self-attested; optional doc image = evidence-of-currency, not verified lookup. |
| FR-731 | CDL verification defaults to self-attestation; live CDLIS/PSP-class lookup is optional. | Should | `[NEEDS INPUT: live CDL-verification integration in scope?]` |
| FR-732 | DOT medical-cert **expiry date only**, never exam result/condition. | Must | Carrier is system of record (391.51 DQ file `[verify]`); platform holds expiry+attestation. |
| FR-733 | Clearinghouse currency as dated attestation (ext. BR-707/BR-211) — no result, violation, or return-to-duty status. | Must | Carrier queries (382.301/.305); platform stores attestation date only. |
| FR-734 | Endorsement-to-load match: hazmat load (BR-719) or tanker trailer requires matching driver endorsement, checked with tractor/trailer type. | Must | → A2 BR-200, A1 BR-118 |
| FR-735 | Every qualification field records verifier-type (self/carrier/platform-doc-check/third-party) + verified-at. | Must | derived |

## 6. Driver lifecycle

| ID | Requirement | MoSCoW | Traces |
|---|---|---|---|
| FR-740 | Driver record created by employing carrier org (or owner-operator self); exists independent of login credentials (mirrors A9 BR-903). | Must | derived |
| FR-741 | Driver leaving deactivates from new Assignments; in-flight Assignments flagged for ops review, not auto-cancelled (mirrors BR-230). | Must | ext. BR-230 |
| FR-742 | Driver abandonment mid-trip = A4 `TRANSIT_EXCEPTION`; F7 supplies only the state change (`ASSIGNED → UNAVAILABLE`) A4 consumes. | Must | → A4 |
| FR-743 | Owner-operator: one person is carrier account + equipment owner + driver at once — not three artificial records; F2's bid-vs-accept-award split (BR-902) still applies, distinctly granted even if self-granted. | Must | → F2, BR-902 |

## 7. The Hours-of-Service tension — options, not a pick

Boss wants driving-hours tracking. A7 already locked **CON-703/NFR-710/BR-709**: no ELD,
Clearinghouse, or D&A data stored absent a lawful basis. Not reconcilable by engineering alone —
**DEC-700 is the fork.**

| Option | What it does | Fulfils ask? | Liability | Cost | Conflicts |
|---|---|---|---|---|---|
| **A — No HOS feature.** No hours field anywhere; carrier alone bears Part 395. | Nothing shown | No | Lowest, zero new exposure | None | Downgrades BR-708 to not-built — a named Boss decision |
| **B — Derived planning signal.** Bounded, attested "hours available this window" at bid/dispatch → FEASIBLE/INFEASIBLE flag vs. transit estimate; flag persisted, raw value discarded. ELD is one optional *source* of the same bounded value, never a raw duty stream. | Partial — signal, not a log | **Real but bounded.** Platform now *influences* scheduling — the negligent-selection logic that hit Boss's own auction (*Montgomery*) extends to "negligent scheduling" if the flag is wrong/ignored. Reduced, not eliminated, by keeping the value bounded and advisory. | Moderate — needs a documented lawful basis + retention rule *before* build (BR-709's own precondition) | Satisfies BR-709 if raw value not retained |
| **C — Full system of record.** Ingest ELD telematics, store RODS-equivalent logs, real-time dashboard, authoritative. | Fully | **High** — platform becomes what an auditor/plaintiff subpoenas; Part 395 duty stays with carrier but platform now holds the evidence and arguably co-manages schedule | High — retention ≈ 395.8(k), multi-vendor ELD surface | **Reverses CON-703/BR-709/NFR-710, already locked.** Silent build overrides a recorded decision |

**DEC-701 (only if B):** input source (driver self-report / dispatcher-report / optional
ELD-capability read) `[NEEDS INPUT]`; INFEASIBLE hard-blocks vs. warns only (per BR-708's "Should")
`[NEEDS INPUT]` — a hard gate is stronger anti-crash but *raises* B's own liability column.

| ID | Requirement (conditional) | MoSCoW |
|---|---|---|
| FR-750 | **[B]** Bounded attested "hours available" at bid/dispatch; never a full RODS/ELD export. | Must-if-B |
| FR-751 | **[B]** FEASIBLE/INFEASIBLE vs. estimated transit time; warning only per BR-708, absent a Boss decision to hard-gate. | Should-if-B |
| FR-752 | **[B]** Persist only flag+timestamp on the award record (already retained per BR-303); discard the raw value after use. | Must-if-B, cites BR-709 |
| FR-753 | **[B]** ELD integration is an optional capability supplying the same bounded value — no vendor, never a raw stream. | Must-if-B |
| FR-754 | **[A]** No hours field/computation/display exists; BR-708 downgrade is a named Boss decision. | Must-if-A |
| FR-755 | **[C]** Out of scope absent an explicit Boss override of CON-703. | — |

## 8. Driver personal data (F12 owns controls)

| ID | Requirement | MoSCoW | Traces |
|---|---|---|---|
| FR-760 | Driver PII (CDL number, medical-cert expiry, home contact, DOB if collected) classified as sensitive personal data under state privacy statutes at schema level. | Must | → A7 §7.7, F12 |
| FR-761 | Driver often not account holder — carrier org's role (controller vs. processor) `[NEEDS INPUT]`, same shape as consignee's unresolved consent (spine §1). Data classes flagged only. | Must | → F12 |

## 9. Permission rows (F2 owns the engine)

| Role | Action | Resource | Scope |
|---|---|---|---|
| `driver` | view | own Assignment | `assigned_load` |
| `driver` | update | own AvailabilityWindow | `own_org` |
| `carrier_dispatcher` | create/edit | Driver, TractorAsset, TrailerAsset | `own_org` |
| `carrier_dispatcher` | create/edit | Assignment (post-award) | `assigned_load` |
| `carrier_owner` | deactivate | Driver | `own_org` |
| `platform_ops` | view | qualification attestation fields | `platform_wide` |
| *(none)* | view | Clearinghouse/D&A/ELD raw data | doesn't exist under A/B |

## 10. API, events, errors, NFRs (capability-named, no vendor)

**API-700–707:** `/v1/carriers/{id}/drivers` · `/v1/drivers/{id}` ·
`/v1/carriers/{id}/equipment/tractors` · `/v1/carriers/{id}/equipment/trailers` ·
`/v1/loads/{id}/assignment` (POST bind, PATCH substitute, GET) · `/v1/drivers/{id}/availability` ·
`/v1/loads/{id}/hos-feasibility-check` `[if B]`.

**EVT-700–708:** `driver.created` · `driver.deactivated` · `equipment.tractor.created` ·
`equipment.trailer.created` · `assignment.bound` · `assignment.substituted` ·
`assignment.mismatch_detected` (→ A8 BR-806) · `trailer.dropped`/`hooked` (→ A4) ·
`hos.feasibility_flagged` `[if B]`.

**ERR-700–706:** `DRIVER_INELIGIBLE_FOR_LOAD` · `EQUIPMENT_TYPE_MISMATCH` ·
`EQUIPMENT_ALREADY_COMMITTED` · `DRIVER_ALREADY_COMMITTED` · `ASSIGNMENT_TUPLE_INCOMPLETE` ·
`ARRIVAL_MISMATCH` (feeds BR-221/224) · `HOS_INFEASIBLE_WINDOW` `[if B]`.

**NFR-700:** no ELD/HOS/Clearinghouse raw-data field exists absent DEC-700 B/C with a documented
lawful basis (mirrors NFR-710). **NFR-701:** every qualification/availability field is verifier-
and time-attributed.

## 11. Edge case register

| ID | Trigger | Behaviour | Who decides | Unresolved? |
|---|---|---|---|---|
| EC-700 | Driver lacks endorsement for an already-assigned hazmat/tanker load | Hold, ERR-700, same-shift review | ops | No |
| EC-701 | Trailer temp range doesn't cover load requirement, found post-bid | Assignment blocked, not auto-cancelled | dispatcher/ops | No |
| EC-702 | CDL/medical cert/Clearinghouse attestation lapses mid-trip | Driver → `INELIGIBLE_FOR_NEW_BIDS` (ext. BR-217); current trip not auto-stopped | ops | Whether current trip continues is a policy call |
| EC-704 | Trailer breakdown/reefer failure mid-transit | A4's `TRANSIT_EXCEPTION`; F7 only flips TrailerAsset state | A4 | No |
| EC-705 | Owner-operator's sole driver unavailable mid-trip, no org substitute | No internal relay; becomes A4's carrier-failure path | A4/carrier | Genuinely hard — no internal substitution exists |
| EC-706 | Driver leased to two orgs bids the same window from both | Double-commitment block (FR-720) | system | Only if FR-723 in scope |
| EC-707 | Shared trailer pool at dock, drop-point ownership ambiguous | VIN/plate resolves it, not "whose pool" | A4/A2 | `[NEEDS INPUT]` drop-pool ownership model |
| EC-708 | Power-only tractor arrives, shipper-supplied trailer not present | `PICKUP_REFUSED`/hold — existing A4 table applies | A4 | No |
| EC-709 | Disclosed drop-and-hook but arriving trailer VIN ≠ disclosed swap | New trailer-identity signal — fraud vector A8's 14-type list doesn't name | A8 | **Yes — recommend A8 add trailer-identity fraud type** |
| EC-710 | Driver deactivated for cause mid-trip | FR-741 flags Assignment; trip not auto-stopped | ops | No |
| EC-712 | HOS attested value (Option B) proves false after an incident | Parallel to A7's EC-724 (Clearinghouse); attestation-only design tested in court | counsel | Yes — inherent to Option B |
| EC-713 | Ops needs to override a mismatch (verified benign cause) | Named-person override + reason, mirrors BR-306 | ops (named) | No |
| EC-714 | Driver never individually onboarded to platform | Assignment binds via carrier-entered record; POD binds per BR-903 | derived | No |

## 12. Summary for Boss

**6-line summary.** Split tractor and trailer into independent assets with own availability so
drop-and-hook is first-class, not an exception; built a full trailer taxonomy with type attributes,
flagging BR-111's closed set is missing tanker. Extended driver+equipment binding (BR-212/221) to
name trailer explicitly — undisclosed trailer swaps are a fraud vector A8's typology doesn't name
yet. Kept every driver-qualification field to attestation-plus-expiry, never the underlying record,
per A7's locked minimisation stance. Resolved the HOS tension into three options (no feature /
bounded planning-signal / full system-of-record), flagging Option C would silently reverse an
already-locked constraint (CON-703). Did not pick — Boss's call.

**Counts.** FR: 38 (6 HOS-conditional). DEC: 2. EC: 13. `[NEEDS INPUT]`: 8.

**Three sharpest questions only Boss can answer.**
1. HOS fork (DEC-700): Option A (no feature, zero new exposure, doesn't fulfil your ask) or Option B
   (bounded feasibility flag, fulfils it but creates negligent-scheduling-adjacent exposure counsel
   hasn't reviewed)? Won't build Option C without you explicitly overriding CON-703.
2. Is a shipper/broker-owned drop-trailer pool in scope, or is every trailer carrier-owned
   (FR-706)?
3. Do owner-operators need to lease on to more than one carrier org, or is one-driver-one-carrier
   fine here (FR-723)?

**CHALLENGE:** repeated from §2 — see there.

**Straight read on whether hours tracking belongs in this product at all:** partially, if scoped
tightly. A feasibility *flag* at bid/dispatch (Option B) answers a real need — your own auction can
today award a lane physically impossible inside HOS, the fact pattern that becomes a
*Montgomery*-style exhibit later. A full duty-log system of record (Option C) isn't a marketplace
feature — it's a second regulated product bolted onto this one, and it contradicts a decision your
own regulatory agent already made and you have on record (CON-703). If I had to bet: build Option B
narrowly, get counsel to sign off on the "documented lawful basis" BR-709 already demands, and don't
chase Option C inside this platform.
