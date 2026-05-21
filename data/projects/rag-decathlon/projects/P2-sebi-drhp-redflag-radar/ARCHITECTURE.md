# P2 sebi-drhp-redflag-radar — Architecture

**Phase 3.2 synthesis** of P2 SOTA_LANDSCAPE + UI_UX_BRIEF
**Generated**: 2026-05-14 by Jarvis

---

## 1. System Diagram

```
                                      ┌─────────────────────────────────┐
                                      │ Next.js 15 App Router (Vercel)  │
                                      │  - /             (browse)        │
                                      │  - /report/[drhp]                │
                                      │  - /api/upload                   │
                                      │  - /api/job/[id]                 │
                                      │  - /api/report/[drhp]/stream     │
                                      │  - /api/source/[chunk_id]        │
                                      └────────┬───────────┬─────────────┘
                                               │           │
                       ┌───────────────────────┘           └──────────────────────┐
                       │                                                          │
       ┌───────────────▼──────────────────┐               ┌───────────────────────▼─────────────────┐
       │  Modal.com Worker (8 vCPU/16GB)  │               │  Vercel Fluid (Sonnet 4.6 + Haiku 4.5)  │
       │   PDF → Docling → Chunker        │               │   LangGraph 0.3+ Send API               │
       │   → Contextual prefix (Haiku)    │               │     ┌─PromoterPledgeAgent       ────┐   │
       │   → voyage-3-large embed         │               │     ├─LitigationRiskAgent       ────┤   │
       │   → Supabase pgvector upsert     │               │     ├─ObjectsOfIssueAgent       ────┤── Aggregator → SSE stream
       │   → Webhook back to /api/job     │               │     ├─RevenueConcentrationAgent ────┤   │
       │   (15-20 min/DRHP, $0.19)        │               │     └─ comply gate (refusal regex)──┘   │
       └──────────────────────────────────┘               └─────────────────────────────────────────┘
                       │                                                          │
                       └─────────────► Supabase Postgres + pgvector ◄──────────────┘
                                       (drhp_chunks, drhp_meta,
                                        ingest_jobs, agent_runs)

                       Browser ── SSE ── streams report sections + citations
                       Browser ── PDF Viewer (react-pdf-highlighter-extended) on citation click
```

## 2. Data Flow

### Ingest (background, Modal worker)
1. User uploads DRHP PDF → Vercel Edge stores in Supabase Storage, inserts `ingest_jobs` row, triggers Modal webhook with `{job_id, drhp_id, pdf_url}` — returns `{job_id}` in <5s
2. Modal worker: download PDF → `PyMuPDF` outline → `Docling hi_res` parse (tables + layout) → section-aware chunker (rapidfuzz fuzzy heading match ≥ 80) → child chunks (512 tok, 10% overlap) with parent-chunk pointers and `is_table` metadata
3. Modal worker: contextual prefix gen via Anthropic batch (Haiku 4.5) — 1-3 sentence "situation" prepend per chunk
4. Modal worker: voyage-3-large embedding (`inputType: "document"`, 1024-dim int8, batched) → Supabase pgvector upsert with full metadata schema
5. Modal worker: POST `/api/job/{id}` webhook with `{status: "complete", chunk_count, page_count}` → triggers in-app + email notification

### Query (Vercel Fluid serverless, per report request)
1. User opens `/report/{drhp}` → Next.js RSC server-fetches drhp_meta + first cached `agent_run` (if exists) → renders shell
2. If no cached agent_run: client opens SSE to `/api/report/{drhp}/stream`
3. Server: LangGraph 0.3+ `Send` API fans out to 4 domain agents in parallel (Promoter Pledge / Litigation Risk / Objects of Issue / Revenue Concentration). Each agent runs its own hybrid pgvector + tsvector retrieval, scoped via `WHERE drhp_id = $1 AND section_type = ANY($2)`, gets reranked top-8 by Cohere Rerank v3.5, then Pydantic-v2 structured-output Sonnet 4.6 call producing `*Report` schema with `source_chunks[]` + `source_pages[]` populated
4. Aggregator (defer=True) waits for all 4, synthesises composite `red_flag_level` per section, streams sections sequentially via SSE as they complete
5. Each section streams: severity badge → headline → details (verbatim blockquote + LLM analysis distinct) → citation chips
6. Report cached to `agent_runs` table — subsequent visits instant

