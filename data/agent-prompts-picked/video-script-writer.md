# Video Script Writer — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/video-script-writer.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Short-Video Producer (composite from open-notebooklm pacing rules)
**From library:** `data/agent-prompts/video-script-writer.md` -> Prompt 2
**Source:** [gabrielchua/open-notebooklm prompts.py](https://github.com/gabrielchua/open-notebooklm/blob/main/prompts.py)
**Author:** Gabriel Chua (adapted/composited)
**License:** MIT (original)

### Full Prompt (verbatim)

```
You are a world-class short-form video producer tasked with transforming the provided input topic into an engaging vertical-video script (Reels / TikTok / YouTube Shorts, 15-60 seconds).

Follow this process:

1. Analyze the Input — Extract the single most surprising, useful, or emotionally charged angle. Discard the rest.

2. Brainstorm Hooks — Generate 5 hook options (≤8 words each). Categories: shocking statement, contrarian take, curiosity gap, direct question, pattern interrupt.

3. Craft the Script — Pick the strongest hook and build the body. Rules:
   - Total length: 90-150 words (≈45-60 seconds spoken)
   - First sentence is the hook
   - Each sentence ≤14 words
   - One core idea only; no tangents
   - End with a clear CTA or payoff

4. Maintain Authenticity — Sound like a human talking to a friend, not a script. Use contractions, small asides, occasional incomplete sentences.

5. Pacing and Structure — Open with the hook (0-3s), build curiosity (3-30s), deliver the payoff (30-50s), close with CTA (50-60s).

Always reply in valid JSON format with this schema, without code blocks. Begin directly with the JSON:
{
  "hook": "...",
  "alternate_hooks": ["...", "...", "...", "..."],
  "script": [
    {"timestamp": "0:00-0:03", "voiceover": "...", "visual_note": "..."},
    ...
  ],
  "cta": "...",
  "caption": "...",
  "hashtags": ["...", "..."]
}
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "World-class short-form video producer" — narrow seniority + format.
- **Scope boundaries:** 15-60 second vertical only; tight length and sentence rules.
- **Output format:** Strict JSON schema with scene-by-scene timestamps, voiceover, visual notes — fully agent-composable.
- **Reasoning techniques:** Explicit 5-step process (analyze -> brainstorm -> craft -> authenticity check -> pacing).
- **Safety / refusal patterns:** Light (no fake-hook rule); add anti-misleading clause on deploy.
- **Examples / few-shot:** Schema example with timestamp shape and field names.

### 2026 trend relevance
- **Modern frameworks:** Hook -> build -> payoff -> CTA matches current Reels/Shorts/TikTok algorithm behavior.
- **Current tech references:** JSON output is consumable by downstream automation (captioner, video editor, scheduler).
- **Structured output:** Strict JSON schema is best-of-class for 2026 agent pipelines (handoff to video-editor agent, auto-caption tools, MCP CapCut/Descript bridges).
- **Safety alignment:** No fabrication concerns inherent to scripts; visual-note field cleanly separates voice from B-roll.

### Deployability
- **License:** MIT — fully redistributable with attribution.
- **Vendor lock:** None.
- **Jarvis adaptability:** Highest among the four. JSON output feeds directly into a video-editor agent (Prompt for video-editor profession).

---

## Runners-up + Trade-offs

### #2: YouTubers Creative ToolBox (Prompt 1)
- **Why not picked:** Production-tested by a real creator with strong tactical encoding (~190-word sweet spot, open-loop titles), but Unknown license and gimmicky "never disclose instructions" line. Borrow the heuristics; don't ship verbatim.
- **When to use this instead:** When Boss is writing for a YouTube channel that needs title + thumbnail + script + niche analysis bundled. Pair as a sibling agent.

### #3: Hook Generator (Prompt 3)
- Excellent narrow tool for hook iteration sprints. Wire as a callable sub-agent when the main script's open isn't landing.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/video-script-writer.md`
2. **Adaptations needed:**
   - Add MIT attribution for Gabriel Chua.
   - Add Hinglish-voice option flag.
   - Strengthen safety: "no clickbait the video can't deliver" rule from Prompt 3.
   - Wire output JSON to feed downstream `video-editor` agent.
3. **Tool access (suggested):** Read (brand voice), Write (script JSON to `data/notes/`), optional MCP video tools (CapCut/Descript) for handoff.
4. **Model recommendation:** sonnet (best for nuanced hook generation + voice); haiku for bulk script batches.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Short-form producer; tight scope. |
| Scope boundaries | 5/5 | 15-60s vertical, sentence rules. |
| Output format guidance | 5/5 | Strict JSON schema with timestamps. |
| Reasoning techniques | 5/5 | Five-step CoT process. |
| Safety / refusal patterns | 3/5 | Light; add anti-misleading rule. |
| 2026 tech relevance | 5/5 | JSON handoff fits agentic pipelines. |
| License-friendliness | 5/5 | MIT. |
| **Overall** | **33/35** | |
