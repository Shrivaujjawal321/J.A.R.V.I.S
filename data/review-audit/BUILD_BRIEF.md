# mySHIPR Carrier Console — Figma → Frontend + Backend
## Enhanced build brief (draft for Boss's approval — nothing has been executed)

---

## 0. What Boss asked for, restated precisely

> Once the Figma design is complete, build both the frontend and the backend from it.
> Divide the work into chunks and hand them to the frontend/backend builders incrementally so the work stays precise.
> After each build lands, spawn critic agents to review it **against the Figma design** and confirm nothing was missed.
> Jarvis orchestrates and keeps the whole thing executing in an organised way.

Two things are added below that Boss did not say but that follow from the audit we just ran, and that I think he wants:

1. **The console's 25 domain/logic defects must not be reproduced.** The Figma file faithfully copied several of them. If we build straight from the design we inherit them. Those are listed in `FINDINGS.md` section H and are treated as fix-forward items, not specification.
2. **The contract comes before the code.** Frontend and backend agree on a typed API contract per chunk before either writes an implementation, so they can be built in parallel without drifting.

---

## 1. Sources of truth (in priority order)

| Rank | Source | What it is authoritative for |
|---|---|---|
| 1 | **Figma file** `mySHIPR — Carrier Console` | Layout, spacing, colour, type, component structure, states, responsive behaviour, navigation |
| 2 | **`mySHIPR_Carrier_Console_v4 (2).html`** | Behaviour, data shapes, validation rules, error codes, business logic |
| 3 | **`data/review-audit/REVIEW_DOC.txt`** | Client requirements — what must exist and why |
| 4 | **`data/review-audit/FINDINGS.md`** | Known gaps and known defects. Section H must be FIXED, not copied |
| 5 | **`mySHIPR_Open_Items_for_Client.md`** | Business questions awaiting client answer — build behind a flag, do not guess |

Rule: if 1 and 2 disagree, the Figma wins on appearance and the console wins on behaviour. If either disagrees with 3, raise it — do not silently pick.

---

## 2. Proposed tech stack — **needs Boss's confirmation before anything is built**

The team lead specified the pipeline (HTML → Figma → frontend → backend) but not the stack. Proposal:

**Frontend**
- Next.js 15 (App Router) + React 19, TypeScript strict
- Tailwind 4 with the design tokens generated **from the Figma variables**, not hand-typed
- shadcn/ui as the primitive layer, wrapped in our own components so the Figma component names map 1:1 (`Chip/Status` → `<ChipStatus>`)
- TanStack Query for server state, `nuqs` for URL state (filters, sort, page — the console keeps all of these in URL-shaped state already)
- Playwright for E2E + visual regression against Figma exports

**Backend**
- Node + TypeScript, Fastify or NestJS
- PostgreSQL + Drizzle (or Prisma), migrations in-repo
- Zod schemas shared with the frontend as the single contract source
- OpenAPI generated from those schemas, not written by hand
- RBAC enforced server-side, mirroring the console's `RBAC` matrix — never trusted from the client

**Why this stack:** it is the one my builder agents are strongest in, it gives a shared type contract between the two halves (which is what makes chunked parallel work safe), and Tailwind tokens can be generated directly from the Figma variables so "pixel perfect" is mechanical rather than eyeballed.

**Alternatives if Boss's company has a standard:** if the team already uses Vite + React Router, or Django/Spring on the backend, say so now — the chunking and review protocol below are stack-agnostic and I will swap the builders.

---

## 3. Chunking — vertical slices, not layers

The work is divided into **10 chunks**. Each chunk is a vertical slice: schema → API → UI → tests. A chunk is never "all the backend" or "all the screens", because that is what makes integration break at the end.

