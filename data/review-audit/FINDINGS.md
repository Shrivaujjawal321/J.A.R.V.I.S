# mySHIPR Figma — consolidated critic findings

Seven adversarial critics reviewed the file against the console, the client review
document and the design-system claims. Every finding below that is marked VERIFIED
was independently re-checked by Jarvis against the source before being accepted.

Legend: [V] verified by Jarvis · [R] rejected (critic was wrong / stale) · [ ] accepted on critic evidence

---

## A. BLOCKERS

| # | Finding | Where | Status |
|---|---|---|---|
| A1 | All 34 paint styles, 7 text styles and 55 variables are bound to ZERO nodes. Every fill is a raw hex. The guide scripts Boss to demo "select a node → see the token" — that demo fails live. | whole file | [V] |
| A2 | 34 tables are 1146–1150px wide in ALL modes inside a `clip:true` wrapper. At 375px only 345px shows → ~800px silently amputated, no scroll affordance. Console uses `overflow-x:auto`. | 84 responsive frames | [V] |
| A3 | Dashboard has 4 of the console's 9 panels. Missing: Live map snapshot, Onboarding & compliance completion, Active Alerts, Upcoming Tasks, Trips on going. | 01 Dashboard | [V] |
| A4 | Reports has 2 of 5 panels. Missing: Recurring contracts, Payment trends, Fuel spend by lane, the 4-card analytics KPI row, panel Export button, both amber notes. | 10 Reports | [ ] |
| A5 | Notification Preferences: the entire 5x3 Email/SMS/Push checkbox matrix is gone; only 5 bare labels remain. | 12.2 Settings | [ ] |
| A6 | Vehicle Types has no truck types — the 10-card TRUCK_TYPES grid is absent from a screen named Vehicle Types. | 02.6 Fleet | [V] |
| A7 | Zero overlay frames exist. No assignment wizard, no record drawers, no create forms, no bulk-upload report, no invite/create-role, no ERR-GEN error states. This is where most of the client review was actually answered. | whole file | [V] |
| A8 | Responsive frames have no sidebar, no off-canvas drawer, no scrim, and zero prototype wiring. The hamburger is drawn but wired to nothing. Prototype is desktop-only. | 84 frames | [V] |
| A9 | No Checkbox, no Bulk-action bar, no loading/skeleton state components. | library | [ ] |
| A10 | `Sidebar/Root` component exists but is instantiated 0 times — the rail is raw-copied onto 42 frames. | library | [V] |

## B. SYSTEMATIC DEFECTS (one generator fix each, not per-screen)

| # | Finding | Blast radius | Status |
|---|---|---|---|
| B1 | Note tones flattened to blue. Console: amber = warning (default), blue = info (opt-in), red = blocking. Same note is amber on one frame, blue on two siblings. | 10+ frames | [V] |
| B2 | Table headers sentence-cased, mangling acronyms: ETA→Eta, CDL→Cdl, VIN→Vin, OCR→Ocr, AWB→Awb. Console CSS is `text-transform:uppercase`. | 34 tables | [V] |
| B3 | Legend (`srcline`) chips dropped and in several cases INVENTED. 8 frames affected. This is a requirements-traceability failure, not cosmetic. | 8 frames | [ ] |
| B4 | Row action buttons dropped from ACTION/ACTIONS columns (Detention, Earnings). | 2+ frames | [ ] |
| B5 | Pagers invented on 5 tables the console never paginates (incl. the 43-row permission catalogue). | 5 tables | [ ] |
| B6 | Filter chip rows dropped where the console has them (Vehicle Types trailers, Exceptions & Safety). | 2 frames | [ ] |
| B7 | Responsive: KPI/pulse/column widths are build-time pixels (`hFix`), not FILL. Dragging a frame edge does not reflow them. | all responsive | [V] |
| B8 | The whole `@media(max-width:640px)` density block ignored — mobile uses desktop padding and type. | 42 mobile frames | [ ] |
| B9 | `KV Row` keeps a fixed 190px key column at 375px, leaving 109px for the value. Console stacks it at <=700px. | Settings/Loads mobile | [ ] |

## C. TOKEN / TYPOGRAPHY

