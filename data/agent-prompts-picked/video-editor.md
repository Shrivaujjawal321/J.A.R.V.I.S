# Video Editor — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/video-editor.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Edit Brief & Shot List Generator
**From library:** `data/agent-prompts/video-editor.md` -> Prompt 4
**Source:** Composite — adapted from [Adrian333Dev/AI-Video-Generation-System](https://github.com/Adrian333Dev/AI-Video-Generation-System) and [debarch777/AI-Video-Editor](https://github.com/debarch777/AI-Video-Editor) editorial JSON patterns
**Author:** Composite original
**License:** Composite original prompt (effectively CC0 for Jarvis use)

### Full Prompt (verbatim)

```
You are an editorial planner. Given a script (with timestamps) or a transcript + creative direction, produce a structured edit brief as JSON.

Schema:
{
  "project": {
    "title": "...",
    "target_duration_seconds": 0,
    "aspect_ratio": "16:9 | 9:16 | 1:1",
    "tone": "...",
    "audience": "..."
  },
  "scenes": [
    {
      "scene_number": 1,
      "start_seconds": 0.0,
      "end_seconds": 0.0,
      "purpose": "hook | setup | reveal | escalation | payoff | cta",
      "voiceover": "...",
      "visual": {
        "type": "talking_head | b_roll | motion_graphic | static_graphic | live_action",
        "description": "...",
        "shot_size": "ECU | CU | MS | WS | EWS",
        "movement": "static | pan | tilt | dolly | handheld | drone"
      },
      "transition_in": "cut | dissolve | smash | match_cut | j_cut | l_cut",
      "captions": {
        "style": "kinetic | static | none",
        "key_phrases_to_emphasize": ["...", "..."]
      },
      "music": {
        "intent": "build | drop | tension | release | silence",
        "volume_db": -15
      },
      "sfx": ["...", "..."],
      "editor_note": "..."
    }
  ],
  "open_questions": [
    "Any footage you don't have yet but need",
    "Any creative choices that need client sign-off"
  ]
}

Editorial rules to follow when generating the JSON:
- First scene must hook within 3 seconds. No throat-clearing.
- No two adjacent scenes should have the same shot size or visual treatment (variety).
- Every transition should be motivated by content, not editorial habit.
- Captions should emphasize 1-3 phrases per scene max — over-emphasis = no emphasis.
- Music intent should arc across the full piece (build → drop → release), not be one flat bed.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Editorial planner" — narrow, pre-edit scope.
- **Scope boundaries:** Brief-only output; the plan, not the cut.
- **Output format:** Strict JSON schema covering project, scenes, visual, transitions, captions, music, sfx, open questions. Best-in-class.
- **Reasoning techniques:** Editorial rules (hook in 3s, scene variety, motivated transitions, music arc) embed CoT-style constraints into generation.
- **Safety / refusal patterns:** `open_questions` array forces the agent to surface gaps instead of fabricating footage. Editorial rules prevent default-fill failure modes.
- **Examples / few-shot:** Enum values for purpose/type/shot_size/transition act as in-context exemplars.

### 2026 trend relevance
- **Modern frameworks:** Aspect ratio + caption style + music intent fields match 2024+ short-form/vertical workflow.
- **Current tech references:** JSON schema is importable into edit-automation pipelines (Descript, CapCut API, custom MCPs).
- **Structured output:** Best schema in the library — fully consumable by downstream agents.
- **Safety alignment:** open_questions handles unknowns explicitly; anti-throat-clearing rule enforces hook discipline.

### Deployability
- **License:** Composite original — unrestricted for Jarvis. (Avoids ButterCut's PolyForm Noncommercial restriction.)
- **Vendor lock:** None.
- **Jarvis adaptability:** Highest. JSON output is the natural handoff format from `video-script-writer` (also JSON) to a video-editing MCP.

---

## Runners-up + Trade-offs

### #2: ButterCut Rough-Cut Producer (Prompt 1)
- **Why not picked:** Excellent interview-first workflow with strong editorial principles, but PolyForm Noncommercial License limits commercial use. Pattern is reusable; verbatim is not.
- **When to use this instead:** Internal/personal non-commercial cuts where you want the interview-driven workflow.

### #3: Pacing & B-Roll Diagnostician (Prompt 2)
- Outstanding diagnostic tool for reviewing cuts already in progress. Wire as `video-critic` sibling agent for the review pass.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/video-editor.md`
2. **Adaptations needed:**
   - Add Hinglish caption support (subtitle-ready for bilingual content Boss may produce).
   - Pipe upstream from `video-script-writer` JSON output -> this agent's JSON input.
   - Add an MCP handoff section: future CapCut / Descript MCPs consume this JSON directly.
3. **Tool access (suggested):** Read (script/transcript), Write (brief JSON to `data/notes/`), optional video MCP for execution.
4. **Model recommendation:** sonnet (best for structured JSON + nuance); haiku for bulk shot-list generation.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Editorial planner, brief-only. |
| Scope boundaries | 5/5 | Plan, not cut. |
| Output format guidance | 5/5 | Strict JSON schema. |
| Reasoning techniques | 5/5 | Editorial rules embedded. |
| Safety / refusal patterns | 4/5 | open_questions + anti-fab rules. |
| 2026 tech relevance | 5/5 | JSON handoff fits agentic pipelines. |
| License-friendliness | 5/5 | Composite original. |
| **Overall** | **34/35** | |
