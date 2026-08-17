# Interview Prep — Project 1: Jarvis (Multi-Agent AI Assistant + RAG Pipeline)

> **Stack grounded in real code:** Python · FastAPI · Claude Agent SDK · ChromaDB · sentence-transformers (`all-MiniLM-L6-v2`) · asyncio · Pydantic v2 · pytest · systemd.
> Files this doc is grounded in: `jarvis_core/recall.py`, `critic.py`, `confidence.py`, `intent.py`, `daemon.py`, `orchestrator.py`, `scripts/episodic_memory.py`, `specs/recall.spec.md`, `specs/critic.spec.md`.
>
> **The one-line pitch (say this when they ask "tell me about Jarvis"):**
> *"Jarvis is a self-hosted personal AI agent built on the Claude Agent SDK. There's a long-running FastAPI daemon that, on every message, runs three layers around the model: an intent classifier, a RAG recall layer over a local ChromaDB vector store, and a self-critique loop that scores the draft on four rubrics and hedges unsourced claims before it ships. It also fans out parallel agent workers over asyncio for multi-domain tasks. 35+ pytest tests, JSONL observability on every layer, runs as hardened systemd services."*

---

## How the `/chat` pipeline actually works (memorize this — everything below hangs off it)

From `daemon.py:chat()`, every user message goes through **4 layers**:

1. **Intent** (`intent.py`) — one cheap Haiku call classifies the message into 8 categories + priority + confidence.
2. **Recall** (`recall.py`) — semantic search over ChromaDB; builds a `<jarvis_memory_context>` block.
   - *Key detail: intent + recall run **in parallel** — `intent` is an `asyncio.create_task`, recall runs via `asyncio.to_thread` (Chroma is sync), then `await`ed together.*
3. **Worker** (`orchestrator.py:run_worker`) — the augmented prompt (`<intent>` block + memory block + user message) goes to a Claude Code session via the Agent SDK.
4. **Critic** (`critic.py`) — silent reviewer scores the draft on 4 rubrics; revises **once** if needed; attaches a confidence tag.

🔑 *Yaad rakhna: intent + recall parallel chalte hain, fir worker, fir critic — yeh sequence interviewer ko pehle hi bata dena, baaki sab sawal isi ke around ghoomenge.*

---

## RAG / Retrieval-Augmented Generation

### What RAG is + why this project uses it
**Kya hai (Hinglish):** RAG ka matlab hai — LLM ko sirf apni training memory par chhodne ke bajaye, hum pehle ek knowledge base se relevant text dhoond ke laate hain aur usko prompt me daal dete hain. Isse model ko *current, personal* context milta hai jo uski training me tha hi nahi. Jarvis me yeh isliye zaroori hai kyunki Boss ke preferences, projects, log — yeh sab markdown files aur conversation logs me hain, model ke andar nahi. Bina recall ke har baat par Jarvis "goldfish" jaisa behave karta — har conversation bhool jaata.

**Aapke project se connection:** `recall.py:Recaller.gather()` har message par ChromaDB query karta hai (`scripts/episodic_memory.py:EpisodicMemory.recall()`), top-k chunks nikaalta hai, score-filter karta hai, token-budget tak trim karta hai, aur ek `<jarvis_memory_context>` XML block bana ke worker prompt me prepend kar deta hai. `specs/recall.spec.md` me likha hai: *"Without this layer ... Jarvis behaves like a goldfish in every conversation despite having 155+ indexed chunks."*

**Interview Q&A:**

**Q1 (basic): What is RAG and why not just fine-tune the model on your data?**
A: RAG retrieves relevant documents at query time and injects them into the prompt, so the model answers from fresh, external context instead of frozen weights. I chose RAG over fine-tuning for three reasons: my knowledge base changes constantly — new conversations, new project notes get added daily, and re-fine-tuning for every edit is absurd. Second, RAG gives me provenance — I tag every chunk with its source file, so I can trace why the model said something. Third, I'm on a hosted Claude model via the Agent SDK; I don't control the weights, so fine-tuning isn't even on the table. RAG is the right tool when your knowledge is dynamic and you need traceability.
🔑 *Fine-tune = knowledge weights me bake karna (mehnga, static); RAG = knowledge run-time pe inject karna (sasta, fresh, traceable).*

**Q2 (basic→intermediate): Walk me through your retrieval pipeline end to end.**
A: On ingestion, markdown files and conversation logs get chunked to roughly 500 tokens at heading and paragraph boundaries, embedded with `all-MiniLM-L6-v2`, and stored in ChromaDB with cosine space and source/section metadata. At query time, the user's message is embedded with the same model, I do a top-k=5 nearest-neighbour search, convert Chroma's cosine *distance* to a 0–1 similarity score, drop anything below 0.55, trim the survivors to a ~2000-token budget (lowest-score-first), and format them into an XML `<jarvis_memory_context>` block that gets prepended to the prompt. The whole thing has a kill-switch and fails open — if Chroma errors, I return an empty block and the model just answers without memory.
🔑 *Pipeline: chunk → embed → store; phir embed query → top-k → distance→similarity → threshold 0.55 → token-trim → XML block.*

