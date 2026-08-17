# FIGMA FILE — CURRENT STATE (mySHIPR — Carrier Console)

3 pages. `01 Design System` (Foundations + Components sections) · `02 Screens` (Desktop 42 frames @1440 + Responsive 84 frames @900/375) · `03 Prototype` (flow & coverage board).
Verified counts from the live file: desktop frames 42, responsive frames 84, component instances 27,384, wired sidebar interactions 756, components 27, variants 110.

## Component library (27 masters / 110 variants)
Icon · Sidebar/Item · Sidebar/SubItem · Sidebar/Root · TopBar · Button · Chip/Status · Chip/Filter · Legend Chip · KPI Card · Pulse Cell · HOS Bar · Bar Row · Panel · Table/Header · Table/Row · Pager · Banner · Note · EmptyState · Toast · Field · Drawer · List Item · Stop Line · KV Row · Lane

## Screens — every block on every frame

### 01 Dashboard — Overview
- nav: Dashboard › Overview   (key=dashboard, subIdx=0)
- title: Fleet Operations Overview
- description: Live snapshot of Apex Freight across the US / CA / MX network — assets, drivers, tenders, loads and compliance, all on one page.
- blocks (6):
  BANNER [crit] 1 required compliance document outstanding — CO-07 lists eight mandatory carrier documents. Profile completion is blocked at 88% until  | buttons: Go to documents
  PULSE: 3 Trucks available ; 2 Out of service / halt ; 2 Drivers available ; 4 Drivers on duty ; 2 Non-dispatchable
  KPI: Fleet size=8 (3 available · 5 not dispatchable) ; In transit=1 (Master Data asset status) ; Tenders open=2 (awaiting accept / decline) ; Awaiting assignment=2 (accepted, no asset selected) ; Trips on going=3 (1 scheduled) ; POD outstanding=1 (awaiting close-out)
  COLUMNS ratio=[1.6, 1]
    PANEL «Fleet by asset status» — hint: interactive · Master Data — 7 values
        - BARS: Available=3 ; Unavailable=1 ; In Transit=1 ; Halt=1 ; At Pickup=0 ; At Delivery/Dump=1 ; Out of Service=1
    PANEL «Drivers by dispatch eligibility» — hint: interactive · FMCSA gate OPS-05 / DRV-002
        - DONUT: Dispatchable 62.5% ; Verification pending 12.5% ; Suspended — compliance 12.5% ; Uninsured (CO-18) 12.5%
  COLUMNS ratio=[1, 1]
    PANEL «Hours of Service — nearing limit» — hint: ELD feed · fleet-wide
        - LIST items: Sofia Torres ; Priya Nair ; Marcus Reyes ; Tyler Brooks
    PANEL «Outstanding payments» — hint: 4 need action
        - LIST items: PMT-CARR-US-00142-0001 · $2,380 ; PMT-CARR-US-00142-0002 · $1,180 ; PMT-CARR-US-00142-0003 · $640 ; PMT-CARR-US-00142-0004 · $1,920
  LEGEND: Master Data — asset & driver status ; Auth Services BRD V3 ; Shipment Execution OPS-01…OPS-12 ; Carrier Onboarding CO-01…CO-30

