# 05 — Failure Physics and Sensor Signatures
**Tata Steel AI Hackathon 2026 — Round 2 Domain Research**
**Authored: 2026-06-08 | Author: tata-pdm-specialist-agent**

---

## Scope

This document is the physics ground-truth layer for the Maintenance Wizard system. It covers:

1. Bearing fault frequencies and their vibration-spectrum signatures
2. Gear mesh frequencies, sideband patterns, and wear progression
3. Structural faults — misalignment, imbalance, looseness
4. Lubrication failure progression (thermal + vibration trace)
5. Motor electrical faults via MCSA
6. Applicable ISO standards and their alarm thresholds
7. Healthy → Warning → Alarm → Failure degradation curves per sensor modality
8. Mathematical models for synthetic run-to-failure data generation

Cross-references: `08_rul-prediction.md` (Weibull AFT model), `12_synthetic-knowledge-data.md` (data generation pipeline), `09_anomaly-detection.md` (anomaly model selection).

---

## 1. Rolling-Element Bearing Fault Frequencies

### 1.1 Kinematic Derivation

A rolling-element bearing has four characteristic defect frequencies, all derived from bearing geometry and shaft speed. Let:

- `N` = shaft rotational speed (rev/s, i.e. Hz)
- `n` = number of rolling elements
- `d` = rolling element diameter (mm)
- `D` = pitch circle diameter (mm)
- `β` = contact angle (degrees)

The four Bearing Defect Frequencies (BDFs) are:

**Ball Pass Frequency Outer race (BPFO):**
```
BPFO = (n/2) · N · [1 - (d/D)·cos(β)]
```

**Ball Pass Frequency Inner race (BPFI):**
```
BPFI = (n/2) · N · [1 + (d/D)·cos(β)]
```

**Ball Spin Frequency (BSF):**
```
BSF = (D / 2d) · N · [1 - ((d/D)·cos(β))²]
```

**Fundamental Train Frequency (FTF)** — cage rotation:
```
FTF = (N/2) · [1 - (d/D)·cos(β)]
```

Typical ratios for a 6205-series deep-groove ball bearing (d/D ≈ 0.38, β ≈ 0°, n=9):
`BPFO ≈ 3.59×N`, `BPFI ≈ 5.41×N`, `BSF ≈ 2.36×N`, `FTF ≈ 0.40×N`

Source: SKF Bearing Maintenance Handbook (2018), Chapter 3; Smith (1999) *Gear Noise and Vibration*, 2nd ed.

### 1.2 Vibration Spectrum Appearance by Fault Stage

| Stage | Spectrum Feature | Sensor Reading |
|---|---|---|
| Stage 1 — Micro-pitting initiation | High-frequency energy 20–60 kHz; barely visible in velocity spectrum | AE RMS rising; velocity RMS flat |
| Stage 2 — Single-point defect | Discrete spectral lines at BDF ± 1× sidebands; 1–20 kHz | Velocity RMS +10–30%; crest factor >4 |
| Stage 3 — Multiple defects | BDF harmonics (2×, 3×, 4×) with shaft-speed sidebands; raised noise floor 2–5 kHz | RMS +50–100%; kurtosis >6 |
| Stage 4 — Severe spalling | Spectral smearing; BDF lines broadened or lost in noise floor | RMS 3–5× baseline; temperature +5–15°C |

Source: Case Western Reserve University Bearing Data Center; Randall & Antoni (2011) *Mechanical Systems and Signal Processing*, 25(2), 485–520.

### 1.3 Envelope Analysis (Hilbert Transform Method)

Raw accelerometer signal → bandpass filter around resonance frequency (typically 3–20 kHz for steel mill bearings) → Hilbert transform → magnitude envelope → FFT of envelope. Envelope spectrum reveals BDF lines even when they are buried in broadband noise. This is the ISO 13373-3 recommended diagnostic method for early-stage detection.

The key math:
```
x_bp(t)  = bandpass(x(t), f_low, f_high)
z(t)     = x_bp(t) + j·H{x_bp(t)}          # analytic signal
env(t)   = |z(t)|                            # envelope
ENV(f)   = FFT(env(t))                       # envelope spectrum
```

Fault confirmed when `ENV(BPFO)` or `ENV(BPFI)` exceeds `3σ` above the spectral noise floor.

Source: Antoni (2007) *Mechanical Systems and Signal Processing*, 21(1), 108–127 — the canonical envelope analysis reference.

