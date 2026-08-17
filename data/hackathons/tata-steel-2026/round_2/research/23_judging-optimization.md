# Component 23 — Judging-Criteria Optimization & Submission Strategy
**Tata Steel AI Hackathon 2026 | Round 2 | Agentic AI Challenge**
*Research date: 2026-06-06 | Deadline: 2026-06-15 23:59 IST*

---

## 1. Recommended Approach (One Clear Winner)

**The Orchestrated Demo-Evidence Method**: design every build decision backwards from explicit judge-criterion coverage, run the demo as a scripted, deterministic proof of each criterion in sequence, and make the architecture document a second judge (it must stand alone as a complete technical story).

This is not a meta-strategy — it is a concrete engineering discipline with three mandatory artifacts and one decision filter:

- **JUDGE_MATRIX.md** (Step 0.6 of the build playbook): a live matrix mapping each of the 13 scoring axes (6 email + 7 webinar) to specific build features + the exact demo moment that satisfies each. Any axis with zero coverage triggers an immediate build task. Any feature with fewer than 2 axis touchpoints is a candidate to cut.
- **HAPPY_PATH.md**: a 5-step scripted demo with target timestamps. Every second of screen-recording time is allocated to a specific judging axis. Nothing improvised.
- **docs/ARCHITECTURE.md** (8 sections, stub on Day 1, completed by Day 8): the document judges read when the video ends. It must tell the complete story without the narrator.
- **Decision filter**: at every build decision, ask "which of the 13 axes does this satisfy?" If the answer is zero, deprioritize or cut.

The pattern is validated across multiple 2025–2026 agentic AI hackathons (Great Agent Hack 2025, Kong Agentic AI Hackathon, Microsoft AI Agents Hackathon 2025, GitLab AI Hackathon 2026). Winners universally shared: (a) working demos over slides, (b) visible reasoning/traceability, (c) production quality over prototype flair, and (d) real problem framing before technical elegance.

---

## 2. Why — Evidence-Based Reasoning

### 2.1 The 13-Axis Reality of This Hackathon

