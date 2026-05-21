# P1 glp1-nutrition-copilot — Architecture

**Phase 3.2 synthesis** of `research/SOTA_LANDSCAPE.md` + `research/UI_UX_BRIEF.md`
**Generated**: 2026-05-14 by Jarvis (synthesis from research outputs)
**Output bar**: production-grade — every code path must work end-to-end on first user query.

---

## 1. System Diagram

```
                       ┌─────────────────────────────────────┐
                       │   Next.js 15 App Router (Vercel)    │
                       │   - / (research-tool layout)        │
                       │   - /api/chat (POST, streaming)     │
                       │   - /api/source/[pmid] (GET)        │
                       │   - /api/eval (GET, cron)           │
                       └──────────────┬──────────────────────┘
                                      │
            ┌─────────────────────────┴────────────────────────┐
            │              RAG Pipeline (Serverless)            │
            │                                                   │
            │  Query → Safety Classifier (Haiku)                │
            │     │      ├─ in_scope        → continue          │
            │     │      ├─ clinical_query  → REFUSAL response  │
            │     │      └─ adversarial     → REFUSAL response  │
            │     ▼                                             │
            │  Voyage embed query (input_type="query")          │
            │     │                                             │
            │     ├─ Dense search → Upstash Vector (top 20)     │
            │     └─ Sparse search → rank_bm25 (top 20)         │
            │     │                                             │
            │     ▼ RRF fusion (k=60) → top 30                  │
            │     ▼ Voyage Rerank 2.5 → top 8                   │
            │     ▼                                             │
            │  Confidence check (max rerank score)              │
            │      ├─ ≥ 0.75   → answer + citations             │
            │      ├─ 0.65-0.74 → answer + "Some Evidence" card │
            │      └─ < 0.65   → "Limited Evidence" + referral  │
            │     ▼                                             │
            │  createDataStreamResponse                         │
            │   ├─ writeMessageAnnotation × 8 (sources first)   │
            │   └─ streamText (Sonnet 4.6 synthesis)            │
            │                                                   │
            └──────────────┬────────────────────────────────────┘
                           │
                  ┌────────┴───────┐
                  │  Browser (UI)  │
                  │  ─ Sources stream in first as cards         │
                  │  ─ Answer text streams with inline [n]      │
                  │  ─ HoverCard on [n] → source popover        │
                  └────────────────┘
```

## 2. Data Flow

### Ingest pipeline (one-time + scheduled refresh)
1. **PubMed**: NCBI E-utilities ESearch (term: GLP-1 nutrition queries) → ESummary → EFetch XML batch (200/req with API key, 10rps) → Parse abstracts → Voyage embed (input_type="document") → Upsert to Upstash Vector with metadata `{pmid, title, journal, year, mesh[], abstract, source_type: "pubmed"}`. Bulk full-text via PMC S3 `oa_comm/oa_noncomm` buckets.
2. **USDA**: FoodData Central search API → batch GET food details → Format as single chunk per food (`"Food: X. Nutrients per 100g: ..."`) → Embed → Upsert with metadata `{fdcId, food_name, data_type: "Foundation"|"SR Legacy", source_type: "usda"}`.
3. **NIH ODS**: Fetch 16 nutrient fact sheets → Section-split by headers → Embed each section → Upsert with metadata `{slug, section_name, source_type: "ods"}`.

Refresh cron: weekly for PubMed (new papers), monthly for USDA + ODS.

### Query pipeline (per request)
1. User query → Safety classifier (Haiku 4.5, structured Pydantic output)
2. If safe → embed query (Voyage, input_type="query")
3. Parallel: BM25 search (in-memory) + Upstash Vector dense search, both top-20
4. RRF fusion → top 30 candidates
5. Voyage Rerank 2.5 → top 8 with rerank scores
6. Confidence gate → choose response template (full / some-evidence / limited / refusal)
7. Stream sources first via `writeMessageAnnotation`, then Sonnet 4.6 synthesis with strict citation-only-from-context prompt

## 3. RAG Pipeline Details

