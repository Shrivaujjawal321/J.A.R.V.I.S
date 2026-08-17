# Component 07: Embedding Model & Vector Store
**Tata Steel AI Hackathon 2026 — Round 2 Research Brief**
*Research date: 2026-06-06 | Constraint: CPU-only, solo build, ~9 days, pip-install-first, must not break on judge's machine*

---

## 1. Recommended Approach — The Single Winner

**`BAAI/bge-small-en-v1.5` via `sentence-transformers` (ONNX backend) + `LanceDB` (embedded, disk-backed) with SQL metadata filtering.**

The winning stack for this build:

| Layer | Choice | Version |
|---|---|---|
| Embedding model | `BAAI/bge-small-en-v1.5` | HF hub, sentence-transformers 3.x |
| Inference backend | sentence-transformers with ONNX | `pip install sentence-transformers[onnx]` |
| Vector store | LanceDB (embedded, no server) | `lancedb>=0.20` |
| Hybrid search | LanceDB native FTS (Tantivy) + vector | built-in |
| Metadata filtering | LanceDB SQL `where()` clause | built-in |

**Why this pair wins over every other combination:** bge-small-en-v1.5 delivers the best BEIR retrieval quality (NDCG@10 avg 0.517) at its size class — far ahead of MiniLM-L6-v2 (0.419) — while staying at 33.4M params / ~90 MB on disk, making it trivially fast on any judge's CPU. LanceDB runs in-process, `pip install lancedb` zero-dependency, stores data on disk via the Lance columnar format (Apache Arrow), and ships native hybrid search (dense vector + Tantivy BM25 FTS) in a single query — no separate BM25 index, no FAISS install, no secondary data structure to manage. For equipment scoping, its SQL `where()` clause pre-filters by `equipment_id`, `document_type`, `criticality` before scoring — which is how industrial systems actually scope queries.

> **Compatibility note with Component 04:** Component 04 (RAG architecture) uses FAISS + bge-base-en-v1.5 as the retrieval layer for the BM25+dense hybrid. Component 07 is the *persistent vector store* layer sitting underneath it — a proper DB with metadata filtering, versioning, and a queryable API. The two are compatible: you can front LanceDB with the Component 04 RRF+rerank pipeline. Alternatively, simplify by replacing FAISS+BM25 entirely with LanceDB's built-in hybrid search and save 2 dependencies. The latter is recommended for a 9-day solo build.

---

## 2. WHY — Evidence-Based Reasoning

### 2a. Embedding model: bge-small-en-v1.5 beats MiniLM by a wide margin

BEIR benchmark (Part A), NDCG@10 across 7 tasks:

| Model | Avg NDCG@10 | NQ | SciFact | MSMARCO | Params | Disk |
|---|---|---|---|---|---|---|
| all-MiniLM-L6-v2 | 0.419 | 0.439 | 0.645 | 0.365 | 22M | 46 MB |
| **bge-small-en-v1.5** | **0.517** | **0.502** | **0.713** | **0.408** | 33M | ~90 MB |
| bge-base-en-v1.5 | 0.532 | — | — | — | 110M | ~440 MB |
| nomic-embed-text-v1.5 | 0.524 (MTEB) | — | — | — | 137M | 274 MB |

