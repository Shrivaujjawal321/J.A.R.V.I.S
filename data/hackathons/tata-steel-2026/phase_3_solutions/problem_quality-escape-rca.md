# Solution Research — `quality-escape-rca`

**Composite:** 8.15 · **Compiled:** 2026-05-14 (Daemon synthesis)
**Problem:** Root-cause analysis agent for quality escapes (defects passing internal QC, reaching customer). Multi-modal evidence fusion → causal hypothesis ranking.

---

## 1. Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│  CUSTOMER COMPLAINT INPUT                                                │
│  • Complaint text (operator note + customer description)                 │
│  • Product SKU + batch + heat number                                     │
│  • Optional defect photo                                                 │
└──────────────────┬──────────────────────────────────────────────────────┘
                   │ {complaint, sku, batch_id, heat_no, photo?}
                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  ROUND 1 ML CORE — Escape-Cause Classifier                               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Feature Pipeline                                                 │  │
│  │   • Process telemetry features (sensor windows during batch)     │  │
│  │   • Heat-cycle metadata                                          │  │
│  │   • Maintenance log features (days-since-last-PM)                │  │
│  │   • Inspection-stage features (which station passed it)          │  │
│  │   • NLP features from complaint text (BERT embedding)            │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Stacked Ensemble Classifier                                     │  │
│  │   ↓ Layer 1: XGBoost / LightGBM / CatBoost / Random Forest       │  │
│  │   ↓ Layer 2: Logistic Regression meta-learner                    │  │
│  │   → 8-class root-cause:                                          │  │
│  │     1. process_param_drift  2. raw_material_defect               │  │
│  │     3. equipment_wear       4. operator_error                    │  │
│  │     5. inspection_miss      6. metallurgical_anomaly             │  │
│  │     7. handling_damage      8. environmental                     │  │
│  │   → Per-class probability with SHAP feature attribution          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└──────────────────┬──────────────────────────────────────────────────────┘
                   │ {top_3_causes, probs, shap_values, evidence}
                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  ROUND 2 AGENTIC LAYER — jarvis_core orchestrator                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  tata-operations-orchestrator-agent (router)                     │  │
│  │       │                                                          │  │
│  │       ├──► tata-incident-rca-agent (lead specialist)             │  │
│  │       │    RAG over past escapes with similar signature           │  │
│  │       │    5-whys causal walk-down                                │  │
│  │       │                                                          │  │
│  │       ├──► tata-process-optimizer-agent (if upstream cause)      │  │
│  │       │    Recommends setpoint correction                        │  │
│  │       │                                                          │  │
│  │       ├──► tata-defect-detector-agent (if photo provided)        │  │
│  │       │    CV classification + VLM cross-check                   │  │
│  │       │                                                          │  │
│  │       └──► [external tool: complaint-management-system]          │  │
│  │            Updates ticket with hypothesis + suggested action     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└──────────────────┬──────────────────────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STREAMLIT DEMO UI                                                       │
│  • Complaint intake form (text + SKU + optional photo)                   │
│  • Live 5-whys reasoning trace                                           │
│  • Ranked root-causes with confidence + evidence citations               │
│  • Suggested customer response template                                  │
│  • TAT timer (judges value 50% reduction story)                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component list

| Component | Responsibility | Tech |
|---|---|---|
| `feature-pipeline` | Multi-modal feature extraction | Pandas + tsfresh + BERT embeddings |
| `classifier` | Stacked ensemble | XGBoost + LightGBM + CatBoost + LR meta |
| `orchestrator` | Multi-specialist routing | jarvis_core `/chat` |
| `rca-specialist` | 5-whys + RAG over past escapes | tata-incident-rca-agent + ChromaDB |
| `process-specialist` | Upstream-cause setpoint advice | tata-process-optimizer-agent |
| `cv-specialist` | Photo-based defect check | tata-defect-detector-agent |
| `tool: ticket-update` | Mock CMS integration | Stub for demo |
| `demo-ui` | Visible 5-whys trace | Streamlit with collapsible reasoning |

### Data flow

1. Complaint → feature pipeline → classifier
2. Top-3 root-causes + SHAP → orchestrator
3. RCA-specialist takes lead, retrieves similar past escapes (RAG)
4. If process-param drift → consult process-optimizer
5. If photo provided → CV-specialist verifies
6. 5-whys synthesised → ticket update + customer response draft
7. Tier-3 confirm before sending response to customer (always)

