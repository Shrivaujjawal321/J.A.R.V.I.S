# Phase 3.4 — User-Sim Runner Playbook

Jarvis's runbook for executing the 10-persona stress test when a project's dev server is live. Reusable across all 10 decathlon projects.

---

## Trigger

When a project hits this state:
- Phase 3.3 integration verdict = PASS
- Local dev server running at known URL (default `http://localhost:3000`)
- Corpus ingested (vector DB populated)
- Eval golden-set in place

Boss confirms server is up → Jarvis runs this playbook.

---

## One-message dispatch

Send all 10 persona agents in a SINGLE message with 10 parallel Agent tool blocks. Each gets:

1. The persona profile (verbatim from `_shared/USER_SIMULATOR_PERSONAS.md` for their persona number)
2. Target URL
3. Per-project context (1-paragraph product description from ROADMAP.md)
4. Output file path: `data/projects/rag-decathlon/projects/Pn-<slug>/user-sims/persona-NN.json`
5. Severity rubric (P0/P1/P2/P3) from PERSONAS file
6. Number of sessions: 5-10 per persona
7. Strict JSON output schema

All run in BACKGROUND. Notifications when complete.

---

## Persona dispatch template

```
You are User Simulator Persona #<N>: <Persona Name from PERSONAS.md>.

PROFILE: <paste exact profile lines from _shared/USER_SIMULATOR_PERSONAS.md persona N>

TARGET PRODUCT: <slug> at <URL>
PRODUCT CONTEXT: <1 paragraph from project's ROADMAP card>

MISSION:
1. Run 5-10 sessions consistent with your persona.
2. Each session: form a query → submit → observe full response (answer + citations + UI state) → critique.
3. Verify ≥1 citation per session by actually following the source URL where applicable.
4. Capture any bug (P0/P1/P2/P3) and any UX critique.

SEVERITY RUBRIC:
- P0: product breaks, hallucinated citation, safety violation (diagnosis/dose), exposed secret, infinite loop
- P1: user can't accomplish goal, broken citation link, missing safety disclaimer, accessibility blocker
- P2: UX friction, slow streaming, confusing copy, layout shift
- P3: polish

OUTPUT JSON (write to <output-path>):
{
  "persona": "<Name>",
  "persona_number": <N>,
  "target_url": "<URL>",
  "session_count": <K>,
  "sessions": [
    {
      "session_id": 1,
      "query": "<exact query typed>",
      "response_excerpt": "<first 200 chars of answer>",
      "citations_observed": <count>,
      "citations_verified": <count of links you actually opened>,
      "ttft_ms_observed": <if measurable, else null>,
      "bug": null | {"severity": "P0|P1|P2|P3", "description": "..."},
      "ux_critique": "<one-line opinion>",
      "trust_verdict": "trust | mistrust | unclear"
    },
    ...
  ],
  "summary": {
    "total_bugs_p0": N,
    "total_bugs_p1": N,
    "total_bugs_p2": N,
    "total_bugs_p3": N,
    "would_recommend": true|false,
    "headline_finding": "<single most important observation>"
  }
}

HARD RULES:
- DO NOT fabricate bugs — only what you observed
- DO actually open citation links (your persona's behavior should drive this)
- DO use a tool/browser to interact with the URL if available, else describe what you'd do
- Return the file path + a 3-line summary in your final message
```

---

## Aggregation step (Jarvis-side, after all 10 return)

When all 10 persona JSONs are in:

```
WRITE: data/projects/rag-decathlon/projects/Pn-<slug>/user-sims/AGGREGATE.md

Structure:
- Per-persona summary table (persona | P0 | P1 | P2 | trust)
- Combined bug list (deduplicated, severity-sorted)
- Cross-persona patterns (e.g., "3/10 personas complained about TTFT > 5s")
- Trust verdict count (X/10 trust | Y/10 mistrust | Z/10 unclear)
- Recommendation: PASS to 3.6 | back to 3.5 (loop with builders)
```

---

## Loop exit criteria (Phase 3.5)

Loop exits ONLY when:
- 0 P0 bugs across all 10 personas
- 0 P1 bugs across all 10 personas
- ≥ 7/10 personas return `trust` verdict
- Eval suite (Ragas) still passing per project's threshold

If after 5 iterations any criterion still failing → escalate to Jarvis architecture review.

---

## Cost estimate per Phase 3.4 run

- 10 persona agents × ~$0.15-0.25 each (Sonnet 4.6 with ~5-10 sessions of LLM-driven product interaction)
- ~$2 per full sweep
- ~$10-15 across all 10 projects total
- Within budget ($8/project allows for 3-4 sweeps)

---

## Tooling note

If browser-autopilot skill is available in the spawned persona agents, they can use Chrome DevTools MCP to actually exercise the product. Otherwise they critique based on API-level inspection (call the `/api/chat` endpoint directly).

Default mode: API-level + manual UI critique via screenshots if the agent has browser access. Per-project we may switch to full browser-autopilot for richer mobile + a11y testing.
