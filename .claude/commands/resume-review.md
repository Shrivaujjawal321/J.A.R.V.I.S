# /resume-review — Full resume diagnostic + rewrite plan

Run a comprehensive review of Boss's current resume. Highest-leverage workflow.

## Usage

```
/resume-review                  # Review the resume at data/resume/current.{pdf,md,docx}
/resume-review <path>           # Specific file
/resume-review --jd <url|text>  # Score against a specific JD
```

## Workflow

### 1. Find the resume
Look in this order:
- Path argument if provided
- `data/resume/current.md`
- `data/resume/current.pdf`
- `data/resume/current.docx`
- Ask Boss to share if none found

### 2. Load research
- Read `data/notes/resume-research-*.md` (latest)
- If older than 30 days OR missing → dispatch research-agent for a refresh first

### 3. Diagnostic (delegate to resume-agent)
Ask resume-agent to:
- Score across 5 axes (ATS, AI/ML signal, project depth, recency, JD-fit)
- Identify top 3 filtering reasons
- Produce prioritized fix list (P0 → P2)

### 4. (If JD provided) JD-match
Ask resume-agent to:
- Extract keywords from JD
- Score keyword coverage
- Generate concrete "add this line to project X" suggestions

### 5. Synthesize for Boss
Output:
```markdown
# 📄 Resume Review — {date}

## Scorecard
{table}

**Overall: X/50** → {one-line verdict}

## 🚨 Top 3 reasons it's likely getting filtered
1. ...
2. ...
3. ...

## 🛠️ Fix plan (do in this order)
- [ ] **[P0]** {fix} — est: {time}
- [ ] **[P1]** {fix}
- [ ] **[P2]** {fix}

## 🎯 Tonight's mission (if you have 2 hours)
{Single most important fix to do RIGHT NOW}

## Next step
{1-line — usually "let's tackle P0 fix together" or "show me your latest resume"}
```

### 6. Track
- Save diagnostic to `data/resume/diagnostic-{date}.md`
- After Boss confirms a fix is done, `touch data/markers/resume_last_updated` (kills trigger nag)

## Important

- **Be brutally honest.** Boss's resume not working = his income blocked. Soft feedback wastes weeks.
- **One fix at a time.** Don't dump 15 changes. Surface P0 first; deeper fixes after he asks.
- **Concrete rewrites > vague advice.** "Make it more impactful" is useless. "Change line 3 of project X from 'Built ML model' to 'Fine-tuned distilBERT on 12K Reddit samples, achieved 87% F1 (0.12 improvement over baseline)'" is useful.
- **Save Boss's voice.** Match the tone he already uses in projects/portfolio — don't make him sound like LinkedIn.

---

**End-state:** Boss closes this command knowing exactly what to fix tonight, in what order, and with concrete rewrites in hand.
