# /braindump — Capture a random thought, route it correctly

Boss said something random. Jarvis figures out where it goes.

## Usage

```
/braindump <whatever's on your mind>
```

Examples:
- `/braindump Cursor ke bare mein research karna hai` → research-agent task
- `/braindump remind me to call mom Sunday` → task-agent
- `/braindump idea: voice interface for Jarvis using whisper` → ideas log + project consideration
- `/braindump I'm feeling burnt out` → mood log + suggest break
- `/braindump Anisha ko bol dena Friday plan` → anisha-agent draft

## Workflow

### 1. Parse intent
Classify the dump into one of:
- **Task** ("remind me", "do this", "I need to") → task-agent
- **Research question** ("kya hai", "kaise karna", "compare", "find") → research-agent
- **Idea** (new project, feature, improvement) → log to `data/notes/ideas.md`
- **Person-related** (message draft, gift, plan) → relevant agent (anisha-agent / email-agent)
- **Mood/feeling** ("burnt out", "low", "excited", "stressed") → log to `data/notes/mood-log.md` + respond appropriately
- **Decision-needed** ("should I do X or Y") → present options with WHY
- **Memory worth saving** (preference, fact, habit) → memory-agent
- **Mixed** — break into pieces, route each

### 2. Route + confirm
Don't just silently file it. Show Boss what you did:
```markdown
## 🧠 Captured

**You said:** "{dump}"

**I parsed it as:** {classification}

**Action taken:**
- {what was routed where}
- {anything saved}

**Next:** {recommendation, if any}
```

### 3. If ambiguous
Ask ONE clarifying question (per Boss's preference — single question). Don't overthink it.

## Hard Rules

- **Don't lose anything.** If you can't classify, log to `data/notes/braindump.md` with timestamp and surface for review later.
- **Be fast.** This is a capture tool, not an interview. Get it parked, give a 1-line confirmation, move on.
- **No advice unless asked.** If Boss says "feeling burnt out" — log it, gently surface a break suggestion, but don't lecture.

## Why This Exists

Boss has thoughts all day. Without capture, they're lost. With this, every thought lands somewhere useful — task list, ideas pile, agent inbox, or mood log. Compounding personal data over time = smarter Jarvis tomorrow.

---

**End-state:** Boss can dump anything, anytime, and trust it goes to the right place.
