# McpIndex — Interview Prep (Hybrid Search Platform)

> **Project:** McpIndex — production search over 1,532 MCP servers. Hybrid BM25 + pgvector semantic search + a 6-dimensional automated quality-scoring pipeline. Built in 2 days, deployed to Vercel. Live: `mcpindex-nu.vercel.app`.
> **Stack (grounded from real repo `/home/ujjwal/Documents/mcp-hub/`):** Next.js 16 (App Router) · Neon serverless Postgres · `pgvector` · Gemini embeddings · Tailwind 4 · Vercel.
> **Real code touchpoints (from the security audit of the actual repo):** `src/app/api/search/route.ts` (search endpoint), `src/lib/data.ts` (`searchServersBySimilarity`, `browseServers`, `keywordFallback`, `getSimilarServers`, `dbRowToSummary` parsing `score_dimensions`), `src/lib/embeddings.ts` (`generateEmbedding` → Gemini `embedContent`), `scripts/scrape-github.ts` (the offline ingest/scrape pipeline).

**How to frame it in one breath (your elevator line):**
> "McpIndex is a search engine for MCP servers — 1,532 of them scraped from GitHub. The retrieval is hybrid: Postgres BM25 for exact keyword matches plus pgvector cosine similarity for semantic intent, fused together so you get both literal precision and conceptual recall. Every server also gets an automated 6-dimensional quality score so results aren't just relevant, they're ranked by quality. Whole thing shipped in 2 days on Next.js + Neon + Vercel."

🔑 *Pitch yaad rakhna: "hybrid = keyword + semantic fuse," "1,532 servers," "6-dim quality score," "2 din mein shipped." Yeh char cheezein bol dije, baaki interviewer khud drill karega.*

---

### Hybrid Search — what it is and WHY

**Kya hai (Hinglish):** Do alag-alag tareeke se search hota hai. **BM25 (lexical/keyword)** — yeh exact shabd match karta hai, jaise Ctrl+F ka smart version: "kaun se documents mein yeh exact word zyada baar aaya, aur woh word kitna rare hai." **Vector/semantic search** — yeh matlab (meaning) match karta hai: query aur document dono ko numbers ke vector mein badalta hai, fir jo vectors paas-paas hain wahi similar maane jaate hain. Akela koi bhi perfect nahi — isliye dono ko milake **hybrid** banate hain.

Samajhiye kyun dono chahiye: agar koi search kare `"postgres"` to BM25 turant exact match dega. Lekin agar koi search kare `"store embeddings in a database"` — yahaan koi exact word match nahi hoga par semantic search samajh jaayega ki user ko vector-database wale MCP servers chahiye. Ulta, agar query mein koi rare exact token ho — error code, ek API ka naam, ek slug — to vector search usko "blur" kar deta hai (kyunki embeddings meaning capture karte hain, exact spelling nahi), aur BM25 usko pakka pakad leta hai.

**Aapke project se connection:** McpIndex mein dono paths real code mein hain. Semantic path = `searchServersBySimilarity()` in `src/lib/data.ts` — yeh `generateEmbedding(query)` (Gemini) call karke pgvector cosine search chalata hai. Lexical fallback/path = `keywordFallback()` in the same file (Postgres text search over name/description). `/browse?q=` aur `/api/search?q=` dono in paths ko hit karte hain. So jab interviewer poochhe "did you actually build hybrid?" — haan, dono retrievers repo mein maujood hain.

**Interview Q&A:**

**Q1 (basic): What is hybrid search and why use it instead of just vector search?**
> Hybrid search combines two retrieval methods: lexical search (BM25 over a keyword index) and dense vector search (embeddings + cosine similarity). I use both because they fail in opposite ways. Vector search is great at semantic intent — "store embeddings in a database" finds a vector-DB server even with zero shared words — but it blurs exact tokens like error codes, slugs, or specific tool names. BM25 nails those exact tokens but is blind to synonyms and paraphrases. Fusing them gives lexical precision plus semantic recall, which in production consistently beats either alone.
> 🔑 *Vector = matlab samajhta hai, BM25 = exact word pakadta hai. Dono ke fail hone ke tareeke ulte hain, isliye fuse karo.*

**Q2 (basic→intermediate): Give a concrete query where vector search alone would fail.**
> Anything with a rare literal token. If someone searches for an exact server slug like `stripe-mcp` or an error string like `ECONNREFUSED`, the embedding for that gets averaged into something generic — the model has no strong concept for a one-off token, so it returns vaguely-related things instead of the exact match. BM25 weights that rare token heavily (high IDF) and surfaces the exact doc instantly. The reverse failure is a conceptual query with no shared vocabulary — that's where BM25 returns nothing and vectors save you.
> 🔑 *Rare exact token (slug, error code) pe vector fail karta hai — woh BM25 ka ghar hai.*

