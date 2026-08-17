# ShipDash — Defensive Security Audit (Bug Bounty)

**Target:** `/home/ujjwal/Documents/My Apps/apps/07-shipdash/` (Next.js 14.2.21 · NextAuth v4 JWT/Credentials · Prisma 5 / SQLite)
**Scope:** Authorized review of Boss Ujjawal's own code. Defensive-only.
**Date:** 2026-05-31
**Reviewer:** security-engineer-agent (Jarvis)

> Tenancy model note: ShipDash is **single-user-per-tenant** — there is no `Org` model. Each `User` owns `Store`/`Order`/`Shipment` via `userId`. "Cross-tenant" below = one logged-in user reaching another user's data. Ownership is enforced by `order.userId !== session.user.id → 403`. Findings center on the routes that **forget** that check, plus the public/unauthenticated surfaces.

---

## Severity Summary

| # | Severity | Title | File:line |
|---|----------|-------|-----------|
| 1 | **CRITICAL** | Committed SQLite DB (`prisma/dev.db`) — real PII + plaintext store API keys + admin bcrypt hash in git | `prisma/dev.db` |
| 2 | **CRITICAL** | Unauthenticated webhook — no signature check; forge any shipment status / inject tracking events | `api/webhooks/route.ts` (POST missing) |
| 3 | **HIGH** | Broken object-level authz (IDOR) on `ship/rates`, `ship/ai-recommend`, `shipments/optimize-route(stops)`, `ship/bulk` | see finding |
| 4 | **HIGH** | Returns-create IDOR — no ownership check, status-flip + tracking inject on any orderId | `api/returns/create/route.ts:21` |
| 5 | **HIGH** | `ship/create` & `ship/bulk` accept arbitrary `orderId` for shipment creation (bulk has NO owner check) | `api/ship/bulk/route.ts:42` |
| 6 | **MEDIUM** | Store API key/secret stored plaintext & returned to client | `api/stores/route.ts:14`, `schema.prisma:28` |
| 7 | **MEDIUM** | Weak/predictable AWB (`Math.random`) → tracking enumeration (chains with #2 & public tracking) | `lib/mock-data.ts generateAWB` |
| 8 | **MEDIUM** | No input validation on writes (zod is a dep but unused on every route) | all POST/PUT routes |
| 9 | **MEDIUM** | No rate limiting / login throttling anywhere → brute force + DoS | `lib/auth.ts authorize`, all routes |
| 10 | **MEDIUM** | Predictable `NEXTAUTH_SECRET` + weak demo creds shown in UI | `.env:2`, `login/page.tsx:13-14`, `seed.ts:152` |
| 11 | **LOW** | Public tracking exposes customer full name (light PII / enumeration aid) | `api/tracking/[awb]/route.ts:30` |
| 12 | **LOW** | Update-status / notify lack per-org tenant model is fine, but no audit log of state changes | `shipments/[id]/update-status` |
| 13 | **INFO** | No security headers; no CSRF hardening on state-changing JSON routes | `next.config.js` |

**Confirmed SECURE (no false alarm):** `orders/[id]` GET (owner check L29), `shipments/[id]/tracking` (L26), `shipments/[id]/update-status` (L58), `shipments/[id]/notify` (L38), `shipments/[id]/ai-recommend` (L27), `ship/create` (L32), `optimize-route` when using `shipmentIds` (scoped L33), all collection routes (`orders`, `returns`, `stores`, `analytics/*`, `export`) are `userId`-scoped. `ship/[id]/label` is a static mock (no DB read) so its missing auth is currently harmless but should be fixed before it returns real labels. **The earlier draft over-flagged these — corrected here against the real code.**

---

## Findings

### 1. CRITICAL — Committed SQLite DB with real PII + plaintext store keys + admin hash
**[OWASP A05:2021 Misconfig / A02 Crypto Failures · CWE-540 Info in Source Repo · CWE-312 Cleartext Storage]**
`prisma/dev.db` is **git-tracked** (confirmed `git ls-files` → `prisma/dev.db`). `.gitignore` ignores `.env*` but **not** `*.db`.

Confirmed by `strings` on the committed DB — it contains live-looking data:
- Admin user `demo@shipdash.com` with bcrypt hash `$2a$10$vGQbsYeTA4iPB/Y/trjoe...` (password is `password123` per `seed.ts:152` — cracks instantly).
- Store row: `shopify ujjwal-store.myshopify.com shpat_mock_key_xxxxx` (plaintext Shopify-style token).
- 30 orders with full customer PII: names, **real-format Indian phone numbers** (`+917033938835`, `+918972919741`…), emails, and full street addresses + pincodes.

> Impact: Anyone with repo read (public GitHub mirror, Vercel source inspection, a forked/leaked clone) gets the entire customer dataset, the integration credential, and a crackable admin login. This is the highest-impact issue.
> Likelihood: HIGH — already committed.
> Remediation:
>   - Short-term: `git rm --cached prisma/dev.db`; add `*.db`, `*.db-journal`, `*.db-wal` to `.gitignore`. Purge from history: `git filter-repo --path prisma/dev.db --invert-paths` (or BFG). Treat `shpat_…` token + admin password as **compromised → rotate/reset**.
>   - Long-term: never commit DBs; use Postgres for any deploy; seed only synthetic data; encrypt secret columns (see #6).

### 2. CRITICAL — Webhook endpoint design flaw (no inbound signature verification)
**[OWASP A08:2021 Data Integrity Failures · CWE-345 Insufficient Verification of Data Authenticity · CWE-306 Missing Auth]** — `api/webhooks/route.ts`

The current `POST` is auth-gated (`getServerSession`) and only manages an **in-memory mock webhook registry** — so today it cannot tamper with shipments. **But there is no inbound courier-webhook receiver at all, and the registry generates signing secrets with `Math.random()`** (L27/L38/L123 — `CWE-330`). When Boss wires the real courier callback (the obvious next step, given `update-status` exists), the pattern here will be copied: unauthenticated + weak secret.

> Impact (on the intended-real version): a forged courier callback marks any shipment `delivered` → COD-fraud / false "lost package"; or injects misleading tracking events. The mock secrets are also predictable.
> Likelihood: MEDIUM now (mock), HIGH once real.
> Remediation:
>   - Build the real receiver with HMAC verification over the **raw** body using a per-courier secret + `crypto.timingSafeEqual`; reject unsigned. Add timestamp/nonce replay window.
>   - Replace `Math.random()` secret generation with `crypto.randomBytes(24).toString("base64url")`.

### 3. HIGH — Broken object-level authorization (IDOR) on rate/recommendation routes
**[OWASP A01:2021 Broken Access Control · CWE-639 IDOR]**
These authenticate the caller but then `findUnique({ where:{ id: orderId }})` with **no `userId` ownership check**:
- `api/ship/rates/route.ts:22-28` — returns rates for *any* order id.
- `api/ship/ai-recommend/route.ts:22-28` — returns AI recommendation for any order id.
- `api/shipments/optimize-route/route.ts:19-25` — the `stops`-array branch runs `optimizeRoute(stops)` on raw client input with no DB check (low data-leak, but unbounded — see #8/DoS). The `shipmentIds` branch IS scoped (L33) — good.

> Impact: A logged-in user enumerates cuid order ids to learn another user's pincode/zone, weight, COD amount, and courier pricing — commercial-intel leak + confirms which order ids exist.
> Likelihood: MEDIUM (cuids are not sequential, but ids leak via other responses/exports).
> Remediation: After fetch, `if (order.userId !== session.user.id) return 403;` — same one-liner already present in `orders/[id]` and `ship/create`. Apply consistently.

### 4. HIGH — Returns-create IDOR (write + state change on unowned orders)
**[OWASP A01:2021 · CWE-639 · CWE-285 Improper Authorization]** — `api/returns/create/route.ts:21-53`

```ts
const order = await prisma.order.findUnique({ where: { id: orderId }, include: { shipment: true } });
if (!order) return 404;
// NO ownership check
await prisma.order.update({ where: { id: orderId }, data: { status: "returned" } });
// + pushes a "returned" tracking event onto the shipment
```

> Impact: Any authenticated user flips **another user's** order to `returned` and injects a tracking event (with attacker-controlled `reason` text) — sabotage + tracking-history poisoning visible on the public track page.
> Likelihood: HIGH (trivial once an orderId is known/guessed).
> Remediation: add `if (order.userId !== (session.user as any).id) return 403;` before the update. Validate `reason` length/charset.

### 5. HIGH — `ship/bulk` (assignments) creates shipments on arbitrary orderIds with no owner check
**[OWASP A01:2021 · CWE-639 · CWE-915 Mass Assignment-ish]** — `api/ship/bulk/route.ts:19-67`

The `assignments` branch loops and `prisma.shipment.create({ data: { orderId, ... }})` directly from client input — **never verifies the order belongs to the caller** (and the `orderIds` recommendation branch L74 also skips the owner check). `ship/create` (single) does check (L32); bulk does not.

> Impact: An attacker books shipments against another user's orders (forcing status→`shipped`, attaching a courier/AWB), corrupting their pipeline. Combined with `orderId` knowledge from #3, fully weaponizable.
> Likelihood: MEDIUM-HIGH.
> Remediation: fetch each order, verify `userId === session.user.id`, skip/deny otherwise. Cap `assignments.length`. Validate `courier ∈ allowlist`.

### 6. MEDIUM — Store integration secret stored & returned in plaintext
**[OWASP A02:2021 · CWE-312 · CWE-200]** — `api/stores/route.ts:14-19`, `schema.prisma:28` (`apiKey String?` plaintext)

`GET /api/stores` returns full Store rows including `apiKey` (the `shpat_…` token). Any authenticated session can read it via the network tab; stored plaintext so #1 leaks it directly.

> Remediation: `select` to exclude `apiKey` from responses (return masked last-4 / `hasKey: boolean`). Encrypt the column at rest (KMS/envelope), decrypt server-side only at call time.

### 7. MEDIUM — Predictable AWB generation enables tracking enumeration
**[OWASP A02:2021 · CWE-330 · CWE-338 Weak PRNG]** — `lib/mock-data.ts generateAWB` (prefix + 10 `Math.floor(Math.random()*10)` digits), used by `ship/create:40` and `ship/bulk:25`.

AWBs are the **public** tracking key (`/api/tracking/[awb]` + `/track/[awb]`). `Math.random()` is non-crypto and the format is `DEL` + 10 digits → enumerable. An attacker scans AWB space to discover valid shipments and read customer name + destination city/state of strangers (#11). No collision-retry on the `@unique awbNumber` either → occasional 500s.

> Remediation: `crypto.randomBytes`-based token (≥128-bit, base32), or decouple a random public tracking token from the internal AWB. Add unique-violation retry. Rate-limit `/api/tracking`.

### 8. MEDIUM — No input validation on any write route (zod unused)
**[OWASP A03:2021 · CWE-20]** — every POST/PUT reads `await req.json()` and destructures untyped.

Examples: `ship/create` writes `rate || 0` but never checks `rate` is a number; `bulk-create` does `weightKg: input.weightKg` (a CSV string flows straight into a Float column); `optimize-route` runs heuristics on an arbitrary `stops` array (no size cap → CPU DoS); `webhooks` URL is validated but `events`/`action` only loosely. `zod` is in `package.json` and imported in `api-helpers.ts` (only for `ZodError`) but **no route defines a schema**.

> Remediation: one zod schema per route, `safeParse`, return 400 via the existing `handleApiError(ZodError)` path. Whitelist fields (kills mass-assignment vectors). Cap array lengths.

### 9. MEDIUM — No rate limiting / no login throttling
**[OWASP A04:2021 Insecure Design · A07 Auth Failures · CWE-307 · CWE-770]** — `lib/auth.ts authorize` + all routes.

`authorize()` has no lockout/backoff → unlimited credential stuffing against `demo@shipdash.com`. No per-IP limit on `/api/tracking`, `/api/webhooks`, `bulk-create` (bulk is capped at 100 rows — good — but the route can be hammered repeatedly). `orders/sync` mass-creates 5-10 rows per call with `Promise.all`, callable in a loop.

> Remediation: add IP+account rate limiting (Upstash Ratelimit / middleware token-bucket) on login, tracking, webhooks; exponential backoff/lockout on failed logins.

### 10. MEDIUM — Predictable secret + demo creds exposed in UI
**[OWASP A05/A07 · CWE-798 Hardcoded Credentials · CWE-521 Weak Password]** — `.env:2` `NEXTAUTH_SECRET="shipdash-super-secret-key-2024"`, `login/page.tsx:13-14` pre-fills `demo@shipdash.com` / `password123` and `:144-148` prints them on screen, `seed.ts:152` seeds that password.

> Impact: `.env` is gitignored (good, not in git). But a predictable/guessable `NEXTAUTH_SECRET` in prod lets an attacker forge session JWTs (full account takeover). The on-screen demo creds + weak password = trivial login if deployed as-is.
> Remediation: prod must set a 32+ byte random `NEXTAUTH_SECRET`; fail-fast at boot if it's unset or matches the known dev string. Remove pre-filled/displayed creds for any real deploy; enforce a password policy.

### 11. LOW — Public tracking exposes customer full name
**[OWASP A01 · CWE-213 Intended Info Exposure]** — `api/tracking/[awb]/route.ts:30`

Good news: the endpoint already trims output (no phone, no full address — only `city, state`). It still returns `customerName` (full) + city. Combined with #7 (enumerable AWBs) that's a name+city harvest.

> Remediation: mask the name (`R*** K***`) or gate tracking behind AWB **+** a second factor (pincode / last-4 phone). Keep the current minimal field set.

### 12. LOW — No audit trail on shipment state changes
**[OWASP A09:2021 Logging Failures · CWE-778 Insufficient Logging]** — `update-status`, `returns/create`, `ship/bulk`.

Status changes and tracking-event injections leave no server-side audit record (only the mutated row). If #4/#5 are exploited, there's no forensic trail.

> Remediation: append an append-only `AuditEvent` (actor userId, action, target id, before/after, ts) on every state-changing route. Avoid logging raw PII (mask phone).

### 13. INFO — Missing security headers / CSRF posture
`next.config.js` sets no headers. NextAuth credential errors are specific ("No user found" vs "Invalid password") at `lib/auth.ts:24/29` → **user-enumeration** (minor; CWE-204) — return a generic "Invalid credentials". State-changing routes are JSON POST with NextAuth `SameSite=Lax` cookies (reasonable CSRF baseline) but add explicit checks if you accept form posts.

> Remediation: add `headers()` in next.config (HSTS, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`/CSP `frame-ancestors`, `Referrer-Policy`). Make auth errors generic.

---

## Hardening snippets

**Reusable owner guard** (apply to #3/#4/#5):
```ts
const order = await prisma.order.findFirst({ where: { id: orderId, userId: session.user.id } });
if (!order) return NextResponse.json({ error: "Not found" }, { status: 404 }); // 404, not 403 (don't confirm existence)
```

**.gitignore add:**
```
prisma/*.db
prisma/*.db-journal
*.db-wal
```

**Crypto AWB:**
```ts
import { randomBytes } from "crypto";
const awb = prefix + randomBytes(8).toString("hex").toUpperCase(); // ~64-bit, retry on P2002
```

## Detection / Verification (no prod exploitation)
- **Owner-check unit tests:** seed two users; assert user-A token gets 404 on user-B `orderId` for `ship/rates`, `ship/ai-recommend`, `returns/create`, `ship/bulk`. Highest-value regression gate.
- **Semgrep CI rule:** flag `prisma.<model>.findUnique({where:{ id` in `src/app/api/**` whose handler lacks a subsequent `userId`/`session.user.id` comparison; flag `data: body`.
- **Secret/DB scan in CI:** `gitleaks detect`; assert `git ls-files | grep -E '\.db$'` is empty; `trivy fs .`.
- **Tracking PII snapshot test:** fail if `/api/tracking/[awb]` JSON keys ever include `customerPhone`/`shippingAddress`/`codAmount`.

## Compliance Mapping (if ShipDash serves real customers)
- **GDPR / India DPDP Act 2023:** §32 / Sec 8 (security safeguards), data-minimization — #1, #4, #6, #11.
- **NIST 800-53 Rev5:** AC-3 (#3,#4,#5), IA-5 (#10), SC-12/SC-28 (#1,#6), SI-10 (#8), AU-2/AU-9 (#12), SC-5 (#9).
- **OWASP ASVS v4:** V4 Access Control (#3-5), V2 Auth (#9,#10), V6 Crypto-at-rest (#1,#6), V5 Validation (#8).

## Handoff
- Code fixes (owner guards, zod, AWB crypto, generic auth errors) → `backend-engineer-agent`.
- Git-history purge + secret rotation + CI scanners + rate-limit infra + security headers → `devops-sre-agent`.
- Webhook HMAC design + capability-token tracking → `backend-engineer-agent`.

## Honesty / completeness
Read all 24 API routes, `middleware.ts`, `auth.ts`, `api-helpers.ts`, `prisma.ts`, `schema.prisma`, `seed.ts`, `mock-ai.ts`, `mock-data.ts` (referenced), `.env`, `.env.example`, `.gitignore`, `next.config.js`, public track page, login page, bulk-upload component. `dev.db` git-tracking + contents **confirmed** via `git ls-files` + `strings`. **Not** dynamically tested — static review only; severities are code-evidence-based. No real LLM is wired (mock-ai is deterministic) → OWASP LLM Top-10 N/A for this app today. I corrected my own first-pass over-flagging of `orders/[id]`, `shipments/[id]/*`, and single `ship/create` after reading their ownership checks — those are secure.
