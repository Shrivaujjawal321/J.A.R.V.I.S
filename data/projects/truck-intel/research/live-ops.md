# Live Operational Intelligence — Free & Legal Source Inventory
**Category:** Road closures · Construction / work zones · Weather · Floods · Traffic
**Project:** US Truck Intelligence Platform
**Researched:** 2026-07-22 (all URLs verified live via web search/fetch on this date unless marked UNCERTAIN)
**Constraint honored:** Zero paid/commercial API keys. Official government, open-licensed, or explicitly-permitted sources only.

---

## How to read this document

- **OFFICIAL** = US government (federal/state/local) source. Public domain or public-use data.
- **OPEN** = open-licensed non-government org (e.g., AWS Open Data Program hosting NOAA data).
- **COMMUNITY** = crowd-sourced (e.g., OSM). *No community source made the cut for this category — live ops data must be authoritative.*
- **UNCERTAIN** = I could not verify this detail today; treat as unconfirmed, do not build on it without checking.

Every source lists: owner, URL, coverage, update frequency, quality, license, access method, auth, cost, pros, cons.

---

## TL;DR — What the platform should actually build on

| # | Source | What it gives you | Auth | Verified |
|---|--------|-------------------|------|----------|
| 1 | NWS `api.weather.gov` | All US weather alerts + forecasts, GeoJSON, no key | User-Agent header only | YES |
| 2 | WZDx Feed Registry (USDOT) | ~38 registered machine-readable work-zone feeds, one schema | ~25 open, ~13 need free keys | YES |
| 3 | State 511 developer APIs (15+ states) | Incidents, closures, roadwork, winter conditions | Free registration per state | YES |
| 4 | Caltrans CWWP2 | CA lane closures, chain controls, CMS, RWIS — no key at all | None | YES |
| 5 | NOAA NWPS API `api.water.noaa.gov` | River gauges, flood stage, flood forecasts | None | YES |
| 6 | USGS Water Services (IV) | 10,000+ real-time stream gauges, 15-min data | None | YES |
| 7 | nowCOAST + NWS ArcGIS services | Radar (MRMS), hazards, river gauges as map services | None | YES |
| 8 | OpenFEMA API | Disaster declarations, IPAWS alert archive | None | YES |

**The one honest hole:** free real-time *nationwide congestion/speed* data does not exist. See §6.

---

## 1. Work Zones & Construction

### 1.1 FHWA/USDOT Work Zone Data Exchange (WZDx) Feed Registry — OFFICIAL

| Field | Detail |
|---|---|
| Owner | US DOT / FHWA (ITS DataHub, ITS JPO) |
| Official URL | https://data.transportation.gov/Roadways-and-Bridges/Work-Zone-Data-Feed-Registry/69qe-yiui |
| CSV export (machine-readable registry) | https://data.transportation.gov/api/views/69qe-yiui/rows.csv?accessType=DOWNLOAD |
| Spec (GitHub) | https://github.com/usdot-jpo-ode/wzdx |
| Coverage | ~38 registered feeds (verified 2026-07-22 by reading the CSV): OK, IL Tollway, MN, CA (MTC), WA, OR, PA Turnpike, NY, FL, MI, TX, NPS, KY, KS, CO, MO, OH, MD, UT, DE, MA, NC, HI, Austin TX, IN, NM, WI, IA, VA, LA, ID, IL, Maricopa County AZ, NJIT, + Quebec City. Mix of active/inactive — test each feed before relying on it. |
| Update frequency | Feeds are near-real-time (typically minutes); registry metadata updated as agencies register |
| Data quality | Varies by state. WZDx is a harmonized GeoJSON schema (location, lanes affected, start/end, verification status), which is exactly what routing needs. Some feeds are stale/inactive — the registry does not guarantee liveness. |
| License | US Government work / public domain (registry); individual feeds are state open data |
| Access method | CSV/Socrata API for the registry itself; each feed is a GeoJSON (or JSON) HTTP endpoint |
| Auth | ~25 feeds open, ~13 require a (free) API key from the publishing agency (e.g., IL Tollway, Oregon, PA Turnpike, TX, CO, OH, MA, VA, MI) |
| Cost | Free |
| Advantages | ONE schema for work zones across dozens of agencies — the single highest-leverage construction source in the US. Example verified live feeds: `https://wzdx.wsdot.wa.gov/api/v4/WorkZoneFeed` (WA, open), `https://mn.carsprogram.org/carsapi_v1/api/wzdx` (MN, open), `https://ks.carsprogram.org/carsapi_v1/api/wzdx` (KS, open), `https://az511.com/api/wzdx` (AZ). |
| Limitations | Not all 50 states publish; some registered feeds are dead; detail depth varies (some only planned events, not live lane status). You must build a per-feed health monitor. |

