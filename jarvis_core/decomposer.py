"""
Goal decomposer — turns Boss's plain-English goal into N sub-tasks.

Uses Claude Agent SDK with a structured planning prompt. The decomposer is
intentionally single-level (no recursion) — sub-tasks cannot spawn further
sub-tasks. This prevents runaway fan-out.

Output is strict JSON validated against `DecompositionPlan`. If the model
returns garbage, the goal goes to status=FAILED with an explanatory error.

The decomposer should default to the CHEAPEST model that does good
single-turn JSON output. For Claude family that's Haiku.

Tier classification is the decomposer's responsibility:
- Tier 1: pure information work (research, summarize, draft)
- Tier 2: write to Jarvis repo / memory / calendar / notion
- Tier 3: external irreversible action (submit, send, publish, push, delete, pay)
"""
from __future__ import annotations

import json
import logging
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from .models import GoalRecord, SubTaskRecord
from .orchestrator import run_worker

log = logging.getLogger("jarvis_core.decomposer")


# === Planner output schema ===


class PlanItem(BaseModel):
    label: str = Field(..., max_length=80, description="2-5 word label, e.g. 'paper-1-summary'")
    prompt: str = Field(..., min_length=20, max_length=2000)
    tier: int = Field(..., ge=1, le=3)
    reason: str | None = Field(default=None, max_length=400, description="Why this sub-task fits the goal")


class DecompositionPlan(BaseModel):
    plan_summary: str = Field(..., max_length=400)
    sub_tasks: list[PlanItem] = Field(..., min_length=1, max_length=8)


@dataclass
class DecomposeOutcome:
    plan: DecompositionPlan | None
    error: str | None
    cost_usd: float | None
    duration_ms: int | None
    raw_text: str  # Always populated for debugging


# === Planner prompt ===


_PLANNER_SYSTEM = """You are Jarvis's goal-decomposition planner. Your ONE job: take Boss's plain-English goal and return a JSON object with a SHORT plan summary plus 1-8 sub-tasks Claude Code workers can execute in parallel.

You MUST return ONLY valid JSON matching this exact schema (no prose before or after):

```json
{
  "plan_summary": "One short paragraph explaining the plan in plain English (Boss-facing).",
  "sub_tasks": [
    {
      "label": "short-label",
      "prompt": "Full prompt that will be sent to a Claude Code worker. Self-contained — the worker has no other context.",
      "tier": 1,
      "reason": "Optional one-line why this sub-task fits."
    }
  ]
}
```

## Tier classification rules (CRITICAL — get this right)

For each sub-task, pick the LOWEST tier that fits:

- **Tier 1** — pure information work. Reading files, web research, summarization, drafting, computation, screenshot. NO side effects.
- **Tier 2** — local writes inside Jarvis repo. File create/edit (NOT in user home), memory writes, calendar event create, Notion page create, browser form FILL (not submit), local git ops (add/branch/checkout/stash).
- **Tier 3** — irreversible external side effect. Submit a form (LinkedIn Easy Apply submit, Naukri apply submit), send an email, publish to social media, delete data, git push, payment, permission change.

## Hard rules

- If the goal touches Tier 3 actions, the FINAL sub-task should be the Tier 3 one — fill/draft first, then submit/publish/send last. Each Tier 3 sub-task is gated on Boss's morning approval.
- DO NOT decompose into sub-sub-tasks. One level only. If something needs multi-step (research → draft → publish), make 3 sequential sub-tasks at this level.
- Each sub-task prompt MUST be self-contained — the worker sees ONLY that prompt. Include all needed context inline.
- Sub-tasks run in PARALLEL where possible. If sub-task B depends on sub-task A's output, say so in the prompt — but prefer designs where sub-tasks are independent.
- If the goal is malformed, ambiguous, or violates safety (Tier 4 — destruction, phishing, ToS), return:
  ```json
  {"plan_summary": "REFUSED: <reason>", "sub_tasks": []}
  ```
- Aim for 3-6 sub-tasks for a typical research/build goal. 1-2 for a simple goal. Never more than 8.

## Examples

Goal: "Research 3 papers on prompt caching, summarize each in 5 bullets"
Plan: 3 sub-tasks (one per paper), each Tier 1 with prompts like "Search for papers on prompt caching, pick #1 [paper title or query], read abstract + key sections, summarize in 5 bullets covering motivation, method, results, limitations, follow-up."

Goal: "Apply to 3 ML PM jobs on LinkedIn matching my resume"
Plan: 4 sub-tasks — (1) Tier 1: find 3 best-fit jobs via LinkedIn search + job-hunt-agent scoring. (2) Tier 1: tailor cover letter per job. (3) Tier 2: open each job's Easy Apply form, fill via browser-autopilot scout-then-fill (form FILL only). (4) Tier 3: SUBMIT each apply (queued for Boss approval).

Goal: "Plan Anisha's birthday surprise next week"
Plan: 2-3 Tier-1 sub-tasks — gift ideas, restaurant options, message drafts. NO Tier 3 (this is research, not booking).

Return ONLY the JSON. No prose, no apology, no preamble.
"""


