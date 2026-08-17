# Bridge Intelligence — Free & Legal Source Inventory
**Category:** Bridge clearance, weight, load rating, posting — US-wide Truck Intelligence Platform
**Researched:** 2026-07-22 · All URLs verified live via web search / direct fetch on this date unless marked UNCERTAIN.
**Constraint honored:** Zero paid APIs. Only official government data, open data portals, public ArcGIS REST services, and community open data.

---

## TL;DR — What to build on

| Rank | Source | What it gives | Access |
|------|--------|--------------|--------|
| 1 | **FHWA National Bridge Inventory (NBI)** annual files | Every public-road bridge in the US (~624k): clearance, load rating, posting status, coordinates | Free bulk ZIP (CSV/ASCII) |
| 2 | **BTS NTAD NBI hosted FeatureServer** | Same NBI data, already geocoded points, queryable ArcGIS REST + GeoJSON | Free, no key |
| 3 | **State DOT ArcGIS services** (WSDOT, TxDOT, OH, NY, PA, RI…) | Fresher, state-verified clearance + posted-weight data | Free ArcGIS REST |
| 4 | **WZDx Feed Registry** | Real-time work zones / lane & road closures (incl. bridge work) | Free feeds (some need free key) |
| 5 | **OSM `maxheight`** | Signed clearance values where mapped (patchy) | Free (ODbL) |

**Biggest honest gaps:** no national real-time bridge-closure feed, no national seasonal-posting dataset, no national *signed* weight/clearance-value dataset. Details in §8.

---

## 1. FHWA National Bridge Inventory (NBI) — THE foundation dataset

| Attribute | Detail |
|---|---|
| **Type** | OFFICIAL (US federal government) |
| **Owner** | Federal Highway Administration (FHWA), US DOT |
| **Official URL (2025 data)** | https://www.fhwa.dot.gov/bridge/nbi/ascii2025.cfm |
| **Landing page (all years)** | https://www.fhwa.dot.gov/bridge/nbi.cfm and https://www.fhwa.dot.gov/bridge/nbi/ascii.cfm |
| **Coverage** | All 50 states + DC + territories. 2025 file = **624,193 highway bridges** (note: Guam did not submit 2025 data) |
| **Update frequency** | **Annual.** States submit inspection data yearly (deadline in spring); FHWA publishes the consolidated year file (2025 file live as of this research; data.gov entry lists NBI "as of June 20, 2025") |
| **Format** | Plain ASCII text, two flavors per year: fixed-width ("no delimiter") and **comma-delimited with single-quote text qualifier**. ZIPs: per-state files (51 MB), single national file (51 MB), all-records incl. non-highway + routes-under (56 MB) |
| **Access method** | Bulk HTTP download (ZIP). No API, no auth, no rate limit concerns for a yearly grab |
| **Authentication** | None |
| **Cost** | $0 |
| **License** | US Government work — **public domain** (data.gov legacy entry: `us-pd`). No restrictions; attribution to FHWA is good practice |
| **Data quality** | High for structure/inventory attributes (federally mandated inspections, mostly 24-month cycle). Coordinates occasionally poor for older/local bridges (see limitations) |

### 1.1 The exact NBI items a truck platform needs
Verified against the official record format page: https://www.fhwa.dot.gov/bridge/nbi/format.cfm

| NBI Item | Name | Why trucks care |
|---|---|---|
| **Item 10** | Inventory Route, Min Vertical Clearance | Min clearance **on** the route carried by/under structure — core height-restriction input |
| **Item 39** | Navigation Vertical Clearance | Clearance over waterway (rarely truck-relevant) |
| **Item 53** | Min Vertical Clearance Over Bridge Roadway | Overhead restriction on the bridge deck itself |
| **Item 54** | Minimum Vertical Underclearance | Clearance **under** the bridge for the road below — the classic "low bridge" number |
| **Item 55** | Minimum Lateral Underclearance | Width pinch under structures |
| **Item 41** | Structure Open / Posted / Closed | Operational status code (open, posted for load, closed…) |
| **Item 63 / 64** | Method + **Operating Rating** | Max load level the bridge may carry (short-term) |
| **Item 65 / 66** | Method + **Inventory Rating** | Load level safe for indefinite service |
| **Item 70** | Bridge Posting | Coded relationship between posted capacity and legal loads |
| **Item 16 / 17** | Latitude / Longitude | Position (degrees-minutes-seconds packed format — must be parsed + converted) |

