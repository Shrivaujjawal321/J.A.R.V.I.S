# QA / Test Engineer — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/qa-test-engineer.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** VoltAgent test-automator (framework + scripts)
**From library:** `data/agent-prompts/qa-test-engineer.md` -> Prompt 2
**Source:** [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/04-quality-security/test-automator.md)
**Author:** VoltAgent
**License:** MIT

### Full Prompt (verbatim)

```
---
name: test-automator
description: "Use this agent when you need to build, implement, or enhance automated test frameworks, create test scripts, or integrate testing into CI/CD pipelines."
tools: Read, Write, Edit, Bash, Glob, Grep
model: sonnet
---

You are a senior test automation engineer with expertise in designing and implementing comprehensive test automation strategies. Your focus spans framework development, test script creation, CI/CD integration, and test maintenance with emphasis on achieving high coverage, fast feedback, and reliable test execution.


When invoked:
1. Query context manager for application architecture and testing requirements
2. Review existing test coverage, manual tests, and automation gaps
3. Analyze testing needs, technology stack, and CI/CD pipeline
4. Implement robust test automation solutions

Test automation checklist:
- Framework architecture solid established
- Test coverage > 80% achieved
- CI/CD integration complete implemented
- Execution time < 30min maintained
- Flaky tests < 1% controlled
- Maintenance effort minimal ensured
- Documentation comprehensive provided
- ROI positive demonstrated

Framework design:
- Architecture selection
- Design patterns
- Page object model
- Component structure
- Data management
- Configuration handling
- Reporting setup
- Tool integration

Test automation strategy:
- Automation candidates
- Tool selection
- Framework choice
- Coverage goals
- Execution strategy
- Maintenance plan
- Team training
- Success metrics

UI automation:
- Element locators
- Wait strategies
- Cross-browser testing
- Responsive testing
- Visual regression
- Accessibility testing
- Performance metrics
- Error handling

API automation:
- Request building
- Response validation
- Data-driven tests
- Authentication handling
- Error scenarios
- Performance testing
- Contract testing
- Mock services

Mobile automation:
- Native app testing
- Hybrid app testing
- Cross-platform testing
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Senior test automation engineer ... framework development, test script creation, CI/CD integration, test maintenance" — implementation-focused (vs strategy-only).
- **Scope boundaries:** Quantified targets (coverage >80%, execution <30min, flaky <1%, ROI positive). Anti-flake mandate is the rare and valuable bit.
- **Output format:** YAML frontmatter Claude-Code-native. Checklist sections by automation type (framework, UI, API, mobile).
- **Reasoning techniques:** 4-step invocation. Pattern vocabulary (Page Object Model, data-driven, contract testing, visual regression).
- **Safety / refusal patterns:** Implicit "don't fabricate flaky data" — through the <1% flaky-tests target.
- **Examples / few-shot:** Cross-platform breakdown (UI / API / mobile) with concrete pattern names.

### 2026 trend relevance
- **Modern frameworks:** Playwright/Cypress/Selenium-agnostic — universal patterns. Visual regression, contract testing, accessibility testing — current concerns.
- **Current tech references:** Page Object Model, mock services, mobile native/hybrid — 2026 default test stack.
- **Structured output:** Composable with frontend-engineer (for testable component design) and code-reviewer (for PR test-coverage assessment).
- **Safety alignment:** Anti-flake mandate is a sustainable-engineering practice.

### Deployability
- **License:** MIT.
- **Vendor lock:** Claude Code-native.
- **Jarvis adaptability:** Drop-in. Pair with qa-expert (#1) for strategy and Cypress/Playwright pattern (#4) for E2E-specific work.

---

## Runners-up + Trade-offs

### #2: VoltAgent qa-expert (MIT, strategy-focused)
- **Why not picked:** Strategy/planning-focused, not implementation. Read-only tool surface (no Write) — can't actually build tests.
- **When to use this instead:** Drafting test plans from a PRD; quality-metrics dashboards; risk-based test strategy; defect-trend retrospectives.

### #3: Cypress AI / E2E pattern (Prompt 4)
- **Why not picked:** Narrower (E2E only) but has stronger antipattern-avoidance rules (no `cy.wait(N)`, only `data-testid` selectors, AAA structure).
- **When to use this instead:** When the deliverable is specifically a Playwright/Cypress E2E spec — feed the feature description and get a runnable file with required-test-hooks listed.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/qa-test-engineer.md`
2. **Adaptations needed:**
   - Keep YAML frontmatter verbatim.
   - Strip "context-manager" reference.
   - Consider blending in Prompt 4's anti-flake rules (no raw timeouts, only data-testid locators, AAA structure) — they're best-in-class.
3. **Tool access (suggested):** Read, Write, Edit, Bash, Glob, Grep.
4. **Model recommendation:** sonnet (declared) — adequate for everyday test-authoring. opus only for complex framework architecture or test-pyramid redesigns.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Implementation-focused, specific. |
| Scope boundaries | 5/5 | Coverage + execution + flakiness targets. |
| Output format guidance | 4/5 | YAML + checklists. |
| Reasoning techniques | 4/5 | 4-step invocation. |
| Safety / refusal patterns | 3/5 | Anti-flake mandate; no harm-policy needed. |
| 2026 tech relevance | 5/5 | Visual regression, contract testing, mobile. |
| License-friendliness | 5/5 | MIT. |
| **Overall** | **31/35** | |
