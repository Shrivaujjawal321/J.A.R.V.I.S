# Mechanical Condition-Monitoring Sensors: Vibration, Acoustic Emission, and Proximity/Displacement
## Deep Reference for Steel-Plant PdM — Normal vs Defect Readings

**Primary standard source:** ISO 10816-3:1998(E) — read directly from IHS Licensee copy (cemb-vib.cn/pdf/ISO%2010816-3%20Mechanical%20Vibration%20Measurements.pdf)
**Superseded by:** ISO 20816-3:2022 (retains same zone-boundary values for Groups 1–2; adds Groups 3–4 structure)

---

## 1. Sensor Types, Physical Quantities, Units, and Sampling Rates

### 1.1 Accelerometers (Vibration)

| Parameter | Value |
|---|---|
| Physical quantity measured | Acceleration of bearing housing or machine structure |
| Primary output unit | g (gravitational acceleration) or m/s² |
| Derived quantities used | Velocity (mm/s RMS) via integration; Displacement (µm p-p) via double-integration |
| Standard measurement band | 10 Hz – 1,000 Hz (ISO 10816-3 §3.1); extend to 2 Hz for machines <600 r/min |
| Bearing defect analysis band | 1 kHz – 25 kHz (envelope/demodulation) |
| High-frequency resonance range | 5 kHz – 25 kHz (structural resonance excited by bearing impacts) |
| Typical continuous sampling rate | 25.6 kSPS (gives ~12.8 kHz Nyquist; adequate for envelope up to ~10 kHz) |
| High-frequency sampling | 51.2–102.4 kSPS for gear-mesh harmonics >10 kHz |
| Transducer types | ICP/IEPE piezoelectric (100 mV/g typical sensitivity); charge-mode for high-temp >120°C |
| Mounting methods | Stud mount (best, flat response to 15 kHz+); adhesive pad (-3 dB ~5 kHz); magnet (-3 dB ~2 kHz); probe (-3 dB ~1 kHz) |
| Temperature range (typical industrial) | -50°C to +120°C (ICP); up to +260°C (charge-mode) |

**ISO 10816-3 §3.1 explicit requirement:** Flat frequency response 10 Hz to 1,000 Hz minimum. Diagnostic use requires upper limit >1,000 Hz (note in §3.1).

### 1.2 Acoustic Emission (AE) Sensors

| Parameter | Value |
|---|---|
| Physical quantity measured | Transient elastic stress waves from crack, friction, impact, plastic deformation |
| Frequency range | 20 kHz – 1 MHz (wideband); resonant sensors tuned 100–500 kHz |
| Common resonant peaks | 150 kHz, 300 kHz, 500 kHz (sensor-dependent) |
| Wideband sensors | 200–1,000 kHz operating range |
| Sampling rate required | 2–5 MSps (at minimum 2× highest frequency of interest per Nyquist) |
| Output signal | Voltage burst (mV–V); parametrized as: Hit count, Hit rate (hits/sec), RMS voltage (V_RMS), Amplitude (dBae), Rise time (µs), Duration (µs), Energy (aJ or arbitrary units) |
| dBae scale reference | 1 µV at sensor preamplifier input = 0 dBae |
| Preamplifier gain | 20 dB, 40 dB, or 60 dB (application-dependent) |
| Coupling medium | Ultrasonic gel or grease; direct contact; waveguide for hot surfaces |
| Lead-time advantage over vibration | AE detects incipient damage 3–8 weeks before vibration analysis registers the same fault (oxmaint.com [unverified]) |

### 1.3 Proximity / Eddy-Current Displacement Probes

| Parameter | Value |
|---|---|
| Physical quantity measured | Shaft-to-probe gap (shaft radial or axial position) |
| Output unit | µm (displacement); typically expressed as µm peak-to-peak (p-p) |
| Sensitivity | 7.87 V/mm (200 mV/mil) for standard Bently Nevada 3300 series |
| Frequency response (dynamic) | DC to ~10 kHz (adequate for all subsynchronous and synchronous shaft motion) |
| Sampling rate | Typically 20–40 kSPS per channel (2 channels per bearing, 90° apart) |
| Mounting | Two probes per fluid-film bearing, 90° apart (X-Y configuration), typically at ±45° from vertical (Bently Nevada standard) |
| Gap setpoint | 1.0–1.5 mm air gap (mid-range of linear zone); linear range ~0.25–2.25 mm for 5 mm probe |
| Target material requirement | Electrically conductive, non-ferrous preferred; ferrous OK with calibration |
| Applications in steel plant | Blast furnace blower shafts, ID/FD fans, main rolling mill drive spindles (fluid-film bearings only) |

---

## 2. Normal (Healthy) Reading Values

### 2.1 ISO 10816-3:1998 — Complete Normative Zone Boundary Tables (Annex A)

These are transcribed verbatim from the ISO 10816-3:1998 standard document (Annex A, Tables A.1–A.4).

**Frequency range for all tables:** 10 Hz – 1,000 Hz (or 2 Hz – 1,000 Hz for machines <600 r/min)
**Measurement quantity:** Broad-band RMS velocity (mm/s) and RMS displacement (µm)
**Zone A** = newly commissioned machine (normal baseline)
**Zone B** = acceptable for unrestricted long-term operation
**Zone C** = unsatisfactory for long-term; operate for limited period, schedule remedial action
**Zone D** = danger of damage; immediate shutdown

