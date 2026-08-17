# BRD Standards Reference — operational

Distilled from `data/research/brd-system/01-standards-and-structure.md`. That file holds
full sourcing; this file is what you actually apply at runtime.

---

## 1. The tier rule (BABOK v3) — decides what belongs in a BRD

| Tier | Name | Answers | Goes in BRD? |
|---|---|---|---|
| 1 | Business Requirements | WHY the change | **Yes — this is the BRD's core** |
| 2 | Stakeholder Requirements | WHAT each stakeholder needs | **Yes, at capability level only** |
| 3 | Solution Requirements (Functional + Non-Functional) | HOW the solution behaves | **No** — FRD/SRS. BRD carries only business-level NFRs (regulatory, volume, availability expectations) |
| 4 | Transition Requirements | HOW we get from as-is to to-be | **Outcome only** ("legacy data must migrate with zero loss"), never mechanism |

**Important honesty note:** ISO/IEC/IEEE 29148:2018 does not define "BRD" as a formal artifact
at all. Its five named types are StRS, SyRS, SRS, **BRS**, and OpsCon. What industry calls a
"BRD" is a hybrid of BRS + StRS. This is *why* BRD scope varies wildly between orgs — and why
this skill fixes one canonical structure (§3) rather than pretending a universal one exists.

---

## 2. Requirement quality characteristics (ISO/IEC/IEEE 29148:2018)

These are the criteria every individual requirement statement must satisfy. The rubric scores
against them directly.

**Individual requirement — 9 characteristics:**

1. **Necessary** — removing it leaves a genuine gap, not just a lost nice-to-have
2. **Appropriate** — detail level matches the document tier (no SRS detail in a BRD)
3. **Unambiguous** — exactly one interpretation. "increase website speed" ✗ → "reduce page load to under 1 second" ✓
4. **Complete** — no further amplification needed; thresholds/conditions are in the statement itself
5. **Singular** — one requirement per statement; "shall do X **and** Y" is a smell → split
6. **Feasible** — achievable within real technical/budget/schedule constraints
7. **Verifiable** — provable true/false by inspection, test, analysis, or demonstration. Bans "user-friendly", "fast", "intuitive" without a number
8. **Correct** — accurately reflects the real stakeholder need
9. **Conforming** — follows consistent template/wording style

**Requirement SET — 5 characteristics:**

1. **Complete** — no gaps across the set
2. **Consistent** — no contradictions; uniform terminology (**this is why the Glossary is mandatory** — inconsistent terminology is the most common way a set fails)
3. **Feasible** — implementable *together*, not just individually
4. **Comprehensible** — business stakeholders can understand it unaided
5. **Able to be validated** — every requirement traces to a real source, not a fabrication

> Source caveat: the standard is paywalled; the list and substance are corroborated across
> multiple secondary sources but are paraphrase, not verbatim ISO text. Do not quote as verbatim.

**Recommended per-requirement attributes:** ID · Heading · Text · Owner · Priority · Source ·
Rationale · Type · Status · Verification Method.

---

## 3. Canonical BRD section anatomy (20 sections)

Order matters. Sections marked ⚡ are the ones reviewers reject BRDs over.

| # | Section | Must contain | Typical length |
|---|---|---|---|
| 1 | Executive Summary | Problem, change, outcome, timing — plain English. **Write this LAST.** | 150-300 words |
| 2 | ⚡ Business Objectives | SMART goals; each maps to ≥1 KPI in §15 | 3-7 objectives |
| 3 | Background / Problem Statement | Why now — quantified pain with named source, business trigger | 0.5-1.5 pg |
| 4 | ⚡ Scope — In / **Out** | Numbered in-scope AND numbered out-of-scope, each exclusion with a reason | 0.5-1 pg |
| 5 | Stakeholder Analysis + RACI | Named people, role, influence, R/A/C/I per deliverable, escalation path | 0.5-1 pg |
| 6 | Current State (As-Is) | Numbered flow + pain points annotated at the exact failing steps, with metrics | 0.5-1.5 pg |
| 7 | Future State (To-Be) | Process at business level; show what changes/disappears/automates, tied to BR-IDs | 0.5-1.5 pg |
| 8 | ⚡ Business Requirements | Table: ID / Statement / Linked Objective / Priority (MoSCoW) / Source / AC pointer | 2-6 pg — the core |
| 9 | Functional Requirements boundary | One paragraph: "detailed FRs live in the companion FRD". **Not a section of FRs.** | 1 para |
| 10 | Non-Functional Requirements | Business-level quality + regulatory only, quantified, each traced to a business risk | 0.5 pg |
| 11 | ⚡ Assumptions | Falsifiable, with owner + validation date + impact-if-wrong | 0.25-0.5 pg |
| 12 | Dependencies | Named dependency, owning team, expected date, impact if late | 0.25-0.5 pg |
| 13 | Constraints | Hard numbers — budget cap, go-live date, untouchable legacy system | 0.25-0.5 pg |
| 14 | Risks | Category, description, likelihood, impact, mitigation, owner, status | 0.5-1 pg |
| 15 | ⚡ Success Metrics / KPIs | Baseline + target + measurement method + cadence + owner, tied to Objective IDs | 0.5 pg |
| 16 | Acceptance Criteria | Per-BR, testable, seeds UAT | 1-2 pg (may be appendix) |
| 17 | Cost-Benefit / Business Case | Build + run cost, quantified benefit, payback, alternatives **including do-nothing** | 0.5-1.5 pg |
| 18 | Glossary | Every domain term and acronym, defined once | 0.5-1 pg |
| 19 | Appendices | Labeled, referenced from body, each with a purpose line | variable |
| 20 | Sign-off / Approval Matrix | Name / Role / **what exactly they approve** / Date. Ambiguous sign-off scope causes later disputes | 0.25 pg |

