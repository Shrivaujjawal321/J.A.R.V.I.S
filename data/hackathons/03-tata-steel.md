# Tata Steel AI Hackathon 2026 — Deep Research (HIGHEST PRIORITY)

**Deadline:** 2026-05-31 | **Mode:** Online (HackerEarth) | **Outcome:** Up to 20 FT job offers + ₹1L bonus per top-3

## Two Rounds
| Round | Window | Type |
|-------|--------|------|
| Round 1 — ML Challenge | May 22–31 | Tabular ML, leaderboard scoring |
| AI Leadership Connect | Jun 4 | Briefing |
| Round 2 — Agentic AI | Jun 5–15 | Build + present working agent |
| Final Interviews | Jun 22–26 | Direct hiring |

---

## Round 1: ML Challenge (Likely Domains)

Exact dataset not public until May 22. Inferred from Tata Steel's documented AI use cases:

| Domain | Probability | Likely Metric |
|--------|------------|--------------|
| **Steel Defect/Quality Classification** | HIGHEST | AUC-ROC (multi-label) or macro-F1 |
| **Predictive Maintenance / RUL** | HIGH | AUC or RMSE for RUL |
| **Energy Consumption Optimization** | MED-HIGH | RMSE |
| **Supply Chain / Demand Forecast** | MEDIUM | MAPE / RMSE |
| **Slab/Cast Quality Grading** | MEDIUM | Regression or ordinal |

### 10 Modeling Approaches (since dataset is fixed)
1. **LightGBM Baseline + DART** — `is_unbalance=True`, stratified K-fold
2. **XGBoost + Optuna Bayesian HPO** — tune `max_depth`, `min_child_weight`, `gamma`
3. **CatBoost** — for high-cardinality categorical features (machine ID, batch ID, shift)
4. **Aggressive Feature Engineering** — ratios, interactions, rolling stats, physics features (surface roughness, defect density)
5. **Target Encoding + Pseudo-Labeling** — high-confidence test predictions as training data
6. **Class Imbalance** — `scale_pos_weight` (cost-sensitive) over SMOTE for tabular
7. **Stacking Ensemble (2-layer)** — LGBM + XGB + CatBoost + ETC + LR → LR meta
8. **AutoGluon / H2O AutoML** — sanity check + diverse ensemble seed
9. **Neural Tabular** (TabNet, FT-Transformer, NODE) — only if >200K rows
10. **Threshold Optimization + Calibration** — `CalibratedClassifierCV`, optimize for F1/recall on OOF

### Practice Datasets (next 12 days)
- **Kaggle Steel Plate Defect Prediction (S4E3)** — closest analog
- **UCI Steel Plates Faults** (1,941 rows, 27 features, 7 defect types)
- **Severstal Steel Defect Detection** (Kaggle, image-based)
- **NASA CMAPSS** (RUL prediction)
- **UCI Steel Industry Energy Consumption** (35K rows hourly)

---

## Round 2: Agentic AI (10 Project Ideas)

### Context
Tata Steel has 300+ agents in production (Google Cloud + ADK + Gemini, April 2026). They're hiring for this exact skillset. Wins go to: specific (blast furnace, not "factory") + working demo + human-in-loop + business framing first.

| # | Title | Persona | Tech Stack | Difficulty |
|---|-------|---------|------------|-----------|
| 1 | **BlastGuard** | Furnace shift supervisor | LangGraph + Claude/Gemini + RAG (SOPs) + anomaly detection + approval node | Medium |
| 2 | **SteelDoc** | Hindi-speaking line operator | LangGraph + Gemini Flash + multilingual RAG + escalation pattern | Medium |
| 3 | **MaintenanceOrchestrator** | Maintenance engineer (hot strip mill) | LangGraph supervisor + 4 sub-agents + SAP PM mock + spare parts API | Med-Hard |
| 4 | **QualityGuard** | QC engineer (cold rolling) | LangGraph + Gemini multimodal + Severstal images + decision branching | Medium |
| 5 | **RawMaterialAdvisor** | Procurement head | LangGraph parallel + Tavily news + commodity APIs + blend optimizer | Medium |
| 6 | **SafetyEyeIQ** | Plant safety officer | LangGraph + safety log + weather + roster + pattern analysis | Medium |
| 7 | **EnergyOptimizer** | Energy manager | LangGraph re-planning loop + LP optimizer (PuLP) + tariff lookup | Med-Hard |
| 8 | **CustomerComplaintIntelligence** | Customer service mgr | Gemini multimodal + coil traceability DB + email drafter | Medium |
| 9 | **CarbonAccountant** | Sustainability head | LangGraph scheduled + IPCC factors + Net Zero trajectory + PDF report | Low-Med |
| 10 | **SupplyChainSentinel** | VP Supply Chain | LangGraph parallel research + Tavily + risk scoring + daily bulletin | Low-Med |

---

## What Tata Steel is Screening For (Hiring Lens)
| What | Round 1 | Round 2 |
|------|---------|---------|
| Statistical rigor | Proper CV, no leakage, honest OOF | Edge case handling |
| Domain understanding | Physics-sensible features | Real Tata Steel problem (not toy) |
| Code quality | Reproducible, clean, documented | Modular agent code, clear state |
| Business framing | SHAP → business insight | Open with ₹ impact, not "cool demo" |
| Communication | Clear README | Explainable to plant manager |
| Agentic maturity | N/A | Human-in-loop, no safety hallucination |

## Critical Demo Tip for Round 2
Open with: *"This agent addresses [specific Tata Steel problem]. Today it costs [X]. Our agent reduces by [Y]. Let me show you."* Then demo. Then explain architecture. Hiring managers respond to this framing.

## Top Picks for Ujjawal
- **R1 modeling stack:** LightGBM + Optuna + Stacking — battle-tested combo. Build the K-fold OOF template NOW (don't improvise during 10 days).
- **R2 ideas (highest win prob):**
  - **#1 BlastGuard** — mirrors Tata Steel's iROC + Asset Sphere
  - **#3 MaintenanceOrchestrator** — supervisor pattern is judge-impressive
  - **#10 SupplyChainSentinel** — exact use case from Tata Steel's April press release

## Prep Plan (next 12 days, May 10–21)
**Week 1 (May 10–17):**
- Set up: Python 3.11, LightGBM, XGBoost, CatBoost, Optuna, SHAP
- Practice on Kaggle S4E3 + UCI Steel Plates
- Build Stratified K-Fold + OOF framework template
- Practice SHAP explanations

**Week 2 (May 17–21):**
- Build stacking ensemble template
- NASA CMAPSS practice (if maintenance round)
- Optuna pipeline (run overnight during competition)
- Read Xomnia-Tata Steel case study

**For Round 2 (now):**
- LangGraph official tutorial (2 days)
- Build human-in-loop agent by May 15
- Practice supervisor multi-agent pattern by May 18
- Read Tata Steel Google Cloud press release (know Zen AI, TDA, Safety EyeQ, Asset Sphere, HR Helpdesk)

## Eligibility Check (URGENT)
HackerEarth page says "final-year/2026 graduates." Confirm 2025 grad eligibility before spending more time. Email HackerEarth support.
