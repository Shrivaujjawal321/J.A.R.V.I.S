Recon complete. All items measured.

## 1. Schemas (all columns verified via `\d`)

**Shared envelope** — every `core.*` and `osm.*` table carries the identical honesty tail: `source_id, run_id, ingested_at, observed_at, confidence, conf_trust, conf_fresh, conf_complete, conf_agree, flags text[], props jsonb`. The honesty contract is structurally enforced, not aspirational.

| Table | Distinctive columns |
|---|---|
| `osm.ways` | `way_id bigint PK, highway NOT NULL, name, ref, maxheight_in, maxweight_lb, hgv, oneway, maxlength_in, maxwidth_in, bridge bool, tunnel bool, geom LineString/4326`. Indexes: PK, GiST(geom), btree(highway) |
| `core.businesses` | `business_id PK, name, category NOT NULL, brand, lat, lon, geom Point, address, city, state char(2), zip, address_norm, phone, website, present_in text[], def, search_tsv GENERATED`. Indexes: PK, btree(category,state), GiST(geom), GIN(name trgm), GIN(tsv) |
| `core.parking_sites` | `site_id PK, kind, name, state, truck_spaces smallint, geom Point` |
| `osm.fuel_stations` | `osm_id PK, name, brand, state, has_diesel, hgv_access, has_def, geom Point` |
| `osm.rest_areas` / `osm.weigh_points` | `osm_id PK, name, state, geom Point` (nothing else) |
| `quality.conflicts` | `conflict_id, entity_type, entity_id, field, value_a/source_a, value_b/source_b, delta, status, opened_at, closed_at` |
| `ops.sources` | `source_id PK, name, owner, url, kind, load_pattern, schedule_minutes, slo_hours, license, attribution_text, gates jsonb, auth jsonb, enabled, verify_status, authority_class, base_trust, trust, parser, target` |
| `ops.source_runs` | `run_id identity, source_id FK, started_at, finished_at, status, rows_in, rows_published, rows_rejected, message, raw_sha256, http_status` |

Three constraints bind any design: `businesses_category_taxonomy` (closed 29-value CHECK — `truck_repair`, `mobile_repair`, `trailer_repair`, `towing`, `tire_service`, `truck_parts`, `truck_wash` already exist as legal values), `businesses_present_in_permissive` (`<@ ARRAY['overture','fsq']` — ODbL firewall), `businesses_def_inferred_only`.

## 2. `osm.ways.ref` — the only route-ish identifier

```
 total_ways | ways_with_ref | ways_ref_null | distinct_refs | ways_with_name | distinct_names
     109777 |          7501 |        102276 |           207 |          41362 |          18610
```

**Only 6.8% of ways carry a `ref`.** 207 distinct refs, all Delaware-scoped (`US 13`, `DE 1`, `I 95`, `DE 1 Toll`, `US 13 Business`). 863 ways use OSM's `;` concurrency notation across 61 distinct multi-refs (`US 9;DE 404`, `I 95;US 202`) — an exact-match `WHERE ref='I 95'` silently drops these.

Highway class distribution (with_ref / no_ref / total):
```
 service        |    1 | 65511 | 65512     trunk_link     |   46 | 1307 | 1353
 residential    |   15 | 26734 | 26749     motorway       |  776 |   21 |  797
 tertiary       |   46 |  4209 |  4255     motorway_link  |   36 |  614 |  650
 primary        | 2761 |   289 |  3050     primary_link   |   17 |  585 |  602
 trunk          | 2476 |    57 |  2533     tertiary_link  |    2 |  265 |  267
 secondary      | 1314 |  1121 |  2435     secondary_link |    9 |  180 |  189
 unclassified   |    2 |  1383 |  1385
```
Refs concentrate exactly where expected: motorway 97.4%, trunk 97.7%, primary 90.5%. **60% of the table is `service` roads** (parking aisles/driveways) — noise for routing, but note those are precisely the geometries that sit *inside* truck-stop and repair-yard parcels.

## 3. Topology — ways ARE noded; fragmentation is structural, not gaps

Endpoint test on `I 95`: **274 endpoints → 139 distinct**, i.e. 135 shared. Endpoints touch exactly (bitwise-identical coords), so PostGIS merges them.

`ST_LineMerge(ST_Union(geom))` per ref returns MULTILINESTRING every time:
```
 US 13  | 936 ways | 29 parts      I 95   | 137 ways | 10 parts
 DE 1   | 346 ways |  8 parts      US 113 | 103 ways |  6 parts
 DE 9   | 215 ways | 25 parts      I 495  |  90 ways |  2 parts
```
Splitting `ref` on `;` and grouping by token materially improves this:
```
 ref_token | n_ways | parts | miles      (before → after)
 I 95      |   186  |   8   |  51.2      137 ways/10 parts/41 mi
 US 13     |  1140  |  20   | 207.1      936 ways/29 parts/177 mi
 DE 1      |   388  |   4   | 137.7      346 ways/ 8 parts/130 mi
 US 40     |   373  |   3   |  34.1
```
**The decisive measurement** — gap between every I-95 merged part and its nearest sibling:
```
 part | miles | gap_to_nearest_part_m
    7 | 22.06 |                   0.0
    8 | 21.86 |                   0.0
    1 |  1.39 |                   0.0
 ... (all 8 parts)         all 0.0
```
Every gap is **0.0 m**. There are no real discontinuities. The 2 large parts (22.06 + 21.86 mi) are the two carriageways — all I-95 ways are `oneway=yes`, and Delaware I-95 is ~23 mi, so this is exactly correct. The 6 remaining ~1-mile stubs are junction branches where degree ≥3 forces `ST_LineMerge` to stop.

