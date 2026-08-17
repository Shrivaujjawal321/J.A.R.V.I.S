# Component 04: RAG Architecture for Industrial Manuals/SOPs
**Tata Steel AI Hackathon 2026 — Round 2 Research Brief**
*Research date: 2026-06-06 | Constraint: CPU-only, solo build, ~9 days, pip-install-first*

---

## 1. Recommended Approach — The Single Winner

**Hierarchical-Chunked Contextual Hybrid RAG with Two-Stage CPU Reranking**

The winning architecture is a four-layer stack:

1. **Ingestion layer:** `pymupdf4llm` converts PDFs/docs to structure-preserving Markdown → `LangChain MarkdownHeaderTextSplitter` cuts along `##`/`###` headers → `RecursiveCharacterTextSplitter` applies a 512-token / 64-token-overlap secondary split within each section. Contextual prefix injection (Anthropic Contextual Retrieval pattern) prepends a one-sentence chunk-context using `claude-haiku-3-5` before embedding.

2. **Index layer:** `FAISS` (flat inner-product) for dense search on `BAAI/bge-base-en-v1.5` embeddings (768-dim, ONNX export) + `rank_bm25` (`BM25Okapi`) in-memory index for exact-term sparse search. Both run fully CPU, zero server.

3. **Retrieval layer:** Parallel BM25 (top-20) + FAISS ANN (top-20) → **Reciprocal Rank Fusion** (k=60, pure Python, 10 lines) → merged top-30 candidate set.

4. **Reranking layer:** `FlashRank` with `ms-marco-MiniLM-L-12-v2` model (cross-encoder, ONNX, ~4MB) → top-5 chunks pass to generation. Adds ~30–80 ms on CPU for 30 candidates, which is within a ≤2 s total budget.

Query side: every incoming engineer query is first rewritten via **HyDE** (one haiku call generates a hypothetical answer paragraph, that paragraph is embedded for retrieval) when the query is short/ambiguous (<15 words). Plain queries use direct embedding. A LangGraph `ToolNode` wraps the retriever so the agentic orchestrator can call it as a tool.

Output side: every answer is grounded — chunks are cited with doc name + section header + page number in a `sources` list. A lightweight NLI faithfulness check (using `cross-encoder/nli-deberta-v3-small`, ~80 ms CPU) flags any claim not supported by a cited chunk, triggering a one-shot re-retrieval.

---

## 2. Why This Wins — Evidence Chain

### 2a. Chunking: Structure-aware beats fixed-size for SOPs

A Nov 2025 clinical benchmark (MDPI Bioengineering) showed adaptive/boundary-aligned chunking hit **87% accuracy vs. 13% for fixed-size** on the same corpus. For steel-plant SOPs and maintenance manuals, the natural boundaries are `##` section headings and numbered procedure steps — exactly what `MarkdownHeaderTextSplitter` exploits after `pymupdf4llm` renders the PDF to Markdown.

The secondary 512-token recursive split is necessary because some SOP sections run 2000+ tokens. 512 tokens is the sweet spot: the 2026 firecrawl chunking playbook shows 400–512 tokens beats both smaller (too fragmented for multi-step procedures) and larger (pushes past useful context density). Overlap at 64 tokens (≈12.5%) preserves cross-sentence continuity at step boundaries.

### 2b. Contextual prefix injection: 49–67% retrieval failure reduction

Anthropic's published Contextual Retrieval results (September 2024, confirmed by 2025 production implementations):
- Baseline top-20 failure rate: **5.7%**
- Contextual Embeddings alone: **3.7%** (35% reduction)
- Contextual Embeddings + Contextual BM25: **2.9%** (49% reduction)
- Adding reranking: **1.9%** (67% reduction)

For industrial maintenance, chunks often lose their context ("The valve must be replaced..." — which valve, which equipment?) when isolated. The Haiku-generated prefix ("This chunk describes the replacement procedure for the hot strip mill descaler valve, from Section 4.2 of the Rolling Mill Maintenance SOP, revision 2024.") restores that context before embedding. Haiku-3-5 costs ~$0.0003/chunk and can be batched with prompt caching; for ~500 synthetic chunks this is <$0.15 total at ingestion time only.

### 2c. Hybrid BM25 + Dense + RRF: proven production gains

The TowardsDataScience production benchmark (150 labeled query-document pairs):
- Dense only: context precision 0.61, recall 0.74
- Hybrid (α=0.5): precision 0.71, recall 0.83
- Hybrid + reranking: **precision 0.79**, recall 0.84

