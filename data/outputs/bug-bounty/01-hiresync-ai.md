# Bug Bounty / Defensive Security Audit — HireSync AI

**Target:** `/home/ujjwal/Documents/My Apps/apps/01-hiresync-ai/` (Next.js 16 + NextAuth + Prisma/SQLite ATS)
**Scope:** Authorized review of Boss's own code. Defensive-only.
**Date:** 2026-05-31
**Reviewer:** security-engineer-agent (Jarvis)

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 1 |
| High     | 3 |
| Medium   | 5 |
| Low      | 4 |
| Info     | 3 |
| **Total**| **16** |

**Overall posture:** Better than typical hackathon scaffolding. Multi-tenant org-scoping (`orgId` / `candidate.orgId`) is applied **consistently** on every data API route — there is **no classic IDOR** on candidates/jobs/interviews/notifications/settings. NextAuth + bcrypt + Zod are wired correctly on most mutations. The serious problems are: (1) a hardcoded/weak `NEXTAUTH_SECRET` that ships in the repo's `.env` and is a placeholder in production, (2) total absence of RBAC despite a `role` field existing, (3) a stored-XSS / open-redirect surface via HTML email templates and an unvalidated `meetingLink`, and (4) no rate-limiting on auth or AI endpoints. None of the data routes leak cross-tenant data.

**Single worst issue:** `NEXTAUTH_SECRET` is the literal string `"hiresync-super-secret-key-change-in-production"` (committed to the working tree, and a placeholder in prod) — anyone who knows or guesses it can forge a valid JWT for **any org**, fully bypassing auth and tenant isolation. (CWE-798 / CWE-321)

---

## Threat Model

- **Asset:** Candidate PII (names, emails, phones, AI assessments), job postings, org settings, recruiter accounts. This is GDPR-class data (recruitment = sensitive).
- **Adversary:** (a) Authenticated tenant user trying to reach another tenant's data; (b) unauthenticated attacker hitting API routes directly; (c) malicious recruiter within an org abusing missing RBAC; (d) attacker who learns the JWT signing secret.
- **Attack vectors:** JWT forgery via known secret (T1552/T1606), broken access control (OWASP A01), stored XSS via email HTML (A03/CWE-79), injection through `meetingLink` (CWE-601), credential brute force (no rate-limit, T1110), info disclosure via verbose errors (CWE-209), notification spoofing (mass-assign `userId`).
- **Existing controls (good):** Per-request `getServerSession` auth on every route; `orgId`-scoped `findFirst`/`findMany`/`update`/`delete` everywhere; ownership re-check before update/delete; Zod validation on most mutating bodies; bcrypt password hashing (cost 10); `.env*` correctly gitignored; transactions for cascade deletes.
- **Gaps:** Weak signing secret; no RBAC; no rate-limiting; unsanitized email HTML; verbose 500s; unvalidated URL fields; `typescript.ignoreBuildErrors`.

---

## Findings

### CRITICAL

**[CRITICAL]** [OWASP A02 / A07 · CWE-798 (Hardcoded Credentials) / CWE-321 (Hardcoded Crypto Key)] — Weak, committed `NEXTAUTH_SECRET`