**Q3 (intermediate): Why all-MiniLM-L6-v2 specifically? What are its tradeoffs?**
A: It's a 384-dimension sentence-transformer, about 80MB, that runs fully locally on CPU with no API key — which matters because the whole point of Jarvis is to be self-hosted and private; my memory never leaves the machine. It's fast enough for sub-second recall and its quality on short semantic-similarity tasks is strong for its size. The tradeoff is the 384-dim space and a 256-token input cap, so it's weaker on very long passages and nuanced multilingual content — and my notes are Hinglish, which is a known soft spot. If recall quality became the bottleneck I'd move up to `bge-base` or `e5-large`, or a hosted embedding model, but that's a cost/latency/privacy tradeoff I haven't needed to make. For a personal assistant where everything is local and free, MiniLM is the right default.
🔑 *MiniLM = chhota (80MB), local, free, fast — privacy + cost ke liye perfect; quality chahiye toh bge/e5 pe upgrade. Maine cheapest-that-works choose kiya.*

**Q4 (intermediate→deep): You filter at cosine similarity 0.55. How did you land on that number, and what breaks if it's wrong?**
A: 0.55 is a precision/recall knob. Too low and I stuff irrelevant chunks into the prompt — that's context pollution, it distracts the model and burns tokens. Too high and I starve it of genuinely relevant memory and it answers blind. I picked 0.55 empirically against eval cases in `data/evals/recall/` — for example "what is the airspeed of an unladen swallow" must return *nothing* (all scores below threshold), while "what does Boss prefer for communication" must surface the preferences chunk. One subtlety worth flagging: Chroma returns cosine *distance* 0–2, and I convert with `score = 1 - distance/2`, so the 0.55 is on the normalized 0–1 similarity, not raw distance — getting that conversion wrong would silently move the effective threshold. It's also env-overridable, so it's a tuning dial, not a magic constant.
🔑 *0.55 = signal-vs-noise dial; neeche = kachra prompt me, upar = relevant memory miss. Eval cases se calibrate kiya. Distance ko similarity me convert karke threshold lagaya.*

**Q5 (deep / system-design): Why ~500-token chunks? How does your chunking strategy avoid splitting meaning?**
A: Chunk size is a tradeoff between retrieval precision and context completeness. Tiny chunks retrieve precisely but fragment an idea across many hits; huge chunks keep ideas whole but dilute the embedding — one vector trying to represent five topics matches nothing well. ~500 tokens is a sweet spot: big enough to hold a coherent thought, small enough that the embedding stays focused. Crucially I don't blind-cut at 500 — I split on markdown heading and paragraph boundaries first, so each chunk is a semantically whole section; I only hard-split with a 100-character overlap when a single section runs long, and the overlap stops a sentence that straddles the cut from losing its context. Each chunk carries its source file and section heading as metadata, which gives me provenance for free.
🔑 *~500 token = idea poora aaye par embedding focused rahe. Heading/paragraph pe todta hoon (meaning-aware), lambe section pe 100-char overlap taaki sentence beech me na kate.*

**Q6 (curveball / gotcha): A user asks something your memory clearly contains, but recall returns nothing. How do you debug it?**
A: First I check the recall log — `data/logs/recall.jsonl` records `skipped_reason`, `top_score`, and `n_chunks` for every call, so I immediately know whether it was skipped (message under 30 chars, a slash command, or a pure greeting), whether the DB was empty, or whether hits existed but all fell below 0.55. If `top_score` was, say, 0.52, it's a threshold/embedding-quality issue — the query and the stored chunk are semantically close to a human but the embedding model under-scored them, often because the phrasing diverged. That's the classic vocabulary-mismatch failure of pure dense retrieval. The fix ladder: lower the threshold, or — the real fix — add hybrid search (BM25 keyword + dense vectors) so exact-term matches survive even when the embedding is lukewarm. If it was skipped wrongly, the skip heuristic is too aggressive and I tighten it.
🔑 *Pehle log dekho (skipped vs low-score). Agar score 0.52 hai toh dense-retrieval ka vocabulary-mismatch hai — hybrid search (BM25 + vector) is the proper fix.*

**Traps / kya NA bolna:**
- ❌ Don't say "RAG means the model searches the internet." That's web-search/tool-use, not RAG over your own corpus.
- ❌ Don't say cosine similarity and cosine distance are the same — Chroma gives distance, you convert. If you blur this you'll fail the follow-up.
- ❌ Don't claim you "trained the embedding model." You *used* a pretrained sentence-transformer. Be precise.
- ❌ Don't invent recall accuracy numbers. You have eval *cases* (pass/fail), not a published accuracy metric — say that honestly.

