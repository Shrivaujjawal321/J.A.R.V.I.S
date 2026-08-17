# Steel-Plant Predictive Maintenance — Complete Sensor & Instrumentation Taxonomy
**Prepared:** 2026-06-08  
**Purpose:** Ground-truth reference for data-quality platform design — what realistic sensor data looks like in a steel plant environment.

---

## 1. Overview

Steel plants instrument every rotating and static asset with a layered sensor suite. Data flows from field devices → PLCs/DCS → OPC-UA server → SCADA/HMI → Historian (OSIsoft PI / AVEVA / Honeywell PHD / GE Proficy) → analytics / ML platform. Understanding each sensor's physics, realistic value ranges, sampling rates, and failure modes is prerequisite to building meaningful data-quality rules.

---

## 2. Sensor Taxonomy — Full Detail

---

### 2.1 Vibration — Accelerometers

**Physical quantity measured:** Vibration (acceleration, integrated to velocity, double-integrated to displacement)  
**Transducer type:** Piezoelectric accelerometer (IEPE/ICP), MEMS (for lower-freq wireless nodes)  
**Mounting:** Stud-mounted (best — 20 kHz), adhesive-mounted (good — 10 kHz), magnetic (field survey — 2 kHz). Always on rigid, non-rotating structural part (bearing housing preferred). Two orthogonal radial axes (vertical + horizontal) per bearing; one axial where thrust loads exist.  
**Typical sensitivity:** 100 mV/g (standard); 10 mV/g (high-shock, rolling-mill roll chocks); 500 mV/g (low-freq, slow rotors)  
**Vendors:** PCB Piezotronics, Brüel & Kjær, Wilcoxon, IFM Electronic  

**Units and measurement domains:**

| Domain | Unit | Preferred for |
|--------|------|--------------|
| Velocity (broadband) | mm/s RMS | ISO 10816/20816 health zones |
| Acceleration | g RMS or m/s² | High-freq bearing/gear faults |
| Displacement (shaft) | µm peak-peak | Low-speed, journal bearings |

**ISO 10816-3 / ISO 20816-3 Velocity Zones** (10–1000 Hz broadband, non-rotating parts, machines 15 kW–300 kW = Group 2 / >300 kW = Group 1):

| Zone | Meaning | Group 2 Rigid (mm/s RMS) | Group 1 Rigid (mm/s RMS) |
|------|---------|--------------------------|--------------------------|
| A | Newly commissioned; acceptable | ≤ 2.3 | ≤ 3.5 |
| B | Unrestricted long-term operation | 2.3–4.5 | 3.5–7.1 |
| C | Restricted operation — remediate | 4.5–7.1 | 7.1–11.2 |
| D | Dangerous — immediate action | > 7.1 | > 11.2 |

> Note: ISO 20816-3 (2022 successor to ISO 10816-3) applies the same zone structure but refines machine groupings. Flexible-foundation machines are permitted ~40% higher thresholds than rigid-foundation values above. [Source: ISO 10816-3 standard; vibromera.eu glossary]

**Typical healthy ranges in steel plant equipment:**

| Asset | Healthy (mm/s RMS) | Degrading | Action |
|-------|-------------------|-----------|--------|
| Rolling mill main drive motor | 1.5–3.5 | 3.5–7.1 | > 7.1 |
| Gearbox (pinion) | 2.0–4.5 | 4.5–11 | > 11 |
| Centrifugal pump | 0.5–2.3 | 2.3–4.5 | > 4.5 |
| Roll chock bearing (work roll) | 1.0–4.0 | 4.0–10 | > 10 |
| Continuous caster withdrawal roll | 1.0–3.5 | 3.5–8 | > 8 |

**Sampling rate:** 
- Continuous online monitoring: 5–25 kHz raw acquisition, decimated to 1–2 kHz for streaming; broadband RMS computed every 1–10 s
- Spectral / FFT snapshots: triggered or every 1–30 min; 2048–65 536-point FFT
- Waveform capture (burst): 25–100 kHz for envelope analysis (bearing defect frequencies)

**Failure modes detected:**
- Imbalance (1× RPM peak)
- Misalignment (1×, 2× RPM; axial elevation)
- Bearing inner/outer race, ball defects (BPFI, BPFO, BSF — sub-harmonics)
- Gear mesh frequency and sidebands
- Resonance / critical speed crossing
- Structural looseness (sub-harmonics, multiple harmonics)
- Cavitation (broadband high-freq energy rise)

