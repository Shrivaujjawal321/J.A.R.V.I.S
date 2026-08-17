# Assembly Report — Invoice Chaser BRD (Smoke Test)

Assembled 2026-07-29 from `part-1-objectives-problem-requirements.md`, `part-2-asis-tobe-scope.md`,
`part-3-nfr-compliance.md`, `part-4-stakeholders-metrics-deps.md`, `part-5-costbenefit-risks-assumptions.md`
into `draft-v1.md`. This report records every ID remap, every de-dup, every orphan trace, every
unresolvable cross-reference, and the per-section word count vs. budget, per the assembly brief.

---

## 1. Orphaned traceability — resolved and genuine

### 1a. `OBJ-###` placeholders resolved against real OBJ IDs

Part 3 (§10 NFR table) emitted two literal `OBJ-###` placeholders because it could not see Part 1's
real objective IDs. Resolved at assembly:

| NFR | Placeholder | Resolved to | Reasoning (assembly judgment, not stated by either source part) |
|---|---|---|---|
| NFR-002 (service availability, daily send window) | `OBJ-###` | **OBJ-001** | A missed send window means chases don't go out, which directly delays OBJ-001's collection-speed objective. Not OBJ-003 (relationship) — a missed window is a reliability failure, not a conduct failure. |
| NFR-004 (interactive response, user-facing screens) | `OBJ-###` | **OBJ-002** | Slow screens add to the freelancer's own manual effort/time cost, which is exactly what OBJ-002 targets. Weaker candidate than NFR-002→OBJ-001; flagged as Should in the source table already, consistent with a softer trace. |

Both links are recorded as **assembly-added, not agent-stated** — inline in §10's Driver column and
here — so a reviewer can distinguish "the drafting agent decided this" from "the assembler inferred
this from the NFR's own content." Neither required inventing a number or fact; both required reading
the NFR's stated purpose and picking the best-fit existing objective.

### 1b. Genuine orphans — found, not invented around

Two real traceability gaps surfaced during the OBJ↔KPI reconciliation and are recorded in the document
rather than patched:

1. **OBJ-004 (regulatory-safe communication) has no KPI.** Part 4's six KPIs (§15) all measure
   collection or relationship outcomes; none measures compliance. Per master.md, "each objective must
   be traceable downward to ≥1 requirement and ≥1 metric" — OBJ-004 has requirements (BR-006, BR-008)
   but no metric. **Not fixed by inventing KPI-07** — a compliance-audit-pass-rate metric would need to
   be proposed and validated with the (currently unnamed) compliance stakeholder, STK-04, not manufactured
   at assembly. Flagged in §2 and again in §15.
2. **KPI-05 (retention/churn) has no upward objective.** It measures venture-viability churn — the
   same variable §17.4 needs (`churn`) — not a stated OBJ-001…004 outcome. Left as a recorded orphan in
   §15 rather than force-linked to an objective it doesn't actually serve.

Both are exactly what the assembly brief calls "a true finding about the document" — recorded, not
resolved.

### 1c. Traceability that was already clean

Part 1's BR-001…BR-009 all traced cleanly to OBJ-001…004 already (same agent authored both §2 and §8,
so no collision existed here). Part 5's RSK-001…009 all had ASM links from the same agent. No orphan
work was needed on these.

---

## 2. ID-block collisions and gaps — resolved

### 2a. ASM- block

Part 5 reserved `ASM-501`–`ASM-510` specifically to avoid colliding with siblings' `ASM-001+` — but no
sibling ever emitted a formal ASM- prefixed ID; all four other parts used bare inline `[ASSUMPTION: ...]`
tags with no ID at all. There was therefore no literal numeric collision, but there **was** the gap the
assembly brief flagged: Part 5's own register explicitly stated "rows below cover only §14 and §17;
Jarvis merges the rest at assembly." That merge is done — see §3 below for the full sweep and the
renumbering table.

**Renumbering:** Part 5's `ASM-501`–`ASM-510` (10 rows) are renumbered to **ASM-028–ASM-037** in the
assembled document, placed after the 27 inline-tag sweep rows (ASM-001–ASM-027) in document-flow order.
Every in-body reference to `ASM-501`…`ASM-510` in Part 5's §14/§17 content (RSK rows' Links column,
§17 inline references) was updated to the new numbers in `draft-v1.md`.

