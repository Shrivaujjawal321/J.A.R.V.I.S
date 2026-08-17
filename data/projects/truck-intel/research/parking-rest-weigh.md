# Truck Parking, Rest Areas & Weigh Stations — Legal Free-Source Inventory

**Category:** Truck parking · Rest areas · Weigh stations (US-wide Truck Intelligence Platform)
**Researched:** 2026-07-22 · All URLs below were checked live on this date via web search, page fetch, or direct HTTP query unless marked **UNCERTAIN**.
**Hard rule honored:** No paid APIs, no scraping behind auth/CAPTCHA, no ToS violations. Every source is government (OFFICIAL), openly licensed (OPEN), or community (COMMUNITY, e.g. OSM).

---

## 0. Executive Summary (read this first)

| What you need | Best free source | Real-time? | Verified today? |
|---|---|---|---|
| National truck-parking location baseline | BTS NTAD "Truck Stop Parking" layer (1,915 points) | No (static, 2019 compile) | YES — live query returned count=1915 |
| Real-time parking availability (Midwest) | MAASTO TPIMS state feeds (JSON, 1–5 min updates) | YES | Spec verified; live URLs now gated (see §2) |
| Real-time parking availability (NY) | 511NY Developer API — truck parking endpoint | YES | YES — API doc fetched, free key, 10 calls/60s |
| Real-time parking availability (FL) | FDOT TPAS via FL511 third-party data feed | YES | System verified; feed access via registration |
| Rest-area locations (state-accurate) | State DOT ArcGIS/open-data layers (CA, TX, IA, MN, WA, IN, + 511 APIs for GA/LA/NV) | No | CA verified live; others verified to exist |
| Weigh-station locations | Caltrans CVEF (53 pts, verified), IDOT Weigh Stations, GA 511 "Ports of Entry", OSM `amenity=weighbridge` | No | CA count=53 verified live |
| Historical parking-occupancy data (research/ML) | WisTransPortal TPIMS Archive (2019–present, 1-min data, 150 sites) | Archive | Page fetched; access by free account + email request |

**The honest headline:** location/static data is richly covered by free official sources. **Real-time availability is only free where a state built a public system** (8 MAASTO states, FL, NY, and a few others). There is **no free national real-time truck-parking feed** and **no maintained official national weigh-station dataset** since HIFLD Open shut down in Aug 2025. Details in §7 (Gaps).

---

## 1. National Baseline — Truck Parking Locations (static)

### 1.1 BTS/FHWA NTAD "Truck Stop Parking" — ★ TOP PICK

