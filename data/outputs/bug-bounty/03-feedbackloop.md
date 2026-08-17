# Bug Bounty / Defensive Security Audit — FeedbackLoop

- **Target:** `03-feedbackloop` (Next.js 16.1.6 + NextAuth v4 + Prisma 7 / SQLite)
- **Path:** `/home/ujjwal/Documents/My Apps/apps/03-feedbackloop/`
- **Scope:** Authorized review of Boss's own code (defensive). Reviewed: schema, auth, middleware, all 20 API routes, webhook + notification libs, seed, env, next config.
- **Date:** 2026-05-31
- **Auditor:** security-engineer-agent (defensive-only)

> **Headline:** This codebase is actually *well-built* on the core authZ axis. Every data API route calls `getServerSession` and scopes queries by `orgId` via `findFirst({ where: { id, orgId } })`. I found **no IDOR, no broken org-scoping, no missing-auth data route, no SQL injection** (Prisma parameterizes everything). The real issues are: a weak/static auth secret, **complete absence of rate-limiting** on public-reachable auth + abuse-prone endpoints, **stored XSS in the HTML report generator**, internal error-message leakage, and an SSRF design landmine baked into the webhook sender for when it stops being a mock. The task brief mentioned "public survey response endpoints" — **those do not exist in this build**; `POST /api/feedback` requires a session. Flagged below as INFO so you know it was checked, not skipped.

---

## Severity Summary

| # | Severity | Category | Issue | Location |
|---|----------|----------|-------|----------|
| 0 | **CRITICAL** | OWASP A02 / CWE-312 / CWE-200 | `prisma/dev.db` is **committed to git** — ships real bcrypt password hashes + all customer PII (emails/names) | tracked in repo |
| 1 | **HIGH** | OWASP A07 / CWE-798 / CWE-330 | Weak, static, predictable `NEXTAUTH_SECRET` (`feedbackloop-secret-key-2024`) | `.env:2` |
| 2 | **HIGH** | OWASP A03 / CWE-79 / LLM02 | Stored XSS in HTML report (feedback content interpolated unescaped) | `api/reports/generate/route.ts:51-248` |
| 3 | **HIGH** | OWASP A04 / CWE-770 | No rate-limiting anywhere → credential stuffing, sync/AI/report DoS | all routes; esp. `[...nextauth]`, `integrations/[id]/sync`, `reports/generate` |
| 4 | **MEDIUM** | OWASP A10 / CWE-918 | SSRF design landmine in webhook sender (URL stored unvalidated; mock today, RCE-adjacent when wired) | `lib/webhook-sender.ts:23-96`, `api/webhooks/route.ts:8-9` |
| 5 | **MEDIUM** | OWASP A05 / CWE-209 | Internal error messages + stack-trigger leaked to client | `lib/api-helpers.ts:36` |
| 6 | **MEDIUM** | OWASP A05 / CWE-1188 | Build ignores all TypeScript errors (`ignoreBuildErrors: true`) | `next.config.ts:5` |
| 7 | **MEDIUM** | OWASP A04 / CWE-789 | Unbounded/negative pagination + integer abuse on list endpoints | `api/feedback/route.ts:26-27`, `notifications/route.ts:24` |
| 8 | **LOW** | OWASP A07 / CWE-1392 | Default demo credentials seeded + pre-filled in login form | `prisma/seed.ts:26-36`, `login/page.tsx:12-13` |
| 9 | **LOW** | OWASP A09 / CWE-532 | Webhook delivery + secret presence logged to console | `lib/webhook-sender.ts:57-62` |
| 10 | **LOW** | OWASP A01 / CWE-639 | No role enforcement — every user is `admin`; `role` claim unused | `schema.prisma:15`, `lib/auth.ts` |
| 11 | **LOW** | OWASP A04 / CWE-352 | No explicit CSRF defense on state-changing JSON routes (mitigated by NextAuth, but assumed not enforced) | all mutating routes |
| 12 | **INFO** | — | Broken `prisma.ts` earlier had duplicate import (now fixed); `export const prisma2` dead code | `lib/prisma.ts:15` |
| 13 | **INFO** | — | "Public survey response endpoint" from brief **does not exist**; feedback POST is auth-gated | `api/feedback/route.ts:69-99` |

---

## Findings

---