**Follow-up rabbit holes (where they'll drill next):**
- "What's the difference between HNSW and flat/IVF indexes?" → ChromaDB uses HNSW (the metadata sets `hnsw:space: cosine`); HNSW is an approximate graph index, fast at scale, slight recall tradeoff vs exact search.
- "How would you add re-ranking?" → A cross-encoder reranker (e.g. `bge-reranker`) over the top-k before injecting — retrieve 20, rerank, keep 5.
- "Chunk overlap — why 100 chars and not bigger?" → Bigger overlap = more duplicate content indexed = wasted storage + duplicate hits; 100 chars just bridges sentence boundaries.
- "How do you keep the index fresh?" → `scripts/incremental_memory_ingest.py` runs on a timer; SHA-256 content-hash dedup means re-ingesting an unchanged file adds nothing.

---

### Embeddings & Vector Databases (ChromaDB)
**Kya hai (Hinglish):** Embedding matlab text ko numbers ke vector me badalna, jaise har sentence ka ek "meaning coordinate" ban jaaye. Similar meaning waale vectors paas-paas hote hain. Vector DB (ChromaDB) in vectors ko store karta hai aur "is query ke sabse paas waale 5 vectors kaunse hain" yeh fast nikaal deta hai — yahi semantic search ki jaan hai.

**Aapke project se connection:** `episodic_memory.py` me `chromadb.PersistentClient` disk pe `data/memory/chroma/` me persist karta hai, collection `metadata={"hnsw:space": "cosine"}` se banta hai, aur embedding function `SentenceTransformerEmbeddingFunction(all-MiniLM-L6-v2)` hai. Dedup ke liye har doc ka ID `SHA-256(source||text)` hai.

**Interview Q&A:**

**Q1 (basic): What is a vector embedding?**
A: It's a fixed-length list of floats that encodes the *meaning* of a piece of text, produced by a neural model. Texts with similar meaning land close together in that vector space, which is what lets me do semantic search — match by meaning, not by keyword overlap. MiniLM gives me 384 dimensions per chunk.
🔑 *Embedding = text ka meaning numbers me; similar meaning = paas-paas vectors.*

**Q2 (intermediate): Why a dedicated vector DB instead of computing cosine similarity in a NumPy loop?**
A: For a few hundred chunks a brute-force NumPy scan works fine. But a vector DB gives me three things I'd otherwise have to build: persistence (Chroma stores to disk and survives restarts), an approximate-nearest-neighbour index (HNSW) so search stays fast as the corpus grows past brute-force territory, and metadata filtering — I can query "nearest chunks *where source = projects.md*". I also get atomic add/dedup. It's the difference between a script and a system.
🔑 *Vector DB = persistence + fast ANN index (HNSW) + metadata filter. NumPy loop chhote data pe chalega, scale pe nahi.*

**Q3 (deep): Explain how Chroma converts a query into ranked results in your code, including the score math.**
A: I call `collection.query(query_texts=[msg], n_results=k, include=[...distances])`. Chroma embeds the query with the same MiniLM function, runs HNSW nearest-neighbour search in cosine space, and returns documents plus cosine *distances*, where 0 is identical and 2 is opposite. My code converts to a 0–1 similarity with `score = 1 - distance/2`, then I sort and threshold on that. The reason I normalize is so my 0.55 threshold is intuitive and stable regardless of Chroma's internal distance convention.
🔑 *Chroma cosine distance deta hai (0=same, 2=ulta); main `1 - dist/2` se 0–1 similarity banata hoon, fir 0.55 pe threshold.*

**Q4 (curveball): Your dedup uses SHA-256 of source+text. What's the failure mode?**
A: It dedups *exact* duplicates only — a one-character edit produces a totally different hash, so a lightly-edited chunk gets re-indexed as a new entry, and now I have two near-identical chunks competing in retrieval. For my use case that's acceptable because `forget(source)` wipes a file's chunks before re-ingesting after edits. The "proper" dedup for near-duplicates would be semantic — cluster by embedding similarity — but that's overkill here and risks dropping legitimately distinct chunks.
🔑 *SHA-256 = sirf exact duplicate pakadta hai; thoda edit = naya hash = duplicate chunk. Edit ke baad `forget()` se purane chunks hata ke re-ingest karta hoon.*

**Traps / kya NA bolna:**
- ❌ Don't confuse embedding dimensions (384) with chunk token size (500). Different axes.
- ❌ Don't say "ChromaDB does the embedding by itself" — you *configured* it with a sentence-transformer embedding function; the model does the embedding.

**Follow-up rabbit holes:**
- "Cosine vs dot-product vs Euclidean — when which?" → Cosine ignores magnitude (good for normalized text embeddings); dot-product if vectors aren't normalized; Euclidean rarely for text.
- "How does HNSW work?" → Hierarchical navigable small-world graph; greedy graph traversal across layers, approximate but logarithmic-ish.
- "Multi-tenant memory?" → metadata `where` filter on user_id; spec notes `user_id` is reserved for future per-user partitioning.

---

## Multi-Agent Orchestration & asyncio Concurrency

### Parallel agent fan-out
**Kya hai (Hinglish):** Multi-agent ka matlab — ek bade kaam ko chhote independent sub-kaamo me todna aur har sub-kaam ek alag Claude worker ko dena, sab ek saath (parallel) chalana. asyncio Python ka concurrency tool hai jo I/O-bound kaam (jaise LLM API call jo network par wait karta hai) ke liye perfect hai — ek worker network ka jawab wait kar raha ho toh CPU dusre workers ko aage badha deta hai.

**Aapke project se connection:** `orchestrator.py:run_parallel_workers()` `asyncio.gather(*(_run_one(w) for w in workers))` use karta hai — N workers concurrently, har ek apni independent Claude session ke saath. `daemon.py` ka `/task` endpoint isko background me chalata hai. Aur `/chat` me intent + recall bhi parallel chalte hain.

**Interview Q&A:**

**Q1 (basic): What does "agentic" actually mean in this project? Be honest, not buzzwordy.**
A: Two concrete things. First, the workers aren't single prompt-response calls — they're Claude Code sessions with tool access (file ops, the specialist sub-agents, MCP servers) running a multi-turn loop with `max_turns`, so they can decide *to read a file, then act*. That decision-loop is the "agent" part. Second, on the `/task` path I decompose a job into sub-tasks, dispatch them to independent workers in parallel, then optionally run an aggregator agent that synthesizes their outputs. So "agentic" here = tool-using, multi-turn, decomposable — not just "I called an LLM." I'd push back on calling a plain one-shot completion "agentic."
🔑 *Agentic = tool-using + multi-turn + decompose-and-aggregate; sirf ek LLM call ko agentic mat bolo — yeh distinction interviewer ko impress karta hai.*

**Q2 (intermediate): Why asyncio for the fan-out and not threads or multiprocessing?**
A: Because the work is I/O-bound, not CPU-bound. Each worker mostly *waits* on the Claude API over the network — there's almost no local computation. asyncio lets one event loop juggle dozens of in-flight awaits cheaply, with no thread-stack overhead and no GIL contention. Threads would also work for I/O but cost more memory and add lock complexity; multiprocessing is for CPU-bound parallelism and would be pure waste here. `asyncio.gather` was the natural fit: fire all worker coroutines, total wall-clock equals the slowest worker, not the sum.
🔑 *LLM calls I/O-bound hain (network wait), CPU-bound nahi — isliye asyncio. gather se wall-clock = sabse slow worker, not sum.*

**Q3 (intermediate): In `/chat` you run intent and recall "in parallel" but you `await` recall before intent. Explain that honestly.**
A: They genuinely overlap, but the mechanics differ because recall is synchronous (ChromaDB has no async API). I wrap intent as `asyncio.create_task` so it starts immediately, then run recall via `asyncio.to_thread` which offloads the blocking Chroma query to a thread pool — so while that thread does the vector search, the event loop is free and the intent task progresses. Then I `await` both. So the LLM classification call and the vector search are genuinely concurrent; I just await them in sequence in the code.
🔑 *Intent = create_task (turant start), recall = to_thread (blocking Chroma ko thread pe), dono overlap karte hain, fir dono await. Honest answer dena — yeh subtle hai.*

**Q4 (deep / system-design): One worker in a parallel fan-out hangs forever. What happens to the others and to the user?**
A: Two protections. Each `run_worker` is individually wrapped in `asyncio.wait_for(..., timeout)` — the collect coroutine is cancelled at the deadline and that worker returns a `WorkerOutcome` with an error string rather than hanging. Because every worker captures its own error instead of raising, `asyncio.gather` doesn't get a propagating exception that would cancel its siblings — the healthy workers still complete. So one slow/dead worker degrades to a labeled error in the aggregated output, not a total task failure. If I wanted hard isolation I could pass `return_exceptions=True` to gather, but I chose the catch-inside-worker pattern so partial results always survive.
🔑 *Har worker apna timeout + apna error catch karta hai, isliye ek worker marne se gather/baaki workers nahi marte — partial result hamesha bach jaata hai.*

**Q5 (curveball): asyncio.gather vs asyncio.as_completed — when would you switch?**
A: `gather` waits for everyone and returns results in input order — right when I need *all* outputs before the aggregation step, which is my case. `as_completed` yields results as each finishes, which I'd switch to if I wanted to stream partial results to the user live (e.g. show each research agent's finding the moment it lands) instead of waiting for the slowest. Given my `/task` flow ends in a synthesis step that needs all inputs, gather is correct; for a streaming Telegram UX, as_completed would be the move.
🔑 *gather = sabka wait karo, order me lo (aggregation ke liye); as_completed = jaise-jaise finish ho dikhao (live streaming ke liye).*