---

### 2.2 Temperature

#### 2.2a RTD / PT100 (Resistance Temperature Detector)

**Physical quantity:** Temperature of bearing housing, motor winding, coolant return  
**Operating range:** −25 °C to +250 °C (bearing); up to +850 °C (stator winding RTDs are rare above 200 °C)  
**Accuracy:** ±0.1–0.5 °C at operating point — high-class accuracy matters because fault-onset thermal rise in bearings is only 3–8 °C above baseline  
**Typical healthy range:**
- Rolling bearing housing: 40–80 °C (ambient +10–40 °C over ambient is the watch point)
- Motor stator winding (Class F insulation): ≤ 155 °C continuous; alarm at +20 °C over design
- Gearbox oil sump: 50–80 °C

**Degrading indicators:** Rise > 10 °C from established baseline within a shift; rate-of-rise > 2 °C/h  
**Sampling rate:** 1 Hz (typical for historian); 0.1–0.5 Hz sufficient for thermal mass assets  
**Failure modes detected:** Lube starvation, overloading, cooling failure, electrical fault (winding), external heat ingress  

#### 2.2b Thermocouple (Type K, J, S)

**Range:**
- Type K: −40 to +1372 °C — furnace flues, reheat furnaces, ladle preheaters
- Type J: −40 to +750 °C — lower-temperature process zones
- Type S (Pt/Rh): to +1600 °C — tundish, basic oxygen furnace

**Typical healthy range:**
- Reheat furnace interior: 1100–1260 °C (process)
- Rolling mill roll surface: 50–180 °C during rolling
- Cooling bed air: 30–100 °C

**Accuracy:** ±1–2 °C (Type K with compensation); less accurate than RTD, but handles extreme temperatures RTDs cannot  
**Sampling rate:** 0.1–1 Hz for process thermocouples; 0.01–0.1 Hz for slow furnace zones  
**Failure modes detected:** Runaway furnace temperature, refractory failure, burner malfunction

#### 2.2c Thermal Imaging (IR Camera)

**Physical quantity:** Radiated thermal flux → surface temperature map (2D)  
**Wavelength band:** LWIR (8–14 µm) for ambient-temperature equipment (bearings, motors, switchgear); MWIR (3–5 µm) for high-temp processes (steel surface, molten metal)  
**Spatial resolution:** 320×240 to 640×480 pixels; spot sensitivity < 0.1 °C NETD  
**Vendors:** FLIR Systems, Fluke, Testo, Optris  
**Typical use:** Route-based walkaround or fixed-mount continuous monitoring  
**Healthy vs alert thresholds:** ΔT < 5 °C vs ambient for bearings; ΔT > 15 °C = caution; ΔT > 30 °C = immediate action (electrical panels: NETA standard)  
**Sampling rate (fixed mount):** 1–25 Hz image capture; alarm on pixel percentile exceeding threshold  
**Failure modes detected:** Hot spots in electrical panels, asymmetric bearing overheating, refractory brick failure (hot-face detection from outside shell), winding insulation breakdown  

---

### 2.3 Pressure & Differential Pressure

**Physical quantity:** Gauge, absolute, or differential pressure  
**Transducer type:** Strain-gauge diaphragm, piezoresistive, capacitive  
**Output:** 4–20 mA (industry standard), HART, Profibus, Foundation Fieldbus

**Applications and ranges in steel plants:**

| Application | Range | Healthy | Alarm trigger |
|-------------|-------|---------|---------------|
| Hydraulic roll-gap control | 0–350 bar | 150–250 bar under load | < 80 bar (low pressure = cylinder leak) |
| Hydraulic system relief | 0–700 bar | Per design | > relief setpoint |
| Lube oil supply pressure | 0–10 bar | 2–5 bar | < 1.5 bar = lube starvation TRIP |
| Bearing lube inlet | 0–6 bar | 2–4 bar | < 1 bar alarm |
| Lube oil filter dP (differential) | 0–2 bar dP | < 0.5 bar dP | > 1 bar dP = filter clogged |
| Compressed air header | 0–10 bar | 6–8 bar | < 5 bar alarm |
| Hydraulic descaler (HSD) | 0–220 bar | 150–180 bar | < 120 bar = nozzle blockage |
| Cooling water supply | 0–10 bar | 3–6 bar | < 2 bar = flow risk |
| Gas (natural gas/BF gas) | 0–500 mbar | 100–300 mbar | ± 20% deviation alarm |

