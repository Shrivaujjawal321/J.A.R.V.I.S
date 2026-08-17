# BRD Readiness Rubric — 0-100

The scoring spec. Every criterion and weight traces to a named source; nothing here is invented.
Full sourcing in `data/research/brd-system/02-quality-rubric-and-defects.md`.

**Score honestly.** If a BRD is a 61, report 61. Never round up to make the output look good.
A flattering score destroys the only thing that makes this system useful — the gap it points at.

---

## Scoring architecture — three layers, in this order

| Layer | What it does | False positives | Run order |
|---|---|---|---|
| **L1 — Structural** | Relational integrity over parsed entities (orphans, missing fields, broken IDs). Deterministic. | Zero | First — cheapest and certain |
| **L2 — Lexical/smell** | Trigger-word and pattern matching from INCOSE R7/R8/R9/R26/R32/R33 + Femmer smell taxonomy | High — published precision ≈0.59 | Second |
| **L3 — LLM judge** | Semantic checks only: is the metric genuinely the success measure, is this claim real, is this hallucinated | N/A | Third, and it **filters L2** |

⚠️ **Critical calibration rule.** The published NLP smell detector (Smella) scores precision 0.59 /
recall 0.82 — it over-flags roughly 4 in 10. **Never let raw L2 hit-counts drive the score.**
Every L2 flag must be confirmed or dismissed by L3 before it costs points. Under-flagging is
acceptable; a score wrecked by false positives is not.

---

## The 10 criteria (total 100)

| # | Criterion | Weight | Layer |
|---|---|---|---|
| 1 | Objectives are SMART / measurable | 12 | L1 + L3 |
| 2 | Requirements are atomic & unambiguous | 15 | L2 → L3 |
| 3 | Requirements are verifiable | 15 | L2 → L3 |
| 4 | NFRs present and quantified | 10 | L1 + L2 |
| 5 | Scope explicit, bounded, prioritized | 12 | L1 |
| 6 | Traceability graph integrity | 12 | L1 |
| 7 | Stakeholder / RACI completeness | 8 | L1 |
| 8 | Risk & assumption management | 8 | L1 |
| 9 | Terminology consistency / glossary | 5 | L1 + L2 |
| 10 | Business alignment & non-hallucination | 3 | L3 only |

**Deviation from the research brief, stated openly:** the source rubric proposed NFR=12 and
Scope=10. This skill uses NFR=10 and Scope=12. Reason: the source rubric was pitched at
SRS-grade documents where NFR engineering is the main event. In a **BRD**, full NFR specification
legitimately belongs downstream in the FRD/SRS, while a missing Out-of-Scope section is the #1
BRD-specific rejection driver in the practitioner literature. Weight follows where the failure
actually happens. All other weights are unchanged from the researched allocation.

---

## Criterion 1 — Objectives are SMART / measurable · 12 pts

Per objective, score 7 checks (each worth an equal share of the criterion):

1. Contains a **number** (target), not just a direction ("increase", "improve", "reduce")
2. Names the **metric / instrument** used to measure it
3. Has a **deadline or window**
4. Names an **accountable owner** (person or role)
5. States a **baseline** — the current value the delta is measured from
6. Target is **achievable** given the constraints stated elsewhere in the doc
7. Traces to a **business driver** in one clause

An objective failing checks 1-3 is **not measurable** — score it near zero regardless of how good
the prose is.

L3 must additionally confirm the metric is genuinely the objective's success measure and not an
incidental number that happens to appear in the sentence.

**Weak → strong:**
> ✗ "Improve customer satisfaction."
> ✓ "Increase CSAT from 72 (Q2 2026 baseline, quarterly survey) to ≥85 by Q4 2026, owned by Head of CX."

---

## Criterion 2 — Requirements are atomic & unambiguous · 15 pts

Full marks: zero compound requirements, zero vague pronouns, zero subjective language, active
voice with a named actor throughout.

**L2 detection patterns:**

- **Compound / non-atomic** (INCOSE R18/R19) — `and` · `or` · `then` · `unless` · `while` joining
  independent obligations; multiple verb phrases; comma-separated distinct obligations under one ID
- **Vague pronouns** (R24) — `it` · `this` · `that` · `which` · `they` whose antecedent is more than
  one clause away or has 2+ candidates
- **Subjective language** — `user-friendly` · `robust` · `intuitive` · `efficient` · `modern` ·
  `seamless` · `flexible` · `scalable` (when used without a number)
