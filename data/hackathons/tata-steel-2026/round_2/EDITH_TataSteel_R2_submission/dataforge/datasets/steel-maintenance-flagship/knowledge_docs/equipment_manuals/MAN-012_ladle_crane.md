# Equipment Manual: Melt Shop Ladle Crane (Molten-Metal Handling Hoist)
**Asset ID:** MS.LDC.CRN01
**Equipment Class:** ladle_crane
**Document:** MAN-012 | Rev 1.0 | Site: TATA_JSR (Synthetic Reference)
**Standard References:** ISO 4309:2017, FEM 1.001, BS EN 13135, ISO 20816-1

> **DISCLAIMER — SYNTHETIC DOCUMENT.** All numeric values are representative industry estimates grounded in cited standards. No proprietary Tata Steel data is used.

---

## 1. Equipment Description

MS.LDC.CRN01 is the 320-tonne ladle crane serving the melt shop ladle bay. It lifts and transfers ladles containing liquid steel at ~1550 °C between EAF tap position, ladle treatment station (LTS/LF), and continuous caster platform. It is a safety-critical machine: a ladle drop event is catastrophic and irreversible.

**Manufacturer:** Konecranes
**Model:** Ladle crane 320 t
**Rated Load (SWL):** 320 tonnes
**Process Stage:** Steelmaking (ladle transfer)
**Criticality:** 1
**Installation Date:** 2016-08-20
**Last Overhaul:** 2024-07-05

**Crane configuration:**
- **Hoist type:** Double-girder overhead traveling crane with main and auxiliary hoists
- **Main hoist:** 320 t (ladle hook); duplicate brake sets; dual motor + gearbox
- **Wire rope:** Multi-strand high-tensile wire rope; MFL (Magnetic Flux Leakage) monitoring system for continuous rope health assessment
- **Brakes:** Electro-hydraulic disc brakes (fail-safe: spring-applied, released by hydraulics) — dual independent brake sets per drum
- **Load monitoring:** Strain-gauge load cell on hoist block
- **Structural design:** Class M8 / FEM 3m (ladle crane — heaviest duty cycle)

---

## 2. Technical Specifications

| Parameter | Value |
|-----------|-------|
| Safe Working Load (SWL) | 320 t (main hoist) |
| Molten-metal profile | Applied: alarm at 95% WLL, cut power at 110% (stricter than general EOT) |
| Wire rope type | 6 × 36 Warrington-Seale, IW (independent wire rope core), galvanised |
| Rope diameter (nominal) | ~60–80 mm (SWL-dependent, OEM-specified) |
| Rope discard criteria (ISO 4309:2017) | ≥12 random broken wires in one lay length; ≥4 broken wires in one strand; rope diameter reduction ≥7% nominal; LMA >15–20% |
| Rope warning criteria | ≥6 random broken wires in one lay; diameter −3%; MFL ~8–12% LMA |
| Brake type | Electro-hydraulic disc, fail-safe spring-applied |
| Brake test interval | Every shift (hoist load test) |
| Duty class | FEM M8 / ISO M8 (heaviest cycle: continuous production ladle handling) |
| Competent Person (CP) inspection | Per ISO 4309 + local statutory regulation (minimum annually; typically quarterly for M8 ladle cranes) |

---

## 3. Sensor Instrumentation

| Tag | Quantity | Unit | Normal Range | Warning | Alarm | Standard |
|-----|----------|------|-------------|---------|-------|----------|
| JSR.MS.CRN01.ROPE.MFL | Wire rope MFL signal | mV | 0 – 100 | 150 | 300 | ISO 4309:2017 |
| JSR.MS.CRN01.LOAD.SWL | Hoist load as % SWL | %SWL | 0 – 95 | 95 | 110 | FEM 1.001 / BS EN 13135 / ISO 4309:2017 |
| JSR.MS.CRN01.GBX.VIB.GMF | Hoist gearbox GMF vibration | g | 0 – 0.5 | 1.0 | 2.5 | ISO 10816 extrap. (unverified) |
| JSR.MS.CRN01.BRAKE.TEMP | Brake drum temperature | degC | 25 – 90 | 110 | 120 | (unverified) |

**ROPE.MFL note (critical):** MFL (Magnetic Flux Leakage) signal is the Local Loss of Metallic Area (LMA) proxy.
- 150 mV warning ≈ 8–12% LMA (advisory; ISO 4309 advisory threshold range)
- 300 mV alarm ≈ >15–20% LMA OR ≥12 random broken wires in one lay OR ≥4 in one strand = **ISO 4309:2017 discard criteria**

At alarm: **Take crane out of service immediately. Do NOT lift.**

**ROPE.MFL vs diameter reduction vs broken wire count are distinct metrics.** All three are discard criteria under ISO 4309 — any ONE is sufficient grounds for immediate rope retirement.

**LOAD.SWL note:** Molten-metal ladle crane has stricter load limits than general EOT cranes:
- Warning at 95% WLL (ladle fill variation can cause brief exceedance)
- Cut power at 110% (FEM / Konecranes molten-metal profile)

