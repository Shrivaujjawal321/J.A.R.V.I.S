# Bug Bounty / Defensive Audit — InvoFlow (Invoicing SaaS)

- **Target:** `/home/ujjwal/Documents/My Apps/apps/02-invoflow/`
- **Stack:** Next.js 16 (App Router) + NextAuth v4 (Credentials/JWT) + Prisma 7 + Neon Postgres + Zod + bcryptjs
- **Scope:** Authorized review of Boss Ujjawal's own code. Defensive-only.
- **Date:** 2026-05-31
- **Overall:** **Good baseline, not yet production-money-ready.** Honest verdict: this app is *well-built* on access control — almost every mutating/reading API route correctly calls `getSessionUser()` and scopes Prisma queries with `where: { id, userId: user.id }`, uses Zod validation, computes invoice totals server-side, and excludes the password hash from responses. I verified each route individually. The remaining issues are concentrated in **(a) the payment flow being a mock with no real PSP/integrity guarantees, (b) one real stored-XSS in the PDF/HTML route, (c) secret hygiene, and (d) missing rate limiting.** No widespread IDOR was found — the per-resource routes are scoped.

> Methodology note: I read every route under `src/app/api/`, the schema, auth config, middleware, and lib helpers line by line. Findings below are evidence-backed with file:line. Where I initially suspected a class of bug (mass-assignment, IDOR) and the code disproved it, I list it under "Checked and clean" so you can see the coverage.

---

## Severity Summary

