# AI/ML Job Hunt — Cold Outreach Operational Playbook
**Date:** 2026-06-20
**Target:** 2025 fresh grad AI/ML engineer, India-based, cold outreach to land interviews

---

## 1. Gmail Sending Limits & Deliverability

### Official Caps (not the real limits — read below)

| Account Type | Official Daily Cap |
|---|---|
| Free Gmail (@gmail.com) | 500 emails/day |
| Google Workspace (paid) | 2,000 emails/day |

### Real Safe Limits for Cold Email (this is what matters)

| Account Stage | Safe Daily Send | Risk Level |
|---|---|---|
| Fresh account, no warmup, Days 1–7 | 5–10 cold emails | Low risk |
| Fresh account, manual warmup, Days 8–14 | 10–20 cold emails | Low risk |
| Warmed account (2+ weeks of consistent use) | 20–30 cold emails | Low if bounce <2% |
| Warmed Workspace (4–12 weeks history) | up to 50–75 cold emails | Low |

**Key thresholds that trigger suspension (Google actively monitors):**

- Volume spike to 100+ sends in Week 1 → **immediate flag**
- Bounce rate above **5%** in any 24-hour window → flag
- Spam complaint rate above **0.08%** (stricter than Google's published 0.10%) → flag
- Domain age under 14 days → heightened scrutiny regardless of volume
- Missing/misconfigured DMARC → increases risk multiplier
- **Suspension rate for fresh Workspace accounts sending 50+ cold emails in first 30 days: above 30%**
- Pre-warmed accounts (4–12 weeks history) at 150/day: below 1% suspension rate

Sources: Litemail.ai (Google Workspace suspension rate study), Smartlead, Mailmeteor

### Warmup: What It Means and Realistic Numbers

"Warmup" = training Gmail/Workspace's sending reputation by starting with low volumes of human-style email (replies to real people, newsletter engagement, normal correspondence) before sending cold outreach.

**Warmup Ramp — Day-by-Day:**

| Period | Warmup Volume | Cold Email Volume | What to Do |
|---|---|---|---|
| Days 1–7 | 5–10 real sends (replies, known contacts) | 0 | No cold yet. Activate SPF, DKIM, DMARC |
| Days 8–14 | 10–20 sends/day | 3–5/day max | Start with highest-quality targets |
| Days 15–21 | 20–30 sends/day | 5–10/day | Monitor bounce rate daily |
| Days 22–30 | 30–40 sends/day | 10–15/day | Build rhythm |
| Days 31+ | Maintenance (10–15 warmup/day) | 20–30/day max | Never kill warmup entirely |

**Safe permanent ceiling for a personal job-hunt account: 25–30 cold emails/day.**
Going above 30/day on a personal account that is not specifically an outreach-configured Workspace domain is not worth the risk of account suspension.

Free tools to automate warmup: Mailreach (freemium), Instantly warmup mode, Lemwarm (freemium).

---

## 2. Finding Real Hiring Manager / Recruiter / Founder Emails

### The Email-Finding Toolkit (Free → Paid)

#### Tier 1: Free (start here)

| Tool | What It Gives You | Free Limit | Best For |
|---|---|---|---|
| **Hunter.io** | Domain search → company email pattern + confidence score + verification | 25 searches/month | Startup founders, HR |
| **Apollo.io** | 270M+ contact DB, email + phone, sequences | ~100 email credits/month (2026 limit) | Recruiters, hiring managers at mid-size companies |
| **LinkedIn → Email pattern guess** | Find name/company via LinkedIn, guess pattern, verify | Unlimited (guessing) | Any company |
| **Google** | `site:linkedin.com/in "AI engineer" "hiring" "India"` + `"@company.com" "engineering"` dorking | Unlimited | Exploratory |
| **Company careers page** | Often lists team leads or department heads | Unlimited | Targeted companies |

#### Tier 2: Paid (if scaling to 50+ targets/week)

| Tool | Cost | Strength |
|---|---|---|
| Hunter.io Starter | $49/month | 500 searches, bulk domain scan, built-in verifier |
| Apollo.io Basic | $59/month | 1,000 email credits + sequences |
| RocketReach | $53/month | Best for Indian startup founders specifically |
| Clearbit Connect | Freemium | Chrome plugin, works inside Gmail |

### Common Email Patterns (guess + verify)

Most Indian tech companies follow one of these patterns:
- `firstname@company.com`
- `firstname.lastname@company.com`
- `f.lastname@company.com`
- `firstnamelastname@company.com`
- `firstname_lastname@company.com`

Use Hunter.io domain search first — it tells you the pattern for that specific company.

### Email Verification Before Sending (MANDATORY)

**Never send to an unverified address.** Bounces above 2% wreck your sender score permanently.

| Verifier | Free Tier | Accuracy | Use Case |
|---|---|---|---|
| **Hunter.io built-in** | 25/month (bundled with searches) | ~95% | Default for any email from Hunter |
| **ZeroBounce** | 100 one-time credits on signup | 95–99% | Batch verify a new list |
| **Bouncer** | 1,000 on signup | 95–99% | Best free bulk option |
| **NeverBounce** | None (pay-as-you-go $0.008/check) | 95–99% | When you need reliability at scale |

**Verification workflow:**
1. Find email via Hunter / Apollo / pattern guess
2. Run through ZeroBounce or Hunter's verifier
3. Status "Valid" = safe to send. "Risky" = your call. "Invalid" = never send.

---

## 3. Channel Ranking by Expected Yield — India AI/ML Fresh Grad

Ranked by realistic interview conversion rate per unit of effort:

| Rank | Channel | Expected Reply Rate | Interview Conversion | Notes |
|---|---|---|---|---|
| 1 | **Warm referral** | 40–60% | 15–25% | Single best channel — always ask |
| 2 | **Cold email to startup founder** | 8–15% | 5–10% | Founders read their inbox. Keep email 100 words. |
| 3 | **LinkedIn DM (post-connection)** | 16–25% | 5–8% | Must connect first, then DM after acceptance |
| 4 | **Cold email to recruiter / HR** | 5–10% | 3–6% | HR at mid-size companies; less effective at enterprises |
| 5 | **Wellfound / AngelList direct apply** | 10–20% viewed | 3–5% | Startup-focused, profiles visible to founders directly |
| 6 | **LinkedIn Easy Apply** | 2–5% | 1–3% | High volume, low quality. ATS black hole at enterprises |
| 7 | **Cutshort / Instahyre** | 5–15% | 2–4% | Better than Naukri for AI/ML; matching-based reduces noise |
| 8 | **Naukri.com** | 1–3% | 0.5–1.5% | High competition, keyword-matched ATS, mostly MNCs |
| 9 | **Careers page ATS (direct)** | 1–3% | 0.5–1.5% | Identical to Naukri — black hole unless you have referral |

**Key insight:** Cold email to a startup founder (Series A or below) + Wellfound apply is the highest-leverage combo for an AI/ML fresher in India. Founders at sub-50-person startups read and reply to direct emails. Enterprise applications (Naukri, LinkedIn Easy Apply) are a volume game with nearly zero ROI per hour invested.

---

## 4. Cold Email Best Practices — Junior AI/ML Engineer, 2026

### Subject Line

**What works (pick one pattern):**
- Achievement-led: `"Hackathon Winner → Interested in ML Eng @ [Company]"`
- Project-led: `"Built RAG system with [X users] — roles at [Company]?"`
- Mutual hook: `"Saw your [specific post/paper] — AI Eng opportunity?"`
- Direct: `"AI/ML Fresher | IIT/NIT | Intern @ [Brand] | [Role] @ [Company]"`

**Rules:**
- Under 50 characters (mobile preview cut-off)
- No spam trigger words: "opportunity", "job offer", "position available", "free"
- Always include company name (personalization → open rate lift ~20%)
- No emoji in subject for professional targets (some founders are fine with it, most are not)

### Email Body — Structure (100–120 words MAXIMUM)

```
Hi [FirstName],

[1 sentence: specific reason you're emailing THEM/THEIR company — not generic]

[1–2 sentences: your single strongest proof-of-work. Lead with project, not degree]
→ "I built [X] — it does [Y], has [Z users/metric]."
→ "I won [Hackathon] building [problem area]."

[1 sentence: connect your project to their actual problem / product]

[1 sentence: explicit ask — not "a chat", not "to connect", but the specific next step]
→ "Would a 20-min screen this week work?"

[Resume link + GitHub/demo link — no attachment, use Google Drive or portfolio URL]

[Name]
```

**What NOT to do:**
- "I hope this email finds you well" — delete immediately
- Paste your entire resume in the body
- Ask for "guidance" or "mentorship" — vague and low-priority
- Send attachments (triggers spam filters, never opens on mobile)
- Lie about competing offers when you have none — gets found out in calls

### Project > Pedigree for Freshers

This is the most important structural insight. A recruiter at a 20-person startup does not care about your B.Tech CGPA. They care:
1. Can you ship? (Show a link to something live or a GitHub with real commits)
2. Do you understand our problem space? (1 sentence connecting your project to theirs)
3. Are you easy to talk to? (Email tone signals communication skill)

**Freshers: Lead with the best of:**
- A deployed project with actual users or metrics
- Hackathon win (especially if recognizable: Smart India Hackathon, HackerEarth, Kaggle)
- Open-source contribution with stars/forks
- A published paper or notable dataset contribution
- A Jarvis-style agentic project is a strong differentiator in AI/ML in 2026

### Follow-Up Cadence

| Follow-Up | Timing | Content |
|---|---|---|
| Email 1 | Day 0 | Full cold email |
| Email 2 | Day 4–5 | 2–3 lines. New angle or context. Not "just checking in." |
| Email 3 | Day 10–12 | Last bump. Mention if you have other interviews. |
| Stop | Day 14+ | If no reply after 3 touches, move on. Try a different contact at same company. |

**Best days to send:** Tuesday, Wednesday, Thursday
**Best times:** 10–11 AM or 2–3 PM in recipient's timezone (IST for India-based companies)
**Never send:** Friday afternoon, Saturday, Sunday, Monday morning

### Legal / Ethical Line (India)

- **CAN-SPAM** applies only to US-based recipients. India has **no equivalent cold email law** as of 2026. The TRAI DND registry covers SMS/calls, not email.
- **DPDP Act 2023** is in force but implementation rules still pending. B2B business email is a grey area — enforcement is near-zero currently.
- **Practical ethical rules** (not legal — reputational):
  - Always include your real name and contact info
  - Never forge headers or sender identity
  - Honor any "please don't contact me" response immediately
  - Max 3 touches per person before stopping
  - Do not mass-blast the same email to 100 people simultaneously — triggers spam filters AND looks lazy if a startup team compares notes

---

## 5. Daily System Design — 2025 Fresh Grad Solo

### The Math

- Safe daily email volume: **20–25 cold emails/day** (after 2-week warmup)
- Target pipeline: **3–5 new companies added per day**
- Contact 3–4 people per company (1 founder + 1 tech lead + 1 recruiter, in that priority order)
- Expected reply rate (weighted across channels): ~8–10%
- At 20 emails/day: expect 1–2 replies/day at steady state
- Pipeline to interviews: roughly 10–15 cold emails per interview scheduled

### Daily Time Budget (2–3 hours total)

| Block | Time | Action |
|---|---|---|
| Morning (30 min) | 9–9:30 AM | Research 3 target companies. Find 1 founder + 1 recruiter email each. Verify via ZeroBounce/Hunter. |
| Morning (45 min) | 9:30–10:15 AM | Write 10–12 personalized cold emails. Send by 10:30 AM (optimal open window). |
| Midday (15 min) | 12–12:15 PM | Check replies, respond immediately to any reply within 2 hours (shows enthusiasm). |
| Afternoon (30 min) | 2–2:30 PM | LinkedIn — send 5 connection requests (personalized note) to targets for tomorrow's email outreach. |
| Afternoon (30 min) | 2:30–3 PM | Wellfound / Cutshort — apply to 3–5 startup jobs with tailored 1-para cover message. |
| Evening (20 min) | 7 PM | Log everything. Update CRM (Notion table or Google Sheet). Schedule follow-ups. |

### Weekly Volume Targets

| Channel | Per Day | Per Week |
|---|---|---|
| Cold emails sent | 20–25 | 100–125 |
| LinkedIn connection requests | 5–8 | 25–40 |
| LinkedIn DMs (to accepted connections) | 3–5 | 15–25 |
| Wellfound / Cutshort applications | 3–5 | 15–25 |
| Follow-up emails (sequence) | 5–10 | 25–50 |

### CRM / Tracking (Non-Negotiable)

Maintain a simple spreadsheet with columns:
`Company | Contact Name | Role | Email | Date Sent | Response | Follow-up 1 | Follow-up 2 | Status`

Without tracking, you will double-contact people, miss follow-ups, and have no data to improve. Use Notion, Google Sheets, or Airtable (free tier).

### Highest-Leverage Startup Target List (India, AI/ML 2026)

Focus cold email on these company types first:
1. **YC India portfolio** (search YC Companies → India filter → AI/ML)
2. **Sequoia Surge cohort companies** (early-stage, founder reads email)
3. **Better Capital / Kalaari / Rainmatter portfolio** (active AI/ML investment)
4. **AI-first startups on Wellfound India** (filter: 10–50 employees, AI/ML stack)
5. **Product companies (not service/IT)** — avoid TCS/Infosys/Wipro for cold email (they have zero cold-email to hire pipeline)

---

## Tools Stack — Minimum Viable Setup (Free)

| Need | Tool | Cost |
|---|---|---|
| Email discovery | Hunter.io (25 free/month) + Apollo.io (100 free/month) | Free |
| Email verification | ZeroBounce (100 free credits) + Bouncer (1,000 signup) | Free |
| Email sending | Gmail (personal, warmup for 2 weeks first) | Free |
| LinkedIn outreach | LinkedIn Free (connection req → DM) | Free |
| Startup jobs | Wellfound + Cutshort (free profile) | Free |
| CRM / tracking | Google Sheets or Notion free tier | Free |
| Warmup | Mailreach free tier or manual (reply to newsletters) | Free |

**Total cost to run this playbook at full volume: Rs. 0/month**

---

## Executive Summary (6 Lines)

**Single most important recommendation: Cap cold email at 20–25/day and verify every address before sending.**

1. A fresh Gmail/Workspace account sending 50+ cold emails in its first 30 days faces 30%+ suspension probability — destroy your sending reputation before the job hunt gains momentum. Warmup for 14 days first, never skip.
2. Cold email to startup founders (Series A or below) + Wellfound direct apply is the highest-yield channel combination for an AI/ML fresher in India — expect 8–15% reply rates vs 1–3% on Naukri ATS black holes.
3. Lead with one deployed project or one measurable achievement — not your CGPA, not your college name. "I built X, it does Y, Z users" in sentence one is worth more than a 3-page resume.
4. Follow up exactly 3 times (Day 0, Day 4–5, Day 10–12) and stop. Every email must add new context — never send "just checking in."
5. The legal risk of cold emailing in India is near-zero in 2026 (no CAN-SPAM equivalent, DPDP enforcement pending) but your reputational risk with the startup community is real — keep volume disciplined and honor every "stop contacting me" response.
6. Sustainable daily system: 20–25 cold emails + 5–8 LinkedIn connection requests + 3–5 Wellfound applications = roughly 1–2 inbound replies/day at steady state = 3–5 interviews/week after 2 weeks of pipeline buildup.

---

## Sources

- [Gmail Sending Limits 2026 — Mailmeteor](https://mailmeteor.com/blog/email-sending-limits)
- [Gmail Sending Limits 2026 — Smartlead](https://www.smartlead.ai/blog/gmail-sending-limits)
- [Google Workspace Suspension Rate Cold Email — Litemail.ai](https://litemail.ai/blog/google-workspace-inbox-suspension-rate-cold-email)
- [Google Workspace Cold Email Limits — OutboundSystem](https://outboundsystem.com/blog/google-workspace-cold-email-limits)
- [Email Warmup Schedule Day-by-Day — Mailivery](https://mailivery.io/blog/email-warmup-schedule)
- [Gmail Warmup Guide 2026 — Mailreach](https://www.mailreach.co/blog/gmail-warmup)
- [30-Day Warmup Plan — Instantly.ai](https://instantly.ai/blog/30-day-warmup-outsourced-sales-emails/)
- [Hunter.io vs Apollo 2026 — Cleanlist](https://www.cleanlist.ai/blog/2026-03-07-hunter-vs-apollo)
- [Hunter.io Email Finder 2026 — ReachStream](https://resources.reachstream.com/hunter-io-email-finder-verification/)
- [ZeroBounce vs NeverBounce 2026 — BounceCheck](https://bouncecheck.email/blog/zerobounce-vs-neverbounce)
- [Email Verification Benchmark 2026 — Instantly](https://instantly.ai/blog/2026-email-verification-benchmark-accuracy-scores-for-8-top-tools/)
- [Cold Email vs LinkedIn InMail 2026 — Clearout](https://clearout.io/blog/cold-email-vs-linkedin-inmail/)
- [Cold Outreach Reply Rates 2026 — GigRadar](https://gigradar.io/blog/cold-outreach-reply-rates-comparison)
- [Cold Email vs LinkedIn Response Rates — GetFuzzy](https://getfuzzy.ai/blog/cold-email-vs-linkedin-response-rates-b2b)
- [LinkedIn InMail Response Rate Statistics — SalesSo](https://salesso.com/blog/linkedin-inmail-response-rate-statistics/)
- [LinkedIn Response Benchmarks 2025 — EngageKit](https://blog.engagekit.io/linkedin-response-benchmarks-2025/)
- [Cold Email for Jobs Guide — NickSingh.com](https://www.nicksingh.com/posts/cold-email-tips-to-land-your-dream-job-with-examples)
- [Cold Emailing & LinkedIn DM Outreach Guide for Job Seekers — Aryan Substack](https://aryan1.substack.com/p/cold-emailing-and-linkedin-dm-outreach)
- [How I Got Interviews Through Cold Emailing as a Fresher — RoadsideCoder](https://roadsidecoder.hashnode.dev/how-i-got-job-interviews-through-cold-emailing-as-a-fresher)
- [Cold Email Laws 2026 — Overloop](https://overloop.com/blog/cold-email-illegal)
- [Cold Email Legal Compliance 2026 — TrulyInbox](https://www.trulyinbox.com/blog/cold-email-compliance/)
- [Best India Job Sites 2026 — CareerBoom](https://careerboom.ai/en/us/blog/tool-review/best-india-job-platforms)
- [Apollo.io Pricing 2026 — SalesHandy](https://www.saleshandy.com/blog/apolloio-pricing/)
