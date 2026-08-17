# FRD — F13: Carrier Vetting & the Eligibility Computation Service

**Origin.** F6 filed a `CHALLENGE`: its gate depends on `eligibility()`, and no agent owned
authority/insurance/safety vetting (F7 = driver/equipment/HOS only). Accepted; block opened. **This
FRD resolves F6's CHALLENGE.**

**ID block:** 1300-1399. **Traces:** BRD A2 §8.2 (BR-200–230, DEC-201), A8 §8.9 (BR-802→303,
BR-806), DEC-LOCK-001, frd-F6 §1/§2, spine §0/§2.

**Owns:** carrier onboarding verification · the `eligibility()` computation service (orchestrates
the six-element BRD A2 tuple) · authority/insurance/safety-signal ingestion + freshness · credential
lifecycle · re-verification cadence · the eligibility evaluation record (F6's selection record
quotes it) · fraud-adjacent identity signals at onboarding/dispatch · gate-policy versioning ·
overrides.

**Must NOT write:** equipment/trailer taxonomy, driver qualification, HOS, assignment/substitution
(F7 — **F13 calls F7's sub-checks, doesn't re-specify them**) · bid/award mechanics, selection-
record write points (F6) · fraud classification/penalty (A8/F11) · entity/state canon (F3) ·
permission rows (F2) · error taxonomy (F5) · ops UI (F11).

---

## 1. The `eligibility()` contract

**FR-1300.** Canonical signature: `eligibility(carrier_id, truck_id, driver_id, load_id) →
{status: ELIGIBLE|INELIGIBLE, reasons: [{code, element, detail}], gate_version, policy_version,
evaluated_at, snapshot_id}`. **A call, never a cached set** — every invocation re-resolves all six
tuple elements from current/last-refreshed data; nothing reads from a prior result.