### Refusal path
- Pre-stream regex check on any free-text query field against `PROHIBITED_QUERY_PATTERNS` (PROMPTS §1). If match → SSE writes single `data-refusal` chunk + closes. Never reach LLM.

## 3. Agent Pipeline (LangGraph 0.3+ Send API)

```python
# lib/agents/graph.py
from langgraph.graph import StateGraph, END
from langgraph.constants import Send
from typing import TypedDict, Annotated, List
from operator import add

class DRHPAnalysisState(TypedDict):
    drhp_id: str
    company_name: str
    sections_to_analyze: List[dict]
    agent_results: Annotated[list, add]
    final_report: dict

def dispatch_agents(state):
    sends = []
    for s in state["sections_to_analyze"]:
        if s["section_type"] in ["promoter_background", "capital_structure"]:
            sends.append(Send("promoter_pledge", {"section": s, "drhp_id": state["drhp_id"]}))
        if s["section_type"] == "legal_proceedings":
            sends.append(Send("litigation_risk", {"section": s, "drhp_id": state["drhp_id"]}))
        if s["section_type"] == "objects_of_issue":
            sends.append(Send("objects_classifier", {"section": s, "drhp_id": state["drhp_id"]}))
        if s["section_type"] in ["financial_statements", "business_overview"]:
            sends.append(Send("revenue_concentration", {"section": s, "drhp_id": state["drhp_id"]}))
    return sends

graph = StateGraph(DRHPAnalysisState)
graph.add_node("dispatch", lambda s: s)  # passthrough
graph.add_node("promoter_pledge", run_promoter_agent)
graph.add_node("litigation_risk", run_litigation_agent)
graph.add_node("objects_classifier", run_objects_agent)
graph.add_node("revenue_concentration", run_revenue_agent)
graph.add_node("aggregate", aggregate_results, defer=True)

graph.set_entry_point("dispatch")
graph.add_conditional_edges("dispatch", dispatch_agents,
    ["promoter_pledge", "litigation_risk", "objects_classifier", "revenue_concentration"])
for node in ["promoter_pledge", "litigation_risk", "objects_classifier", "revenue_concentration"]:
    graph.add_edge(node, "aggregate")
graph.add_edge("aggregate", END)
```

Each agent node: retrieve → rerank → Pydantic structured output → return `{agent_id, report}` to reducer.

## 4. Infra Choices (locked)

| Layer | Choice | Why |
|-------|--------|-----|
| PDF parse | Docling (IBM, MIT) + PyMuPDF | 97.9% table accuracy; native TOC |
| Background worker | Modal.com (8 vCPU, 16GB, 30min timeout) | Vercel 300s can't fit 600pp DRHP |
| Vector DB | Supabase pgvector | SQL WHERE pre-filter + tsvector hybrid in ONE query |
| Embedding | voyage-3-large 1024-dim int8 | MTEB 67.1, regulatory domain fit |
| Reranker | Cohere Rerank v3.5 | +23.4% finance domain over hybrid alone |
| Agent orchestration | LangGraph 0.3+ Send API | Map-reduce fan-out with reducer |
| LLM router | Claude Haiku 4.5 | Contextual prefix gen + safety classify |
| LLM synthesis | Claude Sonnet 4.6 | Per-agent structured Pydantic output |
| Frontend | Next.js 15 + Tailwind 4 + shadcn/ui v4 | Same as P1 baseline |
| PDF viewer | react-pdf-highlighter-extended (DanielArnould fork) | Viewport-independent highlights, pdf.js-dist |
| Streaming | Vercel AI SDK 5 createUIMessageStream (same as P1) | SSE with data-* chunks |

## 5. Database Schema (Supabase Postgres)

