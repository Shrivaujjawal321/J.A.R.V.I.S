# Tata Steel AI Hackathon 2026 — Round 2 Intel

**Source:** Boss attended the Round 2 webinar (Tata Steel AI Leadership team, 4 June 2026, Cisco WebEx).
**Captured:** 2026-06-05.

## What Round 2 IS

> **Build an AGENTIC SYSTEM.** (per webinar — official problem statement still pending release.)

This confirms Round 2 is an agentic-AI build challenge, not another tabular-ML scoring round like R1.

## Judging Criteria (verbatim intent from webinar)

Winners will be selected on how well the agentic system delivers on these qualities. Judges will keep ALL of these in mind:

1. **Fast output** — low latency, quick responses.
2. **Efficient** — resource/compute efficient, not wasteful.
3. **Accurate** — correct, reliable answers/actions.
4. **Easy to use** — good UX, intuitive interface.
5. **Doesn't break** — robust, stable; no crashes.
6. **No errors while working** — graceful operation, error-free execution.
7. **Smooth working** — seamless end-to-end flow.

**One-line summary:** A fast, efficient, accurate, easy-to-use agentic system that runs smoothly without breaking or erroring.

## Implications for our build (Jarvis planning)

- **Latency is a scored axis** → prompt caching, streaming, parallel agent dispatch, small-model routing for cheap sub-tasks.
- **Efficiency scored** → token/compute budget discipline; don't over-call the LLM.
- **Accuracy scored** → grounding, verification/critic pass, eval suite before demo.
- **Easy to use scored** → clean UI; demo-able flow; non-technical judge can drive it.
- **Robustness/no-break/no-error scored** → error envelopes, retries, fallbacks, input validation, no unhandled exceptions in the demo path.
- **Smoothness** → rehearsed, deterministic happy-path demo.

## STILL UNKNOWN (waiting on official drop)

- Exact problem statement / domain (steel-plant ops? defect? maintenance? operator copilot?)
- Submission format + deadline
- Tech constraints / mandatory SDKs
- Round 2 release date/time (watch active on Gmail + HackerEarth)

## Our edge

Jarvis itself is a production multi-agent orchestrator — we have battle-tested patterns (parallel fan-out, recall, critic, intent classifier, tiered trust). The 5 Tata-domain subagents already exist (defect-detector, predictive-maintenance, process-optimizer, incident-rca, operations-orchestrator). Strong head start on an agentic build.
