# D1 — Foundations, Components, Patterns

Pages 01–03 of the Figma-structure map. Every token is read from `prototype.html`'s `#proto-root`
CSS custom properties — none invented. 8 of 31 F9 screens are built and verified: SCR-900, 901,
902, 910/911, 930, 920, 924, plus an unnumbered Shipment Detail timeline (≈SCR-904). All else here
is specified from those patterns and flagged `[SPEC]`.

---

## 01 · Foundations

### Colour — dark primary, light at parity

| Token | Dark | Light | Use |
|---|---|---|---|
| `--bg-canvas` | `#0a0c10` | `#f6f7f9` | page bg |
| `--bg-surface` / `-2` / `-3` | `#12151b`/`#181c24`/`#1f242e` | `#ffffff`/`#eef0f4`/`#e3e6ec` | card/input · th/hover/chip · skeleton/deepest |
| `--bg-overlay` | `rgba(6,7,10,.72)` | `rgba(20,22,28,.45)` | palette/modal backdrop |
| `--border-subtle`/`-default`/`-strong` | `#232833`/`#323a48`/`#4a5264` | `#e3e6ec`/`#cdd2dc`/`#a7aebb` | card → input → dialog edge |
| `--text-primary`/`-secondary`/`-tertiary`/`-disabled` | `#f2f4f7`/`#aab2c0`/`#7c8494`/`#4b5261` | `#12151b`/`#454c59`/`#5b6270`/`#9aa0ac` | heading → disabled |
| `--text-on-accent` | `#0a0c10` | `#ffffff` | text on accent fill |
| `--accent`/`-strong` | `#8fb2ff`/`#b3ccff` | `#2c4fc4`/`#1f3ea3` | primary btn, links, focus |
| `--focus-ring` | `#8fb2ff` | `#2c4fc4` | 2px `:focus-visible` outline |
| `--shadow-1`/`-2` | soft/deep black | soft/deep, lower alpha | resting / overlay elevation |

Theme order: `data-theme` attr → `prefers-color-scheme` → dark default. Both modes render every
screen (`color-scheme` set both sides) — light is not bolted on.

**Status — IBM colour-blind-safe five (spine §7.3), verbatim from prototype:**

| Hue | Dark | Light (darkened) | Why darkened |
|---|---|---|---|
| Blue | `#648fff` | `#2c4fc4` | literal ≈3.1:1 on white — fails 4.5:1 AA body text |
| Violet | `#785ef0` | `#6338c2` | same failure, ≈3.3:1 |
| Magenta | `#dc267f` | `#a3105f` | literal passes large-text AA only |
| Orange | `#fe6100` | `#a34500` | literal ≈2.4:1 — fails outright |
| Amber | `#ffb000` | `#7a5600` | worst literal, ≈1.8:1 |

Dark mode keeps literal IBM values (near-black surfaces give headroom); light mode substitutes
same-hue darkened variants so the five stay pairwise distinguishable by hue+lightness without
breaking AA. **Status is never colour alone** — every badge/banner/queue-severity pairs icon +
colour + text; no bare colour dot ships anywhere in the prototype.

### Type

System stack, no webfont: `--font-sans: ui-sans-serif, system-ui, -apple-system, "Segoe UI",
Roboto, sans-serif`; `--font-mono: ui-monospace, "SF Mono", Menlo, monospace`. Base `14px`/`1.45`.
Observed scale (no formal array — sizes set per-component, `[NEEDS INPUT]` to formalize):
`56px`→`28px` (bid hero amount/cents) → `20px` (screen h1) → `18px` (driver h1) → `16px` (POD/empty
h3) → `15px` (panel h3) → `13.5–14px` (body/buttons/primary cell) → `12.5–13px` (secondary/badge)
→ `11–12px` (th, eyebrow, hint, meta). Headings `weight:650`, `letter-spacing:-.01em`. Every
price/id/timestamp cell carries `font-variant-numeric: tabular-nums` so re-sorted/ticking columns
never jitter.

### Spacing, radius, elevation, border

Space: 4·8·12·16·20·24·32·40·48 (`--sp-1`…`--sp-12`). Radius: `--radius-sm:6px` (buttons, inputs,
skeleton) · `-md:10px` (banners, icon-btn) · `-lg:14px` (cards, table-wrap, POD tiles) · `-full`
(chips, badges, pills). Elevation: `--shadow-1` resting (active chip/thumb), `--shadow-2` overlay
(palette, phone frame) — no third tier. Border: 1px throughout, weight is colour-tier not
width-tier (`subtle→default→strong`); POD choice tiles use 2px deliberately as a large target.

