# Truck Routing Base Network + Freight Corridors — Legal Source Inventory

**Category:** Base road/truck network data + freight corridors + self-hosted routing engines
**Researched:** 2026-07-22 (all URLs verified live on this date via web search + direct fetch, unless marked UNCERTAIN)
**Constraint honored:** Free + legally authorized sources only. No paid APIs, no scraping behind auth/paywalls.

---

## TL;DR — Recommended Stack (for a solo dev, boring-tech)

| Layer | Source | Why |
|---|---|---|
| Routable base network | **OpenStreetMap** (Geofabrik US extract) | Only free nationwide network with actual truck restriction tags AND routing topology |
| Routing engine | **Valhalla** (self-hosted, MIT) | Per-request truck height/weight/length/hazmat — no graph rebuild per vehicle |
| Official truck network overlay | **NTAD National Network (STAA)** + **NTAD NHS** | Federal designation layers, public domain, ArcGIS REST + bulk download |
| Freight corridors | **FAF5 Network Links + Highway Network Assignments** | Official truck flow volumes by link (2017/2022/2050) |
| Attribute enrichment | **HPMS 2023/2024** (geodata.bts.gov) | Truck AADT (single-unit + combination), functional class, NN flag per segment |
| Cross-reference geometry | **Census TIGER/Line 2025** | Public domain, county-level all-roads, good for conflation/geocoding |

Pipeline sketch: `Geofabrik .osm.pbf → Valhalla tiles` for routing; federal layers loaded into PostGIS as display/analysis overlays. That's 2 moving parts. Simple, boring, all free.

---

## 1. NTAD / BTS Geospatial Portal (the front door for federal layers)

The **National Transportation Atlas Database (NTAD)** from the Bureau of Transportation Statistics is the umbrella under which NHS, National Network, FAF5, and HPMS geospatial layers are published. Main portal: https://geodata.bts.gov (ArcGIS Hub). Every NTAD dataset checked carries this statement (verified directly from the FeatureServer metadata):

> "This NTAD dataset is a work of the United States government... not protected by any U.S. copyrights. This work is available for unrestricted public use."

That means: **public domain, no attribution legally required (courtesy attribution recommended), no auth, no cost, no rate-key.** Every dataset is downloadable as Shapefile / File Geodatabase / GeoJSON / CSV from the Hub page AND queryable via ArcGIS REST FeatureServer.

Note: `bts.gov` HTML pages returned HTTP 403 to automated fetch during this research (bot protection on the informational site), but the actual data endpoints (`geodata.bts.gov`, `services.arcgis.com/xOi1kZaI0eWDREZv/...`, `geo.dot.gov`) responded fine. Plan your automation against the data endpoints, not the brochure pages.

---

## 2. Source-by-Source Inventory

### 2.1 National Highway System (NHS) — OFFICIAL

| Field | Value |
|---|---|
| Owner | FHWA, published via USDOT/BTS NTAD |
| Official URL | https://geodata.bts.gov/datasets/usdot::national-highway-system-nhs/about |
| REST endpoint (verified live) | https://services.arcgis.com/xOi1kZaI0eWDREZv/arcgis/rest/services/NTAD_National_Highway_System/FeatureServer/0 |
| Also on | https://catalog.data.gov/dataset/national-highway-system-nhs1 (data.gov catalog entry) |
| Coverage | All 50 states + DC + PR, polyline |
| Update frequency | Periodic; current version **2025.08.08** (verified from layer metadata) — roughly annual refreshes |
| Data quality | High. Authoritative federal designation layer. Includes Interstates, other principal arterials, STRAHNET, STRAHNET connectors, intermodal connectors. Key fields verified: `NHS` (subsystem code), `SIGN1/SIGNT1/SIGNN1` (route signing), `CONNID/CONNDES/CONNMILES` (intermodal connectors), `FACILITYT`, `AADT`, `AADT_COM` (combination trucks), `AADT_SINGL` (single-unit trucks) |
| License | US Government work — public domain, "unrestricted public use" |
| Access method | ArcGIS REST (query, GeoJSON out), bulk download (SHP / FGDB / GeoJSON / CSV) via Hub page |
| Auth | None |
| Cost | Free |
| Advantages | Authoritative; includes truck AADT split; STRAHNET + intermodal connectors are exactly the "freight-relevant highway" signal; maxRecordCount 2000 with pagination supported |
| Limitations | Designation layer, NOT a routable graph (no topology guarantees, no turn restrictions); no physical truck restrictions (no height/weight limits) |
| Label | **OFFICIAL** |

