# AuditAgent

> **tl;dr (LLM-pullable summary)**
>
> AuditAgent is a defensive, authorized-only static security auditor inside the Jarvis
> codebase. It runs SAST (semgrep p/default + 25 custom high-value rules), SCA
> (osv-scanner + trivy with reachability prioritization), and secrets detection
> (gitleaks + trufflehog) against local directories and authorized git repositories.
> It never scans unauthorized third-party live platforms and never auto-submits findings
> to any bug-bounty platform — every submission is a Tier-3 human action.
>
> Architecture: a 6-phase finite-state machine (`SCOPE_GATE → RECON → SCAN_RUNNING →
> ANALYZE → VERIFY → REPORT_GENERATING → DONE`) with a three-pass verification layer
> ("the moat"): deterministic file-context pre-triage (test/doc/example/build → auto
> false-positive, no LLM cost), followed by Haiku batch triage, followed by Sonnet
> deep-confirm for HIGH/CRITICAL only. A **recall-safety guard** prevents the LLM from
> silently discarding real source-code findings — the worst case is `needs_manual`, never
> a quiet drop.
>
> Eval result (25 labeled cases, deterministic + LLM modes): **100% FP-kill rate,
> 100% recall preserved** — zero false negatives, zero leaked false positives.
>
> CLI: `jarvis-audit <path> [--scanners ...] [--budget 0.50] [--top 15] [--reports]`
>
> API: mounted at `/v1/audit` in the jarvis-core daemon (FastAPI, Stripe-style errors,
> idempotency, cursor pagination). Rate-limit: 10 requests per 60 seconds.
>
> Safety model: RFC1918 + cloud metadata hard-blocked in scope.py (not configurable).
> `local_dir` targets auto-approved if under `$HOME`. `allow_exploitation` defaults
> `false` and requires an explicit Tier-3 human confirm even when set `true`. Bug report
> submission to any external platform is permanently Tier-3 — never autonomous.
>
> Scanner install: semgrep via pip (already in `.venv`); gitleaks, osv-scanner,
> trufflehog, trivy as binaries in `~/.local/bin`. Missing binaries degrade gracefully —
> the run continues with the scanners that are present.

---

## What it is

AuditAgent is a **defensive, read-only security scanner** for code you own or are
authorized to audit. It combines three detection layers into one workflow, ranks findings
by CVSS 4.0, kills false positives with a deterministic + LLM verify layer, and emits
either a summary report or submission-ready bug reports per HIGH/CRITICAL finding.

It is not a DAST tool, a live-web scanner, or a penetration-testing framework.
It scans code and dependency manifests. It does not exploit anything unless you
explicitly set `allow_exploitation: true` and then approve the Tier-3 gate.

### Safety model — what it will never do autonomously

| Rule | Enforced where |
|---|---|
| Never scan a target outside your `$HOME` | `scope.py` `_verify_local_path()` — hard check, not configurable |
| Never contact RFC1918 or cloud-metadata IPs | `scope.py` `_BLOCKED_NETWORKS` — hard-coded list |
| Never proceed to active exploitation without human approval | `state_machine.py` — `HUMAN_APPROVAL_PENDING` gate |
| Never submit a report to an external bug-bounty platform | Tier-3 action — requires explicit human confirm |
| Never auto-kill a finding in real source code | `pipeline.py` `_llm_may_kill()` recall guard |
| Never store full secret values in any output | `models.py` `_mask_secret()` — first 4 + last 4 chars only |

The scope verification methods are:

- `local_dir` — auto-approved if the resolved path is under `os.path.expanduser("~")`
- `git_repo` — checks `.github/CODEOWNERS`, `CODEOWNERS`, or `SECURITY.md` for Boss's
  email (`shriva.ujjawal@gmail.com`)
- `openapi_spec`, `container_image` — require `verified_owner: true` set explicitly
- DNS-TXT — `_jarvis-audit.<domain>` TXT record matches the per-audit token

---

## Quickstart

The `jarvis-audit` wrapper at `~/.local/bin/jarvis-audit` calls `scripts/audit.py`.
The jarvis-core daemon does not need to be running for the CLI.

