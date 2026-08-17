---
name: brd
description: Turns a short business-idea paragraph into a professional-grade Business Requirements Document. Drafts speculatively, detects its own gaps, asks Boss only the blocking questions, then scores the result 0-100 against a sourced rubric and loops until it clears the bar. Use when Boss says /brd, asks for a BRD / business requirements doc / requirements document, or wants an idea turned into a formal spec.
---

# /brd — Business Requirements Document engine

Boss gives a paragraph. This produces a BRD a review board would accept — or tells him honestly
how far short it falls and exactly what's missing.

**The system is not a document generator.** Writing prose is the easy part. The hard part is that a
two-line idea is missing ~15 things a BRD must answer, and a naive generator invents them
confidently. This is an **elicitation and gap-detection engine** that happens to emit a document.

---

## Load before acting

| File | When |
|---|---|
| `references/standards.md` | Always — tier rules, ISO 29148 characteristics, section anatomy, ID conventions |
| `references/elicitation.md` | Before gap detection and before asking anything |
| `references/exemplars.md` | Before drafting any section — this is the quality bar |
| `rubric.md` | Before scoring |
| `anti-patterns.md` | Before drafting AND before finalizing |
| `templates/master.md` | At draft assembly |

Business-type variants live in `references/elicitation.md` §6 — that table is the variant spec
(which sections get heavier, which extra sections appear, which questions become mandatory).

---

## Commands

```
/brd "<idea paragraph>"     start a new BRD
/brd_status <slug>          score + open gaps for an in-progress BRD
/brd_resume <slug>          continue an unfinished interview
/brd_score <path>           score any existing BRD file against the rubric
```

---

## File layout

```
data/brd/<slug>/
  intake.md          Boss's original paragraph + any context supplied
  classification.md  business type, domain, compliance surface, template variant
  draft-v1.md        speculative draft, everything unknown tagged
  gaps.json          detected gaps, scored and ranked
  answers.md         Boss's answers, verbatim
  BRD-v2.md          regenerated after answers
  score.json         per-criterion breakdown
  README.md          one-screen status: score, version, open gaps
```

Slug = kebab-case from the idea (`freelance-invoice-chaser`). If it collides, suffix `-2`.

---

## The flow

### Step 1 — Intake

Write Boss's paragraph verbatim to `intake.md`. Do not paraphrase or "improve" it — the original
wording is evidence, and the specific words he chose carry signal about what he actually cares about.

### Step 2 — Classify

Determine and write to `classification.md`:

- **Business type** — from the taxonomy in `elicitation.md` §6
- **Compliance surface** — which trigger rows in `elicitation.md` §5 plausibly match. Only these become candidate questions; never surface all of them.
- **Initiative size** — small (5-10pp) / medium (15-25pp) / large (30-60pp). This is a **budget, not a target.** Padding is a scored defect.
- **Solution-stated-without-problem?** — if the paragraph names a solution ("an app that…", "a dashboard for…") with no problem, flag it. A Five Whys ladder becomes a mandatory blocking question.

### Step 3 — Draft (5 agents, one batch)

Dispatch in a **single tool block** so they run concurrently. Every agent gets: the intake, the
classification, `references/exemplars.md`, and `anti-patterns.md`.

| Agent | Owns |
|---|---|
| `business-analyst-agent` | §2 Objectives · §3 Problem · §8 Business Requirements · §16 Acceptance |
| `business-analyst-agent` (2nd, separate brief) | §6 As-Is · §7 To-Be · §4 Scope |
| `compliance-officer-agent` | §10 NFRs (regulatory) · compliance constraints · retention · audit-trail requirements |
| `product-manager-agent` | §5 Stakeholders + RACI · §15 Success Metrics · §12-13 Dependencies & Constraints |
| `strategy-consultant-agent` | §17 Cost-Benefit · §14 Risks · §11 Assumptions |

**Every agent operates under one hard rule, stated in its brief:**

> If it wasn't in the input, an answered question, or a cited source, it is an ASSUMPTION. Tag it
> `[ASSUMPTION: <statement> | conf: high/med/low]` inline. Never state it as fact. A confident
> unsourced number is worse than a blank.

Assemble into `draft-v1.md` per `templates/master.md`, following the **generation order** at the
bottom of that file — problem before objectives, as-is before to-be, executive summary last.

### Step 4 — Gap ledger

A critic pass over the draft (`business-analyst-agent`, fresh context, adversarial brief). It runs:

- The **12-category gap checklist** (`elicitation.md` §3)
- Every `[ASSUMPTION]` and `[NEEDS INPUT]` tag in the draft
- The compliance triggers matched in Step 2
- The mandatory questions for this business type

Each gap is scored **Reversibility (1-3) × Assumption-confidence (1-3)** per `elicitation.md` §1
and written to `gaps.json`:

