# Steel Plant PdM Sensors — Deployment, Placement & SCADA/Historian Architecture

**Research Date:** 2026-06-08  
**Scope:** Round 2 Tata Steel Hackathon — domain reference for dataset platform design  
**Classification:** [unverified] where sourced from secondary/interpreted material; [verified] where official documentation confirmed

---

## 1. Ranked List of Most Commonly Deployed PdM Sensors in Steel Plants

The steel industry deploys sensors in rough order of penetration and criticality as follows:

### Tier 1 — Universal (virtually every PdM program)

| Rank | Sensor Type | Signal Measured | Why Dominant |
|------|-------------|-----------------|--------------|
| 1 | **Triaxial Accelerometer (Vibration)** | g (acceleration), m/s² | Detects imbalance, misalignment, bearing spall, looseness, gear mesh defects — single sensor surfaces multiple fault modes |
| 2 | **RTD / Thermocouple (Temperature)** | °C / °F | Leading indicator of friction, overload, lubrication failure; cheap and reliable; universal integration via 4-20 mA or direct TC input |
| 3 | **Motor Current Transformer (MCSA)** | Amps RMS + spectrum | Non-invasive, always-on; stator current carries sideband signatures for rotor bars, eccentricity, coupling faults, bearing defects — no physical mounting on rotating parts |

### Tier 2 — Standard in mature programs

| Rank | Sensor Type | Signal Measured | Why Used |
|------|-------------|-----------------|----------|
| 4 | **Pressure Transmitter** | bar / PSI (0-10 bar hydraulics; 0-400 bar rolling forces) | Hydraulic system health, rolling force monitoring, pump discharge/suction differential, coolant circuits |
| 5 | **Flow Meter** (electromagnetic / ultrasonic / Coriolis) | L/min or m³/hr | Cooling water flow loss = imminent thermal failure; lubrication flow drop = bearing starvation |
| 6 | **Online Oil Quality Sensor** | Viscosity, dielectric constant, water content, total acid number (TAN) | Gearbox / hydraulic oil degradation; ferrous particle counters measure debris mass index for catastrophic wear events |

### Tier 3 — Specialist / high-criticality equipment

| Rank | Sensor Type | Signal Measured | Why Used |
|------|-------------|-----------------|----------|
| 7 | **Acoustic Emission (AE) Sensor** | kHz–MHz elastic waves | Detects early-stage crack growth, micro-spalling in bearings and rails; operates 100 kHz–1 MHz; precedes vibration-detectable damage by days to weeks [verified: ScienceDirect] |
| 8 | **Displacement / Proximity Probe** (eddy current) | µm shaft gap | Journal bearing clearance, shaft run-out on large turbines and mill spindles; required by API 670 for critical rotating machinery |
| 9 | **Infrared / Thermal Camera** | °C surface map | Electrical cabinet hot spots, conveyor pulley thermal rise, furnace refractory loss; passive, no contact |
| 10 | **Load Cell / Force Sensor** | kN, tonf | Rolling force, crane hoist load, mold strand force; fatigue-cycle counting for structural life |
| 11 | **Tachometer / Speed Encoder** | RPM, pulse/rev | Required for shaft-order synchronous averaging; enables accurate bearing defect frequency (BPFO/BPFI/BSF/FTF) computation |
| 12 | **Strain Gauge / Fiber Bragg Grating (FBG)** | µε (microstrain) | Caster roll position and strand containment force; structural health of mill housings; Distributed FBG arrays used on continuous caster rolls [verified: PMC/NCBI] |

### Why Vibration + Temperature Dominate

Multi-sensor fusion programs (ArcelorMittal Sentinel, POSCO edge-inference nodes on 180 rolling mill assets) consistently report vibration + temperature as the 80/20 pair: they together expose 70-85% of detectable failure precursors at lowest cost-per-insight ratio. Acoustic emission and current analysis add incremental gain for high-value rotating assets. [unverified: oxmaint.com]

---

## 2. Equipment-to-Sensor Mapping Table

For each equipment class, the sensors fitted and their measurement points:

### 2a. Bearing (standalone or as a sub-component)

| Sensor | Measurement Point | Orientation | Parameter |
|--------|------------------|-------------|-----------|
| Triaxial accelerometer | Bearing housing, as close to load zone as possible | Horizontal + Vertical (radial) + Axial | Broadband vibration; BPFO/BPFI/BSF/FTF frequencies |
| RTD / PT100 | Bearing housing bore or top-cap | — | Housing temperature (alarm limit typically 70-90°C) |
| AE sensor | Bearing housing outer surface | — | High-frequency emission events (100 kHz–500 kHz) |
| Eddy current probe | Inside bearing cap, pointed at shaft | Radial | Shaft displacement / clearance (critical machinery only) |

**Minimum standard:** 2 accelerometers per asset — drive-end (DE) bearing housing + non-drive-end (NDE) bearing housing. Third point on pump/fan casing bearing where accessible. [verified: power-mi.com]

---

### 2b. Electric Motor (induction / DC)

| Sensor | Measurement Point | Parameter |
|--------|------------------|-----------|
| Triaxial accelerometer | DE bearing housing (bolted pad, not adhesive, for heavy motors) | Vibration — rotor imbalance, bearing defects, looseness |
| Triaxial accelerometer | NDE bearing housing | Vibration — structural, belt/coupling excitation |
| RTD | Motor end shield / bearing housing | Bearing temperature |
| RTD or thermocouple | Stator winding (embedded in slot) | Winding temperature — thermal overload, insulation life |
| Current transformer (CT) | Phase leads (all 3 phases, or single + neutral) | MCSA — broken rotor bar sidebands at f₀±2sf₀; air-gap eccentricity harmonics |
| Tachometer / encoder | Shaft end or fan housing | RPM reference for order analysis |

