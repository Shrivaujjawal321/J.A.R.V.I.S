# Fuel Intelligence — Legal Free Source Inventory (US Truck Intelligence Platform)

**Category:** Diesel / gasoline / DEF / LNG / CNG stations + prices
**Researched:** 2026-07-22 (all URLs verified live on this date unless marked otherwise)
**Constraint honored:** free + legally authorized access only. No scraping of ToS-restricted sites, no paid keys.

---

## TL;DR — What exists, what doesn't

| Need | Free legal source? | Best option |
|---|---|---|
| Fuel **station locations** (all fuels, US-wide) | YES | OpenStreetMap (`amenity=fuel`), ~109k US stations |
| **Alternative fuel** station locations (CNG/LNG/biodiesel/renewable diesel/EV/H2/propane/E85) | YES | NREL AFDC API + bulk CSV/GeoJSON (free key) |
| **Diesel/gas price trends** (national/regional/state, weekly) | YES | EIA Open Data API v2 (free key) |
| **Station-level diesel/gas prices** | **NO — honest gap** | Only paid/ToS-restricted (OPIS, GasBuddy, DTN, Mudflap, Fuelbook) |
| **DEF availability** map | **Mostly a gap** | OSM `fuel:adblue` tag exists but is sparse; no official dataset |
| Real-time prices | NO | Even paid data is at best daily; EIA is weekly regional |

---

## 1. EIA Open Data API v2 — fuel price trends — OFFICIAL

