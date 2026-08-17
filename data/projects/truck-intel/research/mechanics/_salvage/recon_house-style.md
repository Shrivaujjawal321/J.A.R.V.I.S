# truck-intel house style — build blueprint

Repo root `/home/ujjwal/Documents/truck-intel`. 427 tests collected (`uv run pytest --collect-only -q`). Everything below is read from the code, with file:line.

---

## 0. Two ways data enters — pick the right one first

| Path | Used when | Machinery |
|---|---|---|
| **Registry source** (`registry/<id>.yaml` + `truckintel/parsers/<mod>.py`) | One remote URL → one parser → one table, fetched by the engine | `truckintel/engine.py:464 run_source` does fetch→raw-zone→gates→load. You write ONLY a YAML + a `parse()` |
| **Derived job** (`scripts/<name>.py` + seeded `ops.sources` row + `engine._DERIVED_RUNNERS` entry) | Multi-source, bulk-parquet/PBF, or anything needing DuckDB/osmium/conflation | You write the whole script incl. its own `_start_run`/`_finish_run`. Examples: `scripts/businesses_pipeline.py`, `scripts/osm_extract.py`, `scripts/osm_ways_job.py`, `scripts/quality_nightly.py` |

A mechanic-shop pipeline that conflates ≥2 sources is **derived**, exactly like `businesses_conflate`.

---

## 1. Registry YAML anatomy — `truckintel/registry.py:70 load_registry`

Loader returns dicts with **exactly** these 14 keys (asserted by `tests/test_registry.py:11 EXPECTED_KEYS`):
`id, name, owner, url, kind, load_pattern, schedule_minutes, license, attribution, slo_hours, gates, auth, parser, target`

| Key | Required? | Validation (registry.py line) |
|---|---|---|
| `id` | **yes**, non-empty str | `:108-113` also enforces global uniqueness across files |
| `name` | **yes**, non-empty str | `:108` |
| `url` | **yes**, non-empty str | `:108` |
| `kind` | **yes** | `:114` ∈ `{bulk_http, arcgis, live_json, api_keyed}` (`:16`) |
| `load_pattern` | **yes** | `:116` ∈ `{snapshot_swap, event_lifecycle, upsert}` (`:17`) |
| `schedule_minutes` | **yes**, positive int | `:185` via `_positive_int` (`:64`) — missing ⇒ raises |
| `slo_hours` | **yes**, positive int | `:190` |
| `owner` | optional | `doc.get` `:182` |
| `license` | optional | `:188` |
| `attribution` | optional | `:189` → column `ops.sources.attribution_text` (`:38`) |
| `gates` | optional mapping (default `{}`) | `:121-123` |
| `gates.required_fields` | optional | `:128-137` must be non-empty list of non-blank strings |
| `auth` | optional mapping or null | `:139-147` if present, `auth.env` must name an env var |
| `parser` | optional | `:149-162` bare lowercase module name (`_PARSER_NAME_RE` `:34`) **and importable at sync time** |
| `target` | optional | `:164-175` must be in `SNAPSHOT_TARGETS` **and** `load_pattern == snapshot_swap` |

`gates` is a free JSONB blob; only `required_fields` is schema-validated at sync. The other gate keys are read by the engine: `min_rows`, `max_row_delta_pct`, `geometry_valid_pct` (engine.py `:608, :619, :637`).

**Canonical modern example — `registry/nti_tunnels.yaml`** (the only one using both `parser:` and `target:`):
```yaml
id: nti_tunnels
name: FHWA National Tunnel Inventory (BTS NTAD FeatureServer)
owner: Federal Highway Administration (FHWA) / Bureau of Transportation Statistics (BTS), US DOT
url: https://services.arcgis.com/xOi1kZaI0eWDREZv/arcgis/rest/services/NTAD_National_Tunnel_Inventory/FeatureServer
kind: arcgis
load_pattern: snapshot_swap
parser: nti                    # truckintel/parsers/nti.py (Phase-2 registry key)
target: core.tunnels           # §5.1 allow-list (registry.SNAPSHOT_TARGETS)
schedule_minutes: 10080
license: US public domain
attribution: "..."
slo_hours: 9490
gates:
  min_rows: 350
  max_row_delta_pct: 10
  geometry_valid_pct: 98
  required_fields: [tunnel_id, lat, lon]
auth: null
```