| # | Finding | Status |
|---|---|---|
| C1 | 19 of 55 tokens invented, not read from `:root`. Console has 34 colours + 2 radii + ZERO spacing vars. `space-32`/`space-48` are not console spacing values and are used nowhere. | [V] |
| C2 | 16 of 23 console font sizes have no text style — including 32px, the largest type in the product (KPI numeral). | [ ] |
| C3 | No 600-weight text style, though 600 is the most-used weight in the console (35 rules). `Body/Small` is Regular where its dominant use is 600. | [ ] |
| C4 | All 6 gradients flattened to a single stop; 7 colours lost. The brand mark is the first thing a reviewer zooms into. | [ ] |
| C5 | 20 console colours have no token and no representation. | [ ] |
| C6 | Colour parity itself is CLEAN — all 34 `:root` colours map 1:1 with identical hexes. | [ ] |

## D. CONTENT PARITY (per-screen, from the two parity critics)

Dashboard payments row shows a Paid item the console filters out · HOS list drops a row · Drivers note text rewritten and its red tone lost · Tenders invents 3 panels + hints + an AWB field and truncates the 2nd tender · POD photo-evidence block absent · Messages is a flat text blob, not a chat · Capacity loses chip state and one category (Hazardous Materials) · RR empty state lost its only CTA · Company Profile lock badge built as a Button · My Profile lost the timezone select · Notifications feed skips 3 items silently · Roles & Users banner/note reordered away from their referents · Revenue-by-load truncated with no indicator · Route profitability shows a 5th lane that `laneStats()` does not produce.

## E. REJECTED — critic was wrong

| # | Claim | Why rejected |
|---|---|---|
| E1 | "Settings nav under-covers by 3 sub-items; 3 screens unreachable" | Critic read the stale `plugin/part1` builder. The live file was built from `subscreens/_base.js` which carries all 10 subs. Independently verified: `frames=42 allMatch`, wiring `missing=0`. A second critic corroborated the fix. |
| E2 | "No hamburger on responsive frames" | The hamburger IS drawn (`if (!desk) add(r1, tbtn(I.menu))`). The real gap is the off-canvas drawer + scrim it should open, and the wiring. Narrower than stated. |

## F. OPEN ITEMS — belong on the client list but are not on it

PTL/STL shipment types dropped and an undocumented "Multileg" added · RBAC categories 18 -> 14 with no explanation · CO-16 asset photographs have no capture surface · CO-13 reassignment remedy replaced by a hard block while the note quotes the rule · dashboard banner says 88% while the checklist on the same screen says 83%.

## G. CONFIRMED GOOD (do not "fix")

Chip tone coverage is complete — all ~48 `COL` values across 8 groups are representable, including purple · the 756 prototype arithmetic is exact and independently re-derived · SCROLL_TO self-navigation is the correct Figma workaround and targets the right node · 34 `:root` colours match 1:1 · 7 of the console's breakpoint behaviours are correctly reproduced (pulse 5-3-2, KPI 6-2-1, grid stacking, search reflow, hamburger visibility, content padding at 920, h1 22px) · the HTML console itself closes 29 of the review's 39 findings with real mechanisms.

---

## H. DOMAIN / LOGIC DEFECTS — these live in the HTML CONSOLE, not in Figma

The Figma file faithfully copied several of these, so fixing Figma alone would preserve the bug.

