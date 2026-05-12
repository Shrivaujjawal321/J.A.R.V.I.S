---
name: browser-autopilot
description: Jarvis's flagship browser-automation skill. Drives Chrome via Chrome DevTools MCP to navigate pages, fill forms, submit applications, log into accounts, and audit web flows on Boss's behalf. Replaces per-platform API integrations (LinkedIn, Naukri, etc.) — Jarvis drives the actual browser. SCOUT-THEN-FILL pattern + Tier-3 confirm for any SUBMIT. Use this skill whenever Boss asks Jarvis to do anything on an external website that involves more than reading.
---

# Browser Autopilot — Jarvis's Web-Action Skill

## When to use this skill

Load this skill when Boss asks Jarvis to:
- Apply to jobs on LinkedIn, Naukri, Indeed, AngelList, Wellfound
- Submit forms anywhere (contest entries, contact forms, registration)
- Log into a personal account (managed via stored credentials)
- Scrape data that requires interaction (clicks, scrolls, dropdowns)
- Audit a logged-in dashboard (Stripe, Vercel, AWS console)
- Take screenshots / snapshots of authenticated pages

**Do NOT use this skill for:**
- Public read-only fetches → use `WebFetch` directly (faster, no browser needed)
- Lighthouse / mobile audits without login → use `/audit-site` slash command (existing browser-agent path)
- Headless automation in CI/test → use `playwright-skill` (different tool, different use case)

## Tools this skill uses

This skill drives Chrome via the **Chrome DevTools MCP** server tools (`mcp__chrome-devtools__*`):

**Navigation & pages:**
- `navigate_page` — go to URL
- `new_page` / `close_page` / `select_page` / `list_pages` — tab management
- `resize_page`, `emulate` — viewport / device emulation

**Interaction:**
- `click`, `hover`, `drag` — pointer actions
- `fill`, `fill_form` — input fields (single + batch)
- `type_text`, `press_key` — keyboard
- `upload_file` — file inputs (resume PDF, cover letter doc)
- `handle_dialog` — alerts / confirms / prompts

**Observation:**
- `take_snapshot` — accessibility tree (PREFER for form discovery — survives DOM cosmetic changes)
- `take_screenshot` — visual (use for audit log + when AT is incomplete)
- `evaluate_script` — run JS to inspect / extract
- `list_console_messages`, `list_network_requests` — debugging

**Waits:**
- `wait_for` — wait for element / condition before next action (avoids race conditions)

## The TIER-AWARE workflow

Before ANY action, this skill MUST:

1. **Read the active auto-mode** from `data/config/auto-mode.json` (or default `autopilot`). See `.claude/skills/auto-mode/SKILL.md`.
2. **Classify each action by tier:**
   - Navigate / click info link / scroll / screenshot → Tier 1 (auto)
   - Form **fill** (typing into fields) → Tier 2 (auto + audit log)
   - Form **SUBMIT** (clicking Apply/Submit/Send) → Tier 3 (CONFIRM with Boss even in `autopilot`)
   - Anything destructive (delete account, cancel subscription) → Tier 3 (CONFIRM even in `fullauto` unless explicitly named)
3. **Write audit log** for Tier 2 and Tier 3 via `scripts/audit_logger.py`.

## The SCOUT-THEN-FILL pattern (core protocol)

Don't blindly fill forms. Survive DOM changes and weird field types by scouting first:

### Step 1 — Scout

```
take_snapshot(uid=null)   # accessibility tree of current page
```

Parse the snapshot to extract:
- All form fields (input/select/textarea elements with their labels)
- Field types (text / email / password / file / select / radio / checkbox)
- Required vs optional flags
- Submit button(s) and their labels (do NOT click yet)
- Multi-step form indicator (Next button, step counter)

### Step 2 — Plan

Build a fill plan as JSON:

```json
{
  "form_url": "https://www.linkedin.com/jobs/view/123/apply",
  "step": "1 of 3",
  "fields": [
    {"label": "Phone", "type": "tel", "selector": "input[name='phoneNumber']", "value": "+91..."},
    {"label": "Resume", "type": "file", "selector": "input[type='file']", "value": "data/career/resume-2026-05.pdf"},
    {"label": "Cover letter", "type": "textarea", "selector": "textarea[name='coverLetter']", "value": "<generated>"}
  ],
  "submit_button": {"label": "Next", "selector": "button[aria-label='Continue']"}
}
```

Show this plan to Boss in Telegram BEFORE executing fill (auto in autopilot, but visible).

### Step 3 — Fill (Tier 2, auto in autopilot)

Use `fill_form` (batch) or sequential `fill` calls. Add small jitter (200-600ms) between fields to avoid bot-detection heuristics. For file inputs use `upload_file`.

### Step 4 — Pre-submit screenshot

`take_screenshot()` BEFORE clicking submit. Save to `data/audits/screenshots/{ts}-{slug}-pre.png`. This is the audit trail.

### Step 5 — Submit (Tier 3, CONFIRM)

In `autopilot` mode: post to Telegram —
> "Form filled. Pre-submit screenshot attached. Submit? Reply `yes` to send, `no` to cancel, `edit` to revise."

In `fullauto` mode (only if Boss explicitly said e.g. "apply to this LinkedIn JD"): proceed but still write the full audit log first.

### Step 6 — Confirmation page capture

After submit completes, `take_screenshot()` + `take_snapshot()` of the result page. Save as `-post.png`. Log success/failure to audit log + memory.