**Truck relevance:** NHS identifies which roads matter federally; the `NHS` code distinguishes subsystems (Interstate, STRAHNET, MaJor Strategic Connectors, intermodal connectors). Truck-restricted roads are NOT identified here — it's a positive designation layer only.

### 2.2 National Network (NN) — the STAA designated truck network — OFFICIAL

| Field | Value |
|---|---|
| Owner | FHWA, published via USDOT/BTS NTAD |
| Official URL | https://geodata.bts.gov/datasets/usdot::national-network/about |
| REST endpoint (verified live) | https://services.arcgis.com/xOi1kZaI0eWDREZv/ArcGIS/rest/services/NTAD_National_Network/FeatureServer |
| Legal basis | 23 CFR 658 + Appendix A (STAA of 1982) — https://www.ecfr.gov/current/title-23/chapter-I/subchapter-G/part-658 |
| Coverage | Nationwide, 200,000+ miles of highway, polyline |
| Update frequency | **Infrequent — current geospatial version is dated December 22, 2020** (verified from service metadata). The NN itself changes rarely by law, so staleness is less harmful than it sounds |
| Data quality | Good for display/planning. **Official disclaimer verified:** the file "should not be interpreted as the official National Network and should not be used for truck size and weight enforcement purposes or for navigation" |
| License | US Government work — public domain, "unrestricted public use" |
| Access method | ArcGIS REST + bulk download (SHP / FGDB / GeoJSON / CSV) |
| Auth | None |
| Cost | Free |
| Advantages | This IS the federal STAA truck network — where 102" wide / twin-trailer STAA vehicles are guaranteed access. Perfect "truck-preferred corridor" overlay |
| Limitations | 2020 vintage; expressly not for enforcement/navigation; states designate additional/"reasonable access" routes not in this file; no restriction attributes |
| Label | **OFFICIAL** |

**Truck relevance:** NN is the inverse of a restriction layer — it says where big trucks are *allowed by federal law*. Roads off the NN aren't necessarily restricted; state/local rules govern there. Treat NN as a preference/scoring signal (Valhalla's `use_truck_route` maps well conceptually), never as a hard filter.

### 2.3 HPMS — Highway Performance Monitoring System — OFFICIAL