RRF at k=60 is the Elasticsearch production default and is scale-invariant across BM25's unbounded integers and cosine similarity's [−1, 1] range. Digital Applied's 2026 WANDS benchmark: basic RRF NDCG **0.7068** vs BM25-alone 0.6983 vs vector-alone 0.6953.

For maintenance queries, BM25 is essential: engineers write queries like "P80 bearing fault 4-high mill" — exact equipment codes and part numbers are 0-similarity in dense space but BM25 hits them precisely. Dense retrieval handles semantic variants: "descaler nozzle blockage" ≠ "plugged spray head" in BM25, but ~0.87 cosine with a good embedding model.

### 2d. FAISS + bge-base-en-v1.5: the right CPU-first vector backend

`FAISS` (CPU flat index) achieves ~2 ms search latency for collections under 100K vectors (well within the ~500-chunk corpus this build will have). Zero server, `pip install faiss-cpu`. The `BAAI/bge-base-en-v1.5` model (768-dim, 110M params, MTEB retrieval score 53.25) is the right balance: it outperforms `all-MiniLM-L6-v2` significantly on retrieval tasks (MiniLM achieved only ~56% Top-5 accuracy in 2025 benchmarks) while remaining CPU-fast (<30 ms per batch embed with ONNX export). Alternatives like `bge-m3` (multi-lingual, 568M params) are overkill for this English-only corpus and add 10× memory.

### 2e. FlashRank + MiniLM-L-12-v2: the right reranker for CPU-only

CPU latency comparison:
- `BGE-reranker-v2-m3`: **350 ms for 3 docs** → ~5 s for 30 candidates (unacceptable)
- `ms-marco-MiniLM-L-6-v2` (sentence-transformers): **45 ms** for typical candidate set
- `FlashRank` with `ms-marco-MiniLM-L-12-v2`: **15–30 ms for 30 candidates** (ONNX-optimized, no PyTorch dependency)

FlashRank wins on the CPU-only constraint. It requires no torch install (uses ONNX Runtime directly), has a ~4MB model footprint, and integrates via `pip install flashrank`. The L-12 variant (vs L-6) gets better precision on technical queries with marginal latency cost. For demo purposes on a judge's laptop, this is the safe choice.

### 2f. HyDE query rewriting: 20–40% improvement on knowledge-dense corpora

The 2026 production RAG playbook (roborhythms.com) cites HyDE delivering "20–40% improvement on knowledge-dense corpora." For industrial queries that are terse ("motor bearing vibration alarm"), generating a hypothetical answer ("If the motor bearing vibration exceeds 7 mm/s, the likely causes are misalignment, unbalance, or early spalling. The recommended diagnostic steps are...") and embedding *that* produces a retrieval vector aligned to the semantic space of manual text, not the sparse query. This is particularly impactful for maintenance manuals where the query vocabulary rarely matches the document vocabulary exactly.

---

## 3. Exact Stack

| Library | Version | Role |
|---|---|---|
| `pymupdf4llm` | 0.0.19+ (PyPI Apr 2026) | PDF/DOCX → Markdown with layout, tables, headers preserved |
| `langchain-text-splitters` | 0.3.x | `MarkdownHeaderTextSplitter` + `RecursiveCharacterTextSplitter` |
| `rank_bm25` | 0.2.2 | Pure-Python BM25Okapi sparse index; zero server |
| `faiss-cpu` | 1.8.x | FAISS flat L2 index; CPU-only ANN search |
| `sentence-transformers` | 3.x | Load + encode with `BAAI/bge-base-en-v1.5`; ONNX export |
| `optimum[onnxruntime]` | 1.21+ | Export bge-base to ONNX for 2–3× CPU speedup |
| `flashrank` | 0.2.x | CPU cross-encoder reranker (MiniLM-L-12-v2 ONNX, no torch) |
| `anthropic` SDK | 0.28+ | Haiku-3-5 for chunk context injection + HyDE generation |
| `langchain-core` | 0.3.x | `ToolNode` wrapper so orchestrator agent can call retriever as a tool |
| `ragas` | 0.2.x | Eval: faithfulness, context precision, answer relevance |
| `cross-encoder/nli-deberta-v3-small` (via sentence-transformers) | — | Faithfulness NLI check post-generation (~80 ms CPU) |

**No Docker required.** Full install: `pip install pymupdf4llm langchain-text-splitters rank_bm25 faiss-cpu sentence-transformers optimum[onnxruntime] flashrank anthropic langchain-core ragas`.

---

## 4. Alternatives Considered — Why Each Lost