### Motion

No formal duration/easing token object exists — durations are inlined per rule (`[NEEDS INPUT]`
to formalize `--motion-duration-fast/base/slow`): `.btn` state `.12s`, skip-link `.15s`,
row-actions fade `.12s`, skeleton shimmer `1.3s` linear infinite, bid-spinner `.8s` linear
infinite, new-bid flash `1.6s ease-out`.

```css
@media (prefers-reduced-motion: reduce){
  #proto-root *{ animation-duration:.001ms !important; animation-iteration-count:1 !important;
    transition-duration:.001ms !important; scroll-behavior:auto !important }
}
```
Global kill-switch already in the prototype — every shimmer/spinner/flash/countdown-shift goes
instant under the OS setting. **Live-update rule, load-bearing:** a new bid never ticks or flashes
repeatedly — `.bid-feed-row.is-new` washes once (blue-tinted → transparent) then the class is
removed after 1.7s. Nothing pulses continuously. This highlight-once-then-settle treatment is
required for any live row (queue re-sort, countdown crossing `is-final`, outbid notice) — never a
persistent blink.

### Iconography

Inline SVG, 24×24 viewBox, `stroke-width:2`, round cap/join, name→path lookup (`aria-hidden` on
the rendered SVG). Sizes: `16px` default, `13px` in badges, `11px` in sort buttons, `36–44px`
(`icon-lg`, empty/outcome states), `38px` (`icon-xl`, POD tiles). 37 icons defined. **Icon =
specific status, colour = severity tier** — independent signals, not duplicates:
`alert-triangle` generic warning · `alert-octagon` hard auction failure · `shield-alert`
fraud/cargo-integrity · `lock` suspension/denied · `clock` time-based (verifying/regulatory/stale)
· `check-circle` success/clean/empty-is-good · `refresh-cw` re-open/sync-pending/extended ·
`wifi-off` offline · `flag` auction-open/report · `x` cancelled/neutral-negative. Icon-only
controls always carry `aria-label` (row actions, theme toggle, bell) — never a bare icon.

---

## 02 · Components

Legend: R=rest H=hover F=focus-visible A=active D=disabled L=loading E=error S=selected
RO=read-only. **Built** = observed in `prototype.html`. `[SPEC]` = specified here, unbuilt.

