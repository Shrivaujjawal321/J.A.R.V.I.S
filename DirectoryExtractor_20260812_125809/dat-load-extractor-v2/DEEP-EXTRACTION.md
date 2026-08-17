# Deep Load Extraction Engine (v3.0.0)

v2 read the search-results table. v3 also reads everything *behind* each row —
the details drawer, its tabs and accordions, the route panel, the company
profile, and the DAT Directory office page — and merges it all into one record
per load.

## Files

| File | World | Role |
|---|---|---|
| `net-capture.js` | MAIN, `document_start` | Mirrors dat.com fetch/XHR JSON out to the extractor. Read-only: responses are cloned, never modified or blocked. |
| `deep-extract.js` | isolated, before `content.js` | The engine. Exposes `window.__DAT_DEEP__`. Harvesting, traversal, normalization, merge, export flattening. |
| `content.js` | isolated | Unchanged v2 pipeline **plus** a deep pass inside `enrichLoadsWithDirectoryData`. |
| `server.py` | — | `DEEP_EXPORT_COLUMNS` mirrors `DEEP_COLUMNS` so the autopilot exports match the manual ones. |

## Pipeline

```
search → scroll + extractLoadFromRow (v2, unchanged)
       → per load:  open details drawer
                    ├─ harvest visible label/value pairs
                    ├─ click every safe revealer (tabs, accordions, VIEW ROUTE,
                    │  company chevron) and re-harvest — recursively, depth 3
                    ├─ positional parsers: rate card, trip stops, company card
                    └─ merge any matching API payload from net-capture
       → directory tab (per company, cached): full office profile
       → merge → normalize → completeness metadata
```

Merge rules: first non-empty value wins; a real value is **never** overwritten by
an empty one; unknown fields land in `additionalData`; nothing is invented — a
field that was not found stays `null`.

## Safety

`classifyInteractive()` is a deny-list-wins classifier. It will click tabs,
accordions, `aria-expanded="false"`, panel headers, and "VIEW ROUTE"/"more
details" style controls. It will **never** click book, bid, offer, call, connect,
email, send, save, delete, report, share, print, export, submit, apply, or any
anchor that navigates or opens a tab. Directory links are handled by the existing
dedicated pipeline, not by generic traversal.

## Output

- **CSV / XLSX** — the 30 v2 columns first (positions unchanged), then 107 deep
  columns. Deep columns appear only when at least one load carries deep data, so
  deep-off output is byte-identical to v2.
- **JSON** — adds `records[]`: `{ load: { id, summary, details, route, truck,
  company, contact, office, rate, additionalData }, extraction: {...} }`.
- **TXT** — per-load RATE / ROUTE / TRUCK / LOAD / COMPANY / CONTACT / OFFICE /
  ADDITIONAL DATA / EXTRACTION blocks.

Every load carries `extraction.status` — `complete` | `partial` | `failed` —
plus `sectionsVisited`, `sectionsFailed`, `linksVisited`, `fieldsExtracted`,
`retries`, `warnings`, `errors`. One load failing never stops the batch.

## Controls (popup / side panel)

Deep Extraction **On/Off**, traversal depth (1-6), max reveals per load (0-80),
retries (0-3). Live progress board: found / processed / complete / partial /
failed / fields / retries plus the sections visited. **Load Inspector** shows any
single load's captured groups and its extraction metadata — use it to verify
coverage against what the browser shows.

## Performance

Traversal clicks only real controls (semantic elements or `cursor: pointer`), so
a typical drawer costs ~2 reveals and ~1.4 s rather than ~26 reveals and ~11 s.
Readiness is MutationObserver-based with a floor, never a fixed sleep. Traversal
stops early after 4 consecutive reveals that mutate the DOM but add no fields.

## Verification status

Verified against faithful mock DOMs rebuilt from the live screenshots (drawer,
directory profile, and a 3-row search page driven through the real `content.js`),
covering: field capture, per-load isolation, failure isolation, merge safety,
CSV/XLSX/JSON/TXT export, network merge, and click safety.

**Not yet run against live DAT One** — that needs a logged-in session. On the
first live run, open the Load Inspector and compare one load against the browser;
anything missing will show up as an unmapped entry under `additionalData` rather
than being lost.
