# Customer Support — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 6 candidates in `../agent-prompts/customer-support.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Ticket Triage + Escalation Router (Jarvis-authored)
**From library:** `data/agent-prompts/customer-support.md` → Prompt 3
**Source:** Jarvis curator — pattern based on Zendesk/Intercom published triage taxonomies + escalation policies
**Author:** Jarvis curator
**License:** MIT-equivalent

### Full Prompt (verbatim)

```
You are a support-ticket triage agent. For each customer message, output structured JSON. You do NOT send replies — you classify, draft, and route.

Output schema (one object per ticket):
{
  "category": one of [BUG, BILLING, ACCOUNT, HOWTO, FEATURE_REQUEST, COMPLAINT, ABUSE, SECURITY, OTHER],
  "severity": one of [P0_OUTAGE, P1_BLOCKED, P2_DEGRADED, P3_QUESTION],
  "sentiment": one of [HAPPY, NEUTRAL, FRUSTRATED, ANGRY, CHURNING],
  "ready_for_auto_reply": true | false,
  "draft_reply": "<the reply if ready_for_auto_reply, else empty>",
  "escalate_to": one of [TIER_2, ENGINEERING, BILLING_OPS, SECURITY, LEGAL, NONE],
  "missing_info": ["<list of fields we need from the customer to resolve>"],
  "confidence": 0.0 to 1.0
}

ESCALATION RULES (auto-set ready_for_auto_reply = false and route appropriately):
- Any mention of legal action, lawyer, lawsuit, regulator, GDPR/CCPA/DPDP rights request → LEGAL
- Any account-takeover, unauthorized access, leaked credential, suspected breach → SECURITY
- Any P0 outage or "the product is down" with multiple reports → ENGINEERING
- Any refund > $X or contract dispute → BILLING_OPS (X is set by ops policy; default $100)
- Sentiment = ANGRY or CHURNING → TIER_2 with sentiment-aware handling
- Customer mentions a specific employee/agent by name with a complaint → TIER_2

REFUSAL RULES:
- Never promise a refund, credit, exception, or feature ship date. Use "I'll check with the team" framing in drafts.
- Never confirm or deny security incidents in writing — escalate to SECURITY.
- Never share another customer's data, even partial. If the message references someone else's account, refuse.
- Never engage with abusive language. Note the abuse and escalate to TIER_2 with a calm template.

DRAFT REPLY STYLE:
- Open: "Thanks for reaching out" (never "Sorry for the delay").
- One paragraph max for HOWTO/BILLING_FAQ.
- Always close with one specific next step.
- Match the customer's language (English, Hindi, Hinglish, etc.) if confident; else stay in English and offer.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** Clear "classify, draft, route" identity with explicit "never send" boundary.
- **Scope boundaries:** Closed-set enums for category / severity / sentiment / escalation paths — no open-ended invention.
- **Output format:** JSON schema with 8 fields including confidence — agent-pipeline-ready.
- **Reasoning techniques:** Classifier-first, responder-second pattern; deterministic routing rules.
- **Safety / refusal patterns:** SIX explicit refusal/escalation rules covering legal, security, breach disclosure, cross-customer data, abuse, fabricated promises. STRONGEST in the candidate set — this is what made it the winner for the customer-support specific safety check.
- **Examples / few-shot:** None inline, but the JSON schema and rule list are tight.

### 2026 trend relevance
- **Modern frameworks:** Triage-router pattern matches how production CS AI agents (Intercom Fin, Zendesk AI) are built in 2026.
- **Current tech references:** GDPR/CCPA/DPDP (Indian Data Protection) — globally aware.
- **Structured output:** JSON-first — directly pipeable to helpdesk APIs.
- **Safety alignment:** Strongest legal/security/abuse escalation patterns in the entire 13-profession set.

### Deployability
- **License:** MIT-equivalent, Jarvis-authored.
- **Vendor lock:** None.
- **Jarvis adaptability:** Drop-in for any support inbox Boss runs (own products + client work).

---

## Runners-up + Trade-offs

### #2: Eva (Anthropic's canonical customer-support template, Prompt 1)
- **Why not picked:** Production-grade pattern with IDENTITY/STATIC/EXAMPLES/GUARDRAILS structure — but content is insurance-specific and requires deep adaptation. Lacks explicit escalation routing.
- **When to use this instead:** Building a customer-facing chatbot for a specific product (use as skeleton).

### #3: Refund / Exception Decision Agent (Prompt 5)
- **Why not picked:** Specialized for refund decisions; narrower than full triage.
- **When to use this instead:** Refund processing workflows where policy adherence matters.

### #4: Voice-of-Customer Synthesizer (Prompt 6)
- **Why not picked:** Analytics tool, not triage agent. Different job.
- **When to use this instead:** Monthly product-feedback synthesis reports.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/customer-support-agent.md`
2. **Adaptations needed:**
   - Replace generic refund threshold ($100) with Boss's actual policy when deployed for his products.
   - Wire in product-specific knowledge base (FAQ / macros) before going customer-facing.
   - For internal use (Boss's own support work), no further adaptation needed.
3. **Tool access (suggested):** Read access to KB; no autonomous send; explicit escalation handoffs to email-agent / human review queue.
4. **Model recommendation:** haiku for high-volume triage; sonnet for nuanced drafts; opus only for legal/security escalation framing.

### Sensitive-profession safety wrapper (mandatory)
This is a winner where safety patterns drove selection: the 6 refusal rules (legal, security incident, cross-customer data, abuse, fabricated promises, autonomous send) are non-negotiable. When adapting, do NOT relax these rules to ship faster — they're the difference between a useful agent and a legal liability.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Classify/draft/route, never send |
| Scope boundaries | 5/5 | Closed-set enums everywhere |
| Output format guidance | 5/5 | JSON schema with confidence |
| Reasoning techniques | 4/5 | Classifier-first with deterministic routing |
| Safety / refusal patterns | 5/5 | 6 explicit rules; STRONGEST in the set |
| 2026 tech relevance | 5/5 | GDPR/DPDP-aware; JSON-pipeline-friendly |
| License-friendliness | 5/5 | MIT-equivalent, Jarvis-authored |
| **Overall** | **34/35** | Picked specifically for refusal-pattern strength |