**Q3 (intermediate): How does BM25 actually score a document? Walk me through the intuition.**
> BM25 builds on TF-IDF with two key ideas. TF (term frequency): a document that contains the query word more often is more relevant — but with saturation, so the 10th occurrence adds far less than the 2nd (controlled by the `k1` parameter). IDF (inverse document frequency): rare words across the whole corpus are more informative than common ones, so "the" weighs almost nothing while "pgvector" weighs a lot. Plus length normalization (the `b` parameter): a long document naturally contains more words, so BM25 discounts it so long docs don't unfairly dominate. The score is the sum over query terms of IDF × saturated-TF × length-norm.
> 🔑 *BM25 = TF (saturating) × IDF (rare word zyada important) × length-normalize. Yahi teen ideas hain.*

**Q4 (deep): Vector search returns a cosine distance; BM25 returns an unbounded relevance score on a totally different scale. How do you combine two ranked lists that aren't comparable?**
> You don't combine the raw scores — that's the classic trap, because BM25 scores and cosine similarities live on incompatible scales and one would silently dominate. The clean answer is **Reciprocal Rank Fusion (RRF)**: you throw away the raw scores entirely and use only the *rank position* in each list. For each document, score = Σ over each retriever of 1/(k + rank), where k is a small constant (60 is the standard). A doc that ranks #1 in BM25 and #3 in vector gets a high combined score; a doc that only appears low in one list gets little. Because it's rank-based, it's scale-independent and needs no per-query normalization — that's why it's the production default. The alternative is weighted score fusion (normalize each score to 0–1, then `α·vector + (1−α)·bm25`), which lets you tune the blend but requires careful normalization and is more brittle across query types.
> 🔑 *RRF: raw score bhool jao, sirf RANK use karo → 1/(k+rank), k=60. Scale ka problem hi khatam. Weighted fusion = doosra option par normalize karna padta hai.*

**Q5 (system-design): If you were scaling McpIndex to 10 million servers, how would the hybrid retrieval change?**
> Three changes. (1) The vector index: at 1.5k rows pgvector doesn't even need an index, but at 10M I'd move to an HNSW index for high-recall ANN, accepting the higher build time and memory. (2) The fusion stage: I'd retrieve top-k from each retriever (say top-100 each), RRF-fuse them, then add a **cross-encoder reranker** (like bge-reranker) over the top ~50 fused results — at scale the reranker is what buys you precision because RRF is coarse. (3) Cost/latency: cache embeddings for repeated queries (the audit on my own code flagged that every search hits Gemini — at 10M scale that's the cost killer), pre-compute a `similar_slugs` column at ingest instead of embedding on every detail-page view, and add edge rate-limiting. So the shape becomes: hybrid retrieve → RRF fuse → rerank → quality-score blend.
> 🔑 *Scale pe: HNSW index + RRF + cross-encoder reranker + embedding cache. Retrieve→fuse→rerank→quality ka pipeline ban jaata hai.*

**Q6 (curveball): Your search returns the right server but it's ranked 4th, not 1st. How do you debug a relevance regression?**
> First I separate the two retrievers — query BM25-only and vector-only and see where the doc ranks in each. If it ranks #1 in vector but #20 in BM25, the doc is semantically right but lexically poor (maybe sparse description), so the fusion is being dragged down by BM25 — I might re-weight or enrich the indexed text. Then I check the fusion: is `k` in RRF too high (flattening rank differences)? Then the quality-score blend: in McpIndex final ranking isn't pure relevance — I blend the 6-dim quality score, so a slightly-less-relevant but much-higher-quality server can legitimately outrank. I'd confirm whether the "wrong" ranking is actually the quality blend doing its job. Build offline eval with labeled query→server pairs and track NDCG/MRR so this is measured, not vibes.
> 🔑 *Debug = dono retrievers alag-alag dekho, fir fusion k, fir quality-blend. Aur offline eval (NDCG/MRR) banao taaki guess na karna pade.*

**Traps / kya NA bolna:**
- ❌ "I just added the BM25 and vector scores together." → instant red flag; scales aren't comparable. Say RRF (rank-based) or normalized weighted fusion.
- ❌ Calling BM25 "just keyword matching." It's a *ranking function* with TF saturation + IDF + length-norm — show you know the mechanism.
- ❌ Claiming hybrid is always better. Be honest: for pure-keyword queries BM25 alone can win; hybrid's value is robustness across query types.
- ❌ Saying "embeddings understand the query." They encode distributional meaning, not understanding — careful, precise language reads as senior.

**Follow-up rabbit holes:**
- "What's `k` in RRF and why 60?" → empirical default; dampens the dominance of rank-1 so lower ranks still contribute.
- "Weighted fusion vs RRF — when pick which?" → weighted when you have a tuned α and consistent score normalization; RRF when you want robust, tuning-free fusion across heterogeneous retrievers.
- "Where does reranking fit?" → after fusion, over a small candidate set; cross-encoder is expensive so you only run it on top-N.
- "How would you evaluate retrieval quality?" → NDCG@k, MRR, Recall@k on a labeled set; A/B on click-through in prod.

