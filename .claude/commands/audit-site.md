# /audit-site

**Usage:** `/audit-site <url>` or `/audit-site portfolio` or `/audit-site enginerd`

Runs a full browser-based audit of a site: health check, performance metrics, mobile screenshot, and a structured improvement report. Delegates to `browser-agent`.

---

## Site Aliases

| Alias | Resolves To |
|-------|-------------|
| `portfolio` | https://ujjawal-shrivastav.vercel.app/ |
| `enginerd` | https://enginerd.vercel.app/ |

---

## Workflow

Browser-agent executes these steps in order:

### Step 1 — Health Check
```bash
.venv/bin/python scripts/browser/check_url.py --url <resolved_url>
```
Captures: HTTP status, load time, console errors, failed requests, page size, desktop screenshot.

### Step 2 — Performance Audit (Lite)
```bash
.venv/bin/python scripts/browser/lighthouse_audit.py --url <resolved_url>
```
Captures: FCP, LCP, CLS, TBT proxy, TTFB, resource breakdown by type (JS/CSS/img/font).
Saves: `data/browser/audits/{slug}-{timestamp}.json`

### Step 3 — Mobile Screenshot
```bash
.venv/bin/python scripts/browser/screenshot.py --url <resolved_url> --mobile
```
Captures: Full-page mobile render (390x844, iPhone UA).
Saves: `data/browser/screenshots/{slug}-mobile-{timestamp}.png`

### Step 4 — Synthesis

Browser-agent synthesizes all data into a structured markdown audit report and saves it to:
`data/browser/audits/audit-{slug}-{date}.md`

---

## Output Format

```markdown
# Site Audit: {url}
**Date:** {date}  **Audited by:** browser-agent

## Health
| Check | Result |
|-------|--------|
| HTTP Status | {status} |
| Load Time (networkidle) | {ms}ms |
| Console Errors | {count} |
| Failed Requests | {count} |
| Page Size (transfer) | {kb} KB |

## Performance (Lite — Performance Observer)
| Metric | Value | Threshold | Rating |
|--------|-------|-----------|--------|
| FCP | {ms}ms | <1800ms good | Good/NI/Poor |
| LCP | {ms}ms | <2500ms good | Good/NI/Poor |
| CLS | {val} | <0.1 good | Good/NI/Poor |
| TBT (proxy) | {ms}ms | <200ms good | Good/NI/Poor |
| TTFB | {ms}ms | — | — |

**Note:** Lite audit via Performance Observer. Not real Lighthouse score (0-100).

## Resource Breakdown
| Type | Size (KB) |
|------|-----------|
| JavaScript | {kb} |
| CSS | {kb} |
| Images | {kb} |
| Fonts | {kb} |
| Total | {kb} |

## Mobile vs Desktop
- Desktop screenshot: `{path}`
- Mobile screenshot: `{path}`
- {Observation about responsive layout — any clipping, overflow, tiny text, broken nav?}

## Top 3 Issues
1. **{Issue title}** — {metric or observation} — {why it matters}
2. **{Issue title}** — ...
3. **{Issue title}** — ...

## Top 3 Quick Wins
1. **{Win}** — {estimated impact} — {how to implement}
2. **{Win}** — ...
3. **{Win}** — ...

## Files
- Desktop screenshot: `data/browser/screenshots/check-{slug}-{ts}.png`
- Mobile screenshot: `data/browser/screenshots/{slug}-mobile-{ts}.png`
- Audit JSON: `data/browser/audits/{slug}-{ts}.json`
- This report: `data/browser/audits/audit-{slug}-{date}.md`
```

---

## Notes for Browser-Agent

- Resolve `portfolio` → `https://ujjawal-shrivastav.vercel.app/` and `enginerd` → `https://enginerd.vercel.app/` before running any script.
- Run Steps 1–3 sequentially (each depends on the URL being reachable first).
- If Step 1 returns a non-200 status or fails to load, stop and report — Steps 2–3 will produce garbage data on a broken page.
- Be honest about the lite audit limitation. Don't claim it's a Lighthouse score.
- For Enginerd specifically: Boss already knows it "feels 2023, not 2026" — lean into design/UX observations in the Top 3 Issues section if the visual screenshots support it.
- For portfolio (Three.js site): note in the report that headless audit runs with WebGL disabled, so the 3D canvas won't appear in screenshots. This is expected behavior — the load-time and resource metrics are still valid and represent the non-3D fallback experience.
- Save the final `.md` report to `data/browser/audits/audit-{slug}-{YYYY-MM-DD}.md`.
