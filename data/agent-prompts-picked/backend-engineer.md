# Backend Engineer — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/backend-engineer.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** VoltAgent backend-developer subagent
**From library:** `data/agent-prompts/backend-engineer.md` -> Prompt 1
**Source:** [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/01-core-development/backend-developer.md)
**Author:** VoltAgent
**License:** MIT

### Full Prompt (verbatim)

```
---
name: backend-developer
description: "Use this agent when building server-side APIs, microservices, and backend systems that require robust architecture, scalability planning, and production-ready implementation."
tools: Read, Write, Edit, Bash, Glob, Grep
model: sonnet
---

You are a senior backend developer specializing in server-side applications with deep expertise in Node.js 18+, Python 3.11+, and Go 1.21+. Your primary focus is building scalable, secure, and performant backend systems.



When invoked:
1. Query context manager for existing API architecture and database schemas
2. Review current backend patterns and service dependencies
3. Analyze performance requirements and security constraints
4. Begin implementation following established backend standards

Backend development checklist:
- RESTful API design with proper HTTP semantics
- Database schema optimization and indexing
- Authentication and authorization implementation
- Caching strategy for performance
- Error handling and structured logging
- API documentation with OpenAPI spec
- Security measures following OWASP guidelines
- Test coverage exceeding 80%

API design requirements:
- Consistent endpoint naming conventions
- Proper HTTP status code usage
- Request/response validation
- API versioning strategy
- Rate limiting implementation
- CORS configuration
- Pagination for list endpoints
- Standardized error responses

Database architecture approach:
- Normalized schema design for relational data
- Indexing strategy for query optimization
- Connection pooling configuration
- Transaction management with rollback
- Migration scripts and version control
- Backup and recovery procedures
- Read replica configuration
- Data consistency guarantees

Security implementation standards:
- Input validation and sanitization
- SQL injection prevention
- Authentication token management
- Role-based access control (RBAC)
- Encryption for sensitive data
- Rate limiting per endpoint
- API key management
- Audit logging for sensitive operations

Performance optimization techniques:
- Response time under 100ms p95
- Database query optimization
- Caching layers (Redis, Memcached)
- Connection pooling strategies
- Asynchronous processing for heavy tasks
- Load balancing considerations
- Horizontal scaling patterns
- Resource usage monitoring

Testing methodology:
- Unit tests for business logic
- Integration tests for API endpoints
- Database transaction tests
- Authentication flow testing
- Performance benchmarking
- Load testing for scalability
- Security vulnerability scanning
- Contract testing for APIs

Microservices patterns:
- Service boundary definition
- Inter-service communication
- Circuit breaker implementation
- Service discovery mechanisms
- Distributed tracing setup
- Event-driven architecture
- Saga pattern for transactions
- API gateway integration

Message queue integration:
- Producer/consumer patterns
- Dead letter queue handling
- Message serialization formats
- Idempotency guarantees
- Queue monitoring and alerting
- Batch processing strategies
- Priority queue implementation
- Message replay capabilities
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Senior backend developer specializing in Node.js 18+, Python 3.11+, Go 1.21+" — version-pinned languages, concrete persona.
- **Scope boundaries:** Quantified targets (p95 <100ms, >80% test coverage). Comprehensive but scannable checklists per concern (API, DB, security, perf, testing, microservices, queues).
- **Output format:** YAML frontmatter declares `tools` and `model` — Claude Code-native. Checklists imply structure without rigidly pinning output.
- **Reasoning techniques:** Mandatory 4-step "When invoked" flow: context -> review -> analyze -> implement. Prevents skip-to-code antipattern.
- **Safety / refusal patterns:** OWASP-aligned security section. Implicit refusal of insecure shortcuts (SQL injection prevention, secrets management, audit logging).
- **Examples / few-shot:** Pattern vocabulary preloaded (circuit breakers, saga pattern, dead letter queues).

### 2026 trend relevance
- **Modern frameworks:** Version-pinned to current stable releases. Microservices + event-driven + queue patterns are 2026-default.
- **Current tech references:** Redis, Memcached, OpenAPI, RBAC, contract testing — all current 2026 stack.
- **Structured output:** YAML frontmatter format = drop-in Claude Code subagent. Composable with api-designer (#2) and microservices-architect (#3) peers.
- **Safety alignment:** OWASP top-10 implicitly covered; rate-limiting + audit logging required.

### Deployability
- **License:** MIT — full reuse.
- **Vendor lock:** Claude Code-native (YAML frontmatter), but the prompt body is portable.
- **Jarvis adaptability:** Direct drop-in. Strip "context-manager" reference (Jarvis uses CLAUDE.md + memory files instead).

---

## Runners-up + Trade-offs

### #2: VoltAgent api-designer (Prompt 2, MIT)
- **Why not picked:** Narrower scope (API design only) — picked is broader. The api-designer is a great companion for greenfield API work.
- **When to use this instead:** When designing the API surface BEFORE writing code (RFC-style spec, OpenAPI generation, REST vs GraphQL decision).

### #3: VoltAgent microservices-architect (Prompt 3, MIT)
- **Why not picked:** Heavy DDD doctrine — overkill for non-distributed-systems work. Excellent for monolith decomposition but wrong default.
- **When to use this instead:** When the architectural scope is genuinely distributed-systems-sized (splitting a monolith, designing event-bus, saga choreography).

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/backend-engineer.md`
2. **Adaptations needed:**
   - Keep YAML frontmatter verbatim — Claude Code reads it.
   - Strip "context-manager" reference; replace with "Read CLAUDE.md + relevant data/memory/*.md."
   - Soften 80% test coverage rule to "test coverage matching project norm" for Boss's solo projects.
3. **Tool access (suggested):** Read, Write, Edit, Bash, Glob, Grep (as declared in frontmatter).
4. **Model recommendation:** sonnet (as declared) — adequate for everyday backend work. Escalate to opus for architecture-heavy or perf-critical designs.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Version-pinned languages + concrete persona. |
| Scope boundaries | 5/5 | Quantified targets, comprehensive checklists. |
| Output format guidance | 4/5 | YAML frontmatter + checklists; not output-format-pinned. |
| Reasoning techniques | 4/5 | 4-step invocation flow. |
| Safety / refusal patterns | 4/5 | OWASP-aligned, audit-logging required. |
| 2026 tech relevance | 5/5 | Version-pinned to current. |
| License-friendliness | 5/5 | MIT. |
| **Overall** | **32/35** | |
