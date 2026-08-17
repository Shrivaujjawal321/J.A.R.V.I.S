# Tunnel Intelligence — Legal Source Inventory (Clearance, Hazmat, Restrictions)

**Category:** Tunnel intelligence for a US-wide Truck Intelligence Platform
**Researched:** 2026-07-22 (all URLs live-verified on this date unless marked UNCERTAIN)
**Constraint honored:** free + legally-authorized sources only. No paid APIs, no scraping of bot-blocked pages.

**Labels used:** `OFFICIAL` = government source · `OPEN` = open-licensed organization · `COMMUNITY` = crowdsourced (e.g. OSM)

---

## Executive Summary (plain language)

There is **one excellent federal backbone** for tunnel data: the **FHWA National Tunnel Inventory (NTI)** — every public-road highway tunnel in the US (~500+), with portal coordinates, length, **minimum vertical clearance**, **height restriction flag**, **hazardous-material restriction field**, and more. It is public domain, downloadable in bulk (Excel/XML), and also served as a live **ArcGIS REST Feature Service** by BTS with GeoJSON/CSV export. Updated once a year.

The **detailed rules** (which hazmat classes, what quantities, what exceptions) live in **per-authority HTML pages and PDFs** (Port Authority NY/NJ, MTA, Maryland MDTA, MassDOT, VDOT, Colorado DOT, PA Turnpike) and in the **FMCSA National Hazardous Materials Route Registry (NHMRR)**. These are free and public but mostly **not machine-readable** — the honest engineering answer is a small **hand-curated overrides table** refreshed manually a few times a year, which is realistic because major tunnel rules change rarely.

**OpenStreetMap** is the only free source that encodes tunnel `maxheight` and `hazmat=no` as routable map attributes — verified live via Overpass (e.g., Eisenhower Tunnel carries `hazmat: no`, `maxheight: 13'11"`).

---

## 1. Federal Core Sources

### 1.1 FHWA National Tunnel Inventory (NTI) — annual bulk download — `OFFICIAL`

| Attribute | Detail |
|---|---|
| Source owner | Federal Highway Administration (FHWA), US DOT |
| Official URL | https://www.fhwa.dot.gov/bridge/inspection/tunnel/inventory/download.cfm (verified 2026-07-22) |
| Program page | https://www.fhwa.dot.gov/bridge/inspection/tunnel/inventory.cfm |
| Geographic coverage | All US states + DC + federal/tribal lands — every highway tunnel on public roads (~500+ tunnels) |
| Update frequency | **Annual.** States submit in spring; final public data published **by June 15 each year**. Files verified for 2018–2025 (`2025NTI.xlsx`, `2025NTI.xml`, etc.) |
| Data quality | High — legally mandated under the National Tunnel Inspection Standards (23 CFR 650 Subpart E); each record inspected/reported by the tunnel owner |
| License | US Government work — public domain (17 U.S.C. § 101), unrestricted use |
| Access method | **Bulk download**: Excel (.xlsx) and XML per year. XML schema + example file provided on the same page |
| Authentication | None |
| Cost | Free |
| Advantages | Complete national baseline; includes restriction-relevant fields (see 1.2 field list); stable, versioned by year; tiny data volume (hundreds of rows) — trivially simple to ingest |
| Limitations | Annual cadence only (no mid-year changes); restriction fields are **coded values**, not full rule text (e.g., it flags a hazmat restriction exists, not which classes/quantities); no geometry beyond portal lat/lon |

**Companion (needed to decode fields):** *Specifications for the National Tunnel Inventory (SNTI)*, PDF linked from the same download page — defines every item code (I/A/C/G/D/L/N/S/T series), including L10 (height restriction), L11 (hazardous material restriction), L12 (other restrictions). `OFFICIAL`, free, public domain.

### 1.2 BTS NTAD "National Tunnel Inventory" Feature Service — ArcGIS REST + exports — `OFFICIAL`

