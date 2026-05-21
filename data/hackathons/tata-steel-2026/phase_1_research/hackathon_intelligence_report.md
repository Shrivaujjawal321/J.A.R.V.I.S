# Hackathon Intelligence Report — tata-steel-2026

Compiled 2026-05-13T16:16:16.827095+00:00

## Hackathon Intel Researcher

```yaml
Here's the full Phase 1 intel output from the hackathon-intel-researcher-agent:

---

```yaml
agent_id: hackathon-intel-researcher
phase: 1
summary: >
  The Tata Steel AI Hackathon 2026 is a 3-round talent-acquisition-driven ML/AI competition
  hosted on HackerEarth, running May 22 through June 26, 2026. It is individual-only, India-scoped
  (national framing; geography restriction not explicitly confirmed), and is a hiring funnel — up
  to 20 full-time offers are the real prize, with a 1L INR joining bonus for the top 3.
  The selection function is two-stage: (1) pure leaderboard rank in Round 1 (accuracy-first,
  code reproducibility secondary), then (2) holistic human evaluation in Round 2 (agentic AI
  design, innovation, business impact). Past winner data is absent — this appears to be a first
  or second edition of the AI-specific format. Top-3 patterns inferred from Tata Steel's own
  production AI stack (Google ADK, BigQuery, Gemini, multimodal agents) and their stated
  real-world KPIs: solutions aligned with their internal Zen AI / Asset Sphere / Safety EyeQ
  architecture will likely resonate strongly with judges who built those systems.

