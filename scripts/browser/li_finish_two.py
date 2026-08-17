#!/usr/bin/env python3
"""Finish Saurabh + Nikunj connects. Click the FIRST main-card Connect (top y),
or open top More then the menu Connect, then add note + send."""
import time
from playwright.sync_api import sync_playwright

CDP="http://127.0.0.1:9222"
TARGETS=[
 ("saurabh","https://www.linkedin.com/in/saurabh-chauhan/",
  "Hi Saurabh — saw you post about self-improving agents + eval loops. Those reflection loops are token-heavy; routing cheap steps to a smaller model cuts cost 40-60% without hurting eval scores. I do this for AI startups. Happy to compare notes / free audit?"),
 ("nikunj","https://www.linkedin.com/in/nikunj-bajaj-10476824/",
  "Hi Nikunj — saw TrueFoundry is hiring for the LLM/agent stack. I build production agent systems (LangGraph, RAG, cost-optimized inference); ran a 90+ agent system of my own. If you take on vetted agent-build help, I would love in. Quick chat?"),
]

def inv(pg):
    for d in pg.query_selector_all("div[role='dialog']"):
        try:
            if "invitation" in (d.inner_text() or "").lower(): return d
        except: pass
    return None

def run(pg, slug, url, note):
    pg.goto(url, wait_until="domcontentloaded", timeout=30000); time.sleep(3.2)
    pg.evaluate("()=>document.querySelectorAll('video').forEach(v=>{try{v.pause()}catch(e){}})")
    pg.keyboard.press("Escape"); time.sleep(0.4)
    # status check
    labs=[ (x.inner_text() or '').strip() for x in pg.query_selector_all("main button") ]
    if "Pending" in labs: print("RESULT",slug,"ALREADY_PENDING"); return
    # 1) primary Connect in top card (y<500, text Connect, aria Invite)
    clicked=False
    for x in pg.query_selector_all("main button"):
        try:
            t=(x.inner_text() or '').strip(); al=(x.get_attribute('aria-label') or '')
            if t=="Connect" and "Invite" in al and x.is_visible():
                box=x.bounding_box()
                if box and box['y']<520:
                    x.click(); clicked=True; break
        except: pass
    # 2) else open the first top-card More, then click menu Connect
    if not clicked:
        for x in pg.query_selector_all("main button"):
            try:
                if (x.inner_text() or '').strip()=="More" and x.is_visible():
                    box=x.bounding_box()
                    if box and box['y']<520:
                        x.click(); break
            except: pass
        time.sleep(1.4)
        for x in pg.query_selector_all("div[role='menu'] *, .artdeco-dropdown__content *"):
            try:
                t=(x.inner_text() or '').strip(); al=(x.get_attribute('aria-label') or '')
                if t=="Connect" or ("Invite" in al and "connect" in al.lower()):
                    x.click(); clicked=True; break
            except: pass
    time.sleep(2)
    dlg=inv(pg)
    if not dlg:
        pg.screenshot(path=f"data/audits/screenshots/li-{slug}-fail2.png")
        print("RESULT",slug,"NO_DIALOG clicked=",clicked); return
    for x in dlg.query_selector_all("button"):
        if (x.inner_text() or '').strip()=="Add a note": x.click(); break
    time.sleep(1.5); dlg=inv(pg)
    ta=dlg.query_selector("textarea") if dlg else None
    if not ta: print("RESULT",slug,"NO_TA"); return
    ta.click(); time.sleep(0.3); ta.type(note, delay=5); time.sleep(0.6)
    dlg=inv(pg); sent=False
    for x in dlg.query_selector_all("button"):
        if (x.inner_text() or '').strip()=="Send" or "Send invitation" in (x.get_attribute('aria-label') or ''):
            x.click(); sent=True; break
    time.sleep(2.2)
    pg.screenshot(path=f"data/audits/screenshots/li-{slug}-ok.png")
    print("RESULT",slug,"SENT" if sent else "NO_SEND")

with sync_playwright() as pw:
    b=pw.chromium.connect_over_cdp(CDP, timeout=10000)
    ctx=b.contexts[0]; pg=ctx.pages[0]; pg.bring_to_front()
    for slug,url,note in TARGETS:
        try: run(pg,slug,url,note)
        except Exception as e: print("RESULT",slug,"ERR",str(e)[:60])
        time.sleep(4)
