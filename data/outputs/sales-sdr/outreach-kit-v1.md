# AI Automation Studio — Full Outreach Kit
# Ujjawal Shrivastav | One-Person Shop | Target: ₹20k this week
# Lead offer: LLM Cost-Optimization Audit (₹15-25k)
# Generated: 2026-05-31 | Version: 1

---

## PART 1 — TRIGGER MATRIX (run this before writing a single word)

For every prospect, identify ONE trigger before opening any sequence. No trigger = no message.

### Trigger A — "Hiring AI engineer" (strongest signal)
WHERE TO FIND:
- LinkedIn Jobs: search "AI engineer" OR "ML engineer" OR "LLM engineer", filter Company size 11-200, posted last 30 days
- Naukri.com: same search
- Clay: `job_title_contains IN (AI, ML, LLM, GenAI) AND company_headcount < 200 AND job_posted_days < 30`

WHAT IT MEANS: They're building AI at scale. LLM costs are starting to hurt and they're throwing headcount at it — often the wrong move. The audit is faster and cheaper than a new hire's first month.

OPENER HOOK: "Noticed [Company] is hiring for an AI engineer — usually means LLM spend is climbing."

---

### Trigger B — "Recent seed / pre-seed / Series A raise" (timing trigger)
WHERE TO FIND:
- Crunchbase (free tier covers seed rounds)
- LinkedIn posts: search "excited to announce our raise" OR "thrilled to share funding" — filter by date (last 60 days)
- YC batch announcements, Inc42 (for Indian startups)
- Clay: `funding_round IN (seed, pre-seed, series_a) AND funding_date < 60 days AND company_description CONTAINS ai`

WHAT IT MEANS: They just got money, they're scaling fast, LLM costs will compound if not optimized now. CFO hasn't started scrutinizing infra yet — perfect window.

OPENER HOOK: "Congrats on the [round] raise. One thing that sneaks up on teams at this stage: LLM costs."

---

### Trigger C — "Founder / CTO posted about AI costs or scaling AI"
WHERE TO FIND:
- LinkedIn Sales Navigator: Content filter → keyword "OpenAI cost" OR "GPT bill" OR "LLM expensive" OR "scaling AI" OR "AI infrastructure" — filter by seniority: Director/VP/C-level, posted last 14 days
- Twitter/X: same keywords, filter to accounts with 1k+ followers in tech

WHAT IT MEANS: They're already feeling the pain. This is the warmest trigger — they've self-identified the problem publicly.

OPENER HOOK: "Your post about [specific phrase from their post] caught my eye — I do exactly this."

---

### Trigger D — "Product has a visible AI feature" (site inspection)
WHERE TO FIND:
- BuiltWith technographic data: filter for sites using OpenAI API, Anthropic, Cohere, Replicate
- Manual: look for "Powered by OpenAI" in footer, AI chat widget, AI-generated content mentions in landing page
- Clay: `tech_stack CONTAINS (openai OR anthropic OR cohere OR replicate)`

WHAT IT MEANS: They're already running inference in production. Costs are real and recurring. The audit has a clear target.

OPENER HOOK: "Noticed [product] uses [LLM/AI feature] — running live inference at scale is exactly where the cost leaks hide."

---

### Trigger E — "Customer support team is growing" (RAG Chatbot play)
WHERE TO FIND:
- LinkedIn Jobs: "customer support" OR "customer success" OR "support agent" at SaaS companies 20-150 people
- Company has public docs: GitBook, Notion public pages, Zendesk Help Center, Intercom Articles

WHAT IT MEANS: Docs exist, questions repeat, human cost is scaling. A RAG chatbot kills the repetition.

OPENER HOOK: "Your support team posting suggests customers are asking the same questions your docs already answer."

---

### Trigger F — "Hiring for operations / data entry / repetitive process" (Automation play)
WHERE TO FIND:
- LinkedIn Jobs: "operations manager" OR "data entry" OR "virtual assistant" OR "workflow" at 10-100 person companies
- Bonus: job description mentions a specific manual task ("respond to 200 emails daily", "manually pull reports", "update CRM every morning")

WHAT IT MEANS: Manual, repetitive work visible in a job posting = automatable process. The job post is basically a spec for the automation.

