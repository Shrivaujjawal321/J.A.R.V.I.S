# Workflow: Generic Form Fill

Foundational pattern. All platform-specific workflows (LinkedIn, Naukri) build on this.

## Inputs
- Target URL (the form page)
- A `fill_plan` dict mapping logical field names → values, e.g.:
  ```python
  {
    "phone": "+919XX...",
    "email": "boss@example.com",
    "resume_pdf": "data/career/resume-2026-05.pdf",
    "cover_letter": "<generated text>",
    "years_experience": "1",
    "willing_to_relocate": "yes",
  }
  ```
- Optional: `submit_confirm_required: bool` (defaults to True regardless of auto-mode)

## Steps

### 1. Open the page (Tier 1)
```
navigate_page(url=<form_url>)
wait_for(text="<page-identifying string>", timeout_ms=15000)
```

### 2. Scout the form (Tier 1)
```
snap = take_snapshot()
```

Walk the AT to extract every interactable form field:
- `<input>` (text, email, tel, password, file, number, date, checkbox, radio)
- `<select>` (native dropdowns)
- `<textarea>`
- Aria-combobox / role=combobox (autocomplete inputs)
- Aria-listbox / role=listbox (custom dropdowns)

For each, capture: `label` (from `<label for>`, `aria-label`, or nearest visible text), `name`/`id`/`uid` for selector, `required` flag, `type`.

### 3. Map fill_plan → fields (Tier 1, pure logic)
For each entry in `fill_plan`, find the best-match field. Match strategy (in order):
1. Exact label match (case-insensitive)
2. Substring match ("email" matches "Email address")
3. Heuristic by input type (the only `type="email"` → email)
4. If ambiguous: ask Boss which field to use

### 4. Build the fill batch (Tier 1)
Produce a list of `(uid, value)` pairs. For file inputs, use the file path; the skill will use `upload_file`.

### 5. Show plan to Boss + audit log (Tier 2)
Telegram message:
```
📝 Form ready to fill at <URL>
Fields detected: <count>
Will fill: <preview list with masked passwords>
Mode: <current auto-mode>
Proceeding to fill...
```
Write audit log entry:
```
log_action(tier=2, action="form_plan", agent="browser-autopilot", target=<url>, extra={"field_count": N})
```

### 6. Fill the form (Tier 2 — auto in autopilot)
Use `fill_form` for batch where possible. For files, use `upload_file`. For autocomplete combos, use `type_text` then `wait_for` option then `click`.

Add jitter between fields: 200-600ms random sleep (via `wait_for(timeout_ms=...)`).

After fill, write audit log:
```
log_action(tier=2, action="form_fill", agent="browser-autopilot", target=<url>, extra={"filled": <count>})
```

### 7. Pre-submit screenshot (Tier 1)
```
take_screenshot(filePath="data/audits/screenshots/<ts>-pre.png", fullPage=True)
```

### 8. Submit (Tier 3 — ALWAYS CONFIRMS)
This is the irreversible step. Even in `fullauto`, default to confirm unless Boss explicitly named this exact target.

Send to Telegram:
```
✅ Form filled at <URL>
[attached: pre-submit screenshot]
Field summary: <one-line per field, passwords masked>

Submit? Reply: yes / no / edit
```

On `yes`:
```
click(uid=<submit_button_uid>)
wait_for(text="<success-indicator>" OR redirect)
take_screenshot(filePath="data/audits/screenshots/<ts>-post.png", fullPage=True)
log_action(tier=3, action="form_submit", agent="browser-autopilot", target=<url>, reversible=False, extra={...})
```

On `no`: leave page open, report to Boss, end.
On `edit`: ask which field to change, fill again, repeat from step 7.

### 9. Verify outcome (Tier 1)
- Look for success text on response page (e.g., "Application submitted")
- Capture any confirmation number / ID
- Note this in memory via memory-agent

## Output to Boss

```
📋 Form @ <URL>
Status: submitted ✅ / declined ❌ / failed ⚠️
Confirmation: <ID or "no ID provided">
Screenshots: pre = data/audits/screenshots/<ts>-pre.png
             post = data/audits/screenshots/<ts>-post.png
Audit entries: data/audits/<today>.jsonl
```

## Common pitfalls
- **Phantom submit buttons** — page has 2 buttons "Submit". Use aria-label or visible text near the form, not blind selector.
- **Form-validation errors aren't shown** until first submit attempt. If submit fails with validation, re-scout for new red fields and retry once.
- **Hidden honeypot fields** — never fill `display: none` or `visibility: hidden` inputs. These are bot traps.
- **Native vs JS-driven forms** — some forms intercept submit via JS. After click, wait_for either URL change OR success text, not just network idle.
