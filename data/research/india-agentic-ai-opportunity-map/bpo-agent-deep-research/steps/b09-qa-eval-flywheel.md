# B09 — QA / Eval Flywheel
## 100% Call Scoring · Gold-Labeling · Drift Detection · Continuous Tuning

**Step context:** India-market, multilingual (Hindi + regional + Hinglish), RBI/IRDAI/DPDP-compliant, action-taking voice+chat contact-center agent for mid-market BPOs.

**Research date:** 2026-06-24  
**Status:** Production-ready architecture; automation readiness 7/10.

---

## 1. What This Step Actually Is

Traditional BPO QA evaluates 2–5% of calls via random sampling: a human QA analyst listens, fills a scorecard, flags gaps, feeds coaching. The QA flywheel replaces that with a continuous, self-improving loop:

1. **100% scoring** — every call scored automatically the moment it ends
2. **Gold-labeling** — a small fraction gets human expert review to build ground truth
3. **Drift detection** — the scoring model is monitored for performance decay
4. **Continuous tuning** — the model is updated when drift is detected, completing the loop

The loop's output is not just scores — it is a labeled dataset of production calls that trains the next version of the model, which scores more calls, which generates better labels, and so on.

---

## 2. Human Micro-Steps (What a Skilled QA Analyst Actually Does)

These are the atomic cognitive + mechanical moves a senior BPO QA specialist performs:

### 2a. Pre-Scoring Setup
1. Recall the scorecard/rubric for THIS call type (collections vs. insurance vs. support — different rubric weights)
2. Identify the call's business context from metadata: campaign name, agent tier, queue, language declared
3. Check if this agent is on a Performance Improvement Plan (PIP) — changes how borderline scores are flagged
4. Open the call recording + transcript simultaneously; sync them mentally
5. Note call duration vs. norm for this queue (too short = possible early disconnect or cherry-picking)

### 2b. Listening + Scoring
6. Listen for the opening: did the agent give proper identification, entity name, and purpose? (RBI FPC mandatory)
7. Score empathy on a Likert 1–5: tone of voice, pace of speech, acknowledgment phrases ("samajh gaye aapki baat")
8. Check compliance gates — fatal/auto-fail items: use of threatening language, incorrect legal disclosures, recording consent not taken, or any promise beyond authority
9. Track script adherence vs. natural deviation: sometimes deviation is better; QA decides which
10. Score problem resolution: was the issue resolved, transferred correctly, or left pending?
11. Score Hinglish handling: did the agent switch language cleanly when the customer switched? Or did they force English on a Hindi-dominant customer?
12. Score data handling: was PAN/Aadhaar/account number repeated unnecessarily on the call? (DPDP violation risk)
13. Score call close: was a proper summary given, reference number shared, survey consent obtained?

### 2c. Edge-Case Judgment
14. Decide borderline scores: a rubric gives 1–5 but the call is a "3.5" — round up or down based on context
15. Flag anomalies: customer threatened legal action, agent offered unauthorized discount, call was in an unexpected language (Tamil when Hindi was expected)
16. Write coaching notes in plain language the agent can act on: not "score 2 on empathy" but "jab customer ne baar baar kehti thi ki samajh nahi aa raha, toh aap ne script continue ki — rukke nahi"
17. Decide escalation: should this call go to compliance team, legal, or fraud team?
18. Assign call to the right bucket for reporting: CSAT impact, compliance breach, coaching opportunity, best-practice example

### 2d. Gold-Label Calibration (for senior QA / calibration sessions)
19. Pull a stratified sample of auto-scored calls for double-blind human review
20. Compare AI score vs. own score on each rubric dimension
21. Identify systematic disagreements: where is the AI consistently wrong?
22. Write calibration notes: "AI scores empathy too high when customer uses polite language even if issue unresolved"
23. Participate in inter-rater calibration: agree with other QA analysts on borderline cases
24. Update rubric language to close ambiguity identified in calibration
25. Label final gold set: assign authoritative scores that will train/tune the model

### 2e. Drift Detection (QA Lead / ML-aware QA Manager)
26. Monitor weekly score distributions: are avg scores rising suspiciously (grade inflation) or drifting down?
27. Compare AI-human agreement rate this week vs. last month — is kappa falling?
28. Check if any external event happened: new regulatory rule, product change, script update — these create concept drift
29. Decide: recalibrate rubric, recalibrate model, or both?
30. Approve or block coach-dispatch: if AI scores are drifted, hold coaching until recalibration

