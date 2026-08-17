# Step A14 — Cross-sell / Up-sell Judgment (when & what to offer without annoying)

**Domain:** India-market, multilingual (Hindi + regional + Hinglish), RBI/IRDAI/DPDP-compliant, action-taking voice+chat contact-center agent for mid-market BPOs.
**Scope of this dossier:** ONLY the judgment step — deciding *whether* this is a moment to offer something, *what* to offer, and *how* to offer it so the customer is helped, not annoyed (and not mis-sold). Excludes: the actual pitch script delivery (separate step), the closing/objection-handling (separate), and the post-sale consent capture mechanics (overlaps but treated downstream).

---

## 0. Why this step is special (first-principles framing)

Cross-sell judgment is the single most **adversarial-to-the-customer** decision a contact-center agent makes. Every other step (answer, resolve, route) is aligned with the customer's goal. This one is the only one where the agent's KPI (revenue) and the customer's immediate goal (get my problem solved) can be in tension. That tension is the whole problem:

- Offer too early → customer feels their problem is being ignored → CSAT crash, churn.
- Offer the wrong thing → "annoying", erodes trust, and in BFSI = **mis-selling = regulatory liability** (RBI mis-selling rules effective phased 2026→Jan 2027 mandate full refund + compensation for mis-sale).
- Offer at the right moment with the right thing → genuinely raises NPS *and* revenue (the "next-best-action done right" case).

So the judgment decomposes into three nested decisions that a skilled human makes almost subconsciously: **WHETHER (moment) → WHAT (product fit) → HOW (framing & restraint)**. The hard part is not the model that predicts propensity — that's commodity. The hard part is the *suppression* logic: knowing when to say nothing.

---

## 1. Human micro-steps (the smallest atomic moves a skilled human agent makes)

A good human agent runs an implicit state machine. Decomposed:

### A. Moment-gating (WHETHER to even consider offering)
1. **Resolution-state check** — Is the customer's *original* problem fully solved? (Humans never pitch on an unresolved complaint. They wait for the "phew, thanks" beat.)
2. **Emotional-valence read** — Is the customer currently positive/neutral, or frustrated/rushed/angry? Read from tone, pace, sighs, word choice ("finally", "ugh", "jaldi karo").
3. **Effort-state read** — Has the call already been long/painful (high customer effort)? If yes, suppress — even a relevant offer lands as "after all this, now you're selling?"
4. **Trust-window detection** — Did a positive micro-moment just happen (problem solved, a fee waived, a thank-you)? That's the open window. Humans pounce on gratitude.
5. **Time/permission read** — Does the customer signal time pressure ("I'm driving", "make it quick")? If yes, suppress or compress.

