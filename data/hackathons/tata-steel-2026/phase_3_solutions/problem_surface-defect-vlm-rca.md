# Solution Research — `surface-defect-vlm-rca`

**Composite:** 8.25 · **Compiled:** 2026-05-14 (Daemon synthesis)
**Problem:** Multi-class steel surface defect classification + VLM root-cause hypothesis layer + agentic upstream routing.

---

## 1. Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│  PLANT INSPECTION CAMERA / DATASET UPLOAD                             │
└────────────────┬─────────────────────────────────────────────────────┘
                 │ JPEG / PNG image (200×200 to 1024×1024)
                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│  ROUND 1 ML CORE — Defect Classifier                                  │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ EfficientNet-B4 backbone (ImageNet-pretrained)                 │  │
│  │   ↓ Conv layers (frozen for first 5 epochs, then fine-tuned)   │  │
│  │   ↓ Class-balanced focal loss (γ=2, α per class freq)          │  │
│  │ → 7-class softmax: {scale, patches, crazing, pitted,           │  │
│  │   inclusion, scratch, sliver}                                  │  │
│  │ → Confidence vector + Grad-CAM heatmap                         │  │
│  └────────────────────────────────────────────────────────────────┘  │
└────────────────┬─────────────────────────────────────────────────────┘
                 │ {label, confidence, heatmap_png, raw_image}
                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│  ROUND 2 AGENTIC LAYER — jarvis_core orchestrator                     │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  tata-operations-orchestrator-agent (router)                   │  │
│  │            │                                                   │  │
│  │            ├──► tata-defect-detector-agent                     │  │
│  │            │    Classifies + recommends inspection workflow    │  │
│  │            │                                                   │  │
│  │            ├──► [VLM root-cause via Gemini Vision]             │  │
│  │            │    Input: {image, defect_label, heatmap, history} │  │
│  │            │    Output: ranked root-cause hypotheses + evidence│  │
│  │            │                                                   │  │
│  │            ├──► tata-process-optimizer-agent                   │  │
│  │            │    If RCA points upstream → suggest setpoint adj  │  │
│  │            │                                                   │  │
│  │            └──► tata-incident-rca-agent                        │  │
│  │                 RAG over plant history for similar past cases  │  │
│  └────────────────────────────────────────────────────────────────┘  │
└────────────────┬─────────────────────────────────────────────────────┘
                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STREAMLIT DEMO UI — visible agent thinking traces                    │
