# Design-structure spine — conventions for the Figma-style application map

**Authored by Jarvis before dispatching any agent.** Same discipline that produced zero ID collisions
across the BRD and FRD phases. Every agent reads this first and works inside it.

**Goal:** a complete, step-by-step map of the application, organised the way a real Figma file is —
pages → frames → components → prototype connections. Someone should be able to read it and know
exactly what screen exists, what is on it, what every state looks like, and what happens on every
action. It is the bridge between `FRD-v1.md` (what the system must do) and a built UI.

---

## 1. Source material — do not invent screens

- **`frd-F9-dashboards-screens.md`** — 31 screens already specified (`SCR-900`…`SCR-943`). **This is
  the authoritative screen inventory.** Use its IDs. If a flow needs a screen F9 did not specify, add
  it and mark it `[NEW — not in F9]` with a one-line justification.
- **`FRD-v1.md`** — §3 entity/state model (the lifecycle every flow moves through), §4 permission
  matrix (who can even see a screen), §7 error taxonomy (what the error states are), §12 events.
- **`prototype.html`** — 8 of these screens are already built and verified working. Where a frame
  exists in the prototype, say so, so the reader knows what is real versus specified.
- **`DECISIONS.md`** — two locked decisions. Do not contradict them.

## 2. Figma file structure — the canonical page tree

```
📄 00 · Cover
📄 01 · Foundations        colour, type, spacing, elevation, motion, iconography
📄 02 · Components         every component, every state, every variant
📄 03 · Patterns           table, form, timeline, queue, empty/error/loading
📄 10 · Flow — Shipper
📄 11 · Flow — Carrier / Dispatcher
📄 12 · Flow — Driver (mobile)
📄 13 · Flow — Platform Ops
📄 14 · Flow — Admin / Fraud review
📄 15 · Flow — Consignee (no account)   ← added after assembly; see note
📄 20 · Cross-flow map     how the four flows hand off to each other
📄 90 · Deprecated / parked
```

**Page 15 was missing from the first version of this tree, and that was a defect in this spine.**
The assembler caught it: D6 correctly identified that the consignee has no `SCR-` frame anywhere, but
the gap sat one layer above any single agent's scope — the tree listed five flow pages and none of
them belonged to the consignee, so no agent was ever asked to design for them. Every agent worked
inside one page, so none could see that a page was absent.

This matters more than a filing error. The consignee signs the document that closes the shipment and
triggers the invoice, and they never sign up for the platform. Designing four flows and omitting the
fifth participant is how the party with the most influence over the money ends up specified only as
an API contract. Page 15 owns their entire touchpoint surface — the tokenised, expiring,
single-purpose link and every way it fails.

## 3. Frame naming — exact format, no variation

```
[SCR-nnn] Persona · Screen name · State
```

Examples:
`[SCR-901] Shipper · Loads dashboard · Default`
`[SCR-901] Shipper · Loads dashboard · Empty`
`[SCR-924] Driver · POD capture · Choice (no selection)`

State suffix is mandatory. **Every frame is one state.** A screen with six states is six frames.

The eight core states, and every screen must declare which apply and which do not:
`Default` · `Loading (skeleton)` · `Empty` · `Partial data` · `Stale data` · `Permission denied` ·
`Error` · `Offline` — plus `Contested` (someone else is editing/claiming the same record) where
relevant.

## 4. How to write a step — mandatory format

Flows are numbered steps. Each step is a table row plus, where the step is non-obvious, a short note.

| Field | Meaning |
|---|---|
| **Step** | `S1`, `S2`… unique within the flow |
| **Frame** | the `[SCR-nnn] … · State` frame the user is looking at |
| **User sees** | the substance on screen — the two or three things that matter, not a component list |
| **User does** | the action available. One row per meaningful action, including *doing nothing*. |
| **System does** | what happens behind it — which entity changes, which state transitions, which event fires. Cite `FRD` IDs. |
| **Goes to** | the next frame, or the branch table below |
| **If it fails** | the error frame and the `ERR-` code |

**Every step must name its failure path.** A step with no failure row is incomplete — Boss's standing
instruction is that nothing may be missed.

## 5. Branches are first-class

Where a step forks, write a branch table — condition, destination frame, and consequence. Do not bury
a fork in prose. The forks that matter most in this product:

- eligibility pass / fail (and *why* it failed — that list is the legal record)
- bid accepted / outbid / rejected
- award accepted / declined / lapsed
- pickup succeeds / carrier no-show / shipper not ready / freight differs from declaration
- delivery clean / exception / refused / nobody there
- invoice clean / disputed / held pending a claim

## 6. Component specification format (page 02)

For each component: name · purpose · **every state** (rest, hover, focus-visible, active, disabled,
loading, error, selected, read-only) · variants · the tokens it consumes · accessibility notes
(role, keyboard behaviour, what a screen reader announces) · and where it is used.

A component spec that lists only the rest state is not a spec.

## 7. Hard rules

1. **Use F9's `SCR-` IDs.** New screens are marked `[NEW]` and justified.
2. **No invented numbers.** No pixel values, durations, or counts unless they come from the prototype
   or an FRD requirement. Tag `[NEEDS INPUT]`. This has held across two phases; hold it here.
3. **Design tokens are already decided** — do not invent a new palette. Dark mode is primary. Status
   colours are the IBM colour-blind-safe set (`#648fff` `#785ef0` `#dc267f` `#fe6100` `#ffb000`), with
   darkened equivalents in light mode because the literal hexes fail AA on white. **Status is always
   colour + icon + text, never colour alone.** System font stack, `tabular-nums` on numerics.
   WCAG 2.2 AA; focus ring ≥2px at 3:1.
4. **Permission-aware.** If a screen is invisible to a role, say so and cite the `PERM-` row. A flow
   that assumes everyone sees everything is wrong.
5. **Mark what is already built.** Eight frames exist in `prototype.html` and are verified working.
   Flag them so the reader can distinguish built from specified.
6. **Word budget 2,000-2,500, hard ceiling 2,500.** Dense tables, thin prose. Write to length once.
7. **`CHALLENGE:` rather than diverge.** Seven challenges were accepted in earlier phases; three
   corrected the manager's own design. It works.

## 8. Output

One file per agent: `design/D<N>-<slug>.md` under
`data/brd/freight-auction-marketplace/`.

The cover page, the consolidated frame index, and the cross-flow map are **assembler-owned**.