**Traps / kya NA bolna:**
- ❌ Don't say asyncio gives "true parallelism / uses all CPU cores." It's single-threaded concurrency — one core, cooperative scheduling. Multiprocessing is for cores.
- ❌ Don't say you used multiprocessing for the LLM workers. You didn't, and it'd be wrong for I/O-bound work.
- ❌ Don't call running a blocking sync function directly inside an async coroutine "fine" — it blocks the whole event loop; that's exactly why recall is wrapped in `to_thread`.

**Follow-up rabbit holes:**
- "What's the GIL and why doesn't it bite you here?" → GIL serializes Python bytecode; doesn't matter for I/O-bound waits since the lock is released during the wait.
- "How do you cap concurrency / avoid rate limits?" → A semaphore around the worker spawn; daemon has `JARVIS_GOAL_MAX_CONCURRENT`. Honest: chat fan-out itself isn't semaphore-capped yet — good "what I'd improve" answer.
- "Session isolation between parallel workers?" → Each worker is its own Claude session = independent context window, no cross-contamination.

---

## Self-Correction / LLM-as-Judge (the Critic loop)

### The four-rubric critique + bounded revision
**Kya hai (Hinglish):** Self-correction matlab — model ka jawab seedha bhejne ke bajaye, ek doosra (sasta) LLM us draft ko judge karta hai: kya yeh sahi sawal ka jawab hai? memory se contradict toh nahi? koi number bina source ke toh nahi bola? tone sahi hai? Agar problem mile toh ek baar revise karaata hai. Yeh "LLM-as-a-judge" pattern hai — quality gate har response par.