def _strip_code_fence(text: str) -> str:
    """Pull JSON out of ```json ... ``` fences if model wraps output."""
    fence_match = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()
    return text.strip()


async def decompose_goal(
    goal: GoalRecord,
    *,
    project_root: Path,
    timeout_seconds: int = 120,
) -> DecomposeOutcome:
    """Run the planner to decompose a goal into sub-tasks."""
    user_prompt = (
        _PLANNER_SYSTEM
        + "\n\n---\n\n"
        + f"## Goal from Boss (id={goal.goal_id})\n\n{goal.description}\n\n"
    )
    if goal.context:
        user_prompt += f"## Context\n```json\n{json.dumps(goal.context, indent=2)}\n```\n\n"
    user_prompt += "Return the JSON plan now. Only JSON, nothing else.\n"

    outcome = await run_worker(
        user_prompt,
        project_root=project_root,
        max_turns=1,
        allowed_tools=[],  # Pure JSON output — no tool use
        timeout_seconds=timeout_seconds,
    )

    raw = outcome.text or ""
    if outcome.error and not raw:
        return DecomposeOutcome(
            plan=None,
            error=outcome.error,
            cost_usd=outcome.cost_usd,
            duration_ms=outcome.duration_ms,
            raw_text="",
        )

    # Parse JSON
    try:
        json_text = _strip_code_fence(raw)
        data = json.loads(json_text)
    except json.JSONDecodeError as e:
        return DecomposeOutcome(
            plan=None,
            error=f"Planner returned invalid JSON: {e}",
            cost_usd=outcome.cost_usd,
            duration_ms=outcome.duration_ms,
            raw_text=raw,
        )

    # Validate schema
    try:
        plan = DecompositionPlan.model_validate(data)
    except ValidationError as e:
        return DecomposeOutcome(
            plan=None,
            error=f"Planner returned JSON not matching schema: {e.errors()[:3]}",
            cost_usd=outcome.cost_usd,
            duration_ms=outcome.duration_ms,
            raw_text=raw,
        )

    # Detect refusal pattern
    if plan.plan_summary.startswith("REFUSED:") and not plan.sub_tasks:
        return DecomposeOutcome(
            plan=plan,
            error=plan.plan_summary,
            cost_usd=outcome.cost_usd,
            duration_ms=outcome.duration_ms,
            raw_text=raw,
        )

    return DecomposeOutcome(
        plan=plan,
        error=None,
        cost_usd=outcome.cost_usd,
        duration_ms=outcome.duration_ms,
        raw_text=raw,
    )


def plan_to_sub_tasks(plan: DecompositionPlan) -> list[SubTaskRecord]:
    """Materialize a DecompositionPlan as SubTaskRecord objects."""
    out: list[SubTaskRecord] = []
    for item in plan.sub_tasks:
        out.append(
            SubTaskRecord(
                sub_id=uuid.uuid4().hex[:10],
                label=item.label,
                prompt=item.prompt,
                tier=item.tier,
            )
        )
    return out


# === Self-test (offline — exercises JSON-shape handling) ===


def _self_test() -> None:
    """Validate the plan parser against canned inputs."""
    raw = """```json
{
  "plan_summary": "Research 3 papers on prompt caching.",
  "sub_tasks": [
    {"label": "paper-1", "prompt": "Find and summarize the first prominent paper on Anthropic prompt caching from 2024-2025. Return 5 bullets covering motivation, method, results, limitations, follow-up.", "tier": 1, "reason": "First key paper"},
    {"label": "paper-2", "prompt": "Find a Google DeepMind paper on KV-cache reuse and summarize in 5 bullets.", "tier": 1},
    {"label": "paper-3", "prompt": "Find a paper on context caching at the inference layer (vLLM PagedAttention or similar) and summarize in 5 bullets.", "tier": 1}
  ]
}
```"""
    text = _strip_code_fence(raw)
    plan = DecompositionPlan.model_validate_json(text)
    assert len(plan.sub_tasks) == 3
    assert plan.sub_tasks[0].tier == 1
    subs = plan_to_sub_tasks(plan)
    assert len(subs) == 3
    assert all(s.sub_id for s in subs)
    print("decomposer self-test: PASS")


if __name__ == "__main__":
    _self_test()
