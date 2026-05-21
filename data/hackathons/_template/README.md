# Hackathon War Room — folder template

This folder is the per-hackathon workspace produced by `scripts/hackathon_warroom.py`.
Each new hackathon gets its own copy at `data/hackathons/{slug}/`.

## Structure

```
{slug}/
├── canonical_state.json         single source of truth — state machine + Input Contract + decisions
├── checkpoint_log.md            append-only log of every Boss decision at each checkpoint
├── phase_1_research/
│   ├── company_intelligence_report.md
│   └── hackathon_intelligence_report.md
├── phase_2_problems.md          10 scored problem opportunities
├── phase_3_solutions/
│   └── problem_<id>.md          deep solution research per shortlisted problem
├── phase_4_risk_register.md     critique output
├── war_room.md                  final consolidated War Room Document (Phase 5)
└── agent_outputs/
    └── <phase>-<agent_id>.yml   raw YAML handoff outputs (audit trail)
```

## Lifecycle

1. `scripts/hackathon_warroom.py <slug>` creates this folder from `_template/`
2. Workflow runner fills `canonical_state.json` as Phase 0 (Input Contract)
3. Each phase appends to its files + bumps `current_phase` in state
4. Checkpoint pauses persist state and wait for Boss reply
5. Phase 5 produces `war_room.md` and marks state `current_phase: "done"`

## Resuming

`scripts/hackathon_warroom.py --resume <slug>` reads `canonical_state.json` and continues from the saved checkpoint.

## Telegram

Boss controls the workflow via:
- `/wr_start <slug>` — begin a hackathon
- `/wr_status [slug]` — current phase, checkpoint state
- `/wr_checkpoint approve|drill|skip` — advance from a checkpoint
- `/wr_pick <ids>` — Phase 2 shortlist, Phase 3 selection
- `/wr_resume <slug>` — resume a paused workflow