- **File:** `.env:2` → `NEXTAUTH_SECRET="hiresync-super-secret-key-change-in-production"`; consumed in `src/lib/auth.ts:71` and `src/middleware.ts:8`. `.env.example:2` ships `"your-secret-key-here"`.
- **Impact:** The JWT session strategy (`session.strategy = "jwt"`) signs/verifies tokens with this secret. Anyone who knows it (it's a guessable English phrase, present in the working tree, and the `.env.example` placeholder strongly implies prod was never rotated) can **forge a valid session JWT** with arbitrary `id`/`orgId`/`role`. That defeats authentication AND every org-scoping control in one shot — full cross-tenant read/write of all candidate PII.
- **Likelihood:** High. The secret is low-entropy and the placeholder pattern means a default deploy may run with `"your-secret-key-here"`.
- **Exploit scenario:** Attacker crafts a JWT `{ id, orgId: <victim org>, role: "admin" }`, HMAC-signs with the known secret, sets it as the `next-auth.session-token` cookie, and calls `GET /api/candidates` — receives the victim org's full candidate list.
- **Fix:**
  - Short-term: Generate a high-entropy secret (`openssl rand -base64 48`), set it as a Vercel **Production** env var, and remove the value from any committed `.env`. Rotate immediately — rotation invalidates all forged + legitimate tokens (acceptable, forces re-login).
  - Long-term: Fail-fast guard so the app refuses to boot in production with a missing/placeholder secret:
    ```ts
    // src/lib/auth.ts (top)
    const secret = process.env.NEXTAUTH_SECRET;
    if (!secret || /change-in-production|your-secret-key-here/.test(secret)) {
      if (process.env.NODE_ENV === "production") throw new Error("NEXTAUTH_SECRET is unset or placeholder");
    }
    ```
  - Add a CI secret-scanner (gitleaks / trufflehog) to block placeholder/low-entropy secrets reaching `main`.

---

### HIGH

**[HIGH]** [OWASP A01 (Broken Access Control) · CWE-862 (Missing Authorization)] — No RBAC; `role` exists but is never enforced

- **File:** Schema defines `User.role` (`prisma/schema.prisma:29`, default `"admin"`); seed creates `admin` + `recruiter` (`prisma/seed.ts:43,54`). `role` is propagated into the JWT/session (`src/lib/auth.ts:38,52,62`). **No API route checks it** (`grep "\.role" src/app/api/` → 0 results).
- **Impact:** Every authenticated user can do everything: delete jobs/candidates, change candidate stages, edit org settings (`PUT /api/settings`), send offer-letter emails. A junior "recruiter" can wipe the org's entire pipeline. New self-registered users default to `role: "admin"` (schema default) — privilege-by-default.
- **Likelihood:** Medium (requires a valid account, but any account is over-privileged).
- **Exploit scenario:** A `recruiter`-role user calls `DELETE /api/jobs/{id}` — succeeds, cascade-deleting all candidates + interviews. No authz gate stops them.
- **Fix:**
  - Short-term: Add a `requireRole()` helper and gate destructive/admin ops (job delete, settings update, offer emails):
    ```ts
    export function requireRole(session, ...roles: string[]) {
      if (!roles.includes(session.user.role)) return forbidden(); // 403
    }
    ```
  - Long-term: Change `User.role` default away from `"admin"`; centralize authz in a policy module; map each route to a required permission. Hand to **backend-engineer-agent** for the policy layer.

**[HIGH]** [OWASP A03 (Injection) / LLM-adjacent · CWE-79 (Stored XSS) / CWE-601 (Open Redirect)] — Unsanitized user data interpolated into HTML emails + unvalidated `meetingLink`

- **File:** `src/lib/email-templates.ts` interpolates `candidateName`, `jobTitle`, `companyName`, and crucially `meetingLink` directly into an HTML string: `interviewInviteEmail` line 134 → `<a href="${data.meetingLink}">${data.meetingLink}</a>`. `meetingLink` is accepted with **no URL validation** in `src/app/api/interviews/route.ts:13` (`meetingLink: z.string().optional()`) and `[id]/route.ts:14`. `companyName` flows from org `name`, settable via `PUT /api/settings` with `name: z.string().min(1)` — no character restriction.
- **Impact:** (1) **Open redirect / phishing:** an attacker sets `meetingLink` to `javascript:...` or `https://evil.tld/phish` and the offer/invite email renders it as a clickable link sent to candidates — credential-harvest vector under the org's brand. (2) **Stored XSS into any HTML consumer:** these templates return raw HTML; if it's ever rendered in an admin preview pane, web view, or an email client that executes inline content, injected `<img src=x onerror=...>` in `candidateName`/`companyName` fires. Email is the current sink (mock-logged), but the templates are XSS-unsafe by construction.
- **Likelihood:** Medium (email is currently mocked, but the unsafe primitive is shipped and the open-redirect works the moment real send is enabled).
- **Exploit scenario:** Recruiter A sets candidate name to `<img src=x onerror=alert(document.cookie)>`; another user opens an HTML preview of the offer letter → script executes in their session context.
- **Fix:**
  - Short-term: HTML-escape every interpolated value before injecting into templates:
    ```ts
    const esc = (s = "") => String(s).replace(/[&<>"']/g, c =>
      ({ "&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;" }[c]!));
    ```
    Wrap all `${data.x}` with `esc(...)`. Validate `meetingLink` as an http/https URL: `z.string().url().refine(u => /^https?:/.test(u))`.
  - Long-term: Use a templating library that auto-escapes (React-email / MJML), and a strict allowlist for link schemes. Add a CSP if any of this HTML is rendered in-browser.

**[HIGH]** [OWASP A04 / A05 · CWE-307 (Improper Restriction of Auth Attempts) / CWE-770 (Resource Exhaustion)] — No rate-limiting on auth or expensive endpoints

- **File:** No rate-limiting anywhere (`grep ratelimit/throttle` → 0). `authorize()` in `src/lib/auth.ts:14` runs bcrypt-compare per attempt with no lockout. AI routes (`scoreResume`, `matchCandidateToJob`, `ai-questions`) each sleep 0.8–1.5s and are callable unbounded.
- **Impact:** (1) Online password brute-force / credential stuffing against `/api/auth/callback/credentials`. (2) Resource-exhaustion DoS by hammering the artificially-slow AI endpoints (and they mutate DB via `candidate.update`). (3) Account enumeration aggravates this (see Medium below).
- **Likelihood:** Medium-High (auth brute force is trivially scriptable).
- **Exploit scenario:** Attacker scripts 10k password guesses against the credentials endpoint — no lockout, no backoff, no CAPTCHA.
- **Fix:**
  - Short-term: Add IP+identifier rate-limiting middleware (Upstash Ratelimit on Vercel, or `@vercel/firewall`). Strictest on the auth callback (e.g. 5/min/IP + per-email throttle); moderate on AI routes (e.g. 20/min/user).
  - Long-term: Exponential backoff + temporary account lockout + alerting on auth-failure spikes. Hand infra config to **devops-sre-agent**.

---

### MEDIUM

**[MEDIUM]** [OWASP A09 · CWE-209 (Information Exposure Through Error Message)] — Verbose error passthrough on 500s

- **File:** `src/lib/api-helpers.ts:36` → `return NextResponse.json({ error: error.message }, { status: 500 })`. Raw `Error.message` (which can include Prisma/SQL internals, file paths, constraint details) is returned to the client.
- **Impact:** Leaks DB schema, file structure, and library internals to attackers — aids further exploitation. Combined with `console.error` of the full error, also risks logging PII.
- **Likelihood:** Medium.
- **Fix:** Return a generic `{ error: "Internal server error" }` with a correlation ID for 500s; log details server-side only. Never echo `error.message` for unhandled errors.

**[MEDIUM]** [OWASP A07 · CWE-204 (Observable Discrepancy) / User Enumeration] — Login distinguishes "no user" vs "wrong password"

- **File:** `src/lib/auth.ts:25` throws `"No user found with this email"` vs line 31 `"Invalid password"`. These distinct messages are surfaced by NextAuth.
- **Impact:** Account enumeration — attacker confirms which emails are registered, sharpening phishing + the brute-force above.
- **Likelihood:** Medium.
- **Fix:** Return one generic message ("Invalid email or password") for both branches. Keep timing roughly constant (run a dummy bcrypt compare when the user is absent to avoid a timing oracle, CWE-208).

**[MEDIUM]** [OWASP A04 / A01 · CWE-602 / Mass Assignment] — Notification POST lets a user write a notification to an arbitrary `userId`

- **File:** `src/app/api/notifications/route.ts:13` accepts `userId: z.string().optional()` and line 76 writes `userId: parsed.data.userId || session.user.id` with **no check that the target user is in the caller's org or is the caller**.
- **Impact:** Any authenticated user can inject arbitrary notifications into **any user's** feed (cross-org), including spoofed titles/links — notification phishing ("Click here to verify", `link` controlled by attacker). Also a minor spam/DoS vector.
- **Likelihood:** Medium.
- **Exploit scenario:** Attacker POSTs `{ userId: "<victim id>", title: "Security alert", message: "...", link: "https://evil.tld" }` — appears as a legit in-app notification to the victim.
- **Fix:** Drop `userId` from the client-accepted schema entirely — always use `session.user.id`. Notifications to other users should only be created server-side by trusted flows (as the stage/interview routes already do). Validate `link` as a relative path or same-origin URL.

**[MEDIUM]** [OWASP A05 · CWE-1287 / Build Integrity] — `typescript.ignoreBuildErrors: true`

- **File:** `next.config.ts:5`.
- **Impact:** Type errors (including auth/authz logic mistakes, null derefs, wrong field access) ship to production silently. The heavy `as Record<string, unknown>` casts in `auth.ts` already bypass the type system around the security-critical session/token mapping — exactly where a type error would be a vuln.
- **Likelihood:** Medium (latent — surfaces as future bugs).
- **Fix:** Set `ignoreBuildErrors: false`; fix the underlying types (proper `next-auth` module augmentation already exists in `src/types/next-auth.d.ts` — use it instead of casts). Add `tsc --noEmit` + ESLint to CI as a gate.

**[MEDIUM]** [OWASP A05 / A09 · CWE-693] — Missing security headers / CSP / cookie hardening not asserted

- **File:** `next.config.ts` sets no `headers()`; no CSP, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, or HSTS. NextAuth cookie flags rely on defaults (no explicit `cookies` config in `auth.ts`).
- **Impact:** Clickjacking, MIME-sniffing, weaker XSS containment (amplifies the email-template XSS if ever rendered in-app), and no defense-in-depth on the session cookie.
- **Likelihood:** Low-Medium.
- **Fix:** Add a `headers()` block with CSP (`default-src 'self'`), `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, HSTS. Explicitly set NextAuth `cookies.sessionToken` with `httpOnly: true, sameSite: "lax", secure: true` in production. Hand to **frontend-engineer-agent** / **devops-sre-agent**.

---

### LOW

**[LOW]** [CWE-20] — Pagination/numeric params unvalidated (`parseInt`)
- **File:** `parseInt(searchParams.get("page"))` etc. in candidates/jobs/interviews/notifications routes (e.g. `src/app/api/candidates/route.ts:19-20`). `NaN`/negative/huge `limit` aren't clamped. `limit=999999` → large result set (mild DoS); negative `skip` → Prisma error (500, hits the verbose-error finding).
- **Fix:** Coerce + clamp via Zod: `z.coerce.number().int().min(1).max(100).catch(10)`.

**[LOW]** [CWE-79] — `resumeUrl` accepted without URL validation
- **File:** `src/app/api/candidates/route.ts:13` (`resumeUrl: z.string().optional()`) and `[id]/route.ts`. Stored unvalidated; if later rendered as a link → `javascript:`/phishing vector (same class as `meetingLink`).
- **Fix:** `z.string().url().refine(u => /^https?:/.test(u)).optional()`.

**[LOW]** [CWE-307] — AI mutation endpoints have no idempotency / abuse cap
- **File:** `src/app/api/candidates/[id]/score/route.ts`, `.../ai-match/route.ts`. Each call mutates `candidate.aiScore`/`aiSummary` and is unbounded — repeated calls churn DB + the (currently mock) AI. Maps to LLM04 (Model DoS) / LLM08 (Excessive Agency) when a real LLM is wired in.
- **Fix:** Rate-limit per candidate, and when a real model is added, add per-org token/budget caps + an action allowlist. Hand the LLM-budget design to **ml-engineer-agent**.

**[LOW]** [CWE-117/532] — PII written to stdout logs
- **File:** `src/app/api/candidates/[id]/send-email/route.ts:120` logs candidate email; `interviews/route.ts:114` logs email; `mock-ai.ts` logs candidate names/phones. In prod these land in log aggregators uncontrolled.
- **Fix:** Redact emails/phones in logs (`a***@domain`); never log full PII. Matches Jarvis's own "never log PII to disk" rule.

---

### INFO

**[INFO]** Secrets hygiene is otherwise correct — `.gitignore` excludes `.env*` and `prisma/dev.db`; git history confirms **no `.env` or `.db` was ever committed** (`git log --all -- .env` empty; `git ls-files` shows only `.env.example`). Good. The only secret exposure is the placeholder value living in the working-tree `.env` (Critical above) — rotate, don't just gitignore.

**[INFO]** Org-scoping is done right and consistently — every data route filters by `orgId` (or `candidate.orgId` for interviews) AND re-checks ownership before update/delete via `findFirst`. I specifically tried to find IDOR on candidates `[id]`, jobs `[id]`, interviews `[id]`, notifications `[id]/read`, settings, and the `jobs/[id]/candidates` and `candidates/[id]/send-email` nested routes — **all are tenant-isolated**. This is the strongest part of the app; keep this pattern.

**[INFO]** No SQL/NoSQL/command injection — all DB access goes through Prisma's parameterized query builder; no `$queryRaw`/`$executeRaw`/`eval`/`child_process`/`dangerouslySetInnerHTML` anywhere (grep-confirmed). Search uses Prisma `contains`, not raw SQL.

---

## Hardening / Config (drop-in patches)

```ts
// next.config.ts — add headers + stop ignoring TS errors
const nextConfig: NextConfig = {
  typescript: { ignoreBuildErrors: false },
  async headers() {
    return [{
      source: "/:path*",
      headers: [
        { key: "X-Frame-Options", value: "DENY" },
        { key: "X-Content-Type-Options", value: "nosniff" },
        { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        { key: "Strict-Transport-Security", value: "max-age=63072000; includeSubDomains; preload" },
        { key: "Content-Security-Policy", value: "default-src 'self'; frame-ancestors 'none'; object-src 'none'" },
      ],
    }];
  },
};
```

```ts
// src/lib/api-helpers.ts — stop leaking internals on 500
if (error instanceof Error) {
  // ...keep the known 404/409 mappings...
  console.error("Unhandled:", error);            // server-side only
  return NextResponse.json({ error: "Internal server error" }, { status: 500 });
}
```

```ts
// src/lib/auth.ts — generic auth error + boot guard (see Critical/Medium)
if (!user || !(await bcrypt.compare(credentials.password, user?.password ?? "$2a$10$invalidhashplaceholderxxxxxxxxxxxxxxxxxxxx")))
  throw new Error("Invalid email or password");
```

---

## Detection

- **Auth brute force (SIEM / log query, MITRE T1110):** alert when failed credential attempts from one IP or against one email exceed N in 5 min. Currently impossible — first add a structured auth-failure log line in `authorize()` (`{event:"auth_fail", emailHash, ip, ts}`), then alert on it.
- **JWT forgery indicator:** after rotating `NEXTAUTH_SECRET`, alert on any request bearing a session token that fails verification (old/forged) — spike = active attack or fleet still on stale secret.
- **Cross-org probing:** log `404 Record not found` on `[id]` routes with the requester's `orgId`; a single user generating many 404s on candidate/job IDs = IDOR/enumeration probing.
- **AI-endpoint abuse:** Prometheus/OTel counter on `score`/`ai-match`/`ai-questions` per user; alert on rate > threshold (Model-DoS, LLM04).

---

## Response Runbook — "Suspected JWT secret compromise"

1. **Detect:** unexplained cross-org data access in logs, or secret known to be leaked.
2. **Contain:** rotate `NEXTAUTH_SECRET` in Vercel prod immediately (`openssl rand -base64 48`) → invalidates all tokens, forces global re-login.
3. **Eradicate:** scrub the value from the working-tree `.env`; run gitleaks across history to confirm it never landed in a commit (already confirmed clean).
4. **Recover:** verify legit users can log in; monitor auth-failure + verification-failure metrics for 48h.
5. **Communicate:** if cross-tenant PII access is confirmed, this is a GDPR personal-data breach — 72h notification clock starts (Art. 33).

---

## Compliance Mapping

- **GDPR Art. 32** (security of processing) — weak secret + no RBAC + PII in logs are direct gaps. **Art. 33/34** — breach-notification readiness depends on the detection logging above (currently absent).
- **SOC 2 CC6.1** (logical access) — RBAC gap; **CC6.6** (boundary protection) — missing rate-limit/headers; **CC7.2** (monitoring) — no security logging/alerting.
- **OWASP Top 10 2025:** A01 (RBAC), A02 (secret), A03 (XSS), A04 (mass-assign/rate), A05 (config/headers/TS), A07 (enumeration), A09 (verbose errors/logging).
- **OWASP LLM Top 10 2025:** LLM04 (Model DoS) + LLM08 (Excessive Agency) become live once mock AI → real model.

---

## Verification Plan (no prod exploitation)

1. **Secret:** confirm prod `NEXTAUTH_SECRET` is rotated to 48-byte random and the boot guard throws on placeholder (unit test the guard).
2. **RBAC:** integration test — a `recruiter`-role session calling `DELETE /api/jobs/{id}` and `PUT /api/settings` must return 403.
3. **XSS/redirect:** unit test `interviewInviteEmail({candidateName:"<img onerror>"})` output contains `&lt;img` not `<img`; `meetingLink:"javascript:alert(1)"` is rejected by the schema.
4. **Mass-assign:** test that POST `/api/notifications` with a foreign `userId` writes to the caller's id, not the supplied one.
5. **Rate-limit:** scripted 20 rapid login attempts must start returning 429.
6. **Tooling:** run `semgrep --config p/nextjs --config p/owasp-top-ten`, `npm audit`/`trivy fs .`, and `gitleaks detect` in CI as a regression gate.
7. **Tabletop:** "An attacker posts our `NEXTAUTH_SECRET` on Pastebin — what's our rotation + breach-assessment flow?" Walk the runbook above.

---

*Defensive-only review. No exploit code generated. All file:line references verified against the source at audit time.*