| Field | Value |
|---|---|
| Owner | US DOT Bureau of Transportation Statistics (BTS), data compiled by FHWA |
| Label | **OFFICIAL** |
| Landing page | https://geodata.bts.gov/datasets/usdot::truck-stop-parking/about |
| ArcGIS REST endpoint (verified live 2026-07-22) | `https://services.arcgis.com/xOi1kZaI0eWDREZv/arcgis/rest/services/NTAD_Truck_Stop_Parking/FeatureServer` |
| Also on | data.gov: https://catalog.data.gov/dataset/truck-stop-parking1 |
| Coverage | US-wide: **1,915 point features** (verified via `returnCountOnly` query — note: press articles claim "8,000+ locations"; the actual public layer has 1,915) |
| Geometry | Point |
| Update frequency | Effectively static. Compiled April 2019 (Jason's Law survey era); ArcGIS item last modified June 2024 (metadata refresh, not a data refresh) |
| Data quality | Good for interstate-corridor coverage of public rest areas + major private truck stops; attributes came from state DOTs + the commercial "Trucker's Friend" directory. **Stale**: closures/new facilities since 2019 not reflected |
| License | **Public domain** (US Government work, "unrestricted public use") |
| Access method | ArcGIS REST (query, GeoJSON out), plus Shapefile/CSV/KML/GeoJSON downloads from the geodata.bts.gov page |
| Auth | None |
| Cost | Free |
| Advantages | Only national truck-parking layer; public domain; trivially easy (one FeatureServer query); includes capacity attributes where states reported them |
| Limitations | 2019 vintage; count far below true national facility count; no availability data |

**Simple pull:** `GET {endpoint}/0/query?where=1=1&outFields=*&f=geojson` (page through with `resultOffset`; maxRecordCount applies).

### 1.2 NTAD Truck Stop Parking — archival versions (ROSAP)

| Field | Value |
|---|---|
| Owner | BTS National Transportation Library |
| Label | **OFFICIAL** |
| URL | https://rosap.ntl.bts.gov/view/dot/88314 ("Truck Stop Parking 2017–Present") |
| Coverage / freq | Versioned snapshots of 1.1; updated when BTS republishes |
| License | Public domain |
| Access | Bulk download (zip/shapefile + data-management-plan docs) |
| Use | Provenance + reproducibility; not needed at runtime |

### 1.3 Jason's Law Truck Parking Survey (FHWA)

| Field | Value |
|---|---|
| Owner | FHWA Office of Freight Management |
| Label | **OFFICIAL** |
| URLs | Results & analysis: https://ops.fhwa.dot.gov/freight/infrastructure/truck_parking/jasons_law/truckparkingsurvey/jasons_law.pdf and https://ops.fhwa.dot.gov/freight/infrastructure/truck_parking/jasons_law/truckparkingsurvey/es.htm |
| What it is | Survey **reports** (2015 and 2020 editions) on parking adequacy per state — shortage metrics, utilization, state-by-state statistics. The geospatial output of the survey IS the NTAD layer (1.1) |
| Third survey status | FHWA launched the third Jason's Law survey (responses collected through Feb 2026 per trade press). **Results not yet published as of 2026-07-22** — expect a refreshed dataset; watch ops.fhwa.dot.gov |
| License | Public domain |
| Access | PDF/HTML reports (analysis tables, not an API) |
| Use | Demand/shortage context for corridor scoring — not a location feed |

---

## 2. Real-Time Truck Parking Availability (TPIMS + state systems)

### 2.1 MAASTO TPIMS — the 8-state Midwest system — ★ TOP PICK (with caveats)

**States:** Iowa, Kansas, Kentucky, Michigan, Minnesota, Ohio, Wisconsin, Indiana. ~150 instrumented sites (public rest areas + participating private truck stops) on I-80, I-35, I-70, I-94, I-65/71/75 corridors.

| Field | Value |
|---|---|
| Owner | MAASTO member state DOTs; archive operated by U. Wisconsin TOPS Lab (WisTransPortal) |
| Label | **OFFICIAL** (state DOT data; university-hosted archive) |
| Spec (verified — full PDF parsed 2026-07-22) | https://transportal.cee.wisc.edu/tpims/TPIMS_TruckParking_Data_Interface_V2.2.pdf (also mirrored at https://trucksparkhere.com/wp-content/uploads/2019/01/TPIMS_TruckParking_Data_Interface_App_Developers_V1.1.pdf) |
| Feed model (from spec) | 3 JSON feeds per state: **Dynamic public** (`GET /api/TPIMS_Dynamic.json`, 8 fields, updated every 1–5 min: siteId, reportedAvailable, trend FILLING/CLEARING, open, trustData, capacity), **Static public** (`GET /api/TPIMS_Static.json`, 19 fields: lat/lon, highway, mile post, direction, amenities, ownership, images), **Archive** (trusted partners only) |
| Auth model (from spec) | Each state MAY keep dynamic+static public feeds **open** or put them behind a free API token; archive feeds always restricted |
| Update frequency | Dynamic: 1–5 min. Static: as-needed |
| License | State government data; spec explicitly designed for third-party redistribution. Per-state terms apply — confirm at registration |
| Cost | Free |
| Quality | Sensor-based (in-pavement + ramp counters); `trustData` flag tells you when to distrust a site's count — honor it |

**Reality check (tested 2026-07-22):** the spec's example live URLs `https://transportal.cee.wisc.edu/TPIMS/dynamic` and `/static` now return **HTTP 404**. The WisTransPortal TPIMS hub (https://transportal.cee.wisc.edu/tpims/ — fetched, live) says feeds + archive access are granted via a **free WisTransPortal account + email to tpims@topslab.wisc.edu**. So: the system is alive, but feed URLs are obtained through registration, not anonymous.

**Per-state access points (all verified to exist unless noted):**

| State | Access point | Status 2026-07-22 |
|---|---|---|
| Kansas | KDOT TPIMS developer registration: https://tpims.ksdot.gov/tpims/ (register → JSON feed for I-70/I-135 sites; interface doc at https://tpims.ksdot.gov/docs/TPIMS_TruckParking_Data_Interface_App_Developers.pdf) | Indexed + linked from KDOT; direct fetch **timed out from my test location** — likely US-geofenced. **UNCERTAIN** whether registration is instant or reviewed |
| Kentucky | KYTC TPIMS page: https://drive.ky.gov/Motor-Carriers/Pages/TPIMS.aspx (fetched, live). Public map: http://www.trimarc.org/site/pages/TruckParking.html. 14 lots on I-65/71/75 | Page confirms a web data feed exists but **publishes no API docs** — programmatic access requires contacting KYTC |
| Iowa | "Iowa Trucks Park Here" — 41 facilities on I-80/I-29/I-35/I-235/I-380. Feed consumed by Iowa 511 and third parties | Feed exists (FHWA + vendor docs confirm); public endpoint URL **UNCERTAIN** — request via Iowa DOT / check Iowa 511 developer resources |
| Wisconsin | Via WisTransPortal (above) + 511WI developer API: https://511wi.gov/developers/help | 511WI dev page exists; whether truck parking is an exposed 511WI resource **UNCERTAIN** |
| Michigan | Mi Drive map shows truck parking (https://mdotjboss.state.mi.us/MiDrive/map); MDOT ITS data page: https://www.michigan.gov/mdot/travel/safety/efforts/its/its-data | ITS-data page returned 403 to my fetcher (bot protection) — details **UNCERTAIN**; contact MDOT for feed |
| Minnesota | MnDOT TPIMS project page: https://www.dot.state.mn.us/its/projects/2016-2020/truckparking.html | Feed access path **UNCERTAIN** — not publicly documented; contact MnDOT |
| Ohio / Indiana | Participate in TPIMS; no public developer page found | **UNCERTAIN** — contact ODOT / INDOT |

### 2.2 WisTransPortal TPIMS Data Archive (historical occupancy) — ★ TOP PICK for ML

| Field | Value |
|---|---|
| Owner | UW–Madison TOPS Lab, on behalf of MAASTO partnership |
| Label | **OFFICIAL/OPEN** (university research portal) |
| URL (fetched, live) | https://transportal.cee.wisc.edu/tpims/ |
| Coverage | 2019–present, ~150 sites, 8 states, up to 21 variables at 1-minute refresh |
| Access | Free WisTransPortal account + request to tpims@topslab.wisc.edu; web query/download UI |
| Cost | Free |
| Advantages | The only long-horizon truck-parking occupancy time series in the US — ideal for training availability-prediction models (it powered published GNN papers) |
| Limitations | Human-in-the-loop access grant; Midwest only |

### 2.3 Florida — TPAS via FL511 data feed

| Field | Value |
|---|---|
| Owner | FDOT |
| Label | **OFFICIAL** |
| URLs | System overview: https://news.fl511.com/fl511-truck-parking-availability-system/ · FL511: https://fl511.com/about · Architecture: https://teo.fdot.gov/architecture/architectures/statewide/html/projects/projarch2.html |
| Coverage | 74 public facilities (rest areas, welcome centers, weigh stations) across the entire FL interstate system |
| Update frequency | Real-time (in-ground + microwave detection), aggregated by SunGuide/DIVAS |
| License / cost | State data, free; third-party feed explicitly offered |
| Access | FL511 **third-party data feed** — requires registration/data-use agreement with FDOT (no anonymous endpoint). Exact onboarding page not published; start at fl511.com/about → data feed contact |
| Limitation | FL only; onboarding friction **UNCERTAIN** (FDOT is re-procuring 511/DIVAS in 2026 — feed mechanics may change) |

### 2.4 511NY Developer API — truck parking endpoint — ★ TOP PICK (verified end-to-end)

| Field | Value |
|---|---|
| Owner | New York State DOT (511NY) |
| Label | **OFFICIAL** |
| URL (fetched, live 2026-07-22) | https://511ny.org/developers/doc (endpoint family incl. `/help/endpoint/truckparking`; also WZDx at https://511ny.org/api/wzdx) |
| Coverage | New York State truck parking sites (incl. I-90 corridor TPAS) |
| Update frequency | Real-time |
| License | Free with registered account + Developer API key; Developer Access Agreement applies; some layers flagged FOUO — respect flags |
| Access | REST + API key (`?key=`), JSON |
| Rate limit | **10 calls / 60 seconds** (documented) — poll one aggregate call per minute, cache server-side |
| Advantages | Fully self-service, documented, free; same Castle Rock platform as many other states (one client works for several states) |
| Limitations | NY only; throttled |

### 2.5 Other state 511 APIs on the same platform (rest areas / truck data)

These states run the same 511 software family with free self-service developer keys. Verified to exist via their live doc pages; the exact resource list varies per state:

| State | Dev docs URL | Relevant resources (per doc index) |
|---|---|---|
| Georgia | https://511ga.org/developers/doc | Rest Areas, **Ports of Entry** (weigh/inspection), cameras, events |
| Louisiana | https://www.511la.org/developers/doc | Rest Areas, events, signs |
| Wisconsin | https://511wi.gov/developers/help | TPIMS state — truck parking exposure UNCERTAIN |
| Idaho | https://511.idaho.gov/developers/doc | Events, cameras, (rest areas UNCERTAIN) |
| Nevada | https://www.nvroads.com/developers/doc | Events, cameras, (rest areas UNCERTAIN) |
| Arizona | https://www.az511.com/developers/doc | Events, cameras, (rest areas UNCERTAIN) |

**Pattern:** register account → request free key → REST JSON, ~10 calls/min throttle. This is the platform's **only legal automated path** — do not scrape the public map pages.

---

## 3. Rest Areas — State GIS Layers (the accurate, maintained source)

State DOTs are the system of record for public rest areas. Seven concrete endpoints (requirement was ≥5):

### 3.1 California — Caltrans "Safety Roadside Rest Areas" (verified live, queried today)

- **Owner:** Caltrans · **OFFICIAL**
- **Endpoint:** `https://caltrans-gis.dot.ca.gov/arcgis/rest/services/CHhighway/Rest_Areas/FeatureServer` (layer 0, point, Query+Extract capabilities, GeoJSON/CSV/shapefile export, maxRecordCount 2000)
- **Updated:** data last updated 2023-08-15 (per service description)
- **License:** Public record, free; no auth
- **Quality:** authoritative statewide inventory from Caltrans Maintenance/ROW

### 3.2 Texas — TxDOT Safety Rest Areas

- **Owner:** TxDOT · **OFFICIAL**
- **URL:** https://gis-txdot.opendata.arcgis.com/datasets/txdot-safety-rest-areas (portal: https://gis-txdot.opendata.arcgis.com/ ; org REST root: https://services.arcgis.com/KTcxiTD9dsQw4r7Z/ArcGIS/rest/services)
- **Access:** ArcGIS Hub — GeoJSON/CSV/shapefile download + underlying FeatureServer
- **License:** TxDOT open data, free, no auth

### 3.3 Iowa — Iowa DOT Rest Areas

- **Owner:** Iowa DOT · **OFFICIAL**
- **URL:** https://public-iowadot.opendata.arcgis.com/datasets/IowaDOT::rest-areas (portal: https://public-iowadot.opendata.arcgis.com/)
- **Access:** ArcGIS Hub + FeatureServer; GeoJSON/CSV
- **License:** Iowa DOT open data, free, no auth

### 3.4 Minnesota — Rest Areas & MnDOT Facilities

- **Owner:** MnDOT via Minnesota Geospatial Commons · **OFFICIAL**
- **URL:** https://gisdata.mn.gov/en_US/dataset/struc-mndot-facilities
- **Access:** Shapefile/GeoJSON download + ESRI Feature Service links on the page
- **Update frequency:** published **weekly** to GeoCommons
- **License:** MN Geospatial Commons open license, free

### 3.5 Washington — WSDOT Facilities Sites: Active Rest Area

- **Owner:** WSDOT · **OFFICIAL**
- **URL:** https://geo.wa.gov/datasets/WSDOT::wsdot-facilities-sites-active-rest-area/about (portal: https://gisdata-wsdot.opendata.arcgis.com/ ; REST root: https://data.wsdot.wa.gov/arcgis/rest/services)
- **Access:** ArcGIS Hub + FeatureServer, GeoJSON/CSV
- **License:** WSDOT open data, free, no auth

### 3.6 Indiana — INDOT Rest Areas

- **Owner:** INDOT · **OFFICIAL**
- **URLs:** https://gisdata.in.gov/server/rest/services/Hosted/INDOT_Rest_Areas/FeatureServer/layers and https://gis.indot.in.gov/ro/rest/services/DOT/INDOT_Rest_Areas/FeatureServer
- **Caveat (tested):** direct curl from a non-US datacenter IP hit a **Cloudflare block**. The service is public (indexed, browser-accessible) but automated pulls should run politely (US egress, low frequency, real User-Agent) and respect the block if it persists — **do not evade**
- **License:** Indiana open data, free

### 3.7 Ohio — ODOT TIMS

- **Owner:** Ohio DOT · **OFFICIAL**
- **URL:** https://tims.dot.state.oh.us/tims (GIS portal with layer search + full-dataset export; contact TIMS@dot.ohio.gov)
- **Caveat:** my query of `gis.dot.state.oh.us/arcgis/rest/services` returned empty — a specific rest-area REST layer is **UNCERTAIN**; use the TIMS portal export path
- **License:** Ohio open data, free

**Plus:** GA + LA rest areas via their 511 APIs (§2.5). Most other states have equivalent layers — find them state-by-state via the FHWA-maintained directory of **State DOT GIS sites**: https://hepgis-usdot.hub.arcgis.com/pages/state-dot-gis-websites (OFFICIAL, verified to exist).

---

## 4. Weigh Stations

**Blunt truth:** there is **no maintained official national weigh-station dataset** available to the public in 2026 (see §4.4). Coverage = state layers + 511 APIs + OSM.

### 4.1 California — Commercial Vehicle Enforcement Facilities (verified live, queried today)

- **Owner:** Caltrans · **OFFICIAL**
- **Endpoint:** `https://caltrans-gis.dot.ca.gov/arcgis/rest/services/CHhighway/Vehicle_Enforcement_Facilities/FeatureServer/0` — **53 point features** (verified via count query 2026-07-22); also at https://gisdata.dot.ca.gov/arcgis/rest/services/CHhighway/Vehicle_Enforcement_Facilities/FeatureServer/0
- **License:** free, no auth · **Quality:** authoritative CHP weigh-station inventory

### 4.2 Illinois — IDOT Weigh Stations

- **Owner:** Illinois DOT · **OFFICIAL**
- **URL:** https://gis-idot.opendata.arcgis.com/datasets/IDOT::idot-weigh-stations/about (map: https://gis-idot.opendata.arcgis.com/maps/idot-weigh-stations)
- **Access:** ArcGIS Hub + FeatureServer, GeoJSON/CSV download · free, no auth

### 4.3 Georgia — "Ports of Entry" via 511GA API

- https://511ga.org/developers/doc — Ports of Entry resource (weigh/inspection stations), free API key (§2.5 pattern)

### 4.4 HIFLD national layer — GONE (do not build on mirrors)

- DHS **HIFLD Open was discontinued 2025-08-26**; portal offline since Sept 2025 (https://www.napsgfoundation.org/hifld_open/). Its national Weigh Stations / Truck Stops layers moved to **HIFLD Secure** (government users only — not legally accessible to this project).
- Snapshots exist (e.g. community archive at https://source.coop/seerai/hifld ; a NASA server still mirrors `hifld_open/transportation_ground` at maps.nccs.nasa.gov). These are **stale snapshots with UNCERTAIN maintenance and licensing posture** — usable at most as a one-time historical cross-check, never as a live dependency.

### 4.5 OSM (COMMUNITY) — the only *national* option

- Tag: `amenity=weighbridge` — **12,163 uses globally** (verified via taginfo API 2026-07-22; US subset smaller). Wiki: https://wiki.openstreetmap.org/wiki/Tag:amenity=weighbridge. Messy variants exist (`amenity=weigh_station`, `highway=weigh_station`) — query all variants.
- Coverage/quality: incomplete and uneven; many US interstate weigh stations ARE mapped (often as `highway=services` + name "Weigh Station").
- Access: Overpass API / Geofabrik extracts (§5). License: **ODbL** (attribution + share-alike on derived databases).

### 4.6 Real-time weigh-station status (open/closed, bypass)

- **No free source.** This is Drivewyze / PrePass commercial territory. Some 511 map pages display status for their own state but offer no documented feed. Honest gap — see §7.

---

## 5. Community Layer — OpenStreetMap (fills every geographic hole)

| Field | Value |
|---|---|
| Owner | OpenStreetMap contributors · **COMMUNITY** |
| Tags | `highway=rest_area` — **42,264 uses globally** (taginfo, verified 2026-07-22) · `highway=services` (service plazas/truck stops) · `amenity=weighbridge` (12,163) · truck-relevant modifiers: `hgv=*`, `access`, `capacity:hgv`, plus `amenity=fuel` + `hgv=yes` for truck fuel stops |
| Wiki (verified) | https://wiki.openstreetmap.org/wiki/Tag:amenity=weighbridge · https://wiki.openstreetmap.org/wiki/Tag:highway=services |
| Access methods | **Overpass API** (https://overpass-api.de — free, fair-use: keep queries modest, identify your app) · **Geofabrik US extracts** (https://download.geofabrik.de/north-america.html — bulk .pbf, unlimited local processing, refreshed daily) · taginfo for stats |
| Update frequency | Continuous (minutely diffs available) |
| License | **ODbL 1.0** — must attribute "© OpenStreetMap contributors"; share-alike applies to derived *databases* (plan your data model so OSM-derived tables are separable) |
| Cost | Free |
| Advantages | Only source covering ALL states uniformly incl. private truck stops (Pilot/Love's/TA locations are well mapped); richest amenity detail; bulk-download friendly (no rate limits if you process Geofabrik extracts locally) |
| Limitations | Volunteer quality — capacity counts mostly missing; weigh-station tagging inconsistent; needs conflation with official layers; ODbL share-alike discipline |

**Recommended pattern for a solo dev:** nightly Geofabrik US extract → `osmium tags-filter` for the 4 tag families → load to Postgres/PostGIS → conflate with NTAD + state layers by proximity. Boring, legal, zero API-limit stress.

---

## 6. Simple Acquisition Architecture (solo-dev friendly)

1. **Static backbone (weekly cron):** NTAD Truck Stop Parking (one GeoJSON query) + 6 state rest-area FeatureServer pulls + CA/IL weigh stations + Geofabrik OSM extract. All anonymous, bulk, boring.
2. **Real-time tier (per-state adapters, only where free feeds exist):** 511NY key (1 call/min) → normalize; KDOT TPIMS JSON after registration; WisTransPortal/MAASTO feeds after email grant; FL511 feed after FDOT agreement. One normalizer to the TPIMS static/dynamic schema (it's already the de-facto standard — reuse its field names).
3. **History/ML:** request WisTransPortal TPIMS archive once; train availability predictor offline.
4. **Compliance:** attribution page listing BTS, state DOTs, OSM (ODbL); honor 511 rate limits; keep OSM-derived tables separable for share-alike.

---

## 7. HONEST GAPS — no free/legal source exists

1. **National real-time truck-parking availability.** Free real-time coverage = 8 MAASTO states + FL + NY (+ scattered others). The other ~40 states have no public feed. National real-time coverage (esp. private truck stops) is commercial only: Trucker Path, Drivewyze Free Parking?, TA/Pilot/Love's app telemetry, Park My Truck (NATSO app — no public API). **Paid gap.**
2. **Private truck-stop amenity/parking database (current).** NTAD's private-facility data is a 2019 snapshot from the commercial "Trucker's Friend" directory. A *current* national private truck-stop dataset with parking counts is commercial (Trucker Path, ProMiles, TruckStop POI vendors). OSM approximates locations but not capacities. **Paid gap.**
3. **National weigh-station dataset (maintained).** Died with HIFLD Open (Aug 2025). Replacement = stitching state DOT layers + OSM yourself. No single free national file. **Structural gap** (state-by-state work, not money, closes it).
4. **Real-time weigh-station open/closed + bypass status.** Drivewyze/PrePass proprietary. No state offers a documented public feed. **Paid gap.**
5. **Rest-area amenity freshness signals** (closed for maintenance, dump station status, etc.) — some states expose closures via 511 event APIs, but there's no uniform source; per-state adapters or nothing.
6. **TPIMS anonymous access.** The spec promised open feeds; in practice every state gates behind registration/email (verified: WisTransPortal URLs 404 anonymously). Free, but human-latency onboarding per state — budget for 8 emails, not 8 curl commands.

---

## 8. Source-verification log (what I actually checked on 2026-07-22)

| Check | Result |
|---|---|
| NTAD FeatureServer count query | HTTP 200, `count: 1915` |
| Caltrans Rest Areas FeatureServer JSON | Live, Query capability, point layer, updated 2023-08-15 |
| Caltrans Vehicle Enforcement Facilities count query | HTTP 200, `count: 53` |
| TPIMS V2.2 spec PDF | Downloaded + parsed full text (feeds, schema, auth model, example URLs) |
| WisTransPortal /TPIMS/dynamic + /static | **HTTP 404** (feeds gated; hub page live, access via tpims@topslab.wisc.edu) |
| WisTransPortal TPIMS hub page | Live; archive 2019–present, account + email required |
| 511NY developer docs | Live; truck parking endpoint, free key, 10 calls/60s |
| tpims.ksdot.gov | DNS/connect timeout from test location (likely geofence) — UNCERTAIN |
| MDOT ITS-data page | HTTP 403 to fetcher (bot protection) — UNCERTAIN |
| gis.dot.state.oh.us REST services | Empty response — rest-area REST layer UNCERTAIN, use TIMS portal |
| INDOT FeatureServer via curl | Cloudflare block from non-US IP (service itself is public) |
| Nevada 511Map MapServer | Live but layer list empty — skip |
| taginfo `highway=rest_area` / `amenity=weighbridge` | 42,264 / 12,163 global uses |
| HIFLD Open status | Confirmed discontinued 2025-08-26 |

---

## Verification (adversarial pass)

Independent re-verification performed 2026-07-22 by an adversarial checker (all URLs re-fetched live; counts re-queried; refutation attempted for each claim).

| # | Source | Verdict | Evidence |
|---|---|---|---|
| 1 | BTS NTAD Truck Stop Parking | **CONFIRMED** | FeatureServer JSON live (v12, 1 point layer "Truck Stop Parking", Jason's Law/MAP-21 description, compiled 2019-04-09, WKID 4326). `returnCountOnly` query re-run → `{"count":1915}` exactly as claimed. Metadata states public domain, no copyright. |
| 2 | MAASTO TPIMS state feeds | **CONFIRMED** (claim as written, incl. its own caveats) | Hub page live (last modified 2025-02-19): 8 states, ~150 sites, variables refreshed every minute, access via WisTransPortal account + tpims@topslab.wisc.edu. Spec's anonymous URL `https://transportal.cee.wisc.edu/TPIMS/dynamic` re-tested → **HTTP 404**, matching the researcher's "anonymous URLs now 404" disclosure. Caveat: "intended for third-party redistribution" license wording comes from the spec, not the page — actual per-state terms only visible at registration, as the claim itself says. |
| 3 | WisTransPortal TPIMS Archive | **CONFIRMED** | Same live page states archive covers "2019 to the present day", "150 sites across these eight states", "up to 21 variables refreshed every minute", access = active WisTransPortal account + email tpims@topslab.wisc.edu. All match. Minor: "granted for research/dev use" license phrasing is not printed on the page (no license text at all) — terms settle at account grant. |
| 4 | 511NY Developer API | **CONFIRMED** | Doc page live. Resource list includes **Truck Parking** ("Returns all truck parking"), WZDx at `https://511ny.org/api/wzdx`, free registered-account API key, **"Ten calls every 60 seconds"** rate limit, and a "Developer's Access Agreement" menu item. Multi-state platform claim spot-checked: 511GA doc page contains "Rest Area" and "Ports Of Entry" resources as claimed. |
| 5 | Caltrans Rest Areas + Vehicle Enforcement Facilities | **CONFIRMED** | Rest_Areas FeatureServer live (v11.1, "Safety Roadside Rest Areas", point, Query+Extract, GeoJSON/CSV/Shapefile export, no auth, updated 2023-08-15). Weigh-station count query re-run → `{"count":53}` exactly as claimed. |
| 6 | State rest-area layers + FHWA directory | **CONFIRMED** (with two footnotes) | FHWA HEPGIS "State DOT GIS Websites" page → HTTP 200. TxDOT and WSDOT Hub dataset pages resolve (SPA titles load for the exact datasets). Iowa: the quoted slug 404s to a plain fetcher, **but** the Hub search API returns the "Rest Areas" hosted Feature Service, public, **CC-BY 4.0** — dataset real, deep-link fragile. Footnotes: (a) Iowa layer description says source vintage 2015; (b) MN/IN endpoints were not independently re-verified in this pass. |
| 7 | OSM via Geofabrik + Overpass | **CONFIRMED** | Geofabrik north-america page live, `north-america-latest.osm.pbf` (17.9 GB) timestamped 2026-07-21 (daily cadence visible), footer states **ODbL 1.0**. Taginfo API re-queried: `highway=rest_area` = 42,264, `amenity=weighbridge` = 12,163 — exact match to claimed counts. |
| 8 | FDOT TPAS via FL511 feed | **UNCERTAIN** | Cited page is live but is a **2018 promotional article**: it confirms real-time truck parking exists in FL511, but mentions neither "74 facilities" nor any third-party data feed / registration path. The feed-via-DUA claim is plausible (FL511 is known to offer a third-party feed) and the researcher honestly flags "no anonymous endpoint", but the cited URL does not substantiate the specific access mechanics or facility count. Treat access path as unverified until FDOT confirms. |

**Adversarial summary:** 7 of 8 claims survive hostile re-checking, several with exact-number matches (1915 NTAD points, 53 CA weigh stations, 42,264/12,163 OSM tags, 10-calls/60s NY throttle). The research is unusually honest — its own caveats (TPIMS 404s, NTAD 2019 staleness, registration gates) reproduced exactly. Two soft spots: the FDOT TPAS entry leans on a promo article rather than feed documentation (facility count + onboarding remain unproven), and the Iowa deep-link 404s anonymously even though the dataset is real and CC-BY-licensed via the Hub API. No claim was found to be fabricated, no license claim was found false, and no source requires unauthorized access.