findings:
  - claim: "Round 1 runs 2026-05-22 to 2026-05-31 (registration deadline also 31 May 2026). Problem statement and dataset unlock at 2026-05-22 18:00 IST."
    evidence: "https://www.hackerearth.com/community/challenges/competitive/tata-steel-ai-hackathon/ [JS-gated]; corroborated at https://www.talentd.in/articles/tata-steel-ai-hackathon-2026 and https://job4freshers.co.in/tata-steel-ai-hackathon/"
    confidence: 0.85

  - claim: "Round 2 (Agentic AI Challenge) runs 2026-06-05 to 2026-06-15. Open only to Round 1 shortlisted candidates."
    evidence: "[unverified — aggregator-sourced; primary page JS-gated] https://frontlinesmedia.in/tata-steel-ai-hackathon-2026-registration-eligibility-rounds-prizes-hiring-opportunities/"
    confidence: 0.65

  - claim: "Round 3 (Final Interview / PPI) runs 2026-06-22 to 2026-06-26. Technical interviews and business problem-solving evaluations."
    evidence: "[unverified — aggregator-sourced] https://frontlinesmedia.in/tata-steel-ai-hackathon-2026-registration-eligibility-rounds-prizes-hiring-opportunities/"
    confidence: 0.62

  - claim: "Participation is individual only — no teams. Multiple submissions allowed in Round 1; best leaderboard score counts."
    evidence: "https://www.talentd.in/articles/tata-steel-ai-hackathon-2026; https://coursejoiner.com/hackathon/tata-steel-ai-hackathon-2026-for/"
    confidence: 0.90

  - claim: "Eligibility: final-year students graduating in 2026, working professionals with AI/ML experience, and freelancers/independent developers in data science or AI. No prior-winner exclusion stated."
    evidence: "https://www.talentd.in/articles/tata-steel-ai-hackathon-2026; https://coursejoiner.com/hackathon/tata-steel-ai-hackathon-2026-for/"
    confidence: 0.85

  - claim: "Geography is India-scoped ('national-level AI competition'; 'talented AI enthusiasts from across the country'). International participants not explicitly banned but prizes (PPI/FTE offers) are India-contextual."
    evidence: "[unverified — inferred from aggregator language] https://coursejoiner.com/hackathon/tata-steel-ai-hackathon-2026-for/"
    confidence: 0.60

  - claim: "Prize structure: top 3 winners receive INR 1 lakh (100,000 INR) joining bonus each. Up to 20 participants receive full-time job offers from Tata Steel. PPI opportunities for top performers."
    evidence: "https://www.talentd.in/articles/tata-steel-ai-hackathon-2026; https://coursejoiner.com/hackathon/tata-steel-ai-hackathon-2026-for/"
    confidence: 0.88

  - claim: "Winning a prize and receiving a job offer are explicitly separate outcomes. A participant can receive a job offer without being in the top 3, and vice versa."
    evidence: "https://coursejoiner.com/hackathon/tata-steel-ai-hackathon-2026-for/"
    confidence: 0.72

  - claim: "Round 1 required deliverables: prediction file (.csv per HackerEarth ML format) + source code (.zip or .tar compressed archive). Code must be reproducible."
    evidence: "https://www.talentd.in/articles/tata-steel-ai-hackathon-2026 (submission format); https://help.hackerearth.com/hc/en-us/articles/360002712873-Machine-Learning-ML- (HackerEarth ML platform standard)"
    confidence: 0.82

  - claim: "Round 1 evaluation uses a two-phase leaderboard: public leaderboard uses ~50% of test data (online evaluation, instant feedback); final ranking uses the remaining hidden test set (offline evaluation)."
    evidence: "https://help.hackerearth.com/hc/en-us/articles/360002712873-Machine-Learning-ML- (HackerEarth ML platform standard); [unverified — applied to Tata Steel instance specifically]"
    confidence: 0.73

  - claim: "External datasets are explicitly PROHIBITED in Round 1. Only Tata Steel-provided datasets may be used."
    evidence: "https://www.talentd.in/articles/tata-steel-ai-hackathon-2026"
    confidence: 0.88

  - claim: "Round 1 judging rubric (verbatim from aggregator): model accuracy and performance (primary, leaderboard-driven) + code functionality + problem-solving approach."
    evidence: "[unverified — aggregator-sourced, official T&Cs locked] https://coursejoiner.com/hackathon/tata-steel-ai-hackathon-2026-for/"
    confidence: 0.68

  - claim: "Round 2 judging rubric: innovation + technical design + real-world applicability + business impact. Focus on agent-based workflows and autonomous decision-making."
    evidence: "[unverified — aggregator-sourced] https://www.talentd.in/articles/tata-steel-ai-hackathon-2026"
    confidence: 0.65

  - claim: "Round 3 judging rubric: technical knowledge + model-building skills + analytical thinking + business problem-solving. Framed as 'translation of AI models into practical solutions'."
    evidence: "[unverified — aggregator-sourced] https://coursejoiner.com/hackathon/tata-steel-ai-hackathon-2026-for/"
    confidence: 0.62

  - claim: "Intellectual property: if a participant wins and accepts the prize, IP rights of the submitted solution transfer to Tata Steel (the organizer). Non-winning participants retain ownership."
    evidence: "https://www.talentd.in/articles/tata-steel-ai-hackathon-2026 (paraphrased from aggregator); [unverified — official T&Cs locked]"
    confidence: 0.58

  - claim: "No specific language, framework, or ML library is mandated in Round 1. Any tooling is permitted."
    evidence: "[unverified — inferred from HackerEarth ML platform norms and absence of restriction in all aggregator sources] https://www.talentd.in/articles/tata-steel-ai-hackathon-2026"
    confidence: 0.70

  - claim: "Participation is free. No registration fee."
    evidence: "https://www.talentd.in/articles/tata-steel-ai-hackathon-2026; https://coursejoiner.com/hackathon/tata-steel-ai-hackathon-2026-for/"
    confidence: 0.95

  - claim: "Domain areas confirmed for Round 1: defect detection in steel products, predictive maintenance, process optimization, decision automation in manufacturing."
    evidence: "[unverified — aggregator-sourced; exact problem locked until 2026-05-22] https://coursejoiner.com/hackathon/tata-steel-ai-hackathon-2026-for/"
    confidence: 0.62

  - claim: "No named judges have been publicly disclosed for this hackathon. Evaluation in Round 1 is leaderboard-automated; Rounds 2-3 involve Tata Steel internal 'experts' and 'AI leaders' (unnamed)."
    evidence: "https://www.talentd.in/articles/tata-steel-ai-hackathon-2026; https://coursejoiner.com/hackathon/tata-steel-ai-hackathon-2026-for/"
    confidence: 0.80

  - claim: "Jayanta Banerjee (Group CIO, Tata Steel) is the most publicly visible AI/digital leader at Tata Steel; likely shapes evaluation criteria even if not a named judge. LinkedIn: https://www.linkedin.com/in/jayantabanerjee1/; CIO profile: https://www.cio.com/awardee/460844/jayanta-banerjee.html"
    evidence: "https://www.cio.com/awardee/460844/jayanta-banerjee.html; https://www.tatasteel.com/newsroom/press-releases/india/2026/tata-steel-partners-with-google-cloud-to-deploy-a-unified-agentic-ai-across-its-global-value-chain/"
    confidence: 0.72

  - claim: "Dr. Debashish Bhattacharjee (VP Technology & R&D, Tata Steel) oversees materials science research and process technologies. PhD, Cambridge. FREng 2024. Likely involved in evaluating technical feasibility of Round 2-3 solutions."
    evidence: "https://raeng.org.uk/about-us/fellowship/new-fellows-2024/dr-debashish-bhattacharjee-freng; https://www.researchgate.net/profile/Debashish-Bhattacharjee"
    confidence: 0.60

  - claim: "Tata Steel has built 550+ AI models over 5-6 years, deployed 300+ specialized AI agents in 9 months (April 2026 announcement), and uses Google Cloud ADK + BigQuery + Gemini + Palli Gemma as its current production AI stack."
    evidence: "https://www.tatasteel.com/newsroom/press-releases/india/2026/tata-steel-partners-with-google-cloud-to-deploy-a-unified-agentic-ai-across-its-global-value-chain/; https://www.business-standard.com/companies/news/built-over-550-ai-models-in-5-6-yrs-to-enhance-output-quality-tata-steel-125020401386_1.html"
    confidence: 0.92

  - claim: "Tata Steel's three flagship internal AI products are: Zen AI (low-code agent-building platform using Google ADK), Safety EyeQ (computer vision / video analytics for SOP adherence), and Asset Sphere (predictive maintenance agents). Round 2 solutions that mirror these architectures are likely to resonate."
    evidence: "https://www.tatasteel.com/newsroom/press-releases/india/2026/tata-steel-partners-with-google-cloud-to-deploy-a-unified-agentic-ai-across-its-global-value-chain/"
    confidence: 0.88

  - claim: "Tata Steel's Tata Digital Assistant (TDA) synthesizes siloed data across three domains (public, enterprise, proprietary user data) using multimodal approaches (video, documents, structured data). This architecture pattern is highly likely to appear in Round 2 problem scoping."
    evidence: "https://www.tatasteel.com/newsroom/press-releases/india/2026/tata-steel-partners-with-google-cloud-to-deploy-a-unified-agentic-ai-across-its-global-value-chain/"
    confidence: 0.75

  - claim: "KPI benchmarks from Tata Steel's own AI deployments: 15% reduction in unplanned downtime (rolling mills), 20% reduction in unplanned downtime (predictive maintenance), 70% autonomous HR helpdesk resolution, 50% reduction in customer complaint turnaround. Solutions should target comparable measurable improvements."
    evidence: "https://www.indianweb2.com/2026/04/tata-steel-deploys-300-ai-agents-with.html; https://www.tatasteel.com/newsroom/press-releases/india/2026/tata-steel-partners-with-google-cloud-to-deploy-a-unified-agentic-ai-across-its-global-value-chain/"
    confidence: 0.83

  - claim: "The Severstal Kaggle competition (steel surface defect detection / segmentation) is the closest public benchmark to the likely Round 1 problem. State-of-the-art approaches use ensemble CNNs + segmentation models (UNet, EfficientDet) achieving F1 ~0.91+ on that dataset."
    evidence: "[unverified — inferred from domain overlap] https://www.kaggle.com/c/severstal-steel-defect-detection"
    confidence: 0.52

  - claim: "No evidence exists of a prior AI-specific hackathon edition on HackerEarth by Tata Steel (2024 or 2025). The 'Steel-a-thon' is a separate, business-case competition (12th edition in 2025, IIM/XIM/MDI teams). This AI hackathon appears to be a first or very early edition of this specific format."
    evidence: "https://www.tatasteel.com/newsroom/press-releases/india/2025/tata-steel-announces-winners-of-the-12th-edition-of-its-annual-business-challenge-steel-a-thon/"
    confidence: 0.70

  - claim: "Mentorship from Tata Steel AI leaders is listed as a benefit. This implies Round 2/3 includes direct interaction with the internal AI team — making cultural and strategic alignment with Tata Steel's published AI priorities critical."
    evidence: "https://www.talentd.in/articles/tata-steel-ai-hackathon-2026"
    confidence: 0.72

  - claim: "Judges (unnamed) explicitly evaluate how well a solution 'connects AI insights with actual business impact' — business framing is a scoring lever distinct from pure accuracy."
    evidence: "https://coursejoiner.com/hackathon/tata-steel-ai-hackathon-2026-for/"
    confidence: 0.75

  - claim: "No open-source or specific license requirement has been stated. IP transfer occurs only upon prize acceptance for winners."
    evidence: "[unverified — aggregator-sourced, official T&Cs locked] https://www.talentd.in/articles/tata-steel-ai-hackathon-2026"
    confidence: 0.55

