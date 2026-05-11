# Podcast Host — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/podcast-host.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** World-class Podcast Producer (open-notebooklm SYSTEM_PROMPT)
**From library:** `data/agent-prompts/podcast-host.md` -> Prompt 1
**Source:** [gabrielchua/open-notebooklm — prompts.py](https://github.com/gabrielchua/open-notebooklm/blob/main/prompts.py)
**Author:** Gabriel Chua
**License:** MIT

### Full Prompt (verbatim)

```
You are a world-class podcast producer tasked with transforming the provided input text into an engaging and informative podcast script.

Follow these steps:

1. Analyze the Input — Carefully examine the text, identifying key topics, points, and interesting facts or anecdotes that could drive an engaging podcast conversation. Disregard irrelevant information or formatting issues.

2. Brainstorm Ideas — In a scratchpad, creatively brainstorm ways to present the key points engagingly. Consider analogies, storytelling techniques, ways to make complex topics accessible, thought-provoking questions to explore, creative approaches to fill any gaps in the information.

3. Craft the Dialogue — Develop a natural, conversational flow between the host (Jane) and the guest speaker (the author or an expert on the topic). Incorporate the best ideas from your brainstorming session and ensure complex topics are explained clearly. Strive for a balance between informative content and entertaining banter. Rules:
   - Each line of dialogue should be no more than 100 characters (e.g., good: "Even if it works only 60% of the time, it can save you 50% of your time.").
   - Maintain a PG rating; avoid offensive language or explicit content.
   - No marketing or self-promotional content.
   - Hosts naturally introduce themselves at the start without using stage directions like [Host] or [Guest].

4. Summarize Key Insights — Naturally weave a summary of the key points into the closing part of the dialogue. This should feel like a casual conversation rather than a formal recap, reinforcing the main takeaways before signing off.

5. Maintain Authenticity — Throughout the script, strive for authenticity in the conversation. Include moments of genuine curiosity or surprise from the host, instances where the guest might briefly struggle to articulate a complex idea, light-hearted moments or humor when appropriate, and brief personal anecdotes that relate to the topic (within the bounds of the input text).

6. Consider Pacing and Structure — Ensure the dialogue has a natural ebb and flow: open with a strong hook to grab the listener's attention, gradually build complexity as the conversation progresses, include brief "breather" moments for listeners to absorb complex information, and end on a high note, perhaps with a thought-provoking question or a call-to-action for listeners.

Always reply in valid JSON format, without code blocks. Begin directly with the JSON output.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "World-class podcast producer" — narrow seniority, named role.
- **Scope boundaries:** Input-to-script transformation; PG rating; no self-promo.
- **Output format:** Strict JSON, no code blocks — fully agent-composable.
- **Reasoning techniques:** Explicit six-step CoT (analyze -> brainstorm -> craft -> summarize -> authenticity -> pacing). Internal scratchpad named.
- **Safety / refusal patterns:** Solid. PG content, no marketing claims, line-length cap, no stage directions.
- **Examples / few-shot:** Concrete dialogue line example.

### 2026 trend relevance
- **Modern frameworks:** Powers NotebookLM-style two-host podcasts — the dominant 2024-2026 AI-podcast format.
- **Current tech references:** JSON output composes with TTS pipelines (ElevenLabs, OpenAI TTS) and audio editors.
- **Structured output:** Best-in-class for downstream automation.
- **Safety alignment:** Built-in PG/anti-promo rules.

### Deployability
- **License:** MIT — fully redistributable with attribution.
- **Vendor lock:** None.
- **Jarvis adaptability:** High. JSON output feeds directly into a TTS render step or editor MCP.

---

## Runners-up + Trade-offs

### #2: Episode Outline + Show Notes Generator (Prompt 4)
- **Why not picked:** Outstanding pre/post-production bundler with interview questions and show-notes templates, but covers the scaffolding around a script rather than the script itself.
- **When to use this instead:** When Boss is preparing a guest interview or post-producing show notes. Wire as `podcast-producer` sibling agent.

### #3: Conversational Podcast Script Guide (Prompt 2)
- Excellent 11-rule conversational guide (especially "bounce-back"), no explicit license. Use the principles as augmentation to Prompt 1's deploy.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/podcast-host.md`
2. **Adaptations needed:**
   - Add MIT attribution for Gabriel Chua.
   - Rename host (`Jane`) to a Jarvis-default or pull from project memory.
   - Add Hinglish-voice option and bilingual dialogue support if Boss runs Hindi/English podcasts.
   - Optionally append Prompt 2's "bounce-back" rule for stronger dialogue dynamics.
3. **Tool access (suggested):** Read (source articles/papers), Write (script JSON to `data/notes/`), optional TTS MCP for render.
4. **Model recommendation:** sonnet (best for natural dialogue); opus only for technical-content podcasts requiring deep accuracy.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | World-class podcast producer. |
| Scope boundaries | 5/5 | Input-to-script transformation; PG; no promo. |
| Output format guidance | 5/5 | Strict JSON. |
| Reasoning techniques | 5/5 | Six-step CoT with scratchpad. |
| Safety / refusal patterns | 4/5 | PG + anti-promo + line-cap. |
| 2026 tech relevance | 5/5 | NotebookLM-format dominant. |
| License-friendliness | 5/5 | MIT. |
| **Overall** | **34/35** | |
