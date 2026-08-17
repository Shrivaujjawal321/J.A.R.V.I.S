# /brd smoke test — findings against the skill

Run: 2026-07-29. Intake: *"freelancers ke liye ek tool jo unpaid invoices automatically chase kare"* —
deliberately the thinnest realistic input, one sentence, no numbers, no context.

Purpose of this run is **not** to produce a BRD about invoice chasing. It is to find out where the
skill breaks when it is actually executed. Every item below was raised independently by the drafting
agents or measured from their output — none is speculative.

---

## Verdict so far

The anti-fabrication core **works**. Five agents, 13,166 words, and not one invented rupee figure,
market size, retention period, uptime target or baseline. Every unknown came back tagged:
**30 `[ASSUMPTION]`, 105 `[NEEDS INPUT]`**. Two agents independently reported cutting their own
drafts down twice to avoid padding, and one refused to opine on payment-aggregator licensing and
marked it `[ESCALATE]` instead. That is the behaviour the skill exists to produce.

The **orchestration around that core is where it breaks.**

---

## D1 — Step 3's parallel fan-out contradicts the skill's own generation order

**Severity: high. Reported independently by 4 of 5 agents.**

`templates/master.md` mandates a generation order — problem before objectives, objectives before
requirements, as-is before to-be, executive summary last — because each stage needs the previous
stage's IDs to trace upward. `SKILL.md` Step 3 then dispatches all five agents **in one batch**, so
no agent can see any other's IDs.

Consequences observed in this run:

- Part 3 (NFRs) emitted `OBJ-### (reconcile at assembly)` placeholders for every upward trace.
  `standards.md` scores a missing NFR→OBJ trace as a defect, so a compliant drafter loses points for
  obeying the dispatch pattern.
- Part 2 refused to invent `BR-XXX` placeholders because they could collide with part 1's real IDs,
  and left cross-references to be added at assembly.
- Part 4's metrics could not be reconciled against the objectives and problem statement they are
  supposed to measure.
- Part 5 reserved an `ASM-501+` ID block defensively, guessing at a convention the skill never states.

This is not editorial friction. Every parallel run ships orphaned requirements unless a human does
the reconciliation by hand afterward.

**Fix options (Boss decides):**
1. **Serial spine, parallel leaves** — one agent writes §3 problem + §2 objectives + §8 requirements
   first (they are one causal chain anyway), then the remaining four run in parallel *with the real
   ID list in their brief*. Costs one extra round-trip; removes the defect entirely.
2. **Pre-allocated ID blocks** — the skill assigns each part a fixed ID range up front and requires a
   declared reconciliation pass. Keeps full parallelism; leaves cross-part *semantic* alignment
   (does NFR-004 really serve OBJ-002?) still unverified.
3. **Keep as-is, make assembly a first-class step** with its own agent and contract. This run proves
   assembly is substantial work, not a merge — it should not be an unwritten sentence in Step 3.

---

## D2 — §11 Assumptions Register cannot be produced by a drafting agent

**Severity: high. Structural, not a quality issue.**

The template requires every `[ASSUMPTION]` tag anywhere in the document to appear as a register row.
`SKILL.md` assigns §11 to the `strategy-consultant-agent`, who runs in parallel and can see only its
own tags — 3 of the 30 that exist. The register is therefore **incomplete by construction on every
run**, and rubric criterion 8 will score it wrong.

That agent detected this itself, wrote a merge note, and reserved an ID block — a correct workaround
for a task it should never have been given.

**Fix:** move §11 to the assembler, which is the only role that can see the whole document. Same
argument applies to §1 Executive Summary, which no agent owned in this run and which generation order
already says must be written last.

---

## D3 — "Small: 5-10 pages" produced 13,166 words (~26 pages, 3x over)

**Severity: high. Measured, not reported.**

Per-part word counts:

| Part | Words |
|---|---|
| part-3 NFR + compliance | 3,667 |
| part-5 cost-benefit + risks + assumptions | 2,947 |
| part-1 objectives + problem + requirements | 2,516 |
| part-4 stakeholders + metrics + deps | 1,961 |
| part-2 as-is + to-be + scope | 1,923 |
| **total** | **13,166** |

The briefs said "SMALL (5-10 pages total across all 5 agents — yours is a fraction of that)."
Two agents flagged "a fraction" as not actionable, and both were right: with no explicit allocation,
each agent sizes its own sections against `exemplars.md`, which demands per-row rationale, owners,
validation methods and cross-links. **The exemplar's depth and the size budget are in direct
conflict** — one agent computed that `standards.md` allots its three sections up to 3 pages while
the exemplar's required fields for 19 register rows cannot fit in 3 pages.

