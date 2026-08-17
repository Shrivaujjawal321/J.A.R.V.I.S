# Truck-Intel Phase 2 — Trackable Checklist

**Live tracker.** Jarvis updates this file at every state change. Boss can read it
any time to see exactly where the work stands, without asking.

- **Started:** 2026-07-23 09:00 IST (session 3 — post-reboot resume)
- **Mandate:** finish Phase 2 (MASTER_PLAN §10 — ingestion breadth + quality layer)
- **Legend:** ⬜ not started · 🔨 in flight · ✅ done · ⛔ blocked · ⏸️ human-gated (cannot do autonomously)
- **Rule:** an item flips to ✅ only with **evidence** in the Evidence column — a row
  count, a test count, a commit sha. Never on "should be fine".

---

## A. Blocking path — US OSM ways backfill

| # | Item | Status | Evidence / note |
|---|---|---|---|
| A1 | Postgres `truckintel-pg` back up after reboot | ✅ | crash-recovery completed; `pg_isready` OK 09:10 |
| A2 | Bank the in-flight gate-2 + osm-ways-hardening work | ✅ | commit `0e1ba42` |
| A3 | Clear stale/unusable workdir (partial 15.6 GB node index) | ✅ | 277 G free after clear |
| A4 | Relaunch US ways pass, detached + `--keep-workdir` | ✅ | PID 33137, workdir `…-run1293`, unbuffered log |
| A5 | **Phase A — osmium scan completes** (~3-4 h) | 🔨 | watch `data/us-osm-ways-rerun.log`; spool `ways.ndjson.gz` > 0 |
| A6 | **Phase B — COPY + snapshot_swap lands** | ⬜ | headroom guard runs first; `--from-spool` replay if it fails |
| A7 | Verify US `osm.ways` row count + class allow-list sanity | ⬜ | currently **109,777 = Delaware-only**; expect tens of millions |
| A8 | Confirm `observed_at` = PBF replication timestamp (not load date) | ⬜ | honesty rule — must not be today's date |

## B. Businesses backfill (serialized — starts only after A6)

> Deliberately **not** run concurrently: simultaneous heavy IO is exactly what
> exhausted the disk and destroyed the 3.4-hour pass this morning.

| # | Item | Status | Evidence / note |
|---|---|---|---|
| B1 | Full US Overture places pull | ⬜ | |
| B2 | Full US FSQ pull (source.coop anon mirror, frozen 2025-02-06, labeled) | ⬜ | HF_TOKEN not needed — worked around |
| B3 | **Measure conflate pair volume before running it** | ✅ **tool ready** (`9bb7bdb`) | `scripts/conflate_gate.py` + 6 tests. Streams the real scorer, spills gray ids to a TEMP TABLE (O(1) RAM), reports distinct gray ids = true array-param size, verdict `run_as_is`/`spill_first`. Verified live: honestly refuses today (`_bo=3000, _bf=0`). **Run it for real after B1+B2.** |
| B4 | Conflate — as-is if pairs+gray < ~5M, else spill gray ids to TEMP TABLE | ⬜ | **UNPROVEN at scale**: NYC proof was Overture-only, cross-source pairing never ran at volume |
| B5 | `/v1/places` US-wide (currently bounded NYC, 2,981 rows) | ⬜ | |

## C. Verification + close-out

| # | Item | Status | Evidence / note |
|---|---|---|---|
| C1 | Full test suite green **with DB up** | ⏸️ **deferred to after A6** | Suite + OSM scan fight for the same disk. Measured: `count(*) from core.bridges where source_id=$1` sat 5+ min in `DataFileRead`/`BufferIO`. Same IO-contention mistake that killed this morning's pass — so the suite waits, the pass gets the disk. (DB-down run of 329 pass/89 skip is NOT the trustworthy number.) |
| C2 | Smoke-test every Phase-2 endpoint | ⬜ | bridges · parking · places · tunnels · fuel · live/closures · live/chain-controls · meta/coverage |
| C3 | Freshness / coverage / status page sane | ⬜ | `make freshness`, `make status-page` |
| C4 | Commit + update MASTER_PLAN §10 status | ⬜ | |
| C5 | Update Jarvis memory (`project-truck-intel-platform`) | ⬜ | |

## D. Human-gated — ⏸️ cannot be completed autonomously (documented honestly, not silently dropped)

| # | Item | Why blocked |
|---|---|---|
| D1 | Keyed state 511 feeds | need per-state API keys + DAA approvals |
| D2 | TPIMS live parking availability | needs registration emails |
| D3 | ~20 additional WZDx feeds in `data/wzdx_proposed/` | license review = legal judgment, not code |

---

## Live log (newest last)

- **09:05** — Resumed. Found Phase 2 incomplete: US ways backfill dead twice (05:41 `DiskFull` + workdir destroyed by old failure path; 08:53 kernel-upgrade reboot killed the retry at ~2.5 h). `truckintel-pg` down.
- **09:10** — PG recovered and up. `osm.ways` measured at 109,777 — still Delaware-only, US ways have never landed.
- **09:12** — Committed `0e1ba42`: gate-2 WKT geometry validation (closes the bypass that let unvalidated LineString/Polygon rows reach `core`) + `--from-spool` phase-B replay + disk-headroom guard.
- **09:13** — Cleared stale workdir; relaunched US ways pass detached (PID 33137). RSS flat at 64 MB as designed.
- **09:31** — Full suite relaunched detached: the DB-up run exceeds 10 min (the 89 previously-skipped DB tests now actually execute), so it needs to run outside the foreground timeout.
- **09:38** — Suite stalled at 34 tests. Diagnosed: **not a lock** — `pg_stat_activity` showed the bridges count query parked in `DataFileRead` / `BufferIO`. Pure disk contention with the OSM scan. Suite terminated and its orphaned backends killed to give the pass its IO back. C1 deferred behind A6 by design, not skipped.
  - Checked while there: `core.bridges` has no index on `source_id`. **Not filing this as a bug** — bridges are single-sourced (NBI), so the predicate matches ~every row and a seq scan is the right plan. The slowness was contention, not a missing index. Re-measure after A6 before drawing any conclusion.
- **10:05** — Wait time spent on zero-IO work: built **B3, the conflate decision gate** (`9bb7bdb`). Caught a real bug in my own first draft — it opened two simultaneous COPY streams on one connection, which Postgres cannot do (a connection is in COPY mode for one statement at a time, and a named cursor's FETCH cannot interleave with it). Rewritten to flush bounded batches between fetches, and pinned by a test that shrinks the batch so the flush path runs repeatedly.
- **10:10** — Confirmed the cross-source path really is unexercised: `staging.fsq_places = 0 rows`. The gate refused to emit a verdict rather than reporting a comfortable zero.
