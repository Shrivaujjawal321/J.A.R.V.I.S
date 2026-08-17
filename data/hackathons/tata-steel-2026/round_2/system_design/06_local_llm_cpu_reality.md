# Local LLM on CPU-Only Laptop — 2026 Reality Check
## Tata Steel R2 — Maintenance Wizard Decision Brief

**Authored:** 2026-06-09 · **Constraint:** CPU-only laptop, no paid API key, Claude Max subscription only.
**Purpose:** Web-verified hard numbers for deciding whether a local LLM (via Ollama / llama.cpp) is viable as primary or fallback in the Maintenance Wizard demo, and how it compares to the measured 11–12 s subscription-subprocess path.

---

## TL;DR Decision

**Run Ollama's `qwen2.5:3b` (or the fine-tuned `steel-wizard` GGUF) as the L3 fallback, not as the primary.** On a modern x86 laptop CPU a 3B Q4_K_M model delivers **~6–12 tok/s**, which is a **300-token answer in ~25–50 s** — slower than the subscription (11–12 s per single call), but rate-limit-immune. For the recorded demo this distinction is irrelevant because the demo is 100% cache-served (L0). Local LLM is the "never breaks" safety net; subscription is the quality primary when it isn't rate-limited.

The fine-tuned GGUF earns **extra merit from the judges (PS §6.1, FR1)** simply by existing and being cited in the demo. It does not need to be the fastest path.

---

## 1. Best Small Models for Local Agentic + RAG Synthesis (2026)

| Model | Params | Q4_K_M GGUF | Notes |
|---|---|---|---|
| **Qwen2.5-3B-Instruct** | 3B | ~2.1 GB | Best quality/size at 3B; native JSON mode; tool-call training in-family; our fine-tune base |
| **Phi-3.5-mini-Instruct** | 3.8B | ~2.3 GB | Strong reasoning; Q4_K_M ~2.3 GB; "near-8B quality in 4 GB RAM" per LocalAIMaster 2026 |
| **Llama-3.2-3B-Instruct** | 3B | ~2.1 GB | Fast decode on llama.cpp; weaker JSON compliance than Qwen2.5 (47–57% parse rate vs 74% for Qwen2.5-7B) |
| **IBM Granite-3.2-3B-Instruct** | 3B | ~2.1 GB | Enterprise/industry-tuned; available on Ollama; on-device deployment target per IBM docs; no published x86 CPU tok/s |
| **Mistral-7B-Instruct-v0.3** | 7B | ~4.1 GB | Higher ROUGE-L quality (0.509 vs ~0.47 for 3B class); but 2× RAM and 2× slower on CPU |

**Recommendation for this build:** `Qwen2.5-3B-Instruct` Q4_K_M. It is already the fine-tune base, already in the `03_local_no_api_stack.md` plan, has the best JSON structured output in its size class, and the GGUF is ~2.1 GB — fits the 4.3 GB total RAM budget with headroom.

---

## 2. GGUF Quantization + Serving: RAM Footprint + CPU tok/s

### Quantization sweet-spot for CPU

| Quant | Quality drop | Size (3B) | RAM RSS | Recommended? |
|---|---|---|---|---|
| Q2_K | Noticeable | ~1.2 GB | ~1.6 GB | No — too lossy for synthesis |
| Q4_K_M | Minimal | ~2.1 GB | ~2.8 GB | **Yes — the sweet spot** |
| Q5_K_M | Tiny vs Q4 | ~2.5 GB | ~3.2 GB | Only if RAM is 16 GB+ |
| Q8_0 | Reference quality | ~3.2 GB | ~4.1 GB | Slower, eats into budget |

### CPU tok/s reality (x86 Intel/AMD laptop, no GPU)

Across 2025–2026 community benchmarks (PromptQuorum, LocalAIMaster, Markaicode, AscentCore) the consensus for a **modern 8-core x86 CPU (Intel i7-12th gen class or AMD Ryzen 7 5800X class)** at Q4_K_M:

| Model size | CPU tok/s (Q4_K_M) | RAM RSS | 300-token answer wall-clock |
|---|---|---|---|
| 1B (e.g. Llama-3.2-1B) | 25–45 tok/s | ~0.9 GB | ~7–12 s |
| **3B (Qwen2.5-3B)** | **6–12 tok/s** | **~2.8 GB** | **~25–50 s** |
| 7B (Mistral-7B) | 3–7 tok/s | ~5.1 GB | ~43–100 s |
| 8B (Llama-3.1-8B) | 5–14 tok/s | ~5.1 GB | ~21–60 s |