**Steel-specific note:** Large AC/DC motors driving rolling mills, conveyors, and pumps in steel plants generate rotor imbalance, bearing wear, and electrical faults with distinctive vibration signatures. MCSA is especially valuable on inverter-fed drives, where spectral sidebands must be corrected for PWM carrier frequency. [verified: Samotics, MDPI Energies]

---

### 2c. Gearbox

| Sensor | Measurement Point | Parameter |
|--------|------------------|-----------|
| Accelerometer (high-sensitivity, 100 mV/g) | Gear mesh transfer path — bearing housing closest to meshing gears | Gear mesh frequency (GMF) = shaft RPM × number of teeth; sidebands indicate gear wear |
| Accelerometer | Input-side bearing housing | Input shaft bearing defects |
| Accelerometer | Output-side bearing housing | Output shaft bearing defects |
| RTD | Oil sump / drain plug | Oil temperature — lubrication degradation, overload |
| Online oil particle sensor (ferrous debris) | Oil return line or sump sampling port | Ferrous particle index; doubling in 72 hours = acute wear event [unverified: machinerylubrication.com] |
| Oil quality sensor | Inline on oil circuit | Viscosity, water content, dielectric constant |
| Pressure transmitter | Oil supply line | Lubrication pressure drop = starvation risk |

**PCB Piezotronics note:** Gearbox monitoring requires stiff mechanical coupling (machine-bolt mounting preferred over adhesive) to preserve high-frequency GMF accuracy. [verified: PCB Whitepaper WPL_82]

---

### 2d. Pump (centrifugal / positive displacement)

| Sensor | Measurement Point | Parameter |
|--------|------------------|-----------|
| Accelerometer | Motor DE bearing + NDE bearing | Bearing defects, cavitation (broadband noise floor rise) |
| Accelerometer | Pump bearing housing | Impeller unbalance, vane pass frequency (VPF = RPM × number of vanes) |
| Pressure transmitter | Suction side | NPSH margin; low = cavitation imminent |
| Pressure transmitter | Discharge side | System resistance; differential = pump head |
| Flow meter (electromagnetic) | Discharge line | Flow rate — pump degradation visible as flow drop at constant pressure |
| RTD | Pump casing / bearing housing | Temperature — seal failure, bearing overload |
| Vibration | Pump casing axial | Axial thrust imbalance in double-suction pumps |

---

### 2e. Fan / Blower

| Sensor | Measurement Point | Parameter |
|--------|------------------|-----------|
| Accelerometer | Motor DE bearing | Rotor imbalance (1× RPM dominant) |
| Accelerometer | Fan bearing housing | Blade pass frequency (BPF = RPM × blade count) |
| Accelerometer | Motor NDE bearing | Structural resonance |
| RTD | Motor winding + fan bearing | Temperature |
| Differential pressure transmitter | Inlet–outlet duct | Performance degradation (fouling, blade erosion) |
| Vibration (velocity) | Duct/casing | Structural resonance from resonance tuning |

**Steel-specific:** Blast furnace blowers and sinter plant fans are high-criticality assets; often instrumented with API 670-compliant displacement probe pairs (X-Y) on plain bearings. [unverified]

---

### 2f. Compressor (reciprocating / centrifugal / screw)

| Sensor | Measurement Point | Parameter |
|--------|------------------|-----------|
| Accelerometer (or velocity transducer) | Bearing housing (each stage) | Bearing defects, blade pass (centrifugal) |
| Pressure transmitter | Each stage suction & discharge | Stage efficiency, valve condition (recip) |
| Temperature transmitter | Stage inlet + outlet | Interstage temperature rise |
| Vibration (proximity probe, X-Y pair) | Shaft inside bearing (large centrifugal) | Shaft orbit, whirl, surge detection |
| RTD | Cylinder head (reciprocating) | Valve leakage (hot cylinder head = bad valve) |
| Current transformer | Motor supply | Power consumption, load factor |

---

### 2g. Hydraulic System (rolling mills, casters, press lines)

| Sensor | Measurement Point | Parameter |
|--------|------------------|-----------|
| Pressure transmitter (high precision, 0-400 bar) | Cylinder lines (A+B sides) | Rolling force control; cylinder position indirect |
| Servo valve position sensor (LVDT) | Servo valve stem | Position error; valve wear |
| Linear position transducer (LVDT) | Cylinder rod | Gap / draft control |
| Temperature transmitter (RTD) | Oil reservoir + return line | Fluid temp; overheating = degradation |
| Online oil particle counter | Return filter housing | ISO 4406 contamination class; steel-specific: ferrous debris from cylinder walls |
| Flow meter | Supply manifold | Flow drop = pump wear or leakage |
| Accumulator pressure sensor | Accumulator top | Pre-charge pressure (nitrogen); loss = sluggish response |

**Tata-specific context:** Roll hydraulic signals include cylinder position, rolling force, rolling pressure, position error, servo valve stem position, servo command signals, screw position, roll velocity, and motor current — all typically at 100 Hz or faster update rates. [verified: ifactoryapp.com caster analytics]

---

### 2h. Rolling Mill (hot/cold)