**BRAKE.TEMP note:** Hot brake drum indicates repeated braking with insufficient cooling time (duty cycle problem) or brake slippage (brake force below requirement).

---

## 4. Operating Limits

| Condition | Limit | Action |
|-----------|-------|--------|
| ROPE.MFL | >150 mV (warning) | Schedule Competent Person inspection within 7 days; consider reducing service load |
| ROPE.MFL | >300 mV (alarm) | **Take crane out of service immediately**; do not lift until rope replaced |
| LOAD.SWL | >95% (warning) | Check ladle weight at next tap; reduce heat size if approaching SWL |
| LOAD.SWL | >110% (alarm) | Power cut-out activates; do NOT override; investigate overload cause |
| GBX.VIB.GMF | >1.0 g (warning) | Gear wear developing; schedule inspection |
| GBX.VIB.GMF | >2.5 g (alarm) | Stop crane; gear inspection before next lift |
| BRAKE.TEMP | >110 °C (warning) | Allow cooling; check brake lining thickness |
| BRAKE.TEMP | >120 °C (alarm) | Stop crane; inspect brake for slippage or seized piston |

---

## 5. Known Failure Modes

### 5.1 Wire Rope Fatigue — Broken Wires (Primary Life-Limiting Mode)

**Root Cause:** Cyclic bending fatigue as rope passes over sheaves and drum; fretting between wire strands; corrosion in melt shop environment (steam, splatter). The ladle crane M8 duty class produces maximum fatigue loading — rope bending cycles accumulate rapidly.

**ISO 4309:2017 Discard Criteria (any one is sufficient to retire rope):**
- Random broken wires: ≥12 in any one lay length (≥4 in one strand)
- Rope diameter reduction: ≥7% of nominal diameter
- LMA (MFL proxy): >15–20%
- Rope corrosion class R4 or worse
- Deformation (kink, bird-cage, crush)

**Degradation Timeline:**
- Healthy: ROPE.MFL = 60 mV; LOAD.SWL = 50% (nominal ladle)
- Warning: ROPE.MFL = 150 mV (~8–12% LMA); 6 random broken wires or −3% diameter
- Alarm: ROPE.MFL = 320 mV (>15–20% LMA); ≥12 broken wires in one lay
- Failure: Rope rupture → ladle drop → catastrophic

**Sensor Signature:**
- ROPE.MFL: 60 → 320 mV (alarm)
- LOAD.SWL: 85 %SWL [normal] (load does not cause rope alarm — only MFL)

**Fault Codes:** ROPE-MFL-RETIRE, ROPE-DISCARD-ISO4309
**Unplanned TTR:** 24 hours | **Cost Impact:** USD 1,000,000 (range $1M–$20M; catastrophic ladle drop = $20M+)
**Safety Class:** P1

**Critical note:** The CATASTROPHIC consequence of a ladle drop (Qinghe 2007 — 32 fatalities, steel plant destroyed) means this P1 classification drives zero-tolerance rope inspection. ISO 4309 discard criteria must never be negotiated.

### 5.2 Hoist Gearbox Gear Wear

**Root Cause:** Gear tooth flank wear from high-cycle duty; contaminated/degraded gearbox oil; shock loads from rapid hoist engagement.

**Signature:** GBX.VIB.GMF rising from 0.5 g → 1.0 g (warning) → 2.5 g (alarm); oil ferrography showing gear wear particles.

**Action:** Oil sample + ferrography at warning; plan gearbox inspection at next maintenance window.

### 5.3 Brake Wear / Slip

**Root Cause:** Brake lining (friction material) wear reduces brake torque; brake piston sticking prevents full engagement; contamination from oil leak onto disc surfaces.

**Consequence:** Brake slip under load = ladle lowering uncontrolled → catastrophic.

**Detection:** BRAKE.TEMP elevated; brake test shows drift (standard test: energise motor to lift load 50 mm; de-energise; verify load does not drift).

**Action:** Brake pad replacement (BRAKE-PAD-01; stock 4 sets); brake thruster inspection (BRAKE-THR-01; stock 1).

---

## 6. Preventive Maintenance Schedule

