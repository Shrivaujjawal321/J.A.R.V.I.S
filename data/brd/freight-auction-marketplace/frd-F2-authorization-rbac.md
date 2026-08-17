# FRD Part F2 — Authorization, Roles, and the Permission Matrix

**US Freight Reverse-Auction Marketplace · Agent F2 · ID block 200-299 · FRD spine §2/§3 binding**

**Owns:** role taxonomy · permission matrix · scope enforcement · delegation · privilege-escalation defence.
**References, does not restate:** auth/sessions (→ F1) · entity + audit store (→ F3) · endpoints (→ F4) · error registry (→ F5) · auction mechanics and the open/sealed fork (→ F6) · assignment (→ F7) · tracking privacy (→ F8) · ops console (→ F11) · tenancy-isolation NFRs (→ F12).

Authorization is **deny-by-default**: a permission absent from §2.2 does not exist.

---

## 2.1 Role taxonomy

A **role** is a record `(user, role, scope binding, granted_by, granted_at, expires_at?)`. A grantable capability (bid, accept-award) is a **role variant**, written `ROLE[+CAP]`, so the §3 scope vocabulary stays closed. Four org shapes: SHIPPER, CARRIER (asset-holder), CARRIER (broker-flagged — same tenant type, spine §2), PLATFORM.

| ID | Role | Org type | Default scope | Note |
|---|---|---|---|---|
| ROLE-200 | `SHIPPER_ORG_ADMIN` | SHIPPER | `own_org` | Users, sites, grants; only role that may cancel post-award |
| ROLE-201 | `SHIPPER_LOAD_POSTER` | SHIPPER | `own_site` | Publishes for its site(s); BR-901 |
| ROLE-202 | `SHIPPER_VIEWER` | SHIPPER | `own_org`/`own_site` | Read-only everywhere |
| ROLE-203 | `SHIPPER_BILLING` | SHIPPER | `own_org` | Invoices, disputes; no load mutation |
| ROLE-204 | `SHIPPER_CLAIMS_CONTACT` | SHIPPER | `own_org` | Claim raise/track; BR-906 relay point |
| ROLE-210 | `CARRIER_OWNER` | CARRIER | `own_org` | Authority holder; inherently `+BID` and `+ACCEPT_AWARD`; sole payee-of-record authority (BR-909) |
| ROLE-211 | `CARRIER_DISPATCHER` | CARRIER | `own_org` | Bids only with `+BID`; accepts only with `+ACCEPT_AWARD` (BR-900/902) |
| ROLE-212 | `CARRIER_ACCOUNTING` | CARRIER | `own_org` | Invoices, settlement; **never** bid/accept/payee |
| ROLE-213 | `CARRIER_COMPLIANCE` | CARRIER | `own_org` | Uploads authority/COI/CDL; no commercial authority |
| ROLE-214 | `CARRIER_DRIVER` | CARRIER | `assigned_load` | Mobile-only; sees nothing unassigned |
| ROLE-215 | `CARRIER_AGENT` | CARRIER | `own_org`, time-boxed | External delegate inside the carrier org via grant, not a second membership (§2.8) |
| ROLE-216 | `OWNER_OPERATOR` | CARRIER | `own_org` + `assigned_load` | Union of ROLE-210 and ROLE-214, nothing more (§2.8) |
| ROLE-220 | `PLATFORM_SUPPORT` | PLATFORM | `granted_case` | Read-only + view-as; no state override |
| ROLE-221 | `PLATFORM_EXCEPTION_DESK` | PLATFORM | `granted_case` | Exception states only; no bids, awards or money |
| ROLE-222 | `PLATFORM_FRAUD_REVIEWER` | PLATFORM | `platform_wide` read, `granted_case` write | Suspend/flag; cannot approve a carrier or settle money |
| ROLE-223 | `PLATFORM_CARRIER_VETTING` | PLATFORM | `platform_wide` | Sole onboarding approver (BR-908); exclusive of ROLE-225 |
| ROLE-224 | `PLATFORM_CLAIMS_DESK` | PLATFORM | `granted_case` | Settles/disallows claims (BR-807/808), maker-checker |
| ROLE-225 | `PLATFORM_BILLING_OPS` | PLATFORM | `granted_case` | *Requests* waivers; never approves its own (BR-907) |
| ROLE-226 | `PLATFORM_ADMIN` | PLATFORM | `platform_wide` | Identity administration **only** — no business-object mutation |
| ROLE-227 | `PLATFORM_AUDITOR` | PLATFORM | `platform_wide` | Read-only by definition; write is unrepresentable |
| ROLE-228 | `PLATFORM_AWARD_OVERRIDE` | PLATFORM | `granted_case`, time-boxed | Break-glass re-award; dual-approved, disclosed to both orgs (BR-306) |
| ROLE-240 | `CONSIGNEE_TOKEN` | *no org/account* | `assigned_load` | Single-load, single-purpose, expiring link — a principal, not a User |
| ROLE-241 | `DRIVER_DEVICE` | CARRIER-bound | `assigned_load` | Driver with no login; POD capture principal, carrier-binding (BR-903) |
| ROLE-242 | `FACTOR_PAYEE` | *no account* | — | Notification target only `[NEEDS INPUT: factor portal wanted?]` |

