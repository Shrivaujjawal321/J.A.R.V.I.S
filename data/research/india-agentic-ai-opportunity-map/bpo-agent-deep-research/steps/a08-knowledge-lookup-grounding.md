# Step A08 — Knowledge Lookup & Grounding (finding the exact right policy/answer, no guessing)

> Deep-research dossier for an India-market, multilingual (Hindi + regional + Hinglish), RBI/IRDAI/DPDP-compliant, action-taking voice+chat contact-center agent for mid-market BPOs.
> Scope: ONLY the knowledge-lookup-and-grounding micro-step. This is the "do not guess — find the exact authoritative answer and say it faithfully" muscle.
> Date: 2026-06-24. Tags: [sourced] vs [estimate].

---

## 0. Why this step is the single highest-leverage step in the whole agent

Every other step (intent, action-taking, empathy) can be "good enough" and the call still succeeds. Knowledge lookup is **binary and adversarial**: a single confidently-wrong policy statement ("yes ma'am, foreclosure pe koi charge nahi hai") is a mis-selling event. Under RBI's draft Directions on Advertising, Marketing and Sales (final norms effective **1 Jan 2027**), a misleading/under-disclosed statement forces the bank to **refund + compensate** the customer ([Angel One, 2026](https://www.angelone.in/news/economy/rbi-issues-new-rules-to-curb-mis-selling-of-financial-products-norms-effective-from-january-1-2027); [Deccan Chronicle, 2026](https://www.deccanchronicle.com/amp/business/rbi-tightens-norms-to-curb-mis-selling-of-financial-products-1963800)). So the grounding step is not "answer quality" — it is **regulatory liability containment**. The agent's job here is to be *right or silent*, never *confidently wrong*.

