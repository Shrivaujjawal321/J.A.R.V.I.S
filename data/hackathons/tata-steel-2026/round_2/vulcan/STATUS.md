# VULCAN — Build Status (Wave 6: Demo Bake + Adversarial Verification)

**Product:** VULCAN — agentic Maintenance Wizard for industrial steel equipment.
**Persona:** EDITH — the conversational voice the engineer talks to.
**Brain:** Claude Max **subscription** via `claude-agent-sdk` (OAuth token). **No API key, ever.**
**Everything else** (bge-small embeddings, FlashRank rerank, ChromaDB, LightGBM/IsolationForest ML, NLI faithfulness gate, optional Ollama SLM): **local, CPU-only, free.**

Verified end-to-end on the flagship dataset
(`round_2/dataforge/datasets/steel-maintenance-flagship/`) on **2026-06-09**.

---

## TL;DR verdict

- **Boots with NO API key:** YES. `ANTHROPIC_API_KEY` is popped at import in `config.py`, `llm.py`,
  and every UI page; the OAuth token is resolved by a walk-up loader to the repo-root `.env`.
  Streamlit booted clean (HTTP 200) under `env -u ANTHROPIC_API_KEY`. Source grep shows zero
  litellm / Gemini / paid-key code paths.
- **Demo is rate-limit-proof:** the 3 chat queries + 1 multi-turn follow-up + 1 autonomous alert
  hand-off were baked into `data/demo/demo_cache.json` as real Claude prose (5 entries).
  Replay serves them from the L0 cache at `rung=cache` (0 ms LLM) — zero live calls.
- **Template fallback catches total outage:** with no token + `provider=template` + an uncached
  query, the supervisor still resolves the asset, runs the full ML/risk pipeline, and returns a
  grounded, cited deterministic answer. **No crash.**
- **Autonomous alert fires on a REAL spine asset:** BF.BLW.FAN01 / SCN-041 escalates
  WARNING (5.28) → ALARM (8.15) → CRITICAL (8.14 @ row 1928), then hands off to EDITH (cached).
- **Citations present (FR4):** every answer carries inline `[N]` citations + a "Grounded in:"
  source panel + a 9-step reasoning trace + a local NLI faithfulness gate (flags unsupported claims).
- **No crash on the happy path.** 35/36 tests pass (1 skipped = live-Claude-gated).

---

## How to run

```bash
PY=/home/ujjwal/Documents/J.A.R.V.I.S./.venv/bin/python
cd /home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_2/vulcan

# 1) (one-time) build artifacts — ALREADY BUILT (data/models 66M, data/vectordb 32M)
$PY -m vulcan.rag.store                                   # ingest 2683 chunks -> Chroma
$PY -c "from vulcan.ml.models import train_all; train_all()"   # 15 fault + 15 anomaly + 13 RUL

# 2) (one-time, when Claude reachable) bake the demo cache — ALREADY BAKED (5 entries)
$PY scripts/capture_demo_cache.py            # live Claude -> demo_cache.json
$PY scripts/capture_demo_cache.py --verify   # replay, assert L0 hits

# 3) run the demo UI (the deliverable). cache_first => sub-ms cached Claude prose.
env -u ANTHROPIC_API_KEY VULCAN_LLM_MODE=cache_first \
  $PY -m streamlit run vulcan/ui/app.py
```

### LLM modes (`VULCAN_LLM_MODE`)
- `cache_first` (default, demo): L0 cache → Claude → SLM → template. Cached demo queries are sub-ms.
- `live`: skip L0, always hit Claude live (used for baking + ad-hoc queries).
- `off`: force the deterministic template floor (offline proof).

### Provider (`VULCAN_LLM_PROVIDER`)
- `subscription` (default): Claude Max via OAuth.
- `local_slm`: Ollama keyless fallback (off by default).
- `template`: deterministic floor only (no model).

---

## The provider ladder (the single LLM chokepoint — `vulcan/llm.py`)

All model text flows through `subscription_llm()`. It **never raises**.

| Rung | Source | Latency | Keyless |
|------|--------|---------|---------|
| L0 | `demo_cache.json` — baked Claude prose, exact `sha256(system+user)` key | sub-ms | yes |
| L1 | Claude Max subscription via `claude_agent_sdk.query()` (OAuth) | ~25 s | yes (OAuth, no key) |
| L2 | Local SLM (Ollama `qwen2.5:3b`) — guarded, off by default | slow | yes |
| L3 | Deterministic template grounded on spine + retrieved chunks | sub-ms | yes |

The cache key is byte-deterministic: the supervisor builds the synthesis prompt from the same
ML/spine outputs each run, so `sha256(system+user)` is stable → reliable L0 hits on replay
(verified: two runs produce an identical hash).

