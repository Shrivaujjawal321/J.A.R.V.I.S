# D5 — Flow: Platform Ops & Admin/Fraud Review (pages 13, 14)

Sources: `design-spine.md`; `frd-F9-dashboards-screens.md` §1.4/1.5; `FRD-v1.md` §13(F11), §15(F13),
§4(perms), §14.6(audit), §3.3(`ExceptionCase`), §7.3/7.8(errors); `BRD-v1.md` §8.8/8.9.

**Frame index**

| SCR | Screen | Status |
|---|---|---|
| SCR-930 | Exception Work Queue | **Built** — Default(open)/Empty/Contested, `prototype.html` |
| SCR-931 | Exception Detail & Resolution | Spec only |
| [NEW] SCR-934 | Configuration Console | Not in F9 — FR-1142/1145 need a governed-settings surface |
| [NEW] SCR-935 | Impersonation Console | Not in F9 — F9 only names a banner (§11.5), no screen |
| SCR-940 | Carrier Vetting Queue | Spec only |
| SCR-941 | Fraud Case Review | Spec only |
| SCR-942 | Selection Record / Audit Viewer | Spec only |
| SCR-943 | Enforcement Action | Spec only |

**Queue composition, once.** SCR-930 unions two sources, never conflated visually: **Load-state
exceptions** (`CARRIER_NO_SHOW`, `TRANSIT_EXCEPTION`, `DELIVERY_REFUSED`, `PICKUP_REFUSED`,
`SHIPPER_NOT_READY` — single-valued, §3.3) and **`ExceptionCase` records** (`FRAUD_REVIEW`,
`CARGO_INTEGRITY`, `CARGO_CLAIM`, `DISPUTE_FREIGHT`/`MONEY`, `CARRIER_ENFORCEMENT_COLLISION` —
many-per-load, `ENT-324`). A row's case-type badge is absent for the former, present for the latter.

---

## 1. Exception Work Queue (SCR-930)

| Step | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S1 | `[SCR-930]·Default` | Swimlanes by domain (FR-1102); money-at-risk / freight-in-motion / time-criticality as three separate signals, never one score (FR-1103); action attached per row | Scans, opens "Urgent" cross-domain view (FR-1104) | Queries `ExceptionCase.status=OPEN\|IN_REVIEW` ∪ open Load-state exceptions | S2 or SCR-931 | No `PERM-236` → `Permission denied`; no rows → `Empty` (built) |
| S2 | same | Unclaimed row, Claim button | Clicks Claim | `PERM-236`, `granted_case` binds this case only | Row → "Claimed by you" | Race with another claimant → S3 (EC-1100) |
| S3 | `[SCR-930]·Contested` (built) | "Claimed by X," action disabled | Reads only — platform-wide read stays (FR-1108) | No write path for this actor | stays S1 | Contest state is itself terminal for the loser |
| S4 | `[SCR-931]·Default` | Full context, prior actions, handoff note | Escalates (reason required, FR-1107) or works case | `case.status→IN_REVIEW`; escalation → `PLATFORM_SENIOR_REVIEWER` | S5 | Missing reason → inline error |
| S5 | `[SCR-931]·Resolved` | Resolution type/actor/reason, linked downstream action (FR-1110) | Confirms | `status→RESOLVED\|CLOSED_UNRESOLVED`, addendum-only | S1, row removed | Already resolved by another actor → `ERR-529`/`567` |

**Shift handoff:** no staffing model exists (`DEP-900`) — FR-1108 keeps every open case, claimed or
not, platform-wide visible; the handoff note is the only mechanism, not a roster. `FR-1106` auto-
return threshold `[NEEDS INPUT]` — an abandoned claim ages visibly (EC-1101), never silently
reassigns.

**Branch — claim/contest/escalate**

| Condition | Destination | Consequence |
|---|---|---|
| Unclaimed, claim succeeds | S4, `IN_REVIEW` | Off others' unclaimed filter, still platform-visible |
| Claimed near-simultaneously by two | Contested | First commit wins; loser sees who, can't duplicate |
| Fraud case = double-brokering/identity-theft, freight-in-motion | Auto-escalate, senior tier | No human gate — FR-1107 |
| Claim nears 30/120/60-day mark | Auto-escalate | `[NEEDS INPUT]` window; statutory floor never configurable down |
| Manual escalation | Reason required | Logged, senior tier notified |

---

## 2. Working three case kinds (SCR-931)

One frame, three data shapes — action set forks, the surface doesn't.