#### Table A.1 — Group 1: Large machines, rated power >300 kW and ≤50 MW; electrical machines shaft height H ≥ 315 mm

| Support class | Zone boundary | RMS displacement (µm) | RMS velocity (mm/s) |
|---|---|---|---|
| Rigid | A/B | 29 | 2.3 |
| Rigid | B/C | 57 | 4.5 |
| Rigid | C/D | 90 | 7.1 |
| Flexible | A/B | 45 | 3.5 |
| Flexible | B/C | 90 | 7.1 |
| Flexible | C/D | 140 | 11.0 |

#### Table A.2 — Group 2: Medium machines, rated power 15–300 kW; electrical machines shaft height 160 mm ≤ H < 315 mm

| Support class | Zone boundary | RMS displacement (µm) | RMS velocity (mm/s) |
|---|---|---|---|
| Rigid | A/B | 22 | 1.4 |
| Rigid | B/C | 45 | 2.8 |
| Rigid | C/D | 71 | 4.5 |
| Flexible | A/B | 37 | 2.3 |
| Flexible | B/C | 71 | 4.5 |
| Flexible | C/D | 113 | 7.1 |

#### Table A.3 — Group 3: Pumps with multivane impeller, separate driver, rated power >15 kW

| Support class | Zone boundary | RMS displacement (µm) | RMS velocity (mm/s) |
|---|---|---|---|
| Rigid | A/B | 18 | 2.3 |
| Rigid | B/C | 36 | 4.5 |
| Rigid | C/D | 56 | 7.1 |
| Flexible | A/B | 28 | 3.5 |
| Flexible | B/C | 56 | 7.1 |
| Flexible | C/D | 90 | 11.0 |

#### Table A.4 — Group 4: Pumps with multivane impeller, integrated driver, rated power >15 kW

| Support class | Zone boundary | RMS displacement (µm) | RMS velocity (mm/s) |
|---|---|---|---|
| Rigid | A/B | 11 | 1.4 |
| Rigid | B/C | 22 | 2.8 |
| Rigid | C/D | 36 | 4.5 |
| Flexible | A/B | 18 | 2.3 |
| Flexible | B/C | 36 | 4.5 |
| Flexible | C/D | 56 | 7.1 |

**ISO 10816-3 §5.2 — Criterion II (change in magnitude):** A change exceeding 25% of the Zone B upper limit is considered significant and triggers investigation, regardless of absolute zone.

**ISO 10816-3 §5.3 — Operational limits:**
- ALARM: Set at baseline + 25% of Zone B upper value. Must not normally exceed 1.25× Zone B upper limit.
- TRIP: Generally within Zone C or D; must not exceed 1.25× Zone C upper limit.

**Steel plant mapping (Group 1, Rigid):** Rolling mill main drives (>300 kW motors with sleeve bearings on rigid concrete pedestals) → ALARM at 4.5 mm/s RMS, TRIP at ~9 mm/s RMS (1.25× C/D boundary of 7.1).

### 2.2 ISO 7919-3 / ISO 20816 — Shaft Displacement (Proximity Probes)

Shaft vibration expressed as peak-to-peak displacement (µm p-p). Zone boundaries are speed-dependent:

**General formula (ISO 7919-3, coupled industrial machines):**
```
Zone A/B boundary (µm p-p) = A × sqrt(12000 / N)
```
where N = shaft speed in r/min. Coefficient A differs by zone and machine type.

**Typical values at representative speeds (Group of coupled industrial machines, fluid-film bearings):**

| Speed (r/min) | Zone A/B (µm p-p) | Zone B/C (µm p-p) | Zone C/D (µm p-p) |
|---|---|---|---|
| 1,500 | ~90 | ~150 | ~200 |
| 3,000 | ~63 | ~100 | ~140 |
| 1,000 | ~110 | ~185 | ~245 |

**[Unverified — derived from ISO 7919-3:1996 formula structure; exact coefficients require the standard document]**

**Normal operating shaft displacement** for a well-balanced, properly aligned rotor at rated speed:
- 1× (synchronous) component: typically 20–40 µm p-p on a healthy Group 1 machine at 1,500 r/min
- DC gap (static eccentricity): <10% of bearing clearance (bearing clearance typically 0.1–0.2% of journal diameter)

### 2.3 Acoustic Emission — Healthy Baseline

- **Hit rate:** Healthy rolling element bearing: 0–5 hits/sec at low loads; at moderate load on clean, well-lubricated bearing: 5–50 hits/sec. [unverified — plant-specific; must establish per-asset baseline]
- **RMS voltage (V_RMS):** Healthy bearing: very low, typically 0.01–0.05 V_RMS at 40 dB preamplifier gain. [unverified]
- **Amplitude distribution:** Normal distribution centered <35 dBae for healthy bearing under moderate load. [unverified]
- **Energy:** Low, quasi-continuous (lubrication film noise); no discrete bursts.
- AE signals from healthy bearings are primarily from elastohydrodynamic (EHD) lubrication film, which produces a characteristic low-amplitude broadband background. Any discrete burst above this background is suspect.

**Key principle:** AE baselines are highly plant- and asset-specific. Establish at commissioning under known-good conditions at rated speed and load. All subsequent monitoring is deviation-based, not absolute-threshold-based.

---

## 3. Defect Signatures — What Readings Become Under Each Fault Mode

### 3.1 Mass Imbalance

**Physics:** Uneven mass distribution creates centrifugal force rotating at shaft frequency.