| Field | Value |
|---|---|
| **Owner** | U.S. Energy Information Administration (U.S. Dept. of Energy) |
| **Official URL** | https://www.eia.gov/opendata/ · docs: https://www.eia.gov/opendata/documentation.php · human view: https://www.eia.gov/petroleum/gasdiesel/ |
| **Geographic coverage** | US national, 5 PADD regions, sub-PADDs (1A New England, 1B Central Atlantic, 1C Lower Atlantic, "West Coast less California"). **Gasoline** additionally: 9 states (CA, CO, FL, MA, MN, NY, OH, TX, WA) + 10 cities (Boston, Chicago, Cleveland, Denver, Houston, LA, Miami, NYC, SF, Seattle). **Diesel (on-highway)**: national + PADDs + sub-PADDs + **California only** — NOT per-state, NOT per-city (verified on the gasdiesel page 2026-07-22). |
| **Update frequency** | Weekly (verified on page: release 2026-07-21, next release 2026-07-28). Survey-based retail averages. |
| **Data quality** | Excellent for what it is: official survey-based averages, long history (decades), stable series IDs. It is a **trend/context layer, NOT station-level** — this must be stated plainly. |
| **License** | US government work → **public domain** (verified at https://www.eia.gov/about/copyrights_reuse.php: "U.S. government publications are in the public domain"). Attribution requested: "Source: U.S. Energy Information Administration (date)". EIA logo is trademarked — don't use it. |
| **Access method** | REST API v2 (JSON default, XML capped at 300 rows). Route for retail gas+diesel prices: `petroleum/pri/gnd` (per EIA API docs and the data.gov catalog entry "Petroleum Data: Prices API": https://catalog.data.gov/dataset/petroleum-data-prices-application-programming-interface-api). Also bulk XLS "Download Series History" on the gasdiesel page. |
| **Auth** | Free API key, auto-emailed on registration at eia.gov/opendata. |
| **Cost** | $0 |
| **Advantages** | Public domain; stable; the only authoritative US fuel-price statistics; trivial to cache (updates once a week); perfect for "diesel is trending up in PADD 3 this week" intelligence and for calibrating fuel-cost estimates per route region. |
| **Limitations** | NOT station-level, NOT daily, diesel not broken out per state (except CA). Rate limits exist but numbers are not published ("throttle requests per second and per hour"; exceeding causes temporary auto-suspension) — a weekly cron fetch is far below any threshold. |
| **Label** | OFFICIAL |

**Practical use:** one weekly cron job pulls `petroleum/pri/gnd` (diesel, all areas) → store ~15 rows/week in SQLite/Postgres. That's the entire integration.

---

## 2. NREL AFDC Alternative Fuel Stations API v1 — CNG/LNG/biodiesel/RD/EV/H2 locations — OFFICIAL

> **CRITICAL 2026 CHANGE (verified):** the old domain `developer.nrel.gov` **was retired on May 29, 2026** and no longer resolves in DNS (confirmed by direct fetch failure on 2026-07-22). The live domain is **`developer.nlr.gov`**. Any tutorial/blog from before mid-2026 will show the dead domain.

| Field | Value |
|---|---|
| **Owner** | National Renewable Energy Laboratory (NREL) / U.S. DOE — Alternative Fuels Data Center (AFDC) |
| **Official URL** | https://developer.nlr.gov/docs/transportation/alt-fuel-stations-v1/ · station locator: https://afdc.energy.gov/stations · historical downloads: https://afdc.energy.gov/data_download/historical_stations_format |
| **Geographic coverage** | Entire US (+ Canada for some fuels) |
| **Update frequency** | Continuous curation by NREL; a `Last Updated Date` endpoint reports the last refresh. Exact internal cadence: UNCERTAIN (not published), but the locator is actively maintained. |
| **Data quality** | High — curated, deduplicated, includes access type (public/private), status (open/planned/temporarily unavailable), connector/fill-pressure details, hours, payment methods. |
| **License** | API/locator data: US DOE-produced, effectively open with attribution; the OEDI archival snapshots are explicitly **CC-BY-4.0** (verified at https://data.openei.org/submissions/106). |
| **Access method** | REST API (JSON; CSV available, plus CSV/GeoJSON/shapefile bulk downloads from the Station Locator). Endpoints: **All Stations**, **Station by ID**, **Nearest** (radius), **Nearby Route** (stations along a driving route — directly useful for truck routing!), EV networks, EV ports, Last Updated. |
| **Auth** | Free api.data.gov-style key. Rate limits (verified at https://developer.nlr.gov/docs/rate-limits/): **1,000 requests/hour** standard key; DEMO_KEY = 30/hr, 50/day. |
| **Cost** | $0 |
| **Advantages** | The definitive US source for **CNG, LNG, biodiesel (B20+), renewable diesel (R20+), propane, E85, hydrogen, EV** stations. `nearby-route` endpoint accepts a route geometry — maps perfectly onto truck-safe routing. Bulk download = no per-request dependency. |
| **Limitations** | **Does NOT cover conventional diesel/gasoline stations** (it's alternative fuels only). **No prices.** **No DEF.** LNG station count in the US is small (that's reality, not a data flaw). |
| **Label** | OFFICIAL |

**Historical/archival variants (same data family):**
- **AFDC historical downloads** — single-day snapshots + per-station change ranges: https://afdc.energy.gov/data_download/historical_stations_format (free, same license posture).
- **OEDI snapshots** (CC-BY-4.0, CSVs from 2012/2014/2021 — stale, archival only): https://data.openei.org/submissions/106
- **Data.gov catalog entry** (pointer to the same): https://catalog.data.gov/dataset/alternative-fueling-station-locations-422f2
- **AFDC Alternative Fuel Corridors station data** (stations grouped by FHWA freight/fuel corridors — nice tie-in to the freight-corridor category): https://afdc.energy.gov/corridors

---

## 3. OpenStreetMap — ALL fuel stations incl. truck-diesel + DEF tags — COMMUNITY

| Field | Value |
|---|---|
| **Owner** | OpenStreetMap contributors / OpenStreetMap Foundation |
| **Official URL** | wiki: https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dfuel · fuel keys: https://wiki.openstreetmap.org/wiki/Key:fuel |
| **Geographic coverage** | Worldwide. **US extract: 108,933 `amenity=fuel` objects** (43,736 nodes / 64,320 ways / 877 relations — verified via taginfo.geofabrik.de `north-america:us` on 2026-07-21 data). Worldwide: 565,015. |
| **Update frequency** | Continuous (minutely diffs); Geofabrik extracts rebuilt daily. |
| **Data quality** | Good for **locations** of stations in the US (~109k vs an estimated ~120-150k real US stations — coverage is strong but not complete; completeness per county: UNCERTAIN). Attribute richness varies: `fuel:diesel`, `hgv=yes` (truck-accessible), `fuel:HGV_diesel` (truck lanes), `fuel:adblue` (DEF), `brand`, `opening_hours` exist but are inconsistently applied. **`fuel:adblue` has only 7,690 objects worldwide** (verified via taginfo) and most are in Europe — US DEF tagging is sparse. **OSM has NO usable price data** — say this honestly; price tags are effectively unused and instantly stale. |
| **License** | **ODbL 1.0** — free for commercial use, requires attribution ("© OpenStreetMap contributors") and share-alike on *derivative databases*. |
| **Access method** | (a) **Geofabrik bulk extracts** (free `.osm.pbf`, US or per-state): https://download.geofabrik.de/north-america.html — process with `osmium`/`osm2pgsql`/DuckDB spatial; (b) **Overpass API** for spot queries; (c) planet files. |
| **Auth** | None. |
| **Cost** | $0 |
| **Advantages** | The ONLY free legal source of **conventional diesel/gas station locations** US-wide. Bulk download = zero API dependency, works offline, simple pipeline (download weekly → filter `amenity=fuel` → load to Postgres/SQLite). Truck-specific tags exist (`hgv`, `fuel:HGV_diesel`, `access`). |
| **Limitations** | Crowd-sourced: no guarantee of completeness/freshness per station; attribute gaps (many stations lack `fuel:diesel` even when they sell it); NO prices; DEF tag sparse in the US; ODbL share-alike needs a moment of thought if you mix it into a proprietary DB (keep OSM-derived layers separable + attributed). |
| **Label** | COMMUNITY |

**Overpass API usage policy (verified on the OSM wiki, 2026-07-22):** the main public instance (overpass-api.de) is free under fair use — "you don't disturb other users when you do less than **10,000 queries per day** and download less than **1 GB data per day**"; send a proper `User-Agent`. For a production platform: use **Geofabrik bulk extracts** as primary (bulk is politer and simpler) and Overpass only for dev/spot checks, or self-host Overpass (AGPL v3).

---

## 4. Station-level diesel/gasoline PRICES — HONEST ANSWER: **NO free legal source exists**

This is the question that matters most, so here it is plainly:

**There is NO legal, free, automated source of station-level fuel prices in the United States. None. Anyone claiming otherwise is reselling scraped or licensed commercial data.**

Why (verified 2026-07-22):

| Source | Status | Detail |
|---|---|---|
| **GasBuddy** | ToS-restricted | Crowd-sourced prices, but ToS (updated June 22, 2026: https://help.gasbuddy.com/hc/en-us/articles/40439396627991) prohibits reproducing/reselling/exploiting any portion of the site for commercial purposes. No free API. Scraping = ToS violation → **off-limits**. |
| **OPIS** (Dow Jones) | Commercial | The industry standard; their Truckstop Report covers daily retail diesel at 9,000+ truck stops (https://www.opis.com/product/pricing/retail-fuel-prices/truckstop-spread-report/). Paid license only. |
| **AAA gas prices** | ToS-restricted | Public webpage, but the underlying data IS OPIS (licensed). No API, no reuse permission. |
| **DTN, Mudflap, Fuelbook, Trucker Path, FleetCollect** | Commercial | Apps/feeds with truck-stop diesel prices; all paid or closed. |
| **TruckMaster Fuel Finder** (findfuelstops.com) | Free web tool, no API | Free for human use along a route; no bulk/API offering, no open license. Site was **unreachable (connection refused) at verification time 2026-07-22** — reliability UNCERTAIN. Automated reuse: not permitted → not a data source for us. |
| **Apex Fuel Finder** (apexcapitalcorp.com/fuel/fuel-finder/) | Free web tool, no API | Same story: human-use map, no open data. |
| **OilPriceAPI and similar API-hub resellers** | Commercial | Free tiers only expose EIA state/regional averages (which we get direct from EIA anyway); station-level is paid. |

**Root cause:** unlike Germany (Tankerkönig), France, Spain, or NSW Australia — where governments *mandate* open publication of station prices — the US has **no legal requirement** for stations to publish prices. So station-level price data only exists inside commercial ecosystems (OPIS surveys, GasBuddy crowd-sourcing, fuel-card transaction networks).

**Named paid gap:** OPIS (gold standard), GasBuddy Business/data licensing, DTN Fuel Data, Mudflap/Fuelbook partnerships. If the platform ever monetizes, this is the line item to budget.

**Legal free approximation (recommended):** OSM station locations + EIA weekly regional averages → show "typical diesel price in this area this week" per station cluster, clearly labeled as a regional estimate, never as a pump price. This is honest, legal, and still useful for route fuel-cost planning.

---

## 5. DEF (Diesel Exhaust Fluid) availability — MOSTLY A GAP

What exists (verified 2026-07-22):

| Source | Label | Verdict |
|---|---|---|
| **OSM `fuel:adblue=yes`** | COMMUNITY | The only open-data DEF signal. 7,690 objects worldwide, heavily European; US coverage sparse (exact US count: UNCERTAIN, but small). Legal, free, ODbL. Usable as a *partial* layer. |
| **NREL AFDC** | OFFICIAL | Does **NOT** track DEF (DEF is an emissions fluid, not an alternative fuel). Confirmed by its fuel-type list. |
| **Retailer locators** — TA/Petro DEF page (https://www.ta-petro.com/professional-drivers/def-fuel/), Love's, Pilot | Commercial sites | Free for humans; no API/open license; automated scraping violates ToS → off-limits. |
| **DEF Search** (defsearch.com) | Community app | Community-verified DEF pump map; free to use as an app, but **no API, no bulk download, no open license found** (verified) → not integrable legally. |
| **FindDEF.com** | Commercial directory | Web map only; no open data. |
| **American Petroleum Institute DEF program** | — | Their DEF Locator page now returns **404** (verified 2026-07-22). API's DEF program certifies DEF *brands*, not station locations. |
| **DiscoverDEF** | — | Educational/where-to-buy info, not a structured station dataset. |

**Honest bottom line:** there is **no official or open nationwide DEF-availability dataset**. Legal free options are (a) OSM `fuel:adblue` (sparse), plus (b) a defensible heuristic: essentially all major-chain US truck stops (Pilot/Flying J, Love's, TA/Petro) dispense DEF at the diesel pump — so "major chain truck stop (from OSM `brand`)" ⇒ "DEF almost certainly available", displayed as an inference, not a fact. Anything better requires commercial data or retailer partnerships.

---

## 6. Supplementary / adjacent sources (verified pointers)

| Source | What it adds | Access | Label |
|---|---|---|---|
| **EIA bulk XLS series history** (on https://www.eia.gov/petroleum/gasdiesel/) | Full weekly price history back-fill without API calls | XLS download, no auth | OFFICIAL |
| **EIA State Energy Data System (SEDS)** | Annual state-level fuel prices/expenditures (too coarse for ops; fine for analytics) | API + CSV | OFFICIAL |
| **Data.gov catalog entries** ("Petroleum Data: Prices API", "Alternative Fueling Station Locations") | Discovery/metadata only — they point back to EIA/NREL | CKAN | OFFICIAL |
| **AFDC TransAtlas / corridor station data** (https://afdc.energy.gov/corridors) | Alt-fuel stations organized along FHWA corridors — bridges to the freight-corridor category | Web + underlying AFDC API | OFFICIAL |

---

## 7. Recommended build stack for this category (boring-tech, solo-dev friendly)

1. **Base station layer:** Geofabrik US `.osm.pbf` weekly → filter `amenity=fuel` (+`hgv`, `fuel:*`, `brand`, `opening_hours`) → Postgres/PostGIS or DuckDB. One script, no API keys, no rate limits. Attribution: "© OpenStreetMap contributors, ODbL".
2. **Alt-fuel overlay (CNG/LNG/biodiesel/RD/EV/H2):** AFDC bulk CSV/GeoJSON download weekly + `last-updated` check; use the API's `nearby-route` endpoint at request time for route-aware lookups (free key, 1,000 req/hr is plenty).
3. **Price context layer:** EIA API v2 `petroleum/pri/gnd` weekly cron → regional diesel/gas averages joined to stations by PADD/state. Label as regional estimates.
4. **DEF layer:** OSM `fuel:adblue` where present + chain-brand heuristic, clearly marked as inferred.
5. **Do NOT build:** any scraper against GasBuddy/AAA/retailer locators — ToS-restricted, legal risk, and against project constraints.

Total moving parts: 3 cron jobs + 1 free API key (NREL) + 1 free API key (EIA). That's the whole category.

---

## 8. Licensing & attribution cheat-sheet

| Source | License | Required attribution |
|---|---|---|
| EIA | Public domain (US gov) | "Source: U.S. Energy Information Administration (date)" — requested, not legally required |
| NREL AFDC | Open / CC-BY-4.0 (OEDI snapshots) | Credit NREL/AFDC |
| OpenStreetMap | ODbL 1.0 | "© OpenStreetMap contributors" + share-alike on derivative *databases* |

## 9. UNCERTAIN items (flagged honestly)

- Exact EIA API numeric rate limits — not published (weekly polling is safely under any threshold).
- NREL AFDC internal update cadence — continuous but unpublished; use the `last-updated` endpoint.
- Exact US-only count of OSM `fuel:adblue` — worldwide 7,690; US share small but not separately verified.
- OSM US fuel-station completeness % vs ground truth — no authoritative station census exists to compare against.
- findfuelstops.com availability — connection refused at verification time.

---

## Verification (adversarial pass)

**Verified 2026-07-22 by independent adversarial pass (live WebFetch/API checks, attempting to refute each claim).**

| # | Source | Status | Finding |
|---|---|---|---|
| 1 | OSM fuel stations (Geofabrik US extract) | **CONFIRMED** | download.geofabrik.de/north-america.html live; free .osm.pbf for US (11.2 GB) rebuilt daily ("last modified 8 hours ago"); ODbL 1.0 stated on-page. Taginfo JSON API independently returned **exactly 108,933** `amenity=fuel` US objects (43,736 nodes / 64,320 ways / 877 relations, data 2026-07-21) — the claimed count matches to the digit. |
| 2 | NREL AFDC Alt Fuel Stations API v1 (developer.nlr.gov) | **CONFIRMED** | The suspicious-looking domain claim survives refutation: `developer.nrel.gov` fails DNS (ENOTFOUND), while `developer.nlr.gov/docs/transportation/alt-fuel-stations-v1/` is live and itself carries the notice "the previous developer.nrel.gov domain was retired on May 29, 2026." Rate-limits page confirms 1,000 req/hr standard key, DEMO_KEY 30/hr + 50/day. Key signup present; pricing not explicitly stated on the rate-limits page but signup is the standard free api.data.gov flow and no fee is mentioned anywhere. |
| 3 | EIA Open Data API v2 (petroleum/pri/gnd) | **CONFIRMED** | eia.gov/opendata live; "EIA data is provided free of charge," free key via registration; petroleum section explicitly lists "daily, weekly, monthly, and annual prices for retail gasoline and diesel fuel." Public-domain status is standard for US-gov works (EIA copyright page previously verified in main research). The specific route string `petroleum/pri/gnd` was not re-executed in this pass — minor residual uncertainty on the exact path only, not on the dataset's existence. |
| 4 | AFDC historical station downloads | **CONFIRMED** | Page live; documents exactly the two claimed products (single-day snapshots + date-range change history), free. Caveat: the page itself states **no license text**; the CC-BY-4.0 claim rests on the OEDI mirror (verified below), so treat the direct download as "US DOE open data, license implicit" and cite OEDI for the explicit CC-BY-4.0. |
| 5 | Overpass API (public instance) | **CONFIRMED** | OSM wiki page live (edited 2026-07-18); fair-use text matches verbatim: "<10,000 queries per day and <1 GB data per day," User-Agent recommended; software GNU AGPL v3; data is OSM → ODbL (wiki page implies rather than states the data license — standard OSM fact). Note some alternative public instances have different policies (some no-limit, some keyed/paid). |
| 6 | AFDC Alternative Fuel Corridors | **CONFIRMED** | afdc.energy.gov/corridors live; offers CSV/GeoJSON/shapefile downloads of stations meeting FHWA Round 8 corridor criteria, backed by developer.nlr.gov API endpoints; no fees. |

**Cross-check:** OEDI submission 106 verified live and explicitly **CC-BY-4.0** — supports the license claims for the AFDC data family.

**Overall:** all six claims survive adversarial verification, including the highest-risk claim (the nrel→nlr domain migration), which was independently reproduced via DNS failure + live retirement notice. Two soft edges worth remembering, neither blocking: (a) AFDC's own pages don't print a license — the explicit CC-BY-4.0 comes only from the OEDI mirror, so attribution should cite NREL/AFDC + OEDI; (b) EIA's exact API route `petroleum/pri/gnd` and its numeric rate limits weren't re-executed here (dataset existence and free access are confirmed). The category's honest gaps (no station-level prices, sparse DEF) are correctly declared, not papered over.
