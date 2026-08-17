# truck-intel — Truck-Route Mechanic Layer: Definitive Research Brief

**Status:** Phase 1 output. This is the artifact the builder implements from.
**Date:** 2026-07-23. Every count and quote below was pulled on the wire or measured on the live DB on 2026-07-22/23 unless explicitly tagged `[UNVERIFIED]`.
**Supersedes:** all eight research lanes and their verifications in `_salvage/`. Where a verification refuted a lane, the verification's fact is carried here and the refuted claim is not repeated.

---

## 1. Bottom line up front

1. **There is no routes table, anywhere.** `information_schema` returns 58 objects; zero matviews; no column anywhere named route/corridor. Every route-relative field in the spec is uncomputable today. This is the single blocking dependency.
2. **A free, public-domain, truck-designated national route layer exists and is a drop-in for the repo's existing `kind: arcgis` connector.** BTS/FHWA NTAD **National Network** — 478,999 polylines, of which **453,529 carry `NN=1`** (on the STAA National Network under 23 CFR 658). It is truck-legal status *as a matter of law*, not a filter applied afterwards. This is exactly what the owner asked for.
3. **The biggest single risk is publishing the 24,169 `NN=0` rows as truck routes.** They ship in the same layer and are *not* on the National Network. A naive `where=1=1` ingest publishes a lie.
4. **Second-biggest risk, and it is live today: the `osm.*` mirrors are already ODbL Derivative Databases being Publicly Used with no §4.6 offer and no licence recorded in `ops.sources`.** `/v1/fuel` serves 108,056 systematically-extracted OSM rows; `ops.sources.license` for `osm_pois`/`osm_ways` is `NULL`, so `/v1/meta` reports the platform's only share-alike source as "unknown". That is simultaneously a licence defect and a violation of the repo's own honesty rule.
5. **The shop layer is buildable, permissively, at ~11k truck-specific rows nationally.** Overture Places US-bbox `truck_repair` = 10,858 (+140 `trailer_repair`), with phone 99.2% / website 70.3% / email 60.4% / socials 82.1% / ZIP 99.4%. Overture Places is empirically OSM-free (unnest of `sources[]` over a live parquet part: zero `osm` rows), so the permissive path is also the *better* path — OSM has only ~700 truck shops in the whole country.
6. **Ratings, review counts, review summaries and photos cannot be filled legally, free or paid.** Google blocks it by four independent contract clauses including an outright ban on using the Services "in a listings or directory service"; Yelp is now paid, 24-hour-capped, and forbids building a listings DB. The honest outcome is a generated `https://www.google.com/maps/search/?api=1&query=…` hyperlink that hands the question to the human.
7. **Operating hours are ~15% coverage, ceiling.** Overture has no hours field (confirmed in `place.yaml`), FSQ has none, website JSON-LD yields ~3% end-to-end. Only OSM (16.2% on `shop=truck_repair`) and AllThePlaces (chains only) carry hours — and taking OSM hours to fill gaps where ATP is silent makes that property *mixed* and triggers share-alike.
8. **The existing confidence score must not ship as-is.** It takes only 8 distinct values across all 2,981 rows (60/63/65/68/70/73/75/78) because T is pinned at 0.65, A is pinned at 0.5 and F≈1.0. A Philippine towing listing force-labelled `state='NY'` scores 73, one point above the table average.
9. **Classification is a solved problem with measured precision, but two signals in the original spec do not exist.** `service:vehicle:truck` and `service:vehicle:hgv` have taginfo total = 0 worldwide; `hgv=*` is a *road access* tag (98.3% on ways) and is a category error as a POI signal. The real key is `service:vehicle:truck_repair`, and 446 of its 529 US uses sit on `shop=car_repair` — the exact "car garage that also services HCV" the inclusion rule wants.
10. **Runtime is minutes, not hours — but only with one index.** A functional GIST on `(geom::geography)` takes a national buffer query from 4,321 ms to 18 ms (240×). Without it the same national job is a multi-hour disaster. The three prior full-US OSM ways loads died on DiskFull; that failure mode does not recur here because the route spine is 453,529 rows (~a few hundred MB), not 60M residential ways.

---

## 2. The routes problem

### 2.0 Ground truth

There is **no routes table**. Measured on the live DB:

```
information_schema.tables                                     → 58 objects, none a route
pg_matviews                                                   → 0 rows
relkind IN ('m','v','f','p') outside pg_catalog               → only PostGIS's geography_columns/geometry_columns
table_name ~* 'route|corridor|highway|segment|path|itiner'    → 0 rows
column_name ~* 'route|corridor' (all schemas)                 → 0 rows
```

The only route-shaped asset in the database is `osm.ways.ref` — 7,501 of 109,777 rows (6.8%), 207 distinct refs, **Delaware only**. The `tiger` schema exists but every table is empty (`tiger.edges`, `county`, `zcta5`, `state`, `place` all 0 rows) — unpopulated `postgis_tiger_geocoder` scaffolding.

`osm.ways` is also explicitly ruled out as a spine by the repo itself (`scripts/osm_ways_job.py:6-7`): *"osm.ways is the conflation substrate for NBI→OSM matching — NOT a routing graph."*

### 2.1 The owner's rule, restated as a design constraint

> Truck-designated routes only. The route spine is the truck network **as a matter of law**, not a filter applied afterwards.

There is exactly one free national dataset that satisfies this literally. The **National Network** was authorized by the Surface Transportation Assistance Act of 1982 (P.L. 97-424) and is specified in **23 CFR 658 Appendix A**, which requires states to allow conventional combinations (102-inch width, 48-ft minimum semitrailer, 80,000 lb GVW) on the listed highways. eCFR verified live: <https://www.ecfr.gov/current/title-23/chapter-I/subchapter-G/part-658> (714,657 bytes; title reads "Truck Size and Weight, Route Designations"; "National Network" appears 39×, "48 feet" 11×, "102 inches" 9×). Appendix A is *prose*, not GIS — the NTAD layer is FHWA's GIS rendering of it.

**Do not confuse the National Network (NN) with the National Highway Freight Network (NHFN).** NHFN is a *funding* network under 23 U.S.C. 167 (where federal freight money goes, 12,989 polylines). NN is the *truck-access* network under 23 CFR 658. This is the single most common conflation in this domain, and the earlier lane-4 recommendation to build on NHFN is **corrected here**.

### 2.2 Option A — NN spine, segment grain, NTAD-only

**What.** `core.truck_routes` = the 453,529 `NN=1` rows from
`https://services.arcgis.com/xOi1kZaI0eWDREZv/arcgis/rest/services/NTAD_National_Network/FeatureServer` (layer 0, `esriGeometryPolyline`, EPSG:4326).

Verified counts (`returnCountOnly=true`, 2026-07-23): total **478,999** · `NN=1` **453,529** · `NN>0` **454,830** · `NN=0` **24,169** · distinct `ROUTEID` **12,491** · distinct `ID` **478,999** · Delaware (`STFIPS=10`) **472**.
Route-type mix on `NN>0`: Interstate 73,828 · US route 164,660 · State route 212,338 · C 843 · F 289 · N 215 · O 181 · M 21 · R 17 · E 6 · T 2. I-95 alone is 2,926 segments.
Fields: `OBJECTID, ID, VERSION, YEAR, STFIPS, CTFIPS, ROUTEID, BEGINPOINT, ENDPOINT, SIGN1, SIGNT1, SIGNN1, LNAME, NN, FCLASS, FACILITYT, OWNERSHIP, URBANCODE, AADT, AADT_COM, AADT_SINGL, FUT_AADT, FUT_YEAR, THROUGH_LA`.

**Why.** It is the only free source encoding truck *legality*. It is unambiguous public domain (`copyrightText`, read verbatim: *"This NTAD dataset is a work of the United States government as defined in 17 U.S.C. § 101 and as such are not protected by any U.S. copyrights. This work is available for unrestricted public use."*), so `core.*` stays ODbL-clean and the existing §3.1-4a ruling survives untouched. It carries `CTFIPS` (county FIPS) on every segment — which fills the "District" field with zero extra joins — and `AADT_COM`, commercial-vehicle AADT per segment, which NHFN does not have and which is the correct way to prioritise enrichment spend.

**Tradeoff.** Geometry is old: the service description says *"as of December 22, 2020"* but every row carries `VERSION='2020.01.10'` and `YEAR=2018` as a **single distinct value across all 478,999 rows**. The honest `observed_at` is therefore **2018**, not 2020-12-22 (correction to lane 1). It has no direction field, no truck restrictions, and `LNAME` is blank on 411,754 of 454,830 rows.

**Effort.** Low. `kind: arcgis` + `load_pattern: snapshot_swap` + one parser. The engine's `_fetch_arcgis` already pages ArcGIS. ~228 pages at `maxRecordCount=2000`.

**Unlocks.** `route_id`, `route_name`, `distance_from_route`, `nearest_route_point`, county assignment, truck-volume prioritisation, per-corridor coverage reporting. Everything except direction, restrictions and junctions.

### 2.3 Option B — NN spine + NHS geometry refresh + FAF5 restriction/direction overlay

**What.** Option A, plus two auxiliary tables:
- `core.route_geometry_nhs` from `NTAD_National_Highway_System` — **492,005** rows, `copyrightText` verified: *"The NHS Version 2025.08.08 database … can be freely distributed as long as this metadata entry is included with each distribution."* Five years fresher geometry than NN. Adds `SPEED_LIMI` and the NHS Intermodal Connector fields (`FACID/CONNID/CONNDES/CONNMILES`) — the literal last-mile truck links to ports, rail yards and airports.
- `core.route_restrictions` from `NTAD_Freight_Analysis_Framework_Network_Links` — **487,394** links. `Truck IS NOT NULL` = **4,365**, exactly {Prohibited 3,519, Restrictions 718, Reserved 128}; the other **483,029 are NULL**. `DIR` exists on all rows but `DIR=0` on 168,215 (34.5%), `DIR=1` on 318,788, `DIR=-1` on 391 — so FAF5 gives usable directionality on roughly two thirds of links, not all.

**Why.** Fixes Option A's two real weaknesses — stale geometry and total absence of restriction/direction — while keeping truck-legality authority in NN. This is the only free national source with an explicit per-link truck-restriction attribute.

**Tradeoff.** Three vintages that must each carry their own `observed_at` and can visibly disagree: NN 2018 · NHS 2025-08-08 · FAF5 2017 base year, published 2022-04-11. **The ID spaces do not join.** NN `ROUTEID` is a state-scoped LRS key, NHFN `ROUTEID` is an HPMS-style opaque key (`1000000X000`), FAF5 `ID` is FAF-internal. Reconciliation must be spatial (`ST_DWithin` + `ST_LineLocatePoint`), which is real work and introduces its own match error that must carry its own confidence. And `Truck IS NULL` on 99.1% of FAF5 links must render as **unknown**, never "no restriction" — rendering it as "no" would be actively dangerous advice to a driver.

**Effort.** Medium-high. Three registry entries + a spatial reconciliation job. This is the right *target state*, not the right first commit.

**Unlocks.** Everything Option A unlocks, plus `travel_direction` on ~2/3 of links, truck-prohibited segments as positive facts, and a currency cross-check that can flag NN segments with no NHS counterpart as possibly superseded.

### 2.4 Option C — NHFN-only, ship-today scaffold

**What.** `core.truck_routes` = the **12,989** NHFN rows.
`copyrightText` verified: *"The NHFN Version 2023.02.08 database, or any portion thereof, can be freely distributed as long as this metadata entry is included with each distribution. The original metadata entry cannot be modified or deleted from any data transfer."* Compiled 2023-01-27 → `observed_at = 2023-01-27`. Carries `ST_NAME` (human-readable state) and `BEGMP/ENDMP` mileposts, which NN lacks.

**Why.** A full national pull is ~7 paged requests and completes in seconds. It proves the entire buffer→enrich→serve pipeline end-to-end today, on a 2023 vintage, with a clean licence.

**Tradeoff.** It is the **wrong network for the owner's stated mandate** — freight funding, not truck access. 12,989 segments vs 453,529. A mechanic shop on a state-route truck corridor simply will not be found. Do **not** ship this to users labelled "US truck routes."

**Effort.** Minimal.

**Unlocks.** Pipeline validation only. Treat as scaffolding, then swap the spine to NN.

### 2.5 The two traps that must be handled whichever option is chosen

**Trap 1 — the `NN=0` rows.** 24,169 of 478,999 rows are carried in the National Network file but are **not on** the National Network. Set the registry query filter to `NN>0` (or `NN=1` if the owner wants the strictest reading — the 1,301-row difference is the non-`1` positive codes 3/4/5/6/7). Set `gates.min_rows` around **440,000** so a truncated pull fails loudly rather than publishing half a network.

**Trap 2 — `ROUTEID` is not a primary key, and neither is the obvious composite.**
- `ROUTEID` is state-scoped and repeats across states — observed literal values `'1'`, `'H3'`, `'93'`. 12,491 distinct values across 478,999 rows.
- The composite proposed by lane 1, `(STFIPS, ROUTEID, BEGINPOINT, ENDPOINT)`, is **also not unique** — verification found `ID` 444801 and 444802 genuinely colliding on it.
- `ID` **is** unique: distinct `ID` = 478,999 = the row count.

→ **Use `ID` as the natural key** (`route_segment_id TEXT PRIMARY KEY`, stamped from the source `ID`), and keep `STFIPS`/`ROUTEID`/`BEGINPOINT`/`ENDPOINT` as ordinary columns for LRS referencing. Register it in `engine._DEDUP_KEY_BY_TARGET` so gate 3 actually fires; without that entry gate 3 silently no-ops.

**Trap 3 — `LNAME` is blank.** 411,754 rows blank, 43,076 non-blank. Route names must be **synthesized**: `TRIM(SIGN1)` first (observed leading whitespace, `' I1'`), then `SIGNT1 + '-' + SIGNN1` with the type code expanded (I→Interstate, U→US, S→State). Store raw `SIGN1/SIGNT1/SIGNN1` alongside so the derivation is auditable.

**Trap 4 — take NN only from the `NTAD_`-prefixed service.** The catalog (1,023 services) also contains an unprefixed `National_Network` mirror with the same 478,999 count and **empty `copyrightText`**, plus `NN` and `nn_conv_comb_trucks_2025_v1` which expose **zero layers** (not a 2025 refresh — do not be fooled by the name).

### 2.6 The honest limit on the whole route layer

The service description carries its own disclaimer, verbatim:

> *"This file is a geospatial representation of the National Network as described in 23 CFR 658 Appendix A and **should not be interpreted as the official National Network and should not be used for truck size and weight enforcement purposes or for navigation.**"*

