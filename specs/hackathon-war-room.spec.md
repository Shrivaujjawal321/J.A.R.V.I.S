# Spec: Hackathon War Room

**Status:** active
**Owner:** `.claude/skills/hackathon-war-room/`, `scripts/hackathon_warroom.py`,
`.claude/agents/{company-tech-stack-researcher,company-ai-ml-researcher,hackathon-intel-researcher,mandatory-tech-deep-dive,hackathon-critique}-agent.md`
**Last reviewed:** 2026-05-13

## Purpose

Convert a `(company, hackathon, team)` brief into a fully-researched, judge-optimised, build-ready project plan via a sequential 5-phase multi-agent workflow with user checkpoints between phases. Output: a single "War Room Document" + canonical state file that can resume across sessions.

Replaces ad-hoc hackathon planning. Provides a contract-driven workflow with verification, scoring, conflict surfacing, and rejection power. Optimises against seven explicit targets: innovation, technical depth, judge appeal, scalability, real-world impact, demo quality, business potential.

## Inputs (the Input Contract — see Layer 0)

Required before any Phase 1 agent runs. If anything missing, halt and ask ONE consolidated question listing every missing field.

| Field | Required | Notes |
|---|---|---|
| `COMPANY.name` | yes | Official name |
| `COMPANY.url` | yes | Primary website |
| `COMPANY.focus` | optional | Specific product line or BU |
| `HACKATHON.url` | yes | Official page |
| `HACKATHON.problem_statements` | yes | Verbatim text or link |
| `HACKATHON.deadline` | yes | ISO date + timezone |
| `HACKATHON.team_size` | yes | Min/max |
| `HACKATHON.required_tech` | yes | "none" allowed |
| `HACKATHON.judging_rubric` | optional, preferred | Verbatim if published |
| `TEAM.roles` | yes | Available roles + headcount |
| `TEAM.skill_levels` | yes | Per role: junior / mid / senior |
| `TEAM.time_budget_hours` | yes | Total person-hours |
| `TEAM.domain_experience` | optional | Prior industry work |
| `CONSTRAINTS.budget` | yes | $ or "none" |
| `CONSTRAINTS.cloud_credits` | optional | Provider + amount |
| `CONSTRAINTS.ip_rules` | optional | Open-source mandates |

## Outputs

| Name | Type | Location |
|---|---|---|
| Canonical state | JSON | `data/hackathons/{slug}/canonical_state.json` |
| Per-agent outputs (yaml schema) | YAML files | `data/hackathons/{slug}/agent_outputs/{phase}-{agent_id}.yml` |
| Phase reports | Markdown | `data/hackathons/{slug}/phase_{n}_*.md` |
| Checkpoint log | Markdown (append-only) | `data/hackathons/{slug}/checkpoint_log.md` |
| War Room Document | Markdown | `data/hackathons/{slug}/war_room.md` |
| Telegram digests | sent | per checkpoint |

## Execution flow (phases)

```
Phase 0 — INPUT CONTRACT  (validate, halt-if-missing)
   ↓
Phase 1 — RESEARCH        7 agents parallel (5 company + 2 hackathon)
   → CHECKPOINT 1         Boss: approve / drill / skip
Phase 2 — PROBLEM DISCOVERY  3 agents → 10 scored problems
   → CHECKPOINT 2         Boss picks 2-3
Phase 3 — SOLUTION RESEARCH  4 agents × N shortlisted, parallel within problem
   → CHECKPOINT 3         Boss picks 1
Phase 4 — VALIDATION      1 critique agent, REJECT-power
   → (automatic gate; loops back to Phase 3 if rejected)
Phase 5 — BUILD PLAN      Final War Room Document
   → DELIVERABLE
```

Each phase emits ONE consolidated document. The Daemon merges + resolves conflicts before presenting; raw agent outputs never stream to Boss.

## Behavioural contract

