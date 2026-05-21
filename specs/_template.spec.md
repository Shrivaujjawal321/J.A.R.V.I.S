# Spec: {component-name}

**Status:** draft | active | deprecated
**Owner:** {file path of implementation}
**Last reviewed:** {YYYY-MM-DD}

## Purpose

One paragraph. What problem does this component solve? Why does it exist? What would break if it disappeared?

## Inputs

| Name | Type | Source | Notes |
|------|------|--------|-------|
| ... | ... | ... | ... |

## Outputs

| Name | Type | Consumer | Notes |
|------|------|----------|-------|
| ... | ... | ... | ... |

## Behavioural contract

Bulleted list of MUST / SHOULD / MUST NOT statements that describe externally observable behaviour. Avoid implementation detail. Example:

- MUST return within 500ms p95
- MUST skip when input matches skip-case regex
- MUST NOT mutate caller-provided state
- SHOULD fall back gracefully on dependency failure

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| Dependency timeout | ... | ... |
| Malformed input | ... | ... |

## Eval cases

Reference to `data/evals/{component}/test_cases.jsonl`. List the categories of cases covered, not the cases themselves.

## Non-goals

What this component explicitly does NOT do. Helps prevent scope creep and misuse.

## Dependencies

- Code: `path/to/dependency.py`
- Data: `data/...`
- Env vars: `FOO_BAR_ENABLED`, ...

## Changelog

- {YYYY-MM-DD}: Initial draft
