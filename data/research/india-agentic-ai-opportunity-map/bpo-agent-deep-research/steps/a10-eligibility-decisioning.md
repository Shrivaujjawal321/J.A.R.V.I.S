# A10 — Eligibility Checks & Decisioning (business rules: can this customer get X?)

> Deep research dossier for the India-market, multilingual (Hindi + regional + Hinglish), RBI/IRDAI/DPDP-compliant, action-taking voice+chat contact-center agent for mid-market BPOs.
> Scope: **ONLY** the eligibility/decisioning micro-step — "given who this customer is and what they want, can they get it, under what conditions, and how do I justify that answer?"
> Date: 2026-06-24. Status: draft research note for review. Cited where possible; [UNSOURCED]/[estimate] elsewhere. Not legal or investment advice.

---

## 0. What this step actually is

Eligibility decisioning is the **judgment hinge** of a contact-center interaction. It sits *after* intent + identity/KYC are established and *before* the action (disburse loan, issue refund, upgrade plan, approve claim, waive fee, reschedule, port number). It answers a deterministic-flavoured question — "does this customer satisfy the policy to get X?" — but a skilled human wraps that deterministic core in a lot of soft work: collecting the missing fact, choosing *which* rule applies, spotting an exception path, explaining the "no" without losing the customer, and offering the next-best alternative.