---

### pgvector — what it is, index types (HNSW / IVFFlat)

**Kya hai (Hinglish):** `pgvector` ek Postgres extension hai jo database ko ek naya column type deta hai — `vector` — jisme aap embeddings (floats ka array, jaise 768 ya 1536 dimensions) store kar sakte ho, aur "in do vectors ke beech distance kitna hai" wali query Postgres ke andar hi chala sakte ho. Iska bada faida: aapko alag se ek vector database (Pinecone, Weaviate) nahi chahiye — aapka relational data aur vectors ek hi DB mein rehte hain, ek hi SQL query mein keyword filter + vector search dono ho jaate hain. McpIndex mein bilkul yahi hua: Neon Postgres + pgvector, koi separate vector store nahi.

Distance operators teen hote hain: `<->` (L2/Euclidean), `<#>` (negative inner product), `<=>` (cosine). Embeddings ke liye aksar cosine (`<=>`) use hota hai kyunki magnitude se zyada direction matter karta hai.

**Index types — yeh interview ka favourite:**
- **Exact (no index):** chhote data pe (jaise McpIndex ka 1,532 rows) Postgres bas saare vectors scan kar leta hai — 100% accurate, aur itne chhote scale pe fast bhi. Index ki zaroorat hi nahi padti.
- **IVFFlat:** data ko k-means se clusters (lists) mein baant deta hai; query pe sirf kuch nazdeeki clusters scan karta hai. Build fast, memory kam — par accuracy clusters ki quality pe depend karti hai, aur isko data load hone ke *baad* banana padta hai (k-means ko data chahiye). Naya data aane pe periodically rebuild karna padta hai.
- **HNSW:** ek multi-layer graph banata hai jisme "navigable small world" property hoti hai — search graph ke through hop karta hai. Sabse acchi accuracy + speed, par build slow aur RAM zyada (2–5x). Writes ko gracefully handle karta hai, khaali table pe bhi ban jaata hai. **2026 ka default choice 1M rows tak.**

**Aapke project se connection:** McpIndex 1,532 servers pe chalti hai — yeh itna chhota hai ki pgvector ko ANN index ki zaroorat hi nahi; exact cosine scan kaafi hai aur 100% recall deta hai. Real code mein vector search `searchServersBySimilarity` se hota hai jo Gemini se query embedding banake `<=>` cosine se nearest servers nikaalta hai. Yeh ek **strong honest point** hai interview mein: "I chose exact search because at 1.5k rows an HNSW index would add complexity and memory for zero recall benefit — I'd switch to HNSW past ~100k rows."

**Interview Q&A:**

**Q1 (basic): What is pgvector and why did you use it over a dedicated vector DB like Pinecone?**
> pgvector is a Postgres extension that adds a `vector` column type and distance operators, so I can store embeddings and run similarity search inside Postgres itself. I chose it over Pinecone because McpIndex already needed a relational database for the server metadata, categories, and quality scores — pgvector lets me keep everything in one Neon Postgres instance and do filtered vector search in a single SQL query (e.g. `WHERE category = $1 ORDER BY embedding <=> $2`). No second system to sync, no extra cost, and it's plenty fast at my scale.
> 🔑 *pgvector = Postgres ke andar hi vector search. Ek hi DB mein metadata + vectors, no Pinecone, no sync headache.*

**Q2 (intermediate): What are the index types in pgvector and what's the tradeoff?**
> Three options. No index — exact brute-force scan, 100% recall, fine for small tables. IVFFlat — clusters vectors with k-means and only scans the nearest clusters; fast to build, low memory, but lower recall and it needs the data present at build time plus periodic rebuilds. HNSW — a layered proximity graph; best recall-vs-speed, handles writes well, builds on an empty table, but slow build and 2–5x memory. The tradeoff is build-time/memory vs query recall/speed. HNSW is the safe modern default under ~1M rows; IVFFlat is the memory-frugal choice at very large scale where you can afford rebuilds.
> 🔑 *No-index (exact, chhota data) → IVFFlat (memory kam, rebuild chahiye) → HNSW (best, par RAM zyada). Default HNSW.*

**Q3 (intermediate→deep): McpIndex has only 1,532 servers. Did you even use an index, and why?**
> No — at 1,532 rows I used exact search, no ANN index. An HNSW index would cost build time and 2–5x memory to approximate something Postgres does exactly and fast at this scale, with zero recall benefit. ANN indexes only pay off when a full scan gets too slow — roughly tens of thousands to millions of rows. I'd add HNSW around 100k+ rows. Picking exact here was a deliberate "right tool for the scale" call, not laziness.
> 🔑 *1.5k rows pe exact scan hi best — index lagana over-engineering hota. HNSW ~100k+ pe.*