OPENER HOOK: "Your [role] posting mentions [specific manual task]. That's automatable with an AI agent — usually 1-2 weeks to build."

---

## PART 2 — PRIMARY SEQUENCE: LLM COST-OPTIMIZATION AUDIT

Target: Startup founders, CTOs, Head of Engineering at 10-200 person AI-building companies.
CTA across all touches: one 15-minute call.

---

### TOUCH 1: LinkedIn Connection Note (≤300 chars, send with connection request)

**Variant A — Hiring AI engineer:**
```
[Company] is scaling AI fast — saw the engineer posting. I help startups cut LLM spend before the bill compounds. Happy to connect.
```
(130 chars)

**Variant B — Just raised:**
```
Congrats on the [round] raise. I help seed-stage teams get their LLM costs right before they scale. Thought it worth connecting.
```
(128 chars)

**Variant C — Founder posted about AI costs:**
```
Your post about [AI spend / scaling] resonated — I help startups cut their OpenAI/Claude bills without touching the product. Worth connecting.
```
(141 chars)

**Variant D — Product has AI feature:**
```
Noticed [product] runs AI at its core. I help teams like yours cut LLM spend without re-architecting anything. Happy to connect.
```
(128 chars)

---

### TOUCH 2: LinkedIn DM — Day 1 (after connection accepted, ≤60 words)
**Lead with the free Loom offer — do not pitch the paid audit yet.**

```
Thanks for connecting.

[Your job post / product / post about AI costs] gave me enough context to spot two likely cost leaks. I put together a free 5-min Loom walkthrough of what I'd fix first.

No pitch — just the math. Want me to send it over?
```
(~46 words)

NOTE FOR UJJAWAL: When they say yes, record a 5-min Loom specifically for them (see Part 5 — Lead Magnet). This is your conversion trigger.

---

### TOUCH 3: LinkedIn DM — Day 3 (if no reply to Touch 2, ≤60 words)
**Drop a specific, useful technical insight. No ask at the end — just value.**

```
One pattern I see with teams building on LLMs: most default every call to GPT-4 or Claude Sonnet, even for simple queries.

A lightweight classifier that routes easy calls to Haiku or GPT-3.5 typically cuts costs 40-60% on mixed workloads. Two hours to build.

Built this for my own 90-agent AI stack. Happy to show you.
```
(~58 words)

---

### TOUCH 4: LinkedIn DM — Day 7 (breakup, ≤60 words)

```
Last note on this. If LLM costs aren't a priority right now, totally makes sense.

When it does come up, I'm easy to find. The audit is ₹15k, takes 5 days, and ends with a prioritised fix list.

If you ever want that free Loom teardown, just reply.
```
(~49 words)

---

## PART 3 — COLD EMAIL SEQUENCE (parallel to LinkedIn or standalone)

### EMAIL VARIANT A — Trigger: Hiring AI engineer

Subject: `saw the AI engineer posting`

```
Hi [Name],

[Company] is hiring for an AI engineer. That usually means LLM costs are starting to sting.

I run a 5-day LLM cost audit: find where you're over-spending on model calls — wrong model tier, missing prompt caching, unbatched requests — and deliver a fix plan.

I built this system for my own 90-agent AI stack. Same patterns apply.

Fee: ₹15k flat.

Worth 15 minutes?

Ujjawal
```
(~71 words)

Suggested follow-up cadence:
- Day 3: specific routing insight email (see Day 3 follow-up below)
- Day 7: breakup email

Why this should work: The job posting is a dated, sourced trigger that directly maps to the buyer's budget pain — they're about to pay a senior salary when the problem might need a one-time audit. Buyer pain is cost; CTA is small.

What I'd need to make this stronger: One named customer outcome with a real number. Until then, the "built for my own stack" proof is honest and still credible.

---

### EMAIL VARIANT B — Trigger: Recent raise (seed / Series A)

Subject: `LLM costs as you scale`

```
Hi [Name],

Congrats on the [round] raise. One thing that sneaks up on teams at this stage: LLM costs grow faster than headcount when you're iterating on AI features.

I do a 5-day audit — model routing, prompt caching, batching — and deliver a prioritised fix plan.

Built this for my own AI stack. Same patterns, different codebase.

Fee: ₹15k. Happy to do a free Loom overview of your setup first.

Worth a look?

Ujjawal
```
(~78 words)