| Component | States (built) | Gaps (spec-only) | Variants | Key tokens | A11y note |
|---|---|---|---|---|---|
| Button | R/H/A/D/L(spinner swap) | — | primary/ghost/danger/sm/lg/icon/block | `-radius-sm`, `--accent`, min-h 36/28/52 | native `<button>`, real `disabled` attr |
| Input/Select/Textarea | R/F(border→ring)/RO | D, L `[SPEC]` | shared `.input` class | `--bg-surface`, `--focus-ring`, min-h 38 | `<label for>` always paired |
| Form field | R/E (weight-required) | S/D `[SPEC]` | hint (info icon) vs error (magenta, alert-triangle) | tertiary text / magenta 600-weight | error inserted inline, natural reading order; `[SPEC-gap]` no `aria-describedby`/`aria-live` wired to `.err` |
| Status badge | R (static) | interactive variant `[SPEC]` | info/pending/critical/warning/attention/neutral | `--c` via `color-mix` 16/55% | icon+text always paired, no bare colour |
| Badge/Chip/Banner | all built | — | chip `is-active`; banner stale/critical/info/neutral(+attention) | `.chip .count` mono | chip group `role="group"`; `[SPEC-gap]` banners lack `role="status"`/`aria-live` for post-load appearance |
| Dense table | sticky header, sortable, 2 pinned cols, hover-reveal row actions, exception-divider grouping, saved-view filter | bulk-select, inline-edit `[SPEC]` | — | sticky `left:0/118px`, scroll-shadow on c2 | sort = real `<button>`; `.row-actions` opacity 0→1 on `:hover,:focus-within` so Tab reveals without hover |
| Saved-view chip | R/S/count | — | — | accent-tinted active via `color-mix` | `role="group"`, real `<button>` each |
| Skeleton | shimmer sweep | `aria-live`/`aria-busy` `[SPEC-gap]` | bar height matches replaced content | `--bg-surface-2` base | should announce "Loading…" once, not per shimmer frame |
| Empty state | built (loads/exceptions "all clear") | — | neutral vs `--denied` (permission) | `icon-lg` tertiary/magenta | `<h3>`+`<p>`+CTA if recoverable; ops-empty explicitly framed as a *good* outcome |
| Timeline event | done/custody/exception(dashed callout)/pending(muted, unreached) | — | scheduled-vs-actual dual timestamp, `is-late` variant | status hue dot rings | `<ol role="list">`; exception item physically breaks the spine so it can't be scanned past |
| Queue row | R/S(critical border)/claimed(DOM swap)/D(claimed-by-other) | — | severity dot via `--c` | `.eq-severity` 38px chip | claim = real button; contest shows literal claimant name, not generic "locked" |
| Countdown | R/`is-final`(<60s amber) | threshold-crossing `aria-live` `[SPEC-gap]` | table-cell vs bid-panel size | mono, `--status-amber` | ticks avoid `aria-live` per-second (correct — no spam); needs announce only at extend/final-min/close, mirroring auction-watch's existing `announce()` |
| Bid hero number | R/dash(failed)/verifying(label swap) | — | 56px+28px split span | tabular-nums | label precedes number in DOM/reading order |
| Phone frame | shell, notch, status bar, offline pill, `.online-only` graceful-degrade | tab-order exclusion when offline `[SPEC-gap]` | — | hard-coded device chrome, not themed | `pointer-events:none` removes click but not confirmed to remove Tab order for all elements |
| Command palette | R/F(autofocus)/list nav(↑↓/Enter)/empty | focus-trap-on-close, `role="listbox"`+`aria-activedescendant` `[SPEC-gap]` | nav/theme/persona items mixed in one list | `--bg-overlay`, `--shadow-2` | `role="dialog" aria-modal="true"`, ⌘K toggle, Esc close |
| Modal/Sheet | `[SPEC]` — unbuilt | full component | confirm-dialog, side-sheet | reuse palette's overlay tokens | must reuse palette's dialog+focus-trap+Esc contract, not a second pattern |
| Toast | `[SPEC]` — unbuilt; prototype uses inline state-swap + `aria-live` regions instead | full component if kept | success/error/undo | `--shadow-2` | **recommend not building** — prototype already proves in-place resolution (bid outcome, POD submit, claim) works without a third notification surface |
| Tab/Segmented control | `.state-switch`, `.persona-switch`, `.lang-toggle`, `.theme-toggle` — same visual pattern | — | pill-group, icon+label group | `--bg-surface-2` track, `-1` shadow on active thumb | `role="group"`; correctly **not** native tab/tabpanel ARIA since these switch views, not panels |
| Signature pad | R/drawing/cleared | keyboard/switch-access alternative `[SPEC — WCAG 2.5.7 gap]` | canvas, Pointer Events (touch+mouse unified) | `--text-primary` stroke, dashed `--border-strong` frame | `role="img" aria-label"` fallback on canvas (correct, canvas has no AX tree); needs a typed-name alternative for non-pointer users |
| Photo capture tile | R/taken(relabel to Retake)/error(mandatory-missing) | camera-permission-denied fallback `[SPEC]` (EC-910 resolved in F9, not yet visualized) | optional vs mandatory (driven by POD choice) | `--status-magenta` error text | icon+label always, never icon-only |
| Offline indicator | `.offline-pill` + status-bar icon swap (driver only) | generalize to desk personas `[SPEC]` | — | `--status-orange` | announced via existing `aria-live="assertive"` in POD flow |
| Persona switcher | sidebar (desktop) + horizontal (driver) | — | vertical icon+label vs horizontal icon-over-label | accent-tinted active row | real `<button>` each; switching re-scopes nav + org identity together, avoiding stale-identity bugs |

---

## 03 · Patterns

