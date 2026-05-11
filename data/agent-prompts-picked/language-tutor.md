# Language Tutor — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/language-tutor.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** LanguageTutorGPT — Conversation + Flashcard Tutor
**From library:** `data/agent-prompts/language-tutor.md` -> Prompt 1
**Source:** [petehuang gist](https://gist.github.com/petehuang/6dbd1caa6a39aaf85c5722e09481445a)
**Author:** Pete Huang
**License:** MIT (gist default; permissive)

### Full Prompt (verbatim)

```
Act as LanguageTutorGPT. Your job is to have a conversation with me in [TARGET LANGUAGE]. If I write something incorrectly or use phrasing that is not natural, create a flashcard using the right word or phrase. If I'm using basic vocabulary when a more advanced one would fit, suggest the advanced version and create a flashcard. If I write a fragment in English, translate it and create a flashcard.

Triggers for creating a flashcard:
- Correction of incorrect or unnatural phrasing
- Suggestion when my vocabulary is too basic
- Translation of an English fragment I wrote
- I write "fc" followed by a word — create a flashcard for that word

Flashcard format:
First, briefly give the pronunciation guide and English definition. Then output a cloze deletion card:
- Front: a sentence in [TARGET LANGUAGE] with the target word/phrase deleted (replaced by "____")
- Back: the full sentence, English translation, and pronunciation guide

Otherwise, keep the conversation flowing in [TARGET LANGUAGE]. Start at a beginner level and adjust based on my responses. Maintain conversational context across exchanges.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** Clear role + target language slot. Trivial to instantiate per learner.
- **Scope boundaries:** Three flashcard triggers + one explicit user trigger ("fc <word>"). No ambiguity.
- **Output format:** Pinned cloze-deletion flashcard format (front/back, pronunciation + definition) — directly importable to Anki/Mochi.
- **Reasoning techniques:** Conversational practice + just-in-time correction + active-recall card generation. Tightly Socratic-adjacent: corrections come as cards (which force the learner to study), not lectures.
- **Safety / refusal patterns:** Minimal — keeps focus on language, no off-topic drift built in.

### 2026 trend relevance
- **Modern frameworks:** Conversation + SRS (spaced-repetition system) is the proven 2026 language-learning combo (Duolingo Max, Speak, Anki ecosystem).
- **Current tech references:** Cloze format is Anki-native, Mochi-compatible.
- **Structured output:** Cards are machine-parseable — Jarvis can pipe them to a deck file or Notion DB.
- **Safety alignment:** Low risk surface. Adapts difficulty based on learner output (built-in calibration).

### Pedagogical quality (tutoring-specific)
- **Socratic vs. answer-dumping:** Production-based, not lecture-based. Learner produces; tutor corrects with study artifacts (cards). Better than answer-dumping but not pure Socratic — for language, production-with-correction is the right pedagogy (Krashen's i+1).
- **Adapts to student level:** "Start at beginner level and adjust based on my responses" — automatic calibration.
- **Builds understanding vs. dependence:** Cards build a permanent study asset. Every error becomes spaced repetition, not just a one-time fix.

### Deployability
- **License:** MIT — clean to ship, fork, redistribute.
- **Vendor lock:** None.
- **Jarvis adaptability:** Trivial to parametrize TARGET LANGUAGE. Easy to pipe flashcards into Notion (Jarvis already has Notion MCP) or a `data/decks/{lang}.tsv` file.

---

## Runners-up + Trade-offs

### #2: Immersion Roleplay Tutor (Prompt 4)
- **Why not picked:** Most engaging format, but no automatic correction during scene (by design). For a daily-driver tutor, Boss wants both flow AND feedback. Roleplay is best as a separate "scenario mode" agent.
- **When to use this instead:** Intermediate+ learner who needs confidence and cultural fluency. Run alongside Prompt 1 — roleplay session, then debrief in tutor mode.

### #3: Spoken English Teacher (Prompt 2)
- **Why not picked:** Ruthless correction loop is great, but only corrects errors — no proactive vocab uplift, no study-deck side-effect. CC0 license is the safest.
- **When to use this instead:** When Boss wants pure intermediate-English correction practice with no card generation overhead.

### #4: Pronunciation Helper (Prompt 3)
- **Why not picked:** Utility, not a tutor. Output-only.
- **When to use this instead:** Boss helping someone read aloud — pair with the tutor agent.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/language-tutor.md`
2. **Adaptations needed:**
   - Parametrize: `[TARGET LANGUAGE]` -> learner-configured slot. Default Spanish for Boss-adjacent context, but let user override.
   - Generalize pronunciation: replace pinyin-implied flow with "IPA or learner's native-script phonetic approximation."
   - Pipe flashcards: append a hidden instruction — "Also output cards as a JSON array at end of each turn so they can be exported to Anki." Or write to Notion deck.
   - Add "session debrief" trigger: when user types "END," summarize: 5 cards made today, 3 patterns observed.
3. **Tool access (suggested):** Notion write (to deck DB) or file Write to `data/decks/{lang}.tsv`.
4. **Model recommendation:** sonnet for accuracy in correction. haiku for high-volume conversation drilling.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 4/5 | Role + language slot clear; tone implicit. |
| Scope boundaries | 5/5 | Trigger list + format spec — unambiguous. |
| Output format guidance | 5/5 | Cloze card format pinned, Anki-compatible. |
| Reasoning techniques | 4/5 | Production-correction + SRS; not pure Socratic but right-for-domain. |
| Safety / refusal patterns | 3/5 | Minimal — fine for language, no surface risk. |
| 2026 tech relevance | 5/5 | Conversation + SRS is the dominant 2026 paradigm; cards are agent-pipeable. |
| License-friendliness | 5/5 | MIT — clean, redistributable. |
| **Overall** | **31/35** | |
