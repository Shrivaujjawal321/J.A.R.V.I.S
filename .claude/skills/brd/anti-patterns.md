# Anti-patterns — never do these

Every item here is a documented failure mode. The first six are how BRDs get rejected by review
boards. The last six are how **LLM-written** BRDs specifically fail — read those twice, because
this system is an LLM writing a BRD.

---

## Part 1 — classic BRD rejection triggers

### 1. Solution language in a BRD

> ❌ "We will build a React SPA with a PostgreSQL backend and integrate Salesforce via REST API to solve the underwriting bottleneck."
>
> ✅ "The solution shall allow an underwriter to review a complete applicant record — including bureau data and decision rationale — from a single interface, without navigating between systems."

Locking a tech stack into a document whose whole purpose is to stay solution-agnostic robs the
delivery team of the architecture choice, and makes the BRD stale the moment the tech decision
changes even though the business need hasn't. **INCOSE R31: Solution-Free.**

### 2. Unmeasurable objectives

> ❌ "Improve the customer experience and make the loan process more efficient."
>
> ✅ "Reduce average origination cycle time from 9.4 to 3.0 business days by Q2 FY27, measured via the LOS pipeline-stage timestamp report."

The bad version can never be disputed as done or not-done. No baseline, no target, no date, no
method. This is the single most frequently cited anti-pattern across every source.

### 3. Missing out-of-scope section

> ❌ Five in-scope bullets and no "Out of Scope" heading at all.
>
> ✅ A table where every exclusion states **why** and where the work went instead.

Silence on scope reads as "undecided", and undecided items resurface as change requests mid-project.
Without a written exclusions list, the change-control gate has nothing to gate against.

### 4. Copy-paste filler

> ❌ "This document outlines the business requirements for the project. It defines scope, objectives, and requirements to ensure successful delivery aligned with organizational goals."
>
> ✅ "Meridian's loan origination requires 14 manual data-entry touches per application, driving a 9.4-day cycle against a 2.1-day competitor median. This BRD defines the requirements to reach 3.0 days and cut compliance exceptions from 6.2% to under 1.0%, without prescribing the replacement platform's architecture."

**The filler test:** could this sentence be dropped unmodified into an unrelated BRD and still make
sense? If yes, delete it.

### 5. Vague NFRs

> ❌ "The system must be fast, secure, and highly available."
>
> ✅ "p95 response <3s under 150 concurrent sessions; 99.9% uptime during business hours (≤43 min/month); AES-256 at rest, TLS 1.2+ in transit."

QA cannot write a test case against an adjective, and no vendor can be held to an SLA against one.

### 6. Stakeholders with no names

> ❌ "Stakeholders: IT, Business, Compliance, Risk."
>
> ✅ "Meredith Voss, Head of Compliance — Interest: High (Reg B exposure) — Influence: High — RACI on requirements sign-off: Consulted."

A department cannot sign off, cannot be escalated to, and cannot be held accountable. Without a
named individual, "stakeholder approval" is unverifiable and later disputes ("Compliance never
approved this") are unresolvable.

---

## Part 2 — how LLM-written BRDs fail

These come from published empirical evaluation of LLM-generated requirements documents. They are
this system's native failure modes.

### 7. Hallucination and fabrication

Generating requirements that reference features, systems, or metrics never present in any input.
**Rule:** if it wasn't in Boss's input, an answered question, or a cited source, it is an assumption
and must be tagged `[ASSUMPTION]` with an owner — never written as established fact.

### 8. Invented metrics — the dangerous one

"The system shall respond within 200ms" with no source for why 200ms.

This is dangerous **specifically because the rubric rewards having a number**. Criterion 3 scores a
quantified requirement highly, so a fabricated threshold scores *well* while being worthless. It has
to be caught by criterion 10.

**Rule:** every number in the document is one of three things — (a) supplied by Boss, (b) derived
from a supplied number with the derivation shown, or (c) tagged `[ASSUMPTION — industry default,
unvalidated]`. There is no fourth category. A confident unsourced number is worse than a blank.

### 9. Generic filler content

LLMs produce vague boilerplate *systematically*, not occasionally, because generic text is a safer
next-token continuation than specific text. Every section must contain something that could only be
true of this project.

### 10. Solution-oriented language creep

LLMs default to prescribing a specific technology or design because it makes for a more
"complete-sounding" continuation than staying abstract. Fight this actively — it is not an
occasional slip, it is the model's default gradient.

### 11. Internal inconsistency and near-duplicates

Generated sets contradict themselves and restate the same requirement under two IDs. Long documents
make it worse — context degrades as length grows.

**Check before finalizing:** do the numbers in Success Metrics match the numbers in Objectives and
the Problem Statement? Mismatch is the classic tell of a stitched-together document.

### 12. Padding to signal effort

Turning a small-scope request into a 40-page document. Length must track complexity, not effort.
Small initiative = 5-10 pages. Reviewers penalize padding as hard as they penalize omission.

---

## The meta-rule

> **Structural quality and business validity are separate axes.**

A BRD can be structurally excellent — perfect IDs, full traceability, quantified everything — and
still be completely wrong about what the business needs. Research on LLM-generated requirements
found exactly this: RE experts rated LLM output "acceptable to high" on structural criteria, while
the researchers cautioned that true requirements must originate from or be validated by the
customer.

Never let a high readiness score imply the requirements are **correct**. It only means they are
**well-formed**. Say so explicitly, every time a score is reported.
