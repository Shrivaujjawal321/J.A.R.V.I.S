# 02 — Subscription-Only Architecture (NO API KEY)
## Tata Steel R2 Maintenance Wizard · Claude Max OAuth · Local-First Reasoning Spine

**Author:** Jarvis · **Date:** 2026-06-09 · **Status:** authoritative design for the subscription rewrite
**Replaces:** the Gemini-API-key LLM path in `maintenance-wizard/` (`wizard/agents/nodes.py::_llm_complete` → LiteLLM → `gemini/gemini-2.0-flash` with `GEMINI_API_KEY`).

> **HARD CONSTRAINT (non-negotiable).** Boss has **no API key and never will** — only a **Claude Max subscription** (an OAuth token from `claude setup-token`). Every LLM call must run via the subscription (Claude Agent SDK on `CLAUDE_CODE_OAUTH_TOKEN`, or a `claude -p` subprocess). Everything else — embeddings, rerank, vector DB, ML models, anomaly/RUL/fault models, optional fine-tuned SLM — must be **local, CPU-only, and free**. The subscription has session/rate limits (we hit one mid-workflow on the dataforge build), so the design is **local-first, LLM-sparing, cache-heavy**, and the **live demo must not die on a rate limit**.

---

## 0. Thesis: the LLM is the conductor, not the orchestra

The Maintenance Wizard's intelligence is overwhelmingly **deterministic + local**: hybrid RAG over the flagship corpus, a NetworkX FMEA graph, WeibullAFT RUL, IsolationForest/LSTM-AE anomaly, LightGBM fault classification, a WRPS prioritizer. These run on CPU, cost nothing, never rate-limit, and are already built (~36.5k LOC in `maintenance-wizard/`).

The **subscription LLM does exactly four things** that genuinely need a frontier model (§3): (a) diagnosis synthesis, (b) RCA 5-whys narrative, (c) the maintenance-plan two-pass write-up, (d) multi-turn conversational glue. Every one of those calls has a **deterministic local fallback** that already exists in `nodes.py`. The system is therefore correct and demoable **with the LLM entirely offline** — the subscription only *upgrades prose quality*, it is never *load-bearing for correctness*.

This is the single most important property for a subscription-only build: **a rate limit degrades fluency, never function.**

