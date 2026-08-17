# FRD — F11: Platform Admin, Ops Console & Support Tooling

ID block **1100-1199**. References: `frd-spine.md` §2 tenancy, §3 permission shape, §4 API/error/event
conventions; `spine.md` §3 lifecycle, §6 scope boundaries; `DECISIONS.md` DEC-LOCK-001/002. Screens →
F9 (referenced, not duplicated). Permission matrix assembly → F2. Error taxonomy → F5. Entity/audit
model → F3. Event catalog → F10. API catalog → F4.

**Thesis, from A9's finding:** every exception state in the lifecycle lands on a human, and this is
that human's tool. The BRD is explicit that no staffing model, coverage size, or SLA exists yet
(DEP-900, RSK-027) — this FRD builds the tooling that works under *any* coverage model the client
eventually picks, and states plainly where the tooling alone cannot substitute for headcount.

## 1. Exception work queue — the core product

Every trigger named across the BRD (spine §3's table; BR-218/219 lapse; BR-224/806 mismatch; BR-814
anomaly; BR-908 vetting approval; BR-907 waiver; BR-807 claim intake; DEC-310 thin-market) opens an
`ExceptionCase`, a first-class record independent of the parent entity's own lifecycle state.

| ID | Requirement | Traces | Pri |
|---|---|---|---|
| FR-1100 | Every trigger above opens exactly one `ExceptionCase`, never held only in the domain entity's state field. AC: load enters `TRANSIT_EXCEPTION` → a case exists referencing it. | BR-913 | Must |
| FR-1101 | One entity may hold multiple, independently-owned open cases concurrently (e.g. a fraud case and a detention dispute on the same load) — opening one never closes or hides another. | BR-913 | Must |
| FR-1102 | Each case carries a domain tag (vetting-review / fraud / claim / auction-failure / transit-exception / delivery-exception / financial-dispute / config-change-pending), rendering as segmented swimlanes — never one flat list. | derived, Boss's brief | Must |
| FR-1103 | Each case exposes three independent prioritisation signals, never pre-collapsed into one number: **money-at-risk** (declared value / invoice / claim amount), **freight-in-motion** (load at/after `PICKED_UP`, before `POD_CAPTURED`), **time-criticality** (proximity to pickup/delivery window, COI/authority expiry, Carmack 30/120/60-day obligation, auction close). `[NEEDS INPUT: does the client want a computed composite score in addition — no formula invented here]` | BR-913, KPI-07/08/09 | Must |
| FR-1104 | A cross-domain "urgent" view unions freight-in-motion cases, any fraud-classified case, and cases within `[NEEDS INPUT: deadline proximity window]` of a bound deadline, regardless of domain tag. | OBJ-006 | Must |
| FR-1105 | Any user with the queue-work permission may claim an unclaimed case; claimed cases stay platform-wide visible (read) but are removed from others' "unclaimed" filter. | BR-913 | Must |
| FR-1106 | A claimed case with no recorded action for `[NEEDS INPUT: inactivity threshold]` auto-returns to unclaimed. | derived | Should |
| FR-1107 | Manual escalation to a named senior tier requires a reason. Auto-escalation, no human decision needed: a fraud case classified double-brokering/identity-theft where the load is at/after `PICKED_UP`; a claim case within `[NEEDS INPUT]` of its BR-808 statutory deadline. | BR-806/808 | Must |
| FR-1108 | Cases carry a free-text handoff note and a last-touched actor/timestamp. No case is bound to a shift roster — there is no staffing model in this spec (DEP-900) — so every open case, claimed or not, stays visible platform-wide to anyone holding the permission, which is how the tool supports whatever coverage model the client adopts. | DEP-900, RSK-027 | Must |
| FR-1109 | Time-in-queue and time-to-resolution are tracked for every case regardless of whether a target exists. A per-domain-tag target-response field exists, empty by default. **`[NEEDS INPUT: SLA targets per domain — none invented]`.** | KPI-11 | Must |
| FR-1110 | Resolution records type, actor, reason, and links to any downstream action taken (override, waiver, suspension, claim decision) — the case is a self-contained audit trail. | BR-306/817/907 | Must |

## 2. Carrier vetting and re-verification tooling

The reviewer surface behind A2's eligibility gate, and the human step BR-908 requires even after every
automated check clears.