**Sampling rate:** 1–10 Hz continuous; up to 100 Hz for hydraulic shock monitoring  
**Failure modes detected:** Filter clogging (lube dP rise), pump wear (pressure drop), valve failure, seal/hose leakage, hydraulic cylinder internal bypass, descaler nozzle erosion

---

### 2.4 Flow (Coolant, Lube, Gas)

**Physical quantity:** Volumetric or mass flow rate  
**Transducer types:**
- **Electromagnetic flow meter** (Coriolis-free, conductive liquids ≥ 5 µS/cm): cooling water, lube — DN3–DN3000, accuracy 0.2–0.5% FS, 4–20 mA / RS485 / HART
- **Ultrasonic (clamp-on or in-line):** coolant loops, hydraulic oil, gas — ±0.1 to ±5 m/s, non-intrusive, unaffected by fine metallic particles
- **Mass flow (Coriolis):** precision lube dosing, scale control — accuracy 0.1–0.5%
- **Variable-area rotameter:** local visual indication for small coolant branch circuits

**Ranges and healthy values:**

| Application | Typical range | Healthy | Alarm |
|-------------|--------------|---------|-------|
| Roll cooling water (per stand) | 0–3000 L/min | 800–1500 L/min | < 400 L/min |
| Bearing lube oil (forced lube loop) | 0–500 L/min | 100–300 L/min | < 50 L/min |
| Hydraulic oil (main circuit) | 0–1000 L/min | 200–600 L/min | Deviation > 20% |
| Blast furnace gas to burner | 0–10 000 Nm³/h | Per burner design | < 50% design flow |
| Nitrogen (inert purge) | 0–500 Nm³/h | Per setpoint | Deviation > 15% |

**Sampling rate:** 1–10 Hz (process control); 0.1–1 Hz (historian)  
**Failure modes detected:** Cooling water blockage (scale, debris), lube pump degradation, valve failure, pipe leakage, nozzle erosion

---

### 2.5 Electrical — Motor Current Signature Analysis (MCSA) + Power Quality

**Physical quantity:** Stator phase current (A), line voltage (V), real/reactive power (kW/kVAR), power factor  
**Transducer type:** Current transformer (CT) clamp, Rogowski coil, voltage divider (for MCSA); power analyzer (for power quality)

**MCSA specifics:**
- Current sensing from motor supply cables — non-invasive, no machine access required
- Fundamental frequency: 50 Hz (India grid) or 60 Hz
- Fault sideband formula: f_fault = f_line ± n × f_bearing_characteristic
- Recording window: 20–60 seconds for ≤ 0.01 Hz frequency resolution (needed for rotor bar analysis)

**Typical current ranges (induction motors in steel plants):**

| Motor type | Rated current | Healthy load (% FLA) | Alarm |
|-----------|--------------|---------------------|-------|
| Rolling mill main drive (MW-class) | 500–5000 A | 60–90% FLA | > 110% FLA sustained |
| Pump / fan motor (100–500 kW) | 200–1000 A | 55–85% FLA | > 105% FLA |
| Conveyor motor (50–200 kW) | 100–400 A | 50–80% FLA | > 110% FLA |

**Sampling rate:**
- MCSA analysis: 5–20 kHz raw acquisition (Nyquist for bearing fault sidebands up to 5 kHz)
- Power metering (kW/kVAR/PF): 1 Hz for historian; 10 ms for PQ analyzers

**Failure modes detected:**
- Broken rotor bars (sidebands at f_line ± 2sf_line)
- Bearing faults (sidebands around f_line)
- Stator winding insulation degradation (inter-turn short — high-freq noise floor rise)
- Eccentricity (static: DC component; dynamic: f_line ± f_rpm)
- Mechanical overload / process jam (current surge)
- Phase imbalance / voltage unbalance
- Efficiency degradation (trending power factor)

---

### 2.6 Acoustic Emission (AE) / Ultrasonic

**Physical quantity:** Stress waves (transient elastic waves) emitted by crack propagation, friction, impacting  
**Frequency range:**
- Acoustic emission: 100 kHz – 1 MHz (stress wave propagation in metal)
- Ultrasonic leak/friction detection (handheld): 20–100 kHz
- Low-freq AE (bearing): 50–300 kHz for fatigue crack initiation

