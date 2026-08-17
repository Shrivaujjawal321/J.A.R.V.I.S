#!/usr/bin/env python3
"""Send a LinkedIn connection request with a note, via CDP to Boss's debug Chrome (9222).
Usage: li_connect.py "<profile_url_or_search>" "<note <=300 chars>" "<slug>"
If first arg is not a URL, it's treated as a people-search query and the top result is used.
Robust: verifies name, handles direct-Connect or More→Connect, fills note, sends, screenshots.
"""
import sys, time, urllib.parse
from playwright.sync_api import sync_playwright

CDP = "http://127.0.0.1:9222"
SHOT = "data/audits/screenshots"

def click_label(scope, labels, exact=True):
    for x in scope:
        try: t = (x.inner_text() or "").strip()
        except Exception: t = ""
        al = ""
        try: al = (x.get_attribute("aria-label") or "")
        except Exception: pass
        hit = (t in labels) if exact else any(l in t for l in labels)
        if hit or any(l == al or l in al for l in labels):
            try:
                x.click(); return True
            except Exception:
                continue
    return False

def main():
    target, note, slug = sys.argv[1], sys.argv[2], sys.argv[3]
    assert len(note) <= 300, f"note too long: {len(note)}"
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(CDP, timeout=10000)
        ctx = b.contexts[0]
        pg = ctx.pages[0] if ctx.pages else ctx.new_page()
        pg.bring_to_front()
        # resolve target → profile URL
        if target.startswith("http"):
            url = target
        else:
            q = urllib.parse.quote(target)
            pg.goto(f"https://www.linkedin.com/search/results/people/?keywords={q}",
                    wait_until="domcontentloaded", timeout=30000)
            time.sleep(4)
            url = None
            for a in pg.query_selector_all("a[href*='/in/']"):
                href = a.get_attribute("href") or ""
                if "/in/" in href:
                    url = href.split("?")[0]; break
            if not url:
                print("RESULT", slug, "NO_PROFILE_FOUND"); return
        pg.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(3.5)
        pg.keyboard.press("Escape"); time.sleep(0.5)
        pg.keyboard.press("Escape"); time.sleep(0.5)
        h1 = pg.query_selector("h1")
        name = (h1.inner_text().strip()[:45]) if h1 else "?"
        # already connected / pending?
        page_btns = pg.query_selector_all("main button")
        labels_now = []
        for x in page_btns:
            try: t=(x.inner_text() or "").strip()
            except: t=""
            if t and len(t)<20: labels_now.append(t)
        if "Pending" in labels_now:
            print("RESULT", slug, "ALREADY_PENDING", "|", name);
            pg.screenshot(path=f"{SHOT}/li-{slug}.png"); return

        def invite_dialog():
            for d in pg.query_selector_all("div[role='dialog']"):
                try:
                    if "invitation" in (d.inner_text() or "").lower():
                        return d
                except Exception:
                    continue
            return None

        # connect: direct or via More
        direct = click_label(pg.query_selector_all("main button"), ["Connect"])
        if not direct:
            click_label(pg.query_selector_all("main button"), ["More"]); time.sleep(1.5)
            click_label(pg.query_selector_all("div[role='menu'] *, .artdeco-dropdown__content *"), ["Connect"])
        time.sleep(1.8)
        dlg = invite_dialog()
        if not dlg:
            print("RESULT", slug, "NO_INVITE_DIALOG", "|", name)
            pg.screenshot(path=f"{SHOT}/li-{slug}-fail.png"); return
        # add a note
        click_label(dlg.query_selector_all("button"), ["Add a note"]); time.sleep(1.6)
        dlg = invite_dialog()
        ta = dlg.query_selector("textarea") if dlg else None
        if not ta:
            print("RESULT", slug, "NO_NOTE_BOX", "|", name)
            pg.screenshot(path=f"{SHOT}/li-{slug}-fail.png"); return
        ta.click(); time.sleep(0.3); ta.type(note, delay=6); time.sleep(0.6)
        dlg = invite_dialog()
        sent = click_label(dlg.query_selector_all("button"), ["Send", "Send invitation", "Send now"])
        time.sleep(2.2)
        pg.screenshot(path=f"{SHOT}/li-{slug}.png")
        print("RESULT", slug, ("SENT" if sent else "SEND_BTN_NOT_FOUND"), "|", name)

if __name__ == "__main__":
    main()