| ID | Requirement | Traces | Pri |
|---|---|---|---|
| FR-1111 | Review surface shows, per candidate, evidence and last-verified timestamp for all six eligibility-tuple elements (§8.2 BRD): FMCSA/SAFER status+age, COI fields **and** verification source (insurer/agent-confirmed vs. carrier-uploaded only, per BR-804 — the two are never shown as equivalent), safety rating/CSA-SMS with refresh time, legal-name/address match (BR-207), identity document (BR-208), declared role + role-specific docs (BR-203). | BR-201-211 | Must |
| FR-1112 | Reviewer decision is APPROVE / REJECT / HOLD-FOR-INFO / CONDITIONAL (approve with a named, tracked condition, e.g. authority-age noted per BR-202). Reason required on every decision. Account stays non-bidding until an explicit APPROVE (BR-908). | BR-908 | Must |
| FR-1113 | Reviewer may REJECT even where every automated check passed — tightening the gate is never additionally gated. Reviewer overriding an automated **FAIL** to APPROVE requires a documented justification **and** a second, named approver before the account becomes bid-eligible. This is DEC-201 made operational: F11 does not pick among DEC-201's three rigour options, it enforces whichever is chosen, but a fail→approve override is never single-actor. | DEC-201, BR-908 | Must |
| FR-1114 | Recurring re-verification cases (cadence `[NEEDS INPUT]`, BR-201/205/217) render on the same surface, tagged distinct from initial onboarding — a carrier already mid-relationship needs different handling than a new applicant. | BR-217-219 | Must |
| FR-1115 | A lapse between award and pickup (BR-218) or mid-transit (BR-219) opens a case tagged `vetting-lapse-in-flight`, pinned to freight-in-motion (FR-1103) so it never sorts below a paperwork-only lapse. | BR-218/219 | Must |
| FR-1116 | Reviewer sees the specific equipment/driver record bid on the load, never a carrier-level rollup — "no carrier is eligible in the abstract" (spine §2) holds in the tool, not just the schema. | BR-200/209/210 | Must |

## 3. Fraud review

| ID | Requirement | Traces | Pri |
|---|---|---|---|
| FR-1117 | Fraud cases open automatically from: BR-221/224 arrival mismatch (driver/tractor/MC at pickup ≠ awarded tuple — the flagship signal), BR-814 award-pattern anomaly (lane rotation, win concentration, implausible underbidding), BR-228 last-minute contact change, BR-812 out-of-band payment/remit change, rating-manipulation pattern (BR-815). Each case carries its triggering signal type as a field. | BR-806/814/228/812 | Must |
| FR-1118 | Review surface shows: triggering signal + raw evidence, the award/selection record (BR-303), the carrier's full onboarding and re-verification history, a **cross-load pattern view** for the same carrier (prior mismatches/anomalies), and the load's communication log. | BR-303/806 | Must |
| FR-1119 | Reviewer classifies — the act A2 explicitly does not perform (BR-225): double-brokering (undisclosed substitution) / carrier-identity-theft (impostor on real MC credentials) / disclosed-and-revetted substitution (closes, no case) / indeterminate-escalate. | BR-806/225 | Must |
| FR-1120 | Where the load is freight-in-motion (§1), the case **cannot** close by cancellation. Available actions are containment only: withhold pending payment/settlement; flag the shipment `custody-under-investigation` for ops/shipper/consignee (BR-820) — `[NEEDS INPUT: whether the flag discloses to the suspect carrier before resolution; containment vs. fair notice is a genuine, unresolved tension]`; require identity re-check at the drop before a signature is accepted (→ F9 delivery screen, → F5 rejection code); generate a law-enforcement/insurer referral packet from BR-303 + case evidence. **Stated plainly: the system cannot recall a truck in physical transit.** That is a real ceiling, not an implementation gap. | BR-818/820 | Must |
| FR-1121 | Suspension from a fraud case follows BR-818: halts new bids/awards immediately, does not strand the in-flight load — the load stays under FR-1120's containment until physically resolved. Suspension is never a cancellation lever. | BR-818 | Must |
| FR-1122 | Any fraud case tied to theft, serious injury, fatality, or an open claim goes under litigation hold (BR-819) — status may change, the case and its evidence may never be deleted. | BR-819 | Must |

## 4. Override powers and their controls

**Overridable, controlled:**