```sql
create extension if not exists vector;
create extension if not exists pg_trgm;

create table drhps (
  id text primary key,           -- "swiggy-2024-09"
  company_name text not null,
  year int not null,
  is_sme_ipo boolean default false,
  pdf_url text not null,
  page_count int,
  ingested_at timestamptz,
  metadata jsonb default '{}'
);

create table drhp_chunks (
  chunk_id text primary key,     -- "{drhp_id}_{section_type}_{idx}"
  drhp_id text references drhps(id) on delete cascade,
  section_type text not null,
  page_range int4range,
  chunk_index int not null,
  text text not null,
  contextual_prefix text,
  is_table boolean default false,
  table_type text,               -- promoter_pledge | fund_use | financials | null
  parent_chunk_id text,
  token_count int,
  embedding vector(1024),
  search_vector tsvector generated always as (to_tsvector('english', text)) stored,
  metadata jsonb default '{}',
  created_at timestamptz default now()
);

create index on drhp_chunks using hnsw (embedding vector_cosine_ops);
create index on drhp_chunks using gin (search_vector);
create index on drhp_chunks (drhp_id, section_type);

create table ingest_jobs (
  id uuid primary key default gen_random_uuid(),
  drhp_id text references drhps(id),
  status text not null default 'queued',  -- queued|parsing|embedding|complete|failed
  progress int default 0,                 -- 0-100
  error_message text,
  created_at timestamptz default now(),
  completed_at timestamptz
);

create table agent_runs (
  id uuid primary key default gen_random_uuid(),
  drhp_id text references drhps(id),
  agent_id text not null,                 -- promoter_pledge | litigation_risk | objects | revenue
  report jsonb not null,                  -- Pydantic Report dump
  source_chunks text[],
  red_flag_level text,
  llm_input_tokens int,
  llm_output_tokens int,
  cost_usd numeric,
  created_at timestamptz default now()
);
```

### Hybrid query

```sql
select chunk_id, section_type, text, page_range,
  (0.7 * (1 - (embedding <=> $1))
   + 0.3 * ts_rank(search_vector, plainto_tsquery($2))) as hybrid_score
from drhp_chunks
where drhp_id = $3
  and section_type = any($4)
  and (search_vector @@ plainto_tsquery($2) or embedding <=> $1 < 0.5)
order by hybrid_score desc
limit 20;
```

## 6. Env vars (`.env.example`)

```
# Required (frontend + Vercel)
ANTHROPIC_API_KEY=sk-ant-...
VOYAGE_API_KEY=pa-...
COHERE_API_KEY=...
SUPABASE_URL=https://<proj>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=...
SUPABASE_ANON_KEY=...

# Modal worker
MODAL_TOKEN_ID=...
MODAL_TOKEN_SECRET=...

# Optional
RESEND_API_KEY=...        # email notification on ingest complete
EVAL_PROTECTED_TOKEN=...
NODE_ENV=production
```

## 7. Repo structure

```
sebi-drhp-redflag-radar/
├── README.md
├── ARCHITECTURE.md
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.mjs
├── .env.example
├── .gitignore
├── app/
│   ├── layout.tsx                 # Tabular numbers, OKLCH tokens
│   ├── page.tsx                   # Pre-indexed DRHP browse
│   ├── report/[drhp]/page.tsx     # Report shell + streaming
│   ├── upload/page.tsx            # Upload + job tracking
│   └── api/
│       ├── upload/route.ts        # POST: store + queue Modal
│       ├── job/[id]/route.ts      # GET status + POST webhook from Modal
│       ├── report/[drhp]/stream/route.ts  # SSE LangGraph run
│       └── source/[chunk_id]/route.ts     # Citation chunk detail
├── components/
│   ├── report/
│   │   ├── ReportShell.tsx
│   │   ├── SectionTabs.tsx
│   │   ├── RedFlagCard.tsx
│   │   ├── SeverityBadge.tsx
│   │   ├── CitationChip.tsx
│   │   ├── PDFViewer.tsx         # react-pdf-highlighter-extended wrapper
│   │   ├── DisclaimerBanner.tsx
│   │   ├── RefusalCard.tsx
│   │   └── EvidenceBlockquote.tsx (verbatim DRHP) + AnalysisBlock.tsx (LLM synth)
│   ├── upload/UploadDropzone.tsx
│   └── ui/                        # shadcn/ui v4 primitives
├── lib/
│   ├── agents/                    # 5-agent LangGraph runtime
│   ├── rag/                       # hybrid query + rerank + chunk fetch
│   ├── ingest/                    # NO — ingest is in Modal worker repo
│   ├── safety/                    # SEBI refusal regex + disclaimer copy
│   ├── pdf/                       # citation → page + highlight helper
│   ├── eval/                      # 30-question golden set + Ragas runner
│   ├── modal/                     # Modal webhook client
│   └── observability/
├── modal_worker/                  # SEPARATE Python project
│   ├── pyproject.toml
│   ├── modal_app.py               # @app.function entrypoints
│   ├── parse.py                   # Docling + PyMuPDF
│   ├── chunk.py                   # section-aware hierarchical
│   ├── embed.py                   # Voyage batch
│   └── upsert.py                  # Supabase pgvector
└── tests/
    ├── unit/                      # rrf, refusal-regex, chunker fuzzy match
    └── e2e/                       # upload → report happy path
```

