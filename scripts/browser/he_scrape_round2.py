#!/usr/bin/env python3
"""
he_scrape_round2.py — Attach to Boss's logged-in Chrome (CDP 9222) and scrape
the FULL Tata Steel AI Hackathon 2026 Round 2 problem statement + microsite.

Assumes Chrome already running with:
  google-chrome --remote-debugging-port=9222 \
    --user-data-dir=/home/ujjwal/.config/google-chrome

Saves:
  data/hackathons/tata-steel-2026/round_2/official_PS/page_text.md
  data/hackathons/tata-steel-2026/round_2/official_PS/*.png (full-page shots)
  data/hackathons/tata-steel-2026/round_2/official_PS/links.txt
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

ROOT = Path("/home/ujjwal/Documents/J.A.R.V.I.S.")
OUT = ROOT / "data/hackathons/tata-steel-2026/round_2/official_PS"
OUT.mkdir(parents=True, exist_ok=True)

CDP_URL = "http://127.0.0.1:9222"
HACK_BASE = "https://www.hackerearth.com/community/challenges/hackathon/ai-hackathon-round-2-agentic-ai-challenge/"


def snap(page, label: str) -> None:
    p = OUT / f"{label}.png"
    try:
        page.screenshot(path=str(p), full_page=True)
        print(f"  shot -> {p.name}")
    except Exception as e:
        print(f"  shot FAILED {label}: {e}")


def dump_text(page, label: str) -> str:
    try:
        txt = page.inner_text("body")
    except Exception as e:
        txt = f"[inner_text failed: {e}]"
    (OUT / f"{label}.txt").write_text(txt, encoding="utf-8")
    print(f"  text -> {label}.txt ({len(txt)} chars)")
    return txt


def collect_links(page, label: str) -> None:
    try:
        hrefs = page.eval_on_selector_all(
            "a[href]", "els => els.map(e => e.textContent.trim() + ' => ' + e.href)"
        )
    except Exception as e:
        hrefs = [f"[link collect failed: {e}]"]
    (OUT / f"{label}_links.txt").write_text("\n".join(hrefs), encoding="utf-8")
    print(f"  links -> {label}_links.txt ({len(hrefs)} links)")


def main() -> int:
    with sync_playwright() as pw:
        try:
            browser = pw.chromium.connect_over_cdp(CDP_URL)
        except Exception as e:
            print(f"CDP attach FAILED: {e}")
            print("Is Chrome running with --remote-debugging-port=9222 ?")
            return 1

        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        page = ctx.new_page()
        page.set_default_timeout(40_000)

        print(f"[1] Opening hackathon base: {HACK_BASE}")
        try:
            page.goto(HACK_BASE, wait_until="domcontentloaded")
        except PWTimeout:
            print("  goto timed out, continuing with whatever loaded")
        time.sleep(4)
        print(f"  title: {page.title()}")
        print(f"  url:   {page.url}")
        snap(page, "01_landing")
        body = dump_text(page, "01_landing")
        collect_links(page, "01_landing")

        # Try to find Round 2 / problem-statement tabs and click through.
        candidate_texts = [
            "Round 2", "Round-2", "Problem", "Problem Statement",
            "Maintenance Wizard", "Agentic", "Overview", "Details",
        ]
        seen = set()
        for ct in candidate_texts:
            try:
                locs = page.get_by_text(ct, exact=False)
                count = locs.count()
            except Exception:
                count = 0
            for i in range(min(count, 3)):
                key = f"{ct}-{i}"
                if key in seen:
                    continue
                seen.add(key)
                try:
                    el = locs.nth(i)
                    el.scroll_into_view_if_needed(timeout=4000)
                    el.click(timeout=4000)
                    time.sleep(3)
                    label = f"tab_{ct.replace(' ', '_')}_{i}"
                    print(f"[+] clicked '{ct}' #{i} -> {page.url}")
                    snap(page, label)
                    dump_text(page, label)
                except Exception as e:
                    print(f"  click '{ct}' #{i} skipped: {e}")

        print("\nDONE. Inspect data/hackathons/tata-steel-2026/round_2/official_PS/")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
