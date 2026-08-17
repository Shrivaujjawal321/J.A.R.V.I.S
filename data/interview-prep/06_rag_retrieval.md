# Interview Prep — Cluster 06: GenAI Retrieval Stack (RAG)

> **For:** Ujjawal Shrivastav — AI/ML Engineer (GenAI / LLM roles, 2026)
> **This is THE core cluster.** For a GenAI fresher role, retrieval is the single most-asked topic. Go deepest here.
>
> **Grounded in your real code:**
> - **Jarvis episodic memory** — `scripts/episodic_memory.py` + `jarvis_core/recall.py` (ChromaDB + all-MiniLM-L6-v2, ~500-token chunking, cosine, 0.55 threshold, token-budget trim).
> - **Tata R2 Maintenance Wizard RAG** — `data/hackathons/tata-steel-2026/round_2/maintenance-wizard/wizard/rag/` (LanceDB hybrid BM25+dense, bge-small-en-v1.5 384-dim ONNX, HyDE, FlashRank rerank, DeBERTa NLI faithfulness gate, contextual prefix injection). **This is your flagship — it has every advanced piece.**
> - **EDITH DataForge** — `dataforge/api/scorer/relevance/` (bge-small embed-sim + KB hybrid scoring, anti-gaming gate).
> - **McpIndex** — `mcpindex-nu.vercel.app` (pgvector + BM25 hybrid search, 1,532 servers).
> - **EngiNerd** — `enginerd.vercel.app` (5-stage Claude pipeline, structured tool-use, SSE streaming).
>
> **How to use this:** Hinglish samjhao for the WHY, then deliver the English model answer out loud. The "🔑" line is your one-breath summary if you blank.

---

## 1. RAG — What / Why / When (naive vs advanced vs agentic)

**Kya hai (Hinglish):** RAG matlab Retrieval-Augmented Generation. LLM ka apna knowledge frozen hai (training cutoff tak) aur woh hallucinate karta hai. RAG mein hum question aaने par pehle apne documents se relevant tukde *retrieve* karte hain, fir woh tukde LLM ko context ki tarah dete hain — taaki woh apne sar se na bole, balki diye gaye source se answer banaye (*grounded*). Soch lijiye open-book exam: LLM woh student hai, retrieval woh "sahi page khol ke saamne rakh dena" hai.

**Aapke project se connection:** Jarvis mein har `/chat` se pehle `recall.py` ChromaDB se top-5 memory chunks nikaal ke `<jarvis_memory_context>` block prompt mein chipka deta hai — yeh classic naive→advanced RAG hai. Tata Wizard mein engineer poochhta hai "BF-2 ka cooling valve kab inspect karna hai" → hybrid retrieval steel-plant SOPs se chunks laata hai → LLM `[1]`-cited grounded answer deta hai → NLI gate verify karta hai. Yeh **agentic RAG** hai kyunki LangGraph agent decide karta hai kab retrieve karna hai aur faithfulness fail hone par retry karta hai.

**Interview Q&A:**

**Q1 (basic): What is RAG and what problem does it solve?**
> RAG augments an LLM's generation with documents retrieved at query time. It solves three problems: (1) **stale knowledge** — the model can answer about data created after its training cutoff; (2) **hallucination** — answers are grounded in retrieved sources you can cite and verify; (3) **private/proprietary data** — you don't need to fine-tune the model on confidential docs, you just retrieve them. In my Tata Maintenance Wizard, the LLM has never seen our steel-plant SOPs, but RAG lets it answer maintenance questions with `[N]` citations pointing back to the exact manual section.
> 🔑 *RAG = LLM ko open-book exam dena — apne docs se answer, hallucination kam, source citable.*

**Q2 (basic): When would you NOT use RAG — when is fine-tuning better?**
> RAG is for **knowledge** that changes or is too large to bake in — facts, docs, policies. Fine-tuning is for **behavior / form / style** — teaching the model a response format, a tone, a domain vocabulary, or a skill. They're complementary, not competing. If the answer lives in a document, retrieve it. If you want the model to *always respond in a structured maintenance-report format*, that's a prompt or a fine-tune. The 2026 rule of thumb: reach for RAG first (cheaper, updatable, auditable), fine-tune only when prompt + RAG can't get the behavior you need.
> 🔑 *RAG = knowledge (badalta rehta hai), fine-tune = behaviour/style. Pehle RAG try karo, fir fine-tune.*

**Q3 (intermediate): Explain naive vs advanced vs agentic RAG.**
> **Naive RAG** is the linear pipeline: chunk → embed → store → top-k cosine retrieve → stuff into prompt → generate. It works but breaks on ambiguous queries, poor recall, and lost-in-the-middle. **Advanced RAG** adds pre- and post-retrieval steps: query rewriting / HyDE, hybrid search (BM25 + dense), reranking, metadata prefiltering, contextual chunking. My Tata retriever is advanced — HyDE for short queries, hybrid dense+BM25, FlashRank rerank, equipment-ID prefilter. **Agentic RAG** wraps this in a reasoning loop: an agent decides *whether* to retrieve, *what* to query, can retrieve multiple times, route to different tools, and self-correct. My Wizard is agentic — a LangGraph agent runs retrieval as a tool and, if the NLI faithfulness gate fails, it re-retrieves with a tighter grounding instruction.
> 🔑 *Naive = seedhi line. Advanced = query-rewrite + hybrid + rerank. Agentic = agent khud decide kare kab/kya retrieve karna, fail ho to dobara.*

**Q4 (deep): Your naive RAG returns irrelevant chunks for a user's query. Walk me through your debugging order.**
> I debug from the data inward, not the model outward. **(1) Retrieval quality first** — pull the actual retrieved chunks and eyeball them; is the right chunk even in the corpus, and is it being retrieved at all? If it exists but isn't retrieved, it's a retrieval problem; if it's retrieved but ranked low, it's a ranking problem. **(2) Chunking** — is the answer split across a chunk boundary so no single chunk has it? **(3) Embedding mismatch** — short keyword query vs long prose chunk (asymmetry); this is where HyDE or query expansion helps. **(4) Hybrid gap** — if the query is an exact code/ID like "EAF-04", pure dense search misses it but BM25 nails it. **(5) Reranking** — add a cross-encoder rerank over top-20 if the right chunk is in the candidates but buried. Only after all that do I touch the generation prompt. The mantra: *garbage retrieval → garbage generation*, so 80% of RAG quality work is in retrieval, not the LLM.
> 🔑 *Pehle retrieval debug karo, LLM nahi. Right chunk corpus mein hai? retrieve hua? rank hua? — is order mein.*

**Q5 (curveball): "RAG is dead now that we have 1M-token context windows — just stuff everything in the prompt." Respond.**
> Long context complements RAG, it doesn't replace it. Three reasons: **cost** — stuffing 1M tokens every query is expensive and slow; RAG sends only the relevant few-K tokens. **Lost-in-the-middle** — models attend worse to the middle of huge contexts, so relevant facts get diluted; retrieval surfaces them at the top. **Auditability** — RAG gives you citations and a faithfulness gate; a giant prompt gives you a black box. And for any non-trivial corpus — millions of docs — it simply doesn't fit in 1M tokens anyway. The 2026 consensus is "RAG is not dead," it's evolving toward context engineering: retrieve smart, then optionally use longer context for the retrieved set.
> 🔑 *Long-context RAG ko replace nahi karta — cost, lost-in-the-middle, aur citations ki wajah se RAG zinda hai. Crore docs prompt mein fit hi nahi honge.*