**[CRITICAL]** [OWASP A02:2021 (Cryptographic Failures / sensitive data exposure) / CWE-312 (Cleartext Storage) / CWE-200] — The SQLite database is committed to the git repository

`git ls-files` → **`prisma/dev.db` is tracked.** (`.gitignore` ignores `.env` correctly, but the DB file was force-added or added before the ignore rule.)

> **Impact:** The committed `dev.db` contains the full seeded dataset: the `User` table with **bcrypt password hashes** for `demo@feedbackloop.io` and `sarah@feedbackloop.io`, every customer's `customerEmail` + `customerName` (real-looking PII: `sarah.m@gmail.com`, `james.w@outlook.com`, etc.), all feedback content, and the seeded webhook **secrets** (`whsec_demo_slack_secret`, `whsec_demo_analytics_secret`) and webhook URLs. Anyone with repo read access (or anyone the repo is ever pushed to publicly — GitHub, a portfolio mirror) can `sqlite3 prisma/dev.db .dump` and read all of it. Bcrypt hashes are offline-crackable (and `password123` cracks in milliseconds against any wordlist). If the same secret/password patterns are reused in a real deployment, this is a direct path to account takeover. PII in a public repo is also a GDPR/notification problem.
> **Likelihood:** High — it's already in history, and history is forever unless rewritten.
> **Asset affected:** All seeded credentials, all PII, all webhook secrets.
> **Existing mitigations:** Repo appears local/private currently (single "Initial commit"). That's the only thing saving it.
> **Remediation:**
>   - Short-term: `git rm --cached prisma/dev.db`, add `prisma/*.db` + `*.db` + `*.sqlite*` to `.gitignore`, commit. Then **purge it from history** (`git filter-repo --path prisma/dev.db --invert-paths` or BFG) before this repo is ever pushed anywhere. Rotate every secret/credential that was in it.
>   - Long-term: never commit databases. Provide a `seed` script + `migrate` to recreate state. For prod use Postgres (the `.env.example` already points to Postgres) with secrets in the platform vault. Add a CI check / pre-commit hook that blocks `*.db`/`*.sqlite` and runs `gitleaks`.

---

**[HIGH]** [OWASP A07:2021 / CWE-798 (Hardcoded Credentials) / CWE-330 (Weak Randomness)] — Static, guessable NextAuth session secret

`/.env:2`
```
NEXTAUTH_SECRET="feedbackloop-secret-key-2024"
```

> **Impact:** `NEXTAUTH_SECRET` signs the JWT session token (strategy is `jwt`, `lib/auth.ts:46`). If an attacker knows or guesses this string, they can **forge a valid session JWT for any `orgId` / `userId`**, bypassing authentication entirely and reading/writing any organization's feedback, webhooks, integrations. The value is a human-readable slug, not random — trivially guessable, and the exact string `your-secret-key-change-this-in-production` ships in `.env.example` (devs often deploy that verbatim).
> **Likelihood:** High (if this ever deploys to a shared/public host).
> **Asset affected:** Every org's data; full auth bypass.
> **Existing mitigations:** `.env` IS correctly gitignored (`git check-ignore .env` confirms) so the secret string is not in the repo. (Note: `prisma/dev.db` is NOT ignored — see Finding 0.) The remaining risk is the secret value being a guessable slug + the `.env.example` placeholder pattern.
> **Remediation:**
>   - Short-term: regenerate now → `openssl rand -base64 32`, put it in `.env`, never reuse across apps. In Vercel set it as an encrypted env var, not in a committed file.
>   - Long-term: add a startup assertion that refuses to boot in production if `NEXTAUTH_SECRET` is missing or equals any known placeholder/short value. NextAuth v4 already warns; make it fatal.

---

**[HIGH]** [OWASP A03:2021 (Injection) / CWE-79 (Stored XSS) / OWASP LLM02-adjacent (insecure output handling)] — Stored XSS in the AI HTML report

`/src/app/api/reports/generate/route.ts:51-248`
```ts
const html = `<!DOCTYPE html> ...
  <p>${report.summary}</p>            // line 123
  ... <div class="name">${t.theme}</div>   // line 179
  ... <div class="list-item">${trend}</div>  // line 188
  ... <td>${item.reasoning}</td>      // line 206
  <title>Feedback Report - ${orgName}</title>  // line 55
`;
return new NextResponse(html, { headers: { "Content-Type": "text/html" }});
```