**Q4 (deep): How do HNSW's tuning parameters affect recall and latency?**
> Build-time: `m` is the number of bidirectional links per node — higher `m` means a denser graph, better recall, more memory and slower build. `ef_construction` is the candidate-list size during build — higher means a better-quality graph but slower build. Query-time: `ef_search` (`hnsw.ef_search`) is the candidate-list size during search — raise it for higher recall at the cost of latency. So recall is dialed mostly by `m`/`ef_construction` at build and `ef_search` at query. The honest part: I didn't tune these on McpIndex because exact search needed no index — but I know that's the lever set when I scale.
> 🔑 *HNSW knobs: build = m + ef_construction; query = ef_search. Recall chahiye to ef_search badhao (latency badhegi).*

**Q5 (system-design): A vector column is 768 floats × 1,532 rows. What about at 10M rows — storage, index, latency?**
> 768 dims × 4 bytes ≈ 3KB per vector; 10M rows ≈ 30GB of raw vectors plus the HNSW graph overhead (often larger than the vectors themselves). At that point: build an HNSW index, watch `maintenance_work_mem` during build, consider half-precision or quantization to cut memory, and possibly partition. Filtered search (`WHERE category=...`) interacts with ANN indexes tricky — you may need partial indexes per category or post-filtering. I'd also separate the embedding model's dimensionality decision: smaller dims (e.g. 256–512 via Matryoshka embeddings) trade a little accuracy for big storage/latency wins at scale.
> 🔑 *10M pe: HNSW index, memory budget dekho, quantization/Matryoshka se dims chhote karo, filtered-search ka ANN interaction handle karo.*

**Traps / kya NA bolna:**
- ❌ "pgvector is a vector database." It's a Postgres *extension* — precision matters.
- ❌ Saying you used HNSW when you didn't. The strong answer is *why exact search was correct at 1.5k rows.* Honesty + reasoning beats name-dropping an index you never configured.
- ❌ Confusing the distance operators. Cosine = `<=>`, L2 = `<->`, inner product = `<#>`.
- ❌ "IVFFlat is always faster than HNSW." IVFFlat builds faster but generally has *lower* query recall; HNSW usually wins on recall-vs-latency.

**Follow-up rabbit holes:**
- "Why cosine not L2 for embeddings?" → embeddings care about direction/semantic angle, not magnitude; many models output normalized vectors where cosine and dot-product align.
- "How does filtered vector search behave with an ANN index?" → pre-filter vs post-filter; ANN + WHERE can under-return, may need partial indexes.
- "What's `lists`/`probes` in IVFFlat?" → `lists` = number of clusters at build; `probes` = clusters scanned at query (recall vs speed knob).
- "Embedding dimensionality choice?" → tradeoff of accuracy vs storage/latency; Matryoshka lets you truncate.

---

### MCP servers — what they are (and why GenAI interviewers care)

**Kya hai (Hinglish):** **MCP = Model Context Protocol** — Anthropic ka introduce kiya hua ek open standard (late 2024) jo LLMs ko external tools, data sources, aur APIs se connect karne ka *ek standard tareeka* deta hai. Pehle har AI app apne-apne tareeke se tools wire karti thi (custom glue code har integration ke liye). MCP isko standardize kar deta hai: ek **MCP server** ek tool/data-source ko ek standard interface ke peeche expose karta hai (tools, resources, prompts), aur koi bhi **MCP client** (Claude Desktop, Cursor, ya aapka apna agent) usse plug-and-play connect kar sakta hai. Ise socho "USB-C for AI tools" — ek hi port, har device chalega.

Teen primitives yaad rakhna: **Tools** (functions LLM call kar sakta hai — e.g. "run a SQL query"), **Resources** (data LLM padh sakta hai — e.g. files, DB rows), **Prompts** (reusable prompt templates). Transport JSON-RPC pe chalta hai (stdio local, ya HTTP/SSE remote).

**Aapke project se connection:** McpIndex *MCP servers ka search engine* hai — 1,532 servers GitHub se scrape (`scripts/scrape-github.ts`) karke index kiye, taaki developers easily woh server dhoond sakein jo unhe chahiye (e.g. "Postgres MCP server" ya "GitHub MCP server"). Yeh khud-ba-khud aapko GenAI-roles ke liye relevant banata hai: aap MCP ecosystem ko itna samajhte ho ki uska discovery layer hi bana diya. Aur Jarvis project mein aap MCP servers *consume* bhi karte ho (Composio, Chrome DevTools, filesystem, memory MCPs) — to aap dono side jaante ho: producer-discovery aur consumer.

**Interview Q&A:**

