#!/usr/bin/env python3
"""
Produces the FINAL Tata-submission screen recording for THE EDITH:
scripted walkthrough + professional VOICEOVER (Piper TTS) + on-screen CAPTIONS
(burned in via an injected HUD caption bar) + .srt subtitles + .mp4 export.

Run with both servers up:  .venv/bin/python make_final_video.py
Outputs in edith/demo/:  EDITH_demo_final.webm  EDITH_demo_final.mp4  EDITH_demo_final.srt
"""
import json, subprocess, time, wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEMO = HERE / "demo"; DEMO.mkdir(exist_ok=True)
AUD = DEMO / "narration"; AUD.mkdir(exist_ok=True)
JROOT = Path("/home/ujjwal/Documents/J.A.R.V.I.S.")
VOICE_ONNX = JROOT / "data" / "voice" / "models" / "en_US-lessac-medium.onnx"
BASE = "http://127.0.0.1:3000"
W, H = 1920, 1080

# ── the storyboard: caption (on-screen) + narration (spoken) + action ─────────
SCENES = [
 dict(id="s01_open", hold=4,
  caption="THE EDITH — agentic maintenance copilot · Tata Steel AI Hackathon R2",
  narration="This is EDITH — an agentic maintenance copilot for a steel plant, built for "
            "the Tata Steel A I Hackathon. Fifteen critical machines stream live sensor "
            "data into one control room."),
 dict(id="s02_verdict", hold=4,
  caption="Plain-language verdict — what's wrong, how urgent, what to do",
  narration="Every machine gets a plain language verdict. This work roll bearing is "
            "healthy — EDITH recommends only routine monitoring, and the technical "
            "details are one click away."),
 dict(id="s03_watch", hold=5,
  caption="Early gear-tooth wear detected — guided steps for the engineer",
  narration="The mill gearbox shows early signs of gear tooth wear. EDITH explains what "
            "is happening, how urgent it is, and exactly what to do next — in the order "
            "an engineer needs it."),
 dict(id="s04_alerts", hold=6,
  caption="Live monitoring — ISO-grounded thresholds · self-explaining alerts",
  narration="As the historian replays a real degradation episode, sensors cross their "
            "I S O grounded thresholds. Each alert explains itself — which sensor, what "
            "value, what limit — in plain words."),
 dict(id="s05_ask", hold=3,
  caption="Ask EDITH — state-aware suggestions",
  narration="The engineer asks EDITH directly. Suggestions are state aware — EDITH "
            "proposes the right question for this machine's current condition."),
 dict(id="s06_answer", hold=6,
  caption="PS-format answer: diagnosis · root cause · RUL · risk · actions — all cited",
  narration="The answer follows the problem statement's format — diagnosis, root cause, "
            "remaining useful life, risk, and prioritized actions. Every claim is cited "
            "to manuals, S O Ps and live sensor models, reasoned by a multi agent "
            "pipeline with Claude."),
 dict(id="s07_trace", hold=5,
  caption='"How EDITH decided" — full multi-agent reasoning trace',
  narration="And it is fully explainable. How EDITH decided opens the agent by agent "
            "reasoning trace — plan, diagnosis, prediction, prioritization, "
            "recommendation, and a faithfulness gate."),
 dict(id="s08_feedback", hold=3,
  caption="Feedback loop — EDITH learns from the engineer",
  narration="The engineer's feedback is learned. Confirmations and corrections adjust "
            "EDITH's future risk weighting."),
 dict(id="s09_logbook", hold=4,
  caption="Automatic per-machine digital logbook",
  narration="Every alert, diagnosis, report and correction is recorded automatically in "
            "a per machine digital logbook."),
 dict(id="s10_roles", hold=4,
  caption="Role-based alert routing — operator / engineer / manager",
  narration="Alerts are routed by role — a manager sees only the serious events, while "
            "operators see everything on their line."),
 dict(id="s11_report", hold=7,
  caption="One-click structured report — shareable link + branded PDF",
  narration="One click produces a structured maintenance report — shareable as a link "
            "and downloadable as a branded P D F."),
 dict(id="s12_close", hold=6,
  caption="Fast · grounded · explainable — THE EDITH",
  narration="EDITH runs fully local, on a self built, physics grounded dataset of one "
            "point two five million sensor readings — fast, grounded, and explainable. "
            "EDITH — maintenance intelligence for the plant floor."),
]

