# /brd — Business Requirements Document engine

Boss ek paragraph deta hai. Jarvis ek professional-grade BRD nikaalta hai — ya honestly batata hai
ki kitna short pad raha hai aur exactly kya missing hai.

## Usage

```
/brd "<idea paragraph>"     nayi BRD shuru karo
/brd_status <slug>          score + open gaps
/brd_resume <slug>          adhoori interview continue karo
/brd_score <path>           kisi bhi existing BRD ko rubric pe score karo
```

Examples:
- `/brd freelancers ke liye ek tool jo unpaid invoices automatically chase kare`
- `/brd internal tool for our ops team to track machine downtime across 3 plants`
- `/brd_score data/brd/invoice-chaser/BRD-v2.md`

## What happens

1. **Intake** — paragraph verbatim save
2. **Classify** — business type, compliance surface, size budget
3. **Draft** — 5 agents parallel, har unknown `[ASSUMPTION]` tag ke saath
4. **Gap ledger** — critic pass, har gap ko Reversibility × Confidence score
5. **Interview** — sirf blocking gaps (score ≥6), max 10, ek-ek karke, Hinglish
6. **Regenerate + score** — 0-100 rubric, per-criterion breakdown, top fixes
7. **Deliver** — `data/brd/<slug>/BRD-v2.md` + readiness report

## Rules Jarvis follows

- Kabhi chup-chaap guess nahi — har assumption tagged, owned, dated, visible
- Har number ka source hona chahiye — Boss ka diya, derive kiya, ya "unvalidated default" tagged
- Max 10 questions per round — isse zyada hua to round 2, round 1 lamba nahi
- Score honest — 61 hai to 61 bolega
- High score ka matlab "well-formed" hai, "correct" nahi — ye har baar batayega

Full contract: `.claude/skills/brd/SKILL.md`