```typescript
// lib/rag/pipeline.ts
type Chunk = {
  id: string
  text: string
  metadata: { source_type: 'pubmed'|'usda'|'ods'; pmid?: string; fdcId?: number; slug?: string; title: string; year?: number; ... }
  rerank_score?: number
}

export async function answer(query: string): Promise<RagResponse> {
  const safety = await classifySafety(query)              // Haiku, ~200ms
  if (safety.refuse) return makeRefusal(safety.reason)

  const qEmbedding = await voyage.embed({                  // ~150ms
    input: [query], model: "voyage-3-large", input_type: "query"
  })

  const [denseHits, sparseHits] = await Promise.all([      // parallel ~20ms
    upstashVector.query({ vector: qEmbedding, topK: 20, includeMetadata: true }),
    bm25.search(query, 20)
  ])
  const fused = rrfFuse(denseHits, sparseHits, 60).slice(0, 30)

  const reranked = await voyage.rerank({                   // ~600ms (main bottleneck)
    query, documents: fused.map(c => c.text), model: "rerank-2.5", top_k: 8
  })
  const final = reranked.results.map(r => ({ ...fused[r.index], rerank_score: r.relevance_score }))

  const maxConfidence = final[0]?.rerank_score ?? 0
  const responseMode = maxConfidence >= 0.75 ? 'full' : maxConfidence >= 0.65 ? 'some_evidence' : 'limited_evidence'

  return { chunks: final, sources: final.map(toCitation), responseMode }
}
```

## 4. Infra Choices (locked)

| Layer | Choice | Why |
|-------|--------|-----|
| Runtime | Next.js 15 Serverless (Node) | RAG pipeline needs full Node; Edge can't fit BM25 index |
| Compute | Vercel Fluid Compute | 99.37% cold-start elimination, IO-bound friendly billing |
| Embeddings | Voyage-3-large 1024-dim int8 | 9.74% better than OpenAI on biomedical |
| Reranker | Voyage Rerank 2.5 | nDCG@10 0.110, beats Cohere 4 Pro on passage ranking |
| Sparse | rank_bm25 (npm: `okapibm25` or Python `rank_bm25`) | In-memory, fast |
| Vector DB | Upstash Vector (Vercel Marketplace) | 5-15ms cold start, PAYG, native Vercel integration |
| Cache | Upstash Redis | Free 10K/day, embedding + retrieval cache |
| LLM router | Claude Haiku 4.5 | Safety classifier, structured extraction |
| LLM synthesis | Claude Sonnet 4.6 | Final answer with strict citation prompt |
| SDK | Vercel AI SDK 5 | `createDataStreamResponse` + `writeMessageAnnotation` for citation-first streaming |

## 5. Env vars (`.env.example`)

```
# Required
ANTHROPIC_API_KEY=sk-ant-...
VOYAGE_API_KEY=pa-...
UPSTASH_VECTOR_REST_URL=https://...
UPSTASH_VECTOR_REST_TOKEN=...
UPSTASH_REDIS_REST_URL=https://...
UPSTASH_REDIS_REST_TOKEN=...
NCBI_API_KEY=...                # free, increases rate to 10rps
USDA_FDC_API_KEY=...            # free

# Optional
RAGAS_OPENAI_API_KEY=...        # only for eval runs (Ragas needs an LLM judge)
NODE_ENV=production
```

## 6. Repo structure

```
glp1-nutrition-copilot/
├── README.md
├── ARCHITECTURE.md (this file copied here)
├── package.json
├── tsconfig.json (strict)
├── tailwind.config.ts
├── next.config.mjs
├── .env.example
├── .gitignore
├── app/
│   ├── layout.tsx              # root layout, fonts, disclaimer banner
│   ├── page.tsx                # main research-tool layout (3-panel)
│   ├── globals.css             # OKLCH tokens
│   └── api/
│       ├── chat/route.ts       # POST streaming RAG endpoint
│       ├── source/[pmid]/route.ts  # GET single source detail
│       └── eval/route.ts       # GET protected eval runner
├── components/
│   ├── chat/
│   │   ├── AskBox.tsx
│   │   ├── AnswerCard.tsx       # streaming + citation rendering
│   │   ├── CitationChip.tsx     # inline [n] with HoverCard
│   │   ├── SourceCard.tsx       # bottom source list
│   │   ├── SourceModal.tsx      # paper detail Sheet (mobile) / Dialog (desktop)
│   │   ├── DisclaimerBanner.tsx
│   │   ├── EvidenceGapCard.tsx
│   │   └── RefusalCard.tsx
│   └── ui/                      # shadcn/ui v4 (HoverCard, Badge, Alert, Skeleton, Card, Sheet, Dialog)
├── lib/
│   ├── rag/
│   │   ├── pipeline.ts
│   │   ├── bm25.ts
│   │   ├── rrf.ts
│   │   ├── rerank.ts
│   │   └── embed.ts
│   ├── ingest/
│   │   ├── pubmed.ts
│   │   ├── usda.ts
│   │   └── ods.ts
│   ├── safety/
│   │   ├── classifier.ts
│   │   ├── refusal-copy.ts
│   │   └── disclaimer-copy.ts
│   ├── eval/
│   │   ├── golden-set.jsonl
│   │   ├── ragas-runner.py
│   │   └── citation-accuracy.ts
│   └── observability/
│       └── logger.ts
├── scripts/
│   ├── ingest.ts               # CLI for one-time + scheduled ingestion
│   └── eval.ts                 # CLI for golden-set eval
└── tests/
    ├── unit/
    │   ├── rrf.test.ts
    │   ├── safety.test.ts
    │   └── citation.test.ts
    └── e2e/
        └── happy-path.spec.ts (playwright)
```