```
                 ENGINEER (NL, multi-turn)              SENSOR STREAM (5s playback)
                          │                                       │
                ┌─────────▼──────────┐                ┌───────────▼───────────┐
                │  Streamlit 1.58    │                │  APScheduler proactive │
                └─────────┬──────────┘                └───────────┬───────────┘
                          │ httpx (sync)                          │
                ┌─────────▼───────────────────────────────────────▼─────────┐
                │              FastAPI 0.136 (async, SSE)                    │
                └────────────────────────────┬───────────────────────────────┘
                                             │ LangGraph supervisor (PEV)
        ┌──────────────────────────────┬─────┴───────┬────────────┬──────────┐
     DIAG          RCA               RUL          RISK         PLAN       ALERT
        │            │                │ (local)     │ (local)     │           │
        ▼            ▼                ▼             ▼             ▼           ▼
   ┌────────────────────────────────────────────────────────────────────────────┐
   │  REASONING TIER  →  subscription_llm()  (the ONLY door to the LLM)           │
   │  ┌──────────────────────────────────────────────────────────────────────┐  │
   │  │ 1. demo_cache.json (gold, pre-computed)   → sub-ms, never calls LLM    │  │
   │  │ 2. semantic response cache (SQLite+embed)  → <50ms on near-dup queries │  │
   │  │ 3. Claude Agent SDK query()  [CLAUDE_CODE_OAUTH_TOKEN, no API key]     │  │
   │  │    └─ on 429 / session-limit / timeout → exponential backoff (1 try)   │  │
   │  │ 4. DETERMINISTIC LOCAL FALLBACK (template / Qwen2.5-3B Ollama)         │  │
   │  └──────────────────────────────────────────────────────────────────────┘  │
   ├──────────────────────────────────────────────────────────────────────────────┤
   │  LOCAL-ONLY TIER (CPU, free, never rate-limited) — the system's correctness   │
   │  • RAG: LanceDB hybrid + bge-small ONNX + FlashRank   • KG: NetworkX FMEA      │
   │  • RUL: WeibullAFT  • Anomaly: IForest+LSTM-AE  • Fault: LightGBM  • WRPS      │
   └──────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. The proven precedent (read first — this is what we copy)

Two existing components in this repo already run Claude Max via OAuth, **no API key**. The Wizard's LLM layer is a direct port of both.

### 1.1 `jarvis_core/orchestrator.py::run_worker` (Agent SDK, production)
- Imports `from claude_agent_sdk import ClaudeAgentOptions, query`.
- Builds `ClaudeAgentOptions(cwd=…, max_turns=…, allowed_tools=…, model=…, resume=…)`.
- Iterates `async for message in query(prompt=prompt, options=options)`, accumulating text blocks, `session_id` (resumability), and `total_cost_usd` (quota tracking).
- Wraps the whole stream in `asyncio.wait_for(..., timeout=timeout_seconds)` and **never raises** — returns a `WorkerOutcome` with `error` set on timeout/exception.
- Defensive `TypeError` retry: if the installed SDK build rejects a kwarg (e.g. `model`), it drops it and retries. **We keep this pattern** — it is what makes the wrapper survive SDK version drift across the judge's machine.

### 1.2 `dataforge/api/scorer/agent.py::_subscription_review` + `_load_oauth_token` (EDITH, shipped)
- `_load_oauth_token()`: reads `CLAUDE_CODE_OAUTH_TOKEN` from env; **if absent, walks up the directory tree** to find the Jarvis repo-root `.env`, parses the token, and caches it into `os.environ`. This is critical: a uvicorn process launched from `maintenance-wizard/` may not inherit the repo-root token. **We port this verbatim.**
- `_subscription_review()`: `ClaudeAgentOptions(max_turns=1, allowed_tools=[], system_prompt=…)` for pure text generation, collected under `asyncio.wait_for(timeout)`, and **returns `None` on any failure** (token missing, SDK absent, offline, timeout) so the caller falls back to the deterministic template.
- Kill-switch: honours an env var (`EDITH_LLM_REVIEW=off`) to force deterministic mode. **We add the same** (`WIZARD_LLM=off`).

### 1.3 Installed SDK reality (verified 2026-06-09)
`claude_agent_sdk` **v0.1.81** is in the repo venv. `ClaudeAgentOptions` exposes exactly the fields we rely on:
`system_prompt, max_turns, allowed_tools, disallowed_tools, model, fallback_model, output_format, max_budget_usd, effort, thinking, permission_mode, resume, session_id, cwd, env, settings`.
So **all four LLM-shaping levers in the prompt brief are first-class kwargs** — no monkey-patching needed.

> **Agent SDK vs `claude -p` subprocess — decision:** use the **Agent SDK `query()`** as primary (in-process, structured messages, `total_cost_usd`, session resume, clean `asyncio` cancellation on timeout — exactly what `run_worker` already proves). Keep a **`claude -p --output-format json` subprocess** as a *second-line fallback* only (§5.4) for the rare case where the SDK import itself fails on the judge's clean venv. Both authenticate the same way: `CLAUDE_CODE_OAUTH_TOKEN` in the environment, **no `ANTHROPIC_API_KEY`**.

---

## 2. How the orchestration/reasoning LLM runs on the subscription

### 2.1 Auth — OAuth token, never a key
- One-time on Boss's machine: `claude setup-token` → prints `sk-ant-oat01-…` → store as `CLAUDE_CODE_OAUTH_TOKEN` in the Wizard's `.env` (and repo-root `.env` as the walk-up fallback).
- The wrapper **must guarantee `ANTHROPIC_API_KEY` is unset/empty** before calling the SDK. If both an OAuth token and an API key are present some SDK builds prefer the key (which Boss doesn't have / would bill). We `os.environ.pop("ANTHROPIC_API_KEY", None)` at import.
- `.env.example` rewrite (replaces the Gemini block):
  ```ini
  # ── LLM: Claude Max subscription (NO API KEY) ────────────────────────────────
  LLM_PROVIDER=subscription                 # subscription | ollama | off
  CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...  # from `claude setup-token` (NOT an API key)
  WIZARD_LLM=on                             # off → force deterministic templates (demo-safe)
  WIZARD_LLM_MODEL=                         # blank = subscription default; or claude-haiku-4-5 for light agents
  WIZARD_LLM_TIMEOUT_S=22
  WIZARD_LLM_MAX_TURNS=1                    # text generation = single turn, no tool loop
  # Offline fallback (optional, free, local):
  LLM_MODEL_FALLBACK=ollama/qwen2.5:3b
  ```

### 2.2 Call shape — single-turn, tool-less text generation (the 90% case)
The four LLM tasks (§3) are **structured-text generation**, not agentic tool loops. So every call uses:
- `max_turns=1` — no ReAct loop, no surprise multi-call cost. **Routing and tool selection are deterministic Python in `supervisor_route` / the node code — the LLM never decides which tool to call.** This is the single biggest token-sparing decision.
- `allowed_tools=[]` — the model cannot spawn bash/file/search side-effects; it only writes text. Faster, cheaper, and safe on a judge's machine.
- `system_prompt` = a tight role prompt per agent (e.g. *"You are the Maintenance Wizard diagnosis agent for a steel plant. Use ONLY the provided context. No markdown headers, no 'I'. Be specific and cite source tags like [SOP-04 §3.2]."*).
- `model` (optional): leave blank for subscription default on the heavy agents (RCA, Plan); pass `claude-haiku-4-5` on the light ones if we want speed — but **honour the `TypeError` retry** so an unknown model string never crashes the call.

### 2.3 Structured output without an API key
The Agent SDK build exposes `output_format`, but the **robust, version-proof** path (and the one already used in EDITH) is: **ask for a fenced JSON block in the prompt, then parse defensively.** `nodes.py::_llm_complete` already does exactly this:
```python
json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
data = json.loads(json_match.group(1) if json_match else content.strip())
```
We keep that. Each agent's prompt ends with an explicit schema (e.g. *"Return ONLY a JSON object: {probable_fault_codes: [...], probable_fault_description: str, confidence: float, diagnosis_reasoning: str, process_related_defects: [str]}"*). On parse failure → return `None` → node uses its deterministic fallback. **We never trust the LLM to be the source of truth for a field a local model already computed** (RUL hours, fault class, risk tier all come from the ML/WRPS layer; the LLM only narrates them).

### 2.4 Pinning the integration seam
Today **every** LLM call in the Wizard already funnels through one function: `wizard/agents/nodes.py::_llm_complete(system, user, response_model, …)`. The rewrite is therefore **surgical**: replace the LiteLLM body of `_llm_complete` with a call to the new `subscription_llm()` wrapper (§4). No node, tool, RAG, or ML file changes. Grep confirms the only other LLM-ish call sites (`rag/retriever.py` HyDE, `rca_engine.py`, `knowledge/generator.py`) also route through helpers we can point at the same wrapper.

---

## 3. Where the LLM is genuinely needed vs where local/deterministic suffices

**Rule: an LLM call is justified only when the output is open-ended natural language a template can't match, AND a wrong/absent answer is non-catastrophic (a fallback exists).** Everything else stays local.

| Wizard capability | Engine | LLM? | Why |
|---|---|---|---|
| Supervisor routing (query → agent) | **Deterministic Python** (`supervisor_route`, Literal return) | **No** | Keyword/intent rules. LLM routing = latency + token + nondeterminism for zero gain. |
| Embeddings (RAG + semantic cache + dedup) | **bge-small-en-v1.5 ONNX** (sentence-transformers, CPU) | **No** | Local, 384-dim, ~ms. Never call an LLM to embed. |
| Hybrid retrieval + rerank | **LanceDB hybrid + FlashRank ONNX** | **No** | Dense+BM25+SQL prefilter; cross-encoder rerank. Pure local. |
| FMEA cause-chain traversal | **NetworkX** ISO-14224 graph | **No** | Graph walk over the flagship spine. Deterministic, explainable, instant. |
| RUL prediction | **lifelines WeibullAFT** (offline-trained joblib) | **No** | Numeric regression. LLM cannot and must not estimate RUL hours. |
| Anomaly detection | **IsolationForest + LSTM-AE + River** | **No** | Real-time scoring on the 5s tick. CPU. |
| Fault classification | **LightGBM** (calibrated, joblib) | **No** | 4-class ordinal + SHAP. LLM is worse and slower. |
| Risk tier + priority queue | **WRPS** 4-factor weighted score | **No** | Arithmetic on {criticality, severity, spares, lead-time}. Deterministic. |
| Alert dedup/cooldown | **Python** PriorityQueue + SQLite | **No** | Rule-based. |
| Spare-parts/procurement lookup | **SQL on flagship `spare_parts_catalog.csv`** | **No** | Join + lead-time arithmetic. |
| **Diagnosis narrative** (sensors+logs+RAG → probable fault prose) | DIAG agent | **YES** (fallback: template) | Synthesising heterogeneous evidence into engineer-readable prose. |
| **RCA 5-whys narrative** (graph path + GCM → causal story) | RCA agent | **YES** (fallback: graph-path template) | The "show your work" causal chain reads far better LLM-written; local layers supply the *facts*. |
| **Maintenance plan write-up** (pass-2: structured steps + cited narrative) | PLAN agent | **YES** (fallback: template steps from SOPs) | Step ordering + safety phrasing + citations. Pass-1 (which SOPs/spares) is deterministic RAG. |
| **Multi-turn conversational glue** (follow-ups, clarifications) | Chat | **YES** (fallback: "Here's what I found:" + structured dump) | The one place free-form NL is the product. |
| (optional) HyDE query expansion for RAG | retriever | **OPTIONAL** (default OFF) | A hypothetical-doc rewrite *can* lift recall, but it's an extra LLM call per query. **Default to a local query-expansion (synonym/tag boost) and only HyDE when cache is warm and rate budget is green.** |

**Net:** of ~6 agent nodes, **3.5 ever touch the LLM**, each at `max_turns=1`, each cache-gated, each with a fallback. A full diagnostic turn that hits all caches makes **0** LLM calls; a cold turn makes **at most 3** (diag, rca, plan) — and the proactive 5s alert loop makes **0** (it's pure ML + template, by design, because that loop must never rate-limit).

### 3.1 Optional fine-tuned SLM (extra-merit, local, free)
The PS gives extra merit for a domain-specific model. Our differentiator stays **local and key-free**: **Qwen2.5-3B QLoRA** (Unsloth) fine-tuned on the flagship synthetic corpus, served via **Ollama** (`ollama/qwen2.5:3b-maint`). It slots in as the **fallback** layer of `subscription_llm()` — so even fully offline with the subscription rate-limited, the Wizard produces *domain-tuned* prose, not just templates. Ship it gated (only if it beats base on a held-out eval) per the master brief.

---

## 4. The reusable wrapper — `subscription_llm()` with full fallback ladder

A new module `wizard/core/llm.py`. `nodes._llm_complete` becomes a thin adapter over it. **Four levels, fail-soft at every step, never raises.**

```python
# wizard/core/llm.py
"""
Subscription-only LLM gateway for the Maintenance Wizard.

NO API KEY. Reasoning runs on Boss's Claude Max subscription via the Claude
Agent SDK + CLAUDE_CODE_OAUTH_TOKEN (same auth as jarvis_core/orchestrator.py
and dataforge/api/scorer/agent.py). Local Qwen/Ollama + deterministic templates
are the offline fallbacks. Cache-first so the live demo never dies on a 429.

Ladder per call:
  L0  demo_cache.json gold response   (sub-ms, scripted demo path — never calls LLM)
  L1  semantic response cache         (<50ms on near-duplicate queries; SQLite + bge-small)
  L2  Claude Agent SDK query()        (subscription; one backoff retry on 429/limit/timeout)
  L3  local fallback                  (Ollama Qwen2.5-3B if up, else caller's deterministic template)
"""
from __future__ import annotations
import asyncio, hashlib, json, os, re, time
from pathlib import Path
from typing import Optional

