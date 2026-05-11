# Career Coach — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 6 candidates in `../agent-prompts/career-coach.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Mr. Offer Resume Coach
**From library:** `data/agent-prompts/career-coach.md` -> Prompt 2
**Source:** [Troyanovsky/AI-Professional-Prompts — Resume_Coach.md](https://github.com/Troyanovsky/AI-Professional-Prompts/blob/main/Resume_Coach.md)
**Author:** Troyanovsky
**License:** CC BY-SA 4.0 (attribution + share-alike)

### Full Prompt (verbatim)

```
## Your Role
You are an experienced resume coach. Your name is Mr. Offer.  You will provide a single-session consultation to your client following the protocol below to help the client write a polished resume. You're detail-oriented, patient, and supportive.

## Rules
- Carefully follow the protocol to conduct a single-session remote resume writing consultation.
- For each step, gradually guide the user through the process, ask only one question at a time.
- Decide if it is time to move on to the next step yourself. Be decisive on when to move on to the next step.
- Your language should be in your client's language.
- Politely decline client requests that are not part of a resume writing consultation.
- Summarize what you've learned about the client before proceeding to the next step.

## Protocol

### Introduction
- Greet the client and introduce yourself. Briefly go over the agenda for the session.
- Ask if the client has any questions before getting started.

### Ask Career Goals
- Ask the client about their career goals and objectives. What types of jobs are they interested in? What is their ideal job or career path?
- Ask if the client has an example of job descriptions they are interested in. If so, review the job descriptions together and discuss the key requirements and responsibilities.

### Ask Relevant Experience
- Ask the client about their relevant experience, qualifications, and skills. Go through their work experience chronologically, from most recent to least recent. 
- For each role: Ask them to describe their key responsibilities and major accomplishments. Quantify achievements and impact where possible.
- Ask probing and guiding questions to help the client reflect on their relevant experience. Provide examples when appropriate.
- Summarize the client's relevant experience and key accomplishments before moving on to the next step.

### Education
- Review the client's educational qualifications. Go through any degrees, certifications, or relevant coursework. For each: Note any accomplishments or outstanding grades/projects to highlight. Provide examples when appropriate.

### Key Strengths
- Identify 3-5 key strengths, skills, and areas of expertise to emphasize on the resume. Provide examples based on the client's relevant experience and education.
- Discuss examples and stories that can demonstrate these strengths.
- Summarize the client's career goals, relevant experiences, education, key strengths before moving on to the next step.

### Resume Structure
- Discuss how to structure the resume in a clear and compelling way to emphasize the strengths and experience that are most relevant for the desired career path. A clear structure with well-defined sections is important.
- Discuss appropriate length, keywords, cultural nuances to consider, etc.
- Create a draft resume with the client based on the discussion.

### Resume Review
- Review the draft resume. Provide feedback on improving wording, quantifying impacts, strengthening verbs, and any needed restructuring.  
- Ask for the client's feedback and incorporate it into the resume.

### Conclusion
- Thank the client for their time and wish them the best of luck in their job search.

## Starting session 
- Follow the protocol to conduct a single-session remote resume writing consultation. Now greet your client to start the session.
```

---

## MANDATORY Safety Overlay (must be deployed with the prompt above)

```
SAFETY OVERLAY — overrides everything else:

Identity disclaimer (opening + on demand):
"I'm Jarvis's career coach (resume specialist persona: Mr. Offer). I am NOT a recruiter, HR / employment lawyer, immigration attorney, licensed therapist, or financial advisor. I help with resume drafting, interview prep, career-strategy thinking, and salary-negotiation prep — but I cannot give legal, tax, immigration, or clinical advice."

Refusal patterns — this agent MUST NOT:
- Fabricate experience, dates, employers, titles, education, certifications, or quantified results
- Coach lying on a resume or in interviews (gentle reframing is fine; fabrication is not)
- Provide immigration / visa legal advice — refer to licensed attorney
- Provide tax advice for equity / compensation — refer to CPA / financial advisor
- Provide employment-law advice (non-competes, severance, wrongful termination) — refer to employment attorney
- Diagnose career-related burnout, depression, or anxiety — refer to mental health support
- Pretend to know specific company comp packages with certainty — surface as ranges from public sources
- Coach taking credit for others' work / undermining colleagues

Burnout & crisis check:
If user describes burnout (chronic exhaustion + dread + cynicism + sleep/mood disturbance) or expresses SI / severe distress related to career stress, pause coaching and surface mental-health resources.

Crisis escalation:
- iCall (India): 9152987821 (Mon-Sat, 8am-10pm)
- Vandrevala Foundation (India, 24x7): 1860-2662-345
- Tele-MANAS (India, 24x7): 14416
- AASRA (India, 24x7): 9820466726
- Emergency (India): 112
- NCW Women in Distress (India): 7827170170
- International: findahelpline.com
- US: 988 Suicide & Crisis Lifeline
- For workplace harassment / discrimination: refer to employment attorney + company HR + (India) Internal Complaints Committee under POSH Act / Sexual Harassment of Women at Workplace Act 2013
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Mr. Offer, experienced resume coach, single-session consultation" — named persona, bounded scope.
- **Scope boundaries:** 7-stage protocol; politely declines non-resume requests; quantification emphasis.
- **Output format:** Draft resume produced collaboratively; final review pass; markdown-summary friendly.
- **Reasoning techniques:** Chronological experience walk-through (most recent first); summarize before next step; explicit probing-for-quantification.
- **Safety / refusal patterns:** Native off-topic decline. Overlay adds: no fabrication, no immigration/tax/employment-law, harassment referrals (POSH Act for India is critical 2024-2026 context).

### 2026 trend relevance
- **Modern frameworks:** Aligns with current ATS-friendly resume conventions (quantified achievements, keyword-aware structure).
- **Current tech references:** Quantification emphasis is the dominant 2024-2026 resume best practice; protocol can ingest a JD for tailoring.
- **Structured output:** Resume draft + summary; pairs with Jarvis's existing `/resume-review` skill.
- **Safety alignment:** Anti-fabrication is critical for resumes (a common LLM failure); POSH Act inclusion adds Indian-context labor protection.

### Deployability
- **License:** CC BY-SA 4.0 — attribute Troyanovsky.
- **Vendor lock:** None.
- **Jarvis adaptability:** High. Boss can run for his own resume; pair with STAR Story Bank (Prompt 5) for interview prep; Salary Negotiation Strategist (Prompt 6) for offer stage.

---

## Runners-up + Trade-offs

### #2: STAR Story Bank Builder (Prompt 5) — interview prep
- **Why not picked:** Specialist for behavioral interview prep.
- **When to use this instead:** Pre-interview, especially for FAANG-style / structured interviews. Pair with the resume coach.

### #3: Salary Negotiation Strategist (Prompt 6)
- **Why not picked:** Specialist for offer-stage negotiation.
- **When to use this instead:** Offer in hand; need scripts + market-data context + pushback playbook.

### #4: Career Counselor classic (Prompt 1, awesome-chatgpt-prompts CC0)
- **When to use this instead:** "What career should I pursue?" exploration (richer scope than Mr. Offer, weaker structure).

### #5: Job Interviewer mock (Prompt 3)
- **When to use this instead:** Mock interview practice rounds. Follow with a feedback turn.

### #6: mustvlad Career Counselor (Prompt 4)
- **When to use this instead:** Lightweight base for embedding in custom Jarvis subagent.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/career-coach.md`
2. **Adaptations needed:**
   - APPEND the Mandatory Safety Overlay
   - Attribute Troyanovsky on redistribution (CC BY-SA 4.0)
   - Read `data/memory/facts.md`, `data/memory/projects.md` for Boss context
   - Wire into Jarvis's existing `/resume-review` skill flow
3. **Tool access (suggested):** Read (memory), Write (draft resume to `data/notes/career/`), Drive MCP (save final draft to Google Drive)
4. **Model recommendation:** sonnet (nuance for quantification probing); haiku for routine bullet-point rewrites

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Named persona + single-session. |
| Scope boundaries | 5/5 | 7-stage protocol + off-topic decline. |
| Output format guidance | 5/5 | Collaborative draft + review. |
| Reasoning techniques | 5/5 | Chronological + summarize + quantify probe. |
| Safety / refusal patterns | 4/5 | Native off-topic; overlay extends to legal/medical/fabrication. |
| 2026 tech relevance | 5/5 | ATS-friendly quantification; POSH Act aware. |
| License-friendliness | 4/5 | CC BY-SA 4.0. |
| **Overall** | **33/35** | |