Modal worker = separate Python project, deployed via `modal deploy modal_worker/modal_app.py`.

## 8. Eval suite design

| Metric | Threshold |
|--------|-----------|
| Ragas Faithfulness | ≥ 0.90 |
| Citation Accuracy (chunk_id + page match) | ≥ 0.85 |
| Section-Match Accuracy | ≥ 0.88 |
| Answer Relevancy | ≥ 0.82 |
| Context Precision | ≥ 0.75 |
| Refusal Fidelity (SEBI prohibited regex) | 100% |

30-Q golden set in `EVAL_PLAN.md`. Test against Swiggy + Vikram Solar (human-verified ground truth).

## 9. Performance budget

| Stage | Target |
|-------|--------|
| PDF upload + Storage | < 5s |
| Modal full ingest (600pp DRHP) | < 20 min |
| Voyage embed 5K chunks | < 45s |
| pgvector upsert | < 20s |
| Pre-indexed DRHP first report | < 15s |
| Per-section TTFT (SSE) | < 3s |
| Full 4-agent report stream | < 60s |
| Modal cost per parse | ~$0.19 |

Pre-index Swiggy + Vikram Solar + Hyundai India + ixigo + Tata Tech at launch for instant demos.

## 10. Risks + mitigations

| Risk | Mitigation |
|------|-----------|
| Modal worker quota exhaustion | Job queue with retry; backpressure UI ("queued ahead of N") |
| Hallucinated red-flag verdict | Pydantic structured output schema validation + post-LLM regex on confidence field; eval gate |
| SEBI compliance violation in output | Hard pre-LLM regex refusal + persistent disclaimer + agent prompts strictly forbid "buy/sell/target/overvalued" tokens |
| pgvector cold connection | Supabase pooler (transaction mode) + Edge runtime where possible |
| Docling crash on weird PDF | Fallback to PyMuPDF4LLM Markdown extraction; flag as `low_confidence: true` on report |
| OFS misclassification | Dedicated objects-of-issue agent with category enum; eval includes OFS-heavy DRHPs (Swiggy) |

## 11. Open architectural questions (resolved)

- **Modal vs Vercel cron for parsing?** → Modal. Vercel 300s timeout kills 600pp DRHP. Modal $0.19/parse acceptable.
- **Pinecone vs Supabase pgvector?** → Supabase. SQL WHERE pre-filter + tsvector hybrid decisive.
- **Cohere Rerank v3.5 vs Voyage Rerank v2.5?** → Cohere v3.5 wins on finance domain (+23.4% over hybrid). Different choice from P1 — correct, each project gets right tool.
- **Pure TS or Python for agents?** → Python in Modal (matches LangGraph 0.3+ + Pydantic v2 + Instructor ergonomics). LangGraph also has TS but Python is the mature path.

## 12. Phase 3.3 handoff

Builders for P2:
- `data-engineer-agent` — Modal worker (Python): parse + chunk + embed + upsert
- `ml-engineer-agent` — LangGraph 5-agent pipeline + retrieval + Pydantic schemas (Python in modal_worker/, OR Node in lib/agents/ using langgraphjs — decide based on stability)
- `backend-engineer-agent` — Next.js API routes (upload/job/stream/source) + Supabase client + Modal webhook
- `frontend-engineer-agent` — UI per UI_UX_BRIEF (institutional audit-report layout, severity badges, PDF viewer)
- `prompt-engineer-agent` — 5 agent system prompts with Pydantic schemas embedded
