# B10 — Telephony / CPaaS & Omnichannel Integration
## (SIP/CTI Transfer, WhatsApp BSP, Channel Unify)

**Step type:** Infrastructure + integration layer  
**Applies to:** India-market, multilingual (Hindi + regional + Hinglish), RBI/IRDAI/DPDP-compliant, action-taking voice+chat BPO contact-center agent  
**Research date:** June 2026  
**Research depth:** SOTA 2026 — sourced from Caller Digital, RTC League, Voiso Medium, Caller Digital Regulatory Map, and primary vendor documentation

---

## 0. Why This Step Is Load-Bearing

Every other BPO micro-step — NLP, intent detection, CRM writes, empathy — dies in production if the telephony and channel integration layer is broken or slow. This is the plumbing. An agent that can't pick up a SIP call, can't transfer to a human with context, can't reply on WhatsApp while the call is live, and can't unify channel history is not a BPO agent — it is a chat toy.

The agent's entire identity in the customer's experience is defined here. Latency >800ms end-to-end sounds like a broken line. A dropped SIP REFER during transfer is an angry escalation. A WhatsApp message landing 4 minutes after the voice call with no context is a compliance breach in some sectors and always a retention event.

---

## 1. Human Micro-Steps — Atomic Sub-Skills Decomposed

What a skilled human BPO agent actually does in the telephony/channel layer, broken into the smallest observable cognitive + mechanical + emotional moves:

### 1A. Call Arrival / Channel Detection
1. Recognizes the channel the contact is arriving on (inbound voice DID, click-to-call web widget, WhatsApp message, email, chat widget, outbound predictive dialer preview)
2. Reads the screen pop surfaced by CTI — ANI/DNIS, queue name, IVR path taken, language preference, prior contact history
3. Mentally anchors on the customer identity before speaking (avoids "who am I talking to?" cold start)
4. Adjusts tone register in the first second based on channel (voice = warm greeting; WhatsApp = shorter, typed-informal-professional)

### 1B. IVR / DTMF Navigation (for outbound or relay scenarios)
5. When calling third-party (insurance hotline, bank, utility) on behalf of the customer, manually navigates their IVR via DTMF key presses ("press 1 for English, press 3 for claims")
6. Holds position in third-party IVR queues without losing the customer call
7. Recognizes when an IVR requires voice input vs. key-press and switches modality

### 1C. Session Establishment and Audio Quality Check
8. Confirms codec handshake is producing intelligible audio (G.711 vs. G.729 trade-offs — agents learn by ear when compression is too heavy)
9. Identifies and compensates for echo, jitter, or clipping within the first 3-5 seconds ("mujhe aap ki awaaz thodi door se aa rahi hai, ek second...")
10. Selects headset input/output profile or switches to speaker if desktop phone rings instead

### 1D. Simultaneous Multi-Channel Management (the "concurrent conversation" skill)
11. While on a voice call, monitors the chat queue tile (WhatsApp/web chat bubble) for incoming messages on the same customer's account
12. Mentally time-slices: responds to WhatsApp "ACK" messages ("haan, main dekh raha hoon") while listening to the caller, without letting the caller sense the split attention
13. Flags channel collision — same customer opens chat mid-call — and decides whether to merge context or defer the chat

### 1E. Attended SIP Transfer Execution (most cognitively demanding)
14. Decides: blind transfer (just send the call) vs. attended transfer (brief the receiving agent before connecting customer)
15. For attended transfer: puts customer on hold, initiates a consult call to the destination agent/queue, delivers a whisper brief ("female caller, account 8842, wants EMI waiver, has been on 3 calls this week, escalated") in under 15 seconds
16. Transfers the customer call to the destination leg (via SIP REFER or platform UI transfer button), waits for the destination to accept
17. Drops out of the 3-party bridge after confirmation, logs transfer reason in CRM
18. For warm/attended transfer of escalation: optionally stays on the 3-way bridge for 30-60 seconds to smooth the handoff ("Mrs. Sharma, I'm connecting you to my senior colleague Rahul who will take care of this")

### 1F. Context Packaging for Transfer / Escalation
19. Before transferring, writes a 2-3 line transfer note in the CRM ticketing system (reason, customer mood, what was tried, next step expected)
20. Decides what NOT to include (PII redaction for chat logs forwarded to third-party queues)
21. Selects the correct destination queue (skill-based routing judgment: "this is a technical complaint for BFSI queue, not general support")

### 1G. WhatsApp BSP Mechanics
22. Sends and receives WhatsApp messages through the unified agent desktop (embedded in CRM or CCaaS agent UI — not through a separate WhatsApp Web tab)
23. Selects the correct message template for regulated communications (HSM templates approved by Meta — cannot send free-text in 24-hour window expiry scenarios)
24. Sends rich media (PDF, invoice image, payment link) via WhatsApp when the customer needs documentation
25. Recognizes when the 24-hour WhatsApp session window is about to expire and either gets the customer to reply within it or switches to a template-based re-entry

