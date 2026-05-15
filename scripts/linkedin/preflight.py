"""
Pre-flight check + auto-recovery for the LinkedIn pipeline's Chrome session.

Run at the top of any pipeline command that needs a logged-in LinkedIn browser
(morning, afternoon batches). On success the rest of the pipeline gets a live
debug-protocol session at http://127.0.0.1:9222 with LinkedIn already logged in.

Recovery ladder:
  1. Port 9222 alive?               → continue.
  2. Dead → auto-launch Chrome with /tmp/chrome-jarvis profile + feed URL.
  3. Wait for port to come up.
  4. Verify LinkedIn session (open feed, check if redirected to /login).
  5. Check li_at cookie expiry → warn if < 7 days remaining.
  6. On any unrecoverable failure → Telegram alert + non-zero exit.

NEVER stores or types LinkedIn passwords — that boundary is Tier-4 per the
auto-mode policy. If the persisted profile lost its session cookie, Boss must
log in manually once; pipeline pauses with a Telegram ping until then.

CLI:
  python -m scripts.linkedin.preflight                 # full preflight
  python -m scripts.linkedin.preflight --check-only    # don't launch, just probe
"""
from __future__ import annotations

import argparse
import shutil
import sqlite3
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import httpx

from . import _telegram_notify

CHROME_PORT = 9222
CHROME_PROFILE = Path("/tmp/chrome-jarvis")
CHROME_BIN_CANDIDATES = (
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "brave-browser",
)
LINKEDIN_FEED = "https://www.linkedin.com/feed/"
LOGGED_OUT_MARKERS = ("/login", "/uas/login", "/checkpoint", "/authwall")
COOKIE_WARN_DAYS = 7
LAUNCH_WAIT_S = 25
VERIFY_WAIT_S = 12


@dataclass
class PreflightResult:
    ok: bool
    chrome_launched: bool
    session_status: str          # "logged_in" | "logged_out" | "unknown"
    cookie_days_remaining: Optional[int]
    note: str

    def as_dict(self) -> dict:
        return {
            "ok": self.ok,
            "chrome_launched": self.chrome_launched,
            "session_status": self.session_status,
            "cookie_days_remaining": self.cookie_days_remaining,
            "note": self.note,
        }


def _find_chrome_binary() -> Optional[str]:
    for name in CHROME_BIN_CANDIDATES:
        path = shutil.which(name)
        if path:
            return path
    return None


