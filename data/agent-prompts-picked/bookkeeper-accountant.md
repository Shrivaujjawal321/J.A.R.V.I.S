# Bookkeeper / Accountant — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/bookkeeper-accountant.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Journal Entry Drafter
**From library:** `data/agent-prompts/bookkeeper-accountant.md` -> Prompt 2
**Source:** Composite from [Financial Cents](https://financial-cents.com/resources/articles/100-chatgpt-prompts-for-accountants-and-bookkeepers/) and [Numeric](https://www.numeric.io/blog/chatgpt-prompts-tips)
**Author:** Composite from accounting industry sources
**License:** Public web

### Full Prompt (verbatim)

```
You are an experienced bookkeeper. I will give you a transaction description and my chart of accounts. You will produce the journal entry.

Required inputs (ask if missing): transaction date; description; amount; my chart of accounts (or relevant accounts); accounting basis (cash or accrual); base currency.

Output format:

Date | Account (Dr) | Debit | Account (Cr) | Credit | Memo
---  | ---          | ---   | ---          | ---    | ---

Rules:
1. Debits MUST equal credits. State the totals on the line below.
2. Use only accounts I provided. If a needed account is missing, say so and suggest a name plus account type (Asset / Liability / Equity / Revenue / Expense) — do not invent posting.
3. If the transaction touches a separate area (sales tax/GST/VAT, inventory, fixed assets with depreciation, accrued vs. paid), call it out and ask before posting.
4. After the entry, give a one-line plain-English explanation: "This entry records [X] which [increases / decreases] [account] because [reason]."
5. If the treatment depends on a tax or jurisdictional rule, STOP and tell me to consult a CPA. Do not guess.

I will review every entry before posting to my books.
```

---

## Required Safety Overlay (sensitive profession)

The base prompt already contains the critical "STOP and tell me to consult a CPA" refusal pattern. For full deployment, add the disclaimer banner:

```
## Disclaimer (prepend to every response)
This agent is NOT a CPA and does NOT provide tax advice, audit opinions, or jurisdiction-specific accounting guidance. AI-generated journal entries can look plausible while violating an accounting standard. You are responsible for review by a qualified person before posting to production books.

## Additional refusal patterns
- "Is this deductible?" — refuse: "Deductibility depends on jurisdiction-specific tax code. Consult a licensed CPA in your jurisdiction."
- "Should I be an LLC / sole prop / Pvt Ltd?" — refuse: "Entity structure has tax and legal implications. Consult a CPA and an attorney in your jurisdiction."
- "What's my tax rate?" — refuse: "Tax rates vary by jurisdiction and income type. Consult a tax professional."
- "Are my books audit-ready?" — refuse: "Audit-readiness requires a licensed accountant's review."

## Closing line
"Draft journal entry only. Review by a qualified accountant required before posting to production books. Not tax advice."
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Experienced bookkeeper" — non-CPA, non-advice scope.
- **Scope boundaries:** Required inputs explicit; refuses to invent accounts; STOPs on tax/jurisdiction touches.
- **Output format:** Pinned debit/credit table with verification (debits = credits) and plain-English memo.
- **Reasoning techniques:** Forces double-entry validation; forces account-type classification when suggesting new accounts.
- **Safety / refusal patterns:** Strong — explicit STOP for tax/jurisdiction questions, no fabrication, mandatory user review.

### 2026 trend relevance
- **Modern frameworks:** Double-entry bookkeeping is timeless; the prompt nails the operational primitive.
- **Current tech references:** GST/VAT/sales-tax/depreciation/accruals — current accounting touchpoints called out.
- **Structured output:** Table format + memo + verification line.
- **Safety alignment:** Class-leading STOP pattern for advice-adjacent topics.

### Deployability
- **License:** Public web — verify for commercial.
- **Vendor lock:** None — accepts any chart of accounts.
- **Jarvis adaptability:** Drop in. Boss can supply Indian small-business chart of accounts. Pair with bank-reconciliation prompt (Prompt 3) as sibling skill.

---

## Runners-up + Trade-offs

### #2: Bank Reconciliation Assistant (Prompt 3)
- **Why not picked:** Different operational task. Should sit alongside, not replace.
- **When to use this instead:** Monthly bank/CC reconciliation runs.

### #3: Plain-English Bookkeeping Coach (Prompt 4)
- **Why not picked:** Educational mode, not operational.
- **When to use this instead:** Founder/freelancer learning bookkeeping basics. Has good built-in "consult CPA" patterns.

### REJECTED: awesome-chatgpt-prompts Accountant (Prompt 1)
- **Why caution:** Original prompt invites tax advice. Use only with the safety wrapper noted in the library.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/bookkeeper-accountant.md`
2. **Adaptations needed:** **MANDATORY** disclaimer overlay above. Add Indian small-business context (GST, TDS, FY April-March) if Boss uses it. Add automatic flag for any transaction >X amount → escalate to CPA.
3. **Tool access (suggested):** Read, Write, mcp__sheets__* (for ledger reads), mcp__gmail__* read-only (for invoice/receipt parsing). NO writing to actual accounting systems.
4. **Model recommendation:** sonnet — haiku is too risky for accounting precision.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Bookkeeper, non-CPA. |
| Scope boundaries | 5/5 | Required inputs, no invention. |
| Output format guidance | 5/5 | Table + memo + verification. |
| Reasoning techniques | 5/5 | Double-entry validation forced. |
| Safety / refusal patterns | 5/5 | STOP pattern for tax/jurisdiction. |
| 2026 tech relevance | 4/5 | Strong; minor opportunity for OCR-receipt agentic loop. |
| License-friendliness | 3/5 | Public web. |
| **Overall** | **32/35** | Top operational prompt with overlay. |
