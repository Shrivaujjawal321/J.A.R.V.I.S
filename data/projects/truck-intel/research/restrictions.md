# Road Restrictions — Free & Legal Source Inventory
**Category:** Weight/height limits, truck bans, seasonal (spring-thaw) restrictions, hazmat routes, construction restrictions
**Project:** US Truck Intelligence Platform
**Researched:** 2026-07-22 (all URLs checked via live web search/fetch on this date)
**Hard rule honored:** Only official government data, open data, and community data with explicit legal access. No paid APIs. Where no free source exists, the gap is stated honestly.

**Labels used:** `OFFICIAL` = government · `OPEN` = open-licensed org · `COMMUNITY` = e.g. OpenStreetMap
**"UNCERTAIN"** = could not verify today; do not treat as fact.

---

## 0. Executive summary (read this first)

There is **no single free national dataset** of truck restrictions. The free landscape is:

| Layer | Best free source | Reality check |
|---|---|---|
| Bridge low clearances (national) | FHWA National Bridge Inventory (NBI) | Best national proxy; FHWA itself says "not for route clearance" — use as advisory layer |
| Construction/work-zone restrictions | WZDx Feed Registry (~40+ GeoJSON feeds) | Verified live; the single best federal aggregation in this whole category |
| State restriction data | Per-state DOT GIS + 511 APIs (15+ states verified below) | Quality and format vary wildly state to state |
| Seasonal spring-thaw limits | MN/WI/ND publish data; MI publishes HTML bulletins | Machine-readable only in some states |
| Hazmat routes | FMCSA NHMRR registry (list) | Current registry is HTML/PDF, **not GIS**; GIS versions are stale (2012 vintage) |
| Physical restrictions crowd layer | OSM `maxheight`/`maxweight`/`hgv` tags | US coverage incomplete — supplement, never sole source |
| Harmonized 50-state legal truck network | **DOES NOT EXIST FREE** | This is the paid gap (HERE, TomTom, Trimble PC*Miler, ProMiles) |

---

## 1. Federal / national sources

### 1.1 FHWA National Bridge Inventory (NBI) — vertical clearance + load posting
| Field | Value |
|---|---|
| Label | OFFICIAL |
| Owner | Federal Highway Administration (US DOT) |
| URL | https://www.fhwa.dot.gov/bridge/nbi/ascii.cfm (verified via search 2026-07-22) |
| Coverage | All 50 states + territories, ~620k bridges |
| Update frequency | Annual releases (states submit under National Bridge Inspection Standards; bridges inspected ~every 24 months) |
| Data quality | High completeness, but clearance values can lag reality by up to 2 years |
| License | US Government public domain |
| Access method | Bulk download — ASCII/CSV files per state + national file |
| Auth | None |
| Cost | Free |
| Key fields | Item 10 (min vertical clearance over route), Item 53 (min vertical clearance over deck), Item 54 (underclearance ref), load posting/operating rating items |
| Advantages | Only free NATIONAL low-clearance + load-posted-bridge dataset; stable schema; decades of history |
| Limitations | **FHWA explicitly warns it must not be used as sole source for route clearance decisions.** Point data (bridge), not road-segment restrictions. Annual snapshot, not real-time. |

Also useful: NBI data dictionary (community mirror): https://nationalbridges.com/nbiDesc.html

