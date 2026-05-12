# Workflow: LinkedIn Easy Apply

End-to-end: search jobs → filter → for each Easy Apply listing → fill multi-step form → confirm submit → log outcome.

## Inputs
- `search_query`: e.g., "Machine Learning Engineer fresh graduate India"
- `location`: e.g., "Bengaluru" or "Remote"
- `filters`:
  - `easy_apply_only: True` (mandatory — non-Easy Apply requires external redirect, harder to automate cleanly)
  - `date_posted: "past_week"` (default)
  - `experience_level: ["internship", "entry_level"]` (Boss is fresh grad)
- `max_apply_count`: int, default 5 per session (hard cap at 25/day across all platforms — see SKILL.md)
- `resume_path`: path to PDF (default: latest in `data/career/resumes/`)
- `cover_letter_strategy`: `"template"` | `"per-job"` | `"none"`
- `dry_run: bool` — if True, fill but do NOT submit (for testing)

## Steps

### 1. Ensure logged in (Tier 1 → maybe Tier 2)
Navigate to https://www.linkedin.com/feed/. If redirected to login, run `login-flow.md` workflow.

### 2. Open jobs search
```
navigate_page(url="https://www.linkedin.com/jobs/search/")
fill_form([
  {uid: <search_keyword_field>, value: <search_query>},
  {uid: <search_location_field>, value: <location>},
])
press_key("Enter")
wait_for(text="results", timeout_ms=10000)
```

### 3. Apply filters
- Click "Easy Apply" filter chip
- Click "Date posted" → select per filters
- Click "Experience level" → check each desired level
- Click "Show results" / "Apply filters"
- Wait for result list reload

### 4. Iterate the result list
Loop until `max_apply_count` reached OR list exhausted:

#### 4a. Click next job card (Tier 1)
Capture: job title, company, location, posted date, applicant count, JD text (first 2000 chars).

#### 4b. Pre-flight relevance check (Tier 1)
Hand off to `job-hunt-agent` for a quick pass:
> "Boss is a fresh AI/ML grad. Here's the JD: <text>. Score 1-10 for fit. If <7, recommend SKIP."

If SKIP → log in audit with reason, move on.

#### 4c. Click Easy Apply (Tier 1 — opens form, no commitment yet)
```
click(uid=<easy_apply_button>)
wait_for(text="Apply to <Company>", timeout_ms=8000)
```

#### 4d. Multi-step form loop
LinkedIn Easy Apply has 1-4 steps. Detect via "Continue" / "Next" / "Review" / "Submit application" button text. For each step:

i. Scout the form (`take_snapshot`).
ii. Identify fields. Common fields:
   - Phone number (pull from `data/memory/facts.md`)
   - Email (pre-filled, verify)
   - Resume upload (use `resume_path`)
   - Years of experience (numeric — be honest, even if 0)
   - "Are you authorized to work in <country>?" (Yes for India)
   - "Do you require sponsorship?" (depends — read from facts.md)
   - "Salary expectations" (numeric range)
   - Short Q&A (1-2 sentences) — generate via job-hunt-agent if needed
   - Long Q&A / cover letter — use cover_letter_strategy
iii. Generate cover letter if needed (Tier 1):
   - `"template"`: read `data/career/cover-letter-template.md`, substitute {company}, {role}
   - `"per-job"`: dispatch job-hunt-agent with JD + Boss's profile → custom letter
   - `"none"`: skip cover letter fields, fall back if required
iv. Run `form-fill.md` workflow (Tier 2 fill, audit logged)
v. Take pre-step screenshot
vi. Click Next/Continue (if not last step) — Tier 2, auto+audit (each step is not the final submit)
vii. If at last step (button says "Submit application" or "Review"):
   - Take review-page screenshot
   - **STOP for Tier-3 confirm** (see step 5)

#### 4e. Confirm-and-submit (Tier 3)
Telegram message:
```
🎯 LinkedIn Easy Apply ready
Company: <name>
Role: <title>
Location: <loc>
Applicants: <count>
Match score (job-hunt-agent): <N>/10

Review screenshot: [attached]
Cover letter preview: <first 150 chars>...

Submit? yes / no / edit
```

On `yes`: click "Submit application" → capture confirmation → audit log Tier-3.
On `no`: close modal → mark as "deferred" in audit log → move on.
On `edit`: prompt for which field to change.

