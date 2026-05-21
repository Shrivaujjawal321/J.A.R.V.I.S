# RAG Decathlon — Top-10 Roadmap (Phase 2 Output)

**Generated**: 2026-05-14 by Jarvis after Phase 1 parallel research (8 domains × 5 candidates = 40 scouted)
**Status**: ⏳ AWAITING BOSS APPROVAL — gate before Phase 3 build begins
**Selection method**: scored each candidate on `impact × novelty × portfolio-leverage × technical-stretch × buildability`, then ordered by difficulty curve so each project adds a new 2026 RAG technique vs the previous.

---

## How to read this roadmap

Each project card has:
- **Slug** — used for repo + Vercel subdomain
- **RAG technique** — the 2026 SOTA pattern this project demonstrates
- **Hours / Complexity (c) / Portfolio leverage (l)** — estimates from Phase 1 research
- **Why this slot** — why it's at this position in the difficulty curve
- **Recruiter pitch** — the one-liner for the resume bullet / portfolio card

Boss can:
- ✅ Approve as-is — kick off P1 build
- 🔄 Swap any project — tell me which # → which alternate from `research/candidates-*.yaml` (40-candidate bank)
- ⏭️ Re-order — change the difficulty curve
- ✂️ Drop count — ship fewer than 10

---

## The Curve (P1 → P10)

| # | Slug | Domain | RAG Technique | Hours | c | l |
|---|------|--------|---------------|-------|---|---|
| **P1** | `glp1-nutrition-copilot` | Healthcare | Hybrid + rerank | 7 | 5 | 9 |
| **P2** | `sebi-drhp-redflag-radar` | Finance (India) | Agentic + structured + section-aware chunking | 7 | 6 | 9 |
| **P3** | `promptwatch` | DevTools | Memory-augmented + CI-native | 6 | 6 | 8 |
| **P4** | `mcp-sentinel` | DevTools / Security | Hybrid + rerank + structured CVE matching | 7 | 7 | **10** |
| **P5** | `claim-auditor` | Creative / Media | Multi-source agentic (5 parallel sources) | 7 | 6 | 9 |
| **P6** | `arxiv-feynman` | Education / AI/ML | Multimodal RAG (text + figures + equations) | 8 | 7 | 9 |
| **P7** | `cbt-dbt-compass` | Healthcare / Mental Health | Memory-augmented + agentic + safety-first | 8 | 7 | **10** |
| **P8** | `upsc-rag-grader` | Education (India) | Agentic + claim-verification + hybrid | 9 | 8 | **10** |
| **P9** | `graphblast` | DevTools (Code) | GraphRAG via AST | 9 | 9 | 9 |
| **P10** | `deallens` | Agentic / VC | **Agentic GraphRAG + MA-RAG + live KG viz** | 11 | 9 | **10** |

**Totals**: ~79 hrs active build, ~$60-80 LLM, capstone projects deliberately stretch into 9-11 hrs.

---

## P1 — glp1-nutrition-copilot

**Tagline**: Hybrid RAG over 200+ peer-reviewed papers + USDA data — fills the documented GLP-1 micronutrient guidance gap.

**Problem**: ~15M US adults on GLP-1 agonists (Ozempic, Wegovy, Mounjaro) lose 20-50% lean mass without correct protein/micronutrient intake; >60% deficient in iron/calcium per 2026 clinical studies. No structured guidance tool at point of need.

**Why P1**: Smallest scope (7h, c5) but production-grade hybrid+rerank fundamentals. Clean win to establish workflow. Fully cited clinical RAG over PubMed + USDA + NIH ODS. Safe and well-bounded.

**Why now 2026**: Feb 2026 Nature IJO paper names the "nutrition guidance gap." 2026 Wiley Clinical Obesity review catalogued specific deficiencies. FDA approved 3 new GLP-1 variants late 2025.

**Data**: PubMed (NCBI E-utilities, free) · USDA FoodData Central · NIH Office of Dietary Supplements · ASMBS guidelines

**Stack 2026**: Voyage embed-3 + Cohere Rerank v3 + Claude Haiku 4.5 + Next 15 + Tailwind 4 + Upstash Vector + Vercel

**Safety**: Disclaimer banner ("Not a substitute for a registered dietitian"). Refuses dose/medication-change questions. PMID-linked sources. Stateless.

**Recruiter pitch**: *"RAG-powered nutrition advisor for GLP-1 users — retrieves from 200+ peer-reviewed papers and USDA data to fill the documented micronutrient-guidance gap, with every answer citing the source paper."*

---

## P2 — sebi-drhp-redflag-radar

**Tagline**: Agentic RAG over SEBI Draft Red Herring Prospectuses — surfaces promoter red flags, IPO-fund misuse, and litigation landmines before retail investors apply.