### Failure modes + mitigations

| Failure | Mitigation |
|---|---|
| No matching past escape in RAG | Fall back to general metallurgy literature + ML classifier confidence only |
| Classifier confidence low (no clear cause) | Surface uncertainty explicitly; recommend human investigation |
| Causal hypothesis is wrong | SHAP explanations + retrieved evidence allow human reviewer to override |
| Customer response auto-sent | Never — always Tier-3 confirm |
| Photo of unrelated product | CV-specialist flags low confidence; orchestrator de-weights |

### Deployment topology

- **Demo:** Streamlit
- **Production target:** Cloud Run for classifier API, BigQuery for complaint+telemetry join, Pub/Sub for new complaint ingest

---

## 2. Stack Selection — every choice with alternatives

### 2.1 Classifier core

| Option | Pros | Cons | Decision |
|---|---|---|---|
| **Stacked ensemble (XGBoost + LightGBM + CatBoost + LR meta)** ⭐ | Highest accuracy on multi-class tabular; widely respected | More code complexity | **Selected** — competition-grade |
| Single XGBoost | Simpler | Lower accuracy ceiling | Reject — judges want depth |
| Neural net + transformer | Trendy | Tabular ML is dominated by GBM — would lose to ensemble | Reject |
| AutoML (H2O, AutoGluon) | Easy | Black-box; judges want SHAP interpretability | Reject — but use as sanity check |

### 2.2 NLP component for complaint text

| Option | Pros | Cons | Decision |
|---|---|---|---|
| **sentence-transformers (all-mpnet-base-v2)** ⭐ | High quality, free, integrates with ChromaDB | English-bias | **Selected** |
| BERT base | Standard | Older | Reject |
| Cohere embeddings v3 | Higher quality | Paid + new dependency | Reject for demo |
| Voyage AI embeddings | Top-quality | Paid | Reject for demo |

### 2.3 Feature attribution

| Option | Pros | Cons | Decision |
|---|---|---|---|
| **SHAP (TreeSHAP for GBMs)** ⭐ | Industry standard, fast on trees, interpretable | — | **Selected** |
| LIME | Model-agnostic | Slower, less stable | Reject |
| Feature importance | Simple | Less granular per-prediction | Use as supplement |

### 2.4 RAG over past escapes

| Option | Pros | Cons | Decision |
|---|---|---|---|
| **ChromaDB hybrid (BM25 + semantic) + Cohere rerank** ⭐ | Boss's existing stack; rerank improves precision | Cohere rerank adds API cost | **Selected** — rerank pattern wins on Round 2 demo precision |
| ChromaDB semantic only | Simpler | Misses keyword matches | Reject |
| Elasticsearch | Mature | Overkill | Reject |

### 2.5 Causal framework

| Option | Pros | Cons | Decision |
|---|---|---|---|
| **5-whys + RAG-grounded narrative** ⭐ | Operator-familiar, demo-friendly | Less rigorous than DAG-based | **Selected** for demo — judges value narrative |
| DoWhy / EconML (causal inference) | Rigorous | Hard to fit in 60h, harder to demo | Reject for hackathon (mention as future work) |
| Bayesian Network | Interpretable structure | Needs prior elicitation | Reject |

### 2.6 Demo UI

| **Streamlit with collapsible 5-whys trace** ⭐ | Visual hierarchy of reasoning | — | **Selected** |

---

## 3. Data Strategy

### 3.1 Training data construction (synthetic — flagged)

Real Tata Steel complaints are proprietary. We construct a realistic synthetic dataset:

**Schema:**
```
complaint_id, sku, batch_id, heat_no, complaint_text,
process_telemetry (linked time-series),
maintenance_history (linked records),
inspection_path (linked QC records),
true_root_cause (ground truth label),
days_to_resolution
```

**Generation:**
- 5000-10000 synthetic complaints
- 8 root-cause classes (balanced + realistic class imbalance)
- Process telemetry: generated from EAF/BF/CC/HSM simulators
- Maintenance history: realistic distributions of PM intervals
- Complaint text: templated + paraphrased via LLM
- Label `[synthetic — for demo only]` everywhere

### 3.2 Realistic complaint templates

Examples (paraphrased + LLM-augmented):
- "Material received showed surface scale on 12% of coils from batch X. Rejected for automotive application."
- "Plate from heat #45872 fractured at customer's stamping operation. Sample inspected showed inclusion line."
- "Coil tension was off-spec by 8% on first 200m of batch Y."