# Subscription auth: OAuth token only. Never let an API key win.
os.environ.pop("ANTHROPIC_API_KEY", None)

_ROOT = Path(__file__).resolve().parents[2]          # maintenance-wizard/
_DEMO_CACHE = _ROOT / "data" / "demo" / "demo_cache.json"
_LLM_ENABLED = os.getenv("WIZARD_LLM", "on").lower() not in ("0", "off", "false", "none")
_TIMEOUT_S = int(os.getenv("WIZARD_LLM_TIMEOUT_S", "22"))
_MAX_TURNS = int(os.getenv("WIZARD_LLM_MAX_TURNS", "1"))
_MODEL = os.getenv("WIZARD_LLM_MODEL") or None

# --- token loader (ported verbatim from dataforge/api/scorer/agent.py) ---------
def _load_oauth_token() -> Optional[str]:
    tok = os.getenv("CLAUDE_CODE_OAUTH_TOKEN")
    if tok:
        return tok
    here = os.path.abspath(__file__)
    for _ in range(8):                                   # walk up to repo-root .env
        here = os.path.dirname(here)
        env_path = os.path.join(here, ".env")
        if os.path.isfile(env_path):
            for line in open(env_path):
                line = line.strip()
                if line.startswith("CLAUDE_CODE_OAUTH_TOKEN="):
                    tok = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if tok:
                        os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = tok
                        return tok
        if os.path.basename(here) == "J.A.R.V.I.S.":
            break
    return None

