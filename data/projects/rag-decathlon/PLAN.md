# RAG Decathlon — 10 Production-Grade RAG Projects

**Owner**: Boss (Ujjawal Shrivastav)
**Executor**: Jarvis (fullauto mode)
**Started**: 2026-05-14
**Output bar**: "isse behtar kuch ban hi nahi sakta" — best-in-class, not template-tier.

---

## Mission

Build 10 deployed, polished, portfolio-grade RAG products that solve REAL 2026-trending problems. Each project must:

1. Be better than the previous (difficulty curve = adds a new 2026 RAG technique)
2. Solve a real, current pain — not a toy demo
3. Use SOTA 2026 RAG patterns (hybrid search, rerankers, GraphRAG, agentic RAG, multimodal, memory)
4. Ship to GitHub (public repo with clean README + arch diagram + demo GIF) + Vercel (clean subdomain)
5. Pass a 10-user-simulator stress test before deploy
6. Have a 1-page case study for portfolio + LinkedIn

## Boss's Goals (verbatim, paraphrased)

- Portfolio ko impove kre — recruiters ko bhejne layak
- Jarvis ki learning + build skill behtar ho
- Pehle research → requirements → prompt + subagent design → SDLC → critic loop → 10-user sim testing → iterate till clean → GitHub + Vercel
- Fullauto mode, full access — but plan-first, never raw execution

## The 5-Phase Master Plan

### Phase 0 — Setup (2026-05-14, complete by EOD)
- [x] Switch auto-mode → fullauto
- [x] Scaffold `data/projects/rag-decathlon/`
- [x] Write PLAN.md (this file)
- [ ] Dispatch Phase 1 research agents

### Phase 1 — Discovery (parallel, ~30 min)
8 research agents in parallel, each scouting one domain for 5 candidate 2026 RAG problems → **40 candidates total**.

Domains:
1. Developer tooling & DevX
2. Healthcare & wellness
3. Education & tutoring
4. Legal & compliance
5. Finance & investing
6. Enterprise knowledge & productivity
7. Creative writing & media
8. Agentic / autonomous workflows

Output: `research/candidates-{domain}.yaml` × 8 → aggregated to `candidates/all-40.yaml`.

### Phase 2 — Selection & Roadmap
Score 40 candidates by: **impact × novelty × portfolio-leverage × technical-stretch × buildability**. Pick top 10 ordered by difficulty curve.

Output: `roadmap/ROADMAP.md` with 10 Project Cards (problem, users, why-now, tech, data, success criteria, RAG technique).

**Gate**: Boss reviews + can swap any project before Phase 3 kicks off.

### Phase 3 — Per-Project SDLC (×10, sequential)
For each project, in order:

**3.1 Deep-Research**: research-agent + ml-engineer-agent — current SOTA, reference apps, exact stack, anti-patterns. Output: `projects/Pn/RESEARCH.md`.

**3.2 Architecture & Prompt Design**: ml-engineer + prompt-engineer + backend-engineer — system architecture, RAG pipeline diagram, agent prompts (each ≤200 words, tightly scoped). Output: `projects/Pn/ARCHITECTURE.md`, `projects/Pn/PROMPTS.md`.

**3.3 Multi-Agent Build**:
- `ml-engineer-agent` — RAG pipeline (ingestion, embedding, retrieval, reranker, generation)
- `data-engineer-agent` — corpus ingestion + chunking strategy
- `backend-engineer-agent` — FastAPI/Next-API routes + auth + rate limit
- `frontend-engineer-agent` — Next.js 15 UI (Tailwind 4 + shadcn/ui v4)
- `ui-ux-designer-agent` — design tokens + flow + a11y
- **Each paired with a `code-agent`-driven CRITIC pass** — review the builder's output, flag issues, force fix-iteration before progress.

**3.4 10-User Simulation Test**: 10 parallel personas (skeptic, power-user, novice, mobile-user, accessibility-user, edge-case-poker, multilingual-user, expert-domain, lazy-typer, hostile-tester) each exercise the product. Output: `user-sims/Pn/reviews.json`. Bugs aggregated by P0/P1/P2.

**3.5 Iterate Until Clean**: Fix root cause of every P0/P1 bug. Re-run sims. Loop until ZERO P0/P1 issues.

**3.6 Deploy**:
- GitHub: public repo, polished README, arch diagram, demo GIF, license
- Vercel: clean subdomain (`{project-slug}.vercel.app`)
- Portfolio: 1-pager case study added

**3.7 Postmortem & Lessons**: `projects/Pn/POSTMORTEM.md` — what worked, what hurt, what to apply to Pn+1.

### Phase 4 — Portfolio Roll-up
Showcase site indexing all 10 RAG products → linked from main portfolio + resume + LinkedIn.

---

## Governance Rules (locked, non-negotiable)

1. **Plan-before-code per project**. No improv. Architecture doc must exist before any code agent ships code.
2. **Research-first per CLAUDE.md build workflow mandate**. Specialist receives `<current_2026_landscape>` block verbatim.
3. **2026-trending only**. Reject any candidate that screams 2022/saturated (basic doc Q&A, generic ChatGPT wrapper).
4. **Difficulty curve**: each project adds a new technique vs the previous (P1 = vanilla + hybrid; P10 = multi-agent + GraphRAG + memory + multimodal).
5. **Critic-loop per builder agent**. No agent output ships unreviewed.
6. **10-user-sim stress test** mandatory before Vercel deploy.
7. **GitHub + Vercel deploy** = definition of "done." No project is done until URL is live.
8. **Per-project budget caps**: $8 LLM spend, 8 hours active build time. Soft-fail beyond.
9. **Tata Steel hackathon priority window May 22+**. Pause decathlon during sacred build slots if conflict.
10. **Boss interruption protocol**: surface ONLY at —
    - Phase 2 Roadmap approval
    - Hard blocker (cost overrun, irreversible decision, data access failure)
    - Project completion (deploy URL + case study link)
    - Phase 4 portfolio roll-up

## Cost & Time Estimates (honest)

- Phase 1 research: ~30 min, ~$3 LLM
- Phase 2 ranking: ~15 min, ~$1
- Per-project Phase 3: 4-8 hours active, $5-$8 LLM
- 10 projects: ~50-80 hours active, ~$60-80 LLM
- **Realistic calendar**: 2-3 projects/day burndown = ~5-7 days for all 10 if Boss available for go/no-go gates.

## Stack Defaults (2026)

- **Frontend**: Next.js 15 (App Router) + React 19 + Tailwind 4 + shadcn/ui v4
- **Backend**: Next.js API routes OR FastAPI (Vercel Python) — chosen per project
- **Vector DB**: Pinecone serverless / Supabase Vector / Upstash Vector (per Vercel friendliness)
- **Embeddings**: Voyage-3 / OpenAI text-embedding-3-large / Cohere embed-v4
- **Reranker**: Cohere Rerank 3 / Voyage Rerank-2
- **LLMs**: Claude Sonnet 4.6 default + Haiku 4.5 for cheap eval/critic
- **Eval**: Ragas + custom eval harness per project
- **Observability**: LangSmith OR Braintrust OR self-rolled

Per-project deviations allowed if research justifies.

## Anti-Patterns (forbidden)

- Generic "chat with my PDF" without a novel angle
- Vanilla RAG with no reranker / no eval / no error-handling
- Demo that breaks on second query
- Hardcoded API keys / leaked secrets
- README without arch diagram + demo
- Vercel deploy that 500s on cold start
- Promising "agentic" but actually being a single LLM call

## Status

- **Current phase**: Phase 1 (Discovery)
- **Last update**: 2026-05-14