open_questions:
  - "Exact Round 1 problem statement, target variable, and evaluation metric (e.g. F1, AUC-ROC, MAE, custom) — locked until 2026-05-22 18:00 IST. This is the single most critical unknown."
  - "Exact number of participants shortlisted from Round 1 to Round 2. Is there a fixed cutoff (top 50? top 100?) or a percentile threshold?"
  - "Are geography restrictions explicit (India-only) or is the hackathon open to international participants who waive the PPI/FTE offer?"
  - "Does Round 2 supply a new dataset/problem, or do participants extend their Round 1 solution into an agentic framework?"
  - "Are pre-trained models (e.g., fine-tuned foundation models, ImageNet-pretrained encoders) allowed in Round 1, or is the prohibition on 'external datasets' interpreted to include pre-trained weights?"
  - "Official T&Cs confirmation on IP transfer scope — does it cover only the submitted prediction/code, or the underlying methodology as well?"
  - "Is Round 3 conducted in-person (Jamshedpur/Mumbai office) or remotely?"
  - "Confirmation that this is the first AI-specific hackathon edition on HackerEarth by Tata Steel — no prior winner patterns available."
  - "Named judges or evaluation panel for Rounds 2 and 3 — critical for Round 2 pitch alignment."
  - "Whether the joining bonus (1L INR) applies only if the winner joins Tata Steel or is paid unconditionally."