```json
{
  "id": "GAP-003",
  "category": "user-roles",
  "question": "Kaun-kaun log ise use karenge, aur har type kya kar sakta hai?",
  "example_answer": "e.g. 'sirf main aur mera accountant — accountant sirf dekh sakta hai, edit nahi'",
  "reversibility": 3,
  "confidence": 3,
  "score": 9,
  "blocking": true,
  "fallback_assumption": "Single admin user, no role separation",
  "affects": ["BR-004", "BR-011", "NFR-05"]
}
```

`blocking` = score ≥ 6. Everything below becomes a documented assumption — **do not ask it.**

### Step 5 — Interview

**Hard ceiling: 10 questions.** If more than 10 gaps score ≥6, take the top 10 by score and defer
the rest to a round 2 after the draft improves. Never extend round 1 — completion-rate data is
unambiguous that long intakes get abandoned.

Rules (full detail in `elicitation.md` §7):

- **One question at a time.** Wait for the answer before the next.
- **Plain Hinglish**, respectful register. Never "aapke non-functional requirements kya hain" — instead "kitne log ek saath ise use karenge?"
- **Always give an example answer inline.** It anchors both scale and format.
- **Always offer the escape hatch:** *"pata nahi — koi sensible default maan lo."* Then show which default you picked, tagged, in the draft.
- Order **easy → hard**, low-stakes → high-stakes.
- Soft progress: "3 of about 8".
- **After the last question, list what you did NOT ask and assumed instead** — so Boss can challenge it before the document is finalized.

Answers go to `answers.md` verbatim.

### Step 6 — Regenerate and score

Fold the answers in. Resolved gaps move out of the ledger and their `[ASSUMPTION]` tags are replaced
with sourced statements (`Source: Boss, 2026-07-29`). Unresolved ones move into §11 Assumptions
Register with an owner and a validation date.

Then score against `rubric.md`, in layer order:

1. **L1 structural** — deterministic integrity checks. Zero false positives. Run first.
2. **L2 lexical** — INCOSE trigger-word lists and smell patterns. **Over-flags by design** (published precision ≈0.59).
3. **L3 judge** — semantic only, and **it filters L2**. No raw L2 hit ever costs points until L3 confirms it.

Write `score.json` and report:

```
BRD Readiness: 68/100
  ✓ Traceability integrity      12/12
  ~ Scope explicit & bounded     8/12  — 3 scope items untagged
  ✗ Requirements verifiable      6/15  — 9 of 22 have no measurable target

  Top 3 fixes to reach 85+:
  1. Add baselines to OBJ-002, OBJ-004                → +4
  2. Quantify BR-007, BR-011, BR-014, BR-018          → +6
  3. Tag all scope items with MoSCoW                  → +3

  Caveat: this measures how well-FORMED the document is, not whether the
  requirements are CORRECT. 14 assumptions remain unvalidated.
```

**If score < 85:** name the specific fixes and offer round 2. Do not silently loop — Boss decides
whether the remaining delta is worth more questions.

**If score ≥ 85:** deliver, still stating open assumptions.

### Step 7 — Deliver

`BRD-v2.md` (or `-v3`…) plus the readiness report. Offer PDF/docx export only if Boss asks; the
markdown master is the source of truth.

---

## Non-negotiables

1. **Never guess silently.** Every inference is a tagged, owned, dated assumption visible in §11. This is the whole reason the system exists.
2. **Never let a number in without provenance.** Boss-supplied, derived-with-derivation-shown, or tagged as an unvalidated default. There is no fourth category. Fabricated thresholds are the LLM failure mode most likely to survive scoring — the rubric rewards *having* a number, so an invented one scores well while being worthless.
3. **Never exceed 10 questions in a round.**
4. **Never report a flattering score.** 61 is 61. A score that hides the gap destroys the only thing that makes this useful.
5. **Never claim a high score means the requirements are correct.** Structural quality and business validity are separate axes. Say so every time.
6. **Never let solution language into the BRD.** This is the model's default gradient, not an occasional slip — a specific tech choice is always a more "complete-sounding" continuation than staying abstract. Fight it actively.
7. **Never pad.** Length tracks complexity. Reviewers penalize padding as hard as omission.
8. **Say what you cannot do.** Workshops, observation, and focus groups are not reproducible through Q&A. When a requirement genuinely needs the ops team in a room, say that instead of asking three more questions.

---

## Provenance

Built 2026-07-29 from four parallel research briefs in `data/research/brd-system/`:
`01-standards-and-structure.md` (BABOK v3, ISO/IEC/IEEE 29148:2018, section anatomy, rejection
patterns) · `02-quality-rubric-and-defects.md` (INCOSE 42 rules, Femmer requirements-smells
taxonomy, LLM-generated-requirements failure modes, the weighted rubric) ·
`03-elicitation-and-gap-detection.md` (question banks, gap heuristics, blocking score, compliance
triggers, interview UX data) · `04-real-templates-and-exemplars.md` (Stanford/IIBA/BC-Gov/CAISO
templates, worked exemplars, MoSCoW discipline).

Those files carry the citations and the `[unverified]` flags. When something here is challenged,
go back to them rather than re-deriving from memory.