**Vibration signature:**
- Dominant peak at exactly 1× running speed (1×N) in radial direction (horizontal and vertical)
- Axial component: low (<30% of radial 1× amplitude) — distinguishes from misalignment
- Phase: stable, repeatable; 1× phase angle constant ±5° when measured repeatedly
- Time waveform: near-sinusoidal at 1× frequency, low harmonic content
- Overall RMS grows proportional to unbalance mass × eccentricity × ω²

**Warning/Alarm indicators:**
- Warning: 1× radial amplitude increases >25% above baseline (ISO 10816-3 Criterion II)
- Alarm: 1× radial dominates spectrum, overall RMS enters Zone C (Group 1 rigid >4.5 mm/s; Group 2 rigid >2.8 mm/s)
- Severe: Zone D (Group 1 rigid >7.1 mm/s; Group 2 rigid >4.5 mm/s)

**Progression:** Gradual if due to material loss (erosion, corrosion on impeller/roll) or sudden if due to piece breakage. Rate-of-change of 1× amplitude is the key trend metric.

### 3.2 Misalignment (Angular and Parallel)

**Physics:** Shaft centerlines not co-linear produce periodic forcing at 1× and 2× (angular misalignment generates strong axial 1×; parallel generates strong radial 2×).

**Vibration signature:**
- **Angular misalignment:** Strong axial 1× (often equal to or greater than radial 1×); axial/radial ratio >0.5 is diagnostic. 180° phase shift across coupling axially.
- **Parallel misalignment:** Strong radial 2× (often 2× > 1×); sometimes 3× visible.
- **Combined misalignment:** Both 1× and 2× elevated in both radial and axial; 1× and 2× may approach equal amplitude.
- Spectrum: clean 1×–2× (sometimes 3×); not a "forest" of harmonics (distinguishes from looseness).
- Orbit plot (proximity probes): banana-shaped or figure-8 orbit indicates misalignment.

**Warning/Alarm:**
- Warning: Axial 1× exceeds 50% of radial 1× (angular), or 2× exceeds 1× in radial (parallel)
- Alarm: Overall entering Zone C per machine group; rate of increase accelerating (indicative of progressive coupling or bearing wear)

### 3.3 Mechanical Looseness

**Physics:** Improperly tightened bearing fits, loose foundation bolts, or cracked frames allow non-linear impacts at multiples of shaft frequency.

**Vibration signature:**
- "Forest" of harmonics: 1×, 2×, 3×, 4× ... up to 10× or more, with roughly decreasing amplitude
- Sub-harmonics possible: 0.5×, 1.5×, 2.5× (indicates severe looseness with rubbing or impacting)
- Phase: unstable (varies between measurements); this instability distinguishes looseness from imbalance
- Time waveform: truncated or clipped appearance (non-linear impact response)
- Kurtosis of time-domain signal increases (>6–10) due to impulsive content

**Warning/Alarm:**
- Warning: 2× and 3× harmonics appear above noise floor where previously absent; sub-harmonics emerging
- Alarm: Multiple harmonics at significant amplitude (>20% of 1×); sub-harmonics >10% of 1×; overall in Zone C

### 3.4 Rolling Element Bearing Faults

#### 3.4.1 Bearing Defect Frequency Formulas

For a rolling element bearing with N rolling elements, ball diameter Bd, pitch diameter Pd, contact angle α, shaft speed f_s (Hz):

```
BPFO (outer race) = (N/2) × f_s × (1 - (Bd/Pd) × cos α)
BPFI (inner race) = (N/2) × f_s × (1 + (Bd/Pd) × cos α)
BSF  (ball spin)  = (Pd/(2×Bd)) × f_s × (1 - ((Bd/Pd) × cos α)²)
FTF  (cage)       = (f_s/2) × (1 - (Bd/Pd) × cos α)
```

**Typical multiplier ranges relative to shaft speed (for most industrial bearings):**
- FTF: 0.35×–0.48× (always sub-synchronous)
- BPFO: 3×–7× (most common range; easiest to detect — stationary outer race, fixed load zone)
- BPFI: 4×–9× (inner race rotates; modulated by shaft speed sidebands around BPFI)
- BSF: 1.5×–4× (often difficult to detect; cage constrains energy)

Source: vibromera.eu/glossary/bearing-fault-frequencies/ ; IoTBearings.com

#### 3.4.2 Fault Progression — Four Stages

Based on the P-F curve model (Machinerylubrication.com, "Detecting Premature Bearing Failure"):

**Stage 1 — Ultrasonic / Early AE** (10–20% life remaining; detection: AE sensor, ultrasound probe)
- AE frequency range: 250–350 kHz
- AE parameters: Discrete bursts emerging above EHD background; hit rate rising from baseline; RMS V_AE increasing >3× baseline [unverified magnitude]
- Conventional vibration: No visible change yet
- kurtosis: Still ~3 (Gaussian); no impulsive signature yet
- Detection lead time: 3–8 weeks before Stage 2 visible [unverified]

**Stage 2 — High-Frequency Resonance Excitation** (5–10% life remaining; detection: HF vibration, envelope)
- AE frequency range: 500 Hz – 2 kHz (bearing natural/structural resonance frequencies)
- Envelope spectrum: Discrete peaks at BPFO, BPFI, BSF, FTF (and harmonics) emerge in demodulated signal
- Kurtosis: Rising above 3; typically 4–8 for developing fault
- Crest factor: Rising above 5 (healthy ≤5)
- Broadband acceleration RMS: Slight increase; may still be within Zone A–B
- Detection: Envelope analysis (demodulation) around resonance band

