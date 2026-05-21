# Solution Research — `eaf-electrode-pdm`

**Composite:** 8.20 · **Compiled:** 2026-05-14 (Daemon synthesis)
**Problem:** PdM for EAF-era equipment health — graphite electrode, power quality, transformer, water-cooled panels. Fills Asset Sphere's BF-era gap.

---

## 1. Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│  EAF SENSOR STREAM (multimodal)                                          │
│  • Electrical: current, voltage, harmonics, flicker (1-50 kHz)           │
│  • Thermal: panel temp, electrode tip temp (1 Hz)                        │
│  • Acoustic: arc stability EMI                                           │
│  • Operational: melt cycle phase, power-on time, scrap mix                │
└─────────────────┬──────────────────────────────────────────────────────┘
                  │ time-series windows (10s, 60s, 300s)
                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│  ROUND 1 ML CORE — Multi-output PdM Model                                │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Feature Engineering Pipeline                                     │  │
│  │   • Rolling stats (mean, std, p95, p99) per window                │  │
│  │   • FFT features (1-5 kHz bands for arc stability)                │  │
│  │   • Lag features (t-1, t-5, t-60 min)                             │  │
│  │   • Cumulative features (heat-cycle total)                        │  │
│  │   • Domain interactions (current × electrode_age)                 │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Multi-output gradient-boosted model (LightGBM)                  │  │
│  │   ↓ Quantile regression (p10, p50, p90) for uncertainty          │  │
│  │   → 3 heads:                                                      │  │
│  │     • electrode_RUL_hours (regression)                            │  │
│  │     • transformer_anomaly (binary classification)                │  │
│  │     • panel_leak_risk (binary classification)                    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────┬──────────────────────────────────────────────────────┘
                  │ {RUL_hours, anomaly_flag, risk_score, confidence}
                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│  ROUND 2 AGENTIC LAYER — jarvis_core orchestrator                       │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  tata-operations-orchestrator-agent                              │  │
│  │            │                                                     │  │
│  │            ├──► tata-predictive-maintenance-agent                │  │
│  │            │    Interprets RUL + recommends action               │  │
│  │            │                                                     │  │
│  │            ├──► tata-incident-rca-agent                          │  │
│  │            │    RAG retrieval over past similar PdM events       │  │
│  │            │                                                     │  │
│  │            ├──► [maintenance-planner via tool call]              │  │
│  │            │    Schedules window, parts, technician              │  │
│  │            │                                                     │  │
│  │            └──► [parts-ordering via tool call]                   │  │
│  │                 Inventory check + order if needed                │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────┬──────────────────────────────────────────────────────┘
                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│  STREAMLIT DEMO UI — agent traces visible                                │
