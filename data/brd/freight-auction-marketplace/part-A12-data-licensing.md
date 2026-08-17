# Part A12 — Data licensing and commercial-use review

**Scope.** Stress-test of `DEC-LOCK-002`: may Boss's `~/Documents/truck-intel` data platform be
redistributed **inside a third party's proprietary commercial product**, per source, and what
obligation attaches. ID block **1200-1299**. Trace: `OBJ-007` unless stated.

**Not legal advice.** A surface-and-controls map, not a clearance. Every "Yes" below is a reading
of a published term, not a conclusion of law. Counsel handoff in §7.

**Method.** Read all 13 `registry/*.yaml`, `README.md` and the non-registry ingestion scripts;
queried the live DB for per-table counts; re-fetched NTAD layer metadata, all four WZDx feeds and
the Overture / ODbL / EIA / NWS / ATP / Caltrans terms **today (2026-07-29)**. A term that could
not be retrieved is **Unverified**, not inferred.

**CHALLENGE (to `DEC-LOCK-002`).** Its inventory table is licence-blind. "Fuel places · fuel prices
151,767 · Overture / OSM" is one row but **two tables under incompatible licences** —
`core.fuel_places` (151,767, Overture, permissive) and `osm.fuel_stations` (**108,056, ODbL,
share-alike**) — and the ODbL one is absent from the inventory though it is what `/v1/fuel` serves.
Same defect on "Weigh points · rest areas · truck parking": first two ODbL, third federal. Restate
per table, per licence, or §2's re-architecture is scoped against the wrong asset.

---

## 1. Per-source register

Counts from the live DB, 2026-07-29.

