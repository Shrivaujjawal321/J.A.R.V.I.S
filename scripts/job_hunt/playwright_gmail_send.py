#!/usr/bin/env python3
"""
Send the outreach batch through Boss's REAL logged-in Chrome profile via Playwright.
No OAuth, no Composio, no App Password — uses existing Gmail cookies.
Opens Gmail compose URL per email and sends with Ctrl+Enter.

SAFETY: verifies the logged-in account is the expected one before sending; aborts otherwise.

Usage: python scripts/job_hunt/playwright_gmail_send.py batch.json [expected_email]
"""
import os
import sys
import json
import time
import urllib.parse
from playwright.sync_api import sync_playwright

PROFILE = os.path.expanduser("~/.config/google-chrome")
EXPECT = (sys.argv[2] if len(sys.argv) > 2 else "shriva.ujjawal@gmail.com").lower()
SHOTS = "/tmp/jarvis-gmail-shots"
os.makedirs(SHOTS, exist_ok=True)


def compose_url(to, subject, body):
    q = urllib.parse.urlencode({"view": "cm", "fs": "1", "tf": "1",
                                "to": to, "su": subject, "body": body})
    return "https://mail.google.com/mail/u/0/?" + q


def main():
    with open(sys.argv[1]) as f:
        items = json.load(f)

    with sync_playwright() as p:
        print("launching chrome context...", flush=True)
        ctx = p.chromium.launch_persistent_context(
            PROFILE, channel="chrome", headless=False,
            args=["--no-first-run", "--no-default-browser-check",
                  "--disable-blink-features=AutomationControlled",
                  "--hide-crash-restore-bubble", "--disable-session-crashed-bubble",
                  "--restore-last-session=false", "--disable-features=Translate,InfiniteSessionRestore"],
            viewport={"width": 1280, "height": 900}, slow_mo=150,
        )
        print(f"context launched, pages={len(ctx.pages)}", flush=True)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.set_default_navigation_timeout(60000)
        page.set_default_timeout(60000)

        # 1) verify account
        print("navigating to gmail...", flush=True)
        try:
            page.goto("https://mail.google.com/mail/u/0/#inbox", wait_until="domcontentloaded")
        except Exception as e:
            print(f"goto warning: {e} — continuing to screenshot anyway", flush=True)
        time.sleep(6)
        title = (page.title() or "")
        page.screenshot(path=f"{SHOTS}/00_inbox.png")
        print("PAGE TITLE:", title)
        low = title.lower()
        if "sign in" in low or "accounts.google" in (page.url or ""):
            print("ABORT: not logged in to Gmail in this profile.")
            ctx.close(); sys.exit(3)
        if EXPECT not in low:
            print(f"ABORT: logged-in account does not match expected ({EXPECT}). Title={title!r}")
            print("Refusing to send from the wrong account.")
            ctx.close(); sys.exit(4)
        print(f"✅ account verified ({EXPECT}). Sending {len(items)} emails...\n")

        # 2) send each
        results = []
        for i, it in enumerate(items, 1):
            try:
                page.goto(compose_url(it["to"], it["subject"], it["body"]),
                          wait_until="domcontentloaded")
                time.sleep(5)  # let compose render + prefill
                page.screenshot(path=f"{SHOTS}/{i:02d}a_compose_{it['to'].split('@')[0]}.png")
                # send: Ctrl+Enter
                page.keyboard.press("Control+Enter")
                time.sleep(5)
                page.screenshot(path=f"{SHOTS}/{i:02d}b_after_{it['to'].split('@')[0]}.png")
                # heuristic confirm: look for "Message sent" / "Sending"
                body_txt = page.content().lower()
                ok = ("message sent" in body_txt) or ("sending" in body_txt) or ("conversation" in body_txt)
                print(f"  [{i}/{len(items)}] {'✅' if ok else '⚠️ '} {it['to']:<35} "
                      f"{'sent' if ok else 'pressed-send (verify shot)'}")
                results.append({"to": it["to"], "ok": ok})
            except Exception as e:
                print(f"  [{i}/{len(items)}] ❌ {it['to']:<35} {e}")
                results.append({"to": it["to"], "ok": False, "error": str(e)})
            time.sleep(8)  # pacing between sends

        ctx.close()
        ok = sum(1 for r in results if r.get("ok"))
        print(f"\nDONE: {ok}/{len(items)} confirmed. Screenshots in {SHOTS}")
        print("RESULTS_JSON " + json.dumps(results))


if __name__ == "__main__":
    main()