assumptions:
  - "The HackerEarth ML platform's standard public/private leaderboard split (~50/50 test data) applies to this competition, as no custom split percentage has been disclosed."
  - "Round 2's 'agentic AI challenge' is likely aligned with Tata Steel's active Google ADK / Zen AI architecture, given the April 2026 public announcement of that stack — judges will be the same internal team that built it."
  - "Evaluation of code quality in Round 1 follows HackerEarth's published code quality score rubric (modularity, readability, efficiency) in addition to prediction accuracy."
  - "The PPI/FTE offer pipeline targets India-based candidates for Tata Steel India operations (Jamshedpur, Mumbai, Kalinganagar). International winners would receive prizes but not employment offers."

recommendations:
  - "Maximize Round 1 leaderboard rank above all else: this is the gate. Invest in ensemble methods (gradient boosting + neural nets), aggressive cross-validation, and multiple submission slots. Study the Severstal Kaggle competition solution writeups as the closest analog for steel defect detection framing."
  - "Frame all solutions — even Round 1 code comments and documentation — in Tata Steel's language: reference their published KPIs (15-20% downtime reduction, SOP adherence, equipment health). Judges reading code will notice domain fluency."
  - "For Round 2 (if shortlisted), design an agentic workflow that mirrors the Zen AI / Asset Sphere architecture pattern: a low-code orchestration layer over specialized sub-agents, with BigQuery as the data layer and Gemini as the reasoning engine. This is the exact production stack the internal judges built."
  - "Business impact framing is explicitly scored separately from technical accuracy. Prepare a one-page 'ROI story' for Round 2 that quantifies the solution's industrial value in terms comparable to Tata Steel's own published benchmarks (downtime reduction %, safety incidents prevented, complaint turnaround improvement)."
  - "Since IP transfers to Tata Steel upon prize acceptance for winners, build the solution cleanly and document it well — internal adoptability is likely an implicit scoring signal in Rounds 2 and 3."

