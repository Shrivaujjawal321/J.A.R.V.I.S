# LOCAL LLM RECOMMENDATION — Maintenance Wizard runtime brain
## Tata Steel R2 · Subscription vs Local-SLM vs HYBRID — the decision + provider ladder

**Author:** Jarvis · **Date:** 2026-06-09 · **Deadline:** 15 Jun 2026 23:59 IST · SOLO
**Synthesises:** `06_local_llm_cpu_reality.md` (CPU tok/s + thermal facts), `07_local_llm_quality_gap.md` (node-by-node quality), `08_finetuned_slm_as_runtime.md` (GGUF→Ollama→LiteLLM wiring), and `MASTER_ARCHITECTURE_AND_PLAN.md` (the L0–L3 ladder + measured 11–12 s subscription call).
**Decision record. This is the authoritative answer to "do we run on a local LLM?"**

> **HARD CONSTRAINTS that govern the answer.** CPU-only laptop, no GPU. No paid API key — only Claude Max via `CLAUDE_CODE_OAUTH_TOKEN`. A single subscription call spawns a `claude` CLI subprocess → **measured ~11–12 s**, and the subscription has real session/rate limits we have hit mid-build. A local Qwen2.5-3B Q4_K_M on this x86 CPU runs **~6–12 tok/s → a 300-token answer in ~25–50 s**, but is keyless, offline, and rate-limit-immune. The deliverable is a **recorded 4-min demo + source ZIP**, not a live service. We already own a fine-tune kit (Qwen2.5-3B QLoRA, 969 SFT examples, Colab T4, GGUF export). Tata rewards FR1 (LLM/SLM reasoning, **extra merit for a domain fine-tune**), FR4 (explainable + traceable), and 7 ops qualities incl. **Fast / doesn't-break / smooth**.

---

## 1. DECISION MATRIX

Three options. **A) subscription-only** (Claude Max is the only LLM, deterministic template is the floor). **B) local-SLM-only** (fine-tuned Qwen2.5-3B on Ollama is the only LLM, no Claude at runtime). **C) HYBRID** (offline-pre-baked Claude answers in the L0 demo cache + fine-tuned SLM as keyless live fallback + template floor — the provider ladder in §3).

Scored 1–5 (5 = best). Weighted toward the axes Tata actually scores.

| Axis | A · Subscription-only | B · Local-SLM-only | C · HYBRID (recommend) |
|---|---|---|---|
| **API-key / offline** (judge box, no net) | 2 — needs OAuth token resolvable + network; dies fully offline unless it drops to template | 5 — 100% keyless + offline; nothing leaves the box | **5** — demo runs from cache + SLM + template with net OFF and token unset |
| **Rate-limit safety** | 2 — we WILL hit the session limit under ad-lib; degrades to template (correct but templated) | 5 — zero rate limit, ever | **5** — scored path is cache (0 calls); live fallback is keyless SLM, never the rate-limited path |
| **Demo robustness** (must not die on camera) | 3 — safe only because the recording is forced 100% cache; any live miss is a 30–45 s stall | 4 — never stalls on a limit but a live miss is a 25–50 s SLM decode on camera | **5** — L0 cache sub-ms for all 5 beats; misses fall to template ~200–400 ms; SLM only off-camera/Q&A |
| **Answer quality** (prose, FR4 5-whys) | 5 — frontier coherence on multi-hop RCA + multi-turn | 3 — fine-tune lifts DIAG/PLAN to "adequate"; RCA 5-hop chaining is its weakest task; reads templated | **5** — Claude prose is *baked into the cache* so the demo shows frontier quality at sub-ms playback |
| **CPU speed** (live, no cache) | 2 — 11–12 s/call, 30–45 s cold turn | 2 — TTFT ~400 ms (feels alive) but 25–50 s full answer; thermal throttle after 10–15 min | **4** — scored path is sub-ms cache; template floor ~200–400 ms; slow paths never user-visible |
| **Judge story — FR1 fine-tune merit** | 2 — fine-tune is an optional stretch, not in the live loop; weak "extra merit" claim | 5 — the fine-tuned SLM IS the runtime brain; strongest possible FR1 story | **5** — SLM is a *named live provider* (visible in Phoenix trace + Settings page) + eval before/after JSON in ZIP; full merit without betting the demo on it |
| **Build effort / risk** | 3 — must land `claude_agent_sdk` + event-loop bridge + key scrub (already core-path work) | 4 — needs Colab run to succeed + Ollama pre-pull; if eval fails, fall to base qwen | **3** — = A's work + the SLM rung (already specced in `08`) + offline cache-bake of Claude answers; most moving parts but each is small and fail-soft |
| **Weighted verdict** | **Adequate floor** | **Keyless, but reads templated as the scored path** | **★ Best across every Tata-scored axis** |