### 1.2 Work Zone Data Exchange (WZDx) Feed Registry — construction restrictions
| Field | Value |
|---|---|
| Label | OFFICIAL |
| Owner | US DOT ITS JPO / FHWA |
| URL | https://data.transportation.gov/Roadways-and-Bridges/Work-Zone-Data-Exchange-WZDx-Feed-Registry/69qe-yiui — machine endpoint **verified live 2026-07-22**: https://data.transportation.gov/resource/69qe-yiui.csv |
| Coverage | ~40+ active feeds: states (OK, CO, UT, TX, VA, PA Turnpike, IL Tollway, OH, CA 511, ...), counties, National Park Service |
| Update frequency | Registry: as feeds register. Individual feeds: 60 seconds to weekly (most 1–15 min) |
| Data quality | High for participating agencies — this is the harmonized federal spec (v4.x) navigation apps use |
| License | Registry: US public domain (Socrata, data.transportation.gov). Individual feeds: agency terms (most open) |
| Access method | Registry: Socrata API / CSV export. Feeds: GeoJSON over HTTPS (WZDx spec) |
| Auth | Registry: none. Feeds: ~1/3 need a **free** API key (CO, TX, VA, OH, NPS, CA 511, ...) |
| Cost | Free |
| Advantages | Standardized schema across agencies (work zone location, lane closures, restrictions); spec on GitHub (https://github.com/usdot-jpo-ode/wzdx); the easiest multi-state win in this whole category |
| Limitations | Not all 50 states participate; covers work zones only, not permanent restrictions |

### 1.3 FMCSA National Hazardous Materials Route Registry (NHMRR)
| Field | Value |
|---|---|
| Label | OFFICIAL |
| Owner | Federal Motor Carrier Safety Administration (US DOT) |
| URL | https://www.fmcsa.dot.gov/regulations/hazardous-materials/national-hazardous-materials-route-registry-state |
| Coverage | All designated + restricted hazmat routes, US-wide, listed by state |
| Update frequency | Roughly annual via Federal Register notice — **current as of Dec 2025** (https://www.federalregister.gov/documents/2025/12/08/2025-22192/national-hazardous-materials-route-registry) |
| Data quality | Authoritative legal registry (it IS the law), but route descriptions are text ("US-30 from X to Y"), not geometry |
| License | US Government public domain |
| Access method | HTML page / PDF list. **NOT GIS.** No API. |
| Auth | None for browser. Note: automated fetch of fmcsa.dot.gov returned **HTTP 403** in testing (bot protection) — plan manual download or respectful scraping per robots.txt |
| Cost | Free |
| Advantages | The only authoritative national hazmat route source; legally definitive |
| Limitations | **No current GIS version exists.** You must geocode/conflate text route descriptions onto a road network yourself. data.gov entry points to a 2009 PDF (https://catalog.data.gov/dataset/national-hm-route-registry-national-hm-route-registry — verified 2026-07-22) |

**Stale GIS versions (usable as a head start only):** FMCSA hazmat routes shapefile built on 2004 TIGER/Line (hazmat.shp + hmroutes.dbf + hmstcnty.dbf), circulated as NTAD 2006/2012 editions via ScienceBase (https://www.sciencebase.gov/catalog/item/4f4e4a1ae4b07f02db60699b) and university geodata libraries (Stanford/MIT/Berkeley mirrors). Label clearly as historic if used.

### 1.4 BTS National Transportation Atlas Database (NTAD) / geodata.bts.gov
| Field | Value |
|---|---|
| Label | OFFICIAL |
| Owner | Bureau of Transportation Statistics (US DOT) |
| URL | https://geodata.bts.gov/ (catalog); update notices at https://www.bts.gov/newsroom/bts-updates-datasets-national-transportation-atlas-database-spring-2025 |
| Coverage | National transportation layers (networks, facilities) |
| Update frequency | Dynamic publication cycle (rolling updates through the year) |
| Data quality | High for infrastructure layers |
| License | US Government public domain |
| Access method | ArcGIS Hub downloads: File Geodatabase, Shapefile, GeoJSON, CSV, KML; **WFS available** |
| Auth | None |
| Cost | Free |
| Advantages | One-stop federal geospatial catalog; good for base networks + weigh stations + intermodal layers |
| Limitations | The hazmat routes layer in the current NTAD cycle is **UNCERTAIN** — search only surfaced the stale 2004-TIGER-based version and a PHMSA "HazMat Regions" (administrative regions, not routes) layer. Do not assume current hazmat geometry lives here. |

### 1.5 data.gov catalog (index, not a source itself)
- URL: https://catalog.data.gov/ — HTML search works; the CKAN `package_search` API returned **404 in live testing 2026-07-22** (endpoint availability UNCERTAIN — treat API access as unreliable, use HTML/Socrata/Hub portals directly).
- Useful entries verified: NYC low bridges (https://catalog.data.gov/dataset/citywide-low-bridges), Iowa 511 (https://catalog.data.gov/dataset/iowa-511-c5c53), WZDx registry.

---

## 2. State DOT sources — verified concrete endpoints (12+ states)

### 2.1 Washington — WSDOT (model state for clearance data)
| Field | Value |
|---|---|
| Label | OFFICIAL |
| Owner | Washington State DOT |
| URL | https://data.wsdot.wa.gov/arcgis/rest/services/ — **fetched live 2026-07-22**, returns folders incl. `Bridge`, `Vertical_Clearance`, `WorkZone`, `TravelInformation` |
| Concrete layers | BridgeData: https://data.wsdot.wa.gov/arcgis/rest/services/Shared/BridgeData/FeatureServer (fields `MinVertClrncOverDeck`, `MinVertClrncUnderBridge`); Vertical Clearance trip-planner service: https://data.wsdot.wa.gov/arcgis/rest/services/Scratch/Vertical_Clearance/FeatureServer |
| Coverage | WA state routes |
| Update frequency | Maintained by Bridge Preservation Office (continuous); UNCERTAIN exact refresh cadence |
| Quality | High — powers WSDOT's own Bridge Vertical Clearance Trip Planner |
| License | Public records; WSDOT data generally free with attribution (confirm per-service disclaimer) |
| Access | ArcGIS REST (query as GeoJSON with `f=geojson`), no auth, free |
| Advantages | True no-key ArcGIS REST; segment+structure level clearance |
| Limitations | One state; "Scratch" folder naming suggests service reorganization risk — pin and monitor |

### 2.2 Pennsylvania — PennDOT (posted + bonded roads)
| Field | Value |
|---|---|
| Label | OFFICIAL |
| Owner | Pennsylvania DOT (PennShare) |
| URL | https://data-pennshare.opendata.arcgis.com/ · Posted Roads (posted weight limits): https://data-pennshare.opendata.arcgis.com/maps/PennShare::posted-roads-2/about · Bonded Roads: https://data-pennshare.opendata.arcgis.com/datasets/bonded-roads/data |
| Also via | PASDA mirror with REST/WMS/GeoJSON/KMZ: https://www.pasda.psu.edu/uci/DataSummary.aspx?dataset=47 |
| Coverage | PA state roads |
| Update frequency | UNCERTAIN exact cadence (portal datasets refreshed by PennDOT; check layer metadata) |
| Quality | High — this is the state's legal posted-weight-restriction inventory |
| License | Open data portal terms (free use w/ attribution; verify layer page) |
| Access | ArcGIS Hub: download Shapefile/GeoJSON/CSV + underlying FeatureServer REST |
| Auth / Cost | None / Free |
| Advantages | One of the few states publishing actual posted WEIGHT restrictions as GIS |
| Limitations | State-maintained roads only; local posted roads coverage partial |

### 2.3 Minnesota — MnDOT (seasonal load limits, the national reference for spring thaw)
| Field | Value |
|---|---|
| Label | OFFICIAL |
| Owner | Minnesota DOT |
| URL | Program hub: https://www.dot.state.mn.us/loadlimits/ · Interactive map (ArcGIS Experience): https://experience.arcgis.com/experience/83f37504c1d344f4bb2a05b355fc80f4 · Map downloads: https://www.dot.mn.gov/loadlimits/maps-pdf.html · SLR research portal: https://sll.dot.state.mn.us/research/seasonal_load_limits/ |
| Coverage | MN; 6 frost zones; 5-ton/7-ton restricted routes |
| Update frequency | Seasonal — zone start/end dates announced ≥3 days ahead; map updates during SLR season |
| Quality | High; MnDOT is the methodological leader (thaw-index based) |
| License | MN government data (public); Minnesota Geospatial Commons (https://gisdata.mn.gov/) for GIS layers |
| Access | HTML + PDF + ArcGIS Experience app; underlying FeatureServer of the Experience app: UNCERTAIN exact REST URL (inspect app config to extract it) |
| Auth / Cost | None / Free |
| Advantages | Best-documented seasonal program in the US; email/phone notification lists |
| Limitations | Data published for humans first; extracting machine-readable zone geometries needs the Commons or app-service spelunking |

### 2.4 North Dakota — NDDOT (live REST incl. load + width/height restrictions)
| Field | Value |
|---|---|
| Label | OFFICIAL |
| Owner | North Dakota DOT |
| URL | https://gis.dot.nd.gov/ArcGIS/rest/services/external/rcrs_dynamic/MapServer — **fetched live 2026-07-22** |
| Verified layers | Load Restrictions current/future/proposed (layers 13–18, 23–28), Width/Height Restrictions – Alerts (8) and – Work Zones (9), road conditions, cameras |
| Coverage | ND highways |
| Update frequency | Near-real-time (powers ND Roads 511 app) |
| Quality | High, operational data |
| License | **CAUTION: service terms state "solely for your own individual non-commercial and informational purposes"; systematic retrieval prohibited.** |
| Access | ArcGIS REST MapServer, no key |
| Cost | Free |
| Advantages | Exactly the restriction content we want, live |
| Limitations | **ToS blocks commercial platform use — you must request permission from NDDOT before building on it.** Honest status: legally unusable as-is for a commercial product. |
| Program page | https://www.dot.nd.gov/driver/commercial/north-dakota-load-restrictions |

### 2.5 Texas — TxDOT (load-zoned roads + load-restricted bridges)
| Field | Value |
|---|---|
| Label | OFFICIAL |
| Owner | Texas DOT |
| URL | Load Restricted Bridge Map: https://apps3.txdot.gov/apps/gis/lrbm/ · Load Zone map: https://apps3.txdot.gov/apps/gis/loadzone/ · Open data portal: https://gis-txdot.opendata.arcgis.com/ · Load zoning program: https://www.txdot.gov/data-maps/load-zoning.html |
| Coverage | TX |
| Update frequency | "May change periodically" per TxDOT; roadway inventory annually |
| Quality | High (engineering-analysis-backed load zones) |
| License | TxDOT open data terms (free w/ attribution) |
| Access | Web apps (ArcGIS JS — underlying REST endpoints discoverable via network tab; exact service URLs UNCERTAIN) + open data portal downloads (Shapefile/GeoJSON) |
| Auth / Cost | None / Free |
| Advantages | Big state, real restriction inventory, WZDx feed too (needs free key) |
| Limitations | Restriction layers are surfaced via apps; bulk restriction layer on the open-data portal not confirmed today |

### 2.6 Ohio — ODOT OHGO Public API
| Field | Value |
|---|---|
| Label | OFFICIAL |
| Owner | Ohio DOT |
| URL | https://publicapi.ohgo.com/ (docs + registration) · ToU: https://publicapi.ohgo.com/docs/terms-of-use |
| Coverage | OH |
| Update frequency | Real-time |
| Data offered | Incidents, work zones, road conditions, RWIS, DMS, cameras, **truck parking** |
| Quality | High, operational |
| License | ODOT states the data is **public domain**; free service with anti-abuse stipulations |
| Access | REST API, JSON |
| Auth | Free API key required |
| Cost | Free |
| Advantages | Explicit public-domain stance; clean modern API |
| Limitations | No permanent weight/height restriction layer in the API (work zones + conditions focus) |

### 2.7 Iowa — Iowa DOT open data + 511
| Field | Value |
|---|---|
| Label | OFFICIAL |
| Owner | Iowa DOT |
| URL | https://data.iowadot.gov/ · 511 feature layer: https://data.iowadot.gov/datasets/IowaDOT::iowa-dot-traveler-information-511/about · Public map: https://www.511ia.org/ |
| Coverage | IA |
| Update frequency | 511 feature layer refreshed **every 10 minutes** |
| Quality | High; includes commercial-vehicle restrictions/closures in event data |
| License | Iowa DOT open data terms (free) |
| Access | ArcGIS Hub / FeatureServer REST; also listed on data.gov |
| Auth / Cost | None for the hub layer / Free |
| Advantages | 511 events as a no-key ArcGIS layer — rare and convenient |
| Limitations | Event-based (closures/restrictions as events), not a static restriction inventory |

### 2.8 Idaho — ITD 511 API (has a literal "Restrictions" endpoint)
| Field | Value |
|---|---|
| Label | OFFICIAL |
| Owner | Idaho Transportation Department |
| URL | https://511.idaho.gov/developers/doc — **fetched live 2026-07-22** |
| Data | **Restrictions (weight limits)**, road conditions, weigh stations, runaway truck ramps, rest areas, mountain passes, events + WZDx feed at https://511.idaho.gov/api/wzdx |
| Update frequency | Real-time |
| License | Developer terms on signup (free use) |
| Access | REST API (JSON/XML) |
| Auth | Free developer key; **throttle: 10 calls / 60 s** |
| Cost | Free |
| Advantages | Purpose-built restrictions endpoint + trucker POI layers |
| Limitations | Rate limit forces caching; ID only |

### 2.9 New York — 511NY API + NYC open data
| Field | Value |
|---|---|
| Label | OFFICIAL |
| Owner | NYSDOT (state) · NYC DOT (city) |
| URLs | State API docs: https://511ny.org/developers/doc · Access agreement: https://511ny.org/developers/daa · Events endpoint: https://511ny.org/developers/help/api/get-api-getevents_key_format · Historical events: https://data.ny.gov/Transportation/511-NY-Events-Beginning-2010/ah74-pg4w · **NYC Truck Routes**: https://data.cityofnewyork.us/Transportation/New-York-City-Truck-Routes-Map-/wnu3-egq7 · **NYC Citywide Low Bridges**: https://data.cityofnewyork.us/Transportation/Citywide-Low-Bridges/rn6h-i66u |
| Coverage | NY state (events, truck parking, winter conditions) + NYC (mandatory truck route network, low-clearance list incl. parkway bans) |
| Update frequency | 511NY: real-time XML/JSON feed; NYC truck routes updated 2026-03-02; low bridges updated 2024-10-30 |
| Quality | High; NYC parkways (trucks banned) are the #1 US bridge-strike zone — this data is essential |
| License | 511NY: Developer Access Agreement (free, requires stating your use). NYC: NYC Open Data terms (free) |
| Access | 511NY: REST + XML feed, free key, 10 calls/60 s. NYC: Socrata (CSV/GeoJSON/OData/API), no key needed for modest use |
| Cost | Free |
| Advantages | NYC set = truck bans + low bridges as clean GIS; state API adds truck parking |
| Limitations | 511NY DAA requires an application describing your product; state API has no static restriction inventory |

### 2.10 Oregon — ODOT TripCheck API + restriction lists
| Field | Value |
|---|---|
| Label | OFFICIAL |
| Owner | Oregon DOT |
| URL | API portal: https://apiportal.odot.state.or.us/product/tripcheck-data-api · Guide: https://www.tripcheck.com/pdfs/TripCheckAPI_Getting_Started_GuideV5.pdf · CCD travel restrictions (trucking): https://www.oregon.gov/odot/mct/pages/oregon-travel-restrictions.aspx |
| Coverage | OR |
| Update frequency | Real-time (incidents, DMS, RWIS); Road & Bridge Restrictions List updated as restrictions change |
| Quality | High |
| License | Free XML/JSON "made available to the public for integration into applications" |
| Access | REST API (XML/JSON) via free portal signup; restriction LIST is HTML/PDF (Commerce & Compliance Division) |
| Cost | Free |
| Advantages | Explicitly welcomes app integration |
| Limitations | Trucking restriction list not GIS — text list requiring conflation |

### 2.11 Colorado — CDOT / COtrip
| Field | Value |
|---|---|
| Label | OFFICIAL |
| Owner | Colorado DOT |
| URL | Developer help: https://maps.cotrip.org/help/117/Traveler-Information-Data-Feed-Access · API manager: https://manage-api.cotrip.org/ · Legacy XML catalog: https://data.colorado.gov/Transportation/COTRIP-s-Catalog-of-XML-Data-Feeds/9j2v-jtrg · Vertical clearances pages: https://ft-cdot.opendata.arcgis.com/pages/vertical-clearances |
| Coverage | CO |
| Update frequency | Real-time feeds (incidents, road conditions, construction); WZDx feed 5-min |
| Quality | High |
| License | Free developer access w/ key |
| Access | JSON/XML APIs + WZDx GeoJSON (key required per WZDx registry) + ArcGIS Hub for clearances |
| Cost | Free |
| Advantages | Chain law / winter restriction state — feed includes those events; separate vertical clearance publication |
| Limitations | Key required; permanent restriction inventory beyond clearances UNCERTAIN |

### 2.12 Wisconsin — WisDOT seasonal programs
| Field | Value |
|---|---|
| Label | OFFICIAL |
| Owner | Wisconsin DOT |
| URL | Program hub: https://wisconsindot.gov/Pages/dmv/com-drv-vehs/mtr-car-trkr/ssnl-wt-rsrctns/default.aspx · GIS dataset (via GeoData@Wisconsin): https://geodata.wisc.edu/catalog/DOT-2e56b5b256124198b0be2c4815c42a18 ("Seasonal Weight Restrictions, WI DOT") |
| Coverage | WI — frozen-road declaration zones, Class II roads, posted roads |
| Update frequency | Seasonal (frozen-road declared ~mid-Dec, ended statewide 2026-02-20; posted roads ~Mar–May) |
| Quality | High; interactive map maintained by WisDOT |
| License | WI open records / GeoData@Wisconsin open access |
| Access | HTML interactive map + GIS download via geodata catalog |
| Cost | Free |
| Advantages | One of the few states with the seasonal layer catalogued as GIS |
| Limitations | Machine-readable *live* status feed UNCERTAIN — may need scraping the map service |

### 2.13 Michigan — MDOT (frost laws, bulletin-based)
| Field | Value |
|---|---|
| Label | OFFICIAL |
| Owner | Michigan DOT + county road agencies |
| URL | Spring Weight Restriction bulletins: https://mdotjboss.state.mi.us/APSWB/SWBHome.htm?bulletin=weight · Trucker hub: https://www.michigan.gov/mdot (Truckers → Restrictions) · County-level: https://micountyroads.org/business/seasonal-weight-restrictions/ |
| Coverage | MI — "all-season" vs "seasonal" routes (25% rigid / 35% flexible pavement reductions) |
| Update frequency | Bulletins issued through the season (2026 season: Feb 17 start, lifted in stages through late April) |
| Quality | Authoritative but **document-shaped** (bulletins + Truck Operators Map PDF) |
| License | Public |
| Access | HTML bulletins + PDF maps; **GIS layer for restrictions: UNCERTAIN** (not found on an MDOT open-data portal today) |
| Cost | Free |
| Advantages | Clear legal rules; county association aggregates local restrictions |
| Limitations | No confirmed machine-readable feed — a scraper/parser is needed; county data fragmented |

### 2.14 Utah + Nevada + Arizona + Georgia + Alaska — same 511 API platform as Idaho/NY
All verified live doc pages (same vendor platform, free key, ~10 calls/60 s):
| State | API docs URL | Trucker-relevant content |
|---|---|---|
| Utah (UDOT Traffic) | https://prod-ut.ibi511.com/developers/doc (also https://www.udottraffic.utah.gov/) | Road conditions, mountain passes, rest areas, events, snow plows |
| Nevada | https://www.nvroads.com/developers/doc | Events, conditions, cameras |
| Arizona | https://www.az511.com/developers/doc | Events, alerts, message boards |
| Georgia | https://511ga.org/developers/doc | Events, conditions |
| Alaska | https://511.alaska.gov/developers/doc | Road conditions, temporary work zones, bridges |
All OFFICIAL, free key, JSON/XML REST. Pattern insight: **any state whose 511 site is on this platform likely exposes `/developers/doc` and often a WZDx endpoint** — check each target state's 511 site first.

### 2.15 Other verified state/city one-offs
| Source | Label | URL | Note |
|---|---|---|---|
| Memphis TN truck routes (prohibited streets) | OFFICIAL | https://maps.memphistn.gov/mapping/rest/services/Engineering/Engineering_Truck_Routes/FeatureServer/layers | Live ArcGIS REST, city truck bans |
| Sonoma County CA vehicle restrictions | OFFICIAL | https://socogis.sonomacounty.ca.gov/map/rest/services/TPWPublic/Ordinance_Vehicle_Restrictions/FeatureServer/layers | County ordinance restrictions w/ limit+units fields |
| FDOT Open Data Hub | OFFICIAL | https://gis-fdot.opendata.arcgis.com/ | Rich portal; a dedicated truck-restriction/clearance layer was NOT confirmed today — UNCERTAIN |
| NYS GIS Clearinghouse (NYSDOT Structures) | OFFICIAL | https://data.gis.ny.gov/ | Bridge locations w/ BDMS attributes |
| MnDOT ArcGIS REST directory | OFFICIAL | https://www.dot.state.mn.us/surveying/geodetics/arcgisrestserv.html | Entry point to MnDOT services |

---

## 3. Seasonal spring-thaw (frost law) coverage summary

| State | Machine-readable? | Best access | Season pattern (2026 observed) |
|---|---|---|---|
| MN | Partial (Experience app + Commons GIS) | dot.state.mn.us/loadlimits + gisdata.mn.gov | 6 zones, 5/7-ton routes, ~8 weeks |
| WI | Yes (GeoData@Wisconsin layer) + HTML map | geodata.wisc.edu catalog + WisDOT map | Frozen-road Dec→Feb, posted roads Mar→May |
| MI | No (bulletins/PDF) | MDOT APSWB bulletins + micountyroads.org | Feb 17 start, staged lift through April |
| ND | Yes (live ArcGIS REST) but **non-commercial ToS** | gis.dot.nd.gov rcrs_dynamic MapServer | ~12-week window, weather-driven |
| MT | UNCERTAIN — not verified today | MDT road restriction pages / 511 (check https://roadreport.mdt.mt.gov) | Frost law state; endpoint unverified |
| Others (SD, ME, NH, VT, WA, MN counties…) | UNCERTAIN | State-by-state check needed | Frost-law states per industry references |

Community reference (context only, commercial site, not a data source): oversize.io frost-laws pages.

---

## 4. OpenStreetMap — the community layer

| Field | Value |
|---|---|
| Label | COMMUNITY |
| Owner | OpenStreetMap contributors |
| Key tags | `maxheight`, `maxweight`, `maxwidth`, `maxlength`, `hgv=*` (truck access), `hazmat=*`, `hgv:national_network` (STAA network) |
| Tag docs | https://wiki.openstreetmap.org/wiki/Key:maxheight · https://wiki.openstreetmap.org/wiki/Key:maxweight · https://wiki.openstreetmap.org/wiki/Key:hgv |
| Coverage reality | **Global** `maxheight`: 495,160 objects (verified via taginfo API 2026-07-22: 422k ways + 72k nodes). **US-only share: UNCERTAIN** (US taginfo instance unreachable today). Practical reality: US coverage is incomplete and uneven — far below NBI's ~620k bridges; treat as supplement, never the legal source. OptimoRoute runs an organized-editing program improving US `hgv` data (https://wiki.openstreetmap.org/wiki/Organised_Editing/Activities/OptimoRoute). |
| Update frequency | Continuous (minutely diffs) |
| License | **ODbL 1.0 — attribution + share-alike on derived databases.** Design your data pipeline so OSM-derived layers stay ODbL-compatible. |
| Access methods | Overpass API (https://overpass-api.de, free, fair-use rate limits) · Geofabrik US extracts (https://download.geofabrik.de, bulk .pbf, free) · planet files |
| Auth / Cost | None / Free |
| Advantages | Only free NATIONAL road-segment-level restriction geometry; includes truck bans (`hgv=no`) on e.g. NYC parkways; instantly routable (OSRM/Valhalla/GraphHopper consume these tags) |
| Limitations | Incomplete + unverified legally; a missing tag ≠ no restriction — silent false negatives are the danger for truck routing |
| QA tooling | OSM Truck QA Map: http://maxheight.bplaced.net/ (community QA overlay for missing maxheight) |

---

## 5. Low-clearance strike databases

**Honest answer: no public national bridge-strike database exists.**
- NYSDOT maintains an internal collision/bridge-hit database (~200 hits/yr) — visible only through research reports (e.g. https://rosap.ntl.bts.gov/view/dot/67805), **not published as data**.
- Free proxies to build with: NBI vertical clearance items (§1.1) + NYC Citywide Low Bridges (§2.9) + OSM `maxheight` (§4).
- Commercial gap: curated national low-clearance databases (e.g. lowclearances.com, Rand McNally/Trimble truck attributes) are paid.

---

## 6. Access-method cheat sheet (what the solo builder actually wires up)

| Access pattern | Sources using it | Effort |
|---|---|---|
| Annual bulk CSV download | FHWA NBI | Trivial — one cron/yr |
| Socrata API/CSV | WZDx registry, NYC datasets, data.ny.gov | Trivial |
| GeoJSON polling (WZDx spec) | ~40+ WZDx feeds | Low — one parser, many feeds |
| No-key ArcGIS REST (`f=geojson`) | WSDOT, PennShare, Iowa, Memphis, Sonoma, (ND — ToS issue) | Low |
| Free-key REST 511 APIs (10 calls/min) | ID, NY, AZ, NV, GA, AK, UT, OHGO, TripCheck, COtrip | Low-medium — key mgmt + caching |
| OSM Overpass / Geofabrik | maxheight/maxweight/hgv | Medium — tag parsing + ODbL care |
| HTML/PDF only (parse or manual) | FMCSA NHMRR, MI bulletins, OR CCD list | High — the unavoidable grind |

---

## 7. HONEST GAPS — no free/legal source exists

1. **Harmonized 50-state truck restriction network** (per-segment weight/height/length/ban attributes, navigation-grade). Only commercial: HERE, TomTom, Trimble Maps (PC*Miler), ProMiles. This is THE paid gap of the category.
2. **Current national hazmat-route GIS.** The legally current NHMRR is an HTML/PDF list; the only GIS versions are 2004-TIGER-vintage (~2012). Free path = digitize the list yourself.
3. **Public bridge-strike incident database.** None. NYSDOT's is internal.
4. **County/municipal posted-road restrictions nationwide.** Fragmented across thousands of jurisdictions, mostly PDFs; no free aggregation (PA + a few counties are the exception, not the rule).
5. **Machine-readable seasonal restriction feeds for most frost-law states.** MI is bulletin-only; MT/SD/ME/NH/VT unverified; ND's live feed is ToS-restricted to non-commercial use.
6. **Complete OSM restriction coverage.** OSM cannot certify absence of a restriction — legal-grade clearance/weight certainty stays a paid/liability gap everywhere.

---

## 8. Recommended build order (simplicity-first)

1. **NBI bulk load** → national low-clearance + load-posted bridge layer (1 file, public domain).
2. **WZDx registry poller** → multi-state construction restrictions with ONE schema.
3. **OSM base** (Geofabrik US) → maxheight/maxweight/hgv/hazmat tags into the routing graph (ODbL-compliant, flagged "community-verified" in UI).
4. **State adapters, one at a time**, starting where data is best: WSDOT → PennDOT → Iowa → Idaho 511 → NYC → OHGO → TripCheck → COtrip.
5. **Seasonal module**: MN + WI GIS first; MI bulletin parser later.
6. **Hazmat**: ship stale-GIS + NHMRR-list cross-check with clear "verify against registry" disclaimer; digitizing the current registry is a background project.
7. **Never claim legal-grade certainty** — every restriction answer carries source + freshness metadata. That honesty is the product.

---

## Verification log (2026-07-22)
- Fetched live OK: `data.transportation.gov/resource/69qe-yiui.csv` (WZDx registry), `data.wsdot.wa.gov/arcgis/rest/services?f=json`, `gis.dot.nd.gov/.../rcrs_dynamic/MapServer?f=json`, `511.idaho.gov/developers/doc`, `taginfo.openstreetmap.org` API, `catalog.data.gov` NHMRR dataset page.
- Fetch blocked (403 bot protection): `fmcsa.dot.gov` NHMRR page (exists per search + Federal Register Dec 2025).
- Unreachable: `taginfo.openstreetmap.us` (DNS fail) — US-specific OSM tag counts UNCERTAIN.
- 404: `catalog.data.gov/api/3/action/package_search` (CKAN API path) — use HTML search instead.
- All other URLs confirmed via current web search results, not memory.

---

## Verification (adversarial pass)
**Verifier run:** 2026-07-22 · Method: independent WebFetch of each claimed URL (or its machine endpoint when the portal is a JS SPA). Default posture was to REFUTE; statuses below are what survived.

| # | Source | Status | Evidence |
|---|---|---|---|
| 1 | FHWA NBI (ascii.cfm) | **CONFIRMED** | Page live (updated 06/18/2025); annual bulk downloads 1992–2025, no auth, no license restriction; FHWA's "not for route clearance purposes" disclaimer verbatim on-page — matches the researcher's caveat exactly. |
| 2 | WZDx Feed Registry | **CONFIRMED** | Portal page is a Socrata SPA shell (uninformative), but the machine endpoint `data.transportation.gov/resource/69qe-yiui.json` returned live registry rows: agency feeds (Oklahoma DOT, Colorado 5-min GeoJSON, NPS…), format=geojson, apikey flags per feed. Claim holds. |
| 3 | State 511 APIs (Idaho pattern) | **CONFIRMED** (Idaho verified; sibling states not re-fetched) | 511.idaho.gov/developers/doc live: literal "Restrictions (weight limits)" endpoint + weigh stations, rest areas, runaway ramps, WZDx at /api/wzdx; free key required; throttle "Ten calls every 60 seconds" — all as claimed. UT/NY/AZ/NV/GA/AK doc pages NOT re-verified in this pass (previously verified per §2.14); treat the multi-state extrapolation as high-confidence but per-state-check-before-build. |
| 4 | WSDOT ArcGIS REST | **CONFIRMED** | Live directory (ArcGIS 11.3) returns `Bridge` and `Vertical_Clearance` folders, no auth. Specific `MinVertClrnc*` field names not independently re-queried this pass — verify at FeatureServer level during build. |
| 5 | PennDOT Posted/Bonded Roads | **CONFIRMED** | Hub portal is an SPA and its search API oddly did NOT return Posted Roads — but ArcGIS Online item search found the PennShare "Posted Roads" Feature Service (REST: gis.penndot.pa.gov/gis/rest/services/opendata/postedroads/MapServer/0, "posted weight restrictions… from PennDOT's RMS") AND the PASDA mirror page (dataset=47) confirms "Pennsylvania Roads with Posted Weight Restrictions," 2026 version, with zip/KMZ/GeoJSON/REST/WMS. Use the direct REST URL, not Hub search. |
| 6 | OSM maxheight/maxweight/hgv | **CONFIRMED** (with license nuance) | Wiki page live, describes vehicle height-restriction tagging as claimed. Nuance: the wiki page itself is CC-BY-SA and does not state ODbL; ODbL 1.0 for the OSM *database* is correct but sourced from osm.org/copyright, not this page. The 495k-object taginfo count and US-share uncertainty were not re-measured — researcher already flagged them honestly. |
| 7 | FMCSA NHMRR | **CONFIRMED** (with the access caveat the researcher already disclosed) | fmcsa.dot.gov returned HTTP 403 to automated fetch — exactly as the claim warns. Independent confirmation via Federal Register 2025-22192 (published 2025-12-08): FMCSA maintains/revises the NHMRR by state, supersedes prior publications, current registry on FMCSA's site. The "no current GIS, text-only, bot-blocked" honesty checks out. Automated scraping of fmcsa.dot.gov should be treated as NOT permitted absent robots.txt review — plan manual/periodic download. |
| 8 | NYC Citywide Low Bridges | **CONFIRMED** (with staleness + access caveats) | Socrata metadata API confirms dataset "Citywide Low Bridges" (NYC DOT, low-clearance locations on limited-access highways). Two adversarial findings: (a) underlying data appears to date from **July 2009** (index refreshed 2024) — older than the file's "updated 2024-10-30" implies; treat as a static historic layer, cross-check against NYC Truck Routes dataset; (b) the no-key `/resource/` JSON endpoint returned 403 to this fetcher — likely UA-based bot filtering, so "no key for modest use" may in practice require a free Socrata app token. |

**Overall:** All 8 sources are real, live, free, and substantively as described — no fabricated sources found, and the researcher's self-flagged caveats (NBI disclaimer, NHMRR 403 + no GIS, OSM incompleteness) were independently reproduced, which is a good sign of honest research. The three soft spots surfaced by this pass: (1) NYC Low Bridges data vintage (~2009) is materially older than presented — demote it from "clean current GIS" to "static baseline layer"; (2) the multi-state 511 claim was only re-verified for Idaho here — re-check each sibling state's `/developers/doc` before committing the shared-client assumption; (3) discovery paths matter — PennShare Hub search hides Posted Roads and Socrata SPAs are opaque to bots, so the build should pin the direct REST/resource endpoints recorded above rather than portal search.