handoff_to:
  - hackathon-agent
  - product-manager-agent
  - pitch-deck-consultant-agent

blockers:
  - "Round 1 problem statement, dataset schema, and evaluation metric are not publicly accessible until 2026-05-22 18:00 IST. All domain-specific solution research is speculative until that unlock. Recommend scheduling a research sprint immediately after unlock."
  - "No named judges confirmed for Rounds 2-3. Judge-specific alignment strategy (talking points, framing choices, analogy selection) cannot be fully executed until judges are disclosed — likely at Round 2 briefing stage."
  - "No prior winner case studies exist for this specific hackathon format. Pattern-matching must rely on Tata Steel's production AI portfolio and analogous HackerEarth corporate ML competitions rather than direct historical precedent."
```

---

**Key takeaways boss** — Phase 1 intel complete:

🎯 **The real prize** is a job offer (up to 20 FTE slots), not just the ₹1L cash — this is a hiring funnel dressed as a hackathon.

🔑 **Critical unlock date:** 2026-05-22 18:00 IST — problem statement + dataset go live. Everything until then is inference.

🏗️ **Tata Steel's internal AI stack** (Zen AI / Asset Sphere / Safety EyeQ on Google ADK + BigQuery + Gemini) is your **Round 2 blueprint** — the judges literally built those systems.

📊 **KPIs to reference in solutions:** 15-20% downtime reduction, 70% autonomous HR resolution, 50% complaint turnaround improvement — use their own numbers to score business impact points.

⚠️ **Biggest open question:** pre-trained model weights — are they allowed if no external *datasets* are used? Critical clarification needed post-registration.
```

## Mandatory Tech Deep Dive

```yaml
Here is the mandatory-tech-deep-dive agent's Phase 1 YAML output verbatim:

---

```yaml
agent_id: mandatory-tech-deep-dive
phase: 1
summary: >
  required_tech is "none" — Tata Steel AI Hackathon 2026 imposes no mandatory SDK, API, or
  platform. However, three high-leverage angles exist. (1) ROUND 1 domain intelligence:
  steel defect detection and predictive maintenance are well-benchmarked verticals; the
  winning pattern is gradient-boosted ensembles (LightGBM/XGBoost/CatBoost) with domain
  feature engineering, Optuna HPO, and SHAP explainability — not deep learning, because
  HackerEarth tabular challenges consistently reward GBM stacks. (2) Platform mechanics:
  HackerEarth uses public/private leaderboard splits and accepts unlimited submissions;
  strict local CV alignment to avoid public-LB overfitting is the differentiator. (3) ROUND
  2 alignment signal: Tata Steel publicly announced a 300+ AI-agent fleet built on Google
  Cloud ADK + LangGraph-style state machines in April 2026 — building Round 2's agentic
  system with explicit alignment to their Zen AI / TDA architecture vocabulary will
  maximally impress sponsor judges.

