# Perceived Performance Playbook for an Operational Dashboard (2026)

Research brief for: dispatch console (TMS operator tool) — dense tables, live status, 4-step
asset-assignment wizard, POD photo review, detention billing, notification centre. Dispatcher
works under time pressure, repeats the same actions hundreds of times a day, over a normal
office connection that is occasionally flaky.

---

## One-paragraph answer

"Instant" in 2026 is not one technique, it's a layered budget: sub-100ms interactions (row
select, filter toggle, status change) must be handled with **optimistic local state** so the
UI never waits on the network at all; the rollback path is the part teams actually get wrong,
so design the failure state first. Loading states above ~500ms-1s need a **skeleton that
matches final layout exactly** (not a generic shimmer) to avoid the well-documented risk that
skeletons feel *slower* than a plain spinner when done badly. Layout must never move
(CLS ≈ 0) — reserve space with matched-dimension placeholders, not `min-height` guesses.
Streaming (RSC/Suspense, or Partial Prerendering) lets the static shell paint immediately
while the slow panels trickle in, but only if Suspense boundaries are drawn around
*independent, co-displayed* data — too many boundaries causes a "popcorn" effect that reads as
janky, too few blocks the whole page on the slowest query. Prefetching (hover-intent,
Speculation Rules API) buys real wins (measured prerender: ~47% perceived-load reduction) but
costs real bandwidth if fired indiscriminately (one team burned 15GB/month on unwanted
prefetches) — scope it to high-confidence navigations only. View Transitions are usable for
route/tab changes in 2026 but should be explicitly disabled on anything that updates in real
time (a live status cell, a ticking count) because morph animation on high-frequency data reads
as noise, not polish. And the one rule specific to a dispatch board: **never let a stale number
look live.** Every fetched value needs an explicit freshness state (live / stale / disconnected)
independent of the number itself — a blank or greyed cell beats a confident-looking wrong
one, the same principle trading-desk UIs use for stale quotes.

---

## Decision table: interaction type → technique → latency budget → library

| Interaction type | Technique | Latency budget | Library / API |
|---|---|---|---|
| Row select, filter toggle, tab switch, checkbox, sort column | Local/client state only, no network wait | **<100ms** (Nielsen "instantaneous" limit) | React state / Zustand — no data-fetch library needed |
| Status change, assign driver, mark detention start/stop, single-field edit | Optimistic mutation, instant UI update, silent success | UI updates **<100ms**; server confirms async, rollback if rejected | TanStack Query `onMutate`/`onError`/`onSettled`, SWR `optimisticData` + `rollbackOnError`, or `useOptimistic()` (React 19) |
| 4-step wizard step transition | Client-side state machine, prefetch next step's data on step N-1 | **<100ms** transition, prefetch during idle | React state + Speculation Rules (`prerender`, "moderate" eagerness) or manual prefetch on step focus |
| POD photo upload / batch photo review | Optimistic thumbnail insert + background upload with visible progress, never optimistic on final "approved" state | Immediate thumbnail (<100ms); upload progress visible if >1s | TanStack Query mutation + native `<progress>` / custom queue UI |
| Detention billing calculation, invoice generation, payment-adjacent actions | **No optimistic UI.** Show a real pending/processing state, confirm only on server ack | Spinner acceptable up to ~1s; beyond that, explicit "processing…" copy, not silence | Standard mutation + loading state (not optimistic) |
| Dense table initial load / dashboard panel load | Skeleton matching exact row/column dimensions, not generic shimmer block | Skeleton justified only when load is reliably **>500ms–1s**; under that, prefer nothing or a subtle inline spinner | CSS skeleton + `content-visibility:auto` + `contain-intrinsic-size` for long tables |
| Route / page navigation inside app | View Transitions API (same-document) for the chrome/layout; skip on the live-data region | Perceived instant if content is already cached; degrade to instant swap if unsupported | `document.startViewTransition()` with `if (!document.startViewTransition)` fallback |
| Hover-intent navigation (e.g., dispatcher hovering a load row before opening detail) | Hover/focus-triggered prefetch, cancelled if unhovered quickly | Prefetch fires after ~50-200ms hover-intent delay [inferred typical implementation] | Next.js `<Link prefetch>` incremental prefetching (v16+), or manual `mouseenter` debounce |
| Predictable next-page navigation (e.g., "next page" of a paginated table) | Speculation Rules API, `prefetch` (cheap) not `prerender` (expensive) unless very high confidence | Prefetch cost is low; reserve prerender for near-certain next click | Speculation Rules API (`<script type="speculationrules">`) |
| Live status cell / ticking counters / notification badge | No optimistic UI, no skeleton, no view-transition morph — direct value swap, but with explicit freshness indicator | Update must be visibly tied to a "live" state; disconnect must be visibly flagged | WebSocket/poll + freshness badge component (custom) |
| Dashboard panels with independent data sources (stats, activity feed, notifications) | Streaming via RSC Suspense boundaries per panel, parallel fetch | Shell paints immediately; each panel streams in as its own query resolves | React Server Components + `<Suspense>`, or Next.js Partial Prerendering |

