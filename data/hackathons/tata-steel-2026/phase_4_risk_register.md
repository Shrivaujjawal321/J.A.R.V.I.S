# Phase 4 — Risk Register & Critique (3-Problem Portfolio)

**Compiled:** 2026-05-14 (Daemon synthesis — `hackathon-critique-agent` rubric applied)
**Scope:** Adversarial critique of all 3 Phase-3 solutions, applying spec §10 rubric — weak assumptions, scalability, security, demo failure modes, judge-appeal gaps, time-budget overruns, boring-tech penalties, mandatory-tech under-utilisation, differentiation gap, eval/measurability.

**Aggregate verdict:** `approve_with_changes` — all 3 cleared the 6.5 composite floor; combined platform is feasible within 60h budget. **3 critical mitigations** flagged below — Boss must execute these in Phase 1 build for portfolio to hold.

---

## Critique 1: `surface-defect-vlm-rca`

### Risk Register

| Risk | Sev (1-5) | Likelihood (1-5) | Mitigation | Owner |
|---|---:|---:|---|---|
| Round 1 dataset is NOT image-based → CV core idle | 5 | 3 | Have tabular-feature-extraction fallback ready (CNN-as-feature-encoder pattern). Day 5 Phase 1 deliverable. | ML engineer |
| Gemini Vision API rate-limit during demo | 4 | 3 | Pre-cache 30 representative responses. Backup: Claude Vision API as drop-in. | ML engineer |
| "We already have Safety EyeQ" — differentiation gap | 5 | 4 | VLM-RCA layer MUST be the visible differentiator. Demo narrative: "Safety EyeQ classifies, mine explains the cause". Pitch deck slide 4 = side-by-side comparison. | Boss (pitch) |
| Demo image quality (synthetic samples spotted by judges) | 3 | 4 | Use real industrial photos from Pexels + GitHub repos. Label `[demo set — real photos, fictional context]`. | ML engineer |
| Heatmap interpretation could mislead RCA | 3 | 2 | Use Grad-CAM++ + smoothed Grad-CAM ensemble; show confidence threshold. | ML engineer |
| Class imbalance worse than NEU on real Tata dataset | 4 | 3 | Focal loss γ=2 + class-balanced sampler; metric: F1-macro not accuracy. | ML engineer |
| Time-budget overrun on Round 2 polish | 3 | 3 | Hard cutoff: 10 hrs for Round 2 share of this problem. Boilerplate Streamlit panel ready Day 7 Phase 1. | Boss (PM) |

### Critique findings

**Weak assumptions:**
- Assumes Tata Steel's Round 1 dataset has image component. If purely tabular sensor data, this problem's ML core idles → Round 1 leaderboard rank from this drops to zero. **Critical:** must have tabular-extraction fallback.

**Scalability ceilings:**
- Production scale needs Cloud Run + GPU pool — out of hackathon scope but mention as roadmap in Round 3 narrative.

**Security exposures:**
- Image uploads accept arbitrary content → must validate format + size limits in Streamlit. Low priority for demo but Round 3 interviewer may probe.

**Demo failure modes:**
- Gemini API down at live demo time = catastrophic. Backup plan: pre-recorded inference results for 5 canonical scenarios.

**Judge-appeal gaps:**
- Safety EyeQ shadow is the dominant risk. VLM-RCA framing must hit in first 30 seconds of demo or judges check out.

**Time-budget:** 8 hrs MVP + 8 hrs polish = 16 hrs. Within scope.

**Boring-tech penalty:** Low. Gemini Vision + agentic routing is contemporary.

**Mandatory-tech utilisation:** N/A — Tata hackathon has no mandatory tech.

**Differentiation:** VLM-RCA layer. Must own this narrative.

**Eval measurability:** Round 1 = F1-macro on leaderboard. Round 2 = 15-scenario rubric with per-scenario score.

### Re-scoring (post-critique)

| Dim | Phase 3 | Phase 4 | Reasoning |
|---|---:|---:|---|
| Innovation | 8 | 7 | Safety EyeQ shadow lowers genuine novelty |
| Judge Appeal | 9 | 8 | Same shadow concern |
| Feasibility | 9 | 8 | Round 1 dataset fit risk acknowledged |
| Technical Depth | 8 | 8 | — |
| Business Potential | 8 | 8 | — |
| **Composite** | **8.40** | **7.85** | Still well above 6.5 floor |

**Verdict:** `approve_with_changes` — execute tabular-fallback + VLM differentiation narrative mitigations.

---

## Critique 2: `eaf-electrode-pdm`

### Risk Register

