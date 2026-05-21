# Per-Project SDLC Runbook — Phases 3.1 → 3.7

Operational runbook Jarvis follows for every project (P1 → P10). Each step has explicit inputs, outputs, agent dispatch list, and gate criteria.

---

## Phase 3.1 — Deep Research (research-first per CLAUDE.md mandate)

**Goal**: Build `<current_2026_landscape>` block that gets injected verbatim into every downstream builder brief. Defends against generic / stale-pattern outputs.

**Agents dispatched (parallel)**:
- `research-agent` → SOTA_LANDSCAPE.md (RAG stack + APIs + safety patterns + eval framework + perf budget)
- `ui-ux-designer-agent` → UI_UX_BRIEF.md (2026 reference sites, design tokens, flow map, component states, a11y, anti-patterns)

**Inputs**: project card from ROADMAP.md + candidate YAML from `research/candidates-<domain>.yaml`

**Outputs**:
- `projects/Pn-<slug>/research/SOTA_LANDSCAPE.md`
- `projects/Pn-<slug>/research/UI_UX_BRIEF.md`

**Gate**: both files present + each ≥ 8 sections covered + concrete URLs cited.

**Estimated time**: 30-45 min (background parallel) · Cost: ~$2

---

## Phase 3.2 — Architecture & Prompt Design

**Goal**: Synthesize research into a build-ready architecture spec + agent prompts. This is Jarvis's synthesis step — NOT delegated.

**Inputs**: Phase 3.1 outputs + project card + governance docs

**Outputs**:
- `projects/Pn-<slug>/ARCHITECTURE.md` — system diagram, data flow, RAG pipeline, infra choices, env vars list, eval-suite design
- `projects/Pn-<slug>/PROMPTS.md` — every system prompt the product uses, ≤200 words each, with refusal patterns + structured-output schemas inlined
- `projects/Pn-<slug>/DATA_PLAN.md` — ingestion plan (sources, chunking, embedding, scheduling)
- `projects/Pn-<slug>/EVAL_PLAN.md` — golden-set design (≥30 questions), Ragas thresholds, eval-runner cron

**Gate**: Jarvis self-review against governance + critic-agent (`code-agent` in spec-review mode) PASS

**Estimated time**: 20-30 min · Cost: ~$1

---

## Phase 3.3 — Multi-Agent Build (parallel, each paired with critic)

**Goal**: Ship working code/spec for every layer of the product.

**Parallel agent fan-out** (dispatched same message, each gets the synthesized brief + governance + research blob):

| Builder | Deliverable | Critic |
|---------|-------------|--------|
| `data-engineer-agent` | corpus ingestion script (chunking, embedding, upsert to vector DB) | `code-agent` (data-quality + idempotency) |
| `ml-engineer-agent` | RAG pipeline (hybrid search + rerank + generation + citation enforcement) | `code-agent` (ML correctness) |
| `backend-engineer-agent` | API routes (Edge or Node) + auth + rate-limit + error envelopes | `code-agent` (security + API design) |
| `frontend-engineer-agent` | Next.js 15 UI (RSC + Server Actions + streaming + a11y) | `code-agent` (frontend a11y + CWV) |
| `prompt-engineer-agent` | tighten all prompts, injection defenses, structured outputs | `prompt-engineer-agent` sibling |

**Per-builder loop** (critic-pair):
1. Builder produces artifact
2. Critic reviews → PASS or REVISE with `must_fix`
3. If REVISE: builder fixes, re-submits (max 3 iters; on 3rd escalate to Jarvis)
4. On PASS: artifact merged into project repo

**Outputs**: working code in the project repo (separate folder: `/home/ujjwal/Documents/rag-decathlon-projects/Pn-<slug>/`)

**Gate**: all 5 critics PASS

**Estimated time**: 2-4 hrs (parallel build) · Cost: $3-4

---

## Phase 3.4 — 10-User Simulation Test

**Goal**: Find real-world failures before deploy.

**Inputs**: deployed local URL + `_shared/USER_SIMULATOR_PERSONAS.md`

**Agents**: 10 parallel persona agents (general-purpose, each given one persona + the target URL)

