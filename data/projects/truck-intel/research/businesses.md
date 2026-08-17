# Business Intelligence Near Truck Routes — Legal Free Source Inventory

**Category:** Repair shops, tire shops, towing, truck stops, fuel stations, hotels/motels, food — POI/business data along US truck corridors.
**Researched:** 2026-07-22 (all URLs verified live via web search/fetch on this date unless marked UNCERTAIN)
**Hard constraints honored:** No paid API keys, no proprietary datasets, no ToS-violating scraping. Free registration keys for official/open services (NLR, EIA, Census, 511, Foursquare portal) are allowed — they cost $0 and the providers explicitly invite automated access.

**Labels used:**
- **OFFICIAL** = US government data
- **OPEN** = open-licensed non-government organization
- **COMMUNITY** = crowdsourced (OpenStreetMap ecosystem)

---

## 0. Executive Summary (read this first)

| Question | Honest answer |
|---|---|
| Can we get truck-relevant business POIs (repair, tires, fuel, truck stops, hotels, food) legally for free? | **YES** — OpenStreetMap + Overture Maps Places + Foursquare OS Places, cross-validated, cover this well. |
| Can we get official truck-stop/parking locations? | **YES** — BTS NTAD Truck Stop Parking (public domain, 8,000+ locations). |
| Can we get fuel station locations? | **YES** — OSM/Overture for diesel; official AFDC API for CNG/LNG/EV/biodiesel/hydrogen. |
| Can we get **fuel prices per station**? | **NO free legal source.** EIA gives free regional/state *averages* only. Station-level prices = paid (OPIS, GasBuddy ToS-restricted). |
| Can we get **star ratings / reviews**? | **NO free legal source.** Google Places, Yelp, Tripadvisor are all paid and/or storage-prohibited. Do NOT scrape them. Build your own ratings or use proxy quality signals. |
| Can we get business density stats for corridor analysis? | **YES** — Census County/ZIP Business Patterns by NAICS code (free API). |
| Real-time truck parking availability? | **PARTIAL** — TPIMS states (KY, IN, IA, KS, MI, MN, OH, WI) + some state 511 APIs. Not nationwide. |

---

## 1. Tier-1 Primary Sources (build on these)

### 1.1 OpenStreetMap (OSM) — the POI backbone