---

## 2.2 The permission matrix

Shape is `(role) may (action) on (resource_type) when (scope)` exactly. Scope kinds are the five in FRD spine §3 plus `granted_case` (see CHALLENGE at the end of §2.9).

| PERM | Role | may (action) | on (resource_type) | when (scope) | Trace |
|---|---|---|---|---|---|
| PERM-200 | `SHIPPER_LOAD_POSTER` | create, amend (pre-bid) | `load_draft` | `own_site` | BR-101/135 |
| PERM-201 | `SHIPPER_LOAD_POSTER` | publish | `load` | `own_site` | BR-901/130 |
| PERM-202 | `SHIPPER_ORG_ADMIN` | publish, amend | `load` | `own_org` | BR-901 |
| PERM-203 | `SHIPPER_LOAD_POSTER` | cancel (pre-award only) | `load` | `own_site` + own-authored | BR-904/140 |
| PERM-204 | `SHIPPER_ORG_ADMIN` | cancel (any pre-pickup state) | `load` | `own_org` | BR-904/141/142 |
| PERM-205 | *no role* | cancel | `load` in/after `PICKED_UP` | — | BR-144 — action does not exist |
| PERM-206 | `SHIPPER_VIEWER` | read | `load`, `bid_summary`, `award` | `own_org`/`own_site` | BR-901 |
| PERM-207 | `SHIPPER_ORG_ADMIN` | read, decide | `bid` (all bids on own load) | `own_org` | BR-303 |
| PERM-208 | `SHIPPER_ORG_ADMIN` | create, revoke | `role_grant` (shipper roles) | `own_org` | NFR-901 |
| PERM-209 | `SHIPPER_ORG_ADMIN` | create, deactivate | `user`, `site` | `own_org` | BR-103 |
| PERM-210 | `SHIPPER_BILLING` | read, dispute | `invoice` | `own_org` | 9.3.2 |
| PERM-211 | `SHIPPER_CLAIMS_CONTACT` | create, read, respond | `claim` | `own_org` | BR-807 |
| PERM-212 | `SHIPPER_*` | read | `tracking_position` | `assigned_load` (own load, post-pickup) | → F8 |
| PERM-213 | `SHIPPER_ORG_ADMIN` | read | `pod`, `bol`, `selection_record` | `own_org` | BR-802/809 |
| PERM-214 | `CARRIER_OWNER` \| `CARRIER_DISPATCHER[+BID]` | read (bid view) | `load` | `eligible_load` | BR-301 |
| PERM-215 | `CARRIER_OWNER` \| `CARRIER_DISPATCHER[+BID]` | create, withdraw (per policy) | `bid` | `eligible_load` | BR-301/308 |
| PERM-216 | `CARRIER_ACCOUNTING`, `CARRIER_DRIVER`, `CARRIER_COMPLIANCE` | create | `bid` | — | denied always |
| PERM-217 | `CARRIER_OWNER` \| `CARRIER_DISPATCHER[+ACCEPT_AWARD]` | accept, decline | `award` | `own_org` | BR-902/905 |
| PERM-218 | `CARRIER_DISPATCHER[+BID]` (no accept grant) | accept | `award` | — | denied — BR-902 acceptance test |
| PERM-219 | `CARRIER_OWNER` \| `CARRIER_DISPATCHER` | create, change | `assignment` (driver + truck) | `assigned_load` | BR-910 → F7 |
| PERM-220 | `CARRIER_OWNER` | create, revoke | `role_grant` (incl. `+BID`, `+ACCEPT_AWARD`) | `own_org` | BR-900 |
| PERM-221 | `CARRIER_OWNER` | set | `payee_of_record` | `own_org` | BR-909 |
| PERM-222 | `CARRIER_DISPATCHER`, `CARRIER_ACCOUNTING` | set | `payee_of_record` | — | denied — BR-909 acceptance test |
| PERM-223 | `CARRIER_COMPLIANCE` \| `CARRIER_OWNER` | upload, replace | `document` (authority, COI, CDL, permit) | `own_org` | BR-804 |
| PERM-224 | `CARRIER_ACCOUNTING` \| `CARRIER_OWNER` | read, dispute | `invoice`, `payment` | `own_org` | → A6 |
| PERM-225 | `CARRIER_OWNER` \| `CARRIER_ACCOUNTING` | create, respond | `claim` | `own_org` | BR-807 |
| PERM-226 | `CARRIER_DRIVER` \| `DRIVER_DEVICE` | read (execution view) | `load` | `assigned_load` | BR-910 |
| PERM-227 | `CARRIER_DRIVER` \| `DRIVER_DEVICE` | capture, sign | `pod`, `bol_exception` | `assigned_load` | BR-903 |
| PERM-228 | `CARRIER_DRIVER` | read | `bid`, `invoice`, `rate_confirmation` amount | — | denied — driver never sees commercials `[ASSUMPTION: rate withheld from driver by default \| conf: med]` |
| PERM-229 | `CARRIER_DISPATCHER` | sign | `pod` | — | denied — §2.8; dispatcher may only record a *carrier attestation*, distinctly typed |
| PERM-230 | `CARRIER_*` | read | `load` | any load not `eligible_load` / not `assigned_load` | denied → **not-found**, §2.6 |
| PERM-231 | `CONSIGNEE_TOKEN` | read (delivery view), submit exception note | `load`, `bol_exception` | `assigned_load` | BR-906/912 |
| PERM-232 | `CONSIGNEE_TOKEN` | read | `bid`, `invoice`, `award`, `carrier commercials` | — | denied always |
| PERM-233 | `PLATFORM_SUPPORT` | read | `load`, `award`, `claim`, `invoice` | `granted_case` | BR-813 |
| PERM-234 | `PLATFORM_SUPPORT` | start (read-only view-as) | `impersonation_session` | `granted_case` | FR-212 |
| PERM-235 | `PLATFORM_SUPPORT` | write anything as another org | any | — | denied always |
| PERM-236 | `PLATFORM_EXCEPTION_DESK` | transition (exception states only) | `load` | `granted_case` | BR-913 |
| PERM-237 | `PLATFORM_EXCEPTION_DESK` | create, amend, withdraw | `bid`, `award`, `invoice` | — | denied always |
| PERM-238 | `PLATFORM_FRAUD_REVIEWER` | read | `bid`, `award`, `selection_record`, `org` | `platform_wide` | BR-814/815 |
| PERM-239 | `PLATFORM_FRAUD_REVIEWER` | suspend, flag | `organization`, `user` | `granted_case` | BR-817/818 |
| PERM-240 | `PLATFORM_CARRIER_VETTING` | approve, reject | `carrier_application` | `platform_wide` | BR-908 |
| PERM-241 | `PLATFORM_CARRIER_VETTING` | approve | `carrier_application` it also authored/edited | — | denied — maker-checker |
| PERM-242 | `PLATFORM_CLAIMS_DESK` | settle, disallow | `claim` | `granted_case` + second approver | BR-807/808/907 |
| PERM-243 | `PLATFORM_BILLING_OPS` | request | `charge_waiver` | `granted_case` | BR-907 |
| PERM-244 | `PLATFORM_BILLING_OPS` | approve | `charge_waiver` it requested | — | denied — maker-checker |
| PERM-245 | `PLATFORM_CLAIMS_DESK` \| ops supervisor | approve | `charge_waiver` | `granted_case`, requester ≠ approver | BR-907 |
| PERM-246 | `SHIPPER_*`, `CARRIER_*` | approve | `charge_waiver`, `claim_settlement` | — | denied always — BR-907 |
| PERM-247 | `PLATFORM_ADMIN` | create, revoke | `role_grant`, `user`, `organization` | `platform_wide` | FR-215 |
| PERM-248 | `PLATFORM_ADMIN` | read, mutate | `bid`, `award`, `invoice`, `claim`, `pod` | — | denied always — admin ≠ operator |
| PERM-249 | `PLATFORM_ADMIN` | grant itself | any business role | — | denied — self-grant blocked, §2.8 |
| PERM-250 | `PLATFORM_AUDITOR` | read | `audit_log`, `selection_record`, all business objects | `platform_wide` | BR-819 |
| PERM-251 | `PLATFORM_AUDITOR` | any mutation | any | — | unrepresentable by role definition |
| PERM-252 | `PLATFORM_AWARD_OVERRIDE` | void, re-award | `award` | `granted_case`, dual-approved, time-boxed | BR-306 |
| PERM-253 | `PLATFORM_*` | accept, decline | `award` on behalf of a carrier | — | **denied always** — §2.4 row 3 |
| PERM-254 | `PLATFORM_*` | create, amend | `bid` | — | **denied always** — BR-317 anti-shill |
| PERM-255 | `CARRIER_OWNER` | read | `audit_log` entries for its own org (incl. who accepted what) | `own_org` | RSK-900 |
| PERM-256 | `SHIPPER_ORG_ADMIN` | read | `carrier identity + authority type` on own load | `own_org`, post-award (identity) / at-bid (authority-type flag) | BR-313 |
| PERM-257 | `CARRIER_AGENT` | inherit | grantor-specified subset of ROLE-211 | `own_org` (host org), until `expires_at` | §2.8 |
| PERM-258 | any role | read | `document` (COI, CDL, authority) of another org | `assigned_load` only | BR-813 |
| PERM-259 | any suspended user/org | any mutating action | any | — | denied — BR-818 preserves read on in-flight loads |

