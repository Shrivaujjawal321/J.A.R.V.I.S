# /prompt-library — Manage the agent system-prompt library

Add new professions to Jarvis's reusable system-prompt library, or list what's already there.

## Usage

```
/prompt-library                        # List current library contents
/prompt-library <profession>           # Add or refresh a profession
/prompt-library <prof1>, <prof2>, ...  # Batch add multiple
```

## What This Does

Delegates to `prompt-curator-agent` to:
1. Search GitHub + curated prompt libraries for high-quality system prompts for the profession
2. Evaluate and pick top 3-5 prompts
3. Save to `data/agent-prompts/{profession-slug}.md`
4. Update the library index at `data/agent-prompts/README.md`

## Workflow

### Mode: List (no argument)
- Read `data/agent-prompts/README.md` if exists
- Show categorized list: profession → number of prompts → file path
- Surface "biggest gaps" — categories where Boss has 0 or only 1 profession covered
- End with: "Want to add a profession? Use `/prompt-library <name>`"

### Mode: Single profession
- Slugify the profession name (lowercase, hyphenated)
- Check if `data/agent-prompts/{slug}.md` already exists
  - **If yes:** ask if Boss wants to refresh (add new prompts) or replace entirely
  - **If no:** dispatch prompt-curator-agent to create from scratch
- Delegate to prompt-curator-agent with clear scope: "Find 3-5 high-quality system prompts for {profession}. Follow output format spec in your definition."
- After agent returns, surface a summary:
  - File path created/updated
  - Number of prompts collected
  - Top recommendation (the "Quick-Pick")

### Mode: Batch
- Dispatch multiple prompt-curator-agent calls **in parallel**
- Surface a single consolidated summary at the end

## Output to Boss

```markdown
## 📚 Prompt Library Update

**Added:** {profession} → {N} prompts saved to `data/agent-prompts/{slug}.md`

**Top pick:** Prompt {N} — {1-line why}

**Sources mined:**
- {source 1}
- {source 2}
- {source 3}

## Next Steps
- Use this library to spin up a specialist agent: copy a prompt into `.claude/agents/{new-agent}.md` with Jarvis-specific tweaks
- Or ask: "Jarvis, make me a {profession} agent" → I'll do the integration
```

## Hard Rules

- **Never edit prompts from the library when copying to an agent file** without explicit purpose (e.g., adding Jarvis-specific safety rules). Library = sources; agent files = derivatives.
- **Always pass to prompt-curator-agent** — don't try to research yourself. That agent has the quality criteria baked in.
- **Respect licenses** noted in each prompt file. Some leaked prompts are not commercial-safe.

---

**End-state:** Boss can think of any role on Earth, type `/prompt-library {role}`, and 5 minutes later have a curated, ranked, cited list of best system prompts for that role — ready to deploy as a Jarvis specialist agent.
