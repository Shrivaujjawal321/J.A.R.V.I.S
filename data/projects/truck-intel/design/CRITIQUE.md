# CRITIQUE — Simplicity & Consistency Review of the Four Design Docs

**Reviewer role:** ruthless simplicity critic + cross-doc consistency checker
**Date:** 2026-07-22
**Docs reviewed:** `pipeline.md`, `storage.md`, `api-routing.md`, `quality-ai.md` (all read in full), cross-checked against `../research/*.md`

---

## Verdict (read this first)

Each document is individually strong: the tech choices are genuinely boring (Postgres queue, systemd timers, no Kafka/Airflow/Elasticsearch), the honest-gap discipline is real (no fake prices, no fake traffic, no scraping), and most alternatives were rejected for the right reasons. **But the four docs were written by four authors who never reconciled, and they currently describe two different systems.** The storage doc mandates SCD2 history (`valid_from`/`valid_to`) on every table while the pipeline doc explicitly rejects bitemporal tables and swaps whole tables atomically — a builder cannot implement both. There are two lineage schemas (`source_runs` vs `ingest_runs`), three names for the live-events table, an ODbL isolation rule that the pipeline *enforces in code* and the storage schema *violates by design*, a conflation step that requires an OSM ways table two docs say must never enter Postgres, and the product's core moat (gov-data enrichment + PBF tag injection) is absent from the pipeline that is supposed to run it. On top of the contradictions there are three concrete bugs (a UNIQUE constraint that breaks after the second successful run, a 2-hour job reaper that will kill every multi-hour Valhalla build forever, and nightly-computed quality columns that a snapshot swap silently wipes) and one honesty contradiction (DEF chain-inference is offered by the API doc and banned by the quality doc). **Verdict: NOT BUILDABLE AS-IS — needs one reconciliation pass, not a redesign.** Fix path: write a single short `ARCHITECTURE.md` that canonicalizes (a) one history model, (b) one lineage/catalog schema, (c) one table/schema naming map, (d) one ODbL posture, (e) one hardware spec and one deployment story; then apply the ~10 targeted fixes below. After that pass this is an unusually good solo-dev design.

---

## A. Cross-doc contradictions (blockers — two different systems on paper)

### A1. History model: SCD2 everywhere vs snapshot-swap-only
- **Where:** `storage.md` §4 (conventions: `valid_from`/`valid_to` on every entity table, close-old-row-insert-new loaders, partial indexes `WHERE valid_to IS NULL`) vs `pipeline.md` §9.1 + §12 ("We deliberately do **not** keep bitemporal core tables… snapshot-swap keeps only current… reconstructible-on-demand history is 10× simpler").
- **Issue:** These are mutually exclusive designs for the *same tables* (NBI bridges is `snapshot_swap → core.nbi_bridges` in pipeline.md and an SCD2 table `bridges` with `UNIQUE(source_id, source_record_id, valid_from)` in storage.md). Every storage.md index and query carries `WHERE valid_to IS NULL` complexity that pipeline.md's model makes meaningless. A newcomer reading both docs cannot know which loader to write.
- **Fix:** Pick pipeline.md's model (it is the simpler one and its own argument is correct): drop `valid_from`/`valid_to` from all entity tables; keep native history only where the data is a true time series (`fuel_prices`, `live_events`), exactly as pipeline.md §9.2/9.3 already says.

### A2. Two lineage/catalog schemas for the same job
- **Where:** `pipeline.md` §12 (`ops.sources`, `ops.source_runs`, `run_id`) vs `storage.md` §4 (`sources`, `ingest_runs`, `ingest_run_id` — different columns, no schema qualifier). `quality-ai.md` header references **both** and its SQL references `run_id`.
- **Issue:** Two different audit tables, two different source catalogs, incompatible column sets. Every "every row carries run_id" guarantee is ambiguous about which table it points to.
- **Fix:** One canonical pair: `ops.sources` (registry-synced, pipeline.md §4 wins because the YAML registry is the richer design) + `ops.source_runs`. Delete storage.md's variants; storage.md keeps only the extra columns it needs (`verify_status`, `attribution_text`) as additions to the canonical tables.

