# mySHIPR Carrier Console → Figma design system + screens

## Source of truth
`/home/ujjwal/Documents/J.A.R.V.I.S./mySHIPR_Carrier_Console_v4 (2).html` — a working 3,240-line
single-file TMS carrier console. Every colour, radius, font size and spacing value used in the
Figma file MUST be read out of this file. Do not invent values.

Reference renders (1440px @2x, full page) are in `figma-build/reference/`:
`01-dashboard` … `12-settings` (desktop) plus `R-fleet-tablet` (900px) and `R-fleet-mobile` (375px).

## Hard constraint on delivery
The Figma account is **Starter plan / View seat = 6 MCP tool calls per month**. The design must
therefore NOT be built by repeated `use_figma` calls. Deliver a **single self-contained Figma
Plugin API script** the user pastes into a Figma plugin and runs once. It must build everything
in one execution and be re-runnable (delete/replace prior output rather than duplicating).

## Design tokens (verbatim from the file's `:root`)
```
chrome        #0f141d   chrome-2   #161d29   chrome-3  #1e2735   chrome-line #2a3446
canvas        #eef1f4   panel      #ffffff   panel-2   #f7f9fb   line        #e0e5ea   line-2 #eef1f4
ink           #141a24   ink-2      #586173   ink-3     #8b93a1   ink-inv     #e7ebf1   ink-inv-2 #9aa5b6
green #157a4a  green-bg #e4f3ea  green-ink #0e5a37
amber #c9770a  amber-bg #fbeede  amber-ink #8f5405
red   #c23b3b  red-bg   #f8e4e4  red-ink   #8f2626
blue  #2c66b0  blue-bg  #e5eefa  blue-ink  #1e4c86
grey  #6b7480  grey-bg  #eceff3  grey-ink  #4b5460
purple #6b4fa8 purple-bg #eee9f8 purple-ink #4d3680
brand #157a4a  sign #e2a90b
radius  r 10px   r-sm 7px
```
Fonts — all three verified present in this Figma account via `listAvailableFontsAsync()`.
**The style strings differ per family — do not normalise them:**
- **Inter** — `Regular`, `Medium`, `Semi Bold` *(with a space)*, `Bold` — body, 14px base, line-height 1.45
- **Barlow Semi Condensed** — `Medium`, `SemiBold` *(no space)*, `Bold` — display: h1, panel headings, buttons
- **IBM Plex Mono** — `Regular`, `Medium`, `SemiBold` *(no space)* — all IDs, VINs, plates, timestamps, codes

Getting this wrong throws `Cannot write to node with unloaded font`. Load every family+style
pair with `figma.loadFontAsync` before creating or mutating any text that uses it.

## Naming contract (must be followed exactly)
- Variable collections: `Color`, `Radius`, `Spacing`
- Text styles: `Display/H1`, `Display/Panel`, `Body/Base`, `Body/Small`, `Body/Sub`, `Mono/Code`, `Mono/Label`
- Components: `Sidebar/Item`, `Sidebar/Root`, `TopBar`, `Button`, `Chip/Status`, `Chip/Filter`,
  `Panel`, `Table/Row`, `Table/Header`, `KPI Card`, `Banner`, `Field`, `Drawer`, `EmptyState`,
  `HOS Bar`, `Pager`, `Toast`, `Lane`
- Pages — **exactly three, already created** (the Starter plan caps a file at 3 pages, so the
  original 5-page layout is impossible; the fourth `createPage()` throws). Organise within them
  using **Sections**, which cost nothing:
  | Page | id | Sections inside |
  |---|---|---|
  | `01 Design System` | `0:1` | `Foundations` (variables, styles, swatches) · `Components` |
  | `02 Screens` | `3:2` | `Desktop` (12 frames) · `Responsive` (900 + 375) |
  | `03 Prototype` | `3:3` | flow map + wiring documentation |

## Components required (with variants)
| Component | Variants |
|---|---|
| `Sidebar/Item` | state = default / hover / selected; badge = none / count / new |
| `Button` | kind = primary / secondary / danger; size = md / sm; state = default / hover / disabled |
| `Chip/Status` | tone = green / amber / red / blue / grey / purple; style = solid-bg / plain |
| `Chip/Filter` | state = off / on; count = yes / no |
| `Table/Row` | state = default / clickable-hover / blocked (red tint) |
| `KPI Card` | tone = default / amber / red / blue / grey |
| `Banner` | tone = info / warn / crit / ok; action = yes / no |
| `Field` | state = default / focus / error; type = input / select |
| `Panel` | header = title-only / title+hint / title+action |
| `EmptyState` | kind = empty / denied (403) / error |
| `HOS Bar` | band = green / amber / red |

Every component must use **Auto Layout** with correct padding/gap read from the CSS, and
**constraints** set so it survives resizing. No absolutely-positioned children except icons.

## Screens required — 12 desktop frames at 1440 × auto
1. Dashboard — Overview
2. Fleet — All Vehicles
3. Drivers — All Drivers
4. Loads — Tenders
5. Trips — On going
6. Driver Ops — Detention
7. RR — Coming soon
8. Yards — All yards
9. Notifications
10. Reports — Operations
11. Earnings — Earnings
12. Settings — My Profile

Each screen = sidebar + top bar + page header + content, built **only from the components above**
(no detached copies). Content/data must match the reference screenshots (real rows, real IDs).

## Responsive
Three widths per the file's real breakpoints:
- **Desktop 1440** — sidebar fixed 248px
- **Tablet 900** — sidebar becomes off-canvas (hidden), hamburger appears in the top bar, grids collapse to 2-up
- **Mobile 375** — single column, tables scroll horizontally inside their container, KPI cards stack

Produce the responsive set for at least Dashboard, Fleet and Detention (3 screens × 2 extra widths).

## Prototype
On the `03 Screens — Desktop` page: wire each of the 12 sidebar items so clicking it navigates
to the matching frame, on every one of the 12 frames. Interaction = On click → Navigate to →
Instant. The remaining in-screen controls do NOT need wiring — this is the agreed scope.

## Acceptance checklist
- [ ] Pixel perfect: colours, radii, font sizes and paddings match the HTML exactly
- [ ] Component based: screens contain instances only; changing a master updates all screens
- [ ] Responsive: auto-layout + constraints, three widths, no manual repositioning needed
- [ ] TMS conventions: dense tables, status chips, operational density preserved
- [ ] Prototype: all 12 sidebar items navigate correctly from every screen
- [ ] Script runs top-to-bottom in one go, loads every font with `figma.loadFontAsync` first,
      and is safe to re-run
