# Elicitation & Gap Detection Reference

Distilled from `data/research/brd-system/03-elicitation-and-gap-detection.md`.

**Core principle:** a real BA does not ask 100 questions. They ask 2-4 opening questions per
category, listen for gaps, and drill only where the answer reveals risk. Use the bank below as a
**candidate pool for gap-triggered question generation**, never as a fixed questionnaire.

---

## 1. The blocking score — decides what to ask vs what to assume

Score every detected gap on two axes, 1-3 each, and multiply.

**Reversibility cost** — how expensive is it to change later if we guess wrong?
- `1` — cheap (copy, a default value, an optional field)
- `2` — moderate (a UI flow, a report format)
- `3` — expensive or irreversible (data model, auth/roles model, payment or compliance flow, core integration architecture, anything touching regulated data)

**Assumption-confidence** — how safe is a default guess?
- `1` — a safe industry-standard default exists and is very likely right ("assume email+password auth")
- `2` — a plausible default exists but could easily be wrong for this specific business
- `3` — no safe default; the answer could go several very different directions

**Blocking score = Reversibility × Confidence**

| Score | Action |
|---|---|
| **≥ 6** | **Blocking question.** Must ask. |
| 3-4 | Secondary. Ask only if the top-10 budget has room after all ≥6 are covered. |
| ≤ 2 | **Do not ask.** Resolve as a documented, user-editable assumption in the draft. |

**Hard ceiling: 10 questions.** Completion-rate data is unambiguous — surveys under 12 questions
get ~40% higher completion with no quality loss; 1-3 questions ≈83% completion, 15+ ≈42%;
Typeform's own data puts the sweet spot at 6. Treat 10 as a ceiling, not a target. If more than
10 genuinely-blocking gaps exist, run a second round after the draft improves — do not extend the
first round.

---

## 2. The solution-without-problem trigger (highest leverage)

If the idea paragraph states a **solution** ("I want an app that...", "build me a dashboard")
without stating a **problem**, a Five Whys ladder becomes a **mandatory** blocking question. This
is the single highest-leverage gap category — building the wrong thing is unrecoverable later.

**Five Whys ladder:**
1. "You said you need [X]. Why do you need that?" → reveals a goal
2. "Why is [goal] important right now?" → reveals a business driver
3. "Why does the current process not already achieve that?" → reveals the actual failure point
4. "Why hasn't that gap been closed already?" → reveals a structural blocker
5. "Why is this the quarter to fix it?" → reveals real urgency and constraint