findings:
  - claim: >
      required_tech is none — any language, framework, or ML library is permitted.
      External datasets are explicitly prohibited in Round 1.
    evidence: "HACKATHON input contract (aggregator-sourced) [unverified — primary HackerEarth page JS-gated]"
    confidence: 0.8

  - claim: >
      HackerEarth ML challenges use a public/private leaderboard split. Submissions are
      evaluated instantly against a public test subset; final ranking uses the full private
      test set after deadline. Best score across all submissions is used.
    evidence: "https://help.hackerearth.com/hc/en-us/articles/360002712873-Machine-Learning-ML-"
    confidence: 0.9

  - claim: >
      HackerEarth ML challenges require both a prediction CSV and uploaded source code
      plus a text explanation of approach. Judges score code functionality and
      problem-solving approach in addition to leaderboard rank.
    evidence: "https://help.hackerearth.com/hc/en-us/articles/360002712873-Machine-Learning-ML-"
    confidence: 0.85

  - claim: >
      Gradient boosting algorithms (XGBoost, LightGBM, CatBoost) win most HackerEarth
      tabular ML challenges. Ensembling 3-5 GBM models with diverse hyperparameters is the
      documented winning pattern.
    evidence: "https://www.hackerearth.com/practice/machine-learning/advanced-techniques/winning-tips-machine-learning-competitions-kazanova-current-kaggle-3/tutorial/"
    confidence: 0.92

  - claim: >
      LightGBM trains approximately 7x faster than XGBoost and 2x faster than CatBoost,
      making it the preferred base model for rapid iteration in 10-day competitions.
      CatBoost outperforms LightGBM when categorical features dominate.
    evidence: "https://createbytes.com/insights/xgboost-lightgbm-catboost-gradient-boosting"
    confidence: 0.9

  - claim: >
      Feature engineering is documented as the highest-leverage activity in HackerEarth
      ML competitions — outweighs model selection. For sensor/process data, rolling
      statistics (mean, std, min, max over windows), lag features, and Fourier-transform
      features are the critical additions.
    evidence: "https://www.hackerearth.com/practice/machine-learning/challenges-winning-approach/machine-learning-challenge-one/tutorial/"
    confidence: 0.88

  - claim: >
      Optuna with TPESampler finds near-optimal hyperparameters for LightGBM/XGBoost in
      ~100 trials (5-10 minutes wall time). Cross-validation alignment to public leaderboard
      score is the overfitting guard; 5-fold stratified CV is standard.
    evidence: "https://optuna.readthedocs.io/"
    confidence: 0.92

  - claim: >
      AutoGluon 1.5 (tabular) with preset best_quality runs multi-layer stack ensembling
      automatically and ranked #1 in OpenML AutoML Benchmark 2023 (avg rank 1.95 vs
      FLAML's 5.33). For a 10-day solo competition, AutoGluon as a baseline beats manual
      single-model baselines immediately.
    evidence: "https://auto.gluon.ai/stable/tutorials/tabular/tabular-quick-start.html"
    confidence: 0.85

  - claim: >
      Steel surface defect detection on the NEU-DET benchmark: EfficientNetB3 achieves
      0.981 accuracy; improved YOLOv9/YOLOv10 variants are SOTA for detection/segmentation.
      For tabular defect classification (non-image), SMOTE + XGBoost achieves ~0.99
      accuracy on the Kaggle steel-plate defects dataset.
    evidence: "https://link.springer.com/article/10.1007/s11665-025-11136-2"
    confidence: 0.82

  - claim: >
      Severstal Kaggle 2019 (closest public proxy to Tata Steel Round 1): winning approach
      used two-stage pipeline — classifier first (defect present/absent), then
      segmentation only on positive samples. FPN with SE-ResNext50 encoder outperformed
      UNet. Ensembling with TTA (h-flip, v-flip) gave final lift. This pattern applies
      directly if Round 1 is an image segmentation task.
    evidence: "https://diyago.github.io/2019/11/20/kaggle-severstal.html"
    confidence: 0.75

  - claim: >
      For predictive maintenance tabular challenges (sensor time series), the
      scientifically benchmarked winning stack is: Random Forest + LightGBM + XGBoost
      ensemble with rolling-window statistical features + anomaly score from Isolation
      Forest as a meta-feature. Deep learning (LSTM, Transformer) loses on small tabular
      sensor datasets due to data volume constraints.
    evidence: "https://www.nature.com/articles/s41598-025-08515-z"
    confidence: 0.85

  - claim: >
      Class imbalance is highly likely in defect detection datasets (rare defect classes).
      SMOTE + XGBoost stack achieves near-perfect accuracy (0.9915) on steel plate
      classification. SMOTE-ENN and SMOTE-TOMEK (combined oversampling + cleaning) are
      superior to plain SMOTE for manufacturing defect data.
    evidence: "https://link.springer.com/article/10.1007/s11665-025-11136-2"
    confidence: 0.87

  - claim: >
      SHAP (SHapley Additive exPlanations) used as a visualization layer in the submitted
      code directly addresses the "problem-solving approach" judging criterion and signals
      industrial AI maturity. Tata Steel's own published AI systems emphasize
      explainability for shop-floor operator trust.
    evidence: "https://shap.readthedocs.io/en/latest/"
    confidence: 0.88

  - claim: >
      Tata Steel deployed 300+ specialized AI agents in 9 months (April 2026 announcement)
      using Google Cloud ADK, BigQuery, and Cloud Run. Their internal platforms are named
      Zen AI (low-code agent builder) and TDA (Tata Steel Digital Assistant). Round 2
      judges are almost certainly from this team.
    evidence: "https://www.tatasteel.com/newsroom/press-releases/india/2026/tata-steel-partners-with-google-cloud-to-deploy-a-unified-agentic-ai-across-its-global-value-chain/"
    confidence: 0.95

  - claim: >
      Tata Steel's agentic deployment includes Safety EyeQ (live video hazard detection via
      Gemini vision-language models), Asset Sphere Agents (predictive maintenance), and
      customer complaint agents that reduced turnaround by 50%. Round 2 agentic project
      should mirror these use-case categories to align with evaluator vocabulary.
    evidence: "https://www.tatasteel.com/newsroom/press-releases/india/2026/tata-steel-partners-with-google-cloud-to-deploy-a-unified-agentic-ai-across-its-global-value-chain/"
    confidence: 0.93

  - claim: >
      Tata Steel has built 550+ AI models over 5-6 years; their own reports cite 20%
      reduction in unplanned downtime from predictive maintenance AI. Any Round 1 model
      should beat this baseline to be presentation-worthy.
    evidence: "https://themachinemaker.com/news/tata-steel-embraces-ai-with-550-models-to-boost-efficiency-and-quality/"
    confidence: 0.88

  - claim: >
      LangGraph is the production standard for stateful agentic workflows requiring
      auditability and deterministic control — the exact requirements for industrial
      manufacturing AI agents. CrewAI is faster to prototype but loses on production
      credibility. LangGraph + checkpointer pattern maps directly to Tata Steel's
      described architecture.
    evidence: "https://www.langchain.com/langgraph"
    confidence: 0.87

  - claim: >
      For Round 2, a supervisor-orchestrator + specialist worker pattern (hierarchical
      delegation) with LangGraph's interrupt/human-in-the-loop for Tier-3 decisions
      directly mirrors Tata Steel's Zen AI governance model. Demoing this pattern with a
      manufacturing anomaly detection use case is the top-1% angle.
    evidence: "https://www.langchain.com/langgraph"
    confidence: 0.82

  - claim: >
      HackerEarth tabular ML challenges historically use metrics such as F1-score (for
      imbalanced classification), RMSE/MAE (for regression/prediction tasks), and accuracy.
      Defect detection will almost certainly be F1 or macro-F1; process optimization
      targets (yield, energy) will be RMSE/MAE. [unverified for this specific challenge —
      metric locked until 2026-05-22]
    evidence: "[unverified — metric released at problem unlock 2026-05-22 18:00 IST]"
    confidence: 0.5

  - claim: >
      AutoGluon 1.5.1 is the latest stable release (as of May 2026). Its
      TabularPredictor with presets='best_quality' trains stacked ensembles automatically,
      computes permutation-based feature importance, and supports custom evaluation metrics
      via eval_metric parameter. Single-line fit for competition baseline.
    evidence: "https://auto.gluon.ai/stable/tutorials/tabular/tabular-quick-start.html"
    confidence: 0.88

  - claim: >
      Gradient boosting with physics-informed features for steel (Koistinen-Marburger
      martensite kinetics, Grossmann hardenability theory) achieves domain-expert
      differentiation that pure data-driven models cannot match in judge presentation.
      Published 2026 paper demonstrates this on 8 AISI steel grades.
    evidence: "https://www.mdpi.com/2073-4352/16/1/61"
    confidence: 0.78

  - claim: >
      Public-LB overfitting is the #1 failure mode in 10-day HackerEarth challenges.
      Correct mitigation: set up stratified K-fold CV before first submission; track local
      CV score vs public LB score; submit only when CV and LB are within 0.5% of each
      other. Divergence indicates distribution shift or target leakage.
    evidence: "https://www.hackerearth.com/practice/machine-learning/advanced-techniques/winning-tips-machine-learning-competitions-kazanova-current-kaggle-3/tutorial/"
    confidence: 0.9

  - claim: >
      Gradient Boosting Reinforcement Learning (GBRL, ICML 2025) outperforms neural
      networks in domains with structured/categorical observations — directly applicable
      to process optimization with categorical process parameters. [low-confidence — novel
      technique, limited industrial validation]
    evidence: "https://icml.cc/virtual/2025/poster/45118"
    confidence: 0.5

