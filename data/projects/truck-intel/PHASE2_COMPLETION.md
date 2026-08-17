# Truck-Intel — Phase 2 Completion Tracker

**Started:** 2026-07-23 (resumed from previous session's in-flight work)
**Owner:** Jarvis (autonomous, ultracode). Mandate: finish the whole Phase 2, don't stop.
**Phase 2 def:** MASTER_PLAN §10 — "Ingestion breadth + quality layer". All verified source families flowing; quality ladder live.

## Baseline at resume (2026-07-23 ~00:00 IST)
- Tests: **354 passed, 5 skipped** (all WIP tested).
- PostGIS `truckintel-pg` up. Row counts: bridges 629,710 · parking 1,915 · tunnels 580 · live_events 5,789 · fuel_prices 17,078 · **businesses 0** · osm.ways 109,777 (DE only) · osm.fuel 302 · osm.rest 4 · osm.weigh 6.
- **Stabilized:** killed orphan US-POIs extract (PID 1047945) that was double-writing the 48GB nodecache with the 23:04 chain (root cause of repeated POI failures); reaped 4 stale `running` rows; cleared stuck osm job-queue. Live US OSM chain (PID 1120651, POIs→WAYS→count) continues.

## Deliverable checklist (MASTER_PLAN §10 Phase 2)

| # | Item | Status | Notes |
|---|------|--------|-------|
| F1 | WZDx multi-feed poller + circuit breaker | ✅ done | 4 license-verified feeds (AZ/KS/MN/WA); breaker in engine |
| F2 | 3–5 state 511 adapters | ⏳ framework + keyless | keyed feeds are WAIT (keys/DAA, plan-acknowledged); build normalizer + keyless adapter, stub keyed as skipped_no_key |
| F3 | NTI tunnels + curated rules | ✅ done | 580 tunnels |
| F4 | OSM mirrors (ways/fuel/rest/weigh) | 🔨 US extract running | DE proven; US chain in background (~hrs) |
| F5 | Overture+FSQ businesses via DuckDB | 🔨 in progress | core.businesses=0 → bounded conflate now, full US after OSM |
| F6 | dedup + conflicts + confidence scoring | ✅ done | gates 3/4 + scoring |
| F7 | nightly quality job (own source_runs) | ✅ done | quality_nightly |
| D1 | /v1/fuel live | ✅ | fuel_prices 17k |
| D2 | /v1/places live | 🔨 | needs businesses > 0 |
| D3 | /v1/tunnels live | ✅ | 580 |
| D4 | /v1/live/closures live | ✅ | live_events |
| D5 | confidence + provenance on every feature | ✅ | scoring + lineage |
| D6 | **weekly digest** | ❌ build | not present — new script + timer + delivery |

## Wait-items (human-gated, cannot complete autonomously — document honestly)
- Per-state 511 API keys + DAA approvals (keyed feeds).
- TPIMS registration emails (live parking availability).
- ~20 WZDx feeds in `data/wzdx_proposed/` awaiting license review (legal judgment, not code).
- HF_TOKEN for FSQ gated release → **worked around** via anonymous source.coop mirror (frozen 2025-02-06, labeled).

## Work plan (resource-aware: 15GB box running 12GB OSM extract)
1. [x] Stabilize OSM extract (kill orphan, reap).
2. [ ] Build **weekly digest** (light, now).
3. [ ] **Bounded businesses conflate** → core.businesses>0 → /v1/places live (light DuckDB now).
4. [ ] **511 adapter framework** + keyless adapter (CWWP2) + keyed stubs (now).
5. [ ] Wiring/consistency fixes (derived runners, seeds).
6. [ ] **After OSM extract done:** full US Overture+FSQ pull + full conflate; verify osm.* US counts.
7. [ ] Full test suite + smoke-test all Phase-2 endpoints + adversarial review.
8. [ ] Commit everything; update MASTER_PLAN Phase-2 status + memory.

## Progress update (mid-session)

| Item | Status | Evidence |
|---|---|---|
| F2 511 adapter | ✅ **DONE** | Caltrans CWWP2 keyless, 3 districts (D02/D03/D09) = **565 chain_control rows** in core.live_events; new `parsers/cwwp2.py`; `/v1/live/chain-controls` endpoint live (covered_districts=[D02,D03,D09]); 13 parser tests |
| D6 weekly digest | ✅ **DONE** | `scripts/weekly_digest.py` (5-section 7-day rollup, Telegram/ntfy delivery seam implemented) + service + timer + Makefile + README + 4 tests |
| F5 businesses / D2 /v1/places | �️ **LIVE** (bounded) | conflate → **core.businesses=2,981** (NYC, Overture); /v1/places returns data + provenance; FSQ-mirror DuckDB-HTTP-glob bug **fixed** (`fsq_mirror_parquet_urls`, verified live) + 3 tests; full US backfill = post-OSM via new monthly `truckintel-businesses` timer |
| F4 OSM mirrors | 🔨 US extract running | POIs pass ~halfway (50k+ POIs found: fuel 46k); publishes at pass-end; WAYS pass follows |
| Wiring | ✅ | `overture_places`+`fsq_places` added to engine `_DERIVED_RUNNERS` (consistency); monthly businesses rebuild timer (fail-safe chain) |
| Tests | ✅ **374 passed, 5 skipped** | +20 new (13 cwwp2 + 4 digest + 3 fsq) |

## Review + commit — DONE
- Adversarial code-review workflow (3 reviewers → verify): **5 findings, all confirmed + FIXED**:
  1. [HIGH] cwwp2 `_point_wkt` published invented null-island/out-of-US geometry (geom_wkt rows bypass gate2) → now validated in-parser via `_in_any_us_box` (drops to None).
  2. [MED] weekly_digest Telegram `parse_mode=Markdown` 400'd on underscores → plain-text + honest truncation + non-zero exit on delivery failure.
  3. [LOW] cwwp2 `active` was False for missing status → tri-state None (unknown, never fabricated "no").
  4. [LOW] digest silent 4096 truncation → marker + full body to ntfy.
  5. [LOW] attention-list double-count (breaker+failing) → single surfaced set.
- **Committed `eb445f9`** — whole Phase 2 (prev-session wave-2 WIP + all new work). Tests: **379 passed, 5 skipped**.

## Remaining (data backfill — gated on OSM extract, resource-serialized)
- [ ] OSM US extract finish (watcher notifies) → verify US osm.* counts (ways + fuel/rest/weigh) + run WAYS pass.
- [ ] Full US Overture+FSQ+conflate backfill (post-OSM) → US-wide /v1/places (currently bounded NYC proof).
- [ ] Final tracker + MASTER_PLAN §10 note.

## Known follow-up (pre-existing, flagged not fixed — out of Phase-2 scope)
- wzdx.py + nws.py `_geom_wkt` have the SAME gate2-bypass as the cwwp2 bug I fixed: LineString/Polygon geom_wkt rows skip coordinate validation. Central fix = teach gate2_coords to parse geom_wkt. Riskier (multi-vertex geometry) → separate change.

## Wait-items (human-gated — cannot complete autonomously)
- Keyed state 511 feeds (API keys + DAA); TPIMS registration; ~20 WZDx feeds awaiting license review; HF_TOKEN for FSQ (worked around via source.coop mirror).

## Log
- 00:00 — resumed; stabilized OSM extract (killed orphan double-writer, reaped stale rows); wrote tracker.
- ~00:40 — built weekly digest (D6). Smoke-tested green.
- ~01:00 — built Caltrans CWWP2 511 adapter (F2): parser + 3 district YAMLs + /v1/live/chain-controls; 565 rows ingested; endpoint verified.
- ~01:20 — businesses conflate → core.businesses=2981; /v1/places live; fixed FSQ-mirror glob bug + verified.
- ~01:35 — wiring: runner entries + monthly businesses timer + deploy README. 374 tests green.

---

# Session 2 — 2026-07-23 06:00 IST onward (backfill completion)

Mandate re-confirmed by Boss: *"previous work resume kro /goal — until you finish whole phase do not stop."*

## What I found on resume (measured, not assumed)

| Check | Result |
|---|---|
| jarvis-core daemon | up, goal queue empty (no in-flight goal to resume) |
| DB row counts | bridges 629,710 · parking 1,915 · tunnels 580 · live_events 6,354 · fuel_prices 17,078 · businesses 2,981 |
| `osm.ways` | **109,777 — still Delaware-only.** US ways pass did NOT land. |
| `osm.fuel_stations` / `rest_areas` / `weigh_points` | **108,056 / 5,452 / 3,773 — US-wide POI pass SUCCEEDED.** |

**Root cause of the missing US ways** (from `data/us-osm-extract.log`, 05:41:15):
the osmium pass completed cleanly through 37.5M+ kept ways, then phase B died:

```
osm_extract --job ways failed: DiskFull: could not write block 3281 in
file "base/16384/711635" ... COPY ways_new, line 906282
```

Disk exhaustion from the *concurrent* POI node-cache (48 GB) and ways node-index
(~48 GB) living side by side — not from the table itself. Measured on Delaware:
476 B/row total relation size → 38M US ways ≈ **~20-30 GB**, comfortably inside
the 274 GB now free. The failure path then `rmtree`'d the workdir, so a clean
**3.4-hour pass was destroyed by a transient load-time error.**

## Work done this session

### 1. US ways pass relaunched (in flight)
`scripts/osm_ways_job.py --pbf data/pbf/us-latest.osm.pbf --keep-workdir`,
nothing else competing for the disk. `--keep-workdir` is the point: a phase-B
failure must never again cost the pass.

### 2. Phase B made independently replayable — `--from-spool` (NEW)
Loads an existing kept spool and skips the osmium pass entirely; recovery drops
from ~4 hours to minutes. A resumed run:
- gets its own audited `ops.source_runs` row, marked `resumed=` in the message;
- reports phase-A counters as `None`, never fabricated as `0`;
- **never deletes a workdir it was handed** (`_cleanup_workdir`) — deleting
  someone else's preserved pass on a transient failure is exactly the loss this
  path exists to prevent.

### 3. Disk-headroom guard before the swap — `check_load_headroom()` (NEW)
Refuses phase B up front when the DB volume cannot plausibly hold
heap+indexes+WAL (~12× the gzip spool; ratio measured on Delaware: 9.79 MB
spool → 50 MB relation = 5.4×, plus ~4.3× transient WAL). The error message
carries the exact `--from-spool` replay command. Opt out via
`TRUCKINTEL_DB_VOLUME_PATH=`; retune via `TRUCKINTEL_LOAD_SIZE_FACTOR`. Skips
are **printed, never silent**.

### 4. Closed the gate-2 geometry bypass (the flagged pre-existing follow-up)
`loaders.py` accepts either a `lat`/`lon` pair **or** a `geom_wkt` string, but
`gate2_coords` judged only the former — so every LineString/Polygon row (wzdx
work zones, nws alert polygons) reached `core` **unvalidated**. That is the
bypass through which the cwwp2 parser bug published null-island geometry.

- New `wkt_coords()` — type-agnostic vertex extraction (POINT/LINESTRING/
  POLYGON/MULTI\*/collections, Z & M ordinates ignored).
- New `_judge_coords()` — one verdict shared by the point and geometry paths,
  so ordering stays identical (`out_of_range` → in-US → swap → not-in-US).
- Multi-vertex rule: **every** vertex must be in range and off null island;
  **at least one** must be in a US box (a work zone or alert polygon may
  legitimately cross into Canada/Mexico/offshore); swap detection stays
  all-or-nothing. Unparseable WKT → `geom_unparseable`, never guessed.

**Verified against real production data, not just unit tests:** replayed every
cached raw payload through parser → gate — **2,180 NWS rows + 13,710 WZDx rows,
zero rejects.** The offshore-marine-polygon regression I was worried about does
not materialise; the residual case (an alert lying wholly beyond the boxes)
would land in `quality.rejects` with a reason, visibly, not be dropped. Pinned
as a skip-if-absent regression test.

### 5. Tests
- `tests/test_osm_ways.py` +9 (spool resolution, line count, headroom guard
  raise/pass/skip/env-override, no-delete-handed-in-spool, full `--from-spool`
  replay against the DB) → **66 passed**.
- `tests/test_validate.py` +25 (WKT parse table, geometry gate rules, ordering
  parity, real-cached-payload sweep) → **37 passed**.

One test-design error caught and corrected by the suite itself: I had expected
`latlon_swapped` for a vertex with |lat| > 90, but the out-of-range check
correctly fires first — matching the long-standing point-path ordering. Fixture
fixed; ordering parity now pinned by its own test.

## Remaining to close Phase 2
- [ ] US ways pass completes → verify `osm.ways` US counts + class allow-list
- [ ] Full US Overture + FSQ pull + conflate (serialized AFTER the OSM pass —
      concurrent heavy IO is what broke the last run)
- [ ] Full suite + endpoint smoke tests
- [ ] Commit; update MASTER_PLAN §10 + memory

## Log
- 06:17 — relaunched US ways pass with `--keep-workdir` (PID 1650501).
- 06:20-06:45 — built `--from-spool` + headroom guard + tests; closed gate-2
  geometry bypass + tests; verified gate against 15,890 real cached rows.

## Risk identified for the next step — full-US conflate is UNPROVEN at scale

`run_conflate()` is global (no bbox scoping) and holds several structures in
RAM on a 15 GB box that also runs Postgres:

| Structure | Bound | Note |
|---|---|---|
| `pairs` list | pairs scoring **≥ 0.85** | pruned by the merge threshold — the smallest of these |
| `gray_o` / `gray_f` sets | pairs scoring 0.55–0.85 | unbounded by any threshold |
| `used_o` / `used_f`, `merges` | ≤ `pairs` | |
| **`gray_params = {"gray_o": sorted(gray_o), …}`** | **full gray id set as a single SQL array parameter** | **likeliest failure point** |

The bounded NYC proof (`core.businesses = 2,981`) pulled **Overture only**, so
the cross-source pairing path has **never actually been exercised at volume** —
calling it "proven" would be wrong.

**Decision gate (measure, don't guess):** after the pulls land, count
`_PAIRS_SQL` bucketed by score band.
- Combined pairs + gray ids **< ~5M** → run `--conflate` as-is.
- Otherwise → spill first: gray ids into a TEMP TABLE instead of an array
  parameter, and an external sort for `pairs`, preserving `score_from()`
  semantics exactly.

This is deliberately NOT pre-optimised — the thresholds may well prune enough,
and rewriting proven scoring logic on a guess is how correctness gets lost.