**Problem**: India sees 50-80 DRHP filings/year on SEBI (400-900 pages each). Retail investors miss buried "Objects of Issue" diversion to promoter debt, 50+ pages of litigation, micro-font pledge tables, and revenue-concentration footnotes. No free DRHP forensics tool exists.

**Why P2**: Introduces agentic 5-step pipeline + section-aware chunking (architectural advance over P1's flat chunking). India-specific = direct recruiter signal for Zerodha / Groww / CoinDCX. 2026 mega-IPO wave (Vikram Solar, Curefoods) = fresh demand.

**Stack 2026**: LangGraph + Unstructured.io + LlamaIndex SentenceSplitter with metadata + Chroma + Cohere Rerank v3 + Claude Sonnet 4.6 + Next 15 + Vercel

**Safety**: "Educational only. NOT investment advice." Every claim cited to DRHP page+section. [INFERRED] vs [STATED IN DRHP] labels.

**Recruiter pitch**: *"Agentic RAG over SEBI Draft Red Herring Prospectuses — section-aware chunking + 5-agent pipeline extracts promoter red flags, litigation landmines, and revenue-concentration risks before retail investors apply."*

---

## P3 — promptwatch

**Tagline**: Memory-augmented RAG over your golden test set + GitHub Action — prompts ship with regression gates like code.

**Problem**: LLM products ship prompt changes with no regression gate. A three-word edit silently breaks a revenue pipeline; provider-side model updates drift outputs without code change. promptfoo/DeepEval are eval frameworks needing 2h+ setup — no zero-friction GitHub Action with golden-set RAG core exists.

**Why P3**: Introduces memory-augmented RAG (the golden set IS the memory corpus). Smallest of the 10 (6h, c6). CI-native = every recruiter at Anthropic / Cohere / Braintrust recognises pattern instantly.

**Why now 2026**: Feb 2026 longitudinal study confirmed "meaningful behavioral drift in deployed transformer services." Martin Fowler published SPDD treating prompts as first-class artifacts.

**Stack 2026**: Chroma + sentence-transformers + Claude Haiku 4.5 + GitHub Actions + Next 15 dashboard + Vercel

**Recruiter pitch**: *"Memory-augmented RAG that embeds a golden test corpus, retrieves semantically matched cases on each prompt commit, runs behavioral regression evals, and posts a drift report as a GitHub Actions PR check."*

---

## P4 — mcp-sentinel (⭐ HIGHEST PORTFOLIO LEVERAGE 10/10)

**Tagline**: Hybrid RAG over CVE/OSV/GitHub Advisory corpora — audits MCP server tool descriptions for supply-chain poisoning and known CVE patterns.

**Problem**: April-May 2026 OX Security disclosed systemic MCP RCE affecting 150M+ downloads + 200k servers. The Register (2026-05-13) reported three unpatched MCP database flaws. CVE-2026-30623 (CVSS 9.8 NGINX MCP) + 30+ MCP CVEs filed Jan-Feb 2026. Anthropic declined to patch the STDIO architectural flaw → developers carry the risk with no semantic audit tooling.

**Why P4**: Anthropic-native problem. Highest portfolio leverage (10/10) — directly targets the protocol Boss's actual job-search audience cares about. Adds structured CVE-schema retrieval on top of P1's hybrid+rerank.

**Stack 2026**: Voyage embed-3 + BM25 + Cohere Rerank v3 + Claude Sonnet 4.6 + Pydantic v2 schemas + Next 15 + Vercel

**Recruiter pitch**: *"MCP-Sentinel: hybrid RAG (BM25 + dense + rerank) over CVE/OSV/GitHub Advisory corpora that audits MCP server tool descriptions for supply-chain poisoning and known CVE patterns — addressing the systemic 2026 MCP security gap affecting 200k servers."*

---

## P5 — claim-auditor

**Tagline**: Multi-source agentic RAG over PolitiFact + Snopes + Wikipedia + OpenAlex + NewsAPI — claim-by-claim audit of any op-ed with a shareable card.

**Problem**: Editors, fact-checkers, readers need traceable claim verification. Factiverse/Full Fact AI are B2B. EU AI Act Article 50 (Aug 2026) + CA SB 942 (Jan 2026) create compliance pressure on media. AI-generated text hit 16% of fact-checked claims in 2025.

**Why P5**: Introduces multi-source parallel agentic retrieval (LangGraph fan-out). 5 retrieval tools running concurrently is a production pattern Anthropic/Stripe interview specifically for. Satori OG-image audit card = viral product mechanic.

**Stack 2026**: LangGraph fan-out + 5 retrieval APIs + Cohere Rerank v3 + Satori OG-cards + Next 15 + Vercel Edge

**Recruiter pitch**: *"Claim auditor for op-eds — LLM claim decomposition + 5-source parallel agentic RAG across PolitiFact, Snopes, OpenAlex, Wikipedia, NewsAPI; per-claim VERIFIED/CONTESTED verdicts with shareable audit cards. Targets EU AI Act Article 50 compliance."*

---

## P6 — arxiv-feynman

**Tagline**: Multimodal RAG over arXiv PDFs — actually reads the figures, equations, and tables; explains at 5 Feynman depth levels.

**Problem**: ExplainPaper, SciSpace, Elicit explain text well but are BLIND to figures, equations, tables. "Attention Is All You Need" is 40% figures and equations — current tools skip them or hallucinate. Researchers on r/MachineLearning flag this as #1 frustration.

**Why P6**: First multimodal RAG project in the curve. Dual-index architecture (text → vector store, figures → image-LLM-described store). voyage-3 + GPT-4o-mini Vision for figure description. AI/ML recruiters all read papers — instant personal-use credibility.

**Why now 2026**: UniDoc-Bench (arXiv 2510.03663) + MegaRAG (arXiv 2512.20626) + FeynmanBench (arXiv 2604.03893) validate multimodal RAG. GPT-4o-mini Vision at $0.001/image makes it affordable.

**Stack 2026**: pymupdf + GPT-4o-mini Vision OCR + dual-namespace Qdrant + Claude Sonnet 4.6 + structured Pydantic Feynman-level output + Next 15 + Vercel

**Recruiter pitch**: *"Multimodal RAG paper explainer — unlike ExplainPaper, actually reads the figures, equations, tables in arXiv PDFs. Ask 'explain Figure 3' and get a grounded visual answer at 5 Feynman depth levels."*

---

## P7 — cbt-dbt-compass

**Tagline**: Memory-augmented RAG over 150+ CBT/DBT/ACT RCT papers — matches journal entry to evidence-supported technique with PMID citation; adapts across sessions.

**Problem**: People on therapy waitlists (UK NHS 18-week avg; US 3-6 mo) use journaling to self-manage but have no evidence-based guidance on which CBT/DBT/ACT technique fits their logged emotional state. Woebot/Wysa use proprietary scripted flows — no citations, no memory across sessions.

**Why P7**: Advances P3's memory-augmented pattern to session-spanning emotional-pattern memory + adds heavy safety scaffolding (crisis detection → 988 redirect). Mental health is highest-engagement consumer AI vertical in 2026. Memory-augmented RAG = direct 2026-SOTA signal.

**Stack 2026**: Chroma (rolling embedding summary, no raw journal text) + sentence-transformers + Claude Haiku 4.5 + Claude Sonnet 4.6 + Next 15 + Vercel

**Safety**: Crisis-keyword detection → immediate 988/Samaritans redirect with zero LLM response. No DSM diagnosis terms. Stateless raw text; only anonymised embedding summary persisted (user-deletable).

**Recruiter pitch**: *"Memory-augmented RAG therapy-technique matcher — retrieves best-evidence CBT/DBT/ACT technique from 150+ RCT papers, adapts across sessions via rolling emotional-pattern memory — cited, not scripted."*

---

## P8 — upsc-rag-grader

**Tagline**: Agentic RAG-grounded UPSC Mains evaluator — verifies every factual claim against PIB, NCERT, government reports. Catches the wrong facts pure-LLM graders miss.

**Problem**: UPSC Mains answer writing has the hardest feedback loop in Indian exams. CollectorBabu (170K+ answers), SuperKalam, Dalvoy all score on structure and keywords — NONE verify facts. Students get confidence boosts on factually wrong answers — dangerous failure mode.

**Why P8**: Full agentic pipeline (Answer Segmentation → atomic claim extraction → parallel claim-level hybrid retrieval → tagged [VERIFIED/UNVERIFIED/CONTRADICTED]). Highest portfolio leverage among India projects. ~0.5M UPSC aspirants annually + ~12M registered over years = obvious market for Indian recruiters.

**Stack 2026**: LangGraph + structured Pydantic claim schemas + Upstash Vector/Supabase pgvector + BM25 hybrid + Claude Sonnet 4.6 + Next 15 + Vercel

**Recruiter pitch**: *"RAG-grounded UPSC answer evaluator — verifies every factual claim against PIB, NCERT, government reports. Catches the wrong facts pure-LLM graders miss."*

---

## P9 — graphblast

**Tagline**: GraphRAG over AST-derived monorepo dependency graph — multi-hop traversal on a PR diff to compute blast radius with human-readable risk report.

**Problem**: In a monorepo, a change to one shared utility silently breaks 15 downstream packages. Human reviewers cannot trace multi-hop chains at review time. AI tools (Copilot, Cursor) use flat vector retrieval — miss structural blast radius. `nx affected` outputs package lists, not risk explanations.

**Why P9**: First pure-GraphRAG project (no vector RAG fallback). AST-to-graph pipeline + multi-hop traversal is technically the most ML-engineering-rigorous build in the curve. Aligns directly with 2026 arxiv research (TDAD: 2603.17973, AST-vs-KG: 2601.08773). Spectro Cloud Jan 2026: "AI is turning 2026 into year of the monorepo."

**Stack 2026**: tree-sitter + NetworkX (or FalkorDB) + LlamaIndex PropertyGraph + Voyage voyage-code-3 + Claude Sonnet 4.6 + React Flow viz + Next 15 + Vercel

**Recruiter pitch**: *"GraphBlast: GraphRAG system that constructs an AST-derived call/import graph over a monorepo, performs multi-hop traversal on a PR diff to compute blast radius, and generates a human-readable risk report citing affected packages, transitive dependents, and uncovered test paths."*

---

## P10 — deallens (⭐ CAPSTONE)

**Tagline**: Agentic GraphRAG + MA-RAG due-diligence memo generator with live KG visualization. The most architecturally rich project in the decathlon.

**Problem**: Angel investors / founders / VCs doing competitive analysis spend 4-8 hours per company on manual research. Crunchbase/PitchBook are static. Perplexity gives flat answers. Nobody ships GraphRAG-guided multi-agent structured memo that builds the KG live and reasons along entity relationships.

**Why P10 (capstone)**: Brings together EVERY technique used in P1-P9: hybrid+rerank (per-entity vector search), agentic loops (KG navigator), multi-agent supervision (Researcher + Validator + Skeptic), GraphRAG (live-built knowledge graph), structured output (Pydantic InvestorMemo), live web crawl (Firecrawl), and React Flow visualization. Directly relevant to Cognition (Devin) / Sierra / a16z portfolio.

**Stack 2026**: LangGraph + Firecrawl + NetworkX KG + Qdrant + Cohere Rerank v3 + Claude Sonnet 4.6 (×3 worker agents) + React Flow + Next 15 + Vercel streaming

**Recruiter pitch**: *"DealLens: Agentic GraphRAG due-diligence memo generator. Live KG construction over Founders→Products→Competitors→Investors. Multi-agent system (Researcher / Validator / Skeptic) collaborates via chain-of-thought to write a structured investor memo with provenance trail — each claim cited to source URL. React Flow visualizes the agent's internal reasoning path through the KG."*

---

## Technique Coverage Check (Boss approved this rule — each project adds something)

| Technique | First introduced | Reinforced in |
|-----------|-----------------|---------------|
| Hybrid + rerank | P1 | P4, P8 |
| Agentic + structured | P2 | P5, P8, P10 |
| Memory-augmented | P3 | P7 |
| Multi-source parallel agentic | P5 | P10 |
| Multimodal RAG | P6 | — |
| Safety scaffolding (crisis detection) | P7 | — |
| GraphRAG | P9 | P10 |
| Multi-agent (MA-RAG) | P10 | — |
| Live web crawl + KG construction | P10 | — |

✅ All major 2026 RAG patterns covered.

---

## Domain Spread

- **DevTools / Security**: 3 (P3, P4, P9) — strong AI engineer signal
- **Healthcare**: 2 (P1, P7) — high consumer-engagement + safety chops
- **Education (India)**: 2 (P6, P8) — Boss's home turf
- **Finance (India)**: 1 (P2) — Indian fintech recruiters
- **Creative / Media**: 1 (P5) — EU AI Act compliance timing
- **Agentic / VC**: 1 (P10) — capstone

---

## Estimated Costs

| Cost head | Per project | All 10 |
|-----------|-------------|--------|
| Active build time | 7-11 hrs | ~79 hrs |
| LLM spend | $5-$8 | $60-80 |
| Vercel | Free tier | Free tier |
| Vector DB | Free tier (Qdrant/Upstash/Chroma) | Free tier |
| Domain (optional) | $0 (use `.vercel.app`) | $0 |

---

## Conflict Watch

- **Tata Steel sacred build window starts May 22** — decathlon WILL pause if collision
- **McpIndex DevNetwork submission May 28** — P0 wins over decathlon if budget conflict

## Next Step (Boss returns)

Please review the 10 picks. Either:

```
✅ approve roadmap          → kick off P1 build
🔄 swap P_n → <alt slug>     → e.g. "swap P3 → upsc-rag-grader" (then I re-curve)
⏭️ reorder                   → tell me the desired sequence
✂️ drop to N                 → ship fewer than 10
```

Phase 3 (per-project SDLC with critic loops + 10-user-sim testing + Vercel deploy) begins on your nod.

---

**Files of interest**:
- `data/projects/rag-decathlon/PLAN.md` — master 5-phase plan
- `data/projects/rag-decathlon/research/candidates-*.yaml` — full 40-candidate research bank (8 files)
- `data/projects/rag-decathlon/roadmap/ROADMAP.md` — this document