```bash
# Audit a local project (deterministic verify only — free, no LLM)
jarvis-audit /path/to/your/project

# Enable LLM verify pass (Haiku triage + Sonnet deep-confirm for HIGH/CRIT)
jarvis-audit /path/to/your/project --budget 0.50

# Run only specific scanners
jarvis-audit /path/to/your/project --scanners semgrep,gitleaks

# Show top 25 findings instead of 15
jarvis-audit /path/to/your/project --top 25

# Emit submission-ready Markdown bug reports for every HIGH/CRITICAL finding
jarvis-audit /path/to/your/project --budget 0.50 --reports
```

**Example terminal output:**

```
Auditing: /home/ujjwal/my-app
   Scanners: semgrep, trivy, osv, gitleaks, trufflehog
   LLM verify budget: $0.50

   • scope_gate → recon
   • recon → scan_running
   • scan_running → analyze
   • analyze → verify
   • verify → report_generating
   • report_generating → done

── Scanners ─────────────────────────
   ✓ semgrep      exit=1
   ✓ trivy        exit=0
   ✓ osv          exit=1
   ✓ gitleaks     exit=0
   ⚠ trufflehog  not_installed

🛡  Verify layer (moat) auto-filtered 9 false-positive(s) of 14 raw findings.

── 5 actionable findings ──────────────────────
   HIGH      3
   MEDIUM    2

── Top findings ─────────────────────────
   [HIGH    ] CVSS 8.6  ✓conf  semgrep    app/db.py:42
              SQL query built from f-string with user input — use parameterized queries
   [HIGH    ] CVSS 8.6  ✓conf  gitleaks   config/settings.py:18
              Stripe secret key found in source file
   ...

📄 Report:  data/outputs/audits/a3f7b2e91c4d/report.md
📦 JSON:    data/outputs/audits/a3f7b2e91c4d/findings.json
   Audit ID: a3f7b2e91c4d
```

Scanners auto-degrade when a binary is absent — the run continues with those that
are installed. The `error="not_installed"` note appears in the scanner summary line
and in `data/outputs/audits/<id>/findings.json`.

Reports are written to `data/outputs/audits/<audit_id>/` relative to the working
directory. The audit ID is a 12-character hex string.

---

## How it works

### The 6-phase FSM

```
SCOPE_GATE → RECON → SCAN_RUNNING → ANALYZE → VERIFY → REPORT_GENERATING → DONE
    │                                                                           ▲
    └── SCOPE_DENIED (terminal)                                                 │
                                                                                │
                  HUMAN_APPROVAL_PENDING ──── (approved) ──────────────────────┘
                           │
                     (rejected/expired) → REPORT_GENERATING (without Phase 4)
                           │
                      CANCELLED (terminal — any unhandled exception)
```

Each `advance()` call in `state_machine.py` drives one transition. The FSM persists
state to `JarvisState` after every step, so a daemon restart resumes from the last
completed phase. The CLI uses a lightweight in-memory stand-in (`StandaloneState`)
that provides the same surface without touching the daemon.

| State | Work done |
|---|---|
| `scope_gate` | Verifies target ownership. Blocks RFC1918/metadata IPs. Resolves `..` traversal. |
| `recon` | Walks the file tree, detects languages, computes a content hash for the run record. |
| `scan_running` | Runs all enabled scanner adapters via `asyncio.gather()` with a concurrency cap of `AUDIT_MAX_CONCURRENT` (default 3). |
| `analyze` | Normalizes scanner-specific JSON into canonical `Finding` objects. Deduplicates by `sha256(rule_id|file_path|line_start)[:16]`. Correlates findings within 10 lines of each other in the same file. Multi-scanner agreement boosts confidence by +0.2. |
| `verify` | The moat — see below. |
| `human_approval_pending` | Phase 4 gate. Created only when `allow_exploitation=true` and confirmed HIGH/CRIT findings exist. Polls every 10 s for a `goal_approve` decision. |
| `report_generating` | Builds `AuditReport` — severity counts, CVSS distribution, top 10 findings by CVSS score, Markdown body. |
| `done` | Terminal. Report available at `GET /v1/audit/{id}/report`. |

### The verify layer ("the moat")

The verify layer is where raw scanner noise becomes a ranked, actionable list.
It runs three passes in sequence.

**Pass 0 — deterministic context pre-triage (no LLM, no cost)**

`context.py` `classify_context(file_path)` labels each finding's source file as one
of six categories and assigns an `fp_prior` float:

| Category | `fp_prior` | Trigger (examples) |
|---|---|---|
| `test` | 0.90 | path contains `tests/`, `__tests__/`, `spec/`; filename matches `*.test.py`, `*.spec.ts` |
| `documentation` | 0.92 | extension `.md`, `.mdx`, `.rst`, `.adoc`; path contains `docs/`, `wiki/`, `blog/` |
| `example` | 0.88 | path contains `examples/`, `fixtures/`, `mocks/`; filename stem matches `*example*`, `*fixture*`, `*mock*`; files like `.env.example`, `.env.sample` |
| `build` | 0.88 | path contains `node_modules/`, `vendor/`, `dist/`, `.next/`, `__pycache__/`, `.venv/` |
| `config_local` | 0.35 | exact filenames `.env.local`, `.env.development`, `.env.production.local` |
| `source` | 0.10 | everything else — production application code |

Any finding whose file category has `fp_prior >= 0.85` is immediately marked
`false_positive` with a deterministic rationale. No LLM is called, no budget
is spent. This pre-triage fires before Pass 1 and eliminates the majority of
noise on real codebases (test fixtures, docs placeholders, node_modules secrets).

**Pass 1 — Haiku batch triage**

Remaining findings (categories `source` and `config_local`, plus anything that
did not meet the fp_prior threshold) are batched in groups of 20 and sent to
claude-haiku-4-5 (`AUDIT_HAIKU_TIMEOUT` default 90 s). The prompt includes each
finding's `file_context` label and `context_rationale` so the model is guided
by the same six-category framework.

The model returns one verdict per finding: `confirmed`, `false_positive`, or
`needs_manual` — each with a mandatory one-line reason.

**Recall-safety guard (enforces zero false negatives)**

`_llm_may_kill(finding)` returns `True` only when the file context is
`test`, `documentation`, `example`, or `build`. For `source` and `config_local`
files, if the Haiku or Sonnet model returns `false_positive`, the verdict is
**clamped to `needs_manual`** instead of being accepted. The finding is never
silently discarded. A human reviews `needs_manual`; nothing in real application
code is dropped on the model's word alone.

```
haiku verdict: false_positive  +  file_context: source
           ↓
verdict clamped → needs_manual
verification_reason: "[haiku→recall-guard] LLM judged FP but file is real source; kept as needs_manual."
```

**Pass 2 — Sonnet deep-confirm**

Findings that survived Pass 1 as `confirmed` with severity `HIGH` or `CRITICAL`
get a full individual analysis from Sonnet (`AUDIT_SONNET_TIMEOUT` default 120 s).
Sonnet refines the CVSS score, generates a concrete remediation recommendation, and
re-evaluates exploitability. The recall guard applies here too.

**LLM-unavailable fallback**

If the LLM is unreachable or times out, the verify layer falls back to deterministic
heuristics: multi-scanner agreement (2+ scanners flag the same location) → `confirmed`;
single scanner + `CRITICAL` severity → `needs_manual`; everything else → `needs_manual`.
The run never fails due to LLM unavailability.

### Eval result

```
$ .venv/bin/python scripts/eval_audit_verify.py

Loaded 25 eval cases from data/evals/audit/verify_cases.jsonl
Mode: deterministic only (classify_context + _deterministic_triage)

=== AuditAgent Verify-Layer Eval (deterministic mode) ===
  Total cases       : 25
  Correct           : 25 / 25  (100%)

  FP-kill rate      : 100.0%  (14/14 known-FPs killed)
  Recall preserved  : 100.0%  (11/11 real findings kept)

  Leaked FPs: none
  False negatives (real→FP): none

  Gate FP-kill ≥ 80%       : PASS  (100.0%)
  Gate recall-preserved ≥ 90%: PASS  (100.0%)

  OVERALL: PASS — moat is working
```

---

## Three detection layers

### Layer 1 — SAST (semgrep)

Runs `p/default` (broad security + correctness pack) alongside 7 custom rule files
in `configs/rules/`. All custom rules are namespaced `jarvis-*` and include CWE,
OWASP category, and a `confidence` hint in metadata.