**Transducer:** Piezoelectric resonant or broadband AE sensor, surface-mounted with coupling gel  
**Key advantage over vibration:** Detects subsurface crack initiation (as small as 0.5 mm) before any vibration signature is visible; unique ability to localize crack position via time-of-arrival (TOA) triangulation on rolling mill work rolls

**Typical parameters:**
- Hit rate (healthy bearing): < 10 hits/s
- Hit rate (degrading bearing): 10–100 hits/s
- Hit rate (severe fault): > 500 hits/s (continuous emission)
- Amplitude (healthy): < 40 dB AE
- Amplitude (active crack): 50–80 dB AE

**Sampling rate:**
- Continuous streaming (AE): 1–2 MHz acquisition; processed to hit count / energy per second (1 Hz to historian)
- Ultrasonic patrol (handheld): non-continuous, route-based

**Failure modes detected:** Subsurface contact fatigue cracks in rolling-element bearings and rolls, spalling onset, active crack propagation in roll barrel, valve seat leakage (ultrasonic), steam trap failure

---

### 2.7 Oil / Lubricant Analysis

**Physical quantity:** Particle count (ISO 4406 cleanliness code), viscosity (cSt), water content (ppm), elemental spectroscopy (Fe, Cr, Si wear metals), Total Acid Number (TAN), oxidation

#### 2.7a ISO 4406:2017 Particle Count

**Code format:** XX/YY/ZZ = particles ≥4 µm / ≥6 µm / ≥14 µm per mL  

| Code level | Approx. particle count / mL |
|-----------|-----------------------------|
| 14 | 80–160 |
| 17 | 640–1280 |
| 20 | 5000–10 000 |
| 22 | 20 000–40 000 |

**Target cleanliness (steel plant):**

| System | Target ISO code | Action code |
|--------|----------------|-------------|
| Hydraulic roll-gap | 15/13/10 | > 18/16/13 |
| Gearbox / main lube | 16/14/11 | > 19/17/14 |
| Circulating lube (bearings) | 17/15/12 | > 20/18/15 |

#### 2.7b Viscosity

**Units:** cSt (mm²/s) at 40 °C and 100 °C  
**Typical oil grades:** ISO VG 46–150 (hydraulic); ISO VG 150–460 (gearbox); ISO VG 32–68 (circulating lube)  
**Action trigger:** Deviation > ±15% from new-oil specification at 40 °C  

#### 2.7c Water Content

**Units:** ppm (mg/kg)  
**Healthy:** < 200 ppm  
**Caution:** 200–500 ppm  
**Action:** > 500 ppm (free water probable; emulsification; corrosion risk)  
**Test methods:** Karl Fischer titration (lab); crackle test (field)

#### 2.7d Wear Metals (Spectroscopy)

**Key elements:** Fe (bearing/gear wear), Cr (seal wear), Si (dirt ingression), Cu (bronze bushing), Al (housing corrosion)  
**Healthy Fe baseline (gearbox):** < 20 ppm; rising trend (> 5 ppm/sample) = active wear

**Sampling frequency:** Every 500–1000 operating hours (route-based, lab-analyzed); online sensors (particle counters with laser diodes) at 1-minute intervals for critical systems

**Failure modes detected:** Active abrasive wear (particle count + Fe rise), water ingress (coalescing, free water), viscosity breakdown (thermal degradation, fuel dilution), contamination (dirt ingress via breathers), seal failure

---

### 2.8 Proximity / Displacement (Eddy-Current Probes)

**Physical quantity:** Shaft-to-bearing clearance (relative displacement), shaft orbit  
**Transducer type:** Non-contacting eddy-current proximity probe (Bently Nevada, Brüel & Kjær, Metrix)  
**Standard:** ISO 7919 series — shaft relative vibration measured as peak-to-peak displacement (µm p-p)  
**Mounting:** Two orthogonal radial probes (X, 0° and Y, 90°) at each journal bearing; one axial probe for thrust  
**Gap (static bias):** Set at mid-linear range, typically 1.0–1.5 mm → ±0.5 mm measurement range  
**Output signal:** Voltage proportional to gap; −4 V/mm to −8 V/mm sensitivity (Bently Nevada standard: 7.87 V/mm = 200 mV/mil)

**ISO 7919-3 shaft vibration limits (mm/s RMS → µm p-p) [unverified exact values — consult standard directly]:**