| Task | Interval | Method | Notes |
|------|----------|--------|-------|
| MFL rope monitoring | Continuous (per-feed) | MFL instrument on rope path | Trend report to maintenance daily |
| Competent Person (CP) rope inspection | Quarterly (M8 duty) or per statutory | Visual + MFL + caliper | ISO 4309:2017 documented inspection |
| Brake hold test | Every shift (pre-operation) | Load test: lift load 50 mm; de-energise; verify no drift | Zero tolerance: any drift = stop crane |
| Brake lining thickness measurement | Monthly | Caliper measurement | Replace (BRAKE-PAD-01) when at wear limit |
| Load cell calibration | 6-monthly | Dead weight or shackle load cell | ±1% accuracy required |
| Hoist gearbox oil sample | Monthly | Lab ferrography + ASTM D5185 | Trend Fe ppm |
| Hoist gearbox oil change | Per OEM schedule (typically annually) | Planned stop | Full drain + flush |
| Hoist gearbox vibration (GMF) monitoring | Continuous 1 Hz | Permanent accelerometer | Trend report |
| Wire rope lubrication | Per OEM (typically monthly) | Rope lubricant application | Reduces corrosion and wire-wire fretting |
| Fleet angle check | At rope change | Measurement | Must be <4° to prevent rapid drum flange wear |
| Sheave groove inspection | At CP inspection | Caliper + template | Worn grooves = increased rope bending |
| Structural crack inspection (main girder) | Annually | Visual + NDT (MT or PT at welds) | M8 class fatigue loading; document weld condition |
| Full crane statutory inspection | Annually (minimum) + after modification | Competent Person + load test | Per local factory legislation |

---

## 7. Troubleshooting

### T1 — ROPE.MFL > 150 mV (Warning)

1. Document current MFL reading and date; add to rope monitoring log.
2. Schedule Competent Person (CP) visual inspection within 7 days.
3. Count broken wires per lay length during CP inspection — if approaching discard count (≥12), retire rope immediately.
4. Measure rope diameter at 5 locations — if any shows −3% or greater, retire immediately per ISO 4309.
5. Review remaining rope campaigns available vs. replacement rope procurement (ROPE-CRN-01; stock 1; 6-week lead).

### T2 — ROPE.MFL > 300 mV (Alarm — ISO 4309 Discard)

1. **Remove crane from service immediately. Do NOT lift with this crane.**
2. If load is currently suspended: lower to floor under controlled operation with maximum caution; do NOT allow personnel below load path.
3. Lock out crane; attach "OUT OF SERVICE" tag; notify melt shop management.
4. Fit replacement rope (ROPE-CRN-01; using wedge socket termination — SOCK-WEDGE-01; not rope clips).
5. Load test after rope change per statutory requirement (typically 1.0 × SWL static test + 1.1 × SWL dynamic if new rope or gearbox change).
6. Competent Person sign-off before return to service.

### T3 — Brake Drift Detected During Shift Test

1. Remove crane from service immediately — ladle operation PROHIBITED.
2. Inspect brake pads for thickness; inspect brake disc for oil contamination.
3. Check brake thruster pressure / actuation stroke.
4. Replace brake pads (BRAKE-PAD-01) if at or below wear limit.
5. If thruster at fault: replace (BRAKE-THR-01; 1 in stock; 8-week lead for replenishment).
6. Brake test + Competent Person sign-off before return to service.

---

## 8. Corrective Maintenance — Rope Replacement

**Required Spares:**
| Part ID | Description | Stock | Lead Time |
|---------|-------------|-------|-----------|
| ROPE-CRN-01 | Wire rope (custom length/spec) | 1 | 6 weeks |
| SOCK-WEDGE-01 | Wedge socket (rope termination) | 4 | Stock |
| BRAKE-PAD-01 | Crane brake pads | 4 | 4 weeks |
| BRAKE-THR-01 | Brake thruster (electro-hydraulic) | 1 | 8 weeks |

**CRITICAL NOTE:** Only ONE rope set in stock with 6-week lead. At ROPE.MFL warning: order replacement immediately to maintain buffer stock. Rope end termination must use wedge sockets (SOCK-WEDGE-01) — rope clips are NOT acceptable for ladle crane application per ISO 4309.

**Unplanned TTR:** 24 hours
**Cost Impact:** USD 1,000,000 (equipment + lost production; catastrophic potential $1M–$20M)
**Safety Class:** P1

---

## 9. Safety

- **P1 — Catastrophic potential:** A ladle drop from a 320-tonne crane carrying liquid steel at 1,550 °C is the most severe possible event in the melt shop. Zero-compromise on rope inspection and brake testing is non-negotiable. Reference: Qinghe Special Steel 2007 (32 fatalities, plant destroyed by ladle drop).
- **Never override rope discard criteria:** ISO 4309:2017 discard criteria are calculated from fatigue physics, not conservative margin. A rope above discard criteria has statistically significant probability of imminent failure.
- **Exclusion zone:** Ladle bay floor must be evacuated of all non-essential personnel during any ladle lift. Liquid steel spatter radius = 15 m for a 320 t ladle; floor must be clear to 25 m.
- **PPE for ladle bay operations:** Full aluminised suit, face shield (must withstand liquid metal splash), metatarsal boots, neck protection. No synthetic fibres (nylon melts to skin).
- **Brake test is mandatory pre-lift — no exceptions:** Even a single shift test omission creates legal and safety liability. Results documented in shift log.
- **Crane electrical:** 6.6 kV crane power supply (typical); MV isolation required before crane maintenance; LOTO includes hoist motor, bridge drive, and travel drive.
- **Fall from height:** Crane maintenance requires working at height (girder top, hoist drum); full harness + lanyard; second person on ground. Fall arrest systems must be rated for steel plant environment (heat, steam).