Implications: buffering/`ST_DWithin` needs no contiguity and works today. `ST_LineLocatePoint` (required for "nearest route point" / "travel direction") requires a single LINESTRING — verified it works per-part (`ST_GeometryN(g,1)` returned a valid fraction) but **not** across a MULTILINESTRING, and dual carriageways mean direction must be modeled per-carriageway, never per-ref.

## 4. `core.businesses`

Category distribution — the headline gap:
```
 restaurant 1093 | cafe 628 | atm_bank 362 | grocery 265 | hotel 220 | pharmacy 144
 fast_food 126 | medical 55 | laundry 53 | fuel_station 25
 towing 6 | truck_repair 1 | tire_service 1 | motel 1 | truck_dealer 1
```
**Truck-service rows total 9.** `present_in` is `{overture}` for all 2,981 (FSQ never loaded). `source_id` = `businesses_conflate` for all. States: NY 2543, NJ 437, FL 1.

Fill rates /2981: `brand` 411 (13.8%), `address` 2931 (98.3%), `city` 2975, `state` 2981 (100%), `zip` 2921 (98%), `phone` 2064 (69.2%), `website` 2098 (70.4%), `observed_at`/`confidence` 2981, `props` non-empty 2981, `flags` non-empty 6. **`address_norm` = 0/2981 and `def` = 0/2981 — declared but never populated.**

`props` is a per-source nested envelope, `props->'overture'->{...}`, preserving `source_record_id`, `release`, `src_confidence`, `category_source` (raw Overture string: `towing_service`, `tire_shop`, `truck_repair`), plus lat/lon/zip/city/name/brand/phone/state/address/website/observed_at. **No hours, no email, no socials** — Overture's schema carries `socials`/`emails` but the staging table has no column for them, so they're dropped at ingest.

## 5. `ops.sources` (22) + last run status

All 22 enabled+`verify_status=verified` (3 are `_test_*`, disabled). Licenses are clean and free: NBI/NTAD/NTI/NWS "US public domain", Overture `CDLA-Permissive-2.0`, FSQ `Apache-2.0`, WZDx/Caltrans state open data "keyless public JSON".

```
 businesses_conflate   | success  2981 published
 caltrans_cwwp2_cc_d02/03/09 | success  208/230/127
 eia_diesel            | skipped_no_key   "EIA_API_KEY is not set"
 fsq_places            | FAILED
 nbi_annual            | success  631301 in → 629710 pub, 1591 rejected
 ntad_parking          | success  1915
 nti_tunnels           | skipped_unchanged  "payload hash unchanged"
 nws_alerts            | success  541
 osm_pois              | success  117281 published, pbf=us-latest.osm.pbf
 osm_ways              | RUNNING (stale)
 overture_places       | FAILED
 quality_nightly/rescore | success
 wzdx_az/ks/mn/wa      | success  3439 / 466 / 643 / 564 (25 rejected)
```

**Both failures are fixable and neither is a legal blocker:**
- `overture_places`: `IO Error: Could not resolve hostname ... overturemaps-us-west-2.s3.us-west-2.amazonaws.com/release/2026-07-22.0/...` — DNS/network, not licensing.
- `fsq_places`: `Invalid Input Error: Globs ('*') for generic HTTP file is are not supported. Consider 'SET allow_asterisks_in_http_paths = true;'` — DuckDB config; the error states its own fix.

**Two findings that matter more than the failures:**

(a) **5 zombie `osm_ways` runs stuck in `status='running'`** — run_ids 1238, 1261, 1292, 1293, 1333, ages 6h22m / 5h48m / 3h27m / 3h26m / 31m, all `finished_at IS NULL`. `ps aux` shows **no live process**; `systemctl --user list-timers` shows **no truck/osm timers**. This confirms the ground truth that the backfill is dead, and it violates the repo rule that every fetch writes one terminal run row — these are neither success nor failure. Published rows carry FKs to runs that never completed.

(b) A prior `overture_places` success reads: `staging.overture_places=0; unmapped_categories_excluded=286777`. **286,777 Overture places were silently discarded for having categories outside the taxonomy allow-list.** The latest success reads `staging.overture_places=3000; bbox=custom; max_rows=3000` — a hard 3000-row cap. `staging.overture_places` = exactly 3000 rows, `staging.fsq_places` = 0. Conflate log: `overture_in=3000, fsq_in=0, merged=0, cell_collision_drops=19`. The 2,981 businesses are a capped proof sample, and the category allow-list — not data availability — is the binding constraint on repair-shop discovery.

## 6. Routes — conclusively refuted

