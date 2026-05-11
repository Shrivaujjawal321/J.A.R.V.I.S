# Growth Hacker — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 5 candidates in `../agent-prompts/growth-hacker.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Funnel Drop-off Audit
**From library:** `data/agent-prompts/growth-hacker.md` → Prompt 2
**Source:** [Reforge / growth community summaries](https://www.reforge.com/blog)
**Author:** Community-curated (adapted)
**License:** Adapted from public content

### Full Prompt (verbatim)

```
You are a conversion rate optimisation specialist. I will paste a funnel:
ordered steps with their conversion rates and (optionally) absolute volumes
and revenue per converted user.

For each step, output:
  - Drop-off % (absolute and relative to prior step)
  - Benchmark for similar products (state your reasoning, even if rough)
  - Likelihood this step is the bottleneck (low / med / high) and why

Then identify:
  1. The biggest absolute drop (where most users vanish)
  2. The biggest relative drop (where the funnel is most "broken")
  3. The drop with the highest *revenue* impact if fixed
  4. Pick ONE step to attack first and justify the choice in 3 sentences

Finally: propose 5 experiments specifically for that step, ranked by ICE.

Funnel:
[PASTE]
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** CRO specialist — focused, single-discipline framing.
- **Scope boundaries:** Per-step structure + 4 identification steps + 5 ranked experiments.
- **Output format:** Step-by-step analysis → bottleneck pick → ICE-ranked experiments.
- **Reasoning techniques:** Forces multi-dimensional analysis (absolute / relative / revenue impact) — prevents myopic "fix the biggest %" thinking.
- **Safety / refusal patterns:** Implicit — no dark patterns in the prompt itself. Library-level guardrail rejects dark patterns globally (forced subscriptions, fake scarcity, etc.).
- **Examples / few-shot:** None inline; analytical schema is clear.

### 2026 trend relevance
- **Modern frameworks:** Funnel-audit methodology + ICE scoring is the standard growth-team operating loop.
- **Current tech references:** Revenue-weighted prioritization matches modern PLG/usage-based pricing thinking.
- **Structured output:** Table-friendly, dashboard-pasteable.
- **Safety alignment:** Library's anti-dark-pattern guardrail aligns with Boss's ethical-growth preferences.

### Deployability
- **License:** Reforge-style community content, adapted — cite, free for use.
- **Vendor lock:** None.
- **Jarvis adaptability:** Pairs naturally with research-agent for benchmark verification.

---

## Runners-up + Trade-offs

### #2: AARRR Funnel Strategist (Prompt 1)
- **Why not picked:** Excellent top-down diagnostic but produces 15 experiments — heavier than the focused 5 in Prompt 2. Less actionable per session.
- **When to use this instead:** Boss inherits a product and needs full-funnel diagnosis.

### #3: Experiment Idea Machine (Prompt 3)
- **Why not picked:** Volume tool (20 hypotheses); useful for backlog filling but not the highest-leverage diagnostic.
- **When to use this instead:** Quarterly planning when the experiment pipeline is dry.

### #4: Viral Loop Architect (Prompt 4)
- **Why not picked:** Specialized for products with natural network effects; not applicable everywhere.
- **When to use this instead:** Products with collaboration/sharing surface (docs, marketplaces).

### #5: Experiment Post-Mortem Writer (Prompt 5)
- **Why not picked:** Post-experiment artifact, narrower scope.
- **When to use this instead:** After every completed experiment.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/growth-hacker-agent.md`
2. **Adaptations needed:**
   - Inherit library-level ethical guardrail: REJECT prompts that propose dark patterns (forced subscriptions, hidden unsubscribe, fake FOMO timers, fake social proof). Bake this refusal into the agent's system prompt.
   - Wire research-agent for benchmark data verification.
3. **Tool access (suggested):** Read access to analytics; research-agent for benchmark verification; no autonomous experiment-launching.
4. **Model recommendation:** sonnet (numeric reasoning + structured output).

### Ethics note (sales/growth-specific)
This is one of two profession winners where the library-level ethical guardrail was a deciding factor. The funnel-audit prompt itself is neutral; what makes it Jarvis-safe is the explicit anti-dark-pattern rule (from the library header) carried forward. When adapting, do NOT relax this for "aggressive growth" scenarios — short-term LTV math always loses to brand trust over the long run.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | CRO specialist, focused |
| Scope boundaries | 5/5 | Per-step + 4 pivots + 5 experiments |
| Output format guidance | 5/5 | Table-friendly schema |
| Reasoning techniques | 5/5 | Multi-dimensional (absolute/relative/revenue) |
| Safety / refusal patterns | 4/5 | Implicit; library-level dark-pattern guardrail |
| 2026 tech relevance | 5/5 | ICE scoring + revenue-weighted thinking |
| License-friendliness | 4/5 | Adapted from public community content |
| **Overall** | **33/35** | Highest-leverage growth diagnostic |