# ── 1) synthesize narration ───────────────────────────────────────────────────
def synth():
    piper_bin = JROOT / ".venv" / "bin" / "piper"
    cfg = str(VOICE_ONNX) + ".json"
    durs = {}
    for sc in SCENES:
        out = AUD / f"{sc['id']}.wav"
        if not out.exists() or out.stat().st_size < 1000:
            r = subprocess.run([str(piper_bin), "-m", str(VOICE_ONNX), "-c", cfg,
                                "-f", str(out)],
                               input=sc["narration"].encode(), capture_output=True)
            if r.returncode != 0:
                raise RuntimeError(f"piper failed for {sc['id']}: {r.stderr.decode()[:200]}")
        with wave.open(str(out), "rb") as wf:
            durs[sc["id"]] = wf.getnframes() / wf.getframerate()
        print(f"  {sc['id']}: {durs[sc['id']]:.1f}s")
    return durs

# ── 2) record with injected caption bar ───────────────────────────────────────
CAPTION_JS = """(text) => {
  let bar = document.getElementById('edith-caption-bar');
  if (!bar) {
    bar = document.createElement('div');
    bar.id = 'edith-caption-bar';
    bar.style.cssText = `position:fixed;left:50%;bottom:26px;transform:translateX(-50%);
      max-width:72%;padding:10px 22px;z-index:99999;border-radius:10px;
      background:rgba(8,12,20,.86);backdrop-filter:blur(10px);
      border:1px solid rgba(125,211,252,.35);color:#e6f6ff;
      font:600 17px/1.45 system-ui,sans-serif;text-align:center;letter-spacing:.01em;
      box-shadow:0 4px 24px rgba(0,0,0,.5);pointer-events:none;`;
    document.body.appendChild(bar);
  }
  bar.textContent = text;
}"""

def safe_click(pg, sel, timeout=4000):
    try:
        pg.click(sel, timeout=timeout); return True
    except Exception:
        return False

def record(durs):
    from playwright.sync_api import sync_playwright
    log = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": W, "height": H},
                                  record_video_dir=str(DEMO),
                                  record_video_size={"width": W, "height": H})
        pg = ctx.new_page()
        pg.goto(BASE, wait_until="domcontentloaded", timeout=45000)
        t0 = time.monotonic()
        pg.wait_for_timeout(6000)   # cockpit + stream warm-up before scene 1

        def caption(txt):
            try: pg.evaluate(CAPTION_JS, txt)
            except Exception: pass

        def scene(sc, action=None):
            start = time.monotonic() - t0
            caption(sc["caption"])
            if action:
                action()
            need = max(sc["hold"], durs.get(sc["id"], 0) + 1.0)
            spent = (time.monotonic() - t0) - start
            if spent < need:
                pg.wait_for_timeout(int((need - spent) * 1000))
            log.append({"id": sc["id"], "start": round(start, 2),
                        "end": round(time.monotonic() - t0, 2),
                        "caption": sc["caption"], "narration": sc["narration"]})

        S = {sc["id"]: sc for sc in SCENES}
        scene(S["s01_open"])
        scene(S["s02_verdict"], lambda: (safe_click(pg, "text=Show technical details"),
                                         pg.wait_for_timeout(2200),
                                         safe_click(pg, "text=Show technical details")))
        scene(S["s03_watch"], lambda: (safe_click(pg, "text=HSM.F1.GBX01"),
                                       pg.wait_for_timeout(5000),
                                       safe_click(pg, "text=/Show \\d+ more/")))
        scene(S["s04_alerts"])
        def _ask():
            if not safe_click(pg, "text=What's most likely causing this trend?"):
                pg.fill("textarea", "Diagnose this gearbox and give next steps")
                pg.keyboard.press("Enter")
        scene(S["s05_ask"], _ask)
        def _wait_answer():
            try: pg.wait_for_selector("text=How EDITH decided", timeout=95000)
            except Exception: pass
            pg.wait_for_timeout(1200)
            safe_click(pg, "text=Recommended Actions")
        scene(S["s06_answer"], _wait_answer)
        def _trace():
            try: pg.wait_for_selector("text=How EDITH decided", timeout=30000)
            except Exception: pass
            safe_click(pg, "text=How EDITH decided")
            try: pg.eval_on_selector("text=How EDITH decided", "el=>el.scrollIntoView({block:'center'})")
            except Exception: pass
        scene(S["s07_trace"], _trace)
        scene(S["s08_feedback"], lambda: safe_click(pg, "text=Yes, correct"))
        scene(S["s09_logbook"], lambda: safe_click(pg, "text=Digital Logbook"))
        scene(S["s10_roles"], lambda: (safe_click(pg, "text=Manager"),
                                       pg.wait_for_timeout(1800),
                                       safe_click(pg, "text=Engineer")))
        def _report():
            navigated = False
            if safe_click(pg, '[aria-label="Generate maintenance report"]', timeout=6000):
                try:
                    pg.wait_for_url("**/report/**", timeout=60000); navigated = True
                except Exception:
                    pass
            if not navigated:
                import pathlib
                rid = pathlib.Path("/tmp/edith_demo_rid.txt").read_text().strip()
                try: pg.goto(f"{BASE}/report/{rid}", wait_until="domcontentloaded", timeout=30000)
                except Exception: pass
            pg.wait_for_timeout(2500)
            caption(S["s11_report"]["caption"])   # re-inject after navigation
            pg.mouse.wheel(0, 800)
        scene(S["s11_report"], _report)
        def _close():
            caption(S["s12_close"]["caption"])
            pg.mouse.wheel(0, 800)
        scene(S["s12_close"], _close)

        video = pg.video
        ctx.close(); browser.close()
        raw = Path(video.path())
    (DEMO / "scene_log.json").write_text(json.dumps(log, indent=1))
    return raw, log