**Reading the matrix:** A maximises *quality* but is fragile (key + net + rate limit) and a weak FR1 story. B maximises *FR1 + offline* but its live quality on the scored path reads templated and a live miss is a 25–50 s decode on camera. **C takes the best column of each: Claude's quality (pre-baked, so it plays back instantly), the SLM's keyless safety + FR1 merit (as a live provider, not a stretch), and the template's unbreakable floor.**

---

## 2. RECOMMENDATION — HYBRID provider ladder, with Claude pre-baked OFFLINE into the demo cache

**Ship Option C.** Concretely:

1. **Pre-generate every scripted demo answer with Claude, OFFLINE, into `data/demo/demo_cache.json`.** Run the 5 beats + CONV-001 turns once on Boss's machine while Claude is reachable; capture the frontier-quality prose into the L0 cache (`demo_cache.json` already exists with 9 keys — extend it). On demo day the recording plays these back **sub-ms, zero live LLM calls** — so the judge sees *Claude-tier quality at cache speed*, immune to rate limits, network, and the 11–12 s subprocess cost. This is the single highest-leverage move: it decouples *quality* (Claude, baked) from *latency + availability* (cache, instant).

2. **Use the fine-tuned local SLM (`ollama/maintenance-wizard`) as the keyless live fallback AND the FR1 showcase.** When a judge ad-libs off-script and misses L0/L1, the keyless SLM answers (TTFT ~400 ms feels alive on camera). It is a **named, live provider** — visible in the Arize Phoenix trace and the Streamlit Settings page — which is the strongest FR1 "extra merit: domain fine-tune" evidence achievable without a GPU. The 969-example QLoRA notebook + SFT data + before/after `eval_results.json` ship in the ZIP as Layer-1/Layer-2 proof.

3. **Deterministic template is the unbreakable floor.** Every node already has a spine-grounded template (`07` §2.5, `08` Risk-4). If Claude is unreachable AND Ollama is down, the answer is still correct, cited, and ~200–400 ms. The demo cannot break.

**Why HYBRID over the alternatives — the reasoning:**

- **vs A (subscription-only):** A's quality is identical *because we bake Claude's output into the cache anyway*. HYBRID adds, for near-zero extra build, the keyless SLM rung — which (a) turns a weak "optional stretch" FR1 claim into a live-serving fine-tune (full merit), and (b) gives a graceful live fallback that isn't the rate-limited path. A loses nothing C keeps; C gains the FR1 story + offline safety.
- **vs B (local-SLM-only):** B's scored demo prose is the SLM's, which `07` honestly rates "adequate for DIAG/PLAN, marginal for RCA, reads templated." Tata scores FR4 (explainability prose) and JC5 (presentation). HYBRID puts *Claude's* prose on the scored path (baked) while *keeping* the SLM as the live/FR1 layer — best quality AND best FR1, where B forces a trade.
- **The provider ladder makes the choice non-exclusive.** It is not "Claude vs local" — it is a fall-through ladder where each rung covers the previous rung's failure mode. That is the architecturally honest answer to "no API key + CPU-only + must not break + reward fine-tune."

