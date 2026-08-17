"""
Drive a headed Chromium to HackerEarth Tata Steel submission, attach the V4
zip, then STOP. Boss clicks the final Submit button manually (Tier-3 boundary).

This version uses NO interactive stdin — Boss interacts with the visible
browser window directly. The script polls for login state and submission
completion via page state, with generous timeouts.

Flow:
  1. Launch persistent-context Chromium at /tmp/jarvis-hackerearth-profile
  2. Navigate to challenge page
  3. Poll for login (up to 5 min)
  4. Find + click 'Submit' tab/link
  5. Find file input, attach zip, screenshot
  6. Poll for submission completion (URL change / success indicator, 10 min)
  7. Final screenshot, close
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Line-buffered stdout so live tail works under background bash.
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

from playwright.sync_api import (
    Page,
    TimeoutError as PlaywrightTimeout,
    sync_playwright,
)

ROOT = Path("/home/ujjwal/Documents/J.A.R.V.I.S.")
ZIP_PATH = ROOT / "data/hackathons/tata-steel-2026/round_1/build_v4/submission_v4.zip"
PROFILE = Path("/tmp/jarvis-hackerearth-profile")
SHOT_DIR = ROOT / "data/audits/screenshots"

CHALLENGE_URL = "https://www.hackerearth.com/community/challenges/competitive/tata-steel-ai-hackathon/"

LOGIN_TIMEOUT_S = 300       # 5 min for Boss to log in
SUBMIT_TIMEOUT_S = 600      # 10 min for Boss to click Submit

assert ZIP_PATH.exists(), f"submission zip missing: {ZIP_PATH}"
SHOT_DIR.mkdir(parents=True, exist_ok=True)


def stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def snap(page: Page, label: str) -> Path:
    p = SHOT_DIR / f"{stamp()}-hackerearth-{label}.png"
    try:
        page.screenshot(path=str(p), full_page=False)
        print(f"  shot: {p}")
    except Exception as e:
        print(f"  shot FAILED ({label}): {e}")
    return p


def looks_logged_in(page: Page) -> bool:
    # Multiple positive + negative signals; first non-error answer wins.
    try:
        # Negative: visible "Sign In" link/button
        sign_in = page.locator("text=/^Sign In$/i").first
        if sign_in.is_visible(timeout=300):
            return False
    except Exception:
        pass
    try:
        if page.locator("a[href*='/users/']").count() > 0:
            return True
    except Exception:
        pass
    try:
        if page.locator("[class*='avatar'], [class*='profile-pic'], [class*='user-menu']").count() > 0:
            return True
    except Exception:
        pass
    return False


def wait_login(page: Page) -> bool:
    print(f"\n  waiting for login (up to {LOGIN_TIMEOUT_S}s)...")
    deadline = time.time() + LOGIN_TIMEOUT_S
    last_print = 0.0
    while time.time() < deadline:
        if looks_logged_in(page):
            print("  -> login detected")
            return True
        now = time.time()
        if now - last_print > 15:
            remaining = int(deadline - now)
            print(f"  ...still waiting ({remaining}s left)")
            last_print = now
        time.sleep(3)
    return False


def click_submit_tab(page: Page) -> bool:
    candidates = [
        "a:has-text('Submit')",
        "a:has-text('Submissions')",
        "button:has-text('Submit')",
        "a[href*='submit']",
    ]
    for sel in candidates:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=800):
                txt = (loc.text_content() or "").strip()[:60]
                href = loc.get_attribute("href") or ""
                print(f"  click candidate: [{sel}] '{txt}' -> {href}")
                loc.click()
                try:
                    page.wait_for_load_state("networkidle", timeout=15000)
                except PlaywrightTimeout:
                    pass
                return True
        except Exception:
            continue
    return False


def list_visible_links(page: Page, limit: int = 30) -> None:
    print("  visible nav links (top {0}):".format(limit))
    try:
        for a in page.locator("a:visible").all()[:limit]:
            try:
                txt = (a.text_content() or "").strip()[:60]
                href = a.get_attribute("href") or ""
                if txt and href:
                    print(f"    [{txt}]  -> {href}")
            except Exception:
                continue
    except Exception as e:
        print(f"  list error: {e}")


def find_file_input(page: Page):
    n = page.locator("input[type='file']").count()
    print(f"  input[type=file] count: {n}")
    if n >= 1:
        return page.locator("input[type='file']").first
    return None


def wait_submission_done(page: Page, baseline_url: str) -> bool:
    """Poll for indicators that Boss has clicked Submit. Indicators:
       (a) URL changes from the upload page
       (b) DOM text contains 'Submission successful' / 'submitted' / 'queued'
       (c) The attached file picker has been reset (file count drops)"""
    print(f"\n  waiting for Boss to click Submit (up to {SUBMIT_TIMEOUT_S}s)...")
    deadline = time.time() + SUBMIT_TIMEOUT_S
    last_print = 0.0
    while time.time() < deadline:
        try:
            current_url = page.url
            if current_url != baseline_url:
                print(f"  -> URL changed: {baseline_url}  ->  {current_url}")
                return True
            for needle in ["Submission successful", "submitted successfully", "queued for evaluation", "submission received"]:
                if page.locator(f"text=/{needle}/i").count() > 0:
                    print(f"  -> found success indicator: '{needle}'")
                    return True
        except Exception:
            pass
        now = time.time()
        if now - last_print > 20:
            remaining = int(deadline - now)
            print(f"  ...waiting on Submit click ({remaining}s left)")
            last_print = now
        time.sleep(3)
    print("  -> submit-wait timed out")
    return False


def main() -> int:
    print(f"\n=== HackerEarth V4 upload  ({time.strftime('%Y-%m-%d %H:%M:%S')}) ===")
    print(f"  zip: {ZIP_PATH}  ({ZIP_PATH.stat().st_size} bytes)")
    print(f"  profile: {PROFILE}")

    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE),
            headless=False,
            viewport={"width": 1366, "height": 850},
            args=["--no-default-browser-check", "--no-first-run"],
        )
        page = ctx.new_page()

        print("\n[1] navigate to challenge page")
        page.goto(CHALLENGE_URL, wait_until="domcontentloaded", timeout=60000)
        try:
            page.wait_for_load_state("networkidle", timeout=12000)
        except PlaywrightTimeout:
            pass
        snap(page, "01-landing")

        print("\n[2] check login state")
        if looks_logged_in(page):
            print("  already logged in (persistent profile worked)")
        else:
            print("  NOT logged in — Boss please sign in in the open browser window.")
            if not wait_login(page):
                print("  ABORT: login not completed. Browser will stay open for a while so you can finish manually.")
                time.sleep(180)
                ctx.close()
                return 2
            # Re-navigate to challenge page if login flow took us elsewhere
            if "challenges/competitive/tata-steel-ai-hackathon" not in page.url:
                page.goto(CHALLENGE_URL, wait_until="domcontentloaded", timeout=45000)
                try:
                    page.wait_for_load_state("networkidle", timeout=10000)
                except PlaywrightTimeout:
                    pass
            snap(page, "02-logged-in")

        print("\n[3] click Submit tab")
        ok = click_submit_tab(page)
        if not ok:
            print("  could not auto-click Submit tab. Listing visible links for diagnosis:")
            list_visible_links(page, limit=40)
            print("  Boss: please click into the Submit tab manually in the open window. I'll poll for the file input.")
        # Either we clicked it, or Boss will navigate. Either way, poll for file input.
        time.sleep(2)
        snap(page, "03-on-submit-tab")

        print("\n[4] find file input (poll up to 60s while Boss navigates if needed)")
        finput = None
        deadline = time.time() + 60
        while time.time() < deadline:
            finput = find_file_input(page)
            if finput is not None:
                break
            time.sleep(3)
        if finput is None:
            print("  no file input found within 60s. Browser stays open for manual upload (180s).")
            time.sleep(180)
            ctx.close()
            return 3

        print("\n[5] attach the zip")
        try:
            finput.set_input_files(str(ZIP_PATH))
            print(f"  attached: {ZIP_PATH.name}")
        except Exception as e:
            print(f"  attach FAILED: {e}")
            time.sleep(120)
            ctx.close()
            return 4
        time.sleep(2)
        baseline_url = page.url
        snap(page, "04-file-attached")

        print("\n[6] STOP — Boss clicks Submit manually (Tier-3 boundary).")
        print("    Browser window is showing the form with the file attached.")
        print("    I will poll for the URL change / success indicator.")
        ok = wait_submission_done(page, baseline_url)
        snap(page, "05-post-submit" if ok else "05-no-submit-detected")

        if ok:
            print("\n[7] submission detected — final state captured")
        else:
            print("\n[7] submission NOT detected in the polling window.")
            print("    Browser stays open another 60s for safety.")
            time.sleep(60)

        print("\n  closing browser in 5s")
        time.sleep(5)
        ctx.close()
        return 0


if __name__ == "__main__":
    sys.exit(main())
