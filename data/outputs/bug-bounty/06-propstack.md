# PropStack — Defensive Security Audit (Bug Bounty)

**Target:** `/home/ujjwal/Documents/My Apps/apps/06-propstack/` (Next.js 16 + NextAuth v4 credentials + Prisma/SQLite real-estate manager)
**Scope:** Authorized review of Boss Ujjawal's own code. Defensive-only.
**Date:** 2026-05-31
**Reviewer:** security-engineer-agent (Jarvis)

> **Honesty note (important).** My first pass *suspected* mass IDOR. After reading every route line-by-line, that was **wrong** — almost every `[id]` and id-by-body endpoint **correctly scopes by `landlordId`** (via `findFirst({ where: { id, landlordId } })` or `where: { property: { landlordId } }`, then a separate existence check before `update`/`delete`). Credit where due: properties, tenants, rent/record, leases/renew, maintenance/status, payments/receipt, ai-rent, rent/ledger, payments/overdue, reports, expenses POST, tenants POST — **all enforce ownership.** This is a genuinely well-authorized codebase. The findings below are the **real** residual issues, not boilerplate. SQL injection is **not present** (Prisma parameterizes everything; no `$queryRaw`). No file-upload handler exists, so "unrestricted upload / path traversal" is **N/A** (evidence at bottom).

---

## Severity Summary

| # | Severity | Category | Title | File |
|---|----------|----------|-------|------|
| 1 | **HIGH** | OWASP A01 / CWE-639 / IDOR + mass-assign | `maintenance` POST writes whole body unscoped — inject records into another landlord's property/tenant | `api/maintenance/route.ts:65-66` |
| 2 | **HIGH** | OWASP A02 / CWE-1188 / CWE-798 | Hardcoded placeholder `NEXTAUTH_SECRET` ("change-in-production") | `.env:2` |
| 2b | **HIGH** | OWASP A02 / CWE-312 / CWE-532 | `prisma/dev.db` (SQLite with bcrypt password hashes + tenant PII) committed to git | `prisma/dev.db` |
| 3 | **MEDIUM** | OWASP A04 / CWE-307 / CWE-770 | No rate limiting anywhere (credential stuffing on login, enumeration, DoS) | app-wide |
| 4 | **MEDIUM** | OWASP A05 / CWE-862 | `/api/*` not in auth middleware matcher (defense-in-depth gap) | `src/middleware.ts:9-19` |
| 5 | **MEDIUM** | OWASP A05 / CWE-209 | Raw `error.message` returned to client on 500 | `src/lib/api-helpers.ts:36` |
| 6 | **MEDIUM** | OWASP A03 / CWE-79 | Unescaped tenant `notes` / custom `message` interpolated into receipt/email HTML (stored XSS when rendered/sent) | `payments/[id]/receipt/route.ts:130`, `tenants/[id]/notify/route.ts:167` |
| 7 | **LOW** | OWASP A09 / CWE-532 | Tenant PII (name/phone/email/rent) written to `console.log` | `rent/remind`, `tenants/[id]/notify`, `rent/record` |
| 8 | **LOW** | OWASP A04 / CWE-770 | `generate-monthly` N+1 query-per-tenant loop (resource amplification) | `rent/generate-monthly/route.ts:28-50` |
| 9 | **LOW** | OWASP A05 / CWE-1127 | `typescript.ignoreBuildErrors: true` ships type-unsafe code | `next.config.ts:5` |
| 10 | **INFO** | OWASP A07 / CWE-203 | Login user-enumeration via early-return timing (no bcrypt on missing user) | `src/lib/auth.ts:50-57` |
| — | N/A | — | File upload / path traversal — **no upload handler exists** | (evidence below) |
| — | OK | — | IDOR on properties/tenants/rent/leases/receipts — **correctly scoped** | (verified) |

---

## Findings

### [HIGH] #1 — `maintenance` POST is unscoped (IDOR + mass-assignment)
`src/app/api/maintenance/route.ts:65-71`