> **Impact:** The report is hand-built string-concatenated HTML served with `Content-Type: text/html`. Multiple interpolation points originate (directly or transitively) from **attacker-controllable feedback content** and `orgName`. Today `mock-ai.ts` returns hardcoded strings so it's not *currently* exploitable end-to-end — but the moment `generateInsightReport` is wired to a real LLM or echoes feedback text (which is its whole purpose), any feedback row containing `<script>` / `<img src=x onerror=...>` executes in the victim's browser when they open the report. `feedback.content` and `customerName` have **zero sanitization** (schema is plain `String`, `createFeedbackSchema` only checks `.min(1)`). Because the response is same-origin HTML, the payload runs with the victim admin's session → session-token theft, CSRF-on-self, data exfil. This is the classic "AI summary renders untrusted user input as HTML" pattern (OWASP LLM02 Insecure Output Handling).
> **Likelihood:** Medium now (gated by mock), High once AI is real.
> **Asset affected:** Admin session of whoever views the report.
> **Remediation:**
>   - Short-term: HTML-escape every interpolated value. Add a helper and wrap all `${...}` that carry data:
>     ```ts
>     const esc = (s: unknown) => String(s ?? "").replace(/[&<>"']/g, c =>
>       ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]!));
>     // ...<p>${esc(report.summary)}</p>, ${esc(orgName)}, ${esc(t.theme)}, etc.
>     ```
>   - Long-term: render reports through React/JSX (auto-escapes) or a templating engine with contextual auto-escaping, never string concat. Add `Content-Security-Policy: default-src 'none'; style-src 'unsafe-inline'` to the report response and serve it as a download (`Content-Disposition: attachment`) rather than `inline`. Treat all feedback content as untrusted on the way OUT (output encoding), not just on the way in.

---

**[HIGH]** [OWASP A04:2021 (Insecure Design) / CWE-770 (Allocation Without Limits)] — Zero rate-limiting across the entire app

`grep -r "rate" src/` → **no results.** No middleware throttle, no per-IP/per-user limiter.

> **Impact:** Several concrete abuse paths:
>   1. **Credential stuffing / brute force** on `POST /api/auth/callback/credentials` — `lib/auth.ts:authorize` does an unthrottled `bcrypt.compare` per attempt. Attacker can run unlimited password guesses against `demo@feedbackloop.com` (known email) or harvested emails.
>   2. **Compute DoS** on `POST /api/integrations/[id]/sync` — each call sleeps 1.5s then writes 3-5 rows (`sync/route.ts:110-135`); a logged-in user can spam it to bloat the DB and pin a connection.
>   3. **Compute DoS** on `POST /api/reports/generate` and `POST /api/surveys/[id]/ai-report` — each loads up to 200 rows and builds a large HTML/JSON payload; cheap to request, expensive to serve.
>   4. **Account lockout absent** — no failed-login counter.
> **Likelihood:** High.
> **Asset affected:** Availability + auth integrity.
> **Existing mitigations:** None.
> **Remediation:**
>   - Short-term: add a rate-limiter to `middleware.ts` (extend `withAuth` matcher to cover `/api/*`) or wrap routes with `@upstash/ratelimit` (sliding window) keyed by IP for auth and by `userId+route` for the rest. Suggested: auth 5/min/IP, sync 5/min/user, report 10/min/user.
>   - Long-term: WAF / platform rate-limit (Vercel Firewall, Cloudflare) + exponential backoff + lockout-with-CAPTCHA after N failed logins. Add a `loginAttempts`/`lockedUntil` column or use a Redis counter.

---

**[MEDIUM]** [OWASP A10:2021 (SSRF) / CWE-918] — Webhook sender is a server-side fetch waiting to happen; URL stored with no allow-list

`/src/lib/webhook-sender.ts:23-96`, `/src/app/api/webhooks/route.ts:8-9`
```ts
// webhooks/route.ts — only validation:
const createWebhookSchema = z.object({ url: z.string().url(), ... });
// webhook-sender.ts — TODAY a mock; comment says:
//   "In production, this would make actual HTTP POST requests to the webhook URLs."
```

