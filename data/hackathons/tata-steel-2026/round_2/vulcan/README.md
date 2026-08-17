# VULCAN

**An agentic Maintenance Wizard for industrial steel equipment.**
Built for the Tata Steel R2 hackathon (theme: *Maintenance Wizard for Industrial Equipment*).

- **Product:** **VULCAN** — the diagnostic / RCA / RUL / risk / planning engine.
- **Persona:** **EDITH** — the conversational voice the operator talks to.
- **Brain:** Claude Max **subscription** via `claude-agent-sdk` (OAuth token) — **no API key, ever.**
- **Everything else** (embeddings, rerank, vector DB, anomaly/RUL ML, optional SLM): **local, CPU-only, free.**

> The deliverable is a recorded demo. The demo happy-path is **fast and never crashes** — every
> LLM call falls through a provider ladder to a deterministic template, so VULCAN works even when
> the subscription is rate-limited or fully offline.

---

## The provider ladder (the LLM chokepoint)

All model text flows through `vulcan.llm.subscription_llm()`. It **never raises**; on total
failure it returns a grounded deterministic template. The rungs, in order:

| Rung | Source | Latency | Keyless? |
|------|--------|---------|----------|
| **L0** | `demo_cache.json` — offline-baked Claude prose (exact system+user hash) | sub-ms | yes |
| **L1** | Claude Max subscription via `claude_agent_sdk.query()` (OAuth token) | ~11–12 s | yes (OAuth, no API key) |
| **L2** | Local SLM via Ollama (`qwen2.5:3b`) — keyless live fallback *(guarded, off by default)* | slow | yes |
| **L3** | Deterministic template grounded on the dataset spine + retrieved chunks | sub-ms | yes |

`ANTHROPIC_API_KEY` is **popped at import** so a paid-key path can never be taken. The OAuth
token is resolved by a **walk-up loader** that climbs to the repo-root `.env`
(`/home/ujjwal/Documents/J.A.R.V.I.S./.env`) — the exact pattern proven in `jarvis_core` and
the EDITH agent. Each rung has a **hard timeout** so it fails forward fast.

---

## Data

VULCAN reads the flagship dataset at
`round_2/dataforge/datasets/steel-maintenance-flagship/` (15 assets, 51 scenarios, sensors +
thresholds + spares, 13 equipment manuals, 13 SOPs, 50 RCA reports, condition-monitoring
time-series, and a 260-prompt user-interaction eval set). Override the path with
`$VULCAN_DATASET_ROOT`.

---

## Install

Use the **shared project venv** (already has torch-cpu, sentence-transformers, lightgbm,
claude-agent-sdk, streamlit, flashrank, chromadb, polars):

```bash
PY=/home/ujjwal/Documents/J.A.R.V.I.S./.venv/bin/python
$PY -m pip install -e .          # editable install of the vulcan package
# or just rely on the shared venv already having the deps
```

## Smoke test

```bash
PY=/home/ujjwal/Documents/J.A.R.V.I.S./.venv/bin/python
$PY -m vulcan.config              # prints paths + OAuth token presence
$PY -m vulcan.data.loaders        # prints dataset summary counts
$PY -m vulcan.llm                 # round-trips a trivial prompt through the ladder
```

---

## Wave-2 components (local, keyless, CPU)

Three keyless engines. Artifacts persist under the canonical `vulcan/data/`
(`models/` for ML joblib, `vectordb/` for the Chroma corpus). One-time build, then
inference is fast and offline.

### 1. RAG — `vulcan.rag`  (bge-small + ChromaDB + FlashRank + NLI gate)

```bash
$PY -m vulcan.rag.store           # ingest corpus -> data/vectordb/ (2683 chunks)
$PY -c "from vulcan.rag import retrieve; \
        [print(c.rerank_score, c.citation()) for c in retrieve('bearing BPFO spall')]"
```

- Ingests 13 manuals + 13 SOPs + 25 RCA reports + 30 domain docs + 118 spare-catalog
  entries = **2683 chunks / 82 sources**. Each chunk keeps its `source` filename + section
  for inline citations (FR4).
