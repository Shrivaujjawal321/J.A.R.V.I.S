# LinkedIn Daily Post Calendar — Boss's Voice

Rotating 7-day content plan. Each day has a *theme*, a *hook style*, and a *CTA pattern*.
The `post_generator.py` reads this file + Boss's recent activity + voice samples and drafts the post.
Boss approves via Telegram morning batch. Auto-publishes via browser-autopilot only after approve.

---

## Voice rules (read by `post_generator.py`)

- **Mirror Boss's natural register** — Hinglish-ok where it sounds natural; English when professional weight needed.
- **Hook in first 2 lines** (LinkedIn truncates after ~210 chars on mobile). Specific > clever.
- **No "thrilled to announce" / no humblebrag / no "in today's fast-paced world"** — instant scroll-past.
- **Use line breaks generously** — wall-of-text dies on LinkedIn.
- **End with one concrete CTA** — comment prompt, link, ask. Not "thoughts?" (lazy).
- **Length:** 800–1,500 chars sweet spot for impressions; 1,800+ for thought-leadership pieces.
- **Hashtags:** 3-5 max, end of post, niche > broad. `#AIagents` beats `#AI`.

---

## Weekly rotation

### Monday — Tech News Take
- **Theme:** Comment on a 2026 AI/ML news item from last 48h
- **Hook style:** "X just announced Y. Here's what most people missed:"
- **CTA pattern:** "What's your take on [implication]?"
- **Source feed:** `data/news/` (RSS digest) + Boss's recent reads
- **Avoid:** Generic "AI is changing everything" takes

### Tuesday — Project Showcase
- **Theme:** Something Boss built (Jarvis, hackathon project, side project, OSS contrib)
- **Hook style:** "I built [X] in [Y time]. Here's what broke and what I learned:"
- **CTA pattern:** Link to GitHub / live demo + "Would love feedback"
- **Source:** `data/conversations/`, `data/outputs/`, `data/hackathons/`
- **Avoid:** Pure self-promotion without story

### Wednesday — Hackathon Spotlight
- **Theme:** Upcoming hackathon Boss is watching/joining, OR recap of one he attended
- **Hook style:** "[Hackathon] is open. Here's why I'm building [X] for it:"
- **CTA pattern:** "Who's joining? Let's team up." + link
- **Source:** `data/hackathons/`
- **Avoid:** Just listing details — add a personal angle

### Thursday — Learning Thread
- **Theme:** Something technical Boss learned recently (paper, framework, debugging story)
- **Hook style:** "I spent [N] hours figuring out [X]. The trick was [Y]:"
- **CTA pattern:** "Anyone else hit this? How did you solve it?"
- **Source:** Boss's recent code/research conversations
- **Avoid:** Tutorial-style; this is narrative

### Friday — Hot Take / Opinion
- **Theme:** Contrarian view on AI/ML/career/tech
- **Hook style:** "Unpopular take: [bold claim]. Here's why:"
- **CTA pattern:** "Disagree? Tell me where I'm wrong."
- **Source:** Boss's strongly-held views (memory + recent rants)
- **Avoid:** Empty contrarianism for engagement bait — must be defensible

### Saturday — Weekly Recap / Behind-the-Scenes
- **Theme:** What Boss shipped/learned/failed at this week
- **Hook style:** "This week I [shipped X / failed at Y / learned Z]. Three takeaways:"
- **CTA pattern:** "What did you build this week?"
- **Source:** Last 7 days of conversations + git log + tasks completed
- **Avoid:** Brag list — include the failures too

### Sunday — Engagement Day (NO POST, but heavy commenting)
- **Theme:** No new post. Comment thoughtfully on 15-20 ICP posts.
- **Why:** Algorithm rewards engagement reciprocity. Pure comment day signals "real human."
- **Source:** Top posts from connections in `data/linkedin/icp.json` categories
- **Tracked by:** `engagement_loop.py` (logs comment count to nightly report)

---

## Holiday / event overrides

- **Project deploy day** (any day): Vercel webhook → next-morning slot becomes auto-Project-Showcase regardless of weekday.
- **Hackathon submission day**: Override → recap post about the build.
- **Major industry news** (e.g., new model release): Monday slot auto-redirects to that.
- **Boss explicit override:** If Boss says "post this today," it preempts the calendar.

---

## Content quality bar (post_generator.py self-check)

Before sending to Telegram approval, the draft must pass:
- [ ] Hook in first 2 lines is specific (not vague)
- [ ] At least one concrete number, name, or example
- [ ] No banned phrases ("thrilled", "humbled", "game-changer", "in today's world")
- [ ] One clear CTA (not "thoughts?")
- [ ] 800-1800 chars
- [ ] 3-5 niche hashtags
- [ ] Line breaks at least every 3 sentences

If draft fails, regenerate with feedback. Max 3 retries, then escalate to Boss with note.