---

## 2.3 The contested actions — explicit answers

| Action | Answer (authoritative) | Trace |
|---|---|---|
| Publish a load | `SHIPPER_LOAD_POSTER` when `own_site`; `SHIPPER_ORG_ADMIN` when `own_org`. Post-only is a real tier: it excludes cancel and amend. | BR-101/901/904 |
| Bid | `CARRIER_OWNER`, or `CARRIER_DISPATCHER[+BID]`, when `eligible_load`. Never accounting, compliance or driver. | BR-900/301 |
| **Accept an award on a carrier's behalf** | Only `CARRIER_OWNER` or `CARRIER_DISPATCHER[+ACCEPT_AWARD]`. The grant is separate from `+BID`; accepting user + grant id are written into the rate confirmation. **No PLATFORM role may ever accept for a carrier** — a phoned-in acceptance is an ops-logged *request* that stays pending until the carrier acts in-system. | BR-902/905, PERM-253 |
| Sign a POD | The assigned driver (`CARRIER_DRIVER`/`DRIVER_DEVICE`) when `assigned_load`; binding on the carrier org. The consignee signature is *captured content*, not an authenticated principal — do not claim non-repudiation for it. A dispatcher-entered POD is a distinctly-typed carrier attestation, weaker evidence (→ A5/A8). | BR-903/910, EC-902 |
| Cancel | Pre-award: original poster or admin. Post-award pre-pickup: `SHIPPER_ORG_ADMIN` only `[ASSUMPTION: admin-tier act \| conf: med]`. Post-`PICKED_UP`: no role — the action is absent, RTO instead. Carrier-side decline = accept tier. | BR-904/905/144 |
| Raise a claim | `SHIPPER_CLAIMS_CONTACT`/admin, `CARRIER_OWNER`/`CARRIER_ACCOUNTING`, or `PLATFORM_CLAIMS_DESK` relaying a consignee observation (BR-906). | BR-807/906 |
| Settle a claim | `PLATFORM_CLAIMS_DESK` only, two distinct platform actors. Never a transacting party. | BR-907/808 |
| Waive a charge | `PLATFORM_BILLING_OPS` requests → different platform approver decides. Requester ≠ approver, enforced, not policy. | BR-907 |
| Approve a carrier | `PLATFORM_CARRIER_VETTING` only; human act even on an all-clear automated pass; approver ≠ editor of the application. | BR-908 |

