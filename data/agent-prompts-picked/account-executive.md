# Account Executive — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/account-executive.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Consultative AE Closer (MEDDIC-aware)
**From library:** `data/agent-prompts/account-executive.md` → Prompt 1
**Source:** [Tenbound — ChatGPT Prompts for Salespeople and SDRs](https://tenbound.com/a-collection-of-chatgpt-prompts-for-salespeople-and-sdrs/)
**Author:** Tenbound editorial
**License:** Article content (cite & adapt; not redistributed verbatim wholesale)

### Full Prompt (verbatim)

```
You are a senior B2B Account Executive with 10+ years closing complex SaaS deals.
I will paste deal context below. Your job: produce a MEDDIC scorecard
(Metrics, Economic Buyer, Decision Criteria, Decision Process, Identify Pain,
Champion) for this opportunity. For each letter:
  1. State what we know (verbatim from context).
  2. State what is missing or assumed.
  3. Suggest the single best discovery question to close the gap.
At the end, give: (a) deal score 0–100 with reasoning, (b) the riskiest
unknown, (c) the next best action with a draft Slack/email to my champion.
Be honest. If the deal looks weak, say so — don't flatter.

Deal context:
[PASTE NOTES, CALL TRANSCRIPTS, EMAIL THREADS]
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** Senior-AE persona (10+ years) anchors the model to enterprise-deal heuristics rather than generic sales talk.
- **Scope boundaries:** Single artifact (MEDDIC scorecard) — not a kitchen-sink output.
- **Output format:** Per-letter 3-row structure (know / missing / question) + 3 closing deliverables (score, risk, next action). Highly composable.
- **Reasoning techniques:** Forces gap-analysis reasoning — "what we know vs. what's assumed" is structured CoT lite.
- **Safety / refusal patterns:** Explicit honesty rule ("if the deal looks weak, say so — don't flatter"). Anti-sycophancy.
- **Examples / few-shot:** None, but the 3-row structure per MEDDIC letter is self-documenting.

### 2026 trend relevance
- **Modern frameworks:** MEDDIC is still the dominant enterprise B2B qualification framework in 2026 — no signs of replacement.
- **Current tech references:** Mentions deliverables (Slack/email to champion) that match modern multi-channel deal motion.
- **Structured output:** Scorecard format = LLM-friendly, agent-pipeline-friendly.
- **Safety alignment:** Honesty mandate is the right vibe; doesn't enable pressure tactics.

### Deployability
- **License:** Tenbound article content — citation required; commercial adaptation acceptable.
- **Vendor lock:** None.
- **Jarvis adaptability:** Trivial to wire — Boss pastes deal context, gets actionable scorecard.

---

## Runners-up + Trade-offs

### #2: Mutual Action Plan + Close Plan Drafter (Prompt 4)
- **Why not picked:** Excellent late-stage artifact, but narrower scope — only useful post-demo. Picked Prompt 1 because MEDDIC scorecard is the higher-frequency artifact across deal stages.
- **When to use this instead:** After a strong demo, when prospect asks "what are next steps?"

### #3: Multi-Stakeholder Mapping (Prompt 2)
- **Why not picked:** Strong for enterprise deals with 4+ buyers, but redundant once MEDDIC's Economic Buyer + Champion sections are filled in well.
- **When to use this instead:** Complex deals where Boss only knows one contact — run as a complement.

### #4: Objection-Handling Drill (Prompt 3)
- **Why not picked:** Useful for rep development, not for closing artifacts. More training-tool than agent.
- **When to use this instead:** Night before a tough closing call — roleplay sparring.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/account-executive-agent.md`
2. **Adaptations needed:**
   - Inject MEDDPICC (Paper Process + Competition) for enterprise — current prompt is MEDDIC-only; consider extending.
   - Add Boss-specific deal context loader (current pipeline notes from CRM).
   - Reinforce anti-flattery rule with Jarvis's "honest, never fabricate" directive.
3. **Tool access (suggested):** Read access to deal notes (Notion/Google Drive); no autonomous email-send; optional research-agent for company-level intel.
4. **Model recommendation:** sonnet (good structured reasoning); opus for million-dollar deals where the scorecard accuracy compounds.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Senior-AE with experience anchor |
| Scope boundaries | 5/5 | Single artifact, well-scoped |
| Output format guidance | 5/5 | Per-letter 3-row + 3 closing deliverables |
| Reasoning techniques | 4/5 | Gap-analysis CoT; could add competitor-frame |
| Safety / refusal patterns | 4/5 | Anti-flattery explicit; no fabrication clause though |
| 2026 tech relevance | 5/5 | MEDDIC still dominant; Slack/email channels modern |
| License-friendliness | 4/5 | Cite Tenbound on reuse |
| **Overall** | **32/35** | Strongest closing artifact in the candidate set |
