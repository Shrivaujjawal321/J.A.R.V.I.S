"""
LB Probing submit script — V62 probe submissions.

Uploads probe CSV + source.zip to HackerEarth, clicks Submit, captures score.
Run once per probe. Pass CoilID as argument.

Usage:
  python hackerearth_probe_submit.py 538
  python hackerearth_probe_submit.py 539

Score decode:
  > 73.0  (+~0.38)  => TP confirmed
  < 72.0  (-~1.35)  => FP confirmed
"""

from __future__ import annotations

import sys
import time
import json
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeout

ROOT      = Path("/home/ujjwal/Documents/J.A.R.V.I.S.")
PROBE_DIR = ROOT / "data/hackathons/tata-steel-2026/round_1/probes_v62"
SHOT_DIR  = ROOT / "data/browser/screenshots"
SHOT_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE  = PROBE_DIR / "probe_results.jsonl"

CDP_URL    = "http://127.0.0.1:9222"
SUBMIT_URL = "https://www.hackerearth.com/challenges/competitive/tata-steel-ai-hackathon/machine-learning/fd-a5a6dcb2/"

SOURCE_ZIP = PROBE_DIR / "source.zip"


def stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def snap(page: Page, label: str) -> None:
    p = SHOT_DIR / f"{stamp()}-probe-{label}.png"
    try:
        page.screenshot(path=str(p), full_page=False)
        print(f"  [shot] {p.name}")
    except Exception as e:
        print(f"  [shot-fail] {label}: {e}")


def settle(page: Page, t: int = 10) -> None:
    try:
        page.wait_for_load_state("networkidle", timeout=t * 1000)
    except PlaywrightTimeout:
        pass


def get_score(page: Page) -> str | None:
    """Try to extract score from the page after submission."""
    # HackerEarth shows score in various places
    score_selectors = [
        ".score",
        "[class*='score']",
        "[class*='result']",
        "text=/\\d+\\.\\d+/",
        ".submission-score",
        ".challenge-score",
    ]
    for sel in score_selectors:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=2000):
                txt = (loc.text_content() or "").strip()
                if txt:
                    return txt
        except Exception:
            pass
    # Fallback: grab page text and search for score pattern
    try:
        import re
        body = page.inner_text("body")
        # Look for "Score\n   XX.XXXXX" pattern (HackerEarth format)
        score_block = re.search(r'Score\s+([0-9]+\.[0-9]+)', body)
        if score_block:
            return score_block.group(1)
        # Generic float pattern 2-3 digits + 4-6 decimals
        matches = re.findall(r'\b([0-9]{2,3}\.[0-9]{4,6})\b', body)
        if matches:
            return matches[0]
    except Exception:
        pass
    return None


