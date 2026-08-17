# D4 — Flow: Driver (mobile), Figma page 12

Scope: `SCR-920`–`926` (F9's driver block) plus three new screens the invite/device and sync-conflict
paths need but F9 never specified. Two frames are **built and verified** in `prototype.html`:
`[SCR-920] Driver · Today · Default` and the full `[SCR-924] Driver · POD capture` sequence (choice
through pending-sync). Everything else below is specified, not built.

**New screens, justified:**
- `[NEW] SCR-927` Driver · Invite Accept & Device Bind — F1 §5.3/§9 requires this handshake; F9 has
  no screen for it.
- `[NEW] SCR-928` Driver · Sync Held for Review — FR-901/`ERR-550`–`553` route offline conflicts to a
  human queue; needs its own honest frame, distinct from ordinary pending-sync.
- `[NEW] SCR-929` Driver · Session Ended — FR-128/FR-150/FR-152 revoke a device or session; driver
  needs to see *why*, not a blank login screen.

Every screen below also carries `Offline` and `Error` per the core set (§3 spine); only additional
states are listed. Sunlight/AAA-contrast, ≥24px glove targets, one-handed thumb-zone layout, and the
EN/ES toggle (already built on `SCR-920`) apply to every frame here without repeating the note per
step.

---

## 1. Device onboarding

| Step | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S1 | `[NEW SCR-927] Invite Accept · Default` | Carrier org name, dispatcher name, role, one "Accept" button | Taps accept | Validates single-use, expiring, phone-bound invite token (FR-106) | S2 | Token expired/used → `Error`: "This invite has expired — ask your dispatcher to resend" |
| S2 | `[NEW SCR-927] · OTP verify` | SMS code field, large numeric keypad | Enters 6-digit code | Verifies phone (FR-108); rate-limits retries | S3 | Mismatch → inline retry; exhausted → "Ask your dispatcher to resend the invite" |
| S3 | `[NEW SCR-927] · PIN/biometric setup` | Set local unlock | Sets PIN or enrolls biometric | Local-unlock layer atop server session (FR-112), never a substitute for it | S4 | Biometric unavailable → PIN-only fallback, no dead end |
| S4 | `[NEW SCR-927] · Device bind` | "This phone is now your Jarvis Freight device" | Confirms | Refresh token bound to device/install id (FR-123); old device (if any) unaffected unless explicitly deregistered | S5 | — |
| S5 | `[NEW SCR-927] · Language` | EN/ES toggle, persists | Picks language | Stored on driver record (BR-914) | S6 | — |
| S6 | `[SCR-920] Today · Empty` or `Default` | No assignment yet, or today's load | Waits, or acts on S7+ | — | §2 | — |

**Lost phone mid-trip:** admin deregisters the device (FR-128) → refresh token invalidated server-side
→ next app open shows `[NEW SCR-929] Session Ended` ("Your access was ended by Ironhide Trucking —
call dispatch"), never a bare login screen implying the driver did something wrong. Admin re-invites
on a replacement device → S1–S6 again; FR-153 requires the admin to bind the replacement session to
the **in-flight load** before any further driver-scoped action — the trip/custody record itself
persisted untouched (FR-152).

**Driver leaves carrier mid-trip:** identical `SESSION_REVOKED` → `SCR-929`. **The FRD names an
honest gap here (EC-107): revoking the session does nothing to the loaded truck still parked
somewhere.** Flagged in the closing questions.

**Not invented:** EC-103 (shared family device, no "switch driver" flow) is explicitly unspecified in
F1 — surfaced here, not guessed.

---

## 2. Today's assignment — `[SCR-920] · Default` (built)

One card, one primary action, large glove-friendly targets (`big-target` class, already ≥24px),
thumb-zone bottom half. Built states: `Default` (in-transit card, ETA, ⁠Start-navigation CTA,
call-dispatch + deliver/POD grid, open-exception card, Report-a-problem). Additional states this spec
adds: `Empty` ("No assignment yet"), `Loading (skeleton)`, `Offline` (built — last-synced badge, "8
min ago," never blank), `Locked` (session revoked mid-view → `SCR-929`).

**HOS is deliberately not a live countdown.** `DEC-700` is unresolved (Option A/B/C, §9.6 FRD). This
design assumes Option B's shape only as a *badge*, never a ticking clock: `FEASIBLE` / `INFEASIBLE` /
`Hours: not evaluated` (EC-912's honest default). A raw hours-remaining display would itself be
Option C — the system-of-record posture already rejected by the minimisation constraint. If Boss
locks Option A, the badge is deleted, not hidden.

**The dark-driver case is designed by omission, on purpose.** Nothing on `SCR-920` nags the driver to
"check in." `NO_UPDATE_RECEIVED` (BR-401) is ops's and the shipper's problem to chase (F9 §4's
notification table), not friction pushed back onto a driver who may have no signal at all.

---

## 3. Heading to pickup

| Step | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S7 | `[SCR-920] Today · Default` | "Start navigation" CTA | Taps | Hands off to external nav app | `[SCR-921]` | No nav app installed → inline "Open in browser maps" fallback |
| S8 | `[SCR-921] Navigation Handoff` | One-tap confirmation only; app owns no in-app map | Confirms | Deep-links out | External app | Deep-link fails → returns to `SCR-920` with address copy-to-clipboard |
| S9 | `[SCR-922] Arrival Capture · Default` | Geofence-assisted "You've arrived" prompt, or manual "I'm here" | Confirms arrival; enters/scans tractor plate + trailer VIN if not auto-paired | Geofence entry (FR-819 debounced) + FR-140 timestamp; compares tuple to bound Assignment | Branch — §5.1 | No geofence on file → manual-only arrival, flagged `Partial data` |
| S10 | Branch outcome | — | — | — | Match → `SCR-923`; Mismatch → `SCR-922 · Held` | See §5.1 |

---

## 4. The pickup handover — highest-risk event in the system

| Step | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S11 | `[SCR-923] Document Capture · Structured count` | Declared vs. actual: piece/pallet count, weight if declared, condition, seal number | Confirms or edits against declared | Builds pickup record per BR-400 | S12 | Count doesn't match declaration → `Discrepancy hold`, see §5.2 |
| S12 | `[SCR-923] · Photo` | Camera CTA, BOL + seal + condition | Takes ≥1 photo | Unreadable image flagged before accept, not silently stored (BR-400/408, `ERR-506`) | S13 | No camera permission → text-only notation fallback (EC-910), never blocks |
| S13 | `[SCR-923] · Dual acknowledgement` | Same signature-pad component as POD (reused, not reinvented) | Driver + shipper rep each sign, printed name + role | BR-400 requires **both** acknowledgements + timestamp before `PICKED_UP` is reachable | S14 | Shipper rep unavailable/refuses → cannot proceed to `PICKED_UP`; routes to §5.2's not-ready/refused branch |
| S14 | `[SCR-923] · Submitted` | "Pickup recorded" confirmation | — | Load state → `PICKED_UP`; F8 milestone `loaded` (claimed) | `[SCR-920] In transit` | Offline → queued locally, `Pending sync` (see §8) |

---

## 5. Branch tables

### 5.1 Arrival identity match/mismatch

| Condition | Destination | Consequence |
|---|---|---|
| Driver session + entered tractor/trailer match bound Assignment tuple | `SCR-922 · Arrival confirmed` | FR-140 timestamp+geofence logged; → `SCR-923` |
| Disclosed, pre-approved relay/drop-and-hook substitution | `SCR-922 · Arrival confirmed` | Re-verified tuple, no case opened (FR-713) |
| Mismatch — wrong driver, wrong tractor, wrong trailer, undisclosed swap | `SCR-922 · Held pending verification` | FR-139 suspends further session-scoped actions on this load; `ExceptionCase(FRAUD_REVIEW)` opens (BR-806); driver sees "Dispatch is verifying this pickup — call them" and a Call button, **never** a raw `ARRIVAL_MISMATCH` code |

### 5.2 Pickup: proceed / refuse / not-ready

| Condition | Destination | Consequence |
|---|---|---|
| Ready, count/condition matches, correct equipment | `SCR-923` proceeds → `PICKED_UP` | Milestone `loaded` claimed |
| Freight not ready | `SCR-922 · Not ready` (reason: not-ready / dock closed) | `SHIPPER_NOT_READY`; TONU flag → §8.6 accessorial |
| Freight differs from declaration | `SCR-923 · Discrepancy hold` | BR-406 hold; resolution outcome (substitution confirmed vs. held) recorded before loading continues |
| Wrong equipment (trailer type mismatch) | `SCR-922 · Refused` | `PICKUP_REFUSED`, `EQUIPMENT_TYPE_MISMATCH` |
| Unsafe load | `SCR-922 · Refused` (reason: unsafe) | `PICKUP_REFUSED`, reason `UNSAFE_LOAD`, same-shift ops review |
| Seal missing where required | `SCR-923 · Condition note` | Logged, not blocking, re-verified at drop (BR-408) unless hazmat mandates it (BR-719) |
| Detention accruing | `SCR-920` banner + `SCR-923` timer | `detention_candidate_minutes` computed (FR-821); informational only, never blocks the driver |
| Lumper fee at pickup | `SCR-923 · Lumper flag` (receipt photo) | **`CHALLENGE`:** BR-516 scopes lumper capture to *delivery* only; the same event happens at pickup docks. Recommend the identical flag+receipt affordance at both ends. |

### 5.3 Delivery: clean / exception / refused / nobody-there

| Condition | Destination | Consequence |
|---|---|---|
| Delivered clean | `SCR-924` Step 3→6→7 (Clean path) | `DELIVERED → POD_CAPTURED`; invoice opens clean |
| Delivered with exception (OS&D) | `SCR-924` Step 3→3b→4(photo mandatory)→5→6→7 | OS&D notation (BR-503); invoice line held pending §8.9 |
| Full refusal | `SCR-922/924 · Refused` **[specified, not yet built]** | `DELIVERY_REFUSED`, required reason code, `RETURN_TO_ORIGIN` custody event; no invoice line (BR-506) |
| Nobody present / hours closed | `SCR-922 · No receiver` **[spec only]** | `DELIVERY_ATTEMPTED_NO_RECEIVER`; arrival timestamp only, no POD, forced-choice screen never reached (BR-509) |

### 5.4 Sync: success / conflict

| Condition | Destination | Consequence |
|---|---|---|
| Queue applies cleanly, causal order matches canonical state | Silent — "Delivered — recorded" | EC-510, indistinguishable from a live submit |
| Load state advanced while dark (reassigned/cancelled/already-captured elsewhere) | `[NEW SCR-928] Held for review` | `ERR-550`→`524`; routed to human queue, **never** last-write-wins |
| Queue exceeds retention before reconnect | `[NEW SCR-928] · Expired` | `ERR-551`; ops-assisted recovery only |
| Device clock skew flags a money-bearing timestamp untrusted | `[NEW SCR-928] · Timestamp held` | `ERR-552`; same human-queue path |

---

## 6. In transit

| Step | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S15 | `[SCR-920] In transit · Default` | ETA, next stop, exception banner if any, Report-a-problem always visible | Mostly nothing — position is passive (FR-800), not a manual check-in chore | Pings feed milestones/ETA (F8); `NO_UPDATE_RECEIVED` if dark, driver never nagged | S16/S17 | — |
| S16 | `[SCR-925] Report a Problem · Category` | Breakdown / weather-closure / reefer-alarm / accident / theft / OOS-order / other | Picks category, attaches photo or voice note | `TRANSIT_EXCEPTION` sub-type opens (BR-405); high-priority sync queue if offline | `[SCR-920]` w/ open-exception card | Offline → queues, `Pending sync` badge, never silently dropped |
| S17 | `[SCR-920] · Interrupt` (system-pushed) | Full-screen, non-dismissible — e.g. telematics-detected reefer alarm | Acknowledges / calls dispatch | Full-screen interrupt per F9 §4 rule — never a toast for anything blocking | Back to Today or `SCR-925` for detail | — |
| S18 | Driver truly dark (no signal, no update) | Last-known cached state stays visible, age-labelled | Nothing — by design | `NO_UPDATE_RECEIVED` flag visible to ops/shipper only | resumes at reconnect | — |

---

## 7. Delivery and POD — `[SCR-924]` (built)

Already built end to end: arrival → count/condition (folded in) → **the forced choice** ("Delivered
clean" vs "Report exception," no pre-selection, Continue disabled until one is picked, `role="group"`,
linear reading order) → exception sub-screen (type/qty/whose-count, structured, notes supplement
only) → photo (optional clean, mandatory exception) → signature (printed name + role, no account,
canvas `aria-label`'d) → read-only confirm → submit → pending-sync. This is the single most
consequential screen in the product and already meets BR-501/502/505/512 by construction: no combined
"confirm delivery" button, no default, exception path has the same tap-count to signature as clean —
**not punished with extra friction**, matching the brief.

**Concealed-damage addendum (BR-504):** reachable later from load history, always linked to the
original POD, never overwriting it — **[specified, not yet built]**, its own frame, same signature
component, one field: "What was found, when."

---

## 8. Offline throughout

Cross-cutting, not a separate screen: every capture (`SCR-922`/`923`/`924`/`925`) persists locally
first, syncs on reconnect, and shows the same `sync-pill--pending` pattern already built on `SCR-924`
step 7 — "captured locally, will upload the moment you're back online. Nothing is lost." A captured
signature is never blocked by connectivity (EC-901, FR-124). The conflict case is §5.4: routed to
`[NEW SCR-928]`, a human-reconciliation queue item, never resolved client-side or presented to the
driver as something they need to fix.

---

## 9. Reporting a problem

Single entry point, reachable from `SCR-920` at all times and from inside the POD flow without losing
in-progress capture: `[SCR-925]`. Always reaches the ops desk (`SCR-930`'s queue) with the category
already attached — never a re-triage step on the ops side (F9 §4). Voice-note option matters most for
low-literacy/Spanish-primary drivers who may not want to type.

---

## Summary

**6-line summary.** Mapped the driver's full journey from SMS invite through device bind, arrival
identity match, pickup's dual-signature handover, in-transit passivity-by-design, to the built
forced-choice POD and its pending-sync/conflict handling. `SCR-920` and `SCR-924` confirmed built and
correct against BR-501/502/505/512. Added three new screens (`SCR-927`–`929`) F9 never specified for
invite/device-bind, sync-conflict, and session-ended. Deliberately did **not** design a live HOS
countdown — `DEC-700` is unresolved and a countdown would itself be the rejected Option C. Named one
BRD gap (lumper capture scoped delivery-only) and one operational gap (revocation doesn't move a
loaded truck).

**Counts:** ~28 steps (S1–S18 plus onboarding S1–S6 and pickup S11–S14) · 10 frames referenced (7
existing `SCR-` IDs, 3 new) · 4 branch tables (§5.1–5.4, 20 rows total).

**Built vs. specified:** `SCR-920` (Today) and `SCR-924` (POD capture, full 7-step sequence) are
built and verified in `prototype.html`. `SCR-921/922/923/925/926` and all three `[NEW]` screens are
specified only.

**Three sharpest questions only Boss can answer:**
1. `DEC-700` — HOS Option A (nothing shown) or Option B (bounded feasibility badge)? Assumed B's
   shape here but builds nothing live without the lock.
2. Session revocation when a driver leaves mid-trip kills the *app*, not the *truck* — freight is
   still physically on a road. Is there an operational handoff process, or does this stay a gap?
3. Lumper-fee capture is written into the BRD as delivery-side only (BR-516) — should pickup-side
   fees get the identical affordance, or is that intentionally out of scope?

**`CHALLENGE`:** see §5.2 — BR-516 scopes lumper-fee capture to the delivery side only; recommend the
identical flag+receipt affordance at pickup too, not left uncaptured there.

**The single moment where a bad UI decision costs the most real money:** the forced-choice screen in
`SCR-924`. A clear-signed POD materially weakens a later cargo claim (BR-505) — any UI that makes
"clean" the path of least resistance (a default, a faster tap-count, a friendlier colour) quietly
biases drivers toward under-reporting real damage, and every under-reported load is a claim someone
cannot win later. The built version already gets this right — no default, equal visual weight, equal
tap-count — and that correctness must survive any future redesign untouched.
