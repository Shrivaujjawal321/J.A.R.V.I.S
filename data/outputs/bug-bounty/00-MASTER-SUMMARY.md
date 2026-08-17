# 🛡️ Bug Bounty — Master Summary (11 apps)

**Date:** 2026-05-31 · Audited by 11 parallel security-engineer agents · Defensive-only, Boss's own code.
**Reports:** one `.md` per app in this folder.

---

## 🚨 URGENT — FIX TODAY (live exposure right now)

1. **ContentForge — password hashes LIVE in a PUBLIC GitHub repo.**
   `dev.db` (user emails + bcrypt hashes) sitting in `github.com/Shrivaujjawal321/contentforge` (verified public + HTTP 200). Anyone can clone + offline-crack.
   → **Make repo private NOW → `git rm --cached dev.db` + purge history → rotate all those passwords.**

2. **McpIndex (LIVE prod) — secrets unrotated + paid endpoint open.**
   GitHub PAT + Gemini key + Neon DB password in `.env.local` (rotation deadline 2026-05-28 already passed — **rotate all 3**). `/api/search` is unauthenticated + un-rate-limited → every query burns Gemini money (confirmed live). **Add rate-limit + billing alert.**
   ✅ Good: secrets were never committed to git.

3. **ClinicOS — 8 CRITICAL cross-tenant IDORs on PATIENT HEALTH DATA.**
   Any logged-in user of any clinic can read/edit/delete ANY patient's records, prescriptions, bills. If this ever deploys with real patients = privacy disaster. **Do not deploy until fixed.**

---

## 📊 Severity Scoreboard

| App | Crit | High | Med | Low | Headline issue |
|-----|:---:|:---:|:---:|:---:|----------------|
| **ClinicOS** (05) | 8 | 1 | 4 | 1 | Mass cross-tenant IDOR on PHI + git-tracked dev.db |
| **TeamPulse** (08) | 5 | 6 | — | — | ~9 single-resource routes ignore orgId; fake "anonymous" survey |
| **ContentForge** (09) | 3 | 1 | 6 | — | **Password DB public on GitHub** + stored XSS + weak secret |
| **FeedbackLoop** (03) | 1 | 3 | 4 | 1 | dev.db committed to git + stored XSS + SSRF landmine |
| **ShipDash** (07) | 2 | 3 | 5 | — | dev.db w/ API keys in git + unauth webhook + IDORs |
| **HireSync AI** (01) | 1 | 3 | 5 | 4 | Weak NEXTAUTH_SECRET + no RBAC (new users default admin) |
| **McpIndex** (LIVE) | 1 | 2 | 3 | — | Unrotated secrets + unrated paid Gemini endpoint |
| **InvoFlow** (02) | 0 | 3 | 4 | 2 | Mock payment + PDF stored XSS + secret hygiene |
| **LearnForge** (04) | 0 | 2 | 6 | — | Paywall bypass (any token enrolls) + weak secret |
| **PropStack** (06) | 0 | 3 | 4 | — | One unscoped maintenance POST + dev.db in git |
| **CompliMate** (10) | 0 | 0 | 4 | 2 | Cleanest — only XSS in reports + no RBAC |

**Totals:** ~21 Critical · ~27 High · ~45 Medium across 11 apps.

---

## 🔁 THE 5 RECURRING BUGS (fix once = fix everywhere)

Same AI generator built all 10 SaaS apps, so they share the SAME flaws. Fix the pattern once and apply to all:

1. **Weak/placeholder `NEXTAUTH_SECRET`** (e.g. `"appname-secret-key-2024"`) — in **all 10**. Anyone who guesses it forges any session → full auth bypass.
   → Rotate to `openssl rand -base64 48` per app, store in env vault, add boot-time guard rejecting placeholder.

2. **`prisma/dev.db` committed to git** — in 5+ apps (ClinicOS, FeedbackLoop, ShipDash, PropStack, ContentForge). Leaks password hashes + PII.
   → Add `*.db` to `.gitignore`, `git rm --cached`, purge history.

3. **Inconsistent tenant scoping (IDOR)** — collection routes scope by orgId, but many `[id]` routes forget it (worst: ClinicOS, TeamPulse, ShipDash).
   → Add ONE shared `getForUser(id, orgId)` guard, use on every `[id]` route. Add a 2-tenant integration test.

4. **Stored XSS in HTML/PDF/report routes** — user fields interpolated raw into `text/html`. In most apps.
   → Escape all interpolated values (or DOMPurify) + strict CSP.

5. **No rate-limiting + no RBAC anywhere** — credential stuffing, cost-abuse, and every user effectively admin.
   → Add Upstash rate-limit middleware + a `requireRole()` helper.

---

## ✅ THE GOOD NEWS (real, agents verified)
- **No SQL injection anywhere** — Prisma parameterizes everything.
- **CompliMate, InvoFlow, PropStack, FeedbackLoop, LearnForge** have genuinely solid tenant isolation — the IDOR cluster is NOT universal.
- **McpIndex** (the live one) has clean injection hygiene; only operational issues (rotate + rate-limit).
- bcrypt used correctly for passwords; React auto-escaping protects the UIs (XSS is only in the raw-HTML email/report/pdf routes).

---

## 🎯 RECOMMENDED ORDER
1. **Today:** ContentForge repo private + purge (live leak) → McpIndex rotate 3 secrets (live).
2. **This week:** the 5 recurring fixes via a shared `lib/` patch applied to all 10 SaaS apps (one fix, ten apps).
3. **Before any deploy:** ClinicOS + TeamPulse + ShipDash IDOR gates + 2-tenant tests.

> Want me to dispatch `backend-engineer-agent` to actually WRITE the shared fixes (secret rotation + tenant guard + escape helper + rate-limit) and apply across all 10 apps? That converts these reports into patched code.
