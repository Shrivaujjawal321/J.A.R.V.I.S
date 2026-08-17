# Truck mechanic layer — enrichment pass, 2026-07-27

Closes every open item in `DEEP_DIVE_2026-07-24.md` §9. That document listed
five priority actions and predicted their effects; this one records what was
built, what was measured, and — in two places — where the prediction was wrong
and the measurement won.

Nothing here supersedes `RESEARCH_BRIEF.md` §5 (legal rulings) or §3 (source
ledger). It adds four sources the ledger already permitted but the pipeline had
never used.

---

## 1. Bottom line

All five deep-dive actions are done, plus the HTML deliverable the original
brief promised and the July run never produced.

| # | Deep-dive action | Status |
|---|---|---|
| 1 | Fix the independence count | **Done** — and the proposed fix turned out to be insufficient; see §2 |
| 2 | CBP per-state denominator | **Done** — the question it was raised to answer is now answered, §4 |
| 3 | OSM `shop=truck_repair` extraction | **Done** — §5 |
| 4 | AllThePlaces chain hours | **Done**, with a correction to the deep dive's premise — §6 |
| 5 | NY/NJ/CT licence join | **Done for NY/NJ. CT dropped with cause** — §3 |

Two findings are worth Boss's attention on their own:

1. **Overture supplies no cross-corroboration at all for this dataset.** Not
   "less than it appeared" — none. Every one of the 11,759 shops traces to
   exactly one real contributor. §2.
2. **The plains states are genuinely empty, not under-listed.** SD, MT, NE, KS,
   WY and MS all show normal capture rates against the Census denominator. The
   state that is actually under-listed is **New York**. §4.

---

## 2. Independence: the fix the deep dive proposed was not enough

The deep dive diagnosed the inflation correctly — `Overture` and
`Overture-signals` are one organisation's two pipelines — and proposed
collapsing them to one vote, predicting `n_independent` would become 1 for
8,565 rows and 2 for 3,193.

**Implemented and measured, that collapse alone leaves:**

| `n_independent` | shops |
|---|---|
| 2 | 11,551 |
| 3 | 208 |

Still no discrimination. The reason is one level deeper than the deep dive
looked. Every row also carries a `meta` or `Microsoft` name, so collapsing only
the Overture pair still leaves two "organisations" on almost every row.

**The actual error is treating the aggregator as a witness.** Overture is a
conflator, not a collector. `Overture` and `Overture-signals` are the
aggregator's own labels on a record it assembled; they attest to no independent
survey of the premises. The collection was done by the member who donated the
record — Meta (owner-maintained Pages) or Microsoft (Bing listings).

With aggregator labels excluded from the count:

| `n_independent` | shops |
|---|---|
| 1 | 11,551 |
| 2 | 208 |

**Every US truck shop in this dataset has exactly one real contributor.**
Source agreement inside Overture carries no information here whatsoever, and
independence must come from outside it. That is precisely what §3 and §5 are
for — they are no longer "nice to have", they are the only corroboration
available.

### What `verified` now means

`verified` requires **≥2 independent organisations** on top of the existing
structural checks. Since a plain row scores 1, only a licence or OSM match can
reach the bar.

| Status | Before (2026-07-24) | After |
|---|---|---|
| verified | 10,794 (91.8%) | **202 (1.7%)** |
| probable | 934 (7.9%) | 11,342 (96.5%) |
| unverified | 31 (0.3%) | 215 (1.8%) |