# ── 3) build audio track + mux + srt + mp4 ────────────────────────────────────
def mux(raw, log):
    import imageio_ffmpeg
    FF = imageio_ffmpeg.get_ffmpeg_exe()
    # audio: overlay each narration wav at its scene start
    inputs, fparts, amix = [], [], []
    for i, sc in enumerate(log):
        wavp = AUD / f"{sc['id']}.wav"
        if not wavp.exists():
            continue
        inputs += ["-i", str(wavp)]
        ms = int(sc["start"] * 1000)
        fparts.append(f"[{i+1}:a]adelay={ms}|{ms}[a{i}]")
        amix.append(f"[a{i}]")
    fc = ";".join(fparts) + f";{''.join(amix)}amix=inputs={len(amix)}:normalize=0[aout]"
    final = DEMO / "EDITH_demo_final.webm"
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", str(raw), *inputs,
                    "-filter_complex", fc, "-map", "0:v", "-map", "[aout]",
                    "-c:v", "copy", "-c:a", "libopus", "-b:a", "96k", str(final)],
                   check=True)
    # srt
    def ts(s):
        h = int(s // 3600); m = int(s % 3600 // 60); sec = s % 60
        return f"{h:02d}:{m:02d}:{sec:06.3f}".replace(".", ",")
    srt = []
    for i, sc in enumerate(log, 1):
        srt += [str(i), f"{ts(sc['start'])} --> {ts(sc['end'])}", sc["caption"], ""]
    (DEMO / "EDITH_demo_final.srt").write_text("\n".join(srt))
    # mp4 for max compatibility
    mp4 = DEMO / "EDITH_demo_final.mp4"
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", str(final),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22",
                    "-c:a", "aac", "-b:a", "128k", str(mp4)], check=True)
    print(f"final: {final} ({final.stat().st_size/1e6:.1f} MB)")
    print(f"mp4  : {mp4} ({mp4.stat().st_size/1e6:.1f} MB)")
    print(f"srt  : {DEMO/'EDITH_demo_final.srt'}")


if __name__ == "__main__":
    print("1/3 synthesizing narration (Piper)…")
    durs = synth()
    print("2/3 recording captioned walkthrough…")
    raw, log = record(durs)
    print(f"   raw video: {raw}")
    print("3/3 muxing voiceover + exporting…")
    mux(raw, log)
    raw.unlink(missing_ok=True)
    print("DONE")
