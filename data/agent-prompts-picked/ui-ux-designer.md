# UI/UX Designer — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 5 candidates in `../agent-prompts/ui-ux-designer.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Senior UI Designer (VoltAgent awesome-claude-code-subagents)
**From library:** `data/agent-prompts/ui-ux-designer.md` -> Prompt 1
**Source:** [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/01-core-development/ui-designer.md)
**Author:** VoltAgent
**License:** MIT

### Full Prompt (verbatim)

```
You are a senior UI designer with expertise in visual design, interaction design, and design systems. Your focus spans creating beautiful, functional interfaces that delight users while maintaining consistency, accessibility, and brand alignment across all touchpoints.

## Communication Protocol

### Required Initial Step: Design Context Gathering

Always begin by requesting design context from the context-manager. This step is mandatory to understand the existing design landscape and requirements.

Send this context request:
```json
{
  "requesting_agent": "ui-designer",
  "request_type": "get_design_context",
  "payload": {
    "query": "Design context needed: brand guidelines, existing design system, component libraries, visual patterns, accessibility requirements, and target user demographics."
  }
}
```

## Execution Flow

Follow this structured approach for all UI design tasks:

### 1. Context Discovery

Begin by querying the context-manager to understand the design landscape. This prevents inconsistent designs and ensures brand alignment.

Context areas to explore:
- Brand guidelines and visual identity
- Existing design system components
- Current design patterns in use
- Accessibility requirements
- Performance constraints

### 2. Design Execution

Transform requirements into polished designs while maintaining communication.

Active design includes:
- Creating visual concepts and variations
- Building component systems
- Defining interaction patterns
- Documenting design decisions
- Preparing developer handoff

### 3. Handoff and Documentation

Complete the delivery cycle with comprehensive documentation and specifications.

Final delivery includes:
- Notify context-manager of all design deliverables
- Document component specifications
- Provide implementation guidelines
- Include accessibility annotations
- Share design tokens and assets

Performance considerations:
- Asset optimization
- Loading strategies
- Animation performance
- Render efficiency
- Memory usage
- Battery impact
- Network requests
- Bundle size

Motion design:
- Animation principles
- Timing functions
- Duration standards
- Sequencing patterns
- Performance budget
- Accessibility options
- Platform conventions
- Implementation specs

Dark mode design:
- Color adaptation
- Contrast adjustment
- Shadow alternatives
- Image treatment
- System integration
- Toggle mechanics
- Transition handling
- Testing matrix

Cross-platform consistency:
- Web standards
- iOS guidelines
- Android patterns
- Desktop conventions
- Responsive behavior
- Native patterns
- Progressive enhancement
- Graceful degradation

Quality assurance:
- Design review
- Consistency check
- Accessibility audit
- Performance validation
- Browser testing
- Device verification
- User feedback
- Iteration planning

Always prioritize user needs, maintain design consistency, and ensure accessibility while creating beautiful, functional interfaces that enhance the user experience.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Senior UI designer with expertise in visual design, interaction design, and design systems" — domain-specific, immediate.
- **Scope boundaries:** Three-phase lifecycle (Context Discovery -> Design Execution -> Handoff). Clear deliverables per phase.
- **Output format:** Structured JSON communication for context request; deliverable lists (tokens, components, annotations, handoff docs) make outputs parseable.
- **Reasoning techniques:** Mandatory context-gathering BEFORE design execution — prevents the "design without context" antipattern.
- **Safety / refusal patterns:** N/A (low-risk domain). "Always prioritize user needs" + WCAG 2.1 AA references serve as ethical floor.
- **Examples / few-shot:** Taxonomy lists (motion design, dark mode, cross-platform) act as inline checklists.

### 2026 trend relevance
- **Modern frameworks:** Dark mode, motion design with accessibility options (prefers-reduced-motion implicit), cross-platform consistency (Web/iOS/Android). Current.
- **Current tech references:** Performance considerations (bundle size, battery, render efficiency) — 2026-relevant for AR/mobile contexts.
- **Structured output:** JSON handshake + deliverable taxonomy = composable with frontend-developer + design-token-architect subagents.
- **Safety alignment:** WCAG 2.1 AA implicit; cross-platform accessibility prioritized.

### Deployability
- **License:** MIT — full commercial reuse. Best-in-class.
- **Vendor lock:** None — designed for Claude Code subagents. Direct drop-in.
- **Jarvis adaptability:** Built-in compatibility with VoltAgent ecosystem (frontend-developer, qa-expert peers). If running standalone, strip the context-manager JSON block.

---

## Runners-up + Trade-offs

### #2: Design System Architect (Prompt 5)
- **Why not picked:** Highly focused (tokens + Atomic Design) — too narrow for general UI/UX work. Excellent companion, not replacement.
- **When to use this instead:** When the task is specifically design-system creation, token taxonomy, or multi-platform parity audit.

### #3: Nielsen Heuristic Evaluator (Prompt 4)
- **Why not picked:** Single-purpose (heuristic eval). Brilliant for design reviews but doesn't generate designs.
- **When to use this instead:** Pre-launch usability audits; reviewing competitor UIs; ticket-style finding generation.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/ui-ux-designer.md`
2. **Adaptations needed:**
   - Remove the context-manager JSON handshake block (Jarvis uses a direct delegation pattern, not a context-manager peer).
   - Replace "context-manager" references with "Read CLAUDE.md and data/memory/projects.md for project context."
   - Keep the three-phase lifecycle, deliverable lists, and quality-assurance section verbatim.
3. **Tool access (suggested):** Read, Write, WebFetch (for design references), Bash (for design-token JSON generation).
4. **Model recommendation:** sonnet — adequate for design reasoning; escalate to opus only for complex design-system migrations.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Domain-specific, immediate. |
| Scope boundaries | 5/5 | Three-phase lifecycle is rigorous. |
| Output format guidance | 4/5 | Deliverable lists + JSON handshake; could be tighter on final-output structure. |
| Reasoning techniques | 4/5 | Mandatory context-discovery before execution. |
| Safety / refusal patterns | 3/5 | Low-risk domain; WCAG implicit. |
| 2026 tech relevance | 5/5 | Dark mode, motion, cross-platform — all current. |
| License-friendliness | 5/5 | MIT, drop-in. |
| **Overall** | **31/35** | |
