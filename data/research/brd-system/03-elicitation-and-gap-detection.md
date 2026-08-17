# Research Brief: BA Elicitation Question Banks & Gap Detection (for BRD-drafting system)

**Purpose:** Ground the "idea paragraph → draft BRD → detect gaps → ask top ~10 blocking questions" system in real business-analyst practice, not invented questions. Compiled 2026-07-29.

---

## 1. Real BA elicitation question banks (by category)

Practitioner sources agree there is no single canonical list — but there is a canonical **method**: the "6 basic questions" frame (Who/What/Where/When/How/Why), applied recursively to every requirement object. Laura Brandenburg (CBAP, Bridging the Gap) built a paid 700+ question "Requirements Discovery Checklist Pack" organized into 40+ categories, and publishes a free literal-question sample using the W-framework ([bridging-the-gap.com](https://www.bridging-the-gap.com/what-questions-do-i-ask-during-requirements-elicitation/)). The Business Analyst Toolkit publishes a similar open framework ([businessanalyststoolkit.com](https://www.businessanalyststoolkit.com/requirements-elicitation-questions/)), and `thebusinessanalystjobdescription.com` has a 60-question interview-question set organized loosely by theme (foundation, techniques, scenario, documentation, industry-specific, best practices) rather than strict W-buckets ([source](https://thebusinessanalystjobdescription.com/requirements-gathering-interview-questions/)).

Below is a synthesized bank, organized into the 11 categories the parent system needs, each with 8-12 literal questions built from the patterns found in these sources plus standard BABOK/PMI elicitation practice. Treat these as the seed bank the system's question-generator should draw from and adapt per business type (see §8).

### A. Business context & problem
1. What business problem are you trying to solve, in one sentence?
2. What is happening today that shouldn't be happening (or not happening that should)?
3. Who first noticed this problem, and how long has it existed?
4. What triggered you to act on this now, rather than 6 months ago or 6 months from now?
5. What have you already tried to fix this? Why didn't it work?
6. If this project didn't happen, what would you do instead?
7. Is this a new capability, or a replacement/improvement of an existing one?
8. Who is your competitor/comparator doing this well, if anyone?
9. What is the cost of doing nothing?
10. Is this problem isolated to one team/region, or organization-wide?
11. What assumptions are you making about the cause of this problem?

### B. Goals & success metrics
1. How will you know, six months after launch, that this was a success?
2. What is the single metric that matters most (North Star)?
3. What is the target number, and what is the number today (baseline)?
4. Who owns that metric after launch?
5. Is this a revenue play, cost-reduction play, risk-reduction play, or experience play?
6. What does "good enough to ship" look like, versus "ideal"?
7. Are there secondary metrics that must not regress (guardrails)?
8. What's the timeframe expectation — weeks, quarter, year?
9. How will success be measured — survey, analytics event, revenue report, support ticket volume?
10. Is there a deadline tied to an external event (funding round, compliance date, seasonal peak)?

### C. Stakeholders & users
1. Who will actually use this day-to-day? (Not who requested it — who touches it.)
2. Who can say no / block this even if everyone else agrees? (True approver)
3. Who is affected but wasn't in the room for this conversation?
4. What roles/permission levels exist among users?
5. Are there external users (customers, vendors, regulators) as well as internal ones?
6. Who will support/maintain this after launch?
7. Who is the budget owner?
8. Are there unions, works councils, or legal/compliance stakeholders who must sign off?
9. What's the technical sophistication of the least tech-savvy user in scope?
10. Who loses something (time, control, job function) if this succeeds — and have they been consulted?

### D. Current process (as-is)
1. Walk me through, step by step, how this happens today.
2. What tools/systems are used at each step?
3. Where does the process start and where does it end?
4. What's the volume today (how many times a day/week/month)?
5. Where do delays or bottlenecks happen currently?
6. What manual workarounds exist that "everyone just knows"?
7. Who does each step, and how long does it take them?
8. What data is captured today, and where does it live?
9. What happens when something goes wrong in the current process?
10. What's the worst part of the current process, from the user's point of view?
11. Is there a "shadow process" (spreadsheet, WhatsApp group, personal notebook) propping up the official one?

### E. Desired process (to-be)
1. Walk me through how you imagine this working, step by step.
2. What should stay exactly the same, and what must change?
3. Who initiates the new process, and what triggers it?
4. What's the ideal number of steps/clicks/approvals?
5. Should this be fully automated, or human-in-the-loop?
6. What does "done" look like for one instance of this process?
7. Are there steps in the current process that should be eliminated, not just improved?
8. What's the desired turnaround time end-to-end?
9. Should the new process run in parallel with the old one during a transition, or cut over immediately?
10. What existing systems must the new process integrate with, not replace?

### F. Data & integrations
1. What data does this feature need to create, read, update, or delete?
2. Where does that data come from — user input, another system, a third party?
3. What existing systems must this integrate with (CRM, ERP, payment gateway, auth provider)?
4. Is there an existing API, or does one need to be built?
5. What's the data format (structured, unstructured, files, streams)?
6. Who owns the source-of-truth for each data entity if there are multiple systems involved?
7. Does data need to sync in real-time, or is batch/nightly acceptable?
8. What happens if an integration is down — does the whole flow fail, or degrade gracefully?
9. Is there existing (legacy) data that needs to be migrated in?
10. What's the data quality of that legacy data — has it been audited?
11. Are there data ownership or contractual restrictions with third parties (can you legally use this data this way)?

### G. Volumes & scale
1. How many users will use this on day one? In year one?
2. What's the peak load — is there a seasonal, daily, or event-driven spike?
3. How many transactions/records per day is this expected to handle?
4. What's the expected data growth rate per year?
5. Are there multiple geographies/time zones/languages to support?
6. What's the largest single file/record/batch size expected?
7. Is there a hard ceiling (contractual, regulatory, or physical) on scale?
8. What happens to performance if volume is 10x higher than expected?

### H. Constraints (budget/time/regulatory)
1. What is the budget range for this project?
2. Is there a hard deadline, and what happens if it's missed?
3. What regulations apply to this business/data (see §6)?
4. Are there existing vendor contracts or platform lock-ins that constrain tool choice?
5. Is there an internal security/architecture review this must pass?
6. What is explicitly out of scope for this phase?
7. Are there brand, legal, or accessibility standards that must be followed?
8. Is there a preferred or mandated technology stack?
9. Are there internal politics/dependencies (another team's roadmap) that could block this?

### I. Edge cases & exceptions
1. What happens when a user does something unexpected — enters wrong data, abandons midway, does it twice?
2. What happens if two people try to do the same action at the same time?
3. What's the process when data is missing or incomplete?
4. What happens at the boundary — zero items, maximum items, exactly one?
5. What happens if a required third-party service is unavailable mid-transaction?
6. What happens if a user's permissions change while they're mid-task?
7. Are there VIP/exception cases that bypass the normal rules?
8. What's the "undo" story — can actions be reversed, and by whom?
9. What happens on partial failure (some of 100 records succeed, some fail)?
10. Is there a fraud/abuse scenario that needs to be designed against?

### J. Reporting needs
1. Who needs to see reports on this, and how often (daily/weekly/monthly)?
2. What decisions will be made based on this report?
3. What format is expected — dashboard, PDF, spreadsheet export, email digest?
4. Does this need to reconcile against another system's numbers (finance, audit)?
5. Who is allowed to see which data in the report (are there permission tiers in reporting)?
6. Does history need to be preserved for trend analysis, and for how long?
7. Are there existing report definitions this must match or replace?
8. Is real-time reporting needed, or is periodic/batch sufficient?

### K. What happens when things go wrong (failure & escalation)
1. Who gets notified when this process fails, and how (email, Slack, page)?
2. What's the acceptable time-to-detect and time-to-resolve for a failure?
3. Is there a manual fallback if the system is down?
4. Who has authority to override or manually correct a bad outcome?
5. What's logged when something fails, for post-mortem purposes?
6. Is there a legal/compliance obligation to report certain failures (breach, mis-transaction)?
7. What's the blast radius if this fails silently for a day before anyone notices?
8. Is there a rollback plan if a deployment/change causes an incident?

**Assessment for the system:** these categories map close to 1:1 onto what an AI-driven intake needs, but a real BA does NOT ask all ~100 questions verbatim to every stakeholder — they ask **2-4 opening questions per category**, listen for gaps, and drill down with follow-ups only where the answer reveals risk. The system should mirror this: use this bank as a **candidate pool for gap-triggered question generation**, not a fixed questionnaire.

---

## 2. BABOK elicitation techniques — applicability to a single-user AI interview

BABOK v3 (IIBA) names techniques under the "Elicitation and Collaboration" knowledge area; the commonly cited set is Brainstorming, Document Analysis, Focus Groups, Interface Analysis, Interviews, Observation, Prototyping, Requirements Workshops, and Survey/Questionnaire, with Conduct Elicitation as the umbrella task ([IIBA BABOK 4.2](https://www.iiba.org/knowledgehub/business-analysis-body-of-knowledge-babok-guide/4-elicitation-and-collaboration/4.2-conduct-elicitation), [watermarklearning.com summary](https://www.watermarklearning.com/blog/babok-techniques/)). Effective real-world practice chains them: document analysis for context → interviews for depth → workshops for consensus → prototypes for validation ([theitba.com](https://www.theitba.com/elicitation-tasks-and-techniques/)).

| Technique | When appropriate | Output produced | Feasible for single-user AI interview? |
|---|---|---|---|
| **Interviews** | 1:1 depth on a specific stakeholder's needs, sensitive topics, early discovery | Narrative requirements, quotes, pain points | **Yes — this is the core mechanic.** The AI Q&A loop *is* a structured interview. |
| **Document analysis** | Existing docs, contracts, legacy specs, competitor sites exist to mine | Extracted requirements, gap list vs. existing docs | **Yes** — if user pastes/uploads existing docs, agent should parse before asking questions (avoid re-asking known answers). |
| **Requirements workshops** | Multiple stakeholders, need consensus/tradeoff negotiation live | Prioritized, agreed requirement set | **No** — needs multiple live humans in a room; not reproducible with one user. Could simulate by asking user to represent multiple stakeholder viewpoints sequentially. |
| **Observation / job shadowing** | Understanding real as-is workflow, especially where told-process ≠ actual process | Accurate as-is process map, uncovers undocumented workarounds | **No** — requires physical/screen presence over time. System should compensate by asking "walk me through your last real example" (a substitute: retrospective narrated observation). |
| **Prototyping** | Ambiguous UI/UX requirements, validate understanding before build | Refined, validated functional requirements | **Partially** — the system could show a draft wireframe/mockup of the BRD's proposed flow and ask "does this match what you meant?" as a lightweight prototype-review step. |
| **Brainstorming** | Early-stage, generating options, no wrong answers | Raw idea list, later filtered | **Limited** — a single user brainstorming with an AI is really just an extended interview; useful for the "any other requirements we haven't discussed?" catch-all question. |
| **Focus groups** | Get diverse user reactions (not decision-makers) to a concept | Qualitative reactions/preferences | **No** — needs multiple non-stakeholder participants; out of scope for a solo intake tool. |
| **Survey/questionnaire** | Broad reach, quantifiable, low-touch, many respondents | Aggregated, structured answers | **Yes, partially** — the top-10-blocking-questions list IS effectively a targeted, adaptive micro-survey. Should follow survey UX best practice (see §7), not open-ended long-form. |
| **Interface analysis** | Requirement touches an existing system's UI/API boundary | Integration requirements, data contracts | **Yes, if user has an existing product** — ask for existing screens/APIs and analyze; otherwise skip. |
| **Process modeling** (BPMN etc.) | As-is/to-be process needs to be visualized for sign-off | Process diagrams | **Partial** — the system can generate a process diagram *from* elicited answers as an artifact, not use it as an elicitation input technique on a first idea-paragraph pass. |

**Conclusion for design:** the system is fundamentally an **AI-mediated structured interview backed by document analysis**, functioning like an adaptive survey. Workshops, observation, focus groups are not reproducible solo — the system should explicitly flag to the user when a requirement really needs a workshop/observation ("this needs input from your ops team directly — I can't infer it") rather than pretending to resolve it via more Q&A.

---

## 3. JTBD / Five Whys / problem-framing — literal question ladders

**Five Whys** (Toyota Production System origin): ask "why did that happen?" repeatedly (typically ~5 times, flexible — stop when you reach an actionable, structural cause, not an infinite regress) ([businessanalystlearnings.com](https://www.businessanalystlearnings.com/ba-techniques/2013/2/5/root-cause-analysis-the-5-whys-technique), [watermarklearning.com](https://www.watermarklearning.com/blog/5-whys/)). Literal ladder pattern:
1. "You said you need [X feature]. Why do you need that?" → answer reveals a goal.
2. "Why is [goal] important to you right now?" → answer reveals a business driver.
3. "Why does [current process] not already achieve that?" → answer reveals the actual gap/failure point.
4. "Why hasn't that gap been closed already?" → reveals a structural/organizational/technical blocker.
5. "Why is this the year/quarter to fix it?" → reveals urgency and real constraint.
Each answer becomes the premise for the next "why" — this is the mechanism the elicitation agent should use whenever a user states a **solution** ("I need a dashboard") instead of a **problem** ("I don't know which orders are late").

**JTBD (Jobs-to-be-Done)**, from Clayton Christensen, reframed as: "people don't buy products, they hire them to make progress in a specific circumstance" ([HBS Online](https://online.hbs.edu/blog/post/jobs-to-be-done-examples)). Practical interview technique (Bob Moesta's "switch interview," refined further by Tony Ulwick's Outcome-Driven Innovation) asks about the **moment of switching**, not abstract preferences:
1. "What were you using/doing before you decided you needed this?" (the "fired" solution)
2. "What was the specific moment or event that made you start looking for something else?" (the trigger/"push")
3. "What were you afraid might happen if you didn't switch?" (anxiety of inaction)
4. "What almost stopped you from switching?" (habit/switching cost — "pull" friction)
5. "What does 'success' feel like once this job is done?" (functional + emotional + social job, per the 3-dimension JTBD model)
6. "If this new thing didn't exist, what's your fallback?" (reveals true urgency/alternative)

**Problem-framing more generally** (standard BA/consulting practice): before accepting a stated solution, ask:
- "What is the underlying business need this solution addresses?" (BABOK explicitly separates "business requirements" — the need — from "solution requirements" — the how)
- "If I gave you [stated solution] tomorrow, would the underlying problem actually be solved?"
- "Is there a simpler way to achieve the same outcome without building this?"

**For the system:** whenever the idea paragraph contains a *solution noun* ("I want an app that...", "build me a dashboard...") without a stated *problem*, trigger a Five-Whys-style drill-down as one of the mandatory blocking questions, not a nice-to-have — this is the single highest-leverage gap category because building the wrong solution is unrecoverable later.

---

## 4. Gap detection heuristics — "how does a BA know it's incomplete?"

Experienced BAs don't detect gaps by re-reading the requirements for what's there — they detect gaps by **running a fixed mental checklist of categories that are chronically under-elicited** and checking each one is explicitly addressed or explicitly waived. PMI's guidance on requirements risk explicitly frames this as looking for what's *absent*, not just conflicts in what's present ([PMI](https://www.pmi.org/learning/library/uncover-gaps-requirements-risk-management-9910)). The core insight from `businessanalystlearnings.com`: missing requirements are usually invisible to stakeholders because they assume it's "obvious" or "goes without saying" — precisely the pattern seen with NFRs ([forasoft.com NFR checklist](https://www.forasoft.com/blog/article/non-functional-requirements-checklist-2026)).

The standing checklist an experienced BA runs (each mapped to what to actually ask):

| Category | Why commonly missed | Trigger question |
|---|---|---|
| **Error/exception paths** | Stakeholders describe the happy path by default; unhappy paths require deliberate prompting ([ACM paper on exception-aware elicitation](https://dl.acm.org/doi/10.5555/2124243.2124259)) | "What happens when this step fails?" for every step in the to-be process |
| **Non-happy-path flows** (sad path, edge case, corner case — distinct categories per testing taxonomy) | Same as above; corner cases (multiple rare conditions at once) are almost never volunteered | "What's the weirdest real situation you've actually seen happen here?" |
| **Data migration** | Treated as a "technical detail" outside BRD scope, but it's a business risk (data loss, downtime) | "Is there existing data that must move into the new system? Has anyone audited its quality?" |
| **User roles & permissions** | Assumed to be "just admin and user" until launch reveals more roles are needed | "List every distinct type of user and what each can/can't do." |
| **Notification/alerting** | Considered a "nice to have" UI detail, not a requirement, until failures go unnoticed | "Who needs to be told when X happens, and how urgently?" |
| **Audit trail** | Invisible until a compliance/dispute event demands "prove who did what, when" | "If there's ever a dispute about who changed something, how would you find out?" |
| **Reporting & analytics** | Treated as a downstream/later concern, but retrofitting event tracking after launch is expensive | "What numbers will leadership ask about in month 1 that this system must be able to answer?" |
| **Offline/degraded behavior** | Only surfaces once a dependency actually goes down in production | "What should happen if [key integration/internet] is unavailable mid-task?" |
| **Capacity limits** | Assumed infinite by non-technical stakeholders | "What's the biggest single spike in usage you can imagine, and is that realistic?" |
| **Archival & retention** | Deferred as "we'll deal with it later," but retention has legal/regulatory teeth (SOX 7yr, HIPAA 6yr, GDPR/DPDPA purpose-limited) — see [archondatastore.com decommissioning guide](https://www.archondatastore.com/blog/data-center-decommissioning/) | "How long must this data be kept, and what happens to it after — delete, anonymize, archive?" |
| **Onboarding/offboarding of users** | Access provisioning is designed; de-provisioning on employee exit is routinely forgotten, a known security gap ([accountablehq.com access review](https://www.accountablehq.com/post/access-review-checklist-how-to-audit-and-certify-user-permissions)) | "When someone leaves or changes role, what needs to happen to their access, same day?" |
| **End-of-life/decommission** | Never considered at project-start time, but defines whether data/process is truly reversible | "If this project were shut down in 2 years, what needs to happen to the data and the users left behind?" |

**Meta-heuristic used by senior BAs (paraphrased across sources):** if a category of the above is answered with silence, a shrug, or "we'll figure it out later" — that is itself the signal of a gap, and the BA writes it down as an **assumption requiring explicit stakeholder sign-off**, not something to quietly invent. The system should replicate this: any checklist category not addressed by the idea paragraph or by document-analysis should generate either (a) a blocking question if the category is high-risk for this business type, or (b) a documented assumption the user can accept/reject with one click if low-risk.

---

## 5. Question prioritization — blocking vs. assumable, with a rankable heuristic

There is no single universally-cited "risk × impact of being wrong" scoring framework specific to requirements elicitation in the sources found — this section synthesizes three converging, well-established ideas into a usable heuristic. [unverified: no single named published framework combines these three axes exactly as below; this is a synthesis]

**Component 1 — Cost-of-change curve (Boehm, *Software Engineering Economics*, 1981):** the cost to fix a requirements-stage error grows roughly 1:100 by the time it's caught in production (smaller/agile projects closer to 1:4-10, not 1:100 — this ratio itself is contested by modern agile critics who argue continuous delivery flattens the curve for less-coupled changes) ([swreflections.blogspot.com](http://swreflections.blogspot.com/2013/09/the-real-cost-of-change-in-software.html), [Mountain Goat Software counterpoint](https://www.mountaingoatsoftware.com/blog/the-cost-of-change-curve-is-outdated), [arXiv empirical revisit](https://arxiv.org/pdf/1609.04886)). **Implication:** any wrong assumption baked into architecture-level decisions is exponentially more expensive to fix than one baked into UI copy — so *stage-of-impact* is one prioritization axis.

**Component 2 — Architecturally Significant Requirements (ASR):** a requirement is architecturally significant (and therefore must be resolved before build, not assumed) if it has high business value/technical risk, is a concern of an influential stakeholder, is first-of-its-kind (no existing pattern handles it), has SLA/QoS characteristics that deviate from the norm, or is cross-cutting (touches multiple parts of the system) ([Wikipedia](https://en.wikipedia.org/wiki/Architecturally_significant_requirements), [IASA Global](https://iasaglobal.org/Public/Public/TOPICS/Architecturally-Significant-Requirements.aspx)). **Implication:** a second axis is *architectural reach* — does the unknown answer change the data model, the auth model, the integration surface, or the compliance posture? If yes, it's blocking. If it only changes copy/layout/a config value, it's assumable.

**Component 3 — MoSCoW prioritization** (also BABOK-referenced): categorize into Must/Should/Could/Won't, with the rule-of-thumb distribution ~60% Must, 25% Should, 10% Could, 5% Won't ([agilebusiness.org](https://www.agilebusiness.org/resource/what-is-moscow-prioritization/), [business-analysis-excellence.com](https://business-analysis-excellence.com/moscow-analysis/)). **Implication:** apply MoSCoW not to features, but to *the unknowns themselves* — is resolving this unknown a Must (blocks any coherent build), Should (materially changes scope/cost but a reasonable default exists), Could (nice precision, safely assumed), or Won't (out of scope, don't even ask)?

**Concrete rankable heuristic for the system** — score every candidate gap on two axes, 1-3 each, multiply:

- **Reversibility cost (1-3):** 1 = cheap to change later (copy, a default value, an optional field) · 2 = moderate (a UI flow, a report format) · 3 = expensive/irreversible (data model, auth/roles model, payment/compliance flow, core integration architecture, anything touching regulated data)
- **Assumption-confidence (1-3):** 1 = a safe, industry-standard default exists and is very likely correct (e.g., "assume email+password auth unless told otherwise") · 2 = a plausible default exists but could easily be wrong for this specific business · 3 = no safe default exists; answer could go multiple very different directions (e.g., "who are your users" for an ambiguous idea paragraph)

**Blocking score = Reversibility cost × Assumption-confidence.** Score ≥ 6 → must be a blocking question. Score 3-4 → optional/secondary question if budget allows (the top-10 list should prefer these only after all ≥6 items are covered). Score ≤ 2 → silently resolve with a documented, reviewable assumption in the draft BRD, don't ask.

This directly operationalizes "ask only the top ~10 blocking questions": rank all detected gaps by this score, take the top ~10, and downgrade everything else to an explicit, editable assumption in the draft.

---

## 6. Domain-triggered compliance questions

| Domain / trigger | Regulation | What triggers the requirement | Question(s) to ask |
|---|---|---|---|
| **Payments** | PCI-DSS (global card-data standard, 12 requirements across 6 themes: network security, cardholder data protection, vulnerability mgmt, access control, monitoring/testing, security policy) ([secureframe.com](https://secureframe.com/blog/pci-compliance-checklist)) | System stores, processes, or transmits cardholder data (even transiently) | "Will you ever touch raw card numbers, or will a hosted/tokenized gateway (Stripe/Razorpay checkout) keep card data off your servers?" — if the former, PCI-DSS SAQ level applies and should be flagged as a major architectural constraint |
| **Payments (India)** | RBI Payment Aggregator rules + data localization directive: all payment-system data (transaction details, credentials, logs) must be stored exclusively on India-located servers; if processed abroad, a full copy must return to India within 24h; PA license needs ₹15cr min net worth at application, ₹25cr by year 3 ([SmartX Solutions](https://www.smartxsolutions.in/blog/rbi-compliance-fintech-apps-india), [IncorpX](https://www.incorpx.io/blog/rbi-payment-aggregator-license-2026)) | Any India-facing product that aggregates/collects payments on behalf of merchants, or stores Indian users' transaction data | "Will payment data ever be processed or stored outside India, even briefly? Are you aggregating funds for third-party merchants (triggers PA license) or just your own sales (does not)?" |
| **Healthcare (US)** | HIPAA — covered entities/business associates handling PHI need risk assessment, audit controls, BAAs with vendors, encryption, access controls, staff training ([Kiteworks](https://www.kiteworks.com/hipaa-compliance/hipaa-compliance-requirements/), [HIPAA Journal](https://www.hipaajournal.com/hipaa-compliance-checklist/)) | System creates/receives/stores/transmits any individually-identifiable health information for a US healthcare provider, payer, or their vendor | "Does this system touch any US patient health/treatment/payment data? Will you sign Business Associate Agreements with any vendors you use?" |
| **Healthcare (India)** | ABDM/ABHA — health apps integrating with India's digital health stack must store clinical records in FHIR R4 format, support the HIE-CM consent manager with 4-state consent (grant/revoke/pause/expire) at artefact-level granularity, federated storage (no central repository) ([productgrowth.in ABDM guide](https://productgrowth.in/insights/healthtech/abdm-digital-health-regulations/), [Ailoitte](https://www.ailoitte.com/blog/abha-abdm-patient-centric-healthcare/)) | Product is a hospital/clinic/lab/pharmacy system in India intending ABDM interoperability, or handles ABHA-linked records | "Do you need this system to interoperate with ABDM (ABHA-linked records, other hospitals/labs)? If yes, records must be FHIR R4 and consent must be artefact-level and revocable." |
| **Personal data (EU)** | GDPR — Article 25 privacy-by-design/default, data minimization, DPIAs for high-risk processing, data subject rights (access/erase/port/restrict), 72-hour breach notification, DPAs with processors ([CookieYes](https://www.cookieyes.com/blog/gdpr-software-requirements/), [Clarip](https://www.clarip.com/data-privacy/gdpr-privacy-by-design/)) | Any EU resident's personal data is processed, regardless of where the company is based | "Will any users be based in the EU/EEA? Will you need to support data export/erasure requests, and within what SLA?" |
| **Personal data (India)** | DPDP Act 2023 + DPDP Rules 2025 — consent must be free/specific/informed/unconditional/unambiguous in plain language across 22 scheduled languages; data-principal rights (access/correct/erase/nominate); heightened consent for minors/persons with disabilities (Section 9); Significant Data Fiduciaries need a DPO + annual audits + DPIAs; Consent Manager registration deadline Nov 2026, full enforcement by May 2027 ([Seclore](https://www.seclore.com/fundamentals/dpdp-rules-2025-compliance-guide/), [RSM](https://www.rsm.global/india/insights/consulting-insights/digital-personal-data-protection-act-2023-compliance-checklist)) | Any India-facing product collecting personal data of Indian residents | "What personal data will you collect from Indian users, and will any of it be from users under 18? Do you need multi-language consent notices?" |
| **Finance/lending (India)** | RBI Digital Lending Guidelines (for any lending product) + KYC/AML per RBI Master Direction; SEBI rules for securities/investment platforms, including digital accessibility standards ([productgrowth.in fintech checklist](https://productgrowth.in/insights/fintech/fintech-compliance-checklist-2026/), [Deque SEBI accessibility](https://www.deque.com/blog/sebi-sets-a-new-standard-for-digital-accessibility-in-finance-in-india/)) | Product extends credit, or facilitates investment/trading | "Is this a lending product (triggers RBI Digital Lending Guidelines) or an investment/broking product (triggers SEBI, including mandatory accessibility)? Will you need KYC/AML checks on users?" |
| **Children's data** | COPPA (US) — apps directed at/attractive to under-13s need Verifiable Parental Consent, consent logging, parent access/deletion/revocation controls; 2025 FTC amendments added biometric identifiers to "personal information" scope ([BigID](https://bigid.com/blog/coppa-compliance/), [Promise Legal](https://blog.promise.legal/coppa-verified-parental-consent-methods/)) | Product is directed at, or likely to attract, children under 13 (US) | "Could this product realistically be used by children under 13? If yes, how will you verify parental consent before collecting any data from them?" |
| **Accessibility** | WCAG 2.2 AA is the working standard in India (GIGW 3.0, IS 17802, SEBI, RPwD Act practice notes) — mandatory for government sites, strongly expected for private enterprise, and legally required for SEBI-regulated entities; new 2.2 criteria include Focus Not Obscured, Dragging Movements, Target Size, Accessible Authentication ([Deque](https://www.deque.com/apac-digital-accessibility-laws/india/), [accesssure.in](https://accesssure.in/learn/wcag-22-checklist/)) | Any public-facing website/app in India, especially government-adjacent or financial | "Does this need to meet WCAG 2.2 AA (recommended baseline for any India-facing product, mandatory for govt/SEBI-regulated)? Any known users with accessibility needs (screen readers, motor impairment)?" |
| **E-commerce/tax (India)** | GST e-invoicing — mandatory once aggregate turnover crosses ₹5cr (₹10cr threshold effective for 30-day IRP reporting from April 2025); every B2B invoice needs IRN + QR code from the Invoice Registration Portal before going to the customer; e-commerce operators must collect TCS; signed JSON/IRN/QR data retained 6 years ([Cygnet](https://www.cygnet.one/blog/e-invoicing-compliance-checklist/), [Vertex](https://www.vertexinc.com/resources/resource-library/indias-e-invoicing-regulations-explained-scope-formats-and-penalties)) | B2B invoicing product for an India business above the turnover threshold, or any e-commerce operator | "Is your annual turnover above ₹5 crore, and do you issue B2B invoices? If yes, invoices need IRP registration + IRN + QR code before delivery to the buyer." |
| **AI systems** | EU AI Act — 4-tier risk model (unacceptable/high/limited-transparency/minimal); high-risk systems (per Annex III — hiring, credit scoring, critical infrastructure, etc.) need risk management, data governance, technical docs, logging, human oversight, conformity assessment, CE marking; most Annex III obligations enforceable from August 2, 2026; transparency-only systems (chatbots, deepfakes) just need disclosure ([Scytale](https://scytale.ai/resources/eu-ai-act-compliance-checklist/), [GDPR Local](https://gdprlocal.com/eu-ai-act-summary/)) | Product uses AI/ML for decisions affecting EU residents, especially in employment, credit, critical infra, law enforcement, education | "Does the AI make or materially influence decisions about hiring, credit, insurance eligibility, or access to essential services for EU users? If yes this is likely 'high-risk' under the EU AI Act and needs a formal risk-management and human-oversight design before build." |

**Design implication:** the system should run a **domain classifier** on the idea paragraph first (payments? health? lending? children? EU users? AI-decisioning? India-facing e-commerce?) and only surface the compliance questions whose trigger condition plausibly matches — asking all of the above to every idea paragraph would itself be a UX failure (see §7).

---

## 7. Interview UX best practice — how to get good answers from non-experts

**Question volume / fatigue data (directly relevant to the "~10 questions" design target):**
- A cross-survey meta-analysis found surveys under 12 questions get ~40% higher completion than 20+ question surveys, with no significant data-quality loss ([Plinth](https://www.plinth.org.uk/complete-guide/survey-fatigue-nonprofits)).
- Completion rate drops steeply with length: 1-3 questions ≈ 83.3% completion; 15+ questions ≈ 41.9% completion ([AYTM](https://aytm.com/post/survey-length-the-optimal-amount-of-questions-to-ask)).
- Gartner-cited data: average survey completion is ~33%, dropping below 15% once the survey exceeds 5 minutes; surveys over 25 minutes lose 3x more respondents than under-5-minute ones ([infeedo.ai](https://www.infeedo.ai/blog/13-proven-ways-to-beat-survey-fatigue-double-response-rates-in-2025)).
- Typeform's own product data: forms under 10 questions see highest completion, with **6 questions cited as a "sweet spot"** ([Typeform via Jotform summary](https://www.jotform.com/blog/conversational-form-design/)).

**Implication for this system:** the "~10 blocking questions" target is close to the upper bound of what completion-rate data supports — it should be treated as a firm ceiling, not a floor, and the system should actively try to resolve gaps via safe assumption (§5) rather than pad the question count. If more than ~10 genuinely-blocking gaps exist, batch into rounds rather than one long form.

**One-at-a-time / conversational form design:** conversational (one-question-at-a-time) forms reduce perceived commitment and cognitive load, support conditional branching so irrelevant questions are skipped, and — per a 650,000-submission Formstack analysis — multi-step forms had 25.4% higher completion than single-page/long forms ([Fillout](https://www.fillout.com/blog/one-question-at-a-time-form), [Jotform](https://www.jotform.com/blog/conversational-form-design/)). Tone matters too: a sentiment study found "happier"-toned forms had ~55% completion vs. ~38% for negative/dry tone.

**Progressive disclosure:** start with easy, low-friction questions to build momentum before harder ones; reveal follow-ups only when conditionally relevant; limit to 2-3 disclosure layers to avoid frustration ([UXPin](https://www.uxpin.com/studio/blog/what-is-progressive-disclosure/), [Userpilot](https://userpilot.com/blog/progressive-disclosure-examples/)).

**Synthesized best-practice checklist for the system's question UI (from the above + standard BA interview practice):**
1. One question at a time, not a wall of a form.
2. Plain language, no jargon — avoid "non-functional requirement," ask "how many people will use this at once?"
3. Give a concrete example answer inline ("e.g., 'about 50 orders a day, mostly evenings'") to anchor scale/format expectations.
4. Every question needs an escape hatch: "Not sure — use a sensible default" — and the system must then show what default it picked, in the draft, for the user to correct later. This operationalizes the assumption-instead-of-ask path from §5.
5. Order questions easy → hard, low-stakes → high-stakes (mirrors progressive disclosure findings).
6. Show implicit progress ("3 of ~8 questions") without being rigid, since conversational-form research shows hiding total count reduces early abandonment, but *some* progress signal reduces mid-flow abandonment — a soft/approximate counter is the middle ground.
7. Batch by category so the user understands *why* they're being asked (mirrors workshop/interview practice of framing before asking).
8. After the last question, explicitly state what was NOT asked and instead assumed, so the user can flag anything wrong before the BRD is finalized.

---

## 8. Business-type taxonomy — different BRD emphasis per type

Direct sourcing on this specific mapping is thin — most BRD-template sites give generic templates, only lightly noting industry differences (e.g., e-commerce BRDs "focus on customer journey, payment gateway integration, inventory management, mobile responsiveness"; financial services BRDs "emphasize SOX compliance, data security, fraud detection"; B2B "focuses on trust/authority, longer sales cycles, multiple decision-makers" — [monday.com](https://monday.com/blog/project-management/business-requirements-document/), [TemplateLab](https://templatelab.com/brd-templates/)). The table below is therefore synthesized from these fragments plus standard product-management/BA domain knowledge — **[unverified as a single canonical published taxonomy; cross-checked against multiple template sources but no single authoritative source enumerates exactly this way]**.

| Business type | Sections that get heavier | Extra sections that appear | Questions that become mandatory |
|---|---|---|---|
| **B2B SaaS** | Stakeholders (buyer ≠ user ≠ admin), integrations, SLAs, pricing/packaging tiers | Multi-tenancy model, admin/org hierarchy, billing & entitlements, API/webhook surface | "Who buys vs. who uses? Is this multi-tenant? What's the pricing model (seat/usage/tier)?" |
| **Internal enterprise tool** | Stakeholders (internal org chart), current process (as-is), change management/training, existing system integration | Internal SSO/identity integration, internal support model, decommission of the tool it replaces | "Which existing internal system does this replace or sit alongside? Who's the internal owner post-launch?" |
| **Consumer marketplace (2-sided)** | Stakeholders (supply side vs. demand side, each with own goals), trust & safety, payments/payouts | Matching/discovery algorithm requirements, dispute resolution, ratings/reviews, seller onboarding & verification | "Who are the two (or more) sides of this marketplace, and what does each need to trust the other? How is a dispute resolved?" |
| **Physical/ops process automation** | Current process (as-is, extremely detailed), edge cases, offline/degraded behavior, hardware/environment constraints | Field/mobile constraints (connectivity, device ruggedness), physical safety, shift/scheduling patterns | "What happens when there's no signal/connectivity on-site? What device will field staff actually carry?" |
| **Data/analytics platform** | Data & integrations, reporting needs, data governance/lineage, volumes & scale | Data ownership/lineage model, data quality SLAs, access-tiering to sensitive fields, retention per dataset | "Who owns each data source as 'source of truth'? What's the freshness requirement — real-time or batch?" |
| **Regulated fintech** | Constraints (regulatory), data & integrations, audit trail, edge cases (fraud) | Full compliance section (RBI/SEBI/PCI-DSS as applicable), KYC/AML flow, settlement/reconciliation, licensing status | "Are you a licensed/regulated entity, or partnering with one? What's your KYC/AML flow?" (See §6 table.) |
| **E-commerce/D2C** | Current/desired process (checkout, fulfillment), data & integrations (payment, inventory, shipping), reporting | Inventory sync, tax/invoicing (GST e-invoicing if India + threshold), returns/refunds flow | "How is inventory tracked and synced? What's your return/refund policy, and does it need to be enforced in-system?" |
| **Services business (booking/scheduling)** | Current process (as-is scheduling), stakeholders (provider vs. client), notifications | Availability/calendar management, cancellation/no-show policy, provider payout | "How is availability managed today — and what happens on cancellation/no-show?" |
| **Healthcare product** | Constraints (regulatory: HIPAA/ABDM), data & integrations, audit trail, edge cases | Consent management (artefact-level if ABDM), clinical data standards (FHIR), interoperability | "Does this need ABDM/HIPAA compliance? What clinical data formats need to interoperate?" (See §6.) |
| **AI/agentic product** | Edge cases (model failure modes), "what happens when things go wrong," constraints (EU AI Act if applicable) | Human-in-the-loop/oversight design, model risk classification, explainability/logging of AI decisions | "Does the AI make consequential decisions about people (hiring/credit/health/access)? If so, what human oversight exists?" (See §6.) |

**Design implication:** the system should run a lightweight business-type classifier on the idea paragraph (keyword + LLM classification against this taxonomy) immediately after ingesting it, *before* generating the draft BRD skeleton — this determines which sections get generated with more depth and which domain-triggered compliance questions (§6) are even candidates for the blocking-question shortlist.

---

## Summary for system design

1. Maintain the §1 question bank as a **candidate pool**, not a fixed script — an LLM should generate/select from it contextually per business type (§8) and gap category (§4).
2. The core mechanic is a **structured interview + document analysis** (§2) — don't try to simulate workshops/observation/focus groups; flag to the user when those are genuinely needed instead.
3. Whenever the idea paragraph states a solution without a problem, run a **Five Whys / JTBD switch-interview ladder** (§3) as a mandatory early question — this is the single highest-leverage gap.
4. Run every draft against the **12-category gap checklist** (§4): error paths, edge cases, data migration, roles/permissions, notifications, audit trail, reporting, offline behavior, capacity limits, retention, onboarding/offboarding, decommission.
5. Score every detected gap by **Reversibility cost × Assumption-confidence** (§5); only score ≥6 gaps become blocking questions (target ceiling ~10, per completion-rate data in §7); everything else becomes a documented, user-editable assumption in the draft.
6. Run a **domain classifier** first to pull in only the relevant compliance questions from §6 — never ask all of them.
7. Follow interview UX best practice (§7): one question at a time, plain language, example answers, an explicit "assume something sensible" escape hatch, easy-to-hard ordering, and an end-of-flow summary of every assumption made.
8. Classify **business type** (§8) before drafting, to determine section depth and which extra BRD sections to auto-include.

---

*Compiled by research-agent, 2026-07-29, for the BRD-drafting system project. All claims cited inline; items without a direct source are flagged [unverified].*
