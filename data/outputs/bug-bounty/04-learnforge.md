# Bug Bounty / Defensive Audit — LearnForge (04-learnforge)

**Target:** `/home/ujjwal/Documents/My Apps/apps/04-learnforge/`
**Stack:** Next.js 16.1.6 (App Router) · NextAuth v4 (Credentials/JWT) · Prisma 7 + SQLite (better-sqlite3) · React 19 · Zod 4
**Scope:** Authorized review of Boss Ujjawal's own code. Defensive-only.
**Date:** 2026-05-31

**Auditor honesty note:** The checked-in `prisma/schema.prisma` is STALE — it describes an exam-prep schema (`Exam/Subject/Topic/StudyNote`), but the running app uses a course-based schema (`Course / Chapter / Lesson / Quiz / LessonProgress / Certificate / Review / Enrollment`, roles `creator` / `student`) per `prisma/seed.ts` + the generated client + every API route. The schema/seed mismatch is itself a finding (#10). All findings below reference the REAL runtime models, confirmed by reading every `route.ts` under `src/app/api`, `auth.ts`, `prisma.ts`, `middleware.ts`, `next.config.ts`, `.env`, `.gitignore`, and the seed.

**Good news first (verified, not flattery):** This app is *substantially* better on access control than typical hackathon LMS code. Almost every creator-management route correctly checks `course.creatorId === userId` before mutating, the `learn` route gates content behind enrollment, `reviews` requires enrollment, `progress`/`certificate` verify enrollment, `notifications` PATCH scopes by `userId`, and writes use Zod `safeParse`. The IDOR-cluster I would normally expect here is mostly absent. The real issues are auth-config hardening, two genuinely missing checks, and payment being mock.

---

## Severity Summary

| # | Severity | Category | Title | Location |
|---|----------|----------|-------|----------|
| 1 | **HIGH** | A02 / CWE-798, CWE-321 | Hardcoded weak `NEXTAUTH_SECRET` — forgeable session JWTs | `.env:2` |
| 2 | **HIGH** | A01 / CWE-602, CWE-840 | Paid-course paywall bypass — "mock payment" accepts ANY/empty token | `courses/[id]/enroll/route.ts:53-80` |
| 3 | **MEDIUM** | A01 / CWE-862 | `ai-quiz` exposes full lesson content to any logged-in user (no enrollment/ownership check) | `courses/[id]/ai-quiz/route.ts:22-66` |
| 4 | **MEDIUM** | A03 / CWE-79 | Stored XSS — lesson `content` is raw HTML, no sanitize on write or render path | `lessons/[lessonId]` PUT, `learn` GET |
| 5 | **MEDIUM** | A05 / CWE-1127 | `typescript.ignoreBuildErrors: true` ships type-unsafe code (incl. authz `as` casts) | `next.config.ts:5` |
| 6 | **MEDIUM** | A07 / CWE-204 | Login user-enumeration — distinct "No user found" vs "Invalid password" | `src/lib/auth.ts:24,33` |
| 7 | **MEDIUM** | A04 / CWE-307 | No rate limiting on login or any route — credential stuffing / scraping | app-wide |
| 8 | **MEDIUM** | A09 / CWE-209 | Verbose errors — `handleApiError` returns raw `error.message` on 500 | `src/lib/api-helpers.ts:36` |
| 9 | **LOW** | A05 / CWE-693, CWE-1275 | Missing security headers (CSP/HSTS/X-Frame) + no explicit cookie/CORS policy | `next.config.ts`, auth config |
| 10 | **LOW** | A05 / CWE-710 | schema.prisma stale/out-of-sync with seed + generated client + routes | `prisma/schema.prisma` |
| 11 | **LOW** | A07 / CWE-521, CWE-798 | Seed default password `password123` for both demo accounts | `prisma/seed.ts:29` |
| 12 | **LOW** | A01 / CWE-639 | `ai-summary` & `reviews` GET fully unauthenticated (info exposure of course structure) | `courses/[id]/ai-summary`, `reviews` GET |
| 13 | **INFO** | A04 / CWE-770 | `reorder` updates items by id without verifying they belong to the course | `chapters/reorder`, `lessons/reorder` |
| 14 | **INFO** | A01 / CWE-863 | No `role`-based separation — any user can become a "creator" by hitting creator APIs | `courses` POST |

> **Verification gaps (honest):** I could not run the app or read `dev.db`/seed binary in this session. Finding #1's "is `.env` committed in history" is `[unverified]` — `git ls-files` showed no tracked `.env` currently (good), and `.gitignore` lists `.env*`. Finding #4's exploitability depends on the client render path (`dangerouslySetInnerHTML`), which I infer from `content` being stored/described as HTML — marked accordingly. All code line-refs are confirmed from full source reads.

---

## Findings (detail)

### 1. HIGH — Hardcoded, guessable `NEXTAUTH_SECRET`
**[A02:2021 Cryptographic Failures / CWE-798 / CWE-321]**

`.env:2` → `NEXTAUTH_SECRET="learnforge-secret-key-2024"`. This is the HMAC key signing every NextAuth JWT. It is human-guessable and pattern-based.

> Impact: Anyone who guesses/derives it can forge a JWT with `{ id: <any user id>, role: "creator" }` and authenticate as any user — full account takeover, and since authz is ownership-by-`creatorId`, they could forge a token for a creator's id and manage that creator's courses.
> Likelihood: MEDIUM (weak enough to be a guessing/dictionary target; HIGH if `.env` was ever committed).
> Existing mitigations: `.gitignore` covers `.env*`; `git ls-files` shows no tracked `.env` now. `.env.example` correctly uses a placeholder.
> Remediation:
>   - Short-term: rotate to `openssl rand -base64 32`; set only in Vercel project env vars. Verify history is clean: `git log --all -- .env`.
>   - Long-term: if it ever was committed, treat as burned + `git filter-repo` to purge.

---

### 2. HIGH — Paid-course paywall bypass (mock payment accepts anything)
**[A01:2021 / CWE-602 Server-Side Enforcement Relies on Untrusted Input / CWE-840 Business Logic Error]**

`courses/[id]/enroll/route.ts:53-80`: for `course.price > 0`, the route reads an optional `paymentToken` from the body, `setTimeout(500)` to "simulate", then sets `paymentStatus = "paid"` and creates the enrollment **regardless of whether a token was supplied or valid** (`paymentId = paymentToken || \`pay_mock_...\``). No `Transaction` record, no payment-gateway verification, no signature check. The schema even has `Transaction` + `razorpay*` fields that go unused.

> Impact: Any logged-in user enrolls in any paid course for free, then reads gated content via the (correctly-gated) `learn` route. Direct revenue loss; the entire pricing model is non-enforcing.
> Likelihood: HIGH — single authenticated POST, no token needed.
> Asset affected: All paid course content + revenue.
> Remediation:
>   - Short-term (defensive): if `course.price > 0`, require a verified completed `Transaction` for `(userId, courseId)` before `enrollment.create`. Reject when absent.
>   - Long-term: make enrollment for paid courses a server-side consequence of a Razorpay webhook with HMAC signature verification (`razorpay.validateWebhookSignature`), never a directly client-callable create. Record the `Transaction` row.
>   - This is the LLM-agnostic equivalent of "never trust the client for authorization decisions." Hand-off: `backend-engineer-agent` for the Razorpay integration.

---

### 3. MEDIUM — `ai-quiz` leaks full lesson content without enrollment/ownership
**[A01:2021 / CWE-862 Missing Authorization]**

`courses/[id]/ai-quiz/route.ts:22-66`: checks `session?.user` only, then loads the course with **all lessons' `content`** and (with no `lessonId`) concatenates every lesson's content and feeds it to `generateQuizFromContent`. There is no enrollment check and no creator check — unlike the sibling `learn` route which correctly requires enrollment.

> Impact: Any logged-in user (incl. a free `student` who never enrolled / never paid) can extract the full text of all lessons of any course id by POSTing to `ai-quiz`. Combined with #2 it's a second content-exfil path that doesn't even need the enroll step. Note the quiz answers (`correctAnswer`) aren't returned here, but the lesson *content* is the paid asset.
> Likelihood: MEDIUM-HIGH.
> Remediation: Require `enrollment` OR `course.creatorId === userId` before reading lesson `content`, mirroring `learn/route.ts:20-29`. Same fix pattern applies — extract a shared `assertCourseAccess(userId, courseId)` helper and use it in `learn`, `ai-quiz`, `certificate`, `progress`.

---

### 4. MEDIUM — Stored XSS via raw-HTML lesson content
**[A03:2021 Injection / CWE-79]**

Lesson `content` is stored/handled as HTML. `lessons/[lessonId]` PUT validates with Zod but `content: z.string().optional()` performs **no sanitization** — arbitrary HTML/JS is persisted. It is then returned by `learn`/`lessons` GET. If the learn UI renders it with `dangerouslySetInnerHTML` (standard for "HTML content" fields), an author can inject `<img src=x onerror=...>`/`<script>` that runs in every enrolled student's browser. The `ai-generate-lesson` route also produces HTML that lands in the same field.

> Impact: Stored XSS → cookie/session abuse, keylogging, defacement, lateral spread across learners viewing the course.
> Likelihood: MEDIUM (confirmed unsafe storage; render-path use of `dangerouslySetInnerHTML` is `[inferred, verify in src/app/(dashboard)/learn/[courseId]/page.tsx]`).
> Remediation:
>   - Sanitize on write AND render with `isomorphic-dompurify` (strict allowlist: no `script`, no `on*` handlers, no `javascript:` URLs).
>   - Add a strict CSP (#9) as defense-in-depth. The same applies to `Review.comment` and `User.bio` if rendered as HTML (they appear to be plain text today — keep them so).

---

### 5. MEDIUM — `ignoreBuildErrors: true`
**[A05:2021 Security Misconfiguration / CWE-1127]**

`next.config.ts:5` disables TypeScript build errors. The whole authz model leans on unchecked casts like `(session.user as { id: string }).id` and `(session.user as { role: string }).role`; type errors that would catch a wrong/missing field ship silently.

> Remediation: Remove `ignoreBuildErrors`. Add proper NextAuth module augmentation (`next-auth.d.ts`) so `session.user.id`/`role` are typed instead of cast. Make `next lint` + `tsc --noEmit` a CI gate.

---

### 6. MEDIUM — Login account enumeration
**[A07:2021 / CWE-204]**

`src/lib/auth.ts:24` throws `"No user found with this email"` vs `:33` `"Invalid password"`. Distinct responses confirm which emails are registered.

> Remediation: Single generic message `"Invalid email or password"` for both. Run a dummy `bcrypt.compare` when the user is not found to flatten the timing oracle.

---

### 7. MEDIUM — No rate limiting
**[A04:2021 / CWE-307]**

No throttle on `/api/auth` login or any endpoint — credential stuffing, brute force, and bulk content scraping (#3) are unbounded.

> Remediation: IP+account rate limiting on login (Upstash Ratelimit / `@vercel/firewall`), plus a global API limiter; backoff/lockout after N failures. Hand-off: `devops-sre-agent`.

---

### 8. MEDIUM — Verbose error leakage
**[A09:2021 / CWE-209]**

`src/lib/api-helpers.ts:36` returns `error.message` directly in 500s; Prisma errors leak table/column/constraint details to clients.

> Remediation: keep `console.error` server-side; return generic `{ error: "Internal server error" }` + a request id for the 500 branch. Don't echo `error.message`.

---

### 9. LOW — Missing security headers + cookie/CORS hardening
**[A05:2021 / CWE-693 / CWE-1275]**

No CSP, HSTS, `X-Frame-Options`/`frame-ancestors`, `X-Content-Type-Options`. No explicit NextAuth cookie config; relying on defaults. Note `certificate/route.ts` returns user-influenced data inside an HTML response with an inline `onclick` — a CSP would also constrain that surface (today `course.title`/`user.name` are interpolated into HTML; if those ever contain markup it's a second XSS vector — escape them).

> Remediation: add `headers()` in `next.config.ts` (`default-src 'self'`, `frame-ancestors 'none'`, HSTS, `nosniff`). Ensure session cookie `httpOnly`+`secure`+`sameSite:'lax'`, set `NEXTAUTH_URL` to https in prod. HTML-escape interpolations in the certificate template.

---

### 10. LOW — `schema.prisma` out of sync with reality
**[A05:2021 / CWE-710 Improper Adherence to Coding Standards]**

`prisma/schema.prisma` (Exam/Subject/Topic/StudyNote) does not match the seed, the generated client (`src/generated/prisma/models/*` has `Course/Chapter/Lesson/...`), or any route. Anyone running `prisma migrate`/`db push` from this file would corrupt or diverge the DB; it also misleads reviewers (it misled this audit initially).

> Remediation: regenerate `schema.prisma` from the live model (`prisma db pull`) and commit the correct one; delete the stale exam schema. Add `prisma validate` to CI.

---

### 11. LOW — Seed default credentials
**[A07:2021 / CWE-521 Weak Password / CWE-798]**

`prisma/seed.ts:29` seeds both `creator@learnforge.io` and `student@learnforge.io` with `password123` (printed to console). Fine for local demo, dangerous if seeded into any shared/preview/prod DB.

> Remediation: gate seeding behind `NODE_ENV !== 'production'`; randomize demo passwords or require env-provided ones; never seed demo accounts into prod.

---

### 12. LOW — Unauthenticated GET on `ai-summary` and `reviews`
**[A01:2021 / CWE-639]**

`courses/[id]/ai-summary/route.ts` and `reviews` GET have no `session` check. `ai-summary` returns course title/description/chapter structure (marketing-ish, low sensitivity) and reviews are arguably public. Lower risk than #3 because neither returns lesson `content`. Flagged for completeness + enumeration (course ids can be probed).

> Remediation: if course catalog is meant to be public, keep but ensure no premium fields leak (currently OK — only `id/duration` selected). If not, add the session check.

---

### 13. INFO — Reorder doesn't verify item ownership/parentage
**[A04:2021 / CWE-770 / CWE-639]**

`chapters/reorder` and `lessons/reorder` correctly gate on `course.creatorId === userId`, but then `prisma.X.update` each `item.id` **without checking those ids belong to this course**. A creator could pass another course's chapter/lesson ids and rewrite their `order`. Impact is minor (only the `order` int), and the caller must still own *a* course, so this is INFO not MEDIUM.

> Remediation: verify every `item.id` belongs to `courseId` (e.g. `findMany({ where: { id: { in: ids }, courseId } })` and compare counts) before the transaction; cap array length.

---

### 14. INFO — No role gate; "creator" is implicit
**[A01:2021 / CWE-863 Incorrect Authorization]**

There's no role check anywhere — any authenticated `student` can `POST /api/courses` and instantly become a course creator (gets `creatorId = self`, then owns/manages it). This is by-design for many open LMS platforms, so it's INFO, but worth a conscious decision: if "becoming a creator" should be restricted, add a `role === 'creator'|'admin'` gate on course creation. The JWT already carries `role` (`auth.ts:52`) — it's just never enforced.

> Remediation (if restricting): add `if (!['creator','admin'].includes(role)) return 403` to `courses` POST. Otherwise document that self-service creation is intended.

---

## Compliance / Framework Mapping

- **OWASP Top 10 2025:** A01 Broken Access Control (#2,3,12,13,14), A02 Crypto (#1), A03 XSS (#4), A04 Insecure Design / rate-limit (#7,13), A05 Misconfig (#5,9,10), A07 Auth Failures (#6,11), A09 Logging/Errors (#8).
- **CWE:** 798, 321, 602, 840, 862, 79, 1127, 204, 307, 209, 693, 1275, 710, 521, 770, 863, 639.
- **OWASP LLM Top 10:** LOW exposure — AI routes use local `mock-ai` (no external model/key). If `mock-ai` is later replaced by a real LLM: lesson `content` is concatenated into prompts in `ai-quiz` (LLM01 prompt-injection surface) and AI output is written back to `content` (feeds #4) — sanitize both at that point.

## Verification Plan (no prod exploitation)

1. **Secret (#1):** `git log --all -- .env` (expect empty); rotate; confirm a JWT signed with the old secret is rejected after rotation.
2. **Paywall (#2):** as a fresh `student`, `POST /api/courses/{paidId}/enroll` with empty body → expect it to FAIL after fix (currently 201). Assert an `enrollment` is created only when a verified `Transaction` exists.
3. **ai-quiz (#3):** as a non-enrolled student, `POST /api/courses/{id}/ai-quiz` → expect 403 after fix (currently 200 with content-derived quiz).
4. **XSS (#4):** PUT a lesson with `content: "<img src=x onerror=alert(1)>"`; load learn page; assert inert after DOMPurify.
5. **Enumeration (#6):** login with unknown email vs known email/wrong password → responses must be identical.
6. **CI gates:** add Semgrep rules — "route handler reading lesson.content without an enrollment/ownership check"; remove `ignoreBuildErrors` and run `tsc --noEmit` + `prisma validate` in CI.

## Recommended Fix Order (highest leverage first)
1. #1 rotate secret (5 min; closes token forgery).
2. #2 enforce real payment before paid enroll (revenue + access).
3. #3 add enrollment/ownership check to `ai-quiz` (content exfil).
4. #4 sanitize lesson HTML + #9 CSP.
5. #5 remove `ignoreBuildErrors` + add NextAuth types; #6 generic login error; #7 rate-limit; #8 generic 500.
6. #10 fix schema drift; #11 guard seed; #12/#13/#14 per product decision.

*Hand-offs: payment + authz helper + error envelope → `backend-engineer-agent`; secret management + headers + rate-limit infra → `devops-sre-agent`; HTML render-path XSS confirmation → `frontend-engineer-agent`.*