def _port_alive(port: int = CHROME_PORT, timeout: float = 1.5) -> bool:
    try:
        r = httpx.get(f"http://127.0.0.1:{port}/json/version", timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False


def _wait_for_port(port: int, deadline_s: float) -> bool:
    end = time.monotonic() + deadline_s
    while time.monotonic() < end:
        if _port_alive(port, timeout=1.0):
            return True
        time.sleep(0.8)
    return False


def _launch_chrome() -> tuple[bool, str]:
    binary = _find_chrome_binary()
    if not binary:
        return False, f"No Chrome binary found (tried {', '.join(CHROME_BIN_CANDIDATES)})"

    CHROME_PROFILE.mkdir(parents=True, exist_ok=True)

    cmd = [
        binary,
        f"--remote-debugging-port={CHROME_PORT}",
        f"--user-data-dir={CHROME_PROFILE}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-session-crashed-bubble",
        "--disable-features=AutomationControlled",
        LINKEDIN_FEED,
    ]

    try:
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception as e:
        return False, f"Popen failed: {e}"

    if not _wait_for_port(CHROME_PORT, LAUNCH_WAIT_S):
        return False, f"Chrome launched but port {CHROME_PORT} never came up in {LAUNCH_WAIT_S}s"
    return True, f"Chrome launched on port {CHROME_PORT} with profile {CHROME_PROFILE}"


def _list_tabs() -> list[dict]:
    try:
        r = httpx.get(f"http://127.0.0.1:{CHROME_PORT}/json", timeout=3.0)
        if r.status_code != 200:
            return []
        return [t for t in r.json() if t.get("type") == "page"]
    except Exception:
        return []


def _find_or_open_linkedin_tab() -> Optional[dict]:
    tabs = _list_tabs()
    for t in tabs:
        url = t.get("url", "")
        if "linkedin.com" in url:
            return t
    try:
        r = httpx.put(
            f"http://127.0.0.1:{CHROME_PORT}/json/new?{quote(LINKEDIN_FEED, safe=':/')}",
            timeout=5.0,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def _verify_session() -> str:
    """Return 'logged_in', 'logged_out', or 'unknown'."""
    tab = _find_or_open_linkedin_tab()
    if not tab:
        return "unknown"
    end = time.monotonic() + VERIFY_WAIT_S
    last_url = tab.get("url", "")
    while time.monotonic() < end:
        time.sleep(1.2)
        for t in _list_tabs():
            if t.get("id") == tab.get("id"):
                last_url = t.get("url", last_url)
                break
        if last_url and not last_url.startswith(("about:", "chrome://", "data:")):
            if any(m in last_url for m in LOGGED_OUT_MARKERS):
                return "logged_out"
            if "linkedin.com/feed" in last_url or "/in/" in last_url or "/home" in last_url:
                return "logged_in"
    if any(m in last_url for m in LOGGED_OUT_MARKERS):
        return "logged_out"
    if "linkedin.com" in last_url and "login" not in last_url:
        return "logged_in"
    return "unknown"


def _check_li_at_cookie() -> Optional[int]:
    """Read Chrome's Cookies sqlite, return days remaining on li_at, or None."""
    db_path = CHROME_PROFILE / "Default" / "Cookies"
    if not db_path.exists():
        return None
    tmp = Path(f"/tmp/jarvis-cookies-{int(time.time())}.db")
    try:
        shutil.copy2(db_path, tmp)
        conn = sqlite3.connect(str(tmp))
        cur = conn.execute(
            "SELECT expires_utc FROM cookies "
            "WHERE host_key LIKE '%linkedin.com' AND name = 'li_at' "
            "ORDER BY expires_utc DESC LIMIT 1"
        )
        row = cur.fetchone()
        conn.close()
    except Exception:
        return None
    finally:
        tmp.unlink(missing_ok=True)
    if not row or not row[0]:
        return None
    # Chrome stores expires_utc as microseconds since 1601-01-01 UTC.
    webkit_epoch = datetime(1601, 1, 1, tzinfo=timezone.utc)
    try:
        expires = webkit_epoch + timedelta(microseconds=int(row[0]))
    except (OverflowError, ValueError):
        return None
    delta = expires - datetime.now(timezone.utc)
    return max(0, delta.days)


def run_preflight(*, check_only: bool = False) -> PreflightResult:
    chrome_launched = False
    note_lines: list[str] = []

    if _port_alive():
        note_lines.append(f"Chrome already alive on port {CHROME_PORT}.")
    else:
        if check_only:
            return PreflightResult(
                ok=False,
                chrome_launched=False,
                session_status="unknown",
                cookie_days_remaining=None,
                note="Port 9222 dead (check-only, did not launch).",
            )
        ok, msg = _launch_chrome()
        note_lines.append(msg)
        if not ok:
            _telegram_notify.safe_send(
                f"🚨 LinkedIn preflight FAILED: {msg}. Pipeline paused.",
                parse_mode=None,
            )
            return PreflightResult(
                ok=False,
                chrome_launched=False,
                session_status="unknown",
                cookie_days_remaining=None,
                note=msg,
            )
        chrome_launched = True

    session = _verify_session()
    note_lines.append(f"Session: {session}.")

    cookie_days = _check_li_at_cookie()
    if cookie_days is None:
        note_lines.append("li_at cookie not found.")
    else:
        note_lines.append(f"li_at expires in {cookie_days}d.")

    if session == "logged_out":
        _telegram_notify.safe_send(
            "🚨 LinkedIn session logged OUT.\n\n"
            f"Chrome is up at port {CHROME_PORT} with profile `/tmp/chrome-jarvis`.\n"
            "Open the browser, sign in to LinkedIn, then rerun:\n"
            "`python -m scripts.linkedin.daily_runner morning`\n\n"
            "Pipeline aborting cleanly — no empty drafts written.",
        )
        return PreflightResult(
            ok=False,
            chrome_launched=chrome_launched,
            session_status=session,
            cookie_days_remaining=cookie_days,
            note=" ".join(note_lines),
        )

    if cookie_days is not None and cookie_days <= COOKIE_WARN_DAYS:
        _telegram_notify.safe_send(
            f"⚠️ LinkedIn li_at cookie expires in {cookie_days} days. "
            "Login refresh soon to avoid pipeline going dark.",
            parse_mode=None,
        )

    if session == "unknown":
        # Don't abort — let the search-agent try; it has its own LinkedIn checks.
        note_lines.append("Session unknown but proceeding (Chrome is up).")

    return PreflightResult(
        ok=True,
        chrome_launched=chrome_launched,
        session_status=session,
        cookie_days_remaining=cookie_days,
        note=" ".join(note_lines),
    )


def main() -> int:
    parser = argparse.ArgumentParser(prog="linkedin.preflight")
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Probe Chrome state without launching anything.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress info prints (errors still go to stderr).",
    )
    args = parser.parse_args()

    result = run_preflight(check_only=args.check_only)
    if not args.quiet:
        import json
        print(json.dumps(result.as_dict(), indent=2))
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