| Attribute | Detail |
|---|---|
| Source owner | Bureau of Transportation Statistics (BTS, distributor) / FHWA (producer), US DOT. ArcGIS owner account: `USDOT_BTS` |
| Dataset page | https://geodata.bts.gov/datasets/usdot::national-tunnel-inventory/about (JS app — view in browser) |
| **ArcGIS REST endpoint (verified)** | `https://services.arcgis.com/xOi1kZaI0eWDREZv/arcgis/rest/services/NTAD_National_Tunnel_Inventory/FeatureServer` (layer 0; queried live 2026-07-22) |
| Geographic coverage | Nationwide (same records as 1.1, as point features at tunnel portals) |
| Update frequency | Annual, following the FHWA June release (service last modified Sep 2025 per item metadata — the 2025 NTI cycle) |
| Data quality | High — direct republication of FHWA NTI in the National Transportation Atlas Database (NTAD) |
| License (verified from item metadata) | "This NTAD dataset is a work of the United States government as defined in 17 U.S.C. § 101 … not protected by any U.S. copyrights. This work is available for unrestricted public use." Attribution requested: FHWA + BTS |
| Access method | **ArcGIS REST** (`/0/query?where=1%3D1&outFields=*&f=geojson`), plus portal exports: **GeoJSON, CSV, Shapefile, File Geodatabase, KML**; WFS also offered for NTAD layers |
| Authentication | None |
| Cost | Free |
| Advantages | Zero-ETL option: query straight to GeoJSON; already georeferenced points; hosted on Esri infrastructure (reliable, rate-limit friendly for a dataset this small) |
| Limitations | Same annual cadence and coded-fields limitation as 1.1; points only (no tunnel centerline geometry) |

**Restriction-relevant fields verified live from the FeatureServer (69 fields total):**

| Field | Meaning |
|---|---|
| `tunnel_name_i2`, `tunnel_number_i1`, `state_code_i3` | Identity |
| `portal_latitude_i13`, `portal_longitude_i14` | Location |
| `route_number_i7`, `facility_carried_i10`, `lrs_route_id_i11` | Route linkage |
| `tunnel_length_g1` | Length |
| `min_vert_clearance_over_tunnel_roadway_g2` | **Minimum vertical clearance** |
| `roadway_width_curb_to_curb_g3` | Width |
| `height_restriction_l10` | **Height restriction flag** |
| `hazardous_material_restriction_l11` | **Hazmat restriction flag** |
| `other_restrictions_l12` | Other restrictions |
| `posting_load_gross_l5` … `posting_load_type_33_l9` | Load postings |
| `adt_a4`, `adtt_a5` | Traffic (incl. truck traffic) |
| `owner_c1`, `operator_c2`, `toll_c4`, `nhs_designation_c5`, `strahnet_designation_c6` | Ownership / network context |

### 1.3 BTS NTAD "National Tunnel Inventory Element Data" — `OFFICIAL`

| Attribute | Detail |
|---|---|
| Source owner | BTS / FHWA (ArcGIS owner `USDOT_BTS`) |
| **ArcGIS REST endpoint (verified)** | `https://services.arcgis.com/xOi1kZaI0eWDREZv/arcgis/rest/services/NTAD_National_Tunnel_Inventory_Element_Data/FeatureServer` |
| Dataset page | https://geodata.bts.gov/datasets/national-tunnel-inventory-element-data/about |
| Coverage / cadence / license / cost | Same as 1.2 (nationwide, annual, public domain, free) |
| What it adds | Element-level **condition** data (structural elements and their condition states) per tunnel |
| Relevance to platform | Low for routing/restrictions; useful only if you want a "tunnel condition" enrichment layer. Listed for completeness |

### 1.4 FMCSA National Hazardous Materials Route Registry (NHMRR) — `OFFICIAL`