| Speed (RPM) | Zone A/B boundary (µm p-p) | Zone C/D boundary (µm p-p) |
|-------------|---------------------------|---------------------------|
| 1500 RPM (4-pole motor) | ~90 µm | ~180 µm |
| 3000 RPM (2-pole motor) | ~65 µm | ~130 µm |
| 150–300 RPM (slow roll) | ~200–300 µm | ~400–500 µm |

> Rule of thumb: Allowable displacement ≈ 25.4 × (12 000 / √N) µm p-p where N = RPM [Bently Nevada practice; [unverified] as exact ISO threshold].

**Orbit analysis:** X–Y Lissajous plot of shaft centreline path within clearance circle. Circular orbit = unbalance; figure-8 = misalignment; precessing orbit = oil whirl/whip instability.

**Sampling rate:** 5–20 kHz (typical eddy-current conditioning); 1× per revolution (keyphasor-gated) for 1× synchronous data; orbit waveform stored at 1–5 kHz

**Failure modes detected:** Journal bearing oil film breakdown, shaft bow (thermal or mechanical), rotor instability (oil whirl/whip), coupling misalignment, excessive bearing clearance (worn journal), axial thrust overload

---

### 2.9 Speed / RPM / Encoder + Torque / Load

#### 2.9a Speed (Tachometer / Encoder)

**Physical quantity:** Rotational speed (RPM) or angular position  
**Transducer types:**
- **Optical encoder (incremental):** 80–2500 PPR; 0–150 kHz output; power 5–24 VDC; quadrature output (A/B channels + Z index)
- **Magnetic pickup (reluctance):** Passive; gear-tooth trigger; robust in contaminated environments; output: variable amplitude 0.5–50 V at frequency = (teeth × RPM / 60)
- **Hall-effect sensor:** Active; cleaner digital pulse; for lower-speed shafts

**Typical ranges in steel plants:**

| Asset | Speed range | Typical operating |
|-------|------------|------------------|
| Rolling mill main motor (DC/AC) | 0–300 RPM | 50–200 RPM (dependent on product) |
| Gear spindle output | 0–200 RPM | 80–150 RPM |
| Strip processing line (tension reel) | 0–600 RPM | 100–500 RPM |
| Centrifugal pump | 1450 / 2900 RPM | Fixed (synchronous) |
| Compressor | 1500–3000 RPM | 2950 RPM |
| Blast furnace blower | 1500–6000 RPM | 3000–4500 RPM |

**Keyphasor signal:** Single pulse per revolution from a notch/key on shaft — used to phase-reference all vibration signals, enabling synchronous averaging and run-up/coast-down analysis.

**Sampling rate:** 1 kHz (encoder pulses) → computed speed output every 10–100 ms (10–100 Hz)

**Failure modes detected:** Speed deviation from setpoint (slip coupling, overload, drive fault), speed oscillation (torsional resonance), roll speed mismatch between mill stands (strip tension upset), encoder failure (loss of control feedback)

#### 2.9b Torque / Roll Force / Load

**Physical quantity:** Torque (N·m or kN·m), roll separating force (kN or MN), strip tension  
**Transducer types:**
- **Load cell (strain gauge):** Hydraulic roll-gap screw-down; tension meter rolls; mounted on frame column
- **Torque transducer (shaft-mounted):** Rotating telemetry or slip ring; rare in hot rolling (heat, contamination); more common in cold mill
- **Motor current proxy:** Torque estimated from motor current and equivalent-circuit model (±5–10% accuracy)

**Typical ranges:**

| Asset | Range | Healthy | Alarm |
|-------|-------|---------|-------|
| Hot rolling mill roll force | 5–50 MN | 8–30 MN (product-dependent) | > rated + 20% |
| Cold rolling mill roll force | 5–20 MN | 3–15 MN | > rated + 15% |
| Strip tension (bridle roll) | 0–500 kN | 50–200 kN | > max setpoint |
| Gearbox output torque | 0–500 kN·m | 70–90% rated | > rated |

**Sampling rate:** 10–100 Hz (roll force, process control loop); 1 Hz (historian trending)  
**Failure modes detected:** Bearing overloading (force spike), roll pass schedule deviation, cobble/jam detection (sudden force spike), coupling slip, screw-down cylinder malfunction, broken roll (force collapse)

---

