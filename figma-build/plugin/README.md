# mySHIPR · Carrier Console → Figma

Three scripts that build the whole Figma file — design tokens, a component library,
12 desktop screens, 6 responsive frames and the sidebar prototype — from the
values in `mySHIPR_Carrier_Console_v4 (2).html`. Nothing is invented: every hex,
radius, font size and padding is read out of that file's `:root` and CSS.

---

## How to run — Scripter (primary path, works in the browser)

Figma has **no Linux desktop app**, and "Import plugin from manifest" only exists in
the desktop app. So on Linux the route is the community plugin **Scripter**, which
runs a Figma Plugin API scratchpad inside the browser.

1. Open your Figma **design file** in the browser (a normal Figma file, not FigJam).
2. Right-click canvas → **Plugins → Scripter** (install once from
   <https://www.figma.com/community/plugin/757836922707087381/scripter>).
3. Open `part1-foundations-components.js`, select all, paste into Scripter, press
   **Run** (⌘/Ctrl + Enter). Watch the Scripter console; it logs each phase.
4. Clear the editor, paste `part2-screens.js`, Run.
5. Clear the editor, paste `part3-responsive-prototype.js`, Run.

**The order matters.**

| Part | Builds | Depends on |
|---|---|---|
| `part1-foundations-components.js` | `01 Foundations`, `02 Components` — variable collections, paint + text styles, every component set | nothing |
| `part2-screens.js` | `03 Screens — Desktop` — 12 frames @ 1440 | **part 1** |
| `part3-responsive-prototype.js` | `04 Screens — Responsive`, `05 Prototype`, plus all sidebar reactions on page 03 | **part 1 and part 2** |

Parts 2 and 3 do **not** rely on anything staying in memory — Scripter gives each
run a fresh scope. They look the library up by name on page `02 Components`
(`collectComponents` → `adoptComponents`) and stop with a loud console error
(`Run part1-foundations-components.js first — N component(s) missing`) if it is not
there.

Each part is **idempotent**: re-running wipes and rebuilds only its own pages and
never duplicates. Part 1 also removes the `Color/*` paint styles, `Display|Body|Mono/*`
text styles and the `Color` / `Radius` / `Spacing` variable collections it created
last time before recreating them.

### Fonts

Part 1 resolves fonts defensively before drawing a single character, because Figma's
style naming differs per family (Inter is `Semi Bold`, Barlow Semi Condensed is
`SemiBold`). Each slot tries a list of candidates and falls back rather than
throwing:

| Slot | Tries | Falls back to |
|---|---|---|
| body / medium / semi / bold | `Inter Regular / Medium / Semi Bold / Bold` | Roboto, then Arial |
| display | `Barlow Semi Condensed Medium / SemiBold / Bold` | the Inter equivalents |
| mono | `IBM Plex Mono Regular / Medium / SemiBold` | Roboto Mono, Courier New |

All three families are free Google fonts and are available in Figma by default, so
the fallbacks should never fire. The console prints the resolved list — check it if
type looks wrong.

---

## Alternative — Figma desktop app (Windows / macOS, or `figma-linux`)

`manifest.json` points at part 1. Use **Plugins → Development → Import plugin from
manifest…**, pick `manifest.json`, run the plugin. To run parts 2 and 3, edit
`"main"` in `manifest.json` to the next file and run again. The Scripter path is
less fiddly; this exists only so the same code works on a machine that has the
desktop app.

---

## What gets built

**`01 Foundations`** — swatches for all 34 colour tokens (name + hex), a type
specimen for all 7 text styles, and the radius + spacing scales.
Variable collections: `Color` (34), `Radius` (7), `Spacing` (14). Paint styles are
`Color/<token>` and are **bound to the matching variable**, so changing a variable
repaints everything downstream.

**`02 Components`** — the library. Named exactly per the naming contract:

| Component | Variants |
|---|---|
| `Sidebar/Item` | state = default / hover / selected × badge = none / count / new (9) |
| `Sidebar/SubItem` | state = default / active (2) |
| `Sidebar/Root` | assembled 248px rail (1) |
| `TopBar` | 1 |
| `Button` | kind = primary / secondary / danger × size = md / sm × state = default / hover / disabled (18) |
| `Chip/Status` | tone = green / amber / red / blue / grey / purple × style = solid-bg / plain (12) |
| `Chip/Filter` | state = off / on × count = yes / no (4) |
| `Panel` | header = title-only / title+hint / title+action (3) |
| `Table/Header` | 1 |
| `Table/Row` | state = default / clickable-hover / blocked (3) |
| `KPI Card` | tone = default / amber / red / blue / grey (5) |
| `Banner` | tone = info / warn / crit / ok × action = yes / no (8) |
| `Field` | state = default / focus / error × type = input / select (6) |
| `Drawer` | 1 |
| `EmptyState` | kind = empty / denied / error (3) |
| `HOS Bar` | band = green / amber / red (3) |
| `Pager` | 1 |
| `Toast` | 1 |
| `Lane` | 1 |
| `Icon` | name = 12 nav glyphs (12) |
| `Pulse Cell`, `Bar Row`, `List Item`, `Stop Line`, `KV Row`, `Note`, `Legend Chip` | supporting sets the 12 screens need (1 / 5 / 10 / 2 / 2 / 3 / 1) |

Everything is Auto Layout with the padding and gaps read from the CSS, and
constraints are set on every child so a frame survives being dragged wider.
No absolutely-positioned children except icons and the notification-count dot.

**`03 Screens — Desktop`** — 12 frames at 1440 × auto:
Dashboard, Fleet, Drivers, Loads/Tenders, Trips, Driver Ops/Detention, RR, Yards,
Notifications, Reports, Earnings, Settings. Data is the real records out of the
HTML (`TRUCKS`, `DRIVERS`, `SHIPMENTS`, `TRIPS`, `YARDS`, `DETENTION`, `NOTIFS`).

**`04 Screens — Responsive`** — Dashboard, Fleet and Detention at 900 (tablet) and
375 (mobile), following the file's real breakpoints: at ≤920px the sidebar goes
off-canvas and a hamburger appears in the top bar with the search on its own row;
at ≤900px KPI grids collapse to 2-up; at ≤380px to 1-up; tables keep their real
width inside a clipped container so they scroll horizontally.

**`05 Prototype`** — a documentation board: the nav-key → destination-frame map and
the wiring stats. The reactions themselves live on page 03.

---

## Prototype

Part 3 sets an **On click → Navigate to → Instant** reaction on every one of the 12
`Sidebar/Item` instances, on every one of the 12 desktop frames — 144 links — so the
rail works from any starting screen. The flow starting point is
`01 Dashboard — Overview`. In-screen controls are deliberately not wired (agreed
scope); their states are documented on page 02 instead.

---

## Honest notes / known limits

- **Containers are frames, not instances.** Figma has no "slot" primitive, so the
  screen frame, the grid rows and the white card that wraps a `Panel` header are
  Auto Layout frames. Every piece of *content* inside them is an instance. This is
  the standard way to do it and is the only reason the SPEC line "screens contain
  instances only" is not literally 100%.
- **Charts are shapes.** The dashboard donut is a real `arcData` ellipse ring and the
  bar charts use the `Bar Row` component; neither is a live chart.
- **`Lane` is used in the library, not inside table cells.** Table lanes are rendered
  as `San Jose → Tracy` with the ZIPs on the sub-line, because a table cell cannot
  host an arbitrary nested instance without an instance-swap property.
- **Nested variant overrides** (the status chip inside a table row) are applied with
  `setProperties`, and then the fill/label are forced directly as a fallback, so the
  chip is correct even if Figma refuses the nested property override.
- Run `bash ../validate.sh` before pasting if you edit the scripts — it checks
  syntax, Scripter-unsafe APIs, font loading order, idempotency and that every hex
  still traces back to the source HTML.