| # | Chunk | Contains | Depends on |
|---|---|---|---|
| **C0** | **Foundations** | Design tokens generated from Figma variables · typography scale · the 40-component library with every variant/state · Storybook · visual-regression harness | — |
| **C1** | **Shell + auth** | App shell, sidebar (all 12 sections + sub-items), top bar, breadcrumb, routing for all 42 routes, role switcher, session handling, the 5 ERR-GEN states, RBAC gate | C0 |
| **C2** | **Fleet** | 8 screens · truck/trailer registry · CO-10/CO-11 validation · vehicle documents + CO-09 expiry ladder · devices & ELD · HOS · truck & trailer drawers · register-truck and bulk-upload forms | C0, C1 |
| **C3** | **Drivers** | 3 screens · driver record + CO-19/CO-20 compliance · CO-21 ratings · CO-22 roster · dispatch-eligibility gate · driver drawer · add-driver form | C0, C1 |
| **C4** | **Loads** | 6 screens · tender accept/decline · **the 4-step assignment wizard** · POD review with photo evidence · close-out · load drawer | C0, C1, C2, C3 |
| **C5** | **Trips** | 5 screens · live tracking · progress · trip↔load relationship | C4 |
| **C6** | **Driver Ops** | 3 screens · detention billing · exceptions & safety · two-way messaging | C3, C4 |
| **C7** | **Yards + Notifications** | Yards CRUD with geo-coordinates · notification centre with ack/dismiss/SOS lock · deep links to source records | C1 |
| **C8** | **Reports + Earnings** | 5 report panels · analytics · CSV export · earnings, payments, disputes · driver settlement · payment-details drawer | C2, C3, C4 |
| **C9** | **Settings** | 10 screens · company profile · users & roles + RBAC matrix · audit logs · sessions · documents · contract · finance · capacity | C1 |

**Ordering rationale:** C0 and C1 are the spine — everything else instantiates them, so they are built and reviewed first and alone. C2–C3 are pure master data with no cross-dependencies, so they can run in parallel. C4 is the product's core action and depends on both, so it comes after. C5–C9 fan out again.

**Chunk size discipline:** if a chunk's diff exceeds roughly 2,500 lines or 6 screens, split it before starting. A chunk that cannot be reviewed in one pass will not be reviewed properly.

---

## 3b. Interaction standards — these apply to every chunk

Derived from five research briefs in `data/research/ops-motion/` (each claim there carries
a URL; anything reasoned rather than found is marked `[inferred]`). These are not polish
to add at the end — they change component APIs, so they belong in C0 and in every chunk
spec after it.

### Motion
- Duration scale, already shipped as Figma variables and documented on the `Motion — spec`
  board: `none 0 · instant 90 · fast 150 · base 220 · slow 300 · toast-in 180 ·
  toast-out 230 · skeleton-swap 130` (ms). Nothing animates past 350ms.
- Ease-out entering, ease-in leaving, and exits run faster than entries.
- **Zero animation on anything a dispatcher repeats hundreds of times a day** — status
  chip changes, row selection, HOS bar updates, detention ticks, every keyboard action.
  Motion is spent only on the wizard, drawers and the notification centre.
- Springs (not CSS keyframes) for anything re-triggerable mid-flight; keyframes visibly
  snap when interrupted.
- `prefers-reduced-motion` collapses spatial transitions to a 100ms opacity crossfade but
  never removes the only signal that something changed.
- **Never animate a number that is evidence.** The detention timer and the HOS clock are a
  billing record and a legal compliance clock. Animate the container's colour at a
  threshold crossing; never the digits.

### Perceived speed
- Loading ladder: under 100ms show nothing · 100–400ms a small spinner · 400ms–3s a
  skeleton shaped like the real content · over 3s skeleton plus progress text.
- Optimistic UI on tender accept/decline, acknowledgements, filters, sort, assignment.
- **Never optimistic:** detention "raise as billable", payment approve/pay, POD close-out,
  and any delete. Money and irreversible actions wait for the server.
- Never render a cached figure as though it were live. Every live surface carries a
  freshness state (live / stale / disconnected) driven by a heartbeat.

### Tables
- TanStack Table v8 + TanStack Virtual on native `<table>` markup; filter, sort and page
  state in the URL via `nuqs` so a dispatcher can share a link to exactly what they see.
- Server-side filter and sort with pagination or load-more — not pure infinite scroll,
  which breaks shareable positions and range selection.
- Density: comfortable 48px default, compact 36–40px toggle, persisted per user.
- **Below 480px a table becomes a list of cards with a details drawer.** A scrolling grid
  on a phone hides compliance columns from a dispatcher checking a load one-handed, and
  they never learn they missed one. Horizontal scroll with a pinned identity column is
  correct for 480–900px only.
