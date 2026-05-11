# Data Analyst — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 6 candidates in `../agent-prompts/data-analyst.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** OpenAI Cookbook Data Analyst (SQL against schema)
**From library:** `data/agent-prompts/data-analyst.md` -> Prompt 1
**Source:** [OpenAI Cookbook — GPT Action SQL Database](https://github.com/openai/openai-cookbook/blob/main/examples/chatgpt/gpt_actions_library/gpt_action_sql_database.ipynb)
**Author:** OpenAI
**License:** MIT

### Full Prompt (verbatim)

```
You are a data analyst. Your job is to assist users with their business questions by analyzing the data contained in a PostgreSQL database.

Database schema:
[Insert your schema here — table names, columns, types, foreign keys, brief description of each table]

When answering a question:
1. First, consider what data is needed against the schema above. If the question cannot be answered with the available tables/columns, say so explicitly.
2. Write a PostgreSQL query and submit it via the API.
3. If the analysis requires statistics, transformation, or visualization beyond what SQL can express cleanly, use the code interpreter on the returned data.
4. Return the answer with: the query you ran, the result, and a one-paragraph plain-English interpretation.

Never run destructive statements (INSERT, UPDATE, DELETE, DROP, TRUNCATE, ALTER). If a user asks for one, refuse and explain why.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** Specific role — "data analyst" against a Postgres DB. Concrete enough that the model doesn't drift into "data science philosophy."
- **Scope boundaries:** Read-only via the destructive-statement blocklist; clear "if you can't answer, say so" pattern.
- **Output format:** Pinned 3-part output (query + result + plain-English interpretation).
- **Reasoning techniques:** Schema-first thinking ("consider what data is needed"), tool delegation to code interpreter when SQL is insufficient.
- **Safety / refusal patterns:** Explicit refusal for write/DDL statements. Honest "can't answer" pattern instead of guessing.

### 2026 trend relevance
- **Modern frameworks:** Two-tool pattern (SQL + code interpreter) — canonical agentic data-analyst design.
- **Current tech references:** Postgres, code interpreter — vendor-neutral, widely deployable.
- **Structured output:** Triplet of artifacts every response.
- **Safety alignment:** Blocklist for destructive ops is the right primitive for read-only analyst agents.

### Deployability
- **License:** MIT — clean, redistributable.
- **Vendor lock:** None — Postgres can swap to MySQL/Snowflake/BigQuery with one schema substitution.
- **Jarvis adaptability:** Plug Jarvis's data sources (sheets, drive, local CSV) and code-agent for stats. Schema placeholder makes it template-ready.

---

## Runners-up + Trade-offs

### #2: EDA Walkthrough (Prompt 5)
- **Why not picked:** Excellent but narrower — for "I have a new dataset" first-pass only, not general analyst Q&A.
- **When to use this instead:** First time seeing a dataset; data-quality audits; pre-modeling validation. Use as a sibling agent or sub-skill.

### #3: A/B Test Analyzer (Prompt 6)
- **Why not picked:** Highly specialized for experiment analysis (SRM, peeking, multiple comparisons). Belongs in statistician territory; perfect as a sub-agent.
- **When to use this instead:** Analyzing experiments. Pair with statistician agent.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/data-analyst.md`
2. **Adaptations needed:** Substitute Postgres with whatever Jarvis touches (sheets, Notion DB, local SQLite/DuckDB). Inline the schema placeholder via tool. Add fallback: "if no DB, use pandas on CSV input."
3. **Tool access (suggested):** Read, Write, mcp__sheets__*, Bash (for sqlite/duckdb), code-execution if available.
4. **Model recommendation:** sonnet — haiku for trivial pulls, opus for complex multi-join reasoning.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Crisp role, concrete domain. |
| Scope boundaries | 5/5 | Destructive blocklist + can't-answer pattern. |
| Output format guidance | 5/5 | Pinned 3-part response. |
| Reasoning techniques | 4/5 | Tool delegation; could add chain-of-thought for joins. |
| Safety / refusal patterns | 5/5 | Explicit DDL/DML blocklist. |
| 2026 tech relevance | 4/5 | Solid but written pre-MCP era; easy to upgrade. |
| License-friendliness | 5/5 | MIT. |
| **Overall** | **33/35** | Production-ready. |
