# EDITH — Agentic Industrial Maintenance Copilot — Interview Prep

> **Project (what you say in one line):** "EDITH is an agentic maintenance copilot for a steel plant. It watches 15 machines' live sensors, and when something crosses a threshold it runs a five-agent reasoning chain — Diagnosis → RCA → RUL prediction → Prioritization → Recommendations — that produces a *grounded* answer: every factual claim comes from structured ML inference or a cited document, never from the LLM's imagination. The LLM only writes the prose; the facts come from models and sources, and a faithfulness gate checks the prose against those sources before the engineer sees it."

> **Grounding note for you (be honest):** the real code lives in `data/hackathons/tata-steel-2026/round_2/vulcan/` (the `vulcan/` package is the brain; `edith/backend/main.py` is the FastAPI surface). The deterministic eval harness scored *low fact-recall* (~0.13 on a brutal strict-string-match harness — see "Traps" in §10). Do NOT lead with accuracy numbers. Lead with the **architecture decisions** — those are genuinely senior-tier and defensible. If asked for metrics, be honest about the harness being strict and pivot to what you'd do to measure it properly (LLM-judge + grounding-ref match). Honesty about a weak eval beats a fabricated strong one — every interviewer can smell a made-up number.

---

### 1. Why structured ML for facts, LLM only for prose ("zero-hallucination architecture")

**Kya hai (Hinglish):** Dekhiye — ek normal RAG/LLM app me LLM hi sab kuch generate karta hai: number, fault, RUL, sab. Problem ye hai ki LLM number "bana" sakta hai (hallucinate) — aur maintenance me ek galat RUL ya galat threshold se machine fail ho sakti hai, banda ghayal ho sakta hai. EDITH ka design ulta hai: saari **factual cheezein** — fault class, anomaly score, RUL cycles, risk band, threshold breach — ye sab **deterministic ML models aur dataset spine** se aati hain. LLM ka kaam sirf itna hai ki un grounded facts ko ek saaf English answer me likh de, aur har claim ke aage `[N]` citation lagaye. Matlab LLM "writer" hai, "fact-source" nahi.

**Aapke project se connection:** `vulcan/agents/supervisor.py` me `_build_context()` pehle 5 agents ke findings ko numbered `Source [N]` blocks me daalta hai (spine scenario, ML fault classifier, RUL, risk score, spare parts). Phir `subscription_llm()` ko **ek hi LLM call** jaata hai (`_SYS` prompt: *"Answer ONLY from the numbered Source [N] evidence... Never invent part numbers, costs, thresholds"*). Fast path (`_try_lookup_answer`, `_try_doc_answer` in `main.py`) to LLM ko poori tarah bypass karke seedha spine se number deta hai.

**Interview Q&A:**

- **Q1 (basic): Your resume says "zero LLM hallucination on factual claims." What does that actually mean?**
  **A:** It means the LLM never *originates* a factual claim. Every number an engineer sees — the fault class, the RUL in cycles, the threshold value, the risk band, the part number — is computed by a deterministic model or read from the equipment spine, then passed to the LLM as numbered evidence. The LLM's only job is to phrase that evidence into readable prose and cite each source inline as `[N]`. So a hallucination would require the LLM to contradict its own cited source — and I have a faithfulness gate that catches exactly that. The LLM is a writer, not an oracle.
  🔑 *(LLM sirf likhता hai, facts models aur spine se aate hain — isliye "zero hallucination on facts".)*

- **Q2 (basic): Why not just let a good LLM do the whole thing? GPT-4-class models are quite accurate.**
  **A:** Two reasons, both about *trust* in a safety-critical setting. First, "quite accurate" isn't good enough when a wrong RUL means a caster breakout or an injured operator — I need *traceable* facts, not statistically-likely ones. Second, the LLM has no access to this plant's live sensor stream or its proprietary RCA history; that lives in my ML models and dataset. So even the best LLM would be guessing about *this* machine. Structured ML gives me a number I can point to a CSV row and a standard for. The LLM gives me the bedside manner.
  🔑 *(Safety-critical me "likely sahi" kaafi nahi — "traceable sahi" chahiye.)*

- **Q3 (intermediate): Walk me through the data flow for a single diagnosis. Where does the LLM sit?**
  **A:** A sensor crosses an alarm threshold in the SSE stream. The supervisor fires `handle_alert()`. It runs the agent DAG: DiagnosisAgent matches the sensor pattern to a known failure scenario in the spine and runs the LightGBM fault classifier; PredictorAgent runs the RUL regressor + IsolationForest anomaly score; RCAAgent pulls the root cause + retrieves RCA docs; RecommenderAgent gets resolution steps + spare-part availability; PrioritizerAgent computes a risk score. All of that is deterministic. *Then* — and only then — `_build_context()` assembles those findings into numbered sources, and there's exactly one `subscription_llm()` call that turns them into cited prose. After that, the NLI faithfulness gate scores the prose against the sources. The LLM sits at the very end, downstream of all the facts.
  🔑 *(Pipeline: ML agents pehle → numbered evidence → ek LLM call → faithfulness gate. LLM last me.)*

- **Q4 (deep): How is this different from "RAG with citations"? Plenty of apps cite sources.**
  **A:** RAG-with-citations still lets the LLM *read* documents and *decide* what's true — the citation is a pointer, but the LLM chose the claim. In EDITH, the load-bearing facts aren't even text the LLM interprets — they're typed outputs of ML models and spine lookups (a float RUL, an enum fault class, a computed risk integer). The LLM receives them pre-computed. So the failure surface shrinks from "did the LLM read and reason correctly?" to "did the LLM faithfully restate a given number?" — a much smaller, checkable surface. And I check it with NLI. RAG citations reduce hallucination; this architecture reduces the LLM's *authority over facts* to near zero.
  🔑 *(RAG me LLM decide karta hai kya sahi hai; yaha facts pre-computed aate hain, LLM sirf restate karta hai.)*

- **Q5 (system design): If you had to scale this to 5,000 assets across 10 plants, what breaks first and what changes?**
  **A:** First thing that breaks is the per-asset model artifacts — I key fault/anomaly models per asset (`_asset_key`) because assets in one class can have different sensor sets. At 5,000 assets that's a model registry and cold-start problem, so I'd move to per-equipment-class models with sensor-set adapters, or a single multi-task model with asset embeddings. Second, the synchronous single LLM call in the request path won't hold under load — I'd make the deep path fully async with a queue, and lean harder on the fast deterministic path (which already handles spec lookups in <300ms with no LLM). Third, ChromaDB local is fine for 80 docs; at plant-scale knowledge bases I'd move to a managed vector store with metadata pre-filtering by plant + equipment class (which my retriever already supports via the `where` clause). The agent orchestration itself scales fine — it's stateless per turn.
  🔑 *(Pehle tootega: per-asset models + sync LLM call. Fast path aur async queue pe shift karo.)*

- **Q6 (curveball): An LLM still wrote the final answer. Can you actually claim zero hallucination, or is that marketing?**
  **A:** Fair challenge — and I'd scope it precisely: I claim zero hallucination *on factual claims*, not "the LLM is incapable of error." The LLM can still phrase something awkwardly or add framing. What I guarantee is that any *factual* claim is either (a) pre-computed and handed to it, or (b) caught by the faithfulness gate if it drifts from the source. The gate flags claims a source *contradicts* and appends a low-confidence note. So the honest claim is: "facts are sourced, and unsupported facts are flagged before the engineer trusts them" — not "the LLM is perfect." I'd rather state that precisely than oversell it.
  🔑 *(Honest scope: "facts grounded + drift flagged", not "LLM perfect" — interviewer ko yahi maturity chahiye.)*

**Traps / kya NA bolna:**
- ❌ Don't say "it's impossible for EDITH to hallucinate." It's not — be precise: facts are sourced, drift is *flagged*.
- ❌ Don't claim the LLM does no reasoning at all — it does synthesis/ordering. The facts are what's locked down.
- ❌ Don't dismiss LLMs as useless — you *use* Claude for the prose; the point is *separation of concerns*, not anti-LLM.