| ID | Requirement | Traces | Pri |
|---|---|---|---|
| FR-1123 | Force a stuck lifecycle transition (e.g. `AWARD_PENDING` past its window with no automated resolution) — named actor, reason, before/after state, mandatory audit entry. | BR-306 | Must |
| FR-1124 | Re-award after `AWARD_DECLINED`/`LAPSED`/`VOIDED_INELIGIBLE` — runs the same eligibility gate and ranking as the original auction (DEC-309's cascade or re-auction, whichever is selected). Ops triggers which path applies; ops may **not** hand-pick a specific winning carrier outside the ranked pool (see FR-1128). | BR-301/304, DEC-309 | Must |
| FR-1125 | Waive a charge / approve a claim payout (BR-907) — the distinct ops role BR-907 already mandates, **plus** a second approver above `[NEEDS INPUT: threshold]`, never the same person who processed the original request. | BR-907 | Must |
| FR-1126 | Correct an operational data-entry error (contact info, load metadata) — audited, old value retained, reversible in the log. | derived | Should |
| FR-1127 | Reinstate a suspended/removed carrier — second approver distinct from whoever suspended, since this directly reverses a safety/fraud control. | BR-817 | Must |

**Never overridable — refused outright:**

| ID | Requirement | Traces | Pri |
|---|---|---|---|
| FR-1128 | The eligibility gate (BR-301/803) may **never** be bypassed to force-award to a carrier that failed it for that load, at any tier. **This is the override this spec refuses to build.** It would directly defeat the negligent-selection defence the whole mechanism exists to construct (DEC-LOCK-001, *Montgomery*), and is the cleanest insider-fraud vector available — a rogue ops actor routing an ineligible, colluding carrier onto a load, indistinguishable from legitimate override without this rule. | DEC-LOCK-001, BR-301/803/814 | Must |
| FR-1129 | A captured POD/BOL signature, or the award's selection record (BR-303), is never edited or deleted — annotate/append only, preserving Carmack evidentiary integrity. | BR-809/819 | Must |
| FR-1130 | A closed auction's ranked bid order or winner determination is never re-ordered after the fact. A wrong result is corrected only by a new, separately-logged event (void + re-auction/cascade), never by editing history. | BR-303/305 | Must |
| FR-1131 | No ops actor approves their own override, waiver, carrier-approval, or reinstatement — segregation of duty is structural, not a training policy. | derived, insider-fraud control | Must |

## 5. Support impersonation

F1 owns the mechanism (auth/session). F11 owns the workflow and its limits.

| ID | Requirement | Traces | Pri |
|---|---|---|---|
| FR-1132 | Initiation requires target user, scope (whole-account read vs. one named load), and a reason. Session is time-boxed (`[NEEDS INPUT: duration]`), auto-expires. | derived, → F1 | Must |
| FR-1133 | For an org user, impersonation requires consent captured per session. `[NEEDS INPUT: implicit-via-ToS at account creation vs. explicit per-session opt-in prompt to the user — a product/legal decision, not F11's to default]`. | derived | Must |
| FR-1134 | Read-only by default. Any mutating action taken while impersonating requires a separate, explicit "acting on behalf of user X, ticket Y" confirmation, logged distinctly — never disguised as the user's own act. | audit integrity | Must |
| FR-1135 | Impersonation never performs an identity-bound action: accepting an award (BR-902), signing a POD (BR-903), changing payee-of-record (BR-909), changing banking/remit (BR-812). These stay blocked under impersonation regardless of scope granted. | BR-902/903/909/812 | Must |
| FR-1136 | The consignee holds no account (spine §2); "support view" for a consignee means viewing the content behind their tokenised delivery link as they see it, not impersonating a login that does not exist. | spine §2 | Must |

## 6. Claims intake and collections support

Does not duplicate F6/BRD A6 pricing or A8 adjudication — F11 owns intake, triage, and the ops-facing
tracking surface.

| ID | Requirement | Traces | Pri |
|---|---|---|---|
| FR-1137 | Intake captures BR-807's §370.3 minimum content (shipment identity, liability assertion, amount) from shipper submission, carrier dispute, or consignee relay (BR-906). F11 owns intake/triage/tracking; A8 owns adjudication (spine §6). | BR-807/906 | Must |
| FR-1138 | Every open claim's 30/120/60-day obligation clock (§370.5/.9) surfaces as an auto-escalating case (FR-1107) as it nears deadline; the statutory floor is never configurable downward (BR-808). | BR-807/808 | Must |
| FR-1139 | Intake separates freight disputes from money disputes (BR-811), routing each to its owning path (A8 liability, F6 money) — F11 does not determine liability or amount. | BR-811 | Must |
| FR-1140 | Collections surface shows F6-flagged aged receivables/payables; F11 provides contact-attempt logging, dispute-hold flagging, escalation-to-external-collections triggers (`[NEEDS INPUT: process/agency]`) — never computes charge amounts or invoice content (F6's domain). | derived, spine §6 | Should |
| FR-1141 | The charge-waiver action (FR-1125) is initiated from either the exception queue or the collections surface and always writes back to the linked invoice/case — one source of truth, not two records that can drift. | BR-907 | Must |

## 7. Configuration management

| ID | Requirement | Traces | Pri |
|---|---|---|---|
| FR-1142 | A governed surface represents the eleven open auction parameters (DEC-302..312 — open/sealed bidding, standing-price vs. rank-only, duration, anti-snipe vs. hard close, reserve/ceiling, whether a shipper may decline the winner, early close, decline-cascade vs. re-auction, thin-market degradation, minimum decrement, overnight/weekend/holiday close) as versioned settings, not code constants. | DEC-302..312 | Must |
| FR-1143 | A parameter change never silently alters terms bidders already committed to: values lock at `PUBLISHED`; changes apply to auctions not yet published, unless the parameter is itself a designed runtime behaviour (e.g. anti-snipe extension). | BR-307 (bid = firm commitment) | Must |
| FR-1144 | Every parameter/threshold change is versioned, attributed, reasoned; the version applied to a given auction is stored on that auction's award record (BR-303 already requires "gate version") so a later dispute can prove which rules applied. | BR-303 | Must |
| FR-1145 | The eligibility-gate content (six-tuple thresholds, DEC-201's chosen rigour tier) is a governed setting under the same discipline as FR-1144, changeable only by a role distinct from the vetting-reviewer role (FR-1112) — no reviewer loosens the gate they themselves operate under. | DEC-201, BR-200 | Must |
| FR-1146 | Feature flags (new queue view, new fraud signal, new intake field) are a separate, audited toggle set from business-rule parameters (FR-1142/1145) — a flag ships a code path, a parameter changes a rule; never conflated in one control. | derived | Should |

## 8. Internal reporting

| ID | Requirement | Traces | Pri |
|---|---|---|---|
| FR-1147 | Daily ops reporting surfaces KPI-01 through KPI-17 (BRD §15) with KPI-05..09 — the counter-metrics — rendered at **equal visual weight** to KPI-04 (price), never subordinated: the BRD's own instruction is that price improving while a counter-metric degrades means the design is wrong, which only holds if the counter-metric is actually looked at daily. | KPI-04..09 | Must |
| FR-1148 | The queue itself feeds a "marketplace health" view: open-case count and age by domain tag, fraud cases opened/closed this period, vetting approvals/rejections/overrides this period, claims aging against statutory deadlines. | FR-1102/1107/1109 | Should |
| FR-1149 | Reporting is read-only; no report triggers a business action directly — an ops user acts through the relevant workflow (queue/vetting/fraud/config), keeping "saw a signal" and "acted on it" as separately auditable steps. | audit hygiene | Must |

## 9. Permission shape (feeds F2's matrix — not restated there)

| Role | Action | Resource | Scope |
|---|---|---|---|
| ops-reviewer | claim / work | exception-case | platform_wide |
| ops-vetting-reviewer | approve / reject / hold / conditional | carrier-vetting-case | platform_wide |
| ops-fraud-reviewer | classify / contain | fraud-case | platform_wide |
| ops-senior | second-approve | waiver / reinstatement / gate-override | platform_wide + segregation-of-duty (actor ≠ original requester — an application-level constraint, not a new scope kind) |
| ops-config-admin | edit | auction-parameter / eligibility-gate | platform_wide, distinct from ops-vetting-reviewer (FR-1145) |
| ops-support | impersonate (read-only default) | user-session | platform_wide + consent_recorded (FR-1133) |
| any org user | approve own carrier-vetting-case / own waiver | — | **never granted** (FR-1131) |

## Events (→ F10 owns catalogue/naming)

`case.opened` · `case.claimed` · `case.escalated` · `case.resolved` · `vetting.approved` /
`.rejected` / `.held` · `fraud.classified` · `override.executed` · `waiver.approved` ·
`config.parameter_changed` · `impersonation.started` / `.ended`.

## CHALLENGE

`spine.md` §3 models exceptions as lifecycle **states** on the parent entity. That collapses when two
independent exceptions apply to one load at once — a fraud case and a detention dispute, say — because
a state field holds one value. FR-1100/1101 require `ExceptionCase` as a first-class F3 entity,
referencing the parent, cardinality many-to-one, independent of the parent's own state. This does not
change the lifecycle states themselves — it adds a parallel case layer the queue is built on. Flag for
F3.

## Edge Case register

| ID | Trigger | Behaviour | Who decides | Unresolved? |
|---|---|---|---|---|
| EC-1100 | Two ops users claim the same case near-simultaneously | Optimistic lock; first commit wins, second sees a conflict error (→ F5) | System | No |
| EC-1101 | Claimed case's owner goes inactive, no auto-release threshold set yet | Case ages visibly (time-in-queue keeps counting per FR-1109) | Ops lead | Yes — depends on FR-1106's `[NEEDS INPUT]` |
| EC-1102 | Fraud case and reinstatement request open on the same carrier at once | Reinstatement request blocks/links to the open fraud case; cannot resolve independently | Fraud reviewer must classify/close first | No |
| EC-1103 | An override is attempted on a load already under litigation hold (BR-819) | Override proceeds but the hold status is force-surfaced in the audit entry | System enforces field; counsel decides disclosure scope | Yes |
| EC-1104 | Impersonation requested on a user who is the subject of an open fraud case against their own account | Blocked while the fraud case is open — support access could taint or tip evidence | System rule | No |
| EC-1105 | Config parameter change submitted while several auctions are `AUCTION_OPEN` | Per FR-1143, change queues for future auctions only; open ones unaffected | System | No |
| EC-1106 | Second-approver required (waiver/reinstatement/gate-override) but no second qualified person on shift | No safe default — action stalls until a second approver is available | Client staffing model (DEP-900) | Yes, explicitly |
| EC-1107 | Mismatch (BR-221) turns out to be a legitimate substitution the shipper approved out-of-band, unrecorded | Classifies "disclosed-and-revetted," case closes, but the review itself is recorded so it isn't silently ignored | Fraud reviewer | No |
| EC-1108 | A party under active fraud investigation requests their own selection record for legal defence | Release vs. investigation-integrity conflict, no default picked | Counsel + fraud lead | Yes |
| EC-1109 | Ops actor waives a charge on an account they have an undisclosed personal relationship with | Not fully software-detectable beyond FR-1131's role/actor check | Policy/training control, residual | Yes, partially |
| EC-1110 | Eligibility-gate config (FR-1145) proposed before DEC-201 is decided | Gate ships at current default, versioned; surface exists regardless of which DEC-201 option lands | Client (DEC-201) | Yes, carried from A2 |
| EC-1111 | A case's freight-in-motion signal flips mid-review (load moves `AT_PICKUP`→`IN_TRANSIT`) | Re-prioritises live; reviewer isn't relying on a stale snapshot | System | No |
| EC-1112 | Fraud-relevant fact reported via the no-account consignee relay (BR-906/912), not the driver/dock signal (BR-221) | Case opens, tagged unverified-source, corroboration required before classification | Fraud reviewer | No |
| EC-1113 | Overnight/weekend exception volume exceeds informal coverage; freight moves 24/7 | Tooling has no coverage-gap remedy — this is the cost the BRD's A9 flagged as most likely underestimated | Client | Yes, explicitly (DEP-900, RSK-027) |
| EC-1114 | Force-transition override (FR-1123) attempted on a load with an open, unresolved fraud case | Blocked/warned before proceeding — forcing a transition could suppress the evidence the case depends on | System warns; ops user proceeds or stops | No |
| EC-1115 | Two fraud cases on different loads share a carrier pattern (serial double-brokering across lanes) | Pattern view (FR-1118) surfaces it; no auto-classification across cases without a human | Fraud reviewer | Partially — whether a cross-case auto-flag threshold should exist is `[NEEDS INPUT]` |
| EC-1116 | Ops user attempts to view impersonation session content after it auto-expired | Session dead, no replay of live actions; only the audit log (actions taken, not screens seen) survives | System | No |
| EC-1117 | A carrier disputes a suspension that was itself the output of an override chain (suspended via a fraud case that was itself escalated from an override-blocked force-transition) | Full chain must be reconstructable from linked case/audit records (FR-1110) for the dispute to be answerable at all | Ops senior / A8 dispute path | No |

---

**Word budget note:** tables dense by design per hard rule §8.5. FR count: 50 (FR-1100–1149). EC count: 18 (EC-1100–1117). `[NEEDS INPUT]` count: 12.
