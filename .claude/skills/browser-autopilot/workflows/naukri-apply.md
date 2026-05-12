# Workflow: Naukri Quick-Apply (India)

Naukri.com is the dominant India job board. Different DOM and flow vs LinkedIn — usually simpler (1-step quick-apply) but messier (irrelevant fields, dated UI).

## Inputs
Same shape as `linkedin-easy-apply.md`:
- `search_query`, `location`, `filters`
- `experience_filter`: "0-1 years" / "1-3 years" (Naukri's discrete ranges)
- `max_apply_count`: default 5/session
- `resume_path`
- `cover_letter_strategy`: usually `"none"` for Naukri (rare to support cover letters)
- `dry_run: bool`

## Steps

### 1. Ensure logged in
Navigate to https://www.naukri.com/. If login page → run `login-flow.md`.

### 2. Open jobs search
```
navigate_page(url="https://www.naukri.com/jobs-in-<location-slug>")
# OR use top search bar:
fill(uid=<search_keyword_field>, value=<search_query>)
fill(uid=<search_location_field>, value=<location>)
fill(uid=<experience_dropdown>, value=<experience_filter>)
click(uid=<search_button>)
wait_for(text="jobs in", timeout_ms=10000)
```

### 3. Apply filters
Naukri's filter sidebar:
- Date posted: Last 7 days
- Salary: optional
- Work experience: already set above
- Industry: Internet / IT-Software (relevant)
- Function: AI/ML / Data Science

Apply, wait for result list reload.

### 4. Iterate results
Loop until `max_apply_count`:

#### 4a. Click result row (Tier 1)
Naukri opens job detail in same-page panel or new tab. Capture: title, company, location, experience required, salary (often "Not Disclosed"), JD.

#### 4b. Relevance check (Tier 1)
Same as LinkedIn — dispatch to `job-hunt-agent` for fit score. Skip if <7.

#### 4c. Click "Apply" button
Naukri has THREE apply button variants:
- **"Apply"** (blue) → opens in-page quick-apply form (the easy path)
- **"Apply on Company Site"** → external redirect; skip these unless explicitly allowed
- **"Apply via WhatsApp"** → don't automate (unusual flow); skip

Only proceed for the in-page "Apply" variant.

#### 4d. Quick-apply form
Naukri's quick-apply is usually:
- Pre-filled fields from profile (name, email, phone, exp, current salary, expected salary)
- Optional "Add a message" textarea (50% of jobs)
- Optional file upload (usually pre-filled with saved resume — verify it's the latest)

Scout form. If fields are pre-filled correctly → minimal work. If empty:
- Read from `data/memory/facts.md` and Boss's Naukri profile
- Fill missing fields via `form-fill.md`

#### 4e. Resume freshness check
Naukri caches resume. If the cached one is older than `resume_path` → upload new one. Otherwise let the cached one stand.

#### 4f. Pre-submit screenshot + Tier-3 confirm
Same protocol as LinkedIn:
```
🎯 Naukri Apply ready
Company: <name>
Role: <title>
Match score: <N>/10
[review screenshot attached]
Submit? yes / no / edit
```

#### 4g. Submit + capture
On `yes`: click Apply submit → wait for confirmation toast / page → screenshot → log to `applications.jsonl`.

#### 4h. Brief dwell
20-60s random wait before next job (Naukri is more forgiving than LinkedIn on rate-limits but be polite).

### 5. Session end
Same summary format as LinkedIn workflow.

## Known gotchas (Naukri-specific)

1. **Pre-filled fields are sometimes STALE.** Naukri pulls from your last-updated profile. If Boss hasn't logged in for months, current_salary / current_company may be wrong. Always read the pre-fill values and confirm they match `data/memory/facts.md`. Update if needed (this is a Tier-2 profile edit — auto in autopilot, audit logged).

2. **"Naukri.com Resume Score" prompt** — pops up randomly. Dismiss (X button) — don't engage.

3. **Walk-in / Interview filter** — Naukri shows walk-in jobs. Boss almost never wants walk-ins. Filter these out at search time via "Job Type: Permanent".

4. **Spammy companies** — Naukri has more low-quality / pyramid-scheme listings than LinkedIn. Maintain `data/career/blocklist.md` (auto-populate from job-hunt-agent's pattern detection: "pay to apply", "training fees", "MLM keywords").

5. **Salary "Not Disclosed" on 60%+ jobs** — don't filter these out; they're often legitimate. Apply anyway, ask in interview.

6. **"Apply" button sometimes opens a survey first** — multi-question modal before the actual form. Treat the survey as part of the form-fill flow.

7. **Email verification reminders** — sometimes a banner prompts to verify email. Dismiss (X) unless it's actually expired (rare).

8. **Mobile-app push** — Naukri pushes "use our app" prompts. Dismiss; we automate web.

## Hard rules

Same as LinkedIn:
- Tier-3 confirm on every submit
- Never misrepresent experience
- Respect `blocklist.md`
- Max 25 applications/day total
- Stop after 3 validation failures

## Output to Boss

Same format as LinkedIn workflow. Tag the platform in audit entries:
```python
extra={"platform": "naukri", "match_score": 8, ...}
```
