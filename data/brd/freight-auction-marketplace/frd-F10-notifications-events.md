# F10 — Notifications, Events & Messaging

*ID block 1000-1099. Owns: event catalog, notification matrix, delivery semantics,
preferences/suppression, outbound webhook catalog+semantics, auditability. Not here: transport/HMAC
mechanics (→ F4), error taxonomy (→ F5), who may trigger an action (→ F2), preference/notification
screens (→ F9). Events named `<entity>.<past_tense_event>` per frd-spine §4, one per BRD §7.4 state
transition unless noted. `Src` column = BR-/state trace.*

## 1. Event catalog & notification matrix

**Tier**: T0 critical (overrides quiet hours, may use voice) · T1 high (real-time, quiet-hours
aware) · T2 normal (real-time best-effort) · T3 digest-default (§3). **Channels**: `IA` in-app ·
`PU` push · `SMS` · `EM` email · `VO` voice call · `OOB` out-of-band, consignee's supplied contact
only (BR-912) · `DG` digest-routed · `—` not notified. **Personas**: `Shpr` shipper (poster+admins,
BR-911) · `Disp` carrier dispatcher · `Drv` driver · `Ops` platform-ops · `Cnsg` consignee.

| EVT | Event | Tier | Shpr | Disp | Drv | Ops | Cnsg | Src |
|---|---|---|---|---|---|---|---|---|
| 1000 | load.published | T3 | IA | — | — | — | — | BR-110/130 |
| 1001 | auction.opened | T3 | IA | DG¹ | — | — | — | spine §3 |
| 1002 | bid.submitted | T3 | DG | IA | — | — | — | BR-301/307 |
| 1003 | bid.rejected_ineligible | T2 | — | IA,EM | — | — | — | BR-301/200 |
| 1004 | auction.closed | T3 | IA | DG | — | — | — | spine §3 |
| 1005 | award.determined | T1 | — | IA,PU | — | DG | — | BR-303 |
| 1006 | award.confirmed | **T0** | IA,EM | IA,PU,SMS,EM;VO² | — | DG | — | BR-302/303 |
| 1007 | award.declined | T1 | IA,EM | IA | — | IA | — | BR-905 |
| 1008 | award.lapsed | T1 | IA,EM | IA,PU | — | IA | — | BR-309 |
| 1009 | award.voided_ineligible | **T0** | IA,EM | IA,PU,SMS | — | IA,SMS | — | BR-302 |
| 1010 | award.accepted | T1 | IA,EM | IA | — | — | — | spine §3 |
| 1011 | rate_confirmation.issued | T1 | IA | IA,PU,EM³ | — | — | — | BR-600 |
| 1012 | pickup.scheduled | T2 | IA,EM | IA,PU,SMS | PU,SMS | — | — | BR-114 |
| 1013 | pickup.identity_mismatch | **T0** | — | IA,SMS | PU,SMS | IA,SMS,VO | — | BR-221/406 |
| 1014 | pickup.shipper_not_ready | T1 | IA,SMS | IA,PU,SMS | PU,SMS | IA | — | BR-143 |
| 1015 | pickup.carrier_no_show | **T0** | IA,SMS,VO | IA,SMS | — | IA,SMS | — | BR-142 |
| 1016 | pickup.refused | T1 | IA,SMS | IA,PU | PU | IA | — | spine |
| 1017 | load.picked_up | T2 | IA,EM | IA,PU | PU | DG | OOB⁴ | BR-400 |
| 1018 | shipment.in_transit | T3 | DG | IA | — | DG | — | spine |
| 1019 | shipment.status_updated | T3 | DG | DG | — | DG | — | BR-401 |
| 1020 | shipment.status_overdue | T1 | IA | IA,PU,SMS | — | IA,SMS | — | BR-401 |
| 1021 | transit.exception_reported | T1/T0⁵ | IA,EM | IA,PU,SMS | PU,SMS | IA,SMS | OOB⁵ | BR-405 |
| 1022 | custody.transferred | T1 | IA,EM | IA,PU | PU | IA | OOB | BR-402 |
| 1023 | truck.arrived_at_drop | T2 | DG | IA | — | — | OOB | spine |
| 1024 | delivery.attempted_no_receiver | **T0** | IA,SMS,EM | IA,PU,SMS | PU | IA | OOB,SMS/VO | BR-509 |
| 1025 | delivery.completed | T1 | IA,EM | IA,PU | PU | DG | — | spine |
| 1026 | delivery.refused | **T0** | IA,SMS,EM | IA,PU,SMS | PU | IA,SMS | — | spine |
| 1027 | delivery.partial_accepted | T1 | IA,EM | IA,PU | — | IA | — | spine |
| 1028 | pod.captured | T1 | IA,EM | IA,EM | — | DG | OOB⁶ | BR-500/501 |
| 1029 | shipment.returned_to_origin | T1 | IA,EM | IA,PU | PU | IA | — | spine |
| 1030 | cargo.exception_reported | **T0** | IA,SMS,EM | IA,SMS | PU | IA,SMS,VO | OOB | BR-820 |
| 1031 | cargo.recovery_opened | T1 | IA,EM | IA | — | IA | OOB | A8 |
| 1032 | fraud.suspected | **T0**⁷ | — | — | — | IA,SMS,VO | — | A8 §8.9.7 |
| 1033 | carrier.suspended_in_flight | **T0** | IA | IA,PU,SMS | — | IA,SMS | — | A8 §8.9.10 |
| 1034 | claim.opened | T1 | IA,EM | IA,EM | — | IA | via Shpr relay | BR-807 |
| 1035 | claim.obligation_due | T1/T0⁸ | DG | DG | — | IA,EM | — | BR-807 |
| 1036 | dispute.opened | T1 | IA,EM | IA,EM | — | IA | via Shpr relay | spine |
| 1037 | dispute.closed_unresolved | T1 | IA,EM | IA,EM | — | IA | via Shpr relay | spine |
| 1038 | load.cancelled | T1/T0⁹ | IA | IA,PU,SMS,EM | PU,SMS | IA | OOB if post-pickup | BR-138/139/144 |
| 1039 | load.withdrawn | T1 | IA | IA,PU,EM | — | — | — | BR-136/138 |
| 1040 | invoice.issued | T2 | IA,EM | IA,EM | — | — | — | BR-601 |
| 1041 | invoice.line_held | T1 | IA,EM | IA,EM | — | DG | — | BR-602/603 |
| 1042 | invoice.settled | T2 | IA,EM | IA,EM | — | DG | — | BR-603 |
| 1043 | shipment.completed | T3 | DG | DG | — | DG | — | spine |
| 1044 | carrier.eligibility_lapsed | T1 | — | IA,PU,SMS,EM | — | DG | — | BR-217 |
| 1045 | carrier.document_expiring | T2 | — | IA,EM,DG | — | DG | — | BR-220 |
| 1046 | payee_of_record.changed | **T0** | — | IA,EM (old+new) | — | IA,SMS | — | BR-909/812 |
| 1047 | consignee.notice_delivery_unknown | T2, internal | — | — | — | DG | (unreached) | BR-912 |
| 1048 | webhook.subscription_unhealthy | T1, internal | IA if subscriber | IA if subscriber | — | IA,EM | — | §5 |