**One-line headline:** *Bake Claude's quality into the cache (offline), serve it instantly, and let the fine-tuned local SLM be the keyless live fallback + the FR1 merit showcase — template as the floor that never breaks.*

---

## 3. PROVIDER-LADDER DESIGN AT `wizard/core/llm.py`

The chokepoint is the single door to all LLM text. `nodes.py::_llm_complete` (and the 3 other call sites: `rca_engine.py:425`, `wrps.py:327`, `middleware.py:213`) become thin adapters over it. **It never raises — returns `None` to signal "use your deterministic template."**

### 3a. The ladder (selection + fallback order)

```
subscription_llm(system, user, task, timeout_s=45) -> str | None
  │
  ├─ L0  demo_cache.json            exact (system,user)-hash → return  | sub-ms,  0 LLM calls   ← SCORED DEMO
  ├─ L1  semantic response cache    bge-small cos ≥ 0.88 (demo) / 0.94 (prod) | <50 ms, 0 calls ← ad-lib hits
  ├─ L2  Claude Agent SDK (OAuth)   _model_for(task) → query(max_turns=1, tools=[]) | ~11–12 s, 1 backoff retry
  │        └─ on 429 / session-limit / timeout / SDK import fail → fall to L3 (no raise)
  ├─ L3  local_slm  ollama/maintenance-wizard (format=json + instructor retry) | TTFT~400ms, 25–50s | 0 key
  │        └─ if Ollama down / parse fail after retries → fall to L4
  └─ L4  deterministic template     spine + RAG chunks (caller builds it on None) | <1 ms, always correct
```

`L0/L1` are populated by `response_cache.py` (reuses the bge-small embedder; pre-warmed from the 260 `user_interaction` prompts + the demo script). `L2` is the proven `jarvis_core` / `dataforge agent.py::_subscription_review` Agent-SDK pattern with the event-loop-safe sync shim (`MASTER` §4.6). `L3` is the `08` wiring: `litellm.completion("ollama/maintenance-wizard", format="json")` + `instructor` 3-retry + Pydantic validate. `L4` is the existing template path in `nodes.py`.

### 3b. Selection logic — provider mode × task

The provider ladder is **mode-gated** so Boss can flip behaviour from `.env` without touching code. `WIZARD_LLM` (`cache_first` | `live` | `off`) controls which rungs are live; `LLM_PROVIDER` (`subscription` | `local_slm` | `template`) controls the *primary engine* of the L2/L3 band; `_model_for(task)` differentiates nodes.

```python
# wizard/core/llm.py  — the chokepoint (shape; full body per MASTER §4.3/4.6 + 08 §2)
import os, asyncio, hashlib, logging
os.environ.pop("ANTHROPIC_API_KEY", None)   # OAuth token must out-rank any stray key

def _model_for(task: str) -> str:
    """LiteLLM/SDK model string for this task, per provider mode (08 §2b)."""
    p = settings.llm_provider                       # subscription | local_slm | template
    if p == "template":      return ""              # forces L4 (None) — deterministic floor
    if p == "local_slm":     return settings.llm_model_primary   # ollama/maintenance-wizard for all
    # p == "subscription": node-differentiated (07 §4) — Claude for the hard reasoning nodes
    if task in ("rca", "multiturn"):  return settings.llm_model_heavy    # claude sonnet-tier
    return settings.llm_model_light                                       # claude haiku-tier DIAG/PLAN

def subscription_llm(system, user, task="diagnosis", timeout_s=45) -> str | None:
    key = hashlib.sha256(f"{system}\x00{user}".encode()).hexdigest()
    if (hit := demo_cache.get(key)) is not None:        return hit          # L0
    if (hit := response_cache.semantic_get(user)) is not None: return hit   # L1
    if settings.wizard_llm == "off" or settings.llm_provider == "template":
        return None                                                         # → L4 template
    model = _model_for(task)
    if model.startswith("ollama/"):                                         # local_slm primary
        out = _local_slm(model, system, user, timeout_s)                    # L3 (format=json+instructor)
        return out  # None → L4
    # subscription primary: L2 Claude SDK (event-loop-safe shim, 1 backoff retry) → on fail, L3 → L4
    out = _claude_sdk(model, system, user, timeout_s)                       # L2; returns None on any fail
    if out is None and settings.llm_model_fallback.startswith("ollama/"):
        out = _local_slm(settings.llm_model_fallback, system, user, timeout_s)  # L3 keyless fallback
    response_cache.put(user, out) if out else None
    return out                                                              # None → caller uses L4
```