**Aapke project se connection:** `critic.py:Critic.evaluate()` ek Haiku call se draft ko **4 rubrics** par score karta hai — INTENT / MEMORY / CLAIMS / TONE (`_REVIEW_PROMPT_TEMPLATE` me likha hai). Verdict `revise` ho toh `_revise()` **exactly ek baar** chalta hai (recursion nahi). Phir `confidence.py:annotate()` se `verified`/`unverified`/`low` tag lagta hai — `verified` silent, baaki visible hedge. Spec: `specs/critic.spec.md`.

**Interview Q&A:**

**Q1 (basic): What problem does the critic solve?**
A: An LLM can confidently hallucinate, contradict context it was given, answer an adjacent question instead of mine, or drift into the wrong tone — and the user has to catch all of that manually. The critic automates that catch: it's a second-pass reviewer that scores the draft on four specific failure modes before it ships, and forces hedging on any claim that isn't sourced. It turns "trust me" into "checked."
🔑 *Critic = automated quality gate; hallucination/contradiction/intent-miss/tone ko user ke bajaye system pakadta hai.*

**Q2 (intermediate): Why a separate cheaper model (Haiku) as the judge instead of the same model?**
A: Cost and latency — it's an *extra* call on every substantive response, so I run it on Haiku-class which is cheap and fast, with an 8-second hard timeout. There's also a mild independence argument: a smaller model with a tight, rubric-scoped prompt is a decent cheap critic for structured checks like "is this number sourced" and "is the register respectful." It's not a heavyweight fact-checker — by design it doesn't hit the web — it's a fast guardrail. The spec even budgets it: about one extra call per chat, roughly $0.05/day at 50 chats.
🔑 *Judge = Haiku (sasta + fast) kyunki har response pe extra call hai; 8s timeout; web fact-check nahi karta, lightweight guardrail hai.*

**Q3 (deep / system-design): How do you guarantee the critic loop never runs forever?**
A: By construction, not by hoping. The flow is review → at most one revise → done. After the single `_revise()` call I never re-submit the revised text to the critic — there's no loop back. The spec states it explicitly: "cap revision at exactly ONE pass — never recurse." So the worst case is exactly two extra LLM calls (one review + one revise), bounded. On top of that, each call has its own `asyncio.wait_for` timeout, and the entire critic pipeline is wrapped in try/except in the daemon so even a crash just ships the original reply. Bounded passes + per-call timeouts + fail-open = no runaway.
🔑 *Loop nahi hai — review + at-most-one revise, bas. Recursion banned by design; har call pe timeout; crash pe original ship. Worst case = 2 extra calls.*

