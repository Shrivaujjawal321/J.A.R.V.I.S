# Jarvis — Product Foundations (Pre-PRD)
**Date:** 2026-06-01
**Author:** product-manager-agent (Jarvis specialist)
**Status:** Decision-grade draft — founder review required
**Anti-fabrication note:** All market-size figures are marked [NEEDS INPUT]. User research is drawn solely from the founder's own lived experience. External data is marked [ASSUMPTION] or [NEEDS INPUT]. Do not promote this doc to a PRD until at least 5 non-founder user interviews are completed.

---

## 0. What This Doc Is

This is not a PRD. It is the product-strategy foundations that a PRD must be built on. It answers: who, what job, which wedge, what's the wow, what's the minimum to ship, how do you onboard, how do you measure success, and what kills you. Founder decides on every fork presented.

---

## 1. Target User

### Recommended v1 ICP

**The AI-Native Career Sprinter** — a CS/AI-ML graduate or 0-2 YOE developer in India (or South/Southeast Asia), actively job-hunting, who already uses Claude/ChatGPT daily as a tool, enters hackathons to build credibility, and is grinding LinkedIn + Naukri applications without a system.

More precisely, someone who:
- Graduated within the last 12 months or is about to graduate
- Has side projects but struggles to frame them compellingly for recruiters
- Applies to 5-30 companies/month with minimal customization because it's too slow to customize manually
- Enters 1-3 hackathons/quarter and has done at least one before
- Is comfortable with AI tools but cannot get them to "remember" who they are
- Gets frustrated restarting every ChatGPT conversation from scratch
- Is price-sensitive: the tool must be either free or under ~₹500/month to trial without friction

**Why this ICP, specifically:**
The founder IS this user, which means (a) the pain is real and the builder has lived context, (b) early feedback loops are fast (founder tests on himself first), and (c) the user community is reachable — Discord servers, LinkedIn, Indian AI/ML college groups, Devfolio, HackerEarth communities.

**Is the proposed framing "ambitious early-career tech person running a job hunt" correct?**
Partially. The word "ambitious" is noise — everyone in the ICP thinks they're ambitious. The precise differentiator is "AI-native" (already uses AI tools daily, so Jarvis is an upgrade, not a behavior change) and "career sprint" (a defined 3-12 month window of high-intensity job-hunting activity). This matters for positioning: you're not asking them to adopt AI — you're offering a better version of the AI they already use.

### 3 Alternative ICPs (for founder to evaluate)

| ICP | Pain | Willingness to Pay | Reachability | Retention Risk |
|---|---|---|---|---|
| **A. AI-Native Career Sprinter (India, 0-2 YOE)** — RECOMMENDED | Resume not shortlisted; application volume vs. customization tradeoff; grinding solo with no system | LOW-MEDIUM (₹0-500/mo trial range) | HIGH (Devfolio, Discord, LinkedIn) | HIGH — job hunt ends = churn. Mitigate by expanding use case. |
| **B. Mid-career SWE switching to AI/ML (India/global, 3-8 YOE)** | Career pivot is slow; no credibility proof in new domain; needs portfolio + network rebuild | MEDIUM-HIGH ($10-30/mo) | MEDIUM (LinkedIn, Reforge-style communities) | LOW — transition takes 12-18 months |
| **C. Global CS undergrad entering AI/ML (US/UK/EU)** | Same job hunt pain, but less price-sensitive; more familiar with SaaS tools; higher competition from Teal/Simplify | MEDIUM-HIGH ($10-20/mo) | MEDIUM (university Discord, GitHub, HN) | HIGH — same job hunt end risk |

**Recommendation:** Lock v1 to ICP-A. It's the tightest feedback loop (founder = user), lowest acquisition cost, and the pain is acute and immediate. If v1 works, ICP-B is the natural upgrade cohort — they have more money and a longer engagement window.

NEEDS INPUT: How many people in your immediate network fit ICP-A precisely? This is your interview pool for user research before any PRD is written.

---

## 2. Jobs-to-Be-Done

These are inferred from the founder's own experience + the built Jarvis features. No external interviews have been conducted. Treat these as hypotheses until validated.

### Functional Jobs (what they literally need done)

**J1: Apply at volume without sacrificing customization.**
When I'm applying to 10+ companies/week, I want every application to feel personal to that company, so I can increase my response rate without spending 2 hours per application.

