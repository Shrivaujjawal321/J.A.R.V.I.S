# Gap Step 06 — Concurrent Multi-Session Context Isolation & Blending Discipline (the Concurrency-Safety Boundary)

**Domain:** India-market, multilingual (Hindi + regional + Hinglish) voice + chat contact-center agent for mid-market BPOs, action-taking (servicing, collections, sales, money movement).
**Compliance envelope:** DPDP Act 2023 + DPDP Rules 2025 (purpose limitation, data minimisation, breach notification, Significant-Data-Fiduciary obligations), RBI cloud/outsourcing + data-localisation expectations, SEBI/IRDAI segregation duties, PCI-DSS scope for card data, ISO 27001 / SOC 2 multi-tenancy controls, OWASP LLM Top-10 (LLM02 sensitive-information-disclosure, LLM06 excessive agency, LLM08 vector/embedding weaknesses).
**Scope of this doc:** ONLY the concurrency-safety boundary — *guaranteeing that, while one agentic system serves many simultaneous customers, no customer A's data, answer, slot-value, retrieved chunk, KV-cache state, tool result, or memory write ever leaks into customer B's call or chat* — PLUS the inverse discipline: *correctly RE-blending the same caller's own context across channels / repeat calls in a short window* (the legitimate stitch) without over-merging two different people. **Distinct from B05 (memory architecture / personalization)** and **A09 (multi-turn context memory):** those two maximise *recall and continuity within a customer's own thread* (remember more, personalize better). THIS step is the *opposite-signed guardrail* — it constrains memory/state so the right context reaches the right session and ONLY that session. B05 asks "did we remember enough?"; this asks "did we leak, and did we stitch the right person?" The two are in productive tension: every gain in shared/global memory raises the contamination surface this step must police.
**Last researched:** 2026-06-24.

---

## 0. Why this is a distinct, high-risk micro-step (not "just memory architecture")

A single human agent is a *physically serial* device: one mouth, one screen, one call at a time. Customer A's data simply cannot fall out of the human's mouth into Customer B's call, because the human is not in Customer B's call. The agent's memory leaks (mis-remembering, calling the customer the wrong name) are bounded to *that one conversation*. The whole class of "wrong customer's data in the wrong session" bug **does not exist for a serial human** — it is *created* the moment one model/process serves N callers concurrently. That is why this is a genuinely new micro-step, not a digitised version of an old one.

Five structural reasons it must be owned separately:

1. **It is a concurrency bug class, not a competence skill.** Every other BPO step (greet, listen, resolve, sell, comply) has a human analogue you can be "good or bad" at. This one has *no human analogue at the failure surface* — it is the price of parallelism. A contact-center AI handling 7,000+ concurrent sessions has 7,000 ways to cross a wire that one human never had ([Salesforce Engineering — 7K sessions without cross-team interference](https://engineering.salesforce.com/building-a-multi-tenant-ai-agent-platform-handling-7k-sessions-without-cross-team-interference/)).

2. **The failure is silent and the model looks correct.** In a **cross-session leak**, "the model returns valid data, but to the wrong user, because the system fails to enforce boundaries between user sessions" — the output is fluent, confident, well-formed, and catastrophically wrong-addressee ([Giskard — Cross-Session Leak](https://www.giskard.ai/knowledge/cross-session-leak-when-your-ai-assistant-becomes-a-data-breach)). There is no slurred speech, no "umm," no tell. QA listening to Customer B's call hears a perfect sentence containing Customer A's loan balance.

3. **It spans four leak planes the memory step never touches.** Contamination can travel through (a) the **KV-cache / inference layer** (vLLM/SGLang concurrent requests reusing stale cache), (b) the **shared-state / orchestration layer** (global variables, shared slot store, inter-agent messages, tool arguments), (c) the **retrieval / vector layer** (a query in session B retrieving session A's embedded chunk), and (d) the **logging / observability layer** (traces, debug output, transcripts written to the wrong partition). Memory architecture (B05) lives mostly in (c); this step polices all four ([arXiv 2605.11202 — fuzzing vLLM/SGLang found KV-cache isolation failures](https://arxiv.org/html/2605.11202); [Giskard](https://www.giskard.ai/knowledge/cross-session-leak-when-your-ai-assistant-becomes-a-data-breach)).

4. **It carries the inverse risk too — over-isolation AND under-isolation are both failures.** Strict isolation that *fails to re-blend the same caller's own context* across an IVR-to-voice-to-WhatsApp hop in 90 seconds produces the "why are you making me repeat myself?" failure — repeat-contact rates and CSAT collapse ([CX Today — omnichannel resets the journey](https://www.cxtoday.com/contact-center/omnichannel-cx-continuity-customer-journey-context/)). The discipline is *two-sided*: never merge two people, always merge one person with themselves. Identity-resolution mistakes go both ways.

5. **In India it is simultaneously a DPDP breach event and an RBI/SEBI segregation event.** A leak isn't just a CX miss — under DPDP 2023 a wrong-recipient disclosure is a reportable **personal-data breach**, and for a regulated-entity tenant (bank/NBFC/insurer) it can breach **outsourcing-segregation** duties. The same wire-cross is two regulators' problem at once ([DLA Piper — India data protection](https://www.dlapiperdataprotection.com/?t=law&c=IN); [Scrut — DPDP Rules 2025 checklist](https://www.scrut.io/post/dpdp-rules)).

---

## 1. Human micro-steps (the atomic decomposition)

Two things to capture: (a) the **thin** set of things a human *does* that maps to isolation (humans get most of this for free from serial physiology), and (b) the **identity-stitch** behaviours humans do consciously — which is where the real human skill lives and where the agent must replicate.

1. **Single-thread attention (the free isolation)** — a human is on exactly one call; A's data is never in B's airspace. (Agent must *manufacture* this guarantee that the human gets from biology.)
2. **Screen / record discipline** — before speaking sensitive data, glance at the screen to confirm *this* CRM record belongs to *this* caller; don't read out the balance from the record left open from the previous call.
3. **Wrap-before-next** — finish disposition + close the previous customer's record *before* accepting the next call; don't carry stale context (the prior caller's name, mood, problem) into the new greeting.
4. **Name/context reset reflex** — actively flush the previous caller's name and details; the classic human error is "Hello Mr. Sharma" to a Ms. Gupta because Sharma was the last call. Good agents consciously reset.
5. **Repeat-caller recognition (the legitimate stitch)** — recognise "you called this morning about the same thing" and pull *that* thread forward, so the customer doesn't re-explain. Conscious, valued skill.
6. **Cross-channel recognition** — "I see you also messaged us on WhatsApp / you were just on the IVR / your email is open" — knit the *same person's* other touchpoints into one continuous service moment.
7. **Identity-confidence judgement** — decide whether the person now on the line is *really* the same person as the prior touchpoint (same number, but is it the account-holder or a family member?) before merging history — the human's fraud-aware caution against over-merging.
8. **Selective carry-forward** — bring forward what's *relevant and permitted* (the open complaint) but NOT what's irrelevant or sensitive-out-of-context (don't volunteer "last time you called about your divorce" on a billing call).
9. **Account-vs-caller disambiguation** — when one phone number maps to a joint account / family / shared SIM, keep *whose* request is whose straight; don't apply the husband's instruction to the wife's policy.
10. **Hold/parallel-task hygiene** — when juggling a hold + an after-call note + a chat (the human's limited concurrency), keep the two customers' notes in the right fields; don't paste A's note into B's record.
11. **Verbal slip-catch** — if the wrong name/detail starts to come out, catch and correct it mid-sentence ("sorry, I mean..."), and recognise the near-miss.
12. **End-of-call teardown** — log out of / close the record so the next agent (or next call on a shared terminal) doesn't inherit residual PII on screen.

---

## 2. Agent approach (how a 2026 AI agent does each sub-step)

The agent does NOT get isolation for free — it must *engineer* the serial human's biological guarantee across a massively parallel substrate. The approach is **defence-in-depth across the four leak planes**, plus a **probabilistic identity-resolution layer** for the legitimate stitch.

| # | Human sub-step | 2026 agent technique |
|---|----------------|----------------------|
| 1 | Single-thread attention | **Per-session execution context keyed by an immutable `session_id` (UUID) bound at call/chat ingress**, threaded through every component. No mutable global conversation state shared across sessions; each turn carries its own context object. Isolation is enforced by **embedding tenant + session identifiers directly into storage keys**, so every read/write validates the boundary ([Giskard](https://www.giskard.ai/knowledge/cross-session-leak-when-your-ai-assistant-becomes-a-data-breach); [Spheron — per-customer isolation](https://www.spheron.network/blog/multi-tenant-llm-serving-gpu-cloud/)). |
| 2 | Screen/record discipline | **Server-side authority binding:** the agent never "remembers" whose record this is from context — it resolves account data fresh from `{tenant_id, verified_customer_id}` set at the auth step (A02), so the data plane is keyed to the *verified* identity, not to whatever the LLM "thinks." Tool calls inject `customer_id` from the trusted session context, never from model-generated text. |
| 3 | Wrap-before-next | **Stateless worker / context teardown:** worker context (and any per-session scratch memory) is destroyed or quarantined on session end; new session = fresh context object. No carry-over of the prior session's prompt, slots, or retrieved chunks. |
| 4 | Name/context reset | **No cross-session prompt accumulation:** the system prompt + history window are reconstructed per session from that session's verified store only. The "Mr. Sharma to Ms. Gupta" error is structurally impossible if no prior-session string is in the new context. |
| 5 | Repeat-caller stitch | **Identity-resolution / CDP layer:** ANI/CLI + verified identity → **golden-profile lookup** in a customer-data-platform (Segment Unify / Twilio-class) that stitches recent interactions into one timeline; a short-window "recent-session" join pulls the morning's open thread forward ([Twilio Unify](https://segment.com/product/unify/); [Twilio — identity resolution](https://www.twilio.com/en-us/blog/insights/identity-resolution)). |
| 6 | Cross-channel recognition | **Unified conversation timeline** across voice/chat/WhatsApp/IVR keyed to the resolved identity, so the agent opens "where the last interaction ended" ([Fini — omnichannel synced history](https://www.usefini.com/guides/ai-customer-support-agents-omnichannel-synced-history); [DevRev — omnichannel 2026](https://devrev.ai/blog/omnichannel-customer-support)). |
| 7 | Identity-confidence judgement | **Match-confidence scoring + step-up:** the resolution layer emits a confidence; low confidence (number matches but no verification, or fraud-sentinel doubt) → **do NOT auto-merge history**, fall back to re-auth (A02) before exposing any prior-session PII. Prevents over-merge → leak-to-impostor. |
| 8 | Selective carry-forward | **Purpose-scoped context injection (DPDP-aligned):** only the *task-relevant, lawful* slice of profile is injected into the prompt — data-minimisation as a code constraint, not LLM discretion. Sensitive out-of-context fields are withheld by policy ([S&R — DPDP data minimisation](https://www.snrlaw.in/navigating-data-minimization-requirements-under-indias-dpdp-act/)). |
| 9 | Account-vs-caller disambiguation | **Caller≠account modelling:** session context distinguishes `verified_caller_id` from `account_id`/`policy_id`; authority checks (shared with A02 / fraud gate) gate which sub-entity's data/actions are permitted. |
| 10 | Hold/parallel-task hygiene | **N/A for serial-human limits, but the agent's analogue is sub-agent / tool-call isolation:** each parallel tool call or sub-agent carries the session's scoped credentials; tool *arguments* and *results* are tagged with `session_id` and validated on return so a slow tool result can't land in another session's turn ([researcher note — contamination via tool arguments / inter-agent messages](https://www.giskard.ai/knowledge/cross-session-leak-when-your-ai-assistant-becomes-a-data-breach)). |
| 11 | Verbal slip-catch | **Output egress guard:** a lightweight check before TTS/send verifies named entities / account numbers in the *response* belong to the *current* session's verified customer (entity-vs-session consistency), blocking a response that references a foreign `customer_id`. This is the agent's "catch it mid-sentence." |
| 12 | End-of-call teardown | **Per-session log/trace partitioning + cache eviction:** transcripts, traces, and KV/prefix caches are partitioned by `{tenant, session}` and evicted/segregated on teardown; `--disable-log-requests`-class hardening prevents prompt cross-contamination in logs ([Spheron / vLLM hardening](https://www.spheron.network/blog/multi-tenant-llm-serving-gpu-cloud/)). |

**Reference architectural pattern (2026) — the four-plane isolation stack + a stitch layer:**

```
                         INGRESS  →  session_id (UUID) + tenant_id bound, immutable
                                       │  verified_customer_id set at A02 auth
            ┌──────────────────────────┼───────────────────────────────────────┐
   PLANE 1  │ INFERENCE   per-session KV/prefix-cache scoping; NO cache reuse    │
            │             across session_id (KV-cache isolation hardening)       │
   PLANE 2  │ ORCHESTRATION  per-session context object; no global mutable state;│
            │             tool args/results tagged + validated by session_id     │
   PLANE 3  │ RETRIEVAL   vector queries filtered by {tenant_id, customer_id}    │
            │             metadata predicate — no unfiltered ANN over all tenants│
   PLANE 4  │ OBSERVABILITY  logs/traces/transcripts partitioned by {tenant,sess}│
            └──────────────────────────┼───────────────────────────────────────┘
                                        │
                EGRESS GUARD: entity-in-response ∈ this session's customer? else BLOCK
                                        │
   STITCH LAYER (CDP/identity-resolution): same verified person's recent
   touchpoints merged into one timeline; LOW match-confidence → re-auth, no merge
```

The LLM **never decides isolation**. The session boundary is a deterministic property of the runtime keys; the model is just a tenant of a correctly-partitioned house.

---

## 3. Tooling (concrete 2026 stack)

**Session / orchestration isolation**
- **LangGraph / Pipecat** FSM where each call spawns a *fresh graph state* keyed by `session_id`; no module-level mutable globals (the #1 prototype footgun). Per-session `RunnableConfig`/thread-id discipline.
- **Stateless worker model** (one ephemeral worker context per session) or hardened pooled workers with explicit context reset between sessions.
- **Inference**: vLLM / SGLang with **per-session KV-cache scoping**, `--disable-log-requests`, prefix-cache keyed so cross-session prefix sharing cannot leak; watch for the documented KV-cache isolation CVE-class ([arXiv 2605.11202](https://arxiv.org/html/2605.11202); [Spheron](https://www.spheron.network/blog/multi-tenant-llm-serving-gpu-cloud/)).

**Retrieval isolation**
- **Vector DB with metadata-filtered ANN** (Qdrant / Milvus / pgvector + `WHERE tenant_id = ? AND customer_id = ?` pre-filter, or per-tenant collections/namespaces). Never run an unfiltered nearest-neighbour search over a shared index — that is the embedding-leak path (OWASP LLM08).

**Identity resolution / stitch**
- **CDP**: Twilio Segment **Unify**, or a contact-center-native identity-resolution layer; ANI + verified-ID → golden profile + recent-interaction join window (e.g. 24–72h) ([Twilio Unify](https://segment.com/product/unify/)).
- **Unified conversation timeline** across voice/chat/WhatsApp/IVR; LoginRadius/Twilio-class identity graph with match-confidence ([LoginRadius — omnichannel identity](https://www.loginradius.com/blog/identity/omnichannel-customer-experience)).

**Egress / guardrails**
- **NeMo Guardrails / Guardrails-AI** + a custom **entity-vs-session consistency check** (NER over the draft response → assert all account numbers / names / IDs belong to `verified_customer_id`).
- **PII tooling**: Microsoft Presidio for detection at log/trace boundaries.

**Observability with isolation**
- **Langfuse / OpenTelemetry traces partitioned per tenant+session**; trace isolation treated as a compliance requirement, not a nice-to-have ([Cresta — Langfuse tracing for agents](https://cresta.com/blog/observability-for-ai-agents-tracing-multi-service-llm-pipelines-with-langfuse)).

**Adversarial testing**
- **LLM-serving fuzzers** (vLLM/SGLang fuzzing harness) + bespoke **concurrency soak + cross-session red-team** (see Build Spec) ([arXiv 2605.11202](https://arxiv.org/html/2605.11202)).

---

## 4. Benchmarks (with tags)

- **Cross-session-leak rate (the headline metric):** target **0 leaks per N sessions** — this is a *zero-tolerance* metric, not an accuracy %; the build gate is "0 cross-session disclosures across a 100k-session adversarial soak." [estimate — no public industry SLA standard; derived from DPDP zero-breach posture]
- **Production scale precedent:** multi-tenant agent platforms operating **7,000+ concurrent sessions without cross-team interference** is a documented engineering target ([sourced — Salesforce Engineering](https://engineering.salesforce.com/building-a-multi-tenant-ai-agent-platform-handling-7k-sessions-without-cross-team-interference/)).
- **Serving-layer vulnerability base rate:** a single fuzzing campaign surfaced **15 vulnerabilities** in vLLM/SGLang including **KV-cache isolation failures** and cross-request interference — i.e. the contamination surface is *empirically real* at the inference layer, not theoretical ([sourced — arXiv 2605.11202](https://arxiv.org/html/2605.11202)).
- **Stitch-side business lift (the inverse metric):** proper unified-profile / identity-stitch implementations report **first-call resolution +34%** and **repeat contacts −28%**; strong-omnichannel firms retain **89% vs 33%** of customers ([sourced — DevRev / industry, directional](https://devrev.ai/blog/omnichannel-customer-support)).
- **Over-merge (false-stitch) rate:** target **<0.1%** of stitches merge two distinct identities; gated by match-confidence threshold tuning. [estimate]
- **Egress-guard latency budget:** the entity-vs-session check must fit the ~300–500ms voice turn budget; NER-on-draft adds ~10–40ms on a small model. [estimate]

> Honest gap: there is **no published, standardised "cross-session leak rate" leaderboard** the way there is for ASR WER or RAG faithfulness. This step's benchmark is *internal and adversarial*, which is itself a maturity signal — the industry hasn't converged on a public metric for the single highest-severity failure of multi-tenant agents.

---

## 5. Failure modes (where the agent breaks)

- **KV-cache / prefix-cache bleed** — concurrent requests on the same GPU reuse stale KV state; one session's tokens influence another's generation ([arXiv 2605.11202](https://arxiv.org/html/2605.11202)).
- **Shared mutable global state** — a module-level dict / singleton holding "current customer" that two coroutines stomp on under load; classic async footgun. The leak only appears *under concurrency*, so it passes every single-session test.
- **Unfiltered vector retrieval** — an ANN query in session B returns session A's embedded transcript chunk because the index is shared and the metadata pre-filter was missing or mis-applied (OWASP LLM08).
- **Tool-result misrouting** — a slow/async tool call returns after the orchestrator has context-switched, and the result is appended to the wrong session's turn ([Giskard — contamination via tool arguments](https://www.giskard.ai/knowledge/cross-session-leak-when-your-ai-assistant-becomes-a-data-breach)).
- **Log / trace cross-contamination** — transcripts or debug traces written to the wrong tenant partition; "a contract violation and a potential regulatory event" even after PII redaction ([Spheron](https://www.spheron.network/blog/multi-tenant-llm-serving-gpu-cloud/); [Cresta](https://cresta.com/blog/observability-for-ai-agents-tracing-multi-service-llm-pipelines-with-langfuse)).
- **System-prompt / cross-tenant prompt leakage** — shared prompt infrastructure leaking one tenant's instructions/data into another ([WitnessAI — system-prompt leakage](https://witness.ai/blog/llm-system-prompt-leakage/)).
- **OVER-isolation (the inverse failure)** — strict isolation that refuses to stitch the same caller's IVR→voice→WhatsApp hop, forcing repeat-explanation, tanking FCR/CSAT ([CX Today](https://www.cxtoday.com/contact-center/omnichannel-cx-continuity-customer-journey-context/)).
- **OVER-merge / wrong-stitch** — ANI-only matching merges a family member or SIM-recycled number into the account-holder's profile → exposes A's data to B who happens to hold A's old number; an *isolation failure dressed as personalization*.
- **Joint-account / shared-number confusion** — applying one party's instruction to the other party's product on a shared phone number.
- **Residual-context teardown miss** — a pooled worker not reset between sessions carries the prior caller's slots into the next greeting.
- **Embedding-space inference** — even without raw-data leak, a shared embedding store can let one tenant infer another's data distribution (subtle, OWASP LLM08).

---

## 6. Gap to full adaptation (what the agent still CANNOT do as well as a human — and the path to close it)

**Where the human still wins:** A human's isolation is *free and absolute by physiology* — you cannot, even in principle, leak Customer A into Customer B's call because you are not in two calls at once. The human's failure ceiling is a *verbal slip* (says the wrong name, catches it, apologises) — recoverable, single-recipient, and obvious. The agent's failure ceiling is a *silent, fluent, machine-speed, many-recipient* disclosure that nobody hears until an audit or a complaint. So at the *worst-case severity* axis, the human is structurally safer; the agent trades the human's serial safety for parallel throughput.

**But the human is far worse at the stitch side:** a human cannot hold a 72-hour, cross-channel, golden-profile memory of every touchpoint; humans routinely make customers repeat themselves and *do* commit the "Mr. Sharma" slip. So the agent, done right, *beats* the human on stitch (continuity) while needing engineering to *match* the human on isolation (safety). The frontier is making the agent's isolation as boringly reliable as the human's biology while keeping the agent's superhuman stitch.

**Concrete path to close the gap:**
1. **Make isolation a runtime invariant, not a model behaviour** — bind `{tenant, session, verified_customer}` into every storage key, cache key, retrieval filter, and trace partition; treat any code path that can read state without those keys as a P0 bug.
2. **Ship an egress consistency guard** — NER-on-draft + assert-entity-belongs-to-session before every TTS/send; this is the agent's recoverable "slip-catch" that the human has natively.
3. **Adopt zero-tolerance adversarial testing** — concurrency soak + cross-session red-team + serving-layer fuzzing as a *release gate*, because the bug is invisible to single-session QA.
4. **Tune the stitch with confidence + step-up** — solve over-merge with match-confidence thresholds that fall back to re-auth, gaining the human's fraud-caution at the merge point.
5. **Formalise the leak SLO** — define and publish (internally) a cross-session-leak SLO of 0 and breach-drill it like a security incident, so the org treats it with security gravity, not CX gravity.

Closing the gap is overwhelmingly an **engineering + testing** problem, not a model-capability problem — which is why this step is *closeable to human-parity-or-better* faster than the judgement-heavy steps (A07, gap-04), provided the isolation discipline is treated as non-negotiable infrastructure.

---

## 7. HITL trigger (when a human MUST take over)

- **Any detected or suspected cross-session leak** → immediate **kill-switch / circuit-break** of the affected worker/pool + human security + DPC-breach-assessment path (potential reportable DPDP breach). This is a *security incident*, not a transfer.
- **Low identity-match confidence on a sensitive request** → don't auto-merge prior context; route to re-auth, and on repeated failure to a human for manual identity verification.
- **Joint-account / coercion ambiguity about whose instruction applies** → human (shared with fraud gate / vulnerable-customer gate).
- **Stitch dispute** ("this isn't my account / I never called about this") → human, because a wrong-stitch may itself be a leak.
- **Egress guard blocks a response** repeatedly for a session → human, because the model is trying to emit foreign-entity data (possible contamination in flight).

Not "human listens to every call" — humans own the *incident response, the ambiguous-identity decision, and the breach assessment*, which the agent must not self-clear.

---

## 8. Automation readiness — **6 / 10**

**Why not higher:** The *failure severity* is maximal (silent multi-recipient PII disclosure = simultaneous DPDP + RBI/SEBI event), the bug class is *invisible to ordinary QA* (only concurrency soak + red-team find it), and the serving layer (vLLM/SGLang) has *documented, empirically-found* KV-cache isolation vulnerabilities — i.e. the substrate itself can leak even when your app code is correct. A naive "just give each call a session_id" implementation *will* leak under load via globals, unfiltered retrieval, or cache bleed. That keeps it short of plug-and-play.

**Why not lower:** This is fundamentally a *well-understood engineering discipline* (multi-tenancy is a solved-shape problem in SaaS) with mature tooling (CDP stitch, metadata-filtered vector search, per-tenant tracing, guardrails). A competent team that treats isolation as a runtime invariant + adversarial release gate *can* reach near-zero leak at scale (the 7K-session precedent exists). The stitch side already *beats* humans. So it's highly automatable **with discipline** — the readiness is gated by engineering rigour and test culture, not by any missing model capability.

---

## 9. Build spec (concrete)

**What to implement**
1. **Session context object** keyed by immutable `session_id` (UUID) + `tenant_id`, with `verified_customer_id` set only by the A02 auth step. Threaded through every component; **ban module-level mutable conversation state** (lint rule + code review gate).
2. **Four-plane isolation:**
   - *Inference:* vLLM/SGLang with per-session KV/prefix-cache scoping + `--disable-log-requests`; pin a serving config that the fuzzing harness has cleared.
   - *Orchestration:* per-session graph state in LangGraph/Pipecat; tool calls inject `customer_id` from trusted context (never from model text); tool results validated against `session_id` on return.
   - *Retrieval:* vector store with **mandatory `{tenant_id, customer_id}` metadata pre-filter** (or per-tenant namespaces); CI test that asserts no unfiltered query path exists.
   - *Observability:* Langfuse/OTel traces + transcripts partitioned by `{tenant, session}`; redaction (Presidio) at the log boundary.
3. **Egress consistency guard:** NER over the draft response → assert every account number / name / customer ID ∈ current session's `verified_customer_id`; BLOCK + alert on mismatch.
4. **Identity-resolution / stitch layer:** CDP (Segment Unify-class) golden profile + recent-interaction join (configurable 24–72h window) + **match-confidence score**; low confidence → re-auth, never silent merge. Purpose-scoped (DPDP-minimised) context injection.
5. **Teardown:** destroy/quarantine per-session context + evict caches on session end; reset pooled workers explicitly.
6. **Kill-switch:** circuit-breaker that quarantines a worker/pool on any egress-guard mismatch or leak alarm.

**Data needed**
- ANI/CLI → identity graph + verified-ID mapping; recent-interaction event stream across channels; per-tenant data-handling agreements (some tenants forbid cross-channel merge entirely); joint-account / authorised-rep maps.

**Eval metric to gate it (release gates):**
- **Gate A — Isolation:** **0 cross-session disclosures** across a ≥100k-session concurrency soak + cross-session red-team + serving-layer fuzz. Any single leak = no ship.
- **Gate B — Egress guard:** ≥99.9% catch of injected foreign-entity responses in the red-team, with false-block rate low enough to fit the turn budget.
- **Gate C — Stitch quality:** false-merge (over-stitch) rate <0.1%; legitimate-stitch recall high enough to move FCR/repeat-contact in A/B.
- **Gate D — Latency:** egress guard + retrieval filter within the ~300–500ms voice turn budget at p95 under peak concurrency.

**Test design (the load-bearing part):**
- **Concurrency soak:** N parallel synthetic callers with distinguishable, traceable PII tokens (canary balances / canary names); automated scan asserts no canary from session i ever appears in session j's transcript/log/trace.
- **Cross-session red-team:** adversarial callers who try to elicit "the last caller's" data; prompt-injection attempts to break tenant/session boundary.
- **Serving-layer fuzz:** run the vLLM/SGLang fuzzing harness against the pinned inference config before every serving upgrade ([arXiv 2605.11202](https://arxiv.org/html/2605.11202)).
- **Stitch precision/recall set:** labelled same-person / different-person pairs across channels (incl. joint accounts, recycled SIMs) to tune match-confidence.

---

## 10. India specifics

- **DPDP 2023 + Rules 2025 make a leak a reportable breach.** A wrong-recipient disclosure is a **personal-data breach** with notification obligations; data-minimisation and purpose-limitation are statutory, so the *stitch* must inject only purpose-relevant fields (don't carry the divorce/health note into a billing call) — minimisation is a code constraint, not a courtesy ([S&R — DPDP minimisation](https://www.snrlaw.in/navigating-data-minimization-requirements-under-indias-dpdp-act/); [Scrut — DPDP Rules 2025](https://www.scrut.io/post/dpdp-rules); [DLA Piper](https://www.dlapiperdataprotection.com/?t=law&c=IN)). Phased enforcement runs into 2027, so the compliance posture must be built now, not retrofitted.
- **Significant Data Fiduciary (SDF) bar:** a large BPO handling banking/insurance volumes may be designated an SDF, pulling in DPIA + audit + DPO duties — the leak SLO becomes auditable, not just internal.
- **RBI / SEBI / IRDAI outsourcing-segregation:** for a regulated-entity tenant, a cross-tenant or cross-customer leak can breach **outsourcing-segregation and data-localisation** expectations — the BPO is processing on the regulated entity's behalf, and segregation between *different banks' tenants* on the same platform is a hard requirement (one NBFC must never see another's customers). Multi-tenant isolation here is *inter-competitor*, the highest-stakes variant.
- **Shared-SIM / recycled-number reality:** India has high SIM churn and family-shared / shared-device usage, so **ANI-only stitch is dangerous** — a recycled number stitched to the prior owner's account is a real, common leak path. Verified-ID + match-confidence + step-up is mandatory, not optional, in the Indian number ecosystem.
- **Joint / family accounts & authorised representatives:** common in Indian banking/insurance; caller≠account-holder is frequent, so the caller-vs-account disambiguation (sub-step 9) carries more weight here than in single-holder Western markets.
- **Multilingual stitch:** the same customer may transact in Hindi on voice and English on WhatsApp; the unified timeline must merge across *language* too, and the egress guard's NER must handle Devanagari/Romanised names so entity-vs-session checks don't silently fail on Indic strings.
- **Data-localisation:** the multi-region cache-locality problem (route a request to a node holding another region's cache) intersects RBI localisation — session routing must respect both cache affinity *and* data-residency, or you trade a leak risk for a localisation breach ([TianPan — multi-region cache locality](https://tianpan.co/blog/2026-04-17-multi-region-llm-serving-data-residency-routing)).

---

## Sources

- [Giskard — Cross-Session Leak: when your AI assistant becomes a data breach](https://www.giskard.ai/knowledge/cross-session-leak-when-your-ai-assistant-becomes-a-data-breach)
- [Salesforce Engineering — Multi-tenant AI agent platform, 7K+ sessions without cross-team interference](https://engineering.salesforce.com/building-a-multi-tenant-ai-agent-platform-handling-7k-sessions-without-cross-team-interference/)
- [Spheron — Multi-Tenant LLM Serving: per-customer isolation, token quotas (2026)](https://www.spheron.network/blog/multi-tenant-llm-serving-gpu-cloud/)
- [arXiv 2605.11202 — Continuous Discovery of Vulnerabilities in LLM Serving Systems with Fuzzing (KV-cache isolation failures in vLLM/SGLang)](https://arxiv.org/html/2605.11202)
- [Cresta — Observability for AI Agents: tracing multi-service LLM pipelines with Langfuse](https://cresta.com/blog/observability-for-ai-agents-tracing-multi-service-llm-pipelines-with-langfuse)
- [WitnessAI — LLM System Prompt Leakage prevention (2026)](https://witness.ai/blog/llm-system-prompt-leakage/)
- [Twilio Segment Unify — identity resolution / golden profile](https://segment.com/product/unify/)
- [Twilio — Identity resolution: what it is and how it works](https://www.twilio.com/en-us/blog/insights/identity-resolution)
- [Fini — Omnichannel AI support agents: synced history](https://www.usefini.com/guides/ai-customer-support-agents-omnichannel-synced-history)
- [DevRev — Omnichannel customer support: the complete guide for 2026](https://devrev.ai/blog/omnichannel-customer-support)
- [CX Today — Why your omnichannel keeps resetting the customer journey](https://www.cxtoday.com/contact-center/omnichannel-cx-continuity-customer-journey-context/)
- [LoginRadius — Fix omnichannel CX with identity](https://www.loginradius.com/blog/identity/omnichannel-customer-experience)
- [S&R Associates — Navigating Data Minimization under India's DPDP Act](https://www.snrlaw.in/navigating-data-minimization-requirements-under-indias-dpdp-act/)
- [Scrut — India's DPDP Rules 2025: practical guide + checklist](https://www.scrut.io/post/dpdp-rules)
- [DLA Piper — Data protection laws in India](https://www.dlapiperdataprotection.com/?t=law&c=IN)
- [TianPan — Multi-region LLM serving: the cache locality problem](https://tianpan.co/blog/2026-04-17-multi-region-llm-serving-data-residency-routing)

---
Draft research note for review. Cited where possible; [estimate]/[unverified] elsewhere. Not investment advice.
