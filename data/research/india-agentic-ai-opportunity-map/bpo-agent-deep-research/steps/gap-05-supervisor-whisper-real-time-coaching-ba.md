# Gap Step 05 — Supervisor Whisper / Real-Time Coaching & Barge-In Support (the Live HITL Intervention Channel)

**Domain:** India-market, multilingual (Hindi + regional + Hinglish) voice + chat contact-center agent for mid-market BPOs, action-taking (servicing, collections, sales, money movement).
**Scope of this doc:** ONLY the *live, in-flight, third-party supervision channel* — a human supervisor (or a supervising AI) **monitoring an active AI session in real time**, **injecting guidance mid-call without stopping it (whisper/coach)**, or **taking over a struggling session live (barge-in / seamless takeover)** — and the operational, telephony, and economic machinery that makes one human able to do this across *many concurrent* AI sessions.
**Compliance envelope:** DPDP Act 2023 + Rules 2025 (live transcript + audio is personal data; supervisor access must be access-controlled, logged, purpose-bound), TRAI/DoT telecom (recording disclosure already covered in gap-03; a *third human listener* may itself need disclosure), labour/monitoring norms, plus the firm's own QA/consent regime. Telephony-side: the supervisor channel rides on CPaaS conferencing (Exotel/Ozonetel/ClearTouch listen-whisper-barge) or WebRTC SFU participant injection (LiveKit/Pipecat).
**Last researched:** 2026-06-24.

---

## 0. Why this is a distinct micro-step (not the same as gap b04 HITL-interrupt, A15 warm-handoff, or b09 QA)

This step is the **live, optional, third-party intervention rail** — and it is operationally different from every adjacent step the deep-research already covers:

1. **vs. A15 / b04 escalation & warm handoff:** Escalation is a *clean exit* — the AI *decides* it can't proceed, *announces* a transfer, *bundles a context packet*, and *hands the call away*. The supervisor-whisper rail is the opposite shape: **the session does NOT exit, the customer is NOT told, and the AI is NOT necessarily the one that triggers it.** A supervisor watching a wall of live sessions can inject a correction into an AI that *thinks it's doing fine*, or yank a call the AI hasn't flagged. It is unrequested, mid-stream, and (for whisper) invisible to both the customer and arguably to the AI's own "I'm confident" state. ([OnSIP monitor/whisper/barge](https://www.onsip.com/voip-resources/smb-tips/call-monitoring-features-monitor-whisper-and-barge-explained))

2. **vs. b09 QA/eval flywheel:** QA is *post-hoc* — sample 2% of yesterday's calls, score them, feed tuning back. This rail is *synchronous* — it changes the outcome of the call *that is happening right now*. QA improves tomorrow's agent; whisper/barge saves today's customer. Both are needed; conflating them is the classic mistake (you cannot "QA your way" out of a live session melting down). ([thequantumleap shift from passive analytics to in-call](https://www.thequantumleap.business/blog/call-coaching-ai-news-roundup-q2-2026))

3. **It is the trust substrate for the *whole* deployment.** Enterprises do not turn an action-taking AI loose on collections or money-movement without a "someone is watching and can pull the cord" guarantee. The live-takeover console *is* that guarantee. It is the difference between "fully autonomous, pray it's fine" and "human-on-the-loop." The 2026 control model has explicitly moved from **human-in-the-loop (approve every action)** to **human-on-the-loop (one human supervises many, intervenes on exception)** — and THIS rail is the mechanism that makes human-on-the-loop real. ([The New Stack human-on-the-loop](https://thenewstack.io/human-on-the-loop-the-new-ai-control-model-that-actually-works/); [Strata HITL 2026 guide](https://www.strata.io/blog/agentic-identity/practicing-the-human-in-the-loop/))

4. **It has its own economics: span-of-control.** A live human-center supervisor whispers to ~1 agent at a time and watches a handful. The agentic equivalent must let **one human supervise 18→30 concurrent AI sessions** — which means the hard problem is not "can a human take over" (trivially yes) but **"which of my 25 live sessions needs me RIGHT NOW, and can I context-load and intervene in <10s before it's too late."** That attention-allocation problem is a genuinely new capability with no human-center analog at that ratio. ([supervisor ratio 1:12→1:18→1:25-30](https://www.thequantumleap.business/blog/call-coaching-ai-news-roundup-q2-2026))

5. **The three modes are mechanically distinct on the audio path.** Monitor = read-only duplicated stream (neither party hears supervisor). Whisper = supervisor mic routed *only to the agent leg* (customer never hears it; in the agentic case the "agent" is software, so whisper becomes an *out-of-band guidance injection into the AI's context*, not audio). Barge = supervisor becomes a full conference participant / replaces the AI leg. Each needs different plumbing. ([ClearTouch monitor/whisper/barge](https://www.cleartouch.in/blog/call-center-software-features-monitor-whisper-barge/); [Happyfox whisper coaching](https://support.happyfox.com/kb/article/1606-understanding-whisper-private-coaching/))

> **One-line framing:** A15/b04 is the AI *asking* to leave. This step is a human (or supervisor-AI) *reaching in* — silently coaching, or forcibly taking the wheel — on a session that is still running, often without the AI having raised its hand.

---

## 1. Human micro-steps (the atomic decomposition)

What a real-center supervisor ACTUALLY does on the live-intervention rail — and what the agentic supervisor (human-on-the-loop) must reproduce:

1. **Live-floor scanning / triage** — keep a peripheral eye on many simultaneous live conversations, sweeping for the one that's starting to go wrong (rising customer anger, agent floundering, a high-value/high-risk call). Allocate scarce attention.
2. **Risk-prioritised attention allocation** — decide *which* session deserves the next 30 seconds: a VIP about to churn, a compliance-sensitive money-movement, a vulnerable caller, an agent visibly stuck. Triage under time pressure.
3. **Drop-in monitoring (silent listen)** — open one session and listen/read silently for a few seconds to *understand the situation* before doing anything — without either party knowing.
4. **Rapid context-load** — in those seconds, reconstruct: who's the customer, what's the intent, what has the agent tried, what's the emotional temperature, what's the risk. (A human supervisor does this from memory + screen-pop; the agentic version must surface it instantly.)
5. **Coaching-vs-barge decision** — judge whether a *whisper hint* will save it (agent is capable, just needs a nudge) or whether the situation needs the supervisor to *take the call* (agent is out of depth / customer demands a human / compliance line about to be crossed).
6. **Whisper formulation** — craft a short, actionable, in-the-moment hint the agent can act on *without* breaking conversational flow ("offer the retention discount," "stop, that's the wrong policy," "slow down, customer's confused"). Brevity + timing are the skill.
7. **Whisper delivery timing** — inject the hint at a *natural gap* so the agent can absorb and use it mid-conversation, not stomp on the customer.
8. **Barge-in execution (graceful seizure)** — when taking over: announce yourself appropriately, smoothly assume control, and continue the conversation *without making the customer re-explain* — the agent steps back, the supervisor steps in, continuity preserved.
9. **State / context inheritance on takeover** — carry over everything the agent knew (identity, verified status, what's been promised, what action is half-done) so the takeover doesn't lose work or re-traumatise the customer.
10. **Mid-call correction of a wrong action** — catch the agent about to do something wrong (quote a wrong figure, process the wrong account, breach a script) and stop/redirect it *before* the harm lands.
11. **Multi-session context-switching** — bounce between sessions, holding partial state for several at once, without dropping the thread on any — the cognitive load of supervising in parallel.
12. **Post-intervention handback / disposition** — after a whisper or barge, either return control (whisper) or close out the call (barge), tag what happened, and log the intervention for coaching/QA.
13. **In-the-moment coaching note** — capture *why* the intervention was needed so it feeds the agent's improvement (in the agentic case: feeds the eval/tuning flywheel, b09).
14. **Composure / judgment under pressure** — stay calm, decide fast, and not over-intervene (whispering five tips a minute) nor under-intervene (letting a call die) — the meta-skill of *good supervision*. ([vendors learned 5 suggestions/min gets muted](https://www.thequantumleap.business/blog/call-coaching-ai-news-roundup-q2-2026))

---

## 2. Agent approach (how a 2026 system does each sub-step)

The 2026 architecture is the **"supervisor + agent loop": a smaller pool of senior humans operating as orchestrators of multiple concurrent AI sessions, intervening on confidence drops or sentiment dips, feeding QA/tuning back** ([thequantumleap](https://www.thequantumleap.business/blog/call-coaching-ai-news-roundup-q2-2026)). The key architectural insight (from WebRTC frameworks) is that **the AI agent is just another participant in the call "room," so you can drop a human into the same room to take over, or run a second supervisor-agent that watches the first, without changing your architecture** ([LiveKit handoff pattern](https://livekit.com/blog/handoff-pattern-voice-agents)).

| # | Human sub-step | 2026 agent technique |
|---|----------------|----------------------|
| 1 | Live-floor scanning | **Supervisor console / "live floor" dashboard** rendering all active sessions as tiles with live signal badges (sentiment, risk, confidence, dead-air, escalation-pending). The human watches *signals*, not raw audio — the system pre-attends. ([Capacity real-time agent assist](https://capacity.com/blog/real-time-agent-assist-for-contact-centers/); [Ecosmob live monitoring](https://www.ecosmob.com/blog/live-call-monitoring-solution)) |
| 2 | Attention allocation | **Automated triage / "needs-you-now" ranker:** a meta-model scores every live session for intervention-urgency (sentiment slope, confidence drop, high-value account, compliance flag, agent-stuck/loop detection) and *sorts the supervisor's queue*, surfacing the top-1 with a reason. This is the genuinely-new capability vs human centers. |
| 3 | Silent monitoring | **Read-only live transcript + audio stream** of any session, one click. WebRTC: subscribe to the room as a hidden participant; CPaaS: native *listen/monitor* leg. ([LiveKit participants](https://docs.livekit.io/telephony/)) |
| 4 | Rapid context-load | **Auto-generated live "situation card"**: rolling LLM summary of the session-so-far (customer, verified intent, actions taken/pending, promises made, emotion arc, risk) — *always pre-computed* so the supervisor doesn't read 4 minutes of transcript. The single biggest enabler of high span-of-control. |
| 5 | Coach-vs-barge decision | **Recommended-action chip** ("suggest: whisper a discount" / "suggest: take over — compliance risk") from the triage model; human confirms. Lowers decision latency. |
| 6 | Whisper formulation | **For the AI agent, "whisper" = out-of-band context injection**, not audio: the supervisor types/picks a directive that is injected as a high-priority system message into the AI's next turn ("DIRECTIVE: offer retention_discount_10; do NOT quote penalty"). The AI obeys deterministically. For human agents on the floor, classic **real-time agent-assist whisper** (Cresta/Balto-style suggestion). ([Cresta live coaching](https://www.thequantumleap.business/blog/ai-driven-call-coaching-2026-capabilities-use-cases-trends); [thelevel.ai agent assist](https://thelevel.ai/blog/real-time-agent-assist/)) |
| 7 | Whisper timing | For AI: injection takes effect at the *next* turn boundary (natural, no audio collision). For human agents: assist surfaces the hint silently on-screen. The AI case is *easier* than the human case — no risk of talking over the customer. |
| 8 | Barge execution | **Seamless takeover / "participant swap":** human joins the room and the AI leg is muted/demoted; OR the AI does a **micro-handoff line** ("let me bring in a colleague") and the human inherits. WebRTC participant injection makes this an architecture-native operation, not a re-architecture. ([LiveKit human takeover](https://livekit.com/blog/handoff-pattern-voice-agents)) |
| 9 | State inheritance | **Live shared session state**: the human takeover console renders the AI's working memory — verified-identity status, slot values, half-completed action (e.g. "transfer ₹50k staged, not yet committed"), tool-call log. Takeover continues from exact state; **warm transfer with full context summary is the gold standard and dramatically outperforms cold transfers**. ([BlueTweak AI-to-human handoff](https://bluetweak.com/blog/ai-to-human-handoff/)) |
| 10 | Mid-call wrong-action catch | **Pre-commit action gate visible to supervisor:** high-risk actions (covered in b07) are *staged* and the supervisor console shows pending actions; supervisor can *veto/redirect before commit*. The whisper-directive can also pre-empt: "STOP — wrong account." |
| 11 | Multi-session switching | The console *holds the state for the human* — each session's situation card persists, so context-switching cost is paid by the system (always-fresh summaries), not the human's memory. This is what lifts the ratio from 1:5 to 1:18+. |
| 12 | Handback / disposition | **Whisper:** AI continues, intervention logged. **Barge:** human closes, disposition + intervention-reason captured. Both auto-tagged. |
| 13 | Coaching note → flywheel | Every intervention (whisper text, barge reason, outcome) is a labelled training signal piped into the **b09 eval/tuning flywheel** — the live rail is also the *best* source of "here's exactly where the AI was about to fail" data. |
| 14 | Don't over/under-intervene | **Adaptive alert thresholds + suppression:** the triage ranker is *tuned* so the supervisor isn't flooded (the muted-in-a-week failure). Intervention-rate is itself a monitored metric. ([5-suggestions/min gets muted](https://www.thequantumleap.business/blog/call-coaching-ai-news-roundup-q2-2026)) |

**Reference architectural pattern (2026):** the AI agent runs as a participant in a **WebRTC room** (LiveKit/Pipecat) or a **CPaaS conference leg** (Exotel/Ozonetel/ClearTouch). A **supervisor-orchestration service** (a) subscribes to *all* live rooms read-only, (b) runs per-session **triage/urgency scorers** + a rolling **situation-card summariser**, (c) renders a **live-floor console** that ranks sessions by intervention-need, and (d) exposes three primitives: **inject-directive (whisper)**, **veto-pending-action**, and **participant-takeover (barge)**. Optionally a **supervisor-AI** ("AI overseeing AI" — second agent watching the first) handles the routine tier of interventions and only escalates the residue to the human, pushing the ratio higher still. ([SiliconANGLE AI-to-oversee-AI](https://siliconangle.com/2026/01/18/human-loop-hit-wall-time-ai-oversee-ai/); [LiveKit second supervisor agent](https://livekit.com/blog/handoff-pattern-voice-agents))

---

## 3. Tooling (concrete 2026 stack)

**Real-time media / participant fabric**
- **LiveKit Agents 1.5.x** (Python, April-2026; adaptive interruption handling, native MCP) or **Pipecat v1.0** (April-2026) — agent-as-participant model; human/supervisor injection into the same room; SIP bridge for telephony. ([LiveKit agents](https://github.com/livekit/agents); [Pipecat 1.0](https://www.forasoft.com/blog/article/livekit-ai-agents-guide))
- **CPaaS listen-whisper-barge** as the India-native fallback/parallel path: **Exotel**, **Ozonetel CloudAgent**, **ClearTouch** — all ship supervisor monitor/whisper/barge for Indian numbers + DLT/TRAI plumbing. ([Exotel call whisper](https://docs.exotel.com/contact-center/call-whisper); [Ozonetel whisper & barge](https://ozonetel.com/contact-center-software-solution/); [ClearTouch](https://www.cleartouch.in/blog/call-center-software-features-monitor-whisper-barge/))

**Supervisor console / agent-assist layer**
- **Real-time agent-assist platforms** for the suggestion/whisper UX bar: **Cresta**, **Balto**, **Level AI**, **Capacity** — sub-400ms suggestion lag, 30+ languages, on-device PII redaction are now table-stakes. ([thelevel.ai](https://thelevel.ai/blog/real-time-agent-assist/); [Cresta/sub-400ms](https://www.thequantumleap.business/blog/call-coaching-ai-news-roundup-q2-2026))
- **Live-floor dashboard** (custom): session tiles + signal badges; built on the observability layer (b12) + AgentOps/Langfuse-class agent telemetry. ([AgentOps/Langfuse](https://aimultiple.com/agentic-monitoring))

**Triage / situation intelligence**
- **Per-session urgency ranker** — small model over live signals (sentiment slope, confidence, dead-air gap-01, risk-flags, loop-detection).
- **Rolling situation-card summariser** — streaming LLM summary, refreshed every few turns (cheap model, cached prefix).
- **Supervisor-AI ("AI overseeing AI")** — a second agent (LangGraph supervisor node) that auto-handles routine interventions, escalates residue. ([SiliconANGLE](https://siliconangle.com/2026/01/18/human-loop-hit-wall-time-ai-oversee-ai/); [LangChain HITL](https://docs.langchain.com/oss/python/langchain/human-in-the-loop))

**Intervention primitives**
- **Inject-directive** — high-priority system-message injection into the AI's next turn (orchestrator API).
- **Veto-pending-action** — hooks into the b07 staged-action gate.
- **Participant-takeover** — WebRTC participant swap / CPaaS barge.

**Governance**
- **DPDP-aware access control + intervention audit log** — every monitor/whisper/barge event logged with supervisor identity, session, timestamp, reason (live audio/transcript is personal data; third-listener access must be controlled + auditable).

**Eval / red-team**
- Triage-precision eval (did the ranker surface the session that actually needed help?), takeover-continuity eval (no state loss / no re-ask), whisper-obedience eval (AI deterministically follows directive), alert-fatigue metric (interventions/hour vs muted-rate).

---

## 4. Benchmarks (real numbers)

- **Supervisor span-of-control is widening fast:** hybrid programs moved **1:12 (2024) → 1:18 (2026)**, projected **1:25–1:30 in mature 2027 programs**. The whole point of this rail is to enable that ratio. [sourced — [thequantumleap Q2-2026](https://www.thequantumleap.business/blog/call-coaching-ai-news-roundup-q2-2026)]
- **Real-time agent-assist table-stakes (2026):** **sub-400ms suggestion lag, 30+ languages, on-device PII redaction** are now baseline for enterprise live-coaching deployments. [sourced — [thequantumleap](https://www.thequantumleap.business/blog/call-coaching-ai-news-roundup-q2-2026)]
- **Alert fatigue is the documented failure:** vendors found an in-call assistant surfacing **~5 suggestions/minute gets muted within a week** — the question shifted from "does it have real-time?" to "is it good enough that reps actually use it?" [sourced — [thequantumleap roundup](https://www.thequantumleap.business/blog/call-coaching-ai-news-roundup-q2-2026)]
- **Confidence-threshold escalation bands (well-tuned 2026 deployments):** >85% → AI proceeds autonomously; 70–85% → flag for post-call review; **<70% → hand off / intervene in real time.** These same bands drive when the supervisor rail should auto-surface a session. [sourced — [BlueTweak handoff](https://bluetweak.com/blog/ai-to-human-handoff/); [buildmvpfast confidence thresholds](https://www.buildmvpfast.com/blog/agent-handoff-patterns-ai-human-escalation-confidence-threshold-2026)]
- **Warm > cold, decisively:** warm transfer with full conversation summary "dramatically outperforms" cold transfer — the takeover-continuity requirement is the empirical winner. [sourced — [BlueTweak](https://bluetweak.com/blog/ai-to-human-handoff/)]
- **Architecture-native takeover exists:** WebRTC frameworks (LiveKit) state the agent "is just another participant, so you can drop a human into the same room to take over… or run a second supervisor agent that watches the first — without changing your architecture." [sourced — [LiveKit handoff](https://livekit.com/blog/handoff-pattern-voice-agents)]
- **Production failure when confidence-aware escalation is ABSENT:** the 2026 airline-agent case — real-time updates exceeded the agent's ability to hold coherent state; rather than escalating on confidence drop, it kept making bookings with degraded awareness. The lesson: high-stakes agents need confidence-aware *proactive* handoff. [sourced — [buildmvpfast confidence-aware escalation](https://www.buildmvpfast.com/blog/agent-handoff-patterns-ai-human-escalation-confidence-threshold-2026)]
- **Control-model shift is real:** 2026 explicitly moving HITL → **human-on-the-loop** (one human supervises many, intervenes on exception) and even **AI-to-oversee-AI** for the routine tier. [sourced — [The New Stack](https://thenewstack.io/human-on-the-loop-the-new-ai-control-model-that-actually-works/); [SiliconANGLE](https://siliconangle.com/2026/01/18/human-loop-hit-wall-time-ai-oversee-ai/)]
- **India CPaaS coverage:** Exotel / Ozonetel / ClearTouch all ship supervisor listen-whisper-barge for Indian deployments today. [sourced — [Exotel](https://docs.exotel.com/contact-center/call-whisper); [Ozonetel](https://ozonetel.com/contact-center-software-solution/); [ClearTouch](https://www.cleartouch.in/blog/call-center-software-features-monitor-whisper-barge/)]
- **Triage-ranker precision / situation-card faithfulness / takeover-continuity on Indic-Hinglish live sessions:** no public benchmark. [estimate — needs in-house eval set]

---

## 5. Failure modes

1. **The attention bottleneck (cardinal failure):** at 1:18–1:30, the human physically cannot watch everything; if the triage ranker is even modestly miscalibrated, the *one* session that needed intervention is the one buried at rank #9 while the supervisor babysits a false alarm. The whole capability lives or dies on triage precision, not on the takeover mechanics.
2. **The AI doesn't know it's failing → it never raises its hand.** Confidence is often *miscalibrated high* exactly when reasoning has degraded (the airline case). A purely AI-triggered escalation misses these; the supervisor rail's value is precisely catching sessions the AI *thinks* are fine. If the ranker also relies only on the AI's self-reported confidence, the gap persists.
3. **Takeover state loss / customer re-ask:** human barges in but the console didn't surface verified-identity / half-staged action / promises made → customer forced to re-explain, or a duplicate action fires (re-transfer the ₹50k). Cold-takeover masquerading as warm.
4. **Whisper-directive disobedience or collision:** AI ignores or partially follows the injected directive, or the injection lands mid-turn and produces an incoherent utterance. The "whisper" must be a *clean, deterministic, turn-boundary* override, not a soft suggestion the model may weigh against its own plan.
5. **Alert fatigue → muted supervisor:** over-firing interventions (the 5/min trap) trains the human to ignore the console — so when the real one fires, it's dismissed. Under-tuned thresholds are as dangerous as no rail at all.
6. **Latency on barge-in:** by the time the human context-loads and joins, the harmful sentence is already spoken / the action already committed. The window for live intervention is seconds; staged-action gating (b07) is what buys the time.
7. **Silent-listener compliance gap:** a human (or supervisor-AI) joining/listening to a live call may itself require disclosure under recording/monitoring norms (interacts with gap-03); DPDP requires the third-listener access be lawful, access-controlled, and logged. Easy to bolt on the console and forget the consent posture.
8. **Supervisor-AI overstepping:** the "AI overseeing AI" tier silently auto-intervenes (whisper/veto) on cases it shouldn't, with no human in the loop — re-introducing autonomy risk under the banner of oversight.
9. **Coaching feedback never closes the loop:** interventions are logged but not piped into b09 tuning → the AI keeps failing in the same spot, supervisor keeps barging on the identical pattern forever (treating the symptom, never fixing the agent).
10. **Privacy/role creep:** the live-floor console becomes a surveillance tool over human agents in hybrid floors, or exposes more PII to supervisors than needed — DPDP + labour-monitoring exposure.

---

## 6. Gap to full adaptation (what the system still can't do as well as a human, and the path to close it)

**What humans still do better:**
- **Attention under genuine ambiguity:** a seasoned floor supervisor *feels* when a call is about to turn even when no single metric has crossed a threshold — a gestalt read of pace, word choice, and silence. Triage rankers approximate this with engineered signals but miss the long-tail "something's off" that an experienced human catches pre-symptomatically.
- **Graceful, face-saving barge-in:** a human takes over a call in a way that doesn't humiliate the (human) agent or alarm the customer — relational finesse. The agentic micro-handoff line is functional but socially flat.
- **Holding rich partial state across many sessions** *with judgment about which thread matters* — humans compress and prioritise context in ways still hard to fully externalise.

**Why the agentic version is *also already superhuman on one axis*:** no human can meaningfully watch 25–30 truly-concurrent conversations; the system *can* pre-attend all of them and surface the right one. So this is not "AI lagging human" — it's a **different shape of capability**: the human is better per-session, the system is better at coverage. Full adaptation = the system's triage gets good enough that the *coverage* advantage isn't paid for in *missed per-session nuance*.

**Concrete path to close the gap:**
1. **Don't trust AI self-confidence for triage.** Build the urgency ranker on *external observable signals* (customer sentiment slope, dead-air, contradiction/loop detection, action-risk, value-of-account) so it catches the sessions the AI *wrongly thinks* are fine. Calibrate against logged real interventions.
2. **Pre-compute the situation card for every live session, always.** The context-load latency is the span-of-control killer; paying it in advance (cheap streaming summariser) is what lets a human intervene in <10s.
3. **Make whisper a deterministic override, not a suggestion.** Inject directives as hard, turn-boundary, obeyed instructions; eval whisper-obedience to near-100%.
4. **Stage high-risk actions (b07) so the intervention window exists at all.** Live barge only matters if the harmful action hasn't committed yet — the gate buys the seconds.
5. **Tier with a supervisor-AI but keep humans on the residual + a hard audit trail.** Let AI-over-AI handle routine nudges; route the ambiguous/high-stakes to the human; log everything for DPDP + the b09 flywheel.
6. **Close the loop into tuning.** Every barge/whisper is a labelled "AI-about-to-fail" example — the single richest training signal the deployment produces. Pipe it to b09.

---

## 7. HITL trigger (when a human MUST own this rail)

This step *is* the HITL rail, so the trigger is about **when the human (not the supervisor-AI) must be the one intervening:**

- **Always-available, but human-mandatory when:** (a) the action about to commit is irreversible + high-value (money movement, account closure, legal commitment) and the AI's confidence is degraded; (b) a compliance line is about to be crossed (mis-selling, prohibited collection pressure, vulnerable-customer harm — gap-04); (c) the customer explicitly demands a human; (d) the triage ranker flags **<70% confidence / sentiment-collapse / loop-detected** on a session the AI hasn't self-escalated; (e) any case the supervisor-AI is uncertain about (residual tier).
- **Supervisor-AI may auto-handle (human-on-loop, not in-loop):** routine low-stakes nudges (whisper a known-good script correction) on reversible actions, with full logging and a sampled human review (b09).
- **Hard rule:** the supervisor-AI may **never auto-execute a barge that takes over a money-movement / irreversible-action session** without a human — that collapses the oversight back into autonomy.

---

## 8. Automation readiness: **5 / 10**

**Why mid-scale, not high:** The *mechanics* are essentially solved and shipping in 2026 — WebRTC participant injection (LiveKit/Pipecat) and CPaaS listen-whisper-barge (Exotel/Ozonetel/ClearTouch) make monitor/whisper/barge architecture-native; real-time agent-assist (Cresta/Balto/Level AI) delivers sub-400ms in-call guidance; state-carrying warm takeover is a known pattern. So the *plumbing* is an 8.

But the **capability that actually matters — the triage/attention layer that lets one human reliably supervise 18–30 concurrent AI sessions and catch the session the AI doesn't know is failing — is immature.** It depends on a well-calibrated urgency ranker (no public Indic benchmark), pre-computed situation cards, and disciplined alert-tuning to avoid the documented muted-in-a-week fatigue. And the human judgment at the moment of intervention (coach-vs-barge, graceful seizure) is still ahead of the machine. The supervisor-AI ("AI over AI") tier is promising but unproven for high-stakes, irreversible-action sessions, where a human MUST remain. Net: the rail is buildable and partially shippable now, but "fully replace the human supervisor" is not — hence **5/10**, gated by triage precision and the irreducible human-on-irreversible-actions requirement.

---

## 9. Build spec (concrete)

**What to implement (MVP → v2):**
1. **Run the AI agent as a room participant** (LiveKit Agents 1.5.x). This makes monitor/whisper/barge architecture-native and is the single most important upfront decision.
2. **Read-only supervisor subscription** to all active rooms → a **live-floor console** (session tiles, signal badges).
3. **Rolling situation-card summariser** per session (cheap streaming model, cached-prefix, refresh every N turns) — *always pre-computed*.
4. **Urgency/triage ranker** over *external* signals (sentiment slope, dead-air [gap-01], confidence, loop/contradiction detection, action-risk [b07], account value) → ranks the supervisor's queue, surfaces top-1 with a reason chip.
5. **Three intervention primitives:** `inject_directive(session, text)` (deterministic turn-boundary override / whisper), `veto_pending_action(session, action_id)` (hooks b07 staged-action gate), `takeover(session, supervisor)` (participant swap with state-card inheritance).
6. **DPDP intervention audit log** — supervisor id, session, mode, reason, timestamp; access-controlled live-stream subscription.
7. **(v2) Supervisor-AI tier** — LangGraph supervisor node auto-handling routine low-stakes whispers; escalates residual + all irreversible-action cases to the human.
8. **Loop-back into b09** — every intervention → labelled training/eval example.

**Data needed:** labelled corpus of *real interventions* (which live session needed help + why + what the supervisor did) to train/calibrate the triage ranker; Indic-Hinglish live-session transcripts with sentiment/risk annotations; a held-out set of "AI thought it was fine but was failing" sessions (the hardest, highest-value class).

**Eval metric that gates it (must pass before relying on it for trust):**
- **Triage precision@1 / recall on the "needed-intervention" set** ≥ target (this is THE gate — a missed critical session is the failure).
- **Takeover-continuity rate** = % of barges with zero state loss / zero customer re-ask / zero duplicate action ≈ 100%.
- **Whisper-obedience** = % of directives the AI follows exactly, near-100%.
- **Alert-rate / muted-rate** kept below the fatigue threshold (well under the 5/min trap).
- **Time-to-intervene** (flag → human acting) < ~10s median, which requires the pre-computed situation card.

---

## 10. India specifics

- **CPaaS path is India-ready today:** Exotel, Ozonetel CloudAgent, and ClearTouch all ship supervisor **listen-whisper-barge** on Indian numbers with DLT/TRAI plumbing — so a mid-market Indian BPO can get the *telephony* side of this rail off the shelf and bolt the AI-triage/console layer on top, rather than building media infra from scratch. ([Exotel call whisper](https://docs.exotel.com/contact-center/call-whisper); [Ozonetel](https://ozonetel.com/contact-center-software-solution/); [ClearTouch](https://www.cleartouch.in/blog/call-center-software-features-monitor-whisper-barge/))
- **DPDP on the live stream + third listener:** the live transcript/audio is personal data; a supervisor (or supervisor-AI) joining/listening must be **access-controlled, purpose-bound, and logged**. A *human* silently joining a recorded call may interact with the recording/monitoring-disclosure obligations covered in **gap-03** — confirm whether the customer must be told a human is now monitoring/has joined.
- **Hinglish + regional code-mix breaks the triage models, not just the conversation model.** The urgency ranker and situation-card summariser must themselves handle Hindi + regional + Hinglish sentiment/risk — a sentiment-slope model trained on English will *under-fire* on a Hinglish call that's actually melting down. This is the same Indic-NLP gap as A06/gap-04, now applied to the *supervision* layer.
- **Span-of-control economics are the India business case.** India mid-market BPOs run on thin margins; the entire ROI of an action-taking AI deck is "one senior supervisor safely covers 18–30 AI sessions instead of a 1:8 human floor." The triage/console layer is therefore not a nice-to-have — it *is* the unit economics. Under-investing in triage (and over-relying on raw barge mechanics) silently caps the achievable ratio and kills the business case.
- **Bilingual supervisor scarcity:** the human in the loop must be able to *take over* in the customer's language. A supervisor pool that can barge in Hindi+English but not Tamil/Telugu/Bengali constrains which sessions can be human-rescued — language-aware routing of *interventions* (not just calls) is an India-specific console requirement.

---

*Draft research note for review. Cited where possible; [estimate]/[UNSOURCED] elsewhere. Not investment advice.*