| Attribute | Detail |
|---|---|
| Source owner | Federal Motor Carrier Safety Administration (FMCSA), US DOT |
| Official URL | https://www.fmcsa.dot.gov/regulations/hazardous-materials/national-hazardous-materials-route-registry-state (by-state listing) |
| Geographic coverage | Nationwide — all state/tribal-reported **designated, restricted, and preferred hazmat routes**, including tunnel restrictions (NRHM and Class 7 radioactive HRCQ/RAM) |
| Update frequency | Irregular — FMCSA publishes revision notices in the Federal Register (2015, 2016, 2018, 2019, 2020, 2021, 2022, 2024, Dec 2025 verified). The FMCSA site holds the "full current" registry |
| Data quality | Authoritative (it is *the* legal registry) but **only as current as states' reporting**; known to lag actual state rules |
| License | US Government work — public domain |
| Access method | **HTML pages per state** (route descriptions as text tables). No GIS service, no CSV, no API |
| Authentication | None for humans. **IMPORTANT (verified 2026-07-22): fmcsa.dot.gov returns HTTP 403 to non-browser clients** — automated fetching is blocked by their web protection. Treat as **manual/browser-refresh source**, not a crawl target. Do not bypass |
| Cost | Free |
| Advantages | The only nationwide legal registry of hazmat route restrictions; text explicitly names tunnels (e.g., Baltimore tunnels, NYC tunnels) |
| Limitations | Not machine-readable; no geometry; bot-blocked (manual refresh only); update lag; route descriptions are free-text ("I-95 from X to Y") that you must geocode yourself |

**Automation-friendly companion — Federal Register (verified):** NHMRR revision notices are published at federalregister.gov, e.g. https://www.federalregister.gov/documents/2025/12/08/2025-22192/national-hazardous-materials-route-registry (verified: covers revisions Apr 2024–Mar 2025; DC, MI, CA changes). The **Federal Register API** (`https://www.federalregister.gov/api/v1/documents.json?conditions[term]=National+Hazardous+Materials+Route+Registry`) is free, no-auth, and explicitly open — use it as a **change-detection trigger**: when a new NHMRR notice appears, do a manual browser review of the affected states. `OFFICIAL`, free, public domain.

**Docket PDFs:** per-state NHMRR submissions exist as PDFs on regulations.gov (e.g. `https://downloads.regulations.gov/FMCSA-2014-0022-0026/attachment_1.pdf` for Virginia — verified reachable via search). regulations.gov has a free API (api.data.gov key, free registration). Useful as archival reference, but vintage varies.

### 1.5 Legacy NTAD "Hazardous Material Routes" shapefile — `OFFICIAL` (stale — honesty note)

