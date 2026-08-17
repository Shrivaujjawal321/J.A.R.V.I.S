"""
V2 — skip login check entirely. Trust the persistent profile + Boss's word.
Just open browser, navigate, find file input, attach, stop.

Cookies from the prior session (where Boss signed in) survive in the
persistent profile dir.
"""

from __future__ import annotations

import sys
import time
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
PROFILE = Path("/tmp/jarvis-hackerearth-profile")
SHOT_DIR = ROOT / "data/audits/screenshots"
SHOT_DIR.mkdir(parents=True, exist_ok=True)

CHALLENGE_URL = "https://www.hackerearth.com/community/challenges/competitive/tata-steel-ai-hackathon/"


def stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def snap(page: Page, label: str) -> Path:
    p = SHOT_DIR / f"{stamp()}-he-{label}.png"
    try:
        page.screenshot(path=str(p), full_page=False)
        print(f"  shot: {p}")
    except Exception as e:
        print(f"  shot fail ({label}): {e}")
    return p


def settle(page: Page, t: int = 8) -> None:
    try:
        page.wait_for_load_state("networkidle", timeout=t * 1000)
    except PlaywrightTimeout:
        pass


def find_file_input(page: Page):
    n = page.locator("input[type='file']").count()
    if n >= 1:
        print(f"  file input found ({n})")
        return page.locator("input[type='file']").first
    return None


def try_click(page: Page, sel: str) -> bool:
    try:
        loc = page.locator(sel).first
        if loc.is_visible(timeout=800):
            txt = (loc.text_content() or "").strip()[:60]
            href = loc.get_attribute("href") or ""
            print(f"  click [{sel}] '{txt}' -> {href}")
            loc.click()
            settle(page, 10)
            return True
    except Exception:
        pass
    return False


def main() -> int:
    print(f"=== V2 upload start {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    print(f"  zip: {ZIP_PATH}")
    print(f"  profile: {PROFILE}")

    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE),
            headless=False,
            viewport={"width": 1366, "height": 850},
            args=["--no-default-browser-check", "--no-first-run"],
        )
        page = ctx.new_page()

        print("\n[1] open challenge page (cookies from prior login should persist)")
        page.goto(CHALLENGE_URL, wait_until="domcontentloaded", timeout=60000)
        settle(page, 12)
        snap(page, "01-landing")
        print(f"  current url: {page.url}")
        print(f"  page title:  {page.title()}")

        # List visible tabs/links once so we can see what's there
        print("\n  visible top-level links (sample):")
        try:
            for a in page.locator("a:visible").all()[:60]:
                try:
                    txt = (a.text_content() or "").strip()
                    href = a.get_attribute("href") or ""
                    if txt and ("submit" in txt.lower() or "submission" in txt.lower() or "machine-learning" in href.lower() or "leaderboard" in txt.lower()):
                        print(f"    [{txt[:40]}]  -> {href}")
                except Exception:
                    pass
        except Exception as e:
            print(f"  list err: {e}")

        print("\n[2] try to click Submit / Submissions / ML problem link")
        clicked = False
        for sel in [
            "a:has-text('Submit'):not(:has-text('Submissions'))",
            "a:has-text('Submissions')",
            "a:has-text('Submit')",
            "a[href*='/submit']",
            "a[href*='/machine-learning/']",
        ]:
            if try_click(page, sel):
                clicked = True
                break
        if not clicked:
            print("  no Submit tab matched. Poll for file input on whatever page we're on.")
        snap(page, "02-after-submit-click")
        print(f"  current url: {page.url}")

        print("\n[3] poll for file input (up to 60s; Boss can navigate manually)")
        finput = None
        deadline = time.time() + 60
        last = 0.0
        while time.time() < deadline:
            finput = find_file_input(page)
            if finput is not None:
                break
            if time.time() - last > 12:
                print(f"  ...no file input yet, {int(deadline - time.time())}s left, url={page.url}")
                last = time.time()
            time.sleep(3)
        if finput is None:
            print("  no file input after 60s. Browser stays open 180s for manual navigation/upload.")
            time.sleep(180)
            ctx.close()
            return 3

        print("\n[4] attach the zip")
        try:
            finput.set_input_files(str(ZIP_PATH))
            print(f"  attached: {ZIP_PATH.name}")
        except Exception as e:
            print(f"  attach failed: {e}")
            time.sleep(120)
            ctx.close()
            return 4
        time.sleep(2)
        baseline_url = page.url
        snap(page, "03-file-attached")

        print("\n[5] STOP — Boss clicks Submit manually (Tier-3).")
        print(f"  watching url '{baseline_url}' for change OR success text (up to 10 min)...")
        deadline = time.time() + 600
        ok = False
        last = 0.0
        while time.time() < deadline:
            try:
                if page.url != baseline_url:
                    print(f"  -> url changed to {page.url}")
                    ok = True
                    break
                for needle in ["Submission successful", "submitted successfully", "queued", "submission received"]:
                    if page.locator(f"text=/{needle}/i").count() > 0:
                        print(f"  -> success text seen: '{needle}'")
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
        print(f"\n[6] done. detected={ok}")
        time.sleep(8)
        ctx.close()
        return 0 if ok else 5


if __name__ == "__main__":
    sys.exit(main())
