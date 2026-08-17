# D6 — Cross-Flow Map, Information Architecture & Prototype Wiring

**Note on method.** `design/` is empty at time of writing — D2-D5 run in parallel and have not
landed files yet. Section 5's "owning file" column is therefore the *structural* assignment per
`design-spine.md` §2's page tree (persona → page), not a confirmed read of a committed D2-D5 file.
Section 6 flags this explicitly rather than silently presenting it as verified.

## 1. The shared lifecycle — one baton, four hands, and a fifth with no hands at all

| Load state(s) | Who acts | What they see | Who is merely notified |
|---|---|---|---|
| `DRAFT`→`PUBLISHED` | Shpr (`SHIPPER_LOAD_POSTER`) | `[SCR-901]` multi-step form, autosaved draft | — (`EVT-1000`, T3, Shpr IA only) |
| `AUCTION_OPEN`→`EXTENDED`→`CLOSED` | Shpr watches; eligible Disp bid | `[SCR-902]` live bids (Shpr) / `[SCR-911]` bid loop (Disp) | Ineligible carriers: nothing — `PERM-230` denies to not-found |
| `AUCTION_FAILED_*` | Shpr | `[SCR-902]` failed, named reason | Disp: `EVT-1004` DG only |
| `AWARD_PENDING`→`AWARDED` | System re-verifies; Disp accepts/declines (`PERM-217`) | Shpr: `[SCR-903]` "verifying" (`EC-902`) → outcome. Disp: no dedicated screen — see §6 | Ops: `EVT-1005` DG |
| `AWARD_ACCEPTED` | Disp (`+ACCEPT_AWARD`) | Fleet binding at `[SCR-912]` | Shpr `EVT-1010` IA,EM |
| `AWARD_DECLINED`/`LAPSED`/`VOIDED_INELIGIBLE` | Nobody — this is where the baton drops | Shpr `[SCR-903]` sees decline/lapse | Ops `EVT-1008`/`1009` — **no queue owns it, §6** |
| `PICKUP_SCHEDULED`→`AT_PICKUP` | Drv | `[SCR-922]` arrival/departure | Shpr `[SCR-904]`, Disp `[SCR-913]` |
| `CARRIER_NO_SHOW`/`SHIPPER_NOT_READY`/`PICKUP_REFUSED` | Ops if unresolved | No dedicated SCR-, folds into exception banners | Both sides `EVT-1014/1015/1016` |
| `PICKED_UP`→`IN_TRANSIT` | Drv | `[SCR-920]` one primary action | Shpr `[SCR-904]`, Disp `[SCR-913]` |
| `TRANSIT_EXCEPTION` | Drv or Disp reports; Ops resolves | `[SCR-925]`/`[SCR-914]` → `[SCR-930]`/`[SCR-931]` | Shpr `EVT-1021` IA,EM |
| `AT_DROP`→`DELIVERED`/`DELIVERY_ATTEMPTED_NO_RECEIVER` | Drv captures; **consignee signs on the driver's device** | `[SCR-924]` forced choice | Cnsg: OOB link only, never in-app |
| `PARTIAL_DELIVERY` | Drv | No line-level UI named — §6 | — |
| `DELIVERY_REFUSED`→`RETURN_TO_ORIGIN` | Drv/Ops | RTO has no SCR- at all — §6 | Shpr `EVT-1026` T0 |
| `POD_CAPTURED`→`INVOICE_ISSUED`→`SETTLED` | Shpr approves/disputes; Disp views | `[SCR-906]`, `[SCR-916]` | Ops `EVT-1041` line-held → **DG only**, not real-time |
| `ExceptionCase` any type, `OPEN`→`RESOLVED` | Ops (`PLATFORM_EXCEPTION_DESK`) | `[SCR-930]`→`[SCR-931]` | Shpr/Disp per §12.1's matrix |

## 2. The six handoffs, spine §4 format