**CHALLENGE (to F6's FR-600 literal reading, not intent):** F6 writes the signature as
`eligibility(carrier, authority, insurance, safety_signal, truck, driver, load)` — implying the
caller resolves authority/insurance/safety_signal. That is BRD A2's *tuple concept*, not the call
surface; **F13 resolves those three internally from `carrier_id`.** FR-1300's four-argument form
is the real contract; F6's list describes what is *evaluated*, not *passed in* — no behavioural
disagreement, flagged so the assembler doesn't merge two signatures into the API catalogue.

**FR-1301.** Output composes two mandatory sub-evaluations: (a) **carrier/authority/insurance/
safety** — computed here, §2-§3; (b) **equipment/driver match + availability** — F13 calls F7's
per-load match function (FR-702/707, HOS capacity), folding its pass/fail + reasons into the same
`reasons[]` unmodified. F13 never re-derives F7-owned facts, only aggregates.

**FR-1302.** `reasons[]` is never empty on `INELIGIBLE`, structured (`element` = one of the six
tuple elements) — F6's selection record and A8's negligent-selection defence both consume it as
the evidentiary "why," not just the boolean.

**FR-1303. Determinism and replay.** Every evaluation persists a **full input snapshot**, not
pass/fail alone: `gate_version` (logic), `policy_version` (§6's thresholds), and a copy of the
actual authority status, insurance evidence, safety data and F7 sub-result **as read at that
instant** (`snapshot_id`). Reconstructable **from stored data alone, months later** — no live
re-query — matching F6's FR-606 exactly, since F6's record quotes this one, not restates it.

**FR-1304.** Gate-policy changes (§6) are never retroactive; an evaluation cites the
`policy_version` active at `evaluated_at`, immutable once written (mirrors F6 FR-650).

**FR-1305.** F13 does not decide *when* it is called — F6 calls it at bid submission and again per
candidate at award (F6 FR-600/602). The same tuple returning a different result between calls is
correct behaviour, not a bug.

---

## 2. Entities (domain-specific; consolidated model owned by F3)

| ID | Entity | Note |
|---|---|---|
| ENT-1300 | `CarrierVettingRecord` | Per carrier org; role, onboarding status, suspension state |
| ENT-1301 | `OperatingAuthorityRecord` | MC/USDOT, status, checked-at, authority-granted-date (age, BR-202) |
| ENT-1302 | `InsurancePolicyRecord` | COI, certificate-holder=platform, coverage, limits, expiry, per-equipment binding (BR-204) |
| ENT-1303 | `SafetySignalRecord` | Safety rating + CSA/SMS BASIC snapshot, refreshed-at (BR-205) |
| ENT-1304 | `CredentialDocument` | Authority cert, COI, W-9, ID doc — submitted→verified→expiring→expired/revoked |
| ENT-1305 | `EligibilityGatePolicy` | Versioned, effective-dated ruleset (§6): hard-gate elements, thresholds, tiering |
| ENT-1306 | `EligibilityEvaluation` | FR-1300 output + FR-1303 snapshot; append-only |
| ENT-1307 | `IdentityMismatchSignal` | §7 output; consumed by A8/F11, never self-classified (BR-225) |

---

## 3. External data ingestion — capabilities, not vendors

| Capability | What it does | Freshness posture | Unreachable behaviour |
|---|---|---|---|
| **Authority status lookup** (FMCSA SAFER-class) | Active/revoked/OOS status, name/address, authority age | Periodically refreshed store (DEC-1300); `[NEEDS INPUT: award-time live vs store]` | Last-known-good + `stale_after` flag; **never auto-fails** — flagged pass or hold per policy tier (§6); routes to F11 past threshold `[NEEDS INPUT]` |
| **Safety/CSA-SMS feed** | Safety rating + BASIC scores | Batch-refreshed store only, no live per-bid call (§8.2, not necessarily hard-gate) | Same posture; last-refreshed timestamp visible (BR-205) |
| **Insurance/COI verification** | COI current, platform as certificate holder, covers bound equipment; ingests cancellation notices (BR-804 — carrier PDFs never suffice alone) | Onboarding + event push + periodic reverification (§4) | No push ≠ assumed valid; expiry alone drives auto-`INELIGIBLE_FOR_NEW_BIDS` (BR-217) |
| **Identity/document verification** | Signer ID (BR-208), name/address vs authority (BR-207) | Onboarding + material change | Onboarding holds open, not silently approved |
| **W-9 capture** | Tax-form intake | Onboarding, before first payout (BR-206) | Collected/stored only; A6 gates payout — **not** in the eligibility tuple |

**FR-1310.** No upstream reachability problem may **auto-abort a trip already in motion** (BR-218/
219) — data-layer failure degrades to a flag + F11 route, never a transit action (A4).

**FR-1311.** Every ingested field records its **source** (verified vs self-reported) so the
snapshot (FR-1303) distinguishes "we checked" from "carrier told us" (BR-226).

---

## 4. Re-verification cadence — `DEC-1300`, options only

BRD A2 left this open; no industry default exists. Cadence can differ **per signal** (authority/
insurance/safety are not equally volatile) — a policy field, not one number.

| Option | Mechanism | Cost | Risk if chosen |
|---|---|---|---|
| A — Real-time per bid | Live call every `eligibility()` invocation | Highest — call volume = bid volume, rate limits, latency | Lowest staleness risk; most defensible post-*Montgomery* |
| B — Periodic batch refresh | Store on a fixed interval `[NEEDS INPUT]`; `eligibility()` reads the store | Low, predictable | Refresh-to-lapse gap; mitigated by BR-217's expiry auto-block (needs no live call) |
| C — On-demand at award only | Live call only at award walk (F6 FR-602); store at bid time | Medium | Bid-time result stale for whole open window, caught only at award — matches F6's two-pass model if bid-time uses B |

**DEC-1301 — staleness threshold.** Store-age at which a signal stops being "current," forcing a
flagged/held result instead of a silent pass. `[NEEDS INPUT]` per signal; on `EligibilityGatePolicy`
(ENT-1305), versioned, not a constant.

**DEC-1302 — mixed cadence, likely shape.** Authority = A or C; safety = B (BRD A2 explicit);
insurance = event-driven push + B baseline + expiry-date hard block regardless of choice.
`[NEEDS INPUT: final per-signal selection]`.

---

## 5. Credential lifecycle — never auto-abort, always flag

| BRD source | Trigger | F13 behaviour |
|---|---|---|
| BR-217 | Authority/COI/CDL lapses (own detection, or F7 for CDL) | `INELIGIBLE_FOR_NEW_BIDS` same-day, automatic; blocks new bids only |
| BR-218 | Lapse **between award and pickup** | Award unchanged; re-run flags the tuple, review item → F11 queue. No auto-cancel |
| BR-219 | Lapse **after custody transfer** | Same — flag to F11, no transit action (A4's domain) |
| BR-229/230 | Carrier suspended/removed | `INELIGIBLE` for new bids/awards immediately; load past pickup **not** auto-altered — flagged to F11 (mirrors BR-818) |
| BR-220 | Advance-expiry reminders | Content owned here; delivery → F10. Cadence `[NEEDS INPUT]` |

**FR-1320.** Every lifecycle transition above writes an addendum to the `EligibilityEvaluation`
row(s) it invalidates — original never edited in place (mirrors F6 FR-605).

---

## 6. Verification rigour vs. supply liquidity — `DEC-201`, as a versioned policy object

BRD A2's DEC-201 (open, Boss decides): most US carriers run very few trucks; a bar tuned for large
fleets removes the supply this marketplace needs. **Not a hard-coded threshold** — a versioned,
effective-dated `EligibilityGatePolicy` (ENT-1305), since every tuning changes *who was allowed to
bid*, itself evidence in a negligent-selection claim.

| Option | Shape | Cost | Risk |
|---|---|---|---|
| A — Uniform high bar before bidding | Every element hard-gates at onboarding | Fewest edge cases, strongest litigation posture | Shrinks the pool hardest — small-fleet carriers (the actual supply) excluded |
| B — Light bar to bid / heavy bar to win | Cheap onboarding check; full re-verification only for the tuple that would win | Best liquidity, lowest friction | Bid-time record with a light bar is weaker evidence if scrutinised without winning |
| C — Baseline bids, tiered award review | Authority/insurance always hard-gate; safety threshold/authority age enter a review tier near award | Balances both | Tier boundary is itself tunable, contestable — needs its own change log |

**FR-1330.** Whichever option is chosen is a field on `EligibilityGatePolicy`, not application
logic; changes are authored, dated, attributed, never retroactive (FR-1304).
`[NEEDS INPUT: Boss to choose A/B/C — reaches F6 §8.3]`.

---

## 7. Fraud-adjacent identity checks — signals only, not classification

BR-225 binds this section: **facts, never a verdict.** Classification, case-opening and consequence
are A8/F11's (BR-806).

| Check | BRD source | F13 output |
|---|---|---|
| Legal name/address vs authority record mismatch | BR-207 | Holds onboarding; `IdentityMismatchSignal` (ENT-1307) |
| Authorized-signer identity | BR-208 | ID doc on file, reviewable; no auto-block criterion invented |
| Brand-new authority as risk signal | BR-202 | Age captured as **distinct field**, visible at review; **no auto-block on age alone** — no universal threshold exists |
| Dispatch-contact change not matching onboarding record | BR-228 | Flag to review, not hard block (legitimate changes occur) |
| Broker double-brokering path | BR-223 | Downstream asset-carrier must independently clear `eligibility()` before dispatch — F13 evaluates the *sub-carrier's* tuple only, does not adjudicate the pattern (A8 BR-806/814) |
| Pickup mismatch (driver/tractor/MC vs bound tuple) | BR-221/224/227 (F7 executes the check) | F13 supplies the bound-tuple record; the mismatch fact routes to A8's classification (BR-806) |

**FR-1340.** Every signal is timestamped, attributed to the check that produced it, and appended to
`EligibilityEvaluation` or `CarrierVettingRecord` — never silently dropped even if no case opens.

---

## 8. Overrides — evidence, not a bypass

**FR-1350.** An ops reviewer (`→ F2 PERM-1300`) may admit a carrier the gate rejected. Requires
named identity + stated reason — unattributed overrides cannot be persisted (mirrors F6 FR-607).

**FR-1351.** The override does not alter the original `EligibilityEvaluation` row; it writes an
addendum row of type `OVERRIDDEN`, referencing the original result and every reason overridden
individually — a blanket override hiding *which* element failed is not permitted.

**FR-1352.** Stated plainly, since it governs F11's review screen: **an override is itself evidence
in a negligent-selection claim** — it converts "the gate said no" into a discoverable fact with a
name attached. F11's console must surface the override's history wherever the evaluation is later
shown, not just at decision time.

---

## 9. API surface (own resources; catalogue conventions → F4)

| ID | Endpoint | Notes |
|---|---|---|
| API-1300 | `POST /v1/loads/{load_id}/eligibility-checks` | Body `{carrier_id, truck_id, driver_id}`; internal, F6 calls at bid+award |
| API-1301 | `GET /v1/carriers/{id}/eligibility-evaluations` | Audit history; scoped `own_org`/`platform_wide` (F2) |
| API-1302 | `POST /v1/carriers/{id}/documents` | Credential upload (authority cert, COI, W-9, ID doc) |
| API-1303 | `GET /v1/carriers/{id}/documents` | Status per document, expiry, source |
| API-1304 | `GET /v1/carriers/{id}/eligibility-status` | **Advisory only**, dashboards (F9); only a per-load `eligibility()` call is authoritative |
| API-1305 | `POST /v1/eligibility-evaluations/{id}/override` | FR-1350 identity+reason required |
| API-1306 | `GET/POST /v1/eligibility-gate-policies` | Policy authoring (§6), admin-scoped |

Errors route via the canonical envelope (§4) to F5's taxonomy; representative codes:
`ELIGIBILITY_AUTHORITY_REVOKED`, `ELIGIBILITY_COI_EXPIRED`, `ELIGIBILITY_COI_COVERAGE_MISMATCH`,
`ELIGIBILITY_SAFETY_DATA_STALE`, `ELIGIBILITY_EQUIPMENT_MISMATCH` (F7 reason, surfaced through this
envelope), `ELIGIBILITY_DATA_SOURCE_UNREACHABLE` (flags, never hard-fails, §3), `CARRIER_SUSPENDED`,
`OVERRIDE_MISSING_REASON`.

---

## 10. Events

`carrier.credential_lapsed` · `carrier.credential_restored` · `carrier.suspended` ·
`carrier.reinstated` · `eligibility.gate_override_applied` · `eligibility.identity_mismatch_flagged`
· `gate_policy.version_published`. **No `eligibility.evaluated` event** — volume equals bid volume;
per-evaluation events would flood F10. Only state-changing outcomes emit.

---

## 11. Edge case register

| ID | Trigger | Behaviour | Decides | Unresolved |
|---|---|---|---|---|
| EC-1300 | Authority/safety upstream unreachable at bid time | Last-known-good + `stale` flag; never hard-fails on unreachability alone | Automatic | Staleness threshold (DEC-1301) |
| EC-1301 | Same, at award-time re-walk (F6 FR-602) | Higher stakes — flagged in selection record | Automatic + F11 | Live vs store read at award (DEC-1300 C) |
| EC-1302 | COI lapses between award and pickup | BR-218: award unchanged, ops flag opened | F11 | — |
| EC-1303 | Authority revoked mid-transit, post-custody-transfer | BR-219: flag only, no transit action | F11/F4 | — |
| EC-1304 | Safety batch refresh fails/falls behind; re-verification backlog misses cadence window | `refreshed_at`/`stale` visible at review (BR-205); held past DEC-1301 threshold per policy tier | Automatic | Alert threshold owner `[NEEDS INPUT]` → F12 |
| EC-1305 | Name/address mismatch vs authority record at onboarding | Onboarding held, not silently approved | Ops (F11) | — |
| EC-1306 | Brand-new authority bids | Age visible, no auto-block | Policy (§6 tiering) | Default review-tier entry for new authority? |
| EC-1307 | Undisclosed post-award substitution signal (BR-224) | Fact recorded only; routes to A8/F11 | A8/F11 | — |
| EC-1308 | Override admits a gate-rejected carrier | Addendum written (FR-1351); treated as evidence (FR-1352) | Named person | — |
| EC-1309 | Gate policy version changes while auctions open on old version | Mirrors F6 FR-650: in-flight evaluations keep `policy_version` | Automatic | — |
| EC-1310 | F7 sub-check (equipment/driver) unavailable or incomplete | Tuple unresolved → `INELIGIBLE`, reason element cited | Automatic | — |
| EC-1311 | Broker wins; downstream asset-carrier not yet vetted | Award proceeds provisionally (BR-223); dispatch-gate blocks dispatch, not award | Automatic + F13 gate | — |
| EC-1312 | Carrier suspended with an in-flight load | New bids/awards blocked; existing load not stranded (BR-818/230) | F11 | — |
| EC-1313 | Identity/document verification capability down at onboarding | Onboarding holds open; no default admission | Automatic | — |
| EC-1314 | W-9 missing | Blocks payout (A6), not bidding — kept out of the tuple | Automatic | — |
| EC-1315 | Identity theft at onboarding — impostor uses real MC/insurance | §7 checks are the only detection surface F13 owns; classification is A8's | A8/F11 | Detection depends on DEC-1300/1302 |
| EC-1316 | Dispatch-contact change not matching onboarding record | Flagged to review, never hard-blocked alone (BR-228) | Ops | — |
| EC-1317 | Self-declared unavailability on an asset bound to an in-progress award | Blocks *new* eligibility only; binding not retracted — conflict flagged | F11 | Precedence rule `[NEEDS INPUT]` |
| EC-1319 | Gate-policy tightening (§6) disqualifies many previously-eligible carriers | No auto-rollback; effective-dated, reviewable — thin-market fallout is F6's DEC-310 | Ops/Boss | Cost-of-tightening not modelled here |
| EC-1320 | `EligibilityEvaluation` write fails mid-transaction | Never reports ELIGIBLE without a complete persisted snapshot | Automatic | Mechanism → F5/F12 |

---

**What F13 cannot resolve alone:** cadence (DEC-1300/1301) and rigour tier (DEC-201/§6) are
supply-vs-liability trade-offs only Boss, with counsel/insurer input, can set; F13 built the
machine to hold whatever numbers arrive, not the numbers themselves.
