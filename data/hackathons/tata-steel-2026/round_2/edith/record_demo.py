#!/usr/bin/env python3
"""
Records the PS §9(c) screen recording — a scripted ~3-minute walkthrough of THE EDITH
showcasing every judged feature, captured headless via Playwright video.

Usage:  .venv/bin/python record_demo.py            (both servers must be running)
Output: edith/demo/EDITH_demo_recording.webm  (+ .mp4 if ffmpeg present)
"""
import shutil, subprocess, time
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / "demo"
OUT.mkdir(exist_ok=True)
BASE = "http://127.0.0.1:3000"
W, H = 1920, 1080


def pause(pg, s):  # smooth pacing for the viewer
    pg.wait_for_timeout(int(s * 1000))


def safe_click(pg, selector, timeout=4000):
    try:
        pg.click(selector, timeout=timeout)
        return True
    except Exception:
        return False


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": W, "height": H},
            record_video_dir=str(OUT),
            record_video_size={"width": W, "height": H},
        )
        pg = ctx.new_page()

        # ── Scene 1: cockpit opens — health strip + verdict + live graphs ──────
        pg.goto(BASE, wait_until="domcontentloaded", timeout=45000)
        pause(pg, 10)                      # strip populates, graphs start streaming

        # ── Scene 2: the guided verdict on the healthy default asset ───────────
        safe_click(pg, "text=Show technical details")
        pause(pg, 3)
        safe_click(pg, "text=Show technical details")   # collapse again
        pause(pg, 1.5)

        # ── Scene 3: focus the WATCH asset — guided verdict changes ────────────
        safe_click(pg, "text=HSM.F1.GBX01")
        pause(pg, 9)                       # watch verdict + steps + new stream

        # show more steps
        for sel in ["text=/Show \\d+ more/", "text=Show 2 more steps"]:
            if safe_click(pg, sel):
                break
        pause(pg, 3)

        # ── Scene 4: live replay crosses thresholds → alerts fire ──────────────
        pause(pg, 10)                      # let the replay raise WARNING alerts

        # ── Scene 5: Ask EDITH via a proactive chip → PS-format answer ─────────
        clicked = False
        for chip in ["text=What's most likely causing this trend?",
                     "text=Show me the full repair procedure, step by step.",
                     "text=What is the most likely root cause of the current fault?"]:
            if safe_click(pg, chip):
                clicked = True
                break
        if not clicked:
            pg.fill("textarea", "Diagnose this gearbox and give next steps")
            pg.keyboard.press("Enter")
        # wait until the answer actually renders (cached Claude + NLI gate ~10-25s)
        try:
            pg.wait_for_selector("text=How EDITH decided", timeout=60000)
        except Exception:
            pass
        pause(pg, 6)

        # expand a PS section card + the reasoning trace
        safe_click(pg, "text=Recommended Actions")
        pause(pg, 3)
        safe_click(pg, "text=How EDITH decided")
        pause(pg, 5)

        # ── Scene 6: feedback loop ──────────────────────────────────────────────
        safe_click(pg, "text=Yes, correct")
        pause(pg, 3)

        # ── Scene 7: digital logbook ────────────────────────────────────────────
        safe_click(pg, "text=Digital Logbook")
        pause(pg, 4)

        # ── Scene 8: role-based alerts ──────────────────────────────────────────
        safe_click(pg, "text=Manager")
        pause(pg, 3)
        safe_click(pg, "text=Engineer")
        pause(pg, 2)

        # ── Scene 9: report — shareable web view ────────────────────────────────
        if safe_click(pg, "[aria-label=\"Generate maintenance report\"]", timeout=6000):
            try:
                pg.wait_for_url("**/report/**", timeout=30000)
            except Exception:
                pass
            pause(pg, 8)                   # report page renders
            pg.mouse.wheel(0, 900); pause(pg, 4)
            pg.mouse.wheel(0, 900); pause(pg, 4)

        pause(pg, 2)
        video = pg.video
        ctx.close()                        # flushes the video
        browser.close()

        path = Path(video.path())
        final = OUT / "EDITH_demo_recording.webm"
        shutil.move(str(path), final)
        print(f"recorded: {final}  ({final.stat().st_size/1e6:.1f} MB)")

        # optional mp4 for max compatibility
        if shutil.which("ffmpeg"):
            mp4 = OUT / "EDITH_demo_recording.mp4"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final),
                            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23",
                            str(mp4)], check=False)
            if mp4.exists():
                print(f"converted: {mp4}  ({mp4.stat().st_size/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
