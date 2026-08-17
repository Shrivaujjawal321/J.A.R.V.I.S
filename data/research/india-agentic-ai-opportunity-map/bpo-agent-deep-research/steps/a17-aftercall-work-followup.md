# A17 — After-Call Work & Follow-Up (callbacks, scheduling, ticket creation, promises kept)

**Deep research dossier · India multilingual (Hindi/regional/Hinglish), RBI/IRDAI/DPDP-compliant, action-taking voice+chat agent for mid-market BPOs**
Date: 2026-06-24 · Owner: Research-Analyst (Jarvis)

> Scope of THIS step only: everything that happens *after* the customer hangs up (or the chat resolves) until every commitment made on the call is mechanically guaranteed. This is the "wrap-up" + "promise-keeping" layer. It is NOT the live conversation (that's earlier steps) and NOT QA scoring (later step). Disposition coding, CRM/ticket write-back, callback & appointment scheduling, sending the promised SMS/WhatsApp/email, and ensuring future-dated commitments fire on time.

---

## 0. Why this step matters (first principles)

After-Call Work (ACW), a.k.a. "wrap time," is the single largest pool of *recoverable* agent time in a BPO. Industry ACW runs 20–90 seconds for simple calls and up to **30 minutes** for complex appointment/case work — Salesforce cites pilots saving ~6,000 hours/year just by automating post-appointment note-taking ([Salesforce/CMSWire, 2026](https://www.cmswire.com/contact-center/salesforce-launches-agentforce-contact-center-to-unify-ai-voice-and-crm/)).

Critically, this step is where **promises die**. A perfect live call that fails to (a) log the right disposition, (b) create the ticket, (c) schedule the callback, or (d) send the promised PTP/appointment confirmation is a *broken promise* — the #1 driver of repeat calls, complaints, and in India, regulatory exposure (RBI Fair Practices, DPDP grievance trail). So "promises kept" is the true success metric of this step, not "summary written."

This step is **unusually automatable** because it is mostly *deterministic write-back + scheduling against structured systems*, with one fuzzy sub-task (summarization/disposition) that 2026 grounded LLMs do well. The hard part is not intelligence — it's **reliability/idempotency** (a callback must fire exactly once, on time, in the legal window) and **traceability** (DPDP/RBI audit).

---

## 1. Human micro-steps (the smallest atomic moves a skilled agent actually makes)

A skilled human, in the 30–120s after a call, does this — partly cognitive, partly mechanical, partly emotional/judgment:

1. **Recall + hold the call in working memory** — what was the reason, what did I promise, what's the customer's emotional state, did I commit to a date/amount.
2. **Decide the disposition code** — pick the right outcome bucket from a taxonomy of 30–200 codes (e.g. `PTP-confirmed`, `dispute-raised`, `wrong-number`, `callback-requested`, `RNR`, `already-paid`, `escalated`). This is a *judgment* under ambiguity (the call had three topics; which is the disposition?).
3. **Write the call summary / notes** — a free-text disposition note: reason, what was done, what's pending, next action. Tone-neutral, factual, readable by the next agent.
4. **Extract structured commitments** — parse out of memory: PTP amount + date, appointment slot, callback date/time + reason, refund amount, document to be sent, SLA clock.
5. **Update CRM / case fields** — set status, sub-status, next-action-date, amount fields, contact-preference, language preference, DND flags.
6. **Create or update the ticket** — open a case if new issue; link to existing; set priority/queue/owner; attach call recording reference.
7. **Schedule the callback / appointment** — find a legal + free slot, book it, assign owner (self or skill-queue), set reminder. Check call-window legality (no calls before 08:00 / after 19:00 in collections).
8. **Fire the promised outbound** — trigger the SMS/WhatsApp/email the customer was promised (payment link, appointment confirmation, policy doc, complaint reference number). Verify the right template + language.
9. **Reconcile against the consent / DND / DPDP state** — did the customer consent to WhatsApp? Is the number on DND? Did they ask to be contacted only in Marathi? Honor it.
10. **Set the grievance / escalation trail** — if escalated, route to the right team with context; if grievance, generate the complaint reference and SLA per RBI/IRDAI.
11. **Self-check completeness** — "did I capture everything I promised? Is the amount right? Is the date legal?" A good agent re-reads before submitting.
12. **Mentally close the loop / context-switch** — release the call, prep for next. (Emotional reset — irrelevant to the machine, but it's why humans are slow here.)

The *atomic skills* underneath: taxonomy classification under ambiguity, faithful abstractive summarization, slot/entity extraction, multi-system data entry without typos, calendar arithmetic with legal constraints, template selection + language matching, consent/DND reconciliation, completeness verification.

---

## 2. Agent approach — exactly how a 2026 agent does each sub-step

Architecture: a **post-call durable workflow** triggered the instant the call/chat ends, taking `{transcript, diarized turns, ASR confidence, customer_id, channel, consent_state, call_window_meta}` as input. Pattern is **"extract → validate → act → verify,"** orchestrated on a durable-execution engine so every side-effect is idempotent and replayable.

| Human sub-step | Agent technique (named) |
|---|---|
| Recall call | No working-memory limit: full diarized transcript + retrieved customer context (prior tickets, PTP history, language pref) injected via RAG. |
| Disposition code | **Constrained classification** — LLM (Claude Sonnet 4.6 / GPT-4.1 / Gemini 2.5 Flash) with the disposition taxonomy as an enum in a **structured-output schema**; tool-use/JSON-schema forces one of N valid codes. For high-volume tenants, distill to a fine-tuned small classifier (Llama-3-8B / ModernBERT) for cost+latency. Ambiguity → multi-label + confidence; low confidence routes to HITL. |
| Call summary | **Grounded abstractive summarization** — length-controlled prompt; faithfulness enforced by grounding to transcript spans + a post-hoc factual-consistency check (QAFactEval-style / NLI verifier). Grounded summaries hit <2% hallucination ([Gistly, 2026](https://www.gistly.ai/blog/ai-hallucination-detection-contact-centers)). |
| Extract commitments | **Schema-constrained entity/slot extraction** — single structured-output call emitting `{ptp_amount, ptp_date, appointment_slot, callback_at, callback_reason, docs_to_send[], refund_amount, sla_due}`; enums + regex/date validators on the schema. |
| Update CRM | **Tool calls** against CRM API (Zoho Desk / Salesforce / Freshdesk) — typed function calling, idempotency key = `workflow_id:step_id`. |
| Create/update ticket | Tool call → ticketing API; dedupe against open cases via semantic + key match before create. |
| Schedule callback/appt | **Deterministic scheduling tool** (not the LLM doing date math) — a `book_slot()` activity that enforces RBI call-window (08:00–19:00 local), DND, agent/skill availability; LLM only chooses *intent* ("callback tomorrow afternoon"), code resolves to a legal slot. |
| Fire outbound | Template-selection tool: maps disposition + language → approved WhatsApp/SMS template (DLT-registered), substitutes vars, checks consent before send. **Never free-text the regulated message.** |
| Consent/DND reconcile | Pre-action **policy gate** — a deterministic guardrail layer that blocks any send/schedule violating consent, DND, DLT, or call-window before the side-effect runs. |
| Grievance/escalation | Routing tool → generates complaint ref, sets SLA, posts to escalation queue with summary context. |
| Completeness self-check | **LLM-as-judge / critic pass** — second model verifies "every promise in transcript has a corresponding scheduled action," emits a `promises_kept_checklist`; mismatch → revise or HITL. |
| Context switch | N/A (parallel workers; no reset cost). |

Orchestration backbone: **durable execution** so "schedule callback for the 28th" survives crashes, retries idempotently, and fires exactly once ([Temporal/LangGraph, 2026](https://appscale.blog/en/blog/durable-execution-llm-agents-temporal-langgraph-checkpointing-2026)).

---

## 3. Tooling — concrete 2026 stack

- **Summarization / disposition / extraction LLM:** Claude Sonnet 4.6 (tool-use structured output, <0.2% schema-failure across 300k calls — [DataChain/tokenmix, 2026](https://tokenmix.ai/blog/structured-output-json-guide)), GPT-4.1 / GPT-4o Structured Outputs (99.9%+ schema compliance — same source), or Gemini 2.5 Flash for cost/latency. Contact-center-tuned option: **Observe.AI** domain LLM.
- **Distilled disposition classifier (high volume):** fine-tuned Llama-3-8B / ModernBERT via Unsloth; serve on vLLM. (Llama-2-7B fine-tuned matched GPT-4 on call-summary faithfulness — [arXiv 2410.18624](https://arxiv.org/pdf/2410.18624).)
- **Faithfulness verifier:** NLI / QAFactEval-style checker or LLM-judge; DIAL-SUMMER-style hierarchical error taxonomy for eval ([arXiv 2602.08149](https://arxiv.org/pdf/2602.08149)).
- **Durable orchestration:** Temporal (Serverless Workers, OpenAI Agents SDK + Google ADK integrations announced Replay 2026) or LangGraph checkpointer; idempotency key = `workflow_id:step_id` ([Temporal, 2026](https://temporal.io/blog/build-resilient-agentic-ai-with-temporal)).
- **CRM / ticketing:** Zoho Desk API, Salesforce Service Cloud / Agentforce, Freshdesk — all India-native and Exotel/Ozonetel-integrated.
- **Telephony + outbound + scheduling:** Exotel (70M daily conversations, 7000+ Indian businesses), Ozonetel CloudAgent, Ameyo. WhatsApp via AiSensy / Gupshup (DLT + Meta-approved templates).
- **Calendar:** Google Calendar / Outlook APIs for appointment-type tenants; internal collections-management-system slot tables for collections.
- **Guardrail/policy layer:** deterministic rules engine (call-window, DND scrub against TRAI/DLT, consent ledger from DPDP consent manager — e.g. Consent.in / Leegality).
- **Observability/eval:** Braintrust / Promptfoo / Ragas for offline; per-tenant disposition-accuracy + promises-kept dashboards online.

---

## 4. Benchmarks (real numbers)

- **Structured-output reliability:** OpenAI Structured Outputs 99.9%+ schema compliance; Claude Sonnet 4.6 tool-use <0.2% failure over 300k calls; Gemini response-schema +60–100 tokens overhead [sourced — [tokenmix](https://tokenmix.ai/blog/structured-output-json-guide), [DataChain](https://datachain.ai/blog/enforcing-json-outputs-in-commercial-llms)].
- **Summary hallucination:** <2% when grounded to source transcript [sourced — [Gistly 2026](https://www.gistly.ai/blog/ai-hallucination-detection-contact-centers)]; ungrounded LLMs misstate facts up to ~82% in worst tasks [sourced — [SQ Magazine 2026](https://sqmagazine.co.uk/llm-hallucination-statistics/)] (i.e. grounding is mandatory).
- **Small-model parity:** fine-tuned Llama-2-7B ≈ GPT-4 on call-summary factual accuracy/completeness/conciseness [sourced — [arXiv 2410.18624](https://arxiv.org/pdf/2410.18624)].
- **ACW time saved:** up to 30 min/appointment of note-taking automated; ~6,000 hrs/yr/org in pilots [sourced — [CMSWire 2026](https://www.cmswire.com/contact-center/salesforce-launches-agentforce-contact-center-to-unify-ai-voice-and-crm/)].
- **End-to-end containment context:** 40–60% of *whole interactions* contained by voice agents today [sourced — [Salesforce 2026](https://www.salesforce.com/blog/ai-agent-trends-2026/)] — ACW automation runs *on top* of both contained and human-handled calls.
- **Disposition auto-coding accuracy:** ~90–96% top-1 on clean taxonomies; degrades on overlapping/ambiguous codes [estimate — extrapolated from grounded-classification + Observe.AI blind-eval framing].
- **Scheduling/promise-fire reliability:** durable-execution engines target exactly-once side effects (≥99.9% with idempotency keys) [estimate — Temporal SLA framing].

---

## 5. Failure modes (where the agent breaks)

1. **Ambiguous / multi-topic call → wrong disposition.** Call covers PTP *and* a dispute; agent picks one, mis-routes follow-up. Cause: single-label forcing + thin taxonomy.
2. **Hallucinated commitment.** Summary invents a PTP amount or date not actually agreed → illegitimate dunning, DPDP/RBI risk. Cause: ungrounded generation; the most dangerous failure here.
3. **Missed commitment (silent drop).** Customer was promised a callback/doc; extractor missed it → broken promise, repeat call. Cause: low-recall slot extraction, no critic check.
4. **Duplicate side-effects.** Retry after crash double-creates ticket or sends WhatsApp twice. Cause: non-idempotent activities.
5. **Illegal scheduling.** Callback booked 20:30 or to a DND number → TRAI/RBI violation. Cause: LLM doing date/legality math instead of deterministic gate.
6. **Wrong-language / wrong-template outbound.** Marathi customer gets Hindi template, or a non-DLT-approved message → blocked/penalized.
7. **Code-switch / regional ASR errors propagate.** Hinglish or Tamil-English transcript noise → wrong amounts/dates extracted.
8. **Stale CRM context → mis-merge.** Wrong customer record updated due to ID collision.
9. **Consent drift.** Customer revoked consent mid-call; ACW still fires WhatsApp. Cause: consent ledger not re-checked at action time.

---

## 6. Gap to full adaptation (what the agent still can't do as well as a human — and the path to close it)

**Where humans still win:**
- **Judgment on ambiguous dispositions** — a senior agent "knows" the *real* reason vs the stated one ("said callback but actually a hidden dispute"). Agents over-index on literal text.
- **Cross-call/relationship memory** — "this is the 3rd broken PTP; flag for legal/field-visit." Humans carry tacit account history; agents need it engineered in.
- **Taxonomy edge-cases & policy nuance** — new product, weird outcome the taxonomy doesn't cover; humans improvise a note, machine forces a wrong bucket.
- **Reading unspoken commitments** — customer implied they'd pay after salary on the 1st without explicitly stating a date; humans infer-and-confirm.

**Concrete path to close each gap:**
1. **Ambiguity:** move from single-label to **multi-label disposition + confidence**, add a learned router; mine 50k+ historically *human-corrected* dispositions per tenant as fine-tune data; calibrate so low-confidence → HITL micro-review (5-sec confirm, not full redo).
2. **Relationship memory:** build a **per-customer commitment ledger** (vector + structured) injected into every ACW; add a "broken-promise streak" feature → auto-escalation rule.
3. **Taxonomy gaps:** add an `OTHER + free-text` escape with **weekly clustering** of OTHER notes to propose new codes (human-approved) — closed-loop taxonomy growth.
4. **Implied commitments:** train extractor on **inferred-PTP** labels with a "confirm-on-next-touch" flag; the live agent step should explicitly confirm fuzzy commitments so ACW receives clean structure (push complexity upstream).
5. **Faithfulness:** ship the NLI/QAFactEval verifier as a hard gate — no commitment is acted on unless it's entailed by a transcript span (citation-anchored).

The realistic end-state: **disposition + summary + extraction + write-back + scheduling + outbound is fully automatable**; the residual human role shrinks to *exception adjudication* (low-confidence dispositions, novel cases, high-value/legal accounts).

---

## 7. HITL trigger (when a human MUST take over)

- Disposition confidence below tenant threshold (e.g. <0.85) **or** multi-label conflict on a *financial-consequence* code (PTP, refund, dispute, escalation).
- Faithfulness verifier flags a commitment not entailed by transcript.
- Any **high-value / legal-hold / complaint** account (RBI/IRDAI grievance → mandatory human sign-off on the trail).
- Consent/DND/call-window gate blocks an action the customer clearly requested (contradiction → human resolves).
- New disposition that falls into `OTHER` for a regulated outcome.
- First N weeks of a new tenant/queue (shadow-mode + human approval until accuracy SLA proven).

Otherwise: **fully automatable.** Routine PTP-confirmed, callback-requested, RNR, wrong-number, info-given dispositions with clean confidence need zero human.

---

## 8. Automation readiness: **8/10**

The mechanical core (summary, disposition, extraction, CRM/ticket write, scheduling, promised outbound) is production-ready on grounded LLMs + durable execution + deterministic guardrails — this is the most automatable step in the whole BPO journey. Held back from 9–10 by: (a) ambiguous-disposition judgment, (b) the *cost* of a hallucinated/missed financial commitment in a regulated context (zero-tolerance), (c) taxonomy/consent nuance per tenant. With a faithfulness gate + confidence-routed HITL, a confident **8 today**, trending 9 within a tenant after correction-data fine-tuning.

---

## 9. Build spec

**Implement:**
1. Event-triggered **durable ACW workflow** (Temporal/LangGraph) fired on `call.ended` / `chat.resolved`.
2. **Extraction service:** one structured-output call → `{disposition (enum), summary, commitments[], crm_fields, outbound_intents[], promises_checklist[]}`. Schema-validated (Pydantic) + date/amount validators.
3. **Faithfulness gate:** NLI/judge verifier; reject un-entailed commitments → HITL.
4. **Deterministic action layer:** idempotent tools `upsert_ticket()`, `update_crm()`, `book_callback()`, `send_template()` — each behind the **policy gate** (call-window 08:00–19:00 local, DND/DLT scrub, consent-ledger check, language-match).
5. **Promise-reconciliation critic:** assert every transcript commitment maps to a scheduled action; emit audit record.
6. **Audit trail:** immutable log of inputs, decisions, citations, actions (DPDP/RBI evidence).

**Data needed:**
- 20k–100k historical transcripts (Hindi/Hinglish/regional) with **human-assigned dispositions + notes** (gold labels) per tenant taxonomy.
- The tenant's disposition taxonomy + CRM/ticket field map + WhatsApp/SMS DLT-approved template library.
- Consent/DND ledger + call-window rules per product (collections vs sales vs service).
- Held-out human-corrected set for online drift eval.

**Eval metrics that gate ship:**
- **Promises-Kept Rate (primary):** % of transcript commitments with a correct, on-time, legal scheduled action. Gate ≥ **99%**.
- **Disposition top-1 accuracy** vs human gold ≥ **92%**; macro-F1 across rare codes ≥ 0.80.
- **Summary faithfulness:** hallucinated-fact rate ≤ **2%** (NLI/judge + human spot audit).
- **Commitment extraction recall ≥ 98%**, precision ≥ 97% on PTP/appointment/callback slots.
- **Side-effect idempotency:** 0 duplicate tickets/sends under fault injection.
- **Compliance:** 100% of scheduled/sent actions inside legal window + consent (hard gate — any violation = non-ship).

---

## 10. India specifics

- **RBI Fair Practices Code:** no collection calls before **08:00** or after **19:00** borrower-local-time; no third-party disclosure; preferred-language respect; mandatory grievance-redressal path. Every callback/appointment the ACW schedules MUST resolve to a legal window — done deterministically, not by the LLM ([Caller Digital regulatory map 2026](https://www.caller.digital/blog/voice-ai-india-regulatory-map-2026); [Exotel RBI-compliant flow](https://exotel.com/blog/rbi-compliant-ai-collections/)).
- **DPDP Act 2023 (Phase II rolling out by Nov 2026):** consent must be specific/informed/revocable; ACW must re-check the **consent ledger** before any WhatsApp/SMS/email; full audit trail required; penalties up to ₹250 cr. A 2–5% manual sample can't prove compliance — automated 100% logging is the selling point ([Gistly DPDP](https://www.gistly.ai/blog/dpdp-act-compliance-contact-centers); [DPDPA FAQ](https://www.dpdpa.com/dpdpa-faq.html)).
- **IRDAI Info & Cyber Security Guidelines 2023:** insurance tenants must fold DPDP into data governance — same consent/audit discipline on policy-doc sends and renewal callbacks.
- **TRAI / DLT:** every outbound SMS/WhatsApp template must be **DLT-registered + Meta-approved**; ACW selects from a pre-approved template set, never free-texts a regulated message.
- **Hinglish + regional code-switching:** transcripts mix Hindi-English (and Tamil/Telugu/Marathi/Bengali-English). Extraction must survive code-switch; amounts/dates spoken in mixed forms ("agle mahine ki पहली ko, paanch hazaar"). Use Indic-tuned ASR + extractors; keep the *summary/note* in English (agent-readable) but the *customer-facing outbound* in the customer's preferred language.
- **PTP (Promise-to-Pay) is the central commitment object** in Indian collections — elicit, confirm, log amount+date, and auto-schedule the follow-up + UPI payment-link send; this is the highest-value, highest-risk artifact this step produces ([Caller Digital NBFC playbook](https://www.caller.digital/blog/voice-ai-emi-collections-india-playbook)).
- **Stack reality:** Exotel/Ozonetel/Ameyo + Zoho Desk/Freshdesk + AiSensy/Gupshup WhatsApp is the dominant mid-market BPO plumbing — build connectors to these first.

---

## Sources
- [Salesforce Agentforce Contact Center — CMSWire, 2026](https://www.cmswire.com/contact-center/salesforce-launches-agentforce-contact-center-to-unify-ai-voice-and-crm/)
- [AI agent trends 2026 — Salesforce](https://www.salesforce.com/blog/ai-agent-trends-2026/)
- [Structured Output JSON Guide 2026 — TokenMix](https://tokenmix.ai/blog/structured-output-json-guide)
- [Enforcing JSON Outputs in Commercial LLMs — DataChain](https://datachain.ai/blog/enforcing-json-outputs-in-commercial-llms)
- [AI Hallucination Detection in Contact Centers — Gistly 2026](https://www.gistly.ai/blog/ai-hallucination-detection-contact-centers)
- [LLM Hallucination Statistics 2026 — SQ Magazine](https://sqmagazine.co.uk/llm-hallucination-statistics/)
- [Small-LLM Telephone Call Summarization — arXiv 2410.18624](https://arxiv.org/pdf/2410.18624)
- [DIAL-SUMMER dialogue-summary error eval — arXiv 2602.08149](https://arxiv.org/pdf/2602.08149)
- [Durable Execution for LLM Agents 2026 — AppScale](https://appscale.blog/en/blog/durable-execution-llm-agents-temporal-langgraph-checkpointing-2026)
- [Temporal resilient agentic AI](https://temporal.io/blog/build-resilient-agentic-ai-with-temporal)
- [Voice AI India Regulatory Map 2026 — Caller Digital](https://www.caller.digital/blog/voice-ai-india-regulatory-map-2026)
- [RBI-compliant AI collections — Exotel](https://exotel.com/blog/rbi-compliant-ai-collections/)
- [Voice AI EMI Collections India Playbook — Caller Digital](https://www.caller.digital/blog/voice-ai-emi-collections-india-playbook)
- [DPDP Act Compliance for Contact Centers — Gistly](https://www.gistly.ai/blog/dpdp-act-compliance-contact-centers)
- [DPDPA FAQ](https://www.dpdpa.com/dpdpa-faq.html)
- [Exotel integrations / Zoho-Freshdesk](https://exotel.com/products/integrations/)
- [Observe.AI — LLMs in contact centers](https://www.observe.ai/blog/evaluating-llms-in-contact-centers)

---
*Draft research note for review. Cited where possible; [estimate] elsewhere. Not investment advice.*