**Q1 (basic): What is MCP and what problem does it solve?**
> MCP — Model Context Protocol — is an open standard from Anthropic for connecting LLMs to external tools and data. Before MCP, every AI app wrote bespoke glue for each integration, an N×M problem. MCP makes it a standard interface: a tool exposes itself as an MCP server, and any MCP-compatible client connects to it the same way. It's often described as "USB-C for AI" — one protocol, many tools. It matters because it turns agent tooling from custom code into a composable ecosystem.
> 🔑 *MCP = LLM-to-tools ka standard protocol. "USB-C for AI." N×M glue problem solve karta hai.*

**Q2 (intermediate): What are the core primitives an MCP server exposes?**
> Three. Tools — callable functions the model can invoke, like "query this database" or "create a GitHub issue," each with a typed input schema. Resources — readable data the model can pull as context, like files or records. Prompts — reusable, parameterized prompt templates the server offers. The client discovers these at connection time, and the host LLM decides when to call a tool. Communication is JSON-RPC, over stdio for local servers or HTTP/SSE for remote ones.
> 🔑 *Teen primitives: Tools (call karo), Resources (padho), Prompts (template). JSON-RPC pe baat hoti hai.*

**Q3 (intermediate→project): Why build a search engine for MCP servers — what's the user problem?**
> The MCP ecosystem exploded fast — thousands of community servers on GitHub, but no good way to discover the right one. If a developer wants "a server that talks to Stripe" or "something for vector search," they're stuck grepping GitHub. McpIndex scrapes and indexes them, scores their quality, and gives semantic + keyword search — so discovery is one query instead of an afternoon of digging. It's a developer-tools play: reduce time-to-find for a fast-growing, fragmented ecosystem.
> 🔑 *Problem = MCP servers bahut, discovery ka koi tareeka nahi. McpIndex = ek search box, woh sab solve.*

**Q4 (deep / GenAI-role connect): How does MCP relate to function calling / tool use? Aren't they the same?**
> They're complementary layers. Function calling / tool use is the *model capability* — the LLM emitting a structured request to call a function with arguments. MCP is the *transport and packaging standard* around that — how a tool advertises its schema, how a client discovers it, how the call and result move over JSON-RPC, regardless of which model. So MCP standardizes the plumbing so the same tool server works across Claude, and any MCP-aware host, without rewriting per-model tool definitions. Function calling is "the model can ask to call X"; MCP is "here's the universal way X describes itself and connects."
> 🔑 *Function calling = model ki capability (tool call karna). MCP = uske around standard plumbing. Complementary hain, same nahi.*

**Q5 (curveball): What are the security risks of MCP servers, and did that show up in McpIndex?**
> MCP introduces real attack surface: a malicious or compromised server can do tool poisoning (a tool description that manipulates the model), exfiltrate data the agent has access to, or perform prompt injection through resource content. For a *discovery* platform like McpIndex, the relevant angle is that I'm ingesting untrusted GitHub content (descriptions, READMEs) — so I render everything as escaped React children, never `dangerouslySetInnerHTML`, and the scraper is an offline script that never fetches arbitrary user URLs (no SSRF). My own security audit of McpIndex confirmed no XSS sinks and parameterized SQL throughout; the real live gap was cost-abuse on the unauthenticated search endpoint, not injection.
> 🔑 *MCP risks = tool poisoning, prompt injection, data exfil. McpIndex untrusted GitHub content ingest karta hai → sab escaped React, no innerHTML, offline scraper. Audit clean tha injection pe.*

**Traps / kya NA bolna:**
- ❌ "MCP is an Anthropic-only thing." It's an *open* standard with broad adoption — say open standard.
- ❌ Confusing MCP server (exposes tools) with MCP client/host (the LLM app consuming them). Be crisp on direction.
- ❌ Saying MCP *replaces* function calling. It standardizes/packages it.
- ❌ Don't fabricate adoption numbers; say "thousands of community servers" not a fake exact count.

**Follow-up rabbit holes:**
- "stdio vs HTTP/SSE transport — when each?" → stdio for local trusted servers, HTTP/SSE for remote/hosted.
- "How does a client discover tools?" → `list_tools` / `list_resources` handshake at connect.
- "Have you written an MCP server?" → tie to consuming MCPs in Jarvis (Composio, filesystem, memory) + indexing them in McpIndex.
- "Tool poisoning defenses?" → human-in-loop for sensitive tools, allowlist trusted servers, sanitize tool descriptions.

---

### Gemini Flash — how the LLM is actually used (embeddings + scoring)