| # | Layer (rows) | True upstream (as built) | Licence | Redistribute? | Obligation | What breaks if ignored |
|---|---|---|---|---|---|---|
| 1 | Truck routes 454,830 | `services.arcgis.com/.../NTAD_National_Network` (BTS/FHWA) | US Govt work. Layer `copyrightText`, re-read live today: *"a work of the United States government as defined in 17 U.S.C. § 101 … not protected by any U.S. copyrights. This work is available for unrestricted public use."* | **Yes** | Attribution requested, not required. Carry the layer's own advisory — *"should not be used for truck size and weight enforcement purposes or for navigation"* — and its 2018 vintage | Not a licence break, a **misrepresentation** break: a 2018 advisory layer sold as legal truck-routing lands on A8's negligent-selection surface |
| 2 | Bridges 629,710 | `fhwa.dot.gov/bridge/nbi/2025allstatesallrecsdel.zip` | US Govt work (FHWA) | **Yes** | Attribution requested; source units metres / metric tons | Silent unit error → false clearance. Safety, not licence |
| 3 | Tunnels 580 | `.../NTAD_National_Tunnel_Inventory` | Same NTAD `copyrightText`, re-read live today | **Yes** | Attribution requested | As row 1 |
| 4 | Truck parking 1,915 | `.../NTAD_Truck_Stop_Parking` | Same NTAD `copyrightText`, re-read live today | **Yes** | Attribution; ~2019 Jason's Law vintage must show | Stale capacity presented as live |
| 5 | Fuel prices 17,089 | `api.eia.gov/v2/petroleum/pri/gnd` (**keyed**) | Public domain — *"U.S. government publications are in the public domain and are not subject to copyright protection"*, attribution requested (`eia.gov/about/copyrights_reuse.php`) | **Yes** on data · **Unverified** on API-key registration terms | Attribution; EIA logo is a trademark; key must be the **client's** | A registration ToS binds independently of copyright and was not retrieved. Boss's personal key in a client product is the live failure |
| 6-9 | WZDx — AZ `az511.com/api/wzdx`, KS + MN `carsprogram.org`, WA `wzdx.wsdot.wa.gov` | Four state DOT feeds, keyless | **Unverified.** Live check today: **all four return `feed_info.license` = null**; no published redistribution grant located. The registry's "state open data" label is an inference, not a cited term | **Unverified — treat as No until cleared** | Unknown | State works get **no** §105 benefit. A paid product on four contractless feeds can be cut off or throttled per state, without notice |
| 10 | Caltrans chain controls D02/D03/D09 | `cwwp2.dot.ca.gov/data/dNN/cc/ccStatusDNN.json`, keyless | `dot.ca.gov/conditions-of-use`: website information *"is considered in the public domain. It may be distributed or copied as permitted by law."* | **Yes-with-obligation** for site content · **Unverified** that it reaches the `cwwp2` machine feed | Attribution + Caltrans no-warranty disclaimer | Weak link is reliance, not copyright — chain control drives a winter routing decision |
| 11 | NWS alerts (in the 10,636) | `api.weather.gov/alerts/active` | US Govt work — *"All of the information presented via the API is intended to be open data, free to use for any purpose."* | **Yes-with-obligation** | Descriptive **User-Agent + contact email** mandatory; undisclosed rate limits; NWS disclaimer | Wrong/absent UA → blocked; live alerts fail **silently** |
| 12 | Fuel places 151,767 (`core.fuel_places`) | Overture Places theme, S3 release **2026-06-17.0** | **CDLA-Permissive-2.0** + **Apache-2.0** (Foursquare). Verified today at `docs.overturemaps.org/attribution/`: the **places theme does not contain OSM-derived records** | **Yes-with-obligation** | `© Overture Maps Foundation`; preserve the Foursquare NOTICE (*"Copyright 2024 Foursquare Labs, Inc."*) | Stripping attribution/NOTICE is the only breach path. **The good news here — the biggest POI layers are not ODbL** |
| 13 | Mechanic shops 11,759 | Overture Places, truck categories only | As row 12 | **Yes-with-obligation** | As row 12 | As row 12 |
| 13a | └ hours / chain badge | All The Places `data.alltheplaces.xyz` | **CC0-1.0**, verified today | **Yes** | None | Residual, non-copyright: ATP's output is itself scraped from brand sites; its CC0 waiver covers its own output, not an upstream site's ToU |
| 13b | └ NY/NJ licence numbers | State licence registries | **Unverified** — ToU not retrieved | **Unverified** | Unknown | A wrong licence status beside a named business is a defamation-adjacent claim |
| 13c | └ coverage denominator | Census CBP 2022 | US Govt work | **Yes** | Attribution requested | — |
| 13d | └ OSM corroboration flag | `osm.*` | ODbL-derived boolean | **Yes-with-obligation** | §2 | Contained by design — only the flag lands, asserted by a test |
| 14 | Fuel stations **108,056** (`osm.fuel_stations`) | Geofabrik `us-latest.osm.pbf` → `osm_extract.py` | **ODbL-1.0** | **Yes-with-obligation — the obligation is the problem.** §2 | Attribution **plus** share-alike | §2 |
| 15 | Weigh points 3,773 · rest areas 5,452 · truck repair 763 · OSM ways | Same PBF / Overpass | **ODbL-1.0** | **Yes-with-obligation** | As row 14 | §2 |
| 16 | AAA daily state diesel (`scripts/aaa_prices.py`) | **Scraped** from `gasprices.aaa.com` | Publisher's terms, quoted in-repo: *"limited licence … for personal, non-commercial use only"*; *"may not reproduce, distribute … modify, **archive** or otherwise exploit"*; *"Any commercial use or exploitation … is strictly prohibited."* © OPIS/AAA | **No** | None available | **The hard stop.** Storing = "archive", serving = "distribute", the product is commercial. Exposure is contract/ToU (potentially CFAA-adjacent) — **independent of copyright in facts**, so *Feist* does not rescue it, and it surfaces only after the client is live |

**Credit to the build:** the repo already knew — `aaa_prices.py` is off behind
`AAA_PRICES_ENABLED=1`, retention is a 30-day window, and `README.md` says *"Remove the timer
before serving the platform to anyone else."* The control exists; the missing piece is a build gate
making it impossible to ship enabled.

---

## 2. The ODbL question — the one issue that can force re-architecture

`osm.*` is **ODbL-1.0**. Verified today against `opendatacommons.org/licenses/odbl/1-0/`:
**§4.5(b)** creating a **Produced Work** is exempt from share-alike · **§4.4** *"Extraction or
Re-utilisation of the whole or a Substantial part of the Contents into a new database is a
Derivative Database"*, and one publicly used must be ODbL or compatible · **§4.6** if the
Derivative Database is publicly used, recipients must be offered, machine-readable, **either the
whole Derivative Database or a file documenting all alterations**.

Two use patterns that look identical to a product manager and are not:

