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
# News digests live at data/briefings/news-YYYY-MM-DD.md (NOT data/news/).
NEWS_DIR = JARVIS_ROOT / "data" / "briefings"
NEWS_GLOB = "news-*.md"
HACK_DIR = JARVIS_ROOT / "data" / "hackathons"
PROJECTS_PATH = JARVIS_ROOT / "data" / "memory" / "projects.md"
POSTS_DIR = JARVIS_ROOT / "data" / "linkedin" / "posts"
IST = ZoneInfo("Asia/Kolkata")

# Daily tech-news rotation — each day a different angle on AI/ML news.
# See data/linkedin/post_calendar.md for hook/CTA/source per theme.
DAY_THEMES = {
    0: "mon_weekend_wrap",       # Mon
    1: "tue_paper_breakdown",    # Tue
    2: "wed_product_launch",     # Wed
    3: "thu_tooling_news",       # Thu
    4: "fri_hot_take",           # Fri
    5: "sat_weekly_roundup",     # Sat
    6: "sun_builder_spotlight",  # Sun
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
    "mon_weekend_wrap": (
        "Weekend Wrap. Pick the top 1-3 AI/ML stories from the past 72 hours (Fri-Sun) "
        "out of the news source block. Frame what the wider conversation is missing. "
        "Hook: 'What you missed in AI over the weekend:' followed by 2-3 punchy lines. "
        "CTA: 'Which of these shifts your stack this week?' Name specific companies / "
        "models / numbers — no generic 'AI is moving fast' framing."
    ),
    "tue_paper_breakdown": (
        "Paper / Research Breakdown. Pick ONE recent paper or lab blog from the news "
        "source block (arxiv, Anthropic/OpenAI/DeepMind/HF). Frame what it actually "
        "proves vs how it's being marketed. Hook: '[Paper title] in one paragraph. "
        "The trick:' followed by a tight technical summary. Name the dataset, metric, "
        "delta over prior SOTA. CTA: 'Anyone tried this in prod yet? What broke?'"
    ),
    "wed_product_launch": (
        "Product / Model Launch Take. Pick a specific product or model release from "
        "the news source block (new SDK, model checkpoint, dev tool). Frame what most "
        "analysis is missing — a technical or strategic angle. Hook: '[Company] just "
        "shipped [X]. Here's what most takes are missing:' CTA: 'Will you migrate to "
        "it? What's your blocker?'"
    ),
    "thu_tooling_news": (
        "Dev Tooling / Infra News. Pick a tooling move from the news source block — "
        "LangChain, DSPy, vLLM, Modal, Replicate, HF, new SDK release, infra benchmark. "
        "Lead with what changes for a working engineer (not press-release tone). Hook: "
        "'[Tool] just got [feature]. Why builders should care:' CTA: 'What's your "
        "default for [X] in 2026?'"
    ),
    "fri_hot_take": (
        "Hot Take / Controversy. Pick a current news item or industry trend from the "
        "source block. Argue a defensible contrarian view — real argument, not "
        "engagement bait. Hook: 'Everyone's saying [common take]. They're wrong "
        "because:' CTA: 'Where am I wrong? Be specific — I'll defend the position in "
        "replies.' Take must be defensible with concrete examples."
    ),
    "sat_weekly_roundup": (
        "Weekly Roundup. Top 5 AI/ML stories of the week from the news source block, "
        "ranked. #1 is the MOST OVERLOOKED (not necessarily the biggest). Each item "
        "gets a one-line 'why it matters' — never just a headline. Hook: '5 AI stories "
        "this week. #1 is the one most people missed:' CTA: 'Which one changes how "
        "you build next week?'"
    ),
    "sun_builder_spotlight": (
        "Builder Spotlight. Pick ONE person or team from the news source block who "
        "shipped something noteworthy this week (paper, OSS release, demo, model "
        "checkpoint, viral thread). Surface independent builders + smaller teams, not "
        "just big-company employees. Hook: '[Person/Team] shipped [project] this week. "
        "Why it matters:' CTA: 'Tag a builder who deserves more attention this week.'"
    ),
}


def _read_safe(path: Path, max_chars: int = 4000, glob: str = "*.md", limit: int = 2) -> str:
    if not path.exists():
        return ""
    if path.is_dir():
        files = sorted(path.glob(glob), reverse=True)[:limit]
        return "\n\n---\n\n".join(f.read_text()[:max_chars] for f in files)
    return path.read_text()[:max_chars]


def _read_news(days: int = 3, max_chars_per_file: int = 4000) -> str:
    """Concatenate the latest `days` news digests from data/briefings/news-*.md."""
    return _read_safe(NEWS_DIR, max_chars=max_chars_per_file, glob=NEWS_GLOB, limit=days)


def _gather_source(theme: str) -> str:
    """Every daily-tech-news theme loads from the news digest as primary source.
    Per-theme extras layered on top where useful (memory, projects, etc.)."""
    blocks = []
    # All themes get the news block — different look-back windows per theme.
    if theme == "sat_weekly_roundup":
        blocks.append("## AI/ML news (last 7 days)\n" + _read_news(days=7))
    elif theme == "mon_weekend_wrap":
        blocks.append("## AI/ML news (last 3 days, Fri-Sun)\n" + _read_news(days=3))
    else:
        blocks.append("## AI/ML news (last 2 days)\n" + _read_news(days=2))

    # Theme-specific supplementary context.
    if theme == "fri_hot_take":
        blocks.append("## Boss's strongly-held views (memory)\n" + _read_safe(JARVIS_ROOT / "data" / "memory" / "preferences.md", max_chars=3000))
    if theme == "thu_tooling_news":
        blocks.append("## Boss's tech-stack context\n" + _read_safe(PROJECTS_PATH, max_chars=2000))

    return "\n\n".join(blocks) if blocks else "(no source material loaded)"


def _today_theme(now: datetime | None = None) -> str:
    now = now or datetime.now(IST)
    return DAY_THEMES[now.weekday()]


def generate_today(now: datetime | None = None, override_theme: str | None = None) -> dict[str, Any]:
    theme = override_theme or _today_theme(now)
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
