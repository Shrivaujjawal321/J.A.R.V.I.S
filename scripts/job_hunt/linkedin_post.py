#!/usr/bin/env python3
"""
Post to LinkedIn by driving a debug Chrome over CDP (connect, not launch).
Chrome must already run with --remote-debugging-port=9222 on a dedicated
user-data-dir, with Boss logged into LinkedIn.

Usage:
  python scripts/job_hunt/linkedin_post.py check               # login state + screenshot
  python scripts/job_hunt/linkedin_post.py post <textfile>     # publish the post
"""
import sys
import time
from playwright.sync_api import sync_playwright

SHOTS = "/tmp/jarvis-li-shots"
import os
os.makedirs(SHOTS, exist_ok=True)
CDP = "http://127.0.0.1:9222"


def get_li_page(browser):
    for ctx in browser.contexts:
        for pg in ctx.pages:
            if "linkedin.com" in (pg.url or ""):
                return pg
    # else open one in the first context
    ctx = browser.contexts[0]
    pg = ctx.new_page()
    pg.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
    return pg


def logged_in(pg):
    url = pg.url or ""
    if "login" in url or "/checkpoint" in url or "authwall" in url:
        return False
    # logged-in feed has the share box / nav
    try:
        return pg.locator("button:has-text('Start a post'), [aria-label*='Start a post']").count() > 0 \
            or pg.locator("a[href*='/in/'], img.global-nav__me-photo").count() > 0
    except Exception:
        return False


def cmd_check():
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(CDP)
        pg = get_li_page(b)
        time.sleep(5)
        pg.screenshot(path=f"{SHOTS}/check.png")
        print("URL:", pg.url)
        print("LOGGED_IN:" , logged_in(pg))


def cmd_post(textfile):
    text = open(textfile, encoding="utf-8").read().strip()
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(CDP)
        pg = get_li_page(b)
        pg.bring_to_front()
        if "feed" not in (pg.url or ""):
            pg.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
        time.sleep(5)
        if not logged_in(pg):
            pg.screenshot(path=f"{SHOTS}/not_logged_in.png")
            print("NOT_LOGGED_IN — Boss must log into LinkedIn in the debug Chrome window first.")
            sys.exit(3)
        # open composer
        pg.locator("button:has-text('Start a post'), [aria-label*='Start a post']").first.click()
        time.sleep(4)
        editor = pg.locator("div[role='textbox'], div.ql-editor[contenteditable='true']").first
        editor.wait_for(state="visible", timeout=20000)
        editor.click()
        time.sleep(1)
        editor.type(text, delay=8)
        time.sleep(2)
        pg.screenshot(path=f"{SHOTS}/composed.png")
        # click Post
        post_btn = pg.locator("button.share-actions__primary-action, button:has-text('Post')").last
        post_btn.wait_for(state="visible", timeout=15000)
        post_btn.click()
        time.sleep(6)
        pg.screenshot(path=f"{SHOTS}/posted.png")
        print("POST_CLICKED — check /posted.png + your LinkedIn profile.")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "check":
        cmd_check()
    elif cmd == "post":
        cmd_post(sys.argv[2])
    else:
        print(__doc__); sys.exit(1)