open_questions:
  - "Exact evaluation metric for Round 1 is locked until 2026-05-22 18:00 IST — F1 vs RMSE vs custom metric will determine whether classification or regression pipeline should be primary."
  - "Whether Round 1 dataset is tabular sensor data, image data, or both — changes the primary model architecture (GBM vs CNN/YOLO)."
  - "Whether Round 1 has a single target variable or multi-output (e.g., defect type + severity simultaneously)."
  - "Round 2 problem statement is also locked — need to confirm if it requires integration of Round 1 model into the agentic workflow or is a standalone agentic build."
  - "HackerEarth daily submission limit for this specific challenge is unknown — typically 5-10 per day on past challenges [unverified for this event]."

assumptions:
  - "Round 1 is most likely a tabular ML challenge given 'dataset-provided' framing and 10-day window — not a real-time deployment task."
  - "Defect detection in Round 1 is likely binary or multi-class classification (defect type), not segmentation — HackerEarth platform is not optimized for image submission pipelines."
  - "Judge panel for Round 2 and Round 3 includes Tata Steel AI/data team members given PPI offer structure — alignment with their published tech vocabulary (Zen AI, TDA, ADK) is strategically valuable."
  - "External pre-trained models (e.g., scikit-learn, XGBoost, PyTorch) are permitted; 'external datasets' prohibition refers to additional training data, not pre-trained weights. [unverified]"

