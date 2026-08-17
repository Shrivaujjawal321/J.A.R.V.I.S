#!/usr/bin/env python3
"""Robust LinkedIn connect+note via CDP. Pauses autoplay video, targets the real
top-card Connect button by aria-label, handles the invite dialog. Loops over a list.

Reads targets from a JSON file: [{"url": "...", "note": "...", "slug": "..."}]
Usage: li_connect_batch.py targets.json
"""
import sys, json, time
from playwright.sync_api import sync_playwright

CDP = "http://127.0.0.1:9222"
SHOT = "data/audits/screenshots"

def pause_videos(pg):
    try:
        pg.evaluate("() => { document.querySelectorAll('video').forEach(v=>{try{v.pause();v.removeAttribute('autoplay');}catch(e){}}); }")
    except Exception:
        pass

def invite_dialog(pg):
    for d in pg.query_selector_all("div[role='dialog']"):
        try:
            if "invitation" in (d.inner_text() or "").lower():
                return d
        except Exception:
            continue
    return None

def click_aria(pg, must_have):
    """Click first visible button whose aria-label contains all substrings in must_have."""
    for x in pg.query_selector_all("button"):
        try:
            al = (x.get_attribute("aria-label") or "")
            if all(m.lower() in al.lower() for m in must_have) and x.is_visible():
                x.click(); return True
        except Exception:
            continue
    return False

def click_text(scope, labels):
    for x in scope:
        try:
            t = (x.inner_text() or "").strip()
        except Exception:
            t = ""
        if t in labels:
            try:
                x.click(); return True
            except Exception:
                continue
    return False

def connect_one(pg, url, note, slug):
    pg.goto(url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(3.0)
    pause_videos(pg)
    pg.keyboard.press("Escape"); time.sleep(0.4)
    pause_videos(pg)
    h1 = pg.query_selector("h1")
    name = (h1.inner_text().strip()[:40]) if h1 else "?"
    # name parts to disambiguate THIS person's Connect from sidebar people
    parts = [p for p in name.split() if len(p) > 2][:2]

    def click_invite_for_name():
        """Click 'Invite <this person> to connect' — match on their name in aria-label."""
        for x in pg.query_selector_all("button"):
            try:
                al = (x.get_attribute("aria-label") or "")
                if "invite" in al.lower() and "to connect" in al.lower() \
                   and any(p.lower() in al.lower() for p in parts) and x.is_visible():
                    x.click(); return True
            except Exception:
                continue
        return False

    # already pending/connected?
    main_labels = []
    for x in pg.query_selector_all("main button"):
        try:
            t = (x.inner_text() or "").strip()
        except Exception:
            t = ""
        if t and len(t) < 18:
            main_labels.append(t)
    if "Pending" in main_labels:
        return ("ALREADY_PENDING", name)

    # Try direct top-card Connect (name-aware), else open top-card More then Connect.
    ok = click_invite_for_name()
    if not ok:
        # open the FIRST "More" button (top card)
        for x in pg.query_selector_all("main button"):
            try:
                if (x.inner_text() or "").strip() == "More" and x.is_visible():
                    x.click(); break
            except Exception:
                continue
        time.sleep(1.5)
        ok = click_invite_for_name() or click_text(
            pg.query_selector_all("div[role='menu'] *, .artdeco-dropdown__content *"), ["Connect"])
    time.sleep(2.0)
    dlg = invite_dialog(pg)
    if not dlg:
        pg.screenshot(path=f"{SHOT}/li-{slug}-fail.png")
        return ("NO_INVITE_DIALOG", name)
    # add a note
    click_text(dlg.query_selector_all("button"), ["Add a note"]); time.sleep(1.6)
    dlg = invite_dialog(pg)
    ta = dlg.query_selector("textarea") if dlg else None
    if not ta:
        pg.screenshot(path=f"{SHOT}/li-{slug}-fail.png")
        return ("NO_NOTE_BOX", name)
    ta.click(); time.sleep(0.3); ta.type(note, delay=5); time.sleep(0.6)
    dlg = invite_dialog(pg)
    sent = click_text(dlg.query_selector_all("button"), ["Send"]) or click_aria(pg, ["Send invitation"])
    time.sleep(2.2)
    pg.screenshot(path=f"{SHOT}/li-{slug}.png")
    return ("SENT" if sent else "SEND_BTN_NOT_FOUND", name)

def main():
    targets = json.load(open(sys.argv[1]))
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(CDP, timeout=10000)
        ctx = b.contexts[0]
        pg = ctx.pages[0] if ctx.pages else ctx.new_page()
        pg.bring_to_front()
        for t in targets:
            assert len(t["note"]) <= 300, f'{t["slug"]} note {len(t["note"])}'
            try:
                status, name = connect_one(pg, t["url"], t["note"], t["slug"])
            except Exception as e:
                status, name = ("ERROR:" + str(e)[:60], "?")
            print("RESULT", t["slug"], status, "|", name, flush=True)
            time.sleep(4)  # human pacing between requests

if __name__ == "__main__":
    main()
