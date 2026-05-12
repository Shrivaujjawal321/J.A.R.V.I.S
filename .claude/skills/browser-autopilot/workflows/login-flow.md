# Workflow: Login Flow (with 2FA)

Used as a sub-step inside platform workflows (LinkedIn, Naukri). Most of the time, persistent Chrome profile means login is skipped — this workflow runs only when the platform shows a login page.

## Inputs
- `platform`: e.g. `linkedin`, `naukri`, `github`
- Credentials are pulled via `scripts/browser/credentials.py`:
  - **Preferred (production):** OS keychain via Python `keyring` library
    - `keyring.set_password(f"jarvis-{platform}", "email", "...")`
    - `keyring.set_password(f"jarvis-{platform}", "password", "...")`
    - For TOTP 2FA: `keyring.set_password(f"jarvis-{platform}", "totp_secret", "<base32 secret>")`
  - **Fallback (dev / quick setup):** `.env` (chmod 600)
    - `JARVIS_CRED_{PLATFORM}_EMAIL`, `JARVIS_CRED_{PLATFORM}_PASSWORD`
- Credentials.py prefers keyring when available, falls back to `.env`. Never echoes values.

## Steps

### 1. Detect login page (Tier 1)
After navigation, snapshot and check for:
- Visible password input
- Login / Sign in form with email field
- URL containing `/login`, `/signin`, `/auth`

If absent → already logged in, exit this workflow.

### 2. Fetch credentials (Tier 1)
```python
from scripts.browser.credentials import get_credential
email = get_credential(platform, "email")     # raises if missing
password = get_credential(platform, "password")
```

Credentials are NEVER printed, logged, or sent to Telegram. The helper masks them in any error output (`***@example.com`).

### 3. Fill credentials (Tier 2 — auto + audit)

```
fill(uid=<email_field>, value=<email>)
wait_for(timeout_ms=300)
fill(uid=<password_field>, value=<password>)
```

Audit log entry — value redacted:
```python
log_action(tier=2, action="login_fill", agent="browser-autopilot",
           target=platform, extra={"email_masked": mask(email)})
```

### 4. Submit login (Tier 3 — but auto-confirmed in autopilot for login itself)

Login is reversible (just log out again) and routine, so even though it's a "submit," for the login flow specifically we treat it as Tier-2-with-audit, NOT Tier-3 confirm. Boss doesn't want "are you sure you want to log in?" every time.

```
click(uid=<login_submit_button>)
wait_for(timeout_ms=8000)
```

### 5. Detect outcome (Tier 1)
After submit, snapshot. Check for:
- **Success:** redirected to home/dashboard URL — proceed
- **2FA prompt:** input field for OTP code → goto step 6
- **Wrong credentials:** error message containing "incorrect", "wrong", "invalid" → STOP, alert Boss
- **CAPTCHA:** detected via reCAPTCHA iframe or "verify you're human" text → STOP, alert Boss (see SKILL.md CAPTCHA section)
- **Account locked / suspicious activity:** STOP, alert Boss

### 6. Handle 2FA (auto for TOTP, ask Boss for SMS/email)

**Path A — TOTP (authenticator app):** If Boss has stored a TOTP secret in keyring once (`keyring.set_password("jarvis-linkedin", "totp_secret", "<base32>")`), generate the code programmatically — no Telegram round-trip needed:

```python
import pyotp, keyring
secret = keyring.get_password(f"jarvis-{platform}", "totp_secret")
if secret:
    code = pyotp.TOTP(secret).now()
    # fill + click — fully automated
```

Boss sets this up ONCE per platform (scan QR or paste base32 secret into keyring). After that, 2FA is invisible.

**Path B — SMS / email OTP (no stored secret):** Pause and ask Boss via Telegram:
```
🔐 2FA required on <platform>
Check your SMS / email and reply with the 6-digit code.
(Timeout: 5 min — login attempt will abort after that.)
```

Poll for Boss's reply OR check `data/browser/2fa-{platform}.txt` flag file.

On code received:
```
fill(uid=<otp_field>, value=<code>)
click(uid=<verify_button>)
wait_for(timeout_ms=8000)
```

Re-snapshot, verify success.

**Hard rules:**
- TOTP **secret** in keyring is fine (it generates codes; codes are short-lived).
- Generated codes are **never persisted** — used immediately, then discarded.
- SMS/email codes: only request from Boss; never store; one-use only.

### 7. Save session (Tier 2 — auto + audit)
On successful login:
- Chrome profile already auto-saves cookies (persistent user-data-dir).
- Write a marker: `data/browser/last-login-{platform}.json` with timestamp.
- Audit log: `action="login_success"`.

### 8. Alert on failure
If login fails after retries, post to Telegram with the screenshot of the error page. Do NOT auto-retry more than once — repeated failures trigger account lock.

## Output to Boss

```
🔓 <platform> login
- Status: logged in ✅ / 2FA needed 🔐 / failed ❌
- Session persisted: yes (next run will skip this step)
- Time: <duration>
```

## Hard rules
- **NEVER attempt login on a non-Boss account** (no shared, no friend's, no employer's)
- **NEVER store 2FA codes** beyond the immediate request
- **NEVER bypass 2FA** via alternative auth flows that weren't explicitly set up by Boss
- **MAX 2 login attempts** per session — repeated failures = stop + alert
