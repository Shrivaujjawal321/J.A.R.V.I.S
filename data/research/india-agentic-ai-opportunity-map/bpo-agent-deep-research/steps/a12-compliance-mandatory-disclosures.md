# Step A12 — Compliance & Mandatory Disclosures (RBI / IRDAI / DPDP scripts, consent capture)

> Deep-research dossier for an India-market, multilingual (Hindi + regional + Hinglish), RBI/IRDAI/DPDP-compliant, action-taking voice + chat contact-center agent for mid-market BPOs.
> Scope: **ONLY** the compliance-disclosure-and-consent-capture micro-step. Standalone — an engineer can build from this.
> Date: 2026-06-24. Status: Draft research note. Cited where possible; [estimate]/[UNSOURCED] elsewhere. Not legal advice.

---

## 0. Why this step is special

Most contact-center steps are *quality* problems (was the answer good?). This step is a *liability* problem. A wrong disclosure or a missing consent artifact is not a bad CSAT — it is a regulatory breach with statutory penalties:

- **DPDP**: penalties up to **₹250 crore per breach instance** under the penalty framework, with repeat violations treated more severely (Source: ConversAI Labs / Haptik, 2026). DPDP Rules 2025 notified **14 Nov 2025**; hard compliance deadline **13 May 2027** (Source: Glocert International / EY India, 2026).
- **RBI Digital Lending Directions, 2025**: issued 8 May 2025, effective **1 Jan 2026**. KFS (Key Fact Statement) must be shown **upfront at offer stage** in the **borrower's preferred language**, not just at disbursal (Source: Leegality / Springverify, 2026).
- **IRDAI**: **30-day free-look** for individual life & health from 1 Apr 2024; mandatory disclosure + suitability ("needs analysis") to prevent mis-selling; **2.57 lakh grievances** on Bima Bharosa in FY25 (Source: IRDAI / Insurance Business Mag, 2026).
- **IT Amendment Rules 2026 (MeitY)**: notified **10 Feb 2026**, effective **20 Feb 2026** — **audio SGI (synthetically-generated information, i.e. cloned/synthetic AI voice) must carry an audio disclosure** (Source: Freshfields / Mondaq, 2026). This makes "you are speaking with an AI" a *legal* requirement for synthetic-voice agents, not just an ethics nicety.

So this step is the one where **deterministic correctness beats fluency**. The design principle for the whole step: *the LLM may decide WHEN to disclose and HOW to phrase the wrapper, but WHAT is disclosed and the EXACT mandatory clauses must be template-locked and machine-verified.*

---

## 1. Human micro-steps (the atomic decomposition)

What a skilled compliance-aware human agent actually does, broken to the smallest cognitive / emotional / mechanical moves:

1. **Identify the regulatory regime in play** — is this a lending call (RBI), an insurance call (IRDAI), a generic data-collection call (DPDP only), or a debt-recovery call (RBI FPC + recovery-agent rules)? Each triggers a different mandatory script set.
2. **Sequence the disclosures correctly** — recording-disclosure and identity/AI-disclosure must come *before* any PII is collected or any product is pitched; KFS before contract; free-look mention before close. Order is itself a compliance requirement.
3. **Deliver the opening disclosure verbatim-enough** — "This call is being recorded for quality & training," company identity, agent/representative identity, and (for synthetic voice) "you're speaking with an automated assistant."
4. **Detect and adapt language** — recognise the customer prefers Hindi/Tamil/Hinglish and switch the mandatory script to the **statutorily-required preferred language** (RBI KFS explicitly requires preferred language).
5. **Capture affirmative consent** — ask the explicit yes/no consent question, *wait* for an unambiguous affirmative ("haan", "yes", "theek hai"), and not proceed on silence or ambiguity.
6. **Distinguish consent scope** — consent to *record* vs consent to *process data for purpose X* vs consent to *cross-sell/marketing* are separate; a skilled agent does not bundle them.
7. **Read the mandatory product disclosures at the right trigger** — KFS line items (APR, all-in charges, cooling-off/look-up period, recovery rights) at offer; insurance suitability + free-look + exclusions before close.
8. **Plain-language translate jargon on the fly** — convert "APR", "lien", "free-look", "nominee" into language the customer understands without changing the legal meaning (mis-statement = mis-selling).
9. **Handle consent refusal / partial consent gracefully** — if customer says "don't record," the human knows the call must end or switch to a no-record/no-AI path; emotional de-escalation without coercion.
10. **Detect vulnerability / non-comprehension** — sense confusion, elderly customer, or pressure, and slow down, re-explain, or flag for human (mis-selling risk is highest here).
11. **Log the consent event mentally / in CRM** — note that consent was given, when, in what language, against which disclosure version, for the after-call wrap.
12. **Resist customer attempts to skip** — when customer says "haan haan chhodo ye sab, bas loan approve karo," the agent still completes mandatory disclosures (can't be talked out of compliance).
13. **Answer compliance follow-ups truthfully** — "is it really 30 days free-look?" / "kya mera data share hoga?" without over-promising or fabricating.
14. **Produce the audit-ready record** — ensure the recording + consent flag + disclosure-read confirmation are captured so an auditor can reconstruct the interaction.

---

## 2. Agent approach — how a 2026 AI agent does each sub-step

Core architecture pattern: **deterministic compliance state-machine wrapped around the LLM** ("policy-as-code over a constrained dialog graph"), not a free-form LLM that "tries to remember" the script. The LLM is the *natural-language surface*; a separate **compliance orchestrator** owns the *obligations*.

| Human sub-step | Agent technique (2026) |
|---|---|
| 1. Identify regime | Route at call-setup from campaign metadata (dialer passes `campaign_type=lending|insurance|recovery|generic`). Regime → loads the correct **obligation manifest** (YAML/JSON policy file). No LLM guessing. |
| 2. Sequence disclosures | **Dialog state-machine / flow engine** (Pipecat Flows, LiveKit Agents state, or a LangGraph state graph) with hard gates: cannot enter `collect_pii` node until `recording_disclosed=true AND ai_disclosed=true`. |
| 3. Deliver opening disclosure | **Template-locked TTS** of the verbatim clause (not LLM-generated). Pre-rendered audio or constrained TTS so wording never drifts. AI-disclosure clause is mandatory per IT Rules 2026 for synthetic voice. |
| 4. Detect & adapt language | Language ID on first 2-3 utterances (Sarvam/Krutrim/Whisper-large-v3 lang-id) → swap to the **pre-translated, legally-reviewed** mandatory script for that language. Translations are *fixed assets*, never live-translated by the LLM. |
| 5. Capture affirmative consent | **Constrained NLU intent classifier** for {affirm, deny, unclear} on the consent turn, NOT open generation. Threshold + on "unclear" → re-ask once → on second unclear → deny path. Consent event written to immutable ledger. |
| 6. Distinguish consent scope | Separate consent nodes per purpose, each with its own ledger entry (purpose-bound consent per DPDP §6). Marketing/cross-sell consent is a distinct, skippable node. |
| 7. Mandatory product disclosures | **RAG-free, deterministic retrieval** of the customer-specific KFS values from the loan/policy system of record, slotted into a fixed template. LLM only reads slots; it never invents numbers. |
| 8. Plain-language jargon | LLM *may* paraphrase, but each paraphrase passes a **fidelity guardrail** (entailment check vs the canonical clause) before it's spoken. NeMo Guardrails / Guardrails AI output rail. |
| 9. Handle refusal | State-machine `consent_denied` branch → graceful close script → call ends or transfers. No coercion logic permitted (guardrail blocks pressure language). |
| 10. Detect vulnerability | Acoustic + lexical signals (confusion markers, repeated "samajh nahi aaya", long pauses, age cues) → **HITL escalation trigger**. This is the hardest sub-step (see §6). |
| 11. Log consent event | Auto: every node transition emits a structured event {ts, purpose, language, notice_version, utterance_hash} to the **consent ledger / CMP**. |
| 12. Resist skip attempts | State-machine simply cannot skip mandatory nodes; LLM persona politely insists ("ye ek-do line zaroori hai, fir aage badhte hain"). |
| 13. Compliance follow-ups | Answered from a **closed compliance KB** (curated, legally-reviewed FAQ) via constrained RAG with citations; if not in KB → "let me get you the exact terms" → HITL, never improvise. |
| 14. Audit record | Recording + transcript + consent ledger + disclosure-read flags bundled into a **proof bundle** (SHA-256 hashed, WORM-stored). |

**Headline pattern names to use in the build:** policy-as-code compliance manifest · constrained dialog graph with hard gates · template-locked disclosure TTS · entailment-based fidelity guardrail · purpose-bound consent ledger · proof-bundle generation.

---

## 3. Tooling — concrete 2026 stack

**Voice transport / orchestration**
- **Pipecat** (open-source, Daily) or **LiveKit Agents** for the real-time pipeline + barge-in/turn-taking. LiveKit ~750-900ms, Pipecat ~800-950ms e2e on a standard stack (Source: Trillet/Hamming benchmarks, 2026).
- **Pipecat Flows** or **LangGraph** for the deterministic compliance state-machine.

**STT (Indian-language + Hinglish)**
- **Sarvam AI** ASR (strong on Indic + code-switch) / **Krutrim** / **Deepgram Nova-3 / Flux** (Flux = model-integrated end-of-turn detection, sub-300ms, built for voice agents — good for English/Hinglish; Nova-3 5.26% WER clean) (Source: Evalgent/Deepgram, 2026). Homegrown Indic models hit **11-14% WER** on noisy Hindi-English telephony vs 14-16% for global models (Source: Gnani.ai, 2026).

**LLM (dialog surface)**
- A mid-tier fast model (GPT-4o-class / Claude Haiku-class / Sarvam-M / Llama-3.x Indic-tuned) — the LLM does NOT own compliance content, so a smaller model + strong guardrails is correct and cheaper.

**TTS (multilingual)**
- Sarvam TTS / ElevenLabs multilingual / Indic TTS. **Mandatory clauses → pre-rendered or template-locked audio** for zero drift.

**Guardrails / policy enforcement**
- **NVIDIA NeMo Guardrails v0.20** (Jan 2026; GPU-accelerated, sub-50ms overhead, 40% lower vs 2025) for topic control + dialog rails (Source: AppSecSanta/NVIDIA, 2026).
- **Guardrails AI** for structured-output validation + fidelity checks (claims up to 20× accuracy improvement vs raw output) (Source: NVIDIA blog, 2026).
- Custom **entailment guardrail**: small NLI model (DeBERTa-v3-NLI class) to verify a paraphrase still entails the canonical clause.

**Consent / audit layer**
- **DPDP Consent Management Platform** — Digio, Consently, Consent Server, SecureDApp-class. Features needed: append-only immutable consent ledger, SHA-256 tamper-detection, purpose/version/language fields, proof-bundle on demand, **WORM** retention (Source: Digio/SecureDApp/Consently, 2026).
- **WORM object storage** (S3 Object Lock / equivalent, on-prem or private cloud for BFSI) for recordings + proof bundles.
- **CMP integration** for consent-withdrawal + data-principal rights link (DPDP Rules 2025 requires an easy withdrawal/rights path).

**KFS / disclosure data source**
- Direct API to the lender's LOS/LMS or insurer's policy admin system for the **customer-specific** numbers (APR, charges, free-look) — deterministic slot-fill, never LLM-generated.

**Observability / eval**
- Hamming AI / Evalgent / Coval-class voice-agent eval harness for adherence scoring + regression on the disclosure flow.

---

## 4. Benchmarks (real numbers, tagged)

| Metric | Number | Tag |
|---|---|---|
| E2E voice latency, LiveKit standard stack | 750-900ms | [sourced — Trillet/Hamming 2026] |
| E2E voice latency, Pipecat/Daily | 800-950ms | [sourced — Trillet 2026] |
| Production target p95 / p50 | <800ms / <400ms | [sourced — Trillet 2026] |
| Deepgram Nova-3 WER (clean) / latency | 5.26% / sub-300ms | [sourced — Deepgram/Evalgent 2026] |
| Hindi ASR best WER (10-model eval) | 16.2% | [sourced — arXiv 2602.03868] |
| Indic models, noisy Hindi-English telephony | 11-14% WER | [sourced — Gnani.ai 2026] |
| WER relative increase on code-switched speech | +30-50% | [sourced — arXiv code-switch SLR] |
| NeMo Guardrails overhead | sub-50ms | [sourced — NVIDIA 2026] |
| Guardrails AI accuracy uplift vs raw | up to 20× | [sourced — NVIDIA 2026] |
| Mandatory-clause read fidelity (template-locked) | ~100% (deterministic) | [estimate — by construction] |
| Consent intent-classification accuracy (affirm/deny/unclear) | 95-98% | [estimate — narrow 3-class telephony NLU] |
| Disclosure-flow adherence (well-built state-machine) | >99% sequence-correct | [estimate] |
| Vulnerability/confusion detection recall | 60-75% | [estimate — weakest sub-step] |
| DPDP max penalty per breach | ₹250 cr | [sourced — Haptik/ConversAI 2026] |

---

## 5. Failure modes (where the agent breaks)

1. **Silent skip on ASR miss** — if STT mishears the consent turn, a naive system proceeds without true affirmative consent. Mitigation: confidence-gated re-ask; treat low-confidence as "unclear," never as "yes."
2. **Language-switch mid-clause** — customer switches to Bhojpuri/Marathi mid-call and the agent has no legally-reviewed script for that language → falls back to English (non-compliant for KFS preferred-language). Coverage gap.
3. **Paraphrase drift** — LLM "simplifies" a clause and changes legal meaning (drops "subject to", softens charges) = mis-selling. Why it breaks: fluency objective conflicts with fidelity. Mitigation: entailment guardrail + template-lock the load-bearing clauses entirely.
4. **Bundled consent** — engineer collapses record-consent + marketing-consent into one question to save time → invalid under DPDP purpose-binding.
5. **Barge-in eats the disclosure** — customer talks over the mandatory clause; agent yields and never finishes reading it → no proof it was delivered. Mitigation: mark mandatory clauses as **non-interruptible-must-complete** (or re-deliver), and log a "disclosure-completed" flag only when fully spoken.
6. **Slot hallucination** — LLM invents an APR/charge when the LOS API is slow/empty. Mitigation: hard-fail (don't speak the disclosure) rather than fill a guessed number.
7. **AI-disclosure omission** — synthetic-voice agent fails the IT Rules 2026 audio-disclosure requirement. Mitigation: AI-disclosure is the first hard gate, blocking all downstream nodes.
8. **Vulnerability blindness** — agent fails to detect an elderly/confused customer being effectively mis-sold; proceeds smoothly = the most dangerous failure (passes every metric, fails the human's duty of care).
9. **Audit-bundle gaps** — recording captured but consent-event metadata (language/version) not linked → not "legal-grade" proof. Mitigation: single transaction emits recording-ref + consent-event atomically.
10. **Coercion regression** — a persuasion/upsell prompt leaks pressure language into the consent ask, voiding "free" consent. Mitigation: separate, audited consent persona with pressure-language output rail.

---

## 6. Gap to full adaptation (what the agent still can't do as well as a human — and how to close it)

**The residual human edge is sub-step 10 (vulnerability + non-comprehension sensing) and sub-step 8/13 (real-time fidelity-preserving plain-language + truthful nuance).**

A skilled human agent *feels* when a customer is confused, intimidated, elderly, or just saying "haan" to make the call end — and slows down, re-explains differently, or refuses to proceed. This is duty-of-care, the thing IRDAI's anti-mis-selling regime actually cares about. The agent today detects confusion at maybe **60-75% recall [estimate]** and cannot truly judge *comprehension* (the customer said "yes" — did they understand?).

**Concrete path to close the gap:**
1. **Comprehension-check turns** — don't just disclose; add a teach-back micro-step ("toh aapko samajh aaya cooling-off period kitne din ka hai?") and classify the answer. Engineering: add a verification node + a small comprehension-classifier. Data: labeled teach-back responses.
2. **Vulnerability model** — multimodal classifier on acoustic (pace, pauses, tremor), lexical (repeated confusion markers, "beta/bhai na" register), and metadata (age band, prior complaints) → escalation score. Data needed: **a few thousand labeled India-telephony calls** annotated for vulnerability/mis-selling-risk by compliance reviewers. This is the single highest-value dataset to build for this step.
3. **Regional-language disclosure coverage** — expand the legally-reviewed, fixed-asset script set beyond Hindi/English to the top 8-10 regional languages so language-switch never forces a non-compliant fallback. Data: lawyer-reviewed translations per regime per language (a content/legal task, not ML).
4. **Fidelity guarantee via lock-not-paraphrase** — for load-bearing clauses, *stop trying to paraphrase*; speak the fixed legal-reviewed plain-language version per language. The "adaptation" is choosing the right pre-approved version, not generating one. This converts a fuzzy ML problem into a retrieval problem and closes the mis-statement gap structurally.
5. **Closed compliance KB with abstain** — every compliance follow-up answered from a curated KB with a hard **"I don't have that exact term, transferring you"** abstain, so truthfulness never depends on LLM recall.

With (1)-(5), the agent matches the human on everything except genuine empathic judgment of a borderline-vulnerable customer — which is exactly where the HITL trigger lives.

---

## 7. HITL trigger (when a human MUST take over)

A human MUST take over when **any** of these fire:
- **Vulnerability/confusion score above threshold** (elderly + confusion markers, repeated non-comprehension after one re-explain, distress).
- **Consent refusal on recording/AI** when the campaign legally cannot proceed without it (graceful close, but escalate if customer is upset/complaining).
- **Compliance follow-up outside the closed KB** (customer asks a specific legal/terms question the curated KB can't answer) → transfer, never improvise.
- **Slot-data unavailable** (LOS/policy API fails to return the customer's KFS numbers) → cannot legally disclose → human or callback.
- **Customer alleges mis-selling / invokes a regulator** ("main IRDAI/RBI complaint karunga") → immediate human + flag.
- **Any ambiguity in affirmative consent after one re-ask** → human verification rather than assume.

**Not "none."** This step is *highly* automatable for the mechanical disclosure+consent core, but the vulnerability/duty-of-care edge keeps a mandatory HITL lane. Target: **HITL on <10-15% of calls** once the vulnerability model is in place [estimate].

---

## 8. Automation readiness: **7/10**

Reasoning: The mechanical core — sequencing disclosures, reading template-locked mandatory clauses, capturing purpose-bound affirmative consent, and producing the audit proof-bundle — is **fully automatable today with high confidence** (deterministic state-machine + template-lock + consent ledger gives ~100% clause fidelity and >99% sequence adherence by construction). That alone would be 8-9.

It is pulled down to **7** by three real residuals: (a) **vulnerability/comprehension sensing** (60-75% recall) where mis-selling liability concentrates and IRDAI scrutiny is highest; (b) **regional-language legal-script coverage** gaps that force non-compliant English fallback today; (c) the **regulatory novelty risk** — DPDP enforcement (deadline May 2027) and IT Rules 2026 AI-disclosure are new enough that auditor expectations aren't fully settled, so conservative BFSI buyers will want HITL on edge cases regardless of technical capability. Close (a)+(b) and this becomes a confident 8.5.

---

## 9. Build spec (what to implement, data, gating eval metric)

**Implement**
1. **Obligation manifest loader** — per-regime YAML (`lending.yaml`, `insurance.yaml`, `recovery.yaml`, `generic.yaml`) listing ordered mandatory nodes, their trigger conditions, and per-language fixed clause IDs.
2. **Compliance state-machine** (Pipecat Flows / LangGraph) with **hard gates**: `recording_disclosed`, `ai_disclosed`, `consent_captured(purpose)`, `kfs_delivered`, `freelook_disclosed` — downstream nodes blocked until predecessors true.
3. **Template-locked disclosure TTS** — pre-rendered/constrained audio per clause × per language; mandatory clauses flagged **non-interruptible-must-complete**.
4. **Constrained consent NLU** — 3-class (affirm/deny/unclear) telephony intent model, confidence-gated re-ask once, immutable consent-event emission.
5. **Entailment fidelity guardrail** — NLI check on any LLM paraphrase of a clause; fail → fall back to fixed plain-language version.
6. **KFS/slot fetcher** — deterministic API to LOS/policy admin; hard-fail (don't speak) on missing data.
7. **Consent ledger + proof-bundle** — append-only, SHA-256-hashed, WORM-stored {ts, purpose, language, notice_version, utterance_hash, recording_ref}; withdrawal/rights link wired.
8. **Vulnerability/escalation classifier** + HITL transfer hook.
9. **Closed compliance KB** with hard abstain → transfer.

**Data needed**
- Lawyer-reviewed mandatory scripts per regime × per language (Hindi/English first, then 8-10 regional) — fixed assets.
- Customer-specific KFS/policy data via API (no synthetic numbers ever).
- **3-5k labeled India-telephony calls** for the vulnerability/mis-selling-risk model + the consent-NLU model (affirm/deny/unclear, code-switched).
- Notice/disclosure version registry.

**Gating eval metrics (ship only if all pass)**
- **Disclosure-sequence adherence ≥ 99.5%** on a held-out call set (correct mandatory nodes, in order, fully delivered).
- **Mandatory-clause fidelity = 100%** (zero altered load-bearing clauses — by construction; verified by transcript diff vs canonical).
- **Consent-capture correctness ≥ 99%** (no proceed-without-affirmative; no bundled-consent; every event in ledger).
- **Proof-bundle completeness = 100%** (every call has recording-ref + consent metadata + version, hash-verified).
- **AI-disclosure present = 100%** for synthetic-voice calls (IT Rules 2026).
- **Vulnerability-detection recall ≥ 80%** at acceptable precision before unsupervised mode; below that → HITL-heavy mode.
- **Latency p95 < 900ms** so disclosures don't feel like a robocall and trigger drop-off.

---

## 10. India specifics (Hinglish / regional / regulatory)

- **Preferred-language is a legal obligation, not UX.** RBI KFS must be in the **borrower's preferred language**; an English-only fallback on a Hindi/Tamil call is a compliance defect, not just a worse experience (Source: Leegality 2026).
- **Hinglish is the default register and the hardest ASR case** — +30-50% WER on code-switched speech; consent words arrive as "haan", "han ji", "ok theek hai", "kar do", "nahi nahi", "rehne do". The consent NLU must be trained on real Hinglish affirm/deny tokens, not English yes/no.
- **AI-voice disclosure is now statutory** — IT Amendment Rules 2026 (eff. 20 Feb 2026) require audio disclosure for synthetic/cloned voice (Source: Freshfields/Mondaq 2026). A natural-sounding Indic TTS agent legally must announce it's automated.
- **DPDP purpose-binding + withdrawal path** — record vs process vs marketing consent are separate; the notice must carry an easy withdrawal/rights/grievance link (DPDP Rules 2025) — for voice, that means an SMS/WhatsApp follow-up with the link, logged as part of the proof bundle.
- **Insurance mis-selling is a live enforcement area** — 2.57 lakh Bima Bharosa grievances FY25; IRDAI wants suitability/needs-analysis + free-look (now 30 days) + customer information sheet. The agent must deliver free-look + exclusions before close, and the vulnerability lane matters most here.
- **BFSI data-residency / on-prem** — Indian banks demand on-prem/private-cloud, field-level encryption, WORM audit logs, and 22-language support (Source: SecureDApp/Digio 2026). The consent ledger + recordings likely cannot sit in a generic US-region SaaS.
- **Recovery calls** carry their own RBI Fair Practices + recovery-agent identity/notification rules — a distinct obligation manifest, not the same as origination.

---

## Sources
- DPDP Act/Rules 2025: [Glocert International](https://www.glocertinternational.com/resources/guides/dpdp-act-and-rules-overview/) · [EY India](https://www.ey.com/en_in/insights/cybersecurity/decoding-the-digital-personal-data-protection-act-2023) · [Hogan Lovells](https://www.hoganlovells.com/en/publications/india-publishes-consent-management-rules-under-digital-personal-data-protection-act)
- RBI Digital Lending / KFS: [Leegality](https://www.leegality.com/blog/digital-lending-directions-2025) · [Springverify](https://in.springverify.com/blog/digital-lending-guidelines-rbi/) · [The Digital Fifth](https://thedigitalfifth.com/decoding-rbis-digital-lending-guidelines-2025/)
- IRDAI / free-look / mis-selling: [IRDAI](https://irdai.gov.in/guidelines) · [Insurance Business Mag](https://www.insurancebusinessmag.com/asia/news/breaking-news/irdai-sees-misselling-complaints-rise-amid-stable-grievances-561149.aspx) · [Ditto](https://joinditto.in/articles/health-insurance/irdai-health-insurance/)
- Voice AI consent/recording compliance: [ConversAI Labs](https://www.conversailabs.com/blog/voice-ai-compliance-in-india) · [Haptik](https://www.haptik.ai/blog/data-privacy-in-voice-ai) · [Cleartouch](https://www.cleartouch.in/blog/call-center-audio-recording-legal-requirements-in-india/)
- IT Rules 2026 / AI-voice disclosure: [Freshfields](https://www.freshfields.com/en/our-thinking/blogs/technology-quotient/india-targets-deepfakes-and-ai-generated-content-key-changes-under-meitys-2026-102mjwn) · [Mondaq](https://www.mondaq.com/india/new-technology/1760554/it-rules-2026-deepfake-regulation-three-hour-takedowns-and-ai-labelling-obligations)
- Guardrails: [NeMo Guardrails / AppSecSanta](https://appsecsanta.com/nemo-guardrails) · [General Analysis](https://generalanalysis.com/guides/best-ai-guardrails)
- Indic ASR / Hinglish: [arXiv 2602.03868](https://arxiv.org/html/2602.03868v1) · [Gnani.ai](https://www.gnani.ai/resources/blogs/blog-code-switching-speech-recognition-hinglish-asr)
- Consent ledger / WORM: [Digio](https://www.digio.in/blog/dpdp-consent-management-what-every-data-fiduciary-must-know-in-2026/) · [SecureDApp](https://blog.securedapp.io/dpdp-consent-management-platform-india-audit-guide/) · [Consently](https://www.consently.in/blog/best-dpdpa-consent-management-platform-for-fintechs-india-2026)
- Voice latency / barge-in: [Trillet](https://trillet.ai/blogs/voice-ai-latency-benchmarks) · [Hamming AI](https://hamming.ai/resources/voice-agent-interruption-handling-runbook) · [Deepgram/Evalgent](https://www.evalgent.com/blog/deepgram-stt-voice-agent-testing-guide)

---
*Draft research note for review. Cited where possible; [UNSOURCED]/[estimate] elsewhere. Not investment or legal advice.*
