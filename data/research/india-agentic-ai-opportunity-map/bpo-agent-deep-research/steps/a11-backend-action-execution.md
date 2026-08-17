# Step A11 — Backend Action Execution (refund / ticket / KYC update / plan change in core systems)

> Deep-research dossier for an India-market, multilingual (Hindi + regional + Hinglish), RBI/IRDAI/DPDP-compliant, action-taking voice+chat contact-center agent for mid-market BPOs.
> Scope: **ONLY** the moment where the agent stops talking and *writes to a system of record* — issues a refund, creates/updates a ticket, pushes a KYC update to CKYCR/CBS, or changes a customer's plan in the billing/policy core.
>
> This is the highest-stakes micro-step in the whole pipeline. Everything upstream (ASR, NLU, intent, policy lookup) is *read-only and reversible*. This step is **irreversible side-effects on money, identity, and contracts**. The engineering bar is therefore "exactly-once, policy-gated, audited" — not "good conversation."

Last updated: 2026-06-24

---

## 0. Why this step is different from every other step

Every other step in a contact-center agent is a *reasoning/communication* problem with a soft failure mode (say the wrong thing → apologize, retry). This step is a *transaction* problem with a hard failure mode (double-refund ₹50,000, wrong customer's KYC overwritten, plan downgraded without consent → regulatory breach + financial loss + chargebacks).

The mental model shift: **the LLM is NOT the executor.** The LLM is a *proposer*. A deterministic, idempotent, policy-gated execution layer is the executor. The 2026 SOTA pattern is unambiguous on this: **propose-then-commit**, where "commit" runs strict checks (idempotency keys, precondition validation, post-action verification) outside the model. (Source: StackAI, "Human-in-the-Loop AI Agents," 2026; Agno, "HITL controls that run in production," 2026.)

---

## 1. Human micro-steps (what a skilled BPO agent actually does)

A trained agent at an Indian BPO (think a senior CSR at a Teleperformance/Concentrix/iEnergizer process for an NBFC, telco, or insurer) does NOT just "click refund." Decomposed to atomic moves:

1. **Re-confirm the resolved intent out loud** — "Sir, toh main aapke last recharge ka ₹299 refund process kar raha hoon, theek hai?" (verbal read-back of the exact action + amount + target before touching the system). This is a consent + error-trap gate.
2. **Authority/eligibility self-check** — mentally checks: *am I allowed to do this?* (refund < ₹X needs no supervisor; > ₹X needs L2 approval; this plan-change requires retention-desk override; this KYC field I can edit, that one is locked).
3. **Pull the correct record** — searches the CRM/CBS by phone/account/policy number, and **disambiguates** when multiple matches appear (same name, joint account, two policies). Picks the *right* row. This is where humans silently prevent the worst errors.
4. **Pre-condition / state read** — checks current state before writing: is the refund already processed? Is there a pending ticket for the same issue? Is the account frozen/under-litigation? Is KYC already up to date? Is the customer in a contract lock-in?
5. **Compute the exact payload** — refund amount (gross vs net of GST/charges), refund channel (back-to-source UPI vs wallet vs bank), effective date of plan change (immediate vs next cycle), KYC field deltas (only the changed fields), ticket category/priority/queue routing.
6. **Capture & verbalize the authorization artifact** — reads back the OTP / takes verbal consent / notes the consent token; for KYC, confirms the document reference; logs *who authorized and how*.
7. **Execute the write** — submits the form / fires the transaction in CBS/CRM/billing. Often across *two screens* (e.g., raise ticket in CRM **and** trigger refund in payment gateway).
8. **Watch for the system response** — reads the success/failure code on screen, spots "transaction timed out," "insufficient float," "duplicate reference," "account locked," "downstream gateway down."
9. **Reconcile partial failure** — if the refund fired but the ticket didn't save (or vice versa), the human *knows the dependency* and fixes the dangling half (re-raises the ticket, or doesn't double-fire the refund). This is implicit saga/compensation reasoning.
10. **Generate & read back the proof** — captures the reference/ARN/SR number and *speaks it to the customer*: "Aapka refund reference 3092… hai, 5-7 working days mein aa jayega."
11. **Log the disposition + notes** — writes the call disposition, attaches the action, free-text notes for the next agent ("customer irate, refund as goodwill, do not repeat").
12. **Decide on escalation** — if anything is off (amount too high, eligibility unclear, system erroring), *stops* and warm-transfers to L2/supervisor with context rather than forcing the write.

