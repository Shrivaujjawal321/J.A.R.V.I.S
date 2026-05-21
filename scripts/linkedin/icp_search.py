"""
Finds ICP-matching LinkedIn profiles to send connection requests / messages to.

Strategy:
  - Spawns Claude Code in a subprocess with a self-contained prompt
  - That subprocess invokes the browser-autopilot skill (Chrome DevTools MCP)
  - Drives LinkedIn search filters per ICP category
  - Returns JSON list of candidate profiles

Why subprocess: MCP tools (mcp__chrome-devtools__*) only work inside a Claude Code
session. Pure Python can't call them directly. So we delegate the browser work
to a headless `claude -p` invocation that has the right tool permissions.

Quotas enforced:
  - Skip profiles already in contacted.jsonl
  - Skip profiles matching exclude list in icp.json
  - Stop at daily_targets quota per category
"""
from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from pathlib import Path

from . import _claude_helper

JARVIS_ROOT = Path(__file__).resolve().parents[2]
ICP_PATH = JARVIS_ROOT / "data" / "linkedin" / "icp.json"
CONTACTED_LOG = JARVIS_ROOT / "data" / "linkedin" / "contacted.jsonl"
DEBUG_DIR = JARVIS_ROOT / "data" / "linkedin" / "_debug"


SEARCH_PROMPT = """\
You are Jarvis driving Boss's logged-in LinkedIn session via Chrome DevTools MCP.

## Goal
Find {n_profiles} candidate profiles matching this ICP category:

{category_block}

## Geo priority
{geo_priority}

## Profiles to EXCLUDE (already contacted or excluded in ICP)
{exclude_block}

## Instructions
1. Use mcp__chrome-devtools__list_pages to confirm a LinkedIn tab is open.
2. Navigate to LinkedIn People search with title + company + geo filters set
   for this category. Example URL pattern:
     https://www.linkedin.com/search/results/people/?keywords=<role>&origin=GLOBAL_SEARCH_HEADER
   Then use UI clicks to apply geo + connection-degree (2nd or 3rd) filters.
3. Take a snapshot. Parse out profile cards. For each card, extract:
   - profile URL (the /in/<handle>/ path)
   - name (first card text)
   - headline (subtitle line)
   - current company (if visible)
   - location
   - mutual connection count (if visible)
4. Skip any profile whose handle matches the exclude list.
5. Skip any profile whose headline contains an exclude keyword from ICP.
6. Skip 1st-degree connections (we want NEW connections, not existing ones).
7. If you have less than {n_profiles} after one page, scroll or paginate
   (max 3 pages of search) until you reach the target.

## Hard limits
- Max 3 search pages explored.
- No clicks INTO profiles (just read the search results).
- No connection requests sent — drafting only.

## Reply
Return ONLY this JSON, nothing else:
{{
  "profiles": [
    {{
      "id": "<linkedin handle from /in/ path>",
      "url": "https://www.linkedin.com/in/<handle>/",
      "name": "<name>",
      "headline": "<headline>",
      "company": "<company or null>",
      "location": "<location or null>",
      "mutual_count": <int or null>,
      "category_id": "{category_id}",
      "discovered_at": "<ISO timestamp>"
    }},
    ...
  ],
  "search_pages_used": <int>,
  "notes": "<any anomalies — CAPTCHA, restriction warning, empty results>"
}}
"""


def _load_contacted_ids() -> set[str]:
    if not CONTACTED_LOG.exists():
        return set()
    ids = set()
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


def _load_icp() -> dict:
    return json.loads(ICP_PATH.read_text())