### A3. Table/schema naming drift — three names for the same table
- **Where:** live events = `core.live_events` (pipeline §9.3) = `live_events` (storage §4) = "one PostGIS `events` table" (api-routing §2.3 Live layer). Parking = `core.truck_parking_static` (pipeline §13.2) vs `parking_sites` (storage). Fuel prices = `core.fuel_price_estimates` (pipeline §14) vs `fuel_prices` (storage). The `ops`/`staging`/`core`/`osm` schema layout (pipeline §5.2) appears nowhere in storage.md, which defines all tables unqualified.
- **Issue:** Pure naming drift, but fatal for a one-read understanding: a builder implementing storage.md produces a database the pipeline doc's SQL and the API doc's queries don't match.
- **Fix:** One naming table in `ARCHITECTURE.md`; adopt pipeline.md's schema qualification (`ops`/`staging`/`core`/`osm`) and pick one name per table.

### A4. ODbL isolation: a rule one doc enforces in code and another violates by design
- **Where:** `pipeline.md` §5.3 ("OSM-derived tables live in the **`osm` schema only** … joined at query time, **never materialized into core tables**. The engine **refuses** a `load.target` outside the `osm` schema when `share_alike: true`") vs `storage.md` §4: `fuel_stations` (~110k OSM rows), `businesses` (OSM conflated in, `present_in ⊇ {'osm'}`), and `restrictions` (community/OSM rows with a `license` column) all live in the main schema. `api-routing.md` §1.4.4 adds a third posture (collective-database pattern with a separate schema).
- **Issue:** Pipeline's engine would literally refuse to load storage's own schema. This isn't a style disagreement — it's the platform's legal architecture, and the docs disagree about it.
- **Fix:** Decide once. Recommended: keep the hard engine rule for *unconflated* OSM mirrors (fuel, rest areas → `osm` schema, query-time join, as pipeline says), and explicitly carve out the two *deliberate* ODbL-derivative artifacts — the conflated `restrictions` table and the enriched PBF/graph — as documented share-alike databases (api-routing §1.4.4's position). Storage.md's `businesses` conflation must then either drop OSM attributes or accept and document the same ODbL consequence. Whatever the ruling, all three docs must state the same one.

### A5. Conflation needs an OSM ways table that two docs forbid and no doc ingests
- **Where:** `api-routing.md` §1.4.2 step 1 ("nearest OSM highway ways within 30 m … on **the ways table we already load via osm2pgsql**") vs `storage.md` §0/A3 ("The 11.2 GB OSM graph **never enters Postgres**") and `pipeline.md` (osm2pgsql appears nowhere; §8.6's PBF flow goes straight to Valhalla).
- **Issue:** The moat's matching step depends on data nobody loads, and that two docs explicitly promise is absent. Loading US highway ways into PostGIS is also a real ops cost (multi-GB, hours) on the pipeline doc's 16 GB box — it must be designed, not assumed.
- **Fix:** Add an explicit registry source to pipeline.md: osmium-filtered *highways-only* extract → `osm.ways` (filtered ways are a fraction of the full PBF; fits the `osm` schema rule from A4). Correct storage.md's "never enters Postgres" to "the routable graph never enters Postgres; a filtered ways mirror lives in `osm` for conflation."

### A6. The product's core enrichment loop is missing from the pipeline that must run it
- **Where:** `api-routing.md` §1.4 (conflate NBI + state DOT → confidence-tiered `pyosmium` tag injection → `valhalla_build_tiles`; "the graph is a derived artifact" of the canonical restriction table) vs `pipeline.md` §8.6 (`pbf` flow = download → build tiles → swap symlink; no conflation, no injection, no restriction table) and §9 (three load patterns, none of which fits a multi-source conflated table). `quality-ai.md`'s gates cover POI dedup but never restriction conflation.
- **Issue:** The single most product-critical process — the thing api-routing.md calls "the moat" — has no owner, no schedule, no failure handling, and no load pattern in the pipeline design. Related: pipeline's per-source `snapshot_swap` cannot build `businesses`/`restrictions` at all — three sources targeting one table means one source's swap wipes the other two's rows.
- **Fix:** Add a fourth pipeline stage type — `derived` jobs (conflation, enrichment, PBF injection) that run *after* their upstream sources publish, declared in the registry with `depends_on: [nbi_annual, penndot_posted, osm_ways]`. Extend §8.6's weekly flow to: download → conflate → inject → build → smoke-test → swap.

### A7. Hardware spec: 16 GB vs 64 GB RAM
- **Where:** `pipeline.md` §1 ("One VPS: 4–8 vCPU, **16 GB RAM**, 500 GB disk, ~$40–80/mo") and §8.6 ("Build takes a few hours **on 16 GB RAM**") vs `api-routing.md` §3 assumption 2 ("US-national Valhalla tile build fits on a **64 GB RAM** / 500 GB NVMe box (research-verified sizes)").
- **Issue:** 4× disagreement on the platform's only machine; the 64 GB figure is also not actually in the research files (grep found no such verification). Whichever is true changes the monthly cost class materially.
- **Fix:** One hardware line in `ARCHITECTURE.md`; empirically verify the US Valhalla build on the chosen box *before* committing (or plan regional builds + merge, which Valhalla supports and api-routing already names as fallback).

### A8. Deployment story: docker-compose vs systemd
- **Where:** `api-routing.md` §0 ("one VM, one `docker-compose.yml`" for PostGIS/Valhalla/FastAPI/Caddy) vs `pipeline.md` and `quality-ai.md` (everything is systemd units/timers; Postgres via `apt install`).
- **Issue:** Not fatal (they can coexist) but the docs never say so — a newcomer doesn't know whether the worker lives in compose or systemd, or where logs go.
- **Fix:** One sentence, stated once: stateful/serving pieces (Postgres, Valhalla, Caddy, FastAPI) in compose; all Python workers/timers as systemd user units on the host. Or all-systemd. Pick and write it down.

---

## B. Concrete bugs (would break in production as written)

### B1. `UNIQUE (source_id, status)` on the job queue breaks after the second run
- **Where:** `pipeline.md` §6, `ops.job_queue` DDL.
- **Issue:** Statuses include `done` and `dead`. The second job for any source that finishes (`status='done'`) violates the constraint — the completion UPDATE fails. Same for a second `dead`. The system deadlocks on its own bookkeeping within a day.
- **Fix:** Replace with a partial unique index: `CREATE UNIQUE INDEX ON ops.job_queue (source_id) WHERE status IN ('queued','running');` (and drop `DEFERRABLE`, which does nothing useful here).

### B2. The 2-hour stuck-job reaper kills every Valhalla build, forever
- **Where:** `pipeline.md` §6 (reaper resets any `running` job with `locked_at < now() − 2 h`) vs §8.6 ("Build takes **a few hours**"; plus an 11.2 GB download first).
- **Issue:** The weekly PBF job will always exceed 2 h, get reaped mid-build, re-queue, re-download 11 GB, and loop until `max_attempts` → dead. The design's own numbers guarantee it.
- **Fix:** Per-source `max_runtime_s` in the registry YAML (default 2 h; `pbf: 28800`); the reaper uses the per-source value.

### B3. Snapshot swap silently destroys nightly quality columns and the AI role's grants
- **Where:** `quality-ai.md` §9/§11 (confidence + component columns recomputed nightly by UPDATE on entity tables; `ai_writer` has *column-level grants on `businesses`*) vs `pipeline.md` §9.1 (publish = build `_new` table, `RENAME` swap, drop old).
- **Issue:** Two collisions: (1) a swap replaces the table, so any column the nightly job wrote since the last ingest (recomputed freshness, conflict penalties, AI-assigned categories not yet re-derivable from staging) vanishes; (2) Postgres grants attach to the table *object* — the renamed `_new` table does not carry `ai_writer`'s grants, so the AI sidecar loses write access after the first swap (or worse, keeps access to the dropped table's OID).
- **Fix:** Make the publish step responsible for both: after swap, re-apply role grants from a checked-in `grants.sql`, and enqueue a rescore job for the swapped table. Conflated/AI-touched tables (`businesses`) should not be `snapshot_swap` at all (see A6's `derived` pattern).

---

## C. Designs that assume data the research marked as a GAP / honesty contradictions

### C1. DEF chain-inference: one doc ships it, another bans it
- **Where:** `api-routing.md` §2.3 `/v1/fuel` ("DEF flag only where OSM `fuel:adblue` exists **or chain-inference (labeled `inferred`)**") vs `quality-ai.md` §5 + §10.4 ("never inferred from siblings — 'other Love's have scales' is **exactly the fabrication the hard rule bans**"; banned table row: "Filling missing amenities").
- **Issue:** Direct contradiction on an operational fact. Note the research (`fuel.md` §5) explicitly blesses the brand heuristic *as a labeled inference* — so quality-ai.md's blanket ban contradicts the research too.
- **Fix:** One ruling, written in both docs: a *deterministic, rule-based, labeled* brand→DEF heuristic is permitted as an explicit, documented exception (it is config, not AI, and renders as "inferred", never as fact); everything else stays banned. Or drop it from `/v1/fuel`. Either is fine — agreement is the requirement.

### C2. "Restrictions ~1–5M segments" sizes a table the research says doesn't exist free
- **Where:** `storage.md` §1 A4 and `quality-ai.md` V2 (both plan for "restrictions ~1–5M segments") vs `research/restrictions.md` ("Harmonized 50-state legal truck network — **DOES NOT EXIST FREE**"; OSM coverage "incomplete — supplement, never sole source").
- **Issue:** Mild, but it's exactly the reviewed-for failure: capacity planning that implies a data richness the research calls the paid gap. Realistic v1 volume is NBI-derived points (~620k) + a handful of state layers + sparse OSM tags — likely well under 1M.
- **Fix:** Restate A4 honestly ("~0.7–1M rows v1; 1–5M only if many state adapters land") so nobody later mistakes the sizing for a coverage promise.

### C3. Production dependency on a consumer Max-subscription OAuth token
- **Where:** `quality-ai.md` V3 + §10.5 (nightly batch AI via Claude Agent SDK on `CLAUDE_CODE_OAUTH_TOKEN`).
- **Issue:** Not a data-legality problem, but a fragility + terms gray zone: an unattended production service riding a personal consumer subscription can break (token expiry, plan limits, ToS changes) at any time. The doc's graceful-absence design is the right mitigation and is already there — the risk itself should still be named.
- **Fix:** Add one honest line to §10.5: "This is a consumer-subscription dependency; the sidecar is optional polish by design, and a paid API key is the named upgrade path if AI jobs ever become load-bearing."

---

## D. Missing error/failure handling

### D1. Routing path has no failure design
- **Where:** `api-routing.md` §2.3 `/v1/route` internals.
- **Issue:** Three gaps. (1) **No Valhalla-down path** — no timeout budget, no error code (`route_not_found` exists; `upstream_unavailable` doesn't), no stated behavior when the engine or PostGIS is unreachable mid-request. (2) **Closure exclusion uses the straight-line corridor** between waypoints — the actual route can leave that corridor (mountain detours, river crossings), so an active closure on the *real* route may never be passed as an exclusion, and no re-route loop exists when the post-route audit finds the returned geometry intersects an active closure. (3) The post-route audit's "graph bug: log loudly, warn the user" path returns a route the platform *knows* violates a restriction — warn-and-serve vs refuse-and-error is a safety-policy decision that must be written down, not left to the implementer.
- **Fix:** (1) 5 s Valhalla timeout → `503 upstream_unavailable`. (2) After routing, intersect returned geometry with active closures; on hit, re-call Valhalla once with the union of exclusions; still hit → serve with a `severe` warning. (3) One explicit paragraph: on-route restriction tighter than the truck → HTTP 200 with a blocking-level warning + incident log, never silent.

### D2. `/v1/along-route` accepts unbounded client input
- **Where:** `api-routing.md` §2.3 along-route.
- **Issue:** No cap on decoded polyline length, `buffer_mi`, or `range_mi` span. A 3,000-mile polyline with a large buffer is a multi-table geography intersection — an accidental (or deliberate) heavy-query DoS on the single node. Every other endpoint got mandatory spatial bounds; this one, the heaviest, didn't.
- **Fix:** Validate: decoded length ≤ 3,500 mi, `buffer_mi` ≤ 10, ≤ 25,000 polyline points; reject with `invalid_geometry` / `buffer_too_large`.

### D3. Quality jobs bypass the pipeline's own audit spine
- **Where:** `quality-ai.md` §11 (`quality-nightly.service`, `quality-ai.service`) vs `pipeline.md` §11 ("Everything derives from two tables the pipeline already writes").
- **Issue:** The nightly quality/AI jobs write no `source_runs` row, so the freshness SLO system — "the single most important alert in the system" — cannot detect a quality job that has been silently failing for a month. Monitoring's core claim ("catches everything") is false for a whole job class.
- **Fix:** Nightly quality/AI jobs write `source_runs` rows under synthetic source ids (`quality_nightly`, `quality_ai`) with their own SLOs (36 h). Zero new machinery — it's the pattern `kind: manual` already uses.

---

## E. Minor consistency nits (fix in the same pass, no debate needed)

1. **`businesses` breaks storage.md's own conventions** — §4 says every entity table carries `source_id` (+ A6: "every row carries `source_id`"), but `businesses` has neither `source_id` nor `source_record_id` (understandable for a conflated table — but the convention text must say so instead of claiming universality).
2. **`ai_writer` is granted UPDATE on `businesses.address_norm`** (`quality-ai.md` §10.0/§10.2) — a column that does not exist in storage.md's `businesses` DDL. Add it or drop the reference.
3. **NBI freshness SLO** — `pipeline.md` §4.1 YAML has `freshness_slo_hours: 8760` (= 12 months) with a comment saying "12 months", while §11 says annual SLO = 13 months. Pick one (13 months is right — vintage lag is real).
4. **WZDx feed count** — "~38" (api-routing), "~40" (storage), "40 feeds × every 5 min" (pipeline §0). Research verified 40 rows in the registry CSV, ~25 open. Standardize on "~40 registered / ~25 open".
5. **`polyline6` in storage.md's along-route SQL** (`ST_LineFromEncodedPolyline`) defaults to precision 5 in PostGIS — must pass `nPrecision => 6` or coordinates land ~10× off. One-word fix, classic footgun.

---

## What is RIGHT (so the reconciliation pass doesn't break it)

To be explicit about what must survive: the Postgres-table queue + `SKIP LOCKED` (correct at 0.14 jobs/sec), systemd timers over Airflow, the registry-YAML-per-source pattern, `polite_get()` as the single legality choke point, the three load patterns (once conflation gets its fourth), refusing to fake prices/traffic/ratings/absence-of-restriction, `manual` sources with staleness SLOs for bot-blocked pages, the two-winner conflict rule (display authority / route restrictive), the AI role that structurally cannot write operational facts, and static `status.html` over Grafana. These are the best parts of the design and every one of them is the *simple* option chosen for stated reasons.