---

## 2. Gear Mesh Frequencies and Wear Signatures

### 2.1 Gear Mesh Frequency (GMF)

```
GMF = N_shaft × Z_gear
```

where `N_shaft` is shaft speed (Hz) and `Z_gear` is number of teeth. For a two-stage gearbox:
- First mesh: `GMF_1 = N_input × Z_1`
- Second mesh: `GMF_2 = N_intermediate × Z_3`

**Sidebands** appear at `GMF ± k·N_shaft` (k=1,2,3,...). Healthy gear: narrow sidebands, symmetric. Worn gear: asymmetric sidebands, elevated amplitudes.

### 2.2 Fault Progression in Frequency Domain

| Fault Type | Primary Spectral Feature | Secondary Feature |
|---|---|---|
| Uniform wear | GMF amplitude rise (+3–6 dB) | Symmetric sidebands widen |
| Localized pitting | Strong 1×, 2× shaft frequency modulation | Sideband asymmetry index >0.15 |
| Cracked tooth | Impulse at 1× shaft; GMF harmonics suppressed | Time-domain: one large pulse per revolution |
| Gear eccentricity | 1× and 2× shaft modulate GMF sidebands | Ghost frequency at (ZPinion × 2π × N / 60) |

**Sideband Amplitude Ratio (SAR)** is a standard scalar health indicator:
```
SAR = (A_{GMF+N} + A_{GMF-N}) / (2 × A_{GMF})
```
Healthy: SAR < 0.1. Warning: 0.1–0.3. Alarm: > 0.3.

Source: Randall (2021) *Vibration-Based Condition Monitoring*, Wiley, Chapter 5.

### 2.3 Cepstrum Analysis for Gearboxes

The cepstrum (IFFT of log power spectrum) separates families of sidebands. A "rahmonics" cluster at spacing `1/N_shaft` indicates gear mesh modulation from a specific shaft. Particularly useful in multi-stage gearboxes where GMF lines overlap.

---

## 3. Structural Fault Signatures — Imbalance, Misalignment, Looseness

These three faults dominate steel-plant rotating machinery and are differentiated primarily by harmonic pattern and phase relationships.

### 3.1 Imbalance

**Physics:** Unequal mass distribution creates a rotating centrifugal force proportional to imbalance magnitude and ω².

**Vibration signature:**
- Dominant 1× peak in radial direction (both horizontal and vertical)
- Amplitude proportional to speed² (i.e., doubles when speed doubles — useful test)
- Phase: stable, approximately 0° or 180° in radial channels (depending on phase reference)
- Axial component: low (<20% of radial 1×)

**Diagnostic thresholds:** ISO 1940-1 G-grades. G2.5 (fans, pumps): residual imbalance ≤ 2.5 mm/s at rated speed.

### 3.2 Misalignment

**Physics:** Angular or parallel shaft offset forces the coupling to transmit bending moments at 2× and higher harmonics of shaft speed.

**Vibration signature:**
- **Angular misalignment:** Strong 1× and 2× in axial direction; axial/radial ratio > 0.5
- **Parallel misalignment:** Strong 2× in radial direction; may show 3×
- Phase: 180° phase difference between shaft ends in axial direction (angular); same phase radially (parallel)
- Shaft orbit plot: figure-eight shape for angular misalignment

**Rule of thumb:** If 2× radial > 50% of 1× radial, investigate misalignment.

Source: Berry (1994) *How to Track Rolling Element Bearing Health*, Technical Associates of Charlotte.

### 3.3 Mechanical Looseness

**Physics:** Loose components (foundation bolts, bearing caps) create asymmetric stiffness, generating sub-harmonics and truncated waveform.

**Vibration signature:**
- Truncated waveform → rich in harmonics: 1×, 2×, 3×, ..., up to 10× and beyond
- Sub-harmonics at 0.5×, 1.5× (phase instability)
- Rapid change in amplitude with small speed variation
- High kurtosis (>4) even without bearing damage

**Discrimination from imbalance:** Harmonics above 3× are prominent in looseness; imbalance is almost entirely 1×.

---

## 4. Lubrication Failure Progression

### 4.1 Degradation Mechanism

Lubricant film collapse follows a four-phase progression:

**Phase 1 — Viscosity degradation:** Oil oxidation increases viscosity index drop; water ingress reduces film thickness. Lambda ratio Λ = h_min / (Rq_1² + Rq_2²)^0.5 drops from > 3 (full film) toward 1 (boundary lubrication). Duration: weeks to months in steel-plant conditions (high temp, contamination).

**Phase 2 — Additive depletion:** Anti-wear additives (ZDDP, phosphates) consumed. Metal debris in oil increases: iron particle count (ISO 4406 cleanliness code rises, e.g., 17/15/12 → 21/19/16). Duration: days to weeks after Phase 1.

**Phase 3 — Metal-to-metal contact:** Boundary lubrication → surface asperity contact → accelerated wear particle generation. Oil debris sensor counts spike. AE sensor detects high-frequency emission bursts (100–500 kHz). Temperature rises 10–30°C above baseline.

**Phase 4 — Catastrophic failure:** Bearing or gear surface seizure. Temperature spike >50°C above baseline. Vibration RMS 5–10× baseline. Oil system pressure drop as pump cannot maintain flow through damaged components.

### 4.2 Sensor Trace per Phase

| Sensor | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|---|---|---|---|---|
| Vibration RMS (mm/s) | Baseline ±5% | +10–20% | +50–100% | 5–10× |
| Temperature (°C above baseline) | +2–5 | +5–10 | +10–30 | +50+ |
| Oil debris count (particles/mL) | Baseline | 2–3× | 10–50× | Off-scale |
| AE RMS (dB re 1μV/√Hz) | Flat | +3–6 dB | +10–15 dB | Saturated |
| Oil viscosity change (%) | +5–15% | +15–30% | — | — |

Source: Holmberg & Erdemir (2017) *Friction*, 5(3), 263–284; ISO 4406:2021 (hydraulic fluid cleanliness); [unverified for exact dB thresholds, based on field survey aggregation].

---

## 5. Motor Electrical Fault Signatures (MCSA)

Motor Current Signature Analysis (MCSA) monitors stator current spectrum. The fundamental electrical frequency is `f_s` (typically 50 Hz in Indian steel plants).

### 5.1 Broken Rotor Bar (BRB)

**Physics:** A cracked or broken rotor bar creates asymmetric rotor resistance, introducing current harmonics at:
```
f_BRB = f_s · (1 ± 2·k·s)    k = 1, 2, 3...
```
where `s` is motor slip (typically 0.01–0.05 at full load).

**Signature:** Sideband pair at `f_s ± 2·s·f_s`. For 50 Hz motor at slip=0.03: sidebands at 47 Hz and 53 Hz.

**Severity index:** Lower Sideband Current Component (LSCC):
```
LSCC_dB = 20·log10(A_{f_s - 2sf_s} / A_{f_s})
```
Healthy: LSCC < −40 dB. One broken bar: −40 to −30 dB. Two bars: −30 to −20 dB. Alarm: > −20 dB.

Source: Thomson & Fenger (2001) *IEEE Industry Applications Magazine*, 7(4), 26–34 — foundational MCSA paper.

### 5.2 Static Eccentricity

**Physics:** Air-gap non-uniformity (stator/rotor misalignment) at a fixed angle creates harmonics at:
```
f_static = f_s · [1 ± (n_p/p)]
```
where `n_p` = 1,2,3 and `p` = number of pole pairs.

**Signature:** Discrete lines at `f_s ± f_r` (rotor frequency) and related harmonics. Amplitude stable with load.

### 5.3 Dynamic Eccentricity

**Physics:** Rotor whirl (bent shaft or worn bearing in motor) creates rotating air-gap variation:
```
f_dynamic = f_s · [n ± (1-s)/p]
```

**Signature:** Sidebands that change with load (vs static, which are load-independent). Distinguishing static vs dynamic requires two load-point current spectra.

### 5.4 Stator Winding Fault

**Physics:** Inter-turn short circuit increases negative-sequence current. Negative-sequence component appears at `3f_s`, `5f_s` (odd harmonics).

**Signature:** Rise in 3rd harmonic (150 Hz) and 5th harmonic (250 Hz) of phase current. Total Harmonic Distortion (THD) >5% is a warning.

Source: Nandi et al. (2005) *IEEE Transactions on Industrial Electronics*, 52(2), 294–303.

---

## 6. ISO Standards and Alarm Thresholds

### 6.1 ISO 10816 / ISO 20816 — Vibration Severity (in-situ measurement)