| Sensor | Measurement Point | Parameter |
|--------|------------------|-----------|
| Load cell | Mill housing window / roll chock | Rolling force (kN or tonf per stand) |
| Linear encoder / LVDT | Roll gap actuator | Roll gap position |
| Accelerometer | Roll chock bearing housing | Chatter (high-frequency oscillation) at mill-specific resonant frequencies |
| Tachometer | Work roll, backup roll drive | Speed; speed mismatch = surface defect |
| Temperature sensor (pyrometer, non-contact) | Strip entry + exit | Strip temperature; controls reduction schedule |
| Torque sensor (strain gauge on spindle) | Main drive spindle | Torque — overload detection |
| Vibration (eddy current, shaft probe) | Main gear spindles | Spindle oscillation, chatter detection |
| Current + power meter | Main drive motors | Energy; overload |
| Roll force sensor (piezoelectric) | Roll bearing chocks | Dynamic force at roll contact |

---

### 2i. Continuous Caster

| Sensor | Measurement Point | Parameter |
|--------|------------------|-----------|
| Thermocouple array (Type K or S) | Mold copper walls (dense grid — broad face + narrow face) | Mold heat flux; thermal asymmetry → breakout precursor |
| Mold level sensor (radioactive or electromagnetic) | Mold top | Meniscus level; ±3 mm control target |
| Hydraulic pressure transmitter | Oscillator cylinder, segment clamping cylinders | Oscillator friction; segment alignment; strand bulging |
| LVDT / linear encoder | Oscillator stroke | Oscillation amplitude and frequency |
| Load cell | Mold frame | Mold foot force; strand containment |
| Spray flow meter + pressure | Each cooling zone spray header | Water density per zone; clogged nozzle detection |
| Speed encoder | Withdrawal rolls (pinch rolls) | Cast speed (m/min) |
| RTD | Tundish body | Tundish steel temperature |
| FBG strain sensors | Roll segments | Roll deformation / strand containment force |
| Pyrometer (optical) | Strand surface in secondary cooling | Surface temperature profile |

**Critical note:** Thermal deviations causing breakouts develop in under 5 seconds; edge IPCs poll mold thermocouples and segment hydraulics in sub-second intervals (<100 ms latency), bypassing historian round-trips. [verified: ifactoryapp.com]

---

### 2j. Conveyor Belt / Roller Table

| Sensor | Measurement Point | Parameter |
|--------|------------------|-----------|
| Accelerometer | Idler bearing housings (drive pulley, tail pulley, snub pulley) | Bearing defects (idler spin frequency, belt frequency) |
| Accelerometer | Drive motor bearing housings | Motor bearing health |
| Thermal camera / RTD | Drive motor, head pulley surface | Pulley bearing overheating, belt slip |
| Current transformer | Drive motor | Power draw; belt load; motor health |
| Belt tension sensor | Take-up system | Belt sag / tension loss |
| Speed encoder / proximity switch | Drive pulley shaft | Belt speed; slip detection |
| Vision camera / laser profile | Belt surface | Tear, rip, edge damage (advanced systems) |

**Ambient condition note:** Conveyors near furnaces and casters operate in ambient temperatures up to 1,200 °C environment — require ceramic-housed accelerometers and high-temperature-rated cable. [unverified: oxmaint.com]

---

### 2k. Overhead / Ladle Crane

| Sensor | Measurement Point | Parameter |
|--------|------------------|-----------|
| Accelerometer | Hoist motor DE bearing | Bearing defects from vertical load cycles |
| Accelerometer | Travel motor (long travel + cross travel) bearing housings | Drive bearing health |
| Accelerometer | Slew bearing (ladle cranes) | Slew gear health |
| RTD | Motor end frames | Motor winding temperature (alarm: >85°C) |
| Load cell | Hoist rope attachment / equaliser beam | Hoist load; overload detection; cycle counting for structural life |
| Absolute rotary encoder | Hoist drum | Hook height, rope length tracking |
| Current transformer | Hoist and travel motor circuits | Power, overload, brake engagement detection |
| Vibration (rope vibration sensor) | Hoist rope | Rope condition (strand breakage) |
| Brake wear sensor | Drum brake pads | Lining thickness |

---

### 2l. Furnace (Reheating / Blast / Annealing)

| Sensor | Measurement Point | Parameter |
|--------|------------------|-----------|
| Thermocouple (Type S or B — Pt/Rh alloys) | Roof, sidewall, hearth zones | Zone temperature (up to 1300–1600°C) |
| Thermocouple (Type K) | Combustion air supply, flue gas | Air preheat temp, flue losses |
| Pyrometer (optical / radiation) | Slab / billet surface at exit | Strip/slab exit temperature |
| Pressure transmitter | Furnace interior (slightly positive pressure) | Draft control; air ingress (negative = energy loss) |
| Flow meter | Gas + combustion air per burner | Fuel-air ratio; burner efficiency |
| CO / O₂ analyzer | Flue duct | Combustion efficiency; CO = incomplete combustion |
| Refractory monitoring (embedded thermocouple strings) | Refractory wall layers | Wear-through early warning (cold face temp rising) |
| Vibration (on combustion air fans / ID fans) | Fan bearing housings | Fan bearing condition |

---

## 3. Sampling Rates and Historian Storage Modes

### 3a. Typical Sampling Rates by Sensor Class

