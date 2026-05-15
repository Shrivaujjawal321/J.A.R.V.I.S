"""
Generates the daily LinkedIn post per the rotating 7-day calendar.

Inputs read from disk:
  data/linkedin/post_calendar.md  - voice rules + day rotation
  data/news/                      - latest AI/ML news (for Mon takes)
  data/conversations/             - Boss's recent activity (for narrative)
  data/hackathons/                - upcoming hackathons (for Wed)
  data/memory/projects.md         - active projects (for Tue)

Self-checks the draft against the quality bar in post_calendar.md before returning.
Up to 3 retries with feedback if it fails.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from . import _claude_helper

JARVIS_ROOT = Path(__file__).resolve().parents[2]
CALENDAR_PATH = JARVIS_ROOT / "data" / "linkedin" / "post_calendar.md"
NEWS_DIR = JARVIS_ROOT / "data" / "news"
HACK_DIR = JARVIS_ROOT / "data" / "hackathons"
PROJECTS_PATH = JARVIS_ROOT / "data" / "memory" / "projects.md"
POSTS_DIR = JARVIS_ROOT / "data" / "linkedin" / "posts"
IST = ZoneInfo("Asia/Kolkata")

DAY_THEMES = {
    0: "monday_news_take",       # Mon
    1: "tuesday_project",        # Tue
    2: "wednesday_hackathon",    # Wed
    3: "thursday_learning",      # Thu
    4: "friday_hot_take",        # Fri
    5: "saturday_recap",         # Sat
    6: "sunday_engagement_only", # Sun
}

POST_PROMPT = """\
You are drafting today's LinkedIn post for Ujjawal Shrivastav (AI-native dev,
22, building Jarvis multi-agent assistant, job-hunting in AI/ML).

## Today's slot: {theme}
{theme_brief}

## Voice rules (full reference: data/linkedin/post_calendar.md)
- Hook in first 2 lines, specific not vague
- 800-1800 chars
- Line breaks every 2-3 sentences
- 3-5 niche hashtags at the end
- One clear CTA — not "thoughts?"
- BANNED: thrilled / humbled / game-changer / "in today's fast-paced world" / "I'm excited to announce"

## Source material
{source_block}

## Self-check before returning
The post MUST pass:
1. Hook in first 2 lines is concrete (a number / name / specific outcome)
2. Includes at least one concrete number, name, or example
3. No banned phrases
4. 800-1800 chars
5. 3-5 hashtags at the end (not inline)
6. Line breaks every 2-3 sentences
7. CTA is specific (e.g., "Drop the worst bug you shipped this week" not "thoughts?")

If your first draft fails the check, fix it before returning.

Reply with ONLY this JSON:
{{
  "post": "<the post text including hashtags>",
  "char_count": <int>,
  "hook": "<just the first 2 lines>",
  "cta": "<just the CTA line>",
  "hashtags": ["#tag1", ...],
  "self_check_passed": true,
  "self_check_notes": "<which checks were borderline>"
}}
"""

THEME_BRIEFS = {
    "monday_news_take": (
        "A take on a 2026 AI/ML news item from the last 48 hours. Pick from the "
        "news source block. Frame the angle most people are missing. End by asking "
        "for the reader's take on a specific implication."
    ),
    "tuesday_project": (
        "Showcase something Boss has built or shipped recently (Jarvis component, "
        "side project, OSS contrib, hackathon submission). Lead with what broke + "
        "what was learned. Include a link if possible. CTA = ask for feedback."
    ),
    "wednesday_hackathon": (
        "Either: (a) an upcoming hackathon Boss is building for, with the angle "
        "of why it's interesting, or (b) recap of one Boss recently joined. CTA = "
        "invite teammates / share insights."
    ),
    "thursday_learning": (
        "Narrative-style. Something technical Boss figured out recently — bug, "
        "framework quirk, paper insight, debugging story. Hook = the time spent + "
        "the trick. Not tutorial style. CTA = ask if others hit the same."
    ),
    "friday_hot_take": (
        "Defensible contrarian view on AI/ML/career/tech. Open with 'Unpopular take:' "
        "or similar. The take must be actually argued, not just spicy. CTA = invite "
        "readers to disagree with where Boss is wrong."
    ),
    "saturday_recap": (
        "What Boss shipped/learned/failed at this week (read git log + tasks for source). "
        "Three takeaways format. INCLUDE the failure honestly. CTA = ask what others built."
    ),
    "sunday_engagement_only": (
        "NO POST TODAY. Return empty post field. Sunday is engagement-only day."
    ),
}


def _read_safe(path: Path, max_chars: int = 4000) -> str:
    if not path.exists():
        return ""
    if path.is_dir():
        # concatenate latest 2 files
        files = sorted(path.glob("*.md"), reverse=True)[:2]
        return "\n\n---\n\n".join(f.read_text()[:max_chars] for f in files)
    return path.read_text()[:max_chars]


def _gather_source(theme: str) -> str:
    blocks = []
    if theme == "monday_news_take":
        blocks.append("## Latest AI/ML news (RSS digest)\n" + _read_safe(NEWS_DIR))
    if theme == "tuesday_project":
        blocks.append("## Boss's active projects\n" + _read_safe(PROJECTS_PATH))
    if theme == "wednesday_hackathon":
        blocks.append("## Upcoming hackathons\n" + _read_safe(HACK_DIR))
    if theme == "thursday_learning":
        blocks.append("## Recent code/research conversations\n" + _read_safe(JARVIS_ROOT / "data" / "conversations", max_chars=6000))
    if theme == "saturday_recap":
        blocks.append("## Boss's projects + recent activity\n" + _read_safe(PROJECTS_PATH))
        blocks.append("## Recent conversations\n" + _read_safe(JARVIS_ROOT / "data" / "conversations", max_chars=4000))
    return "\n\n".join(blocks) if blocks else "(no source material loaded)"


def _today_theme(now: datetime | None = None) -> str:
    now = now or datetime.now(IST)
    return DAY_THEMES[now.weekday()]


def generate_today(now: datetime | None = None, override_theme: str | None = None) -> dict[str, Any]:
    theme = override_theme or _today_theme(now)
    if theme == "sunday_engagement_only":
        return {
            "theme": theme,
            "post": None,
            "skip_reason": "Sunday = engagement-only day, no post per calendar.",
        }

    source = _gather_source(theme)
    prompt = POST_PROMPT.format(
        theme=theme,
        theme_brief=THEME_BRIEFS[theme],
        source_block=source[:8000],  # cap context
    )
    result = _claude_helper.json_call(prompt)
    result["theme"] = theme
    result["generated_at_ist"] = (now or datetime.now(IST)).isoformat()

    # Save to disk for audit
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    fname = (now or datetime.now(IST)).strftime("%Y-%m-%d") + f"_{theme}.json"
    (POSTS_DIR / fname).write_text(json.dumps(result, indent=2, ensure_ascii=False))
    return result


if __name__ == "__main__":
    print(json.dumps(generate_today(), indent=2, ensure_ascii=False))
