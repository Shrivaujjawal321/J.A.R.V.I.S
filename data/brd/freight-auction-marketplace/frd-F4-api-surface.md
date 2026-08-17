# FRD-F4 — API Surface & Integrations

**ID block: 400-499 (`API-`, `INT-`, `EVT-`, `EC-`).** Inherits frd-spine §4 unchanged: `/v1` base,
resource-oriented nouns, idempotency keys on mutating calls, cursor pagination, trace id per response,
canonical error envelope, `<entity>.<past_tense>` events. Domain semantics (auction rules, HOS,
liability) belong to the owning sibling (F2/F3/F5/F6/F7/F8) — F4 is the wire contract, traced to BRD
`BR-`/`OBJ-`.

## 1. Three consumer classes — where they genuinely diverge

| Class | Auth carrier | Payload shape | Pagination | Failure mode designed for |
|---|---|---|---|---|
| **Web** (shipper/carrier/ops) | Bearer session/JWT (→ F1) | Full resource, rich forms | Cursor, filter, sort | Standard timeout/retry |
| **Driver mobile, poor connectivity** | Bearer JWT, long refresh | Minimal fields, compressed images, batched arrays | None — own trip only | **Offline queue**: client persists + client-generated key, flushes on reconnect; server accepts late arrivals, reconciles by sequence, never blind-overwrites |
| **Server-to-server** (TMS, factoring, accounting) | API key+HMAC or OAuth2 client-credentials `[NEEDS INPUT]` | Strict schema, additive-tolerant | Bulk cursor GET, webhook preferred | Middleware retry storms — idempotency-key mandatory |

Mobile has no "list loads" — only the assigned trip (`API-431`). Deliberate payload minimisation.

## 2. Endpoint catalog

Consumers: **W**=web, **M**=driver mobile, **S**=server-to-server, **C**=tokenised/no-auth,
**O**=platform ops (elevated role, → F2). Idem = idempotency-key required.

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
| API-440 | `POST /v1/trips/{id}/positions` | Batched position ingest (→ F8) | M,S | seq-dedup, not key | BR-401 |
| API-441 | `GET /v1/trips/{id}/eta` | Derived ETA (→ F8) | W,S | — | §8.4 |
| API-442 | `GET /v1/track/{token}` | Read-only tracking, tokenised, expiring | C | — | spine §2 |
| API-445 | `POST /v1/documents` | Upload BOL/COI/authority, image-tolerant | W,M,S | Y | §8.5/§8.2 |
| API-446 | `GET /v1/documents/{id}` | Retrieve document | W,M,S,O | — | §8.5/§8.2 |
| API-447 | `POST /v1/trips/{id}/pod` | Structured POD capture incl. OS&D fields | M | **Y, mandatory** | BR-500–509 |
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
| API-468 | `GET /v1/loads/{id}/eligibility?carrier_id=` | Pre-bid self-check, 6-element tuple | W,S | — | BR-200 |
| API-469 | `POST /v1/carriers/{id}/suspend`, `/reinstate` | Graduated enforcement | O | Y | BR-817/818 |
| API-470 | `POST`\|`GET /v1/drivers` | CDL/class registry (→ F7) | W | — | BR-210 |
| API-471 | `POST`\|`GET /v1/equipment` | Tractor/trailer registry — type, VIN, policy | W | — | BR-209 |
| API-472 | `PATCH /v1/equipment/{id}/availability` | Time-windowed lock/release | W,S | — | BR-214/215 |
| API-475 | `GET /v1/notifications` | In-app feed, cursor (→ F10 content) | W,M | — | §7.3 |
| API-476 | `POST /v1/webhooks` | Server-to-server event subscription mgmt | S | — | §4 |
| API-477 | `GET /v1/webhooks/{id}/deliveries` | Delivery log, on-demand replay | S | — | §4 |
| API-480 | `GET /v1/admin/exceptions-queue` | Cross-domain exception desk feed | O | — | §7.3 |
| API-481 | `POST /v1/admin/overrides` | Gate/award override, named + reasoned | O | Y | BR-306 |
| API-482 | `GET /v1/admin/audit-log` | Every mutating action, actor+time | O | — | §8.9 |
| API-485 | `GET /v1/reports/loads` | Bulk export, filter, cursor | W,S | — | derived |
| API-486 | `GET /v1/reports/settlement` | Reconciliation export | W,S | — | §8.6 |
| API-487 | `GET /v1/reports/licence-register` | BR-1205 data-licence register export | O | — | BR-1205 |