Notice: steps 3, 4, 8, 9, 12 are where human judgment quietly carries the load. They are *not* in the happy path and are exactly where naive agents break.

---

## 2. Agent approach (how a 2026 agent does each sub-step)

The architecture is a **constrained tool-calling agent behind a deterministic execution gateway**. Map to the human micro-steps:

| Human micro-step | 2026 agent technique |
|---|---|
| 1. Verbal read-back of action | LLM generates a **structured action proposal** (JSON: `{action, target_id, amount, channel, effective_date}`) → TTS reads it back → captures explicit "haan/yes" as a **consent token** (propose-then-commit gate). |
| 2. Authority/eligibility check | **Policy-as-code** at the gateway: Open Policy Agent (OPA/Rego) or Cedar evaluates `(action, amount, agent_scope, user_scope)`. Agent's effective authority = **intersection of agent baseline scopes ∩ delegated user scopes** (OAuth 2.1 token-exchange). Deny-by-default. (Source: Strata Maverics AI Identity Gateway with embedded OPA; Arcade per-action authorization, 2026.) |
| 3. Pull correct record + disambiguate | Read-only tool call (`lookup_customer`) → if >1 match, agent runs an **explicit disambiguation turn** (DOB/last-4/PIN) before any write tool is even *exposed* in the tool list. |
| 4. Pre-condition / state read | Mandatory **read-before-write**: a `get_state(target_id)` tool call whose result is fed back; gateway enforces precondition validation (e.g., `refund_status != 'PROCESSED'`). |
| 5. Compute exact payload | LLM proposes; **deterministic validators** (Pydantic v2 / Zod schemas + business-rule functions) recompute amounts server-side. The model's number is *checked*, never trusted — recompute GST/net server-side. |
| 6. Auth artifact capture | OTP verification tool, or DPDP **consent-artifact** call (consent manager issues a signed token). The token id is attached to the transaction. |
| 7. Execute the write | **Single idempotent tool call** with a client-generated `idempotency_key` (deterministic hash of `customer+action+amount+session`). Multi-system writes wrapped as a **saga** with declared compensations. |
| 8. Watch system response | Structured response parsed by code (not LLM). Typed error envelope (`{code, retryable, message}`). |
| 9. Reconcile partial failure | **Saga orchestrator** (Temporal / LangGraph durable checkpoint) auto-runs compensating actions; agent narrates, doesn't improvise the recovery. |
| 10. Read back proof | Reference number returned in the tool response → TTS reads it; logged. |
| 11. Log disposition | Auto-generated structured disposition + summary written to CRM via tool; immutable audit row appended. |
| 12. Escalate | Policy/confidence threshold breach → **deterministic HITL handoff** with full transcript + proposed payload, never a silent guess. |

**Core pattern named:** *Propose → Validate (policy + schema + precondition) → Confirm (consent token) → Commit (idempotent, saga-wrapped) → Verify (post-action read) → Log (immutable audit).* The LLM only owns "propose" and "narrate." Everything load-bearing is deterministic code.

**Model layer (2026):** the *proposer* LLM is whatever tops tau2-bench/BFCL for the language mix — Gemini 3.5 Flash (tool-calling leader at 42.4) or Claude Opus 4.8 (41.9) for the reasoning-heavy proposal; a cheaper fine-tuned function-calling model (e.g., a fine-tuned Llama / Qwen / Sarvam for Hindi) for routine single-action calls. (Source: awesomeagents.ai Function Calling Leaderboard, June 2026; llm-stats.com tool-calling leaderboard, 2026.)

