# Workflow: Anti-Detection (Ethical Pacing)

NOT about evading legitimate platform protections. About **behaving humanely** so personal-use automation doesn't trip bot detection and trigger account flags.

## Why this matters

LinkedIn (2026) detection runs on three tiers:
1. **Pattern analysis** — exact same click sequence every time, same timing intervals
2. **Velocity monitoring** — apply rate, connection rate, message rate
3. **Behavioral fingerprinting** — browser fingerprint, mouse paths, typing cadence

You will **never** fully defeat tier 3 without crossing ethical lines (paid services, residential proxies, fingerprint spoofing). The goal is: **stay below detection thresholds** by behaving close to how Boss would actually behave if doing this manually.

## Daily caps (research-confirmed, May 2026)

| Platform | Apply cap | Connection cap | Message cap |
|---|---|---|---|
| LinkedIn | 15-25 / day | 15-20 / day | 25 / day |
| Naukri | 30-50 / day | N/A | N/A |
| Indeed | 20-30 / day | N/A | N/A |

**Jarvis's hard cap: 25 applies/day per platform, 50 across all platforms.** Tracked in `data/audits/daily-counts.json`.

## Per-action jitter

```python
import asyncio, random

async def human_delay(min_s=2.5, max_s=7.0):
    """Sleep a random duration between actions."""
    await asyncio.sleep(random.uniform(min_s, max_s))

async def typing_delay():
    """Per-character delay when type_text is used."""
    await asyncio.sleep(random.uniform(0.05, 0.18))
```

**Where to apply:**
- Between every navigate / click / submit: `human_delay(2.5, 7.0)` (LinkedIn-friendly)
- Between fields in a form: `human_delay(0.8, 2.5)`
- After page load, before first action: `human_delay(1.5, 4.0)` (let JS settle)
- Per character when using `type_text` (vs `fill_form` batch): `typing_delay()`

`fill_form` (batch) is faster but more "obviously bot." For risk-sensitive forms (final submit pages), prefer per-field `fill` with delays.

## Session warmup (on fresh Chrome profile)

If `data/browser/last-login-{platform}.json` doesn't exist OR is >7 days old:

1. Navigate to platform home (not search)
2. Scroll feed for 30-60 sec (use `evaluate_script` with `window.scrollBy(0, 200)` calls)
3. Click 1-2 articles or posts (read-only, no interaction)
4. Maybe view notifications
5. THEN start the apply session

This builds a non-bot behavioral baseline before any apply actions.

```python
async def session_warmup(platform: str):
    await navigate_page(url=PLATFORM_HOMES[platform])
    await human_delay(3, 8)
    for _ in range(random.randint(3, 6)):
        await evaluate_script(script="window.scrollBy(0, " + str(random.randint(200, 600)) + ")")
        await human_delay(2, 5)
    # Visit one feed item
    snap = await take_snapshot()
    feed_item = find_first_post(snap)
    if feed_item:
        await click(uid=feed_item["uid"])
        await human_delay(5, 12)
        await navigate_page(url=PLATFORM_HOMES[platform])  # back to home
        await human_delay(2, 4)
```

## Time-of-day randomization

DON'T run the apply session at the exact same wall-clock time every day. Add ±45 min randomization to cron triggers. Example crontab entry:

```cron
0 14 * * 1-5    sleep $((RANDOM % 2700)) && /path/to/jarvis-apply --platform linkedin
```

## Browser fingerprint hygiene

Chrome DevTools MCP uses your real Chrome instance with persistent user-data-dir. That's fine — fingerprint matches a real user. **DO NOT:**
- Spoof user-agent (mismatches give you away worse than truthful)
- Use proxy / VPN unless Boss already uses one (mismatch = suspicious)
- Switch between proxies mid-session (huge red flag)

If Boss normally uses a VPN: configure Chrome to use the same VPN endpoint consistently.

## Stop triggers (back off immediately)

If ANY of these happen, **stop the current platform's automation for the day**:

1. CAPTCHA appears (snapshot contains reCAPTCHA / hCaptcha / Cloudflare verify)
2. Account warning banner ("Unusual activity detected", "Verify your account")
3. HTTP 429 in `list_network_requests`
4. Login redirected to "Verify it's you" page
5. Two consecutive form-submit failures with no validation errors (suggests rate-limiting)

On any of these:
- Take screenshot, save to `data/audits/incidents/`
- Log to audit + `data/career/sessions/incidents.jsonl`
- Telegram alert Boss
- Set `data/career/cooldown-{platform}.json` with `until: <next day 11am IST>`
- All future autopilot runs for this platform check this file and refuse to run until expired

## Cool-down enforcement

```python
import json
from pathlib import Path
from datetime import datetime

def is_on_cooldown(platform: str) -> tuple[bool, str | None]:
    path = Path(f"data/career/cooldown-{platform}.json")
    if not path.exists():
        return False, None
    data = json.loads(path.read_text())
    until = datetime.fromisoformat(data["until"])
    if datetime.now() < until:
        return True, data.get("reason")
    return False, None
```

Check at start of every session. If on cooldown, alert Boss + refuse to run.

## When in doubt — stop

Boss's account integrity > apply velocity. Skipping a day is fine. A flagged account is not.
