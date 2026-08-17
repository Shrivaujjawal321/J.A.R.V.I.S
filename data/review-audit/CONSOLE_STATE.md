# CONSOLE (HTML) — GROUND TRUTH, all 42 sub-screens

Captured by driving the real console in a browser and reading the rendered DOM of every `go(section, sub)` route.
This is what the Figma file is supposed to represent. Source: `mySHIPR_Carrier_Console_v4 (2).html`.

### Dashboard › Overview   (dashboard, sub 0)
- title: Fleet Operations Overview
- description: Live snapshot of Apex Freight across the US / CA / MX network — assets, drivers, tenders, loads and compliance, all on one page.
- BANNER [crit] 1 required compliance document outstanding — CO-07 lists eight mandatory carrier documents. Profile completion is blocked at 88% until all are uploaded. | buttons: Go to documents
- panels (9):
  · «Fleet by asset status» — hint: interactive · Master Data — 7 values
  · «Drivers by dispatch eligibility» — hint: interactive · FMCSA gate OPS-05 / DRV-002
  · «Hours of Service — nearing limit» — hint: ELD feed · fleet-wide
      LIST: Sofia Torres — OFF_DUTY · 0.0 h remaining · San Jose Hu ; Priya Nair — DRIVING · 4.0 h remaining · CA-99 near E ; Marcus Reyes — DRIVING · 6.5 h remaining · I-580 near L ; Tyler Brooks — ON_DUTY_NOT_DRIVING · 7.1 h remaining ·  ; Rosa Martinez — ON_DUTY_NOT_DRIVING · 8.4 h remaining · 
      chips: OFF_DUTY, 30 min warning, DRIVING, OK, DRIVING, OK, ON_DUTY_NOT_DRIVING, OK, ON_DUTY_NOT_DRIVING, OK
  · «Outstanding payments» — hint: 4 need action
      LIST: PMT-CARR-US-00142-0001 · $2,38 — Load SHP-FTL-10003 · due 2026-07-30 ; PMT-CARR-US-00142-0002 · $1,18 — Load SHP-RCR-10005 · due 2026-07-29 ; PMT-CARR-US-00142-0003 · $640 — Load SHP-LTL-10002 · due 2026-07-25 ; PMT-CARR-US-00142-0005 · $860 — Load SHP-RCR-10002 · due 2026-08-02
      chips: Pending, Approved, Disputed, Pending
      buttons: Open Earnings
  · «Live map snapshot» — hint: GPS-001 feed · refresh 5–30 s
      BODY: San Jose Hub ⏐ Sacramento Depot ⏐ Tracy Staging ⏐ San Francisco ⏐ Salinas ⏐ Stockton ⏐ Fresno ⏐ Modesto ⏐ 001 · In Transit · 62% of TRIP-58021 ⏐ 002 · Available · parked ⏐ 003 · Available · 48% of TRIP-58022 ⏐ 004 · Out of Service · parked
  · «Onboarding & compliance completion» — hint: ONB-004…007
      BODY: 83% ⏐ 5 of 6 complete · ONB-005 ⏐ Company profile ⏐ 13 of 13 fields captured at CO-05 ⏐ FMCSA authority verified ⏐ Authority Active · insurance Active (CO-06) ⏐ Compliance documents ⏐ 7 of 8 uploaded — Cargo Insurance & General Liability outsta ⏐ Contract executed ⏐ Signed (mock) · CTR-APX-00142 ⏐ Financial setup (ACH payout) ⏐ Stripe onboarding completed — CO-29
  · «Active Alerts» — hint: 5 critical · 13 warning
      LIST: SOS alert from Driver Tyler Br — Emergency (911) status received with GPS ; ELD disconnected — TRK-CARR-US — HOS logs may be incomplete. Device TAB-4 ; Insurance certificate expires  — COI expires 2026-08-12. Escalation tier  ; Asset TRK-CARR-US-00142-004 is — DVIR defect reported 2026-07-19: hydraul ; Asset TRK-CARR-US-00142-008 is — Halt reported at San Jose Hub. Reason: i
      buttons: Call driver, Open Notification Centre
  · «Upcoming Tasks» — hint: 5 open
      LIST: Accept or decline tender — SHP — Reefer · Sacramento → San Jose · $2,480  ; Assign assets — SHP-FTL-10001 — Accepted 2026-07-23 · no truck, trailer  ; Confirm POD — SHP-FTL-10003 — Delivered San Jose → Tracy · selfie + 2  ; Upload Cargo Insurance & Gener — Last of eight CO-07 documents · blocks 1 ; Re-pair tablet TAB-4478 — TRK- — ELD disconnected since 2026-07-23 · HOS 
  · «Trips on going» — hint: Live tracking
      TABLE cols[7]: TRIP | LOAD | LANE | TRUCK | DRIVER | ETA | PROGRESS
      total rows in console: 3 (first 3 captured)
- LEGEND: Carrier Onboarding CO-01…CO-30 ; Master Data & Configurable Points V2 ; Auth Services BRD V3 ; Shipment Execution OPS-01…OPS-12 ; Notification Types ; Records: illustrative

### Fleet › All Vehicles   (fleet, sub 0)
- title: All Vehicles
- description: Every field captured at CO-10 and validated at CO-11 — licence plate, plate state, registration expiry, make and model. Rows open the full asset record.
- header actions: Register truck, Bulk upload
- panels (1):
  · «Fleet» — hint: 8 vehicles
      TABLE cols[9]: (blank) | TRUCK | TYPE | MAKE / MODEL | PLATE | REGISTRATION EXPIRY | ASSET STATUS | CO-11 | HOME YARD
      total rows in console: 6 (first 6 captured)
      chips: In Transit, Serviceable, Available, Serviceable, Available, Serviceable, Out of Service, Not serviceable, At Delivery/Dump, Serviceable, Available, Serviceable
      buttons: ‹, 1, 2, ›
- NOTE: Rows shaded red are not dispatchable — asset status is Out of Service or Halt, so allows_dispatch is false. The load assignment wizard filters these out automatically (OPS-03).
- LEGEND: CO-10 Truck Registration ; CO-11 DMV validation ; Master Data §1.2 truck types ; Master Data asset status ; Auth Services BRD V3 — FLEET

### Fleet › Active Vehicles   (fleet, sub 1)
- title: Active Vehicles
- description: Trucks currently moving or on site, by Master Data asset status.
- header actions: Register truck, Bulk upload
- panels (1):
  · «Fleet» — hint: 8 vehicles
      TABLE cols[9]: (blank) | TRUCK | TYPE | MAKE / MODEL | PLATE | REGISTRATION EXPIRY | ASSET STATUS | CO-11 | HOME YARD
      total rows in console: 2 (first 2 captured)
      chips: In Transit, Serviceable, At Delivery/Dump, Serviceable
