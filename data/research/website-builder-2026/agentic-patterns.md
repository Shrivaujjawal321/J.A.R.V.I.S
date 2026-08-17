# Agentic Architectures for High-Quality UI-Code Generation (mid-2026)

**Researched:** 2026-06-11 · For: premium AI website-builder product (short prompt → unique, Awwwards-tier site)
**Method:** WebSearch + WebFetch across primary sources (Vercel/Anthropic/Lovable engineering blogs, arXiv 2024-2026, leaked system prompts, pricing teardowns). Anything not corroborated by a primary source is tagged **[unverified]**.

---

## 1. Production pipeline internals — v0, Lovable, Bolt

### 1.1 Vercel v0 — "composite model" pipeline (best-documented production system)

Primary sources: [Introducing the v0 composite model family](https://vercel.com/blog/v0-composite-model-family) · [How we made v0 an effective coding agent](https://vercel.com/blog/how-we-made-v0-an-effective-coding-agent) · [Fireworks AI case study](https://fireworks.ai/blog/vercel)

v0 is NOT a single model call. It is a **composite pipeline that decouples specialized components from the base model**:

- **Base generation:** `v0-1.5-md` = Claude Sonnet 4 base + **RAG pipeline** pulling from docs, UI examples, and Vercel's internal knowledge base. Full generations go to the frontier model.
- **Dynamic system prompts:** embeddings + keyword matching detect intent; version-targeted SDK knowledge is injected into the prompt. Prompt kept stable to **maximize prompt-cache hits**. Curated, LLM-consumption-optimized code samples live in a read-only filesystem the model can read.
- **QuickEdit routing:** small edits (text change, syntax fix) route to a faster model instead of full regeneration — "surgical modifications without full regeneration."
- **"LLM Suspense" (mid-stream transforms):** while the base model streams, a layer rewrites the stream in real time — long blob URLs swapped for short tokens then restored post-generation; hallucinated `lucide-react` icon names detected via vector embeddings and replaced with nearest real icon **within ~100ms, no extra model call**.
- **AutoFix model:** custom fine-tuned `vercel-autofixer-01` (reinforcement fine-tuning with Fireworks, **10-40x faster** than competing error-correction approaches, post-stream passes run **<250ms**) trained on real generation failures. Result: **93.87% error-free generation rate**; Vercel says LLMs alone err up to ~10% of the time, and the composite pipeline yields a "double-digit increase in success rates."
- Vercel CTO Malte Ubl on the prompt leak: "A prompt without the evals, models, and especially UX is like getting a broken ASML machine without a manual" ([Simon Willison](https://simonwillison.net/2024/Nov/25/leaked-system-prompts-from-vercel-v0/)) — i.e., the moat is the pipeline + evals, not the prompt text.

**Leaked v0 prompt** (~1,300 lines, [GitHub mirror](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools), [March 2025 snapshot](https://agentic-design.ai/prompt-hub/vercel/v0-20250306)): hard-codes Next.js App Router + TypeScript + Tailwind + shadcn/ui + Radix + Lucide + Framer Motion; WCAG 2.1 AA rules (semantic HTML, ARIA, contrast); mobile-first responsive mandates; edit protocol = "identify target component → preserve surrounding context → apply focused modification → maintain design-system consistency → validate accessibility." Claims that v0 runs GPT-4.0/DeepSeek ([cybercorsairs](https://cybercorsairs.com/vercels-v0-prompts-leaked/)) are outdated/**[unverified]** — official 2025 blog says Sonnet 4 base.

### 1.2 Lovable — agent loop + design-system enforcement in the prompt

Primary sources: [Agent Mode (Beta) announcement](https://lovable.dev/blog/agent-mode-beta) · [leaked Agent Prompt](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools/blob/main/Lovable/Agent%20Prompt.txt) · [docs](https://docs.lovable.dev/features/agent-mode) · [beam.cloud architecture teardown](https://www.beam.cloud/blog/agentic-apps)

- Stack: React + Vite + Tailwind + TS; chat left, live iframe preview right; realtime (WebSocket) loop; **no arbitrary backend execution — Supabase native integration** for auth/DB/edge functions.
- **Agent Mode** (default since 2025-07-23): autonomous multi-step loop that can search the codebase, read files on demand, **inspect console logs + network requests**, query the DB, search the web, and — critically — **drive the rendered app in a browser: click buttons, fill forms, navigate, test mobile/tablet/desktop sizes, and capture screenshots to verify real behavior**. Lovable claims this cut build error rates **up to 91%** (vendor claim, **[unverified]** independently).
- **Leaked prompt's design discipline:** "all styles must be defined in the design system" — semantic HSL tokens in `index.css` + `tailwind.config.ts`; explicit ban on ad-hoc utility classes like `text-white`/`bg-black`; custom shadcn variants must be built from tokens. This is *prompt-level design-system enforcement*.
- **Edit strategy:** prefer search-replace diffs over file rewrites; small verifiable changes; batch file ops; "least invasive approach."
- **Interaction model:** discussion-first — assumes user wants to plan unless explicit action words ("implement", "create", "add"). Debug workflow: "use debugging tools FIRST" (logs, network) before touching code.

### 1.3 Bolt.new — environment-control maximalism

Primary sources: [stackblitz/bolt.new GitHub](https://github.com/stackblitz/bolt.new) · [Evil Martians teardown](https://evilmartians.com/chronicles/bolt-new-from-stackblitz-how-they-surfed-the-ai-wave-with-no-wipeouts)

- Claude Sonnet (3.5 at launch) + **WebContainers**: full Node.js runtime in the browser tab. The model gets **complete control of filesystem, node server, package manager, terminal, and browser console** — errors from the live environment feed straight back into the loop.
- Defaults to Vite for HMR-fast previews. Open-source `bolt.diy` repo makes this the most copyable architecture.
- Generic agent-loop shape (per beam.cloud): **plan → edit files → run app → inspect errors → iterate**, sandbox as the most important component (isolated FS, dep install, dev server, log collection, preview URLs, resource limits); "context engineering is more important" than prompt cleverness.

---

## 2. Visual self-critique / screenshot-feedback research (2024 → 2026)

### 2.1 Foundations
- **Design2Code** (Stanford SALT, [arXiv:2403.03163](https://arxiv.org/abs/2403.03163), NAACL 2025): 484 real webpages, screenshot→code. Three prompting modes: direct, text-augmented, **self-revision** (model sees reference screenshot + screenshot of its own render, revises). Humans judged GPT-4V output replaceable-with-original in 49% of cases, *better* in 64%. Self-revision gains were small relative to model choice **[unverified — exact deltas not retrievable; paper PDF 404'd in this pass]**.
- **WebSight** (HuggingFace, [arXiv:2403.09029](https://arxiv.org/abs/2403.09029)): 2M synthetic screenshot↔HTML/Tailwind pairs for fine-tuning VLMs (Sightseer). Established Tailwind-as-target-representation for visual-to-code training.
- **Critical counterweight — Huang et al., ICLR 2024** ([arXiv:2310.01798](https://arxiv.org/abs/2310.01798)): **LLMs cannot self-correct reasoning intrinsically**; GPT-4 *drops* 95.5%→91.5% on GSM8K when asked to review itself without external signal. Implication for UI agents: a critique loop only works when grounded in **external evidence** — a rendered screenshot, console errors, lint output, GUI test results — not "look at your code again."

### 2.2 2025-2026 state of the art
- **METAL** (ACL 2025, [arXiv:2502.17651](https://arxiv.org/abs/2502.17651)): 4-agent chart-replication framework — Generation / **Visual Critique** / **Code Critique** / Revision. +5.2% over best prior; +11.33% over direct prompting (Llama-3.2-11B). Two key findings: (a) **separating visual critique from code critique boosts VLM self-correction**, (b) **test-time scaling — accuracy rises monotonically** as critique-revision compute grows 512→8192 tokens.
- **ReLook** (Oct 2025, [arXiv:2510.11498](https://arxiv.org/abs/2510.11498)): vision-grounded RL for web coding; MLLM critic scores screenshots during training; **strict zero-reward for any invalid render** (anchors renderability, prevents reward hacking); **Forced Optimization** — only accept revisions that improve score (monotonic trajectories); at inference, critic is removed and a cheap self-edit cycle retains most gains.
- **WebGen-Agent** (Sep 2025, [arXiv:2509.22644](https://arxiv.org/abs/2509.22644)): the strongest published evidence for multi-level visual feedback. Loop = generate → render → **(a) VLM screenshot critique with numeric score + (b) GUI-agent actually clicks through the site, also scored** → backtrack-and-select-best. Results on WebGen-Bench: **Claude-3.5-Sonnet accuracy 26.4% → 51.9% (+25.5pp); appearance score 3.0 → 3.9** just from the agent workflow (no retraining). Step-GRPO on the visual scores lifts Qwen2.5-Coder-7B 38.9%→45.4%.
- **Vision-Guided Iterative Refinement / critic-in-the-loop (CITL)** (Amazon AGI, [arXiv:2604.05839](https://arxiv.org/html/2604.05839v1)): generator + **VLM visual critic + LLM code critic, max 3 cycles, keep best-scoring iteration**. Distill-Qwen-14B +17.8% with critic vs **+1.5% refining WITHOUT critic feedback** — i.e., ~12x the gain when refinement is critic-grounded. Claude Sonnet improved on 86% of tasks. Multi-dimensional VLM-judge (task, aesthetics, code accomplishment, code quality) agreed with humans 69.5% vs 48.5% for single-score judging. 42.8% of found issues were visual polish, 25.6% aesthetic — **most of what a critic catches is exactly the "generic AI output" problem**. Caveat: code quality slightly *declined* across cycles (system optimizes user-visible correctness).
- **ScreenCoder** (Jul 2025, [arXiv:2507.22827](https://arxiv.org/abs/2507.22827)): modular 3-agent visual-to-code — **grounding** (VLM detects/labels UI components) → **planning** (hierarchical layout from front-end engineering priors) → **generation** (adaptive prompt-based synthesis). Beats end-to-end GPT-4o on layout (block match 0.755 vs 0.730); interpretable stages.
- **Design critique generation** (Google, [arXiv:2412.16829](https://arxiv.org/abs/2412.16829)): iterative visual prompting produces design comments + bounding boxes from a screenshot + guidelines — the template for an automated "design reviewer" agent.

### 2.3 Benchmarks / judges that matter in 2026
- **WebGen-Bench** ([arXiv:2505.03733](https://arxiv.org/abs/2505.03733)): agent builds multi-file site from scratch; GUI-agent tests functionality; VLM grades appearance 1-5 (rendering, relevance, layout harmony, modernity).
- **ArtifactsBench** ([arXiv:2507.04952](https://arxiv.org/abs/2507.04952)): renders artifacts, captures **temporal (3-step) screenshots** for dynamic behavior, MLLM-judge guided by **per-task fine-grained checklists** across 10 dimensions (functionality, robustness, creativity, aesthetics, UX…). **94.4% ranking consistency with WebDev Arena** human preference; >90% pairwise agreement with experts. → Checklist-guided MLLM judging is now reliable enough to use as an automated quality gate.
- **DesignBench** ([arXiv:2506.06251](https://arxiv.org/abs/2506.06251)): generation/edit/repair across React/Vue/Angular — MLLMs are **markedly worse in framework code than vanilla HTML/CSS**, and the bottleneck in edit/repair is **localizing which code to change**. (Supports v0/Lovable-style structured edit protocols + QuickEdit routing.)
- Model choice (Dec 2025, [Lenny's Newsletter test by Claire Vo](https://www.lennysnewsletter.com/p/which-ai-model-is-the-best-designer)): Claude Opus 4.5 produced "a beautiful, polished, production-ready redesign," Gemini 3 adequate, GPT-5.1 Codex "completely whiffed"; observation: **"planning capabilities dramatically impact design quality."** Gemini 3 leads WebDev Arena style boards ([comparison roundups](https://www.glbgpt.com/hub/claude-opus-4-5-vs-gemini-3/)) — single-source judgments, treat as directional.

---

## 3. Design-system-first generation (the anti-generic lever)

- **shadcn/ui is the de-facto AI-generation substrate in 2026** — v0, Lovable, Claude, Cursor all emit shadcn-shaped output ([Design Systems Collective](https://www.designsystemscollective.com/design-systems-for-the-vibe-coding-era-42282e1affef), [Medium/Pawel Klasa](https://medium.com/design-bootcamp/the-most-important-design-system-in-2026-that-designers-missed-was-built-by-a-developer-d5617753882e)). Consequence: default output converges to the same look → **uniqueness must be injected upstream (tokens + creative direction), not expected from the model.**
- **Vercel's official recipe** ([AI-powered prototyping with design systems](https://vercel.com/blog/ai-powered-prototyping-with-design-systems), Aug 2025): three layers — (1) **design tokens** applied to a shadcn theme as the visual baseline, (2) atomic component architecture (tokens → atoms → molecules → organisms) with low-abstraction components, (3) a **shadcn Registry served over MCP** so agents (v0/Cursor/Windsurf) fetch real components instead of hallucinating. "Models need to understand how components are structured, styled, and relate to each other."
- **Token-first 3-layer pattern** ([Hardik Pandya](https://hvpandya.com/llm-design-systems)): spec files the LLM reads → token layer it must pick from → **automated audit catching violations**. The LLM never decides "what blue" — it selects a token.
- **DESIGN.md** (Google Labs, open-sourced April 2026 per [WaveSpeed analysis](https://wavespeed.ai/blog/posts/design-md-vs-design-tokens-ai-workflows/)): single file = YAML front-matter tokens + **prose rationale** ("why this color exists, when not to use it"). Their testing: **multi-screen consistency measurably improved with prose context even with identical token values**; the narrative layer "re-anchors" the agent across generation passes. Tokens alone are insufficient — agents fill missing context with training-data defaults = generic output.
- **Lovable's leaked prompt** enforces the same idea at runtime (semantic tokens only, no raw utility colors). **shadcn MCP server** lets agents browse/search/install registry components directly.

---

## 4. Structured intake → creative direction → codegen → visual critique → revise

### 4.1 Relume (closest commercial analog of staged site generation)
[relume.io](https://www.relume.io/) pipeline: company-description prompt → **sitemap** (Home first as a direction-check gate, then the rest) → one-click **wireframes** with real copy from a **1,000+ component library** (section title/description in the sitemap selects the component) → **Style Guide Builder** locks a design system → export Figma/Webflow/React. Pattern: **structure before style, human gate at each stage, constrained component vocabulary.**

### 4.2 Anthropic's three-agent harness (April 2026 — the most direct blueprint)
[InfoQ coverage](https://www.infoq.com/news/2026/04/anthropic-three-agent-harness-ai/) of Anthropic Labs' long-running full-stack dev harness:
- **Planner / Generator / Evaluator** as separate agents; handoff via **structured artifacts + context resets** (not compaction) so each agent starts from a defined state.
- Evaluator is **calibrated with few-shot examples + scoring criteria**; for frontend it grades **design quality, originality, craft, functionality**, and **navigates the live page via Playwright MCP** (interacts, not just screenshots).
- **5-15 critique-refine cycles per run**, sessions up to 4 hours, "progressively refined outputs combining visual distinction with functional accuracy."
- Anthropic Labs lead Prithvi Rajasekaran: **"Separating the agent doing the work from the agent judging it proves to be a strong lever."** OpenAI and Anthropic independently converged on this ([Shiplight analysis](https://www.shiplight.ai/blog/planner-generator-evaluator-multi-agent-qa)) because self-evaluation by the producing agent is unreliable (consistent with Huang et al.).
- Code with Claude 2026 (May 2026) reportedly productized this: **Outcomes** (self-grading via separate evaluator agent) + **Multiagent Orchestration** (coordinator fans to specialist subagents on a shared filesystem) + Dreaming (memory consolidation) — **[partially verified: secondary coverage only](https://www.mindstudio.ai/blog/code-with-claude-2026-new-agent-features)**.

### 4.3 Claude Agent SDK loop ([official post](https://claude.com/blog/building-agents-with-the-claude-agent-sdk))
**Gather context → take action → verify work → repeat.** Verification ladder: (1) **rules-based** (typecheck/lint — "generate TypeScript and lint it" for extra feedback layers), (2) **visual** (screenshots for layout/styling/hierarchy/responsiveness), (3) **LLM-as-judge** for fuzzy criteria (higher latency, lower robustness — use last). Subagents = isolated context windows returning only relevant info; compaction for long sessions.

### 4.4 Anthropic multi-agent research system ([official engineering post](https://www.anthropic.com/engineering/multi-agent-research-system))
- Orchestrator-worker: lead agent plans, spawns parallel subagents; **Opus 4 lead + Sonnet 4 workers beat single Opus 4 by 90.2%** on internal research eval.
- **Cost reality: agents ≈ 4x chat tokens; multi-agent ≈ 15x chat tokens.** Token spend itself explains ~80% of performance variance.
- **Explicit warning: coding is a poor fit for parallel multi-agent** (fewer parallelizable components, heavy interdependence, agents need shared context). For a site builder: parallelize *research/asset/section-spec* work, keep *code generation* in one coherent context (or page-level parallelism with a shared design-system contract).
- Delegation prompts must carry objective, output format, tool guidance, task boundaries; embed scaling rules (1 agent for simple, 10+ only for genuinely parallel work). **Parallel tool calling cut research time up to 90%.**
- Eval approach: start with ~20 test cases; single LLM-judge with one rubric prompt (accuracy, citation, completeness, source quality, efficiency) scoring 0-1 was most human-aligned; keep human spot-checks.

---

## 5. Does the critic loop measurably help? (evidence table)

| System | Setup | Gain from critique/judging | Source |
|---|---|---|---|
| CITL (Amazon AGI) | VLM visual critic + LLM code critic, ≤3 cycles | **+17.8%** (best-cycle) vs **+1.5% without critic** | [2604.05839](https://arxiv.org/html/2604.05839v1) |
| WebGen-Agent | screenshot score + GUI-agent test score + backtrack | Claude-3.5 accuracy **26.4→51.9%**, appearance 3.0→3.9 | [2509.22644](https://arxiv.org/abs/2509.22644) |
| METAL | split visual/code critics | +5.2% SOTA, +11.33% vs direct; **monotonic test-time scaling** | [2502.17651](https://arxiv.org/abs/2502.17651) |
| ReLook | MLLM critic in RL + zero-reward invalid renders | consistent wins on 3 benchmarks; critic-free inference keeps most gains | [2510.11498](https://arxiv.org/abs/2510.11498) |
| Anthropic harness | separate Evaluator, 5-15 cycles, Playwright | qualitative: visual distinction + functional accuracy; "strong lever" | [InfoQ](https://www.infoq.com/news/2026/04/anthropic-three-agent-harness-ai/) |
| v0 AutoFix | streaming + post-stream fixers | **93.87% error-free generations**; double-digit success-rate lift | [Vercel](https://vercel.com/blog/v0-composite-model-family) |
| Lovable Agent Mode | logs + network + browser-testing feedback | up to **91% lower build error rate** (vendor claim) | [Lovable](https://lovable.dev/blog/agent-mode-beta) |
| Intrinsic self-correction (no external signal) | model re-reads own output | **negative**: GPT-4 95.5→91.5 on GSM8K | [2310.01798](https://arxiv.org/abs/2310.01798) |
| Design2Code self-revision | sees own render vs reference | small/marginal **[unverified exact numbers]** | [2403.03163](https://arxiv.org/abs/2403.03163) |

**Verdict:** grounded critics (render + screenshot + interaction + lint) reliably add double-digit quality; ungrounded "try again" adds ~nothing or hurts. Judge reliability is solved-enough via checklist-guided MLLM judges (ArtifactsBench: **94.4% agreement with WebDev Arena**). Diminishing returns: CITL caps at 3 cycles, Anthropic runs 5-15; keep-best/backtracking (WebGen-Agent, ReLook's Forced Optimization) prevents regression across cycles.

---

## 6. Token / cost realities (full multi-section site)

- **Bolt.new** observed consumption ([banani.co teardown](https://www.banani.co/blog/bolt-new-pricing), author+user reports, not official): **small projects 50-150K tokens/prompt; medium 150-500K/prompt; a complete simple app ≈ 3M tokens total.** Costs grow as project grows (whole codebase re-enters context). Plans: free 1M/mo, Pro $25/mo = 10M tokens.
- **v0** moved to usage-based credits ([v0 docs](https://v0.app/docs/pricing), [agentrank teardown](https://www.agentrank.tech/blog/v0-pricing-credits-system-what-it-actually-costs)): post-Jan-2026 repricing, **complex generations ≈ $1-4 per prompt** (community-reported, +200-300% vs before); $20/mo Premium = $20 credits. Full-stack generation "can burn a month of credits in a few prompts."
- **Lovable**: flat **1 credit per message** regardless of complexity ([pricing](https://lovable.dev/pricing)); Pro $25/mo = 100 credits + 5/day. So Lovable prices a full site at ~10-40 messages ≈ $2.50-10 of plan value.
- **Anthropic multipliers** ([multi-agent post](https://www.anthropic.com/engineering/multi-agent-research-system)): single agent ≈ **4x** chat tokens; multi-agent ≈ **15x**. Claude Code field data ([cloudzero](https://www.cloudzero.com/blog/claude-code-agents/), [verdent](https://www.verdent.ai/guides/claude-code-pricing-2026)): median ≈ **$6/dev/day** (90% under $12), enterprise avg ≈ $13/day; **multi-agent teams ≈ 7x tokens of a single session**; 3-agent sessions can hit $20-60+/day.
- **Working estimate for an agency-tier pipeline** (intake → research → creative direction → per-section generation → 3-10 grounded critique cycles with screenshots): **plan for low-single-digit millions of tokens per site**, i.e. roughly **$5-25 per site** at mid-2026 Sonnet-class pricing depending on cycle count and screenshot/vision usage **[estimate — derived from Bolt ~3M/app + Anthropic 4-15x multipliers + v0 $1-4/complex-prompt]**. Cost levers proven in production: prompt-cache-stable system prompts (v0), QuickEdit-style routing of small edits to cheap models (v0), critic-free fast paths after training/calibration (ReLook), capped cycles + keep-best (CITL).

---

## 7. Synthesis — recommended architecture for Boss's builder

1. **Staged pipeline with structured artifacts** (Relume + Anthropic harness shape): intake brief → research/creative-direction → sitemap/section plan → DESIGN.md-style design contract → per-section codegen → grounded critique loop → assembly. Context resets + artifact handoffs between stages, not one giant context.
2. **Creative direction as a first-class generated artifact**: tokens (OKLCH palette, type pairing, motion language) + **prose rationale** (DESIGN.md finding: prose measurably improves cross-page consistency) + explicit anti-generic constraints. This is the anti-"shadcn-default-look" lever; 2026 design discourse confirms direction/taste, not generation, is the differentiator ([Anima](https://www.animaapp.com/blog/ai-design-en/graphic-design/), [Creative Bloq](https://www.creativebloq.com/art/digital-art/digital-art-trends-2026-reveal-how-creatives-are-responding-to-ai-pressure)).
3. **Separate Generator from Evaluator** (different agent, ideally different prompt+model). Evaluator = checklist-guided MLLM judge (ArtifactsBench-style rubric: functionality, aesthetics, originality, craft) + Playwright-driven interaction + screenshots at 3 timepoints + multiple viewport sizes (Lovable/WebGen-Agent pattern).
4. **Ground every revision in external evidence**: render success (zero-tolerance for broken renders — ReLook), TS+lint layers, console/network logs, screenshot diffs, GUI-agent click-through. Never ungrounded self-review.
5. **Deterministic fixers around the model**: stream-time icon/URL/import correction + AST autofixers (v0) are cheap and lift error-free rate into the ~94% zone without extra LLM calls.
6. **Parallelism only where independent** (research subagents, per-section spec drafts, asset generation); serial coherent context for code that shares state. Cap critique at 3-5 cycles with keep-best selection; budget ~4-15x chat tokens.

---

### Source index (primary)
- Vercel: [composite model family](https://vercel.com/blog/v0-composite-model-family) · [effective coding agent](https://vercel.com/blog/how-we-made-v0-an-effective-coding-agent) · [design systems + AI](https://vercel.com/blog/ai-powered-prototyping-with-design-systems)
- Anthropic: [multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) · [building agents with Claude Agent SDK](https://claude.com/blog/building-agents-with-the-claude-agent-sdk) · [3-agent harness via InfoQ](https://www.infoq.com/news/2026/04/anthropic-three-agent-harness-ai/)
- Lovable: [Agent Mode](https://lovable.dev/blog/agent-mode-beta) · [leaked prompt](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools/blob/main/Lovable/Agent%20Prompt.txt)
- Papers: [Design2Code 2403.03163](https://arxiv.org/abs/2403.03163) · [WebSight 2403.09029](https://arxiv.org/abs/2403.09029) · [Self-correction 2310.01798](https://arxiv.org/abs/2310.01798) · [METAL 2502.17651](https://arxiv.org/abs/2502.17651) · [WebGen-Bench 2505.03733](https://arxiv.org/abs/2505.03733) · [DesignBench 2506.06251](https://arxiv.org/abs/2506.06251) · [ArtifactsBench 2507.04952](https://arxiv.org/abs/2507.04952) · [ScreenCoder 2507.22827](https://arxiv.org/abs/2507.22827) · [WebGen-Agent 2509.22644](https://arxiv.org/abs/2509.22644) · [ReLook 2510.11498](https://arxiv.org/abs/2510.11498) · [CITL 2604.05839](https://arxiv.org/html/2604.05839v1) · [Design critique 2412.16829](https://arxiv.org/abs/2412.16829)
- Cost: [banani Bolt teardown](https://www.banani.co/blog/bolt-new-pricing) · [v0 pricing docs](https://v0.app/docs/pricing) · [agentrank v0 costs](https://www.agentrank.tech/blog/v0-pricing-credits-system-what-it-actually-costs) · [cloudzero Claude Code](https://www.cloudzero.com/blog/claude-code-agents/)
- Design-system-first: [DESIGN.md analysis](https://wavespeed.ai/blog/posts/design-md-vs-design-tokens-ai-workflows/) · [Hardik Pandya](https://hvpandya.com/llm-design-systems) · [Relume](https://www.relume.io/)