| # | Finding | Status |
|---|---|---|
| H1 | The FMCSA dispatch gate has FOUR different definitions. `dispatchable()` checks 5 conditions; the Dashboard donut checks 3 (drops both expiry checks); the pulse strip checks 2; the wizard checks 7. Dashboard and Reports therefore disagree about how many drivers are dispatchable, on the same data. James Carter is uninsured (CO-18) yet renders green "Dispatchable" because `dispatchable()` never reads the insurance flag — while the wizard blocks him for exactly that. | [V] |
| H2 | `confirmAssign()` sets the committed truck back to `status='Available'` — so it re-enters Idle Vehicles and the next load's truck picker. A truck can be double-booked. The picker has no "already on an open load" check. | [V] |
| H3 | A live SOS driver (Tyler Brooks, SOS-0001) still renders "On Duty · Dispatchable". `SOS` is in the driver-status catalogue but the record is never moved to it, and `blockReason()` does not know about it. | [V] |
| H4 | The driver-assignment model the client explicitly deleted has been rebuilt — `Driver Assigned` state, DRIVER selection slot in the wizard, DRIVER columns, plus a NEW permission code `drivers.assign`. Review CD-5 lists 22 locations to delete: "None is a feature to build." | [ ] |
| H5 | The wizard advertises four compliance filters it never runs: truck payload vs shipment weight, DOT annual inspection, reefer temperature-range support, CDL class compatibility. A stated filter that does not run is worse than no filter. | [ ] |
| H6 | Detention DET-0041 has an arrival timestamp in the FUTURE relative to the console's own "now", and its load is simultaneously 62% en route with a later ETA. Detention cannot accrue from an arrival that has not happened. | [ ] |
| H7 | SHP-LTL-10003 carries 44,000 lbs on a trailer rated 42,000 lbs — violating the very capacity rule the Vehicle Types note advertises. 30 pallets also will not fit a 48' van. | [ ] |
| H8 | TEL-003 "30 minutes remaining" HOS warning fires against a driver the same screen shows with 4.0 h remaining. Notifications are hand-authored instead of derived from the ELD value. | [ ] |
| H9 | Only the 11-hour driving clock is modelled. 49 CFR 395.3 has four limits — 11 h drive, 14 h window, 30-min break, 60/70 h cycle. The 14-hour clock is usually what strands a truck. | [ ] |
| H10 | Fleet utilisation counts Out-of-Service, Halt and Unavailable trucks as "engaged" (predicate is `status !== 'Available'`). Reads 63% when 2 of 8 are actually running freight. | [ ] |
| H11 | Net margin (22%) and on-time delivery (94%) are hardcoded. The same page's data gives a 16.8% GROSS margin — a net margin cannot exceed the gross it derives from. | [ ] |
| H12 | Gross revenue books un-accepted tenders, including two loads the Tenders screen still offers to Decline. | [ ] |
| H13 | Stop pickup/delivery windows render in raw UTC beside PDT timestamps on the same load — the one field where a timezone error means a missed pickup and a PEN-004 penalty. Every other timestamp goes through `ts()`. | [ ] |
| H14 | `At Delivery/Dump` is an ASSET status used as a SHIPMENT status. Not in the 16-state shipment lifecycle; renders as an uncoloured grey chip. | [ ] |
| H15 | Ten code series cited on screen resolve to nothing in the client's document pack: OPS-, TEL-, AU-0xx, CO-29/CO-30, 6A, DR-025/026, CR-022, CR-025, SH-003, FTL-01. A client tracing a citation will fail on them. | [ ] |
| H16 | Three non-expiring instruments (MC permit, FMCSA safety rating, D&A program policy) are given expiry dates and put on the CO-09 ladder. Authority and safety rating are STATES polled from FMCSA, not expiring uploads. The safety rating VALUE — the thing every shipper asks for — is never shown. | [ ] |
| H17 | DVIR is described as a pre-trip duty. Under 49 CFR 396.11 it is the POST-trip report; the pre-trip duty (396.13) is to REVIEW the last one. No defect-repair certification record exists, which 396.11(a)(3) requires before the vehicle runs again. | [ ] |
| H18 | Detention will not survive a dispute: clock starts at arrival rather than max(arrival, appointment), no rounding increment, no cap, no departure timestamp, no appointment shown. The columns present are the ones nobody argues about. | [ ] |
| H19 | Terminology drift across 11 concepts — Load/Shipment/Trip, Available/Idle/Active, Out of Service/Not serviceable/Halt, Yard/Hub/Depot/Staging/Terminal, Driver Ops/Driver Operations, Notifications/Notification Centre/Active Alerts, Salary Payout/Driver Settlement. | [ ] |
| H20 | Auction/RR/6A machinery is built throughout (Capacity screen, "as bid", "Bid accepted") despite the standing decision that auction/bidding is out of scope. | [ ] |
| H21 | Petroleum and Chemicals are declarable capabilities with no hazmat gate — they need H + N endorsements, TSA clearance and higher 49 CFR 387 insurance minimums, but only the literal category "Hazardous Materials" is gated. | [ ] |
| H22 | CDL expiry notification fires 50 days out against a ladder whose first tier is 30 days — `ladderTier()` returns null and the alert is hand-authored anyway. | [ ] |
| H23 | RBAC rebuilt at 14 categories x 5 roles against the review's 18 x 6. The Driver column is gone — but CD-4 (POD ownership) and MF-8 (AWB rights) both rest on Driver rows. | [ ] |
| H24 | Both AWB numbers pass the modulo-7 check but sit on pure over-the-road dry-van loads with no air leg — while the console's own note says AWB appears "only where the shipment has an air segment". | [ ] |
| H25 | A Volvo A40G (off-road articulated site dump truck) is plated, registered, ELD-equipped, DOT-inspected and run 95 miles on public highway. | [ ] |