### 1.2 State DOT ArcGIS open-data portals (construction/closure layers) — OFFICIAL

Many DOTs publish live event layers on ArcGIS Hub with no key. Verified examples:

| State | Portal / layer | Access | Auth |
|---|---|---|---|
| Iowa | https://data.iowadot.gov/ — "511 Traveler Information Events" feature layer, updated every 10 min | ArcGIS REST (GeoJSON/JSON query) | None |
| Texas | https://gis-txdot.opendata.arcgis.com/ | ArcGIS REST | None |
| Florida | https://gis-fdot.opendata.arcgis.com/ | ArcGIS REST | None |
| North Carolina | NCDOT statewide incidents API: `https://eapps.ncdot.gov/services/traffic-prod/v1/incidents` + TIMS web services https://tims.ncdot.gov/tims/V2/webservices | REST/JSON | Key for DriveNC developer API; some endpoints open |

- **License:** state open data / public records.
- **Advantage:** ArcGIS REST is uniform — one client library covers every state that uses it.
- **Limitation:** you must discover and QA each state's layer individually; schemas differ (unlike WZDx).

---

## 2. Road Closures & Incidents — State 511 / DOT APIs

**The big finding:** at least 9 states run their 511 on the **same vendor platform** (IBI Group / Castle Rock "one511"), so they share an identical API shape: register free account → request key → REST at `/developers/doc`, JSON/XML, throttled at **10 calls / 60 seconds**. One integration ≈ nine states.

### 2.1 The shared-platform family (identical API pattern) — OFFICIAL, all verified

| State | Developer portal (verified) | Data available |
|---|---|---|
| New York | https://511ny.org/developers/resources + `/developers/doc` | Events, alerts, roadwork, **traffic speeds**, cameras, message signs, winter road conditions, **truck parking** |
| Georgia | https://511ga.org/developers/doc | Events, alerts, cameras, message signs, rest areas, ports of entry, express lanes, EV chargers |
| Wisconsin | https://511wi.gov/developers/help | **Traffic speeds**, incidents, roadwork, cameras |
| Louisiana | https://www.511la.org/developers/doc | Events, cameras, signs (same pattern) |
| Arizona | https://az511.gov/developers/doc | Cameras, weather stations, message boards, events, alerts, rest areas + open WZDx at `https://az511.com/api/wzdx` |
| Idaho | https://511.idaho.gov/developers/doc | Events, cameras, message signs, etc. |
| Nevada | https://www.nvroads.com/developers/doc | Events, cameras, etc. |
| Utah | https://prod-ut.ibi511.com/developers/doc (UDOT Traffic) | Road conditions, cameras, weather stations, signs, rest areas, mountain passes, events, alerts, **snow plows** |
| North Carolina | https://www.drivenc.gov/developers/doc | Incidents, closures + historical TIMS archive to 2011 |