*Source: Markaicode Ollama CPU Benchmark — Q4_K_M at 12 threads, Llama-3.1-8B measured 14.2 tok/s on high-core-count desktop; laptop CPUs typically 30–50% lower than desktop due to TDP limits. A similar-sized 3B model is proportionally faster due to smaller working set but also constrained by CPU memory bandwidth (~40–80 GB/s on x86 vs 400+ GB/s GPU HBM).*

**Key insight:** Apple M-series (M1/M2/M4) unified memory reaches 15–30 tok/s on 7B models and 25–45 tok/s on 3B. The data above is strictly x86. Since Boss's machine is x86 CPU-only, **6–12 tok/s for Qwen2.5-3B is the honest planning number.**

### Ollama vs llama-cpp-python (in-process)

| Approach | Overhead | Integration |
|---|---|---|
| `ollama serve` + REST | ~150–200 MB daemon RSS; REST round-trip adds ~30 ms | Simple `litellm.completion("ollama/steel-wizard")` — already in plan |
| `llama-cpp-python` in-process | No daemon; ~150 MB less RAM; direct Python API | Tighter integration but complicates Streamlit multi-process |

For this build: **Ollama is safer** for demo (daemon stays warm between calls; cold load penalty is only needed once). Pre-pull the model before the demo recording session.

---

## 3. First-Token Latency vs. the 11–12 s Subscription Call

### Measured subscription path (from MASTER_ARCHITECTURE_AND_PLAN.md)

- Single `subscription_llm()` call (Agent SDK spawning `claude` CLI subprocess): **~11.78 s end-to-end, cold**
- A cold uncached diagnosis turn (3.5 sequential LLM nodes): **~30–45 s**

### Local LLM first-token latency (Ollama, model already warm/loaded)

| Quantization | First-token latency (TTFT, model warm) | Source |
|---|---|---|
| Q4_K_M, 3B, 8-core CPU | ~350–600 ms | Markaicode benchmark (8B at 380ms; 3B lighter model → estimated slightly lower) |
| Q4_K_M, 8B, 8-core CPU | 380 ms (p50) | Markaicode CPU benchmark |
| Q8_0, 8B, 8-core CPU | 890 ms (p50) | Markaicode CPU benchmark |

**Cold model load (first call after `ollama serve` starts):**
- NVMe SSD: model loads in ~1–2 s for a 7B model; ~0.5–1 s for 3B
- HDD/slow SSD: 8–15 s load time — avoid on demo day

**Comparison summary:**

| Path | First-token delay | Full 300-token answer | Rate-limit risk |
|---|---|---|---|
| Subscription (Agent SDK subprocess) | ~10–12 s (no KV cache) | ~12–15 s (single synthesis call) | Yes — real, we've hit it |
| Local 3B Q4_K_M (Ollama, warm) | ~400–600 ms | ~25–50 s | Zero |
| Local 3B Q4_K_M (Ollama, cold load) | ~1.5–2 s | ~27–52 s | Zero |
| L0 demo cache | <10 ms | <10 ms | Zero |

**Verdict:** The local model is **faster to first token** (400 ms vs 11+ s), but **total answer time is ~2–4× longer** because the decode is throttled by RAM bandwidth. For a live judge watching a screen, a 25–50 s answer that starts typing immediately (low TTFT) is more reassuring than an 11 s black hole then sudden complete answer. This is a UX win for the local path — worth noting in the demo narrative as "fully on-device, watching it think in real time."

---

## 4. Tool-Use / Structured JSON Reliability + Hardening

### Baseline reliability of small models (AscentCore April 2026 benchmark, JSON schema compliance)

| Model | JSON parse rate | Notes |
|---|---|---|
| Llama-3.1-8B Q8_0 | 95.7% | Best in benchmark; near GPT-4 for simple schemas |
| Gemma-3-4B Q4_K_M | 87.0% | Second tier |
| Qwen-2.5-7B Q4_K_M | 73.9% | 7B Qwen; 3B likely lower (~60–65% extrapolated) |
| Llama-3.2-3B | 47–57% | Unreliable; not recommended for structured tasks |
| SmolLM2-1.7B | 26.1% | Unusable |