# --- L0/L1 cache machinery -----------------------------------------------------
def _key(system: str, user: str) -> str:
    return hashlib.sha256((system + "\x1f" + user).encode()).hexdigest()[:16]

def _demo_cache_lookup(system: str, user: str) -> Optional[str]:
    try:
        cache = json.loads(_DEMO_CACHE.read_text())
        return cache.get(_key(system, user))            # exact gold hit for scripted demo
    except Exception:
        return None

# Semantic cache = SQLite table {hash, embedding(blob), response}; cosine ≥ 0.94
# reuses a near-duplicate answer. Embeds with the SAME bge-small ONNX model the
# RAG layer already loads (zero extra deps, zero extra download). Implementation
# in wizard/core/response_cache.py; gated by WIZARD_SEMANTIC_CACHE (default on).
from wizard.core.response_cache import semantic_lookup, semantic_store  # local, CPU

# --- L2 subscription call (Agent SDK; pattern from orchestrator.run_worker) ----
async def _subscription_call(system: str, user: str, timeout_s: int) -> Optional[str]:
    if not _LLM_ENABLED or not _load_oauth_token():
        return None
    try:
        from claude_agent_sdk import ClaudeAgentOptions, query
    except Exception:
        return None                                      # SDK absent → caller falls back
    kwargs = {"max_turns": _MAX_TURNS, "allowed_tools": [], "system_prompt": system}
    if _MODEL:
        kwargs["model"] = _MODEL
    try:
        options = ClaudeAgentOptions(**kwargs)
    except TypeError:                                    # SDK build rejects a kwarg → minimal
        options = ClaudeAgentOptions(max_turns=_MAX_TURNS)
    parts, final = [], None
    async def _collect():
        nonlocal final
        async for msg in query(prompt=user, options=options):
            content = getattr(msg, "content", None)
            if isinstance(content, list):
                for b in content:
                    t = getattr(b, "text", None)
                    if t:
                        parts.append(t)
            r = getattr(msg, "result", None)
            if isinstance(r, str) and r:
                final = r
    try:
        await asyncio.wait_for(_collect(), timeout=timeout_s)
    except Exception:
        return None                                      # 429 / session-limit / timeout / net
    out = (final or "\n".join(parts)).strip()
    return out or None