| Risk | Sev (1-5) | Likelihood (1-5) | Mitigation | Owner |
|---|---:|---:|---|---|
| Round 1 dataset is image-based, not time-series | 5 | 3 | PHM-pretrained features can also feed CNN pipeline; pivot path exists. | ML engineer |
| Synthetic EAF sensor data unrealistic | 4 | 3 | Use published Tata Steel Jamshedpur EAF papers for physics constraints. Day 5 Phase 1 review session. | ML engineer |
| LightGBM underperforms ensemble on real Tata dataset | 3 | 3 | Stacked ensemble (XGB + LGB + CatBoost) ready Day 6. | ML engineer |
| Tier-3 confirm UX in demo is buried | 3 | 4 | Approval dialog MUST appear as modal with clear "approve / hold" buttons. Demo Day 8 review. | UI engineer |
| Quantile bands miscalibrated → false alarms | 4 | 3 | Conformal calibration on holdout set Day 7. | ML engineer |
| Parts-ordering tool stub looks fake to judges | 3 | 4 | Make it look real — call to mock API with realistic JSON response + loading state. | UI engineer |
| "We have Asset Sphere already" — judge counter | 4 | 4 | **Critical narrative:** Asset Sphere is BF-era; this is EAF-era. Pitch slide 3 = direct comparison. | Boss (pitch) |
| Maintenance scheduler logic over-simplified | 3 | 3 | Use real maintenance heuristics (parts availability + crew shift). | ML engineer |

### Critique findings

**Weak assumptions:**
- Assumes EAF context applies to Round 1. If Tata's dataset is image / quality classification, the time-series MVP idles. Same dataset-uncertainty problem as #1.

**Scalability:**
- Production: edge inference + Pub/Sub → BigQuery. Already documented as roadmap.

**Security:** PdM models in critical infra need adversarial robustness — flag as Round 3 talking point.

**Demo failure modes:**
- Tier-3 confirm dialog must be prominent, not a footnote. If judges miss it, the safety-architecture story dies.

**Judge appeal:** EAF transition is Tata Steel's $3.5B bet — story resonates IF judges are aware of the BF→EAF strategic context. Bake this into pitch slide 2.

**Time budget:** 8 hrs MVP + 8 hrs polish + 5 hrs Tier-3 UX = 21 hrs. Tight but within scope.

**Boring-tech:** LightGBM is classical — needs ensemble + quantile + conformal to elevate. Done.

**Differentiation:** EAF-era PdM gap vs Asset Sphere's BF coverage. Strong if framed correctly.

**Eval:** Round 1 = RMSE/MAE (if RUL) or F1 (if classification). Round 2 = 15-scenario PdM-specific rubric.

### Re-scoring (post-critique)

| Dim | Phase 3 | Phase 4 | Reasoning |
|---|---:|---:|---|
| Innovation | 7 | 6 | Honest — PdM is well-trodden, EAF-spec is the only novel angle |
| Judge Appeal | 9 | 8 | Strong if framed, but BF/EAF nuance may be lost on non-domain judges |
| Feasibility | 9 | 9 | Time-series + LightGBM is Boss's strongest classical ML zone |
| Technical Depth | 8 | 8 | — |
| Business Potential | 9 | 9 | $3.5B capex aligned |
| **Composite** | **8.35** | **7.80** | Above floor |

**Verdict:** `approve_with_changes` — execute Asset-Sphere-differentiation pitch + Tier-3 UX prominence + synthetic data realism.

---

## Critique 3: `quality-escape-rca`

### Risk Register

| Risk | Sev (1-5) | Likelihood (1-5) | Mitigation | Owner |
|---|---:|---:|---|---|
| Synthetic complaint data spotted as fake | 5 | 4 | **Critical:** Spend extra Day 5 on complaint corpus realism. Use real industry vocabulary from Tata Steel Quality Manual references. | ML engineer |
| Round 1 dataset isn't multi-class root-cause classification | 4 | 4 | Stacked ensemble base is generic; can degrade to binary or regression. | ML engineer |
| 5-whys hallucinates (causal claims without evidence) | 5 | 4 | **Critical:** Strict RAG-grounded prompt template. Each "because X" MUST cite retrieved chunk. Critic loop in Phase B catches violations. | Prompt engineer |
| Customer response auto-sent (Tier-3 fails) | 5 | 1 | Already built — Tier-3 always confirms via jarvis-core safety framework. Tested. | jarvis-core |
| Multi-class imbalance → minority causes never predicted | 4 | 4 | SMOTE-NC + class-weighted ensemble + focal loss fallback. | ML engineer |
| Cohere rerank API cost spike | 2 | 3 | Free tier covers demo scenarios; budget $5 max. | ML engineer |
| Demo cognitive load too high (judges confused) | 4 | 4 | Stage demo: simple scenario first (1 cause) → progressive complexity (multi-modal final). | Boss (UX) |
| 4-specialist orchestration latency overrun | 3 | 3 | Async parallel calls; 12s budget enforced. | jarvis-core |

### Critique findings

**Weak assumptions:**
- Assumes synthetic complaint data is realistic. Tata Steel judges deal with real complaints daily — they SPOT lazy synthetic data instantly. **#1 risk in portfolio.**
- Assumes 5-whys narrative will land. If judges are deep-causal-inference researchers, they'll want DoWhy or DAG-based reasoning.