- **Auth:** free account + API key. **Cost:** $0. **Rate limit:** 10 calls/60s per key (design your poller for 1 call/state/2-5 min — plenty).
- **Terms:** each has a Developer Access Agreement (e.g., https://511ny.org/developers/daa) — you describe your app, agree to attribution/usage terms. Read each one; NY's requires describing intended use.
- **Quality:** authoritative (state TMC-entered events), typically 1-5 min freshness.
- **Limitation:** per-key throttle means you need one key per state; event schemas are similar but not byte-identical across states.

### 2.2 States with their own (still free) systems — OFFICIAL, all verified

| State | System | URL | Access | Auth | Notes |
|---|---|---|---|---|---|
| Ohio | OHGO Public API | https://publicapi.ohgo.com/ (docs: `/docs/v1/construction`, `/docs/api-key`) | REST JSON | Free key | Explicitly public domain. Construction, incidents, **travel delays**, cameras, digital signs |
| Washington | WSDOT Traveler Information API | https://wsdot.wa.gov/traffic/api/ | REST JSON/XML | Free instant key (enter email, key displayed immediately) | Highway alerts, **travel times**, mountain passes, weather stations, ferries |
| Oregon | TripCheck TIS Data API | https://apiportal.odot.state.or.us/product/tripcheck-data-api (guide: https://www.tripcheck.com/pdfs/TripCheckAPI_Getting_Started_GuideV5.pdf) | REST XML/JSON | Free portal signup + subscription key | Incidents, cameras, DMS, RWIS road-weather stations |
| California | Caltrans CWWP2 | https://cwwp2.dot.ca.gov/ (e.g., LCS docs: `/documentation/lcs/lcs.htm`, chain control: `/documentation/cc/cc.htm`) | Bulk HTTPS files — JSON/XML/CSV/TXT | **None** | Lane Closure System, **chain controls** (critical for trucks), CMS, CCTV, RWIS. Explicitly "no charge". Simplest source in the whole inventory |
| Pennsylvania | PennDOT RCRS_Event_Data | https://www.pa.gov/agencies/penndot/programs-and-doing-business/online-services/developer-resources-documentation-api + request form at https://pa.gov/en/services/penndot/request-access-to-transportation-related-data-feeds.html | Web API, JSON | Free — submit Data Feed Request Form, receive HTTP Basic credentials | `plannedEvents`, `winterConditions` methods; statewide incidents + winter conditions |
| Virginia | VDOT SmarterRoads | https://smarterroads.vdot.virginia.gov/ | Portal downloads/feeds (22+ datasets) | Free account + usage agreement | Incidents, lane closures, travel advisories, **truck restrictions**, sensors, sign messages, paving schedules |
| Colorado | COtrip / CDOT data feed | https://maps.cotrip.org/help/117/Traveler-Information-Data-Feed-Access ; API at https://manage-api.cotrip.org/ | XML/API | Free username/password from CDOT | Incidents, road conditions, **speeds**, travel times, weather stations |
| Iowa | 511 data feeds + open data | https://iowadot.gov/travel-tools/iowa-511/511-data-feeds + https://data.iowadot.gov/ | RESTful XML + ArcGIS REST | **None** | Events layer refreshed every 10 min; camera + DMS feeds |
| Minnesota / Kansas | CARS program WZDx + 511 | `https://mn.carsprogram.org/carsapi_v1/api/wzdx`, `https://ks.carsprogram.org/carsapi_v1/api/wzdx` | GeoJSON | **None** | Open WZDx endpoints verified in USDOT registry |
| Texas | DriveTexas | https://drivetexas.org/ (FAQ: `/faq`; conditions pages: http://conditions.drivetexas.org/current/) | API exists (built post-Harvey); conditions pages public | **UNCERTAIN** — public developer signup not confirmed; API historically for partner agencies | Statewide TxDOT-verified conditions, 5-min refresh. Fallback: TxDOT ArcGIS open data + TX WZDx feed (key required) |
| Florida | FL511 third-party data feed | https://fl511.com/ ; FDOT DIVAS data-integration system | Data feed exists; WZDx feed in registry uses `app_key` | **UNCERTAIN** — public self-serve developer registration not confirmed; feed access appears to be "authorized third parties" via FDOT | Fallback: FDOT ArcGIS open data hub + FL WZDx registry feed |
| New England (ME/NH/VT) | newengland511.org | https://newengland511.org/ | Website only | **No public developer API found** (dev doc URL 404s) | Gap state-cluster; contact MaineDOT/NHDOT/VTrans directly. They ingest Waze for Cities internally |

**Count of states with verified, free, self-serve or form-based API access:** NY, GA, WI, LA, AZ, ID, NV, UT, NC, OH, WA, OR, CA, PA, VA, CO, IA, MN, KS = **19 states** — comfortably beyond the 10 asked for. Remaining states mostly have *something* (ArcGIS layers or WZDx feeds) discoverable via https://catalog.data.gov/ (search "511" / "traffic events" / state DOT name).

---

## 3. Weather (alerts, forecasts, radar)

### 3.1 NWS API — `api.weather.gov` — OFFICIAL — **the backbone weather source**

| Field | Detail |
|---|---|
| Owner | NOAA / National Weather Service |
| Official URL | https://api.weather.gov (docs: https://www.weather.gov/documentation/services-web-api ; OpenAPI spec: https://api.weather.gov/openapi.json ; community FAQ: https://weather-gov.github.io/api/general-faqs) |
| Coverage | Entire US + territories |
| Update frequency | Alerts: real-time (seconds-to-minutes). Forecasts: hourly/6-hourly cycles. Observations: ~hourly per station |
| Data quality | Authoritative — this IS the national warning system. Alert polygons are precise GeoJSON |
| License | US Government work — public domain |
| Access method | REST API. Formats: GeoJSON (default), JSON-LD, CAP XML, ATOM |
| Key endpoints | `/alerts/active?area={ST}` (all active alerts by state) · `/alerts/active?point={lat},{lon}` · `/points/{lat},{lon}` → grid → `/gridpoints/{wfo}/{x},{y}/forecast` and `/forecast/hourly` · `/stations/{id}/observations` |
| Auth | **No API key.** A descriptive `User-Agent` header is required (e.g., `(truckintel.app, you@email)`). Docs say a key system may come "in the future" — design for a config header |
| Cost | Free |
| Advantages | One call gets every active winter storm / flood / wind / dense fog alert as polygons you can intersect with truck routes. No signup at all. |
| Limitations | Undisclosed rate limits ("reasonable"; brief 429s resolve in ~5s) — cache aggressively. Forecast grid API has occasional station/grid quirks. Not an SLA'd service. |

### 3.2 NOAA/NWS ArcGIS map services — OFFICIAL

| Field | Detail |
|---|---|
| Owner | NOAA / NWS |
| URLs (verified) | https://mapservices.weather.noaa.gov (e.g., event-driven river gauges: `.../eventdriven/rest/services/water/riv_gauges/MapServer`) · nowCOAST: https://nowcoast.noaa.gov/arcgis/rest/services (e.g., `nowcoast/radar_meteo_imagery_nexrad_time/MapServer`) |
| Coverage | CONUS + AK/HI/PR/Guam |
| Update frequency | Radar mosaics ~every few minutes (time-enabled); gauges event-driven |
| Quality | MRMS quality-corrected 1-km radar mosaic; 60+ services on nowCOAST |
| License | Public domain |
| Access method | ArcGIS REST MapServer/query + OGC WMS 1.3.0 (time-enabled) |
| Auth / Cost | None / Free |
| Advantages | Drop-in map overlays (radar, warnings, river flood status) with zero processing — ideal for a solo dev's map UI |
| Limitations | Imagery services are for display, not analytics; nowCOAST is labeled a prototype — don't make it a single point of failure |

### 3.3 NEXRAD + MRMS raw radar on AWS Open Data — OPEN (NOAA data, AWS-hosted)

| Field | Detail |
|---|---|
| Owner | NOAA (NODD program); hosting: AWS Open Data Registry |
| URLs | https://registry.opendata.aws/noaa-nexrad/ · https://registry.opendata.aws/noaa-mrms-pds/ |
| Coverage | US radar network; MRMS CONUS grid, ~2-min real-time cycle |
| License | "Open to the public and can be used as desired" (NOAA); no restrictions |
| Access | S3 buckets, anonymous (`--no-sign-request`). NOTE: NEXRAD Level II archive moved to `unidata-nexrad-level2` bucket (old `noaa-nexrad-level2` retired Sept 1, 2025) |
| Cost | Free |
| Advantage / Limitation | Full raw radar if you ever need custom processing / — overkill for v1; use nowCOAST tiles instead. Listed for completeness. |

**Skip-for-v1 but real:** NDFD gridded forecasts and HRRR model output are also free on AWS/NOAA — only needed if you build custom route-weather forecasting later.

---

## 4. Floods & Water

### 4.1 NOAA National Water Prediction Service (NWPS) API — OFFICIAL

| Field | Detail |
|---|---|
| Owner | NOAA / NWS Office of Water Prediction (replaced legacy AHPS) |
| URLs | About: https://water.noaa.gov/about/api · Docs (OpenAPI): https://api.water.noaa.gov/nwps/v1/docs/ |
| Coverage | US river forecast locations (thousands of gauges) |
| Update frequency | Observations near-real-time; forecasts on RFC cycles (several times daily) |
| Quality | Authoritative flood-stage data: observed + **forecast** stage/flow, flood category thresholds (minor/moderate/major), crest history, flood impacts text |
| License | Public domain |
| Access method | REST JSON: `/v1/gauges`, `/v1/gauges/{id}`, `/v1/gauges/{id}/stageflow` |
| Auth / Cost | None / Free |
| Advantages | The only free source of *forecast* river flooding — lets you warn "this route's river crossing hits major flood stage in 18h" |
| Limitations | Explicitly "not supported 24/7, may change without notice" — build a health check + cache |

### 4.2 USGS Water Services — Instantaneous Values — OFFICIAL

| Field | Detail |
|---|---|
| Owner | US Geological Survey |
| URLs | https://waterservices.usgs.gov/docs/instantaneous-values/ (service root: `https://waterservices.usgs.gov/nwis/iv/`) |
| Coverage | 10,000+ real-time gauges nationwide |
| Update frequency | Sensors read every 15 min, transmitted ~hourly |
| Quality | Gold-standard observed streamflow/gage height; provisional until reviewed |
| License | Public domain |
| Access method | REST — JSON (WaterML), XML, RDB. Multi-site per request. Historical to Oct 2007 |
| Auth / Cost | None / Free |
| Advantages | Dense observed data to corroborate NWPS forecasts; automated retrieval explicitly supported |
| Limitations | Observations only (no forecast — that's NWPS's job). USGS is mid-migration to modernized APIs (`api.waterdata.usgs.gov`) — watch their Water Data blog for deprecation notices |

### 4.3 OpenFEMA API — OFFICIAL

| Field | Detail |
|---|---|
| Owner | FEMA |
| URLs | https://www.fema.gov/about/openfema/api · example: `https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries` |
| Coverage | Nationwide, 1953-present |
| Update frequency | Declarations updated as issued (daily-ish); not a second-by-second feed |
| Quality | Authoritative federal disaster context |
| License | Public domain; explicitly "free and does not require a subscription or API key" |
| Access method | REST JSON/CSV with OData-style filters; 1,000 records/page |
| Auth / Cost | None / Free |
| Advantages | "County X is under a major disaster declaration" context banner for routes; IPAWS archived alerts dataset for historical analysis |
| Limitations | Not real-time operational routing data — it's situational context. Live *warnings* come from NWS CAP alerts (§3.1), not FEMA |

**Related-but-static:** FEMA National Flood Hazard Layer (flood *zones*) belongs to the static/hazard-mapping category, not live ops — noted here only to avoid double-research.

---

## 5. Winter / Road-Weather Conditions — OFFICIAL

Not a separate national system — it rides on the sources above:

- **State 511 APIs** expose winter road conditions (NY, UT, PA `winterConditions`, CO road conditions, Iowa).
- **Caltrans chain controls** (`cwwp2.dot.ca.gov/documentation/cc/cc.htm`) — legally required chain status for CA mountain passes; truck-critical.
- **RWIS road-weather stations** (pavement temp, visibility, wind) are in WSDOT, TripCheck, UDOT, AZ511, COtrip APIs.
- **NWS alerts** carry winter storm warnings as polygons.

No extra integration needed — just map these fields from feeds you already pull.

---

## 6. Traffic Congestion — THE HONEST ASSESSMENT

**Question asked:** is real-time nationwide traffic congestion possible without paid APIs?

**Answer: NO — and anyone who tells you otherwise is selling something.** Here is the precise breakdown:

### What is NOT available free (verified)

| Source | Why not |
|---|---|
| Google / HERE / TomTom / INRIX / Mapbox traffic | Commercial API keys — excluded by project constraint (freemium tiers are still commercial keys + restrictive ToS) |
| FHWA NPMRDS (national probe speeds) | Free **only for DOTs/MPOs** for federal performance reporting — not for private platforms (https://data.transportationops.org/national-performance-management-research-data-set-npmrds) |
| RITIS | Agency account required (https://ritis.org/tools) |
| Waze for Cities | Free **for government partners only**; the feed license prohibits general public republishing — not available to a private platform |
| Scraping Google/Waze traffic layers | Violates ToS — excluded on legality, full stop |

### What IS genuinely possible free

1. **Nationwide event-based "congestion proxy"** — incidents, closures, work zones from the 19+ state feeds in §2 + WZDx. This is what state 511 maps themselves show. Covers the causes of most truck delays (crashes, closures, weather) without probe speeds.
2. **Real sensor speeds/travel times in ~8-10 states** — free, from the states that publish their own detector data: 511NY traffic speeds, 511WI speeds, WSDOT travel times, OHGO travel delays, COtrip speeds/travel times, and Caltrans PeMS (free registration, CA-only — UNCERTAIN whether current PeMS signup is still self-serve; verify at time of build).
3. **Historical/typical congestion patterns** — public FHWA/BTS datasets can give "this corridor is slow at 5pm" heuristics, not live data.

**Recommendation:** ship "live incidents + closures + work zones + weather" as the congestion story, label it honestly in the UI ("event-based, not probe-speed"), add per-state sensor speeds where free, and list nationwide probe speeds as a future paid upgrade (INRIX/TomTom/HERE).

---

## 7. Discovery / catalog layer

- **data.gov CKAN catalog** — https://catalog.data.gov/ — search per state for anything this doc missed (e.g., the WZDx registry itself is mirrored at https://catalog.data.gov/dataset/work-zone-data-exchange-wzdx-feed-registry). OFFICIAL, free, no auth.
- **State ArcGIS Hub portals** — nearly every DOT has one (`data.iowadot.gov`, `gis-txdot.opendata.arcgis.com`, `gis-fdot.opendata.arcgis.com`, `virginiaroads.org`); uniform ArcGIS REST access.

---

## 8. Recommended architecture for a solo dev (simplicity-first)

1. **One poller, three cadences:** NWS alerts every 2 min (one call per state or one national call); 511/WZDx feeds every 5 min; NWPS/USGS water every 15-30 min.
2. **Normalize everything to one internal event schema** (WZDx's schema is a good template: geometry + type + severity + start/end + source + fetched_at).
3. **Per-feed health table** — feeds die silently (registry has inactive entries); alert yourself when a feed goes stale >30 min.
4. **Respect the throttles:** 10 calls/60s per 511 key is generous for polling; cache NWS responses; send a proper User-Agent everywhere; keep a copy of each Developer Access Agreement you sign.
5. **Attribution page** listing every state DOT + NOAA + USGS + FEMA — cheap goodwill and required by several DAAs.

---

## 9. Honest gaps (no free/legal source exists)

1. **Real-time nationwide probe-based congestion/speeds** — paid only (INRIX / HERE / TomTom / Google). NPMRDS & RITIS are agency-restricted; Waze is partner-restricted.
2. **Predictive traffic ("ETA in 2 hours")** — no free source; requires commercial probe data or your own ML on top of it.
3. **A single unified national road-closure feed** — does not exist at any price; even paid providers aggregate. You must integrate ~19 state APIs + WZDx and accept coverage holes.
4. **Full 50-state coverage of live closures** — a handful of states (e.g., New England 511 cluster ME/NH/VT; FL/TX self-serve access UNCERTAIN) have no confirmed public developer path; fallback is their ArcGIS layers or contacting the DOT for feed credentials (often granted free, but it's a manual ask).
5. **Segment-level commercial road-weather forecasts** (pavement forecast per route mile) — vendors only; free path is NWS grid forecasts + RWIS stations, which is coarser.
6. **Crowd-sourced hazard reports (Waze-style)** — no legal free equivalent for a private platform.

---

*Every URL above was confirmed reachable/real on 2026-07-22 via live search or fetch, except rows explicitly marked UNCERTAIN. Sources: data.transportation.gov, weather.gov, water.noaa.gov, waterservices.usgs.gov, fema.gov, nowcoast.noaa.gov, registry.opendata.aws, and the individual state DOT/511 portals linked inline.*

---

## Verification (adversarial pass)

**Verified:** 2026-07-22, independent adversarial check. Method: WebFetch of each claimed doc URL **plus live HTTP calls to the actual API endpoints** (curl with descriptive User-Agent). Goal was to refute each claim; statuses below reflect what actually happened on the wire today.

| # | Source | Status | Evidence |
|---|--------|--------|----------|
| 1 | NWS API (api.weather.gov) | **CONFIRMED** | Docs page live and matches claim verbatim: no key, User-Agent required, GeoJSON/CAP/JSON-LD, `/alerts/active` `/points` `/gridpoints` `/stations` all documented; docs state data is "open data, free to use for any purpose"; rate limits undisclosed but generous. Live call `GET /alerts/active?area=CA` returned a GeoJSON FeatureCollection. |
| 2 | WZDx Feed Registry | **CONFIRMED** | Socrata HTML page returned only site chrome to the fetcher, but the machine-readable CSV export (`/api/views/69qe-yiui/rows.csv`) downloaded fine: **40 feed rows + header (~claimed "~38")**, with `needAPIKey` column confirming the open-vs-key split. Live sample feed `wzdx.wsdot.wa.gov/api/v4/WorkZoneFeed` returned WZDx v4.2 GeoJSON with no key. Caveat confirmed too: `mn.carsprogram.org/carsapi_v1/api/wzdx` **timed out (30s)** today — the "per-feed health monitor is required" warning is not theoretical. Also note: OK's registry entry embeds a public `access_token` in the URL; treat embedded tokens as agency-published, do not redistribute as your own. |
| 3 | State 511 developer API family | **CONFIRMED (with caveats)** | 511NY developer page live: free account + Developer Access Request Form + NYSDOT Developers Access Agreement + emailed API key, explicitly "a free service" open to commercial vendors and the public. Shared-platform siblings spot-checked: `511ga.org/developers/doc`, `nvroads.com/developers/doc`, `az511.gov/developers/doc` all HTTP 200. Caveats: (a) the 10 calls/60s throttle was NOT visible on the public page (it sits behind login/docs — plausible but unverified today); (b) 511NY's primary event feed is described as **XML**, not JSON, on the public page; (c) full 19-state count not re-verified one-by-one — 12 of 19 confirmed live in this pass, remainder carried from original research. |
| 4 | Caltrans CWWP2 | **CONFIRMED** | Portal live, confirms JSON/XML/CSV/TXT for lane closures, chain controls, CMS, RWIS. Live proof: `GET /data/d3/cc/ccStatusD03.json` returned current chain-control status (Luther Pass record timestamped today) with **zero auth**. The exact phrase "explicitly no charge" wasn't on the fetched page, but no-key access is demonstrated on the wire — the operative claim holds. |
| 5 | NOAA NWPS API | **CONFIRMED** | Docs URL serves a live Swagger UI. Live calls: `GET /nwps/v1/gauges/ptvn6` returned full gauge metadata; `GET .../stageflow` returned observed stage/flow series — no auth, no key. Forecast series and flood categories are part of the same schema per the API's own service description on mapservices. Keep the doc's own warning: not an SLA'd 24/7 service. |
| 6 | USGS Water Services (IV) | **CONFIRMED** | Docs landing page live. Live call `GET /nwis/iv/?format=json&sites=01646500` returned WaterML-JSON instantly, no auth. "Automated retrieval explicitly supported" wording not re-found on the landing page (it's in the deeper service docs), but automated access demonstrably works and USGS data is public domain. Migration-to-`api.waterdata.usgs.gov` caveat stands. |
| 7 | nowCOAST + NWS ArcGIS services | **BROKEN (as cited) — replacement verified** | The claimed URL `nowcoast.noaa.gov/arcgis/rest/services` is **dead**: server returns 403 with an explicit notice that as of **2023-04-19 nowCOAST no longer accepts `arcgis` requests** (service change SCN23-12). The category itself survives via two verified-today endpoints: (a) `mapservices.weather.noaa.gov/eventdriven/rest/services` — live ArcGIS 11.3 REST, folders `radar`, `water`, `WWA`, including `water/riv_gauges/MapServer`; (b) new nowCOAST **WMS** at `nowcoast.noaa.gov/geoserver/ows?service=wms&request=GetCapabilities` — returned WMS 1.3.0 capabilities. **Action: replace the arcgis URL in §3.2 usage; do not build against it.** |
| 8 | OpenFEMA API | **CONFIRMED** | Docs page 403'd to the generic fetcher (bot filter on fema.gov HTML), but the API itself is the claim — live call `GET /api/open/v2/DisasterDeclarationsSummaries?$top=1` returned JSON with OData-style metadata (`$top` honored), no key, no auth. Free/no-subscription claim consistent with FEMA's published OpenFEMA terms. |

### Overall assessment

7 of 8 sources survive adversarial verification with live on-the-wire proof, not just doc-page reads; the inventory is sound and honestly caveated (the stale-feed warning on WZDx proved itself when the MN feed timed out during this very pass). The one real defect is #7: the nowCOAST ArcGIS REST URL has been dead since April 2023 and any code pointed at it will 403 — the fix is mechanical (use `mapservices.weather.noaa.gov` for ArcGIS REST and nowCOAST's geoserver WMS for radar tiles), and both replacements were verified live today. Minor residual uncertainties that don't block building: the 10 calls/60s 511 throttle figure sits behind registration and was not independently re-verified; the 19-state 511 count was spot-checked (12/19 live-confirmed), not exhaustively re-walked; and 511NY's public page advertises XML rather than JSON for its main feed. Nothing in this pass found a licensing or ToS problem — every confirmed source is US-government public-domain or state open data with free registration at most, and automated access worked without evasion on all of them.
