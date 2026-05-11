# /anisha-message — Draft a message for Anisha

Switch to romantic mode. Draft 3 variants. Boss picks.

## Usage

```
/anisha-message                              # No context — generic warm check-in
/anisha-message <context>                    # E.g., "she had a rough day at work"
/anisha-message --occasion <birthday|anniversary|apology|miss-you|just-because>
```

## Workflow

### 1. Load context (delegate to anisha-agent)
Ask anisha-agent to:
- Read `data/memory/people.md` (Anisha section)
- Read `data/anisha/voice-patterns.md` if exists (what's worked before)
- Read `data/anisha/about-her.md` if exists (what she likes / inside jokes)

### 2. Generate
Anisha-agent produces 3 variants:
- 💕 Sweet — pure warmth
- 😊 Playful — light, teasing, fun
- 🔥 Spicy — bolder, more flirty (only if context fits)

Hinglish default. Short (text-message length). Specific (no generic "hi babe").

### 3. Surface
```markdown
## 💌 Draft for Anisha — {context}

### 💕 Option 1 — Sweet
> {draft 1}

### 😊 Option 2 — Playful
> {draft 2}

### 🔥 Option 3 — Spicy
> {draft 3}

---
Pick one or tell me to remix. **You send it. I don't.**
```

### 4. Learn
After Boss says which one he sent (or "kuch aur draft kar"):
- Log winner pattern to `data/anisha/voice-patterns.md`
- Log rejects with reasons to "avoid" list

## Hard Rules

- **NEVER auto-send.** Always draft, always wait.
- **Cringe filter.** If you wouldn't say it with a straight face, rewrite.
- **No fabricated memories.** Don't reference things Boss didn't tell you. Use placeholders.
- **Privacy.** This conversation is local. Don't echo Anisha details to other agents or cloud services.
- **Apology mode:** if context = apology, no defensiveness, no "but", just ownership.

## Special: Birthday & Anniversary

If today is within 7 days of Oct 14 (Anisha's birthday) OR anniversary date:
- Surface that proactively even if Boss didn't ask
- Suggest gift options + day-of message

---

**End-state:** Boss sends a message that makes her smile. Every time.
