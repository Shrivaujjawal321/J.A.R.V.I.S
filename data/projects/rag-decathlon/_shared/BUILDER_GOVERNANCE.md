# Builder Governance — RAG Decathlon

**Purpose**: standard rules every builder agent (ml-engineer, backend, frontend, ui-ux, data-engineer, prompt-engineer) receives at dispatch time, prepended to their specific brief. Ensures consistency across all 10 projects.

---

## YOU ARE BUILDING FOR

- **Boss**: Ujjawal Shrivastav — AI-native fresh-grad in India targeting AI/ML roles + freelance
- **Audience #1**: senior staff engineers / hiring managers at Anthropic / OpenAI / Cohere / Stripe / a16z portfolio companies who will skim 30 seconds of your output and decide whether the candidate is interview-worthy
- **Audience #2**: actual end-users of the deployed product who must derive immediate value
- **Audience #3**: Jarvis's critic-agent who will review your work before it ships

---

## STANDARDS (NON-NEGOTIABLE)

### 1. 2026 stack only
- **Frontend**: Next.js 15 (App Router + RSC + Server Actions + useOptimistic) · React 19 · Tailwind 4 (OKLCH colors, native CSS variables) · shadcn/ui v4 · Radix · Framer Motion 12 (only when motion adds clarity, never decoratively)
- **Backend**: Next.js API routes (Edge or Node runtime as chosen) OR FastAPI for heavy Python work (deploy as Vercel Python serverless if used)
- **Vector DB**: project-specific (Upstash Vector / Pinecone Serverless / Qdrant Cloud / Supabase pgvector / Chroma)
- **Embeddings**: Voyage-3-large (general) / voyage-code-3 (code) / voyage-multimodal-3 (image+text)
- **Reranker**: Cohere Rerank v3 (default) or bge-reranker-v2-m3 (open-source fallback)
- **LLMs**: Claude Sonnet 4.6 (reasoning) + Claude Haiku 4.5 (cheap tasks) — never name 4.5/4o/3-Opus
- **Validation**: TypeScript strict + Zod 3 (TS) / Pydantic v2 (Python)
- **Eval**: Ragas or Promptfoo for RAG quality gates

### 2. NO deprecated patterns
- ❌ Pages Router · ❌ `useEffect` for data fetching when RSC works · ❌ `getServerSideProps` · ❌ axios when fetch+Zod is fine · ❌ Tailwind `gray-500` style classes (use OKLCH semantic tokens) · ❌ Generic shadcn dialog with no a11y wiring · ❌ JS objects masquerading as DTOs (use Zod/Pydantic)

### 3. Citation-first for RAG
- Every claim from retrieval MUST cite the source
- Use Pydantic/Zod schema enforcing `Citation` objects on every fact
- UI MUST render citations inline (hover-card or sidebar)
- Fabricated citation = P0 bug (job-losing severity in product context)

### 4. Safety per domain
- **Healthcare**: disclaimers, no diagnoses, no doses, refuse "should I stop X" — route to physician
- **Legal**: no legal advice, no compliance verdicts, cite statute verbatim only
- **Finance**: no investment advice, no recommendations, educational framing only
- **Mental health**: crisis-keyword detection → immediate 988 (US) / Samaritans (UK) / iCALL (India) redirect with zero LLM response

### 5. Accessibility (WCAG 2.2 AA minimum)
- Keyboard nav through all interactive states
- ARIA live regions for streaming content
- Focus order respects flow
- Color contrast ≥ 4.5:1 body, ≥ 3:1 UI elements
- Reduced-motion media query respected

### 6. Performance budget
- **LCP**: ≤ 2.5s on 4G
- **INP**: ≤ 200ms
- **CLS**: ≤ 0.1
- **TTFT** (streaming RAG): ≤ 3s
- **Cold-start** (Vercel function): ≤ 5s

### 7. Cost discipline (per-project cap $8 LLM)
- Use Haiku 4.5 for routing, extraction, classification, light reasoning
- Reserve Sonnet 4.6 for final synthesis and complex reasoning
- Cache embeddings (compute once, persist in vector DB)
- Cache reranker results when query repeats within session

### 8. Anti-patterns (Boss has flagged)
- ❌ Generic "AI assistant" copy / sparkle icons / gradient avatars
- ❌ "I am an AI and I cannot..." over-apology
- ❌ Confetti / emoji / gamification in serious-domain apps
- ❌ Vanilla "chat with PDF" without novel angle
- ❌ Hardcoded API keys in client code
- ❌ Demo that breaks on second query
- ❌ README without arch diagram + demo GIF

### 9. Repository structure (every project)

```
project-slug/
├── README.md              # Public-facing, must include: hero GIF, problem, demo URL, arch diagram, stack, run-locally instructions, license
├── ARCHITECTURE.md        # Internal arch deep-dive (linked from README)
├── package.json
├── tsconfig.json (strict)
├── tailwind.config.ts
├── .env.example           # All required env vars documented (never .env)
├── .gitignore             # Standard Next.js gitignore + .env
├── app/                   # Next.js 15 App Router
├── components/            # shadcn/ui components
├── lib/
│   ├── rag/               # Hybrid search + rerank + generation
│   ├── ingest/            # Corpus ingestion scripts
│   ├── safety/            # Disclaimer copy + refusal patterns
│   ├── eval/              # Ragas/Promptfoo eval cases
│   └── observability/     # Logging + telemetry hooks
├── scripts/               # ingestion CLI, eval runner
└── tests/                 # vitest + playwright
```

### 10. Deployment definition-of-done
A project is "done" ONLY when ALL of these are true:
- [ ] GitHub repo public + README polished + demo GIF embedded
- [ ] Vercel deploy live at clean subdomain (`{slug}.vercel.app`)
- [ ] All 10 user-sim personas executed against deployed URL with ZERO P0/P1 bugs
- [ ] Critic-agent final PASS on every Phase 3.3 builder output
- [ ] Eval suite shows Ragas Faithfulness ≥ 0.85, Answer Relevancy ≥ 0.80, Context Precision ≥ 0.75 on the project's golden set (≥30 questions)
- [ ] Case study (1-page) added to `data/outputs/portfolio/rag-decathlon/Pn.md`
- [ ] Postmortem written at `projects/Pn/POSTMORTEM.md`

### 11. Reporting back

When your builder phase completes, return a JSON envelope:

```json
{
  "project": "P<n>-<slug>",
  "phase": "3.3-<role>",
  "status": "success | partial | blocked",
  "artifacts": ["path/to/file1", "path/to/file2"],
  "deviations_from_brief": ["..."],
  "open_questions_for_jarvis": ["..."],
  "next_step_recommendation": "..."
}
```

---

## Boss's Working Style (mirror this in your work)

- Hinglish-friendly + RESPECTFUL register (in user-facing copy of India-targeted projects, optionally mirror Boss's tone)
- Vertical depth over surface scans — drill into edge cases
- Options-with-WHY when offering choices; never pre-narrow
- Parallel-default execution; no serial when parallel is safe
- "Isse behtar kuch ban hi nahi sakta" — best-in-class is the output bar

---

## Escalation path

If you're blocked on something Jarvis didn't anticipate:
1. Note it in `open_questions_for_jarvis`
2. Do NOT make destructive assumptions
3. Return your partial output with status `blocked` + reason
4. Jarvis will redesign or unblock and re-dispatch

If you discover that the spec itself has a bug:
1. Implement what's correct
2. Document the deviation in `deviations_from_brief`
3. Jarvis will reconcile with the spec