```ts
const parsed = createMaintenanceSchema.safeParse(body);   // {propertyId, tenantId, title, description, priority}
...
const request = await prisma.maintenanceRequest.create({
  data: parsed.data,          // <-- propertyId + tenantId taken straight from the request, NEVER ownership-checked
  include: { property: {...}, tenant: {...} },
});
```
> **This is the one real authorization hole.** Every *other* create path validates ownership first — `tenants` POST (`tenants/route.ts:56-62`) and `expenses` POST (`expenses/route.ts:63-69`) both do `prisma.property.findFirst({ where: { id: propertyId, landlordId } })` before creating. **`maintenance` POST does not.** It also never stamps a `landlordId` (the model has none), so there's nothing tying the row back to the caller.
> **Impact:** Any authenticated landlord can POST a maintenance request with a `propertyId`/`tenantId` belonging to *another* landlord. The forged ticket then appears in the victim's property detail view and maintenance list (those reads join via `property.landlordId`, so the victim *sees* it). Cross-tenant data injection / pollution / integrity break; attacker-controlled `title`/`description` render in the victim's dashboard.
> **Likelihood:** Medium-High. Needs a valid `propertyId`+`tenantId` of the victim; cuids aren't sequential, but they leak in other responses and shared URLs.
> **Asset affected:** Victim landlords' maintenance data and dashboard integrity.
> **Remediation (mirror the pattern the other routes already use):**
> ```ts
> const owns = await prisma.property.findFirst({
>   where: { id: parsed.data.propertyId, landlordId: session.user.id },
> });
> if (!owns) return NextResponse.json({ error: "Property not found" }, { status: 404 });
>
> const tenantOk = await prisma.tenant.findFirst({
>   where: { id: parsed.data.tenantId, propertyId: parsed.data.propertyId, landlordId: session.user.id },
> });
> if (!tenantOk) return NextResponse.json({ error: "Tenant not found" }, { status: 404 });
> ```
> Long-term: add `landlordId` to `MaintenanceRequest` and a shared `assertOwnsProperty(id, landlordId)` helper so no future create can skip the check.

### [HIGH] #2 — Hardcoded placeholder NEXTAUTH_SECRET
`.env:2` — `NEXTAUTH_SECRET="propstack-secret-key-change-in-production"`

> **Impact:** NextAuth signs session JWTs (HS256) with this secret. It's a guessable English literal. Anyone who knows/guesses it can **forge a valid session JWT for any landlordId** — full auth bypass that would turn every ownership check above into a no-op (attacker just signs a token with the victim's `id`). The literal "change-in-production" strongly implies it was never rotated.
> **Likelihood:** High *if* this value reached the deployed env. `.env` is correctly gitignored (verified: not tracked, never in git history), but placeholder secrets commonly get copy-pasted into the host.
> **Remediation:**
> - Now: `openssl rand -base64 48`, set in Vercel project env (not repo), rotate. Rotation invalidates all current sessions (good).
> - Long-term: fail-fast on boot if `NEXTAUTH_SECRET` is missing or in a known-placeholder denylist.

### [HIGH] #2b — SQLite database committed to git
`prisma/dev.db` — **tracked** (verified: `git ls-files` lists `prisma/dev.db`).