`config.py` already exposes `llm_provider` (extend the `Literal` with `"subscription"` and `"local_slm"`; default `"subscription"`), `llm_model_primary/heavy/light/fallback`. `.env` blocks (from `08` §2a):

```ini
# DEMO DEFAULT — quality from cache, SLM keyless fallback, template floor
LLM_PROVIDER=subscription
WIZARD_LLM=cache_first
LLM_MODEL_HEAVY=<claude sonnet-tier>     # RCA + multi-turn
LLM_MODEL_LIGHT=<claude haiku-tier>      # DIAG + PLAN
LLM_MODEL_FALLBACK=ollama/maintenance-wizard   # keyless live fallback (L3)

# FR1-SHOWCASE / fully-offline mode — SLM is the runtime brain
# LLM_PROVIDER=local_slm
# LLM_MODEL_PRIMARY=ollama/maintenance-wizard
# LLM_MODEL_FALLBACK=ollama/qwen2.5:3b

# FLOOR-ONLY (cold-start proof) — no LLM at all, deterministic templates
# LLM_PROVIDER=template
```

**Key property:** the OAuth token never lives in the wizard `.env` (resolved by `_load_oauth_token()` walk-up to repo-root); the `ollama/` rung needs no key at all; the template needs nothing. So **every rung except L2 is keyless**, and L2 fails soft to keyless rungs.

---

## 4. WHAT THIS CHANGES IN THE EXISTING BUILD PLAN (ordered)

The `MASTER` plan already specifies the subscription path + L0–L3 ladder. HYBRID is a **small superset** — it promotes the SLM rung from "optional stretch" to "named live fallback + FR1 showcase" and adds the offline Claude-bake step. Ordered deltas:

1. **GATE 0 / WAVE 1 (Track A) — unchanged spine.** Install + pin `claude-agent-sdk==0.1.81`; write `wizard/core/llm.py` with the §3 ladder (event-loop-safe `subscription_llm`); scrub the live `GEMINI_API_KEY` from `.env`; `os.environ.pop("ANTHROPIC_API_KEY")`. This is already the plan — no change.
2. **Add the SLM rung to the chokepoint NOW (not as WAVE-2 stretch).** Wire L3 `_local_slm()` (LiteLLM `ollama/...` + `format=json` + `instructor` 3-retry + Pydantic) and the `_model_for(task)` selector into `llm.py` in WAVE 1. Cost is ~40 lines; `litellm` ollama support is native (no adapter). Until the GGUF exists, point `LLM_MODEL_FALLBACK=ollama/qwen2.5:3b` (base) so the rung is testable immediately.
3. **Extend `config.py` Literal** to `["subscription","local_slm","template","gemini","ollama","claude","openai"]`; default `subscription`; add `wizard_llm` (`cache_first|live|off`).
4. **WAVE 2 — run the Colab QLoRA (async, separate worker).** 969 examples, rank-16, 2 epochs, T4, `save_steps=200`. Export GGUF Q4_K_M + Modelfile. **Eval gate:** ship `ollama/maintenance-wizard` only if `eval_results.json` composite delta > 0 vs base; else keep `ollama/qwen2.5:3b` and soften (not drop) the FR1 claim. On the demo laptop: `ollama create maintenance-wizard -f Modelfile` + **pre-pull/warm 24 h before recording** (`08` Risk-1, `06` §5).
5. **WAVE 3 — bake Claude into the cache OFFLINE (the HYBRID move).** Extend `capture_demo_cache.py` to `(system,user)`-hash keys; run the 5 beats + CONV-001 once **live with Claude reachable** to populate `demo_cache.json` with frontier prose. Pre-warm L1 from the 260 prompts at cos ≥ 0.88 (demo build). Then **cold-start test: clean venv, network OFF, OAuth token unset** → full recording completes from L0 cache + L4 template (and L3 SLM for any ad-lib) with zero live-Claude dependency.
6. **Make the SLM visible for FR1 scoring.** Confirm the Streamlit Settings page surfaces `settings.llm_model_primary` (= `ollama/maintenance-wizard` in showcase mode) and that the Phoenix trace shows the model name. Put the `08` §3 design-doc quote + before/after eval table in `ARCHITECTURE.md`.
7. **Docs / limitations (`MASTER` §9).** State plainly: demo prose is Claude baked into cache; live keyless fallback is the fine-tuned SLM at 25–50 s/answer; template is the floor. Honesty is scored (JC4/JC5).

