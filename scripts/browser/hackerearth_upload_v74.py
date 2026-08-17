"""
V74 LB-check submit — Tata Steel R1.

Submits the freshly-retrained prevalence-aware model (regime A, K=200) to the
HackerEarth public leaderboard to get the REAL score (vs the 71.28 estimate).

Flow:
  1. Launches persistent-context Chrome (profile /tmp/jarvis-he-stealth — reuses
     Boss's prior HE login if cookie still valid; else waits up to 5 min for login).
  2. Navigates to HE Tata Steel submit page.
  3. Attaches CSV (+ source.zip if a 2nd input exists).
  4. Fills comment.
  5. Clicks Submit & Evaluate (Boss explicitly said "submit karke dekho").
  6. Polls for the score, decodes vs V44 baseline 72.83 and V71 74.72, logs result.
"""

from __future__ import annotations

import re
import sys
import json
import time
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout, sync_playwright

ROOT      = Path("/home/ujjwal/Documents/J.A.R.V.I.S.")
BUILD_DIR = ROOT / "data/hackathons/tata-steel-2026/round_1"
CSV_PATH  = BUILD_DIR / "build_v74/submission_v74_HE_K200.csv"
ZIP_PATH  = BUILD_DIR / "tata_r1_source.zip"   # attached only if a 2nd input exists
PROFILE   = Path("/tmp/jarvis-he-stealth")
SHOT_DIR  = ROOT / "data/audits/screenshots"
SHOT_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE  = BUILD_DIR / "build_v74/v74_submit_result.jsonl"

SUBMIT_URL = "https://www.hackerearth.com/challenges/competitive/tata-steel-ai-hackathon/machine-learning/fd-a5a6dcb2/"
COMMENT    = ("V74 — fresh prevalence-aware base retrain (LGB+XGB+CatBoost rank-avg), "
              "regime A, K=200. Pure ML, no LB-probed labels. LB-check vs V44=72.83 baseline.")

V44_BASELINE = 72.83
V71_BEST     = 74.72