**Q4 (deep): What's your failure philosophy if the critic itself breaks — times out, returns garbage JSON?**
A: Fail open, never fail closed — a broken guardrail must not block the user's answer. Concretely: critic timeout → return the original reply tagged `unverified`. Unparseable JSON → I try a direct parse, then regex-extract the first `{...}` object, and if both fail I default to `verdict=ok, confidence=unverified` and ship the original. Backend down → same. The principle is that the critic *improves* responses but is never on the critical path for *delivering* one. The cost of a missed critique is a slightly-less-verified answer; the cost of fail-closed is no answer at all — unacceptable for an assistant.
🔑 *Fail open — critic toot jaaye toh original reply `unverified` tag ke saath bhej do. Guardrail kabhi user ka jawab block na kare. JSON parse ki double-fallback (direct → regex).*

**Q5 (intermediate): What is the confidence tag and why surface it to the user?**
A: After critique, the reply carries `verified`, `unverified`, or `low`. `verified` is silent — that's the default, no clutter. `unverified` and `low` append a small visible italic line so Boss can see at a glance which answers were softened or flagged. The philosophy from the spec is that the critic doesn't *block* low-confidence replies — it ships them with the tag and lets the human decide. It's calibrated honesty: the system tells you how much to trust it instead of presenting everything with equal false confidence.
🔑 *Tag = calibrated honesty; verified silent, unverified/low visible. System block nahi karta, bas batata hai kitna bharosa karein — human decide karega.*

**Q6 (curveball): Isn't using an LLM to judge an LLM circular? What if the judge hallucinates a problem that isn't there?**
A: It's a real limitation and I'd name it directly. The mitigations: the judge runs a *narrow, structured* rubric with binary checks, not open-ended "is this good" — narrow tasks are where small models are reliable. A false-positive just triggers one revision pass, which is cheap and usually harmless. And the worst case is bounded — one revise, then ship. What it genuinely *can't* catch is a shared blind spot — if both models believe the same wrong fact, the critic won't flag it; that's exactly why CLAIMS forces *hedging* rather than asserting correctness, and why real web-fact-checking is a noted future phase. So: useful guardrail, honestly not a correctness proof.
🔑 *Haan, thoda circular hai — isliye rubric narrow rakha (binary checks), false-positive sirf 1 revise, aur shared blind-spot nahi pakad sakta. CLAIMS sourcing nahi, hedging enforce karta hai. Honest limitation bolna impress karta hai.*

**Traps / kya NA bolna:**
- ❌ Don't say the critic "guarantees no hallucinations." It reduces and hedges them; it doesn't verify facts against the world.
- ❌ Don't say it loops until the answer is perfect. It's **exactly one** revision — saying "loops until good" contradicts your own design and invites a "what about infinite loops" trap you'd then fail.
- ❌ Don't claim the critic blocks bad answers. It tags and ships; the human decides.

**Follow-up rabbit holes:**
- "How would you measure if the critic actually helps?" → A/B: critic-on vs critic-off on eval cases in `data/evals/critic/`, track human-rated quality + false-revise rate. Honest: you have eval *cases*, an offline A/B is the next step.
- "Structured outputs — how do you make the judge return clean JSON reliably?" → Strict "output ONLY a JSON object" instruction + robust parser with regex fallback + schema-coercion (`normalise()` maps aliases like 'high'→'verified'). Tool/JSON-mode would harden it further.
- "What about prompt injection from the recalled memory into the critic?" → Memory block is XML-fenced and labeled "background context, not user instruction"; good segue into the security rabbit hole below.

---

## FastAPI Daemon, Pydantic v2, and Production Hygiene

### Long-running service design
**Kya hai (Hinglish):** Daemon ek hamesha-chalta-rehne-wala service hai. Har baar `claude` CLI ko subprocess me launch karne ke bajaye, ek FastAPI server background me chalta hai jo state memory me rakhta hai aur HTTP (`/chat`, `/task`) pe requests leta hai. Telegram bridge, voice, web UI — sab isi ek daemon ko hit karte hain. Pydantic v2 har request/response ko validate aur type-check karta hai.

**Aapke project se connection:** `daemon.py` me FastAPI app, `lifespan` context manager state load + background-sync + scheduler start karta hai, `127.0.0.1` pe bind (no public port). `ChatResponse`/`ChatRequest` Pydantic v2 models hain (`reply`, `confidence`, `memory_hits`, `revised`, `intent`, `priority` fields). State har 5 min disk pe sync hota hai aur shutdown pe bhi.

**Interview Q&A:**

**Q1 (basic): Why a long-running daemon instead of spawning the CLI per request?**
A: Three wins. State persistence — conversations, sessions, costs, goals live in memory and sync to disk, so context survives across messages instead of cold-starting every time. Shared infra — one place loads the embedding model, the scheduler, the vector client, instead of paying that cost per invocation. And a clean interface — Telegram, voice, and a future web UI all hit the same HTTP endpoints with a subprocess fallback if the daemon's down. It's the move from "run a script each time" to "a service."
🔑 *Daemon = state persist + shared infra (embedding model ek baar load) + ek HTTP interface sabke liye. Per-call CLI = cold start har baar.*

