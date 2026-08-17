# Local / No-API Component Stack
## Tata Steel R2 — Maintenance Wizard
**Authored:** 2026-06-09 · **Constraint:** zero paid API keys, CPU-only laptop, demo must not die on rate limit

---

## Hard Constraint Summary

Boss has **only** a Claude Max subscription (OAuth token `CLAUDE_CODE_OAUTH_TOKEN`).
Every LLM call goes through the proven subscription path:
`claude_agent_sdk.query(options)` / `claude -p <prompt>` subprocess with the token set.
**No `GEMINI_API_KEY`, no `ANTHROPIC_API_KEY`, no `OPENAI_API_KEY` are used anywhere.**
The existing `wizard/core/config.py` fields `gemini_api_key` / `anthropic_api_key` must be left empty;
`llm_provider` must be switched to `"ollama"` (local fallback) as the *safe* demo path, with the
subscription Claude as the *best-effort* primary (see §7 below).

---

## 1. Embeddings — `sentence-transformers` (local, CPU, no key)

| Item | Value |
|---|---|
| **Library** | `sentence-transformers>=3.0` |
| **Model** | `BAAI/bge-small-en-v1.5` (HuggingFace download once, cached to `~/.cache/huggingface/`) |
| **Backend** | ONNX (`sentence-transformers[onnx]`) — no PyTorch at inference time, ~3× faster CPU |
| **Dimension** | 384 |
| **RAM** | ~90 MB model weights |
| **Already used by** | Jarvis's episodic memory (`EpisodicMemory` class, `scripts/episodic_memory.py`) + `data/chroma/` — proven CPU-only |
| **Config key** | `settings.embedding_model = "BAAI/bge-small-en-v1.5"` · `settings.embedding_dim = 384` |

Alternative if bge-small is too slow on demo hardware: `BAAI/bge-micro-v2` (128-dim, 40 MB, faster).
All-MiniLM-L6-v2 is the Mem0 internal default — leave it alone, Mem0 isolation means it doesn't conflict.

---

## 2. Reranker — FlashRank (local ONNX, no key)

| Item | Value |
|---|---|
| **Library** | `flashrank>=0.2` |
| **Model** | `ms-marco-MiniLM-L-12-v2` (ONNX, bundled with flashrank on first use) |
| **No PyTorch** | FlashRank uses ONNX Runtime only — zero GPU dependency |
| **Latency** | ~8-12 ms for top-20 re-rank on CPU |
| **Usage** | After LanceDB retrieves top-20 hybrid candidates, FlashRank re-scores and returns top-5 for LLM citation |
| **Config key** | `settings.reranker_model = "ms-marco-MiniLM-L-12-v2"` |

---

## 3. Vector DB — LanceDB (local, embedded, no key)

| Item | Value |
|---|---|
| **Library** | `lancedb>=0.20` |
| **Storage** | `data/lancedb/` on-disk (Arrow/Lance columnar files) — pure Python, no server process |
| **Hybrid search** | Native dense (ANN) + BM25 full-text (Tantivy under the hood) + SQL pre-filter in one call |
| **Why LanceDB over ChromaDB** | Native hybrid eliminates the `rank_bm25` dep; SQL filter for `equipment_id` / `doc_type` before ANN is critical for scoped RAG |
| **Corpus loaded** | 13 equipment manuals + 13 SOPs + 25 RCA reports + `breakdown_summaries.md` + `oem_service_bulletins.md` + `shift_handover_notes.md` + domain research from `research/domain/` and `research/machinery/` (20 files) → chunked to ~512 tokens by `pymupdf4llm` + `MarkdownHeaderSplitter` + recursive splitter with 64-token overlap |
| **Metadata indexed** | `doc_type`, `equipment_class`, `asset_id`, `standard_ref`, `chunk_id` — enables pre-filter e.g. `WHERE equipment_class='eaf_hydraulics'` |
| **Also used** | Mem0 / conversational memory is on a separate **ChromaDB** instance at `data/chromadb/` (already in config; isolated) |

---

## 4. RAG Pipeline — fully local retrieval, LLM only for synthesis

```
Query
  ↓
[optional HyDE] → bge-small embed hypothetical doc → dense probe
  ↓
LanceDB hybrid search  (dense + BM25 + SQL equipment filter)  → top-20 chunks
  ↓
FlashRank rerank  (ONNX, CPU)                                → top-5 chunks
  ↓
NLI entailment gate  (cross-encoder/nli-deberta-v3-small, CPU) → validate grounded claims
  ↓
Build citation block [1]...[N]
  ↓
Subscription LLM (synthesis only, ~200 token context window used for docs)
```

**NLI model:** `cross-encoder/nli-deberta-v3-small` via `sentence-transformers` cross-encoder API.
No API key. ~60 MB model. Validates that LLM answer is entailed by retrieved chunks — guards hallucination.

