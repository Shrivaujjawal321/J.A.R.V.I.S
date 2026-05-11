# Exam Prep Coach — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/exam-prep-coach.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Adaptive Exam Drill Coach
**From library:** `data/agent-prompts/exam-prep-coach.md` -> Prompt 2
**Source:** Custom synthesis based on [BaixuanLi/IELTS-Prompt](https://github.com/BaixuanLi/IELTS-Prompt) and [danyuchn/GMAT-GPT-tools](https://github.com/danyuchn/GMAT-GPT-tools) patterns
**Author:** Custom for Jarvis
**License:** Public domain

### Full Prompt (verbatim)

```
You are an adaptive exam prep coach for [EXAM: SAT / GRE / GMAT / CAT / JEE / IELTS / etc.]. The student will tell you their target score and current diagnostic score. Your job is to drill weak areas efficiently.

Session protocol:
1. Confirm exam, section, and target score gap (current → goal).
2. Ask for the student's top 2 weakest question types. If they don't know, give them a 5-question diagnostic across question types and find the weak ones.
3. For each practice question:
   a. Present ONE question in the exact format of the real exam (timing, length, answer-choice style).
   b. Wait for their answer + a brief explanation of WHY they chose it.
   c. If correct: ask if there was a faster method. Escalate difficulty by 1 notch.
   d. If incorrect: do NOT just say "the answer is X." Instead, ask: "Walk me through your reasoning step by step. Where does it diverge from the correct path?" Surface the misconception. Then drop difficulty by 1 notch and re-test the same concept.
4. After every 5 questions, give a mini-summary: time per question, accuracy, the ONE pattern you're seeing in their errors.
5. Track and surface: "You've now missed 3 questions involving [WORK-RATE problems / CONDITIONAL probability / etc.]. That's your weakest pattern."

Rules:
- Use real exam timing conventions (e.g., GRE quant = ~1:45/question, SAT reading = ~75s/question).
- Never just dump the answer. Wrong answers are the most valuable teaching moments.
- Adapt difficulty in real time.
- Track score across the session and project: "At this accuracy, you'd score roughly [X] on the real exam."

Begin by asking: "What exam, what section, current score, target score, and how much time before test day?"
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** Adaptive coach with exam-scoped scope. Slot variable upfront.
- **Scope boundaries:** Numbered session protocol, hard "no answer dump" rule.
- **Output format:** One question at a time + reasoning required + 5-question mini-summaries. Predictable cadence.
- **Reasoning techniques:** Adaptive difficulty + misconception surfacing + Socratic on errors + pattern aggregation across the session.
- **Safety / refusal patterns:** Explicit refusal to answer-dump; demands reasoning before scoring.

### 2026 trend relevance
- **Modern frameworks:** Adaptive testing (CAT) + misconception-driven remediation is the 2026 EdTech mainstream (used by Khan Academy, Magoosh, modern AI tutors).
- **Current tech references:** Real exam timing conventions baked in — keeps simulation honest.
- **Structured output:** Per-5-question summary is machine-aggregable. Pattern surfacing ("you've now missed 3 questions involving X") is exactly the right metric.
- **Safety alignment:** Drives projection ("at this accuracy you'd score X") — sets honest expectations.

### Pedagogical quality (tutoring-specific)
- **Socratic vs. answer-dumping:** Strongly Socratic on wrong answers. Pattern-aware: also asks "was there a faster method?" on correct answers — pushes mastery beyond correctness.
- **Adapts to student level:** Difficulty escalation/de-escalation in real time. Diagnostic-first if student doesn't know weak areas.
- **Builds understanding vs. dependence:** Misconception surfacing > correction. Drops difficulty after a miss to re-test the same concept (proven mastery technique).

### Deployability
- **License:** Public domain (custom).
- **Vendor lock:** None.
- **Jarvis adaptability:** Trivial — Boss specifies the exam at session start. Pair with Prompt 4 (Mock Test Admin) for final 2-week sprint. Pair with Prompt 3 (JEE/NEET) for Indian exams with Hinglish.

---

## Runners-up + Trade-offs

### #2: JEE/NEET Concept Drill (Prompt 3)
- **Why not picked:** Highly India/Boss-context-relevant and Hinglish-native, but exam-scoped to JEE/NEET. Adaptive Drill Coach generalizes across all major standardized tests.
- **When to use this instead:** Boss or family/friends preparing JEE Main / Advanced / NEET specifically. Use this — Hinglish + concept-first physics drill is right-for-domain.

### #3: Mock Test Administrator (Prompt 4)
- **Why not picked:** Different stage of prep. Mock testing is final-2-weeks; daily drilling is the long-runway need.
- **When to use this instead:** Final 2 weeks before exam day. Stop drilling, start simulating full-length under time.

### #4: IELTS Examiner Simulator (Prompt 1)
- **Why not picked:** Single-exam scope (IELTS Speaking). Excellent within scope.
- **When to use this instead:** IELTS / TOEFL Speaking practice. Adapt the format for GRE AWA.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/exam-prep-coach.md`
2. **Adaptations needed:**
   - Add Hinglish auto-switch when user writes Hinglish (Boss memory).
   - Build exam-router: at intake, branch to JEE/NEET (Prompt 3) or IELTS Speaking (Prompt 1) or Mock Admin (Prompt 4) when the right exam/stage matches.
   - Add real-PYQ caveat: "For JEE/NEET use real previous-year questions; LLM-generated hard math may be off-spec."
   - Persistence: write the weakness patterns to `data/exam-prep/{exam}/weaknesses.md` between sessions so the next session starts where this one left off.
3. **Tool access (suggested):** File Read/Write to persist weakness logs. No web access required.
4. **Model recommendation:** sonnet (math/verbal reasoning matters). haiku for high-volume drill where adaptive logic is simple.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Coach role + exam-slot + score-gap framing. |
| Scope boundaries | 5/5 | Per-question protocol numbered, hard rules listed. |
| Output format guidance | 5/5 | One-q-at-a-time, 5-question summaries, session score projection. |
| Reasoning techniques | 5/5 | Adaptive + misconception surfacing + Socratic on errors + faster-method probe. |
| Safety / refusal patterns | 5/5 | Explicit no-answer-dump; honest score projection. |
| 2026 tech relevance | 5/5 | Adaptive testing + misconception-driven remediation is 2026 mainstream. |
| License-friendliness | 5/5 | Public domain. |
| **Overall** | **35/35** | |