Naive RAG pipelines fail at retrieval roughly **40% of the time** ([Techment, RAG in 2026](https://www.techment.com/blogs/rag-in-2026/)). That 40% is the enemy.

---

## 1. Human micro-steps — what a skilled BPO agent ACTUALLY does

Decomposed to the smallest atomic cognitive/emotional/mechanical moves a senior agent performs when a customer asks "mere loan ka foreclosure charge kitna hai?":

1. **Parse the answerable question out of the messy turn.** The customer rarely asks cleanly — "haan wo jo paisa pehle bharne pe lagta hai na, kitna?" The agent silently normalizes this into a *retrievable query*: "prepayment/foreclosure charge, personal loan, floating vs fixed."
2. **Classify the knowledge type.** Is this (a) static policy (foreclosure charge schedule), (b) account-specific fact (this customer's exact rate), (c) procedural ("how do I close the loan"), or (d) regulatory/legal ("can you charge me at all")? Different sources, different bins. A human knows instantly which bucket.
3. **Pick the authoritative source, not the convenient one.** Senior agents know the *MITC / sanction letter / product master* is canonical, while a colleague's WhatsApp tip or last month's circular is **stale**. They prefer the document with effective-date authority.
4. **Disambiguate the variant.** "Foreclosure charge" differs by product (PL vs HL), customer segment (staff vs retail), scheme code, vintage, fixed vs floating, and whether the customer is an MSME (RBI bars foreclosure charges on floating-rate loans to individuals + MSMEs). The agent narrows to the **one applicable row**.
5. **Resolve effective-date / version.** "Is this the charge as of today, or the old schedule?" Agents check the circular date and the customer's onboarding date — old loans may be grandfathered.
6. **Locate the exact clause / number.** Not a paraphrase — the literal figure ("4% of outstanding + GST" or "Nil for floating-rate individual loans").
7. **Cross-check for contradiction.** If the product sheet says 4% but a recent RBI circular says Nil for this category, the agent knows the **regulation overrides** the product sheet. This is a precedence/conflict-resolution move.
8. **Calibrate confidence — and decide guess vs verify vs abstain.** The crux. A good agent *feels* the boundary of their knowledge. If unsure, they say "ek second sir, main confirm karke batati hoon" and put the customer on hold / check the screen — they DON'T guess. The willingness to say "I don't know yet" is the senior skill.
8b. **Suppress the plausible-but-wrong answer.** A human resists the urge to give the answer that *sounds* right. This is active inhibition, not absence of knowledge.
9. **Translate clause-language into customer-language.** Convert "prepayment charge as per clause 7.3 of MITC" into "foreclosure pe 4% lagega plus GST, lekin aapka floating-rate loan hai toh kuch nahi lagega."
10. **State it with appropriate hedging + the source-of-authority.** "As per our current policy…" — the human implicitly cites authority so the answer is defensible.
11. **Disclose the limit honestly.** "Yeh general charge hai; aapke specific account pe exact figure main account check karke confirm karti hoon" — separating the *policy fact* from the *account-specific fact*.
12. **Log/remember what was answered** so the same call doesn't re-ask, and so a wrong answer is traceable for QA.

The five hardest, most human moves: **#3 (authoritative-source instinct), #7 (regulation-overrides-product conflict resolution), #8 (calibrated abstention), #8b (suppress plausible-wrong), #11 (policy-fact vs account-fact separation).**

---

## 2. Agent approach — how a 2026 AI agent performs each micro-step

| Human micro-step | 2026 agentic technique | Model / pattern |
|---|---|---|
| 1. Query normalization | **Query rewriting / decomposition** before retrieval; LLM rewrites the noisy ASR transcript into a clean retrieval query, expands abbreviations, resolves coreference from dialog state | Claude / GPT-class rewriter; multi-query expansion (agentic retrieval breaks one query into focused subqueries — [Azure agentic retrieval](https://learn.microsoft.com/en-us/azure/search/agentic-retrieval-overview)) |
| 2. Knowledge-type classification | **Router / query-type classifier** routes to the right index: policy-KB vs account-API vs procedure-KB vs regulation-KB | Small classifier (fine-tuned encoder or Haiku-class) → metadata-filtered retrieval |
| 3. Authoritative-source selection | **Metadata-filtered hybrid retrieval** with `source_authority` and `effective_date` fields; only canonical docs in the index; pre-curation removes WhatsApp-tier sources | Hybrid dense+BM25 with metadata filters; **Contextual Retrieval** (Anthropic) so each chunk carries doc-level authority context |
| 4. Variant disambiguation | **Metadata faceting + agentic clarification**: filter by `product`, `segment`, `scheme_code`; if multiple candidates survive, ask ONE disambiguating question or read account context | Self-querying retriever; agent loop that inspects retrieved candidates and detects "need to narrow" |
| 5. Effective-date / version | **Temporal metadata filter** `effective_from <= today AND (effective_to IS NULL OR >= today)`; grandfathering via `customer_onboard_date` join | Filtered vector search; recency-aware reranking |
| 6. Exact-clause location | **High-precision reranking** (cross-encoder) over top-k, then **span-level extraction** of the literal clause | Cohere Rerank 3.5 / BGE-reranker-v2-m3; ColBERT multi-vector for token-level match on numbers |
| 7. Conflict resolution / precedence | **Precedence-ranked retrieval + LLM conflict adjudication**: regulation index weighted above product index; reasoning step flags contradiction and applies "regulation overrides" rule | Agentic RAG reasoning loop (System-2); rule-injected precedence in the prompt |
| 8. Calibrated abstain | **Groundedness/faithfulness gate + learned refusal**: generate answer with mandatory citations, then a verifier checks every claim is supported by retrieved spans; if unsupported → abstain ("let me verify / transfer") | Self-RAG reflection tokens; **CRAG** (retrieval-quality grader triggers corrective re-search); grounded-with-verifiable-rewards trained model; LLM-as-judge groundedness check ([RAG Triad](https://www.snowflake.com/en/engineering-blog/benchmarking-LLM-as-a-judge-RAG-triad-metrics/)) |
| 8b. Suppress plausible-wrong | **Context-only constraint** ("answer ONLY from provided sources; if not present, say you'll verify") + **claim-level verification** (RT4CHART-style: decompose answer into claims, enforce context-only evidence) | Strict grounded-generation prompt + post-hoc claim verifier ([RT4CHART concept](https://arxiv.org/html/2603.27752v1)) |
| 9. Clause → customer language | **Grounded generation with style control**: faithful paraphrase into Hinglish at the customer's register, numbers preserved verbatim | Multilingual LLM (Sarvam-class for Indic register) constrained to cited spans |
| 10. State with authority hedge | **Citation-attached generation**: every factual sentence carries an inline source id; spoken version uses "as per current policy" framing | Sub-sentence citation ([arXiv 2509.20859](https://arxiv.org/pdf/2509.20859)); LAQuer localized attribution |
| 11. Policy-fact vs account-fact split | **Tool-typed grounding**: policy facts from KB (RAG), account facts from a typed account API/tool call — never mixed; agent labels each | Tool-calling + RAG hybrid; structured-output enforcing source-of-each-fact |
| 12. Log / traceability | **Citation trail logged** with retrieved chunk ids, scores, version, timestamp for QA + audit | Observability layer (LangSmith/Langfuse) + audit store |

**Headline architecture: Agentic, contextual, hybrid, reranked RAG with a mandatory groundedness gate and learned abstention.** Not vanilla "embed-and-stuff."

---

## 3. Tooling — concrete 2026 stack

**Ingestion & chunking**
- **Anthropic Contextual Retrieval** (contextual embeddings + contextual BM25): prepend an LLM-generated doc-level context blurb to each chunk before embedding/indexing. Reduces retrieval errors **49%** (contextual embeddings + contextual BM25) and up to **67%** with reranking added ([Anthropic via AWS/DataCamp](https://www.datacamp.com/tutorial/contextual-retrieval-anthropic)). Critical for policy docs where a chunk "4% of outstanding" is meaningless without "foreclosure charge, personal loan, floating rate."
- **Late chunking** (Jina v3) for long MITC/circular PDFs to preserve cross-chunk context.
- Rich metadata schema per chunk: `doc_type, product, segment, scheme_code, effective_from, effective_to, source_authority, regulator_ref, language, version`.

**Embeddings (multilingual + Indic)**
- **Cohere embed-v4** (MTEB ~65.2) or **BGE-M3** (MTEB ~63.0, 100+ langs, self-hostable for DPDP data-residency) as the workhorse ([Milvus 2026 guide](https://milvus.io/blog/choose-embedding-model-rag-2026.md)).
- **Indic-specialist**: **Vyakyarth-1** (Ola Krutrim, 10 Indian langs incl. Hindi) or **AI4Bharat/IndicIRSuite (Indic-ColBERT)** for Hindi/regional and code-mixed queries where multilingual models underperform ([Vyakyarth](https://ai-labs.olakrutrim.com/models/Vyakyarth-1-Indic-Embedding); [IndicIRSuite, arXiv 2312.09508](https://arxiv.org/pdf/2312.09508); [DeepRAG Hindi, arXiv 2503.08213](https://arxiv.org/html/2503.08213v1)).

**Retrieval**
- **Hybrid**: dense (vector) + sparse (BM25/SPLADE) with weighted rank fusion (higher weight to dense).
- **Vector DB**: Qdrant / Weaviate / Milvus (self-host for DPDP residency) or Azure AI Search (agentic retrieval built-in).
- **ColBERT/multi-vector** (PLAID) for number-exact policy matching where bag-of-vectors beats single-vector.

**Reranking**
- **Cohere Rerank 3.5** (hosted, strong multilingual) or **BGE-reranker-v2-m3 / Jina Reranker v2** (self-host). Rerankers add **+5 to +15 NDCG@10** ([Local AI Master, 2026](https://localaimaster.com/blog/reranking-cross-encoders-guide)).

**Agentic orchestration**
- **LangGraph** for the corrective/agentic RAG loop (retrieve → grade → re-search if low quality → generate → verify → abstain-or-answer) ([Next-Gen Agentic RAG with LangGraph 2026](https://medium.com/@vinodkrane/next-generation-agentic-rag-with-langgraph-2026-edition-d1c4c068d2b8)).
- **Self-RAG / CRAG** patterns for self-critique and corrective re-retrieval.

**Grounding / faithfulness gate**
- **LLM-as-judge groundedness** (RAG Triad: context relevance, groundedness, answer relevance — [Snowflake](https://www.snowflake.com/en/engineering-blog/benchmarking-LLM-as-a-judge-RAG-triad-metrics/)).
- **FaithJudge / Vectara HHEM** for offline faithfulness scoring + leaderboard regression gating ([FaithJudge](https://github.com/vectara/FaithJudge)).
- **Ragas / TruLens / DeepEval** for the eval harness (faithfulness, context precision/recall, answer relevancy).
- Claim-level verifier (RT4CHART-style) as a runtime safety net for high-risk (financial figure) answers.

**Account-fact (non-RAG) path**
- Typed tool/function calls into core-banking/policy-admin APIs; structured output; NEVER answered from the KB.

**Observability**
- Langfuse / LangSmith for citation trails, retrieval scores, abstain-rate dashboards, drift alerts.

---

## 4. Benchmarks — accuracy / latency / quality

- **Naive RAG retrieval failure ~40%** of queries ([Techment 2026](https://www.techment.com/blogs/rag-in-2026/)) — the baseline to beat. [sourced]
- **Contextual Retrieval: −49% retrieval errors** (contextual embeddings + contextual BM25), **−67%** with reranking ([Anthropic, via DataCamp](https://www.datacamp.com/tutorial/contextual-retrieval-anthropic)). [sourced]
- **Reranking: +5 to +15 NDCG@10** over dense-only ([Local AI Master 2026](https://localaimaster.com/blog/reranking-cross-encoders-guide)). [sourced]
- **Embedding MTEB**: Cohere embed-v4 65.2, OpenAI text-3-large 64.6, BGE-M3 63.0 ([Milvus/Ailog 2026](https://milvus.io/blog/choose-embedding-model-rag-2026.md)). [sourced]
- **FaithBench**: existing hallucination-detection methods (incl. LLM classifiers) hit only **~50% accuracy** at flagging hallucinations — i.e., automatic faithfulness checking is still imperfect, so you need ensemble verifiers + abstain-on-doubt ([FaithBench, NAACL 2025](https://aclanthology.org/2025.naacl-short.38.pdf)). [sourced]
- **Cohere internal**: strong reranking → **80%+ reduction in task-completion time** vs manual search ([search summary]). [sourced — vendor claim, treat as directional]
- **End-to-end target for THIS step (production-grade, post-build)**: retrieval recall@5 ≥ 0.95 on a domain test set; groundedness (faithfulness) ≥ 0.97 on answered queries; **wrong-when-confident rate < 0.5%**; abstain-correctly rate ≥ 0.9 on unanswerable/out-of-KB queries. [estimate — set as ship gate]
- **Latency budget for voice**: retrieve+rerank+verify must fit inside ~700–1100 ms to keep total turn latency conversational; hybrid+rerank on a warm vector DB is ~150–400 ms, reranker ~50–150 ms, groundedness gate ~200–400 ms (can be partially streamed/speculative). [estimate]

---

## 5. Failure modes — where the agent breaks

1. **Stale-source retrieval.** KB not re-indexed after an RBI circular change → confidently quotes the old charge. (Cause: ingestion lag; no `effective_date` enforcement.)
2. **Right-document, wrong-row.** Retrieves the foreclosure clause but for the wrong product/segment (PL vs HL, staff vs retail). Dense similarity is high but the variant is wrong. (Cause: weak metadata faceting; numbers look interchangeable to embeddings.)
3. **Plausible-wrong generation (confident hallucination).** Number not in context, model interpolates a "reasonable" figure. The deadliest mode — FaithBench shows detectors only ~50% reliable. (Cause: weak grounding constraint; no claim-level verifier on figures.)
4. **Conflict mis-resolution.** Product sheet (4%) vs regulation (Nil for floating individual) — agent picks the product sheet. (Cause: no precedence ranking; no regulation-overrides rule.)
5. **Policy-fact / account-fact bleed.** Quotes a *generic* policy number as if it were *this customer's* exact figure. (Cause: mixing RAG output with account context.)
6. **Code-mixed / regional retrieval miss.** "Loan jaldi band karne pe kitna" in Hinglish/Bhojpuri-tinted Hindi → multilingual embedder under-retrieves vs an Indic-specialist. (Cause: embedding model language coverage.)
7. **ASR-garbled query → wrong retrieval.** Voice mishears "foreclosure" / a scheme code; the dirty query retrieves the wrong doc. (Cause: no query-rewrite / no confirm-back on numerics.)
8. **Over-abstention.** Verifier too strict → agent refuses answerable questions, frustrating customers and killing containment rate. (Cause: mis-tuned groundedness threshold.)
9. **Chunk-boundary truncation.** The applicable figure is split across two chunks; neither alone is sufficient. (Cause: poor chunking; fixed by late chunking + contextual retrieval.)
10. **Citation looks valid but is wrong span.** Model cites a real chunk that doesn't actually contain the claim (attribution hallucination). (Cause: no claim-to-span verification.)

---

## 6. Gap to full adaptation — what the agent still can't do as well as a human, and the path to close it

| Residual human edge | Why agent lags | Concrete engineering/data path to close |
|---|---|---|
| **Authoritative-source instinct on incomplete/messy KBs.** A senior agent knows the "real" answer even when the KB is contradictory or silent, from tribal experience. | Agent only knows what's indexed; tribal knowledge is unwritten. | **Knowledge-gap mining**: log every abstain + every escalation; route to a knowledge-ops loop that writes the missing canonical answer into the KB (human-curated, dated, sourced). Over weeks the KB absorbs the tribal knowledge. Add a **"golden answers" table** of QA-verified canonical Q→A pairs that bypass retrieval. |
| **Conflict adjudication with judgment** (which authority truly wins in an edge case). | Precedence rules are coarse; real edge cases need legal nuance. | Encode an explicit **precedence policy graph** (Regulation > Master Circular > Product MITC > FAQ) as retrieval weights + a reasoning rule; for unresolved conflicts → mandatory HITL + flag for compliance to write a tie-break rule (which then becomes a golden answer). |
| **Perfectly calibrated abstention** (knowing exactly when to say "I'll verify"). | FaithBench: faithfulness detection ~50% reliable; thresholds are blunt. | **Ensemble verifier** (LLM-judge + NLI entailment model + claim-decomposition verifier) with a **conformal-prediction calibration** on a labeled domain set to set the abstain threshold at a guaranteed wrong-rate (e.g., <0.5%). Re-calibrate weekly as KB drifts. |
| **Faithful figure preservation under translation** (number-exactness in Hinglish/regional). | Indic generation can mangle/round numbers. | **Number-slotting**: extract figures as structured fields from the cited span, render them via templates (never let the LLM re-type a number), verify slot-equality post-generation. |
| **Self-updating to fresh circulars in real time.** Human hears about a change on day one. | Index refresh lag. | **Event-driven re-index**: webhook from the compliance/circular feed → priority re-embed + cache-invalidate affected scheme codes; staleness alarm if `effective_date` of any answered policy is older than the latest known circular for that product. |
| **Register & empathy in delivering "I don't know."** Human softens it. | Solvable but often neglected. | Style-controlled abstention templates in Hinglish ("ek minute sir, main ekdum sahi figure confirm karke batati hoon"). |

The **closing mechanism that matters most**: a tight **abstain → knowledge-ops → golden-answer** loop. Every "I don't know" is training data; the KB monotonically converges toward the senior human's coverage. That is how the agent *fully adapts* to the human on this step — not a bigger model, but an institutional learning loop on top of a strict grounding gate.

---

## 7. HITL trigger — when a human MUST take over

NOT fully automatable. Hand to human when:
- **Groundedness/verifier fails** (claim unsupported by retrieved spans) AND corrective re-retrieval also fails → no confident answer exists. Transfer rather than guess.
- **Conflict unresolved** (regulation vs product contradiction with no precedence rule covering it).
- **Out-of-KB / novel question** (golden-answer miss + low retrieval scores).
- **Financial figure on a high-stakes irreversible action** (foreclosure amount that triggers a payment) where wrong-number → mis-selling liability — verify-and-confirm or human sign-off per risk tier.
- **Customer disputes the stated policy** ("but the branch told me Nil") → human + relationship judgment.
- **Regulatory/legal interpretation** ("can you legally charge me?") beyond stating the documented charge.

The clean automatable core: static, dated, single-variant policy facts with high retrieval confidence + passing groundedness gate + (for figures) account-API confirmation. That's the majority of volume.

---

## 8. Automation readiness — **7 / 10**

The *retrieval + grounded-generation + citation* machinery is production-mature in 2026 (contextual retrieval, hybrid+rerank, groundedness gates are off-the-shelf). What keeps it off 9–10:
- Faithfulness *detection* is still only ~50% reliable on hard cases (FaithBench) → you cannot fully trust auto-abstention without ensemble + calibration.
- Indic/code-mixed retrieval is a notch behind English.
- Regulatory liability (1 Jan 2027 mis-selling refund rule) raises the cost of the long-tail wrong answer, so the prudent design keeps a HITL safety net on financial figures.
Readiness for the **common, well-covered, English/Hindi policy-fact case: 8–9.** For the **full long-tail incl. conflicts + figures + regional: ~6.** Weighted: **7.**

---

## 9. Build spec — what to implement, data needed, ship gate

**Implement**
1. **Curated, metadata-rich KB** (canonical docs only) with `doc_type, product, segment, scheme_code, effective_from/to, source_authority, regulator_ref, language, version`.
2. **Contextual-retrieval ingestion** (contextual embeddings + contextual BM25 + late chunking).
3. **Hybrid retriever** (dense Cohere embed-v4 / BGE-M3 + Indic Vyakyarth/Indic-ColBERT fallback + BM25) with **metadata filters** (product/segment/effective-date).
4. **Reranker** (Cohere Rerank 3.5 or BGE-reranker-v2-m3).
5. **Agentic CRAG loop** (LangGraph): query-rewrite → route → retrieve → grade → re-search if low → generate-with-citations → groundedness-verify → answer / abstain.
6. **Precedence engine** (regulation > circular > MITC > FAQ).
7. **Groundedness gate**: LLM-judge + NLI entailment + claim-decomposition; **number-slotting** for figures; conformal-calibrated abstain threshold.
8. **Golden-answers table** + **abstain → knowledge-ops** loop.
9. **Account-fact tool path** strictly separate from KB.
10. **Citation/audit trail** logging (chunk ids, scores, version, ts).

**Data needed**
- Full canonical document corpus (MITC, product masters, circulars, SOPs, RBI/IRDAI references) with effective dates.
- A **domain eval set**: 500–1000 real (anonymized, DPDP-safe) customer questions → expert-labeled gold answers + gold source spans + "unanswerable" negatives, in English + Hindi + Hinglish + 2–3 regional languages.
- Code-mixed query set for Indic retrieval tuning.
- Labeled faithfulness set (answer + context + supported/unsupported) for calibrating the gate.

**Eval metric that gates ship** (regression-gated via Ragas/FaithJudge in CI):
- Retrieval **recall@5 ≥ 0.95** and **context-precision ≥ 0.85** on the domain set.
- **Faithfulness (groundedness) ≥ 0.97** on answered queries.
- **Wrong-when-confident rate < 0.5%** (the hard gate — a single confidently-wrong financial figure is a fail).
- **Correct-abstention ≥ 0.90** on the unanswerable/out-of-KB negatives; **over-abstention ≤ 10%** on answerable.
- **Number-exactness = 100%** on figure questions (slotted, verified).
- Indic/Hinglish recall@5 within **5 pts** of English.
- p95 retrieve+rerank+verify latency **≤ 1100 ms** (voice).

Ship only when ALL gates pass on a held-out set; weekly regression after every KB update.

---

## 10. India specifics — Hinglish / regional / regulatory

- **Code-mixed reality.** Customers ask in Hinglish ("loan jaldi band karwana hai, kitna lagega") and regional-tinted Hindi. Multilingual embedders under-retrieve on code-mix; pair a multilingual workhorse with an **Indic specialist** (Vyakyarth-1 / Indic-ColBERT / a fine-tuned Hindi embedder per DeepRAG) and a **query-rewrite to English-or-Hindi canonical** before retrieval. ([Vyakyarth](https://ai-labs.olakrutrim.com/models/Vyakyarth-1-Indic-Embedding); [IndicIRSuite](https://arxiv.org/pdf/2312.09508))
- **Numbers in mixed script.** Figures may be spoken/written in Devanagari or Latin digits, with "lakh/crore/hazaar" units — normalize and slot exactly; never let the LLM re-type.
- **RBI mis-selling rule (effective 1 Jan 2027).** Misleading/under-disclosed statements → **refund + compensation** liability ([Angel One](https://www.angelone.in/news/economy/rbi-issues-new-rules-to-curb-mis-selling-of-financial-products-norms-effective-from-january-1-2027)). This is the reason the grounding gate must err toward abstain on financial figures.
- **RBI FREE-AI framework + AI advisories (2026).** Require **AI-involvement disclosure**, **human override**, grievance/redressal for AI-driven decisions, and an **internal AI sandbox** where prompts/agents are evaluated against ground truth before any customer touchpoint ([RBI FREE-AI](https://www.humaineeti.ai/resources/rbi-free-ai-framework); [Legistify, India-specific legal AI 2026](https://legistify.com/blogs/india-specific-legal-ai/)). Build a non-prod ground-truth eval gate (matches the §9 ship gate) — it's now a quasi-regulatory expectation, not just good practice.
- **IRDAI parallel.** For insurance answers, MITC/policy-wording is canonical; mis-statement of cover/exclusions has the same liability shape.
- **DPDP data residency.** Account-specific PII must not leave India / the bank boundary → favor **self-hostable** embedders/rerankers (BGE-M3, BGE-reranker, Indic-ColBERT) and self-host vector DB (Qdrant/Milvus) for the account-fact path; hosted APIs acceptable for non-PII policy text only.
- **Regulation-overrides-product** is especially live in India: RBI bars foreclosure/prepayment charges on floating-rate loans to individuals + MSMEs — the precedence engine must encode such carve-outs so the agent never quotes a charge the regulator has banned.

---

### Sources
- [Techment — RAG in 2026](https://www.techment.com/blogs/rag-in-2026/)
- [Anthropic Contextual Retrieval (DataCamp)](https://www.datacamp.com/tutorial/contextual-retrieval-anthropic)
- [Local AI Master — Rerankers 2026](https://localaimaster.com/blog/reranking-cross-encoders-guide)
- [Milvus — Best Embedding Models for RAG 2026](https://milvus.io/blog/choose-embedding-model-rag-2026.md)
- [Azure AI Search — Agentic Retrieval](https://learn.microsoft.com/en-us/azure/search/agentic-retrieval-overview)
- [LangGraph Agentic RAG 2026](https://medium.com/@vinodkrane/next-generation-agentic-rag-with-langgraph-2026-edition-d1c4c068d2b8)
- [FaithBench (NAACL 2025)](https://aclanthology.org/2025.naacl-short.38.pdf)
- [Vectara FaithJudge](https://github.com/vectara/FaithJudge)
- [Snowflake — RAG Triad LLM-as-judge](https://www.snowflake.com/en/engineering-blog/benchmarking-LLM-as-a-judge-RAG-triad-metrics/)
- [Sub-sentence citations (arXiv 2509.20859)](https://arxiv.org/pdf/2509.20859)
- [LAQuer localized attribution (arXiv 2506.01187)](https://arxiv.org/pdf/2506.01187)
- [RT4CHART / Retromorphic verification (arXiv 2603.27752)](https://arxiv.org/html/2603.27752v1)
- [Vyakyarth-1 Indic Embedding](https://ai-labs.olakrutrim.com/models/Vyakyarth-1-Indic-Embedding)
- [IndicIRSuite (arXiv 2312.09508)](https://arxiv.org/pdf/2312.09508)
- [DeepRAG Hindi embedding (arXiv 2503.08213)](https://arxiv.org/html/2503.08213v1)
- [RBI mis-selling norms eff. 1 Jan 2027 (Angel One)](https://www.angelone.in/news/economy/rbi-issues-new-rules-to-curb-mis-selling-of-financial-products-norms-effective-from-january-1-2027)
- [RBI tightens mis-selling norms (Deccan Chronicle)](https://www.deccanchronicle.com/amp/business/rbi-tightens-norms-to-curb-mis-selling-of-financial-products-1963800)
- [RBI FREE-AI Framework](https://www.humaineeti.ai/resources/rbi-free-ai-framework)
- [India-specific legal AI 2026 (Legistify)](https://legistify.com/blogs/india-specific-legal-ai/)

*Draft research dossier for review. Cited where possible; [estimate] elsewhere. Not investment/legal advice.*
