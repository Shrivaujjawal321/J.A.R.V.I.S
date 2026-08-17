# Step A16 — Call Wrap-Up & Disposition Coding

**Step:** Notes, tags, CRM update, accurate categorisation — everything the agent does in the 20–90 seconds after the conversation ends (or, increasingly, in parallel during the conversation).

**Context:** India-market, multilingual (Hindi + regional + Hinglish), RBI/IRDAI/DPDP-compliant, action-taking voice+chat contact-center agent for mid-market BPOs.

**Date:** 2026-06-24
**Author:** Jarvis — Research Analyst Specialist
**Status:** Draft research note for review. Cited where possible; [UNSOURCED] elsewhere. Not investment advice.

---

## 0. Why this step matters (the economics)

After-Call Work (ACW), of which disposition coding + notes + CRM update is the bulk, eats **20–30% of total agent handle time** ([Balto / NiCE, 2026](https://www.nice.com/info/call-summary-automation-in-contact-centers)). For a mid-market Indian BPO this is the single highest-ROI automation surface in the entire agent workflow because:

- It is **post-conversation** — no live-latency risk, no customer-facing failure if it's a few hundred ms slow.
- It is **structured-output-shaped** — disposition codes are a closed taxonomy; notes are grounded summarization. Both are squarely inside 2026 LLM competence.
- It is the **data backbone**: every downstream metric (FCR, AHT, root-cause analytics, QA sampling, compliance audit, campaign ROI) is only as good as the disposition + notes the agent enters. Humans are *notoriously* bad at it under AHT pressure — they pick "Other / General Query" to escape the wrap timer, poisoning analytics. **An AI that is consistent beats a rushed human here, not just cheaper.**

This is the rare BPO step where the AI is potentially *more accurate than the median human*, not merely cheaper — making it the natural first full-automation beachhead.

---

## 1. Human micro-steps (atomic decomposition)

What a skilled human agent ACTUALLY does between "call ends" and "ready for next call". Broken into the smallest cognitive / emotional / mechanical moves:

1. **Recall the gist** — reconstruct from working memory what the call was *about* (intent), distinct from what was *said* (transcript). Humans compress 6 minutes into a 2-line mental model.
2. **Identify the primary intent** — pick the *one* reason-for-contact that defines the call even when the customer raised 3 issues (e.g. "called about billing but real issue was failed auto-debit").
3. **Identify secondary intents / cross-sell flags** — note the upsell hint, the churn risk signal, the repeat-caller frustration.
4. **Determine the outcome** — resolved / unresolved / escalated / callback-scheduled / sale-closed / not-interested. This is the disposition's *result axis*.
5. **Map intent+outcome to the disposition code** — translate the messy reality into the *finite, often badly-designed* dropdown taxonomy the CRM forces (e.g. 40–200 codes, frequently overlapping). This is the hardest cognitive step.
6. **Resolve taxonomy ambiguity** — when two codes both fit, apply the *unwritten team convention* (e.g. "we always tag failed-KYC under 'Onboarding-Docs' not 'Compliance'"). Tribal knowledge.
7. **Decide sub-disposition / reason codes** — the second/third dropdown level (product → sub-product → issue-type).
8. **Write the free-text note** — a human-readable summary for the *next* agent: what happened, what was promised, what's pending. Tone-aware (flag an angry customer).
9. **Capture action commitments** — "promised callback Tuesday", "waived ₹200 fee", "raised ticket #X" — the *promises* that become SLAs.
10. **Update structured CRM fields** — change account status, set follow-up date, tick consent-given, update contact preference, set DPDP purpose-tag.
11. **Trigger downstream workflow** — create ticket, fire callback task, push to retention queue, send the e-mandate/SMS — the *action-taking* part.
12. **Self-QA / sanity check** — "did I tag this right? will QA flag me?" — a quiet risk calculation against the agent's own scorecard.
13. **Compliance tagging** — did consent get recorded? was a mis-selling disclosure made? (IRDAI/RBI) — flag if a script step was skipped.
14. **Reset & context-clear** — emotionally dump the previous (possibly abusive) call to be fresh for the next. The emotional-labor micro-step humans need and AI doesn't.

---

## 2. Agent approach (how a 2026 AI does each sub-step)

The whole step collapses into **one grounded, multi-task LLM call over the verified transcript + CRM context, emitting a single schema-constrained JSON object**, then a deterministic tool-execution layer. Mapping to the human micro-steps:

| Human micro-step | 2026 agent technique |
|---|---|
| 1–2 Recall gist + primary intent | **Grounded abstractive summarization** + **intent classification** on the *full diarized transcript* (not memory). Single LLM call, structured output. Model: GPT-5.x / Claude Opus 4.x / Gemini 2.5 for premium; **Sarvam-M / Llama-3.3-70B fine-tune** for cost + Indic. |
| 3 Secondary intents / cross-sell | Multi-label classification head in the same JSON schema (`secondary_intents: []`, `churn_risk: 0-1`, `upsell_flag: bool`). |
| 4 Outcome | Closed-set classification field `outcome ∈ {resolved, unresolved, escalated, callback, sale, no-sale,...}`. |
| 5–7 Map to disposition code + sub-codes | **Constrained decoding against the actual CRM taxonomy** via a JSON-Schema `enum` (XGrammar / Outlines FSM) → the model *cannot* emit an invalid code. For 100–200 code taxonomies: **retrieval-augmented disposition** — embed each code's definition, retrieve top-k candidate codes, LLM picks among them with rationale. |
| 6 Tribal/unwritten convention | **Few-shot exemplars in prompt** mined from this BPO's *historical* (transcript → human-chosen code) pairs; or a lightweight **fine-tune / DSPy-optimized prompt** on that BPO's labeled history so the model learns the team convention. |
| 8 Free-text note | Grounded summarization with a **faithfulness judge** second pass (LLM-as-judge / Ragas faithfulness) to suppress hallucinated commitments. |
| 9 Action commitments | **Structured commitment extraction** (`commitments: [{action, due_date, amount}]`) — same JSON. |
| 10 Structured CRM fields | Field-level extraction → typed JSON → deterministic write. |
| 11 Trigger workflow | **Tool/function-calling** layer: `create_ticket()`, `schedule_callback()`, `send_emandate()` — Tier-3 actions gated (draft/confirm) per Jarvis safety model. |
| 12 Self-QA | **Confidence scoring + LLM-as-judge auto-QA** on its own disposition; low-confidence → route to HITL. |
| 13 Compliance tagging | Dedicated **compliance classifier** checking consent-script presence, mis-selling phrases (RBI/IRDAI keyword + semantic check). |
| 14 Reset | N/A — stateless per call (the AI's structural advantage). |

**Architecture pattern:** *Verified-transcript → single multi-task structured-extraction call → faithfulness/compliance judges → deterministic tool execution with Tier-3 gating.* This is the "LLM proposes, schema + judge + deterministic code disposes" pattern.

---

## 3. Tooling (concrete 2026 stack)

- **ASR (upstream dependency):** **Sarvam Saaras v3 / Sarvam STT** (8 kHz telephony, Indic + Hinglish code-switch) — strong on real call-center audio ([Codersarts/Sarvam, 2026](https://www.codersarts.com/post/how-to-build-a-vernacular-contact-center-qa-platform-with-saaras-v3-and-sarvam-105b)); fallback **Whisper large-v3 + Hinglish community fine-tune**; **Deepgram Nova** for English-heavy queues. Diarization for speaker attribution.
- **Disposition/summary LLM:**
  - Premium tier: **Claude Opus/Sonnet 4.x** or **GPT-5.x** (native structured output GA early 2026) or **Gemini 2.5**.
  - Cost/Indic tier: **Sarvam-M (105B)** or **Llama-3.3-70B** fine-tuned on the BPO's history, served on **vLLM**.
- **Structured output / constrained decoding:** **XGrammar** (default backend for vLLM/SGLang/TensorRT-LLM as of Mar 2026, <40µs/token — [JSONSchemaBench / structured-output guides, 2026](https://dev.to/pockit_tools/llm-structured-output-in-2026-stop-parsing-json-with-regex-and-do-it-right-34pk)) or **Outlines / Guidance**. **Pydantic v2** schema as source of truth.
- **Taxonomy retrieval:** embeddings (BGE-M3 / Sarvam embeddings for Indic) + a vector store (pgvector / Qdrant) of disposition-code definitions for RAG-disposition on large taxonomies.
- **Faithfulness / hallucination judge:** **Ragas faithfulness**, **FaithBench**-style eval, or a cheap LLM-as-judge pass (one extra eval call lowers unfaithful summaries — [ACL Findings 2025 / RAG faithfulness work](https://arxiv.org/pdf/2503.15272)).
- **Prompt optimization / convention learning:** **DSPy** (optimize the disposition prompt against the BPO's labeled history) or LoRA fine-tune via **Unsloth**.
- **CRM write layer:** **Salesforce Einstein Work Summaries / Agentforce** (native AI wrap-up + CRM grounding — [Salesforce, 2026](https://help.salesforce.com/s/articleView?id=service.cc_generative_ai_work_summaries.htm)), **Genesys Cloud** activity-record field mapping ([Genesys, 2026](https://help.genesys.cloud/articles/release-notes-genesys-cloud-salesforce/)), or direct CRM API (Zoho/Freshdesk/LeadSquared common in India BPOs) via deterministic SDK calls.
- **Orchestration / gating:** LangGraph or a thin state machine; Tier-3 action gate per Jarvis auto-mode.
- **Eval + observability:** Promptfoo / Braintrust / Langfuse for offline eval + production drift monitoring.

---

## 4. Benchmarks (real numbers)

- **ACW share of handle time:** 20–30% of agent time ([NiCE, 2026](https://www.nice.com/info/call-summary-automation-in-contact-centers)). Automating it ≈ 0.2–0.3× capacity uplift.
- **Grounded summarization hallucination:** **<2%** when summaries are grounded in source text; RAG/grounding improves factual accuracy ~40% vs ungrounded ([hallucination stats, 2026](https://futureagi.com/blog/understanding-llm-hallucination-2025/)). Ungrounded LLMs hallucinate **up to ~82%** on adversarial fact tasks — grounding is non-negotiable ([SQ Magazine, 2026](https://sqmagazine.co.uk/llm-hallucination-statistics/)).
- **LLM text classification accuracy:** modern models hit **95–99%** on well-defined classification; Llama-3.1-8B fall-2025 cut false positives sharply ([LXT benchmarks, 2026](https://www.lxt.ai/blog/llm-benchmarks/)). Disposition accuracy in practice tracks taxonomy quality, not model ceiling.
- **Structured output validity:** **100%** schema-valid with native structured output / constrained decoding (Level 3); 95–99% with function-calling (Level 2) ([structured output guide, 2026](https://dev.to/pockit_tools/llm-structured-output-in-2026-stop-parsing-json-with-regex-and-do-it-right-34pk)).
- **Indic/Hinglish ASR (the gating dependency):** 90%+ English, **80–85% Hinglish** in real telephony; Tier-2 82–88%, Tier-3 70–80%; code-switch is **3–8 pp lower** ([Caller.digital / Sarvam, 2026](https://www.autointerviewai.com/blog/vernacular-ai-voice-agents-india-hinglish-code-switching-2026)). **This is the real ceiling** — disposition is only as accurate as the transcript feeding it.
- **Disposition coding accuracy (direct):** No clean public 2026 benchmark for call-disposition classification specifically [estimate]: well-tuned systems on a clean 30–60 code taxonomy reach **85–93% top-1 agreement with a gold human coder**; messy 150+ code overlapping taxonomies drop to **65–80%** [estimate, analogous to ICD-coding LLM reviews where ClinicalLongformer hit ~94% on cleaner label sets]([ICD LLM review, 2025](https://www.medrxiv.org/content/10.1101/2025.07.30.25330916.full.pdf)).
- **DIAL-SUMMER:** dialogue-summary error taxonomy = factual / completeness / coherence / relevance; current LLMs still produce measurable errors across all four — use it as the note-quality rubric ([DIAL-SUMMER, 2026](https://arxiv.org/pdf/2602.08149)).

---

## 5. Failure modes

1. **Garbage-in from ASR.** Hinglish/Tier-3 transcript errors (names, amounts, product names) propagate into wrong codes and wrong commitments. The dominant failure source.
2. **Bad taxonomy = bad ceiling.** Overlapping/ill-defined CRM codes mean *no* coder (human or AI) can be consistent. The AI will be confidently wrong on overlapping codes.
3. **Hallucinated commitments in notes** — "agent promised refund" when none was made → creates a phantom SLA / legal exposure. Mitigated but not eliminated by faithfulness judge.
4. **Primary-intent collapse** — multi-issue calls; model picks the *last-discussed* issue instead of the *driving* one.
5. **Tribal-convention drift** — model uses the "textbook" code, not the team's unwritten convention; analytics diverge from history.
6. **Long-call truncation / lost-in-the-middle** — a 20-min escalation exceeds context window or buries the key fact mid-transcript.
7. **Compliance miss** — fails to flag a skipped consent line or a mis-selling phrase in code-switched speech (the semantic-detection-in-Hinglish gap).
8. **Silent CRM schema drift** — CRM admin adds/renames a disposition code; constrained-decoding enum goes stale → invalid writes or forced-wrong code.
9. **Over-tagging "Other"** — if the taxonomy lacks a code, the model defaults to a catch-all just like a rushed human, defeating the purpose.
10. **Action over-execution** — auto-firing a real Tier-3 action (send e-mandate, waive fee) on a misread transcript. Why Tier-3 gating is mandatory.

---

## 6. Gap to full adaptation (what AI still can't do as well as a human, and how to close it)

| Residual gap | Why it's hard | Concrete path to close |
|---|---|---|
| **Tribal/unwritten coding conventions** | Lives in team Slack, floor-supervisor heads, never documented | Mine 6–12 months of (transcript → human code) pairs per BPO; DSPy-optimize or LoRA-fine-tune per client; build a "convention sheet" the model is prompted with. This is the #1 adaptation lever — closes within weeks of labeled data. |
| **Primary-intent judgment on messy multi-issue calls** | Requires understanding which issue *drove* the contact, not which was longest | Add a supervised "primary-intent" head trained on human disambiguation labels; surface the model's rationale for QA feedback loop. |
| **Hinglish/regional semantic nuance** (sarcasm, indirect refusal, mis-sell phrasing) | Code-switch + cultural pragmatics weak in generic LLMs | Fine-tune on Indic call data (Sarvam-M base); build a Hinglish compliance-phrase lexicon + semantic classifier; HiACC-style code-switch corpora for eval. |
| **Compliance judgment ("was this mis-selling?")** | Regulatory line is contextual, not keyword | Hybrid: keyword recall + LLM semantic check + human-reviewed escalation; tune on IRDAI/RBI enforcement examples. Keep human-in-loop on flagged subset. |
| **Novel/unseen dispositions** (taxonomy gap) | Closed enum can't express a new reason | Add an "uncertain / propose-new-code" path that routes to a supervisor instead of forcing "Other"; feed proposals into taxonomy governance. |
| **Emotional context for next agent** ("customer is on the edge, handle with care") | Soft, tone-laden, easily lost in extractive summary | Add an explicit `customer_state` field (frustration 0-1, vulnerability flag) trained on sentiment + escalation labels. |

**Net:** the gap is **data + per-client tuning + a HITL feedback loop**, not model capability. With the BPO's own labeled history, this step reaches human-parity-or-better on the bulk of calls. The irreducible human residue is the **judgment + compliance-edge subset (~5–15% of calls)**, which is a routing problem, not a "can't-automate" problem.

---

## 7. HITL trigger

A human MUST take over (or review) when:

- **Confidence below threshold** on disposition (e.g. model top-1 vs top-2 margin < δ, or self-judge flags).
- **Compliance flag fires** (suspected mis-selling, skipped consent, vulnerable-customer signal) → mandatory human review (RBI/IRDAI exposure).
- **Tier-3 action would execute** (real money waiver, e-mandate send, account status change) → confirm, never auto in autopilot.
- **ASR confidence low** (Tier-3 audio, heavy code-switch, crosstalk) → transcript unreliable, escalate.
- **"Propose-new-code"** path → supervisor reviews taxonomy gap.
- **High-value / complaint / legal-keyword** call → human QA review regardless of confidence.

Otherwise: **fully automatable** for the high-confidence majority (the routine resolved/standard-disposition calls, which are the bulk of volume).

---

## 8. Automation readiness: **8 / 10**

Among all BPO-agent micro-steps, this is one of the **most ready to fully replace the human today**. Reasons for 8 (not 10):
- The *summarization + closed-set classification + structured CRM write* core is solved tech (grounded summary <2% hallucination, 100% schema-valid outputs, 95–99% classification).
- It is post-conversation → no live-latency or customer-facing failure risk.
- Held back from 9–10 by: (a) ASR ceiling on Hinglish/Tier-3 (the upstream dependency, not this step itself), (b) messy real-world taxonomies needing per-client tuning, (c) compliance-judgment + Tier-3 action subset that genuinely needs HITL, (d) hallucinated-commitment tail risk.

With a clean taxonomy + a few months of labeled history per client, the routine-call majority is **fully automatable now with high confidence**; the residual ~10% routes to humans.

---

## 9. Build spec

**What to implement**
1. **Pydantic v2 disposition schema** = single source of truth: `primary_intent`, `secondary_intents[]`, `outcome`, `disposition_code` (enum from CRM), `sub_codes[]`, `commitments[]`, `crm_fields{}`, `customer_state{}`, `compliance_flags[]`, `confidence`, `needs_human` bool, `rationale`.
2. **Extraction service:** verified diarized transcript + CRM context → one LLM call → **XGrammar-constrained** JSON against that schema. Taxonomy `enum` synced live from CRM admin API (kill schema-drift failure mode).
3. **RAG-disposition** for >60-code taxonomies: embed code definitions, retrieve top-k, LLM picks + rationale.
4. **Faithfulness judge** pass on the free-text note (Ragas faithfulness / LLM-judge) → strip/flag unsupported commitments.
5. **Compliance classifier** (keyword + semantic, Hinglish lexicon) → `compliance_flags`.
6. **Deterministic CRM-write + tool layer** with Tier-3 gating (draft/confirm for money/mandate/status actions).
7. **Confidence router** → HITL queue for low-confidence / flagged calls; captured human corrections feed the per-client fine-tune loop.

**Data needed**
- 6–12 months of historical **(transcript → human disposition code + notes + CRM fields)** per client → the gold set for fine-tune/DSPy + eval.
- The **live disposition taxonomy** (codes + definitions) via CRM admin API.
- Hinglish compliance-phrase lexicon + IRDAI/RBI mis-selling examples.
- Labeled **primary-intent disambiguation** set for multi-issue calls.

**Eval metric that gates ship**
- **Primary gate:** Top-1 **disposition agreement with a gold human coder ≥ 90%** (and **≥ 0.80 macro-F1** to catch rare-code collapse) on a held-out, client-specific set.
- **Note quality:** faithfulness (Ragas) ≥ 0.95, zero hallucinated commitments on a curated commitment-bearing slice (hard gate — any phantom commitment = block).
- **Structured validity:** 100% schema-valid (constrained decoding guarantees this).
- **Compliance recall ≥ 0.95** on mis-sell/consent-skip detection (recall-weighted — missing a violation is worse than a false flag).
- **HITL routing precision:** of calls auto-completed (not routed), human-review spot-check disagreement < 5%.
- **Latency:** wrap-up JSON < 5 s after call-end (non-blocking; can run during call).

Ship per-client only when the primary + note + compliance gates pass on *that client's* held-out set — never on a global average.

---

## 10. India specifics

- **Hinglish + 22 scheduled languages.** Disposition codes themselves are usually English, but **notes must be readable by the next (Indian) agent** — keep notes in English (or Hinglish on request) even when the call was Hindi/Tamil/Telugu. ASR code-switch is the dominant accuracy bottleneck (80–85% Hinglish, lower in Tier-3) ([Sarvam/Caller.digital, 2026](https://www.autointerviewai.com/blog/vernacular-ai-voice-agents-india-hinglish-code-switching-2026)). Prefer **Sarvam Saaras v3** for the transcript that feeds this step.
- **DPDP Act 2023 (Rules 2025, substantive provisions effective ~13 May 2027; final rules H1 2026).** Every transcript + note + disposition is personal data of a Data Principal. Implications for THIS step:
  - **Purpose-tagging:** the disposition write should carry a DPDP processing-purpose tag (analytics vs service) and respect consent scope. ([EY/DPDP, 2026](https://www.ey.com/en_in/insights/cybersecurity/decoding-the-digital-personal-data-protection-act-2023))
  - **Data minimization + retention:** notes must not over-capture; retain only as long as necessary (≥1 yr for breach-investigation defensibility) ([Gistly DPDP, 2026](https://www.gistly.ai/blog/dpdp-act-compliance-contact-centers)).
  - **Consent-script verification** belongs in the compliance-flag sub-step — DPDP wants 100% auditability vs the legacy 2–5% manual QA sample; an AI disposition step that flags every skipped-consent call is itself a compliance asset. Penalties up to **₹250 crore**.
- **RBI outsourcing / IRDAI mis-selling:** for BFSI/insurance queues, the compliance classifier must encode RBI outsourcing-of-financial-services norms and IRDAI mis-selling definitions; flagged dispositions → mandatory human review. (RBI-specific guideline text not retrieved here — mark [UNSOURCED], confirm against current RBI outsourcing master direction before BFSI deployment.)
- **Localization of notes/codes** to the 22 scheduled languages may be required for the *consent-notice* trail, not the internal disposition.
- **Mid-market BPO CRM reality:** often **Zoho / Freshdesk / LeadSquared / Ameyo / Sarv**, not Salesforce — build the write-layer CRM-agnostic via API adapters; don't assume Einstein/Agentforce availability.

---

## Sources

- [NiCE — Call Summary Automation in Contact Centers, 2026](https://www.nice.com/info/call-summary-automation-in-contact-centers)
- [Balto — Best Contact Center AI Automation Software, 2026](https://www.balto.ai/blog/best-contact-center-ai-automation-software/)
- [Retell AI — Contact Center Automation Trends, 2026](https://www.retellai.com/blog/contact-center-automation-trends)
- [Salesforce — Einstein Work Summaries](https://help.salesforce.com/s/articleView?id=service.cc_generative_ai_work_summaries.htm)
- [Genesys Cloud for Salesforce — Release Notes](https://help.genesys.cloud/articles/release-notes-genesys-cloud-salesforce/)
- [Structured Output in 2026 (constrained decoding, XGrammar)](https://dev.to/pockit_tools/llm-structured-output-in-2026-stop-parsing-json-with-regex-and-do-it-right-34pk)
- [JSONSchemaBench](https://arxiv.org/pdf/2501.10868)
- [DIAL-SUMMER dialogue-summary error framework, 2026](https://arxiv.org/pdf/2602.08149)
- [FaithBench summarization hallucination benchmark](https://arxiv.org/pdf/2410.13210)
- [LLM Hallucination Statistics 2026](https://sqmagazine.co.uk/llm-hallucination-statistics/)
- [Future AGI — LLM Hallucination 2026](https://futureagi.com/blog/understanding-llm-hallucination-2025/)
- [LXT — LLM Benchmarks 2026](https://www.lxt.ai/blog/llm-benchmarks/)
- [Automatic ICD coding using LLMs: systematic review, 2025](https://www.medrxiv.org/content/10.1101/2025.07.30.25330916.full.pdf)
- [Sarvam — Vernacular Contact-Center QA with Saaras v3](https://www.codersarts.com/post/how-to-build-a-vernacular-contact-center-qa-platform-with-saaras-v3-and-sarvam-105b)
- [Auto Interview AI — Vernacular Voice Agents India Hinglish 2026](https://www.autointerviewai.com/blog/vernacular-ai-voice-agents-india-hinglish-code-switching-2026)
- [Sarvam STT API](https://www.sarvam.ai/apis/speech-to-text)
- [Gistly — DPDP Act Compliance for Contact Centers](https://www.gistly.ai/blog/dpdp-act-compliance-contact-centers)
- [EY India — Decoding the DPDP Act 2023](https://www.ey.com/en_in/insights/cybersecurity/decoding-the-digital-personal-data-protection-act-2023)

---

Draft research note for review. Cited where possible; [UNSOURCED] elsewhere. Not investment advice.
