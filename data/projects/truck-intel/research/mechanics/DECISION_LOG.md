# Mechanic Discovery — Decision Log

Decisions locked by Boss 2026-07-23 after reading RESEARCH_BRIEF.md.
Every decision cites the brief section that justifies it. Where Boss chose against a
brief recommendation, that is recorded as his call.

## LOCKED (blocking decisions — build cannot start without these)

### D1 — Route spine = NTAD National Network, NN-only  ✅ (brief §2, §11.1)
Boss's words: **"i want only truck routes."** → Option A.
- Source: BTS/FHWA NTAD **National Network** ArcGIS FeatureServer.
- Filter **`NN > 0`** at ingest → 453,529 truck-designated polylines. The 24,169 `NN=0`
  rows are carried in the same layer but are NOT on the National Network — they are
  **never published as truck routes** (per §11.4 trap; retained separately only if D12 says so).
- Legal basis 23 CFR 658 / STAA 1982. License = US Government work (17 U.S.C. §105), keyless.
- Primary key = source `ID` (478,999 distinct, verified unique). NOT `ROUTEID` (state-scoped,
  collides) and NOT lane-1's proposed composite (444801/444802 collide).
- Route name = `LNAME` where present, else synthesized `TRIM(SIGN1)` / `SIGNT1`+`SIGNN1`
  (`LNAME` blank on 411,754 rows).
- Uses the repo's existing `kind: arcgis` connector — near-zero new code.
- **This is the truck-designated network as a matter of law, not a filter applied to
  general roads.** Honors the hard scope rule [[feedback-truck-routes-only]].
- WHY not B/C: B (NN+NHS+FAF5) lands incrementally later for fresher geometry + restrictions;
  C (NHFN 12,989) is a funding network, only ever a throwaway pipeline test.

### D3 — Platform is PUBLIC  ✅ (brief §5, §11.3)
Boss chose public (external users), against the internal-only ODbL shortcut.
Consequence, accepted knowingly:
- OSM share-alike (ODbL §4.x) applies. All OSM-derived data (junctions, hours,
  service:vehicle:* capability tags, the ~700 OSM truck shops) stays in the `osm.*`
  schema, joined at query time, **never merged into `core.*`**.
- `core.businesses` stays OSM-free: `present_in <@ ARRAY['overture','fsq']` holds.
- `core.route_shops` link table lives in `core.*` ONLY because the spine is federal
  public-domain geometry (D1). If the spine were ever OSM, it would move to `osm.*` (§11.14).
- Triggers D4.

### D4 — Ship the ODbL §4.6 offer for osm.*  ✅ (brief §5, §11.4)
- Add a machine-readable dump endpoint + `/v1/meta` link for the `osm.*` mirrors.
- Backfill `ops.sources.license` for the OSM sources (currently NULL → `/v1/meta` wrongly
  reports the only share-alike source as "unknown").
- Closes a **live, present-tense** non-compliance: `/v1/fuel` already serves 108,056
  systematically-extracted ODbL rows with no §4.6 offer. This is existing tech debt this
  project must not inherit silently.

### D5 — Buffer = 5 km straight-line  ✅ (brief §7, §11.5)
- `ST_DWithin(geom::geography, route::geography, 5000)` — geography, exact.
- Labelled "straight-line (as-the-crow-flies)", NOT drive distance. 5 km is also the
  measured-optimal chunk scale. Drive distance only later as a separate field if Valhalla lands.

## DEFAULTS TAKEN (non-blocking — brief recommendations adopted unless Boss objects)

- **D2** Geofabrik/Overpass robots.txt → documented narrow exception in the source registry,
  rate-capped, contact UA. Never fetched silently. (§11.2)
- **D6** Publish `LIKELY_TRUCK` band by default, machine-readable + filterable. (§11.6)
- **D7** Surface general `auto_repair` ranked strictly BELOW truck-specific, never relabelled. (§11.7)
- **D8** FSQ HuggingFace gate → measure one-state coverage delta first; skip/ungated-mirror
  defensible because FSQ is largely already inside Overture (independence finding). (§11.8)
- **D9** Overture `categories` → `taxonomy` migration now (categories removed Sept 2026);
  never `basic_category` (destroys truck signal). (§11.9)
- **D10** DROP `average_rating` / `review_count` / `review_summary` / `whatsapp` — no free or
  paid legal path. Record reason in schema comment + `forbidden_sources.yaml`. (§11.10)
- **D11** `observed_at` for NN spine = **2018** (row `YEAR`); other candidate dates → `props`. (§11.11)
- **D12** Retain `NN=0` rows in a separate `core.non_nn_routes` flagged
  `not_on_national_network` (lets the platform answer "is this road truck-legal?" = definitive no). (§11.12)
- **D13** Pin TIGER 2025, vintage encoded in `source_id` (`census_geo_2025_county`). (§11.13)
- **D14** `core.route_shops` in `core.*` (conditional on D1 = federal PD, which holds). (§11.14)

Boss: if you disagree with any DEFAULT, say so and I'll flip it — otherwise I build with these.
