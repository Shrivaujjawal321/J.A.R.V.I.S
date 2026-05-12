#!/usr/bin/env python3
"""
Build Tier-2 Jarvis specialist agents in bulk.

Reads each `data/agent-prompts-final/{slug}.md`, extracts THE PROMPT block,
wraps with YAML frontmatter + minimal Jarvis overlay, writes to
`.claude/agents/{slug}-agent.md`.

Skips:
- Tier-1 already hand-crafted (10 agents)
- Direct overlaps with existing Jarvis specialists
- README.md
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FINAL_DIR = ROOT / "data" / "agent-prompts-final"
AGENTS_DIR = ROOT / ".claude" / "agents"

# Already-built Tier-1 (full Jarvis overlay)
TIER_1 = {
    "backend-engineer", "data-analyst", "devops-sre", "frontend-engineer",
    "ml-engineer", "product-manager", "prompt-engineer", "security-engineer",
    "technical-writer", "ui-ux-designer",
}

# Direct overlaps with existing Jarvis specialists — skip to avoid name/role conflicts
EXISTING_JARVIS_OVERLAP = {
    "software-developer",  # → code-agent
    "code-reviewer",       # → code-agent
}

SKIP = TIER_1 | EXISTING_JARVIS_OVERLAP | {"README"}

# Slug → recommended model. Default sonnet; opus for high-stakes reasoning.
OPUS_AGENTS = {
    "compliance-officer", "legal-assistant", "patent-analyst", "policy-analyst",
    "fact-checker", "investigative-journalist", "medical-scribe",
    "strategy-consultant", "pricing-strategist", "negotiation-coach",
    "statistician", "economist", "research-analyst",
    "mental-health-companion",
}


def extract_prompt_block(text: str) -> str | None:
    """Extract THE PROMPT body (inside triple-backtick after the prompt header)."""
    # Header variations
    header_patterns = [
        r"##\s*[^\n]*THE PROMPT[^\n]*\n",
        r"##\s*THE PROMPT[^\n]*\n",
    ]
    start = None
    for pat in header_patterns:
        m = re.search(pat, text)
        if m:
            start = m.end()
            break
    if start is None:
        return None

    # Find first ``` after header (open fence) and matching close fence
    body = text[start:]
    fence_match = re.search(r"^```[a-zA-Z]*\n", body, re.MULTILINE)
    if not fence_match:
        return None
    open_end = fence_match.end()
    rest = body[open_end:]
    close_match = re.search(r"\n```\s*$", rest, re.MULTILINE)
    if not close_match:
        # try plain "\n```"
        close_match = re.search(r"\n```", rest)
    if not close_match:
        return None
    return rest[: close_match.start()].strip()


def extract_description(text: str, slug: str) -> str:
    """Pull a one-line description from the 'What This Agent Delivers' section."""
    m = re.search(r"##\s*[^\n]*What This Agent Delivers[^\n]*\n+([^\n][^\n]+)", text)
    if m:
        first_line = m.group(1).strip()
        # Trim to ~280 chars; strip bold markers
        first_line = re.sub(r"\*\*", "", first_line)
        if len(first_line) > 280:
            first_line = first_line[:277].rsplit(" ", 1)[0] + "..."
        return f"Use for {slug.replace('-', ' ')} tasks — {first_line}"
    # Fallback
    pretty = slug.replace("-", " ").title()
    return f"Use for {pretty} tasks. Specialist agent at senior-expert tier."


def slug_to_role_name(slug: str) -> str:
    return slug.replace("-", " ").title()


def build_overlay(slug: str) -> str:
    """Minimal Jarvis overlay — memory reads + Hinglish + sibling-agent awareness."""
    role = slug_to_role_name(slug)
    return f"""You are the **{role} Specialist** for Jarvis — a Tier-2 specialist agent built from the max-potential prompt library.

## Jarvis Operating Rules (read every session)

Before substantive work, Read:
- `data/memory/facts.md` — Boss's identity, context
- `data/memory/projects.md` — what's active
- `data/memory/preferences.md` — Hinglish mirror, options-with-why, one-question-at-a-time

Defaults:
- **Hinglish mirror.** Match Boss's register in conversation. Artifacts in target language (usually English).
- **ONE clarifying question** if ambiguous — never batch.
- **Options with WHY** for any non-trivial choice — 2-3 options + reasoning each, Boss picks.
- **Never autonomously send / publish / commit** — draft only.
- **Save substantial outputs** to `data/outputs/{slug}/` (create dir if needed).

Sibling-agent handoffs (use the manager to dispatch):
- Code-level work → `code-agent` / `backend-engineer-agent` / `frontend-engineer-agent`
- Web research → `research-agent`
- Saving learnings to memory → `memory-agent`
- Resume framing / job-hunt → `resume-agent` / `job-hunt-agent`
- Hackathon strategy → `hackathon-agent`

---

## SPECIALIST PROTOCOL (verbatim, max-potential)
""".replace("{slug}", slug)


def build_agent_file(slug: str, src_text: str) -> str | None:
    prompt_body = extract_prompt_block(src_text)
    if not prompt_body:
        print(f"  [SKIP] {slug}: could not extract THE PROMPT block", file=sys.stderr)
        return None
    description = extract_description(src_text, slug)
    model = "opus" if slug in OPUS_AGENTS else "sonnet"
    name = f"{slug}-agent"

    frontmatter = (
        "---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        "tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch\n"
        f"model: {model}\n"
        "tier: 2\n"
        "---\n\n"
    )
    overlay = build_overlay(slug)
    return frontmatter + overlay + "\n" + prompt_body + "\n\n---\n\n**Hinglish mirror in conversation. One question at a time. Options-with-why for choices. Draft only — never autopublish.**\n"


def main() -> int:
    if not FINAL_DIR.exists():
        print(f"ERROR: {FINAL_DIR} not found", file=sys.stderr)
        return 1
    AGENTS_DIR.mkdir(parents=True, exist_ok=True)

    written = []
    skipped = []
    failed = []

    for src in sorted(FINAL_DIR.glob("*.md")):
        slug = src.stem
        if slug in SKIP:
            skipped.append(slug)
            continue
        text = src.read_text()
        out = build_agent_file(slug, text)
        if out is None:
            failed.append(slug)
            continue
        dest = AGENTS_DIR / f"{slug}-agent.md"
        dest.write_text(out)
        written.append(slug)

    print(f"Wrote: {len(written)} Tier-2 agents")
    print(f"Skipped: {len(skipped)} (Tier-1 or existing Jarvis overlap)")
    print(f"Failed: {len(failed)}")
    if failed:
        print("  Failed slugs:", failed)
    return 0 if not failed else 2


if __name__ == "__main__":
    sys.exit(main())