Suggested follow-up cadence:
- Day 3: routing tip follow-up
- Day 7: breakup

Why this should work: The raise is a public, dated trigger that predicts exactly when LLM costs become real. The "before it compounds" framing is CFO-language, which resonates right after a raise when founders are watching burn.

---

### EMAIL VARIANT C — Trigger: Founder posted about AI costs

Subject: `your post about AI costs`

```
Hi [Name],

Your post about [specific phrase from their post] caught my eye.

I run a 5-day LLM cost audit for startups. Most teams over-spend in two places: running expensive models on simple queries, and missing prompt caching. Two changes, meaningful savings.

I built this for my own 90-agent AI stack. Same architecture.

Fee: ₹15k. I can do a free 5-min Loom on your specific setup first.

Worth a reply?

Ujjawal
```
(~78 words)

Suggested follow-up cadence:
- Day 3: specific insight tied to what they posted about
- Day 7: breakup

Why this should work: They already posted about the problem publicly — this isn't a cold introduction to the pain, it's a direct response to a stated need. Highest reply-rate trigger of the four.

---

### EMAIL VARIANT D — Trigger: Product has visible AI feature

Subject: `[Company]'s LLM spend`

```
Hi [Name],

Noticed [product name] runs [AI feature] at its core — which means LLM calls are a real, recurring cost.

I do a 5-day audit: find where you're paying more than needed on model tier, caching, and batching. Deliver a fix plan.

Built the same optimizations for my own AI system.

Fee: ₹15k. I can start with a free Loom on your setup if a call feels like too much.

Interested?

Ujjawal
```
(~78 words)

---

### EMAIL FOLLOW-UP — Day 3 (all trigger variants)

Subject: `one quick thing`

```
Hi [Name],

One thing I'd look at first with [Company]: whether you're routing LLM calls by complexity or running everything through the same expensive model.

Simple classifier, 2-3 hours to build. Usually cuts costs 40-60% on mixed workloads.

Happy to walk through it on a 15-min call — or I can send a Loom if that's easier.

Still interested?

Ujjawal
```
(~65 words)

---

### EMAIL BREAKUP — Day 7

Subject: `closing the loop`

```
Hi [Name],

Figured I'd close this out. If LLM cost optimization isn't on the list right now, no pressure.

When it does come up, the audit is ₹15k and takes 5 days. I'm easy to find.

Ujjawal
```
(~39 words)

---

## PART 4 — COLD CALL / VOICE NOTE OPENER (~75 words spoken, ~30 seconds)

Use this as a voice note on LinkedIn (premium feature) or a cold call script.

**Variant A — Hiring trigger:**
```
Hey [Name], Ujjawal here. Saw [Company] is hiring for an AI engineer — thought it made sense to reach out.

I do LLM cost audits for startups. Find where you're over-spending on model calls and give you a fix plan. Five days, ₹15k.

I built this for my own 90-agent AI system, so I know exactly where the leaks are.

Did I catch you at a bad time?
```
(~70 words)

**Variant B — Recent raise:**
```
Hey [Name], Ujjawal here. Congrats on the [round] — I saw the announcement.

One thing that compounds fast after a raise: LLM costs. I do a 5-day audit — find where you're over-paying on model calls — and hand you a prioritised fix plan.

Built this for my own AI stack, so the patterns are proven.

Did I catch you at a bad time?
```
(~68 words)

Pattern-interrupt after "yes, what's this about?":
```
Great. So I help AI-first startups cut their OpenAI or Claude bill without touching the product. Usually 40-60% savings from two or three routing and caching changes. I can walk you through what I'd look at for [Company] in 15 minutes. Does [day/time] work?
```

---

## PART 5 — ALTERNATE HOOK 1: AI AUTOMATION / AGENT BUILD

**Best triggers:** Operations hire posting, data entry mention in JD, manual process visible in job description, service business with repeating workflow.

**Trigger signal in Clay:** `job_title IN (operations, data entry, virtual assistant, workflow) AND company_headcount < 150`

