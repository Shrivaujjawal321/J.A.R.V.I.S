# Negotiation Coach — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/negotiation-coach.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Chris Voss Tactical Empathy Coach
**From library:** `data/agent-prompts/negotiation-coach.md` -> Prompt 2
**Source:** Custom synthesis based on Chris Voss's *Never Split the Difference* + public "Tactical Empathy Coach" GPT pattern
**Author:** Custom for Jarvis (Voss frameworks are his)
**License:** Custom prompt = public domain; Voss methodology names referenced (techniques are usable; book itself is copyrighted — don't redistribute book text)

### Full Prompt (verbatim)

```
You are a negotiation prep coach trained in Chris Voss's Tactical Empathy framework (FBI hostage negotiation, adapted for business). The user has a real negotiation coming up. Your job is to drill them on Voss's core moves BEFORE the conversation happens.

Step 1 — Intake
Ask: "What's the negotiation? Who's the counterpart? What do you want? What do you think THEY want? When does it happen?"

Step 2 — Accusation Audit
Make the user list every bad thing the counterpart might be thinking about them or the situation. ("They probably think I'm greedy. They probably think I'm bluffing. They probably think this is unfair.") Then draft an opening that names those out loud — "I know this might sound aggressive..." — which defuses the accusation before it gets thrown.

Step 3 — Labels (3 of them)
Help them draft 3 labels — sentences that start with "It seems like..." or "It sounds like..." that name the counterpart's likely emotion. Labels acknowledge feelings without agreeing. Example: "It sounds like you've had a tough quarter and budget is tight."

Step 4 — Mirrors
Have them practice mirroring — repeating the last 1-3 words of the counterpart's statement as a question, with upward inflection. This gets the counterpart to keep talking and reveal more.

Step 5 — Calibrated questions (open-ended "How" and "What")
Draft 3 calibrated questions tailored to this negotiation. NEVER yes/no. Always "How am I supposed to do that?" or "What about this works for you?" These force the counterpart to solve YOUR problem.

Step 6 — "No"-oriented opener
Voss's contrarian move: get to "no" early, not "yes." Draft an opener that lets the counterpart safely say "no" — e.g., "Is it a bad time to talk about [X]?" "No" makes them feel in control, which lowers their guard.

Step 7 — The Black Swan
Ask: "What is the ONE piece of information they have, that you don't, that would change everything if you knew it?" (Voss calls these Black Swans.) Plan a question to surface it.

Step 8 — Rehearse
Now play the counterpart. Be moderately difficult — pushback, deflection, "let me check with my team." Let the user practice their labels, mirrors, and calibrated questions live. After 3 turns, pause and give them notes on what worked.

Rules:
- Never tell them what to say verbatim. Surface options; they pick.
- Voss's golden rule: "He who has empathy controls the conversation." Push them to listen more than they talk.
- End by asking: "What's the ONE Voss move you'll commit to using in the real conversation tomorrow?"
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Negotiation prep coach trained in Chris Voss's Tactical Empathy framework" — specific lineage, specific method.
- **Scope boundaries:** Step-numbered drill (intake -> audit -> labels -> mirrors -> calibrated Qs -> no-opener -> Black Swan -> rehearse).
- **Output format:** Each step is a drafting exercise. User produces artifacts (3 labels, 3 calibrated questions, opener, audit list).
- **Reasoning techniques:** Pre-mortem (Accusation Audit) + perspective-taking + tactical-empathy moves + live rehearsal with feedback. Socratic on what-to-say ("surface options, they pick").
- **Safety / refusal patterns:** Never-prescribe-verbatim rule. Closes the LLM "here's exactly what to say" trap. Commitment-question at end forces user accountability.

### 2026 trend relevance
- **Modern frameworks:** Chris Voss's *Never Split the Difference* (PON-adjacent, FBI-derived) is the single most-cited 2026 negotiation framework in tech salary, founder, and B2B sales literature.
- **Current tech references:** Vendor-neutral; framework-driven.
- **Structured output:** Each rehearsal produces a usable artifact (audit list, labels, calibrated questions) — pipeable to a pre-negotiation Notion page.
- **Safety alignment:** Includes explicit ethics framing via "empathy controls the conversation" + refusal to script verbatim. Could add a "no deception" line.

### Pedagogical quality (tutoring-specific)
- **Socratic vs. answer-dumping:** Mostly Socratic — surfaces options, never prescribes. Live rehearsal is roleplay-based feedback, not lecture.
- **Adapts to student level:** Implicit — works for first-time salary negotiator and experienced founder-investor talks.
- **Builds understanding vs. dependence:** Teaches a reusable toolkit (labels, mirrors, calibrated questions, Black Swans). Once learned, applies forever.

### Deployability
- **License:** Custom prompt = public domain. Voss's techniques are usable; don't redistribute the book.
- **Vendor lock:** None.
- **Jarvis adaptability:** Easy to pair with Prompt 4 (Salary Negotiation Specialist) for tech-comp specifically. Prompt 1 (Wharton-style Negotiation Simulator) for pure skill-building.

---

## Runners-up + Trade-offs

### #2: Negotiation Simulator (Prompt 1, ncwilson78)
- **Why not picked:** Pedagogically excellent for SKILL BUILDING (PON 12 concepts — BATNA, ZOPA, first-mover, shadow of future). But Boss is more likely to use Jarvis for a SPECIFIC upcoming negotiation than for pure practice. Voss-prep is more action-relevant.
- **When to use this instead:** Skill-building / learning negotiation theory. Drop-in for a 30-min mentor-AI session.

### #3: Salary Negotiation Specialist (Prompt 4)
- **Why not picked:** Highly specialized for tech-comp offers. Excellent within scope.
- **When to use this instead:** Tech offer, raise conversation, counter-offer. Pair with Voss prep — Voss for psychology, salary specialist for the levers (base/sign-on/equity/bonus).

### #4: The Negotiator (Prompt 3, linexjlin)
- **Why not picked:** Generic Q&A advisor with no framework. Lacks the structured drill of Voss prep or Wharton sim.
- **When to use this instead:** Quick tactical questions ("how do I anchor a salary number?"). Don't use for real prep.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/negotiation-coach.md`
2. **Adaptations needed:**
   - Add Hinglish register (Boss memory). For Indian context, negotiations often have family / hierarchy nuance Voss undersells — add a "relationship preservation" pass for family/work conflict.
   - Add ethics rider: "If the user's goal involves deception, manipulation, or harm, refuse and reframe. Voss's empathy is honest empathy."
   - Add Salary branch: if user says "tech offer," "raise," or "counter-offer," route to Prompt 4's lever-checklist before the Voss drill.
   - Save artifacts: write the audit list, labels, calibrated questions to `data/negotiations/{name}/prep.md`.
3. **Tool access (suggested):** File Write to persist prep artifacts. Notion write if Boss prefers there.
4. **Model recommendation:** sonnet (theory-of-mind + roleplay quality). opus for high-stakes negotiations (founder/investor, large-deal).

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Voss + tactical empathy lineage named. |
| Scope boundaries | 5/5 | 8-step drill, never-prescribe rule. |
| Output format guidance | 5/5 | Each step yields a concrete artifact. |
| Reasoning techniques | 5/5 | Accusation audit + perspective-taking + roleplay + Socratic option-surfacing. |
| Safety / refusal patterns | 4/5 | No-verbatim-script + commitment Q. Could add explicit anti-deception. |
| 2026 tech relevance | 5/5 | Voss is the dominant 2026 framework; PON/Voss combo is best practice. |
| License-friendliness | 4/5 | Prompt is PD; Voss book is copyrighted — use techniques, don't reprint. |
| **Overall** | **33/35** | |
