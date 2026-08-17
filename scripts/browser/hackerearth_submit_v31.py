"""
V31 submission script — Boss-authorized full auto-submit.
Uploads solution.csv (prediction) + submission_v31.zip (source).
Clicks Submit button. Captures result.

Direct URL: https://www.hackerearth.com/challenges/competitive/tata-steel-ai-hackathon/machine-learning/fd-a5a6dcb2/
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
BUILD = ROOT / "data/hackathons/tata-steel-2026/round_1/build_v31"
CSV_PATH  = BUILD / "solution.csv"
ZIP_PATH  = BUILD / "submission_v31.zip"
SHOT_DIR  = ROOT / "data/browser/screenshots"
SHOT_DIR.mkdir(parents=True, exist_ok=True)

CDP_URL       = "http://127.0.0.1:9222"
SUBMIT_URL    = "https://www.hackerearth.com/challenges/competitive/tata-steel-ai-hackathon/machine-learning/fd-a5a6dcb2/"
COMMENT       = ("V31: V4 ⊕ AutoGluon best_quality rank-blend at K=170. "
                 "Equal-weight, blend_rank = (v4_rank + ag_rank)/2. "
                 "Spearman corr V4 vs AG: −0.0282. 170 positives flagged.")


def stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def snap(page: Page, label: str) -> Path:
    p = SHOT_DIR / f"{stamp()}-v31-{label}.png"
    try:
        page.screenshot(path=str(p), full_page=False)
        print(f"  [shot] {p}")
    except Exception as e:
        print(f"  [shot-fail] {label}: {e}")
    return p


def settle(page: Page, t: int = 10) -> None:
    try:
        page.wait_for_load_state("networkidle", timeout=t * 1000)
    except PlaywrightTimeout:
        pass


def main() -> int:
    print(f"=== V31 submit start {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    print(f"  csv: {CSV_PATH}")
    print(f"  zip: {ZIP_PATH}")

    # Pre-flight checks
    if not CSV_PATH.exists():
        print(f"  ABORT: csv not found: {CSV_PATH}")
        return 1
    if not ZIP_PATH.exists():
        print(f"  ABORT: zip not found: {ZIP_PATH}")
        return 1
    print(f"  csv size: {CSV_PATH.stat().st_size} bytes")
    print(f"  zip size: {ZIP_PATH.stat().st_size} bytes")

    with sync_playwright() as pw:
        print("\n[1] connect to existing Chrome via CDP")
        try:
            browser = pw.chromium.connect_over_cdp(CDP_URL)
        except Exception as e:
            print(f"  ABORT: CDP attach failed: {e}")
            return 2

        ctxs = browser.contexts
        print(f"  browser contexts: {len(ctxs)}")
        ctx = ctxs[0] if ctxs else browser.new_context()
        pages = ctx.pages
        print(f"  open pages: {len(pages)}")
        for pg in pages:
            try:
                print(f"    - {pg.url[:80]}")
            except Exception:
                pass

        # Find or open a page
        page = None
        for pg in pages:
            try:
                if "hackerearth" in pg.url:
                    page = pg
                    print(f"  reusing HE tab: {pg.url[:80]}")
                    break
            except Exception:
                pass
        if page is None:
            page = ctx.new_page()
            print("  opened new tab")
        page.bring_to_front()

        print(f"\n[2] navigate to submission URL")
        print(f"  -> {SUBMIT_URL}")
        page.goto(SUBMIT_URL, wait_until="domcontentloaded", timeout=60000)
        settle(page, 12)
        snap(page, "01-submit-page")
        print(f"  url:   {page.url}")
        print(f"  title: {page.title()}")

        # Safety check — not a login page
        try:
            signin_visible = page.locator("text=/sign in/i").first.is_visible(timeout=1000)
        except Exception:
            signin_visible = False
        if signin_visible:
            print("  WARNING: 'Sign In' text visible — session may not be active.")
            print("  Checking for logged-in indicators...")
            # HackerEarth shows user avatar or username when logged in
            try:
                avatar = page.locator(".avatar, .user-info, [class*='user'], [class*='profile']").first.is_visible(timeout=2000)
                print(f"  user element visible: {avatar}")
            except Exception:
                pass

        # Check for CAPTCHA
        try:
            captcha = page.locator("iframe[src*='recaptcha'], .g-recaptcha, #cf-challenge-running").count()
            if captcha > 0:
                snap(page, "CAPTCHA-detected")
                print("  ABORT: CAPTCHA detected. Boss must handle manually.")
                return 10
        except Exception:
            pass

        print("\n[3] inspect file inputs on page")
        file_inputs = page.locator("input[type='file']")
        n_inputs = file_inputs.count()
        print(f"  file inputs found: {n_inputs}")
        for i in range(n_inputs):
            try:
                fi = file_inputs.nth(i)
                name = fi.get_attribute("name") or ""
                accept = fi.get_attribute("accept") or ""
                inp_id = fi.get_attribute("id") or ""
                print(f"    [{i}] name='{name}' accept='{accept}' id='{inp_id}'")
            except Exception as e:
                print(f"    [{i}] err: {e}")

        if n_inputs == 0:
            print("  No file inputs found. Trying to locate Submit button first...")
            # Maybe need to click a tab or button to reveal the form
            for sel in [
                "a:has-text('Submit')",
                "button:has-text('Submit')",
                "a[href*='submit']",
                ".submit-tab",
                "li:has-text('Submit') a",
            ]:
                try:
                    loc = page.locator(sel).first
                    if loc.is_visible(timeout=1000):
                        txt = (loc.text_content() or "").strip()[:50]
                        print(f"  clicking '{txt}' [{sel}]")
                        loc.click()
                        settle(page, 8)
                        break
                except Exception:
                    continue
            snap(page, "02-after-tab-click")
            # Re-check file inputs
            file_inputs = page.locator("input[type='file']")
            n_inputs = file_inputs.count()
            print(f"  file inputs after click: {n_inputs}")

        if n_inputs == 0:
            snap(page, "02-no-file-input")
            print("  ABORT: still no file inputs found. Page structure unexpected.")
            print("  URL:", page.url)
            # Print page text for diagnosis
            try:
                txt = page.locator("body").text_content()
                print("  Page text (first 500 chars):", (txt or "")[:500])
            except Exception:
                pass
            time.sleep(60)  # keep open for manual inspection
            return 3

        # Identify which input is for prediction CSV vs source zip
        # HackerEarth typically: first input = prediction file, second = source code
        print("\n[4] attach files")

        # Try by name/accept attribute first
        csv_input = None
        zip_input = None

        for i in range(n_inputs):
            fi = file_inputs.nth(i)
            try:
                name = (fi.get_attribute("name") or "").lower()
                accept = (fi.get_attribute("accept") or "").lower()
                inp_id = (fi.get_attribute("id") or "").lower()
                label = name + accept + inp_id
                if "csv" in label or "predict" in label or "output" in label or "submission" in label:
                    csv_input = fi
                    print(f"  prediction input -> [{i}] (name={fi.get_attribute('name')})")
                elif "zip" in label or "source" in label or "code" in label:
                    zip_input = fi
                    print(f"  source input -> [{i}] (name={fi.get_attribute('name')})")
            except Exception:
                pass

        # Fallback: first = prediction, second = source
        if csv_input is None and n_inputs >= 1:
            csv_input = file_inputs.nth(0)
            print(f"  prediction input -> [0] (fallback)")
        if zip_input is None and n_inputs >= 2:
            zip_input = file_inputs.nth(1)
            print(f"  source input -> [1] (fallback)")

        # Attach CSV
        if csv_input is not None:
            try:
                csv_input.set_input_files(str(CSV_PATH))
                print(f"  attached CSV: {CSV_PATH.name}")
                time.sleep(1)
            except Exception as e:
                print(f"  ABORT: CSV attach failed: {e}")
                snap(page, "csv-attach-fail")
                return 5
        else:
            print("  WARNING: no prediction file input found — skipping CSV upload")

        # Attach ZIP
        if zip_input is not None:
            try:
                zip_input.set_input_files(str(ZIP_PATH))
                print(f"  attached ZIP: {ZIP_PATH.name}")
                time.sleep(1)
            except Exception as e:
                print(f"  WARN: ZIP attach failed (non-fatal if field optional): {e}")
        else:
            print("  INFO: no source file input or only 1 input — ZIP not attached")

        settle(page, 5)
        snap(page, "03-files-attached")

        # Fill comment if there's a textarea
        print("\n[5] fill comment field")
        try:
            comment_sel = "textarea, input[name*='comment'], input[placeholder*='comment'], input[name*='note']"
            comment_loc = page.locator(comment_sel).first
            if comment_loc.is_visible(timeout=2000):
                comment_loc.fill(COMMENT)
                print(f"  comment filled ({len(COMMENT)} chars)")
                time.sleep(0.5)
            else:
                print("  no comment field visible — skipping")
        except Exception as e:
            print(f"  comment field: {e}")

        snap(page, "04-pre-submit-VERIFY")
        print("\n[6] PRE-SUBMIT VERIFICATION")
        print(f"  URL: {page.url}")
        print(f"  Title: {page.title()}")

        # Safety checks before clicking Submit
        # Abort if URL doesn't look like HackerEarth submit page
        if "hackerearth.com" not in page.url:
            print("  ABORT: not on hackerearth.com")
            return 6
        if "tata-steel" not in page.url.lower() and "fd-a5a6dcb2" not in page.url:
            print(f"  ABORT: URL doesn't match Tata Steel challenge: {page.url}")
            return 6

        # Re-verify files are attached
        print("  Verifying file inputs post-attach...")
        for i in range(page.locator("input[type='file']").count()):
            fi = page.locator("input[type='file']").nth(i)
            try:
                val = fi.input_value()
                print(f"    input[{i}] value: '{val}'")
            except Exception:
                pass

        print("\n[7] find and click SUBMIT button")
        submit_clicked = False

        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:has-text('Submit')",
            "button:has-text('SUBMIT')",
            "a:has-text('Submit')",
            "[class*='submit']:has-text('Submit')",
            "button.submit-btn",
            ".submit-button",
        ]

        for sel in submit_selectors:
            try:
                loc = page.locator(sel).first
                if loc.is_visible(timeout=1000):
                    txt = (loc.text_content() or "").strip()[:50]
                    tag = loc.evaluate("el => el.tagName")
                    print(f"  found submit: [{sel}] tag={tag} text='{txt}'")
                    loc.click()
                    print(f"  Submit clicked at {time.strftime('%H:%M:%S')}")
                    submit_clicked = True
                    break
            except Exception:
                continue

        if not submit_clicked:
            print("  ABORT: could not find Submit button")
            snap(page, "05-no-submit-button")
            # Print visible buttons
            try:
                for btn in page.locator("button:visible").all()[:20]:
                    txt = (btn.text_content() or "").strip()
                    print(f"    visible button: '{txt}'")
            except Exception:
                pass
            return 7

        # Wait for response
        print("\n[8] waiting for submission result...")
        settle(page, 15)
        time.sleep(3)
        snap(page, "05-post-submit")

        # Detect success / failure
        final_url = page.url
        print(f"  final url: {final_url}")

        success_needles = [
            "submitted successfully", "submission successful",
            "queued", "submission received", "thank you",
            "your submission", "processing"
        ]
        error_needles = [
            "error", "failed", "invalid", "wrong format",
            "file too large", "not accepted"
        ]

        page_text = ""
        try:
            page_text = (page.locator("body").text_content() or "").lower()
        except Exception:
            pass

        detected_success = any(n in page_text for n in success_needles)
        detected_error   = any(n in page_text for n in error_needles)

        # Also check for submission ID in URL or page
        sub_id = None
        import re
        m = re.search(r'submission[_-]?id[=:/]?\s*(\d+)', page_text, re.IGNORECASE)
        if not m:
            m = re.search(r'/(\d{9,})', final_url)
        if m:
            sub_id = m.group(1)

        print(f"  success text detected: {detected_success}")
        print(f"  error text detected:   {detected_error}")
        print(f"  submission ID guess:   {sub_id}")

        # Full page snapshot
        snap(page, "06-final-state")

        # Print relevant snippet from page for diagnosis
        print("\n  Page text snippet (first 800 chars of body):")
        try:
            full_text = page.locator("body").text_content() or ""
            print(" ", full_text[:800].replace("\n", " | "))
        except Exception as e:
            print(f"  page text error: {e}")

        if detected_error and not detected_success:
            print("\n  RESULT: possible error detected — review screenshots")
            return 8
        elif detected_success:
            print("\n  RESULT: submission successful")
            return 0
        else:
            print("\n  RESULT: unclear — review screenshots manually")
            return 9


if __name__ == "__main__":
    sys.exit(main())