> **Impact:** `z.string().url()` accepts `http://169.254.169.254/...` (cloud metadata), `http://localhost:8765/...` (the jarvis-core daemon!), `http://10.x/...` (internal services), and `file://`-adjacent tricks depending on the fetch client. The sender is currently a **mock** (no real `fetch`) so SSRF is **not exploitable today** — but the design stores an attacker-chosen URL and the explicit plan is to POST to it server-side. The instant someone replaces the mock with `fetch(url, ...)`, any authenticated user can make the server fetch internal endpoints, exfiltrate cloud IAM credentials via the metadata endpoint, or pivot to other localhost services on Boss's machine (where jarvis-core listens on 127.0.0.1:8765). This is a pre-planted A10.
> **Likelihood:** Low now (mock), High the day it ships for real.
> **Asset affected:** Internal network / cloud metadata / co-located daemons.
> **Remediation:**
>   - Short-term (do it now, before wiring): add URL validation on create/update — require `https://`, reject hostnames that resolve to private/loopback/link-local/CGNAT ranges (RFC1918, 127/8, 169.254/16, ::1, fc00::/7), reject by-IP literals, and re-validate after DNS resolution to defeat DNS rebinding.
>   - Long-term: send webhooks from an egress-restricted worker/queue with a domain allow-list, a non-routable-to-internal network policy (NetworkPolicy/security group), HMAC-sign payloads with the `secret` so receivers can verify, timeouts + retry caps, and block redirects (`redirect: "manual"`). Reference: OWASP SSRF Prevention Cheat Sheet.

---

**[MEDIUM]** [OWASP A05:2021 / CWE-209 (Information Exposure Through Error Message)] — Raw error messages returned to clients

`/src/lib/api-helpers.ts:36`
```ts
if (error instanceof Error) {
  ...
  return NextResponse.json({ error: error.message }, { status: 500 });
}
```

> **Impact:** Any unhandled `Error` returns its raw `.message` to the client (and `console.error`s the full object server-side). Prisma errors, adapter errors, and DB constraint internals can leak schema names, column names, file paths (`file:./prisma/dev.db`), and library versions — useful reconnaissance for an attacker mapping the data model.
> **Likelihood:** Medium.
> **Asset affected:** Information disclosure → easier follow-on attacks.
> **Remediation:**
>   - Short-term: in the generic branch return a static `{ error: "Internal server error" }` with a correlation id; log the real message server-side only.
>   - Long-term: structured logging (pino/OTel) with a request id echoed to the client for support, never the raw message.

---

**[MEDIUM]** [OWASP A05:2021 (Security Misconfiguration) / CWE-1188] — TypeScript build errors globally suppressed

`/src/next.config.ts:4-6`
```ts
typescript: { ignoreBuildErrors: true },
```

> **Impact:** The app builds even with type errors. This is how `lib/prisma.ts` shipped earlier with a duplicate `import { PrismaClient }` and a malformed `export const globalForPrisma.prisma` (caught and corrected during this audit; current file at `prisma.ts:15` still has dead `export const prisma2`). Type safety is a real security control here — the codebase casts sessions with `as Record<string, unknown>` everywhere (`auth.ts:52-63`, every route), so a typo in `orgId` extraction would silently produce `undefined`, and `where: { orgId: undefined }` in Prisma **matches all rows regardless of org** — that would turn into a cross-tenant data leak that the type checker would otherwise catch. Suppressing TS errors removes the safety net protecting org-scoping.
> **Likelihood:** Medium (latent; depends on future edits).
> **Asset affected:** Cross-tenant isolation integrity.
> **Remediation:**
>   - Short-term: set `ignoreBuildErrors: false`, fix the resulting errors.
>   - Long-term: type the session properly (`next-auth.d.ts` module augmentation already exists — use it instead of `as Record<string,unknown>` casts) so `session.user.orgId` is a typed `string`. Add a CI gate: `tsc --noEmit` must pass.

---

**[MEDIUM]** [OWASP A04:2021 / CWE-789 (Memory Allocation with Excessive Size Value)] — Unvalidated pagination integers

`/src/app/api/feedback/route.ts:26-27` and `/src/app/api/notifications/route.ts:24`
```ts
const page  = parseInt(searchParams.get("page")  || "1");
const limit = parseInt(searchParams.get("limit") || "20");
// later: skip: (page - 1) * limit, take: limit
```