**Qwen2.5-1.5B-Instruct BFCL scores (proxy for Qwen2.5-3B):** Non-Live Simple AST 89%, Multiple AST 86%, Parallel AST 70%, Parallel Multiple AST 66.5%. The 3B will perform somewhat better given more capacity; fine-tuned `steel-wizard` should be meaningfully better on maintenance-domain schemas after SFT.

### Hardening techniques (must-use for the Maintenance Wizard)

**1. Ollama `format: "json"` flag** — forces constrained decoding at the sampler level. All `ollama.chat()` calls in the Ollama path should pass `format="json"`. Zero code overhead; this alone lifts parse rate by ~10–15pp on borderline models.

**2. llama.cpp GBNF grammars** — if using `llama-cpp-python` directly: define a JSON schema as GBNF and pass it to `llama_cpp.Llama()` as `grammar`. The sampler masks any token not valid per current grammar state. Note: does **not** guarantee semantic correctness, only syntactic validity. Known edge case: model can run out of tokens before closing all JSON brackets — set `max_tokens` conservatively.

**3. `instructor` library** — wraps any OpenAI-compatible API (Ollama exposes one). `instructor.patch(openai.OpenAI(base_url="http://localhost:11434/v1"))` + Pydantic model → auto-retry on parse failure (default 3 retries). Already in `requirements.txt`. Use for all 6 agent tool-call schemas (e.g. `DiagnosisOutput`, `RCAOutput`, `WorkOrderPlan`).

**4. Prompt-level schema echo** — unlike GBNF, `format: "json"` does not inject the schema into the prompt. Add the JSON schema as a compact YAML/JSON literal in the system prompt. The model then understands the expected keys, not just the syntax rule.

**5. Validation layer** — `nodes.py` already uses Pydantic for output validation. Keep this; on `ValidationError`, fall through to the deterministic template (current L4 in the four-level ladder).

**Combined hardening stack for local LLM:**
```
Ollama format=json
  + instructor retry (3 attempts)
  + Pydantic validation
  + deterministic fallback template
```
This stack should achieve >90% valid structured output on Qwen2.5-3B for maintenance-domain schemas, acceptable for the L3 fallback role.

---

## 5. Demo-Day Risks: Pre-Pull, RAM, Thermal Throttling

### Pre-pull is mandatory

Ollama downloads models lazily on first call. On a demo recording session start, if the model is not pre-pulled, the first call triggers a network download (2.1 GB for Qwen2.5-3B Q4_K_M). This kills the demo. **Run `ollama pull qwen2.5:3b` (or `ollama create steel-wizard -f Modelfile`) at least 24 hours before the demo and verify with `ollama list`.**

### RAM budget and swap risk

| Total laptop RAM | Risk |
|---|---|
| 8 GB | Safe: 4.3 GB total system RSS (per `03_local_no_api_stack.md §10`) + ~1–2 GB OS overhead → ~6.3 GB. 1.7 GB headroom. No swap expected. |
| 4 GB | DANGER: Model alone (2.8 GB) + OS (1.5 GB) = 4.3 GB → immediate swap. Inference drops to **1–5 tok/s**. Fan screams. Do NOT run Ollama on 4 GB. |
| 16 GB | Comfortable: Arize Phoenix traces add ~300 MB. Full stack + browser recording software fits easily. |

**Swap risk rule of thumb (2026 sources):** Inference speed collapses when model RAM exceeds ~60% of total system RAM. On 8 GB, 2.8 GB model = 35% → safe. On 4 GB, same model = 70% → swap, 5–10× slowdown.

### Thermal throttling

Sustained LLM inference on a laptop CPU is equivalent to full-load video encoding. Benchmarks (PromptQuorum 2026) show thermal throttling emerges after **10–15 minutes of continuous generation, reducing tok/s by 20–40%**.

For a recorded demo:
- Demo recording total length: ~4 minutes (per `05_demo_and_judging_strategy.md`)
- All scripted beats are cache-served (0 live LLM calls) — **no sustained inference during the recording**
- Thermal risk rating: **Negligible** because L0 cache makes the demo zero-LLM