**Dense table.** One shape for Loads Dashboard and Load Board: sticky header + 2 pinned columns
(ref, lane — what you look up *by*) + horizontal scroll contained in `.table-wrap` (never the
page) + saved-view chip filter above + exception-divider grouping putting "Needs attention" ahead
of "On track" inside the *same* table, not a separate panel (F9's exception-forward IA). Row
actions hidden until `:hover`/`:focus-within`. `[SPEC]` bulk-select adds a new pinned `c0`
checkbox column, never displaces `c1`; inline-edit unbuilt.

**Multi-step form.** Post a Load: step-pill progress (`is-done`/`is-current`) + step-label row +
one active `.form-step` + real-second autosave note + inline field-level validation blocking
`Next` (not a page-level summary) + read-only review step before the irreversible action. Required
shape for Claim Intake (SCR-907) and Enforcement Action (SCR-943).

**Timeline.** Vertical spine, dot-per-event, scheduled-vs-actual shown together (gap is the
point, never actual-only), exception events break physically out of the spine, unreached events
render present-but-muted. Canonical for SCR-904 (built); carries unmodified into SCR-903's award
flow and SCR-932's claim-clock, swapping only dot semantics.

**Work-queue.** Severity-colour chip + title + metadata row + one attached action per row (never a
re-triage step) + claimed-by-name replacing the action on contest + rank implicit in top-to-bottom
order, no visible rank number. Pattern for SCR-930 (built), SCR-932 (swap claim for clock-
proximity styling), SCR-940.

**Universal state set.** F9 mandates 8 states + Contested per screen; 5 are demonstrated, 3
extrapolate directly:

| State | Built shape | Reuse rule |
|---|---|---|
| Loading | `.skel` shimmer matching real layout | never spinner-then-blank |
| Empty | icon + h3 + one-line explain + CTA if recoverable | label a *good* empty differently in copy, same visual shape |
| Stale | banner + "last refreshed Nm ago" + retry | never serve cache silently — always timestamp |
| Permission-denied | magenta icon + plain-language cause + one recovery action | states *why*, not just *that* |
| Error | inline field `.err` / screen `.banner--critical` | names the specific cause, never generic |
| Offline | pill + `.online-only` degrade + local-queue pending-sync | `[SPEC]` extend beyond driver persona |
| Partial data | `[SPEC]` — nearest analogue is POD's mixed clean/exception summary | render present and missing pieces distinctly, never merged |
| Contested | `.claimed-tag` name-swap | always names the other actor |

---

## Summary

**Tokens:** ~34 colour custom properties × 2 themes, 5 status hues × 2 theme variants, 9-step
spacing scale, 4 radius steps, 2 shadow tiers, ~14-step de-facto type ramp (no formal array), 6
inline motion durations (no formal token set — both flagged `[NEEDS INPUT]`), 37 icons.

**Components:** 25 documented — 20 built-and-observed, 2 spec-only from scratch (modal/sheet,
toast — recommend not building toast), 3 built-base-with-gaps flagged inline.

**Patterns:** 5 (dense table, multi-step form, timeline, work-queue, universal 8-state set).

**Built vs specified:** 8 screens fully built (SCR-900/901/902/910-911/930/920/924 + ≈SCR-904
timeline). Every component traces to one of those 8 except modal/sheet and toast, specified from
the command palette's overlay contract and the existing `aria-live` pattern respectively.

**Three sharpest questions only Boss can answer:**
1. Commit the whole product to zero toasts (prototype already proves inline-state + `aria-live`
   works for bid outcome, POD submit, claim), or is toast needed for one case — e.g. background
   sync completing while the user has navigated away?
2. Lock formal motion tokens now, or keep inlining per-rule? Six durations already exist at 8
   screens; drifts further across 31 without a token.
3. Signature-pad keyboard/switch-access fallback (WCAG 2.5.7) — build a typed-name alternative, or
   accept pointer-device + physical presence as a valid assumption for this in-person moment? A
   compliance call, not a design one.

**CHALLENGE:** none against the prototype's existing decisions — it is unusually disciplined
(reduced-motion kill-switch, tabular-nums, icon+text status, offline-first POD). One implementation
gap to flag, not a design disagreement: `awExtendedBanner` stacks `.banner--attention` with
`.banner--stale`, but `--attention` is not a defined banner modifier in the CSS, so it silently
falls through to `--stale`'s styling. For `frontend-engineer-agent`.

**Component most likely to be implemented inconsistently:** the **banner** set. Five call sites
already drift — the stacked-class bug above, no stated rule for which banners get a retry action,
and stale/attention/info reading close together in the amber/orange range at a glance. Recommend
`frontend-engineer-agent` lock a single `getBannerProps(kind)` mapping before SCR-905/930/932/933
multiply banner usage across ops screens.

Handoff: implementation → `frontend-engineer-agent` (React 19 + Tailwind 4 + shadcn; tokens map
directly to a Tailwind 4 `@theme` block). `[SPEC-gap]` items above should get axe-core coverage in
the same PR that builds each component.