**Domain verdict:** "TMS based" is defensible on VOCABULARY — Master Data catalogues, the CO-09 ladder, the AWB modulo-7 rule, detention arithmetic and the recurring-contract exclusion from RPM are all genuinely correct. It is NOT yet defensible on BEHAVIOUR.

---

# FIX LOG — what has actually landed in the file

Every line below was verified by reading the result back out of the Figma file,
not inferred from the script completing.

## Fixed and verified

| Ref | Fix | Evidence |
|---|---|---|
| A1 | Styles and variables now bound to nodes. The "select a node, see the token" demo is real. | 876 fills bound on masters (instances inherit) + 3,516 fills on screen frames; text styles 7 -> 60, 2,160 text nodes bound |
| A2 | Tables no longer amputated at narrow widths. Tablet compresses columns to fit; mobile keeps a 600px readable minimum and scrolls horizontally, matching the console's `overflow-x:auto` + `min-width:600px`. | `renderTable` now mode-aware; `overflowDirection = HORIZONTAL` set when wider than the frame |
| A3 | Dashboard rebuilt with all 9 console panels — Live map snapshot (drawn from the console's own projected SVG geometry, not a text list), Onboarding & compliance checklist, Active Alerts, Upcoming Tasks, Trips on going. | frame height 2264 -> 3496; blocks 6 -> 10 |
| A4 | Reports rebuilt with all 5 panels + the analytics KPI row. | blocks 5 -> 8 |
| A5 | Notification Preferences now renders the real 5x3 Email/SMS/Push matrix with per-cell on/off state. | generator special-case, values read from `notifPrefsPage()` |
| A6 | Vehicle Types now carries the 10 truck-type cards. | 10 KPI cards extracted from `TRUCK_TYPES` |
| A9 | Checkbox, Bulk Bar, Skeleton added. | component pass: 13 created |
| B1 | Note tones are the console's again — amber default, blue and red as explicit opt-ins. | ground truth 20 amber / 9 blue / 4 red; generated set now 10 / 6 / 2 |
| B2 | Table headers uppercase, so ETA / CDL / VIN / OCR / AWB read correctly. | 58 headers fixed on the originals, all generated headers uppercased at source |
| B3 | Legend chips verbatim from `srcline()`. | 8 legends restored |
| B4 | Row action buttons restored in ACTION / ACTIONS columns. | 43 cells now carry buttons; the renderer already supported `d.btns`, the generator never emitted them |
| B5 | Invented pagers removed — only the one table the console actually paginates keeps a pager. | 5+ -> 0 |
| B6 | Filter chip rows restored where the console has them. | driven from the console's `.filters` markup |
| B8 | Mobile content padding now 10px sides / 12px top per `@media(max-width:380px)`. | |
| B9 | KV Row key column narrows off desktop instead of holding 190px at 375. | |
| C2 | 53 missing text styles created, including the 32px KPI numeral. | 7 -> 60 |
| D | Lock badge is a badge again, not a button; RR empty state has its CTA back; progress bars render. | `spec.lock` support added; 16 cell bars |
| — | Icon set 12 -> 47 glyphs, and `settings` no longer ships the wrong glyph (was `I.users`, console uses `I.gear`). | component pass |
| — | Toast gained an error variant; Table/Header gained sort arrows; Pager split out Pager Button; Field gained required / help / disabled / textarea; Pulse Cell gained tone variants. | 6 components rebuilt, 142 variants |

## Still open at the time of writing

A7 overlay frames · A8 responsive navigation · A10 Sidebar/Root instancing · B7 responsive uses build-time pixel widths rather than FILL · C1 spacing and radius tokens are derived, not read from `:root` · C4 gradients · C5 20 uncovered colours · section H — the 25 console-side domain and logic defects, which are a separate workstream from the Figma file.

---

# FINAL STATE — end of the Figma workstream

Audited out of the live file, not inferred:

```
desk=42  resp=168 (84 closed + 84 menu-open)  overlays=20
links: desktop 756 + responsive 1,680 = 2,436   failed=0  missing=0
components=40 / 229 variants   paint styles=34   text styles=71
text nodes bound to a style: 88,407 of 88,416
fills bound: 7,377 (screens) + masters
visible placeholders=0   frame overlap=0   section clash=none
```

## Closed since the audit

A1 token binding · A2 table overflow · A3 Dashboard 9 panels · A4 Reports 5 panels ·
A5 Notification Preferences matrix · A6 Vehicle Types truck grid · **A7 overlay frames (20)** ·
**A8 responsive navigation — 84 menu-open frames, hamburger, scrim, 1,680 links** ·
A9 Checkbox / Bulk Bar / Skeleton · B1 note tones · B2 header casing · B3 legend chips ·
B4 row actions · B5 invented pagers · B6 filter rows · B8 mobile density · B9 KV row ·
C2 text styles 7 → 71 · D (all six per-screen parity fixes) ·
Icon 12 → 47 glyphs with the settings-gear correction · Toast error variant ·
Table/Header sort · Pager Button · Field required/help/disabled/textarea · Pulse Cell tones

## Knowingly still open — recorded, not hidden

| Ref | What | Why it was left |
|---|---|---|
| A10 | `Sidebar/Root` is still instantiated 0 times; the rail is built as a raw frame on every screen | Converting it means re-rendering all 294 frames again. It is cosmetic to the reviewer but real to a developer — worth doing before the frontend build starts, not during it |
| B7 | KPI cards, pulse cells and the two-column grid still use build-time pixel widths rather than FILL | Dragging a frame edge will not reflow those three. Tables, padding and KV rows now do reflow |
| C1 | The 7 radius and 14 spacing tokens are derived from measured CSS, not read from `:root` — the console has only 2 radii and no spacing variables | The values are right; only the provenance claim was wrong. The guide now says "derived", not "verbatim" |
| C4 | The six gradients are still flattened to one stop, including the brand mark | |
| C5 | ~20 console colours (scrollbars, map palette, hover tints) still have no token | |
| H1–H25 | The 25 console-side domain and logic defects | These live in the HTML, not the Figma. They are a separate workstream and several are business decisions the client must make, not defects I should silently "fix" |

The guide's section 7 "Known gaps — agar poocha jaye to" carries a one-line answer for each of these, so none of them is a surprise in front of the team lead.

---

# FINAL — Figma workstream closed

Read out of the live file by the end-state audit, not inferred:

```
frames    desktop 42 · responsive 168 (84 closed + 84 menu-open) · overlays 20  = 230
links     desktop 756 + responsive 1,680 = 2,436      failed 0   missing 0
library   40 components / 229 variants
tokens    55 paint styles · 71 text styles · 76 variables
bound     88,407 of 88,416 text nodes · 7,168 screen fills + masters
quality   visible placeholders 0 · frame overlap 0 · section clash none
```

## Closed in this final pass

- **C5** — 21 colours the console used but had no token: map palette, scrollbars, hover
  tints, gradient stops, scrim. Each is a variable AND a paint style, so they bind.
  Paint styles 34 → 55.
- **C4** — gradients restored where the console has them: the brand mark
  (`135deg, --brand → #0c5c38` with its `#2a5c44` inset ring) and the second brand tile
  (`#3a4c66 → #22304a`). These are the first thing a reviewer zooms into.
- **B7 (most of it)** — KPI cards, pulse cells and equal-ratio columns are now rows of N
  with FILL children instead of a wrap of build-time pixels, so dragging a frame edge
  genuinely reflows them. Tables, padding and KV rows already reflowed.

## Still open, deliberately

| Ref | What | Why |
|---|---|---|
| A10 | `Sidebar/Root` is still instantiated 0 times; the rail is a raw frame on every screen | Converting it means re-rendering all 230 frames and re-wiring 2,436 links. Better done before the frontend build starts than as a late change |
| B7 (remainder) | The 1.6:1 column split is still a measured pixel width | Figma's `layoutGrow` is 0/1 only — it cannot express a fractional ratio. Equal splits FILL; uneven ones cannot. Stating this is more honest than claiming full fluidity |
| C1 | Radius and spacing tokens are derived from measured CSS, not read from `:root` | The console has 2 radii and no spacing variables. Values are right; the guide now says "derived", not "verbatim" |
| H1–H25 | 25 console-side domain and logic defects | They live in the HTML, not the Figma, and several are business decisions for the client — not mine to silently change |

## Two tooling lessons worth keeping

1. **Playwright cannot attach to a Figma tab this large** — the CDP handshake enumerates
   every target and never completes. A minimal single-target CDP client attaches instantly.
2. **CDP input is ignored unless `Emulation.setFocusEmulationEnabled` is on.** Every click
   silently did nothing until that was set. And Figma's canvas is WebGL, so results must be
   read from the layers panel DOM or a screenshot — never from canvas text.

---

# ROUND 3 — research findings implemented

Five research briefs (`data/research/ops-motion/`) were run on motion, perceived
performance, dense tables, keyboard-first interaction and live-data alerting, framed
around one fact: this is an operator tool, not a marketing site. A dispatcher repeats
the same actions hundreds of times a day, which inverts most "polish" advice.

## What changed in the file

| Finding | Implemented |
|---|---|
| A scrolling table below ~480px hides columns from someone checking a load one-handed, and they never learn they missed one — every source called it an anti-pattern | Every table on the 42 mobile frames is now a **card list**: identity + status chip, five key fields, row actions, and `View details (N more)` for the rest. Horizontal scroll with a pinned column is kept for 480–900px only, which is where it is correct |
| Severity must never rest on colour alone (Carbon, PatternFly; Bloomberg redesigned its terminal for exactly this) | The `Chip/Status` marker now carries **shape** too — red is a square, amber a diamond, everything else a circle |
| Motion is a design-system concern, not late polish — it changes component APIs | 8 duration variables shipped, plus a `Motion — spec` board on page 01 carrying the scale, easings, the loading ladder, the reduced-motion rule, and the warning below |
| A number that is evidence must never be tweened | Written onto the spec board in red: the detention timer and HOS clock are a billing record and a legal clock. Animate the container's colour at a threshold; never the digits |
| Motion that is only documented cannot be judged | **205 Smart Animate transitions** wired at the documented durations: the wizard advances on asset pick at 220ms ease-out, Back returns at 180ms ease-in, and all 84 mobile/tablet menu drawers open at 220ms and close at 180ms — exits faster than entries, as the research specifies |
| Every chunk of the future build needs these rules in its spec, not in someone's memory | `BUILD_BRIEF.md` section 3b — motion scale, loading ladder, the optimistic-UI no-list, table patterns, keyboard map, and the four-tier severity model |

## End state

```
frames   42 desktop · 168 responsive (84 menu-open) · 20 overlay
links    756 desktop + 1,680 responsive = 2,436, plus 205 Smart Animate transitions
library  40 components / 229 variants
tokens   55 paint · 73 text · 8 motion durations
bound    64,399 of 64,408 text nodes
quality  visible placeholders 0 · frame overlap 0 · section clash none
```

Text nodes fell from 88,416 to 64,408 because a card carries far fewer nodes than a
ten-column table row. The file got lighter as a direct result of the fix.

## Two findings recorded but deliberately not acted on

- **Optimistic UI must not cover detention "raise as billable", payment approve/pay, POD
  close-out or any delete.** That is a frontend rule with nothing to change in Figma; it
  is written into the build brief so it cannot be lost.
- **Sticky header + sticky first column + row virtualisation is unresolved upstream in
  TanStack**, and a virtualised grid misreports its row count to screen readers — so the
  Audit Log and RBAC matrix should probably be paginated instead. Both are scheduling and
  architecture facts for the build, not design changes.

## Still open on the design itself

`Sidebar/Root` is still instantiated zero times — the rail is a raw frame on all 230
screens. It is the one place the "component based" claim is genuinely weak, and it is the
cheapest thing to spot. Fixing it means re-rendering every frame and re-wiring 2,436
links, which is why it should happen before the frontend build starts rather than during.