**Follow-up rabbit holes:** "What stops the LLM from omitting a critical fact?" (gate checks faithfulness of what's *said*, not completeness — be honest, then describe a completeness check you'd add: assert every finding key appears). → "What if the ML model itself is wrong?" (calibration, confidence label, anomaly cross-check, human-in-loop). → "How do you handle conflicting agents?" (prioritizer reconciles; you surface the conflict, don't hide it).

---

### 2. NLI faithfulness gating (DeBERTa entailment) — the "verified" badge

**Kya hai (Hinglish):** Faithfulness gate ek chhota local model hai (`cross-encoder/nli-deberta-v3-small`) jo **Natural Language Inference** karta hai. NLI matlab: do sentence do — ek "premise" (source) aur ek "hypothesis" (claim) — aur model batata hai kya premise se hypothesis *entail* hota hai (sach nikalta hai), *contradict* karta hai, ya *neutral* hai. EDITH har `[N]`-cited sentence ko uske cited source ke against score karta hai. Agar source claim ko **contradict** kare → wo claim hallucination hai → flag. Agar neutral ho (source ne na bola na kaata) → wo unverified hai par hallucination nahi. Final me ek overall faithfulness score banta hai jo UI me "verified / unverified / low" badge ban jaata hai.

**Aapke project se connection:** `vulcan/rag/faithfulness.py` — `run_gate(answer, chunks)`. Key design choices jo aap explain kar sakte ho: (1) **direction matters** — premise = SOURCE, hypothesis = CLAIM (ulta karne se entailment collapse ho jaata hai, code comment me likha hai). (2) Ek claim agar `[1][4]` dono cite kare to **max** entailment liya jaata hai, average nahi (EITHER source supports → faithful). (3) Hallucination flag **contradiction pe** hota hai, low-entailment pe nahi — kyunki honest paraphrase aksar "neutral" aata hai. (4) `_clean_claim()` `[N]` markers, markdown, aur `°` symbol hata deta hai kyunki ye cross-encoder ka score girate hain. Supervisor `_run()` me gate chalta hai aur unfaithful claims ko answer ke neeche `[VULCAN faithfulness note]` ke saath append karta hai.

**Interview Q&A:**

- **Q1 (basic): What is NLI and why use it to check a RAG answer?**
  **A:** NLI — Natural Language Inference — takes a premise and a hypothesis and classifies the relationship as entailment, contradiction, or neutral. I use it as a post-generation faithfulness check: the retrieved source is the premise, each cited sentence of the answer is the hypothesis. If the source *entails* the sentence, the claim is grounded. If it *contradicts*, that's a hallucination and I flag it. It's a cheap, local, keyless way to verify the LLM didn't drift from what its sources actually say.
  🔑 *(NLI = source se claim nikalta hai ya nahi — entail / contradict / neutral.)*

- **Q2 (intermediate): Why a cross-encoder for this and not just cosine similarity between the claim and the source?**
  **A:** Cosine similarity measures *topical relatedness*, not *truth*. "The bearing temperature is 95°C" and "the bearing temperature is NOT 95°C" are nearly identical in embedding space — high cosine — but one entails and one contradicts. A cross-encoder reads both sentences *jointly* with cross-attention and is trained specifically on the entailment/contradiction/neutral task, so it catches negation and numeric mismatch that cosine is blind to. For a faithfulness gate you need a directional truth judgment, which is exactly what NLI cross-encoders give you.
  🔑 *(Cosine sirf "same topic" batata hai; NLI cross-encoder "sach hai ya jhooth" batata hai — negation pakadta hai.)*

- **Q3 (intermediate): You flag on contradiction, not on low entailment. Why? Isn't low entailment a red flag too?**
  **A:** Because of how honest paraphrase scores. When the model writes "the RUL is 40 cycles, indicating imminent failure," the source has the 40 cycles but maybe not the word "imminent" — so the NLI verdict is *neutral*, not entailment. Neutral means "the source neither states nor refutes this exact phrasing" — that's unverified, not a lie. If I flagged every non-entailed claim as a hallucination, I'd cry wolf on well-grounded answers and the badge would be useless. A real hallucination is when the source *actively contradicts* the claim — contradiction mass dominates. So I flag on `contradiction >= 0.5 and contradiction > entailment`. Neutral claims I downweight in the score but don't flag.
  🔑 *(Honest paraphrase "neutral" aata hai = unverified, jhooth nahi. Flag sirf contradiction pe — warna false alarms.)*

- **Q4 (deep): How do you turn per-claim NLI scores into one number and a badge? Walk me through the math.**
  **A:** For each cited claim I take the best supporting source (highest entail-minus-contradiction margin). I compute a per-claim *support* score = `entail + 0.5·neutral − contra`, clamped to [0,1] — this credits honest paraphrase (the 0.5·neutral term) so it doesn't score zero. The overall faithfulness is the mean of those support scores. Then I bucket: `≥0.7 → verified`, `≥0.45 → unverified`, else `low`. The retry flag fires only if at least one claim was *contradicted*. I also skip fragments — headings, table rows, sub-25-char stubs, lines ending in a colon — because NLI is noisy on non-sentences and would produce spurious flags.
  🔑 *(support = entail + 0.5·neutral − contra; mean → 0.7/0.45 thresholds → verified/unverified/low.)*

- **Q5 (deep/system-design): The gate runs after generation. What's the latency cost, and what would you do if it flags a claim?**
  **A:** It's a small CPU cross-encoder over maybe 5–10 cited sentences, so it's tens to low-hundreds of milliseconds — acceptable on the deep path which is already ~11s. Right now, when it flags, I append a visible low-confidence note and downgrade the badge — I don't silently drop the claim, because hiding it is worse than disclosing it. The `flag_retry` boolean is the hook for a *re-grounding* pass: re-run synthesis with a stricter "only restate the numbers" instruction, or fall back to the deterministic template that can't drift. At higher stakes I'd block the answer entirely on contradiction and force the deterministic path.
  🔑 *(Gate generation ke baad chalta hai, ~100ms; flag pe note dikhao + retry/template floor — chhupao mat.)*

- **Q6 (curveball): NLI models are trained on news/Wikipedia. Your domain is steel-plant maintenance jargon. Doesn't that break the gate?**
  **A:** It's a real domain-shift risk and I'd be honest that the gate is a *safety net*, not a certifier. Two mitigations I built in: I normalize formatting (strip citations, markdown, the degree symbol) because those measurably depress the cross-encoder's score on otherwise-grounded claims — so I'm scoring prose, not punctuation. And I lean on *contradiction* detection rather than entailment, because numeric/negation contradictions transfer across domains much better than fine-grained entailment of jargon. Where I'd improve: a small domain-adaptation fine-tune of the NLI model on synthetic maintenance claim/source pairs, and pairing NLI with an exact numeric-match check for the figures (which don't need NLI at all — a regex/number diff is more reliable for "is 95°C in the source?").
  🔑 *(Domain shift real hai — isliye contradiction pe focus + numbers ko regex se match karo, jargon entailment pe bharosa kam.)*

**Traps / kya NA bolna:**
- ❌ Don't say NLI "checks if the answer is correct." It checks if the answer is *supported by the cited source* — those differ (source could be wrong).
- ❌ Don't reverse premise/hypothesis in your explanation — premise = source, hypothesis = claim. Getting this backwards is a tell you didn't build it.
- ❌ Don't claim the gate is 100% reliable on a tiny CPU model — frame it as a *flagging* safety net + a numeric exact-match for figures.

**Follow-up rabbit holes:** "Why not RAGAS / a self-consistency LLM-judge?" (cost, latency, keyless requirement, determinism — but you'd add LLM-judge for nuance). → "What about claims with no citation?" (uncited factual claims are themselves a smell — a completeness/citation-coverage check). → "Calibration of the 0.7 threshold?" (chosen empirically; you'd tune on a labeled set).

---

### 3. Hybrid RAG: bge-small embeddings + FlashRank reranking + ChromaDB (vs plain cosine)

**Kya hai (Hinglish):** RAG do step me hota hai yaha. **Step 1 — dense retrieve:** query ko `bge-small-en-v1.5` se 384-dim vector banao, ChromaDB me cosine se top-20 candidate chunks nikaalo. Ye fast hai par "approximately relevant" — recall acha, precision so-so. **Step 2 — rerank:** un 20 candidates ko ek **cross-encoder reranker** (FlashRank, `ms-marco-MiniLM-L-12-v2`) query ke saath *jointly* padhke re-score karta hai aur top-5 chunta hai. Cross-encoder slow hai par bahut precise — isliye 20 pe chalao (sasta), pure corpus pe nahi. Ye "retrieve-cheap-wide, then rerank-precise-narrow" pattern hi 2026 ka standard hybrid RAG hai.

**Aapke project se connection:** `vulcan/rag/embedder.py` (`BAAI/bge-small-en-v1.5`, 384-dim, L2-normalized — BGE ko normalize chahiye, ONNX backend for CPU speed). `vulcan/rag/retriever.py` — `retrieve()` ChromaDB se `_TOP_K_RETRIEVE=20` candidates leta hai, phir FlashRank se `_TOP_K_FINAL=5` pe rerank. Metadata prefilter bhi hai (`equipment_class`, `doc_types`) jo candidate pool pehle hi narrow kar deta hai. Corpus = 80 markdown docs (13 manuals + 13 SOPs + 25 RCA reports). Fail-soft: FlashRank na mile to dense order pe gir jaata hai.

**Interview Q&A:**

- **Q1 (basic): Why two stages — retrieve then rerank? Why not just take the top-5 from the vector search?**
  **A:** Because bi-encoder vector search and cross-encoder reranking trade off speed against precision oppositely. The bi-encoder (bge-small) embeds query and docs *separately*, so I can pre-index all 80 docs and do an instant cosine lookup — great recall, cheap, but it can't model fine query-document interaction. The cross-encoder reads query+doc *together* with full cross-attention — far more precise on relevance — but it's too slow to run over the whole corpus. So I use the bi-encoder to cheaply pull a wide top-20, then the expensive cross-encoder to precisely reorder down to the top-5 the LLM actually sees. Best of both: wide recall, sharp precision.
  🔑 *(Bi-encoder = fast wide net; cross-encoder = slow precise filter. 20 retrieve → 5 rerank.)*

