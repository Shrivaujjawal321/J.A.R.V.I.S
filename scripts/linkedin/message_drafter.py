"""
Drafts varied messages to existing 1st-degree LinkedIn connections.

Avoids spam-flag detection by:
  - Rotating across 5 template categories
  - Personalizing each message with profile context
  - Enforcing no-repeat via contacted.jsonl

Templates:
  intro          — first message after they accepted a recent connection
  re_engage      — connection went silent for 6+ months, gentle nudge
  share_value    — share something useful (article, tool, opportunity)
  ask_feedback   — ask for input on Boss's project / decision
  congratulate   — react to their recent promotion / new role / launch
"""
from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import _claude_helper

JARVIS_ROOT = Path(__file__).resolve().parents[2]
CONTACTED_LOG = JARVIS_ROOT / "data" / "linkedin" / "contacted.jsonl"

TEMPLATES = ["intro", "re_engage", "share_value", "ask_feedback", "congratulate"]
TEMPLATE_WEIGHTS = [0.15, 0.20, 0.25, 0.20, 0.20]

LINKEDIN_DM_SOFT_CAP = 1200  # chars; LinkedIn allows more but engagement drops

MESSAGE_PROMPT = """\
You are drafting a LinkedIn DM for Ujjawal Shrivastav (AI-native dev,
building Jarvis = multi-agent AI assistant, job-hunting in AI/ML).

## Template type: {template}
{template_brief}

## Recipient
{profile_block}

## Last interaction with this person (if any)
{last_interaction}

## Voice rules
- Real-human tone. NO "Hope this message finds you well."
- NO "I wanted to reach out because…" preamble.
- Open with the specific thing, not a greeting + filler.
- One clear ASK or one clear OFFER per message — not both, not neither.
- 60–180 words. Short paragraphs. Line breaks between thoughts.
- Hinglish ok for Indian recipients ONLY if it would feel natural to them.

## Quality bar
- Mentions at least ONE specific detail from their profile/work
- Does NOT pitch Boss as a candidate unless template = intro AND they're ICP-B (recruiter)
- Does NOT include calendar links / "let's hop on a call" in first message
- Does NOT use the word "synergy", "thrilled", "humbled", "incredible journey"

Reply with ONLY this JSON, no prose:
{{"message": "<the DM>", "word_count": <int>, "ask_or_offer": "<what's the one ask/offer>"}}
"""

TEMPLATE_BRIEFS = {
    "intro": (
        "They accepted Boss's connection request recently. This is the first DM. "
        "Acknowledge a specific thing from their profile, share why Boss connected, "
        "leave the door open without a hard ask."
    ),
    "re_engage": (
        "1st-degree connection but no interaction in 6+ months. Gentle re-engage. "
        "Reference what they've been up to publicly, maybe share something Boss is doing "
        "that overlaps. NO 'long time no see' / 'just checking in'."
    ),
    "share_value": (
        "Share something genuinely useful for them: a tool, article, opportunity, or "
        "intro that maps to their stated focus. Asks nothing in return."
    ),
    "ask_feedback": (
        "Ask their input on a specific thing Boss is building/deciding. "
        "Frame as 'your view would help' not 'pick my brain'. Make the ask concrete and small."
    ),
    "congratulate": (
        "They just got promoted / changed jobs / launched something / hit a milestone. "
        "Genuine congrats with one specific reference, then optionally a short follow-up question. "
        "Not 'congrats on the new role!' generic."
    ),
}


def _last_interaction_for(profile_id: str) -> str:
    """Look up the last logged interaction with this person, if any."""
    if not CONTACTED_LOG.exists():
        return "None — first interaction."
    last = None
    for line in CONTACTED_LOG.read_text().splitlines():
        if not line.strip():
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("profile_id") == profile_id:
            last = ev
    if not last:
        return "None — first interaction."
    return json.dumps(
        {
            "when": last.get("ts"),
            "action": last.get("action"),
            "template": last.get("template"),
            "outcome": last.get("outcome"),
        },
        indent=2,
    )


def _pick_template(profile: dict[str, Any]) -> str:
    """
    Pick template based on signals + weighted random.
    Hard rules:
      - If profile has 'recent_promotion' or 'recent_new_role' -> congratulate
      - If profile.is_first_dm == True -> intro
      - Else weighted random across the rest.
    """
    if profile.get("recent_promotion") or profile.get("recent_new_role"):
        return "congratulate"
    if profile.get("is_first_dm") is True:
        return "intro"
    pool = [t for t in TEMPLATES if t not in ("intro", "congratulate")]
    weights = [TEMPLATE_WEIGHTS[TEMPLATES.index(t)] for t in pool]
    return random.choices(pool, weights=weights, k=1)[0]


def draft_for_profile(profile: dict[str, Any]) -> dict:
    template = profile.get("force_template") or _pick_template(profile)
    profile_block = json.dumps(
        {k: v for k, v in profile.items() if v is not None and not k.startswith("_")},
        indent=2,
        ensure_ascii=False,
    )
    last = _last_interaction_for(profile["id"])
    prompt = MESSAGE_PROMPT.format(
        template=template,
        template_brief=TEMPLATE_BRIEFS[template],
        profile_block=profile_block,
        last_interaction=last,
    )
    result = _claude_helper.json_call(prompt)
    msg = (result.get("message") or "").strip()
    if len(msg) > LINKEDIN_DM_SOFT_CAP:
        msg = msg[:LINKEDIN_DM_SOFT_CAP].rstrip() + "…"
    return {
        "profile_id": profile["id"],
        "name": profile.get("name"),
        "template": template,
        "message": msg,
        "word_count": len(msg.split()),
        "ask_or_offer": result.get("ask_or_offer"),
        "drafted_at": datetime.now(timezone.utc).isoformat(),
    }


def draft_batch(profiles: list[dict[str, Any]]) -> list[dict]:
    out = []
    for p in profiles:
        try:
            out.append(draft_for_profile(p))
        except Exception as e:
            out.append({
                "profile_id": p.get("id"),
                "name": p.get("name"),
                "message": None,
                "error": str(e)[:200],
            })
    return out


if __name__ == "__main__":
    sample = {
        "id": "test-conn-id",
        "name": "Rohan Mehta",
        "headline": "Senior SDE @ Razorpay | ex-Flipkart",
        "company": "Razorpay",
        "is_first_dm": False,
        "recent_post_excerpt": "Migrated our payment service to Rust. 3x throughput, 60% memory reduction.",
    }
    print(json.dumps(draft_for_profile(sample), indent=2, ensure_ascii=False))