| File | Detects | CWE | Mode |
|---|---|---|---|
| `ssrf.yaml` | User input → `requests`/`httpx`/`urllib`/`aiohttp`/`fetch`/`axios` without host allowlist | CWE-918 | taint |
| `injection.yaml` | SQL injection via f-string/.format/concat into `execute()`; OS command injection via `os.system`/`shell=True`/`child_process.exec`; NoSQL injection (Mongo) | CWE-89, CWE-78, CWE-943 | pattern + taint |
| `path-traversal.yaml` | User input → `open()`/`readFile`/`path.join`/`send_file` without confinement | CWE-22 | taint |
| `deserialization.yaml` | `pickle.loads` on untrusted input; `yaml.load` unsafe loader; Node `unserialize`/`vm.run*` | CWE-502 | pattern + taint |
| `ssti.yaml` | `render_template_string` / string-built Jinja2 `Template` with user input; Node template engines compiled from request strings | CWE-1336 | taint |
| `authz.yaml` | JWT `verify=False` / `algorithms: ['none']`; CORS `*` + credentials; hard-coded auth-bypass flag | CWE-287, CWE-942 | pattern (conservative) |
| `mcp-agent-security.yaml` | **2026 wedge** — see below | CWE-78, CWE-94, CWE-22, CWE-306, CWE-77 | taint + pattern |

**The 2026 wedge: `mcp-agent-security.yaml`**

This rule file maps to the OWASP Top 10 for Agentic Applications (2026) and OWASP
MCP Top 10. No off-the-shelf semgrep pack covers these attack surfaces. Five rules:

- `jarvis-mcp-tool-arg-to-shell` — MCP/agent tool passes its argument (attacker-influenceable
  via tool call or poisoned tool input) into `os.system`, `subprocess(shell=True)`, `eval`,
  or `exec`. Maps to OWASP Agentic ASI08 Excessive Agency.
- `jarvis-agent-llm-output-to-sink` (Python + Node) — LLM completion text flows into
  `eval`/`exec`/shell/SQL/file sink. Model output is untrusted data; a poisoned document
  or ticket body becomes RCE via indirect prompt injection (OWASP LLM02 Insecure Output
  Handling).
- `jarvis-mcp-transport-bind-all-interfaces` — MCP server bound to `0.0.0.0` with no
  auth. The CVE-2026-27825 ("MCPwnfluence") enabler — an unauthenticated network-adjacent
  actor can invoke every registered tool.
- `jarvis-mcp-tool-file-write-unconfined` — MCP tool writes to a path built from its
  argument without `validate_safe_path`. A traversal payload overwrites `~/.ssh/authorized_keys`
  or `/etc/cron.d`.
- `jarvis-mcp-tool-description-instruction-bearing` — tool docstring contains imperative
  agent-directed text ("ignore previous", "you must always call"). Tool descriptions are
  injected into the agent's context — a tool-poisoning / prompt-injection surface.

Validate all rules compile cleanly:

```bash
.venv/bin/semgrep --config jarvis_core/audit_agent/configs/rules/ --validate
```

### Layer 2 — SCA (osv-scanner + trivy + reachability)

Two adapters run in parallel. `osv-scanner` queries the OSV database against the
project's dependency manifests (requirements.txt, package.json, go.mod, Gemfile,
pom.xml, and 15 others). `trivy` runs `trivy fs` in JSON mode.

**Reachability prioritization (`reachability.py`)**

60–95% of SCA alerts are unreachable code. Before the LLM verify pass, every OSV
finding gets a deterministic, LLM-free reachability check:

1. Extract the package name from the finding evidence (format: `<vuln_id> in <pkg>@<version>: ...`).
2. Walk up to `AUDIT_REACH_MAX_FILES` (default 5,000) source files in the target tree,
   skipping `node_modules/`, `vendor/`, `.venv/`, and build directories.
3. Scan each `.py`/`.pyi` or `.js`/`.ts`/`.jsx`/`.tsx` file for `import <pkg>`,
   `from <pkg> import ...`, `require('<pkg>')`, or `import ... from '<pkg>'`.
4. Verdict:
   - `reachable=True` → keep; raise priority for HIGH/CRITICAL.
   - `reachable=False` → downgrade to LOW + `needs_manual`. **Never deleted** —
     dynamic imports (`importlib`, variable-based `require`) are a known blind spot,
     so unreachable means "downgrade for human review", not "suppress".
   - `reachable=None` → no adjustment (non-OSV finding or unparseable package name).

### Layer 3 — Secrets (gitleaks + trufflehog)

Both scanners run with project-specific exclude configs that skip `node_modules/`,
`vendor/`, `dist/`, and `__pycache__/` — without this, JS/TS projects hit scanner
timeouts.

