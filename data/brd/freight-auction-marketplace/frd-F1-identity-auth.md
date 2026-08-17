# F1 — Identity, Authentication, Sessions, Onboarding

**Owns:** authentication mechanisms · session/token lifecycle · org & user onboarding flow ·
credential/account recovery · identity assurance framework. **Does not own:** role permissions (F2) ·
entity/state storage & audit log (F3) · comparing a driver's document to the record on file (F7, BRD
BR-221/224) · fraud classification on mismatch (F7/F11 consume F1's signal) · screens (F9) ·
notification delivery (F10) · rate-limit/security NFRs (F12). Errors below are names, not `ERR-` IDs —
catalog is F5's.

## 1. Assurance framework

Two axes, NIST 800-63-3 terms: **IAL** (how sure who this person is), **AAL** (how sure this session
is that person). Populations sit at different points on both.

| Population | IAL target | AAL standing | AAL step-up |
|---|---|---|---|
| Shipper coordinator / carrier dispatcher | IAL1, org-vetted | AAL1, MFA by role (§5) | AAL2 |
| Org admin / owner-operator | IAL2-equiv at onboarding | AAL2 | AAL2 + re-challenge |
| Driver | IAL2-equiv artifact at pickup only (§9) | AAL1, device-bound | AAL2 for payout actions |
| Platform ops | IAL2, employee-vetted | AAL2 always | AAL2 + impersonation consent |
| Consignee | No identity system — capability token only (§8) | n/a | n/a |

## 2. Organization onboarding (creates the tenant)

| ID | Requirement | Pri | Trace |
|---|---|---|---|
| FR-100 | Org creation is type-scoped at entry: SHIPPER, CARRIER (asset-holder/broker), PLATFORM | Must | spine §2 |
| FR-101 | Carrier/shipper org creation requires IAL2-equiv proofing (doc + liveness) of the creating individual before leaving DRAFT | Must | BR-208 |
| FR-102 | Owner-operator org (admin = sole driver) onboards without a forced second-user step | Must | spine §2 |
| FR-103 | Org auth state (`PENDING_VERIFICATION`→`VERIFIED`) is independent of F7's document-vetting; login allowed at `PENDING_VERIFICATION`, bidding is not (F2 gates) | Must | BR-200/908 |
| FR-104 | Shipper proofing is lighter (IAL1 + domain-verified email); no FMCSA dependency | Should | derived |
| FR-105 | Platform-org accounts are never self-serve; created only by an existing platform admin | Must | A9 scope boundary |

## 3. User onboarding into an existing org

| ID | Requirement | Pri | Trace |
|---|---|---|---|
| FR-106 | Org admin/delegate (F2) invites by email or phone; invite = single-use, expiring, role-tagged, bound to one identifier | Must | BR-900/901 |
| FR-107 | Invite acceptance requires credential creation + MFA enrollment matching role policy (§5) before first action | Must | BR-900 |
| FR-108 | Driver invite supports SMS/phone as primary channel, not email-first | Must | BR-914 |
| FR-109 | Self-service signup creates a **new** org only; never a silent join of an existing org | Must | spine §2 |

## 4. Authentication mechanisms

| ID | Requirement | Pri | Trace |
|---|---|---|---|
| FR-110 | Desk users authenticate via credential (identifier+password) or org SSO (§4a) | Must | derived |
| FR-111 | Passwordless magic-link available as an alternative, not a default | Could | derived |
| FR-112 | Driver device biometric/PIN is a local-unlock layer atop a valid server session, never a substitute for it | Must | §1 |
| FR-113 | SSO capability: SAML 2.0, OIDC (no vendor), offered to shipper orgs above a size `[NEEDS INPUT]` | Should | OBJ-002 |
| FR-114 | SSO JIT provisioning requires prior domain verification; unverified domain can't auto-create membership | Must | derived |
| FR-115 | SSO never extends to drivers regardless of org config — phone-first stays | Must | BR-914 |

**`DEC-100` (open):** driver primary credential — (A) phone+SMS-OTP primary; (B) email+password,
phone MFA-fallback; (C) phone-first + device-bound long session, rare OTP re-entry. `[NEEDS INPUT]`.
**`DEC-101` (open):** SSO default — SP-initiated only (lower phishing surface) vs. also accept
IdP-initiated. `[NEEDS INPUT]`.

## 5. MFA policy

| ID | Requirement | Pri | Trace |
|---|---|---|---|
| FR-116 | MFA mandatory for any role that can accept an award, approve a waiver, change payee-of-record, or is platform ops | Must | BR-902/907 |
| FR-117 | MFA optional for read-only/viewer users | Could | derived |
| FR-118 | MFA methods: TOTP, WebAuthn/passkey (strongest), SMS OTP as fallback only — SIM-swap weakness stated, never sole method for a privileged role | Must | OBJ-006 |
| FR-119 | Driver base login needs no MFA (phone-only/low-connectivity reality); MFA required the moment a driver action touches payout/bank details | Must | BR-812/914 |

## 6. Step-up authentication

| ID | Requirement | Pri | Trace |
|---|---|---|---|
| FR-120 | Accepting an award, changing payee-of-record, approving a waiver, starting impersonation each require a fresh MFA challenge within `[NEEDS INPUT]` window regardless of standing session validity | Must | BR-902/907/909 |

## 7. Session & token lifecycle

| ID | Requirement | Pri | Trace |
|---|---|---|---|
| FR-121 | Web/desk: short-lived access token + rotating refresh token; lifetimes `[NEEDS INPUT]` | Must | OBJ-006 |
| FR-122 | Mobile driver: longer-lived, device-bound refresh token, justified by in-truck connectivity; lifetime `[NEEDS INPUT]` | Must | §1 |
| FR-123 | Refresh token bound to device/install id; token from an unregistered device rejected outright | Must | OBJ-006 |
| FR-124 | Driver app caches read state offline; queues state-changing actions (check-in, POD) with a client idempotency key for reconnect-sync (cross-ref F8) | Must | OBJ-004, spine §4 |
| FR-125 | Reconnect tries silent refresh first; interactive re-login only if the refresh token itself is invalid | Must | UX for population |
| FR-126 | Every user can list/revoke their own sessions ("log out other devices") | Should | OBJ-006 |
| FR-127 | Org admin can force-revoke any org user's sessions | Must | BR-900/910 |
| FR-128 | Lost/stolen device: user/admin deregisters device, invalidating its bound refresh token server-side; local lock never treated as a server revoke | Must | §1, OBJ-006 |

## 8. Consignee capability link — the party with no account

| ID | Requirement | Pri | Trace |
|---|---|---|---|
| FR-129 | Every consignee action is a signed, single-purpose, expiring token scoped to one shipment + one action class (view vs. state-changing, BR-906) — never a login | Must | spine §2, BR-906/912 |
| FR-130 | State-changing tokens are single-use; a replay is rejected with the first consumption event shown, not a silent no-op | Must | BR-906 |
| FR-131 | Read-only tokens may be multi-use within expiry; both share BR-912's "no confirmed-read" honesty | Must | BR-912 |
| FR-132 | Token delivered only via the out-of-band channel captured at load creation; never surfaced in a forwardable in-app context | Must | BR-912 |
| FR-133 | Expired-token access returns a safe error plus a relay path back through shipper/carrier contact | Must | BR-906, OBJ-004 |
| FR-134 | Wrong-person-opens-link is a **named residual risk, not solved** — no consignee identity system exists. Mitigation: short expiry `[NEEDS INPUT]`, device/IP fingerprint, flag "unauthenticated party" | Must | BR-906/912 |

## 9. Driver identity assurance at dispatch/pickup — the authentication layer only

Three-agent chain, F1 owns one link: F1 proves the acting session is the authenticated, device-bound
driver session. F7 compares the captured artifact (CDL scan, plate/VIN, selfie) to the dispatch record
(BR-212/221/224). F7/F11 classify and queue the mismatch (BR-806).

| ID | Requirement | Pri | Trace |
|---|---|---|---|
| FR-135 | Dispatch acceptance binds the authenticated driver session to the load's driver+equipment tuple, the object F7's BR-212 acts on | Must | BR-212 |
| FR-136 | Pickup check-in accepted only from an authenticated, device-bound driver session; wrong device rejected before any comparison runs | Must | BR-221/227 |
| FR-137 | Check-in captures a machine-readable identity artifact (CDL scan/selfie) attached to the action record; F1 captures, F7 compares | Must | BR-221 |
| FR-138 | Last-minute change of driver contact channel near dispatch is flagged to F7's review queue, not silently accepted as an identity update | Must | BR-228 |
| FR-139 | On an F7 mismatch signal, F1 suspends further session-scoped actions on that load pending F7/F11 resolution — F1 executes the hold, F7 classifies | Must | BR-221/806, BR-225 |
| FR-140 | Geofence+timestamp of check-in captured as session metadata by F1; geofencing mechanism itself is F8's | Must | OBJ-006 |

## 10. Credential and account recovery — resistant to social engineering

| ID | Requirement | Pri | Trace |
|---|---|---|---|
| FR-141 | Reset via verified channel only (email link / SMS OTP on file); security questions explicitly excluded | Must | OBJ-006 |
| FR-142 | Reset tokens single-use, short expiry `[NEEDS INPUT]` | Must | derived |
| FR-143 | Lost-MFA recovery for a BR-902/907-gated role is never self-service — ops-assisted, re-proofed, logged | Must | §1, OBJ-006 |
| FR-144 | Changing recovery email/phone requires fresh auth + notifies the **old** channel | Must | OBJ-006 |
| FR-145 | All-admins-locked-out recovery is ops-assisted, identity-proofed against onboarding record (§2), never fully automated | Must | OBJ-006 |

## 11. Support impersonation — consented, time-boxed, audited

| ID | Requirement | Pri | Trace |
|---|---|---|---|
| FR-146 | Impersonation is a distinct session type (never the target's own credential), requiring consent or a logged justification when unobtainable | Must | OBJ-006 |
| FR-147 | Impersonation sessions auto-expire, duration `[NEEDS INPUT]`, and every touched screen is visibly bannered (F9) — no indistinguishable UX | Must | derived |
| FR-148 | Starting impersonation requires ops's own fresh MFA (§6) + an elevated permission (F2 defines it, F1 requires the auth event) | Must | BR-907 pattern |
| FR-149 | Every impersonated action audited as actor=ops, on-behalf-of=target, never merged unlabeled into target's history (F3 stores) | Must | OBJ-006 |

## 12. Account and org lifecycle — suspend, offboard, device loss

| ID | Requirement | Pri | Trace |
|---|---|---|---|
| FR-150 | Org suspension revokes every active session for every org user immediately | Must | BR-229 |
| FR-151 | Suspension doesn't retroactively invalidate actions already taken pre-suspension on a load past pickup — in-flight execution not stranded by an auth flag | Must | BR-230 |
| FR-152 | Offboarding one user (driver leaves mid-trip) revokes that session; trip custody/tracking record (F7/F8) persists independently | Must | BR-910 |
| FR-153 | Org admin must bind a replacement driver session to the in-flight load before further driver-scoped actions are accepted (cross-ref F7 reassignment) | Must | BR-910/224 |
| FR-154 | A removed/suspended org's proofed identity (§2) is flagged; re-onboarding under it routes to ops review, resisting ban evasion | Should | BR-229 |

## 13. Language and accessibility

| ID | Requirement | Pri | Trace |
|---|---|---|---|
| FR-155 | Auth flows (login, MFA, recovery, error copy) available in English and Spanish at minimum for drivers | Must | BR-914 |

## 14. API surface (auth; conventions at spine §4 / F4)

| API | Method / path | Idempotency? | FR |
|---|---|---|---|
| API-100 | `POST /v1/orgs` | Yes | FR-100 |
| API-101 | `POST /v1/orgs/{id}/verify-identity` | Yes | FR-101 |
| API-102 | `POST /v1/orgs/{id}/invites` | Yes | FR-106 |
| API-103 | `POST /v1/invites/{token}/accept` | No (token guards) | FR-107 |
| API-104 | `POST /v1/auth/login` | No | — |
| API-105 | `POST /v1/auth/sso/{org_id}/start` | No | FR-113/114 |
| API-106 | `POST /v1/auth/mfa/challenge` | No | FR-116/120 |
| API-107 | `POST /v1/auth/token/refresh` | No | FR-121/125 |
| API-108 | `GET /v1/users/me/sessions` | No | FR-126 |
| API-109 | `DELETE /v1/users/me/sessions/{id}` | No | FR-126/128 |
| API-110 | `DELETE /v1/orgs/{id}/users/{id}/sessions` | No | FR-127 |
| API-111 | `POST /v1/consignee-links` | Yes | FR-129 |
| API-112 | `GET /v1/consignee-links/{token}` | n/a | FR-130/133/134 |
| API-113 | `POST /v1/consignee-links/{token}/submit` | Yes | FR-130 |
| API-114 | `POST /v1/auth/recovery/start` | Yes | FR-141 |
| API-115 | `POST /v1/auth/recovery/mfa-reset` | Yes | FR-143 |
| API-116 | `POST /v1/impersonation/sessions` | Yes | FR-146/148 |
| API-117 | `DELETE /v1/impersonation/sessions/{id}` | No | FR-147 |
| API-118 | `POST /v1/dispatch/{load_id}/checkin` | Yes | FR-136/137 |

## 15. Error names — candidates only, F5 allocates real `ERR-` IDs

`INVALID_CREDENTIALS` · `MFA_REQUIRED` · `MFA_CHALLENGE_FAILED` · `TOKEN_EXPIRED` ·
`TOKEN_ALREADY_USED` · `DEVICE_NOT_REGISTERED` · `SESSION_REVOKED` · `INVITE_EMAIL_MISMATCH` ·
`ORG_NOT_VERIFIED` · `ORG_SUSPENDED` · `STEP_UP_REQUIRED` · `IMPERSONATION_NOT_CONSENTED` ·
`DRIVER_SESSION_MISMATCH_HOLD` · `CONSIGNEE_LINK_EXPIRED` · `CONSIGNEE_LINK_ALREADY_USED`. Canonical
envelope, spine §4; `details.retry_after` etc. `[NEEDS INPUT]`.

## 16. Edge case register

| EC | Trigger | Behaviour | Who decides | Unresolved? |
|---|---|---|---|
| EC-100 | Consignee link forwarded/replayed after use | Flagged "unauthenticated party"; replay shows prior consumption | F1/F9 | Yes — flag only |
| EC-101 | Link opened after expiry | Safe error + relay-back path | F1 | No |
| EC-102 | Owner-operator loses only device | Lost-device flow on the sole session; SLA `[NEEDS INPUT]` | F1 | Partially |
| EC-103 | Driver has no phone / shared family device | Shared device binds sequentially; needs a "switch driver" flow | Product | Yes — flow unspecified |
| EC-104 | Fully offline pickup-to-drop cycle | Queued actions sync via idempotency key; no-reconnect-before-deadline stalls state | F1/F8 | Yes → F7/F4 |
| EC-105 | SSO IdP asserts email on unverified domain | JIT refused, falls to manual invite | F1 | No |
| EC-106 | Impersonation consent unreachable, or session outlives time-box (client bug) | Justification path logged; server-side hard expiry either way | F1 | Escalation authority `[NEEDS INPUT]` |
| EC-107 | Admin offboards driver mid-trip, loaded | Session revoked; trip persists; blocked until reassignment | F1/F7 | Interim gap → F7 |
| EC-108 | Broker's downstream driver never invited as a user | Broker can't dispatch — BR-223 needs driver as User | F1/F7 | Who triggers invite — flag to assembler |
| EC-109 | Two admins race revoke/re-grant same session | Last-write-wins at session store | F3 | Yes |
| EC-110 | Suspended org, in-transit session still valid | Stays valid for that load (FR-151); new actions blocked | F1 | No |
| EC-111 | Reset requested, no login-holding account | Safe, non-enumerating response | F1 | Copy `[NEEDS INPUT]` |
| EC-112 | Driver CDL expires between dispatch and pickup | F1 authenticates check-in; F7's comparison fails and holds (FR-139) | F7/F1 | No |
| EC-113 | Lost phone is both app device and MFA device | Session and MFA recovery must be handled together | F1 | Yes — overlap unmodelled |
| EC-114 | Consignee is also a shipper's posting user elsewhere (ASM-035) | Identities not linked; token flow assumes no account regardless | Product | Yes — matches BRD's own assumption |

**Counts:** FR-100…FR-155 (56) · API-100…API-118 (19) · EC-100…EC-114 (15) · `[NEEDS INPUT]` tags: 13
· open `DEC-`: 2.
