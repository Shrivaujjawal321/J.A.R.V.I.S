# ClinicOS — Defensive Security Audit (Bug Bounty)

- **Target:** ClinicOS — clinic management SaaS (patients, appointments, billing, prescriptions). Handles PHI/health data.
- **Path:** `/home/ujjwal/Documents/My Apps/apps/05-clinicos/`
- **Scope:** Authorized review of Boss Ujjawal's own code. Defensive-only.
- **Date:** 2026-05-31
- **Reviewer:** Jarvis security-engineer-agent
- **Stack:** Next.js 16.1.6 (App Router) · NextAuth v4 (JWT, Credentials) · Prisma 7 · SQLite (dev) · Zod v4 · bcryptjs
- **Frameworks referenced:** OWASP Top 10 2021/2025, OWASP API Security Top 10 2023, CWE, MITRE ATT&CK, HIPAA Security Rule, NIST 800-53 Rev5

> **Threat model (1-line):** Multi-tenant SaaS where each authenticated staff user belongs to one `clinicId`. The core asset is PHI (diagnoses, allergies, medical history, contact info) + billing. Primary adversary = a **logged-in user of clinic A reading/modifying clinic B's data** (cross-tenant IDOR), plus over-privileged staff (receptionist doing admin/doctor actions). Tenant isolation is enforced *inconsistently per-route in app code* — there is no shared guard — so any route that forgets the `clinicId` check is exploitable by any authenticated user.

---

## Severity Summary

| # | Severity | Category | Title | Location |
|---|----------|----------|-------|----------|
**8 CRITICAL · 4 HIGH · 4 MEDIUM · 1 LOW · 1 INFO** (18 findings)