### 3.3 Public reference data

- **NEU dataset** — visual reference for inclusion + scratch + scale defects (link photo→text)
- **Springer 2023 paper on RCA in steel manufacturing** — methodology grounding
- **Tata Steel public annual reports** — RAG corpus for plant-context

### 3.4 RAG corpus for Round 2

```
data/hackathons/tata-steel-2026/rag_corpus/
├── tata_steel_annual_2024.md (extracted text)
├── tata_steel_sustainability_2024.md
├── tata_steel_ai_case_studies.md (from Phase 1 sources)
├── synthetic_past_escapes_corpus.jsonl (100-200 fake past cases with full causal trace)
└── industry_standards_excerpts.md (ASTM / ISO references)
```

---

## 4. AI/ML Strategy

### 4.1 Round 1 model approach

```
Day 1: Baseline single XGBoost on synthetic tabular features → submit
Day 2: Add NLP embedding features (BERT pooled)
Day 3: 5-fold CV setup; stratified by root_cause class
Day 4: Stacked ensemble (XGBoost + LightGBM + CatBoost)
Day 5: SMOTE-NC oversampling for minority classes
Day 6: Optuna tuning (50-100 trials)
Day 7: SHAP analysis — feature pruning, interpretability check
Day 8: Final ensemble + reproducibility
Day 9: Submit
```

**Expected leaderboard position:** Top 15-25%. Stacked ensemble + NLP embeddings is competition-grade.

### 4.2 Round 2 agentic strategy

**Eval scenarios (15):**
1. Clear single cause (e.g., temp drift) → orchestrator → process-optimizer → setpoint fix
2. Multiple plausible causes → 5-whys walks deeper → RAG retrieves analogous case
3. Inspection miss (defect was there but station passed it) → suggests inspection re-train
4. Customer complaint without photo → text-only RCA path
5. Photo + complaint → CV + text fusion
6. Recurring escape (same SKU, third time) → priority escalation
7. Heat-cycle-correlated escapes → time-series anomaly view
8. ... 8 more

**Wow factors:**
- 5-whys collapsible trace in UI — judges click "why?" at each level
- SHAP feature plot visible — explainable AI for industrial domain
- Cost framing: each complaint = ~$5K avg cost; full TAT visible
- Suggested customer response draft (Tier-3 — never auto-sends)
- Stat: "50% TAT reduction" mirrors Tata Steel's published KPI

### 4.3 Evaluation method

- **Round 1**: F1-macro across 8 classes (high class imbalance expected). CV: stratified 5-fold.
- **Round 2**: Per-scenario rubric: correct root cause? correct evidence cited? correct action recommended? latency <15s?

### 4.4 Composite re-score

| Dimension | Phase 2 | Phase 3 reassessed |
|---|---:|---:|
| Innovation | 8 | 8 |
| Judge Appeal | 9 | 9 |
| Feasibility | 7 | **8** (synthetic data path validated) |
| Technical Depth | 9 | 9 |
| Business Potential | 8 | 8 |
| **Composite** | 8.15 | **8.30** |

---

## 5. Latency + cost budget

| Operation | Latency | Cost (USD) |
|---|---|---|
| Feature pipeline | ~50ms | $0 |
| Stacked classifier inference | ~30ms | $0 |
| NLP embedding | ~100ms | $0 |
| RCA agent + RAG (with rerank) | ~4-6s | ~$0.005 |
| Process-optimizer (conditional) | ~3s | ~$0.001 |
| CV-specialist (if photo) | ~2-4s | ~$0.0015 |
| Full orchestrator pass | ~10-14s | ~$0.008 |
| 15-scenario eval | ~3.5 min | ~$0.12 |

---

## 6. Top risks

1. **Synthetic complaint realism is critical** — judges at Tata Steel will spot lazy synthetic data. Mitigation: spend Day 4-5 of Round 2 building rich complaint templates with industry-real language.
2. **Multi-class imbalance (some causes rare)** — SMOTE-NC + class-weighted ensemble + focal loss as fallback.
3. **5-whys can hallucinate** — strict RAG grounding requirement; every "because" must cite retrieved evidence.
4. **Round 1 fit risk** — if Tata's dataset isn't a multi-class problem, partial reuse only. Mitigate: classifier base is generic enough to work as binary too.
5. **Customer response auto-send risk** — Tier-3 confirm always. Demo must visibly show the approval gate (interview-impressing safety story).
