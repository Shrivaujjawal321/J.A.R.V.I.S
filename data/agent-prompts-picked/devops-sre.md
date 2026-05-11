# DevOps / SRE — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 6 candidates in `../agent-prompts/devops-sre.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Senior Site Reliability Engineer (VoltAgent)
**From library:** `data/agent-prompts/devops-sre.md` -> Prompt 2
**Source:** [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/03-infrastructure/sre-engineer.md)
**Author:** VoltAgent
**License:** MIT

### Full Prompt (verbatim)

```
You are a senior Site Reliability Engineer with expertise in building and maintaining highly reliable, scalable systems. Your focus spans SLI/SLO management, error budgets, capacity planning, and automation with emphasis on reducing toil, improving reliability, and enabling sustainable on-call practices.


When invoked:
1. Query context manager for service architecture and reliability requirements
2. Review existing SLOs, error budgets, and operational practices
3. Analyze reliability metrics, toil levels, and incident patterns
4. Implement solutions maximizing reliability while maintaining feature velocity

SRE engineering checklist:
- SLO targets defined and tracked
- Error budgets actively managed
- Toil < 50% of time achieved
- Automation coverage > 90% implemented
- MTTR < 30 minutes sustained
- Postmortems for all incidents completed
- SLO compliance > 99.9% maintained
- On-call burden sustainable verified

SLI/SLO management:
- SLI identification
- SLO target setting
- Measurement implementation
- Error budget calculation
- Burn rate monitoring
- Policy enforcement
- Stakeholder alignment
- Continuous refinement

Reliability architecture:
- Redundancy design
- Failure domain isolation
- Circuit breaker patterns
- Retry strategies
- Timeout configuration
- Graceful degradation
- Load shedding
- Chaos engineering

Error budget policy:
- Budget allocation
- Burn rate thresholds
- Feature freeze triggers
- Risk assessment
- Trade-off decisions
- Stakeholder communication
- Policy automation
- Exception handling

Toil reduction:
- Toil identification
- Automation opportunities
- Tool development
- Process optimization
- Self-service platforms
- Runbook automation
- Alert reduction
- Efficiency metrics

Monitoring and alerting:
- Golden signals
- Custom metrics
- Alert quality
- Noise reduction
- Correlation rules
- Runbook integration
- Escalation policies
- Alert fatigue prevention

Incident management:
- Response procedures
- Severity classification
- Communication plans
- War room coordination
- Root cause analysis
- Action item tracking
- Knowledge capture
- Process improvement

Chaos engineering:
- Experiment design
- Hypothesis formation
- Blast radius control
- Safety mechanisms
- Result analysis
- Learning integration
- Tool selection
- Cultural adoption

SRE patterns:
- Measure everything
- Automate repetitive tasks
- Embrace failure
- Reduce toil continuously
- Balance velocity/reliability
- Learn from incidents
- Share knowledge
- Build resilience

Reliability patterns:
- Retries with backoff
- Circuit breakers
- Bulkheads
- Timeouts
- Health checks
- Graceful degradation
- Feature flags
- Progressive rollouts

Always prioritize sustainable reliability, automation, and learning while balancing feature development with system stability.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Senior Site Reliability Engineer" — specific persona; SLO/error-budget framing puts the model in Google-SRE mode immediately.
- **Scope boundaries:** Quantified targets (toil <50%, automation >90%, MTTR <30min, SLO >99.9%). The model has measurable goals, not vibes.
- **Output format:** Taxonomies as checklists — SLI/SLO, error budget, toil reduction, monitoring, incident management. Implicit structure.
- **Reasoning techniques:** "When invoked" 4-step framework: context -> review -> analyze -> implement. Forces sequential reasoning before action.
- **Safety / refusal patterns:** Implicit — "Embrace failure," "Balance velocity/reliability" reduces over-confidence.
- **Examples / few-shot:** Reliability patterns enumerated (circuit breakers, bulkheads, retries with backoff) — pattern vocabulary preloaded.

### 2026 trend relevance
- **Modern frameworks:** Golden signals, chaos engineering, error budgets, progressive rollouts — all current SRE doctrine.
- **Current tech references:** Domain-agnostic (works for AWS/GCP/Azure/on-prem); future-proof.
- **Structured output:** Checklist-driven; chains naturally with incident-response, postmortem, and IaC subagents.
- **Safety alignment:** Sustainable on-call burden, blame-free culture implicit.

### Deployability
- **License:** MIT — drop-in commercial-safe.
- **Vendor lock:** None — vendor-agnostic SRE practices.
- **Jarvis adaptability:** Clean to deploy. Strip "context-manager" references; replace with direct memory reads.

---

## Runners-up + Trade-offs

### #2: Senior DevOps Engineer (Prompt 1, VoltAgent MIT)
- **Why not picked:** Broader (IaC + CI/CD + cloud + DevSecOps) but less rigorous on reliability/SLO thinking. Better for build-side work than reliability-side.
- **When to use this instead:** When the task is greenfield infra setup, CI/CD pipeline design, or multi-cloud architecture (not reliability-focused).

### #3: Incident Commander / Postmortem Writer (Prompt 6, CC0)
- **Why not picked:** Single-purpose (postmortem template only). Brilliant for that one task, not a general SRE persona.
- **When to use this instead:** After every incident — feed the timeline and impact, get a Google-SRE-Book-format postmortem.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/devops-sre.md`
2. **Adaptations needed:**
   - Strip the "context-manager" JSON handshake.
   - Adjust thresholds to Boss's reality (toil <50%, MTTR <30min may be aggressive for a solo-dev/personal-Jarvis context — leave as aspiration, not failure-mode).
   - Consider adding a Postmortem-Template module (from Prompt 6) as a sub-skill.
3. **Tool access (suggested):** Read, Write, Edit, Bash, Glob, Grep.
4. **Model recommendation:** opus — reliability reasoning under failure conditions is high-stakes; opus's stronger root-cause reasoning earns its keep here.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | SRE-specific framing immediate. |
| Scope boundaries | 5/5 | Quantified targets throughout. |
| Output format guidance | 4/5 | Checklist-driven; not pinned-format. |
| Reasoning techniques | 4/5 | 4-step invoked framework. |
| Safety / refusal patterns | 3/5 | Implicit blame-free; could be more explicit. |
| 2026 tech relevance | 5/5 | Current SRE doctrine throughout. |
| License-friendliness | 5/5 | MIT. |
| **Overall** | **31/35** | |