### 1H. Channel Switch Decision
26. Proactively offers channel downgrade/upgrade ("main aapko WhatsApp par ek link bhejta hoon" while on voice) when:
    - Voice quality is poor
    - A document needs to be shared
    - Customer is in a public space and can't speak freely
    - The issue needs a written trail (disputes, escalations)
27. When a voice call ends, sends a WhatsApp follow-up with summary or action items ("Aapki complaint register ho gayi, reference number hai: XYZ123")
28. Receives an inbound WhatsApp from a customer mid-shift and determines: can I resolve this async, or do I need to initiate a call?

### 1I. Post-Call Channel Hygiene
29. Confirms the call recording started correctly (platform indicator light / recording status icon)
30. Verifies the channel is properly closed (call disconnected, chat session ended, ticket updated) to prevent ghost sessions consuming concurrency slots
31. If using a softphone, manually notches "After Call Work (ACW)" status to prevent new calls arriving during wrap-up

---

## 2. Agent Approach — How a 2026 AI Agent Performs Each Sub-Step

| Human micro-step | AI approach | Technique / Model |
|---|---|---|
| 1A: Channel detection + screen pop read | SIP INVITE header parsing → ANI/DNIS lookup → CRM API call → context injection into LLM system prompt | Deterministic SIP parsing + REST CRM lookup; result stuffed as `<customer_context>` block with cache_control on stable prefix |
| 1A: Tone register adjustment | Channel tag in system prompt ("channel: whatsapp → brevity mode; channel: voice → warm greeting TTS") | Prompt-level instruction; no model change needed |
| 1B: DTMF navigation of third-party IVR | Telnyx AI Assistant DTMF tool / VAPI `dtmf` action / Pipecat `DTMFTool` | Rule-based IVR navigator with fallback NLU for "say your account number" prompts |
| 1C: Audio quality detection | Real-time audio analytics on RTP stream (MOS score monitoring); automatic codec renegotiation via SIP re-INVITE | Opus codec preferred; Ozonetel/Exotel stream API for MOS; alert if MOS < 3.5 → suggest channel switch |
| 1D: Concurrent multi-channel | Event-driven architecture — each channel publishes to a shared customer event bus; AI agent subscribes and maintains a merged context object | LangGraph multi-node state machine; each channel = node; shared `CustomerState` pydantic object |
| 1E: Transfer type decision | Rule-based classifier: escalation_reason + sentiment_score → attended vs. blind; if sentiment == "angry" or escalation_tier >= 2 → attended | Small classifier (Haiku 4.x) with prompt: "should this be attended or blind transfer? reason: {}" |
| 1E: Attended transfer whisper brief | Auto-generated 3-sentence whisper: customer_name, issue_summary, emotional_state, actions_taken | Structured output (Pydantic schema: WhisperBrief) generated by Sonnet; injected as SIP REFER header or pre-call TTS to destination agent |
| 1E: SIP REFER execution | SIP REFER (RFC 3515) via FreeSWITCH / LiveKit SIP / Twilio <Refer> / Exotel transfer API | Platform-specific but standard; deterministic |
| 1F: Transfer note | Auto-generated structured handoff note synced to CRM via API post-transfer | DSPy Signature `TransferNote(conversation_history, sentiment, resolution_status) -> handoff_note: str` |
| 1G: WhatsApp HSM template selection | Intent → template classifier → template ID lookup → BSP API send | Template registry in Redis; intent mapped to approved Meta HSM template ID at runtime |
| 1G: 24-hour session window management | State machine tracks `last_customer_message_ts` per conversation; if elapsed > 23h → force template-only mode | Cron check or event-driven; deterministic |
| 1G: Rich media send | Presigned S3 URL → WhatsApp document/image message via BSP REST API | Standard BSP REST (Gupshup / Kaleyra / 360dialog APIs) |
| 1H: Channel switch decision | Intent + channel_quality_signal → routing decision | Rule-based: if MOS < 3.5 or `document_required=True` → send WhatsApp link during call |
| 1H: Post-call WhatsApp follow-up | Auto-generated summary → sent via BSP API 30s after call disconnect event | Template or session-window-aware free text |
| 1I: Recording verification | SIPREC passive listener confirms recording stream; status event consumed by agent orchestrator | SIPREC on Exotel/Ozonetel; event webhook → state update |
| 1I: ACW state management | Automatic `wrap_up` state after call-end event; configurable timer (90-120s); auto-ready after timer | Platform API: `POST /agent/{id}/status {status: "wrap_up"}` |

---

## 3. 2026 Tooling Stack