> **Impact:** `limit` is not capped. `?limit=10000000` makes Prisma try to `take` 10M rows → memory/latency DoS. `page=-5` produces a negative `skip` (Prisma error → leaks via Finding 5). `?limit=abc` → `NaN` → `take: NaN`. Same on `notifications` and the analytics routes load *all* org feedback unbounded into memory (`dashboard/route.ts:37`, `analytics/route.ts:16`) — fine at demo scale, a DoS vector at real scale.
> **Likelihood:** Medium.
> **Remediation:**
>   - Short-term: clamp — `const limit = Math.min(Math.max(parseInt(...) || 20, 1), 100); const page = Math.max(parseInt(...) || 1, 1);`. Validate with a Zod query schema.
>   - Long-term: cursor-based pagination for large tables; never `findMany` without a `take` on analytics aggregations (or do counts in SQL via `groupBy`).

---

**[LOW]** [OWASP A07:2021 / CWE-1392 (Use of Default Credentials)] — Seeded demo creds + pre-filled login form

`/prisma/seed.ts:31-52` (creates `demo@feedbackloop.io` / `password123` AND `sarah@feedbackloop.io` / `password123`, both with `bcrypt.hash("password123", 10)`), `/src/app/(auth)/login/page.tsx:14-15` (form `useState` defaults to those exact values; line 112 even prints them on screen).

> **Impact:** If this DB/seed ever reaches a non-local environment, `demo@feedbackloop.com` / `password123` is a working admin login that's also pre-typed into the form for the attacker. Combined with no rate-limit (Finding 3) and weak secret (Finding 1), it's a free admin account.
> **Likelihood:** Low (demo artifact) but trivially exploitable if it leaks.
> **Remediation:** Don't seed real-looking creds for prod; gate seeding behind `NODE_ENV !== production`. Remove the default `useState` values from the login form. Force a password reset on first login for any seeded account.

---

**[LOW]** [OWASP A09:2021 / CWE-532 (Insertion of Sensitive Info into Log)] — Webhook delivery + secret presence logged

`/src/lib/webhook-sender.ts:57-62`
```ts
console.log(`[Webhook] Delivered to ${url}`, { event, webhookId, payloadSize, secret: secret ? "***" : "none" });
```

> **Impact:** Logs the destination `url` and whether a secret exists. The secret itself is masked (good), but destination URLs + payload metadata in shared logs aid reconnaissance and can include sensitive query strings if URLs carry tokens. Also the analyze route `console.error("Webhook broadcast error:", ...)` (`feedback/[id]/analyze/route.ts:107`) can dump payloads on failure.
> **Remediation:** Log webhook IDs, not URLs/payloads. Never log secrets even masked-by-presence. Use structured logging with redaction.

---

**[LOW]** [OWASP A01:2021 / CWE-639 (Authorization Bypass) / missing function-level authZ] — `role` exists but is never enforced

`schema.prisma:15` (`role String @default("admin")`), `auth.ts:52` puts `role` in the token, but **no route ever checks it.** Everyone is effectively admin within their org.

> **Impact:** There's no privilege separation. A "viewer" can delete feedback, edit webhooks, change integrations. Within a single org this may be acceptable for an MVP, but the schema implies RBAC intent that isn't implemented — a future viewer/member role would have full admin power.
> **Remediation:** Either remove `role` (don't imply a control you don't enforce) or add an authZ check helper (`requireRole(session, "admin")`) on destructive routes (DELETE feedback/theme/webhook, integration writes).

---

**[LOW]** [OWASP A04 / CWE-352 (CSRF)] — State-changing routes rely on implicit NextAuth CSRF only

All POST/PUT/DELETE routes accept JSON and act on the session cookie. NextAuth protects its own `/api/auth/*` endpoints with CSRF tokens, but the **app's** mutating routes (`/api/feedback`, `/api/webhooks`, etc.) have no explicit CSRF token check; they're protected only by the cookie being `SameSite` (NextAuth default `lax`).

> **Impact:** `SameSite=Lax` blocks cross-site POST CSRF for the common cases, so practical risk is low. But it's not defense-in-depth and `lax` still permits some top-level navigation GETs (none of the GETs mutate here, so OK). If cookie config is ever loosened to `SameSite=None`, every mutating route becomes CSRF-able.
> **Remediation:** Keep cookies `SameSite=Lax/Strict` + `Secure` + `HttpOnly` (verify in prod). For sensitive mutations, require a custom header (`X-Requested-With`) or double-submit token. Confirm NextAuth cookie config in production.

---

**[INFO]** — `lib/prisma.ts` dead code / earlier broken state