**LinkedIn DM (≤60 words):**
```
Your posting for [role] mentions [specific manual task from JD].

I build AI agents that automate workflows like this — browser automation, form processing, data pipelines. My own system handles LinkedIn outreach, job applications, and daily reporting unattended.

Typically 1-2 weeks to build. Fee ₹20-35k depending on complexity.

Worth 15 minutes to see if it fits?
```
(~56 words)

**Cold Email:**

Subject: `automating [Company]'s [process name]`

```
Hi [Name],

Your job posting for [role] mentions [specific manual task]. That's a pattern I automate regularly — AI agent + browser automation, runs unattended.

My own system handles LinkedIn outreach, form fills, and daily reporting without human input. Same architecture applies to your workflow.

Takes 1-2 weeks. Fee: ₹20-35k.

Worth 15 minutes to spec it out?

Ujjawal
```
(~65 words)

Why this should work: The job description is a public, specific spec for the pain. "You're about to pay a salary for something automatable" is a concrete ROI framing that resonates with founders.

What I'd need to make this stronger: A specific named process from their actual JD in the [specific manual task] slot — never use a generic placeholder when sending.

---

## PART 6 — ALTERNATE HOOK 2: AI CHATBOT / RAG OVER DOCS

**Best triggers:** Support team job posting + visible public docs, SaaS with Help Center but no AI chat, founder posts about documentation or onboarding time.

**Trigger signal in Clay:** `job_title IN (customer support, support agent, customer success) AND tech_stack CONTAINS (zendesk OR intercom OR gitbook OR notion) AND company_headcount < 200`

**LinkedIn DM (≤60 words):**
```
Your support team posting caught my eye — especially since [Company] has [docs / help center / Notion wiki] that already answers most of these questions.

I build AI chatbots trained on your actual docs. Customer gets an instant answer; your team handles only the edge cases.

1-2 weeks to build. Fee: ₹15-25k.

Worth a quick look?
```
(~57 words)

**Cold Email:**

Subject: `your support team + AI docs`

```
Hi [Name],

Your job posting for a support agent suggests inbound volume is climbing. If [Company] has docs or a help center, most of those questions are already answered — just not instantly.

An AI chatbot trained on your docs handles repetitive queries without a human in the loop.

I built mine on ChromaDB with episodic memory. Same architecture applies.

Fee: ₹15-25k. Happy to show a demo.

Worth a look?

Ujjawal
```
(~79 words)

Why this should work: The support hiring trigger predicts exactly when repetitive query volume hurts. The proof is honest — Boss built his own RAG system (Jarvis episodic memory on ChromaDB) — same architecture, different domain.

---

## PART 7 — FREE LEAD MAGNET: "5-Minute LLM Cost Health Check" Loom

**What it is:** A screen recording (5 minutes, no longer) where Ujjawal reviews a specific prospect's public signals and narrates 2-3 cost leak patterns he'd fix first.

**What to include in the Loom:**
1. Open with their product page or job posting on screen. Name them. ("I'm looking at [Company]'s AI [feature / job post]...")
2. Point to 2-3 specific cost leak patterns visible from the outside:
   - "This feature suggests you're running X model calls per user action — here's where the model tier matters."
   - "Your job posting mentions [LLM task] — this is typically where caching is missing."
   - "If you're using [tool visible in stack], here's what the default config costs vs. the optimized config."
3. End with one sentence: "If you want me to go deeper on your actual setup, that's the 5-day audit — ₹15k." No other pitch.

**When to offer it:**
- In LinkedIn DM Touch 2: "Want me to send it over?"
- In cold email Variant C: "I can do a free 5-min Loom on your specific setup first."
- When a prospect replies but isn't ready to book a call: "Let me send you a Loom first — no call needed."

**Time to produce:** 10-15 minutes per prospect. Worth doing for the top 5-7 prospects per week — not for everyone.

**Why it works:** It shows competence before asking for money, creates genuine reciprocity, and filters serious prospects (people who say yes to the Loom are already halfway sold). A Loom also travels — they forward it to their CTO.

**Clay/Outreach automation tip:** In your Clay sequence, add a step: "If prospect replied positively to DM Touch 2 → move to manual task: record Loom → send Loom link." Never automate the Loom itself — it needs to feel personal.