Plus a **Document Control** block at the top: version, author, date, status, change log, approvers.

---

## 4. The solution-language boundary — the single most-violated rule

**The test:** a BRD sentence must survive being read by someone with zero knowledge of the
eventual technology and still make complete sense as a business need.

- Answers "what does the business need to achieve" → **BRD**
- Answers "what must the system do to make that happen" → **FRD/SRS**
- Names a specific UI element, field, table, API, algorithm, or vendor → **never BRD**

Worked classifications:

| Sentence | Verdict |
|---|---|
| "Reduce average complaint resolution time to improve retention." | BRD |
| "Support managers need to see at a glance which regions miss SLA." | BRD (Tier 2) |
| "As a support manager I want a dashboard so I can identify weak regions." | PRD |
| "The system shall display a bar chart of SLA by region, refreshed every 15 min." | FRD |
| "Widget shall query `region_sla_summary` and cache in Redis for 15 min." | SRS |
| "All customer financial data must comply with DPDP Act 2023." | BRD |
| "Field-level encryption on `pan_number` using AES-256." | SRS |
| "Legacy records must migrate from the mainframe before go-live with zero data loss." | BRD (Tier 4 outcome) |
| "A nightly NiFi job shall load VSAM records into the PostgreSQL `customers` table." | FRD/SRS |
| "The claims process must reduce manual reconciliation steps from 7 to ≤2." | BRD (legit grey zone) |

**The honest grey zone** is Tier 2. "The system needs to flag high-risk transactions in real
time" is business-flavoured but implies a mechanism. Handle it by (a) keeping it at *capability*
level — "must flag", not "must show a red banner via WebSocket" — and (b) tagging it explicitly
as `[Stakeholder Requirement — solution TBD in FRD]` so a reviewer sees the line was drawn
deliberately, not sloppily.

---

## 5. ID and traceability conventions

Prefixes: `BR-` business · `STK-` stakeholder · `FR-` functional · `NFR-` non-functional ·
`TR-` transition · `OBJ-` objective · `ASM-` assumption · `RSK-` risk · `KPI-` metric ·
`DEP-` dependency · `CON-` constraint. Zero-padded 3 digits (BR-001). Decomposition nests
(BR-001 → FR-001.1).

**RTM columns:** Requirement ID · Description · Source · **Linked Business Objective** ·
Priority · Owner · Type · Status · Linked Solution Element · Linked Test Case · Verification
Method · Regulatory Reference.

⚠️ **Deliberate design point:** most public RTM guidance covers *downward* traceability
(requirement → test case) well and *upward* traceability (requirement → business objective)
poorly. This skill treats upward traceability as mandatory — an orphan requirement (no linked
objective) and a barren objective (no supporting requirement) are both scored defects.

---

## 6. Why real BRDs get rejected — screen for all ten

1. Vague, untestable requirements ("user-friendly", "improve efficiency")
2. **Solution language leaking in** — the #1 boundary violation
3. No explicit out-of-scope section
4. No measurable success criteria / KPIs
5. Broken traceability — requirements not tied to an objective, or objectives with no requirements
6. Unvalidated assumptions stated as fact, with no owner to verify them
7. No sign-off matrix, or ambiguous sign-off scope ("did I approve the budget or just read it?")
8. Passive, over-technical language business approvers cannot genuinely validate → rubber-stamping
9. Stale BRD — no change control after approval
10. Problem-statement framing disputes — writing a BRD is a *negotiation* disguised as a writing
    task. Expect the problem statement to be rewritten twice, and expect the sharpest pushback
    from someone who is factually correct but frames the problem differently. Design for
    iterative reframing, not one-shot approval.
