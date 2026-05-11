# SEO Specialist — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 7 candidates in `../agent-prompts/seo-specialist.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Topic Cluster / Pillar-Page Planner
**From library:** `data/agent-prompts/seo-specialist.md` -> Prompt 6
**Source:** [HubSpot Topic Cluster model](https://blog.hubspot.com/marketing/topic-clusters-seo) + [dair-ai/Prompt-Engineering-Guide](https://github.com/dair-ai/Prompt-Engineering-Guide)
**Author:** Pattern composed for Jarvis
**License:** CC0

### Full Prompt (verbatim)

```
You are an SEO content strategist building a topic-cluster plan for a website. Output a pillar page + cluster structure optimized for topical authority.

Inputs required (ask if missing):
- Domain and current niche
- Business goal (leads, sales, signups, ad revenue)
- Target audience and their level (beginner / intermediate / expert)
- Geography / language
- Existing top-performing content (URLs) — if any
- Constraint: how many articles total can you commit to in next 90 days?

Output structure:

## Pillar Topic
One-line statement of the topic the site will own.

## Pillar Page
- Title (60 chars max)
- Primary keyword + search volume estimate (mark as `[ESTIMATE]` if not verified)
- Search intent (informational / commercial / transactional)
- Target word count
- 1-paragraph outline summary

## Cluster Pages (8-15)
Table format:
| # | Cluster article title | Primary keyword | Search intent | Internal link to pillar (anchor) | Word count | Priority |

## Internal Linking Map
For each cluster, list 2-4 sibling clusters it should link to. Build a connected graph, not a hub-and-spoke star.

## SERP feature opportunities
For each cluster, note if it has a chance for: Featured Snippet, People Also Ask, Image Pack, Video, Local Pack. Note the structural change needed to win it (e.g., "answer in 40-60 words at the top to win featured snippet").

## 90-day production schedule
Week-by-week plan that builds dependencies: pillar first, then highest-priority clusters, then siblings.

Rules:
- Search volume numbers are estimates unless you have data — label clearly.
- Don't propose more articles than the commitment constraint allows.
- Each cluster must support the pillar — no orphan topics.
- Avoid keyword cannibalization (two pages targeting the same keyword).
- Prioritize commercial / transactional intent for revenue goals; informational for awareness goals.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "SEO content strategist" with explicit goal — topical authority via pillar + cluster.
- **Scope boundaries:** Required inputs include a production capacity constraint, which forces realism.
- **Output format:** Five labeled sections including a tabular cluster map and a calendar schedule — fully structured.
- **Reasoning techniques:** Implicit ordering (pillar before clusters, dependencies in calendar). Search-intent classification per page.
- **Safety / refusal patterns:** `[ESTIMATE]` labeling for volume numbers, anti-cannibalization rule, capacity constraint to prevent over-commitment.
- **Examples / few-shot:** Featured-snippet recipe ("answer in 40-60 words at the top").

### 2026 trend relevance
- **Modern frameworks:** Pillar/cluster architecture is the post-Helpful-Content-Update playbook. Topical authority > single-keyword ranking.
- **Current tech references:** SERP-feature awareness (PAA, Featured Snippet, Image Pack) reflects 2024+ SERP layout.
- **Structured output:** Markdown tables + calendar parse into Notion/Sheets cleanly for content-ops teams.
- **Safety alignment:** Anti-fabrication on search volumes; capacity-aware planning.

### Deployability
- **License:** CC0 — no friction.
- **Vendor lock:** None. Works without proprietary tools but composes well with Search Console / Ahrefs data when piped in.
- **Jarvis adaptability:** High. Chains naturally into content-writer (executes the plan) and technical SEO auditor (Prompt 7).

---

## Runners-up + Trade-offs

### #2: Technical SEO Auditor (Prompt 7)
- **Why not picked:** Excellent and CC0, but narrower scope (technical audits). For an "SEO Specialist" default, strategy-level beats audit-only.
- **When to use this instead:** Site audits, pre-launch QA, migrations, traffic-drop recovery. Pair as a second SEO agent in Jarvis.

### #3: Fully SEO Optimized Article + FAQ (Prompt 1)
- Strong outline-then-article workflow with explicit Rank-Math checklist — but Unknown license, dated "bypass AI detector" framing, and built-in promo footer. Useful concept; not the canonical agent.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/seo-specialist.md`
2. **Adaptations needed:**
   - Add optional WebSearch tool wiring for live SERP intel.
   - Drop hardcoded keyword example; pull niche from project memory.
   - Add a "handoff" clause: emit a JSON plan that `content-writer` can consume per cluster.
3. **Tool access (suggested):** WebSearch / WebFetch (SERP + competitor scan), Read (memory), Write (cluster plan to `data/notes/`).
4. **Model recommendation:** sonnet (best for strategic structured output); opus when site is large / niche is competitive.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Strategist, topical authority goal. |
| Scope boundaries | 5/5 | Required inputs + capacity constraint. |
| Output format guidance | 5/5 | Tables + calendar + linking map. |
| Reasoning techniques | 4/5 | Dependency ordering + intent classification. |
| Safety / refusal patterns | 4/5 | Estimate labels + anti-cannibalization. |
| 2026 tech relevance | 5/5 | Post-HCU pillar/cluster + SERP features. |
| License-friendliness | 5/5 | CC0. |
| **Overall** | **33/35** | |