House convention: **every YAML opens with a comment block carrying live verification evidence** (date + HTTP status + row count + license evidence). See `registry/wzdx_az.yaml:1-6`, `registry/caltrans_cwwp2_cc_d03.yaml:1-7`. This is not decoration — `tests/test_wzdx.py::test_promoted_wzdx_yaml_are_valid` and reviewers rely on it.

**Sync:** `make sync` → `registry.sync_sources` (`:200`) upserts on `source_id` (`_UPSERT_SQL` `:36`), then **disables** (never deletes) any enabled non-derived source missing from the registry (`:214-218`). `kind='derived'` rows are exempt.

---

## 2. Parser contract — quote

`truckintel/parsers/__init__.py` (the whole file is the contract):
```python
"""Per-source parsers — the ONLY per-source code in the engine.

Contract: each module exposes `parse(raw: bytes) -> Iterator[dict]` turning the
raw downloaded file into normalized row dicts (documented per module). Parsers
map fields BY NAME, never by column position (survives column shifts like the
NBI->SNBI 2028 migration). Parsers set observed_at to when the fact was true in
the world — never the download date.
"""
```

Exact signature, both reference parsers:
- `truckintel/parsers/nbi.py:82` — `def parse(raw: bytes) -> Iterator[dict]:`
- `truckintel/parsers/cwwp2.py:100` — `def parse(raw: bytes) -> Iterator[dict]:`

**What it receives:** the raw bytes the engine fetched, per `kind` (`engine.py:41 _RAW_EXT`): `bulk_http`→zip bytes, `arcgis`→one merged GeoJSON FeatureCollection (paged by `_fetch_arcgis` `:379`), `live_json`→response body, `api_keyed`→merged EIA doc.

**What it must return** — row dicts whose keys map to target columns (`truckintel/loaders.py:7-11`):
```
- keys matching target columns map 1:1
- 'lat'/'lon' pair, or 'geom_wkt' (WKT, EPSG:4326, may be None), becomes geom
- 'props' dict becomes the props JSONB blob
```
Do **not** set `source_id`/`run_id`/`ingested_at` — the loader stamps them (`loaders.py:125-128`, `:138-141`).

Event feeds use a fixed 5-key shape, stated verbatim in `cwwp2.py:15-26`: `event_id, kind, geom_wkt, observed_at, props`.

**Mandatory parser behaviours (enforced by tests, visible in every parser):**
- **Envelope validation raises, never returns `[]`** — `cwwp2.py:106-116`, `wzdx.py:124-134`. Reason quoted at `wzdx.py:117-123`: *"an event_lifecycle publish of [] soft-closes every active event for the source, so 'not a feed' must NEVER read as 'empty feed'."*
- **Drift guard**: 0-of-N recognizable records ⇒ raise (`wzdx.py:191`, `cwwp2.py:182`).
- **Tri-state**: unknown → `None`, never `False` (`cwwp2.py:140`, `nti.py:51 _coded_flag`, `osm_ways_job.py:223 _tristate`).
- **Never fabricate geometry**: junk coord → `geom_wkt=None` (`cwwp2.py:66-90`).
- **Never emit a garbage PK**: `nti.py:139` — `"tunnel_id": f"{fips}{number}" if fips and number else None` so gate 1 rejects it honestly.
- **`observed_at` = fact vintage** — NBI derives it from the filename year (`nbi.py:72 _vintage_year`, `:118`); NTI from the record's `year` (`nti.py:128-132`); CWWP2 from the Pacific-localized status timestamp (`cwwp2.py:50`).
- Every parser has a **module docstring listing every yielded key with type and meaning** (`nbi.py:96-110`, `nti.py:95-113`) plus a UNITS section when units were verified on the wire (`nti.py:9-21`).

**How rows get gated and written** — `engine._execute` `:574-682`:
```python
parser = importlib.import_module(f"truckintel.parsers.{_resolve_parser_module(src)}")
gates = src.get("gates") or {}
required = tuple(gates.get("required_fields") or _REQUIRED_FIELDS.get(source_id, ()))
ok1, rejects1 = gate1_schema(parser.parse(content), required)
rows_in = len(ok1) + len(rejects1)
ok_rows, rejects2 = gate2_coords(ok1)
dedup_field = _dedup_key_field(src)
if dedup_field is not None:
    ok_rows, rejects3 = quality.dedup(ok_rows, dedup_field)
```