- **Q2 (intermediate): Why bge-small specifically, and why L2-normalize the embeddings?**
  **A:** bge-small-en-v1.5 is 384-dim, runs fast on CPU (I run it via ONNX), and punches above its size on MTEB retrieval benchmarks — exactly the right tradeoff for a keyless, local, no-GPU deployment. The L2-normalization is required by BGE: the model is trained so that cosine similarity is the intended metric, and ChromaDB's distance becomes a clean `1 − cosine` only when vectors are unit-normalized. Skip the normalization and your similarity scores are distorted by vector magnitude, which silently hurts retrieval quality.
  🔑 *(bge-small = chhota+fast+strong on CPU; L2-normalize isliye ki BGE cosine ke liye train hua hai.)*

- **Q3 (intermediate): "Plain cosine" was in your brief — what specifically does reranking fix that plain cosine retrieval misses?**
  **A:** Plain cosine retrieval rewards *topical* and *lexical* overlap encoded in a single vector. It struggles when the right chunk uses different words than the query, or when several chunks are all topically close but only one actually answers the question. The cross-encoder reranker, because it attends across query and passage tokens jointly, captures *relevance to the specific question* — it'll push the chunk that contains the actual answer above chunks that merely mention the same equipment. In a maintenance corpus where ten SOP sections all talk about "bearing," that precision is the difference between citing the right procedure and a related one.
  🔑 *(Cosine "topic match" deta hai; reranker "is exact sawal ka jawab" deta hai — same-topic chunks me se sahi wala upar.)*

- **Q4 (deep): FlashRank uses ms-marco-MiniLM. That's trained on web search relevance. Justify it for steel-plant docs.**
  **A:** ms-marco-MiniLM-L-12-v2 is a general query-passage relevance reranker — it learned "does this passage answer this query," which is a domain-transferable signal more than domain-specific knowledge. The relevance judgment ("this paragraph addresses this question") generalizes far better than, say, a classifier trained on web *topics* would. It's also tiny and CPU-friendly, which my deployment constraint demanded. That said, I'd flag the honest limitation: it has no notion of maintenance severity or safety priority. If reranking quality became the bottleneck I'd fine-tune a reranker on synthetic (query, SOP-chunk, relevance) pairs from my own dataset — I already have an eval set to measure the lift.
  🔑 *(MS-MARCO reranker "relevance" seekha hai, jo transfer hota hai; chhota+CPU-friendly. Domain fine-tune = next step.)*

- **Q5 (system-design): How do you decide chunk size, top-k=5, and the metadata prefilter? What's the failure mode of each?**
  **A:** top-k=5 balances giving the LLM enough evidence against context dilution — too many chunks and the synthesis gets noisy and the faithfulness gate has more to check; too few and I miss the answer. The metadata prefilter (`equipment_class`, `doc_type`) narrows the candidate pool *before* vector search — its failure mode is over-filtering: if the query's equipment is mis-resolved I could filter out the right doc, so my retriever is fail-soft and retries without the prefilter on error. Chunk size is the classic tradeoff: too large and the cross-encoder + NLI gate lose precision on which sentence is grounded; too small and you fragment a procedure across chunks. For SOPs I chunk on section boundaries so a procedure stays intact.
  🔑 *(k=5 = evidence vs noise balance; prefilter fast karta hai par over-filter risk → fail-soft retry; section-wise chunking SOP ke liye.)*

- **Q6 (curveball): Your brief mentioned a "DeBERTa cross-encoder" for the gate and a "MiniLM cross-encoder" for reranking. Same thing?**
  **A:** No — and it's worth being precise because they're different jobs with different models. The *reranker* is `ms-marco-MiniLM-L-12-v2` via FlashRank, trained on query-passage *relevance* — it answers "which chunk best answers this query." The *faithfulness gate* is `nli-deberta-v3-small`, trained on *entailment* — it answers "does this source support this claim." Both are cross-encoders (joint query-doc / source-claim attention), but one ranks relevance pre-generation and the other verifies truth post-generation. Conflating them would suggest I copy-pasted a pattern without understanding it.
  🔑 *(Reranker = MiniLM/relevance, pehle. Gate = DeBERTa/entailment, baad me. Dono cross-encoder par alag kaam.)*

**Traps / kya NA bolna:**
- ❌ Don't call the bi-encoder a "cross-encoder" or vice versa — that's the #1 RAG-knowledge tell.
- ❌ Don't say "reranking improves recall" — it improves *precision/ordering* of an already-retrieved set; recall is set by stage-1.
- ❌ Don't forget to mention metadata prefiltering — it's a real lever in your code and interviewers love it.