¹ digest unless real-time-subscribed. ² voice only if undelivered within ack window (§5). ³ ack
required before `PICKUP_SCHEDULED`. ⁴ first consignee touch, establishes ETA. ⁵ T0 only for safety
sub-types (accident/breakdown/HOS/theft/OOS); weather is T1; consignee told only if ETA changes.
⁶ bundles BR-714 notice if not already sent at 1017/1021. ⁷ restricted fanout, never reaches
suspect/counterparty (BR-225); consequence gets its own event. ⁸ escalates to `Ops` only when
overdue. ⁹ T0 only post-dispatch/pickup (BR-142/144); pre-award is routine.

## 2. Channel semantics

| Channel | Fits | Constraint |
|---|---|---|
| In-app | Desk-based Shpr/Disp/Ops | Audit floor — every event gets an IA record regardless of primary channel |
| Push | Mobile Disp/Drv | Needs app installed; degrades to SMS if not |
| SMS | Drv in cab, Cnsg, T0/T1 fallback | **Regulated act on a US number** — consent, sender ID, opt-out. Regime → BRD §8.7 A7 (BR-714/716), §7.9-6. `[NEEDS INPUT: consent-capture point]` |
| Email | Everyone with an address | Carries BR-714 notice text on first consignee contact |
| Voice | T0 only (§3) | Never for T2/T3 |
| Webhook | Integrated shipper/carrier systems | Signing → F4; catalog/semantics → §5-7; grant → F2; screen → F9 |
| OOB | Consignee only | Only channel available — no login to push into (spine §2) |

