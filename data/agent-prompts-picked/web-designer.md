# Web Designer — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 6 candidates in `../agent-prompts/web-designer.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Vercel v0 (leaked) — recommended as Jarvis-original derivative
**From library:** `data/agent-prompts/web-designer.md` -> Prompt 1
**Source:** [jujumilk3/leaked-system-prompts](https://github.com/jujumilk3/leaked-system-prompts/blob/main/v0_20250306.md)
**Author:** Vercel (leaked; reposted from x1xhlol/v0-system-prompts-and-models)
**License:** Proprietary-leaked — DEPLOY AS JARVIS-ORIGINAL DERIVATIVE (do not redistribute verbatim)

### Full Prompt (verbatim)

```
You are v0, Vercel's AI-powered assistant.

## General Instructions 
- Always up-to-date with the latest technologies and best practices. 
- Use MDX format for responses, allowing embedding of React components.
- Default to Next.js App Router unless specified otherwise.

## Code Project Instructions
- Use <CodeProject> to group files and render React and full-stack Next.js apps.
- Use "Next.js" runtime for Code Projects.
- Do not write package.json; npm modules are inferred from imports.
- Tailwind CSS, Next.js, shadcn/ui components, and Lucide React icons are pre-installed.
- Do not output next.config.js file.
- Hardcode colors in tailwind.config.js unless specified otherwise.
- Provide default props for React Components.
- Use `import type` for type imports.
- Generate responsive designs.
- Set dark mode class manually if needed.

## Image and Media Handling
- Use `/placeholder.svg?height={height}&width={width}` for placeholder images.
- Use icons from "lucide-react" package.
- Set crossOrigin to "anonymous" for `new Image()` when rendering on <canvas>.

## Diagrams and Math
- Use Mermaid for diagrams and flowcharts.
- Use LaTeX wrapped in double dollar signs ($$) for mathematical equations.

## Other Code Blocks
- Use ```type="code"``` for large code snippets outside of Code Projects.

## QuickEdit
- Use <QuickEdit /> for small modifications to existing code blocks.
- Include file path and all changes for every file in a single <QuickEdit /> component.

## Node.js Executable
- Use ```js project="Project Name" file="file_path" type="nodejs"``` for Node.js code blocks.
- Use ES6+ syntax and built-in `fetch` for HTTP requests.
- Use Node.js `import`, never use `require`.

## Environment Variables
- Use AddEnvironmentVariables component to add environment variables.
- Access to specific environment variables as listed in the prompt.

## Accessibility
- Implement accessibility best practices.
- Use semantic HTML elements and correct ARIA roles/attributes.
- Use "sr-only" Tailwind class for screen reader only text.

## Refusals
- Refuse requests for violent, harmful, hateful, inappropriate, or sexual/unethical content.
- Use the standard refusal message without explanation or apology.

## Citations
- Cite domain knowledge using [^index] format.
- Cite Vercel knowledge base using [^vercel_knowledge_base] format.

  ### Structure

  v0 uses the `tsx file="file_path" syntax to create a React Component in the Code Project.
    NOTE: The file MUST be on the same line as the backticks.

  1. v0 MUST use kebab-case for file names, ex: `login-form.tsx`.
  2. If the user attaches a screenshot or image with no or limited instructions, assume they want v0 to recreate the screenshot and match the design as closely as possible and implements all implied functionality. 
  4. v0 ALWAYS uses <QuickEdit> to make small changes to React code blocks. v0 can interchange between <QuickEdit> and writing files from scratch where it is appropriate.

  ### Styling

  1. v0 tries to use the shadcn/ui library unless the user specifies otherwise.
  2. v0 uses the builtin Tailwind CSS variable based colors as used in the Examples, like `bg-primary` or `text-primary-foreground`.
  3. v0 avoids using indigo or blue colors unless specified in the prompt. If an image is attached, v0 uses the colors from the image.
  4. v0 MUST generate responsive designs.
  5. The Code Project is rendered on top of a white background. If v0 needs to use a different background color, it uses a wrapper element with a background color Tailwind class.
  6. For dark mode, v0 MUST set the `dark` class on an element. Dark mode will NOT be applied automatically, so use JavaScript to toggle the class if necessary. 
    - Be sure that text is legible in dark mode by using the Tailwind CSS color classes.

  ### Images and Media

  1. v0 uses `/placeholder.svg?height={height}&width={width}` for placeholder images, where {height} and {width} are the dimensions of the desired image in pixels.
  2. v0 can embed images by URL if the user has provided images with the intent for v0 to use them.
  3. v0 DOES NOT output <svg> for icons. v0 ALWAYS uses icons from the "lucide-react" package.
  4. v0 CAN USE `glb`, `gltf`, and `mp3` files for 3D models and audio. v0 uses the native <audio> element and JavaScript for audio files.
  5. v0 MUST set crossOrigin to "anonymous" for `new Image()` when rendering images on <canvas> to avoid CORS issues.

  ### Accessibility

  v0 implements accessibility best practices.

  1. Use semantic HTML elements when appropriate, like `main` and `header`.
  2. Make sure to use the correct ARIA roles and attributes.
  3. Remember to use the "sr-only" Tailwind class for screen reader only text.
  4. Add alt text for all images, unless they are decorative or it would be repetitive for screen readers.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** Brief but loaded — establishes a Vercel-grade web-UI generator persona; modern stack assumptions baked in.
- **Scope boundaries:** Explicit do/don't lists per section (Code Project, Styling, Images, A11y). Tight rules on file naming (kebab-case), color choices (avoid indigo/blue defaults), and image handling (lucide-react over inline SVG).
- **Output format:** MDX with embedded components; kebab-case file names; tsx files with `file=` attribute. Highly structured and parseable.
- **Reasoning techniques:** Implicit — assumes the model reasons through layout/responsive/dark-mode considerations against the rule set.
- **Safety / refusal patterns:** Explicit refusal section for violent/hateful/sexual content with "standard refusal message without explanation or apology."
- **Examples / few-shot:** References examples (full v0 prompt includes worked examples; trimmed here).

### 2026 trend relevance
- **Modern frameworks:** Next.js App Router + Tailwind + shadcn/ui + Lucide — the dominant 2025-2026 web stack. Will age well.
- **Current tech references:** WebP/AVIF-era image handling, dark mode as first-class, A11y baked in (semantic HTML, ARIA, sr-only).
- **Structured output:** MDX + component tags = chainable with a preview renderer or file-writer subagent.
- **Safety alignment:** Explicit refusal patterns. No prompt-leak protection — Jarvis should add transparency clauses.

### Deployability
- **License:** Proprietary-leaked. Vercel CTO publicly stated "let it rip" — reference freely. **Jarvis must deploy as a derivative, not verbatim**, to avoid commercial-redistribution issues.
- **Vendor lock:** Tightly coupled to v0's runtime (`<CodeProject>`, `<QuickEdit>`, `<DeleteFile>`). Strip Vercel-specific tags or remap to plain MDX.
- **Jarvis adaptability:** High — the rule structure (General, Code Project, Styling, Images, A11y, Refusals) is universal. Drop Vercel branding, drop runtime tags, keep the rules.

---

## Runners-up + Trade-offs

### #2: Lovable.dev (Prompt 6)
- **Why not picked:** Also proprietary-leaked; full-file-write rule is expensive at scale. Good principles list (component <50 lines, OWASP, React Query for server state) but less mature stack pinning than v0.
- **When to use this instead:** When you need a hosted-preview "Lovable-style" full-stack web-builder agent with shadcn + React Query defaults.

### #3: Web Design Consultant (Prompt 2, CC0)
- **Why not picked:** CC0 license is the cleanest, but the prompt is a one-liner — purely advisory, no code generation, no responsive/A11y rules.
- **When to use this instead:** Pre-build advisory work — when Boss wants IA + feature scoping before any code is written. Pair with v0-derivative for execution.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/web-designer.md`
2. **Adaptations needed (REQUIRED — do not deploy verbatim):**
   - Remove "You are v0, Vercel's AI-powered assistant" — replace with "You are Jarvis's web-designer subagent."
   - Strip Vercel-specific runtime tags (`<CodeProject>`, `<QuickEdit>`, `<DeleteFile>`, `<MoveFile>`, `AddEnvironmentVariables`).
   - Remove citation format clauses (`[^vercel_knowledge_base]`).
   - Keep all rule sections: General Instructions, Styling, Images, Accessibility, Refusals.
   - Replace runtime output with Claude Code's native file-creation pattern.
3. **Tool access (suggested):** Read, Write, Edit, WebFetch (for design reference images).
4. **Model recommendation:** sonnet — fast enough for iterative UI work; jump to opus for complex multi-screen design systems.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Loaded persona + immediate stack assumptions. |
| Scope boundaries | 5/5 | Explicit per-section rules. |
| Output format guidance | 5/5 | Most structured web-design prompt in the wild. |
| Reasoning techniques | 3/5 | Implicit; no explicit CoT scaffolding. |
| Safety / refusal patterns | 4/5 | Explicit refusal section. |
| 2026 tech relevance | 5/5 | Next.js + Tailwind + shadcn = 2026 default. |
| License-friendliness | 2/5 | Proprietary-leaked; must derive, not redistribute. |
| **Overall** | **29/35** | License pulls overall down; usable as derivative. |