- Selection must distinguish "this page" from "all rows matching the filter" explicitly.
- **Risk to schedule:** sticky header + sticky first column + row virtualisation together
  is unresolved upstream in TanStack (open discussion and open bug). Spike it before
  committing to the combination.
- **Audit Log and the RBAC matrix should probably not be virtualised at all** — a
  virtualised grid reports a wrong row count to screen readers, and these two are the
  compliance-reviewed tables. Paginate them instead.

### Keyboard
- `Cmd/Ctrl+K` command palette, context-scoped and fuzzy-ranked · `/` local filter ·
  `?` shortcut sheet · `g` then a letter to jump between sections.
- Arrow keys as the baseline for grid navigation with `j`/`k` as an overlay; `Enter`
  opens a row or advances a wizard step; `Cmd/Ctrl+Enter` submits from anywhere.
- Bare single letters only for genuinely high-frequency actions. **Flagged conflict:**
  bare letters collide with NVDA/JAWS browse-mode quick-nav keys. DOM focus is supposed to
  flip the screen reader into forms mode — verify with a real screen reader before
  shipping rather than assuming.
- Focus restoration is the part teams get wrong: after a drawer closes, after a row is
  deleted, after a bulk action, after an async action resolves.

### Live data and alerts
Four tiers. The tier below matters because **the SOS only works if everything under it
stays silent** — that is the documented antidote to alarm fatigue, where 80–99% false
alarms train people to ignore real ones.

| Tier | Cases | Encoding | Motion | Sound | Ack |
|---|---|---|---|---|---|
| P0 | Driver SOS | Full-width banner, distinct shape, top z-index | One entrance, then static | Yes — distinct repeating pattern | Required, logged, escalates if unacked in 60–90s |
| P1 | HOS violation imminent | Red + triangle + text | Flash once on entering the window | Opt-in, off by default | One-click dismiss, reason logged |
| P2 | Detention accruing, document expiring | Amber + diamond + counting text | One pulse at threshold crossing only | No | Visible in a queue |
| P3 | Load tendered, GPS ping, counters | Neutral | None | No | None |

- Severity is never colour alone — colour plus shape plus symbol.
- Deduplicate by `(entity_id, alert_type)`; re-notify only on a state change, with a
  cooldown. A flapping GPS signal must not produce an alert per refresh.
- Timers: `setInterval` drifts over hours and browsers throttle background tabs. Use a
  worker and isolate the re-render to the one changing value.
- SSE rather than WebSocket for this one-way push case, with an explicit per-source
  state machine so a dropped connection is visible rather than silently stale.

## 4. The per-chunk pipeline (identical for every chunk)

```
  ┌── 1. CONTRACT ──────────────────────────────────────────────┐
  │  Jarvis writes the chunk spec:                              │
  │   · which Figma frames are in scope (by exact frame name)    │
  │   · the Zod schemas + endpoint list                          │
  │   · the console behaviours and validation rules to preserve  │
  │   · the FINDINGS.md section-H defects to FIX, not copy       │
  │   · the acceptance checklist                                 │
  └──────────────────────────┬──────────────────────────────────┘
                             │  (Boss sees this before build starts)
  ┌──────────────────────────▼──────────────────────────────────┐
  │  2. BUILD — backend agent and frontend agent in PARALLEL     │
  │     both bound to the same contract; frontend mocks the API  │
  │     from the Zod schemas until the backend lands             │
  └──────────────────────────┬──────────────────────────────────┘
  ┌──────────────────────────▼──────────────────────────────────┐
  │  3. INTEGRATE — Jarvis wires them, runs the app, screenshots │
  │     every in-scope screen at 1440 / 900 / 375                │
  └──────────────────────────┬──────────────────────────────────┘
  ┌──────────────────────────▼──────────────────────────────────┐
  │  4. CRITICS — 4 adversarial agents, in parallel              │
  └──────────────────────────┬──────────────────────────────────┘
  ┌──────────────────────────▼──────────────────────────────────┐
  │  5. GATE — Jarvis verifies each finding himself, fixes the   │
  │     real ones, re-runs critics. No chunk advances with an    │
  │     open BLOCKER. Boss gets a one-screen report.             │
  └─────────────────────────────────────────────────────────────┘
```

### The four critics per chunk

