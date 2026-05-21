# {{PROJECT_NAME}} — {{TAGLINE}}

> {{ONE_LINE_PROBLEM_STATEMENT}}

[![Live Demo]({{VERCEL_URL}})]({{VERCEL_URL}}) [![GitHub]({{GITHUB_URL}})]({{GITHUB_URL}})

![demo]({{DEMO_GIF_URL}})

## Why this exists

{{2-3 paragraphs: the real 2026 pain this solves, the gap in existing tools, what's specifically novel here.}}

## What's inside

- **RAG technique**: {{e.g. Hybrid BM25 + dense (Voyage-3-large) + Cohere Rerank v3, with section-aware chunking}}
- **Stack**: Next.js 15 (App Router + RSC + Server Actions) · Tailwind 4 (OKLCH tokens) · shadcn/ui v4 · {{vector DB}} · Claude {{Sonnet 4.6 + Haiku 4.5}} · Voyage embed-3 · Cohere Rerank v3
- **Eval**: Ragas (Faithfulness {{X}} · Answer Relevancy {{Y}} · Context Precision {{Z}}) on a {{N}}-question golden set
- **Safety**: {{citation-mandatory · disclaimer-banner · refusal-on-out-of-scope}}

## Architecture

![arch diagram]({{ARCH_DIAGRAM_URL}})

{{Inline architecture explanation — 2-3 paragraphs covering the RAG pipeline, agent orchestration if any, and infra choices.}}

See [ARCHITECTURE.md](./ARCHITECTURE.md) for the full deep-dive.

## Key numbers

- **TTFT** (time-to-first-token): {{X}}ms
- **End-to-end p50 latency**: {{X}}ms
- **Eval (Ragas Faithfulness)**: {{X}}
- **Corpus size**: {{X}} documents, {{Y}} chunks
- **Cost per query**: ~${{Z}}

## Run locally

```bash
git clone https://github.com/{{USER}}/{{REPO}}.git
cd {{REPO}}
pnpm install
cp .env.example .env.local   # fill in your keys
pnpm run ingest               # ingest corpus into vector DB (one-time)
pnpm dev
```

Open http://localhost:3000

## Env vars

```
ANTHROPIC_API_KEY=...
VOYAGE_API_KEY=...
COHERE_API_KEY=...
{{VECTOR_DB_KEY}}=...
```

(See `.env.example` for full list.)

## Project structure

```
.
├── app/                    # Next.js 15 App Router pages + API routes
├── components/             # shadcn/ui components + custom
├── lib/
│   ├── rag/                # Hybrid search + rerank + generation
│   ├── ingest/             # Corpus ingestion scripts
│   ├── safety/             # Disclaimers + refusal patterns
│   ├── eval/               # Ragas eval cases + runner
│   └── observability/      # Logging + telemetry
├── scripts/                # CLI: ingest, eval, deploy
└── tests/                  # vitest + playwright
```

## Eval suite

Run the golden-set eval:

```bash
pnpm run eval
```

Sample question from the golden set:

> Q: {{example question}}
> Expected: {{citation context}} present, no hallucination, refusal if asked about {{out-of-scope category}}.

## What's NOT in scope

{{Explicit out-of-scope list — important for trust signaling. E.g.: "Does not provide investment advice. Does not output buy/sell signals. Does not retain user data."}}

## Built by

[Ujjawal Shrivastav]({{LINKEDIN_URL}}) — part of the [RAG Decathlon]({{DECATHLON_INDEX_URL}}), 10 production RAG products solving real 2026 problems.

## License

MIT