### B. Product-fit reasoning (WHAT to offer)
6. **Need-inference from context** — Map what just happened to a latent need ("they called about international transaction decline" → forex card / travel insurance is *contextually relevant*, not random).
7. **Eligibility & holding check** — Do they already own this? Are they eligible (age, KYC, income band, existing limit)? Never pitch what they have or can't get.
8. **Suitability judgment** — Is this *good for them*, not just sellable? (The human's conscience filter; now a hard regulatory requirement.)
9. **Propensity intuition** — "Will this person actually say yes?" Built from segment priors + live cues (did they sound budget-conscious? value-seeking?).
10. **One-best-thing selection** — Pick the single most relevant offer, not a menu. Humans know dumping 3 offers = annoyance.

### C. Framing & restraint (HOW to offer)
11. **Permission-pre-frame** — "Aapke liye ek cheez useful ho sakti hai, sun-na chahenge?" (asks micro-consent before pitching — both polite and now compliance-aligned).
12. **Relevance-anchoring** — Tie the offer explicitly to what just happened ("kyunki aapka card abroad block hua tha...").
13. **Restraint / graceful-no** — Read the first hint of disinterest and *drop it instantly* without pushing. The skill is the soft landing, not the close.
14. **Frequency memory** — Remember "I already pitched this person last week / they said no" and not re-pitch (cross-call memory).

The two hardest, most human moves: **#3/#5 (suppression under effort/time pressure)** and **#13 (instant graceful retreat)**. These are where bots feel robotic and pushy.

---

## 2. Agent approach — how a 2026 AI agent does each sub-step

The winning architecture is a **two-layer split**: a fast deterministic *gate* (should I even consider an offer this turn?) feeding a *recommender* (which offer), wrapped by an LLM *framing+restraint* policy. Do NOT let the generative LLM decide "should I sell" freely — it will over-offer. Gate it.

### Layer 1 — Moment gate (real-time, per-turn, <50ms)
- **Resolution-state (A1):** track a `task_resolved` flag from the dialogue-state tracker / intent engine; offer-eligibility = false until resolved. Implement as a turn-level classifier on the conversation state (small fine-tuned encoder, e.g. a DistilBERT/IndicBERT-class model, or a structured flag emitted by the orchestrator).
- **Emotional-valence + effort (A2/A3):** streaming **prosodic + lexical sentiment**. 2026 SOTA: voice-emotion models detecting 8 emotions (anger, annoyance, disapproval, disappointment, worry, happiness, admiration, gratitude) from tone/pitch/pace/pauses fused with transcript sentiment (Gnani, CloudTalk, Balto-class real-time stacks). Output a continuous `frustration_score` and `effort_score`; gate offer if either over threshold.
- **Trust-window (A4):** event detector firing on positive micro-events (resolution + gratitude detected). This is the *enable* signal, ANDed with low-frustration.
- **Time-pressure (A5):** keyword/intent spotting ("jaldi", "quick", "driving", "busy") + speech-rate spike → suppression flag.

The gate is a boolean AND: `offer_allowed = resolved AND not(frustrated) AND not(high_effort) AND not(time_pressed) AND in_trust_window AND not(recently_pitched)`.

### Layer 2 — What-to-offer recommender (the propensity/uplift core)
- **Need-inference (B6):** LLM reads the conversation context + CRM and maps to a *candidate need*, but candidates are then scored by an offline model, not the LLM. Use a **catalog-retrieval** step (the call-reason → eligible-product mapping) so the LLM can't hallucinate products.
- **Eligibility & holding (B7):** hard deterministic rules from CRM/policy admin system — already-holds filter, KYC/age/income band, regulatory eligibility. This is a **business-rules layer**, never the model.
- **Suitability (B8):** rules + a suitability score keyed on age/income/financial-literacy/risk band (RBI now *mandates* this). Encode as a gating predicate AND log the suitability rationale for audit.
- **Propensity / uplift (B9):** the right model is **uplift (causal), not propensity.** Propensity = "will they buy"; uplift = "will *my offering* change their behavior" — it isolates *persuadables* and avoids pitching people who'd buy anyway or who'll be annoyed. Implement as a two-model / class-transformation uplift learner (e.g., uplift random forest, X-learner, or causal-forest) on historical offer→response logs. For exploration/cold-start, wrap in a **contextual bandit (Thompson sampling)** — adapts exploration to uncertainty, outperforms epsilon-greedy, now standard in NBA stacks (BCG 2026; arXiv generator-mediated bandits 2505.16311).
- **One-best-thing (B10):** take argmax of (uplift × margin × suitability), return exactly ONE offer (or none if top score below a confidence floor). Single-offer constraint is a hard policy.

Serving pattern (from arXiv 2505.16918 retail bandit prototype + BCG NBA science): **neural reward model in the batch layer; distill to a light linear/tree model for <50ms real-time scoring.** Keep the served model interpretable (logistic/tree) so you can emit the "why this offer" reason for compliance.

### Layer 3 — Framing & restraint (the LLM policy)
- **Permission pre-frame (C11):** LLM generates a micro-consent ask in the customer's register/language before pitching. Doubles as RBI explicit-consent capture.
- **Relevance-anchor (C12):** prompt-templated to tie offer to the just-resolved event; the LLM has the resolution summary in context.
- **Restraint / graceful-no (C13):** a **dedicated disinterest detector** on the customer's response (lexical + prosodic) → if any negative/hesitation cue → policy forces immediate `drop_offer` and a warm close. Treat this as a hard interrupt, not an LLM "judgment call," so it never pushes.
- **Frequency memory (C14):** cross-call **offer-history store** keyed on customer; `recently_pitched` and `said_no_to_X` suppress re-pitch for a cooldown window.

**Overall pattern:** deterministic gate + uplift/bandit recommender + tightly-constrained LLM for natural-language framing only. The LLM is the *mouth*, not the *decision-maker*.

---

## 3. Tooling (concrete 2026 stack)

- **Real-time voice + emotion:** Gnani.ai (40+ Indian languages, code-switched, BFSI-tuned, real-time sentiment), or Skit.ai (BFSI/insurance journeys) for the India voice layer; Deepgram/AssemblyAI or Sarvam/IndicConformer-class ASR for Hindi/regional STT; CloudTalk/Balto-class real-time sentiment if building bespoke.
- **Dialogue orchestration / state:** LangGraph or a custom state machine for the gate; the orchestrator owns `task_resolved`, frustration, effort flags.
- **Recommender / uplift:** `causalml` (Uber) or `EconML` (Microsoft) for uplift (X-learner, causal forest); `scikit-uplift`. Bandit layer: Vowpal Wabbit (contextual bandits) or a Thompson-sampling service; feature store via Feast.
- **Serving:** batch neural scorer (PyTorch) distilled to logistic/LightGBM for <50ms online inference behind a feature store; Redis for the offer-history/frequency-memory store.
- **LLM for framing:** a Hindi/Hinglish-strong instruction model — Sarvam-M / Krutrim / or GPT-4o-class / Claude for the multilingual framing, heavily constrained by templates + tool outputs (no free product choice).
- **Suitability + consent + audit:** a business-rules engine (Drools-class or a config DSL) for eligibility/suitability; immutable consent + reason-log store (the RBI audit trail) — per-product separate-consent records.
- **Eval:** offline uplift eval (Qini/AUUC), online A/B + interleaving; CSAT/annoyance guardrail metrics; LLM-judge for framing quality (Confident AI / DeepEval-class multi-turn eval).

---

## 4. Benchmarks (real numbers)

- **Real-time sentiment monitoring is now 100%-of-calls, live** — detects frustration/annoyance as a state transition and can trigger/suppress actions before call loss [sourced — sixelevenbpo, CloudTalk, Balto 2026].
- **8 discrete emotions** including *annoyance* and *gratitude* detectable from voice in real time [sourced — CloudTalk/BuildBetter 2026 sentiment tool surveys].
- **Cricut + Zoom AI sentiment:** call-abandonment dropped **90%** via early frustration detection/intervention [sourced — CloudTalk case study 2026]. Up to **30% FCR improvement, 25% fewer escalations** with real-time sentiment [sourced — same].
- **NBA demand:** 28% of CDP buyers rank next-best-action as #1 desired AI capability, 35% among CX pros [sourced — CDP.com / 2026 brand research].
- **Uplift vs propensity:** uplift modeling targets *persuadables* and reduces wasted/annoying contacts vs propensity (which over-contacts sure-things and lost-causes) [sourced — FICO, Stochastic Solutions, Wikipedia uplift].
- **Thompson sampling > epsilon-greedy** for NBA, adapts exploration to uncertainty; bandit-based NBA architectures adopted broadly in last ~2 years [sourced — BCG 2026, arXiv 2505.16311 / 2505.16918].
- **Latency budget for the gate + score:** [estimate] <50ms achievable with distilled linear/tree models behind a feature store (consistent with the batch-neural→light-online distillation pattern in arXiv 2505.16918).
- **Offer-acceptance lift from contextual NBA:** [estimate] mid-market BFSI typically sees 1.5–3x conversion on contextually-triggered vs random/scripted cross-sell; no clean single public source — must be measured on Boss's own data.

---

## 5. Failure modes (where the agent breaks)

1. **Over-offering / pushiness** — without a hard suppression gate, the LLM defaults to "always be helpful = always suggest." Reads as annoying. (Root cause: generative model optimizing helpfulness, not restraint.)
2. **Misreads frustration in code-switched/regional speech** — emotion models trained mostly on English/Hindi may miss sarcasm or regional prosody ("theek hai" said flatly = annoyed, not consent). False "trust window" → pitch into anger.
3. **Suitability blind spot → mis-selling** — model optimizes uplift×margin and pushes a high-margin product to someone unsuitable (low income, low literacy). This is now a *legal* failure (RBI refund+compensation liability), not just CSAT.
4. **Graceful-no failure** — bot doesn't detect soft disinterest ("hmm… dekhte hain") and keeps pitching → the classic robotic-pushy moment.
5. **Frequency-memory gaps** — re-pitches the same product the customer declined last week (no cross-call memory) → trust erosion.
6. **Consent ambiguity** — captures a vague "haan haan theek hai" as explicit per-product consent when RBI requires *specific, informed, unambiguous, separately-recorded* consent → audit failure / dark-pattern violation.
7. **Bundling drift** — agent conditions help on buying (or implies it) → prohibited bundling.
8. **Cold-start mis-exploration** — bandit explores aggressively on real customers early, annoying a fraction to learn. Needs careful exploration caps.

---

## 6. Gap to full adaptation (what the agent still can't do as well as a human — and how to close it)

**The residual human edge is *restraint calibration under ambiguity* — the "read the room and choose to say nothing" instinct.** A human integrates a hundred faint cues (a tired sigh, a kid crying in the background, "ok I have to go now") into a single decision to *not* pitch, even when the propensity model says yes. The agent's gate is rule-based and will either be too trigger-happy or too conservative.

Concretely the agent still lags on:
- **Subtle/ironic disinterest in regional Hinglish** — "haan haan badhiya hai" (flat) = no; models read it as yes.
- **Effort-fatigue empathy** — knowing that *this particular* long painful call means "never pitch, just close warmly," even though resolution + gratitude both fired.
- **Holistic suitability conscience** — a human senses "this person is stretched, don't sell them more credit" beyond what age/income fields show.

**Path to close the gap (engineering + data):**
1. **Restraint-labeled data:** mine human-agent calls and label the *suppression* decisions — moments where a skilled agent *could* have pitched (window was open) but chose not to, and the outcome (CSAT). This is the missing training signal; most data only labels offers made, never offers wisely withheld. Build a **"should-suppress" classifier** from it.
2. **Regional prosody + sarcasm fine-tuning:** fine-tune the emotion/disinterest detector on code-switched Hindi/regional audio with native-speaker labels for *flat-affect agreement* and sarcasm. (Gnani-class multilingual base + Boss's BPO's own call recordings.)
3. **Conservative-by-default bandit:** initialize the policy with a strong prior toward NOT offering; require the recommender to clear a high uplift×suitability floor. Asymmetric cost: penalize a bad offer (annoyance/mis-sell) far more than a missed offer in the reward function.
4. **Counterfactual suitability layer:** an LLM-reasoned "is this genuinely good for them?" check on top of the rules, with its rationale logged — emulating the human conscience filter, auditable.
5. **Outcome-closed loop:** feed post-call CSAT + complaint + cancellation/refund back as the reward, so the system *learns annoyance*, not just acceptance. Annoyance is the label humans optimize against and bots usually ignore.

When (1)+(3)+(5) are in place — i.e., the system has learned *when withholding beats offering* from human-labeled suppression data and an annoyance-penalizing reward — the gap largely closes for routine cases.

---

## 7. HITL trigger (when a human MUST take over)

Not "none." Specific triggers:
- **High-value or complex product** (e.g., ULIP, large insurance, investment-linked) → mandatory human, because suitability judgment + advice carry advisory liability under IRDAI/RBI.
- **Detected frustration spike or vulnerable customer** (elderly, low-literacy signal, distressed) → suppress *and* route to human if persistence needed.
- **Consent ambiguity** — if explicit per-product consent isn't cleanly captured, a human confirms (or the offer is dropped + logged).
- **Customer asks for advice / "what should I do?"** beyond a single contextual nudge → human, because this crosses from offer into advice.
- **Anything the model flags low-confidence on suitability** → don't sell; either drop or escalate.

For *low-stakes, contextually-obvious, clearly-suitable* cross-sells (e.g., "your card was blocked abroad → would you like travel notifications / a forex card?"), fully automatable.

---

## 8. Automation readiness: **5 / 10**

The *mechanics* (sentiment gate, uplift recommender, bandit, framing LLM) are all production-grade in 2026. What holds it at 5 is: (a) the restraint/suppression calibration gap (#6), (b) the new RBI/IRDAI mis-selling regime making the *suitability + explicit-consent + no-dark-pattern* bar legally hard and the cost of error severe, and (c) regional code-switched annoyance detection being unreliable. For *low-stakes contextual nudges with a hard suppression gate and human escalation on complex products*, it's an 8. For *autonomous selling of regulated financial products in Hindi/regional voice*, it's a 3-4 today. Blended: **5**.

---

## 9. Build spec (what to implement, data, gating eval metric)

**Implement:**
1. **Moment-gate service** — per-turn boolean from {task_resolved, frustration_score, effort_score, time_pressure, trust_window, recently_pitched}. Deterministic AND. Owns suppression.
2. **Eligibility + suitability rules engine** — CRM/policy-admin-driven; already-holds filter, KYC/age/income/risk eligibility, RBI suitability predicate. Emits a logged rationale.
3. **Uplift recommender + Thompson-sampling bandit** — scores eligible-suitable catalog; returns ≤1 offer above a high confidence floor or `none`. Asymmetric reward (penalize annoyance/mis-sell heavily).
4. **Framing LLM (constrained)** — permission-pre-frame + relevance-anchor in customer's language; template-bounded, no free product choice.
5. **Disinterest interrupt** — lexical+prosodic; hard `drop_offer` on any negative/hesitation cue.
6. **Offer-history / frequency store** + **immutable consent+reason audit log** (per-product separate consent, RBI-compliant).

**Data needed:**
- Historical call logs with offers made + responses + post-call CSAT/complaint/cancellation (for uplift + annoyance reward).
- **Suppression-labeled set** (open-window-but-withheld moments + outcomes) — the differentiator; will need human labeling.
- Code-switched Hindi/regional audio labeled for frustration/flat-affect/sarcasm + disinterest.
- Product catalog + eligibility/suitability rule tables.

**Gating eval metric (ship gate):**
- **Primary:** *No CSAT regression vs human/no-offer baseline* AND positive *uplift Qini/AUUC* on held-out offers. Specifically: offer arm must show CSAT ≥ control (non-inferiority, e.g. within −1 pt) **and** complaint/mis-sell rate ≤ control.
- **Annoyance guardrail:** measured frustration-rise-after-offer rate below a hard threshold (e.g. <X% of offered turns trigger a frustration spike) — fail = no ship.
- **Restraint precision:** on the suppression-labeled set, the gate must *withhold* on ≥ the human-agent withhold rate (don't over-offer relative to humans).
- **Consent integrity:** 100% of "yes" outcomes have a clean, separate, recorded per-product consent + logged suitability rationale (RBI). Any gap = no ship.

Ship only when all four pass on held-out + a shadow-mode (recommend-but-don't-speak) live trial.

---

## 10. India specifics (Hinglish / regional / regulatory)

- **RBI mis-selling framework (draft Feb 2026, phased effective Jul 2026 → full Jan 1 2027):** mandatory **suitability assessment** (age, income, financial literacy, risk tolerance); **explicit, separately-recorded consent per product** (no single-click bundle approval); **prohibition of compulsory bundling** (can't condition own product on third-party purchase); **ban on dark patterns** (no pre-ticked consent, no confusing opt-outs, no exit-trap pop-ups); **mis-sale = full refund + compensation.** Sector overlays from IRDAI (insurance suitability), SEBI, PFRDA. The "insurance cross-sell machine" via banks is being structurally constrained [sourced — indiafintech.substack, whalesbook, multibagg 2026].
- **DPDP Act:** offer-targeting uses personal data → needs lawful basis + purpose limitation; consent for using interaction data to personalize offers must be clean. Don't repurpose support-call data for marketing without basis.
- **Hinglish / code-switching is the default register** — the framing LLM must offer in the customer's exact mix; a flat "theek hai" / "haan haan" must NOT be read as consent (consent must be explicit + unambiguous — both a UX and a legal requirement here).
- **Flat-affect agreement & politeness-yes** — Indian customers often say "haan haan" to be polite, not to agree to buy. The disinterest/consent detector must be tuned to this; treat ambiguous yes as *not consent* → reconfirm or drop.
- **Regional prosody** — annoyance/sarcasm cues differ across Tamil/Telugu/Bengali/Marathi/Gujarati/Punjabi; emotion model needs per-language tuning (Gnani-class multilingual base + local labels).
- **Trust deficit from spam-call fatigue** — Indian consumers are heavily over-pitched (TRAI spam regime); the bar for "not annoying" is *higher* than Western markets, which pushes the design toward conservative/suppress-by-default.

---

*Sources: CDP.com (NBA), Teneo/Genesys NBA 2026; sixelevenbpo / CloudTalk / Balto / BuildBetter real-time sentiment 2026; FICO / Stochastic Solutions / Wikipedia uplift; BCG 2026 NBA science; arXiv 2505.16311 (generator-mediated bandits), 2505.16918 (contextual-bandit retail prototype); Gnani.ai / Skit.ai / reachall voice-AI India 2026; indiafintech.substack / whalesbook / multibagg (RBI mis-selling 2026).*

*Draft research dossier for review. Cited where possible; [estimate] elsewhere. Not investment advice.*