For live judge Q&A (if any post-demo):
- Each L3 Ollama call is a discrete burst, not sustained
- Allow 60 s cooldown between calls
- Use a laptop stand (2–3 cm clearance) → extends time-to-throttle from 10 to 20+ min
- Plug into AC; set CPU power plan to "performance" (avoids turbo-boost-then-throttle cycle)

### Ollama daemon stability

- Ollama 0.18+ is stable on Linux; no known crash issues on sustained use
- Model stays hot in RAM between calls (no reload penalty after first call)
- If Ollama crashes, `instructor` fallback → subscription call → deterministic template (three levels of safety)
- **Start Ollama before launching the demo**, not on-demand: `ollama serve &` then `sleep 5` then `ollama run steel-wizard "warmup"` before the FastAPI server starts

---

## 6. Architecture Integration Summary (the four-level ladder, re-confirmed)

```
L0  data/demo_cache.json          → sub-ms    0 LLM calls  ← RECORDED DEMO (all 5 beats)
L1  Semantic SQLite cache         → <50ms     0 LLM calls  ← Live pre-warmed queries
L2  subscription_llm() via SDK   → ~10-12s   1 Claude call ← Quality primary (online, no rate limit)
L3  Ollama / steel-wizard GGUF   → TTFT~500ms, 300-tok~30-50s ← Rate-limit safety net
(L4  Deterministic template       → <1ms      0 LLM calls  ← Structural fallback, always correct)
```

The local LLM (L3) fills the gap where:
- The subscription is rate-limited (we have hit limits mid-build)
- Demo is live and the judge asks an off-script question
- Network is unavailable

It does NOT replace L0/L1/L2. It is the floor that prevents breakage.

---

## 7. Judging Angle: Fine-Tune as Explicit Merit (PS §6.1, FR1)

The problem statement awards **extra merit for creating a domain-specific fine-tuned model**. The `finetune/` kit (Qwen2.5-3B QLoRA, 969 SFT examples, Colab T4, GGUF export) directly earns this. Citing it in the demo ("we fine-tuned a 3B model on our maintenance corpus — it's your local fallback, no API key, zero data leaves your plant") hits:

- FR1: LLM/SLM reasoning + domain fine-tune merit tick
- FR4: Explainable + traceable (fine-tuned model = deterministic weights, auditable training data, no cloud dependency)
- Ops quality "doesn't break" (L3 = no rate-limit failure mode)
- Ops quality "fast" (TTFT < 1 s vs 11–12 s black-hole subscription call, even if total answer is slower)

---

## Sources

- [PromptQuorum — Best Ollama Models Without GPU 2026](https://www.promptquorum.com/prompt-bites/best-ollama-models-cpu-only)
- [PromptQuorum — Run Local LLMs on a Laptop: RAM, Speed & Thermals 2026](https://www.promptquorum.com/local-llms/local-llm-on-laptop)
- [Markaicode — Ollama CPU Benchmark (Q4_K_M threads vs tok/s)](https://markaicode.com/benchmarks/tool-cpu-benchmark/)
- [LocalAIMaster — Phi-3.5 Mini: Best AI for 4GB RAM Laptops](https://localaimaster.com/models/phi-3-5-mini)
- [LocalAIMaster — Ollama System Requirements 2026](https://localaimaster.com/blog/ollama-system-requirements)
- [AscentCore — Small LLM Performance Benchmark April 2026](https://ascentcore.com/2026/04/01/small-llm-performance-benchmark/)
- [DEV.to — Local AI in 2026: Ollama Benchmarks, $0 Inference](https://dev.to/pooyagolchian/local-ai-in-2026-ollama-benchmarks-0-inference-and-the-end-of-per-token-pricing-32e7)
- [Qwen2.5 Speed Benchmark — official docs (GPU; CPU not published)](https://qwen.readthedocs.io/en/v2.5/benchmark/speed_benchmark.html)
- [Qwen BFCL / function-calling docs](https://qwen.readthedocs.io/en/latest/framework/function_call.html)
- [llama.cpp Grammar + Structured Output (DeepWiki)](https://deepwiki.com/ggml-org/llama.cpp/8.1-grammar-and-structured-output)
- [GBNF Grammar README — ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md)
- [IBM Granite 3.2 announcement](https://www.ibm.com/new/announcements/ibm-granite-3-2-open-source-reasoning-and-vision)
- [Ollama IBM Granite 3.0 blog](https://ollama.com/blog/ibm-granite)