- NOTE: Rows shaded red are not dispatchable — asset status is Out of Service or Halt, so allows_dispatch is false. The load assignment wizard filters these out automatically (OPS-03).
- LEGEND: CO-10 Truck Registration ; CO-11 DMV validation ; Master Data §1.2 truck types ; Master Data asset status ; Auth Services BRD V3 — FLEET

### Fleet › Idle Vehicles   (fleet, sub 2)
- title: Idle Vehicles
- description: Trucks with asset status Available and therefore dispatchable.
- header actions: Register truck, Bulk upload
- panels (1):
  · «Fleet» — hint: 8 vehicles
      TABLE cols[9]: (blank) | TRUCK | TYPE | MAKE / MODEL | PLATE | REGISTRATION EXPIRY | ASSET STATUS | CO-11 | HOME YARD
      total rows in console: 3 (first 3 captured)
      chips: Available, Serviceable, Available, Serviceable, Available, Serviceable
- NOTE: Rows shaded red are not dispatchable — asset status is Out of Service or Halt, so allows_dispatch is false. The load assignment wizard filters these out automatically (OPS-03).
- LEGEND: CO-10 Truck Registration ; CO-11 DMV validation ; Master Data §1.2 truck types ; Master Data asset status ; Auth Services BRD V3 — FLEET

### Fleet › Maintenance & DVIR   (fleet, sub 3)
- title: Maintenance & DVIR
- description: Maintenance events and driver vehicle inspection reports. Logging an event sets the asset status and therefore gates dispatch.
- header actions: Log maintenance
- panels (3):
  · «Assets requiring attention» — hint: 5 vehicles
      TABLE cols[7]: TRUCK | TYPE | ASSET STATUS | DEFECT / REASON | LAST DVIR | DETAIL | ACTION
      total rows in console: 5 (first 5 captured)
      chips: In Transit, No defect, Out of Service, Defect reported, At Delivery/Dump, No defect, Unavailable, No defect, Halt, No defect
      buttons: Log event, Log event, Log event, Log event, Log event
  · «Maintenance types» — hint: FLEET-003 catalogue
      BODY: OIL_CHANGE ⏐ DOT_ANNUAL_INSPECTION ⏐ TIRE_ROTATION ⏐ BRAKE_SERVICE ⏐ PM_SERVICE ⏐ REPAIR ⏐ REEFER_PM ⏐ TABLET_BREAKDOWN
      in-panel note: This catalogue currently has no business-document source — it originates from the database dictionary. It is retained pending prom
  · «Inspection reminders» — hint: DR-025 / DR-026 · TEL-011 / TEL-012
      LIST: Pre-trip inspection outstandin — Driver must complete DVIR before dispatc ; DVIR defect — TRK-CARR-US-0014 — Hydraulic leak reported 2026-07-19 · ass ; DOT annual inspection due — TR — Scheduled 2026-08-30 (CR-022)
- LEGEND: Carrier View FLEET-003 ; Notification Types CR-010, CR-022, TEL-011, TEL-012 ; Driver BRD DR-025 / DR-026 ; Fields For HOS inspection events ; Tablet Breakdown / Device Under Repair — engineering brief

### Fleet › Vehicle documents   (fleet, sub 4)
- title: Vehicle documents
- description: Vehicle-level documents and expiries, on the same CO-09 five-tier ladder as carrier documents — including truck registration expiry.
- panels (1):
  · «Documents by vehicle» — hint: 8 vehicles
      TABLE cols[7]: TRUCK | REGISTRATION EXPIRY | REGISTRATION (CO-11) | INSURANCE (CO-11) | DOT ANNUAL INSPECTION | CARGO INSURANCE | ACTION
      total rows in console: 8 (first 7 captured)
      chips: OK, Valid, Valid, Expiring, Valid, OK, Valid, Valid, Expiring, Valid, OK, Valid
      buttons: Upload, Upload, Upload, Upload, Upload, Upload
- LEGEND: CO-10 registration expiry ; CO-11 DMV validation ; CO-09 expiry ladder ; Carrier View FLEET-004

### Fleet › Vehicle Types   (fleet, sub 5)
- title: Vehicle Types
- description: The full Master Data §1.2 truck catalogue — ten types. Dump trucks, bobtails, yard trucks, tankers and car haulers are all registrable.
- BANNER [info] Dump truck, bobtail and yard truck are now registrable — Bobtail is a truck type in Master Data, so the count is read from the catalogue rather than derived from a tru | buttons: 
- panels (1):
  · «Trailers» — hint: 7 units
      TABLE cols[9]: TRAILER | TYPE | VIN | MAKE / YEAR | LENGTH | MAX PAYLOAD | STATUS | ATTACHED TO | PHOTO
      total rows in console: 7 (first 7 captured)
      chips: In Transit, Available, Available, Available, Out of Service, Available, Unavailable
- NOTE: Maximum payload is a legal-weight field captured at CO-12 and drives the capacity filter in the assignment wizard (OPS-04).
- LEGEND: Master Data §1.1 trailer types ; Master Data §1.2 truck types ; CO-12 Trailer onboarding ; CO-13 Assign trailer to truck

### Fleet › Devices & ELD   (fleet, sub 6)
- title: Devices & ELD
- description: Tablet-to-truck pairing and ELD sync health. The tablet belongs to the truck, so this pairing is the foundation of the driver-identification model.
- header actions: Add device
- BANNER [crit] TAB-4478 disconnected — HOS logging inactive on TRK-CARR-US-00142-008 — Last sync 2026-07-23 06:02. HOS logs may be incomplete (TEL-002). CO-23 requires the Fleet Manager to be alert | buttons: Re-pair
- panels (1):
  · «Devices» — hint: 7 registered
      TABLE cols[6]: DEVICE | PAIRED TRUCK | PROVIDER | STATUS | LAST SYNC | ACTION
      total rows in console: 7 (first 7 captured)
      chips: Active, Active, Active, Sync failing, Active, Disconnected, Unassigned
      buttons: Unassign, Report faulty, Unassign, Report faulty, Unassign, Report faulty
- NOTE: Reporting a device faulty unpairs it, moves its truck to Out of Service with reason "Tablet Breakdown / Device Under Repair", and blocks dispatch. Pairing a replacement device to that truck 
- LEGEND: CO-23 ELD integration ; CO-24 Tablet device assignment ; Notification Types TEL-001 / TEL-002 ; Tablet Breakdown / Device Under Repair — engineering brief