## 3. Urgency tiers

| Tier | Meaning | Quiet hours | Retry |
|---|---|---|---|
| T0 | Load uncollected / custody-safety / fraud / payment-diversion risk if missed | **Overrides**, incl. voice | Escalate channel-by-channel until acked; ops paged on exhaustion |
| T1 | Changes what recipient must do next | Respected, bounded delay `[NEEDS INPUT]` | Standard (§5) |
| T2 | Actionable, not urgent | Respected fully | Best-effort, no escalation |
| T3 | Routine/high-frequency/confirmatory | Batched (§6) | Digest job owns delivery |

## 4. Preferences, quiet hours, suppression

Each account-holding persona sets channel preference + quiet-hours window per channel
(`[NEEDS INPUT: default window, org- vs. user-level]`). **T0 overrides every suppression setting
without exception** — the one class quiet hours cannot touch. A recipient cannot opt out of T0 on
every channel at once; onboarding/award-acceptance blocks until ≥1 T0-reachable channel exists
(enforcement → F2). The consignee has no preference surface — its only lever is the contact the
shipper supplied; SMS consent/opt-out mechanics remain `[NEEDS INPUT]` per §2.

## 5. Delivery semantics

At-least-once on every channel except webhooks (dedup, §7); in-app is the idempotent record.
**Ordering:** each event carries the shipment's monotonic sequence number; a consumer seeing a
lower-seq event after a higher one discards and refetches — resolves the named award/cancellation
race. **Dedup:** idempotency key = stable `event_id`, reused on redelivery (header shape → F4).
**Retry/backoff:** exponential, bounded, tier-dependent — `[NEEDS INPUT: interval, multiplier, cap,
max attempts]`. **Dead-letter:** T0/T1 max-attempt failures raise an `Ops` alert, never vanish;
T2/T3 log without paging. **Silent-failure — the money case:** a missed `award.confirmed` is an
uncollected load. Every T0/T1 attempt tracks `PENDING→SENT→DELIVERED|FAILED|UNKNOWN` (email
open-tracking is `UNKNOWN`, never inferred read). No delivered-or-better status within
`[NEEDS INPUT: ack window]` auto-escalates `award.confirmed` to voice and pages `Ops`. API errors
use the canonical envelope → F5.

## 6. Digests vs. real-time

T3 events, and T2 for digest-opted users, batch per persona instead of firing individually —
answers "a dispatcher watching six auctions doesn't want six hundred pings." Frequency
`[NEEDS INPUT: interval — likely shipper-daily, dispatcher-hourly during active auctions]`. T0/T1
always bypass the digest; a digest delivery gets the same status tracking as §5.

## 7. Outbound webhooks

Any EVT- in §1 is subscribable, scoped to the subscribing org's own visible shipments (spine §2) —
never cross-org. `fraud.suspected` (1032) is never webhook-subscribable, matching its restricted
human fanout.

| Concern | Requirement | Owner |
|---|---|---|
| Signing | Verifiable origin, rotatable secret | Mechanics → F4 |
| Replay | Timestamp+nonce; reject stale beyond `[NEEDS INPUT]` window | Mechanics → F4 |
| Retry | Same posture as §5, subscriber-scoped | This doc |
| Subscriber failure | N fails (`[NEEDS INPUT]`) → unhealthy (EVT-1048), pauses, notifies admin, resumable, no silent drop | This doc |
| Versioning | Schema version on payload; additive-only per version; breaking = new version, old kept serving | Convention → F4 |
| Subscribe grant / UI | — | F2 / F9 |

## 8. Auditability