### Alt A: Qdrant local embedded mode
**What it is:** `qdrant-client` with `QdrantClient(path="./db")` — pure Python embedded, no server.
**Why it loses:** Qdrant's embedded mode uses Rust binaries under the hood, adding ~200MB to the install. FAISS flat index is 10× simpler, zero binary dependency, and at <100K vectors the performance difference is nil. Qdrant's rich filtering is valuable at scale but irrelevant for a 500-chunk demo corpus. Adds complexity without benefit at this scale.

### Alt B: Chroma as vector DB
**What it is:** ChromaDB in embedded mode — popular RAG tutorial choice.
**Why it loses:** Chroma's primary use case is prototyping. On the same hardware, FAISS achieves ~2 ms search vs Chroma's ~20 ms due to different index implementations. More critically, Chroma has had stability issues under concurrent access and its HNSW index requires more memory per vector. For a demo that must not crash, FAISS flat index is more reliable.

### Alt C: BGE-reranker-v2-m3 (full cross-encoder)
**What it is:** BAAI's multilingual reranker, 568M params, state-of-the-art quality.
**Why it loses:** CPU latency is ~350 ms for 3 documents, scaling to ~5 seconds for a 30-candidate shortlist. This exceeds the demo latency budget and will make the judge experience painful. Quality gain over MiniLM-L-12 does not justify 100× latency increase on CPU. Reserve this for a GPU-accelerated production deployment.

### Alt D: LlamaIndex AutoMergingRetriever / HierarchicalNodeParser
**What it is:** LlamaIndex's native hierarchical chunking with parent-child node trees and auto-merge on retrieval.
**Why it loses:** LlamaIndex adds significant abstraction overhead. For a solo-9-day build, the `HierarchicalNodeParser` + `AutoMergingRetriever` combo requires understanding LlamaIndex's internal docstore, index store, and service context — three interconnected components that break in non-obvious ways on version mismatches. The LangChain `MarkdownHeaderTextSplitter` + `RecursiveCharacterTextSplitter` combo achieves the same hierarchical intent with 40 lines of explicit code vs. 200 lines of opaque LlamaIndex boilerplate. Explicit beats magic for demo reliability.

---

## 5. Anti-Patterns — What Screams "2022-Tier Amateur"

1. **Fixed-size character splitting (`CharacterTextSplitter(chunk_size=1000)`) on PDFs.** This is the Langchain tutorial default from 2022. It splits mid-sentence, mid-procedure-step, and mid-table. For industrial SOPs it will return garbage chunks that destroy retrieval quality.

2. **Dense-only retrieval without BM25.** Equipment codes like "P-80 bearing NU-330EM" and fault codes like "E-7724" have zero meaningful cosine similarity vector. Pure semantic search will miss these entirely. Hybrid is non-negotiable for industrial text.

3. **No reranker — "top-k=5 from the vector DB is what we use."** The bi-encoder (embedding model) optimizes for approximate similarity at scale, not precision. Without a cross-encoder reranker, the top-5 will contain 1–2 irrelevant chunks that derail the LLM answer. The 2025 TowardsDataScience benchmark shows a 0.71→0.79 context precision jump from reranking alone.

4. **Pinecone / Weaviate cloud dependency.** Any RAG that requires an external vector DB API call on a judge's machine with unknown internet connectivity is a demo liability. Full local stack only.

5. **Parsing with `PyPDF2` or `pdfminer` and dumping raw text.** These libraries destroy table structure, merge multi-column text incorrectly, and strip all headers. `pymupdf4llm` renders to clean Markdown with structure intact — use it.

6. **Embedding with `all-MiniLM-L6-v2` for domain-specific retrieval.** 2025 benchmarks showed MiniLM-L6 achieving only 56% Top-5 accuracy on domain-specific retrieval. `bge-base-en-v1.5` significantly outperforms it on the MTEB retrieval sub-benchmark while remaining CPU-friendly.

7. **No source citation in the output.** Judges score on explainability. Every generated answer must include `sources: [{doc, section, page}]`. Anything less is a black box.

8. **Reranking the full corpus.** Cross-encoders are O(n) over the candidate set. Running the reranker on all 500 chunks = ~8 seconds on CPU. Always retrieve top-30 via hybrid, rerank only those 30.

---

## 6. Integration Notes — How This Plugs Into the Maintenance Wizard