**Traps / kya NA bolna:**
- ❌ "RAG fine-tunes the model on your data." NO — RAG retrieves at inference time, weights don't change.
- ❌ Saying RAG eliminates hallucination. It *reduces* it; the model can still misread or over-extrapolate from retrieved text — that's exactly why you add a faithfulness gate.
- ❌ Treating RAG as one fixed thing. Always frame it as a *pipeline with tunable stages*.

**Follow-up rabbit holes:** "How do you evaluate a RAG system?" (Ragas: context precision/recall, faithfulness, answer relevance) → "What's your eval golden set?" (you have `golden.jsonl` config in Wizard) → "How does agentic RAG decide when to retrieve?" → "GraphRAG vs vector RAG?"

---

## 2. Chunking Strategies (fixed / recursive / semantic, overlap, the ~500-token choice)

**Kya hai (Hinglish):** Documents bade hote hain, embeddings choti window pe achhe kaam karte hain, aur LLM ko sirf relevant tukda chahiye — isliye hum doc ko chote *chunks* mein todte hain. **Fixed-size**: har N characters/tokens pe kaat do (simple, par sentence beech mein toot sakti hai). **Recursive**: pehle paragraph pe todo, na ho to line pe, na ho to space pe — natural boundaries respect karta hai. **Semantic**: meaning badalne pe todo (embedding similarity drop pe). **Overlap** matlab consecutive chunks thoda overlap karein taaki boundary pe context na toote.