## 7. Eval suite design (Phase 3.4 gate)

Run `pnpm run eval` against deployed URL. Reports to `lib/eval/eval-report-<ts>.md`.

| Metric | Threshold |
|--------|-----------|
| Ragas Faithfulness | ≥ 0.90 |
| Ragas Answer Relevancy | ≥ 0.80 |
| Ragas Context Precision | ≥ 0.75 |
| Ragas Context Recall | ≥ 0.80 |
| Citation Accuracy (custom) | ≥ 95% |
| Refusal Fidelity (custom) | 100% on safety questions |
| Recall@5 (MIRAGE-style) | ≥ 0.85 |

Goldenset details: see `EVAL_PLAN.md`.

## 8. Observability

- Log every query: hashed-user-id, query, response confidence, sources cited, refusal-or-not, latency breakdown, cost (input + output tokens)
- Append to `data/audits/YYYY-MM-DD.jsonl` per Tier-2 audit (per auto-mode skill)
- No PHI logged: query hashed-or-omitted if domain-classified as PHI-likely

## 9. Performance budget

| Stage | Target | Hard limit |
|-------|--------|-----------|
| Safety classify | < 200ms | 400ms |
| Embed query | < 150ms | 300ms |
| BM25 + dense (parallel) | < 50ms | 100ms |
| Rerank | < 700ms | 1200ms |
| **TTFT** (first source annotation) | **< 1.5s** | 2.5s |
| Full p50 response | 3-5s | 8s |

## 10. Open architectural questions (resolved)

- **Cohere Rerank v3 vs Voyage Rerank 2.5?** → Voyage wins nDCG@10. Decided.
- **Pinecone vs Upstash Vector?** → Upstash for native Vercel zero-cold-start. Decided.
- **Haiku for everything or Haiku+Sonnet split?** → Haiku for safety+extraction (cheap), Sonnet for final synthesis (quality). Decided.
- **Streaming pattern: SSE vs websocket?** → AI SDK 5 SSE via `createDataStreamResponse`. Decided.

## 11. Risks + mitigations

| Risk | Mitigation |
|------|-----------|
| LLM hallucinates PMIDs despite instructions | All PMIDs flow as message annotations from retrieval; UI shows only `[n]` rendered against annotation map; prompt strictly forbids PMID generation; eval gate catches any leakage |
| Slow rerank (>1.2s) breaks TTFT budget | Voyage Rerank 2.5 Lite fallback ($0.020/1M, ~616ms) configurable via env flag |
| Free-tier limits hit during demo | Upstash Vector $0.40/100K PAYG; Voyage free tier 50M tokens/mo; Anthropic billed against Boss's existing API key |
| Stale guideline contamination | Corpus filter: PubMed papers ≥ 2024; reranker has access to year metadata; system prompt instructs prefer recent |

## 12. Next phase handoff

Phase 3.3 builders dispatched in parallel:
- `ml-engineer-agent` ← RAG pipeline (lib/rag/, scripts/ingest.ts)
- `data-engineer-agent` ← ingestion scripts (lib/ingest/)
- `backend-engineer-agent` ← API routes (app/api/*)
- `frontend-engineer-agent` ← UI components + page (app/, components/)
- `prompt-engineer-agent` ← safety classifier prompt + synthesis prompt (lib/safety/, PROMPTS.md)

Each paired with `code-agent` critic per `_shared/CRITIC_PROMPT_TEMPLATE.md`.
