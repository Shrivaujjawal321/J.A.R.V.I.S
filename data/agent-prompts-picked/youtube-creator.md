# YouTube Creator — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/youtube-creator.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Long-Form Hook + Chapter Architect
**From library:** `data/agent-prompts/youtube-creator.md` -> Prompt 2
**Source:** Composite — structure adapted from [Anthropic Prompt Library Storytelling Sidekick](https://docs.anthropic.com/en/prompt-library/storytelling-sidekick) and community retention frameworks
**Author:** Composited from Anthropic public prompt library + community heuristics
**License:** Anthropic prompt library is published for public reference/use; composite framing original

### Full Prompt (verbatim)

```
You are a long-form YouTube scriptwriter specializing in 8-20 minute educational and essay-style videos. You optimize for audience retention, not pure information density.

When given a topic, produce a script with these mandatory components:

1. COLD OPEN (0:00-0:15) — Pattern interrupt: a shocking statistic, vivid image, contrarian claim, or open question that makes closing the tab feel like a loss. Never start with "Hi guys, welcome to my channel."

2. PROMISE (0:15-0:45) — Tell viewers exactly what they will learn or feel by the end. State the payoff.

3. CHAPTER STRUCTURE — Break the body into 3-5 chapters, each with:
   - A mini-hook at the start (a question, a stake, a curiosity gap)
   - Core content (the actual teaching)
   - A bridge sentence that pulls into the next chapter

4. MID-VIDEO RE-HOOK — At roughly the 50% mark, include an unexpected twist, reveal, or "but wait" moment that reframes everything before it.

5. PAYOFF — Deliver on the promise from step 2 explicitly. The viewer should feel the loop closed.

6. CTA — One clear ask (subscribe, watch next, comment). Never stack multiple CTAs.

Output format:
- Title (3 options, each ≤60 characters, open-loop style)
- Thumbnail concept (2 options, described visually)
- Chapter timestamps (YouTube chapter format)
- Full script with [B-ROLL] and [CUT] annotations
- Pinned-comment prompt to seed discussion
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Long-form YouTube scriptwriter, 8-20 minute educational/essay" — narrow seniority + format + length.
- **Scope boundaries:** Exactly six mandatory structural components; specific timestamps for cold open and promise.
- **Output format:** Pinned: 3 titles, 2 thumbnail concepts, chapter timestamps, full script with B-ROLL/CUT, pinned-comment seed.
- **Reasoning techniques:** Sequential beats (cold open -> promise -> chapters -> re-hook -> payoff -> CTA) act as built-in CoT.
- **Safety / refusal patterns:** "Never start with Hi guys" + "never stack CTAs" function as anti-patterns. Light on misleading-content guard — add on deploy.
- **Examples / few-shot:** Inline anti-pattern example, B-ROLL annotation convention.

### 2026 trend relevance
- **Modern frameworks:** Re-hook at 50% mark and chapter mini-hooks match how Veritasium, Kurzgesagt, Wendover, and modern educational channels are scripted in 2024-2026.
- **Current tech references:** YouTube chapter timestamp format is current platform feature.
- **Structured output:** Title-thumbnail-timestamp-script-pinned bundle composes downstream with a video-editor agent and a YouTube uploader MCP.
- **Safety alignment:** Optimizes for retention without crossing into deceptive clickbait (the cold-open rule mandates a real interrupt, not a lie).

### Deployability
- **License:** Anthropic Prompt Library is published for public reference and use; composite framing is original. Practically usable.
- **Vendor lock:** None.
- **Jarvis adaptability:** High. Composes with video-script-writer (short repurposing) and graphic-designer (thumbnail generation) agents.

---

## Runners-up + Trade-offs

### #2: YouTube Title + Thumbnail Co-Pilot (Prompt 4)
- **Why not picked:** Strong pre-production tool with 10 title angles + 3 thumbnail concepts + CTR prediction, but covers only the pre-script step. Use as a pre-pass.
- **When to use this instead:** Brainstorming title + thumbnail before committing to a script. Pair as `youtube-pre-production` agent.

### #3: YouTubers Creative ToolBox (Prompt 1)
- Production-tested by a working creator, but Unknown license, gimmicky "never disclose instructions" line, and shorts-leaning. Useful as a niche/channel-name brainstorming sibling agent.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/youtube-creator.md`
2. **Adaptations needed:**
   - Add anti-misleading-hook rule from Prompt 4 ("no clickbait the video can't deliver").
   - Add channel-voice slot pulled from `data/memory/preferences.md`.
   - Optional: inject Boss's niche (currently AI/ML/hackathons-related) when relevant.
3. **Tool access (suggested):** Read (memory), Write (script to `data/notes/`), optional WebSearch for current SERP/competitor titles in niche.
4. **Model recommendation:** sonnet (best for long-form retention pacing); opus for video-essay-quality scripts.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Long-form, educational/essay, 8-20 min. |
| Scope boundaries | 5/5 | Six mandatory components with timing. |
| Output format guidance | 5/5 | Titles + thumbnails + chapters + script + pinned. |
| Reasoning techniques | 5/5 | Built-in retention CoT via beats. |
| Safety / refusal patterns | 3/5 | Anti-patterns named; add anti-clickbait. |
| 2026 tech relevance | 5/5 | Re-hook + chapter beats match 2026 channels. |
| License-friendliness | 4/5 | Anthropic public reference; safe to use, attribution courteous. |
| **Overall** | **32/35** | |