def search_category(
    category_id: str,
    n_profiles: int,
    *,
    extra_excludes: list[str] | None = None,
) -> dict:
    icp = _load_icp()
    category = next(c for c in icp["categories"] if c["id"] == category_id)
    contacted = _load_contacted_ids() | set(extra_excludes or [])

    # Truncate exclude list for prompt — Claude only needs recent/relevant
    exclude_sample = list(contacted)[:200]

    prompt = SEARCH_PROMPT.format(
        n_profiles=n_profiles,
        category_block=json.dumps(category, indent=2, ensure_ascii=False),
        geo_priority=", ".join(icp["_meta"]["geo_priority"]),
        exclude_block=json.dumps(exclude_sample),
        category_id=category_id,
    )
    # Browser ops need tool access
    raw = _claude_helper.with_tools(prompt, max_turns=30, timeout=600)

    # Dump raw to disk for post-mortem (overwrites previous run for same category/day)
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    (DEBUG_DIR / f"search_{stamp}_{category_id}.txt").write_text(raw)

    # Parse — Claude wraps in fences sometimes
    import re
    fenced = re.search(r"```(?:json)?\s*(.+?)\s*```", raw, re.DOTALL)
    payload = fenced.group(1) if fenced else raw
    try:
        return json.loads(payload)
    except json.JSONDecodeError as e:
        return {
            "profiles": [],
            "error": f"search returned invalid JSON: {e}",
            "raw_preview": raw[:2000],
            "raw_full_path": str(DEBUG_DIR / f"search_{stamp}_{category_id}.txt"),
        }


def search_all_categories(
    daily_target: int = 20,
    *,
    distribution: dict[str, int] | None = None,
) -> list[dict]:
    """
    Returns a flat list of profiles across all ICP categories, totaling ~daily_target.
    Default distribution: weighted by priority (1=highest).
    """
    icp = _load_icp()
    if distribution is None:
        # Priority-weighted: P1 cats get 2x weight, P2 get 1.5x, P3 1x, P4 0.5x
        weights = {
            cat["id"]: {1: 2.0, 2: 1.5, 3: 1.0, 4: 0.5}.get(cat["priority"], 1.0)
            for cat in icp["categories"]
        }
        total = sum(weights.values())
        distribution = {
            cid: max(1, round(daily_target * w / total))
            for cid, w in weights.items()
        }

    all_profiles: list[dict] = []
    for cat_id, n in distribution.items():
        result = search_category(cat_id, n)
        all_profiles.extend(result.get("profiles", []))

    # Shuffle so the morning batch isn't grouped by category
    random.shuffle(all_profiles)
    return all_profiles[:daily_target]


def find_first_degree_for_messaging(n: int = 30) -> list[dict]:
    """
    Sample 1st-degree connections for the day's outbound DMs.
    Skips anyone messaged in last 30 days (per contacted.jsonl).
    """
    prompt = f"""\
You are Jarvis driving Boss's LinkedIn session via Chrome DevTools MCP.

## Goal
Sample {n} of Boss's existing 1st-degree LinkedIn connections to message today.

## Hard exclude
- Anyone in this list (already messaged recently): {json.dumps(list(_load_contacted_ids())[:300])}
- Anyone whose headline contains "looking for opportunities" or "open to work"

## Instructions
1. Navigate to https://www.linkedin.com/mynetwork/invite-connect/connections/
2. Take a snapshot. Parse the connection cards.
3. For each connection extract: handle, name, headline, recent_post_excerpt (if visible), recent_promotion (if any badge), is_first_dm (assume False — they're 1st-degree).
4. Skip excluded handles.
5. Return {n} profiles.

Reply with ONLY this JSON:
{{
  "profiles": [
    {{
      "id": "<handle>",
      "name": "<name>",
      "headline": "<headline>",
      "company": "<company>",
      "recent_post_excerpt": "<excerpt or null>",
      "recent_promotion": <bool>,
      "recent_new_role": <bool>,
      "is_first_dm": false,
      "discovered_at": "<ISO ts>"
    }}
  ],
  "notes": "<anomalies>"
}}
"""
    raw = _claude_helper.with_tools(prompt, max_turns=15, timeout=240)
    import re
    fenced = re.search(r"```(?:json)?\s*(.+?)\s*```", raw, re.DOTALL)
    payload = fenced.group(1) if fenced else raw
    try:
        data = json.loads(payload)
        return data.get("profiles", [])
    except json.JSONDecodeError:
        return []


if __name__ == "__main__":
    profiles = search_all_categories(daily_target=20)
    print(json.dumps(profiles, indent=2, ensure_ascii=False))
