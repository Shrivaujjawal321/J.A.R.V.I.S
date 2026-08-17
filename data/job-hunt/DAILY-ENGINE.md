# Daily Job-Outreach Engine — Design & Runbook

**Goal:** Land AI/ML interviews for Ujjawal via a sustainable daily multi-channel outreach loop.
**Owner:** Jarvis (autonomous, daily). **Boss decisions:** sending channel = main Gmail safe batches · mix = quality-first.

## Honest cadence (NOT 150/day raw)
150 cold emails/day from a personal Gmail = spam-flag/suspension + ~0.5% reply. Quality-first wins more interviews:
- **~25 cold emails/day** (after a 1–2 week warmup ramp; start ~10/day) → ~125/week
- **+ 5–8 LinkedIn connect/DM/day**
- **+ 3–5 portal applies/day** (Wellfound/Cutshort/Instahyre/company ATS)
- Expected steady state: **1–2 replies/day, ~3–5 interviews/week** after 2 weeks of pipeline.

> Weekly volume ≈ 125 cold + 35 LinkedIn + 25 portal ≈ 185 touches — meets the "150" intent, safely, across channels.

## Daily loop (target 09:00–10:30 IST, Tue–Thu best)
1. **SOURCE** (research-agent): pull fresh AI/ML India roles — YC/Wellfound/Cutshort/Instahyre/LinkedIn + new postings at master-list firms. Dedupe vs `outreach-log.md`.
2. **VERIFY ADDRESS**: cold-email targets only. Confirm `firstname@domain` via Hunter.io/Apollo free tier (or company "People" page). Unverifiable → route to LinkedIn DM, never send to a guess (bounce = reputation hit).
3. **PERSONALIZE**: one tailored email per target — lead with the project that matches THEIR product (hook column in master list), <120 words, one ask, links not attachments.
4. **SEND (safe batch)**: ~25/day cap, warmup ramp respected, 10–11 AM IST. [Needs send-path live — see Setup.]
5. **FOLLOW-UP**: log scan — draft F1 (Day+4) and F2 (Day+10) for prior sends. Max 3 touches.
6. **PORTAL + LINKEDIN**: big-co targets → portal apply + recruiter/engineer DM (browser-autopilot; Tier-3 confirm on any final Submit).
7. **LOG**: append every contact to `outreach-log.md` (no-repeat).
8. **REPORT**: nightly Telegram — sent / replies / interviews / bounces.

## Setup needed to go fully autonomous (one-time)
- [ ] **Send path** — pick one: (a) re-auth Composio Gmail (`mcp__gmail__authenticate`) which can send; or (b) browser-autopilot drives Boss's logged-in Chrome to send drafts. + **confirm the sending Gmail account is shriva.ujjawal@gmail.com.**
- [ ] **Address verification** — Hunter.io / Apollo free API key (25–100/mo free) OR accept LinkedIn-DM fallback for unverifiable addresses.
- [ ] **Resume on Drive** — upload `Ujjawal_Shrivastav_AI_ML_Engineer.pdf` → public link for the email signature.
- [ ] **Schedule** — systemd timer / cron (model on existing LinkedIn pipeline timers) for the 09:00 IST run + nightly report.

## Files
- `batch-YYYY-MM-DD.md` — that day's personalized emails
- `outreach-log.md` — CRM / no-repeat source of truth
- `targets-startups-*.md`, `targets-product-*.md` — sourced target pools
- `outreach-playbook-*.md` — deliverability + channel + copy playbook (the rulebook)