---

## 3. Tooling (concrete 2026 stack)

- **Tool/connector layer:** **MCP (Model Context Protocol)** servers as the standard tool interface — Salesforce Hosted MCP Servers (GA April 2026), plus Stripe/Razorpay, ServiceNow/Zendesk, and **custom MCP servers wrapping the CBS / policy admin / billing core**. MCP registry + approval + audit layer for write scopes. (Source: WorkOS MCP 2026; Salesforce MCP GA, 2026; MCP 2026 roadmap.)
- **Execution / durability:** **Temporal** (durable workflows, automatic retries, saga compensation) or **LangGraph** durable checkpoints for HITL pause/resume at high-risk nodes.
- **Authorization / policy:** **OAuth 2.1 token-exchange** for delegated scoped tokens (TTL in hours, deny-by-default); **Open Policy Agent (Rego)** or **AWS Cedar** for per-action policy; **WorkOS FGA / Arcade / Strata Maverics** as the agent-authorization gateway.
- **Schema / validation:** Pydantic v2 (Python) or Zod (TS) for payload schemas; server-side recompute functions for money fields.
- **Idempotency:** Stripe/Razorpay-style idempotency keys; Redis/DB dedup table keyed on `idempotency_key`.
- **Consent (DPDP):** a **Consent Manager** (DEPA-style / account-aggregator-pattern consent artifact) issuing signed, purpose-bound, time-bound consent tokens.
- **Audit:** append-only immutable log (e.g., signed events to an audit store / WORM bucket) with full `(agent_id, user_id, action, payload, policy_decision, consent_token, result, ref_no, timestamp)`.
- **Voice glue (India):** Sarvam / Bolna / Gnani / Caller Digital (TRAI/DPDP-compliant templates) for the streaming voice loop; the action layer sits behind it. (Source: Caller Digital "Top 10 Voice AI Agents India 2026.")
- **Eval/guardrail:** tau2-bench-style policy-adherence harness in CI; DeepEval/Confident-AI for tool-call + task-completion + trace evals.

---

## 4. Benchmarks (real numbers)

- **Tool-calling leaderboard (June 2026):** Gemini 3.5 Flash **42.4**, Claude Opus 4.8 **41.9**, Llama 3.1 405B **41.0** on the composite function-calling benchmark. [sourced — awesomeagents.ai, June 2026]
- **tau2-bench Airline (policy-adherence, harder):** Claude 3.7 Sonnet **56.0%**, Claude Opus 4.1 **54.0%** pass@1 on the airline domain. [sourced — Holistic Agent Leaderboard / tau2-bench, 2026] — note: this is *single-attempt* on a *policy-strict* benchmark; it directly models "did the agent take the right action AND obey the policy."
- **Reliability decay (pass^k):** a 90% pass@1 agent drops to **~57% at k=8** — i.e., 8-in-a-row success is far lower than headline. [sourced — tau-bench pass^k definition, Sierra, 2026] This is *the* number that matters for write actions: you ship on pass^k, not pass@1.
- **Voice end-to-end latency (with mid-call tool execution):** **580–640ms** across 200 test calls on leading 2026 stacks; third-gen streaming pipelines keep total under **800ms**. [sourced — Retell AI benchmarking, 2026] A core-system write adds the backend round-trip on top (typically 300ms–3s for CBS/payment APIs) → must be masked with a verbal filler ("ek second, main process kar raha hoon…").
- **Enterprise API task realism:** new 2026 benchmarks (Agent-Diff state-diff eval, World-of-Workflows) specifically measure *correct state mutation* on enterprise APIs rather than text answers — the right eval class for this step. [sourced — arXiv 2602.11224, 2601.22130]
- **Double-execution / reversal rate:** vendors now measure "tool executed without error or reversal" as the headline action metric. [sourced — Dialpad/UJET agentic CX, 2026] No published clean industry baseline for refund double-fire rate — **[estimate]** target: < 0.05% double-execution with idempotency keys (Stripe-class infra achieves effectively 0 with proper keys).