---

## 3. Load patterns — `truckintel/loaders.py`

| Pattern | Function | Used by | Semantics |
|---|---|---|---|
| `snapshot_swap` | `:76` | reference datasets: bridges, tunnels, parking, all `osm.*` | Build `<table>_new` `LIKE … INCLUDING ALL`, COPY, RENAME-swap, drop old, **restore original index names** (`:165-168`). All in the caller's transaction — a failed load never touches live |
| `event_lifecycle` | `:172` | NWS, WZDx, CWWP2 | Upsert on `(source_id, event_id)`; anything absent from the poll gets `soft_closed_at = now()` (`:220-225`) — **never deleted** |
| `upsert` | `:229 fuel_upsert` | EIA | `ON CONFLICT (region, product, week_of) DO UPDATE` — idempotent time series |

`snapshot_swap` has a hard floor. Quote (`:149-155`):
```python
    if published < min_rows:
        raise EmptyPublishRefused(
            f"refusing to replace {target}: the load produced {published:,} "
            f"row(s), below the min_rows floor of {min_rows:,}. The live table "
            f"is untouched. ..."
```
`EmptyPublishRefused` is its own class (`:24`) so tests assert on it, not a string. Direct callers (osm jobs, conflate) pass their own `min_rows` — they bypass the registry gate layer entirely (`:96-100`).

**New snapshot table checklist:** add it to `registry.SNAPSHOT_TARGETS` (`registry.py:22-30`, re-checked defensively in `engine._resolve_snapshot_target:316`) **and** to `engine._DEDUP_KEY_BY_TARGET` (`:62-70`) or gate 3 silently no-ops.

A derived table with `lat`+`lon` as real columns **plus** `geom` needs a local swap variant — `businesses_pipeline.py:835 _swap_businesses` documents exactly why the shared loader doesn't fit (`:841-846`) while reusing `_geom_ewkt`, `_index_names_by_def`, `_split_target`, `_table_columns`.

---

## 4. Gates 1–5 and where confidence is scored

**Gate 1 — schema** `truckintel/validate.py:28 gate1_schema(rows, required_fields) -> (ok, rejects)`. Reject reasons `missing_required:<field>` / `unparseable:<field>`; `_FLOAT_FIELDS = ("lat","lon","price_usd_gal")` (`:21`) must parse as float.

**Gate 2 — coordinates** `validate.py:137 gate2_coords(rows)`. Checks `geom_wkt` first (authoritative), else `lat`/`lon`. Reasons: `coords_out_of_range`, `latlon_swapped`, `coords_not_in_us`, `geom_unparseable`. Multi-vertex rule at `:104 _judge_coords`: every vertex in range, ≥1 vertex in a `US_BBOXES` (`:13`) box, swap only when **all** vertices swap-in. **Never auto-fixes** — `:146-148`.

**Gate 3 — dedup** `truckintel/quality.py:65 dedup(rows, key_field)`. Keep-the-LAST occurrence (government files append corrections), earlier ones rejected `duplicate_natural_key`; keyless rows pass through. Wired at `engine.py:586-590`; key resolved by `engine._dedup_key_field:73` (event feeds → `event_id`; snapshot → `_DEDUP_KEY_BY_TARGET`; upsert → `None`).

**Registry gates** (post-gate-3, `engine.py:594-650`), each aborting with `status='gated'` and a message that names the numbers:
1. unconditional: `rows_in > 0 and not ok_rows` → `"all N rows rejected — upstream schema drift suspected"` (`:599`)
2. `min_rows` (`:608`)
3. `geometry_valid_pct` (`:619`) — recomputed from reject reasons
4. `max_row_delta_pct` vs last success's `rows_published` (`:637`)

**Gate 4 — cross-source conflicts** `quality.py:221 run_gate4`. Config-driven `ConsistencyCheck` dataclass (`:155`); `pairs_sql` must select `(entity_id, value_a, value_b, delta)` **for violating rows only**. Idempotent on `conflicts_open_uq`, auto-closes what re-check no longer finds (`:255-261`). Registry at `:176 REGISTERED_CHECKS`. **The disabled second check is the template for any spatial cross-source rule** (`:194-217`) — `ST_DWithin(b.geom::geography, w.geom::geography, 50)`.