| # | Handoff | Frame(s) | User sees / does | System does (EVT) | Goes to | If it fails |
|---|---|---|---|---|---|---|
| H1 | Shipper publishes → carrier becomes eligible | `[SCR-901] Default` → `[SCR-910] Default` | Disp: load appears in Load Board, filtered by `eligibility()` | `EVT-1000 load.published` (T3, Shpr IA only) → gate evaluated (`BR-200-217`) → `EVT-1001 auction.opened` (Disp **DG unless subscribed**) | `[SCR-902]`/`[SCR-911] Live` | **No named nudge to an eligible-but-inactive carrier** — the pool can be silently thin (`EC-908`) with zero active notification driving anyone to look |
| H2 | Carrier wins → dispatcher assigns driver | outcome state (no confirmed SCR-, §6) → `[SCR-912] Default/Contested` | Disp accepts/declines award, then binds tractor+trailer+driver | `EVT-1005`→`EVT-1006 award.confirmed` (**T0**, voice-escalates if unacked) → `EVT-1010 award.accepted` | `[SCR-913] Active Loads` | `ERR-517 AWARD_ACCEPTANCE_WINDOW_EXPIRED` → `EVT-1008 award.lapsed` — **the single most expensive failure named in F10 (§12.5), and it lands nowhere resolvable, §6** |
| H3 | Driver arrives → shipper's tracking updates | `[SCR-922] Default` → `[SCR-904]`/`[SCR-913] Stale/Default` | Shpr/Disp see custody-event feed, not a discrete "arrived" push | Position/status is a continuous feed (F8 §6), not itself an `EVT`; only `EVT-1020 shipment.status_overdue` (T1) is a true event | `[SCR-904] Default` or `Stale` | Missed interval → `[SCR-904]` shows **stale, never hidden** (`BR-401`); `[SCR-933]` catches it ops-side. Best-resolved handoff in the map |
| H4 | Driver captures POD → consignee acts | `[SCR-924]` forced choice (signature on driver's device) | Consignee signs in person; separately holds a tokenised OOB link for read + exception-note | `EVT-1028 pod.captured` → Cnsg `OOB⁶` bundles `BR-714` notice | Consignee's own read-only view — **no SCR- ID exists for it, §3/§6** | `EVT-1047 consignee.notice_delivery_unknown` — platform never fabricates a confirmed-read; `EC-1000` bounce → shipper re-prompted, SLA `[NEEDS INPUT]` |
| H5 | POD captured → invoice raised | `[SCR-924] Confirmation` → `[SCR-906]`/`[SCR-916]` | Shpr reviews lines, disputes one without blocking others | `POD_CAPTURED`→`INVOICE_ISSUED` fires `EVT-1040` (T2) | `[SCR-906] Partial (mixed held/clear)` | `ERR-536 INVOICE_ALREADY_ISSUED` (dup guard); `EVT-1041 invoice.line_held` reaches Ops only as `DG` — a held dollar sits until digest even though money is stuck |
| H6 | Anything breaks → ops picks it up | any exception origin → `[SCR-930] Default` | Ranked queue, action pre-attached, not a re-triage | `ExceptionCase.opened` for the 5 named `case_type`s only | `[SCR-931]` | `EC-904` second claimant blocked cleanly. **But `AWARD_LAPSED`/`VOIDED_INELIGIBLE` never open an `ExceptionCase` (§3.3's list excludes them) — Ops is paged (`EVT-1008/1009`) with nowhere to work it. This is the sharpest silent-break in the whole map.** |

## 3. The consignee problem

The consignee (`ROLE-240 CONSIGNEE_TOKEN`, `PERM-231/232/263`) has **no `SCR-` ID anywhere in F9's
31-screen inventory.** Their surface is defined only at the API/entity layer:

1. **Physical signature** — captured *on the driver's phone* (`[SCR-924]`), not their own device.
   Identity is captured as-stated, never verified (`BR-510/511`) — "requiring verified authority
   would stop deliveries completing in the real world" (BRD §8.5).
2. **Tokenised read link** (`API-112 GET /v1/consignee-links/{token}`) — corridor/ETA band only, no
   coordinates, no history (`PERM-263`); multi-use within expiry (`FR-131`).
3. **Tokenised action link** (`API-113 POST .../submit`) — exception note / concealed-damage
   addendum (`BR-504`); single-use, replay rejected showing the first consumption (`FR-130`).
4. **No claim channel of their own** — relayed through the shipper always (`BR-906`, `EC-1006`).

**Failure modes, mapped to what the spec actually says:**

| Failure | What happens | Cite |
|---|---|---|
| Forwarded to the wrong person | Token is scoped to `assigned_load`, not a named human — anyone holding the link can act as consignee for that load | `ROLE-240`, `BR-510` — an accepted risk trade-off, not a bug |
| Opened after expiry | Safe error + relay path back through shipper/carrier contact | `FR-133`; generically `ERR-530 NOT_AUTHENTICATED` (401) — **no consignee-specific error code exists** |
| Used twice (state-changing) | Rejected, first-consumption event shown, never silently reprocessed | `FR-130`; entity-layer guard `ERR-535 POD_ALREADY_CAPTURED` |
| Opened by the wrong person at the dock | Not blocked by design — captured as-stated, weighed later at claim time | `BR-510`, BRD §8.5's own admission |
| Consignee is also a registered user elsewhere | Identities intentionally not linked; token flow proceeds regardless | `EC-114` |

**Design consequence:** a `[SCR-950] Consignee Delivery Link — Default/Expired/Used/Wrong-load`
frame set is needed and does not currently exist. Marked **[NEW — not in F9]**, justified by
`PERM-231/263`, `BR-906/912`, `FR-129-133`, `API-112/113`.

## 4. Navigation and IA

- **App shell / persona switcher** — `prototype.html` implements four buttons: Shipper, Carrier,
  Ops, Driver. **Admin/Fraud (`SCR-940`-`943`) has no persona-switch entry at all** — zero of its
  four screens are reachable from the built shell.
- **Left nav** — scoped per persona via `[data-p~="persona"]`; exception-forward IA (§7.3 of F9)
  carried structurally, not just as a labelling convention.
- **Cmd+K** — cross-persona: nav jump, persona switch, theme toggle, available to every desk
  persona, not dispatcher-exclusive in the build. It is *named* the dispatcher's primary nav because
  a dispatcher juggling multiple trucks/auctions (`[SCR-913]`) benefits most from search-jump over
  a nested tree — worth confirming that emphasis with D3, not assuming it from the code alone.
- **Deep links** — the consignee's OOB link is the one true "no-login deep link into a specific
  state" pattern in the product (`API-442/448`); everything else deep-links inside an authenticated
  session.
- **Permission-denied vs not-found** — `ERR-531 RESOURCE_NOT_FOUND` (404) is used whenever an actor
  *knowing a resource exists* is itself sensitive; `ERR-532 ACCESS_DENIED` (403) only when the actor
  is already a visible party lacking that specific action (`§7.4`). **Design consequence:** the
  `Permission denied` state (mandatory per spine §3 on every frame) must render **visually identical
  to `Empty`/404** on enumeration-sensitive screens (`[SCR-910]` opening a non-eligible load,
  `[SCR-902]` on another shipper's auction) — and only diverge into a distinct "access denied" look
  where the relationship is already known (e.g. `CARRIER_ACCOUNTING` blocked from bidding on its
  own org's load, `PERM-216`).

## 5. Consolidated frame index (31 `SCR-`, F9 canonical)

| SCR | Screen | Persona | Owning page/file | Built in prototype? |
|---|---|---|---|---|
| 900 | Load Dashboard | Shipper | 10 / D2 | **Yes** |
| 901 | Post a Load | Shipper | 10 / D2 | **Yes** |
| 902 | Auction Watch | Shipper | 10 / D2 | **Yes** |
| 903 | Award & Accept-Flow Monitor | Shipper | 10 / D2 | No |
| 904 | Shipment Tracker | Shipper | 10 / D2 | **Yes** (`shipment-detail`) |
| 905 | Exception Inbox | Shipper | 10 / D2 | No |
| 906 | Invoice Approval | Shipper | 10 / D2 | No |
| 907 | Claim Intake | Shipper | 10 / D2 | No |
| 908 | Standing & Cancellation History | Shipper | 10 / D2 | No — depends on orphan `BR-106` feed (`EC-907`) |
| 910 | Load Board | Carrier | 11 / D3 | **Yes** |
| 911 | Bid & Comparison | Carrier | 11 / D3 | No — build-blocked, `DEC-302/303` |
| 912 | Fleet Assignment | Carrier | 11 / D3 | No |
| 913 | Active Loads | Carrier | 11 / D3 | No |
| 914 | Breakdown/Exception Report | Carrier | 11 / D3 | No |
| 915 | Driver & Equipment Roster | Carrier | 11 / D3 | No |
| 916 | Settlement Status | Carrier | 11 / D3 | No |
| 920 | Today (home) | Driver | 12 / D4 | **Yes** |
| 921 | Navigation Handoff | Driver | 12 / D4 | No — one-tap stub, thinnest spec in F9 |
| 922 | Arrival/Departure Capture | Driver | 12 / D4 | No |
| 923 | Document Capture | Driver | 12 / D4 | No |
| 924 | POD Capture | Driver | 12 / D4 | **Yes** |
| 925 | Report a Problem | Driver | 12 / D4 | No |
| 926 | Language & Support | Driver | 12 / D4 | No — thin spec |
| 930 | Exception Work Queue | Ops | 13 / D5 | **Yes** |
| 931 | Exception Detail & Resolution | Ops | 13 / D5 | No |
| 932 | Claims Desk | Ops | 13 / D5 | No |
| 933 | Silence/No-Response Monitor | Ops | 13 / D5 | No |
| 940 | Carrier Vetting Queue | Admin/Fraud | 14 / D5? | No — **no persona-switch entry point at all, §4** |
| 941 | Fraud Case Review | Admin/Fraud | 14 / D5? | No |
| 942 | Selection Record/Audit Viewer | Admin/Fraud | 14 / D5? | No |
| 943 | Enforcement Action | Admin/Fraud | 14 / D5? | No |

8/31 built (900, 901, 902, 904, 910, 920, 924, 930), matching spine's stated count. `14/D5?` is
flagged because only four D-slots (D2-D5) cover five flow pages (10-14) — confirm with D5 whether it
owns both Ops and Admin/Fraud, or whether Admin/Fraud is genuinely unowned.

## 6. Coverage audit

**Screens with real ownership/substance gaps** (not literally unclaimed — persona↔page mapping is
clean — but under-specified or structurally homeless):

1. **Consignee's own tokenised surface — zero `SCR-` ID.** The largest gap in the whole inventory
   (§3). **[NEW]** `SCR-950` recommended.
2. **Carrier's award accept/decline action has no named screen.** `PERM-217` exists; `[SCR-911]`'s
   "outcome" state is the closest candidate but F9 never says the accept/decline control lives
   there — confirm with D3.
3. **`AWARD_LAPSED`/`AWARD_VOIDED_INELIGIBLE` have no ops resolution screen** — not an
   `ExceptionCase` type per §3.3, so `[SCR-930]`'s queue never ingests them (H2/H6, §2). Named by
   F10 itself as the costliest failure mode in the system.
4. **No `Cancel Load` frame.** `PERM-203/204` define who may cancel and when; no `SCR-` renders the
   action or its confirmation state.
5. **`SCR-908`** is specified but structurally unfulfillable until `BR-106`'s upstream feed exists
   (`EC-907`, already flagged at the FRD layer).
6. **Admin/Fraud page (940-943) has no entry point in the built shell** — a persona-switch gap, not
   a screen-spec gap.

**Lifecycle states in FRD §3.3 with no screen rendering them as a named, distinct state:**

- `CANCELLED_BY_SHIPPER` — action permitted, no confirmation frame
- `CARRIER_NO_SHOW`, `SHIPPER_NOT_READY`, `PICKUP_REFUSED` — each has a T0/T1 `EVT-` but no `SCR-`
  renders it as its own state (folds into generic banners)
- `PARTIAL_DELIVERY` — `BR-507` requires line-level split-POD capture; `[SCR-924]`'s spec describes
  only the binary clear/exception forced choice, never a split-line UI
- `RETURN_TO_ORIGIN` — exists as a `Custody Event` type (`ENT-315`); no `SCR-` shows RTO progress to
  any persona
- `ExceptionCase.RESOLVED` for `CARGO_INTEGRITY`/`FRAUD_REVIEW`/`CARRIER_ENFORCEMENT_COLLISION` —
  `EVT-1049` is new at the assembly layer; `[SCR-931]`'s generic "Resolve" action is the presumed
  trigger but this was never confirmed against F9's original text

## 7. Build-blocking cross-cutting decisions

1. **Rival-bid visibility (`DEC-302`/`303`, §16.1).** Three agents converged independently: F6 found
   "sealed + standing-best-flag" is a false middle ground; F2 proved it **leaks by construction**
   (repeated decrements binary-search the price); F9 shipped `[SCR-911]` on the conservative `none`
   default specifically to avoid a BR-717 violation in production. **Consequence:** `[SCR-911]` is
   feature-complete as a swappable component but cannot ship past `none` until locked.
2. **May the shipper decline the lowest qualified bidder (`DEC-307`, same question as `BR-155` and
   `EC-325` — asked three times).** **Consequence:** if `NONE`, `[SCR-903]` is a pure accept/monitor
   screen; if `STRUCTURED_REASON_REQUIRED`, it needs a decline sub-flow with a mandatory reason
   field feeding the selection record (`ENT-312`) — materially different screen, not a variant.
3. **HOS: planning signal vs. system of record (`DEC-700`).** Option A = no hours UI anywhere;
   Option B = bounded FEASIBLE/INFEASIBLE flag only (`[SCR-920]`'s `EC-912` "not evaluated" fallback
   already assumes B, not C); Option C = full RODS dashboard, which **reverses an already-locked
   data-minimisation constraint** (§14/F12). `[SCR-920]` and `[SCR-915]` cannot finalize until this
   locks.

**CHALLENGE:** F9's `[SCR-911]` "outcome (won/lost/cascaded-in)" state is documented as read-only
narrative, but `PERM-217`'s accept/decline action has to live *somewhere* on the carrier side and no
F9 screen claims it outright. Recommend D3 either extends `[SCR-911]`'s outcome state with an
explicit accept/decline control or specifies a `[NEW]` screen — silently assuming one risks the same
class of miss that produced gap #3 in §6.
