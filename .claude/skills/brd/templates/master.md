# Master BRD Template

The canonical skeleton. Every generated BRD follows this order. Sections marked **[core]** are
never omitted; sections marked **[conditional]** are included only when the business type or
answers warrant it — and when omitted, the document says so explicitly rather than silently
dropping them.

Tagging convention used throughout the draft:
- `[ASSUMPTION: <statement> | conf: high/med/low]` — inferred, not supplied. Every one of these must also appear in §11.
- `[NEEDS INPUT: <what's missing>]` — a gap that was asked about but not answered, or deferred to round 2.
- `[Stakeholder Requirement — solution TBD in FRD]` — a deliberate Tier-2 grey-zone statement.

---

```markdown
# Business Requirements Document — <Project Name>

## Document Control

| Field | Value |
|---|---|
| Document Title | Business Requirements Document — <Project> |
| Document ID | BRD-<SLUG>-<YYYY>-<NNN> |
| Version | <n.n> |
| Status | Draft / In Review / Approved |
| Author | <name> |
| Business Sponsor | <named person, title> |
| Date Created | <YYYY-MM-DD> |
| Readiness Score | <n>/100 (see §Appendix — Readiness Report) |

**Change Log**

| Version | Date | Author | Change | Approved By |
|---|---|---|---|---|

---

## 1. Executive Summary  [core]

2-3 paragraphs. Written LAST, after everything else exists.
A VP reads this in 90 seconds and knows: what's broken, what's changing, what it's worth, when it lands.
Must contain something that could only be true of THIS project.

## 2. Business Objectives  [core]

3-7 objectives, IDs OBJ-001…, each SMART: number · baseline · target · measurement method · date · owner.
Each objective must be traceable downward to ≥1 requirement (§8) and ≥1 metric (§15).
State any non-negotiable constraint inline (e.g. "…without relaxing the current risk threshold").

## 3. Background / Problem Statement  [core]

Why now. Quantified pain with an attributable source per claim.
Frame as CURRENT STATE + COST OF INACTION — never as blame.
Close with what this document is explicitly NOT deciding.

## 4. Project Scope  [core]

| # | In Scope | # | Out of Scope | Rationale for exclusion |
|---|---|---|---|---|

Both columns mandatory. Every exclusion states WHY and where the work went instead.
Every item carries a phase/version tag and a MoSCoW priority.

## 5. Stakeholder Analysis + RACI  [core]

| Stakeholder | Role | Interest | Influence | RACI (Requirements sign-off) | RACI (UAT sign-off) |
|---|---|---|---|---|---|

Named people, not departments. Exactly one **A** per column. State the escalation path for conflicts.
If names are genuinely unknown, use `[NEEDS INPUT: name of the <role>]` — never invent a person.

## 6. Current State (As-Is) Process  [core]

Numbered steps by swimlane, `<phase>.<step>`. Annotate pain points AT the failing step, with a metric.
Each pain point ties numerically back to a claim in §3.

## 7. Future State (To-Be) Process  [core]

Mirror §6's numbering 1:1 so a reviewer can diff side by side.
Business-process level only — not UI, not system design.
Show what changes, disappears, or gets automated; tie each to a BR-ID.

## 8. Business Requirements  [core]

| ID | Requirement | Traces to | Priority | Source | Acceptance |
|---|---|---|---|---|---|

IDs BR-001…. Each: atomic, verifiable, business-language, MoSCoW-prioritized, traced UP to an
objective, sourced to a named person or elicitation event, and pointing DOWN to acceptance criteria.
Requirements needing more detail get the expanded block form (see exemplars).

## 9. Functional Requirements Boundary  [core]

One paragraph, not a section of requirements:
"Detailed functional requirements are out of scope for this document and will be maintained in the
companion FRD. This BRD defines business need and outcome only."

## 10. Non-Functional Requirements  [core]

| ID | Category | Requirement | Target | Measurement Method |
|---|---|---|---|---|

Business-level only. Format: `<attribute> <operator> <threshold> <unit>, measured via <method>, under <conditions>`.
Categories considered: performance · scalability · availability · security · usability · compliance ·
maintainability · portability · retention · localization · accessibility.
**Explicitly state which categories were considered and judged not applicable, and why.**

## 11. Assumptions Register  [core]

| # | Assumption | Owner | Validation Date | Impact if Wrong | Confidence |
|---|---|---|---|---|---|

IDs ASM-001…. Every `[ASSUMPTION]` tag anywhere in the document appears here. Falsifiable,
owned, dated. An assumption with no owner is a guess written down formally.

## 12. Dependencies  [core]

| # | Dependency | Owning team | Expected date | Impact if late |
|---|---|---|---|---|

## 13. Constraints  [core]

Hard numbers only — budget ceiling, go-live date, regulatory deadline, untouchable legacy system.
"Limited budget and time" is not a constraint.

## 14. Risk Register  [core]

| ID | Description | Probability (1-5) | Impact (1-5) | Score | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|---|

Cross-link risks to the assumptions they depend on.

## 15. Success Metrics / KPIs  [core]

| Metric | Baseline | Target | Measurement Method | Measurement Date | Owner | Traces to |
|---|---|---|---|---|---|---|

**Loop-closing check: every number here must already appear in §2 or §3.** A new number appearing
first in this table means the document was stitched together.

## 16. Acceptance Criteria  [core]

Both altitudes:
- Given/When/Then per requirement (AC-BR014.1 …) — maps 1:1 to a future test case
- A go-live readiness checklist referencing requirement IDs and sign-off authority

## 17. Cost-Benefit / Business Case  [conditional — include unless Boss says skip]

Separate INVESTMENT from RUN-RATE (and disclose if the new run-rate is higher).
Quantified benefits, then payback/ROI table, then a downside case,
then unquantified benefits quarantined separately — never folded into the ROI.
Include "do nothing" as an evaluated alternative.

## 18. Glossary  [core]

Every domain term and acronym used ≥3 times. Alphabetized. Business and technical terms both.

## 19. Appendices  [conditional]

Labeled, referenced from the body, each with a one-line purpose statement.

## 20. Sign-off / Approval Matrix  [core]

| Name | Role | Approving WHAT exactly | Date |
|---|---|---|---|

Named individuals with dates. State precisely what each signature covers — "business requirements
only" vs "full BRD including budget". Ambiguous sign-off scope is what re-opens disputes later.

---

## Appendix — Readiness Report

Auto-generated. Score, per-criterion breakdown, top fixes, and the honesty caveat.
```

---

## Generation order (not document order)

Draft in this order, then assemble into the order above:

1. §3 Problem → §2 Objectives (objectives must answer the problem)
2. §6 As-Is → §7 To-Be (to-be must mirror as-is)
3. §8 Requirements (must trace to §2)
4. §4 Scope, §10 NFRs, §5 Stakeholders
5. §11-14 registers (assumptions, dependencies, constraints, risks)
6. §15 Metrics — **reconcile against §2 and §3, do not introduce new numbers**
7. §16 Acceptance, §17 Business case, §18 Glossary, §20 Sign-off
8. §1 Executive Summary — **last**

Stanford's own template enforces this bottom-up discipline: you cannot finish the summary until the
detail exists. Writing top-down and never reconciling is exactly how the numbers drift.