- MUST halt if any Input Contract field is missing and ask ONE consolidated question
- MUST run Phase 1 agents in PARALLEL (asyncio.gather) — never serial
- MUST enforce checkpoint gates — no phase advances without Boss confirmation via Telegram (`/wr_checkpoint approve|drill|skip` or `/wr_pick <ids>`)
- MUST persist canonical_state.json after every phase / agent output
- MUST resume cleanly across daemon restarts using canonical_state.json
- MUST tag any unverified claim with `[unverified]` AND any low-confidence claim (<0.6) with `[low-confidence]`
- MUST refuse silent conflict resolution — surface disagreement between agents with both positions
- MUST cap composite-score rubric at 1-10 with anchored definitions per dimension
- MUST allow the Critique Agent to REJECT a Phase 3 solution and loop back if composite < 6.5
- MUST emit per-agent output in the standard YAML handoff schema (Layer 5)
- MUST refuse to produce partial War Room Document — full or nothing
- MUST honour `JARVIS_WARROOM_ENABLED=0` kill-switch
- MUST NEVER auto-submit or auto-publish — Tier-3 confirm for any external action

## Scoring rubrics (anchored, 1-10)

**Innovation**
- 1 — Direct clone
- 5 — Novel combination of known tech
- 10 — Capability that does not exist anywhere in production

**Judge Appeal**
- 1 — Needs extended explanation
- 5 — Value clear in 60-second demo
- 10 — Audible/visible judge reaction in first 30 seconds

**Feasibility** (relative to team.time_budget_hours)
- 1 — Requires >2× available person-hours
- 5 — Achievable at ~80% of available
- 10 — MVP in <40% of available, leaving polish time

**Technical Depth**
- 1 — CRUD app, no non-trivial systems work
- 5 — Real ML/distributed/systems component, standard patterns
- 10 — Novel architecture, custom models, systems-level innovation

**Business Potential**
- 1 — No revenue / adoption path
- 5 — Plausible product with identifiable buyer
- 10 — Investor-fundable; clear ICP, willingness to pay, defensible moat

**Composite** = weighted average. Defaults: Innovation 0.20, Judge Appeal 0.25, Feasibility 0.25, Technical Depth 0.15, Business Potential 0.15. Daemon may re-weight based on judging rubric and MUST state the new weights.

## Inter-agent handoff schema (YAML — Daemon refuses non-conforming)

```yaml
agent_id: <string>
phase: <0-5>
summary: <≤200 words>
findings:
  - claim: <string>
    evidence: <source URL or "[unverified]">
    confidence: <0.0-1.0>
open_questions: [<string>, ...]
assumptions: [<string>, ...]
recommendations: [<string>, ...]
handoff_to: [<agent_id>, ...]
blockers: [<string>, ...]
```

## Agent roster per phase

### Phase 1 — Research (7 parallel)

Company (5):
- `research-analyst-agent` — Identity, market, business model, revenue
- `company-tech-stack-researcher-agent` — Engineering stack signals, infra, APIs, security posture (NEW)
- `company-ai-ml-researcher-agent` — AI/ML initiatives, papers, hosted models, AI product surface (NEW)
- `investigative-journalist-agent` — Pain points, public incidents, hiring weakness signals, customer complaints
- `librarian-research-assistant-agent` — Sources curation, competitor landscape, controlled-vocab search

Hackathon (2):
- `hackathon-intel-researcher-agent` — Rules, scoring, judges, past winners (NEW)
- `mandatory-tech-deep-dive-agent` — For every required SDK/API: advanced features + hidden capabilities + integration patterns (NEW)

### Phase 2 — Problem Discovery (3 agents)

- `product-manager-agent` — JTBD-driven problem ideation
- `strategy-consultant-agent` — SCQ + pain-severity scoring + steel-man counter
- `hackathon-agent` — Composite scoring + alignment with hackathon theme

### Phase 3 — Solution Research (4 agents × N problems)

For each shortlisted problem in parallel:
- `backend-engineer-agent` — Architecture + APIs + system design
- `frontend-engineer-agent` (or `mobile-developer-agent` if mobile) — UI + UX architecture
- `ml-engineer-agent` — Model choice, fine-tune vs prompt vs RAG vs agentic
- `data-engineer-agent` — Datasets, pipelines, realism for demo

Co-opted as needed:
- `devops-sre-agent` — Deployment topology for scaling claim
- `security-engineer-agent` — If security-critical
- `statistician-agent` — Evaluation method

### Phase 4 — Validation (1 agent + reject-power)

- `hackathon-critique-agent` (NEW) — Risk register, weak assumptions, demo failure modes, judge-appeal gaps, reject-power if composite < 6.5