`prisma.ts:15` has `export const prisma2 = globalForPrisma.prisma; // unused`. Harmless but indicative of the `ignoreBuildErrors` problem (Finding 6). An earlier version had a duplicate `import { PrismaClient }` that would not type-check — only shipped because TS errors are suppressed. Clean it up.

---

**[INFO]** — "Public survey response endpoint" from the brief does not exist in this build

The task flagged "public survey response endpoints" and "spam/abuse on public surveys." I verified: **there is no unauthenticated feedback-submission route.** `POST /api/feedback` (`feedback/route.ts:69`) requires `getServerSession`. The only unauthenticated route is `/api/auth/[...nextauth]` (NextAuth itself, expected). Feedback enters the system via authenticated dashboard create or the mock `integrations/[id]/sync` importer. So the public-IDOR / public-spam class **does not apply to this codebase as written.** If a public widget/survey endpoint is added later (there's a `widget/` dir at the apps root, out of this project's scope), it MUST get: org-scoping by a survey token (not a guessable id), rate-limiting, CAPTCHA/proof-of-work, content-length caps, and output-encoding before it ever feeds the report generator (Finding 2).

---

## Detection (what to monitor when this goes live)

- **Auth brute force:** alert on >10 `401`/failed-credential events per IP per minute on `/api/auth/callback/credentials`.
- **SSRF attempts:** if/when webhooks fetch for real — alert on outbound connections from the app to RFC1918 / 169.254.169.254 / loopback. Log + block at egress.
- **Report XSS:** log when feedback content matches `/<script|onerror=|javascript:/i` on ingest (`POST /api/feedback`) — a WAF signature, not a substitute for output encoding.
- **Pagination abuse:** alert on requests with `limit` > 100 or non-numeric.
- Example Sigma-style hunt (pseudo): `selection: uri.path: "/api/auth/callback/credentials" AND status: 401 | count() by src_ip > 10 within 1m`.

## Verification Plan (non-exploitative, on local/staging only)

1. **Secret:** confirm prod `NEXTAUTH_SECRET` is 32+ random bytes and differs from `.env.example`. Try to verify a self-issued JWT fails after rotation.
2. **XSS:** in staging, create feedback with content `<img src=x onerror=alert(1)>`, wire a real `generateInsightReport`, open `/api/reports/generate` — confirm it does NOT execute after the `esc()` fix.
3. **Rate-limit:** script 100 logins/sec to staging, confirm 429 after threshold.
4. **SSRF:** before wiring real fetch, unit-test the new URL validator against `http://169.254.169.254`, `http://localhost:8765`, `http://10.0.0.1` — all must reject.
5. **Org-scoping regression (the thing that's currently RIGHT):** create two orgs, log in as org A, attempt `GET /api/feedback/{orgB_feedback_id}` → must return 404. Add this as an automated test so `ignoreBuildErrors` removal + future edits can't regress it.

## Compliance mapping (if this ever handles real customer feedback = PII)

- GDPR Art. 32 (security of processing) — encryption at rest for `customerEmail`/`customerName`, breach detection.
- SOC2 CC6.1 (logical access) — Findings 1, 3, 8, 10.
- SOC2 CC7.2 (monitoring) — Detection section above.
- OWASP ASVS v4 L1: V2 (auth) Findings 1/3/8, V5 (validation/encoding) Findings 2/7, V12 (SSRF) Finding 4.

---

### Bottom line
Core multi-tenant authZ is solid — genuinely good for an MVP. Fix in this order: **(0) get `prisma/dev.db` out of git + purge history + rotate everything it held, (1) rotate the NEXTAUTH secret, (2) escape the report HTML, (3) add rate-limiting + a login lockout, (4) harden the webhook URL validator before you ever replace the mock with a real fetch.** Everything else is cleanup. Hand the code-level fixes to `backend-engineer-agent`/`code-agent`; the git-history purge + rate-limit + egress controls to `devops-sre-agent`.

> Note on middleware: `src/middleware.ts` only matches dashboard *page* routes, NOT `/api/*`. That looks scary but is NOT a hole here — every API route independently calls `getServerSession` (verified: 0 of 20 routes are missing it; the only un-gated one is NextAuth's own handler). So API auth is enforced at the handler layer, not the edge. Still, adding `/api/:path*` to the matcher (with public-route exceptions) would give defense-in-depth + a natural place to hang the rate-limiter from Finding 3.