**J2: Know exactly what's wrong with my resume before I get another silent rejection.**
When a recruiter doesn't respond, I want to understand whether it's my resume, my keywords, my framing, or the role itself, so I can fix the right thing instead of guessing.

**J3: Walk into a hackathon with a strategy, not just energy.**
When I register for a hackathon, I want to understand the judging criteria, the sponsor tech, and what winning entries have looked like, so I can build something that competes rather than just participates.

**J4: Keep my portfolio current without it being a project in itself.**
When I ship a new project, I want my portfolio, resume, and LinkedIn to update cohesively, so I don't have to spend a day manually propagating changes across surfaces.

**J5: Have someone who actually knows me help me with outreach.**
When I'm messaging a recruiter or cold-contacting a senior at a target company, I want the message to sound like me — not like a template — so the person feels I wrote specifically for them.

### Emotional Jobs (how they want to feel)

**E1: Feel like I have a system, not just effort.**
The fear: "I'm working hard but nothing is organized — I'm probably missing things." Jarvis should make the user feel like nothing falls through the cracks.

**E2: Feel like I'm maximally prepared, not just present.**
The fear before an interview or hackathon submission: "Am I underprepared?" Jarvis should close that gap.

**E3: Feel less alone in the grind.**
Job hunting as a fresh grad is isolating. A tool that responds to you personally, remembers your wins and losses, and adapts to your situation provides real comfort. This is underrated as a retention driver.

### Social Jobs (how they want to be seen)