| Field | Value |
|---|---|
| Owner | FHWA Office of Highway Policy Information |
| Official URLs | Program: https://www.fhwa.dot.gov/policyinformation/hpms.cfm · Shapefile page (verified live): https://www.fhwa.dot.gov/policyinformation/hpms/shapefiles.cfm · **HPMS 2023:** https://geodata.bts.gov/datasets/483bd180fe814872b82a66dbf65e25f0 · **HPMS 2024:** https://geodata.bts.gov/datasets/5e6a977c2d7c4ec1bdc82e684d3384f2 |
| Per-state REST (verified pattern) | `https://geo.dot.gov/server/rest/services/Hosted/{State}_2018_PR/FeatureServer` (2018 release) and `https://geo.dot.gov/server/rest/services/Hosted/HPMS_FULL_{ST}_2023/FeatureServer` (2023) |
| Coverage | All 50 states + DC + PR; ARNOLD (All Road Network Of Linear-referenced Data) geometry + section attributes |
| Update frequency | Annual state submittals; public geospatial release lags ~1.5–2 years (2024 is latest published on geodata.bts.gov as of research date; 2023 marked BETA) |
| Data quality | High for attributes (AADT, truck AADT by single-unit/combination, functional system, NHS flag, **NN "National Truck Network" data item per HPMS Field Manual**, IRI pavement condition, toll fields). FHWA's own warning on the shapefile page: "Use of these data for navigation is not recommended. The user assumes the risk." |
| License | No explicit statement on the FHWA page; the geodata.bts.gov NTAD copies carry the standard US Government public-domain statement. Treat as public domain (US Gov work) |
| Access method | Bulk download per state (zip shapefiles), File Geodatabase/SHP/GeoJSON/CSV from geodata.bts.gov, ArcGIS REST per state on geo.dot.gov |
| Auth | None |
| Cost | Free |
| Advantages | The richest free per-segment attribute source: truck volumes, functional class, NN membership, toll-charged flags. HPMS Field Manual (https://www.fhwa.dot.gov/policyinformation/hpms/fieldmanual/) documents every data item |
| Limitations | Not routable; linear-referenced sections need conflation onto your network; big files; release lag; attribute completeness varies by state (states self-report) |
| Label | **OFFICIAL** |

**Truck relevance:** HPMS carries the **NN data item** (per 23 CFR 658 Appendix A, verified in the Field Manual) and truck AADT — so it's how you *quantify* truck usage per segment. It has no height/weight restriction limits.

### 2.4 FAF5 — Freight Analysis Framework (network + flows) — OFFICIAL

| Field | Value |
|---|---|
| Owner | BTS + FHWA partnership |
| Official URLs | Program (verified live): https://ops.fhwa.dot.gov/freight/freight_analysis/faf/ · FAF data portal: https://www.bts.gov/faf (exists; returned 403 to automated fetch — bot protection, use for humans) · **Network Links:** https://data-usdot.opendata.arcgis.com/datasets/usdot::freight-analysis-framework-faf5-network-links/about · **Highway Network Assignments:** https://hub.arcgis.com/datasets/9343414b46794fb8be9867db2d1ccb75 (item metadata verified live via arcgis.com sharing API) |
| Coverage | Nationwide network model: **487,384 links / 348,498 nodes**, topologically connected |
| Update frequency | FAF5 base year 2017 (from 2017 Commodity Flow Survey); assignments published 2022-04-11, metadata updated 2024-08-27 (verified). OD flow tables get periodic annual-ish refreshes (FAF5.x point releases) — exact cadence UNCERTAIN |
| Data quality | High for planning-scale freight corridor analysis. Assignment tables give truck flows by link for 2017/2022/2050, split Total / Single Unit / Combination and domestic / import / export. Modeled (not observed) volumes |
| License | "This work is available for unrestricted public use" (verified in item metadata) — US Gov public domain |
| Access method | Bulk download: SHP / FGDB / CSV / spreadsheet; ArcGIS REST for network layers; CSV/Access for OD flow database |
| Auth | None |
| Cost | Free |
| Advantages | The ONLY free national truck-flow-by-link dataset. Join assignment tables to network links → instant freight corridor heat map. Topologically connected (can even path-build on it for planning) |
| Limitations | Planning-grade geometry (not navigation-grade); 2017 base year; flows are model estimates; network is its own geometry (needs conflation to OSM/NHS for display alignment) |
| Label | **OFFICIAL** |

**Truck relevance:** FAF5 = freight corridors. No restrictions; it identifies where trucks flow, not where they can't go.

### 2.5 FHWA Toll Facilities — OFFICIAL

| Field | Value |
|---|---|
| Owner | FHWA Office of Highway Policy Information |
| Official URLs | https://www.fhwa.dot.gov/policyinformation/tollpage/ · Dataset (verified live via Socrata API): https://data.transportation.gov/Roadways-and-Bridges/Toll-Facilities-in-the-United-States-Toll-Faciliti/tfnc-995b |
| Coverage | US toll facilities in operation / financed / under construction; latest edition covers 2023 (verified) |
| Update frequency | Biennial report; dataset metadata says annual (R/P1Y); last modified Jan 2025 (verified) |
| Data quality | Good as an inventory (facility name, operator, road, mileage). **Tabular — no geometry.** No toll *prices* per segment, no truck rate schedules |
| License | Public Domain U.S. Government (USGOV_WORKS) — verified in Socrata metadata |
| Access method | Socrata: CSV export + OData + SODA JSON API |
| Auth | None (SODA app token optional, raises rate limits, free) |
| Cost | Free |
| Advantages | Official national toll facility inventory; easy CSV/OData |
| Limitations | No geometry (must join by road name/state — fuzzy); no live or truck-class toll pricing. HPMS `TOLL_CHARGED`/`TOLL_ID` fields + OSM `toll=yes` tags are the geometric complements |
| Label | **OFFICIAL** |

### 2.6 Census TIGER/Line Roads — OFFICIAL

| Field | Value |
|---|---|
| Owner | U.S. Census Bureau |
| Official URLs (verified live) | https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html · FTP: https://www2.census.gov/geo/tiger/TIGER2025/ |
| Coverage | Nationwide. `tl_2025_us_primaryroads.zip` (nation), primary+secondary per state, ALL roads per county (~3,200 county files) |
| Update frequency | Annual; **2025 edition released Sept 23, 2025** (verified), boundaries as of Jan 1, 2025 |
| Data quality | Good geometry/completeness for existence of roads; MTFCC feature-class codes; road names + address ranges. No speeds, no lanes, no truck anything, weak topology for routing |
| License | US Government work — public domain |
| Access method | Bulk download (zip shapefiles) via web UI or direct FTP/HTTPS; also TIGERweb REST services (ArcGIS-style) at tigerweb.geo.census.gov |
| Auth | None |
| Cost | Free |
| Advantages | Public domain (no ODbL share-alike concerns), stable annual snapshots, county-level granularity, great for geocoding/conflation QA |
| Limitations | NOT suitable as a routing network (no restrictions, no speeds, no one-way reliability at scale); use as reference/cross-check layer only |
| Label | **OFFICIAL** |

### 2.7 OpenStreetMap — the routable base network — COMMUNITY

#### 2.7a Geofabrik extracts (primary acquisition path)

| Field | Value |
|---|---|
| Owner | Data © OpenStreetMap contributors; extracts served by Geofabrik GmbH |
| Official URLs (verified live) | https://download.geofabrik.de/north-america/us.html (US: `us-latest.osm.pbf`, **11.2 GB**, data current to 2026-07-18 at check time) · regional: us-northeast (1.7 GB), us-south (3.8 GB), etc. · per-state files (e.g. …/us/texas.html) |
| Coverage | Full US, updated **daily** |
| Update frequency | Daily extract rebuilds; minutely diffs available from planet.openstreetmap.org if you want continuous updates (pyosmium/osmosis) |
| Data quality | Best free routable network in the US: topology, one-ways, turn restrictions, speed limits, and **the only nationwide free source of truck restrictions**. Coverage of truck tags is uneven (dense metros/known low bridges well-tagged; rural gaps). Community-maintained — verify critical restrictions against state DOT sources |
| License | **ODbL 1.0** (verified at https://www.openstreetmap.org/copyright): attribution required ("© OpenStreetMap contributors"), share-alike on *derived databases*, commercial use allowed |
| Access method | Bulk HTTP download (.osm.pbf / .shp.zip), no auth, no key |
| Auth | None |
| Cost | Free |
| Advantages | Feeds every open routing engine directly; daily freshness; state-sized chunks keep a solo dev's pipeline light |
| Limitations | ODbL share-alike: if you mix OSM into a derived database and publish it, that database must be ODbL. Keep proprietary/other layers *separate* (a "collective database") to avoid contaminating them. Attribution UI requirement is real — plan for it |
| Label | **COMMUNITY** |

**How truck restrictions are identified in OSM (tags verified via https://wiki.openstreetmap.org/wiki/Key:hgv):**

| Tag | Meaning |
|---|---|
| `hgv=yes/no/designated/destination/discouraged/delivery` | Legal truck access per way; `designated` ≈ signed truck route |
| `maxheight` / `maxwidth` / `maxlength` | Physical dimension limits (bridges, tunnels, tight streets) |
| `maxweight`, `maxaxleload`, `maxweightrating:hgv` | Weight limits |
| `hazmat=yes/no/designated` | Hazardous materials permissions |
| `hgv:conditional` | Time/condition-based restrictions (e.g. night bans) |
| `toll=yes`, `toll:hgv=yes` | Toll roads incl. truck-specific tolling |

These are exactly the tags Valhalla/GraphHopper/ORS truck profiles consume — which is why OSM must be the routing base, with federal layers as overlays.

#### 2.7b Overpass API (targeted queries, not bulk)

| Field | Value |
|---|---|
| Owner | OSM ecosystem; main public instance run by FOSSGIS (overpass-api.de) |
| Official URL (policy verified) | https://wiki.openstreetmap.org/wiki/Overpass_API |
| Coverage | Whole planet, minutely fresh |
| Update frequency | Near-real-time |
| Usage policy | Main instance fair use: **<10,000 queries/day and <1 GB/day**, must send identifying `User-Agent`/`Referer`. Commercial use permitted. Other public instances exist (private.coffee etc.); Geofabrik runs a *paid* keyed instance |
| License | Data ODbL; software AGPLv3 if self-hosting |
| Access | HTTP API (Overpass QL), XML/JSON out |
| Auth / Cost | None / Free within fair use |
| Advantages | Perfect for the *delta* problem: "give me all ways with `maxheight` in Ohio changed since X" without re-downloading a state |
| Limitations | Not for full-network pulls; shared instance = be a good citizen or self-host |
| Label | **COMMUNITY** |

### 2.8 Overture Maps — transportation theme — OPEN

| Field | Value |
|---|---|
| Owner | Overture Maps Foundation (AWS/Meta/Microsoft/TomTom-founded Linux Foundation project) |
| Official URLs (verified live) | https://docs.overturemaps.org/guides/transportation/ · access: https://docs.overturemaps.org/getting-data/cloud-sources/ · https://github.com/OvertureMaps/data |
| Coverage | Global incl. full US; road `segment` LineStrings largely OSM-derived + conflated |
| Update frequency | Monthly releases |
| Data quality | Good and improving; schema-normalized (restrictions expressed in a structured schema rather than raw tags). Younger than OSM tooling ecosystem |
| License | Transportation theme: **ODbL** (verified) |
| Access method | Cloud-native **GeoParquet** on S3 (`s3://overturemaps-us-west-2/release/...theme=transportation/`) + Azure Blob; query with DuckDB or the `overturemaps` Python CLI — download only what you need, no auth |
| Auth / Cost | None / Free (standard S3 egress paid by Overture's buckets — requester does NOT pay) |
| Advantages | DuckDB + Parquet is delightfully boring-tech; pre-normalized schema; monthly stable snapshots |
| Limitations | Routing engines (Valhalla/OSRM/GH) natively eat `.osm.pbf`, NOT Overture parquet — conversion adds complexity. Same ODbL obligations as OSM. For a solo dev: use OSM directly for routing; consider Overture only for analytics |
| Label | **OPEN** |

### 2.9 Legacy / adjacent federal layers (know they exist, probably skip)

| Source | URL | Verdict |
|---|---|---|
| FHWA National Highway Planning Network (NHPN) MapServer | https://maps3.arcgisonline.com/ArcGIS/rest/services/A-16/FHWA_National_Highway_Planning_Network/MapServer | Legacy; superseded by NTAD NHS layer. OFFICIAL |
| USGS National Transportation Dataset (NTD) | https://www.sciencebase.gov/catalog/item/4f70b1f4e4b058caae3f8e16 | Cartographic roads for topo maps; not truck-relevant. OFFICIAL |
| State DOT truck-route GIS (e.g. Caltrans STAA layer: https://www.arcgis.com/home/item.html?id=69f376572cda48d09311346bc03abf9b, Kentucky NTN PDF) | varies | Valuable per-state supplements for *state-designated* truck routes, but a 50-state patchwork with inconsistent schemas — belongs to the "commercial vehicle restrictions" category's deep-dive. OFFICIAL (per state) |
| data.gov catalog entries | https://catalog.data.gov/dataset?tags=hpms etc. | Catalog only — always resolves back to the endpoints above. Some individual slugs 404 as they get re-harvested; search the catalog rather than bookmarking slugs |

---

## 3. Self-Hosted Routing Engines for Truck Profiles

All four consume OSM `.osm.pbf` directly (Geofabrik → engine). Verified license + truck capability for each:

| Engine | License (verified) | Truck restrictions | Per-request truck dimensions? | Notes |
|---|---|---|---|---|
| **Valhalla** | MIT (verified from repo README: "Valhalla... use[s] the MIT License") | Reads maxheight/maxweight/hazmat etc. from OSM at tile build | **YES — fully.** `costing: "truck"` with per-request `height, width, length, weight, axle_load, axle_count, hazmat, top_speed, use_truck_route, hgv_no_access_penalty, low_class_penalty` (verified in API docs, with defaults e.g. height 4.11 m, weight 21.77 t) | Dynamic costing = one graph serves every truck config. Also does isochrones, matrix, map-matching. **Best fit for this platform** |
| **GraphHopper** (open-source core) | Apache-2.0 (verified) | Encoded values for max_height/max_weight/hazmat; ships `truck.json` custom model | **YES with caveat** — JSON custom models can be sent per request, but only in flexible mode (`ch.disable=true`), which is slower than prepared CH mode | Java; excellent docs (github.com/graphhopper/graphhopper docs/core/custom-models.md). Solid #2 choice |
| **OpenRouteService** | GPL-3.0 / LGPL-3.0 (verified from repo) | `driving-hgv` profile | **YES** — `options.profile_params.restrictions`: length, width, height, axleload, weight, hazmat + `vehicle_type` (verified in ORS docs/forum). No defaults — unset = unrestricted | Built on a forked GraphHopper 4.0. Heavier to self-host; GPL matters only if you modify+distribute the engine itself |
| **OSRM** | BSD-2-Clause (verified) | Only what you bake into the Lua profile | **NO.** Costs are baked at graph build time; dynamic per-request dimensions are architecturally unsupported (verified via maintainer issue threads #6522, #4504). Workaround = pre-build N graphs for N truck classes | Fastest per-query engine, but wrong tool for "enter your truck's dimensions" UX |

**Recommendation:** Valhalla. One graph, per-request dimensions, MIT license, active project, and its `use_truck_route` preference conceptually mirrors the NN/STAA overlay. GraphHopper is the fallback if you prefer JVM/Java tooling.

---

## 4. How Truck-Restricted Roads Are Identified — per source (honest summary)

| Source | What it tells you about trucks | What it does NOT tell you |
|---|---|---|
| NHS | Which roads are federally significant; STRAHNET; intermodal connectors; truck AADT | Any restriction |
| National Network (NN) | Where STAA-dimension trucks are federally guaranteed access | Restrictions; state/local truck routes; anything current (2020 file); not legal for enforcement |
| HPMS | NN membership per section; truck AADT single/combination; toll-charged flag | Height/weight/dimension limits |
| FAF5 | Where freight actually flows (modeled volumes by link) | Restrictions |
| TIGER/Line | That a road exists, its class + name | Anything truck-related at all |
| Toll Facilities | Which named facilities are tolled | Geometry; prices; truck rates |
| **OSM** | **Actual per-edge restrictions: maxheight, maxweight, hgv=no, hazmat, conditional bans, truck-designated routes** | Guaranteed completeness — community coverage varies; always signpost "verify posted signs" |

Bottom line: **OSM is the only free source of actual restrictions on the network; every federal layer is designations and volumes.** That's not a flaw in the plan — it's why the architecture is "OSM base + federal overlays."

---

## 5. Licensing / Compliance Checklist

1. Federal layers (NTAD, HPMS, FAF5, TIGER, toll data): public domain. Courtesy-attribute "USDOT BTS NTAD" — good practice, keeps provenance visible.
2. OSM + Overture transportation: **ODbL** — show "© OpenStreetMap contributors" in the app; keep OSM-derived databases separate from other layers (collective database pattern) so share-alike doesn't cascade; if you publish an improved restriction database derived from OSM, it must be ODbL.
3. Overpass public instance: <10k queries/day, <1 GB/day, real User-Agent. If the platform needs more, self-host (AGPLv3) or stick to Geofabrik bulk + diffs.
4. Geofabrik download server: free, no key, daily files — don't hammer it; one daily state-level pull is well within norms.
5. NN + HPMS carry explicit "not for navigation/enforcement" disclaimers — surface an equivalent disclaimer in the product UI.

---

## 6. Honest Gaps (no free/legal source exists)

1. **Nationwide authoritative per-road legal truck restriction database (posted height/weight/length limits, local truck bans).** OSM is best-effort community coverage; the curated versions are commercial (HERE, TomTom, Trimble Maps/PC*Miler, ProMiles, INRIX). State DOT GIS fills some states, not all, with inconsistent schemas. **This is the paid gap** — mitigate with OSM + NBI bridge clearances (bridge category) + per-state DOT layers, and say so honestly in the product.
2. **Current-year official National Network geometry** — the free geospatial NN file is 2020-vintage and legally non-authoritative; the authoritative NN is the 23 CFR 658 Appendix A *text* + state supplements, not a maintained national GIS layer.
3. **Toll geometry + truck toll pricing** — FHWA toll data is tabular, biennial, priceless (literally). No free national toll-rate API exists (TollGuru et al. are paid). OSM `toll=yes` gives geometry; prices remain a paid gap.
4. **Navigation-grade commercial truck attributes** (legal speed for trucks by state, differential speed limits, engine-brake ordinances) — no consolidated free source; state patchwork only.
5. **Observed (not modeled) truck volumes on all links** — FAF5 assignments are model output from a 2017 base; real-time/observed truck GPS flow data (e.g. ATRI truck GPS) is restricted/paid.

---

## 7. Verification Log

| Claim | How verified | Date |
|---|---|---|
| NTAD NHS FeatureServer live, v2025.08.08, public domain, truck AADT fields | Direct fetch of REST `?f=pjson` | 2026-07-22 |
| NTAD National Network FeatureServer live, 2020-12-22 vintage, disclaimer + public domain | Direct fetch of REST `?f=pjson` | 2026-07-22 |
| HPMS shapefiles page (2018 by-state) + geo.dot.gov per-state FeatureServers | Direct fetch of fhwa.dot.gov page | 2026-07-22 |
| HPMS 2023 (BETA) + 2024 on geodata.bts.gov, FGDB/SHP/GeoJSON/CSV | Web search results incl. dataset IDs | 2026-07-22 |
| HPMS "NN / National Truck Network" data item exists (23 CFR 658) | Web search of HPMS Field Manual | 2026-07-22 |
| FAF5 network 487,384 links / 348,498 nodes; assignments 2017/2022/2050 by truck type; "unrestricted public use" | FHWA ops page fetch + ArcGIS item metadata fetch | 2026-07-22 |
| Toll Facilities dataset tfnc-995b: USGOV_WORKS license, annual, 2023 edition | Direct fetch of Socrata `/api/views/tfnc-995b.json` | 2026-07-22 |
| TIGER 2025 released 2025-09-23; FTP TIGER2025 | Direct fetch of census.gov page | 2026-07-22 |
| Geofabrik us-latest.osm.pbf 11.2 GB, daily, ODbL | Web search of download.geofabrik.de pages | 2026-07-22 |
| Overpass fair-use 10k q/day, 1 GB/day; commercial OK | Fetch of OSM wiki Overpass page | 2026-07-22 |
| ODbL attribution + share-alike | Fetch of openstreetmap.org/copyright | 2026-07-22 |
| Valhalla MIT + full per-request truck costing options | Fetch of valhalla repo + API reference | 2026-07-22 |
| OSRM BSD-2-Clause + build-time-only restrictions | Web search (LICENSE.TXT + issues #6522/#4504) | 2026-07-22 |
| GraphHopper Apache-2.0 + truck.json custom models | Web search (repo + docs) | 2026-07-22 |
| ORS GPL-3.0/LGPL-3.0, GraphHopper-4.0 fork, driving-hgv restrictions | Fetch of GIScience/openrouteservice repo + docs search | 2026-07-22 |
| Overture transportation ODbL, GeoParquet on S3/Azure, monthly | Docs search (docs.overturemaps.org) | 2026-07-22 |

UNCERTAIN items are labeled inline (FAF5 flow-refresh cadence; exact bts.gov human-page availability under bot protection).

---

## Verification (adversarial pass)

**Verifier:** independent adversarial re-check, 2026-07-22. Method: WebFetch of every claimed URL (or its data endpoint when the Hub "about" page is JS-rendered and returns title-only to non-browser clients), plus raw-doc grep for Valhalla costing options. Default stance: refute; UNCERTAIN unless directly confirmed.

| # | Source | Status | Evidence |
|---|---|---|---|
| 1 | Geofabrik US extract | **CONFIRMED** | Page live; `us-latest.osm.pbf` offered at exactly 11.2 GB, last modified ~7 h before check (data ts 2026-07-21); license stated ODbL 1.0; no anti-automation restriction on the download page. |
| 2 | Valhalla | **CONFIRMED** | Repo live and active (v3.8.2, 2026-07-08); MIT license shown on GitHub. Per-request truck costing verified in `docs/docs/api/route/api-reference.md`: `truck` costing with request-time `height` (default 4.11 m), `width`, `length`, `weight` (default 21.77 t), `axle_load`, `axle_count`, `hazmat`, `top_speed`, `use_truck_route`, `hgv_no_access_penalty` — every claimed option present. Consumes OSM data via Mjolnir. |
| 3 | NTAD National Network | **CONFIRMED** | FeatureServer live (`services.arcgis.com/xOi1kZaI0eWDREZv/.../NTAD_National_Network`); 200,000+ mi STAA network description; "unrestricted public use" public-domain statement verbatim in service metadata; 2020-12-22 vintage confirmed; "not for enforcement/navigation" disclaimer confirmed. Hub "about" page is JS-rendered (title-only to bots) — automate against the REST endpoint, as the researcher advised. |
| 4 | NTAD NHS | **CONFIRMED** | FeatureServer layer 0 live, version 2025.08.08 exactly as claimed; fields `AADT_COM`, `AADT_SINGL`, `NHS` subsystem codes (incl. STRAHNET 3/4, intermodal 8/9) all present; public-domain distribution terms confirmed (metadata-inclusion courtesy request only). |
| 5 | FAF5 Network Links + Assignments | **CONFIRMED** | ArcGIS item (owner USDOT_BTS) carries verbatim "unrestricted public use" license; FHWA ops page live and offers free downloadable truck-flow assignments for exactly 2017 / 2022-baseline / 2050-baseline (214–713 MB zips). Minor unverified detail: the 487,384-link count was not independently re-counted (metadata-level claim only). |
| 6 | HPMS 2023/2024 (ARNOLD) | **CONFIRMED** | ArcGIS item `5e6a977c...` resolves to "Highway Performance Monitoring System (HPMS) 2024", File Geodatabase, owner USDOT_BTS, "unrestricted public use", data as of 2024-12-31, modified 2025-12-23. Per-state geo.dot.gov REST pattern and 2023 BETA edition not re-verified this pass (UNCERTAIN sub-detail, non-blocking). |
| 7 | TIGER/Line 2025 | **CONFIRMED** | `www2.census.gov/geo/tiger/TIGER2025/` directory live with `PRIMARYROADS/`, `PRISECROADS/`, `ROADS/` (all 2025-09-22), open HTTPS bulk access, no auth. Census data is US Gov public domain. |
| 8 | Overpass API (public instance) | **CONFIRMED (one nuance)** | Wiki live (edited 2026-07-18); fair-use figures confirmed verbatim: <10,000 queries/day, <1 GB/day, identifying User-Agent/Referer required; software AGPLv3, data ODbL. Nuance: the wiki does **not explicitly permit** commercial use — it simply doesn't prohibit it. Researcher's "commercial use permitted" is a mild overstatement; treat as "not prohibited on the FOSSGIS instance, self-host if the platform becomes load-heavy." |

**Refutation attempts that failed (i.e., claims that held):** Geofabrik file size and daily cadence; Valhalla's full per-request truck parameter list (the strongest claim in the set — grep-verified in the repo docs, not just README marketing); NN 2020 staleness + disclaimer (researcher disclosed it honestly); NHS truck-AADT fields; FAF5/HPMS public-domain statements.

**Residual soft spots (none disqualifying):** (a) geodata.bts.gov / opendata.arcgis.com Hub pages are useless for automated fetch — all automation must target the ArcGIS REST / sharing-API endpoints; (b) Overpass commercial-use wording; (c) FAF5 link count and HPMS per-state REST pattern taken on metadata trust; (d) all federal geometry layers remain non-routable overlays, exactly as the researcher framed them.

**Overall:** 8/8 sources verified live, free, legally accessible, and accurately described. No fabricated sources, no license misrepresentation found.
