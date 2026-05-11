# Product Manager — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 5 candidates in `../agent-prompts/product-manager.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** PRD Drafter (senior PM persona)
**From library:** `data/agent-prompts/product-manager.md` → Prompt 1
**Source:** [Kraftful — Top ChatGPT Prompts for PMs](https://www.kraftful.com/prompts-for-pm)
**Author:** Kraftful
**License:** Free guide content

### Full Prompt (verbatim)

```
You are a senior product manager. Draft a PRD for [FEATURE NAME] that
solves [USER PROBLEM] for [TARGET USER].

Use these sections, in order:
  1. TL;DR (3 sentences max)
  2. Problem statement (with evidence — quote any user research I paste)
  3. Goals & non-goals (3 of each)
  4. Target users & primary use cases
  5. User stories (As a / I want / So that) — group by persona
  6. Functional requirements (numbered, testable)
  7. Non-functional requirements (perf, security, accessibility)
  8. Success metrics (leading + lagging, with target deltas)
  9. Open questions
  10. Out of scope / future iterations

Be specific and opinionated. If a section requires information I haven't
provided, say "NEEDS INPUT: ..." instead of inventing.

Context:
[PASTE — user research, business goals, constraints, tech notes]
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** Senior PM persona — recognizable, scopes the model's reasoning to enterprise-grade artifacts.
- **Scope boundaries:** 10 named sections in order; non-goals required as a peer to goals (often skipped).
- **Output format:** Pinned PRD structure — directly drops into Notion/Confluence.
- **Reasoning techniques:** "NEEDS INPUT" pattern is anti-hallucination — model flags rather than fabricates.
- **Safety / refusal patterns:** Anti-fabrication clause ("NEEDS INPUT: ..." instead of inventing).
- **Examples / few-shot:** None inline, but section names are unambiguous.

### 2026 trend relevance
- **Modern frameworks:** PRD format with leading + lagging metrics matches modern PM practice (Reforge, Lenny Rachitsky).
- **Current tech references:** NFRs include accessibility (a 2026 must-have).
- **Structured output:** Section-numbered, parseable, composable.
- **Safety alignment:** "NEEDS INPUT" pattern prevents the #1 PM-AI failure mode (fabricated metrics).

### Deployability
- **License:** Free Kraftful guide content — cite, adapt freely.
- **Vendor lock:** None.
- **Jarvis adaptability:** Trivial; Boss pastes context, gets a draft.

---

## Runners-up + Trade-offs

### #2: RICE Prioritisation Helper (Prompt 2)
- **Why not picked:** Excellent specialized tool for prioritization, narrower scope than the PRD drafter. Pair with the winner.
- **When to use this instead:** Quarterly planning, backlog grooming.

### #3: JTBD User Interview Synthesiser (Prompt 3)
- **Why not picked:** Tightly scoped to interview-data synthesis; upstream of PRD work.
- **When to use this instead:** Right after 5+ user interviews.

### #4: Roadmap Narrative Builder (Prompt 4)
- **Why not picked:** Strategic communication artifact, complement to (not replacement for) PRD work.
- **When to use this instead:** Board meetings, stakeholder alignment.

### #5: Feature Kill-or-Keep Memo (Prompt 5)
- **Why not picked:** Specialized pruning tool; valuable but narrower.
- **When to use this instead:** End-of-quarter portfolio review.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/product-manager-agent.md`
2. **Adaptations needed:**
   - Reinforce "NEEDS INPUT" pattern with Jarvis's never-fabricate directive.
   - Add Hinglish toggle for product context delivered in Hinglish.
   - Wire memory loader for projects.md.
3. **Tool access (suggested):** Read access to product memory, prior PRDs; no autonomous publish.
4. **Model recommendation:** sonnet (good long-form structured writing); opus for v0 product strategy work.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Senior PM, well-defined |
| Scope boundaries | 5/5 | 10 named sections, non-goals required |
| Output format guidance | 5/5 | Pinned PRD structure |
| Reasoning techniques | 4/5 | NEEDS INPUT pattern; no explicit CoT |
| Safety / refusal patterns | 4/5 | Anti-fabrication; could add stronger metric-honesty rules |
| 2026 tech relevance | 4/5 | Accessibility in NFRs; could mention AI/agentic features |
| License-friendliness | 4/5 | Cite Kraftful; free for adaptation |
| **Overall** | **31/35** | Most-reusable PM artifact in candidate set |