### Telephony / SIP Layer
- **Exotel** — Indian cloud-telephony incumbent. DLT-compliant. Best for BFSI. SIP media streaming API. DID provisioning 2-5 days. Pricing: ~₹0.80-1.20/min outbound.
- **Ozonetel** — CCaaS-plus-telephony bundle. Predictive dialer + omnichannel layer + CTI. Strongest for enterprise Indian BPOs. G2: 4.6/5 (623 reviews).
- **Plivo** — Developer-API-first. 24-48h DID. Best developer experience for custom AI stacks. Weakest on India DLT vs. Exotel.
- **Direct Airtel/Jio/Tata Comm SIP trunk** — For >20L minutes/month; ~₹0.60-1.20/min. Requires SBC (AudioCodes Mediant, Ribbon, or FreeSWITCH-as-SBC) in DMZ.
- **Twilio** — Global coverage, excellent developer docs, but 2-3x cost of Indian alternatives for India DIDs. Use only if multi-country deployment.

### AI Voice Agent Framework
- **LiveKit Agents** — Open-source real-time voice pipeline. Ships native SIP + phone numbers (2025). Sub-300ms latency. Cost: 60-80% cheaper than managed platforms at >10k min/month.
- **Vapi / Retell AI** — Managed platforms. Faster to ship. $0.05-0.18/min blended. Best below 10k min/month or for rapid prototyping.
- **Pipecat** (Daily.co) — Open-source pipeline for real-time voice. Best for custom codec/transport control.
- **FreeSWITCH** — Open-source media server. Acts as SBC + B2BUA + conference bridge for 3-party attended transfers. Production-grade for high-volume Indian deployments.

### WhatsApp BSP Layer
- **Gupshup** — India's dominant BSP. AI agent layer built-in. Supports WhatsApp + RCS + Voice + SMS unified API. Meta-certified. Pricing: utility ₹~0.115/msg, marketing ₹~0.863/msg (2026 rates).
- **Kaleyra (Tata Communications)** — Enterprise BFSI-focused BSP. 150+ industry-specific templates. Best for banks/NBFCs.
- **Route Mobile** — Listed Indian BSP. Strong for high-volume transactional messaging.
- **360dialog** — Global BSP, popular for developers; thinner India-specific DLT support.
- **ValueFirst** — Multi-channel (WhatsApp + SMS + RCS + Voice + Email) in one API.

### CTI / Omnichannel Orchestration
- **Salesforce Omni-Channel + Einstein CTI** — Best if CRM is SFDC. Unified routing across voice/chat/email/WhatsApp.
- **Freshdesk / Freshcaller** — SMB-friendly; built-in Exotel/Twilio integration; WhatsApp via Freshchat.
- **Ozonetel CloudAgent** — India-native CCaaS with CTI, ACD, quality management, CRM connectors.
- **NICE CXone** — Enterprise omnichannel agent desktop. Expensive but best SIPREC recording + WFM.
- **Custom LangGraph orchestrator** — For AI-native stacks: each channel (voice/WhatsApp/email) = LangGraph node; shared `CustomerState` pydantic model; Redis pub/sub for cross-channel events.

### Media Gateway / SBC
- **AudioCodes Mediant 800/2000** — Hybrid SBC + media gateway. TDM-to-SIP for legacy PBX. Up to 400 concurrent sessions.
- **FreeSWITCH as SBC** — Open-source, battle-tested, used at scale by Indian CCaaS vendors.
- **Ribbon SBC** — Carrier-grade. Used by TATA/Airtel interconnects.

### Observability
- **Langfuse** — LLM call tracing (prompt, output, latency, cost, eval score per call)
- **Ozonetel / Exotel analytics dashboard** — SIP call quality (MOS, jitter, packet loss), concurrency, AHT
- **Grafana + Prometheus** — Custom SIP metrics from FreeSWITCH/LiveKit via ESL event socket

---

## 4. Benchmarks

