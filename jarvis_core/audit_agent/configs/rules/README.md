# AuditAgent — Custom High-Value Semgrep Rules

Defensive-only detection rules for the vuln classes that actually pay on bug-bounty
programs and that the generic `p/default` pack under-covers. These rules describe
**vulnerable code patterns** so the auditor can find and fix them — they do not
exploit anything.

All rules are namespaced `jarvis-*` and emit Semgrep findings with `cwe`, `owasp`,
`references`, and a `confidence` hint in metadata. The orchestrator wires this
directory into the SAST adapter (e.g. `--config <thisdir>` alongside `p/default`);
the LLM verify layer (`pipeline.py`) is the false-positive safety net downstream.

## Packs

| File | Detects | Primary CWE | Mode |
|------|---------|-------------|------|
| `ssrf.yaml` | User input → outbound HTTP client (requests/httpx/urllib/aiohttp; fetch/axios/got/http) without host allowlist | CWE-918 | taint |
| `injection.yaml` | SQLi via f-string/.format/concat into `execute()`/`db.query`; command injection via `os.system`/`shell=True`/`child_process.exec` with concat; NoSQL injection (Mongo query from raw `req.body`) | CWE-89, CWE-78, CWE-943 | pattern + taint |
| `path-traversal.yaml` | User input → `open()`/`readFile`/`path.join`/`send_file` without confinement | CWE-22 | taint |
| `deserialization.yaml` | `pickle.loads` on untrusted input; `yaml.load` unsafe loader; Node `unserialize`/`vm.run*` | CWE-502 | pattern + taint |
| `ssti.yaml` | `render_template_string` / string-built Jinja2 `Template` with user input; Node template engines compiled from request strings | CWE-1336 | taint |
| `authz.yaml` | JWT signature verification disabled (`verify=False`, `verify_signature: False`, `algorithms: ['none']`); CORS `*` + credentials; hard-coded auth-bypass flag in a guard | CWE-287, CWE-942 | pattern (conservative) |
| `mcp-agent-security.yaml` | **2026 wedge.** MCP tool arg → shell/eval; LLM completion → exec/SQL/file sink (indirect prompt injection); MCP transport bound `0.0.0.0`; MCP tool unconfined file-write (CVE-2026-27825 class); instruction-bearing tool descriptions (tool poisoning) | CWE-78, CWE-94, CWE-22, CWE-306, CWE-77 | taint + pattern |

`mcp-agent-security.yaml` maps findings to **OWASP Top 10 for Agentic Applications
(2026)** and **OWASP MCP Top 10** via the `owasp-agentic` metadata field — these are
green-field, low-competition, high-signal detectors no off-the-shelf pack ships.

## Design choices (precision over recall)

- **Taint mode** (`mode: taint`, sources/sanitizers/sinks) is used wherever it raises
  signal. A constant/hard-coded value is NOT a taint source, so e.g. a hard-coded URL
  in `requests.get(...)` does not trip SSRF — only request-derived input does.
- **Sanitizers** are declared so a validated path (`secure_filename`, `validate_safe_path`,
  allowlist membership, `int()` cast, `String()` cast) suppresses the finding.
- **authz.yaml is intentionally narrow** — authorization is the most FP-prone class, so
  it only fires on near-certain mistakes (verification disabled, `none` algorithm,
  wildcard CORS + credentials). "Missing authz decorator" is left to the semantic LLM
  verify layer, not pattern matching.
- Bounty programs punish noise; the verify layer is a net, not an excuse. Rules favor
  **HIGH confidence + low FP** over broad coverage.

## Validate

Every file must compile. The whole directory is validated as one config:

```bash
.venv/bin/semgrep --config jarvis_core/audit_agent/configs/rules/ --validate
# => Configuration is valid - found 0 configuration error(s), and N rule(s).
```

Per-file:

```bash
.venv/bin/semgrep --config jarvis_core/audit_agent/configs/rules/ssrf.yaml --validate
```

`tests/test_audit_reachability.py` includes a test that runs `--validate` over the
directory and asserts exit 0 (skips gracefully if the semgrep binary is absent).

## How to extend

1. Add a new `<class>.yaml` (one vuln class per file) following the existing shape:
   stable `id` (`jarvis-<class>-<lang>-<variant>`), `message`, `severity`
   (`ERROR`/`WARNING`/`INFO` → mapped to severity in `tools/semgrep.py`), and
   `metadata` with `cwe`, `owasp`, `references` (a URL), and a `confidence` hint.
2. Prefer `mode: taint` with explicit `pattern-sources` / `pattern-sanitizers` /
   `pattern-sinks` when the vuln is a dataflow shape — it kills the "constant argument"
   false positive class up front.
3. **YAML gotcha:** patterns containing inline `key: value` (e.g. dict literals like
   `{"verify_signature": False}` or `{ origin: "*" }`) must be single-quoted, or YAML
   parses the `:` as a mapping and `--validate` fails with "mapping values are not
   allowed here".
4. Validate (`--validate`) AND functionally smoke-test (run against a planted-vuln
   fixture; confirm it fires on the vuln and does NOT fire on the safe variant).
5. Keep it defensive: describe the vulnerable pattern to find+fix it. No payloads, no
   exploit generation.

## Known limitations / FP risk per pack

- **ssrf** — taint can miss input laundered through helpers semgrep can't follow
  (false negative); intra-procedural by default. The allowlist sanitizer list is not
  exhaustive (a custom validator named differently won't suppress → possible FP).
- **injection** — `jarvis-sqli-python-formatted-query` is pattern (not taint) and will
  flag an f-string query even if the interpolated value is a constant/enum (FP risk);
  verify layer catches these. NoSQL rule only covers Mongo-style APIs.
- **path-traversal** — `path.basename`/`secure_filename` are treated as full
  sanitizers; a partial sanitizer that still allows traversal would be wrongly
  suppressed (false negative).
- **deserialization** — `yaml.load` rule is high-precision; the pickle taint rule can
  miss deeply-laundered sources. `base64.b64decode` as a source can over-fire if the
  decoded value is actually trusted (FP).
- **ssti** — Node template rule is MEDIUM confidence; some template `.render()` calls
  on a pre-compiled static template can FP if the source flows in via a variable.
- **authz** — the `auth-bypass-flag` rule is LOW confidence by design (heuristic);
  expect it to need human triage. It will not catch most missing-authz bugs (those are
  semantic).
- **mcp-agent-security** — assumes the FastMCP-style `@mcp.tool()` / `@tool` decorator
  convention for tool-entry-point taint sources; servers using a different registration
  style won't be picked up by the tool-arg rules (false negative). The LLM-output-to-sink
  source list covers OpenAI/Anthropic/LangChain shapes — a custom client wrapper needs a
  source added. `bind 0.0.0.0` is LOW confidence (legitimate in containerized deploys
  behind an auth proxy) — treat as a prompt to verify transport auth, not a hard bug.