**Stage 3 — Sidebands + Multiple Harmonics Visible** (1–5% life remaining; detection: conventional FFT)
- BPFO/BPFI harmonics: 2nd, 3rd, 4th harmonics appear; sidebands at ±f_s around BPFI (since inner race rotates)
- Kurtosis: 8–40 (highly impulsive signal)
- Crest factor: 8–20
- Broadband acceleration RMS: Significant increase; entering Zone C
- Temperature: Noticeable rise (typically +5°C to +15°C above baseline)
- Lubrication: Oil debris sensor detects metallic particles >100 µm

**Stage 4 — Random Noise / Catastrophic Approach** (0–1% life remaining; hours to failure)
- Spectrum: Individual fault frequencies broaden and merge into noise floor ("grass" appearance)
- Kurtosis: Paradoxically may decrease as signal becomes more random (less impulsive, more continuous damage)
- Broadband RMS: Very high, Zone D; rapid increase
- Temperature: Rapid rise (+20°C or more above baseline); potential thermal runaway
- AE: Continuous high-amplitude emission; discrete burst structure disappears
- Vibration RMS may actually plateau or decrease just before seizure (bearing cage fracture releases constraint)

#### 3.4.3 Envelope Analysis Procedure

1. Acquire raw acceleration signal at high sampling rate (25.6–51.2 kSPS)
2. Identify structural resonance frequency band (spectral kurtosis or known resonance; typically 3–10 kHz range)
3. Bandpass filter around resonance (e.g., 3–8 kHz for a bearing with resonance at 5 kHz)
4. Rectify (absolute value) the filtered signal
5. Low-pass filter to remove carrier frequency (cutoff = max bearing defect frequency × 5, typically <1 kHz)
6. Apply FFT to the envelope signal → "envelope spectrum" or "demodulated spectrum"
7. Look for peaks at BPFO, BPFI, BSF, FTF and their harmonics

**Spectral kurtosis** is used to automatically identify the optimal frequency band for step 2 (Antoni & Randall, 2006).

#### 3.4.4 Kurtosis and Crest Factor Thresholds

| Condition | Kurtosis | Crest Factor | Interpretation |
|---|---|---|---|
| Healthy | ~3.0 | ≤5 | Gaussian signal; no impulsive faults |
| Early fault | 3–6 | 5–8 | Incipient damage; investigate |
| Developing fault | 6–20 | 8–15 | Clear defect; schedule maintenance |
| Severe fault | 20–100 | 15–30 | Urgent; operate with monitoring |
| Near-failure (Stage 4) | May drop back toward 3 | Variable | Random noise dominates; damage widespread |

Sources: Viking Analytics (vikinganalytics.se); Beckhoff TF3600 condition monitoring documentation (infosys.beckhoff.com)

### 3.5 Gear Mesh Faults

**Physics:** Gears produce a dominant frequency at gear mesh frequency (GMF) = number of teeth × shaft speed. Faults modulate this carrier.

**GMF = Z × f_s** (Hz), where Z = number of teeth, f_s = shaft frequency in Hz

**Healthy gear spectrum:** GMF at low amplitude; 2×GMF, 3×GMF at decreasing amplitude; sidebands at ±f_s around GMF (from manufacturing tolerances) but low amplitude (sideband/GMF ratio <0.1).

**Defect signatures:**

| Fault type | Spectral signature | Diagnostic indicator |
|---|---|---|
| Tooth wear (distributed) | Broad GMF peak; sidebands grow symmetrically | Sideband Energy Ratio (SER) = sum(sidebands)/GMF amplitude; SER > 0.5 is warning [unverified threshold] |
| Tooth crack (local) | Asymmetric sidebands; dominant side at ±f_faulty_gear; harmonics of GMF with sidebands | SER growing; phase modulation visible in time-synchronous averaging |
| Tooth breakage | Sudden large amplitude at GMF and harmonics; impulsive time waveform | Kurtosis spike; crest factor >8 |
| Gear eccentricity | Strong 1× component; sidebands at ±f_s around GMF | GMF sideband at shaft frequency; resembles imbalance but in gearbox |
| Gear misalignment | 2×GMF elevated relative to GMF | 2×GMF/GMF ratio >0.5 |

**Sideband Energy Ratio (SER) method:** Patented by GE (US8171797B2); SER = sum of sideband amplitudes / GMF amplitude. Monitored as a trend; absolute threshold is machine-specific but upward trend is the primary alarm indicator.

**Cepstrum analysis** is ideal for gearboxes: the "rahmonics" (quefrency peaks at 1/f_shaft and 1/f_gear) allow detection of both shaft and gear periodicity in complex multi-stage gearboxes where individual tooth frequencies overlap.

### 3.6 Structural Resonance

**Physics:** When a forcing frequency (1×, GMF, blade pass, etc.) coincides with a structural natural frequency, vibration amplifies dramatically (Q factor 5–50×).

**Signature:**
- Large amplitude at one specific frequency; amplitude highly sensitive to small speed changes
- Amplitude drops sharply above/below resonance speed (Campbell diagram behavior)
- Phase shift of ~180° through resonance
- Not a progressive trend — appears suddenly as speed or excitation changes

