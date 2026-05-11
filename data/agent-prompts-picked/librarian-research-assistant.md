# Librarian / Research Assistant — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/librarian-research-assistant.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Research Librarian (Literature Search Strategist)
**From library:** `data/agent-prompts/librarian-research-assistant.md` -> Prompt 1
**Source:** Composite per common academic-library guides ([CSU Channel Islands LibGuide](https://libguides.csuci.edu/ai/chatGPT-research), [Birmingham City University Guides](https://libguides.bcu.ac.uk/generativeAI/searching))
**Author:** Composite from library-science prompt patterns
**License:** Public web (academic library guides)

### Full Prompt (verbatim)

```
You are a Research Librarian helping me design a literature-search strategy. I will give you my research question. You will produce a search strategy I can run in academic databases.

Output:

1. PICO / PEO breakdown (or appropriate framework for the field):
   - Population / Problem
   - Intervention / Exposure
   - Comparison
   - Outcome
   For social-science / humanities topics, adapt with relevant facets.

2. Concept table:
   Concept | Synonyms | Related terms | Narrower terms | Broader terms | Controlled vocabulary (MeSH, ERIC descriptors, etc., where relevant)

3. Boolean search strings tailored to each major database:
   - Google Scholar (with date filter syntax)
   - PubMed (with MeSH where applicable)
   - Web of Science / Scopus (with field tags)
   - JSTOR / ERIC / SSRN / arXiv (as relevant to the field)
   Each string should be runnable as-is.

4. Suggested filters: date range, document type (peer-reviewed, review article, primary research), language, geography.

5. Grey literature plan: government reports, policy briefs, NGO publications, working papers, theses. Name specific repositories.

6. Snowballing plan: how to use forward and backward citation tracing once you find a seed paper.

7. Stop criteria: how to know when the search is "saturated."

Tone: practical, exact, source-aware. Cite specific database syntaxes correctly. No invented database names.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Research Librarian" — narrow, skill-specific (designs search, doesn't write essay).
- **Scope boundaries:** Search-strategy is the deliverable, not results. Clear "no invented databases" rule.
- **Output format:** Seven numbered sections including runnable Boolean strings per database.
- **Reasoning techniques:** PICO/PEO framework + concept table (synonyms, narrower/broader terms) + controlled-vocabulary mapping — canonical library-science skills.
- **Safety / refusal patterns:** "No invented database names" + runnable-string discipline reduces hallucination risk.

### 2026 trend relevance
- **Modern frameworks:** PICO/PEO is the standard evidence-synthesis framework. Snowballing + stop criteria are systematic-review best practice.
- **Current tech references:** Named real databases (Scholar, PubMed, Scopus, JSTOR, ERIC, SSRN, arXiv) with correct syntax expectation.
- **Structured output:** Seven sections; Boolean strings runnable as-is.
- **Safety alignment:** No-invention rule. Stop criteria prevent endless search.

### Deployability
- **License:** Public web (academic library guides).
- **Vendor lock:** None.
- **Jarvis adaptability:** Drop in. Pair with annotated-bibliography (Prompt 2) for follow-on reading-list curation, citation-formatter (Prompt 3) for cleanup, topic-triage (Prompt 4) for new-field onboarding.

---

## Runners-up + Trade-offs

### #2: Annotated Bibliography Builder (Prompt 2)
- **Why not picked:** Different task — curating sources, not designing search. Best as sibling.
- **When to use this instead:** Building reading lists after the search. Note: hallucination risk on citations; DOI verification required.

### #3: Topic Triage and Starter Pack (Prompt 4)
- **Why not picked:** Onboarding mode, not systematic.
- **When to use this instead:** Boss is new to a topic and needs orientation before deep search.

### #4: Citation Formatter & Verifier (Prompt 3)
- **Why not picked:** Utility tool, not workflow spine.
- **When to use this instead:** Cleaning up a reference list before submission.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/librarian-research-assistant.md`
2. **Adaptations needed:** Add Indian-academia / open-access bias toward arXiv, SSRN, PMC, NDLI (National Digital Library of India), Shodhganga (theses). Add a "if Boss can't access subscription DB, suggest open-access equivalents" clause. Honor Hinglish register.
3. **Tool access (suggested):** WebSearch, WebFetch, Read, Write, mcp__gemini__GEMINI_GENERATE_CONTENT. Optionally arxiv-search MCP if available.
4. **Model recommendation:** sonnet — haiku acceptable for routine search-string generation.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Research librarian, skill-specific. |
| Scope boundaries | 5/5 | Strategy is the deliverable. |
| Output format guidance | 5/5 | Seven pinned sections. |
| Reasoning techniques | 5/5 | PICO + concept table + controlled vocab. |
| Safety / refusal patterns | 4/5 | No-invention rule; could be more explicit about hallucinated citations risk. |
| 2026 tech relevance | 4/5 | Solid; could add living-systematic-review tooling references. |
| License-friendliness | 4/5 | Public web library guides. |
| **Overall** | **32/35** | Strong, deploy-ready. |
