# McpIndex — Defensive Security Audit (Bug Bounty)

**Target:** McpIndex — MCP server discovery (https://mcpindex-nu.vercel.app)
**Repo:** `/home/ujjwal/Documents/mcp-hub/`
**Stack:** Next.js 16 (App Router) + Tailwind 4 + Neon Postgres + pgvector + Gemini embeddings + Vercel
**Scope:** Authorized review — Boss owns the code. Defensive-only.
**Date:** 2026-05-31
**Live status:** Confirmed deployed. `/api/search` returns 200 with real semantic results — Gemini embedding path is LIVE and reachable unauthenticated (verified: `q=database` → 200, `match_mode:"semantic"`, `took_ms:214`).

**Live verification performed (read-only, single low-volume probes — no flooding):**
- `GET /api/search?q=database` → HTTP 200, real semantic results, Gemini called. ✅ confirms Finding #2.
- Root + `/api/search` response headers inspected → HSTS present, but no X-Frame-Options / enforced CSP / nosniff / Referrer-Policy / Permissions-Policy. ✅ Finding #5.
- `/server/<slug>` → 200 in **0.087s** = served from Vercel ISR cache (`x-nextjs-prerender: 1`). So the per-view Gemini call in #3 fires **only on cache miss / revalidation**, not every hit — see corrected #3.
- `git log --all -p` grep for all 3 secret strings → **0 hits**. Secrets never committed. ✅

---

## Severity Summary

| # | Severity | Finding | File | Exploitable in prod NOW? |
|---|----------|---------|------|--------------------------|
| 1 | **CRITICAL** | Live secrets in `.env.local` on disk — GitHub PAT + Gemini key + Neon DB creds in plaintext (rotation date already passed) | `.env.local:5,8,11` | Yes if disk/repo leaks — secrets are valid & unrotated |
| 2 | **HIGH** | No rate-limit / auth on `/api/search` → unbounded Gemini embedding cost-abuse (financial DoS) | `src/app/api/search/route.ts:36` | **YES — live, confirmed** |
| 3 | **HIGH** | No rate-limit on any route → request-flood DoS on Neon (serverless billing) + pgvector scans | `src/lib/data.ts` (all queries) | **YES — live** |
| 4 | **MEDIUM** | Embedding query is sent to Gemini before any length cap → large-body amplification of cost per request | `src/app/api/search/route.ts:40`, `embeddings.ts:12` | **YES — live** |
| 5 | **MEDIUM** | Missing security headers: no `X-Frame-Options`/`frame-ancestors` (clickjacking), no enforced CSP, no `nosniff`, no `Referrer-Policy`, no `Permissions-Policy`. (HSTS **is** present via Vercel — verified live.) | `next.config.ts` | **YES — live** |
| 6 | **MEDIUM** | `/api/digest/subscribe` accepts arbitrary email with weak validation, no rate-limit → spam/abuse vector once wired | `src/app/api/digest/subscribe/route.ts:21` | Partial (stub today) |
| 7 | **LOW** | `dbRowToSummary` does unguarded `JSON.parse` on `score_dimensions` → 500 on malformed DB row | `src/lib/data.ts:206` | Low |
| 8 | **LOW** | Verbose `console.warn` logs full error objects (DB/embedding errors) → info leak in Vercel logs | `src/lib/data.ts:658,681` | Low |
| 9 | **INFO** | `limit` param parsed with `parseInt` — clamped 1–50 (GOOD); `page` unbounded → deep-offset scans | `search/route.ts:41`, `browse/page.tsx:18` | Info |
| 10 | **INFO (GOOD)** | SQL is **parameterized correctly** everywhere — no SQLi. `.env.local` **not** in git history. No XSS sinks. | — | N/A — these are PASSES |

---

## 1. CRITICAL — Live secrets in `.env.local` (CWE-798 / CWE-312 / OWASP A07:2021)

**File:** `/home/ujjwal/Documents/mcp-hub/.env.local`

```
GITHUB_TOKEN=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      # line 5
GEMINI_API_KEY=AIzaSyC4FpeZck05JoWSp4MYjJEwYQLnh04QhLk     # line 8
DATABASE_URL=postgresql://neondb_owner:npg_yFbD12OJIxZr@...neon.tech/neondb   # line 11
```

**Kya galat hai (what's wrong):**
Teen live production secrets plaintext mein disk pe pade hain. The file header itself says *"Token expiry: rotate after DevNetwork AI 2026 submission (2026-05-28)"* — **woh date nikal chuki hai (2026-05-28 < today 2026-05-31), so these are overdue for rotation and presumed still valid.**

**GOOD news (verified):** `.env.local` is **NOT** committed and **never appeared in git history** — I grepped `git log --all -p` for all three secret strings → 0 matches. `.gitignore` correctly covers it. So this is **not a public GitHub leak** today. The risk is: secrets-on-disk + overdue rotation + the Neon string includes the **password inline** (`npg_yFbD12OJIxZr`), and the DB is internet-reachable (Neon serverless over HTTPS).

**Exploit scenario:**
- The Neon `DATABASE_URL` grants `neondb_owner` (owner = full read/write/DDL). Anyone who obtains this string (laptop compromise, accidental paste, a future `git add -f`, a screen-share, a leaked Vercel env dump) gets **full DB control** — read all rows, drop tables, inject poisoned embeddings.
- The `GITHUB_TOKEN` (classic `ghp_` PAT) — depending on its scopes, can read/write the Boss's repos. Classic PATs are often broad.
- The `GEMINI_API_KEY` — direct billing abuse if exfiltrated.

**FIX:**
- **Short-term (do today):** Rotate ALL THREE now — the file's own deadline has passed.
  - Neon: rotate the role password in the Neon console → update Vercel env var. (`neondb_owner` is over-privileged — see long-term.)
  - GitHub: revoke `ghp_h7OL...` at https://github.com/settings/tokens, mint a **fine-grained** PAT scoped to public-repo read-only (the scraper only needs public search/read).
  - Gemini: regenerate at https://aistudio.google.com/app/apikey.
- **Long-term:**
  - Create a **least-privilege Neon role** for the runtime app: `SELECT` on `servers` only, no DDL, no write. The owner role should only be used by migration scripts run from a trusted machine. (NIST 800-53 AC-6 least privilege.)
  - Add **API key restrictions** on the Gemini key (Google Cloud console → restrict to the embedding API + optionally HTTP referrer/IP). Since Gemini is only called server-side on Vercel, an IP allowlist isn't easy on serverless, but API-scope restriction is.
  - Store all secrets only in Vercel Environment Variables (Production scope), never persist a populated `.env.local` long-term — keep `.env.local.example` with placeholders only.
- **Verification:** After rotation, confirm the old Neon password fails: `psql "<old-url>"` should error auth. Confirm old GitHub PAT returns 401 on `curl -H "Authorization: token ghp_h7OL..." https://api.github.com/user`.

---

## 2. HIGH — Unauthenticated, unrated `/api/search` = Gemini cost-abuse / financial DoS (OWASP API4:2023 Unrestricted Resource Consumption / OWASP LLM04 Model DoS / CWE-770)

**File:** `src/app/api/search/route.ts:36-76` → `src/lib/data.ts:642` (`searchServersBySimilarity`) → `src/lib/embeddings.ts:12` (`generateEmbedding`)

**Kya galat hai:**
Every `GET /api/search?q=...` with a non-empty `q` calls `searchServersBySimilarity()`, which **immediately fires a paid Gemini `embedContent` request** (`embeddings.ts:24`) for the user's raw query before any throttling. There is **zero** rate-limiting, auth, CAPTCHA, or per-IP cap anywhere in the codebase. I confirmed it live:

```
$ curl "https://mcpindex-nu.vercel.app/api/search?q=database&limit=2"  → HTTP 200, real semantic results
```

**Exploit scenario:**
An attacker runs a trivial loop:
```
for i in ...: GET /api/search?q=<random unique string i>
```
Each unique query = one Gemini embedding billing event + one pgvector scan + one Neon serverless invocation. A few thousand requests/minute from a single box (or a botnet) can:
1. **Burn the Gemini quota / rack up Gemini bill** (LLM04 Model DoS).
2. **Burn Neon serverless compute** (each request hits the DB).
3. Cache won't save you — unique `q` values bypass any CDN cache; the route is dynamic.

This is the single most-likely-to-actually-hurt-Boss issue because it's **live right now** and costs real money.

**FIX:**
- **Short-term (highest ROI):**
  - Add IP-based rate-limiting at the edge. Cheapest path on Vercel: **Upstash Ratelimit** (`@upstash/ratelimit` + `@upstash/redis`) in Next.js middleware. Example budget: 20 req / 10s / IP for `/api/search`, 60/min sliding.
  - Add a **server-side query cache** keyed by `LOWER(trim(q))` so repeated popular queries don't re-embed. Even an in-memory LRU (per serverless instance) + a short Neon-side cache table cuts cost massively. Cache the embedding vector, not just results.
  - Enforce a **max query length** before embedding (see Finding #4).
- **Long-term:**
  - Pre-compute embeddings for a fixed dictionary of common queries; serve those without hitting Gemini.
  - Add a Vercel WAF / firewall rule (Vercel Pro Firewall or Cloudflare in front) for burst protection + bot challenge on `/api/*`.
  - Add Gemini **budget alerts** in Google Cloud billing so a runaway is caught in hours, not at month-end.
- **Detection:** Alert when `/api/search` request rate per IP exceeds N/min, or when daily Gemini embedding calls exceed a baseline. (See Detection section.)
- **Hand-off:** Rate-limit + cache implementation → `backend-engineer-agent`. Gemini budget caps / LLM-DoS hardening → `ml-engineer-agent`. Vercel/Cloudflare WAF → `devops-sre-agent`.

---

## 3. HIGH — No rate-limit on ANY route → Neon billing/availability DoS (OWASP API4:2023 / CWE-770)

**Files:** all of `src/lib/data.ts` (every DB query), `src/app/browse/page.tsx`, `src/app/server/[slug]/page.tsx`

**Kya galat hai:**
Same root cause as #2 but broader — **no global throttle exists**. `browseServers` runs **two** Neon round-trips per request (`data.ts:464` — count + data via `Promise.all`). The server-detail page (`server/[slug]/page.tsx:77`) fires a Gemini embedding to find "similar servers" — **on cache miss / ISR revalidation** (live test showed cached hits return in 0.087s with no embedding cost; the cost is paid when the cache is cold or stale). The `/browse` page *also* calls `searchServersBySimilarity` whenever `?q=` is present (`browse/page.tsx:68`) — and `/browse` is **not** as aggressively cached as detail pages because of the query-param permutations, so a `?q=<unique>` flood there ALSO hits Gemini, same as #2. Deep pagination (`?page=99999`) forces large `OFFSET` scans (`data.ts:461`, `browse/page.tsx:56` — `page` is validated `>0` but has **no upper bound**).

**Exploit scenario:** Flood `/browse?page=N` or `/server/<slug>` → multiply Neon invocations and (for detail pages) Gemini calls. Serverless Postgres bills per compute-second; an attacker turns Boss's free/low tier into a surprise bill, or exhausts connection budget → legit users get errors.

**FIX:**
- Apply the same edge rate-limiter from #2 globally via `middleware.ts` (matcher `/((?!_next/static|_next/image|favicon).*)`). This is the key control because `/browse?q=` is the un-cached Gemini path.
- **Stop embedding on the detail page**: `server/[slug]/page.tsx:77-84` calls `searchServersBySimilarity(server.description, 5)` to fetch "similar servers." Even though ISR caches most hits, on revalidation this is a wasted Gemini call. Replace with the cheap `getSimilarServers(slug, category)` (already exists, `data.ts:545`, pure SQL same-category) as the primary path, OR pre-compute a `similar_slugs` column at ingest time. No per-view Gemini call.
- Cap `page` (e.g. `Math.min(page, 500)`).
- Use Next.js route segment caching / ISR for `/browse` and `/server/[slug]` (these are read-only public data) so most traffic is served from cache, not the DB.

---

## 4. MEDIUM — No input-length cap before embedding → cost amplification (OWASP LLM04 / CWE-20)

**File:** `src/app/api/search/route.ts:40` (`query = searchParams.get('q')`), `src/lib/embeddings.ts:12-33`

**Kya galat hai:**
`q` is taken raw and passed to `generateEmbedding(query)`. There's no max length. Gemini embedding cost/latency scales with input tokens. An attacker can send a multi-kilobyte `q` (URLs allow long query strings; or via the documented usage there's no body, but `q` can still be large) to maximize cost-per-request and slow the endpoint.

**FIX:**
- Clamp before embedding: `const q = (searchParams.get('q') ?? '').slice(0, 256)`. A search query realistically never needs >256 chars.
- Reject queries over the cap with `400` rather than silently truncating, if you prefer explicit behavior.
- Defense-in-depth with #2's rate-limit + cache.

---

## 5. MEDIUM — Missing security headers (OWASP A05:2021 Misconfiguration / CWE-693 / CWE-1021 Clickjacking)

**File:** `next.config.ts` (no `headers()` block)

**Kya galat hai (live-verified):**
Vercel **does** set `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload` (good — HSTS is covered). But the app sets **none** of: `X-Frame-Options`/CSP `frame-ancestors` (→ clickj­acking possible, CWE-1021), enforced `Content-Security-Policy` (no CSP header at all on the API/pages I checked), `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy`. The app renders external/user-influenced content (MCP server `description`, `name`, `owner`, `repo` scraped from GitHub). React escapes by default (good — no XSS found), but these headers are the missing second layer.

**FIX (add to `next.config.ts` — HSTS already set by Vercel, listed for completeness):**
```ts
const securityHeaders = [
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'X-Frame-Options', value: 'DENY' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
  { key: 'Content-Security-Policy',
    value: "default-src 'self'; img-src 'self' https://avatars.githubusercontent.com https://raw.githubusercontent.com https://github.com data:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'" },
]

const nextConfig: NextConfig = {
  // ...existing...
  async headers() {
    return [{ source: '/:path*', headers: securityHeaders }]
  },
}
```
Tune the CSP `script-src` to drop `'unsafe-inline'` if the build allows (Next 16 supports nonces). Start enforcing, watch for breakage.
- **Hand-off:** `frontend-engineer-agent` / `devops-sre-agent`.

---

## 6. MEDIUM — `/api/digest/subscribe` weak validation + no rate-limit (CWE-20 / OWASP API4)

**File:** `src/app/api/digest/subscribe/route.ts:21`

**Kya galat hai:**
`if (!email || !email.includes('@'))` is the only check — `"@"` alone passes. It's a stub today (returns 202, stores nothing), so impact is currently low. **But** the comment says it will soon "send welcome via Resend" — once wired, this becomes a **mail-bomb / spam relay** vector: no rate-limit, no real email validation, no confirm-double-opt-in, no abuse protection. An attacker could enumerate-subscribe or use it to send mail to arbitrary addresses (Resend abuse → domain reputation damage).

**FIX (before wiring Resend):**
- Validate with a proper regex or a library; normalize + lowercase.
- Rate-limit per IP and per email.
- Implement **double opt-in** (send a confirmation link; only add to list after click) — standard anti-abuse for newsletters.
- Add a honeypot field or hCaptcha/Turnstile on the form.
- Never reflect the email back unsanitized into any HTML email template (template injection).

---

## 7. LOW — Unguarded `JSON.parse` on DB field → 500 (CWE-248 / CWE-20)

**File:** `src/lib/data.ts:204-207`

```ts
const dimensions = typeof row.score_dimensions === 'string'
  ? (JSON.parse(row.score_dimensions) as ScoreDimension[])   // unguarded
  : row.score_dimensions
```

**Kya galat hai:** If any `servers.score_dimensions` row holds malformed JSON (bad ingest, manual DB edit, poisoned write), `JSON.parse` throws → unhandled → 500 on that server's detail/search path. Not attacker-injectable through the web tier (data comes from the trusted ingest pipeline + DB), so LOW. It's a robustness/availability bug more than a vuln.

**FIX:** Wrap in try/catch, default to `[]` on parse failure, and log the offending slug.

---

## 8. LOW — Verbose error logging (CWE-209 Information Exposure Through Logs)

**File:** `src/lib/data.ts:658, 681` (`console.warn(..., err)`)

**Kya galat hai:** Full error objects from embedding and DB failures are logged. Neon/Gemini errors can include connection details, query fragments, or internal hostnames in Vercel function logs. Low risk (logs aren't public), but minimize.

**FIX:** Log `err instanceof Error ? err.message : 'unknown'` and a short code, not the full object. Never log the query string + embedding together with PII. (You're not handling PII here yet, but the digest-subscribe path will introduce emails — keep them out of logs.)

---

## 9. INFO — `page` param unbounded (deep-offset)

**Files:** `browse/page.tsx:18`, `data.ts:461`. `page` is validated `> 0` but has no ceiling → very large `OFFSET` scans. Cap it (`Math.min(page, 500)`). The `limit` param in `/api/search` is correctly clamped 1–50 (`search/route.ts:41`) — good.

---

## 10. INFO — Things that are CORRECT (verified passes, not findings)

These were specifically checked because they're the usual culprits in this stack — all clean:

- **No SQL injection.** The "raw SQL" path in `browseServers` (`data.ts:424-467`) and `keywordFallback` (`data.ts:614-627`) looks scary (string-built `WHERE`) but **all user values go through positional params** (`$1`, `$2`, `ANY($n::text[])`) via `sqlFn.query(query, params)`. The only string-interpolated piece is `sortClause` (`data.ts:403-410`), which is a **switch with hardcoded literal outputs** — the user's `sort` value never reaches the SQL string, only one of four fixed strings does. Column names in SELECT are static. **No injectable surface found.** The pgvector path (`data.ts:670-679`) builds `vectorLiteral` from a Gemini-returned float array joined with `,` — those are numbers from a trusted API, embedded via tagged-template `${vectorLiteral}::vector` (parameterized by Neon). Not user-controlled. Safe.
- **`.env.local` is NOT in git** and the three secret strings appear **0 times** in full git history (`git log --all -p`). Clean.
- **No XSS sinks.** Zero `dangerouslySetInnerHTML`, `eval`, `innerHTML` in `src/`. All external/scraped content (MCP descriptions etc.) is rendered as React children → auto-escaped. `install-config.tsx` uses `JSON.stringify` for display. Good.
- **No SSRF in the web app.** The web tier never fetches attacker-supplied URLs. The GitHub scraper (`scripts/scrape-github.ts`) hits fixed GitHub API queries with a token — it's an offline ingest script, not reachable from the web, and doesn't fetch arbitrary user URLs. The image `remotePatterns` (`next.config.ts:8-12`) are correctly allowlisted to GitHub hosts.
- **`limit` clamping** in search is correct (1–50).
- **`/api/servers/[slug]`** is a 404 stub — no live data exposure there.

---

## Detection (what to add since rate-limit is the live gap)

**Gemini cost-spike alert (Google Cloud Billing):**
- Set a billing budget alert on the Gemini/Generative Language API at e.g. $5/$10/$25 thresholds → email/Telegram. This is the fastest safety net for Finding #2 even before code rate-limiting lands.

**Vercel log-based alert (KQL-style pseudo for whatever log sink you use):**
```
source=vercel route="/api/search"
| stats count by client_ip, bin(1m)
| where count > 40          // >40 search/min from one IP = abuse
```

**Neon dashboard:** watch compute-hours / active-time graph for anomalous spikes; Neon free tier has a compute budget — set the autosuspend low and watch the metric.

---

## Response Runbook — "Gemini/Neon bill spiking" (most likely real incident)

1. **Detect:** Billing alert fires OR Neon compute graph spikes.
2. **Triage:** Check Vercel function logs for `/api/search` request rate + top IPs. Confirm unique-`q` flood pattern.
3. **Contain (fastest first):**
   - Rotate the Gemini key immediately if exfiltration suspected (stops external abuse).
   - Deploy an emergency Vercel env flag (e.g. `SEARCH_DISABLED=1`) that short-circuits `/api/search` to keyword-only (no Gemini) — the code already has a keyword fallback path (`data.ts:614`); wire a flag to force it.
   - Or add a Vercel Firewall rule to rate-limit/block the offending IPs.
4. **Eradicate:** Ship the Upstash rate-limiter + query cache (Finding #2/#3).
5. **Recover:** Re-enable semantic search; confirm cost returns to baseline.
6. **Postmortem (blameless):** Root cause = unrated paid endpoint shipped to prod. Action items = rate-limit middleware + budget alerts + detail-page de-embedding.

---

## Compliance / framework mapping

- **OWASP API Security Top 10 2023:** API4 (Unrestricted Resource Consumption) — Findings #2, #3, #4, #6.
- **OWASP Top 10 2021:** A05 Misconfiguration (#5), A07 Identification/Auth Failures + secrets (#1).
- **OWASP LLM Top 10 2025:** LLM04 Model DoS (#2, #4), LLM10 adjacent (unauth inference endpoint cost) (#2).
- **CWE:** 798/312 (#1), 770 (#2, #3), 20 (#4, #6, #7), 693 (#5), 209/248 (#7, #8).
- **NIST 800-53 Rev 5:** AC-6 least privilege (#1 Neon role), SC-5 DoS protection (#2/#3), SC-8/SC-28 (#1), SI-11 error handling (#8).

---

## Priority order for Boss (do in this sequence)

1. **Rotate all 3 secrets now** (#1) — the file's own rotation deadline already passed. ~15 min.
2. **Rate-limit `/api/search` + add Gemini billing alert** (#2) — this is the one that actively costs money in prod. ~1–2 hrs with Upstash.
3. **Stop the per-view Gemini call on the server-detail page** (#3) — swap to `getSimilarServers`. ~20 min, big cost cut.
4. **Add security headers** (#5) — ~10 min config.
5. Length-cap `q` (#4), cap `page` (#9), harden subscribe before wiring Resend (#6), guard `JSON.parse` (#7), trim logs (#8).

**Net:** No SQLi, no XSS, no SSRF, no committed secrets — the code-injection hygiene is genuinely solid. The real, live, money-losing exposure is **unrated paid endpoints (Gemini + Neon)** plus **overdue secret rotation**. Fix those two and McpIndex is in good shape.