**Detection:** Coast-down or run-up test; plot amplitude vs. speed; identify critical speed peaks. Bode plot (amplitude + phase vs. speed) is definitive.

**Risk in steel plant:** Rolling mill drive-train critical speeds must be >1.3× max operating speed or <0.7× min operating speed. If a critical speed falls in the operating range, torsional damage accumulates rapidly.

### 3.7 Oil Whirl and Oil Whip (Fluid-Film Bearing Instabilities)

Relevant to: blast furnace blowers, ID/FD fans, large steam turbine drives — all with fluid-film (journal) bearings.

**Oil Whirl:**
- Sub-synchronous instability at approximately **0.43×–0.48× shaft speed**
- Onset: when shaft speed exceeds ~2× first critical speed
- Proximity probe signature: Large forward-precessing orbit with one internal loop; amplitude in X or Y probe grows to significant fraction of bearing clearance
- Orbit shape: Banana-shaped forward precession (direction of shaft rotation)
- Whirl frequency tracks shaft speed (always ~0.45× regardless of rpm)
- Warning: Sub-synchronous peak at 0.45× appearing >5% of running speed RMS [unverified]

**Oil Whip:**
- Sub-synchronous instability that locks onto system natural frequency (first critical speed)
- Frequency: Stays fixed at first critical speed even as shaft speed changes — this is the diagnostic differentiator from whirl
- Amplitude: Very large; orbit fills bearing clearance; catastrophic if uncorrected
- Orbit shape: Forward-precessing ellipse at natural frequency; may show bearing-to-shaft contact (half-annular rub signature)
- Transition: Whirl frequency "locks" to natural frequency as speed increases

**Alarm thresholds:**
- ISO 7919-3: proximity probe displacement approaching Zone C/D (see Table 2.2 above)
- Plant practice: Trip on sub-synchronous component >25–30% of clearance × shaft diameter [unverified; Bently Nevada Application Note]

Sources: turbomachinerymag.com; vibromera.eu/glossary/oil-whirl/; vibromera.eu/glossary/whirl/

---

## 4. Analysis Techniques

### 4.1 FFT Spectrum (Frequency Domain Analysis)

- **What it reveals:** Steady-state periodic vibration components; fault frequencies (1×, 2×, GMF, BPFO, BPFI); sub-synchronous instabilities (oil whirl); super-synchronous harmonics (looseness).
- **Window:** Hann (Hanning) for leakage reduction on continuous signals; flat-top for accurate amplitude measurement; rectangular for impact/transient.
- **Resolution:** df = f_sample / N_samples. For bearing analysis, df ≤ 0.5 Hz is required to resolve sidebands.
- **Lines:** 1,600–6,400 lines for routine vibration; 12,800–25,600 for high-frequency gear/bearing analysis.
- **Averaging:** 8–16 linear averages to reduce random noise; synchronous time averaging for gear analysis.
- **Limitation:** Poor for short-lived, transient, or non-stationary signals (bearing early stages, crack propagation events).

### 4.2 Envelope Analysis (Demodulation)

- **What it reveals:** Early bearing faults (Stage 2–3), invisible in standard FFT; bearing race frequencies before they emerge above noise floor in the low-frequency spectrum.
- **Procedure:** Bandpass filter → rectify → low-pass filter → FFT (see §3.4.3)
- **Key output:** Peaks at BPFO, BPFI, BSF, FTF and harmonics in the demodulated spectrum.
- **Spectral kurtosis:** Automatically identifies the optimal filter band. Antoni, J. "The spectral kurtosis: A useful tool for characterising non-stationary signals" Mech. Syst. Signal Process. 2006.
- **When to use:** Routinely from baseline commissioning; essential when kurtosis/crest factor rises above normal.

### 4.3 Time Waveform Analysis

- **What it reveals:** Impulsive events (bearing Stage 2+, gear tooth defects); waveform shape (truncation = looseness; sinusoidal = imbalance/misalignment; spiky = bearing/gear impacts).
- **Crest factor** = Peak / RMS. Healthy: ≤5. Rising CF indicates growing impulsiveness.
- **Kurtosis** = 4th statistical moment / σ⁴. Healthy Gaussian signal: 3.0. Rising kurtosis indicates impulsive damage.
- **Period of impacts:** Time between impacts in waveform × shaft speed → fault frequency confirmation without FFT.
- **Limitation:** Sensitive to noise; large signals (imbalance, misalignment) can mask impulsive bearing signals. Always pre-filter to high-frequency band before kurtosis/CF calculation.

### 4.4 Orbit Plots (Proximity Probe)

- **What it reveals:** Dynamic shaft centreline path; rotor instability signatures; rub; misalignment; critical speed behavior.
- **Construction:** X-probe (horizontal) vs. Y-probe (vertical) in time; 2D Lissajous figure.
- **Shapes and meaning:**
  - Circle: Imbalance (pure 1× forward precession)
  - Banana/inclined ellipse: Normal with some misalignment or anisotropy
  - Figure-8 (two-lobed): 2× dominant (misalignment or 2× resonance)
  - Outer loop: Oil whirl/whip (forward precession sub-synchronous loop)
  - Irregular with sharp corners: Rub or looseness
  - Banana with internal loop: Oil whirl
- **Keystone (notch filter):** Remove 1× component from orbit to see subsynchronous or supersynchronous motions clearly.

### 4.5 Cepstrum Analysis

