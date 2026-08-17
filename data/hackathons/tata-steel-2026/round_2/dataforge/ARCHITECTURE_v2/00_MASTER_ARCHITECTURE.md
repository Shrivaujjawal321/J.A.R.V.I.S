# E.D.I.T.H v2 — Master Architecture & Build Plan
**Tata Steel Hackathon · Round 2 (Maintenance Wizard PS) · deadline 15 Jun 2026**
Status: ARCHITECTURE COMPLETE — awaiting Boss go-ahead for build phase.

This master doc ties together the four specialist deliverables and maps them to the 8 requested deliverables. It also reconciles the cross-team API contract so the build phase is fully unblocked.

| # | Boss's deliverable | Where |
|---|---|---|
| 1 | Updated UI Design | `04_ui_ux_redesign.md` |
| 2 | Improved Backend Architecture | `02_backend_architecture.md` |
| 3 | Security Architecture | `01_security_architecture.md` |
| 4 | Validation Flow Diagram | `01` §3 (+ unified flow below) |
| 5 | Dataset Ranking Logic | `03_relevance_and_ranking_engine.md` |
| 6 | Database Schema Changes | `02` §2 |
| 7 | API Design | `02` §3 (+ contract below) |
| 8 | Vulnerability Prevention Checklist | `01` §4 |

---

## 0. Locked decisions (Boss, 2026-06-10)
1. **Relevance engine = Hybrid** — domain-KB vocab/schema match + local-embedding (bge-small) similarity to the PS. No API key. Bypass-proof via physical-value corroboration.
2. **Auth + storage = Supabase** — Auth (email/Google) + Postgres + private Storage. Per-user **max 5 datasets**.
3. **Sequence = architecture-first → demo-critical build.** (This doc = the gate before build.)
4. Branding: **E.D.I.T.H** only. Remove "Powered by AI" + the entire Advanced Section.
5. Uploads: **CSV, XLSX, JSON**.

---

## 1. Unified pipeline (the spine)
```
Client upload (drag-drop, CSV/XLSX/JSON)
  │  Supabase session (JWT)
  ▼
[1] AuthN  — verify Supabase JWT server-side (never trust client user_id)
[2] Rate limit — per-IP + per-user (upload + API)
[3] Quota — owner dataset count < 5  (DB-trigger backstop + RLS)        ──reject──▶ 429/403
[4] Type/size — ext allow-list + python-magic magic-bytes + 50MB stream cap ──reject──▶ 415/413
[5] Malware — (demo: ext+magic+structural; prod: ClamAV sidecar)        ──reject──▶ 422
[6] Sandbox safe-parse — subprocess, no-network, RLIMIT_AS+CPU+wall timeout,
      openpyxl read_only/data_only (no formula eval), row/col caps,
      zip-bomb ratio guard                                              ──fail────▶ 422
[7] Injection sanitize — neutralize leading = + - @ TAB CR (CSV/Excel formula
      injection); sanitize name/description/tags (XSS)
[8] RELEVANCE GATE (server-authoritative)
      relevance_score < threshold(30) ──▶ status=rejected, relevance=0, RANK=0,
                                          msg "Dataset is not relevant to the
                                          Tata Steel Hackathon." (NOT ranked)
      else ──▶
[9] Quality + domain scoring (existing 10-dim composite + domain_pdm)
[10] Ranking — Overall Score → global RANK() OVER (accepted only)
[11] Store — raw file → private Supabase bucket (signed URLs);
      metadata+report → Postgres; security event → upload_audit_log
  ▼
Board / dataset detail (sanitized, RLS-filtered)
```
Every reject branch is server-side and persisted — a forged request/response cannot surface a rejected dataset (the board view filters on the stored `status='accepted'` flag).

---