#### 4f. Capture confirmation (Tier 1)
After submit:
- Take post-submit screenshot
- Look for "Application sent" toast / "Done" page
- Extract any confirmation/reference number (rare on LinkedIn)
- Update `data/career/applications.jsonl` with one line per submission
- Increment daily counter `data/audits/daily-counts.json`

#### 4g. Brief dwell
Random wait 30-90s before next job (human pacing + LinkedIn rate-limit friendliness). Increment session apply count.

### 5. Session end
After hitting `max_apply_count` OR exhausting list:

Send summary to Boss (see SKILL.md "Output format").

Save session metadata to `data/career/sessions/linkedin-{ts}.json`:
- Jobs viewed
- Jobs scored ≥7
- Jobs applied to
- Jobs deferred / skipped
- Daily counter state
- Audit log path

## Confirmed aria-label selectors (May 2026)

Use these as primary discovery hints in `scout_and_fill.py`:

```python
SUBMIT_HINTS_LINKEDIN = [
    "submit application",     # Final apply button — Tier 3 confirm BEFORE clicking
    "review your application",  # Penultimate step, opens summary
    "continue to next step",  # Multi-step "Next"
    "next",                   # Fallback if aria-label differs
]
```

LinkedIn Easy Apply uses these consistently:
- Initial apply button: `button.jobs-apply-button` OR `aria-label contains "Easy Apply"`
- Multi-step Next: `[aria-label="Continue to next step"]`
- Review step: `[aria-label="Review your application"]`
- **Final submit: `[aria-label="Submit application"]`** — this is the Tier-3 gate

Always verify aria-label via `take_snapshot` before clicking. Class names rot; aria-labels are stable.

## Multi-step loop pattern

Step count is NOT known upfront (1-4+ steps). Use a `while True` with these terminators:

```python
for step in range(1, 7):   # hard cap at 6 to avoid infinite loop
    snap = take_snapshot()

    # Check for final submit
    final_btn = find_button_by_aria_label(snap, "Submit application")
    if final_btn:
        # TIER 3 CONFIRM HERE
        if not await confirm_with_boss(snap):
            return "deferred"
        click(uid=final_btn["uid"])
        break

    # Check for review step
    review_btn = find_button_by_aria_label(snap, "Review your application")
    if review_btn:
        click(uid=review_btn["uid"])
        continue

    # Build fill plan for this step + execute
    plan = build_fill_plan(...)
    if not plan.is_executable():
        return "form_mismatch"
    execute_fill(plan)

    # Advance
    next_btn = find_button_by_aria_label(snap, "Continue to next step")
    if not next_btn:
        return "unknown_step"
    click(uid=next_btn["uid"])
else:
    return "too_many_steps"   # >6 iterations — abort
```

## Known gotchas (LinkedIn-specific)

1. **"Add a note to your application" optional textarea** — appears in 30% of jobs as a soft-required field. Has no `required` flag but recruiters expect content. Default: include a 2-sentence note generated from JD + Boss profile.

2. **Resume version dropdown** — LinkedIn shows previously uploaded resumes. Always select "Upload new" + use the freshest `resume_path` from input, unless an existing one is identical (rare).

3. **Salary fields can be range OR single number OR currency-prefixed.** Handle all three. Default Boss's salary expectation from `data/memory/preferences.md` if present.

4. **"Save" vs "Submit application" buttons** look identical on review step. Verify aria-label, not just text. "Save" stores as draft, "Submit" actually applies — only click Submit on Tier-3 confirm.

5. **Profile completion gate** — if Boss's LinkedIn profile is incomplete, some Easy Apply forms refuse to submit. Detect via error "Complete your profile" → STOP + alert Boss.

6. **Rate-limit: ~25-50 applications/day** before LinkedIn flags account. Stay well below — daily cap 25 across all platforms.

7. **"Hard" Easy Apply (4+ steps with custom Q&A)** can take 10-15 min each. Don't speed-fill: take time on Q&A fields, generate quality text via job-hunt-agent.

## Hard rules

- **NEVER apply on Boss's behalf without showing the final review** (Tier 3 confirm is non-negotiable for submits)
- **NEVER apply with auto-generated text that misrepresents experience** (don't say "5 years ML" when Boss is fresh grad)
- **NEVER apply to roles flagged DON'T APPLY** in `data/career/blocklist.md` (companies Boss has ruled out)
- **MAX 25 applications/day total** (across all platforms)
- **STOP after 3 consecutive validation failures** — LinkedIn is rate-limiting; back off
