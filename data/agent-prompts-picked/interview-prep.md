# Interview Prep — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/interview-prep.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Structured Interview Coach
**From library:** `data/agent-prompts/interview-prep.md` -> Prompt 1
**Source:** [lxfater/Awesome-GPTs — Interview-Coach](https://github.com/lxfater/Awesome-GPTs/blob/main/prompt/Interview-Coach.md)
**Author:** lxfater (curator); attributed to original GPT author
**License:** Repo published openly; treat as permissive-with-attribution reference

### Full Prompt (verbatim)

```
#### GPT Persona: 
- This GPT serves as an interview coach, assisting users by conducting practice interviews and mock interviews. 
- Interview coach leverages best practices when providing feedback such as the STAR method
- Interview coach takes on the persona of the interviewer during the interview
- Interview coach acts as an expert in whatever persona it is emulating
- Interview coach always provided critical feedback in a friendly manner
- Interview coach is concise in it's language 

#### Starting the Conversation Instructions:
To begin the conversation interview will always ask for the following information so it can provide a tailored & personalized experience.  The interview coach will only ask one question at time.
1.  Ask the user to provide their resume by either uploading or pasting the contents into the chat
2. Ask the user to provide the job description or role they are interviewing for by providing uploading or pasting the contents into the chat
3. Ask the user what type of interview it would like to conduct based on the role the user is interviewing for (e.g., behavioral, technical, etc.) 
4. Ask the user for the role of the interviewer (e.g., director of product); if provided act as that role 
5. Ask the user how many questions the user would like to do. Maximum of 10 questions. 
6. Ask for the user for the interview mode: 
- Practice Interview Mode: In practice mode the interview coach will wait for the users response after the question is asked then provide feedback on the users answer. After all questions summarize the feedback. 
- Mock Interview Mode: In mock interview mode the interview coach will ask the user a question, wait for the response, then ask another question. After all questions summarize the interview and provide feedback. 
7. The interview coach will ask one question at a time prior to going to the next question

#### Providing Feedback:
1.  When interview coach provides feedback it always uses best practices based on the role the user is interviewing for 
2. When the interview is over the interview coach always provides detailed feedback. 
3. When applicable the interview coach will provide an example of how the user can reframe the response 
4. When the interview coach provides feedback it always uses a clear structure 
5. When the interview coach provides feedback it will always provide a score from 0 - 10 with rationale for the score
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** Persona explicit (coach + interviewer + role-specialist).
- **Scope boundaries:** Two-mode design (Practice vs Mock), bounded question count (max 10), one-question-at-a-time.
- **Output format:** STAR-method feedback, 0-10 scoring with rationale, optional reframe example. Structured, machine-friendly.
- **Reasoning techniques:** STAR rubric + role-adapted feedback + persona-of-interviewer + Practice mode is Socratic-adjacent (feedback per question, not lecture).
- **Safety / refusal patterns:** "Critical feedback in a friendly manner" + concise language. No harshness escalation.

### 2026 trend relevance
- **Modern frameworks:** STAR is still the 2026 industry standard for behavioral. Practice-vs-Mock distinction matches Pramp / interviewing.io split. Resume + JD intake is the dominant prep pattern.
- **Current tech references:** Vendor-neutral, but recognises interviewer roles (e.g., "director of product").
- **Structured output:** 0-10 score with rationale is machine-aggregable across multiple mocks.
- **Safety alignment:** Friendly-but-critical tone. Aligns with current interview-prep ethics (no fake-out hostile interviewer without consent).

### Pedagogical quality (tutoring-specific)
- **Socratic vs. answer-dumping:** Practice mode is feedback-after-answer (right-for-domain — you can't Socrate someone into a STAR story; you have to coach the iteration). Mock mode simulates real conditions. Provides reframe examples — slightly more directive than pure Socratic, but appropriate for interview coaching.
- **Adapts to student level:** Tailors via resume + JD intake. Interviewer role customizes question depth.
- **Builds understanding vs. dependence:** STAR-trained reflex transfers across roles. End-of-session feedback summary builds the user's self-critique muscle.

### Deployability
- **License:** Repo is openly published; treat as reference with attribution.
- **Vendor lock:** None.
- **Jarvis adaptability:** Pair with Prompt 3 (Technical Coach) for FAANG coding/system design. Pair with Prompt 4 (STAR Story Bank) BEFORE running mocks — story bank first, mock second.

---

## Runners-up + Trade-offs

### #2: STAR Story Bank Builder (Prompt 4)
- **Why not picked:** Story bank is the prep BEFORE mocks. Critical, but earlier in the pipeline. Structured Interview Coach is the workhorse default.
- **When to use this instead:** First session in interview prep — build the 5-7 stories, tagged to competencies, before any mock.

### #3: Technical Interview Coach (Prompt 3)
- **Why not picked:** Excellent for FAANG live-coding / system design / ML system design — but technical-specific. Structured Coach handles behavioral + simpler technical defaults.
- **When to use this instead:** Live-coding mock, system design, ML system design. Especially for senior+ roles.

### #4: Job Interviewer (Prompt 2, awesome-chatgpt-prompts)
- **Why not picked:** Bare-bones, no feedback. Useful as a rep-only session but missing the teaching layer.
- **When to use this instead:** Second/third rep after you've drilled with Prompt 1 — pure pressure simulation with no hints.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/interview-prep.md`
2. **Adaptations needed:**
   - Add Hinglish register and Indian-market interview conventions (NTPC/PSU style, IT services style, product-company style, MBA placements).
   - Add company-router: Amazon -> 16 LP behavioral. Google -> Googleyness + Cognitive + RRK. McKinsey/Bain -> case + PEI. FAANG SWE/ML -> technical (handoff to Prompt 3).
   - Pre-mock check: "Has the user built a STAR story bank yet? If no, handoff to Prompt 4 first."
   - Persist mock transcripts and scores to `data/interviews/{role}/{date}.md` so cross-session improvement is visible.
3. **Tool access (suggested):** File Read (resume + JD), File Write (transcripts + scores). Notion if Boss prefers.
4. **Model recommendation:** sonnet (judgment + persona quality). opus for senior/staff roles where signal evaluation matters.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Persona + dual-mode + interviewer-role customization. |
| Scope boundaries | 5/5 | Two modes, max 10 questions, one-q-at-a-time. |
| Output format guidance | 5/5 | STAR + 0-10 score + reframe example. |
| Reasoning techniques | 4/5 | STAR rubric + persona simulation; less Socratic, more coach-feedback (right for domain). |
| Safety / refusal patterns | 4/5 | Friendly-critical tone. No anti-discrimination / illegal-Q guard (add). |
| 2026 tech relevance | 5/5 | STAR remains canonical; Practice-vs-Mock is industry standard. |
| License-friendliness | 4/5 | Openly-published repo; attribute. |
| **Overall** | **32/35** | |
