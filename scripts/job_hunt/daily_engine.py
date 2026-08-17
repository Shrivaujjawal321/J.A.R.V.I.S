#!/usr/bin/env python3
"""
Jarvis daily job-outreach engine.
Runs once a day: (1) send follow-ups due today, (2) source fresh AI/ML India
targets via headless Claude, (3) verify deliverability, (4) send personalized
cold emails (bounce-safe only), (5) log, (6) Telegram report.

State of record: data/job-hunt/contacted.jsonl (dedupe + follow-up schedule).
Send transport: Gmail App Password SMTP (scripts/job_hunt/gmail_smtp_send.py).

Usage:
  python -m scripts.job_hunt.daily_engine            # full daily run
  python -m scripts.job_hunt.daily_engine --dry-run  # source+verify, NO send
  python -m scripts.job_hunt.daily_engine --limit 25 # cap new sends
  python -m scripts.job_hunt.daily_engine --no-source # follow-ups + report only
"""
from __future__ import annotations
import os
import sys
import json
import time
import argparse
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from scripts.job_hunt.verify_emails import verify
from scripts.job_hunt import gmail_smtp_send as mailer

try:
    from scripts.linkedin._telegram_notify import safe_send
except Exception:
    def safe_send(text, **k):  # fallback if telegram util unavailable
        print("[telegram unavailable]\n" + text); return False

try:
    from scripts.linkedin._claude_helper import with_tools
except Exception:
    with_tools = None

CONTACTED = ROOT / "data/job-hunt/contacted.jsonl"
POOL = ROOT / "data/job-hunt/target_pool.jsonl"
DAILY_CAP = int(os.getenv("JH_DAILY_CAP", "25"))
PACING_SEC = int(os.getenv("JH_PACING_SEC", "20"))
RESUME_PDF = ROOT / "data/resume/Ujjawal_Shrivastav_AI_ML_Engineer.pdf"
SIG = (
    "\n\nUjjawal Shrivastav\nAI/ML Engineer · Delhi, India · +91 9718732066\n"
    "National AI/ML Hackathon (Tata Steel, 4-stage) — Round 2 finalist\n"
    "🎥 EDITH demo (Tata Steel AI Hackathon R2): https://youtu.be/2upa03Ye9Zg\n"
    "Portfolio: https://ujjawal-shrivastav.vercel.app/  ·  Live: https://mcpindex-nu.vercel.app\n"
    "GitHub: https://github.com/Shrivaujjawal321\n"
    "LinkedIn: https://www.linkedin.com/in/ujjawal-shrivastav-79610a291/\n"
    "(Resume attached)"
)


def today() -> dt.date:
    return dt.date.today()


def load_state() -> list[dict]:
    if not CONTACTED.exists():
        return []
    return [json.loads(l) for l in CONTACTED.read_text().splitlines() if l.strip()]


def save_state(rows: list[dict]):
    CONTACTED.write_text("".join(json.dumps(r) + "\n" for r in rows))


def contacted_keys(rows) -> set[str]:
    return {r["email"].lower() for r in rows} | {r.get("domain", "").lower() for r in rows}


# ---------- 1. SOURCING ----------
SOURCE_PROMPT = """You are sourcing cold-email job targets for Ujjawal Shrivastav, an AI/ML Engineer (2025 B.Tech CS/AIML grad, Delhi, open to remote). Projects: Jarvis (multi-agent assistant on Claude Agent SDK), EDITH (Tata Steel R2 industrial-maintenance RAG copilot), McpIndex (hybrid search over 1532 servers), EngiNerd (LLM education), WhatsApp AI (Baileys), a LinkedIn growth pipeline. Skills: production ML (LightGBM/CatBoost), agentic RAG (ChromaDB, FlashRank, NLI gating), FastAPI/SSE, multi-agent orchestration, Next.js. National AI/ML Hackathon (Tata Steel) Round 2 finalist. KEY POSITIONING: he is an AI-native developer — using AI coding tools (Claude Code, agent pipelines) he ships production work in ANY tech stack, fast; the body may weave this in naturally where it fits the company.

Use web search to find {n} CURRENT India-based (or India-remote) seed/Series-A AI/GenAI/agentic startups (<60 people) with a VERIFIABLE current hiring signal for AI/ML or Full-Stack engineers (live careers page JD, job board listing, or founder hiring post; note it in a "hiring_signal" field). For a thoughtful founder cold email to be read, prefer small teams.

EXCLUDE these already-contacted domains: {excluded}

For EACH company output an object with a COMPLETE ready-to-send cold email:
- "company": name
- "email": best real cold-email address. Verify the DOMAIN is correct from their live site. Prefer founder firstname@domain or a published founders@/careers@/hi@.
- "subject": <60 chars, specific, company-named
- "body": <120 words, lead with the ONE Ujjawal project that matches THEIR product (with a metric), one ask "Would a 20-min call this week work?", DO NOT include a signature (it is appended automatically).

Output ONLY a valid JSON array of these objects, nothing else."""


def source_targets(n: int, excluded: set[str]) -> list[dict]:
    if with_tools is None:
        print("  [source] _claude_helper unavailable; skipping sourcing")
        return []
    prompt = SOURCE_PROMPT.format(n=n, excluded=", ".join(sorted(d for d in excluded if d)) or "(none)")
    try:
        out = with_tools(prompt, timeout=420, max_turns=30)
    except Exception as e:
        print(f"  [source] claude error: {e}")
        return []
    # extract JSON array from the response
    s = out.find("["); e = out.rfind("]")
    if s == -1 or e == -1:
        print(f"  [source] no JSON array in response (first 300): {out[:300]}")
        return []
    try:
        items = json.loads(out[s:e + 1])
    except Exception as ex:
        print(f"  [source] JSON parse failed: {ex}")
        return []
    return [it for it in items if it.get("email") and it.get("subject") and it.get("body")]