| Sensor Type | Raw Acquisition Rate | Historian Trend Rate | Notes |
|-------------|---------------------|---------------------|-------|
| Vibration (waveform/spectrum) | 25.6 kHz – 128 kHz | Not stored raw in standard PI — FFT spectrum snapshots taken every 5–60 min | Nyquist requires 2× max frequency of interest; 25.6 kHz covers 10 kHz bandwidth (bearing BPFO range) |
| Vibration (RMS overall) | 1–10 Hz computed | 1 Hz or 0.1 Hz trend stored in historian | Overall RMS is the "trend value"; much lower storage footprint |
| Envelope (demodulated RMS) | 5.12 kHz – 51.2 kHz acquisition → 1 Hz trend | 1 Hz | Early bearing defect detection; acquisition burst-mode then averaged |
| Temperature (RTD/TC) | 0.1 – 1 Hz | 1 Hz or exception on change >0.5°C | Slow physics; 1-second scan overkill for most applications |
| Pressure | 1 – 100 Hz | 1 Hz trend; exception reporting | Rolling hydraulics need 100 Hz; process pressures 1 Hz sufficient |
| Flow | 1 – 10 Hz | 1 Hz | Averaging smooths turbulence noise |
| Current (RMS) | 50/60 Hz (one reading per AC cycle) → 1–10 Hz trend | 1 Hz | MCSA waveform acquisition is separate bursts at kHz |
| Oil quality | 0.001 – 0.1 Hz (one sample per 10–1000 s) | Exception on change | Slow-evolving parameter |
| Load cell / force | 100 Hz – 1 kHz | 1–10 Hz averaged | Rolling forces need high rate for chatter detection |
| Encoder / speed | 1 kHz pulse counting → 10 Hz velocity | 1 Hz | High rate pulse counting; low rate trend |
| Mold thermocouple (caster) | 10–100 Hz | <100 ms to breakout prevention system; 1 Hz to historian | Exception: direct IPC feed for safety-critical |
| AE sensor | 1–10 MHz raw | Not stored raw; AE event count / energy stored at 1 Hz | Only derived features reach historian |

**Rule of thumb:** Vibration raw waveforms are acquired in bursts (typically 1.024 s at 25.6 kHz = 26,214 samples per burst per channel); only computed features (RMS, crest factor, kurtosis, spectral bands, dominant frequency) are pushed to historian at 1 Hz or slower. [unverified: vibromera.eu, iotbearings.com]

---

### 3b. Exception / Dead-Band Compression and the Flat-Line Artifact

**How historian compression works:**

A data historian uses two filtering stages before writing a value to the archive:

1. **Exception deadband (scan-level filter):** A new raw value is only considered for storage if it differs from the last stored value by more than the exception deadband threshold (e.g., ±0.5% of span for temperature). Values within the band are discarded at the interface/OPC layer before entering the archive buffer.

2. **Compression deadband (archive-level filter — Swinging Door algorithm):** Of the values that pass the exception filter, the swinging door algorithm fits a straight-line approximation; points that fall within a tolerance band around the interpolated line are dropped. Only points that "break out" of the sloped box are written to the archive. [verified: hallam-ics.com]

**Practical storage impact:** A 2,000-tag system at 10-second scan without compression → >6 billion values/year. With properly tuned deadbands → 90–98% reduction. A temperature tag stable at 120 °C for 6 hours stores only two records (one at start, one at end) — both identical value at different timestamps.

**The flat-line artifact (critical for ML datasets):**

When compression is aggressive (deadband too wide) or when a sensor is genuinely stuck, the exported historian data shows long stretches of repeated identical values — the "flat line." This manifests in two distinct ways:

- **True flat line (physical):** Process truly held constant (e.g., furnace at setpoint). Legitimate data.
- **Compression flat line (artifactual):** Process varied slightly but stayed within deadband; historian shows last-archived value repeated. Looks identical to the true flat line on export. No quality flag distinguishes these — the compression flat line is stored as "Good" quality.
- **Stale/stuck sensor flat line:** Sensor fails open or short; value freezes. PI may write "Bad Input" digital state, OR (if the interface does not detect it) write the frozen float value continuously as "Good" — indistinguishable from compression flat line without secondary cross-check.

**Implication for dataset platform:** Any data pipeline must implement stale-value detection (e.g., flag runs of identical values > N samples where N = compression_deadband × scan_rate) and cross-correlate with quality codes. Do not assume flat = missing; classify as: [True Steady | Compressed Steady | Stuck Sensor | Communications Loss]. [unverified: flowfuse.com, arcweb.com]

---

## 4. SCADA → Historian Architecture

### 4a. Topology

```
Field Sensors
     │
     ▼ (4-20 mA / HART / Modbus RTU / Profibus)
I/O Modules → PLC / DCS
     │
     ▼ (OPC-DA [legacy] or OPC-UA [modern])
SCADA Server  ←→  HMI
     │
     ▼ (OPC-DA/UA client interface)
Historian Server (OSIsoft PI / AVEVA PI / Honeywell PHD / GE Proficy)
     │
     ├─→ PI Data Archive (compressed time-series)
     ├─→ PI Asset Framework (AF) — hierarchical asset model
     └─→ PI Web API / OLEDB connector
           │
           ▼
     Analytics Layer (Power BI / Seeq / custom ML pipelines)
```

[verified: skan.com, geo-viz.com, oxmaint.ai description]

### 4b. OPC-UA and ISA-95 Integration

OPC-UA has adopted ISA-95 as one of its core information models. The ISA-95 layers map directly to historian hierarchy levels:

| ISA-95 Level | Description | Historian Context |
|-------------|-------------|-------------------|
| L4 | Enterprise (ERP / SAP) | Business context; rarely in historian |
| L3 | MES — Production scheduling | Production orders, batch IDs linked to historian segments |
| L2 | SCADA / DCS supervision | Tag sources; alarm management |
| L1 | PLCs, DCS controllers | Data origin |
| L0 | Field devices / sensors | Physical measurement |

[verified: arxiv.org ISA-95/OPC-UA review 1903.00065]

### 4c. ISA-95 Tag Hierarchy (canonical five-level path)

```
Site . Area . Unit . Equipment . Signal

Example:
TATA_JAMSHEDPUR . HOT_ROLLING . STAND_3 . MAIN_MOTOR . BEARING_DE_VIB_RMS
TATA_JAMSHEDPUR . CASTER_1 . MOLD . THERMOCOUPLE_A12 . TEMPERATURE
TATA_JAMSHEDPUR . BLAST_FURNACE . BLOWER . PUMP_101 . DISCHARGE_PRESSURE
```