│  • Live sensor stream simulator                                          │
│  • RUL prediction with confidence band                                   │
│  • Agentic action plan (visible decision tree)                          │
└────────────────────────────────────────────────────────────────────────┘
```

### Component list

| Component | Responsibility | Tech |
|---|---|---|
| `feature-pipeline` | Time-series featurisation | tsfresh + custom rolling stats |
| `pdm-model` | RUL + anomaly prediction | LightGBM multi-output + quantile regression |
| `orchestrator` | Routes to specialists | jarvis_core `/chat` |
| `pdm-specialist` | Action recommendation | tata-predictive-maintenance-agent |
| `rca-agent` | Past-incident retrieval | tata-incident-rca-agent + ChromaDB |
| `tool: scheduler` | Maintenance window scheduling | Mock tool for demo |
| `tool: parts-order` | Inventory check + order | Mock tool for demo |
| `demo-ui` | Streamlit | Plotly for time-series + agent trace |

### Data flow

1. Sensor window arrives → feature pipeline → LightGBM
2. Model output {RUL, anomaly, risk} → orchestrator
3. Orchestrator dispatches PdM specialist + RCA in parallel
4. PdM specialist proposes action, RCA retrieves similar past events
5. Synthesised plan → maintenance scheduler + parts-order tools (if approved)
6. Action confirmed → Streamlit shows execution trace

### Failure modes + mitigations

| Failure | Mitigation |
|---|---|
| Sensor stream drops (missing data) | Fwd-fill with mask flag; model trained with random dropout |
| Concept drift (electrode supplier change) | Online drift detection on residuals; retrigger fine-tune |
| RUL prediction false alarm | Quantile bands → only alarm if p10 RUL < 4 hours |
| Parts-ordering tool error | Tier-3 confirm — orchestrator never auto-orders, always queues approval |
| Heat-cycle confound | Include heat-cycle phase as categorical feature |

### Deployment topology

- **Demo:** Streamlit with synthetic sensor stream simulator
- **Production target:** Edge inference on plant servers (low-latency required), aggregated to BigQuery for retraining, Cloud Run for orchestrator API — matches Tata Steel stack

---

## 2. Stack Selection — every choice with alternatives

### 2.1 ML model

| Option | Pros | Cons | Decision |
|---|---|---|---|
| **LightGBM multi-output + quantile regression** ⭐ | Fast train/inference, handles missing data, quantile bands for uncertainty | Cant capture deep sequence patterns | **Selected** — wins on tabular industrial PdM benchmarks |
| XGBoost | Slightly higher accuracy | Slower training | Backup if LightGBM hits memory wall |
| CatBoost | Good with categorical features | Less common, fewer ablation tricks | Reject — community is smaller |
| LSTM / Transformer (time-series) | Captures sequence | Needs much more data; overfits on hackathon scale | Reject — feasibility risk |
| Survival analysis (DeepHit, RSF) | Native RUL framing | Complex; harder to demo | Use as Round 2 enhancement only |

**Cost implications:**
- Train: 5-15 min on Kaggle GPU (free)
- Inference: <100ms per window on CPU

### 2.2 Feature engineering

| Option | Pros | Cons | Decision |
|---|---|---|---|
| **tsfresh + custom features** ⭐ | Battle-tested, comprehensive | Need to prune for speed | **Selected** — selectable feature set |
| Featuretools | Auto-feature-engineering | Black box | Reject — Round 1 judges value explainability |
| Manual only | Most interpretable | Time-consuming | Use as supplement to tsfresh |
| TSFEL | Lightweight alternative | Less feature coverage | Reject |

### 2.3 Uncertainty quantification

| Option | Pros | Cons | Decision |
|---|---|---|---|
| **Quantile regression (LightGBM native)** ⭐ | Built-in, no extra training | Doesn't give true posterior | **Selected** — pragmatic for hackathon |
| Bayesian NN | True posterior | Heavy compute | Reject — overkill |
| Conformal prediction | Distribution-free guarantee | Extra calibration set needed | Add in Round 2 polish |
| Ensemble variance | Standard practice | Doubles compute | Backup |

### 2.4 Hyperparameter tuning

| **Optuna + TPE + Hyperband pruning** ⭐ | Industry standard | — | **Selected** |

### 2.5 RAG for past-incident retrieval

| Option | Pros | Cons | Decision |
|---|---|---|---|
| **ChromaDB + sentence-transformers + BM25 hybrid** ⭐ | Already in jarvis_core; hybrid handles both semantic + keyword | — | **Selected** |
| Pinecone | Production-ready | Adds vendor + cost | Reject for demo |

### 2.6 Demo UI

| **Streamlit + Plotly time-series** ⭐ | Fast, Python-native, easy agent trace visualisation | — | **Selected** |

---

## 3. Data Strategy

### 3.1 Training data sources

| Source | Type | Use |
|---|---|---|
| **PHM 2010 Milling dataset** | Real, tool-wear time-series, 6 sensors | Transferable methodology — bearing/wear analog |
| **NASA C-MAPSS turbofan** | Real, RUL with multiple failure modes | RUL ML pattern reference |
| **Case Western Reserve Bearing** | Real, vibration ML benchmark | Frequency-domain feature reference |
| **IMS Bearing dataset** | Real, life-to-failure | Survival analysis reference |
| **Tata Steel Round 1 dataset (locked)** | Will be provided | Fine-tune model on this |
| **Synthetic EAF simulator** | Build via published physics | Demo + edge-case eval |

### 3.2 Synthetic data for demo

EAF physics simulator built in Python:
- Electrode consumption rate = f(power_input, scrap_quality_factor, electrode_age, arc_stability_var)
- Transformer thermal model = f(load_kVA, ambient_temp, cooling_water_temp)
- Realistic noise: AR(1) process for current spikes, Gaussian for thermal
- 50 simulated runs with embedded failure modes for demo eval

Label all synthetic data `[synthetic — for demo, real Tata data is proprietary]`.

### 3.3 Data augmentation

- Time-warp / scale jitter (simulates sensor drift)
- Random masking (sensor dropouts)
- Mixup on adjacent windows
- SMOTE-NC for anomaly class imbalance

### 3.4 Realism for judges

- Use industry-standard sensor names: "IRMS current", "harmonic distortion THDi", "secondary voltage Vsec"
- Match real EAF heat-cycle phase nomenclature: "bore-down", "melt", "refining", "tap"
- Cite published Tata Steel papers on Jamshedpur EAF for context

---

## 4. AI/ML Strategy

### 4.1 Round 1 model approach

```
Day 1: Baseline LightGBM single-output, default params, public dataset → submit
Day 2: Multi-output (RUL + anomaly), tsfresh features, CV setup matched to metric
Day 3: Domain-informed features (FFT bands, heat-cycle interactions)
Day 4: Hyperparameter tuning (Optuna, 50 trials)
Day 5: Pseudo-labeling (if competition allows)
Day 6: Ensemble (LightGBM + XGBoost + CatBoost) with weighted blend
Day 7-8: Final tuning, code cleanup, reproducibility
Day 9: Submit
```

**Expected leaderboard position:** Top 15-25% (PdM benchmarks favor LightGBM ensembles; Boss can hit this).

### 4.2 Round 2 agentic strategy

**Eval scenarios:**
1. Slow drift on electrode → 8h-ahead RUL warning → orchestrator schedules planned shutdown
2. Sudden transformer anomaly → urgent alert → bypasses normal scheduling
3. Multiple equipment near-EOL → prioritisation across maintenance windows
4. False alarm (high model confidence but no real failure) → RCA agent flags pattern
5. ... 11 more scenarios

**Wow factors:**
- Live RUL gauge with shaded uncertainty band
- Multi-step agent reasoning trace: "PdM specialist sees electrode RUL p10 = 3.2h → checks heat-cycle phase = refining → routes to maintenance-planner with priority HIGH → orders new electrode set..."
- Cost-aware: every action carries explicit $ impact
- Tier-3 confirm on parts-order (matches Boss's auto-mode framework — interview talking point)

### 4.3 Evaluation method

- **Round 1**: matches official metric (likely RMSE, MAE, or F1). CV: 5-fold time-aware (no future leakage).
- **Round 2**: 15 scenarios × per-scenario rubric (correct action? confidence calibrated? latency <12s?)

### 4.4 Composite re-score

| Dimension | Phase 2 | Phase 3 reassessed |
|---|---:|---:|
| Innovation | 7 | 7 |
| Judge Appeal | 9 | 9 |
| Feasibility | 8 | **9** (LightGBM pipeline is bread-and-butter for Boss) |
| Technical Depth | 8 | 8 |
| Business Potential | 9 | 9 |
| **Composite** | 8.20 | **8.35** |

---

## 5. Latency + cost budget

| Operation | Latency | Cost (USD) |
|---|---|---|
| Feature pipeline (60s window) | ~10ms | $0 |
| LightGBM inference | ~5ms | $0 |
| Tata-PdM agent reasoning | ~3s (Haiku) | ~$0.001 |
| RCA agent + RAG (k=5) | ~2s | ~$0.001 |
| Full orchestrator pass | ~6-8s | ~$0.003 |
| 15-scenario demo run | ~2 min total | ~$0.05 |

**Round 1 training:** Free (Kaggle 30 GPU-hrs/week)

---

## 6. Top risks

1. **Round 1 dataset may be image-based, not time-series** — fallback: image surface defect on EAF panels, redirect to surface-defect approach
2. **PHM datasets vs EAF reality** — domain gap; bridge via synthetic EAF simulator
3. **Multi-output model may underperform single-output ensemble** — eval both, pick winner
4. **Tier-3 confirm flow in demo** — must be smooth (visible UI element, not buried)
5. **Synthetic sensor data quality** — judges from Tata Steel will spot bad simulator; iterate before demo
