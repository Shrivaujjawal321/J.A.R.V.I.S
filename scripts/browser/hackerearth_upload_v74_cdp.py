"""
V74 LB-check submit — via CDP connect to Boss's OWN Chrome (port 9222).

Connects to Boss's already-running, already-logged-in Chrome (no re-login),
opens the HE Tata Steel submit page, attaches the V74 CSV, fills comment,
clicks Submit & Evaluate, captures the real LB score.

Prereq: Boss launched Chrome with  --remote-debugging-port=9222  using his
default (HE-logged-in) profile.
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
# Optional argv override: argv[1]=CSV path, argv[2]=comment, argv[3]=result-log path
_args = sys.argv[1:]
CSV_PATH  = Path(_args[0]) if len(_args) >= 1 else BUILD_DIR / "build_v74/submission_v74_HE_K200.csv"
ZIP_PATH  = BUILD_DIR / "tata_r1_source.zip"
SHOT_DIR  = ROOT / "data/audits/screenshots"
SHOT_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE  = Path(_args[2]) if len(_args) >= 3 else BUILD_DIR / "build_v74/v74_submit_result.jsonl"

CDP_URL    = "http://127.0.0.1:9222"
SUBMIT_URL = "https://www.hackerearth.com/challenges/competitive/tata-steel-ai-hackathon/machine-learning/fd-a5a6dcb2/"
COMMENT    = _args[1] if len(_args) >= 2 else (
              "V74 — fresh prevalence-aware base retrain (LGB+XGB+CatBoost rank-avg), "
              "regime A, K=200. Pure ML, no LB-probed labels. LB-check vs V44=72.83 baseline.")

V44_BASELINE = 72.83
V71_BEST     = 74.72


def stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def snap(page: Page, label: str) -> Path:
    p = SHOT_DIR / f"{stamp()}-v74cdp-{label}.png"
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
    print(f"=== V74 CDP submit start {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    print(f"  csv: {CSV_PATH}")
    if not CSV_PATH.exists():
        print(f"  ABORT: CSV not found at {CSV_PATH}")
        return 1

    with sync_playwright() as pw:
        print("\n[1] connect over CDP to Boss's Chrome (9222)")
        try:
            browser = pw.chromium.connect_over_cdp(CDP_URL, timeout=10000)
        except Exception as e:
            print(f"  ABORT: cannot connect to {CDP_URL} — is Chrome running with --remote-debugging-port=9222 ?")
            print(f"  detail: {e}")
            return 2

        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        page = ctx.new_page()

        print("\n[2] navigate to HE submit page (using Boss's logged-in session)")
        page.goto(SUBMIT_URL, wait_until="domcontentloaded", timeout=60000)
        settle(page, 15)
        snap(page, "01-landing")
        print(f"  url: {page.url}")

        if "login" in page.url.lower() or "/uas" in page.url or "accounts.google" in page.url:
            print("  WARN: looks like NOT logged in to HE in this Chrome profile.")
            print("  Please log in to HackerEarth in this Chrome, then re-run.")
            snap(page, "not-logged-in")
            return 4

        print("\n[3] poll for file inputs (up to 2 min)")
        deadline = time.time() + 120
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
            time.sleep(3)

        snap(page, "02-after-poll")
        if n_inputs == 0:
            print("  no file inputs found. Screenshot saved. Aborting.")
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
            print("  ABORT: submit button not found")
            return 6

        print("  Submit clicked — waiting for result...")
        settle(page, 20)
        time.sleep(10)
        settle(page, 10)
        snap(page, "05-score-page")

        score = get_score(page)
        verdict = "UNKNOWN"
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
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps({
                "build": "v74_regimeA_K200",
                "score": score,
                "verdict": verdict,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            }) + "\n")
        print(f"  Logged to {LOG_FILE}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