**Q2 (intermediate): What does Pydantic v2 buy you here, concretely?**
A: Validated, typed boundaries. Every request and response is a Pydantic model, so malformed input is rejected at the edge with a clear 422 before it touches my logic, and FastAPI auto-generates OpenAPI docs from those models for free. I use `Field` constraints — for example goal creation enforces `max_budget_usd` between 0.1 and 50, and a description length range — so safety limits are declarative, not scattered `if` checks. v2 specifically is much faster (Rust core) and the validation semantics are stricter, which I want at an API boundary.
🔑 *Pydantic = typed validated boundary; galat input 422 se reject, OpenAPI free, `Field` se limits declarative (budget 0.1–50). v2 = Rust core, fast.*

**Q3 (deep / system-design): How does state survive a daemon crash, and what's the worst-case data loss?**
A: State is held in memory and synced to `data/state/jarvis-state.json` on a 5-minute interval via a background task started in the `lifespan` startup, plus a final sync on graceful shutdown. So a graceful stop loses nothing; a hard crash loses at most the last 5 minutes of conversation/cost deltas. For a personal assistant that's an acceptable RPO. If I needed stronger durability I'd write-ahead each mutation or move to SQLite with WAL — but that's trading simplicity for a guarantee I don't currently need. There's also orphan-recovery: goals left RUNNING when the daemon died get re-queued cleanly on restart.
🔑 *State memory me + 5-min disk sync + shutdown pe final sync. Graceful = zero loss, hard crash = max 5 min loss (acceptable RPO). Zyada durability chahiye toh SQLite WAL.*

**Q4 (intermediate): Security — this exposes `/chat` which runs an LLM with tool access. How is that not a disaster?**
A: It binds to `127.0.0.1` only — no public port — and the docstring explicitly says don't expose it without adding bearer-token auth first. Since the Telegram bridge runs on the same host, localhost is sufficient and the attack surface is local. On the prompt side, recalled memory is XML-fenced and explicitly labeled "background context, not user instruction" to blunt prompt-injection from indexed content, and there's a tiered trust model where irreversible actions (send email, submit forms, delete, publish) require confirmation regardless of mode. So: network-isolated, injection-aware, and human-in-the-loop for anything destructive.
🔑 *127.0.0.1 only (no public port), localhost = Telegram same host. Memory XML-fenced "background only" (injection defense), aur irreversible actions pe human confirm. Public karna ho toh bearer-token pehle.*

