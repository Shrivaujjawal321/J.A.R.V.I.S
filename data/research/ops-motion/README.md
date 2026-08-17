# Research — motion, speed and interaction for the mySHIPR dispatch console

Five parallel research briefs, run 2026-08-07. The question behind all of them:
**can this console feel like a top-tier product, and what specifically would that take?**

The framing that shaped every brief: this is an *operator tool*, not a marketing site.
A dispatcher lives in it all day and repeats the same actions hundreds of times. That
single fact inverts most "polish" advice — the answer is usually less motion, not more.

Every brief marks unverified reasoning as `[inferred]`. Where a number could not be
found, the agent said so instead of estimating.

| File | Question | The one-line answer |
|---|---|---|
| `01-motion-system.md` | What durations and easings do the best dense tools actually use? | 100–300ms band, nothing past 350ms, ease-out in / ease-in out, and **zero animation on anything repeated hundreds of times a day** |
| `02-perceived-performance.md` | What makes an app feel instant? | Optimistic UI is the biggest lever — but never for money or irreversible actions. Skeletons only earn their keep past ~1s |
| `03-dense-tables.md` | How to build tables that stay fast and usable, including on a phone? | TanStack Table + Virtual + URL state. At 375px use cards and a drawer, **not** a scrolling table |
| `04-keyboard-first.md` | What makes a tool fast for an expert? | Cmd+K palette + a few single-letter shortcuts + arrow-key grid nav + disciplined focus restoration |
| `05-live-data-alerts.md` | How to show live data and alerts without causing alarm fatigue? | Four severity tiers. The SOS only works because everything below it stays silent |

---

## Findings that contradict what is already built

1. **Mobile tables.** The Figma responsive frames give tables a 600px minimum with
   horizontal scroll at 375px. Every source reviewed calls that an anti-pattern below
   ~480px: a dispatcher checking a load one-handed in a cab scrolls past hidden columns
   and never knows they missed them. The correct pattern is card-per-row with a details
   drawer. Horizontal scroll with a pinned identity column is right for 480–900px only.

2. **Virtualisation + sticky columns is unresolved upstream.** Row virtualisation needs
   absolute positioning, which breaks sticky columns — there is a live open discussion and
   an open bug in TanStack. Budget a spike; do not assume it is a copy-paste pattern.

3. **Two tables should probably not be virtualised at all.** A virtualised grid reports a
   wrong row count to screen readers. AG Grid's own accessibility docs recommend disabling
   virtualisation or falling back to pagination where full compliance matters. The audit
   log and the RBAC matrix are the two compliance-sensitive tables here.

## Findings that validate what is already built

- The console refuses to show cached figures when the API is unreachable, on the stated
  reasoning that a stale dispatch board is worse than an empty one. Trading-desk UI
  precedent says exactly this: never render a stale number as though it were live.
- Note tones already separate warning from information from blocking. The severity
  research says the same, and adds that colour alone is not enough — shape and symbol too.

## The domain catch worth remembering

Do not animate the detention timer or the HOS bar's *numeric value*. Those are not
decorative counters; they are the evidence in a billing dispute and a legal compliance
clock. A tweened number is a number that is briefly wrong. Animate the container's colour
state when it crosses a threshold — never the digits.