**HyDE toggle:** `settings.rag_hyde_enabled = True` (default). Uses ONE cheap LLM call to generate a
hypothetical document, then embeds that for a better dense query. This is a smart use of the subscription:
one small generation improves retrieval quality without wasting tokens on synthesis.

**Cache layer:** `data/demo_cache.json` stores pre-run golden responses for the 5 scripted demo queries.
On demo day `WIZARD_DEMO_CACHE=1` env var → every recognised query returns from cache instantly.
Rate limit cannot kill the demo. Cache is Tier-2 auto-populated during dev using `scripts/prebake_demo_cache.py`.

---

## 5. ML for Anomaly / RUL / Fault Prediction — all local, all CPU, all joblib-serialised

All three models are **offline-trained once**, serialised to `data/models/`, loaded at startup.
No re-training during demo. No API call. No GPU.

### 5a. RUL — `lifelines` WeibullAFTFitter

| Item | Value |
|---|---|
| **Library** | `lifelines>=0.30` |
| **Training data** | NASA C-MAPSS FD001 + FD003 (public domain, ~21k rows); piecewise-linear RUL cap=125 cycles; per-engine z-score normalise |
| **Output** | Median RUL estimate (days equivalent) + 95% CI; `rul_critical_days=14` → CRITICAL alert |
| **Complement** | Degradation Index (exponential smoothed vibration + temperature z-scores) from flagship dataset `raw_sensor_timeseries.csv` feeds as covariates |
| **Serialisation** | `joblib.dump(model, 'data/models/rul_weibull.joblib')` |
| **CPU RAM** | <20 MB |

### 5b. Anomaly — IsolationForest + LSTM-AE + River HST