| 1 | **CRITICAL** | BOLA/IDOR · OWASP API1 · CWE-639 | Cross-tenant patient record read/modify/delete (`patients/[id]`) | `api/patients/[id]/route.ts` |
| 2 | **CRITICAL** | BOLA/IDOR · OWASP API1 · CWE-639 | Cross-tenant appointment read/update/cancel | `api/appointments/[id]/route.ts`, `queue/[id]/status` |
| 3 | **CRITICAL** | BOLA/IDOR · OWASP API1 · CWE-639 | Cross-tenant bill read + **billing tamper** (mark paid, change method) | `api/billing/[id]/route.ts` |
| 4 | **CRITICAL** | BOLA/IDOR · OWASP API1 · CWE-639 | Cross-tenant prescription read (PHI: diagnosis/meds) + PDF leak | `api/prescriptions/[id]/route.ts`, `.../pdf` |
| 5 | **HIGH** | BOLA/IDOR · CWE-639 | Cross-tenant doctor read/update + appointment-with-patient leak | `api/doctors/[id]/route.ts` |
| 6 | **CRITICAL** | Sensitive data committed · OWASP A05 · CWE-312/CWE-540 | `prisma/dev.db` (with seeded PHI) is git-tracked | `prisma/dev.db` |
| 7 | **HIGH** | Broken Function-Level Authz · OWASP API5 · CWE-862 | No role checks — receptionist can do doctor/clinical writes | most write routes |
| 8 | **HIGH** | Mass assignment · OWASP API6 · CWE-915 | Prescription POST trusts client `patientId`/`doctorId`/`appointmentId` (cross-tenant write) | `api/prescriptions/route.ts` |
| 9 | **HIGH** | Mass assignment · CWE-915 | Bill POST trusts client `patientId`/`appointmentId` (attach bill to another clinic's patient) | `api/billing/route.ts` |
| 10 | **HIGH** | Hardcoded secret · OWASP A05 · CWE-798 | Weak/static `NEXTAUTH_SECRET` committed-style in `.env` | `.env` |
| 11 | **MEDIUM** | Business logic · CWE-840 | Bill `total`/`subtotal`/`tax` fully client-supplied — financial integrity | `api/billing/route.ts` |
| 12 | **MEDIUM** | Info disclosure · OWASP A09 · CWE-209 | Raw Prisma error message returned to client (500 path) | `lib/api-helpers.ts` |
| 13 | **MEDIUM** | Missing rate limiting · OWASP API4 · CWE-307 | No rate limit on login / any API (credential stuffing, enumeration) | global |
| 14 | **MEDIUM** | Build hygiene · CWE-1127 | `typescript.ignoreBuildErrors: true` ships type-unsafe code | `next.config.ts` |
| 15 | **LOW** | Weak password policy · CWE-521 | No password complexity; seed uses `password123`/`admin123` | `auth.ts`, `seed.ts` |
| 16 | **LOW** | Missing security headers / cookie hardening | No CSP/HSTS; default NextAuth cookie flags only | global |
| 17 | **MEDIUM** | PHI in logs · OWASP A09 · CWE-532 | Reminder route logs full patient PII body to console | `api/appointments/[id]/remind/route.ts` |
| 18 | **INFO** | Account enumeration | Login returns distinguishable timing (user lookup before bcrypt) | `auth.ts` |

**Root cause for #1–#6, #8, #9:** there is **no centralized tenant-scoping guard**. Each `[id]` route does its own (or no) `clinicId` check. The ones that were fixed (`patients/[id]/history`, `patients/[id]/ai-summary`, `prescriptions/[id]/pdf`) prove the developer knows the pattern — but most `[id]` routes silently omit it. `middleware.ts` does **not** match `/api/*`, so middleware provides zero API protection; everything rides on per-route `getServerSession`.

---

## Findings

### [CRITICAL] BOLA/IDOR — Cross-tenant patient record read/modify/delete
**OWASP API1:2023 (BOLA) · CWE-639 · MITRE T1530**
`src/app/api/patients/[id]/route.ts` — GET (L32-51), PUT (L87-90), DELETE (L114)

> **Impact:** Any authenticated user of *any* clinic can read, edit, or (if admin of their own clinic) delete the full PHI record of *any* patient in the entire database — name, age, phone, email, address, blood group, **allergies, medical history**, plus all their appointments, prescriptions (diagnosis + medicines) and bills.
> **Likelihood:** High. `cuid` IDs are not secret — they appear in the list endpoint, in appointment/bill payloads, in URLs. An attacker enumerates IDs trivially via objects returned from their own clinic's related records, or via #5/#6.
> **Asset:** All patient PHI, system-wide. HIPAA-reportable breach class.
> **What's wrong:** GET does `prisma.patient.findUnique({ where: { id } })` with **no `clinicId` comparison** before returning. PUT updates `where: { id }` with no ownership check. DELETE checks `role === "admin"` but never checks that the patient belongs to the caller's clinic — a clinic-A admin can delete clinic-B patients.
> **Exploit scenario:** Receptionist at Clinic A is logged in. `GET /api/patients/<clinicB-patient-id>` → full medical record returned (200). `PUT` same URL with `{"allergies":"none"}` → tampers another clinic's patient record. Contrast: the sibling `patients/[id]/history/route.ts` (L83) and `ai-summary` (L44) DO check `patient.clinicId !== session.user.clinicId → 403`. This route forgot.
> **Remediation:**
>   - Short-term: After `findUnique`, add `if (!patient || patient.clinicId !== session.user.clinicId) return notFound("Patient")`. For PUT/DELETE, scope the write: `prisma.patient.updateMany({ where: { id, clinicId: session.user.clinicId }, data })` and treat `count === 0` as 404. (Use `updateMany`/`deleteMany` so the `clinicId` is part of the WHERE — never `update({where:{id}})`.)
>   - Long-term: Centralize. Build `requireSession()` + `assertOwns(model, id, session)` helpers (or a Prisma extension / RLS-style middleware) and route every `[id]` handler through it. Add an integration test per resource that asserts cross-tenant access → 404.

---

### [CRITICAL] BOLA/IDOR — Cross-tenant appointment read / update / cancel
**OWASP API1:2023 · CWE-639**
`src/app/api/appointments/[id]/route.ts` — GET (L29), PUT (L73), DELETE (L97); `src/app/api/queue/[id]/status/route.ts` — PUT (L39)

> **Impact:** Read any appointment in any clinic (returns full `patient`, `doctor`, `prescription`, `bill` — i.e. PHI). Change status, notes, time, type of any clinic's appointment. Cancel any appointment (DELETE sets `cancelled`). Queue-status PUT lets a user flip another clinic's patient to `completed`/`no_show`.
> **Likelihood:** High — same cuid-enumeration as #1.
> **Asset:** Appointment PHI + clinic operational integrity (queue/scheduling sabotage).
> **What's wrong:** All four handlers operate on `where: { id }` with no `clinicId` predicate and no post-fetch ownership check.
> **Exploit:** `PUT /api/queue/<clinicB-appt-id>/status {"status":"no_show"}` → disrupts Clinic B's live queue. `GET /api/appointments/<clinicB-appt-id>` → leaks patient name/phone + diagnosis.
> **Remediation:**
>   - Short-term: GET → fetch then `if (a.clinicId !== session.user.clinicId) return notFound()`. PUT/DELETE/status → `updateMany({ where: { id, clinicId: session.user.clinicId }, data })`, 404 on zero rows.
>   - Long-term: shared `assertOwns` guard (see #1).

---

### [CRITICAL] BOLA/IDOR + Billing tamper — Cross-tenant bill read & status change
**OWASP API1 + API3 · CWE-639 · CWE-840**
`src/app/api/billing/[id]/route.ts` — GET (L25), PUT (L69)

> **Impact:** Read any bill in any clinic (includes `patient`, `appointment.doctor`, `appointment.clinic`). **PUT lets any authenticated user mark any bill `paid` / `pending` and set `paymentMethod`** — direct financial-integrity attack and cross-tenant data tamper.
> **Likelihood:** High.
> **Asset:** Revenue integrity + patient billing PII.
> **What's wrong:** `findUnique({where:{id}})` / `update({where:{id}})` with no tenant scoping or role gate. A receptionist (or attacker in another clinic) can fraudulently mark unpaid bills as paid, or revert paid bills to pending.
> **Remediation:**
>   - Short-term: `prisma.bill.updateMany({ where: { id, clinicId: session.user.clinicId }, data })`; 404 on zero rows. Gate payment-status changes behind `role in (admin, receptionist)` per your policy.
>   - Long-term: treat payment-state transitions as auditable events (append-only audit log: who/when/old→new) — required for any clinic finance trail.

---

### [CRITICAL] BOLA/IDOR — Cross-tenant prescription read (clinical PHI) + PDF
**OWASP API1 · CWE-639**
`src/app/api/prescriptions/[id]/route.ts` — GET (L19, no check)

> **Impact:** `GET /api/prescriptions/<any-id>` returns diagnosis, medicines, instructions, patient, doctor, clinic for *any* clinic. This is the most sensitive PHI class (clinical diagnosis + medication).
> **Likelihood:** High.
> **What's wrong:** The base prescription GET has **no** `clinicId` check — note the sibling `prescriptions/[id]/pdf/route.ts` (L48) *does* check `prescription.appointment.clinicId !== session.user.clinicId → 403`. The JSON route was missed. (The `pdf` and `check-interactions` routes are correctly scoped/scopeless-by-design; the JSON one is the gap.)
> **Remediation:**
>   - Short-term: mirror the pdf route — after fetch, `if (prescription.appointment.clinicId !== session.user.clinicId) return notFound()`.
>   - Long-term: shared guard.

---

### [HIGH] BOLA/IDOR — Cross-tenant doctor read/update (+ patient leak)
**OWASP API1 · CWE-639**
`src/app/api/doctors/[id]/route.ts` — GET (L28), PUT (L70)

> **Impact:** GET returns a doctor with their last 10 appointments **including `patient: true`** → leaks Clinic B patients via Clinic B doctor ID. PUT updates any doctor's profile/`consultationFee` cross-tenant. (DELETE is role+exists-checked but still not clinic-scoped on the delete itself — a clinic-A admin can delete a clinic-B doctor and cascade-delete their prescriptions/appointments. Treat as HIGH too.)
> **Remediation:** scope all three with `clinicId`; use `deleteMany({where:{id, clinicId}})` for delete.

---

### [CRITICAL] Sensitive data committed to git — `prisma/dev.db`
**OWASP A05:2021 · CWE-312 (Cleartext storage) · CWE-540 (Info in source) · MITRE T1552.001**
`prisma/dev.db` (tracked in git per `git ls-files`)

> **Impact:** The SQLite database file is committed to the repository. It contains seeded PHI (20 patients with names, phones, addresses, blood groups, **allergies, medical history**, diagnoses, medicines) and **bcrypt password hashes** for admin/doctor/receptionist accounts. Anyone with repo access (or anyone the repo is ever pushed to / leaked) gets the full dataset and can offline-crack the (weak, see #15) passwords. While the current data is seed/demo, the *pattern* means real PHI will be committed the moment this DB is used with real data.
> **Likelihood:** High — it's already in the tree; any clone/fork/leak exposes it. `.gitignore` does NOT cover `prisma/dev.db` (it only ignores `/src/generated/prisma`, env, .next).
> **Asset:** Entire patient dataset + credential hashes.
> **What's wrong:** Binary DB tracked instead of ignored. `.gitignore` is missing `*.db` / `prisma/*.db`.
> **Remediation:**
>   - Short-term: `git rm --cached prisma/dev.db`, add `prisma/*.db` (and `*.db`, `*.sqlite`) to `.gitignore`, commit. If the repo is shared/pushed, **purge from history** (`git filter-repo` / BFG) and rotate any real credentials.
>   - Long-term: never use SQLite-file-in-repo for anything beyond local scratch; use Postgres (`.env.example` already points there) with the DB outside VCS. Add a `gitleaks`/pre-commit hook blocking `*.db` commits.

---

### [MEDIUM] PHI written to application logs (reminder route)
**OWASP A09:2021 · CWE-532 · HIPAA §164.312(b)**
`src/app/api/appointments/[id]/remind/route.ts` (L61-67)

> **Impact:** On every reminder, the route `console.log`s `template.to` (patient email/phone) and the full `template.body` (which embeds patient name, appointment details). PHI in stdout/log aggregation = uncontrolled disclosure to anyone with log access, and a HIPAA audit-control problem. (Note: this route *does* correctly clinic-scope at L37 — good — so it is **not** an IDOR. The issue is the logging.)
> **Remediation:** Remove the PHI `console.log`s, or log only non-PHI identifiers (appointmentId, channel) at info level. Route any required audit trail through a structured, access-controlled, redacting logger — never raw stdout.

---

### [HIGH] Broken Function-Level Authorization — no role enforcement on clinical/write actions
**OWASP API5:2023 (BFLA) · CWE-862**
Most write routes (`patients` POST/PUT, `appointments` POST/PUT, `prescriptions` POST, `billing` POST/PUT, `queue/next`, `queue/[id]/status`)

> **Impact:** The schema defines roles (`receptionist` default, `doctor`, `admin`) and the session carries `role`, but only `settings` PUT, `reports` GET, and the two DELETEs check it. **A receptionist can create/overwrite prescriptions** (clinical record forgery — wrong diagnosis/medication is a patient-safety issue), edit any appointment, and mutate bills. There is no doctor-vs-receptionist separation.
> **Likelihood:** High (any logged-in receptionist).
> **Remediation:**
>   - Short-term: add a `requireRole(session, [...allowed])` helper. Prescriptions write → `doctor`/`admin` only. Bill payment status → `receptionist`/`admin`. Settings/reports → `admin` (already done).
>   - Long-term: define a permission matrix (resource × action × role) in one module; enforce via a single middleware-style wrapper. Map to least-privilege (NIST AC-6).

---

### [HIGH] Mass assignment — Prescription POST trusts client IDs (cross-tenant write)
**OWASP API6:2023 · CWE-915**
`src/app/api/prescriptions/route.ts` POST (L100-111)

> **Impact:** The handler creates a prescription using client-supplied `patientId`, `doctorId`, `appointmentId` **without verifying any of them belong to the caller's clinic**. An attacker can attach a forged prescription to another clinic's appointment/patient, or mismatch patient↔doctor↔appointment within scope.
> **What's wrong:** No lookup confirming `appointment.clinicId === session.user.clinicId` (and that patient/doctor match the appointment). The "update existing" branch (L83-97) also updates by `appointmentId` cross-tenant.
> **Remediation:** Before create/update, load the appointment, assert `appointment.clinicId === session.user.clinicId`, and derive `patientId`/`doctorId` **from the appointment** rather than trusting the body. Require `role` doctor/admin (#7).

---

### [HIGH] Mass assignment — Bill POST trusts client patientId/appointmentId
**OWASP API6 · CWE-915**
`src/app/api/billing/route.ts` POST (L94-107)

> **Impact:** Bill is created with client `patientId`/`appointmentId` and the caller's own `clinicId` — so an attacker can create a bill in *their* clinic attached to *another* clinic's patient/appointment, corrupting both tenants' data and leaking the related patient on read-back (the response `include`s `patient`).
> **Remediation:** Validate `patientId` (and `appointmentId` if present) belong to `session.user.clinicId` before create: `prisma.patient.findFirst({where:{id:patientId, clinicId:session.user.clinicId}})` → 400/404 if missing.

---

### [HIGH] Hardcoded / weak NEXTAUTH_SECRET
**OWASP A05:2021 · CWE-798 · CWE-330**
`.env` (L2): `NEXTAUTH_SECRET="clinicos-secret-key-2024-secure"`

> **Impact:** This is the JWT signing key for sessions. It's a guessable, human-readable string (and the kind that ends up in screenshots / repos). Anyone who learns it can **forge a valid session JWT for any `id`/`role`/`clinicId`** — instant full compromise including cross-tenant + admin. `.env.example` correctly says "your-secret-key-here", so this real value is a hardcoded weak secret.
> **Mitigations present:** `.env` is gitignored (`.env*`) and not tracked — good, limits exposure to anyone with file/host access or a leak.
> **Remediation:**
>   - Short-term: rotate to a 32+ byte random value (`openssl rand -base64 48`), invalidating existing tokens.
>   - Long-term: load from a secrets manager (Vault / AWS Secrets Manager / Vercel encrypted env), never a literal in `.env`. Add a Semgrep/gitleaks CI rule to block weak/static secrets.

---

### [MEDIUM] Business logic — bill totals fully client-supplied
**CWE-840 · CWE-20**
`src/app/api/billing/route.ts` (schema L8-18, create L94)

> **Impact:** `subtotal`, `tax`, `discount`, `total` come straight from the client with only `min(0)`. No server-side recomputation, no `total == subtotal + tax - discount` invariant, no cross-check against `appointment.doctor.consultationFee` or the `items`. A user can issue a Rs. 0 (or negative-margin) bill, or arbitrary totals, undermining revenue reporting and enabling fraud.
> **Remediation:** Recompute `total` server-side from `items` + fee; reject if client `total` disagrees beyond a tolerance, or ignore the client total entirely. Validate `discount <= subtotal`.

---

### [MEDIUM] Information disclosure — raw error messages to client
**OWASP A09:2021 · CWE-209**
`src/lib/api-helpers.ts` (L36): `return NextResponse.json({ error: error.message }, { status: 500 })`

> **Impact:** On any non-handled `Error`, the raw message is returned to the client. Prisma/runtime errors can leak schema names, constraint details, file paths — aids attackers mapping the DB and IDOR targets.
> **Remediation:** Return a generic `{ error: "Internal server error" }` with a correlation id; log full detail server-side only. Keep the structured 400/404/409 branches.

---

### [MEDIUM] Missing rate limiting (login + all APIs)
**OWASP API4:2023 · CWE-307 · MITRE T1110**
Global — no limiter anywhere (grep found none)

> **Impact:** Credentials provider has no throttle → credential stuffing / brute force against `/api/auth/callback/credentials`. Unbounded IDOR enumeration of the `[id]` routes above. No protection against scraping all patient records.
> **Remediation:** Add an IP+account rate limiter (Upstash Ratelimit / `@vercel/firewall` / nginx) on auth (e.g. 5/min/account) and a global API budget. Add lockout/backoff on repeated auth failures.

---

### [MEDIUM] `typescript.ignoreBuildErrors: true`
**CWE-1127**
`next.config.ts` (L4)

> **Impact:** Type errors are suppressed at build — exactly the class of bug (wrong field, missing null check, unscoped query) that would otherwise be caught. Ships unsafe code to prod.
> **Remediation:** Remove `ignoreBuildErrors`; fix the errors. Gate CI on `tsc --noEmit`.

---

### [LOW] Weak password policy / default creds
**CWE-521 · CWE-1392**
`src/lib/auth.ts` (no policy), `prisma/seed.ts` (L7, L21): `password123`, `admin123`

> **Impact:** No min-length/complexity on credentials; seeded accounts use trivially guessable passwords (combined with #13's no-rate-limit = practical brute force). bcrypt cost 10 is acceptable but on the low end for PHI.
> **Remediation:** Enforce a password policy (length ≥12, breach-list check via HIBP k-anon) at user creation; never ship default creds to any shared/prod env; bump bcrypt cost to 12 or move to argon2id.

---

### [LOW] Missing security headers + cookie hardening
**OWASP A05 · CWE-1021 · CWE-614**
Global

> **Impact:** No CSP (XSS defense-in-depth), no HSTS, no `X-Content-Type-Options`/frame options. NextAuth sets `httpOnly`+`secure`+`sameSite=lax` by default in prod, but there's no explicit hardening or `__Host-` prefix.
> **Remediation:** Add a `headers()` block / middleware with CSP (esp. since `pdf` route emits raw HTML with inline `<style>` + `onclick` — tighten or move to nonce-CSP), HSTS, `X-Content-Type-Options: nosniff`, `Referrer-Policy`. Confirm cookie flags in prod.

---

### [INFO] Account enumeration via auth timing
**CWE-208 · CWE-204**
`src/lib/auth.ts` (L49-64)

> **Impact:** `authorize` returns early `null` when the user doesn't exist (before bcrypt), but runs bcrypt when it does — observable timing difference reveals which emails are registered. Minor, but combined with #13 it speeds targeting.
> **Remediation:** Always run a dummy bcrypt compare on the not-found path to equalize timing.

---

## Hardening — drop-in shared guard (eliminates #1–#6, #8, #9 root cause)

```ts
// src/lib/guard.ts
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { NextResponse } from "next/server";

export async function requireSession() {
  const session = await getServerSession(authOptions);
  if (!session) return { error: NextResponse.json({ error: "Unauthorized" }, { status: 401 }) } as const;
  return { session } as const;
}

export function requireRole(role: string, allowed: string[]) {
  return allowed.includes(role)
    ? null
    : NextResponse.json({ error: "Forbidden" }, { status: 403 });
}
```

```ts
// Pattern for every [id] write — tenant scoping lives IN the WHERE clause:
const r = await requireSession();
if ("error" in r) return r.error;
const { id } = await params;
const result = await prisma.patient.updateMany({
  where: { id, clinicId: r.session.user.clinicId }, // <-- scoped write
  data: parsed.data,
});
if (result.count === 0) return notFound("Patient"); // 404 hides existence cross-tenant
```

```ts
// Pattern for every [id] read:
const patient = await prisma.patient.findFirst({
  where: { id, clinicId: r.session.user.clinicId }, // <-- scoped read
  include: { /* ... */ },
});
if (!patient) return notFound("Patient");
```

Prefer `findFirst({where:{id, clinicId}})` and `updateMany/deleteMany({where:{id, clinicId}})` over `findUnique/update({where:{id}})` everywhere — it makes tenant scoping structurally part of the query rather than a forgettable extra `if`.

## Detection

- **App audit log (build it):** emit a structured event on every PHI read/write + bill status change: `{ts, userId, role, clinicId, resource, resourceId, action, result}`. Required for HIPAA audit controls anyway.
- **SIEM / log hunt (pseudocode):** alert when `resource.clinicId != actor.clinicId` ever appears (should be impossible after the fix → any hit = attack or regression). Alert on >N distinct `resourceId` reads per user per minute (enumeration).
- **Auth:** alert on >5 failed `credentials` logins per account / per IP in 5 min (credential stuffing, T1110).

## Response Runbook (cross-tenant PHI access suspected)
1. **Detect:** audit-log entry with mismatched clinicId, or anomalous enumeration rate.
2. **Triage:** query audit log for all actions by the actor; determine which `resourceId`s (patients) were touched and their `clinicId`s.
3. **Contain:** disable the user account; rotate `NEXTAUTH_SECRET` (invalidates all JWTs) if forgery suspected.
4. **Eradicate:** deploy the tenant-scoping guard; add regression tests.
5. **Recover:** restore any tampered bills/records from backup; verify integrity.
6. **Comms / Compliance:** PHI access by an unauthorized party is a **HIPAA breach** — engage breach-notification process (§164.400-414); document affected patients.

## Compliance Mapping
- **HIPAA Security Rule:** §164.312(a)(1) Access Control (findings #1–#9), §164.312(b) Audit Controls (no audit log), §164.308(a)(4) Info Access Management (no role enforcement #7), §164.312(e) Transmission Security (headers #16).
- **NIST 800-53 Rev5:** AC-3 (Access Enforcement) #1–#9, AC-6 (Least Privilege) #7, AU-2/AU-12 (Audit) detection gap, IA-5 (Authenticator Mgmt) #10/#15, SC-5/SC-7 (#13).
- **OWASP API Security Top 10 2023:** API1 (#1–#6), API3 (#3/#11), API4 (#13), API5 (#7), API6 (#8/#9).

## Verification Plan (no prod exploitation)
1. **Integration tests:** seed two clinics (A, B) + a user in each. For every `[id]` route, assert user-A → B's resource returns **404** (not 200/403-with-data). For every write, assert B's record is unchanged. This is the single highest-value test suite — add it before deploy.
2. **Role tests:** assert receptionist → prescription POST = 403; admin → settings PUT = 200.
3. **Static:** run `semgrep --config p/owasp-top-ten --config p/nextjs` + `gitleaks` in CI; add a custom Semgrep rule flagging `prisma.<model>.findUnique({where:{id}})` inside an API route without a nearby `clinicId` check.
4. **Billing invariant test:** POST a bill with `total` ≠ computed → expect rejection.
5. **Tabletop:** "A disgruntled receptionist at Clinic A wants every patient record in the platform — walk the kill chain and confirm each control now blocks it."

---

### Honesty / completeness notes
- All findings verified against actual source (file:line cited). I distinguished routes that *correctly* scope (`patients/[id]/history`, `patients/[id]/ai-summary`, `prescriptions/[id]/pdf`, `settings`, `reports`) from those that don't — the inconsistency is the story.
- Confirmed `.env` is **not** git-tracked (good) — so #10 is "weak secret on host", not "secret leaked to repo". HOWEVER `prisma/dev.db` **IS** git-tracked (finding #6) — seeded PHI + password hashes are in the repo.
- **Correction made mid-audit:** the `appointments/[id]/remind` route *does* correctly clinic-scope (L37), so it is NOT an IDOR — re-classified to the PHI-logging issue (#17). The other cross-tenant findings (#1–#5) are confirmed unscoped.
- The `pdf` route's HTML is **properly `escapeHtml`-escaped** — no stored XSS there (good). The IDOR on the JSON prescription route is the real issue.
- Not assessed (out of static scope): runtime CSRF behavior of NextAuth in this version, actual deployed cookie flags, prod DB (SQLite is dev-only per `.env.example` pointing at Postgres), and any code in client pages I truncated. Recommend the integration test suite (Verification #1) as the authoritative confirmation.