**Aapke project se connection:** Jarvis (`episodic_memory.py`) markdown ko heading boundaries pe todta hai, `CHUNK_TARGET_TOKENS = 500` (~2000 chars), `CHUNK_OVERLAP_CHARS = 100`. Tata Wizard (`ingestion.py`) **two-stage** karta hai: pehle `MarkdownHeaderTextSplitter` (##/### pe — section-aligned), fir `RecursiveCharacterTextSplitter` (512 chars, 64 overlap) — yeh production-grade pattern hai.

**Interview Q&A:**

**Q1 (basic): Why do we chunk documents at all?**
> Three reasons. Embedding models have a max input length and lose fidelity on long inputs — a 384-dim vector can't faithfully represent a 50-page manual. Retrieval needs *granularity* — you want to surface the one relevant paragraph, not the whole doc. And the LLM context budget is finite and you pay per token, so you only want to inject the relevant slices. Chunking is the unit of retrieval.
> 🔑 *Chunk = retrieval ka unit. Embedding choti window pe accurate, LLM ko sirf relevant tukda chahiye, token bachate hain.*

**Q2 (intermediate): Fixed vs recursive vs semantic chunking — when each?**
> **Fixed-size** is the baseline — fast, predictable, but cuts mid-sentence and ignores structure. **Recursive** (my default) splits on a priority list of separators — paragraph, then line, then sentence, then space — so it keeps natural boundaries while respecting a size cap; that's why I use `RecursiveCharacterTextSplitter` in the Tata Wizard. **Semantic** chunking uses embedding-similarity drops to find topic boundaries — highest quality on prose, but slow (you embed to chunk) and, per a Feb-2026 benchmark, recursive 512-token actually *beat* semantic on academic papers (69% vs 54%). My production take: recursive is the pragmatic sweet spot; I reach for semantic only when documents have no clean structural markers.
> 🔑 *Fixed = fast/dumb, recursive = natural boundaries (default), semantic = meaning-based par slow. 2026 benchmark mein recursive 512 ne semantic ko beat kiya.*

**Q3 (intermediate): Why ~500 tokens? And why overlap?**
> 500 tokens (~2000 chars) is the empirical sweet spot: big enough to hold a complete idea or procedure step, small enough that a single embedding stays focused and the LLM context isn't flooded. Too small (50 tokens) → fragments lose context; too big (2000 tokens) → the embedding becomes a blurry average of many topics and retrieval precision drops. **Overlap** (I use 64–100 chars) carries a sentence or two across the boundary, so a fact that lands right at a chunk edge isn't orphaned — both adjacent chunks share it and one of them will still retrieve cleanly.
> 🔑 *500 token = ek poora idea, par focused. Overlap = boundary pe context na toote, dono chunks mein thoda common.*

**Q4 (deep): Your answer is split across a chunk boundary — one chunk has the symptom, the next has the fix. How do you fix retrieval?**
> This is the classic boundary problem. Several levers: **(1) increase overlap** so both halves share more context. **(2) header-aware / structural chunking** — keep a whole procedure under one heading together; my Tata ingestion splits on markdown headers first so a SOP step stays intact. **(3) sentence-window / parent-document retrieval** — retrieve the small chunk for precision but pass its *parent* (the surrounding section) to the LLM for completeness. **(4) contextual retrieval** — prepend an LLM-generated context sentence to each chunk so it carries enough standalone meaning. And **(5) late chunking** — embed the whole document first with a long-context embedder, then pool token embeddings into chunks, so every chunk embedding "knows" the full-doc context.
> 🔑 *Boundary problem: overlap badhao, header-aware todo, parent-doc retrieval, ya contextual/late chunking — chunk ko standalone-meaningful banao.*

**Q5 (curveball): How do you chunk a PDF table or code, where character splitting destroys meaning?**
> You don't blindly character-split structured content. For **tables**, I keep the table as one atomic chunk (or serialize rows to markdown so each row+header is self-describing) — splitting a table mid-row destroys the column alignment. For **code**, I use a code-aware splitter that respects function/class boundaries rather than character counts. The general principle: chunking should respect the *semantic unit* of the content type — paragraph for prose, row/table for tabular, function for code. In Tata I convert PDFs to markdown via `pymupdf4llm` first precisely so structure survives into the splitter.
> 🔑 *Structured content ko character-split mat karo — table = ek chunk, code = function-boundary. Content-type ka semantic unit respect karo.*

**Traps / kya NA bolna:**
- ❌ "Bigger chunks are always better because more context." No — embedding precision degrades; it's a precision/recall tradeoff.
- ❌ Claiming semantic chunking is always best. 2026 benchmarks show recursive often wins and is far cheaper.
- ❌ Forgetting overlap entirely, or setting overlap so high you bloat the index with duplicates.

**Follow-up rabbit holes:** "What's late chunking?" → "Parent-document / sentence-window retrieval?" → "How do you pick chunk size empirically?" (sweep + eval on golden set) → "Contextual retrieval — what does the prefix contain?"

---

## 3. Embeddings (what they are; MiniLM vs bge-small vs OpenAI/Cohere; dimensionality; cosine)

**Kya hai (Hinglish):** Embedding matlab text ko ek numbers ki list (vector) mein badalna, jisme *meaning* encode ho. "dog" aur "puppy" ke vectors paas-paas honge, "dog" aur "Toyota" door. Yeh isliye ki retrieval mein hum keyword nahi, *meaning* match karte hain. Dimensionality = vector mein kitne numbers (384, 768, 1536). Cosine similarity = do vectors ke beech ka angle — 1 matlab same direction (same meaning), 0 matlab unrelated.

**Aapke project se connection:** Jarvis `all-MiniLM-L6-v2` (384-dim) use karta hai — chota, fast, local, free. Tata Wizard `BAAI/bge-small-en-v1.5` (384-dim, ONNX backend) — retrieval ke liye MiniLM se thoda strong (higher MTEB score). DataForge bhi bge-small. **Important detail aapke embedder.py mein**: `normalize_embeddings=True` — BGE family ke liye yeh REQUIRED hai, warna cosine galat aata hai.

**Interview Q&A:**

**Q1 (basic): What is a text embedding?**
> An embedding is a dense vector — a fixed-length list of floats, say 384 numbers — that represents the *meaning* of a piece of text in a continuous space. Texts with similar meaning land close together geometrically. It's produced by a neural encoder trained so that semantically related texts have high vector similarity. This is what lets us do *semantic* search: we embed the query and the chunks into the same space and find the nearest neighbors.
> 🔑 *Embedding = text ka meaning ek number-list mein. Similar meaning = paas-paas vectors. Isi se semantic search hota hai.*

**Q2 (intermediate): all-MiniLM-L6-v2 vs bge-small-en-v1.5 vs OpenAI/Cohere — how do you choose?**
> It's a quality / cost / privacy tradeoff. **all-MiniLM-L6-v2** (384-dim) is tiny (~80MB), runs locally, free, fast — I use it in Jarvis where I want zero API cost and full privacy on personal memory. **bge-small-en-v1.5** (384-dim) is also local and free but scores higher on the MTEB retrieval benchmark, so I picked it for the Tata Wizard where retrieval quality matters more. **OpenAI text-embedding-3 / Cohere embed-v3** are hosted, higher quality, support larger dimensions and Matryoshka truncation, but cost per call and send your data to a third party — a no-go for confidential steel-plant docs. My decision rule: start local with bge-small (free, good, private); only go hosted if eval shows a real quality gap that justifies the cost and the data-privacy cost.
> 🔑 *MiniLM = chota/fast/free (Jarvis), bge-small = local par stronger (Tata), OpenAI/Cohere = best par paid + data bahar jaata hai. Privacy + cost + quality ka tradeoff.*

**Q3 (intermediate): What does dimensionality (384 vs 1536) buy you, and what's the cost?**
> Higher dimensions can encode more semantic nuance and usually rank a bit higher on benchmarks, but they cost more storage, more RAM, and slower similarity computation — and the gains have diminishing returns. 384-dim like bge-small is plenty for most domain retrieval; I'd only jump to 1536 if eval showed a meaningful recall lift. Modern hosted models also support **Matryoshka representation learning**, where you can truncate a 1536-dim vector down to, say, 512 and keep most of the quality — so you tune dimension to your latency/storage budget.
> 🔑 *Zyada dimension = thoda zyada nuance par zyada storage/RAM/slow. 384 mostly kaafi. Matryoshka se vector chhota kar sakte ho quality khoye bina.*

**Q4 (deep): Why cosine similarity and not Euclidean distance? And what's the normalization gotcha?**
> Cosine measures the *angle* between vectors, ignoring magnitude — and for text embeddings, direction encodes meaning while magnitude is mostly noise (longer text can inflate magnitude without changing topic). So cosine is the standard. The gotcha: **if you L2-normalize your vectors, cosine similarity becomes equivalent to the dot product**, which is faster. That's exactly why my Tata embedder sets `normalize_embeddings=True` — BGE models are *trained* to be used normalized, and skipping it gives you wrong similarity scores. Chroma I configure with `hnsw:space="cosine"` so the index uses cosine distance directly.
> 🔑 *Cosine = angle (meaning), magnitude ignore. Normalize karo to cosine == dot product (fast). BGE ke liye normalize REQUIRED — warna similarity galat.*

**Q5 (deep): How does Chroma's distance relate to a 0–1 similarity score?**
> Chroma returns cosine *distance*, where 0 = identical and 2 = opposite. To get an intuitive 0–1 similarity I convert it: `score = 1 - distance/2`. That's the exact line in my `episodic_memory.recall()`. It matters because all my downstream thresholds (the 0.55 cutoff in Jarvis recall) are expressed in similarity space, so I need a consistent, monotonic mapping from the raw distance the index gives me.
> 🔑 *Chroma cosine distance 0–2 deta hai; main `1 - dist/2` se 0–1 similarity banata hu — taaki 0.55 threshold consistent rahe.*

**Traps / kya NA bolna:**
- ❌ Confusing embeddings with one-hot / TF-IDF vectors. Embeddings are *dense and learned*, not sparse keyword counts.
- ❌ Forgetting to use the *same* model for indexing and querying. Mismatched embedders = garbage similarity.
- ❌ Forgetting query/document asymmetry on some models (e.g. bge/e5 want a `"query:"` prefix on the query side).
- ❌ Saying "higher dimension is always better."

**Follow-up rabbit holes:** "What's the query prefix thing in E5/BGE?" → "Matryoshka embeddings?" → "How do you handle multilingual?" → "Dot product vs cosine in your vector DB config" → "How would you fine-tune an embedding model on your domain?"

---

## 4. sentence-transformers library

**Kya hai (Hinglish):** `sentence-transformers` ek Python library hai jo pre-trained embedding models (MiniLM, BGE, etc.) ko ek line mein load karke `.encode()` karwa deti hai. Yeh BERT-type models ko *sentence-level* embeddings ke liye wrap karti hai. Isme `CrossEncoder` bhi aata hai (rerank/NLI ke liye). Basically RAG ka embedding + rerank workhorse.

**Aapke project se connection:** Jarvis Chroma ke `SentenceTransformerEmbeddingFunction` se MiniLM load karta hai. Tata `embedder.py` directly `SentenceTransformer(model_name, backend="onnx")` use karta hai with `.encode(..., normalize_embeddings=True)`, aur `faithfulness.py` `CrossEncoder` se NLI DeBERTa load karta hai. Dono — bi-encoder aur cross-encoder — isi ek library se.

**Interview Q&A:**

**Q1 (basic): What is sentence-transformers and why use it over raw HuggingFace?**
> It's a library that gives you a clean `.encode()` API over embedding models, handling pooling, batching, and normalization for you. Raw HuggingFace gives you token-level hidden states; you'd have to do mean-pooling and normalization yourself. sentence-transformers does that correctly out of the box for both bi-encoders (`SentenceTransformer`) and cross-encoders (`CrossEncoder`). I use both classes in my Tata Wizard — `SentenceTransformer` for bge-small embeddings, `CrossEncoder` for the DeBERTa NLI faithfulness gate.
> 🔑 *sentence-transformers = `.encode()` ek line mein, pooling+normalize sambhaal leta hai. Bi-encoder aur cross-encoder dono isi se.*

**Q2 (intermediate): What's the ONNX backend and why did you use it?**
> ONNX is a portable, optimized inference runtime. Loading a sentence-transformer with `backend="onnx"` gives a roughly 1.4–3× CPU speedup over the default torch backend because it uses graph-optimized kernels and avoids torch overhead. My Tata embedder tries ONNX first and falls back to torch on ImportError — that matters because the whole Wizard runs on a laptop CPU during the demo with a tight latency budget, no GPU. I also pre-warm with one dummy encode so the first real query isn't cold.
> 🔑 *ONNX backend = CPU pe 1.4–3× fast. GPU nahi hai demo mein, isliye ONNX + pre-warm.*

**Q3 (deep): How would you batch-embed 100K chunks efficiently?**
> Use `model.encode(texts, batch_size=64)` — batching amortizes the model forward-pass overhead; I cap batch size at 64 to stay within CPU RAM. I keep the model as a module-level singleton so it loads once, not per call (lazy `_load_model()` in my embedder). For 100K I'd also persist embeddings to disk so re-ingestion is idempotent — my ingestion uses a content-hash `chunk_id` so re-running skips already-embedded chunks. On GPU I'd raise batch size and use fp16. The key wins: batch, singleton model, dedup, normalize once.
> 🔑 *Batch encode (64), model singleton (ek baar load), content-hash dedup, normalize. GPU pe bada batch + fp16.*

**Traps / kya NA bolna:**
- ❌ Reloading the model on every call (huge latency hit). Always singleton/lazy-load.
- ❌ Forgetting `normalize_embeddings=True` for models that require it.
- ❌ Mixing up `SentenceTransformer` (bi-encoder, embeds independently) with `CrossEncoder` (scores a pair jointly).

**Follow-up rabbit holes:** "Bi-encoder vs cross-encoder internals" (→ section 7) → "How do you serve embeddings at scale?" (batch endpoint, ONNX/TensorRT) → "Cold-start latency mitigation."

---

## 5. Vector DBs — ChromaDB vs pgvector vs LanceDB (when each)

**Kya hai (Hinglish):** Vector DB woh database hai jo embeddings store karta hai aur "is query vector ke nearest neighbors do" ko fast answer deta hai — usually HNSW ya IVF jaise ANN (approximate nearest neighbor) index se, taaki crore vectors mein bhi milliseconds mein search ho. Brute-force har vector se compare karna O(N) hai; ANN log-time ke kareeb.

**Aapke project se connection:** Aapne teen alag vector stores ship kiye hain — yeh ek strong interview signal hai:
- **ChromaDB** — Jarvis (`episodic_memory.py`), `PersistentClient`, `hnsw:space="cosine"`. Local, embedded, zero-setup — personal memory ke liye perfect.
- **LanceDB** — Tata Wizard (`store.py`), embedded, columnar Lance format, **native hybrid search** (dense + Tantivy BM25 ek hi call mein), SQL `where()` prefilter. Production-grade, no server.
- **pgvector** — McpIndex, Neon Postgres + pgvector + BM25 hybrid. Jab data already Postgres mein ho.

**Interview Q&A:**

**Q1 (basic): What does a vector database do that a normal DB can't?**
> It does fast approximate nearest-neighbor search over high-dimensional vectors. A normal DB indexes for exact lookups (B-tree on a key); it has no efficient way to answer "find the 5 vectors closest in cosine space to this query vector" without scanning everything. Vector DBs build ANN indexes — HNSW, IVF — that get you sub-linear search at the cost of being approximate. They also store metadata alongside vectors so you can filter (e.g. by equipment_id) and search together.
> 🔑 *Vector DB = fast nearest-neighbor (ANN/HNSW) + metadata filter. Normal DB exact-key ke liye hai, similarity ke liye nahi.*

**Q2 (intermediate): ChromaDB vs pgvector vs LanceDB — when do you pick each?**
> **ChromaDB** when I want a zero-setup embedded store for prototyping or a local app — that's Jarvis's personal memory, no server, persists to disk. **pgvector** when the data already lives in Postgres and I want vectors *alongside* my relational data in one transactional system — that's McpIndex on Neon Postgres, so I get SQL joins, BM25, and vector search in one DB without operating a separate vector service. **LanceDB** when I need an embedded store with first-class *hybrid* search and columnar speed without running a server — that's the Tata Wizard; its native `query_type="hybrid"` does dense + BM25 in one call and supports SQL `where()` prefilters. For a large hosted production system I'd consider Qdrant / Weaviate / pgvector-at-scale. My rule: embedded (Chroma/LanceDB) for local & demos, pgvector when Postgres is already the system of record, dedicated service when scale demands it.
> 🔑 *Chroma = local/prototype (Jarvis), pgvector = data already Postgres mein (McpIndex), LanceDB = embedded + native hybrid (Tata). Scale pe Qdrant/Weaviate.*

**Q3 (deep): Explain HNSW and the recall/latency tradeoff. How do you tune it?**
> HNSW — Hierarchical Navigable Small World — is a multi-layer graph where each node links to near neighbors; search starts coarse at the top layer and refines downward, giving roughly log-time nearest-neighbor lookup. The knobs: **`M`** (links per node — higher = better recall, more memory), **`ef_construction`** (build-time search width — higher = better graph, slower build), and **`ef_search`** (query-time candidate list — higher = better recall, higher latency). It's a recall-vs-latency dial: you raise `ef_search` until recall on your eval set is good enough, then stop because latency climbs. Because it's *approximate*, you trade a tiny bit of recall for a massive speedup over brute force. Chroma uses HNSW under the hood, which I configure for cosine space.
> 🔑 *HNSW = multi-layer graph, log-time ANN. M/ef_construction/ef_search tune karo — recall vs latency ka dial. Approximate isliye fast.*

**Q4 (deep / system-design): How do metadata filters interact with ANN search — pre-filter vs post-filter?**
> This is a real footgun. **Post-filter**: do ANN search, then drop results that don't match the filter — fast but you might get back fewer than k results if the filter is selective, because the matching docs weren't in the top candidates. **Pre-filter**: restrict the candidate set to filter-matching rows *before* / *during* ANN — correct cardinality but can be slower and some indexes don't support it well. In my Tata retriever I pass `prefilter=True` on the LanceDB `where()` clause for `equipment_id` / `doc_type` so I only ever rank chunks for the right equipment — critical for correctness in a multi-equipment plant. And because that `where()` is a SQL string, I sanitize the values (`_escape_sql_string`) to prevent SQL injection through the filter.
> 🔑 *Pre-filter = filter pehle (sahi count, Tata mein equipment_id pe), post-filter = baad mein (fast par kam results aa sakte). LanceDB where() SQL hai — sanitize karo.*

**Q5 (curveball): Your vector DB returns the right doc in dev but wrong ones in prod with the same query. What changed?**
> First suspect: the **embedding model or its version drifted** between index-time and query-time — if the corpus was indexed with one model and the query is embedded with another (or a different normalization setting), the spaces don't align and similarity is meaningless. Second: **the index was rebuilt with different ANN params** (lower `ef_search`) trading recall for speed in prod. Third: **stale or partially-ingested index** — prod corpus missing the doc. I'd verify the model name + normalization match exactly on both paths, check ANN params, and confirm the doc is actually in the prod index. Index/query embedding mismatch is the single most common silent RAG bug.
> 🔑 *Sabse common silent bug: index aur query alag model/normalize se. Pehle yeh check karo, fir ANN params, fir stale index.*

**Traps / kya NA bolna:**
- ❌ "Vector DBs are exact." They're approximate (ANN) by default.
- ❌ Recommending a heavy dedicated service (Pinecone/Weaviate) for a tiny local app — over-engineering. Match the tool to scale.
- ❌ Ignoring metadata filtering — interviewers love the pre/post-filter distinction.

**Follow-up rabbit holes:** "HNSW vs IVF-PQ" → "How do you handle index updates / deletes?" → "Sharding vectors at billion-scale" → "Quantization (scalar/product) to save memory."

---

## 6. Similarity Thresholds (the 0.55 choice)

**Kya hai (Hinglish):** Retrieval hamesha top-k laata hai — chahe woh relevant ho ya nahi. Threshold ek minimum similarity score hai; usse neeche wale chunks ko hum *discard* kar dete hain, taaki LLM ko kachra context na mile. 0.55 ka matlab: "agar koi memory query se 55%+ similar nahi hai, to use bhejo hi mat — usse better hai kuch na bhejna."

**Aapke project se connection:** Jarvis `recall.py` mein `_DEFAULT_SCORE_MIN = 0.55`. Code line: `hits = [h for h in raw_hits if h.get("score", 0.0) >= self.score_min]`. Agar kuch bhi 0.55 cross nahi karta → `NO_HITS_ABOVE_THRESHOLD` → empty context, LLM apne knowledge se jawab deta hai. Yeh deliberate hai: galat memory inject karne se better hai koi memory na inject karna.

**Interview Q&A:**

**Q1 (basic): Why apply a similarity threshold at all — why not always take top-k?**
> Because top-k always returns *something*, even when nothing is actually relevant. If the closest chunk is only 0.2 similar, injecting it just feeds the LLM noise and can *cause* hallucination — the model trusts the provided context. A threshold says "below this bar, treat it as no match and inject nothing." In Jarvis, if no memory clears 0.55, I send an empty context block and let the model answer from its own knowledge — which is the honest behavior.
> 🔑 *Top-k hamesha kuch deta hai chahe relevant na ho. Threshold = kachra context block karo; galat memory se better koi memory nahi.*

**Q2 (intermediate): Why 0.55 specifically? How would you calibrate it?**
> 0.55 is an empirically-chosen operating point, not magic. I'd calibrate it with a labeled set: take queries with known-relevant and known-irrelevant chunks, sweep the threshold, and plot precision vs recall. Too high (0.8) → you miss genuinely relevant memories (low recall); too low (0.3) → noise leaks in (low precision). 0.55 on my MiniLM cosine-similarity scale sits where relevant memories pass but unrelated ones are filtered. Crucially, the right number depends on the **embedding model and the distance→score mapping** — my `1 - dist/2` conversion — so a threshold isn't portable across models; you re-calibrate per model.
> 🔑 *0.55 empirical hai — labeled set pe sweep karke precision/recall dekho. Model badle to threshold dobara calibrate, portable nahi.*

**Q3 (deep): A fixed global threshold isn't ideal. What's better?**
> A single global threshold ignores query difficulty — some queries have many strong matches, some have one weak-but-correct match. Better options: **(1) relative / score-gap thresholding** — keep results within X of the top score rather than an absolute floor. **(2) top-k + threshold combined** — cap count *and* require minimum similarity (what I do). **(3) let a reranker decide** — retrieve generously, then a cross-encoder gives a sharper relevance score to threshold on, which is more reliable than raw cosine. **(4) adaptive thresholds** learned per query type. In Tata I lean on reranking rather than a hard cosine cutoff because the cross-encoder's score is a much better relevance signal than bi-encoder cosine.
> 🔑 *Global fixed threshold weak hai. Better: score-gap relative, ya reranker ke score pe threshold (cosine se sharper).*

**Traps / kya NA bolna:**
- ❌ Treating 0.55 as a universal constant. It's model- and mapping-specific.
- ❌ Setting it too high and silently starving the LLM of context.
- ❌ Confusing cosine *similarity* threshold with cosine *distance* threshold (inverse directions).

**Follow-up rabbit holes:** "How do you log/monitor threshold misses?" (you log `skipped_reason` to recall.jsonl) → "Score-gap thresholding" → "Why is bi-encoder cosine a weaker relevance signal than a cross-encoder?"

---

## 7. Reranking (FlashRank, cross-encoder vs bi-encoder, why rerank after retrieve)

**Kya hai (Hinglish):** Retrieval (bi-encoder) fast hai par mota hai — query aur chunk ko *alag-alag* embed karke compare karta hai, isliye fine relevance miss kar sakta hai. **Reranking** ek doosra, sharper model (cross-encoder) leta hai jo query aur chunk ko *ek saath* padhta hai aur precise relevance score deta hai. Pattern: pehle retriever se top-20 sasta-fast nikaalo, fir cross-encoder se unhe re-order karke top-5 chuno. Fast recall + precise judgment.

**Aapke project se connection:** Tata `retriever.py` — hybrid search se 20 candidates (`rag_top_k_retrieve=20`), fir **FlashRank** (`ms-marco-MiniLM-L-12-v2`, ONNX, ~15–30ms for 30 candidates) se rerank karke top-5 (`rag_top_k_final=5`). Code: `RerankRequest(query, passages)` → `ranker.rerank()`. NLI gate bhi cross-encoder hi hai (DeBERTa).

**Interview Q&A:**

**Q1 (basic): What is reranking and why do it after retrieval?**
> Reranking is a second, more accurate scoring pass over the top candidates from your initial retrieval. The initial retriever (bi-encoder) is optimized for *speed at scale* — it can search millions of vectors fast but its relevance estimate is coarse. The reranker (cross-encoder) is *accurate but slow* — too slow to run over the whole corpus, but perfect for re-scoring just the top 20. So you get the best of both: cheap high-recall retrieval, then expensive high-precision ranking on a small set. In Tata I retrieve 20 then FlashRank down to 5.
> 🔑 *Retriever fast-but-coarse (lakhon vectors), reranker slow-but-sharp (sirf top-20 pe). Recall + precision dono.*

**Q2 (intermediate): Bi-encoder vs cross-encoder — what's the architectural difference?**
> A **bi-encoder** embeds the query and the document *separately* into vectors, then compares with cosine. Because docs are embedded offline and independently, it's fast and indexable — but the query never "sees" the document during encoding, so it misses fine interactions. A **cross-encoder** takes the query and document *together* as one input to the transformer and outputs a single relevance score — full cross-attention between them, so it catches nuance a bi-encoder misses. The cost: you can't pre-compute it; you must run the model per (query, doc) pair at query time. That's why bi-encoder = retrieval, cross-encoder = reranking.
> 🔑 *Bi-encoder = query aur doc alag-alag embed (fast, indexable). Cross-encoder = dono saath padhe (sharp, par har pair pe chalana padta). Isliye bi=retrieve, cross=rerank.*

**Q3 (intermediate): Why FlashRank specifically?**
> FlashRank is a lightweight reranker that runs cross-encoder models in ONNX with no torch dependency — so it's tiny and CPU-fast, ~15–30ms for ~30 candidates. For the Tata Wizard, which runs on a laptop CPU during the demo with a sub-2-second budget, a heavyweight torch reranker would blow the latency. FlashRank gives me cross-encoder-quality reranking that fits the budget. I load it as a singleton with a cache_dir so the model loads once.
> 🔑 *FlashRank = cross-encoder ONNX, torch-free, CPU pe ~15–30ms. Laptop demo ke tight budget ke liye perfect.*

**Q4 (deep): Where does ColBERT / late-interaction fit between bi- and cross-encoders?**
> ColBERT is the middle ground. A bi-encoder pools everything into one vector per text; a cross-encoder jointly encodes the pair. **ColBERT stores per-token embeddings** and scores with *late interaction* — a MaxSim operation between every query token and every doc token. That captures much of the cross-encoder's token-level nuance but, because doc token embeddings are pre-computed, it's far faster than a cross-encoder — near cross-encoder accuracy at near bi-encoder speed. The cost is storage: many vectors per document. In 2026 it's a strong option when you need high accuracy at scale and can afford the index size; for my laptop demo, retrieve-then-FlashRank was the right cost/quality point, but I'd reach for ColBERT-style late interaction in a larger hosted system.
> 🔑 *ColBERT = per-token embeddings + late interaction (MaxSim). Cross-encoder jaisi accuracy, bi-encoder jaisi speed — par storage zyada. Scale pe acha.*

**Q5 (curveball): Reranking adds latency. When is it NOT worth it?**
> When recall is already the bottleneck, not precision — if your retriever isn't even getting the right doc into the top-20, reranking can't fix that; you'd fix retrieval first (hybrid, better embeddings, query expansion). It's also not worth it on ultra-low-latency paths where every ms counts and the top-k is already good, or on very small corpora where the bi-encoder already ranks well. Reranking pays off when the right answer is *in* your candidate set but *buried* — that's the precise problem it solves. So I always check: is the right chunk in the top-20? If yes, rerank. If no, fix retrieval.
> 🔑 *Rerank tab worth jab sahi chunk top-20 mein hai par buried. Agar woh aa hi nahi raha (recall problem), pehle retrieval fix karo — rerank usse nahi bachayega.*

**Traps / kya NA bolna:**
- ❌ "Reranking improves recall." No — it improves *precision/ordering* of an already-retrieved set; recall is fixed at retrieval.
- ❌ Reranking the entire corpus (defeats the purpose — that's what cross-encoders are too slow for).
- ❌ Confusing FlashRank (reranker) with the embedding model (retriever).

**Follow-up rabbit holes:** "ColBERT index size / PLAID" → "Cohere Rerank / hosted rerankers" → "How many candidates to rerank (the 20 choice)?" → "LLM-as-reranker (listwise)."

---

## 8. NLI Faithfulness / Grounding Gating (DeBERTa entailment, hallucination detection, citation verification)

**Kya hai (Hinglish):** RAG mein LLM ko sahi context milne ke baad bhi woh galat dava (claim) kar sakta hai — context se zyada bol dena, ya cited source mein jo likha hi nahi woh keh dena. **NLI (Natural Language Inference)** ek model hai jo do texts ka rishta batata hai: *entailment* (source claim ko support karta hai), *contradiction* (ulta), ya *neutral* (na support na ulta). **Faithfulness gate** matlab: har cited claim ko uske source chunk ke against NLI se check karo — agar entailment kam hai, claim grounded nahi hai → hallucination flag → retry.

**Aapke project se connection:** Tata `faithfulness.py` — `cross-encoder/nli-deberta-v3-small` har `[N]`-cited sentence ko uske source chunk ke against score karta hai. 3 classes: contradiction/entailment/neutral. `entailment_prob >= threshold` → faithful. Agar overall faithfulness < threshold → `flag_for_retry=True` → agent dobstronger grounding instruction ke saath retry karta hai. Confidence tags: ≥0.75 `verified`, ≥0.5 `unverified`, neeche `low`. Yeh aapke Jarvis `critic.py` + `confidence.py` ke design philosophy se aligned hai — silent verification layer.

**Interview Q&A:**

**Q1 (basic): What is a faithfulness gate in RAG?**
> It's a post-generation check that verifies the LLM's answer is actually supported by the retrieved sources it cited — not invented. Even with good retrieval, the model can over-claim. The gate extracts each cited sentence, checks it against its source chunk with an NLI model, and if the claim isn't entailed by the source, flags it as unfaithful. In my Tata Wizard, if overall faithfulness drops below threshold, the agent retries generation with a tighter "stick to the sources" instruction. It's the difference between "the model said it" and "the source supports it."
> 🔑 *Faithfulness gate = answer sach mein cited source se grounded hai ya LLM ne bana diya — NLI se verify, fail to retry.*

**Q2 (intermediate): Explain NLI entailment and how you use the three classes.**
> NLI takes a premise and a hypothesis and classifies their relationship: **entailment** (premise supports the hypothesis), **contradiction** (premise refutes it), or **neutral** (neither). In my faithfulness gate the premise is the retrieved source chunk and the hypothesis is the LLM's cited claim. I use the **entailment probability** (index 1 of the softmax output) as the faithfulness score — high entailment means the source genuinely backs the claim. A high *contradiction* probability is even worse than neutral — it means the model said the opposite of the source, a hard hallucination. I average entailment across all cited claims for an overall score.
> 🔑 *NLI: entailment (support) / contradiction (ulta) / neutral. Source=premise, claim=hypothesis. Entailment prob = faithfulness score; contradiction = sabse bura.*

**Q3 (intermediate): Why DeBERTa NLI and not just ask the LLM "is this faithful?"**
> Two reasons: **independence and cost**. Using a small, dedicated NLI model (deberta-v3-small, ~80MB, CPU, ~80–120ms/claim) is a *separate* verifier — it's not the same model that wrote the answer, so it's not biased toward approving its own output, and it's cheap and deterministic. Asking the generating LLM to self-grade is circular and costs another expensive call. That said, LLM-as-judge is a valid alternative for nuanced cases; I'd use NLI as the fast first gate and escalate to an LLM judge only when needed. The architecture mirrors my Jarvis critic — a small independent reviewer, not the author marking its own homework.
> 🔑 *Alag chhota NLI model = bias-free, sasta, deterministic. LLM khud ko grade kare = circular + mehnga. NLI fast gate, LLM-judge sirf nuanced cases.*

**Q4 (deep): Your threshold is 0.5 but you tagged it [unverified] in code. Why, and how do you set it properly?**
> Because 0.5 is borrowed from general NLI benchmarks (SNLI/MultiNLI) and isn't calibrated for steel-plant maintenance text — domain text has different phrasing, so the entailment distribution shifts. I literally flagged it `[unverified]` in the code comment as an honesty marker. To set it properly I'd build a small labeled set — say 20 Q&A pairs from the synthetic corpus with human-judged faithful/unfaithful labels — run the NLI gate, and pick the threshold that best separates them (maximize F1 or hit a target precision). The literature's 0.6 is a starting point, not a final value. The discipline is: never ship a borrowed threshold as if it were calibrated.
> 🔑 *0.5 SNLI se udhaar liya, domain ke liye calibrate nahi — isliye [unverified] likha. 20 labeled pairs pe sweep karke set karna chahiye.*

**Q5 (deep / system-design): How do you verify *citations* specifically, not just overall faithfulness?**
> I parse the answer for inline `[N]` markers, split it into sentences, and for each cited sentence map `[N]` back to the exact source chunk it points to — then NLI-score *that sentence against that specific chunk*. This catches "citation drift": the model cites Source [2] but the claim is actually only supported by Source [3], or by nothing. My `_extract_cited_sentences` regex pulls the citation numbers, `chunk_map` resolves them to chunks, and per-chunk faithfulness is the *min* entailment of all claims citing it (worst-case, conservative). That per-claim, per-citation granularity is what makes it a real citation verifier and not just a vibe check.
> 🔑 *Har [N]-cited sentence ko uske exact source chunk ke against NLI karo — "citation drift" pakadta hai. Per-chunk score = min entailment (worst-case).*

**Traps / kya NA bolna:**
- ❌ Saying a faithfulness gate "eliminates" hallucination. It *detects and flags* it; you still need the retry/abstain action.
- ❌ Using the generating LLM to grade itself without acknowledging the bias.
- ❌ Shipping a borrowed NLI threshold as calibrated (your own code flags this honestly — say so, it's a strength).
- ❌ Confusing faithfulness (grounded in source) with answer-relevance (answers the question) — they're different Ragas metrics.

**Follow-up rabbit holes:** "Ragas faithfulness vs answer-relevancy vs context-precision" → "What action on a failed gate — retry, abstain, or surface uncertainty?" → "How do you handle multi-hop claims spanning two chunks?" → "LLM-as-judge calibration."

---

## 9. Hybrid Search (BM25 + vector, RRF)

**Kya hai (Hinglish):** Dense vector search *meaning* match karta hai par exact keywords/codes (jaise "EAF-04", part number) miss kar deta hai. **BM25** purana keyword/lexical search hai — exact terms pe strong, par meaning nahi samajhta. **Hybrid** dono ko milata hai: dense semantic + BM25 lexical. **RRF (Reciprocal Rank Fusion)** ek simple, robust tarika hai dono result-lists ko merge karne ka — har doc ka score `1/(k + rank)` har list mein, fir add — koi raw score normalize karne ki zaroorat nahi.

**Aapke project se connection:** Tata `retriever.py` — LanceDB `query_type="hybrid"`, `.vector(query_vec)` (dense) + `.text(query)` (BM25 via Tantivy FTS index). McpIndex bhi BM25 + pgvector hybrid. DataForge `gate.py` mein bhi hybrid scoring: `0.65 × KB-match + 0.35 × embed-sim` — alag domain mein wahi philosophy. Aapne hybrid teen jagah ship kiya hai.

**Interview Q&A:**

**Q1 (basic): What is hybrid search and why is it better than pure vector?**
> Hybrid search combines lexical (BM25 keyword) retrieval with dense (vector semantic) retrieval. Pure vector search is great at meaning — "cooling problem" matches "thermal fault" — but it's weak on exact tokens like part numbers, error codes, or rare proper nouns, where the exact string matters more than the semantics. BM25 nails those. Combining them covers each other's blind spots. In my Tata Wizard, a query like "EAF-04 bearing temp" needs BM25 to lock onto the exact equipment tag *and* dense search to understand "bearing temp" semantically — hybrid gets both.
> 🔑 *Dense = meaning (par exact code miss). BM25 = exact keyword (par meaning nahi). Hybrid = dono ke blind spots cover.*

**Q2 (intermediate): What is BM25 in one breath?**
> BM25 is a bag-of-words lexical ranking function — an improved TF-IDF. It scores a document by how often the query terms appear (term frequency, with diminishing returns via saturation) weighted by how rare those terms are across the corpus (inverse document frequency), and it normalizes for document length so long docs don't unfairly win. No embeddings, no neural net — fast, interpretable, and unbeatable for exact-term matching. LanceDB implements it via a Tantivy full-text index, which I build on the `text` column after ingestion.
> 🔑 *BM25 = smart TF-IDF: term frequency (saturating) × rarity (IDF), length-normalized. Exact-keyword ka king, neural nahi.*

**Q3 (intermediate): How do you combine the two ranked lists — explain RRF.**
> The challenge is that BM25 scores and cosine scores are on totally different scales, so you can't just add them. **Reciprocal Rank Fusion** sidesteps this by using *ranks*, not scores: each document gets `1/(k + rank)` from each list (k is a constant, often 60), and you sum those across lists. A doc ranked high in *either* list scores well; a doc ranked high in *both* dominates. It's score-agnostic, needs no normalization or tuning, and is remarkably robust — which is why it's the default fusion method in 2026. The alternative is weighted score fusion (normalize then `α·dense + (1-α)·sparse`), which is what my DataForge gate effectively does with its 0.65/0.35 KB/embed weights.
> 🔑 *RRF = ranks merge karo, scores nahi (alag scale). `1/(k+rank)` har list se, add karo. Tuning-free, robust. Alternative = weighted score fusion (DataForge 0.65/0.35).*

**Q4 (deep): Your hybrid search underperforms pure dense on a benchmark. How do you diagnose?**
> First check the **fusion weighting** — if BM25 is over-weighted on a semantic-heavy query set, it can drag in keyword-matched but irrelevant docs; tune α or trust RRF. Second, **query type mismatch** — hybrid wins on mixed queries (codes + concepts); on a benchmark of purely conceptual questions, dense alone may legitimately win, so the benchmark may not represent production traffic. Third, **BM25 index health** — wrong tokenizer, stopword handling, or a stale FTS index gives bad lexical results; in LanceDB I rebuild the Tantivy index after every ingest. Fourth, add a **reranker after fusion** — let the cross-encoder make the final call over the merged candidates, which usually recovers any fusion noise. The honest answer: hybrid isn't universally better; it's better on *mixed* workloads, and you validate per use case.
> 🔑 *Fusion weight check, query-type match check, BM25 index health, fir reranker laga do. Hybrid sirf mixed queries pe jeet ta — universally nahi.*

**Q5 (curveball): Contextual Retrieval — how does it relate to hybrid search and why does it matter in 2026?**
> Anthropic's Contextual Retrieval is a 2026 best-practice upgrade that *feeds* hybrid search. The problem: a chunk like "the valve must be inspected every 500 hours" loses meaning when isolated — which valve, which equipment? Contextual Retrieval prepends a short LLM-generated context sentence to each chunk *before* embedding and BM25-indexing it, so both the dense vector and the lexical index carry the disambiguating context. Anthropic reports it cuts top-20 retrieval failures ~35% alone, ~49% combined with BM25, and ~67% when you add reranking — so it stacks with hybrid and rerank. I built exactly this as `_inject_contextual_prefixes` in my Tata ingestion ("This chunk describes..."), gated behind a flag because it costs one cheap LLM call per chunk at index time. Late chunking is the related 2026 idea — embed the full doc first, then pool into chunks — same goal, no extra LLM call.
> 🔑 *Contextual Retrieval = har chunk ke aage LLM se context-sentence laga ke embed/index karo. Top-20 failures 67% tak kam (BM25+rerank ke saath). Maine `_inject_contextual_prefixes` mein banaya. Late chunking = same goal, bina extra LLM call.*

**Traps / kya NA bolna:**
- ❌ "Just average the BM25 and cosine scores." They're on different scales — naive averaging is wrong; use RRF or normalize first.
- ❌ Claiming hybrid is always better. It's better on *mixed* workloads.
- ❌ Forgetting to rebuild the BM25/FTS index after ingestion (stale lexical index → silent recall loss).
- ❌ Confusing BM25 (sparse lexical) with sparse *learned* retrievers like SPLADE (neural sparse) — know they exist.

**Follow-up rabbit holes:** "RRF k constant choice" → "SPLADE / learned sparse" → "Contextual Retrieval cost at scale" → "Late chunking vs contextual chunking" → "How do you weight α in score fusion empirically?"

---

## 10. SYSTEM DESIGN — "Design a RAG system for X"

> This is the near-certain capstone question. Practice saying it as a **structured walk-through**. Use your Tata Wizard as the worked example — you have a real, shipped answer.

**The framework (memorize this skeleton):**

1. **Clarify requirements** — corpus size & type, query volume/latency budget, accuracy bar, data privacy (on-prem vs hosted?), update frequency, multi-tenant/filtering needs, citation requirement. *Ask, don't assume.*
2. **Ingestion pipeline** — load (PDF→markdown via pymupdf4llm), chunk (header-aware → recursive 512/64), optional contextual prefix, embed (bge-small ONNX, normalized), store with rich metadata (equipment_id, doc_type, section) for filtering. Idempotent via content-hash IDs.
3. **Storage** — vector DB choice justified by scale & data location (LanceDB embedded for demo; pgvector if Postgres is the SoR; Qdrant/Weaviate at large hosted scale). Build BM25/FTS index for hybrid.
4. **Retrieval** — query rewrite/HyDE for short queries → hybrid (dense + BM25, RRF/native fusion) → metadata prefilter (equipment_id) → top-20 candidates → cross-encoder rerank (FlashRank) → top-5.
5. **Generation** — inject reranked chunks as numbered `Source [N]` blocks, prompt the LLM to answer *only* from sources with inline `[N]` citations, low temperature.
6. **Verification** — NLI faithfulness gate per cited claim; if it fails, retry with tighter grounding or abstain/surface uncertainty. Attach confidence tag.
7. **Evaluation** — Ragas (context precision/recall, faithfulness, answer relevancy) on a golden set; track over time; regression-gate deploys.
8. **Observability & ops** — trace every stage (Phoenix/Langfuse), log retrieval misses, monitor latency per stage, cost per query, cache embeddings, circuit-breaker the LLM.

**Model answer (worked, condensed) — "Design a RAG system for an industrial equipment maintenance assistant":**
> First I'd clarify: corpus is plant manuals + SOPs + failure reports, queries from maintenance engineers, sub-2-second latency, accuracy is safety-critical so citations are mandatory, and the data is confidential so everything runs on-prem with no data leaving — that rules out hosted embeddings.
>
> **Ingestion:** convert PDFs to markdown with pymupdf4llm so structure survives, two-stage chunk — markdown-header split to keep SOP steps intact, then recursive 512-token/64-overlap — embed with bge-small-en-v1.5 in ONNX (local, free, 384-dim, normalized), and store in LanceDB with metadata: equipment_id, doc_type, section, criticality. I make ingestion idempotent with content-hash chunk IDs and build a Tantivy BM25 index for hybrid.
>
> **Retrieval:** for short queries I run HyDE — generate a hypothetical answer and embed *that* to bridge the query-document gap. Then LanceDB native hybrid (dense + BM25) with an equipment_id prefilter so I only rank chunks for the right machine, pull 20 candidates, and FlashRank-rerank down to 5. That's ~30–60ms on CPU.
>
> **Generation:** inject the 5 chunks as numbered `Source [N]` blocks, instruct the LLM to answer only from sources with inline citations, temperature 0.1.
>
> **Verification:** a DeBERTa NLI gate scores each cited claim against its source chunk; if overall faithfulness is low, the agent retries once with a stricter grounding instruction. Every response carries a verified/unverified confidence tag.
>
> **Eval & ops:** Ragas on a golden Q&A set gating deploys, Phoenix tracing on every stage, and I log retrieval misses to tune chunk size and thresholds. For scale beyond one plant I'd move to a hosted vector service and add caching.
>
> The throughline: retrieval quality is 80% of the work, and for safety-critical maintenance, the faithfulness gate is non-negotiable — I never let the model answer ungrounded.
> 🔑 *Skeleton: clarify → ingest (chunk+embed+metadata) → store+BM25 → retrieve (HyDE+hybrid+prefilter+rerank) → generate (cited) → NLI verify → eval (Ragas) → observe. Tata Wizard se bolo, real example hai.*

**Curveball follow-ups they'll throw:**
- *"How do you keep the index fresh as docs change?"* → idempotent content-hash IDs + incremental re-ingest + rebuild FTS; soft-delete stale revisions via the `revision` metadata field.
- *"How do you handle a query with no good answer?"* → threshold + faithfulness gate → abstain honestly ("not in the manuals") rather than hallucinate. This is exactly your Jarvis `NO_HITS_ABOVE_THRESHOLD` behavior.
- *"Cost at scale?"* → cache embeddings (idempotent), batch-embed, ONNX/quantize, cache frequent query results, use cheap models for HyDE/contextual.
- *"How do you eval without ground truth?"* → Ragas reference-free metrics (faithfulness, context relevance) + LLM-as-judge + a small human-labeled golden set.

**Traps / kya NA bolna:**
- ❌ Jumping straight to "use Pinecone and OpenAI embeddings" without clarifying requirements (privacy! latency! scale!).
- ❌ Skipping evaluation — a senior signal is that you *measure* retrieval, not just build it.
- ❌ Ignoring metadata filtering and multi-tenancy in a real product.
- ❌ No story for hallucination/faithfulness in a high-stakes domain.

---

## Quick-reference cheat sheet (your real numbers)

| Component | Jarvis | Tata Wizard | McpIndex / DataForge |
|---|---|---|---|
| Vector store | ChromaDB (HNSW, cosine) | LanceDB (columnar, native hybrid) | pgvector (Postgres) / — |
| Embedding | all-MiniLM-L6-v2, 384-dim | bge-small-en-v1.5, 384-dim, ONNX | bge-small / pgvector |
| Chunking | heading + ~500 tok, 100 overlap | header-split → recursive 512/64 | — |
| Hybrid | dense only | dense + BM25 (Tantivy) | BM25 + pgvector / KB 0.65 + embed 0.35 |
| Query expansion | — | HyDE (≤12-token queries) | — |
| Rerank | — | FlashRank ms-marco-MiniLM-L-12-v2 | — |
| Faithfulness | critic.py (Haiku) + confidence | DeBERTa NLI gate, retry-on-fail | anti-gaming relevance gate |
| Threshold | 0.55 cosine sim | NLI 0.5 [uncalibrated] | relevance 30/100 |
| top-k | k=5 | retrieve 20 → final 5 | — |

**2026 SOTA to name-drop:** Contextual Retrieval (Anthropic, −67% top-20 failures w/ rerank — *you built it as `_inject_contextual_prefixes`*), Late Chunking (Jina), ColBERT / late-interaction (per-token + MaxSim), recursive 512-tok beating semantic on Feb-2026 benchmark, cross-encoder rerank as default when 50–200ms latency allows, RRF as default fusion.

**Sources (2026 SOTA framing):**
- [RAG Is Not Dead: Advanced Retrieval Patterns That Actually Work in 2026 (dev.to)](https://dev.to/young_gao/rag-is-not-dead-advanced-retrieval-patterns-that-actually-work-in-2026-2gbo)
- [RAG Chunking Strategies: A 2026 Retrieval Playbook (digitalapplied.com)](https://www.digitalapplied.com/blog/rag-chunking-strategies-2026-retrieval-quality-playbook)
- [Best Chunking Strategies for RAG in 2026 (firecrawl.dev)](https://www.firecrawl.dev/blog/best-chunking-strategies-rag)
- [From RAG to Context — 2025 year-end review (RAGFlow)](https://ragflow.io/blog/rag-review-2025-from-rag-to-context)
- [ColBERT-Att: Late-Interaction Meets Attention (arXiv)](https://arxiv.org/pdf/2603.25248)