**Gate 5 — confidence.** Formula lives once (`quality.py:346 compute_confidence`):
```
confidence = round(100 * clamp01(0.35*T + 0.25*F + 0.20*C + 0.20*A - P_geo - P_conflict))
```
Weights `:270`; `GEO_PENALTY=0.15`, `CONFLICT_PENALTY=0.10` capped `0.20` (`:271-273`). Components T/F/C/A stored per row 0-100 so *"why 65?"* is answerable. Pure helpers: `freshness:310` (from `observed_at`, NULL ⇒ 0.0 + flag `vintage_unknown`), `completeness:326` (weighted manifest fill), `agreement:335` (0.0 with open conflict / 1.0 corroborated / 0.5 baseline). Trust: `AUTHORITY_BASE_TRUST:104`, `fallback_trust:124`, `source_trust_map:135`.

Same formula pushed to SQL in `quality.py:439 rescore_table` — driven by `TABLE_SCORING:393` (`entity_type, table, pk_cols, entity_id_sql, half_life_days, completeness, where`). Only rows whose score actually changes are written (`IS DISTINCT FROM` guard `:557-562`). **A new entity table needs a `TableScoring` entry here** or it never gets scored.

Runner: `scripts/quality_nightly.py` (03:30 timer) `run_nightly:141` → gate 4 then gate 5 in **one transaction**, under one audited run row. Post-swap: every successful `snapshot_swap` calls `engine.enqueue_rescore:163` in the publish transaction (`engine.py:668`).

Exception: `core.businesses` is **not** in `TABLE_SCORING`; its confidence is computed at build time in `businesses_pipeline.py:1198-1204` using the same `quality.*` primitives.

---

## 5. `ops.source_runs` — the audit contract

Table: `sql/schema.sql:43`. Statuses: `running | success | skipped_unchanged | skipped_no_key | gated | failed`. Columns: `rows_in, rows_published, rows_rejected, message, raw_sha256, http_status`.

Docstring, `engine.py:465-466`:
> **Run one source end-to-end. Every outcome writes EXACTLY one `ops.source_runs` row — success, skip, gate-abort, or failure. Never fake success.**

Engine path: `_start_run:232` inserts `status='running'` returning `run_id`; `_finish_run:242` updates with terminal status. `run_source:464` wraps `_execute` in `except BaseException` (`:488`) so Ctrl-C/SIGTERM still closes the row instead of leaving a phantom `running`. Messages are `_redact`-ed (`:205`) — API keys never persist.

Side effects folded into `_finish_run` (both SAVEPOINT-guarded so a missing table can never roll back the run row — `:269-276`): `record_feed_health:135` circuit breaker (`BREAKER_THRESHOLD=5`, cooldown 60 min).

Rejects: `_write_rejects:448` → `quality.rejects(source_id, run_id, reason, raw_record)` — written **even when a later gate aborts the publish** (`:573-574`).

**Derived scripts each own a local copy of this bookkeeping.** The template (identical in 4 files — `businesses_pipeline.py:441/459`, `osm_extract.py:_start_run`, `osm_ways_job.py:438/448`, `quality_nightly.py:90/101`):
```python
_SEED_SQL = """
INSERT INTO ops.sources
    (source_id, name, owner, kind, load_pattern, schedule_minutes, slo_hours,
     enabled, verify_status)
VALUES (%(sid)s, '...', '...', 'derived', 'derived', NULL, %(slo)s, TRUE, 'verified')
ON CONFLICT (source_id) DO NOTHING
"""

def _start_run(source_id: str) -> int:
    with get_conn() as conn:
        conn.execute(_SEED_SQL, {"sid": source_id, "slo": SLO_HOURS})
        return conn.execute(
            "INSERT INTO ops.source_runs (source_id, status) "
            "VALUES (%s, 'running') RETURNING run_id", (source_id,)).fetchone()[0]
```
`kind='derived'` ⇒ `sync_sources` never disables it (`registry.py:216`), the tick never enqueues it (`schedule_minutes IS NULL`, `jobs.py:55`), and the engine worker never claims it (`jobs._CLAIM_SQL:91`).

