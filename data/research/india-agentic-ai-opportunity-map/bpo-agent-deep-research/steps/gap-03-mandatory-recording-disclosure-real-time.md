# Gap Step 03 — Mandatory Recording Disclosure & Real-Time Consent / DPDP Notice at Call Open (the Pre-Conversation Gate)

**Domain:** India-market, multilingual (Hindi + regional + Hinglish) voice + chat contact-center agent for mid-market BPOs, action-taking (servicing, sales, collections, cross-sell).
**Compliance envelope:** DPDP Act 2023 + DPDP Rules 2025 (notified 14-Nov-2025; consent/notice provisions), TRAI TCCCPR-2018 as amended 12-Feb-2025 (DLT, DND/UCC, 140/1600-series, auto-dialer/robocall disclosure, consent-validity caps), MeitY IT Amendment Rules 2026 (synthetic-voice audio SGI disclosure, eff. 20-Feb-2026), RBI/IRDAI sectoral recording-retention rules.
**Scope of this doc:** ONLY the **discrete spoken opening gate** that fires in the FIRST few seconds of a call, *before the substantive conversation begins*: (a) the recording-disclosure announcement, (b) the DPDP "notice + purpose" at point of collection, (c) the AI/synthetic-voice disclosure, and (d) the **DND/consent/DNC pre-flight gate** that decides whether the call/cross-sell is even *permitted* — and what to do if recording consent is refused. **Distinct from A12** (which owns the *full* compliance-disclosure-and-consent-capture lifecycle across the call — KFS, free-look, suitability, in-call regulatory scripts): this step is *only the opening precondition* — the bouncer at the door, not the rules inside the club. **Distinct from A02** (identity/auth): this gate runs *before or alongside* greeting and does not check "who are you?" — it checks "am I even allowed to speak/record/sell to this number, and have I told them I'm recording + an AI?"
**Last researched:** 2026-06-24.

---

## 0. Why this step is a distinct, must-own micro-step (not just "part of A12 disclosures")

A12 treats disclosures as a *process that runs through the call*. But the **call-open gate is a hard precondition with its own clock, its own legal triggers, and its own abort path** — it must complete (or fail-safe) before turn 1 of real conversation, and getting it wrong is not a CSAT problem, it is a *call-shouldn't-have-happened* problem. Four structural reasons it must be owned separately:

1. **It is a GATE, not a SCRIPT.** Most of A12 is "say the right words at the right trigger." This step is "**decide whether to proceed at all**" — DND-scrub the number, check consent validity (TRAI caps consent at 7 days for transactional, and to service-contract end for implicit), check time-window (9am–9pm for promotional), confirm DLT header/template, and only THEN dial / continue. A blocked outcome here means *the conversation never starts*. ([Securiti TCCCPR 2025](https://securiti.ai/india-spam-rules-trai-latest-amendment/); [Caller Digital DND 2026](https://www.caller.digital/blog/trai-dnd-compliance-ai-outbound-calling-india))
2. **The recording disclosure is itself the lawful basis for everything downstream.** If "this call is being recorded" + DPDP purpose notice isn't delivered (and, for explicit-consent recording, *affirmatively accepted*) at the top, then every recording, transcript, QA-score, and training-data use *after* it is built on an unlawful base. The opening seconds are load-bearing for the entire interaction's legality. ([Caller Digital — DPDP vs TRAI consent 2026](https://www.caller.digital/blog/dpdp-vs-trai-consent-voice-recordings-audit-trail-india-2026); [ClearTouch India recording compliance 2026](https://www.cleartouch.in/blog/call-center-audio-recording-legal-requirements-in-india/))
3. **The AI-disclosure is now a fresh statutory line, not etiquette.** Post IT Amendment Rules 2026, a synthetic/cloned-voice agent carries an audio-SGI disclosure duty — "you're speaking with an automated assistant" — that must land at the open. Human agents never had this line; the AI agent *must* speak it. (See A12 §0; [ConversAI Labs voice compliance 2026](https://www.conversailabs.com/blog/voice-ai-compliance-in-india); [Auto Interview AI 2026](https://www.autointerviewai.com/blog/ai-calling-india-dpdp-trai-dlt-compliance-complete-guide-2026))
4. **It has a distinct abort/branch behaviour A12 doesn't.** Refused recording consent → switch to a no-record path or end the call; number on category-DND for your industry → no promotional pitch at all (service-only); revoked consent on file → don't even dial. These are *routing* decisions made at the door, separate from in-call disclosure scripting.

---

## 1. Human micro-steps (the atomic decomposition)

What a skilled, compliance-aware BPO agent (or the dialer + agent together) ACTUALLY does in the first ~10 seconds, broken to the smallest cognitive / mechanical moves:

1. **Pre-dial / pre-pickup permission check (outbound).** Before the call even connects, confirm the number is *callable*: scrubbed against the National DND/DNC registry, the right DLT header/template registered, the campaign category not category-blocked for this subscriber, and the local time inside the 9am–9pm promotional window. (For a human, the dialer/compliance team did this; the agent inherits a "safe-to-talk" flag.)
2. **Consent-on-file lookup.** Check whether *prior, still-valid* consent exists for *this purpose* (and whether it's been withdrawn) — TRAI's 7-day transactional / contract-life implicit caps mean yesterday's consent may already be stale.
3. **Open with the recording disclosure verbatim-enough.** First words after hello: "This call is being recorded for quality and training purposes" — in the customer's language, before any PII is spoken.
4. **Deliver the DPDP notice + purpose at point of collection.** Plain-language, jargon-free statement of *what* data will be processed and *why* (e.g., "to service your loan account / verify your policy"), and that they can withdraw — *before* collecting anything.
5. **Deliver the AI / synthetic-voice disclosure (AI-agent only).** "You're speaking with [Brand]'s automated voice assistant" — at the open, unambiguously.
6. **State company + representative identity.** Brand name and (human) agent/representative ID — the "who is calling and on whose behalf" line bundled into the open.
7. **Ask the affirmative-consent question where recording requires explicit consent.** Not assume; *ask* — "Is that okay to proceed?" — and **wait** for an unambiguous "haan / yes / theek hai." Silence ≠ consent.
8. **Read the customer's response correctly (accept / refuse / ambiguous).** Distinguish a clear yes from "hmm," "kaun bol raha hai?", or a question — and not steamroll an ambiguous answer into a yes.
9. **Branch on refusal — no-record / end-call.** If the customer declines recording, know the call must either continue on a no-record path (if the firm supports it) or be ended politely — *without coercion* ("it's mandatory, so I'll have to record anyway" is the wrong, non-compliant move when explicit consent is required).
10. **Gate the cross-sell separately.** Even with a valid service call, recognise that *promotional/cross-sell* needs its *own* consent and DND-category clearance — and suppress the pitch if the number is promo-blocked or marketing consent is absent. (Bundling service + marketing consent is non-compliant.)
11. **Give the withdrawal route inside the prompt.** Tell the customer *how* to opt out / withdraw — at least as easily as they consented ("you can say 'stop recording' / reply STOP / call 1909") — satisfying DPDP equal-ease-of-withdrawal.
12. **Sequence everything before substantive talk.** Hold the discipline that *all* of the above lands *before* the first real question or pitch — order is itself a legal requirement.
13. **Resist "skip all that" pressure.** When the customer says "haan haan chhodo, kaam batao," still complete the mandatory open (can't be talked out of the gate).
14. **Log the consent artefact precisely.** Capture: consented? / refused? / timestamp / language / *which notice version* the customer heard — for the ledger and for a future complaint six months later.

---

## 2. Agent approach (how a 2026 AI agent does each sub-step)

| # | Human sub-step | 2026 agent technique |
|---|----------------|----------------------|
| 1 | Pre-dial permission check | **Compliance-as-code pre-flight gate** (deterministic, runs *before* the LLM/voice session): real-time **DND/DNC scrub** against the National registry + telco DND, DLT header/template validation, **category-DND** check for the campaign type, and a **time-window guard** (9am–9pm local for promotional). Number fails any check → dialer drops / routes to service-only, never reaches conversation. ([Caller Digital DND 2026](https://www.caller.digital/blog/trai-dnd-compliance-ai-outbound-calling-india)) |
| 2 | Consent-on-file lookup | **Consent-ledger query** keyed by (number, purpose): returns `valid / stale / withdrawn`, honouring TRAI validity caps (7-day transactional; contract-life implicit). Withdrawn → suppress call/pitch. ([Securiti 2025](https://securiti.ai/india-spam-rules-trai-latest-amendment/)) |
| 3 | Recording disclosure | **Template-locked opening utterance** (not LLM-generated) in the detected language, played as the literal first content; machine-verified it was emitted before any PII collection. (Principle from A12: WHAT is disclosed is template-locked; only the wrapper is flexible.) |
| 4 | DPDP notice + purpose | **Versioned notice registry** → the agent plays the *current* plain-language notice for this campaign's purpose; notice version-ID is captured to the ledger. ([DPDP Rules 2025 notice req — EY](https://www.ey.com/en_in/insights/cybersecurity/transforming-data-privacy-digital-personal-data-protection-rules-2025); [Caller Digital consent audit 2026](https://www.caller.digital/blog/dpdp-vs-trai-consent-voice-recordings-audit-trail-india-2026)) |
| 5 | AI / synthetic-voice disclosure | **Deterministic SGI-disclosure node**: mandatory "automated assistant" line at open; cannot be skipped by the LLM; logged. (IT Amendment Rules 2026 audio-SGI duty — see A12.) ([ConversAI Labs 2026](https://www.conversailabs.com/blog/voice-ai-compliance-in-india)) |
| 6 | Company + representative identity | Bundled into the template open (brand + bot/agent ID + on-behalf-of PE). |
| 7 | Affirmative-consent ask | **"Clear affirmative action" capture**: where recording needs explicit consent, an explicit yes/no prompt — voice ("haan/yes") or DTMF ("press 1") — with **silence = no consent** enforced in the dialog FSM. ([Phonexa IVR consent](https://support.phonexa.com/call-routing/ivr-ivr-consent); workmate scripts) |
| 8 | Read accept/refuse/ambiguous | **Intent classifier on the consent turn** (multilingual): `accept / refuse / unclear`; `unclear` → re-prompt once, never auto-proceed. Tuned for Hinglish affirmations + negations. |
| 9 | Branch on refusal | **Consent FSM branch**: refuse → `no_record_path` (if configured) or `graceful_end` with a templated, non-coercive close; recording pipeline halted deterministically (not "agent decides"). |
| 10 | Gate cross-sell separately | **Separate marketing-consent + promo-DND gate**: cross-sell tool/flow is hard-disabled unless `marketing_consent=valid AND not promo-category-DND`. Service and marketing consent never bundled. ([Caller Digital DND 2026](https://www.caller.digital/blog/trai-dnd-compliance-ai-outbound-calling-india)) |
| 11 | Withdrawal route in prompt | **Equal-ease withdrawal line** spoken in the open: "say STOP / reply STOP / call 1909" — surfaced inside the same prompt, satisfying DPDP equal-ease. ([Caller Digital consent audit 2026](https://www.caller.digital/blog/dpdp-vs-trai-consent-voice-recordings-audit-trail-india-2026)) |
| 12 | Sequence before substantive talk | **Orchestration ordering invariant**: the gate node must reach `complete` (or `aborted`) before the intent/dialog graph unlocks; PII-collection tools are gated on `disclosure_done=true`. |
| 13 | Resist "skip" pressure | The gate is **non-skippable by design** — caller utterances are untrusted data; "skip that" cannot bypass a deterministic node (same injection-resistance principle as the fraud layer). |
| 14 | Log the consent artefact | **Immutable, signed consent-ledger write**: `{number, purpose, consent=Y/N, timestamp, language, notice_version, channel, agent_id}` — WORM-stored, queryable for complaints/audit. ([Caller Digital 2026](https://www.caller.digital/blog/dpdp-vs-trai-consent-voice-recordings-audit-trail-india-2026)) |

**Reference architectural pattern (2026):** model this as a **deterministic "door" state-machine that sandwiches the LLM** — a *pre-session* compliance-as-code gate (DND/DLT/category/time/consent-on-file) decides whether to connect at all; then a *session-open* disclosure-FSM plays template-locked recording + DPDP-notice + AI-disclosure lines, captures the affirmative-consent artefact, and only THEN unlocks the conversational graph (and separately unlocks the cross-sell sub-graph only if marketing-consent clears). The LLM never authors the mandatory lines and can never skip the gate. Every gate decision and the consent artefact write to an immutable ledger. This is the **"compliance-as-code + consent ledger"** primitive (already named in the blueprint) instantiated for the *opening* specifically.

---

## 3. Tooling (concrete 2026 stack)

**Pre-flight compliance-as-code**
- **DND/DNC scrubbing service** against National DND + telco registries; **DLT platform** integration (PE/header/template registration, category mapping). (Jio/Airtel/VI DLT, Tanla/Karix/Route Mobile-class CPaaS DLT layers.) ([SMSCountry DLT guide 2026](https://www.smscountry.com/blog/dlt-registration/); [Message Central India 2026](https://www.messagecentral.com/sms-guideline/india))
- **Time-window + category-DND policy engine** (OPA/Cerbos-style policy-as-code) enforcing 9am–9pm promotional window + per-category opt-outs.

**Disclosure + consent capture**
- **Voice orchestration FSM** (Pipecat / LiveKit Agents / LangGraph) with a non-skippable disclosure node + consent branch; DTMF capture for "press 1" affirmative consent.
- **Versioned notice registry** (a config store mapping campaign→purpose→current notice text, per language) + template-locked TTS playback (Sarvam / AI4Bharat IndicTTS / ElevenLabs Indic).
- **Multilingual consent-turn intent classifier** (accept/refuse/unclear) — Indic-tuned (Sarvam-M / AI4Bharat).

**Consent ledger / audit**
- **Immutable consent ledger** — append-only / WORM (e.g., QLDB-style or signed-log) recording `{consent, purpose, ts, lang, notice_version}`; integration toward a **DPDP Consent Manager** (registered intermediary) for cross-fiduciary consent. ([EY DPDP Rules 2025](https://www.ey.com/en_in/insights/cybersecurity/transforming-data-privacy-digital-personal-data-protection-rules-2025); [Seclore DPDP guide](https://www.seclore.com/fundamentals/dpdp-rules-2025-compliance-guide/))
- **Withdrawal channel** wiring (STOP-keyword / 1909 / DTMF opt-out) feeding back into the consent ledger + DND.

**Eval / QA**
- Disclosure-presence + ordering checker over transcripts (deterministic regex/template match per language); consent-artefact completeness auditor.

---

## 4. Benchmarks (real numbers)

- **Promotional calling window:** commercial/telemarketing calls permitted **9am–9pm** only; outside is prohibited for unsolicited commercial communication. [sourced — [Caller Digital DND 2026](https://www.caller.digital/blog/trai-dnd-compliance-ai-outbound-calling-india); [ClearTouch outbound timings 2026](https://www.cleartouch.in/blog/trai-guidelines-for-outbound-calling-timings-in-india/)]
- **Consent validity caps (TCCCPR 2025 amendment, 12-Feb-2025):** transactional-message consent restricted to **7 days**; implicit consent lasts only to **end of service contract**; indefinite consent discouraged. [sourced — [Securiti 2025](https://securiti.ai/india-spam-rules-trai-latest-amendment/); [MEF 2025](https://mobileecosystemforum.com/2025/07/11/in-india-trai-tougher-on-spam-a-call-for-industry-action/)]
- **UCC complaint penalty:** up to **₹25,000 per upheld complaint**, levied on the Principal Entity (PE), not the telemarketer. [sourced — [Caller Digital DND 2026](https://www.caller.digital/blog/trai-dnd-compliance-ai-outbound-calling-india)]
- **DPDP penalty exposure:** up to **₹250 crore per breach instance** (notice/consent failures fall in scope). [sourced — [Auto Interview AI 2026](https://www.autointerviewai.com/blog/ai-calling-india-dpdp-trai-dlt-compliance-complete-guide-2026); see A12]
- **Series mandate:** **140-series** for promotional, **1600-series** for transactional/service calls; auto-dialer/robocall **intent + purpose must be disclosed** to the OAP. [sourced — [Elision 140/160 guide](https://www.elisiontec.com/140-and-160-series-regulations-from-trai-complete-guide-faqs/); [Securiti 2025](https://securiti.ai/india-spam-rules-trai-latest-amendment/)]
- **Recording-disclosure norm:** announce **"this call is being recorded for quality/training"** at start; DPDP pushes BPOs from one-party consent toward **explicit, purpose-specific, documented consent**; sectoral retention **~6 months** (insurance/BPO). [sourced — [ClearTouch recording compliance 2026](https://www.cleartouch.in/blog/call-center-audio-recording-legal-requirements-in-india/); [Alohaa](https://www.alohaa.ai/blog/is-call-recording-legal-in-india-understanding-the-laws-and-practices)]
- **DPDP notice rule:** must be **clear, plain-language, separate (not buried in T&C), at or before point of collection**, itemising data + purpose + withdrawal route. [sourced — [EY DPDP Rules 2025](https://www.ey.com/en_in/insights/cybersecurity/transforming-data-privacy-digital-personal-data-protection-rules-2025); [Scrut DPDP](https://www.scrut.io/post/dpdp-rules)]
- **Affirmative-action / silence rule:** consent needs **"clear affirmative action"** — silence is NOT consent; "press 1" / spoken-yes patterns required; **withdrawal must be at least as easy** as consent. [sourced — [Caller Digital consent audit 2026](https://www.caller.digital/blog/dpdp-vs-trai-consent-voice-recordings-audit-trail-india-2026)]
- **Latency budget for the open:** the gate adds spoken seconds *before* value — disclosure + AI-line + consent ask can consume ~8–15s of opening; over-long opens spike early abandonment. [estimate — needs in-house abandonment A/B]
- **Multilingual consent-turn classifier accuracy on Hinglish/regional accept-vs-refuse:** no public benchmark. [estimate — needs in-house eval set]

---

## 5. Failure modes

1. **Gate skipped under latency pressure / barge-in.** Customer talks over the open ("haan kya hai, jaldi batao") and the agent jumps to business before the recording/DPDP/AI lines land → unlawful recording base. The single most common real-world failure.
2. **Silence-as-consent.** Agent treats no-objection / a "hmm" as a yes where explicit consent is required → consent artefact is legally void.
3. **Stale-consent false-positive.** Calling on a 30-day-old "consent" that TRAI already invalidated (7-day transactional cap) → UCC violation despite a consent record existing.
4. **Category-DND blind spot.** Number isn't on *full* DND but has opted out of your category (e.g., insurance) → a promotional pitch fires anyway → ₹25k/complaint PE penalty. Scrubbing only full-DND misses this.
5. **Service/marketing consent bundling.** One blanket "okay to proceed?" used to justify both servicing AND cross-sell → marketing consent invalid, pitch non-compliant.
6. **AI-disclosure omitted or buried.** Synthetic-voice agent doesn't clearly say "automated assistant" at open (or says it after the pitch) → IT-Rules-2026 SGI-disclosure breach + deception risk.
7. **Coercive refusal handling.** Customer declines recording; agent records anyway / pressures them ("it's compulsory") where explicit consent is required → both a consent and a fairness breach.
8. **Notice-version not logged.** Consent captured but *which* notice text the customer heard isn't recorded → six months later, on complaint, the artefact is unprovable. ([Caller Digital 2026](https://www.caller.digital/blog/dpdp-vs-trai-consent-voice-recordings-audit-trail-india-2026))
9. **Withdrawal route not given / not equal-ease.** Opt-out buried in an IVR tree or omitted from the prompt → DPDP equal-ease-of-withdrawal failure.
10. **Wrong-language disclosure.** Recording/DPDP lines played in English to a Hindi-only customer → "informed" requirement not met; consent not truly informed.
11. **Time-window / series misconfig.** Promotional call dialed at 9:10pm, or on 1600-series instead of 140, or with an unregistered DLT header → straightforward UCC breach before a word is spoken.
12. **Over-disclosure fatigue → abandonment.** A 20-second legalese wall at the open spikes drop-off and tanks containment, pushing teams to *unsafely* trim mandatory lines.
13. **DTMF/voice consent capture mismatch.** "Press 1" prompt but the channel/IVR doesn't reliably capture DTMF, or voice-yes mis-recognised → consent neither captured nor refused, an ambiguous void.
14. **Channel inconsistency (voice vs chat).** Chat path collects a checkbox but the voice path skips the spoken line (or vice-versa) → inconsistent lawful base across channels for the same customer.

---

## 6. Gap to full adaptation (what the agent STILL can't do as well as a human — and the path to close it)

**Gap A — Graceful, non-robotic delivery that survives barge-in.** A skilled human compresses the mandatory open into a warm, fast, natural couple of sentences, handles "haan jaldi batao" without dropping a required line, and re-inserts the missed disclosure mid-flow. Naive agents either robot-read a long wall (abandonment) or skip lines under interruption (breach).
→ **Path:** a **barge-in-aware disclosure FSM** that (a) detects talk-over, (b) holds the conversation lock until mandatory lines are *confirmed-emitted*, (c) can re-deliver a missed line conversationally, and (d) uses tight, TTS-optimised template phrasings tuned for the shortest legally-sufficient open per language; A/B against abandonment.

**Gap B — Judging when explicit consent vs notice-only is required.** Humans (via training) sense whether a given call type needs an *affirmative* recording yes or just a *notice*. The agent must encode this per campaign × purpose × sector correctly — and a wrong default is a breach either way.
→ **Path:** a **policy matrix** (campaign → recording-consent mode: notice-only vs explicit) maintained by compliance, machine-enforced; default to the *stricter* mode on ambiguity; reviewed on regulation change.

**Gap C — Reading an ambiguous or vulnerable consent response.** A human catches "the customer didn't really understand what they agreed to" (elderly, confused, language-mismatch) and re-explains before banking the consent. Agents risk banking a hollow yes.
→ **Path:** a **comprehension/vulnerability signal** on the consent turn (confusion cues, language-mismatch, hesitation) → re-explain-in-simpler-language loop before recording consent as valid; flag for HITL on persistent non-comprehension.

**Gap D — Keeping the gate correct as four regulators move independently.** Humans get a memo; the agent's gate must update when TRAI tightens consent windows, MeitY revises SGI rules, DPDP operationalises Consent Managers, or a sector regulator changes retention.
→ **Path:** **config-driven, versioned compliance rules** (DND windows, consent caps, notice text, AI-line, series mapping) decoupled from code, with a change-review + regression-eval gate so every regulatory update is testable and dated.

**Gap E — Cross-channel consent coherence.** A human serving one customer across call+chat intuitively carries the consent context. The agent must keep one coherent, withdrawable consent state across voice + chat + SMS.
→ **Path:** a **single per-(number,purpose) consent record** in a shared ledger / Consent-Manager-backed store that every channel reads and writes, so withdrawal anywhere propagates everywhere.

---

## 7. HITL trigger (when a human MUST take over)

This step is **mostly a closed deterministic loop** — but a human (compliance / supervisor) MUST take over or be alerted when:

- **Recording consent is refused** AND the firm has no configured no-record path for this call type → graceful end + supervisor log (policy decision on whether to call back differently).
- **Persistent non-comprehension / vulnerability** on the consent turn (elderly, repeated confusion, language the agent can't serve) → warm transfer so a human can obtain *informed* consent.
- **The pre-flight gate hits an ambiguous legal state** — e.g., consent record exists but its validity/scope is unclear, or DND status can't be resolved → fail-safe to *don't proceed* + flag.
- **A regulatory config change is pending review** — new TRAI/MeitY/DPDP rule not yet encoded → compliance owns the update before campaigns resume on the affected path.
- **Repeated gate failures / drift detected** in QA (disclosures missing, consent artefacts incomplete on a campaign) → human audit + halt.

**Routine path that stays fully automatable, no HITL:** the textbook flow — DND/DLT/time/category pre-flight passes, valid consent on file (or freshly, affirmatively captured), template-locked recording + DPDP + AI lines delivered in the right language, artefact logged with notice-version. This is *mechanical and arguably MORE reliable than a human*, who routinely rushes or forgets the open under AHT pressure.

---

## 8. Automation readiness: **8 / 10**

This is one of the **most automatable** steps in the whole map — and the agent is *better than the average human* at the parts that matter most. A deterministic gate **never forgets the recording line under AHT pressure, never silently skips DND scrubbing, never bundles consent by accident, and logs a perfect notice-versioned artefact every time** — exactly the disciplined, boring, repeatable behaviour humans fail at when rushed. The mandatory open is template-locked, the pre-flight is pure policy-as-code, and the consent capture is a finite state machine. What holds it back from 9–10: (a) **graceful barge-in handling + abandonment-vs-completeness tuning** (Gap A) still needs polish, (b) **reading ambiguous/vulnerable consent** needs an HITL escape hatch (Gap C), (c) the **four-regulator config keeps moving** and a stale gate is a live liability (Gap D), and (d) the **explicit-vs-notice consent-mode judgment** must be correctly pre-encoded per campaign (Gap B). With a config-driven rules layer, a barge-in-aware disclosure FSM, and a vulnerability HITL trigger, this comfortably ships autonomously for the bulk of traffic — **8/10**, second only to the most mechanical sub-steps. The legal blast radius (DPDP ₹250cr / UCC ₹25k-per-complaint) is the reason it isn't a careless 10: correctness here is *cheap to automate but expensive to get wrong*, so it must be deterministic + audited, not LLM-improvised.

---

## 9. Build spec

**Implement:**
1. **Pre-flight compliance-as-code gate** (pre-session, deterministic): DND/DNC scrub (full + category) + DLT header/template validation + 9am–9pm promotional time-window guard + 140/1600-series correctness + consent-on-file lookup (`valid/stale/withdrawn`, honouring 7-day/contract-life caps). Fail any → drop/route-to-service-only; never reach conversation.
2. **Session-open disclosure FSM** (non-skippable, before the dialog graph unlocks): template-locked, language-correct (a) recording disclosure, (b) DPDP plain-language purpose notice (current registry version), (c) AI/synthetic-voice SGI disclosure, (d) brand + on-behalf-of identity, (e) withdrawal route line. PII-collection tools gated on `disclosure_done=true`.
3. **Affirmative-consent capture** (where explicit consent required): voice-yes or DTMF "press 1"; **silence = no consent**; intent classifier `accept/refuse/unclear`; `unclear` → one re-prompt, never auto-proceed.
4. **Consent-branch routing:** refuse → `no_record_path` (if configured) or non-coercive `graceful_end`; recording pipeline halted deterministically on refuse.
5. **Separate marketing/cross-sell gate:** cross-sell sub-graph hard-disabled unless `marketing_consent=valid AND not promo-category-DND`. No bundling.
6. **Versioned notice registry** (campaign→purpose→language→notice text, version-IDed) + **config-driven rules layer** (DND windows, consent caps, AI-line, series map) decoupled from code, change-reviewed.
7. **Immutable consent ledger** (WORM/append-only, signed): `{number, purpose, consent=Y/N, ts, language, notice_version, channel, agent_id}`; wired to a DPDP **Consent Manager** path + withdrawal channel (STOP/1909/DTMF) that propagates to DND.
8. **Barge-in-aware delivery:** hold conversation lock until mandatory lines confirmed-emitted; re-deliver missed line conversationally; shortest-legally-sufficient phrasing per language.
9. **Vulnerability/non-comprehension HITL hook** on the consent turn.

**Data needed:**
- Per-campaign **policy matrix** (purpose → recording-consent mode: notice-only vs explicit; category-DND mapping; series; time-window).
- **Notice text corpus** per purpose × 12+ Indian languages, version-controlled.
- **Labelled consent-turn set** (accept / refuse / unclear) in Hinglish + regional, incl. ambiguous + vulnerable examples.
- **DND/DLT registry access** (full + category) + telco integration.

**Eval metrics that gate "good enough to ship":**
- **Disclosure presence + ordering:** 100% of calls emit recording + DPDP-notice + AI-disclosure in the correct language, *before* PII collection — zero misses on a held-out + adversarial-barge-in set.
- **Consent-artefact completeness:** 100% of sessions log `{consent, purpose, ts, language, notice_version}`; zero hollow/silence-as-consent records.
- **Pre-flight correctness:** 100% block of category-DND / out-of-window / stale-consent / unregistered-header calls on a synthetic registry test set; zero false-allows.
- **No-bundling:** 0 cross-sell pitches fired without separate valid marketing consent.
- **Consent-turn classifier:** ≥ target accuracy on Hinglish/regional accept-vs-refuse with **`unclear` never auto-proceeding**.
- **Withdrawal equal-ease:** withdrawal route present in 100% of opens and functional end-to-end (STOP → DND propagation verified).
- **Abandonment:** opening-line completion without abandonment within target (A/B the shortest compliant phrasing).

**Ship gate** = ALL of: 100% disclosure presence/ordering (incl. barge-in) AND 100% consent-artefact completeness AND zero pre-flight false-allows AND zero consent-bundling AND withdrawal equal-ease verified.

---

## 10. India specifics

- **Four regulators stack on the *same opening seconds*.** TRAI (DLT/DND/UCC/series/auto-dialer disclosure + consent-validity caps) governs *whether you may call*; DPDP (notice + purpose + affirmative consent + withdrawal) governs *whether you may record/process*; MeitY IT Rules 2026 governs *the AI-disclosure line*; RBI/IRDAI add sectoral retention. The open must satisfy all four simultaneously — a uniquely Indian four-way stack. ([Caller Digital regulatory map 2026](https://www.caller.digital/blog/voice-ai-india-regulatory-map-2026))
- **"DLT lets you call, not record."** A crucial India nuance: DLT/DND clearance proves you were *allowed to dial* but says *nothing* about recording/processing/retention — that's DPDP's separate consent. Teams routinely conflate the two and skip the recording-consent artefact. ([Caller Digital consent audit 2026](https://www.caller.digital/blog/dpdp-vs-trai-consent-voice-recordings-audit-trail-india-2026))
- **Category-DND is the silent trap.** A number not on *full* DND can still have opted out of *your category* (banking/insurance/real-estate/education/health). Scrubbing only full-DND fires a promotional call that costs **₹25,000/complaint on the PE**. Category-aware scrubbing is mandatory, not optional. ([Caller Digital DND 2026](https://www.caller.digital/blog/trai-dnd-compliance-ai-outbound-calling-india))
- **Consent decays fast.** TRAI's **7-day transactional cap** + **contract-life implicit** means "we have consent" is a time-bound claim; the gate must check *freshness*, not just existence. ([Securiti 2025](https://securiti.ai/india-spam-rules-trai-latest-amendment/))
- **Language is part of "informed."** DPDP "informed consent" + RBI "preferred-language" mean the recording/DPDP/AI lines must play in the **customer's language** (12+ Indian languages) — an English-only open to a Hindi-only customer is not informed consent. Indic TTS + per-language notice registry are load-bearing.
- **Affirmative-action over one-party consent.** Historically India was one-party-consent for recording; DPDP shifts commercial BPO toward **explicit, documented, purpose-specific consent** with **silence ≠ consent** and **equal-ease withdrawal** (say STOP / 1909 / press 1). ([ClearTouch 2026](https://www.cleartouch.in/blog/call-center-audio-recording-legal-requirements-in-india/); [Caller Digital 2026](https://www.caller.digital/blog/dpdp-vs-trai-consent-voice-recordings-audit-trail-india-2026))
- **9am–9pm + 140/1600 series are hard, mechanical rails.** A promotional call after 9pm or on the wrong series is an open-and-shut UCC breach — trivial to enforce in code, embarrassing to miss. ([ClearTouch outbound timings 2026](https://www.cleartouch.in/blog/trai-guidelines-for-outbound-calling-timings-in-india/); [Elision](https://www.elisiontec.com/140-and-160-series-regulations-from-trai-complete-guide-faqs/))
- **Consent Manager ecosystem is emerging.** DPDP Rules 2025 create **registered Consent Managers** as cross-fiduciary consent intermediaries — a mid-market BPO should architect its consent ledger to *interoperate* with these rather than silo consent. ([EY DPDP Rules 2025](https://www.ey.com/en_in/insights/cybersecurity/transforming-data-privacy-digital-personal-data-protection-rules-2025); [Seclore](https://www.seclore.com/fundamentals/dpdp-rules-2025-compliance-guide/))
- **Notice-version proof is the litigation defence.** When a customer complains months later, the *only* defence is showing exactly which versioned notice they heard and that they affirmatively accepted — so logging `notice_version` to an immutable ledger is the single highest-leverage India-specific build detail. ([Caller Digital 2026](https://www.caller.digital/blog/dpdp-vs-trai-consent-voice-recordings-audit-trail-india-2026))

---

### Sources
- Securiti, *India Strengthens Spam Rules: TRAI TCCCPR 2025 Amendment* — https://securiti.ai/india-spam-rules-trai-latest-amendment/
- Sigma Chambers, *2025 TCCCPR Amendments* — https://www.sigmachambers.in/post/2025-tcccpr-amendments-a-renewed-push-by-trai-for-order-in-commercial-communications-1
- Saikrishna & Associates, *Strengthening Consumer Protection — Amendment to TCCCPR* — https://www.saikrishnaassociates.com/strengthening-consumer-protection-by-trai-amendment-to-the-tcccpr/
- MEF, *In India, TRAI Tougher on Spam* — https://mobileecosystemforum.com/2025/07/11/in-india-trai-tougher-on-spam-a-call-for-industry-action/
- Caller Digital, *TRAI DND Compliance for AI Outbound Calling India 2026* — https://www.caller.digital/blog/trai-dnd-compliance-ai-outbound-calling-india
- Caller Digital, *DPDP vs TRAI Consent for Voice Recordings — Audit Trail India 2026* — https://www.caller.digital/blog/dpdp-vs-trai-consent-voice-recordings-audit-trail-india-2026
- Caller Digital, *Voice AI India Regulatory Map 2026* — https://www.caller.digital/blog/voice-ai-india-regulatory-map-2026
- ClearTouch, *Call Center Audio Recording Compliance — India* — https://www.cleartouch.in/blog/call-center-audio-recording-legal-requirements-in-india/
- ClearTouch, *TRAI Guidelines for Outbound Calling Timings in India 2026* — https://www.cleartouch.in/blog/trai-guidelines-for-outbound-calling-timings-in-india/
- ConversAI Labs, *Voice AI Compliance in India* — https://www.conversailabs.com/blog/voice-ai-compliance-in-india
- Auto Interview AI, *AI Calling India — DPDP, TRAI DLT, RBI Compliance Guide 2026* — https://www.autointerviewai.com/blog/ai-calling-india-dpdp-trai-dlt-compliance-complete-guide-2026
- EY India, *Transforming Data Privacy — DPDP Rules 2025* — https://www.ey.com/en_in/insights/cybersecurity/transforming-data-privacy-digital-personal-data-protection-rules-2025
- Seclore, *DPDP Rules 2025 Compliance Guide* — https://www.seclore.com/fundamentals/dpdp-rules-2025-compliance-guide/
- Scrut, *DPDP Rules — Implementation Checklist* — https://www.scrut.io/post/dpdp-rules
- Alohaa, *Is Call Recording Legal in India?* — https://www.alohaa.ai/blog/is-call-recording-legal-in-india-understanding-the-laws-and-practices
- SMSCountry, *DLT Registration: Complete TRAI Guide 2026* — https://www.smscountry.com/blog/dlt-registration/
- Message Central, *India SMS Regulations, DLT & TRAI Compliance 2026* — https://www.messagecentral.com/sms-guideline/india
- Elision, *140 & 160 Series Regulations from TRAI* — https://www.elisiontec.com/140-and-160-series-regulations-from-trai-complete-guide-faqs/
- Phonexa, *IVR Consent* — https://support.phonexa.com/call-routing/ivr-ivr-consent
- TRAI, *Regulation (TCCCPR Amendment) 12-Feb-2025* — https://www.trai.gov.in/sites/default/files/2025-02/Regulation_12022025.pdf

*Draft research dossier for review. Cited where possible; [estimate]/[UNSOURCED] elsewhere. Not legal advice.*