**Kya hai (Hinglish):** McpIndex mein Gemini do alag kaam karta hai, dono ko alag rakhna interview mein important hai:
1. **Embeddings (retrieval ke liye):** har server ki description ko Gemini ke embedding model se ek vector mein badalte hain (ingest time pe), aur query ko bhi search time pe (`generateEmbedding` → Gemini `embedContent` in `src/lib/embeddings.ts`). Yeh vectors pgvector mein store/compare hote hain. **Yeh Gemini Flash (chat model) nahi hai — yeh embedding model hai.** Yeh distinction interviewer ko pasand aayega.
2. **Quality scoring (LLM-as-judge):** Gemini Flash (fast, sasta generative model) ko har server ki metadata di jaati hai aur woh 6 dimensions pe quality score generate karta hai. Yeh ingest-time pe ek baar hota hai (per server), runtime pe nahi — isliye sasta aur scalable.

Flash isliye choose kiya kyunki yeh fast + cheap hai — scoring 1,532 servers ke liye aur high-volume embedding ke liye, sabse mehenga (Pro) model use karna paisa jalaana hota.

**Aapke project se connection:** Real code: `src/lib/embeddings.ts` ka `generateEmbedding()` Gemini `embedContent` call karta hai — yeh search ka dil hai. Security audit ne pakda ki yeh **har search pe** fire hota hai (no cache, no rate-limit) — to aap yeh bhi jaante ho ki cost-wise yeh path optimize karna padega (cache embeddings, pre-compute popular queries). Quality scores `score_dimensions` column mein store hote hain (`dbRowToSummary` in `data.ts` usse parse karta hai) — yani scoring offline/ingest-time hai, jo correct design hai.

**Interview Q&A:**

**Q1 (basic): Where does Gemini fit in McpIndex?**
> Two distinct roles. First, embeddings: I use Gemini's embedding model to turn each server's description into a vector at ingest time, and the user's query into a vector at search time — those feed pgvector's semantic search. Second, quality scoring: I use Gemini Flash as an LLM-judge to score each server across six quality dimensions, run once per server at ingest. So Gemini powers both the semantic-retrieval signal and the quality signal, but at different times — embeddings on every query, scoring offline.
> 🔑 *Gemini do role: embeddings (retrieval) + Flash as judge (6-dim scoring). Embedding query-time, scoring ingest-time.*

**Q2 (intermediate): Why Gemini Flash specifically and not a bigger model?**
> Cost and latency. Flash is the fast, cheap tier — for scoring 1,532 servers and for query-time embedding, I don't need frontier reasoning, I need throughput at low cost. Quality scoring is a structured, well-scoped task that a fast model handles fine with a good rubric prompt. Spending Pro-tier money per server or per search would burn budget for no quality gain. It's a deliberate cost/quality tradeoff for a high-volume, bounded task.
> 🔑 *Flash = sasta + fast. High-volume bounded task ke liye Pro waste hai. Cost/quality tradeoff.*

**Q3 (intermediate→deep): Embeddings run on every search query. What's the cost/latency risk and how would you fix it?**
> That's exactly the gap my own audit flagged. Every `/api/search?q=` immediately calls Gemini `embedContent` before any caching — so unique queries each cost a billing event and add ~200ms latency, and an attacker could loop unique queries to rack up cost (an LLM-DoS / unrestricted-resource-consumption issue). Fixes: cache the *embedding* keyed by normalized query text (LRU + a short DB cache) so popular queries don't re-embed; pre-compute embeddings for a dictionary of common queries; add a max query-length cap before embedding; and edge rate-limiting per IP. Also stop embedding on the server-detail page for "similar servers" — pre-compute a similar-slugs column at ingest instead.
> 🔑 *Har search pe Gemini call = paisa + latency + DoS risk. Fix: embedding cache (normalized query), length-cap, rate-limit, pre-compute popular + similar.*

**Q4 (deep): How do you keep an LLM-as-judge quality score consistent and trustworthy across 1,532 servers?**
> A few disciplines. Use a fixed, explicit rubric in the prompt with anchored definitions for each dimension and each score band so the model isn't inventing the scale per call. Request structured output (JSON with one numeric field per dimension) so it's parseable — in my code the result lands in a `score_dimensions` JSON column. Use a low temperature for determinism. Spot-check a sample against my own judgment to validate calibration, and re-score if I change the rubric. The honest caveat I'd give: LLM-judges have known biases (length bias, position bias), so the scores are a useful relevance/quality signal, not ground truth — I treat them as one ranking input alongside retrieval relevance, not the sole arbiter.
> 🔑 *LLM-judge consistent rakho: fixed anchored rubric + structured JSON output + low temp + spot-check. Aur maano ki yeh signal hai, gospel nahi (length/position bias hota hai).*

**Q5 (curveball): If Gemini is down or rate-limited at search time, what happens to McpIndex?**
> The system degrades gracefully to keyword-only. The code has a `keywordFallback()` path (Postgres text search over name/description) — if the embedding call fails, I can serve lexical results instead of erroring the whole search. That's actually a hybrid-search safety bonus: because I have both retrievers, losing the semantic one doesn't kill search, it just narrows it. My audit even recommended a `SEARCH_DISABLED` flag to force keyword-only mode as an emergency cost cutoff. So the answer is: BM25/keyword keeps the search alive.
> 🔑 *Gemini down? Keyword fallback (keywordFallback) chala do — hybrid hone ka bonus, search marta nahi. Emergency flag bhi rakha.*

