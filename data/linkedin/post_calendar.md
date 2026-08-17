# LinkedIn Daily Post Calendar — Boss's Voice (Pure Tech-News Mode)

Daily AI/ML tech-news posting plan. Every day has a *different angle* on tech news so the
feed never feels monotone. The `post_generator.py` reads this file + the latest news
digests in `data/briefings/news-*.md` + Boss's recent activity, then drafts the post.

Boss approves via Telegram morning batch (fullauto = auto-approves). Auto-publishes via
browser-autopilot at the next `jarvis-linkedin-execute.timer` slot (10:04 IST daily).

**Mode switched from "weekly rotation" → "daily tech news" on 2026-05-21 per Boss's call.**
Old themes (project / hackathon / learning / recap) are deprecated but preserved at the
bottom of this file in case of fallback.

---

## Voice rules (read by `post_generator.py` regardless of theme)

- **Mirror Boss's natural register** — Hinglish-ok where it sounds natural; English when professional weight needed.
- **Hook in first 2 lines** (LinkedIn truncates after ~210 chars on mobile). Specific > clever.
- **No "thrilled to announce" / no humblebrag / no "in today's fast-paced world"** — instant scroll-past.
- **Use line breaks generously** — wall-of-text dies on LinkedIn.
- **End with one concrete CTA** — comment prompt, link, ask. Not "thoughts?" (lazy).
- **Length:** 800–1,500 chars sweet spot for impressions; 1,800+ for thought-leadership pieces.
- **Hashtags:** 3-5 max, end of post, niche > broad. `#AIagents` beats `#AI`.
- **Source-bound:** every claim must trace to a real story in the news block. No invented news.

---

## Daily tech-news rotation

### Monday — Weekend Wrap
- **Theme:** Top 1-3 AI/ML stories from Fri-Sun. Frame what the wider conversation is missing.
- **Hook style:** `"What you missed in AI over the weekend:"` then 2-3 punchy lines listing the items.
- **CTA pattern:** `"Which of these shifts your stack this week?"`
- **Source feed:** `data/briefings/news-*.md` (latest 3 files)
- **Avoid:** Generic "AI is moving fast" framing. Be specific — name companies, models, numbers.

### Tuesday — Paper / Research Breakdown
- **Theme:** ONE recent paper (arxiv, Anthropic/OpenAI/DeepMind/HF blog). What it actually proves vs how it's being marketed.
- **Hook style:** `"[Paper title] in one paragraph. The trick:"` followed by a tight technical summary.
- **CTA pattern:** `"Anyone tried this in prod yet? What broke?"`
- **Source feed:** `data/briefings/news-*.md` + Boss's recent paper notes
- **Avoid:** Vague summaries — name the dataset, the metric, the delta over prior SOTA.

### Wednesday — Product / Model Launch Take
- **Theme:** A specific product or model release (new SDK, model checkpoint, dev tool). What most analysis is missing.
- **Hook style:** `"[Company] just shipped [X]. Here's what most takes are missing:"`
- **CTA pattern:** `"Will you migrate to it? What's your blocker?"`
- **Source feed:** `data/briefings/news-*.md` + Boss's recent reads
- **Avoid:** Pure marketing recap — add a technical or strategic angle.

### Thursday — Dev Tooling / Infra News
- **Theme:** Tooling moves — LangChain, DSPy, vLLM, Modal, Replicate, HF, new SDK, infra benchmarks.
- **Hook style:** `"[Tool] just got [feature]. Why builders should care:"`
- **CTA pattern:** `"What's your default for [X] in 2026?"`
- **Source feed:** `data/briefings/news-*.md` + tech-stack memory
- **Avoid:** Press-release tone. Lead with what changes for a working engineer.

### Friday — Hot Take / Controversy
- **Theme:** A defensible contrarian view on a current news item or industry trend. Real argument, not engagement bait.
- **Hook style:** `"Everyone's saying [common take]. They're wrong because:"`
- **CTA pattern:** `"Where am I wrong? Be specific — I'll defend the position in replies."`
- **Source feed:** `data/briefings/news-*.md` + Boss's strongly-held views (memory)
- **Avoid:** Empty contrarianism. The take must be defensible with examples.

### Saturday — Weekly Roundup
- **Theme:** Top 5 AI/ML stories of the week, ranked, with #1 being the *most overlooked* (not necessarily the biggest).
- **Hook style:** `"5 AI stories this week. #1 is the one most people missed:"`
- **CTA pattern:** `"Which one changes how you build next week?"`
- **Source feed:** `data/briefings/news-*.md` (all of past 7 days)
- **Avoid:** Just listing — each item gets a one-line "why it matters."

### Sunday — Builder Spotlight
- **Theme:** ONE person or team who shipped something noteworthy this week (paper, OSS release, demo, model checkpoint, viral thread).
- **Hook style:** `"[Person/Team] shipped [project] this week. Why it matters:"`
- **CTA pattern:** `"Tag a builder who deserves more attention this week."`
- **Source feed:** `data/briefings/news-*.md` + Twitter / X mentions in news digests
- **Avoid:** Big-company employees only — surface independent builders + smaller teams too.

---

## Holiday / event overrides (preempts daily theme)

- **Boss explicit override:** If Boss says "post this today," it preempts the calendar.
- **Major industry news** (new GPT-class model release, major acquisition, ToS-shift): any day's slot can switch to a "breaking news take" — frame it as Wednesday Product Launch Take regardless of weekday.
- **Hackathon submission day:** override → recap post about Boss's build.
- **Project deploy day** (Vercel webhook): next morning slot becomes Tuesday Paper Breakdown OR Wednesday Product Launch depending on what shipped.

---

## Content quality bar (post_generator.py self-check)

Before sending to Telegram approval, the draft must pass:
- [ ] Hook in first 2 lines is specific (not vague)
- [ ] At least one concrete number, name, model, or company
- [ ] No banned phrases ("thrilled", "humbled", "game-changer", "in today's world")
- [ ] One clear CTA (not "thoughts?")
- [ ] 800-1800 chars
- [ ] 3-5 niche hashtags
- [ ] Line breaks at least every 3 sentences
- [ ] News claim is traceable to a story in the source block (no fabricated news)

If draft fails, regenerate with feedback. Max 3 retries, then escalate to Boss with note.

---

## Deprecated themes (kept for fallback only — DO NOT use unless override)

Pre-2026-05-21 weekly rotation. Replaced by daily tech-news mode above.

- `monday_news_take`, `tuesday_project`, `wednesday_hackathon`, `thursday_learning`,
  `friday_hot_take`, `saturday_recap`, `sunday_engagement_only`
- If you need to revert, update `DAY_THEMES` in `scripts/linkedin/post_generator.py`
  to map back to these keys and restore the old `THEME_BRIEFS`.
