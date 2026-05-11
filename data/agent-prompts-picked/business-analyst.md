# Business Analyst — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 5 candidates in `../agent-prompts/business-analyst.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Requirements-to-User-Stories Converter
**From library:** `data/agent-prompts/business-analyst.md` → Prompt 1
**Source:** [Docsbot — Business Analysis to User Stories](https://docsbot.ai/prompts/business/business-analysis-to-user-stories)
**Author:** Docsbot
**License:** Free prompt template (cite)

### Full Prompt (verbatim)

```
Act as a senior Business Analyst. Convert the following business
requirements into user stories.

Step 1 — Identify the user roles / personas affected. List them.

Step 2 — For each user need, produce a user story in the format:
  "As a [role], I want [feature/capability], so that [benefit]."

Step 3 — For each story, add:
  - 3-5 acceptance criteria in Gherkin form:
    Given [context], When [action], Then [outcome]
  - Priority (Must / Should / Could / Won't — MoSCoW)
  - Story points estimate (Fibonacci: 1, 2, 3, 5, 8, 13)
  - Dependencies on other stories or systems
  - Out-of-scope notes (what this story explicitly does NOT cover)

Step 4 — Validate against INVEST:
  - Independent / Negotiable / Valuable / Estimable / Small / Testable
  Flag any story that fails a criterion and propose a split.

Step 5 — Output the final story map grouped by epic.

Requirements:
[PASTE]
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** Senior BA, anchored to recognized BABOK-style practice.
- **Scope boundaries:** 5 numbered steps; closed-set frameworks (MoSCoW, Fibonacci, Gherkin, INVEST).
- **Output format:** Story map grouped by epic; per-story 6-field structure.
- **Reasoning techniques:** INVEST validation forces self-critique; auto-flags failing stories with split proposals.
- **Safety / refusal patterns:** Implicit (validation + flagging rather than refusal); won't ship broken stories silently.
- **Examples / few-shot:** Format examples inline ("As a [role], I want...").

### 2026 trend relevance
- **Modern frameworks:** INVEST + Gherkin + MoSCoW are the standard agile BA toolkit; still dominant in 2026.
- **Current tech references:** Ready for Jira/Linear ingestion (story-points field, dependency flags).
- **Structured output:** Engineer-ready, sprint-ready.
- **Safety alignment:** Validation step prevents broken stories from shipping.

### Deployability
- **License:** Docsbot free template — cite on reuse.
- **Vendor lock:** None.
- **Jarvis adaptability:** Trivial; engineering teams ingest the output directly.

---

## Runners-up + Trade-offs

### #2: Current-State / Future-State Process Mapper (Prompt 2)
- **Why not picked:** Excellent process-modeling tool with Mermaid output, but narrower scope (process work).
- **When to use this instead:** Process-improvement engagements, ERP/CRM migrations.

### #3: Stakeholder Analysis + RACI (Prompt 3)
- **Why not picked:** Project-kickoff artifact; specialized.
- **When to use this instead:** Before any steering committee.

### #4: FR vs NFR Teaser (Prompt 4)
- **Why not picked:** Cleanup tool; useful upstream of user-story conversion.
- **When to use this instead:** Right after stakeholder workshops.

### #5: Test Scenarios + UAT Script Builder (Prompt 5)
- **Why not picked:** Test artifact; downstream of user stories.
- **When to use this instead:** End of sprint, pre-UAT.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/business-analyst-agent.md`
2. **Adaptations needed:**
   - Reinforce never-fabricate rule: if requirements are ambiguous, flag rather than infer.
   - Wire in projects.md context for Boss's specific projects.
   - For Indian-market projects, add compliance notes (DPDP, sector-specific regulations).
3. **Tool access (suggested):** Read access to requirements docs (Notion/Drive); no autonomous Jira/Linear ticket creation (draft, then human imports).
4. **Model recommendation:** sonnet (structured-text-heavy work, classification).

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Senior BA, BABOK-aligned |
| Scope boundaries | 5/5 | 5 steps, closed-set frameworks |
| Output format guidance | 5/5 | Story map + per-story 6-field schema |
| Reasoning techniques | 5/5 | INVEST self-validation with split proposals |
| Safety / refusal patterns | 3/5 | Implicit flagging; could add explicit ambiguity-refusal |
| 2026 tech relevance | 4/5 | Standard agile tooling; could mention AI-augmented requirements |
| License-friendliness | 4/5 | Cite Docsbot on reuse |
| **Overall** | **31/35** | Most reusable BA artifact; bridge to engineering |