Tata Steel judges on 13 simultaneously active axes — 6 from the email announcement and 7 from the webinar. Most competitors will address the 6 email criteria. Addressing all 13 gives a structural edge, because the webinar axes (Fast, Efficient, Accurate, Easy to use, Doesn't break, No errors, Smooth) are operational qualities that are easy to demonstrate in a working system and very hard to fake in a slide deck.

**Critical insight from the webinar notes (2026-06-05):** The operational axes are scored as observed facts during demo review, not as claims in the document. A system that crashes, hangs, or shows a traceback during the recording loses points on axes K, L, and M regardless of how good the written explanation is. This means demo robustness is not a polish concern — it is a scoring multiplier affecting 7 of 13 axes simultaneously.

### 2.2 Evidence That "Working Demo" Beats Slides

- GitLab AI Hackathon 2026 winner (LORE): judge April Guo said explicitly "this feels like a product, not a hackathon project." The signal: 43 automated tests, production-grade engineering, working in the judge's hands.
- Kong Agentic AI Hackathon 2025: "Every winning entry had a working demo. Real code. Real impact." Submissions without a runnable demo were not considered.
- Microsoft AI Agents Hackathon 2025: the judging rubric explicitly listed "actual demo (not a Figma file or presentation)" as a requirement. Teams submitting only decks were disqualified.
- Great Agent Hack 2025 winner (Zarks.AI, Track B): won specifically by building "a real-time observability framework that captures full execution traces and human-interpretable reasoning chains" — not the most technically complex entry, but the one that made its reasoning visible to judges.

### 2.3 Evidence That Trace Visibility Wins Agentic AI Specifically

The Great Agent Hack 2025 was organized around three governance tracks: performance, transparency, and safety. The transparency track (Agent Glass Box) required "capturing every decision step, memory update, and tool interaction." Zarks.AI won by making agent reasoning human-interpretable and auditable. This directly maps to Tata Steel's Requirement 4 (Explainable + traceable outputs) and judging axis C (Technical Implementation & Innovation).

In the agent trace expander (Step 6.2 of the build playbook), showing the LangGraph nodes fired + latency_ms per node is a 30-second demo moment that satisfies two axes simultaneously (Explainability + FAST proof).

### 2.4 Evidence That Framing Beats Code at This Specific Judging Level

The OpenAI Codex Hackathon winner (2025) won not because of code sophistication but because of "validating the problem itself" — the evaluation framework, not the generator. In industrial AI hackathons judged by Tata Steel's own AI leadership team (who have 800+ deployed models and 8 years of industrial AI), the most powerful signal is demonstrating that you understand their actual pain. Anchoring the demo framing to Tata Steel's published KPIs (22% downtime reduction via Asset Sphere, INR 1.4B savings cited in their own press releases) signals domain comprehension that pure-technical submissions lack.

### 2.5 Evidence From Design Document Structure Research

The SOFTBOTS AI Hackathon 2026 guidebook and multiple industrial AI submission templates consistently require: problem statement → system architecture → innovation differentiation → sector impact → business viability. The Tata Steel problem statement is explicit: the design document must cover all eight content areas (architecture, tech stack, data flow, model design, alerting logic, assumptions, install/run, sample I/O). An incomplete document guarantees a score penalty on Axis A (Problem Understanding & Approach) and Axis E (Presentation & Communication Quality) regardless of how good the code is.

### 2.6 Demo Video Best Practices (Primary Source: Devpost Official Guide)

Six validated tips from the Devpost canonical guide (the platform running most hackathon submissions):
1. Reserve 2–3 hours for recording/editing — never record under time pressure.
2. Write the script first; AI-generated scripts often miss key technical details.
3. Allocate time explicitly: elevator pitch (0:00–0:20), problem (0:20–0:40), demo (0:40–2:30), impact close (2:30–3:00).
4. Use tools you already know — OBS Studio for recording, no new learning overhead.
5. Keep it clear and concise — do not speed up audio to fit content.
6. Verify audio quality, resolution (1920×1080 minimum), and platform accessibility before submission.

The 90-second judge attention window is not a hard limit for this hackathon (the recording should run 3–4 minutes to cover all features), but the *opening 90 seconds must hook the judge* with the problem + the autonomy proof moment (the proactive alert firing at 90s into the sensor playback is exactly this).

---

## 3. Exact Stack

| Tool/Library | Version | Role in Judging Optimization |
|---|---|---|
| OBS Studio | 30.x (latest) | Screen recording at 1920×1080 30fps H.264 MP4 — industry standard, no artifacts |
| Kapwing or DaVinci Resolve | Current free tier | Adding captions, text overlays, trimming — improves Axis E score |
| ffmpeg | 6.x | Compress final video to <80MB without quality loss |
| YouTube (unlisted) | — | Reliable judge access — no download required, no platform friction |
| Mermaid (via LangGraph draw_mermaid()) | LangGraph 0.2.x | Auto-generates system architecture diagram from the actual graph — not a hand-drawn fake |
| Markdown | — | Architecture document format — renders in GitHub, readable as plain text, diffable |
| pytest + Rich | pytest 8.x + Rich 13.x | Generates `regression_report.md` from golden eval — a concrete accuracy proof for the document |
| httpx (sync) | 0.27 | Demo mode cache — ensures <1s responses during recording via `data/demo_cache.json` |
| Streamlit st.status + st.toast | Streamlit 1.35 | Visual proof that agent routing is happening (judges see "Routing to agents..." text) |
| LangSmith | Current | [NICE-TO-HAVE, unverified latency overhead] Agent trace visualization — useful if judges want to inspect traces beyond the in-UI expander |

---

## 4. Alternatives Considered and Why They Lose

### Alternative A: Maximum Feature Count Strategy
Build as many features as possible and let judges discover them. Used by teams that confuse "impressive to build" with "impressive to judge."

**Why it loses:** The Microsoft AI Agents Hackathon 2025 finding: "The most technically impressive solution lost to the one with the most intuitive interface." More features create more surface area for crashes during the demo. In a solo 9-day build, every unscripted feature is a latent demo risk. This hackathon scores SMOOTH and DOESN'T-BREAK as explicit axes — a feature-dense demo that crashes loses both.

### Alternative B: Slide-Deck-First Strategy
Spend significant time on a polished Canva/PowerPoint presentation and treat the code as secondary.

**Why it loses:** Multiple hackathons in 2025–2026 explicitly disqualify slide-only submissions. More importantly, Tata Steel's deliverable list is code + document + screen recording. The judges are Tata Steel's own AI leadership team — they can read code. A beautiful deck with shallow code is immediately detectable. The docstring "This feels like a product" (GitLab 2026) comes from the code, not from the slides.

### Alternative C: Complexity-First Strategy (Full GraphRAG + Custom Fine-Tuning)
Maximize technical impressiveness by fine-tuning a domain-specific SLM and using GraphRAG instead of hybrid RAG.

**Why it loses:** Domain fine-tuning requires real steel-plant data (unavailable) or synthetic data (which defeats the "domain-specific" claim). GraphRAG adds significant build complexity without a proportional judging gain — the problem statement says "extra merit for fine-tuning" but judges cannot validate fine-tuning quality without a benchmark comparison, which a solo 9-day build cannot produce. The net result is lower robustness (more to break) without a verifiable accuracy uplift. Hybrid RAG with citation pills satisfies Requirement 4 and Axis C adequately.

### Alternative D: Real-Time Production Architecture (Kafka + Redis + Docker Compose)
Build a production-grade distributed system with real-time streaming infrastructure.

**Why it loses:** The problem statement explicitly says the system must run on a judge's machine (prefer pip install over docker-compose). Docker Compose introduces setup friction that guarantees at least some judges will not run the system at all — forcing them to rely only on the video. The asyncio + SSE + Streamlit autorefresh architecture achieves the "real-time alerting" visual effect without the deployment complexity.

---

## 5. Anti-Patterns — What Screams Amateur or 2022-Tier

1. **Raw tracebacks in the UI.** A Python `AttributeError` visible in the Streamlit UI during the screen recording is an automatic score penalty on axes K (DOESN'T-BREAK) and L (NO-ERRORS). The global FastAPI exception handler returning `AgentResult(status='error', message='...')` is non-negotiable.

2. **"Chat with PDF" as the primary feature.** Simple RAG-over-PDF was novel in 2023. In 2026, every entry will do RAG. The differentiator is the *agentic* layer — proactive alerting without user input, autonomous maintenance plan generation, multi-turn memory with persistent session state. If the demo only shows question-answer cycles, the system is not agentic.

3. **Un-cited LLM answers.** "Based on my analysis..." with no source reference is a Requirement 4 violation. Judges evaluating explainability will penalize any answer not traceable to a document or a rule. Citation pills (inline `[SOURCE-1]` references with expandable excerpts) are the minimum bar.

4. **Demo that requires judge expertise.** If the judge needs to understand sensor data engineering to appreciate the anomaly detection, the demo is failing Axis D (Easy to use). The "Simulate Fault" button and the pre-seeded EAF-04 CRITICAL alert exist specifically to make the wow moment accessible to a non-technical observer.

5. **Architecture document written on Day 8.** A document written under deadline pressure reads like a technical README — implementation details without the business story. The architecture document written in stubs on Day 1 and updated incrementally through the build contains the problem framing, the design rationale, and the business impact that comes from living with the problem for 8 days. Judges can tell the difference.

6. **Missing the "agentic" proof.** Using LangChain for RAG chaining while calling it "agentic" is detectable. Tata Steel's judging language is explicit: "intelligent agents capable of understanding objectives, making decisions, and adapting to dynamic environments." The proactive planner firing without user input is the clearest proof. If this moment is missing from the demo, Axis B (Effective use of Agentic AI frameworks) is at serious risk.

7. **Generic problem framing.** Opening the demo with "maintenance is important for factories" instead of "Tata Steel operates 35 million TPA across four countries; their own AI team documented 22% downtime reduction through predictive maintenance" signals that the candidate did not research the company. Judges are Tata Steel AI leadership — they know the numbers.

8. **No feedback loop visible in the demo.** Requirement 6 is explicit: feedback-driven improvement. If the demo does not show an engineer correction followed by a visible change in the next response, this requirement is unmet. The correction → RAG re-rank → corrected answer in one turn is the demo moment for Requirement 6, and it must be in the screen recording.

9. **Video with no captions or voiceover.** Screen recordings with only mouse clicks and no narration are opaque to judges who are reviewing 109 submissions. Captions or voiceover are mandatory for Axis E.

10. **Secret keys committed to the ZIP.** A real API key in any file inside the submission ZIP is an instant disqualification risk and a security red flag. The mandatory pre-ZIP `grep -r 'sk-ant-api'` prevents this.

---

## 6. Integration Notes

**Inputs consumed from other components:**
- Component 1 (Agentic Orchestration / LangGraph): the `graph.get_graph().draw_mermaid()` output populates the Architecture document diagram.
- Component 6 (Explainability): citation pills, agent trace expander, and confidence badges are the visual proof for Axis I (ACCURATE) and Axis C (Technical Implementation).
- Component 17 (Backend Architecture): the `GET /health` endpoint output is shown in the Streamlit sidebar health dot — live proof for judges that the system is running correctly.
- Component 18 (Frontend/UX): the five Streamlit pages are the primary judge-facing surface; their layout and error handling directly determine Axis J (EASY-TO-USE), K, L, M scores.
- Component 20 (Feedback Loop): the feedback widget + correction → re-rank → corrected answer chain is the demo moment for Requirement 6.
- Component 22 (Real-time Alerting): the proactive CRITICAL alert toast at 90s is the demo moment for Axis B (Effective use of Agentic AI frameworks) — the single highest-impact moment in the recording.
- Component 7/8 (Embeddings/RUL): the regression_report.md from the golden eval suite is the concrete accuracy proof included in the architecture document.

**Outputs produced:**
- `docs/ARCHITECTURE.md` — 8-section document consumed by judges directly; primary written artifact.
- `docs/BUSINESS_IMPACT.md` — feeds Axis A and F scores; anchored to Tata Steel published KPIs.
- `docs/KNOWN_FAILURE_MODES.md` — demonstrates honest scoping; improves credibility on Axis A and D.
- `docs/SAMPLE_IO.md` — 3 complete query-response pairs with citation JSON; required ZIP artifact.
- `docs/JUDGE_MATRIX.md` — internal build control document; not submitted but drives Day 1–9 decisions.
- `demo/HAPPY_PATH.md` — internal script; determines screen recording structure.
- `data/demo_cache.json` — pre-computed responses ensuring sub-1s demo latency during recording.
- Screen recording (MP4, 1920×1080, 3–4 min, YouTube unlisted) — primary judge-facing video artifact.
- `README.md` — 5-command install sequence; YouTube link; requirements mapping table.

**Components it talks to:**
This component does not add runtime logic. It is a meta-layer that governs what every other component must visibly prove during the demo. The JUDGE_MATRIX.md creates hard coupling: if Component 22 (Alerting) is late, the proactive demo moment for Axis B is at risk — the matrix makes this visible on Day 1, not Day 8.

---

## 7. Open Risks / Unknowns

**Risk 1 — Judging weight distribution is unknown.**
The 6 email criteria and 7 webinar axes are listed without weights. It is unknown whether all 13 axes are equally weighted or whether some (e.g., Technical Implementation) carry more points. Mitigation: treat all 13 as equally weighted; the JUDGE_MATRIX ensures at least one strong demo moment per axis regardless.

**Risk 2 — Judges may not run the code.**
With 109 submissions and likely limited review time, some judges may evaluate only the video and the document, not the runnable system. Mitigation: the screen recording must be self-sufficient — every claimed feature must be visibly demonstrated in the video, not just described. Pre-seeding the database and using `demo_cache.json` ensures the recording is reliable.

**Risk 3 — "Extra merit for domain-specific fine-tuning" is an unknown multiplier.**
The problem statement offers extra merit for creating or fine-tuning a domain-specific model. It is unverified whether this creates a significant scoring gap or is a minor bonus. Mitigation: the hybrid RAG with citation grounding satisfies Requirement 1 without fine-tuning. If time remains after Day 7, a LoRA adapter on a small open-source model (e.g., Phi-3-mini) trained on the synthetic corpus could be demonstrated — but only if the primary system is fully stable. [unverified: whether fine-tuning on synthetic data is considered valid for "extra merit"]

**Risk 4 — Screen recording technical failure.**
OBS Studio has known issues with screen capture on some GPU configurations. Mitigation: run a 30-second test recording on Day 7 and verify output before the full demo recording session. Have a browser-based alternative (Loom) as fallback.

**Risk 5 — YouTube upload latency before deadline.**
YouTube processing time for a 1920×1080 H.264 MP4 video typically takes 10–30 minutes at standard quality. For 4K or large files, processing can take hours. Mitigation: upload the video at least 6 hours before the June 15 23:59 IST deadline. Keep an MP4 backup to include directly in the ZIP if YouTube processing fails.

**Risk 6 — Judge machine Python version mismatch.** [unverified]
The `.python-version` file pins to Python 3.12. Some judge machines may have only 3.10 or 3.11. Mitigation: test that all dependencies install cleanly on 3.10; pin pyproject.toml `python_requires=">=3.10"` if any 3.12-specific syntax is absent from the codebase.