**Traps / kya NA bolna:**
- ❌ Calling the embedding model "Gemini Flash." Embeddings come from Gemini's *embedding* model; Flash is the generative model used for scoring. Mixing them looks sloppy.
- ❌ Saying scoring runs on every search. It's ingest-time, once per server — that's the cost-correct design; say so.
- ❌ Claiming the quality score is objective truth. Acknowledge LLM-judge bias.
- ❌ Don't say "I fine-tuned Gemini." You used it off-the-shelf via API with prompting — that's the truth and it's fine.

**Follow-up rabbit holes:**
- "How do you handle embedding model version changes?" → re-embed the whole corpus on model change; embeddings from different models aren't comparable.
- "Embedding dimensionality / normalization?" → match the model's output dims to the `vector(n)` column; normalize if using cosine.
- "Structured output reliability?" → JSON mode / schema; guard the parse (my audit flagged an unguarded `JSON.parse` on `score_dimensions`).
- "LLM-judge eval?" → correlate against human labels, measure agreement (Cohen's κ), watch for bias.

---

### The 6-dimensional quality-scoring pipeline (design)

**Kya hai (Hinglish):** Search sirf "relevant" results dena kaafi nahi — McpIndex har server ko ek **quality score** bhi deta hai, taaki ek relevant-but-abandoned server, ek relevant-and-well-maintained server se neeche rahe. Yeh score 6 alag dimensions pe banta hai (composite), ek nahi — kyunki "quality" multi-faceted hai. Ek single number sab kuch chhupa deta; 6 dimensions transparent banate hain ki score kyun aaya. Yeh scoring **ingest pipeline** mein hota hai (`scripts/scrape-github.ts` → score → DB), runtime pe nahi. Result `score_dimensions` JSON column mein store hota hai.

Plausible 6 dimensions (GitHub se signals + LLM judgment): **(1) Documentation quality** (README completeness — LLM judge), **(2) Maintenance/recency** (last commit, release cadence — GitHub metadata), **(3) Popularity** (stars/forks — GitHub), **(4) Code/implementation quality** (tests, structure — LLM judge), **(5) Completeness of MCP spec** (kitne tools/resources/prompts properly expose karta hai), **(6) Trust/security signals** (license present, owner reputation, no obvious red flags). Final ranking = retrieval relevance blended with this composite.

**Aapke project se connection:** Real code mein `score_dimensions` ek JSON column hai jise `dbRowToSummary` (`data.ts`) parse karta hai — to multi-dimension design literally schema mein hai, ek aggregate number nahi. Scoring ingest-time hai (audit ne confirm kiya scoring runtime pe nahi chalta), jo cost-correct hai. Aap honestly bol sakte ho ki kuch dimensions deterministic GitHub-metadata se aate hain (stars, last-commit) aur kuch LLM-judge se (docs, code quality) — yeh hybrid scoring design senior-level lagta hai.

**Interview Q&A:**

**Q1 (basic): Why score quality separately from relevance? Isn't relevance enough?**
> Relevance answers "does this match the query"; quality answers "is this actually worth using." A dead, undocumented server can be highly relevant to a query and still be a bad result. So I compute a quality score and blend it into ranking — a slightly-less-relevant but well-maintained, well-documented server can outrank a perfect-keyword-match that's abandoned. For a developer-tools discovery product, surfacing *good* tools is the whole value.
> 🔑 *Relevance = "match karta hai?", quality = "use karne layak hai?". Dono chahiye, warna dead server top pe aa jaata.*

**Q2 (intermediate): Why six dimensions instead of one quality number?**
> Two reasons: accuracy and transparency. Quality is multi-faceted — docs, maintenance, popularity, code quality, spec-completeness, trust — collapsing them into one number hides *why* a server scored high or low and makes it impossible to debug or let users sort by what they care about. Six dimensions let me weight them deliberately into a composite and show the breakdown. In the schema it's a `score_dimensions` JSON column, not a single float, exactly so the components are preserved.
> 🔑 *6 dim kyun: transparency (kyun score aaya pata chale) + tunable weighting. Single number sab chhupa deta.*

**Q3 (intermediate→deep): How do you combine GitHub metadata signals with LLM-judged signals into one score?**
> I separate signal types. Deterministic, cheap signals come straight from GitHub metadata — stars, forks, last-commit recency, release cadence, license presence — and get normalized (e.g. log-scale stars, recency decay). Subjective signals — documentation quality, code/implementation quality, MCP-spec completeness — go to the LLM judge with an anchored rubric returning a 0–N score per dimension. Then each dimension is normalized to a common scale and combined with weights into a composite. Keeping metadata-based dimensions deterministic means most of the score is reproducible and cheap; the LLM only judges what genuinely needs judgment.
> 🔑 *Deterministic GitHub signals (stars, recency — normalize) + LLM-judge subjective signals (docs, code) → normalize → weighted composite. LLM sirf jahan judgment chahiye.*

**Q4 (system-design): How do you keep scores fresh as servers get updated, and how do you avoid re-scoring everything constantly?**
> Scoring is an ingest-time batch, not runtime — so I re-run it on a schedule (the scraper re-crawls GitHub). To avoid wasteful re-scoring: the metadata dimensions (stars/recency) are cheap to refresh every crawl, but the expensive LLM-judged dimensions only need re-running when the underlying content changed — I'd key the LLM-score on a content hash of the README/description, so unchanged servers skip the LLM call. That keeps the popularity/recency parts always-fresh while only paying for LLM scoring when docs actually change. Store a `scored_at` timestamp and re-score on a TTL or on detected change.
> 🔑 *Scoring batch/ingest-time hai. Cheap metadata har crawl refresh, mehengi LLM-score sirf jab content-hash badle. scored_at + TTL.*

**Q5 (curveball): An author games the score by adding 50 fake stars and keyword-stuffing the README. How robust is your pipeline?**
> Good adversarial question. Single-signal gaming is exactly why six dimensions help — stars alone can't dominate. Keyword-stuffing the README inflates lexical relevance but the LLM-judged documentation-quality dimension can detect low-substance stuffing, and code-quality/spec-completeness can't be faked by a README edit (they need real tools/tests). Defenses I'd add: log-scale and cap the popularity contribution so a burst of stars has diminishing effect, weight harder-to-fake dimensions (spec-completeness, actual tool count) higher, and flag sudden metric jumps. No score is unspoofable, but a multi-dimensional composite with most weight on hard-to-fake signals raises the cost of gaming a lot.
> 🔑 *Multi-dim isliye anti-gaming hai — ek signal dominate nahi karta. Stars cap/log-scale karo, hard-to-fake dimensions (spec-completeness, tool count) ko zyada weight do.*

**Traps / kya NA bolna:**
- ❌ Listing six dimensions you can't justify. Have a reason for each; "documentation, maintenance, popularity, code quality, spec-completeness, trust" each maps to a real signal.
- ❌ Saying every dimension is LLM-judged. The strong design is hybrid: cheap deterministic GitHub signals + LLM only where judgment is needed.
- ❌ Claiming scoring runs at query time. It's ingest-time batch — cost-correct, say so.
- ❌ Treating the composite as objective truth — acknowledge weighting is a product decision and LLM dimensions carry bias.

**Follow-up rabbit holes:**
- "How do you weight the six?" → product decision; start equal, tune by eyeballing top results / user feedback.
- "How do you normalize across dimensions?" → min-max or z-score to a common scale before weighting; log-scale skewed signals like stars.
- "How is the composite used in ranking?" → blended with retrieval relevance (e.g. relevance gates candidates, quality re-orders within band) — and yes, this is why a "wrong" rank can be correct (ties back to the hybrid-search debug question).
- "Did you validate the scores?" → spot-check against human judgment; the honest answer is partial validation given the 2-day build.

---

## Cross-cutting "tell me about this project" master narrative

If asked to *just talk about McpIndex*, deliver this arc:
1. **Problem:** MCP ecosystem exploded, thousands of servers on GitHub, no good discovery.
2. **Solution:** scraped 1,532 servers, indexed them with **hybrid search** (BM25 lexical + pgvector semantic) so both exact tokens and conceptual queries work.
3. **Quality layer:** a **6-dimensional automated quality score** (deterministic GitHub signals + Gemini Flash LLM-judge) so results are ranked by quality, not just relevance.
4. **Stack/speed:** Next.js 16 + Neon Postgres + pgvector + Gemini, all one DB, no separate vector store — **shipped in 2 days, live on Vercel.**
5. **Engineering maturity:** I even ran a security audit on my own code — found the live gap was unauthenticated paid-endpoint cost-abuse (LLM-DoS), not injection, and designed the fixes (embedding cache, rate-limit, keyword fallback for graceful degradation).

🔑 *Master narrative: problem → hybrid search → quality score → 2-din stack → "maine apna hi audit kiya." Yeh aakhri point seniority dikhata hai.*

---

## What makes this answer set "shipped it, not textbook"
- You ran your own **security audit** and know the *live* failure mode (Gemini cost-abuse on unauthenticated `/api/search`), not a hypothetical.
- You chose **exact search over an index** deliberately for 1,532 rows and can defend it.
- You separate **embedding model vs Flash generative model** correctly.
- You know scoring is **ingest-time batch**, hybrid deterministic + LLM-judge.
- You have a real **graceful-degradation** story (`keywordFallback`).