**Not built, on purpose:** a driver "browse loads" feed (§1); a raw `osm.*`-record endpoint anywhere
(DEC-1200 — `API-441`'s ETA/routing signals return an aggregated corridor summary, never OSM rows); a
bidder-visible rival-identity field on `API-412` (BR-314).

## 3. Idempotency — where a duplicate is materially harmful

Rule: `Idempotency-Key` header, scoped per (org, endpoint, key). Replay, same body → original
response unchanged. Replay, **different** body, same key → `409 IDEMPOTENCY_KEY_REUSED` (taxonomy →
F5). Retention `[NEEDS INPUT: TTL, ≥24h per spine floor]`.

| Endpoint | Harm if duplicated | Semantics |
|---|---|---|
| `API-411` bid | Phantom price in the pool | Replay = no-op, returns original bid |
| `API-421` award accept | Races a decline/lapse | Re-gates every attempt; only first success binds |
| `API-447` POD capture | Duplicate/overwritten delivery evidence | Replay returns original; a *distinct* 2nd capture on already-`POD_CAPTURED` is `409` |
| `API-432` custody events | Phantom pickup from mobile retry | Mandatory — primary offline-queue endpoint |
| `API-456`/`API-460` dispute/claim | Inflated exposure | Replay returns original claim/dispute ID |
| `API-440` positions | High-frequency, header-per-ping wasteful | Dedup by client sequence number, not header |

## 4. Concurrency

| Scenario | Mechanism | Outcome |
|---|---|---|
| Two bids, same instant | Not a conflict — both persist; ranking deterministic at close (BR-304/305) | None; only a retried bid is deduped (§3) |
| Award races a withdrawal | Optimistic lock; award-commit re-checks load state in-transaction | `409 LOAD_WITHDRAWN` if withdrawal committed first (→ F5) |
| Load amended while bids open | `API-402` PATCH checks `bid_count == 0` via version field | `409 LOAD_HAS_BIDS` → withdraw-and-republish path (BR-136) |
| POD submitted twice, different content | State guard: trip already `POD_CAPTURED` | 2nd distinct submission is `409`; correction = `API-449` addenda only |
| Mobile posts a stale regression (e.g. `IN_TRANSIT` after `DELIVERED`) | Sequence/version check on `API-431` | `409 STALE_STATUS_TRANSITION`; client re-fetches, re-files as exception |

## 5. Events (F4 owns webhook transport; F10 owns notification content/channel)

Delivery: at-least-once, signed, `schema_version` field so additive changes don't break subscribers;
retry/backoff/max-attempts `[NEEDS INPUT]`; failed deliveries logged at `API-477`, replayable.

| ID | Event | ID | Event | ID | Event |
|---|---|---|---|---|---|
| EVT-400 | `load.published` | EVT-410 | `custody.transferred` | EVT-420 | `invoice.finalised` |
| EVT-401 | `load.amended` | EVT-411 | `trip.status_changed` | EVT-421 | `payment.settled` |
| EVT-402 | `load.withdrawn` | EVT-412 | `transit.exception_raised` | EVT-422 | `claim.opened` |
| EVT-403 | `load.cancelled` | EVT-413 | `pod.captured` | EVT-423 | `claim.decided` |
| EVT-404 | `auction.opened` | EVT-414 | `pod.addendum_added` | EVT-424 | `dispute.opened` |
| EVT-405 | `auction.closed` | EVT-415 | `delivery.refused` | EVT-425 | `dispute.resolved` |
| EVT-406 | `bid.placed` | EVT-416 | `rate_confirmation.acknowledged` | EVT-426 | `carrier.suspended` |
| EVT-407 | `bid.withdrawn` | EVT-417 | `award.declined` | EVT-427 | `carrier.reinstated` |
| EVT-408 | `load.awarded` | EVT-418 | `award.lapsed` | EVT-428 | `document.uploaded` |
| EVT-409 | `award.accepted` | EVT-419 | `award.voided` | EVT-429 | `document.verified` |

## 6. Integrations (capability, never vendor)

**Inbound**

| ID | Capability | Consumes at | Note |
|---|---|---|---|
| INT-400 | FMCSA authority/safety data (SAFER, CSA/SMS) | `API-465/467/468` | BR-201/205 |
| INT-401 | Insurance certificate verification | `API-467` | BR-204/804, insurer-sourced, never carrier-supplied PDF |
| INT-402 | ELD/telematics position & HOS signal | `API-440` | **F7's planning-vs-compliance-record fork (spine §7)** — not a compliance system of record |
| INT-403 | Document capture / OCR | `API-445` | BOL/POD/COI extraction |
| INT-404 | Payment & factoring remittance | `API-458` | NOA-gated routing, BR-606–608 |
| INT-405 | Mapping & truck-legal routing | `API-441`, `API-468` | Truck-intel platform candidate (DEC-LOCK-002); **ODbL never crosses boundary** (§2) |
| INT-406 | Identity / KYB (EIN, signer) | `API-465` | BR-104/208 |
| INT-407 | SMS/push delivery | `EVT-*` transport | → F10 |
| INT-408 | Email delivery | `EVT-*` transport | → F10 |
| INT-409 | Weather/work-zone/chain-control feed | `API-441` | Several feeds `Unverified` (A11/A12) — cleared sources only (BR-1209) |

**Outbound**

| ID | Capability | Exposes | Note |
|---|---|---|---|
| INT-420 | Shipper TMS | `API-400/401/403`, `EVT-400/408/413` | Load posting + status by API, not screen |
| INT-421 | Carrier TMS | `API-415/424`, `EVT-406/408/409` | Bid feed + award push, trip pull |
| INT-422 | Accounting/ERP export | `API-457/486` | Invoice/settlement, W-9/1099 (→ F6) |
| INT-423 | Factoring NOA verification | `API-467`, `INT-404` | Signed-NOA-only routing, BR-607 |

## 7. Versioning & deprecation

`/v1` is the only live version. A breaking change (field removal/rename, semantics change, error-code
reuse — forbidden per spine §4) ships as `/v2`, parallel-served for a deprecation window
`[NEEDS INPUT: length]`, announced via `Deprecation`/`Sunset` headers + changelog. An **additive**
change (optional field, event, open-set enum value) ships in place — `API-476` subscribers must
tolerate unknown fields by contract. Event payloads carry their own `schema_version`, independent of
the API version, so a webhook consumer isn't forced to re-version on every API bump.

**CHALLENGE:** the mobile offline queue (§1) means a `TRANSIT_EXCEPTION`-worthy "no status update"
(BR-401) can be a real physical gap or a connectivity gap that resolves on reconnect. If F4 silently
clears the flag on reconnect, F8's exception record understates real gaps in poor-coverage lanes; if
it never clears, every rural lane looks exception-prone. **F8's call, not F4's** — flagged because the
accept-late-vs-reject API choice creates the ambiguity.

## 8. Edge case register

| ID | Trigger | Behaviour | Who decides | Unresolved? |
|---|---|---|---|---|
| EC-400 | Idempotency key replayed w/ different body, or reused across endpoints | `409 IDEMPOTENCY_KEY_REUSED` | F4 | No |
| EC-401 | Award accepted after acceptance window lapses (BR-309) | `409` → `AWARD_LAPSED` cascade | F3/F6 own window value | Value `[NEEDS INPUT]` |
| EC-402 | COI lapses mid-auction, bid already placed | Rejected at submission, never ranked (BR-301) | F2/A2 | No |
| EC-403 | Cursor references a since-withdrawn load | Resolves (tombstone), marked withdrawn in payload | F4 | No |
| EC-404 | Bulk export times out mid-stream | Resumable via cursor, not restart-from-zero | F4 | Caps `[NEEDS INPUT]` |
| EC-405 | Webhook subscriber down past retry exhaustion | Failed delivery visible + replayable, no silent drop | F4 | Retry policy `[NEEDS INPUT]` |
| EC-406 | Position batch arrives out of order | Later sequence applied; stragglers appended, never overwrite current | F4/F8 | No |
| EC-407 | Tokenised consignee link reused after expiry | `410 GONE`; fresh link reissued via `API-431` | F4 | Expiry `[NEEDS INPUT]` |
| EC-408 | Second party attempts to sign an already-signed token | Rejected; correction = `API-449` addenda only | F4/A5 | No |
| EC-409 | Rate limit exceeded mid-run | `429` + `X-RateLimit-Reset` | F4 | Limits `[NEEDS INPUT]` |
| EC-410 | S2S client presents expired API key | `401`, no partial batch processing | F1/F4 | No |
| EC-411 | Uploaded document fails OCR / malformed / oversized | `status=UNPROCESSED`, human-review flag, never dropped | F4/INT-403 | Size cap `[NEEDS INPUT]` |
| EC-412 | Mobile clock skew on a custody timestamp | Server receipt time + device-asserted time both retained, flagged | F4/F7 | Feeds F7's HOS tension (§7) |
| EC-413 | `pod.addendum_added` fires after `pod.captured` delivered | Consumer must reconcile, never assume first event final | F4/A5 | No |
| EC-414 | Regulatory change forces a breaking change mid-deprecation-window | `/v2` ships early, window shortened, notice given | F4 + client relations | Notice period `[NEEDS INPUT]` |
| EC-415 | Integrator requests raw ODbL routing records | Hard-refused, no per-partner exception (DEC-1200) | F4 (enforces A12) | No |
| EC-416 | Mobile queue flushes a multi-day dead-zone backlog on reconnect | Applied by sequence; silent interval stays flagged, not cleared (§7) | F8 | **Yes** |