**Units warning (per Coding Guide):** clearances are recorded in **meters** and ratings in **metric tons** — convert before showing feet/US tons to drivers.

**Coding Guide** (defines every code value): "Recording and Coding Guide for the Structure Inventory and Appraisal of the Nation's Bridges", https://doi.org/10.21949/1519105

### 1.2 SNBI transition — plan for a format change
NBI is migrating from the legacy Coding Guide to the **Specifications for the National Bridge Inventory (SNBI)**: https://www.fhwa.dot.gov/bridge/snbi.cfm

- Timeline (verified via FHWA + state DOT docs): last Coding-Guide-format submittal **March 2025**; SNBI-based collection began Jan 2025; first complete SNBI submittal **March 2028**; new **National Bridge and Tunnel Inventory System (NBTIS)** arriving from Jan 2026.
- Dataset grows from ~120 to **154 items**; clearance moves to the `B.H.*` series (e.g., **B.H.12** vertical clearance per NDDOT/CDOT coding-guide supplements); posting data gets richer (exact SNBI posting item codes: **UNCERTAIN** — confirm in the SNBI publication PDF https://www.fhwa.dot.gov/bridge/snbi/snbi_march_2022_publication.pdf).
- Official old→new item crosswalk: https://www.fhwa.dot.gov/bridge/snbi/codemapping.cfm
- **Practical impact for the platform:** build the ingest with a thin mapping layer keyed on item names, not column positions, so the 2026-2028 file-format switch is a config change, not a rewrite.

### 1.3 Advantages / Limitations

**Advantages**
- The only *complete, national, authoritative* bridge dataset. Free, public domain, one-file simplicity — perfect for a solo dev (annual ZIP → parse → PostGIS/SQLite).
- Contains everything static a truck router needs: clearance, ratings, posting status, condition, detour length, location.

**Limitations (honest)**
- **Annual snapshot.** A bridge posted or closed in July won't appear until next year's file.
- **Item 70 posting is a CODE, not the sign value.** NBI does **not** contain the actual posted tonnage on the sign (e.g., "18 T single / 32 T combo"). No specific weight-limit field exists in the record format (verified on format.cfm).
- Measured clearance ≠ **signed** clearance (signs are usually posted a few inches below measured; resurfacing changes reality between inspections).
- Coordinate quality varies; a small % of bridges geocode badly (plan a snap-to-road sanity check).
- No seasonal restrictions, no real-time closures (see §8).

---

## 2. NBI as a ready-made geospatial service (BTS / NTAD)

| Attribute | Detail |
|---|---|
| **Type** | OFFICIAL (US DOT Bureau of Transportation Statistics) |
| **Portal page** | https://geodata.bts.gov/datasets/national-bridge-inventory/about (page is JS-rendered — didn't render for my fetch tool, but dataset confirmed via data.gov + ArcGIS item pages) |
| **ArcGIS REST (open, verified live 2026-07-22, no login)** | https://geo.dot.gov/server/rest/services/hosted/National_Bridge_Inventory/FeatureServer/0 |
| **ArcGIS REST (now LOGIN-WALLED — avoid)** | https://geo.dot.gov/mapping/rest/services/NTAD/National_Bridge_Inventory/MapServer — my fetch was 302-redirected to an ArcGIS OAuth login. Use the `hosted` endpoint or bulk files instead |
| **data.gov catalog entry** | https://catalog.data.gov/dataset/national-bridge-inventory1 |
| **Coverage** | National (620k+ points) |
| **Update frequency** | Annual (follows FHWA NBI release). **UNCERTAIN which vintage the hosted layer currently serves:** the layer description I fetched says "as of June 15, 2023" while the data.gov entry says "as of June 20, 2025" — check the layer's `editingInfo`/description at ingest time and fall back to §1 bulk files if stale |
| **Format / access** | ArcGIS REST query API — **JSON, GeoJSON, PBF**, point geometry, MaxRecordCount 2000 (paginate with `resultOffset`) |
| **Authentication** | None on the `hosted` endpoint |
| **Cost / License** | $0, US Government public domain |
| **Fields (verified sample)** | `min_vert_c`, `nav_vert_c`, `vert_clr_o` (clearances), `opr_rating`, `inv_rating` (load ratings), `posting_ev` (posting), `state_code`, `year_built`, `deck_cond_` |
| **Quality** | Same content as NBI; already parsed + geocoded — the cheapest path to a working map layer |

**Advantages:** zero parsing of fixed-width files; GeoJSON straight into PostGIS/tiles.
**Limitations:** 2000-records-per-page pagination for 620k points is slow (one-time cost); possible vintage lag vs. the FHWA ZIP; description metadata sparse.

**Also on data.gov:** NBI Element Data — https://catalog.data.gov/dataset/national-bridge-inventory-element-data1

---

## 3. FHWA NBI Element (NBE) data — optional depth

| Attribute | Detail |
|---|---|
| **Type** | OFFICIAL (FHWA) |
| **URL** | https://www.fhwa.dot.gov/bridge/nbi/element.cfm (2025: https://www.fhwa.dot.gov/bridge/nbi/element2025.cfm) |
| **What it is** | Element-level condition (deck, girders, joints, bearings…) for NHS bridges — quantities in condition states 1-4 |
| **Coverage / cadence** | National (NHS bridges), annual |
| **Format / auth / cost** | Bulk ASCII/XML ZIP download, none, $0, public domain |
| **Truck-platform value** | **Low for routing.** Useful only if you later add a "bridge health / risk" intelligence layer. Skip for v1 — simplicity rule |

---

## 4. LTBP InfoBridge — analysis portal, not a pipeline source

| Attribute | Detail |
|---|---|
| **Type** | OFFICIAL (FHWA Long-Term Bridge Performance Program) |
| **URL** | https://infobridge.fhwa.dot.gov/ (data UI: https://infobridge.fhwa.dot.gov/Data) |
| **What it offers** | Unified query/visualization over NBI + NBE + LTBP research data + climate + special projects; per-bridge dashboards; "Export Data" for selected bridges |
| **Coverage** | National; NBI back-years included |
| **Update frequency** | Follows NBI annual cycle (research datasets update on their own schedules) |
| **Access method** | Interactive web portal; Excel-oriented export with an "Allowed Export Limit" |
| **Authentication** | **Login/registration required for export** (verified: portal enforces sessions). Registration is free. |
| **API** | **None documented publicly** (verified: no API mentioned on the data pages) — UNCERTAIN whether any internal endpoints are permitted for automation, so treat as **not automatable** |
| **Cost / License** | $0; underlying federal data public domain; portal has its own Terms & Conditions page — respect it, don't scrape the UI |
| **Verdict for the platform** | Great for *manual research and QA* (e.g., checking one bridge's history). **Do not build a pipeline on it** — use §1/§2 for the same data in bulk |

---

## 5. State DOT bridge / clearance / posting GIS services (7 concrete examples)

State DOTs publish fresher and sometimes *signed-value* data that NBI lacks. All are OFFICIAL (state government). All ArcGIS REST (query → JSON/GeoJSON). No auth, $0. Verification status is per-endpoint, honest.

### 5.1 Washington — WSDOT ✅ VERIFIED LIVE (direct fetch 2026-07-22)
- **Bridge Vertical Clearance (trip-planner-grade):** https://data.wsdot.wa.gov/arcgis/rest/services/Bridge/BridgeVerticalClearance/MapServer — layers *Crossings*, *Bridges* + tables *Lanes, Advisories, Documents*. This is the production service behind WSDOT's Bridge Vertical Clearance Trip Planner — **per-lane clearances + advisories**, i.e., exactly what a truck router wants. Formats: JSON/GeoJSON/PBF. (Caveat from service doc: raise max-records to 4000 when querying.)
- **General bridge data:** https://data.wsdot.wa.gov/arcgis/rest/services/Shared/BridgeData/FeatureServer (also /MapServer) — state structures with `MinVertClrncOverDeck`, `MinVertClrncUnderBridge` fields.
- Update cadence: maintained operationally (WSDOT BPO); exact refresh interval UNCERTAIN.

### 5.2 Texas — TxDOT ✅ VERIFIED (search-indexed service + open-data page)
- **All bridges (NBI fields included):** https://services.arcgis.com/KTcxiTD9dsQw4r7Z/arcgis/rest/services/TxDOT_Bridges/FeatureServer — statewide points, on- and off-system, with all NBI data fields.
- **Vertical clearance measurements:** https://gis-txdot.opendata.arcgis.com/datasets/txdot-vertical-clearances — statewide vertical-clearance measurement points (TxDOT policy: grade-separation clearances re-verified at least annually). Open Data portal offers CSV/GeoJSON/Shapefile export.
- License: TxDOT Open Data portal terms (standard open reuse); attribution TxDOT.

### 5.3 Ohio — ODOT TIMS ✅ VERIFIED via search index (direct fetch failed: DNS `ESERVFAIL` from my sandbox — retry from your network)
- **Bridge Inventory:** https://tims.dot.state.oh.us/ags/rest/services/Assets/Bridge_Inventory/MapServer (layer 0). Point layer, JSON/GeoJSON/PBF, MaxRecordCount **200,000**, and per the dataset page the inventory is **updated daily** — the freshest state bridge feed found.
- Dataset page: https://tims.dot.state.oh.us/tims/data/dataset/474a6698368d4e62a8be9978abbee579
- Bonus federal-measures view: https://gis.dot.state.oh.us/arcgis/rest/services/TIMS/FHWA_TPM_Bridges/MapServer

### 5.4 New York — NYSDOT ✅ VERIFIED via search index + ArcGIS item page
- **Structures service:** https://gis.dot.ny.gov/hostingny/rest/services/NYSDOT_Structures/MapServer (ArcGIS item: https://www.arcgis.com/home/item.html?id=9e038774ef034c7cae5374f3e23f7a67 — "can be freely downloaded and used").
- **Commercial-vehicle layers (incl. restrictions):** https://gisportalny.dot.ny.gov/hostingny/rest/services/CommVehicleDataFeed/MapServer/layers — surfaced in search results; layer-by-layer content UNCERTAIN, inspect before use. NY parkway low bridges are the #1 truck-strike hotspot in the country, so NY-specific data matters.
- **Posted bridges (human-readable):** https://www.dot.ny.gov/postedbridges — authoritative posting list, but HTML/PDF, not an API.

### 5.5 Pennsylvania — PennDOT via PASDA ✅ VERIFIED via search index
- **Posted weight restrictions:** https://maps.pasda.psu.edu/server/rest/services/pasda/PennDOT/MapServer layer 20 ("PA RMS POSTED 2026_01" — road segments with posted weight restrictions; the layer-name datestamp implies periodic refresh, cadence UNCERTAIN). PASDA summary: https://www.pasda.psu.edu/uci/DataSummary.aspx?dataset=47
- This is one of the few free sources of **actual posted-restriction segments** (not just NBI codes). PA posts thousands of bridges — high truck value.
- License: PASDA open access with attribution.

### 5.6 Rhode Island — RIDOT ✅ VERIFIED LIVE (direct fetch 2026-07-22)
- **Bridge inventory:** https://risegis.ri.gov/hosting/rest/services/RIDOT/Bridge/MapServer — layers *Bridge*, *Bridge_Polys*; JSON/GeoJSON; MaxRecordCount 30,000.
- **Posted bridges w/ axle limits:** https://gisstage.dot.ri.gov/gpserver/rest/services/Bridges/PostedBridgesAxles/MapServer — NOTE: `gisstage` hostname suggests a **staging** server; find/confirm the production twin before depending on it (UNCERTAIN).

### 5.7 Indiana — INDOT ⚠️ UNCERTAIN
- **Bridge clearance layer:** https://gis.indot.in.gov/ro/rest/services/RAH_GIO_Collaboration/LRSE_Bridge_Clearance/FeatureServer — appears in search indexes, but my direct fetch returned **HTTP 403** (likely blocks non-browser user agents). Verify from a browser; do not assume automated access is permitted until the service metadata says so.

### 5.8 Also seen (leads, not fully verified)
- **Colorado CDOT** vertical clearances page: https://ft-cdot.opendata.arcgis.com/pages/vertical-clearances
- **Oregon ODOT** TransGIS catalog: https://gis.odot.state.or.us/arcgis1006/rest/services/transgis/catalog/MapServer

**Discovery pattern for the remaining ~43 states:** nearly every DOT runs an ArcGIS Open Data hub (`<agency>.opendata.arcgis.com` or a `gis.dot.<state>.us` REST directory). Search `site:opendata.arcgis.com <state> DOT bridge` or hit `/arcgis/rest/services` directories. Also ArcGIS Hub global search: https://hub.arcgis.com. Budget rule for a solo dev: NBI national baseline first, then add state services **only** for the top freight states + known low-bridge states (NY, PA, TX, OH, WA, IL, GA, CA).

---

## 6. Real-time & event data (what fills NBI's blind spot)

### 6.1 WZDx — Work Zone Data Exchange Feed Registry ✅ VERIFIED
| Attribute | Detail |
|---|---|
| **Type** | OFFICIAL (USDOT ITS JPO registry; feeds owned by state/local agencies) |
| **URL** | https://data.transportation.gov/Roadways-and-Bridges/Work-Zone-Data-Exchange-WZDx-Feed-Registry/69qe-yiui (catalog: https://catalog.data.gov/dataset/work-zone-data-exchange-wzdx-feed-registry) |
| **What** | Registry (CSV/Socrata API) of state/local **live work-zone feeds** in the standard WZDx GeoJSON spec — lane closures, road closures, construction events, including bridge-work closures |
| **Coverage** | Only agencies that publish WZDx (a few dozen; growing) — NOT all 50 states |
| **Cadence** | Feeds are near-real-time; registry metadata updated as feeds register |
| **Auth / cost** | Registry: none. Individual feeds: most open; **some require a free self-service API key** (per-feed) |
| **License** | Open (federal registry public domain; feeds typically open-licensed by agencies) |
| **Spec** | https://github.com/usdot-jpo-ode/wzdx |

### 6.2 State 511 traveler-information APIs
Every state runs a 511 system with closures/incidents; many offer free developer APIs or open GeoJSON/XML feeds (e.g., NY 511, Iowa 511, Nebraska 511). Coverage and licensing are **per-state patchwork** — evaluate individually. This is a "road closures" category concern; for *bridges* specifically, 511 is where an emergency bridge closure appears months before NBI.

### 6.3 Seasonal / spring load restrictions ⚠️ mostly NOT machine-readable
Verified examples:
- **MnDOT Seasonal Load Limits maps:** https://www.dot.state.mn.us/loadlimits/maps.html (frost-zone maps, 5/7-ton routes, dates announced ≥3 days ahead)
- **SDDOT spring load restrictions:** press releases, e.g. https://dot.sd.gov/travelers/travelers/spring-load-restrictions/

Reality: spring-thaw postings (Feb-Apr, northern states) are published as **web pages, PDFs, and press releases** — there is **no national machine-readable feed**. See gaps §8.

---

## 7. Community data — OpenStreetMap

| Attribute | Detail |
|---|---|
| **Type** | COMMUNITY |
| **What** | `maxheight`, `maxweight`, `hgv` tags on ways under bridges/tunnels — the **signed** values, which NBI doesn't carry |
| **Docs** | https://wiki.openstreetmap.org/wiki/Key:maxheight |
| **Access** | Overpass API (free, rate-limited, be polite), Geofabrik extracts (bulk PBF), OSRM/Valhalla consume tags natively |
| **Coverage quality (honest)** | **Patchy in the US.** Per OSM's own wiki/community: absence of `maxheight` can mean "no restriction" OR "nobody mapped it" — you cannot distinguish. QA tooling exists (https://github.com/lbarrosop/osm-maxheight-map). Corporate mapping campaigns (e.g., OptimoRoute organized edits) are improving truck tags |
| **License** | **ODbL** — share-alike applies if you create a derivative database mixing OSM into your bridge DB. Keep OSM-derived columns separable, or use OSM only inside the router (Valhalla/OSRM), to keep licensing simple |
| **Cost** | $0 |
| **Verdict** | Use as the router's restriction layer (Valhalla reads `maxheight` out of the box) + cross-check against NBI-derived low-clearance points. Never as sole source of truth |

---

## 8. HONEST GAPS — no comparable free + legal source exists

1. **Real-time bridge closures, nationwide.** No single free national feed. Best free approximation = WZDx (partial coverage) + per-state 511 APIs (50 integrations). Paid alternatives that own this space: HERE, INRIX, TomTom incident feeds.
2. **Seasonal / spring-thaw load postings as data.** Published as PDFs/press releases per state. No national dataset, free or paid, in machine-readable form — even commercial truck routers handle this imperfectly. Closing it means scraping/manual curation per northern state each spring (legally fine — public info — but labor).
3. **Actual posted SIGN values (weight in tons per axle config, signed height in ft-in) nationwide.** NBI Item 70 is a relational code, not the sign. A handful of states publish real values (PennDOT posted segments, RIDOT posted axles, WSDOT per-lane clearances); the *national* signed-restriction database is proprietary — this is exactly what **Trimble/PC*Miler, ProMiles, HERE Truck Attributes** sell. Free path = NBI proxy (operating rating + posting code) + state services + OSM, clearly labeled with confidence levels.
4. **NBI latency.** Annual file = up to ~12-month staleness on posting changes. No free fix until FHWA's NBTIS (from Jan 2026) potentially enables fresher reporting — watch it, cadence benefit UNCERTAIN.
5. **Signed-vs-measured clearance mismatch.** NBI reports measured minimums; the legally binding sign may differ. No free national signed-clearance dataset exists (see #3).
6. **LTBP InfoBridge automation.** Login-gated export, no public API — fine for manual lookups, not for pipelines.
7. **Small-endpoint uncertainty.** INDOT clearance service (403 to scripts) and RIDOT posted-axles (staging host) need manual confirmation before relying on them.

---

## 9. Recommended architecture for a solo dev (boring-tech)

1. **Once a year:** download NBI delimited ZIP (§1) → small Python script → normalize units (m→ft, metric tons→US tons) → load into PostGIS (or even SQLite+SpatiaLite). ~625k rows is trivially small.
2. **Derive truck layers:** `low_clearance_points` (Item 10/54 < 14'0"), `posted_bridges` (Item 41 in posted/closed codes, Item 70), `weak_bridges` (operating rating below rig weight).
3. **Overlay freshness:** poll WZDx feeds (§6.1) hourly for work-zone closures; add top-freight-state DOT ArcGIS services (§5) on a weekly cron (plain `requests` + `f=geojson` pagination — no SDK needed).
4. **Router integration:** run Valhalla on OSM (gets `maxheight`/`maxweight` for free), and inject NBI-derived restrictions as custom avoid-polygons/edges where OSM is silent.
5. **Label confidence:** every restriction shown carries a source + vintage badge (NBI-2025 / State-DOT-live / OSM-community) — honest data beats pretend-complete data.

---

## Verification log (2026-07-22)

| Check | Method | Result |
|---|---|---|
| NBI 2025 ASCII page + file list + delimiter spec | Direct fetch | ✅ Live, 624,193 bridges |
| NBI record format items (10, 39, 53, 54, 41, 63-66, 70, 16, 17) | Direct fetch of format.cfm | ✅ Confirmed |
| SNBI transition timeline | FHWA snbi.cfm + state DOT docs via search | ✅ Confirmed |
| BTS hosted NBI FeatureServer open access + fields | Direct fetch | ✅ Live, no login (vintage string says 2023 — flag) |
| geo.dot.gov/mapping NTAD MapServer | Direct fetch | ⚠️ Redirects to OAuth login — do not use |
| InfoBridge export/login behavior | Direct fetch | ✅ Login-gated export, no public API |
| WSDOT BridgeVerticalClearance MapServer | Direct fetch | ✅ Live |
| RIDOT Bridge MapServer | Direct fetch | ✅ Live |
| Ohio TIMS Bridge_Inventory | Search-indexed metadata; direct fetch DNS-failed from sandbox | ⚠️ Retry from prod network |
| INDOT LRSE_Bridge_Clearance | Direct fetch | ⚠️ 403 to non-browser agent |
| TxDOT, NYSDOT, PennDOT/PASDA endpoints | Search-indexed service directories | ✅ Exist (spot-check at ingest) |
| WZDx registry | Search + catalog entries | ✅ Confirmed |
| OSM maxheight coverage assessment | OSM wiki + community sources | ✅ Patchy-coverage caveat confirmed |

---

## Verification (adversarial pass)

**Verifier:** independent adversarial check, 2026-07-22. Method: direct WebFetch of every claimed URL (or its Socrata/catalog metadata endpoint when the page is JS-rendered), plus search-index corroboration where DNS failed from the sandbox. Default posture: try to refute; UNCERTAIN when unconfirmable.

| # | Source | Verdict | Evidence |
|---|--------|---------|----------|
| 1 | FHWA NBI 2025 bulk files | **CONFIRMED** | Page live (last updated 06/20/2025); 624,193 bridges; both delimited + fixed-width ZIPs (~51-56 MB); no auth/license restrictions stated — consistent with US-gov public domain. |
| 2 | BTS hosted NBI FeatureServer | **CONFIRMED (with vintage caveat)** | Fetched without login; Feature Layer, point geometry, MaxRecordCount 2000; fields `min_vert_c`, `nav_vert_c`, `opr_rating`, `inv_rating`, `posting_ev` all present. Layer description says data "as of June 15, 2023" (~615k bridges) — the researcher's own vintage warning is REAL, not hypothetical. Check vintage at ingest; prefer #1 ZIP if stale. |
| 3 | WSDOT BridgeVerticalClearance MapServer | **CONFIRMED** | Live; self-describes as "Production BVCTP Service"; layers Crossings(0)/Bridges(1) + tables Lanes(2)/Documents(3)/Advisories(4); no auth needed; doc itself warns to raise max-records to 4000. |
| 4 | TxDOT Bridges FeatureServer | **CONFIRMED** | Live; security level "Public"; one Bridges layer with NBI fields; description says **nightly updates** (better than claimed). The separate vertical-clearances open-data page exists (title renders) but is JS-walled to my fetcher — export formats/license not independently re-verified, spot-check at ingest. |
| 5 | Ohio DOT TIMS Bridge_Inventory | **UNCERTAIN** | DNS resolution failed from sandbox for BOTH tims.dot.state.oh.us and gis.dot.state.oh.us (ESERVFAIL/ETIMEOUT). Search index corroborates the endpoint exists (point Feature Layer, display field SFN, all-Ohio bridges). Could NOT verify "daily refresh", MaxRecordCount 200,000, or open automated access. Retry from prod network before depending on it. |
| 6 | PennDOT posted restrictions via PASDA | **CONFIRMED (layer name drifts)** | Live, 35-layer MapServer, query/export supported without credentials. Layer 20 is now "**PA RMS POSTED 2026_07**" (was 2026_01 in the claim) — refutes the exact layer NAME but confirms the better fact: the layer is refreshed periodically. Ingest must match layer by name-prefix `PA RMS POSTED`, not hardcoded ID/name. |
| 7 | WZDx Feed Registry | **CONFIRMED** | Socrata metadata JSON valid: "Work Zone Data Feed Registry", license = Public Domain U.S. Government, columns include `url`, `format`, `active`, `needAPIKey`, `apiKeyURL` — matching the "some feeds need a free key" claim. data.gov entry live (last checked 2026-07-07), CSV/JSON/GeoJSON exports. Coverage is per-registered-agency, i.e., partial — as claimed. |
| 8 | OSM maxheight (Overpass/Geofabrik) | **CONFIRMED** | Wiki page live; documents `maxheight` as the legal signed limit (+ `maxheight:physical`); references the Maxheight Map QA tool for finding UNMAPPED restrictions — which itself corroborates the patchy-US-coverage caveat. OSM data license is ODbL (wiki text is CC-BY-SA — different thing; the data claim is correct). Overpass is rate-limited community infra: bulk work must use Geofabrik extracts, as claimed. |

**Adversarial findings that stuck:**
1. **#2 vintage is genuinely stale-labeled (2023)** — not just a "maybe". If the hosted layer hasn't been refreshed, the FHWA ZIP is 2 years fresher. Treat #2 as convenience layer only.
2. **#6 layer name already changed** (2026_01 → 2026_07) — hardcoding it would have broken the pipeline within 6 months. Match by prefix.
3. **#5 unprovable from here** — Ohio state DNS appears to block/fail for some resolvers; the "freshest state feed (daily)" selling point rests entirely on a dataset-page claim nobody in this chain has re-fetched. Downgrade to lead until prod-network verified.
4. No claim was found to be fabricated, paywalled, or auth-bypassing. All 7 verifiable sources are genuinely free + legally accessible for automation (US-gov public domain / state open data / ODbL).

**Overall:** 7 of 8 CONFIRMED, 1 UNCERTAIN (Ohio, network-environment issue not a source defect). The source list is honest and production-usable as ranked.
