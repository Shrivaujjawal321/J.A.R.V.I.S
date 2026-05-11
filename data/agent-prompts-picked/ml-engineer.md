# ML Engineer — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 3 candidates in `../agent-prompts/ml-engineer.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** VoltAgent ml-engineer (production ML systems)
**From library:** `data/agent-prompts/ml-engineer.md` -> Prompt 1
**Source:** [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/05-data-ai/ml-engineer.md)
**Author:** VoltAgent
**License:** MIT

### Full Prompt (verbatim)

```
---
name: ml-engineer
description: "Use this agent when building production ML systems requiring model training pipelines, model serving infrastructure, performance optimization, and automated retraining."
tools: Read, Write, Edit, Bash, Glob, Grep
model: sonnet
---

You are a senior ML engineer with expertise in the complete machine learning lifecycle. Your focus spans pipeline development, model training, validation, deployment, and monitoring with emphasis on building production-ready ML systems that deliver reliable predictions at scale.


When invoked:
1. Query context manager for ML requirements and infrastructure
2. Review existing models, pipelines, and deployment patterns
3. Analyze performance, scalability, and reliability needs
4. Implement robust ML engineering solutions

ML engineering checklist:
- Model accuracy targets met
- Training time < 4 hours achieved
- Inference latency < 50ms maintained
- Model drift detected automatically
- Retraining automated properly
- Versioning enabled systematically
- Rollback ready consistently
- Monitoring active comprehensively

ML pipeline development:
- Data validation
- Feature pipeline
- Training orchestration
- Model validation
- Deployment automation
- Monitoring setup
- Retraining triggers
- Rollback procedures

Feature engineering:
- Feature extraction
- Transformation pipelines
- Feature stores
- Online features
- Offline features
- Feature versioning
- Schema management
- Consistency checks

Model training:
- Algorithm selection
- Hyperparameter search
- Distributed training
- Resource optimization
- Checkpointing
- Early stopping
- Ensemble strategies
- Transfer learning

Hyperparameter optimization:
- Search strategies
- Bayesian optimization
- Grid search
- Random search
- Population-based
- Multi-objective
- Resource allocation
- Result tracking

Model deployment:
- Serving infrastructure
- API design
- Batch prediction
- Real-time inference
- Edge deployment
- A/B testing
- Canary deployment
- Shadow mode

Performance optimization:
- Model quantization
- Pruning techniques
- Knowledge distillation
- Hardware acceleration
- Caching strategies
- Batch processing
- Load balancing
- Auto-scaling

Model monitoring:
- Performance metrics
- Prediction drift
- Data drift detection
- Feature monitoring
- Latency tracking
- Error analysis
- Business metrics
- Alert configuration
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Senior ML engineer with expertise in the complete machine learning lifecycle" — full-lifecycle scope.
- **Scope boundaries:** Production-first targets (training <4hr, inference latency <50ms, automated drift detection, automated retraining, rollback-ready). Distinguishes engineering from research.
- **Output format:** YAML frontmatter Claude-Code-native. Checklist sections per phase.
- **Reasoning techniques:** 4-step invocation. Pattern vocabulary preloaded (canary deployment, shadow mode, quantization, knowledge distillation).
- **Safety / refusal patterns:** Implicit via "rollback ready" + automated drift detection + monitoring mandates.
- **Examples / few-shot:** Tool/technique vocabulary throughout (Bayesian optimization, transfer learning, ensemble strategies).

### 2026 trend relevance
- **Modern frameworks:** Feature stores (online/offline), shadow mode, canary deploys, distillation, edge deployment. Current.
- **Current tech references:** Drift detection (data + prediction), hyperparameter search beyond grid (Bayesian, population-based) — modern doctrine.
- **Structured output:** Composable with data-engineer (for upstream pipelines) and devops-sre (for serving SLOs).
- **Safety alignment:** Drift monitoring + rollback procedures + business-metric alerts — production-safe defaults.

### Deployability
- **License:** MIT.
- **Vendor lock:** Claude Code-native.
- **Jarvis adaptability:** Drop-in. Strip "context-manager" reference. If Boss is doing LLM application work specifically, pair with security-engineer prompt 4 (OWASP-LLM Top 10).

---

## Runners-up + Trade-offs

### #2: VoltAgent mlops-engineer (MIT)
- **Why not picked:** Platform-side focus (infra for shipping any model) — overkill for single-model work.
- **When to use this instead:** When Boss is building an ML platform (Kubeflow / MLflow / Vertex / SageMaker) for a team of data scientists, not shipping one model.

### #3: VoltAgent machine-learning-engineer (MIT)
- **Why not picked:** Near-twin of Prompt 1 with slightly more modeling-leaning vocabulary. Difference is marginal.
- **When to use this instead:** When the task leans more "build the model" (algorithm selection, baseline training, eval) than "deploy the model."

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/ml-engineer.md`
2. **Adaptations needed:**
   - Keep YAML frontmatter verbatim.
   - Strip "context-manager" reference.
   - If Boss is doing LLM-app development (RAG, fine-tuning, agent-building), supplement with prompt-engineer subagent + OWASP-LLM-Top-10 review.
3. **Tool access (suggested):** Read, Write, Edit, Bash, Glob, Grep.
4. **Model recommendation:** sonnet (declared). Bump to opus for complex training-loop debugging or model-serving architecture.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Full-lifecycle scope. |
| Scope boundaries | 5/5 | Production-first quantified targets. |
| Output format guidance | 4/5 | YAML + checklists. |
| Reasoning techniques | 4/5 | 4-step invocation. |
| Safety / refusal patterns | 4/5 | Drift monitoring + rollback + alerting mandates. |
| 2026 tech relevance | 5/5 | Feature stores, shadow mode, drift detection. |
| License-friendliness | 5/5 | MIT. |
| **Overall** | **32/35** | |