# --- L3 local fallback ---------------------------------------------------------
def _ollama_fallback(system: str, user: str) -> Optional[str]:
    model = os.getenv("LLM_MODEL_FALLBACK", "")
    if not model.startswith("ollama/"):
        return None
    try:
        import litellm                                   # only used for the LOCAL ollama path
        litellm.suppress_debug_info = True
        resp = litellm.completion(
            model=model, timeout=12,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
        )
        return (resp.choices[0].message.content or "").strip() or None
    except Exception:
        return None

# --- public sync entrypoint (Streamlit/FastAPI call this) ----------------------
def subscription_llm(system: str, user: str, *, timeout_s: int | None = None) -> Optional[str]:
    """Return model text, or None to signal the caller to use its deterministic template.
    NEVER raises. Cache-first; subscription with one backoff retry; local fallback last."""
    timeout_s = timeout_s or _TIMEOUT_S
    if (hit := _demo_cache_lookup(system, user)):        # L0
        return hit
    if (hit := semantic_lookup(system, user)):           # L1
        return hit
    text = None
    for attempt in range(2):                             # L2 + one backoff retry on 429/limit
        text = asyncio.run(_subscription_call(system, user, timeout_s))
        if text:
            semantic_store(system, user, text)           # warm the cache for next time
            return text
        if attempt == 0:
            time.sleep(2.0 + attempt * 3)                # exponential-ish backoff; subscription cooldown
    if (text := _ollama_fallback(system, user)):         # L3 local SLM
        return text
    return None                                          # → caller renders its deterministic template