### 02 Fleet — All Vehicles
- nav: Fleet › All Vehicles   (key=fleet, subIdx=0)
- title: All Vehicles
- description: Every field captured at CO-10 and validated at CO-11 — licence plate, plate state, registration expiry, make and model. Rows open the full asset record.
- header actions: Register truck, Bulk upload
- blocks (3):
  PANEL «Fleet» — hint: 8 vehicles
      - FILTERS Asset status: All, Available, Unavailable, In Transit, Halt, At Pickup, At Delivery/Dump, Out of Service
      - TABLE cols[9]: (blank) | Truck | Type | Make / Model | Plate | Registration expiry | Asset status | CO-11 | Home yard ; rows shown: 6
      - PAGER: Showing 1–6 of 8
  NOTE [amber]: Rows shaded red are not dispatchable — asset status is Out of Service or Halt, so allows_dispatch is false. The load assignment wizard filters these out automatically (OP
  LEGEND: CO-10 Truck Registration ; CO-11 DMV validation ; Master Data §1.2 truck types ; Master Data asset status ; Auth Services BRD V3 — FLEET

### 02.2 Fleet — Active Vehicles
- nav: Fleet › Active Vehicles   (key=fleet, subIdx=1)
- title: Active Vehicles
- description: Trucks currently moving or on site, by Master Data asset status.
- header actions: Register truck, Bulk upload
- blocks (3):
  PANEL «Fleet» — hint: 8 vehicles
      - TABLE cols[9]: (blank) | Truck | Type | Make / model | Plate | Registration expiry | Asset status | CO-11 | Home yard ; rows shown: 2
  NOTE [blue]: Rows shaded red are not dispatchable — asset status is Out of Service or Halt, so allows_dispatch is false. The load assignment wizard filters these out automatically (OP
  LEGEND: CO-10 Truck Registration ; CO-11 DMV validation ; Master Data §1.2 truck types ; Master Data asset status ; Auth Services BRD V3 — FLEET

### 02.3 Fleet — Idle Vehicles
- nav: Fleet › Idle Vehicles   (key=fleet, subIdx=2)
- title: Idle Vehicles
- description: Trucks with asset status Available and therefore dispatchable.
- header actions: Register truck, Bulk upload
- blocks (3):
  PANEL «Fleet» — hint: 8 vehicles
      - TABLE cols[9]: (blank) | Truck | Type | Make / model | Plate | Registration expiry | Asset status | CO-11 | Home yard ; rows shown: 3
  NOTE [blue]: Rows shaded red are not dispatchable — asset status is Out of Service or Halt, so allows_dispatch is false. The load assignment wizard filters these out automatically (OP
  LEGEND: CO-10 Truck Registration ; CO-11 DMV validation ; Master Data §1.2 truck types ; Master Data asset status ; Auth Services BRD V3 — FLEET

### 02.4 Fleet — Maintenance & DVIR
- nav: Fleet › Maintenance & DVIR   (key=fleet, subIdx=3)
- title: Maintenance & DVIR
- description: Maintenance events and driver vehicle inspection reports. Logging an event sets the asset status and therefore gates dispatch.
- header actions: Log maintenance
- blocks (4):
  PANEL «Assets requiring attention» — hint: 5 vehicles
      - TABLE cols[7]: Truck | Type | Asset status | Defect / reason | Last dvir | Detail | Action ; rows shown: 5
      - TEXT lines:  ; buttons: Log event, Log event, Log event
  PANEL «Maintenance types» — hint: FLEET-003 catalogue
      - TEXT lines: OIL_CHANGE · DOT_ANNUAL_INSPECTION ⏐ TIRE_ROTATION · BRAKE_SERVICE ⏐ PM_SERVICE · REPAIR ⏐ REEFER_PM · TABLET_BREAKDOWN
      - TEXT lines: This catalogue currently has no business-document source — it originat
  PANEL «Inspection reminders» — hint: DR-025 / DR-026 · TEL-011 / TEL-012
      - LIST items: Pre-trip inspection outstanding — TRK-CA ; DVIR defect — TRK-CARR-US-00142-004 ; DOT annual inspection due — TRK-CARR-US-
  LEGEND: Carrier View FLEET-003 ; Notification Types CR-010, CR-022, TEL-011, TEL-012 ; Driver BRD DR-025 / DR-026 ; Fields For HOS inspection events ; Tablet Breakdown / Device Under Repair — engineering brief

### 02.5 Fleet — Vehicle documents
- nav: Fleet › Vehicle documents   (key=fleet, subIdx=4)
- title: Vehicle documents
- description: Vehicle-level documents and expiries, on the same CO-09 five-tier ladder as carrier documents — including truck registration expiry.
- blocks (2):
  PANEL «Documents by vehicle» — hint: 8 vehicles
      - TABLE cols[7]: Truck | Registration expiry | REGISTRATION (CO-11) | INSURANCE (CO-11) | Dot annual inspection | Cargo insurance | Action ; rows shown: 7
      - PAGER: Showing 1–7 of 8
      - TEXT lines:  ; buttons: Upload, Upload, Upload
  LEGEND: CO-10 registration expiry ; CO-11 DMV validation ; CO-09 expiry ladder ; Carrier View FLEET-004

### 02.6 Fleet — Vehicle Types
- nav: Fleet › Vehicle Types   (key=fleet, subIdx=5)
- title: Vehicle Types
- description: The full Master Data §1.2 truck catalogue — ten types. Dump trucks, bobtails, yard trucks, tankers and car haulers are all registrable.
- blocks (4):
  BANNER [info] Dump truck, bobtail and yard truck are now registrable — Bobtail is a truck type in Master Data, so the count is read from the catalogue rather tha
  PANEL «Trailers» — hint: 7 units
      - TABLE cols[9]: Trailer | Type | Vin | Make / year | Length | Max payload | Status | Attached to | Photo ; rows shown: 7
  NOTE [blue]: Maximum payload is a legal-weight field captured at CO-12 and drives the capacity filter in the assignment wizard (OPS-04).
  LEGEND: Master Data §1.1 trailer types ; Master Data §1.2 truck types ; CO-12 Trailer onboarding ; CO-13 Assign trailer to truck

### 02.7 Fleet — Devices & ELD
- nav: Fleet › Devices & ELD   (key=fleet, subIdx=6)
- title: Devices & ELD
- description: Tablet-to-truck pairing and ELD sync health. The tablet belongs to the truck, so this pairing is the foundation of the driver-identification model.
- header actions: Add device
- blocks (4):
  BANNER [crit] TAB-4478 disconnected — HOS logging inactive on TRK-CARR-US-00142-008 — Last sync 2026-07-23 06:02. HOS logs may be incomplete (TEL-002). CO-23 requires the Fleet | buttons: Re-pair
  PANEL «Devices» — hint: 7 registered
      - TABLE cols[6]: Device | Paired truck | Provider | Status | Last sync | Action ; rows shown: 7
      - TEXT lines:  ; buttons: Unassign, Report faulty, Unassign
  NOTE [blue]: Reporting a device faulty unpairs it, moves its truck to Out of Service with reason "Tablet Breakdown / Device Under Repair", and blocks dispatch. Pairing a replacement d
  LEGEND: CO-23 ELD integration ; CO-24 Tablet device assignment ; Notification Types TEL-001 / TEL-002 ; Tablet Breakdown / Device Under Repair — engineering brief

### 02.8 Fleet — HOS Status
- nav: Fleet › HOS Status   (key=fleet, subIdx=7)
- title: HOS Status
- description: Hours of service per truck, sourced from the ELD sync. Warning thresholds follow TEL-003 (30 minutes remaining) and TEL-004 (violation past the limit) against the 11-hour driving maximum — no other threshold is applied.
- blocks (3):
  PANEL «HOS by vehicle» — hint: 6 paired vehicles
      - TABLE cols[6]: Truck | Driver logged in | Duty status | Remaining | Location | Warning ; rows shown: 6
  NOTE [blue]: Open question (OC-3): no document defines what should happen if the driver who logs in has insufficient remaining hours — block the login, warn, alert dispatch, or nothin
  LEGEND: Fields For HOS — HOS Duty Status ; Driver BRD §4.2 ELD-001…006 ; Notification Types TEL-003 / TEL-004 / CR-021

### 03 Drivers — All Drivers
- nav: Drivers › All Drivers   (key=drivers, subIdx=0)
- title: All Drivers
- description: Click any driver for their full profile — status, documents, HOS, ratings, earnings, licence and insurance all in one place.
- header actions: Add driver, Bulk upload
- blocks (3):
  PANEL «Driver roster» — hint: 8 drivers
      - FILTERS Driver status: All, Offline, Available, On Duty, In Transit, Off Duty
      - TABLE cols[8]: Driver | Contact | CDL | Type | Status | HOS | Location | Dispatch eligibility ; rows shown: 8
  NOTE [blue]: Dispatch eligibility is a derived gate, not a status — FMCSA medical certificate, CDL validity, identity verification (CO-19) and insurance (CO-18) must all pass before a
  LEGEND: CO-17…CO-21 Driver onboarding ; Master Data — 19 driver statuses ; Fields For HOS ; Auth Services BRD V3 — DRVMGT

### 03.2 Drivers — On Duty
- nav: Drivers › On Duty   (key=drivers, subIdx=1)
- title: On Duty
- description: Drivers currently on duty, by Master Data driver status.
- header actions: Add driver, Bulk upload
- blocks (3):
  PANEL «Driver roster» — hint: 8 drivers
      - TABLE cols[8]: Driver | Contact | Cdl | Type | Status | Hos | Location | Dispatch eligibility ; rows shown: 4
  NOTE [blue]: The eligibility column applies the FMCSA gate documented in DRV-002, CO-20, DOC-017 and DOC-019 and enforced at assignment by OPS-05. Blocked drivers cannot be selected i
  LEGEND: CO-17 / CO-18 driver onboarding ; CO-19 identity verification ; CO-20 drug & alcohol ; Master Data driver status (19 values) ; Shipment Execution OPS-05

### 03.3 Drivers — Off Duty
- nav: Drivers › Off Duty   (key=drivers, subIdx=2)
- title: Off Duty
- description: Drivers off duty or offline.
- header actions: Add driver, Bulk upload
- blocks (3):
  PANEL «Driver roster» — hint: 8 drivers
      - TABLE cols[8]: Driver | Contact | Cdl | Type | Status | Hos | Location | Dispatch eligibility ; rows shown: 2
  NOTE [blue]: The eligibility column applies the FMCSA gate documented in DRV-002, CO-20, DOC-017 and DOC-019 and enforced at assignment by OPS-05. Blocked drivers cannot be selected i
  LEGEND: CO-17 / CO-18 driver onboarding ; CO-19 identity verification ; CO-20 drug & alcohol ; Master Data driver status (19 values) ; Shipment Execution OPS-05

### 04 Loads — Tenders
- nav: Loads › Tenders   (key=loads, subIdx=0)
- title: Tenders
- description: Loads awarded to Apex Freight and awaiting a reply. Accepting the tender links the rate confirmation and moves the load to Carrier Accepted (LED-02).
- blocks (9):
  BANNER [info] Accepting a tender is its own step — Master Data’s lifecycle has "Carrier Accepted" as a distinct state, Ledger LED-02 makes it
  PANEL «SHP-RF-10001 · FTL - Reefer» — hint: Tender expires 2026-07-24 18:00 PDT
  KPI: Awarded rate=$2,480 (as bid) ; Indicative break-even=$2,050 (from your cost per mile) ; Margin=$430 (before penalties) ; TONU exposure=$200 (truck ordered not used)
  COLUMNS ratio=[1, 1]
    PANEL «Stops» — hint: 2 stops · LIVE unload
        - STOPS: P Sacramento, CA ; D San Jose, CA
    PANEL «Load specification» — hint: Master Data §17 commodity master
        - KV rows: Commodity ; Equipment required ; Temperature ; Pre-cooling ; Pallets / weight ; Rate confirmation ; AWB
  PANEL «Tender decision» — hint: LED-02 · DOC-026 / DOC-027
      - TEXT lines: Accepting signs the rate confirmation and moves SHP-RF-10001 to Carrie ; buttons: Accept tender & sign rate confirmation, Decline
  PANEL «SHP-LTL-10004 · LTL - Multiple Goods» — hint: Tender expires 2026-07-25 09:00 PDT
  KPI: Awarded rate=$3,120 (as bid) ; Indicative break-even=$2,640 (from your cost per mile) ; Margin=$480 (before penalties) ; TONU exposure=$150 (truck ordered not used)
  PANEL «Stops» — hint: 4 stops · 2 pickups, 2 deliveries
      - STOPS: P San Jose, CA ; P Tracy, CA ; D Sacramento, CA ; D San Francisco, CA
  LEGEND: Shipment Creation 1.2 ; Ledger LED-01…LED-05 ; DOC-026 / DOC-027 rate confirmation ; Master Data — 16 shipment statuses

### 04.2 Loads — Awaiting Assignment
- nav: Loads › Awaiting Assignment   (key=loads, subIdx=1)
- title: Awaiting Assignment
- description: Accepted loads with no truck, trailer or driver selected. This is where the carrier does its core job: choosing the truck and trailer that will run the load.
- blocks (3):
  PANEL «Awaiting Assignment» — hint: 2 loads
      - TABLE cols[10]: Load | Lane | Equipment | Status | Truck | Trailer | Driver | Progress | Rate | (blank) ; rows shown: 2
      - TEXT lines:  ; buttons: Assign assets, Assign assets
  NOTE [blue]: Selecting assets runs the OPS-03 / OPS-04 / OPS-05 eligibility filters: capacity against shipment weight, equipment type match, annual inspection and insurance validity, 
  LEGEND: Shipment Execution OPS-01…OPS-12 ; Master Data — Shipment Status (16 states) ; Super Set — per-stop execution data ; Notification Types CR-007 / FTL-01 / DT-001

### 04.3 Loads — In Execution
- nav: Loads › In Execution   (key=loads, subIdx=2)
- title: In Execution
- description: Loads with assets committed and moving. Per-stop status, live position and recurring cycle counts.
- blocks (2):
  PANEL «In Execution» — hint: 3 loads
      - TABLE cols[10]: Load | Lane | Equipment | Status | Truck | Trailer | Driver | Progress | Rate | (blank) ; rows shown: 3
  LEGEND: Shipment Execution OPS-01…OPS-12 ; Master Data — Shipment Status (16 states) ; Super Set — per-stop execution data ; Notification Types CR-007 / FTL-01 / DT-001

### 04.4 Loads — POD & Close-out
- nav: Loads › POD & Close-out   (key=loads, subIdx=3)
- title: POD & Close-out
- description: Proof of delivery captured by the driver, reviewed here before the load is closed. POD gates close-out and opens the payment sequence (LED-05).
- blocks (2):
  PANEL «SHP-FTL-10003 · POD review» — hint: Captured 2026-07-23 16:42 PDT
      - KV rows: GPS at submission ; Signature ; Damage notes ; Photos ; Receipts ; Delivered ; Driver ; Truck / trailer
      - TEXT lines:  ; buttons: Confirm POD & close out, Request resubmission
  LEGEND: Driver BRD POD-001…008, DT-25, DT-26 ; Auth Services BRD V3 — POD category ; Master Data POD event sequences ; Ledger LED-05 ; Carrier View SHP-006

### 04.5 Loads — Completed
- nav: Loads › Completed   (key=loads, subIdx=4)
- title: Completed
- description: Delivered loads with POD captured and close-out complete.
- blocks (2):
  PANEL «Completed» — hint: 2 loads
      - TABLE cols[10]: Load | Lane | Equipment | Status | Truck | Trailer | Driver | Progress | Rate | (blank) ; rows shown: 2
  LEGEND: Shipment Execution OPS-01…OPS-12 ; Master Data — Shipment Status (16 states) ; Super Set — per-stop execution data ; Notification Types CR-007 / FTL-01 / DT-001

### 04.6 Loads — History
- nav: Loads › History   (key=loads, subIdx=5)
- title: History
- description: Archived loads.
- blocks (2):
  PANEL «History» — hint: 1 loads
      - TABLE cols[10]: Load | Lane | Equipment | Status | Truck | Trailer | Driver | Progress | Rate | (blank) ; rows shown: 1
  LEGEND: Shipment Execution OPS-01…OPS-12 ; Master Data — Shipment Status (16 states) ; Super Set — per-stop execution data ; Notification Types CR-007 / FTL-01 / DT-001

### 05 Trips — On going
- nav: Trips › On going   (key=trips, subIdx=0)
- title: Trips — On going
- description: A trip is one truck movement against a load. Every trip links to its load, and both follow the single Master Data lifecycle. Live position for every on-going trip is also on the Dashboard Overview.
- blocks (3):
  BANNER [info] Open question (OC-4) — Shipments, Trips and Loads are modelled as three entities across three documents. This bui
  PANEL «On going» — hint: 3 trips
      - TABLE cols[7]: Trip | Load | Lane | Truck | Driver | ETA | Progress ; rows shown: 3
  LEGEND: Master Data — Shipment Status ; Carrier View TRIP-01…03 ; FTL Master Reference status machine

### 05.2 Trips — Scheduled
- nav: Trips › Scheduled   (key=trips, subIdx=1)
- title: Trips — Scheduled
- description: A trip is one truck movement against a load. Every trip links to its load, and both follow the single Master Data lifecycle.
- blocks (3):
  PANEL «Scheduled» — hint: 1 trips
      - TABLE cols[7]: Trip | Load | Lane | Truck | Driver | Eta | Progress ; rows shown: 1
  NOTE [blue]: Open question (OC-4): Shipments, Trips and Loads are modelled as three entities across three documents. This build treats the trip as a view over the load and adopts Mast
  LEGEND: Master Data — Shipment Status ; Carrier View TRIP-01…03 ; FTL Master Reference status machine

### 05.3 Trips — Upcoming
- nav: Trips › Upcoming   (key=trips, subIdx=2)
- title: Trips — Upcoming
- description: A trip is one truck movement against a load. Every trip links to its load, and both follow the single Master Data lifecycle.
- blocks (3):
  PANEL «Upcoming» — hint: 1 trips
      - TABLE cols[7]: Trip | Load | Lane | Truck | Driver | Eta | Progress ; rows shown: 1
  NOTE [blue]: Open question (OC-4): Shipments, Trips and Loads are modelled as three entities across three documents. This build treats the trip as a view over the load and adopts Mast
  LEGEND: Master Data — Shipment Status ; Carrier View TRIP-01…03 ; FTL Master Reference status machine

### 05.4 Trips — Completed
- nav: Trips › Completed   (key=trips, subIdx=3)
- title: Trips — Completed
- description: A trip is one truck movement against a load. Every trip links to its load, and both follow the single Master Data lifecycle.
- blocks (3):
  PANEL «Completed» — hint: 2 trips
      - TABLE cols[7]: Trip | Load | Lane | Truck | Driver | Eta | Progress ; rows shown: 2
  NOTE [blue]: Open question (OC-4): Shipments, Trips and Loads are modelled as three entities across three documents. This build treats the trip as a view over the load and adopts Mast
  LEGEND: Master Data — Shipment Status ; Carrier View TRIP-01…03 ; FTL Master Reference status machine

### 05.5 Trips — Cancelled
- nav: Trips › Cancelled   (key=trips, subIdx=4)
- title: Trips — Cancelled
- description: A trip is one truck movement against a load. Every trip links to its load, and both follow the single Master Data lifecycle.
- blocks (3):
  PANEL «Cancelled» — hint: 1 trips
      - TABLE cols[7]: Trip | Load | Lane | Truck | Driver | Eta | Progress ; rows shown: 1
  NOTE [blue]: Open question (OC-4): Shipments, Trips and Loads are modelled as three entities across three documents. This build treats the trip as a view over the load and adopts Mast
  LEGEND: Master Data — Shipment Status ; Carrier View TRIP-01…03 ; FTL Master Reference status machine

### 06 Driver Ops — Detention
- nav: Driver Ops › Detention   (key=ops, subIdx=0)
- title: Detention
- description: Detention starts at geofence arrival (GPS-004) and runs against the free time agreed for that stop. Minutes past free time are billable and must be raised before the load closes out.
- header actions: Export
- blocks (5):
  BANNER [warn] 2 stops accruing detention right now — DET-003 notifies dispatch as free time expires. Detention is not recoverable once the load
  KPI: Accruing now=2 (stops past free time) ; Billable minutes=195 (across all open stops) ; Recoverable value=$254 (before close-out) ; Within free time=1 (no charge)
  PANEL «Detention events» — hint: 4
      - TABLE cols[10]: Event | Stop | Driver / truck | Arrived | Free time | Elapsed | Billable | Amount | Status | Action ; rows shown: 4
  NOTE [blue]: Open question (OC-11): the Auth Services BRD V3 matrix gives Driver Operations to the Carrier Super Admin alone, yet every channel on these screens is addressed to dispat
  LEGEND: Driver BRD §4.14 DET-001…005 ; GPS-004 geofence arrival ; Ledger LED-05 close-out

### 06.2 Driver Ops — Exceptions & Safety
- nav: Driver Ops › Exceptions & Safety   (key=ops, subIdx=1)
- title: Exceptions & Safety
- description: Route deviation, excessive idle, distance mismatch, speeding, breakdown and reefer deviation. CO-25 generates a red flag; this is where it lands.
- blocks (4):
  BANNER [crit] 3 open exceptions — 2 critical — A critical exception holds the asset out of dispatch until it is cleared. Acknowledging re
  PANEL «Exception log» — hint: 6 events
      - TABLE cols[9]: Event | Type | Driver | Asset | Trip | Detail | Detected | Status | Action ; rows shown: 6
      - TEXT lines:  ; buttons: Acknowledge, Clear, Acknowledge
  NOTE [blue]: Every row here is a channel the Driver BRD specifies: CO-25 exception monitoring, GPS-005 distance, GPS-007 / DR-007 speed, MEC-001…005 breakdown, TRL-002 / ALT-003 reefe
  LEGEND: Carrier Onboarding CO-25 ; Driver BRD §4.11 TRL-002, §4.13 MEC-001…005 ; GPS-005 / GPS-007 ; Notification Types ALT-002 / ALT-003 / DR-007

### 06.3 Driver Ops — Messages
- nav: Driver Ops › Messages   (key=ops, subIdx=2)
- title: Messages
- description: Two-way dispatch messaging with every driver on a live trip. Text, voice notes, documents and location, with read receipts — DSP-001…006, under two seconds delivery.
- blocks (5):
  PANEL «Conversation — Marcus Reyes» — hint: +1 408 555 0231 · 001
      - TEXT lines: MR · Loaded and rolling out of San Jose. Seal 88231 applied. ⏐ Marcus Reyes · 09:41 PDT · read · Y ⏐ Copy. Consignee contact for Tracy is +1-1234567890, ask for the dock s ⏐ You · 09:44 PDT · read · MR ⏐ Live location · 37.7016, -121.7680 · I-580 near Livermore, CA ⏐ Marcus Reyes · 10:58 PDT · read · MR ⏐ Voice note · 0:14 · “Traffic on 580 eastbound, adding about 25 minutes ⏐ Marcus Reyes · 11:02 PDT · read · Y ⏐ rate-confirmation-SHP-FTL-10005.pdf ⏐ 184 KB · DSP-004 document sharing · You · 11:05 PDT · read ; buttons: Play, Open, Send
  PANEL «Threads» — hint: 2 drivers
      - LIST items: Marcus Reyes ; Tyler Brooks
  PANEL «Delivery» — hint: DSP-006
      - KV rows: Target delivery ; Read receipts ; Retention
  NOTE [blue]: Open question (OC-11): the Auth Services BRD V3 matrix gives Driver Operations to the Carrier Super Admin alone, yet every channel on these screens is addressed to dispat
  LEGEND: Driver BRD §4.8 DSP-001…006 ; Driver BRD DT-08 ; Auth Services BRD V3 — DRVOPS

### 07 RR — Coming soon
- nav: RR › Coming soon   (key=rr, subIdx=0)
- title: RR — Rate & Auction Bidding
- description: Real-time load auctions, bidding and bid history for this carrier.
- blocks (2):
  PANEL «None»
      - EMPTY STATE: Coming soon — Auction and bidding mechanics (lot visibility, live bidding, won / los
  LEGEND: 6A Carrier Eligibility & Auction Targeting ; Carrier View RR-01…RR-06

### 08 Yards — All yards
- nav: Yards › All yards   (key=yards, subIdx=0)
- title: All Yards
- description: Yard address and geo-coordinates are captured at CO-14 — a yard without an address cannot be used for dispatch, and the coordinates drive geofencing, arrival detection and detention timing.
- header actions: Add yard
- blocks (3):
  PANEL «Yards» — hint: 3
      - TABLE cols[9]: Yard | Type (CO-14) | Subtype | Address | Coordinates | Truck slots | Trailer slots | Geofence | Status ; rows shown: 3
  NOTE [amber]: Yard type and status now use the CO-14 vocabulary — Owned / Leased / Shared and active / inactive / maintenance — rather than the database values PRIVATE / LEASED / SHARE
  LEGEND: CO-14 Yard onboarding ; Driver BRD GPS-003/004, DET-001/002

### 09 Notifications
- nav: Notifications › Notifications   (key=alerts, subIdx=0)
- title: Notifications
- description: Every alert in one place. Open any item to acknowledge it, call the driver, or join their chat thread — no need to leave this page.
- header actions: Mark all read
- blocks (3):
  BANNER [crit] SOS alert from Driver Tyler Brooks — Emergency (911) status received with GPS 37.6390, -120.9969 on TRIP-58024. Emergency respo | buttons: Acknowledge, Call driver
  PANEL «All notifications» — hint: 8 unread of 22
      - FILTERS Category: All, SOS, Telematics, Documents, Assets, Yard, Loads, Safety, Penalties, Onboarding, Detention, Exceptions
      - LIST items: SOS alert from Driver Tyler Brooks ; ELD disconnected — TRK-CARR-US-00142-008 ; Insurance certificate expires in 19 days ; Asset TRK-CARR-US-00142-004 is Out of Se ; Asset TRK-CARR-US-00142-008 is on Halt ; CDL expiring — James Carter ; Medical certificate expiring — Tyler Bro ; HOS warning — Priya Nair, 30 minutes rem ; Truck TRK-CARR-US-00142-001 assigned to  ; Bid accepted — SHP-RF-10001
  LEGEND: Notification Types — CR / DR / AST / TEL / DOC / YD / SAF / ONB / PEN / CS ; CO-09 five-tier expiry ladder

### 10 Reports — Operations
- nav: Reports › Operations   (key=reports, subIdx=0)
- title: Operations reports
- description: Fleet, driver and compliance reporting. All five carrier roles hold a view right; export is restricted.
- header actions: Export CSV
- blocks (5):
  KPI: Fleet utilisation=63% (5 of 8 engaged) ; Dispatchable assets=3 (of 8 registered) ; Compliant drivers=6 (of 8 on roster)
  KPI: On-time delivery=94% (last 30 days) ; Documents expiring ≤30 d=4 (carrier + driver) ; Loads completed (30 d)=1 (across all freight types)
  PANEL «Freight mix by type» — hint: Master Data — Types of Shipment
      - BARS: FTL - Standard Goods=3 ; FTL - Reefer=1 ; LTL - Multiple Goods=2 ; Dump Truck=2 ; Multileg=1
  PANEL «Route profitability & revenue per mile»
      - TABLE cols[8]: Lane | Loads | Loaded miles | Deadhead | Revenue | RPM | Fuel | Margin vs break-even ; rows shown: 5
  LEGEND: Auth Services BRD V3 — REP ; Ledger — settlement ; Master Data — Types of Shipment

### 11 Earnings — Earnings
- nav: Earnings › Earnings   (key=earnings, subIdx=0)
- title: Earnings
- description: Revenue, margin and outstanding payments in one place. Approve a pending payment to queue it for payout, pay it immediately once approved, or open a dispute chat directly with mySHIPR admin.
- header actions: Update payment details
- blocks (4):
  KPI: Gross revenue=$368,670 (all loads in view) ; Net margin=22% (after fuel, maintenance & settlement) ; Recurring programmes=$349,650 (dump truck contracts) ; Outstanding balance=$5,060 (4 payments awaiting action)
  PANEL «Outstanding payments» — hint: 5
      - TABLE cols[6]: Payment | Load | Amount | Due | Status | Actions ; rows shown: 5
  PANEL «Revenue by load» — hint: 9 loads
      - TABLE cols[7]: Load | Type | Lane | Status | Rate | Break-even | Margin ; rows shown: 7
  LEGEND: Ledger — LED-01…LED-05 ; CO-29 financial setup ; Auth Services BRD V3 — BILL / PAY

### 11.2 Earnings — Salary Payout
- nav: Earnings › Salary Payout   (key=earnings, subIdx=1)
- title: Driver Settlement
- description: One settlement view covering all three CO-18 driver types and all four payment models. AWB and shipment ID are now separate columns.
- blocks (4):
  BANNER [info] One settlement view for every driver type — CO-18 defines three driver types — Salaried, Contractual and Owner-Operator — and four pay
  PANEL «Settlement by driver» — hint: 8 drivers
      - TABLE cols[6]: Driver | DRIVER TYPE (CO-18) | Payment model | Rate | Associated awb | Shipments ; rows shown: 7
      - PAGER: Showing 1–7 of 8
  NOTE [blue]: AWB and shipment ID are separate identifiers. AWB follows the format {AIRLINE_PREFIX_3}-{SERIAL_8} with a modulo-7 check digit and is only present where the shipment has 
  LEGEND: CO-18 driver payment configuration ; Driver BRD DT-28 / ERN-004 ; FTL Master Reference §C5 ; Auth Services BRD V3 — AWB

### 12 Settings — My Profile
- nav: Settings › My Profile   (key=settings, subIdx=0)
- title: My Profile
- description: Your personal account details, distinct from the organisation-wide settings under Company Settings.
- header actions: Edit profile
- blocks (2):
  COLUMNS ratio=[1.6, 1]
    PANEL «Account» — hint: Signed in as
        - KV rows: Name ; Email ; Role ; Multi-factor authentication ; Last sign-in
    PANEL «Password & security» — hint: personal
        - TEXT lines: Organisation-wide sessions and lockout policy are under Settings → Ses ; buttons: Change password, Re-enrol MFA device
    PANEL «Display» — hint: Master Data §18
        - TEXT lines: Timestamps are stored in UTC and rendered in this zone on every screen
        - KV rows: Company default ; Sample timestamp ; Density
  LEGEND: Auth Services BRD V3 — self-managed account fields ; Master Data §18 time zones

### 12.2 Settings — Notification Preferences
- nav: Settings › Notification Preferences   (key=settings, subIdx=1)
- title: Notification Preferences
- description: How you personally are notified. This does not change what appears in the Notifications section — only how you are alerted.
- blocks (2):
  PANEL «Delivery channels» — hint: per notification type
      - TEXT lines: Critical alerts (SOS, breakdown, compliance) ⏐ Load tenders & assignment ⏐ Document & compliance reminders ⏐ Messages from drivers ⏐ Weekly / monthly financial reports
  LEGEND: Personal preference — does not affect Notifications section content or audit trail

### 12.3 Settings — Roles & Users
- nav: Settings › Roles & Users   (key=settings, subIdx=2)
- title: Roles & Users
- description: Every person in the carrier organisation, their role, session state and admin controls — plus the permission matrix those roles are built from. The carrier admin assigns roles from a fixed permission catalogue, and may compose new roles from that same catalogue.
- header actions: Create role, Invite user
- blocks (6):
  BANNER [warn] Auth Services BRD V3 contains two matrices that disagree — The Role Permission Matrix grants drivers.add, drivers.onboard and drivers.update to the C
  PANEL «Organisation users» — hint: 7 accounts
      - TABLE cols[6]: User | Role | Status | Security | Last sign-in | Actions ; rows shown: 7
      - TEXT lines:  ; buttons: Change role, Freeze, Revoke sessions
  PANEL «Functional matrix — fixed permission set» — hint: 14 categories · 75 permission codes
      - TABLE cols[6]: Functional category | Carrier super admin | Fleet manager | Dispatcher | Compliance manager | System admin ; rows shown: 7
      - PAGER: Showing 1–7 of 14
  PANEL «Permission codes in force» — hint: selected from the 75-code catalogue
      - TABLE cols[4]: Permission code | Name | Category | Your role ; rows shown: 7
      - PAGER: Showing 1–7 of 43
  NOTE [blue]: Freeze shuts a user down immediately — every active session ends and sign-in is blocked until an admin unfreezes the account. Invites enforce a unique email within the or
  LEGEND: CO-28 Invite user ; Auth Services BRD V3 — Permission Categories, Permission Catalogue, Role Permission Matrix ; Notification Types AU-014…AU-023

### 12.4 Settings — Audit Logs
- nav: Settings › Audit Logs   (key=settings, subIdx=3)
- title: Audit Logs
- description: Every role assignment, freeze/unfreeze, session revocation and role-creation event in this organisation, each carrying an Audit ID.
- header actions: Export
- blocks (3):
  PANEL «Audit events» — hint: 5 events
      - TABLE cols[5]: Audit id | Timestamp | Actor | Action | Detail ; rows shown: 5
  NOTE [blue]: Audit IDs follow the AU-0xx series (AU-014 status changes, AU-018 invites, AU-021 role assignment, AU-022 session revocation, AU-023 profile views). Every entry is immuta
  LEGEND: Auth Services BRD V3 — USERS category ; Notification Types AU-014…AU-023

### 12.5 Settings — Sessions
- nav: Settings › Sessions   (key=settings, subIdx=4)
- title: Sessions
- description: Active sign-ins across every user in the organisation, and the security policy that governs them.
- header actions: Revoke all other sessions
- blocks (3):
  PANEL «Active sessions» — hint: 5
      - TABLE cols[4]: User | Device | Started | Action ; rows shown: 5
      - TEXT lines:  ; buttons: Revoke, Revoke, Revoke
  PANEL «Security policy» — hint: Auth Services BRD V3
      - KV rows: Multi-factor authentication ; Account lockout ; Session freeze ; Multi-organisation login
  LEGEND: Auth Services BRD V3 §3.1, Driver Login ; Notification Types AU-022

### 12.6 Settings — Company Profile
- nav: Settings › Company Profile   (key=settings, subIdx=5)
- title: Company Profile
- description: Core legal and regulatory identity captured at CO-02, CO-05 and CO-06. This record is locked — it defines the carrier's identity on the platform and cannot be edited from the console. Contact mySHIPR support for corrections.
- header actions: Read only — core identity is frozen
- blocks (7):
  BANNER [crit] 1 required compliance document outstanding — CO-07 lists eight mandatory carrier documents. Profile completion is blocked at 88% until  | buttons: Go to documents
  PANEL «Legal identity» — hint: CO-05 · locked
      - KV rows: Company name ; DBA (Doing Business As) ; Entity type ; EIN / Tax ID ; Corporation number ; Year established ; Fleet size declared ; Country ; Operating scope ; Company website
  PANEL «Regulatory identity & authority» — hint: CO-06 · DOC-001…006
      - KV rows: USDOT number ; MC number ; SCAC code ; Operating authority ; Insurance status ; Compliance status ; Account status
      - TEXT lines: An inactive operating authority blocks interstate haulage and halts on
  PANEL «Contacts» — hint: org.contacts.manage
      - LIST items: Primary — Super Admin ; Compliance ; After hours dispatch
      - TEXT lines:  ; buttons: Request contact change
  PANEL «Addresses» — hint: org.addresses.manage
      - LIST items: Registered office ; Operations
  PANEL «Primary phone & email» — hint: CO-05
      - KV rows: Company phone (US · CA · MX) ; Company email
  LEGEND: CO-02 Super Admin signup ; CO-05 Company profile ; CO-06 FMCSA verification ; Auth Services BRD V3 — ORG category ; Notification Types DOC-001…006

### 12.7 Settings — Documents
- nav: Settings › Documents   (key=settings, subIdx=6)
- title: Compliance & Documents
- description: The eight carrier documents CO-07 requires, with OCR status, version history and the CO-09 five-tier expiry ladder. Owned by the Compliance Manager.
- header actions: Upload document
- blocks (5):
  BANNER [crit] 1 required compliance document outstanding — CO-07 lists eight mandatory carrier documents. Profile completion is blocked at 88% until  | buttons: Go to documents
  PANEL «Carrier documents» — hint: CO-07 · 8 required types
      - TABLE cols[7]: Document type | Status | Expiry | Uploaded | Version | Ocr | Action ; rows shown: 7
      - PAGER: Showing 1–7 of 8
      - TEXT lines:  ; buttons: Replace, Replace, Replace
  PANEL «Expiry escalation ladder» — hint: CO-09 — adopted as the single schedule
      - TEXT lines: 1 ⏐ 1 month ⏐ notify at 30 days before expiry ⏐ 2 ⏐ 3 weeks ⏐ notify at 21 days before expiry ⏐ 3 ⏐ 2 weeks ⏐ notify at 14 days before expiry ⏐ 4 ⏐ 7 days ⏐ notify at 7 days before expiry ⏐ 5 ⏐ daily after expiry
      - TEXT lines: Applies to carrier documents, driver CDL and medical certificates, veh
  PANEL «Driver-level compliance» — hint: CO-19 identity · CO-20 drug & alcohol
      - TABLE cols[5]: Driver | IDENTITY (CO-19) | DRUG & ALCOHOL (CO-20) | Medical cert | INSURED (CO-18) ; rows shown: 7
      - PAGER: Showing 1–7 of 8
  LEGEND: CO-04 OCR & virus scan ; CO-07 document upload ; CO-09 expiry monitoring ; CO-19 / CO-20 ; Auth Services BRD V3 — COMP ; Notification Types DOC-001…030

### 12.8 Settings — Contract
- nav: Settings › Contract   (key=settings, subIdx=7)
- title: Contract
- description: Two contract flows are specified in the onboarding workflow. The console shows the one currently in force and flags the target state.
- blocks (4):
  BANNER [info] Interim flow in force — CO-30 mock contract — CO-30 is an OTP-verified mock contract record. CO-08 (DocuSign e-signature) is the target-
  PANEL «Current contract» — hint: CO-30
      - KV rows: Contract reference ; Status ; Verification method ; Bound to ; Contract type ; Archived
      - TEXT lines:  ; buttons: Update, Archive
  PANEL «Target-state flow» — hint: CO-08 — not yet active
      - TEXT lines: Preview contract · Digital signature via DocuSign ⏐ Signature validation · Store signed contract
      - TEXT lines: Until the Document Service is integrated, contract signature has no le
  LEGEND: CO-08 Digital Contract Signing ; CO-30 Contract Management ; Notification Types DOC-026 / DOC-027

### 12.9 Settings — Finance
- nav: Settings › Finance   (key=settings, subIdx=8)
- title: Financial Setup
- description: Stripe Connect onboarding and the ACH payout account required before the carrier can be paid (CO-29). Payment mechanics, commission and settlement timing are governed elsewhere and are not shown here.
- blocks (3):
  PANEL «Onboarding status» — hint: CO-29
      - KV rows: Stripe Connect onboarding ; KYC / business verification ; ACH payout account ; ACH status ; Completed at ; W-9 on file
      - TEXT lines:  ; buttons: Re-run onboarding
  PANEL «Payment details» — hint: ACH · payout schedule
      - TEXT lines: Bank account, routing number and your weekly payout day/week are manag ; buttons: Update payment details
  LEGEND: CO-29 Financial Setup ; Notification Types DOC-012/013

### 12.10 Settings — Capacity
- nav: Settings › Capacity   (key=settings, subIdx=9)
- title: Capacity & Service Profile
- description: The four carrier-declared inputs auction eligibility depends on. Unlike the core Company Profile, these are operational values the carrier keeps current — without them the carrier is filtered out before an auction is ever created, and 6A's freeze rule makes that exclusion permanent for that auction.
- header actions: Update profile
- blocks (6):
  BANNER [info] These fields decide which loads you are shown — 6A evaluates route match, truck and trailer compatibility, weight and pallet capacity, rem
  PANEL «Operating lanes» — hint: 6A §3.1 — Route Matching
      - TEXT lines: 95112 · 95376 ⏐ 95112 · 95814 ⏐ 95814 · 95112 ⏐ 95376 · 95202 ⏐ 94103 · 93901 ; buttons: Remove, Remove, Remove
  PANEL «Declared capacity» — hint: 6A §5.3 — carrier must provide
      - KV rows: Remaining pallet slots ; Available trailer dimensions ; Cost per mile (break-even) ; Equipment capability ; Team-driver capability
      - TEXT lines: Pallet-to-weight validation is blocked pending a decision on weight pe
  PANEL «Commodity capability» — hint: Master Data §17 — 15 categories
      - TEXT lines: Construction Materials ⏐ Metals ⏐ Lumber & Building Supplies ⏐ Agriculture ⏐ Food & Beverage ⏐ Retail Goods ⏐ Automotive ⏐ Industrial Equipment ⏐ Chemicals ⏐ Petroleum ⏐ Refrigerated Goods ⏐ Waste Management ⏐ Oversized Cargo ⏐ General Freight
      - TEXT lines: Hazardous Materials requires a driver with the H endorsement and a val
  NOTE [blue]: Hazardous Materials requires a driver with the H endorsement and a valid TSA security threat assessment (DRV-07), and blocks status advance to In Transit until confirmed 
  LEGEND: 6A Carrier Eligibility & Auction Targeting §3.1–§5.3 ; Carrier View RR-03 ; Master Data §17 Commodity Master ; Notification Types CR-012