## 2. Reconciled API contract (answers the UI agent's 10 open questions)
Standard envelope: `{ ok, data?, error?: { code, message, field? } }`. Auth = Supabase JWT on all mutating routes.

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/api/datasets` | yes | upload → validate → gate → score → rank. Returns dataset record OR typed `RELEVANCE_REJECTED` error (status=rejected, relevance_score=0, rank=0). Idempotent via SHA-256 checksum. |
| GET | `/api/datasets` | optional | board: cursor pagination + `?q=&tag=&status=&sort=rank|score|date|size`. Public sees `accepted` only. |
| GET | `/api/datasets/{id}` | optional | full Detailed Analysis Report. |
| GET | `/api/datasets/{id}/file` | owner/public-if-accepted | Supabase **signed URL** (short TTL), not a proxy. |
| GET | `/api/me/quota` | yes | `{ used, remaining, max:5 }` → drives the UI counter. |
| DELETE | `/api/datasets/{id}` | owner | RLS owner-only. |

**Contract resolutions for UI:**
- **Rejection shape** → `error.code = "RELEVANCE_REJECTED"`, plus dataset stored as `status:"rejected", relevance_score:0, rank:0, reasons:[…]`. UI renders `RejectedBanner` (constructive: shows *why* + what IS relevant).
- **Rank** → global leaderboard, `RANK() OVER (ORDER BY overall_score DESC, …tiebreaks)`, recomputed after each completed job; accepted-only; rejected=0.
- **description / tags** → user-provided on upload; engine may auto-suggest tags (KB equipment/sensor hits) but user owns final value.
- **quota** → `GET /api/me/quota`.
- **formatFileSize** → shared util export in `web/lib/`.

---

## 3. Data model (Supabase Postgres) — see `02` §2 for full DDL
`users` (→ auth.users) · `datasets` (owner_id, name, description, tags[], size_bytes, n_rows, n_cols, mime, checksum, relevance_score, overall_score, rank, status, file_path, upload_date) · `audit_reports` (dataset_id, typed NUMERIC dimension scores + JSONB report) · `jobs` (async scoring status) · `upload_audit_log` (security/audit events). **RLS**: public read on `accepted`, owner-only writes everywhere; quota enforced by trigger.

---

## 4. Relevance + Ranking (see `03`)
- **Relevance (0–100)** = 0.65·KB-match + 0.35·embedding-sim. KB-match is 3-tier (sensor vocab + physical-range corroboration → equipment-class → maintenance vocab). Embedding = `BAAI/bge-small-en-v1.5` cosine vs PS anchor + 17 equipment concept texts. **Gate threshold = 30.**
- **Anti-gaming** (critical): `_corroborate_column` rejects renamed-junk via impossible value ranges; `_cross_signal_coherence` penalizes physically-incoherent sensor correlations. Renaming iris columns to `sensor_temp` fails.
- **Overall Score** = R·0.30 + Q·0.35 + D·0.20 + F·0.10 + P·0.05 (R=relevance, Q=quality composite [reused], D=domain_pdm [reused], F=feature richness, P=PS alignment). **Unrelated → 0 / Rank 0 always.**
- **Calibration**: positives = `samples/steel_*.csv`; negatives = iris/titanic; gaming = renamed-iris. Targets: precision ≥0.90, recall ≥0.80, false-accept = 0.0. Hot-tunable via `api/data/config/relevance_config.json`.

---

## 5. Build sequence — DEMO-CRITICAL (ship ≤ 15 Jun) vs STAGED
**Phase A — Backend core (demo-critical)**
1. Add `libmagic1` + (later) ClamAV deps to Dockerfile (alongside `libgomp1`).
2. Supabase project: schema + RLS + buckets + Auth. Feature flags `EDITH_AUTH_REQUIRED`, `EDITH_STORAGE_BACKEND`, `EDITH_PERSISTENCE_BACKEND` for atomic rollback.
3. Relevance-gate module + calibration sweep (config-driven threshold).
4. Ranking engine (fold into existing scorer; rejected short-circuit).
5. New `/api/datasets*` + `/api/me/quota`; JWT middleware; rate-limit; sandboxed safe-parse; formula/XSS sanitization; exact-origin CORS; streamed 50MB cap.
6. Backfill `audits.jsonl` → Postgres+Storage under a legacy service user.

**Phase B — Frontend (demo-critical)**
7. Rebrand → E.D.I.T.H; remove "Powered by AI" + Advanced Section.
8. Supabase auth wiring (login/session).
9. `DatasetCard v2` (all fields + states) · Dashboard `/datasets` (search/filter/sort, podium, grid/table) · `/board`→`/datasets`.
10. Upload UX: drag-drop, progress, `UploadCounter` (X of 5), `RejectedBanner`.
11. Dataset detail/report (reuse score-ring/radar) + dark mode + animations.

**Phase C — STAGED (document now, ship post-deadline)**
- Full ClamAV malware scanning (interim: ext+magic+structural+sandbox).
- Container-per-upload isolation (interim: subprocess + rlimits).
- WORM/tamper-evident audit log (interim: append-only Postgres table).
- Move backend HF→Render paid ($7/mo) after 15 Jun.

**Cross-cutting now:** UptimeRobot 5-min ping on the HF Space so it doesn't sleep during judging.

---

## 6. Vulnerability checklist → `01` §4 (OWASP Top 10 + LLM Top 10 mapped, with demo-critical flags).

## 7. Three real v1 holes already identified (fix in Phase A)
1. `await file.read()` whole-body → RAM-DoS → stream + 50MB cap.
2. Extension-only type sniff → add `python-magic` + structural parse (drop parquet/pickle/xls).
3. Over-permissive `.*\.vercel\.app` credentialed CORS → exact-origin allow-list.