ISO 10816-3:1998 (superseded by ISO 20816-3:2022 for industrial machinery) defines four velocity RMS zones:

| Zone | Velocity RMS (mm/s) | Meaning |
|---|---|---|
| A | 0 – 2.3 | New machinery; continue unrestricted |
| B | 2.3 – 4.5 | Acceptable for long-term; monitor |
| C | 4.5 – 7.1 | Tolerate short-term; schedule maintenance |
| D | > 7.1 | Dangerous; immediate action |

For large machines (> 300 kW, > 1500 rpm) — typical of rolling mill drives:

| Zone | Velocity RMS (mm/s) |
|---|---|
| A | 0 – 3.5 |
| B | 3.5 – 7.1 |
| C | 7.1 – 11.2 |
| D | > 11.2 |

Source: ISO 20816-3:2022, Table 1 (Group 1, flexible foundation machines).

### 6.2 ISO 13373 — Condition Monitoring (Vibration Methods)

- Part 1 (2002): General procedures for vibration-based condition monitoring of rotating machinery
- Part 2 (2016): Processing and presentation of vibration data — defines time waveform, FFT, envelope analysis, cepstrum as standard methods
- Part 3 (2015): Guidelines for vibration diagnosis — provides fault-to-frequency mapping tables (the basis for Section 1–3 above)

No explicit numerical alarm thresholds; defers to ISO 20816 for severity. [Note: ISO 13373-7 on torsional vibration published 2019.]

### 6.3 ISO 13381-1 — Prognostics and Health Management

Defines the PHM process model: data acquisition → feature extraction → health assessment → prognostics → decision support. Key definitions:
- **P-F curve:** Point P = detectable degradation onset; Point F = functional failure. P-F interval is the actionable window.
- **RUL definition:** Expected time from current state to functional failure under normal operating conditions.

Does NOT define numerical RUL thresholds (equipment-specific). Provides methodology for confidence intervals, which maps to our Weibull P10/P50/P90 in `08_rul-prediction.md`.

Source: ISO 13381-1:2015.

### 6.4 VDI 3839 (German standard, widely used in European steel) [unverified for EN adoption]

Provides fault-specific vibration limits per machine type. Rolling mill stands: vibration velocity alarm at 6.3 mm/s RMS, trip at 10 mm/s RMS — more aggressive than ISO 20816 Zone C/D because unplanned stop cost is higher than bearing replacement cost. Source: [unverified — cited in multiple condition monitoring textbooks but direct VDI access not confirmed].

---

## 7. Degradation Trajectories: Healthy → Warning → Alarm → Failure

### 7.1 The P-F Curve (Physical Basis)

Every equipment failure follows the P-F curve (Nowlan & Heap, 1978 — the foundational Reliability-Centered Maintenance reference):

```
                   P (detectable)        F (functional failure)
                        |                       |
Health    100% |........|   \                   |
                         \    \                  |
                          \    \                 |
                           \    \________        |
               0%           \____________\______|
                   Time -->
```

The P-F interval (time between P and F) determines how much lead time a PdM system can provide. For rolling-element bearings:
- AE detects at P (~weeks to months before failure)
- Vibration velocity detects at ~2–4 weeks before failure
- Temperature rises at ~days before failure
- Operator feels vibration at hours before failure

This is why **sensor fusion** (AE + vibration + temperature) maximizes lead time.

### 7.2 Per-Sensor Degradation Curves

#### Vibration RMS (bearing example)

Empirical trajectory (IMS Bearing Dataset, Qiu et al. 2006, mechanical systems and signal processing):

```
Stage 1 (healthy):        RMS = RMS_0 ± noise (≈0.1 g)
Stage 2 (defect onset):   RMS = RMS_0 · (1 + 0.02 · t)        # linear rise
Stage 3 (acceleration):   RMS = RMS_0 · exp(0.05 · (t - t_P))  # exponential
Stage 4 (near failure):   RMS > 5 · RMS_0, crest factor > 8
```

where `t` is time in hours from P-point. Typical `t_P` for steel-mill bearings: 50–200 hours before failure.

#### Temperature (lubrication degradation example)

```
T(t) = T_ambient + T_rise_steady + ΔT_lube(t)
ΔT_lube(t) = T_max · (1 - exp(-t / τ))   # asymptotic approach to failure temperature
```

where `τ` is the thermal time constant (typically 4–24 hours depending on bearing size and heat mass). Near failure, the exponential term saturates and a step-change (runaway heating) occurs.

