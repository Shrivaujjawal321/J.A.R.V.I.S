# Component 09: Sensor Time-Series Anomaly Detection
**Tata Steel Maintenance Wizard — Round 2 Research**
*Researched: 2026-06-06 | Powers: FR5 (abnormality detection + failure prediction) + FR7 (real-time alerting)*

---

## 1. Recommended Approach: Layered Hybrid Detector (Isolation Forest + LSTM Autoencoder + Adaptive Threshold)

**Single winner: A two-layer unsupervised detector stack — Isolation Forest for fast point/contextual screening + LSTM Autoencoder for temporal pattern anomalies — unified by a percentile-based adaptive threshold, SHAP-based explainability, and a lightweight engineer feedback loop for contamination recalibration.**

This is not a new research direction — it is the battle-tested 2025 production pattern backed by both academic benchmarks and real industrial deployments.

### Architecture in One Paragraph

Raw sensor windows (e.g., sliding 30-step windows over NASA C-MAPSS / AI4I-style features) enter two parallel heads:

- **Head A — Isolation Forest** (sklearn 1.5+): Detects point anomalies and multivariate outliers in the feature space. Instant inference (<1 ms/sample). No temporal modeling. High precision, noisy recall.
- **Head B — LSTM Autoencoder** (PyTorch 2.3 / Keras 3.x): Trained on "healthy" windows only. Reconstruction error = anomaly score. Captures temporal dependencies, degradation ramps, sequential patterns. CPU-viable at inference (~5–20 ms/window).

Both scores are L2-normalized, then combined with a tunable weight (α×IF_score + (1–α)×AE_score). A **percentile-based adaptive threshold** (e.g., 97th percentile of training-set combined scores) fires the alert. SHAP TreeExplainer (for IF) and per-sensor reconstruction error heatmaps (for AE) together produce the explainability output required by FR4.

An **engineer feedback panel** stores false-positive / true-positive labels in SQLite. A weekly recalibration job reruns threshold fitting and adjusts the IF contamination parameter — fulfilling FR6 (feedback-driven improvement loop).

---

## 2. WHY — Evidence-Based Reasoning

### Benchmark Grounding

**TSB-AD (NeurIPS 2024)** is the gold-standard evaluation, covering 1,070 time series across 40 datasets and 40 algorithms. Its primary metric, VUS-PR (Volume Under Surface Precision-Recall, 2025 — arxiv 2502.13318), replaces the discredited point-adjusted F1. Key finding: *"simpler architectures and statistical methods often yield better performance than advanced neural networks"* on the benchmark leaderboard. This is the single most important result to internalize — over-engineering the detector will not beat a well-tuned hybrid on real industrial data.

**MMPAD (Matrix Profile-based)** ranked first on TSB-AD univariate (VUS-PR 0.4399) and first multivariate (VUS-PR 0.3539) per the 2026 MMPAD paper (arxiv 2604.02445). This is impressive but only marginally better than simpler baselines, and requires STUMPY which adds complexity for a solo 9-day build.

**Hybrid AE + IF**: 2025 benchmark on CIC IoT-DIAD 2024 reports accuracy 0.98, improving to 0.99 with whitening. Deployed hybrid (AE + IF) in industrial IoT contexts reduces false positives by 76% vs. threshold-only systems (etasr.com, 2025). These are directly portable to steel-plant sensor monitoring.

**LSTM Autoencoder on C-MAPSS**: A 2025 paper (arxiv 2601.10269) demonstrates unsupervised LSTM-AE on NASA C-MAPSS with regression-based normalization across operating conditions, achieving high recall / low false-alarm rate with an adaptive data-driven threshold — exactly the dataset this system will use. No run-to-failure labels needed.

**Transformer-Enhanced IF for blast furnace** (ScienceDirect 2025, doi 10.1016/j.engappai.2025): A dynamic anomaly detection framework combining transformer features with Isolation Forest applied directly to blast furnace sensor streams. Confirms the stack is steel-plant valid.

**Isolation Forest on AI4I 2020**: Multiple GitHub projects + Kaggle notebooks confirm IF + RF pipelines on AI4I achieve 84–89% accuracy unsupervised, 96.5% F1 with deep learning extensions.

### Why NOT Pure Transformer (TranAD, PatchTST)