### 2f. Continuous Tuning Loop
31. Collect disagreements (human override of AI score) as negative examples
32. Collect high-confidence agreements as positive examples
33. Trigger retraining or few-shot re-prompting depending on severity
34. A/B test new model version on held-out gold set before promoting to production
35. Document the change: what drifted, what was changed, what the before/after kappa is

---

## 3. Agent Architecture (How a 2026 AI System Handles Each Sub-Step)

### Layer 0: Transcription + Diarization
- **ASR engine:** Gnani.ai Prisma v2.5 (trained on 14M hours, 12 Indic languages, 15% lower WER on rural Hindi dialects vs. competitors as of June 2026) or Sarvam AI Saarika v2 for pure Hindi queues
- **Diarization:** Pyannote 3.x or Gladia Solaria-3 (3x lower DER vs. generic engines)
- **Code-switch handling:** Language-ID per utterance (CLD3 or fastText LangID) → route token to Hindi or English decoder within the same model
- **Confidence scoring per word:** words below confidence threshold (< 0.85) flagged for downstream uncertainty propagation
- **Output:** structured transcript JSON: `{speaker, start_ms, end_ms, text, language_tag, confidence}`

### Layer 1: Feature Extraction
- **Acoustic features:** pitch, pace, silence ratio, overtalk, hold frequency — extracted via librosa or enterprise speech analytics SDK (Tethr, Cogito)
- **Sentiment timeline:** per-utterance sentiment (positive/neutral/negative) via fine-tuned multilingual model (XLM-R or IndicBERT)
- **Entity redaction:** PAN, Aadhaar, account numbers → `[REDACTED]` before LLM processing (presidio or Sarvam's redaction layer)
- **Metadata join:** CRM pull — queue type, agent ID, campaign, customer segment, prior call history

### Layer 2: LLM-as-Judge (Core Scoring)
Architecture: **Autorubric-style rubric decomposition** — each rubric dimension is a separate LLM call with a focused prompt. This outperforms single-prompt-all-dimensions on both accuracy and debuggability.

**Rubric dimensions (typical India BPO):**
| Dimension | Weight | Auto-fail? |
|---|---|---|
| Mandatory disclosure (entity ID, purpose, recording consent) | 15% | YES |
| Compliance — no threatening language, no unauthorized promise | 20% | YES |
| PII handling — no unnecessary repetition of sensitive data | 10% | YES |
| Empathy and tone | 15% | No |
| Language adaptation (code-switch quality) | 10% | No |
| Problem resolution / outcome | 15% | No |
| Call close quality | 10% | No |
| Script adherence vs. natural effectiveness | 5% | No |

**LLM judge pipeline:**
```
transcript_json + metadata
    → [parallel LLM calls, one per rubric dimension]
    → each returns: {score: 1-5, evidence: "quote from transcript", confidence: 0-1, reasoning: "..."}
    → aggregation: weighted sum + auto-fail check
    → final_qa_score + coaching_notes_draft
```

**Model choices:**
- Dimension scoring: Claude Haiku 4.x or Gemini 2.0 Flash (speed + cost priority; ~$0.002/call at typical 15-min call = ~8K tokens)
- Coaching note generation: Claude Sonnet 4.x (quality priority; triggered only when score < threshold or auto-fail triggered)
- Compliance gate verification (regulatory-critical): Claude Opus or GPT-o4 with lower temperature (accuracy priority over cost)

**Prompt pattern:** System prompt contains full rubric with few-shot examples (cached via Anthropic prompt caching — same rubric prefix across all calls = >80% cache hit, 80% cost reduction). User prompt is transcript + metadata.

**Structured output:** Tool use / function calling — LLM fills a typed schema, no free-form parsing.

```python
class DimensionScore(BaseModel):
    dimension: str
    score: int  # 1-5
    auto_fail: bool
    evidence: str  # quote from transcript
    coaching_note: str
    confidence: float  # 0-1

class QAResult(BaseModel):
    call_id: str
    overall_score: float
    weighted_total: float
    auto_fail_triggered: bool
    auto_fail_reasons: list[str]
    dimension_scores: list[DimensionScore]
    recommended_action: Literal["coaching", "escalate_compliance", "escalate_fraud", "best_practice_flag", "none"]
    llm_model_used: str
    scoring_latency_ms: int
    cached_tokens: int
    uncached_tokens: int
```

### Layer 3: Gold-Label Pipeline (Active Learning)
Not every call needs human review. The system routes to human annotators using **uncertainty-first active learning**:

**Routing criteria (in priority order):**
1. Auto-fail triggered → always human review (compliance risk)
2. LLM confidence < 0.75 on any dimension → human review
3. Score in borderline zone (2.0–2.5 or 4.5–5.0) where rubric interpretation matters most → sample 20%
4. Agent on PIP → 100% human review of their calls
5. New agent (< 30 days) → 50% human review
6. Randomly sampled 3–5% of all calls → calibration baseline

**Annotation tooling:** Label Studio or Argilla (open source), or MaestroQA / Enthu.ai for enterprise. Interface shows: audio player synced with transcript, pre-filled AI scores, human override fields, disagreement reason dropdown.

**Gold-label schema:**
```python
class GoldLabel(BaseModel):
    call_id: str
    annotator_id: str
    dimension: str
    human_score: int
    ai_score: int
    agreement: bool
    disagreement_category: Optional[Literal[
        "rubric_ambiguity", "transcript_error", "context_missing",
        "language_nuance", "ai_hallucinated_evidence", "correct_ai_wrong_human"
    ]]
    corrected_evidence: Optional[str]
    note: str
    calibration_session_id: str
```

**Inter-rater agreement:** Minimum 2 annotators per gold-label call. Cohen's kappa computed per dimension per calibration session. Threshold: kappa >= 0.75 to accept dimension as gold. If kappa < 0.6, rubric clarification is mandatory before continuing.

### Layer 4: Drift Detection
Three drift signals monitored continuously:

**Signal 1 — Score distribution drift:**
- Rolling 7-day average score per dimension vs. 90-day baseline
- Alert if avg shifts > 0.3 points or score distribution KL-divergence > 0.2
- Tool: Evidently AI or custom Prometheus metrics + Grafana dashboard

**Signal 2 — Human-AI agreement rate drift:**
- kappa computed weekly from gold-label pipeline output
- Alert if kappa falls below 0.70 (was 0.80 at last calibration)
- This is the primary drift signal — score drift can be false alarm; kappa drift is real

**Signal 3 — Concept drift from external events:**
- Regulatory update tracker: RSS feeds from RBI, IRDAI, DPDP.gov.in
- Script update log from business: when a new call script is deployed, auto-trigger rubric review
- Product change log: new product launches may introduce new compliance requirements
- Alert: "Concept drift likely — manual rubric review required"

**Drift types and remedies:**
| Drift type | Cause | Remedy |
|---|---|---|
| Transcript quality drift | ASR WER increase (new devices, network degradation) | ASR model update / audio pre-processing |
| Rubric interpretation drift | LLM judge model updated by provider | Re-run calibration on gold set, re-prompt |
| Concept drift | Regulatory change, new script | Human rubric rewrite + new gold labels |
| Data distribution shift | New product, new customer segment | Expand gold set to cover new domain |
| Score inflation | Prompt became too lenient over time | Recalibrate few-shot examples in prompt |

### Layer 5: Continuous Tuning
Three levers, in order of preference (cheapest to most expensive):

**Lever 1 — Few-shot recalibration (weekly, no training cost):**
- Take disagreement examples from gold-label pipeline
- Replace worst-performing few-shot examples in rubric prompt with better-calibrated ones
- Re-run on held-out gold set (n=200); accept if kappa improves

**Lever 2 — Rubric rewrite (monthly or after concept drift event):**
- QA lead + legal/compliance team review failing dimension rubrics
- Rewrite ambiguous rubric language; add new examples
- Minimum calibration session before re-deployment

**Lever 3 — Fine-tuning (quarterly or major drift):**
- Collect 5,000+ gold-labeled examples with human overrides
- Fine-tune via DPO (preferred) or SFT on a small judge model (Llama 3.1 8B or Qwen 2.5 7B)
- Serve via vLLM on Modal/Anyscale — cost: ~$0.0001/call vs. $0.002/call for GPT-4o
- A/B gate: new fine-tuned model must match kappa within 0.03 of Claude Sonnet baseline before promotion

---

## 4. 2026 Tooling Stack

### ASR / Transcription
- **Gnani.ai Prisma v2.5** — best-in-class India multilingual (June 2026, beats Sarvam + ElevenLabs + Deepgram on Indic WER)
- **Sarvam AI Saarika v2** — strong Hindi, smaller cost for Hindi-only queues
- **Deepgram Nova-3 Multilingual** — fallback for English-heavy queues
- **AWS Transcribe Call Analytics** — enterprise compliance recording integration
- **Pyannote 3.x** — speaker diarization

### LLM Scoring
- **Claude Haiku 4.x** — fast, cheap per-dimension scoring ($0.80/1M input tokens)
- **Claude Sonnet 4.x** — coaching note generation, complex compliance checks
- **Anthropic Prompt Caching** — system prompt + rubric cached; >80% hit rate for same rubric across calls
- **Autorubric (arxiv 2603.00077)** — open-source rubric decomposition + calibration framework
- **Instructor or Pydantic AI** — structured output enforcement

### Gold-Label + Calibration
- **Label Studio** (open source) or **Argilla** (open source, Python-native)
- **MaestroQA** / **Enthu.ai** / **Evaluagent** — enterprise annotation + QA workflow
- **Krippendorff's alpha calculator** (Python `krippendorff` library) — multi-annotator agreement
- **Autorubric calibration module** — automated kappa computation per dimension

### Drift Detection + Observability
- **Evidently AI** — data drift, score distribution monitoring
- **Langfuse** or **Phoenix (Arize)** — LLM call tracing, token costs, latency per call
- **Prometheus + Grafana** — score distribution dashboards
- **Helicone** — cost tracking per rubric dimension

### Fine-Tuning (when needed)
- **TRL (DPO trainer)** + **Unsloth** — fast, memory-efficient fine-tune on QA judge model
- **Modal Labs** — serverless GPU for training + serving fine-tuned judge
- **vLLM** — serving fine-tuned judge model in production

### Compliance + Privacy
- **Microsoft Presidio** — PII redaction before LLM processing
- **Sarvam Redaction API** — India-specific entity redaction (Aadhaar, PAN, account numbers in Hindi/transliterated form)
- **Audit log store** — immutable append-only log (S3 + object lock or Kafka → Iceberg) for DPDP compliance evidence

---

## 5. Benchmarks

| Metric | Value | Source/Tag |
|---|---|---|
| Traditional QA call sampling rate | 2–5% of calls | [sourced] Industry standard |
| AI auto-QA coverage | 100% | [sourced] Observe.AI, Evaluagent |
| AI-human agreement rate (generic rubric) | 88–91% | [sourced] Observe.AI, theaiqms.com |
| LLM judge kappa vs. human (domain-specific) | 0.51–0.75 (median 0.60) | [sourced] Krippendorff alpha across Gemini 2.5 Pro, GPT-4o, Claude 3.7 Sonnet (2025 study) |
| Target production kappa | >= 0.75 per dimension | [estimate] Industry best practice |
| Counterfactual Flip Rate (CFR) — LLM bias | 5.4%–13.0% (16.4% with context priming) | [sourced] arxiv 2602.14970, 18 models, 3,000 calls |
| Hinglish ASR WER (Tier-1 cities) | 22–30% | [sourced] Deepgram + Gladia research |
| Gnani Prisma v2.5 WER improvement vs. competitors | 15% lower on rural Hindi | [sourced] Gnani.ai / BusinessToday June 2026 |
| End-to-end scoring latency (post-call) | 30–90 seconds typical | [estimate] based on ASR + LLM pipeline timing |
| Cost per call (LLM scoring, 15-min call) | $0.002–0.008 depending on model | [estimate] based on token counts + pricing |
| Traditional QA analyst cost per reviewed call | $1.50–3.00 (India BPO rates) | [estimate] |
| AI QA cost reduction vs. manual | 80–90% | [sourced] callcenterstudio.com, crescendo.ai |
| Fine-tuned judge model cost reduction vs. Claude Sonnet | ~20x cheaper per call | [estimate] vLLM serving of 8B model |
| Gold-label annotation volume needed for DPO fine-tune | 5,000+ examples | [estimate] TRL DPO typical minimum |
| Monthly drift check frequency | 3–5% production sample | [sourced] futureagi.com enterprise pattern |
| Score distribution drift alert threshold | KL divergence > 0.2, avg shift > 0.3 | [estimate] |
| Kappa re-calibration trigger | kappa < 0.70 (vs 0.80 baseline) | [estimate] |

---

## 6. Failure Modes

### 6a. Transcription-layer failures
- **Code-switch ASR collapse:** Agent says "account ka balance hai 15,000 rupees, aur iske against koi pending EMI nahi" — ASR drops "rupees" or garbles the number; downstream score on "accuracy" is wrong
- **Crosstalk / overtalk misattribution:** Diarization assigns customer speech to agent during an interruption → agent gets penalized for customer's angry statement
- **Low-bitrate call recording:** 8kbps GSM encoding (common in India mobile networks) degrades ASR accuracy by 15–25%; no amount of prompt engineering fixes bad transcripts
- **Silence / hold music:** ASR transcribes hold music as unintelligible tokens; pads transcript with noise

### 6b. LLM scoring failures
- **Empathy hallucination:** Agent reads a script verbatim with zero real empathy, but the scripted words contain "I understand your concern" — LLM scores empathy 4/5 based on keywords, not tone
- **Evidence fabrication:** LLM claims agent said X as evidence; agent never said X — transcript quote is confabulated (higher risk with weaker models like Haiku on long transcripts)
- **Rubric-language ambiguity:** "Was the problem resolved?" — if a follow-up is scheduled, is that resolved? LLM interprets differently than human QA
- **Positional bias:** LLM judges score the opening and closing of calls more accurately than the middle (attention degradation on 15-min transcripts at 2K+ tokens)
- **Counterfactual bias (CFR):** When agent background/context is included in prompt, bias rates reach 16.4% CFR — model effectively penalizes accent mentions, regional phrases, non-standard grammar
- **Language-tag errors:** Hindi in Devanagari vs. Romanized Hinglish — rubric written for Devanagari fails to evaluate "Bilkul theek hai sir, aapko kal tak mil jayega" written in Roman script

### 6c. Gold-label pipeline failures
- **Annotator fatigue:** After 50+ calls, human kappa drops; last-hour annotations are lower quality
- **Calibration drift among annotators:** Without regular calibration sessions, two annotators diverge on empathy scoring — gold labels become noisy
- **Survivorship bias in sampling:** If only low-confidence calls go to human review, the gold set is not representative of the full distribution

### 6d. Drift detection failures
- **Silent prompt drift:** LLM provider silently updates model weights (OpenAI does this) → scores shift without any observable trigger; undetected for weeks
- **Kappa masking:** Overall kappa stays 0.78 but one dimension (compliance) drops to 0.55 — masked by aggregate; compliance issues go undetected
- **False drift alarms from script changes:** New call script triggers score distribution shift that looks like drift but is actually a legitimate improvement; auto-recalibration suppresses valid gains

### 6e. Continuous tuning failures
- **DPO on noisy gold labels:** If annotator agreement was kappa=0.60 but you fine-tune on those labels anyway, the fine-tuned model learns noise; can worsen performance
- **Distribution shift from fine-tuning:** Fine-tune on insurance queue calls, but model is deployed on collections queue — catastrophic forgetting of rubric for collections
- **Overfitting to gold annotators' style:** Model learns one QA lead's idiosyncratic scoring preferences; poor generalization when QA lead changes

---

## 7. Gap to Full Adaptation (What AI Still Cannot Do as Well as a Human)

### Gap 1: Tone and Prosody Judgment (Largest Gap)
**What human does:** Listens to the actual voice — detects sarcasm, under-breath sighs, rushed speech, fake concern. A human knows the difference between "I understand sir" said with genuine warmth vs. with barely-concealed impatience.  
**What AI does:** Scores empathy from transcript text + coarse acoustic features (pitch, pace). Misses the 40% of empathy signal that's in prosody but not text.  
**Path to close:** Audio-native LLM scoring (Gemini 2.5 Pro has audio input; Claude does not yet). Fine-tune an audio-language model (e.g., Qwen-Audio, Krutrim-Audio) on annotated empathy clips. Requires a Hindi + Hinglish audio empathy dataset — does not exist commercially today.

### Gap 2: Context-Aware Compliance Judgment
**What human does:** Knows that "main aapka maamla upar bhejoonga" is a harmless escalation promise vs. "legal action liye bina chod dunga" is a veiled threat. Reads intent from context.  
**What AI does:** Keyword-triggers on threat indicators; high false positive rate on colloquial idioms ("maar dunga yeh bill" = "I'll destroy this bill" = pay off the bill, not threat).  
**Path to close:** Build a domain-specific compliance classifier trained on India BPO call transcripts with expert-labeled intent categories. 10K labeled examples needed. Use contrastive pairs (same phrase, different context = different intent).

### Gap 3: Multi-Turn Memory Across the Interaction
**What human does:** Remembers that the agent promised something in minute 3, checks at minute 12 if they delivered on it. Evaluates consistency of position across the call.  
**What AI does:** Processes the transcript but has positional attention limitations on long transcripts; middle-of-call commitments tracked less reliably than opening/closing ones.  
**Path to close:** Implement a "commitment tracker" agent that extracts all agent promises and commitments as structured events, then verifies each at call close. Simpler than full LLM attention fix.

### Gap 4: Cross-Call Pattern Recognition
**What human does:** A senior QA analyst knows Agent X has a habit of deflecting angry customers with filler rather than resolution. This pattern across 20 calls is what earns a coaching session.  
**What AI does:** Scores individual calls; cross-call pattern synthesis requires an additional aggregation layer.  
**Path to close:** Call-level scores are already generated. Add a weekly cross-call synthesis agent: "Here are agent X's 47 calls this week. Summarize recurring patterns in coaching opportunities." Already feasible today with Claude Sonnet.

### Gap 5: Regulatory Nuance (RBI / IRDAI / DPDP)
**What human does:** Knows that under RBI's Fair Practices Code, the specific required phrasing in a collection call is defined; ambiguous phrasing fails compliance even if "polite." Knows that IRDAI requires specific disclosures for unit-linked products.  
**What AI does:** Generic compliance scoring based on rubric; rubric quality is bounded by how well the legal/compliance team has documented the rules.  
**Path to close:** Build a structured regulatory knowledge base (RBI FPC, IRDAI disclosure norms, DPDP consent requirements) in a RAG layer that the LLM judge queries before scoring compliance dimensions. Maintain with regulatory update tracking.

---

## 8. HITL Trigger

Human must take over in these scenarios:

1. **Auto-fail triggered on compliance dimension** → human QA reviewer must confirm before any coaching/escalation action is taken (false positives on compliance have agent career consequences)
2. **LLM judge confidence < 0.65 on any dimension** → human review of that dimension (score is unreliable)
3. **Kappa between AI score and human calibration set drops below 0.70** → halt auto-dispatch of coaching; trigger rubric review by QA lead
4. **Regulatory update detected** (RBI circular, IRDAI notification, DPDP rule amendment) → all compliance-dimension scoring paused; human rubric rewrite required before resuming
5. **New product or script deployed** → 1-week calibration period where 100% of calls in new script go to human review to generate new gold labels
6. **Agent appeals an AI-generated score** → human QA arbitration required; AI score is provisional until human confirms or overrides
7. **Demographic/accent-related score anomaly detected** → fairness audit required (CFR bias; see arxiv 2602.14970)

---

## 9. Automation Readiness: 7 / 10

**What works today (automated):**
- 100% call transcription with Hinglish support: works, 85%+ accuracy
- Automated scoring on text-based dimensions (disclosure, script adherence, resolution): works, 88–91% human agreement
- Structured output, coaching note generation, action routing: works
- Score dashboards, trend monitoring: works
- Gold-label routing with uncertainty-based prioritization: works
- Weekly kappa monitoring: works

**What still needs humans (the 3 points gap):**
- Tone/prosody empathy scoring: audio-native LLMs not yet production-grade for Hinglish
- Compliance nuance on ambiguous idioms: requires India-specific labeled dataset
- Regulatory update interpretation: legal/compliance human required for rubric updates
- Agent appeal arbitration: always human (fairness/legal exposure)

**What gets it to 9/10:**
- Audio-native multilingual LLM (Gemini 2.5 Pro audio or Krutrim-Audio) fine-tuned on India BPO empathy dataset
- India compliance knowledge base (structured + RAG) with regulatory update tracking
- Cross-call pattern synthesis agent (already buildable today)

---

## 10. Build Specification

### What to Build

**Phase 1 (4–6 weeks): 100% Auto-Scoring Pipeline**

Components:
- ASR integration: Gnani Prisma v2.5 API or Sarvam Saarika v2 → diarized transcript JSON
- PII redaction: Presidio + custom India entity patterns (Aadhaar 12-digit, PAN alphanumeric, account numbers)
- LLM judge: Anthropic SDK with prompt caching + Autorubric-style dimension decomposition
- Structured output: Pydantic schema enforced via tool use
- Score storage: PostgreSQL (call_scores table) + S3 (raw transcript archive for DPDP audit trail)
- Dashboard: Metabase or Grafana on top of PostgreSQL

Data needed:
- 500 manually-scored calls per queue type (minimum) to validate auto-scoring accuracy
- Rubric documents from BPO client (existing scorecards)
- Regulatory reference docs (RBI FPC, IRDAI disclosure requirements)

Gate metric: Cohen's kappa >= 0.75 on held-out 200-call validation set, per dimension. Deploy when all dimensions pass.

**Phase 2 (2–3 weeks): Gold-Label Pipeline**

Components:
- Annotation interface: Label Studio deployment with call audio player + transcript + AI pre-fill
- Routing logic: uncertainty-based active learning sampler
- Agreement computation: automated kappa per session per dimension
- Calibration session scheduler: bi-weekly reminder + auto-sample stratified set

Gate metric: Inter-annotator kappa >= 0.75 on calibration session output.

**Phase 3 (ongoing): Drift Detection + Continuous Tuning**

Components:
- Evidently AI score distribution monitor with Prometheus export
- Weekly kappa report generation (automated)
- Regulatory RSS feed watcher → Slack/Telegram alert on new RBI/IRDAI/DPDP notifications
- DPO fine-tune pipeline (quarterly): TRL + Unsloth + Modal → vLLM serving

Gate metric for fine-tune promotion: Fine-tuned model must match or exceed Claude Sonnet kappa on 200-call gold set before promotion.

### Cost Model (India mid-market BPO, 10,000 calls/day)
| Component | Cost/day |
|---|---|
| ASR (Gnani Prisma) | ~$150 (at ~$0.015/min × 15 min avg × 10K calls) |
| LLM scoring (Claude Haiku, cached) | ~$20–40 (8K tokens/call × 10K × $0.0008/1K, ~80% cached) |
| Human gold-label (3–5% of 10K = 300–500 calls) | ~$150–250 (at ₹50/call India QA rate) |
| Infra (storage, compute, dashboard) | ~$30 |
| **Total AI QA cost/day** | **~$350–470** |
| **Equivalent manual QA at 3% sampling (300 calls/day)** | **~$450–900** |
| **Savings from 100% AI coverage vs. 3% manual** | **>60% cost, 33x coverage** |

---

## 11. India-Specific Nuances

### Linguistic Complexity
- **Hinglish code-switching:** A single call can contain Hindi (Devanagari or Roman), English, and regional idioms. QA rubric must explicitly handle: "main samjha ki aap ko kal tak credit milega" — this is a promise that triggers compliance scoring regardless of script language.
- **Regional language distribution:** Hindi queues dominate (30%), but Tamil, Telugu, Kannada, Marathi, Bengali queues each have distinct compliance norms and communication styles. A rubric for Hindi empathy ("arre yaar, samjhiye na") differs from Tamil empathy markers.
- **Romanized Hindi in transcripts:** ASR models often output Romanized Hindi ("abhi main check karta hoon" instead of Devanagari). Rubric examples must cover both scripts or normalize to one.

### Regulatory Specifics
- **RBI Fair Practices Code (FPC):** Collection agents must identify themselves and employer, not harass between 8PM–8AM, not contact references without consent, offer a grievance redressal mechanism. These are binary compliance gates — any failure is auto-fail.
- **IRDAI disclosure norms:** Insurance sales calls must include free-look period disclosure, premium amount confirmation, exclusions summary. Mandatory disclosures vary by product type (term, ULIP, health).
- **DPDP Act 2023 (rules notified Nov 2025, enforcement by May 2027):** Explicit consent required before recording; consent purpose must match actual use; erasure requests must be honored within timeline. QA audit trail itself must be stored with data minimization — don't log full PII in QA records.
- **TRAI DLT framework:** Outbound calls must use registered headers and templates. AI QA should verify if the agent identified the correct DLT-registered entity name in opening.

### BPO Operational Realities
- **Accent diversity within "Hindi":** Bhojpuri-inflected Hindi, Rajasthani Hindi, and UP-Bihari Hindi sound different; ASR models trained on standard Mumbai/Delhi Hindi miss regional agents. Gnani Prisma v2.5's 15% WER improvement on rural Hindi dialects directly addresses this.
- **Agent attrition:** 60–80% annual attrition in Indian BPOs means the agent population is constantly new. QA flywheel must flag new agents (< 30 days) for higher human review rates.
- **Call volume spikes:** Festive season (Diwali, year-end), regulatory deadlines, product launches cause 3–5x call volume spikes. Auto-QA must scale horizontally — stateless scoring pods on Kubernetes or Modal serverless.
- **PIP sensitivity:** In India's BPO culture, QA scores directly determine Performance Improvement Plans and terminations. False positives on AI scoring have real career consequences. This amplifies the need for kappa gates and human escalation on compliance dimensions.
- **BFSI-specific queues:** Banking (RBI-governed), insurance (IRDAI-governed), and NBFC (RBI-governed) clients have distinct rubrics. Multi-client BPOs need per-client rubric isolation — same infrastructure, different prompt cached prefixes per client.

### Gold-Label Workforce
- Senior QA analysts in India earn ₹25,000–50,000/month; annotation rate ~40 calls/day for quality work
- Calibration sessions should be in Hindi/Hinglish — not English-only — to ensure rubric interpretation is culturally aligned
- Inter-annotator disagreements on empathy are higher in India vs. Western benchmarks due to indirect communication norms; rubrics must account for culturally appropriate assertiveness vs. aggression thresholds

---

## 12. References

- [Counterfactual Fairness Evaluation of LLM-Based Contact Center QA Systems (arxiv 2602.14970)](https://arxiv.org/abs/2602.14970) — 18 models, 3,000 calls, CFR 5.4–13.0%
- [Autorubric: Unifying Rubric-Based LLM Evaluation (arxiv 2603.00077)](https://arxiv.org/html/2603.00077v2) — open-source calibration framework
- [Observe.AI Auto QA](https://www.observe.ai/post-interaction/auto-qa) — 100% interaction coverage, 97% compliance monitoring improvement
- [Gladia: Call Center AI Quality Assurance](https://www.gladia.io/blog/call-center-ai-quality-assurance) — transcription-first architecture, WER < 5% target
- [Gnani.ai Prisma v2.5 Launch](https://www.gnani.ai/resources/blogs/gnani-ai-launches-vachana-stt) — 15% lower WER on rural Hindi, 14M hours training data
- [Hinglish Voice AI: Why ASR Fails](https://deepgram.com/learn/hinglish-voice-ai-speech-recognition) — code-switching WER benchmarks
- [LLM Model Drift Detection 2026](https://stackpulsar.com/blog/llm-model-drift-detection/) — drift types and remedies
- [RBI & DPDP Dual Compliance BFSI 2026](https://www.tcsa.in/resources/dpdp-compliance-bfsi-rbi-guidelines) — regulatory requirements
- [AI Calling Compliance India 2026 Complete Guide](https://www.autointerviewai.com/blog/ai-calling-india-dpdp-trai-dlt-compliance-complete-guide-2026) — TRAI DLT, RBI FPC, IRDAI norms
- [Judge's Verdict: LLM Judge Agreement Analysis](https://arxiv.org/html/2510.09738v1) — kappa ranges across 54 LLMs
- [LLM Drift Monitoring Platforms 2026 (Galileo)](https://galileo.ai/blog/best-llm-output-drift-monitoring-platforms) — monitoring tools comparison
- [Krutrim LLM: Multilingual for India (arxiv 2502.09642)](https://arxiv.org/abs/2502.09642) — BharatBench top-3 performance
- [HiACC: Hinglish Code-Switched Corpus (NIH)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12329218/) — research dataset for Hinglish ASR
- [Best AI QA Tools for BPOs 2026 (Gistly)](https://www.gistly.ai/blog/best-ai-qa-tools-for-bpos) — vendor comparison including DPDP readiness
- [Quality Parameters for BPO (DialNexa)](https://dialnexa.com/blogs/quality-parameters-for-bpo/) — scorecard dimensions and benchmarks