## 3. SCADA / Historian Integration and Data Schema

### 3.1 Data Flow Architecture

```
Field Sensor
    → 4-20 mA / HART / pulse → Transmitter / Smart Device
    → Fieldbus (Profibus, FOUNDATION Fieldbus, HART 7) → Field Junction Box
    → I/O Module (DCS / PLC card) → Controller
    → OPC-UA Server (IEC 62541)
    → SCADA / HMI (AVEVA System Platform / Emerson DeltaV / Honeywell Experion)
    → Historian (OSIsoft PI / AVEVA Historian / Honeywell PHD / GE Proficy)
    → Analytics Platform / ML Pipeline
```

### 3.2 Canonical Tag Naming (ISA-95 Asset Hierarchy)

Standard convention: `{Site}.{Area}.{Unit}.{Equipment}.{Tag_Type}.{Qualifier}`

Examples:
```
JAMSHEDPUR.HSM.STAND_4.PINION_GB.VIB_VEL_RMS_H    # Velocity RMS, Horizontal
JAMSHEDPUR.HSM.STAND_4.DRIVE_MOTOR.TEMP_WINDING_U  # Winding temp, phase U
JAMSHEDPUR.HSM.STAND_4.WORK_ROLL.FORCE_SEP         # Roll separating force
JAMSHEDPUR.CASTER_2.STRAND_1.WITHDRAWAL_ROLL.SPD   # Withdrawal roll speed
JAMSHEDPUR.LUBE_STATION.LOOP_3.PRESSURE_SUPPLY      # Lube supply pressure
JAMSHEDPUR.BF_1.BLOWER.CURRENT_PHASE_A             # Blower motor phase A current
```

### 3.3 Historian Record Schema (OSIsoft PI / AVEVA style)

| Field | Type | Example |
|-------|------|---------|
| `tag_name` | string | `HSM.STD4.PINION.VIB_VEL_RMS_H` |
| `timestamp` | ISO 8601 UTC | `2026-06-07T14:32:05.123Z` |
| `value` | float64 | `3.47` |
| `unit` | string | `mm/s` |
| `quality` | integer (OPC-DA: 0=bad, 192=good, 216=interpolated) | `192` |
| `asset_id` | string (SAP / CMMS equipment number) | `EQ-10042-HSM-STD4-PNGB` |
| `sensor_type` | enum | `vibration_velocity` |
| `sampling_interval_ms` | integer | `1000` |

### 3.4 Typical Sampling Rates by Historian Storage Strategy

| Signal class | Acquisition rate | Historian storage rate | Compression |
|-------------|-----------------|----------------------|-------------|
| Vibration RMS (online) | 5–25 kHz raw | 1–10 s average | Dead-band 0.1 mm/s |
| Vibration waveform (burst) | 25 kHz | Triggered snapshots | No compression |
| Temperature (RTD) | 10 Hz | 1 s or exception-based | ±0.5 °C dead-band |
| Pressure | 10–100 Hz | 1 s | ±0.1% FS dead-band |
| Flow | 10 Hz | 1 s | ±0.2% FS dead-band |
| Motor current (RMS) | 1 Hz power meter | 1 s | ±1% FLA dead-band |
| MCSA waveform | 10–20 kHz | Triggered | No compression |
| Speed / RPM | 100 Hz pulse count | 100 ms–1 s | ±0.5 RPM dead-band |
| Roll force | 100 Hz | 100 ms–1 s | ±0.5% FS dead-band |
| AE (processed: hit count) | 1 Hz processed | 1 s | No compression |
| Oil particle count (online) | 1 min | 1 min | None |

---

## 4. Common Data Quality Failure Modes (Platform Design Targets)

| Failure type | Sensor class | Root cause | Data-quality signal |
|-------------|-------------|-----------|-------------------|
| Flat-line / frozen signal | Any | Sensor disconnection, transmitter lockup, historian compression over-aggressive | Zero variance over N minutes |
| Spike / impulse outlier | Vibration, pressure | Electrical transient, mechanical shock, cable fault | Value > 6σ from rolling mean, duration < 1 scan |
| Drift (slow upward) | Temperature, pressure | Calibration shift, process fluid ingress | Monotonic trend over days without process change |
| Range saturation | Any 4–20 mA | Sensor undersized for fault amplitude | Value = exactly 0% or 100% of range |
| Negative value | Pressure, flow | Reversed differential pressure connection, wiring fault | Value < physical lower bound |
| Sampling jitter | All | Network latency, PLC scan miss | Non-uniform timestamp intervals |
| Cross-correlated anomaly | Multi-sensor | Genuine fault — all co-moving | Correlated multi-tag deviation (true signal, not noise) |
| Missing data (gaps) | Any | Maintenance downtime, network outage, scheduled scan skip | NaN / null sequence > configurable threshold |
| Stale quality flag | OPC-UA tags | Upstream PLC communication loss | Quality code ≠ 192 (Good) |
| Calibration zero error | RTD, pressure | Wiring error, drift | Offset from known steady-state baseline |