**Net:** no new architectural risk — HYBRID is the existing ladder with the SLM rung pulled forward and a one-time offline Claude-bake. Every rung is fail-soft; the floor is unchanged.

---

## 5. HONEST TRADE-OFFS · when to pick LOCAL-ONLY vs HYBRID

**HYBRID costs more moving parts.** You maintain three rungs (cache-bake freshness, Ollama-up, template). Mitigation: each is independently fail-soft, and the cold-start test proves the whole thing survives any single rung dying.

**The SLM's live answer is slow on camera (25–50 s).** That is why it is the *fallback/ad-lib* path, never a scored beat — scored beats are L0 cache (sub-ms). If a judge insists on a free-text ad-lib, TTFT ~400 ms makes it *feel* alive while it streams, which `06` §3 notes is actually a UX win ("watch it think, fully on-device"). Frame it that way.

**The fine-tune might not beat base.** Hard gate (`08` Risk-2): if `eval_results.json` shows no improvement, use base `qwen2.5:3b` for the rung and present the *attempt + honest eval* — judges score the rigor. The demo and L0 cache are unaffected either way.

**Pick LOCAL-SLM-ONLY (Option B) instead of HYBRID only if:**
- The demo must provably run with **no Anthropic involvement at all**, even at bake time (e.g. a judge requirement that nothing ever touched a cloud LLM) — then you cannot bake Claude into the cache, so the SLM (or template) must be the scored path. Accept the templated-prose quality hit.
- The Colab fine-tune lands strongly AND you want the cleanest possible single-story FR1 narrative ("our fine-tuned SLM IS the product, end to end, keyless") and are willing to trade FR4 prose polish for it.
- Boss explicitly wants zero dependency on the subscription's availability *during the bake window* (e.g. travelling, no reliable net before the deadline).

**Pick HYBRID (default) in every other case** — it strictly dominates A and B on the Tata-scored axes because the provider ladder is non-exclusive: Claude's quality (baked), the SLM's keyless safety + FR1 merit (live), and the template's unbreakable floor, all at once.

---

## 6. ONE-LINE DECISION

**HYBRID (Option C): pre-bake Claude's frontier-quality answers OFFLINE into the L0 demo cache for instant, rate-limit-proof playback of every scored beat; run the fine-tuned Qwen2.5-3B (`ollama/maintenance-wizard`) as the keyless live fallback and the FR1 extra-merit showcase; keep the deterministic spine-grounded template as the unbreakable floor — all behind one `subscription | local_slm | template` ladder at `wizard/core/llm.py`. It is the existing plan's ladder with the SLM rung promoted from stretch to first-class, and it wins on every axis Tata scores: offline, rate-limit-safe, demo-robust, top-quality, fast (on the scored path), strongest FR1 fine-tune story.**