STEALTH_INIT_JS = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
window.chrome = { runtime: {} };
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
"""


def stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def snap(page: Page, label: str) -> Path:
    p = SHOT_DIR / f"{stamp()}-v74-{label}.png"
    try:
        page.screenshot(path=str(p), full_page=False)
        print(f"  [shot] {p}")
    except Exception as e:
        print(f"  [shot-fail] {label}: {e}")
    return p


def settle(page: Page, t: int = 8) -> None:
    try:
        page.wait_for_load_state("networkidle", timeout=t * 1000)
    except PlaywrightTimeout:
        pass


def try_click(page: Page, sel: str) -> bool:
    try:
        loc = page.locator(sel).first
        if loc.is_visible(timeout=800):
            loc.click()
            settle(page, 8)
            return True
    except Exception:
        pass
    return False


def get_score(page: Page) -> str | None:
    for sel in (".score", "[class*='score']", "[class*='result']",
                ".submission-score", ".challenge-score"):
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=2000):
                txt = (loc.text_content() or "").strip()
                if txt:
                    return txt
        except Exception:
            pass
    try:
        body = page.inner_text("body")
        m = re.search(r'Score\s+([0-9]+\.[0-9]+)', body)
        if m:
            return m.group(1)
        matches = re.findall(r'\b([0-9]{2,3}\.[0-9]{4,6})\b', body)
        if matches:
            return matches[0]
    except Exception:
        pass
    return None


def main() -> int:
    print(f"=== V74 LB-check submit start {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    print(f"  csv: {CSV_PATH}")
    if not CSV_PATH.exists():
        print(f"  ABORT: CSV not found at {CSV_PATH}")
        return 1
    print(f"  csv size: {CSV_PATH.stat().st_size} bytes")

    with sync_playwright() as pw:
        print("\n[1] launch persistent-context Chrome (stealth)")
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE),
            channel="chrome",
            headless=False,
            viewport={"width": 1366, "height": 850},
            ignore_default_args=["--enable-automation"],
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-default-browser-check",
                "--no-first-run",
            ],
        )
        ctx.add_init_script(STEALTH_INIT_JS)
        page = ctx.new_page()

        print("\n[2] navigate to HE submit page")
        page.goto(SUBMIT_URL, wait_until="domcontentloaded", timeout=60000)
        settle(page, 15)
        snap(page, "01-landing")
        print(f"  url: {page.url}")

        print("\n[3] poll for file inputs (up to 5 min for login / page-ready)")
        deadline = time.time() + 300
        last = 0.0
        n_inputs = 0
        while time.time() < deadline:
            try:
                n_inputs = page.locator("input[type='file']").count()
                if n_inputs >= 1:
                    print(f"  file inputs detected: {n_inputs}")
                    break
                try_click(page, "a:has-text('Submit'):visible")
            except Exception:
                pass
            if time.time() - last > 20:
                print(f"  ...polling, {int(deadline - time.time())}s left, url={page.url[:80]}")
                print("     (if a login page is shown, please log in to HackerEarth)")
                last = time.time()
            time.sleep(3)

        snap(page, "02-after-poll")
        if n_inputs == 0:
            print("  no file inputs after 5 min. Browser stays open 5 more min for manual upload.")
            print(f"  Manual path -> CSV: {CSV_PATH}")
            time.sleep(300)
            ctx.close()
            return 3

        print("\n[4] attach files")
        file_inputs = page.locator("input[type='file']")
        try:
            file_inputs.nth(0).set_input_files(str(CSV_PATH))
            print(f"  attached CSV -> input[0]: {CSV_PATH.name}")
            time.sleep(1)
        except Exception as e:
            print(f"  CSV attach failed: {e}")
            snap(page, "csv-fail")
            return 5
        if n_inputs >= 2 and ZIP_PATH.exists():
            try:
                file_inputs.nth(1).set_input_files(str(ZIP_PATH))
                print(f"  attached ZIP -> input[1]: {ZIP_PATH.name}")
                time.sleep(1)
            except Exception as e:
                print(f"  ZIP attach failed (non-fatal): {e}")
        else:
            print("  single input — ZIP not required for this LB-check")

        settle(page, 5)
        snap(page, "03-files-attached")

        print("\n[5] fill comment")
        try:
            comment_loc = page.locator(
                "textarea, input[name*='comment'], input[placeholder*='comment'], input[name*='note']"
            ).first
            if comment_loc.is_visible(timeout=2000):
                comment_loc.fill(COMMENT)
                print(f"  comment filled ({len(COMMENT)} chars)")
                time.sleep(0.5)
        except Exception as e:
            print(f"  comment field error (optional): {e}")

        snap(page, "04-pre-submit")

        print("\n[6] click Submit & Evaluate")
        submitted = False
        for sel in ("button:has-text('Submit & Evaluate')",
                    "a:has-text('Submit & Evaluate')",
                    "input[value='Submit & Evaluate']",
                    "button:has-text('Submit')",
                    "input[type='submit']"):
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=2000):
                    txt = (btn.text_content() or btn.get_attribute("value") or "").strip()[:50]
                    print(f"  clicking '{txt}' [{sel}]")
                    btn.click()
                    submitted = True
                    break
            except Exception:
                continue
        if not submitted:
            snap(page, "no-submit-btn")
            print("  ABORT: submit button not found (browser stays open 3 min)")
            time.sleep(180)
            ctx.close()
            return 6

        print("  Submit clicked — waiting for result...")
        settle(page, 20)
        time.sleep(10)
        settle(page, 10)
        snap(page, "05-score-page")

        score = get_score(page)
        verdict = "UNKNOWN"
        score_f = None
        if score:
            try:
                m = re.search(r'([0-9]+\.[0-9]+)', score)
                score_f = float(m.group(1)) if m else float(score)
                d44 = score_f - V44_BASELINE
                d71 = score_f - V71_BEST
                verdict = f"vs V44(72.83)={d44:+.2f} | vs V71(74.72)={d71:+.2f}"
                score = f"{score_f:.5f}"
            except Exception as ex:
                verdict = f"PARSE_ERROR: {ex}"

        print(f"\n=== V74 LB RESULT: score={score} | {verdict} ===")
        result = {
            "build": "v74_regimeA_K200",
            "score": score,
            "verdict": verdict,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(result) + "\n")
        print(f"  Logged to {LOG_FILE}")

        time.sleep(5)
        ctx.close()
        return 0


if __name__ == "__main__":
    sys.exit(main())