## Workflows (consult these for platform-specific patterns)

- `workflows/login-flow.md` — login with credential mgmt + 2FA (TOTP auto via pyotp, SMS pauses)
- `workflows/form-fill.md` — generic form-fill pattern (this skill's bread and butter)
- `workflows/linkedin-easy-apply.md` — LinkedIn Easy Apply with confirmed aria-labels
- `workflows/naukri-apply.md` — Naukri.com quick-apply flow
- `workflows/anti-detection.md` — ethical pacing, daily caps, session warmup, cool-down

## Helper code

- `scripts/browser/scout_and_fill.py` — snapshot parsing + fill plan builder (PASSES self-test)
- `scripts/browser/credentials.py` — secure credential reader (keyring preferred, .env fallback)
- `scripts/audit_logger.py` — audit trail writer

## Credentials — NEVER inline, NEVER in chat

Credentials live in `.env` (gitignored, chmod 600) using the convention:

```
JARVIS_CRED_LINKEDIN_EMAIL=boss@example.com
JARVIS_CRED_LINKEDIN_PASSWORD=...
JARVIS_CRED_NAUKRI_EMAIL=...
JARVIS_CRED_NAUKRI_PASSWORD=...
```

Use `scripts/browser/credentials.py` to read them — that script never echoes the value back, never logs it, and refuses if the variable is missing (prompts Boss to add).

For 2FA: the skill PAUSES, asks Boss via Telegram for the OTP, then continues. Never store OTP secrets.

## Persistent session (skip re-login)

Chrome user-data-dir: `data/browser/profile/` (gitignored). Reuse across sessions. After successful login, cookies persist — next run jumps straight to the action. If a login page appears unexpectedly, run the `login-flow.md` workflow.

## CAPTCHA / anti-bot — ethical handling

Do **not** attempt to defeat CAPTCHA. If you detect one:
1. `take_screenshot()` of the CAPTCHA page
2. Post to Telegram: "CAPTCHA hit at <URL>. Pausing for 5 min. Solve manually in the open Chrome window, then reply `continue` to resume."
3. `wait_for` with long timeout, OR poll a flag file `data/browser/captcha-resolved`
4. On `continue`, snapshot the page and proceed

## Human-like pacing (built in, not optional)

Between actions, add jitter:
- Click → click: 400-900ms random delay
- Fill field → next field: 200-600ms
- Page load → first action: 1.5-3s
- Per-page dwell on info pages (job descriptions): 5-15s
- Daily cap: 25 form submissions per platform per day. Track in `data/audits/daily-counts.json`. Refuse to exceed.

## Failure modes (plan for these)

1. **Resume upload is a drag-drop, not file input.** Detect via accessibility tree role. Fallback: use `evaluate_script` to find the hidden file input under the drop zone.
2. **Cover letter "optional" turns "required" after first error.** After submit-fail, re-scout the form, look for new red-bordered fields, fill them, retry.
3. **Dropdown is autocomplete (not native select).** Type into the visible input, wait for option list, click matching option. Detect via aria-haspopup="listbox".
4. **Multi-step form changes per role.** Don't assume step count. After each Next click, re-scout and re-plan.
5. **Rate-limited / temporary lockout.** Detect via 429 status or "too many attempts" text. Stop the run, write audit, alert Boss, wait 1h+ before retry.

## Audit log every Tier-2+ action

```python
from scripts.audit_logger import log_action
log_action(
    tier=2,
    action="form_fill",
    agent="browser-autopilot",
    target="https://www.linkedin.com/jobs/view/12345/apply",
    extra={"field_count": 8, "form_step": "1/3", "platform": "linkedin"},
)
```

For Tier-3 SUBMIT:
```python
log_action(
    tier=3,
    action="form_submit",
    agent="browser-autopilot",
    target="https://www.linkedin.com/jobs/view/12345/apply",
    reversible=False,
    extra={"confirm_response": "yes", "post_screenshot": "data/audits/screenshots/...-post.png"},
)
```

## Output format (after a session)

Always end a browser-autopilot session with a summary to Boss:

```
✅ LinkedIn Easy Apply session — 2026-05-12 14:32 IST

Applied: 3
- Senior ML Engineer @ Acme    → confirmation #A8x9 (data/audits/screenshots/...)
- Applied ML Scientist @ Bee    → confirmation #B72k
- ML Engineering @ Cee          → form had Q&A step, used cover-letter template

Skipped: 2
- Staff ML @ Dee     — required 8 yrs experience (Boss has 0)
- ML @ Eee           — visa sponsorship not offered, Boss needs it

Errors: 1
- ML @ Fee           — CAPTCHA hit, paused. Resolve at https://...

Today's apply count: 3/25
Audit log: data/audits/2026-05-12.jsonl (3 entries)
```

## Hard rules (Tier 4 — NEVER violate)

- **Never log into an account that isn't Boss's** (no friend's LinkedIn, no client account)
- **Never bypass CAPTCHA / anti-bot via service** (no 2captcha, no anti-captcha)
- **Never automate against Boss's employer's internal tools** without explicit per-session authorization
- **Never use this skill for spam, scraping at scale, or anything violating site ToS** beyond what a personal user would do manually
- **Never store passwords in chat or non-gitignored files** — `.env` chmod 600 only
- **Never share scraped data with external services** — all output stays on Boss's machine