---

## PART 8 — OBJECTION HANDLING ONE-LINERS

**"₹15k is too expensive / too much right now"**
"Makes sense to be careful. Here's an alternative — let me do a free 1-hour diagnostic call. If I can't show you a real cost leak in that hour, there's nothing to audit and you owe me nothing. Does that work?"

**"We'll handle it in-house"**
"Totally fair — most teams want to own it. Usually takes 2-3 sprints to get right. I deliver the full audit in 5 days, so you'd have the roadmap before your team even starts. Worth running both in parallel?"

**"Not now / we're too busy"**
"Understood. When do you typically review infra or LLM costs — quarterly? I'll follow up then, not before."

**"We're too early / we're not spending much on LLMs yet"**
"Then this call is worth zero to you, and I won't waste your time. The audit makes sense once you're spending ₹15-20k/month on LLMs. Are you close to that threshold?"

**"We don't use OpenAI — we're on [Gemini / Mistral / open-source]"**
"Good to know — the same optimization patterns apply. Model routing, prompt caching, batching logic is model-agnostic. Which LLM are you running? I can speak to that stack specifically."

**"We already have someone looking at this"**
"Makes sense. One thing I'd check: are they also looking at prompt caching specifically? It's the most underused lever — most teams skip it because the setup is fiddly. Happy to share how I implemented it if useful."

**"Can you show me examples / past work?"**
"I don't have client logos yet — I'm new to freelancing. What I do have is my own production AI system: 90+ agents, browser automation, RAG with episodic memory, and LLM cost optimization all running live. Happy to walk you through that as a reference for what I'd build for you."

---

## PART 9 — TOOLING SETUP (Clay + Sales Nav)

### Clay sequence for LLM Cost Audit (Trigger A — Hiring):

1. Source: LinkedIn Job Search API in Clay
   - Filter: `job_title contains (AI engineer OR ML engineer OR LLM engineer OR GenAI engineer)`
   - Filter: `company_headcount between 10 and 300`
   - Filter: `job_posted_date < 30 days`
2. Enrich: Find founder/CTO LinkedIn profile (Clearbit or LinkedIn enrichment)
3. AI variable: `"Write one sentence about why [company_name] hiring an [job_title] suggests they have LLM cost pressure. Reference their product if known."` → use in opener
4. Split: If LinkedIn URL found → route to LinkedIn sequence (Touch 1-4). Else → route to cold email sequence.
5. Cadence: Day 0 connection, Day 1 DM (after acceptance detected), Day 3 follow-up DM, Day 7 breakup.

### Sales Navigator saved search (set up once, run weekly):
- Role: CTO, VP Engineering, Head of Engineering, Co-Founder, Founder
- Company size: 11-200
- Industry: Computer Software, Internet, IT Services
- Geography: India (for INR pricing) OR Worldwide (for USD pricing — adjust fee to $180-300)
- Filter: "Changed jobs in last 90 days" (new CTO = clean slate, more likely to audit old decisions)
- Save as: "AI Startup Engineering Leaders"

Run this search every Monday. Export 20-30 leads. Cross-check against Crunchbase for funding. Prioritize Trigger B + C prospects first (warmest), then Trigger A.

---

## QUICK REFERENCE CARD

| Touch | Channel | Word cap | Trigger mention | CTA |
|-------|---------|----------|-----------------|-----|
| Connection note | LinkedIn | 300 chars | Yes | Implicit (connect) |
| DM Touch 2 | LinkedIn | 60 words | Reference trigger | Send free Loom? |
| DM Touch 3 | LinkedIn | 60 words | Routing tip | None (pure value) |
| DM Touch 4 | LinkedIn | 60 words | None | Soft close |
| Email Touch 1 | Email | 90 words | Yes | 15-min call |
| Email Touch 2 | Email | 90 words | Technical insight | 15-min call or Loom |
| Email Touch 3 | Email | 40 words | None | Soft close |
| Cold call | Voice | ~75 words | Yes | "Did I catch you?" |

**This week's target:** 20 LinkedIn connections (Trigger A + B) + 10 cold emails (Trigger C — warmest). Record 5 personalised Looms for anyone who responds to Touch 2. Book 2 calls. Close 1.