- **What it reveals:** Periodic spacing in the FFT spectrum; ideal for gearboxes with multiple harmonic families; separates shaft modulation sidebands from gear mesh; detects multiple bearing families simultaneously.
- **Definition:** Power cepstrum = IFFT{ log |FFT(signal)|² }. X-axis is "quefrency" (units of time/seconds); Y-axis is "gamnitude".
- **Rahmonics:** Peaks in cepstrum at quefrency = 1/f_fault indicate harmonic family at f_fault. E.g., a rahmonic at 16.7 ms → harmonic family at 60 Hz (the shaft frequency).
- **Advantage over FFT:** Extracts shaft and gear modulation period even when individual sidebands are below the noise floor.
- **Application:** Routinely used on multi-stage gearboxes (hot strip mill finishing stands, continuous caster withdrawal gearboxes).

### 4.6 Shaft Centerline Plot (Proximity Probe)

- **What it reveals:** DC component of shaft position over time; bearing wear progression; thermal growth; load-dependent attitude angle changes.
- **Healthy:** Shaft centerline stable within ±10 µm over steady-state operation.
- **Bearing wear:** Centerline drops (gravity pulls shaft lower as bearing clearance grows). Drop >50% of initial position indicates significant wear [unverified; plant-specific].
- **Oil film breakdown:** Centerline approaches bearing bore — imminent metal-to-metal contact.

---

## 5. Healthy → Warning → Alarm → Failure Progression

### 5.1 Bearing P-F Curve Timeline (Rolling Element Bearing, Rolling Mill)

The progression below maps to the 4-stage model (ISO 13379 / machinerylubrication.com):

```
Time before failure:  [~months]     [~weeks]       [~days]       [hours]
                     |             |              |             |
Stage:               1             2              3             4
Sensor:              AE/Ultrasound HF Vibration   Conv. Vibration Temp + RMS
kurtosis:            ~3            4-8            8-40          drop back to ~3
crest factor:        <5            5-10           10-20         variable
BPFO in envelope:    absent/faint  clear peaks    harmonics     broadband noise
Overall RMS:         Zone A        Zone A/B       Zone B/C      Zone D
AE hit rate:         baseline      2-5× baseline  10×+ baseline continuous
Temperature:         normal        +1-2°C         +5-15°C       +20°C+ rapid rise
Oil debris:          none          <50µm particles >100µm metal  large metal particles
```

**Key point for Tata Steel PdM:** The useful warning window is Stage 2 (envelope spectrum showing BPFO/BPFI peaks). This gives 2–6 weeks to plan a bearing change. Stage 1 (AE only) is the earlier warning — 3–8 more weeks.

### 5.2 ISO 10816-3 Criterion II — Change Rate Alert

A change exceeding **25% of Zone B upper value** within a monitoring period is significant (ISO 10816-3 §5.2). This is velocity-independent and catches early-onset problems before absolute thresholds are breached:
- Group 1 rigid: Alert if change >1.125 mm/s (25% of 4.5) within one measurement cycle
- Group 2 rigid: Alert if change >0.7 mm/s (25% of 2.8) within one measurement cycle

---

## 6. Thresholds and Standards Summary

| Standard | Scope | Key quantity | Key values |
|---|---|---|---|
| ISO 10816-3:1998 / ISO 20816-3:2022 | Housing vibration, industrial machines 15–300 kW and >300 kW, 120–15,000 r/min | Broad-band RMS velocity (mm/s) | See Tables A.1–A.4 above |
| ISO 7919-3:1996 (now ISO 20816-3) | Shaft relative vibration, coupled industrial machines | Peak-to-peak displacement (µm p-p) | Speed-dependent; formula: k × √(12000/N) |
| ISO 13373-1:2002 | General procedures for vibration condition monitoring | Procedures, not thresholds | Defines measurement protocol |
| ISO 13373-2:2016 | Processing, presentation, analysis of vibration data | Analysis methods (FFT, envelope, cepstrum) | Defines techniques |
| ISO 13373-3 (DIS) | Vibration diagnosis guidelines | Fault identification criteria | Qualitative fault patterns (in draft) |
| ISO 13379-1:2012 | Condition monitoring — General guidelines for data interpretation | RUL estimation, degradation indices | No absolute thresholds; trend-based |
| ISO 18436-2 | Vibration analyst certification | Competency framework | Training standard |

**Note:** ISO 20816-3:2022 supersedes ISO 10816-3:1998 for housing vibration AND ISO 7919-3:1996 for shaft vibration, integrating both into one document. Zone boundary values for Groups 1–2 are unchanged. [unverified whether Groups 3–4 zones were revised in 2022 edition]

---

## 7. Sensor Placement Best Practice

### 7.1 Accelerometer Placement (ISO 10816-3 §3.2 / ISO 20816-3)

**Primary rule:** Mount directly on bearing housing or pedestal; as close as possible to the load-bearing zone.

**Direction (ISO 10816-3 §3.2):**
- Horizontal machines: Two orthogonal radial measurements per bearing cap (typically horizontal H and vertical V). H and V measured separately; higher of the two used against zone table.
- Axial measurement: Recommended on thrust bearings and for misalignment/axial force monitoring; not routinely assessed against zone tables (except thrust bearings per §5.1.3).
- Vertical/inclined machines: Measure in direction of elastic axis; may require axial measurement at top bearing.