> **Impact:** The live SQLite DB is in version control. It contains the `Landlord` table — **bcrypt password hashes**, emails, names, phones — plus all tenant PII (names, phones, emails, rent amounts, security deposits) and financial ledgers. Anyone with repo access (or the public repo, if it's pushed to a public remote) gets the entire dataset and can run offline bcrypt cracking against the hashes. The `.gitignore` does **not** exclude `*.db`, so it was added and keeps re-committing on every data change.
> **Likelihood:** High wherever the repo is shared/pushed. Even after deletion, it persists in git history.
> **Remediation:**
> - Add `*.db` / `prisma/*.db` to `.gitignore`.
> - `git rm --cached prisma/dev.db` and commit.
> - **Purge from history** (`git filter-repo --path prisma/dev.db --invert-paths` or BFG) since hashes/PII are already exposed in past commits.
> - Treat all committed credentials as compromised: force a password reset for any real Landlord accounts and rotate #2's secret.

### [MEDIUM] #3 — No rate limiting (credential stuffing + enumeration + DoS)
App-wide; worst on `/api/auth` (NextAuth credentials) and `rent/generate-monthly`.

> **Impact:** Login has no throttle → unlimited bcrypt brute force / credential stuffing. The (correctly-scoped) object endpoints can still be hammered to enumerate ids and confirm 404-vs-200. No per-IP / per-account cap anywhere (CWE-307 / CWE-770).
> **Remediation:** Add IP+account rate limiting (Upstash Ratelimit, `@vercel/firewall`, or a middleware token bucket) on `/api/auth/*`, and a global per-session cap on object endpoints. Lockout/backoff after N failed logins.

### [MEDIUM] #4 — `/api/*` excluded from auth middleware
`src/middleware.ts:9-19` — matcher lists only page routes; **no `/api/...`** (verified via grep).

> **Impact:** Not an open door *today* — every API handler re-checks `getServerSession` inline. But it removes the centralized net: a future route added without that boilerplate is silently public. Defense in depth.
> **Remediation:** Add `"/api/:path*"` to the matcher excluding `/api/auth/*`, or adopt a `withApiAuth` wrapper so auth can't be forgotten.

### [MEDIUM] #5 — Verbose error leakage
`src/lib/api-helpers.ts:36` — `return NextResponse.json({ error: error.message }, { status: 500 })`

> **Impact:** Raw `error.message` (Prisma internals, constraint names, ids) returned to the client on any unhandled error (CWE-209). Aids recon.
> **Remediation:** Log full error server-side with a correlation id; return generic `{ error: "Internal server error", ref }` in non-dev.

### [MEDIUM] #6 — Unescaped user data in generated HTML (stored XSS surface)
`payments/[id]/receipt/route.ts:130` (`${ledgerEntry.notes}`) and `tenants/[id]/notify/route.ts:167` (`${parsed.data.message}`)

> **Impact:** The receipt endpoint returns `text/html` and interpolates `ledgerEntry.notes` directly into the page; `notes` is attacker-controllable via `rent/record` (a landlord sets it on their own ledger). The notify route builds an email body with raw `${message}` and `${tenant.name}`. Today the receipt is only viewable by the owning landlord (self-XSS, low) and email is mocked (console only). **But** the moment (a) receipts are shared with tenants, or (b) real SMTP is wired, this becomes stored XSS / HTML-injection in messages your trusted sender delivers. CWE-79.
> **Remediation:** HTML-escape every interpolated value before templating (a tiny `escapeHtml()` helper, or render via a templating lib that escapes by default). Do this proactively before email/sharing ships.

### [LOW] #7 — PII in console logs
`rent/remind/[tenantId]/route.ts:28-29`, `tenants/[id]/notify/route.ts:181-189`, `rent/record/route.ts:83`

> Tenant `name`, `phone`, `email`, `rentAmount` and message bodies are `console.log`-ged. In prod these land in host log aggregation, retained and broadly readable (CWE-532, GDPR concern).
> **Remediation:** Redact (`em***@domain`, mask phone) or log ids only; route real sends through a provider SDK, never console.

### [LOW] #8 — N+1 loop in generate-monthly (resource amplification)
`rent/generate-monthly/route.ts:28-50` — a `findFirst` + `create` per tenant in a `for` loop.

> Unbounded by tenant count and unthrottled (pairs with #3). A landlord with many tenants (or repeated calls) drives a query storm against SQLite.
> **Remediation:** One `findMany` for existing periods + a single `createMany({ skipDuplicates: true })`. Add a uniqueness constraint on `(tenantId, period)` in the schema.

### [LOW] #9 — `ignoreBuildErrors: true`
`next.config.ts:5` — suppresses all TypeScript errors at build.

> Hides null/typo/type bugs from CI. Remove it; keep the build red on type failures.

### [INFO] #10 — Login user enumeration
`src/lib/auth.ts:50-57` — returns `null` immediately when the email isn't found (no bcrypt run) vs. running bcrypt when it is.

> Timing difference lets an attacker enumerate valid landlord emails (CWE-203). Low alone; compounds with #3.
> **Remediation:** Always run a bcrypt compare against a dummy hash when the user is absent; keep the failure generic.

### [N/A] File upload / path traversal
> Grepped full `src/`: no multipart parser, no `fs.writeFile`, no upload route. `Property.photoUrls`/`MaintenanceRequest.photoUrls` are JSON-string arrays and `Expense.receiptUrl` is a plain string — client-supplied URLs persisted as-is (no current PUT/POST even writes `photoUrls`). Classic upload/traversal does not apply. If photo display is added later, validate they are `https://` on an allowlisted host before rendering (avoids the same XSS class as #6).

### [OK / Verified secure]
> - **IDOR — properties, tenants, rent/record, leases/renew, maintenance/status, payments/receipt, ai-rent, rent/ledger, payments/overdue, reports/pnl, reports/tax-summary, expenses POST, tenants POST, rent/dashboard, leases/expiring, dashboard** — all enforce `landlordId` scoping. Confirmed line-by-line.
> - **SQL injection** — none; Prisma parameterizes, no raw SQL.
> - **Input validation** — Zod schemas on every mutating route (good).
> - **`.env`** — correctly gitignored and not tracked (verified). (Note: `prisma/dev.db` is the exception — see #2b.)

---

## Root Cause & Priority

The codebase is fundamentally sound on authorization — the dominant pattern is correct ownership scoping. The real risk is **one inconsistent route (#1 maintenance POST)** plus the **weak signing secret (#2)** that, if it shipped, would undermine everything.

**Fix order:** #2 (rotate secret) → #1 (scope maintenance POST) → #3/#4 (rate limit + middleware) → #5/#6 (error hygiene + HTML escaping before email/sharing ships) → #7-#10.

**Verification (non-exploit):** integration test — landlord A's token POSTing maintenance with landlord B's `propertyId` must 404. Remove `ignoreBuildErrors` and run `npm run build`. Add a Semgrep rule flagging `prisma.<model>.create({ data: parsed.data })` in `route.ts` where the parsed schema contains a foreign-key field (`propertyId`/`tenantId`) and no preceding `findFirst({...landlordId...})` guard.