**JTBD switch-interview ladder** (use when there's an existing alternative being replaced):
1. "What were you using or doing before you decided you needed this?"
2. "What specific moment made you start looking for something else?"
3. "What were you afraid might happen if you didn't switch?"
4. "What almost stopped you from switching?"
5. "What does success feel like once this job is done?"
6. "If this didn't exist, what's your fallback?"

**Problem-framing challenges** to deploy inline:
- "If I gave you [stated solution] tomorrow, would the underlying problem actually be solved?"
- "Is there a simpler way to achieve the same outcome without building this?"

---

## 3. The 12-category gap checklist — run against every draft

BAs detect gaps not by re-reading what's there, but by running a fixed checklist of chronically
under-elicited categories. **Silence, a shrug, or "we'll figure it out later" is itself the
signal.** Any category not addressed becomes either a blocking question (if high-risk for this
business type) or a documented assumption — never a quiet invention.

| Category | Why it's missed | Trigger question |
|---|---|---|
| Error / exception paths | Stakeholders describe the happy path by default | "What happens when this step fails?" — for every to-be step |
| Non-happy-path flows | Corner cases (several rare conditions at once) are never volunteered | "What's the weirdest real situation you've actually seen here?" |
| Data migration | Treated as a technical detail, but it's a business risk | "Is there existing data that must move in? Has its quality been audited?" |
| User roles & permissions | Assumed to be "admin and user" until launch says otherwise | "List every distinct type of user and what each can and can't do." |
| Notification / alerting | Considered a UI nicety until failures go unnoticed | "Who needs to be told when X happens, and how urgently?" |
| Audit trail | Invisible until a dispute demands "prove who did what, when" | "If there's ever a dispute about who changed something, how would you find out?" |
| Reporting & analytics | Deferred, but retrofitting event tracking is expensive | "What numbers will leadership ask about in month 1?" |
| Offline / degraded behaviour | Only surfaces when a dependency actually goes down | "What should happen if [key integration] is unavailable mid-task?" |
| Capacity limits | Assumed infinite by non-technical stakeholders | "What's the biggest usage spike you can imagine — and is it realistic?" |
| Archival & retention | Deferred, but retention has legal teeth | "How long must this data be kept, and what happens after — delete, anonymize, archive?" |
| Onboarding / offboarding | Provisioning is designed; **de-provisioning is routinely forgotten** | "When someone leaves or changes role, what happens to their access, same day?" |
| End-of-life / decommission | Never considered at project start | "If this were shut down in 2 years, what happens to the data and the users?" |

---

## 4. Question bank — candidate pool by category

### A. Business context & problem
1. What business problem are you solving, in one sentence?
2. What's happening today that shouldn't be (or not happening that should)?
3. Who first noticed this, and how long has it existed?
4. What triggered you to act now rather than 6 months ago?
5. What have you already tried? Why didn't it work?
6. If this project didn't happen, what would you do instead?
7. Is this new capability, or replacing something existing?
8. Who does this well already, if anyone?
9. What is the cost of doing nothing?
10. Is this isolated to one team/region, or organization-wide?

### B. Goals & success metrics
1. How will you know, six months after launch, that this was a success?
2. What's the single metric that matters most?
3. What's the target number — and what is it today (baseline)?
4. Who owns that metric after launch?
5. Is this revenue, cost-reduction, risk-reduction, or experience?
6. What does "good enough to ship" look like vs "ideal"?
7. Are there secondary metrics that must not regress?
8. Is there a deadline tied to an external event?

### C. Stakeholders & users
1. Who will actually use this day-to-day? (Not who requested it.)
2. Who can say no even if everyone else agrees?
3. Who is affected but wasn't in this conversation?
4. What roles / permission levels exist?
5. Are there external users (customers, vendors, regulators) too?
6. Who supports and maintains this after launch?
7. Who owns the budget?
8. **Who loses something (time, control, job function) if this succeeds — and have they been consulted?**

### D. Current process (as-is)
1. Walk me through, step by step, how this happens today.
2. What tools/systems are used at each step?
3. Where does the process start and end?
4. What's the volume today?
5. Where are the delays and bottlenecks?
6. What manual workarounds exist that "everyone just knows"?
7. Who does each step, and how long does it take?
8. What happens when something goes wrong today?
9. **Is there a shadow process — a spreadsheet, WhatsApp group, personal notebook — propping up the official one?**

### E. Desired process (to-be)
1. Walk me through how you imagine this working.
2. What should stay exactly the same, and what must change?
3. What triggers the new process?
4. Fully automated, or human-in-the-loop?
5. What does "done" look like for one instance?
6. Which current steps should be eliminated, not just improved?
7. Desired end-to-end turnaround time?
8. Parallel run during transition, or hard cutover?
9. What existing systems must this integrate with rather than replace?

### F. Data & integrations
1. What data does this create, read, update, delete?
2. Where does it come from — user input, another system, a third party?
3. What must it integrate with (CRM, ERP, payment gateway, auth)?
4. Is there an existing API, or must one be built?
5. Who owns the source-of-truth if multiple systems hold the same entity?
6. Real-time sync, or is batch/nightly fine?
7. What happens if an integration is down — hard fail or graceful degrade?
8. Is there legacy data to migrate, and has its quality been audited?
9. Any contractual restrictions on using this data this way?

### G. Volumes & scale
1. How many users day one? Year one?
2. What's peak load — seasonal, daily, event-driven?
3. Transactions/records per day?
4. Data growth rate per year?
5. Multiple geographies / time zones / languages?
6. Is there a hard ceiling (contractual, regulatory, physical)?
7. What happens if volume is 10x the estimate?

### H. Constraints
1. What's the budget range?
2. Is there a hard deadline, and what happens if it's missed?
3. What regulations apply? (see §5)
4. Existing vendor contracts or platform lock-ins?
5. Is there an internal security/architecture review to pass?
6. What is explicitly out of scope for this phase?
7. Brand, legal, or accessibility standards to follow?
8. Any other team's roadmap that could block this?

### I. Edge cases & exceptions
1. What if a user enters wrong data, abandons midway, or does it twice?
2. What if two people do the same action simultaneously?
3. What if data is missing or incomplete?
4. Boundaries — zero items, maximum items, exactly one?
5. What if a third-party service dies mid-transaction?
6. What if permissions change while a user is mid-task?
7. Are there VIP/exception cases that bypass normal rules?
8. What's the undo story — can actions be reversed, by whom?
9. Partial failure — 60 of 100 records succeed, then what?
10. Is there a fraud/abuse scenario to design against?

### J. Reporting
1. Who needs reports, how often?
2. What decisions get made from them?
3. Dashboard, PDF, spreadsheet, email digest?
4. Must it reconcile against another system (finance, audit)?
5. Who can see which data — permission tiers in reporting?
6. How long must history be preserved for trends?
7. Real-time or batch?

### K. Failure & escalation
1. Who gets notified when this fails, and how?
2. Acceptable time-to-detect and time-to-resolve?
3. Is there a manual fallback if the system is down?
4. Who can override or manually correct a bad outcome?
5. What gets logged for post-mortem?
6. Any legal obligation to report certain failures?
7. What's the blast radius if it fails silently for a day?

---

## 5. Compliance triggers — classify the domain first, then ask only what matches

**Never ask all of these.** Run a domain classifier on the idea paragraph, surface only the rows
whose trigger plausibly matches. Asking all of them is itself a UX failure.

| Trigger | Regulation | Question to ask |
|---|---|---|
| Stores/processes/transmits card data | PCI-DSS | "Will you ever touch raw card numbers, or will a hosted/tokenized gateway (Stripe/Razorpay checkout) keep card data off your servers?" |
| India payments / aggregating funds for merchants | RBI PA rules + data localization (all payment data on India servers; if processed abroad, full copy back within 24h) | "Will payment data ever be processed or stored outside India? Are you aggregating funds for third-party merchants, or just your own sales?" |
| US patient health data | HIPAA | "Does this touch US patient health/treatment/payment data? Will you sign BAAs with vendors?" |
| India health records / ABDM interop | ABDM/ABHA — FHIR R4, artefact-level revocable consent, federated storage | "Does this need to interoperate with ABDM (ABHA-linked records, other hospitals/labs)?" |
| Any EU resident's personal data | GDPR — privacy by design, DPIA, subject rights, 72h breach notice | "Will any users be in the EU/EEA? Will you support data export/erasure requests, and within what SLA?" |
| Indian residents' personal data | DPDP Act 2023 + Rules 2025 — plain-language consent across 22 languages, heightened consent for minors, Consent Manager registration Nov 2026, enforcement by May 2027 | "What personal data will you collect from Indian users? Any users under 18?" |
| Lending or investment product (India) | RBI Digital Lending Guidelines / SEBI (incl. mandatory accessibility) | "Is this a lending product or an investment/broking product? Will you need KYC/AML on users?" |
| Product attractive to under-13s (US) | COPPA — verifiable parental consent; 2025 FTC amendments added biometrics | "Could this realistically be used by children under 13? How will you verify parental consent?" |
| Public-facing India product, esp. govt/financial | WCAG 2.2 AA (GIGW 3.0, IS 17802, RPwD, SEBI) | "Does this need WCAG 2.2 AA? Any known users with accessibility needs?" |
| India B2B invoicing above ₹5cr turnover | GST e-invoicing — IRN + QR from IRP before the invoice reaches the buyer; 6-year retention | "Is turnover above ₹5 crore, and do you issue B2B invoices?" |
| AI making consequential decisions about EU residents | EU AI Act — Annex III high-risk obligations enforceable from 2 Aug 2026 | "Does the AI make or materially influence decisions about hiring, credit, insurance, or access to essential services for EU users?" |

---

## 6. Business-type taxonomy — classify before drafting

Determines which sections get depth and which extra sections appear.

| Type | Heavier sections | Extra sections | Mandatory questions |
|---|---|---|---|
| **B2B SaaS** | Stakeholders (buyer ≠ user ≠ admin), integrations, SLAs | Multi-tenancy, admin hierarchy, billing & entitlements, API/webhook surface | "Who buys vs who uses? Multi-tenant? Pricing model — seat/usage/tier?" |
| **Internal enterprise tool** | Stakeholders (org chart), as-is process, change management | SSO/identity, internal support model, decommission of what it replaces | "Which existing system does this replace? Who owns it post-launch?" |
| **Consumer marketplace** | Stakeholders (supply vs demand side), trust & safety, payouts | Matching/discovery, dispute resolution, ratings, seller verification | "Who are the two sides, and what does each need to trust the other? How is a dispute resolved?" |
| **Physical/ops automation** | As-is (very detailed), edge cases, offline behaviour | Field/mobile constraints, physical safety, shift patterns | "What happens with no connectivity on-site? What device will field staff actually carry?" |
| **Data/analytics platform** | Data & integrations, reporting, governance, volumes | Lineage model, data-quality SLAs, access tiering, per-dataset retention | "Who owns each source as source-of-truth? Real-time or batch freshness?" |
| **Regulated fintech** | Regulatory constraints, audit trail, fraud edge cases | Compliance section, KYC/AML flow, settlement/reconciliation, licensing | "Are you licensed, or partnering with a licensed entity? What's the KYC/AML flow?" |
| **E-commerce / D2C** | Checkout & fulfillment process, payment/inventory/shipping integrations | Inventory sync, GST e-invoicing, returns/refunds | "How is inventory tracked and synced? What's the returns policy, and must it be enforced in-system?" |
| **Services / booking** | As-is scheduling, provider vs client stakeholders, notifications | Availability management, cancellation/no-show policy, provider payout | "How is availability managed today, and what happens on cancellation?" |
| **Healthcare** | Regulatory constraints, data integrations, audit trail | Consent management, clinical data standards (FHIR), interoperability | "HIPAA or ABDM? What clinical formats must interoperate?" |
| **AI / agentic product** | Edge cases (model failure), failure handling, EU AI Act constraints | Human-in-the-loop design, model risk class, decision explainability/logging | "Does the AI make consequential decisions about people? What human oversight exists?" |

---

## 7. Interview UX rules

1. **One question at a time.** Never a wall of a form. (Multi-step forms complete 25.4% better.)
2. **Plain language.** Not "what are your non-functional requirements" — "how many people will use this at once?"
3. **Give an example answer inline** — "e.g. 'about 50 orders a day, mostly evenings'" — to anchor scale and format.
4. **Always offer the escape hatch:** *"Not sure — assume something sensible."* Then **show what default you picked**, in the draft, tagged, so it can be corrected.
5. **Order easy → hard, low-stakes → high-stakes.**
6. **Soft progress signal** — "3 of about 8" — not a rigid counter.
7. **Frame why you're asking** before a category shift.
8. **After the last question, state what you did NOT ask and assumed instead**, so it can be challenged before the BRD is finalized.

---

## 8. Honesty rule — what this cannot do

The system is an AI-mediated structured interview plus document analysis. That covers BABOK's
*interviews*, *document analysis*, *survey*, and *interface analysis* techniques well.

It **cannot** reproduce **workshops** (needs multiple live humans negotiating tradeoffs),
**observation / job shadowing** (told-process ≠ actual process, and only watching reveals the
difference), or **focus groups**.

When a requirement genuinely needs one of those, **say so explicitly** — "this needs your ops team
in a room; I can't infer it from here" — rather than pretending more Q&A will resolve it. The
closest available substitute for observation is "walk me through your last real example" —
retrospective narrated observation. Use it, but don't oversell it.