- `gitleaks` — uses `--no-git` (scans files directly, not git history) with the
  custom config at `configs/gitleaks-jarvis.toml`. Exit code 0 regardless of findings.
- `trufflehog` — uses `filesystem` mode with `--json`. Exclude patterns from
  `configs/trufflehog-exclude.txt`.

All secret values in findings are immediately masked in the normalizer:
`first4...last4` (e.g. `AKIA...MPLE`). Full secret values are never written to
reports, logs, or the findings JSON.

---

## Submission reports

When you pass `--reports`, `write_reports()` in `reporting.py` emits one
`report-NN-<slug>.md` per HIGH or CRITICAL non-FP finding into
`data/outputs/audits/<id>/reports/`, plus an `index.md`. Reports are
huntr/HackerOne paste-ready Markdown.

```bash
jarvis-audit /path/to/project --budget 0.50 --reports
# → data/outputs/audits/a3f7b2e91c4d/reports/report-01-sql-injection-a1b2c3d4.md
# → data/outputs/audits/a3f7b2e91c4d/reports/index.md
```

Each report contains: title, CVSS 4.0 vector + score, CWE, OWASP category,
affected asset, summary, numbered reproduction steps, proof of concept,
impact assessment, primary + secondary remediation, and references. Ten
vulnerability classes have hand-written PoC templates (SQLi, command injection,
hardcoded secrets, SCA/CVE, SSRF, path traversal, XSS, deserialization, JWT,
XXE) with a `GENERIC` fallback.

**Example report header (truncated):**

```markdown
# SQL Injection in `app/db.py:42` leading to database content disclosure or authentication bypass

---

## TL;DR / Summary

SQL injection at `app/db.py:42` allows an attacker to inject arbitrary SQL into the
query via unsanitized user input, potentially disclosing database contents, bypassing
authentication, or corrupting data.

---

## Severity

- **CVSS v4.0 vector:** `CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N`
- **Rating / Score:** High (8.6)
- **Why this severity:** AV:N (network-accessible), AC:L (no special conditions), PR:N
  (unauthenticated), VC:H/VI:H (database read/write). Critical or High depending on auth
  requirement. Computed vector: `CVSS:4.0/AV:N/...`

---

## Proof of Concept

**Detection payload (Boolean-based):**
```sql
' AND '1'='1'--    -- true condition
' AND '1'='2'--    -- false condition
```

**Confirmation:** Deterministic response difference between true/false payloads.
Do NOT use UNION-based or error-based extraction in the PoC — boolean diff is sufficient.
Do NOT dump tables or extract user data.
```

> Submission to any external platform is a Tier-3 action — it requires explicit human
> approval. AuditAgent never submits autonomously, even in `fullauto` mode.

---

## Running the eval

The eval harness at `scripts/eval_audit_verify.py` loads 25 labeled cases from
`data/evals/audit/verify_cases.jsonl` and measures the verify layer's precision
(FP-kill rate) and recall (real findings preserved).

**Deterministic mode (fast, free, CI-safe):**

```bash
.venv/bin/python scripts/eval_audit_verify.py
```

**Full LLM mode (requires daemon, costs ~$0.05):**

```bash
.venv/bin/python scripts/eval_audit_verify.py --llm
```

**Quiet mode (metrics only):**

```bash
.venv/bin/python scripts/eval_audit_verify.py --quiet
```

**Gate definitions:**

| Gate | Threshold | Meaning |
|---|---|---|
| FP-kill rate | ≥ 80% | Of the 14 known-FP cases, how many were correctly killed as `false_positive` |
| Recall preserved | ≥ 90% | Of the 11 real-finding cases, how many were NOT incorrectly killed |

The eval exits with code `0` (both gates pass) or `1` (any gate fails), suitable
as a CI quality gate.

The `_verdicts_match()` function applies flexible matching: for `expected=confirmed`,
both `confirmed` and `needs_manual` count as correct (the finding stays in the human
review queue). For `expected=false_positive`, only `false_positive` counts. This
preserves zero-false-negatives semantics in the eval.

---

## Scanner install

