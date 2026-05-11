# Social Media Manager — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 6 candidates in `../agent-prompts/social-media-manager.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Social Media Strategy Skill (platform-by-platform playbook)
**From library:** `data/agent-prompts/social-media-manager.md` -> Prompt 1
**Source:** [thatrebeccarae/claude-marketing — social-media-strategy SKILL.md](https://github.com/thatrebeccarae/claude-marketing/blob/main/skills/social-media-strategy/SKILL.md)
**Author:** Rebecca Rae Barton (GitHub: thatrebeccarae)
**License:** MIT

### Full Prompt (verbatim)

```
---
name: social-media-strategy
description: Platform-specific organic social media strategy, content calendars, engagement tactics, community building, and performance measurement. Use when the user asks about social media strategy, organic social, content calendars, community management, or social media metrics.
license: MIT
origin: custom
author: Rebecca Rae Barton
---

# Social Media Strategy

Platform-specific organic social strategy, calendars, and community building.

## Platform Strategy Matrix

| Platform | Best Audience | Content Style | Post Frequency | Key Metric |
|----------|--------------|--------------|----------------|------------|
| **LinkedIn** | B2B, professionals, recruiters | Thought leadership, case studies, industry insights | 3-5x/week | Engagement rate |
| **Twitter/X** | Tech, media, real-time conversations | Hot takes, threads, commentary, launches | 1-3x/day | Impressions, replies |
| **Instagram** | DTC, lifestyle, visual brands | Reels, carousels, Stories, aesthetic | 3-5x/week + daily Stories | Reach, saves |
| **TikTok** | Gen Z/Millennial, entertainment-first | Short-form video, trends, behind-scenes | 1-3x/day | Views, shares |
| **YouTube** | Long-form education, tutorials | Tutorials, vlogs, podcasts, reviews | 1-2x/week | Watch time, subscribers |
| **Threads** | Text-first, early adopter | Conversational, casual, community | 3-5x/week | Engagement |

## Content Pillar Framework

### 40/25/25/10 Rule

| Pillar | % of Content | Examples |
|--------|-------------|---------|
| **Educational** | 40% | How-tos, tutorials, tips, frameworks, guides |
| **Thought Leadership** | 25% | Opinions, predictions, industry analysis, hot takes |
| **Social Proof** | 25% | Case studies, testimonials, results, behind-the-scenes |
| **Promotional** | 10% | Product launches, offers, CTAs, announcements |

## Platform-Specific Best Practices

### LinkedIn
- Personal profiles outperform company pages 5-10x
- First 2 lines are the hook (before "see more")
- Carousels (PDF documents) get highest reach
- Comment on 10-15 posts before/after publishing for algorithm boost
- Polls get reach but low quality engagement
- Best times: Tue-Thu 8-10am

### Twitter/X
- Threads outperform single tweets for depth
- First tweet must stand alone as a hook
- Quote tweets with added value > plain retweets
- Engage in replies to build visibility
- Trending hashtags only if genuinely relevant
- Best times: Mon-Fri 9am-12pm

### Instagram
- Reels get 2-3x the reach of static posts
- Carousels get highest saves and shares
- Stories for daily engagement and polls
- Use 3-5 hashtags (down from the old 30)
- Collab posts for cross-audience growth
- Best times: Tue-Fri 11am-1pm

## Engagement Tactics

1. **Comment-first strategy** — engage with 10-15 accounts in your niche before posting
2. **Reply to every comment** within first 2 hours (algorithm signal)
3. **Ask questions** — posts ending with questions get 2x comments
4. **Tag and mention** — give credit, tag people you reference
5. **DM engagement** — thoughtful DMs to new followers builds community
6. **User-generated content** — reshare and credit customer/community content

## Metrics and KPIs

| Metric | What It Measures | Good Benchmark |
|--------|-----------------|----------------|
| Engagement rate | Interactions / reach | >3% (LinkedIn), >1% (Instagram) |
| Reach | Unique viewers | Growing month-over-month |
| Impressions | Total views | 5-10x follower count |
| Follower growth | Net new followers | 2-5% monthly growth |
| Click-through rate | Link clicks / impressions | >1% |
| Saves/bookmarks | Content value signal | Growing trend |
| Share rate | Shares / reach | >1% = viral potential |
| Reply rate | Comments / impressions | >0.5% |
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** Implicit via skill frontmatter — narrowly scoped to organic social strategy.
- **Scope boundaries:** Frontmatter `description` defines exact trigger conditions (calendars, community, metrics).
- **Output format:** Three reference tables (platform matrix, pillar rule, KPI table) the model reads as "ground truth."
- **Reasoning techniques:** Forces matrix-lookup before recommendation — model defaults to grounded numbers, not improv.
- **Safety / refusal patterns:** Implicit — KPIs are benchmark, not promise. (Soft on safety; supplement with crisis-response Prompt 6.)
- **Examples / few-shot:** Embedded best-practice bullets per platform act as in-context examples.

### 2026 trend relevance
- **Modern frameworks:** Built as a Claude Code Skill — native to agentic workflows, fits 2026 Claude Code architecture.
- **Current tech references:** Threads, Reels, TikTok, modern hashtag norms (3-5 not 30), comment-first algo strategy.
- **Structured output:** Markdown tables parse to Sheets/Notion for calendar generation.
- **Safety alignment:** Pure-strategy scope avoids autonomous-posting risk.

### Deployability
- **License:** MIT — fully redistributable with attribution.
- **Vendor lock:** None — skill format is open, works in Claude Code / general SDK.
- **Jarvis adaptability:** Highest possible. It IS already a Skill — Boss can drop it in `.claude/skills/` essentially as-is.

---

## Runners-up + Trade-offs

### #2: Multi-Platform Content Repurposer (Prompt 5)
- **Why not picked:** Excellent and CC0, but narrower scope (repurpose-only). For a default social agent, strategy beats repurposing.
- **When to use this instead:** When Boss has one piece of long-form content and needs 5 platform-native variants. Pair as a secondary agent.

### #3: Crisis / Negative-Comment Response Drafter (Prompt 6)
- Outstanding niche tool with strong refusal pattern ("NEVER auto-publish"). Wire as a separate `social-crisis` agent for inbox-style triage.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/social-media-manager.md` (and consider mirroring to `.claude/skills/social-media-strategy/SKILL.md` to honor the skill format).
2. **Adaptations needed:**
   - Add MIT attribution line for Rebecca Rae Barton.
   - Append a Hinglish-voice section + Boss's accounts (when public).
   - Add a "never auto-publish" rule to align with CLAUDE.md safety section.
3. **Tool access (suggested):** Read (memory/voice), Write (calendar drafts to `data/notes/`), optional Notion MCP for content calendar storage.
4. **Model recommendation:** sonnet (best for nuanced platform-native voice); haiku for bulk calendar fill.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 4/5 | Frontmatter-style; clear trigger. |
| Scope boundaries | 5/5 | Description defines exact use cases. |
| Output format guidance | 5/5 | Tables become the model's grounding. |
| Reasoning techniques | 4/5 | Lookup-first against matrices. |
| Safety / refusal patterns | 3/5 | Light; add anti-auto-post rule. |
| 2026 tech relevance | 5/5 | Native Skill format; current platforms. |
| License-friendliness | 5/5 | MIT. |
| **Overall** | **31/35** | |