Every notification attempt, any channel/persona incl. OOB, logs immutably: `event_id`, recipient,
channel, content version, sent time, delivery status, read/ack time where supported. Retained at
least as long as the shipment record (→ BRD A7 retention table) — "was this party notified" is
evidence in a Carmack claim or negligent-selection dispute (BR-820). The platform never fabricates
a confirmed-read state for the consignee — absent a carrier-level receipt the honest record is
`consignee.notice_delivery_unknown` (EVT-1047, consumes BR-912). Log is queryable independent of
any third-party channel provider's own retention.

## 9. Functional requirements

| FR | Requirement | Traces | Acceptance |
|---|---|---|---|
| FR-1000 | Every §7.4 transition emits exactly one EVT- per §1. | BR-all | §7.4↔§1 mapping complete. |
| FR-1001 | `award.confirmed` escalates per §5 if not delivered within the ack window. | BR-303 | No award unconfirmed past window. |
| FR-1002 | Consignee notices never route in-app; unproven delivery recorded, not assumed. | BR-912 | No `Cnsg=OOB` row has an IA/PU fallback. |
| FR-1003 | T0 delivers regardless of quiet-hours/suppression. | §3/§4 | T0 in quiet hours still delivers ≥1 channel. |
| FR-1004 | Multi-poster orgs route load events to the posting user, not only admin. | BR-911 | Poster A gets Poster A's events. |
| FR-1005 | `fraud.suspected` fans out only to fraud/ops. | BR-225 | No counterparty channel carries EVT-1032. |
| FR-1006 | Every attempt logged (recipient/channel/status/time), retained per A7. | BR-820 | Audit query returns full attempt history. |
| FR-1007 | Webhook subscriptions scope strictly to subscriber's own org. | spine §2 | Cross-org delivery structurally impossible. |
| FR-1008 | Out-of-sequence deliveries discarded, not applied. | task brief | Out-of-order test never regresses state. |
| FR-1009 | Driver content available in English/Spanish minimum. | BR-914 | Spanish driver gets Spanish content. |
| FR-1010 | `payee_of_record.changed` notifies old+new, pages ops pre-effect. | BR-909/812 | No payee change routes without dual notice + ops event. |

## 10. Edge case register

| EC | Trigger | Behaviour | Who decides | Unresolved? |
|---|---|---|---|---|
| EC-1000 | Consignee OOB contact bounces | Falls to `notice_delivery_unknown`; shipper prompted to correct | Ops/Shpr | Yes — re-contact SLA `[NEEDS INPUT]` |
| EC-1001 | Driver has no signal on a T0 event | SMS queues per carrier retry; can't force delivery | Carrier | Yes — blackout tolerance `[NEEDS INPUT]` |
| EC-1002 | Award/cancellation delivery race | Sequence-discard + refetch (§5) | — | No |
| EC-1003 | Webhook subscriber down on a T0 event | Retry → unhealthy; human channels proceed independently | — | No |
| EC-1004 | SMS consent revoked/never captured (consignee) | SMS suppressed, falls to EM/VO; regime → A7 | Counsel (§7.9-6) | **Yes — [NEEDS INPUT]** |
| EC-1005 | HOS-exhaustion event, no stored ELD (frd-spine §7) | Fires from self-report/derived signal only, never stored ELD | F7 / this doc | Yes — depends on F7's DEC- |
| EC-1006 | Consignee has no channel for claim status | Relayed via shipper (BR-906); no direct channel | A5/A8, this doc | Yes — mirrors BR-906 |
| EC-1007 | Award to broker whose sub-carrier executes | Broker gets commercial events; driver/dispatcher get fulfilment events | A2 tuple model | No |
| EC-1008 | Voice escalation reaches an off-duty driver mid-HOS-reset | Attempted anyway — only defined T0 set uses voice | F7/client ops | Yes — `[NEEDS INPUT]` policy |

**CHALLENGE:** none filed — §7.4 was sufficient to derive the catalog without a new lifecycle
state; the two meta-events (1047, 1048) are operational, not business states, so they sit outside
the transition rule rather than contest it.

**What this domain cannot do:** invent quiet-hours windows, retry/backoff counts, digest intervals,
or ack-window durations (no invented numbers); resolve SMS/voice consent and opt-out mechanics for
a US phone number (counsel, BRD §7.9-6); decide whether voice escalation to an off-duty driver is
acceptable policy (client operations, EC-1008).