| Scanner | Layer | Install | Binary location |
|---|---|---|---|
| semgrep | SAST | `pip install semgrep` (already in `.venv`) | `.venv/bin/semgrep` |
| gitleaks | Secrets | `go install github.com/zricethezav/gitleaks/v8@latest` | `~/.local/bin/gitleaks` |
| osv-scanner | SCA | `go install github.com/google/osv-scanner/cmd/osv-scanner@latest` | `~/.local/bin/osv-scanner` |
| trufflehog | Secrets | Download from [trufflesecurity/trufflehog releases](https://github.com/trufflesecurity/trufflehog/releases) | `~/.local/bin/trufflehog` |
| trivy | SCA + container | `apt install trivy` or `brew install aquasecurity/trivy/trivy` | `~/.local/bin/trivy` |

`scripts/audit.py` prepends both `~/.local/bin` and `.venv/bin` to `PATH` at startup,
so the adapters find their binaries without any shell configuration.

**Python dependencies (in `.venv`):**

```
pydantic >= 2.13
dnspython >= 2.6
cvss >= 3.2           # CVSS 4.0 vector scoring
semgrep >= 1.70.0
```

---

## Reference

### File and module map

```
jarvis_core/audit_agent/
├── __init__.py
├── models.py              # Pydantic v2 canonical models (Finding, AuditRun, AuditState, ...)
├── state_machine.py       # advance() coroutine — one state transition per call
├── scope.py               # Ownership verification + RFC1918 hard-blocks + path enforcement
├── pipeline.py            # run_recon / run_scanners / normalize_dedupe_correlate / verify_findings / generate_report
├── context.py             # classify_context() — deterministic file-context FP classifier
├── reachability.py        # assess_reachability() / apply_verdict() — SCA package-level reachability
├── reporting.py           # build_bug_report / render_markdown / write_reports — submission-ready output
├── router.py              # FastAPI router mounted at /v1/audit
├── normalizers/
│   └── cvss.py            # CWE → CVSS 4.0 vector lookup table + scoring
├── tools/
│   ├── base.py            # ToolAdapter ABC + _run_subprocess + timeout/error types
│   ├── semgrep.py         # SemgrepAdapter (SAST)
│   ├── trivy.py           # TrivyAdapter (SCA + container)
│   ├── osv.py             # OsvScannerAdapter (SCA)
│   ├── gitleaks.py        # GitleaksAdapter (secrets)
│   └── trufflehog.py      # TruffleHogAdapter (secrets with live verify)
└── configs/
    ├── gitleaks-jarvis.toml      # gitleaks config with build/vendor excludes
    ├── trufflehog-exclude.txt    # trufflehog path exclude patterns
    └── rules/
        ├── ssrf.yaml
        ├── injection.yaml
        ├── path-traversal.yaml
        ├── deserialization.yaml
        ├── ssti.yaml
        ├── authz.yaml
        └── mcp-agent-security.yaml   # 2026 wedge — OWASP Agentic / MCP Top 10
```

### API router endpoints

Mounted at `/v1/audit` in the jarvis-core daemon. Rate-limit: 10 requests per 60-second
window. All error responses use Stripe-style envelopes: `{"error": {"code": "...", "message": "...", "type": "..."}}`.

| Method | Path | Status | Description |
|---|---|---|---|
| `POST` | `/v1/audit` | 202 | Start a new audit. Returns `AuditRunView`. Supports `Idempotency-Key` header (same key within 24 h returns the existing run). |
| `GET` | `/v1/audit/{audit_id}` | 200 | Poll audit progress. Returns `AuditRunView` with `progress_pct` and `audit_state`. |
| `GET` | `/v1/audit/{audit_id}/report` | 200 / 425 | Full `AuditReport`. Returns 425 Too Early if audit has not reached `done`. |
| `GET` | `/v1/audit/{audit_id}/findings` | 200 | Cursor-paginated `FindingsPage`. Query params: `limit` (1–100, default 20), `cursor` (opaque), `severity` (comma-separated), `status` (comma-separated). |
| `POST` | `/v1/audit/{audit_id}/cancel` | 200 | Cancel a running audit. Returns 409 if already terminal. |

**Start audit request body (`AuditRequest`):**

```json
{
  "user_id": "ujjwal",
  "target_uri": "/home/ujjwal/my-app",
  "target_kind": "local_dir",
  "allowed_scanners": ["semgrep", "trivy", "osv", "gitleaks", "trufflehog"],
  "allow_exploitation": false,
  "max_budget_usd": 2.0,
  "max_duration_seconds": 1800
}
```

**Poll response (`AuditRunView`):**

```json
{
  "audit_id": "a3f7b2e91c4d",
  "audit_state": "verify",
  "target_uri": "/home/ujjwal/my-app",
  "user_id": "ujjwal",
  "created_at": "2026-06-05T10:30:00",
  "updated_at": "2026-06-05T10:31:45",
  "progress_pct": 71,
  "total_findings": 5,
  "cost_usd_total": 0.18,
  "error": null
}
```

### `AuditState` enum

| Value | Meaning |
|---|---|
| `scope_gate` | Target ownership being verified |
| `recon` | File walk + language detection |
| `scan_running` | Scanners running in parallel |
| `analyze` | Normalize + dedupe + correlate |
| `verify` | Three-pass verification (det + Haiku + Sonnet) |
| `human_approval_pending` | Phase 4 exploitation gate — waiting for `goal_approve` |
| `report_generating` | Building Markdown + JSON report |
| `done` | Terminal — report available |
| `scope_denied` | Terminal — target not authorized |
| `cancelled` | Terminal — error or user-cancelled |

Terminal states: `done`, `scope_denied`, `cancelled`. `advance()` is a no-op on any
terminal state.

### Environment variables

| Variable | Default | Effect |
|---|---|---|
| `AUDIT_HAIKU_TIMEOUT` | `90` | Seconds to wait for Haiku batch triage before LLM-fallback |
| `AUDIT_SONNET_TIMEOUT` | `120` | Seconds to wait for Sonnet deep-confirm per finding |
| `AUDIT_MAX_CONCURRENT` | `3` | Max scanners running simultaneously in `asyncio.gather()` |
| `AUDIT_REACH_MAX_FILES` | `5000` | Max source files scanned per reachability check |
| `AUDIT_REACH_MAX_FILE_BYTES` | `2000000` | Per-file byte cap for reachability scanning |
| `AUDIT_ENRICH_TIMEOUT` | `45` | Seconds for optional LLM bug-report prose enrichment |
| `JARVIS_PROJECT_PATH` | (repo root) | Base path for resolving semgrep + scanner configs |

---

## Honest limitations

**Static-only.** AuditAgent runs SAST, SCA, and secrets detection — all static analysis.
It does not do DAST, runtime analysis, or live-web crawling. A vulnerability that only
manifests at runtime with specific database state is outside its scope.

**Reachability is package-level, not symbol-level.** The reachability check confirms
whether a vulnerable package is imported anywhere in the codebase, not whether the
specific vulnerable function is on a reachable call path from user-controlled input.
Symbol-level call-graph analysis (like `govulncheck` for Go) is a future improvement.
The current check is intentionally conservative: it downgrades unreachable packages
but never suppresses them.

**Dependency CVEs are commodity findings.** A finding that `lodash@4.17.20` has
CVE-2021-23337 will appear on every SCA scanner and in every security report for that
project. These findings have real value for understanding your attack surface but are
unlikely to earn a bounty unless you can demonstrate the affected function is
reachable and exploitable in the specific application context.

**MCP/agent-security taint sources are convention-dependent.** The semgrep taint rules
for MCP assume the FastMCP-style `@mcp.tool()` / `@tool` decorator convention. A server
using a different registration style will not be detected as a taint entry point. The
LLM-output-to-sink rules cover OpenAI/Anthropic/LangChain client shapes; a custom
wrapper needs a source pattern added to the YAML.

**Real bug-bounty payout requires manual PoC and Tier-3 human submission.** AuditAgent
identifies and ranks candidate findings. Converting a `confirmed` finding into a paid
report requires: writing a reproducible PoC against the live target, verifying the
vulnerability exists in the deployed version (not just in the code snapshot), checking
the program's scope for that asset, and submitting — all human steps, all Tier-3
actions, none of them autonomous.

---

## Cross-links

- [Verification layer design doc](../../data/notes/docs/reference/bugbounty-deepdive/02-architecture.md)
- [Custom semgrep rules README](configs/rules/README.md)
- [Eval cases](../../data/evals/audit/verify_cases.jsonl) — 25 labeled cases for the moat eval
- [Bug report template](../../data/notes/docs/reference/bugbounty-deepdive/hunting/TEMPLATE-bug-report.md)
- [jarvis-core daemon](../../jarvis_core/daemon.py) — mounts the `/v1/audit` router at startup
