"""
Generates personalized connection-request notes for a batch of ICP profiles.

Input:  list of profile dicts (from icp_search.py) with name, headline, company,
        recent_post (optional), shared_signals.
Output: list of {profile_id, note} dicts.  note is <= 200 chars (LinkedIn limit).

Uses _claude_helper.json_call so retries on malformed JSON are cheap.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import _claude_helper

JARVIS_ROOT = Path(__file__).resolve().parents[2]
ICP_PATH = JARVIS_ROOT / "data" / "linkedin" / "icp.json"

LINKEDIN_NOTE_LIMIT = 200  # chars; LinkedIn truncates harder than 300

DRAFTER_PROMPT = """\
You are drafting LinkedIn connection-request notes for Ujjawal Shrivastav,
an AI-native developer building Jarvis (a multi-agent personal AI assistant)
and actively job-hunting in AI/ML roles.

## Voice rules (CRITICAL — read every time)
- Write like a real human, not a bot. NO "I came across your profile".
- NO "I'd love to connect to expand my network".
- NO "Hope this finds you well".
- Reference ONE specific thing from their profile or a shared signal.
- Sound curious, not transactional.
- Keep it under 200 characters INCLUDING punctuation.
- Use first names. Don't address as "Mr."/"Ms.".
- Hinglish ok ONLY for Indian recipients with Indian names AND if it sounds natural.
  Default to clean English.

## ICP value-offer (use only if it fits naturally — never paste verbatim)
{value_offer}

## Profile to write to
{profile_block}

## Your job
Write ONE connection-request note (<= 200 chars) that:
1. References a specific signal from their profile
2. Says why connecting is interesting (1 short clause)
3. Does NOT ask for a job, a referral, or a call
4. Feels like something a smart 22-year-old engineer would actually write

Reply with ONLY this JSON, no prose:
{{"note": "<the note>", "char_count": <int>, "signal_used": "<which signal you grounded on>"}}
"""


def _load_icp() -> dict:
    return json.loads(ICP_PATH.read_text())


def _value_offer_for_category(icp: dict, category_id: str) -> str:
    for cat in icp["categories"]:
        if cat["id"] == category_id:
            return cat["value_offer"]
    return "AI/ML developer interested in your work."


def draft_for_profile(profile: dict[str, Any], icp: dict | None = None) -> dict:
    """
    profile = {
        "id": "linkedin-handle-or-uuid",
        "name": "First Last",
        "headline": "...",
        "company": "...",
        "recent_post_excerpt": "..." (optional),
        "shared_school": "..." (optional),
        "shared_company_alum": "..." (optional),
        "mutual_count": int (optional),
        "category_id": "A"|"B"|...|"G"
    }
    """
    icp = icp or _load_icp()
    category_id = profile.get("category_id", "A")
    value_offer = _value_offer_for_category(icp, category_id)
    profile_block = json.dumps(
        {k: v for k, v in profile.items() if v is not None},
        indent=2,
        ensure_ascii=False,
    )
    prompt = DRAFTER_PROMPT.format(
        value_offer=value_offer,
        profile_block=profile_block,
    )

    result = _claude_helper.json_call(prompt)
    note = (result.get("note") or "").strip()
    if len(note) > LINKEDIN_NOTE_LIMIT:
        # Hard-trim — better than failing the whole batch
        note = note[: LINKEDIN_NOTE_LIMIT - 1].rstrip() + "…"

    return {
        "profile_id": profile["id"],
        "name": profile.get("name"),
        "category_id": category_id,
        "note": note,
        "char_count": len(note),
        "signal_used": result.get("signal_used"),
    }


def draft_batch(profiles: list[dict[str, Any]]) -> list[dict]:
    """Drafts notes for all profiles. Continues on individual failures."""
    icp = _load_icp()
    out = []
    for p in profiles:
        try:
            out.append(draft_for_profile(p, icp=icp))
        except Exception as e:
            out.append({
                "profile_id": p.get("id"),
                "name": p.get("name"),
                "category_id": p.get("category_id"),
                "note": None,
                "error": str(e)[:200],
            })
    return out


if __name__ == "__main__":
    sample = {
        "id": "test-sample",
        "name": "Priya Sharma",
        "headline": "Engineering Manager, Applied AI @ Razorpay",
        "company": "Razorpay",
        "recent_post_excerpt": "Just shipped LLM-powered fraud detection in production. Latency was the hardest part.",
        "category_id": "A",
    }
    print(json.dumps(draft_for_profile(sample), indent=2, ensure_ascii=False))
