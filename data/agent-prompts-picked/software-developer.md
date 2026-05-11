# Software Developer — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 7 candidates in `../agent-prompts/software-developer.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Aider Coding Agent
**From library:** `data/agent-prompts/software-developer.md` -> Prompt 6
**Source:** [Aider-AI/aider](https://github.com/Aider-AI/aider/blob/main/aider/coders/base_coder.py)
**Author:** Paul Gauthier and Aider contributors
**License:** Apache-2.0

### Full Prompt (verbatim)

```
Act as an expert software developer.
Always use best practices when coding.
Respect and use existing conventions, libraries, etc that are already present in the code base.

Take requests for changes to the supplied code.
If the request is ambiguous, ask questions.

Always reply to the user in the same language they are using.

Once you understand the request you MUST:

1. Decide if you need to propose *SEARCH/REPLACE* edits to any files that haven't been added to the chat. You can create new files without asking!

But if you need to propose edits to existing files not already added to the chat, you *MUST* tell the user their full path names and ask them to *add the files to the chat*. End your reply and wait for their approval. You can keep asking if you then decide you need to edit more files.

2. Think step-by-step and explain the needed changes in a few short sentences.

3. Describe each change with a *SEARCH/REPLACE block* per the examples below. All changes to files must use this *SEARCH/REPLACE block* format. ONLY EVER RETURN CODE IN A *SEARCH/REPLACE BLOCK*!

4. *Concisely* suggest any shell commands the user might want to run in ```bash blocks.

Just suggest shell commands this way, not example code.
Only suggest complete shell commands that are ready to execute, without placeholders.
Only suggest at most a few shell commands at a time, not more than 1-3.

Use the appropriate shell based on the user's system info.

Examples of when to suggest shell commands:
- If you changed a self-contained html file, suggest an OS-appropriate command to open a browser to view it to see the updated content.
- If you changed a CLI program, suggest the command to run it to see the new behavior.
- If you added a test, suggest how to run it with the testing tool used by the project.
- Etc.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Act as an expert software developer" in line 1 — unambiguous, immediate.
- **Scope boundaries:** Explicit — must ask before editing files not in chat; must use SEARCH/REPLACE blocks; only code in those blocks; only 1-3 shell commands per turn.
- **Output format:** Pinned hard — SEARCH/REPLACE blocks for edits, ```bash blocks for runnable commands. Grounded in real file content, not free-form prose.
- **Reasoning techniques:** "Think step-by-step and explain the needed changes" before producing diffs. Forces CoT before action.
- **Safety / refusal patterns:** "If the request is ambiguous, ask questions" — refuses to guess. "Respect and use existing conventions" prevents code-fabrication.
- **Examples / few-shot:** References examples (the full Aider prompt includes worked SEARCH/REPLACE examples in surrounding code).

### 2026 trend relevance
- **Modern frameworks:** Diff-format output is the dominant 2025-2026 pattern for agentic edits (Claude Code, Aider, Cline all use variants). Future-proof.
- **Current tech references:** Language-agnostic — no outdated tech assumptions.
- **Structured output:** SEARCH/REPLACE is parseable, machine-applyable. Chainable with a diff-applier subagent.
- **Safety alignment:** "Ask before editing" + "concisely suggest commands, no placeholders" prevents runaway tool loops.

### Deployability
- **License:** Apache-2.0 — full commercial reuse permitted. No proprietary-leaked baggage.
- **Vendor lock:** None — works on Claude, GPT, Gemini, local models. Aider supports all three.
- **Jarvis adaptability:** Drop-in as a code-agent subagent. Pair with file-read/file-write MCP tools. The SEARCH/REPLACE pattern is already understood by every major code-edit tool.

---

## Runners-up + Trade-offs

### #2: Cline Autonomous Coding Agent (Prompt 7)
- **Why not picked:** Apache-2.0 and also great, but heavier (~10K tokens with all sections) and tightly coupled to Cline's XML tool-call format. More work to retarget for Jarvis tools.
- **When to use this instead:** When building a full computer-use coding agent (browser, shell, filesystem) from scratch where Cline's RULES + CAPABILITIES sections give you a head start.

### #3: Cursor IDE Agent (Prompt 1)
- **Why not picked:** Proprietary-leaked. Brilliant XML-section structure (`<communication>`, `<making_code_changes>`, `<debugging>`) but legally murky to ship. Best used as a *structural reference* for a Jarvis-original prompt, not deployed verbatim.
- **When to use this instead:** Read it to learn the imperative-prohibition pattern; harvest the `<debugging>` rules into a Jarvis-original derivative.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/code-agent.md`
2. **Adaptations needed:**
   - Keep verbatim — already concise and tool-agnostic.
   - Optionally append a Jarvis-specific section: "When working in `/home/ujjwal/Documents/J.A.R.V.I.S./`, respect the existing memory/agent file conventions (see CLAUDE.md)."
   - Replace SEARCH/REPLACE with native Edit tool semantics if using Claude Code's Edit tool — but the discipline (read-before-edit, ask before touching unlisted files) carries over.
3. **Tool access (suggested):** Read, Edit, Write, Bash, Glob, Grep.
4. **Model recommendation:** sonnet — best balance of speed and reasoning for everyday coding. Escalate to opus for architecture-heavy or debugging-heavy tasks.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | First line nails it. |
| Scope boundaries | 5/5 | Explicit do/don't on file edits, shell commands, ambiguity handling. |
| Output format guidance | 5/5 | SEARCH/REPLACE blocks + bash blocks — parseable. |
| Reasoning techniques | 4/5 | "Think step-by-step" present; not multi-stage like CoT-heavy prompts. |
| Safety / refusal patterns | 4/5 | Asks on ambiguity; no harm-policy refusals (not needed for code). |
| 2026 tech relevance | 5/5 | Diff-format edits are the modern standard. |
| License-friendliness | 5/5 | Apache-2.0, fully commercial-safe. |
| **Overall** | **33/35** | |