- `retrieve(query, equipment_class=…, doc_types=…)` → dense (Chroma cosine) → FlashRank
  rerank → top-k `RetrievedChunk` (each `.citation()` renders `[source § section]`).
- `run_gate(answer, chunks)` — local NLI (`nli-deberta-v3-small`) faithfulness check;
  scores each `[N]`-cited claim against its source, flags un-entailed claims (FR4 verified badge).

### 2. ML — `vulcan.ml`  (15 fault + 15 anomaly + 13 RUL models)

```bash
$PY -c "from vulcan.ml.models import train_all; import json; print(json.dumps(train_all()))"
```

- Trained on the steel-native dense tables (`condition_monitoring/by_equipment/*.csv`,
  `fault_label` ∈ {0 normal, 1 warning, 2 failure}) + `rul_trajectories_long.csv`.
- **Fault classifier** (LightGBM 3-class, per asset — keyed per asset because two assets in
  a shared class have different sensor sets): `predict_fault(asset, window)`.
- **Anomaly detector** (IsolationForest on normal-only window features): `anomaly_score(asset, window)`.
- **RUL estimator** (LightGBM regressor on `rul_cycles`, per equipment class): `estimate_rul(asset)`.

### 3. Tools — `vulcan.tools`  (deterministic, LLM-free dataset reads)

`get_asset · get_thresholds · get_sensor_reading · get_sensor_summary · get_scenario ·
get_scenarios_for_asset · get_spare · get_spares_for_scenario · get_recent_alerts ·
search_history`. Every result carries a `source` ref. Forgiving asset resolution (canonical id,
case/separator variant, or sensor tag).

### Verify all three

```bash
$PY vulcan/verify_wave2.py        # RAG retrieval + ML predictions + tool reads, on real data
$PY -m pytest tests/ -q           # 26 pass, 1 skipped (live-Claude gated)
```

---

## Functional-requirement coverage (target)

1. **LLM/SLM contextual reasoning** — Claude subscription brain + optional fine-tuned SLM rung.
2. **Knowledge integration / RAG** — bge-small embeddings + flashrank rerank over manuals/SOPs/RCAs.
3. **NL + multi-turn** — EDITH conversational layer over the 50 multi-turn eval conversations.
4. **Explainable + traceable** — inline citations to dataset sources + reasoning trace + NLI gate.
5. **Anomaly detection + failure prediction (RUL)** — sklearn/LightGBM on condition-monitoring data.
6. **Feedback-driven improvement** — feedback log feeds eval + cache.
7. **Real-time alerting** — anomaly-alert stream → risk classification → prioritized actions.

Outputs: diagnosis · RCA (5-whys) · RUL · risk class (low/med/high/critical) · prioritized actions
(process-criticality + spares availability + procurement lead-time) · spare-procurement strategy ·
structured reports.

---

## Status

**WAVE 1 — FOUNDATION:** package scaffold + `config.py` (settings + OAuth walk-up)
+ `llm.py` (the provider-ladder chokepoint) + `data/loaders.py` (typed dataset access). Verified:
the ladder returns real Claude text with no API key set, and falls to the template without crashing
when the token is missing.

**WAVE 2 — COMPONENTS (this milestone):** `vulcan.rag` (2683-chunk Chroma corpus, bge-small +
FlashRank rerank + NLI faithfulness gate), `vulcan.ml` (15 per-asset LightGBM fault classifiers +
15 IsolationForest anomaly detectors + 13 LightGBM RUL regressors, trained on the steel-native dense
tables) and `vulcan.tools` (10 deterministic dataset readers). Verified end-to-end on real data:
bearing-query retrieval surfaces the exact RCA + SOP with citations; the fault model fires FAILURE +
the anomaly detector flags `is_anomaly` on a real failure window while reading NORMAL on healthy
windows; tools return real spine values. 26/27 tests pass (1 live-Claude test gated).