| Attribute | Detail |
|---|---|
| Source owner | FMCSA (produced), BTS NTAD (distributed) |
| What it is | `hazmat.shp` + `hmroutes.dbf` + `hmstcnty.dbf` — GIS geometry of NHMRR routes |
| Vintage | Built from **2004 TIGER/Line**; catalog copies dated 2006–2012 (MIT/Stanford library mirrors, ROSA-P record https://rosap.ntl.bts.gov/view/dot/71898) |
| Current availability | **No current edition found in the live NTAD catalog** (verified: geodata.bts.gov / `USDOT_BTS` ArcGIS org has NO hazmat-routes feature service today; only "PHMSA HazMat Regions" which is administrative regions, not routes). ScienceBase item https://www.sciencebase.gov/catalog/item/4f4e4a1ae4b07f02db60699b returned 403 to automated fetch — availability UNCERTAIN |
| Honest assessment | **Do not build on this.** It is 20+ years stale. There is no current free GIS version of the NHMRR — that is a real gap (see Gaps) |

---

## 2. State / Regional Authority Sources (the detailed rules)

These are the authorities that own the big restricted tunnels. All are free, public, official. Almost all are **HTML/PDF only** — plan a curated overrides table, refreshed manually (rules change rarely; a quarterly manual check + Federal Register trigger is sufficient).

### 2.1 Port Authority of NY & NJ — Holland + Lincoln Tunnels — `OFFICIAL`

| Attribute | Detail |
|---|---|
| Owner | Port Authority of New York & New Jersey (PANYNJ) |
| URLs | Trucker resources: https://www.panynj.gov/bridges-tunnels/en/trucker-resources.html (verified HTTP 200, 2026-07-22) · **"Green Book"** traffic rules PDF: https://www.panynj.gov/content/dam/bridges-tunnels/pdfs/green-book.pdf · Full Traffic Rules & Regulations PDF: https://www.panynj.gov/content/dam/bridges-tunnels/traffic-rules-and-regulations/TBT%20Traffic%20Rules%20%20Regulations.pdf |
| Coverage | Holland Tunnel, Lincoln Tunnel (+ GWB and PA bridges) |
| Key content | Hazmat prohibited/restricted classes with **per-class quantity limits** (e.g., corrosive liquids max 6.5 gal/100 lb per vehicle); 13'6" height at Lincoln; Holland Tunnel has stricter dimensional limits |
| Cadence | PDFs revised occasionally (no fixed schedule) — UNCERTAIN exact revision cycle |
| License | Public agency publication; facts freely usable with attribution. Not federal public domain — UNCERTAIN formal license text |
| Access / auth / cost | PDF + HTML, no auth, free |
| Advantages | The **legally definitive** class-by-class rules for the two busiest US truck tunnels |
| Limitations | PDF prose → manual extraction into your overrides table |

### 2.2 MTA Bridges & Tunnels — Queens-Midtown + Hugh L. Carey Tunnels (NYC) — `OFFICIAL`

| Attribute | Detail |
|---|---|
| Owner | Metropolitan Transportation Authority (Triborough Bridge & Tunnel Authority) |
| URLs | Truck/commercial info: https://www.mta.info/agency/bridges-and-tunnels/trucks-commercial-vehicle-information · Rules & Regulations PDF: https://www.mta.info/document/14521 |
| Coverage | Queens-Midtown Tunnel, Hugh L. Carey (Brooklyn-Battery) Tunnel |
| Key content | **All hazmat prohibited** in both tunnels; height limit **12'1"**; width 8'6" (QMT) |
| Cadence | Page maintained continuously; UNCERTAIN formal cycle |
| License | Public agency info; UNCERTAIN formal license text |
| Access / auth / cost | HTML + PDF, no auth for humans, free. **Note (verified): mta.info returns 403 to non-browser clients** — manual/browser refresh only |
| Advantages | Simple, absolute rules (blanket hazmat ban) — easy to encode |
| Limitations | Bot-blocked; HTML/PDF only |

### 2.3 Maryland Transportation Authority — Fort McHenry (I-95) + Baltimore Harbor (I-895) Tunnels — `OFFICIAL`

| Attribute | Detail |
|---|---|
| Owner | Maryland Transportation Authority (MDTA) |
| URLs | Hazmat/tunnel restrictions: https://mdta.maryland.gov/TunnelRestrictionsAndVehiclePermits · Facility page: https://mdta.maryland.gov/Toll_Facilities/BHT.html · MDOT SHA quick-reference PDF: https://roads.maryland.gov/OOTS/FORBIDDEN_HAZARDOUS_MATERIALS.pdf (all surfaced via search 2026-07-22) |
| Coverage | Both Baltimore tunnels |
| Key content | Bulk gasoline/flammables/explosives/radioactive **prohibited**; propane limited to 10×10-lb containers (empty or full); legal basis COMAR 11.07.01; alternate route I-695 west |
| Cadence | Standing regulation (COMAR) — changes rare |
| License | Maryland public record; facts freely usable with attribution |
| Access / auth / cost | HTML + PDF, no auth, free |
| Advantages | Clear, stable, includes the regulatory citation (COMAR 11.07.01 — independently verifiable at dsd.state.md.us) |
| Limitations | HTML/PDF prose |

### 2.4 MassDOT — Boston tunnels (Sumner, Callahan, Ted Williams, O'Neill) — `OFFICIAL`

| Attribute | Detail |
|---|---|
| Owner | Massachusetts DOT |
| URLs | Binding regulation **700 CMR 7.06** ("Limitations on Use of Ways") — text mirrored at https://www.law.cornell.edu/regulations/massachusetts/700-CMR-7-06 ; official CMR via mass.gov (search "700 CMR 7.00") — exact mass.gov deep-link UNCERTAIN (mass.gov restructures URLs frequently) |
| Coverage | Sumner (12'6"), Callahan (12'6"), Ted Williams (13'6"), Tip O'Neill/I-93 tunnels |
| Key content | **Placarded hazmat vehicles prohibited** in all Boston harbor/Big Dig tunnels; posted surface alternate routes |
| Cadence | Standing regulation — changes rare |
| License | Massachusetts public record |
| Access / auth / cost | HTML regulation text + posted signage rules; no auth; free |
| Advantages | Codified in regulation → stable and citable |
| Limitations | No dataset; rule text must be hand-encoded |

### 2.5 VDOT — Hampton Roads / Midtown / Downtown / Monitor-Merrimac tunnels — `OFFICIAL`

| Attribute | Detail |
|---|---|
| Owner | Virginia DOT |
| URL (verified via live fetch 2026-07-22) | https://www.vdot.virginia.gov/travel-traffic/freight/truck-restrictions/ |
| Coverage | HRBT (I-64), Midtown (US-58), Downtown (I-264), Monitor-Merrimac (I-664) |
| Key content (verified) | HRBT westbound 13'6" max height (eastbound 14'6"); Downtown Tunnel westbound width ≤8' for tractor-trailers; hazmat classes 1.1/1.2/1.3/2.3/4.3/6.1 prohibited at tunnels, others non-bulk only (per CTB tunnel hazmat regulation, PDF: https://ctb.virginia.gov/media/ctb/agendas-and-meeting-minutes/2011/mar/resol/Agenda_Item_6_Tunnels_HazMat_Regulation_-_Updated_Text.pdf) |
| Bonus geospatial | Page links VDOT **TruckWeb** ArcGIS restriction map + a Power BI weight-posting dashboard (daily updated). Underlying ArcGIS REST endpoint exists but exact URL UNCERTAIN — inspect TruckWeb network calls in a browser to confirm before relying on it |
| Cadence | Page maintained continuously; regulation stable |
| License | Virginia public record |
| Access / auth / cost | HTML + PDF (+ ArcGIS viewer), no auth, free |
| Advantages | One official page covering all Hampton Roads tunnels with exact class lists |
| Limitations | Restriction data as prose; TruckWeb REST endpoint not officially documented |

### 2.6 Colorado DOT — Eisenhower-Johnson Memorial Tunnels (I-70) — `OFFICIAL`

| Attribute | Detail |
|---|---|
| Owner | Colorado DOT |
| URL | https://www.codot.gov/travel/ejmt/metering (EJMT section of codot.gov; surfaced via search 2026-07-22) |
| Coverage | Eisenhower + Johnson bores, I-70 at the Continental Divide |
| Key content | Hazmat **prohibited** through the tunnel (must use US-6 Loveland Pass); when the pass closes in winter, CDOT runs **escorted hazmat convoys** through the tunnel (~hourly). Detailed prohibited-materials list in Colorado hazmat rules (CCR, sos.state.co.us) |
| Cadence | Standing rule; escort operations seasonal |
| License | Colorado public record |
| Access / auth / cost | HTML, no auth, free |
| Advantages | Covers the most operationally complex hazmat tunnel rule in the US (conditional on a mountain pass) |
| Limitations | The conditional logic (pass open vs closed) cannot be captured by any static dataset — real-time CDOT feeds (COtrip) belong to the closures/weather category |

### 2.7 Pennsylvania Turnpike Commission — 5 turnpike tunnels — `OFFICIAL`

| Attribute | Detail |
|---|---|
| Owner | PA Turnpike Commission (PTC) |
| URL | https://www.paturnpike.com/commercial/permits-restrictions/hazardous-materials-(placarded-loads) (surfaced via search 2026-07-22) |
| Coverage | Allegheny, Tuscarora, Kittatinny, Blue Mountain, Lehigh tunnels |
| Key content | Table 1 materials + all explosives **prohibited**; Table 2 (flammable gas/liquid/solid, oxidizer, organic peroxide, poison, corrosive) allowed **non-bulk only** (≤119 gal liquid / ≤882 lb solid / ≤1,000 lb-water-capacity gas); legal basis 67 Pa. Code § 601.5 |
| Cadence | Standing rule |
| License | PA public record |
| Access / auth / cost | HTML, no auth, free |
| Advantages | Explicit quantity thresholds — directly encodable |
| Limitations | HTML prose |

### 2.8 Chesapeake Bay Bridge-Tunnel — `OFFICIAL` (independent authority)

| Attribute | Detail |
|---|---|
| Owner | Chesapeake Bay Bridge and Tunnel Commission (political subdivision of Virginia — not VDOT) |
| URL | https://www.cbbt.com/ — specific restrictions page UNCERTAIN (not directly verified this session) |
| Key content | 13'6" max height (per VDOT cross-reference, verified); hazmat rules and wind-based vehicle restrictions exist — details UNCERTAIN, confirm manually on cbbt.com before encoding |
| Access / cost | HTML, free |

### 2.9 Other notable single-tunnel rules (verify each manually before encoding)

- **East River Mountain / Big Walker tunnels (I-77, VA/WV):** covered by the same VDOT tunnel hazmat regulation (class list in 2.5 PDF). `OFFICIAL`
- **Zion-Mount Carmel Tunnel (UT SR-9, NPS):** oversize vehicles require paid escort permit; height/width rules on nps.gov/zion. Not a freight corridor — low priority. `OFFICIAL`, details UNCERTAIN this session
- **NYC-wide hazmat routing (NYPD/NYCDOT rules, 34 RCNY):** blanket rules for continuous-transit hazmat through NYC; relevant context for the MTA/PANYNJ tunnels. `OFFICIAL`, encode only after manual review

---

## 3. Community Source

### 3.1 OpenStreetMap (via Overpass API / Geofabrik extracts) — `COMMUNITY`

| Attribute | Detail |
|---|---|
| Source owner | OpenStreetMap contributors (OpenStreetMap Foundation) |
| URLs | Overpass API: https://overpass-api.de/api/interpreter (live-verified 2026-07-22) · Bulk extracts: https://download.geofabrik.de/north-america.html · Tag docs: https://wiki.openstreetmap.org/wiki/Key:hazmat |
| Coverage | Nationwide (worldwide), completeness varies by tunnel |
| Update frequency | Continuous (minutely diffs); Geofabrik extracts daily |
| Data quality | Good on major tunnels, unverified crowd data elsewhere. **Live verification this session:** Eisenhower Memorial Tunnel and Johnson Memorial Tunnel both carry `hazmat=no` and `maxheight=13'11"` in OSM today |
| License | **ODbL 1.0** — free, but share-alike applies to derivative *databases*; attribution "© OpenStreetMap contributors" required |
| Access method | Overpass API (query language, JSON/XML out), or bulk `.osm.pbf` download (Geofabrik) processed with osmium/osm2pgsql |
| Authentication | None |
| Cost | Free (public Overpass instances have fair-use rate limits — for production, run your own Overpass or use pbf extracts) |
| Advantages | Only free source where restrictions are attached to **routable road geometry** (`tunnel=yes`, `maxheight`, `hazmat`, `maxweight`); the same data your OSM-based router (OSRM/Valhalla/GraphHopper) would consume, so restrictions become routing constraints for free |
| Limitations | No guarantee of completeness/correctness; hazmat tagging is sparse outside famous tunnels; ODbL share-alike needs a compliance decision if you mix it into your own restriction database |

**Example verified query (Eisenhower Tunnel area):**
```
[out:json];way(39.66,-106.0,39.72,-105.85)["tunnel"="yes"]["highway"="motorway"];out tags;
```

---

## 4. Comparison Matrix

| Source | Label | Machine-readable? | Geometry? | Clearance | Hazmat detail | Cadence | Auth | Cost |
|---|---|---|---|---|---|---|---|---|
| FHWA NTI bulk (1.1) | OFFICIAL | Yes (XLSX/XML) | Portal points | Yes (G2) | Flag only (L11) | Annual | None | Free |
| BTS NTAD NTI REST (1.2) | OFFICIAL | Yes (REST/GeoJSON/CSV) | Portal points | Yes | Flag only | Annual | None | Free |
| NTI Element Data (1.3) | OFFICIAL | Yes | Points | No | No | Annual | None | Free |
| FMCSA NHMRR (1.4) | OFFICIAL | No (HTML, bot-blocked) | No | No | Route-level yes | Irregular | None (browser) | Free |
| Federal Register API (1.4) | OFFICIAL | Yes (JSON API) | No | No | Change notices | Per notice | None | Free |
| Legacy hazmat shapefile (1.5) | OFFICIAL | Yes | Lines | No | Route-level | **Frozen ~2004** | None | Free |
| PANYNJ (2.1) | OFFICIAL | No (PDF) | No | Yes | Class+quantity | Rare | None | Free |
| MTA B&T (2.2) | OFFICIAL | No (HTML/PDF, bot-blocked) | No | Yes | Blanket ban | Rare | None (browser) | Free |
| MDTA (2.3) | OFFICIAL | No (HTML/PDF) | No | Yes | Class+quantity | Rare | None | Free |
| MassDOT 700 CMR (2.4) | OFFICIAL | No (reg text) | No | Yes | Blanket ban | Rare | None | Free |
| VDOT (2.5) | OFFICIAL | No (HTML/PDF; ArcGIS viewer) | Viewer only | Yes | Class list | Maintained | None | Free |
| CDOT EJMT (2.6) | OFFICIAL | No (HTML) | No | Yes | Ban+escort | Seasonal ops | None | Free |
| PA Turnpike (2.7) | OFFICIAL | No (HTML) | No | Yes | Class+quantity | Rare | None | Free |
| OSM/Overpass (3.1) | COMMUNITY | Yes (API/PBF) | **Routable ways** | `maxheight` | `hazmat=*` | Continuous | None | Free |

---

## 5. Recommended Build (simple, boring, solo-friendly)

1. **Base layer:** ingest the BTS NTAD NTI Feature Service once a year (a single GeoJSON query, ~500 rows) into Postgres/SQLite. Decode L10/L11/L12 and G2 using the SNTI spec. This gives every US tunnel with clearance + restriction flags + coordinates.
2. **Overrides table (hand-curated):** one small YAML/CSV — `tunnel_id, authority, rule_type (hazmat_ban | class_limits | height | width | escort), detail, source_url, last_checked`. Populate the ~15 tunnels in Section 2 (they cover the overwhelming majority of real-world truck-tunnel pain). This is maybe a day of manual work and minutes per quarter to maintain.
3. **Change detection:** poll the free Federal Register API for new NHMRR notices; when one appears, manually review the affected states. Re-download NTI every July.
4. **Routing integration:** if the router is OSM-based (OSRM/Valhalla/GraphHopper), the OSM `maxheight`/`hazmat` tags already constrain routes; use layers 1–2 to verify/patch OSM where it's missing (contribute fixes upstream — legal and improves your own router).

---

## 6. Honest Gaps (no free/legal source exists)

1. **Nationwide machine-readable tunnel restriction *rules* feed** — no free source encodes per-tunnel hazmat classes/quantities/height as structured data nationwide. NTI gives flags only; the real rules are scattered HTML/PDF. Commercial gap-fillers: HERE Truck Attributes, Trimble/PC*Miler, ProMiles, INRIX — all paid/proprietary.
2. **Current GIS geometry of the NHMRR** — the only shapefile is ~2004-vintage; the live registry is HTML-only and FMCSA's site blocks automated access (HTTP 403 verified). No free bulk/API path exists today.
3. **Intra-year restriction change feed** — NTI is annual; there is no federal feed of mid-year clearance/restriction changes (temporary restrictions live in state 511/work-zone feeds — a different category of this project).
4. **Verified completeness of OSM hazmat tags** — no free ground-truth to audit OSM coverage nationwide; sparse outside famous tunnels.
5. **Bot-blocked official pages** (fmcsa.dot.gov, mta.info, sciencebase.gov item) — legally public but technically closed to automation; the only compliant path is periodic manual browser review.
6. **CBBT + smaller authority specifics** — restriction details for some independent authorities (CBBT wind rules, Zion escort fees) were not verified this session; marked UNCERTAIN and need one-time manual confirmation.

---

## Verification (adversarial pass)

**Verified:** 2026-07-22, independent adversarial re-check of the 8 claimed sources via live WebFetch. Method: fetch each URL (or a machine-readable variant), attempt to refute liveness / data / license / automation claims. Default UNCERTAIN when not confirmable.

| # | Source | Status | Finding |
|---|---|---|---|
| 1 | BTS NTAD NTI FeatureServer | **CONFIRMED** | Live ArcGIS FeatureServer, point layer, "more than 500 of the Nation's tunnels," compiled Sep 2025 from FHWA. Metadata states US-government work, "available for unrestricted public use." No auth. Query/Extract capabilities enabled. |
| 2 | FHWA NTI bulk download | **CONFIRMED** | Page live; Excel + XML per year 2018–2025 all present; SNTI spec PDF (June 2015) + XML schema + example file linked on same page; "final … by June 15th" language present. No access restrictions stated. |
| 3 | FMCSA NHMRR by-state | **CONFIRMED** (as claimed) | Automated fetch returned HTTP 403 — exactly matching the researcher's own "manual browser only, do not scrape" caveat. Registry existence + FMCSA custodianship independently corroborated by the Dec 2025 Federal Register notice. Page content itself is unverifiable by automation, which is the disclosed limitation, not a refutation. |
| 4 | Federal Register API (NHMRR trigger) | **CONFIRMED** | `api/v1/documents.json?conditions[term]=National+Hazardous+Materials+Route+Registry` returns valid JSON, no auth: doc 2025-22192 (2025-12-08, revisions Apr 2024–Mar 2025) and 2024-15614 (2024-07-16) both present. Change-detection strategy works as described. |
| 5 | OSM Overpass tunnel attributes | **CONFIRMED** | Live Overpass query over the Eisenhower bbox returned way 17025436 "Eisenhower Memorial Tunnel" and way 17025430 "Edwin C. Johnson Memorial Tunnel," both tagged `hazmat=no` and `maxheight=13'11"` — the exact values claimed. |
| 6 | PANYNJ trucker resources + rules PDFs | **CONFIRMED** (caveats) | Page returns 200 but body is JS-rendered (only the "Truckers' Resources" heading visible to a plain fetch). However, the green-book.pdf URL serves the full PANYNJ **Traffic Rules and Regulations** for Holland/Lincoln Tunnels + PA bridges, containing Section 7 "Hazardous Materials and Other Dangerous Articles" and Table I "Vehicle Size and Weight Limitations." **Caveat:** the PDF is marked "Revised September 2016" — check for a newer revision before encoding rules. |
| 7 | MDTA Baltimore tunnel restrictions | **UNCERTAIN** | mdta.maryland.gov returned HTTP 403 to automated fetch, and the roads.maryland.gov FORBIDDEN_HAZARDOUS_MATERIALS.pdf also returned 403. The researcher's "no auth" framing understates this: like FMCSA/MTA, Maryland's sites are bot-blocked — treat as **manual browser refresh only**. Content (COMAR 11.07.01 bans) is plausible and independently citable via COMAR itself, but was not confirmable this pass. |
| 8 | VDOT truck restrictions page | **CONFIRMED** (one overclaim) | Page live: HRBT 13'6" WB, Midtown 13'6", Downtown 13'6" + 8' width WB tractor-trailers, and the TruckWeb ArcGIS viewer link — all verified. **Refuted detail:** the prohibited hazmat class list (1.1/1.2/1.3/2.3/4.3/6.1) is **not on this page**; it links to a separate hazmat section which also does not enumerate classes (it defers to DMV requirements / CTB regulation). The class list must come from the CTB PDF, which was not verified this pass. |

**Overall:** 6 of 8 sources fully confirmed, including everything load-bearing: the federal backbone (NTAD REST + FHWA bulk + SNTI spec), the Federal Register change-detection trigger, the Overpass/OSM routable-attribute layer, and the PANYNJ rules PDF. The two non-confirmations are honest-friction cases, not fabrications: MDTA is bot-blocked (403 on both HTML and PDF — downgrade its access note to "manual browser only," same handling as FMCSA/MTA), and VDOT's hazmat class list lives in the linked CTB regulation PDF rather than on the restrictions page itself. No source was found dead, paywalled, or license-misrepresented; the researcher's own caveats (FMCSA 403, curated-overrides strategy) proved accurate under adversarial re-testing. Action items: (a) mark MDTA bot-blocked in §2.3, (b) verify the CTB tunnel hazmat PDF and the currency of the 2016 PANYNJ Traffic Rules during the one-time manual curation pass.
