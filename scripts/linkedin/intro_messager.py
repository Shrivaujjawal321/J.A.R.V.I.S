"""
Drafts the daily batch of "Jarvis-intro" DMs to 1st-degree LinkedIn connections.

Why these DMs are unusual: they're Jarvis introducing itself — the message IS
the demo of Boss's build. Recruiters who get a personalized note from Boss's
own AI assistant see live proof of his work, not a generic outreach template.

Targeting:
  - Only 1st-degree connections (free to DM, no InMail budget)
  - Filtered by headline to recruiters / hiring managers / talent partners /
    founders / heads of engineering — people whose pipeline this DM fits
  - Skips anyone already in contacted.jsonl
  - Daily cap enforced by daily_runner (default 10/day)

The template is hardcoded English (Boss approved 2026-05-15). Personalization
is minimal — first-name substitution only — by design, so each send looks
identical-but-named, reinforcing the "I'm one AI assistant, talking to many
of you" signal rather than fake-warm-intro signal.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from . import icp_search

JARVIS_ROOT = Path(__file__).resolve().parents[2]
CONTACTED_LOG = JARVIS_ROOT / "data" / "linkedin" / "contacted.jsonl"

# Headline-keyword filter for "people the Jarvis-intro DM is appropriate to send to"
RECRUITER_KEYWORDS = (
    "recruiter", "talent", "talent acquisition", "ta partner", "ta lead",
    "hiring", "people partner", "head of talent", "head of people",
    "campus recruit", "early careers", "university recruit",
)
LEADERSHIP_KEYWORDS = (
    "founder", "co-founder", "cofounder", "ceo", "cto", "vp engineering",
    "head of engineering", "engineering manager", "engineering lead",
    "director of engineering",
)
EXCLUDE_KEYWORDS = (
    "open to work", "looking for opportunities", "seeking", "actively interviewing",
)

INTRO_TEMPLATE = """\
Hi {name},

I'm Jarvis — the personal AI assistant Ujjawal Shrivastav built from scratch. I'm writing this message to you directly; Ujjawal approved it before it left his system, but everything you're reading right now was drafted, scheduled, and sent by me. End-to-end automation, applied to outreach.

Quick context: Ujjawal is a 22-year-old AI/ML developer from India, fresh graduate, looking for AI/ML engineering roles where his build-first instinct lands. He's spent the last several months engineering me into a fully operational, daily-driven system — not a toy, not a hobby project.

Here's what I actually do for him, end-to-end:

• Multi-agent orchestration — I delegate to 93 specialized sub-agents (frontend engineer, ML engineer, security, research, ghostwriter, financial analyst, and 87 others) and synthesize their output into a single coherent response. They run in parallel when the work allows.

• Persistent memory — a file-based memory layer + a knowledge graph for entities and relations + episodic recall via a ChromaDB vector store. I remember Ujjawal's projects, his people, his preferences, and every conversation we've had.

• Autonomous overnight goal pursuit — Ujjawal queues a goal at night through Telegram. I decompose it into sub-tasks, execute the safe ones in parallel, queue irreversible actions for his morning approval, and surface a digest before he wakes up. The system self-recovers across daemon restarts.

• Browser automation — I drive his logged-in Chrome via Chrome DevTools MCP. That's how I scouted your profile, drafted this DM, and queued it for his approval. The same infrastructure handles application submissions, profile audits, and form fills.

• Voice + Telegram interface — Whisper STT + Piper TTS + a Telegram bridge so Ujjawal can run me from his phone, no laptop required.

• Self-growth loop — I auto-capture every conversation, run a weekly self-review that proposes my own capability upgrades within a safe-path allow-list, and surface anything outside that scope for explicit approval.

The operating philosophy Ujjawal wired into me from day one: single unit, output maximized, ego zero. He treats me as half of his throughput — not as a chatbot he opens when stuck.

Why I'm reaching out to you specifically: you hire for technical roles, and the candidate you'd be evaluating isn't applying like an ordinary fresher. He ships AI-native workflows on himself before pitching them anywhere else. If he can automate his own job hunt, his own daily briefing, his own outreach pipeline, and his own hackathon research to this depth — the same instinct comes with him into your team's actual product work. Whatever your AI/ML org is building — workflow automation, internal tooling, agentic interfaces, RAG systems — he's already shipped a smaller-scale version of it on himself.

If you're open to a 5-minute look, I can share his project list, a short demo of me operating, and his resume. No urgency from his side — he just wants to be on your radar for the right role.

Best,
Jarvis
(on behalf of Ujjawal Shrivastav)\
"""


def _load_contacted_ids() -> set[str]:
    if not CONTACTED_LOG.exists():
        return set()
    import json
    ids: set[str] = set()
    for line in CONTACTED_LOG.read_text().splitlines():
        if not line.strip():
            continue
        try:
            ev = json.loads(line)
            if pid := ev.get("profile_id"):
                ids.add(pid)
        except json.JSONDecodeError:
            continue
    return ids


def _is_eligible(profile: dict) -> bool:
    headline = (profile.get("headline") or "").lower()
    if any(k in headline for k in EXCLUDE_KEYWORDS):
        return False
    return any(k in headline for k in RECRUITER_KEYWORDS + LEADERSHIP_KEYWORDS)


def _first_name(full_name: str | None) -> str:
    if not full_name:
        return "there"
    return full_name.strip().split()[0]


def _draft_one(profile: dict, idx: int) -> dict:
    return {
        "id": f"m{idx}",
        "profile_id": profile["id"],
        "name": profile.get("name"),
        "headline": profile.get("headline"),
        "template": "jarvis_intro_v1",
        "message": INTRO_TEMPLATE.format(name=_first_name(profile.get("name"))),
        "char_count": len(INTRO_TEMPLATE.format(name=_first_name(profile.get("name")))),
        "drafted_at": datetime.now(timezone.utc).isoformat(),
    }


def draft_intros(n: int = 10, *, oversample: int = 3) -> list[dict]:
    """
    Returns up to `n` drafted Jarvis-intro DMs for eligible 1st-degree connections.
    Over-samples by `oversample`x so the keyword filter can drop non-matches and still hit n.
    """
    pool_size = max(n * oversample, n + 5)
    candidates = icp_search.find_first_degree_for_messaging(n=pool_size)
    contacted = _load_contacted_ids()

    drafts: list[dict] = []
    idx = 0
    for prof in candidates:
        if prof.get("id") in contacted:
            continue
        if not _is_eligible(prof):
            continue
        drafts.append(_draft_one(prof, idx))
        idx += 1
        if len(drafts) >= n:
            break
    return drafts


if __name__ == "__main__":
    import json
    out = draft_intros(n=3)
    print(json.dumps(out, indent=2, ensure_ascii=False))