### Fleet › HOS Status   (fleet, sub 7)
- title: HOS Status
- description: Hours of service per truck, sourced from the ELD sync. Warning thresholds follow TEL-003 (30 minutes remaining) and TEL-004 (violation past the limit) against the 11-hour driving maximum — no other threshold is applied.
- panels (1):
  · «HOS by vehicle» — hint: 6 paired vehicles
      TABLE cols[6]: TRUCK | DRIVER LOGGED IN | DUTY STATUS | REMAINING | LOCATION | WARNING
      total rows in console: 6 (first 6 captured)
      chips: DRIVING, OK, OK, DRIVING, OK, OK, ON_DUTY_NOT_DRIVING, OK, OK
- NOTE: Open question (OC-3): no document defines what should happen if the driver who logs in has insufficient remaining hours — block the login, warn, alert dispatch, or nothing. The console warns
- LEGEND: Fields For HOS — HOS Duty Status ; Driver BRD §4.2 ELD-001…006 ; Notification Types TEL-003 / TEL-004 / CR-021

### Drivers › All Drivers   (drivers, sub 0)
- title: All Drivers
- description: Click any driver for their full profile — status, documents, HOS, ratings, earnings, licence and insurance all in one place.
- header actions: Add driver, Bulk upload
- panels (1):
  · «Driver roster» — hint: 8 drivers
      TABLE cols[8]: DRIVER | CONTACT | CDL | TYPE | STATUS | HOS | LOCATION | DISPATCH ELIGIBILITY
      total rows in console: 8 (first 7 captured)
      chips: In Transit, Dispatchable, In Transit, Dispatchable, On Duty, Dispatchable, Available, Dispatchable, Off Duty, Blocked, Available, Dispatchable
- NOTE: The eligibility column applies the FMCSA gate documented in DRV-002, CO-20, DOC-017 and DOC-019 and enforced at assignment by OPS-05. Blocked drivers cannot be selected in the assignment wiz
- LEGEND: CO-17 / CO-18 driver onboarding ; CO-19 identity verification ; CO-20 drug & alcohol ; Master Data driver status (19 values) ; Shipment Execution OPS-05

### Drivers › On Duty   (drivers, sub 1)
- title: On Duty
- description: Drivers currently on duty, by Master Data driver status.
- header actions: Add driver, Bulk upload
- panels (1):
  · «Driver roster» — hint: 8 drivers
      TABLE cols[8]: DRIVER | CONTACT | CDL | TYPE | STATUS | HOS | LOCATION | DISPATCH ELIGIBILITY
      total rows in console: 4 (first 4 captured)
      chips: In Transit, Dispatchable, In Transit, Dispatchable, On Duty, Dispatchable, On Duty, Dispatchable
- NOTE: The eligibility column applies the FMCSA gate documented in DRV-002, CO-20, DOC-017 and DOC-019 and enforced at assignment by OPS-05. Blocked drivers cannot be selected in the assignment wiz
- LEGEND: CO-17 / CO-18 driver onboarding ; CO-19 identity verification ; CO-20 drug & alcohol ; Master Data driver status (19 values) ; Shipment Execution OPS-05

### Drivers › Off Duty   (drivers, sub 2)
- title: Off Duty
- description: Drivers off duty or offline.
- header actions: Add driver, Bulk upload
- panels (1):
  · «Driver roster» — hint: 8 drivers
      TABLE cols[8]: DRIVER | CONTACT | CDL | TYPE | STATUS | HOS | LOCATION | DISPATCH ELIGIBILITY
      total rows in console: 2 (first 2 captured)
      chips: Off Duty, Blocked, Offline, Blocked
- NOTE: The eligibility column applies the FMCSA gate documented in DRV-002, CO-20, DOC-017 and DOC-019 and enforced at assignment by OPS-05. Blocked drivers cannot be selected in the assignment wiz
- LEGEND: CO-17 / CO-18 driver onboarding ; CO-19 identity verification ; CO-20 drug & alcohol ; Master Data driver status (19 values) ; Shipment Execution OPS-05

### Loads › Tenders   (loads, sub 0)
- title: Tenders
- description: Loads awarded to Apex Freight and awaiting a reply. Accepting the tender links the rate confirmation and moves the load to Carrier Accepted (LED-02).
- BANNER [info] Accepting a tender is its own step — Master Data's lifecycle has "Carrier Accepted" as a distinct state, Ledger LED-02 makes it a carrier-dispatche | buttons: 
- panels (2):
  · «SHP-RF-10001 · FTL - Reefer» — hint: Tender expires 2026-07-24 18:00PDT
      KV: Commodity = Fresh Produce Refrigerated Goods ; Equipment required = 53′ Reefer ; Temperature = +2 °C · range 0 °C to +4 °C ; Pre-cooling = Required ; Pallets / weight = 22 pallets · 38,400 lbs ; Rate confirmation = Generated — signature required DOC-026
      chips: Required, Generated — signature required
      buttons: Accept tender & sign rate confirmation, Decline
  · «SHP-LTL-10004 · LTL - Multiple Goods» — hint: Tender expires 2026-07-25 09:00PDT
      KV: Commodity = Consumer Goods Retail Goods ; Equipment required = Dry Van ; Pallets / weight = 26 pallets · 41,200 lbs ; Rate confirmation = Generated — signature required DOC-026
      chips: Generated — signature required
      buttons: Accept tender & sign rate confirmation, Decline
- LEGEND: Ledger LED-02 ; Master Data — Shipment Status ; Notification Types CR-005, DOC-026, DOC-027 ; Shipment Execution OPS-02

### Loads › Awaiting Assignment   (loads, sub 1)
- title: Awaiting Assignment
- description: Accepted loads with no truck, trailer or driver selected. This is where the carrier does its core job: choosing the truck and trailer that will run the load.
- panels (1):
  · «Awaiting Assignment» — hint: 2 loads
      TABLE cols[10]: LOAD | LANE | EQUIPMENT | STATUS | TRUCK | TRAILER | DRIVER | PROGRESS | RATE | (blank)
      total rows in console: 2 (first 2 captured)
      chips: Carrier Accepted, Not selected, Not selected, Not selected, Carrier Accepted, Not selected, Not selected
      buttons: Assign assets, Assign assets
- NOTE: Selecting assets runs the OPS-03 / OPS-04 / OPS-05 eligibility filters: capacity against shipment weight, equipment type match, annual inspection and insurance validity, asset status, CDL an
- LEGEND: Shipment Execution OPS-01…OPS-12 ; Master Data — Shipment Status (16 states) ; Super Set — per-stop execution data ; Notification Types CR-007 / FTL-01 / DT-001