**S1: Signal to the market that they are serious and systematic.**
Outbound messages drafted by Jarvis (in the user's voice, with real context) make them look more professional than peers sending copy-paste LinkedIn DMs.

**S2: Be the person who wins the hackathon because they prepared better.**
Using a war-room strategy tool that most competitors don't have is a genuine competitive edge — and it's shareable ("I used Jarvis to prep for this").

---

## 3. The Wedge

### Option A: Career AI — "Jarvis runs your job hunt" (Founder's Proposal)

**What it is:** Position Jarvis as the AI layer for everything in an early-career job hunt: resume, applications, interview prep, cold outreach, portfolio — end-to-end.

**Strengths:**
- Acute pain, high frequency of use during job hunt window (daily touchpoints)
- Clear "before/after": 3 applications/day vs. 10; 2% response rate vs. goal of 5%+
- Demoable in 60 seconds without needing extensive setup
- Community virality: every person who succeeds has peers in the same pain
- Real differentiation vs. ChatGPT/Gemini: they don't know your voice, your projects, your rejection history

**Weaknesses:**
- Temporally bounded: the user's job hunt ends (success = churn trigger unless re-framed)
- Competitor risk: Teal, Simplify, Kickresume, LazyApply, Rezi all exist. [NEEDS INPUT: founder has not done a detailed competitor audit — recommend dispatching research-agent before finalizing wedge]
- Privacy bar: users must give access to resume, email, and ideally LinkedIn — higher trust barrier for new users
- Indian early-career users are price-sensitive; monetization is hard at this ICP

**Mitigation for churn cliff:** Expand the value proposition before the user gets hired. Frame it as "Jarvis for your career, not just your job hunt" — the tool that builds your professional brand permanently, not just for 3 months of applying.

### Option B: Hackathon AI — "Jarvis is your co-founder for every hackathon"

**What it is:** Narrow even further — Jarvis as the specialist tool for AI/ML hackathon participants. War room strategy, tech stack selection, submission framing, demo script.

**Strengths:**
- Already built (hackathon war room exists in current Jarvis)
- Extremely underserved: no tool currently combines strategy + execution for hackathons
- High-intensity 48-72h engagement windows create deep memory rapidly
- Each submission = a portfolio artifact (self-reinforcing flywheel)
- Community: HackerEarth, Devfolio, Unstop are all Indian-first — reachable

**Weaknesses:**
- Smaller reachable market than career AI (hackathon participants are a subset of job seekers)
- Episodic usage — between hackathons, low engagement
- Harder to monetize (users don't have money to spend on hackathon-specific SaaS)

**Best case:** Hackathon AI is an acquisition channel, not the primary wedge. Users discover Jarvis through hackathon prep, then stay for career management.

### Option C: Personal AI for AI-Native Devs — "The AI that knows you"

**What it is:** Broader positioning — Jarvis as a personal operating system for people who build with AI tools. Memory + multi-agent + proactive = the connective tissue between all their tools and projects.

**Strengths:**
- Not temporally bounded (not tied to job hunt duration)
- Larger conceptual TAM
- Closer to the actual long-term product vision
- Differentiation is the deepest here (memory + compounding are the whole value prop)

**Weaknesses:**
- Hardest to demo in 60 seconds — "it's like having an AI that knows you" requires time to demonstrate
- No clear acquisition motion (who do you target and where do you find them?)
- More competition in the "personal AI" category (Mem.ai, Notion AI, Rewind.ai, etc.)
- Requires users to invest in onboarding before seeing value — high drop-off risk

### Wedge Recommendation: Option A with Option B as acquisition channel

**Launch with Career AI. Use Hackathon AI as the first taste.**

Reasoning:
1. Career AI has the highest-pain, most immediate use case for the ICP
2. The hackathon war room is already built and is the best demoable artifact — use it as the top-of-funnel "wow" experience that converts users into career management users
3. The "job hunt ends" churn risk is real, but it's a retention design problem, not a wedge problem — solve it in v1.1 by expanding to "career growth" mode post-hire
4. Option C is the 12-month vision, not the launch wedge — you cannot demo "compounding memory" to a new user; you can demo "Jarvis wrote your cover letter in your voice in 15 seconds"

NEEDS INPUT: Competitor audit on Teal / Simplify / LazyApply / Rezi is required before finalizing. Recommend dispatching research-agent on this before writing the full PRD.

---

## 4. The "Wow" Moment

### Definition: the single 60-second experience that makes a new user say "ChatGPT can't do this"

**The Wow:**
User types: "I'm applying to [Company X]. Write me a LinkedIn DM to their hiring manager."

Jarvis responds in 15 seconds with a DM that:
- Mentions the user's strongest project by name (from their uploaded resume or onboarding)
- References something specific about that company (from a 10-second web lookup)
- Uses the user's actual phrasing patterns (not corporate template language)
- Notes if they've applied to a similar company before and what happened (if logged)

The user immediately recognizes: "This sounds like me. It mentions what I actually built. ChatGPT would have given me a generic template."

**Why this works as the wow:**
- Happens in 60 seconds (no setup beyond onboarding)
- Contrast with ChatGPT is instant and visceral — the user can see what's different
- Uses memory (the core moat) visibly — the user can SEE that Jarvis knows them
- Creates an immediate artifact the user can actually send — real-world value, not a demo trick

**What makes it fail:**
- If the DM sounds generic or uses the wrong project — bad personalization is worse than no personalization
- If onboarding didn't collect enough signal — garbage in, garbage out
- If the company lookup is stale or wrong — this destroys trust immediately

**Implication:** The wow moment's quality is entirely determined by onboarding quality. Onboarding is not a nice-to-have — it is the product.

**Alternative wow (hackathon path):**
User pastes a hackathon problem statement. Jarvis returns a full strategy brief in 90 seconds: winning approach, tech stack recommendation, 3 scoring dimensions to optimize, and a project title. For hackathon-active users, this is the more visceral wow.

Founder decides: which wow moment to lead with in marketing and demo. Recommendation: use the hackathon wow for acquisition (shareable, impressive), the career wow for activation (personal, sticky).

---

## 5. MVP Scope (RICE-Ranked)

### RICE scoring note
Reach = % of v1 users who benefit from this feature (1-10 scale, 10 = all users).
Impact = effect on activation or retention if present (1-5 scale).
Confidence = L/M/H — how sure we are of the Reach and Impact estimates.
Effort = relative build effort (1 = already built, 5 = high net-new).
All Reach/Impact estimates are [ASSUMPTION] until validated with user interviews.

| Feature | Reach | Impact | Conf | Effort | RICE | v1? |
|---|---|---|---|---|---|---|
| **Memory onboarding (resume + 5-question intake)** | 10 | 5 | H | 2 | 25 | IN — non-negotiable foundation |
| **Tailored cover letter / cold DM writer** | 10 | 5 | M | 2 | 25 | IN — primary wow moment |
| **Resume diagnostic + ATS gap analysis** | 10 | 4 | H | 1 (resume-agent exists) | 40 | IN — highest-pain, already half-built |
| **Hackathon war room (strategy brief)** | 7 | 5 | H | 1 (already built) | 35 | IN — best demo artifact, low effort |
| **Application tracker (manual log + status)** | 9 | 3 | M | 2 | 13.5 | IN — lightweight; without it Jarvis has no longitudinal context |
| **Proactive daily briefing (jobs + deadlines)** | 9 | 3 | H | 1 (already built) | 27 | IN — already built; adds retention |
| **Interview prep (company research + mock Q&A)** | 7 | 4 | M | 3 | 9.3 | OUT — v1.1 |
| **Portfolio audit + update suggestions** | 6 | 3 | L | 3 | 6 | OUT — v1.1 |
| **LinkedIn post drafting (in user's voice)** | 6 | 3 | M | 2 | 9 | OUT — v1.1 |
| **Browser automation / auto-apply** | 8 | 4 | L | 5 | 6.4 | OUT — high effort, high privacy risk, wrong for v1 trust-building |
| **Multi-user / team collaboration** | 2 | 2 | L | 5 | 0.8 | OUT — not v1 |

### Explicit Non-Goals for v1

1. **Auto-submitting job applications on behalf of the user.** Jarvis drafts, user sends. Browser automation is v2+.
2. **Integrations with ATS platforms (Greenhouse, Lever, Workday).** API access to employer systems is not v1.
3. **Team/collaborative features.** v1 is personal, single-user only.
4. **Mobile app.** Web-first; mobile is v2.
5. **Voice interface as a primary interaction mode.** Jarvis has voice built, but it is not the v1 UX — text-first.
6. **Employer-side product** (helping companies find candidates). Purely user-side in v1.
7. **Global launch.** India-first for v1 (language, pricing, platform support — LinkedIn/Naukri).

### v1 Package (6 features)

1. Memory onboarding (resume upload + structured intake)
2. Tailored cover letter and cold DM writer
3. Resume diagnostic + ATS analysis
4. Hackathon war room (strategy brief)
5. Application tracker (lightweight)
6. Proactive daily briefing

This is the minimum that delivers the wedge + wow and has a reason for the user to return daily.

---

## 6. Onboarding: Making Jarvis "Know You" in Under 10 Minutes

**The stakes:** The personalization moat lives entirely in the quality of onboarding. A user who completes onboarding and gets a wow-quality first output will return. A user who completes onboarding and gets a generic output will not. Onboarding is the product, not the preamble.

### Proposed 3-layer onboarding flow (target: 8 minutes)

**Layer 1 — Fast Intake (3 minutes, 6 questions)**

Questions must be opinionated and concrete. No vague fields.

1. "What role are you hunting for? Be specific." (e.g., "ML Engineer at a mid-stage startup, India, remote-ok")
2. "Paste your best project's one-line summary." (forces them to articulate their strongest signal)
3. "What's your honest blocker right now?" (recruiter not responding / no interview callbacks / ghosted after round 1 / etc.) — this anchors Jarvis's first action
4. "Name one company you've applied to recently and what happened." (establishes baseline and starts the application tracker)
5. "How do you sound when you write messages to people you respect?" (paste a real message they've sent) — this is how Jarvis learns voice
6. "What are you entering next?" (hackathon / job application / both) — this sets the first proactive brief

**Layer 2 — Resume Upload (2 minutes)**

PDF or paste. Jarvis parses and extracts: strongest projects, tech stack, apparent gaps vs. target role, existing writing voice from bullet language. Immediately shows user what it extracted — user corrects anything wrong. This transparency builds trust and improves data quality.

**Layer 3 — First Action in Session (3 minutes)**

Do not let the user leave onboarding without a real output. Immediately after resume parse:

"Based on what you told me, here's a cold DM to a recruiter at [their named target company from Q4]. Read it. Does it sound like you?"

If yes: activation event achieved. User has seen the memory working.
If no: user corrects it, which is itself a memory training step. Still valuable.

**Key design principles for onboarding:**

- Never ask for permissions (email, LinkedIn OAuth) in onboarding. Ask for manual paste/upload first. Trust is earned, not front-loaded.
- Show the user what Jarvis "knows" about them before the first action — a brief "here's what I've learned about you" screen. This makes the memory visible and correctable.
- The onboarding completion event is defined as: resume parsed + at least one output generated that user did not immediately discard.
- NEEDS INPUT: What is the drop-off rate from question 1 to completion? Cannot be measured until there are real users. Instrument every step.

---

## 7. Success Metrics

### North-Star Metric (proposed)

**"Weekly active users who generated and used at least one Jarvis artifact" (WAU-with-action)**

"Used" = saved, copied, sent, or explicitly approved the output.

Why this North-Star: it connects memory quality (the moat) directly to user action (the value). An artifact that gets used means Jarvis knew the user well enough to be useful. An artifact that gets discarded means personalization failed. This metric degrades naturally when Jarvis is generic and improves when it is personalized.

Why NOT "weekly active users" alone: presence without action means the user is browsing, not benefiting.

### Metric Ladder

| Layer | Metric | Leading or Lagging | Target (v1, 90 days post-launch) | Notes |
|---|---|---|---|---|
| Acquisition | Signups per week | Leading | NEEDS INPUT — depends on launch channel | Track source (LinkedIn / Discord / referral) |
| Activation | % of signups who complete onboarding AND generate one artifact in session 1 | Leading | 60%+ | Below 50% = onboarding is broken |
| Activation quality | % of first artifacts rated "sounds like me" by user (explicit 👍 / 👎) | Leading | 70%+ | Below 60% = memory intake is insufficient |
| Retention D7 | % of activated users who return within 7 days | Leading | 40%+ | [ASSUMPTION] based on general SaaS benchmarks — validate against cohort |
| Retention D30 | % of activated users still active at 30 days | Lagging | 25%+ | [ASSUMPTION] |
| Core action | Artifacts generated per WAU-with-action | Leading | 3+ per week | Measures engagement depth |
| Business outcome | User gets a recruiter response, interview, or hackathon shortlist attributed to a Jarvis artifact | Lagging | 15%+ of active users report within 60 days | Self-reported; hard to measure but qualitatively essential |
| Revenue | NEEDS INPUT — no pricing model defined | — | — | Define before v1 launch |

### Activation Event (the "aha")

Defined: User generates their first artifact that they explicitly save or send. This should happen in session 1, during onboarding. If it doesn't happen in session 1, the probability of return drops sharply.

NEEDS INPUT: What is the median time from signup to first artifact? Cannot be estimated without instrumentation. Prioritize measuring this from day 1.

### What "not working" looks like

- Activation rate below 40%: Onboarding is too slow or first output is generic. Fix: shorter intake + stricter first-output quality gate.
- D7 retention below 30%: User got their wow moment but has no reason to return. Fix: proactive briefing and application tracker must create a daily habit loop.
- Artifact discard rate above 50%: Memory is not capturing enough signal. Fix: intake questions need to be more specific; resume parse needs improvement.

---

## 8. Top 3 Risks

### Risk 1: Privacy barrier blocks meaningful onboarding

**The threat:** To be genuinely useful, Jarvis needs to know the user's email, LinkedIn activity, resume, and application history. Asking for these from a new user — with no established trust — will cause abandonment. Even if users agree in principle, friction in connecting accounts kills completion rates.

**Why it could kill v1:** Without sufficient context, Jarvis produces generic outputs. Generic outputs = no wow moment. No wow moment = no retention. The personalization moat only works if personalization is actually achieved.

**Mitigation:**
- Never ask for OAuth / API access in v1. Manual upload and paste only. Lower the trust bar.
- Show users a "here's what Jarvis knows about you" preview before any output — makes the data use transparent and correctable.
- Start with the smallest useful context: just the resume + 6 questions is enough to produce a non-generic first output. Add email/LinkedIn access as an optional upgrade after trust is earned.
- Frame data collection as "teaching Jarvis" not "giving Jarvis access" — language matters for trust.

### Risk 2: "Job hunt ends" churn cliff

**The threat:** The career AI wedge is temporally bounded. When the user gets hired (the success outcome), the primary use case disappears. This creates a predictable churn wave approximately 2-6 months after acquisition, right when the user has the most positive feelings about the product.

**Why it could kill v1:** High churn = poor retention metrics = hard to grow through word-of-mouth (satisfied users leave before referring). Also: if the product's best users leave at their happiest moment, you lose your best referrers.

**Mitigation:**
- Expand the value proposition BEFORE the job is found. Introduce "career growth mode" (not "job hunt mode") early — projects to build for long-term career health, not just for landing a role. Hackathon AI is the natural bridge.
- At onboarding, set a "career goal" not just a "job hunt goal." This anchors the user's relationship with Jarvis to their career trajectory, not just the current sprint.
- Celebrate the hire. When a user marks a job as "accepted," congratulate them and immediately offer "now let's set up your first 90 days plan." This turns the churn trigger into a re-activation event.
- Track "post-hire retention" as a specific cohort metric from v1. If it's zero, the platform play is broken.

### Risk 3: Memory quality degrades the experience instead of improving it

**The threat:** Bad personalization is materially worse than no personalization. If Jarvis gets the user's voice wrong, uses the wrong project, or hallucinates context from their resume, the output is not just unhelpful — it is embarrassing. A user who pastes a Jarvis DM and sends it verbatim to a recruiter, only to have it be wrong, will never use the product again and will warn peers.

**Why it could kill v1:** The wow moment depends on personalization being accurate. If the first output is generically good but not personal, the user shrugs. If the first output is personally wrong (wrong project name, wrong company context, wrong voice), the user's trust is destroyed in the highest-stakes moment.

**Mitigation:**
- Build explicit confidence signaling into every output: "I'm basing this on [Project X from your resume] and [your stated target of ML roles]. Correct me if wrong." This turns hallucination risk into a trust-building opportunity.
- Implement an explicit 👍/👎 rating on every artifact in v1 — not just for analytics, but as a memory correction mechanism. Every downvote is a data point that improves the next output.
- Establish a minimum context threshold before Jarvis generates an output. If the user has only answered 2 of 6 onboarding questions, Jarvis should prompt for more context rather than generating a mediocre artifact.
- Do not generate an artifact and ask "does this look good?" Generate it, then immediately show: "Here's what I knew about you when I wrote this: [list]. Does this reflect you accurately?" This makes the memory visible and correctable in the same action.

---

## 9. Open Questions Before Any PRD Is Written

These are unresolved forks that will shape the PRD. Founder must answer or research-agent must answer before PRD work begins.

1. **Competitor audit (NEEDS INPUT):** Has anyone audited Teal, Simplify, LazyApply, Rezi, Pyjama Jobs, or any Indian-specific career AI tools in the last 6 months? What do they do well and what gap does Jarvis fill that they don't? This is required before finalizing the wedge.

2. **Pricing model (NEEDS INPUT):** No pricing decision has been made. Options: free-with-waitlist (community first, monetize later), freemium (5 artifacts/month free, unlimited paid), subscription (flat monthly at ₹299-499/mo India tier), usage-based. Each has different implications for the ICP. Must decide before building a signup flow.

3. **Hosting + cost model (NEEDS INPUT):** At what per-user LLM call cost does Jarvis become unprofitable at the India price point? [ASSUMPTION: Claude API costs at scale could be $0.10-2.00 per user session depending on context size.] This needs to be modeled before setting a price floor.

4. **User research gap (NEEDS INPUT):** All JTBD above is inferred from one user (the founder). Minimum viable research: 5 interviews with people who match ICP-A before the PRD is locked. Without this, every design decision is a guess.

5. **Distribution channel (NEEDS INPUT):** How will v1 users be acquired? LinkedIn organic? Discord communities (Devfolio, AI-India)? Hackathon-adjacent distribution (announce it at a hackathon)? Each channel shapes who the first users are and what feedback they give. Must be decided before launch planning.

6. **Platform dependency (NEEDS INPUT):** Current Jarvis is built on Claude Code + Anthropic API. What is the plan if Anthropic changes pricing or access terms? Is there a model-agnostic layer that protects the product from single-vendor dependency?

---

## Summary: Decision Points for Founder

| Decision | Options | Recommendation |
|---|---|---|
| v1 ICP | ICP-A (fresh grad India) / ICP-B (mid-career) / ICP-C (global) | ICP-A — tightest loop, founder = user |
| Launch wedge | Career AI / Hackathon AI / Personal AI platform | Career AI + Hackathon AI as top-of-funnel |
| Wow moment | Career DM in your voice / Hackathon war room in 90s | Lead with hackathon wow for acquisition, career wow for retention |
| MVP scope | 6 features (listed above) vs. narrower (resume + DM only) | 6 features — proactive briefing + tracker are cheap and needed for retention |
| Onboarding style | Form-based / Conversational / Resume-first | Conversational (6 questions) + resume upload — feels like Jarvis, not a form |
| Pricing | Freemium / Flat subscription / Usage-based | NEEDS INPUT — must model cost per user first |

---

*Saved: `/home/ujjwal/Documents/J.A.R.V.I.S./data/outputs/prds/jarvis-product-foundations-2026-06-01.md`*
*Next step: Dispatch research-agent for competitor audit (Teal / Simplify / Indian career AI). Then conduct 5 ICP-A interviews. Then write full PRD.*