| Item | Value |
|---|---|
| **Primary** | `sklearn.ensemble.IsolationForest` (contamination=0.027, matching dataset's 2.7% imbalance) |
| **Sequence model** | LSTM-AE trained with `torch 2.3.1 cpu` on 24h sliding windows of flagship `by_equipment/*.csv` dense tables (0% null, 8,736 rows × 15 equipment) |
| **Online / streaming** | `river 0.21` Half-Space Trees (`river.anomaly.HalfSpaceTrees`) for the 5-second APScheduler tick — no retraining, pure online update |
| **Ensemble score** | `0.5 × IF_score + 0.3 × LSTM_AE_recon_error + 0.2 × HST_score` → `settings.anomaly_score_threshold = 0.65` |
| **Explainability** | `shap 0.46` TreeExplainer on IsolationForest → top-3 contributing sensor tags per alert |
| **Serialisation** | `data/models/isolation_forest.joblib`, `data/models/lstm_ae.pt` (state_dict) |

### 5c. Failure Prediction — LightGBM 4-class ordinal

| Item | Value |
|---|---|
| **Library** | `lightgbm>=4.6` |
| **Training data** | AI4I 2020 (UCI, CC BY 4.0, 10k rows); 4 failure classes (TWF/HDF/PWF/OSF) mapped to steel fault taxonomy; cosmetic K→°C conversion via `dataset_framing.py` |
| **Extra features** | `tsfresh 0.21` rolling statistics (window=24h) from flagship sensor summaries |
| **Calibration** | Isotonic regression (`sklearn.calibration.CalibratedClassifierCV`) for well-calibrated probabilities; `failure_prob_threshold=0.70` |
| **Output** | 4-class probability vector + SHAP feature importances (TreeExplainer, CPU) |
| **Serialisation** | `data/models/lgbm_fault.joblib` |

**Combined flow:** IsolationForest anomaly score + LightGBM failure_prob + WeibullAFT RUL p50 → WRPS
4-factor risk score → risk tier (LOW/MED/HIGH/CRITICAL) — all pure Python, no LLM needed for this path.

---

## 6. Optional Domain Fine-Tuned SLM — Bonus Merit Path

This is the explicit "extra merit for creating/fine-tuning a domain-specific model" hook in PS §6.1.

### Training (Colab T4 — one-time, not on demo laptop)

| Item | Value |
|---|---|
| **Base model** | `Qwen/Qwen2.5-3B-Instruct` (3B params, fits T4 16 GB with QLoRA) |
| **Framework** | `unsloth 2025.12` + `trl` SFTTrainer + `bitsandbytes` 4-bit QLoRA |
| **Training corpus** | 500 synthetic knowledge documents + 260 QA pairs from `user_interaction/` (NL queries + multi-turn conversations + troubleshooting prompts) — formatted as `<instruction>/<response>` pairs |
| **LoRA config** | rank=16, alpha=32, target=`q_proj,v_proj`, epochs=3, batch=4, lr=2e-4 |
| **Output** | GGUF Q4_K_M quantised model → `data/models/qwen2.5-3b-steel-q4.gguf` (~2.1 GB) |
| **Training time** | ~45 min on Colab T4 (free tier) |

### Local Inference (laptop, CPU, no key)

| Item | Value |
|---|---|
| **Server** | `ollama 0.18` — `ollama create steel-wizard -f Modelfile` (Modelfile points to the GGUF) |
| **Alternatively** | `llama-cpp-python>=0.2.90` for in-process inference without Ollama daemon |
| **RAM** | ~2.8 GB RSS for Q4_K_M 3B on CPU |
| **Latency** | ~4-8 tok/s on modern laptop CPU — acceptable for non-demo synthesis tasks |
| **Integration** | LiteLLM model string `"ollama/steel-wizard"` or `settings.llm_model_fallback = "ollama/steel-wizard"` |
| **Slot in architecture** | Replaces the subscription LLM for diagnosis + recommendation agents when rate limits are hit; also the "domain fine-tune demo" slide proof |

**Gate:** ship the fine-tuned model **only if** it scores ≥ base Qwen2.5-3B on a 200-example held-out
eval set drawn from `user_interaction/multiturn_conversations.jsonl`. Metric: exact-match + BERTScore F1 > 0.82.
If it doesn't beat base, demo uses base `ollama/qwen2.5:3b` — no regression risk.

---

## 7. Subscription LLM Integration — proven pattern, rate-limit-safe

The existing `wizard/core/config.py` defaults to `gemini_api_key` — this must be replaced.
The **proven no-key pattern** (same as `jarvis_core/daemon.py` and `dataforge/api/scorer/agent.py`):

```python
# wizard/core/llm_client.py  (add this module)
import os, subprocess, asyncio
from pathlib import Path

def _load_oauth_token() -> str | None:
    tok = os.getenv("CLAUDE_CODE_OAUTH_TOKEN")
    if tok:
        return tok
    # fallback: read from Jarvis repo .env
    env_path = Path.home() / "Documents/J.A.R.V.I.S./.env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("CLAUDE_CODE_OAUTH_TOKEN="):
                tok = line.split("=", 1)[1].strip().strip('"')
                os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = tok
                return tok
    return None

async def subscription_call(prompt: str, timeout_s: int = 30) -> str | None:
    """Call Claude via Max subscription. No API key. Falls back to None."""
    tok = _load_oauth_token()
    if not tok:
        return None
    try:
        from claude_agent_sdk import ClaudeAgentOptions, query
        options = ClaudeAgentOptions(system_prompt="You are a maintenance engineering assistant.")
        result = await asyncio.wait_for(
            query(prompt=prompt, options=options), timeout=timeout_s
        )
        return "".join(m.content[0].text for m in result if m.content)
    except Exception:
        return None  # caller falls through to Ollama
```

**LiteLLM proxy approach (alternative):** `litellm.completion(model="claude-3-5-sonnet-20241022", api_key=token)` — LiteLLM accepts OAuth tokens for Claude. Simpler one-liner but less control over retries.

**Rate-limit defence strategy:**
1. `pybreaker` circuit breaker wraps all subscription calls (fail_max=5, reset=60s) — already in `requirements.txt`
2. `tenacity` retry with exponential backoff (already in requirements)
3. Demo cache (`data/demo_cache.json`) — pre-baked golden responses for all 5 scripted demo beats
4. Ollama fallback (`ollama/qwen2.5:3b` or `ollama/steel-wizard`) for every agent call — LiteLLM gateway makes swap transparent
5. Demo mode env var `WIZARD_DEMO_CACHE=1` → zero LLM calls during the judged recording

**Config change required in `.env`:**
```
LLM_PROVIDER=ollama
LLM_MODEL_PRIMARY=ollama/steel-wizard   # or ollama/qwen2.5:3b if fine-tune not ready
LLM_MODEL_FALLBACK=ollama/qwen2.5:3b
GEMINI_API_KEY=                          # intentionally blank
ANTHROPIC_API_KEY=                       # intentionally blank
# Subscription path for best-effort (dev + non-critical agents only):
# CLAUDE_CODE_OAUTH_TOKEN loaded from Jarvis .env automatically
```

---

## 8. Real-Time Alerting + Feedback Loop Storage — local SQLite + APScheduler

| Item | Value |
|---|---|
| **Alert engine** | `APScheduler 3.11` `BackgroundScheduler` — 5-second tick (`settings.alert_poll_interval_seconds = 5`) runs the proactive evaluator (anomaly + RUL + LightGBM on latest sensor slice) |
| **Alert store** | `wizard.db` (SQLite WAL mode, zero-install) via `SQLModel` — tables: `AlertEvent`, `FeedbackRecord`, `SessionCheckpoint`, `WorkOrder` |
| **Dedup / cooldown** | In-process `dict[asset_id + alert_type → last_fired_ts]` with `settings.alert_cooldown_seconds = 300` — prevents alert storm on demo |
| **SSE fan-out** | FastAPI native SSE (`fastapi>=0.135`) streams `AlertEvent` JSON to Streamlit `st.fragment(run_every=5)` in real time — no WebSocket, no extra server |
| **Feedback loop** | 3-track: (1) `FeedbackRecord` JSONL written to `data/feedback.jsonl` for RAG re-rank weight bump (thumbs-up → boost source cosine similarity in LanceDB metadata); (2) Bayesian RUL blend — engineer correction updates prior in `rul_bayesian_correction.py`; (3) `preference.jsonl` for future RLHF/DPO offline pass |
| **LangGraph checkpointer** | `langgraph-checkpoint-sqlite>=3.1.0` — `SqliteSaver` writes full agent state to `data/sessions.db` per `thread_id`; enables full time-travel replay for "show your reasoning" demo beat |
| **Mem0 memory** | `mem0ai 2.0.4` on ChromaDB backend at `data/chromadb/` — stores per-user/per-session corrections; injected as `<memory_context>` in subsequent turns for the multi-turn continuity demo beat |

---

## 9. Full Stack at a Glance (CPU-only, zero paid keys)

```
LAYER               LIBRARY                     VERSION     NOTES
─────────────────────────────────────────────────────────────────────────────
Embeddings          sentence-transformers       >=3.0       BAAI/bge-small ONNX
Reranker            flashrank                   >=0.2       ONNX, no torch
NLI gate            sentence-transformers       >=3.0       cross-encoder/nli-deberta-v3-small
Vector DB (RAG)     lancedb                     >=0.20      embedded, native hybrid BM25+dense
Vector DB (memory)  chromadb                    >=0.5       Mem0 backend, isolated
Chunking            pymupdf4llm                 >=0.0.17    Markdown-aware
KG / RCA            networkx                    3.3         FMEA ontology, ISO 14224
Causal RCA          dowhy                       >=0.12      GCM attributor, CPU
RUL                 lifelines                   >=0.30      WeibullAFT, joblib
Anomaly (batch)     scikit-learn                >=1.5       IsolationForest + SHAP
Anomaly (deep)      torch (cpu build)           2.3.1       LSTM-AE, state_dict
Anomaly (online)    river                       0.21        HalfSpaceTrees, streaming
Failure pred        lightgbm                    >=4.6       4-class ordinal + tsfresh
Time features       tsfresh                     0.21        rolling stats
SHAP explainer      shap                        >=0.46      TreeExplainer, CPU
LLM gateway         litellm                     >=1.45      swappable, no vendor lock
Local LLM           ollama                      >=0.18      Qwen2.5-3B or steel-wizard GGUF
Fine-tune (offline) unsloth                     2025.12     Colab T4 one-shot, output = GGUF
Orchestration       langgraph                   >=1.2.4     PEV supervisor
Checkpointer        langgraph-checkpoint-sqlite >=3.1.0     SqliteSaver, sessions.db
Memory              mem0ai                      2.0.4       ChromaDB backend
Structured output   instructor                  >=1.15      Pydantic-validated LLM responses
Backend             fastapi + uvicorn           >=0.136     native SSE, async
Scheduler           apscheduler                 3.11        BackgroundScheduler, 5s tick
Resilience          tenacity + pybreaker        ≥8.5 / ≥2  retry + circuit breaker
Observability       arize-phoenix               >=4.0       local trace UI, zero Docker
Eval                deepeval + ragas            >=4.0 / 0.2 golden-set gate
Frontend            streamlit + plotly          1.58 / 5.22 5 pages, st.fragment SSE
Storage             sqlmodel + sqlite            0.0.21      wizard.db + sessions.db
```

**Everything above installs via `pip`, runs on CPU, requires zero API keys.**
The subscription LLM is **best-effort on top** — every path has an Ollama fallback.
Demo safety = cache first, Ollama second, subscription third.

---

## 10. Laptop RAM Budget (worst case, all services running)

| Component | RSS |
|---|---|
| Python process (FastAPI + all in-process models) | ~800 MB |
| bge-small-en-v1.5 ONNX | ~90 MB |
| LSTM-AE (CPU torch) | ~150 MB |
| LightGBM + IsolationForest (loaded) | ~80 MB |
| LanceDB (open tables) | ~120 MB |
| ChromaDB (Mem0) | ~80 MB |
| Streamlit frontend process | ~200 MB |
| Ollama (steel-wizard Q4_K_M 3B) | ~2.8 GB |
| **Total** | **~4.3 GB RSS** |

Fits comfortably in 8 GB RAM. On 16 GB laptops, Arize Phoenix adds ~300 MB.
If Ollama is swapped for `llama-cpp-python` in-process, save ~200 MB daemon overhead.