### Loads › In Execution   (loads, sub 2)
- title: In Execution
- description: Loads with assets committed and moving. Per-stop status, live position and recurring cycle counts.
- panels (1):
  · «In Execution» — hint: 3 loads
      TABLE cols[10]: LOAD | LANE | EQUIPMENT | STATUS | TRUCK | TRAILER | DRIVER | PROGRESS | RATE | (blank)
      total rows in console: 3 (first 3 captured)
      chips: In Transit, In Transit, At Delivery/Dump
- LEGEND: Shipment Execution OPS-01…OPS-12 ; Master Data — Shipment Status (16 states) ; Super Set — per-stop execution data ; Notification Types CR-007 / FTL-01 / DT-001

### Loads › POD & Close-out   (loads, sub 3)
- title: POD & Close-out
- description: Proof of delivery captured by the driver, reviewed here before the load is closed. POD gates close-out and opens the payment sequence (LED-05).
- panels (1):
  · «SHP-FTL-10003 · POD review» — hint: Captured 2026-07-23 16:42 PDT
      KV: GPS at submission = 37.7397, -121.4252 POD-007 auto-captured ; Signature = K. Alvarado ; Damage notes = None reported ; Photos = 1 selfie + 2 truck photos Count valid ; Receipts = 1 uploaded · AI-classified POD-008 / DT-26 ; Delivered = 2026-07-23 16:42PDT ; Driver = Rosa Martinez ; Truck / trailer = 002 · 012
      chips: Count valid
      buttons: Confirm POD & close out, Request resubmission
- LEGEND: Driver BRD POD-001…008, DT-25, DT-26 ; Auth Services BRD V3 — POD category ; Master Data POD event sequences ; Ledger LED-05 ; Carrier View SHP-006

### Loads › Completed   (loads, sub 4)
- title: Completed
- description: Delivered loads with POD captured and close-out complete.
- panels (1):
  · «Completed» — hint: 2 loads
      TABLE cols[10]: LOAD | LANE | EQUIPMENT | STATUS | TRUCK | TRAILER | DRIVER | PROGRESS | RATE | (blank)
      total rows in console: 2 (first 2 captured)
      chips: POD Captured, Completed
- LEGEND: Shipment Execution OPS-01…OPS-12 ; Master Data — Shipment Status (16 states) ; Super Set — per-stop execution data ; Notification Types CR-007 / FTL-01 / DT-001

### Loads › History   (loads, sub 5)
- title: History
- description: Archived loads.
- panels (1):
  · «History» — hint: 1 loads
      TABLE cols[10]: LOAD | LANE | EQUIPMENT | STATUS | TRUCK | TRAILER | DRIVER | PROGRESS | RATE | (blank)
      total rows in console: 1 (first 1 captured)
      chips: Completed
- LEGEND: Shipment Execution OPS-01…OPS-12 ; Master Data — Shipment Status (16 states) ; Super Set — per-stop execution data ; Notification Types CR-007 / FTL-01 / DT-001

### Trips › On going   (trips, sub 0)
- title: Trips — On going
- description: A trip is one truck movement against a load. Every trip links to its load, and both follow the single Master Data lifecycle. Live position for every on-going trip is also on the Dashboard Overview.
- panels (1):
  · «On going» — hint: 3 trips
      TABLE cols[7]: TRIP | LOAD | LANE | TRUCK | DRIVER | ETA | PROGRESS
      total rows in console: 3 (first 3 captured)
- NOTE: Open question (OC-4): Shipments, Trips and Loads are modelled as three entities across three documents. This build treats the trip as a view over the load and adopts Master Data's sixteen-st
- LEGEND: Master Data — Shipment Status ; Carrier View TRIP-01…03 ; FTL Master Reference status machine

### Trips › Scheduled   (trips, sub 1)
- title: Trips — Scheduled
- description: A trip is one truck movement against a load. Every trip links to its load, and both follow the single Master Data lifecycle.
- panels (1):
  · «Scheduled» — hint: 1 trips
      TABLE cols[7]: TRIP | LOAD | LANE | TRUCK | DRIVER | ETA | PROGRESS
      total rows in console: 1 (first 1 captured)
- NOTE: Open question (OC-4): Shipments, Trips and Loads are modelled as three entities across three documents. This build treats the trip as a view over the load and adopts Master Data's sixteen-st
- LEGEND: Master Data — Shipment Status ; Carrier View TRIP-01…03 ; FTL Master Reference status machine

### Trips › Upcoming   (trips, sub 2)
- title: Trips — Upcoming
- description: A trip is one truck movement against a load. Every trip links to its load, and both follow the single Master Data lifecycle.
- panels (1):
  · «Upcoming» — hint: 1 trips
      TABLE cols[7]: TRIP | LOAD | LANE | TRUCK | DRIVER | ETA | PROGRESS
      total rows in console: 1 (first 1 captured)
- NOTE: Open question (OC-4): Shipments, Trips and Loads are modelled as three entities across three documents. This build treats the trip as a view over the load and adopts Master Data's sixteen-st
- LEGEND: Master Data — Shipment Status ; Carrier View TRIP-01…03 ; FTL Master Reference status machine

### Trips › Completed   (trips, sub 3)
- title: Trips — Completed
- description: A trip is one truck movement against a load. Every trip links to its load, and both follow the single Master Data lifecycle.
- panels (1):
  · «Completed» — hint: 2 trips
      TABLE cols[7]: TRIP | LOAD | LANE | TRUCK | DRIVER | ETA | PROGRESS
      total rows in console: 2 (first 2 captured)
- NOTE: Open question (OC-4): Shipments, Trips and Loads are modelled as three entities across three documents. This build treats the trip as a view over the load and adopts Master Data's sixteen-st
- LEGEND: Master Data — Shipment Status ; Carrier View TRIP-01…03 ; FTL Master Reference status machine

### Trips › Cancelled   (trips, sub 4)
- title: Trips — Cancelled
- description: A trip is one truck movement against a load. Every trip links to its load, and both follow the single Master Data lifecycle.
- panels (1):
  · «Cancelled» — hint: 1 trips
      TABLE cols[7]: TRIP | LOAD | LANE | TRUCK | DRIVER | ETA | PROGRESS
      total rows in console: 1 (first 1 captured)
- NOTE: Open question (OC-4): Shipments, Trips and Loads are modelled as three entities across three documents. This build treats the trip as a view over the load and adopts Master Data's sixteen-st
- LEGEND: Master Data — Shipment Status ; Carrier View TRIP-01…03 ; FTL Master Reference status machine

