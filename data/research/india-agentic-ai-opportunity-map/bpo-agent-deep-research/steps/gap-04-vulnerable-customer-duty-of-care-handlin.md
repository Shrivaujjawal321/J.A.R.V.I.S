# Gap Step 04 — Vulnerable-Customer & Duty-of-Care Handling (the Regulated Care Pathway)

**Domain:** India-market, multilingual (Hindi + regional + Hinglish) voice + chat contact-center agent for mid-market BPOs, action-taking (servicing, collections, sales, money movement).
**Compliance envelope:** RBI (proposed Trusted-Person safeguard for 70+/PwD on high-value APP payments ≥₹50k, 24-hr cooling-off; Banking Facility for Senior Citizens & Differently-abled 2017; Fair Practices Code + 2026 recovery-agent rules; Charter of Customer Rights; DPDP Act 2023 + Rules 2025 — health/mental-state = sensitive personal data), IRDAI (PFRDA/IRDAI policyholder-protection + needs-based-suitability), MoHFW Tele-MANAS / 14416 (national mental-health + suicide-prevention rail), Rights of Persons with Disabilities Act 2016, Maintenance & Welfare of Parents & Senior Citizens Act, RBI Digital Lending Guidelines (contact-hour + third-party-contact + app-permission limits). Global benchmark frame: **UK FCA Consumer Duty / FG21-1 four drivers of vulnerability**; **ISO 22458:2022 (consumer vulnerability / inclusive service)**.
**Scope of this doc:** ONLY the formal vulnerable-customer pathway — *detect a vulnerability driver → switch to care protocol → apply special-handling rules (slow down, simplify, offer hardship/forbearance, repeat/confirm comprehension) → SUPPRESS sales/up-sell/aggressive collection → route to human/specialist or external helpline → record sensitively under DPDP.* **Distinct from A06 (emotion/sentiment reading) and A07 (empathy/de-escalation):** A06/A07 read *transient affect* and *soothe* a frustrated caller to keep serving them. THIS step recognises a *durable or acute vulnerability state* that legally/ethically changes WHAT the agent is allowed to do — it can mandate *not* selling, *not* collecting, *not* completing the very transaction the customer asked for, and *handing off* even when the caller is calm. Empathy makes the call nicer; duty-of-care changes the permitted action set.
**Last researched:** 2026-06-24.

---

## 0. Why this step is a distinct, regulated micro-step (not "just empathy")

Empathy (A07) is a *manner*. Duty-of-care is a *permission-and-obligation regime*. The same warm, well-handled call can still be a regulatory breach if the agent up-sold a credit product to someone exhibiting suicidal ideation, completed a ₹2-lakh transfer for a confused 80-year-old being coached off-screen, or pressed a recently-bereaved borrower for a missed EMI. Four structural reasons it must be owned separately:

1. **It is an inverted-objective step, like fraud-handling.** A06/A07/A13/A14 all optimise resolution/CSAT/conversion. This step can *forbid* the conversion and *forbid* completing the request — the correct outcome is sometimes "I will NOT sell you this / will NOT process this now / will pause your obligation." Resolution-tuned and conversion-tuned agents get this exactly wrong by default. ([FCA FG21-1 / Consumer Duty PRIN 2A](https://www.eversheds-sutherland.com/en/united-kingdom/insights/fca-guidance-fair-treatment-of-vulnerable-customers))

2. **The vulnerability taxonomy is broader than "distress."** FCA's four drivers — **Health, Life events, Resilience (financial), Capability** — most of which are *invisible to a sentiment model*. A calm-voiced caller with low financial literacy (capability) or quiet over-indebtedness (resilience) is vulnerable; an emotion classifier reads "neutral." 52% of UK adults show ≥1 vulnerability characteristic — vulnerability is the *majority*, not an edge case, and fluctuates over time. ([Redcliffe/FCA 4 drivers](https://redcliffetraining.com/blog/how-does-the-fca-define-a-vulnerable-customer); [FD Capital](https://www.fdcapital.co.uk/vulnerable-customers-fca-guide/))

3. **It has its own external machinery and clocks.** Tele-MANAS **14416** (24×7, 20 languages, ~53 cells) for self-harm/mental-health routing; RBI Trusted-Person + 24-hr cooling-off for elderly high-value payments; hardship/forbearance and cooling-off in collections; Senior-Citizen/PwD priority-service mandates. None of these belong to the empathy step. ([Tele-MANAS](https://telemanas.mohfw.gov.in/); [Medianama RBI Trusted Person](https://www.medianama.com/2026/04/223-safeguard-elderly-rbi-suggests-trusted-person-approval-high-value-digital-payments/))

4. **The data it touches is the most sensitive there is.** Recording that a customer is suicidal, disabled, bereaved, or in debt is **special-category / sensitive personal data** under DPDP — mis-handling it is its own breach. The detection itself creates a compliance liability the empathy step never does.

---

## 1. Human micro-steps (the atomic decomposition)

What a trained, duty-of-care-aware BPO agent ACTUALLY does — smallest cognitive / emotional / mechanical moves:

1. **Driver-scanning while serving** — continuously listen for the *four vulnerability drivers*, not just upset: **Health** ("my husband is on dialysis," slurred/confused speech, "I can't see the SMS"), **Life events** ("my father passed away last week," job loss, divorce), **Resilience/hardship** ("I have no money till next month," "the EMI broke me"), **Capability** (low literacy, can't navigate the app, repeated confusion, "my grandson usually does this").
2. **Acute-risk listening (the red-flag tier)** — catch *self-harm / suicidal ideation* signals ("there's no point anymore," "I won't be around," "I'll end it"), domestic-abuse / coercion cues, and medical-emergency signals — a separate, higher-urgency channel than ordinary distress.
3. **Disclosure-handling reflex** — when a customer *volunteers* a vulnerability ("I have dementia," "I'm blind," "I just lost my job"), respond with the right micro-acknowledgement (validate, don't pry, don't over-react) — the moment that determines whether they trust the firm or feel labelled.
4. **Care-mode switch** — flip internal posture: *slow the pace*, drop jargon, shorten sentences, lower cognitive load, become patient — a deliberate gear-change distinct from "be nicer."
5. **Comprehension-confirmation loop** — for capability/health vulnerability, *teach-back*: "just so I'm sure I explained it well, can you tell me what you understood?" — verify the customer actually understood, not just heard.
6. **Sales / up-sell SUPPRESSION** — actively *withhold* the cross-sell/up-sell the script would normally trigger; recognise that selling a product to a vulnerable customer right now is a harm, and silently skip the pitch.
7. **Aggressive-collection SUPPRESSION** — for collections, *stand down* the pressure script: no urgency, no penalty-threat, no repeat dunning; recognise genuine hardship vs stalling.
8. **Hardship / forbearance offering** — proactively surface the *care options*: EMI pause / restructure / cooling-off, fee waiver, deadline extension, alternative channel, branch assistance, accessibility accommodation — match the right remedy to the driver.
9. **Capacity / coercion check on transactions** — for elderly/confused callers requesting money movement or product changes, sense whether they truly understand and truly want it (vs being coached/pressured) — and invoke the trusted-person / cooling-off / step-up safeguard rather than just executing.
10. **Accessibility accommodation** — adapt channel and modality: speak slower/louder for hearing, offer to read out / resend, support a *carer/authorised representative* on the line, switch to the customer's comfort language.
11. **Specialist / human routing decision** — decide *this needs a trained human or an external helpline*: a vulnerable-customer specialist desk, a senior agent, a branch, or — for acute self-harm — the **14416 / Tele-MANAS** rail, with a warm bridge not a cold transfer.
12. **Sensitive, minimal recording** — note the vulnerability flag *appropriately*: enough for continuity of care (so the customer isn't re-traumatised next call), minimal/lawful under DPDP, never gossipy, with the right access controls and consent posture.
13. **Hold-firm on protection** — withstand a vulnerable customer's *own* insistence ("just send the money, I know what I'm doing") when protection rules apply — the hardest emotional labour: protecting someone against their stated wish without being paternalistic or disrespectful.
14. **Graceful close + safety-net** — end with the safety information (helpline number, who'll call back, what happens next), confirm the customer is okay to end, and ensure no harm is left on the table.

---

## 2. Agent approach (how a 2026 AI agent does each sub-step)

| # | Human sub-step | 2026 agent technique |
|---|----------------|----------------------|
| 1 | Driver-scanning | **Multi-label vulnerability classifier** over the live transcript mapped to the **FCA four-driver taxonomy** (health / life-event / resilience / capability), NOT a sentiment score. Small fine-tuned multilingual LLM emitting per-turn driver probabilities; runs on the parallel sentinel track (off the 400ms response path). Capability/resilience cues are *lexical/contextual*, so a language model (not a paralinguistic model) is primary here. ([FCA 4 drivers](https://www.helenpettifer.com/resource/vulnerability-drivers-guide/)) |
| 2 | Acute-risk listening | **Dedicated self-harm / crisis classifier** (content-safety model) running as a *high-priority interrupt* on the transcript — AssemblyAI-style content-safety flags / Perspective-class severe-harm detection, multilingual + Indic. Separate, higher-recall, lower-threshold than the general vulnerability scorer. ([AssemblyAI helpline pattern](https://www.balto.ai/blog/top-voice-ai-agent-use-cases/)) |
| 3 | Disclosure-handling | **Disclosure-trigger intent** + a curated, validated **acknowledgement template bank** (validate-don't-pry), so a self-disclosure deterministically routes into care-mode rather than being treated as ordinary content. |
| 4 | Care-mode switch | **Care-mode policy state**: on driver/crisis trigger, the orchestrator switches a system-prompt overlay (slower TTS rate, simpler vocabulary, shorter turns, patience cues) + disables high-pressure playbooks. A *mode flag*, not a tone nudge. |
| 5 | Comprehension loop | **Teach-back prompting**: care-mode injects explicit comprehension-check turns ("aapne jo samjha wo bata dijiye") and a comprehension classifier gates progression. |
| 6 | Sales/up-sell suppression | **Hard policy gate (deterministic):** when `vulnerability_flag` is set, the cross-sell/up-sell tool + pitch playbook are **disabled at the orchestration layer** — not left to model judgment. Mirrors A14 but inverted by the vuln flag. |
| 7 | Collection suppression | **Forbearance gate:** vuln/hardship flag *suppresses* the dunning/urgency playbook and switches to the forbearance-offer playbook; respects RBI recovery-hour + no-third-party-contact + no-harassment rules as deterministic constraints. ([RBI recovery 2026](https://www.amalegalsolutions.com/rbi-new-recovery-guidelines-july-2026)) |
| 8 | Hardship/forbearance offering | **Driver→remedy policy graph:** maps detected driver to the eligible care remedies (EMI pause/restructure, fee waiver, cooling-off, accessible channel, branch). LLM grounds in the policy graph, never improvises eligibility. |
| 9 | Capacity/coercion check | **Step-up + Trusted-Person safeguard:** for elderly/PwD + high-value APP payment, the action gate invokes RBI's trusted-person approval + 24-hr cooling-off; coercion signals (extra-voice diarization, dictation-latency — shared with the fraud sentinel) bias toward hold/step-up. ([Medianama Trusted Person](https://www.medianama.com/2026/04/223-safeguard-elderly-rbi-suggests-trusted-person-approval-high-value-digital-payments/)) |
| 10 | Accessibility accommodation | **Adaptive modality:** TTS rate/volume control, resend/read-out tools, **authorised-representative / carer-on-line** flow, language switch (Indic ASR/TTS) — surfaced automatically by care-mode. |
| 11 | Specialist/helpline routing | **Vulnerability-routing node:** non-acute vuln → vulnerable-customer specialist desk / senior human (warm handoff with packet); **acute self-harm → Tele-MANAS 14416** bridge/referral + human supervisor alert. Cold transfer is a failure mode. ([Tele-MANAS 14416](https://telemanas.mohfw.gov.in/)) |
| 12 | Sensitive recording | **DPDP-aware minimal flag:** vulnerability marker stored as **sensitive personal data** — purpose-bound, access-controlled, minimal free-text, retention-limited, consent/lawful-basis logged. Care-continuity tag readable by future agents on a need-to-know basis. |
| 13 | Hold-firm on protection | **Protection-invariant** in policy: customer insistence does NOT lower the safeguard floor (trusted-person/cooling-off/suppression hold) — analogous to the fraud authority-invariant, enforced by deterministic gates, validated by a "vulnerable-customer-self-override" red-team. |
| 14 | Graceful close + safety-net | **Safety-net close template:** care-mode close always emits the relevant helpline/next-step info + a comprehension/OK-to-end check before disposition. |

**Reference architectural pattern (2026):** run a **parallel "duty-of-care sentinel"** alongside the conversation — the four-driver vulnerability classifier + the acute self-harm classifier + (shared) coercion/diarization — feeding a single **care-gate** that sits between the LLM and the sales/collection/action playbooks. When the gate fires: switch care-mode overlay, **disable sell/dun playbooks**, enable the forbearance + accessibility + routing tools, and set the DPDP-sensitive flag. The LLM never decides "should I stop selling?" — the gate does. ([ISO 22458 inclusive-service design](https://www.bsigroup.com/globalassets/documents/about-bsi/nsb/cpin/s20247_bsi_iso-22458.pdf); [FCA Consumer Duty PRIN 2A](https://reciteme.com/news/financial-conduct-authority-consumer-duty/))

---

## 3. Tooling (concrete 2026 stack)

**Orchestration / care-gate**
- LangGraph / Pipecat FSM with a **care-gate node** between LLM and the sell/collection/action tools; deterministic playbook-disable on `vulnerability_flag` / `crisis_flag`.
- System-prompt **care-mode overlay** (pace, vocabulary, teach-back); driver→remedy **policy graph** (declarative, not model-improvised).
- Guardrails: NeMo Guardrails / Guardrails-AI for output-shape control of acknowledgement + safety-net templates.

**Detection models**
- **Four-driver vulnerability classifier** — multilingual (Hinglish + regional) multi-label LLM/sequence model on FCA-taxonomy-labelled BPO transcripts (health / life-event / resilience / capability).
- **Acute self-harm / crisis content-safety classifier** — high-recall, low-threshold; AssemblyAI content-safety / Perspective-severe-harm class, Indic fine-tuned. Separate interrupt channel.
- **Comprehension classifier** — gates teach-back progression for capability/health cases.
- **Coercion / extra-speaker diarization + dictation-latency** (pyannote-class) — *shared with the fraud sentinel* (gap-02) for the elderly-coercion case.
- **Capability/literacy + accessibility-need detector** — repeated-confusion, request-to-repeat, "my son does this" patterns.

**India care/crisis rails**
- **Tele-MANAS / 14416** (MoHFW, 24×7, 20 languages) — referral/bridge target for self-harm/mental-health. ([Tele-MANAS](https://telemanas.mohfw.gov.in/); [findahelpline](https://findahelpline.com/organizations/tele-manas))
- **RBI Trusted-Person + 24-hr cooling-off** workflow (elderly/PwD high-value APP payments). ([Paypers](https://thepaypers.com/fraud-and-fincrime/news/rbi-proposes-transaction-delays-and-senior-citizen-protections-to-combat-digital-payment-fraud))
- **Forbearance/hardship engine** — EMI pause/restructure, cooling-off, fee-waiver workflows respecting RBI Fair Practices Code + 2026 recovery rules.
- **Accessibility tooling** — adaptive TTS (rate/volume), resend/read-out, carer/authorised-rep flow, Indic language switch (Sarvam / AI4Bharat-grade ASR+TTS).
- Internal **vulnerable-customer specialist desk** routing + warm-handoff packet.

**Governance / standards**
- **ISO 22458:2022** inclusive-service design framework as the build spec for the whole pathway. ([ISO 22458](https://www.iso.org/standard/73261.html))
- **DPDP-aware sensitive-data store** (purpose-bound, access-controlled, retention-limited) for vulnerability flags.

**Eval / red-team**
- Vulnerability-detection eval set (four drivers, Hinglish/regional); self-harm-recall eval (must be near-100% recall); sales-suppression eval (0 up-sells when flagged); customer-self-override red-team; over-flagging/fairness eval.

---

## 4. Benchmarks (real numbers)

- **Vulnerability is the majority, not the edge case:** FCA 2024 Financial Lives Survey — **52% of UK adults** show ≥1 characteristic of vulnerability; it fluctuates over time. India lacks an equivalent national survey but elderly + low-literacy + low-income cohorts make the share plausibly higher. [sourced — [FD Capital / FCA Financial Lives](https://www.fdcapital.co.uk/vulnerable-customers-fca-guide/)]
- **FCA four drivers** are the canonical taxonomy: Health, Life events, Resilience, Capability. [sourced — [Redcliffe / FCA](https://redcliffetraining.com/blog/how-does-the-fca-define-a-vulnerable-customer)]
- **Tele-MANAS scale:** **14416** national number, **24×7, 20 languages, ~53 cells across 36 states/UTs, >1 million calls logged**; routes to state cells, escalates to MH professionals. [sourced — [Tele-MANAS](https://telemanas.mohfw.gov.in/); [DD News](https://ddnews.gov.in/en/transforming-suicide-prevention-into-nationwide-resilience/)]
- **RBI elderly safeguard (proposed 2026):** Trusted-Person approval for **70+ / PwD** on **APP transfers ≥ ₹50,000**; **24-hr cooling-off** to change trusted person / opt-out; excludes merchant/recurring/cheque; consultation feedback by **8-May-2026**. [sourced — [Medianama](https://www.medianama.com/2026/04/223-safeguard-elderly-rbi-suggests-trusted-person-approval-high-value-digital-payments/); [Paypers](https://thepaypers.com/fraud-and-fincrime/news/rbi-proposes-transaction-delays-and-senior-citizen-protections-to-combat-digital-payment-fraud)]
- **RBI recovery rules (2026):** contact only **08:00–19:00**; **no third-party contact** (family/neighbours/colleagues); harassment defined to include **psychological/social pressure**; **cooling-off** encouraged on hospitalisation/family-tragedy; lender fully liable for agent misconduct; agents must pass IIBF exam. [sourced — [Ama Legal July-2026 recovery](https://www.amalegalsolutions.com/rbi-new-recovery-guidelines-july-2026); [Khanna & Associates](https://khannaandassociates.com/blog/loan-recovery-agents-harassing-you/)]
- **AI distress-detection claims:** vendor claims of **~95% accuracy** on mental-health crisis identification and content-safety flags giving "early warning before the agent processes text." Treat as vendor-reported, not independently audited; self-harm needs near-100% *recall* (missing one is catastrophic), so headline accuracy is the wrong metric. [sourced — [Balto use-cases](https://www.balto.ai/blog/top-voice-ai-agent-use-cases/); [NextLevel.AI](https://nextlevel.ai/agent/ai-for-mental-health-support-solution/) — vendor figures]
- **Standard exists:** **ISO 22458:2022** (consumer vulnerability / inclusive service, supersedes BS 18477) — design + delivery requirements for identifying and responding to vulnerability. [sourced — [ISO](https://www.iso.org/standard/73261.html); [BSI](https://www.bsigroup.com/globalassets/documents/about-bsi/nsb/cpin/s20247_bsi_iso-22458.pdf)]
- **Capability/resilience detection accuracy on Indic/Hinglish transcripts:** no public benchmark. [estimate — needs in-house labelled eval set]
- **Human limitation acknowledged:** AI can detect distress in vocal patterns "but cannot replicate the judgment to pause the script, acknowledge the emotion, and adjust." [sourced — [Balto](https://www.balto.ai/blog/top-voice-ai-agent-use-cases/)]

---

## 5. Failure modes

1. **Conversion/resolution bias overrides care (the cardinal failure):** a sales- or collection-tuned agent keeps pitching/dunning *through* a vulnerability signal because its reward is conversion/recovery — exactly the FCA-prohibited harm. Inverse of empathy; the agent must *stop* doing its primary job.
2. **Invisible-driver blindness:** sentiment/emotion models (A06) catch *distress* but miss **capability** (calm low-literacy) and **resilience** (calm over-indebtedness) — the two largest, quietest drivers. Building this on top of an emotion classifier silently misses most vulnerability.
3. **Self-harm miss (catastrophic):** the crisis classifier under-fires on indirect/idiomatic/regional ideation ("ab jeene ka mann nahi," coded phrasing) → no routing to 14416 → worst possible outcome. Demands near-100% recall, accepting false positives.
4. **Self-harm over-fire / mishandling:** robotic or scripted crisis response, or routing a non-crisis as crisis, can re-traumatise or feel cold — and an AI giving *crisis counselling itself* (vs bridging to a trained human) is dangerous.
5. **Coerced-elderly transaction completed:** confused 80-year-old being coached executes a high-value transfer; agent executes because the caller "consented." Needs the trusted-person/cooling-off + coercion sentinel, not consent-at-face-value.
6. **Over-flagging / paternalism / fairness harm:** labelling every elderly or accented or low-literacy caller "vulnerable" → patronising treatment, denial of service ("I can't process this for you"), DPDP-sensitive over-collection, and discrimination exposure (RPwD Act, fair-treatment).
7. **Customer-self-override capitulation:** vulnerable customer insists "just do it" and the (deferential, RLHF-shaped) agent folds the safeguard — same deference pathology as the fraud step.
8. **DPDP mishandling of the flag:** storing "suicidal" / "disabled" / "bankrupt" as free-text without lawful basis, minimisation, access control, or retention limit — the detection *itself* becomes a sensitive-data breach.
9. **Cold transfer / re-traumatisation:** routes to a human but dumps the context, so the vulnerable customer re-explains their bereavement/disability/crisis from scratch.
10. **Latency-forced skip:** under the 400ms turn budget at peak load, the care sentinel is sampled/skipped → vulnerability missed precisely when volume is highest.
11. **Suppression-gate gap across products:** sales suppressed on the up-sell tool but the *embedded* product nudge in the IVR/closing script still fires; or collection suppressed on calls but the automated dunning SMS still sends.
12. **Mode-stuck / mode-thrash:** care-mode latches on and won't release for a now-fine caller (annoying), or flickers turn-to-turn (incoherent). Needs hysteresis.
13. **Multilingual gap:** English-tuned vulnerability + crisis classifiers miss Hinglish/regional expressions of grief, hardship, disability, and suicidal ideation — the highest-stakes language gap in the whole agent.
14. **Accessibility tokenism:** flags PwD but offers no real accommodation (no read-out, no carer flow, no slower pace) → RPwD-Act + ISO-22458 non-compliance dressed as care.

---

## 6. Gap to full adaptation (what the agent STILL can't do as well as a human — and the path to close it)

**Gap A — Detecting quiet, invisible, fluctuating vulnerability.** A skilled human infers capability/resilience vulnerability from dozens of weak cues across the whole call (confusion patterns, "my son handles this," long pauses on numbers, shame-tinged phrasing) — a calm voice that a sentiment model rates neutral. Agents catch loud distress, miss quiet vulnerability.
→ **Path:** a **four-driver multi-label model** (not a sentiment head) trained on FCA-taxonomy-labelled, **confirmed-vulnerability** Indic/Hinglish transcripts, fusing lexical + conversational-pattern + paralinguistic + (where present) coercion signals into a *calibrated per-driver* score; an active-learning loop where human specialists confirm/correct flags and the model learns the long tail.

**Gap B — Acute-crisis human warmth + correct bridge (not AI counselling).** A human senses suicidal ideation, *stays with* the person warmly, and bridges to help. An agent must achieve near-100% *recall* on ideation AND respond with validated, non-robotic care AND **never attempt to counsel** — only bridge to Tele-MANAS/human.
→ **Path:** dedicated high-recall crisis classifier (FP-tolerant) + a **validated crisis-bridge protocol** co-designed with mental-health professionals (Tele-MANAS-aligned) + a hard rule that the agent *refers, never treats* + a supervisor-alert + human-takeover on every positive.

**Gap C — Inverting the objective on demand (stop selling / stop collecting / refuse the request).** Resolution/conversion-optimised agents resist *not completing* the task. Humans flip to "protect over serve" naturally.
→ **Path:** a **care-gate that deterministically disables** the sell/dun/action playbooks (not model goodwill) + a separate **"care-mode policy head"** whose objective is held-floor + correct-remedy + no-harm, explicitly NOT CSAT/conversion — switched on by the gate.

**Gap D — Capacity & coercion judgment on the vulnerable caller's own transaction.** The hardest human skill: deciding a calm, consenting elderly caller shouldn't proceed *right now*. Barely modelled.
→ **Path:** trusted-person/cooling-off safeguard wired to the action gate + the **shared coercion sentinel** (extra-voice/dictation-latency from gap-02), biasing toward step-up/hold on any positive; a **protection-invariant** ("customer insistence never lowers the safeguard floor") validated by a self-override red-team.

**Gap E — Respectful, non-paternalistic, DPDP-clean handling.** Humans support vulnerable customers *without* labelling, infantilising, or over-recording. Agents risk both over-flag harm and sensitive-data breach.
→ **Path:** calibrated thresholds tuned for *low false-flag on protected cohorts*; **minimal, purpose-bound, access-controlled** flag storage with lawful-basis logging; and a "support the need, not the label" response design from ISO 22458.

---

## 7. HITL trigger (when a human MUST take over)

This step is **NOT** a fully closed loop for the acute or high-stakes tiers. A human (vulnerable-customer specialist / senior agent / supervisor — or an external helpline) MUST take over when:

- **Any self-harm / suicidal-ideation / domestic-abuse / medical-emergency signal fires** — immediate warm bridge to **Tele-MANAS 14416** and/or a trained human + supervisor alert. The agent **refers, never counsels**.
- **High-value transaction by a vulnerable/elderly/PwD caller under suspicion of coercion** — human adjudicates the trusted-person / cooling-off / step-up decision.
- **A vulnerable customer pushes the agent to override a protection rule** (complete a risky transfer, take an unsuitable product) — human owns the refusal.
- **Confirmed/strong vulnerability + a consequential decision** (taking on credit, surrendering a policy, large/irreversible action) — needs a human suitability check.
- **Hardship requiring discretionary forbearance** beyond the policy-graph's pre-approved remedies (bespoke restructure, write-off consideration).
- **Detection is ambiguous but the stakes are high** — agent flags "possible vulnerability, uncertain" on a consequential call → route to specialist.
- **Any regulator-defined "must-be-human" vulnerable-customer action** (per internal vulnerable-customer policy / RBI / IRDAI).

**Routine path that stays automatable, no HITL:** detecting a clear vulnerability driver on a *low-stakes* servicing call and applying care-mode (slow down, simplify, teach-back) + **suppressing the up-sell** + offering a *pre-approved* hardship/accessibility remedy + sensitively flagging for continuity — that care-and-suppression behaviour is fully automatable and arguably *more consistent* than humans (an AI never forgets to suppress the pitch, never has a bad day with a confused caller).

---

## 8. Automation readiness: **4 / 10**

The **mechanical care behaviours** are ship-ready and can be *more consistent than human* — deterministic sales/collection suppression on a vuln flag, care-mode pacing/simplification, pre-approved hardship/accessibility remedies, and sensitive-but-minimal flagging (readiness 7–8 for those slices). But the **core human value — reliably catching quiet/invisible/fluctuating vulnerability (capability + resilience), near-100%-recall self-harm detection with warm-but-bounded crisis bridging, capacity/coercion judgment on the vulnerable caller's own transaction, and respectful non-paternalistic handling under DPDP** — still needs HITL and a confirmed-vulnerability continuous-learning loop. The conversion/resolution-bias failure, the catastrophic asymmetry of a missed self-harm signal, the multilingual gap on Indic expressions of distress/hardship, and heavy regulatory + ethical + sensitive-data exposure (RBI elderly safeguard, recovery rules, RPwD Act, DPDP, ISO 22458, FCA-style duty) cap the blended score at **4** — *lower than the fraud step (5)* because the worst-case here (a missed suicidal caller, or selling debt to someone in crisis) is human-harm, not just financial loss, and the detection target (quiet vulnerability) is intrinsically harder than the relatively scripted fraud tells. Most reliable design today: agent runs detection + deterministic suppression + care-mode + pre-approved remedies autonomously, and **hands every acute, high-value, or ambiguous-high-stakes vulnerable case to a trained human or the 14416 rail.**

---

## 9. Build spec

**Implement:**
1. **Parallel duty-of-care sentinel** (off the response path): four-driver vulnerability classifier (health/life-event/resilience/capability) + **separate high-recall self-harm/crisis classifier** + (shared) coercion/diarization → calibrated `vulnerability_flag{driver, confidence}` + `crisis_flag`.
2. **Care-gate node** between LLM and playbooks: on `vulnerability_flag`, **deterministically disable** the up-sell/cross-sell tool AND the dunning/urgency collection playbook; **enable** forbearance + accessibility + routing tools.
3. **Care-mode overlay:** slower TTS, simpler vocabulary, shorter turns, **teach-back** comprehension loop gated by a comprehension classifier.
4. **Driver→remedy policy graph:** declarative map from detected driver to *pre-approved* remedies (EMI pause/restructure, cooling-off, fee-waiver, accessible channel, branch, carer-on-line); LLM grounds in it, never improvises eligibility.
5. **Crisis-bridge protocol** (co-designed with MH professionals): on `crisis_flag` → validated acknowledgement + **warm bridge to Tele-MANAS 14416 / trained human** + supervisor alert; **agent refers, never counsels** (hard rule).
6. **Trusted-Person + cooling-off safeguard** wired to the action gate for 70+/PwD high-value APP payments; coercion sentinel biases toward hold/step-up. **Protection-invariant:** customer insistence never lowers the floor.
7. **Sales/collection suppression coverage** across ALL surfaces (live pitch, IVR nudge, closing script, automated dunning SMS) — not just the live up-sell tool.
8. **DPDP-sensitive flag store:** purpose-bound, minimised, access-controlled, retention-limited vulnerability marker with lawful-basis + consent logging; care-continuity tag on need-to-know basis.
9. **Mode hysteresis:** care-mode latch/release thresholds to avoid stuck/thrashing modes.
10. **Warm specialist handoff** with pre-loaded packet (no re-explaining the bereavement/disability/crisis).

**Data needed:**
- **Four-driver-labelled** Hinglish + regional BPO transcript corpus (health / life-event / resilience / capability), confirmed-vulnerability labels.
- **Self-harm / crisis corpus** in Hinglish + regional, incl. *indirect/idiomatic* ideation — co-labelled with MH professionals; near-100%-recall target.
- **Coercion / extra-speaker / dictation-latency** audio (shared with gap-02 fraud).
- **Accessibility / capability** interaction patterns (repeated confusion, request-to-repeat, "my son does this").
- **Pre-approved remedy catalogue** + RBI/IRDAI hardship/forbearance/recovery-rule constraints encoded.

**Eval metrics that gate "good enough to ship":**
- **Self-harm recall:** **≥ 99%** on the held-out crisis set (FP-tolerant) — a missed ideation is a ship-blocker. AND 100% of positives bridge to human/14416, 0% AI-counselling.
- **Sales/collection suppression:** **0** up-sells / dunning-pressure events when `vulnerability_flag` set, across ALL surfaces.
- **Vulnerability detection:** target recall per driver on the four-driver held-out set, with **calibrated** confidence; **capability + resilience** recall specifically measured (the hard quiet drivers).
- **Over-flag / fairness:** false-vulnerability-flag ≤ target on elderly / accented / low-literacy / PwD cohorts (no paternalism/denial-of-service); RPwD + fair-treatment bar.
- **Protection-invariant:** 100% safeguard-hold on the customer-self-override red-team.
- **Capacity/coercion:** 100% of high-value 70+/PwD transactions under coercion signal invoke trusted-person/cooling-off/step-up.
- **DPDP:** 100% of vulnerability flags stored minimally, purpose-bound, access-controlled, with lawful-basis logged.
- **Audit/continuity:** 100% of vuln cases emit a complete care-handoff packet; 0% cold transfers.

**Ship gate** = ALL of: ≥99% self-harm recall + 100% crisis→human bridge + 0 suppression breaches + protection-invariant 100% + over-flag within fairness bar + DPDP-clean flag storage.

---

## 10. India specifics

- **Tele-MANAS (14416) is THE national self-harm/mental-health rail** — 24×7, **20 languages**, ~53 cells, >1M calls; KIRAN folded into it (2022). Any India BPO agent detecting acute crisis should bridge/refer to 14416, not improvise counselling. This is a concrete, sovereign, multilingual rail an India build can integrate that the West frames differently. ([Tele-MANAS](https://telemanas.mohfw.gov.in/); [Drishti — KIRAN](https://www.drishtiias.com/daily-news-analysis/kiran-mental-health-rehabilitation-helpline))
- **RBI Trusted-Person safeguard for the elderly is India-specific and imminent (2026):** 70+/PwD, APP transfers **≥₹50k**, mandatory trusted-person approval, **24-hr cooling-off**, opt-out allowed; consultation closed **8-May-2026** — design the agent to *invoke* this safeguard, not bypass it. Mirrors but is distinct from FCA's principles-based duty. ([Medianama](https://www.medianama.com/2026/04/223-safeguard-elderly-rbi-suggests-trusted-person-approval-high-value-digital-payments/); [Paypers](https://thepaypers.com/fraud-and-fincrime/news/rbi-proposes-transaction-delays-and-senior-citizen-protections-to-combat-digital-payment-fraud))
- **Collections is the highest-risk vulnerability surface in India:** RBI 2026 recovery rules make harassment of vulnerable borrowers explicitly illegal — **08:00–19:00 only, no third-party contact, no psychological/social pressure, cooling-off on hospitalisation/family-tragedy, lender fully liable**. A collections voice/chat agent MUST hard-code these as deterministic constraints, with hardship-suppression on detection. ([Ama Legal](https://www.amalegalsolutions.com/rbi-new-recovery-guidelines-july-2026); [Khanna & Associates](https://khannaandassociates.com/blog/loan-recovery-agents-harassing-you/))
- **Banking Facility for Senior Citizens & Differently-abled (RBI 2017) + RPwD Act 2016** mandate priority service, accessibility accommodation, doorstep/representative options — the agent's accessibility tooling (read-out, carer-on-line, slower pace, language switch) is a *legal* requirement, not a nicety. ([RBI Senior/Differently-abled](https://www.rbi.org.in/commonman/english/scripts/Notification.aspx?Id=2647); [IBA Bankers' Guide PwD](https://www.unionbankofindia.bank.in/pdf/iba-bankers-guide-for-customers-with-special-needs-and-persons-with-disabilities.pdf))
- **Capability vulnerability is structurally larger in India:** elderly pensioners, daily-wage earners, low-literacy and first-time-digital users who "struggle just to read statements" — RBI itself flags that complexity hits the most vulnerable hardest. The *quiet capability driver* (not loud distress) is the dominant India vulnerability — and exactly what emotion models miss. ([IBPS / RBI guidance](https://ibps.org.in/new-rbi-rules/))
- **Multilingual crisis + vulnerability detection is the hardest, highest-stakes language gap:** Indic + Hinglish expressions of grief, hardship, disability, and suicidal ideation ("ab jeene ka mann nahi," coded/indirect phrasing) break English-tuned content-safety and vulnerability models — needs Indic fine-tuning (Sarvam / AI4Bharat-grade) co-labelled with mental-health professionals, or self-harm recall collapses precisely for the most vulnerable callers.
- **DPDP overlay is acute here:** a vulnerability flag (suicidal / disabled / bereaved / over-indebted) is among the **most sensitive personal data** the agent ever creates — purpose-binding, minimisation, access-control, retention-limits, and lawful basis are mandatory; the *detection itself* is a regulated processing act.
- **No India-codified "Consumer Duty" yet — opportunity + risk:** India has scattered sectoral rules (RBI Charter of Customer Rights, recovery FPC, senior/PwD facility, IRDAI policyholder protection) but no single FCA-Consumer-Duty-style vulnerable-customer regime. A BPO building to **ISO 22458** + FCA's four-driver framing *ahead* of regulation is both a differentiator and future-proofing as India tightens. ([FCA Consumer Duty](https://reciteme.com/news/financial-conduct-authority-consumer-duty/); [ISO 22458](https://www.iso.org/standard/73261.html))

---

### Sources
- FCA / Eversheds-Sutherland, *FCA Guidance — Fair Treatment of Vulnerable Customers (FG21-1)* — https://www.eversheds-sutherland.com/en/united-kingdom/insights/fca-guidance-fair-treatment-of-vulnerable-customers
- Redcliffe Training, *How Does the FCA Define a Vulnerable Customer? (4 Drivers)* — https://redcliffetraining.com/blog/how-does-the-fca-define-a-vulnerable-customer
- Helen Pettifer Training, *FCA Vulnerability Drivers Guide* — https://www.helenpettifer.com/resource/vulnerability-drivers-guide/
- FD Capital, *Vulnerable Customers Under Consumer Duty (incl. Financial Lives 52%)* — https://www.fdcapital.co.uk/vulnerable-customers-fca-guide/
- Recite Me, *FCA Consumer Duty — Accessibility & Vulnerable Customers (PRIN 2A)* — https://reciteme.com/news/financial-conduct-authority-consumer-duty/
- ISO, *ISO 22458:2022 — Consumer Vulnerability / Inclusive Service* — https://www.iso.org/standard/73261.html
- BSI, *BS ISO 22458:2022 Consumer Vulnerability* — https://www.bsigroup.com/globalassets/documents/about-bsi/nsb/cpin/s20247_bsi_iso-22458.pdf
- Tele-MANAS (MoHFW), *National Tele Mental Health Programme — 14416* — https://telemanas.mohfw.gov.in/
- Find A Helpline, *Tele MANAS in India* — https://findahelpline.com/organizations/tele-manas
- DD News, *Transforming Suicide Prevention into Nationwide Resilience (Tele-MANAS)* — https://ddnews.gov.in/en/transforming-suicide-prevention-into-nationwide-resilience/
- Drishti IAS, *Kiran: Mental Health Rehabilitation Helpline (folded into Tele-MANAS)* — https://www.drishtiias.com/daily-news-analysis/kiran-mental-health-rehabilitation-helpline
- Medianama, *RBI Plans Trusted-Person Safeguard for Elderly Payments* — https://www.medianama.com/2026/04/223-safeguard-elderly-rbi-suggests-trusted-person-approval-high-value-digital-payments/
- The Paypers, *RBI Proposes UPI Transaction Delays & Fraud Protections for Elderly* — https://thepaypers.com/fraud-and-fincrime/news/rbi-proposes-transaction-delays-and-senior-citizen-protections-to-combat-digital-payment-fraud
- Ama Legal Solutions, *RBI New Recovery Guidelines July 2026* — https://www.amalegalsolutions.com/rbi-new-recovery-guidelines-july-2026
- Khanna & Associates, *Loan Recovery Agents Harassing You? RBI Guidelines 2026* — https://khannaandassociates.com/blog/loan-recovery-agents-harassing-you/
- RBI, *Banking Facility for Senior Citizens and Differently-abled (2017)* — https://www.rbi.org.in/commonman/english/scripts/Notification.aspx?Id=2647
- IBA / Union Bank, *Bankers' Guide for Customers with Special Needs & PwD* — https://www.unionbankofindia.bank.in/pdf/iba-bankers-guide-for-customers-with-special-needs-and-persons-with-disabilities.pdf
- IBPS, *New RBI Rules 2026 — Zero-Balance / Complexity hits vulnerable hardest* — https://ibps.org.in/new-rbi-rules/
- Balto, *Top Voice AI Agent Use Cases for Contact Centers in 2026 (distress detection limits)* — https://www.balto.ai/blog/top-voice-ai-agent-use-cases/
- NextLevel.AI, *Voice AI for Mental Health Support* — https://nextlevel.ai/agent/ai-for-mental-health-support-solution/
- Gistly, *Call Center Compliance — 2026 Guide (vulnerable-population scrutiny)* — https://www.gistly.ai/blog/call-center-compliance
- Scorebuddy, *8 Call Center Compliance Trends for 2026* — https://www.scorebuddyqa.com/blog/call-center-compliance-trends

*Draft research dossier for review. Cited where possible; [estimate] elsewhere. Not investment/legal/medical advice.*