The run **message is a structured, semicolon-joined fact string**, not prose. E.g. `businesses_pipeline.py:1235-1244`:
```
core.businesses=N; overture_in=N (dropped_invalid=N); fsq_in=N (dropped_invalid_or_closed=N);
merged=N; gray_flagged=N; cell_name_merges=N; cell_collision_drops=N; def_inferred=N
```
Every exclusion is **counted in the message**, never silently dropped. Exit codes: 0 = success/skip, 1 = failure (also on the run row).

Derived dispatch allow-list — `engine.py:707`:
```python
_DERIVED_RUNNERS: dict[str, list[str]] = {
    RESCORE_SOURCE_ID: ["scripts/quality_nightly.py", "--rescore", "all"],
    "osm_pois": ["scripts/osm_extract.py", "--job", "pois"],
    "osm_ways": ["scripts/osm_extract.py", "--job", "ways"],
    "overture_places": ["scripts/businesses_pipeline.py", "--pull-overture"],
    "fsq_places": ["scripts/businesses_pipeline.py", "--pull-fsq", "--fsq-mirror"],
    "businesses_conflate": ["scripts/businesses_pipeline.py", "--conflate"],
}
```
`_run_derived_job:733` refuses any argv resolving outside `<repo>/scripts/` (`:755-763`) and fails honestly if the script doesn't exist (`:764-771`).

---

## 6. API route module structure + registration

**Module shape** (`api/routes_places.py`, `api/routes_fuel_stations.py`, `api/routes_bridges.py`):
1. Docstring naming the endpoint(s) and source table, an **ATTRIBUTION** section explaining the licence posture, a **HONESTY** section, and an **INTEGRATOR NOTE** (`routes_places.py:27-30`):
```
INTEGRATOR NOTE — register in api/main.py (this file never edits main.py):
    from api import routes_places                 # add to the import block
    ...
    routes_places.router,                         # add to the include loop
```
2. `router = APIRouter()` — no prefix; full path in the decorator (`@router.get("/v1/places")`).
3. Module constants: `ATTRIBUTIONS`, `_NOTE`, `_SELECT` (the shared SELECT list), enum sets mirroring the DDL CHECK (`CATEGORY_SLUGS:46`).
4. A `_feature(r)` helper building props then `common.feature(...)`.
5. Handler: `common.parse_bbox` → build `where`/`params` lists → `common.q_all(f"...{' AND '.join(where)}...", params)` → `common.feature_collection(features, note=…, filter_notes=…, attribution=…, limit=…, offset=…)`.

**Shared plumbing — `api/common.py`** (docstring `:3-7`): one error envelope `{"error":{"code","message"}}` with stable codes (`invalid_bbox, bbox_too_large, invalid_param, upstream_unavailable, not_found`); `ApiError:26`; `install_error_handlers:42`; `connect_ro:64` opens the session with `options="-c default_transaction_read_only=on"` — *"even a buggy route physically cannot write"*; `q_all:74` turns any `psycopg.Error` into 503 `upstream_unavailable`; `parse_bbox:87` caps at `MAX_BBOX_DEG = 4.0`; `unknown:111` renders NULL as `"unknown"` (0 and "" pass through); `feature:116` / `feature_collection:126`.

**Registration — `api/main.py:11-21` import block, `:30-40` include loop.** Two touches, nothing else.

Binding conventions visible in every handler:
- Filters that exclude unknowns must say so in `filter_notes` — `routes_fuel_stations.py:130-139`, `routes_places.py:154-158`.
- Tri-state booleans are rendered **literally** `true/false/null`, not via `unknown()` (`routes_fuel_stations.py:167-170`).
- Anything derived from `osm.*` **must** carry `"© OpenStreetMap contributors"` on every feature and on the collection (`routes_fuel_stations.py:32, 177, 185`); `scripts/smoke_endpoints.py:162` FAILs the build if it's missing.
- Anything from `core.businesses` carries the Overture+FSQ pair and **deliberately no OSM attribution**, with the reason written out (`routes_places.py:4-12`).
- Every feature carries `source_id, run_id, ingested_at, observed_at, confidence` (+ `confidence_components` where stored).

New endpoints must also be added to `scripts/smoke_endpoints.py` (`SWEEP:65` for bbox-swept coverage claims, `PROBES:74`, `NEGATIVE_PROBES:100`). OK / **EMPTY** / FAIL — `EMPTY is never folded into OK` (`:12`).

---

## 7. Test conventions — 427 tests