**Scalability:**
- Production: complaint stream from CMS → Cloud Run → BigQuery. Documented.

**Security:**
- Customer-facing response generation = brand risk. Tier-3 confirm is the safety architecture. **Major Round 3 talking point.**

**Demo failure modes:**
- 5-whys can drift if RAG retrieves wrong chunks. Pre-vet 15 demo scenarios; ensure RAG hits are correct.
- Cognitive load: too many panels on screen. Limit to 3 visible at any time (intake → reasoning trace → response draft).

**Judge appeal:** 50% complaint TAT KPI alignment is GOLD. Lead with this in 30-second pitch.

**Time budget:** 10 hrs MVP + 10 hrs polish + 5 hrs synthetic data realism = 25 hrs. Tightest of the 3 but technical depth justifies.

**Boring-tech penalty:** Low. Stacked ensemble + multi-modal + agentic RAG is current state-of-art.

**Mandatory-tech utilisation:** N/A.

**Differentiation:** TDA-extension framing (customer-facing where TDA is HR-facing). Strong.

**Eval:** Round 1 = F1-macro 8-class. Round 2 = scenario rubric × 15 + per-scenario citation correctness. Round 3 = pitch around 50% TAT KPI.

### Re-scoring (post-critique)

| Dim | Phase 3 | Phase 4 | Reasoning |
|---|---:|---:|---|
| Innovation | 8 | 7 | RCA agent novel but 5-whys + RAG is contemporary, not category-creating |
| Judge Appeal | 9 | 9 | 50% TAT KPI lockstep with Tata published goals |
| Feasibility | 8 | 7 | Highest complexity in portfolio; synthetic data realism is real risk |
| Technical Depth | 9 | 9 | Deepest of 3 — stacked + multi-modal + agentic + RAG-rerank |
| Business Potential | 8 | 8 | — |
| **Composite** | **8.30** | **7.85** | Above floor |

**Verdict:** `approve_with_changes` — execute synthetic complaint realism + 5-whys hallucination guard + demo cognitive load reduction.

---

## Portfolio-level critique

### Cross-cutting risks (all 3 problems share)

| Risk | Sev | Mitigation |
|---|---:|---|
| Round 1 dataset matches only ONE of 3 → other 2 idle in Round 1 | 4 | **By design** — portfolio approach guarantees coverage. The "idle" 2 still feed Round 2 demo. |
| Shared jarvis_core bug breaks all 3 | 5 | Pytest suite + 8-second critic timeout; rollback to last known good. |
| Demo cognitive load — judges confused by 3-problem scope | 4 | Crisp 90-second pitch: "Steel Operations Copilot — single query routes to right specialist." Avoid showing 3 separate apps; show ONE orchestrator. |
| Time budget overrun in Phase 1 prep (3 MVPs in 30 hrs) | 4 | Hard daily caps: 10 hrs/day max; 3 hrs per MVP per day; share infrastructure ruthlessly. |
| Synthetic data realism across 3 domains | 5 | Day 5-6 Phase 1 dedicated to data review — Boss compares synthetic samples against Tata Steel public reports for vocabulary. |
| Round 3 narrative dilution (3 stories instead of 1) | 3 | Frame as ONE story: "I built a multi-domain industrial AI platform mirroring Tata's 300+ agent strategy." |

### Top 3 must-execute mitigations (critical path)

1. **Tabular fallback for `surface-defect-vlm-rca`** — Day 6 Phase 1 deliverable. CNN-as-feature-encoder for tabular Round 1 scenario.
2. **Synthetic complaint realism for `quality-escape-rca`** — Day 5-6 Phase 1. Use real Tata Steel quality manual vocabulary; label `[synthetic]` everywhere.
3. **Tier-3 confirm UX prominence in `eaf-electrode-pdm`** — Day 8 Phase 1. Modal dialog, not footnote. Test in demo dry-run.

### Portfolio composite

Weighted by deployment likelihood per Round 1 dataset shape (image / time-series / tabular all ~equally likely):

**Portfolio composite ≈ (7.85 + 7.80 + 7.85) / 3 = 7.83**

Above 6.5 floor. **No problem rejected. No Phase 3 loop required.**

---

## Aggregate verdict

```yaml
verdict: approve_with_changes
verdict_reasoning: >
  Three-problem portfolio survives adversarial critique with all 3 above the 6.5
  composite floor (range 7.80-7.85). Honest re-scoring caught optimism in Phase 3
  (Safety EyeQ shadow on #1, PdM commoditization on #2, synthetic data risk on #3).
  Three critical mitigations identified and assigned to Phase 1 build deliverables.
  Portfolio composite of 7.83 supports the "build all 3" strategic bet — coverage
  across Round 1 dataset uncertainty + Round 2 multi-domain agentic demo +
  Round 3 portfolio firepower.
risk_register_size: 24 risks across 3 problems + 6 portfolio-level
critical_path_mitigations: 3
phase_3_loop_required: false
ready_for_phase_5: true
```
