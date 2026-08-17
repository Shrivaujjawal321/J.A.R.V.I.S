# Research Brief: Objectively Scoring Business Requirements Document Quality

**Purpose:** ground truth for building an automated BRD scorer (0-100, per-criterion breakdown). Every criterion below traces to a published standard, peer-reviewed paper, or named industry practitioner — not invented.

**Date:** 2026-07-29

---

## 1. Existing requirements-quality models (the real frameworks)

### 1.1 ISO/IEC/IEEE 29148:2018 — "Systems and software engineering — Life cycle processes — Requirements engineering"

This is the primary international standard defining what makes an individual requirement "good," and it is the theoretical foundation Femmer et al. explicitly built the requirements-smells taxonomy on. It defines **nine characteristics of individual requirements** plus characteristics for **sets** of requirements. (INCOSE v4 adopts and extends the same characteristic names — see §1.2.)

Individual requirement characteristics (per IEEE/ISO 29148, corroborated by INCOSE v4 summary sheet):
- **Necessary** — defines an essential capability/constraint; removing it creates a deficiency that cannot be met another way.
- **Appropriate** — the specific detail is appropriate to the level of the entity to which it belongs (not over- or under-specified for that abstraction level).
- **Unambiguous** — interpretable in only one way by all readers.
- **Complete** — stands alone without needing further amplification.
- **Singular** — states one and only one capability/characteristic/constraint (atomic).
- **Feasible** — realizable within cost/schedule/technical/legal/regulatory constraints at acceptable risk.
- **Verifiable** — a finite, cost-effective process exists to confirm satisfaction (test/inspection/analysis/demonstration).
- **Correct** — an accurate representation of the actual need.
- **Conforming** — follows the approved template/style for requirement statements.

Requirement **set** characteristics: Complete, Consistent, Feasible, Comprehensible, Able-to-be-validated. [ISO/IEC/IEEE 29148:2018]

