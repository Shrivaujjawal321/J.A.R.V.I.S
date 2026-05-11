# GenAI Forge 2026 (SmartInternz / SmartBridge) — Deep Research

**Deadline:** 2026-05-16 | **Mode:** Hybrid (online bootcamp + offline finale) | **Stack:** IBM Cloud + Watson Studio (mandatory)

## Important Discovery
GenAI Forge has only **2 official problem statements** (not multiple themes). This format has been consistent across 4 prior editions.

---

## Problem Statement 1: Optimized Warehouse Management of Perishable Goods

**Official wording:**
> ML model to predict demand for next 10 weeks
> Mobile/Web app to interact with model deployed on IBM Cloud

### What it's really asking
Full-stack ML *product*, not just a model. Need: trained forecasting model on Watson Studio + REST API on Watson ML + working web/mobile app + clean UI/UX.

### Sub-problems
- Data pipeline (M5, BigMart, Agmarknet datasets)
- Feature engineering (festivals: Diwali/Eid, weather, day-of-week, shelf-life decay)
- Model: SARIMA vs LSTM vs XGBoost vs IBM AutoAI-TS vs IBM Granite TinyTimeMixer (Feb 2025 GA)
- Deployment: Watson ML REST endpoint + Streamlit/Flask frontend
- Actionability: forecast → procurement recs + reorder alerts + waste flags
- UI/UX dashboard (judges score this explicitly)

### Required Tech Stack
- IBM Watson Studio (mandatory)
- IBM Cloud (mandatory)
- Watson Machine Learning for deployment
- IBM SkillsBuild account (bootcamp May 19–Jun 22)
- Python for ML; Android/Web for app
- IBM Granite Time Series (`ibm-watsonx-ai` SDK) — bonus credibility

### 10 Project Ideas
| # | Title | Pitch | Difficulty |
|---|-------|-------|-----------|
| 1 | **FreshCast** | IBM Granite + LSTM hybrid + Indian festival features + auto reorder alerts | Medium |
| 2 | **PerishAI Manager** | Multi-role app: operator + manager dashboards + IBM Cognos | Medium |
| 3 | **Cold Chain AI** | Forecast + LP storage zone optimization (₹92K cr India loss) | Med-Hard |
| 4 | **VoiceOrder** | Hindi/regional voice query → Watson ML forecast (Whisper + IndicTrans2 + Granite) | Hard |
| 5 | **WasteWatch** | Real-time waste prediction + markdown pricing recommender | Medium |
| 6 | **SupplyGPT** | Conversational supply chain analyst (RAG + Watson ML tool calls) | Medium |
| 7 | **AgriCast India** | Onion/tomato/potato — SARIMAX + Agmarknet API + price-demand correlation | Med-Hard |
| 8 | **SmartShelf** | Simulated IoT shelf sensors + Event Streams + auto reorder | Hard |
| 9 | **DemandExplainer** | XGBoost + SHAP + Granite NL explanations in Hindi | Medium |
| 10 | **ZeroWaste Network** | Multi-warehouse demand balancing + transfer optimization (NetworkX + map UI) | Hard |

---

## Problem Statement 2: Wind Turbine Energy Output Prediction

**Official wording:**
> Time series model forecasting power output (1-72 hr) based on weather
> App to recommend Power Grid optimal energy usage timing

### Required Tech Stack
- **IBM Weather Company Data** (mandatory — IBM Cloud service, key differentiator)
- IBM Watson Studio + Watson ML
- Python ML + Android/Web app
- Public datasets for practice: Kaggle wind SCADA, ENGIE La Haute Borne

### Sub-problems
- Weather data ingestion via IBM Weather Company Data API
- Power curve modeling (Weibull/cubic relationship — physics knowledge scores)
- Multi-horizon forecasting (1h vs 72h have different accuracy)
- Uncertainty quantification (probabilistic > point forecast for grid scheduling)
- Grid recommendation engine (the business logic layer)
- Wake effect / farm-level aggregation

### 10 Project Ideas
| # | Title | Pitch | Difficulty |
|---|-------|-------|-----------|
| 1 | **WindWise** | IBM Granite TinyTimeMixer + IBM Weather Co. + probabilistic 72h forecast | Medium |
| 2 | **GridGuard** | Multi-stakeholder app (operator + dispatcher + trader views) | Medium |
| 3 | **TurbineGPT** | Hindi conversational agent for wind farm operators (Granite + WhatsApp) | Hard |
| 4 | **WindIndex India** | Map-based atlas of 5 wind states (Rajasthan, Gujarat, TN, KA, AP) | Med-Hard |
| 5 | **CurtailmentKiller** | TFT + anomaly detection — prevent ₹crores curtailment loss | Hard |
| 6 | **SolarWindBlend** | Hybrid renewable dispatcher (wind + solar blend optimizer) | Med-Hard |
| 7 | **PredictiveMaintenance+** | Output forecast + CUSUM maintenance flag + grid re-commitment | Hard |
| 8 | **EnergyArbitrage** | Wind forecast + IEX price → battery charge/discharge schedule | Medium |
| 9 | **FarmLevelForecaster** | Single turbine LSTM + Jensen wake model + farm aggregation | Hard |
| 10 | **GridTwin** | Digital twin (Three.js 3D) + Watson ML forecast + live IBM Weather feed | Hard |

---

## Top Picks for Ujjawal
- **PS1 — SupplyGPT (#6)**: GenAI-native in a "GenAI Forge" hackathon. RAG + Watson ML tool calling. Full IBM stack story.
- **PS2 — WindWise (#1)**: IBM's newest model (Granite TinyTimeMixer Feb 2025) + IBM Weather Co. (mandatory tool). Clean technical story.
- **Add-on (either PS):** Voice/Hindi layer (VoiceOrder / TurbineGPT pattern) — Jury Award territory at SmartInternz.

## Judging Rubric (consistent across editions)
- Unique value proposition
- Scope defined + completed (no half-done prototypes)
- Programming logic quality (no Jupyter spaghetti)
- Code scalability
- Naming conventions + exception handling (judges literally check)
- UI/UX design (matters more than expected)
- Real-world applicability
- 4-min demo clarity (live system > slides)

## Timeline (tight!)
- Register by **May 16**
- Bootcamp: May 19 – Jun 22 (start IBM setup Day 1, don't wait)
- Solution dev: May 23 – Jun 6 (only 2 weeks)
- Evaluation: Jun 9-13
- Offline finale: Jun 19

## IBM Stack Quick-Start
1. Sign up: IBM Cloud free tier + Watson Studio lite plan
2. Watson Studio project → upload dataset → AutoAI-TS for baseline
3. Extend with custom features → deploy as Watson ML REST endpoint
4. Call from Flask/Streamlit frontend
5. For IBM Granite TS: `pip install ibm-watsonx-ai`, use `TSModelInference` class