| Kind | State | Actions available | Never available | Traces |
|---|---|---|---|---|
| Carrier no-show at dock | `·No-show` | Contact carrier, reassign via cascade/re-auction (FR-1124 — ops picks *path*, never hand-picks a winner outside ranked pool), log ground | Force-award off-pool | BR-301/304, `DEC-309` |
| Insurance lapse mid-trip | `·Vetting-lapse-in-flight` | Flag tuple, pin freight-in-motion (FR-1103/1115), require ID/doc re-check at drop, monitor | **Auto-abort the physical trip** — settled, BR-218/219, FR-1310 | FR-1115 |
| Delivery refused, freight on truck | `·Delivery-refused` | Log reason, route `RETURN_TO_ORIGIN`, open `DISPUTE_FREIGHT` if contested, coordinate RTO | Mark `DELIVERED` by ops fiat | §3.3, BR-813 |

`If it fails` (all three): dependent-system failure (eligibility source, doc store) degrades to
flagged/cached per §7.7 postures — never an auto transit action.

**CHALLENGE:** `ENT-324.case_type`'s six values have no slot for two items F11's own prose opens:
FR-1115's `vetting-lapse-in-flight` tag, and §7.8/EC-1205/1211's offline-sync reconciliation item
(§3 below). Both "open a case, route to §13" in text but can't persist as typed `ExceptionCase`
today. Recommend adding `VETTING_LAPSE`/`DATA_RECONCILIATION` before build proceeds past mock data.

---

## 3. Offline-POD sync conflict (SCR-931, new state)

Highest-stakes screen here: POD content decides who gets paid (§3.4). §7.8's rule: canonical state
machine, not wall-clock arrival order, decides — an illegal queued event is never silently applied or
dropped, always routed to a human (`ERR-550`/`553`). Never last-write-wins: that would let whichever
device syncs second silently override a captured signature — how money gets misdirected.

| Step | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S1 | `[SCR-931]·Sync conflict` | Competing captures side by side: device-local time, server-received time, each event's assumed precondition state vs. current canonical state | Opens item (auto-routed, never a generic exception) | `ERR-550`/`553` surfaces raw events, neither applied | S2 | — |
| S2 | same | Evidence per candidate (photo/signature/exception note), clock-skew flag if `ERR-552` present | Compares, picks authoritative capture **or** requests both preserved sequentially (addendum, never overwrite — FR-1129/BR-512) | Nothing auto-resolves | S3 | Evidence gap (e.g. missing photo) → flagged, choice not forced |
| S3 | `·Sync conflict·Resolved` | Chosen event applied; superseded event retained, linked | Confirms with named reason (mirrors FR-1123) | Canonical write proceeds; addendum shows both attempts | Load resumes lifecycle | State advanced again meanwhile → re-enters S1, not auto-retried |

---

## 4. Support impersonation ([NEW] SCR-935)

| Step | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S1 | `[SCR-935]·Initiate` | Target user, scope (whole-account read vs. one named load), reason field | Fills fields, fresh MFA (FR-148) | Validates scope vs `granted_case`; consent per FR-1133 (`[NEEDS INPUT]` implicit-ToS vs. explicit) | S2 | Target under own open fraud case → blocked (EC-1104) |
| S2 | `·Active session` + persistent banner on every touched screen | "Viewing as {user}, ticket {id}, expires {t}," read-only content | Browses read-only | Every render tags `actor_user_id`≠`real_actor_user_id`, audited (FR-149) | S3 or auto-expire | Screen involves an identity-bound action (accept award, sign POD, change payee/banking) → controls hard-disabled (FR-1135) |
| S3 | `·Write-as confirm` | "Acting on behalf of user X, ticket Y" modal | Confirms mutating action | Separate audit entry; identity-bound actions still excluded unconditionally | Action executes, logged | Cancel/mismatch → no-op |
| S4 | `·Expired` | "Session ended," no replay of live content (EC-1116) | Requests new session if needed | Server-side time-box, `[NEEDS INPUT]` duration | S1 | — |

Consignee has no impersonation path — support reads the tokenised delivery link directly (FR-1136).

**Branch — scope**

| Scope | Read | Write |
|---|---|---|
| Whole-account | ✓ | Only via S3, never identity-bound actions |
| One named load | ✓, scoped | Same S3 gate, narrower `granted_case` |

---

## 5. Configuration ([NEW] SCR-934)