---

## 5. Key Standards Reference

| Standard | Scope |
|----------|-------|
| ISO 10816-3 / ISO 20816-3 | Vibration velocity evaluation zones, non-rotating parts, 15 kW+ industrial machines |
| ISO 7919-3 | Shaft relative vibration (proximity probe), rotating shafts |
| ISO 13373 | Condition monitoring via vibration — measurement procedures |
| ISO 17359 | Condition monitoring and diagnostics — general guidelines |
| ISO 4406:2017 | Oil cleanliness particle count classification |
| ISO 4407 | Oil cleanliness microscopic examination |
| IEC 60751 | PT100 RTD specification |
| IEC 60584 | Thermocouple tolerances and types |
| IEC 62541 (OPC-UA) | Unified architecture for sensor-to-cloud data transport |
| ISA-95 | Enterprise/control system integration, asset hierarchy model |
| API 670 | Machinery protection systems (proximity probes, velocity sensors) — process industry standard used in heavy industry |

---

## 6. Steel-Plant Equipment to Sensor Mapping (Quick Reference)

| Equipment | Primary sensors | Secondary sensors |
|-----------|----------------|------------------|
| Hot strip mill main stand | Vibration (accelerometer), roll force (load cell), speed (encoder), motor current (CT) | Temperature (bearing RTD), lube pressure, roll gap position |
| Continuous caster | Temperature (K-type, infrared), withdrawal roll speed, strand guide roll vibration | Flow (cooling water), mould level (EM sensor) |
| Basic oxygen furnace (BOF) | Temperature (S-type TC, pyrometer), off-gas flow, pressure | AE (steel-structure cracks) |
| Reheat furnace | Temperature (K-type, distributed), fuel gas flow, combustion air flow | Pressure (furnace atmosphere) |
| Gearbox (pinion stand) | Vibration (accelerometer), temperature (RTD), oil particle count | AE (gear crack), oil viscosity, oil water content |
| Centrifugal pump (cooling) | Vibration (accelerometer), flow (EM meter), motor current | Temperature (bearing RTD), pressure (discharge) |
| Blast furnace blower | Vibration (accelerometer + proximity probe), speed (tachometer), motor current | Surge detector (ΔP), temperature, power |
| Ladle crane / overhead crane | Load cell, speed (encoder), motor current | Vibration (drive motor) |
| Rolling mill roll chock | Vibration (high-shock accelerometer), displacement (proximity probe), temperature (RTD) | AE (subsurface crack) |

---

## 7. Confidence and Uncertainty Notes

- ISO 10816-3 zone limit values: **High confidence** — values consistently cited across multiple industry sources (vibromera.eu, dspanalytic.com, acoem.us, Honeywell documentation)
- MCSA sampling rates (5–20 kHz): **High confidence** — confirmed from academic sources (MDPI, IEEE Xplore) and vendor documentation (Sensemore)
- AE hit-rate thresholds: **Medium confidence** — values from MDPI PMC review article; may vary by sensor resonant frequency and coupling method [unverified exact numbers]
- ISO 7919 shaft displacement values in table: **[unverified exact values]** — indicative numbers from Bently Nevada practice; always verify against the actual ISO 7919-3 standard table for the specific machine class
- Hydraulic pressure ranges: **Medium confidence** — cross-matched across patent literature and vendor specs; exact steel-plant OEM setpoints will vary by mill builder
- Oil cleanliness target codes: **High confidence** — confirmed via ISO 4406 and lubrication engineering sources (MachineryLubrication.com, OxMaint)

---

## Sources

