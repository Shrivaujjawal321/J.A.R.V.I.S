# Jarvis Agent Prompt Library

> Curated system prompts for AI agents across professions where AI augments or replaces human work.
> Source: GitHub repos, public prompt libraries, leaked-and-open agent prompts.

**Last bootstrap:** 2026-05-11
**Maintained by:** `prompt-curator-agent`
**Add new:** `/prompt-library <profession>`

**📊 Library size:** 25 professions, 101 curated prompts

---

## Index

### 💻 Tech & Engineering (20 prompts)
- [Software Developer](software-developer.md) — 5 prompts
- [Web Designer / Frontend Developer](web-designer.md) — 4 prompts
- [UI/UX Designer](ui-ux-designer.md) — 3 prompts
- [Code Reviewer](code-reviewer.md) — 4 prompts
- [DevOps / SRE](devops-sre.md) — 4 prompts

### ✍️ Content & Creative (21 prompts)
- [Copywriter](copywriter.md) — 4 prompts
- [Content Writer (Long-form)](content-writer.md) — 4 prompts
- [SEO Specialist](seo-specialist.md) — 5 prompts
- [Social Media Manager](social-media-manager.md) — 4 prompts
- [Technical Writer](technical-writer.md) — 4 prompts

### 💼 Business & Sales (20 prompts)
- [Sales SDR / BDR](sales-sdr.md) — 4 prompts
- [Executive Assistant](executive-assistant.md) — 4 prompts
- [Customer Support](customer-support.md) — 4 prompts
- [Marketing Strategist](marketing-strategist.md) — 4 prompts
- [Recruiter / HR](recruiter-hr.md) — 4 prompts

### 🔬 Knowledge Work (18 prompts)
- [Research Analyst](research-analyst.md) — 4 prompts
- [Data Analyst](data-analyst.md) — 4 prompts
- [Financial Analyst (basic)](financial-analyst.md) — 3 prompts ⚠️ NOT-advice disclaimer required
- [Legal Assistant](legal-assistant.md) — 4 prompts ⚠️ NOT-legal-advice disclaimer required
- [Tutor / Teacher](tutor.md) — 4 prompts

### 🧘 Personal & Lifestyle (17 prompts)
- [Life Coach](life-coach.md) — 3 prompts ⚠️ NOT-therapy disclaimer + crisis escalation
- [Fitness Coach](fitness-coach.md) — 4 prompts ⚠️ NOT-medical disclaimer
- [Travel Planner](travel-planner.md) — 3 prompts
- [Nutritionist (basic)](nutritionist.md) — 3 prompts ⚠️ NOT-RD disclaimer
- [Career / Resume Coach](career-coach.md) — 4 prompts

---

## How to Use This Library

1. **Browsing:** Open any `.md` file → ranked prompts with full text + source + license + use-case notes
2. **Deploying:** Copy a prompt → adapt to Jarvis context → save as `.claude/agents/{new-agent}.md` (add Jarvis safety rules + memory file references)
3. **Adding:** Run `/prompt-library {new-profession}` — prompt-curator-agent will research and save a new file

## Source Quality Distribution

**Verbatim-and-licensed (safe for direct use):**
- `f/awesome-chatgpt-prompts` — CC0 (public domain)
- `mustvlad/ChatGPT-System-Prompts` — MIT
- `TracyWang95/legal-prompts-for-gpt` — MIT
- `Troyanovsky/AI-Professional-Prompts` — CC BY-SA 4.0
- `VoltAgent/awesome-claude-code-subagents` — MIT
- OpenAI Cookbook — MIT
- Anthropic Customer Support Guide, Financial Services Agents — Apache 2.0
- `thatrebeccarae/claude-marketing` — MIT

**Leaked / inspiration-only (do not redistribute commercially):**
- Cursor IDE, v0, Devin AI, GitHub Copilot Chat — from `jujumilk3/leaked-system-prompts` + `EliFuzz/awesome-system-prompts`
- CoppieGPT, Etsy SEO Expert, Sofia (XML technical writer), Fully SEO Optimized Article — from various leaked-Custom-GPT repos
- Customer Service GPT, Executive f(x)n — from `linexjlin/GPTs`
- Khanmigo Lite — described pattern only (verbatim refused at source)

**Rejected (documented in-file with reasoning):**
- "Legal Advisor" from awesome-chatgpt-prompts — framing demands advice in real-stakes scenarios, unfixable with safety wrapper
- HormoziGPT — no-disclosure clause makes verbatim citation impossible
- Various manipulative sales prompts — flagged with ethical warnings + consultative alternatives offered

## Curation Discipline

Every prompt in this library has:
- **Verbatim text** quoted from source (or explicitly noted when reconstructed)
- **Source URL** for verification
- **License** stated honestly (Unknown when uncertain)
- **"Why it works"** annotation (techniques used, what makes it strong)
- **"Best for"** annotation (specific use case)
- **"Limitations"** annotation (where it falls short)

Sensitive professions (legal, financial, medical-adjacent, mental health) require:
- Top-level disclaimer
- Refusal patterns for out-of-scope queries
- Crisis-escalation block where applicable

## License Note

Each prompt in the library has a stated license. Respect it. For commercial / customer-facing deployment, prefer CC0 / MIT / Apache 2.0 prompts. The leaked-prompt section is for **inspiration when building your own** — Vercel's CTO publicly endorsed studying their v0 prompt; using it as a base is standard practice. Redistributing it as-is in a commercial product is not.

## Quality Bar

- **3-5 prompts per profession** — top picks only, no padding
- **Verbatim text** wherever possible
- **Annotated** — every prompt earns its place
- **Diverse approaches** — zero-shot vs. few-shot, terse vs. verbose, generalist vs. specialist