| Metric | Value | Source/Tag |
|---|---|---|
| End-to-end AI voice response latency (ASR → LLM → TTS) | 580-640ms production average | [sourced — Voiso 2026 Contact Center Stack guide] |
| WebRTC sub-300ms audio delivery threshold | <300ms (LAN); 300-500ms (4G India) | [sourced — RTC League WebRTC vs SIP 2026] |
| SIP hop latency penalty | +20-50ms per hop; mediocre routing adds 150-400ms total | [sourced — Caller Digital India Telephony 2026] |
| Exotel DID provisioning | 2-5 business days | [sourced — Caller Digital comparison] |
| Plivo DID provisioning | 24-48 hours | [sourced — Caller Digital comparison] |
| Ozonetel DID provision (new) | 3-7 business days | [sourced — Caller Digital comparison] |
| India outbound per-minute (aggregator) | ₹0.80-1.80/min | [sourced — Caller Digital pricing table] |
| India outbound per-minute (direct SIP) | ₹0.60-1.20/min | [sourced — Caller Digital pricing table] |
| India inbound toll-free | ₹1.20-2.50/min | [sourced — Caller Digital pricing table] |
| WhatsApp utility message cost (India, 2026) | ₹~0.115/msg | [sourced — whautomate pricing India 2026] |
| WhatsApp marketing message cost (India, 2026) | ₹~0.863/msg | [sourced — whautomate pricing India 2026] |
| AI-assisted contact center ROI | $3.50 return per $1 invested; top performers 8x | [sourced — Caller Digital Voice AI benchmarks] |
| WhatsApp AI agent self-resolution rate | 76-92% of interactions | [sourced — egrow WhatsApp AI 2026 guide] |
| WhatsApp AI response time | <3 seconds | [sourced — egrow WhatsApp AI 2026 guide] |
| Cost per interaction: AI vs. human agent | ~12x cheaper for AI | [sourced — egrow WhatsApp AI 2026 guide] |
| SIP REFER attended transfer whisper generation | <500ms target for whisper brief (Haiku 4.x) | [estimate — based on Haiku p50 latency ~300ms] |
| IRDAI call recording retention minimum | 6 months | [sourced — Caller Digital regulatory map 2026] |
| RBI collection call recording retention | 90 days minimum; 12+ months best practice | [sourced — Caller Digital regulatory map 2026] |
| Ozonetel G2 rating | 4.6/5 (623 reviews) | [sourced — Caller Digital comparison] |
| LiveKit vs managed platform cost (>10k min/month) | 60-80% cheaper | [sourced — Forasoft LiveKit guide 2026] |
| Voice AI blended per-minute (managed platforms) | $0.05-0.18 | [sourced — Softcery voice agent platform comparison 2026] |

---

## 5. Failure Modes

### 5.1 SIP / Telephony Layer Failures
- **Codec mismatch on SIP re-INVITE during transfer**: attended transfer triggers SDP re-negotiation; if destination agent's softphone only supports G.729 but the AI was streaming G.711, the media path breaks silently — customer hears silence.
- **SIP REFER race condition**: REFER sent before destination picks up → 202 Accepted but call leg never connects; customer experiences a dropped call.
- **DID not provisioned for DLT outbound category**: outbound AI call using a DID not registered for "transactional" class gets flagged/blocked by DLT. Call silently fails or is filtered by TRAI-compliant carriers.
- **SBC hairpin loop**: FreeSWITCH misconfiguration routes the call back to itself on transfer; the call appears to connect but both parties hear each other's echo.
- **Media gateway codec transcoding latency**: G.711 → G.729 → Opus chain adds 40-80ms per hop; if AI pipeline already burns 600ms, the total round-trip exceeds conversational tolerance (~700ms).
- **Jitter buffer overflow on India 4G**: India mobile networks have higher packet-loss variability; RTP jitter buffer tuned for international networks causes audio artifacts; agents trained on US calls miscalibrate.

### 5.2 WhatsApp BSP Failures
- **24-hour session window expiry mid-conversation**: AI sends free-text reply to a customer who last messaged 24h 2min ago → WhatsApp API returns 131047 error; AI silently fails to deliver; customer thinks they're being ignored.
- **HSM template not pre-approved for the use case**: AI tries to initiate proactive contact (e.g., "your claim is processed") using a template that hasn't cleared Meta's approval queue; message blocked; no fallback configured.
- **BSP rate limit during traffic spikes**: during flash sale or disaster event (insurance claims surge post-cyclone), BSP throughput caps hit; messages queue; SLA breached. Most Indian BSPs cap at 80 messages/second per WABA account by default.
- **Language mismatch in template**: approved HSM template is in English only; customer's preferred language is Tamil → compliance breach if content is regulated (RBI/IRDAI disclosure) + poor CX.

### 5.3 Channel Unification / Context Failures
- **Channel collision without deduplication**: customer sends a WhatsApp message while on a voice call; two separate sessions open in the agent desktop; two AI workers pick it up with divergent context → contradictory responses on the two channels simultaneously.
- **Cross-channel context staleness**: customer changes address on voice call; WhatsApp follow-up bot uses stale CRM record (write-through cache miss); sends old address in confirmation message.
- **CTI screen pop race condition**: CRM lookup triggered on ANI fires after the AI has already generated its greeting → first turn has no customer context; second turn has it → inconsistency visible in transcript.
- **Intent mismatch across channel handoff**: voice intent classifier labels the call "payment dispute" → WhatsApp bot assumes same intent without re-classification → customer had actually asked something new on WhatsApp; bot forces unwanted payment-dispute flow.