- [ISO 10816-3 Vibration Limits: Zones A/B/C/D — Vibromera](https://vibromera.eu/glossary/iso-10816-3/)
- [ISO 10816-1 Standard Overview — Vibromera](https://vibromera.eu/glossary/iso-10816-1/)
- [Understanding the ISO 10816-3 Vibration Severity Table — DSP Analytic](https://dspanalytic.com/en/vibrations/understanding-the-iso-10816-3-vibration-severity-table/)
- [Understanding the ISO 10816-3 Vibration Severity Chart — Acoem USA](https://acoem.us/blog/other-topics/understanding-the-iso-10816-3-vibration-severity-chart/)
- [ISO 20816-3: Industrial Machine Vibration Limits (>15kW) — Vibromera](https://vibromera.eu/glossary/iso-20816-3/)
- [ISO 7919 Shaft Relative Vibration — Vibromera Calculator](https://vibromera.eu/calculators/shaft-vibration-iso7919/)
- [Proximity Probe (Eddy Current Sensor): Full Guide — Vibromera](https://vibromera.eu/glossary/proximity-probe/)
- [Steel Plant Vibration Analysis Best Practices — OxMaint](https://oxmaint.com/industries/steel-plant/steel-plant-vibration-analysis-best-practices-measurement)
- [Early Detection of Subsurface Fatigue Cracks in Rolling Element Bearings by AE — MDPI/PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9315545/)
- [Condition Monitoring and Fault Detection in Roller Bearing Used in Rolling Mill by AE — ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S2214785321040475)
- [Motor Current Signature Analysis (MCSA) for Predictive Maintenance — Sensemore](https://sensemore.io/motor-current-signature-analysis-mcsa-for-predictive-maintenance/)
- [MCSA Predictive Maintenance Guide 2026 — OxMaint](https://oxmaint.com/blog/post/blog-post-motor-current-signature-analysis-predictive-maintenance)
- [Brief Review of Motor Current Signature Analysis — HRCAK (peer-reviewed)](https://hrcak.srce.hr/file/218882)
- [Temperature Sensors in Manufacturing: RTD vs Thermocouple — iFactoryApp](https://ifactoryapp.com/blog/temperature-sensors-manufacturing)
- [Thermocouple vs. RTD (Pt100): The Engineer's Decision Guide — HT Heater](https://www.ht-heater.com/thermocouple-vs-rtd-comparison/)
- [Thermal Imaging for Predictive Maintenance: An OEM's Guide — LightPath](https://www.lightpath.com/blog/thermal-imaging-for-predictive-maintenance-an-oems-guide/)
- [Oil Analysis in Predictive Maintenance — OxMaint](https://oxmaint.com/blog/post/blog-post-oil-analysis-predictive-maintenance-machines)
- [ISO 4406 Oil Particle Counter Standard — Ayalytical](https://ayalytical.com/iso-4406/)
- [Particle Counting — Oil Analysis 101 — MachineryLubrication.com](https://www.machinerylubrication.com/Read/353/particle-counting-oil-analysis)
- [Electromagnetic Flow Meter Specifications — QT Instrument](https://www.qtmeters.com/flowmeter/electromagnetic-flow-meter.html)
- [Ultrasonic Flow Meters for Coolant — IFM](https://www.ifm.com/de/en/shared/technologies/flow-sensors/innovations/puresonic)
- [An In-Depth Study of Vibration Sensors for Condition Monitoring — NCBI/PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10857366/)
- [Predictive Maintenance ML Deployment 2026 — TEEPTRAK](https://teeptrak.com/en/predictive-maintenance-ml-deployment-2026/)
- [Comparative Study: Motor Current vs RPM for Roll Force Estimation — MDPI](https://www.mdpi.com/2075-1702/14/1/45)
- [How Force Sensors Improve Efficiency in Steel Mill Rolling Lines — MSNST](https://www.msnst.com/post/how-force-sensors-improve-efficiency-and-safety-in-steel-mill-rolling-line)
- [Journal Bearing Monitoring Guide — CTC Online](https://www.ctconline.com/resources/journal-bearing-monitoring-guide/)
- [SCADA Historian Integration with CMMS (AVEVA, OSIsoft, Honeywell PHD) — OxMaint AI](https://oxmaint.ai/industries/steel-plant/steel-plant-scada-pi-historian-integration-cmms)
- [Using OPC-UA to Extract IIoT Time Series Data — InfluxData](https://www.influxdata.com/resources/using-opc-ua-to-extract-iiot-time-series-data-from-plc-and-scada-systems/)