### Driver Ops › Detention   (ops, sub 0)
- title: Detention
- description: Detention starts at geofence arrival (GPS-004) and runs against the free time agreed for that stop. Minutes past free time are billable and must be raised before the load closes out.
- header actions: Export
- BANNER [warn] 2 stops accruing detention right now — DET-003 notifies dispatch as free time expires. Detention is not recoverable once the load is closed out (LED- | buttons: 
- panels (1):
  · «Detention events» — hint: 4
      TABLE cols[10]: EVENT | STOP | DRIVER / TRUCK | ARRIVED | FREE TIME | ELAPSED | BILLABLE | AMOUNT | STATUS | ACTION
      total rows in console: 4 (first 4 captured)
      chips: Accruing, Accruing, Ack, Billable, Ack, None, Closed — within free time, Ack
      buttons: Acknowledge, Raise as billable, Raise as billable
- NOTE: Open question (OC-11): the Auth Services BRD V3 matrix gives Driver Operations to the Carrier Super Admin alone, yet every channel on these screens is addressed to dispatch — DET-005, SOS-00
- LEGEND: Driver BRD §4.14 DET-001…005 ; Driver BRD DT-15 ; GPS-003 / GPS-004 geofence arrival ; Ledger LED-05 ; Notification Types DET-003

### Driver Ops › Exceptions & Safety   (ops, sub 1)
- title: Exceptions & Safety
- description: Route deviation, excessive idle, distance mismatch, speeding, breakdown and reefer deviation. CO-25 generates a red flag; this is where it lands.
- BANNER [crit] 3 open exceptions — 2 critical — A critical exception holds the asset out of dispatch until it is cleared. Acknowledging records who saw it; cl | buttons: 
- panels (1):
  · «Exception log» — hint: 6 events
      TABLE cols[9]: EVENT | TYPE | DRIVER | ASSET | TRIP | DETAIL | DETECTED | STATUS | ACTION
      total rows in console: 6 (first 6 captured)
      chips: Open, Open, Acknowledged, Open, Cleared, Cleared
      buttons: Acknowledge, Clear, Acknowledge, Clear, Clear, Acknowledge
- NOTE: Every row here is a channel the Driver BRD specifies: CO-25 exception monitoring, GPS-005 distance, GPS-007 / DR-007 speed, MEC-001…005 breakdown, TRL-002 / ALT-003 reefer. Clearing an excep
- LEGEND: Carrier Onboarding CO-25 ; Driver BRD §4.11 TRL-002, §4.13 MEC-001…005 ; GPS-005 / GPS-007 ; Notification Types ALT-002 / ALT-003 / DR-007

### Driver Ops › Messages   (ops, sub 2)
- title: Messages
- description: Two-way dispatch messaging with every driver on a live trip. Text, voice notes, documents and location, with read receipts — DSP-001…006, under two seconds delivery.
- panels (3):
  · «Conversation — Marcus Reyes» — hint: +1 408 555 0231 · 001
      BODY: MR ⏐ Loaded and rolling out of San Jose. Seal 88231 applied. ⏐ Marcus Reyes · 09:41 PDT · read ⏐ Y ⏐ Copy. Consignee contact for Tracy is +1-1234567890, ask for  ⏐ You · 09:44 PDT · read ⏐ MR ⏐ Live location ⏐ 37.7016, -121.7680 · I-580 near Livermore, CA ⏐ Marcus Reyes · 10:58 PDT · read ⏐ MR ⏐ Voice note · 0:14
      buttons: Play, Open, Send, Voice note, Share document, Share location
  · «Threads» — hint: 2 drivers
      LIST: Marcus Reyes — Voice note ; Tyler Brooks — Shared a document
      chips: 2 new
  · «Delivery» — hint: DSP-006
      KV: Target delivery = < 2 seconds (DSP-006) ; Read receipts = On ; Retention = Message history is retained against the trip r
      chips: On
- NOTE: Open question (OC-11): the Auth Services BRD V3 matrix gives Driver Operations to the Carrier Super Admin alone, yet every channel on these screens is addressed to dispatch — DET-005, SOS-00
- LEGEND: Driver BRD §4.8 DSP-001…006 ; Driver BRD DT-08 ; Auth Services BRD V3 — DRVOPS

### RR › Coming soon   (rr, sub 0)
- title: RR — Rate & Auction Bidding
- description: Real-time load auctions, bidding and bid history for this carrier.
- panels (1):
  · «(untitled)»
      EMPTY STATE: Coming soon — Auction and bidding mechanics (lot visibility, live bidding, won / lost outcomes
      buttons: Go to Capacity & Service Profile
- LEGEND: 6A Carrier Eligibility & Auction Targeting ; Carrier View RR-01…RR-06

### Yards › All yards   (yards, sub 0)
- title: All Yards
- description: Yard address and geo-coordinates are captured at CO-14 — a yard without an address cannot be used for dispatch, and the coordinates drive geofencing, arrival detection and detention timing.
- header actions: Add yard
- panels (1):
  · «Yards» — hint: 3
      TABLE cols[9]: YARD | TYPE (CO-14) | SUBTYPE | ADDRESS | COORDINATES | TRUCK SLOTS | TRAILER SLOTS | GEOFENCE | STATUS
      total rows in console: 3 (first 3 captured)
      chips: active, active, maintenance
- NOTE: Yard type and status now use the CO-14 vocabulary — Owned / Leased / Shared and active / inactive / maintenance — rather than the database values PRIVATE / LEASED / SHARED / CROSS_DOCK and A
- LEGEND: CO-14 Yard onboarding ; Driver BRD GPS-003/004, DET-001/002

### Notifications › Notifications   (alerts, sub 0)
- title: Notifications
- description: Every alert in one place. Open any item to acknowledge it, call the driver, or join their chat thread — no need to leave this page.
- header actions: Mark all read
- BANNER [crit] SOS alert from Driver Tyler Brooks — Emergency (911) status received with GPS 37.6390, -120.9969 on TRIP-58024. Emergency response coordinator noti | buttons: Acknowledge, Call driver
- panels (1):
  · «All notifications» — hint: 8 unread of 22
      LIST: SOS alert from Driver Tyler Br — Emergency (911) status received with GPS ; ELD disconnected — TRK-CARR-US — HOS logs may be incomplete. Device TAB-4 ; Insurance certificate expires  — COI expires 2026-08-12. Escalation tier  ; Asset TRK-CARR-US-00142-004 is — DVIR defect reported 2026-07-19: hydraul ; Asset TRK-CARR-US-00142-008 is — Halt reported at San Jose Hub. Reason: i ; CDL expiring — James Carter — CDL NV D6543210 expires 2026-09-12. Rene ; Medical certificate expiring — — Medical Examiner Certificate expires 202
      chips: Ack, Ack, Ack, Ack
      buttons: Call driver, Call driver, Call driver, Call driver, Call driver, Call driver
- LEGEND: Notification Types — CR-, DR-, AST-, TEL-, YD-, DOC-, SAF-, PEN-, ONB-, CS- families ; Driver BRD DT-23, §4.7–§4.14, §4.8 DSP-001…006 ; Carrier View DASH-003

### Reports › Operations   (reports, sub 0)
- title: Operations reports
- description: Fleet, driver and compliance reporting. All five carrier roles hold a view right; export is restricted.
- header actions: Export CSV
- panels (5):
  · «Freight mix by type» — hint: Master Data — Types of Shipment
      BODY: FTL - Standard Goods ⏐ SHP-FTL ⏐ 3 ⏐ FTL - Reefer ⏐ SHP-RF ⏐ 1 ⏐ LTL - Multiple Goods ⏐ SHP-LTL ⏐ 2 ⏐ Dump Truck ⏐ SHP-RCR ⏐ 2
  · «Route profitability & revenue per mile»
      TABLE cols[8]: LANE | LOADS | LOADED MILES | DEADHEAD | REVENUE | RPM | FUEL | MARGIN VS BREAK-EVEN
      total rows in console: 4 (first 4 captured)
      buttons: Export
      in-panel note: Per-mile figures cover mileage-priced freight only. Recurring dump-truck contracts are priced per hour or per trip and are reporte
  · «Recurring contracts» — hint: priced per hour or per trip — not per mile
      TABLE cols[7]: CONTRACT | PATTERN | UNIT RATE | COMMITMENT | VOLUME | CONTRACT VALUE | MARGIN VS BREAK-EVEN
      total rows in console: 2 (first 2 captured)
  · «Payment trends» — hint: ANA-005 — billed against settled by month
      BODY: Feb ⏐ $41,200 ⏐ $39,800 paid · $1,400 disputed ⏐ Mar ⏐ $46,800 ⏐ $46,100 paid · $700 disputed ⏐ Apr ⏐ $52,400 ⏐ $50,900 paid · $1,500 disputed ⏐ May ⏐ $49,100 ⏐ $49,100 paid
  · «Fuel spend by lane» — hint: ANA-003
      BODY: San Jose → Tracy ⏐ $619 ⏐ Sacramento → San Jose ⏐ $798 ⏐ San Jose → Sacramento ⏐ $512 ⏐ San Jose → San Francisco ⏐ $474
- NOTE: Per-mile figures cover mileage-priced freight only. Recurring dump-truck contracts are priced per hour or per trip and are reported below, so they cannot distort RPM.
- NOTE: Deadhead above 15% of total miles is the single biggest drag on revenue per mile — lanes shaded red return less than their declared break-even and should be re-priced or dropped from the ser
- LEGEND: Auth Services BRD V3 — REP category ; Master Data — Types of Shipment ; Driver BRD §4.18 ANA-001…005 ; Driver BRD DT-21 Route Analytics

### Earnings › Earnings   (earnings, sub 0)
- title: Earnings
- description: Revenue, margin and outstanding payments in one place. Approve a pending payment to queue it for payout, pay it immediately once approved, or open a dispute chat directly with mySHIPR admin.
- header actions: Update payment details
- panels (2):
  · «Outstanding payments» — hint: 5
      TABLE cols[6]: PAYMENT | LOAD | AMOUNT | DUE | STATUS | ACTIONS
      total rows in console: 5 (first 5 captured)
      chips: Pending, Approved, Disputed, Paid, Pending
      buttons: Approve, Dispute, Pay now, Dispute, Dispute, Approve
  · «Revenue by load» — hint: 9 loads
      TABLE cols[7]: LOAD | TYPE | LANE | STATUS | RATE | BREAK-EVEN | MARGIN
      total rows in console: 9 (first 7 captured)
      chips: Tendered, Tendered, Carrier Accepted, Carrier Accepted, In Transit, In Transit, At Delivery/Dump, POD Captured, Completed
- LEGEND: Carrier View EARN-01 / EARN-03 ; AP & AR BRD ; Super Set 5A / 5B / 5C ; Shipment Creation §11 / §12

### Earnings › Salary Payout   (earnings, sub 1)
- title: Driver Settlement
- description: One settlement view covering all three CO-18 driver types and all four payment models. AWB and shipment ID are now separate columns.
- BANNER [info] One settlement view for every driver type — CO-18 defines three driver types — Salaried, Contractual and Owner-Operator — and four payment models: Per Mil | buttons: 
- panels (1):
  · «Settlement by driver» — hint: 8 drivers
      TABLE cols[6]: DRIVER | DRIVER TYPE (CO-18) | PAYMENT MODEL | RATE | ASSOCIATED AWB | SHIPMENTS
      total rows in console: 8 (first 7 captured)
      chips: Check digit valid, Check digit valid
- NOTE: AWB and shipment ID are separate identifiers. AWB follows the format {AIRLINE_PREFIX_3}-{SERIAL_8} with a modulo-7 check digit and is only present where the shipment has an air segment.
- LEGEND: CO-18 driver payment configuration ; Driver BRD DT-28 / ERN-004 ; FTL Master Reference §C5 ; Auth Services BRD V3 — AWB

### Settings › My Profile   (settings, sub 0)
- title: My Profile
- description: Your personal account details, distinct from the organisation-wide settings under Company Settings.
- header actions: Edit profile
- panels (3):
  · «Account» — hint: Signed in as
      KV: Name = D. Rao ; Email = d.rao@apexfreight.example ; Role = Carrier Super Admin CSA ; Multi-factor authentication = Enabled ; Last sign-in = 2026-07-24 08:02PDT
      chips: Enabled
  · «Password & security» — hint: personal
      BODY: Organisation-wide sessions and lockout policy are under Sett
      buttons: Change password, Re-enrol MFA device
  · «Display» — hint: Master Data §18
      KV: Company default = America/Los_Angeles PDT — from the registered  ; Sample timestamp = 2026-07-24 09:12PDT ; Density = Comfortable
- LEGEND: Auth Services BRD V3 — self-managed account fields

### Settings › Notification Preferences   (settings, sub 1)
- title: Notification Preferences
- description: How you personally are notified. This does not change what appears in the Notifications section — only how you are alerted.
- panels (1):
  · «Delivery channels» — hint: per notification type
      BODY: Critical alerts (SOS, breakdown, compliance) ⏐ Load tenders & assignment ⏐ Document & compliance reminders ⏐ Messages from drivers ⏐ Weekly / monthly financial reports
- LEGEND: Personal preference — does not affect Notifications section content or audit trail

### Settings › Roles & Users   (settings, sub 2)
- title: Roles & Users
- description: Every person in the carrier organisation, their role, session state and admin controls — plus the permission matrix those roles are built from. The carrier admin assigns roles from a fixed permission catalogue, and may compose new roles from that same catalogue.
- header actions: Create role, Invite user
- BANNER [warn] Auth Services BRD V3 contains two matrices that disagree — The Role Permission Matrix grants drivers.add, drivers.onboard and drivers.update to the Carrier Super Admin a | buttons: 
- panels (3):
  · «Organisation users» — hint: 7 accounts
      TABLE cols[6]: USER | ROLE | STATUS | SECURITY | LAST SIGN-IN | ACTIONS
      total rows in console: 7 (first 7 captured)
      chips: Active, Active, Active, Active, Active, Unverified, Suspended
      buttons: Change role, Freeze, Revoke sessions, Change role, Freeze, Revoke sessions
  · «Functional matrix — fixed permission set» — hint: 14 categories · 75 permission codes
      TABLE cols[6]: FUNCTIONAL CATEGORY | CARRIER SUPER ADMIN | FLEET MANAGER | DISPATCHER | COMPLIANCE MANAGER | SYSTEM ADMIN
      total rows in console: 14 (first 7 captured)
      chips: CREATE / VIEW / UPDATE, ONLY VIEW, ONLY VIEW, ONLY VIEW, ONLY VIEW, CREATE / VIEW / UPDATE, CREATE / VIEW / UPDATE, ONLY VIEW, ONLY VIEW, CREATE / VIEW / UPDATE, CREATE / VIEW / UPDATE, ONLY VIEW
  · «Permission codes in force» — hint: selected from the 75-code catalogue
      TABLE cols[4]: PERMISSION CODE | NAME | CATEGORY | YOUR ROLE
      total rows in console: 43 (first 7 captured)
      chips: Granted, Granted, Granted, Granted, Granted, Granted, Granted, Granted, Granted, Granted, Granted, Granted
- NOTE: Freeze shuts a user down immediately — every active session ends and sign-in is blocked until an admin unfreezes the account. Invites enforce a unique email within the organisation and retur
- LEGEND: CO-28 Invite user ; Auth Services BRD V3 — Permission Categories, Permission Catalogue, Role Permission Matrix ; Notification Types AU-014…AU-023

### Settings › Audit Logs   (settings, sub 3)
- title: Audit Logs
- description: Every role assignment, freeze/unfreeze, session revocation and role-creation event in this organisation, each carrying an Audit ID.
- header actions: Export
- panels (1):
  · «Audit events» — hint: 5 events
      TABLE cols[5]: AUDIT ID | TIMESTAMP | ACTOR | ACTION | DETAIL
      total rows in console: 5 (first 5 captured)
- NOTE: Audit IDs follow the AU-0xx series (AU-014 status changes, AU-018 invites, AU-021 role assignment, AU-022 session revocation, AU-023 profile views). Every entry is immutable once written.
- LEGEND: Auth Services BRD V3 — USERS category ; Notification Types AU-014…AU-023

### Settings › Sessions   (settings, sub 4)
- title: Sessions
- description: Active sign-ins across every user in the organisation, and the security policy that governs them.
- header actions: Revoke all other sessions
- panels (2):
  · «Active sessions» — hint: 5
      TABLE cols[4]: USER | DEVICE | STARTED | ACTION
      total rows in console: 5 (first 5 captured)
      buttons: Revoke, Revoke, Revoke, Revoke
  · «Security policy» — hint: Auth Services BRD V3
      KV: Multi-factor authentication = Enabled required before a session is issued ; Account lockout = After 3 consecutive failed attempts · reset vi ; Session freeze = Freezing a user (Roles & Users) ends every ses ; Multi-organisation login = Available a carrier may also operate as a ship
      chips: Enabled, Available
- LEGEND: Auth Services BRD V3 §3.1, Driver Login ; Notification Types AU-022

### Settings › Company Profile   (settings, sub 5)
- title: Company Profile
- description: Core legal and regulatory identity captured at CO-02, CO-05 and CO-06. This record is locked — it defines the carrier's identity on the platform and cannot be edited from the console. Contact mySHIPR support for corrections.
- header actions: Read only — core identity is frozen
- BANNER [crit] 1 required compliance document outstanding — CO-07 lists eight mandatory carrier documents. Profile completion is blocked at 88% until all are uploaded. | buttons: Go to documents
- panels (5):
  · «Legal identity» — hint: CO-05 · locked
      KV: Company name = Apex Freight LLC ; DBA (Doing Business As) = Apex Logistics ; Entity type = Limited Liability Company (LLC) ; EIN / Tax ID = 87-2214508 ; Corporation number = CA-LLC-2011-884210 ; Year established = 2011 ; Fleet size declared = 8 vehicles · 8 registered ; Country = United States ; Operating scope = US · CA · MX ; Company website = www.apexfreight.example
  · «Regulatory identity & authority» — hint: CO-06 · DOC-001…006
      KV: USDOT number = 3421887 Verified ; MC number = 874120 Verified ; SCAC code = APXF ; Operating authority = Active DOC-004 — may haul interstate freight ; Insurance status = Active ; Compliance status = APPROVED ONB-010 KYC approved ; Account status = Active CO-05 Pending → CO-06 Active
      chips: Verified, Verified, Active, Active, Active
      in-panel note: An inactive operating authority blocks interstate haulage and halts onboarding (CO-06, DOC-005). This status is visible on every s
  · «Contacts» — hint: org.contacts.manage
      LIST: Primary — Super Admin — D. Rao · +1 408 555 0142 · d.rao@apexfre ; Compliance — A. Beckett · +1 408 555 0198 · complianc ; After hours dispatch — +1 408 555 0111
      buttons: Request contact change
  · «Addresses» — hint: org.addresses.manage
      LIST: Registered office — 1180 Coleman Ave, San Jose, CA 95110, US ; Operations — 2400 Grant Line Rd, Tracy, CA 95377, USA
  · «Primary phone & email» — hint: CO-05
      KV: Company phone (US · CA · MX) = +1 408 555 0142 ; Company email = ops@apexfreight.example
- LEGEND: CO-02 Super Admin signup ; CO-05 Company profile ; CO-06 FMCSA verification ; Auth Services BRD V3 — ORG category ; Notification Types DOC-001…006

### Settings › Documents   (settings, sub 6)
- title: Compliance & Documents
- description: The eight carrier documents CO-07 requires, with OCR status, version history and the CO-09 five-tier expiry ladder. Owned by the Compliance Manager.
- header actions: Upload document
- BANNER [crit] 1 required compliance document outstanding — CO-07 lists eight mandatory carrier documents. Profile completion is blocked at 88% until all are uploaded. | buttons: Go to documents
- panels (3):
  · «Carrier documents» — hint: CO-07 · 8 required types
      TABLE cols[7]: DOCUMENT TYPE | STATUS | EXPIRY | UPLOADED | VERSION | OCR | ACTION
      total rows in console: 8 (first 7 captured)
      chips: Expiring, Verified, Verified, Verified, Verified, Verified, Expiring, Missing
      buttons: Replace, Replace, Replace, Replace, Replace, Replace
  · «Expiry escalation ladder» — hint: CO-09 — adopted as the single schedule
      BODY: 1 ⏐ 1 month ⏐ notify at 30 days before expiry ⏐ 2 ⏐ 3 weeks ⏐ notify at 21 days before expiry ⏐ 3 ⏐ 2 weeks ⏐ notify at 14 days before expiry ⏐ 4 ⏐ 7 days ⏐ notify at 7 days before expiry
      in-panel note: Applies to carrier documents, driver CDL and medical certificates, vehicle documents and truck registration expiry. Notification T
  · «Driver-level compliance» — hint: CO-19 identity · CO-20 drug & alcohol
      TABLE cols[5]: DRIVER | IDENTITY (CO-19) | DRUG & ALCOHOL (CO-20) | MEDICAL CERT | INSURED (CO-18)
      total rows in console: 8 (first 7 captured)
      chips: Verified, Compliant, Yes, Verified, Compliant, Yes, Verified, Compliant, Yes, Verified, Compliant, Yes
- LEGEND: CO-04 OCR & virus scan ; CO-07 document upload ; CO-09 expiry monitoring ; CO-19 / CO-20 ; Auth Services BRD V3 — COMP ; Notification Types DOC-001…030

### Settings › Contract   (settings, sub 7)
- title: Contract
- description: Two contract flows are specified in the onboarding workflow. The console shows the one currently in force and flags the target state.
- BANNER [info] Interim flow in force — CO-30 mock contract — CO-30 is an OTP-verified mock contract record. CO-08 (DocuSign e-signature) is the target-state flow and will  | buttons: 
- panels (2):
  · «Current contract» — hint: CO-30
      KV: Contract reference = CTR-APX-00142 ; Status = Verified & saved ; Verification method = Verification code (OTP) confirmed 2026-01-09 ; Bound to = Carrier Company ID CARR-US-00142 ; Contract type = Master carrier agreement (mock record) ; Archived = No
      chips: Verified & saved
      buttons: Update, Archive
  · «Target-state flow» — hint: CO-08 — not yet active
      BODY: Preview contract ⏐ Digital signature via DocuSign ⏐ Signature validation ⏐ Store signed contract
      in-panel note: Until the Document Service is integrated, contract signature has no legal artefact — the record is a verification receipt, not an 
- LEGEND: CO-08 Digital Contract Signing ; CO-30 Contract Management ; Notification Types DOC-026 / DOC-027

### Settings › Finance   (settings, sub 8)
- title: Financial Setup
- description: Stripe Connect onboarding and the ACH payout account required before the carrier can be paid (CO-29). Payment mechanics, commission and settlement timing are governed elsewhere and are not shown here.
- panels (2):
  · «Onboarding status» — hint: CO-29
      KV: Stripe Connect onboarding = Completed ; KYC / business verification = Passed ONB-010 ; ACH payout account = Linked · account ending ••4417 ; ACH status = Active ; Completed at = 2026-01-11 10:24PDT ; W-9 on file = Received DOC-013
      chips: Completed, Passed, Active, Received
      buttons: Re-run onboarding
  · «Payment details» — hint: ACH · payout schedule
      buttons: Update payment details
      in-panel note: Bank account, routing number and your weekly payout day/week are managed in one place.
- LEGEND: CO-29 Financial Setup ; Notification Types DOC-012/013

### Settings › Capacity   (settings, sub 9)
- title: Capacity & Service Profile
- description: The four carrier-declared inputs auction eligibility depends on. Unlike the core Company Profile, these are operational values the carrier keeps current — without them the carrier is filtered out before an auction is ever created, and 6A's freeze rule makes that exclusion permanent for that auction.
- header actions: Update profile
- BANNER [info] These fields decide which loads you are shown — 6A evaluates route match, truck and trailer compatibility, weight and pallet capacity, remaining space, FMCSA  | buttons: 
- panels (3):
  · «Operating lanes» — hint: 6A §3.1 — Route Matching
      BODY: 95112 ⏐ 95376 ⏐ 95112 ⏐ 95814 ⏐ 95814 ⏐ 95112 ⏐ 95376 ⏐ 95202 ⏐ 94103 ⏐ 93901
      buttons: Remove, Remove, Remove, Remove, Remove, Add lane
  · «Declared capacity» — hint: 6A §5.3 — carrier must provide
      KV: Remaining pallet slots = 14 pallets ; Available trailer dimensions = 48 × 8.2 × 9 ft (L × B × H) ; Cost per mile (break-even) = $2.35 / mile ; Equipment capability = Semi Truck (Sleeper Cab), Semi Truck (Day Cab) ; Team-driver capability = Available 6A §6.3 Long Distance Rule
      chips: Available
      in-panel note: Pallet-to-weight validation is blocked pending a decision on weight per pallet: Master Data states 30–40 lbs, the Shipment Executi
  · «Commodity capability» — hint: Master Data §17 — 15 categories
      BODY: Construction Materials ⏐ Metals ⏐ Lumber & Building Supplies ⏐ Agriculture ⏐ Food & Beverage ⏐ Retail Goods ⏐ Automotive ⏐ Industrial Equipment ⏐ Chemicals ⏐ Petroleum ⏐ Refrigerated Goods ⏐ Waste Management
      in-panel note: Hazardous Materials requires a driver with the H endorsement and a valid TSA security threat assessment (DRV-07), and blocks statu
- NOTE: Hazardous Materials requires a driver with the H endorsement and a valid TSA security threat assessment (DRV-07), and blocks status advance to In Transit until confirmed (FTL Manual BR-09).
- LEGEND: 6A Carrier Eligibility & Auction Targeting §3.1–§5.3 ; Carrier View RR-03 ; Master Data §17 Commodity Master ; Notification Types CR-012
