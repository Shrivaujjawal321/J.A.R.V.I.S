#!/usr/bin/env python3
"""Publish a text post to LinkedIn via CDP to Boss's debug Chrome (9222).
Usage: li_post.py <text_file> [--post]
Without --post: opens composer, types text, screenshots (DRY RUN, does NOT publish).
With --post: also clicks the Post button to publish.
"""
import sys, time, pathlib
from playwright.sync_api import sync_playwright

CDP = "http://127.0.0.1:9222"
SHOT = pathlib.Path("data/audits/screenshots")
SHOT.mkdir(parents=True, exist_ok=True)


def find_btn(pg, labels, exact=False):
    for b in pg.query_selector_all("button"):
        try:
            t = (b.inner_text() or "").strip()
            al = (b.get_attribute("aria-label") or "").strip()
        except Exception:
            t, al = "", ""
        for L in labels:
            if (t == L if exact else L.lower() in t.lower()) or L.lower() in al.lower():
                if b.is_visible():
                    return b
    return None


def main():
    text_file = sys.argv[1]
    do_post = "--post" in sys.argv
    text = pathlib.Path(text_file).read_text().strip()

    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(CDP, timeout=10000)
        ctx = b.contexts[0]
        pg = ctx.pages[0] if ctx.pages else ctx.new_page()
        pg.bring_to_front()

        pg.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=40000)
        time.sleep(4)

        # login check
        if "login" in pg.url or "uas/login" in pg.url:
            print("RESULT NOT_LOGGED_IN url=" + pg.url)
            return

        # open composer — try several robust strategies
        opened = False
        for sel in ["button.share-box-feed-entry__trigger",
                    "button:has-text('Start a post')",
                    "[class*='share-box-feed-entry__trigger']"]:
            try:
                el = pg.query_selector(sel)
                if el and el.is_visible():
                    el.click(); opened = True; break
            except Exception:
                continue
        if not opened:
            try:
                pg.get_by_text("Start a post", exact=False).first.click(timeout=5000)
                opened = True
            except Exception:
                pass
        if not opened:
            start = find_btn(pg, ["Start a post", "Create a post"])
            if start:
                start.click(); opened = True
        if not opened:
            pg.screenshot(path=str(SHOT / "li_post_no_composer.png"))
            print("RESULT NO_COMPOSER_BUTTON (see screenshot)")
            return
        time.sleep(3)

        # find the editor (contenteditable)
        editor = pg.query_selector("div.ql-editor[contenteditable='true']") or \
                 pg.query_selector("[role='textbox'][contenteditable='true']") or \
                 pg.query_selector("div[contenteditable='true']")
        if not editor:
            pg.screenshot(path=str(SHOT / "li_post_no_editor.png"))
            print("RESULT NO_EDITOR (see screenshot)")
            return

        editor.click()
        time.sleep(0.5)
        # type line-by-line preserving blank lines (Shift+Enter avoids submit)
        lines = text.split("\n")
        for i, ln in enumerate(lines):
            if ln:
                pg.keyboard.type(ln, delay=4)
            if i < len(lines) - 1:
                pg.keyboard.press("Shift+Enter")
        time.sleep(1.5)

        pg.screenshot(path=str(SHOT / "li_post_composed.png"))
        print("COMPOSED chars=%d screenshot=%s" % (len(text), SHOT / "li_post_composed.png"))

        if not do_post:
            print("RESULT DRY_RUN (not published). Re-run with --post to publish.")
            return

        # click Post
        post_btn = find_btn(pg, ["Post"], exact=True)
        if not post_btn:
            post_btn = find_btn(pg, ["Post"])
        if not post_btn or not post_btn.is_enabled():
            pg.screenshot(path=str(SHOT / "li_post_no_postbtn.png"))
            print("RESULT POST_BUTTON_NOT_READY (see screenshot)")
            return
        post_btn.click()
        time.sleep(5)
        pg.screenshot(path=str(SHOT / "li_post_published.png"))
        print("RESULT PUBLISHED screenshot=%s" % (SHOT / "li_post_published.png"))


if __name__ == "__main__":
    main()