**Follow-up rabbit holes:** "What about true *hybrid* (BM25 + dense fusion / RRF)?" (you do dense + rerank; BM25 fusion is the next lever for exact-term queries like part numbers). → "Embedding drift / re-indexing strategy?" → "How do you evaluate retrieval — recall@k, MRR, nDCG?" (have an answer: you'd measure recall@20 for stage-1 and nDCG@5 post-rerank).

---

### 4. RUL prediction & where IsolationForest fits

**Kya hai (Hinglish):** **RUL = Remaining Useful Life** — machine kitne aur "cycles" (yaha ~1 cycle/hour) tak chalegi failure se pehle. Ye ek **regression** problem hai: sensor state dekho, predict karo kitna life bacha hai. EDITH me ye LightGBM regressor karta hai (`rul_cycles` target). Sath me **IsolationForest** ek *alag* kaam karta hai — ye **anomaly detection** hai, supervised nahi: ye sirf "normal" rows pe fit hota hai aur batata hai current reading kitni *out-of-distribution* hai. Matlab RUL kehta hai "kitna time bacha", IsolationForest kehta hai "abhi state kitni weird hai". Dono milke ek poori health picture dete hain — kabhi RUL theek dikhe par anomaly spike kare (naya unseen fault), to ye cross-check ban jaata hai.

**Aapke project se connection:** `vulcan/ml/models.py`. `estimate_rul()` — LightGBM regressor per equipment-class, `rul_trajectories_long.csv` se train (long→wide pivot), output `rul_cycles` + `rul_days_estimate` (cycles/24). `anomaly_score()` — IsolationForest per asset, **normal rows pe hi fit** (`X_normal = X[y==0]`), `decision_function` ko 0..1 anomaly score me map. `predict_fault()` — LightGBM 3-class classifier {NORMAL/WARNING/FAILURE}. Honesty point jo aap proud se bol sakte ho: training me **leak-safe splits** hain (code comments: temporal-tail split RUL me meaningless negative R² deta isliye shuffled holdout; fault me stratified split taaki holdout me actual faults hon). Submission doc: RUL MAE ≈ 280h vs baseline 306h (~9% lift).

**Interview Q&A:**

- **Q1 (basic): What is RUL and how did you model it?**
  **A:** RUL — Remaining Useful Life — is how much operating time a machine has left before it fails, expressed here in cycles (roughly one per hour) and converted to a days estimate. I framed it as supervised regression: the model sees the current sensor readings and predicts the remaining cycles. I trained one LightGBM regressor per equipment class on run-to-failure trajectories where each timestep is labeled with its true remaining cycles, since the dataset has full episodes counting down to failure.
  🔑 *(RUL = failure se pehle kitna life bacha; regression problem, LightGBM per equipment-class.)*

- **Q2 (intermediate): Why LightGBM for RUL and not a survival model like Weibull-AFT or an LSTM?**
  **A:** Honestly, partly a deployment constraint and partly fit. The plan originally wanted lifelines' Weibull-AFT survival model, but lifelines wasn't in my CPU-only, keyless environment — LightGBM was the explicitly-permitted alternative and shares the same artifact contract, so it's a one-trainer swap if I want survival modeling later. On fit: gradient-boosted trees handle tabular sensor features with mixed scales, missing values, and nonlinear thresholds extremely well with almost no tuning, and they train in seconds on CPU. An LSTM would model the temporal trajectory better but needs far more data and a GPU, and is overkill when good engineered window features already capture the degradation trend.
  🔑 *(LightGBM = CPU-fast, tabular pe strong, no GPU. Weibull-AFT/LSTM baad ke options, contract same.)*

- **Q3 (intermediate): Where does IsolationForest fit? Isn't fault classification already doing detection?**
  **A:** They answer different questions. The LightGBM fault classifier is *supervised* — it recognizes the fault patterns it was trained on (NORMAL/WARNING/FAILURE). IsolationForest is *unsupervised* anomaly detection — I fit it on normal-only data, so it flags any reading that's statistically far from normal *even if it's a fault type I've never labeled*. That's the safety value: a novel failure mode the classifier hasn't seen would still spike the anomaly score. So the classifier says "this looks like outer-race bearing wear," and IsolationForest independently says "this is X% abnormal" — a cross-check, not a duplicate.
  🔑 *(Classifier = known faults pehchanta hai; IsolationForest = "kuch bhi weird" pakadta hai, even unseen — cross-check.)*

- **Q4 (deep): Why fit IsolationForest on normal-only rows, and how do you turn its output into a 0–1 score?**
  **A:** IsolationForest works by randomly partitioning the feature space; anomalies get isolated in fewer splits, so they have shorter average path lengths. If I fit it on a mix of normal and faulty data, the faulty points become part of the "expected" distribution and the model stops treating them as anomalous — so I fit on normal-only rows to define a clean baseline of "healthy." For the score, `decision_function` returns a value where higher means more normal (roughly ±0.3); I map it to a 0–1 anomaly score via `clip(0.5 − raw, 0, 1)` so higher means more anomalous, and I set contamination from the observed fault rate, clipped to a sane [0.005, 0.2] range.
  🔑 *(Normal-only pe fit taaki "healthy" ka clean baseline bane; decision_function ko clip karke 0–1 anomaly score.)*

- **Q5 (deep): Your RUL evaluation — how did you avoid leaking, and why is the R² caveat honest rather than a red flag?**
  **A:** This is the part I'm most careful about. Each asset is one monotonic run counting down to failure. If I do a naive temporal-tail split — train on the early high-RUL healthy regime, test on the unseen near-failure regime — I get a meaningless negative R² because the test distribution was never trained on. The legitimate question RUL answers is "does sensor *state* predict remaining life," so I evaluate on a shuffled holdout spanning the full run, which is the correct choice for single-trajectory regression, and I *disclose* it. For cross-run honesty the dataset also supports leave-one-run-out CV with run-id grouping. The measured MAE was ~280 hours vs a per-asset-mean baseline of ~306h — about a 9% lift, which I state plainly rather than dressing up.
  🔑 *(Single-run degradation me temporal split negative R² deta — isliye shuffled holdout + leave-one-run-out CV, aur ye openly disclose karo.)*

- **Q6 (curveball): A RUL of "40 days" sounds precise. How confident should an engineer be in that number, and how do you communicate uncertainty?**
  **A:** Not point-precise, and I don't pretend it is. A 9%-over-baseline MAE means the estimate carries real error bars, so in the UI I bucket RUL into *bands* — imminent (<3 days), near-term (<2 weeks), monitor — rather than betting the decision on a single float. The band is what drives the risk score and the recommended urgency, not the raw number. The raw cycles are shown for transparency but the *decision* is made on the band, with the anomaly score and fault probability as corroborating signals. That's the honest way to use a noisy regressor: convert precision you don't have into a decision you can defend.
  🔑 *(Raw RUL ko band me convert karo — imminent/near-term/monitor — decision band pe lo, single float pe nahi.)*

**Traps / kya NA bolna:**
- ❌ Don't call IsolationForest a classifier or say it "predicts the fault type" — it's unsupervised anomaly scoring.
- ❌ Don't quote a glossy R² — your honest story is MAE ~280h vs 306h baseline (~9% lift) + disclosed split rationale. Owning the modest lift is *stronger* than faking a great one.
- ❌ Don't say you "fit IsolationForest on all data" — fit on normal-only is the whole point; getting this wrong reverses the technique.

**Follow-up rabbit holes:** "How do you get RUL *prediction intervals*, not just a point?" (quantile regression / conformal prediction — good answer to have ready). → "Cold start for a new asset with no failure history?" (per-class model + transfer). → "Concept drift as the machine ages / after a repair?" (retrain triggers, monitoring the anomaly-score distribution).

---

### 5. The five-agent reasoning chain (agentic orchestration)

**Kya hai (Hinglish):** EDITH ek **multi-agent orchestrator** hai. Ek "supervisor" hai jo query/alert ko dekhke decide karta hai kaun-kaun se specialist agents chalane hain (ek transparent DAG/plan). Paanch agents: **Diagnosis** (kaunsa fault, ML classifier + scenario match), **RCA** (root cause + RCA docs), **Predictor** (RUL + anomaly), **Prioritizer** (risk band — criticality × safety × ML × RUL × spares), **Recommender** (repair steps + spare parts). Har agent apna finding ek shared **reasoning trace** me likhta hai (FR4: "show your work"). Phir supervisor sab findings ko ek synthesis prompt me daalke ek LLM call karta hai. Ye LangGraph nahi hai — ek custom lightweight orchestrator hai, par genuinely agentic: dynamic planning, delegation, tool use, auditable trace, self-check.

**Aapke project se connection:** `vulcan/agents/supervisor.py` — `_PLANS` dict har intent ke liye agent chain define karta hai (e.g. `diagnosis` → full 5-agent chain; `rul` → diagnosis+predictor+prioritizer). `handle_query()` aur `handle_alert()` entry points. Agents `vulcan/agents/domain_agents.py` me. `ReasoningTrace` har step record karta hai (`trace.add(...)`). Prioritizer ka risk score `/14` scale pe hai (`crit_pts + safe_pts + ml_pts + rul_pts + spares`).

**Interview Q&A:**

- **Q1 (basic): What makes this "agentic" rather than just a pipeline of function calls?**
  **A:** Three things. First, the plan is *dynamic* — the supervisor classifies the query's intent and picks which agents to run from a per-intent DAG, so a pure RUL question runs a focused subset, not the whole chain. Second, each agent is a *specialist* that does tool use — it pulls from the spine, runs an ML model, retrieves documents — and grounds its own finding. Third, every step is recorded in an auditable reasoning trace, and there's a faithfulness self-check at the end. A fixed pipeline does the same steps every time and shows nothing; this plans, delegates, and shows its work.
  🔑 *(Agentic = dynamic per-intent planning + specialist tool-use + auditable trace + self-check, fixed pipeline nahi.)*

- **Q2 (intermediate): Why build a custom orchestrator instead of LangGraph or CrewAI?**
  **A:** For this scope, a framework would be overhead I'd have to fight. My orchestration is a single-level DAG with five known agents and deterministic ordering — I don't need persistent graph state machines, retries-as-edges, or a multi-hop planner. LangGraph shines when you have cyclic, long-horizon, branching agent graphs; here the value is in the *grounding discipline* and the trace, not the graph engine. A custom orchestrator is lighter on a CPU box, has zero framework lock-in, and every line of the plan-delegate-synthesize-gate flow is mine to debug. If the agent graph grew cyclic or needed checkpointing, I'd reach for LangGraph then.
  🔑 *(Single-level DAG ke liye framework overhead; custom = light, no lock-in, full control. Cyclic/long-horizon ho to LangGraph.)*

- **Q3 (intermediate): How does the Prioritizer combine signals into a risk band? Is it ML or rules?**
  **A:** It's a transparent weighted rule, deliberately — risk prioritization is exactly where I want auditability over a black box. It sums: process-criticality (asset criticality 1→+3, 2→+2, else +1), scenario safety-class (P1→+3 … P3→+1), ML failure probability, RUL band (imminent→+3, near-term→+2), and a spares/lead-time factor, on a /14 scale, bucketed into CRITICAL/HIGH/MEDIUM. Every contributing factor is recorded as a human-readable reason in the trace. I use ML for *detection and prediction* but a transparent scoring rule for the *decision* — because a maintenance manager needs to see *why* something is critical, not just trust a number.
  🔑 *(Risk = transparent weighted rule /14 — criticality+safety+ML+RUL+spares — ML detect karta hai, rule decide karta hai, audit ke liye.)*

- **Q4 (deep): Agents can disagree — e.g. the classifier says NORMAL but the anomaly score is high. How does your system handle conflict?**
  **A:** I surface it rather than silently picking a winner. The prioritizer takes *all* the signals as inputs, so a high anomaly score still pushes the risk band up even if the fault classifier says NORMAL — the conflict raises the risk, which is the safe direction. And because the answer cites each finding as a numbered source, the engineer sees both the NORMAL classification and the anomaly spike with their sources. There's also reconciliation logic in the backend (`_turn_payload`) for a specific known conflict: when the diagnosis analyzed a *recorded failure episode* from the historian, it explicitly states that and reports the machine's *current* live baseline, so the answer can't contradict the live cockpit verdict. The principle is: conflicting evidence elevates caution and gets disclosed, never hidden.
  🔑 *(Conflict ko surface karo, chhupao mat — anomaly spike risk band upar uthata hai, safe direction; dono signals cited dikhte hain.)*

- **Q5 (system-design): The whole chain runs synchronously before one LLM call. How would you make this real-time for 15 streaming assets?**
  **A:** It already is, partly — the SSE stream monitors all 15 assets, and the *fast deterministic path* (spec lookups, doc quotes) answers in <300ms with no LLM, while only a sustained alarm triggers the heavy ~11s deep diagnosis. To scale the deep path I'd: run the five agents concurrently where they're independent (predictor and rca don't depend on each other — `asyncio.gather`), cache the synthesis for repeated identical alerts (I already have a demo-cache layer keyed by prompt hash), and move the blocking LLM call fully async behind a queue so the stream never stalls — the backend already wraps `handle_alert` in `asyncio.to_thread`. The trace and findings are computed deterministically, so even if the LLM is slow, the structured answer is ready immediately.
  🔑 *(Independent agents parallel chalao, synthesis cache karo, LLM async queue me — structured answer to deterministic + instant hota hai.)*

- **Q6 (curveball): If the LLM is down, what does the engineer see — an error?**
  **A:** No — and this is a core design choice. The LLM is a *provider ladder* that never raises: demo-cache → Claude subscription → local SLM → a deterministic grounded template that echoes the cited findings in a structured shell. So if Claude is unreachable, the engineer still gets a usable, fully-grounded answer built from the ML outputs and retrieved sources — just less fluent prose. The facts are identical because they come from the agents, not the LLM. In a plant, "the AI is down" can't mean "no diagnosis" — degraded prose is acceptable, no answer is not.
  🔑 *(LLM down = template floor se grounded answer milta hai, facts wahi — "AI down" ka matlab "no diagnosis" kabhi nahi.)*

**Traps / kya NA bolna:**
- ❌ Don't oversell it as "autonomous agents that think" — it's a deterministic DAG of specialists + one synthesis call. Precision reads as senior.
- ❌ Don't claim LangGraph/CrewAI when you didn't use them — own the custom orchestrator and justify it.
- ❌ Don't say agents "vote" — the prioritizer *combines* signals via a transparent rule; conflict is surfaced, not voted away.

**Follow-up rabbit holes:** "How do you test a multi-agent system?" (per-agent unit tests + end-to-end eval harness `eval_run.py` + trace assertions). → "Token/cost budget per turn?" (one LLM call per turn by design; cache reduces it further). → "Multi-turn memory?" (`ConversationStore` + `Focus` — the focused asset persists across turns).

---

### 6. SSE-streamed live monitoring (60fps uPlot, rAF buffering, auto-diagnosis)

**Kya hai (Hinglish):** **SSE = Server-Sent Events** — ek one-way stream jisme server browser ko lagataar events bhejta hai (HTTP pe, WebSocket se simple, kyunki yaha sirf server→client chahiye). EDITH har asset ke real sensor rows ko replay karta hai stream me: har tick pe sensor values + status (normal/warning/alarm). Jab koi sensor threshold cross kare → `alert` event. Jab pehli baar sustained ALARM aaye → automatically EDITH ko diagnosis ke liye trigger kar deta hai (`diagnosis` event). Frontend pe **uPlot** (ek ultra-light canvas charting lib) 60fps pe draw karta hai, aur **rAF (requestAnimationFrame) buffering** se ticks ko smooth karke render karta hai — taaki har event pe re-render na ho aur frame drop na ho.

**Aapke project se connection:** `edith/backend/main.py` — `@app.get("/api/stream/{asset_id}")` ek `StreamingResponse` deta hai `text/event-stream` ke saath. `gen()` async generator real dense-table rows replay karta hai, `event: meta/tick/alert/diagnosis/end` emit karta hai. Threshold crossing pe alert + alert-history + logbook likhta hai. Pehle ALARM pe `SUP.handle_alert()` ko `asyncio.to_thread` me chalata hai (taaki blocking LLM call event loop ko na roke). Role filter bhi hai (operator/engineer/manager — G5).

**Interview Q&A:**

- **Q1 (basic): Why SSE and not WebSockets for live sensor monitoring?**
  **A:** Because the data flow is one-directional — server pushes sensor ticks and alerts to the browser; the browser doesn't need to push back on the same channel. SSE gives me exactly that over plain HTTP: it auto-reconnects, works through proxies, needs no special server, and is dead simple to consume with the browser's `EventSource`. WebSockets are for bidirectional, low-latency, chatty exchanges — overkill and more operational complexity for a push-only telemetry feed. I reserve the request/response channel (`/api/ask`) for engineer questions and keep the live feed on SSE.
  🔑 *(One-way push = SSE; HTTP pe simple, auto-reconnect. WebSocket bidirectional ke liye, yaha overkill.)*

- **Q2 (intermediate): What is rAF buffering and why do you need it at 60fps?**
  **A:** Sensor ticks can arrive faster or more irregularly than the screen refreshes (60Hz). If I redrew the chart on *every* incoming tick, I'd either drop frames or do wasted work between refreshes. So I buffer incoming ticks and flush them to the chart inside a `requestAnimationFrame` callback — the browser calls that exactly once per frame, right before paint. That decouples *data arrival rate* from *render rate*: I batch whatever arrived since the last frame and draw once, which keeps it smooth at 60fps even under bursty SSE. uPlot helps because it's a canvas renderer with almost no per-point overhead, unlike SVG charts that choke on thousands of points.
  🔑 *(Data har tick pe aata hai par screen 60Hz pe; rAF me batch karke ek frame me draw karo — smooth, no dropped frames.)*

- **Q3 (intermediate): Walk me through what happens from "sensor crosses alarm" to "engineer sees a diagnosis."**
  **A:** The stream generator computes each tick's per-sensor status against the spine thresholds. On a *fresh* crossing (status worsened vs the previous tick) it emits an `alert` event and persists it to alert history and the logbook. When the worst status first hits ALARM and we haven't already fired, it sets a one-shot flag and calls `SUP.handle_alert()` — but inside `asyncio.to_thread`, because that's a blocking call that may hit the LLM, and I must not block the event loop that's streaming to 15 assets. The resulting grounded diagnosis is emitted as a `diagnosis` event and also logged. So the engineer sees the chart go red, an alert banner, then an auto-generated diagnosis with risk and actions — without asking.
  🔑 *(Fresh crossing → alert event; pehla ALARM → handle_alert in a thread → diagnosis event. Auto, bina pooche.)*

- **Q4 (deep): The diagnosis call is ~11s. How do you keep the SSE stream responsive while it runs?**
  **A:** Two mechanisms. The diagnosis is dispatched via `asyncio.to_thread`, so the blocking supervisor/LLM work runs on a worker thread and the async generator keeps yielding ticks for that and other assets — the event loop never blocks. And it's fired as a one-shot (`fired_critical` flag) so I don't re-trigger an 11s job on every subsequent alarm tick. The fast paths (spec lookup, doc quote) don't touch the LLM at all and return in <300ms. So the architecture has a clear latency budget: streaming and fast answers stay sub-second; only the deep reasoning takes seconds, and it's offloaded so it never freezes the live view.
  🔑 *(11s diagnosis ko asyncio.to_thread me bhejo + one-shot flag; stream ticks chalti rehti hai, loop block nahi hota.)*

- **Q5 (system-design): This replays a CSV historian. How would the architecture change for *real* live sensors at 1kHz?**
  **A:** The contract — SSE of ticks + alerts + auto-diagnosis — stays; the source changes. I'd put a streaming ingest layer in front (Kafka / MQTT from the PLCs), do edge aggregation/downsampling because 1kHz raw is too much to push to a browser and most of it is redundant between frames — I'd send a windowed summary at display rate and keep the raw for the ML feature windows. Threshold detection moves to a stream processor (so it's not coupled to a browser connection), alerts go to a durable bus, and the browser SSE becomes a *subscriber* to that bus rather than the thing that replays a file. The ML feature extraction already works on windows, so it slots onto the aggregated stream cleanly.
  🔑 *(Real sensors pe: Kafka/MQTT ingest + edge downsample + stream-processor threshold detection; SSE bus ka subscriber ban jaata hai.)*

- **Q6 (curveball): What happens if the SSE connection drops mid-episode — does the engineer miss the alarm?**
  **A:** This is exactly why alerts aren't *only* in the stream. Every alert and every auto-diagnosis is persisted to `alerts_history.jsonl` and the logbook as it fires, independent of the live connection. So a dropped connection loses live *animation*, not the *record* — on reconnect the engineer can pull alert history and the logbook for that asset, and there's an alert-history report endpoint that reconstructs the timeline. SSE auto-reconnects via `EventSource` anyway. The design rule is: the stream is for *attention*, the persisted log is for *truth* — never make a safety alert depend on a live socket staying up.
  🔑 *(Alerts stream ke alawa logbook+history me bhi likhe jaate hain — connection drop = animation gaya, record nahi. Stream attention ke liye, log truth ke liye.)*

**Traps / kya NA bolna:**
- ❌ Don't say SSE is bidirectional or "like WebSockets but easier" without the one-way caveat — that's the defining difference.
- ❌ Don't claim you render every tick — the whole point is rAF *batching*; saying you redraw per-tick undercuts the 60fps claim.
- ❌ Don't forget the persistence point — if you say "alerts live in the stream" only, the dropped-connection question sinks you.

**Follow-up rabbit holes:** "Backpressure if the client is slow?" (buffer bounds, drop-to-latest for display while logging all). → "Why uPlot over Chart.js / D3?" (canvas, tiny, built for huge time-series, minimal GC). → "How do you test a streaming endpoint?" (Playwright captures the live UI; you also have screenshot verification in the repo).

---

### 7. Fast-path vs deep-path latency tradeoff (the two-speed brain)

**Kya hai (Hinglish):** EDITH ke do "speeds" hain. **Fast path (<300ms, LLM-free):** agar query ek exact spec/threshold lookup hai ("gearbox ka vibration alarm kaha pe trip karta hai?") ya ek SOP-doc content question hai, to LLM ko bilkul mat chuo — seedha equipment spine se ya retrieved doc se verbatim answer do. Hamesha sahi, instant. **Deep path (~11s, Claude):** open-ended diagnosis/RCA jaisi cheez ho to poora 5-agent chain + ek Claude synthesis call. Idea: 80% queries fast path se nikal jaayein (sasti + sahi + fast), aur Claude ki cost+latency sirf wahi kharch ho jaha genuinely reasoning chahiye.

**Aapke project se connection:** `edith/backend/main.py` — `/api/ask` me order: `_guardrail_answer()` (off-domain/unsafe → refuse), `_try_lookup_answer()` (threshold/spec → verbatim spine, latency_ms:1), `_try_doc_answer()` (SOP content → RAG quote), warna `SUP.handle_query()` (full deep path). `/api/focus/{asset_id}` bhi LLM-free fast bundle. EVAL_RESULTS: **p50 = 313ms, p90 = 12520ms** — ye literally fast-path/deep-path bimodal distribution dikhata hai. `vulcan/llm.py` ki provider ladder bhi part hai: cache(sub-ms) → Claude(~11s) → SLM → template.

**Interview Q&A:**

- **Q1 (basic): What's the fast path vs the deep path?**
  **A:** The fast path answers deterministic questions — exact threshold/spec lookups and SOP-document content — directly from the equipment spine or the retrieved doc, with no LLM call, in under 300ms. The deep path is for open-ended reasoning — a full diagnosis, root-cause analysis, a report — where I run the five-agent chain and make one Claude synthesis call, around 11 seconds. The router in `/api/ask` tries the fast paths first and only falls through to the deep path when the question genuinely needs reasoning.
  🔑 *(Fast path = exact lookups, no LLM, <300ms; deep path = reasoning, 5 agents + Claude, ~11s.)*

- **Q2 (intermediate): Why bother with the fast path? Couldn't Claude answer a threshold question too?**
  **A:** Claude could, but it'd be the wrong tool three ways. Cost: I'd burn an LLM call on something a dictionary lookup answers. Latency: 11 seconds for "what's the alarm threshold" is absurd when the spine has the exact number in a millisecond. And *correctness*: for an exact value, reading it verbatim from the spine is guaranteed right, whereas asking an LLM introduces a non-zero chance it paraphrases the number wrong. The fast path is faster, cheaper, *and* more correct for factual lookups. Reserving the LLM for genuine reasoning is the whole point.
  🔑 *(Threshold ke liye LLM = mehenga, slow, aur galti ka risk; spine lookup = instant + guaranteed sahi. LLM sirf reasoning ke liye bachao.)*

- **Q3 (intermediate): Your p50 is 313ms but p90 is 12.5s. Explain that gap to me.**
  **A:** That gap is the fast-path/deep-path split showing up in the latency distribution — it's bimodal, not a long tail from one slow operation. The median query hits the fast path (spec lookup, doc quote, guardrail refusal) and returns in ~300ms. The slow tail is the deep-path queries that fire the full agent chain plus a Claude call. So p50 reflects "most questions are factual and instant," and p90 reflects "the genuinely hard diagnoses cost real reasoning time." I'd actually report it as two distributions rather than one, because averaging them hides the design.
  🔑 *(p50/p90 gap = bimodal distribution; median fast path, tail deep path — ek slow operation ka tail nahi.)*

- **Q4 (deep): How does the router decide fast vs deep? What's the risk of misrouting?**
  **A:** It's a cascade of cheap classifiers in `/api/ask`: first a guardrail check (unsafe config request, off-domain, unknown equipment, ambiguous → refuse/clarify), then a lookup-hint matcher (word-boundary regex for "threshold," "limit," "alarm at," etc.) that routes to the verbatim spine answer, then a doc-hint matcher for SOP content, and only then the deep path. The risk is a *false-fast*: routing a question that needs reasoning to a verbatim lookup, giving a thin answer. I mitigate by making the fast-path triggers conservative — they require specific lookup keywords and a resolvable asset; anything ambiguous falls through to the deep path, which is the safe default. The opposite error (deep-pathing a simple lookup) just costs latency, not correctness.
  🔑 *(Router = guardrail → lookup-regex → doc-hint → warna deep. Fast-path triggers conservative; doubt ho to deep path, safe default.)*

- **Q5 (system-design): The provider ladder (cache → Claude → SLM → template) — how does that interact with the fast/deep split, and how do you decide timeouts?**
  **A:** The fast/deep split decides *whether* to call an LLM at all; the provider ladder decides *which* LLM serves a deep-path call and guarantees it never fails. On a deep call it tries the demo-cache (sub-ms, keyed by prompt hash), then Claude on the Max OAuth token with a hard timeout, then a local SLM, then a deterministic grounded template that always returns. Each rung has a hard timeout so it *fails forward fast* rather than hanging — I'd rather degrade to a template in a bounded time than block. The Claude timeout is the main tuning knob: long enough for a real synthesis (~11s), short enough that a stalled call falls to the template before the engineer gives up.
  🔑 *(Fast/deep decide karta hai LLM call karna hai ya nahi; ladder decide karta hai kaunsa LLM + never-fail. Har rung hard timeout = fail-forward-fast.)*

- **Q6 (curveball): Isn't a hard-coded keyword router brittle? A paraphrased question could miss the fast path.**
  **A:** Yes, and I'd own that it's a pragmatic heuristic, not a learned router. The saving grace is the *failure direction*: a missed fast-path doesn't give a wrong answer — it falls through to the deep path, which still answers correctly, just slower. So brittleness costs latency, not correctness. If misrouting became a real problem I'd replace the keyword cascade with the lightweight intent classifier I already use elsewhere (a small fast model that tags intent), keeping the deterministic answer generation but learning the routing. The principle I'd defend: make the cheap path *conservative* so its errors are recoverable, and let the safe default absorb the misses.
  🔑 *(Keyword router brittle hai par miss = slow, not wrong — deep path absorb karta hai; aage ek small intent-classifier se route karo.)*

**Traps / kya NA bolna:**
- ❌ Don't present p90=12.5s as a *problem* — it's *by design* (the deep path costs reasoning time). Frame it as a bimodal distribution.
- ❌ Don't say "everything goes through the LLM" — the fast path explicitly doesn't, and that's a selling point.
- ❌ Don't claim the router is ML — it's a keyword/regex cascade today; be honest and describe the intent-classifier upgrade.

**Follow-up rabbit holes:** "Caching strategy / cache invalidation?" (prompt-hash keyed; invalidate when underlying data changes). → "How do you set the Claude timeout empirically?" → "p99 and worst case?" (template floor bounds it). → "Streaming the deep answer token-by-token to hide latency?" (good UX answer to offer).

---

### 8. The dataset & "physics-grounded" claim (1.25M rows, 120 episodes, eval set)

**Kya hai (Hinglish):** Tata ne real data nahi diya, to aapne ek **synthetic but physics-grounded** dataset khud banaya. "Physics-grounded" matlab numbers random nahi — degradation patterns real failure physics follow karte hain (bearing wear ka BPFO vibration signature, oil contamination ka viscosity drop, etc.), aur thresholds real ISO/IEC/NEMA standards se traced hain. Size: ~1.25M rows (36 CSVs), 15 assets × 8736 rows (ek saal hourly), 120 run-to-failure episodes (8–11 per asset), 80 knowledge docs (manuals/SOPs/RCA), aur ek 310-item eval set (Hinglish + adversarial refusal cases included). Ek "ground truth spine" sab ko link karta hai (asset ↔ scenario ↔ RCA ↔ spares) — 0 orphan references.

**Aapke project se connection:** `round_2/dataforge/datasets/steel-maintenance-flagship/`. `ground_truth_spine.json` har asset/sensor/threshold/scenario ka source of truth — fast-path lookups isi se aate hain. `condition_monitoring/by_equipment/*.csv` (per-asset dense tables, ML training data), `rul_trajectories_long.csv` (RUL target). EDITH ka EDITH-DataForge connection: ye aapka data-quality platform hai jo dataset ko 0-orphan-references tak validate karta hai. SUBMISSION_DOCUMENT: "0 orphan references across all modalities," "876 grounding refs validated, 0 dangling."

**Interview Q&A:**

- **Q1 (basic): You built your own dataset. Why, and what does "physics-grounded" mean?**
  **A:** The hackathon didn't provide real plant data, so I generated a synthetic dataset — but "physics-grounded," not random noise. Each sensor's degradation follows the actual failure physics of that mode: a bearing developing outer-race wear shows the right BPFO vibration signature rising over its episode; oil contamination shows viscosity dropping with particle count climbing. Thresholds are traced to real ISO/IEC/NEMA standards. So the ML models learn realistic patterns and the answers cite real standards — it behaves like plant data even though it's generated.
  🔑 *(Real data nahi mila to synthetic banaya — par physics aur ISO/IEC standards pe grounded, random nahi.)*

- **Q2 (intermediate): How do you defend a model trained on synthetic data — won't it just learn your generator's rules?**
  **A:** That's the central honest caveat and I state it openly: a model trained on synthetic data validates the *system architecture and the pipeline*, not real-world accuracy — it would need site calibration before production, which the report says explicitly. What it *does* prove: the end-to-end flow works (ingest → ML → RAG → agents → grounded answer), the grounding discipline holds, and the failure-physics signatures are learnable. To reduce "learning my own generator," I added realistic noise, soft-capped the RUL labels, used leak-safe splits, and built the eval set to include adversarial and out-of-scope cases the generator didn't trivially solve. But I wouldn't claim production accuracy from it — I'd claim a validated, calibratable architecture.
  🔑 *(Synthetic data system+pipeline prove karta hai, real accuracy nahi — site calibration chahiye; ye openly bolo.)*

- **Q3 (intermediate): Tell me about the eval set — what's in 310 items and why include adversarial cases?**
  **A:** It spans every PS category — lookup, diagnosis, RCA, RUL, risk, procurement, report — plus deliberately hard cases: 17 adversarial, 13 clarification, 5 out-of-scope, and 30 Hinglish queries. The adversarial and out-of-scope items exist because in a safety system, *knowing when not to answer* matters as much as answering. An item like "increase the alarm threshold so it stops beeping" must be *refused*, not helpfully executed. So my eval scores guardrail behavior — does it refuse/clarify instead of confidently guessing — as a first-class metric, not just fact recall. That tests the system's judgment, not just its knowledge.
  🔑 *(Eval set me adversarial + out-of-scope + Hinglish — kyunki "kab NA jawab dena" bhi utna hi important hai safety me.)*

- **Q4 (deep): "Zero orphan references" — what does that mean and why does it matter for a RAG/agent system?**
  **A:** It means referential integrity across all the data modalities: every scenario points to a real asset, every RCA report to a real scenario, every recommended spare part to a real catalog entry, every grounding citation to a real document — 876 grounding refs validated, zero dangling. It matters because my agents *chain* these references: the diagnosis matches a scenario, which the RCA agent expands, whose resolution the recommender turns into spares. One dangling reference and an agent grounds a finding in something that doesn't exist — a hallucination by data error rather than model error. I built EDITH-DataForge specifically to validate this integrity, because in a grounded system the data graph *is* the source of truth.
  🔑 *(0 orphan = har reference real target pe point karta hai; agents references chain karte hain, ek dangling = data-error hallucination.)*

- **Q5 (system-design): How would you replace this synthetic dataset with a real Tata historian without rewriting the system?**
  **A:** The whole system reads through the `ground_truth_spine.json` contract and the dense-table CSV schema — so the integration point is a *data adapter*, not the agents. I'd write a connector that maps the plant historian's tags to my sensor schema and the asset registry to the spine, ingest the real condition CSVs into the same `by_equipment` shape, re-run the trainers (one trainer call per model family — the artifact contract is unchanged), and re-embed the real manuals/SOPs into ChromaDB. The agents, the orchestrator, the gate, the fast/deep router — none of that changes, because they depend on the *contract*, not the data origin. That clean seam is exactly why I put a spine contract in the middle.
  🔑 *(Spine contract + CSV schema = integration seam; real historian ke liye sirf data adapter + retrain, agents/orchestrator same.)*

- **Q6 (curveball): A judge says "synthetic data is a cop-out — real teams handle messy real data." How do you respond?**
  **A:** I'd agree real data is messier and meet it head-on: I built the dataset *to be calibratable*, with a documented schema, a validation layer that enforces zero orphan references, leak-safe splits, and disclosed noise — precisely so swapping in messy real data is a connector, not a rebuild. And I'd argue the *hard* part of this problem isn't owning data — it's the grounded-reasoning architecture that won't hallucinate on safety-critical facts, which is data-source-agnostic. I controlled the data so I could prove the architecture rigorously; the architecture is what transfers to messy reality. Given real Tata data and calibration time, the same system runs — that's the design intent stated in the submission.
  🔑 *(Synthetic = controlled proof of architecture; real data = ek connector dur, rebuild nahi. Hard part data nahi, grounded-reasoning hai.)*

**Traps / kya NA bolna:**
- ❌ Don't claim production-grade accuracy from synthetic data — claim a *validated, calibratable architecture*. Overclaiming here is the fastest way to lose credibility.
- ❌ Don't say the data is "real" or hide that it's synthetic — own it confidently with the physics-grounding + standards-tracing justification.
- ❌ Don't undersell the eval set as "just test cases" — the adversarial/guardrail dimension is a senior-level insight; lead with it.

**Follow-up rabbit holes:** "How exactly did you generate the degradation curves?" (per-mode signature + noise + run-to-failure trajectory). → "How do you validate the generator itself?" (orphan-reference check, distribution sanity, standards cross-check). → "EDITH-DataForge — what does it score?" (dataset quality 0–100 + readiness % — the data-trust layer).

---

### 9. Six PS output types & the engineer-first UX

**Kya hai (Hinglish):** Problem statement ne 6 output types maange the: (1) **diagnosis**, (2) **root cause**, (3) **RUL estimate**, (4) **risk band**, (5) **prioritized repair steps**, (6) **downloadable report (PDF)**. EDITH ke har answer me ye structured sections aate hain (`_SECTION_META` order me — Diagnosis → Root Cause → RUL → Risk → Recommended Actions). PDF Playwright se render hota hai (HTML→PDF, headless Chromium). UX engineer-first hai: har answer ek "verdict + kya ho raha + kitna urgent + kya karo + parts + agar ignore kiya to kya" structure follow karta hai, plain language me, role-aware chips ke saath.

**Aapke project se connection:** `main.py` — `_SECTION_META`/`_fmt_section()` har finding ko ek clean PS-section card me badalte hain. `/api/report` (incident/decision/alert kinds) report banata hai, `/api/report/{rid}/pdf` Playwright async API se A4 PDF render karta hai (custom CSS, EDITH branding). `/api/focus/{asset_id}` engineer-first guided bundle (`_focus_state`: healthy/watch/act_within/act_now) + state-gated action chips (`_CHIPS`). Confidence label har answer pe (`confidence_label`, `reasoning_mode` badge — fast grounded / edith-deep).

**Interview Q&A:**

- **Q1 (basic): The PS wanted six output types. How does one answer produce all of them?**
  **A:** The five-agent chain naturally maps to them: DiagnosisAgent → diagnosis, RCAAgent → root cause, PredictorAgent → RUL estimate, PrioritizerAgent → risk band, RecommenderAgent → prioritized repair steps. Each agent's finding becomes a clean section card in a fixed order, and the sixth output — a downloadable PDF — is rendered from that same assembled report. So I don't run six separate flows; one diagnosis turn produces all six, which is also why they're internally consistent (the risk band reflects the same RUL the predictor computed).
  🔑 *(Ek diagnosis turn → 5 agents → 5 sections + PDF = chhe outputs, sab internally consistent.)*

- **Q2 (intermediate): How is the PDF generated, and why that approach?**
  **A:** I render the report markdown to HTML with branded CSS and then use Playwright's headless Chromium `page.pdf()` to produce an A4 PDF — async, so it doesn't block. I chose browser-rendered PDF over a library like ReportLab because the report has tables, headings, and styling, and Chromium's print engine gives pixel-perfect, well-paginated output for free — the same HTML I'd show on screen becomes the document. It's also keyless and runs locally, which fit my constraints.
  🔑 *(Markdown→HTML→Playwright headless Chromium PDF — tables/styling free, screen aur document same HTML se.)*

- **Q3 (intermediate): What does "engineer-first UX" mean concretely — give me the structure of an answer.**
  **A:** Every focused answer follows a decision-shaped order: the *verdict* (one-line health headline), *what's happening* (the fault in plain language), *how urgent* (a focus state: healthy / watch / act-within / act-now, derived from health + RUL band + safety class), *what to do* (state-gated steps — a healthy machine gets preventive checks, not repair steps), *parts* (with lead times), and *if unaddressed* (the consequence). I also show role-aware follow-up chips — an act-now state surfaces "walk me through safe isolation," a healthy state surfaces "when's the next check." The point is the engineer reads top-to-bottom and knows what to *do*, not just what's wrong.
  🔑 *(Verdict → kya ho raha → kitna urgent → kya karo → parts → ignore kiya to kya; state-gated, role-aware chips.)*

- **Q4 (deep): You show a confidence label and reasoning-mode badge. Walk me through what they mean and the honesty design behind them.**
  **A:** Every answer carries a `reasoning_mode` badge — "fast grounded" (deterministic, no LLM) or "edith-deep" (Claude synthesis, cached or live) — so the engineer knows *how* the answer was produced. And a `confidence_label` that's deliberately honest: for deterministic answers I label "grounded (deterministic — every claim cited)" and I explicitly *do not* emit a 100% number, because a fake "100% confident" is dishonest. For LLM answers that passed the faithfulness gate, I show "verified" with the actual faithfulness score, or "unverified" below threshold. The design rule is that the UI never projects false certainty — deterministic gets "grounded," not "100%."
  🔑 *(reasoning_mode = kaise bana; confidence_label honest — deterministic ko "grounded" bolo, 100% kabhi nahi.)*

- **Q5 (system-design): State-gated actions — a healthy machine gets preventive steps, not repair steps. Why is that a safety/UX decision, not just polish?**
  **A:** Because showing repair steps on a healthy machine invites *unnecessary intervention* — and in a plant, opening up a healthy bearing is itself a risk (you can introduce contamination, misalignment, downtime). So the focus state gates what's offered: healthy → "continue monitoring, next scheduled check"; watch → "increase monitoring, check spare availability"; act-now → "safe isolation steps, who to inform." The system's *recommendation surface* matches the actual urgency, so it never nudges an engineer toward over-maintenance, which is a real failure mode of naive condition-monitoring tools that alarm on everything.
  🔑 *(Healthy machine pe repair steps dikhana = unnecessary intervention ka risk; state-gating over-maintenance rokta hai — safety decision.)*

- **Q6 (curveball): If everything is sectioned and templated, where's the actual intelligence — couldn't this be a form?**
  **A:** The *presentation* is structured, but the content under each section is computed, not filled-in. The diagnosis section holds an ML classifier's prediction over a real sensor window; the RUL is a regressor's output; the risk band is a multi-signal computation; the recommendations are scenario-matched and spare-availability-aware; and the prose synthesis plus faithfulness gate are LLM-driven. A form has fixed answers; EDITH's sections change with the live sensor state, resolve the right scenario, reorder by risk, and flag low-confidence claims. The fixed *structure* is a UX choice for decision speed; the *intelligence* is everything that fills it.
  🔑 *(Structure fixed hai par content live ML+RAG+reasoning se aata hai — form ke answers fixed hote hain, EDITH ke sensor-state pe badalte hain.)*

**Traps / kya NA bolna:**
- ❌ Don't show or claim "100% confidence" — your own code refuses to emit it for deterministic answers; that honesty is a *feature*, say so.
- ❌ Don't describe it as "templated answers" without the "content is computed" follow-through — sounds like a form otherwise.
- ❌ Don't forget the over-maintenance insight — state-gating is a genuinely senior product-safety point.

**Follow-up rabbit holes:** "How do you handle a report for an asset with no alert history?" (falls back to incident report). → "Localization / Hinglish in the UI?" (eval set has Hinglish; answers stay grounded). → "Audit trail for compliance?" (logbook.jsonl + alerts_history.jsonl + reasoning trace per turn).

---

### 10. Honest metrics & how to handle the "what's your accuracy" question

**Kya hai (Hinglish):** Ye section sirf aapke liye — interview survival. EDITH ka deterministic eval harness ne **kam fact-recall** dikhaya (~0.13 strict string-match pe, n=213 answerable). Ye number scary lagta hai par iska reason **harness brutal hai**, not necessarily ki system kharab hai: strict exact-fact matching + forbidden-claim gate, **no LLM judge** (fully reproducible rakhne ke liye). Matlab agar EDITH "RUL ~40 cycles" bole aur gold "40.2 cycles" ho, strict match fail ho sakta hai. Isliye **aapko ye number defend nahi, contextualize karna hai** — kaha strong ho (architecture, guardrails, grounding, latency), aur kaise sahi se measure karoge.

**Aapke project se connection:** `edith/EVAL_RESULTS.md` — fact recall 0.13, forbidden-claim violations only **2** (matlab system confidently-wrong claims bahut kam karta hai — ye *acha* hai), guardrail behavior 0.341, latency p50/p90 = 313ms/12.5s, Hinglish recall (0.167) > English (0.125). `eval_run.py` harness (strict fact matching, no LLM judge).

**Interview Q&A:**

- **Q1 (the question you fear): What's your accuracy / how well does it work?**
  **A:** Let me be precise about what I measured. I built a fully deterministic, reproducible eval harness — strict fact matching plus a forbidden-claim gate, no LLM judge — over a 254-item gold set. On that harness the strict fact-recall is low, around 0.13, and I'll be honest about why: strict string matching penalizes correct-but-differently-phrased answers — "RUL about 40 cycles" vs a gold "40.2" — so it's a *lower bound*, not a true accuracy. What I'm genuinely proud of in the same run: only 2 forbidden-claim violations across 254 items, meaning the system almost never makes a confident wrong statement — which in a safety setting matters more than recall. If I were productizing this, my next step is an LLM-judge eval plus a grounding-reference match to measure *semantic* correctness, which the strict harness undercounts.
  🔑 *(0.13 strict-match ka lower bound hai, real accuracy nahi; asli win = sirf 2 confident-wrong claims; next step = LLM-judge eval.)*

- **Q2: Why didn't you just use an LLM-as-judge to get a better-looking number?**
  **A:** Deliberately — I wanted the headline eval to be *fully reproducible and keyless*, so anyone can rerun `eval_run.py` and get the identical number with no API and no judge variance. An LLM judge would have given a more flattering, semantically-fair score, but it's non-deterministic and costs calls. So I chose a harsh-but-honest deterministic harness for the baseline and would *add* the LLM-judge as a complementary view, clearly labeled. I'd rather show a conservative reproducible number than a generous unreproducible one.
  🔑 *(LLM-judge accha number deta par non-deterministic; maine reproducible+keyless harness chuna — conservative par honest.)*

- **Q3: What does the latency split tell you about real-world readiness?**
  **A:** The p50 of 313ms says the common case — factual lookups and refusals — is genuinely instant, which is what an engineer on the floor needs most of the time. The p90 of 12.5s is the deep-reasoning tail, which is acceptable for an occasional full diagnosis but is my optimization target: streaming the answer, parallelizing the independent agents, and caching would pull that down. So the system is interaction-ready for the high-frequency case and has a clear, bounded path to improve the rare slow case.
  🔑 *(p50 313ms = common case instant; p90 12.5s = rare deep diagnosis, optimization target — stream/parallel/cache.)*

- **Q4 (curveball): Honestly — is this production-ready?**
  **A:** No, and I'd never claim it is — it's a hackathon prototype on synthetic data, and the submission says site calibration is required before production. What it *is*: a validated end-to-end architecture for grounded, low-hallucination maintenance reasoning, with the safety-critical properties (sourced facts, faithfulness gating, guardrail refusals, fail-soft LLM ladder) actually built and tested, not just slides. Production readiness would need real plant data + calibration, the LLM-judge eval, prediction intervals on RUL, and hardening of the streaming layer. I'm comfortable saying "validated architecture, clear path to production" — that's the honest claim and it's a strong one.
  🔑 *(Production-ready nahi — prototype on synthetic data; par architecture validated + safety properties real, "clear path to production" honest claim hai.)*

**Traps / kya NA bolna:**
- ❌ NEVER quote a fabricated high accuracy. If they later ask to see the eval, a made-up number destroys you. The 0.13 + context is *survivable and credible*; a fake 0.9 is not.
- ❌ Don't get defensive about the low recall — *explain the harness*, pivot to the 2-forbidden-violations win and the LLM-judge plan. Calm contextualization reads as senior.
- ❌ Don't say "the eval is just wrong" — say "the eval is a strict lower bound; here's the right way to measure semantic correctness."

**Follow-up rabbit holes:** "Show me the eval harness." (it's `eval_run.py` — strict fact match + forbidden-claim gate; walk them through it). → "How would you build the LLM-judge eval?" (rubric, grounding-ref match, calibration against human labels). → "What's the single thing you'd improve first?" (semantic eval + RUL prediction intervals — answer ready).

---

## 3-line summary
EDITH is an agentic steel-plant maintenance copilot whose core thesis is **separation of concerns**: deterministic ML (LightGBM fault/RUL + IsolationForest anomaly) and a spine-grounded data contract own all *facts*, a five-agent supervisor DAG (Diagnosis→RCA→RUL→Prioritize→Recommend) orchestrates them, and a single Claude call only writes the prose — which a local DeBERTa-NLI faithfulness gate then verifies claim-by-claim against numbered sources. Retrieval is two-stage hybrid RAG (bge-small dense → FlashRank/MiniLM cross-encoder rerank → ChromaDB), and the system is two-speed: a <300ms LLM-free fast path for spec/SOP lookups vs a ~11s deep reasoning path, with a fail-soft provider ladder so the engineer always gets a grounded answer. The honest weak spot is the strict deterministic eval's low fact-recall (~0.13, a lower bound by design) — handle it by leading with architecture, the near-zero confident-wrong-claim rate (2/254), and the LLM-judge eval as the next step.

## Top 5 highest-probability interview questions for this cluster
1. **"You say zero hallucination but an LLM writes the answer — defend that."** → §1 Q6 + §2: facts are pre-computed/sourced, the NLI gate flags drift; the precise claim is "facts grounded + unsupported claims flagged," not "LLM perfect."
2. **"Why two-stage retrieval (bge-small + FlashRank rerank) instead of plain cosine vector search?"** → §3: bi-encoder = cheap wide recall, cross-encoder rerank = precise ordering; cosine measures topic, not answer-relevance.
3. **"How does the NLI faithfulness gate actually work, and why flag on contradiction not low entailment?"** → §2 Q3/Q4: premise=source/hypothesis=claim, max over cited sources, contradiction = hallucination while neutral = honest paraphrase.
4. **"What's RUL, why LightGBM, and where does IsolationForest fit?"** → §4: supervised regression for remaining cycles; IsolationForest is *unsupervised* anomaly detection fit on normal-only rows as an independent cross-check for unseen faults.
5. **"Walk me through the fast-path vs deep-path tradeoff — and explain your p50 313ms / p90 12.5s."** → §7: bimodal by design — LLM-free deterministic lookups (<300ms) vs full 5-agent + Claude reasoning (~11s); misrouting costs latency, not correctness.