Lineage (ISO metadata, Process Step): built from **HPMS 2018** + Federal-aid Primary v2 + the 23 CFR 658 Appendix A text. FHWA on HPMS itself: *"The geodetic accuracy and topological structure of the linework have not been evaluated. Use of these data for navigation is not recommended. The user assumes the risk."* (<https://www.fhwa.dot.gov/policyinformation/hpms/shapefiles.cfm>)

**Consequences the product must honour:**
- The honest sentence is *"On the federal National Network representation (23 CFR 658, BTS NTAD, geometry vintage 2018)."* **Never** *"legal truck route"* or *"enforcement-grade."*
- It is cartographic linework, **not routable**. Buffer/nearest-point is fine; turn-by-turn is not.
- **An authoritative, legally-operative truck-route designation cannot be obtained free at national scale.** The operative law for truck access is state-designated truck routes under each state's own code, and there is no free national compilation — they are ~50 uneven state DOT GIS layers, some unpublished, none harmonised. Caltrans, the largest freight state, publishes **zero** STAA/truck-route datasets across its full 66-dataset DCAT catalog, and its road network is CC-BY-4.0 rather than public domain. NN at `NN=1` is the best free national proxy that exists, and it *is* a legal designation — but it is a 2020 federal representation of 2018 geometry, not a live determination.

### 2.7 What is explicitly rejected as a spine

| Rejected | Measured reason |
|---|---|
| **OSM ways / OSM route relations** | ODbL share-alike; only 975 `network=US:I` route relations nationally; `overpass-api.de/robots.txt` reads `Disallow: /api/` — the exact path — and the repo's robots rule is non-negotiable; OSMF API policy pushes bulk users to planet/Geofabrik. |
| **Overture Transportation theme** | `docs.overturemaps.org/attribution/` shows *"Transportation — License for theme: ODbL"*. It is the obvious-looking choice and it silently imports share-alike into the very join the owner wants to publish. |
| **HPMS 2023 FeatureServer** (6,039,201 rows) | `serviceDescription`, `copyrightText` and `description` are **all empty** — the service asserts no licence — and layer 0 is misnamed `HPMS_2023_Culverts_Web_Mercator` while carrying a roadway schema. Doubly untrustworthy. Also ~3,020 sequential pages. |
| **NHPN** (626,366 rows) | Compiled 2014-05-01. Twelve years stale — older than the NN spine. Its only unique asset is `SIGN2/SIGN3` route concurrency. |
| **USGS National Transportation Dataset** | *"supplemented with HERE road data"* — proprietary — and carries a per-feature `Distribution_Policy` attribute. **Not blanket public domain.** Neither prior lane flagged this. |
| **TIGER PRISECROADS / PRIMARYROADS** | Public domain and live (56 state files; national primaryroads 38,379,400 B), but **zero truck semantics**. Fine as a name-crosswalk (`FULLNAME` is populated) or cartographic base; publishing it as `core.truck_routes` would be the least honest option available. |
| **50-state DOT mosaic** | 50 discovery efforts, 50 licence reviews, 50 schema reconciliations, for a layer FHWA already publishes nationally in one request — and no guarantee the layer exists per state. |

---

## 3. Source ledger

### 3.1 Verified usable

| Source | URL | Licence | Attribution obligation | Access | Real rows | Fills |
|---|---|---|---|---|---|---|
| **NTAD National Network** | `services.arcgis.com/xOi1kZaI0eWDREZv/arcgis/rest/services/NTAD_National_Network/FeatureServer` | US Gov work, 17 U.S.C. §101, unrestricted public use (read from `copyrightText`) | *"Acknowledgment of the Federal Highway Administration (FHWA) and the Bureau of Transportation Statistics (BTS) [distributor]"* | keyless | 478,999 (NN=1 → 453,529) | route geometry, `route_id`, `SIGNT1/SIGNN1`→route_name, `CTFIPS`→county, `AADT_COM` |
| **NTAD NHFN** | `…/NTAD_National_Highway_Freight_Network/FeatureServer` | US Gov work | **Metadata entry must travel unmodified with every distribution** | keyless | 12,989 | freight-tier flag, `ST_NAME`, `BEGMP/ENDMP` |
| **NTAD NHS** | `…/NTAD_National_Highway_System/FeatureServer` | US Gov work | Same metadata-must-travel clause (v2025.08.08) | keyless | 492,005 | fresh geometry cross-check, speed limit, intermodal connectors |
| **NTAD FAF5 Network Links** | `…/NTAD_Freight_Analysis_Framework_Network_Links/FeatureServer` | US Gov work, unrestricted | FHWA/BTS ack | keyless | 487,394 (Truck non-null 4,365) | truck restrictions, `DIR`, lanes, free-flow time |
| **NTAD FAF5 Network Nodes** | `…/NTAD_Freight_Analysis_Framework_Network_Nodes/FeatureServer` | US Gov work (verified from item 8b8c2d53 metadata) | FHWA/BTS ack | keyless | 974,788 (Interchange 4,485 / Exit_Number 3,102) | **toll plazas only** — see §3.2 |
| **NTAD STRAHNET** | `…/NTAD_Strategic_Highway_Network/FeatureServer` | US Gov work | Cite STRAHNET explicitly (service reuses NHS metadata) | keyless | 97,118 | `is_strahnet` enrichment flag |
| **23 CFR 658 (eCFR)** | `ecfr.gov/current/title-23/chapter-I/subchapter-G/part-658` | US federal regulation, public domain | — | keyless | n/a | the **legal citation** for the route layer; spot-audit basis |
| **Overture Places** | `s3://overturemaps-us-west-2/release/2026-07-22.0/theme=places/type=place/` | Per-row in `sources[].license`: CDLA-Permissive-2.0 / Apache-2.0 (FSQ) / CC0-1.0 (ATP) | **Full CDLA-2.0 agreement text** + **full Foursquare NOTICE.txt** | keyless (anon S3) | 74,223,561 world; US-bbox `truck_repair` **10,858** | name, category, lat/lon, address, ZIP, phone, website, **email**, **socials**, brand, confidence, operating_status |
| **Overture categories CSV** | `raw.githubusercontent.com/OvertureMaps/schema/main/docs/schema/concepts/by-theme/places/overture_categories.csv` | Schema repo is **CC-BY-4.0** (not CDLA — corrected) | CC-BY attribution | keyless | 2,117 category codes | the allow-list, matched on **hierarchy path** not substring |
| **FSQ OS Places (HF, current)** | `huggingface.co/datasets/foursquare/fsq-os-places` | Apache-2.0 | NOTICE.txt in full, "prominently in your developer documentation" | free gated token (see §5.3) | US "Automotive Repair Shop" 541,517 | corroboration, `email` (41.0% fill), socials, `date_refreshed` |
| **FSQ OS Places (source.coop mirror)** | `data.source.coop/fused/fsq-os-places/` | Apache-2.0 | Same | keyless | release **2025-02-06** (~17 mo stale) | ungated fallback; no NOTICE.txt at root |
| **AllThePlaces** | `alltheplaces.xyz` / `github.com/alltheplaces/alltheplaces` | Data **CC0-1.0**, spider code MIT (verified in README + LICENSE) | none | keyless | 4,909 spider files; 1,418,830 ATP features inside Overture | **the only permissive `opening_hours` + `image` + `email`** — chains only |
| **Census TIGER county** | `www2.census.gov/geo/tiger/TIGER2025/COUNTY/tl_2025_us_county.zip` | US Gov work, 17 U.S.C. §105 | Census citation requested; **trademark statement if redistributed** | keyless | 83,989,800 B (verified byte-exact) | `county_name` + `county_fips` (the "District" field) |
| **Census TIGER ZCTA520** | `…/TIGER2025/ZCTA520/tl_2025_us_zcta520.zip` | US Gov work | Same | keyless | 529,118,424 B (verified) | `zip5` **fallback only** (ZCTA ≠ ZIP) |
| **Census TIGER state** | `…/TIGER2025/STATE/tl_2025_us_state.zip` | US Gov work | Same | keyless | 9,956,072 B (2025 file confirmed to exist) | `state_usps`, `state_fips` |
| **Census TIGER AREAWATER** | `…/TIGER2024/AREAWATER/` | US Gov work | Same | keyless | 3,235 county files | point-in-water fake-listing check |
| **Census CBP 2022** | `www2.census.gov/programs-surveys/cbp/datasets/2022/cbp22us.zip` (+ `cbp22co.zip`, `zbp22detail.zip`) | US Gov work | Cite Census | keyless | 2,003 US-level NAICS rows; 811111 = 84,101 establishments | **the honest coverage denominator** |
| **Census NAICS index/descriptions** | `census.gov/naics/2022NAICS/2022_NAICS_Index_File.xlsx`, `…_Descriptions.xlsx` | US Gov work | Cite Census | keyless | 20,399 index entries; 2,125 description rows | documentation of what the taxonomy means |
| **Census Geocoder (geographies)** | `geocoding.geo.census.gov/geocoder/geographies/coordinates?…&vintage=…` | US Gov work | — | keyless | ~1.4 s/call | **reconciliation oracle only** — see §3.2 |
| **EPA Envirofacts FRS** | `data.epa.gov/efservice/frs.frs_facility_site/state_code/equals/DE/0:2/JSON` | US Gov work, public domain | — | keyless | national_combined.zip = 1,355,239,400 B, Last-Modified 2026-07-08 | independent federal existence corroboration (name/addr/lat/lon/NAICS) |
| **EPA ECHO RCRA** | `echodata.epa.gov/echo/rcra_rest_services.get_facility_info?output=JSON&p_st=DE&p_naics=811111` | US Gov work | ToS evidence link: use `echo.epa.gov/tools/data-downloads` (the disclaimer page 404s) | keyless | DE/811111 → QueryRows **2,411** | `verification_status`, county FIPS, RCRAStatus, last inspection date |
| **NY DMV facilities** | `data.ny.gov/resource/nhjr-rpi2.json` | **OPEN-NY ToU: no attribution, no share-alike, commercial OK — but a *revocable* licence.** Not CC0. | none required | keyless | **54,563** (RS 18,272 · RSB 3,426 · ISP 10,405) | licence number + expiry + county + geocoded point → `verification_status`, `last_verified_at` |
| **NJ MVC inspection facilities** | `data.nj.gov/resource/t6tk-mr48.json` | NJ legal §F: view/copy/distribute without obligation | none required | keyless | **1,167** | phone corroboration, county, ZIP |
| **CT licensed dealers & repairers** | `data.ct.gov/resource/apne-w8c6.json` | `licenseId = PUBLIC_DOMAIN` (explicit) | none | keyless | **138** | cleanest licence position of any state registry; geocoded + `license_expiration` |
| **Local Calling Guide** | `localcallingguide.com/xmlprefix.php?npa=302&nxx=655` | **No published licence** (`/terms.php` 404s); `robots.txt` = `Disallow: /cgi-bin/` only, so the XML endpoint is not disallowed | — | keyless | NPA-NXX → rate-centre lat/lon, state, OCN | phone-vs-state geography check. `udate` observed 2024 → **not freshly maintained** |
| **Geofabrik US PBF** | `download.geofabrik.de/north-america/us-latest.osm.pbf` | ODbL 1.0 (footer: *"Data processed by Geofabrik GmbH and created by OpenStreetMap Contributors \| License: ODbL 1.0"*) | © OpenStreetMap contributors, ODbL, + link | keyless | 12,038,018,063 B (11.2 GiB), 2026-07-22 | `osm.*` mirrors, junctions — **but see the robots.txt ruling in §5.2** |
| **Name Suggestion Index** | jsDelivr-pinned | BSD-3-Clause | BSD notice | keyless | 49,943 items, 17 under `shop/truck_repair` | brand normalisation for `truck_brands_supported` |

### 3.2 Rejected, with the reason

| Rejected | Reason (evidence) |
|---|---|
| **Google Places API / any Google rating, review, photo** | Four independent kill clauses — see §5.1. Also: Places API is now **Legacy** ("not available in new Cloud projects"), and signup requires a **billing-enabled** project, so the no-paid-API constraint is violated before any clause is reached. |
| **Scraping maps.google.com** | Prohibited by **Google Maps End User Additional Terms §2** (last modified 2026-01-27): *"copy the content"*, *"mass download or create bulk feeds of the content"* — binds every user with or without an account. **NOT** by robots.txt: `google.com/robots.txt` **Allows** `/maps/place/` and `/maps/search/` for `User-agent: *`. Recording "robots.txt forbids it" would be a false statement of fact. |
| **Yelp (API or scrape)** | `robots.txt` verbatim, under a section titled "AI / LLM Crawlers and Agents": *"Use of any robot, spider, service search/retrieval application, or other automated device, process or means to access, retrieve, copy, scrape, or index any portion of the service or any content is prohibited."* Fusion API is now **paid** (§7.1 30-day trial → §8.1 subscription), §5(a) caps storage at 24 hours, §5(b) forbids building a listings database. |
| **YellowPages** | **Correction:** `robots.txt` does *not* forbid it — `Allow: /` for `*`, with `Content-Signal: search=yes,ai-train=no,use=reference`, and only nine named AI bots Disallowed; the ToU page 403s. The correct recorded reason is: proprietary aggregated directory with no licence granting redistribution, plus an express `ai-train=no` reservation. |
| **Nominatim (public)** | OSMF policy, verbatim under *Unacceptable Use*: *"Systematic queries. This includes reverse queries in a grid… If you need complete sets of data, get it from the OSM planet or an extract."* Plus *"an absolute maximum of 1 request per second"* and recurring scripts *"restricted to 4 requests per minute"* — national coverage is arithmetically impossible. The policy also explicitly binds LLM-generated code. |
| **Census Geocoder as the national pipeline** | No coordinate-batch endpoint (`geographies/coordinatebatch` → **404**; `geographies/addressbatch` exists but takes addresses, capped at *"an upper limit of 10,000 records per batch file"*). Measured 1.23–1.57 s/call → ~39 h for 100k shops single-threaded. No published RPS limit ≠ permission to parallelise a free federal service. |
| **FAF5 Network Nodes as an interchange inventory** | Exhaustively refuted: a `returnDistinctValues` query over **all 4,485** `Interchange`-non-null rows returns only `{null, Toll Road Entry Location, Toll Road Entry Point, Toll Road Exit Location, Toll Road Exit Point}`. They are toll plazas, not freeway interchanges. |
| **Overpass as an ingest path** | `overpass-api.de/robots.txt` = `Disallow: /api/` — the exact path. Instances are also unreliable: during research `overpass-api.de` and `overpass.kumi.systems` both returned 504, `overpass.osm.jp` had an expired cert, and `overpass.osm.ch` silently returned **0** for a US bbox (a naive caller would record "zero junctions in the USA" as a fact). Backends reported `osm_base` timestamps two months apart. Use for spot-checks only; treat any 0 as SUSPECT. |
| **SAM.gov** | Returns 200 but the entire visible text after de-tagging is `" SAM.gov --> "` — an empty Angular shell. Reachable-but-unverified. It is an entity-registration DB (UEI/CAGE), not a repair registry. |
| **California DCA / Bureau of Automotive Repair** | Publishes only aggregate statistics (License Population by County, enforcement measures). No per-licensee list; the full roster needs a Public Records Act request. Do not build a scraper against `search.dca.ca.gov`. |
| **Love's, Ryder, TA/Petro store locators** | All three carry **explicit anti-scraping clauses** in their live Terms of Use, quoted verbatim during research — despite permissive robots.txt and published location sitemaps that will tempt a future contributor. Record in `data/config/forbidden_sources.yaml`. Their locations are legally reachable via Overture `brand` (Ryder 431, TA-Petro 104, Pilot 19) and via AllThePlaces (`loves_us` spider, CC0). |
| **Truck OEM dealer locators** (Freightliner, Peterbilt, Mack, Volvo, Western Star, International) | robots.txt allow-all and Freightliner's dealer pages do carry `LocalBusiness` JSON-LD — but **no ToS text could be retrieved** (SPA-rendered or 404), and every large-chain ToS that *could* be read prohibits scraping. Default = unusable pending a human ToS read. **Kenworth returns 403** = active refusal. |
| **Mapillary** | Not uniformly CC BY-SA: ToS says *"unless we indicate otherwise… (such as the Creative Commons Attribution NonCommercial Share Alike (CC BY-NC-SA license)"*. Per-image licence must be read at fetch time. Never register it flatly as CC BY-SA. |
| **Wikimedia Commons photos** | Legal and keyless, but measured coverage is landmarks (Amtrak station, theatre, county jail), not commercial frontages. Near-zero hit rate for truck repair shops. |
| **NAICS as a truck-vs-car discriminator** | 811111 is defined as covering *"passenger cars, trucks, and vans, and all trailers"* in **one code**; its index literally contains both "Truck repair shops, general" and ordinary auto garages. 811310 is titled *"…(except Automotive)…"* and its truck entries are *"Industrial truck (e.g., forklifts)"*. And CBP is aggregate-only by Title 13 confidentiality — there is no free per-establishment NAICS source. |
| **FMCSA** | Registers **motor carriers**, not repair shops. (Note: the FMCSA carrier file *does* have an `email_address` column with 2,939,689 non-null values — 147 columns, not 57 — but those are carriers, often personal Gmail addresses, so it is a PII question as much as a licence one. Dataset self-declares `unknown-license`.) |
| **`scourgify` on PyPI** | **Typosquat-by-coincidence.** `pip install scourgify` (v1.4.0, published 2026-07-11 — it looks fresh and legitimate) installs a *Calibre fanfiction tag normalizer*. The address library is `pip install usaddress-scourgify`, imported as `scourgify`. |

---

## 4. Field-by-field verdict

Legend: **FILLABLE-FREE** = a permissive source fills it at the stated rate · **PARTIAL** = fillable but low/uneven coverage, must render NULL as *unknown* · **NULL-HONEST** = no free source; column exists but is permanently unknown, or should be dropped · **PROHIBITED** = a contract forbids it.

### 4.1 India → US vocabulary mapping (do this before any code is written)

| Spec field | US field | Why | Source |
|---|---|---|---|
| **District** | `county_name` + `county_fips` (5-digit GEOID) | There is **no** US administrative unit called a district at this level; US "districts" (congressional/school/judicial) are different things and would actively mislead. TIGER's county layer already covers all county-equivalents — Louisiana parishes, Alaska boroughs/census areas, independent cities, DC — so one layer is 100% coverage with no special-casing. | NN `CTFIPS` on the route side; TIGER county PIP on the shop side; EPA FRS `std_county_fips` as a cross-check |
| **PIN Code** | `zip5` **TEXT(5)** (never INTEGER — `01234` would become `1234`) | USPS ZIPs are *delivery routes*, not areas. Census: *"The result is a point-based dataset unsuitable for mapping and many analysis applications."* | **Primary: the literal `postcode` from Overture/FSQ** (99.4% filled on truck_repair). **Fallback only:** TIGER ZCTA point-in-polygon, flagged `zip_from_zcta`. |
| **WhatsApp Number** | **drop** | Measured zero, not merely rare: an Overpass sweep across the whole US for `car_repair`/`truck_repair`/`tyres` carrying `contact:whatsapp` or `whatsapp` returned **total = 0** (re-verified 2026-07-23T09:02:21Z), against 17,937 such objects globally. Deriving one from the landline would assert a WhatsApp account exists — fabrication. | The honest US equivalents that *do* exist: Overture `socials[]` (82.1% fill) and FSQ `facebook_id`/`instagram`/`twitter`. |
| **State** | `state_usps` CHAR(2) + `state_fips` | 1:1 map. | Already CHAR(2) throughout the schema; TIGER state PIP for gaps |
| **Travel Direction** | `access_from_direction` + `access_direction_basis` | A stationary building has no travel direction. The only defensible meaning is *which carriageway reaches it without a U-turn*. Renaming forces the honest semantics. | derived; see §7.5 |

### 4.2 The table

| # | Field | Verdict | Source | Expected fill | Notes |
|---|---|---|---|---|---|
| 1 | `name` | **FILLABLE-FREE** | Overture `names.primary` | ~100% | |
| 2 | `category` | **FILLABLE-FREE** | Overture `taxonomy.primary` (migrate off `categories` — removed **September 2026**) | 100% coarse | Match on the **full hierarchy path**, never substring. |
| 3 | `services_offered` (free-text list) | **NULL-HONEST** | — | 0% | Neither Overture nor FSQ carries a service list. 0 of 51 reachable shop websites exposed `makesOffer`/`hasOfferCatalog`/`serviceType` in JSON-LD. Derive the *boolean flags* (#18-24) from category instead, and never present a category as a service inventory. |
| 4 | `truck_brands_supported` | **PARTIAL** | Overture `brand.names.primary` + `brand.wikidata`; ATP `brand:wikidata`/`nsi_id`; NSI (BSD-3) | **~5%** (568 of 10,858 truck_repair have `brand`) | Resolves Penske 1,553 · Ryder 431 · Rush Truck Centers 107 · TA-Petro 104 · MHC Kenworth 62 · Premier Truck Group 25 · Velocity 23 · TLG Peterbilt 22, plus Vanguard, TEC, TruckPro, FleetPride, Boss Truck Shop. `brand` means the shop's **own** brand, not brands serviced. Store as `brands_inferred TEXT[]` + flag `inferred_from_name`, following the repo's existing DEF-inference precedent. **Never assert OEM certification.** |
| 5 | `phone` | **FILLABLE-FREE** | Overture `phones[]`, FSQ `tel` | **99.2%** on truck_repair | |
| 6 | `whatsapp` | **NULL-HONEST → drop** | — | 0% | See §4.1. Building a `wa.me/<E164>` link asserts an account exists = fabrication. |
| 7 | `email` | **FILLABLE-FREE** | Overture `emails[]` (60.4%), FSQ `email` (41.0% on US auto-repair) | **~50-60%** | **Currently thrown away** — `pull_overture`'s SELECT omits `emails`. ~6,600 truck-repair emails discarded on every pull. Cheapest win in the project. |
| 8 | `website` | **FILLABLE-FREE** | Overture `websites[]` | **70.3%** | Of the recorded URLs, only ~42% actually return 200 — 39% are dead. Store the URL; do not imply it resolves. |
| 9 | `google_maps_url` | **FILLABLE-FREE** (generated) | Constructed from our own coordinates | 100% | `https://www.google.com/maps/search/?api=1&query=<url-encoded name>, <address>` (fall back to `<lat>,<lon>`). Implement as a **PostgreSQL `GENERATED ALWAYS AS … STORED` column** so a fetched Google value structurally cannot leak in. `api=1` is mandatory. Never resolve a `place_id`. See §5.1. |
| 10 | `lat` | **FILLABLE-FREE** | Overture `geometry` | 100% | Read `geometry`, **not** `bbox.ymin` — for a Point they coincide but the bbox corner is semantically the wrong thing. |
| 11 | `lon` | **FILLABLE-FREE** | Overture `geometry` | 100% | Same. |
| 12 | `address` | **FILLABLE-FREE** | Overture `addresses[].freeform` | **99.5%** street on truck_repair | Standardize with `usaddress` (MIT, 0.5.16, 2025-08-07) + `usaddress-scourgify` (MIT, 0.6.0, 2023-12-14 — **pin the version**, it is stale). Pub-28 standardization is **formatting, not validation**. |
| 13 | `state` | **FILLABLE-FREE** | Overture `addresses[].region`, else TIGER state PIP | ~98% → 100% after PIP | |
| 14 | `district` → `county_name`/`county_fips` | **FILLABLE-FREE** | TIGER county PIP (shop side); NN `CTFIPS` (route side) | ~100% | `observed_at` = the **TIGER vintage**, not the download date. |
| 15 | `PIN` → `zip5` | **FILLABLE-FREE** | Overture `postcode` (99.4%), ZCTA PIP fallback | **~98-99%** | `ST_Contains` only — **never snap to the nearest ZCTA**. Census: *"Uninhabited areas (land and water areas) over two square miles are potentially left unassigned"* and *"Not all valid ZIP Codes are represented by a 2020 ZCTA"* — that is exactly rural-interstate geography, so genuine NULLs are correct. Flag `zip_outside_zcta_coverage`. |
| 16 | `opening_hours` | **PARTIAL** | ATP `opening_hours` (CC0, chains only) primary; OSM `opening_hours` **only as a separately-attributed ODbL layer** | **≤15-20%**, concentrated in chains | Overture has **no** hours field (confirmed in `place.yaml`, which also disclaims `operating_status` as an hours proxy); FSQ has none. Measured OSM fill: 16.2% on `shop=truck_repair`, 16.1% on `shop=car_repair`. **Filling ATP gaps from OSM makes the property mixed → share-alike** (§5.2 R2). Parse with `opening-hours-py` 2.1.4 (MIT OR Apache-2.0 — *not* AGPL). |
| 17 | `open_24x7` | **PARTIAL** | ATP + ODbL OSM layer | **~10-15%** of those that have hours | Tri-state. Exact string match on `24/7` first. Only 149 US `car_repair` objects and 2 of 272 `truck_repair` objects are tagged 24/7; 15 of an 847-row national truck download (1.8%). **NULL must never render "no".** |
| 18 | `mobile_service` | **PARTIAL** | Overture `mobile_dent_repair` (6) + word-boundary name match | ~1% | The name heuristic is booby-trapped: `mobile` is a substring of **automobile** ("Riverview Automobile Ltd."). Word boundary + exclude `automobile`, always flagged `inferred`. |
| 19 | `roadside_breakdown` | **PARTIAL** | Overture `roadside_assistance` (1,277) + `emergency_roadside_service` (655) | category-derived | |
| 20 | `towing` | **FILLABLE-FREE** | Overture `towing_service` (**21,870**); FSQ "Towing Service" (9,650) | 100% coarse | Note Overture over-counts vs Census CBP 488410 = 10,554 establishments — expect duplicates/mobile/franchise pages. |
| 21 | `welding` | **FILLABLE-FREE** | Overture `welders` (1,315) + `welding_supply_store` (2,366); FSQ "Welding Service" (7,600) + "Machine Shop" (18,537) | 100% coarse | **All four are currently unmapped in `data/config/category_map.yaml`.** |
| 22 | `spare_parts` | **FILLABLE-FREE** | Overture `automotive_parts_and_accessories` (52,802) + `b2b_truck_equipment_parts_and_accessories` (918) | 100% coarse | |
| 23 | `tyre_repair` | **FILLABLE-FREE** | Overture `tire_dealer_and_repair` (42,817) + `tire_shop` (12,184) + `tire_repair_shop` (748); FSQ "Tire Repair Shop" (23,753) | 100% coarse | |
| 24 | `battery_service` | **NULL-HONEST** | — | ~0% | `service:vehicle:batteries` is 3,225 **worldwide**. No usable US source. Leave NULL. |
| 25 | `average_rating` | **PROHIBITED** | — | 0% | See §5.1. **Drop the column.** A permanently-NULL column named "rating" is an invitation for a future contributor to fill it from a prohibited source. |
| 26 | `review_count` | **PROHIBITED** | — | 0% | Same. Do **not** substitute source-count and call it a review count. |
| 27 | `review_summary` | **PROHIBITED** | — | 0% | Doubly barred: §3.2.3(a)(iii) bans saving reviews, §3.2.3(c)(vii) bans using Maps Content to train/test/validate/fine-tune models, and SST §10.3.1-10.3.2 close the Grounding-Lite route. |
| 28 | `photos` | **NULL-HONEST (near-zero)** | ATP `image` (CC0, chains only) is the **only** clean source | ~1-2% | Store the **URL**, never the bytes. Commons coverage is landmarks. Mapillary is per-image-licensed (some CC BY-NC-SA) and depicts the street, not the business. |
| 29 | `distance_from_route` | **FILLABLE-FREE** (once routes exist) | PostGIS `ST_Distance(geography)` against `core.truck_routes` | 100% within buffer | **Straight-line / buffer distance from public-domain federal freight geometry, labelled as such.** Never "driving distance" — every free routable graph (OSRM/Valhalla/OSM) is ODbL, and public-domain TIGER/NN gives geometry, not a turn-restricted network. |
| 30 | `route_id(s)` | **FILLABLE-FREE** | NN `ID` (unique) + `ROUTEID` (state-scoped) | 100% | One shop → many routes via `core.route_shops` link table. |
| 31 | `route_name(s)` | **FILLABLE-FREE** (derived) | `TRIM(SIGN1)` / `SIGNT1`+`SIGNN1` | 100% | `LNAME` is blank on 411,754 rows — **do not trust it**. Store raw sign fields alongside. |
| 32 | `nearest_route_point` | **FILLABLE-FREE** | `ST_ClosestPoint(seg::geography, shop::geography, true)` | 100% within buffer | The **geometry** variant on EPSG:4326 is wrong by up to 163.3 m in distance and 1,637 m along the line, at the same cost. Never use it. |
| 33 | `nearest_highway_junction` | **PARTIAL, blocked** | OSM `highway=motorway_junction`, in `osm.*`, joined at query time | dist always computable; **`ref` ~62%** | No free federal alternative exists (FAF5 Nodes are toll plazas; NHPN is polyline-only). Delaware bbox = 424 nodes (reproduced exactly). US total: the claimed 77,676 could not be reproduced (all Overpass instances failed); a CONUS bbox gives 81,439 with 50,704 refs = **62.26%**, so the honesty-critical *ratio* holds and the absolute total must be recounted from the PBF. Expose `nearest_junction_ref` (often NULL) and `nearest_junction_distance_m` (always computable) as **separate** fields. |
| 34 | `travel_direction` → `access_from_direction` | **PARTIAL, mostly NULL** | `ST_Azimuth` + sign of `sin(bearing_to_shop − route_heading)` | validated **91.3%** (42/46) under ideal conditions; expect **mostly NULL** nationally | NULL when: `distance_m < 150` (3 of the 4 validation failures sat within 135 m of *both* I-95 carriageways, i.e. in the median), the way is not oneway, the road is undivided, the located fraction lands on a segment endpoint (13.8-41.3% depending on vertex density), or access is via the local street network. **Always publish `route_heading_deg` alongside so the value is auditable.** This is the single most fabrication-prone field in the spec — a plausible-looking "Northbound" that is wrong sends a stranded driver to the wrong side of a divided highway. |
| 35 | `verification_status` | **FILLABLE-FREE** (5-value enum) | multi-source agreement + state registries + EPA | see §8.3 | `verified_multi_source` / `verified_single_authority` / `unverified` (the honest default — where nearly all current rows belong) / `disputed` / `closed_reported`. **No `fake` value** — no free source can prove fabrication. |
| 36 | `confidence` | **FILLABLE-FREE** (internal) | `quality.compute_confidence` + Overture per-row confidence | 100% | **Do not ship the current implementation** — see §8.1. |
| 37 | `last_verified_date` | **PARTIAL** | split into `last_verified_at` (world truth) + `last_verification_run_at` (operational) | ~60% | `last_verified_at` = the newest `sources[].update_time` among agreeing families, or an EPA `RCRALastInspectionDate`, or a state licence issue/renewal date. **Never** from FSQ `date_closed` — Foursquare's own docs: *"This does not necessarily mean the POI actually closed on this date."* |
| 38 | `source_urls` | **FILLABLE-FREE** | `ops.sources.url` + per-row `props.<source>.source_record_id` | 100% | Already the repo's pattern (`props.overture.source_record_id`, `release`). Extend with per-row `licence` read from `sources[].license`. |

### 4.3 The honest completeness ceiling

- Realistic national union after conflation: **~11,000-12,000 truck-labelled shops.**
- Census CBP 2022 counts **84,101** establishments in NAICS 811111 — but that code covers cars *and* trucks by definition, so it is an **upper bound on trucks, not a truck count**. No free source can even tell you how many US truck repair shops exist.
- Overture materially **over**-counts against Census for comparable activities (towing 21,870 vs CBP 10,554; tyre retail 55,001 vs CBP 20,455) — feed that into confidence, do not treat raw counts as a headcount.
- Publishing per-county coverage against CBP would be a genuinely differentiating honesty feature and is cheap to build.

---

## 5. Legal rulings

### 5.1 Google — ratings, reviews, photos, and the URL

**MAY NOT — no free path, no paid path, no workaround:**

- **Store** a Google rating, review count, review text, review summary or photo in any table. Ever.
  - ToS §3.2.3(b): *"**No Caching.** Customer will not cache Google Maps Content except as expressly permitted under the Maps Service Specific Terms."*
  - The complete Places grant, SST §14.3, verbatim: *"Customer may temporarily cache latitude and longitude values from the Places API for up to 30 consecutive calendar days, after which Customer must delete the cached latitude and longitude values."* Latitude and longitude. **Nothing else.** Google granted field-level caching with six-row tables for Weather and three for Pollen — it knows how to do that when it intends to.
  - Developer docs, plain English: *"You must not pre-fetch, cache, or store Places API content beyond the allowed exceptions, although the place_id is exempt from caching restrictions."* `place_id` — an opaque string carrying no rating — is the only Places field Google lets you keep.
  - Even the lat/lng grant is useless here: 30 days then **mandatory deletion** is structurally incompatible with a persisted `core.businesses` row carrying `observed_at`.
- **Scrape** it. §3.2.3(a)(iii): *"copy and save business names, addresses, or user reviews"*. "Google Maps Content" is defined as *"any content provided through the Services … including … places data (including business listings)."*
- **Display it live, unstored, at render time.** Two independent bars:
  - §3.2.3(d)(iii): *"use the Google Maps Core Services **in a listings or directory service** or to create or augment an advertising product"*. A searchable database of truck repair shops with names, addresses, phones and hours **is a listings or directory service**. This is a *use* restriction, not a storage restriction — it forbids Places API in this product at all, even as a discarded pass-through. **This closes the live-passthrough escape hatch the earlier lane left open.**
  - §3.2.3(e)(i): *"display or use Places content on a non-Google Map"*, reinforced at SST §14.2. A truck-routing product on public-domain federal geometry will render on MapLibre/deck.gl — so a Google rating beside it breaches this too.
- **LLM-summarise reviews.** §3.2.3(c)(vii) bans using Maps Content to train, test, validate or fine-tune models. SST §10.2.2 permits caching Grounded Output *"solely for the purpose of evaluating and optimizing the performance or display of the Grounded Output"* — an engineering-QA permission, not a data-storage one — and §10.3.1 forbids separating Maps Content from it.
- **Copy ratings by hand.** Google Maps **End User Additional Terms** (`maps.google.com/help/terms_maps/`, last modified 2026-01-27) §2 Prohibited Conduct: *"copy the content"*, *"mass download or create bulk feeds of the content"*. These bind **anyone who uses Google Maps**, with or without a billing account.
- **Record "robots.txt forbids scraping Google Maps."** It does not. `google.com/robots.txt` under `User-agent: *` contains `Disallow: /maps/` followed by `Allow: /maps/search/`, `Allow: /maps/place/`, `Allow: /maps/dir/`, `Allow: /maps/@`. The two paths a rating-scraper would want are **expressly Allowed**. Writing the false reason would repeat the exact error class already caught on YellowPages.

**MAY — free, keyless, expressly permitted in writing:**

- **Construct and store** `https://www.google.com/maps/search/?api=1&query=…` built from our own coordinates/name/address.
  - "Maps URLs" is **absent** from the official Core Services enumeration (`cloud.google.com/maps-platform/terms/maps-services/`, revised 2026-04-22), whose own scoping sentence reads *"only the services below are covered by the Google Maps Platform Terms of Service"*. §3.2.3 therefore never attaches.
  - `developers.google.com/maps/documentation/urls/get-started` (updated 2026-07-20): *"**You don't need a Google API key to use Maps URLs.**"*
  - Geo Guidelines, *Web and apps*: *"You're also welcome to link to Google Maps with text or a button on your website, such as 'View on Google Maps' or 'Open with Google Maps.'"*
  - No Google Maps Content is embedded by definition — nothing to cache, nothing to delete.
- **Use the Google Maps word mark** to label the field/button, as nominative reference per the Geo Guidelines *Use of trademarks* section.

**Implementation rules:** build from OUR coordinates and never resolve a `place_id` (that forms the Platform contract and drags the row inside §3.2.3(d)(iii)); implement as a `GENERATED ALWAYS AS … STORED` column so the provenance is structurally self-evident; `api=1` in every URL or all parameters are silently ignored; prefer `query=<name>, <address>` over bare coordinates (bare coords often drop a pin rather than showing the business card); do **not** fetch, HEAD, render or validate the URL programmatically at scale; do not embed a Google basemap next to it.

**Correction carried forward:** §3.2.3(c)(iv) — *"use latitude/longitude values **from the Places API** as an input for point-in-polygon analysis"* — is **scoped to Places-API coordinates**. Our coordinates come from Overture (CDLA), FSQ (Apache-2.0) and ATP (CC0). **The route-buffer operation is entirely untouched by this clause.** The earlier framing, which implied Google's ToS constrains this project's core spatial query, would have made the build fear a perfectly clean operation.

**The sentence the owner asked for:**

> Average Rating, Review Count and Review Summary cannot be filled legally from Google — not for free, and not for money either. The block is contractual and absolute. Leave the columns out, or NULL rendering "unknown". The only lawful thing this platform may take from Google is a hyperlink it builds itself from its own coordinates — and a hyperlink carries no data. It hands the question to the human, which is the honest outcome.

One legitimate exception, worth one line: if a shop *owner* grants the platform access to their own Google Business Profile, that owner may lawfully supply their own rating data. That is a per-merchant consent flow, not a data source, and it will never populate 10,858 rows.

### 5.2 ODbL share-alike

**The finding that breaks the comfortable answer: the `osm.*` mirrors are already Derivative Databases, before any join happens.**

ODbL §4.4(b): *"For the avoidance of doubt, Extraction or Re-utilisation of the whole or a Substantial part of the Contents into a new database is a Derivative Database and must comply with Section 4.4."* §1.0 defines Extraction to include **temporary** transfer, and Substantial as *"substantial in terms of quantity or quality… The repeated and systematic Extraction or Re-utilisation of insubstantial parts… may amount to the Extraction or Re-utilisation of a Substantial part."*

The OSMF **Substantial Guideline** (endorsed 2014-06-06) quantifies it: not-Substantial is *"Less than 100 Features"*, and *"The systematic extraction of all eating places within an area or at all castles within an area would be considered to be systematic."* Plus: *"we regard repeated small extractions as one big extraction!"*

| `osm.*` table | rows | >100 Features? | systematic? | verdict |
|---|---|---|---|---|
| `osm.fuel_stations` | 108,056 | yes, ×1,080 | "all US fuel stations" | **Derivative Database** |
| `osm.ways` | 109,777 | yes | all highways in a cut | **Derivative Database** |
| `osm.rest_areas` | 5,452 | yes | systematic | **Derivative Database** |
| `osm.weigh_points` | 3,773 | yes | systematic | **Derivative Database** |
| *proposed* `osm.truck_repair` | ~700 | yes, 7× over | the exact pattern OSMF names | **Derivative Database from row 1** |

Because `/v1/fuel` publicly serves `osm.fuel_stations`, §4.4(a) and §4.6 are engaged **today**:

> §4.6: *"If You Publicly Use a Derivative Database or a Produced Work from a Derivative Database, You must also offer to recipients… a copy in a machine readable form of: a. The entire Derivative Database; or b. A file containing all of the alterations made to the Database… free of charge if distributed over the internet."*

A repo-wide grep for any §4.6 affordance (`machine.readable|alterations file|derivative database|bulk export|/download`) returns **nothing**. This is present-tense non-compliance, not hypothetical.

**The Produced Work escape hatch does not exist for a JSON API.** OSMF **Produced Work Guideline**: *"If the published result of your project is intended for the extraction of the original data, then it is a database and not a Produced Work."* and *"Database dumps are usually not Produced Works."* A GeoJSON/REST endpoint returning `name`, `lat`, `lon`, `phone`, `website` is by design intended for data extraction. §4.4(c) closes the rest: *"A Derivative Database is Publicly Used and so must comply with Section 4.4. if a Produced Work created from the Derivative Database is Publicly Used."* **The earlier recommendation to "exploit §4.5 by serving a rendered page or tile" is struck from the record.**

**`core.businesses` itself stays clean — but purity is about *derivation*, not storage.**
- Overture's own words: *"The theme is published under the CDLA Permissive 2.0 and Apache 2.0 licenses. It contains no OpenStreetMap data and carries none of the share-alike obligations of the Open Database License (ODbL)."* — <https://docs.overturemaps.org/guides/places/> (**this is the citation of record; the sentence is NOT on the `/attribution/` page**, where a prior lane wrongly cited it).
- Structural corroboration: Base, Buildings, Divisions and Transportation each carry an explicit *"License for theme: ODbL"* line on the attribution page. **Places carries no such line and lists no OSM source.**
- §4.5(a) preserves the Collective Database carve-out.
- **But schema separation earns nothing on its own.** Collective Database Guideline: *"Technical implementations that are functionally equivalent to a reference but facilitate performance improvements — for example joining two databases together by a key for purposes of a production database — are equivalent to a reference,"* and *"Two data sets need not be physically separated to qualify as 'independent'."*
- The worked negative example is this exact product: *"You have a proprietary list of restaurants for a country. You would like to complement your list with the corresponding data from OpenStreetMap removing any duplicate objects in the process. The resulting, combined database would not be covered by this guideline and you would, if the dataset is publicly used, have to consider that your proprietary data **may** be subject to the ODbL share-alike terms."* (Note the hedge — *may*, not *is*.)
- Horizontal Map Layers says the same in map terms: *"If you use OpenStreetMap data along with non-OpenStreetMap data for a given Feature Type, then the share-alike condition would apply regardless of whether some data for that Feature Type is in a different layer."*

**Where the comfortable answer survives.** The **Geocoding Guideline** blesses a structurally similar pattern: a geocoder with *"two separate map databases, one of which contains solely OSM data"*, searched concurrently, returning results side by side, is fine *"so long as the aggregated collection of results does not contain the whole or a substantial part of the OSM database"* — with §4.3 attribution mandatory. Three load-bearing limits: it is written for *geocoding* (individual address lookups), it self-limits on substantiality, and **with only ~700 OSM truck-repair features nationally a paginated bbox API drains 100% of that layer in a few hundred calls. This layer is too small to hide in.**

**Regional cut.** Everything above is scoped *"within the same regional cut"*, and the Regional Cuts Guideline requires *"a clear boundary"*, *"no holes"*, *"No cuts from other data within the Regional Cut"*, and *"at least a country"*. A US-only platform has exactly **one** regional cut. Every purity test applies nation-wide, all-or-nothing, per Feature Type. "We only join OSM in the Northeast" has no safe harbour.

**Enforceability, honestly.** §10.4 defers to the enforcing jurisdiction. The US has no sui generis database right post-*Feist*, so ODbL bites here principally as **contract** (§2.1(c)) and via copyright in selection/arrangement. The honest framing is *"this is a contractual obligation you would be in breach of"*, not *"you will get sued."* And OSMF says so itself: *"A court would make a final decision on the issue."*

**PLAIN VERDICT — MAY:**
- Serve `osm.*` and `core.*` from separate endpoints, never cross-referenced (as built today). A genuine Collective Database.
- Serve OSM-only endpoints under ODbL, with correct attribution **and** a §4.6 offer.
- Build the truck-repair Feature Type **100% non-OSM** (Overture CDLA + FSQ Apache-2.0 + ATP CC0). Overture has 10,858 US truck_repair vs OSM's ~700 — **the permissive path is 15× better anyway.** This is not a sacrifice; it is the better engineering choice that happens to also be the safe one.
- Build routes from federal public-domain geometry. Never Overture Transportation, never `osm.ways`. **Load-bearing, not merely preferable.**
- Do anything internally. §4.5(c): *"Use of a Derivative Database internally within an organisation is not to the public and therefore does not fall under the requirements of Section 4.4."* Joins for QA, coverage measurement and eval are fully safe **as long as no published output derives from them**.

**PLAIN VERDICT — MAY NOT:**
- Treat schema separation as the legal control. Keep the `present_in <@ ARRAY['overture','fsq']` CHECK — but stop describing it as the thing that makes this legal. It is a *storage* guard doing zero *derivation* work.
- Use OSM to dedup, complement, filter, rank or corroborate `core` rows.
- **Fill any `core` property from OSM unless that property is 100% OSM for that Feature Type nationwide.** Highest-probability future breach: a JSONB `props` merge or a query-time `COALESCE(core.phone, osm.phone)`/hours-gap-fill. The CHECK constraint will not fire, because no row is inserted. (The machinery for this mistake already exists — `core.businesses.conf_agree` and `businesses_pipeline.py:77` compute agreement from `present_in`.)
- Rely on "it's just a query-time join" or "only 3 rows per request."
- Rely on §4.5(b) Produced Work for a JSON/GeoJSON API.
- Publish a bulk export of anything OSM-touched without ODbL + the full §4.6 offer.
- Carry ~700 OSM truck-repair rows and call it insubstantial.

**Three live defects to fix (measured today):**
1. `ops.sources` for `osm_pois` and `osm_ways` has `license = NULL, attribution_text = NULL`. `/v1/meta` renders `common.unknown(...)`, so the platform's own licence-disclosure endpoint reports **"unknown"** for its only share-alike source. Set `license = 'ODbL-1.0'`, `attribution_text = '© OpenStreetMap contributors, ODbL — https://www.openstreetmap.org/copyright'`.
2. `api/routes_fuel_stations.py:32` hardcodes `"© OpenStreetMap contributors"`. The Attribution Guidelines accept that wording but add: *"Attribution must also make it clear that the data is available under the Open Database License"* and *"There needs to be a way to access more information, including origin and licence of the data… (for example by making the text a clickable link)."*
3. No §4.6 affordance exists. Add `/v1/osm-export` or a documented static dump per `osm.*` mirror, free, machine-readable, linked from `/v1/meta`.

**Good news, measured:** no API route currently joins `osm.*` to `core.*` (`routes_places.py` has zero `osm.` references), and there is **no OSM truck-repair or POI table at all** — only `fuel_stations`, `rest_areas`, `ways`, `weigh_points`. **The decision is still free, exactly like the routes table.**

**Replace the ruling's justification.** §3.1-4a currently reasons "OSM lives only in `osm.*`, joined at query time" — contradicted by *"Two data sets need not be physically separated."* Restate it as a **derivation** rule with an enforceable test: *no SQL, pipeline or scoring path may read from `osm.*` and `core.businesses` in the same statement, and no `core` column or `props` key may ever take a value that originated in `osm.*`.* A CI grep for cross-schema references in one query is a stronger control than the CHECK constraint, because it catches the failure mode the constraint structurally cannot see.

### 5.3 Permissive licences — the obligations are cheap to build and fatal to skip

**Overture Places is empirically OSM-free.** DuckDB over `s3://overturemaps-us-west-2/release/2026-07-22.0/…part-00000…parquet`, unnesting `sources[]`:

| dataset | licence | source records |
|---|---|---|
| Overture | CDLA-Permissive-2.0 | 4,595,262 |
| meta | CDLA-Permissive-2.0 | 4,265,983 |
| Overture-signals | CDLA-Permissive-2.0 | 2,744,846 |
| Microsoft | CDLA-Permissive-2.0 | 174,293 |
| **Foursquare** | **Apache-2.0** | **91,257** |
| BrightQuery | CDLA-Permissive-2.0 | 40,191 |
| **AllThePlaces** | **CC0-1.0** | **20,168** |
| DAC | CDLA-Permissive-2.0 | 2,901 |
| PinMeTo | CDLA-Permissive-2.0 | 351 |
| RenderSEO | CDLA-Permissive-2.0 | 118 |

**Zero `osm` rows. Zero NULL licences.** The permissive claim holds on the wire, not just in the docs. Two documentation-drift notes: `Overture` and `Overture-signals` (7.3M of 11.9M source records) **do not appear on the attribution page at all**, and `Krick` appears on the page but not in this file. **Do not treat the attribution page as an exhaustive dataset→licence map — read the licence off `sources[].license` in the data.** There is also a tenth string, `SparkGeo-confidence-conflation`, on ~1M POIs, which the independence logic must handle.

**Schema caveat:** `sourcePropertyItem` has `required: [property, dataset]` — `license` is **optional**, and the schema says *"If the license is NULL, contact the data provider for more license information."* It is populated today; it is not guaranteed to stay so. **Add a pipeline assertion that fails the load if any ingested row has a NULL `sources[].license`.**

**CDLA-Permissive-2.0 §2.1** requires *"A Data Recipient may share Data… so long as the Data Recipient makes available **the text of this agreement** with the shared Data."* That is the **full licence text**, not a credit line. And **the §3 escape hatch does not work**: §3.1 exempts *"Results"*, but §5 defines Results as *"any outcome obtained by computational analysis of Data, including for example machine learning models and models' insights."* A shop record served to a user is **Data, not a Result**. Serving the API = sharing Data = §2.1 applies.

**The Foursquare NOTICE obligation reaches Overture-only builds.** 91,257 FSQ-sourced records sit inside Overture Places (4,748,001 features overall in the July 2026 release). NOTICE requires *"preserving the full content of this NOTICE.txt file"*, and for API distribution *"include a copy of the content from this NOTICE.txt file **prominently in your developer documentation**."* The owner cannot say "I only use Overture, so only CDLA applies."

**The HuggingFace gate is a separate contract, not a licence condition.** Accepting it means *"you… agree to allow repository authors to use your employer or entity name and logo in descriptions of its partners on its website, in media, and in marketing materials"*, plus mandatory contact sharing. Apache-2.0 demands none of that. Alternatives: the ungated `data.source.coop/fused/fsq-os-places/` mirror (frozen at 2025-02-06) or the public `fsq-os-places-us-east-1` S3 bucket, which serves `LICENSE.txt` and `NOTICE.txt` anonymously.

**TIGER's "no attribution burden" is REFUTED.** TGRSHP TechDoc §1.1-1.2, verbatim:
> *"TIGER/Line® is a registered trademark of the Census Bureau. **TIGER/Line cannot be used as or within the proprietary product names of any commercial product**… The Census Bureau requests that any repackaging of the TIGER/Line Shapefile data… for distribution include a conspicuously placed statement to this effect."*
> *"We would ask, however, that you cite the Census Bureau as the source."*
> *"The boundary information in the TIGER/Line Shapefiles is **for statistical data collection and tabulation purposes only**. Their depiction and designation for statistical purposes does not constitute a determination of jurisdictional authority."*

→ **Never name any product, feature, endpoint or table `TIGER`-anything.** Cite the Census Bureau. Carry the trademark statement conspicuously if TIGER data is redistributed. (Internal schema naming `tiger.*` for the loaded shapefiles is a grey area; prefer `census_geo.*`.)

**NHFN/NHS/STRAHNET's "unrestricted, no obligation" is REFUTED in part.** Their `copyrightText` conditions free distribution on carrying the original metadata entry, **unmodified**, with every distribution.

**HPMS chain-of-title — the one risk that could not be closed.** 17 U.S.C. §105 removes copyright from works prepared by federal officers/employees. But FHWA states HPMS — the geometry under the National Network — *"is a compilation of data collected from many State Departments of Transportation."* State DOT submissions are not federal works. Practical risk is low (states submit under federal mandate 23 CFR 420; no state is known to assert copyright; road centrelines are thin-to-unprotectable facts post-*Feist*; BTS affirmatively asserts §101/unrestricted use). **Record it as a known residual, not as a settled fact.** This is the honest version of "public domain."

**AllThePlaces CC0 is a waiver from a party that may not hold the rights** — ATP data is produced by scraping brand store-locator pages and the README says nothing about the ToS status of those scrapes. Practically low risk (US addresses/coordinates are unprotectable facts), but the CC0 tag is ATP's self-assertion, not an indemnity. It reaches the platform indirectly anyway via Overture.

**The attribution ledger — a single footer credit line does NOT discharge these. Build a `/licenses` page and an export-bundle manifest.**

| Obligation | Trigger | What must ship |
|---|---|---|
| **Full CDLA-Permissive-2.0 agreement text** | any sharing of Overture Places Data, incl. API responses | the complete licence text, made available with the Data |
| **Foursquare NOTICE.txt, full content** | any Apache-2.0-sourced row (direct **or** via Overture) | full NOTICE.txt; for an API, prominently in developer documentation |
| **Apache-2.0 licence copy + modification notices** | same | licence copy; state that records were modified/conflated |
| **Census Bureau citation** | any TIGER/ZCTA/county/CBP use | "Source: U.S. Census Bureau" |
| **TIGER trademark statement** | redistribution of TIGER shapefile data | conspicuous statement per TechDoc §1.1; never in a product name |
| **FHWA + BTS acknowledgment** | NTAD National Network use | *"Acknowledgment of the Federal Highway Administration (FHWA) and the Bureau of Transportation Statistics (BTS) [distributor]"* |
| **NHFN/NHS/STRAHNET metadata entry, unmodified** | any redistribution of those layers | the original metadata entry, verbatim, with each distribution |
| **© OpenStreetMap contributors, ODbL + link** | any `osm.*`-derived response | attribution **plus** the ODbL statement **plus** a clickable link, **plus** the §4.6 offer |
| **Overture citation** | courtesy / best practice | "Overture Maps Foundation, overturemaps.org" |
| **Nothing** | AllThePlaces (CC0-1.0) rows | — |

**Per-field licence ledger is now provably necessary, not merely tidy.** A single Overture row carries **multiple** `sources[]` entries with **different** licences scoped to different JSON Pointers (e.g. a `meta`/CDLA root source plus an `Overture`/CDLA source scoped to `/properties/confidence`). Column-group granularity is the minimum; JSON-Pointer-level is what the data actually gives you.

**The Geofabrik robots.txt ruling the owner must make.** `download.geofabrik.de/robots.txt` contains `User-agent: *` then `Disallow: *.osm.pbf` (plus `*.osm.bz2`, `*.osc.gz`, `*.shp.zip`, `*.state.txt`, `*updates*`, `*.md5`). Every artifact this project ingests is disallowed to robots, and the repo's `polite_get` honours robots.txt as a hard rule. Read fairly this is an anti-crawler directive on a service Geofabrik publishes for free download and advertises as *"available for free download"* and *"updated every day"*. But it needs an **explicit written ruling in the source registry**, not silence — the repo already fetches this file. Either (a) record a documented, narrow exception for this host with a rate cap and a contact User-Agent, or (b) source the PBF elsewhere. It must not be fetched silently. Same ruling needed, or a flat prohibition, for `overpass-api.de` (`Disallow: /api/`) — and note that a bare request to `overpass-api.de/robots.txt` returns **406**, so `polite_get`'s robots check needs an explicit documented fail-open/fail-closed policy rather than silently proceeding.

**Dead citation links that must be swapped before they go into `ops.sources`:**

| Broken | Replacement |
|---|---|
| `echo.epa.gov/resources/general-info/echo-data-disclaimer` (404) | `https://echo.epa.gov/tools/data-downloads` (200) |
| `census.gov/programs-surveys/geography/about/terms-of-use.html` (404) | `https://www.census.gov/data/developers/about/terms-of-service.html` (200) |
| `census.gov/about/policies/open-gov/open-data.html` (redirect) | `https://www.census.gov/topics/research/research-transparency-public-access/open-data.html` |
| `usgs.gov/information-policies-and-instructions/copyrights-and-credits` (403) | unresolved — USGS-as-public-domain is almost certainly right as a federal work, but the citation is **unverified**; do not cite a page that does not load |

---

## 6. Classification design

### 6.1 The decision rule

**Step 0 — HARD CATEGORY GATE.** If the POI has no repair-ish category in *any* source — OSM `shop ∈ {truck_repair, car_repair, truck, trailer, tyres, car_parts, truck_parts}`, or Overture taxonomy path under `automotive > automotive_services_and_repair`, or `towing_service` — emit `NOT_REPAIR` and stop. **This single gate killed 56 of 85 false positives in the DFW control experiment before any scoring happened.**

**Step 1 — additive integer score.**

| Signal | Δ |
|---|---|
| OSM `shop=truck_repair` | +6 |
| OSM `service:vehicle:truck_repair=yes` | +6 |
| Overture taxonomy primary ∈ {`truck_repair`, `trailer_repair`, `truck_repair_and_services_for_businesses`} | +6 |
| OSM `shop=truck` or `shop=trailer` | +3 |
| OSM `service:vehicle:{diesel_repair, trailer_repair, truck_tyres, truck_parts}=yes` | +3 each |
| high-precision name phrase (multi-word, word-bounded) | +3 |
| HCV brand token (word-anchored) | +3 |
| Overture `towing_service` / `truck_dealer` / `commercial_vehicle_dealer` | +2 |
| OSM `service:vehicle:towing=yes` | +1 |
| single weak keyword (`truck` alone) | +1 |
| name matches `/food truck\|truck rental\|truck leasing\|truck driving\|truck accessor\|truck toys\|truck cap\|bedliner\|monster truck/i` | **−5** |
| Overture category ∈ {`food_truck`, `truck_rentals` (40,428!), `trailer_rentals`, `game_truck_rental`} | **−8** |
| Overture `confidence < 0.20` | **−4** |
| `operating_status != 'open'` | **−6** |

**Step 2 — band.** `score ≥ 6` **and** ≥1 Tier-A signal → `CONFIRMED_TRUCK` · `3-5` → `LIKELY_TRUCK` · `1-2` → `AMBIGUOUS` · `≤0` with a car-only category and no truck evidence → `CAR_ONLY` · gate failure → `NOT_REPAIR`.

**Publish policy.** Publish `CONFIRMED_TRUCK` and `LIKELY_TRUCK`; the latter only with `flags` containing `truck_service_inferred` so the API can filter it. Hold `AMBIGUOUS` in a staging view — **do not publish, do not delete** — it is the LLM/human queue. Never publish `CAR_ONLY` or `NOT_REPAIR`. Store band + score + per-signal contributions in `props` so every verdict is reproducible.

The existing `core.businesses` taxonomy already permits `truck_repair, mobile_repair, trailer_repair, tire_service, towing, truck_parts, truck_dealer, truck_wash` — **no schema change is needed**.

### 6.2 Signals ranked by precision

**TIER A — CONFIRMED_TRUCK on a single hit**

| Signal | US count | Est. precision | Note |
|---|---|---|---|
| OSM `shop=truck_repair` | **272** (69 nodes / 203 ways / 0 relations — reproduced by two independent methods) | ~0.98 | The tag's whole definition is HCV repair. Worldwide total is only 813, so the US holds 33% of the entire planet's. |
| OSM `service:vehicle:truck_repair=yes` | **529** | ~0.95 | **446 of these sit on `shop=car_repair`** — a `shop=truck_repair`-only filter throws away ~58% of tag-confirmed truck shops, precisely the "car garage that also services HCV" the inclusion rule demands. |
| Overture `truck_repair` / `trailer_repair` / `truck_repair_and_services_for_businesses` | **10,858 / 140 / 1** | high | Match on the **full hierarchy path** (`automotive > automotive_services_and_repair > truck_repair`), never substring — path matching cleanly excludes `food_truck` and `game_truck_rental`. |

**TIER B — LIKELY_TRUCK, needs one corroborator:** OSM `shop=truck` (304, mixes dealers+repair), `shop=trailer` (96), `service:vehicle:diesel_repair` (20), `service:vehicle:trailer_repair` (9), `service:vehicle:truck_parts` (7), `service:vehicle:truck_tyres` (3); Overture `towing_service` / `truck_dealer` / `commercial_vehicle_dealer`.

**TIER C — AMBIGUOUS, never publish alone:** OSM `shop=car_repair` (**47,143**), `shop=tyres` (7,367), `shop=car_parts` (17,072), `amenity=vehicle_inspection` (482); Overture `automotive_repair` (**201,199**) / `tire_dealer_and_repair`.

**TIER D — negative evidence is worthless.** `service:vehicle:truck_repair=no` occurs **exactly once** in an 847-row national download. **Absence of a truck tag means UNKNOWN, never CAR_ONLY. Do not build an exclusion rule on absence.**

**Two signals from the original spec must be deleted:**
1. `service:vehicle:truck=yes` and `service:vehicle:hgv=yes` **do not exist** — taginfo `/key/stats` returns `all=0` for **both keys**, and `/tag/stats` returns 0 for both `=yes` values. Code written against them matches nothing and the failure looks like an ingest bug, not a spec bug.
2. `hgv=yes` is a **road access tag**, not a service tag. 1,633,084 uses, **1,605,995 (98.3%) on ways**, dominated by `hgv=designated` (987,238), `hgv=yes` (217,471), `hgv=no` (243,977). Using it as POI evidence would classify every business adjacent to a truck route as a truck shop — catastrophic for precision on exactly the buffer query this system performs. `hgv` belongs on `osm.ways` (where the repo already correctly stores it), used on the **route** side, never the shop side.

**One more precision caveat:** 495 of the 1,381 global `service:vehicle:truck_repair` objects **also** carry `service:vehicle:car_repair` — ~36% are mixed car+truck shops. A binary truck classifier will always have a fuzzy middle.

### 6.3 False-positive traps (measured, not imagined)

DFW control experiment: name regex `/truck|diesel|fleet|semi/i` over POIs carrying `shop|amenity|office|craft|industrial` returned **85 hits → 1 tag-confirmed truck, 28 repair-ish ambiguous, 56 hard false positives = 66% FP rate.**

Real trap names from that run:
- **`semi`** → **Seminary** (a church, a college *and* a polling station), **Yosemite**. This alone disqualifies bare `semi`.
- **`truck`** → Awestruck Design Company · Food Truck restaurants · "Truck Yard" (a bar) · Budget/Rush Truck Rental · Truck Driving Academy · Truck Toys · Truck Accessories · Trucker Drivers Wash · a lawyer advertising "Car & Truck Accident".
- **`fleet`** → **Fleet Feet** (shoe chain, 3 locations) · Starfleet Couriers.
- **`diesel`** → **Diesel Barbershop** (3 locations) · "Diesel" the clothing brand.
- **`mobile`** → **automobile** ("Riverview Automobile Ltd."). Mobile-mechanic detection **must** use a word boundary and exclude `automobile`.

**Rules that follow:** keyword matching is **forbidden as a standalone signal** and permitted only as a booster inside the category gate. High-precision phrases are multi-word and word-bounded: *truck repair, truck & trailer, trailer repair, diesel repair, diesel service, heavy duty repair, fleet service, fleet maintenance, big rig, 18 wheeler/18-wheeler, DOT inspection, air brake, leaf spring, reefer*. Brand tokens need whole-word anchors: Freightliner, Peterbilt, Kenworth, Western Star, Mack, Navistar, Volvo Trucks, Hino, Isuzu Commercial. Require a **repair verb** — "Truck Parts / Sales / Rental / Leasing / Centers" are parts/sales/rental, not repair (Rush Truck Centers appeared 7× in DFW; it is a dealer network that *does* service, so LIKELY not CONFIRMED). Allow fuzzy matching — real observed typos "Truck Repar" and "Diesel Repar" — via the existing `businesses_name_trgm` GIN index, not exact LIKE.

**Overture's own trap categories:** `truck_rentals` **40,428** rows, `trailer_rentals` 1,510, `food_truck`, `game_truck_rental`. `truck_rentals` alone is 4× the entire truck_repair universe — a substring match on "truck" would drown the signal.

### 6.4 Live precision bug that must be fixed at ingest

The single existing `core.businesses` row with `category='truck_repair'` is **`Вакансии`** (Russian for "Vacancies"), address `Машиностроителей`, plotted in Manhattan, with `props.overture.src_confidence = 0.0668`. It scores confidence **65** (**corrected** — an earlier lane said 73; that number belongs to *Boss K Towing Services*, a Quezon City listing force-labelled `state='NY'`, which does score 73).

Fixes, all cheap:
- Reject rows with `src_confidence < 0.20` outright; 0.20-0.50 caps the band at `AMBIGUOUS`.
- Honour `operating_status` — `permanently_closed`/`temporarily_closed` must never publish as an active shop. **Note the coupling:** Overture's schema states *"A confidence score of 0… will always be paired with an `operating_status` of `permanently_closed`"* — so **confidence = 0 is itself a closure signal** (correction to lane 7's "independent of operating_status").
- Script-mismatch flag: a US POI whose name is majority non-Latin with a non-US-format address.
- Tighten the pull filter — `addresses[1].country = 'US' OR addresses[1].country IS NULL` is how 22 foreign businesses stacked at `40.71670 / -74.00000` got in. Require an affirmative US country **or** a US-parseable address.

### 6.5 The requested sub-categories: DETECTABLE vs UNDETECTABLE

| # | Sub-category | Verdict | Evidence |
|---|---|---|---|
| 1 | Truck mechanic | **DETECTABLE** | `shop=truck_repair` / `service:vehicle:truck_repair` / Overture `truck_repair` |
| 2 | Heavy vehicle garage | **DETECTABLE — same evidence as #1** | |
| 3 | Commercial vehicle workshop | **DETECTABLE — same evidence as #1** | |
| 4 | Commercial vehicle service center | **DETECTABLE — same evidence as #1** | **#1-4 are four names for ONE evidence set and cannot be distinguished from each other in free data. Implement as ONE canonical category, not four.** |
| 5 | Trailer repair | **DETECTABLE** | `service:vehicle:trailer_repair` US 9 + `shop=trailer` 96 + Overture `trailer_repair` 140 |
| 6 | Diesel engine repair | **DETECTABLE (thin)** | `service:vehicle:diesel_repair` US 20 + `diesel_engine_repair` global 15 + name "diesel repair". **There is no `diesel_repair` slug in Overture** — diesel repair is not separately modelled anywhere in Overture. |
| 7 | Welding & fabrication | **DETECTABLE** | Overture `welders` 1,315 + `welding_supply_store` 2,366; FSQ "Welding Service" 7,600 + "Machine Shop" 18,537; OSM `craft=metal_construction` 1,155 / `craft=blacksmith` 127 |
| 8 | Truck AC | **WEAK** | `service:vehicle:air_conditioning` global 3,509 — overwhelmingly **car**, not truck-specific |
| 9 | Radiator | **WEAK** | `service:vehicle:radiators` 84 / `radiator` 23 (global) |
| 10 | Truck electrical | **WEAK** | `service:vehicle:electrical` global 3,317 — again car-dominated |
| 11 | 24×7 | **DETECTABLE but ~98% NULL** | `opening_hours` containing `24/7`; only 15 of 847 national truck rows (1.8%) |
| 12 | Breakdown assistance | **DETECTABLE** | Overture `roadside_assistance` 1,277 + `emergency_roadside_service` 655 |
| 13 | Roadside emergency | **DETECTABLE — same as #12** | |
| 14 | Towing | **DETECTABLE** | Overture `towing_service` 21,870; FSQ 9,650; OSM `service:vehicle:towing` US 299-304 (present on just 3% of the truck set) |
| 15 | Clutch & gearbox | **WEAKLY DETECTABLE** | `service:vehicle:clutches` 55 / `clutch` 24 / `gearbox_repair` 16 — all **global** |
| 16 | Axle & differential | **WEAKLY DETECTABLE** | `differentials` 15 / `axles` 8 global |
| 17 | Hydraulic | **WEAKLY DETECTABLE** | `hydraulics` 15 global |
| 18 | Chassis | **WEAKLY DETECTABLE** | `underchassis` 8 global |
| 19 | Fleet maintenance | **WEAKLY DETECTABLE** | `fleet_services` 18 / `fleet_vehicle_maintenance` 16 global. The name "Fleet Service" is better evidence than the tag — and "Fleet Feet" is the trap. |
| 20 | Air brake | **UNDETECTABLE** | No OSM tag exists. Only inferable from a rare name phrase. |
| 21 | Suspension & leaf spring | **UNDETECTABLE** | `service:vehicle:suspension` is 398 global and car-dominated; "leaf spring" has no tag. |
| 22 | Pneumatic | **UNDETECTABLE** | No tag. |
| 23 | Mobile mechanic | **UNDETECTABLE (name-inferred only)** | NAICS 811111's index literally contains "Mobile automotive and truck repair services" — the business type exists — but there is no free per-business NAICS join and no OSM tag. Populate `mobile_repair` **only** on a word-boundary name match excluding `automobile`, always flagged inferred. |

**Binding rule for every UNDETECTABLE and WEAK row:** emit SQL `NULL` rendered as *unknown*. **Never emit `false`** — that would assert "this shop does not service air brakes" on zero evidence, which is the exact failure the repo's honesty rules forbid, and the highest-harm error class in this product.

### 6.6 LLM adjudication — yes, but narrowly

Justification is quantitative: the DFW experiment left **28 rows** that deterministic rules genuinely cannot resolve, containing real truck shops (G & C Truck Repair, Legendary Automotive & Diesel Repair, Diesel Pros LLC, Mac's Diesel Diagnostics, Inland Truck Parts & Service, "Barebones Auto & Diesel Repar") sitting beside real non-repair businesses (Truck Toys, DFW Truck and Auto Accessories, AFG Truck Parts). No regex separates those.

- **Scope:** run **only** on `band = AMBIGUOUS` (~30% of gated candidates), never the 47k `car_repair` universe.
- **Input:** minimal canonical JSON of `{name, osm tags OR overture path, city, state, website hostname}` and nothing else. No coordinates, no free web text.
- **Output:** strict JSON `{band, primary_category, subcategories[], rationale, confidence}`.
- **Audit:** reuse the existing `quality.ai_decisions` table (verified: `decision_id, job, input_hash, model, prompt_version, input, verdict, rationale, decided_by, created_at`, `UNIQUE(job, input_hash, decided_by)` — currently **0 rows**, so there is no precedent to inherit). `job='truck_vs_car_classification'`, `input_hash = sha256` of the canonicalised input so identical inputs are never re-billed, `prompt_version` pinned so a prompt change forces re-decision. The `decided_by` in the unique key gives a free human-override path.
- **HARD RULE:** an LLM verdict may promote `AMBIGUOUS → LIKELY_TRUCK` but **must never promote to `CONFIRMED_TRUCK`**. The highest-trust tier of published data never depends on a model.

---

## 7. Geospatial design

Environment: **PostgreSQL 16.4 / PostGIS 3.4.3** (GEOS 3.9.0, PROJ 7.2.1). All timings below are warm-cache, single-threaded, measured on the live DB against real national point layers.

### 7.1 Segmentation — measured-fraction chunking

`ST_Segmentize` is a **densifier**, not a splitter (367 points in → 374 out, one geometry). `ST_DumpSegments` gives wildly non-uniform work units (min 1.4 m, max 7,880 m, sd 414.9 m — segment size is a property of the source vertices). Naive equal-fraction `ST_LineSubstring(geom, i/n, (i+1)/n)` **drifts up to +16.4%** because the fraction is measured in planar **degrees**.

The working chunker dumps vertices, accumulates **both** planar-degree and geography-metre cumulative length per vertex, then linearly interpolates each metre boundary back into a planar fraction:

```sql
CREATE FUNCTION core.route_chunks(route geometry(LineString,4326), chunk_m double precision)
RETURNS TABLE (seq int, frac_start double precision, frac_end double precision,
               m_start double precision, len_m double precision, geom geometry(LineString,4326))
LANGUAGE sql IMMUTABLE AS $$
WITH v AS (
  SELECT (dp).path[1] AS i, (dp).geom AS pt
  FROM ST_DumpPoints(route) dp
), cum AS (
  SELECT i, pt,
         sum(ST_Distance(lag(pt) OVER w ::geography, pt::geography)) OVER w AS m_cum,
         sum(ST_Distance(lag(pt) OVER w,             pt))            OVER w AS d_cum
  FROM v WINDOW w AS (ORDER BY i)
), tot AS (SELECT max(m_cum) AS m_tot, max(d_cum) AS d_tot FROM cum),
bounds AS (
  SELECT generate_series(0, ceil(t.m_tot / chunk_m)::int) AS k, t.m_tot, t.d_tot FROM tot t
), cuts AS (          -- interpolate each metre boundary back into a PLANAR fraction
  SELECT b.k, least(b.k * chunk_m, b.m_tot) AS m_at,
         ( SELECT (c.d_cum - (c.d_cum - lag(c.d_cum) OVER (ORDER BY c.i)) *
                   ((c.m_cum - least(b.k*chunk_m,b.m_tot)) /
                    NULLIF(c.m_cum - lag(c.m_cum) OVER (ORDER BY c.i),0)) ) / b.d_tot
           FROM cum c WHERE c.m_cum >= least(b.k*chunk_m,b.m_tot) ORDER BY c.i LIMIT 1 ) AS frac
  FROM bounds b
)
SELECT k+1, frac, lead(frac) OVER (ORDER BY k), m_at,
       lead(m_at) OVER (ORDER BY k) - m_at,
       ST_LineSubstring(route, frac, lead(frac) OVER (ORDER BY k))::geometry(LineString,4326)
FROM cuts WHERE lead(frac) OVER (ORDER BY k) IS NOT NULL;
$$;
```

**Measured:** on a real 425 km route at 2 km, min = max = 2,000 m, sd = 0.0, and the summed covered length equals the route length exactly. Gap proof returns `fraction_gaps = 0`, `geometry_gaps = 0`, `first_frac = 0`, `last_frac = 1`.

**Densify vertex-sparse routes first.** If `length_m / (ST_NPoints(geom) - 1) > 200`, run `ST_Segmentize(route::geography, 1000)::geometry(LineString,4326)` before chunking. On real routed geometry (96-101 m vertex spacing) chunking is **bit-exact lossless** — 123 == 123 fuel stations, 393 == 393 bridges, 169 and 561 identically at chunk sizes 1/2/5/10/25/50 km. On a synthetic 223-km-vertex-spacing route it diverged 0.58%.

**NEVER use `ST_LineSubstring(geography, …)` on PostGIS 3.4.3.** It silently truncates multi-vertex lines. Deterministic reproducer:

```sql
SELECT postgis_lib_version(),
       ST_Length('LINESTRING(-75 39,-75 39.25,-75 39.5)'::geography)                       AS truth,
       ST_Length(ST_LineSubstring('LINESTRING(-75 39,-75 39.25,-75 39.5)'::geography,0,1)) AS got;
-- 3.4.3 | 55510.128 | 41632.596      (stops at exactly 75% of the line)
```

On a 22-vertex route it returned 34.8% of the length and 9 of 22 vertices. **Add a startup assertion** so a future PostGIS upgrade cannot silently reintroduce it: the geography variant may only be used if the above returns within 1 m of 55510.13. No matching upstream trac ticket was found — treat that as `[UNVERIFIED]`.

### 7.2 Buffer — one index is the whole ballgame

```sql
CREATE INDEX CONCURRENTLY <t>_geog_gix ON <schema>.<table> USING GIST ((geom::geography));
-- then, matching the index expression TEXTUALLY:
WHERE ST_DWithin(f.geom::geography, s.geom::geography, 5000)
```

| Approach | Time (same 123-row answer) |
|---|---|
| no index (Parallel Seq Scan over 108,056 rows) | **4,321 ms** |
| functional geography GIST | **68 ms cold / 18.05 ms warm (240×)** |
| `ST_Intersects(f.geom, ST_Buffer(r.geom::geography, 5000)::geometry)` | 952 ms (53× slower — PostGIS runs `_ST_BestSRID` + two `ST_Transform`s per evaluation) |
| hand-rolled `f.geom && ST_Expand(r.geom, 0.06)` prefilter | 15.5 ms — **and silently wrong** |

PostGIS rewrites `ST_DWithin(geography)` to `(geom)::geography && _ST_Expand((s.geom)::geography, '5000')` — it computes the latitude-correct degree expansion itself. **That is exactly why a hand-rolled fixed-degree `ST_Expand` prefilter is unsafe.** Constructed proof:

```sql
WITH route AS (SELECT ST_GeomFromText('LINESTRING(-147.7 64.0,-147.7 65.0)',4326) g),
     shop  AS (SELECT ST_Project(ST_SetSRID(ST_MakePoint(-147.7,64.5),4326)::geography,4000,radians(90))::geometry g)
SELECT ST_Distance(shop.g::geography, route.g::geography),
       shop.g && ST_Expand(route.g, 0.06),
       ST_DWithin(shop.g::geography, route.g::geography, 5000)
FROM route, shop;   -- 4000.0 m | f | t
```

A shop at exactly 4 km is **dropped** at 64.5°N. Three real test routes happened not to expose this purely because no station sat in the affected band — data sparsity, not correctness.

**CRS error budget** (vs `ST_Distance(geography, spheroid)` on 123 real rows within 5 km): geography sphere (`use_spheroid=false`) max 11.244 m / 0.245% · **EPSG:5070 NAD83 CONUS Albers max 45.01 m / 0.934% — it is EQUAL-AREA, never use it for distance** · EPSG:32618 UTM 18N max 1.78 m / 0.040%. For this platform, just use geography: it is exact and already fast enough.

### 7.3 Chunking payoff

Real dense 425 km route, 5 km buffer, identical results at every size:

| Chunk | vs `osm.fuel_stations` (108,056) | vs `core.bridges` (629,710) |
|---|---|---|
| whole route | 305 ms | 1,022 ms |
| 1 km / 426 segs | 76 ms | 224 ms |
| 2 km / 213 segs | 56 ms | 141 ms |
| **5 km / 86 segs** | **34 ms (9.0×)** | **99 ms (10.3×)** |
| 10 km | 39 ms | 176 ms |
| 25 km | 50 ms | 139 ms |
| 50 km | 59 ms | 179 ms |

All 12 runs returned exactly 169 and 561. **Use 5 km chunks for real routed geometry** — it is also the natural buffer-radius scale, so per-chunk false positives drop from 93% (whole route) to ~47%. On sparse synthetic routes the optimum shifts to 25-100 km; re-run the sweep once real national geometry is loaded.

### 7.4 One-pass enrichment: nearest point + distance + fraction + heading + side

**87 ms** for a 425 km route and 169 shops. The trig is effectively free next to the buffer scan (79 ms for the buffer alone).

```sql
WITH cand AS (
  SELECT s.route_id, s.seq, s.m_start, s.len_m, s.geom AS seg_geom,
         f.shop_ref, f.geom AS shop_geom
  FROM core.route_segments s
  JOIN LATERAL (
    SELECT business_id AS shop_ref, geom
    FROM core.businesses b
    WHERE ST_DWithin(b.geom::geography, s.geom::geography, 5000)
  ) f ON TRUE
  WHERE s.route_id = $1
),
best AS (   -- collapse chunk-boundary duplicates; ORDER BY distance to the SEGMENT
  SELECT DISTINCT ON (route_id, shop_ref) *
  FROM cand
  ORDER BY route_id, shop_ref, ST_Distance(shop_geom::geography, seg_geom::geography)
)
SELECT b.route_id, b.shop_ref,
       np.g::geometry                                        AS nearest_point,
       ST_Distance(b.shop_geom::geography, np.g)             AS distance_m,
       b.m_start + lf.f * b.len_m                            AS m_along_route,
       (b.m_start + lf.f * b.len_m) / rt.length_m            AS fraction_along_route,
       degrees(az.a)                                         AS route_heading_deg,
       CASE
         WHEN az.a IS NULL                                          THEN NULL
         WHEN ST_Distance(b.shop_geom::geography, np.g) < 150        THEN NULL  -- median / interchange
         WHEN lf.f <= 0.0 OR lf.f >= 1.0                             THEN NULL  -- azimuth ill-defined at a corner
         WHEN sin(ST_Azimuth(np.g::geometry, b.shop_geom) - az.a) > 0 THEN 'right'
         ELSE 'left'
       END                                                    AS side_of_travel
FROM best b
JOIN core.truck_routes rt ON rt.route_id = b.route_id,
LATERAL (SELECT ST_LineLocatePoint(b.seg_geom::geography, b.shop_geom::geography, true) f) lf,
LATERAL (SELECT ST_ClosestPoint (b.seg_geom::geography, b.shop_geom::geography, true) g) np,
LATERAL (SELECT ST_Azimuth(ST_LineInterpolatePoint(b.seg_geom, greatest(lf.f-0.002,0)),
                           ST_LineInterpolatePoint(b.seg_geom, least   (lf.f+0.002,1))) a) az;
```

**`ST_ClosestPoint` must be the geography variant.** Measured on 169 real shops: the planar 4326 variant gives max **163.315 m** / avg 20.772 m distance error and sits up to **1,637 m along the line** from the true geodesic foot (worst real case: true 2,585.9 m vs planar 2,684.4 m, foot at the wrong interchange). Cause: at 39°N a longitude degree is only 0.777× a latitude degree in ground metres, so the planar perpendicular is not the ground perpendicular. The geography variant is **exact** (0.000 m vs `ST_Distance`) and costs the same (88.0 ms vs 79.2 ms for the whole query).

`ST_LineLocatePoint(geography)` **is** trustworthy (0.249992 vs a true 0.250000) — unlike `ST_LineSubstring`.

**KNN `<->` is for ORDERING only.** Index-assisted KNN works against the functional geography index (0.405 ms/probe over 108,056 rows) but returns a **sphere approximation** (75.209 vs true 75.203). Use it inside a `LATERAL` to get candidates, then recompute the published distance with `ST_Distance(geography)`. The KNN index path needs the probe geometry to be a per-row constant, so a plain two-table `ORDER BY <->` will seq-scan.

**Why `DISTINCT ON` is mandatory:** a 5 km buffer around 5 km chunks means a shop near a boundary matches 2-3 adjacent chunks — 998 candidate pairs collapsed to 169 shops on one route; 34,973 pairs to 12,835 bridges across 1,125 segments. Order by distance to the **segment**, not to the route: the difference between the two is at most **3.48 m** over 169 real rows, so segment-level minimisation is a safe proxy.

### 7.5 Travel direction / side of carriageway

`side = sin(ST_Azimuth(nearest_point, shop) − route_heading) > 0 ? 'right' : 'left'` (azimuth is clockwise from north, so a positive sine puts the shop on the driver's right).

**Validation:** 46 shops matched **both** real I-95 Delaware carriageways (NB headings 36-90°, SB 217-272° — correctly opposite). **42 of 46 = 91.3%** flipped side correctly.

**NULL it in all of these cases:**
- `distance_m < 150` — **3 of the 4 validation failures** sat within 135 m of *both* carriageways, i.e. in the median or at an interchange.
- The underlying way is not `oneway` and the route did not come from a directional router. (Only 22,503 of 109,777 Delaware ways carry a `oneway` tag at all; the NN spine has **no direction field whatsoever**.)
- Undivided road — a left turn across a single centreline is legal, so "side" has no operational meaning.
- The located fraction lands on a segment endpoint (sharp corner) — measured 13.8% on I-95 NB, 16.5% SB, 41.3% on a vertex-sparse route, 0.0% on a dense one.

**Always publish `route_heading_deg` alongside** so the value is auditable rather than an opaque left/right. `observed_at` must be the **older** of (route vintage, shop vintage), and the field must carry a `derived_from_geometry` flag and a reduced confidence sub-score.

### 7.6 Nearest junction — SQL ready, table blocked

```sql
SELECT rs.route_id, rs.shop_ref,
       j.osm_id AS junction_osm_id, j.ref AS exit_number, j.name AS junction_name,
       round(ST_Distance(rs.nearest_point::geography, j.geom::geography)::numeric, 1) AS junction_dist_m
FROM osm.route_shops rs
CROSS JOIN LATERAL (
  SELECT osm_id, ref, name, geom
  FROM osm.junctions j
  WHERE ST_DWithin(j.geom::geography, rs.nearest_point::geography, 8000)
  ORDER BY j.geom::geography <-> rs.nearest_point::geography
  LIMIT 1
) j;
```

The `ST_DWithin` guard bounds the KNN scan (without it a `LIMIT 1` KNN can walk far in empty regions). **Better:** snap to the junction nearest **along the route** (compare `m_along` on the same segment) rather than as-the-crow-flies, so the reported exit is the one a driver actually passes.

`osm.junctions` does not exist yet: `SELECT count(*) FROM osm.ways WHERE highway='motorway_junction'` → **0**, because `highway=motorway_junction` is a **node** tag and `scripts/osm_ways_job.py` applies `EntityFilter(osmium.osm.WAY)`. `motorway_link` is no substitute — 650 rows, 36 with a `ref`, **0** with a `name`.

**The fix is ~30 lines in the right file.** `scripts/osm_extract.py` (line ~238) **already** runs `entities=NODE|WAY` with a `TagFilter` and produces `osm.fuel_stations` / `rest_areas` / `weigh_points` **from nodes**. Add `('highway','motorway_junction')` to `_MATCH_TAGS`, add a `_kind()` branch, create `osm.junctions` modelled exactly on `osm.fuel_stations`. It rides the **same** PBF pass and the **same** disk-based node-location cache — no extra download, no Overpass runtime dependency.

### 7.7 One shop, many routes

```sql
CREATE TABLE core.route_shops (        -- see §5.2: if the spine is federal PD, core.* is correct
  route_id             TEXT   NOT NULL,
  shop_source          TEXT   NOT NULL,   -- 'businesses' | 'osm_fuel' | 'osm_shops' | …
  shop_ref             TEXT   NOT NULL,
  seg_seq              INT    NOT NULL,
  distance_m           DOUBLE PRECISION NOT NULL,
  nearest_point        geometry(Point,4326) NOT NULL,
  m_along_route        DOUBLE PRECISION NOT NULL,
  fraction_along_route DOUBLE PRECISION NOT NULL,
  route_heading_deg    DOUBLE PRECISION,
  side_of_travel       TEXT,
  buffer_m             INTEGER NOT NULL,
  source_id  TEXT NOT NULL, run_id BIGINT NOT NULL,
  ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(), observed_at TIMESTAMPTZ,
  PRIMARY KEY (route_id, shop_source, shop_ref)
);
CREATE INDEX route_shops_shop_ix  ON core.route_shops (shop_source, shop_ref);
CREATE INDEX route_shops_route_ix ON core.route_shops (route_id, m_along_route);
```

The shop lives **exactly once** in its own table; `shop_source` keeps the permissive and ODbL pools separable at query time. Proven: 3,611 link rows over 3,312 distinct shops across 5 routes, built in 1.46 s, with shops correctly carrying up to 4 route links each and per-route distance and side. `buffer_m` is stored on the row so a later re-run at a different radius is distinguishable rather than silently overwriting.

**Batching / spill / resumability.** At `work_mem=1MB` the `DISTINCT ON` collapse over only 34,973 rows already spilled (external merge, peak disk 1,360 kB). Never run one giant query. Loop over `route_segments` in batches of ~2,000 with `SET LOCAL work_mem='256MB'`, materialize candidates into an UNLOGGED temp table, collapse inside the batch, then:

```sql
INSERT INTO core.route_shops (...) VALUES (...)
ON CONFLICT (route_id, shop_source, shop_ref) DO UPDATE
  SET distance_m = EXCLUDED.distance_m, ...
  WHERE EXCLUDED.distance_m < core.route_shops.distance_m;
```

That predicate makes cross-batch boundary shops resolve to their true minimum **regardless of batch order**, so the job is order-independent. Add `ops.route_shop_progress (route_id, seq, run_id, buffer_m, done_at)` written in the same transaction; because `route_chunks` is IMMUTABLE and deterministic, a resumed run reproduces byte-identical segments — no drift, no gaps, no double counting.

### 7.8 Two operational landmines found on the live DB

1. **`ANALYZE` had never been run on any spatial table.** `pg_stat_user_tables.n_live_tup = 0` for bridges, businesses, tunnels, parking_sites, fuel_stations, rest_areas, weigh_points, ways and live_events — the planner was choosing plans blind. **Add an explicit `ANALYZE` to the end of `loaders.snapshot_swap`** (a swap-and-immediately-query pipeline races autovacuum every time) and a smoke check that fails when `reltuples = 0` on a non-empty table.
2. **Stock server config:** `shared_buffers 128MB`, `work_mem 4MB`, `maintenance_work_mem 64MB`, `random_page_cost 4` on SSD, on a 15.9 GB / 4-core host. `random_page_cost 4` is a spinning-disk default actively pushing the planner away from index scans. Recommend `shared_buffers 3GB`, `effective_cache_size 9GB`, `random_page_cost 1.1`, `maintenance_work_mem 1GB`, `max_parallel_workers_per_gather 3`; leave global `work_mem` at 16-32MB and raise it per-session with `SET LOCAL`.

### 7.9 Also extend the existing dedup, do not rebuild it

`scripts/businesses_pipeline.py` already has the right shape (150 m geography block, 0.3 trigram gate, `0.60·name + 0.25·(1−dist/150) + 0.15·bonus`, 0.85 merge / 0.55 distinct with an honest flagged gray zone, deterministic `business_id`). Five concrete extensions:

1. **Add the geography index** — the 150 m self-block on 2,981 rows took **10,932 ms** because the planner drove off `businesses_pkey`; with the functional index the same query returns the same 52,243 pairs in **555 ms** (19.7×), and the full scoring pass went 19,179 ms → 431 ms (44.5×).
2. **Intra-source dedup** — the job only blocks Overture × FSQ today; a single source contains its own duplicates. Add a self-block with `a.rid < b.rid` as a FILTER *after* the spatial predicate, never as the join driver.
3. **Widen the radius for truck shops** — 150 m is tuned for urban storefronts; a repair yard's Overture centroid and its FSQ pin can legitimately sit 300 m apart on the same lot. Raise the block **and** the distance-term denominator in lockstep.
4. **Phone-first blocking** — a btree on the last-10 phone digits catches mobile-repair operators whose "location" is a dispatcher address. Highest-precision non-spatial signal for this domain.
5. **Bound the blow-up before running nationally** — 150 m on 2,981 NYC rows produced 52,243 pairs = 17.5 neighbours/row. Pair count is O(N × local density), not O(N). Process per-state or per-geohash-5 tile and hard-cap neighbours per row (`LIMIT 50` inside a `LATERAL` ordered by `<->`). **Run `scripts/conflate_gate.py` first** — it is the repo's existing measure-before-you-run harness and imports the production SQL so the measurement cannot drift.

---

## 8. Verification + confidence design

### 8.1 The current score is broken and must not ship as-is

Measured across all 2,981 rows: `confidence` spans **60-78**, avg 71.93, and takes only **8 distinct values** (60, 63, 65, 68, 70, 73, 75, 78). The analytic explanation:

- **T is fixed at 0.65** — the flat `AUTHORITY_BASE_TRUST['open_aggregate']`, applied to every row regardless of Overture's own per-record confidence (which *is* staged as `src_confidence` and *is* completely unused).
- **A is fixed at 0.5** — all 2,981 rows are `present_in = {overture}`, so the corroborated branch never fires.
- **F ≈ 1.0 for everyone** — because `observed_at` is the Overture **release date**, which was one day old.
- Only **C** varies → `0.5775 + 0.20·C` = **57.75-77.75**. Exactly the observed band.

The score has essentially zero discriminating power, and a Philippine towing listing force-labelled `state='NY'` scores 73.

**Until the fixes below land, either suppress `confidence` from the API entirely, or serve it with an explicit `"confidence_basis": "single_source_uncorroborated"` qualifier so no consumer mistakes 73 for "checked."**

### 8.2 The independence caveat — Overture vs OSM vs FSQ

**Overture vs OSM IS genuinely independent.** Overture Places carries no OSM data (verified in the docs *and* empirically: zero `osm` rows across 11.9M unnested source records).

**Overture vs FSQ is NOT independent.** Overture absorbed ~6M Foursquare OS Places POIs in the 2025-09-24 release. Overture's own release notes: *"approximately 6 million new POIs from Foursquare Open Source Places"*, *"We selected these records as POIs not previously included in Overture"*, and *"all Foursquare-sourced data is single sourced, meaning we do not blend its attributes with any other sources."* So an Overture row whose `sources[].dataset = 'Foursquare'` agreeing with the FSQ pull is **circular self-agreement** — and `businesses_pipeline.py:~1202` currently scores exactly that as corroborated (A = 1.0). The pipeline cannot even detect it, because `pull_overture`'s SELECT drops the `sources` column.

**Replace the boolean `corroborated = len(present_in) > 1` with an independent-family count:**

| Family | Members | Note |
|---|---|---|
| (a) Overture-non-FSQ | meta, Microsoft, BrightQuery, DAC, Krick, Overture, Overture-signals | |
| (b) Foursquare | FSQ direct **or** via Overture — **same family** | |
| (c) OSM | | genuinely independent, but see §5.2 for where the join may live |
| (d) EPA FRS / ECHO RCRA | | independent **federal** attestation |
| (e) The shop's own web presence | PinMeTo, RenderSEO, AllThePlaces **and** the shop's own website | **Second circularity trap:** these are listing-management / store-locator feeds derived *from* the business's own web presence, so they do not independently corroborate that website. |

Corroborate only when **≥2 distinct families** agree. Also handle the tenth string, `SparkGeo-confidence-conflation`.

### 8.3 The five code changes, in dependency order

1. **Pull the four dropped Overture columns.** `pull_overture`'s SELECT (line ~619) currently takes only `id, name, brand, categories.primary, bbox.ymin/xmin, addresses[1].*, phones[1], websites[1], confidence`. Add **`sources`** (independence + true vintage), **`operating_status`**, **`emails[1]`**, **`socials[1]`**, and switch lat/lon from `bbox.ymin/xmin` to **`geometry`**. This one change unblocks nearly everything else — and recovers ~6,600 truck-repair emails and ~9,000 social handles per pull.
2. **Fix `observed_at`.** It is currently the Overture release date — an aggregator **repackaging** date, i.e. exactly the download-date-shaped thing the repo bans. The honest vintage is `max(sources[].update_time)` across the row's contributing sources. Fall back to the release date only when absent, and set flag `vintage_is_release_date` so the compromise is visible. This also restores freshness as a discriminating signal.
3. **Degrade trust per-row using Overture's own confidence.** `quality.py`'s docstring already sanctions the move: *"Trust can only degrade from its authority-class base."* Use `T_row = AUTHORITY_BASE_TRUST['open_aggregate'] × src_confidence`, clamped to a floor. Store the release id alongside — Overture's confidence normalization **changed** between the March and April 2026 releases and was rolled back (*"~10M places now receive updated confidence scores"*), so re-validate any threshold per release.
4. **Add `core.businesses` to `quality.TABLE_SCORING`.** Today confidence is computed once at build time and `enqueue_rescore` is a documented no-op for this table, so it goes stale immediately. Entry: `entity_type='businesses', table='core.businesses', pk_cols=('business_id',), entity_id_sql='x.business_id', half_life_days=POI_HALF_LIFE_DAYS (730.0), completeness=BUSINESS_COMPLETENESS, where='TRUE'`. The `rescore_table` agreement branch is currently hardcoded 0.5-or-0.0 and must be extended with a corroboration join — **which must not read `osm.*`** (see §5.2).
5. **Add `core.truck_routes` and `core.route_shops` to `TABLE_SCORING` too**, or they are never scored at all.

### 8.4 Fake-listing heuristics (six, all validated against a real live cluster)

1. **Coordinate pile-up.** `GROUP BY round(lat,5), round(lon,5) HAVING count(*) > N` — this alone surfaced **22 rows stacked at 40.71670 / −74.00000**, every one a foreign business (Quezon City, Gujranwala, Boksburg, Tbilisi, Bogor, Luxor) force-labelled `city='New York'`, `state='NY'`. Discriminate genuine multi-tenant sites (truck stops, malls) by **category diversity** — 22 rows spanning cafe+fast_food+grocery+hotel+medical+restaurant+towing at one point is not a building, it is a geocoder's failure bucket. N needs empirical tuning by urban density before it may carry a penalty rather than an advisory flag.
2. **Locale mismatch.** Non-Latin script in name or address while `state` is a US code — caught `Вакансии` / `Машиностроителей` and `深坑街55號`.
3. **US-address parse failure.** No recognisable US street suffix, no 5-digit ZIP, no house number — caught "Quezon City" and "Gujranwala road Sheikhupura".
4. **Low source confidence.** Overture `src_confidence < 0.20` (28 rows in the current extract).
5. **Point in water or parkland.** `ST_Intersects` against TIGER AREAWATER (3,235 county files, keyless) or NHD (`hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer`, layer 10 = 448,512 features, `copyrightText` "Data Refreshed July, 2026" — genuinely queryable).
6. **Name spam.** URL-as-name ("Cafemiraza.us"), a generic word rather than a business name ("Вакансии" = "Vacancies"), keyword stuffing, or a name that is just a category label.

Wire these through the **existing** gate-4 machinery (`quality.REGISTERED_CHECKS` + `run_gate4()`) — it already gives idempotent, auto-closing, persisted conflicts wired into the confidence penalty (0.10 each, capped 0.20, plus A→0.0). Register: `biz_phone_area_vs_state`, `biz_coord_pileup`, `biz_coord_in_water`, `biz_overture_closed_vs_present`, `biz_website_dead`. Extend `quality.GEO_SUSPECT_FLAGS` from `('offroad','coord_suspect')` with `('coord_pileup','coord_in_water','locale_mismatch','address_not_us')` so they pick up the existing 0.15 GEO_PENALTY.

### 8.5 Phone verification — three free layers, and the honest ceiling

- **Layer 1, NANP structural validation** (pure code, zero network): NPA must match `[2-9][0-9]{2}` and not be N11; NXX likewise; **555-0100 through 555-0199 are reserved fictional numbers** and must be rejected; 800/833/844/855/866/877/888 are toll-free and **non-geographic**, so they must SKIP the geography check and score *unknown*, never *fail*.
- **Layer 2, rate-centre geography** via Local Calling Guide `xmlprefix.php` (verified live: `npa=302&nxx=655` → `rc=Wilmington`, `region=DE`, `rc-lat=39.74538`, `rc-lon=-75.545412`, `ocn=9210`, `company-name=VERIZON DELAWARE, INC.`). Compute the great-circle distance between the rate centre and the shop coordinate; hundreds of miles is a strong fake/stale signal. **Cache every NPA-NXX locally and populate lazily only for phones actually held — never sweep the number space.** Rate-limit through `polite_get`.
- **Layer 3**, cross-source phone agreement + "is this number printed on the shop's own website" (the strongest single signal).

**The ceiling, stated plainly:** there is **no free legal carrier or line-type lookup**. LCG's OCN and company-name are LERG-derived **block assignments, i.e. pre-porting** — US Local Number Portability means a legitimately ported number will look wrong. Record `line_type` as NULL = unknown and never guess. NANPA's own site is currently **DNS-dead** (authoritative nameserver returns REFUSED; reproduced via Cloudflare DoH with EDE-22/EDE-23), so LCG is the working substitute — and its `udate` values are 2024, so the block data is **not freshly maintained**. LCG publishes **no licence** (`/terms.php` 404s), so classify it `cache_limited` and get written permission before it becomes a core dependency.

### 8.6 `verification_status` — five values, two flavours of ignorance

| Value | Meaning |
|---|---|
| `verified_multi_source` | ≥2 **independent families** agree on existence AND location within tolerance |
| `verified_single_authority` | exactly one federal/state authority (EPA RCRA facility match, NY DMV licence) with no contradicting evidence |
| `unverified` | present in sources but no independent corroboration — **the honest default, where nearly all current rows belong** |
| `disputed` | an open `quality.conflicts` row exists |
| `closed_reported` | Overture `operating_status='permanently_closed'` (or `confidence = 0`, which the schema says always pairs with it), or FSQ `date_closed`, or an OSM `demolished:`/`was:`/`closed:` prefix |

**Deliberately absent: any `fake` terminal value.** No free source can prove fabrication. The heuristics produce flags and a `disputed` status; only a human audit may promote a row to a suppression list. Keep it a `CHECK` constraint on a TEXT column to match the repo's existing style, not a PG enum type.

**Never present an unqualified "verified" to a driver deciding whether to limp 40 miles.** Two databases agreeing is not someone checking. The API should return the corroborating source list alongside the status so the claim is auditable by the consumer.

### 8.7 `last_verified_date` — split it in two or it becomes a download date

- `last_verified_at TIMESTAMPTZ` = the `observed_at` of the most recent **corroborating evidence** (newest `sources[].update_time` among agreeing families; EPA `RCRALastInspectionDate` when an inspector physically visited; the OSM element's version timestamp; a state licence issue/renewal date). **World truth.**
- `last_verification_run_at TIMESTAMPTZ` = when **our** pipeline last ran the check. **Operational.**

**Never** populate `last_verified_at` from FSQ `date_closed` — Foursquare's own docs: *"The date the POI was marked as closed in our database. This does not necessarily mean the POI actually closed on this date."* That is a database-edit date, exactly the banned kind. Both NULL render as *unknown*, never as "not verified" in a way that reads as "failed verification."

### 8.8 Human-in-the-loop audit

A stratified sample with a pre-registered target, not a vibe check: **~200 shops/quarter** across five strata of 40 — top confidence decile, bottom decile, exactly-one-heuristic-flag, two-or-more-flags, and a uniform random control. Auditors record ground truth using **only permitted means** (visit the shop's own website, check the state registry, check the EPA record — call nothing) and assign exists / correct-location / phone-correct / truck-related / duplicate / closed. Compute per-heuristic precision and recall and **publish them in `status_weekly.md`** alongside the confidence distribution. Store in `quality.ai_decisions` with `decided_by='human'` — it already has the `UNIQUE (job, input_hash, decided_by)` key and the documented human-overrides-ai precedence, so no new table is needed. **Any heuristic whose measured precision drops below ~0.7 is demoted from penalty to advisory flag.** The audit exists to keep the score honest, so its output must be allowed to change the weights.

---

## 9. Proposed architecture

Everything below matches `recon_house-style.md`. Absolute paths under `/home/ujjwal/Documents/truck-intel/`.

### 9.1 Registry source — the route spine

**`registry/ntad_national_network.yaml`** (new). Opens with the house-convention verification comment block (date + HTTP status + row count + licence evidence).

```yaml
# Verified 2026-07-23: FeatureServer?f=json HTTP 200 (5,937 B), layer 0 'National Network'.
#   returnCountOnly: total=478,999 | NN=1 -> 453,529 | NN>0 -> 454,830 | NN=0 -> 24,169
#   distinct ID = 478,999 (unique) ; distinct ROUTEID = 12,491 (state-scoped, NOT a key)
#   copyrightText verbatim: "This NTAD dataset is a work of the United States government as
#   defined in 17 U.S.C. § 101 and as such are not protected by any U.S. copyrights. This work
#   is available for unrestricted public use."
#   Vintage: every row carries VERSION='2020.01.10' and YEAR=2018 (single distinct value).
#   The serviceDescription claims "as of December 22, 2020"; the ROWS say 2018. observed_at=2018.
#   Legal basis: 23 CFR 658 App A (STAA 1982) - https://www.ecfr.gov/current/title-23/.../part-658
#   Service disclaimer: "should not be interpreted as the official National Network and should
#   not be used for truck size and weight enforcement purposes or for navigation."
id: ntad_national_network
name: FHWA/BTS National Network for trucks (STAA, 23 CFR 658) - NTAD FeatureServer
owner: Federal Highway Administration (FHWA) / Bureau of Transportation Statistics (BTS), US DOT
url: https://services.arcgis.com/xOi1kZaI0eWDREZv/arcgis/rest/services/NTAD_National_Network/FeatureServer
kind: arcgis
load_pattern: snapshot_swap
parser: ntad_nn                      # truckintel/parsers/ntad_nn.py
target: core.truck_routes            # add to registry.SNAPSHOT_TARGETS
schedule_minutes: 43200              # monthly; the layer is a 2018-vintage annual-ish publication
license: US public domain (17 U.S.C. §101, NTAD)
attribution: "Acknowledgment of the Federal Highway Administration (FHWA) and the Bureau of Transportation Statistics (BTS) [distributor]."
slo_hours: 2160
gates:
  min_rows: 440000                   # below observed 454,830, above any plausible partial fetch
  max_row_delta_pct: 5
  geometry_valid_pct: 99
  required_fields: [route_segment_id, geom_wkt, nn_code]
auth: null
```

**Query filter.** The engine's `_fetch_arcgis` must be given `NN>0` (the `where` clause belongs in the URL/params for `kind: arcgis`). If the connector has no per-source `where` hook, add one — publishing the 24,169 `NN=0` rows is the single worst failure mode in this build.

**`truckintel/parsers/ntad_nn.py`** (new). Signature `def parse(raw: bytes) -> Iterator[dict]:`. Module docstring lists every yielded key with type and meaning, plus a UNITS section. Behaviours the house style enforces:
- Envelope validation **raises**, never returns `[]`.
- 0-of-N recognizable records ⇒ raise (drift guard).
- Tri-state: unknown → `None`, never `False`.
- Never fabricate geometry: junk coords → `geom_wkt = None`.
- Never emit a garbage PK: `route_segment_id = str(ID) if ID else None` so gate 1 rejects it honestly.
- `observed_at` from the record's own `YEAR` (2018 → `2018-01-01`), following the `nti.py` precedent of deriving vintage from the record's year field. Never the fetch date, never 2020-12-22.
- `route_name` synthesized: `TRIM(SIGN1)` → `SIGNT1`+`SIGNN1` with I/U/S expanded; raw `SIGN1/SIGNT1/SIGNN1` preserved in `props` so the derivation is auditable.
- Keep the whole source record in `props`.

**Allow-list touches:**
- `truckintel/registry.py` `SNAPSHOT_TARGETS` += `"core.truck_routes"`
- `truckintel/engine.py` `_DEDUP_KEY_BY_TARGET` += `"core.truck_routes": "route_segment_id"`
- `truckintel/quality.py` `TABLE_SCORING` += `TableScoring` entries for `core.truck_routes`, `core.route_shops` **and** `core.businesses`
- `api/routes_meta._TABLES` + `_VINTAGE_NOTES` += the new tables, with the 2018-vintage note spelled out

### 9.2 DDL — `sql/schema_wave3.sql` (new, additive, idempotent)

`BEGIN; … COMMIT;` · `CREATE TABLE IF NOT EXISTS` · `ADD COLUMN IF NOT EXISTS` · a header comment carrying the honesty rules and every CHECK's rationale. Every entity table gets `source_id, run_id, ingested_at, observed_at` + `confidence, conf_trust, conf_fresh, conf_complete, conf_agree, flags TEXT[], props JSONB` + a GiST on `geom`.

```
core.truck_routes        route_segment_id TEXT PK (= source ID, verified unique)
                         routeid TEXT, stfips CHAR(2), ctfips CHAR(5),
                         beginpoint/endpoint DOUBLE PRECISION,
                         sign1/signt1/signn1 TEXT, route_name TEXT (derived),
                         nn_code SMALLINT NOT NULL CHECK (nn_code > 0),   -- the NN=0 firewall
                         fclass/facilityt/ownership/urbancode,
                         aadt INT, aadt_com INT, aadt_singl INT,
                         length_m DOUBLE PRECISION,
                         geom geometry(LineString,4326) NOT NULL
core.route_corridors     corridor_id TEXT PK ('I-95'), sign_type, sign_number,
                         segment_count INT, total_length_m, geom geometry(MultiLineString,4326)
                         -- derived rollup; segments carry a corridor_id FK. DO NOT DISSOLVE the
                         -- segments: I-95 alone is 2,926 NN rows and dissolving destroys the
                         -- per-segment milepost / CTFIPS / AADT_COM lineage.
core.route_segments      (route_id, seq) PK, m_start, len_m, frac_start, frac_end,
                         geom geometry(LineString,4326)      -- 5 km chunks from core.route_chunks()
core.route_shops         see §7.7
osm.junctions            osm_id TEXT PK, ref TEXT, name TEXT, geom geometry(Point,4326)
osm.shops                osm_id TEXT PK, shop TEXT, lifecycle TEXT, name, geom,
                         props JSONB (raw tags verbatim)     -- ODbL-isolated; NEVER joined to core.*
census_geo.county        geoid CHAR(5) PK, statefp, countyfp, name, geom(MultiPolygon,4326)
census_geo.zcta          zcta5 CHAR(5) PK, geom(MultiPolygon,4326)
census_geo.state         statefp CHAR(2) PK, stusps CHAR(2), name, geom
                         -- named census_geo.*, NOT tiger.*, per the TIGER trademark restriction
```

Plus, on **every** point layer that participates in route search:
```sql
CREATE INDEX CONCURRENTLY <t>_geog_gix ON <schema>.<table> USING GIST ((geom::geography));
```
Measured: 76.6 bytes/row on `osm.fuel_stations` (8,088 kB, built in 2.67 s), 74.6 bytes/row on `core.bridges` (45 MB, 13.3 s). Budget **75 bytes/row, ~21 µs/row to build**.

Plus `core.route_chunks(route, chunk_m)` (§7.1), `ops.route_shop_progress` (§7.7), and the `google_maps_url` generated column on `core.businesses`:

```sql
ALTER TABLE core.businesses ADD COLUMN IF NOT EXISTS google_maps_url TEXT
  GENERATED ALWAYS AS (
    'https://www.google.com/maps/search/?api=1&query=' ||
    replace(replace(coalesce(name,'') || ', ' || coalesce(address,''), ' ', '%20'), '&', '%26')
  ) STORED;
COMMENT ON COLUMN core.businesses.google_maps_url IS
  'GENERATED from OUR OWN name/address. Contains ZERO Google data. Maps URLs is not a Maps '
  'Platform Core Service (services list rev. 2026-04-22) and needs no API key (docs 2026-07-20). '
  'This column may NEVER be populated from a fetch, and may never feed rating/review/photo '
  'fields - Google ToS 3.2.3(a)(iii)/(b)/(d)(iii)/(e)(i) and SST 14.3 forbid all of those.';
```

Add a `Makefile` target `schema-wave3` next to `schema-wave2`.

### 9.3 Derived jobs

Each is a `scripts/*.py` with its own `_SEED_SQL` + `_start_run`/`_finish_run`, a **structured semicolon-joined fact message counting every exclusion**, `except BaseException` → `failed`, exit 1, and an entry in `engine._DERIVED_RUNNERS`.

| Script | `_DERIVED_RUNNERS` entry | Does |
|---|---|---|
| `scripts/census_geo_job.py` | `"census_geo": [".../census_geo_job.py", "--load"]` | Downloads + loads TIGER county/ZCTA/state into `census_geo.*` via `ogr2ogr`; `observed_at` = TIGER vintage, pinned in the source row |
| `scripts/route_segments_job.py` | `"route_segments": [..., "--build"]` | Densify-if-sparse → `core.route_chunks(geom, 5000)` → `core.route_segments`; per-route `ON CONFLICT` |
| `scripts/route_shops_job.py` | `"route_shops_enrich": [..., "--enrich"]` | Batched buffer join (§7.4/§7.7); writes `core.route_shops` (permissive pool) and, separately, `osm.route_shops` (ODbL pool). `observed_at` = **MIN** of route vintage and shop vintage |
| `scripts/osm_extract.py` **(edit)** | existing `osm_pois` | Add `('highway','motorway_junction')` to `_MATCH_TAGS` + a `_kind()` branch → `osm.junctions`; add the truck-repair tag set → `osm.shops`, **ingesting lifecycle-prefixed rows** (`disused:`/`was:`/`closed:`/`demolished:`) with the prefix in a `lifecycle` column — a `disused:shop=car_repair` at a coordinate is positive evidence an Overture row there is stale |
| `scripts/businesses_pipeline.py` **(edit)** | existing | §8.3 changes: pull `sources`/`operating_status`/`emails`/`socials`, `geometry` not `bbox`, true `observed_at`, per-row trust, confidence floor, independence families, migrate `categories` → `taxonomy` |
| `scripts/conflate_gate.py` **(run first)** | — | Measure before any US-scale conflation |

### 9.4 API

**`api/routes_truck_routes.py`** (new) — `GET /v1/routes` (bbox + `sign_type` + `state` filters), `GET /v1/routes/{route_segment_id}`, `GET /v1/corridors/{corridor_id}`.
**`api/routes_mechanics.py`** (new) — `GET /v1/mechanics` (bbox, `category`, `band`, `route_id` + `buffer_m`), `GET /v1/mechanics/{business_id}`.
**`api/routes_osm_shops.py`** (new) — `GET /v1/osm/shops`, the **explicitly ODbL-attributed, never-merged** layer.
**`api/routes_osm_export.py`** (new) — the **§4.6 affordance**: a free, machine-readable dump of each `osm.*` mirror, linked from `/v1/meta`.

Each follows the module shape exactly: docstring naming the endpoints and source table + **ATTRIBUTION** + **HONESTY** + **INTEGRATOR NOTE** sections; `router = APIRouter()` with full paths in the decorators; module constants `ATTRIBUTIONS`, `_NOTE`, `_SELECT`, enum sets mirroring the DDL CHECK; a `_feature(r)` helper; handler = `common.parse_bbox` → build `where`/`params` → `common.q_all` → `common.feature_collection(..., note=, filter_notes=, attribution=, limit=, offset=)`.

Binding conventions to honour:
- Filters that exclude unknowns **must say so** in `filter_notes`.
- Tri-state booleans render **literally** `true/false/null`, never via `unknown()`.
- Anything derived from `osm.*` carries **`"© OpenStreetMap contributors, ODbL — https://www.openstreetmap.org/copyright"`** on every feature *and* on the collection (`scripts/smoke_endpoints.py:162` already FAILs the build if the OSM string is missing — **update that assertion to require the ODbL text and link too**).
- Anything from `core.businesses` carries the **full CDLA-2.0 text reference + Foursquare NOTICE pointer**, and deliberately **no** OSM attribution, with the reason written out.
- Every feature carries `source_id, run_id, ingested_at, observed_at, confidence` (+ `confidence_components`).
- Route features additionally carry the FHWA/BTS acknowledgment and the *"not for enforcement or navigation"* disclaimer in `_NOTE`.

Registration: two lines in `api/main.py` (import block + include loop). New entries in `scripts/smoke_endpoints.py` `SWEEP` / `PROBES` / `NEGATIVE_PROBES` — **EMPTY is never folded into OK**.

### 9.5 Config, tests, deploy

- `data/config/category_map.yaml` — add `welders`, `welding_supply_store`, FSQ "Welding Service" + "Machine Shop"; add the trap deny-list (`food_truck`, `truck_rentals`, `trailer_rentals`, `game_truck_rental`); migrate keys from `categories.primary` to `taxonomy.primary` paths. `tests/test_businesses_pipeline.py:57` already enforces that every taxonomy slug is mapped or listed in `unreachable_from_sources`. Current file has **67** mappings (43 Overture + 24 FSQ), not "~90".
- `data/config/forbidden_sources.yaml` (new) — Love's, Ryder, TA/Petro, Yelp, Google Maps scraping, YellowPages, Nominatim — each with the **verbatim clause** and the evidence URL, so the decision is never re-litigated.
- Tests, layered per house style: pure parser tests with synthetic-but-format-faithful fixtures (paste a real NN feature); `needs_db` tests against **scratch schemas** using the production functions' `target=`/`staging_*=`/`scoring=` overrides; **parity tests** for any Python↔SQL twin; network tests behind `TRUCKINTEL_NETWORK_TESTS=1`; **never insert fake rows into core tables**. New files: `tests/test_parsers_ntad_nn.py`, `tests/test_route_chunks.py` (gap-free + length-exact + the `ST_LineSubstring(geography)` truncation assertion), `tests/test_route_shops.py`, `tests/test_api_routes.py`, `tests/test_api_mechanics.py`.
- `deploy/truckintel-routes.service` + `.timer` and `deploy/truckintel-route-shops.service` + `.timer` (`Type=oneshot`, `WorkingDirectory=%h/Documents/truck-intel`, `%h/.local/bin/uv run …`, leading `-` only on best-effort steps), plus rows in `deploy/README.md`'s table.

### 9.6 Housekeeping the builder must not skip

- **Close the 5 zombie `osm_ways` runs** stuck in `status='running'` with `finished_at IS NULL` (run_ids 1238, 1261, 1292, 1293, 1333) — `ps` shows no live process and there are no truck/osm systemd timers. Published rows currently carry FKs to runs that never terminated, which violates the "exactly one terminal `ops.source_runs` row" contract.
- **Fix the stale release comment** in `scripts/businesses_pipeline.py` — the docstring and `category_map.yaml` both assert the S3 bucket retains "exactly one release, 2026-06-17.0"; the listing shows **two** (`2026-06-17.0` and `2026-07-22.0`). `max()` behaves correctly but the comment is now false, and the honesty rules apply to comments.
- **Backfill `ops.sources.license` / `attribution_text` for `osm_pois` and `osm_ways`** (§5.2 defect 1).
- **Add `ANALYZE` to `loaders.snapshot_swap`** (§7.8).

---

## 10. Scale + runtime reality

**Box:** 15.9 GB RAM (11.6 GB available), **4 cores**, 254 GB free of 468 GB, DB currently 1,811 MB. Largest tables: `core.bridges` 1,623 MB (incl. TOAST), `osm.ways` 50 MB, `osm.fuel_stations` 45 MB.

**The prior failure that must not repeat.** The full-US OSM ways load died **three times on DiskFull**, and 84% of what it did load was residential/service roads nobody asked for. Measured on the Delaware snapshot: `service` 65,512 + `residential` 26,749 = **84.0%** of 109,777 rows. **That failure mode does not recur here**, because the route spine is a 453,529-row federal polyline layer, not a 60M-way OSM extract — and because the owner's scope rule structurally excludes the noise.

| Workload | Honest national number |
|---|---|
| **NN ArcGIS pull** | 454,830 rows ÷ `maxRecordCount 2000` = **~228 sequential paged requests**. The current `_fetch_arcgis` **accumulates every page into one in-memory merged GeoJSON before returning** — ~450k LineStrings is a real memory spike on a 15 GB box. **Teach the connector to stream/checkpoint before the route layer lands**, or accept a single large allocation and measure it. |
| **`core.truck_routes` storage** | ~450k LineStrings; the geometry dominates. Budget a few hundred MB plus 75 bytes/row of geography index. Trivial against 254 GB free. |
| **`core.route_segments` @ 5 km** | On real dense geometry: 51 vertices, 843 B of geometry, **~900 bytes/row** all-in. Interstates both directions ~154,000 km `[UNVERIFIED mileage]` → ~30,800 segments → **~28 MB**. Full NHS ~354,000 km `[UNVERIFIED]` → ~70,800 → **~64 MB**. |
| **`core.route_shops`** | **342 bytes/row** including all three indexes. This is the only thing that can get big: 5,000,000 links ≈ **1.7 GB** — fits on the box, but no longer fits in 128 MB of `shared_buffers`. Tune per §7.8. |
| **Buffer-enrichment throughput** | 0.40 ms/segment against a 108,056-row point layer · 1.15 ms against 629,710 · **1.73 ms/segment end-to-end including the `DISTINCT ON` collapse** (measured: 1,125 segments × 629,710 bridges in 1,950 ms). Scaling is sub-linear — 5.8× more rows cost 2.9× more time. |
| **Extrapolated national enrichment** | Interstates ~30,800 segments ≈ **53 s per shop layer**; full NHS ~70,800 ≈ **123 s per shop layer**. **Minutes, not hours — provided the geography indexes exist.** Without them the same work is 240× slower and becomes a multi-hour job. (Route-mileage inputs are `[UNVERIFIED]`; the per-segment costs were measured against real national point layers and are the transferable numbers.) |
| **Overture national pull** | 74,223,561 rows across **16 parquet files, ~11.2 GB**. Only **6 files** (parts 00000, 00001, 00002, 00003, 00005, 00006) contain any CONUS row groups — 16,995,025 candidate rows (22.9%). Selecting those files by reading `bbox` row-group statistics via `parquet_metadata()` first (a **footer-only** read) cut a full US category scan to **247 s** and a field-fill scan to **423 s** on a ~2.7 MB/s link. The current glob reads all 16. The pipeline already caps DuckDB at 4 GB with spill-to-disk. |
| **Geofabrik US PBF** | **12,038,018,063 B (11.2 GiB)**, Last-Modified 2026-07-22. Requires `-L` (302 → 206). Junctions and `osm.shops` ride the **same single osmium pass** as the existing POI extract — no extra download. Delaware (21,814,984 B) is the cheap smoke test. **But see the robots.txt ruling in §5.2 before scheduling any automated fetch.** |
| **Conflation blow-up** | 150 m block on 2,981 NYC rows → 52,243 pairs = **17.5 neighbours/row**; the 0.3 name gate cut that to 564 scored pairs. Pair count is O(N × local density) — a national run is dominated by dense metros. Process per-state or per-geohash-5 tile, hard-cap neighbours at 50 per row, and run `conflate_gate.py` first (its `run_as_is` vs `spill_first` verdict triggers at 5M RAM-pressure units). |
| **Spill behaviour** | At `work_mem=1MB` the `DISTINCT ON` collapse over 34,973 rows already spilled to disk (peak 1,360 kB). Batch + `SET LOCAL work_mem='256MB'` + commit per batch, always. |

**Where it breaks.** Three places, all avoidable: (1) a single in-memory ArcGIS merge of ~450k features; (2) a single national `route_shops` query without batching — it will spill hard and may OOM; (3) any national conflation without the geography index, where a 19-second scoring pass becomes a 19-minute one and a 10-second self-block becomes hours.

---

## 11. What the owner must decide

| # | Decision | Options | Recommendation |
|---|---|---|---|
| 1 | **Route spine** | A) NN only (453,529, truck-legal, 2018 geometry) · B) NN + NHS refresh + FAF5 restrictions/direction · C) NHFN-only scaffold (12,989) | **Start with A, land B incrementally.** A is the only option that satisfies "truck-designated as a matter of law" *and* costs almost nothing (`kind: arcgis` already exists). Use C for one afternoon to prove the pipeline, then throw it away — never ship it labelled "US truck routes." |
| 2 | **Geofabrik + Overpass robots.txt** | a) Documented narrow exception per host, rate-capped, contact UA · b) Source the PBF elsewhere · c) Abandon all OSM-derived features (junctions, hours) | **(a), written into the source registry.** `Disallow: *.osm.pbf` on a service Geofabrik advertises as "available for free download" is plainly an anti-crawler directive, but the repo's rule is literal and the exception must be *recorded*, not assumed. Never fetched silently. |
| 3 | **Is the platform publicly used, or internal-only?** | public / internal | **This single answer changes the whole ODbL architecture.** §4.5(c): *"Use of a Derivative Database internally within an organisation is not to the public."* If internal, OSM's ~700 truck shops, its `service:vehicle:*` capability tags and its `opening_hours` all become usable with **zero** share-alike consequence. Decide it consciously rather than inheriting it. |
| 4 | **The §4.6 offer for `osm.*`** | a) Ship a free machine-readable dump + `/v1/meta` link · b) Stop publicly serving `osm.*` endpoints | **(a).** It is a small endpoint and it closes a live, present-tense non-compliance on `/v1/fuel` (108,056 systematically-extracted rows). (b) throws away working features to avoid an afternoon of work. |
| 5 | **Buffer radius, and what it means** | 2 km / 5 km / configurable; straight-line vs drive distance | **5 km, straight-line, labelled as such.** 5 km is also the measured optimal chunk scale. Drive distance requires a routable graph and every free one is ODbL — expose it later as a *separate* field if Valhalla lands, never silently blended. |
| 6 | **Publish `LIKELY_TRUCK` by default?** | CONFIRMED only (~750 OSM + ~11k Overture, high precision) · CONFIRMED+LIKELY (more coverage, name-heuristic risk) | **Expose the band explicitly; default the API to CONFIRMED+LIKELY with a filter.** A stranded driver benefits more from a flagged maybe than from silence — but the flag must be machine-readable, not buried in prose. |
| 7 | **Surface general `automotive_repair` to truckers?** | yes / no / yes-but-ranked-below | Overture has **201,199** `automotive_repair` and FSQ **541,517** — they will numerically drown the 10,858 truck-specific shops. **Yes, but under the honest `auto_repair` slug, ranked strictly below truck-specific, and never relabelled.** The existing category_map decision is correct and must not be softened. |
| 8 | **FSQ: accept the HuggingFace gate?** | a) Accept (current release dt=2026-07-09) · b) Ungated source.coop mirror (frozen 2025-02-06) · c) Skip FSQ entirely | **Boss must be told what he is agreeing to**: the gate licenses Foursquare to use his entity name and logo in marketing material, and requires contact info. That is a real non-monetary obligation, not a "free key." Given the independence finding (FSQ is largely already *inside* Overture), **(c) or (b) is defensible** — measure the coverage delta on one state first. |
| 9 | **Overture `categories` → `taxonomy` migration** | Migrate now / pin a retained release and defer | **Migrate now.** `categories` is removed in the **September 2026** release (~2 months) — *not* June, which has already passed — and the bucket retains only two releases, so pinning has a short shelf life. **Do not migrate to `basic_category`:** it collapses both `truck_repair` and `automotive_repair` into `automotive_service`, destroying exactly the signal this project exists to carry. |
| 10 | **Drop or NULL the impossible fields?** | Drop `average_rating`/`review_count`/`review_summary`/`whatsapp` · keep as permanently-NULL columns | **Drop them.** A 100%-NULL column named "rating" is worse than no column — it is an invitation for a future contributor to "fix" it from a prohibited source. Record the reason in a schema comment and in `forbidden_sources.yaml`. |
| 11 | **`observed_at` for the NN spine** | 2018 (row `YEAR`) · 2020-12-22 (service description) · 2020.01.10 (row `VERSION`) | **2018**, per the repo's precedent of deriving vintage from the record's own year field. Put the other two in `props` and surface the vintage in the UI. Anything implying currency would be misleading by ~8 years. |
| 12 | **Keep `NN=0` rows anywhere?** | Discard · retain in a separate `core.non_nn_routes` flagged `not_on_national_network` | **Retain, separately.** Costs little and preserves the ability to answer "is this road truck-legal?" with a definitive **no** rather than silence — which is a genuinely useful product answer. |
| 13 | **TIGER vintage policy** | Pin 2025 permanently · track latest annually | **Pin, with the vintage encoded in `source_id`** (e.g. `census_geo_2025_county`) so a bump is a deliberate, traceable event and `observed_at` stays reproducible. |
| 14 | **Where does `core.route_shops` live?** | `core.*` (if the spine is federal PD) · `osm.*` (if any OSM geometry contributes) | **`core.*`, conditional on Decision 1 landing on NTAD.** If the spine is ever built from `osm.ways`, the link table must move to `osm.*` — derived geometric facts computed *from* ODbL geometry are ODbL-derived even when no attribute is copied. |

