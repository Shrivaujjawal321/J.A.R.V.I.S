# Case Study — {{PROJECT_NAME}}

> Part of the RAG Decathlon · Project #{{N}} of 10

**Tagline**: {{one-line product description}}
**Live**: [{{VERCEL_URL}}]({{VERCEL_URL}}) · **Code**: [{{GITHUB_URL}}]({{GITHUB_URL}}) · **Built in**: {{X}} hours
**RAG technique**: {{technique}} · **Domain**: {{domain}}
**Recruiter pitch**: *"{{single-line pitch from ROADMAP}}"*

---

## The problem

{{2-3 paragraphs: the documented 2026 pain. Cite Reddit threads, arxiv papers, or competitor failures. Make it visceral — who suffers and what does their day look like?}}

## Why existing tools don't solve it

| Existing tool | Why it falls short |
|---------------|---------------------|
| {{Competitor 1}} | {{Why} |
| {{Competitor 2}} | {{Why}} |
| {{Competitor 3}} | {{Why}} |

## The novel angle

{{1-2 paragraphs: what's specifically new about this approach. Not "AI for X." Pin down the technical or product insight.}}

## Architecture

![arch]({{ARCH_DIAGRAM_URL}})

{{2-3 paragraphs explaining the pipeline. Be concrete about the 2026 SOTA pattern used and WHY it fits the problem.}}

### Key technical decisions

- **{{Decision 1, e.g. Embedding choice}}**: {{Voyage-3-large vs Cohere embed-v4 vs OpenAI text-embedding-3-large. Why we picked X.}}
- **{{Decision 2, e.g. Reranker}}**: {{Cohere Rerank v3 — why}}
- **{{Decision 3, e.g. Chunking}}**: {{Section-aware vs semantic vs naive}}
- **{{Decision 4, e.g. Vector DB}}**: {{Upstash Vector — why Vercel-friendly tradeoff}}
- **{{Decision 5, e.g. Safety}}**: {{Refusal pattern + disclaimer placement}}

## Results

### Eval scores

| Metric | Score | Threshold | Pass? |
|--------|-------|-----------|-------|
| Ragas Faithfulness | {{X}} | ≥ 0.85 | ✅ |
| Answer Relevancy | {{X}} | ≥ 0.80 | ✅ |
| Context Precision | {{X}} | ≥ 0.75 | ✅ |
| Citation Accuracy (custom) | {{X}}% | ≥ 95% | ✅ |

### User-sim results

10 personas × 5-10 sessions each = {{N}} test sessions.

- P0 bugs: 0
- P1 bugs: 0
- P2 bugs: {{N}} (logged for future iteration)
- Trust verdict: {{N}}/10 personas would recommend

### Performance

- TTFT: {{X}}ms (target ≤ 3000ms)
- p50 end-to-end: {{X}}ms
- p99: {{X}}ms
- Cost per query: ${{X}}

## What I'd do differently

{{1-2 paragraphs of honest lessons. This is the section recruiters skim for engineering maturity.}}

## Lessons applied to the next project (P{{N+1}})

- {{Lesson 1}}
- {{Lesson 2}}
- {{Lesson 3}}

---

**Built**: {{DATE}} · **Builder**: Ujjawal Shrivastav · **Pair**: Jarvis (multi-agent SDLC, critic loops, 10-user-sim test, autonomous deploy)
