# cycles_v2 — Cyclical Research-and-Build System

## Purpose

Structured research-then-build loop for Tata Steel Round 1 defect detection.
Each cycle runs 15 parallel research agents (Phase A), synthesises hypotheses,
implements the most promising new technique (Phase B-E), evaluates against
6 hard gate sets, and either banks the new best or rejects the build.

**Banked best:** V4, LB = 56.98 (as of 2026-05-23)

## Plan document

`/home/ujjwal/.claude/plans/ab-mai-chata-hu-distributed-bunny.md`

---

## Directory layout

```
cycles_v2/
├── README.md                  # this file
├── submission_budget.json     # daily HE submission limit tracker
├── _fixtures/
│   ├── hard7.csv              # 7 most-precarious true defects (lowest V4 OOF proba)
│   ├── hard_fp10.csv          # 10 hardest false positives (highest V4 OOF proba on Y=0)
│   ├── easy59.csv             # 59 solidly-caught true defects (regression guard)
│   ├── test_cases.yaml        # gate definitions (thresholds, CI requirements, formulas)
│   └── EXHAUSTED_v1_v22.md   # auto-reject contract: all techniques tried in V1-V22
├── cycle_1/
│   ├── research_*.md          # per-agent research output (15 agents, Phase A)
│   ├── synthesis.md           # synthesized hypotheses + ranked candidates
│   └── test_report_v*.md     # gate report from test_case_checker.py
└── cycle_N/                   # subsequent cycles follow same structure
```

---

## How to run a cycle

### Phase A — Research (15 parallel agents)

Dispatch 15 research agents with `EXHAUSTED_v1_v22.md` as the auto-reject contract.
Each agent searches a distinct hypothesis space (new architectures, features from
metallurgical literature, semi-supervised methods not yet tried, etc.).
Agents must justify why their suggestion is NOT in EXHAUSTED and why it would
specifically separate the Hard-7 CoilIDs.

### Phase B — Synthesis

Read all 15 research outputs. Filter against EXHAUSTED. Score remaining candidates
by plausibility × expected lift. Pick the top 1-3 to implement.

### Phase C — Implementation

Build the new model in `../build_vN/`. The build must:
- Produce `oof_vN.parquet` with CoilID + oof_proba columns (or row-aligned to train_v4)
- Produce `chosen_threshold_vN.json` with key `chosen_threshold`

### Phase D — Gate evaluation

```bash
cd /home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1/

python ml_harness/utils/test_case_checker.py \
  --oof build_vN/oof_vN.parquet \
  --threshold build_vN/chosen_threshold_vN.json \
  --fixtures cycles_v2/_fixtures/ \
  --out cycles_v2/cycle_K/test_report_vN.md

echo "Exit code = number of failed gates (0 = all pass)"
```

**Expected gates for a build to be submittable:**
- Set A: Hard-7 — at least 1/7 precarious defects above 0.5 × v4_threshold
- Set B: Hard-FP-10 — at least 5/10 hard FPs below new_threshold
- Set C: Easy-59 — at least 58/59 solidly-caught defects still caught (regression guard)
- Set D: OOF score >= 54.31 AND bootstrap 95% CI lower >= 53.0
- Set E: Stability std <= 1.5 across 5 × 80% subsamples
- Set F: Calibrated LB estimate (OOF + 2.67) >= 56.98

### Phase E — Submission decision

Only submit if:
1. Gates D + F both pass (actual improvement over V4)
2. `submission_budget.json` today_remaining > 0
3. Build is a single model (no mean-blend — V10 blend disaster: actual LB 47.00 vs OOF estimate 58.14)

Update `submission_budget.json` after each HE submission.

### Phase F — Cycle close

If gates pass and submission improves LB: update `banked_lb` in submission_budget.json.
Add new build to EXHAUSTED if it failed (so next cycle doesn't re-try it).
Start next cycle.

---

## Fixtures explained

### hard7.csv
The 7 Y=1 coils with the LOWEST V4 OOF probability. These are "precarious" — V4
catches them but barely. A new model that improves precision may accidentally drop
these. Gate Set A ensures we don't forget them entirely.

### hard_fp10.csv
The 10 Y=0 coils with the HIGHEST V4 OOF probability. These are the hardest false
positives — V4 is very confident they're defects even though they're not. A better
model should assign them lower probability. Gate Set B measures FP improvement.

### easy59.csv
The 59 Y=1 coils with HIGH V4 OOF probability (solidly caught). A new model must
continue catching at least 58/59 of these or it has regressed on the core signal.
Gate Set C is the regression guard.

### test_cases.yaml
Machine-readable gate definitions used by `test_case_checker.py`. Do not edit
thresholds without updating the gate checker logic.

### EXHAUSTED_v1_v22.md
The canonical auto-reject contract. Sourced from all V1-V22 build reports, CYCLE_LOG,
FINAL_VERDICT, and 4 cycle-track reports. Every research agent reads this before
generating hypotheses. Any recommendation matching an EXHAUSTED line is rejected
at synthesis time without implementation.