Source: [ISO/IEC/IEEE 29148:2018 sample](https://cdn.standards.iteh.ai/samples/72089/62bb2ea1ef8b4f33a80d984f826267c1/ISO-IEC-IEEE-29148-2018.pdf), [ISO 29148:2011 full text mirror](https://nirmt.com/storage/uploads/E-BOOK_BE-INDUSTRIAL-AND-SAFETY/29148-2011%20-%20ISOIECIEEE%20International%20Standard%20-%20Systems%20and%20software%20engineering%20--%20Life%20cycle%20processes%20--Requirements.pdf), [CWNP explainer](https://www.cwnp.com/req-eng/)

### 1.2 INCOSE Guide for Writing Requirements (v4, 2023; v3.1, 2022; v1 2019)

This is the most operational, rule-level framework available and the best candidate for a rules-engine layer of an automated scorer — because it gives literal **detectable linguistic rules**, not just abstract characteristics. It defines the same 9 individual-requirement characteristics as 29148 (Necessary, Appropriate, Unambiguous, Complete, Singular, Feasible, Verifiable, Correct, Conforming) plus 5 set-level characteristics (Complete, Consistent, Feasible, Comprehensible, Able to be Validated), and then operationalizes them into **42 numbered rules** (R1–R42; earlier editions had 41 hence "R1-R41" is sometimes cited) grouped into 14 categories. Full list, reconstructed from the INCOSE summary sheet and a detailed secondary breakdown:

**Accuracy (R1–R9)**
- R1 Structured Statements — conform to agreed grammatical patterns (e.g., "The [entity] shall [action] [object] [conditions]").
- R2 Active Voice — subject of the sentence is the entity responsible for the action.
- R3 Appropriate Subject-Verb — the actor and action match the correct system level.
- R4 Defined Terms — every domain term appears in an explicit glossary/data dictionary.
- R5 Definite Articles — "the" (specific reference) not "a"/"an" (ambiguous reference) when referring to a defined entity.
- R6 Common Units of Measure — one consistent unit system throughout the document.
- R7 Vague Terms — forbids "some," "any," "allowable," "several," "many," "a lot of," "a few," "almost always," "very nearly," "nearly," "about," "close to," "almost," "approximate."
- R8 Escape Clauses — forbids "so far as is possible," "as little as possible," "where possible," "as much as possible," "if it should prove necessary," "if necessary," "to the extent necessary," "as appropriate," "as required," "to the extent practical," "if practicable."
- R9 Open-Ended Clauses — forbids "including but not limited to," "etc.," "and so on."

**Concision (R10–R11)**
- R10 Superfluous Infinitives — cut filler like "to be able to."
- R11 Separate Clauses — one condition/qualification per clause, not stacked.

**Non-Ambiguity (R12–R17)**
- R12 Correct Grammar
- R13 Correct Spelling
- R14 Correct Punctuation
- R15 Logical Expressions — use explicit defined conventions (e.g., "[X AND Y]") instead of prose "and/or."
- R16 Use of "Not" — avoid negative requirements framed as prohibitions; state the positive, verifiable behavior instead.
- R17 Oblique Symbol ("/") — forbidden because it creates "and/or" ambiguity.

**Singularity (R18–R23)**
- R18 Single Thought Sentence — one requirement = one thought + its qualifying sub-clauses only.
- R19 Combinators — "and," "or," "then," "unless" joining independent clauses signal a compound (non-atomic) requirement that should be split.
- R20 Purpose Phrases — strip "the purpose of X is..." rationale language out of the normative requirement text.
- R21 Parentheses — no parenthetical requirement content (it gets silently dropped in review/testing).
- R22 Enumeration — enumerate items explicitly instead of vague group nouns ("relevant subsystems" → name them).
- R23 Supporting Diagrams — complex behavior/logic should reference a diagram, not be crammed into prose.

**Completeness (R24–R25)**
- R24 Pronouns — avoid personal/indefinite pronouns ("it," "this," "which," "they") with unclear antecedents; repeat the noun.
- R25 Headings — a requirement must be understandable without relying on its section heading for context.

**Realism (R26)**
- R26 Absolutes — forbids unachievable absolutes: "100%," "zero defects," "always," "never," "all," unless truly verifiable.

**Conditions (R27–R28)**
- R27 Explicit Conditions — applicability conditions stated directly in the requirement, not implied.
- R28 Multiple Conditions — express compound conditions with explicit logical structure, not run-on prose.

**Uniqueness (R29–R30)**
- R29 Classification — needs/requirements grouped by the aspect of the problem/system they address.
- R30 Unique Expression — each requirement stated exactly once (duplication elsewhere in the doc is a defect).

**Abstraction (R31)**
- R31 Solution-Free — requirements state *what*, not *how*, unless a design constraint is deliberately and justifiably imposed. (This is the direct rule against "solution language creep," relevant to LLM-generated BRDs — see §8.)

**Quantifiers (R32)**
- R32 Universal Qualification — use "each" (distributive, testable per-instance) instead of "all"/"any"/"both" (collective, ambiguous scope).

**Tolerances (R33)**
- R33 Range of Values — quantities need explicit tolerance/range for verification (e.g., "between 200ms and 250ms," not "around 200ms").

**Quantification (R34–R35)**
- R34 Measurable Performance — every performance requirement carries an explicit, testable target.
- R35 Temporal Dependencies — replace vague timing ("eventually," "soon") with explicit timing constraints.

**Uniformity of Language (R36–R40)**
- R36 Consistent Terms and Units across all artifacts.
- R37 Acronyms — defined on first use, used consistently thereafter.
- R38 Abbreviations — defined or avoided.
- R39 Style Guide — project-wide statement style guide followed.
- R40 Decimal Format — consistent decimal notation/significant digits.

**Modularity (R41–R42)**
- R41 Related Requirements grouped together.
- R42 Structured Sets — the set conforms to a defined template/structure.

Sources: [INCOSE Guide to Writing Requirements V4 Summary Sheet](https://www.incose.org/docs/default-source/working-groups/requirements-wg/guidetowritingrequirements/incose_rwg_gtwr_v4_summary_sheet.pdf), [INCOSE V3.1 Summary Sheet](https://www.incose.org/docs/default-source/working-groups/requirements-wg/rwg_products/incose_rwg_gtwr_summary_sheet_2022.pdf), [reqi.io — INCOSE Requirements Quality: The 42 Rules, Made Simple](https://reqi.io/articles/incose-requirements-quality-42-rule-guide) (best available secondary breakdown of the full rule set with categories), [QRA Corp — Automating the INCOSE Guide for Writing Requirements](https://edu.qracorp.com/hubfs/Automating%20the%20INCOSE%20Guide%20for%20Writing%20Requirements.pdf) (confirms these rules are designed to be automated via NLP tooling — directly relevant precedent for our scorer).

**Why this matters for an automated scorer:** R1–R42 are almost entirely regex/POS-taggable. This is the single best source for the "detectable defect" layer of a rubric, because INCOSE literally wrote it to be checkable by tools (QRA Corp's whole paper is about automating exactly this).

### 1.3 IREB CPRE (International Requirements Engineering Board, Certified Professional for Requirements Engineering)

IREB is the dominant European RE certification body. The CPRE Foundation Level syllabus includes an explicit learning objective: "mastering and using quality criteria for requirements" plus "knowing the two most important style rules for requirements" (commonly taught as **active voice** and **one requirement, one sentence** — consistent with INCOSE R2 and R18). IREB maintains a living, versioned glossary (v2.2.0, Oct 2025) harmonized with ISTQB testing terminology since 2019. [unverified: I could not retrieve the specific enumerated IREB quality-criteria list beyond the syllabus learning objective — the CPRE syllabus itself, not the public glossary, contains the full criteria list and is not freely downloadable.] Treat IREB as corroborating INCOSE/29148 rather than as a source of additional distinct criteria.

Source: [IREB CPRE Glossary v2.2.0](https://isqi.org/media/d2/8e/89/1760694720/ireb_cpre_glossary_NL_2.2.pdf), [IREB Wikipedia](https://en.wikipedia.org/wiki/International_Requirements_Engineering_Board), [CPRE official](https://cpre.ireb.org/en)

### 1.4 Karl Wiegers — "Software Requirements" (Microsoft Press, 2nd/3rd ed.) quality characteristics

Wiegers is the most widely cited practitioner-level source (used in industry BA/PM training far more than ISO standards). His characteristics split into two levels:

- **Individual requirement statement:** Complete, Correct, Feasible, Necessary, Prioritized, Unambiguous, Verifiable. Note the addition of **Prioritized** relative to ISO 29148 — Wiegers treats prioritization (must-have/should-have/could-have or similar) as a first-class quality attribute, not just a project-management nicety. This is directly useful: a BRD with zero prioritization signal on its requirements should lose points.
- **Requirements specification (the document as a whole):** Complete, Consistent, Modifiable, Traceable.

Wiegers' companion practice ("Requirements Quality Is in the Eye of the Beholder") stresses that different reviewer roles (BA, dev, tester, end user) catch different defect classes — implying a good scorer should check multiple *dimensions* (linguistic, structural, business-alignment) rather than one lens only.

Source: [O'Reilly — Software Requirements 2nd ed.](https://www.oreilly.com/library/view/software-requirements-second/0735618798/apg.html), [Wiegers — Requirements Quality Is in the Eye of the Beholder (Medium)](https://medium.com/analysts-corner/requirements-quality-is-in-the-eye-of-the-beholder-fec8d2edd6c4), [Wiegers — Writing Quality Requirements (1999, processimpact.com)](https://www.processimpact.com/articles/qualreqs.pdf) [PDF was not machine-readable during this research pass — cite but verify manually before quoting specifics]

### 1.5 Academic requirements-smells literature (Femmer et al. and successors)

This is the empirical/NLP backbone for automated defect detection — most directly usable for a programmatic scorer.

**Femmer, Méndez Fernández, Wagner, Eder (2017), "Rapid quality assurance with Requirements Smells"** (Journal of Systems and Software / extended from their 2014 ICSE workshop paper "Rapid Requirements Checks with Requirements Smells: Two Case Studies"). Defines **nine requirement smells**, grounded explicitly in ISO 29148's "unambiguous" and "verifiable" characteristics, and ships a tool (**Smella**) that detects most of them via POS tagging + dictionaries:

| Smell | Definition | Detection technique | Example |
|---|---|---|---|
| Subjective Language | word whose meaning is not objectively defined | dictionary lookup | "user-friendly" |
| Ambiguous Adverbs/Adjectives | adverbs/adjectives inherently unspecified in degree | dictionary lookup | "almost," "approximately" |
| Non-verifiable Terms (merges the originally separate "Loopholes" and "Open-ended" smells, later found empirically indistinguishable) | terms offering possibility rather than obligation, or an imprecisely bounded extent | dictionary lookup | "sufficient," "as far as possible" |
| Superlatives | adjective expressing the system's relation to *all* other systems/states | POS tagging | "highest," "best," "fastest" |
| Comparatives | adjective expressing relation to one specific other system/prior state without stating the baseline | POS tagging | "more exact," "faster than before" |
| Negative Statements | states a capability the system must *not* provide, which is harder to verify positively | POS tagging | "must not sign off" |
| Vague Pronouns | pronoun whose antecedent is not clear from context | POS tagging | "which," "it," "this" |
| Uncertain Verbs (added in later work) | modal verbs expressing doubt rather than obligation | small modal-verb dictionary | "may," "can," "might" |
| Polysemy (added in later work — domain-specific ambiguity) | a word with multiple valid meanings depending on domain context | word-embedding-based dictionary | "call," "return," "fire" |

Smella's published evaluation: **precision 0.59, recall 0.82** in real-world requirement sets — i.e., it over-flags (roughly 4 in 10 flags are false positives) but rarely misses a real smell. This is an important calibration data point: pure dictionary/POS NLP smell-detection has a real, published false-positive ceiling — an LLM-judge layer should be used to *filter* rule-based flags, not replace them, to control precision.

Sources: [Femmer et al. — Rapid quality assurance with Requirements Smells (arXiv:1611.08847 / ScienceDirect)](https://arxiv.org/pdf/1611.08847), [ScienceDirect version](https://www.sciencedirect.com/science/article/abs/pii/S0164121216000789), [Rapid Requirements Checks with Requirements Smells: Two Case Studies, ACM ICSE-RCoSE'14](https://dl.acm.org/doi/10.1145/2593812.2593817)

**Follow-on academic work extending Femmer's taxonomy:**
- Deep-learning smell classifiers (2021–2025): "Detecting Requirements Smells With Deep Learning" [arXiv:2108.03087] uses ELMo contextual embeddings to catch smells dictionary methods miss (context-dependent ambiguity).
- "Multi-label software requirement smells classification using deep learning" (Nature Scientific Reports, 2025) confirms the consolidated smell set: **Subjective Language, Comparative Phrases, Superlative Phrases, Passive Voice, Uncertain Verbs, Ambiguous Adverbs, Negative Statements, Polysemy, Vague Pronoun, Open-ended Non-verifiable Terms, Loophole** — treating Passive Voice as its own smell category (aligning with INCOSE R2) even though Femmer's original paper folded voice into ambiguity discussion generally. [Nature Scientific Reports](https://www.nature.com/articles/s41598-025-86673-w), [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11833090/)
- "Natural Language Requirements Testability Measurement Based on Requirement Smells" (arXiv:2403.17479, Springer Neural Computing & Applications 2024) — directly operationalizes 9 of these smells (S1–S9: Subjective Language, Ambiguous Adverb/Adjective, Non-verifiable Terms, Superlatives, Comparatives, Negative Statements, Vague Pronouns, Uncertain Verbs, Polysemy) into a **testability score**, i.e. exactly the kind of automated 0–100-style metric we're trying to build, but scoped to individual requirement testability rather than a whole BRD. Worth studying its scoring formula directly as a template. [arXiv:2403.17479](https://arxiv.org/pdf/2403.17479)

### 1.6 ISO/IEC 25010 (SQuaRE) — relevance and boundary

ISO/IEC 25010 (2011, revised 2023) is a **product/software quality model**, not a requirements-document quality model — it defines 8 characteristics a *delivered system* should have: Functional Suitability, Performance Efficiency, Compatibility, Usability, Reliability, Security, Maintainability, Portability (plus a separate "Quality in Use" model: Effectiveness, Efficiency, Satisfaction, Freedom from Risk, Context Coverage). Its relevance to BRD scoring is **indirect but important**: it is the standard taxonomy against which a BRD's non-functional requirements section should be checked for *category coverage* — i.e., "does this BRD's NFR section address Performance Efficiency, Security, Usability, Reliability, Maintainability, Portability, Compatibility?" is a legitimate completeness check, because 25010 is the industry-canonical checklist of NFR categories. Do not conflate it with a document-quality rubric; use it only as the coverage checklist for §4 below.

Sources: [arc42 Quality Model — ISO/IEC 25010](https://quality.arc42.org/standards/iso-25010), [Perforce — What Is ISO 25010?](https://www.perforce.com/blog/qac/what-is-iso-25010), [Codacy — Exploration of ISO/IEC 25010](https://blog.codacy.com/iso-25010-software-quality-model)

---

## 2. Requirements smells / defect taxonomy — detection heuristics + before/after rewrites

This consolidates §1.5 and INCOSE R1–R42 into implementation-ready defect checks. Each is independently detectable (regex/POS or LLM-judge) and independently attested in the literature above.

**1. Ambiguity — subjective language**
- Signal: adjectives/adverbs with no objectively agreed meaning: "user-friendly," "robust," "intuitive," "efficient," "modern," "seamless," "flexible," "scalable" (used without a number).
- Before: "The system shall provide a user-friendly interface."
- After: "The system shall allow a first-time user to complete order entry in ≤3 clicks and ≤90 seconds, measured via usability testing with 10 representative users."

**2. Ambiguity — vague pronouns**
- Signal: "it," "this," "that," "which," "they" with an antecedent more than one clause/sentence away, or with 2+ possible antecedents.
- Before: "The order and the invoice are generated together, which must be reviewed before sending."
- After: "The order and the invoice are generated together. The invoice must be reviewed before sending."

**3. Non-verifiability — vague/ambiguous adverbs**
- Signal: "approximately," "almost," "nearly," "about," "close to," "quickly," "efficiently," "adequately," "sufficient(ly)," "reasonable," "as needed."
- Before: "The report shall generate quickly."
- After: "The report shall generate within 5 seconds for datasets up to 100,000 rows."

**4. Comparatives without a stated baseline**
- Signal: comparative adjective/adverb ("faster," "better," "more accurate," "higher," "lower") with no named comparison point.
- Before: "The new checkout flow shall be faster than before."
- After: "The new checkout flow shall complete in ≤8 seconds at the 95th percentile, versus the current 22-second p95 baseline (measured 2026-06 production logs)."

**5. Superlatives**
- Signal: "best," "highest," "lowest," "most," "fastest," "optimal," "maximum performance" without a defined metric.
- Before: "The platform shall offer the best possible uptime."
- After: "The platform shall maintain 99.9% monthly uptime (≤43.8 minutes downtime/month), measured via [monitoring tool], excluding scheduled maintenance windows."

**6. Negative statements (capability framed as prohibition)**
- Signal: "shall not," "must never," "will not" describing a capability rather than a genuine constraint/safety rule.
- Before: "The system shall not allow slow report generation."
- After: "The system shall generate reports within 5 seconds for 95% of requests."
- (Note: genuine safety/compliance prohibitions — "the system shall not store card CVV" — are legitimate negative requirements per PCI-DSS; the smell is negatives used as a lazy substitute for a positive measurable requirement, not all negatives.)

**7. Loopholes / escape clauses**
- Signal: "if possible," "where possible," "as appropriate," "as required," "to the extent practicable," "if necessary," "so far as is possible" (INCOSE R8).
- Before: "The vendor shall provide support as appropriate."
- After: "The vendor shall provide P1-severity support response within 1 business hour, 24/5, per the SLA in Appendix C."

**8. Open-ended clauses**
- Signal: "etc.," "and so on," "including but not limited to," "such as" used to avoid enumerating a closed set (INCOSE R9).
- Before: "The system shall support common file formats such as PDF, DOCX, etc."
- After: "The system shall support import of PDF, DOCX, and XLSX files (v1.0 scope). Additional formats are explicitly out of scope — see §Out of Scope."

**9. Passive voice hiding the actor**
- Signal: passive construction ("shall be validated," "will be processed," "is required") with no named responsible subject (INCOSE R2/R3).
- Before: "Customer data shall be validated before storage."
- After: "The Order Service shall validate customer data against the schema in Appendix B before writing to the Customer database."

**10. Compound / non-atomic requirements**
- Signal: "and," "or," "then," "unless," "while," multiple verb phrases, or a comma-separated list of distinct obligations in one requirement ID (INCOSE R18/R19).
- Before: "The system shall allow users to register, log in, and reset their password, and shall send a confirmation email for each action."
- After: split into 4 atomic requirements (REQ-01 register, REQ-02 log in, REQ-03 reset password, REQ-04 confirmation email per action), each independently testable and traceable.

**11. Missing units/tolerances**
- Signal: a bare number with no unit, or a target with no acceptable range (INCOSE R6/R33).
- Before: "Page load time shall be under 2."
- After: "Page load time (Largest Contentful Paint) shall be ≤2.0 seconds ±0.2s, measured on a throttled 4G connection per Web Vitals methodology."

**12. Universal quantifiers ("all," "every," "always," "never," "100%")**
- Signal: unqualified absolutes (INCOSE R26/R32).
- Before: "The system shall always be available."
- After: "The system shall maintain 99.95% availability per calendar month, excluding pre-announced maintenance windows ≤4 hours/month."

**13. Undefined/inconsistent terms**
- Signal: a domain noun (e.g., "customer," "order," "active user") used with no glossary entry, or used with two different meanings in different sections (INCOSE R4/R36).
- Detection: build a term-frequency index, flag capitalized domain nouns absent from a Glossary/Definitions section, or check pairwise cosine similarity of usages via embeddings to catch drift.

**14. Duplication**
- Signal: near-identical requirement text appearing under two different IDs (INCOSE R30) — detectable via embedding similarity threshold across the requirements table.

Cumulative source basis for all 14: [Femmer et al. 2017](https://arxiv.org/pdf/1611.08847), [arXiv:2403.17479 testability smells S1–S9](https://arxiv.org/pdf/2403.17479), [reqi.io INCOSE 42 rules](https://reqi.io/articles/incose-requirements-quality-42-rule-guide), [Nature Sci Reports 2025 smell taxonomy](https://www.nature.com/articles/s41598-025-86673-w).

---

## 3. SMART / measurable business objectives

The SMART framework (Specific, Measurable, Achievable, Relevant, Time-bound) is the standard checklist used across BA/PM literature (Atlassian, CMI, Tability, WordStream, Personio all converge on the same 5 dimensions — this is genuinely consensus, not one vendor's spin).

**Testability checklist for "is this objective actually measurable":**
1. Does it contain a **number** (target value) — not just a direction ("increase," "improve," "reduce")?
2. Does it name the **metric/instrument** used to measure it (which system, which report, which dashboard)?
3. Does it have a **deadline or time window**?
4. Does it name an **accountable owner** (person/role/team)?
5. Does it state a **baseline** to measure the delta against (current state)?
6. Is the target **achievable** given known constraints (budget/headcount/timeline stated elsewhere in the BRD) — or is it a number pulled from nowhere?
7. Is it traceable to a **business driver** (why this objective, in one clause)?

A stated objective failing checks 1–3 is not measurable and should score near zero on this criterion regardless of how well-written the prose is.

**5 weak → strong rewrite examples:**

1. Weak: "Improve customer satisfaction."
   Strong: "Increase CSAT score from 72 (Q2 2026 baseline, quarterly survey) to ≥85 by Q4 2026, owned by Head of CX."

2. Weak: "Reduce our profits' cost base."
   Strong: "Reduce cloud infrastructure spend by 15% (from $180K/mo to ≤$153K/mo) within 6 months, owned by VP Engineering, tracked via AWS Cost Explorer monthly report."

3. Weak: "Make the platform more scalable."
   Strong: "Support 50,000 concurrent users at ≤500ms p95 API latency by end of Q1 2027, up from current tested ceiling of 8,000 concurrent users, validated via load testing before go-live."

4. Weak: "Increase website traffic."
   Strong: "Increase organic website traffic 25% (from 40K to 50K monthly sessions, GA4) within 6 months via SEO investment, owned by Marketing."

5. Weak: "We need to increase our sales."
   Strong: "Sell 5,000 units/month by Q3 2026, up from the current 3,200 units/month baseline, owned by UK Sales Director, tracked in the CRM pipeline report."

Sources: [tutor2u SMART Objectives](https://www.tutor2u.net/business/reference/smart-objectives-a-level), [CMI Setting SMART Objectives Checklist](https://www.managers.org.uk/wp-content/uploads/2020/03/CHK-231-Setting_Smart_Objectives.pdf), [Atlassian — How to write SMART goals](https://www.atlassian.com/blog/productivity/how-to-write-smart-goals), [WordStream SMART goal examples](https://www.wordstream.com/blog/smart-goals-examples)

---

## 4. Non-functional requirements quality — categories + quantified vs vague

Standard NFR categories, cross-referenced to ISO/IEC 25010's product-quality characteristics (§1.6) plus the practitioner categories BAs actually use in BRD templates (performance, scalability, availability, security, usability, compliance, maintainability, portability, data retention, localization, accessibility):

| Category | Vague (fails) | Quantified (passes) |
|---|---|---|
| Performance | "The system shall be fast." | "API p95 response time ≤300ms and p99 ≤800ms under 1,000 req/sec load, measured via [load-test tool]." |
| Scalability | "The system shall scale to support growth." | "The system shall support horizontal scale-out to 10,000 concurrent users with linear cost growth ≤$X per additional 1,000 users, validated by load test before GA." |
| Availability | "The system shall be highly available." | "99.9% uptime per calendar month (≤43.8 min downtime), with RTO ≤1 hour and RPO ≤15 minutes, per the DR runbook." |
| Security | "The system shall be secure." | "The system shall enforce TLS 1.2+ for all traffic, encrypt PII at rest (AES-256), pass an annual third-party pen test with zero critical/high findings open >30 days, and comply with OWASP ASVS Level 2." |
| Usability | "The system shall be user-friendly." | "A first-time user shall complete the core task (order placement) in ≤3 minutes with ≤2 errors, per moderated usability testing with n≥8 users; SUS score ≥75." |
| Compliance | "The system shall be compliant." | "The system shall comply with [GDPR Art. 17 right-to-erasure / DPDP Act 2023 / SOC 2 Type II / PCI-DSS v4.0] — name the specific regulation/standard and article/control number." |
| Maintainability | "The code shall be maintainable." | "Cyclomatic complexity ≤10 per function (enforced via CI linter), unit test coverage ≥80%, mean time to deploy a hotfix ≤2 hours." |
| Portability | "The system shall be portable." | "The system shall deploy to AWS, Azure, and on-prem Kubernetes via a single Helm chart with zero cloud-provider-specific code in the application layer." |
| Data retention | "Data shall be retained appropriately." | "Transaction records retained 7 years (statutory), PII anonymized 90 days after account closure, audit logs retained 1 year, per [named regulation]." |
| Localization | "The system shall support multiple languages." | "The system shall support English, Hindi, and Marathi UI strings (ISO 639-1 codes: en, hi, mr) with RTL layout not required for v1; date/currency formats per user locale (Intl API)." |
| Accessibility | "The system shall be accessible." | "The system shall conform to WCAG 2.2 Level AA, verified via axe-core automated scan (zero critical violations) and one manual screen-reader pass (NVDA/JAWS) before release." |

**The metric+threshold format professionals use, generalized:** `<measurable attribute> <comparison operator> <numeric threshold> <unit>, measured/verified via <method/tool>, under <conditions>`. A quantified NFR that is missing the "measured via" clause is still weak — verifiability requires stating *how* it will be checked, not just the number (this is INCOSE's Verifiable characteristic, §1.1/1.2).

Sources: [RadView — NFRs for Performance Testing](https://www.radview.com/blog/non-functional-requirements-nfrs-for-performance-testing/), [Perforce — NFR Tips, Tools, Examples](https://www.perforce.com/blog/alm/what-are-non-functional-requirements-examples), [Spyrosoft — The key to system quality: NFRs](https://spyro-soft.com/blog/managed-services/the-key-to-system-quality-non-functional-requirements), [Cal Poly — Nonfunctional Requirements](https://users.csc.calpoly.edu/~jdalbey/SWE/QA/nonfunctional.html), [ISO/IEC 25010 categories via arc42](https://quality.arc42.org/standards/iso-25010)

---

## 5. Scope-quality criteria

Reviewers judge scope quality on three things, consistently across PM/BA sources:

1. **Explicit boundary, both directions.** A scope section is only complete if it states both **In Scope** (what will be delivered) and **Out of Scope** (what will explicitly not be delivered in this phase/release). Multiple independent sources converge: "write down, in explicit detail, what's in scope, and critically, create an 'Out of Scope' section" [ScopeStack]; a scope-of-work "should ... explicitly document what is out of scope to prevent misunderstandings and scope creep" [SayAnchor]. **An automated scorer should treat a missing/empty Out-of-Scope section as a hard structural defect**, not a stylistic nicety — this is the single most commonly cited concrete BRD-scope failure mode across PM literature.

2. **Why explicit out-of-scope matters (the mechanism):** scope creep is specifically defined as "when out-of-scope work is added to the project without formal review, approval, or adjustment to timeline, budget, or effort" [Atlassian]. Without a written Out-of-Scope list, there is no artifact to point to when a stakeholder requests something outside the original intent — the change-control gate has nothing to gate against. An explicit Out-of-Scope section is therefore the mechanism that makes a formal change-request process possible at all, not decorative.

3. **Prioritized must-have vs nice-to-have scope language.** Scope items should be tagged (MoSCoW: Must/Should/Could/Won't, or similar) — "must haves are absolutely critical... nice to haves are items the client can live without." Scope written as an undifferentiated flat list (no priority tiering) is a quality defect because it gives no signal for scope-cut decisions under schedule pressure.

**Scope-creep-prone language patterns to detect (extends §2's smell list to scope specifically):**
- Open-ended clauses in scope statements ("and other related features," "etc.") — same INCOSE R9 smell, scope-specific application.
- Scope items phrased as vague capabilities rather than concrete deliverables ("improve the user experience" as a scope line item vs "redesign checkout flow screens 1–4").
- No version/phase tag on scope items (nothing distinguishing "v1 scope" from "future phase") — this is itself a completeness defect, since it invites creep-by-ambiguity.

Sources: [Atlassian — Scope Creep in Project Management](https://www.atlassian.com/work-management/project-management/scope-creep), [ScopeStack — What is Out of Scope](https://scopestack.io/blog/what-is-out-of-scope), [SayAnchor — What Is out of scope? A guide to stop scope creep](https://www.sayanchor.com/post/out-of-scope-work), [PMI — Top Five Causes of Scope Creep](https://www.pmi.org/learning/library/top-five-causes-scope-creep-6675), [BA Times — How to Prevent Scope Creep](https://www.batimes.com/articles/how-to-prevent-scope-creep-a-business-analyst-perspective/), [Asana BRD Template](https://asana.com/resources/business-requirements-document-template)

---

## 6. Traceability / completeness checks — fully automatable structural checks

These are graph/set checks over the BRD's structured entities (objectives, requirements, stakeholders, risks, assumptions) — no NLP needed, just relational integrity checks, analogous to foreign-key constraints in a database. This list is the most directly implementable part of a scorer.

1. **Orphan requirements** — a requirement with no link to any business objective. Industry framing: "there should be no orphans (no code or requirement that does not trace to... a higher-level requirement)" [Ketryx/Perforce RTM literature]. Detect: for each requirement row, check for a non-null `objective_id` (or equivalent) foreign key.
2. **Barren objectives** — a business objective with zero requirements tracing to it (stated goal with no execution plan). Detect: inverse of #1 — group requirements by objective_id, flag objectives with count=0.
3. **Requirements with no acceptance criteria** — every requirement should have a defined "done" condition (this is the operational form of INCOSE's Verifiable characteristic, §1.1). Detect: check for non-empty acceptance-criteria field per requirement row.
4. **Untested requirements / requirements without a verification method** — flag requirements missing a stated verification method (test/inspection/analysis/demonstration, per 29148's four standard V&V methods).
5. **Stakeholders with no RACI assignment** — every stakeholder listed should appear at least once in a RACI matrix (as R, A, C, or I on at least one activity/deliverable). Detect: set difference between the Stakeholders list and the set of names appearing in the RACI matrix.
6. **RACI rows with no "Accountable"** — every RACI row/activity must have exactly one "A" (single point of accountability is a RACI-integrity rule, not a style preference — multiple or zero "A"s is a structural defect).
7. **Risks with no mitigation** — every entry in a Risk register should have a non-empty mitigation/response field. Also check for missing risk owner and missing likelihood/impact rating.
8. **Assumptions with no owner or validation date** — assumptions are inherently unverified claims the project is built on; each should have an owner responsible for confirming/invalidating it and (ideally) a target validation date. A BRD with an Assumptions list but no owners/dates is treated as incomplete.
9. **Duplicate requirement IDs** or **broken ID references** (a traceability link pointing to an ID that doesn't exist in the requirements table) — pure referential-integrity check.
10. **Requirements with no priority tag** — every requirement should carry a MoSCoW/priority value (ties to Wiegers' "Prioritized" characteristic, §1.4).
11. **Glossary coverage** — domain terms used ≥N times in the requirements text but absent from the glossary (ties to INCOSE R4, §2 defect #13).
12. **Version/scope tag coverage** — scope/requirement items with no phase or release tag (ties to §5's scope-creep check).
13. **Missing "Out of Scope" section entirely**, or an Out-of-Scope section with zero content (§5).
14. **Objectives with no measurable target** — objectives missing a number/metric field (§3 checklist items 1–3, made structural).

Sources: [Ketryx — Ultimate Guide to Requirements Traceability Matrix](https://www.ketryx.com/blog/the-ultimate-guide-to-requirements-traceability-matrix-rtm), [Perforce — Requirements Traceability Matrix](https://www.perforce.com/resources/alm/requirements-traceability-matrix), [Virtuoso QA — RTM Explained (orphan requirements framing)](https://www.virtuosoqa.com/post/requirements-traceability-matrix-rtm), [Jama Software — What is a Traceability Matrix](https://www.jamasoftware.com/requirements-management-guide/requirements-traceability/traceability-matrix)

---

## 7. Proposed weighted 0-100 rubric

This rubric synthesizes §1–6 into 10 weighted criteria. Weights are justified per-row from the sources above; none are arbitrary. Detection column marks whether each is (a) purely rule-based/structural, (b) NLP/smell-detectable, or (c) requires an LLM judge for semantic assessment (business-alignment, correctness).

| # | Criterion | Weight | Full marks (100%) | Zero marks (0%) | Detection method |
|---|---|---|---|---|---|
| 1 | **Objectives are SMART/measurable** | 12 | Every business objective has a number, metric, baseline, deadline, owner (§3 checklist, all 5 present) | Objectives are pure aspiration with no metric ("improve efficiency") | Rule-based: regex for numerals/% + LLM judge to confirm metric is genuinely the objective's success measure, not incidental |
| 2 | **Requirements are atomic & unambiguous (INCOSE R1–R19 core)** | 15 | Zero compound requirements (no "and/or" joining independent obligations), zero vague-pronoun/subjective-language hits, active voice with named actor throughout | Widespread compound requirements, vague pronouns, passive voice with no actor | NLP: POS-tag + Femmer smell dictionary (§2 items 1,2,6,9,10) — direct precedent: Smella tool, precision 0.59/recall 0.82 |
| 3 | **Requirements are verifiable (measurable targets, no loopholes/escapes)** | 15 | Every requirement has a quantified, testable target with unit+tolerance; zero escape clauses, zero open-ended clauses, zero superlatives/comparatives without baseline | Requirements full of "as appropriate," "etc.," "best possible," no numbers anywhere | NLP: keyword/dictionary match against INCOSE R7/R8/R9 word lists (§2 items 3,4,5,7,8,11,12) — highest-confidence rule-based layer, directly copy INCOSE's published trigger-word lists |
| 4 | **NFRs are present and quantified across standard categories** | 12 | All applicable ISO 25010-aligned NFR categories (performance, availability, security, scalability, usability, maintainability, compliance, accessibility) present with metric+threshold+method format (§4) | NFR section missing entirely, or present only as adjectives ("secure," "fast," "scalable") with no numbers | Rule-based coverage check (category presence) + NLP pattern match for `<metric> <operator> <threshold> <unit>` per category |
| 5 | **Scope is explicit, bounded, and prioritized** | 10 | Both In-Scope and Out-of-Scope sections present and non-empty; scope items tagged must/should/could; phase/version tags present | No Out-of-Scope section, or scope items are vague capability statements with no boundary | Rule-based: section-presence + non-empty check; NLP for vague-capability language in scope lines |
| 6 | **Traceability completeness (structural graph integrity)** | 12 | Zero orphan requirements, zero barren objectives, zero duplicate/broken IDs, every requirement has acceptance criteria + priority + verification method | Requirements table has no linkage fields at all, or majority of rows fail linkage checks | Pure structural/relational check — no NLP needed (§6 items 1–4, 9, 10) |
| 7 | **Stakeholder/RACI completeness** | 8 | Every listed stakeholder appears in RACI with a role; every RACI row has exactly one Accountable | Stakeholder list exists with no RACI, or RACI has rows with 0 or 2+ "A"s | Structural set-difference + integrity check (§6 items 5, 6) |
| 8 | **Risk & assumption management completeness** | 8 | Every risk has mitigation + owner + likelihood/impact; every assumption has owner + validation date | Risk/assumption lists present but fields empty, or sections entirely absent | Structural field-presence check (§6 items 7, 8) |
| 9 | **Terminology consistency / glossary discipline** | 5 | All domain terms used ≥3 times appear in glossary; no term used with 2 conflicting definitions | No glossary at all in a document using domain jargon; terms used inconsistently | NLP: term-frequency index + embedding-similarity drift check (§2 item 13, INCOSE R4/R36) |
| 10 | **Business-alignment & non-hallucination (LLM-judge only)** | 3 | Requirements/objectives/stakeholders plausibly correspond to a real, coherent business context; no fabricated compliance claims, no invented named systems/regulations that don't exist | Fabricated stakeholder names/titles, invented regulation names, invented metrics with no source, generic filler sections with no business specificity | LLM judge only — this is exactly the LLM-generated-document failure mode class from §8; cannot be rule-based |

**Total: 100.**

**Weighting rationale summary:**
- Criteria 2+3 (atomicity + verifiability) together = 30% because these are the two characteristics *every* source in §1 converges on as most fundamental (ISO 29148's Unambiguous/Verifiable, INCOSE's core Accuracy+Non-Ambiguity rule blocks R1–R19, Wiegers' Unambiguous/Verifiable, Femmer's entire smell taxonomy exists to detect exactly these two failure classes).
- Criterion 6 (traceability) gets 12% because both Wiegers ("Traceable" is one of only 4 spec-level characteristics) and ISO 29148 (set-level "Complete") name it explicitly, and it's the highest-confidence, zero-false-positive detection layer available (pure structural check) — worth weighting up because it's cheap to verify with certainty.
- Criterion 4 (NFRs) at 12% reflects that NFRs are routinely the weakest section in real BRDs (per practitioner sources in §4) and ISO 25010 gives a defined, checkable category list.
- Criterion 10 (business-alignment/hallucination) is deliberately low weight (3%) because it is the least reliably automatable (only an LLM judge, no ground truth), but it must exist given this scorer's explicit use case includes checking LLM-generated BRDs (§8) — a hallucinated-but-otherwise-well-formatted document should not score 100.
- Criteria 7+8 (RACI, risk/assumptions) get moderate weight (8% each) — these are standard BA deliverable components but are secondary to the core requirements-quality criteria per every source surveyed; still fully structural/automatable so cheap to include.

**Calibration note:** because rule-based/NLP smell detectors have a published precision ceiling (Smella: 0.59 precision — [Femmer et al.](https://arxiv.org/pdf/1611.08847)), the recommended architecture is: rule-based/NLP layer flags candidates → LLM judge confirms/dismisses each flag before it affects the score. Do not let raw regex/dictionary hit-counts drive the score unfiltered, or false positives will dominate criteria 2, 3, and 9.

---

## 8. Known pitfalls of LLM-generated requirements documents

Published empirical evaluation: **"Using LLMs in Software Requirements Specifications: An Empirical Evaluation"** (arXiv:2404.17842) systematically assessed LLM-generated SRS documents against Completeness, Clarity, Consistency, Correctness, and Traceability, and found the following failure modes — directly relevant since this is the closest published empirical study to our exact use case:

1. **Hallucination & fabrication** — LLMs generated requirements referencing features/metrics that were never actually part of the real system/product being specified (i.e., invented functionality not grounded in any actual input).
2. **Generic filler content** — vague, boilerplate requirement language lacking specific technical detail or measurable criteria (this is the same failure class as §2's smell taxonomy — but LLMs produce it systematically, not occasionally).
3. **Solution-oriented language creep** — requirements specify *implementation approach* rather than *need/behavior* (directly violates INCOSE R31 "Solution-Free," §1.2). LLMs default to prescribing a specific tech/design because that's a more "complete-sounding" continuation than staying abstract.
4. **Invented metrics** — LLMs fabricate specific-sounding performance targets/numbers with no grounding in real system data (e.g., "the system shall respond within 200ms" with no source for why 200ms) — dangerous because a naive rubric that just rewards "has a number" would score these highly despite the number being fabricated. This is precisely why criterion 10 (business-alignment/non-hallucination) must exist as a distinct LLM-judge check separate from "is this requirement quantified" (criterion 3).
5. **Inconsistency** — generated requirement sets contain internally contradictory specifications and near-duplicate/redundant statements (violates INCOSE R30 Unique Expression + ISO 29148's set-level Consistent characteristic).
6. **Loss of broader context on complex/long documents** — a related paper (broader GenAI-for-SE research agenda, arXiv:2310.18648) notes generative models "often lose broader context... potentially leading to discrepancies or conflicts within generated requirements," especially as document length grows — relevant because a full BRD is a long-context generation task.

**On evaluation methodology itself:** the same study flagged a meta-problem worth building into our scorer's design — LLM-generated requirements were rated "acceptable to high" on structural criteria (atomicity, consistency, correctness) by RE-expert reviewers, but the researchers explicitly cautioned that "true requirements must originate from or be validated by the customer, not just RE experts" — i.e., **structural quality and business validity are separate axes**, and a document can score well structurally while still being wrong about what the business actually needs. This is the core justification for keeping criterion 10 separate and LLM-judge-based rather than folding "correctness" into the same NLP layer as the smell/structure checks — structural well-formedness cannot certify business correctness, only a human or a context-grounded judge can.

Additional mitigation research: "Refine and Thought (RaT)" methodology (referenced in search results, not independently verified in depth here) proposes shortening/sharpening input context specifically to reduce hallucination when LLMs process/analyze complex requirements documents — relevant if our scorer itself uses an LLM judge, since the judge is equally susceptible to the same hallucination failure mode when reasoning over a long BRD. [unverified — could not independently confirm RaT methodology details or publication venue; flagging for follow-up rather than citing as fact.]

Sources: [arXiv:2404.17842 — Using LLMs in Software Requirements Specifications: An Empirical Evaluation](https://arxiv.org/pdf/2404.17842), [Literature review summary of same](https://www.themoonlight.io/en/review/using-llms-in-software-requirements-specifications-an-empirical-evaluation), [arXiv:2507.19113 — Exploring the Use of LLMs for Requirements Specification](https://arxiv.org/pdf/2507.19113), [arXiv:2310.18648 — Generative AI for Software Engineering, A Research Agenda](https://arxiv.org/pdf/2310.18648), [arXiv:2501.19297 — Analysis of LLMs vs Human Experts in Requirements Engineering](https://arxiv.org/pdf/2501.19297)

---

## Summary / what to build directly from this brief

1. **Rule-based/regex layer**: implement INCOSE R7, R8, R9, R26, R32, R33 word/pattern lists verbatim (§1.2, §2) — highest confidence, lowest cost, directly sourced from a named standard.
2. **NLP smell layer**: implement Femmer's 9(+2) smells (§1.5, §2) using POS tagging for structural smells (superlative/comparative/negative/pronoun) and dictionary lookup for lexical smells (subjective/vague-adverb/non-verifiable) — expect ~0.6 precision, filter with an LLM judge before scoring impact.
3. **Structural/relational layer**: implement all 14 traceability checks in §6 as pure data-integrity constraints over the BRD's parsed entity tables (objectives, requirements, stakeholders, RACI, risks, assumptions, scope) — zero false positives, cheapest to build, should be built first.
4. **LLM-judge layer**: reserved for exactly 3 things this cannot be rule-based for — (a) SMART-objective semantic check (is the stated metric *actually* the success measure, §3), (b) NFR-category semantic coverage (is "the system shall be scalable" *actually* addressed elsewhere with real numbers, §4), (c) business-alignment/hallucination check (§7 criterion 10, §8) — keep this layer's weight low (per §7) since it's the least certifiable.
5. Use the §7 rubric table as the literal scoring spec — every weight and pass/fail criterion in it traces to a named source above.