### Inputs Consumed
- **Synthetic manuals corpus** (PDF/DOCX files): equipment manuals, SOPs, maintenance procedures, spare-parts catalogs — generated by the data-generation component.
- **Engineer natural-language queries** from the multi-turn conversation interface (passed as strings from the orchestrator's `ToolNode` call).
- **Query context**: conversation history from the memory component (passed as preamble to HyDE generation for better query rewriting).

### Outputs Produced
- **`retrieved_chunks`**: list of top-5 objects, each containing `{text, doc_name, section_header, page_number, rerank_score}`.
- **`sources`**: structured citation list embedded in every LLM-generated answer.
- **`faithfulness_flag`**: boolean + explanation if the NLI check detects an unsupported claim (triggers re-retrieval).
- **`retrieval_metadata`**: token count, latency breakdown (BM25 / FAISS / RRF / rerank ms), for the observability dashboard.

### Component Interactions
- **Receives from: Orchestrator (Component 01)** — the orchestrator calls the RAG retriever as a LangGraph `ToolNode`. The tool signature is `retrieve(query: str, filters: dict | None) -> RetrievedContext`.
- **Receives from: Memory / Conversation Manager** — conversation history is injected into the HyDE prompt to make the hypothetical answer contextually grounded (e.g., if prior turn established "we're discussing the #4 blast furnace cooling system", HyDE generates a contextual hypothetical).
- **Feeds: LLM Generation step (Component 02/03)** — the `retrieved_chunks` are formatted as `<context>` blocks in the generation prompt; sources are appended to the final structured output.
- **Feeds: Feedback Loop (Component 07)** — `retrieval_metadata` + `faithfulness_flag` + engineer thumbs-up/down are logged to `data/feedback/retrieval_feedback.jsonl`. Weekly RAGAS evaluation reruns against this logged data to measure drift.
- **Feeds: Alerting Component** — when `faithfulness_flag=True` triggers re-retrieval 3× in one session, an alert fires ("knowledge base gap detected for query class X") to the alerting bus.

### Feedback-Driven Improvement Loop (FR-6 compliance)
The feedback loop is lightweight but genuine:
1. Engineer rates each answer (thumbs up/down via the UI).
2. Rating + retrieved chunks + query → appended to `retrieval_feedback.jsonl`.
3. Weekly RAGAS run (`ragas evaluate`) re-scores faithfulness + context precision on the accumulated feedback set.
4. If context precision drops >5pp from baseline, a re-indexing is triggered with tighter chunk overlap or a revised contextual prefix prompt.
5. This is presentable as a real continuous-improvement loop to judges — not a stub.

---

## 7. Open Risks and Unknowns

### Confirmed/Low Risk
- FAISS CPU flat index: stable, well-tested, zero dependency footprint. Low risk.
- `rank_bm25`: pure Python, 2k stars, actively maintained. Low risk.
- `FlashRank` + MiniLM ONNX: used in multiple 2025-2026 production RAG write-ups. Low risk for demo scale.
- `pymupdf4llm`: PyPI updates confirmed to April 2026. Low risk.

### Medium Risk
- **Synthetic corpus quality**: The retrieval quality is only as good as the synthetic manual text. If the generator produces repetitive or low-diversity text, BM25 will have poor IDF discrimination. Mitigation: generate at least 15–20 distinct "manuals" with varied terminology.
- **HyDE latency on slow Haiku calls**: HyDE adds one Haiku API call per query. If the judge's machine has slow internet, this adds 500–1500 ms. Mitigation: make HyDE optional (disable for short queries; use direct embedding path as fallback with a config flag).
- **Contextual prefix injection cost at ingestion**: Haiku calls at indexing time. For 500 chunks at $0.0003/call = $0.15 — acceptable, but must be done once and cached. Mitigation: save prefixed chunks to disk; skip re-generation on re-run.

### [unverified] — Tag
- **FlashRank ms-marco-MiniLM-L-12-v2 vs L-6-v2 delta on industrial text**: The bswen.com benchmark compared these on general web queries. Whether the L-12 variant provides meaningful gains on domain-specific maintenance text vs L-6 is not confirmed by a specific industrial benchmark. [unverified]
- **`bge-base-en-v1.5` ONNX export CPU speedup factor**: The 2–3× speedup claim for ONNX-exported sentence-transformers models is from Sentence Transformers documentation (general) and may vary on specific hardware. [unverified]
- **RAGAS faithfulness threshold ≥0.85 achievability on synthetic corpus**: RAGAS benchmarks exist for general QA datasets; performance on synthetic steel-plant text is uncharted. [unverified] — run the eval baseline on first 50 queries and set the threshold from that run, not from literature.

---

## Implementation Skeleton (key scaffolding, not boilerplate)

```python
# ingestion.py — run once at setup
import pymupdf4llm
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from rank_bm25 import BM25Okapi
import faiss, numpy as np, pickle

# Step 1: PDF → Markdown
md_text = pymupdf4llm.to_markdown("manuals/rolling_mill_sop.pdf")

# Step 2: Header-aware split
header_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[("##", "section"), ("###", "subsection")]
)
header_chunks = header_splitter.split_text(md_text)

# Step 3: Token-bounded secondary split
char_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
chunks = char_splitter.split_documents(header_chunks)

# Step 4: Contextual prefix injection (Anthropic Haiku)
# [batch call: generate 1-sentence context per chunk, prepend to chunk.page_content]

# Step 5: BM25 index
tokenized = [c.page_content.lower().split() for c in chunks]
bm25 = BM25Okapi(tokenized)
pickle.dump(bm25, open("bm25.pkl", "wb"))

# Step 6: Dense FAISS index
from sentence_transformers import SentenceTransformer
encoder = SentenceTransformer("BAAI/bge-base-en-v1.5")  # or ONNX-exported variant
embeddings = encoder.encode([c.page_content for c in chunks], normalize_embeddings=True)
index = faiss.IndexFlatIP(768)
index.add(embeddings.astype(np.float32))
faiss.write_index(index, "dense.index")

# retrieval.py — called at query time
from flashrank import Ranker, RerankRequest

def retrieve(query: str, top_k: int = 5) -> list[dict]:
    # HyDE for short queries
    if len(query.split()) < 15:
        hyp = haiku_generate_hypothesis(query)  # 1 Haiku call
        q_embed = encoder.encode(hyp, normalize_embeddings=True)
    else:
        q_embed = encoder.encode(query, normalize_embeddings=True)
    
    # BM25 top-20
    bm25_scores = bm25.get_scores(query.lower().split())
    bm25_top20 = np.argsort(bm25_scores)[::-1][:20].tolist()
    
    # FAISS top-20
    _, faiss_top20_idx = index.search(q_embed.reshape(1, -1).astype(np.float32), 20)
    faiss_top20 = faiss_top20_idx[0].tolist()
    
    # RRF fusion (k=60)
    rrf_scores = {}
    for rank, idx in enumerate(bm25_top20):
        rrf_scores[idx] = rrf_scores.get(idx, 0) + 1 / (60 + rank + 1)
    for rank, idx in enumerate(faiss_top20):
        rrf_scores[idx] = rrf_scores.get(idx, 0) + 1 / (60 + rank + 1)
    top30 = sorted(rrf_scores, key=rrf_scores.get, reverse=True)[:30]
    
    # FlashRank rerank
    ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2")
    passages = [{"id": i, "text": chunks[i].page_content} for i in top30]
    reranked = ranker.rerank(RerankRequest(query=query, passages=passages))
    
    return [{"text": r.text, "score": r.score, **chunks[r.id].metadata}
            for r in reranked[:top_k]]
```

---

*Sources consulted: [Building Production RAG 2026 — Premai](https://blog.premai.io/building-production-rag-architecture-chunking-evaluation-monitoring-2026-guide/) · [Chunking Strategies 2026 — Digital Applied](https://www.digitalapplied.com/blog/rag-chunking-strategies-2026-retrieval-quality-playbook) · [Hybrid Search BM25+Vector 2026 — Digital Applied](https://www.digitalapplied.com/blog/hybrid-search-bm25-vector-reranking-reference-2026) · [Production RAG Pipeline 2026 — RoboRhythms](https://www.roborhythms.com/how-to-build-production-rag-pipeline-2026/) · [Hybrid Search + Reranking — TowardsDataScience](https://towardsdatascience.com/hybrid-search-and-re-ranking-in-production-rag/) · [Agentic RAG Developer Guide 2026 — FutureAGI](https://futureagi.com/blog/agentic-rag-systems-2025/) · [Reranker Leaderboard — Agentset](https://agentset.ai/rerankers) · [Best Reranker Models 2026 — BSWEN](https://docs.bswen.com/blog/2026-02-25-best-reranker-models/) · [Contextual Retrieval — Anthropic](https://www.anthropic.com/news/contextual-retrieval) · [FlashRank GitHub](https://github.com/PrithivirajDamodaran/FlashRank) · [pymupdf4llm PyPI](https://pypi.org/project/pymupdf4llm/) · [Qdrant Client PyPI](https://pypi.org/project/qdrant-client/) · [Best Chunking Strategies 2026 — Firecrawl](https://www.firecrawl.dev/blog/best-chunking-strategies-rag) · [BAAI bge-reranker-v2-m3 HuggingFace](https://huggingface.co/BAAI/bge-reranker-v2-m3) · [MarkdownHeaderTextSplitter — LangChain](https://docs.langchain.com/oss/python/integrations/splitters/markdown_header_metadata_splitter)*