---

## 5. Failure modes (where the agent breaks)

1. **Wrong-record write (disambiguation miss)** — picks the wrong account/policy among look-alikes and refunds/edits the wrong customer. Highest-severity, lowest-noise failure.
2. **Hallucinated payload** — LLM invents an amount, channel, plan code, or KYC value not grounded in the read-state. Mitigated by server-side recompute, but the *proposal* can still mislead the consent read-back if the validator is missing a rule.
3. **Double execution** — retry after a timeout fires the action twice (the classic refund-twice). Only idempotency keys prevent it; agents that "retry the tool" naively will double-fire.
4. **Partial-saga orphan** — refund succeeds, ticket save fails (or KYC pushes to CBS but not CKYCR). Without saga compensation the customer record is left inconsistent.
5. **Policy bypass under social pressure** — caller insists "your colleague approved ₹10k last time"; a weak agent rationalizes past the amount cap. tau2-bench shows even top models violate stated policy a meaningful fraction of the time.
6. **Stale precondition** — reads state, then a human/another channel changes it before the write (race). Needs optimistic-concurrency / conditional writes.
7. **Latency-masking failure on voice** — backend takes 3s, agent goes silent, customer thinks call dropped and disconnects mid-write.
8. **Consent ambiguity** — captures "haan" that was answering a different question; weak consent-token binding lets an un-consented action through (DPDP breach).
9. **Downstream error mis-narration** — gateway returns "insufficient float," agent tells customer "done, refund processed." Trust + compliance failure.
10. **Schema drift** — CBS/CRM API changes a field; tool call silently sends wrong/empty value. Needs contract tests.

---

## 6. Gap to full adaptation (what the agent still can't do as well as a human — and how to close it)

**Where humans still win:**

- **Cross-system implicit reconciliation under ambiguity.** A senior human *knows* that "refund fired but ticket failed" means "don't re-refund, just re-raise ticket," even on a novel two-system combo it's never seen. Agents only handle the saga compensations you *explicitly declared*. Undeclared partial-failure paths = agent flounders.
  - *Close it:* mine 6–12 months of human action logs + reversal/rework tickets to enumerate the real partial-failure transitions; encode each as an explicit Temporal compensation. Build a "saga coverage" metric (% of observed real-world failure transitions with a defined compensation). Gate ship at e.g. ≥ 99% coverage of historical failure modes.

- **Disambiguation with weak signals.** Humans use accent, prior-call memory, "the wife usually calls about this policy" — soft context to pick the right record. Agents need hard keys.
  - *Close it:* fuse CRM 360 + voice-biometric speaker ID + prior-interaction memory into the lookup tool so the agent has more disambiguation signal; force a confirm-turn whenever match confidence < threshold.

- **Discretion / goodwill judgment.** Humans bend rules with judgment (waive a fee for a loyal customer). Agents must stay inside policy-as-code.
  - *Close it:* this is *not* a gap to close blindly — encode an explicit **discretion budget** (e.g., agent may issue goodwill ≤ ₹200, > that → HITL). Make the boundary a policy, not a model guess.

- **Reading the regulatory edge.** A human senses "this KYC change smells like account takeover fraud" and stops. Agents need explicit fraud signals.
  - *Close it:* wire a fraud/risk-score tool (device, velocity, anomaly) into the precondition read; high score → mandatory HITL.

**The honest frontier:** the agent can match or beat humans on *declared, common, well-instrumented* actions. It cannot yet match a senior human on *novel cross-system failures, fraud intuition, and discretionary goodwill*. The path to closing it is **data + explicit encoding**, not a bigger model: every human override and every rework ticket is a labeled example of a missing rule. Build the loop that turns those into new policy/compensation code, and the gap shrinks monotonically.