# ---------- 2. VERIFY + SEND ----------
def load_pool(excluded: set[str]) -> list[dict]:
    """Un-contacted, ready-to-send targets from the pool file (fast, no LLM)."""
    if not POOL.exists():
        return []
    out = []
    for line in POOL.read_text().splitlines():
        if not line.strip():
            continue
        try:
            it = json.loads(line)
        except Exception:
            continue
        email = (it.get("email") or "").strip().lower()
        dom = email.split("@")[-1] if "@" in email else ""
        if email and dom and email not in excluded and dom not in excluded \
           and it.get("subject") and it.get("body"):
            out.append(it)
    return out


def run_new_outreach(state, limit, dry, no_source) -> list[dict]:
    excluded = contacted_keys(state)
    # 1) pool first (fast, deterministic) ; 2) live Claude sourcing only if pool short
    raw = load_pool(excluded)
    print(f"  pool candidates: {len(raw)}")
    if len(raw) < limit and not no_source:
        raw += source_targets(min(limit + 12, 40), excluded)
    print(f"  total candidates: {len(raw)}")
    safe = []
    for it in raw:
        email = it["email"].strip().lower()
        dom = email.split("@")[-1] if "@" in email else ""
        if not dom or email in excluded or dom in excluded:
            continue
        v = verify(email)
        print(f"    {v['verdict']:>10}  {email:<34} {it.get('company','')}")
        if v["verdict"] in ("valid", "catch_all"):
            safe.append(it); excluded.add(email); excluded.add(dom)
        if len(safe) >= limit:
            break
    sent = []
    if not safe:
        print("  no bounce-safe targets this run")
        return sent
    if dry:
        print(f"  [dry-run] would send {len(safe)}")
        return [{"company": s.get("company"), "email": s["email"], "dry": True} for s in safe]
    srv = mailer._connect()
    f1 = (today() + dt.timedelta(days=4)).isoformat()
    f2 = (today() + dt.timedelta(days=10)).isoformat()
    attachments = [str(RESUME_PDF)] if RESUME_PDF.exists() else None
    for s in safe:
        try:
            mailer.send_one(srv, s["email"], s["subject"], s["body"].rstrip() + SIG,
                            attachments=attachments)
            print(f"    ✅ sent {s['email']}")
            sent.append({
                "date": today().isoformat(), "email": s["email"].lower(),
                "domain": s["email"].split("@")[-1].lower(), "company": s.get("company", ""),
                "subject": s["subject"], "status": "sent",
                "f1_due": f1, "f1_sent": False, "f2_due": f2, "f2_sent": False,
            })
        except Exception as e:
            print(f"    ❌ {s['email']}: {e}")
        time.sleep(PACING_SEC)
    try:
        srv.quit()
    except Exception:
        pass
    return sent


# ---------- 3. FOLLOW-UPS ----------
def followup_body(stage: int, subject: str) -> str:
    line = ("Following up on my note last week — I know inboxes get busy. "
            "Still genuinely keen on a quick 20-min chat about how I could contribute."
            if stage == 1 else
            "Last gentle nudge on this — I have a couple of other processes moving, "
            "but you're top of my list. Happy to work around your schedule for 20 minutes.")
    return f"Hi,\n\n{line}\n\nQuick recap of what I bring: production ML + agentic RAG + multi-agent systems, all shipped and live (links below).{SIG}"


def run_followups(state, dry) -> int:
    t = today().isoformat()
    srv = None
    n = 0
    for r in state:
        if r.get("status") != "sent":
            continue
        for stage, due, flag in ((1, "f1_due", "f1_sent"), (2, "f2_due", "f2_sent")):
            if not r.get(flag) and r.get(due) and r[due] <= t:
                if dry:
                    print(f"  [dry-run] would F{stage} → {r['email']}")
                    r[flag] = True; n += 1; continue
                try:
                    if srv is None:
                        srv = mailer._connect()
                    subj = "Re: " + r.get("subject", "Reaching out")
                    mailer.send_one(srv, r["email"], subj, followup_body(stage, subj))
                    print(f"  ✅ F{stage} → {r['email']}")
                    r[flag] = True; n += 1
                    time.sleep(PACING_SEC)
                except Exception as e:
                    print(f"  ❌ F{stage} {r['email']}: {e}")
    if srv:
        try:
            srv.quit()
        except Exception:
            pass
    return n


# ---------- MAIN ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=DAILY_CAP)
    ap.add_argument("--no-source", action="store_true")
    args = ap.parse_args()

    state = load_state()
    print(f"=== Jarvis daily job-engine {today()} (state={len(state)}) ===")

    print("[follow-ups]")
    nf = run_followups(state, args.dry_run)

    print("[new outreach]")
    sent = run_new_outreach(state, args.limit, args.dry_run, args.no_source)
    if not args.dry_run:
        state.extend(sent)

    if not args.dry_run:
        save_state(state)

    n_new = len([s for s in sent if not s.get("dry")])
    total = len([r for r in state if r.get("status") == "sent"])
    report = (
        f"📬 *Job Outreach — {today()}*\n"
        f"• New cold emails sent: *{n_new}*\n"
        f"• Follow-ups sent: *{nf}*\n"
        f"• Lifetime contacted: *{total}*\n"
        + ("\n_(dry-run — nothing actually sent)_" if args.dry_run else "")
    )
    if sent and not args.dry_run:
        report += "\n\nToday: " + ", ".join(s.get("company") or s["email"] for s in sent[:12])
    print("\n" + report)
    if not args.dry_run:
        safe_send(report)


if __name__ == "__main__":
    main()