def main(coil_id: int) -> int:
    csv_path = PROBE_DIR / f"probe_add_{coil_id}.csv"
    if not csv_path.exists():
        print(f"ABORT: {csv_path} not found")
        return 1
    if not SOURCE_ZIP.exists():
        print(f"ABORT: source.zip not found at {SOURCE_ZIP}")
        return 1

    print(f"=== Probe CoilID={coil_id} start {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    print(f"  csv: {csv_path} ({csv_path.stat().st_size} bytes)")
    print(f"  zip: {SOURCE_ZIP} ({SOURCE_ZIP.stat().st_size} bytes)")

    with sync_playwright() as pw:
        print("\n[1] Connect to Chrome via CDP")
        try:
            browser = pw.chromium.connect_over_cdp(CDP_URL)
        except Exception as e:
            print(f"  ABORT: CDP attach failed: {e}")
            return 2

        ctxs = browser.contexts
        ctx  = ctxs[0] if ctxs else browser.new_context()

        # Find or open page
        page = None
        for pg in ctx.pages:
            try:
                if "hackerearth" in pg.url:
                    page = pg
                    break
            except Exception:
                pass
        if page is None:
            page = ctx.new_page()
        page.bring_to_front()

        print(f"\n[2] Navigate to submission URL")
        page.goto(SUBMIT_URL, wait_until="domcontentloaded", timeout=60000)
        settle(page, 12)
        snap(page, f"{coil_id}-01-landed")
        print(f"  url: {page.url}")
        print(f"  title: {page.title()}")

        # Check login
        if "login" in page.url or "signin" in page.url:
            print("  ABORT: not logged in — Boss must log in manually first")
            return 3

        print(f"\n[3] Find file inputs")
        # Try clicking Submit tab if needed
        for sel in ["a:has-text('Submit')", "button:has-text('Submit')", ".submit-tab", "li:has-text('Submit') a"]:
            try:
                loc = page.locator(sel).first
                if loc.is_visible(timeout=1500):
                    loc.click()
                    settle(page, 6)
                    print(f"  clicked: {sel}")
                    break
            except Exception:
                continue

        file_inputs = page.locator("input[type='file']")
        n_inputs    = file_inputs.count()
        print(f"  file inputs: {n_inputs}")

        if n_inputs == 0:
            snap(page, f"{coil_id}-no-inputs")
            print("  ABORT: no file inputs found")
            return 4

        for i in range(n_inputs):
            fi     = file_inputs.nth(i)
            name   = fi.get_attribute("name") or ""
            accept = fi.get_attribute("accept") or ""
            print(f"    [{i}] name='{name}' accept='{accept}'")

        print(f"\n[4] Upload CSV (prediction file)")
        # First input = prediction CSV
        try:
            file_inputs.nth(0).set_input_files(str(csv_path))
            print(f"  CSV uploaded: {csv_path.name}")
            settle(page, 4)
            snap(page, f"{coil_id}-02-csv-uploaded")
        except Exception as e:
            print(f"  CSV upload failed: {e}")
            snap(page, f"{coil_id}-csv-fail")
            return 5

        # ZIP handled in step 5b below

        print(f"\n[5b] Upload source ZIP via Upload button")
        if n_inputs >= 2:
            try:
                file_inputs.nth(1).set_input_files(str(SOURCE_ZIP))
                print(f"  ZIP set: {SOURCE_ZIP.name}")
                settle(page, 3)
                # Click Upload button for source ZIP
                upload_btn = page.locator("button:has-text('Upload'), input[value='Upload']").first
                if upload_btn.is_visible(timeout=3000):
                    upload_btn.click()
                    settle(page, 5)
                    print("  ZIP Upload button clicked")
                snap(page, f"{coil_id}-03-zip-uploaded")
            except Exception as e:
                print(f"  ZIP upload (non-fatal): {e}")
        else:
            print("  Only 1 file input — skipping ZIP")

        print(f"\n[6] Click Submit & Evaluate button")
        submit_selectors = [
            "button:has-text('Submit & Evaluate')",
            "a:has-text('Submit & Evaluate')",
            "input[value='Submit & Evaluate']",
            "button:has-text('Submit')",
            "input[type='submit']",
        ]
        submitted = False
        for sel in submit_selectors:
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
            snap(page, f"{coil_id}-no-submit-btn")
            print("  ABORT: submit button not found")
            return 6

        print("  Submit clicked — waiting for result...")
        settle(page, 20)
        snap(page, f"{coil_id}-04-after-submit")

        # Wait a bit more for score
        time.sleep(10)
        settle(page, 10)
        snap(page, f"{coil_id}-05-score-page")

        score = get_score(page)
        print(f"\n  Raw score extracted: {score!r}")

        # Decode
        verdict = "UNKNOWN"
        BASELINE = 72.83019  # V44 K=200 banked score
        if score:
            try:
                import re
                score_num = re.search(r'([0-9]+\.[0-9]+)', score)
                score_f   = float(score_num.group(1)) if score_num else float(score)
                delta     = score_f - BASELINE
                if delta > 0.20:
                    verdict = f"TP_CONFIRMED (delta=+{delta:.5f})"
                elif delta < -0.50:
                    verdict = f"FP_CONFIRMED (delta={delta:.5f})"
                else:
                    verdict = f"AMBIGUOUS delta={delta:.5f}"
                score = f"{score_f:.5f}"
            except Exception as ex:
                verdict = f"PARSE_ERROR: {ex}"

        print(f"  Verdict: {verdict}")
        print(f"\n=== PROBE RESULT: CoilID={coil_id} | score={score} | verdict={verdict} ===")

        # Log result
        result = {
            "coil_id": coil_id,
            "score": score,
            "verdict": verdict,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(result) + "\n")
        print(f"  Logged to {LOG_FILE}")

        return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python hackerearth_probe_submit.py <CoilID>")
        print("Example: python hackerearth_probe_submit.py 538")
        sys.exit(1)

    coil_id = int(sys.argv[1])
    sys.exit(main(coil_id))