**Outputs**:
- `user-sims/Pn/persona-01.json` ... `persona-10.json`
- `user-sims/Pn/aggregate-report.md` (bug list with severities, UX critiques, trust verdicts)

**Gate**: 0 P0 + 0 P1 bugs across all 10 personas

**Estimated time**: 30-45 min · Cost: ~$2

---

## Phase 3.5 — Iterate Until Clean

**Goal**: Fix every P0/P1 from Phase 3.4 → re-run sims → repeat until clean.

**Process**:
1. Aggregate P0+P1 bug list
2. Route fixes back to relevant builder (ml/backend/frontend/etc.)
3. Each fix paired with critic-agent re-review
4. Re-deploy locally
5. Re-run Phase 3.4 (full 10-persona sweep)
6. Loop

**Max iterations**: 5. If still bugs after 5 iterations, escalate to Jarvis for architecture re-think.

**Estimated time**: 30 min - 2 hrs · Cost: $1-3

---

## Phase 3.6 — Deploy

**Goal**: Public GitHub + live Vercel URL.

**Steps** (Tier-3 confirm = Boss must approve, since this is public-publish):
1. Create public GitHub repo (visibility audit: no .env, no secrets, no PII data)
2. Push polished README with demo GIF
3. Connect repo to Vercel (use Boss's existing Vercel account)
4. Set env vars in Vercel dashboard (Tier-3 confirm — Boss pastes API keys; we never see them in logs)
5. Deploy
6. Verify live URL with smoke test
7. Update `data/projects/rag-decathlon/projects/Pn-<slug>/deploy/DEPLOY_LOG.md` with timestamps + URLs

**Gate**: Live URL returns 200 + key user flows work end-to-end on the deployed URL

**Estimated time**: 15-30 min · Cost: minimal

---

## Phase 3.7 — Postmortem & Case Study

**Goal**: Capture lessons for Pn+1 and write portfolio-ready case study.

**Outputs**:
- `projects/Pn-<slug>/POSTMORTEM.md` — what worked, what hurt, lessons applied to next project
- `data/outputs/portfolio/rag-decathlon/Pn.md` — 1-page case study (problem, approach, results, lessons, screenshots)

**Estimated time**: 15 min · Cost: ~$0.50

---

## Project Definition-of-Done Checklist

Run this before marking project complete:

- [ ] All 7 phases complete (3.1 → 3.7)
- [ ] GitHub repo public
- [ ] Vercel URL live + smoke-tested
- [ ] README includes: hero, problem, demo GIF, arch diagram, stack, run-locally, license
- [ ] All 10 personas: 0 P0 + 0 P1 bugs
- [ ] Eval suite passes (Faithfulness ≥0.85, AR ≥0.80, CP ≥0.75)
- [ ] Critic pass on every builder output
- [ ] Case study added to portfolio outputs folder
- [ ] POSTMORTEM.md saved
- [ ] Boss notified with URL + recruiter pitch

---

## Cost-and-time-tracking per project

| Phase | Time | Cost |
|-------|------|------|
| 3.1 Research | 30-45 min | $2 |
| 3.2 Architecture | 20-30 min | $1 |
| 3.3 Build (parallel) | 2-4 hrs | $3-4 |
| 3.4 User-sim test | 30-45 min | $2 |
| 3.5 Iterate | 30 min - 2 hrs | $1-3 |
| 3.6 Deploy | 15-30 min | minimal |
| 3.7 Postmortem | 15 min | $0.50 |
| **TOTAL** | **4-8 hrs active** | **~$8** |

Stays within Boss's $8/project + 8hr budget cap. If a project trips a cap → status `blocked` + escalate.

---

## Speculative parallelism (Jarvis discretion)

While project Pn is in Phase 3.3 build (which runs 2-4 hrs in background), Jarvis MAY:
- Kick off Pn+1 Phase 3.1 (deep research) in parallel
- This way 2 projects always in flight; effective throughput doubles
- Cost discipline: never have more than 2 projects in simultaneous research-or-build

This is enabled by Boss's fullauto mode + parallel-default working style.
