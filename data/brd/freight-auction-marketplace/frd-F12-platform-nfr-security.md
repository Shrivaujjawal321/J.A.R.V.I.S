# F12 — Platform NFRs: Security, Tenancy Isolation, Availability, Observability, DR

**Agent F12. ID block 1200-1299.** Traces to BRD `OBJ-006` (trustworthy under fraud pressure),
`OBJ-007` (lawful across regimes), and A7/A9/A12's BRD-phase NFRs (701-712, 900-901, 1200) — carried
forward, not restated. F2 owns the permission model; this section owns that it cannot be bypassed
beneath it.

---

## 1. Tenant isolation — the highest-severity property in this system

A shipper seeing a competitor's freight, or a carrier seeing a rival bid, ends the business.
Isolation holds **beneath** F2's RBAC — every layer below the API independently refuses cross-org
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
| NFR-1207 | **Errors & diagnostics** | An error body, stack trace, or debug payload — to a client or an error tracker — never carries another tenant's identifiers, freight, bids, or PII; the canonical error envelope (frd-spine §4) is sanitized before serialization | Every documented error path (`→ F5`) contract-tested for foreign `org_id`/entity leakage; fuzz malformed input for stack-trace leaks |
| NFR-1208 | Support/impersonation tooling | "View as" a tenant is session-scoped, time-boxed, reason-coded — never a standing credential | 100% of sessions logged: actor, target org, reason, duration (`→ F11`) |
| NFR-1209 | Shared compute | No worker/queue message processes two tenants without re-deriving scope per unit of work — never inherits caller's ambient scope | Poisoned job cannot pull unscoped data |

**CHALLENGE:** frd-spine §3's five scope kinds don't cover NFR-1206 — cross-org, de-identified,
threshold-gated comparative reporting (in scope via BRD A6/A10). Proposing a sixth:
`aggregate_threshold`. Flagged for F2/assembler, not invented unilaterally.

---

## 2. Availability — tiered by consequence

BRD A2's rule holds: a data problem never auto-aborts a physical trip. All numeric targets
`[NEEDS INPUT]`; the tiering and degradation contract is not optional even before numbers exist.

| ID | Tier | Example | Degradation when a dependency is down |
|---|---|---|---|
| NFR-1210 | 0 — physical-blocking | POD/BOL capture, custody handover, driver/truck assignment lookup | Offline-capable local capture, client-timestamped, syncs on reconnect — never blocks a truck at the dock |
| NFR-1211 | 1 — auction-critical | Bid submission, auction close, award | Close **extends** rather than closing on an unreliable clock (`→ F6`); never award on partial data |
| NFR-1212 | 2 — operational | Load publish, eligibility check, notifications | Queue + retry; visible "delayed" beats false success |
| NFR-1213 | 3 — informational | Dashboards, reports, ratings | Stale-data banner acceptable; never blocks Tier 0/1 |
| NFR-1214 | Evidence retrieval (carries BRD NFR-711) | Selection record, audit log, POD on demand | Served off a path architecturally independent of the auction/award path, so a degraded auction never hides a record a party has the right to review (49 CFR 371) |

Every external dependency (safety-data feed, telematics, payment/factoring, notification) needs
documented timeout/retry-backoff/circuit-breaker and a fallback that degrades the *feature*, never
the *trip*. Numbers `[NEEDS INPUT]`.

---

## 3. The 24/7 reality

| ID | Requirement |
|---|---|
| NFR-1215 | No planned maintenance overlaps a known high-load period; zero-downtime rolling deploys for Tier 0/1. Windows `[NEEDS INPUT]` — freight has no universal quiet hour |
| NFR-1216 | Continuous on-call, not business-hours; escalation/paging thresholds `[NEEDS INPUT]`, must exist pre-launch |
| NFR-1217 | Support path for a driver at a dock does not assume desk-hours staffing (`→ F11`) |
| NFR-1218 | Migrations run without locking Tier 0 write paths — backward-compatible given zero acceptable downtime |

---

## 4. Data classes and retention

Carrying A7 §7.7 exactly — fixed periods stay fixed, open periods stay open.