Sources: [supermemory benchmark](https://supermemory.ai/blog/best-open-source-embedding-models-benchmarked-and-ranked/), [BAAI HF card](https://huggingface.co/BAAI/bge-small-en-v1.5), [BEIR comparison via OpenRouter](https://openrouter.ai/compare/baai/bge-large-en-v1.5/sentence-transformers/all-minilm-l6-v2)

Key insight: bge-small-en-v1.5 is **+23% NDCG@10** over MiniLM-L6-v2 at only 1.5× the parameter count. For a domain with precise technical terminology (part codes, fault codes, SOP section references), this retrieval quality gap is the difference between correct chunk retrieval and hallucination.

Speed on CPU: bge-small-en-v1.5 embeds at approximately 14-22 ms/1K tokens range (extrapolated from the base-v1.5 at 22.5 ms with proportional scaling to 33M params). With ONNX backend (`sentence-transformers[onnx]`), the sentence-transformers docs confirm **1.39× speedup for short texts, 3.08× with int8 quantization** — bringing per-query embedding to ~5–10 ms on modern laptop hardware.

### 2b. LanceDB: the only embedded DB that ships hybrid search out of the box

Comparison of embedded/local vector stores:

| DB | In-process | pip only | Native FTS/BM25 | SQL metadata filter | Hybrid query | Disk-backed | Python API simplicity |
|---|---|---|---|---|---|---|---|
| **LanceDB** | Yes | Yes | Yes (Tantivy) | Yes (Lance SQL) | Yes (native) | Yes (Lance/Arrow) | High |
| ChromaDB | Yes | Yes | No | Limited (where dict) | No (need separate BM25) | Yes (SQLite+HNSW) | Very high |
| Qdrant local | Yes (local mode) | Yes | No | Yes (payload filter) | No (need separate BM25) | SQLite (brute-force only) | High |
| FAISS | Yes | Yes | No | No | No | No (RAM only) | Low |

Sources: [4xxi comparison 2026](https://4xxi.com/articles/vector-database-comparison/), [aicoolies LanceDB vs Chroma](https://aicoolies.com/comparisons/lancedb-vs-chromadb), [Qdrant local mode docs](https://deepwiki.com/qdrant/qdrant-client/2.2-local-mode), [LanceDB hybrid search docs](https://docs.lancedb.com/search/hybrid-search)

The decisive factor: **LanceDB is the only pip-installable embedded DB that can do `dense + BM25 + metadata filter` in a single query call**, returning RRF-reranked results natively. For the Maintenance Wizard, a typical query looks like: "find maintenance procedures for equipment_id='P80_BEARING' where document_type='SOP' AND criticality='high'." LanceDB's prefilter mode applies the SQL `where()` before scoring — which is both faster and more accurate than post-hoc metadata filtering.

LanceDB also uses Apache Arrow / Lance columnar format on disk: memory-mapped SIMD-optimized reads, disk footprint scales with data not RAM, and it handles datasets far larger than available memory — irrelevant at demo scale but signals production-readiness to judges.

ChromaDB 1.x (released 2025, Rust rewrite, 3–5× faster) is the simplest API but lacks native BM25 — you'd need a separate `rank_bm25` index in parallel. For a 9-day solo build, that's an extra data structure to sync. LanceDB eliminates that complexity entirely.

### 2c. Equipment-scoped metadata filtering — the critical industrial feature

Industrial RAG must scope retrieval to the right equipment before ranking. Without scoping, a query for "furnace bearing fault" retrieves results from rolling mills, not just furnaces. The LanceDB prefilter pattern handles this:

```python
results = (
    table.search(query_embedding, query_type="hybrid")
    .where(f"equipment_type = '{equipment_type}' AND doc_type IN ('SOP', 'manual')", prefilter=True)
    .limit(10)
    .to_pandas()
)
```

Prefilter runs before scoring — it restricts the candidate set, not the result set. This is the pattern Qdrant uses (and is praised for in the 4xxi benchmark). LanceDB matches it natively.

ChromaDB's `where` dict is equivalent for simple key=value filters but cannot express `IN (...)` conditions or range queries cleanly. LanceDB's SQL `where()` can: `equipment_id IN ('P80', 'P81') AND last_maintenance_date > '2024-01-01'`.

---

## 3. Exact Stack

```
lancedb>=0.20.0             # Embedded vector DB, hybrid search, disk-backed (pip install lancedb)
sentence-transformers>=3.0  # Model loading + inference pipeline
onnxruntime>=1.18           # CPU-optimized ONNX backend for ST
sentence-transformers[onnx] # Pull ONNX extras in one command
pyarrow>=15.0               # Lance columnar format dependency (usually auto-installed)
tantivy>=0.22               # LanceDB's FTS engine (auto-installed via lancedb)
```

Model: `BAAI/bge-small-en-v1.5` — downloaded from HF hub once, cached at `~/.cache/huggingface/hub/`. On a judge's machine: first-run download (~90 MB), then fully offline. Alternatively, ship the model weights inside the ZIP (90 MB is acceptable for a hackathon submission).

**Role of each library:**

- `lancedb`: Persistent vector store, ANN index (IVF-PQ for large, flat for demo scale), native BM25 FTS via Tantivy, SQL filtering, Arrow storage. Zero server, single `import lancedb` line.
- `sentence-transformers`: High-level `SentenceTransformer('BAAI/bge-small-en-v1.5')` API for embedding documents and queries. Handles tokenization, batching, normalization.
- `onnxruntime`: Accelerates inference — enables ONNX-exported model for 1.4–3× CPU speedup vs raw PyTorch. Drop-in via `model = SentenceTransformer('BAAI/bge-small-en-v1.5', backend='onnx')`.
- `pyarrow`: Data interchange between LanceDB and the rest of the pipeline (DataFrames, Arrow tables).
- `tantivy`: BM25 full-text search engine embedded in LanceDB. Auto-installed, no separate config needed.

---

## 4. Alternatives Considered and Why Each Lost

### Alt 1: `all-MiniLM-L6-v2` as embedding model
- **Tradeoff that kills it:** BEIR NDCG@10 avg 0.419 vs bge-small's 0.517 — a **+23% gap**. For technical maintenance docs with exact part codes and error codes, BM25 handles lexical hits but dense embedding must handle semantic synonyms ("worn bearing" / "fatigued journal bearing" / "bearing failure"). MiniLM's lower retrieval quality is a genuine correctness risk. It was SOTA in 2022; in 2026, there is no reason to accept its lower ceiling when bge-small is only 44 MB heavier.
- **Only keep if:** Inference speed on an extremely limited CPU (<1 GHz, <512 MB RAM) is the constraint. For a modern laptop CPU demo machine, the latency difference is imperceptible.

### Alt 2: `nomic-embed-text-v1.5` as embedding model
- **Tradeoff that kills it:** 137M params, 274 MB disk, requires `trust_remote_code=True` flag (a red flag on a judge's fresh machine — may trigger firewall or policy block). Its MTEB average (62.39) is slightly above bge-small (62.17) but this is a composite score; on retrieval-specific BEIR the gap narrows. For 3× the model size and a `trust_remote_code` dependency, the gain is marginal. Also, its 8192-token context window is overkill for 512-token chunks — you pay the overhead without benefit.
- **Keep if:** You need long-document embedding (>1K token chunks). Not the case here.

### Alt 3: ChromaDB as vector store
- **Tradeoff that kills it:** No native BM25/FTS. For an industrial RAG system, hybrid search is mandatory — equipment fault codes ("Fault 0x4A2"), part numbers ("SKF 6208-2Z"), SOP section IDs all require exact keyword matching that dense-only search misses. Adding `rank_bm25` as a parallel index doubles the storage burden and requires manual sync logic. ChromaDB 1.x (Rust rewrite) is excellent for pure dense search, but the missing hybrid search is a hard blocker for this use case.
- **Keep if:** The RAG corpus is purely natural-language (no codes/IDs), or if you are already managing a separate BM25 index for Component 04.

### Alt 4: Qdrant local mode as vector store
- **Tradeoff that kills it:** Local mode uses **brute-force search** (no HNSW indexing) and is officially capped at ~20,000 vectors for performance. Runs on SQLite under the hood in local mode, not a proper ANN index. Also no native BM25 — same problem as ChromaDB. For a production-quality demo claiming scalability, using Qdrant local mode (dev/test only per their own docs) would look amateurish to a judge who reads the code. Qdrant proper (Docker/server) is excellent but violates the pip-install-first constraint.
- **Keep if:** You want Qdrant in production later — the API is identical between local and remote mode, so migration is trivial.

---

## 5. Anti-Patterns — What Screams "Amateur / 2022-Tier"

1. **Using `all-MiniLM-L6-v2` by default with no justification.** It is ChromaDB's default model, which means most tutorial-copy-paste code uses it. Judges at Tata Steel who read the code will recognize it as the "first thing I googled" model. Switching to bge-small-en-v1.5 with a 2-line justification in comments signals deliberate choice.

2. **Pure dense-only retrieval with no BM25 component.** Industrial vocabulary is full of exact codes. Missing them means your system won't find the SOP for "Fault E-0042" when an engineer asks about it. Hybrid search is the 2025+ standard; pure dense is 2021.

3. **Storing embeddings in a flat JSON file or pickle.** Kills demo restarts (re-embed every time) and has no metadata filtering. Any self-respecting RAG uses a vector store.

4. **Using Qdrant local mode and calling it "production Qdrant."** The brute-force, no-HNSW, SQLite-backed local mode is for unit tests only. A judge who checks the Qdrant docs will notice.

5. **Not normalizing embeddings.** bge-small-en-v1.5 (like all BGE models) requires L2-normalized embeddings for cosine similarity. Forgetting `normalize_embeddings=True` in `model.encode()` — or skipping it because ChromaDB normalizes by default — causes subtly wrong similarity scores. Always pass `normalize_embeddings=True` explicitly.

6. **One monolithic collection / no metadata schema.** Dumping all documents (manuals, SOPs, incident logs, sensor summaries) into a single flat table with no `document_type`, `equipment_id`, `criticality` fields. Without metadata, you cannot scope queries to relevant equipment — every query searches everything.

7. **Embedding at query time with PyTorch on a cold CPU without batching.** First-load latency of a PyTorch model on CPU is 2–4 seconds. Cache the model at startup; pre-warm with a dummy embed. Use ONNX backend to cut steady-state latency.

---

## 6. Integration Notes — How This Plugs Into the Maintenance Wizard

### Inputs consumed
- **Document ingestion pipeline (Component 04):** Receives chunked text dicts with fields: `{text, document_id, document_type, equipment_id, equipment_type, criticality, source_page, section_header}`. Embeds `text` via bge-small-en-v1.5, stores all fields as LanceDB metadata columns.
- **Engineer NL query (via multi-turn conversation, Component 03):** Receives the resolved query string (after context resolution from conversation history). Optionally receives `equipment_id` and `document_type` filters extracted by the agentic router.
- **Sensor/anomaly alert (Component 05, for alert-driven retrieval):** Receives structured alert dict: `{equipment_id, alert_type, severity, timestamp}`. Constructs query string and filter automatically.

### Outputs produced
- **Retrieved chunks list** (top-k, default k=10 before reranking): list of dicts with `{text, document_id, document_type, equipment_id, section_header, source_page, score}`.
- **Grounding sources** for citation layer (Component 06): the `document_id + section_header + source_page` fields flow directly into the explainability layer.

### Components it talks to
- **Component 04 (RAG architecture):** Sits as the persistent store layer underneath Component 04's BM25+dense pipeline. LanceDB replaces the need for a separate FAISS index + BM25 index — it is both.
- **Component 06 (Explainability):** Provides `source` metadata on every retrieved chunk so the explanation layer can cite "SOP-RM-042, Section 3.4, Page 12."
- **Component 03 (Conversation memory):** The agentic router in Component 03 calls the retriever as a LangGraph `ToolNode`; the LanceDB retriever wraps as a simple Python function — no special integration needed.
- **Component 05 (Anomaly detection / alerting):** Triggered by alert events to retrieve relevant equipment history and repair procedures automatically.
- **Feedback loop (FR-6):** When an engineer marks a retrieved result as "not relevant," the feedback is logged. Weekly, this can be used to fine-tune embeddings (via sentence-transformers `FitMixin` or synthetic hard-negative mining) — satisfying the feedback-driven improvement loop requirement.

### Schema design (LanceDB table)

```python
import lancedb, pyarrow as pa

schema = pa.schema([
    pa.field("id", pa.string()),                     # chunk UUID
    pa.field("text", pa.string()),                   # chunk text (embedded)
    pa.field("vector", pa.list_(pa.float32(), 384)), # bge-small-en-v1.5 dims
    pa.field("document_id", pa.string()),            # source document
    pa.field("document_type", pa.string()),          # "SOP" | "manual" | "incident_log" | "history"
    pa.field("equipment_id", pa.string()),           # "P80_BEARING" | "HSM_FURNACE_1"
    pa.field("equipment_type", pa.string()),         # "bearing" | "furnace" | "roller"
    pa.field("criticality", pa.string()),            # "critical" | "high" | "medium" | "low"
    pa.field("section_header", pa.string()),         # "Section 4.2 — Descaler Valve"
    pa.field("source_page", pa.int32()),             # page number in source doc
    pa.field("ingested_at", pa.timestamp("us")),     # for freshness filtering
])
```

### Retrieval call pattern

```python
def retrieve(query: str, equipment_id: str = None, doc_types: list = None, top_k: int = 10):
    embedding = model.encode(query, normalize_embeddings=True).tolist()
    
    search = table.search(embedding, query_type="hybrid")
    
    # Equipment scoping (pre-filter)
    filters = []
    if equipment_id:
        filters.append(f"equipment_id = '{equipment_id}'")
    if doc_types:
        types_str = ", ".join(f"'{t}'" for t in doc_types)
        filters.append(f"document_type IN ({types_str})")
    if filters:
        search = search.where(" AND ".join(filters), prefilter=True)
    
    return search.limit(top_k).to_pandas().to_dict("records")
```

---

## 7. Open Risks / Unknowns

1. **LanceDB FTS index build time on first run [LOW RISK]:** LanceDB requires `table.create_fts_index("text")` to be called explicitly after data load. If the judge runs the ingestion script and it silently skips FTS creation, hybrid search falls back to dense-only without error. Fix: make FTS index creation idempotent and check for it in the health-check startup.

2. **bge-small-en-v1.5 first-download on judge machine [MEDIUM RISK]:** If the judge has no internet access, the HuggingFace hub download fails. Mitigation: bundle the model weights in the ZIP (90 MB), load with `SentenceTransformer('/path/to/local/model')`. This is standard practice for offline demos.

3. **ONNX export compatibility [LOW RISK]:** `sentence-transformers[onnx]` requires `optimum` and `onnxruntime`. On some machines, `onnxruntime` has platform-specific wheels. Fallback: `backend='torch'` — slightly slower but zero additional deps. Implement with a try/except at startup.

4. **LanceDB version compatibility [LOW RISK]:** LanceDB's Python API has changed significantly across 0.x → 0.20 → 0.21. Pin `lancedb==0.20.x` in `requirements.txt`. The hybrid search API (`query_type="hybrid"`) and FTS index API are stable as of 0.20 per their docs. [Note: verify latest stable version at submission time — as of 2026-06 this is in the 0.20+ range; check `pip index versions lancedb`.]

5. **Domain-specific vocabulary gap [MEDIUM RISK — manageable]:** bge-small-en-v1.5 is trained on general English corpora (no steel-plant data). For exact technical codes (e.g., "Fault E-0042"), the BM25 FTS component handles keyword hits; the dense component handles semantic variants. The hybrid architecture explicitly covers this gap. If retrieval quality is still poor after hybrid, the mitigation is to add domain-specific fine-tuning via sentence-transformers `FitMixin` on a synthetic QA dataset (20–50 query-document pairs, ~2 hours to generate with Claude, ~30 min to fine-tune on CPU for a small model). This can be framed as "the feedback-driven improvement loop" (FR-6) — satisfying a judging criterion while solving a real problem. [unverified: exact fine-tune time on CPU for 33M param model at 50 pairs]

6. **ChromaDB default in LangChain integrations [AWARENESS RISK]:** Many LangChain tutorials default to ChromaDB + MiniLM. If the agentic framework (LangGraph, Component 01) uses LangChain's `VectorstoreRetriever`, swapping in LanceDB requires a `lancedb` LangChain integration (`langchain-community` has one). Verify integration compatibility before committing to LanceDB. Fallback: use a thin wrapper function that exposes LanceDB's `retrieve()` as a standard `BaseTool` — avoids the LangChain VectorStore interface entirely.

---

## Sources

- [BAAI/bge-small-en-v1.5 HuggingFace Model Card](https://huggingface.co/BAAI/bge-small-en-v1.5)
- [Best Open-Source Embedding Models Benchmarked — supermemory.ai](https://supermemory.ai/blog/best-open-source-embedding-models-benchmarked-and-ranked/)
- [Vector Database Comparison 2026: ChromaDB vs Qdrant vs LanceDB — 4xxi](https://4xxi.com/articles/vector-database-comparison/)
- [LanceDB vs ChromaDB comparison — aicoolies](https://aicoolies.com/comparisons/lancedb-vs-chromadb)
- [LanceDB Hybrid Search docs](https://docs.lancedb.com/search/hybrid-search)
- [LanceDB Metadata Filtering docs](https://lancedb.com/docs/search/filtering/)
- [Qdrant Local Mode — DeepWiki](https://deepwiki.com/qdrant/qdrant-client/2.2-local-mode)
- [Chroma 1.0 release — 4x faster Rust rewrite](https://www.trychroma.com/project/1.0.0)
- [Sentence Transformers ONNX efficiency docs](https://sbert.net/docs/sentence_transformer/usage/efficiency.html)
- [Chroma Embedding Functions docs](https://docs.trychroma.com/docs/embeddings/embedding-functions)
- [LanceDB Full-Text Search docs](https://docs.lancedb.com/search/full-text-search)
- [Towards Building General Purpose Embedding Models for Industry 4.0](https://arxiv.org/html/2506.12607v1)
- [Don't use all-MiniLM-L6-v2 for new datasets — HN discussion](https://news.ycombinator.com/item?id=46081800)