OSIsoft PI Asset Framework (AF) provides a rich hierarchical asset model that decouples the naming path from the underlying PI tag name. A concise tag name like `P101.PV` maps to a long AF attribute path `TATA_JSR\BlastFurnace\CoolingWater\Pump101|DischargePressurekPa`. [verified: osipi.wordpress.com, pisharp.com]

**Tag naming segments (common convention):**
- Location code (plant / area abbreviation)
- Equipment type code (MTR = motor, PMP = pump, GB = gearbox, FAN, COMP, etc.)
- Equipment number (sequential)
- Measurement type (VIB = vibration, TEMP = temperature, PRES = pressure, CURR = current, FLW = flow, SPD = speed)
- Point descriptor (DE = drive-end, NDE = non-drive-end, H = horizontal, V = vertical, A = axial, INL = inlet, OUT = outlet)
- Units suffix (optional)

Example: `JSR.HR.STD3.MTR001.VIB.DE.H` = Jamshedpur, Hot Rolling, Stand 3, Motor 001, Vibration, Drive-End, Horizontal

[unverified: osipi.wordpress.com best practices article]

### 4d. Historian Products Deployed in Steel Plants

| Historian | Vendor | Market Position in Steel | Key Characteristics |
|-----------|--------|--------------------------|---------------------|
| **AVEVA PI System** (formerly OSIsoft PI) | AVEVA (Schneider Electric) | Dominant; Tata Steel, ArcelorMittal, POSCO deployments confirmed | Two-stage compression (exception + swinging door); PI Asset Framework for hierarchy; PI Web API for REST access; paradigm shifting from Tag-Centric → AF-Centric |
| **Honeywell PHD** | Honeywell | Significant in integrated mill DCS (Honeywell TDC/Experion sites) | Tight Experion DCS integration; similar time-series compression; less dominant than PI for 3rd-party integration |
| **GE Proficy Historian** (iFIX) | GE Vernova | Common in older North American plants; some Asian plants | Similar dead-band compression; percent-good quality parameter |
| **Canary Historian** | Canary Labs | Growing presence (ISA-95 compliant, unified namespace native) | Modern REST-first; Unified Namespace (MQTT/OPC-UA native); lower cost |
| **Rockwell FactoryTalk Historian** | Rockwell | Rockwell DCS-heavy plants | Built on PI engine under license |

[verified: oxmaint.ai description; geo-viz.com; canarylabs.com blog]

### 4e. OPC Quality Codes — The Standard

OPC-DA and OPC-UA define a 16-bit quality field. The high 2 bits encode the Quality status:

| Quality Class | High 2 bits | Decimal | Hex | Meaning |
|--------------|-------------|---------|-----|---------|
| **Bad** | 00 | 0 | 0x00 | Value is not usable; do not use for control |
| **Uncertain** | 01 | 64 | 0x40 | Value may be correct; use with caution |
| **Good** | 11 | 192 | 0xC0 | Value is reliable |
| **Good, Clamped** | 11 + substatus | 216 | 0xD8 | Value is at a limit (sensor saturated) |

Substatus bits (bits 2-5) add specificity:
- Bad 0x04 — Configuration Error in Server
- Bad 0x0C — Device Failure  
- Bad 0x10 — Sensor Failure
- Uncertain 0x44 — Last Usable Value (historian uses last-known-good)
- Uncertain 0x50 — Sensor Not Accurate (out-of-calibration flag)

[verified: OPC DA Quality Codes — softwaretoolbox.com; opcfoundation.org]

**PI System Digital States (SYSTEM set) — quality stored as named states when numeric value unavailable:**

| PI Digital State | Meaning |
|-----------------|---------|
| `No Data` | No value ever received for this period |
| `Shutdown` | Source system (PLC/DCS) was in shutdown state |
| `Bad Input` | Value received was invalid (type mismatch, out-of-range) |
| `Configure` | PI point configured but interface not started |
| `No Result` | Calculation produced no result (e.g., divide by zero in PE) |
| `Pt Created` | New point, no data yet collected |

Numeric offset for `No Data` in the SYSTEM set = 248. [unverified: pisquare community; AVEVA docs partially confirmed]

### 4f. Typical Historian Export Schema

A standard PI data archive export (CSV / REST / OLEDB) has this row structure:

```
timestamp          | tag                              | value   | quality | asset_id
-------------------+----------------------------------+---------+---------+-----------------------------
2026-06-07 08:00:01| JSR.HR.STD3.MTR001.VIB.DE.H.RMS | 2.34    | 192     | MOTOR-STD3-001
2026-06-07 08:00:02| JSR.HR.STD3.MTR001.VIB.DE.H.RMS | 2.34    | 192     | MOTOR-STD3-001
2026-06-07 08:05:17| JSR.HR.STD3.MTR001.VIB.DE.H.RMS | 2.51    | 192     | MOTOR-STD3-001
2026-06-07 08:10:03| JSR.HR.STD3.MTR001.TEMP.DE      | No Data | —       | MOTOR-STD3-001
```

Note: rows only appear when value changes beyond deadband OR at configured max-time-interval (typically 8 hours for slowly-changing signals). Absence of a row is NOT absence of data — it means the previous value held steady.

**Extended schema (PI AF–enriched export):**

```
timestamp | tag | value | quality | asset_id | asset_class | equipment_type | 
location_site | location_area | location_unit | unit_of_measure | scan_rate_s | 
compression_deadband | engineering_low | engineering_high
```