### Phase 5 — Build Plan (synthesis)

- `product-manager-agent` — PRD-style final spec
- `technical-writer-agent` — War Room Document final compose
- `pitch-deck-consultant-agent` — Demo + slide narrative
- `qa-test-engineer-agent` — Test + demo dry-run plan

### Layer 6 — Prompt Engineer

- `prompt-engineer-agent` — On underperformance (validation reject ×2), revises per-agent operating prompts

## Verification & failure-mode discipline

- Every claim about API / library version / pricing / company fact / judge identity / hackathon rule MUST cite source URL or `[unverified]` tag
- Confidence < 0.6 → `[low-confidence]` tag in user-facing output
- Hackathon rule ambiguous → flag to user with proposed interpretations; do not guess
- Two agents disagree → Daemon surfaces both; does not pick silently
- Sources weak/contradictory → confidence < 0.6; do not synthesise past evidence
- Scope > time budget → flag with revised scope options before producing plan

## State machine (canonical_state.json shape)

```json
{
  "version": 1,
  "slug": "<hackathon-slug>",
  "started_at": "<iso>",
  "current_phase": 0|1|2|3|4|5|"done",
  "current_checkpoint": null|"1"|"2"|"3"|"awaiting_pick",
  "input_contract": { ... full §1 fields ... },
  "phase_outputs": {
    "1": { "agent_outputs": [...], "report_path": "...", "completed_at": "..." },
    ...
  },
  "shortlisted_problem_ids": [],
  "selected_problem_id": null,
  "scoring_weights": { ... },
  "decisions": [ ... append-only ... ],
  "errors": [ ... ],
  "telegram_chat_id": null
}
```

## Failure modes

| Failure | Response |
|---|---|
| Input Contract field missing | Halt; one consolidated question |
| Phase 1 agent raises / fails | Mark agent output with error, continue with remaining 6; flag in checkpoint digest |
| Phase 1 conflict between agents | Both surface in checkpoint digest; Boss adjudicates |
| Boss times out on checkpoint (>72h) | Reminder Telegram nudge; pause indefinitely until reply |
| Critique Agent rejects ×2 | Prompt Engineer revises Phase 3 prompts and re-runs |
| Scope > time budget | Surface revised scope options; do not auto-trim |
| Required tech non-functional / deprecated | Halt; surface to Boss |
| canonical_state.json corrupt | Backup → reset to last valid phase output |

## Eval cases

`data/evals/hackathon-war-room/test_cases.jsonl` covers:

1. Input Contract complete → Phase 1 runs all 7 agents
2. Input Contract missing 2 fields → halt + consolidated question
3. Phase 1 agent timeout → graceful degrade, partial report
4. Checkpoint approval received → Phase 2 starts
5. Conflict surfacing → both positions visible in digest
6. Critique Agent reject → Phase 3 loop
7. Resume across daemon restart → state.json restores cleanly

## Non-goals

- Does NOT auto-submit to hackathon platforms (Tier-3 confirm required)
- Does NOT generate code beyond architecture skeletons (build phase is human-led, agents support)
- Does NOT replace `hackathon-agent` general slash command — War Room is for full deep workflow
- Does NOT do multi-user (single Boss)
- Does NOT make purchases (cloud credits etc.)

## Dependencies

- Code: `jarvis_core/orchestrator.py:run_worker()` + `run_parallel_workers()`
- Code: `bridge/telegram_bridge.py` for `/wr_*` commands
- Data: `data/hackathons/{slug}/` per-hackathon state
- Env vars: `JARVIS_WARROOM_ENABLED` (default 1), `JARVIS_WARROOM_MODEL` (default `claude-sonnet-4-6`)
- Agents: 5 new (listed above) + 15+ reused Tier-1/2 specialists

## Termination conditions

Stop and ask Boss when:
- Any Input Contract field missing
- Any checkpoint reached
- Two agents disagree on material decision
- Critique Agent rejects Phase 3
- Scope exceeds time budget
- Required technology non-functional / deprecated / blocked

Never:
- Stop mid-phase
- Summarise prematurely
- Output partial War Room Document

## Changelog

- 2026-05-13: Initial spec drafted from Boss's pasted War Room system prompt
