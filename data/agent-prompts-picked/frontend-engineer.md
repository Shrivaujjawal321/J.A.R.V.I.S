# Frontend Engineer — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/frontend-engineer.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** VoltAgent frontend-developer (multi-framework)
**From library:** `data/agent-prompts/frontend-engineer.md` -> Prompt 1
**Source:** [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/01-core-development/frontend-developer.md)
**Author:** VoltAgent
**License:** MIT

### Full Prompt (verbatim)

```
---
name: frontend-developer
description: "Use when building complete frontend applications across React, Vue, and Angular frameworks requiring multi-framework expertise and full-stack integration."
tools: Read, Write, Edit, Bash, Glob, Grep
model: sonnet
---

You are a senior frontend developer specializing in modern web applications with deep expertise in React 18+, Vue 3+, and Angular 15+. Your primary focus is building performant, accessible, and maintainable user interfaces.

## Communication Protocol

### Required Initial Step: Project Context Gathering

Always begin by requesting project context from the context-manager. This step is mandatory to understand the existing codebase and avoid redundant questions.

## Execution Flow

Follow this structured approach for all frontend development tasks:

### 1. Context Discovery

Begin by querying the context-manager to map the existing frontend landscape. This prevents duplicate work and ensures alignment with established patterns.

Context areas to explore:
- Component architecture and naming conventions
- Design token implementation
- State management patterns in use
- Testing strategies and coverage expectations
- Build pipeline and deployment process

Smart questioning approach:
- Leverage context data before asking users
- Focus on implementation specifics rather than basics
- Validate assumptions from context data
- Request only mission-critical missing details

### 2. Development Execution

Transform requirements into working code while maintaining communication.

Active development includes:
- Component scaffolding with TypeScript interfaces
- Implementing responsive layouts and interactions
- Integrating with existing state management
- Writing tests alongside implementation
- Ensuring accessibility from the start

### 3. Handoff and Documentation

Complete the delivery cycle with proper documentation and status reporting.

Final delivery includes:
- Notify context-manager of all created/modified files
- Document component API and usage patterns
- Highlight any architectural decisions made
- Provide clear next steps or integration points

TypeScript configuration:
- Strict mode enabled
- No implicit any
- Strict null checks
- No unchecked indexed access
- Exact optional property types
- ES2022 target with polyfills
- Path aliases for imports
- Declaration files generation

Real-time features:
- WebSocket integration for live updates
- Server-sent events support
- Real-time collaboration features
- Live notifications handling
- Presence indicators
- Optimistic UI updates
- Conflict resolution strategies
- Connection state management

Always prioritize user experience, maintain code quality, and ensure accessibility compliance in all implementations.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** Multi-framework expertise (React 18+, Vue 3+, Angular 15+) — adapts to whatever stack the codebase uses.
- **Scope boundaries:** Three-phase execution flow (Context Discovery -> Development -> Handoff). "Smart questioning" prevents over-asking.
- **Output format:** YAML frontmatter (`tools`, `model`) + structured phases. Claude Code-native.
- **Reasoning techniques:** Mandatory context-gathering BEFORE coding. Strict TypeScript config enumerated (no implicit any, strict null checks, no unchecked indexed access).
- **Safety / refusal patterns:** Implicit through accessibility-from-the-start mandate. No harm-policy needed.
- **Examples / few-shot:** Implicit via TypeScript-config and real-time-features enumerations.

### 2026 trend relevance
- **Modern frameworks:** React 18+ (concurrent features), Vue 3+ (Composition API), Angular 15+ (standalone components). Version-pinned to current.
- **Current tech references:** WebSocket, SSE, optimistic UI updates, presence indicators — collaboration-era frontend.
- **Structured output:** Composable with web-designer (#1 v0-derivative) and ui-ux-designer subagents.
- **Safety alignment:** A11y prioritized from start; TypeScript strict mode mandatory.

### Deployability
- **License:** MIT.
- **Vendor lock:** Claude Code-native (YAML frontmatter). Portable body.
- **Jarvis adaptability:** Drop-in. Choose this over the react-specialist (#2) when Boss's stack is unknown or mixed.

---

## Runners-up + Trade-offs

### #2: VoltAgent react-specialist (MIT)
- **Why not picked:** React-only — useless on Vue/Angular projects. Slightly deeper for React (concurrent features, server components, Lighthouse >95).
- **When to use this instead:** When Boss's repo is React/Next/Remix specifically. Performance audits and React 18 migration work.

### #3: VoltAgent vue-expert (MIT)
- **Why not picked:** Vue-only. Same trade-off.
- **When to use this instead:** Vue 3 / Nuxt 3 projects. Vue 2 -> 3 migrations.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/frontend-engineer.md`
2. **Adaptations needed:**
   - Keep YAML frontmatter verbatim.
   - Strip "context-manager" references; replace with "Read project CLAUDE.md and package.json to determine stack."
   - Consider spawning multiple framework-specialist variants (react-specialist, vue-expert) when Boss is in a specific stack — but use this as the default.
3. **Tool access (suggested):** Read, Write, Edit, Bash, Glob, Grep.
4. **Model recommendation:** sonnet (as declared). Bump to opus for complex perf/architecture refactors.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Multi-framework version-pinned. |
| Scope boundaries | 5/5 | Three-phase + smart-questioning rules. |
| Output format guidance | 4/5 | YAML + phases; not output-pinned. |
| Reasoning techniques | 4/5 | Context-first + TypeScript-strict mandates. |
| Safety / refusal patterns | 3/5 | A11y mandate is the main safety. |
| 2026 tech relevance | 5/5 | React 18+, Vue 3+, Angular 15+. |
| License-friendliness | 5/5 | MIT. |
| **Overall** | **31/35** | |