---

## 7. HITL trigger (when a human MUST take over)

Not fully automatable today. Mandatory HITL when **any** of:

- Action **amount/impact exceeds policy cap** (e.g., refund > ₹X; bulk plan change; KYC change to a high-risk field like registered mobile/PAN).
- **Disambiguation confidence below threshold** (couldn't uniquely + confidently identify the record).
- **Consent/OTP failed or ambiguous.**
- **Precondition anomaly** (account frozen, under litigation, fraud score high, duplicate-in-flight).
- **Saga partial failure with no declared compensation** (orphan state).
- **Policy engine returns DENY or INDETERMINATE.**
- **Repeated downstream error** (idempotent retry budget exhausted).
- **Customer explicitly requests a human** / regulatory category requiring human (some IRDAI grievance closures).

Below all those thresholds and for **declared, capped, low-risk actions** (small refunds, standard ticket creation, address-line KYC update with valid OTP, like-for-like plan change), the step runs **auto with audit + post-action verify**.

---

## 8. Automation readiness: **5 / 10**

Reasoning: the *mechanics* (idempotent execution, policy gating, saga, audit) are production-ready and arguably **safer than humans** (no fat-finger, perfect logging). But *autonomous, high-confidence, unsupervised* write to money/identity systems across the messy long-tail — fraud edges, undeclared partial failures, discretion — is **not** there. With a tight policy-cap + HITL-above-threshold design, the *capped happy path* is an 8/10; the *full unsupervised replacement of a senior agent's judgment* is a 3/10. Blended, weighted toward the high-stakes irreversibility: **5/10**. (Contrast: upstream read/reasoning steps are 7–8.)

---

## 9. Build spec

**What to implement:**

1. **Action Gateway service** (deterministic, language-agnostic) exposing each write as an MCP tool: `issue_refund`, `create_ticket`, `update_kyc`, `change_plan`. Each tool: requires `idempotency_key`, runs schema validation (Pydantic v2), precondition read, OPA/Cedar policy check, consent-token verification, then executes; returns typed `{status, ref_no, error}`.
2. **Propose-then-commit loop:** LLM emits a *proposal object*; service returns a human-readable confirmation string; voice/chat layer captures consent → binds consent token → commit. Block commit until consent recorded.
3. **Saga orchestrator (Temporal/LangGraph):** multi-system actions with declared compensations; durable checkpoints; HITL pause node.
4. **Authorization:** OAuth 2.1 token-exchange, scoped per action, TTL ≤ 1h, deny-by-default; effective scope = agent ∩ delegated-user.
5. **Immutable audit log** of every attempt (incl. denied/escalated).
6. **HITL console** for above-threshold actions with full transcript + proposed payload + one-tap approve/reject/edit.

**Data needed:**
- 6–12 months of historical human action logs (action type, payload, outcome, reversals, reworks) → mine partial-failure transitions + amount distributions to set caps.
- Full business-rule catalog per action (refund eligibility, GST/net rules, plan-change effective-date rules, KYC editable-field matrix, queue routing).
- CBS/CRM/payment API contracts (OpenAPI) for tool schemas + contract tests.
- Labeled consent/OTP flows.

**Eval metric that gates ship (must all pass before this step goes live):**
- **Action correctness (state-diff):** ≥ 99.5% correct target+payload on a held-out replay set (Agent-Diff-style state-diff eval).
- **Policy adherence:** 100% — *zero* policy violations on the tau2-bench-style harness for this domain (any violation blocks ship).
- **Reliability:** **pass^8 ≥ 0.95** on the capped happy-path suite (not pass@1).
- **Double-execution rate:** 0 in a 10k-call idempotency stress test (forced timeouts/retries).
- **Partial-failure recovery:** 100% of *declared* failure transitions auto-compensate; ≥ 99% of *historically observed* failure transitions are declared.
- **HITL escalation precision/recall:** recall ≥ 0.99 on must-escalate cases (missing one is worse than over-escalating).
- **Latency:** action proposal-to-commit p95 < 3s with voice filler covering any gap.

If any gate fails → ship the step in *suggest-only* mode (agent proposes, human commits) until it passes.

---

## 10. India specifics (Hinglish / regional / regulatory)

- **DPDP Act (Rules notified 2025):** the BPO's client is a **Data Fiduciary**; KYC/plan/refund writes touching personal data need a **purpose-bound, time-bound consent artifact**. Bind every write to a consent token; expose data-principal rights (correction/erasure) as actions too. (Source: ksandk DPDP-for-NBFCs; Protean Video-KYC checklist 2026.)
- **RBI KYC (Master Direction, 2026 updates):** KYC updates pushed to core must also flow to **CKYCR** (Central KYC Records Registry) — uploads required on new *and* amended records; CKYC Identifier reused across REs *on consent*. Re-KYC/periodic-updation writes are a distinct action class. Video-KYC writes must capture live location + simulate real-time face-to-face. (Source: HyperVerge RBI KYC 2026; Protean; RBI Master Direction FAQs.)
- **IRDAI:** policy/plan changes and grievance closures have category-specific human-touch and TAT requirements → keep certain dispositions HITL.
- **TRAI:** voice channel itself must be TRAI/DPDP-compliant (consent for the call, DND); Indian vendors (Caller Digital, Sarvam, Bolna, Gnani) ship this. (Source: Caller Digital 2026.)
- **Refund channels:** India-specific routing — UPI back-to-source (ARN/RRN), IMPS/NEFT, wallet — the payload must pick the *original* instrument; reference numbers (UTR/ARN/RRN) must be read back.
- **Hinglish/regional read-back:** the *confirmation + reference read-back* (steps 1 & 10) must be in the caller's register — "Aapka ₹299 ka refund 5-7 working days mein aa jayega, reference number teen-zero-nine-two…" — with digit-by-digit reference spelling in Hindi/regional, and code-switching. The *payload/audit* stays in English/structured. Number/amount handling across Hindi spoken forms ("ढाई sau" = 250, "sava sau" = 125) is a known ASR/NLU trap that must be normalized **before** it reaches the payload validator — never let spoken-number ambiguity reach a money field.
- **Language ≠ action layer:** keep the deterministic gateway language-agnostic; only the proposer-LLM and TTS handle Hinglish/regional. A Hindi/Indic-tuned function-calling model (Sarvam-class) reduces proposal errors on Hinglish intents.

---

## Sources
- awesomeagents.ai — Function Calling Benchmarks Leaderboard (June 2026)
- llm-stats.com — Best AI for Tool Calling 2026
- Sierra Research — tau2-bench (GitHub) + pass^k reliability metric, 2026
- Holistic Agent Leaderboard — tau-bench Airline scores, arXiv 2510.11977
- arXiv 2602.11224 — Agent-Diff (state-diff enterprise API eval)
- arXiv 2601.22130 — World of Workflows (enterprise system world-models)
- StackAI / Agno / AlignX — Human-in-the-loop & propose-then-commit patterns, 2026
- WorkOS / Salesforce — MCP in 2026, Salesforce Hosted MCP GA (April 2026)
- Strata Maverics + OPA / Arcade per-action authorization / WorkOS FGA — agent authorization, 2026
- Dev.to (Arcade) — OAuth 2.1 / OIDC delegated access for agents, 2026
- Retell AI — voice agent latency benchmarks (580–640ms), 2026
- Caller Digital — Top 10 Voice AI Agents India 2026 (TRAI/DPDP)
- HyperVerge / Protean / ksandk / RBI Master Direction FAQs — RBI KYC, CKYCR, Video-KYC, DPDP 2026

---
Draft research note for review. Cited where possible; [UNSOURCED]/[estimate] elsewhere. Not investment advice.
