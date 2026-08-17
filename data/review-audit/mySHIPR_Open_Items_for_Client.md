# mySHIPR Carrier Console — what is still open after the v4 rebuild

Prepared 5 August 2026. Everything below is outside the console itself: it needs either a
business decision or an edit to a BRD. The console has been updated for every item that
could be fixed in the UI.

---

## A. Business decisions we need answered

These block work. Nothing in the console can settle them.

| # | Question | Why it blocks | Where it surfaces today |
|---|---|---|---|
| **OC-1** | Is **CO-22 a driver→truck assignment or a truck roster?** | The two readings produce opposite implementations of the core operating model. "Min 4 drivers per truck" reads as a roster; the title, goal and table name say assignment. | Assignment wizard, driver step — both paths are offered, flagged |
| **OPS-5** | **Who selects the truck for a load?** Shipment Execution names the Dispatcher; the Auth Services BRD V3 matrix gives the Dispatcher no `fleet.truck.view`. | The Dispatcher cannot legally see the list they are told to choose from. | Assignment wizard, truck step — warning banner |
| **OC-2** | **Who onboards drivers?** CO-17 / CO-18 / CO-22 say Fleet Manager; RBAC row 8 gives Fleet Manager view-only and grants create to the Dispatcher. | Build against the wrong role and one of the two cannot do their documented job. | Console follows the RBAC matrix |
| **OC-3** | If the driver who logs into a truck has **insufficient remaining HOS**, what happens — block the login, warn, alert dispatch, or nothing? | No document addresses it. | HOS Status — the console warns and does not block |
| **OC-4** | Are **Shipments and Trips one lifecycle or two?** TRIP-01 defines a Trip as "truck + driver + shipment", but the driver is unknowable at trip creation under the truck-login model. | The Trip entity as defined cannot be created. | Trips — console treats the trip as a view over the load |
| **OC-5** | Should the CO-18 **driver-insurance flag become a full policy record** (policy number, insurer, coverage, expiry)? | Today it is only Yes/No. | Driver profile |
| **OC-7** | Why do **Costco scenarios omit per-stop contact points** when FTL, LTL and Dump Truck all carry them? | A driver arriving at a Costco stop has no site contact. | Load detail — shown as "No site contact supplied for this stop" |
| **OC-8** | What is the **source of six fields the console displays that no CO- step captures**: fuel type, odometer, yard subtype, geofence radius, CDL endorsements, GVWR? | CDL endorsements is the pressing one — DRV-07's TSA rule cannot fire on data that is never collected. | Truck and yard records — labelled "not captured at CO-…" |
| **OC-11** *(new)* | **Driver Operations is Carrier-Super-Admin-only in the RBAC matrix**, yet DET-005, SOS-003, MEC-002 and DSP-001…006 all address *dispatch*. Add a Dispatcher column, or reword the Driver BRD? | The Dispatcher cannot see detention, exceptions or driver messages. | Driver Ops — Dispatcher gets a 403 |
| **New** | **Weight per pallet: 30–40 lbs (Master Data) or 2,000 lbs (Shipment Execution BRD)?** The Shipment Execution BRD cites Master Data as its source and then contradicts it. | Pallet-to-weight validation cannot be built. | Capacity & Service Profile — flagged red |
| **New** | The **maintenance-type catalogue** (OIL_CHANGE … TABLET_BREAKDOWN) has no business-document source; it comes from the database dictionary. | Needs promoting into Master Data or dropping. | Maintenance & DVIR |

**Closed by the rebuild, no longer open:** OC-6 (Costco is LTL), OC-9 (CO-09 five-tier ladder
adopted), OC-10 ("Flat Truckload" removed — Bobtail is a Master Data truck type).

---

## B. Document edits still outstanding

The console is clean on all of these. The BRDs are not.

1. **CD-5 — the old driver-assignment model still appears in 22 documented locations**, including a database table (`truck_driver_assignments`), an audit event (`ASSIGNMENT_CHANGE`), a shipment state (Driver Assigned), three lifecycle events (TRIP_ASSIGNED / ACCEPTED / REJECTED), three notification contracts (CR-020, DR-001, DR-008) and a status-update payload (`driverId`). Spread across the Carrier View BRD, Master Data, Fields For HOS, Notification Types, the FTL Master Reference, Appendix E and the Driver BRD. Delete or rewrite each — this is cheap now and expensive once code exists.
2. **Carrier View BRD §2 and §17** — rename "Dispatch Admin" to "Dispatcher" and add Fleet Manager and Compliance Manager, which the document has never contained.
3. **Publish a glossary** and align every document to the Auth Services BRD V3 vocabulary (11 naming conflicts: Bob tails / Bobtail, PRIVATE / Owned, CAR_CARRIER / Car Hauler, IN_SERVICE / Serviceable, CONTRACT / Contractual, Trip / Shipment / Load / Manifest, and so on).
4. **Close four open items the pack already answers itself:** OPEN-01 → CO-21 driver ratings; OPEN-02 → CO-18 insurance flag; OPEN-03 → SHP-RF and SHP-RCR prefixes; GAP-10 → per-stop contacts are already standard in the Shipment Execution Super Set.
5. **AP-001** — change the actor from "Carrier" to "Carrier Super Admin" for precision.
6. **Align DOC-009 / DOC-010 / DOC-016 / DOC-018** to CO-09's five-tier ladder, which is the only schedule covering post-expiry escalation.
7. **Add CDL endorsements to CO-17.** DRV-07 builds a TSA rule on endorsements and the console renders a TSA flag from them, but no onboarding step collects them.
8. **Reconcile CO-13's secondary trailer** with the Shipment Execution flow — the console now attaches primary at assignment and secondary on the asset record; the documents should say which is authoritative.

---

## C. What changed in the console (for reference)

Fixed in this pass: broken "Register truck" action · hardcoded vehicle-document dates ·
undocumented HOS colour bands · missing loading / 401 / 503 / 400 states · dismissible SOS ·
reviewer commentary printed inside the product · missing detention, breakdown, exception,
safety and messaging surfaces · missing route/RPM/fuel/deadhead/payment analytics and CSV
export · non-configurable timezone · missing CO-13 secondary trailer · static map ·
unvalidated AWB check digit · create forms that were buttons without forms.
