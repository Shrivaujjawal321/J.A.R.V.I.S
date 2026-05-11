# Graphic Designer — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/graphic-designer.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Mini-Brief Designer (DesignRush framework)
**From library:** `data/agent-prompts/graphic-designer.md` -> Prompt 2
**Source:** [DesignRush — Mastering Graphic Design Prompts With ChatGPT](https://www.designrush.com/agency/graphic-design/trends/graphic-design-prompts)
**Author:** DesignRush editorial team (community framework)
**License:** Public blog content — quoted for educational/transformative use with attribution; pattern itself is uncopyrightable. Re-implement as Jarvis-original derivative for safety.

### Full Prompt (verbatim)

```
You are a senior graphic designer. When given a design request, produce a complete mini-brief before any visual suggestion. Cover all five components:

1. DESIGN CONTEXT
   - What is being designed (exact deliverable: poster, banner, slide, ad, infographic)
   - Where it will live (Instagram feed? print A2? web hero? OOH billboard?)
   - Required dimensions, formats, file types
   - Audience and reading distance

2. AESTHETIC & EMOTION
   - How it should look (3-5 visual adjectives — e.g., "spacious, confident, editorial")
   - How it should feel to the viewer (emotional payoff in one sentence)
   - What it must NOT feel like (the trap you want to avoid)

3. VISUAL REFERENCES
   - 3-5 named visual references with reasoning ("inspired by Nike brand system because...", "Apple keynote slide spacing because...", "Pentagram poster archive 2010-2020 because...")
   - 1-2 anti-references (what NOT to look like)

4. IMPLEMENTATION DETAILS
   - Layout grid (columns, baseline, margins)
   - Typography pairing (heading + body + accent)
   - Color palette (primary + secondary + accent with HEX or token names)
   - Hierarchy (what the eye should see 1st, 2nd, 3rd)
   - Imagery treatment (photography? illustration? abstract? icon set?)
   - Accessibility minimums (contrast ratio, min text size)

5. STRUCTURED BREAKDOWN
   - Break the deliverable into design phases (concept → wireframe → comp → polish)
   - List 3 distinct creative directions to explore before locking one
   - Specify the round count and review checkpoints

Output as a complete brief in markdown, ready to hand to a designer or to a generative-image tool as a long-form prompt.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Senior graphic designer" — narrow seniority.
- **Scope boundaries:** Brief-first discipline — no visuals until brief is complete.
- **Output format:** Five mandatory components with sub-bullets. Pinned.
- **Reasoning techniques:** Aesthetic + anti-aesthetic (what NOT to feel like) forces contrastive reasoning. Three creative directions force option-thinking.
- **Safety / refusal patterns:** Accessibility minimums baked in (contrast ratio, min text size). Anti-references reduce pastiche risk.
- **Examples / few-shot:** Named references ("Nike brand system", "Pentagram poster archive") teach the right kind of citation.

### 2026 trend relevance
- **Modern frameworks:** "Brief output composes into generative-image tool prompt" — explicitly 2024+ workflow where designer feeds into Midjourney, Imagen, DALL-E, or Adobe Firefly.
- **Current tech references:** Token-name color references (`primary`, `accent`) match design-system practice (Tailwind, Material 3, Figma variables).
- **Structured output:** Markdown brief is consumable by both human designers and image-gen tools.
- **Safety alignment:** Accessibility-by-default; anti-pastiche via anti-references.

### Deployability
- **License:** Source is public blog content — recommend re-implementing as Jarvis-original derivative. Pattern is uncopyrightable.
- **Vendor lock:** None.
- **Jarvis adaptability:** High. Output JSON/Markdown can feed image-generation MCPs (Gemini, future Imagen MCP).

---

## Runners-up + Trade-offs

### #2: Layout Critic (Prompt 4)
- **Why not picked:** Excellent rubric-based critique tool with seven scored dimensions, but reactive rather than generative. Wire as `design-critic` sibling agent for review passes.
- **When to use this instead:** Reviewing an existing layout before shipping.

### #3: Typography & Color System Specialist (Prompt 3)
- Strong design-system specialist for type + color artifacts. Wire as `design-system` sibling for design-system audit / build work.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/graphic-designer.md`
2. **Adaptations needed:**
   - Re-implement wording as Jarvis-original derivative (pattern is fine, exact phrasing is from a blog).
   - Chain output to image-generation MCP (currently Gemini, future Imagen) so brief -> image is one workflow.
   - Add Indian/regional design context awareness (festival visuals, regional typography like Devanagari pairings).
3. **Tool access (suggested):** Read (brand brief from memory), Write (brief to `data/notes/`), optional Gemini MCP for image generation, Blender MCP for 3D mockups.
4. **Model recommendation:** sonnet (best for nuanced brief generation); opus only for complex multi-asset systems.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Senior designer, brief-first. |
| Scope boundaries | 5/5 | Brief before visuals; five components. |
| Output format guidance | 5/5 | Five sections with sub-bullets. |
| Reasoning techniques | 5/5 | Contrastive aesthetic + 3 directions. |
| Safety / refusal patterns | 4/5 | Accessibility + anti-pastiche. |
| 2026 tech relevance | 5/5 | Composes with image-gen MCPs. |
| License-friendliness | 3/5 | Public blog source; re-implement as original. |
| **Overall** | **32/35** | |
