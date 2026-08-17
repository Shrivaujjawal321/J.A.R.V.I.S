# Step A05 — Language, Dialect & Code-Mixing Handling (Hinglish, regional switch mid-sentence)

**Domain:** India-market, multilingual (Hindi + regional + Hinglish), RBI/IRDAI/DPDP-compliant, action-taking voice + chat contact-center agent for mid-market BPOs.
**Scope of this dossier:** ONLY the cross-cutting capability of *handling the language the customer actually speaks* — detecting it, transcribing it, understanding it, and replying in the matching register — when that language is fluid Hinglish or shifts dialect/language mid-sentence.
**Date:** 2026-06-24
**Status:** Standalone build-spec dossier.

> This is not the same as "translation." It is the layer that keeps every other step (intent, retrieval, action-taking, compliance disclosure) working when the human refuses to stay in one language for one sentence. In India this is the *default* mode of speech, not an edge case.

---

## 0. Why this step is load-bearing

In India, code-switching is the norm, not the exception — typical conversations mix 2–3 languages within a single sentence ([Cyfuture, 2026](https://cyfuture.ai/blog/multilingual-chatbots-india)). The proportion of Indian users preferring romanized Hinglish rose from 44.9% (2014) to 56.3% (post-2020) ([arXiv 2511.22769, 2025](https://www.arxiv.org/pdf/2511.22769)). A production agent that only handles "clean Hindi" or "clean English" silently fails on the majority of real calls.

Real utterance the system must handle in one pass, no restart:
> "Sir, aapka EMI **due hai** on the 15th, can you **confirm** the payment account?"
> (Hindi opener → English temporal anchor → English body → English entity)
([Caller Digital, 2026](https://caller.digital/blog/multilingual-voice-ai-hindi-tamil-telugu-bengali-india-2026))

This step degrades **every downstream step**: a mis-transcribed switch point poisons NLU, retrieval, the action payload, and the compliance disclosure. So its quality bar is higher than its perceived "support" status.

---

## 1. Human micro-steps (the smallest atomic moves a skilled bilingual agent makes)

A skilled Indian BPO agent does NOT consciously "detect language." They do a tight, sub-second loop. Decomposed:

1. **Passive language inventory** — within the first 1–2 seconds of the caller speaking, the agent forms an implicit profile: base language (Hindi/Tamil/etc.), comfort with English, register (formal/casual), and roughly the dialect/region ("yeh Bihar-side ka Hindi hai", "yeh South-accented Hindi hai").
2. **Matrix-language decision** — picks the *base* (matrix) language to anchor their own reply, while keeping English available for embedded technical/financial terms. (e.g., decides "I'll speak Hindi but say EMI/account/KYC in English because translating them sounds weird.")
3. **Borrowing vs. switching discrimination** — distinguishes an English word that is *naturalized* into Hindi ("payment", "balance", "block kar do") — keep as-is — from a genuine switch ("can you confirm…") — match it. They never translate "account" to "khaata" unless the caller did.
4. **Mid-sentence switch tracking** — follows the caller flipping languages within one breath and does NOT lose the thread; resolves pronouns/entities across the switch ("woh card… the new one… block kar do").
5. **Entity preservation across scripts** — hears an alphanumeric / name / amount embedded in the other language and locks it exactly ("order ID ABC-1234", "Rs. 4,500", "Lucknow") without "translating" or rounding it.
6. **Register mirroring** — mirrors formality and warmth: respectful "aap/aapka" if caller is formal/elderly; lighter if casual; never down-shifts to disrespectful "tu". Adds fillers a human would ("ji", "bilkul", "haan ji").
7. **Dialect accommodation** — adjusts comprehension for regional Hindi (Bhojpuri-tinged, Marwari, Mumbai-Hindi with Marathi loanwords) AND optionally softens own dialect to a neutral standard the caller will understand.
8. **Repair on mismatch** — if they guessed the wrong base language ("Tamil samajh aata hai?"), they gracefully re-anchor without making the caller feel judged ("English mein bata doon?").
9. **Code-mix the *reply*** — produces an answer in the same mixed style the caller used, because a pure-Hindi or pure-English reply to a Hinglish caller feels robotic/cold.
10. **Compliance-language gating** — knows the mandatory disclosure (identity, recording consent, KFS-type facts) must land in a language the customer *actually understands*, and will switch to deliver it clearly even if the chit-chat was casual.
11. **Pronunciation of the other language's tokens** — when reading back, pronounces English numbers/names correctly inside a Hindi sentence (says "fifteen", not "pandrah", if the caller said "fifteen") to confirm faithfully.
12. **Continuous re-profiling** — keeps updating the inventory; if the caller drifts more into English mid-call, the agent drifts with them. It's a live tracking task, not a one-time setting.

These twelve are the gap-to-close list. Most 2026 systems nail 1–6 and 9–11; they are weakest on **8 (graceful repair), 7 (deep dialect), and 12 (live adaptive drift).**

---

## 2. Agent approach — how a 2026 AI agent performs each micro-step

The winning 2026 pattern is **NOT** "LID router → monolingual ASR." First-gen utterance-level LID assigns one label per utterance and "fails completely on intra-sentential switches because the utterance contains two languages and one label has to win" ([Gladia, 2026](https://www.gladia.io/blog/what-is-code-switching-in-speech-recognition)). The winning pattern is a **single end-to-end multilingual code-switch-native ASR**, an **Indic-tuned code-mix-native LLM** for understanding, and a **code-mix-native TTS** for the reply — all language-agnostic at the *model* level.

| Human micro-step | 2026 agent technique |
|---|---|
| 1. Passive language inventory | End-to-end multilingual ASR emits per-segment language attribution as a side output (no separate LID hop). Sarvam **Saaras V3** auto-identifies Hindi/Tamil/Telugu/etc. natively ([Sarvam, 2026](https://www.sarvam.ai/blogs/asr)). Maintain a rolling `language_profile` state object in the orchestrator. |
| 2. Matrix-language decision | LLM system-prompt policy: "Reply in the caller's *matrix* language; keep their English-borrowed terms in English." Set `matrix_lang` from the modal language of the last N segments. |
| 3. Borrowing vs. switching | Don't translate. Use a **naturalized-loanword allowlist** (account, balance, EMI, KYC, block, payment, OTP, branch…) the LLM is instructed to preserve verbatim. Code-mix-native LLMs (Sarvam-M) already model this distributionally. |
| 4. Mid-sentence switch tracking | Code-switch-native ASR keeps one token stream across the switch; no re-segmentation. Apple's retraining-free method cuts intra-sentential WER 34.4%→15.3% (55.5% rel.) on Hindi-English ([via Gladia, 2026](https://www.gladia.io/blog/what-is-code-switching-in-speech-recognition)). |
| 5. Entity preservation across scripts | **Domain/keyword biasing** (phrase hints: order-ID format, customer name list, amounts) + verbatim formatting. Saaras V3 "preserves correct word boundaries… avoids hallucinated insertions" ([Sarvam, 2026](https://www.sarvam.ai/blogs/asr)). Post-ASR regex/validator for alphanumerics. |
| 6. Register mirroring | LLM persona prompt enforces respectful "aap" register + Indian fillers ("ji", "bilkul"). Style-conditioned generation. |
| 7. Dialect accommodation | Dialect-balanced fine-tuning / data augmentation on Bhojpuri, Marwari, Chhattisgarhi, Mumbai-Hindi (Augmen, Gnani approach). Still the weakest link (see §5/§6). |
| 8. Repair on mismatch | Orchestrator rule: if 2 consecutive low-confidence ASR segments OR a language-confidence flip, agent offers a language switch ("English mein बताऊँ?"). Confidence-gated, not free-form. |
| 9. Code-mix the reply | Code-mix-native TTS: **Bulbul V3** generates Hinglish "in a single pass," not a detect-then-route pipeline ([Sarvam/dev.to, 2026](https://dev.to/agent_paaru/indian-language-tts-for-your-ai-agent-integrating-sarvamai-bulbul-v3-with-openclaw-1fdg)). LLM produces mixed-script/romanized output the TTS speaks naturally. |
| 10. Compliance-language gating | Deterministic policy layer: mandatory disclosures rendered from **pre-approved per-language templates**, selected by `matrix_lang`, never free-generated. (DPDP "preferred language", RBI trilingual — see §10.) |
| 11. Pronunciation of other-language tokens | TTS with per-token G2P routing + rule-based expansion for numerals/abbreviations/alphanumerics; Bulbul V3 scores lowest CER on numerics, code-mixing, Romanized text, named entities ([Sarvam, 2026](https://www.sarvam.ai/blogs/bulbul-v3)). |
| 12. Continuous re-profiling | Streaming update of `language_profile` every segment; `matrix_lang` is an EWMA over recent segments, so the agent drifts with the caller. |

**Reference architecture (voice):**
```
Caller audio
  → [Streaming code-switch-native ASR]  (Saaras V3 / Sarvam, or Gladia Solaria-1 w/ enable_code_switching)
       emits: tokens + per-segment lang tags + confidence
  → [Language-profile tracker]  (rolling matrix_lang, register, dialect hint, drift)
  → [Code-mix-native LLM NLU + dialogue]  (Sarvam-M / GPT-class w/ Indic adaptation)
       w/ loanword-preserve prompt + entity validator
  → [Compliance template selector]  (deterministic, per-language approved scripts)
  → [Code-mix-native TTS]  (Bulbul V3 single-pass Hinglish)
```
Chat path is the same minus ASR/TTS, plus a **romanized-Hindi normalizer** (transliteration) because chat Hinglish is overwhelmingly Roman-script ([arXiv 2511.22769, 2025](https://www.arxiv.org/pdf/2511.22769)).

---

## 3. Tooling — concrete 2026 stack

**ASR (code-switch-native, streaming):**
- **Sarvam Saaras V3** — trained on 1M+ hrs Indic audio; TTFT < 150 ms; preserves code-mix word boundaries ([Sarvam, 2026](https://www.sarvam.ai/blogs/asr)).
- **Gladia Solaria-1** — `enable_code_switching: true`, per-utterance language attribution, ~270 ms real-time target, 94% WAR avg ([Gladia, 2026](https://www.gladia.io/blog/what-is-code-switching-in-speech-recognition)).
- **Gnani.ai ASR** — 12+ Indian languages, telephony-tuned, Hinglish focus ([Gnani, 2026](https://www.gnani.ai/resources/blogs/blog-code-switching-speech-recognition-hinglish-asr)).
- **Augmen AI Labs STT** — 22 Indian languages, dialect-balanced sampling ([Augmen](https://augmen.io/labs-stt.html)).

**LLM / NLU (code-mix-native):**
- **Sarvam-M** (open-weight Indic) — near-SOTA on code-mixed Hinglish intent in zero-shot ([JMIR 2026](https://www.jmir.org/2026/1/e86545)).
- GPT-class / Llama-class **with Indic adaptation + few-shot Hinglish exemplars**; gate with a loanword-preserve + romanization-aware prompt.

**TTS (code-mix-native):**
- **Sarvam Bulbul V3** — sub-250 ms streaming, single-pass Hinglish, lowest CER on numerics/named-entities/Romanized text ([Sarvam, 2026](https://www.sarvam.ai/blogs/bulbul-v3)).

**Romanized-Hindi / transliteration (chat + LLM normalization):**
- Transliteration models from the **Romanized Hindi/Bengali dataset work** ([arXiv 2511.22769, 2025](https://www.arxiv.org/pdf/2511.22769)); IndicXlit-class transliterators.

**Orchestration / telephony:**
- **Bolna**, **Caller Digital**, **Rootle**, **ConvozenAI**, **Haptik**, **Haloocom Hexa** — Indian voice-agent platforms wiring ASR+LLM+TTS with code-switch handling ([Bolna](https://blog.bolna.ai/multilingual-voice-ai/); [Haptik 2026](https://www.haptik.ai/blog/voice-ai-agents-for-indian-languages)).
- LiveKit / Pipecat-class real-time pipeline if self-hosting.

**Eval / benchmarks / data:**
- **LAHAJA** — multi-accent Hindi ASR benchmark ([arXiv 2408.11440](https://arxiv.org/pdf/2408.11440)).
- **HiACC** — Hinglish adult+children code-switched corpus, 5.24 hrs ([ScienceDirect, 2025](https://www.sciencedirect.com/science/article/pii/S2352340925006109)).
- **COMI-LINGUA** — expert-annotated large Hindi-English code-mix multitask dataset ([arXiv 2503.21670](https://arxiv.org/pdf/2503.21670)).
- **SwitchLingua** — 420K CS text samples, 80+ hrs, 12 languages ([via Gladia, 2026](https://www.gladia.io/blog/what-is-code-switching-in-speech-recognition)).
- **GLUECoS / LinCE** — code-switched NLU benchmarks.
- **"Voice of India"** national benchmark — shows global speech AI underperforms on Indian speech ([CXOToday, 2026](https://cxotoday.com/media-coverage/global-speech-ai-struggles-to-understand-india-new-national-benchmark-voice-of-india-reveals/)).

---

## 4. Benchmarks (real numbers)

| Metric | Value | Source |
|---|---|---|
| WER penalty of code-switch vs monolingual | **+30–50% relative** | [Gladia, 2026](https://www.gladia.io/blog/what-is-code-switching-in-speech-recognition) |
| Real Hindi-English noisy telephony WER — global models | **14–16%** | [Gnani, 2026](https://www.gnani.ai/resources/blogs/blog-code-switching-speech-recognition-hinglish-asr) |
| Same — leading Indic models | **11–14%** | [Gnani, 2026](https://www.gnani.ai/resources/blogs/blog-code-switching-speech-recognition-hinglish-asr) |
| Saaras V3 WER (top-10 IndicVoices subset) | **19.31%** | [Sarvam, 2026](https://www.sarvam.ai/blogs/asr) |
| Saaras V3 TTFT | **< 150 ms** | [Sarvam, 2026](https://www.sarvam.ai/blogs/asr) |
| Apple retraining-free intra-sentential CS WER | **34.4% → 15.3%** (−55.5% rel., Hi-En/Zh-En) | [via Gladia, 2026](https://www.gladia.io/blog/what-is-code-switching-in-speech-recognition) |
| Concatenated-tokenizer LID accuracy (FLEURS OOD) | **98%+** | [via Gladia, 2026](https://www.gladia.io/blog/what-is-code-switching-in-speech-recognition) |
| Gladia Solaria-1 word accuracy / latency | **94% WAR (6% WER) / ~270 ms** | [Gladia, 2026](https://www.gladia.io/blog/what-is-code-switching-in-speech-recognition) |
| Bulbul V3 TTS streaming latency | **sub-250 ms** | [Sarvam, 2026](https://www.sarvam.ai/blogs/bulbul-v3) |
| Standard Hindi WER vs Bhojpuri/dialect WER | **sub-10% → 20–30%** | [CXOToday, 2026](https://cxotoday.com/media-coverage/global-speech-ai-struggles-to-understand-india-new-national-benchmark-voice-of-india-reveals/) |
| Accuracy drop outside Delhi-Mumbai corridor | **−10–20%** unless fine-tuned | [AutoInterviewAI, 2026](https://www.autointerviewai.com/blog/vernacular-ai-voice-agents-india-hinglish-code-switching-2026) |
| Romanized-Hinglish user preference | **44.9% (2014) → 56.3% (post-2020)** | [arXiv 2511.22769, 2025](https://www.arxiv.org/pdf/2511.22769) |
| Voice-pipeline budget before TTS | **~600 ms (ASR 400 + LLM 200)** in cascade | [Gladia, 2026](https://www.gladia.io/blog/what-is-code-switching-in-speech-recognition) |

**Eval discipline (mandatory):** never report blended WER. Report **switch-point WER** (2–3 word window around transitions), **per-language WER separately**, and **hallucination rate at transitions** — a model at 3% English / 45% Spanish blends to ~8–12% which "looks acceptable until you check churn" ([Gladia, 2026](https://www.gladia.io/blog/what-is-code-switching-in-speech-recognition)).

---

## 5. Failure modes (where the agent breaks and why)

1. **Switch-point hallucination** — at a language boundary the LM "hallucinates a phonetically similar word in Language A or drops the segment" ([Gladia, 2026](https://www.gladia.io/blog/what-is-code-switching-in-speech-recognition)). Catastrophic when the dropped token is an amount or order-ID.
2. **Monolingual-bias substitution** — a monolingual-leaning model never emits `[UNK]`; it maps a foreign phoneme to the nearest English word, so "khaata" becomes a wrong English word silently ([Gladia, 2026](https://www.gladia.io/blog/what-is-code-switching-in-speech-recognition)).
3. **Tokenizer OOV gaps** — character-rich/rare tokens fall outside vocab (one study: 177 OOV tokens per test set), producing `[UNK]`/drops ([via Gladia, 2026](https://www.gladia.io/blog/what-is-code-switching-in-speech-recognition)).
4. **Dialect cliff** — WER jumps to 20–30% on Bhojpuri/Marwari/Chhattisgarhi and Lucknow-vs-Bhojpuri variation "breaks naive models" ([CXOToday, 2026](https://cxotoday.com/media-coverage/global-speech-ai-struggles-to-understand-india-new-national-benchmark-voice-of-india-reveals/)).
5. **Over-translation** — agent "translates" a naturalized loanword the caller deliberately kept English (says "khaata" when caller said "account"), sounding stilted and untrustworthy.
6. **Romanized chat misreads** — non-standard Roman spellings ("kal", "kl", "qal") of the same Hindi word fragment NLU; billions of words reach LLM backends "in a form they were never trained to understand" ([arXiv 2511.22769, 2025](https://www.arxiv.org/pdf/2511.22769)).
7. **Cascade latency compounding** — every LID/ASR/translate hop adds to a budget already ~600 ms before TTS; a detect-then-route design blows past the ~700–900 ms naturalness ceiling ([Gladia, 2026](https://www.gladia.io/blog/what-is-code-switching-in-speech-recognition)).
8. **Numeral/alphanumeric TTS errors** — reading "2026" as a year vs a confirmation code; G2P can't phonemize numerals/abbrevs without rule-based expansion ([Deepgram, 2026](https://deepgram.com/learn/alphanumeric-pronunciation-tts-quality-benchmark)).
9. **Register collapse** — agent drops to flat/disrespectful tone, or mismatches formality with an elderly/rural caller, damaging trust even when words are correct.
10. **Wrong matrix-language lock-in** — agent picks the wrong base language early and rigidly holds it, ignoring the caller's drift (micro-step 12 failure).
11. **Compliance-in-wrong-language** — disclosure rendered in a language the caller doesn't understand → DPDP "preferred language" / RBI vernacular non-compliance even if the transcript is perfect.

---

## 6. Gap to full adaptation (what the agent still can't match — and how to close it)

| Human edge the agent lacks | Why it's hard | Concrete close-the-gap path |
|---|---|---|
| **Deep dialect comprehension** (Bhojpuri-tinged Hindi, Marwari, Mumbai-Hindi) | Dialects under-represented; WER 20–30% vs <10% standard | **Dialect-balanced fine-tuning**: collect/label per-dialect telephony audio (use LAHAJA accent taxonomy), data-augment (pitch/speed/loanword injection), train per-region adapters; evaluate on a held-out per-dialect WER grid. |
| **Graceful repair on mis-guess** (micro-step 8) | Models commit to a transcription instead of signaling uncertainty | Calibrate ASR confidence; on 2 low-conf segments or a language-flip, trigger a **scripted, warm language-offer** ("English mein बताऊँ?"). Treat repair as a first-class dialogue state, not an error. |
| **Live adaptive drift** (micro-step 12) | One-time language settings are rigid | `matrix_lang = EWMA(recent segment langs)`; re-evaluate every turn; let TTS voice/register follow. Eval on synthetic "drift" dialogues. |
| **Borrowing/switching judgment** (micro-step 3) | Distributional, context-dependent | Curate a domain **loanword-preserve lexicon** (BFSI/insurance terms) + few-shot exemplars; RLHF/preference-tune on "did the reply keep the caller's English terms?" |
| **Faithful entity readback across scripts** | Numerals/IDs/names cross script boundary | Post-ASR **entity validator** (regex + checksum for IDs, amount parser) + TTS rule-based numeral/alphanumeric expansion; readback-confirm critical entities. |
| **Emotional warmth in the matrix language** | Generic TTS sounds cold | Style-conditioned TTS (Bulbul V3 styles) + persona prompt with Indian fillers; A/B on CSAT/"felt human" survey. |

**Net:** the 2026 stack matches the human on micro-steps 1–6, 9, 11 for **standard Hindi + English + Hinglish**. It is NOT yet at human parity on **7 (deep regional dialect), 8 (graceful repair), 12 (live drift)**. All three are closable with **data + orchestration engineering**, not new science — which is exactly why this is a high-readiness automation target *within its competence band*.

---

## 7. HITL trigger — when a human MUST take over

This step is **not independently escalatable** — it's a capability, not a task. But these conditions force human handoff (to a same-language agent, per RBI call-center routing norms):

1. **Persistent low ASR confidence** across 3+ turns after a language-offer (repair failed) → caller is on a dialect/accent the model can't track.
2. **Unsupported language** detected (e.g., the agent supports Hindi/En/Tamil/Telugu and the caller is in Assamese/Bhojpuri beyond the trained set).
3. **Compliance-critical disclosure** where the agent cannot confirm the caller understands the language (DPDP "preferred language" risk) — escalate rather than risk an unintelligible consent.
4. **Repeated entity-readback mismatch** on a money/ID field across the language boundary (caller corrects ≥2×).
5. **Emotional escalation** compounded by language frustration ("aapko meri baat samajh nahi aa rahi") → human empathy + language match.

Route to: agent fluent in detected language (RBI: call centers must offer local-language support; staff pass a Local Language Proficiency Test — [PIB/RBI, 2026](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2155543)).

---

## 8. Automation readiness: **7 / 10**

**Why 7, not higher:** For **standard Hindi + English + Hinglish on clean-to-moderate telephony**, the 2026 stack (Saaras V3 + Sarvam-M + Bulbul V3, all code-switch-native) handles micro-steps 1–6, 9–11 at near-human quality with low latency — this band is essentially shippable. Code-switch is handled at the *model* level, removing the brittle LID-router class of failures.

**Why not 9–10:** (a) **Dialect cliff** — 20–30% WER on Bhojpuri/Marwari and a −10–20% drop outside the Delhi-Mumbai corridor; (b) **switch-point hallucination on critical entities** (money/IDs) is still real and high-stakes in BFSI; (c) **graceful repair + live drift** are under-engineered in most deployments; (d) **compliance-language gating** must be deterministic, not model-trusted. These keep it short of "fully replace the human with high confidence" outside its core competence band.

**Verdict:** ship as primary for Hindi/En/Hinglish core; HITL fallback for dialect/unsupported/compliance-critical.

---

## 9. Build spec

**What to implement**
1. **End-to-end code-switch-native ASR** (Saaras V3 primary; Gladia Solaria-1 or Gnani as fallback/AB). Streaming, per-segment language tags + confidence. NO utterance-level LID router.
2. **Language-profile tracker** (orchestrator state): `matrix_lang` = EWMA of recent segment langs; `register` (formal/casual); `dialect_hint`; `confidence_trend`. Updated every turn.
3. **Loanword-preserve + romanization-aware NLU/dialogue** on a code-mix-native LLM (Sarvam-M / Indic-adapted GPT-class) with a BFSI/insurance loanword lexicon and few-shot Hinglish exemplars.
4. **Romanized-Hindi normalizer** (transliteration) on the chat path before NLU.
5. **Entity validator** post-ASR: regex + checksums for order/policy IDs, amount parser; readback-confirm critical entities.
6. **Deterministic compliance-template selector**: per-language pre-approved disclosure scripts, chosen by `matrix_lang`; never free-generated.
7. **Code-mix-native TTS** (Bulbul V3) with rule-based numeral/alphanumeric/abbrev expansion + style conditioning for warmth/register.
8. **Repair + drift dialogue states**: confidence-gated language-offer; EWMA-driven drift.

**Data needed**
- Real Hindi-English code-mixed **telephony** audio (noisy, 8 kHz), labeled at switch points (HiACC, COMI-LINGUA seed; collect own from production with consent).
- **Per-dialect** sets (Bhojpuri, Marwari, Chhattisgarhi, Mumbai-Hindi) using LAHAJA accent taxonomy for the dialect WER grid.
- **Romanized Hinglish chat** corpus with spelling variants (arXiv 2511.22769 dataset).
- Domain **loanword-preserve lexicon** (BFSI/insurance terms).
- Per-language **approved compliance scripts** (legal-reviewed).

**Eval metrics that gate ship**
- **Switch-point WER** ≤ target (window of ±2–3 words). Gate, e.g., ≤ 15% on core Hi-En; track to parity with 11–14% Indic baseline ([Gnani, 2026](https://www.gnani.ai/resources/blogs/blog-code-switching-speech-recognition-hinglish-asr)).
- **Per-language WER** reported separately (no blended scores).
- **Hallucination rate at transitions** ≤ threshold (target near-zero on entity tokens).
- **Critical-entity accuracy** (amounts/IDs across script boundary) ≥ 99% (with validator).
- **Per-dialect WER grid** — no dialect > 25%; flag any > 20% for HITL routing.
- **Loanword-preserve rate** ≥ 95% (reply keeps caller's English terms).
- **Register-match / "felt human" CSAT** in A/B.
- **End-to-end first-audio latency** ≤ ~800 ms (ASR TTFT <150 ms + LLM + TTS <250 ms).
- **Compliance-language correctness** = 100% (deterministic templates → must be exact).

**Ship gate:** all of the above met on the core Hi/En/Hinglish band; dialect/unsupported/compliance-critical paths wired to HITL.

---

## 10. India specifics (Hinglish / regional / regulatory)

**Linguistic**
- Code-switching is the **default**, 2–3 languages per sentence ([Cyfuture, 2026](https://cyfuture.ai/blog/multilingual-chatbots-india)); design for it as the base case.
- **Romanized Hinglish** dominates chat (56.3% preference post-2020) — Roman-script normalization is mandatory, not optional ([arXiv 2511.22769, 2025](https://www.arxiv.org/pdf/2511.22769)).
- **Respectful register is non-negotiable**: "aap/aapka", "ji", never "tu" — critical with elderly/rural BFSI customers.
- **Dialect reality**: Mumbai Hindi (Marathi loanwords), Lucknow Hindi (Urdu-influenced, formal), Bihar Hindi (Bhojpuri-blended); Bhojpuri alone 50M+ speakers ([CXOToday, 2026](https://cxotoday.com/media-coverage/global-speech-ai-struggles-to-understand-india-new-national-benchmark-voice-of-india-reveals/)).
- Keep BFSI terms (EMI, KYC, OTP, NEFT, account, balance) in English — that's how customers say them.

**Regulatory**
- **RBI**: every bank must offer services in **regional language + Hindi + English**, including at **call centres**; frontline staff pass a **Local Language Proficiency Test**; **Key Fact Statement (KFS)** must be "in a language understood by the borrower" ([Trak.in](https://trak.in/stories/every-bank-must-offer-services-in-regional-languages-hindi-english-rbi/); [PIB/RBI, 2026](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2155543); [Leegality KFS](https://www.leegality.com/blog/kfs-in-local-language)). → The agent MUST be able to deliver disclosures and KFS-type facts in the customer's language, and route to a same-language human if it can't.
- **DPDP (2023)**: consent notices "in plain language, in the customer's **preferred language** where reasonable"; maintain audit trail of who consented, to what, on what notice version — **language selection is part of the defensible record** ([Caller Digital regulatory map, 2026](https://www.caller.digital/blog/voice-ai-india-regulatory-map-2026)). → Log `matrix_lang` + notice-language per consent event.
- **IRDAI**: emphasis on accurate, clear disclosure of coverage/exclusions/premium aligned to policy document — clarity in the customer's language is implied ([Caller Digital, 2026](https://www.caller.digital/blog/voice-ai-india-regulatory-map-2026)).
- **Telephony reality**: 8 kHz noisy lines → benchmark on telephony audio, not studio; global models 14–16% vs Indic 11–14% WER on this ([Gnani, 2026](https://www.gnani.ai/resources/blogs/blog-code-switching-speech-recognition-hinglish-asr)).

---

## Sources
- [Gladia — Code Switching in Speech Recognition (2026)](https://www.gladia.io/blog/what-is-code-switching-in-speech-recognition)
- [Sarvam — Saaras V3 ASR (2026)](https://www.sarvam.ai/blogs/asr)
- [Sarvam — Bulbul V3 TTS (2026)](https://www.sarvam.ai/blogs/bulbul-v3)
- [Sarvam — Bulbul V3 / OpenClaw integration (dev.to, 2026)](https://dev.to/agent_paaru/indian-language-tts-for-your-ai-agent-integrating-sarvamai-bulbul-v3-with-openclaw-1fdg)
- [Gnani — Why ASR Fails on Hinglish (2026)](https://www.gnani.ai/resources/blogs/blog-code-switching-speech-recognition-hinglish-asr)
- [Caller Digital — Multilingual Voice AI India 2026](https://caller.digital/blog/voice-ai-india-regulatory-map-2026)
- [Caller Digital — Voice AI India Regulatory Map 2026](https://www.caller.digital/blog/voice-ai-india-regulatory-map-2026)
- [Cyfuture — Multilingual Chatbots India (2026)](https://cyfuture.ai/blog/multilingual-chatbots-india)
- [CXOToday — Voice of India benchmark (2026)](https://cxotoday.com/media-coverage/global-speech-ai-struggles-to-understand-india-new-national-benchmark-voice-of-india-reveals/)
- [AutoInterviewAI — Vernacular Voice Agents 2026](https://www.autointerviewai.com/blog/vernacular-ai-voice-agents-india-hinglish-code-switching-2026)
- [JMIR — Code-Mixed Intent w/ LLMs incl. Sarvam-M (2026)](https://www.jmir.org/2026/1/e86545)
- [arXiv 2511.22769 — Romanized Hindi/Bengali modeling (2025)](https://www.arxiv.org/pdf/2511.22769)
- [arXiv 2503.21670 — COMI-LINGUA](https://arxiv.org/pdf/2503.21670)
- [arXiv 2408.11440 — LAHAJA multi-accent Hindi ASR](https://arxiv.org/pdf/2408.11440)
- [ScienceDirect — HiACC Hinglish corpus (2025)](https://www.sciencedirect.com/science/article/pii/S2352340925006109)
- [Deepgram — Alphanumeric Pronunciation TTS Benchmark 2026](https://deepgram.com/learn/alphanumeric-pronunciation-tts-quality-benchmark)
- [Trak.in — RBI regional language mandate](https://trak.in/stories/every-bank-must-offer-services-in-regional-languages-hindi-english-rbi/)
- [PIB/RBI — Multilingual customer communication (2026)](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2155543)
- [Leegality — KFS in local language](https://www.leegality.com/blog/kfs-in-local-language)
- [Augmen AI Labs — STT 22 Indian languages](https://augmen.io/labs-stt.html)
- [Haptik — Voice AI Agents for Indian Languages 2026](https://www.haptik.ai/blog/voice-ai-agents-for-indian-languages)
- [Bolna — Multilingual Voice AI (2025)](https://blog.bolna.ai/multilingual-voice-ai/)

---
*Draft research dossier for build. Cited where possible; [estimate] flagged inline where no direct source.*