---

## Functional-requirement coverage (evidence)

| FR | Status | Evidence |
|----|--------|----------|
| **FR1 — LLM/SLM contextual reasoning** | **works** | Claude Max subscription via Agent SDK + OAuth (no key); answered the bearing query live in ~26 s with a correct technical diagnosis. SLM (L2) + template (L3) rungs back it. |
| **FR2 — Knowledge integration / RAG** | **works** | bge-small + ChromaDB (2683 chunks / 82 sources) + FlashRank rerank. Bearing query surfaces RCA-001 + SOP-01 with rerank scores; gearbox query cites SOP-02 + spare catalog. |
| **FR3 — NL + multi-turn** | **works** | EDITH NL front door; follow-up "and what spare…" (no asset named) inherits focus HSM.F3.WR.BRG01 and switches intent diagnosis→procurement. Verified cached. |
| **FR4 — Explainable + traceable** | **works** | Inline `[N]` citations in every answer + "Grounded in:" dataset source pills + 9-step reasoning trace (PLAN→TOOL→ML→SYNTHESIS→LLM→GATE) + local NLI faithfulness gate that flags unsupported claims (e.g. flagged the P(FAILURE)=1.00 claim). |
| **FR5 — Anomaly detection + RUL** | **works** | 15 LightGBM fault classifiers (3-class) + 15 IsolationForest anomaly detectors + 13 LightGBM RUL regressors on the steel-native dense tables. Bearing window: P(FAILURE)=1.00, anomaly 0.67, RUL ~118 cycles (~4.9 d). |
| **FR6 — Feedback-driven improvement** | **works** | `vulcan/feedback.py` SQLite store; thumbs up/down moves a per-asset priority weight live (no retrain) and feeds back into the risk score (trace shows "feedback weight 0.86 → -0.42"). |
| **FR7 — Real-time alerting** | **works** | `vulcan/alerting/` deterministic threshold detector replays a real per-asset dense stream; BF.BLW.FAN01 fires WARNING→ALARM→CRITICAL on real rows; first CRITICAL auto-hands-off to EDITH for an explainable diagnosis. Persisted to SQLite alert store. |

### Outputs produced
Diagnosis · Root-Cause · RUL · risk class (low/med/high/critical with factor math) · prioritized
actions · spare-procurement strategy (in-stock vs ORDER-NOW + lead-time, e.g. GEAR-WHL-M20 36-week
lead, total INR 10,395,750) · structured reports (Incident / Alert / Decision). All cited.

---

## What genuinely works
- Keyless boot (no `ANTHROPIC_API_KEY`); OAuth subscription brain; key-scrub verified.
- 5-entry demo cache baked with real Claude prose; replays at `rung=cache` (0 ms LLM).
- Full agentic pipeline: resolver → per-intent agent DAG → grounded synthesis → NLI gate → memory.
- Template floor under total outage — no crash, still grounded + cited.
- Autonomous FR7 alert on a real spine asset with cached agentic hand-off.
- Streamlit UI: Chat (3 demo chips), Alerts (live replay + escalation table), Reports (generate),
  Health Dashboard. Sidebar shows Brain / Mode / No-API-key state.
- 35/36 tests pass.

## Known limitations / TODO
- Faithfulness lands at ~0.65–0.69 ("unverified", not "verified") because Claude's rich prose adds
  detail (exact sensor values, °C) not present verbatim in the numbered source strings. The gate
  correctly flags these as low-confidence rather than hiding them — honest, but the badge reads
  "unverified". Tightening would mean feeding the raw sensor readings into the scoreable sources.
- FR6 delta display shows "+0" in the int format even though the float weight genuinely changes
  (cosmetic only; the re-weighting works).
- Streamlit multipage navigation is mildly racy when driven by an automated browser (reruns can
  interrupt a click); a human demo operator is unaffected. Engine-level verification of every page
  path was done headlessly to confirm correctness.
- Live Claude latency is ~25 s/call on this CPU box — which is exactly why the demo runs from the
  baked cache. Re-bake (`scripts/capture_demo_cache.py`) whenever the demo script changes.
- L2 SLM (Ollama) is off by default and not load-bearing; enable with `VULCAN_ENABLE_SLM=1` if an
  Ollama daemon is present.

---

## Re-bake the demo cache
If you change a demo query, the scenario data, or the synthesis prompt, re-bake while Claude is
reachable so the L0 keys match again:

```bash
$PY scripts/capture_demo_cache.py           # bake all 5 scripted scenarios
$PY scripts/capture_demo_cache.py --verify  # assert L0 hits on replay
```
