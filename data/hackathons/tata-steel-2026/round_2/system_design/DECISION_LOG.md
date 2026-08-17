# VULCAN — Decision Log (ADRs)

**Standard (Boss, 2026-06-09):** We must WIN Round 2. Every decision is planned + justified, with a documented WHY and why the alternatives were rejected. Adversarially stress-tested before locking.

Status legend: ✅ locked · 🔨 building · 🔁 revisit if evidence changes

---

## ADR-1 — Names: persona **EDITH**, product **VULCAN**  ✅ locked (Boss confirmed 2026-06-09)
- **Decision:** Public AI persona = EDITH; the maintenance system product = VULCAN.
- **Why:** Named systems are memorable to judges; "Vulcan" = Roman god of the forge/fire/metal → tight steel theme; EDITH is Boss's chosen public identity (ties his brand together).
- **Alternatives considered:** keep generic "Maintenance Wizard"; ForgeSense; AEGIS; Sentinel.
- **Why rejected:** "Maintenance Wizard" is generic/forgettable; "Sentinel" collides with ArcelorMittal's real PdM platform (naming clash); ForgeSense/AEGIS weaker theme fit than Vulcan.

## ADR-2 — Build our own **flagship synthetic dataset** (physics-grounded)  ✅
- **Decision:** Generate a multi-modal dataset to the PS input spec 4.1–4.4 (15 assets, 51 scenarios, sensors, manuals, SOPs, incidents, spares, conversations).
- **Why:** Tata provided NO dataset (microsite question unanswered, confirmed); rules allow synthetic + public data; research confirmed **no public multi-equipment steel-PdM dataset exists**; we need internal consistency + accuracy across all input types.
- **Alternatives:** use only public datasets (NASA C-MAPSS / AI4I / Bosch); obtain real plant data.
- **Why rejected:** public sets are single-modality (sensors only), wrong domain, and don't cover manuals/SOPs/incidents/spares/Q&A; real plant data is unavailable + confidential.
- **Evidence:** dense per-equipment tables score 89–93 ("Excellent") on DataForge; cross-consistency = zero orphans; required-input accuracy 97–99 after tightening.

## ADR-3 — LLM brain = **Claude Max subscription (OAuth), NO API key**  ✅ (Boss confirmed)
- **Decision:** All agent reasoning runs through a single `subscription_llm()` chokepoint via `claude_agent_sdk` + `CLAUDE_CODE_OAUTH_TOKEN` (walk-up to repo-root `.env`); deterministic template = fallback floor. Run live Claude locally.
- **Why:** Boss has no API key, only a Claude Max subscription; pattern proven in `jarvis_core/daemon.py` + EDITH; Claude gives top reasoning for FR4 explainability; keyless = no leak + offline-capable recording.
- **Alternatives:** (a) Gemini/OpenAI **API key**; (b) **local SLM only** (Ollama Qwen2.5-3B); (c) hybrid.
- **Why rejected:** (a) violates no-key constraint — and a **live Gemini key leak was found in `.env` and scrubbed** (would have shipped to judges); (b) **hardware too weak** — verified i5-7300U (2c/4t, ~4 GB free) runs a 3B model at ~2–5 tok/s = 60–150 s/answer + swap → too slow for live + "Marginal" FR4 quality → lowers score. **Hybrid chosen:** Claude live (local) + Claude-baked cache (recording) + template floor + fine-tuned SLM shipped as FR1 *evidence* (not the live brain).
- **Trade-off accepted:** ~10–12 s per Claude call (subprocess); acceptable for local quality; demo uses cache for instant playback.

## ADR-4 — **New clean build (VULCAN)** vs patching the old `maintenance-wizard`  🔨 (Boss directed)
- **Decision:** Fresh build; port only the *proven keyless* components (bge-small embedder, FlashRank, NLI gate, ML patterns); drop all key-dependent code.
- **Why:** old repo had Gemini/litellm key dependency across 6+ call sites, an EAF-04 phantom asset, a Gemini-placeholder demo cache, and accumulated debt; clean build wires to the new dataset + subscription chokepoint from day one.
- **Alternatives:** patch the old repo in place.
- **Why rejected:** patching = repoint every key call site + fix phantom assets + carry latent debt; higher risk than rebuilding on the known-good parts.

## ADR-5 — RAG = **local bge-small + Chroma/LanceDB + FlashRank**  🔨
- **Why:** keyless, CPU-capable, proven in the old repo + Jarvis episodic memory.
- **Alternatives:** API embeddings (OpenAI/Voyage/Cohere).
- **Why rejected:** require an API key (violates constraint) + cost.

## ADR-6 — ML = **LightGBM (fault) + IsolationForest (anomaly) + WeibullAFT/LightGBM (RUL)**  🔨
- **Why:** research (09_sota_pdm_models) shows gradient boosting **beats** deep learning on C-MAPSS (RMSE ~6.6 vs Transformer ~13); CPU-friendly; explainable (SHAP); fast to train; the dense per-equipment tables already validate well.
- **Alternatives:** deep learning (LSTM / TCN / Transformer).
- **Why rejected:** heavier + slower on a CPU-only weak laptop, lower accuracy here, less explainable.

## ADR-7 — UI = **Streamlit**  🔨
- **Why:** fastest to build solo; demoable; a non-technical judge can drive it; CPU-light; the *recording* is what's scored.
- **Alternatives:** Next.js/React frontend (as used for DataForge).
- **Why rejected:** heavier + more build time with no benefit for a recorded demo; 6-day solo budget.

## ADR-8 — **DataForge kept SEPARATE** from VULCAN  ✅ (Boss chose option B)
- **Decision:** DataForge (data-quality platform) is a standalone product, not folded into the wizard.
- **Why:** Boss's explicit call — wants it as his own product + a networking move; avoids two-system demo confusion.
- **Alternatives:** fold DataForge in as a "Data Trust Score" badge inside the wizard (strategy agent's recommendation).
- **Why rejected:** Boss's decision.

## ADR-9 — Build process = **workflow waves + adversarial verification**  🔨
- **Why:** deterministic sequencing; each wave self-tests (boot + smoke); an adversarial agent challenges claims before we trust them — this is *how we avoid wrong choices*. Already caught: the live Gemini key, the hardware-too-weak reality, the phantom EAF-04 asset.
- **Alternatives:** ad-hoc building.
- **Why rejected:** ad-hoc misses integration + accuracy gaps and breeds wrong-but-unnoticed choices.

---

### Open decisions to lock (with Boss)
- Final product name (VULCAN vs alternative) — awaiting Boss confirm.
- Whether to ship the fine-tuned SLM as a live optional rung or ZIP-only evidence (depends on real measured speed on the i5-7300U).
- Demo scenario set + storyboard (which scenarios make the 5 beats).