Governs §8.7's eleven auction parameters (`DEC-302`…`312`) and the eligibility-gate policy (§15.6) —
versioned settings, never code constants.

| Step | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S1 | `[SCR-934]·List` | All 11 parameters + gate-policy tier, each with version/author/date | Selects a parameter | Read scoped `PLATFORM_CONFIG_ADMIN`/`PERM-264` only | S2 | Wrong role → denied — `PLATFORM_CARRIER_VETTING` explicitly excluded from gate edits (FR-1145) |
| S2 | `·Edit` | New value, effective-date, mandatory reason | Submits | New versioned row, attributed, dated (FR-1144); never overwrites prior | S3 | Missing reason → blocked |
| S3 | `·Applied` | "Applies to auctions not yet published" (or immediate if a runtime-behaviour parameter) | — | `AUCTION_OPEN` instances untouched (FR-1143); award record stores governing version (FR-650) | S1 | Mid-`AUCTION_OPEN` edit for a value-locking parameter → queues for future auctions only (EC-1105), not rejected |

Gate-policy changes carry an explicit flag: *"alters who was allowed to bid — evidence in a future
negligent-selection review"* (FR-1330), never presented as routine config.

---

## 6. Carrier vetting queue (SCR-940)

| Step | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S1 | `[SCR-940]·Default` | Candidates (new + re-verifying, tagged distinct — FR-1114), freight-in-motion pinned (FR-1115) | Opens candidate | Scoped `PLATFORM_CARRIER_VETTING`, `platform_wide` | S2 | Empty → `Empty` |
| S2 | `·Evidence` | Per-tuple evidence + last-verified time for all six elements; COI shown insurer-confirmed vs. carrier-uploaded, **never equivalent** (FR-1111); specific equipment/driver record, never carrier rollup (FR-1116) | Decides APPROVE/REJECT/HOLD-FOR-INFO/CONDITIONAL, reason always required | Writes decision; non-bidding until explicit APPROVE (BR-908) | S3 | No reason → blocked |
| S3a | `·Approve` | Confirm | Approves | `PERM-240`, approver≠editor (maker-checker) | Resolved | Self-approve → denied |
| S3b | `·Override(FAIL→approve)` | Automated-FAIL banner, mandatory per-element justification, "needs second approver" | Submits | `PERM-260` writes addendum type `OVERRIDDEN`, every failed element cited individually (FR-1351) — never blanket | S4 | Missing per-element justification → blocked (FR-1352) |
| S4 | `·Second approve` | Full override context, first reviewer named | Distinct `PLATFORM_SENIOR_REVIEWER` approves/rejects | Bid-eligibility flips only on second approve | Resolved | No second approver on shift → **stalls, no safe default** (EC-1106) |

**Branch — vetting decision**

| Outcome | Destination | Consequence |
|---|---|---|
| APPROVE (gate passed) | Bid-eligible immediately | Single approver, maker≠checker |
| REJECT (even if all checks passed) | Non-bidding | Reviewer discretion permitted, BR-908 |
| Override FAIL→APPROVE | Held pending second approver | Never single-actor; addendum evidence trail |
| HOLD-FOR-INFO | Re-queued | No bidding meanwhile |

---

## 7. Fraud review (SCR-941)

| Step | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S1 | `[SCR-941]·Default` | Case from arrival mismatch (driver/tractor/MC≠awarded tuple, BR-221/224 — flagship signal) or anomaly/contact/remit-change (FR-1117), triggering signal typed | Opens case | Scoped `PLATFORM_FRAUD_REVIEWER` | S2 | — |
| S2 | `·Evidence` | Signal+evidence, award/selection record, vetting history, **cross-load pattern view**, comms log (FR-1118) | Investigates | Read-only aggregation | S3 | Cross-case pattern can't auto-classify — flagged for human (EC-1115) |
| S3 | `·Classify` | Four outcomes: double-brokering / identity-theft / disclosed-and-revetted (closes, no case) / indeterminate-escalate | Selects | `fraud.classified`; disclosed-and-revetted closes but review stays on record (EC-1107) | S4 or resolved | — |
| S4 | `·Containment (freight in motion)` | **No cancel affordance — absent.** Available: withhold payment/settlement, flag `custody-under-investigation`, require ID re-check at drop, generate LE/insurer referral (FR-1120) | Applies containment | Suspension halts new bids/awards, doesn't strand the load (BR-818/FR-1121) | Monitors to resolution | Plainly stated: **cannot recall a truck in transit** — a real ceiling |