The single most important architectural truth for 2026, repeated across the literature: **the LLM must NOT be the thing that decides.** "An LLM that decides whether to approve a loan is a regulatory liability… AI agents should be discrete, observable, swappable nodes, not the whole decision." (Source: MightyBot, "What Is a Policy Engine for AI Agents?", 2026, https://mightybot.ai/blog/what-is-a-policy-engine-for-ai-agents/). The decision itself belongs in a **deterministic policy/rules engine** (DMN, OPA/Rego, Cedar, or a domain rules engine). The LLM's job is to *gather facts, route to the right rule set, narrate the verdict, and handle exceptions* — never to compute the eligibility verdict from its weights.

This split — LLM for language + orchestration, deterministic engine for the verdict — is the spine of the whole build spec below.

---

## 1. Human micro-steps (the smallest atomic moves)

A skilled BPO agent doing an eligibility check actually executes ~14 micro-moves. Decomposed:

1. **Frame the ask precisely.** Convert a fuzzy request ("can I get more time on my EMI?") into a typed eligibility question (product = personal loan, action = EMI moratorium/restructuring, policy_id = hardship_v3). Cognitive: disambiguation + product mapping.
2. **Select the governing rule set.** Pick *which* policy applies — by product, customer segment (salaried vs self-employed), geography/state, channel, regulator (RBI vs IRDAI), and effective-date version. Wrong rule set = wrong answer that *looks* confident.
3. **Inventory required attributes.** Mentally list the facts the rule needs: tenure, DPD/bucket, CIBIL band, KYC status, existing exposure, income proof, age, cooling-off window, prior claims, plan-tenure, etc.
4. **Pull facts from systems.** Query CRM/LOS/policy admin/CIBIL/core-banking — note which are present, stale, or missing. Mechanical + verification.
5. **Detect missing/conflicting facts and ask the customer.** "Aapki last salary credit kab aayi thi?" — collect the one decisive missing input conversationally, not as a form dump.
6. **Verify/validate volunteered facts.** Decide whether a customer-stated fact (income, employment) can be trusted as-is or needs documentary/API verification before it can drive a decision. Risk/trust calibration.
7. **Run the rule (mentally or in tool).** Apply thresholds/branches: meets-all → eligible; fails-one → ineligible; near-miss → exception candidate.
8. **Identify the binding constraint.** When ineligible, pinpoint *the one* rule that failed (DPD > 30, CIBIL < 650, tenure < 6 months) — the "reason code" — because that drives both the explanation and the remedy.
9. **Check for exception / override paths.** Is there a discretion lever (waiver authority, supervisor override, alternate product, manual underwriting queue)? Skilled agents know the *unwritten* escalation map.
10. **Compute conditions & sub-limits.** Eligible-but-conditional: max amount, revised tenure, required co-applicant, premium loading, deductible. Decisioning is rarely binary; it's "yes, up to ₹X, if Y."
11. **Decide confidence & whether to commit.** Gauge "am I sure enough to *tell the customer yes/no and act*, or do I hedge / escalate?" Metacognition.
12. **Translate verdict into customer-appropriate language.** Render "fails hardship_v3 clause 4(b)" into empathetic Hinglish: "Sir, abhi aapka account 45 din se due hai, isliye is plan ke liye system allow nahi kar raha — lekin ek aur raasta hai…"
13. **Offer next-best alternative / remedy.** Down-sell, cure path ("clear ₹X to become eligible"), alternate product, or call-back-after-N-days. Retention move.
14. **Log the decision + reason + evidence.** Record what was decided, on which rule version, with which inputs — the audit trail. (Often the weakest human step; done sloppily.)

Emotional layer threaded through 5, 11, 12, 13: managing the customer's hope/anger when the answer trends to "no," and protecting the brand from a mis-sell or a false promise.

---

## 2. Agent approach (how a 2026 AI agent does each move)

Core pattern: **LLM-orchestrator + deterministic decision service**, with the LLM doing language/routing and a DMN/policy engine doing the verdict. Named techniques per micro-step:

| # | Human micro-step | 2026 agent technique |
|---|---|---|
| 1 | Frame the ask | Intent + slot classifier (fine-tuned small model or structured-output LLM) maps utterance → `{product, action, policy_id}` enum. Constrained decoding (XGrammar-2 / JSON-schema) to force valid enums. |
| 2 | Select rule set | **Policy router**: deterministic lookup keyed on (product, segment, state, channel, effective_date). LLM proposes, router validates against a registry; effective-date versioning is hard data, never inferred. |
| 3 | Inventory attributes | DMN decision table / rule metadata declares required inputs. Agent reads the schema, not its memory. |
| 4 | Pull facts | **Tool calling**: typed function calls to CRM/LOS/CIBIL/core-banking APIs. BFCL-style function calling; parallel calls where independent. |
| 5 | Ask for missing facts | **Slot-filling dialogue policy** — agent asks for exactly the missing decisive slot, one at a time, in the customer's language. |
| 6 | Verify volunteered facts | Trust-tier policy: customer-stated facts flagged `unverified`; rule engine treats them as provisional → triggers verification tool or HITL before commit. |
| 7 | Run the rule | **Deterministic DMN / OPA-Rego / Cedar evaluation.** Same inputs → same verdict, every time. LLM never computes the verdict. |
| 8 | Binding constraint / reason code | Engine returns structured `reason_codes[]` (which rule fired/failed). No LLM guessing why. |
| 9 | Exception paths | Policy engine encodes override matrix; agent can route to a `manual_underwriting`/`supervisor_waiver` queue node, not invent discretion. |
| 10 | Conditions & sub-limits | Decision tables emit `max_amount`, `tenure`, `loading`, `conditions[]` as structured outputs. |
| 11 | Confidence to commit | **Uncertainty-aware gating**: combine NLU confidence + data-completeness + whether any input is `unverified` → commit / clarify / escalate (cf. AT-CXR uncertainty-aware agentic triage, arXiv 2508.19322). |
| 12 | Translate verdict | LLM **grounded generation**: render structured verdict + reason_codes into empathetic Hinglish, constrained to only the facts in the decision payload (no hallucinated reasons). |
| 13 | Next-best alternative | Eligibility engine also runs *adjacent* product/cure rules in parallel → returns ranked alternatives; LLM narrates. |
| 14 | Log decision | Auto-emit immutable audit record: inputs, policy_id+version, verdict, reason_codes, model versions, timestamp, consent_ref. |

The "LLM authors rules, deterministic code executes them" pattern is the explicit 2026 consensus: "The AI is used only for parsing rules into structured data, not for runtime decisions, with all business logic execution as deterministic code." (Source: brain.co, "LLM-Generated Rules Engines," 2026, https://brain.co/blog/llm-generated-rules-engines-executable-if-then-logic-for-llm-explainability-in-regulated-industries).

Guardrail enforcement at the tool-call boundary: **OPA/Cedar** decide what the agent is *allowed* to do, independent of the LLM — "even if the agent is tricked into attempting a prohibited action, OPA blocks it before it reaches the target system." (Source: CodiLime, "Why Open Policy Agent is the Missing Guardrail for Your AI Agents," 2026, https://codilime.com/blog/why-use-open-policy-agent-for-your-ai-agents/). Microsoft's **Agent Governance Toolkit (Mar 2026)** packages this decoupling for production. (Source: same CodiLime/aport.io guardrails coverage, 2026.)

---

## 3. Tooling (concrete 2026 stack)

**Decision/rules layer (the verdict — must be deterministic):**
- **DMN engine**: Camunda 8 (BPMN+DMN, explicitly positioned for agentic orchestration with deterministic decision nodes — Source: Camunda, "Guardrails and Best Practices for Agentic Orchestration," Jan 2026, https://camunda.com/blog/2026/01/guardrails-and-best-practices-for-agentic-orchestration/), or open-source **kogito/drools**, or **GoRules / DecisionRules.io** (Source: DecisionRules.io top-10 BRE 2026).
- **Policy-as-code / authorization**: Open Policy Agent (Rego) or AWS Cedar at the tool-call boundary (Source: aport.io, "Best AI Agent Guardrails 2026," https://aport.io/blog/best-ai-agent-guardrails-2026-pre-action-authorization-compared/).
- **Optional formal layer for high-value commits**: Lean-4 theorem-proving guardrails for financial agents — "Type-Checked Compliance: Deterministic Guardrails for Agentic Financial Systems Using Lean 4" (Source: arXiv 2604.01483, 2026). Use for the small set of irreversible money-moving eligibility verdicts.

**Orchestration / agent layer:**
- LangGraph or Camunda-orchestrated graph; one node per micro-step; decision node calls DMN, not the LLM.
- **Structured outputs / constrained decoding**: XGrammar-2 dynamic structured generation (Source: arXiv 2601.04426) or provider JSON-schema mode, to force valid enums and tool args.

**Models (2026):**
- Orchestrator/narration LLM: Claude/GPT/Gemini frontier tier for Hinglish narration; a fine-tuned small model (e.g., Indic-tuned 7-12B) for intent/slot to cut latency/cost.
- Tool-calling reliability: pick by BFCL V4 standing (see §4).
- ASR for the voice channel: India-tuned STT (e.g., Sarvam/Bhashini-class, or Deepgram for telephony — Source: Deepgram contact-center STT, 2026).

**Data/integration:**
- Typed connectors to LOS/CRM/policy-admin/core-banking + bureau (CIBIL/Experian) — the lending stack already does this (Source: scnsoft, "AI for Lending 2026," https://www.scnsoft.com/lending/artificial-intelligence; roopya.money LOS guide 2026).
- Consent manager + audit store (DPDP-mandated, see §10).

**Eval/observability:**
- Hamming AI / Braintrust for voice-agent eval; Promptfoo/Inspect for the decisioning logic; golden decision-table test suite as a regression gate.

---

## 4. Benchmarks

- **Tool-calling accuracy (BFCL V4, Berkeley Function Calling Leaderboard):** top open model Llama 3.1 405B ~**88.5%** overall, 70B ~84.8%, 8B ~76.1% on the leaderboard snapshot reported; frontier closed models trade the top spots quarter-to-quarter (Source: llm-stats.com/benchmarks/bfcl; Berkeley BFCL, 2026, https://gorilla.cs.berkeley.edu/leaderboard.html). **Implication:** even best-in-class tool calling errs ~10%+ on complex/multi-turn calls — so the *verdict* must not depend on the LLM emitting the right call unverified; the deterministic engine + schema validation catch malformed calls.
- **Voice intent/NLU target:** execution-layer intent + tool-call accuracy target **>95%** for production contact-center voice agents (Source: Hamming AI, "Voice Agent Testing Guide 2026," https://hamming.ai/resources/voice-agent-testing-guide).
- **Latency (voice):** target **P95 < 800ms** voice-assistant response time; India sales-tuned agents claim **<0.8s latency, 4.23 MOS**, trained on 600M+ min of Indian calls (Source: SquadStack via Retell/Hamming roundups, 2026). Reality for cascaded STT→LLM→TTS over telephony is often P50 ~1.5–1.7s, P95 ~5s (Source: Hamming AI metrics guide) — the eligibility tool round-trip adds 100–600ms of API time on top [estimate].
- **Decision determinism:** a compiled policy engine "produces deterministic outputs… the same path for the same input type, every time" — effectively **100% reproducibility** on the verdict given identical inputs (Source: MightyBot policy-engine, 2026). This is the number that matters for audit: the *engine* is exact; only fact-gathering is probabilistic.
- **Lending speed when agentic + deterministic:** 2026 digital-lending apps report application-to-disbursal "measured in seconds" once eligibility is automated (Source: scnsoft AI-lending 2026; stashfin RBI 2026 guide). [Vendor-reported, treat as upper bound.]

---

## 5. Failure modes (where the agent breaks on THIS step)

1. **Stale rule set / wrong effective-date version.** Agent applies last quarter's policy; verdict is confidently wrong. Most dangerous because it's invisible to the customer.
2. **Wrong rule selected.** Right product, wrong segment (salaried rules on a self-employed applicant). Routing error, not a math error.
3. **Hallucinated reason / ungrounded justification.** LLM narrates a plausible-sounding reason that isn't the actual binding constraint → mis-explanation, compliance gap.
4. **Malformed / wrong tool call.** ~10%+ tail on BFCL means the agent fetches the wrong field or mis-orders parallel calls; if unvalidated, feeds garbage into the engine.
5. **Trusting unverified customer claims.** Customer overstates income; agent treats it as fact and approves → mis-sell/fraud exposure.
6. **Near-miss mishandling.** Treats a "fails by one day of DPD" as a flat no, missing the legitimate exception/cure path a human would catch — bad CX and lost revenue.
7. **Over-promising on conditional eligibility.** Says "yes" before the condition (co-applicant, document) is satisfied → false promise, IRDAI/RBI mis-sell liability.
8. **Silent data gaps.** A required attribute is NULL/stale; engine defaults it and decides anyway instead of pausing to collect.
9. **Code-switch / regional misparse.** Hinglish or regional number/date/amount ("dhai lakh", "saadhe teen percent") mis-extracted → wrong slot → wrong verdict.
10. **Prompt injection via volunteered text/documents.** Customer-supplied content tries to alter the decision ("system says I'm approved"). Mitigated only if the verdict lives in the engine, not the prompt.
11. **Audit log incompleteness.** Decision made but inputs/version/consent_ref not captured → fails RBI/DPDP audit even if the decision was correct.

---

## 6. Gap to full adaptation (what the agent still can't do as well as a human, and how to close it)

What a skilled human still beats the agent at, on THIS step:

- **A. Unwritten exception judgment.** Humans know "the supervisor will waive this for a 10-year customer." Agents only know codified rules. **Close it:** mine resolved-exception logs + supervisor-override records → train a *discretion-candidate classifier* that flags "this near-miss historically gets waived" and routes to the human-authority queue with the precedent attached. Don't let the agent auto-waive; let it *surface the lever* a human pulls. Data needed: 6–12 months of override/waiver tickets with outcomes.
- **B. Trust calibration on volunteered facts.** Humans sense when a stated income is fishy. **Close it:** a verification-need scorer (fact value vs segment distribution + channel risk) that decides per-fact whether to accept, API-verify, or HITL. Data: historical stated-vs-verified deltas + fraud labels.
- **C. Empathetic "no" + retention save.** Humans soften a rejection and convert it to a cure path. **Close it:** the engine already returns the binding reason_code + cure delta ("clear ₹4,200 → eligible"); fine-tune narration on top human-agent rejection transcripts that *retained* the customer. Eval on save-rate, not just accuracy.
- **D. Cross-policy reasoning / "what if".** Humans simulate "if you add a co-applicant, you'd qualify." **Close it:** run the decision tables in *counterfactual mode* (perturb inputs, re-evaluate) and surface the cheapest qualifying path. This is deterministic, so it's safe to automate.
- **E. Novel/edge cases with no rule.** Genuinely new situation with no codified policy. **Cannot close fully** — route to human, and feed the resolution back into the rule registry (closing the loop turns the gap into a rule next cycle).

The honest frame for Boss: the *verdict* (given clean inputs) is **already fully automatable and more reliable than a human** because it's a deterministic engine — humans make data-entry and version errors that the engine doesn't. The residual gap is entirely in (a) **getting clean, verified inputs**, (b) **discretion/exception judgment**, and (c) **the human warmth around a "no."** Those are the engineering targets, not "make the LLM smarter at deciding."

---

## 7. HITL trigger (when a human MUST take over)

Hand to a human when ANY of:
1. **Manual underwriting / discretion path** — a near-miss or override-candidate the rules flag as human-authority-only (waivers, premium loading judgment, hardship discretion).
2. **Unverified decisive fact** that can't be API-verified and materially changes the verdict (e.g., unverifiable income for a high-ticket loan).
3. **Irreversible high-value commit** above a money/risk threshold (large disbursal, claim approval) — even if eligible, require human sign-off (formal-verification or maker-checker gate).
4. **No applicable rule / conflicting rules** (policy gap or contradiction).
5. **Confidence gate fails** — NLU/extraction confidence or data-completeness below threshold.
6. **Customer disputes the verdict** / requests human (DPDP/RBI grievance-redressal right; customer can always demand a human).
7. **Regulator-sensitive products** where IRDAI/RBI requires human-in-loop disclosure or the company is liable for mis-sell.

The *eligible-and-fully-verified-and-below-threshold* path is fully automatable. Everything ambiguous, discretionary, irreversible, or disputed is HITL.

---

## 8. Automation readiness: **8 / 10**

Justification: the decision *computation* is a solved, deterministic problem (DMN/OPA/Cedar → 100% reproducible verdict) and is, given clean inputs, **more reliable than a human today**. Tool-calling to fetch facts is ~88–95% and rising, and the residual errors are *catchable* by schema validation + the engine refusing on incomplete inputs. What holds it back from 9–10: (a) input cleanliness/verification of volunteered facts, (b) unwritten-exception discretion, (c) regulatory requirement for human-in-loop on irreversible/high-value/regulator-sensitive commits, and (d) audit-trail completeness in production. For the **majority of standard eligibility checks** (plan upgrade eligibility, refund eligibility, fee-waiver within policy, standard loan pre-eligibility, claim-intimation eligibility) it is ship-ready behind the deterministic-engine pattern. For high-ticket lending/insurance *final approval*, it's a confident assist, not a replacement → that's why 8, not 10.

---

## 9. Build spec

**Implement:**
1. **Policy registry + DMN decision tables**, versioned by (product, segment, state, channel, effective_date). Author rules with LLM assistance; **execute deterministically** (Camunda DMN / GoRules / Drools). Each table declares: required inputs, reason_codes, conditions/sub-limits, override-eligibility flag.
2. **Policy router** — deterministic selection of the governing rule set; LLM proposes, registry validates; reject if no exact version match.
3. **Fact-gathering layer** — typed tool calls to CRM/LOS/bureau/core-banking with JSON-schema-constrained args; parallel where independent; each fact tagged `verified|unverified|stale|missing`.
4. **Slot-filling dialogue policy** — ask exactly the missing decisive slot, one at a time, in the customer's language.
5. **Decision service call** — engine returns `{verdict, reason_codes[], conditions[], max_amount?, alternatives[]}`; counterfactual mode for next-best path.
6. **Confidence/HITL gate** — combine NLU confidence + data-completeness + unverified-fact flags + value-threshold → commit/clarify/escalate.
7. **Grounded narration** — LLM renders verdict in Hinglish using ONLY the decision payload (no extra reasons); constrained generation.
8. **Guardrail boundary** — OPA/Cedar (and Lean-4 for money-moving commits) authorize the action before any system-of-record write.
9. **Immutable audit emitter** — inputs, policy_id+version, verdict, reason_codes, model versions, consent_ref, timestamp.

**Data needed:**
- Codified policy docs → decision tables (per product/segment/state, with effective dates).
- 6–12 months of resolved cases incl. override/waiver tickets + outcomes (for discretion classifier).
- Stated-vs-verified fact deltas + fraud labels (for trust scorer).
- Retained-after-rejection transcripts (for empathetic-narration tuning).
- A **golden decision-table test suite** — hand-labelled input→verdict pairs covering boundary/near-miss/exception cases.

**Eval metric that gates ship:**
- **Decision-correctness (gate): 100% match to golden decision tables** on the deterministic engine for codified cases — this is exact and non-negotiable (the engine is wrong only if a table is wrong).
- **End-to-end eligibility accuracy ≥ 98%** including fact-gathering (i.e., the agent fetches the right facts and routes to the right table); errors must be *conservative* (false-ineligible → escalate, never false-eligible commit).
- **Zero ungrounded reasons**: 0% hallucinated reason_codes vs engine output (LLM-as-judge + exact-match check).
- **Tool-call validity ≥ 99%** post-schema-validation; **>95% raw** intent/slot accuracy (Hamming target).
- **Voice latency P95 < 1.2s** end-to-end including the eligibility API round-trip [estimate target, vs <0.8s narration-only].
- **Audit completeness = 100%** of decisions logged with full required fields.
- **HITL-routing recall ≥ 99%** on the must-escalate set (no irreversible/high-value/disputed case auto-committed).

Ship gate = ALL of the above green on the golden suite + a shadow-mode run against live human decisions with ≤0.5% false-eligible disagreement.

---

## 10. India specifics

**Regulatory (this is where India diverges hard):**
- **RBI Digital Lending Directions (2025) + Model Risk Circular (Aug 2024):** credit/eligibility decisions must be **explainable** — "which data points were considered, what rules were applied, and why approved/rejected" — with mandatory **audit trails**, data localization in India, and KYC via V-CIP (Source: stashfin "Digital Loans & RBI Rules India 2026," https://www.stashfin.com/blogs/digital-loans-mobile-lending-apps-india-guide; scnsoft AI-lending 2026; RBI Digital Lending FAQs, https://www.rbi.org.in/commonperson/english/scripts/FAQs.aspx?Id=3413). The deterministic-engine + reason_codes pattern is essentially mandated, not optional.
- **IRDAI (2025/2026):** AI agents selling/renewing insurance must **disclose all material terms + cooling-off period**, and the **company remains liable for AI mis-sell**; IRDAI now mandates DPDP compliance and updated cyber rules (Source: autointerviewai "AI Calling India … Compliance Guide 2026," https://www.autointerviewai.com/blog/ai-calling-india-dpdp-trai-dlt-compliance-complete-guide-2026; medianama Apr 2026, https://www.medianama.com/2026/04/223-lowdown-insurers-comply-dpdp-irdai-updates-cyber-security-guidelines/). → Eligibility narration must include mandatory disclosures, not just the verdict.
- **DPDP Act 2023 + Rules 2025:** consent must be "free, specific, informed, unconditional, unambiguous" and **purpose-limited / data-minimized** — the agent may pull *only* the attributes the specific eligibility rule needs, must carry a `consent_ref`, and must keep audit trails (Consent Managers: 7 yrs; activity logs: 1 yr). Penalties up to **₹250 crore**. Substantive obligations phase in by ~May 2027; larger/higher-risk firms expected at maturity by mid-2026 (Source: Seclore DPDP guide 2025; EY DPDP 2023/2025; mondaq "DPDP 2026 Reality Check"). → Build per-rule **minimal-attribute manifests** so the agent never over-fetches.
- **TRAI DLT** for the voice channel (Principal Entity + header/template registration, DND scrubbing) governs outbound eligibility calls (Source: autointerviewai 2026).

**Language/Hinglish/regional:**
- **Number & amount parsing is a top failure source:** "dhai lakh" (2.5L), "saadhe teen" (3.5), "pauna" (¾), lakh/crore vs millions, "EMI", "kist", "byaaj" (interest), "DPD/bucket" in agent jargon vs customer plain speech. Slot extractor must be India-number-aware, not generic.
- **Code-switching:** customers state facts in Hindi/regional, products/policies are English-named ("hardship plan", "moratorium"). Intent/slot model must handle mid-sentence switch; use Indic-tuned ASR/NLU (Bhashini/Sarvam-class).
- **Date/tenure idioms:** "pichhle mahine", "do saal pehle", festival-relative dates — normalize before they hit a DPD/tenure rule.
- **Empathetic "no" register:** respectful forms ("aap", "kariye"), face-saving framing of rejection; a flat translated "you are ineligible" reads as rude and raises grievance/escalation rates. Narration tuning on Indian retention transcripts matters here specifically.
- **Trust nuance:** customers volunteer income/employment verbally far more than they upload documents → the §6-B trust scorer is *more* load-bearing in India than in document-heavy markets.

---

## Sources
- MightyBot — What Is a Policy Engine for AI Agents? (2026): https://mightybot.ai/blog/what-is-a-policy-engine-for-ai-agents/
- brain.co — LLM-Generated Rules Engines (2026): https://brain.co/blog/llm-generated-rules-engines-executable-if-then-logic-for-llm-explainability-in-regulated-industries
- CodiLime — Why OPA is the Missing Guardrail for AI Agents (2026): https://codilime.com/blog/why-use-open-policy-agent-for-your-ai-agents/
- aport.io — Best AI Agent Guardrails 2026: https://aport.io/blog/best-ai-agent-guardrails-2026-pre-action-authorization-compared/
- Camunda — Guardrails & Best Practices for Agentic Orchestration (Jan 2026): https://camunda.com/blog/2026/01/guardrails-and-best-practices-for-agentic-orchestration/
- DecisionRules.io — Top 10 Business Rule Engines 2026: https://www.decisionrules.io/en/articles/top-10-business-rule-engines/
- Berkeley BFCL leaderboard / llm-stats: https://gorilla.cs.berkeley.edu/leaderboard.html · https://llm-stats.com/benchmarks/bfcl
- arXiv 2601.04426 — XGrammar-2 structured generation
- arXiv 2604.01483 — Lean-4 deterministic guardrails for agentic financial systems
- arXiv 2508.19322 — AT-CXR uncertainty-aware agentic triage
- Hamming AI — Voice Agent Testing Guide / Metrics (2026): https://hamming.ai/resources/voice-agent-testing-guide
- SCNSoft — AI for Lending 2026: https://www.scnsoft.com/lending/artificial-intelligence
- Stashfin — Digital Loans & RBI Rules India 2026: https://www.stashfin.com/blogs/digital-loans-mobile-lending-apps-india-guide
- RBI — Digital Lending FAQs: https://www.rbi.org.in/commonperson/english/scripts/FAQs.aspx?Id=3413
- autointerviewai — AI Calling India DPDP/TRAI/RBI/IRDAI Compliance 2026: https://www.autointerviewai.com/blog/ai-calling-india-dpdp-trai-dlt-compliance-complete-guide-2026
- medianama — IRDAI/DPDP cyber rules (Apr 2026): https://www.medianama.com/2026/04/223-lowdown-insurers-comply-dpdp-irdai-updates-cyber-security-guidelines/
- Seclore / EY / mondaq — DPDP Rules 2025 compliance guides

---
Draft research note for review. Cited where possible; [UNSOURCED]/[estimate] elsewhere. Not investment advice.