`tests/conftest.py` is 22 lines; it exports exactly one thing:
```python
needs_db = pytest.mark.skipif(not _db_available(), reason="PostGIS unreachable")
```

Per-file counts: `test_osm_ways` 66, `test_validate` 37, `test_tunnels` 37, `test_api` 36, `test_parsers` 24, `test_quality` 23, `test_phase2_foundation` 23, `test_businesses_pipeline` 23, `test_wzdx` 21, `test_cwwp2` 16, `test_api_closures` 16, `test_registry` 12, `test_api_places` 12, `test_wave2_foundation` 11, `test_loaders` 11, `test_osm_extract` 10, `test_engine` 9, `test_api_fuel_stations` 9, `test_politeness` 8, `test_jobs` 8, `test_weekly_digest` 6, `test_conflate_gate` 6, `test_fsq_mirror_urls` 3.

**Layering is declared in each test module's docstring.** `tests/test_businesses_pipeline.py:1-14`: pure → DB-parity (`needs_db`) → DB end-to-end into **scratch clones** → live-network tests gated behind `TRUCKINTEL_NETWORK_TESTS=1`.

- **Parsers**: pure, no network, no DB. Fixtures are *"synthetic but format-faithful"* — `test_parsers.py:3-6`; the real NBI header is pasted in verbatim (`:23-35`) and a mini ZIP is built in memory (`_nbi_zip:39`).
- **API**: two layers (`test_api.py:1-8`). Validation/envelope tests need no DB; DB-backed tests assert **shape, never row counts** — *"No fake rows are ever inserted into core tables — real data only, even in tests."* Unregistered routers mount on a local app: `app = FastAPI(); common.install_error_handlers(app); app.include_router(routes_places.router)` (`test_api_places.py:27-29`). Requests via `asyncio.run` + `ASGITransport` (`:32-39`). Envelope asserted by `_err_code` (`test_api.py:43`).
- **Rendering tests monkeypatch `common.q_all`** onto canned rows and capture the SQL+params (`test_api_fuel_stations.py:116`).
- **DB tests use a scratch schema** (`SCHEMA = "scratch_businesses_test"`, `test_businesses_pipeline.py:34`) and pass the production functions' `target=`/`staging_*=`/`scoring=`/`conflicts_table=` overrides — that's *why* those kwargs exist (`run_conflate:1063`, `rescore_table:439`, `run_pois:...`).
- **Scripts are not a package** — loaded by path: `importlib.util.spec_from_file_location("businesses_pipeline", REPO_ROOT/"scripts"/"businesses_pipeline.py")` (`test_businesses_pipeline.py:44-51`); `conflate_gate.py:54` does `sys.path.insert` for the same reason.
- **Parity tests are a house rule**: any Python mirror of a Postgres function is pinned to it under `needs_db` — `norm_name` ↔ `norm_name_sql`, `trigram_similarity` ↔ `pg_trgm similarity()`, `geohash_encode` ↔ `ST_GeoHash`. If you write a Python twin of SQL, you owe a parity test.
- Registry-wide invariants live in `test_registry.py:34` (`set(s) == EXPECTED_KEYS` for every real YAML).

---

## 8. Existing conflation / entity-resolution to EXTEND, not rebuild

**`scripts/businesses_pipeline.py` is the entity-resolution engine.** A mechanic-shop pipeline should reuse it wholesale. The reusable, already-tested primitives:

| Symbol | Line | What |
|---|---|---|
| `squeeze` | 280 | `[a-z0-9]`-only key for brand/address/id |
| `norm_name` / `norm_name_sql` | 285 / 296 | matching-name normalization; **SQL twin generated from the same `_ABBREV` table (`:212`) so they cannot drift** |
| `trigram_similarity` | 307 | pg_trgm-compatible pure mirror |
| `haversine_m` | 328 | |
| `geohash_encode` | 339 | matches `ST_GeoHash` |
| `business_id` | 368 | `'biz_' + sha256(squeeze(name)|geohash7)[:16]` |
| `pair_bonus` | 387 | brand / last-10 phone digits / squeezed address match → 1.0 |
| `score_from` | 404 | **THE formula, the only place it exists** |
| `score_pair` | 411 | pure test surface |
| `_STAGE_TEMP_SQL` / `_PAIRS_SQL` | 916 / 936 | blocking join |
| `_MERGED_INSERT_SQL` / `_SINGLE_INSERT_SQL` | 950 / 985 | canonical-source merge |
| `_COLLISION_SQL` / `_resolve_collisions` | 998 / 1010 | geohash-cell key collisions |
| `run_conflate` | 1063 | the 3-phase orchestration |
| `def_inferred` | 423 | the one permitted inference |