### 5.4 Compliance / Regulatory Failures
- **DND scrub not applied to outbound AI campaign**: automated dialer hits a number on the National DND registry → TRAI violation; ₹5 lakh per incident fine exposure.
- **Identity disclosure missed in first 30 seconds (RBI)**: AI voice agent's greeting is long or the ASR is slow on the customer's opening; 30-second clock ticks without "I am calling on behalf of [entity]" disclosure → RBI violation.
- **Recording not started before customer-consent disclosure**: DPDP requires consent to record; if the consent prompt plays before recording is armed, the consent itself is unrecorded and un-auditable.
- **IRDAI 6-month recording purge**: auto-purge policy deletes call recordings at 90 days without sector override; insurance vertical loses required evidence.

### 5.5 AI-Specific Failure Modes
- **Hallucinated SIP destination**: AI decides to transfer to "claims escalation queue" but generates an incorrect SIP URI that connects to a wrong department or dead number.
- **Attended transfer whisper too long**: LLM-generated whisper brief exceeds the 15-second window before the destination human agent gets impatient and picks up without listening; customer has to repeat everything.
- **Sentiment misread → wrong transfer type**: AI classifies "frustrated but cooperative" customer as "angry" → routes to senior escalation queue unnecessarily; loads tier-2 agents with resolvable tier-1 issues.

---

## 6. Gap to Full Adaptation — What the Agent Still Cannot Do as Well as a Human

### Gap 1: Dynamic IVR Navigation at Unfamiliar Third-Party Systems
**Current gap:** Humans learn to navigate novel IVR trees by listening, inferring structure, and trying options. AI agents need a pre-built IVR map or must use ASR+NLU on the audio stream to detect option prompts in real time — but this breaks when IVR audio quality is poor or uses non-standard flows (e.g., "say your 10-digit account number" in accented Hindi).

**Path to close:** LiveKit + Pipecat `DTMFTool` + a dedicated IVR-audio NLU model (fine-tuned Whisper for Indian-accented telephony audio); maintain a shared IVR-tree knowledge base per major third-party (banks, insurers, utilities) as JSON navigator trees, updated weekly.

### Gap 2: Audio Quality Perception and Real-Time Codec Negotiation
**Current gap:** Humans immediately notice echo or clipping and ask the customer to move to a better spot or switch to a different number. AI MOS monitors are reactive, not proactive — they detect degradation after it has already impacted the conversation.

**Path to close:** Real-time MOS scoring on the RTP stream (every 5 seconds); LLM-accessible tool `get_call_quality()` → if MOS < 3.5, trigger automatic proactive channel-switch suggestion. Exotel and Ozonetel expose WebSocket stream events for this; LiveKit has built-in audio quality metrics.

### Gap 3: Attended Transfer Whisper Quality
**Current gap:** A skilled human whisper brief is perfectly calibrated — not too long, uses the destination agent's vocabulary, highlights the one thing that matters most. LLM-generated whispers are often 2-3x too long, include irrelevant context, or miss the critical frame ("she's been waiting 40 minutes" is the most important fact; the LLM buries it third).

**Path to close:** Fine-tune (or DSPy-compile) a WhisperBrief generator on a golden set of human-agent whispers tagged with "which fact mattered most" labels. Eval metric: destination agent survey ("did the whisper brief help you? rate 1-5"). Target: 4.2/5 within 3 months.

### Gap 4: Cross-Channel Identity Resolution
**Current gap:** When the same customer contacts via voice (caller ID), WhatsApp (+91 number), and web chat (logged-in session) simultaneously or sequentially, a human agent immediately links them by name/voice/context. The AI requires all three to map to the same CRM contact — which breaks when the WhatsApp number differs from the registered mobile (common in India: SIM-swaps, family phones, dual-SIM).

**Path to close:** Probabilistic identity resolution layer: embed customer utterances + WhatsApp display name + interaction time proximity into a vector space; cluster sessions to a single CRM contact with confidence score. Flag low-confidence merges for human review. Use Qdrant or pgvector for identity-resolution index.

### Gap 5: Regulatory Compliance in Real-Time Spoken Disclosures (Hindi/Regional)
**Current gap:** RBI requires identity disclosure within 30 seconds in a form the customer comprehends. AI TTS produces regulatory disclosure text in standard Hindi that regional-dialect customers may not fully process ("aap ki yeh call record ki ja rahi hai" may not land clearly for a Bhojpuri-dominant customer). Humans adapt the phrasing.