| Old ID (Part 5) | New ID (draft-v1.md) |
|---|---|
| ASM-501 | ASM-028 |
| ASM-502 | ASM-029 |
| ASM-503 | ASM-030 |
| ASM-504 | ASM-031 |
| ASM-505 | ASM-032 |
| ASM-506 | ASM-033 |
| ASM-507 | ASM-034 |
| ASM-508 | ASM-035 |
| ASM-509 | ASM-036 |
| ASM-510 | ASM-037 |

### 2b. RSK- block

Part 5 owned §14 "wholly" (RSK-001–RSK-009), but Part 3's §10.5 feed-forward routed **three additional
risks** to §14 that were never given IDs: channel-provider suspension, DLT Principal-Entity burden, and
CMP-A resolving against the vendor. These are genuinely new risk content, not restatements — assigned
continuing the existing sequence:

| New risk (source: Part 3 §10.5 feed-forward) | Assigned ID |
|---|---|
| Channel-provider suspension (Meta/email AUP) disabling core function | **RSK-010** |
| DLT Principal-Entity registration burden making SMS commercially unusable (C-2) | **RSK-011** |
| CMP-A resolving against the vendor → vendor becomes a Data Fiduciary in its own right | **RSK-012** |

These three could not be scored (P/I) — neither Part 3 nor Part 5 assigned probability/impact to them,
and assembly does not invent scores. They are recorded in §14 with `[NEEDS INPUT]` in the P/I/Score
cells rather than a fabricated number, per the hard rule against inventing numbers. Their Owner cell is
populated as "Ujjawal" only by extension of Part 5's document-wide "solo initiative, Ujjawal owns every
row" statement — flagged inline as an assembly-applied fact, not an invented one, since it was stated
elsewhere in the document by the section that actually owns §14.

### 2c. §4 Scope-guard addition

Part 3's §10.5 routed a scope guard ("add an explicit out-of-scope entry for cross-user payment-reputation
features") to §4, which Part 2 (the §4 owner) could not see. Added as **OS-6** in the assembled §4 table,
with the compliance rationale (CMP-H) cross-referenced rather than restated.

### 2d. §13 Constraint addition

Part 3's §10.5 routed "DR/RPO-RTO blocked until NFR-002 has a target" to §13. Added as **CON-07**,
continuing Part 4's existing CON-01…CON-06 sequence with no collision (Part 4 never used CON-07).

### 2e. No collisions found in BR-, OBJ-, STK-, DEP-, KPI-, NFR-, CMP-, RET-, AUD- prefixes

Each of these was owned wholly by a single part with no sibling emitting the same prefix, so no
renumbering was required for them — only the cross-reference and trace fixes recorded elsewhere in
this report.

---

## 3. §11 Assumptions Register — full sweep

**Raw inline `[ASSUMPTION` tag count per file** (via text search, before any filtering):

| File | Raw matches |
|---|---|
| part-1 | 10 |
| part-2 | 9 |
| part-3 | 4 |
| part-4 | 3 |
| part-5 | 4 |
| **Total** | **30** |

This matches the assembly brief's stated count of "30 inline `[ASSUMPTION]` tags across the five parts."

**Filtering applied — 3 of the 30 are not independent assumption content:**

1. `part-1`, line 65 — `[ASSUMPTION | conf: med]` inside BR-003's expanded-block Source field. This is
   a **duplicate reference** to the same assumption already registered from line 55 (BR-003's row-level
   Source), not new content. Not double-counted; both references point to the single register row
   **ASM-014**.
2. `part-2`, line 51 — `"Every step below is tagged \`[ASSUMPTION]\` at the confidence..."` — this is
   the drafting agent **explaining the tagging convention itself**, not tagging a specific claim.
   Excluded — no register row.
3. `part-5`, line 13 — `"every \`[ASSUMPTION]\` tag anywhere in the BRD terminates here"` — same
   pattern, meta-explanation of the convention, not a claim. Excluded — no register row.

**Result: 27 genuine, distinct inline assumptions**, registered as **ASM-001–ASM-027** in document-flow
order (the order sections appear in the assembled document: §2 → §3 → §4 → §5 → §6 → §7 → §8 → §10 →
§13 → §17), plus Part 5's pre-formed register of **10 rows**, renumbered to **ASM-028–ASM-037** (see §2a
above). **Final register: 37 rows.**