**Disclosure question — mapped both ways, not picked (`[NEEDS INPUT]`, FR-1120):**

| Path | Protects | Costs |
|---|---|---|
| Disclose pre-resolution | Fair notice, due process, may surface a legitimate explanation early | Tips off real fraud mid-investigation, risks evidence/asset flight |
| Withhold pending resolution | Containment integrity, referral packet's evidentiary value | Flagged carrier can't respond; due-process exposure if wrong |

**Branch — fraud outcome**

| Outcome | Destination | Consequence |
|---|---|---|
| Cleared (disclosed-and-revetted) | Closes | Review stays on record |
| Contained, freight in motion | Stays open, monitored | No cancel path exists structurally |
| Escalated | Senior tier | Litigation hold if theft/injury/fatality/open claim (BR-819) — never deletable after |

---

## 8. Overrides

No dedicated screen — actions embed in SCR-931 (force-transition, re-award, waiver) and SCR-940/943
(vetting override, reinstatement). The design decision is what does **not** render.

| Override | Where | Gate |
|---|---|---|
| Force stuck transition | SCR-931 | Named actor, reason, before/after, audited (FR-1123); blocked/warned if an open fraud case exists (EC-1114) |
| Re-award after decline/lapse/void | SCR-931 | Same gate + ranked pool; ops picks cascade-vs-re-auction, never a specific carrier (FR-1124) |
| Waive charge / claim payout | SCR-931 / collections | Requester≠approver, second approver above `[NEEDS INPUT]` threshold |
| Reinstate suspended carrier | SCR-943 | Second approver≠suspender (FR-1127); blocked while a fraud case is open (EC-1102) |
| **Force-award to gate-failed carrier** | **Nowhere — no affordance exists, any tier** | FR-1128: refused outright — the action is absent, not disabled |

**Branch — permitted/refused**

| Type | Destination | Consequence |
|---|---|---|
| Overridable | Executes, named actor+reason, audited | Reversible only by a new logged event, never edited history |
| Never overridable | No control renders | Gate bypass, POD/selection-record edits, re-ordering a closed auction, self-approval — structurally absent |

---

## 9. Audit review (SCR-942)

| Step | Frame | User sees | User does | System does | Goes to | If it fails |
|---|---|---|---|---|---|---|
| S1 | `[SCR-942]·Search` | Search by load/carrier/date; entitled-party framing (49 CFR 371) | Searches | `PLATFORM_AUDITOR` (`platform_wide`, read-only, PERM-250/251) or ops via `granted_case` | S2 | No match → `Empty` |
| S2 | `·Record` | Full 371.3 six-element package + selection record + custody events, from stored snapshot alone (FR-1200, no live re-query) | Views, exports | Read path independent of transactional write path (NFR-1229) | S3 | Export target unreachable → retry, never a partial silent file |
| S3 | `·Exported` | Confirmation, `trace_id` | — | Cross-org audit access itself audited, bounded to ops (NFR-1230) | — | — |

---

**Counts:** 9 flows (30 steps across 9 tables) · 8 frames (6 F9 + 2 `[NEW]`) · 8 branch tables · 1
`CHALLENGE`. All screens are permission-aware (§4); ops access is bound to `granted_case` — the case
being worked, not the whole platform — everywhere except `PLATFORM_AUDITOR`/`PLATFORM_ADMIN`
(`platform_wide` by design, both structurally read-only or identity-only).

**Built vs. spec:** SCR-930 alone is built (Default-open, Empty, static Contested). SCR-931,
SCR-934[NEW], SCR-935[NEW], SCR-940, SCR-941, SCR-942, SCR-943 are specified, not built.

**Three questions only Boss can answer:**
1. Fraud disclosure (§7, FR-1120) — does the suspect carrier see the flag before resolution?
   Containment and fair notice pull opposite ways; no default exists.
2. `EC-1106` — second approver required but none on shift: spec says "stalls, no safe default." Is
   that acceptable at launch, or does Boss want a named fallback escalation despite the weaker
   segregation-of-duty?
3. This doc's `CHALLENGE` — extend `ENT-324.case_type` now, or leave `VETTING_LAPSE`/sync-conflict
   items un-typed and queue-unioned without a formal case record?

**Screen whose absence hurts day one most:** SCR-931. SCR-930 lists work, but claim/escalate/resolve
and the §3 sync adjudication have nowhere to execute — a queue showing what's broken with no tool to
fix it, on freight moving 24/7 with no staffing model defined yet.