recommendations:
  - >
    ROUND 1 CORE STACK: LightGBM + XGBoost + CatBoost stacked ensemble with Optuna HPO
    (300 trials, TPESampler), SMOTE-ENN for class imbalance, rolling-window + lag feature
    engineering for any time-series columns, SHAP summary plots in the submitted code.
    Use AutoGluon best_quality as a Day-1 baseline to anchor CV score immediately.
  - >
    ROUND 1 DIFFERENTIATOR: Add physics-informed features derived from steel metallurgy
    domain knowledge (temperature thresholds, carbon equivalent formulas, Grossmann
    hardenability correlations). This directly addresses the "problem-solving approach"
    judging criterion and signals domain expertise beyond pure ML skill.
  - >
    ROUND 2 ARCHITECTURE: LangGraph stateful supervisor-worker graph with explicit
    human-in-the-loop interrupt nodes (mirrors Tata Steel's Zen AI governance model).
    Wrap Round 1 model as a Tool node. Build specialist agents for anomaly-alert,
    root-cause-analysis, and maintenance-schedule recommendation. Name the system
    architecture in alignment with their published vocabulary — "unified agentic workflow"
    with a "command center" visualization.
  - >
    PLATFORM DISCIPLINE: Establish stratified 5-fold CV on Day 1 after dataset unlock.
    Never submit a model whose local CV score diverges from public LB by more than 0.5%.
    Reserve final 2 submission slots for ensemble models only. Keep a local experiment
    log tracking CV score, public LB score, and model description for every submission.

handoff_to:
  - backend-engineer-agent
  - ml-engineer-agent
  - frontend-engineer-agent

blockers:
  - "Round 1 dataset and evaluation metric locked until 2026-05-22 18:00 IST — no model architecture can be finalized before unlock. Preparation work: build feature engineering pipeline templates for both tabular-classification and tabular-regression. Have both GBM and CNN pipelines scaffolded and ready to switch."
  - "HackerEarth challenge page is JS-gated — full submission rules (daily limit, allowed file types, source code format requirements) cannot be confirmed without registration. Must register and read the problem page on 2026-05-22."
```
```