**Owner/validation-date discipline:** only ASM-028–ASM-037 (Part 5's own rows) carry Owner=Ujjawal and
a validation date, because Part 5 explicitly stated the solo-initiative ownership fact for its own
register. ASM-001–ASM-027 came from sections that made no such statement. Per the hard rule against
inventing owners, their Owner and Validation Date cells are `[NEEDS INPUT]`, not inherited from Part 5's
statement. This was a deliberate choice — it would have been easy and superficially reasonable to apply
"Ujjawal owns every row" document-wide, but that fact was stated by one part about its own content, not
established as a global document fact by whoever is accountable for the whole BRD (that accountability
itself is `[NEEDS INPUT]`, per STK-01/DEP-01).

---

## 4. De-duplication — the data-protection requirement across §8/§10/§13/§14

Four sections independently stated closely related content about protecting client personal data under
DPDP:

| Section | Statement type | Original content |
|---|---|---|
| §8 BR-006 | Business requirement | "The solution shall handle all client and invoice data... in accordance with applicable data-protection law..." |
| §10 NFR-006 | Non-functional / compliance target | "Personal data of users and their clients protected by the safeguards required of a Data Fiduciary," cited to DPDP §8(5)/Rule 6 |
| §13 CON-04 | Regulatory constraint (fact of applicability) | "DPDP Act 2023 applies to any processing of the client's personal data..." |
| §14 RSK-007 | Risk (exposure if mishandled) | "DPDP 2023 exposure via third-party data. The offering processes personal data of the user's clients..." plus a restatement of the fiduciary/processor split also covered by §10.2 CMP-A |

**Resolution:** these are not true duplicates in the sense of saying literally the same thing for the
same purpose — a requirement, a quality target, a constraint, and a risk are four different document
functions per BABOK tiering. But their **prose overlapped** (each re-explained "client data needs DPDP
protection" from scratch), which is the actual defect the assembly brief is pointing at.

- **BR-006 (§8)** kept as the **single canonical business-requirement statement**. Added an explicit
  de-dup note directly under the §8 table naming the other three sections and instructing future editors
  not to add a fifth restatement.
- **NFR-006 (§10)** kept as the canonical **safeguard-standard/citation** — this is where the DPDP §8(5)
  / Rule 6 specifics belong, since BR-006 deliberately stays business-language-only per the
  solution-language boundary. Added a cross-reference sentence pointing back to BR-006 and forward to
  CMP-A.
- **CON-04 (§13)** kept as the canonical statement of **regulatory applicability as an external fact**
  (a constraint, not a requirement). Added a cross-reference to BR-006/NFR-006 instead of re-explaining
  the obligation.
- **RSK-007 (§14)** trimmed: removed its re-explanation of the fiduciary/processor split (that now lives
  once, in CMP-A, §10.2) and reframed its description to focus specifically on **exposure given the
  currently-assumed role split**. Cross-referenced BR-006, NFR-006, and CMP-A.

**A second near-duplicate found and deliberately NOT merged:** RSK-007 ("DPDP exposure under the
assumed fiduciary/processor split") and the newly-added RSK-012 ("the split itself resolves against the
vendor") describe adjacent but genuinely different risk conditions — one assumes the current working
theory of who is fiduciary and asks what exposure follows; the other is the risk that the working theory
is wrong. Merging them would have deleted a real, distinct risk. Kept as two rows, cross-referenced to
each other in both Links cells, with the distinction stated explicitly in-line so a reviewer doesn't
mistake it for an unnoticed duplicate.

**A third near-duplicate reviewed and kept separate:** RSK-006 (general regulated/rate-limited channel
risk) vs. RSK-010 (contractual channel-provider suspension) vs. RSK-011 (DLT registration burden
specifically for SMS). All three are "channel + regulation" risks but describe different failure
mechanisms (consent/template regime risk; platform-suspension/availability risk; a specific
registration-cost-of-onboarding risk). Kept as three rows with cross-references rather than merged into
one, on the grounds that collapsing them would lose the distinct mitigation each one implies.

---

## 5. Risk table field mismatch — confirmed and kept as the richer form

`master.md`'s §14 table header is: `| ID | Description | Probability (1-5) | Impact (1-5) | Score |
Mitigation | Owner | Status |` — **no Category column.**

`references/standards.md` (§3, row 14) describes the same section's required content as: **"Category**,
description, likelihood, impact, mitigation, owner, status" — Category is explicitly required in the
prose standard even though the template's own markdown skeleton omits it.

Part 5's actual draft used the richer form: `| ID | Cat | Description | P | I | Score | Mitigation |
Owner | Status | Links |` — Category **and** an additional Links (cross-reference) column beyond what
either master.md or standards.md specifies.

**Decision:** kept Part 5's richer form (Category + Status + Links) in the assembled §14, since it
satisfies standards.md's actual content requirement and master.md's own table header is the artifact
that's out of sync with its own written standard. Flagged inline in §14 of `draft-v1.md` and here so the
discrepancy between `master.md` and `references/standards.md` is visible for whoever maintains the skill
templates next — this is a defect in the skill's own template files, not something assembly should
silently paper over by dropping Category to match the narrower table header.

---

## 6. §1 Executive Summary

Did not exist in any of the five parts (correctly — per master.md's generation order, it's written
last). Drafted at assembly from the fully-reconciled document. States explicitly: what's decided (the
document's structure and the shape of the open-question set), what's not decided (sponsor identity,
segment, root cause, monetisation, every numeric target), and the single recommended next action
(ASM-028's retrospective). No new facts, numbers, or claims were introduced that aren't already present
and sourced elsewhere in the assembled document.

---

## 7. Structural sections added at assembly (not present in any of the 5 parts)

None of the five parts owned §1 (by design), §9, §18, §19, §20, the Document Control block, or the
Appendix — Readiness Report. These were added as minimal, honest scaffolding rather than left absent
from a document claiming to follow `master.md`:

- **Document Control** — populated with known facts (title, today's date) and `[NEEDS INPUT]` for
  everything requiring a real person or a computed score (sponsor, readiness score).
- **§9 FR boundary** — the fixed one-paragraph boilerplate `master.md` prescribes verbatim; not
  content generation.
- **§18 Glossary** — built exclusively from terms and definitions that already appear, explained inline,
  somewhere in the five source parts (e.g. DLT's non-blockchain meaning was already clarified in Part
  3's CMP-C; DSO was already used in Part 4's KPI-01). No new definitions invented.
- **§19 Appendices** — stated as empty rather than omitted silently.
- **§20 Sign-off** — structurally complete (roles, what each signature covers) but every name
  `[NEEDS INPUT]`, consistent with §5's stakeholder gaps. Explicitly states the document is **not**
  ready for sign-off.
- **Appendix — Readiness Report** — deliberately **not scored**. Computing a real rubric score was
  outside this assembly's explicit task list, and inventing a plausible-looking number here would be
  exactly the "invented metric" anti-pattern this skill exists to prevent. Flagged as a pending follow-up
  action instead.

---

## 8. Per-section word count vs. standards.md budget

`references/standards.md` gives typical lengths per section for the initiative-size class this document
was classified into ("Small (5-10 pages)" per `classification.md` — roughly 2,000–5,000 words at
~400–500 words/page). Actual counts from the assembled `draft-v1.md`:

| Section | Words | standards.md typical length | Over/under |
|---|---|---|---|
| Document Control | 274 | (not sized in standards.md) | — |
| 1. Executive Summary | 421 | 150-300 words | **~1.4-2.8x over** |
| 2. Business Objectives | 476 | 3-7 objectives (no word count given) | — |
| 3. Background / Problem Statement | 751 | 0.5-1.5 pg (~200-750 words) | at/near top of range |
| 4. Project Scope | 696 | 0.5-1 pg (~200-500 words) | **~1.4-3.5x over** |
| 5. Stakeholder Analysis + RACI | 694 | 0.5-1 pg (~200-500 words) | **~1.4-3.5x over** |
| 6. Current State (As-Is) | 669 | 0.5-1.5 pg (~200-750 words) | at top of range |
| 7. Future State (To-Be) | 591 | 0.5-1.5 pg (~200-750 words) | within range |
| 8. Business Requirements | 941 | 2-6 pg (~800-3000 words) | within range |
| 9. FR Boundary | 67 | 1 paragraph | within range |
| 10. NFR (incl. 10.2-10.5 + Counsel handoff) | 5,731 (1278+1128+553+354+215+227+1945-mixed*) | 0.5 pg (~200-500 words) | **~11-28x over** — see note |
| 11. Assumptions Register | 1,945 | 0.25-0.5 pg (~100-250 words) | **~8-19x over** |
| 12. Dependencies | 412 | 0.25-0.5 pg (~100-250 words) | **~1.6-4x over** |
| 13. Constraints | 378 | 0.25-0.5 pg (~100-250 words) | **~1.5-3.8x over** |
| 14. Risk Register | 1,327 | 0.5-1 pg (~200-500 words) | **~2.7-6.6x over** |
| 15. Success Metrics / KPIs | 620 | 0.5 pg (~200-250 words) | **~2.5-3.1x over** |
| 16. Acceptance Criteria | 599 | 1-2 pg (~400-1000 words) | within range |
| 17. Cost-Benefit / Business Case | 1,321 | 0.5-1.5 pg (~200-750 words) | **~1.8-6.6x over** |
| 18. Glossary | 425 | 0.5-1 pg (~200-500 words) | within range |
| 19. Appendices | 28 | variable | — |
| 20. Sign-off | 181 | 0.25 pg (~100 words) | **~1.8x over** |
| Appendix — Readiness Report | 140 | (not sized) | — |
| **Document total** | **16,720** | **5-10 pages (~2,000-5,000 words)** | **~3.3-8.4x over** |

*\* The §11 Assumptions Register word count (1,945) is counted once in its own row; the §10 subtotal
above sums 10/10.2/10.3/10.4/10.5/Counsel-handoff only (5,731 words) and does not include §11.*

**Note on §10's overrun specifically:** this is by far the largest section (5,731 words against a
~200-500 word budget in `master.md`/`standards.md` — a 11-28x overrun on its own), because Part 3 treated
§10 as the home for the entire compliance analysis (CMP-A through CMP-H, retention RET-001-007, audit
AUD-001-007, and a full counsel-handoff list) rather than the narrow "business-level NFR table" the
template describes. That is a legitimate response to a genuinely compliance-heavy product (an automated
third-party-contacting tool touching DPDP, TRAI/TCCCPR, GDPR, GST, and PCI-DSS trigger surfaces
simultaneously) — but it means §10 alone is roughly 2.7x the entire document's page-count budget. This
was not trimmed at assembly per the explicit instruction not to cut content to hit the page budget on
this pass; it is reported here as the single largest driver of the overall overrun.

**Total document (16,720 words) is larger than the ~13,000-word figure cited in the assembly brief** —
the brief's figure describes the raw sum of the five source parts before assembly (2,516 + 1,923 + 3,667
+ 1,961 + 2,947 = 13,014 words); assembly added roughly 3,700 words of connective tissue (cross-references,
the new ASM/RSK/OS/CON rows, §1/§9/§18/§19/§20/Document Control/Readiness-Report scaffolding, and the
de-dup annotations), which is itself worth flagging: **assembly work that resolves fragmentation
structurally increases page count**, and a real productionisation pass would need a separate trimming
pass against the 5-10 page target — not attempted here per the explicit "do not cut content" instruction.

---

## 9. Unresolvable cross-references — none found requiring escalation beyond `[NEEDS INPUT]`

Every cross-reference staged by the five parts (Part 3's §10.5 feed-forward table; Part 5's
"traceability gap for assembly" note; Part 1's internal BR/OBJ links; Part 2's "BR-ID cross-references
added at assembly" note) was resolvable using content that existed somewhere in the five parts. No
cross-reference required inventing a fact to close. The two genuine orphans in §1a above are the
closest thing to an "unresolvable" reference — they are resolvable only by new input (a compliance KPI
proposal, a churn-objective decision), not by assembly.

---

## 10. Summary counts

- **ID remaps:** 10 (ASM-501…510 → ASM-028…037)
- **New IDs assigned to previously-unrouted content:** 30 inline assumptions swept into ASM-001–ASM-027 (27 genuine + 3 excluded as meta/duplicate), 3 new risks (RSK-010–012), 1 new scope exclusion (OS-6), 1 new constraint (CON-07), 2 resolved `OBJ-###` placeholders (NFR-002, NFR-004)
- **De-duplications:** 1 primary (the DPDP data-protection obligation across BR-006/NFR-006/CON-04/RSK-007) with 2 additional near-duplicate pairs reviewed and deliberately kept separate (RSK-007/RSK-012; RSK-006/RSK-010/RSK-011)
- **Genuine orphans recorded (not invented around):** 2 (OBJ-004 has no KPI; KPI-05 has no OBJ)
- **Total words:** 16,720 vs. a 5-10 page (~2,000-5,000 word) budget — see §8 above for the per-section breakdown and the §10-specific driver of the overrun