**Mounting hierarchy (response quality):**
1. Stud mount (threaded, M6 or 10-32 UNF): Best — maintains full sensor frequency response to >20 kHz.
2. Adhesive stud: Good — response to ~10 kHz; acceptable for routine monitoring.
3. Magnet: Acceptable for portable use; response limited to ~3 kHz; NOT for high-frequency bearing analysis.
4. Probe (handheld): Portable only; response <1 kHz; trend monitoring only, not diagnosis.

**Surface requirement:** Clean, flat, smooth metal (≤1.6 µm Ra); remove paint, scale, rust at mount point.

**Cable routing:** Strain relief loop at sensor; shielded cable; ground shield at ONE end only (signal conditioner end) to avoid ground loops.

**Hot surfaces:** Use charge-mode accelerometer (no internal electronics); mount with heat-isolating stud.

**Steel plant specifics:**
- Roll shop area: High EMI from drives; use differential (IEPE) or charge-mode with external charge amplifier in shielded enclosure
- Near reheat furnace: Thermal isolation of cable required; thermocouple-grade extension cable NOT acceptable for accelerometer signals
- Caster roll area: Water ingress risk; IP67 or better sensor; stainless steel housing

### 7.2 AE Sensor Placement

- Mount on bearing housing or shaft-adjacent structure; minimize acoustic path length to source.
- Contact coupling: Ultrasonic gel or petroleum jelly on ground surface.
- Waveguide rod (stainless steel): Required for high-temperature surfaces (>120°C); introduces ~6 dB signal attenuation and low-pass filtering effect.
- Source localization: Three AE sensors at known locations → triangulation from arrival time differences (used for structural crack monitoring in pressure vessels; overkill for bearing monitoring).
- Avoid mounting across weld seams or bolted joints (acoustic discontinuities attenuate signals drastically).

### 7.3 Proximity Probe Placement

- Two probes per fluid-film bearing, 90° apart (X–Y).
- Standard orientation: +45° from vertical (at 10:30 and 1:30 positions looking from drive end).
- Probe face to shaft surface: 1.0–1.5 mm air gap at installation (mid-range of linear zone).
- Target surface: Must be clean, smooth, concentric; any keyway, oil hole, or surface irregularity passing under probe causes false high-frequency spike (must be tracked out in analysis software as "glitch").
- Proximity probe extension cable: Must be matched to probe/driver (Bently Nevada 3300 series: cable + probe length determines scale factor; do not extend without recalibrating).

---

## 8. Common False-Alarm Causes

| False Alarm Source | Affected Sensor | Mitigation |
|---|---|---|
| Electrical noise / EMI from VFD drives | Accelerometer | Shielded cable; single-point ground; IEPE supply noise filter; distance from drive cabling |
| Loose accelerometer mounting | Accelerometer | High-frequency noise at 5–20 kHz; check mounting torque (2–5 Nm for M6); resonance at mount natural frequency |
| Soft foot (uneven frame support) | Accelerometer | Appears as looseness (harmonics); tighten or shim before baselining |
| Structural resonance (not a fault) | Accelerometer | Appears as alarming amplitude at one frequency; confirm with run-up/down test; offset excitation frequency or detune structure |
| Nearby machine cross-talk | Accelerometer / AE | Isolate by comparing phase and frequency against known-running neighboring equipment |
| Temperature coefficient drift (IEPE supply) | Accelerometer | Use temperature-compensated sensor; do not alarm on gradual drift without trend context |
| Proximity probe target surface defect (keyway, hole) | Proximity probe | Glitch filter in signal processor; synchronous notching in software |
| Probe cable ground loop | Proximity probe | Single-point ground system; isolated conduit |
| AE from process noise (cooling water, steam jets) | AE sensor | Frequency discrimination; process-state gating (suppress AE alarm when cooling water on) |
| AE from normal EHD lubrication at high load | AE sensor | Load-normalized thresholds; alarm only on delta above load-adjusted baseline |
| Load variation causing amplitude change | All | Use load-normalized or speed-normalized baselines; do not compare measurements at different loads |
| Background vibration from external source (crane, conveyor) | Accelerometer | ISO 10816-3 §3.4: if machine-off vibration >25% of machine-on, subtract or flag |
| Transient events during start/stop | All | Gate alarms to steady-state operating window (RPM ± 2% of rated, load >80%) |

---

## 9. Supplementary Notes

### 9.1 Acceleration vs. Velocity vs. Displacement — When to Use Which

| Quantity | Sensitive to | Best for |
|---|---|---|
| Displacement (µm) | Low-frequency vibration (<10 Hz) | Shaft orbit; slow-speed equipment (<600 r/min); ISO 7919 shaft evaluation |
| Velocity (mm/s) | Mid-frequency (10–1,000 Hz) | General machine health; ISO 10816 compliance; imbalance/misalignment/looseness in normal-speed machines |
| Acceleration (g) | High-frequency (>1,000 Hz) | Bearing defects; gear mesh; AE; any impulsive fault signature |

Rule of thumb: Use velocity for reporting against ISO zones; use acceleration for bearing/gear diagnostics; use displacement for shaft proximity monitoring.

### 9.2 Steel Plant Equipment Class Mapping to ISO Groups