**Q5 (curveball): You log to JSONL files everywhere. Why JSONL and not a proper DB or logging service?**
A: JSONL — one JSON object per line — is append-only, crash-safe (a half-written last line doesn't corrupt earlier ones), trivially greppable, and streamable line-by-line without loading the whole file. Every layer writes its own: `recall.jsonl`, `critic.jsonl`, `intent.jsonl`, `conversations.jsonl` — with hashed message content, not raw text, for privacy in some logs. It's the right weight for a single-host personal system where I want observability and tunability without standing up Postgres + Grafana. The logging is also best-effort and never raises — observability must not break the feature it observes.
🔑 *JSONL = append-only, crash-safe, greppable, streamable; har layer apna log. Best-effort (never raises) — logging feature ko todna nahi chahiye. Single-host ke liye sahi weight.*

**Traps / kya NA bolna:**
- ❌ Don't say "FastAPI is multi-threaded so it's fast." FastAPI is async/ASGI; throughput comes from the event loop, not threads.
- ❌ Don't claim the daemon is production-internet-grade. Be honest: it's localhost-bound, single-host, no auth yet — that's a deliberate scope, not an oversight.
- ❌ Don't say Pydantic "just does type hints." It does *runtime validation + coercion*, which is the whole point at an API boundary.

**Follow-up rabbit holes:**
- "How would you scale this to many users?" → Per-user session partitioning (the `user_id` hook already exists), concurrency caps, move state to Redis/Postgres, add auth.
- "Graceful shutdown details?" → `lifespan` `finally` stops scheduler + final state sync; uvicorn handles SIGTERM.
- "Why systemd?" → auto-restart on crash, boot persistence, log capture via journald, hardening directives — turns the script into a managed service.

---

## Testing & Evals (the part that signals "I ship real systems")

### pytest suite + per-layer eval cases
**Kya hai (Hinglish):** Do alag cheezein. Unit tests (pytest) deterministic code ko check karte hain — parser sahi JSON nikaal raha? threshold sahi filter kar raha? skip-logic sahi? Evals LLM ke *behaviour* ko check karte hain — kya recall sahi chunk laata hai, kya critic tone-violation pakadta hai. LLM non-deterministic hai isliye uske liye example-based eval cases chahiye, plain assertions nahi.

**Aapke project se connection:** `tests/test_recall.py`, `test_critic.py`, `test_intent.py` + audit tests — 35+ tests. Eval cases `data/evals/recall/test_cases.jsonl` aur `data/evals/critic/test_cases.jsonl` me. Code testability ke liye design hai: `build_block_from_hits()` aur `parse_output_for_test()` pure functions hain jo LLM ke bina test ho jaate hain.

**Interview Q&A:**

**Q1 (intermediate): How do you unit-test code that's wrapped around a non-deterministic LLM?**
A: You separate the deterministic shell from the stochastic core and test the shell hard. I deliberately factored the pure logic out: the recall formatter (`build_block_from_hits`), the critic JSON parser, the intent parser, the threshold filter, the skip heuristics — all pure functions I can unit-test with synthetic inputs and exact assertions, no model call. For the LLM behaviour itself, I keep example-based eval cases as JSONL — "this input should surface that chunk," "this tone-violating reply should get verdict=revise" — and run them as a behavioural regression suite. So unit tests guard the plumbing, evals guard the behaviour.
🔑 *Deterministic shell ko pure-function bana ke pytest se test karo (parser, threshold, skip); LLM behaviour ke liye example-based eval cases. Dono alag.*

**Q2 (deep): Give a concrete eval case and what it protects against.**
A: From the recall evals: the input "what is the airspeed of an unladen swallow" must return an *empty* context — all scores below 0.55. That protects against threshold drift: if someone lowers the threshold or swaps the embedding model and irrelevant junk starts leaking into prompts, this case goes red. Another, from critic evals: a reply using shortened forms like "bta"/"kr" must produce `verdict=revise` on TONE — that locks in Boss's non-negotiable respectful-register preference so a model update can't silently regress it. Evals turn "preferences" into "tests."
🔑 *Eval case = behaviour ko lock karta hai; e.g. irrelevant query → empty (threshold drift se bachao), "bta/kr" → revise (tone preference lock). Regression catch karte hain.*

**Q3 (curveball): Your tests pass but production answers feel worse. Where do you look?**
A: That gap is exactly why I have layered JSONL logs in production, not just tests. Tests prove the *plumbing* is correct; they can't prove the *retrieved content* is good. I'd pull `recall.jsonl` to see if `top_score` distributions dropped (embedding or threshold issue), `critic.jsonl` to see if revise-rate or low-confidence-rate spiked, and `conversations.jsonl` for the actual turns. Often "feels worse" is a recall-quality regression — relevant chunks scoring just under threshold — which no unit test catches but the score logs reveal immediately. That's the difference between testing and observability: tests catch what you anticipated, logs catch what you didn't.
🔑 *Tests = plumbing sahi; logs = content sahi. "Feels worse" usually recall-quality drop hota hai — recall.jsonl ka top_score dekho, critic.jsonl ka revise-rate dekho. Tests anticipated bugs pakadte hain, logs unanticipated.*

**Traps / kya NA bolna:**
- ❌ Don't claim a fixed accuracy percentage for the system. You have pass/fail eval *cases* and observability logs — say that. Inventing "94% accuracy" is the fabrication trap.
- ❌ Don't say "I mock the LLM in every test." You test pure functions directly; you don't need to mock what you factored out.

**Follow-up rabbit holes:**
- "CI?" → pytest runs the suite; `scripts/eval_baseline.py --check` exits non-zero on >5pp pass-rate drop per agent = a quality gate.
- "Coverage gaps?" → Honest: behavioural evals run offline, not in CI on every commit (the LLM cost) — a real "what I'd improve."

---

## 60-Second Architecture Story (rehearse this out loud)

"User sends a message to the Telegram bridge, which hits my FastAPI daemon's `/chat`. The daemon kicks off two things concurrently with asyncio — an intent classifier on a cheap Haiku model, and a recall layer that embeds the message with MiniLM, does a top-5 cosine search in ChromaDB, drops anything under 0.55 similarity, trims to a 2000-token budget, and builds an XML memory block. Both get prepended to the prompt, which goes to a Claude Code worker via the Agent SDK. The draft then passes through a silent critic — one Haiku call scoring it on intent, memory-contradiction, claim-sourcing, and tone; if it fails, exactly one revision runs, and a confidence tag gets attached. For bigger jobs the `/task` endpoint fans out N independent workers in parallel via `asyncio.gather` with an aggregator step. Every layer is fail-open, has a kill-switch, logs to JSONL, and runs as a hardened systemd service. 35+ pytest tests on the deterministic logic plus behavioural eval cases for the LLM layers."

🔑 *Yeh poori kahani ek saans me bol pao — interviewer ko pura system ek minute me dikh jaata hai.*