---

## 1. Optimistic UI

**What mature teams apply it to, and what they never do.**

TanStack Query's canonical pattern (the de facto reference implementation most other
libraries mirror): in `useMutation`, the `onMutate` handler (a) cancels in-flight queries for
the affected key so they don't clobber the optimistic write, (b) snapshots the previous cache
value, (c) writes the optimistic value into the cache immediately, and (d) returns the
snapshot as `context`. `onError` uses that context to restore the previous value. `onSettled`
(not `onSuccess`) triggers the real refetch/invalidation so the cache is correct regardless of
outcome. ([TanStack Query docs](https://tanstack.com/query/latest/docs/framework/react/guides/optimistic-updates))

SWR mirrors this with `optimisticData` (write immediately) + `rollbackOnError` (revert
automatically on failure, then trigger revalidation to pull the authoritative value).
([SWR docs](https://swr.vercel.app/docs/mutation))

Apollo Client caches an `optimisticResponse` as temporary data until the real mutation
resolves; from v3.4+ it auto-clears `ROOT_MUTATION` fields after completion.
([Apollo docs](https://www.apollographql.com/docs/react/data/mutations))

**Linear's version is the deepest implementation found.** Linear inverts the client-server
relationship: IndexedDB in the browser *is* the primary database the UI reads from. Mutations
write to a MobX observable graph synchronously (`issue.title = 'x'; issue.save()`), which is
what makes edits feel instant — there's no request/response round trip in the critical path at
all; the network sync happens asynchronously afterward. Because MobX tracks per-property
observables, a change to one field of one issue re-renders exactly the components reading that
field — a 50-issue bulk update is 50 cell re-renders, not a full list re-render. Initial
mutations apply in "a few milliseconds" versus roughly 300ms for a typical fetch-then-render
CRUD cycle. If the server rejects a mutation, the observable reverts with "a brief flicker,"
but Linear's engineers note this is rare in practice because most invalid mutations are caught
client-side before a transaction is even created.
([performance.dev breakdown](https://performance.dev/how-is-linear-so-fast-a-technical-breakdown), [reverse-engineered sync engine, CTO-endorsed](https://github.com/wzhudev/reverse-linear-sync-engine))

Rails/Hotwire's Turbo 8 takes a server-driven variant: rather than client-side optimistic
state, it uses DOM **morphing** — a `<template>` with an inverted-state `<turbo-stream>` swaps
the element instantly, then reconciles with the server's broadcast response, using
diff-based morphing (not full replace) to avoid flicker and preserve focus/scroll state.
([Hotwire Club: Optimistic UI with Turbo 8 Morphs](https://hotwire.club/blog/2024-03-26-optimistic-ui-with-turbo-8-morphs/), [Turbo Handbook: page refreshes](https://turbo.hotwired.dev/handbook/page_refreshes))

**What never to apply optimistic UI to** — consensus across sources: financial transactions,
irreversible actions (permanent deletes), and any state where showing a false-positive success
could cause the user to act on it (e.g., placing an order against a balance that hasn't
actually cleared). Destructive deletes without an undo path should not show instant success —
there's no safe rollback once the user has mentally committed to the result.
([The Imperfect Builder: "Optimistic UI is an anti-pattern"](https://imperfectbuilder.com/blog/posts/optimistic-ui-is-an-anti-pattern), synthesis across DEV/SitePoint sources)

**For this console specifically:** status changes, driver/asset assignment, notification
read/dismiss, wizard step navigation → optimistic, yes. **Detention billing calculations and
invoice generation → no** — these are financially adjacent and should show a real pending
state, not a lie the system might have to walk back.

**Good rollback UX** (synthesized from TanStack/SWR patterns + Linear's approach): revert the
value silently and immediately (no jarring re-flash), then surface a small, specific,
dismissible error near the affected row (not a global toast that requires hunting) — "Could not
reassign to Driver X — [Retry]" beats a generic "Something went wrong." The goal is the user
never mentally banks a value that later turns out false; the shorter and more localized the
correction, the more the tool retains trust.

---

## 2. Skeletons vs spinners vs nothing — the evidence is genuinely split

**Case for skeletons:** Multiple UX-blog syntheses report skeleton screens are perceived as
~20-30% faster than an identical wait shown with a spinner, on the reasoning that a spinner
signals *activity* with no information about progress or shape, while a skeleton previews the
page's structure and reduces the surprise of the layout appearing.
([LogRocket](https://blog.logrocket.com/ux-design/skeleton-loading-screen-design/), [UX Collective](https://uxdesign.cc/what-you-should-know-about-skeleton-screens-a820c45a571a))

**Case against — and this is the one Boss should actually weight, because it's an actual
study, not a listicle:** Viget's controlled test (136 participants, mobile, three identical
loading durations shown as skeleton / spinner / blank) found skeletons performed *worst*:

- Agreement with "loaded quickly": spinner 74%, blank 66%, **skeleton 59%**
- Disagreement/dissatisfaction: spinner 10%, blank 26%, **skeleton 36%**
- Perceived duration: spinner 2.41s, blank 2.29s, **skeleton 2.82s** (identical actual time)
- Post-load task completion: spinner/blank ~9.5s, **skeleton 10.54s**

Viget's hypothesis: skeletons draw more visual attention (novelty), which makes the wait feel
longer, and the benefit (if any) may only show up on genuinely long waits, not the short ones
most apps actually have. ([Viget: "A Bone to Pick with Skeleton Screens"](https://www.viget.com/articles/a-bone-to-pick-with-skeleton-screens), underlying [academic study, ResearchGate](https://www.researchgate.net/publication/326858669_The_effect_of_skeleton_screens_Users'_perception_of_speed_and_ease_of_navigation))

**Reconciling the two camps:** the sources that favor skeletons are almost all product/design
blogs re-citing older claims (Facebook/LinkedIn/YouTube "use them, so they must work"); the
one designed experiment says the opposite for short waits. The practical read: **skeletons earn
their keep on content-rich, structurally-predictable panels with genuinely nontrivial load
time** (a full table load, a dashboard refresh after navigation) — not on short, atomic, or
already-fast interactions, where a plain spinner or nothing at all is safer.

**Latency threshold that actually matters:** tie the choice to Nielsen's bands (below).
Under ~1s: don't show a skeleton at all — either it resolves before the skeleton even registers
(pure waste) or it resolves right as attention shifts to the skeleton (which is the point at
which skeletons apparently backfire, per Viget). Above ~1s and up to ~10s, on a content-heavy
panel with predictable structure, a *dimension-matched* skeleton is defensible. Beyond 10s, the
guidance shifts to progress indication with an actual completion estimate, not either loading
pattern. **What causes skeletons to feel slower:** (a) too much visual detail/shimmer that
draws attention to the wait itself, (b) skeleton shape that doesn't match final content
(the reflow when real content lands undoes the trust the skeleton built), (c) using them for
waits under ~500ms where the flash-then-swap is itself distracting.

---

## 3. Layout stability — zero CLS on variable-height content

The core technique: the skeleton (or space-holder) must reserve **the exact final dimensions**
of the real content, not an approximation. For genuinely variable content (a table row whose
height depends on wrapped text, a notification list with 1-3 line messages):

- Use `min-height` or `aspect-ratio` sized to the *maximum expected* content size, not the
  average — CLS is triggered by growth, not by wasted whitespace.
  ([web.dev: Optimize CLS](https://web.dev/optimize-cls/))
- For long/virtualized lists and tables, `content-visibility: auto` + `contain-intrinsic-size`
  is the current (2026) mechanism: off-screen rows are skipped from layout/paint work entirely
  (measured ~40% rendering/paint improvement on long lists), while `contain-intrinsic-size`
  tells the browser what placeholder size to reserve so the scrollbar and layout don't jump
  when rows enter/leave the render boundary. `contain-intrinsic-size: auto <value>` lets the
  browser remember the last-rendered size of a row once it has been measured once, which is the
  right default for a table where row heights vary but are roughly stable per data type.
  Browser support as of 2026 is Chromium-family only (Chrome/Edge/Opera) — needs a fallback for
  Safari/Firefox. ([web.dev: content-visibility](https://web.dev/articles/content-visibility), [DebugBear](https://www.debugbear.com/blog/content-visibility-api))
- Practically for the dispatch table: pre-measure or fix row height where the data model allows
  (status pill + truncated text = predictable height), and only let genuinely variable rows
  (e.g., a row with an expandable POD thumbnail) grow via explicit expand/collapse transitions,
  never an unannounced reflow.

---

## 4. Streaming and progressive rendering (RSC + Suspense / PPR)

**Boundary placement is the whole game.** The rule that recurs across sources: **one Suspense
boundary per independent data dependency, grouped by what's visually/logically displayed
together** — if two pieces of data always render together, they share a boundary; if they're
independent (stats panel, activity feed, notification panel), they get separate boundaries so
they stream and resolve in parallel rather than serially.

Two failure modes, both real:
- **Too few boundaries** — wrapping the entire dashboard in one `<Suspense>` means nothing
  paints until the *slowest* of three panels resolves, which defeats the purpose of streaming
  entirely.
- **Too many boundaries** — a boundary around every individual stat card causes a "popcorn
  effect": dozens of skeleton→content flips firing in rapid, staggered succession, which reads
  as jankier than one clean, slightly longer load.
  ([synthesis of Next.js docs + patterns.dev + community guidance](https://nextjs.org/learn/dashboard-app/streaming), [patterns.dev: Streaming SSR](https://www.patterns.dev/react/streaming-ssr/))

For a data-dense dispatch dashboard specifically: this buys the ability to paint the app shell,
nav, and cached/static chrome instantly while the live-status table, notification centre, and
any per-panel stat blocks each stream in independently as their own queries resolve — the user
sees the frame and starts orienting before every number has arrived. It backfires if the
boundaries are drawn along technical lines (one query = one boundary) rather than visual ones
— that produces the popcorn effect described above.

**Partial Prerendering (Next.js, no longer experimental as of Next 16)** goes one step further
than Suspense-only streaming: it prerenders a static shell (nav, table headers, layout) at
build time and serves it from the CDN instantly, then streams only the dynamic Suspense
boundaries (per-row live status, notification count, current-user greeting) at request time.
This is explicitly called out as a fit for "dashboard and app shell" cases — cached layout +
personalized/live widget. ([Vercel: Partial Prerendering](https://vercel.com/blog/partial-prerendering-with-next-js-creating-a-new-default-rendering-model), [Vercel PPR docs](https://vercel.com/docs/partial-prerendering))

---

## 5. View Transitions API

**Browser support, 2026:**
- Same-document transitions: Chrome/Chromium since Chrome 111, Safari/WebKit since Safari 18,
  Firefox/Gecko since Firefox 144 — effectively universal now.
- Cross-document transitions (MPA-style, full navigation): Chrome since Chrome 126; Safari and
  Firefox **do not yet support cross-document transitions** as of mid-2026 — Firefox support is
  expected but not shipped, and there's hope it lands in Interop 2026.
  ([MDN: ViewTransition](https://developer.mozilla.org/en-US/docs/Web/API/ViewTransition), [Trade Assistance: Cross-Document View Transitions 2026 guide](https://trade-assistance.com/blog/cross-document-view-transitions-mpa-2026/), [TestMu: browser support](https://www.testmuai.com/learning-hub/view-transitions-api-browser-support/))

Practical implication for a dispatcher console (which will be a client-rendered SPA-style app,
same-document navigations): this is safe to use broadly today; cross-document isn't a
dependency you'd need for an internal app-shell architecture.

**Usage patterns:** route/tab changes (wrap the state update in `document.startViewTransition()`)
and shared-element morphs (assign the same `view-transition-name` to a source element — e.g. a
row in the load list — and its destination — e.g. the detail panel header — so the browser
animates a morph between them instead of a cut).

**Gotchas that matter for a dashboard:**
- Two elements sharing one `view-transition-name` in the same snapshot silently kills the
  transition (browser can't decide which to morph) — scope names to unique instance IDs, not a
  shared class.
- Always guard with `if (!document.startViewTransition) { updateCallback(); return; }` for
  unsupported browsers — no error, just an instant update.
- Respects `prefers-reduced-motion` automatically for the morph, but should still be explicitly
  wrapped/guarded for a fully accessible minimal-motion path.
- **Explicitly recommended against** for: frequent rapid updates (data refreshing every ~100ms),
  large data-heavy tables (hundreds of rows), and real-time dashboards where "live data updates
  should be instant, not animated." This maps directly onto this console's live-status column
  and notification centre — do not apply View Transitions there; reserve it for the wizard
  step-to-step transitions, tab switches, and row→detail-panel morphs.
  ([synthesis of DEV/Egnworks/animationpatterns.art guides](https://animationpatterns.art/animations/shared-element-layout-transition/))

---

## 6. Prefetching and speculative loading

**Speculation Rules API** (Chrome-native, declarative) offers three eagerness tiers:
- **Immediate/eager** — fires on page load, for very high-confidence next navigations.
- **Moderate** — fires on hover or viewport visibility.
- **Conservative** — fires only on pointerdown/explicit interaction.

And two modes: **prefetch** (download the response, don't render — cheap, low risk, safe to
apply broadly across "significant pages") vs **prerender** (fully render the destination in a
hidden tab — much higher upfront cost, but the navigation itself becomes near-instant since
everything is already painted). Chrome caps concurrent speculation: 2 eager prerenders, 10
moderate/conservative. Guidance is explicitly to start with prefetch broadly and reserve
prerender for near-certain clicks. ([Chrome for Developers: implementing speculation rules](https://developer.chrome.com/docs/web-platform/implementing-speculation-rules), [MDN: Speculation Rules API](https://developer.mozilla.org/en-US/docs/Web/API/Speculation_Rules_API))

**Measured win:** one independent test found prerender cut perceived load time by ~47%
(10,644ms → 5,679ms in that test's conditions), and sites running speculation rules at moderate
eagerness saw ~28% of navigations successfully prefetched/prerendered, with a prefetched-path
p75 TTFB of ~45ms. ([LogRocket: does Speculation Rules API boost web speed?](https://blog.logrocket.com/speculation-rules-api-web-speed-test/))

**Measured cost of getting this wrong:** one developer's blog reported Next.js `<Link>`
hover-prefetch quietly burning 15GB/month of bandwidth from unintended hovers; after scoping
prefetch behavior down, bandwidth dropped 40-60%. The specific failure mode called out: when
many links are visually stacked (a table full of clickable rows, exactly this console's
situation), users hover over several rows before clicking the one they want, so naive
hover-prefetch fires far more requests than clicks that follow. Next.js 16's "incremental
prefetching" mitigates this by fetching only uncached segments, cancelling requests when a link
leaves viewport, and reprioritizing on actual hover/focus.
([Mike Bifulco: reducing Next.js bandwidth with Link prefetch](https://mikebifulco.com/posts/reduce-nextjs-bandwidth-with-link-prefetch), [Next.js prefetching guide](https://nextjs.org/docs/app/guides/prefetching))

**For this console:** scope prefetch to (a) the *next* wizard step once the current step is
valid/complete — high confidence, cheap; (b) the next page of a paginated table — high
confidence; (c) explicitly **not** every row in a dense table on hover — the stacked-links
failure mode above applies directly. Use a hover-intent debounce (~150-200ms) [inferred typical
value; not found as a hard number in sources] before firing prefetch on row hover, if row-level
prefetch is used at all.

---

## 7. Response-time thresholds — Nielsen's 0.1 / 1 / 10s, still the reference model

Nielsen's three limits (originally 1993, restated by NN/g and still cited as current in 2026 —
"the same today as when Nielsen wrote about them," per Nielsen's own retrospective):

- **0.1s** — the ceiling for feeling like *direct manipulation*; the only feedback needed is the
  result itself appearing. This is the target for row select, toggle, filter, checkbox — any
  action the user perceives as touching the UI directly, not "requesting" something.
- **1.0s** — the ceiling for keeping the user's flow of thought uninterrupted; the user notices
  the delay but doesn't lose their mental thread. This is where a lightweight, immediate loading
  cue (not necessarily a skeleton) becomes worthwhile.
- **10s** — the ceiling for keeping attention on the task at all; beyond this users mentally
  context-switch, so the system must give a progress indicator and, ideally, a completion
  estimate.
  ([NN/g: Response Time Limits](https://www.nngroup.com/articles/response-times-3-important-limits/), [NN/g: Powers of 10 — Time Scales in UX](https://www.nngroup.com/articles/powers-of-10-time-scales-in-ux/))

**Modern mapping onto Core Web Vitals' INP** (which formalizes the 0.1s idea for real
interactions): Google's INP "good" threshold is **≤200ms** at the 75th percentile of a page's
interactions, needs-improvement is 200-500ms, poor is >500ms. Note this is *not* the same
number as Nielsen's 0.1s — 200ms is the measured-responsiveness bar (input delay + processing +
next paint), calibrated to what's achievable in practice, while 0.1s is the perceptual "feels
instantaneous" bar. Practically: **treat 100ms as the design target and 200ms as the hard
compliance ceiling** for anything the dispatcher does dozens of times an hour (row select,
status toggle, filter). ([web.dev: INP](https://web.dev/articles/inp))

---

## 8. Offline and flaky networks — and the "never show a wrong number" rule

**Queueing/retry pattern (general, synthesized across offline-first sources):** mutations
attempted while offline or during a failed request go into a durable local queue (IndexedDB or
equivalent), retried with exponential backoff and a maximum retry ceiling, with the queue state
(pending / retrying / failed) visible to the user rather than silent. Linear's implementation is
the concrete reference: mutations queue in IndexedDB's transaction store, persist across
reloads, and flush automatically on reconnect; the app stays usable offline for reads and most
writes in the meantime. ([performance.dev](https://performance.dev/how-is-linear-so-fast-a-technical-breakdown))

**Conflict resolution options**, roughly in order of implementation complexity: Last-Write-Wins
by timestamp (simplest, acceptable for single-owner fields like "assign driver"), custom merge
rules for specific fields, and CRDTs for genuinely concurrent multi-user edits (Linear uses
Yjs CRDTs specifically for its collaborative text/description fields, not for simple
field-level state). For a dispatch console where most edits are single-dispatcher-owned
(assigning a load, marking detention), LWW is very likely sufficient — CRDTs are overkill unless
multiple dispatchers edit the same record simultaneously as a normal workflow. [inferred:
recommendation, not found verbatim in a source, based on synthesis of the offline-first
material and the described use case]

**The rule that matters most for a dispatch board specifically — never show stale data as
live.** This is exactly the problem trading-desk UIs solved for stale quotes, and the pattern
transfers directly: a data value is only meaningful together with its *freshness state* — the
same number can represent a live tick, a cached snapshot, or a disconnected last-known value,
and showing them identically is what causes bad decisions. The concrete implementation pattern
from trading dashboards: track a "last heartbeat" timestamp per data source; if it exceeds a
threshold (their example: 30s), the UI element visibly changes state (amber/red badge, "stale"
label) rather than continuing to display the number as if current. A disconnect, a stale value,
a delayed update, and "no update needed because nothing changed" are four different states and
need four different visual treatments, not one silent number.
([EODHD: real-time market data reliability — stale price detection](https://eodhd.com/financial-academy/fundamental-analysis-examples/real-time-market-data-reliability-stale-price-detection-rest-fallback-and-websocket-recovery), [insightbig: real-time market data fails quietly](https://www.insightbig.com/post/real-time-market-data-fails-quietly-here-s-how-to-make-it-recoverable))

Applied directly to the console: the live-status column, notification centre, and any
"last synced" indicator should carry an explicit freshness badge (live / Xs ago / disconnected)
independent of the value shown, and on a confirmed disconnect the correct behavior is to grey
out or blank the affected cells — never leave the last good number sitting there looking
current. This directly matches the brief's own instruction and is well-precedented outside
logistics.

---

## 9. Measurement — INP, LCP, CLS in production

**Thresholds (unchanged for 2026, confirmed across multiple current sources):**

| Metric | Good | Needs Improvement | Poor |
|---|---|---|---|
| LCP (Largest Contentful Paint) | ≤2.5s | 2.5-4.0s | >4.0s |
| INP (Interaction to Next Paint) | ≤200ms | 200-500ms | >500ms |
| CLS (Cumulative Layout Shift) | ≤0.1 | 0.1-0.25 | >0.25 |

Both LCP and CLS thresholds are measured at the page level; Core Web Vitals compliance
requires 75% of real-user page loads (via Chrome's CrUX dataset) to be "good" on all three.
([web.dev: INP](https://web.dev/articles/inp), [industry 2026 recap sources](https://www.digitalapplied.com/blog/core-web-vitals-2026-inp-lcp-cls-optimization-guide))

**INP's three sub-phases** (useful for actually debugging a slow interaction, not just scoring
it): input delay (main-thread contention before the handler even starts), processing duration
(the handler's own work), and presentation delay (time from handler completion to next paint).
For a data-dense dispatch table, input delay is the most likely offender if the main thread is
busy re-rendering large tables — this is the direct argument for the `content-visibility`/
virtualization techniques in section 3, and for keeping optimistic updates scoped (per-row
re-render, à la Linear's MobX approach) rather than triggering full-list re-renders.

**Instrumentation:** Google's `web-vitals` JS library is the standard RUM instrument — a tiny
library that reports LCP/INP/CLS from real users matching exactly how Chrome measures them
internally. Typical production setup: hook each metric's callback, ship the value (plus
navigation context) to an observability backend (OpenTelemetry metrics is one documented path),
and build alerting/dashboards on top rather than relying solely on lab tools or CrUX's
delayed aggregate reporting. ([DebugBear: monitor Core Web Vitals with web-vitals.js](https://www.debugbear.com/blog/core-web-vitals-js), [OneUptime: web vitals via OpenTelemetry](https://oneuptime.com/blog/post/2026-02-06-core-web-vitals-lcp-fid-cls-opentelemetry-metrics/view))

---

## Anti-patterns and the specific failure they cause

| Anti-pattern | Failure it causes |
|---|---|
| Optimistic UI on financial/irreversible actions (invoice totals, payment, permanent delete) | User acts on a value the system later reverses; trust in the tool collapses faster than any latency problem would cause |
| Generic shimmer skeleton that doesn't match final content dimensions | Reflow on content-load (defeats CLS goal) *and* the mismatch itself undermines the trust-building purpose of the skeleton |
| Skeleton on a sub-1s load | Per Viget's data, this is the exact condition where skeletons measured *worse* than a spinner or nothing — novelty/attention cost without enough wait to amortize it |
| One Suspense boundary around an entire multi-panel dashboard | Blocks the whole page on the single slowest data source; defeats streaming entirely |
| Suspense boundary per individual field/stat | "Popcorn effect" — dozens of staggered skeleton-to-content flips reads as jankier than one clean wait |
| `view-transition-name` reused across rows/instances | Browser silently drops the transition when two elements share a name in one snapshot |
| View Transitions applied to live-updating cells (status, notification counts) | Morph animation fires on every data tick, reads as visual noise, not polish |
| Broad hover-prefetch on a dense table of stacked links/rows | Every incidental hover fires a fetch; measured real-world cost was tens of GB/month of wasted bandwidth |
| `prerender` (not `prefetch`) applied broadly instead of to near-certain navigations | High resource cost for low actual click-through; Chrome's own concurrency caps (2 eager prerenders) exist because of this |
| Showing a cached/stale number identically to a live one, with no freshness indicator | User makes an operational decision (e.g., "detention has stopped") on data that's actually minutes old — the single highest-stakes failure mode on a dispatch board specifically |
| Optimistic update without a defined rollback path | The documented "most dangerous anti-pattern" in optimistic UI guidance — assuming the server call always succeeds |

---

## Open questions not resolved by this research

1. **Exact hover-intent debounce value mature teams use in production** (this brief used
   ~150-200ms as an inferred typical figure; no source gave a specific, sourced number for a
   dense-table row-hover use case specifically). Needs either direct testing or a deeper source
   dig (Linear/Notion have not published this specific number).
2. **Whether CRDTs are warranted for this console's data model** — depends on whether multiple
   dispatchers ever concurrently edit the same load/asset record as a normal workflow (not just
   a rare collision). This is a product-decision question, not answerable from performance
   research alone.
3. **content-visibility's Safari/Firefox gap** — no clean cross-browser equivalent was found
   in this pass; if the console must support non-Chromium browsers for dispatchers, a
   virtualization library (react-window / TanStack Virtual) is the safer, broadly-supported
   substitute and should be researched separately if not already the plan.
4. **Concrete latency numbers for Speculation Rules `prerender` cost** (memory/CPU overhead per
   concurrent prerender) were not found with hard figures — only the concurrency caps (2 eager)
   were documented, which implies real cost but wasn't quantified in the sources reviewed.
5. **Whether Viget's 2017-era finding still replicates on modern hardware/networks** — the study
   is not recent, and skeleton implementations have evolved (better dimension-matching,
   subtler shimmer). Treat the "skeletons can feel slower" finding as a real risk to design
   around, not a settled verdict against skeletons categorically.

---

*Compiled 2026-08-07. All non-inferred claims sourced above; items without a citable source are
explicitly marked `[inferred]`.*