This is the outcome the deep dive predicted in kind ("a large share moves from
verified to probable, which is the honest outcome, not a regression") and
understated in degree. The 91.8% figure was never a measurement of anything;
it was every row scoring full marks on a component that could not fail.

`probable` is not a demotion in usefulness — the 0-100 confidence score still
ranks within it, and it is now driven by signals that actually vary
(Overture's own confidence, phone/state agreement, coordinate sanity).

The rule is pinned by tests in `tests/test_mechanic_enrich.py` so it cannot
regress back into flattery.

---

## 3. State licences — NY and NJ joined, CT dropped with cause

`core.mechanic_licences` mirrors the registries; the join stamps
`licence_id` / `licence_expiry` / `licence_rule` onto shops. Four match rules,
strongest first, first hit wins, each recording which rule fired.

| Rule | Matched |
|---|---|
| `name_zip` — normalised name + ZIP | 71 |
| `name_city` — normalised name + city | 2 |
| `geo_name` — within 150 m + leading-6-char name agreement | 115 |
| `addr_zip` — normalised street address + ZIP | 44 |
| **Total** | **232** of 558 shops in NY+NJ |

`addr_zip` was added after the first run measured 188: registries hold the
*legal* name ("BROADWAY GARAGE OF BETHPAGE INC") where Overture holds the
*trading* name ("Broadway Garage"), so the street address is the second
identifier both sides publish. It added 44 matches (+23%).

Per state: **NY 176/311 (57%)**, **NJ 12/247 (5%)**. The NJ rate is not a bug —
`t6tk-mr48` is an *emission repair facility* register, which barely intersects
heavy-truck repair, and NJ publishes no coordinates so the geographic rule
cannot fire there.

### CT is deliberately absent

The deep dive listed CT `apne-w8c6` ("Licensed Automobile Dealers And
Repairers") at 138 rows. Measured 2026-07-27, **all 138 carry
`license_type = 'MANUFACTURER LICENSE'`** — the published extract contains no
repairers at all despite its title. Including it would contribute zero matches
while implying CT coverage we do not have.

### Honesty rule encoded in the schema

`licence_verified` is NULL outside NY/NJ (no registry consulted), FALSE inside
them when no match was found (looked, did not find), TRUE on a match. A
non-match is **not** evidence a shop is unlicensed. An expired licence buys no
independence vote — it says the shop existed, not that it still trades.

---

## 4. Coverage: the plains states are really empty; New York is the thin one

`core.mechanic_coverage` holds per-state shops, on-route shops, the Census CBP
denominator, capture rate, route-miles-per-shop and a verdict.

**The Census DATA API now refuses keyless requests** (HTTP 302 → "Missing Key",
measured 2026-07-27), so this reads the **bulk state file**
(`cbp22st.zip`, 11.8 MB) instead — same agency, same numbers, no key, no
account. The `lfo` (legal form of organisation) column must be filtered to `-`
or every state is double- or triple-counted; that filter has its own test.

National: **11,732 truck shops / 84,101 CBP establishments in NAICS 811111 =
13.9% capture.** The 84,101 reproduces the deep dive's figure exactly.

The deep dive posed the question as a fork — real scarcity or data thinness?
The answer is both, in different states:

| State | Shops | CBP 811111 | Capture | Route mi/shop | Reading |
|---|---|---|---|---|---|
| NY | 311 | 5,346 | **5.8%** | 7 | **under-listed** |
| AK | 15 | 218 | 6.9% | 72 | under-listed |
| SD | 80 | — | normal | **80** | genuinely thin |
| MT | 91 | — | normal | 74 | genuinely thin |
| NE | 122 | — | normal | 63 | genuinely thin |
| KS, WY, MS | — | — | normal | 50-62 | genuinely thin |
| CA | 832 | 9,705 | 8.6% | 5 | ok |

**Product consequence.** In SD/MT/NE/KS/WY/MS the supply really is that sparse,
so the interface must surface **distance to the next shop**, not a count — "3
mechanics near this route" is the whole supply for 240 miles and reads as
reassurance when it should read as a warning. In NY the count is an artefact of
listing coverage and a second source is what fixes it.

That NY is simultaneously the best-licensed state (176 matches) and the
worst-covered one is not a contradiction: the licence registry proves the shops
exist; Overture simply does not list them.

---

## 5. OpenStreetMap — the only independent truck-specific source

`osm.truck_repair` holds **763 US truck/trailer-repair POIs**, matching
`shop=truck_repair` plus the capability tags
`service:vehicle:truck_repair=yes` / `service:vehicle:trailer_repair=yes` that
sit on shops whose primary tag is `car_repair`. Overture exposes neither.

**326 shops (2.8%) are now OSM-corroborated**, and 34 gained opening hours from
OSM — the only independents in the whole dataset that have hours at all.

### The transport was changed mid-flight, and the numbers say why

It was first built as a fourth kind in `scripts/osm_extract.py --job pois`,
which walks the 12 GB US PBF. That ran for **2 h 21 m** and was still going,
with the node-location index past 1 GB, the page cache thrashing on a 15 GB
laptop, and 1.1 GB pushed into swap. Boss reported the machine had become
unusable — a fair complaint, and the right moment to question the approach
rather than wait it out.

Measured alternative, same three tags, same data:

| | PBF pass | Overpass API |
|---|---|---|
| Wall clock | 2 h 51 m (prior run, `ops.source_runs` 981) | **~2 min** |
| Local I/O | 12 GB read + >1 GB node index | **357 KB** |
| Rows produced | 763 | **763** |
| Vintage | weekly snapshot (21 Jul) | **minutes old** |

Identical output, because 763 is simply all the truck-repair tagging that
exists in the US. The PBF pass was grinding 12 GB to extract a 357 KB answer.

So the local job was killed and `scripts/osm_overpass.py` written in its place.
The rule it encodes: **choose the transport by result size, not by habit.** A
national layer of a few thousand objects is an API query; a national layer of a
hundred thousand — `amenity=fuel`, 108k rows — stays a bulk file, because no
public API should be asked for that. Both paths remain in the repo, each
documented with which case it is for.

The Overpass path retries with backoff across three independently-operated
mirrors, and that earned its keep on the first live run: two 504s from the
primary before it answered. Only transient codes (429/502/503/504) retry — a
400 means our query is wrong and hammering three hosts with it would be rude.

It refuses to load at all if the response carries no
`osm3s.timestamp_osm_base`: a row with an invented vintage is worse than no row.

Implementation notes worth keeping:

- **Repair is an *overlapping* layer, not a fourth branch of `classify()`.** A
  truck stop can be both a fuel station and a repair shop; folding repair into
  the existing exclusive classifier would have silently moved those sites out
  of `osm.fuel_stations` and shrunk a working layer. `is_truck_repair()` is
  evaluated independently and an object may land in both tables.
- **`--only` was added to the pois job.** The pass still reads every kind in
  one walk of the PBF, but publishing can be restricted to selected tables.
  Two reasons: refreshing the repair layer should not force a re-swap of three
  unrelated tables, and — see §7 — a swap of `osm.fuel_stations` is currently
  blocked by an object outside this repo's control.
- ODbL containment is unchanged (brief D3): OSM data stays in `osm.*`. What
  crosses into `core.mechanic_shops` is a **match flag** (`osm_match_id`,
  `osm_match_m`), never an OSM field — plus `opening_hours`, which is filled
  from OSM only where no permissive source had it and is attributed as such.

---

## 6. Chain hours — the deep dive's premise was half right

The deep dive recommended AllThePlaces (CC0) as "the only permissive source
with `opening_hours`". Measured across the truck-relevant US spiders:

| Spider | Features | With `opening_hours` |
|---|---|---|
| `pilot_flying_j` | 724 | **679** |
| `fleetpride_us` | 378 | **374** |
| `loves_us` | 730 | **0** |
| `travelcenters_of_america_us` | 362 | **0** |
| `penske` | 1,777 | **0** |

So ATP carries hours for *some* brands, not all — and specifically **not** for
Love's/Speedco or TA/Petro, the two networks the deep dive named. The other
three spiders are still ingested for the `chain_brand` badge, because knowing a
site is a national chain is itself the reliability signal the deep dive was
after.

Result: **888 shops badged as chain sites, 375 gained opening hours.**

Matching is nearest-chain-point within 500 m with no name test — at that radius
on a truck-stop parcel the only candidate *is* the chain, and our Overture row
is often named "Speedco" where ATP says "Love's Travel Stop".

Ranking rule from the deep dive is respected: chains are **badged**, never
boosted above a closer independent shop.

---

## 7. Found, not fixed: an untracked view blocks the fuel/rest/weigh refresh

`osm.fuel_stations` cannot currently be re-published. `snapshot_swap` renames
the live table to `…_old` and drops it, and that drop fails:

```
DependentObjectsStillExist: cannot drop table osm.fuel_stations_old
because other objects depend on it
DETAIL: view lane6.v_enriched depends on table osm.fuel_stations_old
```

`lane6.v_enriched` **does not exist anywhere in this repository** — it is a
leftover from a hand-run experiment, and it now holds a hard dependency on a
production table. Any future `--job pois` full run fails on it.

It was left in place rather than dropped: it is not reproducible from source,
so dropping it destroys it, and that is Boss's call, not mine. The repair layer
was published with `--only repair` instead, which touches no table with
dependents.

**Two ways out, when Boss decides:** drop the orphan view (fast, irreversible),
or teach `snapshot_swap` to capture, drop and recreate dependent view
definitions around the swap (correct, protects every future swap, touches
shared loader machinery used by every source).

---

## 8. Still genuinely unobtainable

Unchanged from the brief §4.3 and the deep dive §8:

- Ratings, review counts, review text, photos — no free or paid *legal* path.
- Live "open now" status — nothing free publishes it.
- Actual Class-8 capability — inferable from OSM capability tags for a
  minority; otherwise a per-site website parse, not a dataset.

Opening hours have moved from "unobtainable" to "partial": 375 shops have them
from permissive sources. The rest render **"unknown"**, never "closed".

---

## 9. What changed in the repo

| File | Change |
|---|---|
| `scripts/mechanic_list.py` | `--licence`, `--chains`, `--osm-match`, `--cbp` stages; independence rebuilt; `ensure_schema()` migration path; HTML rebuilt |
| `scripts/osm_extract.py` | `repair` kind, `is_truck_repair()`, `--only`, route assignment for published kinds only |
| `sql/schema_phase2.sql` | `osm.truck_repair` |
| `truckintel/registry.py` | `osm.truck_repair` added to `SNAPSHOT_TARGETS` |
| `tests/test_mechanic_enrich.py` | 30 tests pinning independence, normalisers, OSM classifier, CBP filter |

New tables: `core.mechanic_licences`, `core.mechanic_coverage`,
`osm.truck_repair`. New columns on `core.mechanic_shops`: `source_orgs`,
`n_independent`, `licence_*`, `opening_hours`, `open_24h`, `hours_source`,
`chain_brand`, `osm_match_*`.

Deliverable: `truck_mechanics.html` + `truck_mechanics.json` in this folder.

---

## 10. Priority order from here

1. **Decide the `lane6.v_enriched` question** (§7) — it blocks every future POI
   refresh, including fuel.
2. **A second source for New York** (§4) — the licence registry proves 5,346
   repair facilities exist against our 311 shops.
3. **Distance-to-next-shop in the sparse states** (§4) — a product change, not
   a data one, and the CBP verdict column already identifies where.
4. **Extend the licence join to more states** — every additional registry is a
   genuinely independent vote, and §2 showed those are the only ones we have.
