"""
Drive Boss's REAL Chrome (his /home/ujjwal/.config/google-chrome profile)
via Chrome DevTools Protocol. Cookies + HackerEarth login persist from his
prior browsing — should be already logged in.

This script assumes Chrome was launched separately with:
  google-chrome --remote-debugging-port=9222 \
    --user-data-dir=/home/ujjwal/.config/google-chrome
"""

from __future__ import annotations

import sys
import time
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

from playwright.sync_api import (
    Page,
    TimeoutError as PlaywrightTimeout,
    sync_playwright,
)

ROOT = Path("/home/ujjwal/Documents/J.A.R.V.I.S.")
ZIP_PATH = ROOT / "data/hackathons/tata-steel-2026/round_1/build_v4/submission_v4.zip"
SHOT_DIR = ROOT / "data/audits/screenshots"
SHOT_DIR.mkdir(parents=True, exist_ok=True)

CDP_URL = "http://127.0.0.1:9222"
CHALLENGE_URL = "https://www.hackerearth.com/community/challenges/competitive/tata-steel-ai-hackathon/"


def stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def snap(page: Page, label: str) -> Path:
    p = SHOT_DIR / f"{stamp()}-cdp-{label}.png"
    try:
        page.screenshot(path=str(p), full_page=False)
        print(f"  shot: {p}")
    except Exception as e:
        print(f"  shot fail ({label}): {e}")
    return p


def wait_for_cdp(timeout_s: int = 15) -> bool:
    print(f"  waiting for CDP at {CDP_URL} ...")
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{CDP_URL}/json/version", timeout=2) as r:
                if r.status == 200:
                    data = r.read().decode()
                    print(f"  CDP up: {data[:140]}")
                    return True
        except Exception:
            pass
        time.sleep(1)
    return False


def main() -> int:
    print(f"=== CDP attach upload  {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    print(f"  zip: {ZIP_PATH}")

    if not wait_for_cdp(20):
        print("  ERROR: CDP not up. Launch Chrome with --remote-debugging-port=9222 first.")
        return 1

    with sync_playwright() as pw:
        print("\n[1] connect to existing Chrome via CDP")
        try:
            browser = pw.chromium.connect_over_cdp(CDP_URL)
        except Exception as e:
            print(f"  attach failed: {e}")
            return 2
        ctxs = browser.contexts
        print(f"  contexts: {len(ctxs)}")
        ctx = ctxs[0] if ctxs else browser.new_context()
        # Find an existing tab or open a new one
        pages = ctx.pages
        print(f"  existing pages: {len(pages)}")
        page = None
        for pg in pages:
            try:
                u = pg.url
                if "hackerearth" in u:
                    print(f"  reusing existing tab: {u}")
                    page = pg
                    break
            except Exception:
                pass
        if page is None:
            page = ctx.new_page()
        page.bring_to_front()

        print("\n[2] navigate to challenge page (reusing Boss's profile cookies)")
        page.goto(CHALLENGE_URL, wait_until="domcontentloaded", timeout=60000)
        try:
            page.wait_for_load_state("networkidle", timeout=12000)
        except PlaywrightTimeout:
            pass
        snap(page, "01-landing")
        print(f"  url:   {page.url}")
        print(f"  title: {page.title()}")

        # Check login signals
        try:
            signin = page.locator("text=/^Sign In$/i").first.is_visible(timeout=600)
        except Exception:
            signin = False
        print(f"  'Sign In' visible: {signin}")

        if signin:
            print("\n  NOT logged in even with Boss's real profile.")
            print("  Boss: please sign in in the open Chrome window.")
            print("  Polling for login state for up to 5 min...")
            deadline = time.time() + 300
            while time.time() < deadline:
                try:
                    if not page.locator("text=/^Sign In$/i").first.is_visible(timeout=400):
                        print("  -> sign in cleared")
                        break
                except Exception:
                    break
                time.sleep(3)

        print("\n[3] click Submit / Submissions tab")
        clicked = False
        for sel in [
            "a:has-text('Submit'):not(:has-text('Submissions'))",
            "a:has-text('Submissions')",
            "a:has-text('Submit')",
            "a[href*='/submit']",
            "a[href*='/machine-learning/']",
        ]:
            try:
                loc = page.locator(sel).first
                if loc.is_visible(timeout=800):
                    txt = (loc.text_content() or "").strip()[:60]
                    href = loc.get_attribute("href") or ""
                    print(f"  click [{sel}] '{txt}' -> {href}")
                    loc.click()
                    try:
                        page.wait_for_load_state("networkidle", timeout=12000)
                    except PlaywrightTimeout:
                        pass
                    clicked = True
                    break
            except Exception:
                continue
        if not clicked:
            print("  no Submit-link auto-found. Polling for file input regardless.")
        snap(page, "02-after-submit-click")

        print("\n[4] poll for file input (60s; Boss can navigate manually)")
        finput = None
        deadline = time.time() + 60
        last = 0.0
        while time.time() < deadline:
            n = page.locator("input[type='file']").count()
            if n >= 1:
                finput = page.locator("input[type='file']").first
                print(f"  file input found ({n})")
                break
            if time.time() - last > 12:
                print(f"  ...no file input yet, {int(deadline - time.time())}s left, url={page.url[:90]}")
                last = time.time()
            time.sleep(3)
        if finput is None:
            print("  no file input. Boss: navigate to submit page manually, then come back here.")
            print("  Browser stays open 4 minutes — drag-drop manually OR I'll keep watching.")
            time.sleep(240)
            browser.close()
            return 3

        print("\n[5] attach the zip")
        try:
            finput.set_input_files(str(ZIP_PATH))
            print(f"  attached: {ZIP_PATH.name}")
        except Exception as e:
            print(f"  attach failed: {e}")
            time.sleep(120)
            browser.close()
            return 4
        time.sleep(2)
        baseline_url = page.url
        snap(page, "03-file-attached")

        print("\n[6] STOP — Boss clicks Submit (Tier-3). Polling 10 min.")
        deadline = time.time() + 600
        ok = False
        last = 0.0
        while time.time() < deadline:
            try:
                if page.url != baseline_url:
                    print(f"  -> url changed: {baseline_url} -> {page.url}")
                    ok = True
                    break
                for needle in ["Submission successful", "submitted successfully", "queued", "submission received"]:
                    if page.locator(f"text=/{needle}/i").count() > 0:
                        print(f"  -> success text: '{needle}'")
                        ok = True
                        break
                if ok:
                    break
            except Exception:
                pass
            if time.time() - last > 25:
                print(f"  ...waiting on submit click, {int(deadline - time.time())}s left")
                last = time.time()
            time.sleep(3)

        snap(page, "04-post-submit" if ok else "04-timeout")
        print(f"\n[7] done. detected={ok}")
        # Do NOT close browser — it's Boss's real Chrome
        return 0 if ok else 5


if __name__ == "__main__":
    sys.exit(main())