#### Kurtosis (impulsiveness indicator)

```
K(t) = 3.0 + K_fault · (1 - exp(-(t - t_fault) / τ_k))
```

Healthy: kurtosis ≈ 3.0 (Gaussian). At Stage 2: K rises to 6–10. Near failure: K can decrease again (impulsive → random as damage spreads) — this "kurtosis reversal" is a known trap in simple threshold-based systems. Source: Randall & Antoni (2011).

---

## 8. Mathematical Models for Synthetic Run-to-Failure Data

### 8.1 Weibull Degradation Process

The time-to-failure `T` follows a Weibull distribution:

```
F(t) = 1 - exp(-(t/η)^β)
```

Parameters for typical steel-mill equipment (empirical estimates, [unverified for exact values]):
- Rolling-mill bearings: β = 2.0–3.5 (wear-out), η = 2000–8000 h
- Gearbox: β = 1.8–2.5, η = 15000–30000 h
- Motor (electrical): β = 0.8–1.2 (random failures dominate), η = 50000–100000 h
- Caster rolls: β = 1.5–2.0, η = 5000–12000 h

Source for parameter methodology: Jardine et al. (2006) *Mechanical Systems and Signal Processing*, 20(7), 1483–1510.

### 8.2 Exponential Degradation Model (scalar health index)

The most commonly used model for synthetic data generation (and for the degradation index in `08_rul-prediction.md`):

```
x(t) = a · exp(b · t) + σ · ε(t)
```

where:
- `x(t)` is the observable (vibration RMS, temperature, etc.)
- `a` = initial condition level (healthy state baseline)
- `b` = degradation rate parameter (b > 0 for monotone increasing)
- `σ` = measurement noise standard deviation
- `ε(t)` ~ N(0,1) i.i.d. noise

**RUL from exponential model:**
```
RUL(t) = (1/b) · ln(x_threshold / x(t))
```

This is directly used in the Stage 2 correction of the Weibull AFT pipeline.

### 8.3 Paris Law for Crack Propagation (AE-based monitoring)

For equipment with fatigue crack growth (rollers, shafts):

```
da/dN = C · (ΔK)^m
ΔK = Δσ · √(πa) · F(a/W)
```

where:
- `a` = crack length
- `N` = number of load cycles
- `ΔK` = stress intensity factor range
- `C`, `m` = Paris constants (material-specific; for steel: C ≈ 1×10⁻¹², m ≈ 3)
- `F(a/W)` = geometry factor

The AE event rate `dN_AE/dt` is proportional to `da/dt`, so cumulative AE counts follow a power law in time:

```
AE_cumulative(t) = AE_0 · (t / t_0)^p    p > 1 for accelerating damage
```

Source: Anderson (2005) *Fracture Mechanics*, 3rd ed., CRC Press; Grosse & Ohtsu (2008) *Acoustic Emission Testing*, Springer.

### 8.4 Multi-Sensor Synthetic Data Generation Recipe

To generate a realistic run-to-failure dataset for one bearing:

**Step 1 — Sample failure time:**
```python
import numpy as np
T_failure = np.random.weibull(beta) * eta   # scale by eta
```

**Step 2 — Generate degradation trajectory (per sensor):**
```python
t = np.linspace(0, T_failure, n_samples)
t_P = T_failure * 0.75   # P-point at 75% of life (adjustable per fault mode)

# Vibration RMS
vib_rms = np.where(
    t < t_P,
    vib_healthy * (1 + np.random.normal(0, 0.02, n_samples)),         # healthy phase: noise only
    vib_healthy * np.exp(b_vib * (t - t_P)) + np.random.normal(0, sigma_vib, n_samples)  # degradation
)

# Temperature
temp = (
    T_ambient
    + T_rise_steady
    + T_max_delta * (1 - np.exp(-(t - t_P).clip(0) / tau_temp))
    + np.random.normal(0, sigma_temp, n_samples)
)

# Kurtosis (with reversal)
kurt = np.where(
    t < t_P,
    3.0 + np.random.normal(0, 0.1, n_samples),
    3.0 + K_peak * np.exp(-(t - t_P - t_P*0.1)**2 / (2 * t_peak_width**2))   # Gaussian rise then fall
)
```