The thresholds (`:184-189`):
```python
BLOCK_RADIUS_M = 150.0
BLOCK_NAME_SIM = 0.3
MERGE_THRESHOLD = 0.85
DISTINCT_THRESHOLD = 0.55
W_NAME, W_DIST, W_BONUS = 0.60, 0.25, 0.15
```
```python
def score_from(name_sim: float, dist_m: float, bonus: float) -> float:
    """THE formula (quality-ai.md §3.2 step 3) — the only place it exists."""
    return (W_NAME * name_sim
            + W_DIST * (1.0 - min(dist_m, BLOCK_RADIUS_M) / BLOCK_RADIUS_M)
            + W_BONUS * bonus)
```

Band policy (docstring `:42-52`) — **the gray zone is kept distinct and flagged, never guessed**:
```
  merge   sim >= 0.85 -> greedy 1:1 auto-merge (best score first, both sides used at most once)
  distinct sim <= 0.55 -> both kept.
  gray    0.55 < sim < 0.85 -> BOTH KEPT DISTINCT + flags ['dedup_gray_zone'].
          AI adjudication is Phase 4 — until then the safe default is
          distinct, honestly flagged (quality-ai.md §10.1).
```
Greedy 1:1 loop at `:1122-1137`; an ambiguous second-best ≥0.85 match is demoted to gray, not merged. Merge stays **reversible**: both per-source blobs survive under `props.overture` / `props.fsq` (`:976`), surfaced only on the detail endpoint (`routes_places.py:192-193`).

Also reusable:
- **`scripts/conflate_gate.py`** — measure-before-you-run harness. It *imports the production SQL* rather than retyping it (`:56-67`, `_PROD_WHERE:76`) so the measurement can't drift. Verdict `run_as_is` vs `spill_first` at 5M RAM-pressure units (`:71, :177`). **Run this before any US-scale conflation.**
- **`quality.dedup:65`** — within-source gate 3.
- **`quality.run_gate4:221` + `REGISTERED_CHECKS:176`** — cross-source disagreement persistence. The disabled `bridges_nbi_vs_osm_maxheight` check (`:194`) is the ready-made pattern for "OSM corroborates a core row via `ST_DWithin`" without copying ODbL attribute values.
- **`data/config/category_map.yaml`** already maps the mechanic vocabulary. The taxonomy has `truck_repair, mobile_repair, trailer_repair, tire_service, towing, truck_parts, truck_wash, truck_dealer` + honest general `auto_repair, auto_parts` (`schema_wave2.sql:73-82`, `businesses_pipeline.py:138-152`). The header (`category_map.yaml:39-51`) states the binding rule: general shops are surfaced **under general slugs, never relabeled truck-specific**, and `car_wash / dealerships / motorcycle / RV / inspection / IT repair` stay unmapped because *"Calling any of those 'truck_repair' — or even 'auto_repair' — would be fabrication."* `test_businesses_pipeline.py:57` enforces that every taxonomy slug is either mapped or listed in `unreachable_from_sources`.

**Hard constraint to respect:** `present_in <@ ARRAY['overture','fsq']` (`schema_wave2.sql:96-97`) makes `'osm'` structurally impossible in `core.businesses`. OSM mechanic POIs must land in a new `osm.*` table and be joined at query time with ODbL attribution, exactly like `osm.fuel_stations` + `/v1/fuel`. Adding a new source to `core.businesses` means widening that CHECK **and** re-justifying the licence posture in the header comment.

---

## 9. Route / corridor concept — what exists today

**Nothing structural.** No routes table, no linear referencing, no `ST_LineLocatePoint` / `ST_LineSubstring` / `ST_Buffer` anywhere (grep over `*.py *.sql *.yaml`). The only hooks a route feature could build on:

1. **`osm.ways`** (`sql/schema_phase2.sql:136-160`) — 109,777 rows, **Delaware only**. Carries `highway`, `name`, `ref` (`:140` — *"route ref, e.g. 'I 95'"*), `geom geometry(LineString,4326)` with a GiST index (`:159`) and `osm_ways_highway_ix` (`:160`). `way_row:235` also emits `oneway, maxheight_in, maxweight_lb, maxlength_in, maxwidth_in, hgv, bridge, tunnel` (extra columns added by `ensure_ways_columns:412`). **This is the only line geometry in the DB and the only `ref` field — a corridor built from `ref`-grouped ways is the natural path.**
2. **Explicit ruling that constrains it** — `osm_ways_job.py:6-7`: *"osm.ways is the conflation substrate for NBI->OSM matching — **NOT a routing graph**; the routable graph never enters Postgres (§3.1-5)."* And `README.md:61`: Valhalla/routing is out of scope by rule. `HIGHWAY_CLASSES` (`:92-98`) is deliberately drivable-only.
3. **Per-event route strings, props-only, no table**: CWWP2 emits `route`, `route_suffix`, `direction`, `postmile`, `milepost`, `county`, `elevation_ft` into `props` (`cwwp2.py:150-158`), rendered at `api/routes_live.py:346-354`. WZDx emits `road_names` (list) + `direction` (`wzdx.py:160-161`). These are **text labels, not geometry-linked references**.
4. **NBI props carry LRS route identifiers** — the real 2025 header includes `ROUTE_PREFIX_005B, SERVICE_LEVEL_005C, ROUTE_NUMBER_005D, DIRECTION_005E, LRS_INV_ROUTE_013A, SUBROUTE_NO_013B, KILOPOINT_011` (`tests/test_parsers.py:23-35`); the parser keeps the whole record in `props` (`nbi.py:154`), so route+milepoint is queryable from JSONB today but is not promoted to a column.
5. `quality.ConsistencyCheck` already demonstrates the point↔line spatial join idiom that a route-buffer query would use: `ST_DWithin(b.geom::geography, w.geom::geography, 50)` (`quality.py:207`), with the standing caveat (`:213-217`) that proximity alone is insufficient — *"the match needs the same-road name/ref refinement on top of <=50 m"*.

---

## 10. Ten-step checklist for the builder

1. **Decide registry vs derived.** Multi-source/conflated ⇒ derived script + seeded `ops.sources` row + `_DERIVED_RUNNERS` entry.
2. **DDL**: new additive `sql/schema_<wave>.sql`, `BEGIN;`…`COMMIT;`, `CREATE TABLE IF NOT EXISTS`, `ADD COLUMN IF NOT EXISTS`, idempotent, header comment carrying the honesty rules and every CHECK's rationale. Every entity table gets `source_id, run_id, ingested_at, observed_at` + `confidence, conf_trust, conf_fresh, conf_complete, conf_agree, flags TEXT[], props JSONB` + a GiST index on `geom`. Add a `Makefile` target next to `schema-wave2` (`Makefile:15-17`).
3. **Allow-lists**: `registry.SNAPSHOT_TARGETS` (if swapped), `engine._DEDUP_KEY_BY_TARGET`, `quality.TABLE_SCORING`, `api/routes_meta._TABLES` + `_VINTAGE_NOTES`.
4. **Parser or puller** honoring the `parse(raw: bytes) -> Iterator[dict]` contract or the DuckDB-pull pattern (`_duck():471` — 4 GB cap, spill to disk; `TRUNCATE` staging per run; COPY in `_COPY_BATCH=10_000` batches; progress every 100k).
5. **All HTTP through `polite_get`.** No exceptions.
6. **One `ops.source_runs` row per invocation**, structured semicolon message counting every exclusion, `except BaseException` → `failed`, exit 1.
7. **Confidence**: reuse `quality.compute_confidence` + store all four components.
8. **API route module** with the docstring sections + INTEGRATOR NOTE, then two lines in `api/main.py`, then entries in `scripts/smoke_endpoints.py`.
9. **Tests**: pure layer always-on, `needs_db` layer against scratch schemas, parity tests for any Python↔SQL twin, network tests behind `TRUCKINTEL_NETWORK_TESTS=1`. Never insert fake rows into core.
10. **Deploy**: `deploy/truckintel-<name>.service` + `.timer` (`Type=oneshot`, `WorkingDirectory=%h/Documents/truck-intel`, `%h/.local/bin/uv run …`, leading `-` on best-effort steps only), plus a row in `deploy/README.md`'s table.