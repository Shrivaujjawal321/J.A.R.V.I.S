# SEBI DRHP Red-Flag Radar — SOTA Landscape (P2 Phase 3.1 Research)

**Generated**: 2026-05-14 by research-agent
**Purpose**: `<current_2026_landscape>` block for P2 builder briefs.

---

## Executive Summary

P2 should be built as a **LangGraph 0.3+ Send-API 5-agent fan-out pipeline** running on **Modal.com** for heavy PDF parsing (Vercel's 300s limit kills 600-page DRHP ingestion) with **Vercel Fluid Compute** serving the agent orchestration + SSE streamed report rendering. PDF parsing: **Docling (IBM, MIT, 97.9% table accuracy)** + PyMuPDF for native TOC extraction. Embeddings: **voyage-3-large** (MTEB 67.1, regulatory domain fit). Reranker: **cohere-rerank-v3.5** (+23.4% finance domain). Vector DB: **Supabase pgvector** — only option supporting SQL WHERE pre-filter + tsvector hybrid + JOINs in one query, decisive for `WHERE drhp_id = X AND section_type = 'objects_of_issue'` patterns. Chunking: hierarchical hybrid — section chunks (1500 tok parents) + 512-tok children with **Anthropic Contextual Retrieval prepend** (35-49% retrieval improvement). 5 agents: Promoter Pledge Extractor / Litigation Risk Summariser / Objects of Issue Classifier / Revenue Concentration Detector / Synthesis. All Pydantic-v2 structured outputs with chunk_id + page citations. SEBI compliance: hard refusal regex on "should I invest / buy / target price / overvalued"; **"educational only" disclaimers have ZERO legal protection** if buy/sell signals leak. Test corpus: Swiggy + Vikram Solar + Hyundai India + ixigo + Tata Tech. Realistic ingest: 15-20 min background per DRHP, not 90s. Modal cost ~$0.19/parse. Total TTFT for report (post-ingest): <3s.

---

## 1. Agentic RAG Architecture SOTA for Long Regulatory PDFs

### Chunking — Hierarchical Hybrid + Contextual Retrieval

The 2026 production default for 400-900 page regulatory PDFs:

1. **Level 1 — Section chunks** (~1,500-2,000 tokens): Parse DRHP TOC, split into named sections (Objects of Issue, Risk Factors, Financial Statements, Promoter Background, Legal Proceedings). Retrieval context windows.
2. **Level 2 — Child chunks** (~300-512 tokens): Subdivide each section for embedding/ANN search. Each child points to parent.
3. **Anthropic Contextual Retrieval prepend**: Before embedding each child, prepend a 1-3 sentence LLM-generated "situation" summary (where in document). Done once at ingestion. **35-49% reduction in top-20 retrieval failure rate.**

Sizes:
- Child: **512 tokens, 10% overlap**
- Parent/section: **1,500 tokens** no overlap (section boundaries natural)
- **Financial tables: atomic — NEVER split mid-table**; embed full table with `"table:"` metadata prefix
- Financial statement pages: 1,000 tokens (dense numbers need context)
- Individual risk factor items: ONE chunk each (200-400 tokens). NEVER merge across risk items.

### LangGraph 0.3+ Send-API 5-Agent Fan-Out

The 2026 canonical pattern is LangGraph's **Send API for dynamic map-reduce** with reducer-aggregation:

```python
from langgraph.constants import Send
from typing import TypedDict, Annotated, List
from operator import add

class DRHPAnalysisState(TypedDict):
    drhp_id: str
    company_name: str
    sections_to_analyze: List[dict]
    agent_results: Annotated[list, add]   # parallel reducer — no race
    final_report: dict

def dispatch_agents(state: DRHPAnalysisState):
    sends = []
    for s in state["sections_to_analyze"]:
        if s["section_type"] in ["Promoter Background", "Capital Structure"]:
            sends.append(Send("promoter_pledge_agent", {"section": s, "drhp_id": state["drhp_id"]}))
        if s["section_type"] == "Legal Proceedings":
            sends.append(Send("litigation_risk_agent", {"section": s, "drhp_id": state["drhp_id"]}))
        if s["section_type"] == "Objects of Issue":
            sends.append(Send("objects_classifier_agent", {"section": s, "drhp_id": state["drhp_id"]}))
        if s["section_type"] in ["Financial Statements", "Business Overview"]:
            sends.append(Send("revenue_concentration_agent", {"section": s, "drhp_id": state["drhp_id"]}))
    return sends
```

Use `defer=True` on aggregator for asymmetric agent durations. Each agent subgraph can have its own `AsyncSqliteSaver` checkpointer for audit logs.

### Embeddings + Reranker

- **Embedding: `voyage-3-large`** — MTEB 67.1, $0.18/1M tokens, 16K context, regulatory fit
  Fallback: `text-embedding-3-large` (OpenAI MTEB 65.1, $0.13/1M)
- **Reranker: `cohere-rerank-v3.5`** — **+23.4% over hybrid search on finance domain**, +30.8% over BM25 alone. 4,096 token context. 100+ languages (Hindi/English mixed DRHPs). Available via AWS Bedrock.

### Vector DB — Winner: Supabase pgvector

| Criterion | Pinecone Serverless | Upstash Vector | Supabase pgvector |
|-----------|--------------------|-----------------|--------------------|
| Vercel-friendly | Yes | Yes (HTTP REST) | Yes (connection pooler) |
| Metadata filters | JSON subset | SQL-like nested | **Full SQL WHERE + JOIN** |
| Hybrid BM25+dense | Native alpha param | No native BM25 | tsvector + pgvector one query |
| Pricing < 5M vectors | $0.096/1M reads | Free tier | Free / ~$25 base |
| ACID + relational | No | No | **Yes** |

**Decision: Supabase pgvector.** `WHERE section_type = 'objects_of_issue' AND drhp_id = 'vikram-solar-2024'` in one SQL. JOIN `drhp_metadata` for multi-DRHP corpus queries. Decisive for section-aware queries.

Sources: [LangGraph Send API](https://medium.com/@vinodkrane/next-generation-agentic-rag-with-langgraph-2026-edition-d1c4c068d2b8) · [Contextual Retrieval — Anthropic](https://www.anthropic.com/news/contextual-retrieval) · [pgvector vs Pinecone — Supabase](https://supabase.com/blog/pgvector-vs-pinecone) · [Cohere Rerank 3.5 — AWS Bedrock](https://aws.amazon.com/blogs/machine-learning/cohere-rerank-3-5-is-now-available-in-amazon-bedrock-through-rerank-api/)

---

## 2. SEBI DRHP Corpus Specifics

### URL Structure

```
# DRHP listing (smid=10):
https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=3&ssid=15&smid=10

# Per-company filing page:
https://www.sebi.gov.in/filings/public-issues/{month-year}/{company-slug}_{filing-id}.html

# Direct PDF:
https://www.sebi.gov.in/sebi_data/attachdocs/{month-year}/{ts}_{doc-id}.pdf

# BSE alternative (faster PDF availability):
https://www.bseindia.com/corporates/download/{company-id}/IPO Prior/{filename}.pdf

# NSE archives:
https://nsearchives.nseindia.com/corporate/{filename}.pdf
```

Better structured HTML: `https://www.sebi.gov.in/filings/public-issues.html`

### Scraping

DRHPs are public disclosures under SEBI ICDR Regulations 2018 — legal. Use `httpx` async with 1-2s delays, standard browser UA, cache PDFs in Supabase Storage after first fetch. Supplement with `chittorgarh.com` and `unlistedzone.com` (clean DRHP indexes).

### OCR vs Native

2024-2026 main-board DRHPs are native PDFs — PyMuPDF extracts cleanly. Older SME DRHPs (pre-2022) may have scanned annexures — detect with empty `get_text()`, trigger Tesseract OCR fallback.

### 5 Test Corpus DRHPs

| Company | Sector | URL | Pages |
|---------|--------|-----|-------|
| Tata Technologies | Engineering/IT | [Mar 2023](https://www.sebi.gov.in/filings/public-issues/mar-2023/tata-technologies-limited_68881.html) | 530 |
| ixigo | Travel-tech | [Feb 2024](https://www.sebi.gov.in/filings/public-issues/feb-2024/le-travenues-technology-limited-drhp_81469.html) | 480 |
| Vikram Solar | Renewable | [Oct 2024](https://www.sebi.gov.in/filings/public-issues/oct-2024/vikram-solar-limited_87278.html) | 600 |
| Swiggy | Food-tech | [Sep 2024](https://www.sebi.gov.in/filings/public-issues/sep-2024/swiggy-limited-updated-drhp-i_87047.html) | 800 |
| Hyundai Motor India | Auto | [Jun 2024](https://www.sebi.gov.in/filings/public-issues/jun-2024/hyundai-motor-india-limited-drhp_84186.html) | 700 |

Primary stress-test: **Swiggy** (largest, complex promoter, multiple litigation) + **Vikram Solar** (capex-intensive, fund-use flags). **Hyundai India** for revenue-concentration testing (single OEM parent).

---

## 3. PDF Parsing Toolkit 2026

### Benchmark (Procycons, March 2026)

| Parser | Table Cell Accuracy | TOC Reconstruction | 1-page | 50-page | License |
|--------|---------------------|--------------------|--------|---------|---------|
| **Docling** (IBM) | **97.9%** | **100% fidelity** | 6.3s | 65s | MIT (free) |
| LlamaParse | 100% numerical, **0% column placement** | Structural failure | 6s | 6s | API $0.003/page |
| Unstructured hi_res | 75% | Near-complete failure | 51s | 141s | Apache 2 |
| PyMuPDF4LLM | ~85% simple tables | Good (native outline) | <1s | <5s | AGPL |
| pypdf | ~60% | Poor | <1s | <2s | MIT |

**Critical:** LlamaParse's 0% column placement = promoter pledge tables come out structurally wrong = false red flags. Docling 97.9% is required. 58,600+ GitHub stars, IBM Research.

### Tiered Pipeline

```
DRHP PDF
    |
[PyMuPDF] — page count + native outline extraction (<2s)
    |-- Outline found? use as section boundaries
    |-- No outline? heuristic heading detection
    |
[Docling hi_res] — full structural parse (tables + layout)
    |
[PyMuPDF4LLM] — export to GitHub-flavored Markdown
    |
[Section-aware chunker]
    |
[claude-haiku-4-5 batch] — contextual prefix generation (once)
    |
[voyage-3-large] — embedding
    |
[Supabase pgvector upsert]
```

```python
import fitz
doc = fitz.open("drhp.pdf")
toc = doc.get_toc()  # [(level, title, page_num), ...]
# Main-board DRHPs: 30-80 TOC entries
```

Sources: [PDF Data Extraction Benchmark 2025 — Procycons](https://procycons.com/en/blogs/pdf-data-extraction-benchmark/) · [Docling GitHub](https://github.com/docling-project/docling) · [Best PDF Parsers 2026 — Firecrawl](https://www.firecrawl.dev/blog/best-pdf-parsers)

---

## 4. Red-Flag Agent Schemas (Pydantic v2)

### Agent 1: Promoter Pledge Extractor

```python
class PromoterHolding(BaseModel):
    promoter_name: str
    total_shares: int
    pledged_shares: int
    pledge_percentage: float = Field(..., ge=0, le=100)
    pledge_value_cr: Optional[float] = None

class PromoterPledgeReport(BaseModel):
    drhp_id: str
    company_name: str
    aggregate_pledge_pct: float
    holdings: List[PromoterHolding]
    red_flag_level: Literal["NONE", "MODERATE", "HIGH", "CRITICAL"]
    red_flag_rationale: str
    source_chunks: List[str]   # mandatory chunk_ids
    source_pages: List[int]
    confidence: float = Field(..., ge=0, le=1)
```

Thresholds: `> 50%` aggregate = HIGH; `> 75%` = CRITICAL.

### Agent 2: Litigation Risk Summariser

```python
class LitigationItem(BaseModel):
    case_type: Literal["Tax Dispute", "Consumer", "Criminal", "SEBI Investigation", "Other"]
    parties: str
    claim_amount_cr: Optional[float] = None
    outcome_risk: Literal["LOW", "MEDIUM", "HIGH"]
    summary: str = Field(..., max_length=300)
    source_chunk_id: str
    source_page: int

class LitigationRiskReport(BaseModel):
    drhp_id: str
    total_litigation_items: int
    total_contingent_liability_cr: Optional[float] = None
    sebi_investigations: List[LitigationItem]
    criminal_proceedings: List[LitigationItem]
    material_tax_disputes: List[LitigationItem]
    aggregate_risk_level: str
    synthesis: str = Field(..., max_length=500)
    source_chunks: List[str]
```

Multi-chunk synthesis: top-20 chunks → single LLM call with CoT: enumerate → classify → flag SEBI/CBI/ED as CRITICAL → sum contingent liabilities. Haiku 4.5 for speed; escalate to Sonnet 4.6 if chunks > 8K tokens.

### Agent 3: Objects of Issue Classifier

```python
class FundAllocationItem(BaseModel):
    purpose: str
    amount_cr: float
    percentage_of_total: float
    category: Literal["CAPEX", "PROMOTER_DEBT_REPAYMENT", "WORKING_CAPITAL", "ACQUISITION", "GENERAL_CORPORATE", "OFFER_EXPENSES"]
    red_flag: bool
    red_flag_reason: Optional[str] = None
    source_chunk_id: str
    source_page: int

class ObjectsOfIssueReport(BaseModel):
    drhp_id: str
    total_issue_size_cr: float
    fresh_issue_cr: float
    ofs_cr: float   # money to existing shareholders, NOT company
    fund_allocation: List[FundAllocationItem]
    promoter_debt_repayment_pct: float
    red_flag_level: str
    key_concerns: List[str]
```

Triggers: `ofs_cr / total > 0.7` = CRITICAL; any `PROMOTER_DEBT_REPAYMENT` = HIGH; `GENERAL_CORPORATE > 30%` = MODERATE.

### Agent 4: Revenue Concentration Detector

```python
class RevenueConcentrationReport(BaseModel):
    drhp_id: str
    top_customer_pct: float
    top_5_customers_pct: float
    single_customer_above_40_pct: bool
    geographic_concentration_risk: Optional[str] = None
    red_flag_level: str
    synthesis: str
```

Thresholds: `top_customer_pct > 40%` = HIGH; `> 30%` = MODERATE. Indian DRHPs anonymize "Customer A, B, C" — extract percentages regardless.

---

## 5. Section-Aware Chunking — Fuzzy Normalization

```python
DRHP_SECTIONS = {
    "definitions": "Definitions and Abbreviations",
    "risk_factors": "Risk Factors",
    "business_overview": "Business Overview",
    "objects_of_issue": "Objects of the Issue",
    "financial_statements": "Audited Financial Statements / Restated Financials",
    "mda": "Management's Discussion and Analysis",
    "promoter_background": "Our Promoters and Promoter Group",
    "legal_proceedings": "Outstanding Litigation and Material Developments",
    "capital_structure": "Capital Structure",
    "other_regulatory": "Other Regulatory and Statutory Disclosures",
}

from rapidfuzz import process, fuzz

def normalize_section_type(raw_title: str) -> str:
    candidates = [v.upper() for v in DRHP_SECTIONS.values()]
    match, score, _ = process.extractOne(raw_title.upper(), candidates, scorer=fuzz.partial_ratio)
    return {v.upper(): k for k, v in DRHP_SECTIONS.items()}[match] if score >= 80 else "other"
```

### Chunk metadata schema

```python
class DRHPChunk(BaseModel):
    chunk_id: str            # "{drhp_id}_{section_type}_{idx}"
    drhp_id: str
    company_name: str
    year: int
    section_type: str
    page_range: tuple[int, int]
    chunk_index: int
    text: str
    contextual_prefix: str   # Anthropic prepend
    is_table: bool
    table_type: Optional[Literal["promoter_pledge", "fund_use", "financials"]]
    parent_chunk_id: Optional[str]
    token_count: int
    is_sme_ipo: bool
```

---

## 6. Hybrid Query — Supabase pgvector SQL

```sql
SELECT chunk_id, section_type, text,
    (0.7 * (1 - (embedding <=> $query_embedding))
     + 0.3 * ts_rank(search_vector, plainto_tsquery($query_text))) AS hybrid_score
FROM drhp_chunks
WHERE drhp_id = $drhp_id
    AND section_type = ANY($section_types)
    AND search_vector @@ plainto_tsquery($query_text)
ORDER BY hybrid_score DESC
LIMIT 20;
```

Pinecone uses `sparse_vector=bm25_sparse, alpha=0.7`. Upstash supports metadata filter but no native BM25 — post-filter only. Supabase wins on full SQL pre-filter.

---

## 7. India SEBI Compliance + Safety

### Critical 2025-2026 Legal Position

1. **"Educational only" disclaimers have ZERO protection** if output contains buy/sell signals. SEBI IA Regulations 2013 apply regardless of labeling. Confirmed in enforcement orders.
2. **SEBI AI Accountability Framework (2026):** AI users bear full legal responsibility. P2 must NEVER generate recommendations.
3. **Jan 2025 SEBI circular:** Educational content cannot use stock prices from preceding 3 months. Pre-IPO DRHP analysis unaffected; GMP references prohibited.
4. DRHPs are public documents under SEBI ICDR Regulations 2018 — educational analysis legal.

### Hard Refusal Patterns

```python
PROHIBITED_QUERY_PATTERNS = [
    r"should i (apply|invest|buy|subscribe)",
    r"is (this|the) ipo (good|bad|worth it)",
    r"(listing|allotment) (gain|return|profit)",
    r"(buy|sell|hold) recommendation",
    r"target price",
    r"overvalued|undervalued",
    r"will (the )?(stock|share) (go up|rise|fall)",
]
```

### Citation Format

`[Source: Vikram Solar DRHP (Oct 2024) | Section: Objects of Issue | Page 187 | sebi.gov.in]`

### Persistent Disclaimer (every report header + card footer + first-run modal)

```
Analysis based on public SEBI filings. Educational use only.
Not investment advice. Not affiliated with SEBI.
Consult a SEBI-registered adviser before investing.
```

Sources: [SEBI Digital Compliance Rules 2026 — Mondaq India](https://www.mondaq.com/india/securities/1759228/sebis-new-digital-compliance-rules-what-investment-advisers-must-know-in-2026) · [SEBI Finfluencer Clampdown — BusinessToday](https://www.businesstoday.in/markets/stocks/story/sebis-clampdown-on-finfluencers-cannot-use-live-stock-market-data-in-educational-content-462704-2025-01-31)

---

## 8. RAG Eval Framework

### Metrics

| Metric | Target | Tool |
|--------|--------|------|
| Faithfulness | > 0.90 | Ragas |
| Citation Accuracy | > 0.85 | Custom (chunk_id + page match) |
| Section-Match Accuracy | > 0.88 | Custom (metadata check) |
| Answer Relevancy | > 0.82 | Ragas |
| Context Precision | > 0.75 | Ragas |
| Refusal Rate (prohibited) | 100% | Custom regex |

Faithfulness is P0 — hallucinated pledge ratio or missed SEBI investigation = product-ending.

### Benchmarks

- **FinanceBench** (Patronus): 10,231 QA over real financial PDFs. SOTA Mafin 2.5 = 98.7%
- **FinanceQA** (Jan 2025): financial analysis over long docs
- **HierFinRAG**: 82.5% EM on FinQA, hierarchical approach

### 30-Question Golden Set Distribution

- **Objects of Issue (10):** debt repayment %, fresh vs OFS split, allocation categories, promoter selling, capex, timeline, GC %, working cap, acquisitions, vagueness
- **Promoter (10):** aggregate pledge %, identities, SEBI actions, related-party txns, post-IPO equity, lock-ins, encumbrances, acquisition cost, tenure, experience
- **Litigation (10):** total proceedings, contingent liability, SEBI investigations, tax disputes, criminal, largest claim, consumer, regulatory penalties, IP, material developments

Run on Swiggy + Vikram Solar with human-verified ground truth.

Sources: [Ragas Faithfulness](https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/faithfulness/) · [FinanceBench — Patronus AI](https://github.com/patronus-ai/financebench) · [HierFinRAG — MDPI 2025](https://www.mdpi.com/2227-9709/13/2/30) · [FinSage Multi-Aspect RAG — arXiv 2504.14493](https://arxiv.org/pdf/2504.14493)

---

## 9. Frontend Stack 2026

**File upload:** Vercel Edge → Supabase Storage → trigger Modal background worker → return `{job_id}`.

**Report streaming:** Next.js 15 App Router SSE endpoint streaming LangGraph results. `for await (const chunk of runRedFlagPipeline(drhpId))` pattern.

**PDF Viewer: `react-pdf-highlighter-extended`** (DanielArnould fork) — actively maintained, viewport-independent highlights, pdf.js-dist base, Next.js 15 compatible via `"use client"`.

**Citation UX:** HoverCard preview → Sheet/Dialog full PDF view with highlight scrolled to page. Linear.app issue detail = UX reference.

**shadcn/ui v4 components:**
- Card + Badge variant="destructive" — red flag cards
- Tabs + TabsList — per-agent report sections
- Skeleton — per-section loading during stream
- Accordion — expandable risk-factor list
- Alert — persistent non-dismissable disclaimer
- HoverCard — citation tooltip
- Sheet + Dialog — citation PDF drawer

Sources: [shadcn/ui v4 March 2026](https://ui.shadcn.com/docs/changelog/2026-03-cli-v4) · [react-pdf-highlighter-extended](https://github.com/DanielArnould/react-pdf-highlighter-extended)

---

## 10. Finance / Regtech UI References (2026)

1. **Tickertape (tickertape.in)** — 6M+ users. "SmartScore" badge = direct template for P2 severity badges (color + icon + label + number).
2. **Screener.in** — Citation-first philosophy. Every number links to source. P2 must mirror.
3. **Linear.app** — Citation drawer UX reference (hover → inline preview → click → full detail).
4. **Fortress shadcn/ui template** — Bloomberg-style data density for institutional finance.
5. **Awwwards Fintech SOTD** — Dark sidebar + light content + OKLCH accent + monospaced numbers.
6. **Anthropic Claude.ai** — Streamed analysis with source chips below each section.

### Calm Finance OKLCH Palette

```css
--color-background:  oklch(0.98 0.005 240);   /* Off-white cool tint */
--color-surface:     oklch(0.96 0.006 240);
--color-critical:    oklch(0.55 0.200 25);    /* Red */
--color-high:        oklch(0.65 0.180 50);    /* Orange */
--color-moderate:    oklch(0.75 0.150 80);    /* Amber */
--color-none:        oklch(0.55 0.140 150);   /* Green */
--color-accent:      oklch(0.55 0.120 240);   /* Brand blue */
```

Rules: No gradients on data. No animations on numbers. `font-variant-numeric: tabular-nums` for all financial figures.

Sources: [Fintech Design Guide 2026 — Eleken](https://www.eleken.co/blog-posts/modern-fintech-design-guide) · [Fintech UX Trust Patterns — Phenomenon Studio](https://phenomenonstudio.com/article/fintech-ux-design-patterns-that-build-trust-and-credibility/)

---

## 11. Anti-Patterns — Strict Prohibition

1. **Vanilla "summarize this PDF" wrapper** — ChatPDF with SEBI skin. Build structured red-flag extraction with Pydantic schemas.
2. **Generic chatbot copy** — "Welcome to your AI IPO assistant!" — UX must be an audit report, not chat.
3. **Confident verdicts** — "This IPO is overvalued!" — prohibited legally and epistemically.
4. **No citation traceability after synthesis** — every atomic claim must trace to chunk_id + page.
5. **Crashing on large PDFs** — test Swiggy ~800 pages in CI. Stream Docling output, never load full result in memory.
6. **Fixed-vocabulary section detection** — use rapidfuzz 80% threshold. "Outstanding Litigations" maps to "Legal Proceedings."
7. **Embedding financial tables as plain text** — always use table metadata prefix with row-column structure.
8. **Single-shot retrieval, no reranking** — hybrid BM25 + dense + Cohere reranker-v3.5 required.
9. **Ignoring OFS component** — OFS proceeds go to existing shareholders, not the company. Critical red flag.
10. **Skipping SME vs Main Board distinction** — tag `is_sme_ipo: bool`; add UI disclaimer for SME.
11. **Ignoring Hindi/English mixed text** — Cohere reranker handles 100+ languages; BM25 tokenizer must handle Devanagari.

Sources: [DRHP Red Flags Guide — Gretex Corporate](https://gretexcorporate.com/blog/understanding-drhp-complete-guide-to-indias-ipo-investors/)

---

## 12. Performance Budget for Vercel — Split Execution Model

### Core constraint

Vercel serverless: 300s max. Docling on 600-page DRHP: ~17 min. **Cannot run in Vercel Function. Requires split execution.**

### Architecture

```
User uploads PDF (<5s)
    |
[Vercel Edge Function] — store Supabase Storage, return job_id
    |
[Modal.com — 8 vCPU, 16GB RAM, 30min timeout]
    --> Docling parse (~8-10 min, 600 pages)
    --> Section-aware chunking
    --> Contextual prefix gen (claude-haiku-4-5 batch)
    --> voyage-3-large embedding
    --> Supabase pgvector upsert
    --> Webhook: "ingestion complete"
    |
[Vercel Fluid Compute — maxDuration 300s, 3008MB]
    --> LangGraph 5-agent parallel (<60s)
    --> SSE stream to frontend
```

| Step | Target |
|------|--------|
| PDF upload + storage | < 5s |
| Docling parse 600pp | < 15 min (Modal 8 vCPU) |
| Voyage embedding 5K chunks | < 45s (2K tokens/sec) |
| pgvector upsert | < 20s (100/batch) |
| **Total background ingest** | **< 20 min** |
| First red-flag report post-ingest | < 15s |
| TTFT | < 3s (SSE) |
| Full report | < 60s (5 parallel agents) |

Note: "<90s ingest" from candidate spec NOT achievable with CPU Docling. Realistic: 15-20 min background. Acceptable UX — upload + come back. **Pre-index Swiggy/Hyundai/Vikram/ixigo/Tata Tech at launch** so first-time demo is instant. MD5 hash dedup skips re-ingest.

**Modal cost:** ~$0.0004/vCPU-s × 8 × 600s = **~$0.19/DRHP parse**.

Sources: [Vercel Fluid Compute](https://vercel.com/docs/fluid-compute) · [Vercel Function Timeouts](https://vercel.com/kb/guide/what-can-i-do-about-vercel-serverless-functions-timing-out) · [Next.js Background Jobs 2026 — Render](https://render.com/articles/nextjs-background-jobs-postgresql-production)

---

## Full Stack Summary

| Layer | Choice | Why |
|-------|--------|-----|
| Agent Orchestration | LangGraph 0.3+ Send API | Map-reduce fan-out, PostgresSaver |
| PDF Parsing | Docling + PyMuPDF | 97.9% table accuracy; native TOC |
| Embeddings | voyage-3-large | MTEB 67.1, regulatory domain |
| Reranker | cohere-rerank-v3.5 | +23.4% finance domain |
| Vector DB | Supabase pgvector | Full SQL filters + tsvector hybrid |
| Hybrid BM25 | pg_search (Supabase tsvector) | One-query hybrid |
| Structured Output | Pydantic v2 + Instructor | Type-safe agent outputs |
| Frontend | Next.js 15 App Router | RSC + streaming |
| UI Components | shadcn/ui v4 + Radix | Own-your-components, a11y |
| PDF Viewer | react-pdf-highlighter-extended | Viewport-independent highlights |
| Background Worker | Modal.com | $0.19/DRHP, 8 vCPU |
| Eval | Ragas + 30Q golden set | Faithfulness + Section-Match |
| Compliance | Hard refusal regex + disclaimer | SEBI IA Regs + 2025-2026 circulars |

**Confidence: High** — Sources from 2025-2026 publications, official docs, benchmarks. SEBI URLs verified live. Docling benchmark from Procycons March 2026 study (1000+ pages).