| Field | Value |
|---|---|
| **Label** | COMMUNITY |
| **Owner** | OpenStreetMap contributors / OpenStreetMap Foundation |
| **Official URLs** | Data license: https://www.openstreetmap.org/copyright · Overpass API: https://wiki.openstreetmap.org/wiki/Overpass_API · Bulk extracts: https://download.geofabrik.de/north-america/us.html |
| **Coverage** | Worldwide; US coverage strong for fuel, food, hotels; **patchy for truck-specific POIs** (see tag counts below) |
| **Update frequency** | Continuous edits; Geofabrik US extract rebuilt **daily** (verified: last-modified 7 hours before check, 11.2 GB `.osm.pbf`) |
| **Data quality** | Variable by area. Chains (Pilot, Love's, TA, major fuel brands) are well mapped. Independent truck repair/towing is under-mapped. No systematic verification — community QA only. |
| **License** | **ODbL 1.0** — attribution required ("© OpenStreetMap contributors") + **share-alike on derivative databases** (if you mix OSM into a database and publish it, that database must be ODbL too). Verified at osm.org/copyright. |
| **Access methods** | (a) **Bulk download**: Geofabrik `.osm.pbf` / `.gpkg.zip` per state or whole US, load with `osmium`/`osm2pgsql` into PostGIS. (b) **Overpass API** (query language, JSON/XML out) for dev-time queries. (c) Full planet file. |
| **Auth** | None. Free, no key. |
| **Cost** | $0 |
| **Advantages** | Richest attribute model (hgv access, `service:vehicle:*` tags, opening hours, brand, phone); daily updates; you can fix/add data yourself; huge ecosystem (PostGIS, tilemaker, Nominatim). |
| **Limitations** | ODbL share-alike needs care if you enrich and republish; public Overpass servers are shared/rate-limited (~10k users/day capacity, "moderate use" load-shedding, no SLA — commercial products should self-host Overpass or query a local PostGIS import instead: https://operations.osmfoundation.org/policies/api/ and https://www.geofabrik.de/data/overpass-api.html); truck-specific POIs sparse. |

**Verified OSM tag reality check (taginfo API, 2026-07-21):**

| Tag | Global count | Verdict |
|---|---|---|
| `amenity=truck_stop` | **50 objects total** | Effectively unused — do NOT rely on it |
| `shop=truck_repair` | **812 objects** | Real but sparse |
| `highway=services` | **32,455 objects** | The actual "highway service area / truck stop area" tag — use this |
| `amenity=fuel` + `hgv=yes` / `hgv:lanes` / `fuel:HGV_diesel=yes` | combination query needed | The practical truck-fuel filter |

**Practical truck-POI extraction recipe (query a local import, not public Overpass, for production):**
- Truck stops: `highway=services` areas + `amenity=fuel` with `brand` in {Pilot, Love's, TA, Petro, Flying J, Buc-ee's...} + `hgv=yes`
- Repair: `shop=truck_repair`, `shop=car_repair` + `service:vehicle:truck=yes`, `shop=tyres`
- Towing: `service:vehicle:towing=yes` (sparse — see Gaps)
- Food/hotels near corridor: `amenity=restaurant|fast_food`, `tourism=hotel|motel` within buffer of NHS/FAF corridors
- Brand normalization: use **Name Suggestion Index** (§1.8)

---

### 1.2 Overture Maps Foundation — Places theme

| Field | Value |
|---|---|
| **Label** | OPEN (Linux Foundation project; data from Meta, Microsoft, et al.) |
| **Owner** | Overture Maps Foundation |
| **Official URLs** | Guide: https://docs.overturemaps.org/guides/places/ · License page: https://docs.overturemaps.org/attribution/ · Download: https://overturemaps.org/download/ · AWS registry: https://registry.opendata.aws/overture/ |
| **Coverage** | Worldwide; **75.9 million places** (verified June 2026 release), Meta contributes ~58.9M — this is essentially the Facebook business-pages POI universe, so US small-business coverage (independent repair shops, diners, motels) is notably better than OSM |
| **Update frequency** | Monthly-cadence releases (current verified release: **2026-06-17.0**) |
| **Data quality** | Good; every place carries a **confidence score (0-1)** so you can filter junk; `brand` field for chains; operational status field |
| **License** | Places theme: **CDLA-Permissive-2.0** (mixed sources also CC0/Apache-2.0) — permissive, **no share-alike**, commercial use fine, attribution required |
| **Access methods** | Bulk **GeoParquet** on Amazon S3 + Azure Blob; `overturemaps` Python CLI (`overturemaps download --bbox ...`); direct **DuckDB** SQL over S3 (solo-dev friendly: one `duckdb` query pulls a state's POIs, no infra) |
| **Auth** | None. Anonymous S3 reads. |
| **Cost** | $0 |
| **Advantages** | Permissive license (safe to mix with anything); confidence scores; addresses + phones + websites + categories + brand; DuckDB access = simplest possible pipeline for a solo dev |
| **Limitations** | **No ratings/reviews** (verified — docs list no such fields); no truck-specific attributes (no "truck parking spaces" count); monthly not real-time; category taxonomy needs mapping to your own (e.g. `truck_repair`, `truck_stop` categories exist in taxonomy but completeness UNCERTAIN) |

---

### 1.3 Foursquare Open Source Places (FSQ OS Places)

| Field | Value |
|---|---|
| **Label** | OPEN |
| **Owner** | Foursquare |
| **Official URLs** | Announcement: https://foursquare.com/resources/blog/products/foursquare-open-source-places-a-new-foundational-dataset-for-the-geospatial-community/ · Evolution/portal: https://foursquare.com/resources/blog/data/evolving-fsq-os-places/ · Hugging Face mirror: https://huggingface.co/datasets/foursquare/fsq-os-places · Schema: https://docs.foursquare.com/data-products/docs/places-os-data-schema |
| **Coverage** | 100M+ POIs worldwide, strong US commercial POI coverage |
| **Update frequency** | Monthly releases (verified current HF release dated 2026-07-09) |
| **Data quality** | Good for existence/category/name; includes `date_closed` and `date_refreshed` (useful for weeding dead businesses) |
| **License** | **Apache 2.0** with attribution (verified on HF README) |
| **Access methods** | Parquet via Foursquare **Places Portal** (free account + access token, Iceberg catalog on S3) or **Hugging Face** (gated: free account + click-through form) or Snowflake Marketplace; community mirror at https://source.coop/fused/fsq-os-places |
| **Auth** | Free account (portal or HF). No payment. |
| **Cost** | $0 |
| **Advantages** | Third independent POI source → use for **cross-validation/conflation** (a POI present in 2+ of OSM/Overture/FSQ = high confidence it's real); permissive license |
| **Limitations** | **No ratings/reviews in the open dataset** (README shows none; Foursquare keeps ratings in its paid products); gated download adds a manual step; no truck-specific attributes |

---

### 1.4 BTS NTAD — Truck Stop Parking (the official truck-stop layer)

| Field | Value |
|---|---|
| **Label** | OFFICIAL |
| **Owner** | USDOT Bureau of Transportation Statistics (data compiled by FHWA from Jason's Law Truck Parking Survey, MAP-21) |
| **Official URLs** | About: https://geodata.bts.gov/datasets/usdot::truck-stop-parking/about · Explore/download: https://geodata.bts.gov/datasets/fff36e0c37c748a5a1773b5784d4d9a5_0/explore · NTAD home: https://www.bts.gov/ntad · ArcGIS REST folder: https://maps.bts.dot.gov/services/rest/services/NTAD · Archive record: https://rosap.ntl.bts.gov/view/dot/88314 |
| **Coverage** | US-wide; **8,000+ truck parking locations** (public rest areas + private truck stops), with parking space counts where surveyed |
| **Update frequency** | Underlying survey compiled April 2019; ArcGIS item created 2024-06-26, **modified 2025-09-25** (verified via ArcGIS item metadata) — treat attribute freshness as ~survey-era; exact refresh cadence UNCERTAIN |
| **Data quality** | Authoritative for existence/location; amenity attributes (spaces, facilities) dated |
| **License** | **US Government work — "not protected by any U.S. copyrights... available for unrestricted public use"** (verified in item licenseInfo). Public domain. |
| **Access methods** | **ArcGIS REST FeatureServer** (query as GeoJSON), Shapefile / File GDB / CSV / GeoJSON bulk download from geodata.bts.gov |
| **Auth** | None |
| **Cost** | $0 |
| **Advantages** | The only *official national* truck-stop/parking dataset; public domain (mix freely, no share-alike); parking-space counts |
| **Limitations** | Static/dated amenities; no fuel prices, no ratings; private truck stop list not exhaustive |

---

### 1.5 AFDC Alternative Fuel Stations API (DOE / NLR — formerly NREL)

| Field | Value |
|---|---|
| **Label** | OFFICIAL |
| **Owner** | US DOE — National Laboratory of the Rockies (NLR; formerly NREL). **Domain migrated 2026-05-29: use `developer.nlr.gov`, not `developer.nrel.gov`** (verified). |
| **Official URLs** | API docs: https://developer.nlr.gov/docs/transportation/alt-fuel-stations-v1/ · Mirrored dataset at BTS: https://data-usdot.opendata.arcgis.com/datasets/usdot::alternative-fueling-stations/about · data.gov: https://catalog.data.gov/dataset/alternative-fueling-station-locations-422f2 |
| **Coverage** | US + Canada; all public alt-fuel stations: **biodiesel (B20+), CNG, LNG, EV charging, hydrogen, propane, renewable diesel, E85** — the CNG/LNG/EV entries matter for modern fleets |
| **Update frequency** | Continuously maintained station database (per-station `updated_at`) |
| **Data quality** | High — curated by the lab, station-level detail (access hours, truck-class access fields for CNG/LNG) |
| **License** | US government open data; attribution to AFDC customary. Explicit license text on docs page: not stated — UNCERTAIN on formal license string, but it is a federal open-data API built for public consumption. |
| **Access methods** | REST **API** (JSON/CSV; endpoints: all / by id / nearest), free key via api.data.gov signup; also bulk CSV from AFDC/BTS mirror |
| **Auth** | **Free API key** (standard api.data.gov key, $0) |
| **Cost** | $0 (standard api.data.gov rate limit ~1,000 req/hr) |
| **Advantages** | Official, station-level, has "nearest along a route" query built in; covers the fuel types OSM covers worst |
| **Limitations** | Does **not** cover ordinary diesel/gasoline stations (use OSM/Overture for those); no prices |

---

### 1.6 EIA Open Data API — the only legal free fuel-price signal

| Field | Value |
|---|---|
| **Label** | OFFICIAL |
| **Owner** | US Energy Information Administration |
| **Official URLs** | Portal/registration: https://www.eia.gov/opendata/ · Docs: https://www.eia.gov/opendata/documentation.php · Petroleum data: https://www.eia.gov/petroleum/data.php |
| **Coverage** | **On-highway diesel retail price: national + 5 PADD regions + 4 sub-regions + California**, weekly (published Mondays). Gasoline similar. |
| **Update frequency** | Weekly |
| **Data quality** | Gold-standard survey data |
| **License** | US government public domain |
| **Access methods** | REST **API** (JSON) with free registered key; CSV/XLS bulk downloads |
| **Auth** | **Free API key** (emailed on registration) |
| **Cost** | $0 |
| **Advantages** | Legal, stable, forever-free; good enough for "diesel is ~$X in this region this week" trip-cost estimates |
| **Limitations** | **Regional averages only — NOT per-station prices.** Cannot answer "cheapest diesel on this exit." That is a paid gap (see §3.2). |

---

### 1.7 Census County Business Patterns (CBP) + ZIP Code Business Patterns (ZBP)

| Field | Value |
|---|---|
| **Label** | OFFICIAL |
| **Owner** | US Census Bureau |
| **Official URLs** | CBP API: https://www.census.gov/data/developers/data-sets/cbp-zbp/cbp-api.html · ZBP API: https://www.census.gov/data/developers/data-sets/cbp-zbp/zbp-api.html · Bulk: https://www.census.gov/programs-surveys/cbp/data.html |
| **Coverage** | US-wide, annual; establishments/employment/payroll by **NAICS × county/ZIP**. Relevant NAICS: 811111/811198 (vehicle repair), 8113 (heavy truck/machinery repair), 441340 (tire dealers), 488410 (towing), 457/4471 (fuel stations), 72111 (hotels), 7225 (restaurants), 484 (trucking carriers). |
| **Update frequency** | Annual (≈18-month lag) |
| **Data quality** | Authoritative counts; suppression rules hide tiny cells |
| **License** | Public domain |
| **Access methods** | REST **API** (free key) + CSV bulk downloads |
| **Auth** | Free API key |
| **Cost** | $0 |
| **Advantages** | Ground truth for **business density BI** ("this corridor segment has 0 heavy-truck repair establishments within 50 mi") and for validating POI-source completeness |
| **Limitations** | **Aggregates, not points** — no individual business names/locations. Complements, never replaces, POI sources. |

---

### 1.8 State 511 Developer APIs + TPIMS real-time truck parking

| Field | Value |
|---|---|
| **Label** | OFFICIAL (per-state) |
| **Owner** | State DOTs |
| **Verified example URLs** | Wisconsin: https://511wi.gov/developers/help · Georgia: https://511ga.org/developers/doc · Idaho: https://511.idaho.gov/developers/doc · Iowa: https://iowadot.gov/travel-tools/iowa-511/website-and-apps and https://data.iowadot.gov/ · TPIMS interface spec: https://transportal.cee.wisc.edu/tpims/TPIMS_TruckParking_Data_Interface_V2.2.pdf · KY TPIMS: https://drive.ky.gov/Motor-Carriers/Pages/TPIMS.aspx |
| **Coverage** | Per-state. **TPIMS 8-state coalition (KY, IN, IA, KS, MI, MN, OH, WI)** publishes real-time truck-parking availability (JSON, refresh 1-5 min). Many 511 APIs also expose rest areas, cameras, events, weigh stations, EV chargers. WSDOT launched truck-parking info 2025. |
| **Update frequency** | Real-time (1-5 min) for TPIMS dynamic feeds; static feeds as needed |
| **Data quality** | High (sensor-based parking counts), but only at instrumented sites |
| **License** | Free developer access with registration; per-state terms — read each state's developer agreement (generally permissive for display with attribution). Formal license strings vary: UNCERTAIN per state until you register. |
| **Access methods** | REST **API** (JSON/XML), free developer key per state |
| **Auth** | Free registration per state |
| **Cost** | $0 |
| **Advantages** | The ONLY legal real-time "is there parking at this truck stop" data; official |
| **Limitations** | Fragmented — one integration per state; nationwide coverage does not exist; mostly covers public rest areas + select private stops on instrumented corridors |

---

### 1.9 BTS NTAD — Intermodal Freight Facilities (freight-demand context)

| Field | Value |
|---|---|
| **Label** | OFFICIAL |
| **Owner** | USDOT BTS |
| **Official URLs** | https://geodata.bts.gov/ (search "Intermodal Freight Facilities") · e.g. https://data-usdot.opendata.arcgis.com/datasets/usdot::intermodal-freight-facilities-pipeline-terminals/about · REST: https://geo.dot.gov/server/rest/services/NTAD/ |
| **Coverage** | US intermodal terminals: air-to-truck (top-60 airports), rail/truck, pipeline, marine; modal connections + commodities |
| **Update frequency** | Per-dataset compile dates (2017-2021 era); UNCERTAIN refresh cadence |
| **License** | US Government public domain |
| **Access** | ArcGIS REST + GeoJSON/Shapefile/CSV download; no auth; $0 |
| **Use for BI** | Where trucks concentrate → where repair/fuel/food demand concentrates. Context layer, not a POI layer. |

---

### 1.10 FMCSA public registries (niche but official)

| Field | Value |
|---|---|
| **Label** | OFFICIAL |
| **Owner** | FMCSA |
| **Verified URLs** | Cargo Tank Facility registration: https://www.fmcsa.dot.gov/registration/cargo-tank-facilities · SAFER Cargo Tank Facility dataset record: https://catalog.data.gov/dataset/safer-cargo-tank-facility · Motor Carrier Census + inspections downloads: https://ai.fmcsa.dot.gov/SMS/Tools/Index.aspx · https://data.transportation.gov/Trucking-and-Motorcoaches/Vehicle-Inspections-and-Violations/876r-jsdb |
| **What exists** | (a) **Cargo Tank (CT) facility registry** — facilities certified to manufacture/inspect/repair *cargo tanks* (searchable via SAFER, dataset listed on data.gov — "intended for public access and use"). (b) **Motor Carrier Census** — all registered carriers with addresses (business-density BI, potential B2B layer). (c) Inspection/violation datasets. |
| **What does NOT exist** | **There is NO FMCSA registry of general truck repair shops.** The CT registry covers only hazmat cargo-tank work — a narrow, specialized slice. Anyone claiming FMCSA lists "repair shops" nationally is wrong. |
| **License / cost** | Public domain / $0 / bulk CSV + web query |
| **Limitation** | CT registry ≠ consumer-facing repair directory; addresses need geocoding (use Census geocoder, free) |

---

### 1.11 Name Suggestion Index (NSI) — brand normalization helper

| Field | Value |
|---|---|
| **Label** | OPEN |
| **Owner** | OSM community (osmlab) |
| **URLs** | https://github.com/osmlab/name-suggestion-index · browse: https://nsi.guide/ |
| **What it is** | Canonical list of brands (Pilot Flying J, Love's, TA/Petro, Speedco, major tire/repair chains, hotel & fast-food chains) with matching rules. **3-Clause BSD license** (verified). |
| **Use** | Normalize/dedupe brand names when conflating OSM + Overture + FSQ; identify "this fuel POI is actually a major truck-stop chain." JSON in the repo, $0, no auth. |

---

### 1.12 SAM.gov Entity Extracts (marginal — listed for completeness)

| Field | Value |
|---|---|
| **Label** | OFFICIAL |
| **Owner** | GSA |
| **URLs** | https://open.gsa.gov/api/sam-entity-extracts-api/ · https://sam.gov/entity-information |
| **What it is** | Monthly public extract of businesses registered for federal contracting (name, address, NAICS, POC). Free account. |
| **Honest assessment** | Only businesses that *want government contracts* — a skewed sliver of roadside businesses. **Low value for this platform**; do not build on it. Included so the "SBA/business registry" lead is answered honestly: there is **no national geocoded all-business registry** in the US open-data world. State Secretary-of-State registries exist per state but are non-geocoded, non-uniform, and often ToS/fee-restricted — not practical. |

---

## 2. Ratings & Reviews — the honest assessment (CRITICAL)

**Bottom line: there is NO legal free source of star ratings or review text for US businesses. Every path is paid, storage-prohibited, or both. Do not scrape.**

| Provider | Cost | Can you store/cache ratings? | Verdict |
|---|---|---|---|
| **Google Places API** | Paid (per-call, Maps Platform billing) | **NO** — ToS prohibits pre-fetch/cache/store of content; only `place_id` storable indefinitely, lat/lng ≤30 days; content must be shown live with Google attribution, effectively on a Google map. Scraping Maps explicitly prohibited. (Verified: https://developers.google.com/maps/documentation/places/web-service/policies and https://cloud.google.com/maps-platform/terms/maps-service-terms) | **Unusable** under our constraints |
| **Yelp Fusion API** | **Free tier ended** — now paid plans from $7.99/1k calls (30-day trial only). (Verified: https://business.yelp.com/data/resources/pricing/ and https://terms.yelp.com/developers/api_terms/20250113_en_us/) | No bulk storage; display rules | **Unusable** (paid) |
| **Tripadvisor Content API** | 5,000 calls/month free BUT requires partner approval, credit card on file, B2C display rules, must use their bubble icons, no warehousing | Restricted display-only | **Unusable as a data source**; at best a display widget for hotels if approved. (Verified: https://developer-tripadvisor.com/content-api/ · https://tripadvisor-content-api.readme.io/reference/api-master-terms-new) |
| **Scraping Google/Yelp SERPs** (or "scraper API" resellers) | — | — | **Refused — violates ToS.** Not recommended under any framing. |

**What a solo dev CAN legally do instead:**
1. **Own ratings loop** — let platform users rate/review stops. You own the data 100%. This is how Trucker Path built its moat; it is the only durable legal path.
2. **Proxy quality signals (all free/legal):** brand affiliation (chain = predictable quality) via NSI/Overture `brand`; presence in 2-3 independent POI datasets (OSM+Overture+FSQ conflation confidence); Overture confidence score; FSQ `date_refreshed`/`date_closed` (recently-refreshed = likely operating); amenity richness in OSM (showers, parking count tagged = cared-for POI).
3. **Official signals:** NTAD parking-space counts; FMCSA inspection-activity density (where inspections happen, services cluster).

---

## 3. Named paid gaps (no free equivalent exists — say it like it is)

| # | Gap | What the paid world uses | Free reality |
|---|---|---|---|
| 3.1 | **Star ratings / review text** | Google Places API, Yelp Fusion, Tripadvisor | None. Build own + proxies (§2). |
| 3.2 | **Station-level diesel prices (real-time)** | OPIS (industry standard, $$$), GasBuddy (ToS-restricted app data), Pilot/Love's apps | EIA weekly **regional averages** only (§1.6). |
| 3.3 | **Verified towing directory with dispatch info** | NTTS Breakdown Directory, FleetNet — commercial | OSM towing tags sparse; CBP NAICS 488410 gives *counts* only. No open national towing registry exists. |
| 3.4 | **Truck-stop amenity freshness** (showers, scales, reserved parking, live occupancy nationwide) | TruckerPath/chain apps (proprietary crowdsourcing) | NTAD static + TPIMS 8 states + OSM tags. Partial. |
| 3.5 | **Chain locator feeds** (Pilot/Love's/TA official store JSON) | Private app APIs; no open-data program; site ToS generally prohibit automated collection | Use OSM/Overture/FSQ coverage of these brands instead (it is good). Do not scrape locators. |
| 3.6 | **Phone/hours completeness at Google's level** | Google Places | Overture/FSQ/OSM have these fields but fill rates are lower. Accept it. |

---

## 4. Considered and rejected (with reasons)

| Source | Why rejected |
|---|---|
| **HIFLD Open** (DHS) | **Discontinued Aug 26, 2025**; portal offline since Sep 2025. Successor layers moved to HIFLD Secure (gov-only) or back to originating agencies. Archives exist (https://source.coop/seerai/hifld, https://www.datalumos.org/datalumos/project/241367/version/V1/view) but are frozen snapshots — use the live originating-agency sources in §1 instead. (Verified: https://www.napsgfoundation.org/hifld_open/) |
| **SafeGraph / Data Axle / Infogroup / Dun & Bradstreet** | Proprietary commercial POI/firmographic datasets. Paid. Out of scope by constraint. |
| **GasBuddy** | Crowdsourced prices, but API/ToS restricted; no open license. |
| **Trucker Path** | Proprietary app; no public API. |
| **NATSO truck-stop directory** | Trade-association member directory; no open license (UNCERTAIN terms) — skip. |
| **Yellow-pages-style sites** | Scraping violates ToS; no bulk license. |
| **OSHA/enforcement establishment lists** | Public domain, but heavily skewed (only inspected firms) and non-truck-specific — noise. |
| **Road511.com** (unified 511 aggregator) | Useful commercial normalization of 65 jurisdictions but a **paid third-party product** — integrate the free state 511 feeds directly instead. |

---

## 5. Recommended build stack (simple, boring, solo-dev-sized)

**Layer 1 — Static POI base (refresh monthly):**
DuckDB pulls Overture Places (S3, no auth) + FSQ OS Places (HF parquet) for target categories → PostGIS. Geofabrik US `.osm.pbf` → `osmium tags-filter` for truck tags → same PostGIS. Conflate by name+distance, normalize brands with NSI. Score = how many sources agree + Overture confidence.

**Layer 2 — Official overlays (refresh quarterly):**
NTAD Truck Stop Parking (GeoJSON, public domain) as the authoritative truck-parking layer; NTAD intermodal facilities as demand context; AFDC API for CNG/LNG/EV/biodiesel stations.

**Layer 3 — Live signals (refresh weekly/real-time):**
EIA API weekly regional diesel prices; TPIMS/511 feeds for real-time parking in the 8+ instrumented states.

**Layer 4 — Analytics:**
Census CBP/ZBP by NAICS for corridor-segment business-density scoring and gap detection ("service desert" flags).

**Compliance one-liners:** attribute "© OpenStreetMap contributors (ODbL)"; keep OSM-derived tables ODbL-share-alike-clean (simplest: keep the conflated POI database internally consistent — if you publish the database itself, publish under ODbL; displaying results/"produced work" is fine with attribution); attribute Overture (CDLA-P-2.0) and Foursquare (Apache 2.0); federal data is public domain, courtesy attribution to BTS/FHWA/EIA/Census.

---

## 6. Source-by-source quick matrix

| Source | Label | License | Access | Auth | Points or aggregate | Truck-specific? | Fresh? |
|---|---|---|---|---|---|---|---|
| OpenStreetMap (Geofabrik/Overpass) | COMMUNITY | ODbL 1.0 (share-alike) | PBF bulk / Overpass API | None | Points | Partly (sparse tags) | Daily |
| Overture Places | OPEN | CDLA-P-2.0 | GeoParquet S3/Azure, DuckDB, CLI | None | Points (75.9M) | Categories only | Monthly |
| FSQ OS Places | OPEN | Apache 2.0 | Parquet (portal/HF, free acct) | Free account | Points (100M+) | Categories only | Monthly |
| NTAD Truck Stop Parking | OFFICIAL | Public domain | ArcGIS REST / GeoJSON / SHP / CSV | None | Points (8k+) | **Yes** | Item modified 2025-09; survey-era attrs |
| AFDC Alt-Fuel Stations | OFFICIAL | Gov open data | REST API / CSV | Free key | Points | Alt-fuel yes | Continuous |
| EIA diesel prices | OFFICIAL | Public domain | REST API / CSV | Free key | Regional aggregate | Diesel yes | Weekly |
| Census CBP/ZBP | OFFICIAL | Public domain | REST API / CSV | Free key | County/ZIP aggregate | Via NAICS | Annual |
| State 511 / TPIMS | OFFICIAL | Per-state terms | REST API JSON | Free per-state key | Points + live counts | **Yes** (parking) | 1-5 min |
| NTAD Intermodal | OFFICIAL | Public domain | ArcGIS REST / downloads | None | Points | Freight context | 2017-21 era |
| FMCSA CT registry / Carrier Census | OFFICIAL | Public domain | Web query / CSV bulk | None | Addresses (geocode) | Niche | Ongoing |
| NSI (brands) | OPEN | BSD-3 | GitHub JSON | None | Reference list | Chain IDs | Ongoing |
| SAM.gov extracts | OFFICIAL | Public | Monthly extract | Free account | Addresses | No (skewed) | Monthly |

---

*Every "Verified" claim above was confirmed live on 2026-07-22 via web search/fetch. Items marked UNCERTAIN could not be fully confirmed and must be re-checked at integration time. No source in this document requires payment, ToS violation, or credential workarounds.*

---

## Verification (adversarial pass)

Independent adversarial re-verification, 2026-07-22. Each URL was fetched live; findings below attempt to refute the researcher's claims.

| # | Source | Status | Finding |
|---|---|---|---|
| 1 | Overture Maps Places | **CONFIRMED** | Docs live. "More than 75 million" places, confidence score 0-1, brand/address/phone/website fields, free access via S3 GeoParquet + Azure + Python CLI + DuckDB — all verified on page. License is *mixed* per source: largest contributor (Meta, 58.9M features, June 2026) is CDLA-Permissive-2.0; other sources CC0-1.0/Apache-2.0. All permissive — claim holds. |
| 2 | OSM via Geofabrik US extract | **CONFIRMED** | Page live; `us-latest.osm.pbf` = 11.2 GB, last modified 8 hours before fetch (data through 2026-07-21, daily rebuilds). ODbL 1.0 stated in footer. No auth, no cost. Only the metadata-stripped public variant is anonymous — irrelevant for POI use. Taginfo counts not re-checked this pass. |
| 3 | Foursquare OS Places (HF) | **CONFIRMED** | Dataset page live; Apache 2.0 stated; parquet (places + categories); `date_closed` / `date_refreshed` fields present in schema; latest release 2026-07-09 matches claim; ~227 GB, "100M-1B" size class. Caveat: HF access is **gated** — you must share contact info AND accept a clause letting Foursquare use your employer/entity name in marketing. Free, but not friction-free; read the click-through before accepting. |
| 4 | BTS NTAD Truck Stop Parking | **CONFIRMED** | The /about HTML page renders client-side (near-empty to fetchers), but the underlying ArcGIS item (fff36e0c37c748a5a1773b5784d4d9a5) verified directly via arcgis.com REST JSON: owner USDOT_BTS, public Feature Service, licenseInfo verbatim = "not protected by any U.S. copyrights... available for unrestricted public use", modified 2026. Exact 8,000+ count and parking-space attributes not independently recounted — plausible per NTAD/Jason's Law provenance. |
| 5 | AFDC Alt-Fuel Stations API (NLR) | **CONFIRMED** | Docs live on developer.nlr.gov; endpoints verified (all / by-id / nearest / **nearby-route** / EV networks; JSON+CSV); fuel types match claim exactly (biodiesel B20+, CNG, LNG, EV, E85, hydrogen, propane, renewable diesel); NREL→NLR migration explicitly confirmed on page ("developer.nrel.gov... retired on May 29, 2026"). Minor: the fetched page does not itself state the api.data.gov key requirement or the ~1k req/hr limit — standard for this API family but re-check at signup. |
| 6 | EIA Open Data API | **CONFIRMED** | Portal live; "EIA data is provided free of charge", free registered API key confirmed. Weekly/daily/monthly retail diesel prices listed among offerings; the exact PADD/sub-region breakdown wasn't itemized on the portal page itself (it lives in the API browser) — long-standing EIA product, low risk, but confirm series IDs at integration. |
| 7 | State 511 / TPIMS feeds | **UNCERTAIN** | TPIMS V2.2 spec PDF fetched and read: genuine MAASTO 8-state spec; dynamic + static **public feeds explicitly "meant to be shared with third party application developers"** — intent confirmed. BUT 511wi.gov/developers/help returned **HTTP 403 to automated fetch** (bot protection), so the per-state free-registration claim and each state's developer terms could NOT be verified this pass. Spec is also 2019-era (v2.2 July 2019) — per-state feed liveness must be verified state-by-state at registration time, in a real browser. |
| 8 | Census CBP/ZBP API | **CONFIRMED** | Page live (revised 2026-05-20); annual establishment stats by 2-6 digit NAICS at county level; free API key required, no fees. ZBP variant not separately fetched but same program/portal. |

**Overall:** 7 of 8 sources fully survive adversarial verification — live, free, licensed as claimed, and open to automated access; the researcher's claims are accurate and in places conservative (Overture's mixed-but-all-permissive licensing, FSQ's marketing-clause gate are the only nuances worth noting). The single UNCERTAIN is State 511/TPIMS: the coalition spec and public-feed intent are verified, but the state developer portals themselves resist automated fetching (511wi 403), so free-key access and current feed liveness must be confirmed per state manually — consistent with the researcher's own "read each agreement" caveat. The document's honest paid-gap admissions (per-station fuel prices, ratings/reviews) were not contradicted by anything found in this pass.