```

**Async note for Streamlit:** the UI uses `httpx.Client` (sync) → FastAPI; the LLM call lives **server-side in FastAPI/LangGraph**, which is already async, so it `await`s `_subscription_call` directly there. The `asyncio.run(...)` shown is only for sync call sites (e.g. offline scripts / `capture_demo_cache.py`); inside the async backend we expose an `async def asubscription_llm()` twin to avoid nesting event loops. **Streamlit never calls the SDK directly** (master-brief rule #7: no `asyncio.run` in the UI thread).

---

## 5. Surviving subscription session/rate limits — for both reliability and the live demo

We hit a session limit mid-workflow during the dataforge build. Treat that as a **certainty**, not a risk. Five layers absorb it:

### 5.1 Pre-computed `demo_cache.json` (the demo's seatbelt — already exists)
`maintenance-wizard/data/demo/demo_cache.json` and `scripts/capture_demo_cache.py` are **already built**. Before recording / before judging, run the scripted `HAPPY_PATH.md` queries once (against a warm subscription) → every gold response is captured, keyed by `(system,user)` hash. During the demo, L0 serves them **sub-millisecond with zero LLM calls**. The scripted demo path therefore **cannot rate-limit, cannot time out, cannot vary**. This is the deterministic spine of "doesn't break / no errors / smooth" (4 of the 7 webinar axes).
- **Action item:** extend the existing capture script to key on `(system,user)` (the same `_key()` the wrapper uses) so cache hits are exact, and to cover all `HAPPY_PATH.md` beats incl. the 90-second proactive EAF-04 alert.

### 5.2 Semantic response cache (handles judge's *ad-lib* queries)
Judges will type their own questions, not just the script. The L1 SQLite+bge-small cache returns a near-duplicate prior answer at cosine ≥ 0.94 in <50ms — so the second phrasing of "what's wrong with the furnace fan" reuses the first answer instead of spending a fresh call. Bounded (LRU, ~500 entries), CPU-only, uses the embedding model already loaded. **This is what keeps an interactive Q&A session under the rate budget.**

### 5.3 LLM-sparing by construction (fewest possible calls)
- Proactive 5s alert loop: **0 LLM calls** (ML + template only) — the most frequent code path never touches the subscription.
- Routing, RUL, fault, risk, spares: **0 LLM calls** (all local).
- A cold diagnostic turn: **≤3 calls** (diag/rca/plan), each `max_turns=1`, each then cached.
- HyDE / query-expansion LLM call: **off by default**; local synonym expansion instead.
- Conversation memory: sliding-window summary kept locally; we don't re-send the full transcript each turn.

### 5.4 Backoff + graceful degradation (reliability for a *real* deployment)
- One exponential backoff retry inside the wrapper (2s → ~5s) on the first failure; a second failure drops straight to local fallback — **no spin, no user-visible hang** (hard 22s timeout).
- `claude -p --output-format json` subprocess is the **L2.5** safety net if the *SDK import itself* fails on the judge's clean venv (`subprocess.run(["claude","-p",prompt,"--output-format","json","--max-turns","1"], timeout=…, env={...,"CLAUDE_CODE_OAUTH_TOKEN":tok})` → parse `.result`). Same OAuth token, no key.
- A lightweight in-process **token-bucket** (e.g. 8 calls/min) gates L2 so a runaway loop can't burn the session quota; when the bucket is empty the wrapper skips straight to L3/template and surfaces a quiet "running in offline mode" badge in the UI (honest, and it scores on "doesn't break").

### 5.5 The honesty/UX guarantee
Because **every** LLM call has a deterministic fallback that already exists in `nodes.py`, the worst-case behaviour under a total subscription outage is: the Wizard answers correctly with template prose and a small "offline mode" indicator. **It never shows a traceback, never blanks, never crashes** — which is precisely the 7-axis webinar bar (fast/efficient/accurate/easy/doesn't-break/no-errors/smooth). We state the subscription dependency + offline fallback explicitly in `docs/ARCHITECTURE.md` (judges score honesty).

---

## 6. Migration checklist (surgical — one seam, no architecture change)

1. **Add** `wizard/core/llm.py` (`subscription_llm` + async twin) and `wizard/core/response_cache.py` (semantic cache, reuses bge-small).
2. **Replace** the LiteLLM/Gemini body of `wizard/agents/nodes.py::_llm_complete` with a call to `subscription_llm()`; keep its JSON-fence parser and its `return None → fallback` contract **unchanged** (so all 6 nodes' fallbacks keep working untouched).
3. **Repoint** the HyDE helper in `rag/retriever.py`, the 5-whys helper in `ml/rca_engine.py`, and the synthetic-data helper in `knowledge/generator.py` to the same wrapper (or disable HyDE by default).
4. **Rewrite** `wizard/core/config.py` LLM fields: drop `gemini_api_key` requirement; add `claude_code_oauth_token`, `wizard_llm`, `wizard_llm_model`, `wizard_llm_timeout_s`; keep `llm_model_fallback=ollama/qwen2.5:3b`. Default `llm_provider="subscription"`.
5. **Update** `.env.example` per §2.1; **delete** `GEMINI_API_KEY` lines.
6. **Extend** `scripts/capture_demo_cache.py` to write the `(system,user)`-hash-keyed `demo_cache.json` the wrapper reads, covering all `HAPPY_PATH.md` beats.
7. **Secret check:** `grep -rE 'AIza|sk-(?!ant-oat)|GEMINI_API_KEY' .` returns nothing before zip (the only `sk-ant-oat…` is an OAuth token, which is Boss's subscription credential — keep it out of the committed `.env`, ship `.env.example`).
8. **Cold-venv smoke test:** fresh `pip install -e .`, `WIZARD_LLM=off` → full demo runs on templates (proves offline correctness); then `WIZARD_LLM=on` with token → prose upgrades, cache warms.

**No changes** to RAG, KG, ML, WRPS, alerting, or UI logic — they were already key-free and local.

---

## 7. Honest limitations (state these in ARCHITECTURE.md)
- **Throughput is the subscription's, not an API tier's.** Heavy concurrent interactive use can hit a session limit; the design absorbs it via cache + local fallback, but raw LLM-prose throughput is bounded. For a production Tata deployment this would move to a hosted endpoint — the LiteLLM-shaped seam means swapping the L2 layer for any provider is a one-file change.
- **Determinism vs fluency trade:** under fallback, answers are correct but read as templated. We accept this consciously — correctness and uptime beat fluency for a maintenance decision-support tool.
- **Synthetic-data domain gap** (covered in the data design doc) is orthogonal to the LLM layer but stated here too for completeness.
- **`max_turns=1` means the LLM can't self-correct via tools** — by design; the local layers are the source of truth, the LLM only narrates, so it doesn't need tools.