[unverified: compiled from hallam-ics.com, geo-viz.com, softwaretoolbox.com]

---

## 5. Data Realities a Dataset Platform Must Know

### 5a. Multi-Rate Sensor Problem

A single physical asset will have sensors reporting at wildly different rates:

- Vibration RMS trend: 1 Hz (1 row per second)
- Temperature: 1 row per 60 seconds (or only on change)
- Pressure: 1 row per second
- Oil quality: 1 row per 10 minutes
- Spectrum snapshot: 1 row per 5 minutes (but each row contains a JSON/binary blob of 1024 frequency bins)

When joining these on timestamp to build a feature vector, naive inner-join produces extremely sparse data. A dataset platform must implement **forward-fill-with-staleness-limit** (e.g., carry last temperature value forward up to 5 minutes; beyond that, flag as stale). [unverified: arcweb.com, flowfuse.com]

### 5b. Missing Data Patterns

**Common root causes:**

1. **Communications loss** (PLC to SCADA network drop): historian stores `No Data` or a gap. Duration minutes to hours.
2. **Planned maintenance window** (tag goes to `Shutdown` state): may span days.
3. **Sensor failure** (wiring break, head failure): historian receives `Bad Input` or stale value depending on whether the OPC server can detect it.
4. **Historian interface restart**: brief gap (seconds) every time the OPC interface restarts.
5. **Clock skew**: OPC server timestamp and historian server timestamp diverge. Creates out-of-order records, duplicates, or false gaps. IEEE 1588 PTP synchronization is best practice but not universal. [unverified: PMC clock-skew paper 12468194]
6. **Batch processing mode**: some PLCs batch their OPC updates; data arrives in bursts with identical timestamps for multiple tags.
7. **Compression-induced false flat**: described in §3b above.

### 5c. Timestamp Issues

- **UTC vs. local time confusion**: Historians store UTC internally but display in local time. Exports may include offset inconsistency around DST boundaries.
- **PLC clock drift**: PLCs without NTP synchronization can drift hours over weeks.
- **Retroactive backdating**: Some historians allow manual entry with arbitrary timestamps — these create anomalous data spikes in historical records.
- **Sub-second precision loss**: Some SCADA systems only provide 1-second resolution timestamps even if the underlying event occurred faster.

### 5d. Asset Metadata Requirements

A complete asset registry entry (needed to make sensor data useful for ML):

| Field | Example |
|-------|---------|
| `asset_id` | MOTOR-STD3-001 |
| `asset_class` | Electric Motor |
| `manufacturer` | ABB |
| `model` | M3BP 400 |
| `rated_power_kW` | 3200 |
| `rated_speed_rpm` | 990 |
| `bearing_model_DE` | SKF 6326 |
| `bearing_model_NDE` | SKF 6226 |
| `installation_date` | 2019-03-15 |
| `last_overhaul_date` | 2023-11-02 |
| `criticality_tier` | 1 |
| `connected_tags` | [JSR.HR.STD3.MTR001.VIB.DE.H.RMS, ...] |
| `location_hierarchy` | TATA_JSR / HOT_ROLLING / STAND_3 |
| `failure_modes` | [Bearing Spall, Rotor Bar Break, Winding Short] |

Without this metadata, a dataset of time-series values is not linkable to failure events and is not trainable for condition-specific ML models. [unverified: compiled from multiple sources]

---

## 6. ISA-18.2 Alarm Management

### 6a. Standard Overview

ISA-18.2 (ANSI/ISA-18.2-2016, technical supplement ISA-TR18.2.3-2024) defines the alarm lifecycle for SCADA systems across process industries including steel. [verified: isa.org, mikrodev.com]

### 6b. Priority Tiers

| Priority | Level | Criteria | Typical Response Time |
|----------|-------|----------|-----------------------|
| **P1 — Critical** | Safety / catastrophic equipment damage | Imminent risk to personnel or irreversible process damage (caster breakout, bearing seizure on critical drive) | <1 minute |
| **P2 — High** | Equipment damage risk | Significant degradation, major quality impact (temperature > trip setpoint, severe vibration) | <5 minutes |
| **P3 — Medium** | Process deviation | Off-normal but recoverable without major loss (elevated vibration trend, oil temperature rising) | <15 minutes |
| **P4 — Low** | Advisory / informational | Early warning, maintenance trigger | <60 minutes or next shift |

[verified: mikrodev.com ISA-18.2 article; instrumentationtools.com]

### 6c. Alarm KPIs (ISA-18.2 benchmarks)

| KPI | ISA-18.2 Good Target | "Flood" Threshold |
|-----|---------------------|-------------------|
| Alarm rate (normal operations) | <1 alarm / 10 min per operator | >10 alarms / 10 min = flood |
| Chattering alarms | <5% of total | >10% = rationalization needed |
| Standing alarms | <5 per console | >10 = suppression/shelving required |
| P1 Critical alarms as % of total | <5% | >10% = priorities miscalibrated |

**Before rationalization, a large steel or chemical plant can generate 200+ alarms/hour. After proper ISA-18.2 rationalization: <10 alarms/hour.** [verified: mikrodev.com case study; isa.org]

### 6d. Steel-Specific Alarm Configuration Patterns

- **Vibration alarms:** Typically two levels — ISO 10816 "Warning" (1.5× baseline RMS) and "Danger" (2.5× baseline RMS). Alarm deadband (hysteresis) set to 10% of span to prevent chatter on noisy signals.
- **Temperature alarms:** Motor bearing: Warning 75°C, Danger 90°C. Mold thermocouple: deviation alarm (any single TC deviating >15°C from neighbors triggers P1 breakout response).
- **Oil particle alarms:** Ferrous index Warning at 150% of baseline; Danger at 200% or on sustained 72-hour doubling trend.
- **Process safety alarms:** Tied to SIS (Safety Instrumented System) layer separate from SCADA alarms — governed by IEC 61511, not ISA-18.2.