- **Passive voice hiding the actor** (R2/R3) — "shall be validated" / "will be processed" with no
  named responsible subject
- **Parenthetical requirement content** (R21) — normative content inside parentheses gets silently
  dropped in review
- **Purpose phrases** (R20) — rationale language inside the normative statement

**Weak → strong:**
> ✗ "The system shall allow users to register, log in, and reset passwords, and shall send a confirmation email for each."
> ✓ Split into four atomic requirements, each independently testable and traceable.

---

## Criterion 3 — Requirements are verifiable · 15 pts

Full marks: every requirement carries a quantified, testable target with unit and tolerance; zero
escape clauses, zero open-ended clauses, zero unbaselined superlatives/comparatives.

**L2 trigger-word lists — apply verbatim, these come straight from INCOSE:**

- **R7 Vague terms** — `some` · `any` · `allowable` · `several` · `many` · `a lot of` · `a few` ·
  `almost always` · `very nearly` · `nearly` · `about` · `close to` · `almost` · `approximate`
- **R8 Escape clauses** — `so far as is possible` · `as little as possible` · `where possible` ·
  `as much as possible` · `if it should prove necessary` · `if necessary` · `to the extent necessary` ·
  `as appropriate` · `as required` · `to the extent practical` · `if practicable`
- **R9 Open-ended clauses** — `including but not limited to` · `etc.` · `and so on`
- **R26 Absolutes** — `100%` · `zero defects` · `always` · `never` · `all` (unless genuinely verifiable)
- **R32 Quantifiers** — prefer `each` (distributive, testable per instance) over `all` / `any` / `both`
- **R33 Tolerances** — a bare quantity with no range/tolerance ("around 200ms" → "between 200ms and 250ms")
- **Superlatives** — `best` · `highest` · `lowest` · `fastest` · `optimal` without a defined metric
- **Comparatives without baseline** — `faster` · `better` · `more accurate` · `higher` with no named
  comparison point
- **Uncertain verbs** — `may` · `can` · `might` where obligation was intended