`information_schema.tables` returns 58 objects; none is a route. I also checked the object classes that `information_schema` **omits**:
```
SELECT * FROM pg_matviews;                          → 0 rows
relkind IN ('m','v','f','p') outside pg_catalog     → only public.geography_columns, public.geometry_columns (PostGIS views)
table_name ~* 'route|corridor|highway|segment|path|itiner'   → 0 rows
column_name ~* 'route|corridor' (all schemas)       → 0 rows
```
**Zero materialized views, zero foreign/partitioned tables, and no column anywhere named route/corridor.** The only route-shaped asset in the database is `osm.ways.ref`.

Also: the entire **`tiger` schema is empty** — `tiger.edges`, `county`, `zcta5`, `state`, `featnames`, `place` all **0 rows**. It's unpopulated `postgis_tiger_geocoder` scaffolding, so there is no working geocoder and no TIGER route/county/ZIP source loaded today (though TIGER is free public-domain and would be the natural County/ZIP source).

## 7. Headroom — ample

```
/dev/sda2  468G  191G used  254G avail  43%
Mem: 15 GB total, 4 used, 12 buff/cache, 11 available;  Swap 3 GB
nproc: 4
db_size: 1811 MB
```
Largest tables: `core.bridges` 1623 MB, `osm.ways` 50 MB, `osm.fuel_stations` 45 MB, `core.live_events` 20 MB, `quality.rejects` 11 MB, `core.businesses` 5.3 MB. 254 GB free against a 1.8 GB DB — disk is a non-issue; 4 cores / 15 GB RAM is the real constraint for a national OSM PBF pass.

## Corrections and cross-checks against the brief

- **OSM POI tables are NATIONAL, not Delaware.** Only `osm.ways` is Delaware-bboxed. Measured extents: `fuel` lon −177.20..−67.00 / lat 19.06..71.30 (51 distinct states), `rest` −166.52..−67.02, `weigh` −151.64..−67.84, vs `ways` −75.85..−75.05 / 38.40..39.87. `osm_pois` published 117,281 = 108,056+5,452+3,773 exactly, from `us-latest.osm.pbf`.
- **`core.businesses` is far smaller in footprint than "NYC/NJ"**: extent is `BOX(-74.0499 40.7006, -73.9915 40.8490)` — roughly a 5 km × 16 km sliver (Manhattan/Jersey City/Little Ferry).
- **The two datasets do not overlap at all**: `ST_Intersects` of the two extents = **`f`**, separated by ~90 km. A route-buffer join of businesses against ways returns **zero rows today** — the requested pipeline cannot be demonstrated end-to-end on current data. (The exhaustive `ST_DWithin` cross-join timed out at 120 s; the extent test is the cheap conclusive proof.)
- All ground-truth row counts reproduced exactly (629,710 / 1,915 / 580 / 2,981 / 109,777 / 108,056 / 5,452 / 3,773), including "exactly 1 row category='truck_repair'".

## Field-availability evidence for the enrichment task

OSM tag coverage measured on the 108,056 national fuel stations — the best available proxy for what OSM will yield for repair shops:
```
 name 78.99% | brand 68.94% | addr:street 32.83% | addr:housenumber 31.88%
 addr:city 30.76% | addr:postcode 30.61% | addr:state 29.52% | website 17.41%
 opening_hours 8.49% | phone 8.39% | hgv 4.40% | contact:website 244 rows
 contact:phone 164 | contact:facebook 67 | email 31 (0.03%) | contact:instagram 16
```
`props` preserves **raw OSM tags verbatim** (`opening_hours: "24/7"`, `addr:*`, `brand:wikidata`, `compressed_air`), which is the working model for storing the requested per-shop fields. Grep for `whats` across all tag keys returned **zero** — there is no WhatsApp tag in OSM.

Structured column fill on those national POIs is much worse than the raw tags: `has_diesel` 7,981 (7.4%), `hgv_access` 4,939 (4.6%), **`has_def` 92 (0.09%)**, `state` 31,875 (29.5%); `rest_areas.state` 541/5,452 (9.9%); `weigh_points.state` 45/3,773 (1.2%). The `state` column is effectively unusable as a filter today — relevant because the requested output keys on state/county.

`quality.conflicts` holds 723 rows, **all** `entity_type=bridges, field=posting_status_vs_clearance, status=open` — no business/POI conflict detection exists yet. `quality.rejects`: `nbi_annual missing_required:lon` 1872, `missing_required:lat` 1762, `coords_not_in_us` 187, `wzdx_wa duplicate_natural_key` 25.

**Bottom line for design:** routes must be built (ref-token expansion over `osm.ways` is the only in-DB path, and it works — geometry is fully noded with 0.0 m gaps, but yields per-carriageway MULTILINESTRINGs, so linear referencing must be per-part); the national OSM POI ingest already proves the country-scale path works; `core.businesses` is a 3000-row capped sample whose truck content is 9 rows; the ODbL firewall (`present_in <@ ARRAY['overture','fsq']`) means OSM-derived repair shops cannot legally land in `core.businesses` under the existing ruling and must stay in `osm.*` joined at query time.