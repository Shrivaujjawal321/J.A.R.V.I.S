# Round 1 Pre-Launch — Kaggle Practice Plan

**Window:** 2026-05-15 → 2026-05-21 (7 days, ~28 hrs)
**Goal:** Upgrade ML muscle on 3 tracks mirroring the 3 shortlisted Tata problems, AND build a reusable ML harness that copy-pastes into Round 1 Day-0.
**Mode:** Structured (per Boss approval — Option A).
**Source-of-truth war room:** `../war_room.md`

---

## 1. Why this exists

22 May 18:00 IST ko Tata Round 1 ka problem unlock hoga. Hum nahi jaante kaunsa track aayega (image / time-series / tabular+NLP). Isliye:

- **3 Kaggle tracks** — har ek Tata Steel ke 3 shortlisted problems se directly mirror karta hai.
- **2 din per track** — Day 1 = EDA + baseline + leaderboard submit. Day 2 = feature eng + ensemble + reusable notebook template.
- **1 din (aaj) harness skeleton** — CV utils + Optuna + metric matchers — common across all 3.

**Output bar:** Top-50% on each Kaggle leaderboard + 3 reusable notebook templates + 1 ML harness folder. **Not "Kaggle gold."**

---

## 2. The 3-track mapping

| Track | Kaggle dataset (primary) | Fallback | Mirrors Tata problem | ML core to practice |
|---|---|---|---|---|
| **A — Image** | [Severstal Steel Defect Detection](https://www.kaggle.com/c/severstal-steel-defect-detection) | NEU Surface Defect Database | `surface-defect-vlm-rca` | EfficientNet-B4 + focal loss + ensemble |
| **B — Time-series** | [NASA C-MAPSS Turbofan Degradation](https://www.kaggle.com/datasets/behrad3d/nasa-cmaps) | Kaggle Pump Sensor Data | `eaf-electrode-pdm` | LightGBM multi-output + quantile regression |
| **C — Tabular + NLP** | [CFPB Consumer Complaints](https://www.kaggle.com/datasets/cfpb/us-consumer-finance-complaints) | Mercari Price Suggestion | `quality-escape-rca` | Stacked GBM + BERT embeddings + SHAP |

**Why these specifically:**
- **Severstal** = literal steel-defect images, multi-label segmentation/classification — exactly what Tata might drop.
- **C-MAPSS** = canonical PdM dataset, sensor drift + RUL prediction = perfect EAF electrode analog.
- **CFPB** = real consumer complaint text → category → mirrors quality escape RCA (complaint → defect class → upstream cause).

---

## 3. Day-by-day schedule

| Day | Date | Hours | Task | Deliverable |
|---:|---|---:|---|---|
| 0 | **15 May (aaj)** | 4 | Harness skeleton (Section 4) | `ml_harness/` folder populated |
| 1 | 16 May | 4 | Track A Day 1 — Severstal EDA + ResNet/EfficientNet baseline + first submit | Leaderboard score baseline |
| 2 | 17 May | 4 | Track A Day 2 — focal loss + augmentation + 5-fold ensemble + final submit | `image_template.ipynb` |
| 3 | 18 May | 4 | Track B Day 1 — C-MAPSS EDA + LightGBM RUL baseline | Leaderboard score baseline |
| 4 | 19 May | 4 | Track B Day 2 — lag/FFT features + quantile ensemble + final submit | `timeseries_template.ipynb` |
| 5 | 20 May | 4 | Track C Day 1 — CFPB EDA + TF-IDF + LightGBM baseline | Leaderboard score baseline |
| 6 | 21 May AM | 3 | Track C Day 2 — BERT embeddings + stacking + SHAP | `tabular_nlp_template.ipynb` |
| 7 | 21 May PM | 1 | **REST + Round 1 Day-0 dry-run** (mental walkthrough of "data drops at 18:00 — what's my first hour?") | Mental readiness |
| | **Total** | **28** | | |

---

## 4. ML Harness Skeleton (Today's deliverable)

Folder created: `round_1/ml_harness/`

```
ml_harness/
├── configs/
│   └── default.yaml          # seed, n_folds, n_trials, metric
├── utils/
│   ├── cv.py                 # StratifiedKFold + GroupKFold + TimeSeriesSplit
│   ├── metrics.py            # binary/multi-class/RMSE/Dice/F1/MAP@K matcher
│   ├── seed.py               # set_seed() across torch + numpy + lightgbm
│   ├── optuna_runner.py      # generic Optuna study wrapper
│   ├── ensemble.py           # weighted avg + rank-avg + stacking helper
│   └── submission.py         # writes submission.csv + validates schema
├── notebooks/
│   ├── _harness_smoke_test.ipynb  # validates utils run
│   ├── image_template.ipynb       # filled on Day 2
│   ├── timeseries_template.ipynb  # filled on Day 4
│   └── tabular_nlp_template.ipynb # filled on Day 6
└── outputs/
    └── .gitkeep
```

**Today's harness scope:**
1. `cv.py` — three split strategies (Stratified for image/tabular, TimeSeriesSplit for TS, GroupKFold reserved).
2. `metrics.py` — auto-detect classification vs regression; return metric callable matching Kaggle/Tata format.
3. `seed.py` — one-call seed lock (`set_seed(42)`) for torch + numpy + random + lightgbm.
4. `optuna_runner.py` — accepts `objective(trial, X, y)` callable, returns best params + study.
5. `ensemble.py` — weighted average, rank average, simple stacking on OOF predictions.
6. `submission.py` — writes submission, validates row count + columns vs `sample_submission.csv`.
7. `_harness_smoke_test.ipynb` — synthetic XY dataset, runs CV + Optuna + ensemble + submission in <60 sec.

**Today, Boss spawns `ml-engineer-agent`** with the harness brief — agent writes the scaffolding. Boss reviews + smoke-tests.

---

## 5. Per-track playbooks

### Track A — Image (Severstal Steel Defect Detection)

**Day 1 (16 May, 4 hr):**
- Kaggle CLI download (`kaggle competitions download -c severstal-steel-defect-detection`)
- EDA: image dimensions, class distribution (4 defect classes + no-defect), mask area stats, image-quality outliers
- Baseline: ResNet50 (timm) or EfficientNet-B0, 5-fold stratified on `defect_class`, simple BCE, 5 epochs
- Submit, note public LB score, document gap to top

**Day 2 (17 May, 4 hr):**
- Upgrade to EfficientNet-B4 (more capacity)
- Focal loss (γ=2.0, α=0.25) — class imbalance
- Heavy augmentation: HorizontalFlip + Rotate + RandomBrightness + Cutout (via Albumentations)
- TTA: original + h-flip averaged at inference
- 5-fold ensemble → final submit
- Save `image_template.ipynb` with all of the above + clear "swap dataset path here" markers

**Reusable patterns harvested:**
- Albumentations augmentation pipeline (industrial vision standard)
- Focal loss implementation (class imbalance fix)
- TTA inference loop
- Submission format for image segmentation (RLE encoding)

### Track B — Time-series (C-MAPSS Turbofan)

**Day 1 (18 May, 4 hr):**
- Download from Kaggle (4 sub-datasets FD001-FD004; start with FD001 = single op condition)
- EDA: sensor distributions per unit, RUL distribution, sensor drift visualization
- Baseline: per-cycle row → engineered features (rolling mean, rolling std, last-value, slope) → LightGBM regressor → RUL prediction
- TimeSeriesSplit CV (not random — leak risk!)
- RMSE on hold-out, document

**Day 2 (19 May, 4 hr):**
- Lag features (lag 1, 5, 10, 20 cycles)
- FFT features on top-3 informative sensors (spectral energy in low/mid/high bands)
- Multi-output quantile regression (P10/P50/P90) — gives prediction intervals (matters for PdM)
- Stacked ensemble: LightGBM + CatBoost + simple LSTM (optional, time-permitting)
- Save `timeseries_template.ipynb`

**Reusable patterns:**
- Proper TS cross-validation (no shuffling)
- Lag + rolling feature engineering at scale
- Quantile regression → uncertainty quantification (rare in hackathons, judges notice)
- FFT-based feature extraction (vibration/electrode signals love this)

### Track C — Tabular + NLP (CFPB Complaints)

**Day 1 (20 May, 4 hr):**
- Kaggle CSV download — `Consumer_Complaints.csv` (~1M rows, ~18 columns)
- Target = `Issue` or `Product` (multi-class classification)
- EDA: class imbalance, text length distribution, missing values, top terms per class
- Baseline: TF-IDF (1-2 grams, top 50K features) + LightGBM multi-class → macro F1
- StratifiedKFold (5-fold), document baseline

**Day 2 (21 May AM, 3 hr):**
- Add `sentence-transformers` embeddings (`all-MiniLM-L6-v2`) → 384-dim per row
- Stacked GBM: TF-IDF predictions + BERT-embedding predictions → meta-learner (Logistic Regression)
- SHAP explanations on tabular features (where labels exist) → "why did model predict X?"
- Save `tabular_nlp_template.ipynb`

**Reusable patterns:**
- Text → embeddings → tabular features pipeline
- Stacking with meta-learner (powerful + safe)
- SHAP for explainability (judges love this in industrial AI)
- Imbalanced multi-class handling (weights, focal-like loss)

---

## 6. Definition of "done" per day

A day is **done** when:

1. ✅ Notebook runs end-to-end without errors (kernel restart + run-all passes)
2. ✅ At least 1 Kaggle leaderboard submission made (public score recorded)
3. ✅ A 1-paragraph note in `journal/YYYY-MM-DD.md`: what tried, what worked, what didn't, score gap to top
4. ✅ Reusable patterns extracted into `ml_harness/utils/` if generalisable
5. ✅ Template notebook updated (on Day 2 of each track)

**Anti-pattern to avoid:** "I'll just keep tuning Severstal till Day 4 because it's interesting." → No. Hard time-box. Move to next track on schedule.

---

## 7. Realistic expectations

| Track | Realistic LB position in 8 hrs | Why we're OK with this |
|---|---|---|
| Severstal | Top 40-60% | Comp had 2400+ teams, ours is a fast pass. Patterns > position. |
| C-MAPSS | Top 30-50% | Smaller dataset, fewer participants. Achievable. |
| CFPB | N/A (no live LB) | Hold-out F1 score is our metric. Target ≥0.65 macro F1. |

**Real win = the templates, not the leaderboard.**

---

## 8. Risks + mitigations

| Risk | Mitigation |
|---|---|
| Severstal download is huge (~6 GB) | Start download at end of Day 0 (today night) — kaggle CLI in background |
| C-MAPSS confused with FD002-FD004 variants | Stick to FD001 only — simpler, cleaner |
| BERT embedding generation is slow on CPU | Use `sentence-transformers` with `device='cuda'` if Kaggle GPU avail; else cap to 100K rows |
| Boss runs out of energy after 2 tracks | Built-in rest on Day 7 PM; can compress Track C to 1 long day if needed |
| Harness has bugs found mid-Track-A | Day 1 of Track A doubles as harness validation; fix on-the-fly before Track B |

---

## 9. Handoff to Tata Round 1 Day-0 (22 May 18:00 IST)

When Tata data drops, here's the **first hour** flow that this practice enables:

```
T+0:00  Download Tata data + sample_submission.csv
T+0:10  Identify track (image / TS / tabular-NLP)
T+0:15  Copy matching template notebook → rename
T+0:25  Swap dataset path + target column name
T+0:35  EDA cells run (5 min — already coded)
T+0:50  Baseline cell runs (CV + first model)
T+0:55  submission.py validates output
T+1:00  First Tata leaderboard submission
```

**Goal: First Tata submission within 1 hour of data unlock.** Without practice + harness, this would be 4-6 hrs.

---

## 10. Tracking + accountability

- Each day's work logged in `data/hackathons/tata-steel-2026/journal/YYYY-MM-DD.md`
- Auto-capture script ingests journal → vector memory → Jarvis remembers progress next session
- Tasks tracked in Jarvis TaskList (created 2026-05-15)
- Harness commits to local git (no push) — recover-friendly

---

**Boss's call to action — today, 15 May:**

1. Spawn `ml-engineer-agent` with this plan + harness scope (Section 4)
2. Kick off Severstal Kaggle data download in background (overnight pull)
3. EOD journal entry

**Tomorrow morning — start Track A.**