| Use pattern in the client's product | Character | Obligation | Proprietary-compatible? |
|---|---|---|---|
| A rendered map/route screen, a corridor summary, "3 mechanics within 5 miles", a computed cost floor | **Produced Work** | Attribution notice only (§4.3) | **Yes.** Proprietary code and database stay closed. |
| An endpoint returning OSM records as JSON (today's `/v1/fuel`), a bulk/CSV export, a feed a client's customer can pull | **Re-utilisation → Derivative Database, publicly used** | ODbL on that database + §4.6 offer of the database or an alterations file | **No, not silently.** This is the clause that reaches into the client's product. |

The system is **already architected for the right answer** — `schema_phase2.sql` isolates ODbL in
the `osm` schema, `core.*` takes Overture + Foursquare attributes only, `fuel_enrich.py` joins at
query time via `ov_place_id` instead of copying, and `test_fuel_verify.py` + `verify_claims.py`
assert it. **Containment holds at rest; the serving boundary is undecided** — `/v1/fuel` today
emits ODbL records over an API, i.e. the right-hand row.

**Design-forcing choice (`DEC-1200`, open):** (a) ODbL layers consumed **as Produced Works only** —
rendered/aggregated, never emitted as records, never exported, `osm.*` never crosses the API
boundary; or (b) publish the ODbL-derived layer under ODbL with a §4.6 alterations file; or (c)
drop OSM and re-source weigh points / rest areas / truck repair. **(a) is the only option that
keeps both the layers and the client's proprietary posture — and it is an architecture constraint,
not a policy sentence.**

---

## 3. Requirements

| ID | MoSCoW | Requirement | Acceptance condition | Source |
|---|---|---|---|---|
| BR-1200 | Must | Every response, screen, export and document from an attribution-bearing source carries that source's notice | Automated check per payload; `smoke_endpoints.py` does this for ODbL — extend to Overture/Foursquare/ATP/Caltrans/NWS | §1 |
| BR-1201 | Must | Every stored record carries machine-readable licence + attribution + provenance | Any row returns source id, licence id, attribution, `observed_at` | Derived |
| BR-1202 | Must | ODbL stays structurally isolated; no ODbL attribute value reaches a permissive table | Existing invariant test runs in CI and blocks release | `schema_phase2.sql`, `verify_claims.py` |
| BR-1203 | Must | The ODbL **serving** boundary is enforced in code per `DEC-1200` | (a) no endpoint/export returns `osm.*` rows, asserted by test; or (b) a §4.6 alterations file is published and reachable | §2 |
| BR-1204 | Must | No source forbidding commercial use exists in a client-facing build | Build gate fails if `aaa_daily` (or any non-commercial-flagged source) is enabled, in schema, or holds rows | §1 r16 |
| BR-1205 | Must | A licence register — source, URL, licence, verified-on date, evidence excerpt, obligation — ships to the client | 100% of live sources; no entry older than the BR-1206 window | Derived |
| BR-1206 | Should | Terms are re-verified on a cadence and the evidence **archived** (dated copy), not linked | Every source has an in-window evidence artefact | Derived |
| BR-1207 | Must | Advisory layers show the upstream's own limitation verbatim (NTAD not-for-enforcement/navigation; EIA regional weekly ≠ pump price; Caltrans/NWS no-warranty) | Notice on every surface; not suppressible by a query parameter | NTAD metadata |
| BR-1208 | Must | Every upstream credential/identity (EIA key, NWS UA + contact) belongs to the operating client | No personal key or contact string in client deployment config | §1 r5, r11 |
| BR-1209 | Should | Every **Unverified** layer is flagged off by default and unsellable as a contracted feature until cleared | Flag exists; feature list excludes it | §1 r6-9, r13b |
| BR-1210 | Must | The client agreement sets per-layer downstream rights (sublicence, resale, export) and passes upstream obligations through | Data-terms schedule matches the BR-1205 register line by line | **counsel** |
| NFR-1200 | Must | Notices survive caching, pagination, partial responses, error paths | Contract test on every response shape | Derived |
| CON-1200 | — | Upstream rate limits/throttles (NWS, ArcGIS, S3) cap the freshness a client SLA can promise | — | §1 |
| CON-1201 | — | Four WZDx and three Caltrans feeds are keyless, contractless, revocable at will | — | §1 |

**Risks (P/I).** `RSK-1200` scraped AAA reaches a client build (L/H — ToU claim by OPIS/AAA,
remediation post-go-live) · `RSK-1201` ODbL records leave via endpoint or export and pull §4.6 onto
the client's own database (**M — `/v1/fuel` already does this** /H) · `RSK-1202` Unverified state
feeds contracted as features, then cut off (M/M) · `RSK-1203` attribution stripped in a client-side
redesign, silently (M/M) · `RSK-1204` Boss's personal EIA key ships (M/L-M) · `RSK-1205` advisory
routing presented as legal compliance — the largest *non-licence* exposure, landing on A8's
negligent-selection surface (M/H).

**Assumptions.** `ASM-1200` client product is proprietary/closed `[conf: high]` · `ASM-1201`
delivery is a hosted service, not a database handover `[conf: low — materially changes §2]` ·
`ASM-1202` today's Overture terms apply to release 2026-06-17.0 `[conf: med]` · `ASM-1203` no
upstream changed terms since the registry's 2026-07-22/24 checks `[conf: med]`.
`[NEEDS INPUT: hosted API, embedded dataset, or a database the client takes possession of? The ODbL
answer differs in all three.]`

**Edge cases.** `EC-1200` upstream changes terms mid-contract — no watcher exists · `EC-1201` the
client's customer bulk-exports through the client → second-order ODbL re-utilisation, unowned ·
`EC-1202` an ODbL layer used to *correct* a permissive record → licence mixing the current test
misses · `EC-1203` a keyless state feed adds a key → live-ops layer dies · `EC-1204` a future
Overture release adds OSM-sourced places → today's finding inverts; re-verify per release ·
`EC-1205` a stale/wrong state licence record shown beside a named business.

---

## 4. Safe to build on now

NTAD truck routes (454,830) · tunnels (580) · truck parking (1,915) · FHWA NBI bridges (629,710) ·
EIA prices (17,089, on the client's own key) · NWS alerts (with UA + contact) · Overture
`core.fuel_places` (151,767) · Overture `core.mechanic_shops` (11,759) · All The Places hours/chain
(CC0) · Census CBP. **"Safe" means safe *with* BR-1200/1201/1207 — never bare.**

## 5. Needs a licence decision before it can be sold

`osm.fuel_stations` (108,056) · `osm.weigh_points` (3,773) · `osm.rest_areas` (5,452) ·
`osm.truck_repair` (763) · OSM ways — **all blocked on `DEC-1200`**; buildable today as Produced
Works, not emittable as records without accepting §4.6. · WZDx AZ/KS/MN/WA — **blocked on a written
term or grant, per state.** · Caltrans D02/D03/D09 — usable if counsel accepts `conditions-of-use`
reaching the `cwwp2` feed. · NY/NJ licence registries — blocked on ToU.

## 6. Drop or replace

**AAA daily diesel (`scripts/aaa_prices.py` + `truckintel-aaa-prices.timer`) — remove from the
client build entirely.** Personal/non-commercial only; "archive" and "distribute" both named;
commercial use "strictly prohibited". Replace with EIA regional weekly (already the source of
record) or a paid **OPIS** licence if daily station-level price is a contracted feature. Nothing
else free and lawful publishes US pump-level prices.

## 7. Handoff — requires qualified counsel licensed in the relevant US jurisdiction

1. Whether serving `osm.*` records through an API is public use of a **Derivative Database**
   (ODbL §4.4/§4.6) or a **Produced Work** (§4.5(b)) — `DEC-1200` turns on this.
2. Whether the client's architecture triggers §4.6 disclosure of its own database.
3. Whether `dot.ca.gov/conditions-of-use` reaches the `cwwp2.dot.ca.gov` machine feed.
4. Redistribution rights for the AZ/KS/MN/WA WZDx feeds and NY/NJ registry ToU — state by state;
   no federal §105 shortcut exists.
5. Residual exposure from the historical AAA collection and the scope of any deletion.
6. Whether an API registration ToS (EIA) binds independently of public-domain status.
7. The client agreement's data-terms schedule, warranties and indemnities (BR-1210) — including
   whether Boss can warrant these layers at all.
8. CFAA / contract exposure from any scraped source, separate from copyright.

---

**Counts:** BR ×11 · NFR ×1 · CON ×2 · RSK ×6 · ASM ×4 · EC ×6 · DEC ×1 (open) ·
**Unverified ×7** (WZDx AZ, KS, MN, WA · Caltrans feed-scope · NY/NJ registries · EIA API-key ToS).

General awareness only. Not legal advice. Qualified counsel required for binding decisions in your
jurisdiction.