---

## 7. Additional Data Platform Considerations

### 7a. Vibration Feature Types in Historian vs. Raw Acquisition Systems

A standalone vibration monitoring system (e.g., SKF Enlight, Emerson AMS 2140, Bently Nevada System 1) acquires raw waveforms but stores computed features to the historian:

| Feature | Formula / Method | Fault Sensitivity |
|---------|-----------------|-------------------|
| Overall RMS velocity (ISO 10816) | √(mean(v²)) over 10–1000 Hz | General machine condition |
| Crest factor | Peak / RMS | Impulsiveness (early bearing) |
| Kurtosis | 4th statistical moment of accel waveform | Very early bearing spall |
| Envelope RMS (BPFO/BPFI) | High-pass filter → rectify → low-pass → RMS | Bearing defect frequency energy |
| Gear mesh frequency amplitude | FFT bin at GMF ± sidebands | Gear wear severity |
| Spectral band alarms | RMS in user-defined Hz bands | Customizable fault detection |

Only these scalar features flow into the historian at 1 Hz. The raw waveforms (26k samples/sec) are stored locally in the vibration analyzer or in a separate high-speed data store (e.g., National Instruments historian, Seeq, or custom HDF5 archive). [unverified: oxmaint.com vibration analysis; vibromera.eu]

### 7b. Wireless vs. Wired Sensors

Modern deployments (Tata Steel, ArcelorMittal Sentinel) increasingly deploy **wireless triaxial vibration+temperature sensors** (IP67, loop-powered or battery, ISA 100.11a or WirelessHART protocol) on Tier-2 assets. Key data characteristics:

- Reporting interval: typically 1–15 minutes (not continuous streaming)
- Battery life: 2–5 years at 15-minute reporting
- Data gaps: radio interference from furnaces / high EMI environments creates periodic packet loss
- Latency: 5–30 seconds from measurement to historian

Wired accelerometers (IEPE, 4-20 mA, Profibus) remain dominant on Tier-1 critical assets where continuous monitoring and sub-second alarm response is required. [unverified: oxmaint.com deployment scale article]

### 7c. Edge IPC / Edge Historian Layer

Modern architecture (post-2022) often includes an **edge historian** layer:

```
Sensor → Gateway/Edge IPC → Edge Historian (local, 30-day buffer)
                                    │
                                    ▼ (compressed delta sync)
                           Enterprise PI Historian
```