**On negative statements:** "shall not / must never" used as a lazy substitute for a positive
measurable requirement is a defect. A genuine safety or compliance prohibition ("the system shall
not store card CVV") is **not** a defect. L3 makes this call — do not penalize it at L2.

---

## Criterion 4 — NFRs present and quantified · 10 pts

Coverage checked against the ISO/IEC 25010-aligned category list. Score = (categories addressed
with a quantified threshold) ÷ (categories *applicable* to this business type). Do not penalize a
BRD for omitting a category that genuinely does not apply — but require it to say so.

Categories: performance · scalability · availability · security · usability · compliance ·
maintainability · portability · data retention · localization · accessibility.

**Required format:**
`<measurable attribute> <operator> <numeric threshold> <unit>, measured via <method/tool>, under <conditions>`

A quantified NFR **missing the "measured via" clause is still weak** — verifiability requires
stating how it will be checked, not just the number.

> ✗ "The system shall be secure."
> ✓ "The system shall enforce TLS 1.2+ for all traffic, encrypt PII at rest (AES-256), and pass an annual third-party penetration test with zero critical/high findings open beyond 30 days."

Remember the tier boundary: a BRD carries **business-level** NFRs (regulatory obligations, volume
expectations, availability the business needs). Deep engineering NFRs belong in the SRS. Do not
reward a BRD for smuggling in SRS-grade NFR detail — that costs points under criterion 10.

---

## Criterion 5 — Scope explicit, bounded, prioritized · 12 pts

Three sub-checks:

1. **Both directions present** (6 pts) — In-Scope *and* Out-of-Scope sections both exist and are
   non-empty. A missing or empty Out-of-Scope section is a **hard structural defect**, not a
   stylistic nicety. Mechanism: scope creep is defined as out-of-scope work added without formal
   review; with no written exclusions list there is nothing for a change-control gate to gate
   against.
2. **Prioritized** (3 pts) — scope items carry MoSCoW (Must / Should / Could / Won't) or equivalent.
   A flat undifferentiated list gives no signal for scope-cut decisions under schedule pressure.
3. **Bounded language** (3 pts) — no open-ended clauses in scope lines ("and other related
   features"), no vague capability statements as line items ("improve the user experience" instead
   of a concrete deliverable), and every item carries a phase/version tag.

Extra credit signal (not scored, but flag it as strong): each out-of-scope item states **why** it
is excluded and where it went ("Mobile redesign — Phase 2, per roadmap 2026-03").

---

## Criterion 6 — Traceability graph integrity · 12 pts

Pure L1. Zero false positives, so build and run this first. Each check is pass/fail across the
document; the criterion scores as the proportion passed.

1. **Orphan requirements** — any requirement with no link to a business objective
2. **Barren objectives** — any objective with zero requirements tracing to it (a stated goal with
   no execution plan)
3. **Missing acceptance criteria** — any requirement with no defined "done" condition
4. **Missing verification method** — per ISO 29148's four V&V methods (test / inspection / analysis
   / demonstration)
5. **Duplicate requirement IDs**
6. **Broken ID references** — a traceability link pointing at an ID that does not exist
7. **Missing priority tag** — every requirement carries MoSCoW (Wiegers treats *Prioritized* as a
   first-class quality attribute, not a PM nicety)

Both directions matter. Public RTM guidance covers downward traceability (requirement → test)
well and **upward traceability (requirement → objective) poorly** — this skill scores both, and
upward failures are the ones that reveal a BRD nobody can justify.

---

## Criterion 7 — Stakeholder / RACI completeness · 8 pts

1. Every listed stakeholder appears at least once in the RACI matrix (set difference over names)
2. **Every RACI row has exactly one Accountable** — zero or 2+ "A"s is a structural defect, not a
   style preference
3. Stakeholders are **named people or specific roles**, not departments ("Finance" is not a
   stakeholder; "Priya Nair, Financial Controller" is)
4. An escalation path exists for RACI conflicts

---

## Criterion 8 — Risk & assumption management · 8 pts

**Risks** — each entry has: category · description · likelihood · impact · mitigation · owner · status.
Any risk with an empty mitigation or no owner fails.

**Assumptions** — each entry has: statement · owner · validation date · impact-if-wrong. An
assumption without an owner is just a guess written down formally.

This is where LLM-drafted BRDs quietly fail: they state assumptions as fact. Every assumption this
system generates must be visibly tagged and owned, never smuggled into the body as established
truth.

---

## Criterion 9 — Terminology consistency / glossary · 5 pts

- Every domain term used ≥3 times appears in the Glossary (INCOSE R4 / R36)
- No term carries two conflicting definitions across sections
- Acronyms defined on first use, used consistently after (R37)
- Consistent units throughout (R6)

This is the single most common way a requirements **set** fails ISO 29148's *Consistent*
characteristic — which is exactly why the Glossary is mandatory rather than decorative.

---

## Criterion 10 — Business alignment & non-hallucination · 3 pts

**L3 only.** Deliberately low-weight because it is the least certifiable — but it must exist,
because otherwise a beautifully-formatted fabrication scores 100.

Zero marks for any of:
- Fabricated stakeholder names or titles
- Invented regulations, standards, or clause numbers that do not exist
- **Invented metrics** — a specific-sounding number with no stated source. This is the dangerous
  one: criterion 3 rewards "has a number", so an ungrounded "shall respond within 200ms" would
  otherwise score *well*. It must be caught here.
- Generic filler sections with no business specificity
- Solution-language creep (INCOSE R31) — prescribing implementation instead of stating need
- Internal contradictions or near-duplicate requirements

**The axis rule:** structural quality and business validity are separate axes. A document can be
structurally excellent and still be wrong about what the business needs. Never let a high total
score imply the requirements are *correct* — only that they are *well-formed*. Say this explicitly
in the score report.

---

## Reporting format

```
BRD Readiness: 68/100

  ✓ Traceability integrity      12/12
  ✓ Stakeholder / RACI           8/8
  ~ Scope explicit & bounded     8/12   — Out-of-Scope present but unprioritized, 3 items untagged
  ~ Objectives SMART             7/12   — OBJ-002 and OBJ-004 have no baseline
  ✗ Requirements verifiable      6/15   — 9 of 22 requirements have no measurable target
  ...

  Top 3 fixes to reach 85+:
  1. Add baselines to OBJ-002, OBJ-004                          → +4
  2. Quantify BR-007, BR-011, BR-014, BR-018 (no target today)  → +6
  3. Tag all scope items with MoSCoW                            → +3

  Caveat: this score measures how well-FORMED the document is, not whether the
  requirements are CORRECT for your business. 14 assumptions remain unvalidated —
  see the Assumptions Register.
```

Always end with the caveat. Always name the specific IDs. "Improve your objectives" is exactly
the kind of unverifiable feedback this rubric exists to eliminate.