---

## 2.4 Cross-org visibility — what a carrier sees, and when

Legend: **✓** visible · **✗** hidden · **D** = decided by F6's DEC-302/303 fork · **P** = post-award only.

| Field | Ineligible carrier | Eligible, not bid | Live bidder | Losing bidder (post-award) | Awarded carrier | Assigned driver | Consignee token |
|---|---|---|---|---|---|---|---|
| Load exists at all | ✗ (not-found) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Lane at city/state level | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Full pickup/drop street address | ✗ | ✗ | ✗ | ✗ | **P** ✓ | **P** ✓ | own stop only |
| Dock #, gate code, site contact name/phone | ✗ | ✗ | ✗ | ✗ | **P** ✓ | **P** ✓ | own stop only |
| Commodity class, weight, dims, equipment, hazmat | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| Appointment windows | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Shipper legal identity | ✗ | **D** `[NEEDS INPUT]` | **D** | **D** | ✓ | ✓ | ✓ |
| Shipper payment-standing indicator (not financials) | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ |
| Own bid | — | — | ✓ | ✓ | ✓ | ✗ | ✗ |
| Rival bid amounts | ✗ | ✗ | **D** (see §2.5) | ✗ | ✗ | ✗ | ✗ |
| Rival bidder identities | ✗ | ✗ | ✗ **never** | ✗ | ✗ | ✗ | ✗ |
| Live bid count / pool size | ✗ | ✗ | **D** — F2 recommends ✗ live, ✓ on the award record | ✗ | ✗ | ✗ | ✗ |
| Reserve / ceiling price | ✗ | ✗ | **D** (DEC-306) | ✗ | ✗ | ✗ | ✗ |
| Award outcome (won/closed) | ✗ | ✗ | ✓ | ✓ "no longer open" — **not** the clearing price | ✓ | ✓ | ✗ |
| Winning price | ✗ | ✗ | ✗ | ✗ | ✓ (own) | ✗ | ✗ |
| Selection record (who was excluded and why) | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ — shipper + platform + auditor only (BR-802) |
| Tracking positions | ✗ | ✗ | ✗ | ✗ | ✓ (own trip) | ✓ | ETA only (→ F8) |
| POD / BOL images | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | own delivery only |