| # | Severity | Category (OWASP / CWE) | Title | File:Line |
|---|----------|------------------------|-------|-----------|
| 1 | **HIGH** | A04 Insecure Design / CWE-840 | Payment is a mock: no real charge, status flips to `paid` on an unauthenticated request | `api/invoices/[id]/pay/route.ts:79-147` |
| 2 | **HIGH** | A03 Injection / CWE-79 | Stored XSS in invoice PDF/HTML route (unescaped user fields, served as `text/html` + auto-`window.print()`) | `api/invoices/[id]/pdf/route.ts:39-120` |
| 3 | **HIGH** | A02 Crypto / CWE-798 / CWE-321 | Weak placeholder `NEXTAUTH_SECRET` + live Neon DB credentials sitting in `.env` | `.env:1-2`, `src/lib/auth.ts:64` |
| 4 | **MEDIUM** | A04 / CWE-799 / CWE-770 | No rate limiting on login, register, public `/pay`, or email routes (brute force + spam + enumeration) | global |
| 5 | **MEDIUM** | A05 Misconfig / CWE-1059 | `typescript.ignoreBuildErrors: true` disables a key safety net | `next.config.ts:4-6` |
| 6 | **MEDIUM** | A05 / CWE-209 | `handleApiError` returns raw `error.message` (and Prisma internals) to the client on 500 | `src/lib/api-helpers.ts:36` |
| 7 | **MEDIUM** | A07 / CWE-307 | User enumeration on register (`"A user with this email already exists"`) and on login (distinct error messages) | `api/auth/register/route.ts:34`, `src/lib/auth.ts:24-29` |
| 8 | **LOW** | A04 / CWE-841 | Public pay GET leaks client email + business email to anyone with the invoice ID (by design, but unauthenticated) | `api/invoices/[id]/pay/route.ts:13-73` |
| 9 | **LOW** | A09 Logging / CWE-532 | Console-logs payer email + payment details to server logs (PII in logs) | `api/invoices/[id]/pay/route.ts:150-153` |
| 10 | **LOW** | A04 / CWE-770 | No HTTP security headers / CSP (amplifies the XSS in #2) | `next.config.ts` |
| 11 | **INFO** | — | Positive: broad correct authz + Zod + server-side totals + bcrypt + gitignored secrets | — |

---

## Findings

### 1. HIGH — [A04 Insecure Design / CWE-840 Business Logic Errors] — Payment is a mock; status flips to "paid" with no real money moving
**File:** `src/app/api/invoices/[id]/pay/route.ts:79-147`

The public POST `/api/invoices/[id]/pay` is intentionally unauthenticated (it's the customer-facing pay page). **Good news first:** it does NOT trust a client-supplied amount — it computes `balanceDue` server-side (`invoice.total - totalPaid`, line 116-117), rejects already-`paid`/`cancelled` invoices (102-114), and rejects `balanceDue <= 0` (119-124). So the naive "tamper the amount / re-pay a paid invoice" attacks are already blocked. Credit where due.

The real problem is that **there is no payment processor**. The flow generates a fake gateway id (`pay_${Date.now()}_${random}`, line 127), writes a `Payment` row, and sets `status: "paid"` (144-147) — all triggered by anyone who can POST to the URL, with **no charge ever made**:

```ts
const mockGatewayId = `pay_${Date.now()}_${Math.random()...}`;
const payment = await prisma.payment.create({ data: { invoiceId: id, amount: balanceDue, gateway: "online", gatewayPaymentId: mockGatewayId, status: "completed" }});
await prisma.invoice.update({ where: { id }, data: { status: "paid" } });
```

> Impact: Anyone who knows an invoice ID (IDs leak via emails, the pay link, PDFs) can mark it `paid` for free — the business's books show paid invoices that were never paid. The UI even shows a "Payment Successful" receipt. This is fine as a *demo/mock* but is a critical integrity hole the moment this represents real revenue. There is **no Stripe webhook route in the codebase** despite `STRIPE_SECRET_KEY` being present in `.env`.
> Likelihood: high (if treated as real). Asset: payment integrity, financial records.
> Existing mitigations: server-side amount, already-paid guard, balance guard (all good).
> Remediation:
>   - Wire a real PSP. The pay endpoint should create a Stripe **PaymentIntent** server-side using `invoice.total - paid` (never the body), return the client secret to Stripe Elements, and flip `status: "paid"` **only inside a signature-verified webhook** (`stripe.webhooks.constructEvent(rawBody, sig, STRIPE_WEBHOOK_SECRET)`).
>   - Add `Payment.gatewayPaymentId` as a `@unique` column and reconcile against the PSP; add an idempotency key so retries don't double-record.
>   - Until a PSP is wired, label this clearly as a demo and do not deploy with real client data.

---

### 2. HIGH — [A03 Injection / CWE-79 Stored XSS] — Invoice PDF/HTML route injects unescaped user fields and serves them as live HTML
**File:** `src/app/api/invoices/[id]/pdf/route.ts:39-120`

This route IS correctly authenticated and tenant-scoped (`getSessionUser()` + `findFirst({ where: { id, userId: user.id } })`, lines 11-25) — no IDOR here. The bug is that it builds an HTML string by directly interpolating user-controlled fields with **zero escaping**, returns it as `Content-Type: text/html` (line 120), and auto-runs `window.print()` (line 115):

```ts
<td ...>${item.description}</td>                         // line 39
<div ...>${invoice.user.address}</div>                  // line 72
<div>${invoice.client.name}</div>                       // line 83
<div ...>${invoice.notes}</div>                          // line 112
<div ...>${invoice.terms}</div>                          // line 113
```

All of `item.description`, `client.name/company/address/phone`, `invoice.notes/terms`, and `user.businessName/address/phone/taxId` are free-text fields the user (or, via a future shared/import path, a client) controls. Example: set an item description to `<img src=x onerror=alert(document.cookie)>` → it executes when the invoice "PDF" is opened in a browser, on the app's own origin.

> Impact: Stored XSS executing on the InvoFlow origin → session/JWT theft, actions-as-user, data exfiltration. The blast radius is currently same-tenant (only the owner can open their own scoped PDF), but it becomes cross-tenant the moment any sharing/staff/multi-user-per-account feature is added — and self-XSS still matters if any field is ever populated from an external import. With no CSP (Finding 10) there's nothing to blunt it.
> Likelihood: medium. Asset: session integrity.
> Remediation:
>   - HTML-escape every interpolated value. Minimal helper:
>     ```ts
>     const esc = (s: unknown) => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]!));
>     ```
>     then `${esc(invoice.notes)}` etc. everywhere.
>   - Better: render a real PDF server-side (`@react-pdf/renderer`, or Playwright print-to-pdf) and return `application/pdf` + `Content-Disposition: attachment` so the browser never executes it as a document.
>   - Add a `Content-Security-Policy` (Finding 10).

---

### 3. HIGH — [A02 Cryptographic Failures / CWE-798 Hardcoded Credentials / CWE-321 Hardcoded Crypto Key] — Weak NEXTAUTH_SECRET + live DB creds in `.env`
**File:** `.env:1-2`, `src/lib/auth.ts:64`

```
DATABASE_URL="postgresql://neondb_owner:npg_dFj8RVU0wJct@ep-solitary-shadow-...neon.tech/neondb?sslmode=require"
NEXTAUTH_SECRET="invoflow-super-secret-key-change-in-production"
```

Two issues: (a) `NEXTAUTH_SECRET` is a guessable English placeholder. NextAuth uses it to sign the session JWT — a guessable secret means an attacker can **forge a session token for any user** → full account takeover of every tenant, if this value reaches prod. (b) `.env` contains a **live-looking Neon Postgres connection string with the password in cleartext**.

> Good: `.env*` IS in `.gitignore` (line 34) and I confirmed via `git ls-files` that `.env` is **not tracked** — secrets are not in git history. That's the main thing done right.
> Impact: forged sessions (a); DB compromise if the `.env` value leaks via a build artifact, log, or shared machine (b).
> Likelihood: medium. Asset: all sessions, the entire database.
> Remediation:
>   - Generate a real secret: `openssl rand -base64 32`. Set it per-environment via Vercel env vars (a secret store), never a committed/placeholder file. Add a boot assertion that refuses to start if `NEXTAUTH_SECRET` is missing or matches the placeholder.
>   - **Rotate the Neon DB password** — treat any credential that has lived in a working-tree file as potentially exposed. Restrict the DB role to least privilege.
>   - If `STRIPE_SECRET_KEY` / `OPENAI_API_KEY` / `GMAIL_APP_PASSWORD` were ever real values in this `.env`, rotate them too. Prefer a Stripe **restricted** key.

---

### 4. MEDIUM — [A04 / CWE-799 Improper Control of Interaction Frequency / CWE-770] — No rate limiting anywhere
**Files:** `api/auth/[...nextauth]`, `api/auth/register/route.ts`, `api/invoices/[id]/pay/route.ts`, `api/invoices/[id]/send-email/route.ts`, `api/invoices/[id]/remind/route.ts`

No throttling on login (credential brute force), register (account/enumeration spam), the public pay endpoint, or the email routes.

> Impact: password brute force against the credentials provider; mass payment/email triggering. If the email routes are ever wired to a real SMTP/Gmail sender (currently they only `console.log`), this becomes a spam/reputation vector.
> Remediation: Add IP + account rate limiting (e.g. `@upstash/ratelimit` with Vercel KV, or `@vercel/firewall`) on auth, register, pay, and email routes. Add a small exponential backoff on repeated failed logins per account.

---

### 5. MEDIUM — [A05 Security Misconfiguration / CWE-1059] — TypeScript build errors ignored
**File:** `next.config.ts:4-6`

```ts
typescript: { ignoreBuildErrors: true },
```

> Impact: Type errors can't fail the build. The `Record<string, unknown>` / loosely-typed `body` patterns in a few routes (e.g. `recurring` PUT at lines 134-150 reads `id, active, frequency, nextDate` off raw `body` without Zod) are exactly the kind of thing a strict build catches. Shift-left control is off.
> Remediation: Remove the ignore; fix whatever it's hiding. Run `tsc --noEmit` + `eslint` as a CI gate. (ESLint is run at build by default; keep it.)

---

### 6. MEDIUM — [A05 / CWE-209 Information Exposure Through Error Message]
**File:** `src/lib/api-helpers.ts:36`

```ts
if (error instanceof Error) { ...; return NextResponse.json({ error: error.message }, { status: 500 }); }
```

The generic 500 path echoes the raw exception message to the client, which can include Prisma/SQL internals, column names, or stack context.

> Remediation: Log the full error server-side with a correlation id; return a generic `{ error: "Internal server error", id }` to the client. The ZodError and known-constraint branches above it are fine to keep.

---

### 7. MEDIUM — [A07 Identification & Auth Failures / CWE-307 / CWE-203] — User enumeration
**Files:** `api/auth/register/route.ts:34`, `src/lib/auth.ts:23-29`

Register returns `"A user with this email already exists"` (409) — confirms which emails are registered. Login throws distinct errors: `"No user found with this email"` vs `"Invalid password"` (auth.ts 24, 29) — same enumeration oracle.

> Impact: an attacker can build a list of valid accounts to target with brute force / phishing. Combined with no rate limiting (Finding 4) this is meaningfully exploitable.
> Remediation: Return a generic, identical response for both "no user" and "wrong password" on login (NextAuth typically surfaces a single `CredentialsSignin`). For register, consider a generic "If this email is available you'll be able to sign in" or at least pair it with rate limiting + CAPTCHA on repeated attempts.

---

### 8. LOW — [A04 / CWE-841] — Public pay GET exposes client + business email to anyone with the invoice ID
**File:** `src/app/api/invoices/[id]/pay/route.ts:13-73`

The public GET returns `client.email` and `business.email` (and full line items) to any unauthenticated caller who has the invoice ID. This is partly by-design (the payer needs to see who they're paying), and it correctly uses `select` to avoid leaking the password hash / secret user columns — good. But the client's email is arguably more PII than a payer needs.

> Impact: minor PII disclosure / scraping if invoice IDs are guessed (CUIDs make mass-enumeration hard, mitigating this).
> Remediation: Consider dropping `client.email` from the public payload (the payer already knows who they are). Keep business name; business email is reasonable. Optionally gate the pay link behind a per-invoice unguessable token rather than the raw DB id.

---

### 9. LOW — [A09 Logging Failures / CWE-532 Insertion of Sensitive Info into Log] — PII in server logs
**File:** `src/app/api/invoices/[id]/pay/route.ts:150-153` (also `send-email` and `remind` routes log client emails)

```ts
console.log(`  Payer: ${payerName || invoice.client.name} (${payerEmail || invoice.client.email})`);
```

> Impact: payer/client emails written to stdout → captured by the hosting platform's log retention; PII in logs is a GDPR/retention concern.
> Remediation: Redact or drop PII from logs; if you need correlation, log the invoice id only. Use a structured logger with a redaction allowlist.

---

### 10. LOW — [A05 / CWE-1021] — No security headers / CSP
**File:** `next.config.ts` (no `headers()` defined)

No `Content-Security-Policy`, `X-Frame-Options`/`frame-ancestors`, `X-Content-Type-Options`, `Referrer-Policy`, or HSTS. A CSP would significantly blunt the XSS in Finding 2.

> Remediation: Add a `headers()` block in `next.config.ts` setting `Content-Security-Policy` (script-src self + nonces), `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Strict-Transport-Security`, and `frame-ancestors 'none'`.

---

### 11. INFO — Positive findings (verified, not assumed)
These were checked specifically because they're the usual SaaS failure points, and the code handles them correctly:

- **Access control is consistently applied.** Every per-resource and action route I read calls `getSessionUser()` → `unauthorized()` and scopes with `where: { id, userId: user.id }` (or `where: { invoice: { userId: user.id } }` for payments). Verified in: invoices `[id]` GET/PUT/DELETE, clients `[id]` GET/PUT/DELETE, invoices `[id]/pay` (the privileged GET is the public one by design), `payments` POST/GET, `pdf`, `send`, `send-email`, `remind`, `duplicate`, `check-overdue`, `smart`, `recurring`, `dashboard`, `analytics`, `reports`, `reports/revenue`, `settings`. **No IDOR found** on authenticated routes.
- **No mass assignment.** Invoice/client/settings/recurring writes use **Zod schemas** with explicit field whitelists, not raw-`body` spreads. `clientId` ownership is verified on recurring create (lines 85-90). Settings PATCH only allows `name/businessName/address/phone/taxId` and re-selects safe output.
- **Money is computed server-side.** Invoice create/update recompute `subtotal/tax/total` from items + taxRate (invoices route 97-106; `[id]` PUT 102-118) — the client cannot set the total directly. Payment POST rejects over-payment (`totalPaid > invoice.total`, line 74).
- **Password handling is correct.** bcrypt cost 10; register uses `select` to exclude the hash (register 49-55); settings/pay use `select` to avoid leaking it. `getSessionUser` returns only id/email/name.
- **Secrets not in git.** `.env*` and `*.db` are gitignored and untracked (confirmed via `git ls-files`).
- **No SQL injection surface.** All DB access is via Prisma's typed query builder — no raw `$queryRawUnsafe`/string-built SQL anywhere.
- **Page-level auth.** `middleware.ts` wraps `withAuth` over all dashboard page routes (redirect to `/login`). (API routes self-authenticate, which is the correct pattern — middleware is not relied on for API authz.)

---

## Priority Fix Order
1. **Finding 2 (XSS)** — escape PDF HTML or render a real PDF. Concrete, fast, real exploit.
2. **Finding 3 (secrets)** — strong `NEXTAUTH_SECRET` via env store + rotate Neon password.
3. **Finding 1 (payments)** — wire a real Stripe PaymentIntent + signed webhook before any real-money use; add idempotency + unique gateway id.
4. **Findings 4, 7 (rate limit + enumeration)** — throttle auth/register/pay/email; generic auth errors.
5. **Findings 5, 6, 9, 10** — re-enable type checks; sanitize 500 output; redact log PII; add security headers/CSP.

## Verification Plan (no prod exploitation)
- **XSS regression test:** create an invoice with `notes = <img src=x onerror=alert(1)>`; GET the `/pdf` route; assert the response body is escaped (`&lt;img`) or `Content-Type: application/pdf`.
- **Authz regression suite:** seed users A and B; as B, hit every `/api/.../[id]` route with A's ids → expect 404/401. Add to CI as a gate (this already passes — lock it in so it stays passing).
- **Payment integrity:** once Stripe is wired, assert `status:"paid"` is only set by a webhook with a valid signature; assert the pay POST cannot mark paid on its own.
- **SAST/secrets in CI:** Semgrep (`p/owasp-top-ten`, `p/nextjs`) + a custom rule flagging unescaped `${...}` inside HTML template literals; `gitleaks`/`trufflehog` pre-commit; `tsc --noEmit` + ESLint gate (re-enabled per Finding 5).
- **Boot assertion:** test that the app refuses to start when `NEXTAUTH_SECRET` is unset or equals the placeholder.

## Compliance Mapping
- Client/payer PII (Findings 8, 9) → GDPR Art. 32 (security of processing) / NIST 800-53 **SI-11**, **AU-3**.
- Payment integrity (Finding 1) → if real cards are involved, keep all card data in Stripe Elements/Checkout so InvoFlow stays out of PCI scope (SAQ-A); NIST **SI-10**.
- Crypto/secrets (Finding 3) → NIST **IA-5**, **SC-12/SC-28**.
- XSS (Finding 2) → OWASP A03, CWE-79, NIST **SI-10**; CSP → **SC-18**.
- Rate limiting (Finding 4) → NIST **SC-5**, **AC-7**.
- Error leakage (Finding 6) → NIST **SI-11**.