| Class | Period | Fixed by |
|---|---|---|
| Broker transaction record (BR-703, 6 elements) | ≥3 yrs | 49 CFR 371.3 |
| BOL/POD/exception notation | **Open** — claim/suit horizon (Carmack) | — |
| Bid history, selection/award record | **Open**, litigation-evidence value argues long | — |
| Consignee contact data | **Open**, purpose-limited | State statute |
| Driver personal/location data | **Open**, minimise; no ELD/HOS/Clearinghouse/D&A (BRD NFR-710) | State statute |
| Audit log (this section's artefact) | **Open** — NFR-1219: cannot be shorter than the retention of the record it documents | — |
| Security/error logs, telemetry | `[NEEDS INPUT]` — high-volume, needs its own cost/legal review, not a "forever" default | — |
| Backups | `[NEEDS INPUT]`, ≥ live-data retention per class; outliving a record's legal window is itself a compliance question | — |

**NFR-1220 — Legal hold overrides purge.** Any record under litigation hold, claim, or subpoena is
exempt from automated deletion regardless of class; the hold is logged, reversible only by the
authority that placed it (carries BRD `EC-715`).

---

## 5. Privacy for the two populations who never signed up

| ID | Requirement |
|---|---|
| NFR-1221 | Consignee reaches access/deletion/opt-out from the unregistered, tokenised delivery link alone — no account required (carries BRD NFR-709) |
| NFR-1222 | Driver rights requests route through the employing carrier for data the platform doesn't hold directly (HOS-adjacent, out of scope per NFR-710); a direct path exists for what the platform does hold (assignment history, in-trip location) |
| NFR-1223 | **Deletion vs. evidentiary retention** (carries BRD `EC-711`, unresolved by counsel there — restated as an enforceable pattern): a request against a record inside its 371.3 window, under legal hold, or evidence for an open claim is not auto-honoured; system supports a distinct **retained-restricted** state — held for lawful purpose, suppressed from support view/analytics/marketing |
| NFR-1224 | Location data minimised to active-trip need; retained-trip-history period is a separate `[NEEDS INPUT]`, distinct from the transaction record it supports |
| NFR-1225 | Third-party processors (background check, telematics, payment/factoring) bound by terms matching this section's class-level retention/deletion — no processor retains longer than the platform without documented reason |

**DEC-1200 (options).** How `retained-restricted` surfaces: **(a)** name the legal basis/duration —
transparent, more friction. **(b)** confirm receipt only, "per applicable law" — less exposure, less
transparent. **(c)** silent partial deletion of non-required fields — most protective, most build
cost. Needs counsel + product.

---

## 6. The immutable audit trail

BRD A8's selection record (`BR-802`) is legal evidence post-*Montgomery*; 49 CFR 371 gives parties a
right to review the broker record. This must be structurally unfalsifiable.

| ID | Requirement |
|---|---|
| NFR-1226 | Append-only store for load/bid/award/eligibility/POD/claim state changes and every permission grant/revoke (carries BRD NFR-704/901). No in-place `UPDATE`/`DELETE`; corrections are compensating entries |
| NFR-1227 | Tamper-evidence: entries hash-chained (or equivalent) so any alteration anywhere is detectable |
| NFR-1228 | The selection record snapshots safety/insurance/authority evidence **as it existed at award time** — not a live pointer that changes when source data later changes |
| FR-1200 | A record-production capability assembles the full transaction record (371.3's 6 elements + selection record + custody events) for an entitled party (carrier, shipper, regulator, subpoena) within a stated turnaround `[NEEDS INPUT]`, designed against the pending 48-hr FMCSA proposal (BRD NFR-705) |
| NFR-1229 | Audit retrieval served off a path independent of the transactional write path (extends §2 NFR-1214) |
| NFR-1230 | Audit trail is tenant-scoped per §1; cross-org audit access is itself audited, bounded to platform-ops (`→ F11`) |

---

## 7. The ODbL architectural boundary — enforceable, not advisory

Per `DECISIONS.md` DEC-LOCK-002 and BRD A12 (`BR-1202`/`BR-1203`): `osm.*` tables compute Produced
Works internally (route-feasibility, fuel-cost-floor signal) but raw records never cross the API
boundary. `/v1/fuel` does exactly this today — the counter-example this closes.

| ID | Requirement | Test |
|---|---|---|
| NFR-1231 | No response body, export, webhook, or error `details` field ever contains a raw row or row-derived field-set from `osm.*` | Static: any serializer touching an `osm.*` model flagged at build. Dynamic: every response shape contract-tested for absence of ODbL-sourced fields |
| NFR-1232 | Only aggregated Produced Works (feasibility flag, cost-floor number, distance) cross the boundary — never station name/coordinates/tags sourced from `osm.*` | Field-provenance tagging (BR-1201): a field whose lineage touches `osm.*` and isn't a documented aggregation is rejected pre-serialization |
| NFR-1233 | CI-enforced (extends the existing invariant test, BR-1202/1203) — not a code-review convention | Release blocked if the test is missing or fails, same severity as a security-scan failure |
| EC-1200 | New endpoint joins `osm.*` "for one internal report" | Boundary test runs against it before merge, no exemption path | — |

---

## 8. Observability

| ID | Signal | What must be measurable |
|---|---|---|
| NFR-1234 | Golden signals per tier | Latency/error-rate/saturation/traffic per Tier (§2) — a Tier 3 outage never masks a Tier 0 problem |
| NFR-1235 | Correlation | `trace_id` (frd-spine §4) threads logs/metrics/traces end-to-end |
| NFR-1236 | Authorization denials | Rate/pattern of denials, tenant-scoped, alertable — a spike against one org is a probe signal |
| NFR-1237 | Cross-tenant attempt | A request whose resolved scope would have crossed org boundary (caught by §1) is logged as a **security event**, not silently 403'd |
| NFR-1238 | Impersonation/override use | "View as," manual award override (BRD `EC-725`), claim waiver — first-class observable events with volume trend, not log lines |
| NFR-1239 | Auction integrity | Bid-timing anomalies, rotation patterns (BRD `EC-710`), shill-bid heuristics — feeds F6/F8's anti-gaming, observed here as platform health |
| NFR-1240 | SLO burn | Error-budget consumption per Tier; multi-window (fast+slow) burn-rate alerts, thresholds `[NEEDS INPUT]` |

---

## 9. Secrets, keys, encryption, third-party data handling

| ID | Requirement |
|---|---|
| NFR-1241 | Secrets in a dedicated store, never in config/source/logs; rotation interval `[NEEDS INPUT]` |
| NFR-1242 | Encryption in transit (all hops) and at rest for every §4 data class — mandatory, no exception path |
| NFR-1243 | Key rotation/revocation is drillable; compromise blast radius bounded by per-purpose key separation (signing ≠ encryption ≠ consignee tokenised-link signing) |
| NFR-1244 | Every third-party processor has a data-processing agreement matching this section's retention/deletion/breach obligations before integration |
| NFR-1245 | Breach-notification procedure/timeline `[NEEDS INPUT]` per state law; drilled, not shelved |

---

## 10. Backup and disaster recovery

| ID | Requirement |
|---|---|
| NFR-1246 | RPO `[NEEDS INPUT]` per Tier — Tier 0 evidentiary data (custody events, selection record) drives the tightest RPO |
| NFR-1247 | RTO `[NEEDS INPUT]` per Tier |
| NFR-1248 | Backups verified by actual restore drill, cadence `[NEEDS INPUT]` — not assumed functional from a clean completion log |
| NFR-1249 | Restore respects §1 isolation and §4 retention boundaries — no resurrecting data past its lawful window without a hold |

**The honest question:** freight physically moves while the system is down. "Recovered" for a Tier
0 system is not "database restored to a consistent point" — it means the gap between last-synced
state and physical reality is **reconciled**, not assumed correct. A truck that moved during an
outage needs a driver/dispatcher-asserted, timestamped reconciliation workflow (`→ F11`), not a
silent overwrite.

---

## Edge-case register

| ID | Trigger | Behaviour | Decides | Unresolved |
|---|---|---|---|---|
| EC-1201 | File path/prefix guessed or brute-forced | Signed-URL denial + security alert | Platform | Alert threshold `[NEEDS INPUT]` |
| EC-1202 | Support agent queries logs outside assigned case | Denied (NFR-1204); elevation needs a logged reason | Platform ops | Elevation approval flow → F11 |
| EC-1203 | Benchmark report would reveal a single-bidder lane | Refuse below `k`-anonymity floor (NFR-1206) | A6/A10 | Floor value `[NEEDS INPUT]` |
| EC-1204 | Unanticipated exception leaks a foreign `org_id` in a stack trace | Caught pre-release by NFR-1207; if it reaches prod, treated as a security incident | Security on-call | Severity threshold |
| EC-1205 | Tier 0 capture fully offline, no dock connectivity | Local capture, capture-time timestamp, sync + reconcile on reconnect | F4/F5 | Conflict resolution on double-sync |
| EC-1206 | Auction close-time infra degraded | Extend, never close on an unreliable clock | F6 | Extension length `[NEEDS INPUT]` |
| EC-1207 | Deletion request against a record under hold / in 371.3 window | `retained-restricted`, not deleted | Counsel + Platform | Disclosure model — DEC-1200 |
| EC-1208 | Hold placed after a related record already queued for purge | Purge suspendable per-record on demand (carries BRD EC-715) | Platform | Hold-placement latency `[NEEDS INPUT]` |
| EC-1209 | Feature joins `osm.*` "just this once" | CI boundary test blocks merge regardless of intent | Platform eng | No exemption path — by design |
| EC-1210 | Regulator/counsel subpoenas the full transaction record | FR-1200 serves it off the audit-independent path | Counsel + Platform | Turnaround SLA `[NEEDS INPUT]` |
| EC-1211 | System recovers from Tier 0 outage; pickup/delivery occurred during the gap | Reconciliation workflow, not silent overwrite (§10) | Ops → F11 | Reconciliation UX + authority |
| EC-1212 | Driver rights-request arrives directly, not via carrier | Standing/verification (carries BRD EC-713) | Counsel | Verification method |
| EC-1213 | Impersonation session left open beyond intended use | Time-boxed auto-expiry, not manual-only close | Platform | Timeout value `[NEEDS INPUT]` |
| EC-1214 | Restore for one tenant's incident overlaps another tenant's active hold | Isolation (NFR-1205) and hold (NFR-1220) both hold simultaneously | Platform + Counsel | Concurrent-constraint procedure |
| EC-1215 | Cross-tenant read succeeds despite layered defences | SEV-1 security incident, breach-assessment procedure triggers | Security on-call | Customer-notification threshold |

---

**Summary:** 50 NFRs, 1 FR, 15 EC, 1 DEC, 1 CHALLENGE. `[NEEDS INPUT]`: 21 distinct tags — all
numeric (RPO, RTO, retention periods A7 left open, rotation intervals, timeouts, thresholds). Zero
invented numbers.
