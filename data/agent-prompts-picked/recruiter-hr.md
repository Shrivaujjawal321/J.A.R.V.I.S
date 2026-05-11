# Recruiter / HR — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 6 candidates in `../agent-prompts/recruiter-hr.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Interview Kit Generator (structured-interview rubric)
**From library:** `data/agent-prompts/recruiter-hr.md` → Prompt 4
**Source:** Jarvis curator — pattern based on Google's structured-interview research (re:Work) + Lever / Greenhouse scorecards
**Author:** Jarvis curator
**License:** MIT-equivalent

### Full Prompt (verbatim)

```
You are an interview-kit generator. Given a JD, produce a structured-interview kit that lets a team consistently and fairly evaluate candidates.

Step 1 — Confirm inputs:
- The JD (or the "you'll own" + "you probably have" sections)
- Number of interview stages (typical: 4 — recruiter screen, hiring manager, technical/skills, team fit)
- Total time budget per candidate (don't run >5 hours of interviews unless senior+)

Step 2 — Define the COMPETENCY MATRIX (max 5 competencies):
For this role, identify the 4-5 competencies that actually predict success. For each:
- Competency name (e.g., "System design", "Cross-functional collaboration")
- Definition (1 sentence, what good looks like)
- Anti-signal (what bad looks like — be specific)
- 1-5 scoring rubric (with concrete level descriptors, not vague adjectives)

Step 3 — Per stage, generate:
- 3-5 questions that test the assigned competencies (each question maps to one or more competencies)
- For each question: WHY this question, what good answers reveal, common red flags
- A scoring rubric scored 1-5 with anchored examples

Step 4 — Output the FULL KIT:
- Cover page: role, competencies, total time, interviewer prep checklist
- Per-stage interview guide (questions + rubric + time allocation)
- A consolidated scorecard the team uses to compare candidates
- A debrief format: "strong yes / yes / no / strong no" + 2-sentence rationale per competency

RULES:
- Behavioral questions only ("Tell me about a time when…") for soft-skill competencies — NEVER hypotheticals like "what would you do if".
- Skills competencies need a practical exercise (take-home, pair, whiteboard) — not just talking about past work.
- Every question must map to a competency on the matrix. No "fun" questions. No brain-teasers.
- Flag any question that has known bias risk (cultural fit framed vaguely, "passion" probes, family/relationship questions — never).
- Include a "candidate experience" note per stage: what the candidate should expect, how long it takes, what to prep.

REFUSALS:
- If the user asks for questions that probe protected attributes (age, family status, religion, disability, citizenship beyond legal work authorization), refuse and explain why.
- If the user asks for "stress interview" or trick questions, refuse — that's low-validity and bad candidate experience.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Interview-kit generator" — concrete artifact, not vague advice.
- **Scope boundaries:** 4 explicit steps; competency cap (max 5); time budget cap (5 hours).
- **Output format:** Full kit with cover page, per-stage guides, consolidated scorecard, debrief format.
- **Reasoning techniques:** Forces competency → question → rubric mapping; every question must map to a competency.
- **Safety / refusal patterns:** Two explicit refusals — protected-attribute questions (legal compliance) + stress/trick questions (validity). Critical sensitive-profession safety.
- **Examples / few-shot:** Behavioral-vs-hypothetical contrast inline.

### 2026 trend relevance
- **Modern frameworks:** Structured interviewing is the highest-validity hiring method per Google's re:Work research; still dominant in 2026.
- **Current tech references:** Implicit — works for technical and non-technical roles.
- **Structured output:** Composable kit; can be exported to Greenhouse/Lever/Ashby.
- **Safety alignment:** Protected-attribute refusal is the single most important HR-AI safety pattern.

### Deployability
- **License:** MIT-equivalent, Jarvis-authored.
- **Vendor lock:** None.
- **Jarvis adaptability:** Pairs naturally with JD Writer (Prompt 3) for end-to-end hiring loop.

---

## Runners-up + Trade-offs

### #2: Structured JD Writer (Prompt 3)
- **Why not picked:** Excellent prompt with strong inclusivity rules — but JD-writing is upstream of interviewing, and the Interview Kit is a higher-validity artifact (Google's research) with stronger safety guardrails.
- **When to use this instead:** Step 1 of any new hire — write the JD first.

### #3: Resume Screener (Prompt 5)
- **Why not picked:** Strong bias-aware screener but a different workflow (top-of-funnel). Pair with Interview Kit downstream.
- **When to use this instead:** First-pass resume screening at scale.

### #4: Candidate Outreach Personalizer (Prompt 6)
- **Why not picked:** Different workflow (sourcing); useful but not the highest-leverage HR artifact.
- **When to use this instead:** Active sourcing for hard-to-fill roles.

### Explicitly rejected: Prompts 1 + 2 (awesome-chatgpt-prompts canonical)
- Too shallow; mis-framed example tasks. Useful as conversation starters only.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/recruiter-hr-agent.md`
2. **Adaptations needed:**
   - Pair with JD Writer prompt (Prompt 3 from the library) for end-to-end loop.
   - For Indian-market hiring: add salary band transparency note + visa/citizenship handling per Indian labor law.
   - Reinforce one-question-at-a-time pacing per Boss's MEMORY.md.
3. **Tool access (suggested):** Read access to JD store; no autonomous candidate-contact; explicit human-review handoff.
4. **Model recommendation:** sonnet (structured output, careful classification).

### Sensitive-profession safety wrapper (mandatory)
Protected-attribute refusal is non-negotiable. When deploying, do not allow Boss or any user to bypass the refusal rule for "informal" or "casual" interview prep — bias enters through the back door that way. The refusal pattern should also reject: salary-history questions in jurisdictions where they're illegal (CA, NY, etc.); "where are you from originally" probes; arrest-record questions outside legally permitted contexts.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Kit generator, concrete artifact |
| Scope boundaries | 5/5 | 4 steps, caps on competencies + time |
| Output format guidance | 5/5 | Full kit with cover + scorecard + debrief |
| Reasoning techniques | 5/5 | Competency-question-rubric mapping |
| Safety / refusal patterns | 5/5 | Protected-attribute + stress-interview refusals |
| 2026 tech relevance | 5/5 | Structured interviewing, Google re:Work-aligned |
| License-friendliness | 5/5 | MIT-equivalent, Jarvis-authored |
| **Overall** | **35/35** | Strongest HR prompt; safety patterns are best-in-class |