**The rule underneath the table:** an eligible-but-not-awarded carrier gets exactly the fields needed to *price* the load — geography, freight characteristics, timing, counterparty payment standing. Everything identifying a *place* or a *person* (street address, gate code, dock contact, and per DEC-302 possibly the shipper's name) unmasks on `AWARD_ACCEPTED`, never before (BR-126), and by state event rather than client request.

---

## 2.5 Bid confidentiality — which options are enforceable and which leak by construction

F6 owns the mechanism. F2 states only what is *technically containable*:

| Option (DEC-302/303) | Enforceable server-side? | Leak |
|---|---|---|
| Sealed, no feedback until close | **Yes, fully.** Rival bids are never in any bidder-principal response. | Only the shipper telling a carrier — outside the system boundary. |
| Sealed + "you are currently winning" flag | **No — leaks by construction.** Repeated decrements binary-search the standing best price. The oracle *is* the leak; access control cannot fix it. | Full rival price recovery in a handful of bids. |
| Open standing best price | Not a security question — a disclosure decision. | Rival cost structure across repeat lanes; anonymisation does **not** help, since price patterns fingerprint a bidder over time. BR-314 is unachievable under this option — say so rather than promise it. |
| Live bid count | Enforceable either way. | Reveals pool thinness *and* lets a cartel verify no outsider entered. F2 recommends post-award only; BR-318 needs it on the award record, not the live view. |
| Rival identity, ever | Enforceable, and should always be off — nothing in the mechanism needs it. | Direct collusion enablement (Sherman §1, BR-315). |

**CHALLENGE (to F6, not a divergence):** DEC-303's "rank only" and DEC-302's sealed option should be evaluated as one fork, not two, because rank feedback is the same oracle as a winning-flag once decrements are small.

---

## 2.6 Scope enforcement and its failure modes

| Failure mode | Control | Detection |
|---|---|---|
| IDOR on load/bid/document id | Reads filter by the session's derived scope set at the **query** layer (row-level), never a post-fetch handler check. Ids non-sequential (→ F3). | Per-principal deny rate (FR-220) |
| Tenant id from a client-supplied value | Org context derives **only** from the session (→ F1), never from a body/header/path org id; a mismatching org id is rejected, not coerced. | `SESSION_ORG_CONTEXT_MISMATCH` counter |
| Enumeration via authorization errors | Cross-org and non-eligible denials return **not-found**, never forbidden — for `load`, `bid`, `document`, `invoice`, `claim`, `user`, `organization`. Within-org denials may return forbidden; existence is already known to that tenant. Eligibility *reasons* live on the carrier's own eligibility resource, never on the load. | Per-principal not-found rate |
| Driver enumerating unassigned loads | Driver principal resolves to a set of `assigned_load` ids; no list filter widens it. | Driver-scope deny alerts |
| Suspended user's live token | Suspension revokes sessions at the authorization layer, not only at login (→ F1). Reads on in-flight loads survive; mutations deny (BR-818). | `ORG_SUSPENDED` on mutation |
| Permissions cached after revocation | Caching allowed only within a bounded window `[NEEDS INPUT: max staleness]`; revocation, suspension and award-state changes publish invalidation events. | Revocation-to-effect lag |
| Broker-carrier seeing a load via two paths | Visibility computed **per org context, once per request**; one active org context per session; one org per user (spine §2), so cross-org work is a delegation grant (ROLE-215), never dual membership. A re-brokered load creates a second, independently-scoped record (→ A2/A8), not a widened view of the first. | Related-entity check, BR-316/317 |
| Escalation via self-grant | No role grants itself, or grants a role it does not hold. Platform business roles are grantable only by `PLATFORM_ADMIN`, which holds no business permission (PERM-247/248/249). | Grant-graph audit |

---

## 2.7 Platform ops power — the insider case

An insider who can quietly re-award a load is A8's fraud vector in its purest form. Controls:

1. **Impersonation is read-only** (`view-as`); write-as does not exist for `PLATFORM_SUPPORT`. If write-as is ever required it must be case-bound, time-boxed `[NEEDS INPUT: duration]`, dual-approved, banner-visible, and emit an event *to the impersonated org*.
2. **Every audit entry carries `actor_user_id` and `real_actor_user_id`**, plus case id and trace id (→ F3).
3. **Separation of duties, enforced not stated:** vetting ≠ billing ops; claim settlement needs two platform actors; waiver requester ≠ approver; `PLATFORM_ADMIN` holds no business permission; `PLATFORM_AUDITOR` cannot be granted write.
4. **Award override is its own break-glass role** (ROLE-228): dual-approved, auto-expiring, and notified to the shipper *and* every affected carrier org, including the one whose award was voided. An override no counterparty can see is precisely the fraud this control exists to stop.
5. **No platform role bids or accepts** (PERM-253/254) — the hardest line in this document.

---

## 2.8 Delegation

| Case | Model | Guard |
|---|---|---|
| Dispatcher acting for a driver | Dispatcher may create/change the driver+truck assignment, and may record a **carrier attestation** of delivery. It may not produce a driver signature. | PERM-229; attestation is a distinct evidence type |
| Owner-operator | One user holds `OWNER_OPERATOR` = ROLE-210 ∪ ROLE-214. Union, not superset: no platform visibility, no cross-org read; accept-award comes from the owner role it genuinely holds. Each action records *which* capability was exercised, so the audit distinguishes "accepted an award" from "signed a POD". No maker-checker rule ever needs two humans on the carrier side, so a one-person carrier is never blocked. | PERM-216/228 |
| Agent acting for a carrier | `CARRIER_AGENT` is a time-boxed grant inside the carrier's org, revocable by the owner, capped at a subset of dispatcher powers, and never inheriting `+ACCEPT_AWARD` unless explicitly granted. | PERM-257 |
| A person who works for two carriers | Two separate user identities in two orgs. Their linkage is a related-entity signal for BR-316/317, not a convenience feature. | BR-316 |

---

## 2.9 Functional requirements

| FR | Requirement | Traces |
|---|---|---|
| FR-200 | Authorization is evaluated server-side from the session's org context; no client-supplied tenant/org id participates. | OBJ-006 |
| FR-201 | Deny by default: no matching PERM row = denial. | OBJ-006 |
| FR-202 | Scope kinds are closed; a new kind is a spine change, not a code change. | spine §3 |
| FR-203 | Grants are records with granter, timestamp, optional expiry; revocable; all grant/revoke events audited. | NFR-901 |
| FR-204 | Revocation, suspension and award-state changes invalidate cached decisions within a bounded window `[NEEDS INPUT]`. | OBJ-006 |
| FR-205 | Cross-org and non-eligible denials return not-found; within-org denials may return forbidden. | OBJ-006 |
| FR-206 | Eligibility failure reasons served only from the carrier's own eligibility resource. | BR-301 |
| FR-207 | Bid confidentiality enforced in the data-access layer, not the view layer. | BR-314 |
| FR-208 | Post-award unmasking is triggered by `award.accepted`, never by a request parameter. | BR-126 |
| FR-209 | Accept-award is a distinct grant from bid. | BR-902 |
| FR-210 | No PLATFORM role may create/amend/withdraw a bid or accept/decline an award for a carrier. | BR-317 |
| FR-211 | Award override requires a dedicated role, two approvers, a reason, an event, and notice to every affected org. | BR-306 |
| FR-212 | Impersonation is read-only; write-as is case-bound, time-boxed, dual-approved and disclosed to the impersonated org. | OBJ-006 |
| FR-213 | Audit records actor, real actor, org context, resource, decision, grant id, trace id; append-only. | NFR-901, BR-819 |
| FR-214 | Maker-checker enforced for waivers, claim settlements, carrier approvals. | BR-907/908 |
| FR-215 | `PLATFORM_AUDITOR` and `PLATFORM_ADMIN` cannot hold business-object write permissions, by role definition. | OBJ-006 |
| FR-216 | One org per user; one active org context per session. | spine §2 |
| FR-217 | Driver principals resolve to an explicit assigned-load set; no endpoint widens it. | BR-910 |
| FR-218 | Suspension blocks mutation, preserves read on in-flight loads. | BR-818 |
| FR-219 | Consignee access is a single-load, single-purpose, expiring, revocable token, not an account; lifetime `[NEEDS INPUT]`. | spine §2, BR-912 |
| FR-220 | Denials emit per-principal counters for enumeration/IDOR detection. | OBJ-006 |
| FR-221 | The §2.2 matrix is executable: every PERM row carries a negative test in CI. | OBJ-006 |
| FR-222 | The rate confirmation records the accepting user id and the authorising grant id. | BR-902, RSK-900 |

**Error codes → F5** (names proposed, registry is F5's): `NOT_FOUND` · `FORBIDDEN_ACTION_FOR_ROLE` · `ACCEPT_AWARD_GRANT_REQUIRED` · `ORG_SUSPENDED` · `SESSION_ORG_CONTEXT_MISMATCH` · `DELEGATION_EXPIRED` · `SEPARATION_OF_DUTIES_VIOLATION` · `DUAL_APPROVAL_REQUIRED` · `IMPERSONATION_WRITE_NOT_PERMITTED` · `CONSIGNEE_TOKEN_EXPIRED` · `SELF_GRANT_NOT_PERMITTED`. There is deliberately **no** `BID_VISIBILITY_DENIED` — that response would confirm the bid exists.

**CHALLENGE (scope kind, additive).** FRD spine §3 fixes five scope kinds. Platform roles need a sixth: **`granted_case`** — access bound to a specific ticket/load/claim, time-boxed and audited. Without it every ops permission collapses to `platform_wide`, which is exactly the standing all-tenant access that makes the insider re-award fraud (A8) undetectable. Proposed as an addition, not a replacement.

---

## 2.10 Edge-case register

| EC | Trigger | Behaviour | Who decides | Unresolved |
|---|---|---|---|---|
| EC-200 | Dispatcher accepts an award beyond internal authority | Platform honours the grant; carrier-visible audit shows who accepted (PERM-255) | Platform enforces BR-902 | Platform exposure for honouring a misused grant (EC-900) |
| EC-201 | Carrier owner revokes `+ACCEPT_AWARD` seconds after acceptance | Acceptance stands; revocation is forward-only | F6 (award state) | Whether a revocation window exists at all |
| EC-202 | Sole owner of a carrier org leaves / dies | Org has no one who can accept, assign or set payee | Platform vetting desk | Recovery path undefined `[NEEDS INPUT]` |
| EC-203 | Owner-operator's single login is compromised | Attacker holds bid, accept, assign, POD and payee powers at once | → F1 | Step-up auth on payee-of-record is the obvious control — F1 owns it |
| EC-204 | Carrier suspended mid-transit (EC-905/906) | Reads on the in-flight load survive; all new bids/awards blocked | Fraud reviewer | No clean action while freight is in custody |
| EC-205 | Awarded carrier re-brokers to a second carrier org | Second org must not inherit visibility of the first award | A2/A8 detection | Whether legitimate co-brokerage is ever permitted |
| EC-206 | Driver assigned, then unassigned mid-trip | Access must revoke, but the driver still physically holds the freight | Exception desk | Read-only grace access for the holding driver is unresolved |
| EC-207 | Consignee forwards their token link to a third party | Token grants full delivery view to whoever holds it | Platform | Bearer tokens cannot be bound to a person with no account — accept and limit blast radius |
| EC-208 | Dock staff who signs is not the consignee | Signature captured from an unauthenticated person | → A5 | Non-repudiation is not achievable here; do not claim it |
| EC-209 | Shipper poster leaves; their loads are live | Loads orphaned from a cancel-authorised user | `SHIPPER_ORG_ADMIN` | Reassignment flow undefined |
| EC-210 | Two shipper posters publish the same freight | Two auctions, two eligible pools | Shipper admin | Platform cannot detect duplicate freight (BR-132) |
| EC-211 | Support agent views a load while an auction is live | Read-only view includes rival bids | Ops policy | Should support see live bid amounts at all? F2 says no by default |
| EC-212 | Fraud reviewer needs bid data platform-wide to detect rotation | Broad read is genuinely required (BR-814) | Fraud desk | Reconcile with least privilege — read-only + audited + no write |
| EC-213 | Platform admin grants itself a business role | Blocked (PERM-249) | System | Who audits the auditor — needs an external review cadence `[NEEDS INPUT]` |
| EC-214 | Ops overrides an award; the voided carrier is already en route | Both carriers notified; freight custody unresolved | Exception desk + override role | Custody unwind is A4/A8 territory |
| EC-215 | Factoring company demands read access to invoices | No account exists (ROLE-242) | Client | Portal vs notification-only `[NEEDS INPUT]` |
| EC-216 | Agent's delegation expires mid-negotiation | Actions deny with `DELEGATION_EXPIRED` | Carrier owner | Warning-before-expiry behaviour undefined |
| EC-217 | Eligible carrier loses eligibility while its bid is live | Bid must stop being rankable (BR-302); does its *visibility* also drop? | F6 | Whether the load disappears mid-auction — a jarring but safer default |
| EC-218 | Carrier queries a load id it saw before losing eligibility | Returns not-found, though it once returned data | System | Accepted inconsistency; enumeration protection wins |
| EC-219 | Shipper user asks support for a rival carrier's bid on another shipper's load | Not-found for support too, unless case-bound | Support policy | Case-binding rigour depends on `granted_case` being accepted |
| EC-220 | Driver device shared between two drivers | POD attribution ambiguous | → F7 | Device-to-driver binding is unresolved |
| EC-221 | A user holds shipper and carrier roles at two orgs (same person) | Two identities; related-entity flag | BR-316/317 | Whether the platform blocks or merely flags |
| EC-222 | Revocation event lost / consumer lagging | Stale permission persists past intent | → F12 | Bounded staleness value is `[NEEDS INPUT]` |

**What F2 cannot resolve without the client:** the post-award cancel tier, the impersonation and delegation durations, whether the shipper's identity is masked pre-award (F6's DEC-302 depends on it), and the sole-owner account-recovery path. These are risk-appetite calls, not drafting gaps.