TranAD (VLDB'22) is an excellent research model: 127K parameters, inference ~20–75 ms CPU per step (Striim blog, 2024), F1 gains up to 17% over baselines on SMAP/SMD. However:
- Requires dataset-specific pretraining (6 datasets in paper: SMAP, MSL, SWaT, WADI, SMD, MSDS).
- TSB-AD 2024 finding shows transformer-based methods do NOT universally dominate — simpler methods often win.
- Solo 9-day build: training TranAD on a custom C-MAPSS derived dataset, debugging attention masks, and packaging it for a judge's `pip install` adds 2–3 days of risk for marginal gain.
- PatchTST is a forecasting model primarily; its anomaly detection variant is not independently benchmarked in TSB-AD 2024 for multivariate industrial data.

### Why NOT Pure Matrix Profile (STUMPY)

STUMPY 1.14.1 (PyPI 2024) is mathematically elegant and the TSB-AD univariate winner. Problems for this build:
- MMPAD's advantage requires "multidimensional aggregation, efficient k-NN retrieval, and moving-average post-processing" beyond vanilla STUMPY (arxiv 2604.02445) — significant implementation overhead.
- Transductive: must see all data to compute the profile. Streaming requires incremental `stumpy.stumpi` which is less stable.
- No built-in SHAP explainability — explainability is a judging criterion.
- Good as an offline secondary tool; poor as the primary real-time detector.

### Why NOT River (HalfSpaceTrees only)

River 0.21+ `HalfSpaceTrees` achieves ROCAUC 0.781 in IoT streaming benchmarks (ResearchGate 2024). Excellent for concept drift adaptation. However:
- Designed for truly streaming one-sample-at-a-time scenarios, not batch re-scoring.
- No native SHAP explainability.
- Weaker on the C-MAPSS type multivariate temporal dependency patterns.
- Best used as a *complement* (real-time streaming head) not primary detector.

**Recommended role for River**: Add `river.anomaly.HalfSpaceTrees` as a third lightweight streaming head for the real-time alerting path (FR7). Its online update (`learn_one`) adapts to sensor drift without retraining.

---

## 3. Exact Stack

| Library | Version | Role |
|---|---|---|
| `scikit-learn` | 1.5.x | `IsolationForest` — fast point anomaly head; `StandardScaler`, `MinMaxScaler` for normalization |
| `torch` (CPU build) | 2.3.x | LSTM Autoencoder training + inference; `torch.no_grad()` for inference mode |
| `numpy` | 1.26.x | Sliding window feature extraction; score fusion |
| `pandas` | 2.2.x | Time-indexed sensor data ingestion, resampling, forward-fill on missing values |
| `shap` | 0.45.x | `TreeExplainer` for Isolation Forest → feature importance per alert; SHAP waterfall plots |
| `river` | 0.21.x | `HalfSpaceTrees` streaming head for real-time path; `ADWIN` concept drift detector |
| `stumpy` | 1.14.1 | Optional: offline matrix profile computation for historical discord analysis in the report generator |
| `pyod` | 2.0.3 | ADEngine orchestration for quick baseline comparison; `LSTMAD`, `MatrixProfile`, `SpectralResidual` all accessible via unified API |
| `matplotlib` / `plotly` | latest | Anomaly overlay plots, reconstruction error timelines for UI |
| `sqlite3` (stdlib) | — | Feedback store: engineer labels, false positive log, recalibration history |
| `scipy` | 1.13.x | `percentileofscore` for adaptive threshold; signal smoothing |

**Install command for judge's machine:**
```bash
pip install scikit-learn torch numpy pandas shap river stumpy pyod matplotlib plotly scipy
```
No docker, no GPU, no CUDA required. All CPU-native.

---

## 4. Alternatives Considered and Why They Lost

### Alternative A: TranAD (Transformer, VLDB'22)
**What it is**: 127K-param transformer with adversarial training + focus-score self-conditioning. VLDB'22, GitHub: imperial-qore/TranAD.
**Why it loses**: TSB-AD 2024 shows transformer methods do not universally outperform simpler approaches. Training on custom C-MAPSS subset is a 2–3 day debugging risk for a solo build. CPU inference 20–75 ms is fine, but pretraining overhead and lack of plug-and-play explainability make it a poor fit for 9 days. **Use it in future work if the model wins.**

### Alternative B: Pure Matrix Profile / STUMPY
**What it is**: O(n²) nearest-neighbor in z-normalized Euclidean distance space. Best on TSB-AD univariate (VUS-PR 0.44 for MMPAD variant).
**Why it loses**: To match MMPAD performance requires multidimensional aggregation beyond vanilla STUMPY (arxiv 2604.02445). Transductive nature means no true online streaming. No SHAP explainability built-in. Explainability is a judging criterion — this would require bespoke annotation. Good secondary tool for offline batch analysis.

### Alternative C: River HalfSpaceTrees only
**What it is**: Online variant of Isolation Forest; one-sample-at-a-time update. ROCAUC 0.781 on IoT streams.
**Why it loses**: Works per-sample without temporal window context. Misses the reconstruction-error signal from autoencoders that captures gradual degradation ramps (essential for RUL + early warning). But it *wins* as a third streaming head because it adapts to sensor drift without retraining — included in the recommended stack as a parallel real-time path.

### Alternative D: USAD / OmniAnomaly (VAE-based)
**What it is**: USAD (Under-Sampling Anomaly Detection) and OmniAnomaly (stochastic RNN + VAE). Solid multivariate detectors in TSB-AD-M.
**Why it loses**: More complex architecture, harder to install (some require older TF or custom CUDA ops), and explainability is harder (latent space not directly interpretable). TSB-AD shows LSTMAD and CNN often beat them on multivariate industrial data. Not worth solo 9-day build risk.

---

## 5. Anti-Patterns — What Screams "Amateur / 2022-tier"

1. **Hard-coded threshold (e.g., `score > 0.7`)**: No adaptive mechanism. Will break on new equipment or operating regime. Judging criteria explicitly covers "doesn't break."
2. **Using point-adjusted F1 as your evaluation metric**: The research community (TSB-AD NeurIPS 2024) has established this metric inflates scores by crediting detectors for entire anomaly windows when only one point is detected. Use VUS-PR or range-based precision/recall.
3. **Training autoencoder on the full dataset including anomalies**: Autoencoders must be trained on "healthy/normal" windows only. Training on contaminated data destroys the reconstruction error signal.
4. **Single-sensor isolation**: Processing each sensor independently and threshold-alerting per sensor → explosion of false positives from correlated sensors. Multivariate joint modeling is non-negotiable.
5. **No explainability**: Outputting "anomaly detected" with no attribution to which sensor/feature caused it. The hackathon explicitly requires "explainable + traceable outputs." SHAP feature importance is the minimum.
6. **Static contamination parameter in Isolation Forest**: Setting `contamination=0.05` and never touching it. Industrial data drifts. No feedback loop = 2022-tier.
7. **Dense autoencoder on raw long sequences**: Using a plain MLP autoencoder (no LSTM/GRU) on raw 500-step sequences. Loses all temporal structure. 2019-tier.
8. **sklearn IsolationForest on raw sensor readings without feature engineering**: IF works on feature vectors, not raw time series. You must extract sliding-window features (mean, std, max, min, rate-of-change, FFT peaks) first.

---

## 6. Integration Notes

### Inputs Consumed
- **Sensor data summaries** (FR input): multivariate time series from C-MAPSS (21 sensors: T24, T30, T50, P30, Nf, Nc, etc.) or AI4I 2020 (air temp, process temp, rotational speed, torque, tool wear). Arrives as pandas DataFrame with timestamps.
- **Anomaly alerts feed**: real-time sensor readings from Component 08 (sensor preprocessing/ingestion layer) via an internal queue or shared DataFrame.
- **Historical maintenance records**: used to label "known fault windows" for evaluating recall (not for training — unsupervised).

### Outputs Produced
- **Anomaly score**: float 0–1 per window per equipment unit. Stored in SQLite `anomaly_scores` table.
- **Alert object**: `{equipment_id, timestamp, score, severity: low|medium|high|critical, triggered_sensors: [sensor_id], shap_values: {sensor: contribution}}` — passed to Component 10 (risk classifier) and Component 12 (report generator).
- **Reconstruction error heatmap**: per-sensor contribution to the LSTM-AE total reconstruction error — rendered as a chart in the UI.
- **Streaming alert**: River HST fires a JSON event on the real-time websocket (FR7) with `{equipment_id, ts, streaming_score, threshold}`.

### Components This Talks To
- **Component 04 (RAG / Knowledge Integration)**: When an alert fires, the alert payload triggers a RAG query for relevant maintenance SOPs and equipment manual sections — the anomaly detector is the trigger, not the responder.
- **Component 06 (Explainability layer)**: SHAP values and per-sensor reconstruction errors are consumed by the explainability component to generate human-readable "why flagged" text via LLM.
- **Component 10 (Risk Classifier)**: Receives anomaly score + severity enum. Risk classifier combines this with spares availability and process criticality to produce urgency tier.
- **Component 11 (RUL predictor)**: Anomaly onset timestamp feeds into RUL model as "degradation start" reference point.
- **Feedback Store**: Engineer false-positive/true-positive labels (captured via UI) write to SQLite → weekly recalibration job reruns adaptive threshold and contamination tuning.

### Data Flow Pseudocode
```
sensor_df → preprocess (normalize, sliding window 30 steps, extract features)
           → [IF head, LSTM-AE head, River HST head] (parallel)
           → score fusion (weighted sum + adaptive threshold)
           → if score > threshold: emit alert(equipment_id, ts, score, shap_values)
           → alert → RAG trigger + Risk Classifier + RUL updater
           → engineer label (UI) → feedback_store → weekly recalibration
```

---

## 7. Risks and Unknowns

| Risk | Severity | Mitigation |
|---|---|---|
| **C-MAPSS has no explicit "anomaly" labels** — it has RUL labels | Medium | Derive anomaly labels: last 30 cycles before failure = anomaly window. This is standard practice (arxiv 2601.10269). |
| **LSTM-AE training time on CPU** — a 2-layer LSTM-AE on C-MAPSS FD001 (~20K samples) takes ~5–10 min on CPU | Low | Pre-train once, pickle the model. Inference is fast (~5–20 ms/window). |
| **Adaptive threshold drift on demo day** | Low | Freeze threshold at demo time. Recalibration is shown as a UI feature, not run live. |
| **SHAP TreeExplainer slow for IF on high-dimensional features** [unverified exact timing] | Medium | Use `shap.TreeExplainer(model).shap_values(X[:100])` only on flagged windows, not batch. Cache SHAP per anomaly. |
| **River HalfSpaceTrees on multivariate data with many sensors** — paper notes "does not work well if anomalies are packed together in windows" | Low | HST is the streaming head only, IF+AE are primary. HST false positives filtered by IF score. |
| **Contamination parameter tuning without ground-truth labels** | Medium | Use 2% as starting contamination (matches ~2% failure rate in AI4I 2020). Expose as UI slider for engineer. |
| **AI4I 2020 class imbalance** (only ~3.4% failures) | Low | Use `class_weight='balanced'` for any supervised head; for unsupervised heads, imbalance is a feature not a bug — anomalies ARE rare. |
| **MMPAD beats the recommended stack on VUS-PR** [benchmark confirmed] | Low | MMPAD's advantage is 0.03 VUS-PR on multivariate vs CNN second-place. Within noise range. MMPAD complexity not worth solo-build risk. |
| **Concept drift from operating regime changes in C-MAPSS FD002/FD004** (multi-condition) | Medium | River ADWIN drift detector flags regime change → triggers LSTM-AE re-threshold. Isolation Forest retrained on new baseline window. |

---

## Sources

- [TSB-AD NeurIPS 2024 Benchmark](https://thedatumorg.github.io/TSB-AD/) — primary ground truth for method ranking
- [TranAD arxiv paper](https://arxiv.org/abs/2201.07284) — VLDB'22 transformer anomaly detection
- [TranAD GitHub](https://github.com/imperial-qore/TranAD) — imperial-qore/TranAD
- [MMPAD: Matrix Profile for Anomaly Detection (arxiv 2604.02445)](https://arxiv.org/html/2604.02445) — TSB-AD top performer
- [STUMPY 1.14.1 docs](https://stumpy.readthedocs.io/en/latest/Tutorial_The_Matrix_Profile.html) — matrix profile Python library
- [PyOD 2.0.3 time series](https://github.com/yzhao062/pyod) — ADEngine with TSB-AD routing
- [VUS-PR metric paper (arxiv 2502.13318)](https://arxiv.org/abs/2502.13318) — recommended evaluation metric
- [River HalfSpaceTrees docs](https://riverml.xyz/dev/api/anomaly/HalfSpaceTrees/) — streaming anomaly detection
- [LSTM-AE on C-MAPSS (arxiv 2601.10269)](https://arxiv.org/abs/2601.10269) — early fault detection without labels
- [Hybrid AE+IF IoT benchmark (etasr.com)](https://etasr.com/index.php/ETASR/article/view/15288) — 98% accuracy, 76% FP reduction
- [Transformer-Enhanced IF for blast furnace (ScienceDirect 2025)](https://www.sciencedirect.com/science/article/abs/pii/S0952197625017269) — steel-plant validation
- [Adversarial Autoencoder blast furnace pressure (PMC 2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12158386/) — steel-plant anomaly detection
- [ShaTS Shapley for time series (arxiv 2506.01450)](https://arxiv.org/html/2506.01450) — SHAP explainability for time-series anomaly detection
- [AI4I 2020 Dataset (UCI)](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset) — benchmark dataset
- [Argos: Agentic Anomaly Detection (arxiv 2501.14170)](https://arxiv.org/abs/2501.14170) — Microsoft, LLM-driven rule generation (future extension)
- [HILAD: Human-in-the-Loop Anomaly Detection (arxiv 2405.03234)](https://arxiv.org/abs/2405.03234) — feedback loop design
- [TimeSeriesBench industrial benchmark](https://arxiv.org/abs/2402.10802) — industrial-grade evaluation framework