Both constraints are stated by the skill. It does not say which wins.

**Fix:** allocate an explicit word budget per part in the dispatch brief, derived from
`standards.md` §3's per-section page budgets, and state which constraint wins when exemplar depth
does not fit. Padding is a scored defect, so this currently costs points on every run.

---

## D4 — `master.md` and `rubric.md` disagree on required fields

**Severity: medium. A drafter who follows the template loses points.**

The risk table in `master.md` has no `category` column; `rubric.md` criterion 8 requires a category
per risk entry. The drafting agent added Category and Status columns on its own initiative and
flagged the mismatch. Anyone who follows the template literally is penalised by the rubric.

**Fix:** reconcile the two files. A template that cannot score full marks against its own rubric is
a trap.

---

## D5 — No ownership rule for boundary-straddling requirements

**Severity: medium.**

Compliance obligations legitimately belong in §8 Business Requirements, §10 NFRs, §13 Constraints and
§14 Risks. The skill assigns those sections to four different parallel agents and states no ownership
or de-duplication rule. In this run, part 1 kept a data-protection requirement in §8 while part 3 was
independently writing the same obligation into §10 — and `anti-patterns.md` #11 scores near-duplicates
under two IDs as a defect.

**Fix:** state a precedence rule (e.g. regulatory *obligations* live in §10 with a §8 cross-reference)
and make de-duplication an explicit assembler responsibility.

---

## D6 — Unhandled: the whole org is one person

**Severity: medium. Affects any Boss-scale BRD, which is most of them.**

`anti-patterns.md` #6 bans departments-as-owners and requires named individuals. Here there is exactly
one person, so all 19 register rows name Ujjawal — satisfying the letter of the rule while defeating
its purpose, which is independent accountability. The agent flagged this and compensated by requiring
external evidence in several validation methods.

**Fix:** the skill should say what "owner" means in a solo venture — probably that the validation
*method* must be externally verifiable precisely because the owner cannot be independent.

---

## D7 — No defined behaviour when a specialist's own protocol conflicts

**Severity: low-medium.**

`compliance-officer-agent`'s system prompt mandates a 6-section memo with a disclaimer banner and
self-rubric; the BRD task mandates `master.md`'s section format. The agent chose the BRD format and
compressed its disclaimer, then flagged the collision. The same agent also hit its own mandatory
escalation trigger (payment-aggregator licensing) *inside* a BRD section, where the skill defines no
behaviour — it marked `[ESCALATE — not analysed here]` and refused to opine either way.

Both judgment calls were right. Both should be written down rather than re-derived per run.

**Fix:** state that the BRD output contract wins on format, and define an escalation marker so a
trigger firing mid-document has a defined home.

---

## D8 — Open question the run has not answered yet

Does the rubric **punish honesty?** This draft is deliberately saturated — 105 `[NEEDS INPUT]` from a
one-sentence intake — and one agent asked directly how a scorer is supposed to grade an objective that
has an ID, a measurement method and a valid upward trace but no numbers, because no number exists to
have.

Two possible outcomes, and they demand opposite fixes:

- **Rubric scores it low** → the rubric rewards fabrication, since an invented baseline would score
  higher than an honest blank. That would be the most serious defect in the system and it inverts the
  skill's entire purpose.
- **Rubric scores it well** → the score is measuring form while the document is nearly empty of
  decided content, and the readiness report must state that far more loudly than a caveat line.

The related check: does the rubric catch the 3x padding overrun in D3? If not, that is a second gap.

*Answered after the scoring pass — see `score.json` and the addendum below.*

---

## What is confirmed working

- Anti-fabrication holds under pressure. Zero invented numbers across 13,166 words and five
  independent agents. This was the highest-risk failure mode and it did not occur.
- `[NEEDS INPUT]` tags are specific questions, not vague gaps — mostly answerable by Boss in a
  sentence each.
- Agents correctly refused impossible work: one listed five items requiring observation or interviews
  that Q&A cannot resolve, rather than asking three more questions to fake coverage.
- Domain sharpness survived the format. The third-party-data-subject problem (the freelancer's client
  never opted in), the counter-metric guarding against optimising collection while harming that client,
  and the pre-build risks that no amount of building fixes — all surfaced without being prompted for
  by name.
