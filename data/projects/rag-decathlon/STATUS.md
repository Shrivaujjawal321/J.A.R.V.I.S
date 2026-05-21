# RAG Decathlon — Live Status Dashboard

> Source of truth for which projects are at which phase. Jarvis updates after every status transition.

**Last updated**: 2026-05-14
**Mode**: fullauto
**Active in parallel**: P1 (research), P2 (research speculative-parallel)

---

## Phase Tracker

| # | Phase | Status |
|---|-------|--------|
| Phase 0 | Setup | ✅ Complete |
| Phase 1 | Discovery (40 candidates) | ✅ Complete |
| Phase 2 | Selection & Roadmap | ✅ Complete (approved by Boss) |
| Phase 3 | Per-project SDLC × 10 | 🔄 In progress (P1 + P2 active) |
| Phase 4 | Portfolio roll-up | ⏳ Pending |

---

## Project Tracker (P1 → P10)

| # | Slug | Domain | Technique | Phase 3.x | Status | Live URL |
|---|------|--------|-----------|-----------|--------|----------|
| **P1** | `glp1-nutrition-copilot` | Healthcare | Hybrid + rerank | 3.3 Build ✅ → 3.4 awaiting install | 🟢 Awaits Boss `pnpm install` | — |
| **P2** | `sebi-drhp-redflag-radar` | Finance 🇮🇳 | Agentic + section-aware | 3.1 Research ✅ (SOTA done; UI/UX pending) | 🔄 | — |
| **P3** | `promptwatch` | DevTools | Memory-augmented + CI | — | ⏳ Queued | — |
| **P4** | `mcp-sentinel` | DevTools/Security | Hybrid + structured CVE | — | ⏳ Queued | — |
| **P5** | `claim-auditor` | Media | Multi-source agentic | — | ⏳ Queued | — |
| **P6** | `arxiv-feynman` | Education | Multimodal RAG | — | ⏳ Queued | — |
| **P7** | `cbt-dbt-compass` | Mental Health | Memory + safety | — | ⏳ Queued | — |
| **P8** | `upsc-rag-grader` | Education 🇮🇳 | Agentic claim verify | — | ⏳ Queued | — |
| **P9** | `graphblast` | DevTools | GraphRAG via AST | — | ⏳ Queued | — |
| **P10** | `deallens` | Agentic/VC | Agentic GraphRAG + MA-RAG | — | ⏳ Queued | — |

### Phase-3 sub-phase legend

- **3.1** Deep Research (research-agent + ui-ux-designer-agent)
- **3.2** Architecture & Prompt Design (Jarvis synthesis)
- **3.3** Multi-Agent Build (5 builders × critics, parallel)
- **3.4** 10-User Simulation Test
- **3.5** Iterate Until Clean
- **3.6** Deploy (GitHub + Vercel — Boss approval gate)
- **3.7** Postmortem & Case Study

---

## Budget Watch

| Resource | Budget | Spent | Remaining |
|----------|--------|-------|-----------|
| LLM (Phase 1+2 research) | $80 | ~$10 | $70 |
| Active build time | ~80 hrs | ~2 hrs | ~78 hrs |

---

## Cross-Project Infrastructure

- ✅ `_shared/USER_SIMULATOR_PERSONAS.md` — 10 personas for stress testing
- ✅ `_shared/CRITIC_PROMPT_TEMPLATE.md` — generic critic for every builder
- ✅ `_shared/BUILDER_GOVERNANCE.md` — 2026 stack standards + anti-patterns
- ✅ `_shared/SDLC_RUNBOOK.md` — Phase 3.1-3.7 operational SOP
- ✅ `_shared/README_TEMPLATE.md` — project repo README boilerplate
- ✅ `_shared/CASE_STUDY_TEMPLATE.md` — portfolio entry boilerplate
- ✅ `_shared/EVAL_GOLDEN_SET_SCHEMA.md` — eval-case schema + Ragas gates
- ✅ `/home/ujjwal/Documents/rag-decathlon-projects/` — parent dir for project repos

---

## Active Background Agents

| Agent ID | Project | Task | Started | Status |
|----------|---------|------|---------|--------|
| `a369...` | P1 | SOTA_LANDSCAPE research | 2026-05-14 | 🔄 Running |
| `ab4b...` | P1 | UI_UX_BRIEF research | 2026-05-14 | 🔄 Running |
| `a2ad...` | P2 | SOTA_LANDSCAPE research (speculative) | 2026-05-14 | 🔄 Running |

---

## Conflict Watch

- ⚠️ **Tata Steel sacred build slot starts 2026-05-22** — decathlon WILL pause
- ⚠️ **McpIndex DevNetwork submission 2026-05-28** — P0 wins over decathlon if budget conflict

---

## Boss Approval Gates (Tier-3)

These specifically require Boss confirmation before Jarvis proceeds:

- [ ] P1 GitHub repo public push (Phase 3.6)
- [ ] P1 Vercel env-var setup (Boss pastes keys)
- [ ] Same for P2-P10 deploys (per project)
- [ ] Portfolio site public publish (Phase 4)

Everything else (research, build, critic loops, sim tests, local iteration) runs autopilot per fullauto mode.
