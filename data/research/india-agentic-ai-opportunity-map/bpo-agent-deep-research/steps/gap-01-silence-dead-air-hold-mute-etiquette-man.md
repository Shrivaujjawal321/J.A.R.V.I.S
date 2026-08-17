# Gap-01 — Silence / Dead-Air & Hold-Mute Etiquette Management

> Deep-research dossier for an India-market, multilingual (Hindi + regional + Hinglish), RBI/IRDAI/DPDP/TRAI-compliant, action-taking voice+chat contact-center agent for mid-market BPOs.
> Scope: **ONLY** the social ritual around *unavoidable waits* — the human stagecraft that keeps a customer feeling attended-to while the agent is thinking, reading a screen, waiting on a 20-second backend call, consulting a supervisor, or needs to cough/mute. This is the connective tissue *between* the "primary" steps. The latency/barge-in engineering (b01) covers the <700ms turn loop; this dossier covers what happens when the wait is *longer than a turn* and the agent must manage the human's perception of that wait.

Last updated: 2026-06-24

---

## 0. Why this micro-step is its own thing (and why it is usually missed)

Every latency document optimises the *steady-state* turn: ASR → NLU → LLM → TTS in <700ms. That budget assumes the answer is *available*. The real call has three classes of wait that blow past that budget and are **not** an engineering bug to be removed — they are unavoidable physics:

1. **Cognitive wait** — the agent (human or AI) is reasoning/looking something up. 1–4s.
2. **System wait** — a backend write/read takes 3–30s (CBS refund, KYC push, payment gateway, slow CRM). Cannot be sped past the upstream system.
3. **Off-stage wait** — the agent must consult a supervisor, check a second screen, sneeze, or talk to a colleague — and the customer **must not hear it**.

A skilled human never lets any of these become *dead air*. Dead air on a voice call is the single most corrosive UX failure: at ~1.5–2s of unexplained silence the customer says "Hello? Are you there?", assumes the line dropped, or assumes the agent is incompetent. The b01 pipeline can hit 600ms and **still feel broken** if, the one time it takes 18 seconds to process a refund, it goes silent. **The wait is inevitable; the silence is a choice.** This step is the craft of converting unavoidable wait into *managed, narrated, permission-based* wait.

It is missed because it has no "intent," no "transaction," no row in a CRM. It is pure social protocol — and protocol is exactly what naive LLM voice agents fumble: they either talk continuously (no room to think, robotic), or they go silent while a tool runs (feels dead), or they say "one moment" and then **never come back** during a 25s wait (abandonment feel), or they leak off-stage audio because they have no concept of "mute."

---

## 1. Human micro-steps (what a skilled BPO agent actually does)

A senior CSR at a Teleperformance / Concentrix / iEnergizer / Tech Mahindra process runs a continuous, mostly-unconscious sub-protocol. Decomposed to atomic moves:

1. **Detect that a wait is coming and classify it** — "this needs a lookup" (short, fill in place) vs "this needs a real hold" (long, ask permission) vs "this is off-stage" (mute). The classification happens *before* the silence, not after.
2. **Pre-emptive micro-acknowledgement (gap-filler)** — for a 1–4s cognitive wait, drop a short verbal token *immediately* so there is zero silence: "ji ek second…", "let me just check that for you…", "main dekh raha hoon…". This is said in the agent's normal voice, conversationally, not scripted.
3. **Continuous low-stakes narration during a medium wait** — "abhi aapka account khul raha hai… haan mil gaya…" — narrating the screen so the customer *hears progress* even when nothing is resolved yet.
4. **Explicit hold request with reason + duration + permission** — for anything >~15–20s or anything requiring the agent to fully disengage: "Sir, iske liye mujhe system check karna padega, kya main aapko 2 minute ke liye hold pe rakh sakta hoon?" — three components: **reason**, **estimated duration**, and an actual **permission ask** that waits for a yes.
5. **Wait for and register consent** — does not slam the customer onto hold mid-sentence; waits for "haan theek hai" / "yes okay" (and handles "no, I'll wait on the line" or "actually I'm in a hurry").
6. **Engage hold cleanly** — presses hold so the customer gets hold-tone/music (not the agent's background, not dead silence, not the agent typing).
7. **Periodic check-back on a ~30–45s cadence** — comes back *before* the customer gets anxious: "Sir, thank you for holding, main abhi bhi check kar raha hoon, bas ek minute aur…". Re-confirms the line is alive and resets the patience clock.
8. **Honour the quoted time / renegotiate** — if it's taking longer than the "2 minutes" promised, comes back, apologises, gives a new estimate, and **re-asks** to continue holding rather than silently overrunning.
9. **Clean return from hold** — "Sir, thank you so much for holding, sorry to keep you waiting — toh maine check kiya…" — a deliberate re-entry that acknowledges the wait and immediately delivers value.
10. **Mute discipline for off-stage moments** — mutes the mouthpiece to cough, sneeze, sip water, ask the team lead a quick question, or let a floor announcement pass — so the customer hears *nothing* objectionable.
11. **Un-mute safety check** — before un-muting/speaking, makes sure the off-stage exchange has ended; never returns mid-sentence of a side-conversation. (The classic human failure: un-muting while still saying "…yaar isko kya bolun".)
12. **Hold-overflow / abandonment guard** — if the wait becomes very long (supervisor unreachable, system down), proactively offers a callback or alternative rather than holding the customer hostage in silence: "Sir, ye thoda time le raha hai — main aapko 10 minute mein callback karwa doon?"
13. **Read the customer's tolerance** — an irate or rushed customer gets shorter holds, more frequent check-backs, and faster escalation; a calm customer tolerates a longer single hold. The cadence is *adaptive*, not fixed.

Moves 1, 5, 8, 11, 12, 13 are where human social intelligence quietly carries the call. They are not in any script and are exactly where naive agents break.

---

## 2. Agent approach (how a 2026 agent does each sub-step)

The architecture is a **wait-aware dialogue controller** sitting between the LLM/tool layer and the TTS, driven by *tool-call lifecycle events* rather than by the LLM's text alone. The key insight: the LLM should **not** be the thing that decides "stay silent for 18s." A deterministic **filler/hold orchestrator** owns the audio of the wait; the LLM owns the *words* of the acknowledgement and the *reason*.

| Human micro-step | 2026 agent technique |
|---|---|
| 1. Detect & classify the wait | The orchestrator inspects the **pending tool call's declared latency class** (each tool registered with `expected_latency: fast(<1s) / medium(1–5s) / slow(5–60s)`). Classification is metadata-driven, fired the instant a tool is invoked — **before** any silence. |
| 2. Pre-emptive micro-ack (gap-filler) | **Speculative filler streamed to TTS while the LLM/tool is still running.** Pattern: emit a short acknowledgement token immediately (`"ek second…"`) decoupled from the main reply. LiveKit `BackgroundAudioPlayer` with a **thinking sound** (`BuiltinAudioClip.KEYBOARD_TYPING`) auto-plays when the agent is "thinking"; spoken fillers layer on top. (Source: LiveKit Agents `BackgroundAudioPlayer` / `AudioConfig` / `BuiltinAudioClip` docs, 2026.) GPT-Realtime-class models emit ~16% spoken-filler rate to cover gaps. (Source: Tough Tongue AI / VoiceInfra prompt-engineering guides, 2026.) |
| 3. Continuous narration (medium wait) | For `medium` tools, orchestrator streams **progress narration** tied to tool-call lifecycle events (`tool_started → tool_progress → tool_finished`), so the agent literally says "abhi khul raha hai… mil gaya." Falls back to ambient/thinking audio (`OFFICE_AMBIENCE`) so the channel is never dead. |
| 4. Explicit hold request (reason+duration+permission) | For `slow`/off-stage waits, a **HOLD state** in the dialogue FSM: LLM generates a structured hold-intent (`{reason, est_seconds, needs_consent:true}`); TTS speaks reason + estimate + permission; FSM **blocks** until consent is parsed. The estimate comes from the tool's p50/p95 latency telemetry, not a guess. |
| 5. Register consent | Turn-detector + semantic classifier on the reply: `consent_yes / consent_no / conditional`. On `no` (customer wants to stay on line), agent skips music-hold and narrates instead. (Source: AssemblyAI / Hamming AI semantic turn-detection, 2026.) |
| 6. Engage hold cleanly | On consent, orchestrator switches the outbound audio to **hold media** (music/tone) and *suppresses* the live mic + thinking audio; the customer hears designed hold audio, never raw backstage. |
| 7. Periodic check-back (~30–45s) | A **hold-timer** fires check-back events on a configurable cadence (default 30s, adaptive). Each tick speaks a fresh reassurance line ("thank you for holding, still working on it"). The timer is deterministic — it does **not** depend on the LLM remembering to come back. This is the single most important fix vs naive agents. |
| 8. Honour/renegotiate the quote | If `elapsed > quoted_estimate`, orchestrator forces a **re-consent event**: apologise, new estimate, re-ask. Prevents silent overrun. |
| 9. Clean return from hold | On `tool_finished`, FSM transitions HOLD→ACTIVE with a templated re-entry ("thank you for holding, sorry for the wait — so…") then delivers the result in the same breath. |
| 10. Mute discipline | For an AI agent "mute" maps to **output gating**, not a physical button: when the orchestrator triggers an off-stage action (e.g., an internal supervisor-LLM consult, a tool that would otherwise narrate), it **routes that audio to /dev/null** and plays hold/ambient to the customer. There is no literal cough — the risk is *internal reasoning or tool chatter leaking to TTS*. Mute discipline = a hard gate that only the "customer-facing" channel reaches TTS. |
| 11. Un-mute safety check | Before re-opening the customer channel, a **guard** confirms the off-stage task is complete and the next utterance is customer-directed (no leakage of internal tokens / system prompts / tool JSON). Output-side guardrail filter. |
| 12. Hold-overflow / abandonment guard | A **max-hold budget** (e.g., 90s) → on breach, FSM offers callback/async resolution instead of infinite hold. Wired to the b04 HITL / callback queue. |
| 13. Adaptive cadence to tolerance | Emotion/sentiment signal (a06) feeds the orchestrator: irate/rushed → shorter max-hold, faster check-back (15–20s), earlier escalation; calm → standard cadence. |

**Core pattern named:** *Classify-the-wait → Fill (speculative ack + thinking audio) → if-long: Request-consent → Hold (designed media, mic+reasoning gated) → Check-back on deterministic timer → Renegotiate-on-overrun → Clean-return.* The LLM owns *what to say*; a deterministic FSM + timer + audio router owns *the silence*. Never let the LLM "decide" to be quiet.

---

## 3. Tooling (concrete 2026 stack)

- **Voice runtime / audio routing:** **LiveKit Agents** — `BackgroundAudioPlayer` with `AudioConfig(volume, probability)`, `BuiltinAudioClip.OFFICE_AMBIENCE` (ambient) + `BuiltinAudioClip.KEYBOARD_TYPING` (thinking sound auto-played while the agent thinks), `allow_interruptions` on `session.say()`/`generate_reply()`. Or **Pipecat** processor pipeline (VAD→STT→LLM→TTS) where a custom frame processor injects filler frames on tool-call frames. (Source: LiveKit Agents docs + `examples/voice_agents/background_audio.py`, 2026; Pipecat GitHub, 2026.)
- **Turn-taking / barge-in / false-interrupt control:** **Krisp 6M-param turn-taking model**, LiveKit built-in turn detector, or AssemblyAI/Hamming semantic endpointing — so a *gap-filler* ("let me check…") is **not** clipped by the customer's "okay" backchannel, and a real interruption during hold *is* caught. (Source: Krisp turn-taking model, 2026; Hamming AI interruption runbook, 2026.)
- **Hold/IVR media:** CPaaS/telephony layer (b10) — Plivo / Exotel / Ozonetel / Knowlarity (India) — supplies designed hold music/tone; orchestrator swaps streams on HOLD.
- **Dialogue FSM / orchestration:** **LangGraph** (durable state, HOLD node with pause/resume) or **Pipecat Flows**; tool registry carries `expected_latency` + p50/p95 telemetry. Async tool pattern: invoke synchronously, **narrate asynchronously** while it runs.
- **Filler-text generation:** small fast model (Gemini 2.5/3.x Flash-Lite, Sarvam-M for Hindi) generates contextual, non-repetitive fillers; or a **curated multilingual filler bank** (pre-rendered TTS clips) for zero-latency, deterministic, brand-safe phrasing.
- **Indic TTS for fillers (b03):** Sarvam / Dhwani / ElevenLabs-multilingual — fillers and check-backs need natural Hindi/Hinglish prosody, not robotic ("ji ek second" must sound human).
- **Output-side guardrail (mute leakage):** a thin filter that strips system/tool/internal-reasoning tokens from the TTS-bound channel (NeMo-Guardrails output rail / custom).
- **Observability (b12):** instrument **dead-air ms per call**, **hold count/duration**, **check-back adherence**, **abandon-during-hold rate**, **filler-repetition rate** as first-class metrics.

---

## 4. Benchmarks (real numbers)

- **Dead-air tolerance threshold:** customers perceive **>300ms** as "thinking time" that breaks immersion; ~1.5–2s of unexplained silence triggers "hello? are you there?" / drop-assumption. [sourced — CallSphere / VoiceInfra latency guides, 2026]
- **Steady-state turn budget (for contrast):** leading 2026 stacks hit **580–640ms** end-to-end across 200 calls; third-gen pipelines keep total <800ms. [sourced — Retell AI benchmarking, 2026] — but this is the *available-answer* path; the wait-management path is what covers the >800ms cases.
- **Filler rate (natural coverage):** GPT-Realtime-class achieves **~16%** filler-phrase rate ("let me check") to cover gaps naturally. [sourced — Tough Tongue AI / VoiceInfra, 2026]
- **Barge-in / false-interrupt production bar (2026):** turn-taking gap **200–400ms**, **false-barge-in rate <2%**, **TTS flush <60ms**. [sourced — FutureAGI / CallSphere barge-in guides, 2026] Directly governs whether a spoken filler survives a customer backchannel.
- **Backend round-trip that must be masked:** CBS/payment/CRM writes typically **300ms–3s**, with `slow` outliers to **20–30s** (the exact case this step exists for). [sourced — Retell AI, 2026; a11 dossier]
- **Human hold-etiquette cadence (industry training standard):** quote a time frame for any hold **>30s**; **check back within the quoted time**; thank for patience on return. [sourced — AVOXI / Sprinklr / Gladly call-center etiquette guides, 2026] → the agent's default check-back cadence (30s) is calibrated to this human standard.
- **Abandon-during-hold:** no clean published AI baseline. **[estimate]** target: <3% abandon on holds ≤90s with 30s check-backs; deterministic check-back timer is the lever. Human benchmark: long unmanaged holds are a top driver of call abandonment.

---

## 5. Failure modes (where the agent breaks)

- **Dead air on slow tools** — the #1 failure: LLM calls a 20s tool, no filler/timer wired, channel goes silent → customer assumes drop. (Naive single-prompt agents do exactly this.)
- **The "one moment" black hole** — agent says "ek second" then *never comes back* during a long wait because there is no deterministic check-back timer; the LLM "forgot" it was mid-task.
- **Filler clipped by backchannel** — customer says "haan" / "okay" over the agent's "let me check…", weak turn-detector treats it as interruption, agent stops and the wait-cover collapses into silence.
- **Robotic / repetitive fillers** — same "please hold one moment" every single time → uncanny, obviously scripted; erodes trust.
- **Hold without permission / no reason / no estimate** — agent dumps customer onto hold mid-sentence, or says "please hold" with no reason or time → reads as rude/evasive (the human ritual's three components are missing).
- **Silent overrun** — quoted "2 minutes," takes 5, no apology/renegotiation → trust collapse.
- **Mute leakage (the AI-specific catastrophe)** — internal reasoning, tool JSON, system-prompt fragments, or an off-stage supervisor-LLM consult leaks to TTS and the customer hears "the model talking to itself." The human-cough-analogue failure, but worse because it can leak PII or policy internals.
- **Un-mute mid-thought** — agent resumes the customer channel while an internal/async task is still emitting → customer hears half of a system utterance.
- **Hold during an irate moment** — putting an already-angry customer on a long hold with sparse check-backs → escalation; cadence not adapted to sentiment.
- **Code-mix register break in fillers** — English filler bolted onto a Hindi conversation ("please stay on the line") jars; the filler must match the conversation's language/register (a05).
- **Infinite hold (no overflow guard)** — supervisor/system unreachable, no max-hold budget → customer held hostage until they hang up.

---

## 6. Gap to full adaptation (what the agent still cannot do as well as a human, and the path to close it)

**What humans still do better:**
- **Truly adaptive, read-the-room cadence.** A human shortens holds for a sighing, rushed customer and stretches them for a chatty, relaxed one — fluidly, mid-call, on subtle vocal cues. Agents do a coarse 2-bucket version (calm vs irate) via sentiment, but miss the fine gradient and the *trajectory* (a customer getting more impatient over successive holds).
- **Graceful, human-sounding over-the-shoulder narration.** "Haan, system thoda slow hai aaj, sorry…" — the small, honest, humanising asides that make a wait feel shared rather than imposed. Agents produce these stiffly or not at all.
- **Knowing when *not* to hold.** A human often realises "this isn't worth a hold, let me just call you back" or "I'll keep you on and chat while it loads." Agents over-rely on the binary hold/no-hold and under-use the "stay-and-chat" middle path.
- **Zero-leakage off-stage instinct.** A human *knows* the mouthpiece exists and muting is reflexive. An agent has no native "off-stage" concept — every leakage is an engineering gate that can be misconfigured.

**Concrete path to close it:**
1. **Wait-management eval set** — build a labelled corpus of calls with `slow`-tool moments and score agents on dead-air-ms, check-back adherence, filler diversity, leakage incidents, abandon-during-hold (see §9). Gate releases on it.
2. **Sentiment→cadence policy as code** — make check-back interval and max-hold a *function* of live sentiment + hold-trajectory, tuned against the eval set, not a fixed 30s.
3. **Contextual filler generation with anti-repetition memory** — track fillers used this call; force diversity; match language/register (a05) per filler.
4. **Hard output-channel firewall** — make "customer-facing TTS channel" a single audited egress that *only* whitelisted, customer-directed text can reach; treat any internal-token leak as a Sev. Close the mute-leakage gap by construction.
5. **"Stay-and-chat" and "callback-instead" as first-class options** in the FSM, with a policy for when to choose each, so the agent stops over-using cold hold.

---

## 7. HITL trigger (when a human MUST take over for this step)

This micro-step is **low-stakes by itself** (it's stagecraft, not a transaction), so it rarely *needs* a human — but it is the **canary** that should *trigger* handoff for the underlying cause:

- **Max-hold budget breached** (e.g., backend down >90s, supervisor-consult unresolved) → don't hold longer; **warm-transfer or offer callback** (b04/a15). The hold-overflow guard *is* the HITL trigger.
- **Customer explicitly demands a human while on hold** ("I don't want to wait, give me a person") → immediate escalation, preserve context.
- **Repeated overruns on the same call** (≥2 broken time-quotes) → escalate; the agent is clearly stuck on something it can't resolve.
- **Mute-leakage incident detected** (internal tokens reached/nearly reached TTS) → flag the session, and in regulated processes treat as a potential data-exposure event for review.
- **Otherwise: fully automatable.** Routine fill/hold/check-back/return needs no human.

---

## 8. Automation readiness — **8 / 10**

The mechanics (speculative filler, thinking audio, deterministic check-back timer, designed hold media, output gating) are **shipping today** in LiveKit/Pipecat and production stacks — this is largely a solved *engineering* problem when explicitly built. The remaining 2 points are the genuinely human bits: fine-grained adaptive cadence to a shifting emotional read, naturally humanising asides, the judgment of when to stay-and-chat vs hold vs call back, and bulletproof zero-leakage off-stage discipline. It is **not** a hard-blocked human-only step; it's "fully buildable to ~90% with current tools, last-mile naturalness is the gap." High confidence the readiness rises to 9 within a year as turn-taking models + sentiment-driven cadence mature.

---

## 9. Build spec (what to implement, data needed, eval gate)

**Implement:**
1. **Wait-aware dialogue FSM** (LangGraph or Pipecat Flows) with states `ACTIVE / FILLING / HOLD_REQUEST / HOLD / RETURN`, driven by tool-call lifecycle events (`tool_started/progress/finished`), not LLM text.
2. **Tool latency registry** — every tool annotated `expected_latency: fast|medium|slow` + live p50/p95 telemetry feeding the spoken time-estimate.
3. **Speculative filler layer** — on `tool_started`, immediately stream a contextual filler (small fast model or curated multilingual bank) to TTS; layer `BackgroundAudioPlayer` thinking audio (`KEYBOARD_TYPING`) underneath. Anti-repetition memory per call.
4. **Deterministic check-back timer** — fires every N seconds during HOLD (default 30, sentiment-adaptive), speaks a fresh reassurance line; independent of LLM memory.
5. **Consent gate** for `slow`/off-stage waits — speak reason+estimate+permission, block on semantic `consent_yes/no/conditional`.
6. **Hold-media swap** — on consent, route outbound to designed hold music (CPaaS), gate mic + thinking audio.
7. **Output-channel firewall** — single audited TTS egress; whitelist customer-directed text only; alarm on internal-token leak (the mute-discipline guarantee).
8. **Overrun renegotiation + max-hold overflow → callback/HITL** wiring.

**Data needed:**
- Multilingual **filler & check-back & return phrase banks** (Hindi / Hinglish / Tamil / Telugu / Marathi / Bengali / English), register-matched, pre-rendered TTS for zero-latency.
- A **labelled call corpus** containing real `slow`-tool moments + hold sequences, annotated with: dead-air spans, check-back events, consent exchanges, leakage incidents, abandon-on-hold outcomes, and per-segment sentiment.
- Tool **latency telemetry** (p50/p95) per backend.

**Eval metric to gate release (all must pass on the corpus):**
- **Max dead-air per call ≤ 1.2s** (no silence span beyond it during any wait). *Primary gate.*
- **Check-back adherence ≥ 98%** (a check-back fires within cadence+10% on every hold >quoted).
- **False-barge-in on fillers < 2%** (fillers not clipped by backchannels).
- **Filler-repetition rate < 10%** per call (anti-robotic).
- **Mute-leakage incidents = 0** (zero internal/tool/PII tokens reach TTS). *Hard fail on any.*
- **Abandon-during-hold ≤ 3%** on holds ≤90s.
- **Consent-before-hold = 100%** for `slow`/off-stage holds (no surprise holds).

---

## 10. India specifics

- **Language/register matching is non-negotiable.** Fillers and check-backs must mirror the call's code-mix (a05): "ji ek second", "bas ho hi gaya hai", "thodi der aur lagegi, sorry" in Hindi/Hinglish; equivalent natural forms in Tamil/Telugu/Marathi/Bengali/Kannada. An English "please stay on the line" injected into a Hindi call is an instant tell. Build the filler bank per-language, not translated-on-the-fly.
- **Honorific/respect register.** Indian customers expect "sir/ma'am/ji", "aap" (never "tu/tum"), and apologetic framing on waits ("sorry to keep you waiting"). The check-back and return lines must carry this respect register — the same rule Boss enforces for Jarvis.
- **Patience norms & line quality.** Indian mobile calls have higher drop/jitter rates; an unexplained silence is *more* likely to be read as "call dropped." Dead-air discipline matters *more*, not less. Conversely, customers on flagship NBFC/telco lines are conditioned by years of IVR holds and tolerate *announced* holds reasonably — provided permission + reason + check-back are present.
- **DPDP / mute-leakage = data exposure.** Under DPDP, leaking another customer's data or internal system details via a mute-discipline failure is a reportable exposure. The output-channel firewall (§9.7) is a *compliance* control here, not just UX (ties to b08 compliance-as-code, b11 PII).
- **TRAI / call-recording context.** Holds and check-backs occur on recorded lines; the designed hold media and announcements should be consistent with disclosure/recording norms already handled in a12/b08.
- **Cost-sensitivity (b12).** Long holds burn LLM/TTS/telephony minutes with no resolution; the max-hold→callback overflow guard is also a **cost-per-resolution** lever for mid-market BPOs, not only a UX one.
- **India voice stack alignment.** Sarvam / Bolna / Gnani / Caller Digital templates already ship TRAI/DPDP-compliant voice loops; the wait-management FSM layers on top of these rather than replacing them.

---

### Sources
- LiveKit Agents — `BackgroundAudioPlayer`, `AudioConfig`, `BuiltinAudioClip` (OFFICE_AMBIENCE / KEYBOARD_TYPING), `allow_interruptions`; `examples/voice_agents/background_audio.py` (docs.livekit.io, 2026)
- Pipecat — open-source voice pipeline / Flows (github.com/pipecat-ai/pipecat, 2026)
- Krisp — 6M-param turn-taking model for voice agents (krisp.ai, 2026)
- AssemblyAI — voice agent turn detection (assemblyai.com, 2026); Hamming AI — interruption-handling runbook (hamming.ai, 2026); FutureAGI — barge-in & turn-taking 2026 guide (futureagi.com, 2026)
- CallSphere — voice-agent latency & barge-in (callsphere.ai, 2026); VoiceInfra — voice AI prompt-engineering guide (voiceinfra.ai, 2026); Tough Tongue AI / Auto Interview AI — filler-rate & latency-masking (autointerviewai.com, 2026)
- AVOXI / Sprinklr / Gladly / Versadial — call-center hold etiquette & check-back standards (2026)
- Retell AI — voice latency & build guide (docs.retellai.com, 2026); Sierra — engineering low-latency voice agents (sierra.ai, 2026)

Draft research note for review. Cited where possible; [UNSOURCED]/[estimate] elsewhere. Not investment advice.