**Step 3 — Generate spectral features:**
For each time window, compute:
- BPFO amplitude at known bearing geometry frequencies
- Envelope spectrum peak at BPFO
- Sideband asymmetry at GMF (if gearbox)
Scale amplitudes by `vib_rms(t)` to maintain physical consistency.

**Step 4 — Add fault-specific discrete events:**
- BPFO impact pulses: Poisson-distributed in time windows; rate = `λ(t) = λ_0 · exp(b · (t - t_P))`
- AE burst events: rate follows Paris law AE cumulative model above
- Temperature step (lubricant failure): add ΔT = 15°C step at `t_P + 0.1·(T_failure - t_P)`

**Step 5 — Label RUL:**
```python
rul = T_failure - t   # continuous RUL in hours
health_state = np.select(
    [rul > 0.25*T_failure, rul > 0.05*T_failure, rul > 0],
    ['healthy', 'warning', 'alarm'],
    default='failure'
)
```

This recipe generates data consistent with IMS, CWRU, and PHM 2010 dataset characteristics and can be directly fed into the synthetic data pipeline in `12_synthetic-knowledge-data.md`.

---

## 9. Physical Parameter Reference Table

Quick lookup for synthetic data parameter seeding:

| Equipment | Fault Mode | Dominant Sensor | Key Frequency | Degradation b | Weibull β |
|---|---|---|---|---|---|
| Rolling-mill bearing | BPFO spalling | Vibration 1–10 kHz | BPFO = 3.59×N | 0.02–0.05/h | 2.5–3.5 |
| Rolling-mill bearing | BPFI spalling | Vibration + AE | BPFI = 5.41×N | 0.03–0.06/h | 2.0–3.0 |
| Gearbox pinion | Pitting wear | Vibration 500Hz–5kHz | GMF = N×Z | 0.01–0.03/h | 1.8–2.5 |
| HSM conveyor bearing | FTF cage damage | Low-freq vibration | FTF = 0.40×N | 0.04–0.08/h | 2.0–3.0 |
| Drive motor | Broken rotor bar | MCSA 50±2sf_s | f_s(1±2s) | 0.001–0.01/h | 1.0–1.5 |
| Hydraulic circuit | Seal degradation | Pressure + temp | DC drift | 0.005–0.02/h | 1.5–2.5 |
| Caster roll | Surface crack | AE + vibration | — (Paris law) | p=1.5–3.0 | — |
| Lubrication system | Oil degradation | Temp + debris | DC | 0.002–0.008/h | 1.5–2.0 |

Parameter ranges are indicative based on published case studies; validate against actual plant telemetry if available. Source basis: PHM Society 2010 Milling Data Challenge; IMS Bearing Dataset (University of Cincinnati, 2003); Nectoux et al. PRONOSTIA dataset (2012).

---

## 10. Citations Summary

| Reference | Used In |
|---|---|
| Randall & Antoni (2011) *Mechanical Systems and Signal Processing* 25(2) 485–520 | Bearing stage classification, envelope analysis theory |
| Antoni (2007) *MSSP* 21(1) 108–127 | Envelope analysis Hilbert method |
| SKF Bearing Maintenance Handbook (2018) | BDF kinematic formulas |
| Thomson & Fenger (2001) *IEEE IAS Mag* 7(4) 26–34 | MCSA broken rotor bar LSCC |
| Nandi et al. (2005) *IEEE Trans IE* 52(2) 294–303 | Motor stator fault signatures |
| ISO 20816-3:2022 | Vibration severity zones |
| ISO 13373-2:2016 | Envelope/cepstrum processing standard |
| ISO 13381-1:2015 | RUL/prognostics PHM process model |
| ISO 4406:2021 | Oil cleanliness code |
| ISO 1940-1:2003 | Imbalance G-grades |
| Jardine et al. (2006) *MSSP* 20(7) 1483–1510 | Weibull parameter methodology |
| Anderson (2005) *Fracture Mechanics* 3rd ed. CRC | Paris law constants |
| Nowlan & Heap (1978) *RCM Report* NTIS AD/A066579 | P-F curve origin, RCM |
| Qiu et al. (2006) *MSSP* | IMS bearing dataset; vibration trajectory characterization |
| PHM Society 2010 Milling Data Challenge (public) | Parameter reference for synthetic generation |
| [unverified] VDI 3839 rolling mill alarm thresholds | Section 6.4 |
| [unverified] Exact dB thresholds for oil-phase AE signatures | Section 4.2 |