**Path to close:** Per-state, per-dialect disclosure script library; AI dialect classifier (detect customer's likely regional dialect from first 2-3 seconds of speech); serve the matching disclosure template. Build eval: human listener panel rates comprehension across 5 Hindi + 5 regional dialect variants.

---

## 7. HITL (Human-in-the-Loop) Triggers

These are the conditions under which a human MUST take over for this step:

| Trigger | Reason |
|---|---|
| MOS score < 2.5 for >30 seconds AND customer reports audio issues | AI cannot fix physical call-quality problems; human may know to switch the call to a different DID or advise callback |
| SIP REFER fails after 2 retries | Transfer failure recovery requires human judgment on whether to re-queue, escalate, or call back |
| Customer is on a third-party hold >8 minutes (outbound relay) | Context loss risk; customer frustration management requires human presence |
| WhatsApp 24h session expired AND regulated content needed | Cannot use free text; only HSM template allowed; if no approved template exists, human must compose a custom message manually |
| Identity resolution confidence < 0.7 on cross-channel merge | Risk of giving wrong customer's data to the calling party — DPDP breach |
| DND scrub system returns error (not a match/not a non-match, but a system error) | Cannot proceed with outbound call without clean DND status; human operations review required |
| Attended transfer destination queue is unavailable (busy / offline) | AI cannot make the judgment call of whether to queue, try alternate routing, or callback; requires supervisor input |
| Regulatory disclosure not acknowledged by customer after 2 attempts | Cannot proceed under RBI/IRDAI rules; compliance officer review |

---

## 8. Automation Readiness: 6 / 10

**Why not higher:**
- SIP REFER + attended transfer whisper generation has a functional failure rate of ~8-15% in production [estimate] due to race conditions, codec mismatches, and LLM-generated whispers that are too long or miss the key frame.
- India's regulatory layer (DPDP + TRAI DLT + RBI + IRDAI) is still being notified through 2026-2027; rules change quarterly; real-time rule compliance is fragile.
- Cross-channel identity resolution is probabilistic, not deterministic; edge cases are frequent in India (dual-SIM, family phones, SIM swaps).
- WhatsApp BSP 24-hour session window management and HSM template approval process introduce external dependencies that break at inconvenient times.

**Why not lower:**
- The SIP, WebRTC, and BSP APIs are mature, well-documented, and widely deployed in production.
- The deterministic parts (call routing, DTMF, recording, basic transfer) are fully automatable today.
- LiveKit + FreeSWITCH + Exotel combinations are powering production Indian contact centers with millions of monthly minutes today.

---

## 9. Build Spec

### What to Implement

#### Phase 1: Core Telephony Bridge (Ship in 2 weeks)
- **SIP inbound/outbound** via Exotel (for India DLT compliance) or Plivo (for developer speed)
- **LiveKit Agents** voice pipeline: STT (Deepgram Nova-2 / Sarvam AI for Indian accents) → LLM (Sonnet 4.x, prompt-cached) → TTS (ElevenLabs Hindi / Sarvam TTS)
- **ANI lookup on call arrival**: `GET /customer?phone={ANI}` → CRM → inject as cached system-prompt prefix
- **Call recording**: SIPREC passive listener → S3 storage → 90-day default, sector-configurable retention policy
- **DND scrub**: before every outbound dial → TRAI DND API check → proceed or skip with log

#### Phase 2: WhatsApp BSP Integration (Ship in 1 week alongside Phase 1)
- **Gupshup BSP** (or Kaleyra for BFSI clients) REST API wrapper
- **Template registry**: Redis hash `{intent_code} → {template_id, language_code}` — seeded from Meta-approved HSM library
- **Session window tracker**: Redis sorted set `{wa_contact_id} → last_message_ts`; middleware enforces template-only above 23h
- **Rich media sender**: presigned S3 → BSP `/messages` API with document/image type

#### Phase 3: Channel Unification (Ship in week 3-4)
- **LangGraph multi-channel orchestrator**: each channel (voice, WhatsApp, email, web chat) = LangGraph node; shared `CustomerState` Pydantic model
- **Redis pub/sub**: `customer:{id}:events` channel; all nodes subscribe; voice node publishes `{intent, sentiment, actions_taken}`; WhatsApp node consumes before generating next reply
- **CTI screen pop**: on SIP INVITE, async-fire CRM lookup; inject context into LLM state before first TTS word (target: <200ms)

#### Phase 4: Transfer + Handoff (Ship in week 5)
- **Blind transfer**: SIP REFER via LiveKit/Exotel transfer API; log `{transfer_reason, destination_queue, customer_id, transcript_url}` to CRM
- **Attended transfer whisper brief**: DSPy-compiled `WhisperBriefSignature(conversation_summary, key_issue, sentiment, actions_taken) -> whisper: WhisperBrief` — max 3 sentences, prioritized by issue severity
- **3-party bridge** for warm handoff: FreeSWITCH conference room (2-leg → 3-leg → 2-leg) via ESL commands

### Data Needed
- Minimum 500 labeled attended-transfer whisper brief examples (human-agent transcripts + destination agent ratings) to fine-tune/DSPy-compile the WhisperBrief generator
- IVR tree maps for top 20 third-party systems the BPO calls on behalf of customers (banks, insurers, utilities)
- Identity resolution training data: CRM pairs of (caller_ANI, WhatsApp_number, web_chat_session) confirmed to be the same customer — minimum 5,000 confirmed pairs per tenant
- Meta-approved HSM template library per vertical (BFSI, insurance, e-commerce) and per language (Hindi, English, regional top-5)
- Regulatory disclosure scripts per regulator (DPDP/RBI/IRDAI) × language (Hindi + 5 regional) — reviewed by legal

### Eval Metrics (Gate Before Shipping to Production)

| Metric | Target | Measurement Method |
|---|---|---|
| E2E voice response latency (ASR → LLM → TTS → audio out) | P95 < 800ms | LiveKit telemetry, Langfuse trace timestamps |
| SIP transfer success rate (call connected at destination) | > 97% | FreeSWITCH CDR `TRANSFER_SUCCESS` events / total transfers |
| Attended whisper brief quality score | Mean ≥ 4.0/5 | Destination human agent post-transfer survey (sampled 20%) |
| WhatsApp message delivery rate | > 99.5% | BSP delivery webhooks: delivered / sent |
| 24h session window violation rate | 0% | Redis session tracker audit log |
| DND scrub coverage | 100% of outbound dials | Audit log: every dial must have a DND check event with result |
| Regulatory disclosure completion rate (within 30s) | 100% | Post-call transcript analysis: disclosure utterance detected within 30s of call start |
| Cross-channel context merge accuracy | > 90% on confirmed same-customer pairs | Labeled test set of known same-customer cross-channel sessions |
| Channel collision deduplication rate | > 99% | Count of sessions where two AI workers opened simultaneously on same customer |

---

## 10. India Specifics

### Regulatory Layer (5 active regulators for contact centers)

**TRAI DLT (Distributed Ledger Technology)**
- All outbound commercial calls (voice + SMS) must originate from a DLT-registered principal entity with a registered header (sender ID / calling line identity) and pre-registered script template.
- DND scrub is mandatory for non-transactional calls. Transactional calls (customer-initiated in last 24h) bypass DND.
- AI agent must carry the registered template ID in call metadata for auditability.
- Strongest DLT operations in India: Exotel, Knowlarity, Ozonetel. Plivo is weaker on India-specific DLT.

**RBI (Banking + NBFCs + Payments)**
- Collection calls: 8:00 AM - 7:00 PM IST only.
- Identity disclosure within 30 seconds: "[Agent name] calling from [entity] regarding [purpose]; this call is being recorded."
- Recording retention: 90 days minimum; 12+ months best practice; 3+ years for high-value loans.
- Digital Lending Guidelines (2022): lender identity, effective interest rate disclosure required.

**IRDAI (Insurance)**
- Entity + capacity disclosure within seconds of call start.
- Recorded consent required for policy-impacting changes (renewals, rider additions, beneficiary changes).
- Recording retention: 6 months minimum; 3+ years for life insurance grievance defense.
- No mis-selling language on coverage, exclusions, returns, or tax benefits.

**DPDP Act 2023 (Digital Personal Data Protection) + Rules 2025 (notified November 2025)**
- Full compliance expected by 13 May 2027; enforcement beginning.
- Consent required for call recording; consent audit trail must be stored.
- Purpose limitation: data captured for support cannot be used for marketing without fresh consent.
- Right to erasure vs. IRDAI 3-year retention tension → architect a "retain recording, restrict further processing" mode.
- Preferred: sensitive personal data stored in India-region cloud (ap-south-1 / Google Mumbai / Azure Central India).

### Language / Dialect Nuances

- **Hindi** is not monolithic. A customer from Bihar speaks Bhojpuri-inflected Hindi; from Rajasthan, Marwari-inflected; from Maharashtra, Marathi-inflected. STT models trained only on Bollywood Hindi miss ~15-30% of phoneme variations [estimate].
- **Hinglish** (Hindi + English code-switching) is the dominant register for urban, under-45 Indians. "Mera account freeze ho gaya hai" mid-sentence is normal. LLM system prompt must be Hinglish-capable.
- **Regional languages in top-5**: Telugu (Andhra/Telangana), Tamil (TN/Sri Lanka), Kannada (Karnataka), Bengali (WB/Bangladesh), Marathi (Maharashtra). BPO with national reach must route to a matching-language queue or support multilingual TTS/STT.
- **Sarvam AI** (India-built) offers the best Indian multilingual STT + TTS in 2026 for production deployments: supports 10+ Indian languages including Hinglish, regional accents.
- **TRAI DLT templates must be in the language registered at DLT**. If the template is Hindi and you serve a Tamil customer, you either need a separate Tamil template or serve English.

### Infrastructure Nuances

- **DID provisioning delays**: Exotel/Ozonetel take 2-7 business days for new India DIDs due to DoT regulatory requirements. Plan ahead; do not assume instant provisioning as in the US.
- **VoIP regulation**: India permits VoIP for business (non-retail PSTN replacement). Operators must be licensed under UAS/ISP license. Using unlicensed VoIP for outbound to PSTN customers is a DoT violation.
- **4G variability**: India's 4G network (dominant for mobile callers) has significant jitter variance. Jitter buffer tuning for India networks (larger buffers: 60-120ms vs. 20-40ms for fiber-dominant markets) is required for acceptable MOS.
- **Toll-free (1800) vs. local DID**: Toll-free costs are ₹1.20-2.50/min for the business (caller pays nothing). For high-volume inbound service lines, local DIDs at ₹0.40-0.90/min inbound are significantly cheaper but customers incur the charge. BFSI typically mandates toll-free for complaint lines.
- **Data localization**: No hard mandate yet (government retains the power to mandate per DPDP Rules), but TRAI recommends India-region storage for telecom data. Using AWS ap-south-1 (Mumbai) or Azure Central India is the defensible default for 2026.

---

## 11. Architecture Diagram (Text)

```
INBOUND VOICE (PSTN)
       │
  [SIP Trunk: Airtel/Jio/Tata]
       │
  [SBC: FreeSWITCH / AudioCodes Mediant]
       │
  [CPaaS: Exotel/Plivo]
       │
  [LiveKit SIP Gateway]
       │
  [AI Voice Agent Pipeline]
  ├── STT: Sarvam AI / Deepgram Nova-2
  ├── LLM: Anthropic Sonnet 4.x (prompt-cached)
  │       └── Tools: CRM_lookup, transfer_call, send_whatsapp, check_dnd
  └── TTS: Sarvam TTS (Hindi/regional) / ElevenLabs
       │
  [Customer Event Bus: Redis pub/sub]
       │
  ┌────┼────────────────────┐
  │    │                    │
[Voice Node]  [WhatsApp Node]  [Email/Chat Node]
       │             │
  [BSP: Gupshup/Kaleyra]
  [WhatsApp Cloud API]
       │
  [Shared CustomerState: Pydantic / Redis]
       │
  [CRM: Salesforce / Freshdesk / Zoho]
       │
  [Call Recording: SIPREC → S3 ap-south-1]
       │
  [DLT Compliance: DND scrub → TRAI API]
       │
  [Observability: Langfuse + Grafana]
```

---

## 12. References

- [Caller Digital — Telephony for Voice AI India 2026](https://www.caller.digital/blog/telephony-partner-voice-ai-india-plivo-exotel-ozonetel-knowlarity-twilio-2026)
- [Caller Digital — Voice AI India Regulatory Map 2026](https://www.caller.digital/blog/voice-ai-india-regulatory-map-2026)
- [RTC League — WebRTC vs SIP for AI Voice Agents 2026](https://rtcleague.com/blogs/when-to-use-webrtc-and-sip-for-ai-voice-agents)
- [Voiso — 2026 Contact Center Technology Stack](https://medium.com/@voiso/contact-center-technology-stack-e2825b906db3)
- [Pulse.in — Top 10 CPaaS Companies India 2026](https://www.pulse.in/blog/top-10-cpaas-companies-in-india/)
- [Whautomate — WhatsApp Business API Pricing India 2026](https://whautomate.com/whatsapp-business-api-pricing-india)
- [eGrow — WhatsApp AI Agent for E-commerce 2026](https://www.egrow.com/en/blog/whatsapp-ai-agent-for-e-commerce-the-complete-2026-playbook)
- [Gupshup — Autonomous AI Agents WhatsApp](https://www.gupshup.ai/whatsapp-api)
- [Kaleyra (Tata Communications) AI Solutions](https://www.tatacommunications.com/kaleyra/cpaas/kaleyra-ai)
- [Decagon — What is a SIP transfer](https://decagon.ai/glossary/what-is-a-sip-transfer)
- [Forasoft — Build and Deploy LiveKit AI Voice Agents 2026](https://www.forasoft.com/blog/article/livekit-ai-agents-guide)
- [Softcery — 12 Voice Agent Platforms Compared 2026](https://softcery.com/lab/choosing-the-right-voice-agent-platform-in-2026)
- [DPDP Act compliance guide — EY India](https://www.ey.com/en_in/insights/cybersecurity/decoding-the-digital-personal-data-protection-act-2023)
- [Cleartouch — Call Center Audio Recording Compliance India](https://www.cleartouch.in/blog/call-center-audio-recording-legal-requirements-in-india/)
