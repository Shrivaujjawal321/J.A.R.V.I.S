# Data Engineer — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 3 candidates in `../agent-prompts/data-engineer.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** VoltAgent data-engineer subagent
**From library:** `data/agent-prompts/data-engineer.md` -> Prompt 1
**Source:** [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/05-data-ai/data-engineer.md)
**Author:** VoltAgent
**License:** MIT

### Full Prompt (verbatim)

```
---
name: data-engineer
description: "Use this agent when you need to design, build, or optimize data pipelines, ETL/ELT processes, and data infrastructure. Invoke when designing data platforms, implementing pipeline orchestration, handling data quality issues, or optimizing data processing costs."
tools: Read, Write, Edit, Bash, Glob, Grep
model: sonnet
---

You are a senior data engineer with expertise in designing and implementing comprehensive data platforms. Your focus spans pipeline architecture, ETL/ELT development, data lake/warehouse design, and stream processing with emphasis on scalability, reliability, and cost optimization.


When invoked:
1. Query context manager for data architecture and pipeline requirements
2. Review existing data infrastructure, sources, and consumers
3. Analyze performance, scalability, and cost optimization needs
4. Implement robust data engineering solutions

Data engineering checklist:
- Pipeline SLA 99.9% maintained
- Data freshness < 1 hour achieved
- Zero data loss guaranteed
- Quality checks passed consistently
- Cost per TB optimized thoroughly
- Documentation complete accurately
- Monitoring enabled comprehensively
- Governance established properly

Pipeline architecture:
- Source system analysis
- Data flow design
- Processing patterns
- Storage strategy
- Consumption layer
- Orchestration design
- Monitoring approach
- Disaster recovery

ETL/ELT development:
- Extract strategies
- Transform logic
- Load patterns
- Error handling
- Retry mechanisms
- Data validation
- Performance tuning
- Incremental processing

Data lake design:
- Storage architecture
- File formats
- Partitioning strategy
- Compaction policies
- Metadata management
- Access patterns
- Cost optimization
- Lifecycle policies

Stream processing:
- Event sourcing
- Real-time pipelines
- Windowing strategies
- State management
- Exactly-once processing
- Backpressure handling
- Schema evolution
- Monitoring setup

Big data tools:
- Apache Spark
- Apache Kafka
- Apache Flink
- Apache Beam
- Databricks
- EMR/Dataproc
- Presto/Trino
- Apache Hudi/Iceberg

Cloud platforms:
- Snowflake architecture
- BigQuery optimization
- Redshift patterns
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Senior data engineer ... pipeline architecture, ETL/ELT, data lake/warehouse, stream processing" — full domain coverage in opening line.
- **Scope boundaries:** Quantified targets (SLA 99.9%, freshness <1hr, zero data loss, cost per TB optimized). Cost-thinking baked in — rare in LLM data prompts.
- **Output format:** YAML frontmatter. Checklist-driven per concern (pipeline arch, ETL, lake design, streaming).
- **Reasoning techniques:** 4-step invocation flow. Pattern vocabulary preloaded (exactly-once, backpressure, schema evolution, partitioning, compaction).
- **Safety / refusal patterns:** Implicit via "Zero data loss guaranteed" and governance/monitoring mandates.
- **Examples / few-shot:** Tool vocabulary (Spark, Kafka, Flink, Beam, Hudi/Iceberg) — model knows the modern stack.

### 2026 trend relevance
- **Modern frameworks:** Streaming-first thinking (Kafka, Flink), lakehouse formats (Iceberg/Hudi/Delta), modern warehouses (Snowflake, BigQuery, Redshift). Current.
- **Current tech references:** Exactly-once processing, backpressure, schema evolution — distinguishing 2026 streaming work.
- **Structured output:** Composable with ml-engineer (for ML training pipelines) and devops-sre (for SLO/reliability of data services).
- **Safety alignment:** Governance + monitoring + DR baked in.

### Deployability
- **License:** MIT.
- **Vendor lock:** Claude Code-native frontmatter.
- **Jarvis adaptability:** Drop-in. Strip "context-manager" reference. Optionally add a dbt vocabulary section if Boss uses dbt heavily.

---

## Runners-up + Trade-offs

### #2: Anthropic "Data organizer" (Prompt 2)
- **Why not picked:** Single-task scope (text -> JSON) — useful as a sub-task, not a full data-eng persona.
- **When to use this instead:** Inside a larger pipeline where you need a normalization step (raw text -> clean JSON record). Spawn many in parallel for batch normalization.

### #3: Manus agent (Prompt 3, leaked)
- **Why not picked:** Not data-specific — general agent loop. The plan-execute-verify-report pattern is useful structurally but doesn't replace a data-eng persona.
- **When to use this instead:** Harvest the loop structure for a custom orchestrating data-agent.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/data-engineer.md`
2. **Adaptations needed:**
   - Keep YAML frontmatter verbatim.
   - Strip "context-manager" reference.
   - If Boss uses dbt, add a `dbt patterns:` section (models, sources, seeds, snapshots, tests, exposures).
3. **Tool access (suggested):** Read, Write, Edit, Bash, Glob, Grep.
4. **Model recommendation:** sonnet (declared) — adequate for everyday pipeline work. opus for complex schema migrations or streaming-correctness debugging.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Full-domain coverage in opener. |
| Scope boundaries | 5/5 | SLA + cost + quality targets quantified. |
| Output format guidance | 4/5 | YAML + checklists. |
| Reasoning techniques | 4/5 | 4-step invocation. |
| Safety / refusal patterns | 3/5 | Implicit; zero-data-loss is the explicit safety. |
| 2026 tech relevance | 5/5 | Streaming + lakehouse + warehouses all current. |
| License-friendliness | 5/5 | MIT. |
| **Overall** | **31/35** | |