---

## 12. Open questions / still unverified

1. **The absolute US `motorway_junction` count.** 77,676 could not be reproduced — every Overpass instance failed (504 / 406 / expired cert / a regional instance silently returning 0). A CONUS bbox gives 81,439 nodes with 50,704 refs = **62.26%**, so the honesty-critical *ratio* is independently confirmed but the total must be **recounted from the PBF at ingest**. Delaware (424) reproduced exactly.
2. **Whether a GeoJSON API response is a Produced Work under ODbL is genuinely unsettled.** The Licensor's own stated test points clearly one way ("intended for the extraction of the original data… is a database"); the Geocoding Guideline's two-database concurrent-search example points partly the other. No court has ruled. Confident about the *direction*; not confident there is a bright line.
3. **Whether ODbL share-alike is enforceable against a US-only, US-hosted product beyond contract.** §10.4 defers to the enforcing jurisdiction and the US has no sui generis database right. A question for a lawyer, not for this brief — and the reason the honest framing is "breach of contract," never "you will get sued."
4. **HPMS chain of title.** The federal geometry under the National Network is *"a compilation of data collected from many State Departments of Transportation."* State submissions are not federal works under §105. Practical risk low; **not a closed question.** Record as residual.
5. **Overture per-row provenance is asserted, not measured, in the repo.** The blanket "Places contains no OpenStreetMap data" is strong and I verified zero `osm` rows over one parquet part — but the ingest trusts it globally. **Add a test that fails if any ingested Overture row carries an OSM-derived `sources[].dataset`.** That is the one place where "core is OSM-free" is asserted rather than measured.
6. **`sources[].dataset` literal string values.** The independence logic keys entirely off them (`meta` vs `Meta`? `Microsoft` vs `msft`?). Read them off the actual parquet before writing the family map. Ten strings are known to exist including `SparkGeo-confidence-conflation`.
7. **Fill rate of `operating_status` and `sources[].update_time` for US `truck_repair`.** The fields exist in the schema; the pipeline never pulled them, so the fill rate is unknown. One DuckDB query against the S3 parquet — **run it before designing around them.**
8. **Is Overture's per-place `confidence` comparable across source datasets?** A meta-sourced 0.7 and a BrightQuery-sourced 0.7 may not mean the same thing, and the March-2026 normalization incident (rolled back in April, ~10M places rescored) suggests it is not stable even within one source over time. If not comparable, per-dataset calibration is needed rather than a single global multiplier.
9. **How many US mechanic shops does EPA RCRA actually cover?** The join works and a real match was pulled, but national recall is unmeasured. Measurable by pulling NAICS 811111/811310/423120 for one state and joining to a completed Overture extract for that state. Absence must never subtract confidence, but the expected match rate determines the scoring weight.
10. **Local Calling Guide has no published licence.** `/terms.php` 404s; `robots.txt` disallows only `/cgi-bin/`. Before it becomes a pipeline dependency, get written permission from the operator or find the LERG-derived NPA-NXX data from a source with explicit terms. It is the weakest link in the verification design.
11. **Will `nationalnanpa.com` come back?** Its authoritative nameserver is currently REFUSING queries — an outage or migration rather than a shutdown. If it returns, its published NPA reports are the authoritative upstream and should displace LCG. Worth a periodic re-probe.
12. **Overture's national truck-repair conflation survival rate.** How many of the 10,858 `truck_repair` rows survive the existing 150 m / 0.85 conflation? Because FSQ has **no** truck category, every merge will be against a general "Automotive Repair Shop" record, so the 0.55-0.85 gray band is expected to be unusually wide. **Needs a real conflation dry-run before anyone quotes a final national figure.**
13. **Optimal chunk size on real national geometry.** 5 km was measured on the only dense real route available (101 m vertex spacing, Delaware, TIGER-derived). Interstate geometry in the western US may be far less densely vertexed, which would shift the optimum. Re-run the sweep once national geometry is loaded.
14. **`ST_LineSubstring(geography)` upstream status.** Reproduced deterministically on 3.4.3; no matching trac ticket found; 3.5.x untested. Worth confirming against a newer PostGIS before filing — and worth pinning the PostGIS version in `deploy/` either way.
15. **Freshness SLO for derived tables.** `route_shops.observed_at` should be the MIN of (shop vintage, route vintage) — but with a 2018 route spine that makes every derived row look 8 years stale and will trip the freshness checker. Does the SLO apply to the derived table, or only to its inputs?
16. **Whether the ~11,000-12,000 national truck-shop estimate survives contact with reality.** It is an arithmetic union of measured category counts, not a measured post-conflation figure, and Overture demonstrably over-counts against Census for comparable activities. Treat it as an order of magnitude, not a number to publish.
17. **AllThePlaces bulk-download URL.** The `/builds.html` page is JavaScript-rendered and the historical `alltheplaces-data.openaddresses.io` paths now 404/416. Someone must read the live URL off the page before a fetcher is written, and skim `docs/WHY_SPIDER.md` so the owner is comfortable with the provenance of a CC0 dataset produced by scraping brand store-locator pages.
18. **Whether per-state licence-registry ingestion is worth it beyond NY/NJ/CT.** Each state is a bespoke integration; CA — despite legally licensing every repair dealer — publishes only aggregates and would need a Public Records Act request. The payoff is `verification_status`, which nothing else can fill honestly.

---

*Every count in this document was measured on the wire or on the live DB on 2026-07-22/23. Where a verification pass corrected a researcher, the corrected fact is what appears above and the refuted claim appears nowhere. Items that could not be verified are tagged `[UNVERIFIED]` and are never presented as fact.*
