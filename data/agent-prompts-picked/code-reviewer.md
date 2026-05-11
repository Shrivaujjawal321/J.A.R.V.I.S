# Code Reviewer — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 6 candidates in `../agent-prompts/code-reviewer.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Anthropic Cookbook PR Reviewer (structured XML rubric)
**From library:** `data/agent-prompts/code-reviewer.md` -> Prompt 5
**Source:** [anthropics/anthropic-cookbook](https://github.com/anthropics/anthropic-cookbook)
**Author:** Anthropic team (cookbook examples)
**License:** MIT

### Full Prompt (verbatim)

```
You are an expert code reviewer performing a thorough review of a pull request.

<review_criteria>
1. Correctness — logic errors, off-by-one, null hazards, race conditions, edge cases.
2. Security — injection, XSS, unsafe deserialization, secrets, missing authz, unsafe regex, SSRF.
3. Performance — quadratic loops, N+1 queries, missing pagination, missing indexes.
4. Maintainability — unclear naming, dead code, magic numbers, duplicated logic.
5. Tests — coverage, determinism, meaningful assertions.
6. Style — convention violations, formatter, import order.
</review_criteria>

<output_format>
For each finding:
**[SEVERITY]** `path/to/file.ext:line` — One-sentence summary
> Explanation: impact.
> Suggested fix: concrete change.

SEVERITY: BLOCKER / MAJOR / MINOR / NIT.
End with Overall Recommendation: APPROVE / REQUEST_CHANGES / COMMENT.
</output_format>

<rules>
- Only flag things in the diff (or directly affected by it).
- Do not fabricate file paths or line numbers.
- If uncertain, label MINOR and frame as a question.
- Do not lecture about general best practices unless tied to a specific line.
- Stay within the diff. No unrelated refactors.
</rules>
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** Single line, unambiguous — "expert code reviewer performing a thorough review of a pull request."
- **Scope boundaries:** Explicit rules — "stay within the diff," "do not fabricate file paths," "do not lecture about general best practices unless tied to a specific line." Surgical.
- **Output format:** Pinned hard — `[SEVERITY]` `path:line` — summary -> impact -> fix. Plus SEVERITY enum (BLOCKER/MAJOR/MINOR/NIT) and APPROVE/REQUEST_CHANGES/COMMENT recommendation. Parseable into a CI bot.
- **Reasoning techniques:** Implicit per-criterion walk (correctness -> security -> perf -> maintainability -> tests -> style). 6-dimension forcing function prevents shallow review.
- **Safety / refusal patterns:** "If uncertain, label MINOR and frame as a question" — refuses confident hallucination. "Do not fabricate file paths or line numbers" — explicit anti-hallucination.
- **Examples / few-shot:** Implicit through the SEVERITY enum and rubric.

### 2026 trend relevance
- **Modern frameworks:** XML-tagged sections (`<review_criteria>`, `<output_format>`, `<rules>`) — Claude-native; works on all 2026 Anthropic models.
- **Current tech references:** Security criteria cover modern attack surfaces (SSRF, unsafe deserialization, regex DOS). Performance covers N+1 queries (ORM-era concern).
- **Structured output:** SEVERITY enum + APPROVE/REQUEST_CHANGES/COMMENT = chainable with a PR-bot or merge-gate subagent.
- **Safety alignment:** Anti-hallucination rules are gold-standard 2026 prompt-engineering.

### Deployability
- **License:** MIT (Anthropic Cookbook) — full reuse. No proprietary baggage.
- **Vendor lock:** Claude-tuned (XML tags work best with Claude) but portable to GPT/Gemini with minor adjustments.
- **Jarvis adaptability:** Drop-in. Pair with Git diff input (e.g., `git diff main...HEAD`) via Bash tool.

---

## Runners-up + Trade-offs

### #2: Roo Code Reviewer Mode (Prompt 6, Apache-2.0)
- **Why not picked:** Also excellent — strict read-only review mode, no-edit policy, specific suggested-fix phrasing. Slightly less structured output than Anthropic's XML rubric.
- **When to use this instead:** When running review as a dedicated step in a multi-agent dev pipeline where review-vs-fix separation matters.

### #3: Devin Truthful & Transparent (Prompt 3)
- **Why not picked:** Proprietary-leaked. The "Truthful and Transparent" rules ("don't create fake sample data," "don't pretend broken code is working") are gold but designed for a coder, not a reviewer. Best harvested as additional rules atop Prompt 5.
- **When to use this instead:** Layer the Truthful/Transparent rules INTO the Anthropic prompt to harden against AI-reviewer failure modes (hallucinated bugs, made-up fixes).

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/code-reviewer.md`
2. **Adaptations needed:**
   - Keep verbatim — it's already production-ready.
   - Optionally append the Devin "Truthful and Transparent" rules (from Prompt 3) as an additional `<truthfulness>` section.
   - Add a Jarvis preamble: "Boss is the senior dev — give honest, specific feedback. Hinglish OK if Boss is writing Hinglish."
3. **Tool access (suggested):** Read, Grep, Glob, Bash (for `git diff`). NO Write/Edit — review is read-only.
4. **Model recommendation:** opus — security/correctness reasoning is high-stakes; the marginal cost is worth it. Drop to sonnet for trivial style/lint reviews.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | One line, unambiguous. |
| Scope boundaries | 5/5 | "Stay within the diff" + "don't fabricate" rules. |
| Output format guidance | 5/5 | SEVERITY enum + line-anchored findings = parseable. |
| Reasoning techniques | 4/5 | Implicit 6-dimension walk; could add explicit CoT. |
| Safety / refusal patterns | 5/5 | "If uncertain, label MINOR and frame as a question." |
| 2026 tech relevance | 5/5 | Modern attack surfaces + XML-tag structure. |
| License-friendliness | 5/5 | MIT — drop-in commercial-safe. |
| **Overall** | **34/35** | |