│  • Image upload + classifier verdict + heatmap overlay                │
│  • Live reasoning trace: orchestrator → 4 specialists                 │
│  • Citation panel with retrieved evidence                             │
│  • Suggested next action (operator-actionable)                        │
└──────────────────────────────────────────────────────────────────────┘
```

### Component list

| Component | Responsibility | Tech |
|---|---|---|
| `classifier` | Round 1 leaderboard model | PyTorch + EfficientNet-B4 + Optuna |
| `orchestrator` | Route to specialists, synthesise | jarvis_core daemon `/chat` |
| `vlm-rca` | Root-cause hypothesis from image | Google Gemini Vision API |
| `process-optimizer` | Map RCA → setpoint suggestion | tata-process-optimizer-agent |
| `rag-history` | Retrieve similar past defects | ChromaDB + sentence-transformers |
| `demo-ui` | Visible agentic trace | Streamlit |

### Data flow

1. Image → classifier → label + confidence + heatmap
2. {label, image, heatmap} → orchestrator → routes to defect-detector + VLM-RCA in parallel
3. VLM-RCA output → orchestrator → maps to process-optimizer (if upstream cause) OR RAG-history (if similar incidents)
4. All evidence → synthesised reasoning trace → Streamlit UI

### Failure modes + mitigations

| Failure | Mitigation |
|---|---|
| Classifier confidence low (<0.5) | Trigger VLM-only mode + flag to human inspector |
| Gemini Vision API rate-limit / latency | Cache by image hash; pre-warm with sample images |
| RAG corpus empty for new defect class | Fall back to general metallurgy literature |
| Heatmap misleads RCA | Multiple Grad-CAM passes (smooth + sharp); ensemble Grad-CAM++ |
| Production camera not industrial-grade | Synthetic augmentation (Gaussian noise + perspective shifts) |

### Deployment topology

- **Demo:** Streamlit on Vercel/Streamlit Cloud
- **Production target (post-hackathon):** Cloud Run for classifier API, BigQuery for inference logs, Pub/Sub for plant camera ingest — matches Tata Steel's GCP stack

---

## 2. Stack Selection — every choice with alternatives

### 2.1 Classifier backbone

| Option | Pros | Cons | Decision |
|---|---|---|---|
| **EfficientNet-B4** ⭐ | Strong accuracy/param ratio; NEU benchmarks well documented; transfers from ImageNet | Slower than ResNet50 on CPU | **Selected** — best balance for Round 1 (Sonnet eval) |
| ResNet50 | Industry baseline, fast inference | Older architecture, lower accuracy ceiling | Reject — accuracy ceiling matters more than speed |
| YOLOv8-cls | Easy to swap to detection mode | Optimised for detection not classification; underperforms on small NEU | Reject for classification; reconsider if Round 1 dataset is detection |
| Vision Transformer (ViT-B/16) | Highest accuracy ceiling on large data | Needs 10K+ samples to beat CNN; NEU is small | Reject — data efficiency loses |
| **Fallback:** EfficientNet-B7 + DINOv2 features (few-shot) | Robust to small data | Higher compute | Selected for ensemble in Round 1 day 6 |

**Cost implications:**
- Demo scale (1 inference / sec): ~$0 (single Colab GPU)
- 10K-user scale: GPU autoscaling on Cloud Run, ~$200-500/mo

### 2.2 Loss function

| Option | Pros | Cons | Decision |
|---|---|---|---|
| **Class-balanced focal loss (γ=2)** ⭐ | Handles severe class imbalance in defect data | Hyperparameter tuning needed | **Selected** — NEU + Severstal both have heavy imbalance |
| Cross-entropy | Standard, fast | Poor on imbalance | Reject |
| Label smoothing CE | Calibration improvement | Doesn't address imbalance | Reject |

### 2.3 VLM for root-cause

| Option | Pros | Cons | Decision |
|---|---|---|---|
| **Gemini 2.5 Pro Vision** ⭐ | Tata Steel uses Gemini + PaliGemma → exact stack-fit; multimodal accurate | Costs ~$0.0015/image at scale | **Selected** — perfect alignment with Safety EyeQ |
| GPT-4o Vision | Comparable accuracy | Doesn't match Tata stack | Reject — narrative loses |
| Claude Sonnet Vision | Boss's strongest API familiarity | Slower; doesn't match Tata stack | Reject for demo polish, use as backup |
| Local LLaVA / Llama Vision | Free, offline | Inferior accuracy on industrial domain | Reject |

### 2.4 RAG / vector store

| Option | Pros | Cons | Decision |
|---|---|---|---|
| **ChromaDB + sentence-transformers** ⭐ | Already in jarvis_core; zero new infra | Single-machine only | **Selected** — leverage existing |
| pgvector (Neon Postgres) | Boss uses for McpIndex | Adds new dependency | Reject — chromaDB already integrated |
| Pinecone | Production-grade | Paid + adds latency | Reject — overkill for demo |

### 2.5 Demo UI

| Option | Pros | Cons | Decision |
|---|---|---|---|
| **Streamlit** ⭐ | Fast to ship, Python-native, agent traces easy to show | Limited customisation | **Selected** — speed > polish for hackathon |
| Gradio | Easier image input UX | Less flexible for agent traces | Reject — agent traces matter |
| Next.js / React | Maximum polish | Boss has 60h budget — not worth |  Reject |

### 2.6 Hyperparameter tuning

| Option | Decision |
|---|---|
| **Optuna with TPE sampler + ASHA pruner** ⭐ | **Selected** — standard for tabular/CV competition. 50-100 trials in 8 hrs on Kaggle GPU |
| Grid search | Reject — inefficient |
| Ray Tune | Reject — overkill |

---

## 3. Data Strategy

### 3.1 Training data sources

| Source | Type | Use |
|---|---|---|
| **NEU Surface Defect Database** ⭐ | Public, 1800 images, 6 classes | Pre-train + transfer baseline |
| **Severstal Steel Defect Detection (Kaggle)** | Public, 12568 images, 4 classes + masks | Augmentation source + bag-of-models |
| **GC-10-DET** | 10-class steel defect | Pre-train alternative |
| **Tata Steel Round 1 dataset (unknown until May 22)** | Will be provided | Fine-tune on this once unlocked |

### 3.2 Data augmentation pipeline

- Horizontal/vertical flip (rolled steel orientation invariant)
- Random rotation ±15°
- Brightness/contrast jitter (varying lighting on plant cameras)
- Cutout + MixUp + CutMix (improves generalisation)
- Defect-class-specific augmentation: extra perspective shifts for elongated defects (slivers, scratches)

### 3.3 Synthetic data for demo

- 5-10 synthetic images for non-NEU classes labelled `[synthetic — for demo only]`
- Plant operator scenarios with known root-causes (e.g., "scale from reheat furnace temp drift")

### 3.4 Realism techniques (Round 2 demo critical)

- Real plant photos from Boss's GitHub + Pexels industrial archives
- Synthetic logbook for RAG: 100 fake-but-realistic past incidents tagged with defect_label, root_cause, action_taken
- **Always label synthetic data explicitly** — judges spot fake data instantly

---

## 4. AI/ML Strategy

### 4.1 Round 1 model approach

**Pipeline:**
```
1. Baseline: pretrained EfficientNet-B4 + linear head (Day 1, ~15 min training)
2. Strong baseline: fine-tune all layers + focal loss + standard augmentation (Day 2-3)
3. Cross-validation: 5-fold stratified, matched to leaderboard metric
4. Ensemble: 3 backbones (EfficientNet-B4, B7, ResNeSt-50) + 5 seeds = 15 models
5. Test-time augmentation (TTA): flip + rotate + scale → average predictions
6. Pseudo-labeling on test set (if competition allows)
```

**Expected leaderboard position:** Top 20-30% (Boss's CV experience is mid; ensemble + TTA pushes up).

### 4.2 Round 2 agentic strategy

**Eval scenarios (15 designed):**
1. Clear single-class defect → classifier high-conf → defect-detector responds
2. Ambiguous defect (low classifier conf) → VLM-RCA takes over
3. Defect + sensor anomaly correlation → process-optimizer + defect-detector
4. Historical defect match → RAG returns past incident + resolution
5. ... (10 more covering edge cases)

**Wow-factor moments engineered:**
- Live multi-agent reasoning trace visible on UI as it happens
- Cite-as-you-go: every claim links to retrieved chunk or model output
- Latency budget: classifier <1s, VLM-RCA <5s, full orchestration <12s
- Confidence calibration visible (`verified` / `unverified` / `low` per claim)

### 4.3 Evaluation method

**Round 1 metrics (likely):** F1-macro (handles imbalance) OR AUC-ROC OR accuracy. We optimise for F1-macro by default; rebuild after May 22 if metric differs.

**Round 2 metrics (judging rubric):**
- Innovation: 8/10 (VLM-RCA novel on top of standard CV)
- Judge appeal: 9/10 (Gemini + PaliGemma matches Safety EyeQ exactly)
- Feasibility: 8/10 (Round 1 + Round 2 both clean, fits time budget)
- Technical depth: 8/10 (CV + VLM + agentic orchestration)
- Business potential: 8/10 ($3-12M/yr/mill savings)

---

## 5. Latency + cost budget

| Operation | Latency | Cost/call (USD) |
|---|---|---|
| Classifier inference | ~0.3s on CPU, ~0.05s on GPU | $0 (local) |
| Gemini Vision RCA | ~3-5s | ~$0.0015 |
| ChromaDB retrieval (k=5) | ~50ms | $0 |
| Full orchestrator pass | ~8-12s | ~$0.003 |
| 15-scenario demo run | ~3 min total | ~$0.05 |

**Round 1 training cost:** Free (Kaggle 30 GPU-hrs/week)
**Round 2 demo total:** <$5 for full eval suite

---

## 6. Composite re-score (post-research)

| Dimension | Phase 2 score | Phase 3 reassessed |
|---|---:|---:|
| Innovation | 8 | 8 (unchanged) |
| Judge Appeal | 9 | 9 (unchanged) |
| Feasibility | 8 | **9** (research confirms pipeline cleanly fits 60h) |
| Technical Depth | 8 | 8 (unchanged) |
| Business Potential | 8 | 8 (unchanged) |
| **Composite** | 8.25 | **8.40** |

Reasoning for feasibility bump: NEU pre-training cleanly transfers to whatever Tata's Round 1 dataset shape is (image-based). All 4 specialists already built in jarvis_core. Streamlit demo trivial.

---

## 7. Top risks (carried from Phase 2 + added)

1. **Round 1 dataset may not be image-based** — fallback: pivot to tabular CV-feature extraction, use NEU-pretrained CNN as feature embedder for tabular classifier. Coverage: medium.
2. **Gemini Vision API quota** — pre-register, batch test before May 22.
3. **Class imbalance worse than NEU** — focal loss + oversampling tuned per discovered dist.
4. **Synthetic demo data realism** — manual review of 100 demo images, label `[synthetic]` clearly.
5. **Judges' Safety EyeQ familiarity** — they'll want to see DIFFERENTIATION, not duplication. VLM-RCA is the diff; lean into it heavily in demo narrative.