| Critic | Question it answers | Evidence it must cite |
|---|---|---|
| **Visual parity** | Does the built screen match the Figma frame — every panel, column, chip, state, at all three widths? | Side-by-side screenshot + Figma frame name + the specific element that differs |
| **Behaviour parity** | Does it do what the console does — validations, error codes, empty/loading/denied states, filters, sort, pagination, RBAC? | The console function name and line, and the built code path |
| **Contract + data** | Does the API match the agreed schema? Any endpoint the UI needs that does not exist, or returns a shape the UI cannot render? Migrations reversible? N+1s? | Endpoint, schema diff, query plan |
| **Domain correctness** | Does it reproduce any FINDINGS.md section-H defect? Is the FMCSA/HOS/detention/AWB logic right? One definition of the dispatch gate, not four? | The regulation or the finding reference |

Critics are told: **find what is missing or wrong, do not praise, cite evidence, propose one concrete fix.** Same discipline as the audit we just ran — where 2 of 47 findings turned out to be wrong and I rejected them rather than acting on them.

---

## 5. Definition of done — per chunk

A chunk is done only when **all** of these hold:

- [ ] Every in-scope Figma frame has a route that renders it
- [ ] Visual diff vs the Figma export is within tolerance at 1440, 900 and 375
- [ ] Every interactive element in the design does something (no dead buttons — this was a named defect in the client's own review)
- [ ] Loading, empty, error and permission-denied states exist for every data surface
- [ ] Every console validation rule in scope fires, with the same ERR-GEN code and HTTP status
- [ ] RBAC enforced server-side and reflected in the UI
- [ ] No section-H domain defect reproduced; each one either fixed or explicitly deferred with a reason
- [ ] Types shared, no `any` at the API boundary
- [ ] Tests: unit on logic, integration on endpoints, one E2E per primary flow
- [ ] Lighthouse ≥ 90 on the chunk's heaviest screen; keyboard-navigable; WCAG 2.2 AA on colour and focus
- [ ] All four critics clear of BLOCKERs, and every MAJOR either fixed or consciously accepted by Boss

---

## 6. What Boss sees, and when

I do **not** surface every agent result. Boss gets:

- **Before each chunk starts:** the one-page chunk spec — scope, endpoints, screens — to approve or redirect
- **After each chunk's gate:** a one-screen report — what was built, what the critics found, what I verified and fixed, what is left open and why
- **Immediately, out of band:** anything that blocks (a stack decision, a client business question, a contradiction between Figma and console that I cannot resolve alone)

Everything else — agent chatter, intermediate failures, retries — stays with me.

---

## 7. Risks I already know about

| Risk | Mitigation |
|---|---|
| The Figma file still has open gaps (`FINDINGS.md`: A7 overlays, A8 responsive nav, B7 fluid layout, C4 gradients) | C0/C1 do not start until the Figma work in flight lands. Anything still open at that point is written into the chunk spec as "build from the console, not the design" |
| Figma is a static picture; interaction detail lives in the HTML | Every chunk spec names the console functions that define the behaviour, so the builder reads them rather than guessing |
| Section-H defects get copied because they are in both sources | The domain critic exists specifically to catch this, and each chunk spec lists the section-H items in its area |
| Chunks drift apart when built in parallel | The shared Zod contract is written before either side starts, and C0/C1 land first so everything instantiates the same shell |
| Open client questions (OC-1…OC-11) block real decisions | Build behind a feature flag with the console's current behaviour as the default; never invent a resolution |

---

## 8. Open decisions — Boss, I need these before I start

1. **Stack** — confirm the proposal in §2, or tell me the company standard so I swap the builders.
2. **Repository** — new repo, or a folder inside an existing one? Monorepo (frontend + backend together, shared types) or two repos?
3. **Auth** — is there an existing identity provider to integrate with, or do we build session auth ourselves for now?
4. **Database** — is there an existing schema/DB this must fit into, or is it greenfield?
5. **Scope of "complete"** — all 10 chunks, or do you want C0–C4 first (the spine plus the core dispatch flow) as a demonstrable milestone?
6. **Deploy target** — Vercel + a managed Postgres, or the company's own infrastructure?

I can start C0 the moment §2 and question 2 are answered; the rest can be answered as we go.