The edge layer runs local ML inference (POSCO's 180-asset deployment), stores raw bursts locally, and only transmits features upstream. This means the enterprise historian may only receive 1 Hz feature data even though 25.6 kHz raw data exists at the edge. A dataset platform that only taps the enterprise historian will miss raw waveform fidelity. [verified: oxmaint.com POSCO deployment reference]

### 7d. Multi-Site Tag Collisions

Large steel companies (Tata Steel: Jamshedpur, Kalinganagar, Port Talbot, IJmuiden) often have independently evolved tag naming conventions per site. A company-wide dataset will have:
- Different depth of ISA-95 hierarchy (some 3-level, some 5-level)
- Inconsistent unit codes (PSI vs. bar vs. kPa for same type of sensor)
- Identical tag names for different assets across sites
- Timestamp timezone variations

Asset UUID + site prefix normalization is mandatory before cross-site model training. [unverified: general knowledge from multi-site historian implementations]

---

## Sources

| Source | URL | Credibility Note |
|--------|-----|-----------------|
| Predictive Maintenance Trends for Steel Industry 2026 | [oxmaint.com](https://oxmaint.com/industries/steel-plant/predictive-maintenance-trends-steel-industry-2026-ai-iiot) | Industry blog; useful practitioner data |
| ArcelorMittal Sentinel Platform | [oxmaint.com](https://oxmaint.com/industries/steel-plant/arcelormittal-sentinel-platform-predictive-maintenance-steel-robots-equipment) | Industry blog; specific platform details |
| Steel Plant SCADA-PI Historian Integration | [oxmaint.ai](https://oxmaint.ai/industries/steel-plant/steel-plant-scada-pi-historian-integration-cmms) | Industry blog; architecture overview |
| OSIsoft PI Historian Overview | [geo-viz.com](https://geo-viz.com/blog/osisoft-pi-historian-data-historian-overview/) | Practitioner overview |
| PI Tag Naming Conventions | [osipi.wordpress.com](https://osipi.wordpress.com/2009/10/28/pi-tag-naming-conventions/) | Official OSIsoft community |
| PI Tag Naming Rules Deep Dive | [pisharp.com](https://www.pisharp.com/article/511/pi-tag-naming-rules-a-deep-dive-into-best-practices) | PI specialist blog |
| ISA-95 / OPC-UA Interoperability Review | [arxiv.org 1903.00065](https://arxiv.org/pdf/1903.00065) | Academic; peer-reviewed |
| OPC Foundation — ISA-95 Information Model | [reference.opcfoundation.org](https://reference.opcfoundation.org/ISA-95/v100/docs/4) | Official OPC Foundation |
| Vibration Sensor Placement Guide | [power-mi.com](https://power-mi.com/content/where-place-vibration-sensor) | PdM practitioner reference |
| PCB Piezotronics Gearbox Whitepaper | [pcb.com WPL_82](https://www.pcb.com/ContentStore/MktgContent/whitepapers/WPL_82_GearBoxWhitePaper.pdf) | Manufacturer; technical |
| Vibration Monitoring for Steel Industry | [ctconline.com](https://www.ctconline.com/blog-archive/vibration-monitoring-for-the-steel-industry/) | Sensor manufacturer blog |
| In-Depth Study of Vibration Sensors for CM | [MDPI Sensors 2024](https://www.mdpi.com/1424-8220/24/3/740) | Peer-reviewed journal |
| Vibration Analysis for Pumps & Compressors | [blackhawkequipment.com](https://blackhawkequipment.com/resources/Vibration-Analysis-for-Pumps-Compressors) | Equipment specialist |
| Condition Monitoring for Conveyors | [oxmaint.com](https://oxmaint.com/industries/steel-plant/condition-monitoring-conveyors-bearings-rollers) | Industry blog |
| Continuous Caster Analytics | [ifactoryapp.com](https://ifactoryapp.com/industries/steel-plant/continuous-caster-analytics-mold-segments) | IIoT platform vendor |
| Liquid Core Detection via FBG | [PMC/NCBI 9783033](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9783033/) | Peer-reviewed journal |
| MCSA for Fault Detection | [Samotics](https://samotics.com/kb/drive-train-insights-using-electric-motor-as-vibration-sensor/) | MCSA specialist vendor |
| MCSA Inverter-Fed Systems | [MDPI Energies 2023](https://www.mdpi.com/1996-1073/16/15/5628) | Peer-reviewed |
| Oil Debris / Particle Counter PdM | [machinerylubrication.com](https://www.machinerylubrication.com/Read/219/debris-monitor-pdm) | Lubrication specialist |
| Ferrous Debris Sensor Study | [PMC/NCBI 6187361](https://pmc.ncbi.nlm.nih.gov/articles/PMC6187361/) | Peer-reviewed |
| Steel Plant Crane Analytics | [ifactoryapp.com](https://ifactoryapp.com/industries/steel-plant/steel-plant-crane-analytics-eot-ladle) | IIoT platform vendor |
| AE for Bearing Crack Detection | [ScienceDirect 0888327005000051](https://www.sciencedirect.com/science/article/abs/pii/S0888327005000051) | Peer-reviewed |
| AE Sensor — ScienceDirect Topics | [sciencedirect.com](https://www.sciencedirect.com/topics/chemistry/acoustic-emission) | Reference aggregator |
| Introduction & Optimization of Data Historians | [hallam-ics.com](https://www.hallam-ics.com/blog/introduction-and-optimization-of-data-historians) | Systems integrator blog |
| SCADA Data Management at Scale | [tigerdata.com](https://www.tigerdata.com/learn/scada-data-management-at-scale-architecture-historians-and-the-modern-database) | Data platform vendor |
| ISA Deadband Compression Patent | [USPTO 7496590](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7496590) | Patent specification |
| OPC DA Quality Codes | [softwaretoolbox.com](https://support.softwaretoolbox.com/app/answers/detail/a_id/414/~/opc-da-quality-codes) | OPC integration vendor |
| OPC Quality Codes Reference | [opcsupport.com](https://www.opcsupport.com/s/article/What-are-the-OPC-Quality-Codes) | OPC support portal |
| ISA-18.2 Alarm Management | [instrumentationtools.com](https://instrumentationtools.com/isa-18-2-alarm-management-in-process-plants/) | Process instrumentation reference |
| Alarm Management ISA-18.2 SCADA | [mikrodev.com](https://www.mikrodev.com/alarm-management-isa-18-2-scada-alarms-event-management-priority-and-operator-effectiveness/) | SCADA vendor |
| ISA-TR18.2.3-2024 | [isa.org](https://www.isa.org/standards-and-publications/isa-standards/isa-18-series-of-standards) | Official ISA standards body |
| Industrial Data Validation Guide | [flowfuse.com](https://flowfuse.com/blog/2025/11/industrial-data-validation-guide/) | IIoT platform blog |
| Valid Real-Time Data for Analytics | [arcweb.com](https://www.arcweb.com/industry-best-practices/industrial-data-analytics-solutions-require-valid-real-time-data) | ARC Advisory Group |
| Clock Synchronization IIoT | [PMC/NCBI 12468194](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12468194/) | Peer-reviewed |
| RMS Vibration Analysis | [vibromera.eu](https://vibromera.eu/glossary/rms/) | Vibration instrumentation vendor |
| Sampling Rate for Bearing Monitoring | [iotbearings.com](https://iotbearings.com/why-sampling-rate-matters-bearing-vibration-monitoring/) | IIoT bearing specialist |
| AVEVA PI System Digital State Set | [docs.aveva.com](https://docs.aveva.com/bundle/pi-server-s-da-admin/page/1022870.html) | Official AVEVA documentation |
| What Causes PI Data Quality Issues | [tychodata.com 2025](https://blog.tychodata.com/2025/03/11/what-causes-data-quality-issues-in-pi-system/) | PI specialist consultancy |
| Motor & Pump Vibration Monitoring 2026 | [oxmaint.com](https://oxmaint.com/blog/post/motor-pump-vibration-monitoring-bearing-failure-detection) | Industry blog |
| Smart Conveyor Belt Monitoring | [ifactoryapp.com](https://ifactoryapp.com/industries/steel-plant/conveyor-belt-health-monitoring-steel) | IIoT platform vendor |
| Steel Plant Hydraulic Maintenance | [oxmaint.com](https://oxmaint.com/industries/steel-plant/steel-plant-hydraulic-system-maintenance-mills-casters-furnaces) | Industry blog |

---

*Document generated: 2026-06-08. All [unverified] tags indicate data synthesized from secondary sources or practitioner blogs not independently cross-verified against primary manufacturer/standards documentation.*
