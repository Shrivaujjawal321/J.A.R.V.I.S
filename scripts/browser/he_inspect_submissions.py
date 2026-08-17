"""Read-only inspect of the HE Tata Steel submissions page via CDP (port 9222).
Dumps any text about offline-evaluation selection, submission count, and the
submissions table, plus a full-page screenshot. Does NOT click or submit."""
from __future__ import annotations
import sys, time, re
from pathlib import Path
sys.stdout.reconfigure(line_buffering=True)
from playwright.sync_api import sync_playwright

ROOT = Path("/home/ujjwal/Documents/J.A.R.V.I.S.")
SHOT = ROOT / "data/audits/screenshots"
SHOT.mkdir(parents=True, exist_ok=True)
CDP = "http://127.0.0.1:9222"
BASE = "https://www.hackerearth.com/challenges/competitive/tata-steel-ai-hackathon/machine-learning/fd-a5a6dcb2/"
CANDIDATES = [
    BASE + "submissions/",
    BASE,
    "https://www.hackerearth.com/challenges/competitive/tata-steel-ai-hackathon/machine-learning/",
]

def main() -> int:
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(CDP, timeout=10000)
        ctx = b.contexts[0] if b.contexts else b.new_context()
        page = ctx.new_page()
        for url in CANDIDATES:
            print(f"\n=== navigate: {url}")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
            except Exception as e:
                print(f"  nav err: {e}"); continue
            try:
                page.wait_for_load_state("networkidle", timeout=12000)
            except Exception:
                pass
            time.sleep(2)
            print(f"  final url: {page.url}")
            ts = time.strftime("%Y%m%d-%H%M%S")
            shot = SHOT / f"{ts}-he-submissions.png"
            try:
                page.screenshot(path=str(shot), full_page=True)
                print(f"  [shot] {shot}")
            except Exception as e:
                print(f"  shot err: {e}")
            try:
                body = page.inner_text("body")
            except Exception:
                body = ""
            # Surface lines mentioning the key concepts
            keys = ("offline", "select", "final", "private", "evaluat", "submission",
                    "remaining", "per day", "limit", "leaderboard", "score")
            seen = set()
            print("  --- relevant lines ---")
            for line in body.splitlines():
                l = line.strip()
                if not l or len(l) > 200:
                    continue
                ll = l.lower()
                if any(k in ll for k in keys) and l not in seen:
                    seen.add(l)
                    print(f"   | {l}")
                if len(seen) > 60:
                    break
            # also report number of submission rows / score figures
            scores = re.findall(r'\b(\d{2,3}\.\d{2,6})\b', body)
            if scores:
                print(f"  --- score-like figures on page: {scores[:15]}")
            if "offline" in body.lower() or "select" in body.lower():
                print("  >>> page mentions offline/select — likely the right page")
                break
        return 0

if __name__ == "__main__":
    sys.exit(main())