| Equipment | ISO 10816-3 Group | Support typical | Notes |
|---|---|---|---|
| Rolling mill main drive motor (>300 kW) | Group 1 | Rigid (concrete pedestal) | Sleeve bearings common on large motors |
| Conveyor drive motor (15–300 kW) | Group 2 | Rigid | Rolling element bearings |
| Caster withdrawal drive | Group 2 | Rigid | High torque, low speed; check lower frequency range |
| Hot strip mill finishing stand gearbox | Group 1 | Rigid | Gear mesh analysis critical; cepstrum |
| ID/FD fan on blast furnace | Group 1 or 2 (power-dependent) | Flexible (spring-isolated) | Oil whirl risk if fluid-film bearings; use proximity probes |
| Reheat furnace pusher/walking beam drive | Group 2 | Rigid | Low speed; 2 Hz lower bound on vibration measurement |
| Coke oven charge/push car wheels | Group 2–3 | N/A (mobile) | Use portable measurement |

### 9.3 Motor Current Signature Analysis (MCSA) — Complementary to Vibration

Not a mechanical vibration sensor, but highly complementary:

- **Bearing defects** modulate current at: f_line ± n × f_bearing_defect (e.g., f_line ± BPFO)
- **Rotor bar crack:** Sidebands at f_line ± 2sf_line (slip frequency sidebands); ratio >-60 dBc (relative to fundamental) is alarm level [unverified]
- **Eccentricity:** Sidebands at f_line ± f_rotate (static) or f_line ± (k×poles/2 ± 1) × f_rotate (dynamic)
- **Advantage:** No sensor installation on machine; uses existing current transducers
- **Limitation:** Electrical noise; only detects faults that modulate electromagnetic air-gap

### 9.4 AE for Slow-Speed Bearings (Key Steel Plant Application)

Conventional vibration analysis is ineffective below ~100 r/min because bearing defect frequencies fall below 1 Hz. AE is the only reliable technique for:
- Continuous caster withdrawal rolls (~10–30 r/min)
- Ladle car wheel bearings
- Walking beam hearth bearings in reheat furnace

At very slow speeds, bearing contact stresses are high (quasi-static loading); AE energy is still generated from asperity contact and micro-plasticity even without fatigue spalling. AE RMS trending at these speeds is the primary PdM tool.

Reference: pmc.ncbi.nlm.nih.gov/articles/PMC11299867/ (AE for slow-speed ropeway bearings — analogous physics)

---

## 10. References and Sources

1. **ISO 10816-3:1998(E)** — Mechanical vibration: Evaluation of machine vibration by measurements on non-rotating parts. Part 3: Industrial machines >15 kW, 120–15,000 r/min. [Primary source: direct PDF read, cemb-vib.cn/pdf/ISO%2010816-3%20Mechanical%20Vibration%20Measurements.pdf — Tables A.1–A.4 transcribed verbatim]

2. **ISO 20816-3:2022** — Supersedes ISO 10816-3:1998 and ISO 7919-3:1996. Vibromera.eu/glossary/iso-20816-3/

3. **ISO 7919-3:1996** — Shaft vibration on rotating shafts, coupled industrial machines. [Formula structure confirmed via vibromera.eu/calculators/shaft-vibration-iso7919/; exact coefficients [unverified from primary document]]

4. **ISO 13373-1:2002** — Condition monitoring: General procedures. iso.org/standard/21831.html

5. **ISO 13373-2:2016** — Condition monitoring: Processing and presentation of vibration data. cdn.standards.iteh.ai/samples/68128/...

6. **ISO 13373-3 (DIS)** — Guidelines for vibration diagnosis. iso.org/obp/ui/#!iso:std:iso:13373:-3:dis:ed-1:v1:en

7. **ISO 13379-1:2012** — Condition monitoring: General guidelines for data interpretation and diagnostics.

8. **Bearing defect frequency formulas:** vibromera.eu/glossary/bearing-fault-frequencies/ ; iotbearings.com/bearing-defect-frequencies-bpfo-bpfi-bsf-ftf-explained/

9. **Kurtosis / crest factor thresholds:** vikinganalytics.se — "Vibration Condition Monitoring Fundamentals"; Beckhoff TF3600 documentation (infosys.beckhoff.com)

10. **Oil whirl/whip:** turbomachinerymag.com/view/back-to-basics-fluid-induced-instability ; vibromera.eu/glossary/oil-whirl/ ; vibromera.eu/glossary/whirl/

11. **AE for steel plant bearing monitoring:** ScienceDirect (doi:10.1016/j.matpr.2021.xxx — "Condition monitoring and fault detection in roller bearing used in rolling mill by AE and vibration analysis"); MDPI Sensors 2024, 24(19):6462 (pmc.ncbi.nlm.nih.gov/articles/PMC11479289/)

12. **4-stage bearing failure model:** machinerylubrication.com/Read/1041/detecting-bearing-failure

13. **Sideband Energy Ratio for gears:** US Patent 8171797B2 (GE); EP2434266A2

14. **Sensor placement:** Wilcoxon Sensing Technologies Application Note "Measurement Locations" (wilcoxon.com — PDF blocked, content from search); ISO 10816-3:1998 §3.2 (primary)

15. **MCSA for motor fault detection:** MDPI Machines 2025, 13(10):902 — "Intelligent Fault Diagnosis of Ball Bearing Induction Motors"

16. **AE early detection lead time claim (3–8 weeks):** oxmaint.com/blog/post/blog-post-acoustic-emission-monitoring-predictive-maintenance [unverified exact figure — plant-specific]

---

*File written by tata-predictive-maintenance-subagent, 2026-06-08*
*For Tata Steel Round 2 Agentic AI Challenge — machinery sensor reference library*
