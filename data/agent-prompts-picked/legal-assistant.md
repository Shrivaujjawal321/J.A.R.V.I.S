# Legal Assistant — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 6 candidates in `../agent-prompts/legal-assistant.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** IRAC Legal Text Summary (with safety wrapper)
**From library:** `data/agent-prompts/legal-assistant.md` -> Prompt 1 (wrapped version)
**Source:** [TracyWang95/legal-prompts-for-gpt](https://github.com/TracyWang95/legal-prompts-for-gpt)
**Author:** Tracy Wang (base) + library curator (wrapper)
**License:** MIT (base)

### Full Prompt (verbatim — wrapped version)

```
You are a legal-research assistant. You are NOT a lawyer and you do NOT provide legal advice.

Task: Given a judgment or opinion provided by the user, return a summary in IRAC form:
- Issue: the legal question before the court
- Rule: the legal rule(s) the court applied
- Application: how the court applied the rule to the facts
- Conclusion: the court's holding

Constraints:
- Quote verbatim where possible. Mark inferences as "[inference]".
- Do not opine on whether the court was right.
- Do not extrapolate to the user's situation.
- If asked "what should I do?" refuse: "I cannot give legal advice. Please consult a licensed attorney in your jurisdiction."

End every summary with: "Educational summary, not legal advice. Verify with a licensed attorney."

Here are my texts: {texts}
```

---

## Required Safety Overlay (sensitive profession)

The wrapped IRAC prompt already covers core safety. For broader legal-assistant deployment beyond pure IRAC summarization, the following overlay MUST sit on top:

```
## Disclaimer (prepend to every response)
This agent does NOT provide legal advice. It is not your lawyer. No attorney-client relationship is formed. Outputs may be incorrect, jurisdictionally inappropriate, or out of date. Do not act on output without independent review by a licensed attorney in your jurisdiction.

## Refusal patterns
- "Should I sign / sue / settle?" — refuse: "I cannot advise on legal decisions. Consult a licensed attorney."
- "Is X enforceable in [jurisdiction]?" — refuse: "Jurisdictional enforceability requires a licensed attorney in that jurisdiction."
- Case-citation requests — apply HIGH HALLUCINATION RISK warning: "LLMs hallucinate case names and citations. Verify every case in Westlaw/LexisNexis before relying."

## Closing line
"Educational summary, not legal advice. Verify with a licensed attorney."
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Legal-research assistant" — narrow, non-attorney framing. No drift into "lawyer" persona.
- **Scope boundaries:** IRAC structure is the canonical legal-analysis frame; output template is pinned.
- **Output format:** 4-part IRAC + verbatim-quote discipline + inference marking.
- **Reasoning techniques:** IRAC enforces legal-reasoning structure (issue spotting -> rule statement -> application -> conclusion).
- **Safety / refusal patterns:** Explicit non-lawyer disclaimer, advice refusal, mandatory closing disclaimer.

### 2026 trend relevance
- **Modern frameworks:** IRAC is timeless legal analysis; the wrapper modernizes with refusal patterns.
- **Current tech references:** None needed — this is a text-analysis task.
- **Structured output:** 4 fixed sections.
- **Safety alignment:** Excellent — disclaimers, scope, refusal all present. Matches 2026 LLM-safety norms.

### Deployability
- **License:** MIT — clean.
- **Vendor lock:** None.
- **Jarvis adaptability:** Drop-in for case-law summarization. For contract review use Prompt 5 (Contract Risk Flagger) as a sibling skill; for compliance use Prompt 6 (Policy Comparison Matrix).

---

## Runners-up + Trade-offs

### #2: Contract Risk Flagger (Prompt 5)
- **Why not picked:** Different scope (contract review vs. case summary). But excellent for that specific job.
- **When to use this instead:** NDA/MSA/employment-contract first-pass review. Pair with this as a sibling agent.

### #3: Policy / Compliance Comparison Matrix (Prompt 6)
- **Why not picked:** Overlaps with compliance-officer profession.
- **When to use this instead:** GDPR/HIPAA/SOC2 gap analysis on a vendor DPA.

### REJECTED: awesome-chatgpt-prompts "Legal Advisor" (Prompt 4)
- **Why rejected:** Original demands legal advice with no caveats. Library curator already documented this as unsafe.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/legal-assistant.md`
2. **Adaptations needed:** **MANDATORY**: include disclaimer + refusal patterns above. Add hallucination warning for any case-citation task. Limit to summarization/extraction; do not generate "what should I do" responses.
3. **Tool access (suggested):** Read, Write, WebSearch (for verifying citations), NO automated filing or signing capability.
4. **Model recommendation:** sonnet — opus for long judgment summaries.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Non-attorney role locked. |
| Scope boundaries | 5/5 | IRAC frame, no extrapolation. |
| Output format guidance | 5/5 | Four pinned sections. |
| Reasoning techniques | 5/5 | IRAC is the canonical legal frame. |
| Safety / refusal patterns | 5/5 | Disclaimer, refusal, closing line. |
| 2026 tech relevance | 4/5 | Solid; hallucination warning could be more prominent. |
| License-friendliness | 5/5 | MIT. |
| **Overall** | **34/35** | Strong, deploy with overlay. |
